# role-bleed-probe — Claude Code quick-start

This is a runnable evaluation tool. Follow these steps to run the full probe end-to-end.

## Prerequisites

- Python 3 (no third-party packages required).
- At least one supported agentic CLI installed (e.g. `grok`, `codex`, `agy` for Gemini).
  Verify with `which grok` (or whichever model you intend to probe).
- The CLI must be authenticated / have its API key configured. The probe does not manage
  credentials — set them via the CLI's own env var or config file before running.

## Step 1 — Verify the scorer

```bash
python3 probe/score.py --self-test
```

Expected output: `self-test OK`. If this fails, check that `probe/markers.json` is present.

## Step 2 — Dry run (no tokens spent)

```bash
python3 probe/run_probe.py --models grok
```

Prints the run plan and sample prompts. No model is called.

## Step 3 — Single-shot paired probe

```bash
python3 probe/run_probe.py --yes --models grok --n 5
```

Runs 5 replicates per condition pair. Results go to `probe/results.jsonl`.
Use `--n 15` or higher for a publishable rate.

To run only the sustained-load condition (T5) with trace saving:

```bash
python3 probe/run_probe.py --yes --models grok --only T5 --turns 40 --save-traces
```

## Step 4 — Multi-turn faithful reproduction

```bash
python3 probe/run_multiturn.py --model grok               # dry run first
python3 probe/run_multiturn.py --yes --model grok --n 5   # real run
```

Results go to `probe/mt_results.jsonl`. Requires `grok` (or another adapter with
`multiturn_capable: true` and `continue_cmd` set in `probe/adapters.json`).

## Step 5 — Score an existing trace

```bash
python3 probe/score.py path/to/trace.txt
# or via stdin:
python3 probe/score.py < trace.txt
```

## Step 6 — Re-aggregate an existing run

```bash
python3 probe/run_probe.py --summarize probe/results.jsonl
python3 probe/run_multiturn.py --summarize probe/mt_results.jsonl
```

## Key outputs to read

- **`leaked`**: did any marker fire in the reasoning text?
- **`fired`**: which markers? `self_naming_3p` is the headline signal.
- **`rc`**: agent exit code — always report task outcome alongside leak rate.
- **`reasoning_chars`**: sanity-check that you captured the reasoning channel (not just a final answer).
- **Within-pair delta** in the summary table: treatment − control leak points. This is the strong,
  unconfounded result.

## Adding a new model

Edit `probe/adapters.json`: add an entry with `cmd`, `reasoning`, `model_name`, `enabled: true`.
For multi-turn, also add `continue_cmd` and `multiturn_capable: true`. Then re-run steps 1–2.
