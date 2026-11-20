# Method diagrams

Draw **what the paper did** (its method or analysis pipeline) as a hand-drawn Mermaid flowchart laid out with ELK, and let the reader step through it. Detail follows the reader's explanation level. Use it when the **method diagrams** component is included and the contribution is a sequence of steps: an architecture, an algorithm, a processing pipeline, or an analysis with branches.

- **Used from:** [`SKILL.md`](../SKILL.md), when method diagrams are included. Build the stage graph in Step 2; draw it in Step 4.
- **Follows:** [`explanation-levels.md`](explanation-levels.md). Same mechanism at every level, accurate at every level, numbers keep their conditions. Drive the view from its `reader_level` picker (§9); don't add a second one.
- **Renders with:** [`assets/mermaid_view.py`](../assets/mermaid_view.py) (`MermaidView`). Copy it next to the notebook, add `anywidget` and `traitlets` to the PEP 723 dependencies, and import it in the cell that imports `marimo`. Not `mo.mermaid`: its default layout overlaps group boxes and routes arrows through labels.
- **Versus [`dynamic_figure_annotation.md`](dynamic_figure_annotation.md):** that one annotates every main-text figure the paper printed. This one draws the method ourselves, when the paper has no figure of the pipeline or the reader needs a level-aware view. A notebook can use both.

## 1. Stage graph

Extract the method as data before drawing, so every level's view comes from one source. Write it as a Python literal (a dict with `stages` and `edges` lists) in its own cell with `hide_code=True`, named descriptively (`method_graph`), so the notebook stays one file. Put the helpers that draw and check it in `@app.function(hide_code=True)` cells.

**Stage fields:** `id` (a valid identifier, not a Mermaid keyword such as `end` or `class`), `label` (short verb phrase), `group` (the phase), `ref` (section, figure, or table), or `inferred` (`true` or a reason) when the paper doesn't state the step, `what` (two or three sentences), `params` (settings, each with its condition), and optionally `input` and `pools` (§3) and `demo` (what our demo does here).

**Edge fields:** `from`, `to`, `ref` or `inferred`, optional `data` (what flows), and optional `kind` with a `label`:

| `kind` | For | `label` says |
|---|---|---|
| `branch` | Which path a case takes | The condition |
| `loop` | Repetition | The rule and count |
| `split` | One output sent different ways (observed vs. permuted) | The split's name |
| `parallel` | Copies side by side (heads, folds) | What runs in parallel |

## 2. One view per level

| Level | View | Draws | Side panel |
|---|---|---|---|
| Child, Teen | Overview | One box per group, left to right; only labels of `kind` edges | Label, `ref`, `what` |
| Undergrad | Detail | Every stage, boxed by group | Same |
| Grad student, Expert | Spec | Detail plus short `params` and edge `data` (rule 6) | Plus full `params` and each incoming edge's `data` |

- Dash inferred stages and edges.
- Write group titles and `kind` labels in plain words: they are all Child and Teen readers see.
- Generate the Mermaid source with one function of (graph, view). Don't add `<br>` breaks; Mermaid wraps labels.
- Build `MermaidView`'s `steps` from the graph, one per stage: the node to highlight (its group in Overview), the arrows into it, and the side-panel text. The widget steps through them (Prev / Next, arrow keys, clicking a node), highlights the node and its incoming arrows, and pans to them without redrawing. Create the widget in its own cell that re-runs only when the paper changes, and set `source` and `steps` from the cell that reads the level, so changing level keeps the step.

Transformer encoder, Overview:

```text
flowchart LR
  g0["Text to vectors"] --> g1["Words share information (8 heads in parallel)"] --> g2["Each word refined"]
  g2 -->|"repeat: N = 6 layers"| g1
```

## 3. Rules

Run these as a check under the figure; it's ready when the check reports nothing.

1. Every stage and edge has a `ref` or is `inferred`.
2. Every `kind` edge has a `label`.
3. Every stage has an incoming edge, unless it's first in its group or marked `input` (data or parameters entering mid-group). Anything else is a forgotten edge.
4. A stage receiving several splits either says the paper pools them (`pools`) or each split gets its own route.
5. A branch, split, or parallel edge inside one group vanishes in Overview: split the group, or name the structure in its title and list it in the graph's `named`.
6. Spec view inlines `params` and `data` only up to ~40 characters; longer params show "⋯" and go to the side panel.
7. Group titles ≤ ~50 characters and stage labels ≤ ~40, so neither wraps into a tall block.

The limits come from rendering five papers; tune them rather than drop them. The check can't see where arrows land: `MermaidView` slides group titles clear of arrows, or halos the letters when the group is too narrow. Other overlaps only show in the render (§4).

## 4. Check the render

Render each view at the first, middle, and last step and look at it: a browser screenshot when pairing live, or `marimo export html` plus headless Chrome. Look for overlapping groups, arrows through node or edge labels, a Spec view taller than ~2 screens, and the highlight on the wrong box. Fix the data or the rules, not one figure by hand.

Re-running the cell that defines the graph resets the level picker and step slider to their defaults.

## Open questions

- Should Overview step through groups instead of stages?
- Should groups have a separate plain-language title for Child and Teen?
- Move the check into `scripts/` so `validate_notebook.py` runs it?
