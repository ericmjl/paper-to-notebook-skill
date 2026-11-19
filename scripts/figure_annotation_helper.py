# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow", "numpy"]
# ///
"""CLI helper for dynamic figure annotation: 100x100 % grid overlay, ink/color isolation, and visual centering audit sheets.

Subcommands:
1. grid    - Overlay a 100x100 percentage slice grid (0%..100% horizontally and vertically) on a private copy of a figure.
2. isolate - Isolate foreground ink or specific color-channel segments inside a rough percentage window to compute a centered [left%, top%, width%, height%] bounding box.
3. audit   - Render a Visual Centering Audit Contact Sheet with zoomed crops, bounding boxes, and red center crosshairs (+) for every annotation.

Usage:
    uv run scripts/figure_annotation_helper.py grid --image path/to/fig.webp --output /tmp/fig_grid.png
    uv run scripts/figure_annotation_helper.py isolate --image path/to/fig.webp --window 50,9,60,16 --channel any --pad-x 12 --pad-y 9 --output /tmp/box.json
    uv run scripts/figure_annotation_helper.py audit --image path/to/fig.webp --annotations path/to/annotations.json --output /tmp/audit_sheet.png
"""

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


def cmd_grid(args: argparse.Namespace) -> int:
    img_path = Path(args.image)
    if not img_path.is_file():
        print(f"Error: Image not found at {img_path}", file=sys.stderr)
        return 1

    img = Image.open(img_path).convert("RGB")
    w, h = img.size
    draw = ImageDraw.Draw(img)

    for i in range(101):
        px = int(round(w * i / 100.0))
        if i % 10 == 0:
            color, width = (255, 0, 0), 2
        elif i % 5 == 0:
            color, width = (0, 180, 0), 1
        else:
            color, width = (220, 220, 220), 1
        draw.line([(px, 0), (px, h)], fill=color, width=width)
        if i % 5 == 0:
            draw.text((px + 2, 5), f"{i}%", fill=color)
            draw.text((px + 2, int(h * 0.48)), f"{i}%", fill=color)

    for j in range(101):
        py = int(round(h * j / 100.0))
        if j % 10 == 0:
            color, width = (255, 0, 0), 2
        elif j % 5 == 0:
            color, width = (0, 180, 0), 1
        else:
            color, width = (220, 220, 220), 1
        draw.line([(0, py), (w, py)], fill=color, width=width)
        if j % 5 == 0:
            draw.text((5, py + 2), f"{j}%", fill=color)
            draw.text((int(w * 0.5), py + 2), f"{j}%", fill=color)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    print(f"Saved 100x100 percentage slice grid image ({w}x{h}) to {out_path}")
    return 0


def cmd_isolate(args: argparse.Namespace) -> int:
    img_path = Path(args.image)
    if not img_path.is_file():
        print(f"Error: Image not found at {img_path}", file=sys.stderr)
        return 1

    try:
        x1_pct, y1_pct, x2_pct, y2_pct = [float(v.strip()) for v in args.window.split(",")]
    except ValueError:
        print("Error: --window must be 4 comma-separated numbers: x1,y1,x2,y2 (in %)", file=sys.stderr)
        return 1

    img = Image.open(img_path).convert("RGB")
    w, h = img.size
    arr = np.array(img)

    px1 = max(0, min(w - 1, int(round(w * x1_pct / 100.0))))
    px2 = max(px1 + 1, min(w, int(round(w * x2_pct / 100.0))))
    py1 = max(0, min(h - 1, int(round(h * y1_pct / 100.0))))
    py2 = max(py1 + 1, min(h, int(round(h * y2_pct / 100.0))))

    sub = arr[py1:py2, px1:px2]
    thresh = args.threshold

    if args.channel == "any":
        diff = np.max(np.abs(sub.astype(int) - 255), axis=2)
        mask = diff > thresh
    elif args.channel == "black":
        mask = (sub[:, :, 0] < 120) & (sub[:, :, 1] < 120) & (sub[:, :, 2] < 120)
    elif args.channel == "red":
        mask = (sub[:, :, 0].astype(int) - sub[:, :, 2].astype(int)) > thresh
    elif args.channel == "blue":
        mask = (sub[:, :, 2].astype(int) - sub[:, :, 0].astype(int)) > thresh
    else:
        print(f"Error: Unknown channel '{args.channel}'", file=sys.stderr)
        return 1

    rows = np.where(mask.any(axis=1))[0]
    cols = np.where(mask.any(axis=0))[0]

    if len(rows) == 0 or len(cols) == 0:
        print("Error: No matching ink pixels found in the specified window.", file=sys.stderr)
        return 1

    ink_x1 = px1 + int(cols.min())
    ink_x2 = px1 + int(cols.max())
    ink_y1 = py1 + int(rows.min())
    ink_y2 = py1 + int(rows.max())

    cx = (ink_x1 + ink_x2) / 2.0
    cy = (ink_y1 + ink_y2) / 2.0
    bw = (ink_x2 - ink_x1) + 2.0 * args.pad_x
    bh = (ink_y2 - ink_y1) + 2.0 * args.pad_y
    bx = max(0.0, cx - bw / 2.0)
    by = max(0.0, cy - bh / 2.0)

    box_pct = [
        round(bx / w * 100.0, 2),
        round(by / h * 100.0, 2),
        round(bw / w * 100.0, 2),
        round(bh / h * 100.0, 2),
    ]

    result = {
        "window_pct": [x1_pct, y1_pct, x2_pct, y2_pct],
        "channel": args.channel,
        "ink_bounds_px": [ink_x1, ink_y1, ink_x2, ink_y2],
        "center_pct": [round(cx / w * 100.0, 2), round(cy / h * 100.0, 2)],
        "box": box_pct,
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2) + "\n")
    print(f"Isolated centered percentage box {box_pct} -> saved to {out_path}")
    return 0


def cmd_audit(args: argparse.Namespace) -> int:
    img_path = Path(args.image)
    annot_path = Path(args.annotations)
    if not img_path.is_file():
        print(f"Error: Image not found at {img_path}", file=sys.stderr)
        return 1
    if not annot_path.is_file():
        print(f"Error: Annotations JSON not found at {annot_path}", file=sys.stderr)
        return 1

    raw = json.loads(annot_path.read_text())
    annotations = raw["annotations"] if isinstance(raw, dict) and "annotations" in raw else raw
    if not isinstance(annotations, list) or len(annotations) == 0:
        print("Error: Annotations file must contain a non-empty list of annotation objects.", file=sys.stderr)
        return 1

    img = Image.open(img_path).convert("RGB")
    w, h = img.size

    cols_n = min(4, len(annotations))
    rows_n = math.ceil(len(annotations) / cols_n)
    cell_w, cell_h = 320, 220

    card = Image.new("RGB", (cell_w * cols_n, cell_h * rows_n), (255, 255, 255))
    card_draw = ImageDraw.Draw(card)

    for idx, annot in enumerate(annotations):
        name = f"{idx + 1}. {annot.get('id', 'item')} ({annot.get('label', '')[:16]})"
        xp, yp, wp, hp = annot["box"]
        col = idx % cols_n
        row = idx // cols_n
        ox, oy = col * cell_w, row * cell_h

        bx, by = xp * w / 100.0, yp * h / 100.0
        bw, bh = wp * w / 100.0, hp * h / 100.0
        bcx, bcy = bx + bw / 2.0, by + bh / 2.0

        margin = 38
        cx1, cy1 = max(0, int(bx - margin)), max(0, int(by - margin))
        cx2, cy2 = min(w, int(bx + bw + margin)), min(h, int(by + bh + margin))

        crop = img.crop((cx1, cy1, cx2, cy2))
        cdraw = ImageDraw.Draw(crop)
        rel_bx, rel_by = bx - cx1, by - cy1
        cdraw.rectangle([rel_bx, rel_by, rel_bx + bw, rel_by + bh], outline=(37, 99, 235), width=2)

        rel_cx, rel_cy = bcx - cx1, bcy - cy1
        cdraw.line([(rel_cx - 9, rel_cy), (rel_cx + 9, rel_cy)], fill=(239, 68, 68), width=2)
        cdraw.line([(rel_cx, rel_cy - 9), (rel_cx, rel_cy + 9)], fill=(239, 68, 68), width=2)

        aspect = crop.width / max(1, crop.height)
        target_h = cell_h - 40
        target_w = int(target_h * aspect)
        if target_w > cell_w - 20:
            target_w = cell_w - 20
            target_h = int(target_w / max(0.01, aspect))

        resized = crop.resize((max(1, target_w), max(1, target_h)), Image.Resampling.LANCZOS)
        paste_x = ox + (cell_w - target_w) // 2
        paste_y = oy + 30 + (cell_h - 30 - target_h) // 2
        card.paste(resized, (paste_x, paste_y))

        card_draw.rectangle([ox, oy, ox + cell_w, oy + cell_h], outline=(226, 232, 240), width=1)
        card_draw.rectangle([ox, oy, ox + cell_w, oy + 26], fill=(241, 245, 249))
        card_draw.text((ox + 8, oy + 6), name, fill=(15, 23, 42))

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    card.save(out_path)
    print(f"Saved visual centering audit sheet ({len(annotations)} tiles) to {out_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    p_grid = subparsers.add_parser("grid", help="Overlay 100x100 percentage slice grid on a private copy of an image")
    p_grid.add_argument("--image", required=True, help="Path to input figure image")
    p_grid.add_argument("--output", required=True, help="Path to write gridded scratch PNG")
    p_grid.set_defaults(func=cmd_grid)

    p_iso = subparsers.add_parser("isolate", help="Isolate ink/color segment inside a percentage window")
    p_iso.add_argument("--image", required=True, help="Path to input figure image")
    p_iso.add_argument("--window", required=True, help="Search window in percentages: x1,y1,x2,y2")
    p_iso.add_argument("--channel", choices=["any", "black", "red", "blue"], default="any", help="Color channel filter")
    p_iso.add_argument("--threshold", type=int, default=45, help="Pixel threshold for foreground isolation")
    p_iso.add_argument("--pad-x", type=float, default=10.0, help="Symmetric horizontal padding in pixels")
    p_iso.add_argument("--pad-y", type=float, default=8.0, help="Symmetric vertical padding in pixels")
    p_iso.add_argument("--output", required=True, help="Path to write JSON output with centered box")
    p_iso.set_defaults(func=cmd_isolate)

    p_audit = subparsers.add_parser("audit", help="Render Visual Centering Audit Contact Sheet with crosshairs")
    p_audit.add_argument("--image", required=True, help="Path to input figure image")
    p_audit.add_argument("--annotations", required=True, help="Path to JSON file containing list of annotations")
    p_audit.add_argument("--output", required=True, help="Path to write audit contact sheet PNG")
    p_audit.set_defaults(func=cmd_audit)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
