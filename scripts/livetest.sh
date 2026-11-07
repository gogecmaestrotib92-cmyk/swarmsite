#!/usr/bin/env bash
# livetest.sh — the step before you land code. Renders the sample direction through every blueprint,
# grades each render against the contract at 1440 and 390, and fails loudly. Usage: scripts/livetest.sh [min-score]
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
MIN="${1:-75}"; TMP="$(mktemp -d)"; FAIL=0; export LIVETEST=1
BPS="butter cerebrium tengile lpas crav atelier"; [ "${2:-}" = "--all" ] && BPS="$(ls lib/blueprints/*.bp.json | xargs -n1 basename | sed 's/.bp.json//' | tr '\n' ' ')"
mkdir -p "$TMP/site"; cp tests/direction.sample.json "$TMP/site/direction.json"; cp tests/images.sample.json "$TMP/site/images.json"; cp tests/assets.sample.json "$TMP/site/assets.json" 2>/dev/null || true
echo "livetest → $TMP"
one() { bp="$1"; mkdir -p "$TMP/$bp"
  if ! python3 lib/render/render_bp.py "$TMP/site" "$bp" "$TMP/$bp/page.html" >/dev/null 2>"$TMP/$bp/err"; then echo "✗ $bp: render failed — $(tail -c 300 "$TMP/$bp/err")" > "$TMP/$bp/result"; return; fi
  out="$(node lib/qa/contract.mjs "$TMP/$bp/page.html" --dir "$TMP/$bp" 2>"$TMP/$bp/cerr" | tail -1)"
  score="$(echo "$out" | python3 -c 'import sys,json; print(json.load(sys.stdin)["score"])' 2>/dev/null || echo -1)"
  if [ "$score" -lt "$MIN" ]; then echo "✗ $bp: contract $score < $MIN — $(echo "$out" | python3 -c 'import sys,json; print("; ".join(json.load(sys.stdin)["failed"][:4]))' 2>/dev/null)" > "$TMP/$bp/result"; else echo "✓ $bp: contract $score" > "$TMP/$bp/result"; fi; }
for bp in $BPS; do one "$bp" & done; wait
for bp in $BPS; do r="$(cat "$TMP/$bp/result" 2>/dev/null || echo "✗ $bp: no result")"; echo "$r"; case "$r" in ✗*) FAIL=1;; esac; done
python3 -c "import ast,glob; [ast.parse(open(f).read()) for f in glob.glob('lib/**/*.py', recursive=True)]" && echo "✓ python syntax" || { echo "✗ python syntax"; FAIL=1; }
node --check server/index.mjs && node --check lib/pipeline/capture.mjs && echo "✓ node syntax" || { echo "✗ node syntax"; FAIL=1; }
[ "$FAIL" = 0 ] && echo "LIVE TEST PASSED" || { echo "LIVE TEST FAILED"; exit 1; }
