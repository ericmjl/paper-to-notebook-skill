# Paper to guided marimo learning notebook

A reusable **agent skill** that turns a published research paper into a [marimo](https://marimo.io) notebook: plain-language explanations, interactive widgets for key equations and figures, and checks for understanding along the way.

Born at the **snake_case 2026** hackathon (Posit, Austin, Nov 19–20, 2026). This repo is a collaborative workspace for [Eric Ma](https://github.com/ericmjl)'s project idea.

**Repository description:** A megaskill (or multiple skills) to create notebook explainers for published papers.

## The problem

Research papers are dense. Many readers skim equations and figures instead of working through them, so the ideas never really land.

## The goal

Build a skill an AI agent can follow to:

1. Read a paper and identify what a learner must understand.
2. Plan a guided path through concepts, equations, and figures.
3. Generate a marimo notebook with explanations, interactive widgets, and comprehension checks.
4. Validate that the notebook runs end-to-end.

**Hackathon stretch (two days):** a working first version of the skill, plus notebooks generated from a few real papers. Exact paper list: **TODO.**

## How this repo is laid out

| Path | Role |
|------|------|
| [`SKILL.md`](SKILL.md) | Agent skill entry point (Agent Skills format). |
| [`assets/`](assets/) | Templates and static files (e.g. notebook starter). |
| [`resources/`](resources/) | Reference material the agent should read (marimo widgets, pedagogy). |
| [`scripts/`](scripts/) | Helper scripts (e.g. validate a generated notebook). |
| [`evals/`](evals/) | Promptfoo test cases, a synthetic paper, and runnable marimo fixtures. |

Style and patterns for marimo work also live in Eric's skill collection: [github.com/ericmjl/skills](https://github.com/ericmjl/skills) (e.g. `marimo`, `marimo-notebook-patterns`, `awesome-marimo-notebook`).

## Run the notebook eval

The [eval setup](evals/README.md) includes two local checks for table accuracy and widget behavior. An optional model judge compares the notebook's explanation with the paper to catch unsupported interpretations.

## Try it with an agent

**TODO:** pin exact install paths for Cursor, Claude Code, and other hosts.

Placeholder workflow:

1. Clone this repo (or add it as a skill path).
2. Point your agent at `SKILL.md` when you want a guided learning notebook for a paper.
3. Provide the paper (PDF, URL, or arXiv id).
4. Ask the agent to follow the skill and write the notebook to a path you choose.
5. Run validation when available:

   ```bash
   uv run scripts/validate_notebook.py path/to/notebook.py
   ```

6. Open the notebook:

   ```bash
   uv run marimo edit path/to/notebook.py
   ```

## Help wanted

- **marimo widgets** — sliders, anywidgets, and math-friendly interactions.
- **Teaching and learning design** — pacing, scaffolding, comprehension checks.
- **Visualizing math** — pairs with a sibling *Visual LaTeX* hackathon idea.

Interested collaborators (from the attendee doc): Daina Bouquin, Ben Lear, Josh Starmer, Leland McInnes, Erik Welch, Leon Johnson, Carol Willing, Matthew Feickert, Konstantin Taletskiy, Ariana Mendible.

## How to contribute

Issues and PRs welcome during and after the hackathon.

1. Open an issue to discuss scope, or grab a **TODO** in `SKILL.md` / this README.
2. Keep changes focused; match the tone of existing docs.
3. Prefer `uv run` for Python commands; do not document global `pip install` as the default path.
4. When adding marimo guidance, link or mirror relevant notes in `resources/` rather than duplicating long references in `SKILL.md`.

**Open decisions (TODO):**

- Single megaskill vs. split skills (e.g. paper ingestion, pedagogy, marimo build).
- Default audience level (undergrad, grad, practitioner).
- Licensing for generated notebooks vs. skill metadata.

## License

**TODO:** choose license (Eric's other skills often use MIT — confirm for this repo).
