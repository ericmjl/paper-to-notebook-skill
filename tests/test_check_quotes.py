"""Tests for paper-quote matching."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from check_quotes import (  # noqa: E402
    NO_QUOTES_WARNING,
    find_quotes,
    main,
    quotes_in_text,
    straight_quoted,
)


def test_inch_mark_does_not_break_straight_quote_pairing() -> None:
    text = (
        'The rod was 5" long. Later the text says '
        '"both scalable to massive data here".'
    )
    quotes = straight_quoted(text)
    assert quotes == ["both scalable to massive data here"]


def test_inch_mark_inside_a_quote_does_not_close_it() -> None:
    text = '"a sample about 5" long was used here"'
    assert straight_quoted(text) == ["a sample about 5" + '" long was used here']


def test_zero_quotes_warns_and_exits_zero(tmp_path: Path, capsys) -> None:
    paper = tmp_path / "paper.txt"
    paper.write_text("the full paper text\n", encoding="utf-8")
    ladder = tmp_path / "ladder.md"
    ladder.write_text("No quoted passages in this ladder.\n", encoding="utf-8")
    assert main(str(paper), str(ladder)) == 0
    captured = capsys.readouterr()
    assert NO_QUOTES_WARNING in captured.out
    assert str(ladder) in captured.out


def test_curly_quote_found_in_paper(tmp_path: Path, capsys) -> None:
    paper = tmp_path / "paper.txt"
    paper.write_text(
        "It is thus desirable to have an algorithm that is both scalable "
        "to massive data and able to cope with the diversity of data available.\n",
        encoding="utf-8",
    )
    ladder = tmp_path / "ladder.md"
    ladder.write_text(
        "It needs an algorithm “both scalable to massive data and able to cope "
        "with the diversity of data available”.\n",
        encoding="utf-8",
    )
    assert main(str(paper), str(ladder)) == 0
    captured = capsys.readouterr()
    assert "1 of 1 quotes found" in captured.out
    assert NO_QUOTES_WARNING not in captured.out


def test_missing_quote_exits_nonzero(tmp_path: Path, capsys) -> None:
    paper = tmp_path / "paper.txt"
    paper.write_text("unrelated paper text\n", encoding="utf-8")
    ladder = tmp_path / "ladder.md"
    ladder.write_text(
        "It needs an algorithm “both scalable to massive data and able to cope”.\n",
        encoding="utf-8",
    )
    assert main(str(paper), str(ladder)) == 1
    captured = capsys.readouterr()
    assert "NOT IN PAPER" in captured.out


def test_find_quotes_reads_markdown_path(tmp_path: Path) -> None:
    path = tmp_path / "ladder.md"
    path.write_text(
        'Straight “curly here” and "four word quote here".\n',
        encoding="utf-8",
    )
    assert find_quotes(str(path)) == ["curly here", "four word quote here"]


def test_quotes_in_text_json_mode_uses_curly_only() -> None:
    raw = '{"question": "What did it find “in the noise of a dataset”?"}'
    assert quotes_in_text(raw, json_mode=True) == ["in the noise of a dataset"]
