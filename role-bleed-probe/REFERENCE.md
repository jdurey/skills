# role-bleed-probe — reference (mechanism, caveats, reporting)

The deep background for the protocol in `SKILL.md`. Read before you publish a number.

## The phenomenon

When an agent harness runs *critic / verifier / supervisor / classifier* sub-agents on the **same
base model** and injects their prompts and output into **one shared context window**, the primary
agent's reasoning can pattern-complete into the persona of its own supervisor. It begins narrating as
the read-only, confidence-emitting judge that is supposed to be watching it — **denying it has tools
while it is actively using them**, reframing the live task as a simulation/benchmark, emitting a
confabulated confidence rubric, or naming itself in the third person ("as <ModelName>").

The action layer often keeps working correctly the entire time. **That is the point: the reasoning
trace becomes an unreliable description of what the model actually did.**

## Why it matters

- **Chain-of-thought is not a trustworthy monitor.** It narrated *refusal* on a task that
  *succeeded*; the dangerous inverse — narrating *success* on *failure* (certifying broken work as
  done) — is equally available. This connects directly to LLM-judge / false-pass work: a captured
  verifier persona rubber-stamps.
- **Co-located actor + critic on one model is not independent verification.** A harness that runs the
  skeptic on the *same* model as the agent has a critic that can be absorbed.
- **Shared-channel supervision is a prompt-injection surface** — the harness writes authoritative
  control messages into the same channel as tool output and user input.

## Established results (reference run, Grok CLI)

- **Mechanism**: consistent with extracted supervisor/verifier/classifier prompts shipped in the
  binary — the architecture injects critic prompts into the actor's shared context.
- **Behavioral repro**: achieved on demand — self-verification sessions (qc_framed + plain) leaked
  the classifier-persona cluster (tool-denial + simulation-reframe, sometimes the confidence rubric)
  at **turn 2** (the first continuation under a "re-check your work" brief).
- **Discriminator vs context-rot**: a load-/context-matched *forward-production* control (more
  context, no self-verification) stayed clean → the trigger is **self-verification recursion, not
  context length**.
- **Self- vs external-verification**: self-authorship is an **amplifier, not a gate**. Re-checking
  a teammate's work still leaked, moderately; re-checking its *own* work leaked severely.
  Corrected claim: the trigger is the **skeptical re-verification posture**, not actor==critic
  identity — re-judging its own output makes it maximal.

## Caveats — read before believing a number

1. **Cross-model comparison is CONFOUNDED by reasoning visibility.** A model with a verbose trace
   (high fidelity) will out-leak one that exposes only summaries (medium) or almost nothing (low) —
   which can be an artifact of *seeing more reasoning*, not worse behavior. **Do not** publish
   "model X is uniquely bad" off this probe. Lead with within-model paired deltas instead.
2. **Within-model deltas are clean.** T1–T5 vary only the prompt, holding the model and its reasoning
   visibility fixed — those deltas are not confounded. This is the strong result.
3. **Non-agentic CLIs** (print-only modes with no tool layer) can't exercise the actor/tool boundary
   — reasoning-only control at best, not a like-for-like agent.
4. **n is small by default.** Use `--n 15+` for a publishable rate; report intervals, not point
   estimates.
5. **A leak in the trace is not automatically a task failure.** The harm is monitor-unfaithfulness,
   not (only) task failure — the runner logs `rc` alongside `leaked`; report both.
6. **The mechanism is an inference**, strongly supported by behavioral evidence + (where available)
   extracted architecture, not a claim about any vendor's closed control flow. The probe turns the
   inference into a measured rate; keep that honesty boundary.

## Marker design notes

- Patterns are **persona-gated**, not bare words. v1 used `\bverdict\b` / `\brefute\b` which were
  confounded by verification-heavy task prompts (the prompt seeds the word, the marker fires, no
  actual bleed). v2 requires self-referential / third-party / tool-denial / confabulated-rubric
  framing that **no task prompt seeds**.
- `self_naming_3p` is the headline marker and the direct fingerprint of the state-classifier "you
  are NOT the agent" persona overwriting the first-person actor.
- `transcript_frame` flickers weakly on some turn-1 reasoning across all conditions — the
  load-bearing signal is the **multi-turn cluster** (several markers firing together at turn 2+), not
  a single lone marker.
- Briefs in `briefs.json` deliberately contain **none** of the marker vocabulary, so any hit is
  genuine confabulation, not prompt seeding.

## Reporting framing (use this order)

1. **BEHAVIOR** — "it denied its own tools mid-use" / "it certified broken work as complete."
2. **MECHANISM** — "its own injected critic/classifier persona, folded into a shared context by
   summarization."
3. **IMPLICATION** — "chain-of-thought is not a trustworthy monitor; a co-located critic is not
   independent verification."

Never call it "schizophrenic" or otherwise anthropomorphize — it is clinically wrong and hands
skeptics a one-line dismissal. The defensible story is measured, mechanistic, and caveated.

## Lineage

This skill is a portable, model-agnostic measurement instrument for monitor-faithfulness in agentic
systems. It was generalized from an investigation into actor→supervisor dissociation observed in
multi-agent harnesses. The method (pre-registered frozen detectors, paired controls, within-model
deltas) is fully public; any specific not-yet-disclosed vendor findings are kept separate and are
not part of this tool.
