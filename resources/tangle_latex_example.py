# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.14.0",
#     "wigglystuff>=0.6.0",
#     "plotly>=5.24.0",
# ]
# ///

# paper-to-notebook-skill-components: equations

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import math

    import marimo as mo
    import plotly.graph_objects as go
    from wigglystuff import TangleLatex

    return TangleLatex, go, math, mo


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Interactive equations with `TangleLatex`

    Widget reference, not a paper walkthrough. In a generated notebook,
    replace this with **the paper's** equation and cite its number.

    Here the equation is the Gaussian density, written as **Eq. 1** of
    this demo (the usual normal PDF). μ is the centre; σ is the width.

    $$
    p(x) = \frac{1}{\sigma\sqrt{2\pi}}
    \exp\left(-\frac{(x-\mu)^2}{2\sigma^2}\right)
    $$

    Demo ranges around a standard normal: μ from −4 to 4, σ from 0.1 to 4.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **What to try (Eq. 1).** Drag μ (pink): the bell slides. Drag σ
    (purple): the bell widens and shortens so the area stays 1. Watch the
    dashed line — that is `committed_values`, the numbers from before this
    drag.
    """)
    return


@app.cell(hide_code=True)
def _(TangleLatex, mo):
    gauss_eq = mo.ui.anywidget(
        TangleLatex(
            latex=(
                r"p(x) = \frac{1}{\note{norm}{\tangle{sigma}\sqrt{2\pi}}}"
                r"\exp\!\left(-\frac{(x-\note{center}{\tangle{mu}})^2}"
                r"{2\note{width}{\tangle{sigma}}^2}\right)"
            ),
            parameters={
                "mu": {
                    "value": 0,
                    "min_value": -4,
                    "max_value": 4,
                    "step": 0.1,
                    "digits": 1,
                    "display": "symbol",
                    "symbol": r"\mu",
                    "label": "μ",
                    "color": {"light": "#a23b78", "dark": "#f08bc2"},
                },
                "sigma": {
                    "value": 1,
                    "min_value": 0.1,
                    "max_value": 4,
                    "step": 0.1,
                    "digits": 1,
                    "display": "symbol",
                    "symbol": r"\sigma",
                    "label": "σ",
                    "color": {"light": "#6f5cbd", "dark": "#b9a8ff"},
                },
            },
            notes={
                "norm": "keeps the area under the curve at $1$",
                "center": "**μ**: where the bell is centered",
                "width": "**σ**: how wide the bell is",
            },
            reveal_all_on_drag=True,
            theme="light",
        )
    )
    return (gauss_eq,)


@app.cell(hide_code=True)
def _(gauss_eq, go, math, mo):
    mu = gauss_eq.values["mu"]
    sigma = gauss_eq.values["sigma"]
    mu0 = gauss_eq.committed_values["mu"]
    sigma0 = gauss_eq.committed_values["sigma"]

    def _normal_pdf(
        x_val: float, mu_val: float, sigma_val: float
    ) -> float:
        return math.exp(-((x_val - mu_val) ** 2) / (2 * sigma_val**2)) / (
            sigma_val * math.sqrt(2 * math.pi)
        )

    def _pdf_curve(
        mu_val: float, sigma_val: float
    ) -> tuple[list[float], list[float]]:
        x_min, x_max = -6.0, 6.0
        n_points = 201
        step = (x_max - x_min) / (n_points - 1)
        xs = [x_min + i * step for i in range(n_points)]
        ys = [_normal_pdf(x, mu_val, sigma_val) for x in xs]
        return xs, ys

    x_now, y_now = _pdf_curve(mu, sigma)
    x_before, y_before = _pdf_curve(mu0, sigma0)

    gauss_fig = go.Figure()
    gauss_fig.add_scatter(
        x=x_before,
        y=y_before,
        mode="lines",
        name="before this drag",
        line={"dash": "dash", "color": "#94a3b8", "width": 2},
    )
    gauss_fig.add_scatter(
        x=x_now,
        y=y_now,
        mode="lines",
        name="Eq. 1, current μ and σ",
        line={"color": "#a23b78", "width": 3},
        fill="tozeroy",
        fillcolor="rgba(162, 59, 120, 0.12)",
    )
    gauss_fig.update_layout(
        title="Gaussian density vs x (Eq. 1)",
        xaxis_title="x",
        yaxis_title="p(x)",
        paper_bgcolor="white",
        plot_bgcolor="white",
        template="plotly_white",
        height=380,
        legend={"orientation": "h", "y": 1.12},
        margin={"l": 50, "r": 20, "t": 60, "b": 50},
    )
    gauss_fig.update_xaxes(showgrid=True, gridcolor="#e2e8f0")
    gauss_fig.update_yaxes(showgrid=True, gridcolor="#e2e8f0", rangemode="tozero")

    peak = _normal_pdf(mu, mu, sigma)
    mo.vstack(
        [
            gauss_eq,
            mo.md(
                f"Current values: μ = {mu:g}, σ = {sigma:g}. "
                f"Peak height at $x = \\mu$ is {peak:.3f} (Eq. 1)."
            ),
            gauss_fig,
        ]
    )
    return


if __name__ == "__main__":
    app.run()
