"""Tests for explanation-ladder length and voice checks."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

from check_levels import (  # noqa: E402
    NO_LEVELS_MESSAGE,
    assess_level,
    issue_lines,
    levels_from_notebook,
    main,
)

CHILD = (
    "> **1 · Child.** Some collections have too many details for anyone to "
    "draw as a picture. This new way squashes them into a flat map that keeps "
    "close things close. Its maps looked about as good as the best older way, "
    "and it was faster. It also worked on much bigger collections than the "
    "older way could. But it can find shapes in messy dots, like seeing "
    "pictures in the stars.\n"
)


def test_no_levels_exits_nonzero(tmp_path: Path, capsys) -> None:
    path = tmp_path / "empty.md"
    path.write_text("# Notes\n\nNo ladder here.\n", encoding="utf-8")
    assert main(str(path)) == 1
    captured = capsys.readouterr()
    assert NO_LEVELS_MESSAGE in captured.out
    assert str(path) in captured.out


def test_umap_ladder_passes() -> None:
    ladder = ROOT / "resources" / "examples" / "ladder-umap.md"
    assert main(str(ladder)) == 0


def test_sentence_over_35_words_is_a_problem() -> None:
    body = " ".join(["word"] * 36) + "."
    _words, _n, longest, problems = assess_level("Expert", body)
    assert longest > 35
    assert any("over 35 words" in item for item in problems)


def test_one_paragraph_grad_student_is_a_problem() -> None:
    sentences = [
        "Neighbour-graph methods rest their choices on heuristics or on experiments in a neighbouring field.",
        "However, without theory, design choices can be argued only through empirical measures on the data.",
        "UMAP gives each point its own metric by normalising distances to its nearest neighbours in the graph.",
        "It merges local fuzzy simplicial sets by fuzzy union, then lays out the weighted graph by cross-entropy.",
        "The weights need no global normalisation, which removes the space trees that make t-SNE scale poorly.",
        "In accuracy UMAP matched t-SNE at small k and led at large k on COIL-20 against LargeVis.",
        "Single-core UMAP embedded MNIST in 87 s against 292 s for FIt-SNE on that laptop run.",
        "Its arguably better global structure owes much to the spectral initialisation used at the start.",
    ]
    body = " ".join(sentences)
    _words, n_sentences, _longest, problems = assess_level("Grad student", body)
    assert n_sentences == 8
    assert any("under 2 paragraphs" in item for item in problems)


def test_levels_from_notebook_reads_name_and_text() -> None:
    source = '''
levels = [
    {"name": "Child", "text": "One. Two. Three. Four. Five."},
    {"name": "Teen", "text": "Not a real Teen level, only a name check."},
]
'''
    found = levels_from_notebook(source)
    assert found == [
        ("Child", "One. Two. Three. Four. Five."),
        ("Teen", "Not a real Teen level, only a name check."),
    ]


def test_issue_lines_names_the_level() -> None:
    lines = issue_lines([("Child", "Too short.")])
    assert lines
    assert all(line.startswith("Child:") for line in lines)
