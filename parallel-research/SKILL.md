---
name: parallel-research
description: Decompose a research task into independent subagent dispatches that run in parallel, then synthesize the results. Use whenever a research, analysis, audit, or fact-check request touches 2+ independent entities, sources, files, or analysis threads. Trigger on "run the agents," "parallel research," "dispatch agents," "analyze these sources," "audit this," "cross-reference," "fact-check these," "entity map," "source audit," or any investigative request with independent parts. Even when the user doesn't ask for parallelization explicitly, use this skill to evaluate whether the task should be split and dispatch accordingly.
---

# Parallel Research Dispatch

This skill turns a research request into parallel subagent dispatches. Instead of running research threads one after another in a single context window (slower, and lower-quality as the window fills), it decomposes the work into independent tasks, dispatches them in the same turn, and synthesizes what comes back.

The win is twofold: each thread gets its own clean context, and the threads run concurrently. A request like "audit these claims and map how these organizations connect" is two independent tasks that never needed to share a context window.

## When to parallelize (decision logic)

Evaluate the task before executing it.

**Parallelize when ALL of these are true:**
- The task contains 2+ independent research threads
- No thread depends on another thread's output
- Each thread can produce a self-contained summary
- Threads don't write to the same output file

**Stay sequential when ANY of these are true:**
- Thread B needs Thread A's output
- The task is narrative drafting where voice consistency matters
- Scope is unclear and needs exploration before you can decompose it
- All the work targets a single file or entity with no natural division

**Run in the background when:**
- The work is read-only analysis that doesn't block what you're doing now
- It's web research or source verification
- It's document summarization for later reference

## How to decompose a request

1. **Parse the request into distinct threads.** Look for multiple named entities, multiple source types, multiple documents or sections, multiple analysis types, and conjunctions that separate independent tasks ("and," "also," "plus").

2. **Match each thread to the right agent and tier** (see Model routing). A discovery thread and a deep-analysis thread are not the same job and shouldn't cost the same.

3. **Write a precise invocation for each thread.** Every dispatch must include:
   - Specific scope: which files, sources, or entities to examine
   - Clear success criteria: what the output must contain
   - Output format: how to structure the findings (a table, a registry, a ranked list)
   - Exact file references, not vague descriptions
   - A save location on disk for the detailed findings
   - The model tier (never let a thread silently inherit your most expensive model)

4. **Dispatch all threads in the same turn.** Don't dispatch one, wait, then dispatch the next — launch them together so they actually run in parallel.

5. **While they run,** tell the user what was dispatched, one line per thread.

6. **When results return, read the saved files** (not just the returned summaries) and synthesize across threads. The synthesis should:
   - Identify connections between findings from different threads
   - Flag contradictions
   - Highlight gaps that need follow-up
   - Present a unified summary organized by significance, not by which agent produced it

## Model routing

Route by the work, and route explicitly — an un-pinned subagent tends to inherit your most capable (most expensive) model and quietly bill at that rate for work that didn't need it.

- **The orchestrator (you):** the top tier. Decomposition, editorial judgment, final synthesis, and talking to the user.
- **Analysis / fact-check / extraction threads:** a mid research tier (for example, a Sonnet-class agent). Source analysis, entity mapping, evidence extraction, cross-document comparison.
- **Pure discovery:** a shell command, not an agent. Grep, glob, file listing, line counts, and format checks are deterministic — run them inline for zero model tokens. Only reach for a cheap search/extract agent (a Haiku-class one) when discovery requires *reading and judging*, not when a pattern match answers it.

Only fall back to the top tier for a thread when it genuinely needs the deepest reasoning — and say so when you do.

## Writing a good dispatch

The templates below are starting points. The value is in precision of scope and output format — adapt them to the request.

**Source / claim audit:**
```
Read the specified source files. For each factual or empirical claim:
- Extract the exact claim text and its location
- Classify the cited evidence (peer-reviewed, self-reported, testimonial, press release, none)
- Flag discrepancies: unsupported claims, overstated strength, circular citations, conflation
Output a markdown table: | Claim | Source | Evidence Cited | Evidence Type | Discrepancy |
Save to: analysis/source-audit-<topic>.md
```

**Cross-document comparison:**
```
Read the specified documents. Extract the fields that matter for comparison
(parties, amounts, dates, terms, methods — whatever the task is about).
Cross-reference across documents: compare like against like, flag outliers,
note gaps and inconsistencies.
Output: a comparison table, then a short narrative of the patterns and flags.
Save to: analysis/comparison-<topic>.md
```

**Entity / relationship map:**
```
Read the specified files. Extract all entities (organizations, people, instruments).
Map relationships: ownership chains, overlaps, flows, movement between roles.
Flag patterns: undisclosed connections, shared identifiers, conflicts.
Output: an Entity Registry table, a Relationship narrative, and a Flags list.
Save to: analysis/entity-map-<topic>.md
```

## Context preservation

- Subagents save detailed findings to disk, not just the summaries they return.
- When synthesizing 3+ results, read the saved files rather than relying on returned summaries alone.
- This keeps your context clean for synthesis and the follow-up conversation.

## Single-task fallback

If the request is genuinely one thread (one entity, one source, one analysis type), skip parallelization and just do it. The skill's value is in decomposition and dispatch, not in forcing parallelism where it doesn't help.
