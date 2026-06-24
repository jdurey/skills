# skills

Skills I built for my own AI setup, cleaned up and shared.

I can't really code. I have AI write what I need, and over time I've built a set of skills that make that work more trustworthy and less manual. These are the public, standalone versions, with none of my private setup in them.

Each folder is one skill. A skill is just a `SKILL.md`, which is YAML frontmatter plus plain-markdown instructions, so it works with any coding agent that loads markdown skills (Claude Code, the Claude Agent SDK, and similar). No build step, no dependencies. Every skill has a README that explains what it does and why I made it.

## Skills

| Skill | What it does |
|---|---|
| [adversarial-harden](./adversarial-harden) | Hardens code you can't fully trust by having rival AI model families try to break it, then integrating the fixes by severity. |
| [divergent-solve](./divergent-solve) | Cracks a stuck problem by fanning the same brief out to rival model families in parallel, then verifying every fix against an objective pass/fail gate. |
| [witness](./witness) | Turns a heavy task into a self-verifying loop: define done as a list of runnable checks, freeze it, then keep going until every check passes with captured proof. |

## Install any skill

Run this from inside your agent's skills directory (for Claude Code that's `~/.claude/skills/`), swapping in the skill name:

```sh
curl -fsSL https://github.com/jdurey/skills/tarball/main | tar -xz && mv jdurey-skills-*/adversarial-harden . && rm -rf jdurey-skills-*
```

More to come. I write about each one as I publish it.
