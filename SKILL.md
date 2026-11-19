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
- Prerequisites a reader likely needs.
- Key concepts and **terms the paper uses but does not define** (core metadata or field terms). Example raised in design discussion: a paper about heart attacks that never explains “myocardial infarction.”
- Key equations, numbered as in the paper, with variables.
- Key figures: what each encodes, how it is labeled, and whether underlying data appear to be available.
- Risk points for generation: heavy LaTeX or math, Greek-letter figure labels, other non-ASCII text.
- Obvious gaps in methods or reporting. Do not invent missing experimental results.

**TODO:** whether to classify the paper as established, emergent, or interdisciplinary, and whether that should change linguistic strategy in v1, or only guide testing.

**TODO:** whether to classify the paper as algorithm-like (coding exercises, reverse-engineer the method) vs. concept-like (agent-written explainer widgets). Chemistry examples used in discussion: mass balance, reaction kinetics, a new kinetic model.

### 3. Plan the learning path

Design a path a human can follow in one sitting. **TODO:** target duration.

Do not lock the whole notebook to a single reading level. Plan for **adaptive explanation**: the reader should be able to get a simpler or more advanced account of a hard passage. **TODO:** default direction — start simple and add complexity, or start high and step down when the reader is confused. Both were proposed; neither was chosen.

Suggested spine (adjust per paper):

1. Why this paper matters.
2. Intuition or a toy example before heavy notation.
3. Setup: notation, assumptions, terms.
4. Core idea, tied to an equation or figure.
5. Step-through aligned with the paper.
6. Informal checks after segments (not formal assessment — formal assessment is out of scope).
7. For graduate-and-above readers, critique beats: does the experimental design address the stated question; is the statistical framework an appropriate choice; what is missing; what assumptions is the reader making.
8. Wrap-up: limitations, what to read next, citation.

**TODO:** how far critique, results-section analysis, and figure-interpretation prompts go in the first version, versus a plain guided walkthrough.

If the user supplied extra sources, plan where those will be cited in the notebook and how sourced evidence will be distinguished from general knowledge. **TODO:** the mechanism for that distinction, and whether a small concept map or “knowledge wiki” belongs here later.

### 4. Generate the marimo notebook

Start from an `assets/` template when one exists (**TODO:** add `assets/notebook_template.py`). Write a marimo notebook that can be opened with `uvx marimo edit --sandbox`.

Follow marimo conventions in `resources/` when they are present (one `import marimo as mo` cell; unique top-level names; widgets that drive exploration, not decoration).

Declare dependencies in a [PEP 723](https://peps.python.org/pep-0723/) inline script metadata block at the top of the file (`# /// script` … `# ///`), listing `marimo` and every package the notebook imports, each with a lower-bound version (e.g. `numpy>=2.0`). This lets `uv run` and `marimo edit --sandbox` install them.

Hard requirements for the prose:

- Intelligible and representative of the paper's core ideas.
- Not generic “AI slop.” If a sentence could have been written about any paper, rewrite it.
- Define symbols and field terms when they first matter, or point to a glossary / tooltip / highlight-to-explain aid. **TODO:** which of those reader aids to ship first. “Marimo Lens” was mentioned as a possible fit for highlight-to-explain; confirm the actual feature name and host support.

Other generation rules:

- Equations: LaTeX in `mo.md`; widgets on parameters when that builds intuition.
- Figures: reproduce or simplify when data allow; link back to the paper's figure number. If data are not available, say so — do not invent plots. **TODO:** how far to go with vision-based estimates or reader-written figure interpretations in v1.
- Informal checks: short questions, not graded assessment. **TODO:** patterns (dropdown, text plus reveal, numeric tolerance).
- Domain mode from step 2: coding exercises and method reconstruction for algorithm-like papers; agent-written visualization/widget explainers for concept-like papers (for example, a mechanism in a cell).
- Label anything that goes beyond the paper (“Our demo,” “Simplified assumption”).
- Include paper metadata and citations.

### 5. Validate and hand off

**Minimum (v1 skeleton): the notebook must run.**

```bash
uv run scripts/validate_notebook.py path/to/notebook.py --run
```

It checks Python syntax, runs `marimo check --strict`, and with `--run` executes the notebook top to bottom. Fix every reported problem before delivery.

Tell the user:

- Path to the notebook and the command to open it (`uvx marimo edit --sandbox …`).
- Assumed audience and what was simplified.
- TODOs and known gaps (including missing data or undefined terms).
- Paper reference (title, authors, year, link).

**Planned validation beyond “it runs” (not all required for a first sketch):**

- Writing is intelligible and representative, not slop.
- Core concepts and metadata terms actually get explained.
- No fabricated numbers or claims.
- **TODO:** assertion- or gold-question evals; multi-model runs (Chinese open-weight and Claude models were offered); LLM-as-judge only as a first filter that is more trustworthy on “this is bad” than on “this is good”; a human try-on-an-unfamiliar-paper pass; domain-expert review after an own-field smoke test.
- **TODO:** a shared test-paper set that covers established, emergent, and interdisciplinary work, and subdomains, not just one field. A 2016 influenza paper was offered as one possible case; the list is not chosen.

## Folder reference

- **`assets/`** — templates and snippets to copy or fill in.
- **`resources/`** — material the agent should read (pedagogy, format-specific ingest notes, writing and eval guidance). Do not paste these wholesale into notebooks.
- **`scripts/`** — helpers, run with `uv run`. `validate_notebook.py` checks syntax, runs `marimo check --strict`, and smoke-runs the notebook with `--run`. Future: per-input-format ingest, metadata fetch, figure extraction.

## Open decisions

- Default audience and the default direction of adaptive explanation.
- Which components ship in the first version (progressive explanation, visualizations, glossary/highlight-to-explain, informal checks, experimental critique, results analysis, figure reproduction, extra-source grounding).
- One mega-skill with internal components (the shape described in design discussion) vs. splitting later (ingest, pedagogy, build, eval).
- How to classify domain type and paper “mode” (algorithm vs. concept; established vs. emergent vs. interdisciplinary).
- Ingest details per input format; figure handling when data are missing.
- Eval suite, criteria scaffold, and test-paper list.
- License for the skill and for generated notebooks.
- Whether to mandate `wigglystuff.CellTour` for every notebook.
- Standard library set for math plots (plotly vs. matplotlib).
- i18n and accessibility requirements.

## Related work at hackathon

Pairs with **Visual LaTeX** for equation-heavy papers. Collaborators are listed in the repo `README.md`.
