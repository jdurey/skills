# divergent-solve

A skill for the problems one AI can't crack: throw rival model families at it in parallel, and make them prove the fix against an objective test.

## The problem it solves

I can't really code. So when something breaks, I have AI debug it. Most of the time that's fine. But every so often I hit a problem that one model just can't beat. It gives me a fix, swears it works, and it doesn't. So I ask again, and it produces a brand new root cause with exactly the same confidence as the last wrong one. One model has one blind spot, and it will defend that blind spot all day.

I lost a whole session to this once. The model locked onto a wrong cause, twice, before the real evidence came in.

So now, when a problem starts fighting me, I stop asking one model harder. I write down a pass/fail test first, something a machine can check with no opinion involved. Then I hand the exact same problem to a few different model families at once and let them work it in parallel. Because they were trained on different data, they tend to get stuck in different places, and the one that disagrees with the others is often the one that's right.

Then I trust none of them. I run every proposed fix through my own test, from a clean start, reading the actual logs instead of the model's summary. A model will tell you it passed by ignoring the part that failed. The test doesn't let it.

I keep whichever fix actually passes the test in front of me, no matter how sure the others sounded.

## How it works

1. **Frame the problem and write an objective gate**, a command or check that prints a clear PASS or FAIL with no judgment call.
2. **Fan the same brief out to independent model families in parallel**: a builder, a contrarian, a structural thinker. Different priors, different blind spots.
3. **Verify adversarially**, running every candidate through the gate yourself from a clean state, reading the instrument and not the model's self-report. Assume a false pass until proven otherwise.
4. **Synthesize the winner**: keep the fix that reproducibly passes, and confirm *why* it works before you write the lesson down.

See [`SKILL.md`](./SKILL.md) for the full method.

## Install

A skill is just a `SKILL.md`, which is YAML frontmatter plus markdown, so it works with any agent that loads skills. Run this from your agent's skills directory:

```sh
curl -fsSL https://github.com/jdurey/skills/tarball/main | tar -xz && mv jdurey-skills-*/divergent-solve . && rm -rf jdurey-skills-*
```

That drops a `divergent-solve/` folder in the current directory. For Claude Code that's `~/.claude/skills/`. The method is model-agnostic, so adapt the fan-out to whatever CLIs or model families you have.

## Why it's public

I built this inside an AI OS I put together to run my own work, and I keep reaching for it when a problem won't die. This is a scrubbed, standalone version with none of my private setup in it. It's one of a series of skills I'm writing up.
