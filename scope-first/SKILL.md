---
name: scope-first
description: >-
  Run a short intake-and-plan pass at the START of any substantive request before doing the work.
  Use when a task is multi-step, produces a deliverable or file, requires tools or research, or
  when the goal, scope, or output format is even slightly ambiguous. The skill restates the goal,
  surfaces genuine ambiguity, recommends appropriate effort level, and lays out a lean plan —
  then waits for a go-ahead before executing. Do NOT trigger on quick factual lookups, simple
  one-step answers, or casual conversation.
---

# Scope-First Intake

A brief pass at the start of any real task: pin down exactly what's wanted, surface any genuine ambiguity, match the effort to the task, and sketch an efficient plan. Then get a green light before spending effort on execution.

The deep reason this matters: the most expensive mistake in AI-assisted work isn't using a slightly heavier tool. It's doing the wrong work well, or doing the right work with the wrong shape. A 30-second intake prevents the kind of rework that actually costs.

## Step 0: Calibrate — does this need an intake?

Not every request deserves the full ritual.

**Trivial** — a quick fact, a definition, a one-line lookup, casual conversation, or a single obvious one-step action. Answer directly. Forcing an intake here wastes time and adds friction.

**Substantive** — anything multi-step, any deliverable or file, anything needing tools or research, or anything where the goal, scope, or format is even slightly ambiguous. Run the full intake below and wait for a go-ahead before doing the work. A 20-second confirmation is cheap insurance against building the wrong thing.

When in doubt, treat it as substantive but keep the intake short.

## Step 1: Restate the goal

Write one or two sentences describing the outcome, not the steps. Then surface anything genuinely ambiguous: scope, audience, format, depth, constraints, or the definition of "done."

If a real fork exists ("quick summary vs. deep analysis," "one-off vs. reusable tool"), ask about it. If the ask is already clear, state your understanding and let the person correct it. Don't manufacture questions when none are needed.

**Scope guard:** before planning sub-steps, confirm you are solving the whole goal, not just the first concrete slice of it. A recurring failure mode is that the easiest thing to build pulls the plan toward itself, and the scope narrows until you're building the mechanical part while the judgment-heavy part goes unaddressed. When the goal is a role, a function, or "automate X end-to-end," restate its full breadth and get it confirmed before proposing where to start.

## Step 2: Recommend effort level

Name the approach and give a one-line rationale. A few default tiers to reason from:

- **Light** — classification, extraction, parsing, routing, or simple lookups. Fast and cheap; the right choice for bulk or repetitive steps.
- **Standard** — most production work, multi-step tasks, agentic coding. The default for most requests.
- **Heavy** — hardest reasoning, long-horizon autonomy, deep research, final synthesis. Reserve for tasks where judgment is the actual bottleneck.

If the task has a cheap bulk phase and an expensive judgment phase, say so and recommend handling them separately. The bulk runs fast; the judgment only applies to the distilled result.

Match the effort to the task. Over-resourcing a simple request and under-resourcing a hard one are equally wasteful.

## Step 3: Lean plan

A short numbered list of the actual steps, with efficiency notes where they apply:

- **Offload deterministic work:** any step that is filtering, counting, parsing, deduplication, aggregation, or validation should be done in code or a script so you reason over a small summary instead of raw bulk.
- **Note reuse:** if a large stable input will be referenced more than once, plan to extract and store it rather than re-processing it each time.

End with a rough effort read: "small / one pass," "medium / a few steps," or "large / spans multiple passes." If it reads as large (multi-session build, migration, big multi-file deliverable, content sprint), hand off to a dedicated planning pass before executing.

Then stop. Wait for confirmation or adjustment before doing the work.

## One-line version

At the start of any real task, spend 30 seconds restating the goal, naming the effort level, and sketching the plan, then wait for a go-ahead. The cost of a wrong build is almost always larger than the cost of this pause.
