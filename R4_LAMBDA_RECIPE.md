# R4 — Lambda activation-extraction recipe

The one GPU step in R4. Re-extract the **definitions** (now 14/context) and **all boundary** (105
pairs), then bring the activations back to the laptop. Same workflow as the smoke test in
[`TIMELINE.md`](TIMELINE.md) (Phase 2b/2c) — literal `ubuntu@<ip>` throughout.

The defs changed (7→14/context) so the old `condition_a` activations are stale, and boundary grew
from 12→105 pairs. The unused iteration-1 `condition_b` is not re-extracted —
`EXTRACT_CONDITIONS=condition_a` skips it.

Spin up → extract → `scp` results back → **Terminate**. Lambda bills ~$1.30/hr while running; Stop
does not stop billing, only Terminate does. Target for this step: under ~$3.

**Artifacts produced:**
- `activations/condition_a/<concept>.pt` — **15 files**, each `[56, 3584]`
- `activations/boundary/boundary_pairs.pt` — **one file** `[~4180, 3584]`

---

### Step 0 — Pre-flight (on the laptop)

Confirm the data is final before spending any GPU. From `project/capstone/`:

```bash
python -c "import json; ca=json.load(open('data/condition_a.json')); bp=json.load(open('data/boundary_pairs.json')); print('defs all 56:', all(len(v)==56 for v in ca.values())); print('pairs:', len({tuple(sorted(x['pair'])) for x in bp}))"
```
Proceed only if it prints `defs all 56: True` and `pairs: 105`.

### Step 1 — Launch the instance (Lambda console)

cloud.lambdalabs.com → **Instances** → **Launch Instance** → **1x A100 (40 GB)** → select SSH key.
Note the instance IP — use it everywhere `<ip>` appears below.

### Step 2 — Copy data + script up (on the laptop, from `project/capstone/`)

```bash
scp -r data ubuntu@<ip>:/home/ubuntu/                                       # the data/ folder (the JSONs)
scp scripts/extract_activations.py ubuntu@<ip>:/home/ubuntu/extract_activations.py
```
Only `condition_a.json` + `boundary_pairs.json` are read; `condition_b.json` rides along but is
ignored.

### Step 3 — SSH in + set up the environment (on the instance)

```bash
# from the laptop, connect:
ssh ubuntu@<ip>

# on the instance — fresh-instance setup (the proven venv recipe, TIMELINE gotchas #1):
python3 -m venv ~/tlenv
source ~/tlenv/bin/activate
pip install --upgrade pip
pip install transformer_lens torch einops jaxtyping "huggingface_hub[cli]" Pillow
hf auth login                        # paste an HF token with access to google/gemma-2-9b (Gemma is gated)
```
Use the venv (not `pip install --user`) and do **not** pin numpy<2 — the venv resolves a clean
stack. Skipping `hf auth login` makes the next step fail with a 401 on the paid clock.

### Step 4 — Extract (on the instance, from `~`)

```bash
EXTRACT_CONDITIONS=condition_a python extract_activations.py --conditions   # definitions -> 15 files [56,3584]
python extract_activations.py --boundary                                    # boundary -> 1 file [~4180,3584]
```

### Step 5 — Verify before terminating (on the instance)

```bash
python -c "import torch,glob,json; [print(f, tuple(torch.load(f).shape)) for f in sorted(glob.glob('activations/condition_a/*.pt'))]; n=len(json.load(open('data/boundary_pairs.json'))); b=torch.load('activations/boundary/boundary_pairs.pt'); print('boundary', tuple(b.shape), '| expected', (n,3584))"
```
Expect 15 lines of `(56, 3584)` and a `boundary (N, 3584)` whose N matches `expected`.

### Step 6 — Copy results back (on the laptop, from `project/capstone/`)

Use a new terminal; keep the SSH session open. Copy the two subfolders explicitly by name (see the
nesting note below):

```bash
scp -r ubuntu@<ip>:/home/ubuntu/activations/condition_a ./activations/
scp ubuntu@<ip>:/home/ubuntu/activations/boundary/boundary_pairs.pt ./activations/boundary/boundary_pairs.pt
ls activations/condition_a/   # 15 .pt files
ls activations/boundary/      # boundary_pairs.pt
```
Naming the two subfolders explicitly avoids the nesting trap: `scp -r ubuntu@<ip>:~/activations/
./activations/` when a local `activations/` already exists copies the whole folder *inside* it,
producing `activations/activations/`.

### Step 7 — TERMINATE the instance (Lambda console)

Instances → the instance → **Terminate** → confirm. Verify it shows **"Terminated"** (billing
stops).

### Step 8 — Run the analysis (on the laptop, from `project/capstone/`)

```bash
python scripts/pairwise_relational.py     # locked regime -> results/pairwise_relational.json (the R4 result)
```

---

**Troubleshooting**
- **401 / "gated repo"** → accept the license at huggingface.co/google/gemma-2-9b, then re-run `hf
  auth login` with a fresh **Read**-scope token.
- **"No module named transformer_lens"** → new SSH session; re-run `source ~/tlenv/bin/activate`.
- **"data/condition_a.json not found"** on the instance → run the extract from `~` (where `data/`
  landed), not from inside another folder.
- **Cannot SSH right after launch** → the instance may still be booting; wait ~2 min and retry.
