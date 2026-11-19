# scripts/

Helper scripts for maintainers and agents. Run Python via **`uv run`**, not global `pip install`.

**Planned contents:**

- `validate_notebook.py` — verify a generated marimo notebook (syntax, `marimo check`, optional smoke run). **TODO:** implement.

Example (once the script exists):

```bash
uv run scripts/validate_notebook.py ../path/to/paper_explainer.py
```

Keep script dependencies in a `pyproject.toml` at repo root when the first script lands (**TODO**).