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
    # Mean completion time

    Compare the groups in Table 1 of the dummy study. These are descriptive
    means from synthetic data.
    """)
    return


@app.cell
def _(mo):
    group = mo.ui.radio(["Group A", "Group B"], value="Group A", label="Study group")
    group
    return (group,)


@app.cell
def _(mo):
    mo.Html('<output data-testid="estimate">12 seconds</output>')
    return


if __name__ == "__main__":
    app.run()
