# Method diagrams

Guide an agent to draw **what the paper did** (its method or analysis pipeline) as a hand-drawn Mermaid flowchart laid out with ELK. The reader steps through it one stage at a time. The diagram follows the explanation level the reader picked: the same pipeline, drawn with more detail at higher levels.

Use it for the "Step-through aligned with the paper" part of the learning path, whenever the paper's contribution is a sequence of steps: an architecture, an algorithm, a data-processing pipeline, or an analysis with branches and permutation tests.

---

## Dependencies & Related Resources

- **Used from**: [`SKILL.md`](../SKILL.md). Build the stage graph in **Step 2**; draw it in **Step 4**.
- **Levels**: [`explanation-levels.md`](explanation-levels.md). The diagram is one more rung of the explanation ladder and obeys its rules (one mechanism at every level; accurate at every level; numbers carry their conditions).
- **Widget**: [`assets/mermaid_view.py`](../assets/mermaid_view.py). `MermaidView` (`anywidget`) renders Mermaid with ELK in the hand-drawn look. Copy it next to the notebook and add `anywidget` and `traitlets` to the PEP 723 dependencies.

Do **not** use `mo.mermaid` for these figures. It uses Mermaid's default (dagre) layout, which overlaps group boxes and routes arrows through labels on real pipelines, and it shrinks the diagram to the column width.

---

## 1. Write the stage graph first, as data

Extract the method into a small, grounded graph before drawing anything. Keep it as data (for example `data/methods.json`) so every level's view is generated from the same source and cannot drift apart.

**Stages:**

| Field | Meaning |
|---|---|
| `id` | Short identifier. Must be a valid identifier and not a Mermaid keyword (`end`, `graph`, `subgraph`, `class`, `style`, `click`, `direction`, ...). |
| `label` | What the step does, as a short verb phrase. |
| `group` | The phase it belongs to. Groups are what lower levels see. |
| `ref` | Where the paper says this (section, figure, table). |
| `inferred` | Instead of `ref`: `true`, or a reason, when the paper doesn't state the step and we added it to connect the stages. |
| `what` | Two or three sentences for the side panel. |
| `params` | Settings and sizes, each with its condition (dataset, cohort, figure). |
| `input` | `true` for data or parameters that enter the pipeline partway through a group. |
| `pools` | `true` only when the paper says it pools different data splits at this stage. |
| `demo` | Optional: what our notebook demo does here, labeled as ours. |

**Edges:** `from`, `to`, `ref` or `inferred`, optional `data` (what flows along it), and optional `kind` with a `label`:

| `kind` | Use for | `label` says |
|---|---|---|
| `branch` | A decision: which path a case takes | The condition |
| `loop` | Repetition | The repeat rule and count |
| `split` | One output sent different ways (observed vs. permuted, train vs. test) | The split's name |
| `parallel` | Copies run side by side (heads, folds, segments) | What runs in parallel |

Also record `named`: the groups whose title names structure hidden inside them (see rule 5 in §3).

---

## 2. Draw one view per level

Every view is generated from the same graph. Pick the view from the reader's level with the same level picker the ladders use.

| Level | View | Draws | Side panel for the current step |
|---|---|---|---|
| 1 · Child, 2 · Teen | **Overview** | One box per group, left to right. Only edges between groups, and only labels of branch, loop, split, and parallel edges. A loop inside one group becomes a self-loop. | The step's label, `ref`, and `what` |
| 3 · Undergrad | **Detail** | Every stage, boxed by group, top to bottom. Branch, loop, split, and parallel labels. | Same as Overview |
| 4 · Grad student, 5 · Expert | **Spec** | Detail plus each stage's `params` and each edge's `data`, inline only when short (see §3). | Detail's panel plus full `params` and what the stage receives (each incoming edge's `data` and source) |

Across all views:

- **Highlight the current step.** Give the current stage (or its group, in Overview) a thick orange outline, and drive it from a step slider.
- **Dash what we inferred.** Dash inferred stages and edges, and label inferred steps in the side panel.
- **Write group titles for the lowest level that sees them.** Child and Teen readers see only group titles and consequential-edge labels. Write those in plain words ("Words share information (8 heads in parallel)"), and keep technical names for stage labels.

Example, the Transformer encoder (Vaswani et al., 2017). Overview, for Child and Teen:

```text
flowchart LR
  g0["Text to vectors"]
  g1["Words share information (8 heads in parallel)"]
  g2["Each word refined"]
  g0 --> g1 --> g2
  g2 -->|"repeat: N = 6 layers"| g1
```

Spec, for Grad student and Expert (abridged):

```text
flowchart TB
  subgraph g0["Text to vectors"]
    direction LR
    tok["Byte-pair encoding (~37k shared tokens)"]
    emb["Input embedding (d_model = 512)"]
  end
  ...
  tok -->|"token ids"| emb
  norm2 -->|"repeat: N = 6 layers"| attn
```

Generate the Mermaid source, don't hand-write it: one function from (stages, edges, view, current step) to Mermaid text. Pass it to `MermaidView(source=...)` without manual `<br>` line breaks; the widget lets Mermaid wrap labels itself.

---

## 3. Rules that keep any paper's diagram readable

Encode these as a check that runs on the stage graph and is shown under the figure, so problems surface when the data loads, not after someone notices a messy figure. The figure is ready when the check returns nothing.

**Grounding:**

1. **Every stage and edge has a `ref`, or is marked `inferred`.**
2. **Branch, loop, split, and parallel edges have a label.** An unlabeled branch hides the condition the reader needs.
3. **Every stage has an incoming edge, unless it's an input.** A stage listed **first in its group** counts as an input automatically, since groups start where their data comes in. Any other stage with nothing feeding it is either a parameter or dataset entering mid-group (mark `input`) or a forgotten edge.
4. **No silent pooling.** If one stage receives several different splits, either the paper pools them (say so in the label, set `pools`) or each split needs its own route.
5. **Groups don't hide structure.** A branch, split, or parallel edge inside one group disappears in the Overview. Either split the group, or name the structure in the group title and list the group in `named`. The same applies when splits enter one group at different stages.

**Layout** (limits found by rendering five real papers; tune them, don't drop them):

6. **Inline only short details.** In the Spec view, show `params` and edge `data` inside the figure only when they fit in about 40 characters. Mark a box whose params were left out with "⋯", and put the full text in the side panel. In testing, inlining full params made one analysis pipeline four screens tall; with this rule it was half that, and nothing was lost.
7. **Group titles fit in about 50 characters.** Arrows into a group cross its title, and a long title wraps into a tall block that every incoming arrow cuts through. Move the detail into the stages' `what`, and keep any name of hidden structure (rule 5).
8. **Stage labels stay short phrases** (about 40 characters). Counts and conditions belong in `params`.

---

## 4. Verify by looking at it

The check catches data problems; only rendering catches layout problems. Before handing off:

1. Run the check for every paper in the notebook; it must report nothing.
2. Render every view (Overview, Detail, Spec) and step the slider to the first, a middle, and the last stage.
3. Look at the rendered page. When pairing on a live notebook, screenshot it in the browser; otherwise export with `marimo export html` and screenshot that with headless Chrome. Look for:
   - group boxes overlapping, or titles hidden behind another group;
   - arrows crossing titles or labels;
   - a figure taller than about two screens in the Spec view (move more detail into the side panel);
   - text too small to read, or the figure scrolling sideways;
   - the highlight on the wrong box.
4. Fix the **data or the rules**, not one figure by hand, so the next paper benefits.

---

## 5. Pitfalls

- **Reloading the data resets the widgets.** Re-running the cell that loads the stage graph rebuilds every dropdown and slider that depends on it, so the reader's paper, level, and step jump back to their defaults.
- **`mo.mermaid` and `MermaidView` disagree.** Check the figure in the renderer the notebook actually uses.
- **Long numbers lose their condition.** When a figure shortens `params`, the condition (cohort, table, figure panel) must survive in the side panel.
- **A tidy figure can still be wrong.** The same accuracy rules as the ladders apply: simplify by leaving out, never by drawing a step the paper didn't take without marking it inferred.

## Open questions

- Whether Overview should step through groups instead of stages (currently it steps through stages and highlights the group).
- Whether group titles should carry a separate plain-language title for Levels 1–2.
- Moving the stage-graph check into `scripts/` so `validate_notebook.py` can run it.
