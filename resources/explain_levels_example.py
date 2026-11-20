# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.14.0",
#     "anywidget>=0.9.0",
#     "traitlets>=5.14.0",
# ]
# ///
# paper-to-notebook-skill-components: explain-levels

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import sys
    from pathlib import Path

    import marimo as mo

    here = Path(__file__).resolve().parent
    for folder in (here.parent / "assets", here):
        if (folder / "explain_levels.py").is_file():
            sys.path.insert(0, str(folder))
            break
    from explain_levels import ExplainLevels

    return ExplainLevels, mo


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # ExplainLevels: UMAP's two-phase mechanism

    A standalone demo of the `ExplainLevels` anywidget. The five rungs and
    checks are the worked UMAP ladder in
    [`examples/ladder-umap.md`](examples/ladder-umap.md), from McInnes, Healy
    & Melville (2018), arXiv:1802.03426 (v3). Anchored to **Section 2**,
    **Section 3**, and Algs. 1–5.

    **Mechanism spine.** UMAP builds a fuzzy $k$-neighbour graph in which every
    point measures distance on its own local scale $(\rho_i, \sigma_i)$, merges
    one-way memberships by fuzzy union, then lays the graph out in $\mathbb{R}^d$
    by minimising fuzzy-set cross-entropy (Section 2, Section 3).

    Change the dropdown to drive the widget. Click the widget's own rungs, or
    focus it and use ← → (or 1–5). Answer the check under the open rung.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    LEVELS = ["Child", "Teen", "Undergrad", "Grad student", "Expert"]
    reader_level = mo.ui.dropdown(
        options=LEVELS,
        value="Undergrad",
        label="Explain it at this level:",
    )
    reader_level
    return LEVELS, reader_level


@app.cell(hide_code=True)
def _():
    UMAP_LEVELS = [
        {
            "name": "Child",
            "text": (
                "Picture thousands of photos as a crowd, where similar photos "
                "stand close. Each one points at its few nearest neighbours and "
                "counts the closest as touching. Two are linked if either one "
                "points at the other. On a small map, linked pairs are pulled "
                "close and random pairs pushed apart."
            ),
            "check": {
                "question": "Which is closest to what UMAP does?",
                "options": [
                    "It shrinks the whole crowd evenly, so every distance stays in proportion",
                    "It links each person to their nearest few, then draws linked people close and pushes random others apart",
                    "It sorts people into a set number of teams and draws each team as a circle",
                ],
                "correct": (
                    "It links each person to their nearest few, then draws linked "
                    "people close and pushes random others apart"
                ),
                "why": (
                    "That is the mechanism: neighbour links (Sec. 3.1), then a "
                    "layout that pulls linked pairs together and pushes random "
                    "points apart (Sec. 3.2, Alg. 5). Keeping every distance in "
                    "proportion is what UMAP does not try to do; the paper points "
                    "to MDS for that (Sec. 6). Sorting into teams is clustering."
                ),
            },
        },
        {
            "name": "Teen",
            "text": (
                "Earlier we pictured a crowd of photos; more precisely, each "
                "point is a list of numbers, like 784 pixel values. Earlier, "
                "links were all or nothing; more precisely, each one-way link "
                "has a strength from 0 to 1. The closest neighbour gets strength "
                "1, and farther neighbours get less, measured from that closest "
                "distance. Earlier, a pair was linked if either pointed; more "
                "precisely, its strength is the chance at least one link exists. "
                "In the embedding (the low-dimensional map), dots move so "
                "strongly linked pairs sit close and random pairs spread out.\n\n"
                "**Toy numbers (ours).** Point A's four nearest points: B at 2 "
                "units, C at 3, D and E at 4.\n\n"
                "- A→B: **1** (B is closest). A→C: **0.5**. A→D and A→E: **0.25** each. Here each unit past B halves the strength.\n\n"
                "- C's own list gives C→A: **0.4**.\n\n"
                "- Pair A–C: 0.5 + 0.4 − 0.5 × 0.4 = **0.7**.\n\n"
                "- In the embedding, the A–C pair is pulled together on about 70% of passes; a pair with strength 0.25, on about 25%."
            ),
            "check": {
                "question": (
                    "In the toy, A's link to C is 0.5 and C's link to A is 0.4, "
                    "so the pair's strength is 0.7. If C's link to A dropped to 0 "
                    "(A is not among C's nearest), what would the pair's strength be?"
                ),
                "options": ["0: the link disappears", "0.5", "0.7: no change", "0.25"],
                "correct": "0.5",
                "why": (
                    "Re-run the toy: 0.5 + 0 − 0.5 × 0 = 0.5. A pair stays linked "
                    "if either one-way link exists; the combined strength is the "
                    "probability that at least one of the two directed edges exists "
                    "(Sec. 3.1; App. C, Eq. 16)."
                ),
            },
        },
        {
            "name": "Undergrad",
            "text": r"""
Take data $X = \{x_1, \dots, x_N\}$, a metric $d$ (not necessarily Euclidean) and a neighbour count $k$ (written $n$ in Sec. 4). For each $x_i$, find its $k$ nearest neighbours; let $\rho_i$ be the distance to the nearest one at non-zero distance, and binary-search $\sigma_i$ so the $k$ weights $w$ below sum to $\log_2 k$ (Sec. 3.1, Alg. 3). Each weight is a *fuzzy membership*, a strength in $[0, 1]$ (Sec. 2.3). The one-way weights form a matrix $A$; the *probabilistic t-conorm* merges them into the symmetric $B$ (Sec. 3.1). Embedded points $y_i \in \mathbb{R}^d$ get memberships $\Phi$. The layout minimises the *fuzzy-set cross-entropy* $C$ (Def. 10).

$$w(x_i, x_{i_j}) = \exp\!\left(\frac{-\max\big(0,\ d(x_i, x_{i_j}) - \rho_i\big)}{\sigma_i}\right), \qquad B = A + A^{\top} - A \circ A^{\top}, \qquad \Phi(y_i, y_j) = \big(1 + a\,\|y_i - y_j\|_2^{2b}\big)^{-1}$$

$$C = \sum_{e} \mu(e)\log\frac{\mu(e)}{\nu(e)} + \big(1 - \mu(e)\big)\log\frac{1 - \mu(e)}{1 - \nu(e)}$$

Starting from a *spectral embedding* (Alg. 4), SGD uses each edge with probability $\mu$ and then *negative sampling* (Alg. 5, Sec. 4.1). Here the crowd-map picture breaks. A paper map keeps every distance at one scale, but UMAP measures each point on its own scale, so it keeps who is near whom, not how far (Sec. 6).

**What we simplified, and what is true:**

- *"Each unit past the closest halves the strength"* held only for toy point A: there $\rho_A = 2$ and $\sigma_A = 1/\ln 2 \approx 1.44$ make its weights $1, 0.5, 0.25, 0.25$, which sum to $\log_2 4 = 2$.

- *"Pulled together in proportion to strength"* describes how often an edge is used. Where the dots end up is a local minimum of the total $C$.

- *"Random pairs are pushed apart":* only $y_a$ moves, away from randomly drawn points.

- *"A small flat map":* $d$ can be any dimension, not only 2 (Sec. 5.4.1).
""",
            "check": {
                "question": (
                    "For x_i, rho_i = 1.2 and Alg. 3 gives sigma_i = 0.5. "
                    "Neighbour x_j is at d(x_i, x_j) = 1.7, and x_j's own weight "
                    "on x_i is 0.25. What is B_ij?"
                ),
                "correct": 0.53,
                "tolerance": 0.02,
                "why": (
                    r"$w_{i\to j} = \exp(-\max(0, 1.7-1.2)/0.5) = e^{-1} \approx 0.368$; "
                    r"then $B_{ij} = 0.368 + 0.25 - 0.368 \times 0.25 \approx 0.526$ "
                    "(Sec. 3.1; App. C, Eqs. 15–16)."
                ),
            },
        },
        {
            "name": "Grad student",
            "text": r"""
Each piece follows from the axioms listed in Sec. 3: the data are uniformly distributed on a manifold, the manifold is locally connected, and preserving its topology is the goal. Under uniformity, a ball holding the $k$ nearest neighbours of $X_i$ has roughly fixed volume, so Lemma 1 lets geodesic distance from $X_i$ be approximated by normalising by the distance to its $k$th neighbour (Sec. 2.1). Earlier we called $\sigma_i$ a binary-searched scale; more precisely, it is a smoothed version of that normaliser and defines the Riemannian metric local to $x_i$ (Sec. 3.1), with the $\log_2(k)$ target chosen “based on empirical experiments” (Sec. 4.1).

Local connectivity gives $\rho_i$: every $x_i$ keeps an edge of weight 1 (Secs. 3.1, 5.4.2). Against t-SNE (App. C), $\sigma_i$ is calibrated much as perplexity is, but nothing is normalised into probability distributions, and the cost is cross-entropy rather than KL divergence. With no global normaliser the cost is a sum over edges, so SGD with negative sampling runs in $O(kN)$ (Sec. 4.2).

When assumptions fail: with no manifold structure, UMAP “can tend to find manifold structure within the noise of a dataset” (Sec. 6), and a small $n$ reads sampling noise as fine structure (Sec. 4.3). If density differences are signal, uniformity erases them by design (Sec. 6). Because it models local distance and topology, it does worse than MDS-like methods on metric-preservation measures (Sec. 6).

**What we simplified, and what is true:** samples drawn as negatives are not exactly uniform. The formulation implies a vertex distribution $P(x_i)$, which the paper approximates as uniform for sufficiently large data sets (Sec. 4.1).
""",
            "check": {
                "question": (
                    "Your data have two groups of 1,000 points with the same shape, "
                    "but group 2's points are spaced ten times wider than group 1's. "
                    "With default settings, how will the two groups compare in the "
                    "UMAP embedding?"
                ),
                "options": [
                    "Group 2 is drawn about ten times more spread out",
                    "Both are drawn with similar spread",
                    "Group 2 is dropped as noise",
                ],
                "correct": "Both are drawn with similar spread",
                "why": (
                    "Each x_i's distances are offset by rho_i and scaled by sigma_i, "
                    "both taken from its own neighbours, so a uniform tenfold spacing "
                    "cancels out. The paper states the consequence: UMAP would attempt "
                    "to put these local areas on an even footing (Sec. 6)."
                ),
            },
        },
        {
            "name": "Expert",
            "text": r"""
Computationally UMAP is another kNN-graph method with a force-directed layout, the skeleton the paper says any such algorithm “must follow” (Sec. 3, App. C); what is new is the derivation that fixes each choice. Each local metric space $(X, d_i)$ (Def. 9) is sent through FinSing, and the representation is $\bigcup_i \mathrm{FinSing}((X, d_i))$. Only its 1-skeleton is used, since higher skeleta come at “non-negligible computational cost” (Sec. 2.3). Dropping normalisation buys plain SGD, unrestricted $d$, and an embedding of the full GoogleNews dataset of 3 million word vectors (Secs. 5.4.1, 5.4.3).

**kNN-classifier accuracy** (Sec. 5.2, Tables 1–2). Against t-SNE and LargeVis, UMAP is at least as accurate at the smaller $k$ tested, significantly more accurate at larger $k$ on COIL-20 and Shuttle, and notably worse on Fashion-MNIST at 100–400.

**Costs:** no interpretable axes or loadings, no metric faithfulness, and density differences erased (Sec. 6). The authors say UMAP “arguably preserves more of the global structure” (Abstract) and credit part of that to initialisation (Sec. 6).

**Our take:** not every choice comes from the theory. The $\log_2(k)$ target is empirical, and $\Phi$ is a fitted surrogate (Sec. 4.1, Def. 11).

**Open questions the paper names:** detecting spurious embeddings, defining global-structure preservation, and the impact of each component (Secs. 6–7).
""",
            "check": {
                "question": (
                    "The paper says UMAP arguably keeps more global structure than "
                    "t-SNE. What experiment would separate the objective function's "
                    "contribution from the initialisation's?"
                ),
                "correct": None,
                "why": (
                    "Cross the two factors: UMAP vs t-SNE objective × spectral vs "
                    "random initialisation, on the same data and neighbour graph, "
                    "over several seeds, scored by a fixed global-structure measure. "
                    "The paper does not run this. It concedes that a significant "
                    "contributor is the Laplacian Eigenmaps initialization, while "
                    "holding that cross-entropy vs KL also contributes (Sec. 6). "
                    "Sec. 7 calls for this kind of component study."
                ),
            },
        },
    ]
    return (UMAP_LEVELS,)


@app.cell(hide_code=True)
def _(ExplainLevels, UMAP_LEVELS, mo, reader_level):
    umap_ladder = mo.ui.anywidget(
        ExplainLevels(
            title="UMAP's two-phase mechanism",
            paper_ref="Section 2, Section 3, Algs. 1–5 (McInnes, Healy & Melville 2018)",
            level=reader_level.value,
            levels=UMAP_LEVELS,
        )
    )
    umap_ladder
    return (umap_ladder,)


@app.cell(hide_code=True)
def _(mo, umap_ladder):
    mo.md(f"""
    The widget's synced `level` trait is **{umap_ladder.value["level"]}**
    (`paper_ref` is Section 2, Section 3, Algs. 1–5). A second ladder in the same
    notebook would take the same `level=reader_level.value` so one picker
    drives every rung. See [`explain_levels.md`](explain_levels.md).
    """)
    return


if __name__ == "__main__":
    app.run()
