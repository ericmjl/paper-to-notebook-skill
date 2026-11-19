# Field maturity and vocabulary onboarding

Reference for **Phase 2 (Extract)** and **Phase 3–4 (Plan / Generate)** in [`SKILL.md`](../SKILL.md). Read this when the paper sits in a field whose vocabulary may be **settled**, **in flux**, or **overloaded across disciplines**.

**Goal:** onboard the reader onto **contemporary dominant vocabulary** for that field while **never silently renaming** the paper's own terms.

---

## 1. Three maturity classes

| Class | Vocabulary character | Notebook emphasis |
|---|---|---|
| **Established** | Canonical terms; define-on-first-use is usually enough | Compact **glossary**; link to standard references |
| **Emergent** | Competing synonyms; recent coinages; shifting scope (*agentic*, *tool learning*, …) | **Terminology in flux** map + **search hints**; date-stamped "current dominant" claims |
| **Interdisciplinary** | Same word, different discipline senses (*feature*, *model*, *batch*, *cluster*, …) | **Disambiguation** table + glossary tied to *this paper's* usage |

Papers can be **mixed** (e.g. emergent methods applied in an interdisciplinary domain). Record **primary** and **secondary** class with evidence; apply the **strictest** onboarding components required by either class.

---

## 2. Classification rubric

Score each **signal** as **low / medium / high** from (a) the paper and (b) a **lightweight literature sample** (see §6). No single signal is decisive; use judgement and cite evidence in the extract artifact.

| Signal | Established (↑) | Emergent (↑) | Interdisciplinary (↑) |
|---|---|---|---|
| **Term variance** across recent papers | Same lemmas for core objects (e.g. posterior, MCMC) | Multiple labels for same idea (LLM agent vs agentic workflow vs tool-learning agent) | Same lemma, different definitions (*integration* vs *batch correction*; *cluster* as biology vs algorithm) |
| **Age of key terms** | Decades-old core terms | Many terms &lt; 5 years; surveys list "fragmented" literature | Mix of old (gene, cell type) + borrowed CS/stats terms |
| **Surveys / textbooks** | Standard texts cite stable defs | "Survey" papers organize competing frameworks | Best-practice / benchmark papers spend pages on definitions |
| **Venue spread** | Single discipline dominates | Often cs.AI / cs.CL + application verticals | Nature Methods + Bioinformatics + NeurIPS-style methods |
| **Citation spread** | Citations stay in one field cluster | Fast-moving preprint + product blog ecosystem | Citations bridge ≥2 Citation Cluster IDs (OpenAlex) or journal scopes |
| **Explicit disambiguation in paper** | Rare ("we use Gibbs…") | Occasional ("following ReAct…") | Frequent ("batch effect as in Tran et al.", "clusters of cells") |
| **"We use X to mean Y"** | Low except notation | Medium (framework branding) | High (overload resolution) |

**Mixed-field rule:** If emergent **and** interdisciplinary signals are both medium+, include both **flux** and **disambiguation** sections.

**Defaults when offline:** Infer from paper metadata (venue, keywords, citation titles). If confidence is low, ship **glossary + short disambiguation** for any term in the extract's "undefined terms" list that appears in the [overload list](#overload-starter-list) below.

---

## 3. Linguistic strategy by class

### Established

- **Define on first use** with one clause; optional tooltip to glossary.
- Prefer **contemporary dominant** forms (*MCMC* vs always spelling out; *Hamiltonian Monte Carlo* on first HMC mention).
- Glossary: **paper term → standard definition → equation/symbol** if any.
- Do **not** add flux/disambiguation sections unless the paper crosses into another class.

### Emergent

- **Map paper terms to dominant search vocabulary** without renaming in prose tied to the paper ("The authors' *X* is often called *Y* in 2025 surveys; we keep *X* when quoting the paper.").
- **Terminology in flux** section: synonyms, approximate first-use year, which label dominates in recent sample (with date stamp).
- Prefer citations to **recent surveys** for taxonomies ([example surveys in research notes](field-maturity-research-notes.md)).
- Flag **framework-branded** names (ReAct, Reflexion) as proper nouns with one-line mechanism, not generic English.

### Interdisciplinary

- **Disambiguation first** for overloaded lemmas before teaching the mechanism.
- Glossary entries: **In this paper | In discipline A | In discipline B | Common confusion**.
- When the paper imports ML onto biology (or vice versa), state **which ontology** a noun belongs to (cell, gene, embedding, cluster).
- Link benchmark/best-practice papers when the paper assumes their definition.

### Universal rules

1. **Prefer contemporary dominant vocabulary** for *further reading* and search hints only.
2. **Never silently rename** the paper's terms in quotes, equations, or figure callouts.
3. **Date-stamp** dominance claims: "In our OpenAlex/arXiv sample (2026-11-19), …".
4. **Cite evidence** (survey section, benchmark, or counted sample)—see [research notes](field-maturity-research-notes.md).

---

## 4. Notebook components (onboarding)

Place after **Setup: notation, assumptions, terms** and before core mechanism ladders unless the user needs vocabulary earlier.

| Component | Established | Emergent | Interdisciplinary | Marimo pattern |
|---|---|---|---|---|
| **Glossary** | Required (core terms + symbols) | Required | Required | `mo.accordion` or table in `mo.md` |
| **Disambiguation** | Optional | Optional | **Required** | Dedicated `### Disambiguation` section |
| **Terminology in flux** | Optional | **Required** | Optional (if emergent subtopic) | Table: alias → meaning → dominance note |
| **Search / read further** | Optional | **Recommended** | **Recommended** | Short bullet list of dominant query terms |
| **Term-drift timeline** | Rare | Recommended when ≥3 synonyms | Rare | Markdown timeline or small table |

**Glossary row template (established):**

| Term (as in paper) | Definition (this notebook) | First use (section) |
|---|---|---|

**Disambiguation row template (interdisciplinary):**

| Term | In this paper | Elsewhere (discipline) | Practical tip |
|---|---|---|---|

**Flux row template (emergent):**

| Concept | Also called… | Most common in recent literature (as of DATE) | Paper uses |
|---|---|---|---|

**Checks:** Add one informal check per required section (e.g. "In this notebook, *batch* means …").

---

## 5. Overload starter list

Trigger **disambiguation** when the paper uses these without definition (non-exhaustive):

| Term | Typical disciplines | Notes |
|---|---|---|
| model | stats, ML, biology | Generative vs statistical vs biological model |
| feature | ML, genetics | Column vs gene / peak |
| kernel | ML, genetics, chemistry | Similarity function vs genomic locus vs matrix |
| cluster | ML, biology | Algorithmic partition vs cell population |
| batch | ML training, experiments | Mini-batch vs experimental batch / sample prep |
| integration | calculus, data engineering, genomics | Data merge vs batch correction vs atlas integration |
| embedding | linear algebra, deep learning, genomics | Vector representation (shared) but different objects |
| fitness | evolution, ML | Reproductive success vs loss / score |
| entropy | physics, information theory, ecology | Same formula, different interpretations |

Extend from the paper's undefined-term list (Phase 2).

---

## 6. Lightweight literature sampling (runtime)

Run during **Extract** when network is available. **Time budget: ≤ 90 seconds, ≤ 30 works total** across all queries.

### Steps

1. **Classify the field** from title/abstract/keywords (one sentence).
2. **Query one primary API:**
   - **OpenAlex** (preferred): `GET https://api.openalex.org/works?filter=title_and_abstract.search:<3-6 keywords>&per_page=15&sort=cited_by_count:desc`  
     Optional: `from_publication_date:YYYY-01-01` for emergent fields (last 3 years).
   - **arXiv** (CS/physics/math-heavy): `export.arxiv.org/api/query` with `max_results=15`.
   - **PubMed** (biomed): optional `esearch` + `efetch` for 10 PMIDs when OpenAlex lacks abstracts.
3. **Count** (case-insensitive substrings in title+abstract) for:
   - 5–10 **candidate terms** from the paper and extract list;
   - 3–5 **synonym candidates** for emergent topics.
4. **Record** counts, query URL, date, and top 3 titles in the extract artifact (or scratch JSON).
5. **Decide** primary maturity class; note confidence (high/medium/low).

### Caps and degradation

| Limit | Value |
|---|---|
| Works retrieved | 30 total |
| HTTP timeout | 15 s per request |
| Retries | 1 |

**Offline / API failure:** Set class from rubric signals detectable in-paper only; add notebook TODO: "Vocabulary dominance not verified against literature sample." Still ship glossary; use optional disambiguation if interdisciplinary cues are obvious from citations (e.g. scRNA + deep learning).

### What **not** to do at runtime

- No full bibliometric study.
- No mental arithmetic on large counts—use script or tallies in scratch.
- Do not fabricate citations or counts (see audit trail in [research notes](field-maturity-research-notes.md)).

---

## 7. Phase 2 extract fields (add to intermediate picture)

Alongside existing extract bullets, record:

- `field_maturity_primary`: established | emergent | interdisciplinary
- `field_maturity_secondary`: optional
- `maturity_evidence`: short bullet list with links or counts
- `vocabulary_onboarding_plan`: which notebook components are required
- `dominant_terms_snapshot`: table term → count (optional) with `as_of_date`

---

## 8. Validation hook

When running planned evals (see `SKILL.md` §5), include a **vocabulary onboarding check**:

- Established paper: glossary covers all symbols in the first equation used in the ladder.
- Emergent paper: flux map lists ≥2 aliases for the core framework term; dominance claim is date-stamped.
- Interdisciplinary paper: disambiguation covers every term from the overload starter list that appears in the paper.

---

## 9. Worked notebook examples

See [`examples/field-maturity-bayesian-mcmc.md`](examples/field-maturity-bayesian-mcmc.md), [`examples/field-maturity-llm-agents.md`](examples/field-maturity-llm-agents.md), and [`examples/field-maturity-scrna-integration.md`](examples/field-maturity-scrna-integration.md).

---

## Credits and related reading

- Design discussion: Eric Ma; motivation from Daina Bouquin (domain-grounded evaluation; interdisciplinary communication).
- Research sampling: [`field-maturity-research-notes.md`](field-maturity-research-notes.md).
- Explanation ladders (orthogonal): [`explanation-levels.md`](explanation-levels.md).