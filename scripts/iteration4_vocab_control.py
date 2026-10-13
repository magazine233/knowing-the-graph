#!/usr/bin/env python3
"""Iteration-4 — per-edge summary + vocabulary control on the scaled (70/context) data.

Discharges the pre-registered vocabulary item (iteration4_scaling/PREREGISTRATION.md §4:
"report the vocab regression on the scaled data so the held-out-edge result is read net of
lexical overlap where possible"). The pre-registration did not fix the exact model, so the
operationalisation below was chosen after the primary result was known — report it as the
pre-registered *item*, with a post-hoc *specification*.

Specification. For every (directed edge, held-out context, seed) row, a condition's
"vocabulary advantage" is how much more word overlap its negative set shares with the
evaluated sibling than the count-matched random set does:

    vocab_adv = mean_w Jaccard(sibling, neg) over the condition's negatives (weighted by
                passage count) − the same quantity over the random_non_graph negatives

Jaccard is over word sets ([a-z]{3,}) of each concept's passages, exactly as in
scripts/path2_hard_negatives.py. Rows are averaged to one value per directed edge (52), then

    ΔF1_edge ~ 1 + vocab_adv_edge         (OLS)

The intercept is the condition's ΔF1 at zero vocabulary advantage — the net-of-vocabulary
effect. Only the held-out-edge row is interpretable this way: the direct and mixed negative sets
contain the evaluated sibling itself (Jaccard = 1), so their vocab_adv is dominated by
self-overlap and their intercepts are extrapolations far outside the observed range. They are
written out for completeness, flagged as such.

Also writes (a) a compact per-edge table at the top volume (52 edges × 3 conditions) and (b) the
across-edge paired statistics at every volume whose rows file is present, so the paper's paired
tests and figure error bars can be re-checked without the 40 MB gitignored rows files.

Inputs: data/condition_a.json and results/iteration4_scaling/sweep_n70_rows.json (gitignored;
regenerate with iteration4_scaling/RUNBOOK.md STEP 3). CPU only, deterministic.

Run from the repository root:
    python scripts/iteration4_vocab_control.py [--rows-dir DIR]
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np
from scipy import stats

CONDS = ["direct_neighbors", "graph_aware_mixed", "heldout_edge_graph_aware"]
OUT_DIR = Path("results/iteration4_scaling")


def word_sets(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {c: set().union(*(set(re.findall(r"[a-z]{3,}", r["text"].lower())) for r in rows))
            for c, rows in data.items()}


def jaccard(A: set, B: set) -> float:
    return len(A & B) / len(A | B) if (A | B) else 0.0


def neg_overlap(row: dict, sibling: str, wset: dict) -> float:
    counts = row["negative_concept_counts"]
    total = sum(counts.values())
    return sum(n * jaccard(wset[sibling], wset[c]) for c, n in counts.items()) / total


def ols(y: np.ndarray, x: np.ndarray) -> dict:
    X = np.column_stack([np.ones(len(y)), x])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    dof = len(y) - X.shape[1]
    se = np.sqrt(np.diag(resid @ resid / dof * np.linalg.inv(X.T @ X)))
    t = beta / se
    p = 2 * stats.t.sf(np.abs(t), dof)
    half = stats.t.ppf(0.975, dof) * se
    return {"intercept": float(beta[0]), "intercept_ci95": [float(beta[0] - half[0]), float(beta[0] + half[0])],
            "intercept_p": float(p[0]), "slope_vocab_adv": float(beta[1]), "slope_p": float(p[1]),
            "r2": float(1 - resid @ resid / np.sum((y - y.mean()) ** 2))}


def edge_deltas(rows_path: Path, wset: dict) -> dict:
    """{condition: {(target, sibling): [(dF1, vocab_adv), ...]}} paired within (edge, context, seed)."""
    rows = json.loads(rows_path.read_text(encoding="utf-8"))
    by_key: dict = {}
    for r in rows:
        by_key.setdefault((r["target"], r["heldout_sibling"], r["held_context"], r["seed"]), {})[r["condition"]] = r

    per_edge: dict = {c: {} for c in CONDS}
    for (target, sib, _ctx, _seed), conds in by_key.items():
        base = conds.get("random_non_graph")
        if base is None or base.get("f1") is None:
            continue
        base_ov = neg_overlap(base, sib, wset)
        for c in CONDS:
            r = conds.get(c)
            if r is None or r.get("f1") is None:
                continue
            per_edge[c].setdefault((target, sib), []).append(
                (r["f1"] - base["f1"], neg_overlap(r, sib, wset) - base_ov))
    return per_edge


def paired_stats(d: np.ndarray) -> dict:
    n = len(d)
    se = d.std(ddof=1) / np.sqrt(n)
    lo, hi = stats.t.interval(0.95, n - 1, loc=d.mean(), scale=se)
    return {"mean_dF1": float(d.mean()), "ci95": [float(lo), float(hi)],
            "p_t": float(stats.ttest_1samp(d, 0.0).pvalue),
            "p_wilcoxon": float(stats.wilcoxon(d).pvalue),
            "mde_80pct_power": float((stats.t.ppf(0.975, n - 1) + stats.t.ppf(0.80, n - 1)) * se)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows-dir", default=str(OUT_DIR))
    ap.add_argument("--data", default="data/condition_a.json")
    args = ap.parse_args()
    rows_dir = Path(args.rows_dir)

    wset = word_sets(Path(args.data))

    by_volume = {}
    for vol in (7, 14, 28, 56, 70):
        path = rows_dir / f"sweep_n{vol}_rows.json"
        if not path.exists():
            continue
        pe = edge_deltas(path, wset)
        eds = sorted(pe["heldout_edge_graph_aware"])
        by_volume[str(vol)] = {c: {"n_edges": len(eds), **paired_stats(
            np.array([np.mean([v[0] for v in pe[c][e]]) for e in eds]))} for c in CONDS}
    (OUT_DIR / "paired_stats_by_volume.json").write_text(json.dumps({
        "model": "gemma-2-9b",
        "unit": "per directed edge (52), averaged over 4 held-out contexts x 30 seeds; one-sample t "
                "across edges (edges share endpoints, so these intervals are optimistic)",
        "by_volume": by_volume}, indent=2), encoding="utf-8")

    per_edge = edge_deltas(rows_dir / "sweep_n70_rows.json", wset)
    edges = sorted(per_edge["heldout_edge_graph_aware"])
    table, results = [], {}
    for c in CONDS:
        d = np.array([np.mean([v[0] for v in per_edge[c][e]]) for e in edges])
        v = np.array([np.mean([v[1] for v in per_edge[c][e]]) for e in edges])
        results[c] = {
            "n_edges": len(d),
            "gross": paired_stats(d),
            "mean_vocab_advantage": float(v.mean()),
            "net_of_vocab_ols": ols(d, v),
        }
        for i, e in enumerate(edges):
            if c == CONDS[0]:
                table.append({"target": e[0], "heldout_sibling": e[1]})
            table[i][f"{c}_dF1"] = float(d[i])
            table[i][f"{c}_vocab_adv"] = float(v[i])

    meta = {"source_rows": "sweep_n70_rows.json", "volume_per_context": 70, "model": "gemma-2-9b",
            "unit": "per directed edge, averaged over 4 held-out contexts x 30 seeds"}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "per_edge_top_volume.json").write_text(
        json.dumps({**meta, "edges": table}, indent=1), encoding="utf-8")
    (OUT_DIR / "vocab_control_top_volume.json").write_text(json.dumps({
        **meta,
        "status": "pre-registered item (PREREGISTRATION.md §4); specification chosen post hoc",
        "specification": "dF1_edge ~ 1 + vocab_adv_edge (OLS); intercept = net-of-vocabulary effect",
        "interpretable": ["heldout_edge_graph_aware"],
        "caveat": ("direct_neighbors and graph_aware_mixed include the evaluated sibling among their "
                   "negatives (self-Jaccard = 1), so their vocab_adv is dominated by self-overlap and "
                   "their intercepts are extrapolations; do not read them as net-of-vocabulary effects"),
        "results": results}, indent=2), encoding="utf-8")

    for c in CONDS:
        g, o = results[c]["gross"], results[c]["net_of_vocab_ols"]
        print(f"{c:26s} gross {g['mean_dF1']:+.4f} [{g['ci95'][0]:+.4f}, {g['ci95'][1]:+.4f}]  "
              f"vocab_adv {results[c]['mean_vocab_advantage']:+.4f}  net {o['intercept']:+.4f} "
              f"[{o['intercept_ci95'][0]:+.4f}, {o['intercept_ci95'][1]:+.4f}] p={o['intercept_p']:.3f}  "
              f"slope {o['slope_vocab_adv']:+.3f} (p={o['slope_p']:.3f}) R2={o['r2']:.2f}")
    for vol, st in by_volume.items():
        h = st["heldout_edge_graph_aware"]
        print(f"  vol {vol:>2s}: held-out-edge {h['mean_dF1']:+.4f} [{h['ci95'][0]:+.4f}, {h['ci95'][1]:+.4f}]")
    print(f"wrote per_edge_top_volume.json, vocab_control_top_volume.json, paired_stats_by_volume.json "
          f"in {OUT_DIR}")


if __name__ == "__main__":
    main()
