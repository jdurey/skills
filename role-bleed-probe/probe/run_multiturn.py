#!/usr/bin/env python3
"""
run_multiturn.py — FAITHFUL reproduction of the actor->supervisor role-bleed.

The synthetic single-shot probe (run_probe.py) measures paired-condition deltas but
rarely reproduces the FULL break, because the real collapse needs the regime a
ground-truth trace shows: a MULTI-TURN, QC-framed agentic session with real tool
work and accumulating context. This driver recreates that. For each condition it:

  - makes a throwaway workdir, seeds it with the editor fixtures,
  - delivers a SEQUENCE of briefs to ONE agent session:
        turn 1 : <adapter.cmd>            (creates the session for this cwd)
        turn k : <adapter.continue_cmd>   (continues the SAME session)
  - captures each turn's reasoning stream and scores it with markers.json,
  - records per (condition, rep, turn) which markers fired, especially self_naming_3p.

The signal is WITHIN-model and longitudinal: does leakage appear and ESCALATE across
turns under qc_framed, vs stay clean under the plain control (same work, flat voice)?

MODEL: pass --model <name> (default grok). The model MUST have continue_cmd +
multiturn_capable:true in adapters.json (session continuation is what makes turn 2+
land on the SAME accumulating context). The runner refuses non-multiturn adapters.

HARNESS-VALIDITY GATE: you must capture the model's REASONING channel, not just its
final answer. For grok that means the verbose trace (and ideally
--output-format streaming-json, scoring type:thought events); the plain answer stream
can hide the dissociation entirely and yield false nulls. Confirm reasoning_chars is
large on a known-positive condition before trusting any clean result.

SAFETY: dry-run by default (renders the brief sequence, no model calls). --yes to dispatch.
The work is on throwaway fixtures in temp dirs; nothing real is touched.

Usage:
    python3 run_multiturn.py                                   # dry run
    python3 run_multiturn.py --yes --n 5                       # qc_framed + plain, grok
    python3 run_multiturn.py --yes --n 5 --model grok --check  # add the CLI self-verify loop
    python3 run_multiturn.py --summarize mt_results.jsonl
"""
import argparse
import json
import os
import shutil
import subprocess
import tempfile
import time
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
import sys
sys.path.insert(0, str(HERE))
from score import load_markers, score  # noqa: E402


def load_json(name):
    return json.loads((HERE / name).read_text())


def seed_fixtures(workdir, fixtures_rel):
    src = HERE / fixtures_rel
    n = 0
    for f in sorted(src.glob("*")):
        if f.is_file():
            shutil.copy(f, Path(workdir) / f.name)
            n += 1
    return n


def build_cmd(template, prompt, workdir, turns, check_flag=None):
    out = []
    for tok in template:
        tok = (tok.replace("{PROMPT}", prompt)
                  .replace("{WORKDIR}", workdir)
                  .replace("{TURNS}", str(turns))
                  .replace("{HOME}", os.path.expanduser("~")))
        out.append(tok)
    if check_flag:
        out.append(check_flag)
    return out


def dispatch(cmd, workdir, timeout, reasoning):
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                           cwd=workdir, stdin=subprocess.DEVNULL)
        out, err, rc = p.stdout, p.stderr, p.returncode
    except subprocess.TimeoutExpired as e:
        out, err, rc = (e.stdout or ""), (e.stderr or ""), 124
    if reasoning == "stderr":
        text = err or ""
    elif reasoning == "stdout":
        text = out or ""
    else:
        text = (err or "") + "\n" + (out or "")
    return text, rc, round(time.time() - t0, 1)


def run(args):
    briefs = load_json("briefs.json")
    adapters = load_json("adapters.json")["adapters"]
    a = adapters.get(args.model)
    if not a:
        print(f"  !! no adapter for '{args.model}' in adapters.json")
        return
    if not a.get("multiturn_capable") or not a.get("continue_cmd"):
        print(f"  !! adapter '{args.model}' has no session continuation "
              f"(multiturn_capable/continue_cmd) — the multi-turn driver needs it. "
              f"Add a continue_cmd or use run_probe.py for single-shot.")
        return

    markers = load_markers(model_name=a.get("model_name"))
    reasoning = a.get("reasoning", "both")
    check_flag = a.get("check_flag") if args.check else None
    if args.check and not check_flag:
        print(f"  ~~ --check ignored: adapter '{args.model}' declares no check_flag")
    conditions = briefs["conditions"]
    fixtures = briefs["fixtures"]

    total = len(conditions) * args.n * max(len(v) for v in conditions.values())
    print(f"model={args.model}  conditions={list(conditions)}  reps={args.n}  "
          f"turns/condition={ {k: len(v) for k, v in conditions.items()} }")
    print(f"check={bool(check_flag)}  reasoning_stream={reasoning}  => up to {total} agent calls")

    if not args.yes:
        print("\nDRY RUN. Re-run with --yes to dispatch. Brief sequence (qc_framed):")
        for i, b in enumerate(conditions["qc_framed"], 1):
            head = b.replace("{WORKDIR}", "<WORKDIR>").splitlines()[0]
            print(f"  turn {i}: {head[:100]}")
        return

    out_path = Path(args.out)
    tdir = out_path.parent / "mt_traces"
    tdir.mkdir(exist_ok=True)
    n_done = 0
    with out_path.open("w") as fh:
        for cond, turn_briefs in conditions.items():
            for rep in range(args.n):
                workdir = tempfile.mkdtemp(prefix=f"mt_{cond}_")
                seed_fixtures(workdir, fixtures)
                for turn, brief in enumerate(turn_briefs, 1):
                    prompt = brief.replace("{WORKDIR}", workdir)
                    template = a["cmd"] if turn == 1 else a["continue_cmd"]
                    cmd = build_cmd(template, prompt, workdir, args.turns, check_flag)
                    text, rc, elapsed = dispatch(cmd, workdir, args.timeout, reasoning)
                    sc = score(text, markers)
                    tf = tdir / f"{args.model}_{cond}_r{rep}_t{turn}.txt"
                    tf.write_text(text)
                    rec = {"model": args.model, "condition": cond, "rep": rep, "turn": turn,
                           "leaked": sc["leaked"], "n_markers": sc["n_markers"],
                           "fired": sc["fired"], "rc": rc, "elapsed": elapsed,
                           "reasoning_chars": len(text), "trace_file": tf.name}
                    fh.write(json.dumps(rec) + "\n")
                    fh.flush()
                    n_done += 1
                    print(f"  [{n_done}] {cond} r{rep} t{turn} "
                          f"leaked={sc['leaked']} fired={sc['fired']} "
                          f"chars={len(text)} {elapsed}s")
                shutil.rmtree(workdir, ignore_errors=True)
    print(f"\nwrote {n_done} records to {out_path}")
    summarize(out_path)


def summarize(path):
    rows = [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]
    if not rows:
        print("no records")
        return
    by = defaultdict(list)
    for r in rows:
        by[(r["condition"], r["turn"])].append(r)
    print("\n=== leak rate by condition x turn (does it escalate?) ===")
    print(f"{'condition':12} {'turn':>4} {'n':>3} {'leak%':>6}  markers")
    for key in sorted(by):
        rs = by[key]
        leak = 100 * sum(r["leaked"] for r in rs) / len(rs)
        fired = defaultdict(int)
        for r in rs:
            for m in r["fired"]:
                fired[m] += 1
        ms = ",".join(f"{k}:{v}" for k, v in sorted(fired.items())) or "-"
        print(f"{key[0]:12} {key[1]:>4} {len(rs):>3} {leak:>5.0f}%  {ms}")
    # self_naming_3p is the headline; report it separately
    print("\n=== self_naming_3p hits — the cleanest signal ===")
    for cond in sorted(set(r["condition"] for r in rows)):
        hits = [(r["rep"], r["turn"]) for r in rows
                if r["condition"] == cond and "self_naming_3p" in r["fired"]]
        print(f"  {cond:12}: {len(hits)} hits  {hits if hits else ''}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="grok", help="adapter name (must be multiturn_capable)")
    ap.add_argument("--n", type=int, default=5, help="replicates per condition")
    ap.add_argument("--turns", type=int, default=30, help="max agent turns per call")
    ap.add_argument("--timeout", type=int, default=420)
    ap.add_argument("--check", action="store_true",
                    help="append the CLI's own self-verification loop (amplifier), if it has one")
    ap.add_argument("--out", default=str(HERE / "mt_results.jsonl"))
    ap.add_argument("--yes", action="store_true", help="actually dispatch")
    ap.add_argument("--summarize", metavar="FILE")
    args = ap.parse_args()
    if args.summarize:
        summarize(Path(args.summarize))
    else:
        run(args)


if __name__ == "__main__":
    main()
