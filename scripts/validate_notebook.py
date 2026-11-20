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

Usage:
    uv run scripts/validate_notebook.py path/to/notebook.py [--run]
"""

import argparse
import ast
import subprocess
import sys
from pathlib import Path

_APP_BLOCK_KINDS = frozenset({"cell", "function", "setup"})


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

    print("[1/3] syntax")
    try:
        tree = ast.parse(nb.read_text(), filename=str(nb))
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

    notes: list[str] = []
    if visible:
        noun = "warning" if len(visible) == 1 else "warnings"
        notes.append(f"{len(visible)} hide_code {noun}")
    if split:
        noun = "warning" if len(split) == 1 else "warnings"
        notes.append(f"{len(split)} figure-tab {noun}")
    if notes:
        print(f"OK: {nb} ({', '.join(notes)}; not a failure)")
    else:
        print(f"OK: {nb}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
