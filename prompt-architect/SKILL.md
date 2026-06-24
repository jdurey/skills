---
name: prompt-architect
description: Turn a big, fuzzy task into a tight, structured prompt or spec that an AI (or a person) can execute faithfully. Use when handing off a multi-step task to another session or agent, writing a reusable protocol or runbook, or when a paragraph of description has already failed to convey what you actually need. Do NOT use for quick one-shot asks — ceremony-wrapping a trivial task is its own waste.
---

# Prompt Architect

Big tasks don't fail because a model can't hold a long prompt. Context windows are large. They fail because a long prompt spreads attention thin and quietly drops or contradicts instructions buried in the middle. This skill produces prompts that stay addressable: every rule discrete, scannable, and hard to misread. Length is free; attention budget is not. The goal is dense, necessary structure, not padding.

## When to use

- You're handing a large or multi-step task to another session, a subagent, or a future executor.
- You want a reusable protocol, spec, brief, or runbook someone or something else will run repeatedly.
- The task is complex enough that "just describe it in a paragraph" has already lost fidelity.

## When NOT to use

- Quick one-shot asks. Don't wrap a small thing in structure it doesn't need.
- Pure planning of *what* to do. This skill authors the *instructions* once the work is understood. Plan first; then architect the prompt.

---

## Method

### Step 1 — Interview for load-bearing unknowns only

Ask only for the things that change the output: the goal and definition of done, who or what executes it (which AI? a person? what tools do they have?), hard constraints, source material, required output format, and what's explicitly out of scope. Assume sensible defaults for everything else, and state those assumptions in the draft.

### Step 2 — Draft using the template below

Use the sections that apply; cut the ones that don't. The order matters: the most load-bearing constraints go first or last, never buried in the middle.

### Step 3 — Run the self-audit before delivering

Deliver as a file the executor can paste or run directly, not just inline chat.

---

## The template (in this order)

**1. Goal + definition of done.**
One line on the outcome, one on what "finished and correct" looks like. This is the single most load-bearing element in any prompt, so it goes first. Don't bury it after background or context.

**2. Executor + context.**
Who or what is running this, what tools and access they have, and the minimum background needed to act. Note if the executor is running in a fresh session with no prior context.

**3. Scope — in AND out.**
State explicitly what is *not* in scope. Omitting this is the most common cause of drift. Collect all out-of-scope items in one place; don't scatter them across the document.

**4. Decisions locked.**
Enumerate choices that are frozen and not up for debate. This prevents future editors from unknowingly reopening settled questions and explains why constraints exist that would otherwise look arbitrary. Example: "Sort order: recency. LOCKED."

**5. Glossary / decode.**
Define every acronym, nickname, and term of art once, up front. Don't assume your shorthand is shared.

**6. Inputs / source of truth.**
Name exact documents or data with IDs or links. Instruct the executor to work from the source rather than paraphrasing from memory. Where accuracy matters, instruct a check back against the source before returning.

**7. External dependency protocols.**
For every data source the executor must fetch: what to do if it's unavailable. Options: (a) halt the entire run, (b) log and skip that item, (c) log and continue. Specify which. A prompt that says "read file X" but doesn't say what happens when X is unreadable will silently hallucinate or stall without guidance.

**8. Steps / rules.**
Numbered. One idea per rule. State each thing exactly once, clearly. If a rule appears elsewhere (for example in a gate definition), reference it — don't restate it.

**9. Output contract.**
The literal format: schema, columns, enums, length, ordering. Be exact. Designate one canonical place for every numeric target and reference from everywhere else.

**10. Worked example(s).**
At least one concrete input and its exact output. This is the highest-leverage section and the one most people skip. For content-generation prompts, a bad example showing a common failure is as valuable as a good one.

**11. HALT conditions.**
Distinct from the Do-NOT list. HALT conditions are mid-execution stop conditions: "If X is detected, stop immediately and emit this diagnostic." Specify the diagnostic format. Do NOT auto-continue after a HALT — require explicit instruction. HALT conditions apply *during* a run; Do-NOT items apply *before* it starts.

**12. Checkpoint design** *(for long-running prompts).*
At what intervals does the executor pause for human review? What does it surface at each pause? What are the options (continue / fix in place / halt and revise)? A mid-run checkpoint at 25% is far cheaper than discovering drift at 100%.

**13. Conflict-resolution rule.**
"If two instructions conflict, X wins." Long specs accumulate contradictions. Give a tie-breaker. For multi-source prompts (main body plus appendix), specify which governs per domain.

**14. Ambiguity default.**
What to do when an input is missing or unclear: stop and ask, or assume a named default. Pick one explicitly.

**15. Assumptions, stated.**
List what the prompt rests on so they're auditable and easy to correct.

**16. Do-NOT list.**
Sharp edges and known failure modes, as explicit prohibitions. Applied before execution begins.

**17. Self-verification step.**
Tell the executor to check its own work against the definition of done and output contract before returning — ideally as a concrete checklist it must pass.

**18. Failure history** *(for v2+ prompts).*
A section named "Why this version exists" or "What broke before." Name the prior failure modes, their root causes, and what changed. This is the highest-value thing a mature prompt can carry: it prevents re-discovering the same failures and explains why constraints exist that would otherwise look arbitrary.

---

## Rules this method enforces in every draft

- **Structure over length.** Headers, numbered rules, tables, explicit enums. A scannable two-page spec beats a rambling three-paragraph description and beats a ten-page wall of prose too.
- **Primacy and recency.** Put the most load-bearing constraints near the top or the very end. The middle is where instructions get lost. Goal and definition of done go first.
- **State once.** Each rule appears one time, unambiguously. The same point stated three ways reads as a contradiction and invites silent resolution. Designate canonical locations for recurring values and reference, don't restate.
- **Attention economy.** Every added rule competes with the rest for the executor's attention. Cut anything not doing work.
- **Examples beat description.** Show the output; don't only describe it. A bad-example and good-example pair is more constraining than either alone.
- **No undefined shorthand.** Define the vocabulary.
- **Name a tie-breaker and an ambiguity default** so the executor never has to silently guess.
- **Make success checkable.** Definition of done plus a self-check turns "hope it's right" into "verify it's right."
- **Anchor to source.** Cite the real documents and instruct checking against them rather than trusting a paraphrase.
- **State assumptions out loud.** Auditable beats hidden.
- **Specify failure behavior, not just success behavior.** For every external fetch and every checkpoint, name what happens on failure. A prompt that only describes the happy path will improvise on the sad path.
- **Make constraints model-computable.** If you require a measurement the model can't verify, convert it to something it can compute (for example, a readability target with the formula embedded). Soft measurements are only constraints if they're verifiable.

---

## The sections people forget

Most authors — even careful ones writing multi-page specs — nail the steps and output format but leave these out:

- A **definition of done** and a **self-verification checklist** (people specify the task, not the finish line)
- **Worked examples** (people give enums and rules but no input-to-output sample)
- A **conflict-resolution rule** and an **ambiguity default** (people don't say what happens when the spec contradicts itself or an input is missing)
- A **glossary** (people assume their shorthand travels)
- **Stated assumptions** and source-of-truth discipline
- An explicit **out-of-scope list**, collected in one place
- **External dependency protocols** (people say "read file X," not "if file X is unreadable, do Y")
- **HALT conditions** with a named diagnostic format
- **Checkpoint design** for long-running prompts
- **Failure history** for v2+ prompts
- **Decisions locked** (people explain what to do but not what's settled and off the table)

---

## Worked example — vague ask to architected prompt skeleton

**Before:** "Write me a prompt to summarize my weekly sales emails and flag what's important."

**After (skeleton this method would produce):**

- *Goal + done:* A weekly digest of sales-related email. "Done" = every thread from the last 7 days triaged, top 5 action items surfaced, nothing fabricated.
- *Executor:* an AI assistant with email access, running in a fresh session with no prior context.
- *Scope in:* threads labeled `sales`, last 7 days. *Scope out:* internal or HR mail, anything older, drafting replies.
- *Decisions locked:* Sort by recency, not urgency. LOCKED. One row per account, not per thread. LOCKED.
- *Glossary:* "hot lead" = replied within 24h and asked about pricing. "stalled" = no reply in 5+ days.
- *Source:* the email account, label `sales`. Read actual threads; quote, don't infer.
- *Dependency protocol:* if email is unreachable, halt and emit `=== HALT: email unavailable. Cannot proceed. ===`
- *Rules:* (1) group by deal or account; (2) one line of status per account; (3) flag hot leads and stalled deals.
- *Output contract:* markdown — a `## Top 5 actions` list, then a table: account | status | last touch | next step.
- *Example:* one filled-in table row with realistic values.
- *HALT condition:* if any thread has no account match: `=== HALT: unmatched thread [subject]. Awaiting instruction. ===`
- *Ambiguity default:* if a thread's deal is unclear, list it under "Unsorted" rather than guessing.
- *Assumptions:* email connector authenticated; threads go back at least 7 days; "sales" label exists.
- *Do-NOT:* invent figures; include non-sales mail; draft replies unless asked.
- *Self-check:* every `sales` thread from the window appears exactly once; no numbers stated that aren't in an email.

The same shape scales to a multi-page protocol. The sections don't change, only the depth.

---

## Self-audit before delivering

**Core (every prompt):**
- [ ] Goal + definition of done in the first lines?
- [ ] Executor context stated (who, what tools or access, fresh session if relevant)?
- [ ] In-scope AND out-of-scope both stated, collected in one place?
- [ ] Every acronym or term defined once?
- [ ] Sources named with links or IDs, plus "work from source, don't paraphrase" instruction?
- [ ] One idea per rule; nothing said three different ways?
- [ ] Output format literal, with at least one worked example?
- [ ] Conflict tie-breaker and ambiguity default present?
- [ ] Assumptions listed?
- [ ] Do-NOT list covers the known failure modes?
- [ ] A self-verification step the executor runs before returning?
- [ ] Most load-bearing constraints near top or end, not buried mid-document?
- [ ] Anything padded that could be cut?
- [ ] Every numeric target has one canonical location; other occurrences reference it?

**Long-running or multi-step prompts (also check):**
- [ ] External dependency protocols specified for every required fetch?
- [ ] HALT conditions defined with a named diagnostic format?
- [ ] Checkpoint design: where does executor pause for human review? What does it surface?
- [ ] Decisions-locked section enumerates frozen choices?
- [ ] Soft measurement requirements converted to something the executor can actually compute?

**v2+ prompts (also check):**
- [ ] "Why this version exists" section names prior failure modes and their root causes?
- [ ] Each fix traceable to a specific prior failure?

---

## One-paragraph version

Interview only for the forks that change the output. Draft with goal and definition of done first, scope and out-of-scope collected in one place, a glossary, source-of-truth anchors, numbered rules with one idea each, a worked example, HALT conditions, and a self-verification step at the end. Cut anything not doing work. Deliver as a file. The goal is not the longest prompt; it's the one where every instruction is findable, unambiguous, and paired with what happens if it fails.
