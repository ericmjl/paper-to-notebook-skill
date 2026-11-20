"""Tests for paper-figure and paper-anchor scans in ``validate_notebook``."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from validate_notebook import (  # noqa: E402
    UNANCHORED_MARKDOWN_WARN_FRACTION,
    has_paper_figure_images,
    markdown_texts,
    paper_grounding_warnings,
    split_math_sub_warnings,
)


def test_has_paper_figure_images_detects_webp_path() -> None:
    source = 'annotator.load_image_from_path(Path("figures/fig1.webp"))\n'
    assert has_paper_figure_images(source) is True


def test_has_paper_figure_images_detects_markdown_image() -> None:
    source = 'mo.md("![Fig. 1](figures/fig1.png)")\n'
    assert has_paper_figure_images(source) is True


def test_has_paper_figure_images_false_for_plotly_only() -> None:
    source = 'fig = go.Figure()\nmo.md("A sketch of made-up data")\n'
    assert has_paper_figure_images(source) is False


def test_markdown_texts_collects_mo_md_strings() -> None:
    source = '''
mo.md("The yield falls (Fig. 2).")
mo.md(r"""
## Why this paper

See Section 2 for the claim.
""")
'''
    texts = markdown_texts(source)
    assert len(texts) == 2
    assert "Fig. 2" in texts[0]
    assert "Section 2" in texts[1]


def _long(text: str) -> str:
    """Pad markdown so the scan counts it as a real section, not chrome."""
    return text + " " + ("word " * 40)


def test_paper_grounding_warnings_when_no_images() -> None:
    anchored = _long("The authors report the yield in Figure 1 of the paper.")
    source = f'mo.md("""{anchored}""")\n'
    warnings = paper_grounding_warnings(source)
    assert any("no paper figure" in w.lower() for w in warnings)


def test_paper_grounding_warnings_when_unanchored_fraction_high() -> None:
    background = _long(
        "A survey of the surrounding literature on catalysis and related methods."
    )
    also_background = _long(
        "Here is extra background on a dataset this paper does not use."
    )
    source = (
        f'mo.md("""{background}""")\n'
        f'mo.md("""{also_background}""")\n'
        'load_image_from_path("fig1.webp")\n'
    )
    warnings = paper_grounding_warnings(source)
    assert any("paper anchor" in w.lower() for w in warnings)
    assert UNANCHORED_MARKDOWN_WARN_FRACTION <= 1.0


def test_paper_grounding_silent_when_figures_and_anchors_present() -> None:
    body = _long("Cage escape is higher for the triplet (Fig. 1A; Table 1).")
    source = (
        f'mo.md("""{body}""")\n'
        'annotator.load_image_from_path(Path("figures/fig1.webp"))\n'
    )
    assert paper_grounding_warnings(source) == []


def test_short_markdown_chrome_does_not_count_as_unanchored() -> None:
    source = (
        'mo.md("*Answer to see feedback.*")\n'
        'mo.md("**Check your understanding (Child)**")\n'
        'load_image_from_path("fig1.png")\n'
    )
    assert paper_grounding_warnings(source) == []


def test_split_math_sub_warns_on_rho_closed_then_letter() -> None:
    warnings = split_math_sub_warnings(r"there $\rho$ A = 2 and the rest")
    assert warnings
    assert "subscripted Greek" in warnings[0]


def test_split_math_sub_warns_on_unicode_greek_then_math_letter() -> None:
    warnings = split_math_sub_warnings("there ρ $A$ = 2")
    assert warnings


def test_split_math_sub_silent_on_intact_span_and_prose() -> None:
    source = r"there $\rho_A = 2$ and $\sigma_A = 1/\ln 2$; $\mu$ and $\nu$."
    assert split_math_sub_warnings(source) == []
