# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Check each explanation-ladder level against the length caps and the voice rule.

    uv run scripts/check_levels.py ladder.md

Levels are blockquotes starting "> **1 · Child.** " through "> **5 · Expert.** "
(resources/explanation-levels.md §7). Words are counted without locations in
parentheses and without math. Prints a table and exits 1 if any level falls outside its
sentence or word band, has too many paragraphs, or uses reporting-voice phrases.
"""

import re
import sys

CAPS = {  # level: (min, max sentences), max words per sentence, (min, max words), max paragraphs
    "Child": ((3, 5), 15, (None, None), 1),
    "Teen": ((5, 8), 25, (None, None), 1),
    "Undergrad": ((None, None), None, (200, 400), 4),
    "Grad student": ((6, 8), None, (150, 220), 1),
    "Expert": ((4, 6), None, (100, 180), 1),
}
REPORTING = re.compile(r"\b(the authors|the paper|this paper|the study|this study|this work|they (?:report|note|argue|find|found|show))\b", re.I)


def levels(text):
    for m in re.finditer(r"^> \*\*\d · ([^.]+)\.\*\* (.*?)(?=^> \*\*\d · |^(?!>)\S|\Z)", text, re.S | re.M):
        body = re.sub(r"^> ?", "", m.group(2), flags=re.M)
        yield m.group(1), body


def clean(body):
    body = re.sub(r"\$\$.*?\$\$|\$[^$]*\$", " ", body, flags=re.S)
    body = re.sub(r"\((?:[^()]*(?:§|\bTables?\b|\bFig(?:ure)?s?\b|\bEq(?:uation)?s?\b|\bAbstract\b|\bApp(?:endix)?\b|\bAlg(?:orithm)?s?\b|\bSec(?:tion)?s?\b|\bLemma\b|\bTheorem\b|\bDef(?:inition)?\b|\bHighlights\b|\bIntroduction\b|\bMethods\b|\bResults\b|\bDiscussion\b|\bConclusions?\b|\bSignificance\b|\bLimitations\b|\bSupplement\w*)[^()]*)\)", " ", body)
    return re.sub(r"\*\*|\*", "", body)


def main(path):
    failed = False
    print(f"{'level':<13} {'words':>5} {'sentences':>9} {'longest':>7}  problems")
    for name, body in levels(open(path, encoding="utf-8").read()):
        text = clean(body)
        sentences = [s for s in re.split(r"(?<=[.!?])[”\"]?\s+", text.strip()) if len(s.split()) > 1]
        words = len(text.split())
        longest = max((len(s.split()) for s in sentences), default=0)
        (min_s, max_s), max_len, (min_w, max_w), max_paras = CAPS.get(name, ((None, None), None, (None, None), None))
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
        if max_paras and paragraphs > max_paras:
            problems.append(f"over {max_paras} paragraph{'s' if max_paras > 1 else ''}")
        unquoted = re.sub(r"“[^”]*”", " ", body)  # a verbatim quote may say "this work"
        problems += [f"reporting voice: “{m}”" for m in sorted({m.group(0) for m in REPORTING.finditer(unquoted)})]
        failed |= bool(problems)
        print(f"{name:<13} {words:>5} {len(sentences):>9} {longest:>7}  {'; '.join(problems) or 'ok'}")
    return 1 if failed else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1]))
