#!/usr/bin/env python3
"""Render the paper's figures from committed result JSONs (nothing hardcoded).

Run from the repository root:
    python paper/figures/make_figures.py

Writes vector PDFs (used by main.tex) and PNG previews into paper/figures/.
Inputs:
    pivot/graph_contrastive_boundary_set.json
    results/path2_hard_negatives.json, results/path2_placebo_graph.json
    results/iteration4_scaling/paired_stats_by_volume.json
    results/capstone_replication/graph_contrastive_discrimination.json            (E4B, 7/ctx)
    results/capstone_replication/gen_claude_x4/graph_contrastive_discrimination.json (E4B, 28/ctx)
    results/near_oos_rejection/near_oos_rejection.json
    results/iteration4_scaling/per_edge_top_volume.json
    results/iteration4_scaling/vocab_control_top_volume.json
    results/iteration4_scaling/menger_per_edge_top_volume.json
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import networkx as nx  # noqa: E402
import numpy as np  # noqa: E402
from networkx.algorithms.connectivity import local_node_connectivity  # noqa: E402

OUT = Path("paper/figures")
RES = Path("results")

# Reference palette, light mode, first three categorical slots (validated all-pairs) + neutrals.
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
GREY, LIGHT, INK, INK2 = "#8a8985", "#e4e3df", "#0b0b0b", "#52514e"
COND = {"direct_neighbors": (BLUE, "direct neighbours"),
        "graph_aware_mixed": (AQUA, "graph-aware mixed"),
        "heldout_edge_graph_aware": (ORANGE, "held-out edge (primary)")}

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8, "axes.titlesize": 8.5, "axes.labelsize": 8,
    "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "legend.fontsize": 7, "axes.edgecolor": INK2,
    "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2, "text.color": INK,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#eeeeec",
    "grid.linewidth": 0.6, "axes.axisbelow": True, "lines.linewidth": 2, "pdf.fonttype": 42,
    "savefig.dpi": 300, "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
})


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save(fig, name: str) -> None:
    fig.savefig(OUT / f"{name}.pdf")
    fig.savefig(OUT / f"{name}.png", dpi=200)
    plt.close(fig)
    print("wrote", OUT / f"{name}.pdf")


ABBR = {"ManipulativeCommunication": "Manip", "PersuasiveCommunication": "Persuas", "Propaganda": "Propag",
        "Misinformation": "Misinfo", "Disinformation": "Disinfo", "PsychologicalExploitation": "PsyExpl",
        "SycophancyRegister": "Syco", "UnwarrantedPraise": "Praise", "ExcessiveAgreement": "Agree",
        "Misdirection": "Misdir", "Threaten": "Threat", "UlteriorMotiveDetection": "Ulterior",
        "SpecificationGamingProcess": "SpecGame", "StrategicDeceptionPlanningProcess": "StratDec",
        "Deepfake": "Deepfake"}


# --------------------------------------------------------------------------- Fig. 1
def fig_conditions() -> None:
    spec = load(Path("pivot/graph_contrastive_boundary_set.json"))
    G = nx.Graph()
    G.add_nodes_from(c["id"] for c in spec["concepts"])
    G.add_edges_from((e["a"], e["b"]) for e in spec["edges"])
    hub = "ManipulativeCommunication"
    ring = [c["id"] for c in sorted(spec["concepts"], key=lambda c: c["cluster"]) if c["id"] != hub]
    ang = np.pi / 2 - 2 * np.pi * np.arange(len(ring)) / len(ring)
    pos = {hub: np.zeros(2), **{n: np.array([np.cos(a), np.sin(a)]) for n, a in zip(ring, ang)}}
    target, sib = "Misinformation", "Disinformation"
    nbrs = set(G[target])
    dist = nx.single_source_shortest_path_length(G, target)
    panels = [
        ("(a) random non-graph", {n: "pool" for n in G if n not in nbrs and n != target}),
        ("(b) direct neighbours", {n: "pool" for n in nbrs}),
        ("(c) held-out edge", {**{n: "pool" for n in nbrs if n != sib},
                               **{n: "pool_far" for n in G if dist.get(n, 9) >= 2}, sib: "heldout"}),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.7))
    for ax, (title, roles) in zip(axes, panels):
        ax.set_axis_off()
        ax.set_title(title, loc="left", fontweight="bold")
        nx.draw_networkx_edges(G, pos, ax=ax, edge_color="#cfcec9", width=0.8)
        if title.startswith("(c)"):
            nx.draw_networkx_edges(G, pos, edgelist=[(target, sib)], ax=ax, edge_color=ORANGE,
                                   width=1.6, style="dashed")
        for n in G:
            role = "target" if n == target else roles.get(n, "unused")
            face, edge, lw = {"target": (BLUE, INK, 1.0), "pool": (ORANGE, INK, 0.6),
                              "pool_far": ("#f6c3ad", INK2, 0.6), "heldout": ("white", ORANGE, 1.8),
                              "unused": (LIGHT, "#b5b4af", 0.6)}[role]
            ax.scatter(*pos[n], s=150, c=face, edgecolors=edge, linewidths=lw, zorder=3)
            x, y = pos[n]
            lx, ly = (x, y - 0.24) if np.hypot(x, y) < 0.1 else (x * 1.45, y * 1.45)
            ax.text(lx, ly, ABBR[n], ha="center", va="center", fontsize=5.8, color=INK2, zorder=4)
        ax.set_xlim(-1.8, 1.8)
        ax.set_ylim(-1.6, 1.6)
        ax.set_aspect("equal")
    handles = [plt.Line2D([], [], marker="o", ls="", ms=7, mfc=f, mec=e, mew=w, label=l) for f, e, w, l in [
        (BLUE, INK, 1.0, "target concept (probe trained for it)"),
        (ORANGE, INK, 0.6, "negative pool: direct neighbours"),
        ("#f6c3ad", INK2, 0.6, "negative pool: distance $\\geq$ 2"),
        ("white", ORANGE, 1.8, "held-out sibling (evaluated, never a negative)"),
        (LIGHT, "#b5b4af", 0.6, "not used")]]
    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.1),
               columnspacing=1.2, handletextpad=0.3)
    save(fig, "fig1_conditions")


# --------------------------------------------------------------------------- Fig. 2
def fig_path2() -> None:
    d = load(RES / "path2_hard_negatives.json")["experiment_A_primary"]
    rows = sorted(d["per_concept"], key=lambda r: r["delta"])
    fig, ax = plt.subplots(figsize=(3.4, 3.1))
    y = np.arange(len(rows))
    dl = np.array([r["delta"] for r in rows])
    ax.hlines(y, 0, dl, color=LIGHT, lw=2.2, zorder=1)
    ax.scatter(dl, y, s=30, color=BLUE, edgecolors="white", linewidths=1.2, zorder=3)
    ax.axvline(0, color=INK2, lw=0.8)
    m = d["primary"]["mean_delta"]
    ax.axvline(m, color=ORANGE, lw=1.2, ls="--")
    ax.text(m + 0.004, 1.0, f"mean +{m:.3f}", fontsize=6.8, color=INK, va="center")
    ax.set_yticks(y, [ABBR[r["concept"]] for r in rows])
    ax.set_xlabel("confusability gap: F1 vs random $-$ F1 vs sibling")
    ax.grid(axis="y", visible=False)
    save(fig, "fig2_path2_confusability")


# --------------------------------------------------------------------------- Fig. 3
def fig_sweep() -> None:
    st = load(RES / "iteration4_scaling/paired_stats_by_volume.json")["by_volume"]
    vols = sorted(int(v) for v in st)
    e4b = {7: load(RES / "capstone_replication/graph_contrastive_discrimination.json"),
           28: load(RES / "capstone_replication/gen_claude_x4/graph_contrastive_discrimination.json")}
    fig, ax = plt.subplots(figsize=(3.5, 2.7))
    for c, (col, lab) in COND.items():
        mu = np.array([st[str(v)][c]["mean_dF1"] for v in vols])
        lo = np.array([st[str(v)][c]["ci95"][0] for v in vols])
        hi = np.array([st[str(v)][c]["ci95"][1] for v in vols])
        ax.fill_between(vols, lo, hi, color=col, alpha=0.13, lw=0)
        ax.plot(vols, mu, color=col, marker="o", ms=4.5, mec="white", mew=1, label=lab, zorder=3)
        ex = sorted(e4b)
        ax.plot(ex, [e4b[v]["summary"]["deltas_vs_random"][c]["f1"]["mean"] for v in ex], ls="",
                marker="s", ms=4.5, mfc="white", mec=col, mew=1.2, zorder=4)
    ax.axhline(0, color=INK2, lw=0.8)
    ax.set_xticks(vols)
    ax.set_xlabel("training passages per concept per context")
    ax.set_ylabel("$\\Delta$F1 vs random negatives")
    h, l = ax.get_legend_handles_labels()
    h.append(plt.Line2D([], [], ls="", marker="s", mfc="white", mec=INK2, mew=1.2, ms=4.5))
    l.append("Gemma-4-E4B (peer replication)")
    ax.legend(h, l, loc="lower center", frameon=False, ncol=2, bbox_to_anchor=(0.45, 1.0),
              columnspacing=1.0, handletextpad=0.4)
    save(fig, "fig3_scaling_sweep")


# --------------------------------------------------------------------------- Fig. 4
def fig_near_oos() -> None:
    n = load(RES / "near_oos_rejection/near_oos_rejection.json")
    R, P = n["results"], n["paired_tests_vs_random"]
    faces = [("fpr_graph_neighbors", "graph_neighbors", "graph\nneighbours"),
             ("fpr_offgraph_confusers", "offgraph_confusers", "off-graph\nconfusers"),
             ("fpr_near_oos_pooled", "near_oos", "near-out-of-set\n(legit. influence)")]
    schemes = [("random", GREY, "random"), ("graph_sibling", BLUE, "graph-sibling"),
               ("model_mined", ORANGE, "model-mined")]
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.0, 2.5), gridspec_kw={"width_ratios": [1.15, 1]})
    x = np.arange(len(faces))
    w = 0.26
    for i, (s, col, lab) in enumerate(schemes):
        vals = [R[s][f] for f, _, _ in faces]
        bars = a.bar(x + (i - 1) * w, vals, w - 0.03, color=col, label=lab)
        for bar, v in zip(bars, vals):
            a.text(bar.get_x() + bar.get_width() / 2, v + 0.006, f"{v:.2f}", ha="center", fontsize=6,
                   color=INK2)
    a.set_xticks(x, [t for _, _, t in faces])
    a.set_ylabel("FPR at 95% TPR")
    a.set_title("(a) false-positive rate by boundary face", loc="left", fontweight="bold")
    a.legend(frameon=False, loc="upper right", title="negatives", title_fontsize=7)
    a.grid(axis="x", visible=False)
    a.set_ylim(0, 0.45)

    ylab, yy = [], 0
    for _, key, txt in faces:
        for s, col, lab in schemes[1:]:
            t = P[key][s]
            lo, hi = t["ci95"]
            b.plot([lo, hi], [yy, yy], color=col, lw=1.6)
            b.scatter(t["mean_delta_vs_random"], yy, s=26, color=col, edgecolors="white", linewidths=1, zorder=3)
            pv = "p < 0.001" if t["wilcoxon_p"] < 0.001 else f"p = {t['wilcoxon_p']:.3f}"
            b.text(0.22, yy, f"{t['mean_delta_vs_random']:+.3f} ({pv})", va="center", fontsize=6.2, color=INK2)
            ylab.append(f"{txt.splitlines()[0]}: {lab}")
            yy -= 1
        yy -= 0.6
    b.axvline(0, color=INK2, lw=0.8)
    b.set_yticks([0, -1, -2.6, -3.6, -5.2, -6.2], ylab)
    b.set_xlim(-0.42, 0.58)
    b.set_xticks([-0.4, -0.2, 0, 0.2])
    b.set_xlabel("$\\Delta$FPR vs random negatives (95% CI)")
    b.set_title("(b) paired effect of each scheme", loc="left", fontweight="bold")
    b.grid(axis="y", visible=False)
    fig.tight_layout(w_pad=1.5)
    save(fig, "fig4_near_oos_rejection")


# --------------------------------------------------------------------------- Fig. 5 (appendix)
def fig_per_edge() -> None:
    pe = load(RES / "iteration4_scaling/per_edge_top_volume.json")["edges"]
    vc = load(RES / "iteration4_scaling/vocab_control_top_volume.json")["results"]["heldout_edge_graph_aware"]
    mg = load(RES / "iteration4_scaling/menger_per_edge_top_volume.json")
    spec = load(Path("pivot/graph_contrastive_boundary_set.json"))
    G = nx.Graph()
    G.add_edges_from((e["a"], e["b"]) for e in spec["edges"])
    d = np.array([r["heldout_edge_graph_aware_dF1"] for r in pe])
    v = np.array([r["heldout_edge_graph_aware_vocab_adv"] for r in pe])

    fig, (a, b) = plt.subplots(1, 2, figsize=(7.0, 2.5))
    a.scatter(v, d, s=16, color=ORANGE, edgecolors="white", linewidths=0.8, zorder=3)
    o = vc["net_of_vocab_ols"]
    xs = np.linspace(v.min(), v.max(), 50)
    a.plot(xs, o["intercept"] + o["slope_vocab_adv"] * xs, color=INK2, lw=1.2)
    a.axhline(0, color=INK2, lw=0.8)
    a.axvline(0, color=INK2, lw=0.6, ls=":")
    a.set_xlabel("vocabulary advantage of negatives over random set\n(mean Jaccard with the held-out sibling)")
    a.set_ylabel("held-out-edge $\\Delta$F1")
    lo, hi = o["intercept_ci95"]
    a.set_title("(a) vs vocabulary advantage (52 directed edges)", loc="left", fontweight="bold")
    a.text(0.98, 0.04, f"intercept {o['intercept']:+.4f} [{lo:+.4f}, {hi:+.4f}]\n$R^2$ = {o['r2']:.2f}",
           transform=a.transAxes, ha="right", va="bottom", fontsize=6.5, color=INK2)

    und: dict = {}
    for r in pe:
        und.setdefault(tuple(sorted((r["target"], r["heldout_sibling"]))), []).append(r["heldout_edge_graph_aware_dF1"])
    K, D = [], []
    for (x1, x2), vals in und.items():
        H = G.copy()
        H.remove_edge(x1, x2)
        K.append(local_node_connectivity(H, x1, x2) if nx.has_path(H, x1, x2) else 0)
        D.append(np.mean(vals))
    K, D = np.array(K), np.array(D)
    rng = np.random.default_rng(0)
    b.scatter(K + rng.uniform(-0.12, 0.12, len(K)), D, s=18, color=ORANGE, edgecolors="white",
              linewidths=0.8, zorder=3)
    for k in sorted(set(K)):
        b.hlines(D[K == k].mean(), k - 0.28, k + 0.28, color=INK, lw=1.4, zorder=4)
    b.axhline(0, color=INK2, lw=0.8)
    b.set_xticks(sorted(set(K)))
    b.set_xlabel("vertex-disjoint alternate paths (edge removed)")
    b.set_ylabel("held-out-edge $\\Delta$F1")
    s = mg["spearman_k_alt_vs_dF1"]
    b.set_title("(b) vs alternate-path count (26 edges)", loc="left", fontweight="bold")
    b.text(0.98, 0.96, f"Spearman $\\rho$ = {s['rho']:+.2f}, p = {s['p']:.3f}", transform=b.transAxes,
           ha="right", va="top", fontsize=6.5, color=INK2)
    b.grid(axis="x", visible=False)
    fig.tight_layout(w_pad=2)
    save(fig, "fig5_per_edge_diagnostics")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    fig_conditions()
    fig_path2()
    fig_sweep()
    fig_near_oos()
    fig_per_edge()
