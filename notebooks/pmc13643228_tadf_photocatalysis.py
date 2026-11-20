# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.14.0",
#     "anywidget>=0.9.0",
#     "traitlets>=5.14.0",
#     "plotly>=5.24.0",
#     "wigglystuff>=0.6.0",
# ]
# ///

# paper-to-notebook-skill-components: figure-walkthroughs, method-diagrams, final-quiz

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium", auto_download=["html"])

with app.setup(hide_code=True):
    from pathlib import Path

    import marimo as mo
    import plotly.graph_objects as go
    import wigglystuff
    from figure_annotator_widget import FigureAnnotatorWidget
    from mermaid_view import MermaidView
    from paper_quiz import PaperQuiz

    LEVELS = ["Child", "Teen", "Undergrad", "Grad student", "Expert"]
    SINGLET_COLOR = "#e11d48"
    TRIPLET_COLOR = "#2563eb"
    SUM_COLOR = "#64748b"
    DEMO_COLOR = "#0d9488"

    # Central values from the phenol / PC2+ / MeCN series. Uncertainties are
    # stated in the prose; this sketch uses the centers only.
    ETA_CE_S_PHENOL = 0.028
    ETA_CE_T_PHENOL = 0.42
    PHENOL_LOW_MM = 0.3
    PHENOL_HIGH_MM = 13.0
    PHI_Q_S_LOW = 0.03
    PHI_Q_T_LOW = 0.65
    PHI_Q_S_HIGH = 0.54
    PHI_Q_T_HIGH = 0.30

    def show_check(tabs, checks, answers):
        """Show the check for the open tab of a ladder, with feedback once answered.

        :param tabs: Ladder tabs whose ``value`` is the open level name.
        :param checks: ``mo.ui.dictionary`` of widgets keyed by level.
        :param answers: Mapping of level name to ``correct``, optional ``tolerance``, and ``why``.
        :returns: A stack of the prompt, the widget, and the feedback.
        """
        level = tabs.value
        answer = answers[level]
        response = checks.value[level]
        if response in (None, ""):
            feedback = mo.md("*Answer to see feedback.*")
        elif answer["correct"] is None:
            feedback = mo.callout(
                mo.md(f"**Compare with ours:** {answer['why']}"), kind="info"
            )
        else:
            if isinstance(answer["correct"], float):
                try:
                    right = abs(float(response) - answer["correct"]) <= answer.get(
                        "tolerance", 0.01
                    )
                except ValueError:
                    right = False
            else:
                right = response == answer["correct"]
            feedback = mo.callout(
                mo.md(("**Right.** " if right else "**Not quite.** ") + answer["why"]),
                kind="success" if right else "warn",
            )
        return mo.vstack(
            [mo.md(f"**Check your understanding ({level})**"), checks[level], feedback]
        )

    def plain_feedback(widget, correct, why):
        """Feedback for a single radio that is not inside a ladder.

        :param widget: A radio or text widget.
        :param correct: The option string that counts as right.
        :param why: Reasoning, with the paper location.
        :returns: A callout, or a prompt if the reader has not answered.
        """
        response = widget.value
        if response in (None, ""):
            return mo.md("*Answer to see feedback.*")
        right = response == correct
        return mo.callout(
            mo.md(("**Right.** " if right else "**Not quite.** ") + why),
            kind="success" if right else "warn",
        )


@app.cell(hide_code=True)
def hero():
    hero_banner = mo.Html(
        """
        <div style="font-family: Georgia, serif; border: 1px solid #e2e8f0; border-radius: 14px; overflow: hidden;">
          <div style="background: #0f172a; color: #f8fafc; padding: 22px 26px 18px;">
            <div style="font-family: ui-sans-serif, system-ui; letter-spacing: .14em; text-transform: uppercase; font-size: 12px; color: #99f6e4;">Chemical Science, 2026 · a learning notebook</div>
            <h1 style="margin: 8px 0 0; font-size: 30px; line-height: 1.2; font-weight: 650;">When less quencher makes more radicals</h1>
            <p style="margin: 10px 0 0; max-width: 40rem; color: #e2e8f0; font-size: 17px;">A TADF photocatalyst can waste a photon if the quencher catches the short-lived singlet before the long-lived triplet is formed.</p>
          </div>
          <svg viewBox="0 0 640 92" width="100%" height="92" role="img" aria-label="Two paths from an excited catalyst: a short path that mostly recombines, and a long path that more often escapes.">
            <rect width="640" height="92" fill="#f8fafc"/>
            <circle cx="46" cy="46" r="16" fill="#0f172a"/>
            <text x="46" y="50" text-anchor="middle" fill="white" font-size="11" font-family="ui-sans-serif, system-ui">PC*</text>
            <path d="M70 36 H210" stroke="#e11d48" stroke-width="3" fill="none"/>
            <path d="M70 58 H360" stroke="#2563eb" stroke-width="3" fill="none"/>
            <rect x="210" y="24" width="78" height="24" rx="12" fill="#fff1f2" stroke="#e11d48"/>
            <text x="249" y="40" text-anchor="middle" fill="#9f1239" font-size="11" font-family="ui-sans-serif, system-ui">mostly back</text>
            <rect x="360" y="46" width="78" height="24" rx="12" fill="#eff6ff" stroke="#2563eb"/>
            <text x="399" y="62" text-anchor="middle" fill="#1d4ed8" font-size="11" font-family="ui-sans-serif, system-ui">more escape</text>
            <text x="520" y="40" fill="#9f1239" font-size="13" font-family="ui-sans-serif, system-ui">short path · singlet</text>
            <text x="520" y="64" fill="#1d4ed8" font-size="13" font-family="ui-sans-serif, system-ui">long path · triplet</text>
          </svg>
        </div>
        """
    )
    hero_citation = mo.md(
        r"""
        Fina, Schmitz, Bertrams, Bellatreccia, Burdenski, Hansmann, Ceroni, and Kerzig,
        *Chemical Science*, **2026**, *17*, 21624–21634.
        DOI [10.1039/d6sc06836g](https://doi.org/10.1039/d6sc06836g)
        (checked on the Crossref API: journal article, Royal Society of Chemistry, issued 2026, volume 17, issue 44, those pages; record created 2026-09-28; license CC BY 3.0).
        PMCID [PMC13643228](https://pmc.ncbi.nlm.nih.gov/articles/PMC13643228/).
        PMID 42846667 is the identifier on the PMC record.

        **Assumed reader.** An undergraduate who has met orbitals, electrons, and concentration, and who has not worked in photoredox catalysis. The level picker below retells two ideas for a younger reader, a graduate student, or someone who already reads this literature. **Our demo** plots are marked wherever they go beyond a number printed in the paper.

        Open this file with `uvx marimo edit --sandbox notebooks/pmc13643228_tadf_photocatalysis.py`.
        """
    )
    mo.vstack([hero_banner, hero_citation])
    return


@app.cell(hide_code=True)
def cell_tour():
    walkthrough = mo.ui.anywidget(
        wigglystuff.CellTour(
            steps=[
                {
                    "cell_name": "hero",
                    "title": "The paper, in one picture",
                    "description": "Background section. You are at the top. The drawing is a sketch of the claim: a short path that mostly undoes the electron transfer, and a long path that more often lets the pieces escape.",
                },
                {
                    "cell_name": "level_picker",
                    "title": "Choose how technical the ladders are",
                    "description": "Hands-on section. Pick a level. The two ladders further down open on that choice. You can switch later without losing the quiz.",
                },
                {
                    "cell_name": "why_it_matters",
                    "title": "Why quenching is the wrong scoreboard",
                    "description": "Background section. Read the usual habit this paper pushes against: more quencher, more quenching, supposedly more reaction.",
                },
                {
                    "cell_name": "intuition_pick",
                    "title": "Commit before the traces",
                    "description": "Try-it-yourself section. Two flasks differ only in how much 4-tert-butylphenol they contain. Choose which one you think frees more catalyst radical, then read the reveal underneath.",
                },
                {
                    "cell_name": "glossary",
                    "title": "Words the paper expects you to know",
                    "description": "Background section. Singlet, triplet, cage escape, and quantum yield, in the sense this paper uses them. The disambiguation table is the next cell.",
                },
                {
                    "cell_name": "figure_tour",
                    "title": "Walk Figures 1 to 6",
                    "description": "Hands-on section. One tab per figure, inside a panel you can drag. Use Prev and Next inside the open tab. Hover a colored badge to light the same region on the figure. The captions are the paper's. The words stay with what the main text states.",
                },
                {
                    "cell_name": "escape_ladder",
                    "title": "Same mechanism, five depths",
                    "description": "Background section. This ladder is cage escape. Stay on your level, or open another tab to see what was left out. The check sits under the tabs.",
                },
                {
                    "cell_name": "materials_methods",
                    "title": "What they actually did",
                    "description": "Hands-on section. This is the paper's experimental and computational pipeline, not a figure they printed. Step through it. Drag to pan; Ctrl-scroll, pinch, or the +/− buttons zoom; Fit resets the view. The level picker above changes how much detail the boxes show.",
                },
                {
                    "cell_name": "evidence",
                    "title": "What was actually measured",
                    "description": "Background section. Four catalyst–quencher pairs, the continuous-light model, and the one preparative reaction. Numbers here are quoted from the paper.",
                },
                {
                    "cell_name": "demo_chart",
                    "title": "A labeled sketch, not Figure 4",
                    "description": "Hands-on section. The chart weights the reported quenching yields by the reported phenol cage-escape efficiencies. The code stays hidden. It is not a fit to the paper's kinetic plot.",
                },
                {
                    "cell_name": "quiz_intro",
                    "title": "Five questions on the paper",
                    "description": "Wrap-up. Answer from the paper's claims, not from the demo plot. Each question tells you why the option you picked does or does not match the text.",
                },
            ],
            auto_start=False,
            show_progress=True,
        )
    )
    walkthrough
    return


@app.cell(hide_code=True)
def level_picker():
    mo.md(
        r"""
        ## How technical should this be?

        The two ladders open on this choice. Child and Teen use the door story. From Undergrad on, the symbols are the paper's. Default is **Undergrad**, for a reader who can follow a rate but has not read this subfield.
        """
    )
    reader_level = mo.ui.dropdown(
        options=LEVELS,
        value="Undergrad",
        label="Explain the ladders at this level:",
    )
    reader_level
    return (reader_level,)


@app.cell(hide_code=True)
def why_it_matters():
    mo.md(r"""
    ## Why this paper

    A photoredox cycle starts when a catalyst absorbs a photon and then meets a **quencher**, a partner that takes or gives an electron. The usual first measurement is a Stern–Volmer plot: how completely that partner turns off the catalyst's glow. The introduction says it is then natural to push the quencher concentration up, on the idea that more quenching means more reaction.

    The glow going out does not mean a free radical was released. After the electron moves, the two products are still a **geminate pair** inside a solvent cage. They can fall back to the starting molecules (charge recombination, CR on Fig. 1A) or separate (cage escape, CE). Only the separated pair can go on to do chemistry.

    Fina and coworkers use catalysts whose singlet and triplet excited states are both redox-active. The triplet lives much longer, so a low quencher concentration is enough to quench it. The singlet is so short-lived that only a high concentration catches it, and catching it also blocks intersystem crossing into the triplet. Their claim, tested by nanosecond transient absorption rather than by a Stern–Volmer plot alone, is that the low-concentration route makes more free radicals.
    """)
    return


@app.cell(hide_code=True)
def intuition_pick():
    mo.md(
        r"""
        ## Before the symbols: two flasks

        Both flasks are acetonitrile with the same small amount of the photocatalyst PC$^{2+}$ (5 µM, iso-absorbing, 355 nm, 5.5 mJ per pulse; Fig. 2 caption). They differ only in the concentration of 4-*tert*-butylphenol. The detector watches 450 nm, where the reduced catalyst radical absorbs. Which flask do you expect to show the **larger** signal of freed radical?
        """
    )
    flask_choice = mo.ui.radio(
        options=[
            "0.3 mM phenol, the dilute flask",
            "13 mM phenol, forty times more quencher",
        ],
        label="I expect more free PC•+ in…",
    )
    flask_choice
    return (flask_choice,)


@app.cell(hide_code=True)
def intuition_reveal(flask_choice):
    flask_why = (
        "Fig. 2 and the paragraph that introduces it. At 0.3 mM, "
        "$\\Phi_{\\mathrm{q,T}} = 0.65$ and $\\Phi_{\\mathrm{q,S}} = 0.03$: "
        "almost all of the quenching is from the triplet, and the 450 nm trace is the large one. "
        "At 13 mM, $\\Phi_{\\mathrm{q,T}} = 0.30$ and $\\Phi_{\\mathrm{q,S}} = 0.54$: "
        "more of the excited states are quenched in total, and the free-radical signal is markedly smaller."
    )
    mo.vstack(
        [
            mo.md("### What Fig. 2 shows"),
            plain_feedback(
                flask_choice,
                "0.3 mM phenol, the dilute flask",
                flask_why,
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def glossary():
    mo.md(r"""
    ## Setup: words this paper uses

    **Field class: established, with an interdisciplinary borrow.**
    The objects in the argument — singlet, triplet, intersystem crossing, cage escape, Stern–Volmer quenching, quantum yield — are standard photochemistry. The paper points at textbooks (Turro; Balzani, Ceroni, and Juris; Klán and Wirz) and at a Chemical Reviews article on cage escape (Goodwin, Dickenson, Ripak, Deetz, and coworkers, *Chem. Rev.* **2024**, DOI [10.1021/acs.chemrev.3c00930](https://doi.org/10.1021/acs.chemrev.3c00930), Crossref title *Factors that Impact Photochemical Cage Escape Yields*; the paper's ref. 23).
    The borrowed word is **TADF**. It comes from OLED materials and is used here as a photocatalyst. That second life is surveyed by Bryden and Zysman-Colman, *Chem. Soc. Rev.* **2021**, *50*, 7587–7680, DOI [10.1039/d1cs00198a](https://doi.org/10.1039/d1cs00198a) (Crossref; the paper's ref. 37).

    A live OpenAlex sample on 2026-11-20 did not reach the skill's 30-work target: one query was rate-limited, and `title_and_abstract.search` for "cage escape photoredox singlet triplet" returned 3 works, two of them this paper and its data deposit. The class above is from the paper's own citations and venue, not from a term count. There is no terminology-in-flux table: the paper does not juggle competing names for cage escape. "Less is more" is the authors' phrase for this result, not a community label.

    | Term as the paper uses it | In this notebook | Where it first matters |
    |---|---|---|
    | TADF | Thermally activated delayed fluorescence: $S_1$ and $T_1$ lie close enough (the papers they cite use $\Delta E_{\mathrm{S-T}} < 0.3$ eV) that the triplet can repopulate the singlet, and both states can do redox chemistry | Introduction; Fig. 1 |
    | $S_1$, $^1$PC* | Lowest singlet excited state. For PC$^{2+}$ in MeCN, Fig. 1B prints $\tau_{0,\mathrm{S}} = 17$ ns and $E(^1{^*}\mathrm{PC}^{2+}\mid\mathrm{PC}^{\bullet+}) = +2.0$ V vs SCE | Fig. 1B |
    | $T_1$, $^3$PC* | Lowest triplet. Fig. 1B prints $\tau_{0,\mathrm{T}} = 44$ µs and $E(^3{^*}\mathrm{PC}^{2+}\mid\mathrm{PC}^{\bullet+}) = +1.8$ V vs SCE | Fig. 1B |
    | isc, $\Phi_{\mathrm{isc}}$ | Intersystem crossing, singlet to triplet. Without quencher, $\Phi_{\mathrm{isc}} = 0.68$ (text, pointing at Fig. 1) | Fig. 1B; Table 1 |
    | risc | Reverse intersystem crossing, triplet back to singlet. Included in the exact TADF treatment in the SI; not what makes the triplet more productive | Section on the non-TADF approximation |
    | Quencher, Q | The redox partner that deactivates the excited catalyst. Here the quenchers are electron donors | Fig. 1C |
    | $\Phi_{\mathrm{q,S}}$, $\Phi_{\mathrm{q,T}}$ | Quantum yield of quenching from that excited state: the fraction of absorbed photons whose excited state is intercepted by Q | Fig. 2 discussion; Table 1 |
    | $\eta_{\mathrm{q,S}}$, $\eta_{\mathrm{isc}}$ | Efficiencies of singlet quenching and of intersystem crossing in the presence of Q. Table 1 defines $\Phi_{\mathrm{q,T}} = \eta_{\mathrm{isc}} \times \eta_{\mathrm{q,T}}$ | Table 1 |
    | Solvent cage | The solvent shell around the geminate radical pair just after electron transfer | Fig. 1A |
    | CE, $\eta_{\mathrm{ce,S}}$, $\eta_{\mathrm{ce,T}}$ | Cage escape: the pair separates before it recombines. $\eta_{\mathrm{ce}}$ is the fraction of pairs born from that state that escape | After Table 1 |
    | CR | Geminate charge recombination: back electron transfer inside the cage, back to the ground-state starting materials | Fig. 1A |
    | $\Phi_{\mathrm{r,tot}}$ | Free-radical quantum yield. The text of eqn (1) defines it as free radicals formed per excited state produced by photon absorption. The typeset equation is an image and is not copied below | Eqn (1); Fig. 2 inset |
    | PC$^{2+}$ | The dicationic TADF photocatalyst in this study, a π-extended heterocycle/carbene hybrid (Results; the synthesis paper is Ritu, Schmitz, Burdenski, and coworkers, *ACS Catal.* **2025**, *15*, 16718–16730, DOI [10.1021/acscatal.5c06069](https://doi.org/10.1021/acscatal.5c06069), Crossref; this paper's ref. 54) | Fig. 1B |
    | 4CzIPN, DMA | A second TADF catalyst, in toluene, quenched by the aromatic amine DMA | Fig. 6A |
    | SO$_2$TDS$^{2-}$, HAsc$^-$ | A non-TADF organic catalyst in water, quenched by ascorbate monoanion | Fig. 6B |

    **Search terms, if you want the surrounding literature.** Use these; do not rename the paper's symbols when you quote a figure.

    - thermally activated delayed fluorescence photocatalyst
    - cage escape quantum yield photoredox
    - Stern–Volmer quenching versus cage escape
    - 4CzIPN triplet quenching
    """)
    return


@app.cell(hide_code=True)
def glossary_ask():
    glossary_choice = mo.ui.radio(
        options=[
            "The fraction of geminate radical pairs, born from that excited state, that separate before they recombine",
            "The fraction of ground-state catalyst molecules that absorb a photon",
            "The chemical yield of isolated product after the flask is worked up",
        ],
        label="In this paper, a cage-escape efficiency η_ce is…",
    )
    glossary_choice
    return (glossary_choice,)


@app.cell(hide_code=True)
def glossary_feedback(glossary_choice):
    plain_feedback(
        glossary_choice,
        "The fraction of geminate radical pairs, born from that excited state, that separate before they recombine",
        "That is how the authors use $\\eta_{\\mathrm{ce,T}} = 0.42 \\pm 0.02$: "
        "42% of the geminate pairs from a triplet quenching event escape the cage "
        "(paragraph after experiment series 1a). "
        "It is not the absorption efficiency, and it is not an isolated product yield.",
    )
    return


@app.cell(hide_code=True)
def disambiguation():
    mo.md(r"""
    ## Disambiguation

    TADF is the term that travels between fields. A few other ordinary words are easy to hear in the wrong sense. The middle column is this paper only.

    | Term | In this paper | Elsewhere | Practical tip |
    |---|---|---|---|
    | TADF | A photocatalyst with a small $S_1$–$T_1$ gap, so both states can transfer an electron. Delayed fluorescence is the spectroscopic signature | In OLED papers, a TADF dye is an emitter design whose point is the light it emits, not a radical it releases | Keep the paper's "TADF photocatalyst". Do not swap in "OLED emitter" when you mean PC$^{2+}$ |
    | Yield | Usually a **quantum yield**: events per photon, or per excited state formed (eqn 1). The pinacol "performance" in Section S3.2 is a separate, preparative comparison | An isolated chemical yield is mass of product out over mass expected | If a sentence has no "quantum", check which one it is before you compare numbers |
    | Quencher | The electron donor that deactivates $S_1$ or $T_1$ (phenol, naphthalene, DMA, ascorbate) | In other labs, a quencher is any species that shortens a lifetime, including an impurity | Here the quencher is an intentional reactant, sometimes the sacrificial donor and sometimes, in the SI model, the substrate itself |
    | Model | A kinetic scheme for excited-state populations and cage escape, plus a continuous-irradiation simulation from the authors' earlier code | A statistical model or a machine-learning model | Nothing in this paper is fitted by a learning algorithm |
    | Cage | The solvent shell around the geminate radical pair | A covalent molecular cage, or a sample-prep "batch" | Fig. 1A draws the cage as brackets around the radical pair |

    The strict onboarding for an established field is the glossary. The disambiguation is here because TADF is shared with OLED photophysics, which is the secondary, interdisciplinary part of the classification.
    """)
    return


@app.cell(hide_code=True)
def disambiguation_ask():
    yield_choice = mo.ui.radio(
        options=[
            "The free-radical quantum yield, radicals per excited state",
            "The isolated mass yield of a worked-up organic product",
            "The fluorescence quantum yield of the catalyst with no quencher present",
        ],
        label="When the authors say the yield falls as the quencher gets more concentrated, which yield do they mean in Fig. 2?",
    )
    yield_choice
    return (yield_choice,)


@app.cell(hide_code=True)
def disambiguation_feedback(yield_choice):
    plain_feedback(
        yield_choice,
        "The free-radical quantum yield, radicals per excited state",
        "Fig. 2's inset is $\\Phi_{\\mathrm{r,tot}}$ against quencher concentration. "
        "Equation (1)'s prose defines that quantity as free radicals per excited state produced by absorption. "
        "The ~50% preparative comparison is a different experiment (Section S3.2), on a different catalyst.",
    )
    return


@app.cell(hide_code=True)
def notebook_paths():
    notebook_dir = Path(__file__).resolve().parent
    return (notebook_dir,)


@app.cell(hide_code=True)
def figure_tour(
    notebook_dir, fig3_annotator, fig4_annotator, fig5_annotator, fig6_annotator
):
    mo.md(
        r"""
        ## Figures 1–6

        Figs. 1–6 are every main-text figure, one tab each, in a panel you can drag while you scroll. An image was obtained for each of them.

        Boxes stay hidden until you hover a badge or the drawing. Coordinates are the 100×100 percentage boxes from the repository's figure-annotation example, checked again with `scripts/figure_annotation_helper.py audit` before this notebook was written. The words on the badges were rewritten so they do not quote absorbances or quantum yields that the main text never prints. Equations (1), (3), and (4) are graphics in the PMC XML; they are not redrawn here.
        """
    )
    fig1_annotator = FigureAnnotatorWidget()
    fig1_annotator.load_image_from_path(notebook_dir / "figures" / "fig1.webp")
    fig1_annotator.caption = (
        "Fig. 1. (A) Spin-dependent pathways following excitation of a general TADF "
        "photocatalyst (PC), showing competition between S1 and T1 quenching and, "
        "after electron transfer, between cage escape (CE) and geminate charge "
        "recombination (CR). (B) Selected TADF photocatalyst (PC2+) and relevant "
        "photophysical characteristics in acetonitrile solution. (C) Quenchers used "
        "as electron donors and their oxidation potentials."
    )
    fig1_annotator.annotations = [
        {
            "id": "ground_state",
            "label": "1PC ground state",
            "box": [35.56, 43.19, 5.44, 5.47],
            "color": "#0284c7",
            "description": "Ground state drawn at the bottom of panel A",
        },
        {
            "id": "absorption",
            "label": "Excitation",
            "box": [37.5, 14.15, 1.94, 30.12],
            "color": "#0d9488",
            "description": "The arrow that populates the singlet excited state",
        },
        {
            "id": "singlet_excited",
            "label": "1PC* singlet",
            "box": [36.25, 6.86, 6.69, 5.68],
            "color": "#e11d48",
            "description": "Singlet excited state. Fig. 1B gives it a 17 ns lifetime in MeCN",
        },
        {
            "id": "triplet_excited",
            "label": "3PC* triplet",
            "box": [51.38, 10.18, 6.75, 5.68],
            "color": "#2563eb",
            "description": "Triplet excited state. Fig. 1B gives it a 44 microsecond lifetime in MeCN",
        },
        {
            "id": "isc_risc",
            "label": "isc and risc",
            "box": [43.56, 6.43, 7.31, 16.61],
            "color": "#9333ea",
            "description": "Both crossing directions are drawn. The paper's cited TADF criterion is a gap below 0.3 eV, not a number measured on this arrow",
        },
        {
            "id": "singlet_quenching",
            "label": "Singlet radical pair",
            "box": [14.12, 18.65, 15.75, 8.57],
            "color": "#dc2626",
            "description": "Geminate pair born from the singlet, still inside the solvent cage",
        },
        {
            "id": "triplet_quenching",
            "label": "Triplet radical pair",
            "box": [49.88, 20.15, 15.75, 8.25],
            "color": "#7c3aed",
            "description": "Geminate pair born from the triplet",
        },
        {
            "id": "cage_escape_left",
            "label": "CE from the singlet pair",
            "box": [17.03, 25.99, 6.12, 10.5],
            "color": "#059669",
            "description": "Cage escape. For the phenol this efficiency is 0.028",
        },
        {
            "id": "cage_escape_right",
            "label": "CE from the triplet pair",
            "box": [62.38, 26.53, 6.12, 10.5],
            "color": "#0d9488",
            "description": "Cage escape. For the phenol this efficiency is 0.42",
        },
        {
            "id": "cr_left",
            "label": "CR, spin-allowed",
            "box": [27.06, 32.37, 6.12, 10.5],
            "color": "#ea580c",
            "description": "Back electron transfer from the singlet pair. The ground state is a singlet, so this path is spin-allowed",
        },
        {
            "id": "cr_right",
            "label": "CR, spin-forbidden",
            "box": [49.25, 28.89, 6.12, 10.5],
            "color": "#d97706",
            "description": "Back electron transfer from the triplet pair. The paper marks this path spin-forbidden",
        },
        {
            "id": "pc_structure",
            "label": "PC2+ structure",
            "box": [0.25, 61.52, 19.88, 38.2],
            "color": "#0284c7",
            "description": "The dicationic catalyst drawn in panel B, with two SbF6 counterions on the figure",
        },
        {
            "id": "pc_redox_s1",
            "label": "Singlet potential +2.0 V",
            "box": [20.62, 69.88, 24.94, 4.82],
            "color": "#e11d48",
            "description": "Excited-state reduction potential of the singlet, vs SCE, as printed in Fig. 1B",
        },
        {
            "id": "pc_redox_t1",
            "label": "Triplet potential +1.8 V",
            "box": [20.62, 75.13, 24.94, 4.93],
            "color": "#2563eb",
            "description": "Excited-state reduction potential of the triplet, vs SCE, as printed in Fig. 1B",
        },
        {
            "id": "pc_lifetimes",
            "label": "17 ns and 44 µs",
            "box": [28.38, 81.35, 9.5, 10.5],
            "color": "#059669",
            "description": "Unquenched lifetimes in MeCN from Fig. 1B. Our arithmetic: 44 µs is about 2600 times 17 ns",
        },
        {
            "id": "pc_phi_isc",
            "label": "Φ_isc = 0.68",
            "box": [28.5, 92.5, 9.25, 4.82],
            "color": "#9333ea",
            "description": "Intersystem-crossing efficiency with no quencher. The text quotes 0.68 and points at Fig. 1",
        },
        {
            "id": "quencher_np",
            "label": "Naphthalene, +1.61 V",
            "box": [50.75, 65.06, 17.44, 26.8],
            "color": "#dc2626",
            "description": "Oxidation potential vs SCE, Fig. 1C and the Results text",
        },
        {
            "id": "quencher_tbuphoh",
            "label": "4-tert-butylphenol, +1.65 V",
            "box": [68.56, 64.95, 28.5, 26.26],
            "color": "#7c3aed",
            "description": "Oxidation potential vs SCE, Fig. 1C and the Results text",
        },
    ]
    fig1_annotator.tour_steps = [
        {
            "title": "1. Light makes the singlet",
            "target_ids": ["ground_state", "absorption", "singlet_excited"],
            "html": (
                "<p>The catalyst starts at the "
                '<a class="fig-ref" data-target="ground_state">ground state</a>. '
                "Absorption "
                '(<a class="fig-ref" data-target="absorption">the vertical arrow</a>) '
                "reaches the "
                '<a class="fig-ref" data-target="singlet_excited">singlet excited state</a>. '
                "Fig. 1B gives that state a 17 ns lifetime in acetonitrile.</p>"
            ),
        },
        {
            "title": "2. Intersystem crossing fills the triplet",
            "target_ids": ["singlet_excited", "triplet_excited", "isc_risc", "pc_phi_isc"],
            "html": (
                "<p>The "
                '<a class="fig-ref" data-target="isc_risc">isc / risc arrows</a> '
                "connect the "
                '<a class="fig-ref" data-target="singlet_excited">singlet</a> '
                "to the "
                '<a class="fig-ref" data-target="triplet_excited">triplet</a>. '
                "With no quencher, "
                '<a class="fig-ref" data-target="pc_phi_isc">Φ_isc = 0.68</a> '
                "(text, citing Fig. 1). The literature criterion the introduction quotes "
                "is a singlet–triplet gap below 0.3 eV. This figure does not print that gap. "
                "It does print excited-state potentials of +2.0 V and +1.8 V vs SCE, a 0.2 V difference.</p>"
            ),
        },
        {
            "title": "3. Quenching leaves a caged radical pair",
            "target_ids": ["singlet_quenching", "triplet_quenching"],
            "html": (
                "<p>Electron transfer from the singlet leaves a "
                '<a class="fig-ref" data-target="singlet_quenching">singlet radical pair</a>. '
                "Electron transfer from the triplet leaves a "
                '<a class="fig-ref" data-target="triplet_quenching">triplet radical pair</a>. '
                "The introduction's assumption, which it attributes to spin retention, is that the pair is born with the spin of the excited state that made it.</p>"
            ),
        },
        {
            "title": "4. Escape or recombine",
            "target_ids": [
                "cage_escape_left",
                "cage_escape_right",
                "cr_left",
                "cr_right",
            ],
            "html": (
                "<p>Each pair can "
                '<a class="fig-ref" data-target="cage_escape_left">escape (singlet side)</a> '
                "or "
                '<a class="fig-ref" data-target="cage_escape_right">escape (triplet side)</a>, '
                "or recombine: "
                '<a class="fig-ref" data-target="cr_left">spin-allowed from the singlet pair</a>, '
                '<a class="fig-ref" data-target="cr_right">spin-forbidden from the triplet pair</a>. '
                "For 4-tert-butylphenol the measured efficiencies are "
                "η_ce,S = 0.028 ± 0.005 and η_ce,T = 0.42 ± 0.02.</p>"
            ),
        },
        {
            "title": "5. Both quenchers can feed both excited states",
            "target_ids": [
                "pc_structure",
                "pc_redox_s1",
                "pc_redox_t1",
                "pc_lifetimes",
                "quencher_np",
                "quencher_tbuphoh",
            ],
            "html": (
                "<p>Panel B is "
                '<a class="fig-ref" data-target="pc_structure">PC2+</a>, '
                "with "
                '<a class="fig-ref" data-target="pc_redox_s1">+2.0 V</a> '
                "and "
                '<a class="fig-ref" data-target="pc_redox_t1">+1.8 V</a> '
                "vs SCE, and "
                '<a class="fig-ref" data-target="pc_lifetimes">lifetimes 17 ns and 44 µs</a>. '
                "Panel C is "
                '<a class="fig-ref" data-target="quencher_np">naphthalene at +1.61 V</a> '
                "and "
                '<a class="fig-ref" data-target="quencher_tbuphoh">the phenol at +1.65 V</a>. '
                "Both oxidation potentials sit below both excited-state potentials, so electron transfer is downhill from either state. "
                "Our arithmetic from the two printed lifetimes: 44 µs / 17 ns is about 2600.</p>"
            ),
        },
    ]

    fig2_annotator = FigureAnnotatorWidget()
    fig2_annotator.load_image_from_path(notebook_dir / "figures" / "fig2.webp")
    fig2_annotator.caption = (
        "Fig. 2. Time-resolved absorption traces recorded at λ = 450 nm, corresponding "
        "to PC•+ generated via photoinduced electron transfer, upon 355 nm laser "
        "excitation (5.5 mJ per pulse) of two iso-absorbing acetonitrile solutions "
        "containing 5 µM PC2+ and different concentrations of 4-tbuPhOH. Inset: "
        "measured quantum yields for free radical production as function of quencher "
        "concentration. Further explanations are given in the text."
    )
    fig2_annotator.annotations = [
        {
            "id": "y_axis_main",
            "label": "ΔA at 450 nm",
            "box": [0.25, 25.93, 3.81, 31.79],
            "color": "#0284c7",
            "description": "Transient absorbance of the reduced catalyst. The text does not print a plateau value",
        },
        {
            "id": "x_axis_main",
            "label": "Time in microseconds",
            "box": [54.19, 94.15, 9.81, 5.6],
            "color": "#0d9488",
            "description": "The window after the 355 nm pulse. Cage escape is read here, before bulk recombination",
        },
        {
            "id": "legend_box",
            "label": "13 mM and 0.3 mM",
            "box": [18.81, 4.31, 21.25, 13.58],
            "color": "#7c3aed",
            "description": "The two 4-tert-butylphenol concentrations in the main panel",
        },
        {
            "id": "blue_trace",
            "label": "0.3 mM trace",
            "box": [39.38, 13.82, 59.06, 15.77],
            "color": "#0284c7",
            "description": "Triplet quenching dominates: Phi_q,T = 0.65, Phi_q,S = 0.03. The trace ends higher than the 13 mM trace",
        },
        {
            "id": "red_trace",
            "label": "13 mM trace",
            "box": [19.5, 53.82, 22.88, 16.02],
            "color": "#dc2626",
            "description": "Phi_q,T = 0.30, Phi_q,S = 0.54. Total quenching is higher and the radical signal is lower",
        },
        {
            "id": "inset_y_axis",
            "label": "Phi_r,tot",
            "box": [41.5, 49.67, 4.06, 9.11],
            "color": "#9333ea",
            "description": "Measured free-radical quantum yield. Point values are drawn, not listed, in the main text",
        },
        {
            "id": "inset_x_axis",
            "label": "Quencher concentration",
            "box": [68.12, 81.71, 9.81, 5.12],
            "color": "#0d9488",
            "description": "The caption and text cover 0.1 mM to 200 mM for the wider series",
        },
        {
            "id": "inset_blue_pt",
            "label": "Low-concentration points",
            "box": [49.5, 35.53, 3.62, 4.8],
            "color": "#0284c7",
            "description": "The high end of the measured yield curve. The text does not print this point's y-value",
        },
        {
            "id": "inset_red_pt",
            "label": "The 13 mM point",
            "box": [54.75, 55.37, 3.62, 4.88],
            "color": "#dc2626",
            "description": "Sits below the low-concentration points. The text calls the yield markedly lower, without a printed number",
        },
        {
            "id": "inset_high_q_decay",
            "label": "Still falling at high concentration",
            "box": [58.69, 57.24, 35.88, 17.15],
            "color": "#d97706",
            "description": "The text says the quantum yield keeps dropping as the quencher concentration rises through this range",
        },
    ]
    fig2_annotator.tour_steps = [
        {
            "title": "1. What the axes are",
            "target_ids": ["y_axis_main", "x_axis_main", "legend_box"],
            "html": (
                "<p>After a 355 nm pulse (5.5 mJ) the plot records "
                '<a class="fig-ref" data-target="y_axis_main">ΔA at 450 nm</a> '
                "against "
                '<a class="fig-ref" data-target="x_axis_main">time in microseconds</a> '
                "for two "
                '<a class="fig-ref" data-target="legend_box">phenol concentrations</a>. '
                "Both solutions are 5 µM PC2+ in acetonitrile and are iso-absorbing. "
                "450 nm is the reduced catalyst, PC•+, not the excited state itself.</p>"
            ),
        },
        {
            "title": "2. More quencher, smaller radical signal",
            "target_ids": ["blue_trace", "red_trace"],
            "html": (
                "<p>The "
                '<a class="fig-ref" data-target="blue_trace">0.3 mM trace</a> '
                "is the one the text calls pronounced: Φq,T = 0.65 and Φq,S = 0.03. "
                "The "
                '<a class="fig-ref" data-target="red_trace">13 mM trace</a> '
                "has Φq,T = 0.30 and Φq,S = 0.54. "
                "Adding those pairs, total quenching efficiency is higher at 13 mM "
                "(0.84 versus 0.68; our addition of the reported yields) "
                "and the free-radical signal is lower. "
                "The paper does not print the plateau absorbances.</p>"
            ),
        },
        {
            "title": "3. The inset is the same comparison, wider",
            "target_ids": ["inset_y_axis", "inset_x_axis", "inset_blue_pt", "inset_red_pt"],
            "html": (
                "<p>The inset plots "
                '<a class="fig-ref" data-target="inset_y_axis">Φr,tot</a> '
                "against "
                '<a class="fig-ref" data-target="inset_x_axis">quencher concentration</a>. '
                "The "
                '<a class="fig-ref" data-target="inset_blue_pt">low-concentration points</a> '
                "sit above the "
                '<a class="fig-ref" data-target="inset_red_pt">13 mM point</a>. '
                "Read the direction off the figure. Do not treat a digit you estimate by eye as a number the paper reported.</p>"
            ),
        },
        {
            "title": "4. The decline continues past 13 mM",
            "target_ids": ["inset_high_q_decay"],
            "html": (
                "<p>Across the "
                '<a class="fig-ref" data-target="inset_high_q_decay">higher concentrations</a> '
                "the text says the free-radical quantum yield keeps falling, out to the 0.1–200 mM window. "
                "The authors place the onset of that decline, for this system, where singlet quenching "
                "starts to compete with intersystem crossing, above about 1 mM.</p>"
            ),
        },
    ]
    wigglystuff.FloatingPanel(
        mo.ui.tabs(
        {
            "Figure 1. States, cage, catalyst, quenchers": fig1_annotator,
            "Figure 2. 450 nm traces and the yield inset": fig2_annotator,
            "Figure 3. Spectra, the averaging window, and the actinometer": mo.vstack(
                [
                    mo.md(
                        "This is the measurement behind the yields in Fig. 2. "
                        "The radical concentration comes from ΔA at 450 nm, and the "
                        "number of excited states comes from the ruthenium actinometer."
                    ),
                    fig3_annotator,
                ]
            ),
            "Figure 4. Quenching only, then quenching times cage escape": mo.vstack(
                [
                    mo.md(
                        r"The curves are the paper's prediction for phenol with PC$^{2+}$. "
                        "This notebook does not recompute them. The rate constants are not in the main text."
                    ),
                    fig4_annotator,
                ]
            ),
            "Figure 5. The same idea under continuous light": mo.vstack(
                [
                    mo.md(
                        "The quencher is consumed as the reaction runs, so the system slides "
                        "along the Fig. 4 curve instead of sitting at one concentration."
                    ),
                    fig5_annotator,
                ]
            ),
            "Figure 6. Two more pairs, and the only flask result": mo.vstack(
                [
                    mo.md(
                        r"4CzIPN with DMA in toluene, and SO$_2$TDS$^{2-}$ with ascorbate in water. "
                        "The ratios 125 and 11.5 are stated in the text. Digits that appear only "
                        "inside the property boxes are left on the figure."
                    ),
                    fig6_annotator,
                ]
            ),
        },
        ),
        title="Figures 1–6",
        corner="bottom-right",
        width=880,
    )
    return


@app.cell(hide_code=True)
def figure_3(notebook_dir):
    fig3_annotator = FigureAnnotatorWidget()
    fig3_annotator.load_image_from_path(notebook_dir / "figures" / "fig3.webp")
    fig3_annotator.caption = (
        "Fig. 3. (A) Calibrated steady-state absorption spectrum of PC2+ in solution "
        "(brown trace), together with transient absorption spectra of PC2+-derived "
        "species in MeCN upon photoexcitation, showing the triplet 3*PC2+ (green trace) "
        "and the radical PC˙+ formed after electron transfer in the presence of a "
        "reductive quencher (blue trace). Excitation and detection wavelengths selected "
        "during the measurements are indicated. (B) Time-resolved absorption traces at "
        "450 nm under laser excitation intensities of 5–8 mJ per pulse, for a ~5 µM PC2+ "
        "solution with 0.22 mM 4-tbuPhOH, chosen to quench the triplet. The dashed lines "
        "mark the microsecond window used to average ΔA after cage escape. (C) Ground-state "
        "bleach at 455 nm of an iso-absorbing aqueous [Ru(bpy)3]Cl2 solution, recorded "
        "under the same conditions as the actinometric reference."
    )
    fig3_annotator.annotations = [
        {
            "id": "spectra",
            "label": "Panel A spectra",
            "box": [2.0, 7.51, 32.19, 86.08],
            "color": "#92400e",
            "description": "Steady-state PC2+ and the two transient spectra in acetonitrile",
        },
        {
            "id": "legend_a",
            "label": "PC2+, triplet, radical",
            "box": [20.2, 12.0, 10.2, 16.8],
            "color": "#0f766e",
            "description": "Brown ground state, green triplet, blue radical",
        },
        {
            "id": "detect_450",
            "label": "450 nm detection",
            "box": [16.62, 32.78, 9.31, 5.31],
            "color": "#0284c7",
            "description": "The detection wavelength the text uses for PC˙+",
        },
        {
            "id": "time_window",
            "label": "Averaging window",
            "box": [42.5, 18.86, 9.94, 18.13],
            "color": "#1d4ed8",
            "description": "Microsecond window after cage escape, before bulk recombination",
        },
        {
            "id": "traces_b",
            "label": "450 nm traces",
            "box": [33.75, 5.31, 33.44, 87.18],
            "color": "#2563eb",
            "description": "Three pulse energies, 5–8 mJ, at 0.22 mM phenol",
        },
        {
            "id": "actinometry",
            "label": "Ru actinometry",
            "box": [70.25, 14.84, 28.19, 66.12],
            "color": "#b45309",
            "description": "Iso-absorbing [Ru(bpy)3]2+ bleach at 455 nm",
        },
    ]
    fig3_annotator.tour_steps = [
        {
            "title": "1. Which spectrum is which",
            "target_ids": ["spectra", "legend_a", "detect_450"],
            "html": (
                "<p>Panel A is the set of spectra the quantitative analysis needs. "
                "The <a class='fig-ref' data-target='legend_a'>legend</a> "
                "marks ground-state PC<sup>2+</sup> in brown, the triplet "
                "<sup>3</sup>*PC<sup>2+</sup> in green, and the radical PC˙<sup>+</sup> "
                "in blue. The "
                "<a class='fig-ref' data-target='detect_450'>450 nm label</a> "
                "is the wavelength the text uses to quantify that radical. "
                "The extinction coefficient used to turn ΔA into a concentration "
                "is determined in SI Section S2.1; this caption does not print it.</p>"
            ),
        },
        {
            "title": "2. The window after cage escape",
            "target_ids": ["traces_b", "time_window"],
            "html": (
                "<p>Panel B is 450 nm, ~5 µM PC<sup>2+</sup>, and 0.22 mM phenol, "
                "low enough that the triplet is the state being quenched. "
                "Three pulse energies, 5–8 mJ, are overlaid. The "
                "<a class='fig-ref' data-target='time_window'>dashed marks</a> "
                "are the microsecond window used to average ΔA: after cage escape, "
                "and before bulk back-electron transfer on a hundreds-of-microseconds "
                "scale (Fig. S16). The signal is linear in laser power (Fig. S15), "
                "which the authors use to rule out two-photon chemistry.</p>"
            ),
        },
        {
            "title": "3. Counting the excited states",
            "target_ids": ["actinometry"],
            "html": (
                "<p>Panel C is the actinometer: an iso-absorbing aqueous solution of "
                "[Ru(bpy)<sub>3</sub>]<sup>2+</sup>, recorded under the same laser "
                "conditions, as a ground-state bleach at 455 nm. "
                "The text uses it to count how many excited states the pulse produced, "
                "so the radical signal can be turned into a quantum yield.</p>"
            ),
        },
    ]
    return (fig3_annotator,)


@app.cell(hide_code=True)
def figure_4(notebook_dir):
    fig4_annotator = FigureAnnotatorWidget()
    fig4_annotator.load_image_from_path(notebook_dir / "figures" / "fig4.webp")
    fig4_annotator.caption = (
        "Fig. 4. (left) Predicted radical-formation yields from quenching efficiency "
        "alone. Red and blue are the singlet and triplet contributions; black is their "
        "sum. (right) Free-radical formation quantum yield once cage-escape efficiencies "
        "are included. Red and blue are the singlet and triplet channels; black is the "
        "total. Yellow dots are measured free-radical quantum yields from 0.1 mM to 200 mM."
    )
    fig4_annotator.annotations = [
        {
            "id": "quench_only",
            "label": "Quenching only",
            "box": [1.75, 3.39, 47.47, 88.37],
            "color": "#334155",
            "description": "Left plot: radical yield if every quenching event counted",
        },
        {
            "id": "legend_left",
            "label": "Singlet, triplet, sum",
            "box": [7.75, 5.33, 10.44, 23.1],
            "color": "#be123c",
            "description": "Red singlet, blue triplet, black sum",
        },
        {
            "id": "with_escape",
            "label": "With cage escape",
            "box": [50.16, 3.39, 49.03, 88.37],
            "color": "#0f172a",
            "description": "Right plot: the same kinetics, times the cage-escape efficiencies",
        },
        {
            "id": "legend_right",
            "label": "Channels and data",
            "box": [54.72, 7.43, 21.33, 25.04],
            "color": "#a16207",
            "description": "Singlet channel, triplet channel, total, and the measured points",
        },
        {
            "id": "measured",
            "label": "Measured yields",
            "box": [67.48, 58.16, 24.33, 21.0],
            "color": "#ca8a04",
            "description": "Yellow points, the Fig. 2 inset replotted from 0.1 mM to 200 mM",
        },
    ]
    fig4_annotator.tour_steps = [
        {
            "title": "1. Quenching alone would say: use more",
            "target_ids": ["quench_only", "legend_left"],
            "html": (
                "<p>The left plot is quenching efficiency only. "
                "<a class='fig-ref' data-target='legend_left'>Red, blue, and black</a> "
                "are the singlet contribution, the triplet contribution, and their sum. "
                "The sum rises toward complete quenching. That model would tell you to "
                "raise the donor concentration. The text says this is the opposite of Fig. 2. "
                "The rate constants that draw the curves are not printed in the main text, "
                "so they are not restated here.</p>"
            ),
        },
        {
            "title": "2. Cage escape puts a maximum on the curve",
            "target_ids": ["with_escape", "legend_right", "measured"],
            "html": (
                "<p>The right plot multiplies those channels by the cage-escape efficiencies. "
                "The <a class='fig-ref' data-target='legend_right'>legend</a> "
                "keeps singlet, triplet, and total, and adds the measured yields. "
                "The <a class='fig-ref' data-target='measured'>yellow points</a> "
                "are the experimental free-radical quantum yields from 0.1 mM to 200 mM, "
                "the same comparison as the Fig. 2 inset. "
                "Below about 0.1 mM the text says the yield is limited by triplet quenching "
                "that has not finished. The decline sets in above about 1 mM, where singlet "
                "quenching starts to compete with intersystem crossing. "
                "Do not read an extra digit off the axis: the main text does not print one.</p>"
            ),
        },
    ]
    return (fig4_annotator,)


@app.cell(hide_code=True)
def figure_5(notebook_dir):
    fig5_annotator = FigureAnnotatorWidget()
    fig5_annotator.load_image_from_path(notebook_dir / "figures" / "fig5.webp")
    fig5_annotator.caption = (
        "Fig. 5. Predicted maximum photoreaction quantum yield, from the initial radical "
        "yield after quenching of the excited photocatalyst, against reaction progress, "
        "for three initial quencher concentrations. The x-axis is normalized to the course "
        "of the reaction so the three runs can be compared."
    )
    fig5_annotator.annotations = [
        {
            "id": "model_plot",
            "label": "Continuous-light model",
            "box": [7.62, 3.52, 88.69, 82.89],
            "color": "#334155",
            "description": "Quantum yield against conversion for three starting concentrations",
        },
        {
            "id": "q10",
            "label": "10 mM start",
            "box": [13.0, 7.5, 78.12, 16.48],
            "color": "#0284c7",
            "description": "Stoichiometric with the 10 mM substrate",
        },
        {
            "id": "q20",
            "label": "20 mM start",
            "box": [13.0, 32.81, 82.44, 15.55],
            "color": "#7c3aed",
            "description": "Twice the substrate concentration",
        },
        {
            "id": "q100",
            "label": "100 mM start",
            "box": [13.0, 62.97, 82.44, 2.27],
            "color": "#e11d48",
            "description": "Ten times the substrate concentration",
        },
        {
            "id": "legend5",
            "label": "Three starting concentrations",
            "box": [72.5, 39.8, 20.8, 17.4],
            "color": "#0f172a",
            "description": "10, 20, and 100 mM",
        },
        {
            "id": "progress",
            "label": "Reaction progress",
            "box": [28.31, 88.36, 52.0, 9.84],
            "color": "#475569",
            "description": "Substrate conversion, not clock time",
        },
    ]
    fig5_annotator.tour_steps = [
        {
            "title": "1. Conversion, not the clock",
            "target_ids": ["model_plot", "progress", "legend5"],
            "html": (
                "<p>The model uses the same conditions as the rest of the continuous-light "
                "section: 10 mM substrate, [PC<sup>2+</sup>] = 1 mM, "
                "ε = 1 × 10<sup>4</sup> M<sup>−1</sup> cm<sup>−1</sup> at 440 nm, "
                "and a photon flux of 1 × 10<sup>−3</sup> einstein s<sup>−1</sup>. "
                "The <a class='fig-ref' data-target='legend5'>three traces</a> "
                "start at 10 mM quencher (stoichiometric with the substrate), 20 mM, and 100 mM. "
                "The <a class='fig-ref' data-target='progress'>x-axis</a> "
                "is substrate conversion from 0 to 100%, because the time to 99% conversion "
                "is very different for the three runs. The y-axis is the predicted "
                "photoreaction quantum yield from the radical yield after quenching.</p>"
            ),
        },
        {
            "title": "2. The stoichiometric start climbs",
            "target_ids": ["q10"],
            "html": (
                "<p>The <a class='fig-ref' data-target='q10'>10 mM trace</a> "
                "starts between the singlet and triplet regimes. As the sacrificial donor "
                "is used up, the system moves into the triplet domain and the quantum yield rises. "
                "The main text describes that direction. It does not print the endpoint values "
                "on the axis.</p>"
            ),
        },
        {
            "title": "3. A large excess stays in the singlet regime",
            "target_ids": ["q20", "q100"],
            "html": (
                "<p>The <a class='fig-ref' data-target='q20'>20 mM</a> and "
                "<a class='fig-ref' data-target='q100'>100 mM</a> runs start where "
                "singlet quenching dominates, so the initial efficiency is low. "
                "The yield still rises as the donor is consumed, but less than in the "
                "10 mM case, because the donor concentration barely moves relative to "
                "where it started. A less efficient run also means more re-excitation "
                "before the substrate is consumed, which the authors connect to a higher "
                "chance of degradation.</p>"
            ),
        },
    ]
    return (fig5_annotator,)


@app.cell(hide_code=True)
def figure_6(notebook_dir):
    fig6_annotator = FigureAnnotatorWidget()
    fig6_annotator.load_image_from_path(notebook_dir / "figures" / "fig6.webp")
    fig6_annotator.caption = (
        "Fig. 6. (A) 4CzIPN and the reductive quencher DMA, with photophysical properties "
        "of 4CzIPN in toluene (Φisc from ref. 75) and the S1 and T1 quenching rate constants "
        "for DMA. (B) The non-TADF photocatalyst SO2TDS2− and HAsc−, with properties of "
        "SO2TDS2− in water (Φisc from ref. 74) and the quenching rate constants for HAsc−. "
        "(C) Relative radical yield against quencher concentration for the two systems, "
        "with a fit of eqn (2)–(4) used to extract the ratio of triplet to singlet "
        "cage-escape efficiencies."
    )
    fig6_annotator.annotations = [
        {
            "id": "cz_structure",
            "label": "4CzIPN",
            "box": [3.47, 1.83, 52.9, 18.64],
            "color": "#1d4ed8",
            "description": "The second TADF photocatalyst, used in toluene",
        },
        {
            "id": "dma",
            "label": "DMA",
            "box": [68.95, 1.89, 20.72, 9.99],
            "color": "#1d4ed8",
            "description": "The aromatic amine used as a reversible reductive quencher",
        },
        {
            "id": "cz_box",
            "label": "Toluene properties",
            "box": [51.41, 14.15, 47.1, 15.99],
            "color": "#1e3a8a",
            "description": "Lifetimes and Φisc printed on the figure; Φisc is cited to ref. 75",
        },
        {
            "id": "cz_rates",
            "label": "DMA quenching scheme",
            "box": [23.06, 25.9, 60.61, 7.31],
            "color": "#1d4ed8",
            "description": "The electron-transfer scheme and the two rate constants printed under it",
        },
        {
            "id": "so2",
            "label": "SO2TDS2−",
            "box": [15.28, 34.9, 73.2, 11.17],
            "color": "#b91c1c",
            "description": "A non-TADF organic photocatalyst, soluble in water",
        },
        {
            "id": "hasc",
            "label": "Ascorbate",
            "box": [2.19, 47.82, 44.91, 14.34],
            "color": "#b91c1c",
            "description": "HAsc−, the reductive quencher in water",
        },
        {
            "id": "so2_box",
            "label": "Water properties",
            "box": [47.45, 47.88, 51.06, 14.13],
            "color": "#7f1d1d",
            "description": "Lifetimes and Φisc printed on the figure; Φisc is cited to ref. 74",
        },
        {
            "id": "legend_c",
            "label": "Two systems",
            "box": [71.57, 70.98, 26.8, 5.56],
            "color": "#0f172a",
            "description": "Blue squares are 4CzIPN; red squares are SO2TDS2−",
        },
        {
            "id": "cz_curve",
            "label": "4CzIPN radical yield",
            "box": [15.91, 73.77, 34.72, 19.16],
            "color": "#1d4ed8",
            "description": "Relative radical yield falling as DMA concentration rises",
        },
        {
            "id": "so2_curve",
            "label": "SO2TDS radical yield",
            "box": [19.31, 73.94, 77.3, 12.73],
            "color": "#b91c1c",
            "description": "The same fall, smaller, for ascorbate",
        },
        {
            "id": "ratio_125",
            "label": "4CzIPN escape ratio",
            "box": [31.26, 86.7, 37.41, 5.72],
            "color": "#1d4ed8",
            "description": "ηce,T / ηce,S = 125, as the text states for 4CzIPN",
        },
        {
            "id": "ratio_115",
            "label": "SO2TDS escape ratio",
            "box": [24.61, 75.01, 30.83, 7.06],
            "color": "#b91c1c",
            "description": "ηce,T / ηce,S = 11.5, as the text states for SO2TDS2−",
        },
    ]
    fig6_annotator.tour_steps = [
        {
            "title": "1. 4CzIPN and DMA in toluene",
            "target_ids": ["cz_structure", "dma", "cz_box", "cz_rates"],
            "html": (
                "<p><a class='fig-ref' data-target='cz_structure'>4CzIPN</a> "
                "with <a class='fig-ref' data-target='dma'>DMA</a>, in toluene. "
                "The text says Φ<sub>isc</sub> is much higher there than in acetonitrile, "
                "which should make the concentration effect larger. DMA was chosen to avoid "
                "side reactions known for aliphatic amines. The "
                "<a class='fig-ref' data-target='cz_box'>property box</a> "
                "and the <a class='fig-ref' data-target='cz_rates'>rate constants</a> "
                "are printed on the figure. The main text does not reprint those digits, "
                "and this tour does not read them off the image.</p>"
            ),
        },
        {
            "title": "2. A non-TADF catalyst in water",
            "target_ids": ["so2", "hasc", "so2_box"],
            "html": (
                "<p><a class='fig-ref' data-target='so2'>SO<sub>2</sub>TDS<sup>2−</sup></a> "
                "with <a class='fig-ref' data-target='hasc'>ascorbate</a>. "
                "This pair is the non-TADF example, in water. The "
                "<a class='fig-ref' data-target='so2_box'>property box</a> "
                "again prints lifetimes, Φ<sub>isc</sub> (ref. 74), and quenching rate "
                "constants that the main text does not restate as numbers.</p>"
            ),
        },
        {
            "title": "3. Less is more in both systems",
            "target_ids": ["legend_c", "cz_curve", "so2_curve", "ratio_125", "ratio_115"],
            "html": (
                "<p>Panel C is relative radical yield against quencher concentration. "
                "<a class='fig-ref' data-target='legend_c'>Blue is 4CzIPN, red is "
                "SO<sub>2</sub>TDS<sup>2−</sup></a>. Both fall as the quencher gets more "
                "concentrated. The fit of eqn (2)–(4) gives "
                "η<sub>ce,T</sub>/η<sub>ce,S</sub> = "
                "<a class='fig-ref' data-target='ratio_125'>125</a> for 4CzIPN and "
                "<a class='fig-ref' data-target='ratio_115'>11.5</a> for SO<sub>2</sub>TDS<sup>2−</sup>. "
                "The 4CzIPN signal drops almost to zero at high DMA. The text says that "
                "would cut the reaction quantum yield by about tenfold from 10 mM to 200 mM DMA. "
                "The one preparative check is the pinacol coupling of acetophenone (15.7 mM) "
                "with this water system: about 50% higher performance at 19.2 mM ascorbate "
                "than at 96.9 mM, in the same direction as the red trace.</p>"
            ),
        },
    ]
    return (fig6_annotator,)




@app.cell(hide_code=True)
def escape_ladder(reader_level):
    mo.md(
        r"""
        ## Ladder: why the triplet frees more radicals

        **Mechanism spine.** The free-radical quantum yield is the sum of a singlet channel and a triplet channel. Cage escape is much more likely for a pair born from the triplet, because recombination back to the ground state is spin-forbidden for that pair and spin-allowed for the singlet pair. A quencher concentration that intercepts the singlet before intersystem crossing therefore lowers the free-radical yield.

        **Analogy, carried through Undergrad.** A short corridor with a door that slams, and a long corridor with a door that sticks open. The slam is singlet recombination. The sticking door is triplet escape. Crowding the entrance is a high quencher concentration, which shoves people into the slamming corridor before they can reach the long one.

        | In the analogy | In the mechanism |
        |---|---|
        | The person who just stepped in | The excited catalyst, and then the geminate radical pair it forms with Q |
        | Slamming door | Spin-allowed recombination of the singlet pair (CR on the left of Fig. 1A) |
        | Door that sticks open | Spin-forbidden recombination, so the triplet pair escapes more often |
        | Crowding the entrance | High [Q], which quenches $S_1$ before isc |
        | People who get outside | Free radicals (PC•+ and Q•+) |

        The limit is in the Undergrad tab: molecules are not choosing a door, and both channels run at once.
        """
    )
    escape_tabs = mo.ui.tabs(
        {
            "Child": mo.md(
                """
                Light excites a catalyst, and a partner can take an electron from it.
                The two new pieces start stuck together.
                Pieces made on the short-lived path usually stick back together.
                Pieces made on the long-lived path more often split, so less partner can free more of them.
                """
            ),
            "Teen": mo.md(
                r"""
                The short-lived state is the **singlet**. The long-lived state is the **triplet**.
                Quenching means the partner turns that state off by taking or giving an electron.
                At 0.3 mM 4-*tert*-butylphenol, triplet quenching is 0.65 and singlet quenching is 0.03.
                At 13 mM those numbers are 0.30 and 0.54, and the 450 nm radical signal is the smaller one (Fig. 2).

                Toy line, phenol in acetonitrile, central values: about 42% of triplet-born pairs escape the cage, and about 2.8% of singlet-born pairs do.
                """
            ),
            "Undergrad": mo.md(
                r"""
                Equation (2), printed in the text, splits the free-radical quantum yield:

                $$\Phi_{\mathrm{r,tot}} = \Phi_{\mathrm{r,S}} + \Phi_{\mathrm{r,T}}$$

                $\Phi_{\mathrm{r,S}}$ and $\Phi_{\mathrm{r,T}}$ are the contributions from pairs born from $S_1$ and from $T_1$. Equation (1) is an image in the paper. Its prose defines $\Phi_{\mathrm{r,tot}}$ as the concentration of free radical divided by the number of excited states formed when a photon is absorbed. The numerator can be either reduced catalyst or oxidized quencher, because the stoichiometry is 1:1.

                The authors then report cage-escape efficiencies, the fraction of those geminate pairs that separate. For PC$^{2+}$ with 4-*tert*-butylphenol in acetonitrile, $\eta_{\mathrm{ce,T}} = 0.42 \pm 0.02$ and $\eta_{\mathrm{ce,S}} = 0.028 \pm 0.005$ (text immediately after Table 1). Equations (3) and (4), which convert the measured radical yields into those efficiencies, are also images. They are not retyped here. The ratio of the central values is $0.42 / 0.028 = 15$, which is the "more than one order of magnitude" in that paragraph.

                Fig. 1B, acetonitrile: $\tau_{0,\mathrm{S}} = 17$ ns, $\tau_{0,\mathrm{T}} = 44$ µs, $\Phi_{\mathrm{isc}} = 0.68$ with no quencher, excited-state reduction potentials $+2.0$ V ($S_1$) and $+1.8$ V ($T_1$) vs SCE. Naphthalene sits at $+1.61$ V and the phenol at $+1.65$ V, so both excited states are strong enough oxidants. The singlet is the stronger of the two. The triplet wins on cage escape, not on driving force.

                **Where the door story breaks.** Nobody chooses a corridor. The branching ratio is kinetic: $k_{\mathrm{q,S}}[\mathrm{Q}]$ competes with $k_{\mathrm{isc}}$, and cage escape competes with recombination. Both channels are open in the same solution. "Short-lived" was a stand-in for 17 ns versus 44 µs, and "usually / more often" was a stand-in for 2.8% versus 42% in this one phenol series, not a universal fraction.
                """
            ),
            "Grad student": mo.md(
                r"""
                Experiment 1a (Table 1) holds the phenol at 0.22 mM so that $\eta_{\mathrm{q,S}} = 0.02$. Essentially every radical detected there is assigned to the triplet. $\eta_{\mathrm{isc}} = 0.66$, close to 0.68 with no quencher, and $\Phi_{\mathrm{q,T}} = 0.65$. Actinometry against $[\mathrm{Ru(bpy)_3}]^{2+}$ (Fig. 3C) supplies the number of excited states. The time window is a few microseconds: after cage escape, before bulk recombination on a hundreds-of-microseconds scale (Fig. S16). Three pulse energies, 5–8 mJ, stay linear (Fig. S15), which they use to rule out two-photon chemistry.

                Experiment 1b cannot do the mirror image. At 132 mM, solubility stops them, $\eta_{\mathrm{q,S}} = 0.94$, and a residual $\eta_{\mathrm{isc}} = 0.05$ remains. Because the triplet channel is so much more productive, they subtract its contribution with equation (2) before reporting $\eta_{\mathrm{ce,S}}$. Ignoring that residual would credit triplet radicals to the singlet and inflate $\eta_{\mathrm{ce,S}}$.

                **What we simplified earlier.** "Less partner frees more pieces" is not true at arbitrarily low concentration. The Fig. 4 discussion says that below about 0.1 mM the phenol yield is limited by incomplete triplet quenching. The maximum is the tradeoff where triplet quenching is nearly complete and singlet quenching is not yet stealing the population. They put that downturn above about 1 mM for this system. They also say a maximum of this kind needs a high enough isc yield: on the order of 10%, given the tenfold cage-escape gap they measured. Below that, there is not enough triplet for the more productive channel to matter.

                Relative to Tamaki, Kamogawa, Inoue, Ceroni, and Ishitani (*J. Am. Chem. Soc.* **2025**, DOI [10.1021/jacs.5c10614](https://doi.org/10.1021/jacs.5c10614), Crossref; this paper's ref. 36), the advance they claim is a direct transient-absorption measurement of the radicals, a time window that separates geminate escape from bulk recombination, and a TADF scheme that includes reverse intersystem crossing. The earlier work inferred cage escape by fitting final yields.

                The non-TADF approximation (equations 2 and 3, ignoring $S_1$–$T_1$ cycling) gives the same $\eta_{\mathrm{ce}}$ as the exact recursion in SI Section 2.8, for the systems they checked. They read that as evidence that the important quenching happens on the first visit to each state, at the high concentrations used in synthesis.
                """
            ),
            "Expert": mo.md(
                r"""
                What is new is a spectroscopic $\eta_{\mathrm{ce,S}}$ and $\eta_{\mathrm{ce,T}}$ on one TADF catalyst, plus the same direction of effect for three further pairs: naphthalene with PC$^{2+}$ ($\eta_{\mathrm{ce,T}} = 0.46 \pm 0.03$ at 0.12 mM, $\eta_{\mathrm{ce,S}} = 0.07 \pm 0.01$ at 120 mM), 4CzIPN with DMA in toluene (ratio of cage-escape efficiencies 125), and non-TADF SO$_2$TDS$^{2-}$ with ascorbate in water (ratio 11.5). Solvents are acetonitrile, toluene, and water. The 4CzIPN curve is predicted to drop by about an order of magnitude in reaction quantum yield from 10 mM to 200 mM DMA, and the relative radical signal "drops almost to zero" at high DMA (Fig. 6C discussion).

                The preparative test is narrower than that sentence. One pinacol coupling of acetophenone (15.7 mM) with SO$_2$TDS$^{2-}$ and HAsc$^-$, 390 nm LEDs, is about 50% higher in performance at 19.2 mM ascorbate than at 96.9 mM (Section S3.2). The continuous-irradiation model (their earlier Python framework: Bellatreccia, Fina, and Ceroni, *Photochem. Photobiol. Sci.* **2026**, DOI [10.1007/s43630-026-00901-4](https://doi.org/10.1007/s43630-026-00901-4), Crossref; this paper's ref. 68) uses [substrate] = 10 mM, [PC$^{2+}$] = 1 mM, $\varepsilon = 1 \times 10^{4}\,\mathrm{M^{-1}\,cm^{-1}}$ at 440 nm, and a photon flux of $1 \times 10^{-3}$ einstein s$^{-1}$. It puts the highest quantum yield near 1 mM and still requires a stoichiometric 10 mM of quencher for full conversion (Fig. 5 compares 10, 20, and 100 mM).

                Open, and not settled in the main text: the substrate-as-quencher case is a simulation in SI Section 2.9, not a measured scope. Rate constants behind Fig. 4 ($k_{\mathrm{q,S}}$, $k_{\mathrm{q,T}}$, $k_{\mathrm{isc}}$) are not printed in the main text, so those curves are not recomputed here. The printed Fig. 4 is annotated above, from the paper's image. Spin retention at the moment of electron transfer is taken from the literature they cite, not re-proved here.
                """
            ),
        },
        value=reader_level.value,
    )
    escape_tabs
    return (escape_tabs,)


@app.cell(hide_code=True)
def escape_ask():
    escape_checks = mo.ui.dictionary(
        {
            "Child": mo.ui.radio(
                options=[
                    "Less partner can free more pieces, because more catalysts stay on the long-lived path, and that path splits apart more often",
                    "Less partner frees more pieces because the catalyst absorbs more light when the flask is dilute",
                    "More partner always frees more pieces, because more collisions make more electron transfers",
                ],
                label="Which picture matches the story above?",
            ),
            "Teen": mo.ui.radio(
                options=[
                    "Fewer free radicals from that event",
                    "More free radicals from that event",
                    "The same number, because both paths transfer one electron",
                ],
                label="A quenching event moves from the triplet (about 42% escape) to the singlet (about 2.8% escape). Free radicals from that event…",
            ),
            "Undergrad": mo.ui.text(
                placeholder="e.g. 10",
                label="Phenol, central values: η_ce,T = 0.42 and η_ce,S = 0.028. How many times larger is the triplet efficiency? Ignore the ± ranges.",
            ),
            "Grad student": mo.ui.radio(
                options=[
                    "η_ce,S would come out too high, because productive triplet radicals would be counted as singlet radicals",
                    "η_ce,S would come out too low, because the residual triplet is less productive than the singlet",
                    "Nothing would change, because equation (2) does not involve the triplet",
                ],
                label="In experiment 1b a residual η_isc of 0.05 remains. If that triplet contribution were not subtracted, what would happen to the reported singlet cage-escape efficiency?",
            ),
            "Expert": mo.ui.text_area(
                rows=4,
                label="What measurement, missing from the main text, would test the claim when the substrate itself is the quencher rather than a sacrificial donor?",
            ),
        }
    )
    escape_answers = {
        "Child": {
            "correct": "Less partner can free more pieces, because more catalysts stay on the long-lived path, and that path splits apart more often",
            "why": "That is the mechanism in the Child tab. Dilute solutions do not absorb more light in the Fig. 2 comparison: the two traces are iso-absorbing. More collisions quench more excited states, which is the idea the paper says fails.",
        },
        "Teen": {
            "correct": "Fewer free radicals from that event",
            "why": "About 2.8% of singlet-born pairs escape, against about 42% of triplet-born pairs (phenol, acetonitrile, central values in the text after Table 1). One electron is transferred either way; most singlet pairs then recombine inside the cage.",
        },
        "Undergrad": {
            "correct": 15.0,
            "tolerance": 0.5,
            "why": r"$0.42 / 0.028 = 15$. The paper's phrase for this phenol pair is “more than one order of magnitude.” The $\pm 0.02$ and $\pm 0.005$ are real, and this check uses only the centers.",
        },
        "Grad student": {
            "correct": "η_ce,S would come out too high, because productive triplet radicals would be counted as singlet radicals",
            "why": "Series 1b still has η_isc = 0.05 at 132 mM (Table 1). The authors subtract that triplet share with equation (2) before applying equation (3). The triplet channel is the productive one, so leaving it in the singlet bucket inflates η_ce,S.",
        },
        "Expert": {
            "correct": None,
            "why": "Run the same reaction at two dilutions where the substrate, not a sacrificial donor, is what quenches the catalyst, and compare quantum yields. The main text only simulates that case (SI Section 2.9, mechanistic model b). The lab-scale reaction that is reported uses HAsc− as the quencher and acetophenone as the substrate (Section S3.2), which is the other way around.",
        },
    }
    return escape_answers, escape_checks


@app.cell(hide_code=True)
def escape_feedback(escape_answers, escape_checks, escape_tabs):
    show_check(escape_tabs, escape_checks, escape_answers)
    return


@app.cell(hide_code=True)
def quench_ladder(reader_level):
    mo.md(
        r"""
        ## Ladder: a dark glow is not a free radical

        **Mechanism spine.** Stern–Volmer quenching counts how often the excited state is intercepted. It does not count how often the geminate pair escapes the cage. A higher quenching efficiency can sit next to a lower free-radical quantum yield, which is what Fig. 2 shows between 0.3 mM and 13 mM 4-*tert*-butylphenol.

        This is the same phenol experiment as the ladder above, read off the other axis: the scoreboard, not the spin.
        """
    )
    quench_tabs = mo.ui.tabs(
        {
            "Child": mo.md(
                """
                A glow that goes out only says the excited catalyst met a partner.
                It does not say the new pieces got free.
                A flask can quench more glow and still make fewer free pieces.
                """
            ),
            "Teen": mo.md(
                r"""
                **Quenching efficiency** here means the fraction of excited states that meet the partner.
                Add the paper's two phenol yields. At 0.3 mM, $0.65 + 0.03 = 0.68$. At 13 mM, $0.30 + 0.54 = 0.84$.
                More of the excited states are turned off at 13 mM.
                Fig. 2 still shows the smaller 450 nm radical signal there.

                Toy line: 0.84 is more quenching than 0.68, and it produces fewer free radicals.
                """
            ),
            "Undergrad": mo.md(
                r"""
                Table 1 writes the link between the triplet quenching yield and the two efficiencies that build it:

                $$\Phi_{\mathrm{q,T}} = \eta_{\mathrm{isc}} \times \eta_{\mathrm{q,T}}$$

                In series 1a, $\Phi_{\mathrm{q,T}} = 0.65$ and $\eta_{\mathrm{isc}} = 0.66$, so $\eta_{\mathrm{q,T}} = 0.65 / 0.66 \approx 0.985$. The triplet that gets made is almost completely quenched. The singlet quenching efficiency on that row is only $\eta_{\mathrm{q,S}} = 0.02$.

                Series 1b flips the bookkeeping: $\eta_{\mathrm{q,S}} = 0.94$, $\eta_{\mathrm{isc}} = 0.05$, $\Phi_{\mathrm{q,T}} = 0.05$. Nearly every singlet is quenched, almost no triplet is formed, and the triplet quenching yield collapses because there is nothing left to quench.

                A Stern–Volmer plot of emission reports this interception. $\Phi_{\mathrm{r,tot}}$ divides escaped radicals by excited states formed (the prose of eqn 1). The two quotients share a photon and almost nothing else. The Fig. 4 discussion says a model that stops at quenching efficiency rises monotonically toward complete quenching, which is the opposite of the measured radical yields (the yellow points, inset of Fig. 2).
                """
            ),
            "Grad student": mo.md(
                r"""
                The quenching-only curve in Fig. 4 (left) is what you would plot if every quenching event freed a radical. The right-hand curve multiplies by the cage-escape efficiencies and produces a maximum. The paper does not print $k_{\mathrm{q,S}}$, $k_{\mathrm{q,T}}$, or $k_{\mathrm{isc}}$ in the main text, so the curves cannot be rebuilt from the article body alone. The qualitative shape is constrained: below about 0.1 mM, triplet quenching is incomplete; above about 1 mM, singlet quenching competes with isc; at still higher concentration the yield flattens at the low singlet cage-escape efficiency.

                Under continuous irradiation the quencher is consumed, so a flask does not sit on one x-position of Fig. 4. It slides left as the donor is used up (Fig. 5). Starting at 10 mM, stoichiometric with their 10 mM substrate, the model moves toward the triplet-rich region and the quantum yield rises as the reaction proceeds. Starting at 20 mM or 100 mM, the flask spends the conversion in the singlet-dominated region. The x-axis of Fig. 5 is substrate conversion, not clock time, because the times required to reach 99% conversion differ.

                **What we simplified.** The Teen sum $0.65+0.03$ treats the two reported quantum yields as an exhaustive split of "fraction quenched." That is the comparison the text makes when it says total quenching efficiency is higher at 13 mM. It is not a claim that the yields of unquenched $S_1$ emission, isc, and non-radiative decay were remeasured in that sentence.
                """
            ),
            "Expert": mo.md(
                r"""
                The operational recommendation is not "never measure a Stern–Volmer plot." The $\Phi_{\mathrm{q}}$ values in the paper come from those experiments (SI Section S2.3). The recommendation is to stop treating a high quenching efficiency as evidence that the radical yield will be high. For 4CzIPN / DMA the spectroscopic curve implies about a tenfold drop in reaction quantum yield between 10 mM and 200 mM. For the phenol model, the quantum-yield maximum near 1 mM is not a preparative recipe: full conversion of 10 mM substrate still wants a stoichiometric donor.

                Kamogawa, Okumura, Ishitani, and coworkers (*Chem. Sci.* **2026**, DOI [10.1039/d5sc08659k](https://doi.org/10.1039/d5sc08659k), Crossref; this paper's ref. 78) are cited for the same direction of effect in non-TADF catalysts. This notebook does not re-derive that paper. The limit to remember from Fina et al. is the isc threshold: with a tenfold cage-escape gap, they estimate $\Phi_{\mathrm{isc}}$ on the order of 10% before a maximum versus concentration is worth expecting.
                """
            ),
        },
        value=reader_level.value,
    )
    quench_tabs
    return (quench_tabs,)


@app.cell(hide_code=True)
def quench_ask():
    quench_checks = mo.ui.dictionary(
        {
            "Child": mo.ui.radio(
                options=[
                    "The glow going out means the excited catalyst met a partner, not that the new pieces got free",
                    "The glow going out means a free radical was released",
                    "A brighter glow means more free radicals, so quenching should be avoided entirely",
                ],
                label="What does a glow that goes out tell you, in this story?",
            ),
            "Teen": mo.ui.radio(
                options=[
                    "13 mM quenches more of the excited states (0.84 versus 0.68) and frees fewer radicals",
                    "13 mM quenches less and frees fewer radicals",
                    "0.3 mM quenches more of the excited states, which is why its radical signal is larger",
                ],
                label="Using only the addition in the Teen tab, which statement matches Fig. 2?",
            ),
            "Undergrad": mo.ui.text(
                placeholder="e.g. 0.90",
                label="Table 1, series 1a: Φ_q,T = 0.65 and η_isc = 0.66. The table sets Φ_q,T = η_isc × η_q,T. What is η_q,T?",
            ),
            "Grad student": mo.ui.radio(
                options=[
                    "It slides toward lower quencher concentration, into the more productive triplet region, so the quantum yield rises during the reaction",
                    "It stays at 10 mM, because the model holds every concentration fixed",
                    "It slides toward higher quencher concentration as product accumulates",
                ],
                label="In the continuous-irradiation model, a run that starts at 10 mM quencher (stoichiometric with 10 mM substrate) does what as the donor is consumed?",
            ),
            "Expert": mo.ui.text_area(
                rows=3,
                label="Why is a Stern–Volmer plot still worth measuring, if it is an unreliable proxy for the radical yield?",
            ),
        }
    )
    quench_answers = {
        "Child": {
            "correct": "The glow going out means the excited catalyst met a partner, not that the new pieces got free",
            "why": "Quenching is the meeting. Cage escape is the split. The paper's point is that those are different events (introduction, and Fig. 2).",
        },
        "Teen": {
            "correct": "13 mM quenches more of the excited states (0.84 versus 0.68) and frees fewer radicals",
            "why": "0.30 + 0.54 = 0.84 and 0.65 + 0.03 = 0.68, from the Φq values in the Fig. 2 discussion. The text says the free-radical quantum yield is markedly lower at 13 mM.",
        },
        "Undergrad": {
            "correct": 0.985,
            "tolerance": 0.02,
            "why": r"$0.65 / 0.66 \approx 0.985$. Table 1 defines $\Phi_{\mathrm{q,T}} = \eta_{\mathrm{isc}} \times \eta_{\mathrm{q,T}}$. Series 1a is 0.22 mM 4-*tert*-butylphenol, not the 0.3 mM trace in Fig. 2.",
        },
        "Grad student": {
            "correct": "It slides toward lower quencher concentration, into the more productive triplet region, so the quantum yield rises during the reaction",
            "why": "Fig. 5 discussion, optimal case (10 mM). The quencher is the sacrificial donor, so its concentration falls as the reaction proceeds. The 20 mM and 100 mM starts remain in the singlet-dominated region for much more of the conversion.",
        },
        "Expert": {
            "correct": None,
            "why": "The plot is how the authors obtained Φq,S and Φq,T (SI Section S2.3). Those yields are inputs to the cage-escape analysis. The mistake they argue against is reading a high quenching efficiency as if it were already a radical yield (Conclusions).",
        },
    }
    return quench_answers, quench_checks


@app.cell(hide_code=True)
def quench_feedback(quench_answers, quench_checks, quench_tabs):
    show_check(quench_tabs, quench_checks, quench_answers)
    return


@app.function(hide_code=True)
def method_view_name(level: str) -> str:
    """Return the method-diagram view that matches one explanation level.

    Child and Teen share the group-level Overview. Undergrad gets every
    stage. Grad student and Expert get Spec, with short parameters on
    the boxes and full parameters in the side panel.

    :param level: A name from the notebook's ``reader_level`` picker.
    :returns: ``overview``, ``detail``, or ``spec``.
    """
    if level in ("Child", "Teen"):
        return "overview"
    if level == "Undergrad":
        return "detail"
    return "spec"


@app.function(hide_code=True)
def method_groups(graph: dict) -> list[str]:
    """Return group titles in first-seen order.

    :param graph: The method graph with a ``stages`` list.
    :returns: Unique ``group`` strings, in first-seen order.
    """
    titles: list[str] = []
    for stage in graph["stages"]:
        if stage["group"] not in titles:
            titles.append(stage["group"])
    return titles


@app.function(hide_code=True)
def mermaid_from_graph(graph: dict, view: str) -> str:
    """Draw one Mermaid flowchart from the method graph.

    Overview is one box per group. Detail and Spec draw every stage,
    boxed by group. Spec inlines short ``params`` and edge ``data``.
    Inferred stages and edges are dashed. Labels are passed without
    ``<br>`` so Mermaid can wrap them.

    :param graph: Stages, edges, and optional ``named`` structures.
    :param view: ``overview``, ``detail``, or ``spec``.
    :returns: Mermaid source for ``MermaidView``.
    """

    def shorten(text: str, limit: int = 40) -> str:
        if len(text) <= limit:
            return text
        return text[: limit - 1] + "⋯"

    def safe(text: str) -> str:
        return (
            text.replace('"', "'").replace("[", "(").replace("]", ")")
        )

    groups = method_groups(graph)
    group_id = {title: f"g{index}" for index, title in enumerate(groups)}
    by_id = {stage["id"]: stage for stage in graph["stages"]}
    lines = ["flowchart TD"]
    if view == "overview":
        for title in groups:
            lines.append(f'  {group_id[title]}["{safe(title)}"]')
        pair_label: dict[tuple[str, str], str | None] = {}
        pair_inferred: dict[tuple[str, str], bool] = {}
        for edge in graph["edges"]:
            source = by_id[edge["from"]]
            target = by_id[edge["to"]]
            left = group_id[source["group"]]
            right = group_id[target["group"]]
            if left == right:
                continue
            pair_inferred[left, right] = pair_inferred.get(
                (left, right), True
            ) and bool(edge.get("inferred"))
            if edge.get("kind") and edge.get("label"):
                pair_label[left, right] = edge["label"]
            else:
                pair_label.setdefault((left, right), None)
        for (left, right), label in pair_label.items():
            arrow = "-.->" if pair_inferred.get((left, right)) else "-->"
            if label:
                lines.append(f'  {left} {arrow}|"{safe(label)}"| {right}')
            else:
                lines.append(f"  {left} {arrow} {right}")
        return "\n".join(lines)

    dashed_ids: list[str] = []
    for title in groups:
        lines.append(f'  subgraph {group_id[title]}["{safe(title)}"]')
        for stage in graph["stages"]:
            if stage["group"] != title:
                continue
            label = stage["label"]
            if view == "spec" and stage.get("params"):
                extras = ", ".join(shorten(item) for item in stage["params"])
                label = f"{label}. {shorten(extras)}"
            lines.append(f'    {stage["id"]}["{safe(label)}"]')
            if stage.get("inferred"):
                dashed_ids.append(stage["id"])
        lines.append("  end")
    for edge in graph["edges"]:
        arrow = "-.->" if edge.get("inferred") else "-->"
        bits: list[str] = []
        if edge.get("kind") and edge.get("label"):
            bits.append(edge["label"])
        if view == "spec" and edge.get("data"):
            bits.append(shorten(edge["data"]))
        if bits:
            lines.append(
                f'  {edge["from"]} {arrow}|"{safe(shorten(" · ".join(bits)))}"| {edge["to"]}'
            )
        else:
            lines.append(f'  {edge["from"]} {arrow} {edge["to"]}')
    if dashed_ids:
        lines.append("  classDef inferred stroke-dasharray: 5 5")
        for node_id in dashed_ids:
            lines.append(f"  class {node_id} inferred")
    return "\n".join(lines)


@app.function(hide_code=True)
def method_steps(graph: dict, view: str) -> list[dict]:
    """Build ``MermaidView`` steps, one per stage.

    Overview highlights the stage's group. Detail and Spec highlight the
    stage and the arrows into it. Spec adds full ``params`` and incoming
    ``data`` to the side panel.

    :param graph: The same graph ``mermaid_from_graph`` draws.
    :param view: ``overview``, ``detail``, or ``spec``.
    :returns: Step dicts for ``MermaidView.steps``.
    """
    groups = method_groups(graph)
    group_id = {title: f"g{index}" for index, title in enumerate(groups)}
    by_id = {stage["id"]: stage for stage in graph["stages"]}
    steps: list[dict] = []
    for stage in graph["stages"]:
        incoming = [
            [edge["from"], edge["to"]]
            for edge in graph["edges"]
            if edge["to"] == stage["id"]
        ]
        if view == "overview":
            node = group_id[stage["group"]]
            incoming = [
                [group_id[by_id[start]["group"]], group_id[by_id[end]["group"]]]
                for start, end in incoming
                if by_id[start]["group"] != by_id[end]["group"]
            ]
        else:
            node = stage["id"]
        step = {
            "node": node,
            "title": stage["label"],
            "what": stage["what"],
            "incoming": incoming,
        }
        if stage.get("ref"):
            step["ref"] = stage["ref"]
        elif stage.get("inferred"):
            step["ref"] = "inferred"
            step["note"] = str(stage["inferred"])
        if view == "spec":
            if stage.get("params"):
                step["params"] = "; ".join(stage["params"])
            receives = [
                edge["data"]
                for edge in graph["edges"]
                if edge["to"] == stage["id"] and edge.get("data")
            ]
            if receives:
                step["receives"] = receives
        steps.append(step)
    return steps


@app.function(hide_code=True)
def check_method_graph(graph: dict) -> list[str]:
    """Return problems in the method graph, or an empty list if it is ready.

    The rules are those in ``resources/method_diagrams.md`` §3: every
    stage and edge has a ``ref`` or is ``inferred``; every ``kind`` edge
    has a label; every stage has an incoming edge unless it is first in
    its group or marked ``input``; several splits into one stage need
    ``pools``; a branch, split, or parallel inside one group is named;
    Spec inlines stay short; group titles and stage labels stay short.

    :param graph: The method graph.
    :returns: Human-readable problems, empty when the check is clean.
    """
    problems: list[str] = []
    stages = graph["stages"]
    edges = graph["edges"]
    by_id = {stage["id"]: stage for stage in stages}
    first_in_group: dict[str, str] = {}
    for stage in stages:
        first_in_group.setdefault(stage["group"], stage["id"])
        if not stage.get("ref") and not stage.get("inferred"):
            problems.append(f"{stage['id']} has neither ref nor inferred")
        if len(stage["label"]) > 40:
            problems.append(f"{stage['id']} label is longer than 40 characters")
        if len(stage["group"]) > 50:
            problems.append(f"{stage['id']} group title is longer than 50 characters")
        incoming = [edge for edge in edges if edge["to"] == stage["id"]]
        if (
            not incoming
            and stage["id"] != first_in_group[stage["group"]]
            and not stage.get("input")
        ):
            problems.append(f"{stage['id']} has no incoming edge")
        split_in = [edge for edge in incoming if edge.get("kind") == "split"]
        if len(split_in) > 1 and not stage.get("pools"):
            problems.append(f"{stage['id']} receives several splits without pools")
    named = graph.get("named") or []
    for edge in edges:
        label = f"{edge['from']}->{edge['to']}"
        if not edge.get("ref") and not edge.get("inferred"):
            problems.append(f"edge {label} has neither ref nor inferred")
        if edge.get("kind") and not edge.get("label"):
            problems.append(f"edge {label} has a kind but no label")
        if edge.get("kind") in {"branch", "split", "parallel"}:
            source = by_id[edge["from"]]
            target = by_id[edge["to"]]
            if source["group"] == target["group"] and not named:
                problems.append(
                    f"edge {label} is a {edge['kind']} inside "
                    f"{source['group']!r} but the graph has no named structure"
                )
        if edge.get("data") and len(edge["data"]) > 40:
            # Spec inlines shorten these; the full text belongs in the panel.
            pass
    return problems


@app.cell(hide_code=True)
def method_graph():
    method_graph = {
        "named": [
            "low versus high quencher concentration",
            "mechanistic models a and b",
        ],
        "stages": [
            {
                "id": "synth_pc",
                "label": "Synthesize PC2+",
                "group": "Make the catalyst",
                "ref": "SI S5; SI S1 (Dortmund); Author contributions",
                "what": (
                    "Chris Burdenski synthesized PC2+ at TU Dortmund under "
                    "Max Hansmann. Solvents were dried on an MBraun SPS and "
                    "degassed with argon; solids were handled in a nitrogen "
                    "glovebox. The main text uses this dicationic "
                    "pi-extended heterocycle/carbene hybrid as the TADF "
                    "photocatalyst in Fig. 1B."
                ),
                "params": [
                    "SPS solvents over molecular sieves, argon-degassed",
                    "N2 glovebox for solids and NMR samples",
                ],
            },
            {
                "id": "tas_setup",
                "label": "Record ns TAS at 355 nm",
                "group": "Set up photophysics",
                "ref": "SI S1 (Mainz photophysical studies)",
                "what": (
                    "Transient absorption used an Edinburgh LP980KS with a "
                    "frequency-tripled Nd:YAG (Quantel Q-smart 450) at 355 nm, "
                    "about 5 ns, 10 Hz. Spectra were an Andor iCCD integrated "
                    "over 100 ns; single-wavelength traces a Hamamatsu R928 "
                    "PMT. The cell holder was at 20 C. Pulse energy was read "
                    "with a gentec-eo pyroelectric detector."
                ),
                "params": [
                    "355 nm, about 5 ns, 10 Hz",
                    "cell holder 20 C",
                ],
            },
            {
                "id": "tcspc",
                "label": "Measure lifetimes by TCSPC",
                "group": "Set up photophysics",
                "ref": "SI S1",
                "input": True,
                "what": (
                    "PC2+ prompt fluorescence used a Mini-Tau with an EPL-450 "
                    "at 446 nm (pulse width 74.5 ps). 4CzIPN and SO2TDS2- used "
                    "an FS5 spectrofluorometer with an EPL-375 at 371 nm "
                    "(58.3 ps) at 20 C. The instrument response was stray "
                    "light from dilute Ludox."
                ),
                "params": [
                    "EPL-450 446 nm for PC2+",
                    "EPL-375 371 nm for 4CzIPN and SO2TDS2-",
                ],
            },
            {
                "id": "delta_eps",
                "label": "Calibrate Δε of PC radical",
                "group": "Quantify cage escape at low and high Q",
                "ref": "SI S2.1",
                "what": (
                    "Biphenyl was the reference quencher. After 355 nm "
                    "excitation, the concentration of BP•+ came from ΔA "
                    "at 385 nm (literature Δε 27000 M⁻¹ cm⁻¹). PC•+ "
                    "and BP•+ form 1:1, and ΔA at 450 nm (no BP•+ there) "
                    "gave Δε₄₅₀(PC•+) = 13600 ± 700 M⁻¹ cm⁻¹, averaged "
                    "over five laser intensities."
                ),
                "params": [
                    "5 µM PC2+, 197 mM biphenyl, MeCN",
                    "Δε₄₅₀ = 13600 ± 700 M⁻¹ cm⁻¹",
                ],
            },
            {
                "id": "quench_sv",
                "label": "Stern-Volmer quench S1 and T1",
                "group": "Quantify cage escape at low and high Q",
                "ref": "SI S2.3; Table 1 caption",
                "what": (
                    "S1 quenching of PC2+ was TCSPC of prompt fluorescence "
                    "(excitation 446 nm, emission 525-575 nm, 200 kHz) in "
                    "air-equilibrated acetonitrile. T1 quenching was TAS of "
                    "the 405 nm triplet absorption in argon-saturated "
                    "acetonitrile (20 min of bubbling). Those rate constants "
                    "are what Table 1 uses for ηq and Φq."
                ),
                "params": [
                    "S1: TCSPC 446 nm, 525-575 nm, 200 kHz",
                    "T1: TAS 405 nm, Ar-saturated MeCN",
                ],
            },
            {
                "id": "actinometry",
                "label": "Count excited states vs Ru",
                "group": "Quantify cage escape at low and high Q",
                "ref": "SI S2.4; Fig. 3C",
                "what": (
                    "Relative actinometry used an iso-absorbing aqueous "
                    "[Ru(bpy)3]Cl2 solution under the same 355 nm pulses. "
                    "The ground-state bleach at 455 nm supplied the number "
                    "of *PC2+ per pulse for Φᵣ,ₜₒₜ in eqn (1)."
                ),
                "params": [
                    "iso-absorbing [Ru(bpy)3]2+ in water",
                    "bleach monitored at 455 nm",
                ],
            },
            {
                "id": "phi_r",
                "label": "Measure Φᵣ,ₜₒₜ versus Q",
                "group": "Quantify cage escape at low and high Q",
                "ref": "SI S2.4; Fig. 2; Results, spectroscopic evidence",
                "what": (
                    "Φᵣ,ₜₒₜ is free radicals per excited state (eqn 1). "
                    "[PC•+] came from Beer-Lambert with the calibrated "
                    "Δε and the 450 nm ΔA in a few-microsecond "
                    "window after cage escape, before bulk recombination "
                    "(hundreds of microseconds, Fig. S16). Phenol and "
                    "naphthalene were scanned over 0.1-200 mM."
                ),
                "params": [
                    "450 nm, few-microsecond averaging window",
                    "quencher 0.1-200 mM",
                ],
            },
            {
                "id": "eta_t",
                "label": "Get ηce,T at low Q",
                "group": "Quantify cage escape at low and high Q",
                "ref": "SI S2.5-S2.7; Table 1 series 1a/2a",
                "what": (
                    "Low quencher (0.22 mM phenol; 0.12 mM naphthalene) makes "
                    "quenching almost all triplet. Φᵣ,T with the known "
                    "ηisc and ηq,T gives ηce,T = 0.42 ± 0.02 "
                    "(phenol) and 0.46 ± 0.03 (naphthalene). Three pulse "
                    "energies stayed linear (Fig. S15), which they use to "
                    "rule out two-photon chemistry."
                ),
                "params": [
                    "phenol 0.22 mM; naphthalene 0.12 mM",
                    "ηce,T phenol 0.42 ± 0.02",
                ],
            },
            {
                "id": "eta_s",
                "label": "Get ηce,S at high Q",
                "group": "Quantify cage escape at low and high Q",
                "ref": "SI S2.5-S2.7; Table 1 series 1b/2b",
                "what": (
                    "High quencher still leaves residual triplet (ηisc = "
                    "0.05 at 132 mM phenol; solubility stops a further "
                    "increase). Equation (2) subtracts that triplet share "
                    "before equation (3) reports ηce,S = 0.028 ± 0.005 "
                    "(phenol) and 0.07 ± 0.01 (naphthalene at 120 mM)."
                ),
                "params": [
                    "phenol 132 mM; naphthalene 120 mM",
                    "ηce,S phenol 0.028 ± 0.005",
                ],
            },
            {
                "id": "fig4_model",
                "label": "Predict Φᵣ versus Q",
                "group": "Model the kinetics",
                "ref": "Fig. 4; Predicting concentration-dependent radical yield",
                "what": (
                    "Using k_q,S, k_q,T, k_isc, the unquenched lifetimes, "
                    "and the measured cage-escape efficiencies, they plot a "
                    "quenching-only Φq (monotonic) against Φᵣ that "
                    "includes cage escape (a maximum, then a low plateau). "
                    "Yellow points are the measured Φᵣ,ₜₒₜ from 0.1 to "
                    "200 mM. Rate constants are not printed in the main text."
                ),
                "params": [
                    "uses k_q,S, k_q,T, k_isc, τ₀",
                    "yellow dots: 0.1-200 mM",
                ],
            },
            {
                "id": "tadf_exact",
                "label": "Recheck with exact TADF kinetics",
                "group": "Model the kinetics",
                "ref": "SI S2.8; Mathematical treatment of TADF kinetics",
                "what": (
                    "Equations (2) and (3) treat the catalyst as non-TADF. "
                    "Section S2.8 adds isc-risc cycling and a recursion "
                    "factor. ηce,S and ηce,T come out the same, so the "
                    "first visit to each state dominates at the high "
                    "concentrations used in synthesis."
                ),
                "params": ["recursion factor for isc-risc cycling"],
            },
            {
                "id": "cw_sim",
                "label": "Simulate continuous irradiation",
                "group": "Simulate continuous light (models a and b)",
                "ref": "SI S2.9; Fig. 5; Transferring spectroscopic predictions",
                "what": (
                    "A Python model from Bellatreccia, Fina, and Ceroni "
                    "(University of Bologna). Model a: phenol is the "
                    "sacrificial donor and later steps are quantitative "
                    "(Fig. S26). Model b: the substrate itself is the "
                    "quencher. Conditions: [substrate] = 10 mM, [PC2+] = "
                    "1 mM, ε(440 nm) = 1e4 M⁻¹ cm⁻¹, flux 1e-3 "
                    "einstein s-1. Fig. 5 compares initial quencher of 10, "
                    "20, and 100 mM."
                ),
                "params": [
                    "[PC2+] = 1 mM; [substrate] = 10 mM",
                    "flux 1e-3 einstein s-1 at 440 nm",
                ],
            },
            {
                "id": "czipn",
                "label": "TAS of 4CzIPN with DMA",
                "group": "Test other catalysts",
                "ref": "SI S3.1; Fig. 6A and 6C",
                "what": (
                    "4CzIPN in toluene with DMA as a reversible reductive "
                    "quencher, on the same TAS bench. Relative radical "
                    "yields versus [DMA] give ηce,T / ηce,S = 125. "
                    "The relative radical signal falls almost to zero at "
                    "high DMA; they predict about a tenfold drop in "
                    "reaction quantum yield from 10 mM to 200 mM DMA."
                ),
                "params": [
                    "solvent: toluene",
                    "ηce,T / ηce,S = 125",
                ],
            },
            {
                "id": "so2tds",
                "label": "TAS of SO2TDS with ascorbate",
                "group": "Test other catalysts",
                "ref": "SI S3.2; Fig. 6B and 6C",
                "what": (
                    "The water-soluble non-TADF catalyst SO2TDS2- with "
                    "ascorbate monoanion in 200 mM phosphate buffer at "
                    "pH 7.2. Relative cage-escape ratio 11.5. They "
                    "reproduced the known radical spectra rather than "
                    "repeating the absolute Δε calibration used "
                    "for PC2+."
                ),
                "params": [
                    "200 mM phosphate buffer, pH 7.2",
                    "ηce,T / ηce,S = 11.5",
                ],
            },
            {
                "id": "pinacol",
                "label": "Pinacol under 390 nm LED",
                "group": "Test other catalysts",
                "ref": "SI S3.2; SI S1 irradiation experiments",
                "what": (
                    "Acetophenone 15.7 mM, SO2TDS2-, and HAsc- in "
                    "Ar-saturated D2O with 200 mM phosphate. A Kessil "
                    "RP160L 390 nm LED irradiated a septum-sealed NMR "
                    "tube in a water bath, still on an Ar line. Yield "
                    "was 1H NMR versus NaOAc. Performance was about 50% "
                    "higher at 19.2 mM HAsc- than at 96.9 mM."
                ),
                "params": [
                    "Kessil RP160L 390 nm",
                    "acetophenone 15.7 mM in D2O",
                ],
            },
        ],
        "edges": [
            {
                "from": "synth_pc",
                "to": "tas_setup",
                "ref": "Author contributions; SI S1",
                "data": "PC2+ from Dortmund to Mainz TAS",
            },
            {
                "from": "tas_setup",
                "to": "delta_eps",
                "ref": "SI S2.1",
                "data": "355 nm TAS traces of PC•+ and BP•+",
            },
            {
                "from": "tas_setup",
                "to": "quench_sv",
                "ref": "SI S2.3",
                "data": "T1 decays at 405 nm",
            },
            {
                "from": "tcspc",
                "to": "quench_sv",
                "ref": "SI S2.3",
                "data": "S1 prompt-fluorescence lifetimes",
            },
            {
                "from": "tas_setup",
                "to": "actinometry",
                "ref": "SI S2.4; Fig. 3C",
                "data": "same 355 nm pulses as the samples",
            },
            {
                "from": "delta_eps",
                "to": "phi_r",
                "ref": "SI S2.4",
                "data": "Δε₄₅₀ of PC•+",
            },
            {
                "from": "actinometry",
                "to": "phi_r",
                "ref": "SI S2.4; eqn (1)",
                "data": "number of *PC2+ per pulse",
            },
            {
                "from": "quench_sv",
                "to": "phi_r",
                "ref": "SI S2.3; Fig. 2",
                "data": "Φq,S and Φq,T versus Q",
            },
            {
                "from": "phi_r",
                "to": "eta_t",
                "ref": "SI S2.5 general procedure for ηce,T",
                "kind": "branch",
                "label": "low Q, mostly T1",
                "data": "Φᵣ,ₜₒₜ at low Q assigned to T1",
            },
            {
                "from": "phi_r",
                "to": "eta_s",
                "ref": "SI S2.5 general procedure for ηce,S",
                "kind": "branch",
                "label": "high Q, mostly S1",
                "data": "Φᵣ,ₜₒₜ minus residual T1",
            },
            {
                "from": "quench_sv",
                "to": "eta_t",
                "ref": "Table 1; SI S2.5",
                "data": "ηisc and ηq,T at low Q",
            },
            {
                "from": "quench_sv",
                "to": "eta_s",
                "ref": "Table 1; SI S2.5",
                "data": "ηisc and ηq,S at high Q",
            },
            {
                "from": "eta_t",
                "to": "fig4_model",
                "ref": "Fig. 4; Predicting concentration-dependent radical yield",
                "data": "ηce,T",
            },
            {
                "from": "eta_s",
                "to": "fig4_model",
                "ref": "Fig. 4",
                "data": "ηce,S",
            },
            {
                "from": "quench_sv",
                "to": "fig4_model",
                "ref": "Fig. 4",
                "data": "k_q,S, k_q,T, k_isc, τ₀",
            },
            {
                "from": "fig4_model",
                "to": "tadf_exact",
                "ref": "SI S2.8",
                "data": "same ηce values to re-derive",
            },
            {
                "from": "fig4_model",
                "to": "cw_sim",
                "ref": "SI S2.9",
                "data": "kinetic constants and ηce for models a and b",
            },
            {
                "from": "tas_setup",
                "to": "czipn",
                "ref": "SI S3.1",
                "data": "same LP980KS TAS bench",
            },
            {
                "from": "tas_setup",
                "to": "so2tds",
                "ref": "SI S3.2",
                "data": "same LP980KS TAS bench",
            },
            {
                "from": "tcspc",
                "to": "czipn",
                "ref": "SI S1; SI S3.1",
                "data": "FS5 / EPL-375 lifetimes of 4CzIPN",
            },
            {
                "from": "so2tds",
                "to": "pinacol",
                "ref": "SI S3.2; SI S1 irradiation experiments",
                "data": "relative SO2TDS radical yield vs Q",
            },
        ],
    }
    return (method_graph,)


@app.cell(hide_code=True)
def materials_methods():
    mo.md(r"""
    ## Materials and methods

    This is the pipeline in the paper and its SI, not a figure they printed. The boxes follow SI S1 (Mainz TAS and Dortmund synthesis), SI S2.1–S2.7 (Fig. 2, $\Phi_{\mathrm{r,tot}}$ and Table 1 cage escape), Fig. 4 (kinetic model), SI S2.9 (Fig. 5, continuous light), and SI S3 (Fig. 6, other catalysts). Nothing here is inferred: every arrow cites a section.

    The level picker at the top of the notebook sets the amount of detail. Child and Teen see the phases. Undergrad sees every stage. Grad student and Expert see short settings on the boxes and the full settings in the side panel.

    Drag the diagram to pan. Zoom with Ctrl-scroll or pinch, or the **+** / **−** buttons. **Fit** puts the whole graph in view; **Re-centre** goes back to the highlighted step. Prev / Next, the arrow keys, or a click on a box steps through the method.
    """)
    return


@app.cell(hide_code=True)
def method_diagram_widget():
    method_view = MermaidView()
    method_view
    return (method_view,)


@app.cell(hide_code=True)
def method_diagram(method_graph, method_view, reader_level):
    method_level = method_view_name(reader_level.value)
    method_view.source = mermaid_from_graph(method_graph, method_level)
    method_view.steps = method_steps(method_graph, method_level)
    method_problems = check_method_graph(method_graph)
    if method_problems:
        method_check = mo.callout(
            mo.md(
                "The method graph still has problems:\n\n"
                + "\n".join(f"- {item}" for item in method_problems)
            ),
            kind="warn",
        )
    else:
        method_check = mo.md(
            f"*Graph check: nothing to fix. View: **{method_level}** "
            f"({reader_level.value}).*"
        )
    method_check
    return


@app.cell(hide_code=True)
def evidence():
    mo.md(r"""
    ## What the paper reports, system by system

    All of these are from the main text or from a figure it points at. Supplementary figures are named where the text names them. Nothing in this table was read off a plot by eye.

    | System | What they compare | What they report |
    |---|---|---|
    | PC$^{2+}$ / 4-*tert*-butylphenol / MeCN | 0.3 mM vs 13 mM, 450 nm, Fig. 2 | $\Phi_{\mathrm{q,T}}, \Phi_{\mathrm{q,S}} = 0.65, 0.03$ at 0.3 mM and $0.30, 0.54$ at 13 mM. Radical signal lower at 13 mM despite higher total quenching |
    | Same pair, cage escape | Table 1: 0.22 mM (1a) and 132 mM (1b) | $\eta_{\mathrm{ce,T}} = 0.42 \pm 0.02$, $\eta_{\mathrm{ce,S}} = 0.028 \pm 0.005$ |
    | PC$^{2+}$ / naphthalene | 0.04 mM vs 54 mM, Fig. S14a | $\Phi_{\mathrm{q}} = (0.67, 0.02)$ vs $(0.18, 0.75)$. About a twofold larger PC•+ signal at the low concentration. Separate cage-escape runs: $0.46 \pm 0.03$ (0.12 mM) and $0.07 \pm 0.01$ (120 mM) |
    | 4CzIPN / DMA / toluene | Concentration series, Fig. 6A and 6C | $\eta_{\mathrm{ce,T}} / \eta_{\mathrm{ce,S}} = 125$. Relative radical signal falls almost to zero at high DMA. They predict about a tenfold drop in reaction quantum yield from 10 mM to 200 mM |
    | SO$_2$TDS$^{2-}$ / HAsc$^-$ / water | Fig. 6B and 6C, then a flask | Ratio of cage-escape efficiencies 11.5. Pinacol of acetophenone (15.7 mM), 390 nm: performance about 50% higher at 19.2 mM ascorbate than at 96.9 mM (Section S3.2) |
    | Continuous light, phenol model | Fig. 5; conditions in the text | [substrate] = 10 mM, [PC$^{2+}$] = 1 mM, $\varepsilon(440\,\mathrm{nm}) = 1 \times 10^4\,\mathrm{M^{-1}\,cm^{-1}}$, flux $1 \times 10^{-3}$ einstein s$^{-1}$. Initial quencher 10, 20, or 100 mM |

    The conclusions then do two pieces of interpretation. First, the triplet is the more productive manifold in all four pairs because triplet recombination is spin-forbidden, not because TADF recycles the singlet. Second, choosing a quencher concentration that still allows isc is a shared tactic for TADF and non-TADF catalysts. Both of those are the authors' reading of the table above. The second one is only as wide as the four pairs and the one preparative reaction.
    """)
    return


@app.cell(hide_code=True)
def lab_ask():
    mo.md(
        r"""
        ### Check, after the table

        The only preparative number in the main text is the pinacol coupling. Which way does it go?
        """
    )
    lab_choice = mo.ui.radio(
        options=[
            "About 50% higher performance at 19.2 mM HAsc− than at 96.9 mM",
            "About 50% higher performance at 96.9 mM HAsc− than at 19.2 mM",
            "The main text reports the spectroscopy and does not mention a flask reaction",
        ],
        label="Section S3.2, as the main text describes it…",
    )
    lab_choice
    return (lab_choice,)


@app.cell(hide_code=True)
def lab_feedback(lab_choice):
    plain_feedback(
        lab_choice,
        "About 50% higher performance at 19.2 mM HAsc− than at 96.9 mM",
        "Acetophenone at 15.7 mM, SO$_2$TDS$^{2-}$ as the catalyst, 390 nm LEDs. "
        "The text says this matches the direction of the spectroscopic radical yield in Fig. 6C. "
        "It does not say every reaction will be 50% faster.",
    )
    return


@app.cell(hide_code=True)
def demo_pick():
    mo.md(
        r"""
        ## Our demo: weight the two reported phenol points

        Figure 4 is a full kinetic prediction. The rate constants that draw it are not in the main text, so this notebook does not redraw Fig. 4 and does not invent those rates.

        What is below uses only the four quenching yields printed for 0.3 mM and 13 mM 4-*tert*-butylphenol, and the two phenol cage-escape efficiencies (central values 0.028 and 0.42). **Our demo** assumes

        $$\Phi_{\mathrm{r}} \approx \eta_{\mathrm{ce,S}}\Phi_{\mathrm{q,S}} + \eta_{\mathrm{ce,T}}\Phi_{\mathrm{q,T}}$$

        which is the relation you get if equations (3) and (4) are the inverses of that product, summed as in equation (2). That is a reading of how the text uses the equations, not a copy of the graphics. The $\pm$ ranges are ignored. The 0.3 mM and 13 mM yields are not the same experiments as Table 1's 0.22 mM and 132 mM rows.
        """
    )
    regime = mo.ui.radio(
        options=["0.3 mM", "13 mM"],
        value="0.3 mM",
        inline=True,
        label="Highlight a reported phenol concentration",
    )
    regime
    return (regime,)


@app.cell(hide_code=True)
def demo_chart(regime):
    def teaching_phi_r(phi_q_s: float, phi_q_t: float) -> float:
        """Weight each quenching yield by the phenol cage-escape efficiency.

        Our demo. Equation (2) splits the free-radical quantum yield into a
        singlet part and a triplet part. Equations (3) and (4) are images in
        the paper. This helper assumes those equations invert
        cage-escape efficiency times that state's quenching quantum yield.

        :param phi_q_s: Singlet quenching quantum yield at one stated concentration.
        :param phi_q_t: Triplet quenching quantum yield at the same concentration.
        :returns: A teaching estimate of the free-radical quantum yield.
        """
        eta_ce_s = ETA_CE_S_PHENOL
        eta_ce_t = ETA_CE_T_PHENOL
        return eta_ce_s * phi_q_s + eta_ce_t * phi_q_t

    low_phi_r = teaching_phi_r(PHI_Q_S_LOW, PHI_Q_T_LOW)
    high_phi_r = teaching_phi_r(PHI_Q_S_HIGH, PHI_Q_T_HIGH)
    labels = ["0.3 mM", "13 mM"]
    phi_s = [PHI_Q_S_LOW, PHI_Q_S_HIGH]
    phi_t = [PHI_Q_T_LOW, PHI_Q_T_HIGH]
    phi_sum = [PHI_Q_S_LOW + PHI_Q_T_LOW, PHI_Q_S_HIGH + PHI_Q_T_HIGH]
    phi_r = [low_phi_r, high_phi_r]
    yield_fig = go.Figure()
    yield_fig.add_bar(
        name="Φq,S reported",
        x=labels,
        y=phi_s,
        marker_color=SINGLET_COLOR,
    )
    yield_fig.add_bar(
        name="Φq,T reported",
        x=labels,
        y=phi_t,
        marker_color=TRIPLET_COLOR,
    )
    yield_fig.add_bar(
        name="Φq,S + Φq,T (our sum)",
        x=labels,
        y=phi_sum,
        marker_color=SUM_COLOR,
    )
    yield_fig.add_bar(
        name="teaching Φr (our demo)",
        x=labels,
        y=phi_r,
        marker_color=DEMO_COLOR,
    )
    yield_fig.update_layout(
        barmode="group",
        title="Phenol / PC2+ / MeCN: reported quenching yields, and a teaching radical yield",
        yaxis_title="Quantum yield (dimensionless)",
        paper_bgcolor="white",
        plot_bgcolor="white",
        height=420,
        margin=dict(l=60, r=20, t=60, b=40),
        legend=dict(orientation="h", y=-0.25),
        font=dict(family="Georgia, serif", size=13),
    )
    yield_fig.update_yaxes(gridcolor="#e2e8f0", range=[0, 1])
    highlighted = low_phi_r if regime.value == "0.3 mM" else high_phi_r
    reported_sum = (
        PHI_Q_S_LOW + PHI_Q_T_LOW
        if regime.value == "0.3 mM"
        else PHI_Q_S_HIGH + PHI_Q_T_HIGH
    )
    note = mo.md(
        f"""
        **{regime.value} 4-*tert*-butylphenol.** Our sum of the reported quenching yields is **{reported_sum:.2f}**.
        Our teaching $\\Phi_\\mathrm{{r}}$ is **{highlighted:.3f}** (central cage-escape efficiencies, no uncertainty propagated).
        Quenching is higher at 13 mM. The teaching radical yield is higher at 0.3 mM.
        That direction matches the paper's statement about Fig. 2. The teaching value is not a digitization of the inset.
        """
    )
    mo.vstack([yield_fig, note])
    return


@app.cell(hide_code=True)
def critique(reader_level):
    detail = (
        "### A critique you can do at this level"
        if reader_level.value in ("Grad student", "Expert")
        else "### For a graduate reading, switch the level picker"
    )
    body = mo.md(
        r"""
        The spectroscopic question — which spin state frees more radicals, and does concentration pick the state — is the one the transient-absorption design can answer. Iso-absorbing samples, actinometry, a microsecond window before bulk recombination, and a laser-power check are all aimed at that question. Four pairs and three solvents (acetonitrile, toluene, water) are the width of the claim as written.

        The preparative question is thinner. One pinacol coupling, reported as “about 50% higher” performance, is the only flask result in the main text. The continuous-light curves are a model with a stated photon flux, path-length absorption coefficient, and a sacrificial-donor mechanism (Fig. S26 is the scheme; the numbers used are those quoted above). A reader who came for a general synthetic rule has to supply the leap from $\Phi_{\mathrm{r,tot}}$ to isolated yield, catalyst death, and side reactions. The authors flag the last of these: a less efficient reaction needs more re-excitation and, they say, more chance of degradation. They do not measure that degradation here.

        Two assumptions are easy to miss. The pair is born with the spin of the precursor (they cite this as expected). And the 450 nm signal is entirely PC•+, which they argue by ruling out the oxidized phenol at that wavelength (SI Section S2.6) rather than by a measurement the main text plots.

        **Not rebuilt.** Fig. 4's rate constants, the exact TADF recursion (SI Section 2.8), and equations (1), (3), and (4), which are images.
        """
    )
    mo.vstack([mo.md(detail), body])
    return


@app.cell(hide_code=True)
def wrapup():
    mo.md(r"""
    ## What this does not settle, and where to go next

    The paper does not give you a universal optimal concentration. For the phenol model the quantum-yield maximum is near 1 mM, and full conversion of a 10 mM substrate still wants a stoichiometric donor. Below about 0.1 mM the same model is limited by triplet quenching that has not finished. Catalysts with a low intersystem-crossing yield (they estimate below about 10%, for a tenfold cage-escape gap) are not expected to show the maximum at all.

    Read next, all checked on Crossref except where noted as the paper's own reference entry:

    - Bryden and Zysman-Colman, *Chem. Soc. Rev.* **2021**, *50*, 7587–7680. DOI 10.1039/d1cs00198a. The TADF-as-photocatalyst review.
    - Goodwin, Dickenson, Ripak, Deetz, and coworkers, *Chem. Rev.* **2024**. DOI 10.1021/acs.chemrev.3c00930. Cage-escape yields, the prior physical-chemistry map. This paper's ref. 23.
    - Tamaki, Kamogawa, Inoue, Ceroni, and Ishitani, *J. Am. Chem. Soc.* **2025**. DOI 10.1021/jacs.5c10614. The concentration effect inferred from product yields rather than from transient absorption. This paper's ref. 36.
    - Ritu, Schmitz, Burdenski, and coworkers, *ACS Catal.* **2025**, *15*, 16718–16730. DOI 10.1021/acscatal.5c06069. The PC$^{2+}$ catalyst itself. This paper's ref. 54.
    - Bellatreccia, Fina, and Ceroni, *Photochem. Photobiol. Sci.* **2026**. DOI 10.1007/s43630-026-00901-4. The kinetic model this paper reuses for continuous irradiation. This paper's ref. 68.

    Data: the paper says the sets behind the main figures go to the JGU library (Gutenberg Open Science) and the corresponding author's site after final publication, and that the SI holds methods, synthesis, and the kinetic modelling. This notebook did not re-download that archive.

    This notebook was drafted with an AI agent following the paper-to-notebook-skill. Numbers that are not in the paper are confined to the cells marked **Our demo**, and to the lifetime ratio 44 µs / 17 ns, which is arithmetic on Fig. 1B.
    """)
    return


@app.cell(hide_code=True)
def quiz_intro():
    mo.md(r"""
    ## Check yourself

    Five questions on the paper. Pick an answer to see why it is or isn't right. The demo plot is not one of the questions.
    """)
    return


@app.cell(hide_code=True)
def quiz_cell():
    quiz = mo.ui.anywidget(
        PaperQuiz(
            questions=[
                {
                    "question": "What is the paper's central claim about quencher concentration for these dual singlet–triplet photoredox systems?",
                    "answer": "Lower quencher concentrations can raise the free-radical quantum yield, because they favor triplet quenching, and triplet-born pairs escape the solvent cage more efficiently than singlet-born pairs.",
                    "explain": "Abstract and Conclusions. The authors call this “less is more” and tie it to spin-dependent cage escape. It is not a claim about absorbing more photons.",
                    "distractors": {
                        "Higher quencher concentrations raise the free-radical quantum yield, because a Stern–Volmer experiment shows that more of the excited state is quenched.": "This is the habit the introduction says is intuitive and that Fig. 2 rejects. Between 0.3 mM and 13 mM phenol, total quenching goes up and the radical signal goes down.",
                        "Diluting the quencher raises the yield because the photocatalyst then absorbs a larger fraction of the incident light.": "The Fig. 2 comparison uses iso-absorbing solutions of 5 µM PC2+. The effect is which excited state gets quenched, not the optical density.",
                        "The yield rises at low quencher concentration because reverse intersystem crossing recycles the singlet, so each photon is used several times.": "The non-TADF-approximation section says the exact TADF treatment, which includes that recycling, gives the same cage-escape efficiencies, and that repopulation is not what makes the triplet more productive in the systems they studied.",
                    },
                },
                {
                    "question": "For PC2+ with 4-tert-butylphenol in acetonitrile, what happens to free-radical production when the phenol concentration goes from 0.3 mM to 13 mM?",
                    "answer": "The 450 nm signal from free PC•+ drops, even though total quenching rises: Φq,S goes from 0.03 to 0.54 and Φq,T goes from 0.65 to 0.30.",
                    "explain": "Results section “Spectroscopic evidence of the less is more effect,” and Fig. 2. The text says the higher total quenching efficiency at 13 mM still gives a markedly lower free-radical quantum yield.",
                    "distractors": {
                        "The 450 nm signal rises, because more of the excited state is quenched at 13 mM.": "That reverses Fig. 2. Total quenching is higher at 13 mM (0.54 + 0.30 versus 0.03 + 0.65), and the radical signal is lower.",
                        "The signal is unchanged, because the two solutions were prepared to be iso-absorbing.": "Iso-absorbing means the same PC2+ absorbance (Fig. 2 caption), not the same radical yield. The traces are different.",
                        "Only the naphthalene series shows a smaller signal at high concentration. The phenol traces do not.": "Fig. 2 is the phenol comparison. Naphthalene is a second case: about a twofold larger PC•+ signal at 0.04 mM than at 54 mM (Fig. S14a).",
                    },
                },
                {
                    "question": "Why do the authors say a triplet-born geminate pair is more likely to yield free radicals than a singlet-born pair?",
                    "answer": "Back electron transfer to the ground-state reactants is spin-forbidden for the triplet pair and spin-allowed for the singlet pair, so the triplet pair has more opportunity to escape the cage.",
                    "explain": "Introduction and Fig. 1A. For the phenol they measure ηce,T = 0.42 ± 0.02 and ηce,S = 0.028 ± 0.005, which they describe as more than a tenfold gap.",
                    "distractors": {
                        "The triplet is a stronger oxidant, so electron transfer from the triplet is more downhill.": "Fig. 1B prints +2.0 V for the singlet and +1.8 V for the triplet vs SCE. The singlet is the stronger excited-state oxidant. Both still oxidize naphthalene (+1.61 V) and the phenol (+1.65 V).",
                        "The singlet pair recombines more slowly, because recombination to the ground state is spin-forbidden from the singlet.": "That reverses the introduction. The ground state is a singlet, so recombination of the singlet pair is the spin-allowed path.",
                        "The triplet absorbs at 450 nm and the singlet does not, so only triplet events are detected.": "450 nm is the absorption of PC•+ after electron transfer (Fig. 2 and Fig. 3A), used for both concentrations. It is not a selective detector of the triplet excited state.",
                    },
                },
                {
                    "question": "When do the authors say you should not expect a maximum in free-radical yield versus quencher concentration?",
                    "answer": "When intersystem crossing is too inefficient to populate the triplet. For the roughly tenfold cage-escape gap they measured, they estimate that Φisc has to be on the order of 10% or the effect does not operate.",
                    "explain": "Section “Predicting concentration-dependent radical yield.” They also locate the downturn, for the phenol system, above about 1 mM, where singlet quenching competes with intersystem crossing, and a flat, low-yield region at very high concentration.",
                    "distractors": {
                        "When the solvent is polar. They report the effect only in toluene.": "The abstract says four catalyst–quencher systems and three solvents spanning a wide polarity range. The bodies of evidence include acetonitrile, toluene, and water.",
                        "When the photocatalyst is not a TADF dye. They say ordinary organic catalysts do not show it.": "SO2TDS2− in water is presented as a non-TADF example (Fig. 6B and 6C), and the conclusions put both classes under one concentration strategy.",
                        "Whenever the two cage-escape efficiencies differ by less than a factor of ten. Any smaller gap cannot produce a maximum.": "The “on the order of 10%” estimate is specifically for the tenfold gap they observed. The paper does not claim that every smaller gap is incapable of producing a maximum. It does say the effect is most pronounced when the cage-escape ratio is large (11.5 and 125 in Fig. 6C).",
                    },
                },
                {
                    "question": "Which statement matches what the authors do not conclude about a preparative flask?",
                    "answer": "They do not conclude that the quencher should be kept far below the substrate concentration. In the continuous-irradiation model the highest quantum yield is near 1 mM, but with 10 mM substrate they say at least a stoichiometric 10 mM of quencher is required for full conversion.",
                    "explain": "Section “Transferring spectroscopic predictions to continuous irradiation.” Model conditions: [substrate] = 10 mM, [PC2+] = 1 mM, ε = 1×10^4 M−1 cm−1 at 440 nm, photon flux 1×10−3 einstein s−1. Fig. 5 compares initial quencher concentrations of 10, 20, and 100 mM.",
                    "distractors": {
                        "They conclude that Stern–Volmer measurements are no longer worth doing.": "The conclusions call a high quenching efficiency an unreliable proxy for productivity. The quenching yields themselves come from those emission experiments (SI Section S2.3).",
                        "They conclude that every synthetic photoredox reaction will be about 50% faster if the quencher is diluted.": "The ~50% figure is one pinacol coupling of acetophenone (15.7 mM) with SO2TDS2− and ascorbate, 19.2 mM versus 96.9 mM, at 390 nm (Section S3.2). It is not offered as a general percentage.",
                        "They conclude that a sub-millimolar quencher concentration is the practical optimum whenever the flask must reach full conversion.": "That mixes the spectroscopic maximum (near 1 mM in the model; below about 0.1 mM the yield is limited by unfinished triplet quenching) with the stoichiometric requirement they state for full conversion.",
                    },
                },
            ]
        )
    )
    quiz
    return


if __name__ == "__main__":
    app.run()
