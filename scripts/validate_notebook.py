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

Usage:
    uv run scripts/validate_notebook.py path/to/notebook.py [--run]
"""

import argparse
import ast
import subprocess
import sys
from pathlib import Path


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
        ast.parse(nb.read_text(), filename=str(nb))
    except SyntaxError as e:
        print(f"FAIL: {e}")
        return 1

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

    print(f"OK: {nb}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
