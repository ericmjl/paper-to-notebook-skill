import { execFile, spawn } from 'node:child_process';
import { mkdtemp, readFile, rm } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { createServer } from 'node:net';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { setTimeout as delay } from 'node:timers/promises';
import { fileURLToPath } from 'node:url';
import { promisify } from 'node:util';

const require = createRequire(import.meta.url);
const execFileAsync = promisify(execFile);
const host = '127.0.0.1';
const fixtures = new Map([
  ['reactive', 'reactive.py'],
  ['stale', 'stale.py'],
]);

function fixturePath(name) {
  return fileURLToPath(new URL(`./fixtures/${name}`, import.meta.url));
}

function notebookEnvironment(home) {
  return {
    PATH: process.env.PATH,
    HOME: home,
    XDG_CACHE_HOME: join(home, 'cache'),
    PYTHONDONTWRITEBYTECODE: '1',
  };
}

async function inspectProgrammatically(notebook) {
  const home = await mkdtemp(join(tmpdir(), 'marimo-fixture-'));
  try {
    const script = fileURLToPath(new URL('./inspect-programmatically.py', import.meta.url));
    const report = join(home, 'report.json');
    await execFileAsync(process.env.MARIMO_PYTHON || 'python3', [
      script, notebook, report,
    ], { cwd: home, env: notebookEnvironment(home), timeout: 90_000 });
    return JSON.parse(await readFile(report, 'utf8'));
  } finally {
    await rm(home, { recursive: true, force: true });
  }
}

async function availablePort() {
  const server = createServer();
  return new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(0, host, () => {
      const { port } = server.address();
      server.close((error) => error ? reject(error) : resolve(port));
    });
  });
}

async function waitForServer(url, exited, startupDetails) {
  const deadline = Date.now() + 15_000;
  while (Date.now() < deadline) {
    if (exited()) {
      throw new Error(`marimo exited before serving the notebook: ${startupDetails()}`);
    }
    const response = await fetch(url, { signal: AbortSignal.timeout(1_000) }).catch(() => null);
    if (response?.ok) return;
    await delay(150);
  }
  throw new Error(`marimo did not start: ${startupDetails()}`);
}

async function inspectInBrowser(notebook) {
  const { chromium, errors } = require('playwright');
  const home = await mkdtemp(join(tmpdir(), 'marimo-fixture-'));
  let browser;
  let child;
  let childStopped;
  let exited = false;
  let logs = '';

  try {
    const port = await availablePort();
    const url = `http://${host}:${port}/`;
    child = spawn(process.env.MARIMO_PYTHON || 'python3', [
      '-m', 'marimo', 'run', notebook,
      '--host', host, '--port', String(port), '--headless', '--no-token',
    ], {
      cwd: home,
      env: notebookEnvironment(home),
      stdio: ['ignore', 'ignore', 'pipe'],
    });
    childStopped = new Promise((resolve) => {
      child.once('close', () => { exited = true; resolve(); });
      child.once('error', (error) => { logs = error.message; exited = true; resolve(); });
    });
    child.stderr.setEncoding('utf8');
    child.stderr.on('data', (chunk) => { logs = (logs + chunk).slice(-3000); });
    await waitForServer(url, () => exited, () => logs.trim());

    const channel = process.env.NOTEBOOK_BROWSER_CHANNEL;
    browser = await chromium.launch({ headless: true, ...(channel && { channel }) });
    const page = await browser.newPage();
    page.setDefaultTimeout(10_000);
    await page.goto(url);

    const estimate = page.getByTestId('estimate');
    await estimate.waitFor({ state: 'visible' });
    const observedA = (await estimate.innerText()).trim();
    await page.getByText('Group B', { exact: true }).click();
    try {
      await estimate.filter({ hasNotText: observedA }).waitFor({
        state: 'visible',
        timeout: 3_000,
      });
    } catch (error) {
      if (!(error instanceof errors.TimeoutError)) throw error;
    }
    return {
      rendered: true,
      observed_a: observedA,
      observed_b: (await estimate.innerText()).trim(),
    };
  } finally {
    try {
      if (browser) await browser.close();
    } finally {
      if (child && !exited) {
        child.kill();
        const forceStop = setTimeout(() => child.kill('SIGKILL'), 2_000);
        try {
          await childStopped;
        } finally {
          clearTimeout(forceStop);
        }
      }
      await rm(home, { recursive: true, force: true });
    }
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
      // The stub selects checked-in output. A real generator receives this same request.
      const request = { prompt, paper };
      const notebook = fixtures.get(variant);
      const useBrowser = process.env.MARIMO_CHECK_MODE === 'browser';
      const inspect = useBrowser ? inspectInBrowser : inspectProgrammatically;
      const observed = await inspect(fixturePath(notebook));
      return {
        output: {
          paper_id: paperId,
          notebook,
          mode: useBrowser ? 'browser' : 'programmatic',
          ...observed,
        },
        metadata: { generation: 'fixture', prompt: request.prompt, paper_bytes: Buffer.byteLength(request.paper) },
      };
    } catch (error) {
      return { error: `${variant}: ${error.message}` };
    }
  }
}
