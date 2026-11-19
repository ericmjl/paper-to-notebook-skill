# Field-maturity research notes

Auditable sampling for **field-maturity vocabulary onboarding** (branch `field-maturity-vocabulary`). Counts below are from live API calls on **2026-11-19** unless noted. No counts were invented; where a query hit API limits, that is recorded.

## Case-study fields chosen

| Class | Field (case study) | Why this field |
|---|---|---|
| **Established** | Bayesian hierarchical modeling / MCMC | Centuries-long statistical vocabulary; standard textbooks (Gelman et al.; Brooks et al.); methods papers reuse *posterior*, *prior*, *likelihood*, *MCMC* without redefining them. |
| **Emergent** | LLM-based agents & tool-using systems | Rapid coinage since 2022; surveys explicitly organize fragmented frameworks ([Tool Learning survey](https://arxiv.org/abs/2405.17935)); competing labels (*LLM agent*, *agentic*, *tool learning*, *function calling*, *ReAct*). |
| **Interdisciplinary** | Single-cell RNA-seq integration & annotation | Biology + statistics + ML; overloaded terms (*batch*, *cluster*, *feature*, *embedding*, *integration*); benchmark and best-practice papers define terms for readers ([Luecken & Theis, 2019](https://doi.org/10.1186/s13059-019-00621-z); [Lahnemann et al., 2020](https://doi.org/10.1186/s13059-019-1850-9)). |

## Background: Bouquin / Eric design thread

- **Daina Bouquin** (astrophysics + library/data science) has argued that **AI evaluation needs domain experts** and that **“LLM” is not a synonym for “AI”** ([Give Me 5 interview, 2024](https://www.youtube.com/watch?v=-LA1maNOJfM)). The pre-LLM abstract-matching observation (established vs emergent/interdisciplinary degradation) was raised in **paper-to-notebook design discussion** for this repo; we did not find a single published citation for that exact experiment in this audit—treat it as motivation, not as a cited result here.
- **Eric Ma** proposed classifying field maturity with a rubric, then applying a different **linguistic / onboarding strategy** per class (implemented in [`field-maturity.md`](field-maturity.md)).

---

## 1. Established: Bayesian hierarchical modeling / MCMC

### APIs used

- **OpenAlex** — `filter=title_and_abstract.search:hierarchical Bayesian model MCMC`, `per_page=25`, `from_publication_date:2022-01-01`, sorted by publication date (desc). **25 works** returned.
- **arXiv** — `all:hierarchical+Bayesian+MCMC`, `max_results=25`, newest first. **25 works** returned.

### Term hits (titles + abstracts, case-insensitive substring counts)

| Term | OpenAlex (n=25) | arXiv (n=25) |
|---|---:|---:|
| posterior | 29 | 38 |
| prior | 21 | 22 |
| likelihood | 8 | 14 |
| Markov chain Monte Carlo | 14 | 13 |
| MCMC | 34 | 35 |
| Gibbs sampling | 5 | 1 |
| Hamiltonian Monte Carlo | 2 | 1 |
| hierarchical Bayesian | 10 | 15 |
| empirical Bayes | 0 | 0 |

**Interpretation:** High overlap on canonical terms; *MCMC* often stands in for spelled-out *Markov chain Monte Carlo*. Subfield variants (Gibbs vs HMC) appear without definitional essays. No competing umbrella neologisms in the sample.

### Sample titles (OpenAlex, from 2025-11-19 query)

- Subspace splitting Gibbs sampling for image inverse problems based on nonsmooth heavy-tailed Bayesian priors
- Deterministic variational inference for hierarchical Bayesian Cox regression: the VB–CAVI method based on quadratic upper bounds
- A Sequential Monte Carlo Method for Data Assimilation in Subsurface Flow Systems with Hierarchical Uncertainty

Representative arXiv sample (same date): *Behavioral Mapping of Hierarchical Dynamical Models Accelerates Bayesian Parameter Inference*; *Hierarchical Bayesian Inference on the intrinsic event rate of Type I gamma-ray bursts from the Fermi/GBM catalogue*

### Textbooks / surveys (stable vocabulary evidence)

- Gelman, A. et al., *Bayesian Data Analysis* (3rd ed.) — standard *prior / likelihood / posterior* workflow.
- Brooks, S. et al., *Handbook of Markov Chain Monte Carlo* (2011) — settled MCMC nomenclature.

### Supplement: classical population genetics (secondary established check)

OpenAlex: `title_and_abstract.search:population genetics Wright-Fisher`, 25 works — term hits: *fixation* 20, *hardy-weinberg* 9, *genetic drift* 6, *allele frequency* 4, *linkage disequilibrium* 3. Confirms stable classical vocabulary in a second established domain.

---

## 2. Emergent: LLM agents & tool use

### APIs used

- OpenAlex — `title_and_abstract.search:large language model agent tool use`, 25 works from 2022+, plus informal counts on titles/abstracts.
- arXiv — multiple queries with **submittedDate** windows (max **200** results per query; API cap).

### OpenAlex sample (n=25, 2022+)

| Term | Hits |
|---|---:|
| agentic | 16 |
| multi-agent | 6 |
| tool use | 3 |
| LLM agent | 2 |
| function calling | 1 |
| ReAct | 0 |

Survey hit in sample: *Agentic workflows in large language models: a comprehensive review…* ([search on OpenAlex](https://openalex.org/works?filter=title.search:agentic%20workflows%20large%20language%20models)).

### arXiv date-range samples (titles + abstracts, cap 200/query)

Query: `submittedDate:[YYYY0101 TO YYYY1231] AND all:LLM AND all:agent`

| Year | n (cap) | `llm agent` (text) | `agentic` (text) | `multi-agent` (text) | Titles with “agentic” | Titles with “LLM agent” |
|---|---:|---:|---:|---:|---:|---:|
| 2023 | 200 | 28 | 2 | 45 | 0 | 8 |
| 2024 | 200 | 101 | 6 | 97 | 2 | 18 |
| 2025 | 200 | 53 | **70** | 105 | 10 | 14 |

Query: `submittedDate:[YYYY0101 TO YYYY1231] AND ti:agentic AND all:language model`

| Year | n (cap) | `agentic` (text) | Titles with “agentic” |
|---|---:|---:|---:|
| 2024 | 200 | 9 | 3 |
| 2025 | 200 | 70 | 20 |

**Interpretation:** **Terminology in flux.** 2023–2024 discourse emphasizes *LLM agent* / *LLM-based agent* and *multi-agent*; **2025** shows a sharp rise in *agentic* in both titles and body text. Parallel taxonomies coexist: **tool learning** ([Qin et al., 2024 survey](https://arxiv.org/abs/2405.17935)), **tool use**, **function calling** (API vendors), **ReAct** ([Yao et al., 2022](https://arxiv.org/abs/2210.03629)).

### Surveys documenting fragmentation (not counted—qualitative)

- [2404.11584](https://arxiv.org/abs/2404.11584) — emerging agent architectures (reasoning, planning, tool calling).
- [2406.05804](https://arxiv.org/html/2406.05804v2) — LLM-based agents; reusable components; names ReAct, Reflexion, ToT.
- [2405.17935](https://arxiv.org/abs/2405.17935) — tool-learning workflow stages (planning, selection, calling, response).
- [2409.18807](https://arxiv.org/abs/2409.18807) — “LLM with tools” vs tool creation.

### Pedagogy / terminology literature (cross-cutting)

- [Nomenclature consensus for diverse intelligent systems](https://pmc.ncbi.nlm.nih.gov/articles/PMC11278797/) — calls for community consensus; notes interchangeable signifiers.
- Huggett & Lee (2024) on **portmanteau discipline titles** — [SAGE](https://journals.sagepub.com/doi/full/10.1177/03091333241263859).

---

## 3. Interdisciplinary: scRNA-seq integration

### APIs used

- OpenAlex — `title_and_abstract.search:single cell RNA sequencing clustering batch correction`, 25 works (2022+).
- arXiv — `all:single+cell+RNA+clustering`, 25 works.

### Term hits (titles + abstracts)

| Term | OpenAlex (n=25) | arXiv (n=25) |
|---|---:|---:|
| cluster / clustering | 66 | 114 |
| cell type | 28 | 7 |
| batch correction | 20 | 1 |
| batch effect | 9 | 2 |
| feature | 20 | 17 |
| embedding | 5 | 14 |
| trajectory | 1 | 3 |
| pseudotime | 0 | 0 |

**Interpretation:** *Cluster* dominates (biology: cell clusters; ML: clustering algorithm). *Batch correction* vs *integration* vs *alignment* name the same family of tasks in different communities ([benchmark](https://doi.org/10.1186/s13059-019-1850-9), [atlas-level integration benchmark](https://doi.org/10.1038/s41592-021-01336-8)). *Feature* means gene (or gene program) in biology, dimension/variable in ML.

### Integration / terminology surveys located (OpenAlex `search=batch effect integration`, `title.search:single-cell`)

| Title | DOI / link |
|---|---|
| A benchmark of batch-effect correction methods for single-cell RNA sequencing data | [10.1186/s13059-019-1850-9](https://doi.org/10.1186/s13059-019-1850-9) |
| Benchmarking atlas-level data integration in single-cell genomics | [10.1038/s41592-021-01336-8](https://doi.org/10.1038/s41592-021-01336-8) |
| Best practices for single-cell analysis | [10.1186/s13059-019-00621-z](https://doi.org/10.1186/s13059-019-00621-z) |
| Annotation of cell types in single-cell sequencing for cardiovascular disease: Concepts, workflows, challenges, and best practices | (OpenAlex cardiovascular annotation review in sample) |

### Overloaded-term literature

- Cecconi et al., *Ecology Needs a Convention of Nomenclature* — [Bioscience](https://doi.org/10.1093/biosci/biu013): polysemy and redefinition across ecology subfields (analogous risk in scRNA).
- IBISBA (2025) on **semantic ambiguity in biotechnology** — [New Biotech](https://doi.org/10.1016/j.nbt.2025.04.010).

---

## 4. Literature on terminology & onboarding (general)

| Source | Relevance |
|---|---|
| Huggett & Lee (2024), portmanteau discipline names | Interdisciplinary / emergent naming confusion |
| Biomimetics meta-analysis ([PMC11853458](https://pmc.ncbi.nlm.nih.gov/articles/PMC11853458/)) | Synonymous competing terms break literature search |
| Intelligent-systems nomenclature call ([PMC11278797](https://pmc.ncbi.nlm.nih.gov/articles/PMC11278797/)) | Emergent AI/agent vocabulary |
| Cecconi et al., ecology nomenclature | Cross-subfield term overload |

---

## 5. API failures, limits, and gaps

| Issue | Impact |
|---|---|
| **`uv` not on PATH** in the cloud agent VM | Ran Python 3 with stdlib only (`urllib`); no `uv run` for sampling script. |
| **arXiv `max_results` cap** (200 per query) | Year counts are **lower bounds** when more than 200 papers match. |
| **OpenAlex abstract reconstruction** | Works without `abstract_inverted_index` counted title only → term hits biased low. |
| **Semantic Scholar / PubMed** | Not called in this audit (time box); procedure in `field-maturity.md` includes them as optional. |
| **Bouquin abstract-matching study** | Not located as a citable paper in this search; kept as design motivation only. |
| **Population genetics sample** | Small secondary check only; primary established case study is Bayesian/MCMC. |

---

## 6. Raw machine output

Full JSON from the initial three-field sampler is in the agent run artifact `/tmp/field_maturity_sample.json` (not committed). Reproduce with the procedure in [`field-maturity.md`](field-maturity.md) §Sampling procedure.