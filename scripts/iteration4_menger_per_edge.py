#!/usr/bin/env python3
"""Iteration-4 — exploratory (post hoc, NOT pre-registered): does the per-edge held-out-edge
benefit at top volume track alternate-path connectivity on the graph-contrastive graph?

The pre-registered iteration-4 endpoint is the *mean* held-out-edge ΔF1 against volume; it does
not ask whether edges with more alternate routes benefit more. This script asks that directly.
For each edge (a, b) of SET_G_N15_graph_contrastive_boundary_v1, k_alt is the number of
vertex-disjoint a–b paths once the edge itself is removed — the routes the held-out-edge
condition could in principle reconstruct the withheld boundary from. It also reports how many
non-hub edges have every alternate route passing through the ManipulativeCommunication hub.

Input: results/iteration4_scaling/per_edge_top_volume.json (written by
scripts/iteration4_vocab_control.py). CPU only, deterministic.

Run from the repository root:
    python scripts/iteration4_menger_per_edge.py
"""
from __future__ import annotations

import json
from pathlib import Path

import networkx as nx
import numpy as np
from networkx.algorithms.connectivity import local_node_connectivity
from scipy import stats

GRAPH = Path("pivot/graph_contrastive_boundary_set.json")
PER_EDGE = Path("results/iteration4_scaling/per_edge_top_volume.json")
OUT = Path("results/iteration4_scaling/menger_per_edge_top_volume.json")
HUB = "ManipulativeCommunication"


def k_alt(G: nx.Graph, a: str, b: str) -> int:
    H = G.copy()
    H.remove_edge(a, b)
    return local_node_connectivity(H, a, b) if nx.has_path(H, a, b) else 0


def main() -> None:
    spec = json.loads(GRAPH.read_text(encoding="utf-8"))
    G = nx.Graph()
    G.add_edges_from((e["a"], e["b"]) for e in spec["edges"])

    hub_only = 0
    non_hub = [(a, b) for a, b in G.edges() if HUB not in (a, b)]
    for a, b in non_hub:
        H = G.copy()
        H.remove_edge(a, b)
        if nx.has_path(H, a, b):
            H.remove_node(HUB)
            hub_only += not nx.has_path(H, a, b)

    rows = json.loads(PER_EDGE.read_text(encoding="utf-8"))["edges"]
    undirected: dict = {}
    for r in rows:
        key = tuple(sorted((r["target"], r["heldout_sibling"])))
        undirected.setdefault(key, []).append(r["heldout_edge_graph_aware_dF1"])
    keys = sorted(undirected)
    K = np.array([k_alt(G, a, b) for a, b in keys])
    D = np.array([np.mean(undirected[e]) for e in keys])

    rho = stats.spearmanr(K, D)
    hi, lo = D[K >= 2], D[K <= 1]
    mw = stats.mannwhitneyu(hi, lo)
    out = {
        "status": "exploratory, post hoc, NOT pre-registered",
        "graph": spec["name"], "n_edges": len(keys), "volume_per_context": 70,
        "unit": "undirected edge; held-out-edge dF1 averaged over both directions",
        "hub": HUB, "hub_degree": G.degree(HUB),
        "k_alt_distribution": {int(k): int((K == k).sum()) for k in sorted(set(K))},
        "non_hub_edges": len(non_hub), "non_hub_edges_all_alternates_via_hub": int(hub_only),
        "spearman_k_alt_vs_dF1": {"rho": float(rho.statistic), "p": float(rho.pvalue)},
        "k_alt_ge2_vs_le1": {"mean_ge2": float(hi.mean()), "n_ge2": len(hi), "mean_le1": float(lo.mean()),
                             "n_le1": len(lo), "mannwhitney_p": float(mw.pvalue)},
    }
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
