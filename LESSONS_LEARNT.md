# Methods Evolution & Lessons

This appendix documents the methodological evolution of the capstone study (working title: *Knowing the Graph — Does Relational Structure Improve Detection and Steering of Related Concepts in LLMs?*) and the durable lessons that emerged from it. It is distinct from the formal proposal ([`_proposal_extracted.md`](_proposal_extracted.md) / `Capstone_proposal_final.docx`). The aim is to record how the experimental design, its instruments, and its conclusions changed as errors were found and corrected — a record of what was learned methodologically, not a chronological log.

The study's headline result is an informative, pre-registered null: at Gemma-2-9B layer 18, with the probe described below, relational structure provided no measurable, connectivity-tracking benefit to pairwise concept discrimination. The path to that conclusion ran through two earlier apparent positives, both of which dissolved under more rigorous design and greater statistical power. The sections below trace that arc, ordered from the initial framing to the final result, and conclude with cross-cutting reflections and open questions.

---

## Table of contents

- [Substrate selection: from a historical concept list to a graph-defensible set](#substrate)
- [Data quality: label contradictions, parent/child contamination, and an ontological finding](#data-quality)
- [The ceiling effect: probes too good to be informative](#ceiling)
- [Breaking the ceiling: out-of-distribution evaluation and a matched control](#ood)
- [The Menger correlation: a fragile, underpowered positive](#menger)
- [Non-replication at N=15: an honest null](#nonreplication)
- [Methodological recast: test the pair against the pair, and power the per-pair estimate](#recast-power)
- [The pilot gate: a headroom-gated effect at pilot scale](#r3-gate)
- [The powered, pre-registered test: an informative null](#r4-null)
- [Cross-cutting methodological reflections](#reflections)
- [Open methodological questions](#open-questions)

---

## Substrate selection: from a historical concept list to a graph-defensible set {#substrate}

The original capstone proposal centred on SUMO/WordNet direct curation of the `IntentionalPsychologicalProcess` sub-tree. The initial concept list (v3) was a 15-concept set: Deception, Manipulation, Persuasion, Coercion, Intimidation, Negotiation, Gaslighting, Distraction, Propaganda, Concealment, Mediation, Encouragement, Cooperation, Flattery, Instruction. The plan was to extract definitions and relationships directly from SUMO, hand-build the concept graph, train Condition A / B probes, and test the Menger correlation. The v3 list originated in an earlier refinement document (`sumo_refinement.md`) composed as a historical artefact during proposal drafting — a hypothesis about the right concepts, not an analytically load-bearing decision. That distinction was not visible at the time.

**Lesson: a concept list inherited from a historical refinement document is a hypothesis about the right concepts, not load-bearing. Substrate fit must be verified before downstream analysis is anchored on it.** Several v3 concepts (Cooperation, Flattery, Instruction, Mediation, Encouragement) ultimately added no statistical power; recognising this earlier would have saved a round of analysis.

A literature and lexical sweep (see [`lit/influence_lexical_sweep.md`](lit/influence_lexical_sweep.md)) then surfaced that SUMO's coverage of influence/manipulation/safety concepts was thinner than the Menger experiment required. Many v3 concepts existed in SUMO only as leaf nodes with sparse `relationships` declarations, whereas the Menger experiment needs a graph with declared, navigable edges providing k variance across the selection. Two paths existed: hand-author new relationship edges (out of scope for a short capstone), or find a richer substrate. The second path led to a brief survey of alternative substrates (DOLCE, KIF, BFO, CYC, custom hand-authored ontologies), each with disqualifying trade-offs for AI-safety specificity or authoring cost, and ultimately back to HatCat — an existing project that had spent months curating an applied-meld layer over SUMO/WordNet specifically for AI-safety probe training.

**Lesson: check substrate density before locking the experimental design.** A statistically meaningful Menger test needs k variance across the selection; a substrate that is mostly k=0 or k=1 collapses the test before any probes are trained. This is a methodological prerequisite, not an implementation detail. **Lesson: the survey of upper ontologies was not wasted — it sharpened the criteria for what makes a substrate good for a Menger experiment — but survey-then-reuse beats survey-then-build when the budget is tight, and reuse of one's own prior work should be an explicit option in any build/buy/reuse decision.**

HatCat applied melds (`HatCat/melds/applied/*.json`) were adopted read-only as the concept-graph substrate: HatCat upstream supplies ontology, meld substrate (definitions, passages, relations), graph, layer hints, critical-simplex registry, and validation rules; the capstone downstream added Gemma-2-9B activations, A-vs-B probe training, the vertex-disjoint-path metric, and the Menger correlation. Nothing wrote back to HatCat during the project. This also made a **model mismatch** explicit and load-bearing: HatCat production lenses target Gemma-3-4B (residual dim 2560) and Apertus-8B, while the capstone targets Gemma-2-9B (dim 3584), so existing lens weights could not transfer and the capstone trained its own probes from scratch.

**Lesson: model mismatch is a load-bearing risk to surface early in a proposal, not a footnote in the implementation notes.**

A parallel multi-agent analysis of the HatCat substrate (read-only inputs, one output file per agent) produced a pivot dossier covering architecture, meld-inventory triage, concept mapping, and Menger fitness. A subsequent graph analysis of the v3-anchored selection found it empirically thin: 70 of 190 pairs (37%) were zero-edge, the graph split into two regions joined by a single bridge edge, and only 1 of v3's 5 predicted dense pairs survived (Deception–Manipulation at k=4). The proximate cause was proxy substitution — v3 concepts without direct meld candidates (Coercion, Persuasion, Concealment) had been mapped to proxies in different sub-graphs from the central influence cluster. This recommended dropping the isolated and dead-end nodes and crystallised the question of whether v3 was the right concept set at all.

**Lesson: validate substrate fit empirically before committing — predicted dense pairs are not always dense in the actual substrate. Pre-register the edge-counting rule before training any probes, so the analysis cannot be post-hoc tuned.** **Lesson: multi-agent parallel analysis produces clean, citable, reproducible artefacts when each agent has read-only inputs and owns a single output, with no shared mutable state.**

The v3 list was then dropped entirely and a fresh selection re-optimised on a joint criterion: maximise Menger statistical power and AI-safety phenomenology coverage simultaneously, drawn from any candidate in the HIGH-relevance meld shortlist. Two dense substructures emerged that v3 had missed:

- **The `ManipulativeCommunication` 5-clique.** `ManipulativeCommunication.has_part = [Misinformation, Disinformation, Propaganda, Astroturfing, DarkPatterns, PsychologicalExploitation]`. Four has_part children plus the parent form a 5-clique in which every sibling pair sits at vertex-connectivity k=4; adding `PersuasiveCommunication` as MC's parent lifts MC↔Propaganda to k=5. v3 had treated "Persuasion" and "Deception" as umbrella categories rather than naming Misinformation/Disinformation as separable nodes, so this dense substructure was structurally invisible to v3's mapping.
- **The `SycophancyRegister` triangle** (re-mined from a rejected meld). SR plus three has_part children gives a parallel k ∈ {1,2,3} sub-grid — a pure AI-safety addition (Sharma 2023 sycophancy; MASK Ren 2025) absent from v3.

The final selection was **SET G, N=15**. Against the v3-anchored N=12 baseline it improved on every structural and coverage metric (k≥2 fraction 13.6% → 20.0%; mean k 1.15 → 1.41; max k 3 → 5; AI-safety mean score 2.58 → 2.73; Bucket-1 phenomena covered 7/14 → 11/14; no isolated nodes). Two sensitivity tiers are documented (SET C, N=12 dense core, k≥2 fraction 40.9% but narrower coverage; SET B, N=20 with coercion and jailbreak).

**Lesson: do not anchor on a historical concept list; let the substrate's structure suggest the optimal selection. A tractable optimisation criterion (joint statistical power + phenomenology coverage) beats inheriting a prior list.** The structural finding — that the MC 5-clique was always present, hidden behind v3's umbrella terminology — is itself a lesson about substrate-first thinking.

**Cross-refs:** [`pivot/04_menger_fitness.md`](pivot/04_menger_fitness.md), [`pivot/07_aisafety_concept_selection.md`](pivot/07_aisafety_concept_selection.md), [`pivot/menger_analysis.py`](pivot/menger_analysis.py), [`pivot/menger_analysis_v2.py`](pivot/menger_analysis_v2.py), [`pivot/06_synthesis_report.md`](pivot/06_synthesis_report.md).

---

## Data quality: label contradictions, parent/child contamination, and an ontological finding {#data-quality}

The hand-inspection checkpoint before activation extraction surfaced two distinct data-quality bugs and one genuine ontological finding, each of which would otherwise have silently corrupted or muddied the result.

**Part 1 — Condition B label contradiction (dual-labeling).** The pre-registered generator produced boundary passages per related pair and added all of them to *both* concepts' training sets. But each boundary passage exemplifies exactly one concept, so this filed the identical activation vector under two contradictory labels at the very related-concept frontier the experiment measures — an asymmetric corruption that depresses Condition B and could mechanically flip the headline. The fix regenerated the boundary set so each passage is returned tagged with the single concept it exemplifies and assigned to that concept only; re-verification found no passages under two different concepts.

**Part 2 — Condition A parent/child contamination.** Inspection revealed that some passages labelled `ManipulativeCommunication` were plainly gaslighting — i.e. `PsychologicalExploitation`, a child of MC — rather than the umbrella. Rather than fix line by line, a blind label-audit was built (`audit_condition_a.py`): for every passage, a model blind to the assigned label chose the single best-fitting tier-8 concept under a most-specific-wins rule, flagging mismatches. This turned one eyeballed defect into a contamination map. The pattern was structural, not random: sharp leaf concepts audited near-perfectly while umbrella/parent concepts collapsed into their children (overall self-match rose from 142/200, 71%, to 177/200, 88%, after curation). The fix regenerated only the contaminated concepts with a `DIFFERENTIATION` spec steering each toward its distinctive territory and away from sibling territory, while keeping passages non-contrastive (the passage text never names another concept), and preserved the already-clean leaf concepts unchanged. The re-audit served as the acceptance test that closes the loop against recurrence.

**Part 3 — `ManipulativeCommunication` has no clean residual (ontology, not a bug).** Curation cleanly fixed four concepts but made MC worse (14→10/25), drifting toward PsychologicalExploitation. The curation had worked as instructed — MC's new passages are textbook structural manipulation (false-urgency timers, fabricated social proof, dark-pattern defaults, coercive ultimatums) — but the audit still routed them to PsychologicalExploitation because that child's source definition covers exploitation of cognitive biases, which dark patterns do. The finding: `ManipulativeCommunication` as an umbrella has no coherent residual identity distinct from its children; its definition is the union of their mechanisms, and every vivid manipulation example is claimed by some child. This is a property of the concept hierarchy, not a fixable prompt, and MC↔PsychologicalExploitation is exactly the high-k (k=4) pair the experiment is built to study. MC was retained as a coherent dark-pattern/pressure bucket (surface-distinct from PsychologicalExploitation's gaslighting bucket, so a probe can still separate them linguistically) and the entanglement was documented rather than over-tuned away.

**Lessons:**
- **The hand-inspection gate is not ceremony.** It caught a mechanical label-contradiction invisible in the logs, a systematic parent→child contamination invisible without a blind audit, and an ontological limit invisible without inspecting why a fix backfired — none of which would have surfaced until the probe results were already confusing.
- **Turn a single eyeballed defect into a measurement.** One "this looks like gaslighting" became an 8-concept contamination map via a blind, most-specific-wins audit. Build the audit as a re-runnable acceptance test so the fix is verified, not hoped.
- **Decide a label at generation time, not in downstream assembly.** Tag each artifact with its single ground-truth class as it is made; never let later code duplicate it into two classes.
- **Curate the umbrella, preserve the clean leaves.** Regenerating data that already audits clean only adds variance and risk.
- **Know when to stop.** Distinguish "hard because the model represents them similarly" (the finding you want) from "hard because the labels overlap" (a confound to fix). When the overlap is definitional (MC ⊇ its children), stop fixing and document — over-tuning to beat a proxy metric is its own form of p-hacking.
- **Pre-registered code is not a reason to extract activations from data that is visibly wrong.** Fix at the gate, before any GPU spend, and document the amendment with rationale.

**Cross-refs:** [`scripts/generate_condition_b.py`](scripts/generate_condition_b.py), [`scripts/generate_condition_a.py`](scripts/generate_condition_a.py), [`archive/mvv_v1_definition_only/audit/`](archive/mvv_v1_definition_only/audit/), [`TIMELINE.md`](TIMELINE.md) Phase 3 Step 3.2.

---

## The ceiling effect: probes too good to be informative {#ceiling}

The first probe training run (the minimum-viable-version, tiers 4 and 8, both conditions) returned every AUC = 1.000 with near-perfect confusion matrices. This was a measurement failure rather than a success: Condition A was saturated, so Condition B had no room to show any effect, the observed B−A = 0.000 meant "the task is too easy to measure anything" rather than "relational structure does not help," and with no AUC variance there was nothing to correlate against vertex connectivity — the Menger prediction was untestable in this regime.

A difficulty sweep confirmed the ceiling was robust, not a fluke of one split: Condition A stayed ~0.99 even at 10 PCA dimensions with 3 training examples per class, and the hardest pairs (Misinformation vs Disinformation, differing only by intent; ManipulativeCommunication vs PsychologicalExploitation) were also at or near ceiling. Two compounding causes were identified: p ≫ n (3584 features vs ~25 samples/class makes a linear separator near-automatic regardless of content), and, more fundamentally, strong surface/topic signal in the LLM-generated passages — each concept's passages shared vocabulary and a single generation's style, so the model separated them on surface features and the probe never had to use the conceptual boundary Condition B teaches. The chosen path was a surface-controlled regeneration: passages tagged by context, trained on some contexts and tested on held-out contexts (out-of-distribution), to remove the surface-topic crutch and give both Condition B and the Menger prediction a fair test. The complete first attempt was archived ([`archive/mvv_v1_definition_only/`](archive/mvv_v1_definition_only/)).

**Lessons:**
- **A probe AUC of 1.000 is a red flag, not a trophy.** Before believing any probe result, check for a ceiling — run a difficulty sweep (regularization, dimensionality reduction, few-shot) and confirm the headline metric is not saturated. A saturated metric cannot measure the thing the experiment was built to measure.
- **Relatedness of concepts does not guarantee probe difficulty.** SET G was chosen because its concepts are confusable, yet they separated trivially at layer 18. Conceptual subtlety is not the same as representational closeness.
- **LLM-generated probe data leaks surface cues.** Passages generated per concept share topic and style; a probe will exploit that. The honest test forces generalization the surface cue cannot carry — here, out-of-distribution across contexts.
- **Design the difficulty knob in from the start.** An A-vs-B comparison needs A to sit below ceiling by construction (OOD evaluation, harder negatives, fewer dimensions, or a smaller model) — otherwise there is no headroom to detect B's effect.
- **A decision gate before scale-up pays for itself.** Catching the ceiling at the minimum-viable scale, before expanding to larger tiers and the full Menger run, avoided days of wasted compute on more 1.000s.

**Cross-refs:** [`archive/mvv_v1_definition_only/`](archive/mvv_v1_definition_only/), [`scripts/train_probes.py`](scripts/train_probes.py), [`TIMELINE.md`](TIMELINE.md) Phase 3 Step 3.4 / Phase 4.

---

## Breaking the ceiling: out-of-distribution evaluation and a matched control {#ood}

Re-extracting the context-tagged data and running out-of-distribution leave-one-context-out probes (train on 3 contexts, test on the held-out one) broke the ceiling — but only on the right metric:

- **AUC stayed saturated (~0.99)** in both conditions and tiers. As a ranking metric, AUC still ranked probabilities well even when hard-decision errors appeared, so it hid the entire effect. AUC was the wrong headline.
- **Accuracy dropped below ceiling** and became informative (tier 4 A = 0.938, tier 8 A = 0.884, versus 1.000 under the in-distribution split), with confusion matrices that were no longer diagonal.
- **Condition B improved accuracy** (+0.049 at tier 4, +0.028 at tier 8), and the errors concentrated on the high-k pairs (ManipulativeCommunication↔PsychologicalExploitation, Misinformation↔Disinformation, ManipulativeCommunication↔Disinformation) — connectivity tracking confusability, the Menger signal becoming visible once there was per-pair variance to measure.

Because Condition B had more passages than A, the gain could have been relational content or simply more data. A matched control was built — A's exact size with a small number of boundary passages swapped in per context — and compared to A over 30 random draws. At this scale matched-B beat A at both tiers (+0.038 ± 0.012 at tier 4, 30/30 seeds; +0.021 ± 0.013 at tier 8, 29/30), and at tier 8 matched-B ≈ full-B, suggesting the content rather than the volume did the work. This was a positive result at the minimum-viable scale. It did not survive replication on fresh N=15 data (see [non-replication](#nonreplication)), where matched-B − A fell to −0.011 (tier 4) and +0.004 (tier 8) — the advantage was dataset-specific, not stable.

**Lessons:**
- **AUC saturates on near-separable linear-probe tasks — use accuracy, macro-F1, or the confusion matrix as the headline.** A metric at ceiling cannot measure the effect, and it nearly buried a real result here. Check that the headline metric has headroom before concluding "no effect."
- **Out-of-distribution evaluation is how a probe is forced off surface features.** Training and testing on disjoint contexts turned an uninformative in-distribution ceiling into a measurable task — the same data, a harder and fairer question.
- **A measured improvement on unequal data is not yet a finding.** Control for the obvious confound (here, training-set size) before attributing the gain to the mechanism; holding size constant and repeating over many draws is what turns a suggestive average into a defensible claim.

**Cross-refs:** [`scripts/train_probes.py`](scripts/train_probes.py) (OOD split), `results/results.json`, `results/matched_control.json`, [`TIMELINE.md`](TIMELINE.md) Phase 3 Step 3.4 / Phase 4.

---

## The Menger correlation: a fragile, underpowered positive {#menger}

The sharp form of the project's claim is Menger-specific: relational data should help most on densely-connected concept pairs. Tested at the N=8 minimum-viable scale as per-pair OOD confusion improvement (A vs matched-B, averaged over 20 seeds) against vertex connectivity k, the direction was positive but not significant (Pearson r ≈ +0.35, p ≈ 0.07), with a clean pre-registered categorical split (k≥2 pairs improving, k=1 pairs roughly flat) and agreement between the two operationalizations of k. With only 28 pairs and small effect sizes, this was suggestive but inconclusive — neither a finding nor a null — and it was the explicit motivation for expanding to N=15 (105 pairs) for power.

A dedicated binary probe per pair (replacing scavenged multi-class off-diagonals) lifted Pearson to nominal significance (r ≈ +0.39, p ≈ 0.043) and sharpened the categorical split, but Spearman stayed non-significant and the top pair was an outlier, so the Pearson significance was outlier-driven and fragile; the robust statement remained the k≥2-vs-k=1 categorical contrast. At N=15 (105 pairs) this reversed entirely (see [non-replication](#nonreplication)): the N=28 positive was underpowered noise.

**Lessons:**
- **A correlation needs enough units to be testable.** For the Menger test the number of pairs is the sample size, and it must be planned for the test, not the probe; 8 concepts / 28 pairs is underpowered for a moderate effect.
- **Report direction, effect, and power honestly.** "r ≈ 0.35, p ≈ 0.07, n = 28" is a suggestive trend, not a result — and saying so is more credible than over-claiming.
- **Sensitivity-check the operationalization.** Two definitions of k agreeing guards against a conclusion that depends on an arbitrary modeling choice.
- **Switching metrics until p < 0.05 is p-hacking unless all metrics are reported and the choice is justified a priori.** Both the multi-class and binary metrics were reported, binary was defended on signal-quality grounds rather than significance, and the non-significant Spearman was kept in view so the fragile Pearson was not oversold.

**Cross-refs:** [`scripts/menger_correlation.py`](scripts/menger_correlation.py), [`scripts/menger_pairwise.py`](scripts/menger_pairwise.py), `results/menger_correlation.json`, `results/menger_pairwise.json`, [`pivot/menger_analysis_v2.py`](pivot/menger_analysis_v2.py).

---

## Non-replication at N=15: an honest null {#nonreplication}

Expanding to the full SET G N=15 — done specifically for statistical power — overturned both N=8 findings. All 15 concepts were regenerated fresh (context-tagged, re-audited), extracted, and re-run at tiers 4/8/12/15 and across all 105 pairs.

**Relational > volume (matched control) did not replicate.** The N=8 result had been matched-B − A = +0.038 (tier 4) and +0.021 (tier 8). On fresh 15-concept data the size-matched effect was gone:

| tier | A | full-B | matched-B − A | seeds + |
|---|---|---|---|---|
| 4 | 0.991 | 0.992 | −0.011 | 0/30 |
| 8 | 0.902 | 0.944 | +0.004 | 15/30 |
| 12 | 0.887 | 0.923 | +0.012 | 26/30 |
| 15 | 0.907 | 0.926 | −0.000 | 12/30 |

full-B still beat A (more data helps), but size-matched the relational effect vanished. The earlier positive was an artifact of one particular generated dataset.

**The Menger correlation was not supported, and slightly reversed.** With 105 pairs (vs 28): Pearson r = −0.08 (p = 0.41), Spearman r = −0.20 (p = 0.045, significant but negative); k≥2 pairs improved −0.000 (n=21) and k=1 pairs +0.003 (n=84), the opposite of the prediction. The N=28 +0.39 Pearson was underpowered noise.

The conclusion at this stage was that there was no robust evidence that relational structure (as then operationalised) improved probe discrimination of related concepts, and no Menger relationship; Condition B helped only by adding data volume. This was the correct outcome rather than a failure: the matched control, multi-seed robustness, and above all the expansion for power caught a false positive before write-up.

**Lessons:**
- **Underpowered positives do not replicate.** 8 concepts / 28 pairs with a small effect was a coin-flip dressed as significance. Plan for power and replicate on fresh data before believing an effect.
- **"Robust across 30 seeds" is not "robust across datasets."** The matched-B seed-robustness resampled only within one generated dataset; it never tested whether a fresh generation reproduces the effect. Seed-stability is not dataset-stability — the subtle trap that made the N=8 result look solid.
- **`full-B > A` is the volume confound, not the hypothesis.** Always headline the size-matched comparison; the unmatched gain says nothing about mechanism.
- **A rigorous null is a result.** The pipeline worked precisely because it could return "no," and reporting it honestly — including how the apparent effect dissolved — is the credible outcome.

This null was later reinterpreted (see [recast](#recast-power)) as also testing the wrong question and being underpowered at the per-pair level — not as settled evidence against the hypothesis.

**Cross-refs:** `results/results.json`, `results/matched_control.json`, `results/menger_pairwise.json`, [`scripts/train_probes.py`](scripts/train_probes.py), [`scripts/menger_pairwise.py`](scripts/menger_pairwise.py).

---

## Methodological recast: test the pair against the pair, and power the per-pair estimate {#recast-power}

A mentor review of the first iteration flagged major methodological issues. Two distinct problems surfaced, both addressed in the second-iteration instruments (full plan in [`ITERATION2_TIMELINE.md`](ITERATION2_TIMELINE.md)).

**Part 1 — the validity error: the relational signal was never tested against the pair it is about.** The first iteration claimed to ask "does A-vs-B relational data help distinguish A from B?" but tested something else on both ends. The test target was wrong: the probe used a multi-class, leave-one-*context*-out test, so A-vs-B boundary data was judged by overall classification on a new context rather than by A-vs-B discrimination. The training content was also wrong: the matched-B control sampled each concept's entire boundary pool (A-vs-anything), not the A-vs-B edge specifically. The net effect was that the first-iteration null answered the wrong question. The recast made the pair the unit and matched on both ends — a binary A-vs-B probe, trained with that pair's pair-specific boundary swapped in (volume-matched against def-only), tested only on held-out-context A and B definitions, with the improvement-vs-k correlation reported raw and partialling out baseline separability `acc_def` (the headroom↔k confound).

**Lesson: test the signal against the thing it is supposed to explain.** If the claim is "A-vs-B data helps tell A from B," both the training content and the evaluation must be about the A-vs-B pair — not A-vs-everything content scored by whole-context classification. A null about the wrong question is not evidence.

**Part 2 — the per-pair test set was too small to be statistically viable.** Even with the right test, each pair was scored on only 56 held-out decisions (7 A + 7 B definitions × 4 leave-one-context-out folds). A power analysis grounded in the real SET G k-distribution made the cost concrete: a single pair needed an improvement ≥ ~0.10 to be individually significant, so first-iteration-scale effects of 0.01–0.03 were invisible per pair; the Menger trend had only ~68% power at a realistic effect; and measurement noise attenuated the correlation, so a genuinely real trend would show as observed r ≈ +0.24. That attenuation matched the first-iteration symptom exactly — r = +0.39 at N=28 then −0.08 at N=105 — indicating a noise-dominated estimate rather than the truth flipping. Raising to 14–21 definitions per context (n_test 112–168) lifted trend power to ~89–98% and roughly halved the per-pair minimum detectable effect. This was distinct from the pair-count problem the N=8→N=15 expansion fixed: that enlarged the number of units in the correlation, whereas this concerned the precision of each unit, which had never been addressed.

The deepest trap here was that seed-stability is not test-set sufficiency. The first iteration's "robust across 30 seeds" resampled only the training draw and held the test set fixed, so it was structurally blind to test-set sampling noise. The honest empirical measure is a test-point bootstrap that resamples the held-out definitions, now emitted per pair and fed back into the power calculator.

**Lessons:**
- **Power the per-pair estimate, not just the number of units.** A correlation over 105 pairs is still underpowered if each pair's value carries ±0.05 noise and the effect is 0.02; measurement error attenuates the correlation toward zero. Compute the per-pair minimum detectable effect and the attenuated observed-r before spending compute.
- **Seed-stability ≠ test-set sufficiency.** Resampling seeds (training draws) cannot reveal test-set sampling noise; only resampling the test points — or enlarging the test set — can. Never read seed-robustness as statistical adequacy. (This is the same trap as the [non-replication](#nonreplication), one level deeper: there, seed-stability missed dataset-stability; here, it missed test-set sampling.)
- **Size the test set with a power calculation, not after another null.** Pick definitions-per-context for a target minimum detectable effect before the next run, refined with the pilot's bootstrap noise.
- **More information requires more independent draws, not more resamples of the same points.** Bootstrapping and seeding cannot manufacture information the sample does not contain; the fix is a larger per-pair test set or a pooled (mixed-effects) estimator over all decisions.

**Part 3 — the boundary passages must be non-contrastive too.** Generating the pilot boundary surfaced a third surface-feature trap. The first-iteration boundary prompt instructed the generator to "explicitly state why it is that concept and not the other," so 98% of pilot passages ended with a literal label (e.g. "This is misinformation, not disinformation, because…"). The blind exemplifies-audit returned a clean 100% — which was itself the warning sign, because the label was in the text. Since the pairwise test is evaluated on held-out definitions (which never name concepts), a probe trained on label-bearing boundary could exploit a token the test set cannot carry — a surface-feature confound. Programmatic stripping was unreliable (it gutted 21% of passages with 15% residual leak), so the generator was made non-contrastive: depict the distinguishing feature through the scenario, never name or label the concept (the rule already enforced on Condition A). Re-auditing the regenerated pilot gave 99% exemplifies-match at 0% naming-leak, and the audit now gates on both correct tag and no naming.

**Lesson: every contrastive cue is a surface feature.** The no-naming discipline is not only for the definition-only condition — any training data whose text names or labels the target lets a probe shortcut the representation under test. Apply it everywhere the probe trains, and make the data-quality audit check for leakage as well as correct labels: a 100% label-audit can be a red flag that the label leaked into the text.

**Cross-refs:** [`ITERATION2_TIMELINE.md`](ITERATION2_TIMELINE.md), [`scripts/pairwise_relational.py`](scripts/pairwise_relational.py), [`scripts/power_analysis.py`](scripts/power_analysis.py), [`scripts/generate_condition_b.py`](scripts/generate_condition_b.py), [`audit/audit_boundary.py`](audit/audit_boundary.py).

---

## The pilot gate: a headroom-gated effect at pilot scale {#r3-gate}

The corrected pairwise analysis ([`scripts/pairwise_relational.py`](scripts/pairwise_relational.py)) was run on the 12-pair pilot using the iteration-2 boundary activations. To force the headroom the first iteration never had, the OOD regime was hardened: train on 1 context, test on the held-out A/B definitions; 20 seeds; 3 pair-specific boundary passages swapped in, volume-matched against def-only.

- **Headroom was achieved.** Mean `acc_def` 0.918, with 6/12 pairs below 0.95 — for the first time, room for relational data to move the needle (first-iteration pairs ceilinged ~0.99).
- **The effect tracked k on rank and survived the confound control, but only on Spearman.** Improvement-vs-k: Spearman r = 0.58 (p = 0.049 raw); r = 0.64 (p = 0.035 partialling out `acc_def`). The partial was the pre-specified headline (it guards the headroom↔k confound) and was stronger than the raw, so the trend was not merely "hard pairs have more room." Pearson r = 0.36 raw / 0.31 partial, both non-significant — no linear signal at this n.
- **Direction was sensible.** Mean improvement k≤1 = −0.017 (4 pairs), k≥2 = +0.004 (8 pairs). The cleanest positive was SycophancyRegister↔UnwarrantedPraise (k=3): +0.074 at `acc_def` 0.865, ~2.5× its test-point bootstrap SD. The largest negative, ManipulativeCommunication↔PersuasiveCommunication (k=2): −0.061, was ceilinged (`acc_def` 0.978), so swapping definitions for boundary merely removed def-signal it could not replace — exactly as theory predicts for a no-headroom pair.

The result was borderline: significant on the rank test but not the linear one; n = 12; and leverage-sensitive, since one influential pair could be carrying the rank signal (most k≥3 pairs live in the ManipulativeCommunication 5-clique). The gate question — does the corrected, pair-matched test produce a measurable, sensible relational effect on pairs that have headroom? — was answered with a qualified yes: headroom existed, the effect was directionally sensible, tracked k, and survived the `acc_def` confound control. What was missing was power, not signal; the two things the first iteration lacked (headroom and a pair-matched test) were now in place and behaving as the hypothesis predicts. The honest resolver for a borderline, underpowered pilot is a powered run, not further instrument-tuning, and the power analysis (grounded in the pilot's empirical noise and the real 105-pair k-distribution) indicated the full run would be well-powered even at the current dose (linear-trend power 0.99 at 7 defs/context, ~1.0 at 14).

To prevent the scale-up from inheriting the pilot's tuning, the design was pre-registered before scaling: the OOD regime was frozen (`train_contexts=1`, `n_bnd=3`, `n_seeds=20`, volume-matched, test on held-out A/B definitions only); the primary headline was declared as partial Spearman controlling `acc_def` (with raw, Pearson, and the k≤1-vs-k≥2 contrast as secondary); the dose was set to 14 defs/context for Pearson margin and leverage robustness; and a leverage guard (leave-one-out on influential pairs, plus the categorical k≤1 vs k≥2 contrast as a balanced fallback) was specified. The OOD regime had been tuned on the pilot to obtain headroom — defensible because that tuning targets the precondition (headroom), not the hypothesis (the k-correlation) — but it had to be frozen before the powered run, not re-tuned after seeing its results.

**Lesson: borderline at pilot scale is a power signal, not a stop signal.** Once the preconditions (headroom plus a valid, pair-matched test) are in place and the effect is directionally sensible and confound-robust, the honest next move is the powered run, not another round of instrument-tuning — but freeze the regime first, or the scale-up silently inherits the pilot's tuning and the result stops being pre-registered.

**Cross-refs:** [`ITERATION2_TIMELINE.md`](ITERATION2_TIMELINE.md), [`results/pairwise_relational.json`](results/pairwise_relational.json), [`results/power_analysis.json`](results/power_analysis.json), [`scripts/pairwise_relational.py`](scripts/pairwise_relational.py), [`scripts/power_analysis.py`](scripts/power_analysis.py).

---

## The powered, pre-registered test: an informative null {#r4-null}

The corrected, pair-matched experiment was run at full scale exactly as pre-registered ([`R4_PREREGISTRATION.md`](R4_PREREGISTRATION.md)): all 105 SET G pairs, 14 defs/context (n_test = 112), the frozen regime (`train_contexts=1, n_bnd=3, n_seeds=20, n_boot=1000`), primary = partial Spearman of improvement-vs-k controlling `acc_def` (output [`results/pairwise_relational.json`](results/pairwise_relational.json)).

**The result was a clean null.** Primary partial Spearman (controlling `acc_def`): r = −0.125, p = 0.20 — negative and non-significant (raw Pearson +0.068, p = 0.49; raw Spearman −0.027, p = 0.78). Mean improvement k≤1 = +0.0017, k≥2 = +0.0034, both within noise of zero; overall median improvement 0.000. The pre-registered verdict was NULL / not supported: the Menger prediction — that A-vs-B relational data helps an A-vs-B probe more for more-connected pairs — was not supported by the corrected, powered test.

This was an informative null, not an underpowered one. The per-pair estimates were now precise (median test-point bootstrap SD = 0.0046 at n_test = 112, versus 0.018 at 56 in the pilot), and the power analysis put trend power at ~1.0 for the planned effect at 105 pairs — so the test could have seen a real effect of the hypothesised size, and there was none. The null was also robust to ceiling artefacts: restricting to the 29 pairs with headroom (`acc_def` < 0.95) gave partial Spearman = −0.20 (p = 0.30).

Decisively, the pilot's own 12 pairs collapsed under the powered test. Re-measured at 14/context, the exact 12 stratified pairs that had produced the borderline-positive pilot (partial Spearman +0.637, p = 0.035 at 7/context) now gave partial Spearman −0.043, p = 0.90. Nothing about the pairs changed except that the test set doubled and its sampling noise halved — and the apparent signal evaporated. The pilot positive was per-pair sampling noise, precisely the law-of-large-numbers gap identified in the [recast](#recast-power) Part 2: with n_test = 56 and true per-pair effects of ~0.002–0.03, each improvement is noise-dominated, and a rank correlation over a dozen such points can land at +0.64 by chance. This was the first-iteration trap caught one level deeper — and this time the pre-registered, powered replication caught it instead of a headline surviving on it. The data did contain scattered real per-pair effects (7 pairs at z ≥ +2, 11 at z ≤ −2), but they did not track k (the largest positives were mostly k=1), so relational boundary data nudges individual pairs both ways without systematically helping, and the help it gives is unrelated to graph connectivity.

With both the validity and power errors fixed, relational structure provided no measurable, k-tracking benefit to pairwise concept discrimination at Gemma-2-9B layer 18 with this probe. The recast turned an underpowered, wrong-target null (first iteration) and a borderline noise-positive (the pilot) into a valid, powered, confound-controlled answer — which is a null, and a real result rather than a failure of the experiment.

**Lesson: a small-n positive that lives only in the rank test is what sampling noise looks like — treat it as a hypothesis to replicate at power, never as a finding.** Pre-registration plus a precision-improved, powered replication is what separated the mirage from a signal here; the null can be reported with the same confidence a positive would have earned, because the design earned it.

**Cross-refs:** [`R4_PREREGISTRATION.md`](R4_PREREGISTRATION.md), [`results/pairwise_relational.json`](results/pairwise_relational.json), [`R4_results_explorer.ipynb`](R4_results_explorer.ipynb), [`ITERATION2_TIMELINE.md`](ITERATION2_TIMELINE.md). Builds on the [recast](#recast-power) and the [pilot gate](#r3-gate).

---

## Cross-cutting methodological reflections {#reflections}

These are durable takeaways that do not fit any single decision point.

**The honest-null iteration arc.** The study's central methodological lesson is the arc itself: an underpowered, wrong-target null in iteration 1; a borderline noise-positive at pilot scale; and a valid, powered, confound-controlled null at full scale. At each stage the apparent signal that did not survive a more rigorous design was discarded rather than defended. The instruments — matched controls, out-of-distribution evaluation, blind data-quality audits, per-pair power analysis, test-point bootstraps, and pre-registration — earned their place by repeatedly catching false positives before they became headlines. A rigorous null reported with the confidence its design earned is the credible outcome.

**Pre-registered edge rules made the analysis reproducible.** The edge rules (direct candidate-term reference; shared parent; pack-layer projection) were codified before any probes were trained and implemented in the Menger analysis scripts. Pre-registration matters because the Menger test correlates per-pair Δ with k, and any post-hoc tuning of the edge rule would look like p-hacking.

**The leverage problem is real.** 10 of 11 k≥3 pairs in SET G come from one 5-clique, so the headline regression depends heavily on the probe quality of those five nodes. Mitigation — leave-one-out plus the categorical k=1 vs k≥2 contrast (84 vs 21 pairs) as a balanced fallback — must be planned in the analysis plan up front, not after the result.

**"AI-safety relevant" is not "graph-bridging."** During the SET G search, attempts to use multimodal-safety siblings (Deepfake, CounterfeitGeneration, ExploitativeImagery) as a parallel dense sub-graph failed (32–36% k=0 pairs) because only `Deepfake.related = Misinformation` bridged into the influence cluster. Rich AI-safety content does not guarantee that a concept's declared relationships bridge into the other concepts under study — check both, and check empirically.

**Separate "is the concept in the graph" from "is the probe trainable on it."** Six of 15 SET G nodes have fewer than 20 training examples in their source meld; the graph is fine but the probes are lower-confidence. The augmentation rule (borrow from parents and has_part siblings) is pre-registered, and the lowest-data nodes are treated explicitly as graph-only / low-confidence diagnostics. These are distinct constraints with distinct mitigations.

**Governance load is real, and rejected is not wrong.** Five of 15 SET G nodes come from rejected melds, re-mineable because the rejection reasons were ontology-hygiene rather than topical irrelevance, but flagged explicitly in the proposal. Check the rejection reasons before excluding a candidate.

**Multi-agent parallel analysis works with read-only inputs and clear separation of concerns.** The pivot dossier produced clean, citable, reproducible artefacts because each agent owned one file and could not modify another's outputs. Orchestration with read-only inputs is a force multiplier for analytical work; orchestration with shared mutable state usually is not.

---

## Open methodological questions {#open-questions}

From [`pivot/06_synthesis_report.md`](pivot/06_synthesis_report.md) §7 and [`pivot/04_menger_fitness.md`](pivot/04_menger_fitness.md) §8:

- **Primary tier (resolved):** locked at SET G N=15, with SET C (N=12 dense core) and SET B (N=20 balanced) documented as sensitivity tiers.
- **Leverage robustness (active):** 10 of 11 k≥3 pairs come from the `ManipulativeCommunication` 5-clique. Plan: leave-one-out sensitivity on each MC-clique node; categorical k=1 vs k≥2 (84 vs 21 pairs) as the fallback headline.
- **Isolated concepts (deferred):** Concealment, Encouragement, Mediation, and MaskedStates were dropped from the primary set; they can be re-mined from rejected/pending melds in post-project work if the governance load is acceptable.
- **Single A↔B bridge (deferred):** the Manipulation–Intimidation bridge in SET B is accepted as a substrate fact for the SET G primary; it could be repaired by commissioning a Coercion↔Manipulation bridge meld in post-project work.
- **MVV Tier 4 composition (resolved):** set to (ManipulativeCommunication, PersuasiveCommunication, Propaganda, Misinformation), all in the MC 5-clique.
- **HatCat contribution-back (deferred):** default is to contribute a Menger-fitness-analysis document to HatCat post-project; if probe results warrant, commission repair melds. The full contribution-back decision is deferred to post-project.

---

*Reproducibility footnote: activation extraction ran on fresh cloud GPU instances. Use an isolated virtualenv rather than the system Python (apt-installed scientific packages shadow pip and pin incompatible ABIs), do not carry stale dependency pins across instances, and tag every reproduction step by machine (laptop vs instance) to avoid running commands on the wrong host. See [`TIMELINE.md`](TIMELINE.md) "Environment gotchas" and [`scripts/extract_activations.py`](scripts/extract_activations.py) for details.*
