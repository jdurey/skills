# gate-canaries

Ship a small canary test suite alongside any LLM gate, so "it ran once and
nothing broke" stops counting as tested.

## Why I made this

I audited my own automation and found five LLM gates shipped in eight days —
a fact-check gate on a content feed, a work-queue admission classifier, and
friends — every one of them "proven" by a single live run. Each one that later
misbehaved cost about two hours to diagnose, patch, and re-fire, always at a
worse time than authoring time.

The fix was a standing rule, and this skill is that rule packaged: an LLM gate
ships with 3–5 canary cases beside it, and a green run is part of "done."

Two details do most of the work:

- **Must-refuse cases.** A gate that approves everything and a gate that
  rejects everything both look fine in a demo. The suite has to include inputs
  the gate must reject — including one that tries prompt injection against the
  judge itself — plus one over-refusal guard it must pass.
- **Never copy the gate prompt into the test.** Copies drift. The provider runs
  the real gate hermetically (sandbox its filesystem via env overrides) or loads
  the same prompt file the gate loads, so the thing under test is always the
  thing in production.

The first suite I built with this pattern runs four canaries against a live
web-grounded judge in about 70 seconds. It confirmed the judge refuses a
fabricated brand, refuses token-project hype, refuses an embedded injection,
and still approves a real, documented claim.

## Use it

Drop `SKILL.md` into your agent's skills directory and invoke it when you write
or change a gate. It works with any agent that loads markdown skills; the suite
it produces runs on [promptfoo](https://promptfoo.dev), which is a free CLI.
