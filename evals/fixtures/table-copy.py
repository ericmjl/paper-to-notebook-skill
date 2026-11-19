import marimo

__generated_with = "0.17.6"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md("""
    ## Table 1. Mean completion time

    Source: Table 1 of *A simulated comparison of two study groups*.
    The times are descriptive means from simulated data. They do not establish
    a causal effect.
    """)
    return


@app.cell
def _(mo):
    mo.ui.table(
        [
            {"Group": "Group A", "Mean completion time": 12},
            {"Group": "Group B", "Mean completion time": 8},
        ],
        format_mapping={"Mean completion time": "{} seconds"},
        selection=None,
    )
    return


if __name__ == "__main__":
    app.run()
