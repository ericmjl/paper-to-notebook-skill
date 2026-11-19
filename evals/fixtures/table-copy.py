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

    | Group | Mean completion time |
    | --- | ---: |
    | Group A | 12 seconds |
    | Group B | 8 seconds |

    Source: Table 1 of *A simulated comparison of two study groups*.
    The times are descriptive means from simulated data. They do not establish
    a causal effect.
    """)
    return


if __name__ == "__main__":
    app.run()
