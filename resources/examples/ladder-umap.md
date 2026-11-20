# Worked example: UMAP

**Paper:** McInnes, L., Healy, J. & Melville, J. (2018). *UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction.* arXiv:1802.03426.

**How it was made:** a fresh agent, given only [`explanation-levels.md`](../explanation-levels.md), the levels section of [`SKILL.md`](../../SKILL.md), and the paper's arXiv text, wrote everything below. Quotes pass `scripts/check_quotes.py` and every level passes `scripts/check_levels.py`. The matching level-matched quiz is [`quiz-umap.json`](quiz-umap.json). Check both against the paper before reusing them.

## Paper kind

Methods / algorithm (the abstract leads with “a novel manifold learning technique for dimension reduction”), so "what they did" gets the most space at every level; theory (§2, Lemma 1, Theorem 1) and benchmarks (§5) support it.

## Prerequisite profile

| Level | Assumes the reader knows | Does not assume | Must teach at this level |
|---|---|---|---|
| Child | Drawing a picture or map; things being close or far apart | Data, dimensions, computers learning, any method names | — (describe what the method does, never its name) |
| Teen | A dataset is a table of numbers; a point on a chart; percentages and seconds | Dimensions as a technical idea, neighbour graphs, t-SNE | *Dimension reduction*; what t-SNE is (the earlier leading tool), as the paper describes it |
| Undergrad | An intro machine-learning course: vectors, Euclidean distance, nearest neighbours, graphs and adjacency matrices, eigenvectors, exp and log, basic probability, gradient descent, PCA as a method name | Manifolds, fuzzy sets, topology, category theory, t-SNE and LargeVis internals | *Manifold* (as the paper uses it), the edge weight as a membership strength in $[0,1]$, the fuzzy union, the cross-entropy objective, what a kNN-classifier accuracy measures; t-SNE, LargeVis, FIt-SNE, PCA and each dataset named |
| Grad student | Nonlinear dimension reduction (t-SNE, LargeVis, Laplacian eigenmaps, PCA, MDS), kNN graphs, SGD and negative sampling, cross-entropy, Riemannian metrics | Simplicial sets, fuzzy simplicial sets, Spivak's functors | *Fuzzy simplicial set* in passing; FIt-SNE and MulticoreTSNE in passing |
| Expert | The manifold-learning literature the paper cites (t-SNE variants, LargeVis, Laplacian eigenmaps, MDS) and the paper's categorical vocabulary | — | — |

## Spine

| Part | Says | Quote | Location |
|---|---|---|---|
| Question | Dimension reduction needs a method that scales and handles diverse data; t-SNE leads for visualisation; theory for neighbour methods assumes uniform data, which real data are not; without theory, choices rest on empirical measures | “It is thus desirable to have an algorithm that is both scalable to massive data and able to cope with the diversity of data available”; “t-SNE is the current state-of-the-art for dimension reduction for visualization”; “In practice, finite real world data is rarely so nicely behaved”; “Without strong theoretical foundations the only arguments which can be made about algorithms amount to empirical measures” | §1, §2.1, §2 |
| What they did | Give each point a local metric that makes the data uniform (normalise by the $k$th-neighbour distance), turn each local metric space into a fuzzy simplicial set, merge by fuzzy union, then lay out a low-dimensional graph by minimising fuzzy-set cross-entropy with SGD and negative sampling, initialised spectrally | “UMAP uses local manifold approximations and patches together their local fuzzy simplicial set representations to construct a topological representation of the high dimensional data”; “UMAP then optimizes the layout of the data representation in the low dimensional space, to minimize the cross-entropy between the two topological representations”; edge weight $\exp(-\max(0,d(x_i,x_{i_j})-\rho_i)/\sigma_i)$ with $\sum_j(\cdot)=\log_2(k)$; $B=A+A^\top-A\circ A^\top$ | §2, §3.1, §3.2, §4.1, Eq. 13 |
| What they found | kNN-classifier accuracy matches t-SNE and LargeVis at small $k$ and is higher at large $k$ (COIL-20 $k=160$: 0.803 vs 0.616 LargeVis; Shuttle $k=3200$: 0.957 vs 0.895 Eigenmaps), but trails on Fashion-MNIST at small $k$ (0.790 vs 0.818 t-SNE at $k=100$). Faster than every other algorithm in Table 3 except on PenDigits (MNIST 87 s vs 292 s FIt-SNE; PenDigits 9 s vs 2 s Eigenmaps/Isomap). Full GoogleNews 3M in ~200 min vs several days. Stability: at a 5% subsample UMAP's error is below any t-SNE value. Linear scaling in embedding dimension (Pen digits) | “UMAP performs at least as well as t-SNE and LargeVis (given the confidence bounds on the accuracy) for $k$ in the range 10 to 40”; “notably underperforms on the Fashion-MNIST dataset”; “UMAP consistently performs faster than any of the other algorithms aside from on the very small Pendigits dataset”; “completed in around 200 minutes, as compared with several days required for MulticoreTSNE”; “after sub-sampling on 5% of the million data points, the per point error for UMAP was already below any value achieved by t-SNE”; “t-SNE scales worse than exponentially while UMAP and LargeVis scale linearly” | Tables 1–3, §5.2, §5.3, §5.4, §5.4.3, Fig. 9 caption |
| Why it matters | A new mathematical framing of manifold learning; competitive quality, arguably more global structure, faster; no restriction on embedding dimension, so general purpose | “One of the primary contributions of this paper is to reframe the problem of manifold learning and dimension reduction in a different mathematical language”; “arguably preserves more of the global structure with superior run time performance”; “UMAP has no computational restrictions on embedding dimension, making it viable as a general purpose dimension reduction technique for machine learning” | §1, Abstract |
| Limits | Finds structure in noise; global-structure advantage owes much to the Laplacian-eigenmaps initialisation; not the choice when global structure is primary; small datasets (<500) suffer from approximations; axes have no meaning; metric structure preserved less well than by MDS; no clear definition of global structure | “UMAP can tend to find manifold structure within the noise of a dataset”; “a significant contributor to UMAP’s relative global structure preservation is derived from the Laplacian Eigenmaps initialization”; “if global structure is of primary interest then UMAP may not be the best choice for dimension reduction”; “This can have an impact on the results of UMAP for small (less than 500 samples) dataset sizes”; “the dimensions of the UMAP embedding space have no specific meaning”; “the lack clear objective measures, or even definitions, of global structure preservation” | §6, §7 |

## Term ledger

| Term | Defined in the paper? | Status | Levels that must define it |
|---|---|---|---|
| Dimension reduction | Described by use: visualisation and pre-processing for machine learning (§1) | established | Child (described, unnamed), Teen |
| Manifold | Used, not defined in plain terms; Riemannian manifold assumed; locally "roughly flat" at the scale of $n$ neighbours (§4.3) | established (math) | Undergrad (by the paper's description); Grad and Expert assume it |
| Riemannian metric, geodesic distance | Used, not defined | established | Grad and Expert assume; Undergrad avoids the terms |
| k-nearest-neighbour graph | Constructed in §3.1, term not defined | established | Teen describes it in plain words; Undergrad assumes |
| Edge weight / membership strength | Yes (§2.2 classical fuzzy set, §3.1) | established | Undergrad |
| Fuzzy set | Yes (§2.2, Def. 3–4) | established | Undergrad (as weights in $[0,1]$); Grad assumes |
| Simplicial set, fuzzy simplicial set | Yes (Def. 2, Def. 5) | emergent (the paper's new framing for this field) | Grad (in passing); Expert uses undefined (the paper does not flag it as unsettled) |
| Local connectivity ($\rho_i$) | Yes (§2.2, §3.1) | established | Undergrad (as $\rho_i$), Grad (as $\rho_i$) |
| Fuzzy union / probabilistic t-conorm | Yes (§3.1 formula for $B$) | established | Undergrad (as the formula); Expert uses the term |
| Cross-entropy (fuzzy set) | Yes (Def. 10) | overloaded (differs from the probability-distribution cross-entropy a neighbouring reader brings; Eq. 13 sums over both $v$ and $1-v$) | Undergrad (displayed), Grad (named "fuzzy-set cross-entropy") |
| Negative sampling | Described (§4.1), cited to [41] | established | Undergrad avoids; Grad and Expert assume |
| Spectral embedding / normalised Laplacian | Described (Alg. 4) | established | Undergrad (as eigenvectors of the normalised Laplacian); Grad/Expert assume |
| min-dist | Yes (§4.3) | established | Undergrad |
| Global vs local structure | Not defined; §7 says the field lacks definitions of global structure preservation | emergent / overloaded | Teen avoids "global"; Undergrad describes "local" as neighbours; Grad and Expert use it with the §7 caveat |
| kNN-classifier accuracy (as a quality measure) | Yes, described as a measure of local structure preservation (§5.2) | established | Undergrad |
| Procrustes distance | Yes (§5.3) | established | Not used below Grad; Grad and Expert omit it |
| t-SNE | Not defined (named, compared in App. C) | established | Teen and Undergrad describe it; Grad/Expert assume |
| LargeVis, FIt-SNE, MulticoreTSNE | LargeVis described in App. C; FIt-SNE described in §5.4.3; MulticoreTSNE in §5.4 | established | Undergrad describes or omits; Grad gives a passing gloss; Expert assumes |
| PCA, MDS | Named, PCA's axes described in §6 | established | Undergrad describes PCA where used; Expert uses MDS undefined |
| Datasets: MNIST, Fashion-MNIST, COIL-20, Shuttle, GoogleNews | Yes (§5) | established | Teen and Undergrad describe at first use; Grad describes briefly; Expert names |

## One-line summary

A neighbour-graph method built from topology, UMAP was competitive with t-SNE on visual quality and kNN accuracy at small $k$, more accurate at large $k$ on most datasets, and faster than every t-SNE implementation timed (MNIST: 87 s against 292 s), with no restriction on embedding dimension (Abstract, §5, Tables 1–3).

## The ladder

> **1 · Child.** Some collections have too many details for anyone to draw as a picture. This new way squashes them into a flat map that keeps close things close. Its maps looked about as good as the best older way, and it was faster. It also worked on much bigger collections than the older way could. But it can find shapes in messy dots, like seeing pictures in the stars.

> **2 · Teen.** Each handwritten-digit image in one test set is a list of 784 numbers (§5). **Dimension reduction** shrinks such lists to a few numbers each, for drawing pictures or feeding other programs (§1). The leading earlier tool for pictures, called t-SNE, becomes too slow for very large data sets (§1, §5.4.3). UMAP, the new method, links each point to its nearest neighbours, then arranges dots so that linked points stay close (§3). Its pictures showed the same groups as t-SNE's, and on 70,000 digit images it took 87 seconds against 292 for the fastest t-SNE version (§5.1, Table 3). It arranged 3 million words and phrases in about 200 minutes, while a fast t-SNE version needed several days (§5.4.3). Unlike t-SNE, it can cheaply shrink data to more than two or three numbers, so it suits general machine learning (Abstract, §5.4.1). It can find patterns in random noise, like seeing pictures in the stars, so small noisy data sets need care (§6).

> **3 · Undergrad.** *Question.* Dimension reduction maps high-dimensional data to a few dimensions, for visualisation or as pre-processing for machine learning, and it needs an algorithm “both scalable to massive data and able to cope with the diversity of data available” (§1). The leading visualisation method, t-SNE, favours preserving local distances over global ones, and without theory, design choices in such neighbour-graph methods can be argued only through empirical measures (§1, §2).
>
> *Method.* UMAP assumes the data lie uniformly on a manifold: a shape that is roughly flat at the scale of a point's $k$ nearest neighbours (§2.1, §4.3). Real data rarely are, so each point $x_i$ gets its own distance scale (§2.1). With $\rho_i$ the distance to its nearest neighbour and $\sigma_i$ set so the weights below sum to $\log_2 k$, the edge from $x_i$ to its neighbour $x_{i_j}$ gets weight $\exp(-\max(0,d(x_i,x_{i_j})-\rho_i)/\sigma_i)$, a number in $[0,1]$ read like the probability that the edge exists (§3.1). Subtracting $\rho_i$ gives every point at least one edge of weight 1 (§3.1). The directed weights $A$ merge into a symmetric graph $B=A+A^\top-A\circ A^\top$, the probability that at least one of the two edges exists (§3.1). Points $y_1,\dots,y_N$ in the low-dimensional layout get weights $w_{ij}=(1+a\|y_i-y_j\|_2^{2b})^{-1}$, with $a$ and $b$ fitted from a spacing parameter, min-dist (§4.1, App. C). Starting from eigenvectors of the graph's normalised Laplacian, stochastic gradient descent moves the $y_i$ to minimise the cross-entropy between the input weights $v_{ij}$ (the entries of $B$) and $w_{ij}$ (Eq. 13):
>
> $$C_{UMAP}=\sum_{i\neq j} v_{ij}\log\frac{v_{ij}}{w_{ij}}+(1-v_{ij})\log\frac{1-v_{ij}}{1-w_{ij}}$$
>
> Its gradients act as attractive forces along edges and repulsive forces between vertices (§3.2).
>
> *Findings.* A classifier that labels each point by its $K$ nearest points in the layout (written $k$ in Tables 1–2) measures how well local structure survives (§5.2). On 1,440 images of 20 rotated objects (COIL-20) at $K=160$, accuracy was 0.803 for UMAP against 0.616 for LargeVis, another neighbour-graph method and the next best (Table 1). On clothing images (Fashion-MNIST) it trailed t-SNE at small $K$: 0.790 against 0.818 at $K=100$ (Table 2). On 70,000 digit images (MNIST) on a laptop, UMAP took 87 s against 292 s for the faster of two t-SNE implementations (Table 3).
>
> *Why it matters and its limits.* UMAP has “no computational restrictions on embedding dimension” (Abstract). It can “find manifold structure within the noise of a dataset”, its approximations can hurt below 500 samples, and its axes have no meaning, unlike those of principal component analysis, which are directions of greatest variance (§6).

> **4 · Grad student.** Nonlinear dimension reduction for visualisation is led by t-SNE, which, like LargeVis and Laplacian eigenmaps, favours local over global distances (§1). However, without theory, neighbour-graph design choices can be argued only through empirical measures, and Laplacian-eigenmap theory assumes data uniformly distributed on the manifold, which finite data rarely are (§2.1, §3). UMAP gives each point its own Riemannian metric by normalising distances to its $k$ nearest neighbours, turns each local metric space into a fuzzy simplicial set (simplices carrying membership strengths in $[0,1]$), merges them by fuzzy union, and lays out the resulting weighted graph by minimising fuzzy-set cross-entropy with SGD, negative sampling and spectral initialisation (§2, §3, §4.1). The weights $\exp(-\max(0,d-\rho_i)/\sigma_i)$ need no global normalisation, which removes the space trees that make t-SNE scale poorly with embedding dimension (§3.1, §5.4.1). In kNN-classifier accuracy UMAP matched t-SNE and LargeVis at small $k$ and led at large $k$, 0.803 against 0.616 for LargeVis on COIL-20 at $k=160$, but trailed t-SNE on Fashion-MNIST at $k=100$, 0.790 against 0.818 (Tables 1–2). Single-core UMAP embedded MNIST in 87 s against 292 s for FIt-SNE, a Fourier-interpolation t-SNE, and 3 million GoogleNews vectors in about 200 minutes against several days for MulticoreTSNE (Table 3, §5.4.3). Its arguably better global structure owes much to the spectral initialisation, and UMAP can find structure in noise and can embed suboptimally below 500 samples (§6).

> **5 · Expert.** Neighbour-graph methods such as t-SNE and LargeVis rest their graph and layout choices on heuristics or task-focused experimentation, and Laplacian-eigenmap theory needs uniformly distributed data or infinite samples (§2, §2.1, §3). UMAP applies Spivak's fuzzy singular-set functor to per-point extended-pseudo-metrics normalised by $\rho_i$ and $\sigma_i$, unions the local fuzzy simplicial sets with the probabilistic t-conorm, and minimises fuzzy-set cross-entropy on the 1-skeleton (§2.2, §3, §4.1). kNN accuracy matched t-SNE and LargeVis at small $k$ and exceeded the best baseline at large $k$ on COIL-20 (0.803 vs 0.616 at $k=160$) and Shuttle (0.957 vs 0.895 for Laplacian eigenmaps at $k=3200$), but trailed t-SNE on Fashion-MNIST for $k$ from 100 to 800 (Tables 1–2). Single-core UMAP ran MNIST in 87 s against 292 s for multi-core FIt-SNE, scaled linearly in embedding dimension, and embedded 30 million points in about 1.8 million dimensions (Table 3, §5.4). The arguable global-structure gain is partly the spectral initialisation, with which t-SNE matches UMAP on one measure, and global structure preservation still lacks objective definitions (§6, §7). UMAP can also find structure in noise, can embed suboptimally below 500 samples, and preserves metric structure less well than MDS (§6).

## Simplification ledger

| Level | Simplification | What the paper actually says | Why the simplified version is still true |
|---|---|---|---|
| Child | *Too many details for anyone to draw as a picture* | Datasets of 64 to 49,152 dimensions, up to about 1.8 million (§5, §5.4.3); dimension reduction is used for visualisation (§1) | A picture has two or three directions; these data have many more, which is why they must be reduced to be drawn |
| Child | *Squashes them into a flat map that keeps close things close* | Builds a weighted neighbour graph and optimises a low-dimensional layout to match it; UMAP “concerns itself primarily with accurately representing local structure” (§3, §6) | The layout is low-dimensional (usually $\mathbb{R}^d$, §2.3) and the objective favours local neighbours staying together; other target dimensions are left out, not denied |
| Child | *About as good as the best older way* | “competitive with t-SNE for visualization quality” (Abstract); t-SNE is “the current state-of-the-art” (§1) | "About as good" is the plain sense of "competitive"; the Fashion-MNIST shortfall at small $k$ is left out, not contradicted |
| Child | *It was faster* | Faster than both t-SNE implementations on every Table 3 dataset; slower than Laplacian eigenmaps and Isomap on PenDigits (Table 3) | The comparison is with *the best older way* (t-SNE), against which it was faster on every dataset timed |
| Child | *Worked on much bigger collections than the older way could* | “able to scale to significantly larger data set sizes than are feasible for t-SNE” (§1) | Direct restatement |
| Child | *Like seeing pictures in the stars* | “similar to the way the human mind finds structured constellations among the stars” (§6) | The paper's own comparison, unlabelled because it is the paper's, not ours |
| Teen | *Links each point to its nearest neighbours, then arranges dots so that linked points stay close* | Weighted k-neighbour graph, then a force-directed layout with attraction along edges and repulsion among vertices (§3.1, §3.2) | Attraction along edges keeps linked points close; repulsion and weights are left out |
| Teen | *Showed the same groups as t-SNE's* | “UMAP distinguishes the same structures as t-SNE and LargeVis” (§5.1) | "Groups" for "structures" in a qualitative picture comparison; "precise embeddings are different" is left out, not denied |
| Teen | *A fast t-SNE version needed several days* | MulticoreTSNE, “the fastest extant implementation of Barnes-Hut t-SNE” in the paper's belief, required “several days” (§5.4, §5.4.3) | MulticoreTSNE is a t-SNE implementation the paper calls fast; FIt-SNE was not reported on the full set |
| Teen | *Can cheaply shrink data to more than two or three numbers* | “no computational restrictions on embedding dimension”; scales linearly in embedding dimension on Pen digits (Abstract, Fig. 9) | Restates the claim; "cheaply" rests on the linear scaling |
| Undergrad | *Read like the probability that the edge exists* | “Intuitively one can think of the weight of an edge as akin to the probability that the given edge exists” (§3.1) | Keeps the paper's "akin to" as "like" |
| Undergrad | Renamed the classifier's neighbour count to $K$ | The paper uses $k$ for both graph neighbours (§3.1) and the classifier (§5.2), and $n$ for graph neighbours in §4 | Renaming is allowed (§7 of the guide) and stated in the level |
| Teen | *Becomes too slow for very large data sets* | t-SNE cannot feasibly scale to the data sizes UMAP handles (§1); MulticoreTSNE needed “several days” for 3 million word vectors (§5.4.3) | Infeasibility on large sets is a speed limit in these benchmarks |
| Undergrad | *A shape that is roughly flat at the scale of a point's $k$ nearest neighbours* | $n$ is “the local scale at which to approximate the manifold as roughly flat” (§4.3); the paper gives no plain definition of manifold | Uses only the paper's own description, not an outside definition |
| Grad, Expert | *Can embed suboptimally below 500 samples* | Approximations “can have an impact on the results of UMAP for small (less than 500 samples) dataset sizes” and “can result in suboptimal embeddings” (§6) | Keeps the paper's "can" |

No analogy of our own: the only comparison used (stars) is the paper's (§6).

## Notes for the user

**Terms the paper uses without defining:** manifold (beyond "Riemannian manifold" and the locally-flat reading in §4.3), geodesic distance, embedding, local vs global structure (§7 says the field lacks definitions of global structure preservation), "constellation effect" (footnote 1 points to §6, which uses the image but not the term), t-SNE and MulticoreTSNE (named, not defined), Barnes-Hut.

**Places where the paper disagrees with itself:**
- Mouse scRNA-seq: “20,921 cells” in §5, but Table 3 lists it as (21086x1000).
- Design rationale: §1 says “UMAPs design decisions were all grounded in a solid theoretic foundation and not derived through experimentation”, but §4.1 says the $\log_2(n)$ target was chosen “based on empirical experiments”, and §4.3 calls min-dist “an essentially aesthetic parameter”.
- Edge weight: §3.1 writes $\exp(-\max(0,d-\rho_i)/\sigma_i)$; Eq. 15 writes $\exp[(-d(x_i,x_j)-\rho_i)/\sigma_i]$ (different sign placement, no max); Algorithm 3's sum has no $\max(0,\cdot)$.
- $\rho$: §3.1 defines it as the smallest *positive* neighbour distance; Algorithm 2 uses knn-dists[1].
- Neighbour count is $k$ in §3 and $n$ in §4 (where $n$ is also the ambient dimension in §2); Definition 9's union runs to $n$ while the data index runs to $N$.
- §4.3 says “four hyper-parameters”, but Algorithm 5 also uses n-neg-samples.
- §5.4 lists six timed datasets; Table 3 has nine rows (adds Pen Digits, scRNA, Flow).
- The abstract says “superior run time performance”; Table 3 shows Laplacian eigenmaps and Isomap faster on PenDigits (2 s vs 9 s), which §5.4 acknowledges.
- Stability: §5.3's text compares UMAP with t-SNE only; the Fig. 8 caption also says UMAP outperforms LargeVis.
- MulticoreTSNE threading: §5.4 says it was benchmarked as fastest “even when run in single core mode”, §5.4.3 says it was run single-threaded, yet §5.4.3 and the Fig. 11 caption also report a multicore (8-core) run and "several days … even using multiple cores" for the full GoogleNews set.

**Could not read:** all figures are images (Figs. 1–15), so stability curves (Fig. 8), scaling curves (Figs. 9–11) and the qualitative embeddings (Fig. 4) are known only from text and captions; Table 3's bolding of fastest times is lost; the Appendix B commutative diagram is garbled. The main point does not depend on these, since the text states the key stability and scaling results.
