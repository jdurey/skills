#!/usr/bin/env bash
# lint-premise-gate.sh — the Premise Gate: input-truth validation as a fourth gate class.
#
# WHAT: flags load-bearing STAKEHOLDER-ATTRIBUTION claims ("X asked for / wants / needs / requested Y")
#   that carry NO provenance tag, in plan / DoD / overnight artifacts. SOFT gate: a hit means "verify
#   this premise before acting / tag it", not a hard refusal. Same
#   wrap-tolerant spirit as a definition-of-done checker (a claim split across soft-wrapped lines still matches).
#
# WHY: my automation ran three gates — Firewall (May I?), Outcome (Should I?), Witness (Did it land?) — and
#   NONE asked "Is it TRUE?". An autonomous overnight run laundered an INFERENCE ("M is probably
#   missing X") into a stated fact ("M asked for X"); it passed all three gates, the DoD scored 8/8,
#   and a human acted on a request that never existed 
#   A note-to-self recorded the lesson and it
#   STILL happened — only a MECHANISM that fires (this lint) closes the gap, not knowledge.
#
# PROVENANCE TAGS (a load-bearing premise carries exactly one):
#   [VERIFIED: <src>]   — an externally-checkable source (linked message / doc / ticket / observed event)
#   [INFERRED]          — a reasoned guess, explicitly not confirmed
#   [ASSUMED → verify]  — taken as true pending a NAMED check
# Highest-risk class, gated hardest: stakeholder-attribution (verbs asked/requested/wants/needs/told/
#   expects). These MUST be [VERIFIED: src] or be auto-downgraded to [INFERRED].
#
# DESIGN (precision lever = the SUBJECT must be a person/role): "the build requires X" must NOT flag;
#   "Bill requires X" MUST. Three claim shapes are detected; a unit (paragraph / bullet / table row,
#   wrap-folded) is CLEARED if it carries a provenance tag or an explicit non-fact framing.
#   Recall-biased on purpose: it is a SOFT gate, so a false positive costs a "review this" prompt while
#   a false negative launders a fabricated premise — the expensive error.
#
# USAGE:
#   lint-premise-gate.sh <file...>     scan files; print untagged attribution claims; exit 1 if any
#   lint-premise-gate.sh --selftest    regression: the §2 specimen MUST flag; a tagged/clean control MUST pass
#   lint-premise-gate.sh -q <file...>  exit code only (no per-hit output)
#   (--canary is an alias for --selftest, for harnesses that plant known-bad drift)
#
# EXIT: 0 = clean / selftest PASS · 1 = untagged premise(s) found / selftest FAIL · 2 = usage error
# House style: set -uo pipefail; deterministic; no hardcoded user paths; reads but never emits zone content.
set -uo pipefail

# ---- pattern library -------------------------------------------------------------------------------
# SUBJ: a person/role. Case-SENSITIVE capitalized token (a name like "Bill"/"M") OR a lowercase role-noun.
SUBJ="([A-Z][A-Za-z.'-]*|[Mm]anager|[Cc]lient|[Ss]takeholder|[Bb]oss|[Dd]irector|[Cc]ustomer|[Tt]he team|[Tt]he lead)"
# VERB: request / desire verbs (common inflections).
VERB="(ask|asks|asked|request|requests|requested|want|wants|wanted|need|needs|needed|tell|tells|told|expect|expects|expected|demand|demands|demanded|require|requires|required|wish|wishes|wished|would[[:space:]]+like)"
P1="\\b${SUBJ}[[:space:]]+${VERB}\\b"                                  # <Subject> <verb>
P2='\b(asked|requested|told)[[:space:]]+(me|us|him|her|them|the team)[[:space:]]+to\b'  # <verb> me/us... to
P3="\\b[Pp]er[[:space:]]+[A-Z][A-Za-z.'-]*('s)?[[:space:]]+(request|ask|instruction|require)"  # per <Name>('s) request
# Non-stakeholder leading words that look like a capitalized subject but are not a person/role (drop these
# P1 hits). Matched case-INSENSITIVELY so all-caps connectives ("BUT needs") are caught too. Covers: sentence
# connectives, articles/quantifiers + common adjective ("The need", "Real need" — noun "need", not the verb),
# contractions/imperatives ("Don't ask"), and bare pronouns ("He needs" — too vague to source; a real
# "He told me to" is still caught by P2). Possessives like "X's ask" stay flagged (they ARE attribution).
STOP="^(Then|This|That|It|We|I|They|There|Here|These|Those|Also|And|But|So|Now|When|If|After|Before|Once|Each|Every|No|Not|To|Either|Neither|Whether|Which|Who|What|Why|How|The|A|An|Our|Your|My|His|Her|Its|Their|Real|Some|Any|Most|More|He|She|Him|Don.t|Won.t|Can.t|Doesn.t|Didn.t|Couldn.t|Wouldn.t|Only|Just|Even|Still|Again|Really|Simply|Maybe|Perhaps|Always|Often)[[:space:]]"
# A premise is CLEARED if it carries a provenance tag ...
TAG='\[(VERIFIED:[^]]*|INFERRED|ASSUMED[^]]*)\]'
# ... or is explicitly framed as not-a-fact in prose.
CLEAR='(unsolicited|hypothes|not[[:space:]]+confirmed|unconfirmed|no[[:space:]]+source|specul|my[[:space:]]+(read|guess|inference)|to[[:space:]]+be[[:space:]]+confirmed|tbd|pending[[:space:]]+confirm)'

TOTAL=0; QUIET=0

# segment a file into units (paragraph / bullet / numbered / heading / table-row), wrap-folding
# soft-wrapped continuation lines, collapsing internal whitespace, carrying the start line number.
# Output: "<lineno>\t<flattened-unit>" per unit (buf is tab-free after the gsub, so TAB is a safe sep).
segment() {
  awk '
    function flush(){ if(buf!=""){ gsub(/[ \t]+/," ",buf); sub(/^ /,"",buf); printf "%d\t%s\n", start, buf; buf="" } }
    /^[[:space:]]*$/ { flush(); next }
    /^[[:space:]]*([-*+>]|[0-9]+\.|#|\|)/ { flush(); start=NR; buf=$0; next }
    { if(buf==""){ start=NR }; buf=(buf==""?$0:buf" "$0) }
    END{ flush() }
  ' "$1"
}

scan_file() {
  local f="$1"
  if [ ! -r "$f" ]; then echo "  ⚠️  unreadable (skipped): $f" >&2; return 0; fi
  local ln unit c1 c2 c3 cands phrase excerpt
  while IFS=$'\t' read -r ln unit; do
    [ -n "${unit:-}" ] || continue
    case "$unit" in \#*) continue ;; esac                       # skip pure headings (labels, not claims)
    c1="$(printf '%s\n' "$unit" | grep -oE "$P1" 2>/dev/null | grep -vEi "$STOP" 2>/dev/null || true)"
    c2="$(printf '%s\n' "$unit" | grep -oiE "$P2" 2>/dev/null || true)"
    c3="$(printf '%s\n' "$unit" | grep -oE  "$P3" 2>/dev/null || true)"
    cands="$(printf '%s\n%s\n%s\n' "$c1" "$c2" "$c3" | grep -v '^[[:space:]]*$' || true)"
    [ -n "$cands" ] || continue
    printf '%s\n' "$unit" | grep -qE  "$TAG"   2>/dev/null && continue   # has a provenance tag → cleared
    printf '%s\n' "$unit" | grep -qiE "$CLEAR" 2>/dev/null && continue   # explicit non-fact framing → cleared
    TOTAL=$((TOTAL+1))
    if [ "$QUIET" -eq 0 ]; then
      phrase="$(printf '%s\n' "$cands" | head -1 | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
      excerpt="$unit"; [ "${#excerpt}" -gt 130 ] && excerpt="${excerpt:0:130}…"
      echo "  ❌ $f:$ln — untagged stakeholder-attribution: \"$phrase\""
      echo "       ↳ $excerpt"
    fi
  done < <(segment "$f")
}

# ---- selftest (hermetic; the frozen failure specimen MUST flag, the clean controls MUST pass) ------
selftest() {
  local td dirty clean rc=0
  td="$(mktemp -d)"; trap 'rm -rf "$td"' RETURN
  dirty="$td/specimen-dirty.md"; clean="$td/specimen-clean.md"

  # DIRTY — the frozen failure specimen (the laundered "M asked for X" premise) + variants. All MUST flag.
  cat > "$dirty" <<'EOF'
# Tomorrow's plan (overnight build)
1. **M asked for the onboarding rubric** — top priority, ready to execute by 9am.
2. Per Bill's request, ship the Q3 dashboard Friday.
3. The manager wants a weekly mastery report.
4. She told me to prioritize the migration.
EOF

  # CLEAN — same claims, correctly tagged OR genuinely non-attribution. NONE may be flagged.
  cat > "$clean" <<'EOF'
# Tomorrow's plan (correctly gated)
1. **Draft the onboarding rubric** — [INFERRED] M would likely benefit; not confirmed with M.
2. Per Bill's request [VERIFIED: gmail thread 2026-06-20 "Q3 dashboard"], ship the dashboard Friday.
3. The build requires Node 20.
4. This needs a retry guard before it ships.
5. We asked ourselves whether to ship now or harden first.
EOF

  TOTAL=0; QUIET=1; scan_file "$dirty"; local d=$TOTAL
  TOTAL=0; QUIET=1; scan_file "$clean"; local c=$TOTAL
  # also confirm the canonical specimen line ("M asked") is specifically caught, not just some line
  local m; m="$(QUIET=0; TOTAL=0; scan_file "$dirty" 2>/dev/null | grep -c 'M asked' || true)"

  echo "selftest: DIRTY flagged $d/4 (want 4) · CLEAN flagged $c/5 (want 0) · specimen 'M asked' caught: $([ "$m" -ge 1 ] && echo yes || echo NO)"
  [ "$d" -eq 4 ] || { echo "  FAIL: dirty specimen under-flagged ($d/4) — a fabricated premise would slip"; rc=1; }
  [ "$c" -eq 0 ] || { echo "  FAIL: clean control over-flagged ($c/5) — tagged/non-attribution text false-positived"; rc=1; }
  [ "$m" -ge 1 ] || { echo "  FAIL: the specimen line 'M asked for ...' was NOT caught"; rc=1; }
  [ "$rc" -eq 0 ] && echo "SELFTEST PASS" || echo "SELFTEST FAIL"
  return "$rc"
}

# ---- driver ----------------------------------------------------------------------------------------
case "${1:-}" in
  --selftest|--canary) selftest; exit $? ;;
  -q|--quiet) QUIET=1; shift ;;
  "" ) echo "usage: lint-premise-gate.sh [--selftest|-q] <file...>" >&2; exit 2 ;;
esac
[ "$#" -ge 1 ] || { echo "usage: lint-premise-gate.sh [--selftest|-q] <file...>" >&2; exit 2; }

for f in "$@"; do scan_file "$f"; done
if [ "$TOTAL" -gt 0 ]; then
  echo "PREMISE-GATE: $TOTAL untagged stakeholder-attribution premise(s) — tag each [VERIFIED: src] or [INFERRED] before the plan/DoD is trusted."
  exit 1
fi
echo "PREMISE-GATE: clean — no untagged stakeholder-attribution premises in $# file(s)."
exit 0
