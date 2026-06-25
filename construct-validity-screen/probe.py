#!/usr/bin/env python3
"""Construct-divergence defect probe.

Two COLD model passes per MCQ, then a divergence score that flags
construct-invalid items WITHOUT any named rule and WITHOUT a per-topic
misconception bank:

  Pass A (rendered-item, no key)  -> is the intended answer reachable from
                                     surface cues? more than one defensible
                                     answer? how many options are even serious?
  Pass B (construct, key known)   -> does each distractor map to a REAL
                                     4th-grade misconception? is the item too
                                     guessable for an unmastered student?

Where A and B diverge (the item is exploitable / under-constrained in ways the
construct does not justify), that gap is an unnamed-defect CANDIDATE — handed to
a human, not auto-verdicted. Loud screen, candidates not verdicts.

Backend: any model behind a CLI (or API wrapper) listed in `backends.json`.
Each call is a fresh context = a genuinely blind solver. Defaults to the
`claude` CLI when no config is present, so the single-model path is unchanged.

Multi-model is OPTIONAL and capability-detected: configure additional families
in `backends.json` and the report layer fans each item across whichever ones are
reachable, then scores their AGREEMENT. This is a generic judge-panel layer — it
deliberately does NOT depend on any external orchestration/dispatch tooling, so
the folder stays self-contained and portable.
"""
import json, subprocess, argparse, re, sys, statistics, shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent

# A backend is just {name: {"cmd": [...with "{prompt}"...], "family": "...",
# "enabled": bool, "stdin": bool}}. "family" groups backends so two models from
# the same lab don't count as independent cross-family votes. Keep secrets OUT of
# this file — adapters should read API keys from the environment, not config.
DEFAULT_BACKEND = {"claude": {"cmd": ["claude", "-p", "{prompt}"], "family": "anthropic", "enabled": True}}


def load_backends():
    # backends.local.json (gitignored, never packaged) overrides the shipped
    # template — so your real multi-model wiring stays private and only the
    # generic placeholder config travels with a release.
    for fn in ("backends.local.json", "backends.json"):
        cfg = HERE / fn
        if cfg.exists():
            return json.loads(cfg.read_text())
    return dict(DEFAULT_BACKEND)


def reachable_backends(backends=None):
    """Capability detection: keep only enabled backends whose executable resolves.
    Returns {} -> caller falls back to the default single-model path."""
    out = {}
    for name, spec in (backends or load_backends()).items():
        if name.startswith("_") or not isinstance(spec, dict) or "cmd" not in spec:
            continue  # skip comment / non-backend keys
        if spec.get("enabled", True) and shutil.which(spec["cmd"][0]):
            out[name] = spec
    return out


def ask(prompt, backend=None, timeout=180):
    cmd_tmpl = (backend or DEFAULT_BACKEND["claude"])["cmd"]
    via_stdin = bool((backend or {}).get("stdin"))
    raw = ""
    for attempt in range(2):
        p = prompt if attempt == 0 else prompt + "\n\nReturn ONLY the JSON object. No prose. No code fences."
        if via_stdin:
            argv = [a for a in cmd_tmpl if a != "{prompt}"]
            r = subprocess.run(argv, input=p, capture_output=True, text=True, timeout=timeout)
        else:
            argv = [a.replace("{prompt}", p) for a in cmd_tmpl]
            # close stdin: some CLIs (e.g. codex exec) otherwise block waiting on it
            r = subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=timeout)
        raw = (r.stdout or "").strip()
        m = re.search(r"\{.*\}", raw, re.S)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                continue
    raise ValueError(f"could not parse JSON from model. raw head:\n{raw[:400]}")


def letters(item):
    return [k for k in ("a", "b", "c", "d", "e") if item["options"].get(k)]


def pass_a(item, backend=None):
    L = letters(item)
    opts = "\n".join(f"{k.upper()}. {item['options'][k]}" for k in L)
    prompt = f"""You are shown a multiple-choice question exactly as a 4th-grade student sees it. You do NOT have the answer key.

QUESTION: {item['stem']}
OPTIONS:
{opts}

Analyze it for ITEM QUALITY, not to get it right. Return ONLY a JSON object:
{{"answerable_without_content": <true|false>, "cue_type": "<length|grammar|only-serious-option|stem-telegraph|none>", "serious_options_count": <int>, "num_defensible_answers": <int>, "best_guess": "<A|B|C|D|E>", "note": "<one sentence>"}}"""
    return ask(prompt, backend)


def pass_b(item, backend=None):
    L = letters(item)
    key = item["key"]
    dist = "\n".join(f"{k.upper()}. {item['options'][k]}" for k in L if k != key)
    prompt = f"""You are an expert assessment designer. Here is the standard, stem, and intended correct answer for a 4th-grade MCQ.

STANDARD/OBJECTIVE: {item['standard']} — {item['objective']}
STEM: {item['stem']}
INTENDED CORRECT ANSWER: {item['options'][key]}
DISTRACTORS:
{dist}

A well-built distractor represents a SPECIFIC misconception a real 4th grader would plausibly hold. Evaluate each distractor. Return ONLY a JSON object:
{{"distractors":[{{"option":"<letter>","maps_to_misconception":<true|false>,"misconception":"<student error, or null>"}}], "expected_unmastered_difficulty":"<near-chance|somewhat-easy|too-easy>", "multiple_keys_possible":<true|false>, "note":"<one sentence>"}}"""
    return ask(prompt, backend)


STRUCTURAL_CUES = {"length", "grammar", "stem-telegraph"}  # construct-irrelevant by definition


def score(a, b):
    """Divergence model — the score IS the gap between the two reads, not a sum of
    independent flaws.

    A defect candidate is an item the surface lens (A) can exploit in a way the
    construct lens (B) does not justify. So heavy weight is reserved for places
    where the two lenses CORROBORATE (both point to the same break); a finding from
    a single lens is downgraded to a soft candidate, and an A-vs-B disagreement is
    surfaced as an explicit *lens conflict* for the reviewer rather than silently
    summed. This makes the operationalization match the claim: divergence-gated, not
    additive. The only signal allowed to gate alone is a structural cue (length/
    grammar/stem-telegraph) — surface reaching the key with zero construct mastery
    is intrinsic divergence, no corroboration needed."""
    s, reasons = 0.0, []
    cue = a.get("cue_type")
    answerable = bool(a.get("answerable_without_content"))
    too_easy = b.get("expected_unmastered_difficulty") == "too-easy"
    too_easy_used = False
    dead = [d for d in b.get("distractors", []) if d.get("maps_to_misconception") is False]
    nd = len(dead)
    a_ambig = bool(a.get("num_defensible_answers", 1) and a.get("num_defensible_answers", 1) > 1)
    b_ambig = bool(b.get("multiple_keys_possible"))
    serious = a.get("serious_options_count")

    # Channel 1 — surface-reachable answer the construct does not justify.
    if answerable and cue in STRUCTURAL_CUES:
        s += 3; reasons.append(f"surface giveaway via {cue} — key reachable with no construct mastery (intrinsic divergence)")
    elif answerable and cue == "only-serious-option":
        # elimination exploit: a real defect ONLY if the construct lens agrees the
        # item is under-demanding (too-easy, or carrying dead distractors).
        if too_easy or nd >= 1:
            s += 2; too_easy_used = too_easy
            reasons.append("elimination exploit, construct-corroborated (A: one serious option; B: under-demanding)")
        else:
            s += 1; reasons.append("lens conflict — A finds it guessable, B finds it sound (reviewer adjudicates)")
    elif answerable:
        s += 1; reasons.append("surface read reached the key without a named cue (soft, single-lens)")

    # Channel 2 — dead distractors, weighted by whether the surface lens corroborates
    # that they are actually eliminable. Both lenses agreeing = full weight.
    if nd:
        surface_confirms = answerable or (serious is not None and serious <= 2)
        per = 2 if surface_confirms else 1
        s += per * nd
        how = "both lenses agree (dead AND eliminable)" if surface_confirms else "construct-only, surface not corroborating (soft)"
        reasons.append(f"{nd} distractor(s) map to no real misconception — {how}")

    # Channel 3 — ambiguity: corroboration upgrades, a single lens stays soft.
    if a_ambig and b_ambig:
        s += 3; reasons.append("multiple defensible answers — BOTH lenses agree (high confidence)")
    elif a_ambig or b_ambig:
        s += 1; reasons.append(f"multiple defensible answers — {'surface' if a_ambig else 'construct'} lens only (soft)")

    # Residual construct-only difficulty concern (not already used to corroborate above).
    if too_easy and not too_easy_used and not (answerable and cue == "only-serious-option"):
        s += 1; reasons.append("construct lens alone flags it too guessable for an unmastered student (soft)")
    return s, reasons


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", default=str(HERE / "items.json"))
    ap.add_argument("--ids", nargs="*", help="run only these item ids")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--out", default=str(HERE / "results.md"))
    args = ap.parse_args()

    items = json.loads(Path(args.items).read_text())
    if args.ids:
        items = [i for i in items if i["id"] in args.ids]
    if args.limit:
        items = items[: args.limit]

    rows = []
    for it in items:
        try:
            a, b = pass_a(it), pass_b(it)
            sc, reasons = score(a, b)
        except Exception as e:
            print(f"  ! {it['id']}: {e}", file=sys.stderr)
            continue
        rows.append({"id": it["id"], "label": it["label"], "score": sc, "reasons": reasons})
        print(f"  {it['id']:42s} score={sc:4.1f}  [{it['label']}]")

    rows.sort(key=lambda r: -r["score"])
    clean = [r["score"] for r in rows if r["label"] == "clean"]
    defect = [r["score"] for r in rows if r["label"] != "clean"]

    auc = None
    if clean and defect:
        wins = sum((d > c) + 0.5 * (d == c) for d in defect for c in clean)
        auc = wins / (len(defect) * len(clean))

    out = ["# Construct-divergence probe — results\n"]
    if auc is not None:
        out.append(
            f"**Separation (clean vs defect):** mean clean = {statistics.mean(clean):.1f}, "
            f"mean defect = {statistics.mean(defect):.1f}, ranking AUC = {auc:.2f}\n"
        )
    out += ["| rank | item | label | score | why flagged |", "|---|---|---|---|---|"]
    for i, r in enumerate(rows, 1):
        out.append(f"| {i} | {r['id']} | {r['label']} | {r['score']:.1f} | {'; '.join(r['reasons']) or '—'} |")
    Path(args.out).write_text("\n".join(out) + "\n")

    print(f"\nwrote {args.out}")
    if auc is not None:
        print(f"ranking AUC (defect ranked above clean) = {auc:.2f}")


if __name__ == "__main__":
    main()
