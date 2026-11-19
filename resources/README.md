# resources/

Reference documents the agent should **read** while planning or building a notebook—not large blobs to paste into every output.

**Contents:**

- [`explanation-levels.md`](explanation-levels.md): explaining one mechanism at five prerequisite-defined levels, with profiles, ledgers, level-matched checks, and tested marimo cells.
- [`field-maturity.md`](field-maturity.md): classifying established vs. emergent vs. interdisciplinary fields; vocabulary onboarding components; runtime literature-sampling procedure.
- [`field-maturity-research-notes.md`](field-maturity-research-notes.md): auditable API sampling for Bayesian/MCMC, LLM agents, and scRNA-seq integration.
- [`examples/`](examples/): complete example ladders for real papers (UMAP; influenza reassortment); field-maturity notebook mocks (`field-maturity-*.md`).
- [`dynamic_figure_annotation.md`](dynamic_figure_annotation.md): resource: self-verification workflow for dynamically annotating scientific figures and data plots using a 100×100 percentage slice grid, ink/color-channel segment isolation, a visual crosshair audit contact sheet, and `FigureAnnotatorWidget`.
- [`figure_annotator_widget.py`](figure_annotator_widget.py): reusable `FigureAnnotatorWidget` (`anywidget.AnyWidget`) with Just-In-Time (JIT) hover spotlights, color-matched explanation badges, click-box-to-jump-to-step navigation, and original figure caption display.
- [`figure_annotator_example.py`](figure_annotator_example.py): standalone runnable Marimo notebook demonstrating `FigureAnnotatorWidget` across all panels of Figure 1 (Panels A–C) and Figure 2 (Transient Absorption & Inset Quantum Yield) from an open-access TADF photocatalysis paper (PMC13643228).
- [`final-quiz.md`](final-quiz.md): what to ask in the required end-of-notebook quiz, and how to use the `PaperQuiz` widget in `assets/`.

**Planned contents:**

- Marimo widget patterns and footguns (may point to [ericmjl/skills](https://github.com/ericmjl/skills) `marimo-notebook-patterns`).
- Pedagogy notes: pacing, prerequisites, check-for-understanding patterns.
- **TODO:** `learning-path-template.md` for Phase 2 planning.
- Notes on pairing with the hackathon *Visual LaTeX* idea for equation visualization.

Add short, focused markdown files here as collaborators contribute them.
