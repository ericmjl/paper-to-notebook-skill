# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Check each explanation-ladder level against the length caps and the voice rule.

    uv run scripts/check_levels.py ladder.md

Levels are blockquotes starting "> **1 · Child.** " through "> **5 · Expert.** "
(resources/explanation-levels.md §7). Words are counted without locations in
parentheses and without math. Prints a table and exits 1 if any level falls outside its
sentence or word band, has too many or too few paragraphs, a sentence over the
35-word cap (15 at Child, 25 at Teen), or uses reporting-voice phrases. Exits 1
with a clear message when the file has no levels.
"""

from __future__ import annotations

import ast
import re
import sys

CAPS = {  # level: (min, max sentences), max words per sentence, (min, max words), (min, max paragraphs)
    "Child": ((3, 5), 15, (None, None), (1, 1)),
    "Teen": ((5, 8), 25, (None, None), (1, 1)),
    "Undergrad": ((None, None), 35, (200, 400), (2, 4)),
    "Grad student": ((6, 8), 35, (150, 220), (2, 3)),
    "Expert": ((4, 8), 35, (100, 180), (2, 3)),
}
REPORTING = re.compile(r"\b(the authors|the paper|this paper|the study|this study|this work|they (?:report|note|argue|find|found|show))\b", re.I)
NO_LEVELS_MESSAGE = "ERROR: no explanation levels found"


def levels(text):
    for m in re.finditer(r"^> \*\*\d · ([^.]+)\.\*\* (.*?)(?=^> \*\*\d · |^(?!>)\S|\Z)", text, re.S | re.M):
        body = re.sub(r"^> ?", "", m.group(2), flags=re.M)
        yield m.group(1), body


def clean(body):
    body = re.sub(r"\$\$.*?\$\$|\$[^$]*\$", " ", body, flags=re.S)
    body = re.sub(r"\((?:[^()]*(?:§|\bTables?\b|\bFig(?:ure)?s?\b|\bEq(?:uation)?s?\b|\bAbstract\b|\bApp(?:endix)?\b|\bAlg(?:orithm)?s?\b|\bSec(?:tion)?s?\b|\bLemma\b|\bTheorem\b|\bDef(?:inition)?\b|\bHighlights\b|\bIntroduction\b|\bMethods\b|\bResults\b|\bDiscussion\b|\bConclusions?\b|\bSignificance\b|\bLimitations\b|\bSupplement\w*)[^()]*)\)", " ", body)
    return re.sub(r"\*\*|\*", "", body)


def _string_from_ast(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        parts = []
        for value in node.values:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                parts.append(value.value)
            else:
                parts.append(" ")
        return "".join(parts)
    return None


def levels_from_notebook(source):
    """Return ``(name, text)`` pairs from ExplainLevels-style dicts in ``source``."""
    tree = ast.parse(source)
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        fields = {}
        for key_node, value_node in zip(node.keys, node.values, strict=False):
            if key_node is None or value_node is None:
                continue
            key = _string_from_ast(key_node)
            value = _string_from_ast(value_node)
            if key is not None and value is not None:
                fields[key] = value
        name = fields.get("name")
        text = fields.get("text")
        if name in CAPS and text is not None:
            found.append((name, text))
    return found


def assess_level(name, body):
    """Return ``(words, n_sentences, longest, problems)`` for one level."""
    text = clean(body)
    sentences = [s for s in re.split(r"(?<=[.!?])[”\"]?\s+", text.strip()) if len(s.split()) > 1]
    words = len(text.split())
    longest = max((len(s.split()) for s in sentences), default=0)
    (min_s, max_s), max_len, (min_w, max_w), (min_p, max_p) = CAPS.get(
        name, ((None, None), None, (None, None), (None, None))
    )
    joined = re.sub(r"\n\s*\n\s*\$\$.*?\$\$\s*\n\s*\n", " ", body.strip(), flags=re.S)  # a displayed equation doesn't split a paragraph
    paragraphs = len([p for p in re.split(r"\n\s*\n", joined) if p.strip() and not p.strip().startswith("$$")])
    problems = []
    if max_s and len(sentences) > max_s:
        problems.append(f"over {max_s} sentences")
    if min_s and len(sentences) < min_s:
        problems.append(f"under {min_s} sentences")
    if max_len and longest > max_len:
        problems.append(f"a sentence over {max_len} words")
    if max_w and words > max_w:
        problems.append(f"over {max_w} words")
    if min_w and words < min_w:
        problems.append(f"under {min_w} words")
    if max_p and paragraphs > max_p:
        problems.append(f"over {max_p} paragraph{'s' if max_p > 1 else ''}")
    if min_p and paragraphs < min_p:
        problems.append(f"under {min_p} paragraph{'s' if min_p > 1 else ''}")
    unquoted = re.sub(r"“[^”]*”", " ", body)  # a verbatim quote may say "this work"
    problems += [f"reporting voice: “{m}”" for m in sorted({m.group(0) for m in REPORTING.finditer(unquoted)})]
    return words, len(sentences), longest, problems


def issue_lines(named_bodies):
    """Return human-readable issue lines for notebook or markdown levels."""
    lines = []
    for name, body in named_bodies:
        _words, _n, _longest, problems = assess_level(name, body)
        for problem in problems:
            lines.append(f"{name}: {problem}")
    return lines


def main(path):
    named = list(levels(open(path, encoding="utf-8").read()))
    if not named:
        print(f"{NO_LEVELS_MESSAGE} in {path}")
        return 1
    failed = False
    print(f"{'level':<13} {'words':>5} {'sentences':>9} {'longest':>7}  problems")
    for name, body in named:
        words, n_sentences, longest, problems = assess_level(name, body)
        failed |= bool(problems)
        print(f"{name:<13} {words:>5} {n_sentences:>9} {longest:>7}  {'; '.join(problems) or 'ok'}")
    return 1 if failed else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1]))
