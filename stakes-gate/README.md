# stakes-gate

I built a gate that lets my AI make a judgment call but stops short of giving it the final say.

The model reads an escalated situation, scores it against my recorded decision policy, and proposes a verdict. A separate script then checks that proposal against hard limits the model is structurally forbidden from crossing. When the stakes are outward-facing or irreversible, the answer is ASK — route to a human — and no amount of confident reasoning from the model can move it.

Then I handed the design to three other AI models from different labs and asked each of them to break it. One did: my gate trusted a confidence score that was supposed to fall between zero and one, and I had never checked that it actually did. A model reporting a confidence of 1.7 could have walked straight through the wall. The fix is in this version, and `stakes-gate-test.sh` carries a regression test that fails against the old code, so the same bypass can't slip back in unnoticed.

## What's here

- `stakes-gate.sh` — the gate. Model proposes, deterministic wall enforces. Fail-closed everywhere: unknown stakes are treated as irreversible, out-of-range confidence collapses to zero, novel situations and broken judges route to a human.
- `stakes-gate-test.sh` — hermetic regression suite (stub judge, no model, no network). Includes the found bypass.
- `policy-example.md` — the shape of the decision canon the judge reads, with the append marker the learning flywheel writes above.
- `SKILL.md` — the skill instructions, for agents that load markdown skills.

## Quick start

```sh
export STAKES_GATE_POLICY=policy-example.md
echo "Request: prune the scratch logs older than 30 days." > req.txt
bash stakes-gate.sh judge --request req.txt --stakes internal-reversible
```

Run the suite first: `bash stakes-gate-test.sh`. A guard you've never watched fail hasn't earned its green light.

MIT, like everything in this repo.
