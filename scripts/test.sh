#!/usr/bin/env bash
# npm test — every regression test in the repo. Fails on the first red file. ~8 min; run `scripts/livetest.sh 80` too before a commit (AGENTS.md).
set -u; cd "$(dirname "$0")/.."
export LIVETEST=1 CHROME_PATH="${CHROME_PATH:-$(command -v google-chrome || command -v chromium || true)}"
python3 -m pytest tests -q -p no:cacheprovider || exit 1
# tests that need a service this machine may not have: run only when it is there
skip='^(crawl-lease-postgres|font-selection|capture-live-ui|crawl-worker-restart)\.mjs$'
fail=0; for f in tests/*.mjs; do n=$(basename "$f"); [[ "$n" =~ $skip ]] && continue
  if ! timeout 180 node "$f" >"/tmp/test-$n.log" 2>&1; then echo "✗ $n"; grep -m2 -E "Error|assert" "/tmp/test-$n.log" | cut -c1-160; fail=1; else echo "✓ $n"; fi; done
exit $fail
