---
name: voice-profile
description: >-
  Build a reusable writing voice profile from a person's own writing, then apply it as a context
  layer before any AI-assisted draft. When invoked without an existing profile, run the intake — ask
  the person for their real samples, extract the patterns, and produce the profile file for them. Use
  when you need AI-written output in someone's own voice: social posts, emails, essays, scripts, or
  any first-person writing where authenticity matters. Pair with a cleanup pass (such as ai-proof)
  after drafting. Do not use for generic or brand copy where a personal voice is not the goal.
---

# Voice Profile

A method for capturing a person's authentic writing voice as a set of reusable rules, then applying those rules as a context layer so any AI-assisted draft starts from something real.

The core problem is that AI writes in its own voice by default. It has preferred rhythms, go-to words, and structural habits it reaches for under any prompt. You can tell it to "write in my voice," but without something concrete to work from, it produces a polished, plausible version of a voice, not the real one. Building a profile once and referencing it every time is how you shift from that default to output that reads like the person actually wrote it.

## How to run this skill

There are two modes. Figure out which one you're in before doing anything else.

- **Build mode** — no profile exists yet for this person. This is the common case. Run the intake (Step 0), extract the patterns (Step 1), and produce the profile file (Step 2).
- **Apply mode** — a profile already exists. Load it and skip to Step 3.

Start by asking: *"Do you already have a voice profile I should use, or should I build one from your writing?"* If they have one, ask for the file or paste, then go to Step 3. Otherwise, run the intake below. Build the profile **per person** — never reuse one person's profile for someone else, and never assume whose voice you're capturing.

## When This Earns Its Cost

- The person writes regularly in their own name and wants consistency across AI-assisted drafts
- They've read AI-generated copy in their voice and felt something was off, even when the content was right
- They work across formats (posts, emails, longer essays) and want a single source of truth for their voice
- They're building a pipeline where multiple drafts go through AI before a human touches them

Skip it for one-off generic copy where a personal voice is not the point.

## The Method

### Step 0: Intake — gather the person's real writing

The skill runs this; it does not tell the person to go do it alone. Ask for raw material and offer easy ways to hand it over:

- **Paste** 5 to 10 pieces they wrote themselves, without AI help, that they're happy with.
- **Point to files** — a folder or file paths you can read directly.
- **Point to public writing** — their posts, blog, or newsletter you can fetch.

Ask for variety: a few short pieces (posts, emails) and at least one longer one (an essay, a script, a long message). The closer the samples are to the format they'll be writing in, the more useful the profile will be.

**Guard against fabricating a voice.** A profile is only as real as the samples behind it. If the person can only produce one or two short snippets, say so plainly: the profile will be thin, and it's better to gather more than to guess. Never pad the profile with patterns you didn't actually observe in their writing — an invented voice is worse than none, because it reads as confident and is wrong.

### Step 1: Extract the patterns

Read through the samples and look for what shows up consistently across multiple pieces, not quirks from one. Work through these categories:

**Sentence structure.** How long are the sentences on average? Short punches or longer flowing ones? Fragments or always full sentences? Do they start sentences with conjunctions (And, But, So)?

**Vocabulary.** What words do they reach for? Are there words they never use? Contractions? Technical terms used without explanation, or always defined?

**Openings and closings.** How does a paragraph start? How does it end? Open with a question, a statement, or a scene? Close with a reflection or a directive?

**Tone.** How is uncertainty handled — hedged, or stated flat? How do they write about failure or difficulty? Is there a consistent emotional register across pieces?

**Things they avoid.** As important as what they do. List specific constructions, phrases, or rhythms that never appear. The avoidance list is what stops the AI from defaulting back to its own habits.

Write all of this down as rules an AI can follow. Describe what they *actually wrote* in the samples, not what they aspire to write.

### Step 2: Write the profile file and confirm it

Produce a single file holding the rules from Step 1. Structure it however fits the voice, but keep it readable in a few minutes — it gets pasted into context often. Include a short section of **raw examples**: 3 to 5 sentences or short paragraphs pulled directly from the source material. When an AI has both the rules and real examples, the output is more accurate than rules alone.

A good profile is 300 to 600 words. Shorter misses nuance; longer dilutes the signal.

Then show it to the person and ask them to sanity-check it: *"Does this read like the rules of how you actually write?"* Correct anything that sounds like aspiration rather than observation. The person's confirmation is what turns a plausible profile into a real one.

### Step 3: Apply as a context layer

Before any writing task where the voice matters, put the profile into the model's context *before* the request. The simplest version is a preamble: paste the profile, then give the writing task. If there's a system prompt or a persistent context block, the profile belongs there. The goal is that the model has the rules in front of it when it generates the first word, not as an afterthought revision.

### Step 4: Pair with a cleanup pass

A voice profile gets you most of the way. AI still has its own rhythms it falls back on, especially in longer pieces. Running the output through a cleanup pass (such as the ai-proof skill in this series) strips the generic patterns out after the draft is done. Voice profile sets the target; cleanup removes what doesn't belong.

### Step 5: Maintain the profile

Voice drifts over time. Every six months or so, read a few recent pieces the person is happy with and check whether the profile still matches. Update any rules that feel off. It's a living document, not a one-time setup.

---

## One-Paragraph Version

When asked for someone's voice and no profile exists, run an intake: ask for 5 to 10 things they actually wrote, read them, and extract the consistent patterns (sentence length, vocabulary, openings, closings, tone, avoidances). Write those down as explicit rules with a few raw examples as anchors, and confirm the file with the person before trusting it. Put the profile into the model's context before every writing task in their voice, then follow with a cleanup pass. Review it periodically so it stays accurate. Never fabricate a voice from too little material.
