# heavy-task-planner

Force an efficiency-first planning pass before any heavy multi-step task, so you know the cost and the shape before you start spending.

## The problem it solves

I kept running AI into big builds without any real plan. Not vague; I had a clear idea of what I wanted. But a clear idea and a shaped task are different things, and I kept learning that lesson the hard way.

The pattern was always the same. I'd describe a project, the AI would start, and three hours later something would be partially built in a way that made the next step twice as hard. An assumption I hadn't named had turned into an architectural choice, and by the time I found it, a lot of other things depended on it.

The worst case I ran into cost me eight separate conversation sessions on a single project. Thousands of calls, a week of rework. And when I looked back at it afterward, the expensive decisions had mostly been made in the first few minutes, silently, before anyone stopped to ask whether they were right.

The fix I landed on is to run a deliberate planning pass before any heavy task starts. Not a checklist, but an actual process that challenges what I asked for, proposes alternatives I hadn't considered, compresses the scope to the smallest version that delivers most of the value, and produces a written cost estimate with a real basis for every number. Then it writes all of that down as a plan document before any execution begins.

The comparison between before and after was stark. The project that prompted this took roughly seven times as many calls when I ran it without the planning pass. With it, the same class of project finishes in one session, inside the estimate.

## How it works

1. **Challenge the framing.** Restate the goal as one plain sentence that is not the proposed solution. Ask what happens if the project is skipped. Name at least two alternatives to whatever tool or platform was suggested. Find the ten-percent version of the scope.

2. **Compress scope.** Write the MVP explicitly. Move everything else to a "later" list. Cut decorative features, multi-tool complexity, and anything introduced with "we could also." If still too large, compress again.

3. **Produce a grounded cost estimate.** One row per axis (turns, calls, sessions, manual steps, failure modes), each with a one-line basis. If the estimate says the work spills across more than one session, redesign until it fits.

4. **Write the plan document.** Required sections: goal, framing challenge results, compressed scope, cost estimate, phase-by-phase execution plan, waste modes pre-empted, pilot definition, success criteria, and execution protocol.

5. **Critique the plan twice.** Flag issues as Critical, High, Medium, or Low. Fix every Critical and High. Log the changes so the progression from v1 to v3 is visible.

6. **Enforce one task per session.** When the plan is approved, execution starts in a fresh session with the plan document as the handoff. If the plan is too large for one session, split it at a clean seam.

7. **Pilot first, then batch.** Build the smallest representative sample, verify it against the success criteria, and only then scale. If the pilot fails, fix it and verify again before batching.

See `SKILL.md` for the full method, including the waste-mode catalog and anti-patterns.

## Install

```
curl -fsSL https://github.com/jdurey/skills/tarball/main | tar -xz && mv jdurey-skills-*/heavy-task-planner . && rm -rf jdurey-skills-*
```

## Why it's public

I built this inside a personal AI operating system I put together to run my own work. After running the same class of expensive mistake a few times, I wanted a skill that would force the right questions before any heavy task started, regardless of what I asked for. This is a scrubbed, standalone version with none of my private setup in it; the method is the same, the private plumbing is gone. It's one of a series of skills I'm writing up.
