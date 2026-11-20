# Final quiz

When the **final quiz** is included, the generated notebook ends with **5 multiple-choice questions about the paper itself**, matched to the reader's explanation level. Read this before writing them. Skip this file when the user left the final quiz out.

Quiz questions are only about this paper. Do not quiz on adjacent literature, extra examples, or the notebook's own demos or toy simulations.

The quiz is an informal check, not formal assessment. It closes the notebook.

## What to ask

**Quiz the substance, not the machinery.** Questions should be about what the paper claims, what it found, why those findings follow, what they mean beyond the specific system, and what the paper says it cannot conclude. A reader who understood the paper should get them right; one who skimmed the abstract should not.

Ask about a method **only when understanding it is needed to understand what the result means** — for example, when a result is a comparison against a baseline and the reader would misread the number without knowing that. Do not ask about implementation detail: software names and versions, parameter values, thresholds, database download dates, sample sizes, or the order of processing steps. If the answer is a fact a reader could copy from the Methods section without understanding the paper, cut the question.

Across the 5, aim to cover:

1. The central claim.
2. A main finding and its direction.
3. Why a finding follows — the mechanism or the reasoning.
4. An exception, or a boundary of the claim.
5. What the paper cannot conclude.

## Match the quiz to the reader's level

Write **five questions for each of the five levels** in [`explanation-levels.md`](explanation-levels.md), 25 in all. The notebook shows the set for the reader's level.

- **Same targets at every level.** Each set covers the five targets above, like the explanation ladder covers its five parts at every level.
- **Answerable from that level alone.** Readers see only their own level, so the correct answer to each question comes from that level's ladder text. Explanations of why a distractor is wrong may cite anything in the paper.
- **That level's vocabulary throughout:** questions, options, explanations, and any quoted passage. At the Child level, a location such as "(§3)" is fine, and distractors name misconceptions in plain words rather than the paper's terms.
- **Targets 4 and 5 test different things.** Target 4 is a boundary or exception of a finding; target 5 is an overreach. Frame target 5 as "How firmly is X claimed?" or "Does X support Y?", so every option isn't also a valid conclusion.
- **Where the paper disagrees with itself,** a question can use the disagreement, and its explanation gives both values with both locations, as the ladder does.
- **Deeper as the levels rise:**

  | Level | Questions ask about | The reader should be able to |
  |---|---|---|
  | 1 · Child | The claim and the finding, in everyday words | Recall and explain |
  | 2 · Teen | The headline numbers, with their conditions | Explain |
  | 3 · Undergrad | How the result follows from what was measured or computed | Apply |
  | 4 · Grad student | Assumptions, what breaks when one fails, and how the result was checked (when the level says so) | Analyse and compare |
  | 5 · Expert | What is claimed as new, its limits, and what is left untested | Critique |

  The last column follows the revised Bloom's taxonomy: each level's questions need that kind of thinking, not just recall of the level's text.

- **Only the paper.** The same grounding rules as the ladder apply: every answer and explanation comes from the paper, with a location, and any quoted passage passes `scripts/check_quotes.py` (it reads a quiz saved as JSON directly).

## Rules for the options

- Each question has **4 options, exactly one correct**.
- **Distractors are plausible** given the paper: built from its real terms, numbers and findings, and each one targets a specific misconception a reader could plausibly hold. Common ones worth targeting:
  - confusing correlation with the causal claim;
  - mixing up what was measured with what was inferred;
  - overstating the scope of a result;
  - swapping which group showed the effect;
  - reversing the direction of an effect;
  - treating a well-explained exception as a contradiction.

  Avoid joke answers or options that are wrong on their face.
- Every option gets a short explanation: for the answer, why it is right with a pointer to the paper section or figure; for each distractor, the misconception it reflects and why the paper does not support it.
- Correct-answer positions vary across the 5 questions. The widget handles this: write the answer separately from the distractors and it places them.

## The widget

Use **`assets/paper_quiz.py`**, an anywidget. Copy it next to the notebook, add `anywidget` and `traitlets` to the PEP 723 dependencies, and import it in the cell that imports `marimo`:

```python
from paper_quiz import PaperQuiz
```

It shuffles the options, marks the chosen answer right or wrong, shows the explanations, and keeps a running score. Positions for the correct answer are spread across A–D (each letter used before any repeats) in a shuffled order, so the answer key is never a pattern; pass `seed=` for a different but reproducible layout.

`quiz.value["selected"]` holds the chosen option index per question (-1 if unanswered) and `quiz.value["score"]` the number correct, if you want to react to them in another cell.

## The final cells

Hide both cells. The reader sees the heading and the quiz; the Python is not the teaching point.

The cells assume `import marimo as mo` in `with app.setup(hide_code=True):` and the `reader_level` picker from [`explanation-levels.md`](explanation-levels.md) §9. Changing the level shows that level's set and clears the answers.

```python
@app.cell(hide_code=True)
def _():
    QUIZ_BY_LEVEL = {
        "Child": [
            {
                "question": "...",
                "answer": "...",
                "explain": "Why this is right (Fig. N / Section N).",
                "distractors": {
                    "Plausible wrong answer 1": "Misconception it targets, and why the paper does not support it.",
                    "Plausible wrong answer 2": "...",
                    "Plausible wrong answer 3": "...",
                },
            },
            # 5 questions per level
        ],
        "Teen": [...],
        "Undergrad": [...],
        "Grad student": [...],
        "Expert": [...],
    }
    return (QUIZ_BY_LEVEL,)


@app.cell(hide_code=True)
def _(PaperQuiz, QUIZ_BY_LEVEL, reader_level):
    quiz = mo.ui.anywidget(PaperQuiz(questions=QUIZ_BY_LEVEL[reader_level.value]))
    mo.vstack([
        mo.md("## Check yourself\n\nFive questions on the paper. Pick an answer to see why it is or isn't right."),
        quiz,
    ])
    return
```
