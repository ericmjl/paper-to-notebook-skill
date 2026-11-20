"""Tests for component-header parsing in ``scripts/validate_notebook.py``."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from validate_notebook import (  # noqa: E402
    banner_warnings,
    check_components,
    check_figure_walkthroughs,
    explanation_warnings,
    parse_component_header,
    quiz_length_warnings,
    quiz_sets,
    quotes_from_notebook,
)


HEADER = "# paper-to-notebook-skill-components:"


def test_parse_component_header_returns_none_when_absent() -> None:
    assert parse_component_header("import marimo\n") is None


def test_parse_component_header_splits_listed_ids() -> None:
    source = f"{HEADER} figure-walkthroughs, method-diagrams, final-quiz\n"
    assert parse_component_header(source) == [
        "figure-walkthroughs",
        "method-diagrams",
        "final-quiz",
    ]


def test_parse_component_header_empty_list() -> None:
    assert parse_component_header(f"{HEADER}\n") == []


def test_check_components_skips_undeclared_notebooks() -> None:
    source = "from paper_quiz import PaperQuiz\n"
    assert check_components(source) == []


def test_check_components_warns_on_missing_included_marker() -> None:
    source = f"{HEADER} figure-walkthroughs, method-diagrams, final-quiz\n"
    source += "FigureAnnotatorWidget\nPaperQuiz\n"
    warnings = check_components(source)
    assert len(warnings) == 1
    assert "method-diagrams" in warnings[0]
    assert "MermaidView" in warnings[0]


def test_check_components_does_not_require_skipped_components() -> None:
    source = f"{HEADER} final-quiz\nfrom paper_quiz import PaperQuiz\n"
    assert check_components(source) == []


def test_check_components_skipped_marker_absent_is_ok() -> None:
    source = f"{HEADER} final-quiz\nPaperQuiz\n"
    assert "FigureAnnotatorWidget" not in source
    assert "MermaidView" not in source
    assert check_components(source) == []


def test_check_components_warns_on_unknown_name() -> None:
    source = f"{HEADER} final-quiz, snacks\nPaperQuiz\n"
    warnings = check_components(source)
    assert len(warnings) == 1
    assert "snacks" in warnings[0]


def test_check_components_empty_header_requires_nothing() -> None:
    assert check_components(f"{HEADER}\n") == []


def test_missing_figure_annotator_without_comment_fails() -> None:
    warnings, errors = check_figure_walkthroughs("mo.md('hello')\n")
    assert warnings == []
    assert len(errors) == 1
    assert "FigureAnnotatorWidget" in errors[0]


def test_missing_figure_annotator_with_opt_out_warns() -> None:
    source = f"{HEADER} final-quiz\nPaperQuiz\n"
    warnings, errors = check_figure_walkthroughs(source)
    assert errors == []
    assert len(warnings) == 1
    assert "figure-walkthroughs" in warnings[0]


def test_empty_component_header_opts_out_of_figure_walkthroughs() -> None:
    warnings, errors = check_figure_walkthroughs(f"{HEADER}\n")
    assert errors == []
    assert len(warnings) == 1


def test_figure_annotator_present_is_silent() -> None:
    source = "fig = FigureAnnotatorWidget()\n"
    assert check_figure_walkthroughs(source) == ([], [])


def test_included_figure_walkthroughs_without_widget_fails() -> None:
    source = f"{HEADER} figure-walkthroughs, final-quiz\nPaperQuiz\n"
    warnings, errors = check_figure_walkthroughs(source)
    assert warnings == []
    assert len(errors) == 1
    assert "FigureAnnotatorWidget" in errors[0]


def test_parse_component_header_includes_explain_levels() -> None:
    source = (
        f"{HEADER} figure-walkthroughs, method-diagrams, "
        "final-quiz, explain-levels\n"
    )
    assert parse_component_header(source) == [
        "figure-walkthroughs",
        "method-diagrams",
        "final-quiz",
        "explain-levels",
    ]


def test_check_components_warns_on_missing_explain_levels() -> None:
    source = f"{HEADER} explain-levels, final-quiz\nPaperQuiz\n"
    warnings = check_components(source)
    assert len(warnings) == 1
    assert "explain-levels" in warnings[0]
    assert "ExplainLevels" in warnings[0]


def test_check_components_explain_levels_present() -> None:
    source = f"{HEADER} explain-levels\nfrom explain_levels import ExplainLevels\n"
    assert check_components(source) == []


def test_parse_component_header_includes_equations() -> None:
    source = (
        f"{HEADER} figure-walkthroughs, method-diagrams, "
        "final-quiz, explain-levels, equations\n"
    )
    assert parse_component_header(source) == [
        "figure-walkthroughs",
        "method-diagrams",
        "final-quiz",
        "explain-levels",
        "equations",
    ]


def test_check_components_warns_on_missing_tangle_latex() -> None:
    source = f"{HEADER} equations, final-quiz\nPaperQuiz\n"
    warnings = check_components(source)
    assert len(warnings) == 1
    assert "equations" in warnings[0]
    assert "TangleLatex" in warnings[0]


def test_check_components_equations_present() -> None:
    source = f"{HEADER} equations\nfrom wigglystuff import TangleLatex\n"
    assert check_components(source) == []


def test_check_components_equations_is_not_unknown() -> None:
    source = f"{HEADER} equations\nTangleLatex\n"
    warnings = check_components(source)
    assert warnings == []
    assert not any("unknown" in warning for warning in warnings)


def test_check_components_does_not_require_skipped_equations() -> None:
    source = f"{HEADER} final-quiz\nPaperQuiz\n"
    assert "TangleLatex" not in source
    assert check_components(source) == []


def test_explanation_warnings_silent_without_inline_levels() -> None:
    source = "from explain_levels import ExplainLevels\nExplainLevels\n"
    assert explanation_warnings(source) == []


def test_explanation_warnings_flag_short_inline_level() -> None:
    source = '''
levels = [{"name": "Child", "text": "Too short."}]
'''
    warnings = explanation_warnings(source)
    assert any("Child:" in item for item in warnings)


def test_quotes_from_notebook_skips_python_string_delimiters() -> None:
    source = '''
title = "this four word python string"
levels = [{"name": "Child", "text": "It needs an algorithm “both scalable to massive data”."}]
'''
    quotes = quotes_from_notebook(source)
    assert "this four word python string" not in quotes
    assert "both scalable to massive data" in quotes


def test_explanation_warnings_zero_quotes_in_inline_quiz() -> None:
    source = '''
questions = [{
    "question": "What did the method find on the main task?",
    "answer": "It matched the earlier tool on that task.",
    "explain": "See the results section of the paper.",
}]
'''
    warnings = explanation_warnings(source)
    assert any("no quotes found" in item for item in warnings)


def _quiz_question(answer: str, distractors: list[str], as_list: bool = False) -> str:
    if as_list:
        options = "[" + ", ".join(f'"{item}"' for item in distractors) + "]"
    else:
        options = "{"
        options += ", ".join(f'"{item}": "why it is wrong"' for item in distractors)
        options += "}"
    return (
        "{\n"
        '        "question": "What does the paper claim?",\n'
        f'        "answer": "{answer}",\n'
        '        "explain": "Section 2 of the paper.",\n'
        f'        "distractors": {options},\n'
        "    }"
    )


def _quiz_source(longest_correct: int, total: int = 5, as_list: bool = False) -> str:
    long_answer = "the correct answer with several extra clarifying words"
    short_answer = "short"
    long_distractors = [
        "a much longer wrong option that keeps going on",
        "another fairly long wrong option here",
        "tiny",
    ]
    short_distractors = ["short", "shorter", "tiny"]
    questions = []
    for index in range(total):
        if index < longest_correct:
            questions.append(_quiz_question(long_answer, short_distractors, as_list))
        else:
            questions.append(_quiz_question(short_answer, long_distractors, as_list))
    return "QUIZ = [\n" + ",\n".join(questions) + ",\n]\n"


def test_quiz_sets_finds_one_set_of_questions() -> None:
    sets = quiz_sets(_quiz_source(0))
    assert len(sets) == 1
    lineno, questions = sets[0]
    assert len(questions) == 5
    assert lineno == 1
    answer, distractors = questions[0]
    assert answer == "short"
    assert len(distractors) == 3


def test_quiz_length_warns_when_answer_always_longest() -> None:
    warnings = quiz_length_warnings(_quiz_source(5))
    assert len(warnings) == 1
    assert "line 1" in warnings[0]
    assert "longest" in warnings[0]


def test_quiz_length_silent_when_answer_varies() -> None:
    assert quiz_length_warnings(_quiz_source(2)) == []
    assert quiz_length_warnings(_quiz_source(0)) == []


def test_quiz_length_warns_one_bad_set_in_by_level_dict() -> None:
    bad_list = _quiz_source(5).split("=", 1)[1].strip()
    good_list = _quiz_source(0).split("=", 1)[1].strip()
    source = f"QUIZ_BY_LEVEL = {{'Child': {bad_list}, 'Teen': {good_list}}}\n"
    warnings = quiz_length_warnings(source)
    assert len(warnings) == 1


def test_quiz_length_ignores_sets_below_minimum_size() -> None:
    assert quiz_length_warnings(_quiz_source(2, total=2)) == []


def test_quiz_length_handles_list_distractors() -> None:
    warnings = quiz_length_warnings(_quiz_source(5, as_list=True))
    assert len(warnings) == 1
    assert quiz_length_warnings(_quiz_source(0, as_list=True)) == []


def test_banner_warns_when_marker_missing() -> None:
    source = f"{HEADER} final-quiz\nPaperQuiz\n"
    warnings = banner_warnings(source)
    assert len(warnings) == 1
    assert "data-p2n-banner" in warnings[0]


def test_banner_skips_notebooks_without_components_comment() -> None:
    assert banner_warnings("mo.md('hello')\n") == []


def test_banner_silent_when_marker_present() -> None:
    source = 'mo.Html("<div data-p2n-banner=\'1\'>Title</div>")\n'
    assert banner_warnings(source) == []
