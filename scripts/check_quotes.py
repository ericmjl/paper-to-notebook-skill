# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Check that every quoted passage in a text appears word for word in the paper.

    uv run scripts/check_quotes.py paper.txt ladder.md
    uv run scripts/check_quotes.py paper.txt quiz.json

Quotes are text inside curly quotes “…” (any length), or inside straight quotes "…"
of at least four words. For a .json file, only curly quotes inside its string values
count. A quote with an ellipsis (… or ...) is checked piece by piece. Whitespace,
curly vs. straight apostrophes, dashes, and LaTeX `$` are normalised before matching.
Prints each quote that is not in the paper and exits 1 if any are missing.
"""

import json
import re
import sys

CURLY = re.compile(r"“([^”]+)”")
STRAIGHT = re.compile(r"\"([^\"]+)\"")


def normalise(text):
    for a, b in (("’", "'"), ("‘", "'"), ("–", "-"), ("—", "-"), ("−", "-"), ("$", "")):
        text = text.replace(a, b)
    return re.sub(r"\s+", " ", text).strip().lower()


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for k, v in value.items():
            yield from strings(k)
            yield from strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from strings(v)


def find_quotes(path):
    text = open(path, encoding="utf-8").read()
    if path.endswith(".json"):
        return [q for s in strings(json.loads(text)) for q in CURLY.findall(s)]
    return CURLY.findall(text) + [q for q in STRAIGHT.findall(text) if len(q.split()) >= 4]


def main(paper_path, text_path):
    paper = normalise(open(paper_path, encoding="utf-8").read())
    quotes = find_quotes(text_path)
    missing = []
    for q in quotes:
        pieces = [normalise(p).strip(" .,;:") for p in re.split(r"…|\.\.\.", q)]
        if not all(p in paper for p in pieces if p):
            missing.append(q)
    for q in missing:
        print(f"NOT IN PAPER: “{q}”")
    print(f"{len(quotes) - len(missing)} of {len(quotes)} quotes found in {paper_path}")
    return 1 if missing else 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1], sys.argv[2]))
