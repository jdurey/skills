---
name: session-handoff
description: "Produce a tight handoff summary so the user can clear the current session and resume in a fresh one without losing context. Use whenever the user says 'handoff', 'session handoff', 'wrap this up so I can clear', 'I'm running out of context', 'summarize for a new session', 'before I /clear', 'the context is getting big', or any variation that signals they want to dump current state and start clean. Faster than a full auto-compaction, preserves the cache better than continuing into a long session, and lets the next session start with a focused prefix."
---

# Session Handoff

The user wants to close out the current session, start fresh, and pick up where they left off without losing momentum. Your job: produce a single self-contained markdown block they can paste into the next session as the first message.

A good handoff is **shorter than an automatic compaction, sharper, and easier to cache** — because the next session reads it once as a single message instead of replaying a long history.

## What to include

Write the summary in this exact structure (skip sections that don't apply):

```
# Session handoff — <one-line topic>

## What we're doing
<2-4 sentence framing of the project / task and why>

## State of play
- <bullet of what's been decided>
- <bullet of what's been built / written / changed>
- <bullet of any constraint or preference the user has expressed this session>

## Key files / artifacts
- `<path>` — <one line on what it is and its current state>
- `<path>` — <one line>

## Open decisions
- <thing the user hasn't decided yet> — <options on the table>

## Next step
<the single most important next action when the new session opens>

## Quick context for the new session
<anything else the next session needs to know that isn't obvious from the files — e.g. "the draft has already been voice-checked", "the user prefers no emoji", "tests are green as of the last run">
```

## Rules

- **One screen max.** If it spills past ~40 lines, you're padding. Cut.
- **Concrete file paths and decisions, not vibes.** "We discussed the structure" is useless. "Decided 5 sections, intro is drafted in `outputs/draft.md`" is useful.
- **Don't re-explain what the project does** if the project files already say it. Point at them.
- **Preserve user-stated preferences from this session** — these are the things that would otherwise vanish when the context is cleared.
- **No filler** — no "great progress!", no recap of what they already know they did.

## Output

After writing the handoff, tell the user:
1. Copy the block above.
2. Clear the session (`/clear`, or open a fresh session).
3. Paste it as the first message.

Do not write any files. The handoff is a chat message, not a file — writing it as a file would itself add to the context you're trying to keep small.
