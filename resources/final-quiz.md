# Final quiz

When the **final quiz** is included, the generated notebook ends with **5 multiple-choice questions about the paper itself**. Read this before writing them. Skip this file when the user left the final quiz out.

Do not quiz on the notebook's own demos or toy simulations.

The quiz is an informal check like the rest of the notebook's checks, not formal assessment. It closes the notebook; the level-matched checks in [`explanation-levels.md`](explanation-levels.md) stay where they are, alongside each ladder.

## What to ask

**Quiz the substance, not the machinery.** Questions should be about what the paper claims, what it found, why those findings follow, what they mean beyond the specific system, and what the paper says it cannot conclude. A reader who understood the paper should get them right; one who skimmed the abstract should not.

Ask about a method **only when understanding it is needed to understand what the result means** — for example, when a result is a comparison against a baseline and the reader would misread the number without knowing that. Do not ask about implementation detail: software names and versions, parameter values, thresholds, database download dates, sample sizes, or the order of processing steps. If the answer is a fact a reader could copy from the Methods section without understanding the paper, cut the question.

Across the 5, aim to cover:

1. The central claim.
2. A main finding and its direction.
3. Why a finding follows — the mechanism or the reasoning.
4. An exception, or a boundary of the claim.
5. What the paper cannot conclude.

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

```python
@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Check yourself

    Five questions on the paper. Pick an answer to see why it is or isn't right.
    """)
    return


@app.cell(hide_code=True)
def _(PaperQuiz, mo):
    quiz = mo.ui.anywidget(PaperQuiz(questions=[
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
        # 5 questions total
    ]))
    quiz
    return
```
