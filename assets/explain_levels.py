"""A five-level explanation ladder anywidget for paper notebooks.

Copy this file next to the generated notebook and use it in a cell:

    from explain_levels import ExplainLevels

    ladder = mo.ui.anywidget(ExplainLevels(
        title="UMAP's two-phase mechanism",
        paper_ref="Secs. 2–3, Algs. 1–5",
        level="Undergrad",
        levels=[
            {
                "name": "Child",
                "text": "Picture thousands of photos as a crowd…",
                "check": {
                    "question": "Which is closest to what UMAP does?",
                    "options": ["…", "…", "…"],
                    "correct": "…",
                    "why": "That is the mechanism (Sec. 3).",
                },
            },
            # Teen, Undergrad, Grad student, Expert…
        ],
    ))
    ladder

Each level is a dict with ``name``, ``text`` (markdown; HTML is escaped),
and an optional ``check``. A check is a multiple-choice question
(``options`` + ``correct`` as the matching option string), a numeric
question (``correct`` as a number, optional ``tolerance``), or an open
question (``correct`` is ``None``). After the reader answers, the widget
shows right/wrong feedback and the ``why``.

``level`` is the open rung. Pass a 0-based index or a level name; the
synced value is always the canonical name. A notebook-level picker can
drive several ladders by passing the same ``level=reader_level.value``
into each widget cell (see ``resources/explain_levels.md``). Changing
tabs inside the widget writes ``level`` back, so a downstream cell can
read ``ladder.value["level"]``.

``paper_ref`` is the paper section, figure, equation, or algorithm the
ladder is explaining. The widget will render without it; the
stick-to-the-paper rule still requires one — call
:func:`assert_paper_ref` from a validator, or pass it here.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Literal

import anywidget
import traitlets

DEFAULT_LEVEL_NAMES: tuple[str, ...] = (
    "Child",
    "Teen",
    "Undergrad",
    "Grad student",
    "Expert",
)
DEFAULT_NUMERIC_TOLERANCE = 0.01
CheckKind = Literal["choice", "numeric", "open"]

_CSS = """
.el-root {
  font-family: inherit;
  color: inherit;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  outline: none;
  box-sizing: border-box;
  width: 100%;
  max-width: 100%;
  min-width: 0;
}
.el-root:focus-visible {
  box-shadow: 0 0 0 2px rgba(70, 130, 220, 0.65);
  border-radius: 10px;
}
.el-root .katex { white-space: nowrap; }
.el-head {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem 1rem;
  align-items: baseline;
  justify-content: space-between;
}
.el-title {
  font-weight: 650;
  font-size: 1.05rem;
  margin: 0;
  line-height: 1.35;
}
.el-ref {
  font-size: 0.82rem;
  opacity: 0.82;
  padding: 0.12rem 0.6rem;
  border: 1px solid rgba(128, 128, 128, 0.35);
  border-radius: 999px;
  white-space: nowrap;
}
.el-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.28rem;
  padding: 0.28rem;
  border: 1px solid rgba(128, 128, 128, 0.35);
  border-radius: 10px;
}
.el-tab {
  all: unset;
  cursor: pointer;
  padding: 0.38rem 0.72rem;
  border-radius: 8px;
  line-height: 1.3;
}
.el-tab:hover { background: rgba(70, 130, 220, 0.08); }
.el-tab[aria-selected="true"] {
  background: rgba(70, 130, 220, 0.16);
  font-weight: 650;
}
.el-tab:focus-visible { box-shadow: 0 0 0 2px rgba(70, 130, 220, 0.7); }
.el-hint { font-size: 0.78rem; opacity: 0.7; margin: 0; }
.el-body, .el-check {
  border: 1px solid rgba(128, 128, 128, 0.35);
  border-radius: 10px;
  padding: 0.9rem 1.05rem;
  line-height: 1.5;
  min-width: 0;
  max-width: 100%;
  box-sizing: border-box;
}
.el-body p { margin: 0.55rem 0; min-width: 0; }
.el-body p:first-child { margin-top: 0; }
.el-body p:last-child { margin-bottom: 0; }
.el-body ul {
  margin: 0.4rem 0 0.55rem;
  padding-left: 1.25rem;
  list-style: disc outside;
}
.el-body ol {
  margin: 0.4rem 0 0.55rem;
  padding-left: 1.25rem;
  list-style: decimal outside;
}
.el-body li {
  margin: 0.2rem 0;
  display: list-item;
}
.el-body, .el-fb { overflow-x: auto; }
.el-math-scroll {
  display: block;
  overflow-x: auto;
  overflow-y: hidden;
  max-width: 100%;
  text-align: center;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: thin;
  scrollbar-color: rgba(128, 128, 128, 0.55) rgba(128, 128, 128, 0.14);
  /* Scroll shadows: a fade on the overflowing edge, independent of native bars. */
  background:
    linear-gradient(Canvas, Canvas) left center / 1.4rem 100% local no-repeat,
    linear-gradient(Canvas, Canvas) right center / 1.4rem 100% local no-repeat,
    linear-gradient(to right, color-mix(in srgb, currentColor 28%, transparent), transparent) left center / 1rem 100% scroll no-repeat,
    linear-gradient(to left, color-mix(in srgb, currentColor 28%, transparent), transparent) right center / 1rem 100% scroll no-repeat;
}
.el-math-scroll::-webkit-scrollbar { height: 8px; }
.el-math-scroll::-webkit-scrollbar-track {
  background: rgba(128, 128, 128, 0.14);
  border-radius: 999px;
}
.el-math-scroll::-webkit-scrollbar-thumb {
  background: rgba(128, 128, 128, 0.5);
  border-radius: 999px;
}
.el-math-scroll .katex-display {
  display: inline-block;
  margin: 0.75rem 0;
  text-align: left;
  max-width: none;
}
.el-check { display: flex; flex-direction: column; gap: 0.65rem; }
.el-check h3 { margin: 0; font-size: 0.95rem; }
.el-q { margin: 0; font-weight: 600; line-height: 1.4; }
.el-opts { display: flex; flex-direction: column; gap: 0.4rem; }
.el-opt {
  all: unset;
  box-sizing: border-box;
  cursor: pointer;
  padding: 0.5rem 0.7rem;
  border: 1px solid rgba(128, 128, 128, 0.35);
  border-radius: 8px;
  line-height: 1.35;
  display: flex;
  gap: 0.55rem;
  align-items: baseline;
}
.el-opt:hover { border-color: rgba(70, 130, 220, 0.8); background: rgba(70, 130, 220, 0.08); }
.el-opt.el-right { border-color: rgb(40, 160, 90); background: rgba(40, 160, 90, 0.12); }
.el-opt.el-wrong { border-color: rgb(210, 70, 70); background: rgba(210, 70, 70, 0.12); }
.el-opt.el-dim { opacity: 0.55; }
.el-letter { font-weight: 700; min-width: 1.15em; }
.el-input, .el-area {
  font: inherit;
  color: inherit;
  background: transparent;
  border: 1px solid rgba(128, 128, 128, 0.5);
  border-radius: 8px;
  padding: 0.45rem 0.65rem;
}
.el-area { min-height: 4.5rem; resize: vertical; }
.el-submit {
  all: unset;
  cursor: pointer;
  align-self: flex-start;
  padding: 0.35rem 0.85rem;
  border-radius: 6px;
  border: 1px solid rgba(128, 128, 128, 0.5);
}
.el-submit:hover { background: rgba(70, 130, 220, 0.08); }
.el-fb {
  padding: 0.6rem 0.8rem;
  border-radius: 8px;
  line-height: 1.45;
  background: rgba(128, 128, 128, 0.1);
  min-width: 0;
  max-width: 100%;
  box-sizing: border-box;
}
.el-fb.el-ok { background: rgba(40, 160, 90, 0.12); }
.el-fb.el-no { background: rgba(210, 70, 70, 0.12); }
.el-fb.el-info { background: rgba(70, 130, 220, 0.12); }
.el-fb p { margin: 0; }
"""

_ESM = r"""
import katex from "https://cdn.jsdelivr.net/npm/katex@0.16.21/dist/katex.mjs";

const LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";

function ensureKatexCss(el) {
  const id = "explain-levels-katex-css";
  const root = el.getRootNode();
  const inShadow = root instanceof ShadowRoot;
  const scope = inShadow ? root : document;
  if (scope.querySelector(`#${id}`)) return;
  const link = document.createElement("link");
  link.id = id;
  link.rel = "stylesheet";
  link.href = "https://cdn.jsdelivr.net/npm/katex@0.16.21/dist/katex.min.css";
  if (inShadow) root.appendChild(link);
  else document.head.appendChild(link);
}

function make(tag, cls, parent, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text !== undefined) e.textContent = text;
  parent?.append(e);
  return e;
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function extractMath(src) {
  const slots = [];
  const replaced = String(src).replace(
    /\$\$([\s\S]+?)\$\$|\$([^$\n]+)\$/g,
    (_, display, inline) => {
      const i = slots.length;
      slots.push({ display: Boolean(display), tex: (display || inline).trim() });
      return `%%MATH${i}%%`;
    },
  );
  return { replaced, slots };
}

function inlineFmt(s) {
  let t = escapeHtml(s);
  t = t.replace(/`([^`]+)`/g, "<code>$1</code>");
  t = t.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  t = t.replace(/(^|[^*])\*([^*]+)\*/g, "$1<em>$2</em>");
  t = t.replace(
    /\[([^\]]+)\]\((https?:[^)\s]+)\)/g,
    '<a href="$2" rel="noopener noreferrer" target="_blank">$1</a>',
  );
  t = t.replace(/\n/g, "<br>");
  return t;
}

function renderMarkdown(raw) {
  const { replaced, slots } = extractMath(String(raw ?? "").replace(/\r\n/g, "\n").trim());
  if (!replaced) return "";
  const blocks = replaced.split(/\n{2,}/);
  const html = blocks.map((block) => {
    const lines = block.split("\n");
    if (lines.some((l) => /^[-*] /.test(l))) {
      let out = "";
      let items = [];
      const flush = () => {
        if (!items.length) return;
        out += `<ul>${items.map((t) => `<li>${inlineFmt(t)}</li>`).join("")}</ul>`;
        items = [];
      };
      for (const line of lines) {
        if (/^[-*] /.test(line)) items.push(line.slice(2));
        else {
          flush();
          if (line) out += `<p>${inlineFmt(line)}</p>`;
        }
      }
      flush();
      return out;
    }
    const heading = lines[0].match(/^(#{1,3}) (.*)$/);
    if (heading) {
      const n = heading[1].length;
      const rest = lines.slice(1).join("\n");
      return `<h${n}>${inlineFmt(heading[2])}</h${n}>` +
        (rest ? `<p>${inlineFmt(rest)}</p>` : "");
    }
    return `<p>${inlineFmt(lines.join("\n"))}</p>`;
  }).join("");
  return html.replace(/%%MATH(\d+)%%/g, (_, i) => {
    const slot = slots[Number(i)];
    if (!slot) return "";
    try {
      const rendered = katex.renderToString(slot.tex, {
        displayMode: slot.display,
        throwOnError: false,
      });
      return slot.display
        ? `<span class="el-math-scroll">${rendered}</span>`
        : rendered;
    } catch {
      return `<code>${escapeHtml(slot.tex)}</code>`;
    }
  });
}

function verdict(check, response) {
  if (!check || response === undefined || response === null || response === "") return null;
  if (check.kind === "open") return null;
  if (check.kind === "numeric") {
    const n = Number(response);
    if (!Number.isFinite(n)) return false;
    const tol = Number(check.tolerance ?? 0.01);
    return Math.abs(n - Number(check.correct)) <= tol;
  }
  return response === check.correct;
}

function render({ model, el }) {
  ensureKatexCss(el);
  const root = make("div", "el-root", el);
  root.tabIndex = 0;
  const drafts = {};

  function levels() {
    return model.get("levels") || [];
  }
  function names() {
    return levels().map((lv) => lv.name);
  }
  function indexOf(level) {
    const list = names();
    const asName = String(level ?? "");
    let i = list.indexOf(asName);
    if (i >= 0) return i;
    const folded = asName.toLowerCase();
    i = list.findIndex((n) => String(n).toLowerCase() === folded);
    if (i >= 0) return i;
    const n = Number(level);
    if (Number.isInteger(n) && n >= 0 && n < list.length) return n;
    return 0;
  }
  function setLevel(i) {
    const list = names();
    if (!list.length) return;
    const next = Math.max(0, Math.min(list.length - 1, i));
    model.set("level", list[next]);
    model.save_changes();
  }
  function setResponse(i, value) {
    const current = [...(model.get("responses") || [])];
    while (current.length < levels().length) current.push("");
    current[i] = value;
    model.set("responses", current);
    model.save_changes();
  }

  function draw() {
    const list = levels();
    const i = indexOf(model.get("level"));
    const lv = list[i] || { name: "", text: "" };
    const responses = model.get("responses") || [];
    root.replaceChildren();

    const head = make("div", "el-head", root);
    if (model.get("title")) make("h2", "el-title", head, model.get("title"));
    if (model.get("paper_ref")) make("span", "el-ref", head, model.get("paper_ref"));

    const tablist = make("div", "el-tabs", root);
    tablist.setAttribute("role", "tablist");
    tablist.setAttribute("aria-label", "Explanation level");
    list.forEach((item, idx) => {
      const tab = make("button", "el-tab", tablist, item.name);
      tab.setAttribute("role", "tab");
      tab.setAttribute("aria-selected", idx === i ? "true" : "false");
      tab.addEventListener("click", () => setLevel(idx));
    });
    make("p", "el-hint", root, "← → to change level · 1–5 jump to a rung");

    const body = make("div", "el-body", root);
    body.setAttribute("role", "tabpanel");
    body.innerHTML = renderMarkdown(lv.text || "");

    const check = lv.check;
    if (!check) return;
    const checkBox = make("section", "el-check", root);
    make("h3", null, checkBox, `Check your understanding (${lv.name})`);
    make("p", "el-q", checkBox, check.question);
    const committed = responses[i] || "";
    const draft = drafts[i] ?? committed;

    if (check.kind === "choice") {
      const opts = make("div", "el-opts", checkBox);
      const answered = Boolean(committed);
      const right = verdict(check, committed);
      (check.options || []).forEach((opt, oi) => {
        const b = make("button", "el-opt", opts);
        if (answered) {
          if (opt === check.correct) b.classList.add("el-right");
          else if (opt === committed) b.classList.add("el-wrong");
          else b.classList.add("el-dim");
        }
        make("span", "el-letter", b, LETTERS[oi] || String(oi + 1));
        make("span", null, b, opt);
        b.addEventListener("click", () => {
          drafts[i] = opt;
          setResponse(i, opt);
        });
      });
      if (answered) {
        const fb = make("div", `el-fb ${right ? "el-ok" : "el-no"}`, checkBox);
        fb.innerHTML = `<p><strong>${right ? "Right." : "Not quite."}</strong> ${renderMarkdown(check.why)}</p>`;
      }
      return;
    }

    const isOpen = check.kind === "open";
    const input = make(isOpen ? "textarea" : "input", isOpen ? "el-area" : "el-input", checkBox);
    if (!isOpen) input.setAttribute("type", "text");
    input.setAttribute("aria-label", check.question);
    if (!isOpen) input.setAttribute("placeholder", "e.g. 0.53");
    input.value = draft;
    input.addEventListener("input", () => { drafts[i] = input.value; });
    const submit = make("button", "el-submit", checkBox, "Check");
    submit.addEventListener("click", () => {
      drafts[i] = input.value;
      setResponse(i, input.value);
    });
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !isOpen) {
        e.preventDefault();
        drafts[i] = input.value;
        setResponse(i, input.value);
      }
    });
    if (committed) {
      if (isOpen) {
        const fb = make("div", "el-fb el-info", checkBox);
        fb.innerHTML = `<p><strong>Compare with ours:</strong> ${renderMarkdown(check.why)}</p>`;
      } else {
        const right = verdict(check, committed);
        const fb = make("div", `el-fb ${right ? "el-ok" : "el-no"}`, checkBox);
        fb.innerHTML = `<p><strong>${right ? "Right." : "Not quite."}</strong> ${renderMarkdown(check.why)}</p>`;
      }
    }
  }

  root.addEventListener("keydown", (e) => {
    const tag = (e.target && e.target.tagName) || "";
    if (tag === "INPUT" || tag === "TEXTAREA") return;
    const i = indexOf(model.get("level"));
    if (e.key === "ArrowLeft") { e.preventDefault(); setLevel(i - 1); }
    else if (e.key === "ArrowRight") { e.preventDefault(); setLevel(i + 1); }
    else if (e.key === "Home") { e.preventDefault(); setLevel(0); }
    else if (e.key === "End") { e.preventDefault(); setLevel(names().length - 1); }
    else if (/^[1-9]$/.test(e.key)) {
      e.preventDefault();
      setLevel(Number(e.key) - 1);
    }
  });

  model.on("change:level", draw);
  model.on("change:levels", draw);
  model.on("change:title", draw);
  model.on("change:paper_ref", draw);
  model.on("change:responses", draw);
  draw();
}

export default { render };
"""


class ExplainLevelsError(ValueError):
    """Invalid ``ExplainLevels`` configuration."""


def resolve_level(level: int | str, names: Sequence[str]) -> int:
    """Return the 0-based index of ``level``.

    :param level: A 0-based index, or a level name (matched case-insensitively).
    :param names: The level names, in display order.
    :returns: The index into ``names``.
    :raises ExplainLevelsError: If ``level`` is not a valid index or name.
    """
    labels = [str(name) for name in names]
    if isinstance(level, bool) or not isinstance(level, (int, str)):
        raise ExplainLevelsError(
            f"level must be an index or name, got {type(level).__name__}"
        )
    if isinstance(level, int):
        if level < 0 or level >= len(labels):
            raise ExplainLevelsError(
                f"level index {level} is out of range for {len(labels)} levels"
            )
        return level
    wanted = level.casefold()
    for index, name in enumerate(labels):
        if name.casefold() == wanted:
            return index
    raise ExplainLevelsError(f"Unknown level {level!r}; expected one of {labels}")


def normalize_level(level: int | str, names: Sequence[str]) -> str:
    """Return the canonical level name for ``level``.

    :param level: A 0-based index or a level name.
    :param names: The level names, in display order.
    :returns: ``names[resolve_level(level, names)]``.
    """
    return str(names[resolve_level(level, names)])


def assert_paper_ref(paper_ref: str | None) -> str:
    """Require a paper section, figure, equation, or algorithm anchor.

    The widget trait is optional so a ladder can be tried on its own. The
    stick-to-the-paper rule still needs an anchor; a notebook validator can
    call this helper.

    :param paper_ref: The paper location the ladder is explaining.
    :returns: The stripped anchor.
    :raises ExplainLevelsError: If ``paper_ref`` is missing or blank.
    """
    text = str(paper_ref or "").strip()
    if not text:
        raise ExplainLevelsError(
            "paper_ref is required by the stick-to-the-paper rule "
            "(a section, figure, equation, or algorithm number)"
        )
    return text


def validate_check(
    check: Mapping[str, Any] | None, *, level_name: str = ""
) -> dict[str, Any] | None:
    """Return a normalized check dict, or ``None`` when the level has no check.

    Author schema:

    - ``question`` and ``why`` are required.
    - Multiple choice: ``options`` (two or more strings) and ``correct``
      matching one option.
    - Numeric: ``correct`` is an ``int`` or ``float``, optional
      ``tolerance`` (default 0.01).
    - Open: ``correct`` is ``None`` (or omitted, when there are no options).

    :param check: The author-facing check mapping, or ``None``.
    :param level_name: Used only in error messages.
    :returns: A dict with ``kind`` of ``choice``, ``numeric``, or ``open``.
    :raises ExplainLevelsError: If the check is incomplete or inconsistent.
    """
    if check is None:
        return None
    if not isinstance(check, Mapping):
        where = f" for {level_name}" if level_name else ""
        raise ExplainLevelsError(f"check{where} must be a mapping")
    where = f" for {level_name}" if level_name else ""
    question = str(check.get("question") or "").strip()
    why = str(check.get("why") or "").strip()
    if not question:
        raise ExplainLevelsError(f"each check{where} needs a question")
    if not why:
        raise ExplainLevelsError(f"each check{where} needs a why")

    options_raw = check.get("options")
    correct = check.get("correct", None)
    if options_raw is not None:
        if not isinstance(options_raw, Sequence) or isinstance(options_raw, (str, bytes)):
            raise ExplainLevelsError(f"check{where} options must be a list of strings")
        options = [str(opt) for opt in options_raw]
        if len(options) < 2:
            raise ExplainLevelsError(f"check{where} needs at least two options")
        if not isinstance(correct, str) or correct not in options:
            raise ExplainLevelsError(
                f"check{where} correct must be one of the options"
            )
        return {
            "kind": "choice",
            "question": question,
            "why": why,
            "options": options,
            "correct": correct,
        }

    if correct is None:
        return {
            "kind": "open",
            "question": question,
            "why": why,
            "correct": None,
        }

    if isinstance(correct, bool) or not isinstance(correct, (int, float)):
        raise ExplainLevelsError(
            f"check{where} correct must be an option string, a number, or None"
        )
    tolerance_raw = check.get("tolerance", DEFAULT_NUMERIC_TOLERANCE)
    if tolerance_raw is None:
        tolerance_raw = DEFAULT_NUMERIC_TOLERANCE
    try:
        tolerance = float(tolerance_raw)
    except (TypeError, ValueError) as exc:
        raise ExplainLevelsError(
            f"check{where} tolerance must be a number"
        ) from exc
    if tolerance < 0:
        raise ExplainLevelsError(f"check{where} tolerance must be >= 0")
    return {
        "kind": "numeric",
        "question": question,
        "why": why,
        "correct": float(correct),
        "tolerance": tolerance,
    }


def validate_levels(levels: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Validate and normalize a ladder's ``levels`` payload.

    :param levels: Author-facing level dicts (``name``, ``text``, optional
        ``check``).
    :returns: A new list of normalized level dicts.
    :raises ExplainLevelsError: If the ladder is empty, a level is missing
        ``name`` or ``text``, or two levels share a name.
    """
    if not isinstance(levels, Sequence) or isinstance(levels, (str, bytes)):
        raise ExplainLevelsError("levels must be a list of dicts")
    if len(levels) < 1:
        raise ExplainLevelsError("levels needs at least one entry")

    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, entry in enumerate(levels):
        if not isinstance(entry, Mapping):
            raise ExplainLevelsError(f"levels[{index}] must be a dict")
        name = str(entry.get("name") or "").strip()
        text = entry.get("text")
        if not name:
            raise ExplainLevelsError(f"levels[{index}] needs a name")
        if text is None or str(text).strip() == "":
            raise ExplainLevelsError(f"levels[{index}] ({name}) needs text")
        folded = name.casefold()
        if folded in seen:
            raise ExplainLevelsError(f"Duplicate level name {name!r}")
        seen.add(folded)
        item: dict[str, Any] = {"name": name, "text": str(text)}
        check = validate_check(entry.get("check"), level_name=name)
        if check is not None:
            item["check"] = check
        normalized.append(item)
    return normalized


def evaluate_response(check: Mapping[str, Any] | None, response: str) -> bool | None:
    """Return whether ``response`` is right, or ``None`` when there is no verdict.

    Open checks and unanswered closed checks return ``None``.

    :param check: A normalized check dict, or ``None``.
    :param response: The reader's committed answer.
    :returns: ``True`` / ``False`` for a closed check, else ``None``.
    """
    if not check:
        return None
    text = "" if response is None else str(response)
    if text == "":
        return None
    kind = check.get("kind")
    if kind == "open" or check.get("correct") is None:
        return None
    if kind == "numeric" or isinstance(check.get("correct"), (int, float)):
        try:
            value = float(text)
        except ValueError:
            return False
        tolerance = float(check.get("tolerance", DEFAULT_NUMERIC_TOLERANCE))
        return abs(value - float(check["correct"])) <= tolerance
    return text == check.get("correct")


class ExplainLevels(anywidget.AnyWidget):
    """Five-level explanation ladder with a per-level comprehension check.

    :param levels: Sequence of level dicts. See the module docstring.
    :param title: Heading shown above the level tabs.
    :param level: Open rung, as a 0-based index or a name. The synced
        trait is the canonical name. Defaults to ``"Undergrad"`` when that
        name exists, otherwise the first level.
    :param paper_ref: Paper section/figure/equation/algorithm anchor.
    """

    _esm = _ESM
    _css = _CSS
    title = traitlets.Unicode("").tag(sync=True)
    levels = traitlets.List(traitlets.Dict()).tag(sync=True)
    level = traitlets.Any("Undergrad").tag(sync=True)
    paper_ref = traitlets.Unicode("").tag(sync=True)
    responses = traitlets.List(traitlets.Unicode(), default_value=()).tag(sync=True)

    def __init__(
        self,
        levels: Sequence[Mapping[str, Any]],
        *,
        title: str = "",
        level: int | str | None = None,
        paper_ref: str = "",
        **kwargs: Any,
    ) -> None:
        normalized = validate_levels(levels)
        names = [str(item["name"]) for item in normalized]
        if level is None:
            chosen = "Undergrad" if "Undergrad" in names else names[0]
        else:
            chosen = normalize_level(level, names)
        for key in ("title", "levels", "level", "paper_ref", "responses"):
            kwargs.pop(key, None)
        super().__init__(
            title=str(title),
            levels=normalized,
            level=chosen,
            paper_ref=str(paper_ref or ""),
            responses=[""] * len(normalized),
            **kwargs,
        )

    @traitlets.validate("level")
    def _coerce_level(self, proposal: dict[str, Any]) -> str:
        names = [str(item.get("name", "")) for item in (self.levels or [])]
        names = [name for name in names if name]
        value = proposal["value"]
        if not names:
            if isinstance(value, int) and not isinstance(value, bool):
                return str(value)
            return str(value) if value is not None else ""
        return normalize_level(value, names)

    @traitlets.validate("levels")
    def _coerce_levels(self, proposal: dict[str, Any]) -> list[dict[str, Any]]:
        value = proposal["value"]
        if not value:
            return []
        if (
            isinstance(value, Sequence)
            and value
            and isinstance(value[0], Mapping)
            and "kind" in (value[0].get("check") or {})
        ):
            return list(value)
        return validate_levels(value)
