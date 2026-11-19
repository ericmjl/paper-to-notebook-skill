# Field-maturity research notes

Auditable sampling for **field-maturity vocabulary onboarding** (branch `field-maturity-vocabulary`). Counts below are from live API calls on **2026-11-19** unless noted. No counts were invented; where a query hit API limits, that is recorded.

## Case-study fields chosen

| Class | Field (case study) | Why this field |
|---|---|---|
| **Established** | Bayesian hierarchical modeling / MCMC | Centuries-long statistical vocabulary; standard textbooks (Gelman et al.; Brooks et al.); methods papers reuse *posterior*, *prior*, *likelihood*, *MCMC* without redefining them. |
| **Emergent** | LLM-based agents & tool-using systems | Rapid coinage since 2022; surveys explicitly organize fragmented frameworks ([Tool Learning survey](https://arxiv.org/abs/2405.17935)); competing labels (*LLM agent*, *agentic*, *tool learning*, *function calling*, *ReAct*). |
| **Interdisciplinary** | Single-cell RNA-seq integration & annotation | Biology + statistics + ML; overloaded terms (*batch*, *cluster*, *feature*, *embedding*, *integration*). Method vocabulary is set out in [Tran et al., 2020](https://doi.org/10.1186/s13059-019-1850-9) (batch-effect benchmark) and [Luecken & Theis, 2019](https://doi.org/10.15252/msb.20188746) (analysis tutorial). [Lähnemann et al., 2020](https://doi.org/10.1186/s13059-020-1926-6) is a separate grand-challenges paper, not that benchmark. |

## Background: Bouquin / Eric design thread

- **Daina Bouquin** appears in [Give Me 5 Season 2, Episode 2](https://www.youtube.com/watch?v=-LA1maNOJfM) (YouTube oEmbed title verified; channel PyData). Claims about what she says in the episode (domain-expert evaluation; “LLM” is not a synonym for “AI”) were **not re-checked against a transcript** in this audit. The pre-LLM abstract-matching observation was raised in design discussion for this repo and was **not found as a published paper**.
- **Eric Ma** proposed classifying field maturity with a rubric, then applying a different **linguistic / onboarding strategy** per class (implemented in [`field-maturity.md`](field-maturity.md)).

---

## 1. Established: Bayesian hierarchical modeling / MCMC

### APIs used

- **OpenAlex** — `filter=title_and_abstract.search:hierarchical Bayesian model MCMC`, `per_page=25`, `from_publication_date:2022-01-01`, sorted by publication date (desc). **25 works** returned.
- **arXiv** — `all:hierarchical+Bayesian+MCMC`, `max_results=25`, newest first. **25 works** returned.

### Term hits

**Corpus:** 25 works per API (see above). **Metric:** case-insensitive **substring mentions** in the concatenated titles + abstracts of those 25 works (not 25 independent papers per term).

| Term | OpenAlex mentions (25 works) | arXiv mentions (25 works) |
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

### Sample titles (OpenAlex, from the 2026-11-19 query)

- Subspace splitting Gibbs sampling for image inverse problems based on nonsmooth heavy-tailed Bayesian priors
- Deterministic variational inference for hierarchical Bayesian Cox regression: the VB–CAVI method based on quadratic upper bounds
- A Sequential Monte Carlo Method for Data Assimilation in Subsurface Flow Systems with Hierarchical Uncertainty

Representative arXiv sample (same date): *Behavioral Mapping of Hierarchical Dynamical Models Accelerates Bayesian Parameter Inference*; *Hierarchical Bayesian Inference on the intrinsic event rate of Type I gamma-ray bursts from the Fermi/GBM catalogue*

### Textbooks / surveys (stable vocabulary evidence)

- Gelman, Carlin, Stern, Dunson, Vehtari & Rubin (2013), *Bayesian Data Analysis*, Chapman and Hall/CRC, [10.1201/b16018](https://doi.org/10.1201/b16018). Crossref records no edition number on this DOI, so this note does not call it a numbered edition.
- Brooks, Gelman, Jones & Meng (2011), *Handbook of Markov Chain Monte Carlo*, Chapman and Hall/CRC, [10.1201/b10905](https://doi.org/10.1201/b10905).

### Supplement: classical population genetics (secondary established check)

OpenAlex: `title_and_abstract.search:population genetics Wright-Fisher`, **25 works** — substring mentions in that corpus: *fixation* 20, *hardy-weinberg* 9, *genetic drift* 6, *allele frequency* 4, *linkage disequilibrium* 3. Confirms stable classical vocabulary in a second established domain.

---

## 2. Emergent: LLM agents & tool use

### APIs used

- OpenAlex — `title_and_abstract.search:large language model agent tool use`, 25 works from 2022+, plus informal counts on titles/abstracts.
- arXiv — multiple queries with **submittedDate** windows (max **200** results per query; API cap).

### OpenAlex sample (25 works, 2022+)

**Metric:** case-insensitive substring **mentions** in the concatenated titles and abstracts of those 25 works. Not the number of works that contain the term.

| Term | Mentions in 25 works |
|---|---:|
| agentic | 16 |
| multi-agent | 6 |
| tool use | 3 |
| LLM agent | 2 |
| function calling | 1 |
| ReAct | 0 |

One title in that sample matches Bhardwaj, Thakur, Dhaliwal & Viswanathan (2026), *Agentic workflows in large language models: a comprehensive review of architectures, planning strategies, and real-world applications*, *Discover Computing*, [10.1007/s10791-026-10743-4](https://doi.org/10.1007/s10791-026-10743-4) (Crossref issued 2026-11-18). The earlier OpenAlex HTML search URL returned HTTP 403 and is not used as a citation.

### arXiv date-range samples

These counts were **not recomputed** during the citation audit. Labels below match the original script.

Query: `submittedDate:[YYYY0101 TO YYYY1231] AND all:LLM AND all:agent`. Each year returned **200 works** (the API cap), so these are not full-year totals.

| Year | Works returned (capped) | Mentions of `llm agent` | Mentions of `agentic` | Mentions of `multi-agent` | Works whose title contains “agentic” | Works whose title contains “LLM agent” |
|---|---:|---:|---:|---:|---:|---:|
| 2023 | 200 | 28 | 2 | 45 | 0 | 8 |
| 2024 | 200 | 101 | 6 | 97 | 2 | 18 |
| 2025 | 200 | 53 | **70** | 105 | 10 | 14 |

A second query, `submittedDate:[YYYY0101 TO YYYY1231] AND ti:agentic AND all:language model`, also returned 200 works per year, but only **3** (2024) and **20** (2025) of those titles contained “agentic”, with **9** and **70** substring mentions of `agentic`. That does not match a title-restricted sample. **Do not treat those two rows as evidence of title usage.** They are left out of the interpretation below.

**Interpretation:** **Terminology in flux.** In the first query’s capped 200-work samples, 2023–2024 text mentions *LLM agent* and *multi-agent* more often than *agentic*; the 2025 sample has more *agentic* mentions (70) than *llm agent* mentions (53). Parallel labels still coexist: **tool learning** ([Qu et al., 2024](https://arxiv.org/abs/2405.17935)), **tool use**, **function calling** (vendor docs; not a paper cited here), **ReAct** ([Yao et al., 2022](https://arxiv.org/abs/2210.03629)).

### Surveys (qualitative; not part of the mention counts)

- [2404.11584](https://arxiv.org/abs/2404.11584) — Masterman, Besen, Sawtell & Chao (2024), *The Landscape of Emerging AI Agent Architectures for Reasoning, Planning, and Tool Calling: A Survey*.
- [2406.05804](https://arxiv.org/abs/2406.05804) — Li (2024), *A Review of Prominent Paradigms for LLM-Based Agents: Tool Use (Including RAG), Planning, and Feedback Learning*. The current abstract (arXiv v6) says frameworks use inconsistent taxonomies and offers a unified taxonomy for tool use, planning, and feedback learning. An earlier HTML snapshot ([v2](https://arxiv.org/html/2406.05804v2)) uses a different title (*A Survey on LLM-Based Agents: Common Workflows and Reusable LLM-Profiled Components*). This note does not claim that either version names ReAct, Reflexion, or Tree-of-Thoughts; that was not in the v6 abstract.
- [2405.17935](https://arxiv.org/abs/2405.17935) — Qu et al. (2024), *Tool Learning with Large Language Models: A Survey*. The abstract says the tool-learning literature is fragmented and reviews why and how tool learning is implemented.
- [2409.18807](https://arxiv.org/abs/2409.18807) — Shen (2024), *LLM With Tools: A Survey*. The abstract is about teaching LLMs to use external tools.

### Pedagogy / terminology literature (cross-cutting)

- Kagan et al. (2024), *Toward a nomenclature consensus for diverse intelligent systems: Call for collaboration*, *The Innovation*, [10.1016/j.xinn.2024.100658](https://doi.org/10.1016/j.xinn.2024.100658) ([PMC11278797](https://pmc.ncbi.nlm.nih.gov/articles/PMC11278797/)).
- Huggett & Lee (2024), *Problems and prospects of portmanteau titles and other neologisms for interface disciplines in the Earth and life sciences*, *Progress in Physical Geography: Earth and Environment*, [10.1177/03091333241263859](https://doi.org/10.1177/03091333241263859).

---

## 3. Interdisciplinary: scRNA-seq integration

### APIs used

- OpenAlex — `title_and_abstract.search:single cell RNA sequencing clustering batch correction`, 25 works (2022+).
- arXiv — `all:single+cell+RNA+clustering`, 25 works.

### Term mentions (titles + abstracts)

**Corpus:** 25 works per API. **Metric:** substring mentions in the concatenated titles and abstracts. Example: 66 mentions of `cluster` is not 66 papers.

| Term | OpenAlex mentions (25 works) | arXiv mentions (25 works) |
|---|---:|---:|
| cluster / clustering | 66 | 114 |
| cell type | 28 | 7 |
| batch correction | 20 | 1 |
| batch effect | 9 | 2 |
| feature | 20 | 17 |
| embedding | 5 | 14 |
| trajectory | 1 | 3 |
| pseudotime | 0 | 0 |

**Interpretation:** In the OpenAlex corpus, the substring `cluster` occurs 66 times across 25 works (biology: cell clusters; ML: a clustering algorithm). *Batch correction* and *integration* name related tasks in different communities: Tran et al. (2020), *A benchmark of batch-effect correction methods for single-cell RNA sequencing data*, *Genome Biology*, [10.1186/s13059-019-1850-9](https://doi.org/10.1186/s13059-019-1850-9); Luecken et al. (2021), *Benchmarking atlas-level data integration in single-cell genomics*, *Nature Methods*, [10.1038/s41592-021-01336-8](https://doi.org/10.1038/s41592-021-01336-8). *Feature* is a gene (or gene program) in this literature and a column in machine learning.

### Papers located for vocabulary (titles checked on Crossref)

| Title | Attribution |
|---|---|
| A benchmark of batch-effect correction methods for single-cell RNA sequencing data | Tran et al. (2020), *Genome Biology*, [10.1186/s13059-019-1850-9](https://doi.org/10.1186/s13059-019-1850-9) |
| Benchmarking atlas-level data integration in single-cell genomics | Luecken et al. (2021), *Nature Methods*, [10.1038/s41592-021-01336-8](https://doi.org/10.1038/s41592-021-01336-8) |
| Current best practices in single-cell RNA-seq analysis: a tutorial | Luecken & Theis (2019), *Molecular Systems Biology*, [10.15252/msb.20188746](https://doi.org/10.15252/msb.20188746) |
| Eleven grand challenges in single-cell data science | Lähnemann et al. (2020), *Genome Biology*, [10.1186/s13059-020-1926-6](https://doi.org/10.1186/s13059-020-1926-6). This is not the batch-effect benchmark. |
| Annotation of cell types in single-cell sequencing for cardiovascular disease: Concepts, workflows, challenges, and best practices | Sun, Ma & Chen (2026), *The International Journal of Biochemistry & Cell Biology*, [10.1016/j.biocel.2026.107027](https://doi.org/10.1016/j.biocel.2026.107027) |

`10.1186/s13059-019-00621-z` does not resolve (Crossref HTTP 404). It is not cited.

### Overloaded-term literature

- Herrando-Pérez, Brook & Bradshaw (2014), *Ecology Needs a Convention of Nomenclature*, *BioScience*, [10.1093/biosci/biu013](https://doi.org/10.1093/biosci/biu013).
- Ancelin et al. (2025), *Addressing semantic ambiguity in biotechnology: Proposals from the European research infrastructure IBISBA*, *New Biotechnology*, [10.1016/j.nbt.2025.04.010](https://doi.org/10.1016/j.nbt.2025.04.010).

---

## 4. Literature on terminology & onboarding (general)

| Source | Relevance |
|---|---|
| Huggett & Lee (2024), [10.1177/03091333241263859](https://doi.org/10.1177/03091333241263859) | Portmanteau names for interface disciplines |
| Huber & Müssig (2025), *Clarity Amidst Ambiguity…*, *Biomimetics*, [10.3390/biomimetics10020076](https://doi.org/10.3390/biomimetics10020076) ([PMC11853458](https://pmc.ncbi.nlm.nih.gov/articles/PMC11853458/)) | Competing labels in bio-inspired fields |
| Kagan et al. (2024), [10.1016/j.xinn.2024.100658](https://doi.org/10.1016/j.xinn.2024.100658) | Call for nomenclature consensus for intelligent systems |
| Herrando-Pérez et al. (2014), [10.1093/biosci/biu013](https://doi.org/10.1093/biosci/biu013) | Synonymy and polysemy in ecology |

---

## 5. API failures, limits, and gaps

| Issue | Impact |
|---|---|
| **`uv` not on PATH** in the cloud agent VM | Ran Python 3 with stdlib only (`urllib`); no `uv run` for sampling script. |
| **arXiv `max_results` cap** (200 per query) | Work counts at 200 are capped samples, not full-year totals. Mention counts are inside that cap. |
| **`ti:agentic` query** | Returned 200 works while only 3 (2024) and 20 (2025) titles contained “agentic”. Those rows are not used as title-frequency evidence. |
| **Mention counts not recomputed** | The 2026-11-19 citation audit relabeled the original tallies. It did not re-download the corpora, so the integers were not reproduced in this pass. |
| **OpenAlex abstract reconstruction** | Works without `abstract_inverted_index` counted title only → term hits biased low. |
| **Semantic Scholar / PubMed** | Not called in this audit (time box); procedure in `field-maturity.md` includes them as optional. |
| **Bouquin abstract-matching study** | Not located as a citable paper in this search; kept as design motivation only. |
| **Population genetics sample** | Small secondary check only; primary established case study is Bayesian/MCMC. |

---

## 6. Citation audit

Checked on 2026-11-19. DOIs via `https://api.crossref.org/works/<doi>`. arXiv ids via `http://export.arxiv.org/api/query?id_list=<id>`. A match means title, first author, and year agree with the text.

| Citation in these notes | How verified | Result |
|---|---|---|
| Tran et al. 2020, batch-effect benchmark, `10.1186/s13059-019-1850-9` | Crossref | Match. First author Hoa Thi Nhu Tran; *Genome Biology*; issued 2020-01-16. |
| Lähnemann et al. 2020, eleven grand challenges, `10.1186/s13059-020-1926-6` | Crossref | Match. First author David Lähnemann; *Genome Biology*; issued 2020-02-07. Not the batch-effect benchmark. |
| Luecken & Theis 2019, tutorial, `10.15252/msb.20188746` | Crossref | Match. Malte D. Luecken and Fabian J. Theis; *Molecular Systems Biology*; issued 2019-06-01. |
| Luecken et al. 2021, atlas integration, `10.1038/s41592-021-01336-8` | Crossref | Match. First author Malte D. Luecken; *Nature Methods*; issued 2021-12-23. |
| Gelman et al. 2013, *Bayesian Data Analysis*, `10.1201/b16018` | Crossref | Match on title, first author Andrew Gelman, issued 2013-11-27. Edition number is absent in Crossref, so the notes do not say “3rd ed.” |
| Brooks et al. 2011, *Handbook of Markov Chain Monte Carlo*, `10.1201/b10905` | Crossref | Match. First author Steve Brooks; issued 2011-05-10. |
| Bhardwaj et al. 2026, agentic-workflows review, `10.1007/s10791-026-10743-4` | Crossref | Match. First author Vivek Bhardwaj; *Discover Computing*; issued 2026-11-18. |
| Yao et al. 2022, ReAct, `2210.03629` | arXiv API | Match. First author Shunyu Yao; published 2022-10-06. |
| Qu et al. 2024, tool learning survey, `2405.17935` | arXiv API | Match. First author Changle Qu; published 2024-05-28. Abstract says the literature is fragmented. |
| Masterman et al. 2024, agent architectures, `2404.11584` | arXiv API | Match. First author Tula Masterman; published 2024-04-17. |
| Li 2024, LLM-based agent paradigms, `2406.05804` | arXiv API (current record, v6) | Match for the current title. First author Xinzhe Li; published 2024-06-09. |
| HTML snapshot `arxiv.org/html/2406.05804v2` | HTTP GET | 200. Page title is the older title *A Survey on LLM-Based Agents: Common Workflows and Reusable LLM-Profiled Components*. |
| Shen 2024, *LLM With Tools*, `2409.18807` | arXiv API | Match. Zhuocheng Shen; published 2024-09-24. |
| Kagan et al. 2024, `10.1016/j.xinn.2024.100658` and PMC11278797 | Crossref; PMC HTML title | Match. First author Brett J. Kagan; *The Innovation*; issued 2024-09. PMC page title matches. |
| Huggett & Lee 2024, `10.1177/03091333241263859` | Crossref | Match. First author Richard Huggett; issued 2024-06-22. |
| Herrando-Pérez, Brook & Bradshaw 2014, `10.1093/biosci/biu013` | Crossref | Match. First author Salvador Herrando-Pérez; *BioScience*; issued 2014-02-18. |
| Ancelin et al. 2025, `10.1016/j.nbt.2025.04.010` | Crossref | Match. First author Marie Ancelin; *New Biotechnology*; issued 2025-09. |
| Huber & Müssig 2025, `10.3390/biomimetics10020076` and PMC11853458 | Crossref; PMC HTML title | Match. Tim Huber and Jörg Müssig; *Biomimetics*; issued 2025-01-25. PMC page title matches. |
| Sun, Ma & Chen 2026, `10.1016/j.biocel.2026.107027` | Crossref | Match. First author Lu Sun; issued 2026-12. |
| YouTube `-LA1maNOJfM` | YouTube oEmbed | 200. Title: *Give Me 5 Season 2, Episode 2: Daina Bouquin from Anaconda*. |
| Removed: `10.1186/s13059-019-00621-z` | Crossref | HTTP 404. Not cited. |
| Removed: OpenAlex HTML search URL for “agentic workflows” | HTTP GET | HTTP 403 (challenge page). Replaced by the Crossref record above. |

**Still unverified**

- Spoken claims in the Bouquin video (no transcript retrieved).
- A published Bouquin study of pre-LLM abstract matching (not found).
- Substring mention counts and the untitled OpenAlex/arXiv sample titles from the original sampling run (not re-downloaded in this pass).
- The `ti:agentic` arXiv rows (internally inconsistent; not used as evidence).

## 7. Raw machine output

Full JSON from the initial three-field sampler is in the agent run artifact `/tmp/field_maturity_sample.json` (not committed). Reproduce with the procedure in [`field-maturity.md`](field-maturity.md) §Sampling procedure.