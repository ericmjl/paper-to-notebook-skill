"""Tests for mechanical processing-friendly-prose checks."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from check_prose import (  # noqa: E402
    LONG_PARAGRAPH_WORDS,
    LONG_SENTENCE_WORDS,
    extract_prose_spans,
    noun_stacks,
    prose_warnings,
)


def _md(body: str) -> str:
    return f'mo.md("""{body}""")\n'


def _checks(source: str) -> set[str]:
    return {warning.check for warning in prose_warnings(source)}


def test_long_sentence_warns() -> None:
    sentence = " ".join(["word"] * LONG_SENTENCE_WORDS) + "."
    warnings = prose_warnings(_md(sentence))
    assert any(item.check == "long_sentence" for item in warnings)


def test_short_sentence_is_silent() -> None:
    assert prose_warnings(_md("The yield falls (Fig. 2).")) == []


def test_long_paragraph_warns() -> None:
    paragraph = " ".join(["word"] * LONG_PARAGRAPH_WORDS) + "."
    warnings = prose_warnings(_md(paragraph))
    assert any(item.check == "long_paragraph" for item in warnings)


def test_ordinary_hyphenated_compound_plus_head_is_silent() -> None:
    assert noun_stacks("the cage-escape efficiency") == []
    assert noun_stacks("the excited-state reduction potential") == []
    assert noun_stacks("the continuous-light model") == []
    assert noun_stacks("the reader-patience budget") == []


def test_familiar_hyphenated_term_alone_is_not_a_stack() -> None:
    assert noun_stacks("an object-relative clause") == []


def test_title_case_name_list_is_not_a_stack() -> None:
    assert noun_stacks("Fina, Schmitz, Bertrams, and Kerzig.") == []


def test_three_unhyphenated_nouns_are_not_a_stack() -> None:
    assert noun_stacks("a fuzzy neighbour graph") == []


def test_four_unhyphenated_nouns_are_a_stack() -> None:
    stacks = noun_stacks("phenol cage escape efficiencies")
    assert stacks
    assert any(len(stack.split()) >= 4 for stack in stacks)


def test_five_unhyphenated_nouns_are_a_stack() -> None:
    stacks = noun_stacks("the unit test failure retry policy")
    assert any(len(stack.split()) >= 4 for stack in stacks)


def test_noun_stack_warns_in_markdown() -> None:
    source = _md("Skip the unit test failure retry policy today.")
    assert "noun_stack" in _checks(source)


def test_hyphenated_compound_stacked_onto_further_nouns() -> None:
    stacks = noun_stacks("the cage-escape quantum yield photoredox")
    assert stacks


def test_three_part_hyphenated_compound_is_a_stack() -> None:
    stacks = noun_stacks("the reader-patience-budget")
    assert stacks


def test_hyphenated_name_with_stopword_is_not_a_stack() -> None:
    assert noun_stacks("the paper-to-notebook-skill") == []


def test_third_person_verb_breaks_a_noun_run() -> None:
    assert noun_stacks("the free-radical quantum yield keeps falling") == []
    assert noun_stacks("the main text never prints lifetimes") == []


def test_comparative_does_not_pad_a_noun_run() -> None:
    assert noun_stacks("more quencher, smaller radical signal") == []


def test_inanimate_actor_from_skill_example() -> None:
    source = _md("The diagram assumes a sorted input.")
    assert "inanimate_actor" in _checks(source)


def test_swallow_verb_from_skill_example() -> None:
    source = _md("`is_file()` swallows that and returns False.")
    assert "inanimate_actor" in _checks(source)


def test_human_actor_does_not_warn() -> None:
    source = _md("The authors report the yield in Figure 1.")
    assert "inanimate_actor" not in _checks(source)


def test_denominal_from_skill_example() -> None:
    source = _md("Footnote it, then calendar the follow-up.")
    assert "denominal_verb" in _checks(source)


def test_delve_and_crucial_are_not_flagged() -> None:
    source = _md(
        "It is worth noting, in conclusion, that this is crucial. "
        "We delve into the result — see Fig. 1."
    )
    checks = _checks(source)
    assert "long_sentence" not in checks
    assert checks.isdisjoint({"filler", "ai_tell", "emdash"})


def test_extracts_mo_md() -> None:
    spans = extract_prose_spans(_md("The yield falls (Fig. 2)."))
    assert any("Fig. 2" in span.text for span in spans)


def test_extracts_explain_levels_text() -> None:
    source = '''
levels = [{
    "name": "Child",
    "text": "Each photo points at its few nearest neighbours.",
    "check": {
        "question": "Which is closest to what UMAP does?",
        "options": ["Build a graph, then flatten it.", "Fit one global line."],
        "why": "That is the mechanism (Sec. 3).",
    },
}]
'''
    spans = extract_prose_spans(source)
    texts = [span.text for span in spans]
    assert "Each photo points at its few nearest neighbours." in texts
    assert "Which is closest to what UMAP does?" in texts
    assert "That is the mechanism (Sec. 3)." in texts


def test_extracts_tangle_latex_notes_and_what_to_try() -> None:
    source = '''
mo.md("""**What to try (Eq. 1).** Drag μ: the bell slides.""")
TangleLatex(
    notes={
        "norm": "keeps the area under the curve at $1$",
        "center": "**μ**: where the bell is centered",
    },
    parameters={"mu": {"label": "μ"}},
)
'''
    spans = extract_prose_spans(source)
    texts = [span.text for span in spans]
    assert any("What to try" in text for text in texts)
    assert any("area under the curve" in text for text in texts)
    assert "μ" in texts


def test_extracts_figure_tour_html() -> None:
    source = '''
tour_steps = [{
    "title": "1. Light makes the singlet",
    "html": "<p>The catalyst starts at the ground state (Fig. 1).</p>",
}]
'''
    spans = extract_prose_spans(source)
    texts = [span.text for span in spans]
    assert "1. Light makes the singlet" in texts
    assert any("ground state" in text for text in texts)


def test_extracts_quiz_explain() -> None:
    source = '''
questions = [{
    "question": "What did the authors compare?",
    "explain": "Abstract and Conclusions. The authors call this less is more.",
    "distractors": {"A plausible wrong answer.": "The misconception it targets."},
}]
'''
    spans = extract_prose_spans(source)
    texts = [span.text for span in spans]
    assert "What did the authors compare?" in texts
    assert any("less is more" in text for text in texts)
    assert "A plausible wrong answer." in texts


def test_warnings_are_not_failures() -> None:
    source = _md("The diagram assumes a sorted input.")
    warnings = prose_warnings(source)
    assert warnings
    assert all(isinstance(item.detail, str) for item in warnings)
