#!/usr/bin/env python3
"""
run_probe.py — measure actor->supervisor role-bleed across agent CLIs.

For each (model x condition x replicate) it dispatches a self-contained task to
the model's CLI, captures the reasoning stream, and scores it with the frozen
markers in markers.json (via score.py). Paired conditions isolate one variable
at a time (phrasing, horizon, tool-ambiguity, loop-pressure); compare the two
rows of each pair.

SAFETY: by default this is a DRY RUN — it renders prompts and prints the plan
without calling any model. Pass --yes to actually dispatch (this spends tokens
and runs real agents in a throwaway temp dir).

Usage:
    python3 run_probe.py                       # dry run: show the plan + cost
    python3 run_probe.py --yes --models grok --n 5
    python3 run_probe.py --yes --models grok,codex --n 8 --turns 10 --out results.jsonl
    python3 run_probe.py --summarize results.jsonl   # re-aggregate an existing run
"""
import argparse
import json
import os
import shutil
import statistics
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


def flatten_conditions(conditions):
    """Yield (pair_id, condition_label, prompt_template)."""
    for pair in conditions["pairs"]:
        for label, prompt in pair["conditions"].items():
            yield pair["id"], label, prompt


def fixtures_for(conditions):
    """Map pair_id -> fixtures subdir (relative to probe/), if declared."""
    return {p["id"]: p["fixtures"] for p in conditions["pairs"] if p.get("fixtures")}


def seed_fixtures(workdir, fixtures_rel):
    """Copy fixture files into the throwaway workdir before dispatch."""
    src = HERE / fixtures_rel
    n = 0
    for f in sorted(src.glob("*")):
        if f.is_file():
            shutil.copy(f, Path(workdir) / f.name)
            n += 1
    return n


def render(prompt, workdir):
    return prompt.replace("{WORKDIR}", workdir)


def build_cmd(template, prompt, workdir, turns):
    out = []
    for tok in template:
        tok = (tok.replace("{PROMPT}", prompt)
                  .replace("{WORKDIR}", workdir)
                  .replace("{TURNS}", str(turns))
                  .replace("{HOME}", os.path.expanduser("~")))
        out.append(tok)
    return out


def dispatch(cmd, reasoning_stream, timeout, cwd=None):
    t0 = time.time()
    try:
        # stdin=DEVNULL: several CLIs hang waiting on stdin otherwise (see dispatch.sh).
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                           cwd=cwd, stdin=subprocess.DEVNULL)
        out, err, rc = p.stdout, p.stderr, p.returncode
    except subprocess.TimeoutExpired as e:
        out, err, rc = (e.stdout or ""), (e.stderr or ""), 124
    except FileNotFoundError:
        return None  # binary not present
    elapsed = round(time.time() - t0, 1)
    if reasoning_stream == "stderr":
        text = err
    elif reasoning_stream == "stdout":
        text = out
    else:
        text = (err or "") + "\n" + (out or "")
    return {"text": text, "rc": rc, "elapsed": elapsed,
            "stdout_len": len(out or ""), "stderr_len": len(err or "")}


def run(args):
    conditions = load_json("conditions.json")
    adapters = load_json("adapters.json")["adapters"]
    markers = load_markers()
    models = [m.strip() for m in args.models.split(",") if m.strip()]

    plan = list(flatten_conditions(conditions))
    fixtures_map = fixtures_for(conditions)
    if args.only:
        wanted = [s.strip() for s in args.only.split(",") if s.strip()]
        plan = [p for p in plan if any(w in p[0] for w in wanted)]
        if not plan:
            print(f"  !! --only={args.only} matched no pairs; aborting")
            return
    total = len(models) * len(plan) * args.n
    print(f"models={models}  conditions={len(plan)}  replicates={args.n}  "
          f"=> {total} agent runs")
    for m in models:
        a = adapters.get(m)
        if not a:
            print(f"  !! no adapter for '{m}'")
        elif not a.get("enabled"):
            print(f"  ~~ adapter '{m}' is disabled in adapters.json "
                  f"(enable + verify flags before use)")

    if not args.yes:
        print("\nDRY RUN. Re-run with --yes to dispatch. Example prompts:")
        for pid, label, prompt in plan[:2]:
            print(f"\n[{pid}/{label}]\n{render(prompt, '<WORKDIR>')}")
        return

    out_path = Path(args.out)
    n_done = 0
    with out_path.open("w") as fh:
        for model in models:
            a = adapters.get(model)
            if not a or not a.get("enabled"):
                continue
            for pid, label, prompt_tpl in plan:
                for rep in range(args.n):
                    workdir = tempfile.mkdtemp(prefix=f"probe_{model}_")
                    prompt = render(prompt_tpl, workdir)
                    cmd = build_cmd(a["cmd"], prompt, workdir, args.turns)
                    cwd = workdir if a.get("cwd") else None
                    res = dispatch(cmd, a.get("reasoning", "both"), args.timeout, cwd=cwd)
                    if res is None:
                        print(f"  !! {model}: binary not found ({cmd[0]}) — skipping")
                        shutil.rmtree(workdir, ignore_errors=True)
                        break
                    sc = score(res["text"], markers)
                    rec = {"model": model, "pair": pid, "condition": label,
                           "rep": rep, "leaked": sc["leaked"],
                           "n_markers": sc["n_markers"], "fired": sc["fired"],
                           "rc": res["rc"], "elapsed": res["elapsed"],
                           "reasoning_chars": len(res["text"])}
                    if args.save_traces:
                        tdir = out_path.parent / "traces"
                        tdir.mkdir(exist_ok=True)
                        tf = tdir / f"{model}_{pid}_{label}_{rep}.txt"
                        tf.write_text(res["text"])
                        rec["trace_file"] = str(tf.name)
                    fh.write(json.dumps(rec) + "\n")
                    fh.flush()
                    n_done += 1
                    print(f"  [{n_done}/{total}] {model} {pid}/{label} #{rep} "
                          f"leaked={sc['leaked']} markers={sc['fired']}")
                    shutil.rmtree(workdir, ignore_errors=True)
    print(f"\nwrote {n_done} records to {out_path}")
    summarize(out_path)


def summarize(path):
    rows = [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]
    if not rows:
        print("no records")
        return
    agg = defaultdict(list)
    for r in rows:
        agg[(r["model"], r["pair"], r["condition"])].append(r)
    print("\n=== leak rate by model x condition ===")
    print(f"{'model':10} {'pair':22} {'cond':10} {'n':>3} "
          f"{'leak%':>6} {'mean#':>6}")
    for key in sorted(agg):
        rs = agg[key]
        leak = 100 * sum(r["leaked"] for r in rs) / len(rs)
        meanm = statistics.mean(r["n_markers"] for r in rs)
        print(f"{key[0]:10} {key[1]:22} {key[2]:10} {len(rs):>3} "
              f"{leak:>5.0f}% {meanm:>6.2f}")
    # within-pair deltas (the controlled comparison)
    print("\n=== within-pair delta (treatment leak% - control leak%) ===")
    pairs = defaultdict(dict)
    for (model, pid, cond), rs in agg.items():
        leak = 100 * sum(r["leaked"] for r in rs) / len(rs)
        pairs[(model, pid)][cond] = leak
    order = {"T1_rubric_framing": ("rubric", "plain"),
             "T2_horizon_length": ("long", "short"),
             "T3_tool_ambiguity": ("silent", "confirmed"),
             "T4_loop_pressure": ("unbounded", "bounded"),
             "T5_sustained_load": ("heavy_loop", "heavy_plain")}
    for (model, pid), conds in sorted(pairs.items()):
        hi, lo = order.get(pid, (None, None))
        if hi in conds and lo in conds:
            print(f"  {model:10} {pid:22} {hi}-{lo}: "
                  f"{conds[hi]-conds[lo]:+.0f} pts")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="grok")
    ap.add_argument("--n", type=int, default=5, help="replicates per condition")
    ap.add_argument("--turns", type=int, default=10, help="max agent turns")
    ap.add_argument("--timeout", type=int, default=240)
    ap.add_argument("--out", default=str(HERE / "results.jsonl"))
    ap.add_argument("--yes", action="store_true", help="actually dispatch")
    ap.add_argument("--only", help="comma-sep pair-id substrings to include (e.g. T5)")
    ap.add_argument("--save-traces", action="store_true",
                    help="persist each run's raw reasoning text to traces/ for inspection")
    ap.add_argument("--summarize", metavar="FILE", help="re-aggregate an existing jsonl")
    args = ap.parse_args()
    if args.summarize:
        summarize(Path(args.summarize))
    else:
        run(args)


if __name__ == "__main__":
    main()
