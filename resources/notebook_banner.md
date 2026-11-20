# Notebook banner

Every generated notebook opens with a **banner**: a full-width header cell that names the paper and gives the notebook visual pop. It should look designed, catch the eye, and reward cursor movement — a hover that lifts it, brightens it, or shifts its gradient is enough. The banner is chrome, not content. Nothing in it teaches, except the one-line summary, which must be the same sentence the explanation ladder shows (write it twice and they will drift apart).

## What goes in it

- Paper title, authors, year, and venue or arXiv id, with a link to the paper.
- One hook line: the paper's main point in one sentence. When ExplainLevels is included, reuse its `summary` string verbatim.
- One orientation line when the notebook has a level picker: "Pick your reading level below; every section follows it."
- Nothing else. No claims, no numbers from the paper, no logos.

## How to build it

One cell, `hide_code=True`, directly above the level picker (or above the first content cell when there is no picker). Build the banner as a single `mo.Html` block with inline `<style>`: a gradient or duotone background, a large title, comfortable padding, rounded corners. Pick colors that suit the paper's figures, and keep text contrast high in both light and dark marimo themes (a translucent white or black overlay over the gradient survives both).

```python
@app.cell(hide_code=True)
def _(mo):
    banner = mo.Html("""
    <div data-p2n-banner="1" class="p2n-banner">
      <style>
        .p2n-banner {
          border-radius: 16px;
          padding: 28px 32px;
          background: linear-gradient(120deg, #0f766e, #0284c7 55%, #7c3aed);
          color: #f8fafc;
          transition: transform .35s ease, box-shadow .35s ease;
        }
        .p2n-banner:hover {
          transform: translateY(-2px) scale(1.005);
          box-shadow: 0 10px 30px rgba(2, 132, 199, .35);
        }
        .p2n-banner h1 { margin: 0 0 6px; font-size: 1.6em; line-height: 1.2; }
        .p2n-banner p  { margin: 2px 0; opacity: .92; }
        .p2n-banner a  { color: inherit; }
      </style>
      <h1>UMAP: Uniform Manifold Approximation and Projection</h1>
      <p>McInnes, Healy &amp; Melville, 2018 &middot;
         <a href="https://arxiv.org/abs/1802.03426">arXiv:1802.03426</a></p>
      <p>One hook line: the paper's main point, in one sentence.</p>
    </div>
    """)
    mo.vstack([banner])
    return (banner,)
```

Cursor movement: CSS `:hover` transitions (lift, glow, gradient shift) are the default and they are enough. Inline `<script>` tags inside `mo.Html` do not execute — marimo injects the markup into the page, and browsers do not run scripts added that way. Only build pointer-tracking effects (a spotlight that follows the cursor) when the user asks for more than hover, and build those as a small anywidget, not as a script tag. The banner must look finished with no interaction at all.

## Marimo footguns

- **One expression per cell.** A cell renders only its last top-level expression. A banner cell that also ends with a `mo.md` heading shows the heading and hides the banner. Compose one `mo.Html` block, or wrap the pieces in `mo.vstack([...])`.
- **Dedent strings.** `marimo check --strict` flags indented markdown and HTML strings inside cell functions. Write them flush-left inside the triple quotes.
- **No external assets.** No CDN fonts, no images, no libraries. Inline CSS only, so the notebook works offline after the first install.
- **No layout shift.** The banner keeps a stable height: fixed padding, no auto-playing animation, nothing that moves until the reader moves the cursor.
- **Hide the code.** `hide_code=True`, like every other cell.

## Marker

Give the banner's root element the attribute `data-p2n-banner="1"`. `scripts/validate_notebook.py` warns when a notebook has no such marker, so the banner is a choice rather than an omission.
