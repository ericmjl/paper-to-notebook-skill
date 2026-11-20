"""Tests for component-header parsing in ``scripts/validate_notebook.py``."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from validate_notebook import (  # noqa: E402
    check_components,
    check_figure_walkthroughs,
    parse_component_header,
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
