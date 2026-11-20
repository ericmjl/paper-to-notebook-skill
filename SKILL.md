---
name: paper-to-notebook-skill
description: >
  Turn a research paper — provided as a PDF, HTML, or plain-text source
  (LaTeX, Markdown, or similar) — into a guided, runnable marimo learning
  notebook. Use when asked to make a paper explainer notebook, teach a paper
  interactively, or build a marimo walkthrough of a publication. Do not use
  for multi-paper literature reviews or non-marimo outputs unless the user
  explicitly changes the format.
---

# Paper to notebook

Steer an agent from **one paper** to a **runnable marimo notebook** that helps a reader understand that paper. The notebook is a lesson, not a summary page: plain-language explanation, interactive widgets where they help, and informal checks along the way. The writing must be intelligible and representative of the paper, not generic AI prose. Follow [Writing quality](#writing-quality).

This file is a skeleton. Lots of details will be filled in later. Items marked **TODO** are still undecided or only sketched.

## Contract

| | |
|---|---|
| **Input** | A paper as PDF, HTML, or plain-text source (LaTeX, Markdown, etc.). Path, URL, or identifier is fine as long as full text can be obtained. |
| **Output** | A runnable marimo notebook (`*.py`) the reader can open with `uvx marimo edit --sandbox …`. |

### Stick to the paper

The notebook teaches **this paper**. Every section is anchored to a specific part of the paper (section, equation, figure, or table number) and cites it.

Outside material is allowed only as the minimum background a reader at the chosen level needs to follow a specific passage. Keep it brief. Label it as background. It never replaces paper content.

- No tangents.
- No surveys of related work.
- No extra examples or datasets the paper doesn't use.
- No content from other papers except a one-line pointer when the paper itself depends on it.

The literature sample in [`resources/field-maturity.md`](resources/field-maturity.md) is only for classifying vocabulary. Do not turn it into notebook content.

When in doubt, cut.

Optional inputs to ask for if they are missing (do not block if the user only gives the paper):

- Starting audience or “adapt as I go.” Default working assumption: undergrad through graduate student, plus working professionals new to this paper or field, with some general scientific knowledge. **TODO:** tighten the default.
- Extra context: supporting information the user supplies (SI, a cited paper this paper depends on). Use it only as the minimum background for a specific passage, labeled as background. It is not a license to survey the field.
- Depth: full walkthrough vs. methods, results, or one figure.
- Output path and runtime constraints.
- Which notebook components to include (see [Choose notebook components](#choose-notebook-components)). Offer the four default tools, plus interactive equations when the paper has equations. The user may pick a subset.

Do **not** treat this skill as a tool for reviewing a large literature. That is a different job.

## Workflow

```
1. Ingest the paper (PDF / HTML / plain-text source)
2. Extract structure, terms, equations, figures, and gaps
3. Plan the learning path
   Then ask which components to include (all four is the default offer;
   also equations when the paper has them)
4. Generate the marimo notebook
5. Validate it runs with `uv run`, run the writing check, then hand off
```

### 1. Ingest the paper

Obtain the **full text**, not an abstract only. Branch on the input type; put format-specific notes in `resources/` and any helpers in `scripts/` (always `uv run`, never a global `pip install`).

- **PDF:** **TODO:** how to fetch and parse (text, math, figures, reading order). Flag failures rather than guessing.
- **HTML:** **TODO:** how to fetch and parse (main text vs. navigation/chrome, MathJax/MathML, figures).
- **Plain-text source (LaTeX, Markdown, etc.):** **TODO:** how to follow includes, bibliography, and figure files; how to keep equation and figure labels.

Record the paper's title, authors, year, and a stable link or identifier when available.

### 2. Extract structure, equations, and figures

Build an intermediate picture of the paper before writing any notebook. **TODO:** settle the data shapes for this step (see also the idea that sound intermediate structures make the rest easier).

Extract at least:

- Problem and contribution, in your own words.
- Prerequisite profile: what a reader at each level knows, doesn't know, and must be taught (see [Explaining at multiple levels](#explaining-at-multiple-levels)).
- Key concepts and **terms the paper uses but does not define** (core metadata or field terms). Example raised in design discussion: a paper about heart attacks that never explains “myocardial infarction.”
- Key equations, numbered as in the paper, with variables.
- Every main-text figure, enumerated before any notebook cells are written. For a PMC paper, take each `<fig>` `<label>` from the eutils XML. Record the label, what the figure encodes, whether underlying data appear to be available, and the image path — or that no image could be obtained. Do not drop a figure from this list. Supplementary figures only when the user asks. When figure walkthroughs are included, tour each of them: [`resources/dynamic_figure_annotation.md`](resources/dynamic_figure_annotation.md).
- Risk points for generation: heavy LaTeX or math, Greek-letter figure labels, other non-ASCII text.
- Obvious gaps in methods or reporting. Do not invent missing experimental results.

Classify **field maturity** (established, emergent, interdisciplinary, or mixed) using the rubric and lightweight literature sample in [`resources/field-maturity.md`](resources/field-maturity.md). Record the class, evidence, and which vocabulary-onboarding notebook components are required (glossary, disambiguation, terminology in flux).

**TODO:** whether to classify the paper as algorithm-like (coding exercises, reverse-engineer the method) vs. concept-like (agent-written explainer widgets). Chemistry examples used in discussion: mass balance, reaction kinetics, a new kinetic model.

### 3. Plan the learning path

Before writing cells, build an outline. Map each planned section to its paper anchor (section, equation, figure, or table number). Drop any section that has none.

Design a path a human can follow in one sitting. **TODO:** target duration.

Do not lock the whole notebook to a single reading level. Plan for **adaptive explanation**: the reader should be able to get a simpler or more advanced account of a hard passage. **TODO:** default direction — start simple and add complexity, or start high and step down when the reader is confused. Both were proposed; neither was chosen. The paper's main point gets an explanation ladder (see [Explaining at multiple levels](#explaining-at-multiple-levels)).

Suggested spine (adjust per paper):

1. Why this paper matters.
2. The explanation ladder: the paper's main point as a one-line summary, then the reader's own level (see [Explaining at multiple levels](#explaining-at-multiple-levels)).
3. Intuition or a toy example before heavy notation.
4. Setup: notation, assumptions, terms, and field vocabulary onboarding (glossary; disambiguation or terminology-in-flux when required—see [`resources/field-maturity.md`](resources/field-maturity.md)).
5. Core idea, tied to an equation or figure.
6. Step-through aligned with the paper.
7. For graduate-and-above readers, critique beats: does the experimental design address the stated question; is the statistical framework an appropriate choice; what is missing; what assumptions is the reader making.
8. Wrap-up: limitations, what to read next, citation.
9. If the final quiz is included: five multiple-choice questions on the paper, as the last section (see [Final quiz](#final-quiz)).

**TODO:** how far critique, results-section analysis, and figure-interpretation prompts go in the first version, versus a plain guided walkthrough.

If the user supplied extra sources, use them only as background for a specific paper passage, labeled as such. Do not plan a related-work survey. **TODO:** the mechanism for distinguishing sourced evidence from general knowledge, and whether a small concept map or “knowledge wiki” belongs here later.

### Choose notebook components

Before writing cells for a **new** notebook, ask the user whether to include **all** of these components (the default offer) or to pick which ones:

1. **Figure walkthroughs** — annotated tours of every main-text figure, in one `mo.ui.tabs` inside `wigglystuff.FloatingPanel` (`FigureAnnotatorWidget`; [`resources/dynamic_figure_annotation.md`](resources/dynamic_figure_annotation.md)). **Default on.** Omit only when the user explicitly opts out. If you cannot ask, include them.
2. **Method diagrams** — a Materials-and-Methods flowchart of the paper's pipeline (`MermaidView`; [`resources/method_diagrams.md`](resources/method_diagrams.md)). The flowchart is pannable and zoomable (drag, Ctrl/pinch zoom, +/− and Fit buttons).
3. **Final quiz** — five multiple-choice questions at the end of the notebook (`PaperQuiz`; [`resources/final-quiz.md`](resources/final-quiz.md)).
4. **Explain at five levels** — level picker, one-line summary, and the paper's main point at the reader's own level (`ExplainLevels` in [`assets/explain_levels.py`](assets/explain_levels.py); [`resources/explanation-levels.md`](resources/explanation-levels.md)).
5. **Interactive equations** — draggable variables in a key paper equation (`TangleLatex` from `wigglystuff`; [Tools](#tools)). **Default on when the paper has equations** whose behaviour the reader benefits from exploring (scaling laws, rate equations, loss functions, model parameters). Skip papers with no equations, purely definitional notation, or huge derivations. Mention it in the offer even when the paper has none, so the user can confirm. If you cannot ask, include it when the paper has such equations.

Build only the components they choose. If you cannot ask, or they do not answer, include all four, plus interactive equations when the paper has equations worth exploring, and say so at handoff.

Record the choice in a comment near the top of the notebook, after the script metadata. List only the components that are in:

```
# paper-to-notebook-skill-components: figure-walkthroughs, method-diagrams, final-quiz, explain-levels, equations
```

The validator reads that comment. A skipped component is not a failure, except figure walkthroughs: omitting `FigureAnnotatorWidget` without opting out in that comment is a failure. If `equations` is listed, the notebook must use `TangleLatex`.

**Figure walkthroughs — do not skip these steps:**

1. Copy [`resources/figure_annotator_widget.py`](resources/figure_annotator_widget.py) next to the notebook.
2. Add `anywidget` and `traitlets` to the PEP 723 dependencies.
3. Extract each main-text figure image into the notebook's directory (for example `figures/fig1.webp`).
4. For each figure, build tour steps with coordinates via [`scripts/figure_annotation_helper.py`](scripts/figure_annotation_helper.py). Read [`resources/dynamic_figure_annotation.md`](resources/dynamic_figure_annotation.md).
5. Show the paper's caption and figure number on every tour.
6. Put every tour in one `mo.ui.tabs` inside `wigglystuff.FloatingPanel`.

### Tools

Five widgets. For the four that live in this repo, copy the file next to the notebook, add its packages to the PEP 723 block, and import it. `TangleLatex` comes from `wigglystuff` — add the package, nothing to copy. Details live in the resource linked on each tool. Stick to the paper when you fill them.

#### Assessment widget (`PaperQuiz`)

**For:** the end-of-notebook quiz: five questions at each reader level, shown for the reader's level.

**Files:** [`assets/paper_quiz.py`](assets/paper_quiz.py). Copy `paper_quiz.py` next to the notebook. Add `anywidget` and `traitlets`.

```python
from paper_quiz import PaperQuiz

quiz = mo.ui.anywidget(PaperQuiz(questions=[...], seed=0))
quiz
```

**Parameters:** `questions` — five dicts with `question`, `answer`, `explain`, and exactly three `distractors`. `seed` — reproducible option order. `quiz.value["selected"]` / `["score"]` after the reader answers.

**Read:** [`resources/final-quiz.md`](resources/final-quiz.md). Questions are only about this paper.

#### Figure annotator (`FigureAnnotatorWidget`)

**For:** a step-through of each main-text figure the paper printed, in one `mo.ui.tabs` inside `wigglystuff.FloatingPanel`.

**File:** [`resources/figure_annotator_widget.py`](resources/figure_annotator_widget.py). Copy it next to the notebook. Add `anywidget`, `traitlets`, and `wigglystuff>=0.6.0`.

```python
from figure_annotator_widget import FigureAnnotatorWidget

annotator = FigureAnnotatorWidget()
annotator.load_image_from_path(Path("figures/fig1.webp"))
annotator.caption = "Fig. 1. …"  # paper's caption
annotator.annotations = [{"id": "…", "label": "…", "box": [l, t, w, h], "color": "#0d9488"}]
annotator.tour_steps = [{"title": "…", "target_ids": ["…"], "html": "…"}]
```

**Parameters:** `load_image_from_path(path)`, `caption`, `annotations` (`id`, `label`, `box` as `[left%, top%, width%, height%]`, `color`, `description`), `tour_steps` (`title`, `target_ids`, `html` with `.fig-ref` badges). Display every tour as values of one `mo.ui.tabs`, wrap that tab box in `wigglystuff.FloatingPanel`.

**Read:** [`resources/dynamic_figure_annotation.md`](resources/dynamic_figure_annotation.md). Build boxes with [`scripts/figure_annotation_helper.py`](scripts/figure_annotation_helper.py).

#### Materials-and-methods flowchart (`MermaidView`)

**For:** a pannable, zoomable ELK Mermaid drawing of **this paper's** pipeline (top-down by default; drag, Ctrl/pinch zoom, +/− and Fit buttons), stepped with the reader's level.

**File:** [`assets/mermaid_view.py`](assets/mermaid_view.py). Copy it next to the notebook. Add `anywidget` and `traitlets`.

```python
from mermaid_view import MermaidView

MermaidView(
    source="flowchart TD\n  a --> b",
    steps=[{"node": "a", "title": "Start", "ref": "Section 2"}],
)
```

**Parameters:** `source` (Mermaid, no `<br>`), `steps` (each `node`, `title`, optional `ref`, `what`, `params`, `incoming`), `step`, `theme` (default `forest`), `look` (default `handDrawn`), `height`. Not `mo.mermaid`.

**Read:** [`resources/method_diagrams.md`](resources/method_diagrams.md).

#### Explain at five levels (`ExplainLevels`)

**For:** the paper's main point at five reader levels. Generated notebooks show the one-line summary and only the reader's level (`tabs=False`), driven by the notebook's level picker; no per-level checks.

**File:** [`assets/explain_levels.py`](assets/explain_levels.py). Copy it next to the notebook. Add `anywidget` and `traitlets`.

```python
from explain_levels import ExplainLevels

explainer = mo.ui.anywidget(ExplainLevels(
    title="…",
    paper_ref="Abstract, Secs. 1–3",
    summary="…",  # the one-line summary
    tabs=False,
    level=reader_level.value,
    levels=[{"name": "Child", "text": "…"}, …],
))
explainer
```

**Parameters:** `title`, `paper_ref` (section, figure, equation, or algorithm of **this paper**), `summary` (the one-line summary), `tabs` (default `True`; generated notebooks pass `False`), `level` (0-based index or name; the synced value is the canonical name), `levels` (each `name`, markdown `text`, optional `check`, which generated notebooks leave out since the final quiz is matched to the level). `explainer.value["level"]` after the reader changes rungs. One notebook-level picker can drive several ladders via `level=reader_level.value`. Write each subscripted or decorated symbol as a single math span (`$\rho_A$`, not `$\rho$ A` or a Unicode ρ followed by math A).

**Read:** [`resources/explanation-levels.md`](resources/explanation-levels.md) (how to write the five levels) and [`resources/explain_levels.md`](resources/explain_levels.md) (trait schema and snippets).

#### Interactive equations (`TangleLatex`)

**For:** a paper equation whose behaviour the reader benefits from exploring — scaling laws, rate equations, loss functions, model parameters. One widget per key equation, tied to the paper's equation or section number.

**When not:** purely definitional notation (symbols introduced, not used), or a huge derivation the reader only needs to see written down. Those stay as LaTeX in `mo.md`.

**Package:** `wigglystuff`. Add `wigglystuff>=0.6.0` to the PEP 723 block. Import `TangleLatex` from the package; there is no file to copy.

```python
from wigglystuff import TangleLatex

eq = mo.ui.anywidget(
    TangleLatex(
        latex=r"v = \frac{\tangle{Vmax}[S]}{\tangle{Km} + [S]}",
        parameters={
            "Vmax": {"value": 100, "min_value": 20, "max_value": 200, "step": 1},
            "Km": {"value": 50, "min_value": 5, "max_value": 150, "step": 1},
        },
    )
)
eq
```

**Parameters:** `latex` — KaTeX containing at least one `\tangle{name}` marker. `parameters` — a dict per marker; `value` is required. Optional keys: `min_value`, `max_value`, `step`, `digits`, `display` (`"number"` or `"symbol"`), `symbol`, `label`, `pixels_per_step`, `color` (a CSS string or `{"light": ..., "dark": ...}`). Prefer native Greek/Unicode in `label` (μ, σ, Φ) over ASCII spellings (mu, sigma, Phi). KaTeX `symbol` still uses TeX (`\\mu`). `notes` — optional; wrap a part in `\note{name}{tex}` and map `name` to text, or to a dict with `text`, `side` (`"auto"`, `"top"`, `"bottom"`), and `color`. Keyword-only: `display_mode` (default `True`), `editor` (`"popover"` or `"inline"`), `reveal_all_on_drag`, `theme` (`"auto"`, `"light"`, `"dark"`). In a **different** cell, read `eq.values` (live while dragging) and `eq.committed_values` (the numbers from before the drag). Do not invent constructor arguments.

**How:** one `TangleLatex` per key equation. Cite the paper's equation or section number next to it. Set `min_value` / `max_value` from values the paper reports, not round numbers you guessed. Follow with a short markdown cell that says what to try (which variable to drag, what to watch). Equations come from the paper. Same Greek rule as method diagrams: native Unicode in labels and notes, not ASCII spellings.

**Read:** [`resources/tangle_latex_example.py`](resources/tangle_latex_example.py).

### 4. Generate the marimo notebook

Start from an `assets/` template when one exists (**TODO:** add `assets/notebook_template.py`). Write a marimo notebook that can be opened with `uvx marimo edit --sandbox`.

Follow the skills installed in `.agents/skills/` (one `import marimo as mo` cell; unique top-level names; widgets that drive exploration, not decoration):

- [`marimo-notebook-patterns`](.agents/skills/marimo-notebook-patterns/SKILL.md): read before writing or editing any notebook cell (import and cell-parameter rules, unique variables, widget API signatures, common errors). For charts, follow its `plotly-over-matplotlib` rule: Plotly is the default.
- [`marimo`](.agents/skills/marimo/SKILL.md): broader authoring reference, including live pairing and embedding notebooks on the web.
- [`awesome-marimo-notebook`](.agents/skills/awesome-marimo-notebook/SKILL.md): how to make a paper or dataset explainer engaging and polished.
- [`processing-friendly-prose`](.agents/skills/processing-friendly-prose/SKILL.md): sentence shape for every reader-facing string. Read it in full before writing prose; see [Writing quality](#writing-quality).

Declare dependencies in a [PEP 723](https://peps.python.org/pep-0723/) inline script metadata block at the top of the file (`# /// script` … `# ///`), listing `marimo`, `plotly`, and every other package the notebook imports, each with a lower-bound version (e.g. `numpy>=2.0`, `plotly>=5.24.0`). This lets `uv run` and `marimo edit --sandbox` install them.

If the final quiz is included, end the notebook with the five-question quiz described under [Final quiz](#final-quiz).

#### Writing quality

Every reader-facing sentence follows
[`processing-friendly-prose`](.agents/skills/processing-friendly-prose/SKILL.md).
That is not only `mo.md` cells. It is also widget copy: ExplainLevels
level `text` and checks, TangleLatex `notes` / `label` strings and the
markdown "what to try" cell that follows each equation, figure-tour
`html` and labels, quiz questions and feedback, MermaidView step `what`
/ `params` / `incoming`, flowchart labels, and figure annotations.

Read that skill and
[`references/sources.md`](.agents/skills/processing-friendly-prose/references/sources.md)
in full before writing. Do not work from memory.

When you delegate writing or review to a subagent or helper, put this
requirement in that helper's instructions, and give it the path
`.agents/skills/processing-friendly-prose/SKILL.md`. If the helper cannot
see the repo, give it
https://github.com/ericmjl/skills/tree/main/skills/processing-friendly-prose
instead. Review the helper's prose against that skill before you merge it
into the notebook.

Hard requirements:

- Intelligible and representative of the paper's core ideas.
- Not generic. If a sentence could have been written about any paper, rewrite it.
- Define symbols and field terms when they first matter, or point to a glossary / tooltip / highlight-to-explain aid. Follow [`resources/field-maturity.md`](resources/field-maturity.md) for maturity-specific onboarding sections. **TODO:** which of those reader aids to ship first. “Marimo Lens” was mentioned as a possible fit for highlight-to-explain; confirm the actual feature name and host support.
- Follow the processing-friendly-prose checklist on every sentence you write or accept: do not pack a sentence by dropping a useful word; unpack noun stacks of three or more; keep optional "that" or "which"; keep each subject next to its verb; do not give inanimate subjects verbs of eating, biting, swallowing, thinking, or wanting; do not invent denominal verbs; prefer ordinary wording over rare coinages. Tutorials, widget copy, and handoff notes need extra care.

A `[prose]` warning from the validator is a pointer, not an order to rewrite. Look at that sentence again. Change it only when the new wording is easier to read. Keep wording that is already clear and natural, including ordinary scientific terms, even if the checker still flags it. Do not rewrite a clear sentence just to make the warning list shorter. Leftover warnings are fine. In the handoff, list any you kept on purpose and say why in a short clause.

Other generation rules:

- Hide code on nearly every cell: `@app.cell(hide_code=True)`, and the same flag on `@app.function` and `app.setup`. Readers see prose, figures, widgets, and outputs. Showing the code is the exception, and only for a cell whose code is itself the teaching point (a short snippet the reader is meant to read, if the notebook has one). When you leave a cell visible, say so in that cell's prose. Cell templates in `resources/` set `hide_code=True`.
- Equations: LaTeX in `mo.md` for definitional notation. When the equations component is included, put each key equation whose behaviour is worth exploring in a `TangleLatex` widget (see [Tools](#tools)): one widget per equation, cited by the paper's equation or section number, with ranges from the paper's reported values, and a short markdown cell saying what to try. Do not invent equations.
- **Figures first:** the paper's own main-text figures (images extracted from the paper) appear in the notebook regardless of which components were chosen. If figure walkthroughs are skipped, still show each figure with its caption and number. Missing figure images are reported; never silently replace them with unrelated plots. A reproduced or simplified plot is extra, and only when the paper's data allow — it does not stand in for the printed figure. Default plotting library is **Plotly** (`plotly.graph_objects` / `plotly.express`). Put `plotly` in the PEP 723 block. Use Plotly annotations, shapes, and hover text for callouts on recreated figures. Do not start from matplotlib or Altair unless the user asks. **TODO:** how far to go with vision-based estimates or reader-written figure interpretations in v1.
- Figure walkthroughs (when included): every main-text figure gets an annotated tour (`FigureAnnotatorWidget`), not a subset. Enumerate the figures first and report any figure whose image you could not obtain instead of skipping it. Put every tour in one `mo.ui.tabs`, one tab per figure, and wrap that tab box in `wigglystuff.FloatingPanel` (`wigglystuff>=0.6.0`) so the reader can drag it while scrolling. Recreated plots stay in Plotly; the widget tours the paper's printed figure. Read [`resources/dynamic_figure_annotation.md`](resources/dynamic_figure_annotation.md) (`FigureAnnotatorWidget` plus a coordinate-audit helper in `scripts/`).
- Method diagrams (when included): draw the paper's pipeline as a hand-drawn ELK Mermaid flowchart whose detail follows the reader's level, and step through it. Default layout is top-down (`flowchart TD`). Prefer native Greek/Unicode symbols in diagram labels over ASCII spellings. The rendered view is pannable and zoomable (drag, Ctrl/pinch zoom, +/− and Fit buttons). Read [`resources/method_diagrams.md`](resources/method_diagrams.md) (`MermaidView` in `assets/`).
- Explain at five levels (when included): the paper's main point gets one explanation ladder via `ExplainLevels`, showing only the reader's level (`tabs=False`) under its one-line summary (`summary=`); other concepts get one explanation at the reader's level ([Explaining at multiple levels](#explaining-at-multiple-levels); [Tools](#tools)). Pass `paper_ref` and `level=reader_level.value`; no per-level checks, since the final quiz is matched to the level.
- Interactive equations (when included): one `TangleLatex` per key equation, cited by equation or section number, ranges from the paper, and a short markdown cell saying what to try ([Tools](#tools)). Prefer native Greek/Unicode in `label` and notes over ASCII spellings.
- Domain mode from step 2: coding exercises and method reconstruction for algorithm-like papers; agent-written visualization/widget explainers for concept-like papers (for example, a mechanism in a cell).
- Label anything that goes beyond the paper (“Our demo,” “Simplified assumption”).
- Include paper metadata and citations.

### 5. Validate and hand off

**Minimum (v1 skeleton): the notebook must run.**

```bash
uv run scripts/validate_notebook.py path/to/notebook.py --run
```

It checks Python syntax, runs `marimo check --strict`, and with `--run` executes the notebook top to bottom. Fix every reported problem before delivery. It also warns, without failing, when a cell, `@app.function`, or `app.setup` block does not set `hide_code=True`. A warning names a cell you left visible because its code is the teaching point; any other visible cell should be hidden. When a notebook builds two or more figure tours, it warns, again without failing, if those tours are not all values of a single `mo.ui.tabs`. If the notebook has a `# paper-to-notebook-skill-components:` comment, the script also warns when an included component is missing (`FigureAnnotatorWidget`, `MermaidView`, `PaperQuiz`, `ExplainLevels`, `TangleLatex`); skipped components are not a failure. Missing `FigureAnnotatorWidget` is a failure unless that comment opts out of `figure-walkthroughs`. It warns, without failing, when no paper figure image is embedded or referenced, when more than half of the long markdown cells cite no paper anchor (Fig./Figure/Eq./Table/Section/§), when a Greek TeX command is split from its subscript across a math span (`$\rho$ A`), and when notebook prose trips a mechanical processing-friendly-prose check (very long sentences or paragraphs, clear noun stacks of four or more nouns or a hyphenated compound stacked onto further nouns, inanimate actors with person-verbs, ad-hoc denominal verbs from the skill's examples). Each `[prose]` line points to a sentence to look at again. It does not require a rewrite. Keep clear wording, including scientific terms of art, even if it stays flagged.

**Writing check (required before you declare the notebook done).** The validator's `[prose]` warnings are a first filter, not a pass. They mark a sentence to look at again. They do not mark a sentence you must rewrite. Then do an explicit review pass on every prose span: markdown, ExplainLevels level `text` and checks, TangleLatex "what to try" cells and `notes`, figure annotations, quiz feedback, and flowchart step descriptions. List issues first (`location + type + short description`), the same shape as processing-friendly-prose. Rewrite only when the change makes the sentence clearer. Keep wording that is already clear and natural. Report leftovers in the handoff, with a short reason for any warning you kept on purpose.

For each item, either rewrite the prose or report it as a gap:

1. **Brevity is not readability.** A cut that saves words but packs modifiers or drops a useful "that" is a miss. Prefer a slightly longer sentence the reader can predict.
2. **One idea per sentence; subjects next to verbs.** If a subject waits through a long aside before the verb, split the sentence.
3. **Noun stacks of three or more** are unpacked into a phrase with prepositions or a clause. Familiar hyphenated terms that already name one thing may stay.
4. **Optional "that" or "which"** stays when the clause is long or the next noun is not the subject the reader expects.
5. **Inanimate subjects** do not take verbs of eating, biting, swallowing, thinking, or wanting. Name the human actor, or pick a verb that fits an object.
6. **No ad-hoc denominal verbs** ("footnote it", "calendar it"). Common ones ("email me") are fine.
7. **Ordinary wording**, not rare coinages or generic filler. If a sentence could have been written about any paper, rewrite it.
8. **Terms defined before use.** Symbols and field terms are defined when they first matter, or the glossary is pointed at.
9. **Concrete referents and paper anchors.** Each section cites a paper section, figure, equation, or table. Numbers keep their conditions.
10. **Mechanical warnings.** Look at every `[prose]` line from `uv run scripts/validate_notebook.py`. Rewrite only when the change is clearer. Keep natural scientific terms even if they stay flagged. Leftover warnings are fine; list each one you kept, with a short reason.

Optional extra, not required: `uvx proselint path/to/notebook.py` after the mechanical checker. Do not install it globally. This skill does not depend on it.

Before handoff, scan the notebook against [What a good notebook looks like](#what-a-good-notebook-looks-like):

- List any cell without a paper anchor and either anchor it or cut it.
- Report the count and fraction of background cells.
- Report the writing-check findings (mechanical warning count, issues you fixed, leftovers you kept on purpose with a short reason).

Tell the user:

- Path to the notebook and the command to open it (`uvx marimo edit --sandbox …`).
- Assumed audience and what was simplified.
- TODOs and known gaps (including missing data, main-text figures whose images could not be obtained, or undefined terms).
- Which of figure walkthroughs, method diagrams, the final quiz, explain-at-five-levels, and interactive equations were included, and that the defaults (all four, plus equations when the paper has them) were used if you could not ask.
- Each main-text figure and whether its tour was built (or that the user opted out).
- The background-cell count and fraction from the scan above.
- The writing-check report: mechanical `[prose]` warning count, checklist issues you fixed, and leftovers you kept on purpose, each with a short reason.
- Paper reference (title, authors, year, link).

**Planned validation beyond “it runs”** is the [good-notebook checklist](#what-a-good-notebook-looks-like), plus:

- Writing is intelligible and representative, and it passes the [writing check](#writing-quality) against processing-friendly-prose.
- Core concepts and metadata terms actually get explained.
- No fabricated numbers or claims.
- If the final quiz is included: the notebook ends with it, and its questions are about the paper's claims, findings and limits rather than its implementation detail.
- Every ladder level carries the same five parts; every quote appears word for word in the paper (`scripts/check_quotes.py`); every simplification is true as it stands, since each level stands alone; any analogy is labelled and its limit stated.
- **Vocabulary onboarding:** for established, emergent, and interdisciplinary case studies, verify glossary coverage and—where required—disambiguation or terminology-in-flux sections per [`resources/field-maturity.md`](resources/field-maturity.md) §8.
- **TODO:** assertion- or gold-question evals; multi-model runs (open-weight and frontier models from several providers were offered); LLM-as-judge only as a first filter that is more trustworthy on “this is bad” than on “this is good”; a human try-on-an-unfamiliar-paper pass; domain-expert review after an own-field smoke test.
- **TODO:** a shared test-paper set that covers established, emergent, and interdisciplinary work, and subdomains, not just one field. A 2016 influenza paper was offered as one possible case; the list is not chosen.

## Explaining at multiple levels

The paper's main point gets an **explanation ladder**: the paper explained at five levels, each written for a reader with specific prerequisites. It is modeled on WIRED's [5 Levels](https://www.wired.com/video/series/5-levels/) series. The level names are **shorthand**. What defines a level is the subject knowledge and math the reader brings, and how deep the level goes.

| Level (shorthand) | Subject knowledge assumed | Math assumed | Depth |
|---|---|---|---|
| 1 · Child | Everyday experience | Counting and comparison | Cause and effect, in everyday words |
| 2 · Teen | General science literacy | Arithmetic, percentages, simple charts | The paper's headline numbers, with one or two terms defined |
| 3 · Undergrad | An introductory course in the field | The field's introductory tools | The exact method, every symbol defined |
| 4 · Grad student | An adjacent area's standard methods | Follows the paper's derivations | An abstract for a neighbouring field: results with their anchors, plus why it is built this way |
| 5 · Expert | This subfield's literature | Full formalism | An abstract for this subfield: what's new against prior work, results at full precision, the main limit, and open questions |

Rules:

1. **Profile prerequisites per paper** (Phase 1): for each level, what the reader knows, what they don't, and what the notebook must teach. Map the user's stated background (from the optional inputs under Contract) onto a level.
2. **Every level carries the main point.** Write a *spine* first: the question, what the authors did, what they found, why it matters, and its limits, each with a quote and a location. From it, write a **one-line summary** of what the paper found and why it matters, shown above the ladder. Every level covers all five, deeper as the levels rise. The paper's kind (methods, empirical, theory, review, dataset, or position) sets what each part means and which gets the most space.
3. **Only the paper** for the ladder and the quiz; a glossary may use outside sources if labelled. Work from the full text, never the abstract alone or memory. If you can't read the whole paper, ask the learner for the PDF instead of summarizing it. No outside facts, no invented numbers or toy examples, and only the paper's own definitions. Significance is what the paper claims, cited, with the paper's own qualifiers.
4. **Each level stands alone and is accurate.** Readers see only their own level, so each one is complete without the others. Simplify by leaving things out, never by saying something false; a ledger records why each simplification is still true.
5. **Direct voice, no unexplained acronyms:** state the content and cite it, without "the authors…" or "the paper…"; below Expert, spell out and explain every acronym and named method, and use none at the Child level.
6. **Analogies only when they help:** labelled as ours, adding no facts, mapped onto the paper, with their limit stated.
7. **Numbers carry their conditions:** the table, cohort, feature set, or range goes in the same sentence. In testing on real papers, both misconceptions the ladders caused came from a number stripped of its condition.
8. **Check before shipping:** match every claim to a quote, and run `uv run scripts/check_quotes.py paper.txt ladder.md` so every quote appears word for word, and `uv run scripts/check_levels.py ladder.md` for the length caps and voice. Keep a term ledger (no term used undefined below its level), and check the trends up the ladder.

**In the notebook:** add one level picker near the top; it drives every section. The ladder is one `ExplainLevels` widget with `level=reader_level.value`, `tabs=False`, `summary=` the one-line summary, and `paper_ref`; it shows only the reader's level, with no per-level check.

**Read before writing:** [`resources/explanation-levels.md`](resources/explanation-levels.md) has the spine and profile templates, grounding rules, a pointer to the worked example (UMAP), tested marimo cells, and pitfalls. [`resources/explain_levels.md`](resources/explain_levels.md) is the widget contract. [`resources/examples/`](resources/examples/) has a complete ladder and level-matched quiz written with this skill (UMAP).

## Final quiz

When the final quiz is included, the notebook ends with **five multiple-choice questions about the paper itself**, written for the reader's explanation level, rendered by the `PaperQuiz` anywidget in [`assets/paper_quiz.py`](assets/paper_quiz.py). It shuffles the options, marks the answer right or wrong, shows an explanation for whichever option the reader picked, and keeps a score. Skip this section when the user left the final quiz out.

Quiz the substance, not the machinery: the paper's claims, what it found, why those findings follow, and what it says it cannot conclude. Ask about a method only when the reader needs it to read a result correctly. These are informal checks like the rest, not formal assessment.

**Read before writing:** [`resources/final-quiz.md`](resources/final-quiz.md) has what to ask, how to match the questions to each level, how to build distractors that target real misconceptions, and the cells to add.

## What a good notebook looks like

Check this before handoff. If a box fails, fix it or report it as a gap.

1. **Faithful to the paper.** Every claim, number, and conclusion is supported by the paper. Every section is anchored to a paper section, figure, equation, or table.
2. **Stays on the paper.** Background is the minimum a reader at the chosen level needs for a specific passage, labeled as background. No tangents. No other papers' content except a one-line pointer when this paper depends on it.
3. **Figures are present.** Every main-text figure appears with its number and caption, and is toured with `FigureAnnotatorWidget` unless the user opted out.
4. **Chosen components are present.** Figure walkthroughs, the `MermaidView` methods flowchart, the final quiz, `ExplainLevels`, and — when the paper has equations — `TangleLatex` — whichever the user kept, and the defaults if you could not ask.
5. **Explanations fit the reader.** Match the level the user gave. Define terms when they first matter.
6. **Nothing invented.** No fabricated data or plots. Gaps are reported.
7. **Runs cleanly.** The validator passes, code is hidden, and the notebook executes top to bottom.
8. **The handoff report is complete.** It lists figures and their tour status, components, gaps, and the writing-check report.
9. **Interactive equations when the paper has math.** Key equations whose behaviour is worth exploring use `TangleLatex`, each tied to the paper's equation or section number.
10. **Prose is processing-friendly.** Every reader-facing sentence — markdown, ExplainLevels level text, TangleLatex "what to try" cells and notes, widget text, annotations, quiz feedback, flowchart steps — follows [`processing-friendly-prose`](.agents/skills/processing-friendly-prose/SKILL.md). The writing check was run and reported. Leftover `[prose]` warnings are fine when the wording is already clear; list those in the handoff with a short reason.

---

## Folder reference

- **`.agents/skills/`** — skills installed from [ericmjl/skills](https://github.com/ericmjl/skills) (`marimo`, `marimo-notebook-patterns`, `awesome-marimo-notebook`, `processing-friendly-prose`), pinned in `skills-lock.json`; refresh with `npx skills update`.
- **`assets/`** — templates and snippets to copy or fill in. Includes [`paper_quiz.py`](assets/paper_quiz.py) (`PaperQuiz`), [`mermaid_view.py`](assets/mermaid_view.py) (`MermaidView`), and [`explain_levels.py`](assets/explain_levels.py) (`ExplainLevels`). See [Tools](#tools).
- **`resources/`** — material the agent should read (pedagogy, format-specific ingest notes, writing and eval guidance). Do not paste these wholesale into notebooks. Includes [`explanation-levels.md`](resources/explanation-levels.md) (the explanation ladder: the paper's main point at five prerequisite-defined levels, paper-only grounding, and a worked example), [`field-maturity.md`](resources/field-maturity.md) (field-maturity rubric, vocabulary onboarding, and literature-sampling procedure), [`field-maturity-research-notes.md`](resources/field-maturity-research-notes.md) (auditable sampling for three case-study fields), [`dynamic_figure_annotation.md`](resources/dynamic_figure_annotation.md) (annotated walkthrough of every main-text figure, in one tab box inside a floating panel, when figure walkthroughs are included), [`method_diagrams.md`](resources/method_diagrams.md) (level-aware method diagrams), [`final-quiz.md`](resources/final-quiz.md) (what to ask in the end-of-notebook quiz), [`tangle_latex_example.py`](resources/tangle_latex_example.py) (`TangleLatex` on a real rate equation), and [`examples/`](resources/examples/) (a ladder and level-matched quiz for UMAP; field-maturity notebook mocks).
- **`scripts/`** — helpers, run with `uv run`. `validate_notebook.py` checks syntax, runs `marimo check --strict`, warns when code is left visible or when two or more figure tours are not in one `mo.ui.tabs`, and smoke-runs the notebook with `--run`. If the notebook declares `# paper-to-notebook-skill-components: …`, it warns when an included component is missing (`FigureAnnotatorWidget`, `MermaidView`, `PaperQuiz`, `ExplainLevels`, `TangleLatex`) and does not require skipped ones. Missing `FigureAnnotatorWidget` without an opt-out is a failure. It also warns, without failing, on mechanical processing-friendly-prose issues via `check_prose.py`. A `[prose]` warning is a sentence to look at again, not a sentence that must be rewritten. Future: per-input-format ingest, metadata fetch, figure extraction.

## Open decisions

- Default audience and the default direction of adaptive explanation.
- Which components ship in the first version (progressive explanation, visualizations, glossary/highlight-to-explain, informal checks, experimental critique, results analysis, figure reproduction, extra-source grounding).
- One mega-skill with internal components (the shape described in design discussion) vs. splitting later (ingest, pedagogy, build, eval).
- How to classify domain type and paper “mode” (algorithm vs. concept). Field maturity (established vs. emergent vs. interdisciplinary) is sketched in [`resources/field-maturity.md`](resources/field-maturity.md); algorithm vs. concept remains TODO.
- Ingest details per input format; figure handling when data are missing.
- Eval suite and test-paper list. The handoff bar is [What a good notebook looks like](#what-a-good-notebook-looks-like); remaining eval work is automating that checklist.
- License for the skill and for generated notebooks.
- Whether to mandate `wigglystuff.CellTour` for every notebook.
- i18n and accessibility requirements.

## Related work at hackathon

Pairs with **Visual LaTeX** for equation-heavy papers. In-notebook, key equations use `TangleLatex` from `wigglystuff`. Collaborators are listed in the repo `README.md`.
