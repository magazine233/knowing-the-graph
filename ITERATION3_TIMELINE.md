# Iteration 3 — Path 2 (relations as hard negatives): Methods and Results

*A record of iteration 3. Branch: `iteration-3` (off `main` after the iteration-2 merge).
Companions: [`PATH2_PREREGISTRATION.md`](PATH2_PREREGISTRATION.md), [`REPLICATION_WRITEUP.md`](REPLICATION_WRITEUP.md)
(p0ss), [`WRITEUP.md`](WRITEUP.md) (iteration 2), [`LESSONS_LEARNT.md`](LESSONS_LEARNT.md).*

---

## Summary

Iteration 3 tested **Path 2**: whether relations help when they enter as **hard negatives** (sibling discrimination)
rather than as the extra positives the capstone originally probed. The Path-2 result was run, adversarially verified,
and bounded by three controls (placebo, vocabulary, in-distribution split). A second researcher (p0ss) independently
ran the same experiment on a different model and converged. The bounded finding: declared relations identify the
concept pairs the model finds harder to separate (a real hard-negative source the capstone's positive-only proxy
missed), but the alignment runs substantially through shared vocabulary, the connectivity/graph structure barely
generalises, and the purely-structural component is real but modest.

---

## How iteration 3 followed from iterations 1–2 (the arc)

1. **Iteration 2** closed as a **powered, pre-registered NULL** (pair-matched Menger, Gemma-2-9B, primary
   partial Spearman −0.125). Tagged `iteration-2`; merged into `main` (`a5283b47`).
2. **p0ss replication** (on `main`): cross-model (Gemma-4-E4B) **null confirmed + strengthened**, and a **reframe** —
   the capstone tested the wrong *operationalisation* of "relationship" (extra **positives** in a joint multiclass
   read-mode probe). HatCat uses relations as **hard negatives** (sibling discrimination), per-concept lenses, a
   graduation gate, self-generated data, generate-mode. This yielded 5 candidate "Paths"; Path 2 = relations-as-hard-negatives.
3. **Pivot** (hygienic): merge iteration-2 → main; 4-lens agent verification of the replication
   (numbers reproduce **12/12**, label-leak found in p0ss's `condition_b.json`, so clean data only is used, model
   decision = Gemma-2-9B committed activations); pre-register Path 2.

---

## Path 2 — methods (Gemma-2-9B, definitions-only, pre-registered)

Design (`PATH2_PREREGISTRATION.md`): siblings = **declared ontology edges** (covering all 15; `k≥2` zeroed 6); OOD
leave-one-context-out train-on-1; balanced logistic; 30 seeds. **Primary = Experiment A** (do declared siblings
predict representational confusability?); **Secondary = Experiment B** (hard-negative *training* utility — kept
secondary because it has a train-on-test-distribution triviality).

## Path 2 — results (`results/path2_hard_negatives.json`)

- **Exp A (primary): siblings ARE more confusable.** mean Δ = **+0.055, Wilcoxon p = 0.00015**, 13/15 concepts,
  holds excl. MC (+0.057, p = 0.0003).
- **Exp B (secondary): sibling-negative training helps.** F1 +0.096; graduation 53% vs 13%; 14/15 — *with the
  in-distribution caveat*.
- **Adversarially verified** (3 lenses): implementation clean / no leakage; reproduces from first principles; stats
  exact. Verdict: real, but the *claim* must be bounded.

## Three controls bounding the claim

- **Placebo-graph permutation** (`results/path2_placebo_graph.json`): the **declared graph is special** — it aligns
  with confusability ~3 SD better than random relabelings of the same topology (**z = 2.99, p = 0.002**). Not a
  uniform-cluster artefact.
- **Vocabulary control** (`results/path2_vocab_control.json`): vocab overlap strongly predicts F1 (Spearman −0.73);
  siblings +10% overlap; **~⅓ of the effect is lexical**; the residual is_sibling effect survives OLS (p = 0.0004) but
  is **marginal on the rank partial (p = 0.074)**. (Vocab plausibly *mediates* relatedness, so this over-controls.)
- **In-distribution split** (the held-out-edge / graph-aware condition, below): the clean alternate-path / Menger test,
  ≈0 at 1×, which serves as the in-distribution control and confirms the bounding.

**Honest bounded claim:** *declared relations identify the concept pairs Gemma-2-9B finds harder to separate
(validating relations as a real hard-negative source the capstone's positive-only proxy missed) — but the alignment
runs substantially through shared vocabulary, and the purely-structural component is real-but-modest. Tests 2 of
HatCat's 5 levers → necessary, not sufficient.*

---

## Independent convergence (p0ss)

In parallel, p0ss pushed **`c8899244` "related-negative follow-up"** to `main` (PR #14):
- `scripts/capstone_negative_relationship_discrimination.py` + `results/capstone_replication/negative_relationship_discrimination.json`.
- Design = **Experiment B** (per-concept lens; related-sibling vs count-matched random negatives; common
  held-out C-vs-sibling test). Model: **Gemma-4-E4B**, tier 8, 30 seeds.
- Result: related−random **F1 +0.112**, bal-acc +0.185, AUC +0.089 (1700/2400 positive). Conclusion:
  **"supported … recovers the relational effect when relations enter as contrastive negatives."**
- **Convergence:** +0.112 ≈ Exp B +0.096, on a *different model* — independent cross-model replication of
  the Path-2 headline. The value-add over the quick follow-up: the cleaner **Exp A primary** plus the **vocab**
  and **placebo** controls, which show the +0.11 is partly the in-distribution triviality + lexical overlap, with a
  real-but-modest structural core.

### Follow-ups and cross-model convergence (2026-06-09)

After the controls merged to main (PR #15), p0ss ran two follow-ups (PR #16/#17):
- **MLP** variant of the related-negative test: F1 **+0.105** (≈ linear +0.112) — not a linear-probe artifact.
- **Graph-contrastive test** (curated 26-edge graph, reuses E4B activations): `direct_neighbors` **+0.057**,
  `graph_aware_mixed` **+0.043**, **`heldout_edge_graph_aware` +0.008**. The held-out-edge condition (graph-aware
  negatives *excluding* the tested sibling) is the **clean alternate-path / Menger test** — and it is ≈0 at 1×.
  It is effectively the in-distribution control, and it **confirms the bounding**.

Synthesis (paper-ready): relations help as **local hard-negative contrast** (direct neighbours), but the
**graph/connectivity structure barely generalises** (held-out-edge +0.008; matching the iteration-2 Menger null),
and ~⅓ of the direct effect is **lexical**. Local yes; Menger/connectivity no; partly surface.

---

## Limitation: geometry caveat (graph↔representation mismatch)

A 4× graph-contrastive run (E4B, ~28/ctx) found the **held-out-edge mean flat at +0.010** (1× = +0.008), confirming
the flat trend. The task is near-ceiling, so scaling tightened *reliability*, not mean; the held-out-edge condition
was positive in only ~40% of pairs.

A centroid audit (p0ss) showed the curated graph is **not Gemma-native**: adjacent cosine 0.971 vs non-adjacent
0.961 (overlapping); graph-distance↔cosine r = −0.29; the nearest representational neighbour is a graph-neighbour for
only **6/15** concepts. The connectivity null may therefore be partly a **graph↔geometry mismatch** rather than a true
absence of alternate-path structure. This motivates Path 3 (generate-mode) and a Gemma-native graph derived from the
centroid audit, and bounds any claim that connectivity structure is genuinely absent.

---

## Iteration 4 (downstream)

p0ss's explicit next step is to retest the alternate-path/Menger prediction **after scaling** → iteration 4. An
iteration-4 teaching/scaling package was built with a LOCKED pre-registration (Gemma-2-9B, top 70/ctx, curve
{7,14,28,56,70}) in [`iteration4_scaling/`](iteration4_scaling/) — `PRIMER.md` (concepts), `RUNBOOK.md` (step-by-step
run, verified commands), `figures/` (presentation PNGs), `PREREGISTRATION.md`. File organisation was consolidated to
curb iteration sprawl: [`MAP.md`](MAP.md) (the index + iteration↔Path key), `iteration4_scaling/` (next-stage docs),
`paper/` (write-up + slides), `results/iteration4_scaling/`; shared machinery (`scripts/`, `data/`, `results/`,
`pivot/`, …) is referenced in place by both pipelines.

---

## Next steps

1. **Iteration-3 write-up** — synthesise the independent cross-model convergence (p0ss E4B + Gemma-2-9B) on "related
   negatives help", plus the controls that bound it honestly. Draft → adversarially verify → commit.
2. **Path 3 — generate-mode vs read-mode** — the agreed top next lever; needs its own pre-registration and
   generate-mode activation capture (local generation).

---

## Watch-items (don't repeat past traps)

- **In-distribution triviality:** the Exp-B / "+0.11" condition trains on the very siblings it tests → inflated; Exp A
  is the clean primary. Keep B interpreted *through* A.
- **Lexical confound:** related concepts share vocabulary; ~⅓ of the effect is that. Report the vocab control.
- **Positives need replication:** iteration 1 was fooled by a noise-positive. Path 2's positive survived 3-lens
  adversarial verify + 2 controls + independent cross-model convergence — believe it *as bounded*, not as a clean
  "mechanism recovered."
- **Necessary-not-sufficient:** Path 2 = 2 of 5 levers. "Supported" must not inflate to "the capstone hypothesis is
  vindicated."
