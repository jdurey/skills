---
name: witness
description: Turn a heavy task into a self-verifying loop that runs to a proven definition-of-done. Use whenever a task is big, multi-step, or high-stakes enough that the real risk is declaring victory early — "looks done" with no check behind it. Witness derives explicit success criteria, each with a runnable/objective check, gets them signed off once, then executes and KEEPS GOING — re-checking every criterion each round — until all of them are objectively met with captured evidence. Trigger on "witness this", "keep going until it's done", "don't stop until the criteria are met", "define success and finish it", "hold yourself to a definition of done", or "run this to completion". Do NOT use for trivial one-step tasks, lookups, or pure conversation.
---

# Witness

A witness holds the work accountable to a **definition of done that has teeth**. The job is not to "do the task" — it is to define what *done* objectively means, prove each part of it, and refuse to stop until every part is proven. The failure mode this skill exists to kill is **declaring victory early**: "looks complete," with no check behind the claim.

This is the persistent-definition-of-done loop. It sits between planning (shaping the work *before* it starts) and verification methods that attack *code* specifically. Witness works for **any** task type — content, systems, migrations, research, builds — and its spine is one rule: **every criterion has a runnable check, and the loop ends only when all checks pass.**

## When to trigger

- Someone says "witness this", "keep going until done", "don't stop until the criteria are met", "run to completion", "hold yourself to a definition of done".
- Any heavy, multi-step, or high-stakes task where stopping early — at plausible-but-unproven "done" — is the real risk.
- Pairs with, doesn't replace, a planning pass: shape the task first if its *shape* is still ambiguous. Witness assumes the task is shaped and now needs to be *finished and proven*.

Do NOT trigger for trivial one-step tasks, lookups, or pure conversation.

## The protocol

### Phase 0 — Derive checkable criteria

**Layer 0 — validity of the inputs (runs before any craft criterion).** Before deriving criteria about the quality of the work, gate the task's *premises*. Every load-bearing claim should carry its provenance: verified against a named source, inferred, or merely assumed and still needing a check. Pay special attention to **attribution** claims — "X asked for / wants / needs Y." Treat an unverified attribution as a premise to confirm, not a fact to build on. **No craft criterion closes while a load-bearing premise is still unverified** — it caps the definition-of-done below 100% until the premise is confirmed, or until the dependent criterion is reframed to "verify the premise first." This is the row most checklists miss: a plan can score full marks on craft while resting on a request nobody actually made.

Then restate the task in one or two sentences and decompose "done" into a list of **success criteria**. For **each one, attach an objective verification** — something a machine can settle, not a vibe:

- a command whose output settles it (`test passes`, `exit 0`, `grep returns N`, `build succeeds`)
- a file or artifact that must exist or contain X
- a count or threshold that must match (`all 44 items present`, `0 findings`, `≥ 3 sources cited`)
- a downstream gate or tool that must pass (a linter exits clean, a quality check returns no flags)

**Convert subjective criteria into checkable proxies.** "Prose reads well" → "passes the writing-quality linter with no flags." "Dashboard looks polished" → "passes the UI quality check." "Code is safe" → "the adversarial pass finds no high-severity issue." If a criterion genuinely cannot be made objective, say so explicitly and mark it `[judgment]` — but treat that as a smell and keep it rare. The default is **runnable proof required**: nothing counts as met on the model's say-so alone.

Track the criteria as a live checklist so status is visible the whole way through.

### Phase 1 — Sign-off (the one and only checkpoint)

Present the criteria as a table:

| # | Criterion | How it's verified (the check) |
|---|-----------|-------------------------------|

Ask once: *anything to add, cut, or tighten?* Apply the edits. **This is the only place witness stops for input.** Once it is signed off, the definition-of-done is frozen and the loop goes autonomous.

(If invoked in an unattended or "no checkpoints" mode, skip the sign-off, derive criteria with logged defaults, and proceed — but still emit the criteria table so the choice is auditable.)

### Phase 2 — The verify-and-iterate loop

Now execute, autonomously, to completion:

1. **Do a round of work** toward the unmet criteria.
2. **Run every criterion's check** — actually run it, capture the real output. Do not infer a pass.
3. **Record status** per criterion: ✅ met (with the evidence) / ❌ unmet (with the failing output) / `[judgment]` (with the reasoning). Update the live checklist.
4. **If anything is unmet, loop** — work the failures and re-check. Re-running a check that already passed is cheap insurance; a criterion is only "done" when its check passes in the *current* state, not because it passed three rounds ago.
5. **Repeat until every criterion passes.** No partial credit, no "close enough."

Guardrails for the autonomous stretch:

- **No silent truncation.** If you bound coverage — sampled, capped, skipped a check that won't run in this environment — say so. A skipped check is an unmet criterion, never a silent pass.
- **No false-pass.** If a check is weak, or you are tempted to mark something met without proof, strengthen the check instead. That is the whole point of the skill.
- **Resolve small ambiguities with a logged default** and keep going. Don't hang on choices anyone would wave through.

### Phase 3 — Witness report (only when all checks pass)

The loop ends **only** when every criterion is ✅ (or an explicitly accepted `[judgment]`). Then report:

- **Verdict:** all N criteria met.
- **Evidence table:** criterion → check → captured result. The proof, not a summary of the proof.
- **Rounds taken**, and anything resolved by a logged default.
- **Residue:** anything out of frozen scope that surfaced and was deliberately left, so it is visible rather than buried.

## HALT conditions

Witness is autonomous after sign-off, but it should **stop and surface** — not silently hang, not silently proceed — on:

- **An irreversible or outward-facing action** — sending, publishing, deleting, anything hard to undo — unless it was pre-authorized in the frozen criteria.
- **A true blocker** — a criterion that cannot be met without a decision, credential, or resource only a human can provide. Report the blocker and the next runnable check, not a multiple-choice symptom question.
- **A boundary it isn't sure it may cross** — any action whose permission is genuinely ambiguous. Ambiguous means stop and ask.

Everything short of those resolves with a logged default and the loop continues.

## One-line spine

Define done as a list of checks → freeze it with the user once → loop work-and-verify until every check passes with captured proof → report the proof. Don't stop early; don't mark met without running the check.
