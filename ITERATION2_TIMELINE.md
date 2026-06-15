# Iteration 2 — Methodological Recast: Methods and Results

*A record of the methodological recast that followed iteration 1. Companion to [`README.md`](README.md), [`LESSONS_LEARNT.md`](LESSONS_LEARNT.md), and the iteration-1 record in [`TIMELINE.md`](TIMELINE.md) / [`archive/iteration1_relational_probing/`](archive/iteration1_relational_probing/).*
*Branch: `iteration-2` (off the `iteration-1` tag + the prepared foundation).*

---

## Summary

Iteration 1's null result was found to rest on a validity error: the relational signal for a concept pair was never tested against that pair. Iteration 2 recast the design around the pair as the unit of analysis, ran a power analysis to size the test, pre-registered the analysis, and executed a powered replication. The corrected, powered test returned a pre-registered **NULL** (primary partial Spearman = −0.125, p = 0.20). The borderline-positive pilot collapsed to ≈0 when re-measured at the powered dose, identifying it as small-sample noise.

---

## Why the design was recast (the validity error)

The mentor review identified "major methodological issues." Both reduced to the same root cause: **the relational signal for a pair was never tested against that pair** (full detail: [`LESSONS_LEARNT.md`](LESSONS_LEARNT.md) #recast).

- **Issue 1 — wrong test target.** `train_probes.py` used a *multi-class, leave-one-CONTEXT-out* test: train on 3 contexts, test on the 4th — which contains *all* concepts. So A-vs-B boundary data was judged by overall classification on a new *context*, not by A-vs-B discrimination. *(Analogy: adding "cat fur vs dog fur" and then scoring whether it improves llama detection.)*
- **Issue 2 — wrong training content.** The matched-B condition sampled each concept's **entire** boundary pool (A-vs-anything), not the **A-vs-B** edge specifically. *(Analogy: telling cat from dog by feeding cat-vs-llama and dog-vs-hamster details.)*

Net effect: iteration 1 never tested *"does A-vs-B relational data help distinguish A from B?"* Its null was a null about the wrong question.

---

## The corrected design (pair-matched on both ends)

**Unit = the pair.** For each concept pair (A, B):

1. **Binary A-vs-B probe**, two conditions, **volume-matched** (same number of passages):
   - *def-only:* A-definition + B-definition examples.
   - *def+relational:* same size, with **A-vs-B boundary** passages (pair-specific) swapped in for some definitions.
2. **Pair-specific, out-of-distribution evaluation:** leave-one-context-out — train on A/B (+ that pair's boundary) from 3 contexts, **test A-vs-B on the held-out context's A and B examples**.
3. **Effect** = `acc(def+rel) − acc(def-only)`, per pair, averaged over seeds/folds.
4. **Correlation:** per-pair effect against `k(A,B)`, **partialling out baseline separability** `acc(def-only)`.

Rationale for each piece: OOD-context evaluation defeats the surface-cheating ceiling; the binary, pair-specific test fixes Issue 1; pair-specific boundary content fixes Issue 2; volume-matching isolates content from data quantity; the partial correlation guards the headroom↔k confound.

---

## What was reused versus changed

**Reused unchanged** (not flagged in review):
- 15-concept **definition passages + activations** (`data/condition_a.json`, `activations/condition_a/`) — the def-only side.
- **SET G concepts + per-pair `k`** (`pivot/menger_analysis_v2.py`, `pivot/menger_analysis_output_v2.json`).
- The **OOD-context** headroom mechanism, the **volume-matched control**, and the **blind contamination audit**.

**Changed for iteration 2:**
- Boundary data was **pair-tagged**: `{pair:[A,B], exemplifies:A|B, context, text}` (iteration 1 discarded the partner — the root of Issue 2).
- Boundary coverage spanned the **k range**, not just the 18 graph edges.
- A new **pairwise analysis** (binary, OOD, volume-matched, tested on held-out A/B of the same pair) replaced the multi-class leave-one-context-out path, which was **retired** as the hypothesis test.

---

## Instruments

The boundary generator was pair-tagged and the corrected pairwise analysis was written before any data was generated.

- `scripts/generate_condition_b.py` recorded the pair on every boundary passage, with output schema `{pair:[A,B], exemplifies:<A|B>, context, text}`. A `--pairs` option allowed boundary generation for an arbitrary list of pairs (not only `RELATED_PAIRS`), so any pairs across `k` could be targeted. Output was written to `data/boundary_pairs.json`, kept separate from the iteration-1 `condition_b.json`. The generator retained all 18 `RELATED_PAIRS` distinctions and fell back to a generic A-vs-B distinction for any other `--pairs` pair; the default dose was `--per-context 10` (~5 per concept), since pair-specific boundary is thinner than iteration 1's concept-pooled version.
- `scripts/pairwise_relational.py` built def-only and volume-matched def+relational training sets from `data/condition_a.json` (defs) and `data/boundary_pairs.json` (that pair's boundary), per context; ran a binary logistic probe with leave-one-context-out, testing only on held-out-context A and B; and output per pair `acc_def`, `acc_rel`, `improvement`, `k`, plus seeds, followed by correlation (Pearson/Spearman + k≤1 vs k≥2) and partial correlation controlling `acc_def`. It exposed `--train-contexts` / `--n-bnd` to harden the OOD regime, and reported headroom (fraction of pairs with `acc_def < 0.95`) and dose (flagging pairs with thin/missing boundary so a flat improvement would not be mistaken for "no effect"). Output went to `results/pairwise_relational.json`.

Validation: `py_compile` passed on both scripts; a `--selftest` built a synthetic stub (new boundary schema + fake activations) and ran the real load/compute/correlation path end-to-end, asserting the per-pair fields, the sign-chain, and the dose audit; and the analysis shared no code with the retired multi-class leave-one-context-out path (`train_probes.train_and_eval`).

The boundary-activation layout expected was a single `activations/boundary/boundary_pairs.pt`, rows aligned to `data/boundary_pairs.json` list order.

---

## Pilot data and activations

Pair-tagged boundary was generated for a small **stratified** set of pilot pairs spanning `k`, with a real dose, then audited.

- ~8–12 pilot pairs were chosen to span `k = 1…5` and mix easy/hard (including the hard MC↔Disinfo / Misinfo↔Disinfo and some easy cross-cluster k=1 pairs), with candidate `k` drawn from `pivot/menger_analysis_output_v2.json`.
- `scripts/generate_condition_b.py --pairs "<A,B>;<C,D>;..."` produced `data/boundary_pairs.json` (≈5 per concept per context per pair).
- The boundary passages were re-audited for correct exemplifies-tagging (each passage's best-fit matched against its `exemplifies` label). `data/boundary_pairs.json` held each pilot pair × 4 contexts, roughly balanced A/B, every item carrying `pair`, `exemplifies`, `context`, and the spot-audit confirmed passages exemplified the tagged concept rather than the partner.

Boundary activations for the pilot passages were extracted (definitions were already extracted in iteration 1): `scripts/extract_activations.py` was adapted to process `data/boundary_pairs.json` → `activations/boundary/`, producing one `.pt` per pilot boundary passage set, rows aligned to `data/boundary_pairs.json` order, width 3584. Lambda spend for this step was under $2.

---

## Pilot analysis (R3)

The question at the pilot stage was whether pair-specific relational data improved that pair's OOD discrimination, volume-matched, and whether there was headroom to measure. The OOD difficulty was tuned (e.g. training on fewer contexts, or capping train examples) until a healthy fraction of pairs sat below ~0.95.

Outcomes:
- A meaningful fraction of pilot pairs had `acc_def < 0.95` (room for relational data to help): **6/12 below 0.95** (mean `acc_def` 0.918).
- On hard pairs, `acc_rel − acc_def` was measurable and directionally sensible: Sycophancy↔UnwarrantedPraise (k=3) **+0.074**, Disinfo↔MC (k=4) **+0.037**; the ceilinged MC↔Persuasive (k=2) **−0.061**.
- The plumbing was pair-matched end-to-end (content and test both about the same pair).

**Pilot result:** borderline pass — Spearman improvement-vs-`k` r = 0.58 (p = 0.049 raw) / **r = 0.64 (p = 0.035 partialling out `acc_def`)**; Pearson n.s. at n = 12. Regime: `train_contexts=1`, `n_bnd=3`, 20 seeds. Full read in [`LESSONS_LEARNT.md`](LESSONS_LEARNT.md#r3-gate).

---

## Decision: scale to a powered test

The question before scale-up was whether the corrected, pair-matched test produced a measurable, sensible relational effect on pairs that had headroom.

| Answer | Next |
|---|---|
| **Yes** | Scale to all/most pairs across `k` for the powered, *valid* Menger test |
| **No / still ceilinged** | Iterate the design (harder regime, layer, or a different instrument — e.g. steering/geometry per the candidate directions) before spending more |

**Decision — qualified yes, proceed to the powered run.** The pilot had headroom (6/12 pairs `acc_def < 0.95`) and a directionally-sensible effect that tracked `k` on rank and survived the `acc_def` confound control (partial Spearman r = 0.64, p = 0.035), but was underpowered (Pearson n.s. at n = 12, leverage-sensitive). The missing ingredient was **power, not signal**, and [`results/power_analysis.json`](results/power_analysis.json) indicated the full 105-pair run was well-powered even at the current dose.

The powered run was pre-registered ([`R4_PREREGISTRATION.md`](R4_PREREGISTRATION.md)) with: the locked regime (`train_contexts=1`, `n_bnd=3`, `n_seeds=20`, volume-matched, test on held-out A/B defs only); the **partial Spearman controlling `acc_def`** as the primary headline; a **14 defs/context** dose; and a **leverage guard** (leave-one-out on influential pairs + categorical k≤1 vs k≥2 fallback, 84 vs 21 pairs). Full reasoning: [`LESSONS_LEARNT.md`](LESSONS_LEARNT.md#r3-gate).

---

## Powered Menger test (R4)

Pair-tagged boundary was generated for all pairs across `k`, activations extracted, and `pairwise_relational.py` run to produce the valid improvement-vs-`k` correlation with the partial-correlation control.

- Per-pair improvement was estimated for **105 pairs**, median per-pair boot SD **0.0046** (n_test = 112); trend power ~1.0.
- Correlation was reported **raw and partialling out `acc_def`**, with Pearson, Spearman, and k≤1 vs k≥2, all in `results/pairwise_relational.json`.

**Result:** a powered, pre-registered **NULL**. Raw Pearson +0.07 / Spearman −0.03 (both n.s.); partial (primary) Spearman **−0.125, p = 0.20**. Mean improvement k≤1 +0.0017, k≥2 +0.0034 (both ≈0). The 12 pilot pairs collapsed from +0.64 to −0.04 at 14/context — the pilot positive was small-sample noise. Robust to a headroom-only subset (−0.20). The Menger prediction was **not supported** by the corrected, powered test. Full read: [`LESSONS_LEARNT.md`](LESSONS_LEARNT.md#r4-null); the results can be explored in [`R4_results_explorer.ipynb`](R4_results_explorer.ipynb).

---

## Write-up

The iteration-2 write-up (`WRITEUP.md`) leads with what was wrong in iteration 1 and how the pair-matched design fixes it, then reports the valid powered result with method, results, honest discussion, and limitations. The completed snapshot is tagged `iteration-2`.

---

## Watch-items carried forward (so iteration 1's traps are not repeated)

- **Headroom first.** Even OOD-binary, iteration-1 pairs averaged ~0.99 — most ceiling. The regime must be tuned so pairs sit below ceiling, or there is nothing to measure.
- **Headroom↔k confound.** Improvement *needs* headroom, and hard pairs are often high-`k`, so improvement is always reported **partialling out `acc_def`**, not raw, so a "Menger" signal is not just "hard pairs have more room."
- **Dose.** Pair-specific boundary is thinner than the old concept-pooled version — enough per pair per context is required.
- **Per-pair test-set power.** Each pair's improvement was estimated on only ~56 held-out decisions (7 A + 7 B × 4 folds) — too few to resolve a sub-0.10 per-pair effect, so the Menger trend was underpowered (~68%) and attenuated at that size. [`scripts/power_analysis.py`](scripts/power_analysis.py) sizes the **definitions per context** for a target MDES (14–21/context → ~92–98% trend power); after the pilot, it can be refined with `--emp-noise-sd` from a **test-point bootstrap**. Seed-stability does NOT capture this sampling noise (seeds hold the test set fixed — the iteration-1 trap).
- **Replicate.** Before believing any positive: fresh-data replication, not just seed-stability (the trap that fooled iteration 1).

---

*Reproducibility note: defs + their activations are reused from iteration 1; only boundary data and the pairwise analysis are new in iteration 2. The iteration-1 frozen snapshot is git tag `iteration-1`.*
