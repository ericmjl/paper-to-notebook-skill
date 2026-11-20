# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Mechanical processing-friendly-prose warnings for notebook source.

Warnings only. Nothing here fails a run. The checks are the subset of
`.agents/skills/processing-friendly-prose` that can be tested without a
parser: very long sentences (a proxy for a subject far from its verb),
very long paragraphs (packing), clear noun stacks (four or more nouns,
or a hyphenated compound stacked onto further nouns), inanimate
subjects with person-verbs named in the skill, and the skill's ad-hoc
denominal examples. Filler lists that the skill does not name (for
example "delve" or em-dash counts) are out of scope.

Usage:
    uv run scripts/check_prose.py path/to/notebook.py
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from dataclasses import dataclass
from pathlib import Path

LONG_SENTENCE_WORDS = 40
LONG_PARAGRAPH_WORDS = 150
NOUN_STACK_MIN = 4

PROSE_KEYS = frozenset(
    {
        "html",
        "title",
        "label",
        "description",
        "explain",
        "question",
        "answer",
        "what",
        "params",
        "incoming",
        "caption",
        "why",
        "text",
        "notes",
    }
)
NESTED_PROSE_KEYS = frozenset({"notes", "distractors"})
LIST_PROSE_KEYS = frozenset({"options", "params"})

_STOPWORDS = frozenset(
    """
    a an the of to in for on with at by from as is are was were be been being
    that which who whom this these those and or but if then so not no nor it its
    they their them we our you your he she his her i my can could would should
    may might will shall do does did have has had than into over under between
    among about after before while when where how what why because also just
    only even still already such both each every all any some more most less
    few many much other another same own     via per vs versus using used use than
    there here than too very rather quite around
    above below further down up out off once
    one two three four five six seven eight nine ten
    first second third next last
    must never almost again either enough
    """.split()
)
_COMMON_VERBS = frozenset(
    """
    make makes made making show shows shown showing get gets got getting
    take takes taken taking give gives given giving see sees seen seeing
    go goes went going come comes coming know known knowing think thinks
    thought thinking find found finding tell told telling call called calling
    keep keeps kept keeping let help try tried trying start started starting look
    looks looking want wants wanting need needs needing seem seems seeming
    become became becoming leave left leaving put putting mean means meaning
    include includes including follow follows following report reports
    reported reporting cite cites cited citing write writes written writing
    read reads reading run runs running set sets setting add adds added adding
    say says said saying ask asks asked asking work works working feel feels
    feeling fall falls fell falling rise rises rose rising
    replace replaces replaced replacing measure measures measured measuring
    open opens opened opening change changes changed changing
    retell retells retelling
    print prints printed printing stand stands stood standing
    sit sits sat sitting drop drops dropped dropping
    slide slides sliding push pushes pushed pushing
    produce produces produced producing compare compares compared comparing
    reach reaches reached reaching born
    """.split()
)
_MODIFIERS = frozenset(
    """
    smaller larger higher lower highest lowest high low full well
    relative similar random main free total
    """.split()
)
_FAMILIAR_HYPHENS = frozenset(
    {"object-relative", "state-of-the-art", "end-to-end"}
)
_REF_TOKENS = frozenset({"fig", "eq", "eqn", "table", "tab", "sec", "section"})
_ABBREV = (
    "Fig",
    "Eq",
    "Eqn",
    "Table",
    "Tab",
    "Sec",
    "Section",
    "Dr",
    "Prof",
    "vs",
    "al",
    "e.g",
    "i.e",
)
_SENTENCE_SPLIT = re.compile(
    r"(?<=[.!?])\s+(?=[A-Z“\"'])"
)
_HTML_TAG = re.compile(r"<[^>]+>")
_MD_LINK = re.compile(r"\[([^\]]*)\]\([^)]+\)")
_INLINE_CODE = re.compile(r"`[^`]+`")
_MATH = re.compile(r"\$[^$]+\$")
_EMPHASIS = re.compile(r"[*_#>]")
_INANIMATE_ACTOR = re.compile(
    r"\b(?:the\s+)?(?:diagram|paper|result|results|script|file|"
    r"notebook|widget|figure|algorithm|method|model|tool|check|"
    r"function|class|validator|pipeline|flowchart|tour|quiz|ladder)\s+"
    r"(?:assumes?|wants?|thinks?|decides?|hopes?|believes?|"
    r"swallows?|bites?|eats?)\b",
    re.IGNORECASE,
)
_BODY_VERB = re.compile(
    r"\b(?:swallows?|swallowing|bites?|biting|eats?|eating)\b",
    re.IGNORECASE,
)
_DENOMINAL = re.compile(
    r"\b(?:footnote|calendar)\s+(?:it|the|this|that)\b",
    re.IGNORECASE,
)
_CODE_FENCE = re.compile(r"```.*?```", re.DOTALL)


@dataclass(frozen=True)
class ProseSpan:
    """A reader-facing string taken from notebook source.

    :param kind: ``markdown`` or ``widget``
    :param lineno: 1-based line of the string in the source
    :param text: raw extracted text
    """

    kind: str
    lineno: int
    text: str


@dataclass(frozen=True)
class ProseWarning:
    """One mechanical prose warning.

    :param check: machine name of the check
    :param lineno: 1-based line of the span
    :param kind: span kind
    :param detail: short description
    :param excerpt: clipped text that tripped the check
    """

    check: str
    lineno: int
    kind: str
    detail: str
    excerpt: str


def _string_from_ast(node: ast.AST) -> str | None:
    """Return a string constant or the literal parts of an f-string.

    :param node: AST node that may hold prose
    :return: extracted text, or None when the node is not a string
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        parts: list[str] = []
        for value in node.values:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                parts.append(value.value)
            else:
                parts.append(" ")
        return "".join(parts)
    return None


def _collect_from_value(node: ast.AST, found: list[ProseSpan]) -> None:
    """Append prose strings nested under ``node``.

    :param node: dict value, list, or string
    :param found: list to extend
    """
    text = _string_from_ast(node)
    if text is not None:
        found.append(ProseSpan("widget", getattr(node, "lineno", 1), text))
        return
    if isinstance(node, ast.List):
        for elt in node.elts:
            _collect_from_value(elt, found)
    elif isinstance(node, ast.Dict):
        for key, value in zip(node.keys, node.values, strict=False):
            key_text = _string_from_ast(key) if key is not None else None
            if key_text is not None:
                found.append(
                    ProseSpan("widget", getattr(key, "lineno", 1), key_text)
                )
            if value is not None:
                _collect_from_value(value, found)


def extract_prose_spans(source: str) -> list[ProseSpan]:
    """Return reader-facing strings from notebook source.

    Collects ``mo.md`` arguments, widget dict fields (ExplainLevels
    ``text``, TangleLatex ``notes`` and ``label``, figure-tour ``html``,
    quiz ``explain``, flowchart ``what``), ``options`` lists, and string
    arguments to ``plain_feedback``.

    :param source: notebook source text
    :return: spans in source order
    """
    tree = ast.parse(source)
    found: list[ProseSpan] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if node.args and isinstance(func, ast.Attribute) and func.attr == "md":
                text = _string_from_ast(node.args[0])
                if text is not None:
                    found.append(ProseSpan("markdown", node.lineno, text))
            elif node.args and isinstance(func, ast.Name) and func.id == "plain_feedback":
                for arg in node.args[1:]:
                    text = _string_from_ast(arg)
                    if text is not None:
                        found.append(ProseSpan("widget", arg.lineno, text))
            for keyword in node.keywords:
                if keyword.arg is None or keyword.value is None:
                    continue
                if (
                    keyword.arg in NESTED_PROSE_KEYS
                    or keyword.arg in LIST_PROSE_KEYS
                    or keyword.arg in PROSE_KEYS
                ):
                    _collect_from_value(keyword.value, found)
        elif isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values, strict=False):
                if key is None or value is None:
                    continue
                key_text = _string_from_ast(key)
                if key_text in NESTED_PROSE_KEYS:
                    _collect_from_value(value, found)
                    continue
                if key_text not in PROSE_KEYS:
                    continue
                _collect_from_value(value, found)
    found.sort(key=lambda span: span.lineno)
    return found


def normalize_prose(text: str) -> str:
    """Strip markup so word counts and stacks see ordinary words.

    :param text: raw markdown, HTML, or widget copy
    :return: plain text
    """
    cleaned = _CODE_FENCE.sub(" ", text)
    cleaned = _HTML_TAG.sub(" ", cleaned)
    cleaned = _MD_LINK.sub(r"\1", cleaned)
    cleaned = _INLINE_CODE.sub(" ", cleaned)
    cleaned = _MATH.sub(" ", cleaned)
    cleaned = _EMPHASIS.sub(" ", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


def _protect_abbreviations(text: str) -> str:
    """Replace ``Fig.``-style dots so sentence splits keep the abbreviation.

    :param text: normalized prose
    :return: text with abbreviation dots swapped for a placeholder
    """
    protected = text
    for abbrev in _ABBREV:
        protected = re.sub(
            rf"\b{re.escape(abbrev)}\.",
            abbrev + "\uff0e",
            protected,
        )
    return protected


def split_sentences(text: str) -> list[str]:
    """Split ``text`` into sentences, keeping ``Fig. 1`` together.

    :param text: normalized prose
    :return: sentence strings
    """
    if not text.strip():
        return []
    protected = _protect_abbreviations(text)
    parts = _SENTENCE_SPLIT.split(protected)
    return [part.replace("\uff0e", ".").strip() for part in parts if part.strip()]


def split_paragraphs(text: str) -> list[str]:
    """Split raw text on blank lines, dropping tables and headings.

    :param text: raw markdown or HTML
    :return: paragraph strings
    """
    chunks: list[str] = []
    for raw in re.split(r"\n\s*\n", text):
        lines = [
            line
            for line in raw.splitlines()
            if line.strip()
            and not line.strip().startswith("|")
            and not line.strip().startswith("#")
        ]
        if lines:
            chunks.append("\n".join(lines))
    return chunks


def word_count(text: str) -> int:
    """Count whitespace-separated tokens in normalized prose.

    :param text: prose, already normalized or not
    :return: number of words
    """
    cleaned = normalize_prose(text)
    if not cleaned:
        return 0
    return len(cleaned.split())


def _looks_like_verb(part: str) -> bool:
    """Return whether ``part`` is a listed verb or a regular 3sg form.

    :param part: lowercase token
    :return: True when the token should not count as a noun
    """
    if part in _COMMON_VERBS:
        return True
    if part.endswith("es") and part[:-2] in _COMMON_VERBS:
        return True
    if part.endswith("s") and part[:-1] in _COMMON_VERBS:
        return True
    return False


def _is_noun_part(part: str) -> bool:
    """Return whether ``part`` looks like a noun rather than glue.

    :param part: lowercase token or hyphen piece
    :return: True when the piece should count in a noun run
    """
    return not (
        len(part) < 3
        or part in _STOPWORDS
        or part in _MODIFIERS
        or _looks_like_verb(part)
        or part in _REF_TOKENS
        or part.endswith("ly")
    )


def _noun_units(token: str) -> list[str]:
    """Split a token into noun units.

    A two-part hyphenated compound (``cage-escape``, ``excited-state``)
    counts as one unit: that is ordinary scientific naming, not a stack.
    Three or more hyphenated noun parts are a stacked compound, so each
    part counts. Title-case runs (author names, headings) are ignored.

    :param token: a whitespace token, punctuation stripped
    :return: noun units inside the token, or empty if it is not a noun
    """
    stripped = token.strip(".,;:!?()[]{}\"'“”‘’")
    if not stripped or any(ch.isdigit() for ch in stripped):
        return []
    if stripped.isupper() and len(stripped) <= 5:
        return []
    if stripped[0].isupper() and not stripped.isupper():
        return []
    if stripped.endswith(("ed", "ing")) and "-" not in stripped:
        return []
    lower = stripped.lower()
    if lower in _FAMILIAR_HYPHENS:
        return [lower]
    parts = stripped.split("-")
    lower_parts = [part.lower() for part in parts if part]
    if not lower_parts:
        return []
    if len(lower_parts) > 1 and any(part in _STOPWORDS for part in lower_parts):
        return [lower]
    noun_parts = [part for part in lower_parts if _is_noun_part(part)]
    if not noun_parts:
        return []
    if len(lower_parts) == 2:
        return [lower]
    return noun_parts


def noun_stacks(text: str) -> list[str]:
    """Return clear noun stacks: four or more nouns, or a stacked hyphen.

    Ordinary two-part compounds plus a head noun (``cage-escape
    efficiency``, ``excited-state reduction potential``) do not warn.
    A hyphenated compound stacked onto enough further nouns to make four
    units does, as does a single token with three or more noun parts
    (``reader-patience-budget``).

    :param text: normalized prose
    :return: joined stacks
    """
    cleaned = re.sub(r"\([^)]*\)", " ", text)
    tokens = normalize_prose(cleaned).split()
    stacks: list[str] = []
    current: list[str] = []
    stacked_hyphen = False
    for token in tokens:
        units = _noun_units(token)
        if units:
            current.extend(units)
            stripped = token.strip(".,;:!?()[]{}\"'“”‘’")
            if "-" in stripped and len(units) >= 3:
                stacked_hyphen = True
            continue
        if _stack_hits_threshold(current, stacked_hyphen):
            stacks.append(" ".join(current))
        current = []
        stacked_hyphen = False
    if _stack_hits_threshold(current, stacked_hyphen):
        stacks.append(" ".join(current))
    return stacks


def _stack_hits_threshold(units: list[str], stacked_hyphen: bool) -> bool:
    """Return whether a noun run is a clear stack.

    :param units: consecutive noun units
    :param stacked_hyphen: whether a 3+ part hyphenated compound contributed
    :return: True when the run should warn
    """
    if stacked_hyphen:
        return True
    return len(units) >= NOUN_STACK_MIN


def _clip(text: str, limit: int = 80) -> str:
    """Return a one-line excerpt.

    :param text: source snippet
    :param limit: max characters
    :return: clipped string
    """
    flat = re.sub(r"\s+", " ", text).strip()
    if len(flat) <= limit:
        return flat
    return flat[: limit - 1] + "…"


def check_span(span: ProseSpan) -> list[ProseWarning]:
    """Run mechanical checks on one span.

    :param span: extracted prose
    :return: warnings for that span
    """
    warnings: list[ProseWarning] = []
    raw = span.text
    for paragraph in split_paragraphs(raw):
        words = word_count(paragraph)
        if words >= LONG_PARAGRAPH_WORDS:
            warnings.append(
                ProseWarning(
                    "long_paragraph",
                    span.lineno,
                    span.kind,
                    f"{words} words (threshold {LONG_PARAGRAPH_WORDS})",
                    _clip(paragraph),
                )
            )
        normalized = normalize_prose(paragraph)
        for sentence in split_sentences(normalized):
            n_words = word_count(sentence)
            if n_words >= LONG_SENTENCE_WORDS:
                warnings.append(
                    ProseWarning(
                        "long_sentence",
                        span.lineno,
                        span.kind,
                        f"{n_words} words (threshold {LONG_SENTENCE_WORDS})",
                        _clip(sentence),
                    )
                )
            for stack in noun_stacks(sentence):
                warnings.append(
                    ProseWarning(
                        "noun_stack",
                        span.lineno,
                        span.kind,
                        f"noun stack of {len(stack.split())}: {stack}",
                        _clip(sentence),
                    )
                )
            if _INANIMATE_ACTOR.search(sentence) or _BODY_VERB.search(sentence):
                warnings.append(
                    ProseWarning(
                        "inanimate_actor",
                        span.lineno,
                        span.kind,
                        "inanimate subject with a person-verb, or eat/bite/swallow",
                        _clip(sentence),
                    )
                )
            if _DENOMINAL.search(sentence):
                warnings.append(
                    ProseWarning(
                        "denominal_verb",
                        span.lineno,
                        span.kind,
                        "ad-hoc denominal verb (footnote/calendar it)",
                        _clip(sentence),
                    )
                )
    return warnings


def prose_warnings(source: str) -> list[ProseWarning]:
    """Return mechanical prose warnings for notebook source.

    :param source: notebook source text
    :return: warnings in source order
    """
    found: list[ProseWarning] = []
    for span in extract_prose_spans(source):
        found.extend(check_span(span))
    return found


def format_warning(warning: ProseWarning) -> str:
    """Format one warning for stdout.

    :param warning: a mechanical prose warning
    :return: one line
    """
    return (
        f"line {warning.lineno} ({warning.kind}): {warning.check}: "
        f"{warning.detail}: {warning.excerpt}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("notebook", type=Path)
    args = parser.parse_args()
    nb: Path = args.notebook
    if not nb.is_file():
        print(f"FAIL: {nb} not found")
        return 1
    source = nb.read_text()
    try:
        ast.parse(source, filename=str(nb))
    except SyntaxError as error:
        print(f"FAIL: {error}")
        return 1
    warnings = prose_warnings(source)
    if warnings:
        print("[prose]")
        for warning in warnings:
            print(f"WARN: {format_warning(warning)}")
        noun = "warning" if len(warnings) == 1 else "warnings"
        print(f"OK: {nb} ({len(warnings)} prose {noun}; not a failure)")
    else:
        print(f"OK: {nb}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
