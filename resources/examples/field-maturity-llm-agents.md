# Field-maturity example: LLM-based agent with tool use

**Illustrative paper type:** A 2025 systems paper describing an **agentic** LLM workflow with external tools (aligned with survey literature: [Tool Learning with LLMs](https://arxiv.org/abs/2405.17935), [ReAct](https://arxiv.org/abs/2210.03629)).

**Classification:** **Emergent** (primary). **Evidence:** arXiv samples 2023→2025 show rising *agentic* label (70 text hits in 200-paper cap for 2025 vs 6 in 2024 for overlapping queries); parallel terms *LLM agent*, *multi-agent*, *tool learning*, *tool use*; multiple surveys exist partly to organize fragmented naming ([research notes](../field-maturity-research-notes.md)).

---

## Extract snippet

```yaml
field_maturity_primary: emergent
field_maturity_secondary: interdisciplinary  # CS + application domain
maturity_evidence:
  - arXiv submittedDate 2025: agentic 70 hits vs llm agent 53 in LLM+agent query (cap 200)
  - Surveys 2404.11584, 2405.17935 document competing agent/tool taxonomies
vocabulary_onboarding_plan:
  - glossary: required
  - terminology_in_flux: required
  - search_read_further: recommended
```

---

## Notebook mock

Cells hide their code. The reader sees the vocabulary, not the Python.

### Cell: Terminology in flux

```python
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### Terminology in flux (emergent field)

        **Snapshot date:** 2026-11-19 (arXiv/OpenAlex keyword samples in the skill's research notes).

        | Concept | Also called | Common in recent preprints (2025 sample) | This paper says |
        |---|---|---|---|
        | LLM-driven loop of think → act → observe | **ReAct** (proper noun; Yao et al., 2022), tool-use workflow, tool-learning agent | *agentic* workflows; *multi-agent* orchestration | *(fill from paper)* |
        | Calling APIs / plugins from the model | **function calling** (vendor docs), **tool calling** (surveys), tool learning (Qu et al., 2024) | Mixed; the Qu et al. abstract says the literature is fragmented | *(fill from paper)* |
        | Single model vs many | LLM agent, language agent, autonomous agent | **LLM agent** still frequent; **agentic** rising in titles | *(fill from paper)* |

        We **keep the paper's terms** when describing their system. Search terms below help you find *related* work, not rename their modules.
        """
    )
    return
```

### Cell: Search / read further

```python
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        **Which term to use when searching (2025–2026):**

        - Broad: `LLM agent` OR `agentic` + your task domain
        - Tool-centric: `tool learning` large language model (survey taxonomy)
        - Architecture-specific: `ReAct` only when you mean interleaved reasoning and actions

        **Anchors:** [ReAct (2022)](https://arxiv.org/abs/2210.03629);
        [Tool learning survey, Qu et al. (2024)](https://arxiv.org/abs/2405.17935).
        """
    )
    return
```

### Cell: Glossary (branded + generic)

```python
@app.cell(hide_code=True)
def _(mo):
    mo.accordion({
        "Glossary": mo.md(
            """
            | Term | Meaning here | Not the same as… |
            |---|---|---|
            | **Agent** | Policy that chooses tool actions over multiple steps | Reinforcement-learning agent without an LLM (unless paper says so) |
            | **Tool** | External function/API the LLM invokes | Neural network "module" |
            | **Trajectory** | Sequence of thoughts, actions, observations | Single model completion |
            """
        )
    })
    return
```

### Cell: Check

```python
@app.cell(hide_code=True)
def _(mo):
    mo.ui.radio(
        options=[
            "ReAct is a generic word for any chatbot",
            "ReAct names interleaved reasoning traces and environment/tool actions (Yao et al., 2022)",
            "Tool learning and function calling always mean identical APIs",
        ],
        label="Terminology check",
    )
    return
```