# 10-minute capstone talk — FORMAL register (script)

*Formal counterpart to `TALK_10MIN.md` (the spoken-voice cut). Same 11 slides, same figures, same numbers and
claims; titles and speaker notes are in the **academic register of `PAPER_DRAFT.md`** (no direct address,
contractions, or colloquial landings — phrasing pulled from the paper). Deliberately complete, as a **base to pare
back**: trim for time/delivery to taste. Built by `build_deck_10min_formal.py` → two shipped theme variants
(Jason's pick, for two audiences): `TALK_10MIN_formal_warm.pptx` (off-white paper, Georgia titles,
burgundy/deep-green) and `TALK_10MIN_formal_slate.pptx` (pale cool-grey, Segoe UI, navy). A no-arg run rebuilds
both; the unshipped "academic" theme remains available via `... academic`. The spoken-voice and 8-minute cuts are in
`archive/`. Audience: TARA participants. ~9:35 + buffer.*

---

## 1. Title (0:15)
**SHOW:** "Does relational structure improve linear-probe detection of related AI-safety concepts?" — Jason
Boudville. One line: *"Four iterations, two models, independently replicated — a bounded result."*
**SAY:** This talk asks whether relational structure between concepts improves linear-probe detection of related
AI-safety concepts. Across four iterations — every powered run pre-registered, with independent peer replication on a
second model — we reach a bounded result: relations help, but only as local hard-negative contrast; the graph's
connectivity contributes no measurable benefit.

## 2. Motivation (0:55)
**SHOW:** the SET G graph (hub emphasised). One line: *"Relational structure is cheap to specify; labelled data is not."*
**SAY:** Deployable safety monitoring requires a detector — a lens — for each behaviour of concern. These concepts
are not independent: manipulation, deception, and sycophancy form a graph of overlapping, related categories. The
hypothesis under test is that this relational structure can be exploited — that training each lens against its
relatives, and exploiting connectivity between concepts, improves detection and reduces the data required. The
appeal is straightforward: relational structure is inexpensive to specify, whereas labelled data is costly.

## 3. The HatCat programme and the relational hypothesis (1:15) [NEW]
**SHOW:** bullets — *HatCat: a navigable, interpretable map of the concepts a model represents* · *an atlas of
per-concept lenses connected by a relational graph* · *premise: relational knowledge improves discrimination and
coverage efficiency* · accent: *"We test the sharpest form: does the graph help, and does connectivity scale?"*
**SAY:** The hypothesis originates in HatCat, an interpretability programme whose objective is a navigable,
interpretable map of the concepts a model represents — not a single probe, but an atlas of per-concept lenses
connected by a relational graph. HatCat's central premise is that relational knowledge improves both
discrimination, through training against neighbouring concepts, and coverage efficiency, since the graph indicates
where to probe and connectivity provides access to concepts that lack direct data. This capstone evaluates the
sharpest, most falsifiable form of that premise: does relational structure measurably improve a linear probe, and
does the benefit scale with graph connectivity?

## 4. Experimental setup (0:30)
**SHOW:** fig1. Bullets: 15 concepts · 26-edge curated graph · 4 surface-distinct contexts · train-3 / test-1 (OOD) ·
layer-18 mean-pooled residual stream · logistic-regression probes · Gemma-2-9B (+ E4B peer replication) · 30 seeds.
**SAY:** The setup follows standard interpretability practice: the mean-pooled residual stream at layer 18 of
Gemma-2-9B, logistic-regression probes, 30 seeds, over 15 concepts and a curated 26-edge graph. The critical design
decision is out-of-distribution evaluation. Passages are generated across four surface-distinct contexts; probes are
trained on three and tested on the held-out fourth. Without this control, surface vocabulary saturates discrimination
to near-perfect accuracy and the experiment retains no headroom.

## 5. Iterations 1–2: a powered, pre-registered null (1:00)
**SHOW:** the iter-1 → iter-2 timeline (iter-1 struck through; iter-2 → partial Spearman −0.125 ≈ NULL).
**SAY:** Iteration 1 initially indicated a positive effect. Adversarial verification identified it as a noise
artifact, compounded by a mis-specification: relational knowledge had been operationalised as additional positive
examples rather than as contrastive structure. The design was rebuilt. Iteration 2 was a pair-matched, powered test
over 105 pairs, with the decision rule fixed in advance. It returned a clean null — a partial Spearman correlation of
minus 0.125 between connectivity and probe benefit. Because the analysis was pre-registered, the null is reported as
a result. It is subsequently explained, rather than merely recorded.

## 6. Iteration 3: relations as hard negatives (1:10)
**SHOW:** two-model table (direct +0.057/+0.059, mixed +0.043/+0.039, held-out-edge +0.008/+0.012); Path-2 controls
— placebo p=0.002, ~⅓ vocabulary.
**SAY:** The correct operationalisation uses related concepts as hard negatives rather than additional positives —
contrast, not coverage. Training each concept's probe against its graph siblings improves discrimination by
approximately 0.06 F1. A placebo-graph permutation confirms the effect is specific to the curated relationships, at
p equals 0.002, rather than an artifact of any graph. Two bounds apply. Approximately one third of the effect is
attributable to shared vocabulary — an upper bound, since the vocabulary regression over-controls. And the benefit
is confined to direct adjacency. The pattern replicates across both models and codebases.

## 7. Iteration 4: does the connectivity benefit scale? (1:15)
**SHOW:** fig5 (the scaling sweep, E4B overlaid). Bullets: *"held-out-edge: graph-aware negatives excluding the
evaluated sibling"* / *"top volume +0.005, 95% CI [−0.005, +0.014] — spans zero"* / *"MDE 0.014; direct effect 3×"* /
*"pre-registered NULL."*
**SAY:** The clean test of connectivity, as distinct from adjacency, is the held-out-edge condition: the probe is
trained on all graph-aware negatives except the sibling against which it is evaluated. If connectivity carries
transferable signal, the remaining relationships should partially reconstruct the withheld boundary. They do not —
the effect is approximately 0.01. To address the possibility that this reflects insufficient data, we pre-registered
a within-model scaling sweep to ten times the original volume. The held-out-edge delta does not increase; at the top
volume it is 0.005, with a 95% confidence interval spanning zero. The minimum detectable effect at this power was
0.014, and the same design resolves the direct-neighbour effect at three times that magnitude. The alternate-path,
or Menger, prediction is therefore refuted at adequate power.

## 8. Mechanism: independent-constraint boundary coverage (0:35)
**SHOW:** the boundary-coverage cartoon (near negative places the facet; far constraint faces elsewhere).
**SAY:** A single model accounts for the full pattern. A concept is represented as a centroid with a surrounding
distribution; the probe's boundary lies at the distribution's tail. Positive examples sharpen the centroid but do not
relocate the boundary; each negative constrains the boundary facet it faces. This predicts that additional positives
have no effect once the centroid is well estimated, that sibling negatives improve the tested boundary, and that the
benefit decreases with distance from it. The held-out-edge effect is null because, in this graph, the alternate paths
route through the ManipulativeCommunication hub: the constraints are correlated rather than independent. Connectivity
matters only insofar as it counts independent constraints.

## 9. Geometry control: the anisotropy correction (0:55) [NEW]
**SHOW:** before/after — raw cosine adjacent 0.971 vs non-adjacent 0.961 (anisotropy-confounded) vs mean-centred:
adjacent separation +0.166, far controls −0.147, graded distance r ≈ −0.30.
**SAY:** An unsupervised geometric check both corroborates the mechanism and illustrates the analysis discipline.
Raw cosine similarity between concept centroids suggested near-total overlap — 0.971 for adjacent versus 0.961 for
non-adjacent pairs — which would imply the graph is not represented in the model. This is an anisotropy artifact:
transformer activations occupy a narrow cone, inflating all similarities. After mean-centring, the structure is
recovered: adjacent pairs separate by 0.166, far-domain controls fall well outside the cluster at minus 0.147, while
graded graph distance remains uncorrelated with representation. The geometry independently reproduces the probe
result — local structure is real, multi-hop structure is absent — and the probe results themselves are unaffected,
since a linear classifier removes the common direction. This is the second instance in which a raw metric was
misleading and a control proved decisive.

## 10. Deployment: rejection scaffolds and tiered negatives (0:55)
**SHOW:** the faces table (FPR@95%TPR by negative scheme). Title: *"Each scheme seals only the faces it trains against."*
**SAY:** The findings yield a practical recipe. A flat 15-way classifier has no rejection option and assigns every
out-of-domain input to some concept; a coarse "other" class rejects out-of-family inputs at full recall with no
false rejection of genuine concepts. With negative count held fixed, false-positive rate at a 95%-true-positive
operating point shows that each scheme seals only the faces it trains against. Graph siblings seal the neighbour
face but not off-graph confusers, against which they perform no better than random. Model-mined confusers seal that
face — a 20-point reduction — but not the others. And a cheap "other" tier seals the far-out-of-distribution face
entirely. The recommended pipeline is therefore tiered: inexpensive negatives throughout, an audit to locate the
off-graph gap, and expensive mining applied only to that gap. Calibration drift is a material failure mode:
operating points set on training data degrade substantially under distribution shift.

## 11. Conclusions and future work (0:50)
**SHOW:** summary lines (pre-registration / adversarial verification / bounded result + mechanism); a "Future work"
line.
**SAY:** In summary: relational structure improves safety-concept probes only as local hard-negative contrast —
approximately 0.06 F1, roughly one third lexical, replicated across two models — while the graph's connectivity
contributes no measurable benefit at any data volume tested. Methodologically, pre-registration and adversarial
verification were each decisive: on two occasions a raw signal was misleading and was identified by a control.
Finally, the relational structure is better understood not as a classifier but as a map of where to extend coverage
— which is the cartographic objective of the HatCat programme. Future work includes contrast-prompted generation, a
near-but-out-of-set rejection test, and a connectivity test that counts independent constraints rather than raw
edges.

---

## Delivery notes
- This is the **formal base** — complete by design. Pare back per slide for time; the spoken-voice cut
  (`TALK_10MIN.md`) and the 8-minute decks remain as alternatives.
- ~10 minutes. If squeezed to 8, drop slides 3 (HatCat) and 9 (geometry control); the talk still stands.
- Numbers stated, precise: 0.06 F1 (local), ~⅓ lexical, ≈0.01 held-out-edge, p = 0.002 placebo, 20-point FP
  reduction; geometry 0.971 vs 0.961 raw, +0.166 / −0.147 mean-centred. Slide 9: the figure carries all geometry
  numbers — cite only 0.971 versus 0.961 aloud; the before/after structure makes the point.
- Q&A: "is 0.06 F1 meaningful?" (it is approximately the residual headroom at a 0.93 ceiling; the operating-point
  false-positive analysis is where deployment value is demonstrated) · "does this generalise beyond SET G?" (a
  single concept family — stated as a limitation) · "why linear probes?" (deployment-realistic; MLP spot-checks
  concur) · "who performed the second-model replication?" (an independent peer replication, credited as such at the
  researcher's request; full provenance is in the shared repository).
