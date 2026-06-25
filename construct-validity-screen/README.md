# Construct-Validity Screen

A **pre-data predictor of low item discrimination** for multiple-choice questions — it flags
items where knowing vs. not-knowing the content doesn't change whether a student gets them
right. It reads each item **twice, cold** — once with the answer key hidden (what a non-master
can recover from the surface), once against the standard (what it claims to measure) — and
flags where the two **diverge**: guessable stems, distractors that map to no real
misconception, a second defensible answer. This is **not** an item-quality checklist and not a
per-topic rule list; it predicts one psychometric property — discrimination — and the judgment
layer generalizes.

**It's a loud screen — it produces candidates for review, not verdicts.** "Distrust the
zero, distrust the hit." Because it's tuned to over-flag, a different-family adjudicator belongs
right after it — so only confirmed findings reach a builder and the gate doesn't cry wolf.

## Try it (Claude Code)

Open this folder in Claude Code and just say: *"screen these items"* and paste a batch —
the agent will format, run, and walk you through the results (see `CLAUDE.md`).

Or run it directly:

```bash
./run-qc.sh example-items.json "example run"
# then: ./run-qc.sh your-items.json "your batch"
```

Needs `python3` (stdlib only) and the `claude` CLI — no API key, no install. Each item is
screened by default as **worst-of-3 reruns** (~6 `claude` calls/item, run concurrently) so
borderline flags don't flip by luck; pass `--runs 1` for a fast, less stable pass. Items the
engine can't parse are surfaced as `⚠️ unscored`, never silently dropped.

### Optional: cross-family panel (`--multi`)

A single model family judging alone reflects *that* family's priors about students. To
cross-check, list more models in `backends.json` (or a private `backends.local.json` that
overrides it) and add `--multi`:

```bash
python3 report_qc.py --items items.json --out review.md --label "batch" --multi
```

Each item is judged by every **reachable** backend (capability-detected — unreachable ones
are skipped, and it falls back to single-model if fewer than two resolve). The report gains
an `agree` column = how many families independently elevate the item: a **consensus** flag is
high-confidence; a **split** flag is surfaced as a cross-family conflict for the reviewer.
Cross-family spread is reported separately from the within-family rerun envelope — they
measure different things (prior disagreement vs sampling noise). The panel is a generic
judge-ensemble layer with no dependency on any external orchestration tooling; configure
each backend as a plain command template (`{prompt}` placeholder, or `"stdin": true`). Keep
API keys in the environment, never in the config file.

## Input shape

JSON array; copy `batch-template.json`:

```json
{ "id": "...", "standard": "...", "objective": "...",
  "stem": "...", "options": {"a":"...","b":"...","c":"...","d":"..."}, "key": "a" }
```

`key` = the correct option's letter. **If your source lists the correct answer in a fixed
position, shuffle the options first** (Claude Code will do this for you) — otherwise the
position is a trivial cue.

## Output

`review-*.md`: items ranked worst-first, each flagged item with a card —
- **Surface read** (key hidden): what a non-master could exploit
- **Construct read** (key known): which distractors fail, and the misconception they should
  target instead
- **Suggested fix**

## What it can and can't do

- **Can:** predict low discrimination from surface-exploitability and distractors that carry
  no real misconception — the judgment defects a deterministic lint can't catch. Structural,
  rule-shaped tells (an always-A key, grammatical agreement with the stem, length cues) should
  be caught **deterministically**, not here; this screen is for the part that genuinely needs a
  judgment.
- **Can't (yet):** tell you whether real students actually exploit it. The ceiling is
  empirical distractor-selection data; on a bank with outcomes the score becomes a
  calibrated early-warning signal.
- **MCQ only.** Free-response items need a separate rubric-integrity pass.

## Packaging (maintainers)

Build a release with `./package.sh [version]`. It ships **only** an explicit allowlist of
files — test batches, generated `review-*.md`, `__pycache__`, and any audit/forge byproducts
are structurally excluded, never swept in by a `zip -r`. Keep audit output (e.g.
`trust-audit-output/`, cross-model verifier responses) in a sibling folder *outside* this
tree; `package.sh` warns if it finds any here.
