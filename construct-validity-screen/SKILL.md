---
name: construct-validity-screen
description: Predict which multiple-choice questions won't separate students who know the material from those who don't, BEFORE any student sees them, by reading each item twice cold — once with the answer key hidden (what a guesser could recover from the surface) and once against the standard it claims to measure — and flagging where the two reads diverge: guessable stems, distractors that map to no real misconception, a second defensible answer. It is a LOUD screen that produces candidates for human review, not verdicts, so it pairs with an optional cross-family judge panel that keeps only the flags independent model families agree on. Use to triage an MCQ item bank for low-discrimination items, to sanity-check questions before piloting them, or whenever you want a trust/consensus read on item quality before spending real test-taker time. MCQ only; free-response needs a separate rubric-integrity pass.
---

# Construct-Validity Screen — predict the dud questions before students do

A good multiple-choice question separates the students who know the material from the ones who don't. A bad one looks fine and fails silently: the stem gives it away, the wrong answers are ones nobody would pick, or there are two defensible right answers. Students land it without knowing a thing, and the test learns nothing about them. You can catch a lot of that **before a single student sees the question** — and that is what this screen does.

It reads each item **twice, cold**. Once with the answer key hidden, to see what a non-master could recover from the surface alone. Once against the standard the item claims to measure, to see what it should actually take to get right. Where the two reads **diverge**, it flags the item. This is a prediction of one psychometric property — discrimination — not a generic item-quality checklist, and not a per-topic rule list.

**It is a loud screen: candidates for human review, not verdicts.** "Distrust the zero, distrust the hit." Because it is tuned to over-flag, it pairs with a different-family adjudicator so only confirmed findings reach a builder and the gate does not cry wolf.

## When it's worth it (and when it isn't)
- **Worth it:** triaging an MCQ bank for low-discrimination items, sanity-checking questions before a pilot, or getting a trust/consensus read before spending real test-taker time.
- **Not here:** structural, rule-shaped tells — an always-A key, grammatical agreement with the stem, length cues — should be caught **deterministically** by a lint, not by a judgment model. This screen is for the part that genuinely needs judgment.
- **MCQ only.** Free-response items need a separate rubric-integrity pass.

## How to run it
The tool ships as a small Python engine (stdlib only) that uses a local `claude` CLI as a blind solver — no API key, no install.

1. **Format the items** into a JSON array (copy `batch-template.json`). Each item:
   `{ "id", "standard", "objective", "stem", "options": {"a","b","c","d"}, "key" }`.
   `key` is the correct option's letter. **If your source always lists the correct answer in a fixed position, shuffle the options per item first** — otherwise the position is a trivial cue and the screen is meaningless.
2. **Run it:** `./run-qc.sh items.json "Batch label"` (or `python3 report_qc.py --items items.json --out review.md --label "Batch label"`). Default is worst-of-3 reruns (~6 calls/item, run concurrently) so borderline flags don't flip by luck; pass `--runs 1` for a fast, less stable pass. Unparseable items are surfaced as `⚠️ unscored`, never silently dropped.
3. **Read the result** from the generated `review-*.md`: items ranked worst-first, each flagged item with a card — the **surface read** (what a guesser could exploit), the **construct read** (which distractors fail and the misconception they should target instead), and a **suggested fix**. Present these as candidates to review, not verdicts.

## Optional: cross-family panel (`--multi`)
A single model family judging alone reflects *that* family's priors about students, and it over-flags. To cross-check, list more models in `backends.json` (or a private `backends.local.json` that overrides it) and add `--multi`:

```bash
python3 report_qc.py --items items.json --out review.md --label "batch" --multi
```

Each item is judged by every **reachable** backend (capability-detected — unreachable ones are skipped, and it falls back to single-model if fewer than two resolve). The report gains an `agree` column: a **consensus** flag (families independently elevate it) is high-confidence; a **split** flag is surfaced as a cross-family conflict for the reviewer, not summed into a fake verdict. Cross-family spread is reported separately from the within-family rerun envelope — they measure different things (prior disagreement vs sampling noise). The panel is a generic judge-ensemble layer: configure each backend as a plain command template (`{prompt}` placeholder, or `"stdin": true`), and keep API keys in the environment, never in the config file.

## What it can and can't do
- **Can:** predict low discrimination from surface-exploitability and distractors that carry no real misconception — the judgment defects a deterministic lint can't catch.
- **Can't (yet):** tell you whether real students actually exploit it. The ceiling is empirical distractor-selection data; on a bank *with* outcomes, the divergence score becomes a calibrated early-warning signal.

See `README.md` for input shape, output format, and packaging notes.
