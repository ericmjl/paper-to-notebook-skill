# Notebook evaluation

These evals check three things a notebook should do when teaching a paper. The current cases use a [synthetic paper](fixtures/dummy-paper.md) and prepared notebooks with known good and bad outputs. They provide examples for testing the evaluator before connecting it to the notebook-generation skill.

| Check | What it asks | API key |
| --- | --- | --- |
| [Table accuracy](table-eval.yaml) | Are the headings, group labels, values, and units the same as in the paper? | None |
| [Explanation fidelity](judge-eval.yaml) | Does the notebook draw conclusions that the paper supports? | OpenAI |
| [Widget behavior](promptfooconfig.yaml) | Does changing the input produce the expected output? | None |

## How a case runs

1. Promptfoo reads a case from a CSV. The row identifies a paper and the notebook to run.
2. [The notebook provider](notebook-provider.mjs) loads those files. [The Python runner](inspect-programmatically.py) executes the notebook through marimo and extracts the emitted table, prose, or widget result.
3. The table and widget checks compare the outputs with expected values in their CSVs. The judge check sends the paper, emitted prose, and table to a model with a rubric. Promptfoo records the verdict and its reason.

## Start with table accuracy

The table check compares the column headings and ordered cells with the expected table in [table_test_cases.csv](table_test_cases.csv). It ignores styling and normalizes whitespace.

- [table-copy.py](fixtures/table-copy.py) shows Group A at 12 seconds and Group B at 8 seconds. It should pass.
- [table-swapped.py](fixtures/table-swapped.py) has the same numbers but assigns them to the wrong groups. It should fail.

Install Node 24 and [uv](https://docs.astral.sh/uv/getting-started/installation/). Run the commands from the repo root. uv selects Python 3.12 and can download it if needed.

```sh
export PROMPTFOO_CONFIG_DIR="$PWD/evals/.promptfoo"
uv run --no-project --python 3.12 --with-requirements evals/requirements.txt -- \
  npx --yes promptfoo@0.126.0 eval -c evals/table-eval.yaml --no-cache
```

Expect **1 passed, 1 intentional failure, 0 errors**. The deliberately bad notebook triggers a nonzero exit status. Look for a reason showing the swapped Group A and Group B values.

## Judge the notebook's explanation

Both [judge cases](judge_test_cases.csv) reproduce the table correctly. [The faithful notebook](fixtures/table-copy.py) explains that the numbers are descriptive and cannot establish causation. [The misleading notebook](fixtures/table-causal.py) claims that assignment to Group B caused faster completion. The rubric asks GPT-4.1 mini to identify the wording or omission behind its verdict and point to the relevant statement in the paper.

If the repo root has no `.env` file, copy [the template](.env.example) there with `cp evals/.env.example .env`. Set `OPENAI_API_KEY` in that local file. Git ignores the file. From the repo root:

```sh
export PROMPTFOO_CONFIG_DIR="$PWD/evals/.promptfoo"
uv run --no-project --python 3.12 --with-requirements evals/requirements.txt -- \
  npx --yes promptfoo@0.126.0 eval -c evals/judge-eval.yaml --env-file .env --no-cache
```

The run sends the synthetic source and notebook output to OpenAI for two model judgments. Expect a pass for the faithful explanation and a fail for the causal claim. In the viewer, expand the rubric assertion for each case to see what the judge relied on. If both rows show an API authentication or quota message, the requests ended before grading.

## Check widget output

The widget smoke test reads two cases from [test_cases.csv](test_cases.csv). The runner executes each notebook with marimo's `app.run()`, first with its default input and then with Group B supplied programmatically. Promptfoo compares the emitted values with the CSV.

| Case | Group A | Group B | Expected result |
| --- | --- | --- | --- |
| Reactive notebook | 12 seconds | 8 seconds | Pass |
| Deliberately stale notebook | 12 seconds | 12 seconds | Fail the Group B assertion |

### Run from the repository root

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

The fixture eval needs no API keys. For a separate live provider check, use the same root `.env` file and set the key for one provider. Git ignores the local `.env` and the eval results.

```sh
npx --yes promptfoo@0.126.0 eval -c evals/providers-smoke.yaml \
  --env-file .env --filter-providers openai --no-cache
```

Use `anthropic` or `google` in place of `openai` to test another configured provider.

## Connect the notebook-generation skill

To evaluate the skill itself, replace fixture selection with a call to the team's generator that receives the prompt and paper contents. Then run the generated notebook through the same checks. Keep the expected values on the evaluation side. For the widget fixture, the Python mode supplies Group B directly and the browser mode clicks the Group B control. Both read an estimate marked with `data-testid="estimate"`.

Run generated notebooks in an isolated environment with no credentials or writable access to your checkout. The fixture runner gives the two hand-written notebooks a temporary working directory and a limited set of environment variables.
