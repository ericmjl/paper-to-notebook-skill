# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.14.0",
#     "anywidget>=0.9.0",
#     "traitlets>=5.14.0",
# ]
# ///
# paper-to-notebook-skill-components: explain-levels

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import re
    import sys
    from pathlib import Path

    import marimo as mo

    here = Path(__file__).resolve().parent
    for folder in (here.parent / "assets", here):
        if (folder / "explain_levels.py").is_file():
            sys.path.insert(0, str(folder))
            break
    from explain_levels import ExplainLevels

    return ExplainLevels, Path, mo, re


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # ExplainLevels: the paper's main point at five levels

    A standalone demo of the `ExplainLevels` anywidget. The five rungs are
    the worked UMAP ladder in
    [`examples/ladder-umap.md`](examples/ladder-umap.md), from McInnes, Healy
    & Melville (2018), arXiv:1802.03426 (v3). Anchored to the **Abstract** and
    **Secs. 1–3, 5–6**.

    The one-line summary sits above the reader's own level. Change the
    dropdown to drive the widget. Generated notebooks hide the tabs and
    leave out a check under the rung; the final quiz is matched to the level.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    LEVELS = ["Child", "Teen", "Undergrad", "Grad student", "Expert"]
    reader_level = mo.ui.dropdown(
        options=LEVELS,
        value="Undergrad",
        label="Explain it at this level:",
    )
    reader_level
    return LEVELS, reader_level


@app.cell(hide_code=True)
def _(Path, re):
    ladder_path = Path(__file__).resolve().parent / "examples" / "ladder-umap.md"
    ladder_source = ladder_path.read_text(encoding="utf-8")
    summary_match = re.search(
        r"^## One-line summary\n\n(.+?)\n\n## ",
        ladder_source,
        flags=re.S | re.M,
    )
    UMAP_SUMMARY = summary_match.group(1).strip() if summary_match else ""
    UMAP_LEVELS = []
    for match in re.finditer(
        r"^> \*\*\d · ([^.]+)\.\*\* (.*?)(?=^> \*\*\d · |^(?!>)\S|\Z)",
        ladder_source,
        flags=re.S | re.M,
    ):
        body = re.sub(r"^> ?", "", match.group(2), flags=re.M).strip()
        UMAP_LEVELS.append({"name": match.group(1), "text": body})
    return UMAP_LEVELS, UMAP_SUMMARY


@app.cell(hide_code=True)
def _(ExplainLevels, UMAP_LEVELS, UMAP_SUMMARY, mo, reader_level):
    umap_ladder = mo.ui.anywidget(
        ExplainLevels(
            title="UMAP: Uniform Manifold Approximation and Projection",
            paper_ref="Abstract, Secs. 1–3, 5–6 (McInnes, Healy & Melville 2018)",
            summary=UMAP_SUMMARY,
            tabs=False,
            level=reader_level.value,
            levels=UMAP_LEVELS,
        )
    )
    umap_ladder
    return (umap_ladder,)


@app.cell(hide_code=True)
def _(mo, umap_ladder):
    mo.md(f"""
    The widget's synced `level` trait is **{umap_ladder.value["level"]}**
    (`paper_ref` is Abstract, Secs. 1–3, 5–6). This notebook has one ladder,
    driven by `level=reader_level.value`. See
    [`explain_levels.md`](explain_levels.md).
    """)
    return


if __name__ == "__main__":
    app.run()
