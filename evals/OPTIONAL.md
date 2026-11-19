# Optional eval checks

Follow the [eval setup instructions](README.md#set-up-the-evals) and run these commands from the repo root.

## Widget output

The widget smoke test runs the two notebooks in [test_cases.csv](test_cases.csv) through marimo's `app.run()`. It checks the output with the default Group A input, then supplies Group B through Python.

```sh
uv run --no-project --python 3.12 --with-requirements evals/requirements.txt -- \
  npx --yes promptfoo@0.126.0 eval -c evals/promptfooconfig.yaml --no-cache
```

Expect **1 pass, 1 intentional failure, 0 errors**. The stale notebook stays at 12 seconds and fails the Group B assertion.

## Browser interaction

This experimental path uses Playwright to open the notebook, click the Group B control, and read the result. It needs its own browser installation.

```sh
cd evals
npm install
npx playwright install chromium --only-shell
cd ..

MARIMO_CHECK_MODE=browser uv run --no-project --python 3.12 \
  --with-requirements evals/requirements.txt -- \
  npx --yes promptfoo@0.126.0 eval -c evals/promptfooconfig.yaml --no-cache
```

## Model credentials

Use the root `.env` file and set the key for the provider you want to test. Use the [template](.env.example) for variable names.

```sh
npx --yes promptfoo@0.126.0 eval -c evals/providers-smoke.yaml \
  --env-file .env --filter-providers openai --no-cache
```

Use `anthropic` or `google` in place of `openai` to test a different configured provider.
