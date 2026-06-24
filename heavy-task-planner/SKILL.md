---
name: heavy-task-planner
description: Force an efficiency-first planning pass before any heavy multi-step task -- a build, migration, content sprint, automation, multi-file deliverable, or anything that will span many turns or conversation sessions. Use this skill first whenever a request involves "build," "rebuild," "create a system," "automate," "migrate," "generate N of," or any task that smells like it will touch more than one context window. The skill challenges the framing, proposes cheaper alternatives, compresses scope to an MVP, produces a grounded cost estimate, and writes a plan document before any execution begins. Do not use it for single-file edits, one-shot scripts, or tasks already scoped to a handful of turns.
---

# Heavy Task Planner

A meta-skill that runs before any other skill or execution when a task is heavy. Its job is to make sure the task is shaped correctly, the cheapest viable path is chosen, and you have a written plan before resources are spent.

## When to trigger

Trigger on any of:

- Requests that include "build X," "rebuild X," "create X system," "automate X," "set up X," "migrate X"
- "Generate N of Y" where N is not trivially small
- Any task spanning multiple files, multiple databases, multiple phases, or a sprint
- Any task that will take many turns or spill across more than one session
- Any task where the requester has pre-committed to a tool but the container might be wrong

Do not trigger on:

- Simple conversation or quick factual questions
- Single-file edits, one-shot content, single posts, scripts, or emails
- Tasks already scoped to a handful of turns with a clear, bounded deliverable

## Non-negotiables

Before executing a heavy task, the requester must have:

1. A written plan document in the workspace
2. A one-sentence goal restatement that is not the proposed solution
3. A cost estimate table with p50 and p90 values and a grounded basis for each number
4. An iteration log showing the plan was critiqued at least twice before being finalized
5. An explicit protocol to start execution in a fresh session

If any of these is missing at the end of the planning pass, do not execute.

## The process

Run each phase in order. Do not skip.

### Phase 1 -- Challenge the framing

Before accepting the task as stated, answer these four questions out loud:

1. **What is the actual goal?** Restate it in one sentence that is not the proposed solution. "Rebuild my Notion lab" might mean "have a place to track weekly assignments." Those are different problems with different cheapest paths.
2. **What is the zero-option?** What happens if this task is skipped entirely? If the loss is small, say so. Do not do work because you were asked -- do work because not doing it is worse.
3. **Is the container right?** If the requester named a specific tool, surface at least two alternatives and their trade-offs. Common substitutions worth naming: a static site or a markdown archive instead of a hosted platform, a spreadsheet instead of a database, a no-code tool instead of a custom build.
4. **What is the ten-percent version?** The smallest deliverable that captures most of the value. Build that first to prove the architecture, then scale.

If any answer changes the shape of the task, surface it before continuing. Do not silently re-scope.

### Phase 2 -- Scope compression

Write the MVP version of the task explicitly. Everything else goes to a "later" list.

Cut:

- Decorative features with no clear user value
- Features that require multiple tools when one would do
- Features that assume a future state that does not yet exist
- Anything introduced with "we could also..."

Leave only the core loop. If still too large, compress again.

### Phase 3 -- Cost estimate

Produce a table with a one-line basis for every number. Do not hand-wave.

| Axis | p50 | p90 | Basis |
|---|---|---|---|
| Assistant turns | N | N | phases x avg turns per phase |
| Tool or API calls | N | N | break down by tool and any parallelism limits |
| Context windows needed | 1 / 2 / 3+ | -- | hard constraint |
| Manual steps the user must take | N | N | list them |
| Top 3 failure modes | -- | -- | name them |

**If the p90 estimate exceeds one context window, stop and redesign.** Push state into scripts, YAML, JSON, or state files so the session handles only orchestration. This is the single most important discipline.

### Phase 4 -- Write the plan

Write a plan document to the workspace. Required sections:

1. **Goal** -- one sentence, not the solution
2. **Framing challenge results** -- what was asked, what changed
3. **Compressed scope** -- what is in, what is out, and why
4. **Cost estimate table** from Phase 3
5. **Phase-by-phase execution plan** with a call budget per phase
6. **Waste modes pre-empted** (see catalog below)
7. **Pilot definition** -- what the ten-percent build looks like
8. **Success criteria** -- how the requester verifies it worked
9. **Known limitations and manual steps**
10. **Execution protocol** -- instructions to start in a fresh session

Save the document. **Wait for approval before executing anything.**

### Phase 5 -- Iterate the plan

Critique the plan twice. Severity tiers:

- **Critical** -- will break the build or violate a hard constraint
- **High** -- will cause significant waste or rework
- **Medium** -- worth fixing but not load-bearing
- **Low** -- polish

Fix every Critical and High issue. Log the changes alongside the plan so the progression from v1 to v3 is visible.

Skipping iteration is always more expensive than doing it. A plan that is not critiqued tends to encode the same assumptions that made the naive approach fail.

### Phase 6 -- One task per session

When the plan is approved, tell the requester:

> This is one session's worth of work. Start execution in a fresh session. Paste the plan document and say "execute this plan."

If the plan will not fit in one session even after Phase 2 compression, split it at a clean seam. Each split gets its own plan document, its own cost estimate, and its own session.

### Phase 7 -- Pilot first, then batch

During execution:

1. Build the smallest representative sample (one page, one record, one item).
2. Verify it against the success criteria from the plan.
3. Only then batch the rest.

If the pilot fails, stop. Fix it. Verify again. Do not fix and immediately batch -- the fix may have introduced a new failure.

## Waste-mode catalog

Pre-empt these in every plan. When a novel failure mode appears in production, add it here before fixing the data.

| # | Waste mode | Pre-empt |
|---|---|---|
| W1 | Logic scattered across turns | single source of truth in one script |
| W2 | Cost estimates with no grounded basis | every number needs a one-line reason |
| W3 | Accepting the stated container without challenging it | Phase 1 question 3 is mandatory |
| W4 | Running the full batch before the pilot is verified | Phase 7 sequence is non-negotiable |
| W5 | Mixing multiple tasks in one session | Phase 6 protocol, every time |
| W6 | Unknown parallelism or rate limits | document them; respect them |
| W7 | Fallback values hiding missing inputs | fallbacks must be explicit and render a literal |
| W8 | Planning privately and presenting only the final plan | show v1, iterate in the open, give checkpoints |
| W9 | Optimizing for elegance instead of waste reduction | the plan should be boring on purpose |
| W10 | Fabricated timelines or skipped iteration | each critique pass is the cheapest rework available |

## Anti-patterns

- Starting execution before Phase 4 is written
- Accepting the requester's container choice without Phase 1 question 3
- Iterating in your head instead of writing the critique down
- Running the full batch before the pilot is verified
- Running multiple tasks in one session
- Silently re-scoping when a framing answer changes the shape of the task
- Telling the requester "I can do this in the current session" when the task is heavy

## Output contract

At the end of a planning pass the requester gets:

1. A plan document in the workspace
2. An iteration log alongside it showing v1/v2/v3 severity fixes
3. A one-message summary covering: the goal, the top framing challenge result, the cost estimate headline, and the execution protocol

If the task turns out to be small enough that this skill should not have triggered, say so plainly and proceed without the planning pass.

## One-line version

Before any heavy task, challenge the framing, compress the scope to an MVP, produce a grounded cost estimate, write the plan down, critique it twice, and only then execute -- in a fresh session, with the written plan as the handoff.
