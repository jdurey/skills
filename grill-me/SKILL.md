---
name: grill-me
description: Interview yourself relentlessly about a plan, design, or idea, one question at a time, checkpointing every answer to a running file so nothing is lost. Use when you want to stress-test a plan before committing to it, extract scattered thinking into a document, surface dependencies you have been avoiding, or run a structured discovery session on your own work. The method works on any plan, proposal, design, or decision where you are the source of the knowledge and want to pressure-test it before presenting or acting on it.
---

# Grill Me

A method for extracting what is in your head and stress-testing a plan before you commit to it. You know more than you realize, and most of the gaps are things you have been quietly avoiding. This skill surfaces them one question at a time, and writes down every answer so nothing is lost.

## When this earns its cost

Use it when you are about to commit to a plan but have not yet had to defend it. Use it when you keep adding detail to a plan but have not tested the seams between parts. Use it when a previous plan fell apart in a meeting because a question exposed a dependency you had glossed over. For routine tasks or things you have already thought through thoroughly, skip it.

## Method

### 0. Set up the capture file before the first question

Create a markdown file at `brainstorms/YYYY-MM-DD-{topic-slug}.md` (create the `brainstorms/` folder if it does not exist). Give the file a header: the topic, the date, the goal of the session, and an empty section called "Open flags." Tell the user where the file is. Then ask the first question.

Every raw capture lives in `brainstorms/`. If the session produces a polished deliverable later, that artifact can move to a relevant project folder, but the raw capture stays where it is.

### 1. Ask one question at a time

For each question, offer your best-guess answer based on what you know so far, so the user can confirm, correct, or redirect rather than having to produce an answer from nothing. Ask only one question per turn. Resolve dependencies in order: settle the upstream decision before asking about things that depend on it.

If a question can be answered by reading a file or document the user has provided, read it first and only ask about what is genuinely unclear. If the user cannot answer something, flag it and move on. Do not stall on unanswered items.

### 2. Checkpoint after every answer, without exception

Before asking the next question, append one structured entry to the capture file:

```
### Q{N} — {topic}
- Asked: {the question}
- Captured: {key facts and decisions, in the user's words where the wording matters}
- Flags: {open item -> who can answer, if any}
```

One entry per answer. Never batch multiple answers into one write. Never hold an answer in context and write it later. The file, not your context, is the source of truth. If the session were cut off after any answer, the file should already hold everything said up to that point.

Update earlier entries if a later answer corrects or refines something already captured.

### 3. Keep a running summary

Maintain a "Summary / key decisions" section at the top of the file. Update it as the session progresses so anyone reading the file can get the shape of the plan without reading every Q&A entry.

### 4. Offer a completeness backstop near the end

When the main branches feel covered, ask: "Is there anything we have not touched that you want to capture?" Then do a final pass.

### 5. Close with a reconciliation

Read the whole capture file. Flag any answers that contradict each other. Summarize what is resolved, what is still open, and what the suggested next step is.

## One-line version

Ask one question at a time with a best-guess answer offered, write every answer to a file immediately after you receive it, surface contradictions at the end, and do not stop until every branch is covered or the user calls it done.
