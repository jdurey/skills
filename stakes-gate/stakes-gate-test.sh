#!/usr/bin/env bash
# stakes-gate-test.sh — hermetic regression suite for stakes-gate.sh. No model, no network:
# a deterministic stub judge (STAKES_GATE_CMD) emits whatever verdict line each case needs.
#
# The suite encodes the gate's contract, including the one bypass that was actually found when
# three rival model families attacked this design: an out-of-range confidence (1.7, 99) sailed
# past a digits-only check and through the preauth wall. These tests FAIL against that old code.
#
# Run:  bash stakes-gate-test.sh   (exit 0 = all green)
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GATE="$HERE/stakes-gate.sh"
TD="$(mktemp -d)"; trap 'rm -rf "$TD"' EXIT

# a minimal policy canon and a benign request
cat > "$TD/policy.md" <<'EOF'
# Decision policy canon (test fixture)
Recorded dimension: HOUSEKEEPING — approve routine internal cleanups.
<!-- STAKES-GATE-LEARN-APPEND -->
EOF
echo "Request: rotate the internal scratch logs." > "$TD/req.txt"

export STAKES_GATE_POLICY="$TD/policy.md"

fails=0
check() { # name expected_exit actual_exit expected_grep output
  local name="$1" want="$2" got="$3" pat="$4" out="$5"
  if [ "$got" = "$want" ] && printf '%s' "$out" | grep -qE "$pat"; then
    echo "  PASS $name"
  else
    echo "  FAIL $name — exit $got (want $want); output: $out"
    fails=$((fails+1))
  fi
}

run() { # verdict_line stakes extra_args...
  local line="$1" stakes="$2"; shift 2
  STAKES_GATE_CMD="printf '%s\n' \"$line\"; cat >/dev/null" \
    bash "$GATE" judge --request "$TD/req.txt" ${stakes:+--stakes "$stakes"} "$@" 2>&1
}

echo "1) happy path — internal+reversible, confident APPROVE auto-acts:"
OUT="$(run $'APPROVE\t0.9\tHOUSEKEEPING\troutine' internal-reversible)"; RC=$?
check "confident internal APPROVE -> exit 0" 0 "$RC" '\[GATE-APPROVE\]' "$OUT"

echo "2) the wall — outward stakes NEVER auto-fire, whatever the model says:"
OUT="$(run $'APPROVE\t0.99\tHOUSEKEEPING\tsure' outward)"; RC=$?
check "outward + conf 0.99 -> ASK (exit 3)" 3 "$RC" '\[GATE-ASK\].*wall' "$OUT"
OUT="$(run $'APPROVE\t0.99\tHOUSEKEEPING\tsure' '')"; RC=$?
check "omitted stakes -> treated as wall -> ASK" 3 "$RC" '\[GATE-ASK\]' "$OUT"

echo "3) THE FOUND BYPASS — out-of-range confidence must fail CLOSED (old code let it through):"
OUT="$(run $'APPROVE\t1.7\tHOUSEKEEPING\toverconfident' internal-reversible)"; RC=$?
check "conf=1.7 -> clamped to 0 -> ASK, not APPROVE" 3 "$RC" 'confidence 0 below' "$OUT"
OUT="$(run $'APPROVE\t99\tHOUSEKEEPING\toverconfident' internal-reversible)"; RC=$?
check "conf=99 -> clamped to 0 -> ASK" 3 "$RC" 'confidence 0 below' "$OUT"
OUT="$(run $'APPROVE\t99\tHOUSEKEEPING\toverconfident' outward --preauth some-class)"; RC=$?
check "conf=99 cannot open the PREAUTH wall either" 3 "$RC" '\[GATE-ASK\]' "$OUT"
OUT="$(run $'APPROVE\tbanana\tHOUSEKEEPING\tnonnumeric' internal-reversible)"; RC=$?
check "non-numeric conf -> fail closed -> ASK" 3 "$RC" 'confidence 0 below' "$OUT"

echo "4) threshold config is also fenced — an out-of-range floor is a usage error, not a bypass:"
OUT="$(run $'APPROVE\t0.9\tHOUSEKEEPING\tok' internal-reversible --conf-threshold -1)"; RC=$?
check "--conf-threshold -1 -> ERROR exit 4" 4 "$RC" 'must be a number in \[0,1\]' "$OUT"

echo "5) low confidence and novelty route to the human floor:"
OUT="$(run $'APPROVE\t0.3\tHOUSEKEEPING\tunsure' internal-reversible)"; RC=$?
check "conf 0.3 < tau -> ASK" 3 "$RC" 'below tau' "$OUT"
OUT="$(run $'APPROVE\t0.9\tNOVEL\tno precedent' internal-reversible)"; RC=$?
check "NOVEL dimension -> ASK" 3 "$RC" 'novel' "$OUT"
OUT="$(run $'APPROVE\t0.9\tnovel\tlowercase sentinel' internal-reversible)"; RC=$?
check "lowercase 'novel' also caught" 3 "$RC" 'novel' "$OUT"

echo "6) model failure modes -> ERROR (== human), never a silent pass:"
OUT="$(STAKES_GATE_CMD="cat >/dev/null; true" bash "$GATE" judge --request "$TD/req.txt" --stakes internal-reversible 2>&1)"; RC=$?
check "empty model output -> ERROR exit 4" 4 "$RC" '\[GATE-ERROR\]' "$OUT"
OUT="$(STAKES_GATE_CMD="cat >/dev/null; echo 'i cannot decide, sorry'" bash "$GATE" judge --request "$TD/req.txt" --stakes internal-reversible 2>&1)"; RC=$?
check "no verdict line -> ERROR exit 4" 4 "$RC" 'no parseable verdict' "$OUT"

echo "7) refusal fence — a fenced request is never modeled:"
echo "This touches confidential-client material." > "$TD/fenced.txt"
OUT="$(STAKES_GATE_REFUSE_REGEX='confidential-client' STAKES_GATE_CMD="echo SHOULD-NEVER-RUN" \
  bash "$GATE" judge --request "$TD/fenced.txt" --stakes internal-reversible 2>&1)"; RC=$?
check "fence match -> ASK without a model call" 3 "$RC" 'refusal fence' "$OUT"

echo "8) sidecar stays metadata-only and single-line even under a hostile reason field:"
OUT="$(run "APPROVE	0.9	HOUSEKEEPING	line1
line2	injected" internal-reversible)"; RC=$?
LINES="$(wc -l < "$TD/req.txt.gate.tsv" | tr -d ' ')"
if [ "$LINES" = "1" ]; then echo "  PASS sidecar is exactly one line"; else echo "  FAIL sidecar has $LINES lines"; fails=$((fails+1)); fi

echo "9) the learning flywheel appends above the marker:"
bash "$GATE" learn --dimension HOUSEKEEPING --said REJECT --did approve --rule "cleanups are fine" --date 2026-01-01 >/dev/null 2>&1
if grep -q 'cleanups are fine' "$TD/policy.md" && \
   [ "$(grep -n 'STAKES-GATE-LEARN-APPEND' "$TD/policy.md" | cut -d: -f1)" -gt "$(grep -n 'cleanups are fine' "$TD/policy.md" | cut -d: -f1)" ]; then
  echo "  PASS learn datum appended above the marker"
else
  echo "  FAIL learn append"; fails=$((fails+1))
fi

echo
if [ "$fails" -gt 0 ]; then echo "RESULT: $fails FAILED"; exit 1; fi
echo "RESULT: ALL GREEN"
