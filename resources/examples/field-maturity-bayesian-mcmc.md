# Field-maturity example: Bayesian hierarchical model with MCMC

**Illustrative paper type:** A 2024–2025 methods/application paper fitting a hierarchical Bayesian model with MCMC (sampled titles in [research notes](../field-maturity-research-notes.md): Gibbs / HMC / SMC variants).

**Classification:** **Established** (primary). **Evidence:** posterior/prior/MCMC terminology stable across OpenAlex and arXiv samples; no competing umbrella neologism; surveys are textbooks/handbooks, not "fragmented field" essays.

---

## Extract snippet (agent artifact)

```yaml
field_maturity_primary: established
field_maturity_secondary: null
maturity_evidence:
  - OpenAlex 25-works sample (2022+): MCMC 34 hits, posterior 29, prior 21 (2026-11-19)
  - Papers use canonical terms without redefining "posterior distribution"
vocabulary_onboarding_plan:
  - glossary: required
  - disambiguation: optional
  - terminology_in_flux: skip
```

---

## Notebook mock (marimo cells)

### Cell: Field vocabulary (established)

```python
@app.cell
def _(mo):
    mo.md(
        r"""
        ### Vocabulary for this paper (established field)

        This paper sits in **Bayesian hierarchical modeling**. Terms below follow
        Gelman et al. (2013), *Bayesian Data Analysis* (10.1201/b16018), and contemporary MCMC practice.
        The paper's own wording is kept when we quote results.
        """
    )
    return
```

### Cell: Glossary accordion

```python
@app.cell
def _(mo):
    glossary = mo.accordion(
        {
            "Glossary": mo.md(
                """
                | Term (paper) | Definition | Symbol |
                |---|---|---|
                | **Prior** | Distribution for parameters before seeing these data | \(p(\theta)\) |
                | **Likelihood** | Sampling model for data given parameters | \(p(y \mid \theta)\) |
                | **Posterior** | Updated distribution for parameters after conditioning on data | \(p(\theta \mid y)\) |
                | **MCMC** | Markov chain Monte Carlo; simulate correlated draws whose stationary distribution is the posterior | — |
                | **Hierarchical** | Parameters of one unit are drawn from a population distribution shared across units | hyperparameters \(\phi\) |
                """
            ),
        }
    )
    glossary
    return (glossary,)
```

### Cell: Optional note (contemporary shorthand)

```python
@app.cell
def _(mo):
    mo.callout(
        mo.md(
            """
            **Search tip (as of 2026-11):** Recent literature often writes **MCMC**
            without expanding it on first use; we expand once above. Subfield papers
            may say **Gibbs** or **HMC** when those kernels apply—this paper's Methods
            names which sampler it uses.
            """
        ),
        kind="info",
    )
    return
```

### Cell: Check

```python
@app.cell
def _(mo):
    mo.ui.radio(
        options=[
            "The prior is the distribution of data given parameters",
            "The posterior combines prior and likelihood for parameters given data",
            "MCMC always returns independent draws from the posterior",
        ],
        label="After Setup, which statement matches standard Bayesian vocabulary?",
    )
    return
```

**Expected answer:** middle option. MCMC draws are generally correlated; prior is over parameters, not data.