---
name: voice-profile
description: Build a reusable writing voice profile from your own writing and apply it as a context layer before any AI-assisted draft. Use when you need AI-written output in your own voice: social posts, emails, essays, scripts, or any first-person writing where authenticity matters. Pair with a cleanup pass (such as ai-proof) after drafting. Do not use for generic or brand copy where a personal voice is not the goal.
---

# Voice Profile

A method for capturing your authentic writing voice as a set of reusable rules, then applying those rules as a context layer so any AI-assisted draft starts from something real.

The core problem is that AI writes in its own voice by default. It has preferred rhythms, go-to words, and structural habits it reaches for under any prompt. You can tell it to "write in my voice," but without something concrete to work from, it produces a polished, plausible version of a voice, not yours. Building a profile once and referencing it every time is how you shift from that default to output that reads like you actually wrote it.

## When This Earns Its Cost

- You write regularly in your own name and want consistency across AI-assisted drafts
- You've read AI-generated copy in your voice and felt something was off, even when the content was right
- You work across formats (posts, emails, longer essays) and want a single source of truth for your voice
- You're building a pipeline where multiple drafts go through AI before you touch them

Skip it for one-off generic copy where your personal voice is not the point.

## The Method

### Step 0: Gather source material

Pull together 5 to 10 pieces you actually wrote, without AI help, that you're satisfied with. Aim for variety: a few short pieces (posts, emails) and at least one longer one (an essay, a script, a long message). These are your raw material. The closer they are to the format you'll be writing in, the more useful the profile will be.

### Step 1: Extract the patterns

Read through your source material and look for what shows up consistently. You're after patterns across multiple pieces, not quirks from one.

Work through these categories:

**Sentence structure.** How long are your sentences on average? Do you use short punches or longer flowing ones? Do you write in fragments or always full sentences? Do you start sentences with conjunctions (And, But, So)?

**Vocabulary.** What words do you reach for? Are there words you never use? Do you use contractions? Do you use technical terms without explaining them, or do you always define them?

**Openings and closings.** How do you start a paragraph? How do you end one? Do you open with a question, a statement, or a scene? Do you close with a reflection or a directive?

**Tone.** How do you handle uncertainty? Do you hedge, or do you just say what you think? How do you talk about failure or difficulty? Is there a consistent emotional register across pieces?

**Things you avoid.** These are as important as what you do. List specific constructions, phrases, or rhythms you never use. The avoidance list prevents the AI from defaulting back to its own habits.

Write all of this down in plain language, as rules an AI can follow. Avoid describing what you aspire to write. Describe what you actually wrote in those samples.

### Step 2: Build a reference file

Create a single document that holds the rules from Step 1. Structure it however makes sense for your voice, but keep it readable in a few minutes. You'll be pasting it into context often.

Include a short section of raw examples: 3 to 5 sentences or short paragraphs pulled directly from your source material. These work as few-shot anchors. When an AI has both the rules and a handful of real examples, the output is more accurate than rules alone.

A good profile is 300 to 600 words. Shorter tends to miss nuance; longer tends to dilute the signal.

### Step 3: Apply as a context layer

Before any writing task where your voice matters, put the profile into the model's context window before the request. The simplest version is a preamble: paste the profile, then give the writing task.

If you have a system prompt or a persistent context block, the profile belongs there. The goal is that the model has the rules in front of it when it generates the first word, not as an afterthought revision pass.

### Step 4: Pair with a cleanup pass

A voice profile gets you most of the way there. AI still has its own rhythms it falls back on, especially in longer pieces. Running the output through a linter or cleanup pass (such as the ai-proof skill in this series) strips the generic patterns out after the draft is done. Voice profile sets the target; cleanup removes what doesn't belong.

### Step 5: Maintain the profile

Your voice drifts over time. Every six months or so, read through a few recent pieces you're happy with and check whether the profile still matches. Update any rules that feel off. The profile is a living document, not a one-time setup.

---

## One-Paragraph Version

Pull 5 to 10 pieces you actually wrote, extract the consistent patterns (sentence length, vocabulary, openings, closings, tone, avoidances), and write them down as explicit rules. Add a few raw examples from your own writing as anchors. Put this profile into the model's context before every writing task in your voice. Follow with a cleanup pass to strip AI's default rhythms out of the draft. Review the profile periodically so it stays accurate as your writing evolves.
