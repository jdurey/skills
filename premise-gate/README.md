# premise-gate

I caught an AI system doing flawless work on a fabricated premise. The task passed all three of my quality gates and scored 8 out of 8 on its own verification checklist — but the claim underneath it, that a stakeholder had requested the work, was fiction. Every check pointed at the output. Not one asked whether the justification was true.

Most QC runs three gates: may I do this, should I do this, did it land. This is the fourth: **is the premise itself true?**

It's a small lint script that runs before work starts and flags stakeholder-attribution claims — "X asked for Y", "per Bill's request", "the manager wants" — that carry no provenance tag. When I swept it across 79 of my old planning documents it caught 14 real cases where work had been justified by an attribution nobody could trace.

And I sabotaged it before trusting it: the built-in self-test plants the original laundered premise plus clean controls, and the gate fails loudly if the specimen ever stops flagging.

## What's here

- `lint-premise-gate.sh` — the lint. Deterministic, no model, no network. Recall-biased by design: it over-flags rather than misses, because a false positive costs a review prompt and a false negative launders fiction into executed work.
- `SKILL.md` — the skill instructions (the tagging discipline plus the lint), for agents that load markdown skills.

## Quick start

```sh
bash lint-premise-gate.sh --selftest   # watch it fail on the known-bad specimen first
bash lint-premise-gate.sh my-plan.md   # exit 1 + a list of untagged attribution claims
```

Tag each hit `[VERIFIED: source]`, `[INFERRED]`, or `[ASSUMED → verify]`, and don't let anything act on an unverified "somebody asked for this."

MIT, like everything in this repo.
