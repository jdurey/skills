# divergent-solve

A skill for the problems one AI can't crack: throw rival model families at it in parallel, and make them prove the fix against an objective test.

## The problem it solves

I can't really code, so when something breaks I get an AI to fix it. Most of the time that's enough. But every so often I run into a problem a single model simply can't solve, and the real trouble is that it won't concede the point. It hands me a confident fix and declares the matter closed, and the fix doesn't work. So I ask again, and it produces an entirely different explanation, delivered with the same certainty as the wrong one before it.

The underlying problem is that one model has essentially one way of being wrong. It will defend that blind spot indefinitely, no matter how many times I push back.

So I stopped leaning harder on a single model. I write a small, objective test that a computer can score, so the result comes back as an unambiguous pass or fail. Then I hand the identical problem to three different model families at once and let each one work it independently. Because they were trained by different labs on different data, they rarely get stuck in the same place. The model that breaks from the consensus is, surprisingly often, the one that turns out to be right.

I don't take any of them at their word. Every proposed fix gets run through the test on a clean machine, and the raw output matters more than the model's cheerful summary of it. A model will gladly announce success while omitting the one line that proves it failed. The test is the only authority worth trusting.

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
