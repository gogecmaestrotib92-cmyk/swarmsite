"""stress.py — does a template hold for clients it has not seen?

A template is measured on two or three test clients, and those happen to have two plans, three steps, seven features.
`maze` ran 263 px past the right edge on real captures with three to five plans. So before a template is offered it
is tried on made-up variants of a client, and the gate (lib/qa/template_gate.mjs) must pass on each:

    plans-1 · plans-3 · plans-5 · features-2 · features-9 · steps-1 · steps-6 · h1-12-words · button-40 · no-faq · no-photographs

    variants(d) -> {name: data, or None when the client has nothing of that kind to vary}
    run(slugs, d, outdir, media=None) -> {slug: {'base': result, 'variants': {name: result}, 'fails': [names]}}
    python3 lib/templates/stress.py [slug …] [--client FILE] [--media DIR] [--out DIR] [--json]

The variants are stress data, never shown to a client: longer lists repeat the client's own items under numbered names,
the long heading and the long label are made from the client's own words. A result names what fails in the variant
that does NOT fail on the client as given (`new`), so that a fault of the client's own page is not counted against the
variant; the client as given is reported as `base`.

Pictures. With --media the client's real files are used (the research folder has them for the test clients). Without
it every picture the data names is drawn as a plain two-tone field of the stated proportions in the client's own
colours — enough to hold the layout, and a fair ground to read text on; a film has only its poster.
"""
import copy
import importlib.util
import json
import struct
import sys
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
NAMES = ('plans-1', 'plans-3', 'plans-5', 'features-2', 'features-9', 'steps-1', 'steps-6', 'h1-12-words', 'button-40', 'no-faq', 'no-photographs')


def _sibling(name):
    key = 'swarmsite_templates_' + name
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, HERE / (name + '.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


def _resized(items, n, label):
    """n items made of the client's own, in order, repeating; a repeated one gets a number so that two are never alike"""
    out = []
    for i in range(n):
        it = copy.deepcopy(items[i % len(items)])
        if i >= len(items) and isinstance(it, dict):
            for k in label:
                if isinstance(it.get(k), str) and it[k]:
                    it[k] = '%s %d' % (it[k], i + 1)
                    break
        out.append(it)
    return out


def _words(d):
    h = d.get('hero') or {}
    texts = [h.get('title'), h.get('text'), h.get('text2'), (d.get('statement') or {}).get('text'), (d.get('close') or {}).get('text')]
    return [w for t in texts if isinstance(t, str) for w in t.split()]


def variants(d):
    out = {}

    def block(name, key, n, label):
        v = None
        items = (d.get(key) or {}).get('items') if isinstance(d.get(key), dict) else None
        if isinstance(items, list) and items:
            v = copy.deepcopy(d)
            v[key]['items'] = _resized(items, n, label)
        out[name] = v
    for n in (1, 3, 5):
        block('plans-%d' % n, 'plans', n, ('name',))
    for n in (2, 9):
        block('features-%d' % n, 'features', n, ('t',))
    for n in (1, 6):
        block('steps-%d' % n, 'steps', n, ('title',))
    words = _words(d)
    v = copy.deepcopy(d)
    title = ((d.get('hero') or {}).get('title') or '').split()
    extra = [w for w in words[len(title):] if w]
    while len(title) < 12 and extra:
        title.append(extra.pop(0).strip('.,;:!?—–'))
    v.setdefault('hero', {})['title'] = ' '.join(w for w in title[:12] if w)
    out['h1-12-words'] = v if len(v['hero']['title'].split()) == 12 else None
    v = copy.deepcopy(d)
    spots = [x for x in ((v.get('hero') or {}).get('primary'), v.get('cta'), (v.get('close') or {}).get('cta')) if isinstance(x, dict) and x.get('t')]
    for x in spots:
        label = x['t']
        for w in words:
            if len(label) >= 40:
                break
            label += ' ' + w.strip('.,;:!?—–')
        x['t'] = label[:40].rstrip()
    out['button-40'] = v if spots and all(len(x['t']) >= 36 for x in spots) else None
    v = None
    if (d.get('faq') or {}).get('items'):
        v = copy.deepcopy(d)
        v.pop('faq')
    out['no-faq'] = v
    # no photographs. A client without photographs to begin with (a product shown in screens) loses every picture
    # instead, so that the variant is never the client as given.
    m = d.get('media') if isinstance(d.get('media'), dict) else {}
    v = copy.deepcopy(d)
    if m.get('photos'):
        gone = {p.get('src') for p in m['photos'] if isinstance(p, dict)}
        v['media']['photos'] = []
    elif any(m.get(k) for k in ('screens', 'phones', 'video')):
        gone = {p.get('src') for k in ('screens', 'phones') for p in m.get(k) or [] if isinstance(p, dict)}
        v['media'].update(screens=[], phones=[], video=None)
    else:
        gone, v = None, None
    if v is not None:
        for holder, key in ((v.get('steps') or {}, 'items'), (v.get('place') or {}, 'spaces')):
            for it in holder.get(key) or []:
                if isinstance(it, dict) and it.get('img') in gone:
                    it.pop('img')
    out['no-photographs'] = v
    return {n: out[n] for n in NAMES}


# ───────────────────────── stand-in pictures
def _rgb(h, fallback=(128, 128, 128)):
    h = str(h or '').lstrip('#')
    try:
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) if len(h) == 6 else fallback
    except ValueError:
        return fallback


def png(w, h, top, bottom):
    """a w×h picture that goes from one colour at the top to another at the bottom"""
    rows = bytearray()
    for y in range(h):
        t = y / max(1, h - 1)
        rows += b'\x00' + bytes(round(a + (b - a) * t) for a, b in zip(top, bottom)) * w
    chunk = lambda kind, data: struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(bytes(rows), 9)) + chunk(b'IEND', b'')


def stand_ins(d, outdir):
    """Write a stand-in for every picture the data names, under outdir, at the data's own paths. A picture keeps its
    stated proportion (drawn at most 480 px long: it only has to hold its place); a film is not drawn."""
    R = _sibling('registry')
    pal = d.get('palette') or {}
    ground, ink = _rgb(pal.get('ground'), (245, 245, 245)), _rgb(pal.get('ink'), (20, 20, 20))
    mix = lambda t: tuple(round(g + (i - g) * t) for g, i in zip(ground, ink))
    sizes = {}

    def walk(v):
        if isinstance(v, dict):
            if isinstance(v.get('src'), str) and v.get('w') and v.get('h'):
                sizes[v['src']] = (int(v['w']), int(v['h']))
            if isinstance(v.get('poster'), str) and v.get('w') and v.get('h'):
                sizes[v['poster']] = (int(v['w']), int(v['h']))
            for x in v.values():
                walk(x)
        elif isinstance(v, list):
            for x in v:
                walk(x)
    walk(d)
    written = []
    for p in R.media_paths(d):
        if p.lower().split('?')[0].endswith(('.mp4', '.webm', '.mov', '.svg')):
            if p.lower().endswith('.svg'):
                f = Path(outdir) / p
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 24" width="120" height="24"><rect width="120" height="24" rx="4" fill="rgb(%d,%d,%d)"/></svg>' % ink, encoding='utf-8')
                written.append(p)
            continue
        w, h = sizes.get(p, (1200, 800))
        k = 480 / max(w, h)
        f = Path(outdir) / p
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(png(max(8, round(w * k)), max(8, round(h * k)), mix(.30), mix(.42)))
        written.append(p)
    return written


# ───────────────────────── the run
def _new(base, res):
    """what fails in a variant that does not fail on the client as given"""
    if res.get('failed') == ['tool']:
        return ['tool']
    out = []
    for k, found in (res.get('checks') or {}).items():
        had = (base.get('checks') or {}).get(k) or []
        if k == 'legible':
            texts = {(x.get('at'), x.get('text')) for x in had}
            if any((x.get('at'), x.get('text')) not in texts for x in found):
                out.append(k)
        elif k in ('sideways', 'h1', 'errors'):
            if {x.get('at') for x in found} - {x.get('at') for x in had}:
                out.append(k)
        elif len(found) > len(had):
            out.append(k)
    return out


def run(slugs, d, outdir, media=None, **kw):
    R, G = _sibling('registry'), _sibling('gate')
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    if media:
        base_url = Path(media).resolve().as_uri() + '/'
    else:
        stand_ins(d, outdir)
        base_url = outdir.resolve().as_uri() + '/'
    vs = variants(d)
    jobs = []
    for s in slugs:
        for name, v in [('base', d)] + list(vs.items()):
            if v is None:
                continue
            f = outdir / ('%s--%s.html' % (s, name))
            f.write_text(R.render(s, v, base_url), encoding='utf-8')
            jobs.append((s, name, f))
    results = G.check([f for _, _, f in jobs], **kw)
    report = {s: {'base': None, 'variants': {n: None for n in vs}, 'fails': []} for s in slugs}
    for (s, name, f), res in zip(jobs, results):
        slim = {'ok': res['ok'], 'failed': res['failed'], 'checks': {k: v for k, v in (res.get('checks') or {}).items() if v}}
        if res.get('error'):
            slim['error'] = res['error']
        if name == 'base':
            report[s]['base'] = slim
        else:
            report[s]['variants'][name] = slim
    for s in slugs:
        base = report[s]['base'] or {}
        for name, res in report[s]['variants'].items():
            if res is None:
                continue
            res['new'] = _new(base, res)
            if res['new']:
                report[s]['fails'].append(name)
    return report


def table(report):
    lines = []
    for s, r in report.items():
        b = r['base'] or {}
        lines.append('%s — as given: %s' % (s, 'ok' if b.get('ok') else 'FAILS ' + ', '.join(b.get('failed') or ['?'])))
        for name, res in r['variants'].items():
            if res is None:
                lines.append('  %-16s —  (the client has nothing to vary)' % name)
            elif not res['new']:
                lines.append('  %-16s ok%s' % (name, '' if res['ok'] else '  (fails only what the client as given fails: %s)' % ', '.join(res['failed'])))
            else:
                bits = []
                for k in res['new']:
                    f = res['checks'].get(k) or []
                    if k == 'sideways':
                        bits.append('sideways ' + ', '.join('%spx at %s' % (x.get('px'), x.get('at')) for x in f))
                    elif k == 'legible':
                        bits.append('legible %d line(s), worst %s:1 "%s"' % (len(f), f[0].get('ratio'), f[0].get('text')))
                    elif k == 'overlap':
                        bits.append('overlap "%s" under "%s"' % (f[0].get('under'), f[0].get('upon')))
                    else:
                        bits.append('%s %s' % (k, json.dumps(f[:1], ensure_ascii=False)[:90]))
                lines.append('  %-16s FAILS  %s' % (name, ' · '.join(bits)))
    return '\n'.join(lines)


if __name__ == '__main__':
    argv, opt = sys.argv[1:], {}
    for flag in ('--client', '--media', '--out'):
        if flag in argv:
            i = argv.index(flag)
            opt[flag] = argv[i + 1]
            del argv[i:i + 2]
    as_json = '--json' in argv
    slugs = [a for a in argv if not a.startswith('--')] or _sibling('registry').slugs()
    client = Path(opt.get('--client') or HERE.parent.parent / 'tests' / 'fixtures' / 'templates' / 'tallyfern.json')
    import tempfile
    tmp = None
    if '--out' not in opt:
        tmp = tempfile.TemporaryDirectory(prefix='stress-')
    rep = run(slugs, json.loads(client.read_text(encoding='utf-8')), opt.get('--out') or tmp.name, opt.get('--media'))
    print(json.dumps(rep, ensure_ascii=False) if as_json else table(rep))
    if tmp:
        tmp.cleanup()
    sys.exit(1 if any(r['fails'] or not (r['base'] or {}).get('ok') for r in rep.values()) else 0)
