"""Tests for the ExplainLevels trait schema and validation helpers."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

ASSETS = Path(__file__).resolve().parents[1] / "assets"
sys.path.insert(0, str(ASSETS))

from explain_levels import (  # noqa: E402
    DEFAULT_LEVEL_NAMES,
    ExplainLevels,
    ExplainLevelsError,
    assert_paper_ref,
    evaluate_response,
    normalize_level,
    resolve_level,
    validate_check,
    validate_levels,
)


def _choice_check(**overrides: Any) -> dict[str, Any]:
    check = {
        "question": "Which picture fits?",
        "options": ["shrink evenly", "link then pull", "sort into teams"],
        "correct": "link then pull",
        "why": "Neighbour links, then a layout (Sec. 3).",
    }
    check.update(overrides)
    return check


def _numeric_check(**overrides: Any) -> dict[str, Any]:
    check = {
        "question": "What is B_ij?",
        "correct": 0.53,
        "tolerance": 0.02,
        "why": r"$e^{-1} + 0.25 - e^{-1}\times 0.25 \approx 0.53$ (Sec. 3.1).",
    }
    check.update(overrides)
    return check


def _open_check(**overrides: Any) -> dict[str, Any]:
    check = {
        "question": "What experiment would separate the objective from init?",
        "correct": None,
        "why": "Cross objective × initialisation (Sec. 6).",
    }
    check.update(overrides)
    return check


def _five_levels() -> list[dict[str, Any]]:
    texts = [
        "Crowd of photos; point at neighbours; pull linked pairs close.",
        "Each one-way link has a strength from 0 to 1.",
        "Fuzzy memberships, t-conorm union, then cross-entropy layout.",
        "Local metrics from the uniformity axiom; compare with t-SNE.",
        "kNN-graph plus a derivation that fixes each choice.",
    ]
    checks = [
        _choice_check(),
        _choice_check(
            question="If C→A drops to 0, pair strength is?",
            options=["0", "0.5", "0.7"],
            correct="0.5",
            why="0.5 + 0 − 0 = 0.5 (Sec. 3.1).",
        ),
        _numeric_check(),
        _choice_check(
            question="Two groups, same shape, tenfold spacing. In the embedding?",
            options=["group 2 is ten times wider", "similar spread", "group 2 dropped"],
            correct="similar spread",
            why="rho_i and sigma_i cancel a uniform scale (Sec. 6).",
        ),
        _open_check(),
    ]
    return [
        {"name": name, "text": text, "check": check}
        for name, text, check in zip(DEFAULT_LEVEL_NAMES, texts, checks, strict=True)
    ]


def test_default_level_names_are_the_five_shorthands() -> None:
    assert DEFAULT_LEVEL_NAMES == (
        "Child",
        "Teen",
        "Undergrad",
        "Grad student",
        "Expert",
    )


def test_resolve_level_accepts_index_and_name() -> None:
    names = list(DEFAULT_LEVEL_NAMES)
    assert resolve_level(0, names) == 0
    assert resolve_level("Teen", names) == 1
    assert resolve_level("grad student", names) == 3


def test_resolve_level_rejects_out_of_range_and_unknown_name() -> None:
    names = list(DEFAULT_LEVEL_NAMES)
    with pytest.raises(ExplainLevelsError, match="index"):
        resolve_level(-1, names)
    with pytest.raises(ExplainLevelsError, match="index"):
        resolve_level(5, names)
    with pytest.raises(ExplainLevelsError, match="Unknown level"):
        resolve_level("wizard", names)


def test_normalize_level_returns_canonical_name() -> None:
    names = list(DEFAULT_LEVEL_NAMES)
    assert normalize_level(2, names) == "Undergrad"
    assert normalize_level("expert", names) == "Expert"


def test_validate_check_choice_records_kind_and_options() -> None:
    check = validate_check(_choice_check())
    assert check is not None
    assert check["kind"] == "choice"
    assert check["correct"] == "link then pull"
    assert check["options"][1] == "link then pull"


def test_validate_check_rejects_choice_whose_correct_is_not_an_option() -> None:
    with pytest.raises(ExplainLevelsError, match="correct"):
        validate_check(_choice_check(correct="not an option"))


def test_validate_check_numeric_records_kind_and_default_tolerance() -> None:
    check = validate_check(_numeric_check(tolerance=None))
    del check  # replaced below; ensure omitted tolerance is valid
    payload = {
        "question": "What is B_ij?",
        "correct": 0.53,
        "why": "Sec. 3.1",
    }
    check = validate_check(payload)
    assert check is not None
    assert check["kind"] == "numeric"
    assert check["correct"] == pytest.approx(0.53)
    assert check["tolerance"] == pytest.approx(0.01)


def test_validate_check_integer_correct_is_numeric() -> None:
    check = validate_check(
        {"question": "Ratio?", "correct": 15, "tolerance": 0.5, "why": "0.42/0.028"}
    )
    assert check is not None
    assert check["kind"] == "numeric"
    assert check["correct"] == pytest.approx(15.0)


def test_validate_check_open_when_correct_is_none() -> None:
    check = validate_check(_open_check())
    assert check is not None
    assert check["kind"] == "open"
    assert check["correct"] is None


def test_validate_check_requires_question_and_why() -> None:
    with pytest.raises(ExplainLevelsError, match="question"):
        validate_check({"why": "because", "correct": None})
    with pytest.raises(ExplainLevelsError, match="why"):
        validate_check({"question": "Why?", "correct": None})


def test_validate_check_none_is_allowed() -> None:
    assert validate_check(None) is None


def test_validate_levels_requires_name_and_text() -> None:
    with pytest.raises(ExplainLevelsError, match="name"):
        validate_levels([{"text": "hello"}])
    with pytest.raises(ExplainLevelsError, match="text"):
        validate_levels([{"name": "Child"}])
    with pytest.raises(ExplainLevelsError, match="at least one"):
        validate_levels([])


def test_validate_levels_rejects_duplicate_names() -> None:
    with pytest.raises(ExplainLevelsError, match="Duplicate"):
        validate_levels(
            [
                {"name": "Child", "text": "one"},
                {"name": "Child", "text": "two"},
            ]
        )


def test_validate_levels_normalizes_checks() -> None:
    levels = validate_levels(_five_levels())
    assert [lv["name"] for lv in levels] == list(DEFAULT_LEVEL_NAMES)
    assert levels[0]["check"]["kind"] == "choice"
    assert levels[2]["check"]["kind"] == "numeric"
    assert levels[4]["check"]["kind"] == "open"


def test_evaluate_response_choice_and_numeric_and_open() -> None:
    choice = validate_check(_choice_check())
    numeric = validate_check(_numeric_check())
    open_check = validate_check(_open_check())
    assert evaluate_response(choice, "link then pull") is True
    assert evaluate_response(choice, "shrink evenly") is False
    assert evaluate_response(choice, "") is None
    assert evaluate_response(numeric, "0.53") is True
    assert evaluate_response(numeric, "0.52") is True
    assert evaluate_response(numeric, "0.40") is False
    assert evaluate_response(numeric, "nope") is False
    assert evaluate_response(open_check, "cross the two factors") is None
    assert evaluate_response(None, "anything") is None


def test_assert_paper_ref_requires_a_nonempty_anchor() -> None:
    assert assert_paper_ref("Secs. 2–3, Algs. 1–5") == "Secs. 2–3, Algs. 1–5"
    with pytest.raises(ExplainLevelsError, match="paper_ref"):
        assert_paper_ref("")
    with pytest.raises(ExplainLevelsError, match="paper_ref"):
        assert_paper_ref("   ")


def test_widget_synced_traits() -> None:
    widget = ExplainLevels(
        title="UMAP's two-phase mechanism",
        levels=_five_levels(),
        level="Teen",
        paper_ref="Secs. 2–3, Algs. 1–5",
    )
    for name in ("title", "levels", "level", "paper_ref"):
        trait = widget.traits()[name]
        assert trait.metadata.get("sync") is True
    assert widget.title == "UMAP's two-phase mechanism"
    assert widget.level == "Teen"
    assert widget.paper_ref == "Secs. 2–3, Algs. 1–5"
    assert len(widget.levels) == 5
    assert widget.levels[2]["check"]["kind"] == "numeric"


def test_widget_level_accepts_int_or_name_and_canonicalizes() -> None:
    widget = ExplainLevels(levels=_five_levels(), level=0)
    assert widget.level == "Child"
    widget.level = 3
    assert widget.level == "Grad student"
    widget.level = "Expert"
    assert widget.level == "Expert"
    widget.level = "undergrad"
    assert widget.level == "Undergrad"


def test_widget_defaults_level_to_undergrad_when_present() -> None:
    widget = ExplainLevels(levels=_five_levels())
    assert widget.level == "Undergrad"


def test_widget_paper_ref_is_optional_on_the_widget() -> None:
    widget = ExplainLevels(levels=_five_levels()[:1])
    assert widget.paper_ref == ""


def test_widget_rejects_invalid_level() -> None:
    with pytest.raises(ExplainLevelsError):
        ExplainLevels(levels=_five_levels(), level="wizard")


def test_widget_has_inline_esm_and_css() -> None:
    widget = ExplainLevels(levels=_five_levels()[:1], title="t")
    assert isinstance(widget._esm, str) and "function render" in widget._esm
    assert isinstance(widget._css, str) and ".el-root" in widget._css
    assert "ArrowLeft" in widget._esm
    assert "save_changes" in widget._esm
