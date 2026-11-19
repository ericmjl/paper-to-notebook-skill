---
name: paper-to-notebook
description: >
  Turn a published research paper into a guided marimo learning notebook:
  plain-language explanations, interactive widgets for key equations and figures,
  and comprehension checks. Use when asked to make a paper explainer notebook,
  teach a paper interactively, or build a marimo walkthrough of a publication.
metadata:
  author: ericmjl
  version: "0.1.0"
---

# Paper to notebook

Guide an agent from **source paper** to **runnable marimo notebook** that teaches the paper step by step—not a summary page, but an interactive lesson.

This skill lives in a small repo layout:

- **`SKILL.md`** (this file) — workflow and rules.
- **`assets/`** — templates and static files to copy or fill in.
- **`resources/`** — reference docs to read before writing (marimo patterns, pedagogy).
- **`scripts/`** — validation and other helpers (`uv run …`).

For deep marimo craft, also load Eric's skills when available: `marimo`, `marimo-notebook-patterns`, `awesome-marimo-notebook` ([github.com/ericmjl/skills](https://github.com/ericmjl/skills)).

---

## When to use

- User names a paper (PDF, URL, arXiv, DOI) and wants a **learning notebook**.
- User wants **widgets** around specific equations or figures from a paper.
- User wants **checks for understanding** (questions, mini-exercises) while reading.

Do **not** use for: literature review only, slide decks, or non-marimo outputs (unless the user explicitly changes format).

---

## Inputs to gather

| Input | Notes |
|-------|--------|
| Paper source | File path, URL, or identifier. **TODO:** standardize fetch/parse steps. |
| Audience | **TODO:** default if unspecified (suggest "graduate-level STEM reader"). |
| Depth | Full walkthrough vs. highlights (methods only, one figure, etc.). |
| Output path | Where to write `*.py` marimo notebook. |
| Constraints | GPU, runtime limits, offline, etc. |

---

## Workflow overview

```
1. Ingest paper
2. Select learning objectives + key artifacts (concepts, equations, figures)
3. Plan narrative path (hook → intuition → formalism → checks)
4. Draft notebook structure from assets/templates
5. Implement cells: prose, math, widgets, checks
6. Validate (scripts + manual read-through)
7. Hand off: how to run, known gaps, citations
```

---

## Phase 1 — Read and understand the paper

1. Obtain full text (not abstract-only).
2. Extract:
   - **Problem** and **contribution** (one paragraph each, in your own words).
   - **Prerequisites** the reader needs.
   - **Key concepts** (3–8 terms with short definitions).
   - **Key equations** (numbered as in paper; note variables).
   - **Key figures** (what each encodes; what to interact with).
3. Flag **TODO** items where the paper is ambiguous or you lack domain context; do not invent experimental results.

**Resources:** add domain cheat-sheets to `resources/` as you find them; read any pedagogy notes there before planning.

---

## Phase 2 — Plan the learning path

Design a linear path a human can follow in one sitting (**TODO:** target duration, e.g. 30–60 minutes).

Suggested spine (adjust per paper):

1. **Why this paper matters** — motivating question.
2. **Intuition** — metaphor or toy example **before** heavy notation.
3. **Setup** — notation table, assumptions.
4. **Core idea** — one central mechanism, linked to an equation or figure.
5. **Step-through** — 2–4 segments aligned with paper sections.
6. **Checks** — short questions after each segment.
7. **Wrap-up** — limitations, what to read next, citation.

For each segment, specify:

- Learning objective (one sentence).
- Marimo cell types: `mo.md`, code, `mo.ui.*` / anywidget, plot.
- Comprehension check (question type: recall, apply, interpret figure).

Write the plan in the agent transcript or a scratch file; **TODO:** optional `resources/learning-path-template.md`.

---

## Phase 3 — Generate the marimo notebook

1. Start from **`assets/`** notebook template when present (**TODO:** add `assets/notebook_template.py`).
2. Follow marimo conventions (see `resources/` and `marimo-notebook-patterns`):
   - Import `marimo as mo` in **one** cell only; use `mo` elsewhere.
   - Unique top-level names across cells; no private `_names` needed downstream.
   - Prefer reactive widgets that **drive** exploration, not decoration.
   - Declare dependencies in a [PEP 723](https://peps.python.org/pep-0723/) inline script metadata block at the top of the file (`# /// script` … `# ///`), listing `marimo` and every package the notebook imports, each with a lower-bound version (e.g. `numpy>=2.0`). This lets `uv run` and `marimo edit --sandbox` install them.
3. **Explanations:** short paragraphs; define symbols when introduced.
4. **Equations:** LaTeX in `mo.md`; consider sliders tied to parameters in key formulas.
5. **Figures:** reproduce or simplify; link back to paper figure number; interactive where it aids understanding.
6. **Comprehension checks:** **TODO:** pick patterns (dropdown quiz, `mo.ui.text` + reveal, numeric input with tolerance).

Label any extension beyond the paper ("Our demo", "Simplified assumption") explicitly.

---

## Phase 4 — Validate

1. Run the validator:

   ```bash
   uv run scripts/validate_notebook.py path/to/notebook.py --run
   ```

   It checks Python syntax, runs `marimo check --strict`, and with `--run` executes the notebook top to bottom. Fix every reported problem before delivery.

2. Mental checklist:
   - [ ] Notebook runs top-to-bottom without errors.
   - [ ] Citations and paper metadata present.
   - [ ] Checks have documented expected answers or reveal cells.
   - [ ] No fabricated numbers or claims.

3. If validation fails, fix and re-run before delivery.

---

## Phase 5 — Deliver

Tell the user:

- Path to the notebook and command to open it (`uvx marimo edit --sandbox …`).
- Assumed audience and what was simplified.
- **TODOs** left in the notebook or skill.
- Paper reference (title, authors, year, link).

---

## Folder reference

### `assets/`

Templates: starter marimo app, banner markdown, check-for-understanding snippets, shared CSS/SVG if needed.

### `resources/`

Material the agent should **read**, not paste wholesale into notebooks:

- Marimo widget notes and gotchas.
- Pedagogy guidelines (scaffolding, cognitive load).
- Links to sibling hackathon ideas (e.g. Visual LaTeX).

### `scripts/`

Automation with documented `uv` usage:

- `validate_notebook.py` — confirm generated notebook is healthy (syntax, `marimo check --strict`, smoke run with `--run`).
- Future: fetch paper metadata, extract figures, etc.

---

## Open decisions (TODO)

- PDF vs. LaTeX vs. HTML ingestion pipeline.
- Whether to mandate `wigglystuff.CellTour` for every notebook.
- Standard library set for math plots (plotly vs. matplotlib).
- i18n / accessibility requirements.

---

## Related work at hackathon

Pairs with **Visual LaTeX** for equation-heavy papers. Collaborators listed in repo `README.md`.