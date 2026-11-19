# Notebook evaluation

These optional evals check specific outputs from a notebook. The bundled cases use a [synthetic paper](fixtures/dummy-paper.md) and prepared notebooks with known good and bad outputs. The [skill's notebook validator](../scripts/README.md) checks syntax, marimo lint rules, and execution. The evals add checks for table accuracy, explanation, and widget output.

| Check | What it asks | API key |
| --- | --- | --- |
| [Table accuracy](table-eval.yaml) | Are the headings, group labels, values, and units the same as in the paper? | None |
| [Explanation fidelity](judge-eval.yaml) | Does the notebook draw conclusions that the paper supports? | OpenAI |
| [Widget behavior](OPTIONAL.md) | Does changing the input produce the expected output? | None |

## Set up the evals

1. Clone the repository and enter it. If you already have a checkout, open a terminal at its root.

   ```sh
   git clone https://github.com/ericmjl/paper-to-notebook-skill.git
   cd paper-to-notebook-skill
   ```

   If the evals are on a branch, check out the branch your teammate shared. Confirm that `evals/table-eval.yaml` exists.
2. Choose a setup for Node.js and uv:

   - **Direct install:** Install [Node.js 24](https://nodejs.org/en/download) and [uv](https://docs.astral.sh/uv/getting-started/installation/).
   - **Pixi on macOS or Linux:** With [Pixi](https://pixi.prefix.dev/latest/installation/) installed, open a shell with Node.js 24 and uv available:

     ```sh
     pixi exec --channel conda-forge --spec 'nodejs=24' --spec uv -- bash --noprofile --norc
     ```

     Run the remaining commands in that shell. Use `exit` to return to your original shell. Pixi uses a temporary environment and needs no workspace manifest.

   Check that `node --version`, `npx --version`, and `uv --version` work before continuing.

3. Set the local results directory. Run this from the repo root in each terminal you use for the evals or the viewer.

   ```sh
   export PROMPTFOO_CONFIG_DIR="$PWD/evals/.promptfoo"
   ```

4. Run the [table accuracy check](#start-with-table-accuracy) below. It runs without an API key.

`npx` runs the pinned Promptfoo CLI with Node.js. The fixture commands use `uv run --no-project` to select Python 3.12 and install marimo from [`evals/requirements.txt`](requirements.txt). Candidate notebooks can use their own inline dependencies. This eval setup needs no `pyproject.toml`. [`evals/package.json`](package.json) lists Playwright for the optional browser check.

## How a case runs

1. Promptfoo reads a case from a CSV. The row identifies a paper and the notebook to run.
2. [The notebook provider](notebook-provider.mjs) loads those files. [The Python runner](inspect-programmatically.py) executes the notebook through marimo and extracts the emitted table, prose, or widget result.
3. The table check compares the output with an answer key. The widget check reads its expected values from the case CSV. The judge sends the paper, emitted prose, and table to a model with a rubric. Promptfoo records the verdict and its reason.

## Start with table accuracy

The table check compares the column headings and ordered cells with the [answer key](fixtures/table-1.json). It reads Markdown or HTML tables and native `mo.ui.table` widgets emitted directly from notebook cells. It normalizes whitespace and compares the recorded cell text, including units.

- [table-copy.py](fixtures/table-copy.py) shows Group A at 12 seconds and Group B at 8 seconds. The evaluator should accept it.
- [table-swapped.py](fixtures/table-swapped.py) assigns those numbers to the wrong groups. The evaluator should reject it.

```sh
uv run --no-project --python 3.12 --with-requirements evals/requirements.txt -- \
  npx --yes promptfoo@0.126.0 eval -c evals/table-eval.yaml --no-cache
```

Expect **2 passed, 0 failed, 0 errors**, with exit status **0**. The second case passes because the evaluator correctly rejects the swapped values.

## Evaluate a generated notebook

Save the generated notebook as a `.py` file and validate it using the command in [the skill](../SKILL.md#5-validate-and-hand-off). Create a JSON answer key from the source paper, using [the sample key](fixtures/table-1.json) as a template. The first row contains headers. Every remaining row contains cell values as strings, with the same number of cells as the header. Keep the order and units you expect to see in the notebook.

Run the same eval with paths to your notebook and answer key:

```sh
NOTEBOOK_PATH="path/to/notebook.py" TABLE_ANSWER_KEY="path/to/answer-key.json" \
  uv run --no-project --python 3.12 --with-requirements evals/requirements.txt -- \
  npx --yes promptfoo@0.126.0 eval -c evals/table-eval.yaml --no-cache
```

The candidate replaces the accurate fixture. The swapped-value control still runs against the bundled key. A candidate passes when one of its emitted tables matches the key exactly. A failure shows the expected and observed tables or reports that no supported table was found. Both paths can be relative to the repo root or absolute.

The runner uses uv to honor the candidate's PEP 723 inline dependencies and Python requirement. Candidates without inline metadata use the fixture environment. Execution uses a temporary working directory, so use a self-contained notebook or resolve asset paths relative to the notebook file. Native table extraction is verified with the marimo version pinned in `evals/requirements.txt`. Markdown tables are the simplest format to use when testing a candidate with a different marimo version.

Run notebooks you trust. For untrusted generated code, use an isolated environment with no credentials or writable access to your checkout.

## Judge the notebook's explanation

This demonstration uses two bundled [judge cases](judge_test_cases.csv). Both reproduce the table correctly. [The faithful notebook](fixtures/table-copy.py) explains that the numbers are descriptive and cannot establish causation. [The misleading notebook](fixtures/table-causal.py) claims that assignment to Group B caused faster completion. The rubric asks GPT-4.1 mini to identify the wording or omission behind its verdict and point to the relevant statement in the paper. Use a human review to assess whether a generated notebook explains the paper well.

If the repo root has no `.env` file, copy [the template](.env.example) there with `cp evals/.env.example .env`. Set `OPENAI_API_KEY` in that local file. Git ignores the file. From the repo root:

```sh
uv run --no-project --python 3.12 --with-requirements evals/requirements.txt -- \
  npx --yes promptfoo@0.126.0 eval -c evals/judge-eval.yaml --env-file .env --no-cache
```

The run sends the synthetic source and notebook output to OpenAI for two model judgments. Expect a pass for the faithful explanation and a fail for the causal claim. In the viewer, expand the rubric assertion for each case to see what the judge relied on. If both rows show an API authentication or quota message, the requests ended before grading.

## View results

To open the viewer, keep the same results directory and run:

```sh
npx --yes promptfoo@0.126.0 view
```

See [optional checks](OPTIONAL.md) for widget behavior, browser interaction, and model credential checks.
