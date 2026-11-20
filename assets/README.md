# assets/

Static files and templates the agent copies or fills when generating a notebook.

**Contents:**

- `paper_quiz.py` — `PaperQuiz` anywidget for the 5-question end-of-notebook quiz when that component is included (see `resources/final-quiz.md`).
- `mermaid_view.py` — `MermaidView` anywidget that renders Mermaid with the ELK layout in the hand-drawn look, for method diagrams (see `resources/method_diagrams.md`).
- `explain_levels.py` — `ExplainLevels` anywidget for five-level explanation ladders (see `resources/explanation-levels.md` and `resources/explain_levels.md`). Copy and import it the same way as the other assets.

The four notebook tools (`PaperQuiz`, `FigureAnnotatorWidget`, `MermaidView`, `ExplainLevels`) are documented in `SKILL.md` under Tools. `FigureAnnotatorWidget` lives in `resources/figure_annotator_widget.py`, not here.

**Planned:**

- `notebook_template.py` — starter marimo app (hero, section headers, empty check cells).
- Reusable snippets for comprehension checks and notation tables.
- Optional images, SVG motifs, or CSS shared across generated notebooks.

**TODO:** add the first notebook template during the hackathon.