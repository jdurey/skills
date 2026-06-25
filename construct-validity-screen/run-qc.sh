#!/usr/bin/env bash
# Run the screen on a batch and write the review report.
#   ./run-qc.sh items.json "Batch label"
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
BATCH="${1:?usage: ./run-qc.sh items.json \"label\"}"
LABEL="${2:-item batch}"
OUT="$HERE/review-$(basename "$BATCH" .json).md"
python3 "$HERE/report_qc.py" --items "$BATCH" --out "$OUT" --label "$LABEL"
echo "open: $OUT"
