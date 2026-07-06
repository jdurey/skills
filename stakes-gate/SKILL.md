---
name: stakes-gate
description: Put a deterministic floor under an autonomous system's judgment calls. A model loaded with your recorded decision policy PROPOSES a verdict on an escalated action; a script the model cannot see or edit ENFORCES the limit around it — outward or irreversible stakes always route to a human, out-of-range confidence fails closed, novel situations hit the human floor. Use when an agent needs room to act autonomously on routine internal calls without ever owning the final say on consequential ones. Trigger on "add a stakes gate", "the model shouldn't have the final say", "graduated autonomy", "gate this decision", or any design where an AI's confident reasoning could otherwise talk its way past a safety limit.
---

# Stakes Gate

The question this skill answers is not "is the model smart enough to be trusted with the decision?" It is "who owns the final call when the model and the limit disagree?" Here the answer is structural: the model drafts the judgment, and a deterministic layer it cannot see or edit enforces the envelope around it.

## The two layers

1. **Prediction** — a model loaded with your policy canon (your recorded past decisions, one dimension per class of call) reads the escalated request and proposes one verdict line: `VERDICT<TAB>confidence<TAB>dimension<TAB>reason`.
2. **The wall** — `stakes-gate.sh` takes that proposal and checks it against limits the model never touches:
   - **Outward / irreversible / unknown stakes always resolve to ASK** (the human floor), regardless of predicted confidence. Only an explicit `internal-reversible`-class token opens the auto-act lane.
   - **Confidence must be a number in [0, 1].** Anything else — `1.7`, `99`, `banana` — is clamped to 0 and fails closed. This is not hypothetical: an out-of-range confidence walking through the wall was a real bypass found by adversarial review, and `stakes-gate-test.sh` keeps it dead.
   - **Novel dimensions go to the human.** If the request matches nothing in the recorded policy, no prediction is trusted.
   - **A broken judge is a human, not a pass.** Empty output, no verdict line, non-zero exit — all ERROR, which routes to the operator.

## Run it

```sh
export STAKES_GATE_POLICY=path/to/policy.md   # your recorded decisions; see policy-example.md
bash stakes-gate.sh judge --request request.txt --stakes internal-reversible
# exit 0 = APPROVE/EDIT (auto-act lane) · 1 = REJECT · 3 = ASK a human · 4 = error (also a human)
```

Every human override feeds the flywheel, so the canon sharpens over time:

```sh
bash stakes-gate.sh learn --dimension BACKUPS --said REJECT --did approve --rule "retention pruning is routine"
```

## Verify it before trusting it

```sh
bash stakes-gate-test.sh   # hermetic — a stub judge, no model, no network; exit 0 = all green
```

A guard you have never watched fail hasn't earned its green light: the suite includes the found bypass (case 3) specifically so the gate can demonstrably refuse it.
