# Knowing the Graph — Capstone

> 🗺️ **New here / lost in the iterations? Start with [`MAP.md`](MAP.md)** — the index of every artifact by iteration & owner, with the iteration↔Path key and current state.

> **Status: COMPLETE — a bounded result across four pre-registered iterations.**
> Does relational structure improve linear-probe detection of related AI-safety concepts? The answer, replicated across two models (Gemma-2-9B and, by independent peer replication, Gemma-4-E4B):
> - **Relations help — but only as local hard-negative contrast.** Training a concept's probe against its directly-related siblings improves discrimination by ~**+0.06 F1**; roughly **one third** of that is shared vocabulary, not deep structure.
> - **The graph's connectivity adds nothing measurable on this graph.** The alternate-path / Menger test (held-out-edge) sits at ~**+0.01**, and a pre-registered **10× within-model scaling sweep** does not raise it (top volume +0.005, 95% CI [−0.005, +0.014]; net of vocabulary −0.006). That rules out a benefit much above +0.015 F1, not one near the minimum detectable effect (0.014). The graph is small (15 concepts, 26 edges, ≤4 alternate paths per edge), so the null is scoped to it.
> - **Deployment boundary:** each negative-selection scheme seals only the boundary face it trains against; on legitimate influence (negotiation, advertising, lobbying) no scheme helps — FPR ≈0.23 on held-out contexts ([`NEAR_OOS_RESULT_NOTE.md`](NEAR_OOS_RESULT_NOTE.md)).
> - **Account (post hoc):** independent-constraint boundary coverage — negatives place boundary facets; path counts matter only insofar as they count *independent* constraints.
>
> The arc: iterations 1–2 (powered, pre-registered null on connectivity) → iteration 3 / Path 2 (relations-as-hard-negatives, bounded positive) → iteration 4 (null on alternate-path scaling under the locked rule) → near-OOS rejection test. The honest nulls are the point. **Start at [`MAP.md`](MAP.md); the plain-English explainer is [`iteration4_scaling/PRIMER.md`](iteration4_scaling/PRIMER.md); the paper is [`paper/main.tex`](paper/main.tex) (build: [`paper/README.md`](paper/README.md)).**

> **Reproduce:** source-text data is committed (`data/*.json`); only the GPU activation extract + sweep need re-running. Canonical path for the headline (iteration 4): [`iteration4_scaling/RUNBOOK.md`](iteration4_scaling/RUNBOOK.md) STEP 1–4 (extraction recipe in [`R4_LAMBDA_RECIPE.md`](R4_LAMBDA_RECIPE.md)). Environment: [`requirements.txt`](requirements.txt). Earlier iterations: [`scripts/README.md`](scripts/README.md).

## Repository contents

Key artifacts at the repository root:

| Path | What it is |
|---|---|
| [`LESSONS_LEARNT.md`](LESSONS_LEARNT.md) | Methods evolution and lessons: ceiling → OOD fix → apparent N=8 effect → N=15 non-replication. |
| [`scripts/`](scripts/) | The probing pipeline (generation, extraction, probing, Menger connectivity). See [`scripts/README.md`](scripts/README.md). |
| [`data/`](data/) · [`audit/`](audit/) · [`pivot/`](pivot/) | Context-tagged passages · contamination audit · SET G concepts + Menger graph. |
| [`TIMELINE.md`](TIMELINE.md) | Design and timeline. |
| [`archive/`](archive/) | Archived: iteration-1 conclusions, the v1 ceiling sub-attempt, the v3 concept list. |

**Quarantined (iteration-1 conclusions):** [`archive/iteration1_relational_probing/WRITEUP.md`](archive/iteration1_relational_probing/WRITEUP.md) and [`archive/iteration1_relational_probing/results/`](archive/iteration1_relational_probing/results/). Honest-null headline, for reference: once data volume was matched, relational data gave no robust probe improvement, and per-pair gain did not track connectivity; an apparent N=8 positive did not replicate at N=15.

**Future directions:** causal/steering instead of detection · representational-geometry (diff-of-means directions, RSA vs the graph with a text-similarity baseline) · Gemma Scope SAE features · human-written (not LLM-generated) data. See `LESSONS_LEARNT.md` and the archived `WRITEUP.md` §4.

---

*Below: the original project reference (research question, substrate, resources). The "Plan" section is the historical forward plan; the iteration-1 outcome is in the archived [`WRITEUP.md`](archive/iteration1_relational_probing/WRITEUP.md).*

## Research Question
Does training concept probes with explicit relational structure (drawn from HatCat applied melds layered on the SUMO/WordNet-grounded concept pack `org.hatcat/sumo-wordnet-v4`) improve discrimination between semantically related safety concepts compared to definition-only probes, and is the per-pair effect predictable from vertex-connectivity in the concept graph?

## Active artifacts
- **Proposal:** [`_proposal_extracted.md`](_proposal_extracted.md) is the canonical version (a Word version can be regenerated via pandoc if needed).
- **Timeline:** [`TIMELINE.md`](TIMELINE.md) — execution plan with day-by-day steps, locked decisions, and decision gates.
- **Pivot dossier:** [`pivot/`](pivot/) — multi-agent substrate analysis (Agents 1–7). Start with [`pivot/06_synthesis_report.md`](pivot/06_synthesis_report.md) for the pivot synthesis and [`pivot/07_aisafety_concept_selection.md`](pivot/07_aisafety_concept_selection.md) for the SET G specification.
- **Lessons learnt / pivot history:** [`LESSONS_LEARNT.md`](LESSONS_LEARNT.md) — methods-evolution notes: the SUMO→HatCat pivot, the v3→SET G re-selection, and the methodological lessons.

(The TARA participant project guide and earlier v2 administrative artifacts are course-administration documents and are intentionally not included in this public research release.)

## Plan
- **Week 12 (by Sat 30 May):** Lock the SET G N=15 concept set (per `pivot/07_aisafety_concept_selection.md`: ManipulativeCommunication, PersuasiveCommunication, Propaganda, Misinformation, Disinformation, PsychologicalExploitation, SycophancyRegister, ExcessiveAgreement, UnwarrantedPraise, Misdirection, Threaten, UlteriorMotiveDetection, SpecificationGamingProcess, StrategicDeceptionPlanningProcess, Deepfake); nested 4/8/12/15 tiers with SET C (N=12 dense core) and SET B (N=20 balanced) as sensitivity tiers; Condition A and Condition B training data sourced from HatCat applied + re-mineable rejected melds; model + activation-extraction pipeline set up; activations cached.
- **Week 13 (by Sat 6 Jun):** Train and evaluate Condition A and Condition B probes at every tier; confusion matrices, per-pair AUC, relational discrimination scores; paired-bootstrap comparison; vertex-connectivity correlation (continuous regression + categorical k=1 vs k≥2 contrast + leave-one-out sensitivity on the `ManipulativeCommunication` 5-clique). Begin steering stretch if on track.
- **Week 14 (by Fri 13 Jun):** Complete analysis; optional steering completions; 4–6 page write-up; reproducible notebook; presentation slides.

## Substrate

This capstone consumes **HatCat applied melds** as its concept-graph substrate. Each applied meld (e.g. `HatCat/melds/applied/persuasive-communications.json`) bundles into one JSON: concept definitions, `relationships.{related, has_part, antonyms}`, parent/child links, `training_hints.{positive_examples, negative_examples}`, `safety_tags`, `simplex_mapping`, and `layer_hint` — exactly the artifacts this experiment needs to build Condition A and Condition B training corpora and to compute the Menger vertex-connectivity graph.

Primary substrate: `persuasive-communications.json` (6 SET G nodes including the ManipulativeCommunication 5-clique). Supplements: `speech-acts-core.json` (`Threaten`), `assistant-user-modeling.json` (`UlteriorMotiveDetection`), `cog-architecture-core-packH.json` (`SpecificationGamingProcess`), `multimodal-safety.json` (`Deepfake`). Re-mineable rejected melds: `register-stance.json` (3 nodes), `rhetorical-markers.json` (`Misdirection`), `cog-architecture-core-packF.json` (`StrategicDeceptionPlanningProcess`). Concept-pack snapshot: `org.hatcat/sumo-wordnet-v4@7.7.1`.

SET G covers 11 of 14 Bucket-1 AI-safety phenomena: deception, sycophancy (with internal triangle granularity), alignment faking, specification gaming, propaganda/misinformation/disinformation as separable nodes, gaslighting, deepfakes, threat-as-blackmail, asymmetric assistant→user influence, rhetorical misdirection.

**Model mismatch note:** HatCat production lenses target Gemma-3-4B (residual dim 2560) and Apertus-8B; this capstone targets Gemma-2-9B (dim 3584) and therefore trains its own probes — existing HatCat lens weights do not transfer.

## Resources
- ARENA exercises as reference implementations
- HatCat codebase (https://github.com/p0ss/HatCat) — applied-meld substrate; consumed read-only. The self-prompting and yin-yang negative sampling are the mechanisms this experiment isolates and verifies.
- HatCat concept pack `sumo-wordnet-v4@7.7.1` (https://github.com/p0ss/HatCat/tree/main/concept_packs/sumo-wordnet-v4) — pinned for reproducibility
- SUMO/WordNet (open) — upstream of the HatCat concept pack
- TA guidance and peer feedback
- Compute credits from TARA (Gemma 2 9B on Lambda Labs A100 40GB; $400 credit; expected burn 10–20 GPU-hours per `TIMELINE.md`)
