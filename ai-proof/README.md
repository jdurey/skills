# ai-proof

A two-pass skill for removing AI writing-tells from any prose.

## The problem it solves

My writing kept coming back sounding like everyone else's. I'd hand a draft to an AI, ask it to improve the language, and get back something that flowed but felt like nothing in particular. Easy to read, easy to forget.

The underlying problem is perplexity. AI text is statistically predictable: the model picks word choices that are common given what came before. That produces smooth prose, but smooth in a way that doesn't belong to anyone. Human writers phrase things in ways that are slightly off from what you'd predict, because the phrasing comes from how they actually think.

I started keeping a list of the patterns that gave it away. Vocabulary that AI overuses until it's drained of meaning. Formal transitions that no human reaches for in conversation. Sentence rhythms that stay too even for too long. Structural templates: the tricolon, the clean landing, the terse reversal punch. The more I cataloged them, the clearer it became that there were two kinds of fix: the ones with one right answer (always delete "delve into," always convert em-dashes to commas), and the ones that require reading and deciding.

So I split the process in two. A linter handles the deterministic pass. Then a set of judgment categories handles the rest.

## How it works

1. Run `scripts/lint.py` on the draft. It auto-fixes the hard bans and prints a list of flagged patterns with line numbers. Each flag is a pointer; the rewrite is yours to do.
2. Work through the judgment categories in `SKILL.md`: perplexity (word-level predictability), burstiness (sentence rhythm), structural tells (tricolons, clean landings, manufactured symmetry), and perplexity injection (techniques for making a passage feel like a person thinking).
3. Re-run the linter. The gate is zero flags and a Flesch-Kincaid grade between 6 and 9. If something still doesn't sound right after passing the gate, trust your ear over the tool.

The linter is fast and free to run; the judgment sweep is where the actual work happens. A draft that passes the linter can still read as generic. The categories in `SKILL.md` are the part worth spending time on.

## Install

```
curl -fsSL https://github.com/jdurey/skills/tarball/main | tar -xz && mv jdurey-skills-*/ai-proof . && rm -rf jdurey-skills-*
```

Requires Python 3.6 or later. No dependencies beyond the standard library.

## Why it's public

I built this as part of an AI OS I put together to run my own work. It started as a private finishing layer and turned into something I reach for on everything I publish. The scrubbed, standalone version here has none of my personal voice profile or private setup in it, just the method for identifying and removing AI writing-tells, generalized so anyone can apply it to their own writing. It's one of a series of skills I'm writing up.
