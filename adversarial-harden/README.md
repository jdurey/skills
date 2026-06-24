# adversarial-harden

A skill for hardening code you can't fully trust, by having rival AI models try to break it.

## The problem it solves

I can't really code. So when I need software built, I have AI write it. The hard part is what comes after. The model that writes your code is the worst possible reviewer of it. Ask it to check its own work and it tells you everything looks clean, right up until something breaks in the exact spot it swore was fine.

So I stopped asking it to grade itself.

When a piece of code actually matters, a bug in it that would leak data or let something through that shouldn't, I hand the same code to a few rival model families and tell each one to break it. Their only job is to attack it, and they have to prove the break by actually running it. A model checking its own work shares its own blind spots, and a different family of model is enough of an outsider to find them.

The first time I ran this, one model had already cleared a security hole in code it called clean. A different model caught it on the first try. Same code, same prompt. The only thing that changed was who was looking.

## How it works

It's a **build → harden → integrate** loop:

1. **Build the core yourself** and state the invariants, meaning what must always be true, what's approved, and what would count as a break.
2. **Fan out parallel reviewers from different model families**, each with a distinct angle (precision / false-positive, security / boundary, correctness / concurrency). Every reviewer has to verify findings empirically by running the code.
3. **Get a structured, severity-ranked return**, worst-first, with the exact input, observed vs. expected, and a one-line fix.
4. **Integrate by severity**, and add a regression test for each fix that fails before and passes after.
5. **Re-verify** by re-running the suite and the reviewers' own attacks against the fixed code.

See [`SKILL.md`](./SKILL.md) for the full method, including a standing threat checklist for new code surfaces.

## Install

A skill is just a folder with a `SKILL.md` (YAML frontmatter plus plain-markdown instructions). Any coding agent that loads markdown skills can use it, so this is tool-agnostic. Run the one-liner from inside your agent's skills directory:

```sh
curl -fsSL https://github.com/jdurey/skills/tarball/main | tar -xz && mv jdurey-skills-*/adversarial-harden . && rm -rf jdurey-skills-*
```

That drops an `adversarial-harden/` folder in the current directory. Where "your skills directory" is depends on your tool:

- **Claude Code** → `~/.claude/skills/` (or `.claude/skills/` in a project)
- **Claude Agent SDK** → wherever you point the skills loader
- **Anything else** → the folder your agent reads skills from, or just keep the `SKILL.md` handy and paste it in as a system instruction

No build step, no dependencies. It's a markdown file.

## Why it's public

I built this inside an AI OS I put together to run my own work, and I keep reaching for it. This is a scrubbed, standalone version with none of my private setup in it. It's the first of a few skills I want to write up.
