# scripts/

Helper scripts for maintainers and agents. Run Python via **`uv run`**, not global `pip install`.

- `validate_notebook.py` — verify a generated marimo notebook: Python syntax, `marimo check --strict`, and (with `--run`) a smoke run of the notebook as a script. Dependencies are declared inline (PEP 723), so `uv run` installs them.

```bash
uv run scripts/validate_notebook.py ../path/to/paper_explainer.py --run
```

Keep script dependencies in a `pyproject.toml` at repo root when the first script lands (**TODO**).