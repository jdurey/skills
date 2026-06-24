---
name: divergent-solve
description: Crack a HARD, stuck, or repeatedly-failing technical problem by fanning it out across multiple independent model families in parallel, then adversarially verifying every candidate fix against an objective pass/fail gate before trusting any of them. Use when single-model attempts keep stalling or producing plausible-but-wrong answers, you're getting false-passes, or a bug/auth/config/build issue is "fighting you" and the cost of a wrong answer is high. Do NOT use for routine tasks, simple lookups, or work one model is clearly handling fine.
---

# Divergent Solve

A harness for the problems that beat a single model: the bug that keeps coming back, the auth wall that "should" work, the fix that looks right three times and is wrong all three. One model, however capable, has one prior, one blind spot, and a habit of falling in love with its first hypothesis. This skill borrows three things single-model iteration can't give itself: **independent perspectives** (other model families), **an objective referee** (a pass/fail gate the model can't argue with), and **adversarial doubt** (assume every fix is wrong until the gate proves otherwise).

It exists because of a real failure: a session where one model canonized a *wrong root cause twice* before the evidence was in. The same problem, fanned out to several model families in parallel with an objective gate, was cracked in one pass, and the decisive insight came from the contrarian model, not the consensus.

## When this earns its cost (and when it doesn't)

Fanning out to three or four model families is expensive in tokens, wall-clock, and your attention. Spend it only when the cheaper path has actually failed or the stakes justify it.

- **Use it** when you've iterated solo and stalled; answers keep being plausible-but-wrong; you're catching or fearing false-passes; the cost of shipping a wrong fix is high; or the problem is genuinely ambiguous about its *cause*, not just its mechanism.
- **Skip it** when the task is routine, a lookup, or one model is clearly converging. Boring is beautiful. Don't convene a swarm to change a config value.

**For GENERATIVE problems** (novel idea generation, strategy discovery), this is the wrong instrument. It converges on a gate that selects for safe, correct answers, which kills genuinely novel ideas. Use a divergent *ideation* method for generative work, and save this for "why won't this work, and what fix actually holds?"

## The method

### 0. Frame the problem and define the objective gate (the linchpin)

Before dispatching anything, write down two things:

1. **The problem**, tightly: current state, what's been tried, the exact symptom, and the constraints (what a fix may NOT do, e.g. "must survive past date X", "no per-call manual step").
2. **An objective, automatable SUCCESS GATE**: a command or test whose output is an unambiguous `PASS` / `FAIL`, readable without judgment. This is the linchpin. Without it you have no way to tell a real fix from a confident wrong one, and the whole exercise collapses back into vibes. The gate is also what every verifier runs, so it must be runnable by an agent with no extra context.

A good gate reads ground truth, not self-report. Prefer logs, exit codes, telemetry, and structured error reports over asking the artifact how it's doing. Models and systems misreport themselves. Trust the instrument, not the narrator.

### 1. Fan out to independent model families, in parallel

Give each solver the **same** package: the framed problem, the success gate, the constraints, and an instruction to return working code/commands plus how to verify them. Run them concurrently as background tasks. The point is independence: different model families have different training priors, so they fail differently, and the union of their coverage beats any single model's depth.

A practical shape, using whatever CLIs you have for different families (the names below are examples, swap in yours):

```sh
# Write the shared brief once, reuse it for every solver.
cat > /tmp/ds-problem.txt <<'EOF'
<framed problem + the SUCCESS GATE verbatim + constraints +
"return working code I can run and verify; don't hang on a TTY (use a timeout);
report your findings within ~6-8 min; don't loop re-running the same checks;
state how to confirm the fix hit the gate">
EOF

# One builder model that can execute/test in a sandbox:
codex exec "$(cat /tmp/ds-problem.txt)" </dev/null > /tmp/ds-A.md 2>&1 &
# One contrarian model (often catches the framing error everyone else shares):
grok -p "$(cat /tmp/ds-problem.txt)" > /tmp/ds-B.md 2>&1 &
# One structural/architecture model:
gemini -p "$(cat /tmp/ds-problem.txt)" > /tmp/ds-C.md 2>&1 &
```

Use every family you committed to. Don't run two and silently drop the third. A dropped lane that goes unreported reads as "the whole panel weighed in" when it didn't. If a lane genuinely fails (a timeout, or a safety-filter refusal on the framing), say so explicitly and note whether the survivors still clear your bar.

**Bound each solver's wall-clock.** Some models over-run, looping on the same probes long after a contrarian has delivered a complete answer. Capture each PID, give it a hard deadline (~8 min), and stop it once it has emitted a findings list. The run shouldn't wait on a runaway.

If you also have an in-house agent framework, add a few **divergent-hypothesis agents** in parallel, each chasing a *different* escape route (version/update, config/permissions, a wrapper around the known-good path, docs research, an alternative architecture), with an adversarial verify step that checks each claimed fix against the gate as it lands.

### 2. Adversarially verify every claimed fix (assume false-pass until the gate proves otherwise)

This is where single-model work goes wrong, and why the gate exists. For each candidate any solver returns:

- **Run it through the gate yourself, from a clean state.** Don't trust the solver's "verified PASS." A solver can manufacture a pass by filtering the failure signature out of its own logs, or by reading a self-report instead of the instrument. The gate, run independently, is the only authority.
- **Read the structured error/log, not the summary.** The truth is usually in the report the tool already wrote, not in anyone's interpretation of it.
- **Convergence of *independent* solvers on the same fix is a strong signal.** Convergence on the same *wrong* answer (a shared prior) is the failure mode to watch, which is exactly why the contrarian leg matters.

### 3. Synthesize the verified winner

Pick the fix that genuinely passes the gate with reproducible evidence. Record which angle won and why, and verify the *cause* before you canonize it as a lesson. A wrong "lesson" written into your notes is worse than no note, because it misleads the next person (or agent) who reads it. If two solvers disagree on *why* the winning fix works, that disagreement is unresolved data, not a footnote. Chase it or flag it. Don't paper over it.

## The one-paragraph version

Frame the problem and write a pass/fail gate. Fan the *same* brief out to several independent model families in parallel. Trust nothing: run every candidate through the gate yourself, reading instruments not self-reports, assuming false-pass until proven otherwise. Keep the fix that reproducibly passes, prefer the one the contrarian and the consensus both survive, and verify the *cause* before you write it down. The diversity finds the answer, the gate proves it, and the skepticism keeps a confident wrong answer from shipping.
