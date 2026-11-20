# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "marimo",
#     "anywidget",
#     "traitlets",
#     "pillow",
# ]
# ///

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import base64
    from pathlib import Path
    from typing import List, Optional
    import anywidget
    import marimo as mo
    import traitlets

    return List, Optional, Path, anywidget, base64, mo, traitlets


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 🎯 Dynamic Figure Annotation Widget (`FigureAnnotatorWidget`)

    An interactive **AnyWidget** for guided figure walkthroughs in Marimo notebooks.

    Overlays use **100×100 percentage slice coordinates** (`[left%, top%, width%, height%]`). They stay aligned when the browser viewport changes size.

    Hover badges next to `.fig-ref` links match the color of the matching overlay box.

    Overlay boxes stay hidden at rest, so the figure is not cluttered. They light up on hover. Clicking a box jumps to its tour step.

    Layout from top to bottom: step navigator, then explanation card, then the interactive diagram, then the original figure caption.

    **One tab box**: a paper notebook puts every main-text figure in a single `mo.ui.tabs`, one tab per figure. The two tabs below are that box.
    """)
    return


@app.cell(hide_code=True)
def _(List, Optional, Path, anywidget, base64, traitlets):
    ESM_CODE = """
    export function render({ model, el }) {
        el.innerHTML = `
            <div class="annotator-container">
                <div class="tour-toolbar">
                    <div class="tour-nav">
                        <button class="nav-btn prev-btn" title="Previous Step">◀ Prev</button>
                        <span class="step-counter">Step 1 of 1</span>
                        <button class="nav-btn next-btn" title="Next Step">Next ▶</button>
                    </div>
                    <div class="tour-step-title"></div>
                    <div class="jit-hint">💡 Hover badges or diagram elements • Click any diagram box to jump to its step</div>
                </div>

                <div class="explanation-card">
                    <div class="explanation-content"></div>
                </div>

                <div class="stage-container">
                    <img class="base-image" src="" alt="Figure" />
                    <div class="overlay-stage"></div>
                </div>

                <div class="caption-card">
                    <div class="caption-label">📄 Original Figure Caption</div>
                    <div class="caption-content"></div>
                </div>
            </div>
        `;

        const imgEl = el.querySelector(".base-image");
        const overlayStage = el.querySelector(".overlay-stage");
        const prevBtn = el.querySelector(".prev-btn");
        const nextBtn = el.querySelector(".next-btn");
        const stepCounter = el.querySelector(".step-counter");
        const stepTitle = el.querySelector(".tour-step-title");
        const explanationContent = el.querySelector(".explanation-content");
        const captionCard = el.querySelector(".caption-card");
        const captionContent = el.querySelector(".caption-content");

        let activeHoverId = null;

        function getAnnotMap() {
            const annotations = model.get("annotations") || [];
            const map = {};
            annotations.forEach(a => {
                if (a && a.id) {
                    map[a.id] = a;
                }
            });
            return map;
        }

        function updateImage() {
            const src = model.get("image_src") || "";
            imgEl.setAttribute("src", src);
        }

        function updateCaption() {
            const cap = (model.get("caption") || "").trim();
            if (cap) {
                captionCard.style.display = "block";
                captionContent.textContent = cap;
            } else {
                captionCard.style.display = "none";
            }
        }

        function findStepsForAnnotation(annotId) {
            const steps = model.get("tour_steps") || [];
            const matching = [];
            steps.forEach((step, idx) => {
                const targets = step.target_ids || step.focus_ids || [];
                const html = step.html || step.commentary || "";
                if (targets.includes(annotId) || html.includes(`data-target="${annotId}"`)) {
                    matching.push(idx);
                }
            });
            return matching;
        }

        function renderOverlays() {
            overlayStage.innerHTML = "";
            const annotations = model.get("annotations") || [];

            annotations.forEach(annot => {
                const [x, y, w, h] = annot.box || [0, 0, 0, 0];
                const color = annot.color || "#3b82f6";

                const box = document.createElement("div");
                box.className = "annot-box";
                box.setAttribute("data-id", annot.id);
                box.style.left = `${x}%`;
                box.style.top = `${y}%`;
                box.style.width = `${w}%`;
                box.style.height = `${h}%`;

                const visuals = document.createElement("div");
                visuals.className = "annot-visuals";
                visuals.style.borderColor = color;
                visuals.style.backgroundColor = `${color}28`;
                visuals.style.boxShadow = `0 0 10px ${color}99`;

                const badge = document.createElement("div");
                badge.className = "annot-badge";
                badge.style.backgroundColor = color;
                badge.textContent = annot.label || annot.id;

                if (y < 6) {
                    badge.style.top = "calc(100% + 5px)";
                    badge.style.bottom = "auto";
                }

                const centerX = x + (w / 2);
                if (centerX < 12) {
                    badge.style.left = "0";
                    badge.style.transform = "none";
                } else if (centerX > 88) {
                    badge.style.left = "auto";
                    badge.style.right = "0";
                    badge.style.transform = "none";
                }

                visuals.appendChild(badge);
                box.appendChild(visuals);

                box.addEventListener("mouseenter", () => {
                    activeHoverId = annot.id;
                    highlightBoxes(annot.id);
                    highlightLinks(annot.id);
                });

                box.addEventListener("mouseleave", () => {
                    if (activeHoverId === annot.id) {
                        activeHoverId = null;
                        unhighlightAll();
                    }
                });

                box.addEventListener("click", (e) => {
                    e.stopPropagation();
                    const matchingSteps = findStepsForAnnotation(annot.id);
                    if (matchingSteps.length === 0) return;

                    const currentStep = model.get("active_step") || 0;
                    let targetStep = matchingSteps[0];
                    if (matchingSteps.includes(currentStep)) {
                        const pos = matchingSteps.indexOf(currentStep);
                        targetStep = matchingSteps[(pos + 1) % matchingSteps.length];
                    }

                    if (targetStep !== currentStep) {
                        model.set("active_step", targetStep);
                        model.save_changes();
                        renderExplanation();
                    }
                    activeHoverId = annot.id;
                    highlightBoxes(annot.id);
                    highlightLinks(annot.id);
                });

                overlayStage.appendChild(box);
            });
        }

        function renderExplanation() {
            const steps = model.get("tour_steps") || [];
            const stepIdx = model.get("active_step") || 0;

            if (steps.length === 0) {
                stepCounter.textContent = "Overview";
                stepTitle.textContent = "Figure Analysis";
                explanationContent.innerHTML = "<p>No active tour steps defined.</p>";
                prevBtn.disabled = true;
                nextBtn.disabled = true;
                return;
            }

            const currentStep = steps[stepIdx] || steps[0];
            stepCounter.textContent = `Step ${stepIdx + 1} of ${steps.length}`;
            stepTitle.textContent = currentStep.title || `Phase ${stepIdx + 1}`;
            explanationContent.innerHTML = currentStep.html || currentStep.commentary || "<p></p>";

            prevBtn.disabled = (stepIdx === 0);
            nextBtn.disabled = (stepIdx === steps.length - 1);

            attachLinkListeners();
        }

        function attachLinkListeners() {
            const annotMap = getAnnotMap();
            const links = explanationContent.querySelectorAll(".fig-ref");
            links.forEach(link => {
                const targetId = link.getAttribute("data-target");
                const annot = annotMap[targetId];
                const color = (annot && annot.color) ? annot.color : "#2563eb";

                link.style.setProperty("--ref-color", color);
                link.style.setProperty("--ref-bg", `${color}18`);
                link.style.setProperty("--ref-border", `${color}88`);
                link.style.setProperty("--ref-shadow", `${color}66`);

                link.addEventListener("mouseenter", () => {
                    activeHoverId = targetId;
                    highlightBoxes(targetId);
                    link.classList.add("link-active");
                });
                link.addEventListener("mouseleave", () => {
                    if (activeHoverId === targetId) {
                        activeHoverId = null;
                        unhighlightAll();
                    }
                });
            });
        }

        function highlightBoxes(id) {
            const boxes = overlayStage.querySelectorAll(".annot-box");
            boxes.forEach(b => {
                if (b.getAttribute("data-id") === id) {
                    b.classList.add("visible");
                } else {
                    b.classList.remove("visible");
                }
            });
        }

        function unhighlightAll() {
            const boxes = overlayStage.querySelectorAll(".annot-box");
            boxes.forEach(b => b.classList.remove("visible"));
            const links = explanationContent.querySelectorAll(".link-active");
            links.forEach(l => l.classList.remove("link-active"));
        }

        function highlightLinks(id) {
            const links = explanationContent.querySelectorAll(`[data-target="${id}"]`);
            links.forEach(l => l.classList.add("link-active"));
        }

        prevBtn.addEventListener("click", () => {
            const current = model.get("active_step") || 0;
            if (current > 0) {
                model.set("active_step", current - 1);
                model.save_changes();
            }
        });

        nextBtn.addEventListener("click", () => {
            const current = model.get("active_step") || 0;
            const steps = model.get("tour_steps") || [];
            if (current < steps.length - 1) {
                model.set("active_step", current + 1);
                model.save_changes();
            }
        });

        model.on("change:image_src", updateImage);
        model.on("change:caption", updateCaption);
        model.on("change:annotations", () => {
            renderOverlays();
            renderExplanation();
        });
        model.on("change:tour_steps", () => {
            renderExplanation();
            renderOverlays();
        });
        model.on("change:active_step", () => {
            renderExplanation();
            if (activeHoverId) {
                highlightBoxes(activeHoverId);
                highlightLinks(activeHoverId);
            }
        });

        updateImage();
        updateCaption();
        renderOverlays();
        renderExplanation();
    }
    """

    CSS_CODE = """
    .annotator-container {
        display: flex;
        flex-direction: column;
        gap: 12px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 14px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }

    .tour-toolbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #f8fafc;
        padding: 8px 14px;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        flex-wrap: wrap;
        gap: 8px;
    }

    .tour-nav {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .nav-btn {
        background: #2563eb;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 5px 12px;
        font-size: 13px;
        font-weight: 600;
        cursor: pointer;
        transition: background 0.15s ease;
    }

    .nav-btn:hover:not(:disabled) {
        background: #1d4ed8;
    }

    .nav-btn:disabled {
        background: #cbd5e1;
        cursor: not-allowed;
    }

    .step-counter {
        font-size: 13px;
        font-weight: 600;
        color: #475569;
    }

    .tour-step-title {
        font-size: 14px;
        font-weight: 700;
        color: #0f172a;
    }

    .jit-hint {
        font-size: 12px;
        font-weight: 500;
        color: #64748b;
    }

    .explanation-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 12px 14px;
        font-size: 14px;
        color: #1e293b;
        line-height: 1.65;
    }

    .explanation-content p {
        margin: 0;
    }

    .fig-ref {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        background: var(--ref-bg, #eff6ff);
        color: var(--ref-color, #2563eb);
        border: 1.5px solid var(--ref-border, #bfdbfe);
        padding: 1px 8px;
        border-radius: 5px;
        font-weight: 700;
        font-size: 13px;
        cursor: pointer;
        text-decoration: none;
        transition: all 0.15s ease;
    }

    .fig-ref:hover, .fig-ref.link-active {
        background: var(--ref-color, #2563eb);
        color: #ffffff;
        border-color: var(--ref-color, #1d4ed8);
        box-shadow: 0 0 10px var(--ref-shadow, rgba(37, 99, 235, 0.4));
        transform: translateY(-1px);
    }

    .stage-container {
        position: relative;
        width: 100%;
        border-radius: 8px;
        overflow: hidden;
        background: #f8fafc;
        border: 1px solid #cbd5e1;
        line-height: 0;
    }

    .base-image {
        width: 100%;
        height: auto;
        display: block;
        user-select: none;
    }

    .overlay-stage {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
    }

    .annot-box {
        position: absolute;
        box-sizing: border-box;
        cursor: pointer;
        pointer-events: auto;
    }

    .annot-visuals {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        border: 2.5px dashed;
        border-radius: 6px;
        box-sizing: border-box;
        opacity: 0;
        transition: opacity 0.18s ease;
        pointer-events: none;
    }

    .annot-box.visible .annot-visuals {
        opacity: 1 !important;
    }

    .annot-badge {
        position: absolute;
        bottom: calc(100% + 6px);
        left: 50%;
        transform: translateX(-50%);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 12px;
        line-height: 1.35;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 6px;
        white-space: nowrap;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.35);
        pointer-events: none;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    .caption-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 3.5px solid #64748b;
        border-radius: 6px;
        padding: 10px 14px;
        font-size: 13px;
        color: #334155;
        line-height: 1.55;
    }

    .caption-label {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: #64748b;
        margin-bottom: 4px;
    }

    .caption-content {
        color: #1e293b;
    }
    """

    class FigureAnnotatorWidget(anywidget.AnyWidget):
        """AnyWidget for interactive, 100-slice scale-invariant figure annotation tours with JIT spotlights."""

        _esm = ESM_CODE
        _css = CSS_CODE

        image_src = traitlets.Unicode("").tag(sync=True)
        caption = traitlets.Unicode("").tag(sync=True)
        annotations = traitlets.List([]).tag(sync=True)
        tour_steps = traitlets.List([]).tag(sync=True)
        active_step = traitlets.Int(0).tag(sync=True)

        def load_image_from_path(self, path: Path) -> None:
            """Load an image file and convert to base64 data URI."""
            if not path.exists():
                return

            suffix = path.suffix.lower()
            if suffix == ".webp":
                mime = "image/webp"
            elif suffix in (".jpg", ".jpeg"):
                mime = "image/jpeg"
            else:
                mime = "image/png"
            b64_data = base64.b64encode(path.read_bytes()).decode("utf-8")
            self.image_src = f"data:{mime};base64,{b64_data}"

        def add_annotation(
            self,
            id: str,
            label: str,
            box: List[float],
            color: str = "#3b82f6",
            description: str = "",
        ) -> None:
            annots = list(self.annotations)
            annots.append(
                {
                    "id": id,
                    "label": label,
                    "box": box,
                    "color": color,
                    "description": description,
                }
            )
            self.annotations = annots

        def add_tour_step(
            self, title: str, html: str, target_ids: Optional[List[str]] = None
        ) -> None:
            steps = list(self.tour_steps)
            steps.append(
                {
                    "title": title,
                    "html": html,
                    "target_ids": target_ids or [],
                }
            )
            self.tour_steps = steps

    return (FigureAnnotatorWidget,)


@app.cell(hide_code=True)
def _(FigureAnnotatorWidget, Path, mo):
    _base_dir = Path(__file__).resolve().parent / "figures"

    # =========================================================================
    # 1. FIGURE 1 ANNOTATOR (All Panels: A, B, and C)
    # =========================================================================
    fig1_annotator = FigureAnnotatorWidget()
    fig1_annotator.load_image_from_path(_base_dir / "fig1.webp")
    fig1_annotator.caption = (
        "Fig. 1. (A) Spin-dependent pathways following excitation of a general TADF "
        "photocatalyst (PC), showing competition between S₁ and T₁ quenching and, "
        "after electron transfer, between cage escape (CE) and geminate charge "
        "recombination (CR). (B) Selected TADF photocatalyst (PC²⁺) and relevant "
        "photophysical characteristics in acetonitrile solution. (C) Quenchers used "
        "as electron donors and their oxidation potentials."
    )

    fig1_annotator.annotations = [
        {
            "id": "ground_state",
            "label": "¹PC (Ground S₀)",
            "box": [35.56, 43.19, 5.44, 5.47],
            "color": "#0284c7",
            "description": "Unexcited ground state",
        },
        {
            "id": "absorption",
            "label": "hν (Light Excitation)",
            "box": [37.5, 14.15, 1.94, 30.12],
            "color": "#0d9488",
            "description": "Photon absorption S₀ → S₁",
        },
        {
            "id": "singlet_excited",
            "label": "¹PC* (Singlet S₁)",
            "box": [36.25, 6.86, 6.69, 5.68],
            "color": "#e11d48",
            "description": "Short-lived singlet excited state",
        },
        {
            "id": "triplet_excited",
            "label": "³PC* (Triplet T₁)",
            "box": [51.38, 10.18, 6.75, 5.68],
            "color": "#2563eb",
            "description": "Lower-energy triplet excited state",
        },
        {
            "id": "isc_risc",
            "label": "k_ISC ⇄ k_rISC (TADF)",
            "box": [43.56, 6.43, 7.31, 16.61],
            "color": "#9333ea",
            "description": "Thermal equilibrium between S₁ and T₁",
        },
        {
            "id": "singlet_quenching",
            "label": "¹[Qᵒˣ ... PCʳᵉᵈ] (Singlet Pair)",
            "box": [14.12, 18.65, 15.75, 8.57],
            "color": "#dc2626",
            "description": "Solvent-caged singlet radical pair",
        },
        {
            "id": "triplet_quenching",
            "label": "³[Qᵒˣ ... PCʳᵉᵈ] (Triplet Pair)",
            "box": [49.88, 20.15, 15.75, 8.25],
            "color": "#7c3aed",
            "description": "Solvent-caged triplet radical pair",
        },
        {
            "id": "cage_escape_left",
            "label": "CE (Singlet Cage Escape)",
            "box": [17.03, 25.99, 6.12, 10.5],
            "color": "#059669",
            "description": "Radicals separate into solution",
        },
        {
            "id": "cage_escape_right",
            "label": "CE (Triplet Cage Escape)",
            "box": [62.38, 26.53, 6.12, 10.5],
            "color": "#0d9488",
            "description": "Radicals separate into solution",
        },
        {
            "id": "cr_left",
            "label": "CR (Spin-Allowed Recombination)",
            "box": [27.06, 32.37, 6.12, 10.5],
            "color": "#ea580c",
            "description": "Fast spin-allowed back electron transfer",
        },
        {
            "id": "cr_right",
            "label": "CR (Spin-Forbidden Recombination)",
            "box": [49.25, 28.89, 6.12, 10.5],
            "color": "#d97706",
            "description": "Slow spin-forbidden back electron transfer",
        },
        {
            "id": "pc_structure",
            "label": "PC²⁺ Structure (2 SbF₆⁻)",
            "box": [0.25, 61.52, 19.88, 38.2],
            "color": "#0284c7",
            "description": "Dicationic acridinium-imidazolium TADF photocatalyst",
        },
        {
            "id": "pc_redox_s1",
            "label": "E(¹*PC²⁺|PC•⁺) = +2.0 V vs SCE",
            "box": [20.62, 69.88, 24.94, 4.82],
            "color": "#e11d48",
            "description": "Singlet excited-state reduction potential",
        },
        {
            "id": "pc_redox_t1",
            "label": "E(³*PC²⁺|PC•⁺) = +1.8 V vs SCE",
            "box": [20.62, 75.13, 24.94, 4.93],
            "color": "#2563eb",
            "description": "Triplet excited-state reduction potential",
        },
        {
            "id": "pc_lifetimes",
            "label": "τ₀,S = 17 ns vs. τ₀,T = 44 μs",
            "box": [28.38, 81.35, 9.5, 10.5],
            "color": "#059669",
            "description": "T₁ lives ~2,600× longer than S₁",
        },
        {
            "id": "pc_phi_isc",
            "label": "Φ_isc = 0.68 (ISC Yield)",
            "box": [28.5, 92.5, 9.25, 4.82],
            "color": "#9333ea",
            "description": "68% of S₁ undergoes intersystem crossing to T₁ in the absence of quencher",
        },
        {
            "id": "quencher_np",
            "label": "Naphthalene (Np, +1.61 V)",
            "box": [50.75, 65.06, 17.44, 26.8],
            "color": "#dc2626",
            "description": "Aromatic electron donor with E_ox = +1.61 V vs SCE",
        },
        {
            "id": "quencher_tbuphoh",
            "label": "4-(tert-butyl)phenol (+1.65 V)",
            "box": [68.56, 64.95, 28.5, 26.26],
            "color": "#7c3aed",
            "description": "Phenolic electron donor with E_ox = +1.65 V vs SCE",
        },
    ]

    fig1_annotator.tour_steps = [
        {
            "title": "1. Panel A: Ground State vs. Singlet Excitation",
            "target_ids": ["ground_state", "absorption", "singlet_excited"],
            "html": '<p>Hover over the color-matched badges or diagram elements to spotlight them (or click any box on the figure to jump to its step)! The unexcited catalyst begins at <a class="fig-ref" data-target="ground_state">¹PC Ground State (S₀)</a> at the bottom. Light absorption (<a class="fig-ref" data-target="absorption">hν</a>) promotes it upward to the <a class="fig-ref" data-target="singlet_excited">¹PC* Singlet Excited State (S₁)</a>.</p>',
        },
        {
            "title": "2. Panel A: TADF Equilibrium (k_ISC ⇄ k_rISC)",
            "target_ids": ["singlet_excited", "triplet_excited", "isc_risc"],
            "html": '<p>In a TADF catalyst, the energy gap between <a class="fig-ref" data-target="singlet_excited">¹PC* (Singlet)</a> and <a class="fig-ref" data-target="triplet_excited">³PC* (Triplet)</a> is small (only 0.2 eV). They interconvert via <a class="fig-ref" data-target="isc_risc">k_ISC and k_rISC</a>.</p>',
        },
        {
            "title": "3. Panel A: Singlet vs. Triplet Solvent Cages",
            "target_ids": ["singlet_quenching", "triplet_quenching"],
            "html": '<p>Quenching by electron donor Q produces a solvent-caged radical pair. Electron transfer from S₁ forms the <a class="fig-ref" data-target="singlet_quenching">¹[Qᵒˣ ... PCʳᵉᵈ] Singlet Pair</a>. Electron transfer from T₁ forms the <a class="fig-ref" data-target="triplet_quenching">³[Qᵒˣ ... PCʳᵉᵈ] Triplet Pair</a>.</p>',
        },
        {
            "title": "4. Panel A: Cage Escape (CE) vs. Charge Recombination (CR)",
            "target_ids": [
                "cage_escape_left",
                "cage_escape_right",
                "cr_left",
                "cr_right",
            ],
            "html": '<p>Each solvent cage has two competing fates.</p><p><a class="fig-ref" data-target="cage_escape_left">CE from the singlet</a> and <a class="fig-ref" data-target="cage_escape_right">CE from the triplet</a>: the radicals separate into bulk solution.</p><p><a class="fig-ref" data-target="cr_left">CR from the singlet</a> is spin-allowed, so it wastes energy back to the ground state quickly.</p><p><a class="fig-ref" data-target="cr_right">CR from the triplet</a> is spin-forbidden. Back-electron transfer is slow, which gives the radicals time to leave the cage.</p>',
        },
        {
            "title": "5. Panel B: Photocatalyst Structure, Redox & Lifetimes",
            "target_ids": [
                "pc_structure",
                "pc_redox_s1",
                "pc_redox_t1",
                "pc_lifetimes",
                "pc_phi_isc",
            ],
            "html": '<p>Panel B details the dicationic <a class="fig-ref" data-target="pc_structure">PC²⁺ catalyst structure</a> in acetonitrile.</p><p>Both <a class="fig-ref" data-target="pc_redox_s1">S₁ (+2.0 V vs SCE)</a> and <a class="fig-ref" data-target="pc_redox_t1">T₁ (+1.8 V vs SCE)</a> are strong oxidants, separated by just 0.2 V.</p><p>Look at the <a class="fig-ref" data-target="pc_lifetimes">excited-state lifetimes (17 ns vs 44 μs)</a>: T₁ lives <b>~2,600× longer</b> than S₁ and forms with <a class="fig-ref" data-target="pc_phi_isc">Φ_isc = 0.68</a>, so low quencher concentrations can selectively harvest T₁.</p>',
        },
        {
            "title": "6. Panel C: Electron-Donor Quenchers (Q)",
            "target_ids": [
                "quencher_np",
                "quencher_tbuphoh",
                "pc_redox_s1",
                "pc_redox_t1",
            ],
            "html": '<p>Panel C introduces the two sacrificial electron donors: <a class="fig-ref" data-target="quencher_np">Naphthalene (Np, +1.61 V)</a> and <a class="fig-ref" data-target="quencher_tbuphoh">4-(tert-butyl)phenol (+1.65 V)</a>. Because both oxidation potentials (+1.61 V and +1.65 V) sit well below the catalyst reduction potentials of <a class="fig-ref" data-target="pc_redox_s1">S₁ (+2.0 V)</a> and <a class="fig-ref" data-target="pc_redox_t1">T₁ (+1.8 V)</a>, photoinduced electron transfer is thermodynamically favorable from <b>both</b> spin states.</p>',
        },
    ]

    # =========================================================================
    # 2. FIGURE 2 ANNOTATOR (Main Transient Absorption & Inset Quantum Yield)
    # =========================================================================
    fig2_annotator = FigureAnnotatorWidget()
    fig2_annotator.load_image_from_path(_base_dir / "fig2.webp")
    fig2_annotator.caption = (
        "Fig. 2. Time-resolved absorption traces recorded at λ = 450 nm, corresponding "
        "to PC•⁺ generated via photoinduced electron transfer, upon 355 nm laser "
        "excitation (5.5 mJ per pulse) of two iso-absorbing acetonitrile solutions "
        "containing 5 μM PC²⁺ and different concentrations of 4-tbuPhOH. Inset: "
        "measured quantum yields for free radical production as function of quencher "
        "concentration."
    )

    fig2_annotator.annotations = [
        {
            "id": "y_axis_main",
            "label": "ΔA at 450 nm (Tracks Free PC•⁺)",
            "box": [0.25, 25.93, 3.81, 31.79],
            "color": "#0284c7",
            "description": "Transient absorbance at 450 nm proportional to escaped PC•⁺ radical concentration",
        },
        {
            "id": "x_axis_main",
            "label": "t / μs (Time After Laser Flash)",
            "box": [54.19, 94.15, 9.81, 5.6],
            "color": "#0d9488",
            "description": "Microsecond timescale following 355 nm laser excitation",
        },
        {
            "id": "legend_box",
            "label": "Quencher Concentrations (13 mM vs 0.3 mM)",
            "box": [18.81, 4.31, 21.25, 13.58],
            "color": "#7c3aed",
            "description": "Comparison of high (13 mM, red) vs low (0.3 mM, blue) 4-tbuPhOH concentration",
        },
        {
            "id": "blue_trace",
            "label": "0.3 mM Trace (T₁ Quenching → High Yield)",
            "box": [39.38, 13.82, 59.06, 15.77],
            "color": "#0284c7",
            "description": "At 0.3 mM, slow μs rise via T₁ (Φ_q,T = 0.65) yields a high ΔA ≈ 0.023 plateau",
        },
        {
            "id": "red_trace",
            "label": "13 mM Trace (S₁ Quenching → Low Yield)",
            "box": [19.5, 53.82, 22.88, 16.02],
            "color": "#dc2626",
            "description": "At 13 mM, fast ns quenching of S₁ yields less than half the free radicals (ΔA ≈ 0.009)",
        },
        {
            "id": "inset_y_axis",
            "label": "Φ_r,tot (Total Radical Quantum Yield)",
            "box": [41.5, 49.67, 4.06, 9.11],
            "color": "#9333ea",
            "description": "Total quantum yield of cage-escaped free radicals",
        },
        {
            "id": "inset_x_axis",
            "label": "[Q] / M (4-tbuPhOH Concentration)",
            "box": [68.12, 81.71, 9.81, 5.12],
            "color": "#0d9488",
            "description": "Molar concentration of 4-tbuPhOH quencher from 0 to 0.18 M",
        },
        {
            "id": "inset_blue_pt",
            "label": "0.3 mM Point (Φ_r,tot ≈ 0.28 via T₁)",
            "box": [49.5, 35.53, 3.62, 4.8],
            "color": "#0284c7",
            "description": "Peak radical quantum yield at low quencher concentration (matches blue trace)",
        },
        {
            "id": "inset_red_pt",
            "label": "13 mM Point (Φ_r,tot ≈ 0.13 via S₁/T₁)",
            "box": [54.75, 55.37, 3.62, 4.88],
            "color": "#dc2626",
            "description": "Reduced quantum yield at 13 mM (matches red trace)",
        },
        {
            "id": "inset_high_q_decay",
            "label": "High-[Q] Regime (0.02–0.18 M → S₁ Takeover)",
            "box": [58.69, 57.24, 35.88, 17.15],
            "color": "#d97706",
            "description": "Increasing [Q] progressively intercepts S₁ before ISC, lowering Φ_r,tot to ~0.04",
        },
    ]

    fig2_annotator.tour_steps = [
        {
            "title": "1. Tracking Escaped Radicals via Transient Absorption",
            "target_ids": ["y_axis_main", "x_axis_main", "legend_box"],
            "html": '<p>Following a 355 nm laser pulse, the main plot records <a class="fig-ref" data-target="y_axis_main">ΔA at 450 nm</a> over <a class="fig-ref" data-target="x_axis_main">t / μs (Microseconds)</a>. Because the reduced catalyst radical (<b>PC•⁺</b>) absorbs strongly at 450 nm, the plateau height directly measures how many radicals escaped the solvent cage under the two <a class="fig-ref" data-target="legend_box">Quencher Concentrations (13 mM vs 0.3 mM)</a>.</p>',
        },
        {
            "title": "2. The Concentration Paradox: 0.3 mM (Blue) vs. 13 mM (Red)",
            "target_ids": ["blue_trace", "red_trace", "legend_box"],
            "html": '<p>Compare the two kinetic traces.</p><p>The <a class="fig-ref" data-target="blue_trace">0.3 mM blue trace (low [Q])</a> rises gradually over ~2 μs, from diffusional quenching of long-lived <b>T₁</b>, to a high plateau (<b>ΔA ≈ 0.023</b>).</p><p>The <a class="fig-ref" data-target="red_trace">13 mM red trace (43× higher [Q])</a> rises immediately within the laser pulse, intercepting short-lived <b>S₁</b>. It still reaches less than half the signal (<b>ΔA ≈ 0.009</b>), because singlet radical pairs recombine quickly by spin-allowed charge recombination.</p>',
        },
        {
            "title": "3. Connecting the Kinetic Traces to the Inset Quantum Yields",
            "target_ids": [
                "inset_y_axis",
                "inset_x_axis",
                "inset_blue_pt",
                "inset_red_pt",
            ],
            "html": '<p>The inset plots <a class="fig-ref" data-target="inset_y_axis">Φ_r,tot (free-radical quantum yield)</a> against <a class="fig-ref" data-target="inset_x_axis">[Q] / M (quencher molarity)</a>.</p><p>The <a class="fig-ref" data-target="inset_blue_pt">blue data point (0.3 mM)</a> sits near the maximum quantum yield (<b>Φ_r,tot ≈ 0.28</b>), matching the blue trace.</p><p>The <a class="fig-ref" data-target="inset_red_pt">red data point (13 mM)</a> drops to <b>Φ_r,tot ≈ 0.13</b>, matching the red trace.</p>',
        },
        {
            "title": "4. High-[Q] Regime: Singlet Interception Outcompetes ISC",
            "target_ids": ["inset_high_q_decay", "inset_blue_pt", "inset_red_pt"],
            "html": '<p>As quencher concentration increases across the <a class="fig-ref" data-target="inset_high_q_decay">High-[Q] Regime (0.02 M to 0.18 M)</a>, bimolecular collisions with <b>¹PC*</b> become faster than intersystem crossing (k_ISC). Consequently, quenching shifts from the productive triplet channel (<a class="fig-ref" data-target="inset_blue_pt">0.3 mM Peak</a>) through the intermediate crossover (<a class="fig-ref" data-target="inset_red_pt">13 mM</a>) toward the low-efficiency singlet channel (Φ_r,tot → 0.04).</p>',
        },
    ]

    annotator_tabs = mo.ui.tabs(
        {
            "📊 Figure 1: Full Mechanism, Catalyst & Quenchers (Panels A–C)": fig1_annotator,
            "📈 Figure 2: Transient Absorption & Concentration Paradox": fig2_annotator,
        }
    )
    annotator_tabs
    return


if __name__ == "__main__":
    app.run()
