# scope-first

Run a short intake-and-plan pass before any real task, so you don't build the wrong thing well.

## The problem it solves

I used to start immediately. A request would come in, it would look clear, and jumping straight to work felt responsible. The problem was that "looks clear" is not the same as "is clear," and several steps into execution I'd realize I was solving a slightly different problem than the one that was actually wanted, at the wrong scope, in the wrong format.

By then it was too late to recover cheaply. Undoing confident, thorough work on the wrong question costs more than a 30-second pause at the start would have. So I stopped treating the impulse to start immediately as a virtue.

The framing that stuck: the most expensive mistake in AI-assisted work isn't picking a slightly heavier tool. It's doing the wrong work well. A brief intake at the start addresses that. It restates the goal, surfaces any real ambiguity, recommends an appropriate level of effort, and lays out a lean plan. Then it waits for a green light before anything gets built.

A few things I've learned about running it well. Keep it short. Three labeled sections, a few lines each. Don't invent questions when the ask is already clear. Only surface ambiguity that would actually change what you build. And watch for the failure mode where the scope keeps contracting toward whatever is easiest to produce. When you notice it, stop and re-confirm the actual goal.

## How it works

1. **Calibrate depth.** Trivial lookups, quick facts, and single-step answers get answered directly. Anything multi-step, any deliverable, or anything with even slight ambiguity in scope or format triggers the intake.
2. **Restate the goal.** One or two sentences on the outcome, not the steps. Surface any genuine forks ("one-off vs. reusable?", "quick summary vs. deep analysis?"). Don't manufacture questions when the ask is clear.
3. **Recommend effort.** Name the approach and give a one-line rationale. If the task has a cheap bulk phase and an expensive judgment phase, name them separately.
4. **Sketch a lean plan.** Short numbered steps. Flag deterministic work that should run in code rather than reasoning over raw bulk. Give a rough size estimate.
5. **Stop and wait.** Don't execute until the person confirms or adjusts. The intake is cheap; the rework is not.

See `SKILL.md` for the full method.

## Install

```
curl -fsSL https://github.com/jdurey/skills/tarball/main | tar -xz && mv jdurey-skills-*/scope-first . && rm -rf jdurey-skills-*
```

## Why it's public

I built this inside an AI OS I put together to run my own work. It started as a personal rule I kept forgetting to follow, and at some point I wrote it down formally so I could hand it off to the AI and stop enforcing it manually. This is a scrubbed, standalone version with none of my private setup in it. It's one of a series of skills I'm writing up.
