# overnight

A skill that runs a multi-step task straight through, unattended, without ever stopping to ask a question. You kick it off and walk away; you come back to finished work and one review list, not a prompt that hung at 2am.

## The problem it solves

The failure this exists to kill is a build that stalled waiting for an answer nobody was awake to give. You hand an agent a real task, go to bed, and in the morning it's sitting at "should I use approach A or B?" — having done nothing for six hours. Every minute after that question was wasted.

Overnight flips the default. There is no question to the user for the duration. Every ambiguity gets resolved with the most reasonable default, logged, and passed. The work never halts as a whole. In the morning you read a log of what it did, what it assumed (so you can override), and the short list of things it correctly refused to decide alone.

## How it works

1. **Plan once, up front**, then execute end-to-end with no interactive checkpoints.
2. **Keep a live decision log** — `OVERNIGHT-LOG.md` — with four entry types: `DID`, `ASSUMED` (the question it didn't ask), `DEFERRED` (a thing it deliberately skipped), and `FIXED`.
3. **Verify as it goes.** A step that fails gets a bounded fix attempt; if it still fails, it's deferred and the run moves to independent work rather than blocking.
4. **Hard-stops skip and log, they never hang.** Three things it won't do alone — a confidentiality/data-boundary doubt, an irreversible or outward action you didn't authorize, or a genuine blocker — get logged as `DEFERRED` and the rest of the build continues.
5. **Morning report:** what's done and verified, every assumption you can override, every real decision waiting for you.

Two parts I think are the point. It spends the minimum that still finishes — offloading bulk to scripts, delegating to cheaper tiers, staying on low effort unless a step actually needs more — because nobody's watching the meter overnight. And it refuses to launder a guess into a fact: any output resting on an unverified premise ("they probably wanted this") gets a banner at the top and is never labeled "ready to execute."

It also has a non-colliding mode for when other agents are working the same repo: map who owns what, stay on un-owned files, don't move the baseline others are building on.

## Install

```
curl -fsSL https://github.com/jdurey/skills/tarball/main | tar -xz && mv jdurey-skills-*/overnight . && rm -rf jdurey-skills-*
```

No dependencies. It's just a `SKILL.md`.

## Why it's public

I built this the first time an overnight build hung on a question and lost me a night. It's the discipline that lets me hand off real work and trust that I'll get a finished result plus an honest account of every call it made, instead of a stalled prompt. The version here has none of my private setup in it — just the autonomous-execution protocol, the token discipline, and the hard-stops.
