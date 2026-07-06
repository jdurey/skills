# Decision policy canon — example

This file is what the gate's judge model reads before every prediction. Each dimension is one
class of decision with the operator's recorded rulings. Keep entries short, dated, and honest —
the gate is only as good as the canon underneath it.

## Dimensions

### HOUSEKEEPING
Routine internal cleanups (log rotation, cache pruning, renaming scratch files).
Recorded rulings: approve when scoped to scratch/temporary artifacts; reject anything touching
records another process reads.

### RETRY
Re-running a failed internal job with unchanged inputs.
Recorded rulings: approve up to two retries; a third failure escalates.

## Verdict format the judge must emit

One line, tab-separated: `VERDICT<TAB>confidence<TAB>dimension<TAB>reason`
- VERDICT: APPROVE | EDIT | REJECT | ASK
- confidence: a number in [0,1]
- dimension: one of the headings above, or NOVEL when nothing matches

## Learned overrides

Appended automatically by `stakes-gate.sh learn` — newest just above the marker.

<!-- STAKES-GATE-LEARN-APPEND -->
