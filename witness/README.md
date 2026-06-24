# witness

A skill for the work that isn't done until it's proven done: define success as a list of checks a computer can run, freeze it, then loop until every check passes with the evidence to show for it.

## The problem it solves

I kept running into the same problem with AI doing my work. It would tell me something was finished when it only looked finished. The page rendered, so it called the job shipped, with no actual check behind the claim, just a confident "done."

The failure mode is declaring victory early. "Looks complete" is not the same as complete, and by eye I'd sign off on things a real test would have caught. So I stopped letting "looks done" count for anything.

Now, before the work even starts, I make it write down what done actually means, as a list of checks a computer can run. Instead of "the writing reads well," the line has to say "passes the writing linter with zero flags." Instead of "the build works," it says "the command exits clean." Every item carries a test, or it doesn't earn a place on the list. Then the list gets frozen, and the loop refuses to stop until every line on it comes back green.

The honest version of done turns out to be slower and a good deal less flattering than the one a model hands you. I trust the list more than I trust the model announcing that it finished.

## How it works

1. **Derive checkable criteria.** Decompose "done" into success criteria, and attach an objective check to each one: a command, a file that must exist, a count that must match, a gate that must pass. Convert vibes into proxies — "reads well" becomes "passes the linter with no flags."
2. **Gate the premises first.** Before any quality criterion closes, confirm the load-bearing assumptions the task rests on — especially "X asked for Y." A plan can score full marks on craft while resting on a request nobody made.
3. **Sign off once.** Present the criteria table, take edits, then freeze it. That's the only checkpoint.
4. **Loop work-and-verify.** Each round, actually run every check and capture the real output. A criterion is done only when its check passes in the current state, not because it passed earlier. Keep going until all of them are green.
5. **Report the proof.** End with an evidence table: criterion → check → captured result. The proof, not a summary of it.

See [`SKILL.md`](./SKILL.md) for the full protocol.

## Install

A skill is just a `SKILL.md`, which is YAML frontmatter plus markdown, so it works with any agent that loads skills. Run this from your agent's skills directory:

```sh
curl -fsSL https://github.com/jdurey/skills/tarball/main | tar -xz && mv jdurey-skills-*/witness . && rm -rf jdurey-skills-*
```

That drops a `witness/` folder in the current directory. For Claude Code that's `~/.claude/skills/`. The method is tool-agnostic, so swap in whatever checks, linters, and gates you have.

## Why it's public

I built this inside an AI setup I put together to run my own work, and I keep reaching for it whenever the cost of a premature "done" is high. This is a scrubbed, standalone version with none of my private setup in it. It's one of a series of skills I'm writing up.
