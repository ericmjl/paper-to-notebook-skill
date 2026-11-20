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

Style and patterns for marimo work come from Eric's skill collection, [github.com/ericmjl/skills](https://github.com/ericmjl/skills). The `marimo`, `marimo-notebook-patterns`, `awesome-marimo-notebook`, and `processing-friendly-prose` skills are installed in [`.agents/skills/`](.agents/skills/) and pinned in `skills-lock.json`; refresh them with `npx skills update`.

## Run the notebook eval

Start with the [eval setup instructions](evals/README.md#set-up-the-evals). The first run checks table accuracy and needs no API key. A separate local check covers widget behavior, and an optional model judge checks whether the paper supports the notebook's explanation.

## Install the skill

This skill uses the open [Agent Skills](https://agentskills.io) format. An agent installs it by copying the folder from https://github.com/ericmjl/paper-to-notebook-skill into wherever the harness keeps skills. Include `SKILL.md`, plus `scripts/`, `assets/`, `resources/`, and the vendored skills in `.agents/skills/`. Clone the repo or download the files.

```bash
git clone https://github.com/ericmjl/paper-to-notebook-skill path/to/skills/paper-to-notebook-skill
```

Optional: `npx skills add ericmjl/paper-to-notebook-skill`.

Give the agent a paper (PDF, URL, or arXiv id). When the notebook is ready:

```bash
uvx marimo edit --sandbox path/to/notebook.py
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

## Acknowledgments

Specific adaptations are credited in each resource file's **Credits** section.

- [WIRED, 5 Levels](https://www.wired.com/video/series/5-levels/): the format behind explanation ladders.
- [marimo-team/skills](https://github.com/marimo-team/skills) (Apache-2.0): `implement-paper`'s reader-background step, which the prerequisite profile extends.
- [Eric Ma's skills](https://github.com/ericmjl/skills) (MIT): `marimo` patterns and naming conventions.
- [K-Dense claude-scientific-skills](https://github.com/K-Dense-AI/claude-scientific-skills) (MIT): the anthropomorphism rule.
- Anderson & Krathwohl (2001): the revised Bloom's taxonomy behind the level-matched quiz.
- **Worked-example papers:**
  - Vaswani et al. (2017);
  - McInnes, Healy & Melville (2018), arXiv:1802.03426;
  - Ma, E. J. et al. (2016), PNAS 113:5335–5339.

## License

**TODO:** choose license (Eric's other skills often use MIT — confirm for this repo).
