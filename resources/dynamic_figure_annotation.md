# Dynamic Figure Annotation

Guide an agent to turn any static figure from a scientific paper (reaction schemes, multi-panel diagrams, chemical structures, or data plots with kinetic traces and insets) into an interactive, step-by-step guided tour using `FigureAnnotatorWidget` inside a [marimo](https://marimo.io) notebook.

## Every main-text figure

The notebook includes one `FigureAnnotatorWidget` walkthrough for **every main-text figure**, not a subset of the striking ones. A multi-panel figure is one figure: one tour that walks its panels, as the example notebook does for Figure 1. Supplementary figures are out of scope unless the user asks for them.

A reproduced or simplified plot does not stand in for this tour. The tour is of the figure the paper printed.

The runnable example tours Figure 1 and Figure 2 of one paper so the widget pattern is visible. A paper notebook still tours every main-text figure.

Enumerate the figures before writing any annotation cell:

1. List every main-text figure from the paper's own structure, in reading order. For a PMC article, read the `<fig>` elements in the eutils XML and take each `<label>` (`Fig. 1`, `Fig. 2`, …). For LaTeX, use the `figure` environments and their captions. For PDF or HTML, use the numbered figures in the main text. Write the list down: label, caption, and image path.
2. Obtain an image for each label. When an image cannot be fetched or cropped out, **report that label** — a short note in the notebook where the tour would have been, and the same label in the handoff. Do not drop it from the list and continue.
3. Build a walkthrough for every figure that has an image, using the steps below.

## One tab box

All of a paper's figure walkthroughs go in **one** `mo.ui.tabs`. One tab per figure. The label is the figure number and a short title, for example `Figure 3. Spectra, the averaging window, and the actinometer`.

Build each tour in its own cell with `hide_code=True`, and return the widget from that cell so it does not also render as its own section. One display cell holds the tab box. Do not give each figure its own heading, and do not split the tours across two tab boxes or an accordion.

A figure whose image could not be obtained still gets a tab. The tab body is the short note that the image is missing.

The runnable example already uses this box for the two figures it tours.

Wrap that one tab box in `wigglystuff.FloatingPanel` (wigglystuff 0.6.0 and later; declare `wigglystuff>=0.6.0`). The class is a marimo display helper, not an anywidget: pass the tab box as `child`, and display the panel as the last expression of the cell.

```python
wigglystuff.FloatingPanel(
    mo.ui.tabs(
        {
            "Figure 1. States, cage, catalyst, quenchers": fig1_annotator,
            "Figure 2. 450 nm traces and the yield inset": fig2_annotator,
        }
    ),
    title="Figures 1–2",
    corner="bottom-right",
    width=880,
)
```

`corner` is `top-left`, `top-right`, `bottom-left`, or `bottom-right`. `width` is the panel width in pixels. `title` is the caption on the drag header. The reader drags that header to move the panel, and the header's minimize control collapses it. Do not invent a second panel, and do not paste a static image in place of the live tabs.

---

## Dependencies & Related Resources

- **Used from**: [`SKILL.md`](../SKILL.md) — read this during **Step 2** (enumerate every main-text figure) and **Step 4** (one walkthrough per figure).
- **Widget Module**: [`resources/figure_annotator_widget.py`](figure_annotator_widget.py) — Reusable `FigureAnnotatorWidget` (`anywidget.AnyWidget`) implementation.
- **Runnable Example Notebook**: [`resources/figure_annotator_example.py`](figure_annotator_example.py) — Self-contained Marimo notebook demonstrating full multi-panel diagram (Figure 1, Panels A–C) and data plot + inset (Figure 2) tours.
- **CLI Helper Script**: [`scripts/figure_annotation_helper.py`](../scripts/figure_annotation_helper.py) — Run via `uv run` for 100×100 percentage grid overlays, ink/color-channel isolation, and visual centering audit contact sheets.

---

## Core Design Principles

1. **100×100 Percentage Slice Coordinate System (`[left%, top%, width%, height%]`)**:
   - All bounding boxes are expressed as percentages ($0\text{--}100\%$) of the image's natural width and height.
   - Because `.annot-box` overlays are positioned with CSS percentages (`left: X%`, `top: Y%`, `width: W%`, `height: H%`) inside a `position: relative` container wrapping `<img style="width: 100%; height: auto; display: block;">`, annotations are **mathematically scale-invariant** across any browser viewport resize or zoom level.
2. **Just-In-Time (JIT) Visibility**:
   - All overlay boxes on the figure are **hidden by default** (`opacity: 0`) so the scientific figure remains completely unobstructed at rest.
   - Boxes and their floating pill labels light up **only on hover**—either when the reader hovers over an inline `.fig-ref` badge in the explanation text or hovers directly over an element on the figure.
3. **Color-Matched Explanation Badges**:
   - Every inline `<a class="fig-ref" data-target="element_id">Label</a>` badge in the explanation text automatically binds its CSS custom properties (`--ref-color`, `--ref-bg`, `--ref-border`, `--ref-shadow`) to the `color` defined on its corresponding diagram overlay box.
   - If an overlay box on the diagram is teal (`#0d9488`), its hover badge in the explanation text is also teal. Assign distinct colors to elements within the same tour step so readers can immediately associate text concepts with visual regions.
4. **Click-Any-Box-to-Jump-to-Step Navigation**:
   - While hovering over the diagram reveals any annotated element (even those from other steps), **clicking** any box on the diagram automatically jumps `active_step` to the tour step associated with that annotation (and cycles through matching steps if the element appears in more than one step).
5. **Top-to-Bottom Pedagogical Layout Contract**:
   Inside `FigureAnnotatorWidget`, components must appear in this exact vertical order:
   1. **Step Navigator Toolbar** (`◀ Prev`, `Step X of N`, `Next ▶`, step title, and interaction hint)
   2. **Explanation Card** (step narrative containing color-matched `.fig-ref` hover badges)
   3. **Interactive Diagram Stage** (`<img>` + 100-slice percentage overlay boxes)
   4. **Original Figure Caption Card** (verbatim caption from the paper)

---

## Step-by-Step Workflow

### Step 1: Overlay a Private 100×100 Percentage Slice Grid

Never guess bounding box coordinates blindly from raw images, and **never** draw grid lines onto the actual figure displayed to the user. First, generate a **private scratch copy** of the figure overlaid with a $100 \times 100$ percentage slice grid ($1\%$ slices, green lines every $5\%$, red labeled lines every $10\%$):

```bash
uv run scripts/figure_annotation_helper.py grid \
  --image resources/figures/fig1.webp \
  --output /tmp/fig1_100x100_grid.png
```

Read `/tmp/fig1_100x100_grid.png` using your multimodal image viewer (`read_file`). Use the percentage grid lines as a visual reference to identify the approximate percentage window `x1,y1,x2,y2` enclosing each target element.

---

### Step 2: Isolate Exact Glyph, Shape, or Color-Channel Bounds

Do **not** snap bounding boxes coarsely to grid lines, and beware of **connected-element pollution**: in scientific diagrams and plots, target labels or circular nodes are often adjacent to reaction arrows, arrow glows, horizontal energy bars, or axis lines. A naive bounding box over a wide window will grab neighboring arrows and shift the box off-center.

Use the `isolate` subcommand on a tight window around the target glyphs/trace, selecting the appropriate `--channel` filter (`any`, `black`, `red`, or `blue`) and symmetric pixel padding (`--pad-x`, `--pad-y`):

```bash
uv run scripts/figure_annotation_helper.py isolate \
  --image resources/figures/fig1.webp \
  --window 51.5,10.5,58.0,15.5 \
  --channel any \
  --pad-x 12 \
  --pad-y 9 \
  --output /tmp/triplet_box.json
```

#### Rules for Clean Isolation by Element Type:
- **Text Labels Near Arrows or Energy Bars (e.g., `¹PC`, `¹PC*`, `³PC*`)**:
  Tighten `--window` to enclose only the character glyphs (`¹`, `P`, `C`, `*`), excluding vertical excitation arrows above/below, horizontal energy bars underneath, or nearby colored arrow glows.
- **Circular Nodes Connected to Incoming/Outgoing Arrows (e.g., `CE`, `CR`)**:
  Do not include the black reaction arrows entering or leaving the circle. Measure the center of the text inside the circle (`CE` or `CR`) and the radius of the circular ring/halo (`r`), then construct a square pixel window `[cx - r, cy - r, cx + r, cy + r]` with symmetric padding.
- **Multi-Line Bracketed Groups (e.g., `"Solvent cage" + "¹[Qᵒˣ ... PCʳᵉᵈ]"`)**:
  Ensure `--window` captures both the superscript (`¹` or `³`) on the far left and the closing bracket (`]`) on the far right without touching adjacent curved arrows.
- **Colored Data Traces & Data Points in Plots (e.g., Figure 2)**:
  Use `--channel blue` or `--channel red` to isolate colored kinetic traces or individual colored scatter points in an inset without picking up black axis ticks or neighboring points.

---

### Step 3: Mandatory Self-Verification via Visual Centering Audit Sheet

Before delivering annotations or updating the notebook, you **must** generate and visually inspect a **Visual Centering Audit Contact Sheet**.

Save your candidate annotations list to a JSON file (e.g., `/tmp/annotations.json`) and run:

```bash
uv run scripts/figure_annotation_helper.py audit \
  --image resources/figures/fig1.webp \
  --annotations /tmp/annotations.json \
  --output /tmp/centering_audit_sheet.png
```

Read `/tmp/centering_audit_sheet.png` with your multimodal image reader (`read_file`) and inspect **every tile**:
1. Each tile displays a zoomed crop of one annotated element, its blue bounding box, and a **red crosshair (`+`)** at the exact center of the box.
2. **Pass Criteria**:
   - The red crosshair `+` lands directly on the visual center of the target element (e.g., the center stem of `P` in `¹PC*`/`³PC*`, between `C` and `E` in circular `CE` nodes, or the center of a data point/trace).
   - Left/right and top/bottom padding around the element are visually symmetrical.
   - No part of the target glyph, closing bracket `]`, or circle halo is clipped by the blue box.
3. **If any tile fails**: Adjust that element's isolation window or circle center, re-run `audit`, and re-inspect the image before proceeding.

---

### Step 4: Render in Marimo with `FigureAnnotatorWidget`

Import `FigureAnnotatorWidget` in the import cell. Instantiate each figure in its own cell with the code hidden: the reader sees the tour, not the coordinates. Load the figure image, set `.caption`, assign the verified `.annotations` and `.tour_steps`, return the widget, and validate the notebook. The cell below is one figure. A later cell puts every figure in the single tab box from [One tab box](#one-tab-box).

```python
@app.cell(hide_code=True)
def _(FigureAnnotatorWidget, Path):
    annotator = FigureAnnotatorWidget()
    annotator.load_image_from_path(Path("resources/figures/fig1.webp"))
    annotator.caption = "Fig. 1. (A) Spin-dependent pathways..."

    annotator.annotations = [
        {
            "id": "ground_state",
            "label": "¹PC (Ground S₀)",
            "box": [35.56, 43.19, 5.44, 5.47],
            "color": "#0284c7",
            "description": "Unexcited ground state",
        },
        # ...
    ]

    annotator.tour_steps = [
        {
            "title": "1. Ground State vs. Singlet Excitation",
            "target_ids": ["ground_state", "absorption", "singlet_excited"],
            "html": (
                '<p>The unexcited catalyst begins at '
                '<a class="fig-ref" data-target="ground_state">¹PC Ground State (S₀)</a>...</p>'
            ),
        },
        # ...
    ]
    return (annotator,)


@app.cell(hide_code=True)
def _(fig1_annotator, fig2_annotator, mo, wigglystuff):
    wigglystuff.FloatingPanel(
        mo.ui.tabs(
            {
                "Figure 1. States, cage, catalyst, quenchers": fig1_annotator,
                "Figure 2. 450 nm traces and the yield inset": fig2_annotator,
            }
        ),
        title="Figures 1–2",
        corner="bottom-right",
        width=880,
    )
```

Validate the generated Marimo notebook before handoff:

```bash
uv run scripts/validate_notebook.py resources/figure_annotator_example.py --run
```

---

## Widget CSS & Layout Footguns to Avoid

1. **Floating Badge Pill Height (`line-height: 0` inheritance)**:
   - `.stage-container` uses `line-height: 0` so the `<img>` element has no extra baseline gap underneath.
   - `.annot-badge` lives inside `.stage-container` and **must** explicitly set `line-height: 1.35; display: inline-flex; align-items: center; padding: 4px 10px;`—otherwise it inherits `line-height: 0` and its colored background collapses into a thin strip while the label text overflows top and bottom.
2. **Edge-Aware Badge Placement**:
   - When an annotation sits near the top edge of the figure (`y < 6%`), flip `.annot-badge` below the box (`top: calc(100% + 5px); bottom: auto;`) so the pill is not clipped by the top border.
   - When an annotation sits near the left edge (`x + w/2 < 12%`, such as a vertical y-axis label) or right edge (`x + w/2 > 88%`), anchor `.annot-badge` inward (`left: 0; transform: none;` or `right: 0; left: auto; transform: none;`) so long labels never clip horizontally.
