# Construct-Validity Screen — agent instructions

You are running inside this folder in Claude Code. This is a **pre-data predictor of low
item discrimination** for multiple-choice questions — it flags items where knowing vs.
not-knowing the content doesn't change whether a student gets them right. It reads each item
twice (once with the key hidden, once against its standard) and flags where the two reads
diverge — guessable stems, distractors that map to no real misconception, a second defensible
answer. It is a **loud screen: candidates for human review, not verdicts.** It is not an
item-quality checklist; structural/rule-shaped tells (always-A keys, grammar cues) belong in a
deterministic lint, not here.

## When the user pastes items or points at a file

1. **Format the items** into a JSON array matching `batch-template.json`. Each item:
   `{ "id", "standard", "objective", "stem", "options": {"a","b","c","d"}, "key" }`.
   - `key` is the correct option's letter. If the source always lists the correct answer
     first, **shuffle the option order per item and set `key` accordingly** — otherwise
     "always A" is a trivial cue and the screen is meaningless. (See `scrub` note below.)
   - `objective`/`standard` are optional labels; `stem` + `options` + `key` are required.
   - Save to `items.json` (or any name).
2. **Run it:** `./run-qc.sh items.json "Batch label"`  (or
   `python3 report_qc.py --items items.json --out review.md --label "Batch label"`).
   It uses the local `claude` CLI as a blind solver — ~2 calls per item per run, runs
   concurrently. Default is worst-of-3 reruns (~6 calls/item) to stabilize borderline
   flags; pass `--runs 1` for a fast, less stable pass.
3. **Present the result** from the generated `review-*.md`: the ranked worst-first table,
   then walk the user through the elevated (🔴) items — for each, the surface read (what a
   non-master could exploit), the construct read (which distractors fail and why), and the
   suggested fix. Make clear these are candidates to review, not verdicts.

## If the source lists the correct answer in a fixed position
Shuffle before screening. Quick approach: for each item, randomly permute the four option
texts, write them as a–d, and set `key` to the letter the correct text landed on. This
mirrors runtime answer-shuffling and removes the positional tell.

## Cross-family panel (optional)
If more than one model is configured in `backends.json`/`backends.local.json`, you can run
`./run-qc.sh items.json "label" --multi` (or pass `--multi` to `report_qc.py`) to judge each
item with every reachable family and report their **agreement**. Offer this when the user
wants a trust/consensus check or is sharing the report externally — a consensus flag is
high-confidence, a split flag is a cross-family conflict for the reviewer. It auto-falls back
to single-model if fewer than two backends resolve. It's a generic ensemble layer — no
external orchestration tooling.

## What to tell the user about limits
- It reasons from model priors about students, not real student data. The only ground
  truth for "is this item broken" is empirical distractor-selection rates — a distractor
  no student ever picks is dead weight (screen right); one they pick is functioning (screen
  loud). On a bank *with* outcomes, the divergence score becomes a calibrated signal.
- MCQ only. Free-response items need a separate rubric-integrity pass.
- Single run is non-deterministic on borderline items; the elevated/clean split is stable.

## Files
- `probe.py` — engine (two cold passes + divergence score). Pure stdlib + the `claude` CLI.
- `report_qc.py` — runs the engine over a batch, writes the review report.
- `example-items.json` — a 6-item sample to try immediately: `./run-qc.sh example-items.json "example"`.
- `batch-template.json` — the input shape.
