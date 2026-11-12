"""stress.py — does a template hold for clients it has not seen?

A template is measured on two or three test clients, and those happen to have two plans, three steps, seven features.
`maze` ran 263 px past the right edge on real captures with three to five plans. So before a template is offered it
is tried on made-up variants of a client, and the gate (lib/qa/template_gate.mjs) must pass on each:

    plans-1 · plans-3 · plans-5 · features-2 · features-9 · steps-1 · steps-6 · h1-12-words · button-40 · no-faq · no-photographs
    and the soft sections absent (select.py offers a template that misses one of them with that section dropped, so the
    template must hold without it): no-features · no-close · no-steps · no-step-pictures · no-screens · no-made ·
    minimal (the hero, the brand, three photographs and the contact lines; nothing else) · photos-3 (the client as given
    with only its first three photographs: a template that breaks on it names `photos` in `hard` of its needs.json)

    variants(d) -> {name: data, or None when the client has nothing of that kind to vary}
    run(slugs, d, outdir, media=None) -> {slug: {'base': result, 'variants': {name: result}, 'fails': [names]}}
    python3 lib/templates/stress.py [slug …] [--client FILE] [--media DIR] [--out DIR] [--json]
    python3 lib/templates/stress.py --sweep [slug …] [--out DIR] [--json]     every template × every test client of its niche × the soft variants

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
NAMES = ('plans-1', 'plans-3', 'plans-5', 'features-2', 'features-9', 'steps-1', 'steps-6', 'h1-12-words', 'button-40', 'no-faq', 'no-photographs',
         'no-features', 'no-close', 'no-steps', 'no-step-pictures', 'no-screens', 'no-made', 'minimal', 'photos-3')
# what the minimal client keeps: who it is, its opening, how to reach it — the least a capture yields (see minimal())
MINIMAL_KEEP = ('brand', 'lang', 'kind', 'character', 'palette', 'type', 'nav', 'hero', 'cta', 'signin', 'contact', 'foot', '_note')
PLACE_CONTACT = ('address', 'phone', 'email', 'hours', 'booking', 'social')


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
    # the soft sections absent, each alone: the block is not in the data at all (that is how the adapter leaves a
    # section it could not read); a client without the block has no variant of it
    for name, key in (('no-features', 'features'), ('no-close', 'close'), ('no-steps', 'steps')):
        v = None
        if _present(d.get(key)):
            v = copy.deepcopy(d)
            v.pop(key)
        out[name] = v
    v = None
    if any(isinstance(i, dict) and i.get('img') for i in (d.get('steps') or {}).get('items') or []):
        v = copy.deepcopy(d)
        for i in v['steps']['items']:
            if isinstance(i, dict):
                i.pop('img', None)
    out['no-step-pictures'] = v
    out['no-screens'] = _without_media(d, ('screens', 'phones', 'video'))
    out['no-made'] = _without_media(d, ('made',))
    out['minimal'] = minimal(d)
    v = None
    if len([p for p in m.get('photos') or [] if isinstance(p, dict)]) > 3:
        v = copy.deepcopy(d)
        gone = {p.get('src') for p in v['media']['photos'][3:] if isinstance(p, dict)}
        v['media']['photos'] = v['media']['photos'][:3]
        for holder, key in ((v.get('steps') or {}, 'items'), (v.get('place') or {}, 'spaces')):
            for it in holder.get(key) or []:
                if isinstance(it, dict) and it.get('img') in gone:
                    it.pop('img')
    out['photos-3'] = v
    return {n: out[n] for n in NAMES}


def _present(v):
    if isinstance(v, dict):
        return any(_present(x) for x in v.values())
    if isinstance(v, list):
        return any(_present(x) for x in v)
    return v not in (None, '', False)


def _without_media(d, kinds):
    """the client without these kinds of picture, and every step or space picture that was one of them; None when it
    has none of them"""
    m = d.get('media') if isinstance(d.get('media'), dict) else {}
    if not any(_present(m.get(k)) for k in kinds):
        return None
    v = copy.deepcopy(d)
    gone = set()
    for k in kinds:
        x = m.get(k)
        for p in (x if isinstance(x, list) else [x] if isinstance(x, dict) else []):
            if isinstance(p, dict):
                gone.update(q for q in (p.get('src'), p.get('poster')) if q)
    for k in kinds:
        v['media'][k] = None if k == 'video' else ({} if k == 'made' else [])
    if 'made' in kinds:
        v['media'].pop('made', None)
    for holder, key in ((v.get('steps') or {}, 'items'), (v.get('place') or {}, 'spaces')):
        for it in holder.get(key) or []:
            if isinstance(it, dict) and it.get('img') in gone:
                it.pop('img')
    return v


def minimal(d):
    """The least a capture yields: the brand, the opening, at most three photographs and the contact lines; every
    other block absent. A client with fewer than three photographs keeps what it has (stress data invents no
    picture). None when that is the client as given."""
    v = {k: copy.deepcopy(d[k]) for k in MINIMAL_KEEP if k in d}
    m = d.get('media') if isinstance(d.get('media'), dict) else {}
    v['media'] = {'screens': [], 'phones': [], 'photos': copy.deepcopy([p for p in m.get('photos') or [] if isinstance(p, dict)][:3]), 'video': None}
    place = d.get('place') if isinstance(d.get('place'), dict) else {}
    if any(_present(place.get(k)) for k in PLACE_CONTACT):
        v['place'] = {k: copy.deepcopy(place[k]) for k in PLACE_CONTACT if k in place}
    rest = [k for k in d if k not in MINIMAL_KEEP and k not in ('media', 'place') and _present(d[k])]
    rest += [k for k in ('screens', 'phones', 'video') if _present(m.get(k))] + (['photos'] if len(m.get('photos') or []) > 3 else [])
    rest += [k for k in place if k not in PLACE_CONTACT and _present(place[k])]
    return v if rest else None                                       # already no more than the minimal client: nothing to take away


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


def with_made(d, root=None):
    """the client with the first family of made pictures the library gives it (what a job adds before it renders), or
    as given when its kind takes none or there is no library"""
    PI = _sibling('pictures')
    lib = PI.root_of(root)
    three = PI.pick_three(d, lib) if lib else []
    if not three:
        return d
    return {**d, 'media': {**(d.get('media') or {}), 'made': three[0]}}


def run(slugs, d, outdir, media=None, made=False, names=None, **kw):
    """made=True: the client as given carries the made pictures a job would give it — the library's own files, beside
    the stand-ins — so that no-made is a real variant. names: only these variants (default every one)."""
    R, G = _sibling('registry'), _sibling('gate')
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    if made:
        d = with_made(d)
    if media:
        base_url = Path(media).resolve().as_uri() + '/'
    else:
        stand_ins(d, outdir)
        base_url = outdir.resolve().as_uri() + '/'
        PI = _sibling('pictures')
        lib = PI.root_of() if (d.get('media') or {}).get('made') else None
        for rel in PI.files((d.get('media') or {}).get('made')) if lib else []:
            if (lib / rel).is_file():                               # a made picture is what the library holds, not a stand-in
                (outdir / rel).write_bytes((lib / rel).read_bytes())
    vs = {n: v for n, v in variants(d).items() if names is None or n in names}
    jobs = []
    for s in slugs:
        for name, v in [('base', d)] + list(vs.items()):
            if v is None:
                continue
            f = outdir / ('%s--%s.html' % (s, name))
            try:
                f.write_text(R.render(s, v, base_url), encoding='utf-8')
            except Exception as ex:                                  # a template that raises on a variant has failed it
                jobs.append((s, name, {'page': str(f), 'ok': False, 'failed': ['render'], 'checks': {'render': [{'error': '%s: %s' % (type(ex).__name__, str(ex)[:160])}]}}))
                continue
            jobs.append((s, name, f))
    pages = [f for _, _, f in jobs if not isinstance(f, dict)]
    got = iter(G.check(pages, **kw))
    results = [f if isinstance(f, dict) else next(got) for _, _, f in jobs]
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


FIXTURES = HERE.parent.parent / 'tests' / 'fixtures' / 'templates'
SOFT_VARIANTS = ('no-features', 'no-close', 'no-steps', 'no-step-pictures', 'no-screens', 'no-made', 'minimal', 'photos-3')


def sweep(outdir, slugs=None, names=SOFT_VARIANTS, fixtures=None, **kw):
    """Every template through every test client of its niche, as given and in each of `names`; a software client
    with the made pictures a job gives it. The verdict is the gate's own (ok on the page, not only 'nothing new'):
    a soft section dropped is a page shown to a visitor. -> [{'slug', 'client', 'variant', 'ok', 'failed', 'checks'}]"""
    R, S = _sibling('registry'), _sibling('select')
    fixtures = fixtures or sorted(FIXTURES.glob('*.json'))
    rows = []
    for f in fixtures:
        d = json.loads(Path(f).read_text(encoding='utf-8'))
        niche = S.client(d)['niche']
        mine = [t['slug'] for t in R.list_templates() if t['selectable'] and (slugs is None or t['slug'] in slugs)
                and set(x for w in t['needs'].get('niche') or [] for x in S.niche_tags(w)) & set(niche)]
        if not mine:
            continue
        rep = run(mine, d, Path(outdir) / Path(f).stem, made=True, names=names, **kw)
        for slug, r in rep.items():
            for name, res in [('base', r['base'])] + [(n, r['variants'].get(n)) for n in names]:
                if res is not None:
                    rows.append({'slug': slug, 'client': Path(f).stem, 'variant': name, 'ok': res['ok'], 'failed': res['failed'], 'checks': res.get('checks') or {}})
    return rows


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
    sweep_ = '--sweep' in argv                                        # every template through every test client of its niche
    slugs = [a for a in argv if not a.startswith('--')] or _sibling('registry').slugs()
    client = Path(opt.get('--client') or HERE.parent.parent / 'tests' / 'fixtures' / 'templates' / 'tallyfern.json')
    import tempfile
    tmp = None
    if '--out' not in opt:
        tmp = tempfile.TemporaryDirectory(prefix='stress-')
    if sweep_:
        rep = sweep(opt.get('--out') or tmp.name, slugs=[a for a in argv if not a.startswith('--')] or None)
        print(json.dumps(rep, ensure_ascii=False) if as_json else '\n'.join('%-14s %-14s %-17s %s' % (r['slug'], r['client'], r['variant'], 'ok' if r['ok'] else 'FAILS ' + ', '.join(r['failed'])) for r in rep))
        if tmp:
            tmp.cleanup()
        sys.exit(1 if any(not r['ok'] for r in rep) else 0)
    rep = run(slugs, json.loads(client.read_text(encoding='utf-8')), opt.get('--out') or tmp.name, opt.get('--media'))
    print(json.dumps(rep, ensure_ascii=False) if as_json else table(rep))
    if tmp:
        tmp.cleanup()
    sys.exit(1 if any(r['fails'] or not (r['base'] or {}).get('ok') for r in rep.values()) else 0)
