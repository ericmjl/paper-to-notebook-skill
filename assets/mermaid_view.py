"""Render Mermaid source with the ELK layout engine, at a readable size.

marimo's built-in `mo.mermaid` uses Mermaid's default (dagre) layout and always
shrinks the diagram to the column width. For the method figures that means
arrows through labels, overlapping group boxes, and tiny text. This widget loads
Mermaid and its ELK layout from a CDN and:

- lays the graph out with ELK (cleaner routing, no overlaps);
- draws it in Mermaid's hand-drawn `look` by default (`look="classic"` for plain boxes);
- lets Mermaid wrap labels itself (`wrap_width` px), so pass the source without
  manual `<br>` wrapping;
- draws at natural size, scaling down only when wider than the column and never
  below `min_scale`; past that, the figure scrolls sideways.

Usage:

    from mermaid_view import MermaidView
    MermaidView(source=method_mermaid(stages, edges, view="detail", wrap_at=10_000))

Needs internet access the first time (jsdelivr).
"""

import anywidget
import traitlets

_ESM = """
import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11.12.0/dist/mermaid.esm.min.mjs";
import elkLayouts from "https://cdn.jsdelivr.net/npm/@mermaid-js/layout-elk@0.2.0/dist/mermaid-layout-elk.esm.min.mjs";

mermaid.registerLayoutLoaders(elkLayouts);
let counter = 0;

function isDark(el) {
  const root = el.getRootNode().host ?? el;
  return Boolean(root.closest?.(".dark, .dark-theme, [data-theme='dark']")) ||
    document.documentElement.classList.contains("dark") ||
    document.body.classList.contains("dark") ||
    document.body.classList.contains("dark-theme");
}

function render({ model, el }) {
  const style = document.createElement("style");
  style.textContent = `
    .mv { width: 100%; overflow-x: auto; display: flex; }
    .mv > svg { margin: 0 auto; flex: none; }
    .mv-error { color: #c0392b; font-family: monospace; white-space: pre-wrap; }
  `;
  const box = document.createElement("div");
  box.className = "mv";
  el.append(style, box);

  function fit() {
    const svg = box.querySelector("svg");
    if (!svg) return;
    const vb = svg.viewBox.baseVal;
    const avail = box.clientWidth || el.clientWidth || vb.width;
    const scale = Math.max(model.get("min_scale"), Math.min(1, avail / vb.width));
    svg.setAttribute("width", vb.width * scale);
    svg.setAttribute("height", vb.height * scale);
    svg.style.maxWidth = "none";
  }

  async function draw() {
    mermaid.initialize({
      startOnLoad: false,
      securityLevel: "strict",
      theme: isDark(el) ? "dark" : model.get("theme"),
      layout: "elk",
      look: model.get("look"),
      elk: { nodePlacementStrategy: "NETWORK_SIMPLEX" },
      fontFamily: "var(--text-font, system-ui, sans-serif)",
      themeVariables: { fontSize: `${model.get("font_size")}px` },
      flowchart: {
        htmlLabels: true,
        curve: "basis",
        nodeSpacing: 36,
        rankSpacing: 56,
        padding: 14,
        wrappingWidth: model.get("wrap_width"),
        useMaxWidth: false,
        subGraphTitleMargin: { top: 6, bottom: 10 },
      },
    });
    try {
      const { svg } = await mermaid.render(`mermaid-view-${counter++}`, model.get("source"));
      box.innerHTML = svg;
      fit();
    } catch (err) {
      box.innerHTML = "";
      const pre = document.createElement("div");
      pre.className = "mv-error";
      pre.textContent = `Mermaid error: ${err?.message ?? err}`;
      box.appendChild(pre);
    }
  }

  const observer = new ResizeObserver(fit);
  observer.observe(box);
  for (const name of ["source", "theme", "look", "font_size", "wrap_width"]) model.on(`change:${name}`, draw);
  model.on("change:min_scale", fit);
  draw();
  return () => observer.disconnect();
}

export default { render };
"""


class MermaidView(anywidget.AnyWidget):
    _esm = _ESM
    source = traitlets.Unicode("").tag(sync=True)
    theme = traitlets.Unicode("forest").tag(sync=True)
    look = traitlets.Unicode("handDrawn").tag(sync=True)  # or "classic"
    font_size = traitlets.Int(16).tag(sync=True)
    wrap_width = traitlets.Int(220).tag(sync=True)
    min_scale = traitlets.Float(0.75).tag(sync=True)
