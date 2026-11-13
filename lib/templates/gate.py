"""gate.py — the gates as a library call: is a rendered variant fit to be shown?

    check(files, settle=None, pause=None, crops=None) -> [result]    one per file, in order
    shown(variants) -> the variants whose gate passed                 (a failing variant is not shown)
    render_and_check(d, slugs, outdir, media_base='', root=None) -> [{'slug', 'file', 'ok', 'failed', 'gate'}]

The checks themselves are lib/qa/template_gate.mjs (one browser; every page at 1440 and 390, and at 1920, 1024 and 768
for all but the photographed legibility pass): sideways scroll, script errors, distorted media, exactly one h1, every
text line readable on what is behind it, no line of text over another, no line the screen's edge cuts, and the
client's headline readable on the first screen at load, without scrolling; and no screen with a large empty region.
A result is the JSON that tool prints: {page, ok, failed: [...], checks: {name: [findings]}, line_readings, ms}.
When the tool cannot run (no node, no Chrome, it dies) every page gets ok=False with failed=['tool'] and the reason:
a page that could not be checked is not a page that passed.
"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE.parent / 'qa' / 'template_gate.mjs'
CHECKS = ('sideways', 'errors', 'distorted', 'h1', 'legible', 'overlap', 'cut', 'first', 'blank')


def _registry():
    key = 'swarmsite_templates_registry'
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, HERE / 'registry.py')
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


def check(files, settle=None, pause=None, crops=None, timeout=None):
    files = [str(f) for f in files]
    if not files:
        return []
    cmd = ['node', str(TOOL)] + files
    for flag, v in (('--settle', settle), ('--pause', pause), ('--crops', crops)):
        if v is not None:
            cmd += [flag, str(v)]
    why = ''
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout or 120 + 90 * len(files))
        out, why = r.stdout, (r.stderr or '').strip()[-300:]
    except (OSError, subprocess.SubprocessError) as ex:
        out, why = '', '%s: %s' % (type(ex).__name__, str(ex)[:200])
    got = {}
    for line in out.splitlines():
        try:
            x = json.loads(line)
        except ValueError:
            continue
        if isinstance(x, dict) and 'page' in x:
            got[x['page']] = x
    res = []
    for f in files:
        x = got.get(f)
        if x is None or not isinstance(x.get('ok'), bool) or (x.get('ok') and x.get('failed')):
            x = {'page': f, 'ok': False, 'failed': ['tool'], 'error': why or 'the gate printed nothing for this page'}
        res.append(x)
    return res


def shown(variants):
    """the rule of the gate: only a variant whose every check passed is shown"""
    return [v for v in variants if v.get('ok') is True and not v.get('failed')]


def render_and_check(d, slugs, outdir, media_base='', root=None, **kw):
    """Render the data through each template into outdir/<slug>.html (media at `media_base`, by default beside the
    page) and gate every page. The caller writes the media files; the gate judges what the browser really shows."""
    R = _registry()
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    files = []
    for s in slugs:
        f = outdir / (s + '.html')
        f.write_text(R.render(s, d, media_base, root=root), encoding='utf-8')
        files.append(f)
    return [{'slug': s, 'file': str(f), 'ok': g['ok'], 'failed': g['failed'], 'gate': g} for s, f, g in zip(slugs, files, check(files, **kw))]


if __name__ == '__main__':                                          # python3 lib/templates/gate.py page.html [more …]
    results = check(sys.argv[1:])
    for x in results:
        print(json.dumps(x, ensure_ascii=False))
    sys.exit(0 if all(x['ok'] for x in results) else 1)
