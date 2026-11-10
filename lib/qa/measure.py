"""measure.py — what a browser measures on the page that is about to ship, and what the Standard says of it.

  python3 lib/qa/measure.py <page.html> [<out dir>]      → <out dir>/measure.json and findings.json; prints a summary
  measure(page_html, out_dir, seconds=110)                → {'readings', 'findings', 'technical'} or None

The readings are taken by lib/qa/inspect.mjs in its quick form (both viewports, the load, a stepped scroll, reduce-motion;
about 45 seconds, no screenshots) — the only QA tool of the engine that looks at a page while it moves. lib/qa/standard.py
turns them into findings. Nothing here calls a model, edits a page or decides what ships: it reports. A page that cannot
be measured (no browser, out of time) yields None and the job goes on."""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import standard as STANDARD


def measure(page_html, out_dir, seconds=110):
    evidence = os.path.join(out_dir, 'measure.json')
    try:
        if os.path.exists(evidence): os.remove(evidence)
        done = subprocess.run(['node', os.path.join(HERE, 'inspect.mjs'), 'page', 'file://' + os.path.abspath(page_html), '--quick', '--evidence', evidence],
                              capture_output=True, text=True, timeout=seconds, cwd=os.path.dirname(os.path.dirname(HERE)))
        if done.returncode != 0 or not os.path.exists(evidence): return None
        with open(evidence, encoding='utf-8') as f: read = json.load(f)
    except (OSError, ValueError, subprocess.SubprocessError): return None
    report = {'readings': STANDARD.readings(read), 'findings': STANDARD.findings(read), 'technical': STANDARD.technical(read)}
    try:
        with open(os.path.join(out_dir, 'findings.json'), 'w', encoding='utf-8') as f: json.dump(report, f, indent=1, ensure_ascii=False)
    except OSError: pass
    return report


if __name__ == '__main__':
    if len(sys.argv) < 2: raise SystemExit(__doc__)
    page = sys.argv[1]; out = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(page))
    report = measure(page, out)
    if not report: raise SystemExit('the page could not be measured')
    print(json.dumps({'findings': [f"{f['id']}@{f['view']}" for f in report['findings']], 'technical': {c['id']: c['pass'] for c in report['technical']}}, ensure_ascii=False))
