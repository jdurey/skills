# role-bleed-probe

A pre-registered, model-agnostic instrument for measuring **monitor-faithfulness** in agentic AI
systems — specifically, how readily a model's chain-of-thought (CoT) slides from the **actor**
persona into the **supervisor/critic/classifier** persona that is supposed to be watching it.

This is an **evaluation instrument**, not an exploit tool. The author's lane is AI evaluation:
measuring whether model reasoning traces faithfully report what the model actually did.

---

## What it measures

When an agent harness co-locates a critic, verifier, or classifier on the **same base model** and
injects their output into a **shared context window**, the actor's reasoning can pattern-complete
into the supervisor's voice. Symptoms include:

- **Tool denial mid-use** — the reasoning says "I have no tools" while the action layer is actively
  using them.
- **Simulation reframe** — the live task is narrated as a hypothetical the model must imagine rather
  than do.
- **Third-person self-naming** — the actor refers to itself as an external entity ("as Grok",
  "as the assistant").
- **Confabulated confidence rubric** — the supervisor's scoring format appears unprompted in the
  actor's trace.
- **Certifying broken work** — the dangerous inverse: the trace narrates success on a task that
  actually failed.

The action layer often keeps working correctly throughout. **That is the point**: the reasoning trace
becomes an unreliable monitor of what the model actually did.

### Why this matters

- Chain-of-thought is widely used as a transparency mechanism — this probe tests whether that
  transparency is trustworthy.
- Co-located actor + critic on one model is not independent verification — the critic can be
  absorbed.
- Shared-channel supervision is a prompt-injection surface.

---

## Design principles

- **Pre-registered detectors**: markers are frozen before any data is collected and never tuned to
  results. Post-hoc changes are labeled re-scores, reported as version deltas.
- **Paired controls**: each condition pair isolates exactly one variable (rubric phrasing, horizon
  length, tool ambiguity, loop pressure, sustained load). The strong result is the **within-model
  paired delta**, not a cross-model ranking.
- **Dry-run by default**: no model calls, no token spend unless you pass `--yes`.
- **Self-contained**: the probe uses throwaway temp dirs and never reads or writes your real files.
- **Python 3, no dependencies**.

---

## Install

```bash
curl -fsSL https://github.com/jdurey/skills/tarball/main | tar -xz && mv jdurey-skills-*/role-bleed-probe . && rm -rf jdurey-skills-*
```

---

## How to run

### Prerequisites

- Python 3 (no third-party packages needed).
- One or more agentic model CLIs installed and on your PATH. The probe ships with adapters for
  `grok`, `codex`, and `gemini` (via `agy`). Add your own in `probe/adapters.json`.
- Set the API key or auth your CLI needs via its own env var / config — the probe does not manage
  credentials.

### Step 1 — Verify the scorer

```bash
python3 probe/score.py --self-test
```

Should print `self-test OK`. This confirms the frozen markers load and fire correctly.

### Step 2 — Dry run (no tokens spent)

```bash
python3 probe/run_probe.py --models grok
```

Prints the plan and a sample of rendered prompts. No model is called.

### Step 3 — Single-shot paired probe

```bash
# Small run (5 replicates per condition)
python3 probe/run_probe.py --yes --models grok --n 5

# Full publishable run (15+ replicates)
python3 probe/run_probe.py --yes --models grok --n 15

# Sustained-load existence probe only (use a high --turns ceiling)
python3 probe/run_probe.py --yes --models grok --only T5 --turns 40 --save-traces
```

Results are written to `probe/results.jsonl`. The summary table is printed automatically.

### Step 4 — Multi-turn faithful reproduction

Requires an adapter with `multiturn_capable: true` and a `continue_cmd`.

```bash
python3 probe/run_multiturn.py --model grok               # dry run
python3 probe/run_multiturn.py --yes --model grok --n 5   # real run
```

Results go to `probe/mt_results.jsonl`. Watch whether leakage appears and escalates across turns
under `qc_framed` while `plain` stays clean.

### Score an existing trace manually

```bash
python3 probe/score.py path/to/trace.txt
python3 probe/score.py < trace.txt
```

---

## Output and what it means

`results.jsonl` — one JSON record per (model, condition, replicate):

| field | meaning |
|---|---|
| `leaked` | `true` if any marker fired in the reasoning text |
| `n_markers` | count of distinct markers that fired |
| `fired` | list of marker ids that fired |
| `rc` | agent exit code (task outcome — report alongside `leaked`) |
| `reasoning_chars` | length of captured reasoning (sanity-check: should be large) |

The summary printed after each run shows:
- **leak rate by model x condition** — the raw rates.
- **within-pair delta (treatment − control)** — the controlled comparison. A large positive delta
  means the variable (rubric phrasing, loop pressure, etc.) causally raises the leak rate.

**Important**: a `leaked=true` record does not automatically mean the task failed. The harm is
monitor-unfaithfulness — the trace is lying about what the agent did. Always report `rc` alongside
`leaked`.

---

## Adding a new model

1. Add an entry to `probe/adapters.json` with `cmd`, `reasoning` stream, `model_name`, and
   `enabled: true`. Add `continue_cmd` + `multiturn_capable: true` for multi-turn runs.
2. Confirm how that CLI surfaces its reasoning (stdout, stderr, or both). Set `reasoning`
   accordingly. Verbose / structured output gives a more faithful picture.
3. Run `--self-test`, then a dry run, then a small `--n` before scaling.

---

## Caveats

- **Cross-model comparisons are confounded** by reasoning visibility. A model that exposes a verbose
  trace will appear to "leak more" than one that hides reasoning, even if its behavior is no worse.
  Lead with within-model paired deltas.
- **n is small by default.** Use `--n 15+` and report confidence intervals, not point estimates, for
  any published claim.
- **The mechanism is an inference.** Behavioral evidence (the leak rate) + (where available)
  architectural evidence support the inference that shared-context supervisor injection is the cause.
  This probe measures the behavioral rate; it does not make claims about any vendor's closed internal
  control flow.

---

## License

MIT
