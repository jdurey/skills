# forge

A premise-first ideation and validation engine: validate the idea against live evidence before designing anything, and generate across genuinely independent model families rather than one model wearing different hats.

## The problem it solves

I wasted about a week on an idea that was dead before I started designing it. The concept was clean, the structure held together, and the more I worked on it the more confident I felt. When I finally went looking for evidence that anyone would pay for the outcome, I found that practitioners in the space had already labeled it a non-starter. The idea had not failed during design; it had been dead on arrival and I had spent real time making it look alive.

The problem was the order of operations. I put effort into design before I put any effort into reality. By the time the premise got tested, I was already too invested in the architecture to look at the evidence clearly.

The other failure mode I kept running into was fanning the same question across multiple subagents spawned from the same model. That produces confident consensus, not useful disagreement. Different model families, trained by different labs on different data, get stuck in different places. The disagreement between them is usually more informative than what they agree on.

The Forge is built around both of those lessons. Validate the premise first, against live evidence, with a gate that points outward at the world. Then generate across genuinely independent families and look at where they diverge.

## How it works

1. **Gate your own premise before dispatch.** Strip any unearned givens from the framing. If the prompt assumes credentials, an existing audience, capital, or relationships you do not actually have, the families will dutifully return answers built on sand. State hard constraints as explicit auto-KILL gates in the prompt itself.

2. **Run the reality gate first.** Fan the prompt to independent model families and require each to generate candidate premises, then kill any that fail against live web evidence: is the space saturated or already dismissed? Does a real, currently-existing buyer pay for this outcome? Require each family to show its kills and end with a forced "GATE RESULT: N survivors / M killed" line. Zero kills means the gate did not bite.

3. **Divergent generation.** For premises that survive, fan the same prompt out again with each family working a distinct angle. Collect comparable outputs so you can diff them rather than read summaries.

4. **Adversarial cross-verify.** Feed all families' designs back as a bundle and have each attack the others against explicit pass/fail criteria. Cross-family attack, not self-review.

5. **Synthesize and verify.** Check the load-bearing claims yourself with web search before trusting them. Precedent cases and "live demand" URLs are the most confabulation-prone outputs. Down-weight vague evidence (generic landing pages) relative to exact, checkable URLs. For a large claim set, fan the verification out with one refute-mode pass per claim; for a small set, a single batched pass is usually enough.

See `SKILL.md` for the full method and gate criteria.

## Install

```
curl -fsSL https://github.com/jdurey/skills/tarball/main | tar -xz && mv jdurey-skills-*/forge . && rm -rf jdurey-skills-*
```

## Why it's public

I built this inside an AI OS I put together to run my own work, and the private version has a lot of personal machinery around it. This is a scrubbed, standalone version with none of that in it. The method itself is general: validate the premise before the design, use genuinely independent model families, and treat the gate as a way to find kills rather than confirm survivors. It's one of a series of skills I'm writing up.
