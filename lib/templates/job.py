"""job.py — the template path of a job, after capture and the reader: adapt → select → render three → gate; and,
for a variant the visitor may download, the package.

    python3 lib/templates/job.py build <job dir> --out <dir> [--base URL] [--limit 3] [--library DIR]
        --library   a folder holding media/library (else $SWARMSITE_LIBRARY, else the repo's); none → no made pictures
        --form F --photos DIR   a site from nothing: the visitor's form (JSON, lib/templates/form.py) and their uploads,
                    in place of a capture (<job dir> is then only where the job lives)
        <job dir>   capture's files (inventory, assets, images, geometry …) and the reader's factsheet.json
        --out       written there:
                      data.json         the client's data (adapter output, private keys removed)
                      adapter.json      what the adapter could not fill (gaps) and the rules it applied
                      media/…           every picture the data names, written from the capture
                      <slug>.html       each chosen variant, media beside it — the page the gate judges and the package is made from
                      <slug>.data.json  a variant's own data when it takes made pictures (three variants, three families)
                      media/library/…   the library files the variants show
                      pub/<slug>.html   the same render with its media at --base (the page a preview address serves)
                      templates.json    {niche, pictures, chosen, shown, rejected, timings_ms}
        prints templates.json as one line
    python3 lib/templates/job.py package <out dir> <slug> <zip> [--verify]
        prints {slug, ok, why, bytes, files, ms} as one line and exits 0; ok=false means the package is refused

No model call: the reader's call happened before this, in the job. No network except the gate's and the package's
font files (Google Fonts) and nothing at all for the rest. A variant that fails the gate is not shown.
"""
import base64
import importlib.util
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _mod(name):
    key = 'swarmsite_templates_' + name
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, HERE / (name + '.py'))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


def _bytes(data_uri):
    head, _, body = str(data_uri or '').partition(',')
    if not head.startswith('data:') or not body:
        return None
    try:
        return base64.b64decode(body) if ';base64' in head else body.encode('utf-8')
    except ValueError:
        return None


def write_media(seed, d, out):
    """every picture the data names, written from the capture's own bytes; -> (written, missing)"""
    by_id = {im.get('id'): im for im in seed.get('images') or [] if isinstance(im, dict)}
    marks = (seed.get('logos') or {}).get('items') or []
    written, missing = [], []
    for rel, src in (d.get('_media') or {}).items():
        if '..' in Path(rel).parts or Path(rel).is_absolute() or not rel.startswith('media/'):
            missing.append(rel)
            continue
        if src.get('from') == 'images':
            raw = _bytes((by_id.get(src.get('id')) or {}).get('data'))
        elif src.get('from') == 'assets.logo':
            raw = _bytes(((seed.get('assets') or {}).get('logo') or {}).get('data'))
        elif src.get('from') == 'logos':
            i = src.get('index')
            raw = _bytes(marks[i].get('data')) if isinstance(i, int) and 0 <= i < len(marks) else None
        else:
            raw = None
        if not raw:
            missing.append(rel)
            continue
        f = Path(out) / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(raw)
        written.append(rel)
    return written, missing


def _drop(d, paths):
    """the data without pictures whose files could not be written: a page never asks for a file that is not there"""
    gone = set(paths)
    if not gone:
        return d
    def clean(v):
        if isinstance(v, dict):
            if v.get('src') in gone:
                return None
            return {k: x for k, x in ((k, clean(x)) for k, x in v.items()) if not (k in ('img', 'logo', 'poster') and isinstance(v.get(k), str) and v[k] in gone)}
        if isinstance(v, list):
            return [x for x in (clean(x) for x in v) if x is not None]
        return v
    out = clean(d)
    if (out.get('brand') or {}).get('logo') is None and 'brand' in out:
        out['brand']['logo'] = None
    return out


def from_form(form, photos, out):
    """a site from nothing: the visitor's form and uploaded photographs as the contract data, the photographs written
    beside it; -> (data, notes, written, missing)"""
    d, notes = _mod('form').from_form(form, photos)
    written, missing = [], []
    for rel, name in notes['media'].items():
        f = Path(photos) / name
        if rel.startswith('media/') and '..' not in Path(rel).parts and f.is_file():
            (Path(out) / rel).parent.mkdir(parents=True, exist_ok=True)
            (Path(out) / rel).write_bytes(f.read_bytes())
            written.append(rel)
        else:
            missing.append(rel)
    return d, notes, written, missing


def build(job_dir, out, base='', limit=3, gate_kw=None, library=None, form=None, photos=None):
    """job_dir: a capture with the reader's factsheet — or, with `form`, the visitor's form (a dict) and `photos`, the
    folder of their uploads: the same data, the same choice, the same gate"""
    A, R, S, G = _mod('adapt'), _mod('registry'), _mod('select'), _mod('gate')
    out = Path(out)
    (out / 'pub').mkdir(parents=True, exist_ok=True)
    t = {}
    t0 = time.perf_counter()
    if form is not None:
        d, notes, written, missing = from_form(form, photos, out)
        d = _drop(d, missing)
        t['adapt'] = round((time.perf_counter() - t0) * 1000)
        notes = {'source': 'form', 'gaps': notes['gaps'], 'rules': notes['rules']}
    else:
        seed = A.load_seed(job_dir)
        d = A.adapt(seed)
        t['adapt'] = round((time.perf_counter() - t0) * 1000)
        t0 = time.perf_counter()
        written, missing = write_media(seed, d, out)
        d = _drop(d, missing)
        notes = d.get('_adapter', {})
    data = {k: v for k, v in d.items() if not k.startswith('_')}
    (out / 'data.json').write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    (out / 'adapter.json').write_text(json.dumps({**notes, 'media_missing': missing}, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    t['media'] = round((time.perf_counter() - t0) * 1000)
    t0 = time.perf_counter()
    # made pictures: three families of the prepared library, in the order the client's niche gives (owner, 2026-11-12);
    # none for places, clinics, law, services, shops, schools, people, nonprofits — and none when there is no library
    PI = _mod('pictures')
    lib_root = PI.root_of(library)
    three = PI.pick_three(data, lib_root) if lib_root else []
    sel = S.select({**data, 'media': {**(data.get('media') or {}), 'made': three[0]}} if three else data, limit=limit)
    t['select'] = round((time.perf_counter() - t0) * 1000)
    t0 = time.perf_counter()
    files, families, copied = [], {}, set()
    for i, c in enumerate(sel['chosen']):
        made = three[i % len(three)] if three else {}
        v = {**data, 'media': {**(data.get('media') or {}), 'made': made}} if made else data
        for rel in PI.files(made):                                    # the library files this variant shows, beside it like any media
            if rel not in copied and rel.startswith('media/') and '..' not in Path(rel).parts:
                (out / rel).parent.mkdir(parents=True, exist_ok=True)
                (out / rel).write_bytes((lib_root / rel).read_bytes())
                copied.add(rel)
        if made:
            families[c['slug']] = {'family': made.get('family'), 'palette': made.get('palette')}
            (out / (c['slug'] + '.data.json')).write_text(json.dumps(v, ensure_ascii=False) + '\n', encoding='utf-8')
        f = out / (c['slug'] + '.html')
        f.write_text(R.render(c['slug'], v, ''), encoding='utf-8')
        (out / 'pub' / (c['slug'] + '.html')).write_text(R.render(c['slug'], v, base), encoding='utf-8')
        files.append(f)
    t['render'] = round((time.perf_counter() - t0) * 1000)
    t0 = time.perf_counter()
    gates = G.check(files, **(gate_kw or {})) if files else []
    t['gate'] = round((time.perf_counter() - t0) * 1000)
    chosen = []
    for c, g in zip(sel['chosen'], gates):
        chosen.append({**c, **({'made': families[c['slug']]} if c['slug'] in families else {}), 'ok': g['ok'], 'failed': g['failed'], 'gate': {k: v for k, v in (g.get('checks') or {}).items() if v}, 'gate_ms': g.get('ms'), **({'error': g['error']} if g.get('error') else {})})
    res = {'niche': sel['niche'], 'pictures': sel['pictures'], 'chosen': chosen, 'shown': [c['slug'] for c in chosen if c['ok'] and not c['failed']],
           'rejected': sel['rejected'], 'media': {'written': len(written), 'missing': missing, 'library': len(copied)}, 'group': PI.niche_group(data)[0], 'timings_ms': t}
    (out / 'templates.json').write_text(json.dumps(res, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    return res


def package(out, slug, zip_path, verify=True, workdir=None):
    P, R = _mod('package'), _mod('registry')
    out = Path(out)
    t0 = time.perf_counter()
    try:
        own = out / (slug + '.data.json')                             # a variant with made pictures has its own data
        data = json.loads((own if own.is_file() else out / 'data.json').read_text(encoding='utf-8'))
        shown = json.loads((out / 'templates.json').read_text(encoding='utf-8')).get('shown') or []
        if slug not in shown:
            raise P.PackageError('%s is not a variant this job shows' % slug)
        rep = P.build(slug, data, out, zip_path)
    except (P.PackageError, OSError, ValueError) as ex:
        return {'slug': slug, 'ok': False, 'why': [str(ex)[:300]], 'ms': round((time.perf_counter() - t0) * 1000)}
    res = {'slug': slug, 'ok': True, 'why': [], 'bytes': rep['bytes'], 'files': len(rep['files']), 'fonts': len(rep['fonts'])}
    if verify:
        import tempfile
        with tempfile.TemporaryDirectory(prefix='pkg-', dir=workdir) as tmp:
            v = P.verify(out / (slug + '.html'), zip_path, tmp)
        res.update(ok=bool(v.get('ok')), why=v.get('why') or [], compared=[{k: w.get(k) for k in ('at', 'screens', 'worst')} for w in v.get('widths') or []])
    res['ms'] = round((time.perf_counter() - t0) * 1000)
    return res


if __name__ == '__main__':
    a = sys.argv[1:]
    opt = lambda k, dflt=None: a[a.index(k) + 1] if k in a else dflt
    if a[:1] == ['build'] and len(a) >= 2:
        form = json.loads(Path(opt('--form')).read_text(encoding='utf-8')) if opt('--form') else None
        print(json.dumps(build(a[1], opt('--out') or str(Path(a[1]) / 'templates'), opt('--base', ''), int(opt('--limit', 3)), library=opt('--library'),
                               form=form, photos=opt('--photos')), ensure_ascii=False))
    elif a[:1] == ['package'] and len(a) >= 4:
        r = package(a[1], a[2], a[3], verify='--verify' in a)
        print(json.dumps(r, ensure_ascii=False))   # exit 0 either way: the verdict is `ok`, an exit code is for a crash
    else:
        raise SystemExit(__doc__)
