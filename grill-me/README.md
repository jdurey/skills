# grill-me

Interview yourself relentlessly about a plan, one question at a time, and checkpoint every answer to a file so nothing is lost.

## The problem it solves

I had a habit of committing to plans that felt solid until someone poked at them. Usually in a meeting, which is the worst possible time. I would spend a couple of hours thinking something through, feel good about it, and then a single question would reveal that I had never really resolved a core dependency.

The problem was that I was doing all of that thinking alone. When I lay out a plan in my head, I also decide which questions are worth asking, and I instinctively skip the ones I do not know how to answer yet. That is not rigor. It is just confidence.

I started using AI to interview me about my own plans instead of generating plans for me. One question at a time. Before each question it offers its best guess at the answer so I can confirm, correct, or redirect. If I cannot answer something, it flags it and moves on.

But the part that actually made it useful was writing everything down immediately. After every single answer, before the next question, it appends one entry to a running file. Not a summary of the session, one entry per answer as the session goes. The file holds the actual record, and I can hand it off or return to it without reconstructing anything from memory.

At the end it reads the whole file back, flags anything that contradicts something else I said, and tells me what is still open. The gaps are rarely surprises. They are mostly things I had already been quietly avoiding. Getting them in writing is the useful part.

## How it works

1. **Create the capture file first.** Before the first question, open a markdown file at `brainstorms/YYYY-MM-DD-{topic}.md`. Put the topic, date, and session goal at the top with an empty "Open flags" section. Tell the user where the file is, then ask Q1.

2. **Ask one question at a time with a best-guess answer offered.** For each question, provide your inference about what the answer likely is so the user can confirm, correct, or redirect rather than starting from nothing. Resolve dependencies in order: settle upstream decisions before asking about things that depend on them.

3. **Checkpoint after every answer without exception.** Before asking the next question, append one entry to the capture file: the question, the key facts from the answer in the user's words where the wording matters, and any flags. One entry per answer. Never batch. Never hold and write later. The file is the source of truth.

4. **Keep a running summary at the top.** Update the "Summary / key decisions" section as the session goes so the file is readable without scanning every Q&A entry.

5. **Close with a reconciliation pass.** Read the whole file. Flag contradictions. Summarize what is resolved, what is still open, and what the next step is.

See `SKILL.md` for the full method.

## Install

```
curl -fsSL https://github.com/jdurey/skills/tarball/main | tar -xz && mv jdurey-skills-*/grill-me . && rm -rf jdurey-skills-*
```

## Why it's public

I built this inside an AI system I put together to run my own work. The checkpoint rule and the dependency-ordering logic came from hitting the same failure mode enough times: a plan I felt good about would fall apart the first time someone pushed on it, because I had never had to defend it out loud. This is a scrubbed, standalone version with none of my private setup in it. It works with any capable chat model. It is one of a series of skills I am writing up.
