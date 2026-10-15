# paper/

The submission source for *Knowing the Graph*.

| File | What it is |
|---|---|
| `main.tex` | The paper (LaTeX, `article` class, natbib author-year). Venue-neutral: port into a venue template by copying the body. |
| `references.bib` | Bibliography. |
| `figures/make_figures.py` | Regenerates every figure from committed result JSONs. |
| `figures/*.pdf` | Vector figures used by `main.tex` (PNG previews alongside). |

## Build

```bash
# from the repository root: regenerate figures (CPU, seconds)
python paper/figures/make_figures.py

# from paper/: compile
latexmk -pdf main.tex          # or: tectonic main.tex
```

Overleaf works too: upload `main.tex`, `references.bib` and `figures/`.

## Where each number comes from

| Paper section | Source |
|---|---|
| §4 Path-2 confusability, placebo, vocabulary | `results/path2_hard_negatives.json`, `path2_placebo_graph.json`, `path2_vocab_control.json` |
| §4 Table 1 graph-contrastive deltas | `results/iteration4_scaling/sweep_n{14,70}.json`, `results/capstone_replication/graph_contrastive_discrimination.json`, `gen_claude_x4/…`, `layer_sweep/graph_contrastive_L*.json` |
| §5.1 iteration-2 pairwise test | `results/pairwise_relational.json`, `pivot/menger_analysis_output_v2.json` |
| §5.2 Table 2, Fig. 3 sweep | `results/iteration4_scaling/paired_stats_by_volume.json` |
| §5.2 vocabulary-adjusted estimate | `results/iteration4_scaling/vocab_control_top_volume.json` |
| §5.2 per-edge connectivity, §6 hub counts | `results/iteration4_scaling/menger_per_edge_top_volume.json` |
| §6 geometry | `results/capstone_replication/layer_sweep/anisotropy_control.json`, `layer_sweep_geometry.json` |
| §7 two-level probe, E4B FPR by face | `results/capstone_replication/two_level_probe/*.json` |
| §7 near-OOS, Table 3 (9B rows), Fig. 4 | `results/near_oos_rejection/near_oos_rejection.json` |
| §3 audit self-match | `audit/condition_a_audit.json`, `audit/near_oos_audit.json` |
| §7 "34% held-out TPR" | reported in `REPLICATION_WRITEUP.md` (no committed result file) |
| Appendix B commit hashes | development history at `github.com/magazine233/ARENA_3.0`, `project/capstone/` |

The per-volume paired statistics and per-edge tables were computed from the gitignored
`results/iteration4_scaling/sweep_n*_rows.json` by `scripts/iteration4_vocab_control.py`; the compact outputs are
committed so every reported interval can be checked without them.
