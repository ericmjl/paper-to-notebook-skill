# Field-maturity example: scRNA-seq integration / batch correction

**Illustrative paper type:** A single-cell genomics paper correcting **batch effects** or performing **atlas integration** before clustering cell types (benchmark: [Tran et al., 2020](https://doi.org/10.1186/s13059-019-1850-9); tutorial: [Luecken & Theis, 2019](https://doi.org/10.15252/msb.20188746); atlas integration: [Luecken et al., 2021](https://doi.org/10.1038/s41592-021-01336-8)).

**Classification:** **Interdisciplinary** (primary; biology + statistics + ML). **Evidence:** overloaded *cluster*, *feature*, *batch*, *integration*, *embedding* in OpenAlex/arXiv samples; benchmark papers exist explicitly to compare **batch-effect correction** methods; annotation guides define workflows for non-specialists.

---

## Extract snippet

```yaml
field_maturity_primary: interdisciplinary
field_maturity_secondary: null
maturity_evidence:
  - OpenAlex scRNA sample: 66 mentions of "cluster" and 20 of "batch correction" in 25 works (2026-11-19)
  - Luecken et al. 2021, Nature Methods, 10.1038/s41592-021-01336-8
vocabulary_onboarding_plan:
  - glossary: required
  - disambiguation: required
  - search_read_further: recommended
```

---

## Notebook mock

Cells hide their code. The reader sees the vocabulary, not the Python.

### Cell: Disambiguation (required)

```python
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ### Disambiguation

        Single-cell papers borrow vocabulary from **molecular biology**, **statistics**,
        and **machine learning**. This table fixes meanings **for this notebook**;
        senses in other fields appear in the third column.

        | Term | In this paper / notebook | Elsewhere | Tip |
        |---|---|---|---|
        | **Batch** | Experimental batch, donor, plate, or sequencing run that drives technical variation | ML *mini-batch* of training examples | If the Methods mention Scanpy/Seurat, batch ≈ sample ID covariate |
        | **Batch correction / integration** | Removing or modeling technical variation **across batches** while keeping biology | Generic data integration in ETL | Benchmarks often say *batch-effect correction*; atlases say *integration* |
        | **Cluster** | Group of cells with similar expression profiles (often = putative cell type/state) | Unsupervised algorithm output only | Clusters ≠ necessarily *annotated cell types* until validated |
        | **Feature** | Measured gene (or gene program) used in analysis | ML feature column | scRNA feature = gene count or normalized expression |
        | **Embedding** | Low-dimensional coordinates (UMAP, PCA, scVI latent space) | — | Same math object; biological interpretation is cell state similarity |
        | **Kernel** | *(if paper uses)* similarity kernel for graph | Genetics: regulatory *cis* kernel, etc. | Often absent in scRNA; if present, read Methods carefully |
        """
    )
    return
```

### Cell: Glossary

```python
@app.cell(hide_code=True)
def _(mo):
    mo.accordion({
        "Glossary": mo.md(
            """
            | Term (paper) | Definition | Link |
            |---|---|---|
            | **scRNA-seq** | Single-cell RNA sequencing; counts mRNA per cell | Luecken & Theis 2019 tutorial (MSB) |
            | **Cell type** | Biologically defined class; may require markers + manual annotation | Paper's marker list / reference atlas |
            | **Pseudotime** | Ordered axis of continuous state change (optional in paper) | Distinct from clinical timepoint |
            """
        )
    })
    return
```

### Cell: Search further

```python
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        **Search vocabulary (2020s dominant):**

        - Methods: `single-cell batch correction`, `scRNA integration benchmark`
        - Software: `Harmony`, `scVI`, `BBKNN` + the task (integration vs label transfer)
        - Biology: `cell type annotation` + tissue name

        **Do not** conflate *batch correction* with *label transfer* unless the paper does both.
        """
    )
    return
```

### Cell: Check

```python
@app.cell(hide_code=True)
def _(mo):
    mo.ui.radio(
        options=[
            "Batch always means mini-batch gradient descent",
            "Batch effect refers to technical variation across experimental/sample groups",
            "Cluster always means a validated cell type name",
        ],
        label="Disambiguation check",
    )
    return
```