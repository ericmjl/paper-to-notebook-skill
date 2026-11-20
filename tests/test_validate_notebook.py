"""Tests for component-header parsing in ``scripts/validate_notebook.py``."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from validate_notebook import check_components, parse_component_header  # noqa: E402


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
