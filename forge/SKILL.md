---
name: forge
description: >-
  A premise-first ideation and validation engine. Use the Forge when you want to generate,
  pressure-test, or de-risk an idea, strategy, product concept, positioning angle, or research
  direction — anything where the failure mode is "well-designed but already saturated" or
  "nobody actually pays for this." It validates the premise against live evidence before any design
  work begins, and fans the prompt across genuinely independent model families (not one model
  running multiple subagents) to surface disagreement rather than echo consensus. Do NOT use for
  routine builds, simple lookups, or problems one model is already handling cleanly.
---

# Forge

An ideation engine built around two disciplines, both learned by getting them wrong.

The failure mode the Forge is designed to prevent: spending real effort on a design whose founding
premise is already saturated, dismissed, or lacks a real buyer. By the time that fact surfaces in a
conventional process, the sunk cost has made it hard to see clearly. The Forge front-loads the
reality check so the gate runs before the design, not after.

## When this earns its cost

Use it when novelty and validity both matter and a wrong-but-plausible answer is expensive:
strategy, positioning, product or premise ideation, research direction. For purely technical
stuck-problem solving with an objective pass/fail gate, a divergent-solve approach is the closer
fit. For routine tasks a single model handles clearly, the dispatch overhead is not worth it.

## The two non-negotiable disciplines

**1. Validate the premise before designing anything.**
Ideas are cheap; the gate is the point. Before any design work, every candidate premise is tested
against live web evidence: Is this space already saturated or actively dismissed by practitioners?
Does a real, currently-existing buyer pay for this outcome? Is it different in a way the market
rewards? The falsifiability test always points outward at the world, not inward at the logic of
the idea itself. Internally consistent is not the same as externally valid.

**2. Use genuinely independent model families, not one model with multiple subagents.**
Fanning a prompt across subagents spawned from the same model is convergent thinking in costume.
Different model families (trained by different labs on different data) get stuck in different
places. The divergence between families, not the consensus, is what makes the method useful. Use
whatever independent families and CLIs you have available; codex, grok, and gemini are examples
of this pattern, not requirements.

## Phase 0a -- Gate your own premise before dispatch

The panel will faithfully answer whatever premise you hand it, including a false assumption you
built in. Before writing the prompt, audit the premise itself:

- Strip unearned givens. Does the framing assume credentials, an existing audience, prior
  relationships, capital, or resources the actual operator does not have? Name only what is
  genuinely in hand and exclude the rest explicitly in the prompt as auto-KILL constraints.
- State hard constraints as auto-KILL gates in the prompt, not as soft preferences: "any path
  requiring X is a KILL," where X names each unearned given.

Garbage premise in, garbage survivors out. The gate in Phase 0 does not catch a flawed framing;
only this step does.

## Phase 0 -- Reality gate (almost always run first)

Write a prompt instructing each family to generate candidate premises and immediately kill any
that fail the gate against live web evidence, citing real URLs. The gate:

- **G1 Saturation** -- already common, crowded, or actively dismissed by practitioners? Find who
  is already doing it. Saturated or dismissed means kill.
- **G2 Paid demand** -- name a real, currently-existing buyer or contract that pays for this
  outcome, with a verifiable URL (a live job post, a funded company, a paid contract pattern).
  No payer means kill.
- **G3 Novelty that matters** -- different in a way the market rewards? Why has no obvious
  incumbent already taken it?
- **G4 Edge-fit** (when ideating around a specific person's advantage) -- does this genuinely
  require their particular intersection, or could a generalist do it?

Require each family to show its kills alongside its survivors and end with a forced summary line:
"GATE RESULT: N survivors / M killed." A run with zero kills means the gate did not bite.
Re-run with a harder gate or a more pointed falsifiability rider.

Give each family a distinct facet or source set (a short per-family focus instruction) so they do
not all search the same corners of the web.

## Phase 1 -- Divergent generation (after a premise survives the gate)

Same fan-out, new prompt. Each family independently designs an answer in a fixed, comparable
output format so you can diff the responses. Use per-family focus instructions to push each
toward a different angle rather than letting them converge on the same framing.

## Phase 2 -- Adversarial cross-verify

Bundle all families' Phase 1 answers into one file and feed it back: each family attacks the
others' designs against explicit pass/fail gates, names the single hardest hole in each, and
proposes its own synthesis. Cross-family attack, not self-review.

## Phase 3 -- Synthesis and verification (orchestrator does this)

Read the distilled responses. Verify the load-bearing claims yourself with web search before
trusting them -- precedent cases and "live demand" URLs are the most confabulation-prone outputs.
A single fabricated payer can flip a verdict. Down-weight any family whose evidence is vaguer
(generic landing pages, no specific post) relative to one citing exact, checkable URLs.

For a large set of claims, fan the verification out: one researcher-tier pass per claim, each
told to try to refute it rather than confirm it. Force a verdict schema so results compose cleanly.
For a small claim set (roughly eight or fewer), a single batched refute-mode pass is usually
sufficient and cheaper than one-agent-per-claim.

Two failure modes to catch explicitly:
- A precedent that is real but irrelevant: it happened, but it required resources the operator
  does not have, so it does not support the claim it is cited for.
- A stale fact: the company or role was real but has since been acquired or dissolved, so it is
  no longer the buyer named.

## Output discipline

Always show the kills, not just the survivors. The kills are where the gate earns its keep. Each
surviving claim should carry its evidence URL; flag any you could not verify. Note provenance:
which families ran, which were unavailable, and what you verified versus accepted on the panel's
word.

## One-paragraph version

Write a prompt with a reality gate built in. Fan it simultaneously to genuinely independent model
families -- trained by different labs so they fail differently -- and require each to kill
premises that lack real, URL-verifiable demand before designing anything. Collect the survivors,
cross-verify load-bearing claims yourself, then synthesize. The goal of the gate is to find kills,
not survivors; a clean gate that kills nothing did not bite hard enough.
