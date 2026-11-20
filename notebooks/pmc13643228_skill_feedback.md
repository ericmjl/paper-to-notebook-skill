# Skill feedback from the PMC13643228 notebook

Test of the paper-to-notebook-skill on Fina et al., *Chemical Science* **2026**, *17*, 21624–21634 (DOI 10.1039/d6sc06836g, PMC13643228). The notebook is `pmc13643228_tadf_photocatalysis.py`. Nothing under `SKILL.md` or `resources/` was edited. These are the places the written workflow was ambiguous or fought the marimo skills while this notebook was being built.

## 1. HTML ingest is still a TODO, and this paper's equations are images

`SKILL.md` marks PDF and HTML ingest as TODO and says to flag failures rather than guess. That instruction is right, and it is also the whole procedure.

What actually happened:

- `curl` of `https://pmc.ncbi.nlm.nih.gov/articles/PMC13643228/` returned a reCAPTCHA page, not the article.
- Europe PMC HTML and the RSC article page returned Cloudflare 403. The PMC OA `fcgi` link 404'd. BioC JSON returned no result.
- NCBI eutils `efetch` (`db=pmc`, `rettype=xml`) and Europe PMC `fullTextXML` did return the full text. The skill never names those endpoints.
- Equations (1), (3), and (4) are `<graphic>` webp files (`d6sc06836g-t1.webp`, `t2`, `t3`) with no MathML and no alt text. The image binaries were not fetchable (403/404). Equation (2) is real text: Φr,tot = Φr,S + Φr,T. The notebook therefore does not transcribe (1), (3), or (4). It labels the product form used in the demo as a reading of how the text uses those equations, not a copy of the glyphs.
- Figure image binaries from PMC were also blocked. The notebook uses the copies already in `resources/figures/fig1.webp` and `fig2.webp`.
- The SI PDF, which holds the Fig. 4 rate constants, was not downloadable. Those constants are absent from the notebook.

The skill needs a fallback order (PMC XML, then Europe PMC XML, then HTML) and an explicit rule for an equation that is only a graphic: do not OCR it into a numbered equation; say the glyph is missing.

## 2. `mo` as a cell parameter fights `app.setup`

`resources/explanation-levels.md` shows the ladder as `def _(mo):` and `def _(mo, reader_level):`. `SKILL.md` says to follow that file.

`.agents/skills/marimo-notebook-patterns/SKILL.md` says the opposite for a notebook that uses setup: `import marimo as mo` goes in `with app.setup(hide_code=True):`, and cells then use bare `mo` with no `mo` parameter. Passing `mo` into a cell that can already see the setup global is a multiply-defined name.

Those two files were both required reading before any cell was written, and they disagree. This notebook followed the marimo skill (setup holds `mo`; cells do not take it). The paper skill should say that when the two conflict, the marimo skill wins, and it should update the explanation-level snippets so they are not copied in.

A related trap in the same skill file: a cell renders only its last top-level expression. The first draft of the hero cell called `mo.Html(...)` and then `mo.md(...)`. The banner never appeared. `uv run scripts/validate_notebook.py --run` and `uvx marimo check --strict` both passed. Only the browser showed the missing banner. Wrapping both in `mo.vstack` fixed it. The paper skill's generate step should say this in one sentence; it is easy to miss inside the long marimo skill, and the validator cannot see it.

`marimo check --strict` also failed until `mo.md` strings were dedented (markdown-indentation, six cells). `marimo check --fix` rewrote them. The paper skill's cell examples are indented inside the function, which is what triggered the warning.

## 3. The OpenAlex sample procedure does not survive contact with the API

`resources/field-maturity.md` asks for one query, `title_and_abstract.search` with 3–6 keywords, at most 30 works and 90 seconds, one retry, 15 s timeout.

- The first request returned HTTP 429. The procedure does not mention a `User-Agent` or a polite `mailto`, which is what Crossref also required before it would answer.
- OpenAlex treats `title_and_abstract.search` as an AND of the tokens. "cage escape photoredox singlet triplet" returned 3 works: a cage-escape review, this paper, and this paper's data deposit. That is not a sample you can use for a dominance count.
- The degradation rule ("set the class from the paper; add a TODO that vocabulary dominance was not verified") is usable, and this notebook followed it. What is missing is what to do when the query is too strict rather than down: drop to fewer tokens, or search a concept id, before declaring the sample failed. The notebook states the class from the paper and says the literature count was not verified. It does not invent a 30-work tally.

Crossref worked with `User-Agent: paper-to-notebook-skill/1.0 (mailto:research@example.com)`. Romero, *Chem. Rev.* 2016, DOI 10.1021/acs.chemrev.6b00057, stayed at 429 and was left out. The skill should say: if a DOI does not resolve, do not cite it.

## 4. The figure-annotation example states numbers that are not in the paper

`resources/figure_annotator_example.py` is the worked tour for this paper's Figures 1 and 2. Its step text includes quantities that are not printed in the main text and that this notebook refused to copy:

- "only 0.2 eV" for the singlet–triplet gap
- "acridinium-imidazolium" as the catalyst description
- ΔA ≈ 0.023 and ΔA ≈ 0.009 read off the traces
- Φr,tot ≈ 0.28 at 0.3 mM and ≈ 0.13 at 13 mM read off the inset

An agent that treats the example as source text will fabricate results. The skill should say the example's boxes may be reused after a visual audit, and its prose may not, unless each number is also in the paper.

The audit itself is a visual judgment. `dynamic_figure_annotation.md` says to overlay a 100×100 grid on a private copy and not guess. It does not say how close a crosshair must sit, or what to do when a box is the region between points. On Fig. 2 the high-[Q] crosshair sits in the space between points; the box was kept as a region, and the badge text does not quote an eyeballed absorbance.

The lifetime ratio ~2600 in this notebook is labeled as arithmetic on Fig. 1B (44 µs / 17 ns), not as a reported result.

## 5. "Our demo" has no boundary, and the two skill families want opposite things

`awesome-marimo-notebook` asks for an original quantitative extension. The paper skill says not to invent plots or results, and Fig. 4's rate constants live in an SI PDF that could not be fetched.

This notebook draws a grouped bar chart from the phenol cage-escape efficiencies and the two Fig. 2 quenching pairs, and it labels the chart **Our demo**. It does not fit kq or kisc, and it does not present the bars as Fig. 4. The skill never says whether that is allowed. A one-line rule would do: a demo may recombine numbers that are already in the main text, must say so in the cell, and may not introduce a rate, a yield, or a fit that the paper does not print.

## 6. Smaller gaps that cost time

- **Where helpers live.** `PaperQuiz` and `FigureAnnotatorWidget` import from the notebook's directory, because `uv run notebook.py` puts that directory on `sys.path`. The skill points at `assets/paper_quiz.py` and `resources/figure_annotator_widget.py` and does not say to vendor them (or the figure images) beside the notebook. This notebook copies all three into `notebooks/`.
- **CellTour.** `SKILL.md` still lists "whether to mandate `wigglystuff.CellTour`" as an open decision. The marimo skills treat a 7–12 stop tour as part of the notebook. This notebook includes one (`auto_start=False`, 10 stops, tour cell excluded). The paper skill should pick.
- **Default audience.** Still TODO. The notebook defaults the picker to Undergrad, which matches the working assumption in `SKILL.md` ("undergrad through graduate student") and is a judgment, not a rule.
- **What the validator checks.** `scripts/validate_notebook.py --run` checks syntax, `marimo check --strict`, and a smoke run. It does not check that the five quiz questions are about the paper, that the two ladders are different, that every number has a section or figure, or that a cell's first output is actually visible. Those are the failure modes this skill cares about.
- **`uv` was not on PATH.** The skill says to validate with `uv run` and does not say what to do when `uv` is missing. It was installed from https://astral.sh/uv/install.sh into `~/.local/bin` (uv 0.13.9).
