import contextlib
import importlib.util
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from types import SimpleNamespace

import marimo as mo


def read_estimate(outputs):
    pattern = r'<output data-testid="estimate">([^<]+)</output>'
    for output in outputs:
        match = re.search(pattern, getattr(output, "text", "") or "")
        if match:
            return match.group(1).strip()
    raise ValueError("No visible estimate output was produced")


class NotebookHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables = []
        self.text = []
        self.table = None
        self.row = None
        self.cell = None

    def handle_starttag(self, tag, attrs):
        if tag in ("h1", "h2", "h3", "p", "div", "br", "th", "td", "li"):
            self.text.append(" ")
        if tag == "table":
            self.table = []
        elif tag == "tr" and self.table is not None:
            self.row = []
        elif tag in ("th", "td") and self.row is not None:
            self.cell = []
        elif tag == "br" and self.cell is not None:
            self.cell.append(" ")

    def handle_data(self, data):
        self.text.append(data)
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag in ("th", "td") and self.cell is not None:
            self.row.append(" ".join("".join(self.cell).split()))
            self.cell = None
        elif tag == "tr" and self.row is not None:
            self.table.append(self.row)
            self.row = None
        elif tag == "table" and self.table is not None:
            self.tables.append(self.table)
            self.table = None


def read_notebook_output(outputs):
    tables = []
    text = []
    for output in outputs:
        if isinstance(output, mo.ui.table):
            # Use the same formatted data as the table widget in pinned marimo.
            columns = [str(column) for column in output._manager.get_column_names()]
            rows = json.loads(output._manager.to_json_str(output._format_mapping))
            cells = [
                [normalize_cell(row.get(column)) for column in columns]
                for row in rows
            ]
            tables.append([[normalize_cell(column) for column in columns], *cells])
            continue
        parser = NotebookHTML()
        parser.feed(getattr(output, "text", "") or "")
        parser.close()
        tables.extend(parser.tables)
        text.append(" ".join("".join(parser.text).split()))
    return {"tables": tables, "notebook_text": "\n".join(part for part in text if part)}


def normalize_cell(value):
    return "" if value is None else " ".join(str(value).split())


def inspect(notebook, check):
    spec = importlib.util.spec_from_file_location("notebook_fixture", notebook)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    default_outputs, definitions = module.app.run()
    if check == "table":
        return read_notebook_output(default_outputs)
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
        result = inspect(sys.argv[1], sys.argv[3])
    Path(sys.argv[2]).write_text(json.dumps(result), encoding="utf-8")
