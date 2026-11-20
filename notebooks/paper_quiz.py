"""A multiple-choice quiz anywidget for the end of a paper notebook.

Copy this file next to the generated notebook and use it in the final cell:

    from paper_quiz import PaperQuiz

    quiz = mo.ui.anywidget(PaperQuiz(questions=[
        {
            "question": "What did the authors compare?",
            "answer": "The right answer.",
            "explain": "Why it is right, pointing to the paper section/figure.",
            "distractors": {
                "A plausible wrong answer.": "The misconception it targets and why it is wrong.",
                "Another plausible wrong answer.": "Why it is wrong.",
                "A third plausible wrong answer.": "Why it is wrong.",
            },
        },
        # ... five questions in total
    ]))
    quiz

Each question is written with the correct answer separate from the
distractors. The widget places the options itself: correct-answer positions
are spread across A-D (each letter is used before any repeats) in a shuffled
order, so the answer key is never a pattern. Pass `seed=` to get a different
but still reproducible layout.

The reader clicks an option, sees whether it was right, and reads the
explanation for the option they picked (and the correct one, if they missed).
`quiz.value["selected"]` holds the chosen option index per question
(-1 if unanswered) and `quiz.value["score"]` the number correct.
"""

import random

import anywidget
import traitlets

_ESM = """
function render({ model, el }) {
  const style = document.createElement("style");
  style.textContent = `
    .pq-root { font-family: inherit; display: flex; flex-direction: column; gap: 1.25rem; }
    .pq-card { border: 1px solid rgba(128,128,128,.35); border-radius: 10px; padding: 1rem 1.1rem; }
    .pq-q { font-weight: 600; margin: 0 0 .75rem; line-height: 1.4; }
    .pq-opts { display: flex; flex-direction: column; gap: .45rem; }
    .pq-opt { all: unset; box-sizing: border-box; display: flex; gap: .6rem; align-items: baseline;
      padding: .55rem .75rem; border: 1px solid rgba(128,128,128,.35); border-radius: 8px;
      cursor: pointer; line-height: 1.35; }
    .pq-opt:hover:not([disabled]) { border-color: rgba(70,130,220,.8); background: rgba(70,130,220,.08); }
    .pq-opt[disabled] { cursor: default; }
    .pq-letter { font-weight: 700; min-width: 1.2em; }
    .pq-opt.pq-right { border-color: rgb(40,160,90); background: rgba(40,160,90,.12); }
    .pq-opt.pq-wrong { border-color: rgb(210,70,70); background: rgba(210,70,70,.12); }
    .pq-opt.pq-dim { opacity: .55; }
    .pq-fb { margin-top: .75rem; padding: .6rem .8rem; border-radius: 8px; line-height: 1.45;
      background: rgba(128,128,128,.1); }
    .pq-fb p { margin: .25rem 0; }
    .pq-footer { display: flex; gap: 1rem; align-items: center; }
    .pq-score { font-weight: 600; }
    .pq-reset { all: unset; cursor: pointer; padding: .35rem .8rem; border-radius: 6px;
      border: 1px solid rgba(128,128,128,.5); }
  `;
  el.appendChild(style);

  const root = document.createElement("div");
  root.className = "pq-root";
  el.appendChild(root);

  const LETTERS = ["A", "B", "C", "D"];

  function pick(qi, oi) {
    const sel = [...model.get("selected")];
    if (sel[qi] !== -1) return;
    sel[qi] = oi;
    model.set("selected", sel);
    model.save_changes();
  }

  function draw() {
    const items = model.get("_items");
    const sel = model.get("selected");
    root.replaceChildren();

    items.forEach((item, qi) => {
      const card = document.createElement("div");
      card.className = "pq-card";

      const q = document.createElement("p");
      q.className = "pq-q";
      q.textContent = `${qi + 1}. ${item.question}`;
      card.appendChild(q);

      const opts = document.createElement("div");
      opts.className = "pq-opts";
      const chosen = sel[qi];
      const answered = chosen !== -1;

      item.options.forEach((opt, oi) => {
        const b = document.createElement("button");
        b.className = "pq-opt";
        if (answered) {
          b.disabled = true;
          if (oi === item.answer) b.classList.add("pq-right");
          else if (oi === chosen) b.classList.add("pq-wrong");
          else b.classList.add("pq-dim");
        }
        const l = document.createElement("span");
        l.className = "pq-letter";
        l.textContent = LETTERS[oi];
        const t = document.createElement("span");
        t.textContent = opt.text;
        b.append(l, t);
        b.addEventListener("click", () => pick(qi, oi));
        opts.appendChild(b);
      });
      card.appendChild(opts);

      if (answered) {
        const fb = document.createElement("div");
        fb.className = "pq-fb";
        const lines = [];
        if (chosen === item.answer) {
          lines.push(`<strong>Correct.</strong> ${esc(item.options[chosen].why)}`);
        } else {
          lines.push(`<strong>Not quite.</strong> ${esc(item.options[chosen].why)}`);
          lines.push(`<strong>Answer: ${LETTERS[item.answer]}.</strong> ${esc(item.options[item.answer].why)}`);
        }
        fb.innerHTML = lines.map((s) => `<p>${s}</p>`).join("");
        card.appendChild(fb);
      }
      root.appendChild(card);
    });

    const footer = document.createElement("div");
    footer.className = "pq-footer";
    const done = sel.filter((s) => s !== -1).length;
    const score = document.createElement("span");
    score.className = "pq-score";
    score.textContent = `Score: ${model.get("score")} / ${items.length}` +
      (done < items.length ? ` (${items.length - done} unanswered)` : "");
    const reset = document.createElement("button");
    reset.className = "pq-reset";
    reset.textContent = "Start over";
    reset.addEventListener("click", () => {
      model.set("selected", items.map(() => -1));
      model.save_changes();
    });
    footer.append(score, reset);
    root.appendChild(footer);
  }

  function esc(s) {
    const d = document.createElement("div");
    d.textContent = s ?? "";
    return d.innerHTML;
  }

  model.on("change:selected", draw);
  model.on("change:score", draw);
  draw();
}
export default { render };
"""


class PaperQuiz(anywidget.AnyWidget):
    _esm = _ESM
    _items = traitlets.List().tag(sync=True)
    selected = traitlets.List().tag(sync=True)
    score = traitlets.Int(0).tag(sync=True)

    def __init__(self, questions, seed=0, **kwargs):
        rng = random.Random(seed)
        n = len(questions)
        offset = rng.randrange(4)
        positions = [(i + offset) % 4 for i in range(n)]
        rng.shuffle(positions)

        items = []
        for q, pos in zip(questions, positions):
            distractors = list(q["distractors"].items())
            if len(distractors) != 3:
                raise ValueError(
                    f"Question {q['question']!r} needs exactly 3 distractors, "
                    f"got {len(distractors)}."
                )
            rng.shuffle(distractors)
            options = [{"text": t, "why": w} for t, w in distractors]
            options.insert(pos, {"text": q["answer"], "why": q["explain"]})
            items.append({"question": q["question"], "options": options, "answer": pos})

        super().__init__(_items=items, selected=[-1] * n, **kwargs)

    @traitlets.observe("selected")
    def _update_score(self, change):
        self.score = sum(
            s == item["answer"] for s, item in zip(change["new"], self._items)
        )
