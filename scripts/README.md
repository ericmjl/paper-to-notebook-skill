# scripts/

Helper scripts for maintainers and agents. Run Python via **`uv run`**, not global `pip install`.

- `validate_notebook.py` — verify a generated marimo notebook: Python syntax, `marimo check --strict`, and (with `--run`) a smoke run of the notebook as a script. It also warns, without failing, when a cell, `@app.function`, or `app.setup` block does not set `hide_code=True`. A visible cell is allowed when the code itself is the teaching point; the warning names it so that stays a choice. When the notebook builds two or more `FigureAnnotatorWidget` tours, it warns, without failing, if they are not all values of a single `mo.ui.tabs`. If the notebook has a `# paper-to-notebook-skill-components:` comment, the script warns when an included component (`figure-walkthroughs`, `method-diagrams`, `final-quiz`, `explain-levels`, `equations`) is missing and does not require skipped ones. The `explain-levels` marker is `ExplainLevels`. The `equations` marker is `TangleLatex`. Notebooks without the comment skip those component checks. Missing `FigureAnnotatorWidget` is a failure unless the comment opts out of `figure-walkthroughs`. It also warns, without failing, when no paper figure image is embedded or referenced, when more than half of the long `mo.md` strings cite no paper anchor (Fig./Figure/Eq./Table/Section/§), and when notebook prose trips a mechanical processing-friendly-prose check (`check_prose.py`: very long sentences or paragraphs, clear noun stacks of four or more nouns or a hyphenated compound stacked onto further nouns, inanimate subjects with person-verbs, ad-hoc denominal verbs from the skill's examples). A `[prose]` warning is a sentence to look at again, not a sentence that must be rewritten. Keep clear wording even if it stays flagged. When the notebook has inline ExplainLevels level text, it also warns on `check_levels.py` length and voice issues, and on missing quotes in that copy or in inline quiz questions (`check_quotes.py`). Pass `--paper paper.txt` to warn when a quoted passage is not in the paper. Dependencies are declared inline (PEP 723), so `uv run` installs them.

```bash
uv run scripts/validate_notebook.py ../path/to/paper_explainer.py --run
```

- `check_prose.py` — mechanical processing-friendly-prose warnings for markdown, ExplainLevels level text, TangleLatex notes and "what to try" cells, figure-tour HTML, quiz copy, and flowchart step descriptions. Warnings are not failures. Each one marks a sentence to look at again; rewrite only when the change is clearer. Keep wording that is already clear and natural, including ordinary scientific terms, even if it stays flagged. The validator runs this after a successful parse. Optional extra, not required: `uvx proselint path/to/notebook.py` (do not install it globally).

- `check_quotes.py` — check that every quoted passage in a ladder or quiz (Markdown or JSON) appears word for word in the paper's plain text, for [`resources/explanation-levels.md`](../resources/explanation-levels.md). Lists each quote it can't find. A ``"`` after a digit (``5"``) is not a quote mark. A file with no quotes prints a warning and still exits 0. The validator runs this on inline ladder and quiz copy.

```bash
uv run scripts/check_quotes.py paper.txt ladder.md
```

- `check_levels.py` — count each explanation-ladder level's words and sentences against the caps in [`resources/explanation-levels.md`](../resources/explanation-levels.md) §7, and flag reporting-voice phrases. Exits nonzero with a clear message when the file has no levels. The validator runs this on inline ExplainLevels level text.

```bash
uv run scripts/check_levels.py ladder.md
```

- `figure_annotation_helper.py` — CLI helper for [`resources/dynamic_figure_annotation.md`](../resources/dynamic_figure_annotation.md): generates a private 100×100 percentage slice grid (`grid`), isolates foreground ink or colored traces to compute centered percentage bounding boxes (`isolate`), and renders a Visual Centering Audit Contact Sheet with center crosshairs (`audit`).

```bash
uv run scripts/figure_annotation_helper.py grid --image resources/figures/fig1.webp --output /tmp/fig1_grid.png
uv run scripts/figure_annotation_helper.py isolate --image resources/figures/fig1.webp --window 51.5,10.5,58.0,15.5 --channel any --output /tmp/box.json
uv run scripts/figure_annotation_helper.py audit --image resources/figures/fig1.webp --annotations /tmp/annotations.json --output /tmp/audit_sheet.png
```

Keep script dependencies in a `pyproject.toml` at repo root when the first script lands (**TODO**).