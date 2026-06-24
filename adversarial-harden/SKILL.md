---
name: adversarial-harden
description: Harden a freshly-written precision-critical or security-critical piece of code by fanning out parallel adversarial reviewers from DIFFERENT model families that try to BREAK it (each verifying findings empirically by running the code), then integrating fixes by severity with a regression test per fix. Use right after authoring detectors, classifiers, parsers, permission checks, persistence layers, file walkers, token/crypto handling, or anything where a false positive, a data leak, an auth bypass, or a silent correctness bug would be costly.
---

# Adversarial Harden — break it before it ships

Self-review misses the bugs that matter most: the symlink that reads across a trust boundary, the env var that silently disables a "permanent" ban, the regex that fires on the one input you didn't picture. You wrote the code holding a mental model, and that same model blinds you to its failure modes. The fix is **independent adversaries that try to break it and PROVE the break by running it**, not by eyeballing.

This is a **build → harden → integrate** loop. It is cheap, repeatable, and pays for itself the first time it finds a leak.

## When it's worth it (and when it isn't)

Run it when a defect is **expensive or hard to detect later**: false positives on a high-precision surface, any trust/permission boundary, auth/token logic, a parser or classifier facing adversarial input, a new persistence layer (concurrency, leaks, partial writes), a file walker (symlinks, traversal). Skip it for trivial edits, pure refactors already under test, or subjective/style work.

Scale the fan-out to the risk: 2 reviewers for a normal precision/correctness pass, 3–4 (add a dedicated security reviewer and a concurrency reviewer) for anything touching a boundary, money, or credentials.

**Also works on publish-bound prose / claims docs.** Same loop, different attack angles: (a) legal/defamation — does any line name or implicate a real party, or read as a threat? (b) credibility — is any claim false, staged, or unsupportable, would a skeptical expert refute it? (c) leak — does it give away more than intended? State what's APPROVED up front (intended examples, the call to action) so reviewers don't burn findings false-flagging your intent.

## The loop

### 1. Build the core yourself
Write the precision/security-critical piece with the full context you hold — the contract, the invariants, the data model. Don't delegate the core; delegate the *attack*. Get it to a state where it runs and its own tests pass. **State the invariants explicitly** ("this fires only on a genuine placeholder, never on prose"; "this handle is always closed"). The reviewers need these to know what counts as a break. For boundary code, also state what is **APPROVED** (which paths/processors are in-policy), not just what's forbidden — otherwise reviewers waste findings flagging an in-policy path as a breach.

### 2. Harden — fan out parallel adversaries from OTHER model families

**The key rule: the adversary that tries to break the code must be a different model family from the one that wrote it.** A model attacking its own code shares the author's blind spots; it reliably clears the bug a different family catches. (In practice: a same-family reviewer passed an XSS that a rival family broke on its first probe.) The author writes the core and **integrates**; the other families attack.

Give each adversary a **distinct angle** so they don't overlap:

- **Precision / false-positive attacker** — for detectors, classifiers, matchers, filters. Find inputs that SHOULD NOT trigger but do (the cardinal sin for a high-precision surface), and genuine inputs that are MISSED. Bias toward realistic inputs from the actual domain.
- **Security / boundary / edge-case auditor** — for anything touching a boundary, secret, or the filesystem. Find any path that breaches the stated invariant: symlinks/realpath, sidecar files (e.g. SQLite `-wal`/`-shm`/`-journal`), traversal, env vars that weaken an invariant, fallback paths that bypass the guard, error handling that masks a breach.
- **Correctness / concurrency auditor** (add for persistence/stateful code) — resource lifecycle (handles not closed), races between writers, time/ordering bugs, partial-write/atomicity, malformed-row handling, off-by-one in liveness/dedup logic.

**Non-negotiable for every reviewer: verify empirically.** The reviewer must import/run the actual code, construct throwaway inputs (temp dirs, crafted strings, monkeypatched config), and *demonstrate* each finding — observed vs. expected. A plausible-sounding finding that wasn't run is a hypothesis, not a finding, and wastes integration time. Reviewers return findings; they don't edit (the author integrates, so fixes stay coherent).

> If your harness/sandbox blocks the reviewer from writing under the repo (some test suites write artifacts/DBs), have it redirect the write root to a temp dir (a `TMPDIR`/`ARTIFACTS_DIR` override, or a monkeypatched config) before running the suite, or fall back to no-write repros. Don't treat a blocked write-lane as a failed review — cross-check its findings against a lane that ran the full suite.

### 3. Demand a structured, severity-ranked return
Each reviewer returns a **ranked, deduped list, worst-first**, capped (~10–12) so you get signal not noise. Per finding: exact scenario/input, observed vs. expected, **severity** (CRITICAL for any leak/breach/auth-bypass · high · med · low), one-line root cause, one-line fix. Plus a one-line verdict (SAFE / NEEDS-FIX). Terse — it feeds your integration, it isn't an essay.

### 4. Integrate by severity — you are the integrator
Triage all findings together (the reviewers are blind to each other; you dedupe and resolve conflicts). Fix **CRITICAL and high first**; for each fix, **add a regression test that fails before and passes after** — the test is what makes the hardening durable instead of a one-time cleanup. Accept low-severity findings consciously, and say why if you're not fixing one. Resolve cross-reviewer tension explicitly (e.g. a concurrency reviewer wanting WAL vs. a security reviewer warning WAL sidecars carry bytes next to a secret DB → keep DELETE journaling and document why).

### 5. Re-verify and record
Re-run the full test suite. Re-run the reviewers' own adversarial inputs against the fixed code to confirm the breaks are closed. Briefly record what was found and fixed so the next change knows the threat model.

## A standing threat checklist (start here, don't stop here)

Most real findings cluster on a short list of "new surface" failure modes. Skim it before you even spawn the reviewers:

- **Filesystem:** symlinks (read across a boundary; `realpath`-reclassify, don't trust the lexical path), traversal, size/DoS, non-UTF8, permission errors swallowed silently.
- **Boundaries/secrets:** env vars that weaken an invariant ("permanent" should not be one var away from off), fallback/except paths that bypass the guard, sidecar/temp/journal files that carry protected bytes to an unprotected location, anything that classifies by name instead of by resolved identity.
- **Persistence:** connection/handle lifecycle (a `with sqlite3.connect()` commits but does NOT close), concurrent writers, atomicity of writes, time-granularity collisions in liveness/dedup keys, malformed rows poisoning a batch.
- **Matchers:** the marker/word that appears in prose, code, quotes, or meta-discussion vs. genuine use; case/locale; links and brackets; the common real form you forgot.
- **Extraction from untrusted text:** when a parser pulls a KNOWN field set out of untrusted input (frontmatter, headers, a config block), **allowlist the fields — don't try to perfectly detect the boundary.** Boundary detection is endlessly breakable; an allowlist of expected keys makes the whole class structurally impossible because only the fields you already render survive.

The checklist is a prior, not a substitute — the reviewers exist to find what isn't on it.

## How to run the fan-out

If you have CLIs for multiple model families, dispatch the same brief to each in parallel and collect their findings. If you only have one model available, the weak substitute is a single model running multiple *diverse-lens* reviewer passes — better than nothing, but a real second family is the asset, because independence is the whole point.
