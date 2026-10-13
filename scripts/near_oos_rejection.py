#!/usr/bin/env python3
"""Near-OOS rejection test (Gemma-2-9B side) — the hard rejection regime.

The §7 far-domain controls (weather, basketball, photosynthesis) are the EASY
rejection regime: a passage about photosynthesis is never going to read as
gaslighting. The hard regime is the legitimate neighbour — influence that is
honest but adjacent: Negotiation, Advertising, Lobbying.

Pre-committed analysis (PAPER_DRAFT.md §7, iteration4_scaling/RUNBOOK.md STEP 5a):
  - the rejection test runs over the other 14 lenses;
  - PersuasiveCommunication is analytically QUARANTINED — its own marketplace
    training rows include honest ads and sales pitches, so it firing on these rows
    is a true positive by construction. Reported separately, never pooled.
  - FPR reported BOTH pooled AND split by whether a row's context was held out of
    the scoring lens's training fold.

Design mirrors scripts/capstone_multiscale_negatives.py (p0ss, E4B/L19) so the
result slots into the same FPR-by-face table: per-concept one-vs-rest lens,
mean-centred activations, held-out-context CV, negative COUNT held fixed at the
concept's graph degree, metric = FPR at a 95%-TPR operating point.

Deviation from that script, stated honestly: the `multi_scale` scheme is DROPPED
here. It trains against far-domain controls, and this repo has exactly one usable
far-domain control set (photosynthesis, 20 rows) — training on it and then
evaluating far-OOD leakage on it would be leakage. Far-OOD is therefore an
evaluation-only face on this side. Schemes run: random / graph_sibling / model_mined.

Cached activations only, no model, no API. CPU.
"""
from __future__ import annotations

import json
import time
import warnings
import zlib
from pathlib import Path

import numpy as np
import torch

warnings.filterwarnings("ignore")
from sklearn.linear_model import LogisticRegression  # noqa: E402

ACT = Path("activations/condition_a")
ACT_NEAR = Path("activations/near_oos_controls")
ACT_FAR = Path("activations/photosynthesis.pt")
DATA = Path("data/condition_a.json")
DATA_NEAR = Path("data/near_oos_controls.json")
GRAPH = Path("pivot/graph_contrastive_boundary_set.json")
OUT = Path("results/near_oos_rejection/near_oos_rejection.json")

CONTEXTS = ["workplace", "online", "relationships", "marketplace"]
TPR_TARGET = 0.95
SCHEMES = ["random", "graph_sibling", "model_mined"]
QUARANTINED = "PersuasiveCommunication"  # pre-committed: scored, never pooled
N_SEEDS_RANDOM = 5  # the random scheme is the only stochastic one
LAYER = 18
MODEL = "gemma-2-9b"


def mk():
    return LogisticRegression(max_iter=3000, C=1.0, class_weight="balanced")


def fpr(scores, thr):
    return float(np.mean(np.asarray(scores) >= thr)) if len(scores) else float("nan")


def main():
    t0 = time.time()
    g = json.loads(GRAPH.read_text())
    nodes = [c["id"] for c in g["concepts"]]
    adj = {n: set() for n in nodes}
    for e in g["edges"]:
        adj[e["a"]].add(e["b"])
        adj[e["b"]].add(e["a"])

    data = json.loads(DATA.read_text())
    ctx = {c: np.array([r["context"] for r in data[c]]) for c in nodes}
    near = json.loads(DATA_NEAR.read_text())
    near_names = sorted(near)
    nctx = {c: np.array([r["context"] for r in near[c]]) for c in near_names}

    X = {c: torch.load(ACT / f"{c}.pt", map_location="cpu").float().numpy() for c in nodes}
    XN = {c: torch.load(ACT_NEAR / f"{c}.pt", map_location="cpu").float().numpy() for c in near_names}
    XF = torch.load(ACT_FAR, map_location="cpu").float().numpy()

    # global mean-centring over every row that will be scored
    gm = np.concatenate([X[c] for c in nodes] + [XN[c] for c in near_names] + [XF]).mean(0)
    X = {c: X[c] - gm for c in nodes}
    XN = {c: XN[c] - gm for c in near_names}
    XF = XF - gm

    cent = {c: (lambda v: v / (np.linalg.norm(v) + 1e-9))(X[c].mean(0)) for c in nodes}
    cos = lambda a, b: float(cent[a] @ cent[b])
    confusers = {a: [m for _, m in sorted(((cos(a, m), m) for m in nodes if m != a), reverse=True)] for a in nodes}
    offgraph_conf = {a: [b for b in confusers[a][: max(len(adj[a]), 3)] if b not in adj[a]] for a in nodes}

    # score accumulators, per (scheme, lens)
    blank = lambda: {A: [] for A in nodes}
    pos_oof = {s: blank() for s in SCHEMES}      # out-of-fold positives (threshold calibration)
    pos_tr_s = {s: blank() for s in SCHEMES}     # in-fold train positives (drift check)
    neg_in = {s: {A: {B: [] for B in nodes if B != A} for A in nodes} for s in SCHEMES}
    far_s = {s: blank() for s in SCHEMES}
    # near-OOS split by whether the row's context was held out of THIS lens's training fold
    near_s = {s: {A: {"heldout": [], "seen": [], "by_concept": {n: [] for n in near_names}} for A in nodes}
              for s in SCHEMES}

    n_fits = 0
    for A in nodes:
        deg = len(adj[A])
        neigh = sorted(adj[A])
        mined = confusers[A][:deg]
        nonA = [c for c in nodes if c != A]

        for held in CONTEXTS:
            tr_mask = ctx[A] != held
            pos_tr = X[A][tr_mask]

            for scheme in SCHEMES:
                seeds = range(N_SEEDS_RANDOM) if scheme == "random" else [0]
                for seed in seeds:
                    if scheme == "random":
                        # zlib.crc32, not hash(): Python randomises str hashing per process
                        rng = np.random.default_rng(1000 * seed + zlib.crc32(A.encode()) % 997)
                        negs = list(rng.choice(nonA, size=min(deg, len(nonA)), replace=False))
                    else:
                        negs = {"graph_sibling": neigh, "model_mined": mined}[scheme]

                    neg_rows = [X[b][ctx[b] != held] for b in negs]
                    Xtr = np.concatenate([pos_tr] + neg_rows)
                    ytr = np.r_[np.ones(len(pos_tr)), np.zeros(sum(len(r) for r in neg_rows))]
                    clf = mk().fit(Xtr, ytr)
                    n_fits += 1

                    pos_oof[scheme][A].extend(clf.decision_function(X[A][ctx[A] == held]).tolist())
                    pos_tr_s[scheme][A].extend(clf.decision_function(pos_tr).tolist())
                    for B in nonA:
                        neg_in[scheme][A][B].extend(clf.decision_function(X[B][ctx[B] == held]).tolist())
                    far_s[scheme][A].extend(clf.decision_function(XF).tolist())

                    for n in near_names:
                        sc = clf.decision_function(XN[n])
                        hm = nctx[n] == held
                        near_s[scheme][A]["heldout"].extend(sc[hm].tolist())
                        near_s[scheme][A]["seen"].extend(sc[~hm].tolist())
                        near_s[scheme][A]["by_concept"][n].extend(sc.tolist())

    scored_lenses = [c for c in nodes if c != QUARANTINED]
    summary = {}
    for s in SCHEMES:
        rows = {}
        for A in nodes:
            thr = float(np.quantile(pos_oof[s][A], 1 - TPR_TARGET))
            thr_train = float(np.quantile(pos_tr_s[s][A], 1 - TPR_TARGET))
            nbr = [fpr(v, thr) for B, v in neg_in[s][A].items() if B in adj[A]]
            off = [fpr(v, thr) for B, v in neg_in[s][A].items() if B in offgraph_conf[A]]
            allo = [fpr(v, thr) for v in neg_in[s][A].values()]
            n_all = near_s[s][A]["heldout"] + near_s[s][A]["seen"]
            rows[A] = {
                "tpr_holdout": fpr(pos_oof[s][A], thr),
                "tpr_holdout_train_calibrated": fpr(pos_oof[s][A], thr_train),
                "fpr_in_set_all": float(np.mean(allo)),
                "fpr_graph_neighbors": float(np.mean(nbr)) if nbr else float("nan"),
                "fpr_offgraph_confusers": float(np.mean(off)) if off else float("nan"),
                "fpr_far_ood": fpr(far_s[s][A], thr),
                "fpr_near_oos_pooled": fpr(n_all, thr),
                "fpr_near_oos_context_heldout": fpr(near_s[s][A]["heldout"], thr),
                "fpr_near_oos_context_seen": fpr(near_s[s][A]["seen"], thr),
                "fpr_near_oos_train_calibrated": fpr(n_all, thr_train),
                "fpr_near_oos_by_concept": {n: fpr(v, thr) for n, v in near_s[s][A]["by_concept"].items()},
            }
        mean_over = lambda key: float(np.nanmean([rows[A][key] for A in scored_lenses]))
        summary[s] = {
            "n_lenses_scored": len(scored_lenses),
            "tpr_holdout": mean_over("tpr_holdout"),
            "tpr_holdout_train_calibrated": mean_over("tpr_holdout_train_calibrated"),
            "fpr_in_set_all": mean_over("fpr_in_set_all"),
            "fpr_graph_neighbors": mean_over("fpr_graph_neighbors"),
            "fpr_offgraph_confusers": mean_over("fpr_offgraph_confusers"),
            "fpr_far_ood": mean_over("fpr_far_ood"),
            "fpr_near_oos_pooled": mean_over("fpr_near_oos_pooled"),
            "fpr_near_oos_context_heldout": mean_over("fpr_near_oos_context_heldout"),
            "fpr_near_oos_context_seen": mean_over("fpr_near_oos_context_seen"),
            "fpr_near_oos_train_calibrated": mean_over("fpr_near_oos_train_calibrated"),
            "fpr_near_oos_by_concept": {
                n: float(np.nanmean([rows[A]["fpr_near_oos_by_concept"][n] for A in scored_lenses]))
                for n in near_names
            },
            "per_lens": rows,
            "quarantined_lens": {QUARANTINED: rows[QUARANTINED]},
        }

    # Paired tests across the scored lenses: does ANY negative scheme seal the near-OOS face?
    # The graph-neighbour face is the positive control — it shows the instrument can see a seal.
    from scipy import stats  # noqa: E402

    def vec(s, key):
        return np.array([summary[s]["per_lens"][A][key] for A in scored_lenses])

    paired = {}
    for face, key in [("near_oos", "fpr_near_oos_pooled"),
                      ("graph_neighbors", "fpr_graph_neighbors"),
                      ("offgraph_confusers", "fpr_offgraph_confusers")]:
        base = vec("random", key)
        paired[face] = {}
        for s in [x for x in SCHEMES if x != "random"]:
            d = vec(s, key) - base
            ok = ~np.isnan(d)  # some lenses have no off-graph confuser to score
            d = d[ok]
            if len(d) < 3:
                paired[face][s] = {"n_lenses": int(len(d)), "note": "too few lenses to test"}
                continue
            ci = stats.t.interval(0.95, len(d) - 1, loc=d.mean(), scale=stats.sem(d))
            paired[face][s] = {
                "n_lenses": int(len(d)),
                "mean_delta_vs_random": float(d.mean()),
                "ci95": [float(ci[0]), float(ci[1])],
                "ttest_p": float(stats.ttest_rel(vec(s, key)[ok], base[ok]).pvalue),
                "wilcoxon_p": float(stats.wilcoxon(vec(s, key)[ok], base[ok]).pvalue),
            }
    hs, sn = vec("graph_sibling", "fpr_near_oos_context_heldout"), vec("graph_sibling", "fpr_near_oos_context_seen")
    paired["near_oos_context_heldout_vs_seen"] = {
        "mean_delta": float((hs - sn).mean()),
        "wilcoxon_p": float(stats.wilcoxon(hs, sn).pvalue),
        "note": "positive = leakage is worse when the row's context was held out of the lens's training fold",
    }

    result = {
        "test": "near_oos_rejection",
        "model": MODEL,
        "layer_index": LAYER,
        "probe": "linear",
        "tpr_target": TPR_TARGET,
        "negatives_count": "matched to graph degree",
        "n_seeds_random_scheme": N_SEEDS_RANDOM,
        "schemes": SCHEMES,
        "schemes_omitted": {"multi_scale": "only one far-domain control set available; training and "
                                           "evaluating on it would leak. Far-OOD is evaluation-only here."},
        "near_oos_concepts": near_names,
        "near_oos_rows_per_concept": {n: len(near[n]) for n in near_names},
        "quarantined_lens": QUARANTINED,
        "quarantine_rationale": "its own marketplace training rows include honest ads and sales pitches, so "
                                "firing on these rows is a true positive by construction",
        "far_ood_control": "photosynthesis (20 rows, evaluation-only)",
        "n_fits": n_fits,
        "runtime_sec": round(time.time() - t0, 1),
        "paired_tests_vs_random": paired,
        "results": summary,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2))

    print(f"\nNear-OOS rejection — {MODEL} L{LAYER}, FPR @ {int(TPR_TARGET*100)}% TPR, "
          f"{len(scored_lenses)} lenses ({QUARANTINED} quarantined), {n_fits} fits in {result['runtime_sec']}s\n")
    hdr = f"  {'scheme':14s} {'TPR':>5s} {'inset':>7s} {'nbr':>7s} {'offgr':>7s} {'farOOD':>7s} " \
          f"{'NEAR':>7s} {'near/ho':>8s} {'near/seen':>10s}"
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))
    for s in SCHEMES:
        v = summary[s]
        print(f"  {s:14s} {v['tpr_holdout']:.2f} {v['fpr_in_set_all']:7.3f} {v['fpr_graph_neighbors']:7.3f} "
              f"{v['fpr_offgraph_confusers']:7.3f} {v['fpr_far_ood']:7.3f} {v['fpr_near_oos_pooled']:7.3f} "
              f"{v['fpr_near_oos_context_heldout']:8.3f} {v['fpr_near_oos_context_seen']:10.3f}")

    print("\n  near-OOS leakage by control concept:")
    for s in SCHEMES:
        bc = summary[s]["fpr_near_oos_by_concept"]
        print(f"    {s:14s} " + "  ".join(f"{n} {bc[n]:.3f}" for n in near_names))

    print(f"\n  QUARANTINED {QUARANTINED} (reported, never pooled): near-OOS FPR "
          + ", ".join(f"{s} {summary[s]['quarantined_lens'][QUARANTINED]['fpr_near_oos_pooled']:.3f}"
                      for s in SCHEMES))

    print("\n  calibration drift (threshold set on TRAIN positives instead of held-out):")
    for s in SCHEMES:
        v = summary[s]
        print(f"    {s:14s} TPR {v['tpr_holdout_train_calibrated']:.3f} "
              f"(vs {v['tpr_holdout']:.3f})   near-OOS FPR {v['fpr_near_oos_train_calibrated']:.3f} "
              f"(vs {v['fpr_near_oos_pooled']:.3f})")

    print("\n  PAIRED vs random across the 14 scored lenses (does any scheme seal the face?):")
    for face in ["near_oos", "graph_neighbors", "offgraph_confusers"]:
        print(f"    {face}:")
        for s, v in paired[face].items():
            if "mean_delta_vs_random" not in v:
                print(f"      {s:14s} {v['note']}")
                continue
            print(f"      {s:14s} delta {v['mean_delta_vs_random']:+.4f}  "
                  f"95%CI [{v['ci95'][0]:+.4f},{v['ci95'][1]:+.4f}]  wilcoxon-p={v['wilcoxon_p']:.4f}  "
                  f"(n={v['n_lenses']})")
    ch = paired["near_oos_context_heldout_vs_seen"]
    print(f"    near-OOS held-out-context vs seen-context: {ch['mean_delta']:+.4f} "
          f"(wilcoxon-p={ch['wilcoxon_p']:.4f})")

    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
