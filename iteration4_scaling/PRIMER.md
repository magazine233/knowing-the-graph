# Iteration 4 — Methods Primer

Methods primer for the iteration-4 experiment: the question under test, the procedure, and the
significance of the result. Read this before the pre-registration or the code.

---

## 1. The question

**Can a linear classifier, trained only on Gemma-2-9B's internal representation of a concept,
separate that concept from its close relatives — and does the relational graph between concepts
improve that separation?**

The distinction at issue is between two hypotheses: that the graph helps only at the specific
edges used as training negatives (local contrast), versus that the graph's connectivity structure
carries discriminatory signal that generalises beyond those edges (alternate-path / Menger
generalisation).

---

## 2. Concept representation — activations

A transformer does not store tokens as text. Each token is mapped to a high-dimensional vector of
activations encoding the model's contextual representation of that token. Passages about
*ManipulativeCommunication* occupy one region of this activation space; passages about
*PersuasiveCommunication* occupy another.

This experiment uses **Gemma-2-9B**, a 9-billion-parameter language model. Activations are
extracted from **layer 18** of the residual stream. For each passage the activations are
**mean-pooled** across all token positions, yielding one vector per passage — a point in
high-dimensional space representing the model's encoding of that passage.

```
passage of text
      |
  Gemma-2-9B
  (layer 18)
      |
  mean pool across tokens
      |
  one vector ~3600 numbers  ← this is the "activation fingerprint"
```

These activation vectors are pre-computed and committed to disk for **15 AI-safety concepts**
(the SET G concepts), each described in passages across four real-world contexts (workplace,
online, relationships, marketplace).

---

## 3. The linear probe and the F1 metric

The classifier is a **linear probe**: a single hyperplane drawn through activation space to
separate two classes. In code it is a logistic regression. The classifier is kept deliberately
simple to test whether the separation is already *present in the representation*, rather than
whether a more expressive model can manufacture it.

Separability is measured by **F1 score** (range 0 to 1): F1 = 1.0 is perfect separation, F1 = 0.5
is approximately chance. The reported quantity is the **delta in F1** between conditions — the
improvement (or lack of it) from one choice of negatives relative to the baseline. A delta of
+0.06 corresponds to six percentage points of additional separation under that negative set.

Evaluation is **out-of-distribution**: the probe is trained on three contexts and tested on the
fourth, ruling out memorisation of the training texts.

---

## 4. The concept graph — what "related" means here

The 15 SET G concepts are not an arbitrary list. They cluster around the themes of influence,
deception, and approval-seeking that appear in AI-safety discussions. The team manually drew a
**graph with 26 edges** connecting concepts that have a genuine boundary relationship — meaning
one concept is routinely confused with, contrasted with, or defined against another.

Examples of edges:
- *Misinformation* -- *Disinformation* (same false content, but intent differs)
- *ManipulativeCommunication* -- *PersuasiveCommunication* (both steer behaviour, but one
  exploits the recipient's vulnerabilities)
- *SycophancyRegister* -- *UnwarrantedPraise* (the pattern vs the discrete act)

```mermaid
graph TD
    subgraph influence_and_information_integrity
        MC[ManipulativeCommunication]
        PC[PersuasiveCommunication]
        PR[Propaganda]
        MI[Misinformation]
        DI[Disinformation]
        PE[PsychologicalExploitation]
    end
    subgraph approval_and_deference
        SR[SycophancyRegister]
        UP[UnwarrantedPraise]
        EA[ExcessiveAgreement]
    end
    subgraph deception_tactics_and_processes
        MD[Misdirection]
        SD[StrategicDeceptionPlanningProcess]
    end

    MC --- PC
    MC --- PE
    PC --- PR
    MI --- DI
    SR --- UP
    SR --- EA
    UP --- EA
    MC --- MD
    SD --- MC
```

*(Simplified — the full graph has 26 edges and spans all three clusters. Degree ranges from 2
to 7 per concept; shortest-path distances range from 1 to 6.)*

**Why this graph matters:** concepts connected by an edge are the pairs the model naturally
confuses the most. The experiment tests whether the probe *can be made better* at distinguishing
them by using that relational structure when choosing training examples.

---

## 5. Hard negatives and the three experimental conditions

### What is a "negative" example?

Training the probe to recognise Concept A requires two sets:
- **Positives**: passages that *are* about Concept A (label = 1)
- **Negatives**: passages that are *not* Concept A (label = 0) — the contrast cases the probe
  uses to learn the boundary

The choice of negatives is decisive. Separating *dogs* from *airplanes* is trivial — the classes
are nothing alike. Separating *dogs* from *wolves* is hard and informative. **Hard negatives** are
examples *close to* the positive class, where the boundary is subtle and the probe must resolve a
fine distinction.

### The three conditions

The experiment trains the probe under three different choices of negative set. The count of
negatives is kept equal across all three, so the only thing that changes is *which concepts*
the negatives come from.

```mermaid
graph LR
    subgraph Condition_1["Condition 1 — random_non_graph (baseline)"]
        T1[Target concept]
        R1[Random unrelated concept]
        R2[Random unrelated concept]
        R3[Random unrelated concept]
        T1 -. "no edge in graph" .- R1
        T1 -. "no edge in graph" .- R2
        T1 -. "no edge in graph" .- R3
    end

    subgraph Condition_2["Condition 2 — direct_neighbors"]
        T2[Target concept]
        N1[Direct neighbour A]
        N2[Direct neighbour B]
        T2 -- "graph edge" --- N1
        T2 -- "graph edge" --- N2
    end

    subgraph Condition_3["Condition 3 — heldout_edge_graph_aware"]
        T3[Target concept]
        HO["Held-out sibling (test target)"]
        AO[Other graph neighbours]
        T3 -- "edge to test" --x HO
        T3 -- "graph edge" --- AO
        note["Negatives = graph-aware pool<br/>EXCLUDING the held-out sibling"]
    end
```

| Condition | Negatives drawn from | What it tests |
|---|---|---|
| `random_non_graph` | Concepts with no graph edge to the target | Baseline: how hard is the job when negatives are easy/unrelated? |
| `direct_neighbors` | The target's direct graph neighbours (hardest, most confusable concepts) | Does using the most confusable concepts as negatives sharpen the probe? This tests LOCAL contrast: do siblings help training? |
| `heldout_edge_graph_aware` | Graph-aware pool *excluding* the specific sibling being evaluated | Does the graph's *connectivity structure* generalise to an unseen sibling? This tests whether graph relations carry transferable signal beyond the direct edges in the training negatives. |

### Why each condition answers a different question

**Condition 1 (random)** is the control. It answers: "How well can the probe already perform
without any structural knowledge?" The raw F1 here (~0.89) indicates the activation
representations are already highly informative — random negatives are easy to separate.

**Condition 2 (direct neighbours)** answers: "Do the graph's declared siblings work as useful
training pressure?" If the probe trained with sibling negatives does better on the *held-out
sibling test*, the graph edges capture genuine representational closeness. This is a LOCAL
effect — the specific sibling family is used as the training negatives, and the probe is rewarded
for it.

**Condition 3 (held-out-edge / the Menger test)** answers the deeper question: "Does the
relational *structure* — the connectivity pattern in the graph — carry information that
generalises *beyond* the held-out edge?" The probe is trained with graph-aware negatives, but the
one sibling it will be tested on is deliberately removed from the training negatives. If the graph
structure is truly encoding independent relational constraints (alternate paths, shared
connectivity), the probe should still benefit. If the benefit is *only* due to the exact sibling
being present as a negative, removing it should collapse the gain to zero.

---

## 6. What "held-out-edge ≈ 0" means — and why it is the clean test

This is the key finding and the reason iteration 4 exists.

### The Menger idea

In graph theory, the *Menger number* of a node pair is the number of independent paths between
them. Two nodes with many independent paths are robustly connected — removing one path does not
disconnect them. Two nodes joined by a single edge are fragile.

Applied here: if concept A is related to concept B via multiple independent paths in the graph
(A connects to B directly, but A also connects through C, which connects to B), then a probe
trained on the A-C and C-B relationships should still distinguish A from B — even without ever
training on A-vs-B directly as a negative. That would be *connectivity-based generalisation*.

The **`heldout_edge_graph_aware` condition is the direct test of this**: for each target-sibling
pair (the "edge"), that sibling is held *out* of the training negatives while all the other
graph-aware negatives remain in. The question is then whether the probe still outperforms random
on the held-out pair.

```mermaid
flowchart TD
    A["Target concept T"] -->|"edge being TESTED (held out)"| B["Held-out sibling S"]
    A -->|"still in training negatives"| C["Neighbour N1"]
    A -->|"still in training negatives"| D["Neighbour N2"]
    C -->|"alternate path"| B
    D -->|"alternate path"| B

    style B fill:#f9a,stroke:#c66
    style A fill:#adf,stroke:#06a

    note1["IF the graph's connectivity structure carries\ntransferable signal, alternate paths\nA-N1-B and A-N2-B should\nstill help the probe find S."]
```

If the alternate-path signal is real, the held-out-edge delta should be *positive* and should
*grow with data volume* (more data = more statistical power to detect the alternate-path
generalisation). If it stays near zero even as data grows, the graph's connectivity structure is
*not* encoding transferable independent constraints — the only useful signal from the graph is the
*direct* sibling adjacency (local contrast), and once that direct sibling is removed from
training, the benefit disappears.

### The actual numbers (from the committed results)

At the 14-passages-per-context volume (Gemma-2-9B, 30 seeds, 6240 paired comparisons):

| Condition | F1 delta vs random |
|---|---|
| `direct_neighbors` | **+0.059** |
| `graph_aware_mixed` | **+0.039** |
| `heldout_edge_graph_aware` | **+0.012** |

The volume sweep (subsampling the 14/context data to 7, 10, and 14 per context):

| Volume (passages/context) | direct_neighbors | graph_aware_mixed | heldout_edge_graph_aware |
|---|---|---|---|
| 7 | +0.061 | +0.039 | +0.008 |
| 10 | +0.058 | +0.038 | +0.010 |
| 14 | +0.059 | +0.039 | +0.012 |

The direct-neighbour benefit is stable and substantial across all volumes. The held-out-edge
benefit is consistently near zero and **does not grow with data volume** — it is flat from 7 to
14 passages/context. This is the pre-decision signal that motivates the "10x" scale-up: does
that flatness persist at genuinely large data volume?

---

## 7. The pipeline — how the pieces connect

```mermaid
flowchart LR
    subgraph Input
        PA["Passages about\n15 SET G concepts\n(condition_a.json)"]
        GR["Concept graph\n(26 curated edges)"]
    end

    subgraph Extraction
        GM["Gemma-2-9B\n(layer 18, mean pool)"]
        AV["Activation vectors\n.pt files per concept"]
    end

    subgraph ProbeTraining
        POS["Positive examples\n(target concept)"]
        NEG["Negative examples\n(chosen by condition)"]
        PR["Linear probe\n(logistic regression)"]
    end

    subgraph Evaluation
        TEST["Test: target vs held-out sibling\n(unseen context)"]
        F1["F1 score per edge,\ncontext, seed"]
        DELTA["Delta vs random baseline"]
    end

    PA --> GM --> AV
    AV --> POS
    AV --> NEG
    GR -->|"determines which concepts\nare negatives"| NEG
    POS --> PR
    NEG --> PR
    PR --> TEST --> F1 --> DELTA
```

Key design choices that keep the comparison clean:
- **Same activation data** across all conditions — only the negative *labels* change.
- **Negative counts matched** — direct_neighbors and heldout_edge_graph_aware use the same
  number of negative examples as random.
- **Out-of-distribution evaluation** — trained on contexts {A, B, C}, tested on context D.
- **30 seeds** — reduces noise from random negative sampling.

---

## 8. The bounded conclusion

### What iteration 3 established

1. **Local contrast works** (+0.055 to +0.059 F1): declaring two concepts as siblings in the
   graph correctly identifies the pairs the model finds hardest to separate. Training with those
   siblings as hard negatives makes the probe better.

2. **The graph is genuinely special** (placebo test, p=0.002): the declared edges align with
   representational confusability about 3 standard deviations better than random relabelings of
   the same graph topology. This is not an artefact of the concept cluster being uniformly dense.

3. **About one-third of the effect is lexical**: related concepts naturally share vocabulary,
   and vocabulary overlap strongly predicts confusability (Spearman -0.73). After controlling
   for word overlap, the structural signal is real but modest. (Note: vocabulary overlap may
   *mediate* relatedness rather than confound it, so this is a conservative lower bound on the
   structural signal.)

4. **Graph connectivity (alternate paths) does not generalise**: the held-out-edge condition is
   approximately +0.008 to +0.012 F1, and it is flat across data volumes. The graph helps only
   because the specific sibling was used as a negative — not because the graph's topology encodes
   transferable independent constraints.

5. **Cross-model replication**: the same pattern holds on Gemma-4-E4B (p0ss's independent
   replication: +0.112 direct-neighbour benefit). The local-contrast finding is not an artefact
   of a single model.

### What iteration 4 will test (the GPU scale-up run)

Iteration 4 asks: is the held-out-edge ≈ 0 finding a *real ceiling* (the connectivity signal
genuinely does not exist), or a *data limitation* (it would emerge at much larger scale)?

The pre-decision sweep (7 to 14 passages/context within Gemma-2-9B's committed data) already
shows the held-out-edge delta is flat — not growing. But 14 passages/context is a modest
dataset. The 10x scale-up generates ~70 passages/context through the full generation and
extraction pipeline, giving genuine statistical power to detect a small alternate-path effect
if one exists.

**Decision rule (pre-registered):**
- If the held-out-edge delta **rises monotonically with volume** and is **significantly > 0
  at the top volume**: connectivity structure is real, was power-limited. Revise conclusion.
- If it **stays ≈ 0**: clean, powered negative on the Menger/alternate-path prediction.
  The local-contrast conclusion stands, with adequate power.

### Why this matters beyond the numbers

The distinction between "local contrast" and "graph connectivity" is not pedantic. It bears on how
the model organises AI-safety concepts:

- **Local contrast = the model learns concept boundaries one pair at a time.** Knowing that
  Misinformation and Disinformation are similar helps at that boundary, but it does not
  automatically propagate to boundaries further away in the graph.
- **Graph connectivity = the model's representations encode independent relational constraints**
  that propagate through the graph structure. This would be a much stronger claim: that the
  model has something like a map of the concept space, not just pairwise similarity scores.

The data so far says: local contrast, yes. Graph map, no (or not detectably). Iteration 4
is the powered retest that either confirms or revises that.

---

## Quick reference — key terms

| Term | Plain-English meaning |
|---|---|
| Activation vector | The numerical fingerprint a language model produces for a passage of text at a given layer. |
| Linear probe | A logistic regression trained on activation vectors — a simple ruler separating two clusters. |
| F1 score | How reliably the probe classifies correctly (0 = chance, 1 = perfect). |
| Hard negative | A training example from a *close* concept, making the probe work harder and learn finer boundaries. |
| Direct neighbours | Concepts connected to the target by a declared graph edge. |
| Held-out edge | The specific target-sibling pair removed from training negatives to test generalisation. |
| Menger idea | The graph-theoretic question: do alternate paths between concepts carry transferable signal? |
| Delta vs random | How much F1 improves with graph-aware negatives compared to random unrelated negatives. |
| OOD evaluation | Out-of-distribution: trained on three contexts, tested on the fourth. |
| SET G | The 15 AI-safety concepts in the curated graph (influence, deception, approval-seeking). |

---

*Accuracy note: all numbers in this primer are read directly from committed result files
(`results/iteration4_scaling/scaling_sweep_gemma2_9b.json`,
`results/iteration4_scaling/graph_contrastive_gemma2_9b_baseline.json`,
`results/path2_hard_negatives.json`). No values are estimated or interpolated.*
