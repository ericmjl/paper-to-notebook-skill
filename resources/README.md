# resources/

Reference documents the agent should **read** while planning or building a notebook—not large blobs to paste into every output.

**Contents:**

- [`explanation-levels.md`](explanation-levels.md): explaining one mechanism at five prerequisite-defined levels, with profiles, ledgers, level-matched checks, and tested marimo cells.
- [`field-maturity.md`](field-maturity.md): classifying established vs. emergent vs. interdisciplinary fields; vocabulary onboarding components; runtime literature-sampling procedure.
- [`field-maturity-research-notes.md`](field-maturity-research-notes.md): auditable API sampling for Bayesian/MCMC, LLM agents, and scRNA-seq integration.
- [`examples/`](examples/): complete example ladders for real papers (UMAP; influenza reassortment); field-maturity notebook mocks (`field-maturity-*.md`).
- [`dynamic_figure_annotation.md`](dynamic_figure_annotation.md): required annotated walkthrough for every main-text figure, gathered into one `mo.ui.tabs` (one tab per figure) inside a `wigglystuff.FloatingPanel`, with a self-verification workflow (100×100 percentage slice grid, ink/color-channel segment isolation, visual crosshair audit contact sheet, and `FigureAnnotatorWidget`).
- [`figure_annotator_widget.py`](figure_annotator_widget.py): reusable `FigureAnnotatorWidget` (`anywidget.AnyWidget`) with Just-In-Time (JIT) hover spotlights, color-matched explanation badges, click-box-to-jump-to-step navigation, and original figure caption display.
- [`figure_annotator_example.py`](figure_annotator_example.py): standalone runnable Marimo notebook demonstrating `FigureAnnotatorWidget` across all panels of Figure 1 (Panels A–C) and Figure 2 (Transient Absorption & Inset Quantum Yield) from an open-access TADF photocatalysis paper (PMC13643228).
- [`method_diagrams.md`](method_diagrams.md): drawing the paper's method as a hand-drawn ELK Mermaid flowchart whose detail follows the reader's explanation level: stage-graph data, one view per level, readability rules, and a visual check.
- [`final-quiz.md`](final-quiz.md): what to ask in the required end-of-notebook quiz, and how to use the `PaperQuiz` widget in `assets/`.

Marimo widget patterns and pitfalls live in the installed skill [`.agents/skills/marimo-notebook-patterns/`](../.agents/skills/marimo-notebook-patterns/SKILL.md), not here.

**Planned contents:**

- Pedagogy notes: pacing, prerequisites, check-for-understanding patterns.
- **TODO:** `learning-path-template.md` for Phase 2 planning.
- Notes on pairing with the hackathon *Visual LaTeX* idea for equation visualization.

Add short, focused markdown files here as collaborators contribute them.
