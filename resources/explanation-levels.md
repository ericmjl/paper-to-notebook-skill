# Explaining at multiple levels

Reference for the **Explaining at multiple levels** section of [`SKILL.md`](../SKILL.md). Read it before writing explanation ladders.

An **explanation ladder** explains one core mechanism at five levels. Each level is written for a reader with specific prerequisites and adds precision to the same mechanism. The model is WIRED's [5 Levels](https://www.wired.com/video/series/5-levels/) series: one expert explains one idea to five listeners of rising expertise, and each explanation is complete and correct for its listener.

This guide refines Step 1 of marimo-team's [`implement-paper`](https://github.com/marimo-team/skills/tree/main/skills/implement-paper) skill ("gauge what the user already knows… skip basics they're familiar with, explain prerequisites they're not") into a repeatable procedure.

---

## 1. Define readers by prerequisites, not age

The level names are **shorthand**. What defines a level is the subject knowledge and math the reader brings, and what precision the level adds.

| Level (shorthand) | Subject knowledge assumed | Math assumed | What this level adds to the mechanism |
|---|---|---|---|
| 1 · Child | Everyday experience only | Counting and comparison ("more", "less", "twice as") | The mechanism as cause and effect in everyday terms |
| 2 · Teen | General science literacy: what a cell, a dataset, or a probability is | Arithmetic, fractions and percentages, reading a simple chart | The mechanism run on a toy example with real, small numbers |
| 3 · Undergrad | An introductory course in the paper's field and its core vocabulary | The field's introductory tools (e.g. algebra, summation, basic probability; calculus or linear algebra where the field uses them) | The exact form: the key equation or algorithm, every symbol defined |
| 4 · Grad student | Working knowledge of an adjacent area and its standard methods | Follows derivations in the paper's notation family | Why it is built this way: assumptions, when it holds, what breaks, how it compares with the standard approach |
| 5 · Expert | This subfield's literature | Full formalism, used only to state what's new | What is new relative to prior work, trade-offs, limits, and open questions |

### Write a prerequisite profile for each paper (Phase 1)

"An introductory course in the field" means different things for a topology-heavy method, a phylogenetics study, and a neuroimaging cohort. So for each paper, fill in this table before writing any ladder:

| Level | Assumes the reader knows | Does not assume | Must teach before or at this level |
|---|---|---|---|

Use it two ways:

- **Choosing the reader's level.** Map what the user tells you about their background (as asked in `implement-paper` Step 1) onto a row. If they don't say, use the audience from the Inputs table.
- **Filling gaps.** Anything in the "must teach" column gets a short explanation at that level, or in the Setup section.

---

## 2. Explain one mechanism at every level

1. **Write the mechanism spine first.** This is one sentence, at Level 3 precision, saying what the method does and how. Every level explains this same spine; no level swaps in a different or vaguer mechanism.
2. **Each level adds precision to the spine** (the last column of the table above). It doesn't add a new topic.
3. **Test for specificity.**
   - At Levels 1–2 the explanation may fit the method's whole family. (UMAP's own paper says neighbour-graph methods "must follow a similar basic structure".)
   - From Level 3 on, it must say what sets *this* method apart. If a Level 3+ explanation would be equally true of a different method, it is too vague.
4. **Test for sameness.** Read the five levels in order. Each should be recognizably the same process with more detail, like zooming in on one picture.

---

## 3. Keep every level accurate: the simplification ledger

Simplify by leaving things out, never by saying something false. Every simplification is a debt that a later level repays.

Keep a ledger for each ladder, in the transcript or a scratch file:

| Simplification | Introduced at | What is actually true | Corrected at |
|---|---|---|---|

- Every row is corrected at a later level, in so many words: "Earlier we said X; more precisely, Y." A row may be repaid in stages, so list every level that corrects part of it.
- A row that can't be corrected without the full formalism is corrected at Grad student or Expert level.
- Higher levels can show the ledger to readers as a short "What we simplified" note.

---

## 4. Analogies: map the parts and state the limit

1. **Choose one anchor:** an analogy or toy example introduced at Level 1 or 2 and built on at each level up to Level 3. Levels 4 and 5 may drop it once its limit has been stated.
2. **Map it.** List each part of the analogy next to the part of the mechanism it stands for. A part with no counterpart in the method invites a wrong inference, so drop it or address it. The map must include **what the method acts on** (the data, sequences, or scans); otherwise a Level 1 reader can't connect the story to the paper.

   | In the analogy | In the method |
   |---|---|

3. **State the limit** by Level 3, or at the first level where it matters: what the analogy gets wrong, and what is true instead.
4. **Don't anthropomorphize** ("the model wants", "the network decides") unless the analogy is labelled as one and its limit is stated.

---

## 5. Comprehension checks matched to each level

Each level gets at least one check, tied to what that reader should be able to do afterwards. The same targets are what any evaluation of the ladder should test.

| Level | The reader can… | Check format | Feedback |
|---|---|---|---|
| 1 · Child | **Explain** what it does and why it matters | Pick the everyday picture that fits (`mo.ui.radio`), or teach it back in a sentence | Says why each option fits or doesn't |
| 2 · Teen | **Predict** how the toy example responds to a change | Commit to a prediction, then reveal | Re-runs the toy example with the change |
| 3 · Undergrad | **Apply** the equation or algorithm to a tiny new input | Numeric answer with a tolerance (`mo.ui.text`, parsed) | Shows the worked computation |
| 4 · Grad student | **Apply and critique** assumptions: what breaks when one fails | Scenario question with an explanation | Names the assumption and cites where the paper states it |
| 5 · Expert | **Critique**: name a limitation, or the experiment that would test a claim | Open answer, then compare with a model answer | Model answer, citing what the paper did or didn't do |

Every check has an expected answer, the reasoning behind it, and the paper location it relies on. Write these when you write the level, not afterwards.

- **Level-locked.** A check must be answerable from its own level's text plus the levels below. A Child check can't depend on an idea first introduced at Teen.
- **Not answerable cold.** If a smart reader could answer it without the notebook, it tests prior knowledge. Make it specific to this paper: its toy numbers, its design, its splits.
- **Audit the answers like prose.** Check expected answers and rubrics against the paper, including its figures. A trend that "increases" in the text may flatten in the figure's last bin.

---

## 6. Choosing what gets a ladder

Give full ladders to **1–3 concepts per notebook**:

- the **core idea** from Phase 2, and
- the concept with the **biggest prerequisite gap** in the profile.

Everything else gets one explanation at the reader's level. A supporting concept likely to trip readers up gets a single "Simpler version" accordion one level down.

---

## 7. Length, vocabulary, and grounding

| Level | Length | Vocabulary |
|---|---|---|
| 1 · Child | 2–4 sentences of about 15 words or fewer | Everyday words, no jargon |
| 2 · Teen | 3–5 sentences of about 20 words or fewer, plus one line of toy numbers (not counted) | 1–2 field terms, each defined (the concept's own name doesn't count) |
| 3 · Undergrad | 1–3 short paragraphs (about 150–350 words) plus the equation | Standard field vocabulary |
| 4 · Grad student | 1–3 paragraphs (about 150–350 words) | The paper's notation |
| 5 · Expert | 1–2 paragraphs (about 100–250 words) | Terse and technical |

**When a level runs long**, don't cram it:

- Teach the profile's must-teach items earlier, in Setup or a lower level.
- Move ledger corrections into a short "What we simplified" note under the level.

In our tests on three papers, an Undergrad level that introduced six untaught terms in one paragraph was the level readers struggled with most.

**Define what you use.** Any term from the profile's "does not assume" column that a level uses is defined at that level or earlier.

**Grounding:**

- Write ladders after the paper has been read in (Phase 1). From Level 3 up, cite equation, section, table, or figure numbers from the text you actually have.
- **Numbers carry their conditions.** Name the table or column, cohort, feature set, or range in the same sentence: "test error 6.6 days (external cohort, raw features; Table 4)", not "test error 6.6 days". In our tests, both misconceptions the ladders caused came from a number stripped of its condition.
- **Comparisons state where they hold:** "higher accuracy at the two largest k tested (Table 2)", not "higher accuracy".
- **Check completeness words against the paper.** Sweep "only", "all", "first", "the best", and "never" against the paper's own list of evidence. "Validated only against simulations" was wrong in one test, because the paper also validates against known reassortants.
- **When the paper disagrees with itself** (text vs. table vs. figure), give both values with both locations. Don't silently pick one.
- **Never guess a number or location.** While drafting, mark gaps as `[cite: …]` or `[TODO: …]`. Before shipping, resolve them, or replace them with plain words such as "the paper doesn't say whether…". No drafting markers in reader-facing text.
- If the concept supports the paper's contribution rather than being it (for example, a building block in a systems paper), Level 5 states the concept's role in that contribution.
- Keep the authors' hedges: "the authors suspect" stays a suspicion.

---

## 8. Worked example: self-attention

From *Attention Is All You Need* (Vaswani et al., 2017).

**Prerequisite profile**

| Level | Assumes | Does not assume | Must teach |
|---|---|---|---|
| Child | Reading a sentence; words can refer to other words | Any computing terms | — |
| Teen | Computers store words as lists of numbers; percentages | Vectors, softmax | A relevance score; scores that add up to 1 |
| Undergrad | Vectors, dot products, matrix multiplication; what a neural-network layer is | Softmax | Softmax turns scores into weights that sum to 1 |
| Grad student | Recurrent sequence-to-sequence models; gradient-based training | The specifics of additive attention | — |
| Expert | Attention in sequence-to-sequence models; translation benchmarks | — | — |

**Mechanism spine:** self-attention rebuilds each word's vector as a weighted average of every word's *value* vector, with the weights given by a softmax over how well that word's *query* matches each word's *key*.

**The ladder**

> **1 · Child.** In *"The dog chased its tail,"* you know whose tail it is by looking back at *dog*. Attention lets a computer do that. For every word, it decides which other words to look at, and how much.

> **2 · Teen.** The computer gives each word a score for how relevant every other word is. For *its*, it might score *dog* 0.8, *tail* 0.15, and *chased* 0.05; the scores always add up to 1. It then builds a new version of *its* by blending the words in those proportions: mostly *dog*, a little of the rest.

> **3 · Undergrad.** Each word is a vector. Three learned matrices turn it into a **query** *q* (what am I looking for?), a **key** *k* (what do I contain?), and a **value** *v* (what do I pass on?). A word's scores are the dot products of its query with every key, scaled and passed through softmax; its output is the weighted sum of the values (Eq. 1, Section 3.2.1):
>
> $$\mathrm{Attention}(Q, K, V) = \mathrm{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}\right)V$$
>
> The 0.8 / 0.15 / 0.05 from Level 2 is one row of that softmax, and the words being "blended" are really their value vectors. Here the "looking back" picture breaks: in the encoder, every word attends to every word, including itself and words that come later.

> **4 · Grad student.** The authors suspect that for large $d_k$ the dot products grow large and push softmax into regions with tiny gradients; dividing by $\sqrt{d_k}$ counters that (Section 3.2.1). They choose dot-product over additive attention (Bahdanau et al.) because it runs as optimized matrix multiplication. A self-attention layer links any two positions in a constant number of sequential steps, at $O(n^2 \cdot d)$ cost per layer (Table 1). Because attention ignores order, position must be injected separately through positional encodings (Section 3.5).

> **5 · Expert.** Attention wasn't new; the contribution is showing that a model built only from attention and feed-forward layers, with no recurrence or convolution, beats the best previous translation results on WMT 2014 while training far faster. Earlier we described one set of weights per word; the model actually runs $h = 8$ attention heads in parallel, which offsets the loss of resolution from averaging over positions (Sections 2 and 3.2.2). The cost is quadratic in sequence length; for very long inputs the authors suggest restricting attention to a local neighborhood (Section 4).

**Simplification ledger**

| Simplification | Introduced at | What is actually true | Corrected at |
|---|---|---|---|
| Attention "looks back" | Child | In the encoder, every word attends to all words, including later ones | Undergrad |
| It blends "the words" | Teen | It blends value vectors, which are learned projections of the words | Undergrad |
| Scores measure "relevance" | Teen | Scores are scaled dot products of queries and keys | Undergrad |
| One set of weights per word | Undergrad | Eight heads compute separate weights in parallel | Expert |

**Analogy map**

| In the analogy | In the method |
|---|---|
| Reading *its* and looking back at *dog* | The query of *its* compared with the key of *dog* |
| How much you look at each word | The attention weight (one softmax output) |
| What you take away from *dog* | The value vector of *dog* |
| **Limit:** you look back at a few words | Every word attends to every word, ahead and behind, with weights summing to 1 |

**Checks**

| Level | Check | Expected answer and reasoning |
|---|---|---|
| Child | Which is closest to what attention does? (a) reads words one by one, in order; (b) for each word, decides which other words to look at, and how much; (c) counts how often each word appears | (b). That is the mechanism. (a) is how older recurrent models read; (c) ignores how words relate. |
| Teen | If *dog*'s score for *its* dropped from 0.8 to 0.4, would the new *its* be more or less like *dog*? | Less. The blend takes 40% from *dog* instead of 80%. |
| Undergrad | One word's three scores are 2, 0 and 0. What weight does softmax give the first? | ≈ 0.79, since $e^2 / (e^2 + 1 + 1) = 7.39 / 9.39$. |
| Grad student | With $d_k = 512$ and no scaling, what tends to happen to the softmax weights? | They become nearly all-or-nothing, with one weight near 1. The authors suspect this leaves tiny gradients (Sec. 3.2.1). |
| Expert | What experiment would show whether multiple heads matter, rather than extra computation? | Vary the number of heads while holding computation fixed. The paper reports this (Table 3, rows A; Sec. 6.2): one head is worse than the best setting, and quality also drops with too many heads. |

**More worked examples**, each with a profile, spine, all five levels, ledger, analogy map, and checks:

- [UMAP](examples/ladder-umap.md): a mathematically dense method paper.
- [Reassortment and influenza host switching](examples/ladder-influenza-reassortment.md): an analysis paper, where the "mechanism" is a measurement against a null.

---

## 9. Notebook pattern

This section covers what is specific to ladders. For general cell conventions (PEP 723 metadata, naming, `marimo check`), follow marimo-team's [`marimo-notebook`](https://github.com/marimo-team/skills/tree/main/skills/marimo-notebook) skill, and Eric Ma's [`marimo`](https://github.com/ericmjl/skills/tree/main/skills/marimo) skill where installed. Following Eric's preference, the examples use descriptive names rather than `_`-prefixed ones.

**One level picker near the top.** Its default comes from the reader's mapped level.

```python
@app.cell
def _(mo):
    LEVELS = ["Child", "Teen", "Undergrad", "Grad student", "Expert"]
    reader_level = mo.ui.dropdown(
        options=LEVELS,
        value="Grad student",  # set from the reader's mapped level
        label="Explain it at this level:",
    )
    reader_level
    return LEVELS, reader_level
```

**A check helper, defined once.** It shows the check for whichever tab is open, and gives feedback once the reader answers.

```python
@app.cell
def _(mo):
    def show_check(tabs, checks, answers):
        """Show the check for the open tab of a ladder, with feedback once answered.

        `checks` is a mo.ui.dictionary of widgets keyed by level. `answers[level]` has
        "correct" (an option string, a float, or None for open answers), an optional
        "tolerance" for numbers, and "why" (the reasoning, citing the paper).
        """
        level = tabs.value
        answer = answers[level]
        response = checks.value[level]
        if response in (None, ""):
            feedback = mo.md("*Answer to see feedback.*")
        elif answer["correct"] is None:
            feedback = mo.callout(mo.md(f"**Compare with ours:** {answer['why']}"), kind="info")
        else:
            if isinstance(answer["correct"], float):
                try:
                    right = abs(float(response) - answer["correct"]) <= answer.get("tolerance", 0.01)
                except ValueError:
                    right = False
            else:
                right = response == answer["correct"]
            feedback = mo.callout(
                mo.md(("**Right.** " if right else "**Not quite.** ") + answer["why"]),
                kind="success" if right else "warn",
            )
        return mo.vstack([mo.md(f"**Check your understanding ({level})**"), checks[level], feedback])
    return (show_check,)
```

**Per ladder: tabs, checks, and the check display.** The tabs open on the reader's level, and the check below follows whichever tab is open. Checks live in their own cell, so answering one never resets the tabs.

```python
@app.cell
def _(mo, reader_level):
    attention_tabs = mo.ui.tabs(
        {
            "Child": mo.md("In *The dog chased its tail*, you know whose tail it is by looking back at *dog*. ..."),
            "Teen": mo.md("The computer gives each word a score ..."),
            "Undergrad": mo.md(
                r"""
                ...
                $$\mathrm{Attention}(Q, K, V) = \mathrm{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}\right)V$$
                """
            ),
            "Grad student": mo.md(r"The authors suspect that for large $d_k$ ..."),
            "Expert": mo.md("Attention wasn't new; the contribution is ..."),
        },
        value=reader_level.value,
    )
    mo.vstack([mo.md("### Self-attention lets every word look at every other word"), attention_tabs])
    return (attention_tabs,)


@app.cell
def _(mo):
    attention_checks = mo.ui.dictionary({
        "Child": mo.ui.radio(
            options=["It reads the words one by one, in order",
                     "For each word, it decides which other words to look at, and how much",
                     "It counts how often each word appears"],
            label="Which is closest to what attention does?"),
        "Teen": mo.ui.radio(
            options=["More like 'dog'", "Less like 'dog'", "No change"],
            label="If dog's score for 'its' dropped from 0.8 to 0.4, the new 'its' would be…"),
        "Undergrad": mo.ui.text(
            placeholder="e.g. 0.50",
            label="Scores are 2, 0 and 0. What weight does softmax give the first?"),
        "Grad student": mo.ui.radio(
            options=["They become nearly all-or-nothing", "They become nearly equal", "They stop summing to 1"],
            label="With d_k = 512 and no scaling, the softmax weights tend to…"),
        "Expert": mo.ui.text_area(
            rows=3, label="What experiment would show whether multiple heads matter, rather than extra computation?"),
    })
    attention_answers = {
        "Child": {"correct": "For each word, it decides which other words to look at, and how much",
                  "why": "That's the mechanism. Reading in order is how older recurrent models work."},
        "Teen": {"correct": "Less like 'dog'", "why": "The blend now takes 40% from *dog* instead of 80%."},
        "Undergrad": {"correct": 0.79, "tolerance": 0.02, "why": "$e^2 / (e^2 + 1 + 1) = 7.39 / 9.39 \\approx 0.79$."},
        "Grad student": {"correct": "They become nearly all-or-nothing",
                         "why": "Large dot products saturate the softmax; the authors suspect tiny gradients result (Sec. 3.2.1)."},
        "Expert": {"correct": None,
                   "why": "Vary the number of heads with computation held fixed. The paper reports this "
                          "(Table 3, rows A; Sec. 6.2): one head is worse, and so are too many."},
    }
    return attention_answers, attention_checks


@app.cell
def _(attention_answers, attention_checks, attention_tabs, show_check):
    show_check(attention_tabs, attention_checks, attention_answers)
    return
```

**Other uses of `reader_level`:**

- Expand optional derivations (`mo.accordion`) by default only at Grad student and Expert.

---

## 10. Pitfalls

- **The same paragraph with the jargon swapped out.** Each level should add precision, not restate the previous level with harder words.
- **A different mechanism at Level 1.** A vague story that would fit any method fails the specificity test (§2).
- **A decorative analogy.** If its parts don't map onto the method's parts (§4), it misleads at Level 3.
- **Unpaid simplifications.** Every row in the ledger gets corrected at a later level.
- **Checks that test reading, not understanding.** "What did Level 2 say?" is recall. Ask the reader to explain, predict, apply, or critique.
- **Numbers without conditions.** "6.6 days" invites the wrong reading; "6.6 days (external cohort, raw features)" doesn't.
- **Condescension.** Level 1 is simple, not cute.
- **Invented context.** Claims about prior work or novelty come from the paper and what it cites. Label your own perspective ("Our take: …").

---

## Credits

- **WIRED, [5 Levels](https://www.wired.com/video/series/5-levels/):** the five-listener format.
- **marimo-team, [`implement-paper`](https://github.com/marimo-team/skills/tree/main/skills/implement-paper) (Apache-2.0):** the idea of gauging the reader's background before planning the notebook. This guide extends it into prerequisite profiles.
- **The explain / predict / apply / critique targets** loosely follow the revised Bloom's taxonomy (Anderson & Krathwohl, 2001: understand, apply, analyze, evaluate).
- **The "don't anthropomorphize" rule** is adapted from the `scientific-writing` skill in K-Dense's [claude-scientific-skills](https://github.com/K-Dense-AI/claude-scientific-skills) (MIT).
- **Eric Ma, [`marimo`](https://github.com/ericmjl/skills/tree/main/skills/marimo) skill (MIT):** the naming preference used in the examples.
- **Worked example:** Vaswani et al. (2017), *Attention Is All You Need*.
- **Revisions from testing on real papers:** the length bands, the overflow rule, conditions on numbers, completeness words, level-locked checks, and the Level 1–2 specificity rule. These came from testing on UMAP (McInnes, Healy & Melville, 2018), Ma et al. (2016, *PNAS*), and a 2026 neonatal brain-age study (*Dev. Cogn. Neurosci.*).
