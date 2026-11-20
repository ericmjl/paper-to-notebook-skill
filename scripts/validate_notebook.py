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


def report_visible_code(blocks: list[tuple[int, str]]) -> None:
    """Print the hide-code scan. Warnings do not fail the run.

    :param blocks: ``(lineno, label)`` pairs from :func:`visible_code_blocks`
    """
    if not blocks:
        print("[hide_code] all cells set hide_code=True")
        return
    noun = "block" if len(blocks) == 1 else "blocks"
    print(
        f"[hide_code] WARN: {len(blocks)} {noun} leave code visible. "
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

    if visible:
        noun = "warning" if len(visible) == 1 else "warnings"
        print(f"OK: {nb} ({len(visible)} hide_code {noun}; not a failure)")
    else:
        print(f"OK: {nb}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
