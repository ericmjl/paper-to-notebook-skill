# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Check that every quoted passage in a text appears word for word in the paper.

    uv run scripts/check_quotes.py paper.txt ladder.md
    uv run scripts/check_quotes.py paper.txt quiz.json

Quotes are text inside curly quotes “…” (any length), or inside straight quotes "…"
of at least four words. A quote mark right after a digit (``5"``) is an inch mark,
not a quote, so it does not start or end a pair. For a .json file, only curly
quotes inside its string values count. A quote with an ellipsis (… or ...) is
checked piece by piece. Whitespace, curly vs. straight apostrophes, dashes, and
LaTeX `$` are normalised before matching. Prints each quote that is not in the
paper and exits 1 if any are missing. A file with no quotes prints a warning
and still exits 0.
"""

import json
import re
import sys

CURLY = re.compile(r"“([^”]+)”")
NO_QUOTES_WARNING = "WARN: no quotes found"


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


def _is_inch_mark(text, index):
    return index > 0 and text[index - 1].isdigit()


def straight_quoted(text):
    """Return straight-quoted passages of at least four words.

    A ``"`` immediately after a digit is an inch mark and does not open or
    close a pair, so a stray ``5"`` cannot swallow the next quote.
    """
    quotes = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] != '"':
            i += 1
            continue
        if _is_inch_mark(text, i):
            i += 1
            continue
        j = i + 1
        while j < n and not (text[j] == '"' and not _is_inch_mark(text, j)):
            j += 1
        if j >= n:
            break
        q = text[i + 1 : j]
        if len(q.split()) >= 4:
            quotes.append(q)
        i = j + 1
    return quotes


def quotes_in_text(text, json_mode=False):
    if json_mode:
        return [q for s in strings(json.loads(text)) for q in CURLY.findall(s)]
    return CURLY.findall(text) + straight_quoted(text)


def find_quotes(path):
    text = open(path, encoding="utf-8").read()
    return quotes_in_text(text, json_mode=path.endswith(".json"))


def missing_quotes(paper_text, quotes):
    paper = normalise(paper_text)
    missing = []
    for q in quotes:
        pieces = [normalise(p).strip(" .,;:") for p in re.split(r"…|\.\.\.", q)]
        if not all(p in paper for p in pieces if p):
            missing.append(q)
    return missing


def main(paper_path, text_path):
    quotes = find_quotes(text_path)
    if not quotes:
        print(f"{NO_QUOTES_WARNING} in {text_path}")
        print(f"0 of 0 quotes found in {paper_path}")
        return 0
    missing = missing_quotes(open(paper_path, encoding="utf-8").read(), quotes)
    for q in missing:
        print(f"NOT IN PAPER: “{q}”")
    print(f"{len(quotes) - len(missing)} of {len(quotes)} quotes found in {paper_path}")
    return 1 if missing else 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1], sys.argv[2]))
