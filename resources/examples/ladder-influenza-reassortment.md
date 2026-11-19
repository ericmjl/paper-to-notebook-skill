# Worked example: Reassortment and influenza host switching

**Paper:** Ma, E. J., Hill, N. J., Zabilansky, J., Yuan, K. & Runstadler, J. A. (2016). Reticulate evolution is favored in influenza niche switching. *PNAS* 113:5335–5339.

**Core concept:** Reassortment versus clonal descent at host switches: measuring how often a reticulate mechanism, rather than mutational drift, accompanies influenza's move between host species, and testing that against a label-permutation null

**What this example shows:** an analysis paper rather than an algorithm paper. The mechanism is a measurement (a weighted share against a permutation null). Numbers carry their conditions, the validation analyses are named, and the authors' hedges on causality are kept.

**How it was made:**

1. An agent followed [`explanation-levels.md`](../explanation-levels.md), working from the paper's reading-order text.
2. A separate agent, with the paper text, audited it.
3. We then edited it to fix the issues found and to meet the guide's length rules.

Every quote was checked verbatim against the paper. Check it against the paper before reusing it.

---

## Prerequisite profile

| Level | Assumes the reader knows | Does not assume | Must teach before or at this level |
|---|---|---|---|
| 1 · Child | Animals and people catch flu; flu spreads from one animal to another; things can be swapped and mixed; more vs. less. | Genes, viruses as particles, DNA or RNA, data, charts, chance as a number. | A flu virus carries its instructions on eight separate pieces, so two flu viruses in the same animal can swap pieces; and that scientists compare what they see with what would happen by chance. |
| 2 · Teen | Viruses have genes; genetic sequences can be compared and scored for similarity; species; percentages and proportions; reading a bar chart. | Phylogenetics, networks, permutation tests, weighting, evolutionary distance measures. | Clonal descent (ordinary copying with small changes) vs. reassortment; what a null model is and why a shuffled version of the data is the right comparison; percentage points as a gap between two proportions. |
| 3 · Undergrad | Introductory evolution and virology: mutation, drift, selection, segmented genomes, reassortment; sequence alignment and pairwise identity; proportions and simple probability; what a graph (nodes and edges) is. | SeqTrack-style heuristics, affinity propagation, permutation-test construction, COI barcoding, patristic distance. | Pairwise identity summed across eight segments and the per-segment similarity cutoff; the source-pair search; edge weighting (1/n, and the source-pair share) and why it exists; the weighted proportion formula; equal-class-size label permutation; COI divergence as a quantitative niche-dissimilarity axis. |
| 4 · Grad student | Molecular phylogenetics (tree reconstruction, patristic distance, BEAST), reassortment detection by tree incongruence, network reconstruction from genetic data, null/permutation inference, sampling bias in surveillance data. | The specifics of the SeqTrack adaptation, affinity propagation thresholding, or this paper's weighting scheme. | Why a maximal-similarity heuristic replaces per-segment tree reconciliation at this scale and how it was validated (simulations, Fig. S3; patristic-distance comparison, Fig. S4); how equal-class-size permutation is meant to absorb sampling bias; the data-sufficiency thresholds and what they do to Fig. 1 B and C. |
| 5 · Expert | Influenza reassortment and host-switch literature; IRD and BOLD as resources; reticulate-evolution and niche-diversification debates; zoonosis and reverse zoonosis. | — | — |

## Mechanism spine

The method links every influenza isolate to the most similar earlier isolate(s) across all eight genome segments — one source for clonal descent, or a complementary source pair for reassortment — weights each in-edge so that equally plausible sources are not double-counted, and then, for each class of host transition, compares the weighted proportion of reassortant edges with the proportion obtained when host labels are permuted at equal class size.

## The ladder

> **1 · Child.** A flu virus keeps its instructions on eight separate pages, like a booklet. When two flu viruses meet inside one animal, they can swap pages. Scientists traced which flu viruses had moved into a different kind of animal. Those moves came with swapped pages far more often than chance would give.

> **2 · Teen.** Each virus is matched, where possible, to the older viruses whose eight pages, or segments, look most like its own. One older virus matching all eight pages means clonal descent — ordinary copying, with small changes. Two older viruses, each matching part of the eight, means reassortment. Shuffling the host labels and recounting gives the null model: the share you would see anyway. Between different host species the real share ran 19 percentage points above that null; within one species, 7 points below.
>
> *Toy numbers:* in 100 links between viruses from two different host species, about 19 more are reassortant than shuffling predicts; in 100 links inside one species, about 7 fewer.

> **3 · Undergrad.** Start from 18,632 complete influenza A genomes from the Influenza Research Database. Each of the eight segments is aligned separately, and affinity propagation sets a per-segment similarity cutoff below which descent is deemed implausible. Because affinity propagation doesn't scale, the cutoff is the “median threshold of 50 random subsamples of 500 isolates” (Materials and Methods, *Reassortant Virus Identification*). Summing the eight thresholded similarity matrices, each isolate is joined to “the most similar isolate that occurred before it in time”, which gives the full complement graph; each edge carries a pairwise identity (PWI) summed across all eight segments. Isolates with no full-complement source, and those whose in-edges sit in “the bottom 10% of all edges present in the graph”, are candidate reassortants. Of the bottom-10% candidates, “1,357 of 1,368 such viruses were eventually identified as reassortant”. For each candidate, the method searches for a source pair, one virus supplying part of the genome and another the rest, and accepts it when the pair's summed PWI beats the best single source.
>
> For a transition class $t$ the quantity compared is the weighted share below. The class is one of: same vs. different host species (Fig. 1A); a donor–recipient host-group pair (Fig. 1B); or a COI-distance bin (Fig. 1C).
>
> $$P_t \;=\; \frac{\sum_{e \in R_t} w_e}{\sum_{e \in R_t} w_e \; + \; \sum_{e \in C_t} w_e}$$
>
> Here $R_t$ and $C_t$ are the reassortant and clonal edges whose source and sink hosts realise transition $t$, and $w_e$ is each edge's weight (Materials and Methods, *Edge Weighting and Proportion Reassortment Calculations*). The null recomputes $P_t$ after permuting node labels: at equal class size for host species and host groups (Fig. 1 A and B; *Permutation Tests*), and by “a similar permutation test” for the COI bins (Fig. 1C). Observed minus null is +19 percentage points between different host species and −7 points within the same species (Fig. 1A).
>
> Here the booklet picture breaks. Nothing is observed being copied: a source is only the most similar earlier isolate that happened to be sampled. And “Edges in the network connected viral isolates with a median genetic similarity of 99.7%” (Fig. S2), so these are near-identical relatives, not observed parents.

> *What we simplified, and what's true:*
>
> - *"Counting links":* every in-edge is weighted so that ties aren't double-counted. A virus with $n$ equally similar clonal sources gives each in-edge a weight of $1/n$. A reassortant's in-edges are weighted by how often each source appears in a maximal-similarity pair: for pairs (B, C) and (B, D) into A, “the edge B–A would be given a weight of 0.5, and the edges C–A and D–A would be given a weight of 0.25 each” (Fig. S7).
> - *"Chance":* node labels are permuted and $P_t$ is recomputed: at equal class size, 100 times, for Fig. 1 A and B; by a similar test, 500 times, for Fig. 1C (Fig. 1 legend; *Permutation Tests*).

> **4 · Grad student.** Reassortment is classically called by incongruence between per-segment phylogenies; the authors instead adapt SeqTrack (ref. 17) into a maximal-similarity source search, a heuristic rather than a tree reconciliation. Several checks stand in for the trees, including:
>
> - small-world simulations (Fig. S3);
> - a BEAST reconstruction of H3N8 viruses from Minto Flats, Alaska, against which “our method captures the shorter end of the distribution of patristic distances on a tree” (Fig. S4);
> - recovery of the phylogeny of known reassortants, including the 2009 pandemic H1N1 and 2013 H7N9 viruses (Results).
>
> The working assumption: an isolate's true source was sampled and is its most similar earlier relative. Edges join near-identical isolates, with a median genetic similarity of 99.7% (Fig. S2).
>
> The null carries the weight of the design. Human isolates predominate and outbreak sequences are overrepresented, which the authors say inflates detected clonal descent within one host species. Their answer: “our permutation tests (for the host species and group labels) involve class labels of equal sizes”. Where the similarity signal fails, so does the call. Among human-to-human transitions, limited subtype diversity and serial selective sweeps leave high sequence similarity, which “likely obscures the distinction between reassortment and clonal descent”.
>
> Earlier we treated the 19-point gap as one number. In fact it varies by host-group interface (Fig. 1B). It also rises with host COI divergence across the bins with enough data, from about 0.14 at 0 to about 0.5 at 0.15 (read from Fig. 1C). The most divergent bin (0.20) falls back near the null but has too few events to interpret. Fig. 1B has two exceptions:
>
> - Wild bird to wild bird is overrepresented although the groups match; the authors cite the range of species the label covers.
> - Human to domestic mammal is not; they attribute this to “shared cellular receptors for viral entry”.
>
> Only transitions with at least 1,000 descent events or at least 10 reassortment events are interpreted (Results; weighted sums in the Fig. 1 legend), though all are displayed. Finally, the design is associational in time: the authors “do not specifically identify whether reassortment occurs before or after host switching”, and clonal expansion of a reassortant strain is scored as clonal descent.

> **5 · Expert.** That reassortment accompanies host switches is not the claim; the denominator is. Prior reviews assert reticulate events as drivers of speciation and niche diversification (refs. 22, 23), but on the authors' account “none have quantitatively tested the importance of reticulate evolutionary strategies in enabling ecological niche switches on a global scale”. The contribution has three parts:
>
> - put clonal and reassortant descent in one weighted network over 18,632 genomes;
> - score host-species and host-group transitions against an equal-class-size permutation null (+19 points between species, −7 within; Fig. 1A);
> - track that overrepresentation along a continuous niche axis, host COI divergence (Fig. 1C).
>
> The trade-offs:
>
> - **A similarity heuristic in place of per-segment tree reconciliation.** It is validated against simulations, one BEAST-reconstructed H3N8 subset, and known reassortants (Results; Figs. S3–S4).
> - **A niche operationalised as host species.** The authors say the choice is “in part, borne out of data availability”, and mallards are a known exception (Fig. S5).
> - **A null that neutralises sampling bias only by assuming equal sampling.**
>
> Timing and causality stay open. Surveillance is “less dense than necessary to distinguish between these two scenarios”, so “Whether reticulate evolution is causal for ecological niche switching will require further study.”

## Simplification ledger

| Simplification | Introduced at | What is actually true | Corrected at |
|---|---|---|---|
| Two flu viruses swap pages, as if the exchange were watched. | Child | Nothing is observed being exchanged. Reassortment is inferred when a sink genome's segments are best matched by two different earlier isolates, and the source pair is accepted only when its summed PWI beats the best single source. | Undergrad |
| The Child level's phrase *far more often than chance would give*. | Child | Chance is a specific construction: node labels are permuted and the weighted proportion recomputed. This is done at equal class size, 100 times, for host species and host groups (Fig. 1 A and B), and by a similar permutation test, 500 times, for the COI bins (Fig. 1C) (Fig. 1 legend; Permutation Tests). | Teen, and in full at Undergrad (What we simplified) |
| Each virus is linked to the most similar earlier virus (one link). | Teen | Where multiple sources or multiple source pairs tie at maximal similarity, all are kept as plausible sources and the edges are down-weighted (1/n, or the source-pair share) so they are not double-counted. | Undergrad (What we simplified) |
| Links are counted, so the share is a count of links. | Teen | The proportion is a ratio of summed edge weights, not of counts. | Undergrad (What we simplified) |
| One number, 19 percentage points, describes host switching. | Teen | 19 points is the different-vs-same-species contrast of Fig. 1A. The gap varies by host-group interface, with two exceptions (wild bird to wild bird; human to domestic mammal), and rises with host COI distance (Fig. 1 B and C). | Grad student |
| The network recovers descent relationships. | Undergrad | It is a heuristic adapted from SeqTrack. It was validated on simulated graphs (Fig. S3); against a BEAST tree it captures the shorter end of the distribution of patristic distances (Fig. S4); and it recreates the phylogeny of known reassortants such as 2009 pandemic H1N1 (Results). | Grad student |
| Every transition in Fig. 1 B and C supports the conclusion. | Undergrad | Only transitions with at least 1,000 descent events or at least 10 reassortment events are interpreted; the rest are plotted for completeness with unbolded tick labels. | Grad student |
| Reassortment happens as the virus crosses into the new host. | Child, carried through Undergrad | The method identifies host transitions across which reassortment is implicated, not when it happened; a reassortment may precede, accompany or follow the switch, and clonal expansion of a reassortant is scored as clonal descent. | Grad student |
| A host species is an ecological niche. | Teen | The authors state this choice is in part borne out of data availability, expect exceptions where species differences are not a major barrier (mallards, Fig. S5), and note the data do not exist to quantify niches at other levels. | Expert |
| Reassortment is favoured for switching niches — stated as a result. | Child | The study establishes association, not causation: whether reticulate evolution is causal for ecological niche switching will require further study. | Expert |

## Analogy map

| In the analogy | In the method |
|---|---|
| An instruction booklet of eight loose pages, handed down from older booklets | An influenza A isolate's genome of eight segments, descended from earlier isolates |
| One older booklet whose every page is the closest match | A clonal source: the most similar isolate occurring before it in time, supplying a full complement of all eight segments |
| Two older booklets that only together match better than any single one | A reassortant source pair, accepted when the summed PWI across segments beats the best single source |
| How closely the pages match | Pairwise identity (PWI), summed across all eight segments, after each segment's similarity cutoff is applied |
| Several older booklets matching equally well, so you hedge between them | Multiple plausible sources or source pairs at maximal similarity, each in-edge down-weighted (1/n, or the source-pair share) |
| Which household the booklet turns up in | The host species (and host group) of the isolate |
| Shuffling the household tags and recounting | The permutation null: equal class size, 100 times, for host species and groups (Fig. 1 A and B); a similar test, 500 times, for COI bins (Fig. 1C) |
| How unlike two households are | Host evolutionary distance, the proportion of mismatched nucleotides between the hosts' COI genes |

**Limit:** The booklet picture implies you watch a copy being made and know who the parents were. In the method nothing is observed being copied: a source is only the most similar earlier isolate that happened to be sampled, the true ancestor may never have been sequenced, and edges connect isolates at a median genetic similarity of 99.7% (Fig. S2) rather than parent to offspring. The picture also implies you know when the assembly happened; the authors do not specifically identify whether reassortment occurs before or after host switching, only the host transitions across which reassortment is implicated. Stated at Undergrad level, where the ladder first makes the edges and their weights explicit.

## Checks

| Level | Check | Expected answer and reasoning | Paper location |
|---|---|---|---|
| 1 · Child (radio) | Which is closest to what the scientists found about flu viruses that move into a different kind of animal? Options: (a) Swapping pieces with another flu virus happens more often than expected when flu moves to a different kind of animal; (b) Flu viruses only ever copy themselves, with small changes; (c) Flu viruses swap pieces just as often whether or not they move to a different kind of animal | **Swapping pieces with another flu virus happens more often than expected when flu moves to a different kind of animal**. The paper compares the share of swapped-piece links with the share after shuffling the host labels: 19 percentage points higher between different host species, and 7 points lower within one species (Results; Fig. 1A). The second option is wrong because swaps are detected; the third is wrong because the two situations differ, which is the whole result. The paper describes this two ways. The Abstract says reassortment “predominates over mutational drift in transmission between different host species”. But in Fig. 1A the reassortant share between species is about 0.32 against a null of about 0.125: favoured relative to chance, not a majority of links. | Results (“reassortant edges were overrepresented at 19 percentage points above a null permutation model”); Fig. 1A |
| 2 · Teen (radio) | Suppose the host labels in the network carried no information at all — any virus equally likely to sit in any host. What would happen to the 19-point gap between the data and the null? Options: (a) It would grow; (b) It would shrink to about zero; (c) It would stay at 19 points | **It would shrink to about zero**. The null is the same network with its labels shuffled at equal class size. If the real labels behaved like shuffled ones, the observed and null proportions would land on top of each other. The 19 points measure exactly how far the real labelling departs from a shuffled one (Results; Materials and Methods, Permutation Tests). | Materials and Methods, Permutation Tests; Results; Fig. 1A |
| 3 · Undergrad (number) | In one transition class the reassortant edges carry weights 0.5, 0.25 and 0.25, and the clonal edges carry weights 1, 0.5 and 0.5. What is the weighted proportion of reassortment for that class? | **0.333**. Reassortant weights sum to 1.0 and clonal weights to 2.0, so P = 1.0 / (1.0 + 2.0) ≈ 0.333. The proportion is taken over summed weights, not counts — by count it would be 3/6 = 0.5, which is the mistake the weighting exists to prevent (Materials and Methods, Edge Weighting and Proportion Reassortment Calculations). | Materials and Methods, Edge Weighting and Proportion Reassortment Calculations |
| 4 · Grad student (radio) | Fig. 1B shows reassortment underrepresented at human-to-human transitions. Which assumption of the detection step does that observation most directly strain, and where does the paper say so? Options: (a) That a reassortant can be told from a clonal descendant because some source pair scores higher than any single source; (b) That host species is a meaningful ecological niche; (c) That the permutation null uses classes of equal size | **That a reassortant can be told from a clonal descendant because some source pair scores higher than any single source**. Human viruses are a limited set of subtypes undergoing serial selective sweeps, so sequence similarity within the human viral pool is high, which the authors say “likely obscures the distinction between reassortment and clonal descent” (Results, human-to-human paragraph). When every candidate source is nearly identical, the summed-PWI comparison that defines a reassortant loses its discriminating power. The authors also expect antibody-mediated immunity to limit coinfection, which is a biological rather than a methodological reason. The other two options are real assumptions of the study, but neither is what the human-to-human result strains. | Results, human-to-human paragraph; Materials and Methods, Reassortant Virus Identification |
| 5 · Expert (open) | Name one reason the paper's association between host switching and reassortment cannot be read as causal, and say what evidence would settle it. | *Open answer; model answer:* Model answer: the method places reassortment on host transitions but not in time. The authors state they “do not specifically identify whether reassortment occurs before or after host switching, but only identify host transitions across which reassortment is implicated”, and that clonal expansion of a reassortant strain is itself identified as clonally descended; they attribute this to IAV surveillance being “less dense than necessary to distinguish between these two scenarios”, and conclude that “Whether reticulate evolution is causal for ecological niche switching will require further study.” Settling it needs densely sampled, dated isolates on both sides of a switch — enough to place a reassortant genotype in the donor host before transfer, or only in the recipient after it — or an experimental system in which reassortant and clonal variants compete across a host barrier. Acceptable alternatives: the sampling bias that the equal-class-size null only partly neutralises, or the confound that host species stands in for the niche. | Discussion, fourth limitation |
