# Notebook evaluation smoke test

Promptfoo reads two cases from [test_cases.csv](test_cases.csv). A fixture provider loads a [synthetic paper](fixtures/dummy-paper.md) and selects a hand-written notebook. The runner executes the notebook with marimo's `app.run()`, first with its default input and then with Group B. Promptfoo compares the displayed values with the CSV.

| Case | Group A | Group B | Expected result |
| --- | --- | --- | --- |
| Reactive notebook | 12 seconds | 8 seconds | Pass |
| Deliberately stale notebook | 12 seconds | 12 seconds | Fail the Group B assertion |

## Run from the repository root

Use Node 24, Python 3.12, and [uv](https://docs.astral.sh/uv/getting-started/installation/).

```sh
export PROMPTFOO_CONFIG_DIR="$PWD/evals/.promptfoo"
uv run --no-project --python 3.12 --with-requirements evals/requirements.txt -- \
  npx --yes promptfoo@0.126.0 eval -c evals/promptfooconfig.yaml --no-cache
```

Expect **1 passed, 1 failed, 0 errors**. The deliberate failure produces a nonzero exit status. The stale notebook should produce an estimate and pass the Group A assertion before failing Group B.

To open the viewer, keep the same results directory and run:

```sh
npx --yes promptfoo@0.126.0 view
```

## Check the browser interaction

The default run checks the two outputs through Python. To check that clicking Group B updates the rendered page, install the additional dependencies:

```sh
cd evals
npm install
npx playwright install chromium --only-shell
cd ..

MARIMO_CHECK_MODE=browser uv run --no-project --python 3.12 \
  --with-requirements evals/requirements.txt -- \
  npx --yes promptfoo@0.126.0 eval -c evals/promptfooconfig.yaml --no-cache
```

## Test model credentials

The fixture eval needs no API keys. For a separate live provider check, copy `evals/.env.example` to `evals/.env` and set the key for one provider. Git ignores the local `.env` and the eval results.

```sh
npx --yes promptfoo@0.126.0 eval -c evals/providers-smoke.yaml \
  --env-file evals/.env --filter-providers openai --no-cache
```

Use `anthropic` or `google` in place of `openai` to test another configured provider.

## Connect the notebook-generation skill

Replace fixture selection with a call to the team's generator that receives the prompt and paper contents. Keep the expected values on the evaluation side. This fixture checks for a Group B control and a visible output with `data-testid="estimate"`.

Run generated notebooks in an isolated environment with no credentials or writable access to your checkout. The fixture runner gives the two hand-written notebooks a temporary working directory and a limited set of environment variables.
