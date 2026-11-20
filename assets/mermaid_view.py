"""Render Mermaid with the ELK layout in the hand-drawn look, in a zoomable viewport.

Unlike `mo.mermaid` (dagre layout, shrunk to the column), it draws at natural size in a
viewport you can zoom (buttons, Ctrl-scroll, pinch) and drag, lets Mermaid wrap labels
(pass source without `<br>`), and moves group titles clear of arrows. Loads Mermaid
from jsdelivr, so it needs internet the first time.

Pass `steps` to step through the diagram: Prev / Next, arrow keys, or click a node.
Each step highlights its node and incoming arrows, centres them, and shows its text in
a side panel; only the highlight moves, the diagram is not redrawn. A step is a dict:
`node` (Mermaid node id), `title`, and optional `ref`, `what`, `params`, `note`,
`incoming` ([from, to] node-id pairs), `receives` (lines of text). `step` is the
current index, set by the widget.

    from mermaid_view import MermaidView
    MermaidView(source="flowchart LR\\n  a --> b", steps=[{"node": "a", "title": "Start"}])
"""

import anywidget
import traitlets

_ESM = """
import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11.12.0/dist/mermaid.esm.min.mjs";
import elkLayouts from "https://cdn.jsdelivr.net/npm/@mermaid-js/layout-elk@0.2.0/dist/mermaid-layout-elk.esm.min.mjs";

mermaid.registerLayoutLoaders(elkLayouts);
let counter = 0;
const HIGHLIGHT = "#e8590c";

function isDark(el) {
  const root = el.getRootNode().host ?? el;
  return Boolean(root.closest?.(".dark, .dark-theme, [data-theme='dark']")) ||
    document.documentElement.classList.contains("dark") ||
    document.body.classList.contains("dark") ||
    document.body.classList.contains("dark-theme");
}

function make(tag, cls, parent, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text !== undefined) e.textContent = text;
  parent?.append(e);
  return e;
}

// Arrows into a group often run through its title. Slide each title sideways, inside its
// group, to the nearest spot no arrow crosses. If there is none, draw the title above the
// arrows with a thin halo around its letters (no box over the arrow).
function haloTitle(svg, label) {
  const m = svg.getScreenCTM().inverse().multiply(label.getScreenCTM());
  const bg = mermaid.mermaidAPI.getConfig().themeVariables?.clusterBkg ?? "white";
  label.setAttribute("transform", `matrix(${m.a} ${m.b} ${m.c} ${m.d} ${m.e} ${m.f})`);
  svg.append(label);  // after the arrows, so it paints on top
  for (const span of label.querySelectorAll("span, p, div")) {
    span.style.webkitTextStroke = `4px ${bg}`;
    span.style.paintOrder = "stroke fill";  // the stroke sits behind the letters
  }
}

function clearGroupTitles(svg) {
  const scale = svg.getScreenCTM()?.a;
  if (!scale) return;
  const pad = 6;
  const points = [];
  for (const path of svg.querySelectorAll(".edgePaths path")) {
    const m = path.getScreenCTM();
    for (let s = 0, n = path.getTotalLength(); s <= n; s += 2) points.push(path.getPointAtLength(s).matrixTransform(m));
  }
  const groups = [...svg.querySelectorAll(".cluster")].map((g) => g.getBoundingClientRect());
  for (const label of svg.querySelectorAll(".cluster-label")) {
    const range = document.createRange();
    range.selectNodeContents(label);
    const t = range.getBoundingClientRect();  // the text itself, not its wider layout box
    const g = groups
      .filter((g) => g.left <= t.left && t.right <= g.right && g.top <= t.top && t.bottom <= g.bottom)
      .sort((a, b) => a.width * a.height - b.width * b.height)[0];  // innermost group
    if (!g) continue;
    const blocked = points
      .filter((p) => p.y >= t.top - pad && p.y <= t.bottom + pad && p.x >= g.left && p.x <= g.right)
      .map((p) => [p.x - pad - t.width, p.x + pad]);  // left edges that would touch this arrow point
    const lo = g.left + pad, hi = g.right - pad - t.width;
    const free = (x) => x >= lo && x <= hi && blocked.every(([a, b]) => x <= a || x >= b);
    const best = [t.left, ...blocked.flat()].filter(free)
      .sort((a, b) => Math.abs(a - t.left) - Math.abs(b - t.left))[0];
    if (best === undefined) haloTitle(svg, label);
    else if (best !== t.left) {
      label.setAttribute("transform", `${label.getAttribute("transform") ?? ""} translate(${(best - t.left) / scale}, 0)`);
    }
  }
}

function render({ model, el }) {
  make("style", null, el).textContent = `
    .mv { font: 14px/1.5 var(--text-font, system-ui, sans-serif); color: inherit; }
    .mv-bar { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; margin-bottom: 6px; }
    .mv-bar button { font: inherit; padding: 2px 10px; border: 1px solid #bbb; border-radius: 6px;
      background: transparent; color: inherit; cursor: pointer; }
    .mv-bar button:disabled { opacity: 0.4; cursor: default; }
    .mv-title { flex: 1; text-align: center; font-weight: 600; }
    .mv-main { display: flex; flex-wrap: wrap; gap: 12px; }
    .mv-port { position: relative; overflow: hidden; flex: 3 1 420px; border: 1px solid #ccc;
      border-radius: 8px; cursor: grab; touch-action: none; outline: none; }
    .mv-port:focus-visible { box-shadow: 0 0 0 2px ${HIGHLIGHT}; }
    .mv-port.drag { cursor: grabbing; }
    .mv-port > svg { position: absolute; left: 0; top: 0; transform-origin: 0 0; max-width: none; }
    .mv-port.glide > svg { transition: transform 300ms ease; }
    @media (prefers-reduced-motion: reduce) { .mv-port.glide > svg { transition: none; } }
    .mv-port .mv-ring { fill: none; stroke: ${HIGHLIGHT}; stroke-width: 4px; pointer-events: none; }
    .mv-port path.mv-in { stroke: ${HIGHLIGHT} !important; stroke-width: 2.5px !important; }
    .mv-port [data-step] { cursor: pointer; }
    .mv-panel { flex: 1 1 220px; overflow: auto; padding: 8px 12px; border-left: 3px solid ${HIGHLIGHT}; }
    .mv-panel p { margin: 0 0 8px; }
    .mv-panel ul { margin: 0 0 8px; padding-left: 18px; }
    .mv-muted { opacity: 0.75; font-style: italic; }
    .mv-error { color: #c0392b; font-family: monospace; white-space: pre-wrap; }
  `;
  const root = make("div", "mv", el);
  const bar = make("div", "mv-bar", root);
  const prev = make("button", null, bar, "◀ Prev");
  const title = make("span", "mv-title", bar);
  const next = make("button", null, bar, "Next ▶");
  const zoomBar = make("div", "mv-bar", root);
  const [zoomOut, zoomIn, fitBtn, centreBtn] = ["−", "+", "Fit", "Re-centre"].map((t) => make("button", null, zoomBar, t));
  const main = make("div", "mv-main", root);
  const port = make("div", "mv-port", main);
  port.tabIndex = 0;
  const panel = make("div", "mv-panel", main);

  let svg = null, ring = null, boxes = {}, edges = [], drawId = 0;
  let view = { k: 1, x: 0, y: 0 }, follow = true, size = { w: 0, h: 0 }, origin = { x: 0, y: 0 };
  const steps = () => model.get("steps");

  function apply(glide) {
    if (!svg) return;
    port.classList.toggle("glide", glide);
    svg.style.transform = `translate(${view.x}px, ${view.y}px) scale(${view.k})`;
  }
  function frame(b, keepZoom) {  // centre box b (diagram units); zoom out only if it doesn't fit
    const w = port.clientWidth, h = port.clientHeight, m = 32;
    const fits = Math.min((w - m) / b.w, (h - m) / b.h, 2);
    const k = keepZoom ? Math.min(view.k, fits) : fits;
    view = { k, x: w / 2 - (b.x + b.w / 2) * k, y: h / 2 - (b.y + b.h / 2) * k };
  }
  function fitAll(glide) {
    const w = port.clientWidth, h = port.clientHeight;
    const k = Math.min(1, (w - 16) / size.w, (h - 16) / size.h);
    view = { k, x: (w - size.w * k) / 2, y: (h - size.h * k) / 2 };
    apply(glide);
  }
  function zoomAt(f, px = port.clientWidth / 2, py = port.clientHeight / 2) {
    const k = Math.max(0.1, Math.min(4, view.k * f));
    view = { k, x: px - (px - view.x) * (k / view.k), y: py - (py - view.y) * (k / view.k) };
    follow = false;
    apply(false);
  }
  function union(list) {
    const x0 = Math.min(...list.map((b) => b.x)), y0 = Math.min(...list.map((b) => b.y));
    const x1 = Math.max(...list.map((b) => b.x + b.w)), y1 = Math.max(...list.map((b) => b.y + b.h));
    return { x: x0, y: y0, w: x1 - x0, h: y1 - y0 };
  }
  const inEdges = (s) => edges.filter((e) => (s.incoming ?? []).some(([a, b]) => e.id.startsWith(`L_${a}_${b}_`)));

  function focus(glide) {
    const s = steps()[model.get("step")];
    if (!s || !boxes[s.node]) return fitAll(glide);
    frame(union([boxes[s.node], ...inEdges(s).map((e) => e.box)]), true);
    apply(glide);
  }

  function show() {
    const list = steps(), i = Math.min(model.get("step"), list.length - 1);
    const hasSteps = list.length > 0;
    bar.style.display = panel.style.display = hasSteps ? "" : "none";
    if (!hasSteps || !svg) return;
    const s = list[i];
    prev.disabled = i <= 0;
    next.disabled = i >= list.length - 1;
    title.textContent = `Step ${i + 1} of ${list.length}: ${s.title}`;
    const b = boxes[s.node];
    ring.style.display = b ? "" : "none";
    const ringBox = b && { x: b.x + origin.x - 5, y: b.y + origin.y - 5, width: b.w + 10, height: b.h + 10 };
    if (b) for (const [k, v] of Object.entries(ringBox)) ring.setAttribute(k, v);
    const lit = new Set(inEdges(s));
    for (const e of edges) e.path.classList.toggle("mv-in", lit.has(e));
    panel.replaceChildren();
    make("p", null, panel).append(make("strong", null, null, s.title), s.ref ? ` (${s.ref})` : "");
    if (s.what) make("p", null, panel, s.what);
    if (s.params) make("p", null, panel, `Parameters: ${s.params}`);
    if (s.receives?.length) {
      make("p", null, panel, "Receives:");
      const ul = make("ul", null, panel);
      for (const line of s.receives) make("li", null, ul, line);
    }
    if (s.note) make("p", "mv-muted", panel, s.note);
    if (follow) focus(true);
  }
  function go(i) {
    const n = steps().length;
    if (!n) return;
    follow = true;
    model.set("step", Math.max(0, Math.min(n - 1, i)));
    model.save_changes();
  }

  function markSteps() {  // nodes with a step get a pointer cursor
    for (const g of svg?.querySelectorAll("[data-node]") ?? []) {
      g.toggleAttribute("data-step", steps().some((s) => s.node === g.dataset.node));
    }
  }

  async function draw() {
    const id = ++drawId;
    if (!model.get("source").trim()) { svg = null; port.replaceChildren(); return; }
    mermaid.initialize({
      startOnLoad: false,
      securityLevel: "strict",
      theme: isDark(el) ? "dark" : model.get("theme"),
      layout: "elk",
      look: model.get("look"),
      handDrawnSeed: 1,  // same strokes on every redraw
      elk: { nodePlacementStrategy: "NETWORK_SIMPLEX" },
      fontFamily: "var(--text-font, system-ui, sans-serif)",
      themeVariables: { fontSize: `${model.get("font_size")}px` },
      flowchart: {
        htmlLabels: true, curve: "basis", nodeSpacing: 36, rankSpacing: 56, padding: 14,
        wrappingWidth: model.get("wrap_width"), useMaxWidth: false,
        subGraphTitleMargin: { top: 6, bottom: 10 },
      },
    });
    try {
      const out = await mermaid.render(`mermaid-view-${counter++}`, model.get("source"));
      if (id !== drawId) return;  // a newer draw started while this one rendered
      port.innerHTML = out.svg;
      svg = port.querySelector("svg");
      const vb = svg.viewBox.baseVal;
      size = { w: vb.width, h: vb.height };
      origin = { x: vb.x, y: vb.y };
      svg.setAttribute("width", size.w);
      svg.setAttribute("height", size.h);
      const fitWidth = Math.min(1, (port.clientWidth || size.w) / size.w);
      port.style.height = `${Math.min(model.get("height"), size.h * fitWidth + 16)}px`;
      clearGroupTitles(svg);
      // Measure nodes and arrows once, in diagram units, before any zoom is applied.
      const toSvg = svg.getScreenCTM().inverse();
      const measure = (e) => {
        const r = e.getBoundingClientRect();
        const p = new DOMPoint(r.left, r.top).matrixTransform(toSvg), q = new DOMPoint(r.right, r.bottom).matrixTransform(toSvg);
        return { x: p.x - vb.x, y: p.y - vb.y, w: q.x - p.x, h: q.y - p.y };
      };
      boxes = {};
      for (const g of svg.querySelectorAll("g[id^='flowchart-'], g.cluster[id]")) {
        const id = g.classList.contains("cluster") ? g.id : g.id.replace(/^flowchart-/, "").replace(/-\\d+$/, "");
        boxes[id] = measure(g);
        g.dataset.node = id;
      }
      edges = [...svg.querySelectorAll(".edgePaths path[id]")].map((path) => ({ id: path.id, path, box: measure(path) }));
      ring = document.createElementNS("http://www.w3.org/2000/svg", "rect");
      ring.setAttribute("class", "mv-ring");
      ring.setAttribute("rx", 6);
      svg.append(ring);
      markSteps();
      if (steps().length) { follow = true; show(); }  // keeps the current zoom (natural size at first)
      else fitAll(false);
    } catch (err) {
      svg = null;
      port.replaceChildren(make("div", "mv-error", null, `Mermaid error: ${err?.message ?? err}`));
    }
  }

  // Stepping: buttons, arrow keys, or a click on a node (cycles through that node's steps).
  prev.onclick = () => go(model.get("step") - 1);
  next.onclick = () => go(model.get("step") + 1);
  port.addEventListener("keydown", (e) => {
    const keys = { ArrowLeft: () => go(model.get("step") - 1), ArrowRight: () => go(model.get("step") + 1),
      "+": () => zoomAt(1.25), "=": () => zoomAt(1.25), "-": () => zoomAt(0.8), "0": () => fitAll(true) };
    if (keys[e.key]) { e.preventDefault(); keys[e.key](); }
  });
  // Zoom: buttons, or Ctrl-scroll / pinch at the pointer. Plain scrolling still scrolls the page.
  zoomIn.onclick = () => zoomAt(1.25);
  zoomOut.onclick = () => zoomAt(0.8);
  fitBtn.onclick = () => { follow = false; fitAll(true); };
  centreBtn.onclick = () => { follow = true; view.k = 1; focus(true); };  // back to natural size, shrunk only to fit
  port.addEventListener("wheel", (e) => {
    if (!e.ctrlKey) return;
    e.preventDefault();
    const r = port.getBoundingClientRect();
    zoomAt(Math.exp(-e.deltaY * 0.01), e.clientX - r.left, e.clientY - r.top);
  }, { passive: false });
  // Pan by dragging; a press that barely moves is a click.
  let drag = null;
  port.addEventListener("pointerdown", (e) => {
    drag = { x: e.clientX, y: e.clientY, vx: view.x, vy: view.y, moved: false };
    port.setPointerCapture(e.pointerId);
  });
  port.addEventListener("pointermove", (e) => {
    if (!drag) return;
    const dx = e.clientX - drag.x, dy = e.clientY - drag.y;
    if (!drag.moved && Math.hypot(dx, dy) < 4) return;
    drag.moved = true;
    port.classList.add("drag");
    follow = false;
    view = { ...view, x: drag.vx + dx, y: drag.vy + dy };
    apply(false);
  });
  port.addEventListener("pointerup", (e) => {
    const clicked = drag && !drag.moved;
    drag = null;
    port.classList.remove("drag");
    if (!clicked) return;
    port.releasePointerCapture(e.pointerId);
    const scope = el.getRootNode().elementsFromPoint ? el.getRootNode() : document;  // marimo renders in a shadow root
    const node = scope.elementsFromPoint(e.clientX, e.clientY).map((t) => t.closest?.("[data-node]")).find(Boolean);
    const id = node?.dataset.node, list = steps(), at = model.get("step");
    const matches = list.map((s, i) => (s.node === id ? i : -1)).filter((i) => i >= 0);
    if (matches.length) go(matches.find((i) => i > at) ?? matches[0]);
  });

  for (const name of ["source", "theme", "look", "font_size", "wrap_width", "height"]) model.on(`change:${name}`, draw);
  model.on("change:steps", () => { markSteps(); show(); });
  model.on("change:step", show);
  draw();
}

export default { render };
"""


class MermaidView(anywidget.AnyWidget):
    _esm = _ESM
    source = traitlets.Unicode("").tag(sync=True)
    steps = traitlets.List(traitlets.Dict()).tag(sync=True)
    step = traitlets.Int(0).tag(sync=True)
    theme = traitlets.Unicode("forest").tag(sync=True)
    look = traitlets.Unicode("handDrawn").tag(sync=True)  # or "classic"
    font_size = traitlets.Int(16).tag(sync=True)
    wrap_width = traitlets.Int(220).tag(sync=True)
    height = traitlets.Int(520).tag(sync=True)  # most the viewport grows to, in px
