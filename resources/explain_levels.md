# ExplainLevels widget

The **five-level explanation ladder** as a reusable anywidget. One mechanism, five rungs, a check under the open rung. Use it instead of wiring `mo.ui.tabs` and `show_check` by hand.

- **Used from:** [`SKILL.md`](../SKILL.md) [Tools](../SKILL.md#tools); copy [`assets/explain_levels.py`](../assets/explain_levels.py) next to the notebook.
- **How to write the five levels:** [`explanation-levels.md`](explanation-levels.md) (prerequisite profiles, mechanism spine, simplification ledger, analogy map, level-matched checks). Worked ladders live in [`examples/`](examples/) (`ladder-umap.md`, `ladder-influenza-reassortment.md`).
- **Renders with:** `ExplainLevels`. Add `anywidget` and `traitlets` to the notebook's PEP 723 block. Not `mo.ui.tabs` plus a separate check cell: the widget holds the tabs, the prose, and the check.

A companion change documents `ExplainLevels` as a default notebook tool and teaches the validator to look for it. This file is the widget contract.

---

## 1. Write the levels first

Follow [`explanation-levels.md`](explanation-levels.md) before touching the widget:

1. Prerequisite profile per paper.
2. One-sentence mechanism spine; every level explains that spine.
3. Simplification ledger (leave things out, never say something false).
4. One analogy, mapped, with its limit stated by Level 3.
5. A check at each level: Child *explain*, Teen *predict*, Undergrad *apply*, Grad student *apply and critique*, Expert *critique*.

The default names are **Child**, **Teen**, **Undergrad**, **Grad student**, **Expert**. They are shorthand for prerequisites, not age. The widget will render other names if you pass them; generated notebooks should keep the five.

Every ladder needs a **paper anchor** (`paper_ref`): a section, figure, equation, or algorithm number from the text you actually read. That is the [stick-to-the-paper](../SKILL.md#stick-to-the-paper) rule. The widget will start without one so a ladder can be tried alone; generated notebooks must still pass `paper_ref`. `assert_paper_ref()` in `assets/explain_levels.py` is the helper a validator can call.

---

## 2. Trait schema

`ExplainLevels` is an `anywidget.AnyWidget` with inline `_esm` / `_css` and these synced traits:

| Trait | Type | Role |
|---|---|---|
| `title` | str | Heading above the level control. |
| `levels` | list[dict] | The rungs. See below. |
| `level` | int or str in, **str out** | Open rung. Accepts a 0-based index or a name (case-insensitive). The synced value is the canonical name, so a dropdown of names can drive it and the widget can report which tab is open. |
| `paper_ref` | str | Paper location for this ladder. Optional on the constructor; required by the stick-to-the-paper rule. |
| `responses` | list[str] | Committed answers, one per level (`""` if unanswered). Filled from the browser. |

Each entry of `levels`:

```python
{
    "name": "Undergrad",          # required
    "text": r"Markdown for this rung. HTML is escaped. $x$ and $$x$$ are KaTeX.",
    "check": {                    # optional
        "question": "…",          # required when check is present
        "why": "Reasoning, with the paper location.",
        # then exactly one of:
        "options": ["…", "…"],    # multiple choice; correct is that option string
        "correct": "…",
        # or:
        "correct": 0.53,          # numeric; optional tolerance (default 0.01)
        "tolerance": 0.02,
        # or:
        "correct": None,          # open; why is the model answer
    },
}
```

The widget stores a normalized `check` with a `kind` of `choice`, `numeric`, or `open`. Authors do not pass `kind`.

Helpers in the same module (stdlib-style, for tests and validators):

- `DEFAULT_LEVEL_NAMES`
- `resolve_level(level, names) -> int`
- `normalize_level(level, names) -> str`
- `validate_check(check)`, `validate_levels(levels)`
- `evaluate_response(check, response) -> bool | None`
- `assert_paper_ref(paper_ref) -> str`
- `ExplainLevelsError`

---

## 3. Usage

PEP 723 at the top of the notebook:

```python
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.14.0",
#     "anywidget>=0.9.0",
#     "traitlets>=5.14.0",
# ]
# ///
```

Copy `assets/explain_levels.py` next to the notebook (the same pattern as `PaperQuiz` and `MermaidView`) and import it in the cell that imports `marimo`.

### Single ladder

Usable on its own. The widget draws segmented level buttons, the current explanation, and that level's check. Arrow keys (and `1`–`5`) change the rung; type in a numeric/open check is left alone.

```python
@app.cell(hide_code=True)
def _(ExplainLevels, mo):
    umap_ladder = mo.ui.anywidget(ExplainLevels(
        title="UMAP's two-phase mechanism",
        paper_ref="Secs. 2–3, Algs. 1–5",
        level="Undergrad",
        levels=UMAP_LEVELS,  # from a hide_code data cell
    ))
    umap_ladder
    return (umap_ladder,)
```

Read the open rung in a **different** cell (`mo.ui.anywidget` forbids reading `.value` in the cell that created the widget):

```python
@app.cell(hide_code=True)
def _(mo, umap_ladder):
    mo.md(f"Open rung: **{umap_ladder.value['level']}**.")
    return
```

### Shared picker across several ladders

One dropdown near the top of the notebook, same default as [`explanation-levels.md`](explanation-levels.md) §9. Each ladder cell reads `reader_level.value` and remounts on that rung. Clicking a widget's own buttons still updates that widget's `level` trait; it does not rewrite the dropdown unless you wire that yourself.

```python
@app.cell(hide_code=True)
def _(mo):
    LEVELS = ["Child", "Teen", "Undergrad", "Grad student", "Expert"]
    reader_level = mo.ui.dropdown(
        options=LEVELS,
        value="Grad student",
        label="Explain it at this level:",
    )
    reader_level
    return LEVELS, reader_level


@app.cell(hide_code=True)
def _(ExplainLevels, mo, reader_level):
    graph_ladder = mo.ui.anywidget(ExplainLevels(
        title="Fuzzy k-neighbour graph",
        paper_ref="Sec. 3.1, Alg. 3",
        level=reader_level.value,
        levels=GRAPH_LEVELS,
    ))
    graph_ladder
    return (graph_ladder,)


@app.cell(hide_code=True)
def _(ExplainLevels, mo, reader_level):
    layout_ladder = mo.ui.anywidget(ExplainLevels(
        title="Cross-entropy layout",
        paper_ref="Sec. 3.2, Alg. 5",
        level=reader_level.value,
        levels=LAYOUT_LEVELS,
    ))
    layout_ladder
    return (layout_ladder,)
```

Remounting from the picker rebuilds the widget, so committed check answers on that instance reset. Answers survive tab changes *inside* one mounted widget.

---

## 4. What the reader sees

- Segmented buttons for the rungs (not a second notebook-level dropdown per ladder).
- Markdown explanation for the open rung, with KaTeX for `$…$` / `$$…$$`. Raw HTML in `text` is escaped.
- The check for that rung: radio options, a numeric field, or a short text area. Choice clicks submit immediately; numeric/open use **Check** (or Enter in the numeric field).
- Feedback: **Right.** / **Not quite.** plus `why`, or **Compare with ours:** for an open check.
- Keyboard: focus the widget, then `←` `→`, `Home` / `End`, or `1`–`5`.

---

## 5. Demo

[`explain_levels_example.py`](explain_levels_example.py) is a small marimo notebook that loads the UMAP ladder from [`examples/ladder-umap.md`](examples/ladder-umap.md), with a shared picker driving one `ExplainLevels` widget.

```bash
uv run scripts/validate_notebook.py resources/explain_levels_example.py
uvx marimo edit --sandbox resources/explain_levels_example.py
```
