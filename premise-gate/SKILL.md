---
name: premise-gate
description: Validate a task's PREMISES before any work starts — the fourth gate class almost nobody runs. Most QC asks "may I do this?", "should I do this?", and "did it land?"; none of those ask "is the justification TRUE?". This skill tags every load-bearing claim in a plan or definition-of-done with provenance ([VERIFIED: src] / [INFERRED] / [ASSUMED → verify]) and runs a recall-biased lint that flags stakeholder-attribution claims ("X asked for Y") carrying no source. Use before acting on any plan that justifies work by what someone supposedly requested, before autonomous/overnight runs, and when auditing old planning docs for laundered premises. Trigger on "premise gate", "is this premise sourced", "who actually asked for this", or "lint the plan for untagged claims".
---

# Premise Gate

Output validation without input validation is theater: you can grade an answer perfectly and still be grading the answer to a question nobody asked. This gate exists because an autonomous run once laundered an inference ("M is probably missing X") into a stated fact ("M asked for X"). The work passed permission checks, judgment checks, and outcome checks — it scored a perfect definition-of-done — and a human acted on a request that never existed.

## The rule

Every load-bearing premise in a plan, definition-of-done, or task justification carries exactly one provenance tag:

- `[VERIFIED: <src>]` — an externally checkable source: a linked message, doc, ticket, observed event.
- `[INFERRED]` — a reasoned guess, explicitly not confirmed.
- `[ASSUMED → verify]` — taken as true pending a named check.

The highest-risk class is **stakeholder attribution** — "X asked / wants / needs / told us / expects Y". These must be `[VERIFIED: src]` or be downgraded to `[INFERRED]` before anyone acts on them.

## The lint

```sh
bash lint-premise-gate.sh plan.md          # prints untagged attribution claims; exit 1 if any
bash lint-premise-gate.sh --selftest       # the frozen failure specimen MUST flag; clean controls MUST pass
bash lint-premise-gate.sh -q plan.md       # exit code only
```

It is **recall-biased on purpose**. A false positive costs a "review this" prompt; a false negative launders a fabricated premise into executed work — the expensive error. The precision lever is the subject: "the build requires X" never flags; "the manager requires X" always does.

It is also a **soft gate**: a hit means "verify or tag this premise before the plan is trusted," not a hard refusal.

## Sabotage it before trusting it

Run `--selftest` first, and feed it a known-bad plan of your own. A guard you have never watched fail hasn't earned a place in your pipeline. The self-test plants the original laundered premise and fails the whole gate if that specimen ever stops flagging.
