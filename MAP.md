# Capstone — MAP (start here)

*Navigational index for the relational-probe study. The one place to orient. Updated 2026-06-09.*

## Iteration ↔ HatCat-"Path" key (the naming that was getting confusing)

| Our label | What it tested | HatCat "Path" | Verdict |
|---|---|---|---|
| **iteration 1** | def-vs-relational probing + Menger (multiclass) | — | null (later understood as the *wrong question*) |
| **iteration 2** | pair-matched, powered, pre-registered Menger | the validity + power fix | **powered NULL** (partial Spearman −0.125) |
| **iteration 3** | relations as **hard negatives** | **Path 2** | **bounded positive** — local + ~⅓ lexical |
| **iteration 4** (done 2026-06-12) | scale-up retest of alternate-path / Menger | **Path 1 (scale) × Path-2 held-out-edge** | **powered NULL** — top volume +0.005, CI spans 0, MDE 0.014 |
| (later) | generate-mode vs read-mode | **Path 3** | not started |

## Owners
- **Jason (lead):** iterations 1–4 — pre-registrations, controls, the paper + slides.
- **p0ss (mentor):** `REPLICATION_WRITEUP.md`, `scripts/capstone_*`, `results/capstone_replication/` — E4B replication, related-negative + graph-contrastive follow-ups.

## Artifacts by type
- **Index / status:** `MAP.md` (this) · `README.md`
- **Cross-cutting log:** `LESSONS_LEARNT.md`
- **iter 1:** `TIMELINE.md` · `archive/iteration1_relational_probing/`
- **iter 2:** `ITERATION2_TIMELINE.md` · `R4_PREREGISTRATION.md` · `R4_LAMBDA_RECIPE.md` · `WRITEUP.md` · `R4_results_explorer.ipynb`
- **iter 3 (Path 2):** `ITERATION3_TIMELINE.md` · `PATH2_PREREGISTRATION.md` · `PATH2_CONTROLS_NOTE.md` · `results/path2_*.json`
- **iter 4 (scaling):** `iteration4_scaling/` — `PRIMER.md` (concepts, start here) · `RUNBOOK.md` (step-by-step run) · `PREREGISTRATION.md` (locked) · `ITERATION4_results_explorer.ipynb` (STEP 4: decision rule + E4B overlay + figs) · `figures/` (presentation PNGs) · `results/iteration4_scaling/` · near-OOS add-on for p0ss: `scripts/generate_near_oos_controls.py` + `audit/audit_near_oos.py` → `data/near_oos_controls.json`
- **p0ss (replication):** `REPLICATION_WRITEUP.md` · `results/capstone_replication/` · `scripts/capstone_*`
- **deliverable:** `paper/` (`PAPER_DRAFT.md` + `slides/`)
- **shared machinery — DO NOT MOVE (both pipelines reference these paths):** `scripts/` `data/` `activations/` `audit/` `pivot/` `results/`

## Current state (one line)
**Iteration 4 complete (2026-06-12): powered, pre-registered NULL** on alternate-path/Menger — held-out-edge flat-to-declining {+.008/+.012/+.009/+.005/+.005} across 7→70/ctx, top-volume CI spans 0, MDE 0.014 shown; direct effect positive but declining (+.061→+.040 — relational negatives are a *low-data lever*). Verdict + figures: `iteration4_scaling/ITERATION4_results_explorer.ipynb`. **Next = paper assembly** (`paper/PAPER_DRAFT.md` §5.4 filled) + near-OOS rejection test (p0ss).

## Conventions (going forward)
- New **code** → `scripts/` with a stage-clear name (`scaling_*`). New **results** → `results/<stage>/`. New **stage docs** → a `<stage>/` folder.
- **Pre-register** before any powered run; **adversarially verify positives**; **bound claims** honestly.
- The **final paper** (in `paper/`) *synthesises* the iterations — assembled at the end, not mid-flight. A one-pass tidy/archive of completed-iteration docs happens then.
