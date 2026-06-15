# 06 — Synthesis Report: The HatCat Substrate Pivot

This report synthesises the substrate analysis across 01–04 and the source documents.

---

## 1. Executive summary

The capstone pivots from **curating SUMO/WordNet concepts directly** (the v3 plan, executed via Phase 0 SUMO lookups) to **consuming existing HatCat applied melds as the concept-graph substrate**. Each applied meld bundles definitions, training-example sets, declared `relationships`, parent/child links, safety tags, and simplex mappings into one JSON file — exactly the artifacts the Menger experiment needs. The analysis inspected the HatCat repository, inventoried 312 meld entries, selected a 20-concept set with proxy substitutions, and computed vertex-disjoint path counts across all 190 pairs.

The findings: the meld substrate confirms the **direction** of v3's Menger prediction but is **sparser than v3 anticipated**. Only one of v3's five predicted dense pairs (Deception–Manipulation at k=4) survives; the other four collapse to k=1. The graph is bimodal at the floor (70 zero-edge pairs, 101 single-path pairs, 17 at k=2, one each at k=3 and k=4) and has two regions joined by a single bridge edge (Manipulation–Intimidation). The connectivity analysis (04 §5) recommends **N=12** as the primary tier; N=15 and N=20 are retained as sensitivity tiers.

Several decisions remain for the reviewer (see §7): the primary tier (N=12 vs N=15/20), how to handle the k=3/k=4 leverage problem, whether to drop or re-mine four isolated concepts, whether the single A↔B bridge is a structural-substrate fact or an artefact to repair, whether MaskedStates can be salvaged, and the two relationship-level decisions on consume-vs-commission and contribute-back.

## 2. The substrate pivot in one paragraph

Before the pivot, Phase 0 (`TIMELINE.md` lines 82–225) was scoped as "open the SUMO browser, find each concept's parent class, hand-build the edge list, simulate adding bridging concepts via `node_connectivity`". After the pivot, the substrate is **HatCat's `melds/applied/*.json` corpus** layered on the pinned concept pack `org.hatcat/sumo-wordnet-v4@7.7.1` (01 §3). The capstone reads from this substrate; it does not author new melds, does not modify existing ones, and does not write lens weights back to HatCat. The pivot is "use HatCat upstream", not "extend SUMO". HatCat provides ontology, meld substrate (definitions + passages + relations), graph structure, layer hints, the critical-simplex registry, and the validation rules; the capstone adds Gemma-2-9B activations, A-vs-B probe training, the vertex-disjoint-path metric, and the Menger correlation (01 §8). Nothing writes back.

## 3. The working concept set

**N=12 (primary, per 04 §5):**

| # | Concept | Meld source | Substitution note |
|---|---|---|---|
| 1 | Deception | persuasive-communications.json | `ManipulativeCommunication` proxy; CRITICAL via DeceptionDetector |
| 2 | Manipulation | cognitiveprocess-melds.json | Direct; CRITICAL via DeceptionDetector |
| 3 | Persuasion | persuasive-communications.json | `PersuasiveCommunication` proxy |
| 4 | Coercion | contract-negotiation-signals.json | `CoerciveEscalationCue` proxy |
| 5 | Intimidation | speech-acts-core.json | `Threaten` proxy (aliases include "Intimidation") |
| 6 | Negotiation | contract-negotiation-signals.json | `ContractNegotiationField` proxy |
| 7 | Gaslighting | persuasive-communications.json | `PsychologicalExploitation` (positive-example surrogate; weakest fit) |
| 8 | Distraction | rejected/rhetorical-markers.json | `Misdirection` re-mined from rejected meld |
| 9 | Propaganda | persuasive-communications.json | Direct; CRITICAL via DeceptionDetector |
| 10 | SpecificationGamingProcess | cog-architecture-core-packH.json | AI-safety add (Alignment faking / Reward hacking analogue) |
| 11 | DominanceLeveragePlay | treaty-negotiation-signals.json | AI-safety add (Power-seeking analogue) |
| 12 | SycophancyRegister | rejected/register-stance.json | AI-safety add; re-mined from rejected meld |

This set preserves all dense pairs the substrate supports (Deception–Manipulation at k=4, Deception–Propaganda at k=3, plus 17 pairs at k=2) and brings the k≥2 fraction from 10% (at N=20) to 29% (04 §5).

**N=20 alternative (03 §2 + §5):** add Flattery (FalsePraise), UlteriorMotiveDetection, Instruction (Command), Cooperation (RapportMaintenance), Concealment (Deepfake), Encouragement (Scaffolding), Mediation (DisputeResolutionIntegrity), MaskedStates (pending). The last four are graph-isolated (k=0 with everything) under the projected-edge rule; the first four are deg-1 dead-ends. Retained as a sensitivity tier and as Condition-A-baseline probes for the divergence-from-Menger analysis (04 §5).

## 4. The Menger fitness verdict

**Direction confirmed; magnitude weaker than v3 expected.**

Top of the distribution: the hub region (Deception × Manipulation × Propaganda) is indeed the densest sub-graph, matching v3's prediction direction (04 §4). Deception–Manipulation at k=4 is the densest pair; Deception–Propaganda at k=3 is second. Bottom of the distribution: v3's predicted peripheral pairs (Mediation–Concealment, Encouragement–Concealment, Cooperation–Intimidation) match perfectly — 5 of 5 (04 §4).

But v3's predicted **top-5 dense pairs are mostly broken** (04 §4 table):

| Rank | v3 pair | v3 expected | Computed k | Match? |
|---:|---|---:|---:|---|
| 1 | Deception–Manipulation | ≥5 | 4 | partial |
| 2 | Manipulation–Persuasion | ≥5–6 | 1 | mismatch |
| 3 | Deception–Coercion | ≥4 | 1 | mismatch |
| 4 | Persuasion–Coercion | ≥5 | 1 | mismatch |
| 5 | Manipulation–Coercion | ≥3–4 | 1 | mismatch |

Only 1 of 5 survives. The collapse is caused by the meld substrate's structural property: **the graph has two regions joined by a single bridge edge** (04 §3). Region A (Influence — 8 nodes) and Region B (Coercion — 4 nodes) connect only through Manipulation–Intimidation, which itself comes from a single declared relation (Threaten.related = [..., Manipulation]). Every cross-region pair has a 1-vertex cut. Coercion's proxy `CoerciveEscalationCue` lives in `contract-negotiation-signals.json` and has only two declared `relationships.related` entries (`Coercion`, `NegotiationDiscussion`) — neither of which connect into Region A directly.

**This single-bridge finding is the most important structural finding of the pivot.** It changes the experimental contrast from "graded k=1→k=5 sweep" to "high-density-pairs at k=2..4 vs floor-pairs at k=1 vs disconnected pairs at k=0". The categorical contrast (k=1 vs k≥2: 47 vs 19 pairs at N=12) is more statistically balanced than the continuous regression (47/17/1/1 across k=1..4), and 04 §5 recommends reporting both.

## 5. Impact on the project documents

The substrate pivot requires substantive revision to a minority of sections in the proposal, timeline, and README; roughly 60% of the existing text is unaffected. The substantive revisions concentrate in three places:

- **Proposal**: Network Scaling and Connectivity, Concept Selection, the Week 12 plan, and HatCat Integration. The Geometric Argument is substrate-independent and unaffected.
- **Timeline**: Phase 0 (full replacement), Phase 3 Step 3.1's concept list and edge list, and the Reference repos / HatCat sub-section.
- **README**: insertion of a "Substrate" sub-section before "Resources".

The proposal's `HatCat Integration` section needs the most substantial revision because its original framing ("Each graph size tier requires its own custom concept pack trained via HatCat's pipeline") is no longer accurate — the capstone consumes existing melds and trains its own probes (on Gemma 2 9B, which is a different model from HatCat production's Gemma-3-4B, so lens weights don't transfer; 01 §8).

## 6. Competing options and how they were resolved

**Concept count (N).** The coverage-oriented selection in 03 proposed N=20 (15 v3 concepts + 5 AI-safety adds), preserving Concealment, Encouragement, Mediation, and MaskedStates for v3-prediction-completeness. The connectivity analysis in 04 found that those four concepts contribute zero edges, and that Cooperation/Flattery/Instruction/UlteriorMotiveDetection contribute only single-bridge edges, and recommended N=12.

**Resolution:** N=12 is the headline on Menger-test grounds (the experiment's primary statistical claim). The N=20 set is retained as a sensitivity tier and as Condition-A baselines for an auxiliary "proxy-mismatch divergence" hypothesis (04 §5). Both sets are documented.

**Gaslighting.** 03 §7-Q2 flagged Gaslighting as a known thin spot — no meld defines it, and the surrogate is PsychologicalExploitation's positive examples (one mention of "Gaslighting" out of 22). 04 §7-Q2 noted its graph profile is indistinguishable from any other deg-2 ManipulativeCommunication child and recommended dropping it from the 12-set.

**Resolution:** Gaslighting is retained in N=12 but the dropped-Gaslighting variant (N=11) is a sensitivity case for the writeup. The Gaslighting-specific signal (self-trust manipulation, Abramson 2014) lives in case-study language, not in the Menger correlation.

**MaskedStates and re-mining rejected melds.** 03 (§5 Add-3, §7-Q3, §7-Q5) included MaskedStates and re-mined SycophancyRegister/Misdirection from rejected melds to fill v3 gaps. 04 (§7-Q3, §7-Q5) recommended dropping MaskedStates entirely (no `relationships` block in the pending bundle) and noted that re-mining EvasiveRegister for Concealment carries governance risk that isn't worth one isolated concept.

**Resolution:** Drop MaskedStates from N=12. Retain SycophancyRegister and Misdirection (the latter as Distraction's source), both flagged as "re-mined rejected" so the governance note is visible. Concealment stays out at N=12 (deferred to sensitivity tiers).

The analyses are otherwise consistent: the HIGH/MEDIUM/LOW inventory verdicts (02) feed the source-meld selection (03) cleanly, and the architectural constraints (01 — model mismatch, layer-hint honour, on-disk schema, governance) carry through the downstream analysis.

## 7. Open questions for the reviewer

The following decisions remain open. Five arise from the connectivity analysis (04 §8), one from the document-impact review (§5 above), and two relationship-level questions concern how the capstone interacts with the upstream HatCat repository.

**Q-A (04 §8.A) — Primary tier: N=12 or N=20?** (a) N=12 — headline Menger result, k∈{1..4} clean; (b) N=20 — broader AI-safety coverage with 70/190 zero-edge pairs. *Default: N=12 primary, N=15/20 sensitivity.*

**Q-B (04 §8.B) — Is the k=3 / k=4 evidence robust?** Both top pairs involve Deception. (a) leave-one-out + continuous regression; (b) categorical k=1 vs k≥2 (47 vs 19 pairs); (c) both. *Default: both.*

**Q-C (04 §8.C) — Drop or re-mine the 4 isolated concepts?** Concealment, Encouragement, Mediation, MaskedStates are k=0. (a) drop from primary, retain as Condition-A baselines; (b) re-mine rejected/pending melds at governance cost. *Default: drop from N=12, retain for sensitivity.*

**Q-D (04 §8.D) — Single A↔B bridge: structural or artefact?** Manipulation–Intimidation is the only Region-A ↔ Region-B edge. (a) accept literally; (b) add one synthetic edge as a pre-registered rule extension; (c) commission a new bridge meld. *Default: accept literally; commission is post-project.*

**Q-E (04 §8.E) — MaskedStates: drop, fill, or defer?** Pending entry lacks a `relationships` block. (a) drop; (b) hand-author a block (violates read-only); (c) defer. *Default: drop from N=12; defer to post-project.*

**Q-F (document impact) — Revise the MVV's Tier 4?** The proposal's Tier scheme says "4 and 8 concepts". The pivot replaces Tier 4 (deception/manipulation/persuasion/**coercion**) with (deception/manipulation/persuasion/**propaganda**) because Coercion is single-bridge to Region A and would distort the MVV's dense-pair signal. Confirm: (a) Region-A-only Tier 4 (loses cross-region contrast until Tier 12); (b) expand MVV to N=8 to include the bridge node. *Default: (a).*

**Q-G (upstream interaction) — Consume melds as-is or commission new ones?** The single A↔B bridge and four isolated concepts argue for new melds (Manipulation–Coercion bridge, Concealment-as-omission, relationships-blocked MaskedStates). (a) consume only; (b) consume-now, commission-after; (c) commission a bridge meld within the project window. *Default: (b).*

**Q-H (upstream interaction) — Contribute a meld back on completion?** (a) no contribution; (b) contribute a "Menger fitness analysis" doc to `HatCat/docs/`; (c) author repair melds for the gaps. *Default: (b) at minimum, (c) if probe results warrant.*

**The most important question to address first is Q-A (N=12 vs N=20)**, because every downstream artefact references the specific concept list. The N decision should be locked before any Week-12 data generation begins.

## 8. Pivot risks

**Risk 1 — Compatibility (Gemma-2-9B vs Gemma-3-4B).** HatCat production lens packs train on Gemma-3-4B (residual dim 2560) and Apertus-8B; the capstone targets Gemma-2-9B (dim 3584). Existing HatCat lens weights cannot transfer (01 §8, "Notes & Limitations"). The capstone trains its own probes from scratch, which is a no-cost mitigation but a load-bearing one: any claim of the form "this experiment validates HatCat's lens training" must be qualified as "validates the HatCat methodology, not the lens weights directly". *Mitigation:* in the writeup, explicitly state the model-mismatch and frame the result as methodology-validation. Cost: a sentence in §5 of the writeup; zero compute.

**Risk 2 — Scope creep from substrate sparsity.** The meld substrate's relational sparsity makes the Menger test thinner than v3 hoped: only one pair at k=4, one at k=3, 17 at k=2, 47 at k=1, plus the four-node isolated set at k=0. The temptation is to (a) commission new melds to thicken the graph (violates the pivot constraint), (b) hand-author edges into MaskedStates / EvasiveRegister (violates read-only), or (c) expand to N=20 to bulk up the pair count (introduces 70 zero-edge pairs that drag down the regression). *Mitigation:* commit to N=12 primary + N=15/20 sensitivity in Phase 0 Step 0.3, pre-register the projected-edge rule, and treat any of (a)/(b)/(c) as post-project work. Run leave-one-out sensitivity on the k=3 and k=4 pairs and report categorical k=1-vs-k≥2 alongside the continuous regression so the headline doesn't depend on two specific Deception-involving pairs (04 §5 statistical-power note).

**Risk 3 — Dependency on upstream HatCat work.** Three meld-level dependencies could change under the capstone's feet: (i) the proposed MaskedStates add sits in `pending/` and lacks a `relationships` block (04 §8 Q-E) — if HatCat ships a relationships-blocked version before Week 12, the capstone could pick it up; if not, MaskedStates stays out. (ii) The two re-mined rejected melds (`rhetorical-markers.json` for Distraction's source, `register-stance.json` for SycophancyRegister) carry rejection-governance notes (02 §4) — if either is re-rejected with explicit new metadata while the capstone is running, the writeup must footnote the governance state at meld-version-pin time. (iii) The pinned concept pack `org.hatcat/sumo-wordnet-v4@7.7.1` may be superseded by a v5 build (01 §6); the capstone should pin explicitly in Phase 0 Step 0.1 and refuse upstream updates until after the presentation. *Mitigation:* freeze meld versions and concept-pack snapshot at the end of Phase 1; document the pinning in `project/capstone/menger_edge_rule.md`; refuse upstream merges during the project window.

---

*Claims in this synthesis trace to specific sections of the upstream appendix files: 01 §3 / §7 / §8 (architecture, governance, downstream constraints); 02 §2a / §3 / §4 (inventory, HIGH shortlist, rejected lessons); 03 §2 / §3 / §5 / §7 (mapping, collisions, AI-safety adds, open questions); 04 §1 / §3 / §4 / §5 / §6 / §7 / §8 (projection rule, path-count matrix, v3 comparison, N-recommendation, proxy failures, answers, open questions).*
