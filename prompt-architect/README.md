# prompt-architect

Turn a big, fuzzy task into a tight spec an AI or a person can actually execute faithfully.

## The problem it solves

I kept handing off large tasks with a paragraph of description, and the AI would do exactly what I said. Which turned out not to be what I meant. Not because it was careless, but because a loose description leaves a lot of room for interpretation, and models fill that room with confidence.

A structured spec fixed it almost immediately. Not a longer brief, a better-shaped one. Goal and definition of done at the top. An explicit out-of-scope list collected in one place. Worked examples instead of another page of rules. A self-verification step so the executor checks its own work before returning. HALT conditions so it stops and surfaces a problem instead of improvising around one.

The sections I use now mostly exist because I watched something break without them. A conflict-resolution rule is in there because I had two instructions contradict each other and the model picked the wrong one without saying anything. Failure history is in there because the second version of a prompt keeps re-discovering the same bugs the first version hit.

The underlying idea is that structure carries more weight than length. A well-shaped two-page spec beats a rambling paragraph, and it beats a ten-page wall of prose that no executor will read evenly.

## How it works

1. **Interview for load-bearing unknowns only.** Ask only for what changes the output: goal and definition of done, who executes it and with what tools, hard constraints, source material, output format, and what's explicitly out of scope. Assume sensible defaults for the rest.

2. **Draft with the most critical elements first.** Goal and definition of done go at the top. Scope in and scope out collected in one place. Glossary. Source-of-truth anchors with a "check against source, don't paraphrase" instruction. Numbered rules, one idea each. Worked example with exact input and output.

3. **Add the sections people skip.** HALT conditions with a named diagnostic format. An ambiguity default. A conflict-resolution rule. Checkpoint design for long-running prompts. For v2+ prompts, a "why this version exists" section that names what broke before and why.

4. **Run the self-audit before delivering.** The `SKILL.md` has a checklist; run every item, fix any "no," then deliver as a file the executor can paste or run directly.

See `SKILL.md` for the full method and template.

## Install

```
curl -fsSL https://github.com/jdurey/skills/tarball/main | tar -xz && mv jdurey-skills-*/prompt-architect . && rm -rf jdurey-skills-*
```

## Why it's public

I built this inside an AI-assisted workflow system I put together to run my own work. The private version has hooks for specific internal tooling and session patterns. This is a scrubbed, standalone version with none of that in it, just the method, which works on its own regardless of what you're using to run AI tasks. It's one of a series of skills I'm writing up.
