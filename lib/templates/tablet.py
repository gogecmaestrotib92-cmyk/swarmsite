"""tablet.py — a design stands in its desk composition from 768 px, not only from where its template starts it.

Owner, 2026-11-22: a customer chooses a design from its desk look (the chooser shows every design 1440 wide, drawn
smaller), so a tablet or a narrow window must show that composition too — not the phone's, set large. Measured that
day on the 48 templates: 7 stood in their desk composition at 768 px, 14 at 900, 33 at 1024.

    threshold(page) -> the width (px) the page's desk rules start at, or None when it has none between 769 and 1101
    desk(page)      -> the page with those rules applied from 768 px and, between 768 and that width, the whole page
                       drawn smaller to fit (as the chooser draws it); a page without a threshold is returned as it is
    python3 lib/templates/tablet.py --sweep [slug …] [--out DIR] [--json]
                       every template × every test client of its niche: the page with desk() applied, through the gate
                       at 768 and 900 and read for its composition (lib/qa/composition.mjs) -> who may be switched on

How. Every width query of the page between 769 px and the threshold T is rewritten to 768 px (min-width) or 767 px
(max-width), so at 768–T the page has exactly the rules it has at T; a script first in <body> then sets `zoom` on
<html> to window width / T in that range, so the layout made for T fits the window. Nothing changes at 767 px and
below, nor at T and above: the preview at 1440 and 390, and the package compared with it, are byte-for-byte the rules
they were.

It is NOT applied to every template. A design whose opening is sized by the window's height, or whose pictures are
already small at T, breaks when drawn smaller (measured: 12 of 48 gained a fault). registry.render() applies desk()
only to a template whose needs.json says "tablet": "desk" — written there only after --sweep passed for it on every
test client of its niche. A template without the line stays as it was. No template file is rewritten.
"""
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FROM, CAP = 768, 1101                 # desk rules from here; a template whose desk starts above CAP would be drawn under 0.7
_Q = re.compile(r'\((min|max)-width:\s*([0-9.]+)px\)')
_STYLE = re.compile(r'(<style\b[^>]*>)(.*?)(</style>)', re.S | re.I)
MARK = 'data-sw-tablet'


def _css(page):
    return ''.join(m.group(2) for m in _STYLE.finditer(page))


def threshold(page):
    at = set()
    for kind, n in _Q.findall(_css(page)):
        b = float(n) if kind == 'min' else float(n) + 1
        if FROM < b <= CAP:
            at.add(int(round(b)))
    return max(at) if at else None


def desk(page):
    if MARK in page:
        return page
    t = threshold(page)
    if not t:
        return page

    def q(m):
        kind, n = m.group(1), float(m.group(2))
        if kind == 'min' and FROM < n <= t:
            return '(min-width:%dpx)' % FROM
        if kind == 'max' and FROM <= n <= t - 1:
            return '(max-width:%dpx)' % (FROM - 1)
        return m.group(0)
    page = _STYLE.sub(lambda m: m.group(1) + _Q.sub(q, m.group(2)) + m.group(3), page)
    js = ('<script %s>(function(){var T=%d,h=document.documentElement;function f(){var w=window.innerWidth;'
          'h.style.zoom=(w>=%d&&w<T)?String(w/T):"";}f();addEventListener("resize",f);})();</script>') % (MARK, t, FROM)
    return re.sub(r'(<body\b[^>]*>)', lambda m: m.group(1) + js, page, count=1)


def _sib(name):
    key = 'swarmsite_templates_' + name
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, HERE / (name + '.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


def sweep(outdir, slugs=None):
    """-> {slug: {'threshold', 'clients': {name: {'ok', 'failed', 'desk': {768: bool, 900: bool}}}, 'pass': bool, 'why'}}"""
    ST, R, SE, PI = _sib('stress'), _sib('registry'), _sib('select'), _sib('pictures')
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    pages, rep = [], {}
    for f in sorted(ST.FIXTURES.glob('*.json')):
        d = json.loads(f.read_text(encoding='utf-8'))
        niche = SE.client(d)['niche']
        mine = [t['slug'] for t in R.list_templates() if t['selectable'] and (slugs is None or t['slug'] in slugs)
                and set(x for w in t['needs'].get('niche') or [] for x in SE.niche_tags(w)) & set(niche)]
        if not mine:
            continue
        d = ST.with_made(d)
        cdir = outdir / f.stem
        cdir.mkdir(exist_ok=True)
        ST.stand_ins(d, cdir)
        lib = PI.root_of() if (d.get('media') or {}).get('made') else None
        for rel in PI.files((d.get('media') or {}).get('made')) if lib else []:
            if (lib / rel).is_file():
                (cdir / rel).parent.mkdir(parents=True, exist_ok=True)
                (cdir / rel).write_bytes((lib / rel).read_bytes())
        for s in mine:
            raw = R.render(s, d, cdir.resolve().as_uri() + '/', tablet=False)
            page = desk(raw)
            p = outdir / ('%s--%s.html' % (s, f.stem))
            p.write_text(page, encoding='utf-8')
            rep.setdefault(s, {'threshold': threshold(raw), 'clients': {}})['clients'][f.stem] = {'page': str(p)}
            pages.append(p)
    qa = HERE.parent / 'qa'
    gate = subprocess.run(['node', str(qa / 'template_gate.mjs')] + [str(p) for p in pages] + ['--widths', '768x1024,900x900', '--jobs', '4'], capture_output=True, text=True)
    comp = subprocess.run(['node', str(qa / 'composition.mjs')] + [str(p) for p in pages], capture_output=True, text=True)
    by = {}
    for line in gate.stdout.splitlines():
        try:
            x = json.loads(line)
            by[str(Path(x['page']).resolve())] = x
        except (ValueError, KeyError):
            pass
    try:
        compo = json.loads(comp.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        compo = {}
    for s, r in rep.items():
        why = []
        if not r['threshold']:
            why.append('no desk threshold between %d and %d px' % (FROM + 1, CAP))
        for name, c in r['clients'].items():
            g = by.get(str(Path(c['page']).resolve())) or {}
            c['ok'], c['failed'] = bool(g.get('ok')), g.get('failed') or ['not gated']
            c['desk'] = (compo.get(str(Path(c['page']).resolve())) or {}).get('desk') or {}
            if not c['ok']:
                why.append('%s: %s' % (name, ', '.join(c['failed'])))
            if not all(c['desk'].get(str(w)) for w in (768, 900)):
                why.append('%s: not in its desk composition at 768 and 900' % name)
        r['pass'], r['why'] = not why, why
    return rep


if __name__ == '__main__':
    a = sys.argv[1:]
    if '--sweep' not in a:
        sys.exit('usage: python3 lib/templates/tablet.py --sweep [slug …] [--out DIR] [--json]')
    out = a[a.index('--out') + 1] if '--out' in a else 'bench/runs/_tablet'
    slugs = [x for x in a if not x.startswith('--') and x != out] or None
    rep = sweep(out, slugs)
    if '--json' in a:
        print(json.dumps(rep, indent=1))
    else:
        for s in sorted(rep):
            r = rep[s]
            print('%-16s %-5s T=%-5s %s' % (s, 'PASS' if r['pass'] else 'no', r['threshold'], '; '.join(r['why'])[:150]))
        print('%d of %d may be switched on' % (sum(r['pass'] for r in rep.values()), len(rep)))
