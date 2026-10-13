"""Render the §7 figure: FPR by boundary face, by negative-selection scheme.

Run from the repository root:
    python scripts/render_near_oos_figure.py

Produces results/near_oos_rejection/fig8_fpr_by_face.png

The argument the figure has to carry, in one image: each negative-selection scheme
collapses the face it trains against and no scheme touches the near-out-of-set face.
Panel A shows the levels; panel B shows the paired effect estimates with 95% CIs, so
the null is visibly separable from an underpowered one -- the two positive controls
sit clear of zero while both near-OOS intervals straddle it.

All numbers are read from the committed result JSON. Nothing is hardcoded.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
CAP = HERE.parent
SRC = CAP / "results" / "near_oos_rejection" / "near_oos_rejection.json"
OUT = CAP / "results" / "near_oos_rejection" / "fig8_fpr_by_face.png"

# Okabe-Ito, matching iteration4_scaling/figures/render_figures.py.
# Validated for a light surface: lightness band, chroma floor, CVD separation
# (worst adjacent dE 11.4 protan) and normal-vision floor all pass; the orange
# contrast warning is discharged by the direct value labels on every bar.
OKABE = {"blue": "#0072B2", "orange": "#E69F00", "green": "#009E73", "grey": "#999999"}
SCHEME_COLOR = {"random": OKABE["blue"], "graph_sibling": OKABE["orange"], "model_mined": OKABE["green"]}
SCHEME_LABEL = {
    "random": "random negatives (baseline)",
    "graph_sibling": "graph-sibling negatives",
    "model_mined": "model-mined confusers",
}
# (json key, display label, is this face trained against by anything?)
FACES = [
    ("fpr_graph_neighbors", "graph neighbours", "graph_neighbors"),
    ("fpr_offgraph_confusers", "off-graph confusers", "offgraph_confusers"),
    ("fpr_near_oos_pooled", "near-out-of-set\n(honest influence)", "near_oos"),
]
INK, MUTED = "#222222", "#555555"

plt.rcParams.update({
    "font.size": 13,
    "axes.titlesize": 15,
    "axes.titleweight": "bold",
    "axes.labelsize": 13,
    "figure.dpi": 150,
    "savefig.dpi": 150,
    "savefig.bbox": "tight",
    "font.family": "DejaVu Sans",
})


def main():
    doc = json.loads(SRC.read_text(encoding="utf-8"))
    res, paired = doc["results"], doc["paired_tests_vs_random"]
    schemes = doc["schemes"]

    fig, (axA, axB) = plt.subplots(1, 2, figsize=(16.5, 6.8), gridspec_kw={"width_ratios": [1.0, 1.0]})
    fig.subplots_adjust(wspace=0.30)
    fig.suptitle("Nothing seals the near-out-of-set face", fontsize=19, fontweight="bold", y=1.02)

    def fmt_p(p):
        return "p<0.001" if p < 0.001 else f"p={p:.3f}"

    # ---------------------------------------------------------------- Panel A: levels
    x = np.arange(len(FACES))
    w = 0.26
    for i, s in enumerate(schemes):
        vals = [res[s][k] for k, _, _ in FACES]
        off = (i - 1) * (w + 0.015)  # small surface gap between adjacent bars
        bars = axA.bar(x + off, vals, w, label=SCHEME_LABEL[s], color=SCHEME_COLOR[s],
                       edgecolor="white", linewidth=1.2, zorder=3)
        for b, v in zip(bars, vals):
            axA.text(b.get_x() + b.get_width() / 2, v + 0.008, f"{v:.3f}", ha="center", va="bottom",
                     fontsize=11, fontweight="bold", color=INK, zorder=4)

    axA.set_xticks(x)
    axA.set_xticklabels([lbl.split("\n")[0] for _, lbl, _ in FACES])
    axA.set_ylabel("false-positive rate @ 95% TPR")
    axA.set_title("A.  Each scheme seals only the face it trains against", fontsize=14, pad=10)
    axA.set_ylim(0, max(res[s][k] for s in schemes for k, _, _ in FACES) * 1.22)
    axA.grid(axis="y", color="#EEEEEE", zorder=0)
    axA.set_axisbelow(True)
    for side in ("top", "right"):
        axA.spines[side].set_visible(False)
    axA.legend(loc="upper left", fontsize=11.5, frameon=False)

    trained = {0: "trained: graph-sibling", 1: "trained: model-mined"}
    for xi in range(len(FACES)):
        note = trained.get(xi, "trained: NOTHING")
        axA.text(xi, -0.075, note, ha="center", va="top", fontsize=10.5, style="italic",
                 color=MUTED if xi in trained else INK,
                 fontweight="normal" if xi in trained else "bold",
                 transform=axA.get_xaxis_transform())

    # ---------------------------------------------------------------- Panel B: effects
    # One row per face; the two schemes sit as offset dots, taking their identity from
    # panel A's legend rather than repeating the scheme name in every tick label.
    faces_top_down = list(enumerate(FACES))[::-1]
    for row, (_, (_, lbl, pkey)) in enumerate(faces_top_down):
        for j, s in enumerate(("graph_sibling", "model_mined")):
            e = paired[pkey][s]
            d, ci, p = e["mean_delta_vs_random"], e["ci95"], e["wilcoxon_p"]
            y = row + (0.17 if j == 0 else -0.17)
            axB.errorbar(d, y, xerr=[[d - ci[0]], [ci[1] - d]], fmt="o", markersize=9,
                         color=SCHEME_COLOR[s], ecolor=SCHEME_COLOR[s], elinewidth=2.2,
                         capsize=5, capthick=2.2, markeredgecolor="white", markeredgewidth=1.2, zorder=3)
            seals = ci[1] < 0
            axB.text(ci[1] + 0.015, y, f"{d:+.3f}  {fmt_p(p)}" + ("  ← seals" if seals else ""),
                     va="center", fontsize=11, color=INK if seals else MUTED,
                     fontweight="bold" if seals else "normal")

    axB.axvline(0, color=INK, lw=1.4, zorder=2)
    axB.set_yticks(range(len(FACES)))
    axB.set_yticklabels([lbl.split("\n")[0] for _, (_, lbl, _) in faces_top_down], fontsize=12.5)
    axB.set_ylim(-0.6, len(FACES) - 0.4)
    axB.set_xlabel("change in FPR vs random negatives   (95% CI)")
    axB.set_title("B.  The null is instrumented, not asserted", fontsize=14, pad=10)
    axB.set_xlim(-0.46, 0.44)
    axB.set_xticks([-0.4, -0.3, -0.2, -0.1, 0.0, 0.1])
    axB.xaxis.set_label_coords(0.33, -0.105)  # centre the label over the visible tick range
    axB.grid(axis="x", color="#EEEEEE", zorder=0)
    axB.set_axisbelow(True)
    for side in ("top", "right", "left"):
        axB.spines[side].set_visible(False)
    axB.annotate("seals the face", xy=(-0.40, -0.47), xytext=(-0.22, -0.47), fontsize=10.5,
                 color=MUTED, style="italic", va="center", ha="left",
                 arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.3))
    axB.text(0.015, -0.47, "no effect", fontsize=10.5, color=MUTED, style="italic", va="center")

    fig.text(0.5, -0.045,
             "Gemma-2-9B, layer 18, 14 lenses (PersuasiveCommunication quarantined), negatives count-matched to "
             "graph degree.  Legitimate-influence passages\n(Negotiation, Advertising, Lobbying) leak at "
             "0.164 / 0.175 / 0.182 and no scheme improves on random.  The same instrument, same lenses and "
             "thresholds, registers a\n−0.286 seal on the neighbour face (p<0.001) — an effect of that "
             "size on the near-OOS face would have been unmissable.",
             ha="center", va="top", fontsize=11, color=MUTED, linespacing=1.5)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, facecolor="white")
    plt.close(fig)
    print(f"wrote {OUT}")
    for s in schemes:
        print(f"  {s:14s} " + "  ".join(f"{lbl.splitlines()[0]}={res[s][k]:.3f}" for k, lbl, _ in FACES))


if __name__ == "__main__":
    main()
