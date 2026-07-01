# session-handoff

A skill that writes a tight, paste-ready summary of the current session so you can clear the context and resume in a fresh one without losing your place.

## The problem it solves

Long agent sessions get slow and expensive. The context fills with history the model re-reads every turn, and the usual fix — an automatic compaction — tends to produce a bloated, hedged summary that keeps a lot of what you didn't need and loses the two or three things you did.

I kept hitting the same wall: I'd want to start clean, but starting clean meant re-explaining the whole task from scratch. So I made the handoff explicit. Instead of letting the tool compact everything, I have it write one focused block — what we're doing, what's decided, which files matter, what's still open, and the single next step — and nothing else.

## How it works

1. Ask for a handoff when the session is getting long or you're about to switch tasks.
2. The skill writes a single markdown block in a fixed structure: framing, state of play, key files, open decisions, next step, and any preference from this session that would otherwise vanish.
3. You copy it, clear the session, and paste it as the first message in the new one.

The rule that keeps it useful: one screen, concrete paths and decisions, no filler. It points at your files instead of re-explaining them, which is what keeps it short.

It writes nothing to disk on purpose. The handoff is a chat message — saving it as a file would add to the context you're trying to shrink.

## Install

```
curl -fsSL https://github.com/jdurey/skills/tarball/main | tar -xz && mv jdurey-skills-*/session-handoff . && rm -rf jdurey-skills-*
```

No dependencies. It's just a `SKILL.md`.

## Why it's public

This is one of the smallest skills I use and one of the most frequent. Starting a fresh session with a clean, dense prefix is faster and cheaper than dragging a long history forward, and a good handoff beats an automatic compaction almost every time. The version here has none of my private setup in it — just the structure and the rules.
