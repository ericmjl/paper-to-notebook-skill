import contextlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from types import SimpleNamespace


def read_estimate(outputs):
    pattern = r'<output data-testid="estimate">([^<]+)</output>'
    for output in outputs:
        match = re.search(pattern, getattr(output, "text", "") or "")
        if match:
            return match.group(1).strip()
    raise ValueError("No visible estimate output was produced")


def inspect(notebook):
    spec = importlib.util.spec_from_file_location("notebook_fixture", notebook)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    default_outputs, definitions = module.app.run()
    if definitions["group"].value != "Group A":
        raise ValueError("The notebook did not start on Group A")
    changed_outputs, _ = module.app.run(defs={"group": SimpleNamespace(value="Group B")})
    return {
        "rendered": True,
        "observed_a": read_estimate(default_outputs),
        "observed_b": read_estimate(changed_outputs),
    }


if __name__ == "__main__":
    with contextlib.redirect_stdout(sys.stderr):
        result = inspect(sys.argv[1])
    Path(sys.argv[2]).write_text(json.dumps(result), encoding="utf-8")
