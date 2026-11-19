"""Interactive AnyWidget with 100-slice percentage coordinate tracking, color-matched badges, click-to-step navigation, and JIT spotlights."""

import base64
from pathlib import Path
from typing import List, Optional
import anywidget
import traitlets

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

            // Clickable & hoverable bounding box container in 100-slice % space
            const box = document.createElement("div");
            box.className = "annot-box";
            box.setAttribute("data-id", annot.id);
            box.style.left = `${x}%`;
            box.style.top = `${y}%`;
            box.style.width = `${w}%`;
            box.style.height = `${h}%`;

            // Visual spotlight container (invisible until hovered)
            const visuals = document.createElement("div");
            visuals.className = "annot-visuals";
            visuals.style.borderColor = color;
            visuals.style.backgroundColor = `${color}28`;
            visuals.style.boxShadow = `0 0 10px ${color}99`;

            // Floating badge label
            const badge = document.createElement("div");
            badge.className = "annot-badge";
            badge.style.backgroundColor = color;
            badge.textContent = annot.label || annot.id;

            // If near the very top of figure, flip badge below the box
            if (y < 6) {
                badge.style.top = "calc(100% + 5px)";
                badge.style.bottom = "auto";
            }

            // Prevent horizontal clipping when box center is near left or right edge
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

            // Hover interactions
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

            // Click interaction: jump to the step associated with this box
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

            // Apply color-matched styling via CSS custom properties
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

/* Color-Matched Interactive Hover Badges in Explanation */
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

/* Percentage 100-Slice Stage Container */
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

/* JIT Visibility: Invisible by default */
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

/* Revealed on hover! */
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

/* Original Figure Caption Card below Diagram */
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
