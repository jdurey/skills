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
| [ai-proof](./ai-proof) | Strips the tells that make AI writing sound generic: a deterministic linter for the mechanical slop, plus a judgment pass for the rhythm a script can't see. |
| [prompt-architect](./prompt-architect) | Turns a big, fuzzy task into a tight spec an AI can execute faithfully: goal, explicit scope, worked examples, a definition-of-done with a built-in self-check, and HALT conditions. |
| [forge](./forge) | A premise-first ideation engine: validate an idea against live demand before designing it, then generate and stress-test across genuinely independent model families. |
| [scope-first](./scope-first) | Runs a short intake pass before any real task, restating the goal, surfacing ambiguity, and laying out a lean plan, so effort never goes into building the wrong thing well. |
| [voice-profile](./voice-profile) | Captures your authentic writing voice as a reusable rules document pulled from your own writing, then applies it as context so AI drafts sound like you. |
| [heavy-task-planner](./heavy-task-planner) | Forces an efficiency-first planning pass before any heavy build: challenge the framing, compress to an MVP, ground a cost estimate, then write the plan before executing. |
| [grill-me](./grill-me) | Has the AI interview you about your own plan one question at a time, checkpointing every answer to a file, to surface the gaps before you commit. |
| [parallel-research](./parallel-research) | Splits a research task into independent threads, dispatches them to subagents in parallel, then synthesizes the results, routing each thread to the cheapest capable model tier instead of paying top-tier rates for a file listing. |
| [overnight](./overnight) | Runs a multi-step task straight through unattended, resolving every ambiguity with a logged default so it never hangs on a question, and skipping only genuinely unsafe actions to a clean morning review list. |
| [session-handoff](./session-handoff) | Writes a tight, paste-ready summary of the session so you can clear the context and resume in a fresh one without losing your place, sharper and cheaper than an automatic compaction. |
| [construct-validity-screen](./construct-validity-screen) | A runnable tool that predicts which multiple-choice questions won't separate students who know the material from those who don't, before any student sees them, then hands its loud flags to a cross-family panel so only what the models agree on counts as high confidence. |
| [role-bleed-probe](./role-bleed-probe) | A runnable tool that measures how readily an AI agent's reasoning trace slips into narrating its own internal critic, denying its tools, scoring itself, or naming itself in the third person, while it is actively using those tools. It turns that anecdote into a pre-registered monitor-faithfulness rate with frozen detectors and paired controls. |

## Install any skill

Run this from inside your agent's skills directory (for Claude Code that's `~/.claude/skills/`), swapping in the skill name:

```sh
curl -fsSL https://github.com/jdurey/skills/tarball/main | tar -xz && mv jdurey-skills-*/adversarial-harden . && rm -rf jdurey-skills-*
```

More to come. I write about each one as I publish it.
