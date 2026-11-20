---
name: paper-to-notebook
description: >
  Turn a research paper — provided as a PDF, HTML, or plain-text source
  (LaTeX, Markdown, or similar) — into a guided, runnable marimo learning
  notebook. Use when asked to make a paper explainer notebook, teach a paper
  interactively, or build a marimo walkthrough of a publication. Do not use
  for multi-paper literature reviews or non-marimo outputs unless the user
  explicitly changes the format.
---

# Paper to notebook

Steer an agent from **one paper** to a **runnable marimo notebook** that helps a reader understand that paper. The notebook is a lesson, not a summary page: plain-language explanation, interactive widgets where they help, and informal checks along the way. The writing must be intelligible and representative of the paper, not generic AI prose.

This file is a skeleton. Lots of details will be filled in later. Items marked **TODO** are still undecided or only sketched.

## Contract

| | |
|---|---|
| **Input** | A paper as PDF, HTML, or plain-text source (LaTeX, Markdown, etc.). Path, URL, or identifier is fine as long as full text can be obtained. |
| **Output** | A runnable marimo notebook (`*.py`) the reader can open with `uvx marimo edit --sandbox …`. |

Optional inputs to ask for if they are missing (do not block if the user only gives the paper):

- Starting audience or “adapt as I go.” Default working assumption: undergrad through graduate student, plus working professionals new to this paper or field, with some general scientific knowledge. **TODO:** tighten the default.
- Extra context: supporting information, cited papers, or other sources the user wants treated as grounding (not just general knowledge).
- Depth: full walkthrough vs. methods, results, or one figure.
- Output path and runtime constraints.

Do **not** treat this skill as a tool for reviewing a large literature. That is a different job.

## Workflow

```
1. Ingest the paper (PDF / HTML / plain-text source)
2. Extract structure, terms, equations, figures, and gaps
3. Plan the learning path
4. Generate the marimo notebook
5. Validate it runs with `uv run`, then hand off
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
- Key figures: what each encodes, how it is labeled, and whether underlying data appear to be available.
- Risk points for generation: heavy LaTeX or math, Greek-letter figure labels, other non-ASCII text.
- Obvious gaps in methods or reporting. Do not invent missing experimental results.

Classify **field maturity** (established, emergent, interdisciplinary, or mixed) using the rubric and lightweight literature sample in [`resources/field-maturity.md`](resources/field-maturity.md). Record the class, evidence, and which vocabulary-onboarding notebook components are required (glossary, disambiguation, terminology in flux).

**TODO:** whether to classify the paper as algorithm-like (coding exercises, reverse-engineer the method) vs. concept-like (agent-written explainer widgets). Chemistry examples used in discussion: mass balance, reaction kinetics, a new kinetic model.

### 3. Plan the learning path

Design a path a human can follow in one sitting. **TODO:** target duration.

Do not lock the whole notebook to a single reading level. Plan for **adaptive explanation**: the reader should be able to get a simpler or more advanced account of a hard passage. **TODO:** default direction — start simple and add complexity, or start high and step down when the reader is confused. Both were proposed; neither was chosen. Core concepts get a full ladder (see [Explaining at multiple levels](#explaining-at-multiple-levels)).

Suggested spine (adjust per paper):

1. Why this paper matters.
2. Intuition or a toy example before heavy notation.
3. Setup: notation, assumptions, terms, and field vocabulary onboarding (glossary; disambiguation or terminology-in-flux when required—see [`resources/field-maturity.md`](resources/field-maturity.md)).
4. Core idea, tied to an equation or figure.
5. Step-through aligned with the paper.
6. Informal checks after segments, matched to the explanation level: explain, predict, apply, or critique (not formal assessment — formal assessment is out of scope).
7. For graduate-and-above readers, critique beats: does the experimental design address the stated question; is the statistical framework an appropriate choice; what is missing; what assumptions is the reader making.
8. Wrap-up: limitations, what to read next, citation.
9. Final quiz: five multiple-choice questions on the paper, always the last section (see [Final quiz](#final-quiz)).

**TODO:** how far critique, results-section analysis, and figure-interpretation prompts go in the first version, versus a plain guided walkthrough.

If the user supplied extra sources, plan where those will be cited in the notebook and how sourced evidence will be distinguished from general knowledge. **TODO:** the mechanism for that distinction, and whether a small concept map or “knowledge wiki” belongs here later.

### 4. Generate the marimo notebook

Start from an `assets/` template when one exists (**TODO:** add `assets/notebook_template.py`). Write a marimo notebook that can be opened with `uvx marimo edit --sandbox`.

Follow the marimo skills installed in `.agents/skills/` (one `import marimo as mo` cell; unique top-level names; widgets that drive exploration, not decoration):

- [`marimo-notebook-patterns`](.agents/skills/marimo-notebook-patterns/SKILL.md): read before writing or editing any notebook cell (import and cell-parameter rules, unique variables, widget API signatures, common errors).
- [`marimo`](.agents/skills/marimo/SKILL.md): broader authoring reference, including live pairing and embedding notebooks on the web.
- [`awesome-marimo-notebook`](.agents/skills/awesome-marimo-notebook/SKILL.md): how to make a paper or dataset explainer engaging and polished.

Declare dependencies in a [PEP 723](https://peps.python.org/pep-0723/) inline script metadata block at the top of the file (`# /// script` … `# ///`), listing `marimo` and every package the notebook imports, each with a lower-bound version (e.g. `numpy>=2.0`). This lets `uv run` and `marimo edit --sandbox` install them.

End the notebook with the five-question quiz described under [Final quiz](#final-quiz).

Hard requirements for the prose:

- Intelligible and representative of the paper's core ideas.
- Not generic “AI slop.” If a sentence could have been written about any paper, rewrite it.
- Define symbols and field terms when they first matter, or point to a glossary / tooltip / highlight-to-explain aid. Follow [`resources/field-maturity.md`](resources/field-maturity.md) for maturity-specific onboarding sections. **TODO:** which of those reader aids to ship first. “Marimo Lens” was mentioned as a possible fit for highlight-to-explain; confirm the actual feature name and host support.

Other generation rules:

- Hide code on nearly every cell: `@app.cell(hide_code=True)`, and the same flag on `@app.function` and `app.setup`. Readers see prose, figures, widgets, and outputs. Showing the code is the exception, and only for a cell whose code is itself the teaching point (a short snippet the reader is meant to read, if the notebook has one). When you leave a cell visible, say so in that cell's prose. Cell templates in `resources/` set `hide_code=True`.
- Equations: LaTeX in `mo.md`; widgets on parameters when that builds intuition.
- Figures: reproduce or simplify when data allow; link back to the paper's figure number. If data are not available, say so — do not invent plots. **TODO:** how far to go with vision-based estimates or reader-written figure interpretations in v1.
- Figure walkthroughs: when a key figure needs a guided, step-by-step tour, read [`resources/dynamic_figure_annotation.md`](resources/dynamic_figure_annotation.md) (`FigureAnnotatorWidget` plus a coordinate-audit helper in `scripts/`).
- Method diagrams: draw the paper's pipeline as a hand-drawn ELK Mermaid flowchart whose detail follows the reader's level, and step through it. Read [`resources/method_diagrams.md`](resources/method_diagrams.md) (`MermaidView` in `assets/`).
- Core concepts (1–3 per notebook) get an explanation ladder ([Explaining at multiple levels](#explaining-at-multiple-levels)).
- Informal checks: short questions, not graded assessment. Use the `show_check` pattern in `resources/explanation-levels.md` §9 (radio, a numeric answer with tolerance, or an open answer with a model answer).
- Domain mode from step 2: coding exercises and method reconstruction for algorithm-like papers; agent-written visualization/widget explainers for concept-like papers (for example, a mechanism in a cell).
- Label anything that goes beyond the paper (“Our demo,” “Simplified assumption”).
- Include paper metadata and citations.

### 5. Validate and hand off

**Minimum (v1 skeleton): the notebook must run.**

```bash
uv run scripts/validate_notebook.py path/to/notebook.py --run
```

It checks Python syntax, runs `marimo check --strict`, and with `--run` executes the notebook top to bottom. Fix every reported problem before delivery. It also warns, without failing, when a cell, `@app.function`, or `app.setup` block does not set `hide_code=True`. A warning names a cell you left visible because its code is the teaching point; any other visible cell should be hidden.

Tell the user:

- Path to the notebook and the command to open it (`uvx marimo edit --sandbox …`).
- Assumed audience and what was simplified.
- TODOs and known gaps (including missing data or undefined terms).
- Paper reference (title, authors, year, link).

**Planned validation beyond “it runs” (not all required for a first sketch):**

- Writing is intelligible and representative, not slop.
- Core concepts and metadata terms actually get explained.
- No fabricated numbers or claims.
- The notebook ends with the five-question quiz, and its questions are about the paper's claims, findings and limits rather than its implementation detail.
- Every ladder explains the same mechanism spine at every level; every ledger simplification is corrected at a later level; the analogy's limit is stated.
- **Vocabulary onboarding:** for established, emergent, and interdisciplinary case studies, verify glossary coverage and—where required—disambiguation or terminology-in-flux sections per [`resources/field-maturity.md`](resources/field-maturity.md) §8.
- **TODO:** assertion- or gold-question evals; multi-model runs (Chinese open-weight and Claude models were offered); LLM-as-judge only as a first filter that is more trustworthy on “this is bad” than on “this is good”; a human try-on-an-unfamiliar-paper pass; domain-expert review after an own-field smoke test.
- **TODO:** a shared test-paper set that covers established, emergent, and interdisciplinary work, and subdomains, not just one field. A 2016 influenza paper was offered as one possible case; the list is not chosen.

## Explaining at multiple levels

Core ideas get an **explanation ladder**: one mechanism explained at five levels, each written for a reader with specific prerequisites. It is modeled on WIRED's [5 Levels](https://www.wired.com/video/series/5-levels/) series. The level names are **shorthand**. What defines a level is the subject knowledge and math the reader brings, and the precision the level adds.

| Level (shorthand) | Subject knowledge assumed | Math assumed | Adds to the mechanism |
|---|---|---|---|
| 1 · Child | Everyday experience | Counting and comparison | Cause and effect, in everyday terms |
| 2 · Teen | General science literacy | Arithmetic, percentages, simple charts | A toy example with real, small numbers |
| 3 · Undergrad | An introductory course in the field | The field's introductory tools | The exact equation or algorithm, every symbol defined |
| 4 · Grad student | An adjacent area's standard methods | Follows the paper's derivations | Assumptions, when it holds, what breaks, and how it compares with the standard approach |
| 5 · Expert | This subfield's literature | Full formalism | What's new, trade-offs, limits, and open questions |

Rules:

1. **Profile prerequisites per paper** (Phase 1): for each level, what the reader knows, what they don't, and what the notebook must teach. Map the user's stated background (from the optional inputs under Contract) onto a level.
2. **One mechanism at every level.** Write a one-sentence *mechanism spine* first; each level adds precision to it. No level substitutes a vaguer or different mechanism.
3. **Accurate at every level.** Simplify by leaving things out, never by saying something false. Record each simplification in a ledger and correct it at a later level.
4. **Map the analogy and state its limit.** Carry one anchor up to Level 3, map its parts onto the method's parts, and say where it breaks by Level 3.
5. **Checks matched to the level:**
   - Child: explain.
   - Teen: predict.
   - Undergrad: apply.
   - Grad student: apply and critique assumptions.
   - Expert: critique.

   Each check has an expected answer, the reasoning, and the paper location.
6. **Ladders are for the core:** 1–3 concepts per notebook.
7. **Grounded:** cite locations from the text you read in, and never guess. Mark gaps `[cite: …]` while drafting, and resolve them before shipping.
8. **Numbers carry their conditions:** the table, cohort, feature set, or range goes in the same sentence. In testing on real papers, both misconceptions the ladders caused came from a number stripped of its condition.

**In the notebook:** add one level picker near the top. Each ladder gets `mo.ui.tabs` that open on the reader's level, with that level's check underneath.

**Read before writing:** [`resources/explanation-levels.md`](resources/explanation-levels.md) has the profile and ledger templates, a worked example, tested marimo cells, and pitfalls. [`resources/examples/`](resources/examples/) has two more complete ladders, for a method paper (UMAP) and an analysis paper (influenza reassortment).

## Final quiz

Every notebook ends with **five multiple-choice questions about the paper itself**, rendered by the `PaperQuiz` anywidget in [`assets/paper_quiz.py`](assets/paper_quiz.py). It shuffles the options, marks the answer right or wrong, shows an explanation for whichever option the reader picked, and keeps a score.

Quiz the substance, not the machinery: the paper's claims, what it found, why those findings follow, and what it says it cannot conclude. Ask about a method only when the reader needs it to read a result correctly. These are informal checks like the rest, not formal assessment.

**Read before writing:** [`resources/final-quiz.md`](resources/final-quiz.md) has what to ask, how to build distractors that target real misconceptions, and the cells to add.

---

## Folder reference

- **`.agents/skills/`** — marimo skills installed from [ericmjl/skills](https://github.com/ericmjl/skills) (`marimo`, `marimo-notebook-patterns`, `awesome-marimo-notebook`), pinned in `skills-lock.json`; refresh with `npx skills update`.
- **`assets/`** — templates and snippets to copy or fill in. Includes [`paper_quiz.py`](assets/paper_quiz.py), the widget for the required final quiz.
- **`resources/`** — material the agent should read (pedagogy, format-specific ingest notes, writing and eval guidance). Do not paste these wholesale into notebooks. Includes [`explanation-levels.md`](resources/explanation-levels.md) (prerequisite-defined explanation ladders, checks, and a worked example), [`field-maturity.md`](resources/field-maturity.md) (field-maturity rubric, vocabulary onboarding, and literature-sampling procedure), [`field-maturity-research-notes.md`](resources/field-maturity-research-notes.md) (auditable sampling for three case-study fields), [`dynamic_figure_annotation.md`](resources/dynamic_figure_annotation.md) (interactive figure walkthroughs), [`method_diagrams.md`](resources/method_diagrams.md) (level-aware method diagrams), [`final-quiz.md`](resources/final-quiz.md) (what to ask in the end-of-notebook quiz), and [`examples/`](resources/examples/) (ladders for UMAP and influenza reassortment; field-maturity notebook mocks).
- **`scripts/`** — helpers, run with `uv run`. `validate_notebook.py` checks syntax, runs `marimo check --strict`, warns when code is left visible, and smoke-runs the notebook with `--run`. Future: per-input-format ingest, metadata fetch, figure extraction.

## Open decisions

- Default audience and the default direction of adaptive explanation.
- Which components ship in the first version (progressive explanation, visualizations, glossary/highlight-to-explain, informal checks, experimental critique, results analysis, figure reproduction, extra-source grounding).
- One mega-skill with internal components (the shape described in design discussion) vs. splitting later (ingest, pedagogy, build, eval).
- How to classify domain type and paper “mode” (algorithm vs. concept). Field maturity (established vs. emergent vs. interdisciplinary) is sketched in [`resources/field-maturity.md`](resources/field-maturity.md); algorithm vs. concept remains TODO.
- Ingest details per input format; figure handling when data are missing.
- Eval suite, criteria scaffold, and test-paper list.
- License for the skill and for generated notebooks.
- Whether to mandate `wigglystuff.CellTour` for every notebook.
- Standard library set for math plots (plotly vs. matplotlib).
- i18n and accessibility requirements.

## Related work at hackathon

Pairs with **Visual LaTeX** for equation-heavy papers. Collaborators are listed in the repo `README.md`.
