# Explaining at multiple levels

Reference for the **Explaining at multiple levels** section of [`SKILL.md`](../SKILL.md). Read it before writing the explanation ladder.

An **explanation ladder** explains the paper's main point at five levels. Each level is written for a reader with specific prerequisites, and every level carries the same five parts: the question, what the authors did, what they found, why it matters, and its limits. Higher levels add depth to those parts; they don't swap in a different story. A reader sees only their own level, so each level stands alone. The model is WIRED's [5 Levels](https://www.wired.com/video/series/5-levels/) series: one expert explains one idea to five listeners of rising expertise, and each explanation is complete and correct for its listener.

This guide refines Step 1 of marimo-team's [`implement-paper`](https://github.com/marimo-team/skills/tree/main/skills/implement-paper) skill ("gauge what the user already knows… skip basics they're familiar with, explain prerequisites they're not") into a repeatable procedure.

---

## 1. Define readers by prerequisites, not age

The level names are **shorthand**. What defines a level is the subject knowledge and math the reader brings, and how deep the level goes.

| Level (shorthand) | Subject knowledge assumed | Math assumed | Depth of the five parts |
|---|---|---|---|
| 1 · Child | Everyday experience only | Counting and comparison ("more", "less", "twice as") | Cause and effect in everyday words |
| 2 · Teen | General science literacy: what a cell, a dataset, or a probability is | Arithmetic, fractions and percentages, reading a simple chart | The paper's headline numbers, with one or two field terms defined |
| 3 · Undergrad | An introductory course in the paper's field and its core vocabulary | The field's introductory tools (e.g. algebra, summation, basic probability; calculus or linear algebra where the field uses them) | The exact method: the key equation, algorithm, or analysis, every symbol defined |
| 4 · Grad student | Working knowledge of an adjacent area and its standard methods | Follows derivations in the paper's notation family | An abstract for a neighbouring field: the results with their anchors, plus why it is built this way |
| 5 · Expert | This subfield's literature | Full formalism, used only to state what's new | An abstract for this subfield: what is new against the prior work the paper discusses, the results at full precision, the main limit, and the open questions the paper names |

### Write a prerequisite profile for each paper (Phase 1)

"An introductory course in the field" means different things for a topology-heavy method, a phylogenetics study, and a neuroimaging cohort. So for each paper, fill in this table before writing the ladder:

| Level | Assumes the reader knows | Does not assume | Must teach at this level |
|---|---|---|---|

Use it two ways:

- **Choosing the reader's level.** Map what the user tells you about their background (as asked in `implement-paper` Step 1) onto a row. If they don't say, use the audience from the Inputs table.
- **Filling gaps.** Anything in the "must teach" column gets a short explanation at that level, or in the Setup section, using the paper's own definitions (§3).

---

## 2. Every level carries the paper's main point

1. **Write the spine first.** Before any level, record the paper's kind (rule 4), then fill in the five parts below at Level 3 precision, each with a verbatim quote and its location (section, figure, table, or equation):

   | Part | Says | Typical place in the paper |
   |---|---|---|
   | **Question** | What problem the paper takes on, and what was missing before | Abstract, introduction |
   | **What they did** | The method, data, or analysis, in the paper's terms | Methods, model or algorithm sections |
   | **What they found** | The headline results, with their numbers and conditions | Abstract, results, tables |
   | **Why it matters** | The authors' own claim of significance or novelty | Abstract, introduction, discussion, conclusion |
   | **Limits** | What the paper says it doesn't show, its scope, its stated weaknesses | Discussion, limitations, weaknesses, future work |

2. **Write the one-line summary.** From the spine, write one or two plain sentences, about 50 words at most, that say what the paper found, under what conditions, and why it matters, with a location. It sits above the ladder in the notebook, so the reader, and anyone checking the notebook, sees the main point first. If the sentence doesn't state a finding, the spine has missed the main point; fix the spine before writing any level.
3. **Every level has all five parts.** A Child level that explains only how the method works, or an Expert level that is the first to mention the result, has lost the main point. Read the five levels side by side: each part should appear in each level, deeper as the levels rise.
4. **Weight the parts by the paper's kind.** Decide what kind of paper it is from the contribution the authors lead with, then use its row: it says what each part means for that kind and which part gets the most space at every level. No level drops a part.

   | Kind | Question | What they did | What they found | Main limit to look for | Most space |
   |---|---|---|---|---|---|
   | Methods / algorithm | The gap in existing methods | The method | How well it works, against which baselines | Where it fails, what it costs | What they did |
   | Empirical / analysis | The hypothesis | The data and analysis | The effect, its direction and size | Causation, sampling, scope | What they found |
   | Theory | The conjecture or open problem | The proof approach | The theorems, as stated | The assumptions behind them | What they found |
   | Review / survey | The scope | How the literature was chosen | Where the field agrees and disagrees | What was left out | What they found |
   | Dataset / benchmark | The missing resource | How it was built | What baseline methods score on it | Biases in how it was collected | What they did |
   | Position / perspective | The claim argued | The argument | Its conclusions | What evidence it rests on | What they found |

   **Mixed papers:** use the row for the contribution the authors lead with, and treat the rest as supporting. The methods and empirical rows have been tested on real papers; the other four are a first pass, not yet tested.

5. **One story at every level.** Higher levels add precision to the same five parts. They don't introduce a different question or a vaguer method. If a Level 3+ explanation would be equally true of a different paper, it is too vague.
6. **Significance comes from the paper.** "Why it matters" states what the paper claims, with its location and the paper's own qualifiers (§7, *Voice*). Don't add your own assessment of impact, and don't describe what happened after publication.
7. **Each level stands alone.** Readers see only their own level, not the ones below it. So every level is complete by itself: no "earlier we said" or "as above", and every term it uses is either defined in it or assumed by its profile row.

**What to produce**, in the transcript or a scratch file, before the notebook cells:

1. The paper's kind, the prerequisite profile, and the spine.
2. The term ledger (§7).
3. The one-line summary and the five levels.
4. The simplification ledger (§4).
5. Notes for the user: terms the paper uses without defining, places where the paper disagrees with itself, and anything you couldn't read.

Only the summary and the levels reach the reader.

---

## 3. Use only the paper

Everything a ladder states about the work comes from the paper's full text. NotebookLM-style tools work the same way: answer only from the sources, and cite the passage.

**Before writing:**

- **Read the whole paper, or don't summarize it.** If you can't get the full text, or parts the main point depends on are unreadable (equations or tables that exist only as images, a missing results section), stop and ask the learner for the PDF. Don't write a ladder from the abstract or from the parts you could read.
- **Read it fresh.** Don't rely on what you remember about the paper or its field.
- **Collect the evidence first.** Build a list of verbatim quotes with their locations, covering the five parts. Write the ladder from that list.

**While writing:**

- **No outside facts.** Nothing from other papers, later work, textbooks, or general knowledge of the field, even if it's true. Claims about prior work or novelty come from what the paper itself says about them. This holds for the ladder and the final quiz. The notebook's glossary and vocabulary onboarding ([`field-maturity.md`](field-maturity.md)) may use outside sources, but only labelled as such.
- **Use the paper's definitions.** Define a term only the way the paper does. If the paper uses a term without defining it, describe it only by what the paper says about it ("roughly flat locally", from how the paper uses *manifold*), and list it in the notes for the user rather than importing a definition. This holds even when the main point rests on the term.
- **No invented numbers.** No toy examples or made-up figures. Use the paper's own numbers.
- **Numbers carry their conditions.** Name the table or column, cohort, feature set, or range in the same sentence: "test error 6.56 days (clinical cohort, raw features; Table 4)", not "test error 6.56 days". Copy the condition from the paper; don't reuse this example's wording. In our tests, both misconceptions the ladders caused came from a number stripped of its condition.
- **Use the paper's own differences and units.** Keep percentage points as percentage points, absolute differences as absolute, ratios as ratios, and the paper's units; never convert one kind of difference into another ("19 percentage points above the null" is not "19% more"). Only the Child level may simplify, to a plain comparison that is still true ("about twice as fast", "off by less than a week on average").
- **Comparisons state where they hold:** "higher accuracy at the two largest k tested (Table 2)", not "higher accuracy".
- **Compare against the strongest result reported.** For each comparison you make (a row, a dataset, a setting), name the best competing method in that comparison, not a convenient one; if the best one changes between rows, say so: "87 s against 292 s for the fastest t-SNE implementation (Table 3)", not only the slowest.
- **Check completeness words against the paper.** Sweep "only", "all", "first", "the best", and "never" against the paper's own list of evidence. "Validated only against simulations" was wrong in one test, because the paper also validates against known reassortants.
- **When the paper disagrees with itself** (text vs. table vs. figure, abstract vs. results), give both values with both locations wherever a level states the number; a level may instead leave that number out. Don't silently pick one, and list the disagreement in the notes for the user.
- **Keep the paper's hedges in the sentence:** what the paper suspects stays "probably" or "may", and "arguably" stays "arguably".
- **Never guess a number or location.** While drafting, mark gaps as `[cite: …]`. Before shipping, resolve them, or say plainly that it isn't reported. No drafting markers in reader-facing text.

**After writing:**

- **Check every claim.** Split each level into its claims, and match each one to a quote in the evidence list. Rewrite or delete any claim without one.
- **Check every quote.** Text in quotation marks must appear word for word in the paper:

  ```bash
  uv run scripts/check_quotes.py paper.txt ladder.md
  ```

  It lists each quote it can't find. Fix or remove every one.

---

## 4. Keep every level accurate: the simplification ledger

Simplify by leaving things out, never by saying something false. Because each level stands alone, a simplification is never fixed later in the reader's text; it has to be true as it stands.

Keep a ledger, in the transcript or a scratch file; readers don't see it:

| Level | Simplification | What the paper actually says | Why the simplified version is still true |
|---|---|---|---|

- Quote the ladder's own wording in italics, not quotation marks, so the quote check only sees the paper's words.
- If you can't fill the last column, the simplification is false: rewrite it at that level.

---

## 5. Analogies, only when they help

Use an analogy only when a level would otherwise be hard to follow. Plain words from the paper are better when they work. An analogy the paper itself makes (UMAP finding structure in noise "similar to the way the human mind finds structured constellations among the stars", §6) is paper content: use it with its location, unlabelled. An analogy of yours is not the paper's, so:

1. **Label it** ("Think of it like…") so it's never mistaken for the paper's claim.
2. **It adds no facts.** Everything it stands for is in the paper.
3. **Map it.** List each part of the analogy next to the part of the work it stands for, including **what the method acts on** (the data, sequences, or scans). A part with no counterpart invites a wrong inference, so drop it.

   | In the analogy | In the paper |
   |---|---|

4. **State its limit** in the level that uses it: what it gets wrong, and what the paper says instead.
5. **Don't anthropomorphize** ("the model wants", "the network decides") unless the analogy is labelled as one and its limit is stated.

---

## 6. One ladder per notebook

The ladder covers the paper's main point. Other concepts get one explanation at the reader's level. A concept likely to trip readers up gets a single "Simpler version" accordion one level down.

---

## 7. Length and vocabulary

| Level | Length (the upper number is a cap) | Vocabulary |
|---|---|---|
| 1 · Child | 3–5 sentences, about 12 words each, none over 15 | Words a young child knows: no acronyms, no names of methods or datasets, no technical words, no numbers beyond small counts and comparisons |
| 2 · Teen | 5–8 sentences, about 20 words each, none over 25 | 1–3 field terms, each defined from the paper; acronyms and names explained (below) |
| 3 · Undergrad | 200–400 words in 2–4 short paragraphs, plus one displayed equation | Standard field vocabulary |
| 4 · Grad student | One paragraph, 6–8 sentences, 150–220 words | The paper's notation; terms the profile doesn't assume defined in passing |
| 5 · Expert | One paragraph, 4–6 sentences, 100–180 words | Standard field terms, undefined |

**How to count.** Count words in the level's text, leaving out locations in parentheses ("(§3.1, Table 2)", "(Appendix C)", "(Fig. 8)") and math. A sentence ends at a full stop, question mark, or exclamation mark. `uv run scripts/check_levels.py ladder.md` counts each level and flags anything over its cap.

**Over the cap, cut; don't add notes.** Cut in this order: context, then secondary results, then design detail. Keep the main result with its anchor, the claim of novelty, and the main limit. If a level still runs over, teach fewer terms in it, not more briefly.

In our tests on three papers, an Undergrad level that introduced six untaught terms in one paragraph was the level readers struggled with most.

**One displayed equation.** Undergrad displays the single equation most central to the main point; any other appears inline. The displayed equation doesn't split the paragraph it sits in. If the paper uses one symbol for two things, you may rename one, saying so in the level.

**Define what you use.** Any term a level uses that its profile row doesn't assume is defined in that level.

**Acronyms and names.** At the Child, Teen, and Undergrad levels, every acronym and every named method, model, or dataset is explained at first use, or left out. At the Grad student level, acronyms the profile assumes may stand; any other gets a short definition in passing. At the Child level there are none: say what the thing does ("a new way to draw data as a map"), not what it's called. Everyday names, such as languages and countries, are fine.

- An acronym's expansion is not an explanation; "t-distributed stochastic neighbor embedding" tells a Teen reader nothing. Say what the thing is or does.
- Prefer the paper's own spelling-out. If the paper never spells an acronym out, describe the thing and give the name as a label after it: "a standard 2014 English-to-German test (WMT 2014)".
- As a rare exception, when an acronym is unavoidable and its expansion genuinely helps, you may spell it out on first use even though the paper doesn't.

### Grad student and Expert read like abstracts

Write these two levels the way a strong abstract is written: one paragraph, one job per sentence.

1. **Order:** context, the gap ("However, …"), one sentence that states what was done and matches the gap, the results, what they change compared with the prior work the paper discusses, and the implication with its limits.
2. **The finding is the subject.** Lead with the method or result and put the action in the verb: "The Transformer replaces recurrence with attention alone (§3)."
3. **Numbers beat adjectives.** Each result has its number and a named anchor: the strongest baseline reported, the previous best, the benchmark, and n or an interval where the paper gives them. Never "significantly better".
4. **Confidence at the paper's level.** Strong verbs for results; hedges only where the paper hedges, usually the outlook and limits.
5. **Tense:** past for what was done and found, present for established facts and what they imply.
6. **Old information first, new last** in each sentence, so the number or claim lands at the end.
7. **One term per concept** throughout; no synonyms for variety.
8. **Grad student** opens from the broader field. It may add one sentence on why the method is built the way it is, and one on how the result was checked, if the paper checks it. **Expert** opens at the gap, names benchmarks and scale, says what the work overturns or refines against prior work, and names the main limitation.

Unlike a journal abstract, each sentence keeps its location in parentheses, since every claim must trace to the paper.

### Voice

Write the content, not the reporting, in everything the reader sees: the summary, the levels, and the quiz. (Working tables such as the ledgers are exempt.) State what the work did and found directly, and let the location in parentheses carry the attribution:

- "Self-attention links any two positions in a constant number of steps (§2)", not "The authors show that self-attention links…".
- Leave out "the authors", "the paper", "the study", "this work", and "they report, note, argue, or find".
- Subheadings inside a level name the part (*Question*, *Method*, *Findings*, *Why it matters and its limits*), not "what they did".
- Don't restate the reader's level in the text ("for the Grad student level"); the picker already shows it.
- A verbatim quote keeps the paper's own wording, including its "we"; the voice rule applies to your sentences, not to what you quote.
- Bring quotes into the sentence the same way: "Attention mechanisms were used “in conjunction with a recurrent network” in all but a few cases (§1)."
- Hedges and claims of novelty keep the paper's own qualifier in the sentence ("probably", "arguably"), so the direct voice never turns a suspicion into a fact. For "to the best of our knowledge", write "the first known … (§2)" or "as far as is known (§2)".

### The term ledger

List the paper's field terms before writing the levels, and record which levels must define each one:

| Term | Defined in the paper? | Status | Levels that must define it |
|---|---|---|---|

- **The profile decides.** A level may use a term undefined only if its profile row assumes it.
- **Whether the paper defines a term is evidence for the profile, not a rule.** A term the paper defines is probably new to some of its readers; a term it uses undefined is assumed in its own field, so Expert can use it, and Grad student too if the profile says so.
- **Status**, adapting [`field-maturity.md`](field-maturity.md)'s classes to single terms:
  - *established*, including terms the paper defines operationally (a grading scale, a threshold): follow the profile, and define them as the paper does;
  - *emergent* (recent, or with competing labels in the paper): define it at every level up to Grad student; at Expert, add a short gloss only if the paper itself flags the term as unsettled;
  - *overloaded* (a different meaning in a neighbouring field or in everyday speech, such as *cluster*, *feature*, *batch*, *attention*): define it at every level up to Grad student, because the reader brings the other meaning.

**Check:** no level uses a term undefined unless its profile row assumes it. A grad-level term in the Teen level is the classic failure.

### Check the ladder as a whole

Writers misjudge what readers already know, so check the levels against the text, not your sense of them:

- **Trends from Undergrad up.** From Undergrad to Expert, definitions, analogies, and linking words should become fewer, and notation, named methods, and stated limits more frequent. (Child has nothing to define, so definitions rise from Child to Undergrad.) A level that breaks a trend is probably at the wrong level.
- **Don't over-explain at the top.** An Expert level full of definitions is pitched too low; scaffolding that helps newcomers gets in experts' way.
- **Readability scores are only a ceiling for Child and Teen.** A grade score such as Flesch–Kincaid measures only word and sentence length, so it misreads short sentences dense with jargon. Use it to catch a Child or Teen level that runs too hard, never to judge Undergrad and above.

---

## 8. Worked example

[`examples/ladder-umap.md`](examples/ladder-umap.md) is a complete run of this guide on a methods paper: the paper kind, profile, spine, term ledger, one-line summary, all five levels, the simplification ledger, and the notes for the user. A fresh agent wrote it from the paper's text and this guide alone. Its level-matched quiz ([`final-quiz.md`](final-quiz.md)) is [`examples/quiz-umap.json`](examples/quiz-umap.json).

---

## 9. Notebook pattern

Use `ExplainLevels` from [`assets/explain_levels.py`](../assets/explain_levels.py). Copy it next to the notebook, add `anywidget` and `traitlets`, wrap with `mo.ui.anywidget`, and pass `paper_ref` (a section, figure, equation, or algorithm of this paper), `summary` (the one-line summary), and `tabs=False`, so the reader sees only their own level. Leave out `check`: the final quiz is matched to the level. Trait schema and snippets: [`explain_levels.md`](explain_levels.md). Demo: [`explain_levels_example.py`](explain_levels_example.py).

This section covers what is specific to the ladder. For general cell conventions (PEP 723 metadata, naming, `marimo check`), follow marimo-team's [`marimo-notebook`](https://github.com/marimo-team/skills/tree/main/skills/marimo-notebook) skill, and Eric Ma's [`marimo`](https://github.com/ericmjl/skills/tree/main/skills/marimo) skill where installed. Following Eric's preference, the examples use descriptive names rather than `_`-prefixed ones. Where these snippets and the installed marimo skills disagree, the marimo skills win.

The cells assume `import marimo as mo` in `with app.setup(hide_code=True):`, so they use `mo` without taking it as a parameter. A cell shows only its last expression: wrap several outputs in `mo.vstack([...])`.

**Hide the code.** Every cell below is `@app.cell(hide_code=True)`. The reader sees the level picker, the one-line summary, and their own level. Leave a cell's code visible only when that code is itself the teaching point, and say so in the prose beside it.

**One level picker near the top.** Its default comes from the reader's mapped level. Pass `level=reader_level.value` into `ExplainLevels` so the one picker drives the ladder and every other section.

```python
@app.cell(hide_code=True)
def _():
    LEVELS = ["Child", "Teen", "Undergrad", "Grad student", "Expert"]
    reader_level = mo.ui.dropdown(
        options=LEVELS,
        value="Grad student",  # set from the reader's mapped level
        label="Explain it at this level:",
    )
    reader_level
    return LEVELS, reader_level
```

**The ladder: the one-line summary, then only the reader's level.** Readers see their own level, so there are no tabs; the level picker at the top changes it, and every other section follows the same picker without restating it.

```python
@app.cell(hide_code=True)
def _(reader_level):
    paper_ladder = mo.ui.anywidget(ExplainLevels(
        title="...",  # the paper's title
        paper_ref="...",  # the sections the spine draws on
        summary="...",  # the one-line summary
        tabs=False,  # readers see only their own level
        level=reader_level.value,
        levels=[
            {"name": "Child", "text": "..."},
            {"name": "Teen", "text": "..."},
            {"name": "Undergrad", "text": r"... $$...$$ ..."},  # raw string for LaTeX
            {"name": "Grad student", "text": r"..."},
            {"name": "Expert", "text": r"..."},
        ],
    ))
    paper_ladder
    return (paper_ladder,)
```

**Other uses of `reader_level`:**

- Expand optional derivations (`mo.accordion`) by default only at Grad student and Expert.

---

## 10. Pitfalls

- **Mechanics instead of the main point.** A ladder that explains how the method works but never says what the paper asked, found, or concluded misses the paper. Every level has all five parts (§2).
- **The result saved for Expert.** If a Child reader can't say what was found, the ladder has failed.
- **A one-line summary with no finding.** "This paper introduces a method for X" says what was done, not what was found.
- **The same paragraph with the jargon swapped out.** Each level should add depth, not restate the previous level with harder words.
- **Outside knowledge.** A true fact from outside the paper is still outside the paper (§3).
- **A decorative analogy.** If it doesn't help, or its parts don't map (§5), cut it.
- **A simplification that's false as it stands.** Each level stands alone, so no later level will fix it (§4).
- **Leaning on another level.** "As we saw", "earlier", or a term defined only in a lower level breaks a level that has to stand alone.
- **Numbers without conditions.** "6.6 days" invites the wrong reading; "6.6 days (external cohort, raw features)" doesn't.
- **Condescension.** Level 1 is simple, not cute.
- **A tour of the field.** Levels 4–5 still explain this paper's main point. One-line pointers to a work the paper itself depends on are enough; do not survey adjacent areas.
- **Reporting voice.** "The authors found…" and "the paper shows…" put a narrator between the reader and the work. State it, and cite it (§7).
- **Acronyms at the bottom of the ladder.** An undefined acronym or method name at Child or Teen level is a wall, not a word (§7).
- **Definitions at the Expert level.** Defining what experts know is pitched too low (§7).

---

## Credits

- **WIRED, [5 Levels](https://www.wired.com/video/series/5-levels/):** the five-listener format.
- **marimo-team, [`implement-paper`](https://github.com/marimo-team/skills/tree/main/skills/implement-paper) (Apache-2.0):** the idea of gauging the reader's background before planning the notebook. This guide extends it into prerequisite profiles.
- **The five-part spine** draws on [paper-reader-heilmeier](https://github.com/RealZYZhang/paper-reader-heilmeier) (Heilmeier's questions, main point first), [paper-to-intuition](https://github.com/majiayu000/claude-skill-registry-data) (key insight before the level ladder), and [Paper-insight](https://github.com/Stars-Shen/Paper-insight-skill) (findings with what they don't prove).
- **The grounding rules** follow NotebookLM's source-grounded answers, Anthropic's [reduce-hallucinations guidance](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations) (quotes first, then check each claim), and the full-text gate in [paper-digest](https://github.com/drpwchen/paper-review-and-digest).
- **The abstract style for the top two levels** follows Nature's guide to [constructing a summary paragraph](https://www.nature.com/documents/nature-summary-paragraph.pdf), Mensh & Kording's [*Ten simple rules for structuring papers*](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005619) (2017), Gopen & Swan's [*The Science of Scientific Writing*](https://cseweb.ucsd.edu/~swanson/papers/science-of-writing.pdf) (1990), and the abstract skills in [research-agent-skills](https://github.com/KalarisLabs/research-agent-skills) and [nature-writing-skill](https://github.com/SyntaxSmith/nature-writing-skill).
- **The "don't anthropomorphize" rule** is adapted from the `scientific-writing` skill in K-Dense's [claude-scientific-skills](https://github.com/K-Dense-AI/claude-scientific-skills) (MIT).
- **Eric Ma, [`marimo`](https://github.com/ericmjl/skills/tree/main/skills/marimo) skill (MIT):** the naming preference used in the examples.
- **Worked example:** McInnes, Healy & Melville (2018), *UMAP*; the short examples of voice and abstract style quote Vaswani et al. (2017), *Attention Is All You Need*.
- **Revisions from testing on real papers:** the length caps and cut order, standalone levels, conditions on numbers and the paper's own units, completeness words, the strongest-baseline rule, and the term-ledger rules. These came from fresh agent runs on UMAP (McInnes, Healy & Melville, 2018), *Attention Is All You Need* (Vaswani et al., 2017), and a 2026 neonatal brain-age study (*Dev. Cogn. Neurosci.*), and earlier tests on Ma et al. (2016, *PNAS*).
