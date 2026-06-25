#!/usr/bin/env python3
"""Construct-Validity Screen — internal QC review report.

Runs the two-cold-pass construct-divergence engine (probe.py) over a batch of
real items and renders a clean, reviewer-facing report: a ranked worst-first
table plus an evidence card for each elevated item (what the surface read saw,
what the construct read saw, and a suggested action).

Screen, not verdict. Every elevated item is a CANDIDATE for human review.

Usage:
    python3 report_qc.py --items batch.json --out review-report.md [--label "Batch name"]
"""
import json, argparse, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import probe  # same-dir engine; identical to the synthetic build

ELEVATED = 5.0  # score at/above this = flagged for reviewer attention (screen, not verdict)


def analyze(item, runs=3, backend=None):
    """Run the two-cold-pass engine `runs` times and elevate on the WORST case.

    The screen is non-deterministic on exactly the borderline items it exists to
    adjudicate (the 🟡/🔴 margin). A single run lets a defect item flip under the
    threshold by luck. So we sample `runs` times, keep the highest-scoring read
    for the review card, and report the score envelope (min–max) so a reviewer
    can see how stable each flag is. Worst-of-N is the conservative choice for a
    miss-averse screen.

    `backend` selects which model judges (None = default single-model path). The
    rerun envelope here is WITHIN one family (sampling noise); cross-family spread
    is a separate axis computed in analyze_panel."""
    best, scores = None, []
    for _ in range(runs):
        a, b = probe.pass_a(item, backend), probe.pass_b(item, backend)
        sc, reasons = probe.score(a, b)
        scores.append(sc)
        if best is None or sc > best["score"]:
            best = {"item": item, "a": a, "b": b, "score": sc, "reasons": reasons}
    best["score_min"], best["score_max"], best["runs"] = min(scores), max(scores), runs
    return best


def analyze_panel(item, families, runs=1):
    """Cross-family panel: judge the item with each available family, then score
    their AGREEMENT — a confidence axis kept deliberately separate from the
    within-family rerun envelope.

    Loud identity preserved: the reported score is the WORST family's score (any
    family that elevates surfaces the item). But the card now also says HOW MANY
    families concurred — a flag all four families raise is high-confidence; one only
    a single family raises is a cross-family conflict the reviewer adjudicates. One
    family's priors about students no longer decide alone."""
    per, failed = {}, []  # family name -> per-family analyze() result; families that errored
    for name, spec in families.items():
        try:
            per[name] = analyze(item, runs=runs, backend=spec)
        except Exception as e:
            failed.append(name)  # one flaky family must not void the whole item
            print(f"    · {item.get('id','?')}/{name} failed: {str(e)[:80]}", file=sys.stderr)
    scored = {n: r for n, r in per.items() if r["score"] is not None}
    if not scored:  # every family failed — surface as unscored, never silently dropped
        return {"item": item, "a": {}, "b": {}, "score": None,
                "reasons": [f"unscored — all {len(families)} families errored: {', '.join(failed)}"]}
    by_fam = {n: r["score"] for n, r in scored.items()}
    worst = max(scored.values(), key=lambda r: r["score"])  # drives the card + loud score
    elevated_fams = [n for n, s in by_fam.items() if s >= ELEVATED]
    n_fam = len(scored)

    agree = f"{len(elevated_fams)}/{n_fam} families elevate"
    if elevated_fams and len(elevated_fams) == n_fam:
        xf = f"cross-family CONSENSUS — all {n_fam} families elevate (high confidence)"
    elif elevated_fams:
        others = [n for n in scored if n not in elevated_fams]
        xf = (f"cross-family conflict — {', '.join(elevated_fams)} elevate; "
              f"{', '.join(others)} find it sound (reviewer adjudicates) [{agree}]")
    else:
        xf = f"no family elevates ({agree})"

    out = dict(worst)  # inherit the worst family's a/b/score/envelope for the card
    out["reasons"] = list(worst["reasons"]) + [xf]
    if failed:  # honor "all models' output" — never hide that a family dropped out
        out["reasons"].append(f"⚠️ {len(failed)} family/families errored on this item ({', '.join(failed)}); agreement computed over the {len(scored)} that returned")
    out["families"] = by_fam
    out["failed_families"] = failed
    out["elevated_families"] = elevated_fams
    out["xfam_min"], out["xfam_max"] = min(by_fam.values()), max(by_fam.values())
    out["panel"] = True
    return out


def card(r):
    it, a, b = r["item"], r["a"], r["b"]
    L = probe.letters(it)
    env = (f" (envelope {r['score_min']:.1f}–{r['score_max']:.1f} over {r['runs']} runs)"
           if r.get("runs", 1) > 1 and r.get("score_min") != r.get("score_max") else "")
    lines = [f"### {it.get('id','(item)')} — score {r['score']:.1f}{env}", ""]
    lines.append(f"**Standard/objective:** {it.get('standard','?')} — {it.get('objective','?')}")
    lines.append(f"**Stem:** {it['stem']}")
    keyed = it.get("key")
    for k in L:
        mark = "  ✅ keyed" if k == keyed else ""
        lines.append(f"- **{k.upper()}.** {it['options'][k]}{mark}")
    lines.append("")
    # surface read
    cue = a.get("cue_type", "?")
    lines.append(f"**Surface read (key hidden):** answerable from surface = "
                 f"`{a.get('answerable_without_content')}`"
                 + (f", cue = `{cue}`" if cue and cue != "none" else "")
                 + f", defensible answers = {a.get('num_defensible_answers','?')}"
                 + f", serious options = {a.get('serious_options_count','?')}.")
    if a.get("note"):
        lines.append(f"  > {a['note']}")
    # construct read
    bad = [d.get("option","?").upper() for d in b.get("distractors", []) if d.get("maps_to_misconception") is False]
    lines.append(f"**Construct read (key known):** unmastered difficulty = "
                 f"`{b.get('expected_unmastered_difficulty','?')}`"
                 + (f", distractors with NO real misconception: {', '.join(bad)}" if bad else ", distractors map to real misconceptions")
                 + (f", multiple defensible keys = `{b.get('multiple_keys_possible')}`" if b.get("multiple_keys_possible") else "") + ".")
    if b.get("note"):
        lines.append(f"  > {b['note']}")
    lines.append("")
    lines.append(f"**Why flagged:** {'; '.join(r['reasons']) or '—'}")
    lines.append(f"**Suggested action:** {suggest(r)}")
    lines.append("")
    return "\n".join(lines)


def suggest(r):
    a, b = r["a"], r["b"]
    if a.get("num_defensible_answers", 1) > 1 or b.get("multiple_keys_possible"):
        return "Tighten the stem or options — more than one answer is defensible."
    bad = [d for d in b.get("distractors", []) if d.get("maps_to_misconception") is False]
    if len(bad) >= 2:
        return "Rebuild the weak distractors to target real student misconceptions."
    if a.get("cue_type") in ("length", "grammar"):
        return f"Remove the {a.get('cue_type')} cue that telegraphs the key."
    if a.get("answerable_without_content") and b.get("expected_unmastered_difficulty") == "too-easy":
        return "Item is answerable without the target knowledge — raise the construct demand."
    return "Human review: borderline signal."


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", required=True)
    ap.add_argument("--out", default="review-report.md")
    ap.add_argument("--label", default="item batch")
    ap.add_argument("--workers", type=int, default=5, help="items screened concurrently")
    ap.add_argument("--runs", type=int, default=3, help="cold-pass repetitions per item (worst-of-N; 1 = fastest, less stable)")
    ap.add_argument("--multi", action="store_true",
                    help="cross-family panel: judge each item with every reachable backend in backends.json and score their agreement")
    args = ap.parse_args()

    # Capability detection — the panel runs only across backends that are both
    # enabled in backends.json AND actually resolve on this machine. Falls back to
    # the default single-model path when <2 are reachable, so the tool degrades
    # gracefully on a box that only has one model wired.
    families = probe.reachable_backends() if args.multi else {}
    panel = len(families) >= 2
    if args.multi and not panel:
        print(f"  --multi requested but only {len(families)} backend reachable "
              f"({', '.join(families) or 'none'}); running single-model.")
    runs = 1 if panel else args.runs  # families provide diversity; don't multiply calls
    if panel:
        print(f"  panel: {len(families)} families — {', '.join(families)}")

    def work(it):
        return analyze_panel(it, families, runs=runs) if panel else analyze(it, args.runs)

    items = json.loads(Path(args.items).read_text())
    rows = []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(work, it): it for it in items}
        for fut in as_completed(futs):
            it = futs[fut]
            try:
                rows.append(fut.result())
                print(f"  ok {it.get('id','?')}")
            except Exception as e:
                # T9: never silently drop. A screen that loses items it cannot
                # parse fails in the one direction it must not — surface them.
                rows.append({"item": it, "a": {}, "b": {}, "score": None,
                             "reasons": [f"unscored — engine error: {e}"]})
                print(f"  ! {it.get('id','?')}: {e}  (surfaced as ⚠️ unscored)")
    # unscored (score None) sort to the very top — they need manual eyes most.
    rows.sort(key=lambda r: -(r["score"] if r["score"] is not None else 1e9))

    elevated = [r for r in rows if r["score"] is not None and r["score"] >= ELEVATED]
    unscored = [r for r in rows if r["score"] is None]
    pct = (100 * len(elevated) / len(rows)) if rows else 0

    out = []
    out.append(f"# Construct-Validity Screen — {args.label}\n")
    out.append("*Two cold reads per item (surface vs construct); the gap is the signal. "
               "A screen that narrows the haystack — every flag is a candidate for human review, not a verdict.*\n")
    runs_used = next((r["runs"] for r in rows if r.get("runs")), args.runs)
    method = (f"{len(families)}-family panel — {', '.join(families)}" if panel
              else f"worst-of-{runs_used} runs")
    unscored_note = f" · {len(unscored)} ⚠️ unscored (engine error — manual review)" if unscored else ""
    out.append(f"**{len(rows)} items screened · {len(elevated)} elevated for review "
               f"({pct:.0f}%) · threshold {ELEVATED:.0f} · {method}{unscored_note}.**\n")
    out.append("## Ranked (worst first)\n")
    if panel:
        out.append("| rank | item | score | families | agree | flag | why |")
        out.append("|---|---|---|---|---|---|---|")
    else:
        out.append("| rank | item | score | envelope | flag | why |")
        out.append("|---|---|---|---|---|---|")
    for i, r in enumerate(rows, 1):
        if r["score"] is None:
            flag, score_str, env = "⚠️ unscored", "—", "—"
        else:
            flag = "🔴 review" if r["score"] >= ELEVATED else ("🟡 watch" if r["score"] >= 3 else "🟢 ok")
            score_str = f"{r['score']:.1f}"
            env = (f"{r['score_min']:.1f}–{r['score_max']:.1f}"
                   if r.get("runs", 1) > 1 and r["score_min"] != r["score_max"] else "stable")
        rid = r["item"].get("id", "?")
        if panel:
            fams = r.get("families", {})
            spread = (f"{r.get('xfam_min',0):.1f}–{r.get('xfam_max',0):.1f}"
                      if r.get("score") is not None and r.get("xfam_min") != r.get("xfam_max") else "stable")
            agree = (f"{len(r.get('elevated_families', []))}/{len(fams)}" if fams else "—")
            out.append(f"| {i} | {rid} | {score_str} | {spread} | {agree} | {flag} | {'; '.join(r['reasons']) or '—'} |")
        else:
            out.append(f"| {i} | {rid} | {score_str} | {env} | {flag} | {'; '.join(r['reasons']) or '—'} |")
    out.append("")
    if elevated:
        out.append("## Review cards — elevated items\n")
        out += [card(r) for r in elevated]
    out.append("---")
    out.append("*Construct-divergence screen. Surface read = item with the answer key hidden; "
               "construct read = item judged against its standard. Calibration ceiling is empirical "
               "student-outcome data; this is a pre-outcome screen.*")
    out.append("")
    if panel:
        out.append(f"*Limits: judged by a {len(families)}-family panel ({', '.join(families)}); "
                   "the `agree` column is how many families independently elevate — a consensus flag is "
                   "high-confidence, a split flag (cross-family conflict) leans on the reviewer. \"Real "
                   "misconception\" is now cross-checked across families, but all families can still share a "
                   "blind spot, so flags remain candidates, not verdicts. Items that errored are listed "
                   "⚠️ unscored, never dropped.*")
    else:
        out.append("*Limits: a single model family does the judging, so \"real misconception\" reflects "
                   "that model's priors about students, not a cross-checked consensus — treat family-specific "
                   "flags as candidates. Re-run with `--multi` (configure backends.json) to add a cross-family "
                   "agreement check. Scores are worst-of-N across reruns; a wide envelope means the flag "
                   "is unstable and leans on the reviewer. Items that errored are listed ⚠️ unscored, never dropped.*")
    Path(args.out).write_text("\n".join(out) + "\n")
    print(f"wrote {args.out} — {len(rows)} screened, {len(elevated)} elevated")


if __name__ == "__main__":
    main()
