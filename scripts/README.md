# scripts/

Helper scripts for maintainers and agents. Run Python via **`uv run`**, not global `pip install`.

- `validate_notebook.py` — verify a generated marimo notebook: Python syntax, `marimo check --strict`, and (with `--run`) a smoke run of the notebook as a script. It also warns, without failing, when a cell, `@app.function`, or `app.setup` block does not set `hide_code=True`. A visible cell is allowed when its code is the teaching point; the warning names it so that stays a choice. When the notebook builds two or more `FigureAnnotatorWidget` tours, it warns, without failing, if they are not all values of a single `mo.ui.tabs`. Dependencies are declared inline (PEP 723), so `uv run` installs them.

```bash
uv run scripts/validate_notebook.py ../path/to/paper_explainer.py --run
```

- `figure_annotation_helper.py` — CLI helper for [`resources/dynamic_figure_annotation.md`](../resources/dynamic_figure_annotation.md): generates a private 100×100 percentage slice grid (`grid`), isolates foreground ink or colored traces to compute centered percentage bounding boxes (`isolate`), and renders a Visual Centering Audit Contact Sheet with center crosshairs (`audit`).

```bash
uv run scripts/figure_annotation_helper.py grid --image resources/figures/fig1.webp --output /tmp/fig1_grid.png
uv run scripts/figure_annotation_helper.py isolate --image resources/figures/fig1.webp --window 51.5,10.5,58.0,15.5 --channel any --output /tmp/box.json
uv run scripts/figure_annotation_helper.py audit --image resources/figures/fig1.webp --annotations /tmp/annotations.json --output /tmp/audit_sheet.png
```

Keep script dependencies in a `pyproject.toml` at repo root when the first script lands (**TODO**).