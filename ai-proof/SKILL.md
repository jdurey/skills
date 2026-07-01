---
name: ai-proof
description: A two-pass finishing layer that removes AI writing-tells from any text. Use it after any draft exists — LinkedIn posts, articles, essays, scripts, or any other prose meant to read as genuine. The first pass is a deterministic linter that auto-fixes hard bans and flags patterns with line numbers. The second pass is judgment-driven rewriting guided by categories of slop the linter can't fully catch. Run it on anything you care about before it goes out.
---

# AI-Proof

A finishing layer for prose. It runs after a draft exists and removes the specific patterns that mark text as machine-generated. There are two passes: a deterministic linter that handles what has one right answer, and a judgment sweep that handles what requires reading and deciding.

The core problem is perplexity. AI generates text by choosing statistically predictable words and structures. The result flows smoothly but reads as generic — assembled from the most common version of each sentence rather than from how a person actually thinks. Raising perplexity means making choices that are specific, unexpected, or slightly off from what a reader would predict. This skill is designed to do that systematically.

Always run the linter first, then apply judgment. The script handles the rules with one right answer; you handle the rewrites that need a brain.

---

## Pass 1 — Run the Linter

Run `scripts/lint.py` on your draft first. It handles the part of ai-proofing that has one right answer.

**Auto-fixed automatically:**
- Em-dashes and en-dashes converted to commas
- The word "quiet/quietly" removed (a hard ban — AI uses it to make flaws sound ominous rather than naming them plainly)

**Flagged with line numbers for rewriting:**
- Drained vocabulary: words AI overuses to signal importance without delivering it (crucial, robust, leverage, delve, tapestry, seamless, and others)
- Formal transitions: Furthermore, Moreover, Additionally, In conclusion, Therefore, Thus, and similar
- Hedge openers: "It's worth noting that," "It's important to understand that," and similar wrappers
- Meta-commentary: announcing the writing instead of doing it ("In this post, I will...")
- AI slop openers and intrigue frames: formulaic hooks ("Here's why," "The thing is," "What they don't tell you is," "the part nobody warns you about") and fake summative landings ("that's the whole point")
- Pseudo-cleft reframes: "What I've gotten better at is X" instead of "I've gotten better at X"
- Manufactured symmetry: "not only X but also Y," "it's not X, it's Y" (including the cross-sentence form "It isn't A. It's B."), and the quantifier swing ("Almost everyone can X. Far fewer can Y.")
- The "X, not Y" antithesis and the imperative reversal ("Don't ask whether it works. Ask someone to prove it doesn't.")
- Rhythm echoes: doubled "just as X, just as Y," a repeated adverb for balance, and "First I… then I…" scaffolding
- Anaphora runs: three or more consecutive sentences opening with the same word
- Low burstiness: five or more consecutive sentences all in the 10-20 word range
- Readability: Flesch-Kincaid grade reported every run; flagged outside the 6-9 band

```
python3 scripts/lint.py path/to/draft.txt
python3 scripts/lint.py path/to/draft.txt --write   # applies autofixes to the file
python3 scripts/lint.py path/to/draft.txt --json     # machine-readable flags for a pipeline
```

Requires Python 3.6+ and nothing else — standard library only.

The linter is the floor. A draft with zero flags can still read as slop. Pass 2 is where the real work happens.

---

## Pass 2 — Judgment Sweep

Work through these categories in order. The linter points; you rewrite. Most of these require reading the text.

### 1. Perplexity: word-level predictability

Replace words that AI overuses. The full list is in `references/ai-marker-vocabulary.md`. Common offenders:

| Flagged | Fix |
|---|---|
| ensure / ensure that | Say what actually happens. "This ensures X" → "X happens." |
| delve into | Cut it. Start the sentence. |
| crucial / critical without specifics | Name the consequence: "Skip this and Y breaks." |
| utilize | Use "use." Always. |
| facilitate | Replace with the actual verb. |
| robust | Cut or replace with something measurable. |
| innovative / cutting-edge | Cut entirely. |
| leverage (business sense) | Never. |
| comprehensive | Name the actual scope. |

Also break predictable word pairs: "significant impact," "rich learning experience," "meaningful engagement," "deep understanding." These feel smooth and say nothing. Name the specific thing.

Vary sentence openers. If three or more sentences in a row start with "The," "This," "It," or "In," break the pattern.

### 2. Burstiness: sentence rhythm

Human writing varies sentence length dramatically. AI clusters around 12-18 words per sentence.

Flag any stretch of five or more sentences where all are in the 10-20 word range. Break it by shortening one sentence or expanding another.

Target readability: Flesch-Kincaid grade 6-9, sweet spot around 8. The linter reports this on every run. To raise a grade that's too low, combine some short sentences; to lower one that's too high, shorten sentences and swap multi-syllable words for plain ones. Depth lives in the ideas, not in long sentences or Latinate vocabulary.

### 3. Structural tells

These require paragraph-level or sentence-level rewrites.

**Formal transition words** — Furthermore, Moreover, Additionally, In conclusion, Therefore, Thus, Hence, Consequently, Nevertheless, Nonetheless. Replace with And, But, So, or just start the new sentence.

**Hedge clusters** — "It's worth noting that," "It's important to understand that," "It should be noted that." Delete the opener. Start with the statement.

**Meta-commentary** — "In this post I will," "Let's explore," "Let's unpack." Delete the announcement. Start with the thing.

**AI slop frames** — "Here's why," "The thing is," "What they don't tell you," "the part nobody warns you about," "the kind where." These promise a secret instead of delivering content. State the thing directly.

**Fake summative landings** — "That's the whole idea," "That's the beauty of it." The narrator announces the takeaway instead of letting the content land it. Cut it, or replace with the actual point.

**Tricolons** — three perfectly parallel items in a list, three consecutive sentences with the same opener, three rhetorical questions. Two is human; three is a template. Cut the third, make it grammatically different, or add a specific detail that makes it uneven.

**Long enumeration lists** — four or more comma-separated items in one sentence flag as AI regardless of how specific each item is; the uniform structure across that many items is rare in human writing. Distribute the items across prose: describe two naturally, fold one into a subordinate clause, move the rest into a differently-shaped sentence — or name the most important two or three and cut the rest.

**Clean landings** — a short, thematically resolved summation at the end of a passage. AI produces these every time. If a landing feels too closed, add a small complication before or after it, or replace the resolution with something slightly less finished.

**Terse reversal punches** — "It looked clean. It wasn't." A setup followed by a clipped reversal. AI's most overused rhythm. Fold the reversal into the sentence or drop it.

**The "X, not Y" swing** and **the quantifier swing** — "I keep the fix that passes, not the one that sounds certain." / "Almost everyone can generate something. Far fewer can sit with their own output." Manufactured antithesis, one within a sentence and one spread across two. Make it one plain claim.

**The imperative reversal** — "Don't ask whether it works. Ask someone to prove it doesn't." A negated command followed by the same verb as a positive command. Give one straight instruction instead.

**Passive voice clusters** — one passive is fine; three in a paragraph signals AI. Find the human agent and make them the subject.

**Statistics piles** — three or more data points in consecutive sentences, even accurate ones, read as AI evidence-piling. Break the pile with two or three sentences of narrative or observation before the next figure — a single interjection isn't enough.

**Section-template announce language** — "This chapter examines," "This section establishes." AI uses this formula for every section. Either invert it (put the specific content first, drop the meta-claim) or cut it entirely.

**Section-template repetition** — when three or more consecutive entries (comp titles, chapter descriptions, bios) follow the same internal structure, vary the length and sentence order across entries so a reader can't predict the shape of the next entry from the previous one.

**Compound-complex chains** — three or more consecutive sentences that each pair an independent clause with a subordinate clause and a clean resolution. Humans don't produce them in unbroken runs. Break one into two simple sentences, or drop a short declarative between them.

**Rhythm slop** — after stripping lexical slop, prose can develop rhythmic slop: relentlessly balanced and punchy, every point landing with the same structure. Read the piece aloud. If it sounds like a polished keynote, the rhetorical architecture has become its own tell. Plainer beats punchier.

### 4. Fabricated specificity and inconsistent timelines

AI invents concrete-sounding detail to make a story vivid, and the invented details don't cohere. The classic tell is a timeline that jumps: "Last week…" in the opener, then "I lost a whole afternoon to this once," then "a problem that had beaten me for an hour." Three time frames for one event, none of them real.

Don't invent timestamps, durations, counts, or scene details you don't actually have. Pick one true frame and hold it, or stay honestly unspecified. Specificity earns trust only when it's real; fabricated specificity that contradicts itself destroys it.

### 5. Perplexity injection

When a passage reads as too smooth, use these to break it:

- Replace a generic noun with a real one. "A user" → the actual name or role.
- Add a mid-sentence self-correction. AI doesn't second-guess itself mid-thought. Humans do.
- Drop to a more casual register briefly. Humans shift register; AI stays flat.
- Replace an abstract claim with a situational anchor. The specific scene raises perplexity.
- After making a point, resist the expected conclusion. Introduce a wrinkle or a qualification.

---

## What this skill is NOT

It doesn't make writing deliberately strange to fool a detector. The goal is to write the way a specific person actually thinks and talks — which happens to produce text that reads as human, because the patterns are genuinely theirs. If a sentence is already strong, don't touch it. Fix what's broken, not everything.

---

## One-line version

Run the linter to fix what has one right answer, then read the text and rewrite what doesn't — the rhythm, the structure, the collocations, the landings — until it sounds like a person thinking rather than a model assembling.

## Reference

For the full vocabulary blacklist with replacement guidance: `references/ai-marker-vocabulary.md`
