# /// script
# requires-python = ">=3.10"
# dependencies = ["marimo"]
# ///
"""Validate a generated marimo notebook.

Checks, in order (stops at the first failure):

1. The file parses as Python.
2. `marimo check --strict` reports no errors or warnings.
3. With `--run`: the notebook executes top to bottom as a script
   (`uv run <notebook>`, so the notebook's own inline dependencies are used).

After a successful parse, and without stopping the run, the script also
warns on every ``@app.cell``, ``@app.function``, and ``app.setup`` block
that does not set ``hide_code=True``. A warning is not a failure: a cell
whose code is itself the teaching point may stay visible, and failing the
run would reject that exception. The warning names each block so a visible
cell is a choice rather than an omission.

When the notebook assigns ``FigureAnnotatorWidget()`` at least twice, the
script also warns, without failing, unless every such name appears inside
one ``mo.ui.tabs`` call. One figure needs no tab box, so a single tour is
silent. The check looks only at names assigned from that constructor and at
dict values of ``something.ui.tabs(...)``. Explanation-level tabs, which
do not hold those names, are ignored.

If the notebook declares ``# paper-to-notebook-skill-components:``, also
warn when an included component is missing (``FigureAnnotatorWidget``,
``MermaidView``, ``PaperQuiz``, ``ExplainLevels``, ``TangleLatex``).
Skipped components are not required. Notebooks without the comment skip
those checks.

After a successful parse, also warn, without failing, when the notebook
embeds no paper figure image (png/jpg/webp/svg/gif, ``mo.image``,
``load_image``, or a markdown image) and when more than half of the long
``mo.md`` strings cite no paper anchor (Fig./Figure/Eq./Table/Section/§).
It also warns when a Greek TeX command is closed and then a subscript
letter is written outside the span (``$\\rho$ A`` or a Unicode ρ followed
by ``$A$``): write ``$\\rho_A$`` instead.

After a successful parse, also warn, without failing, on mechanical
processing-friendly-prose issues via :mod:`check_prose` (very long
sentences or paragraphs, noun stacks, inanimate actors with person-verbs,
ad-hoc denominal verbs from the skill's examples). Those warnings never
fail the run.

Missing ``FigureAnnotatorWidget`` is a **failure** unless the component
comment opts out of ``figure-walkthroughs``. An explicit opt-out warns
instead of failing. Other warnings never fail the run.

Usage:
    uv run scripts/validate_notebook.py path/to/notebook.py [--run]
"""

from __future__ import annotations

import argparse
import ast
import re
import subprocess
import sys
from pathlib import Path

from check_prose import format_warning, prose_warnings

_APP_BLOCK_KINDS = frozenset({"cell", "function", "setup"})
COMPONENT_HEADER = "# paper-to-notebook-skill-components:"
COMPONENT_MARKERS: dict[str, str] = {
    "figure-walkthroughs": "FigureAnnotatorWidget",
    "method-diagrams": "MermaidView",
    "final-quiz": "PaperQuiz",
    "explain-levels": "ExplainLevels",
    "equations": "TangleLatex",
}

PAPER_ANCHOR_RE = re.compile(
    r"(?:(?:Fig|Figure|Eq|Eqn|Equation|Table|Tab|Section|Sec)\.?\s*\d|§\s*\d)",
    re.IGNORECASE,
)
PAPER_IMAGE_RE = re.compile(
    r"""(?x)
    \.(?:png|jpe?g|webp|svg|gif|tif{1,2})\b
    | \bmo\.image\s*\(
    | \bload_image(?:_from_path)?\s*\(
    | !\[[^\]]*\]\([^)]+\)
    """,
    re.IGNORECASE,
)
UNANCHORED_MARKDOWN_WARN_FRACTION = 0.5
MIN_MARKDOWN_CHARS = 80
_GREEK_TEX = (
    "alpha|beta|gamma|delta|epsilon|varepsilon|zeta|eta|theta|vartheta|"
    "iota|kappa|lambda|mu|nu|xi|pi|varpi|rho|varrho|sigma|varsigma|"
    "tau|upsilon|phi|varphi|chi|psi|omega|Gamma|Delta|Theta|Lambda|"
    "Xi|Pi|Sigma|Upsilon|Phi|Psi|Omega"
)
SPLIT_MATH_SUB_RE = re.compile(
    rf"\$\\(?:{_GREEK_TEX})\$(?:\s+[A-Z]\b|_)"
    r"|[αβγδεζηθικλμνξπρστυφχψωΓΔΘΛΞΠΣΦΨΩ]\s*\$[A-Za-z_]"
)


def _called(node: ast.expr) -> ast.expr:
    """Return the callable a decorator or ``with`` item names.

    :param node: decorator or context expression, with or without a call
    :return: the name or attribute being called
    """
    if isinstance(node, ast.Call):
        return node.func
    return node


def _app_kind(node: ast.expr) -> str | None:
    """Return ``cell``, ``function``, or ``setup`` when ``node`` is an app block.

    :param node: decorator or ``with`` context expression
    :return: the block kind, or None when ``node`` is not an ``app`` block
    """
    target = _called(node)
    if (
        isinstance(target, ast.Attribute)
        and isinstance(target.value, ast.Name)
        and target.value.id == "app"
        and target.attr in _APP_BLOCK_KINDS
    ):
        return target.attr
    return None


def _hides_code(node: ast.expr) -> bool:
    """Return whether ``node`` passes the literal keyword ``hide_code=True``.

    :param node: decorator or ``with`` context expression
    :return: True only for a call that sets ``hide_code`` to the constant True
    """
    if not isinstance(node, ast.Call):
        return False
    return any(
        keyword.arg == "hide_code"
        and isinstance(keyword.value, ast.Constant)
        and keyword.value.value is True
        for keyword in node.keywords
    )


def visible_code_blocks(tree: ast.AST) -> list[tuple[int, str]]:
    """List notebook blocks that leave their source visible.

    :param tree: parsed notebook module
    :return: ``(lineno, label)`` pairs in source order
    """
    found: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for decorator in node.decorator_list:
                kind = _app_kind(decorator)
                if kind in {"cell", "function"} and not _hides_code(decorator):
                    name = "" if node.name == "_" else f" {node.name}"
                    found.append((decorator.lineno, f"@app.{kind}{name}"))
        elif isinstance(node, ast.With):
            for item in node.items:
                expr = item.context_expr
                if _app_kind(expr) == "setup" and not _hides_code(expr):
                    found.append((expr.lineno, "with app.setup"))
    found.sort(key=lambda pair: pair[0])
    return found


def _is_annotator_call(node: ast.expr) -> bool:
    """Return whether ``node`` constructs a ``FigureAnnotatorWidget``.

    :param node: expression on the right of an assignment
    :return: True when ``node`` calls the name ``FigureAnnotatorWidget``
    """
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "FigureAnnotatorWidget"
    )


def _is_ui_tabs(node: ast.Call) -> bool:
    """Return whether ``node`` is a ``something.ui.tabs`` call.

    :param node: call expression
    :return: True for ``mo.ui.tabs(...)`` and the same shape under another name
    """
    func = node.func
    return (
        isinstance(func, ast.Attribute)
        and func.attr == "tabs"
        and isinstance(func.value, ast.Attribute)
        and func.value.attr == "ui"
    )


def _annotator_names(tree: ast.AST) -> list[tuple[int, str]]:
    """List names assigned from ``FigureAnnotatorWidget()``.

    :param tree: parsed notebook module
    :return: ``(lineno, name)`` pairs in source order
    """
    found: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or not _is_annotator_call(node.value):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name):
                found.append((target.lineno, target.id))
    found.sort(key=lambda pair: pair[0])
    return found


def _tabs_holding(tree: ast.AST, names: set[str]) -> list[tuple[int, set[str]]]:
    """List ``mo.ui.tabs`` calls whose dict values mention figure tours.

    :param tree: parsed notebook module
    :param names: assigned ``FigureAnnotatorWidget`` names
    :return: ``(lineno, names found in that call)`` for tabs that hold at least one
    """
    found: list[tuple[int, set[str]]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not _is_ui_tabs(node) or not node.args:
            continue
        argument = node.args[0]
        if not isinstance(argument, ast.Dict):
            continue
        held = {
            child.id
            for child in ast.walk(argument)
            if isinstance(child, ast.Name) and child.id in names
        }
        if held:
            found.append((node.lineno, held))
    found.sort(key=lambda pair: pair[0])
    return found


def split_figure_tours(tree: ast.AST) -> list[tuple[int, str]]:
    """List figure tours that are not all inside one ``mo.ui.tabs``.

    :param tree: parsed notebook module
    :return: ``(lineno, label)`` pairs, empty when the tours share one tab box
    """
    assigned = _annotator_names(tree)
    if len(assigned) < 2:
        return []
    names = {name for _, name in assigned}
    boxes = _tabs_holding(tree, names)
    if len(boxes) == 1 and boxes[0][1] == names:
        return []
    if not boxes:
        return [(lineno, name) for lineno, name in assigned]
    covered = set().union(*(held for _, held in boxes))
    missing = [
        (lineno, name) for lineno, name in assigned if name not in covered
    ]
    if len(boxes) > 1:
        return [(lineno, f"mo.ui.tabs ({len(held)} tours)") for lineno, held in boxes] + missing
    return missing or [(assigned[0][0], "figure tours are split across tabs")]


def report_figure_tabs(blocks: list[tuple[int, str]], tour_count: int) -> None:
    """Print the one-tab-box scan. Warnings do not fail the run.

    :param blocks: ``(lineno, label)`` pairs from :func:`split_figure_tours`
    :param tour_count: how many ``FigureAnnotatorWidget`` names were assigned
    """
    if tour_count < 2:
        return
    if not blocks:
        print("[figures] figure tours share one mo.ui.tabs")
        return
    print(
        "[figures] WARN: figure tours do not share one mo.ui.tabs "
        "(one tab per figure):"
    )
    for lineno, label in blocks:
        print(f"  line {lineno}: {label}")


def report_visible_code(blocks: list[tuple[int, str]]) -> None:
    """Print the hide-code scan. Warnings do not fail the run.

    :param blocks: ``(lineno, label)`` pairs from :func:`visible_code_blocks`
    """
    if not blocks:
        print("[hide_code] all cells set hide_code=True")
        return
    if len(blocks) == 1:
        summary = "1 block leaves code visible."
    else:
        summary = f"{len(blocks)} blocks leave code visible."
    print(
        f"[hide_code] WARN: {summary} "
        "Use hide_code=True unless the code itself is the teaching point:"
    )
    for lineno, label in blocks:
        print(f"  line {lineno}: {label}")


def _string_from_ast(node: ast.AST) -> str | None:
    """Return a string constant or the literal parts of an f-string.

    :param node: AST node that may hold markdown text
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


def markdown_texts(source: str) -> list[str]:
    """Return the string arguments of every ``mo.md(...)`` call.

    :param source: Notebook source text.
    """
    tree = ast.parse(source)
    found: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not node.args:
            continue
        func = node.func
        if not (isinstance(func, ast.Attribute) and func.attr == "md"):
            continue
        text = _string_from_ast(node.args[0])
        if text is not None:
            found.append(text)
    return found


def has_paper_figure_images(source: str) -> bool:
    """Return whether the source embeds or points at a raster/vector image.

    :param source: Notebook source text.
    """
    return PAPER_IMAGE_RE.search(source) is not None


def paper_grounding_warnings(source: str) -> list[str]:
    """Return warnings for missing paper figures or unanchored markdown.

    Short ``mo.md`` strings (chrome, check prompts) are ignored. A notebook
    with no long markdown cells is silent on the anchor scan.

    :param source: Notebook source text.
    """
    warnings: list[str] = []
    if not has_paper_figure_images(source):
        warnings.append(
            "no paper figure images embedded or referenced "
            "(png/jpg/webp/svg/gif, mo.image, load_image, or markdown image)"
        )
    sections = [
        text for text in markdown_texts(source) if len(text.strip()) >= MIN_MARKDOWN_CHARS
    ]
    if sections:
        unanchored = sum(1 for text in sections if PAPER_ANCHOR_RE.search(text) is None)
        fraction = unanchored / len(sections)
        if fraction > UNANCHORED_MARKDOWN_WARN_FRACTION:
            warnings.append(
                f"{unanchored}/{len(sections)} markdown cells cite no paper anchor "
                f"(Fig./Figure/Eq./Table/Section/§); fraction {fraction:.2f} "
                f"> {UNANCHORED_MARKDOWN_WARN_FRACTION}"
            )
    return warnings


def split_math_sub_warnings(source: str) -> list[str]:
    """Return warnings for Greek symbols split across a math-span boundary.

    Catches ``$\\rho$ A`` / ``$\\rho$_A`` and a Unicode Greek letter followed
    by a one-letter math span. Intact ``$\\rho_A$`` is silent.

    :param source: Notebook source text.
    """
    if SPLIT_MATH_SUB_RE.search(source) is None:
        return []
    return [
        "subscripted Greek split across a math span "
        r"($\rho$ A or Unicode ρ + $A$); write $\rho_A$ as one span"
    ]


def parse_component_header(source: str) -> list[str] | None:
    """Return included component ids, or ``None`` if none are declared.

    :param source: Notebook source text.
    """
    for line in source.splitlines():
        stripped = line.strip()
        if stripped.startswith(COMPONENT_HEADER):
            rest = stripped[len(COMPONENT_HEADER) :].strip()
            if not rest:
                return []
            return [part.strip() for part in rest.split(",") if part.strip()]
    return None


def figure_walkthroughs_opted_out(source: str) -> bool:
    """Return whether the component comment omits figure walkthroughs.

    No comment means the user did not opt out.

    :param source: Notebook source text.
    """
    included = parse_component_header(source)
    if included is None:
        return False
    return "figure-walkthroughs" not in included


def check_figure_walkthroughs(source: str) -> tuple[list[str], list[str]]:
    """Return ``(warnings, errors)`` for missing ``FigureAnnotatorWidget`` use.

    Missing the widget is a failure unless the component comment opts out
    of ``figure-walkthroughs``. An explicit opt-out is a warning: the
    paper's figures must still appear with number and caption.

    :param source: Notebook source text.
    """
    if "FigureAnnotatorWidget" in source:
        return [], []
    if figure_walkthroughs_opted_out(source):
        return [
            "figure-walkthroughs omitted; still show each main-text figure "
            "with its number and caption"
        ], []
    return [], [
        "no FigureAnnotatorWidget usage; include figure walkthroughs, or "
        f"opt out with {COMPONENT_HEADER.strip()} listing the other "
        "components only"
    ]


def check_components(source: str) -> list[str]:
    """Return warning messages for included components that are missing.

    Unknown names in the header are also reported. A skipped known
    component is never a warning, even when its marker is absent.

    :param source: Notebook source text.
    """
    included = parse_component_header(source)
    if included is None:
        return []

    warnings: list[str] = []
    known = set(COMPONENT_MARKERS)
    for name in included:
        if name not in known:
            warnings.append(
                f"unknown component {name!r} in {COMPONENT_HEADER.strip()}"
            )
            continue
        if name == "figure-walkthroughs":
            continue  # check_figure_walkthroughs owns missing-widget failures
        marker = COMPONENT_MARKERS[name]
        if marker not in source:
            warnings.append(
                f"included component {name} is missing ({marker} not found); "
                "skipped components are not required"
            )
    return warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("notebook", type=Path)
    parser.add_argument(
        "--run", action="store_true", help="also execute the notebook as a script"
    )
    parser.add_argument(
        "--timeout", type=int, default=600, help="seconds allowed for --run"
    )
    args = parser.parse_args()
    sys.stdout.reconfigure(line_buffering=True)  # keep step headers in order with subprocess output
    nb: Path = args.notebook

    if not nb.is_file():
        print(f"FAIL: {nb} not found")
        return 1

    source = nb.read_text()

    print("[1/3] syntax")
    try:
        tree = ast.parse(source, filename=str(nb))
    except SyntaxError as e:
        print(f"FAIL: {e}")
        return 1
    visible = visible_code_blocks(tree)
    report_visible_code(visible)
    tours = _annotator_names(tree)
    split = split_figure_tours(tree)
    report_figure_tabs(split, len(tours))

    print("[2/3] marimo check --strict")
    result = subprocess.run(
        [sys.executable, "-m", "marimo", "check", "--strict", str(nb)]
    )
    if result.returncode != 0:
        print("FAIL: marimo check reported problems")
        return 1

    if args.run:
        print("[3/3] smoke run")
        try:
            result = subprocess.run(["uv", "run", str(nb)], timeout=args.timeout)
        except subprocess.TimeoutExpired:
            print(f"FAIL: notebook did not finish within {args.timeout}s")
            return 1
        if result.returncode != 0:
            print("FAIL: notebook raised an error when run")
            return 1
    else:
        print("[3/3] smoke run skipped (pass --run to enable)")

    component_warnings = check_components(source)
    if component_warnings:
        print("[components]")
        for message in component_warnings:
            print(f"WARN: {message}")

    grounding_warnings = paper_grounding_warnings(source)
    if grounding_warnings:
        print("[paper]")
        for message in grounding_warnings:
            print(f"WARN: {message}")

    math_span_warnings = split_math_sub_warnings(source)
    if math_span_warnings:
        print("[math]")
        for message in math_span_warnings:
            print(f"WARN: {message}")

    writing_warnings = prose_warnings(source)
    if writing_warnings:
        print("[prose]")
        for warning in writing_warnings:
            print(f"WARN: {format_warning(warning)}")

    walkthrough_warnings, walkthrough_errors = check_figure_walkthroughs(source)
    if walkthrough_warnings or walkthrough_errors:
        print("[figure-walkthroughs]")
        for message in walkthrough_warnings:
            print(f"WARN: {message}")
        for message in walkthrough_errors:
            print(f"FAIL: {message}")

    notes: list[str] = []
    if visible:
        noun = "warning" if len(visible) == 1 else "warnings"
        notes.append(f"{len(visible)} hide_code {noun}")
    if split:
        noun = "warning" if len(split) == 1 else "warnings"
        notes.append(f"{len(split)} figure-tab {noun}")
    if component_warnings:
        noun = "warning" if len(component_warnings) == 1 else "warnings"
        notes.append(f"{len(component_warnings)} component {noun}")
    if grounding_warnings:
        noun = "warning" if len(grounding_warnings) == 1 else "warnings"
        notes.append(f"{len(grounding_warnings)} paper-grounding {noun}")
    if math_span_warnings:
        noun = "warning" if len(math_span_warnings) == 1 else "warnings"
        notes.append(f"{len(math_span_warnings)} math-span {noun}")
    if writing_warnings:
        noun = "warning" if len(writing_warnings) == 1 else "warnings"
        notes.append(f"{len(writing_warnings)} prose {noun}")
    if walkthrough_warnings:
        noun = "warning" if len(walkthrough_warnings) == 1 else "warnings"
        notes.append(f"{len(walkthrough_warnings)} figure-walkthrough {noun}")
    if walkthrough_errors:
        noun = "error" if len(walkthrough_errors) == 1 else "errors"
        notes.append(f"{len(walkthrough_errors)} figure-walkthrough {noun}")
        print(f"FAIL: {nb} ({', '.join(notes)})")
        return 1
    if notes:
        print(f"OK: {nb} ({', '.join(notes)}; not a failure)")
    else:
        print(f"OK: {nb}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
