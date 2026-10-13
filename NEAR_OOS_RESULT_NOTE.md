# Near-OOS rejection test — result note

*Jason Boudville, 2026-08-05. Gemma-2-9B, layer 18. Run:
`python scripts/near_oos_rejection.py` → [`results/near_oos_rejection/near_oos_rejection.json`](results/near_oos_rejection/near_oos_rejection.json).
Analysis pre-committed in the iteration-4 paper draft §7 (now [`paper/main.tex`](paper/main.tex) §7) and
[`iteration4_scaling/RUNBOOK.md`](iteration4_scaling/RUNBOOK.md) STEP 5a; controls generated and blind-audited
2026-06-11 (84/84 self-match, zero in-set drift). Deterministic — verified by repeat run.*

## Headline

**Nothing seals the near-OOS face.** Legitimate-influence passages (Negotiation, Advertising, Lobbying) trip the
manipulation lenses at **FPR ≈ 0.16–0.18 at a 95%-TPR operating point**, and *no* negative-selection scheme moves
it — not the cheap human graph, not expensive model-mined confusers.

This is the fourth face measured, and the first one that no tier in the §7 recipe touches.

## The table (FPR @ 95% TPR, 14 lenses, negatives count-matched to graph degree)

| scheme | TPR | in-set | **nbr** | **off-graph** | far-OOD | **NEAR-OOS** | near/held-out ctx | near/seen ctx |
|---|---|---|---|---|---|---|---|---|
| random | 0.95 | 0.246 | 0.318 | 0.335 | 0.196 | **0.164** | 0.229 | 0.143 |
| graph_sibling | 0.95 | 0.266 | **0.032** | 0.378 | 0.320 | **0.175** | 0.225 | 0.158 |
| model_mined | 0.95 | 0.260 | 0.158 | **0.119** | 0.165 | **0.182** | 0.227 | 0.167 |

Paired across the 14 scored lenses, vs the random-negative baseline:

| face | graph_sibling | model_mined |
|---|---|---|
| graph neighbours | **−0.286**, CI [−0.378, −0.195], p=0.0001 | −0.161, CI [−0.271, −0.050], p=0.013 |
| off-graph confusers | +0.043, CI [−0.062, +0.147], p=0.50 | **−0.216**, CI [−0.328, −0.104], p=0.006 |
| **near-OOS** | **+0.010**, CI [−0.074, +0.095], p=0.86 | **+0.018**, CI [−0.101, +0.136], p=1.00 |

**The null is instrumented, not asserted.** The same lenses, thresholds, and paired test detect a −0.286 seal on
the neighbour face at p=0.0001 and a −0.216 seal on the off-graph face at p=0.006. A seal of that size on the
near-OOS face would have been unmissable. The near-OOS CIs are tight around zero and slightly *positive* — if
anything, training on graph siblings makes honest-influence leakage marginally worse.

## What else the run establishes

**It independently reproduces §7 on the 9B side.** Until now the FPR-by-face table was p0ss's E4B/L19 result only.
The same pattern holds on Gemma-2-9B/L18: graph siblings seal the neighbour face (0.318 → 0.032; p0ss: 0.192 →
0.046) and do nothing off-graph; model-mined confusers seal the off-graph face (0.335 → 0.119; p0ss: → 0.058) and
partly abandon the neighbour one. Different absolute values, same structure — **cross-model, cross-codebase
convergence on the "you seal the faces you train against" rule.** That upgrades §7 from a single-model extension
to a replicated finding.

**The leak is concentrated and nameable, not diffuse.** Near-OOS FPR per lens (graph_sibling), worst first:

| lens | FPR | | lens | FPR |
|---|---|---|---|---|
| UnwarrantedPraise | **0.589** | | Threaten | 0.107 |
| ExcessiveAgreement | **0.497** | | Deepfake | 0.083 |
| ManipulativeCommunication | 0.286 | | PsychologicalExploitation | 0.033 |
| Misdirection | 0.265 | | Misinformation | 0.003 |
| Disinformation | 0.208 | | Propaganda | 0.000 |
| SycophancyRegister | 0.188 | | StrategicDeceptionPlanning | 0.000 |
| SpecificationGamingProcess | 0.185 | | UlteriorMotiveDetection | 0.000 |

Three lenses never fire (a fourth, Misinformation, fires at 0.003). Two — the praise/agreement pair — account for most of the leak: honest
advertising and cooperative negotiation read as **UnwarrantedPraise** and **ExcessiveAgreement**. That is a
specific, actionable deployment failure, and it is exactly the pair the iteration-2 audit already flagged as
definitionally umbrella-ish.

**The context split matters and was worth pre-committing.** Leakage is significantly worse when the row's context
was held out of the lens's training fold: +0.068, p=0.016 (0.225 held-out vs 0.158 seen). **The honest
out-of-distribution number is ≈0.23, not the pooled 0.16.** Pooling flatters the result.

**The quarantine was correct.** PersuasiveCommunication fires on near-OOS rows at 0.238–0.523 — well above every
other lens. Its own training rows contain honest ads, so this is a true positive by construction, and pooling it
would have inflated the headline by a third. The pre-committed decision to quarantine it is vindicated by the
data rather than justified after the fact.

**Calibration drift reproduces, mildly.** Thresholds set on train positives instead of held-out ones collapse TPR
from 0.95 to 0.75–0.81 (and near-OOS FPR to a falsely reassuring ~0.05). Same direction as §7's finding, less
severe than p0ss's collapse to 34% — report as a milder reproduction, not a match.

## Figure

[`results/near_oos_rejection/fig8_fpr_by_face.png`](results/near_oos_rejection/fig8_fpr_by_face.png) —
rebuild with `python scripts/render_near_oos_figure.py` (reads the committed JSON; nothing hardcoded).

> **Fig. 8 — Nothing seals the near-out-of-set face.** False-positive rate at a 95%-TPR operating point for
> per-concept one-vs-rest lenses on Gemma-2-9B (layer 18), by boundary face and negative-selection scheme;
> 14 lenses with PersuasiveCommunication quarantined, negatives count-matched to graph degree. **(A)** Levels.
> Graph-sibling negatives collapse the neighbour face (0.318 → 0.032) but not the off-graph face; model-mined
> confusers collapse the off-graph face (0.335 → 0.119) and only partly the neighbour one. The near-out-of-set
> face — legitimate influence, trained against by nothing — sits flat at 0.164 / 0.175 / 0.182. **(B)** Paired
> effect estimates against the random-negative baseline with 95% CIs. Both positive controls clear zero
> (−0.286, p<0.001; −0.216, p=0.006) while both near-OOS intervals straddle it (+0.010, p=0.86; +0.018, p=1.00),
> so the null is separable from an underpowered one. Far-OOD is omitted: `multi_scale` is not run on this side, so
> that face is untrained here and its rate is not comparable to §7's sealed 0.000.

## Bounds and deviations (state these in the paper)

- **`multi_scale` was not run.** It trains against far-domain controls, and this repo has one usable far-domain
  set (photosynthesis, 20 rows); training and evaluating on it would leak. Far-OOD is **evaluation-only** here,
  which is why the far-OOD column is ~0.2–0.3 rather than §7's sealed 0.000 — nothing trained against it. **Do not
  present this column as contradicting §7's far-OOD result; it measures the untrained case.**
- **84 near-OOS rows, 3 concepts, 7 per context.** Small. The per-lens FPRs are coarse (granularity ~1/84 pooled)
  and the per-concept split (Advertising 0.190 / Lobbying 0.179 / Negotiation 0.155 under graph_sibling) should
  not be over-read — those differences are within noise.
- **One layer, one probe family, one model** — same bounds as the rest of the paper.
- **A caught bug, logged:** the first two runs of the random scheme differed (near-OOS 0.166 vs 0.142) because the
  seed used Python's `hash()`, which randomises string hashing per process. Switched to `zlib.crc32`; determinism
  verified by repeat run. Only the `random` scheme was affected — `graph_sibling` and `model_mined` were
  deterministic throughout and are unchanged.

## Why this matters for the paper

§7's recipe currently reads: cheap tiers everywhere, expensive mining only on the measured off-graph gap. This
result adds the gap the recipe does not close. The far-domain "other" tier handles passages about photosynthesis;
it does nothing for a legitimate negotiation. **The honest deployment claim is now: this scaffold rejects the easy
regime and leaks roughly one in four honest-influence passages in the hard one** — concentrated in two named
lenses.

It also sharpens the boundary-coverage model in §6.1 rather than complicating it. Near-OOS is simply another
facet, and no scheme in the study ever placed a constraint on it. The model implies this face should leak; it
does (consistent with the model, though the test was designed as a rejection test, not a test of the model); and the size of the leak is now measured instead of assumed.
