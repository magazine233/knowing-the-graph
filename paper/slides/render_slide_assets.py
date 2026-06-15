"""Render the bespoke slide visuals for TALK_8MIN.pptx -> paper/slides/assets/.

Run from project/capstone/:  python paper/slides/render_slide_assets.py
Then build the deck:         python paper/slides/build_deck.py

Three assets (the rest of the deck reuses iteration4_scaling/figures/):
  slide2_graph.png    - the curated SET G graph, clusters coloured, hub emphasised
  slide4_timeline.png - iter-1 noise-positive (struck) -> iter-2 powered pre-registered NULL
  slide7_cartoon.png  - boundary-coverage picture: near negative places the tested facet,
                        far constraint touches a different facet
"""
import json
import textwrap
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

ASSETS = Path("paper/slides/assets")
ASSETS.mkdir(parents=True, exist_ok=True)
CLUSTER_COLORS = {
    "influence_and_information_integrity": "#4C72B0",
    "deception_tactics_and_processes": "#C44E52",
    "approval_and_deference": "#55A868",
    "coercive_pressure": "#8172B2",
    "synthetic_media_and_falsehood": "#CCB974",
}


def wrap_label(name: str) -> str:
    # CamelCase -> spaced, wrapped for node labels
    out = "".join((" " + ch if ch.isupper() else ch) for ch in name).strip()
    return "\n".join(textwrap.wrap(out, 14))


def slide2_graph():
    g = json.loads(Path("pivot/graph_contrastive_boundary_set.json").read_text(encoding="utf-8"))
    G = nx.Graph()
    cluster = {c["id"]: c["cluster"] for c in g["concepts"]}
    G.add_nodes_from(cluster)
    G.add_edges_from((e["a"], e["b"]) for e in g["edges"])
    pos = nx.kamada_kawai_layout(G)
    pos = nx.spring_layout(G, pos=pos, seed=7, k=1.8, iterations=80)

    fig, ax = plt.subplots(figsize=(9, 6.2))
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color="#999999", width=1.2, alpha=0.7)
    hub = "ManipulativeCommunication"
    sizes = [2600 if n == hub else 1500 for n in G]
    colors = [CLUSTER_COLORS[cluster[n]] for n in G]
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=sizes, node_color=colors,
                           edgecolors=["black" if n == hub else "white" for n in G],
                           linewidths=[2.5 if n == hub else 1.0 for n in G], alpha=0.95)
    nx.draw_networkx_labels(G, pos, ax=ax, labels={n: wrap_label(n) for n in G},
                            font_size=7, font_weight="bold")
    # place the hub annotation pointing AWAY from the graph centroid to avoid collisions
    import numpy as np
    centre = np.mean(list(pos.values()), axis=0)
    away = np.array(pos[hub]) - centre
    away = away / (np.linalg.norm(away) + 1e-9)
    txt_xy = np.array(pos[hub]) + away * 0.45 + np.array([0, 0.12])
    ax.annotate("the hub\n(degree 7)", pos[hub], xytext=txt_xy,
                fontsize=10, fontstyle="italic", ha="center",
                arrowprops=dict(arrowstyle="->", color="black", lw=1.2))
    ax.set_title("SET G: 15 AI-safety concepts, 26 curated edges (colour = concept family)",
                 fontsize=12)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(ASSETS / "slide2_graph.png", dpi=200)
    plt.close(fig)


def slide4_timeline():
    fig, ax = plt.subplots(figsize=(9, 3.4))
    ax.axhline(0.5, color="#bbbbbb", lw=2, zorder=0)
    boxes = [
        (0.16, "ITERATION 1", '"positive!"', "#C44E52",
         "killed by adversarial verification:\nnoise artifact + wrong question\n(relations as extra positives)", True),
        (0.62, "ITERATION 2 (R4)", "powered, pre-registered", "#4C72B0",
         "105 matched pairs, rule locked first\npartial Spearman − 0.125  ≈  NULL\n(rank corr. of connectivity vs probe benefit,\ncontrolling for confounds — ≈ zero)", False),
    ]
    for x, title, sub, color, body, strike in boxes:
        ax.scatter([x], [0.5], s=220, color=color, zorder=3)
        ax.text(x, 0.80, title, ha="center", fontsize=13, fontweight="bold", color=color)
        t = ax.text(x, 0.68, sub, ha="center", fontsize=11, fontstyle="italic")
        if strike:
            t.set_bbox(dict(boxstyle="round,pad=0.25", fc="white", ec=color))
            ax.plot([x - 0.07, x + 0.07], [0.685, 0.685], color=color, lw=2)
        ax.text(x, 0.30, body, ha="center", va="top", fontsize=9.5)
    ax.annotate("", xy=(0.52, 0.5), xytext=(0.26, 0.5),
                arrowprops=dict(arrowstyle="->", lw=2, color="#555555"))
    ax.text(0.39, 0.555, "fix validity + power,\nlock the rule BEFORE the run", ha="center", fontsize=9)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(ASSETS / "slide4_timeline.png", dpi=200)
    plt.close(fig)


def slide7_cartoon():
    import numpy as np
    rng = np.random.default_rng(3)
    fig, ax = plt.subplots(figsize=(9, 5))
    a = rng.normal([0, 0], 0.55, (90, 2))
    ax.scatter(*a.T, s=14, color="#4C72B0", alpha=0.55, label="concept A (positives)")
    ax.scatter([0], [0], marker="*", s=420, color="#1a3a6b", zorder=5)
    ax.text(0.04, 0.12, "centroid\n(positives sharpen this)", fontsize=10, color="#1a3a6b")
    circ = plt.Circle((0, 0), 1.55, fill=False, color="#333333", lw=2, ls="-")
    ax.add_patch(circ)
    b = rng.normal([2.5, 0.4], 0.38, (45, 2))
    ax.scatter(*b.T, s=14, color="#C44E52", alpha=0.7, label="sibling B (near negative)")
    ax.annotate("", xy=(1.30, 0.21), xytext=(2.0, 0.33),
                arrowprops=dict(arrowstyle="-|>", lw=3, color="#C44E52"))
    ax.text(1.62, 0.62, "near negative\nplaces THIS facet\n(+0.06)", fontsize=11,
            color="#C44E52", fontweight="bold", ha="center")
    c = rng.normal([-2.2, -1.7], 0.33, (35, 2))
    ax.scatter(*c.T, s=14, color="#999999", alpha=0.7, label="distant relative C")
    ax.annotate("", xy=(-1.06, -0.82), xytext=(-1.78, -1.38),
                arrowprops=dict(arrowstyle="-|>", lw=3, color="#999999", ls=":"))
    ax.text(-2.25, -0.78, "far constraint touches\na DIFFERENT facet\n(held-out-edge ≈ 0)",
            fontsize=11, color="#777777", ha="center")
    ax.text(0, -2.35,
            'Positives sharpen the centroid; INDEPENDENT negatives place the boundary facets.\n'
            'Our graph’s "alternate paths" all route through one hub — correlated, not independent.',
            ha="center", fontsize=11.5, fontweight="bold")
    ax.set_xlim(-3.6, 3.6)
    ax.set_ylim(-2.8, 1.9)
    ax.axis("off")
    ax.legend(loc="upper left", fontsize=9, frameon=False)
    fig.tight_layout()
    fig.savefig(ASSETS / "slide7_cartoon.png", dpi=200)
    plt.close(fig)


def slide9_anisotropy(formal=False):
    """Before/after of the geometry near-miss: raw cosine (looks flat) vs mean-centred
    (structure reappears). Numbers from REPLICATION_WRITEUP §6 / paper §6.2.
    formal=True renders the academic-register variant (slide9_anisotropy_formal.png)."""
    import numpy as np
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(10, 4.4))

    t = {
        "sup": ("Geometry control: raw cosine is anisotropy-confounded; mean-centring recovers structure"
                if formal else "Twice the raw data nearly lied to us — twice a control caught it"),
        "lt": "Raw cosine\n(anisotropy-confounded)" if formal else "RAW cosine\n\"the graph isn't even in the model?\"",
        "la": "adjacent ≈ non-adjacent\n(artifact)" if formal else "looks flat —\nbut it's an artifact",
        "rt": "Mean-centred\n(graph structure recovered)" if formal else "MEAN-CENTRED (anisotropy removed)\nstructure snaps back",
        "rc": ("graded distance r ≈ −0.30:\nlocal structure real,\nmulti-hop absent" if formal
               else "graded distance\nstill flat (r ≈ −0.30):\nlocal real,\nmulti-hop absent"),
    }

    # LEFT — raw cosine: adjacent vs non-adjacent nearly identical (the trap)
    axL.bar([0, 1], [0.971, 0.961], color=["#4C72B0", "#C44E52"], width=0.6)
    axL.set_ylim(0.90, 1.0)
    axL.set_xticks([0, 1]); axL.set_xticklabels(["graph-\nadjacent", "non-\nadjacent"], fontsize=10)
    axL.set_title(t["lt"], fontsize=11)
    axL.set_ylabel("centroid cosine")
    for x, v in zip([0, 1], [0.971, 0.961]):
        axL.text(x, v + 0.002, f"{v:.3f}", ha="center", fontsize=11, fontweight="bold")
    axL.annotate(t["la"], (0.5, 0.935), ha="center", fontsize=10, fontstyle="italic", color="#777777")

    # RIGHT — mean-centred: structure reappears
    cats = ["adjacent\nseparation", "far controls\n(dog/weather)"]
    vals = [0.166, -0.147]
    axR.bar([0, 1], vals, color=["#55A868", "#999999"], width=0.6)
    axR.axhline(0, color="k", lw=0.8)
    axR.set_ylim(-0.22, 0.24)
    axR.set_xticks([0, 1]); axR.set_xticklabels(cats, fontsize=10)
    axR.set_title(t["rt"], fontsize=11)
    axR.set_ylabel("mean-centred cosine")
    axR.text(0, 0.166 + 0.012, "+0.166", ha="center", fontsize=11, fontweight="bold")
    axR.text(1, -0.147 - 0.022, "−0.147", ha="center", va="top", fontsize=11, fontweight="bold")
    axR.text(-0.35, -0.07, t["rc"], ha="left", va="top", fontsize=9, fontstyle="italic", color="#555555")

    fig.suptitle(t["sup"], fontsize=13, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(ASSETS / ("slide9_anisotropy_formal.png" if formal else "slide9_anisotropy.png"), dpi=200)
    plt.close(fig)


def menger_diagram():
    """Vertex-disjoint paths illustration for the Menger slide (transparent PNG, blends
    with any deck background). k(A,B)=3: three independent routes, no shared nodes."""
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    A, B = (0.0, 0.0), (6.0, 0.0)
    paths = [
        ([(1.8, 1.5), (4.2, 1.5)], "#3A6351"),   # A–C–D–B (top)
        ([(3.0, 0.0)], "#8C2D2D"),               # A–E–B (middle)
        ([(1.8, -1.5), (4.2, -1.5)], "#4C72B0"), # A–F–G–B (bottom)
    ]
    names = iter(["C", "D", "E", "F", "G"])
    for mids, color in paths:
        pts = [A] + mids + [B]
        for p1, p2 in zip(pts, pts[1:]):
            ax.annotate("", xy=p2, xytext=p1,
                        arrowprops=dict(arrowstyle="-", lw=2.4, color=color, alpha=0.85))
        for m in mids:
            ax.scatter(*m, s=900, color="white", edgecolors=color, linewidths=2.2, zorder=3)
            ax.text(*m, next(names), ha="center", va="center", fontsize=12, color=color,
                    fontweight="bold", zorder=4)
    for pt, name in [(A, "A"), (B, "B")]:
        ax.scatter(*pt, s=1500, color="#2B2B28", zorder=3)
        ax.text(*pt, name, ha="center", va="center", fontsize=15, color="white",
                fontweight="bold", zorder=4)
    ax.text(3.0, 2.35, "k(A, B) = 3 vertex-disjoint paths — no shared intermediate node",
            ha="center", fontsize=12.5, fontweight="bold", color="#2B2B28")
    ax.text(3.0, -2.35, "equivalently: disconnecting A from B requires removing at least 3 nodes",
            ha="center", fontsize=11, fontstyle="italic", color="#6E6A62")
    ax.set_xlim(-0.9, 6.9)
    ax.set_ylim(-2.8, 2.8)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(ASSETS / "menger_diagram.png", dpi=200, transparent=True)
    plt.close(fig)


if __name__ == "__main__":
    slide2_graph()
    slide4_timeline()
    slide7_cartoon()
    slide9_anisotropy()
    slide9_anisotropy(formal=True)
    menger_diagram()
    print(f"rendered 6 assets -> {ASSETS}")
