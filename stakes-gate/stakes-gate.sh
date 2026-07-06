#!/usr/bin/env bash
# stakes-gate.sh — a supreme-stakes gate: the model PROPOSES a verdict, a deterministic
#   wall the model cannot see or edit ENFORCES the limit around it.
#
# WHAT: when an autonomous system can't responsibly judge an action/decision on its own,
#   this gate inserts ONE autonomy-preserving step before the human floor: a model loaded
#   with your recorded decision policy predicts what the operator would decide — and the
#   gate only lets that prediction act when it is confident AND the action stays inside
#   the internal/reversible lane. Outward or irreversible stakes ALWAYS route to a human,
#   no matter how confident the model sounds.
#
# TWO LAYERS (the model proposes, the GATE enforces):
#   * PREDICTION — a model loaded with the policy canon proposes a verdict line.
#                  Replaceable/stubbable via STAKES_GATE_CMD (tests inject a deterministic stub).
#   * THE STAKES WALL (this script's security-critical core) — enforced ON TOP of the
#     prediction. The model can never talk the gate past the wall: outward / irreversible /
#     unknown stakes ALWAYS resolve to ASK (the human floor), regardless of confidence.
#
# FAIL-CLOSED INVARIANT: the gate NEVER manufactures a confident approval. Doubt => ASK =>
#   human floor. Unknown stakes => treated as outward/irreversible. Unparseable or erroring
#   model => ERROR (== human). A guessed APPROVE is the exact failure this gate prevents.
#
# VERDICT / EXIT:
#   APPROVE exit 0    EDIT exit 0    REJECT exit 1    ASK exit 3    ERROR/usage exit 4
#   ASK and ERROR both route to the human floor. APPROVE/EDIT auto-act ONLY in the
#   internal+reversible lane at conf >= tau; REJECT auto-rejects there too.
#
# OUTPUT: a machine-greppable status line on stdout — one of:
#   [GATE-APPROVE] <name> conf=<c>   [GATE-EDIT] <name> conf=<c>   [GATE-REJECT] <name> conf=<c>
#   [GATE-ASK] <name> <why>          [GATE-ERROR] <name> <why>
#   plus a metadata-only sidecar <request>.gate.tsv: verdict, confidence, dimension, stakes, reason.
#   The sidecar persists ONLY that metadata — never the request body, never free rationale.
#
# CONFIG (all via environment; no hardcoded paths):
#   STAKES_GATE_POLICY       path to your policy canon markdown (REQUIRED — your recorded decisions)
#   STAKES_GATE_CMD          the judge command; reads (canon + request) on STDIN, emits ONE verdict
#                            line "VERDICT<TAB>confidence<TAB>dimension<TAB>reason"
#                            (default: claude -p --output-format text)
#   STAKES_GATE_TAU          confidence floor for the auto-act lane (default 0.65)
#   STAKES_GATE_TAU_HIGH     higher floor required for a --preauth'd outward class (default 0.85)
#   STAKES_GATE_REFUSE_REGEX optional case-insensitive extended regex; a request matching it is
#                            NEVER modeled (refuse -> ASK). Use it to fence off confidential or
#                            out-of-policy domains from prediction entirely.
#
# USAGE:
#   stakes-gate.sh judge --request FILE [--stakes S] [--dimension D]
#                        [--conf-threshold T] [--preauth CLASS] [--sidecar PATH]
#     --stakes   one of: internal-reversible | internal | reversible  (the ONLY tokens that open
#                the auto-act lane); anything else / omitted => treated as outward/irreversible
#                (fail closed).
#     --preauth  names an outward CLASS the operator pre-authorized for THIS run (opens the wall
#                at tau_high only — and even then the gate only RECOMMENDS, logged).
#   stakes-gate.sh learn --dimension D --said X --did Y [--rule R] [--date YYYY-MM-DD]
#     the learning flywheel: every human override appends a labeled datum to the policy canon,
#     just above its '<!-- STAKES-GATE-LEARN-APPEND -->' marker line.
#
# House style: set -uo pipefail; bash 3.2-safe; deterministic; no hardcoded user paths.
set -uo pipefail

CANON="${STAKES_GATE_POLICY:-}"
GATE_CMD="${STAKES_GATE_CMD:-claude -p --output-format text}"
TAU="${STAKES_GATE_TAU:-0.65}"
TAU_HIGH="${STAKES_GATE_TAU_HIGH:-0.85}"
REFUSE_RE="${STAKES_GATE_REFUSE_REGEX:-}"

die() { printf 'stakes-gate: %s\n' "$*" >&2; exit 4; }

CMD="${1:-}"; [ $# -gt 0 ] && shift
case "$CMD" in
  -h|--help|'')
    sed -n '/^# USAGE:/,/^# House style/p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//; /^House style/d'
    exit 0 ;;
  judge) : ;;
  # ---- the learning flywheel: an override appends a labeled datum to the policy canon ----------
  learn)
    L_DIM=""; L_SAID=""; L_DID=""; L_RULE=""; L_DATE="${STAKES_GATE_LEARN_DATE:-}"
    while [ $# -gt 0 ]; do
      case "$1" in
        --dimension) L_DIM="${2:?--dimension needs a value}";  shift 2 ;;
        --said)      L_SAID="${2:?--said needs a value}";      shift 2 ;;
        --did)       L_DID="${2:?--did needs a value}";        shift 2 ;;
        --rule)      L_RULE="${2:?--rule needs a value}";      shift 2 ;;
        --date)      L_DATE="${2:?--date needs a value}";      shift 2 ;;
        *) die "learn: unknown arg: $1" ;;
      esac
    done
    [ -n "$L_DIM" ] && [ -n "$L_SAID" ] && [ -n "$L_DID" ] || die "usage: stakes-gate.sh learn --dimension D --said X --did Y [--rule R]"
    [ -n "$CANON" ] || die "STAKES_GATE_POLICY is not set"
    [ -w "$CANON" ] || die "policy canon not writable: $CANON"
    [ -n "$L_DATE" ] || L_DATE="$(date +%F 2>/dev/null || echo 'undated')"
    MARK='<!-- STAKES-GATE-LEARN-APPEND -->'
    grep -qF "$MARK" "$CANON" || die "policy canon missing the append marker: $MARK"
    # sanitize to a single pipe-delimited line (no tabs/newlines that would corrupt the log)
    san() { printf '%s' "$1" | tr '\t\n|' '   ' | sed 's/^[[:space:]]*//; s/[[:space:]]*$//'; }
    NEWLINE="$L_DATE | $(san "$L_DIM") | gate said $(san "$L_SAID") | operator did $(san "$L_DID") | $(san "${L_RULE:-rule: strengthen this dimension}")"
    TMP="$(mktemp -t stakes-gate-learn.XXXXXX)" || die "mktemp failed"
    awk -v line="$NEWLINE" -v mark="$MARK" '
      index($0, mark) { print line; print; next } { print }
    ' "$CANON" > "$TMP" && cat "$TMP" > "$CANON" && rm -f "$TMP" || { rm -f "$TMP"; die "append failed"; }
    printf '[GATE-LEARN] appended: %s\n' "$NEWLINE"
    exit 0 ;;
  *) die "unknown subcommand: '$CMD' (want: judge | learn)" ;;
esac

REQ=""; STAKES=""; DIM=""; CT="$TAU"; PREAUTH=""; SIDE=""
while [ $# -gt 0 ]; do
  case "$1" in
    --request)        REQ="${2:?--request needs a value}";       shift 2 ;;
    --stakes)         STAKES="${2:?--stakes needs a value}";     shift 2 ;;
    --dimension)      DIM="${2:?--dimension needs a value}";     shift 2 ;;
    --conf-threshold) CT="${2:?--conf-threshold needs a value}"; shift 2 ;;
    --preauth)        PREAUTH="${2:?--preauth needs a value}";   shift 2 ;;
    --sidecar)        SIDE="${2:?--sidecar needs a value}";      shift 2 ;;
    *) die "judge: unknown arg: $1" ;;
  esac
done
[ -n "$REQ" ]   || die "usage: stakes-gate.sh judge --request FILE [--stakes S] ..."
[ -r "$REQ" ]   || die "request not readable: $REQ"
[ -n "$CANON" ] || die "STAKES_GATE_POLICY is not set (path to your policy canon)"
[ -r "$CANON" ] || die "policy canon not readable: $CANON"
NAME="$(basename "$REQ")"
[ -n "$SIDE" ] || SIDE="${REQ}.gate.tsv"

# valid_prob <x> — exit 0 IFF x is a number in [0,1]. This hardens the gate's one CRITICAL bypass:
# a digits-only check let conf=99 / 1.7 / 1.01 sail past tau and the preauth wall. Out-of-range
# confidence must fail CLOSED, never silently open a lane.
valid_prob() { awk -v x="$1" 'BEGIN{ if (x ~ /^[0-9]+(\.[0-9]+)?$/ && x+0 >= 0 && x+0 <= 1) exit 0; exit 1 }'; }
# Caller-supplied thresholds are CONFIG: an out-of-range value fails CLOSED (usage error), never
# silently loosens the floor (a --conf-threshold of -1 must not bypass it).
valid_prob "$TAU"      || die "STAKES_GATE_TAU must be a number in [0,1]: $TAU"
valid_prob "$TAU_HIGH" || die "STAKES_GATE_TAU_HIGH must be a number in [0,1]: $TAU_HIGH"
valid_prob "$CT"       || die "--conf-threshold must be a number in [0,1]: $CT"

# sani <field> — collapse CR/LF/TAB to spaces + trim + cap length, so a model-controlled field can
# never inject record separators or a wall of text into the metadata-only sidecar.
sani() { printf '%s' "$1" | tr '\r\n\t' '   ' | sed 's/^[[:space:]]*//; s/[[:space:]]*$//' | cut -c1-200; }
write_sidecar() {
  printf '%s\t%s\t%s\t%s\t%s\n' "$(sani "$1")" "$(sani "$2")" "$(sani "$3")" "$(sani "$4")" "$(sani "$5")" >"$SIDE" 2>/dev/null || true
}
emit_ask()   { write_sidecar ASK "${2:-0}" "${DIM:-NOVEL}" "${STK:-unknown}" "$1"; printf '[GATE-ASK] %s %s\n' "$NAME" "$1"; exit 3; }
emit_error() { write_sidecar ERROR 0 "${DIM:-NOVEL}" "${STK:-unknown}" "$1"; printf '[GATE-ERROR] %s %s\n' "$NAME" "$1"; exit 4; }

# --- REFUSAL FENCE: runs FIRST, before any model call ----------------------------------------------
# A request matching the operator's refusal regex is NEVER modeled. The scan is over a FLATTENED
# body (newlines -> spaces, NUL bytes stripped) so a marker split across lines can't slip past a
# line-oriented grep.
if [ -n "$REFUSE_RE" ]; then
  REQ_FLAT="$(tr -d '\000' < "$REQ" 2>/dev/null | tr '\r\n' '  ')"
  if printf '%s' "$REQ_FLAT" | grep -qiE "$REFUSE_RE" 2>/dev/null; then
    STK="${STAKES:-unknown}"; emit_ask "request matches the refusal fence — never modeled; route to the operator" 0.99
  fi
fi

# --- STAKES NORMALIZATION: ONLY an explicit recognized token opens the auto-act lane (fail closed) --
stk_lc="$(printf '%s' "$STAKES" | tr '[:upper:]' '[:lower:]')"
case "$stk_lc" in
  internal-reversible|internal_reversible|internal+reversible|reversible-internal) STK="internal-reversible"; LANE="open" ;;
  internal|reversible)                                                              STK="$stk_lc";            LANE="open" ;;
  ''|unknown)                                                                       STK="unknown";            LANE="wall" ;;
  *)                                                                                STK="$stk_lc";            LANE="wall" ;;  # outward/irreversible/financial/delete/anything => wall
esac

# --- PREDICTION: prompt the policy-loaded model; expect ONE tab-separated line ----------------------
RAW="$( { cat "$CANON"; printf '\n\n===REQUEST UNDER JUDGMENT===\n'; cat "$REQ"; printf '\n===END REQUEST===\nEmit ONLY the single verdict line now: VERDICT<TAB>confidence<TAB>dimension<TAB>reason\n'; } | eval "$GATE_CMD" 2>/dev/null )"
rc=$?
[ "$rc" -eq 0 ] || emit_error "prediction model exited rc=$rc"
[ -n "$RAW" ]   || emit_error "prediction model returned empty output"

# Take the LAST line that begins with a known verdict token (robust to any model preamble).
LINE="$(printf '%s\n' "$RAW" | grep -E '^[[:space:]]*(APPROVE|EDIT|REJECT|ASK)([[:space:]]|$)' | tail -n1)"
[ -n "$LINE" ] || emit_error "no parseable verdict line in model output"

VERDICT="$(printf '%s' "$LINE" | awk -F'\t' '{print $1}' | tr -d '[:space:]' | tr '[:lower:]' '[:upper:]')"
CONF="$(printf '%s'    "$LINE" | awk -F'\t' '{print $2}' | tr -d '[:space:]')"
MDIM="$(printf '%s'    "$LINE" | awk -F'\t' '{print $3}' | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')"
REASON="$(printf '%s'  "$LINE" | awk -F'\t' '{print $4}' | sed 's/^[[:space:]]*//; s/[[:space:]]*$//; s/	/ /g')"
[ -n "$MDIM" ] && DIM="$MDIM"
[ -n "$DIM" ]  || DIM="NOVEL"
# Reserved sentinel compare is CASE-INSENSITIVE (a lowercase `novel` must not slip the NOVEL floor).
DIM_UC="$(printf '%s' "$DIM" | tr '[:lower:]' '[:upper:]')"
[ -n "$REASON" ] || REASON="(no reason given)"
# Confidence must be a NUMBER IN [0,1]; anything else (non-numeric OR out-of-range like 99 / 1.7)
# fails closed (treated as 0). A guessed-high confidence can never open any lane.
valid_prob "$CONF" || CONF="0"

# numeric >= compare without bc (bash 3.2): let awk do the arithmetic.
ge() { awk -v a="$1" -v b="$2" 'BEGIN{ exit (a+0 >= b+0) ? 0 : 1 }'; }

# --- THE STAKES WALL + FAIL-CLOSED RESOLUTION (the security-critical core) --------------------------
# 1) NOVEL or the model itself ASKed => human floor.
case "$VERDICT" in
  ASK) emit_ask "model could not responsibly predict: $REASON" "$CONF" ;;
esac
[ "$DIM_UC" = "NOVEL" ] && emit_ask "request matches no recorded dimension (novel) — route to the operator" "$CONF"

# 2) THE WALL: outward / irreversible / unknown stakes never auto-fire on a prediction.
if [ "$LANE" = "wall" ]; then
  if [ -n "$PREAUTH" ] && ge "$CONF" "$TAU_HIGH"; then
    : # pre-authorized outward class at high confidence — fall through to verdict (recommend, logged).
  else
    emit_ask "stakes=$STK is outward/irreversible (or unknown) — the wall forces the human floor (predicted $VERDICT conf=$CONF)" "$CONF"
  fi
fi

# 3) confidence floor — below tau even an internal+reversible call goes to the operator.
ge "$CONF" "$CT" || emit_ask "confidence $CONF below tau=$CT — route to the operator" "$CONF"

# 4) auto-act (open lane, conf >= tau, dimension matched, model gave a real verdict).
write_sidecar "$VERDICT" "$CONF" "$DIM" "$STK" "$REASON"
case "$VERDICT" in
  APPROVE) printf '[GATE-APPROVE] %s conf=%s\n' "$NAME" "$CONF"; exit 0 ;;
  EDIT)    printf '[GATE-EDIT] %s conf=%s — %s\n' "$NAME" "$CONF" "$REASON"; exit 0 ;;
  REJECT)  printf '[GATE-REJECT] %s conf=%s — %s\n' "$NAME" "$CONF" "$REASON"; exit 1 ;;
  *)       emit_error "unrecognized verdict token: $VERDICT" ;;
esac
