import { execFile } from 'node:child_process';
import { mkdtemp, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { basename, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { promisify } from 'node:util';

const execFileAsync = promisify(execFile);
const fixtures = new Map([
  ['reactive', { notebook: 'reactive.py', check: 'widget' }],
  ['stale', { notebook: 'stale.py', check: 'widget' }],
  ['table-copy', { notebook: 'table-copy.py', check: 'table' }],
  ['table-swapped', { notebook: 'table-swapped.py', check: 'table' }],
  ['table-causal', { notebook: 'table-causal.py', check: 'table' }],
]);

function fixturePath(name) {
  return fileURLToPath(new URL(`./fixtures/${name}`, import.meta.url));
}

async function readAnswerKey(file) {
  const rows = JSON.parse(await readFile(file, 'utf8'));
  if (!Array.isArray(rows) || rows.length < 2 ||
      !Array.isArray(rows[0]) || rows[0].length === 0 ||
      !rows.every((row) => Array.isArray(row) && row.length === rows[0].length &&
        row.every((cell) => typeof cell === 'string'))) {
    throw new Error('The answer key must be a JSON array of string rows with a header and equal row widths');
  }
  return rows.map((row) => row.map((cell) => cell.trim().replace(/\s+/g, ' ')));
}

function notebookEnvironment(home) {
  return {
    PATH: process.env.PATH,
    HOME: home,
    XDG_CACHE_HOME: join(home, 'cache'),
    PYTHONDONTWRITEBYTECODE: '1',
  };
}

async function candidatePython(notebook, home) {
  const source = await readFile(notebook, 'utf8');
  if (!/^# \/\/\/ script\s*$/m.test(source)) {
    return process.env.MARIMO_PYTHON || 'python3';
  }

  const options = {
    cwd: home,
    env: {
      ...notebookEnvironment(home),
      HOME: process.env.HOME,
      XDG_CACHE_HOME: process.env.XDG_CACHE_HOME,
      UV_CACHE_DIR: process.env.UV_CACHE_DIR,
      UV_PYTHON_INSTALL_DIR: process.env.UV_PYTHON_INSTALL_DIR,
      UV_SYSTEM_CERTS: process.env.UV_SYSTEM_CERTS,
      UV_OFFLINE: process.env.UV_OFFLINE,
      HTTPS_PROXY: process.env.HTTPS_PROXY || process.env.https_proxy,
      HTTP_PROXY: process.env.HTTP_PROXY || process.env.http_proxy,
      ALL_PROXY: process.env.ALL_PROXY || process.env.all_proxy,
      NO_PROXY: process.env.NO_PROXY || process.env.no_proxy,
    },
    timeout: 180_000,
  };
  await execFileAsync('uv', ['sync', '--quiet', '--script', notebook], options);
  const { stdout } = await execFileAsync('uv', ['python', 'find', '--script', notebook], options);
  return stdout.trim();
}

async function inspectProgrammatically(notebook, check, isCandidate) {
  const home = await mkdtemp(join(tmpdir(), 'marimo-fixture-'));
  try {
    const script = fileURLToPath(new URL('./inspect-programmatically.py', import.meta.url));
    const report = join(home, 'report.json');
    const python = isCandidate ? await candidatePython(notebook, home) : process.env.MARIMO_PYTHON || 'python3';
    await execFileAsync(python, [
      script, notebook, report, check,
    ], { cwd: home, env: notebookEnvironment(home), timeout: 90_000 });
    return JSON.parse(await readFile(report, 'utf8'));
  } finally {
    await rm(home, { recursive: true, force: true });
  }
}

export default class NotebookProvider {
  id() {
    return 'marimo-notebook-fixtures';
  }

  async callApi(prompt, context) {
    const { paper_id: paperId, notebook: variant } = context.vars;
    if (paperId !== 'dummy-paper' || !fixtures.has(variant)) {
      return { error: 'Unknown paper or notebook fixture' };
    }
    try {
      const paper = await readFile(fixturePath('dummy-paper.md'), 'utf8');
      const { notebook, check } = fixtures.get(variant);
      const isAccuracyCase = context.vars.expected_match !== undefined;
      const canUseCandidate = String(context.vars.expected_match) === 'true';
      const candidate = canUseCandidate ? process.env.NOTEBOOK_PATH : undefined;
      const candidateKey = canUseCandidate ? process.env.TABLE_ANSWER_KEY : undefined;
      if (Boolean(candidate) !== Boolean(candidateKey)) {
        throw new Error('Set both NOTEBOOK_PATH and TABLE_ANSWER_KEY to evaluate a candidate notebook');
      }
      const notebookFile = candidate ? resolve(candidate) : fixturePath(notebook);
      const answerKey = isAccuracyCase
        ? await readAnswerKey(candidateKey ? resolve(candidateKey) : fixturePath('table-1.json'))
        : undefined;
      const useBrowser = check === 'widget' && process.env.MARIMO_CHECK_MODE === 'browser';
      let observed;
      if (useBrowser) {
        const { inspectInBrowser } = await import('./browser-inspector.mjs');
        observed = await inspectInBrowser(notebookFile, notebookEnvironment);
      } else {
        observed = await inspectProgrammatically(notebookFile, check, Boolean(candidate));
      }
      return {
        output: {
          paper_id: paperId,
          notebook: basename(notebookFile),
          mode: useBrowser ? 'browser' : 'programmatic',
          ...observed,
          ...(check === 'table' && !isAccuracyCase && { source_paper: paper }),
        },
        metadata: {
          generation: candidate ? 'candidate' : 'fixture',
          prompt,
          paper_bytes: Buffer.byteLength(paper),
          ...(answerKey && { answer_key: answerKey }),
        },
      };
    } catch (error) {
      return { error: `${variant}: ${error.message}` };
    }
  }
}
