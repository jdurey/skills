# parallel-research

A skill that splits a research task into independent threads, dispatches them to subagents in parallel, and synthesizes what comes back — instead of grinding through the threads one at a time in a single context window.

## The problem it solves

A lot of research requests are secretly several requests. "Audit these claims and map how these organizations connect" is two jobs that don't depend on each other. Run them sequentially in one context window and two things go wrong: it's slower, and the quality drops as the window fills with the first job's material while the model works the second.

I kept doing this by hand — spinning up separate agents, remembering to launch them in the same turn so they actually ran at once, telling each one exactly what to produce and where to save it, then reading the saved files back to synthesize. Enough of it was mechanical that it belonged in a skill.

## How it works

1. **Decide whether to parallelize.** There's explicit decision logic: split only when the threads are truly independent and don't write to the same place; stay sequential when one thread needs another's output or when it's narrative drafting.
2. **Decompose** the request into distinct threads and match each to the right agent and model tier.
3. **Dispatch all threads in the same turn**, each with a precise scope, an output format, and a save location.
4. **Synthesize** by reading the saved files — not just the returned summaries — and organizing findings by significance, flagging contradictions and gaps.

The part I care most about is the model routing. Discovery that a grep can answer runs as a shell command for zero model tokens; analysis runs on a mid tier; the top tier is reserved for the synthesis at the end. Left unmanaged, every subagent inherits the most expensive model and you pay top-tier rates for a file listing.

## Install

```
curl -fsSL https://github.com/jdurey/skills/tarball/main | tar -xz && mv jdurey-skills-*/parallel-research . && rm -rf jdurey-skills-*
```

No dependencies. It's just a `SKILL.md`. It assumes your agent can spawn subagents and run shell commands; the tier names (Haiku / Sonnet / top) are examples — map them to whatever agent types your setup has.

## Why it's public

This is my default execution mode for anything investigative that has more than one moving part. The standalone version here has none of my own project's entities, files, or agent names in it — just the decomposition logic, the dispatch discipline, and the routing rules that keep it cheap.
