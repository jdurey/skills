---
name: overnight
description: >-
  Run a build or task STRAIGHT THROUGH, unattended, without ever stopping to ask a question — so the user can
  kick it off and walk away (overnight, or just AFK) and come back to finished work plus a review list, never a
  hung prompt. Trigger on "overnight", "run this overnight", "work through the night", "I'm going to bed", "do
  this while I'm out/away/asleep", "don't stop to ask", "don't check with me", "work straight through",
  "autonomous build", "unattended", "no questions", "just get it done by morning", or any variation that hands
  off a multi-step task to run with nobody watching. This skill flips into autonomous mode: every ambiguity is
  resolved with a logged sensible default and the build continues; the only things that would normally halt (a
  confidentiality/data-boundary doubt, an irreversible or outward action, a hard blocker) are skipped-and-logged,
  never hung on. It suppresses the interactive checkpoints of intake/planning skills for the duration. Do NOT use
  when the user is present and wants to steer, or for a one-shot trivial task.
---

# Overnight — autonomous, no-hang execution

The user invokes this when they're NOT watching and want the work done by the time they're back. The cardinal sin is a **hung decision**: a build that stalled at 2am waiting for an answer nobody was awake to give. In overnight mode there is no such thing as a question to the user — there is only the work, sensible defaults, and a log they read in the morning.

## The one rule

> **Never stop to ask. Resolve every choice yourself with the most reasonable default, log it, and keep going.**
> If a choice is genuinely unsafe to make alone (see Hard-stops), take the SAFE option — skip that sub-step and
> log it — then continue with everything else. The build never halts as a whole.

Interactive questions are **banned** for the duration. So is any "should I proceed?" / "let me confirm before…" pause. A heavy task still gets planned once, up front, but the plan is then executed end-to-end without interactive checkpoints.

## Protocol

1. **Plan once, silently.** Restate the goal, lay out the steps and the definition-of-done, pick the approach — and for each heavy step, the cheapest capable path (see Token economy). Don't ask for approval of the plan — commit to it and start. Write the plan as the head of the log.
2. **Keep a live decision log.** Create `OVERNIGHT-LOG.md` in the working directory and append to it as you go (live, not reconstructed at the end). Every entry is one of:
   - `DID:` an action taken and its result (including test/verify output).
   - `ASSUMED:` an ambiguity you resolved, the default you chose, and why (this is the question you did NOT ask).
   - `DEFERRED:` something you deliberately did NOT do (a Hard-stop), the reason, and what the user needs to decide.
   - `FIXED:` a failure you hit and how you recovered.
3. **Resolve ambiguity with defaults, not questions.** Pick the option most consistent with the stated goal, the conventions already in the project, and the user's known preferences. Log it as `ASSUMED:` and move on. A reasonable default that's logged beats a perfect answer that hangs.
4. **Verify as you go.** Run the tests / boot / lint that prove each step. If a step fails: try a reasonable fix (log `FIXED:`); if it still fails after a bounded effort, log `DEFERRED:` and move to independent work. One broken step must not block the rest of the build.
5. **Bias hard to completion.** Finish the task. If you finish with time or budget left, do the clearly in-scope verification, hardening, and polish — do NOT expand scope into features nobody asked for.
6. **Morning report.** End with a tight summary (and leave `OVERNIGHT-LOG.md` in place): what's done and verified; every `ASSUMED:` (the decisions the user can override); every `DEFERRED:` (the real decisions waiting for them); any **⚠️ PREMISE UNVERIFIED** banner at the very top (see Premise validity); and the recommended next actions. The user wakes to finished work and one clean review list — never a prompt.

## Token economy — unattended runs spend the minimum that still finishes

Nobody watches the meter overnight, so frugality can't be something you remember to do — it has to be the default path at every step, applied before the work, not after. A run that finishes correctly for a third of the tokens is the win. Quality is never traded; waste always is.

> **At each step, take the cheapest path that still does the job. Spending more is a choice you log (`ASSUMED:`), not the reflex.**

- **Offload deterministic / bulk work to a script; reason over the digest.** Filtering, parsing, counting, dedup, transforming, validating, or any repeated operation goes into a script run in the shell — read a small summary, never the raw bulk. Write the script once; don't re-author the same loop in context.
- **Batch independent model calls.** When a step is N standalone calls (grading, classifying, extracting over many items where call N doesn't inform N+1), drive them through a batch mechanism rather than N interactive turns; many providers price batch work at a discount. Not batchable when each call needs the prior result — that stays a normal loop.
- **Delegate bulk down a tier so the payload never enters your context.** Big input that distills to a small answer → a cheap search/extract subagent (Haiku-class) or a mid read-and-digest subagent (Sonnet-class). Keep orchestration, cross-file judgment, and final synthesis for yourself. Each dispatch has fixed overhead — tier only for substantial bulk, never a 1-2 file task.
- **Cheapest capable model and effort per step.** Low/medium effort unless a step's reasoning is the actual bottleneck. Never switch models mid-run — it busts the cached prefix and re-bills the whole history at full input price.
- **File and log hygiene.** Prefer a diff-style edit over a full rewrite (a rewrite re-emits the whole file as output). Read slices, not whole files; never re-read a file you just wrote. Keep `OVERNIGHT-LOG.md` to one line per entry — it's re-read every turn — and link to artifacts instead of pasting bulk output into it.

## Premise validity — never present an unverified premise as fact

Autonomous runs are where an unverified premise does the most damage: nobody is awake to catch it, and a confident finished plan reads as true. The failure mode is an inference ("they'd probably want X") laundered overnight into a stated fact ("they asked for X"), presented as "ready to execute" — costing real trust over a request that never existed.

- **Tag load-bearing premises in the plan and log them.** A claim about what someone wants or asked for, with no source, is `[INFERRED]` — never written as fact.
- **Any artifact resting on an `[INFERRED]` or `[ASSUMED]` load-bearing premise gets a top-of-output banner** — `⚠️ PREMISE UNVERIFIED — verify before acting` — and is never labeled "ready to execute." Surface the unverified premise first (as a `DEFERRED:` to verify), not buried inside a confident plan.
- **Agreement is not truth.** If you fanned the work to multiple models, their consensus validates the reasoning *given* the premise, never the premise itself. Say so.

## Hard-stops — skip and log, never hang, never barge ahead

These are the only situations that would normally make you stop. In overnight mode you neither ask NOR push ahead — you take the safe default (don't do it), log `DEFERRED:` with what you'd need to decide, and continue with the rest of the work.

- **Confidentiality / data-boundary doubt.** If an output's destination is ambiguous, or an action might move sensitive or private content toward a surface it shouldn't reach → do NOT perform that output, log `DEFERRED:`, continue. Fail closed, every time. This does not relax overnight.
- **Irreversible or outward-facing actions the user didn't explicitly authorize** — sending email, posting, publishing, pushing to a shared branch, deleting things you didn't create, spending real money, anything hard to undo. Default is don't; log `DEFERRED:`. (Local commits, file writes, tests, and reversible edits are fine — do them.)
- **A genuine hard blocker** — a missing credential, an external service down, a dependency that can't be resolved. Log `DEFERRED:` with the blocker and continue with any work that doesn't depend on it.

## Concurrent sessions — non-colliding mode

If other sessions or agents are working the same repo at the same time (the user says "two sessions are running," or you find live git worktrees, a dirty tree you didn't create, or another agent's open log), flip into non-colliding mode: do all you can on un-owned surface only, never touching what a live session owns.

- **Map ownership first.** `git worktree list`, per-branch `git diff --name-only`, `git status` in each worktree, recent commit times, other agents' logs. Establish who owns what before writing anything.
- **Stay on un-owned surface:** new files (coordination docs, specs, helper scripts) and read-only analysis. Never edit a file another session is editing.
- **Don't move the baseline others build on.** Do NOT commit to a shared branch that live sessions rebase onto — keep your artifacts as untracked files in the working dir unless told otherwise. No merges, no rebases of someone else's branch, no pushes.
- **Key off files and content, not commit hashes** — concurrent branches get reset, rebased, and squashed under you; hashes are volatile, the file-level surface is stable.
- **Delegated recon must be read-only too.** Any subagents you spawn must not run tests or edit — concurrent test suites contend and can disrupt a live session. Inspect only.
- **Re-poll between work batches.** When a live session lands or rebases, new un-owned surface opens — pick it up; if it reshaped a branch, re-verify your analysis against the new state before trusting it.

## Boundaries

- Overnight suppresses *interactive checkpoints*, not *judgment* — you still think, plan, verify, and stay in scope. It is "decide and proceed," never "do anything."
- When the user is back and present, drop overnight mode and resume normal interactive working.
