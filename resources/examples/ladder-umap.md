# Worked example: UMAP

**Paper:** McInnes, L., Healy, J. & Melville, J. (2018). *UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction.* arXiv:1802.03426 (v3).

**Core concept:** UMAP's two-phase mechanism (Secs. 2-3, Algs. 1-5): build a fuzzy k-neighbour graph in which every point measures distance on its own local scale (rho_i, sigma_i), merge the one-way memberships by fuzzy union, then lay the graph out in R^d by minimising fuzzy-set cross-entropy with edge sampling and negative sampling.

**What this example shows:** a mathematically dense method paper. Levels 1–2 explain the method's family, and Level 3 singles out UMAP. One toy example (point A) runs from Teen to Undergrad, and the ledger repays its shortcuts. The Expert level states each accuracy comparison with the range where it holds.

**How it was made:**

1. An agent followed [`explanation-levels.md`](../explanation-levels.md), working from the paper's reading-order text.
2. A separate agent, with the paper text, audited it.
3. We then edited it to fix the issues found and to meet the guide's length rules.

Every quote was checked verbatim against the paper. Check it against the paper before reusing it.

---

## Prerequisite profile

| Level | Assumes the reader knows | Does not assume | Must teach before or at this level |
|---|---|---|---|
| 1 · Child | Everyday experience: crowds, standing near or far from someone, pointing at people, drawing a simple map; comparing nearer and farther. | Data, measurements as numbers, dimensions, graphs, probability. | Nothing beyond the picture itself. 'Near' is judged person by person, so even someone in an empty corner has a closest person. |
| 2 · Teen | A dataset is a table of measurements; a probability is a number from 0 to 1; arithmetic with decimals; reading a scatter plot. | Distance between long lists of numbers, exponentials, graphs or adjacency matrices, optimisation. | A data point is a list of measurements with a distance to every other point; a one-way link strength between 0 and 1; combining two chances as 'at least one' = first + second - first x second; 'embedding' means the low-dimensional map. |
| 3 · Undergrad | An introductory ML or data-science course: metrics and Euclidean distance, k-nearest neighbours, weighted graphs and adjacency matrices, exp and log, gradient descent and SGD, matrix transpose, basic probability. | Fuzzy sets, t-conorms, fuzzy-set cross-entropy, negative sampling, spectral embedding with a graph Laplacian, non-linear least-squares curve fitting. | A fuzzy set gives each element a membership strength in [0, 1] (Sec. 2.3); the probabilistic t-conorm a + b - ab as fuzzy union (Sec. 3.1); fuzzy-set cross-entropy (Def. 10); negative sampling (Sec. 4.1); spectral initialisation in one line (Alg. 4). |
| 4 · Grad student | Working knowledge of t-SNE (perplexity calibration, KL divergence, Student-t kernel), Laplacian eigenmaps and spectral methods, SGD with negative sampling (word2vec, LargeVis), the manifold hypothesis, basic Riemannian geometry; follows derivations in the notation of Sec. 3 and App. C. | Category theory (functors, adjunctions), simplicial sets, Spivak's fuzzy singular sets, the proof of Lemma 1. | The axioms listed in Sec. 3; what Lemma 1 buys (normalise by the distance to the kth neighbour, Sec. 2.1); local connectivity as the source of rho_i (Sec. 2.2); the App. C correspondence v_{j\|i}, v_ij, w_ij (Eqs. 15-17). |
| 5 · Expert | The nonlinear dimension-reduction literature: SNE and t-SNE, Barnes-Hut and FIt-SNE, LargeVis, Isomap, Laplacian eigenmaps, diffusion maps, PHATE; evaluation by kNN-classifier accuracy and Procrustes alignment. | Fuzzy simplicial sets and the FinReal/FinSing adjunction (Spivak's metric realization). | Def. 9 (the fuzzy topological representation as a union of FinSing applied to local metric spaces) and Thm. 1, stated only as far as needed to say what is new. |

## Mechanism spine

UMAP gives each point's $k$ nearest neighbours fuzzy memberships $\exp(-\max(0, d(x_i, x_{i_j}) - \rho_i)/\sigma_i)$, where $\rho_i$ is the point's nearest-neighbour distance and $\sigma_i$ a per-point scale; merges the one-way memberships into a symmetric fuzzy graph with the probabilistic t-conorm $w_1 + w_2 - w_1 w_2$; and then places points $y_i \in \mathbb{R}^d$ by stochastic gradient descent on the fuzzy-set cross-entropy between those memberships and $(1 + a\|y_i - y_j\|_2^{2b})^{-1}$, which pulls sampled edges together and pushes negative samples apart.

## The ladder

> **1 · Child.** Picture thousands of photos as a crowd, where similar photos stand close. Each one points at its few nearest neighbours and counts the closest as touching. Two are linked if either one points at the other. On a small map, linked pairs are pulled close and random pairs pushed apart.

> **2 · Teen.** Earlier we pictured a crowd of photos; more precisely, each point is a list of numbers, like 784 pixel values. Earlier, links were all or nothing; more precisely, each one-way link has a strength from 0 to 1. The closest neighbour gets strength 1, and farther neighbours get less, measured from that closest distance. Earlier, a pair was linked if either pointed; more precisely, its strength is the chance at least one link exists. In the embedding (the low-dimensional map), dots move so strongly linked pairs sit close and random pairs spread out.
>
> **Toy numbers (ours).** Point A's four nearest points: B at 2 units, C at 3, D and E at 4.
>
> - A→B: **1** (B is closest). A→C: **0.5**. A→D and A→E: **0.25** each. Here each unit past B halves the strength.
> - C's own list gives C→A: **0.4**.
> - Pair A–C: 0.5 + 0.4 − 0.5 × 0.4 = **0.7**.
> - In the embedding, the A–C pair is pulled together on about 70% of passes; a pair with strength 0.25, on about 25%.

> **3 · Undergrad.** Take data $X = \{x_1, \dots, x_N\}$, a metric $d$ (not necessarily Euclidean) and a neighbour count $k$ (written $n$ in Sec. 4). For each $x_i$, find its $k$ nearest neighbours; let $\rho_i$ be the distance to the nearest one at non-zero distance, and binary-search $\sigma_i$ so the $k$ weights $w$ below sum to $\log_2 k$ (Sec. 3.1, Alg. 3). Each weight is a *fuzzy membership*, a strength in $[0, 1]$ (Sec. 2.3). The one-way weights form a matrix $A$; the *probabilistic t-conorm* merges them into the symmetric $B$, which reads as the probability that at least one of the two directed edges exists if each weight is read as a probability ($\circ$ is the elementwise product; Sec. 3.1). Embedded points $y_i \in \mathbb{R}^d$ get memberships $\Phi$, with $a, b$ fit by non-linear least squares to a curve that is 1 within min-dist and decays exponentially beyond it (Def. 11). The layout minimises the *fuzzy-set cross-entropy* $C$, with $\mu(e) = B_{ij}$ and $\nu(e) = \Phi(y_i, y_j)$ (Def. 10): its first term pulls linked points together, and its second pushes unlinked points apart.
>
> $$w(x_i, x_{i_j}) = \exp\!\left(\frac{-\max\big(0,\ d(x_i, x_{i_j}) - \rho_i\big)}{\sigma_i}\right), \qquad B = A + A^{\top} - A \circ A^{\top}, \qquad \Phi(y_i, y_j) = \big(1 + a\,\|y_i - y_j\|_2^{2b}\big)^{-1}$$
> $$C = \sum_{e} \mu(e)\log\frac{\mu(e)}{\nu(e)} + \big(1 - \mu(e)\big)\log\frac{1 - \mu(e)}{1 - \nu(e)}$$
>
> Starting from a *spectral embedding* (a layout computed from the graph's normalized Laplacian, Alg. 4), stochastic gradient descent uses each edge with probability $\mu$ and steps $y_a$ along $\nabla \log \Phi$ (attraction). It then steps $y_a$ along $\nabla \log(1 - \Phi)$ for a few randomly drawn points treated as membership 0, which is *negative sampling* (Alg. 5, Sec. 4.1). Here the crowd-map picture breaks. A paper map keeps every distance at one scale, but UMAP measures each point on its own scale, so it keeps who is near whom, not how far. UMAP would put a loose region and a dense region “on an even footing” (Sec. 6), so cluster sizes and the gaps between clusters are not distances.

> *What we simplified, and what's true:*
>
> - *"Each unit past the closest halves the strength"* held only for toy point A: there $\rho_A = 2$ and $\sigma_A = 1/\ln 2 \approx 1.44$ make its weights $1, 0.5, 0.25, 0.25$, which sum to $\log_2 4 = 2$.
> - *"Pulled together in proportion to strength"* describes how often an edge is used. Where the dots end up is a local minimum of the total $C$, measured against $\Phi$, a different curve with no per-point $\rho$ or $\sigma$ (Sec. 3.2).
> - *"Random pairs are pushed apart":* only $y_a$ moves, away from randomly drawn points.
> - *"A small flat map":* $d$ can be any dimension, not only 2 (Sec. 5.4.1).

> **4 · Grad student.** Each piece follows from the axioms listed in Sec. 3: the data are uniformly distributed on a manifold, the manifold is locally connected, and preserving its topology is the goal. Under uniformity, a ball holding the $k$ nearest neighbours of $X_i$ has roughly fixed volume, so Lemma 1 lets geodesic distance from $X_i$ be approximated by normalising by the distance to its $k$th neighbour (Sec. 2.1). Earlier we called $\sigma_i$ a binary-searched scale; more precisely, it is a smoothed version of that normaliser and defines the Riemannian metric local to $x_i$ (Sec. 3.1), with the $\log_2(k)$ target chosen “based on empirical experiments” (Sec. 4.1). The price is $N$ mutually incompatible local metrics (Def. 9), which is why they are merged by a fuzzy union rather than averaged. Local connectivity gives $\rho_i$: every $x_i$ keeps an edge of weight 1, which the authors say significantly improves the representation on very high-dimensional data (Secs. 3.1, 5.4.2). Against t-SNE (App. C), $\sigma_i$ is calibrated much as perplexity is, but nothing is normalised into probability distributions, and the cost is cross-entropy rather than KL divergence. Its $-(1 - v_{ij})\log(1 - w_{ij})$ term supplies the repulsion, and $a = b = 1$ recovers t-SNE's Student-t kernel. With no global normaliser the cost is a sum over edges, so SGD with negative sampling runs in $O(kN)$ (Sec. 4.2).
>
> When assumptions fail: with no manifold structure, UMAP “can tend to find manifold structure within the noise of a dataset” (Sec. 6), and a small $n$ reads sampling noise as fine structure (Sec. 4.3). Separately, with fewer than 500 samples its approximations (approximate nearest neighbours, negative sampling) can give suboptimal embeddings (Sec. 6). If density differences are signal, uniformity erases them by design (Sec. 6). Because it models local distance and topology, it does worse than MDS-like methods on metric-preservation measures (Sec. 6). Earlier we started from a spectral embedding; more precisely, random initialisation is possible (Sec. 3.2). The authors also concede that the Laplacian-eigenmaps initialisation is a significant contributor to UMAP's relative global-structure preservation, while holding that the cross-entropy objective contributes too (Sec. 6).

> *What we simplified, and what's true:* negative samples aren't exactly uniform. The formulation implies a vertex distribution $P(x_i)$, which the paper approximates as uniform for sufficiently large data sets (Sec. 4.1).

> **5 · Expert.** Computationally UMAP is another kNN-graph method with a force-directed layout, the skeleton the paper says any such algorithm “must follow” (Sec. 3, App. C); what is new is the derivation that fixes each choice. Each local metric space $(X, d_i)$ (Def. 9) is sent through FinSing, the right adjoint of FinReal (Defs. 7–8, Thm. 1), and the representation is $\bigcup_i \mathrm{FinSing}((X, d_i))$. Only its 1-skeleton is used, since higher skeleta come at “non-negligible computational cost” (Sec. 2.3). Dropping normalisation buys plain SGD, unrestricted $d$, and an embedding of the full GoogleNews dataset of 3 million word vectors (Secs. 5.4.1, 5.4.3).
>
> **kNN-classifier accuracy** (Sec. 5.2, Tables 1–2). Against t-SNE and LargeVis, UMAP is:
>
> - at least as accurate at the smaller $k$ tested (10–40 on PenDigits and COIL-20; 100–400 on Shuttle and MNIST);
> - significantly more accurate at larger $k$ on COIL-20 (80, 160) and Shuttle (800, 3200);
> - notably worse on Fashion-MNIST at 100–400, and comparable there at 1600 and 3200.
>
> **Costs:** no interpretable axes or loadings, no metric faithfulness, and density differences erased (Sec. 6). The authors say UMAP “arguably preserves more of the global structure” (Abstract) and credit part of that to initialisation (Sec. 6).
>
> **Our take:** not every choice comes from the theory. The $\log_2(k)$ target is empirical, and $\Phi$ is a fitted surrogate (Sec. 4.1, Def. 11).
>
> **Open questions the paper names:** detecting spurious embeddings, defining global-structure preservation, and the impact of each component (Secs. 6–7).

> *What we simplified, and what's true:*
>
> - An "edge weight" is the membership strength of a 1-simplex in a fuzzy simplicial set (Def. 8, Thm. 1).
> - Reading strengths as probabilities is an intuition the paper offers (Sec. 3.1). Of the possible unions, the authors write “we have found it most effective to work with the probabilistic t-conorm” (Sec. 4.1).

## Simplification ledger

| Simplification | Introduced at | What is actually true | Corrected at |
|---|---|---|---|
| Data points are photos standing in a crowd, close if similar. | Child | Each point is a vector of measurements (e.g. 784 values for an MNIST image), compared under any metric d, not necessarily Euclidean (Secs. 3.1, 5). | Teen (lists of numbers); Undergrad (any metric d) |
| Each one points at its few nearest neighbours (all or nothing). | Child | Each one-way edge to one of the k nearest neighbours has a strength in [0, 1]: exp(-max(0, d - rho_i)/sigma_i) (Sec. 3.1). | Teen |
| Two people are linked if either one points at the other (yes or no). | Child | The pair's strength is w1 + w2 - w1*w2, i.e. B = A + A^T - A o A^T, the probabilistic t-conorm (Sec. 3.1; App. C, Eq. 16). | Teen |
| The result is a small (flat, two-dimensional) map. | Child | The target dimension d is a free hyper-parameter; UMAP has no computational restriction on embedding dimension (Abstract, Sec. 5.4.1). | Undergrad (What we simplified) |
| Random pairs get pushed apart (Child); random pairs spread out (Teen). | Child | For each sampled edge, only y_a moves, along grad log(1 - Phi), away from n-neg-samples randomly drawn points treated as membership 0 (Alg. 5, Sec. 4.1). | Undergrad (What we simplified) |
| Each unit past the closest neighbour halves the strength. | Teen | True only for toy point A, where sigma_A = 1/ln 2; in general sigma_i is binary-searched so the k strengths sum to log2(k) (Alg. 3, Sec. 3.1). | Undergrad (What we simplified) |
| Linked dots are pulled together in proportion to their strength (toy: A–C on about 70% of passes). | Teen | That is how often an edge is sampled. Where the dots settle is a local minimum of the total fuzzy cross-entropy against Phi = (1 + a\|\|y_i - y_j\|\|^(2b))^-1, which has no per-point rho or sigma (Defs. 10-11, Sec. 3.2). | Undergrad (What we simplified) |
| A strength is like a probability; the pair's strength is the chance at least one link exists. | Teen | Strengths are fuzzy-set memberships; the probability reading is offered as an intuition (Sec. 3.1), and the probabilistic t-conorm is the union the authors found most effective (Sec. 4.1). | Expert (What we simplified) |
| sigma_i is a per-point scale found by binary search. | Undergrad | It is a smoothed version of normalising by the distance to the kth neighbour, which under the uniform-distribution assumption and Lemma 1 approximates geodesic distance and defines the local Riemannian metric (Secs. 2.1, 3.1); the log2(k) target is empirical (Sec. 4.1). | Grad student |
| The layout starts from a spectral embedding. | Undergrad | Spectral initialisation is what Alg. 1 uses; random initialisation is possible (Sec. 3.2), and the initialisation is a significant contributor to global-structure preservation (Sec. 6). | Grad student |
| Negative samples are random (uniform) points. | Undergrad | The formulation implies a vertex sampling distribution P(x_i) that is approximately uniform for sufficiently large data sets (Sec. 4.1). | Grad student (What we simplified) |
| UMAP builds a weighted graph with edge weights. | Undergrad | The graph is the 1-skeleton of a fuzzy simplicial set; weights are 1-simplex membership strengths obtained via FinSing (Def. 8, Thm. 1), and higher skeleta are dropped for cost (Sec. 2.3). | Expert (What we simplified) |

## Analogy map

| In the analogy | In the method |
|---|---|
| A photo standing in the crowd | A data point x_i, a vector of measurements |
| How far apart two people stand | The input distance d(x_i, x_j) under the chosen metric (Sec. 3.1) |
| Pointing at your few nearest people | The k-nearest-neighbour search (Sec. 3.1; NN-Descent, Sec. 4.2) |
| Counting the closest one as touching | Subtracting rho_i, the nearest-neighbour distance, so that edge gets membership 1 (Secs. 2.2, 3.1) |
| Pointing less strongly at ones farther away | The membership exp(-max(0, d - rho_i)/sigma_i), with sigma_i from Alg. 3 |
| Linked if either one points | The fuzzy union B = A + A^T - A o A^T (Sec. 3.1; App. C, Eq. 16) |
| Dots on the map | Embedded points y_i in R^d |
| How close two dots are drawn, read as a strength | Phi(y_i, y_j) = (1 + a\|\|y_i - y_j\|\|^(2b))^-1 (Def. 11) |
| Pulling linked pairs close | Attractive SGD step along grad log Phi on an edge sampled with probability mu (Alg. 5) |
| Pushing random pairs apart | Negative sampling: step along grad log(1 - Phi) against random points (Alg. 5, Sec. 4.1) |
| (no counterpart) Where the dots start | Spectral initialisation (Alg. 4); not in the analogy, introduced at Undergrad |

**Limit:** A paper map keeps every distance at one scale. UMAP measures each point's neighbourhood on its own scale (rho_i, sigma_i), so it keeps who is near whom, not how far: a loose region and a dense region are put “on an even footing” (Sec. 6), and cluster sizes and the gaps between clusters cannot be read as distances. The map can also have any number of dimensions d, not just two (Sec. 5.4.1). Stated at the Undergrad level.

## Checks

| Level | Check | Expected answer and reasoning | Paper location |
|---|---|---|---|
| 1 · Child (radio) | Which is closest to what UMAP does? Options: (a) It shrinks the whole crowd evenly, so every distance stays in proportion; (b) It links each person to their nearest few, then draws linked people close and pushes random others apart; (c) It sorts people into a set number of teams and draws each team as a circle | **It links each person to their nearest few, then draws linked people close and pushes random others apart**. That is the mechanism: neighbour links (Sec. 3.1), then a layout that pulls linked pairs together and pushes random points apart (Sec. 3.2, Alg. 5). Keeping every distance in proportion is what UMAP does not try to do; the paper points to MDS for that (Sec. 6). Sorting into teams is clustering; UMAP places points, it does not assign a fixed number of groups. | Sec. 3; Sec. 3.2; Alg. 5; Sec. 6 |
| 2 · Teen (radio) | In the toy, A's link to C is 0.5 and C's link to A is 0.4, so the pair's strength is 0.7. If C's link to A dropped to 0 (A is not among C's nearest), what would the pair's strength be? Options: (a) 0: the link disappears; (b) 0.5; (c) 0.7: no change; (d) 0.25 | **0.5**. Re-run the toy: 0.5 + 0 − 0.5 × 0 = 0.5. A pair stays linked if either one-way link exists; the combined strength is “the probability that at least one of the two directed edges” exists (Sec. 3.1). | Sec. 3.1 (B = A + Aᵀ − A∘Aᵀ); App. C, Eq. 16 |
| 3 · Undergrad (number) | For x_i, rho_i = 1.2 and Alg. 3 gives sigma_i = 0.5. Neighbour x_j is at d(x_i, x_j) = 1.7, and x_j's own weight on x_i is 0.25. What is B_ij? | **0.53**. $w_{i\to j} = \exp(-\max(0, 1.7 - 1.2)/0.5) = e^{-1} \approx 0.368$; then $B_{ij} = 0.368 + 0.25 - 0.368 \times 0.25 \approx 0.526$ (Sec. 3.1, weight function and $B = A + A^\top - A \circ A^\top$). | Sec. 3.1; App. C, Eqs. 15-16 |
| 4 · Grad student (radio) | Your data have two groups of 1,000 points with the same shape, but group 2's points are spaced ten times wider than group 1's. With default settings, how will the two groups compare in the UMAP embedding? Options: (a) Group 2 is drawn about ten times more spread out; (b) Both are drawn with similar spread; (c) Group 2 is dropped as noise | **Both are drawn with similar spread**. Each x_i's distances are offset by rho_i and scaled by sigma_i, both taken from its own neighbours, so a uniform tenfold spacing cancels out and the two fuzzy graphs have the same memberships. This follows from the assumption that the data are uniformly distributed on the manifold (Sec. 2.1; axioms in Sec. 3). The paper states the consequence, “UMAP would attempt to put these local areas on an even footing” (Sec. 6), and advises a distance-preserving method when you trust the ambient distances. | Sec. 2.1; Sec. 3 (axioms); Sec. 3.1; Sec. 6 |
| 5 · Expert (open) | The paper says UMAP arguably keeps more global structure than t-SNE. What experiment would separate the objective function's contribution from the initialisation's? | *Open answer; model answer:* Cross the two factors: UMAP vs t-SNE objective × spectral (Laplacian-eigenmaps) vs random initialisation, on the same data and neighbour graph, over several seeds, scored by a fixed global-structure measure (e.g. kNN-classifier accuracy at large k as in Sec. 5.2, or a distance-correlation measure). The paper does not run this. It reports UMAP with its default spectral start against tuned baselines (Sec. 5), and concedes that “a significant contributor to UMAP’s relative global structure preservation is derived from the Laplacian Eigenmaps initialization”, noting that [29] found t-SNE with similar initialisation performs equivalently “in a particular measure of global structure preservation”, while holding that cross-entropy vs KL is also a significant contributor (Sec. 6). Sec. 7 calls for this kind of component study. | Sec. 6; Sec. 5.2; Sec. 7; Abstract |
