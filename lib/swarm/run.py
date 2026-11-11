"""run.py — the swarm loop. After the Designer (direct.py) has written direction.json:
  round 0: Reader (if not yet) → UX → Copy → UI → Visual → render
  round k: Critic looks at the render → routes each defect to its owner (copy / ui / visual / ux) → owners fix in parallel → bounded critic ops → render
Stops at --target score or --rounds. Prints one JSON line per event (the server turns them into swarm events) and a final {"done":…} line.
Opt-in, after the rounds (brief.json "compose": true, or SWARM_COMPOSE=1): the first screen of the winning page and the lists
below it are recomposed (lib/compose) and the composed page is kept only if it stands at least as high as the page it would replace.
Which page stands is decided on two tracks that are never added up (SWARMSITE_STUDIO_QUALITY_STANDARD.md §2): a page that
breaks no hard promise, then one that clears the technical bar, then the one the critic reads higher. SWARM_DECIDE=blend
brings back the one blended number. The page that ships is measured in a browser (lib/qa/measure.py) and what the
Standard says of the readings is written beside it (findings.json); in the composed path the critic's final look is given them.
Usage: python3 lib/swarm/run.py out/<slug> <blueprint-id> --out bp-<id>.html [--rounds 3] [--target 80]"""
import json, os, sys, time, subprocess, traceback, shutil, tempfile, hashlib
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'lib/swarm')); sys.path.insert(0, os.path.join(ROOT, 'lib/qa')); sys.path.insert(0, os.path.join(ROOT, 'lib'))
import agents as A
import critic as C
import measure as MEASURE
import standard as STANDARD
sys.path.insert(0, os.path.join(ROOT, 'lib/render'))
import rules as RULES
import coverage_report as Coverage
import pattern_stage as Patterns
import house as HOUSE
import moods as MOODS

def relock(slug_dir):
    """The house owns order and moves; agents own copy, pictures and layout details. Re-applied after every agent pass."""
    try:
        with A._document_lock:
            d = A.J(slug_dir, 'direction.json')
            if d and d.get('house'): A.W(slug_dir, 'direction.json', HOUSE.lock(d))
    except Exception as e: print(json.dumps({'event': {'role': 'Render', 'text': 'house lock skipped: ' + str(e)[:80]}}), flush=True)

def ev(role, text): print(json.dumps({"event": {"role": role, "text": str(text)[:140]}}, ensure_ascii=False), flush=True)

INPUTS = ('direction.json', 'images.json', 'assets.json', 'inventory.json', 'brief.json', 'hero.mp4')
ENGINE = ('lib/render/render_bp.py', 'lib/templates/recipes.py', 'lib/visual_quality.py', 'lib/visual_semantics.py',
          'lib/colour/palette.py', 'lib/colour_policy.py', 'lib/motion/moves.js', 'lib/motion/swarm.js')
def digest(path):
    if not os.path.isfile(path): return None
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''): h.update(chunk)
    return h.hexdigest()
def fingerprints(slug_dir, bp):
    return {'inputs': {name: digest(os.path.join(slug_dir, name)) for name in INPUTS},
            'engine': {name: digest(os.path.join(ROOT, name)) for name in (*ENGINE, f'lib/blueprints/{bp}.bp.json')}}
def render(slug_dir, bp, out):
    before = fingerprints(slug_dir, bp)
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'lib/render/render_bp.py'), slug_dir, bp, out], capture_output=True, text=True, timeout=120)
    if r.returncode: raise RuntimeError('render: ' + r.stderr[-400:])
    if before != fingerprints(slug_dir, bp): raise RuntimeError('render inputs changed during render')
    return {'fingerprints': before, 'html': digest(out)}

OWNER = {'seo-text': 'ux', 'seo-h1': 'copy', 'seo-links': 'ux', 'seo-meta': 'ui', 'h1': 'copy', 'h2': 'copy', 'one-cta': 'ux', 'actionable-cta': 'ux', 'page-length': 'ux', 'sections': 'ux', 'upscaled': 'visual', 'duplicate': 'visual', 'first-screen': 'visual', 'empty': 'ui', 'overflow': 'ui', 'sticky': 'ui', 'pinned': 'ui', 'contrast': 'ui'}
def contract(slug_dir, html):
    """THE CONTRACT: mechanical promises, graded on the render. Returns {score, failed:[{id, detail, weight}]}."""
    report = os.path.join(slug_dir, 'contract.json')
    if os.path.exists(report): os.remove(report)
    r = subprocess.run(['node', os.path.join(ROOT, 'lib/qa/contract.mjs'), html, '--dir', slug_dir], capture_output=True, text=True, timeout=240)
    if r.returncode:
        if os.path.exists(report): os.remove(report)
        raise RuntimeError('contract failed: ' + (r.stderr or r.stdout)[-300:])
    try:
        with open(report) as f: result = json.load(f)
        if not isinstance(result, dict) or not isinstance(result.get('score'), (int, float)) or not isinstance(result.get('failed'), list):
            raise ValueError('missing score or failed checks')
        return result
    except (OSError, ValueError) as e:
        if os.path.exists(report): os.remove(report)
        raise RuntimeError('contract produced an invalid report: ' + str(e)) from e
def owner_of(fid): return next((v for k, v in OWNER.items() if k in fid), 'ui')

def route_fixes(fixes, direction):
    """Send layout feedback to both its UI owner and the structural designer.

    The UI tool cannot select a section move; Concept can, but only for
    existing sections. Contract-wide and hero/form notes remain with UI.
    """
    notes = {'copy': [], 'ui': [], 'visual': [], 'ux': [], 'concept': []}
    eligible = {b.get('id') for b in direction.get('beats', []) if b.get('type') not in ('form',)}
    for f in fixes:
        owner = f.get('agent') or {'shorten': 'copy', 'hero_h1': 'copy', 'swap_image': 'visual', 'hero_image': 'visual', 'band': 'ui', 'layout': 'ui', 'drop_beat': 'ux', 'reorder': 'ux', 'concept': 'concept', 'note': 'ui'}.get(f.get('op'), 'ui')
        note = f"[{f.get('op')}] beat={f.get('beat', '')} {f.get('field', '')} {f.get('value', '') or f.get('image', '') or ''} — {f.get('reason', '')}"
        notes.setdefault(owner, []).append(note)
        if owner == 'ui' and f.get('op') == 'layout' and f.get('beat') in eligible:
            notes['concept'].append(note)
    return notes

# Promises whose failure means the page is broken for a visitor, not merely off-style.
HARD = ('no-overflow', 'no-empty-screens', 'contrast', 'actionable-cta', 'seo-text-kept', 'seo-links-kept')

TASTE_NOISE = 3    # one reading of the critic moves about four points either way: a smaller difference between two rounds is not one
MEASURE_BY = 730   # seconds into the loop after which the page is no longer measured: the server stops the loop at 900
DECIDE = 'blend' if os.environ.get('SWARM_DECIDE') == 'blend' else 'gates'


def bar(name, default):
    try: return int(os.environ.get(name) or default)
    except ValueError: return default


def standing(taste, contract_score, broken):
    """Where a page stands on each track: its taste, its contract score, the hard promises it breaks, and whether it
    clears the technical bar (GATE_TECHNICAL, default 90, and no hard failure)."""
    hard = sorted({str(f.get('id')) for f in broken or [] if isinstance(f, dict) and any(h in str(f.get('id')) for h in HARD)})
    number = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool)
    return {'taste': taste if number(taste) else -1, 'contract': contract_score if number(contract_score) else -1, 'hard': hard,
            'technical': bool(number(contract_score) and contract_score >= bar('GATE_TECHNICAL', 90) and not hard)}


def beats(new, old):
    """Does the page standing at `new` come before the one at `old`? The two tracks are never added up: fewer broken hard
    promises first; then clearing the technical bar; then the higher taste, when the difference is more than one reading's
    noise; within that noise the higher contract; then taste again."""
    if len(new['hard']) != len(old['hard']): return len(new['hard']) < len(old['hard'])
    if new['technical'] != old['technical']: return new['technical']
    if abs(new['taste'] - old['taste']) > TASTE_NOISE: return new['taste'] > old['taste']
    if new['contract'] != old['contract']: return new['contract'] > old['contract']
    return new['taste'] > old['taste']


_MEASURED = {}   # page digest → what a browser measured on it, so the page that ships is not measured twice


def measured(slug_dir, page, folder=None):
    """What a browser measures on `page` and what the Standard says of it (lib/qa/measure.py), or None. Best effort: a
    page that cannot be measured does not stop a job. Off under tests (LIVETEST) unless SWARM_MEASURE=1; SWARM_MEASURE=0
    switches it off everywhere."""
    wanted = os.environ.get('SWARM_MEASURE', '' if os.environ.get('LIVETEST') else '1')
    if wanted != '1': return None
    try:
        key = digest(page)
        if key not in _MEASURED:
            where = folder or slug_dir; os.makedirs(where, exist_ok=True); _MEASURED[key] = MEASURE.measure(page, where)
        return _MEASURED[key]
    except Exception: return None


def scorecard(log, best_round, report=None):
    """Taste and contract of the round that ships, side by side, and whether each clears its own bar: GATE_TECHNICAL
    (default 90, and no hard failure) and GATE_CREATIVE (default 70). The two are never added up, and since the loop
    decides on the same two tracks (`decided_by`), what is reported here is what was enforced. With `report` — what a
    browser measured on the page — the card also says how many findings the Standard has and which measured checks fail."""
    rec = next((r for r in log.get('rounds', []) if r.get('k') == best_round), None)
    if not rec: return None
    technical_min, creative_min = bar('GATE_TECHNICAL', 90), bar('GATE_CREATIVE', 70)
    contract, taste = rec.get('contract'), rec.get('taste')
    hard = [str(f.get('id')) for f in rec.get('broken') or [] if isinstance(f, dict) and any(h in str(f.get('id')) for h in HARD)]
    number = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool)
    return {'round': best_round, 'taste': taste, 'contract': contract, 'blended': rec.get('score'), 'axes': rec.get('axes'),
            'technical': {'pass': bool(number(contract) and contract >= technical_min and not hard), 'min': technical_min, 'hard_failures': hard},
            'creative': {'pass': bool(number(taste) and taste >= creative_min), 'min': creative_min, 'level': STANDARD.level_of(taste),
                         **({'levels': rec['levels'], 'page_level': rec.get('page_level')} if isinstance(rec.get('levels'), dict) and rec['levels'] else {})},
            'decided_by': DECIDE, 'enforced': DECIDE == 'gates',
            **({'measured': {'findings': len(report['findings']), 'by_area': {a: sum(1 for f in report['findings'] if f['area'] == a) for a in sorted({f['area'] for f in report['findings']})},
                             'ids': [f"{f['id']}@{f['view']}" for f in report['findings']], 'checks_failed': [c['id'] for c in report['technical'] if not c['pass']]}} if isinstance(report, dict) and isinstance(report.get('findings'), list) else {})}

def safe(name, fn, *a):
    t = time.time()
    try: n = fn(*a); ev(name, f'{n if isinstance(n, int) else "ok"} change(s) · {round(time.time() - t)}s'); return n
    except Exception as e: ev(name, 'skipped: ' + str(e)[:90]); traceback.print_exc(file=sys.stderr); return 0

def checked_render(slug_dir, bp, out):
    safe('Visual check', A.review_ledger_leads, slug_dir)
    safe('Visual', A.review_software_hero, slug_dir)
    # The structural selector can still make a weaker page. Keep it opt-in
    # until its candidate can be compared with the original for visual quality.
    if os.environ.get('SWARM_VERIFIED_PATTERNS') == '1':
        selection = Patterns.apply_verified_patterns(slug_dir, bp, fingerprints)
        ev('Patterns', f"{len(selection['choices'])} verified section move(s) · {selection['reason']}")
    return render(slug_dir, bp, out)

STUDIO_BY = 620   # seconds into the loop after which the studio page is no longer composed: the server stops the loop at 900


def studio_wanted(slug_dir):
    """The page is composed from authored scenes (lib/studio) unless the job or the deployment says no: brief.json
    "studio": false, or SWARM_STUDIO=0. Under tests nothing is composed unless asked."""
    asked = (A.J(slug_dir, 'brief.json') or {}).get('studio'); env = os.environ.get('SWARM_STUDIO')
    if asked is True or asked is False: return asked
    if env in ('0', '1'): return env == '1'
    return not os.environ.get('LIVETEST')


def studio_page(slug_dir, out):
    """Compose three variants of the page from the studio's scenes and stand the first clean one in place of the page the
    round made. Returns what happened: {'kept': tag | None, 'variants': […], 'usd', 'seconds', 'why'}. The page at `out`
    is replaced only by a variant that passed every check (numbers, links, pictures, layout at five widths); the other
    clean variants stay in <job>/studio/ for the server to publish beside it. Anything else leaves `out` untouched."""
    for sub in ('studio', 'devices'):
        if os.path.join(ROOT, 'lib', sub) not in sys.path: sys.path.insert(0, os.path.join(ROOT, 'lib', sub))
    import studio as STUDIO, scenes as SCENES
    folder = os.path.join(slug_dir, 'studio'); report = STUDIO.build(slug_dir, folder, 3)
    clean = [v for v in report['variants'] if v.get('clean')]
    info = {'kept': None, 'variants': [{k: v.get(k) for k in ('tag', 'type', 'scheme', 'scenes', 'clean', 'story')} for v in report['variants']], 'usd': report.get('usd'), 'seconds': report.get('seconds')}
    if not clean: info['why'] = 'no variant passed its checks'; return info
    inventory = A.J(slug_dir, 'inventory.json') or {}; brief = A.J(slug_dir, 'brief.json') or {}
    import seo as SEO
    for v in clean:   # every clean variant carries what the client's search standing needs, when the job asked for that
        path = os.path.join(folder, f'page-{v["tag"]}.html')
        with open(path, encoding='utf-8') as f: page = f.read()
        if SEO.mode(brief) == 'seo-safe': page = SCENES.keep(page, inventory)
        with open(path, 'w', encoding='utf-8') as f: f.write(page)
    first = clean[0]
    shutil.copyfile(os.path.join(folder, f'page-{first["tag"]}.html'), out + '.studio'); os.replace(out + '.studio', out)
    info['kept'] = first['tag']; info['others'] = [v['tag'] for v in clean[1:]]
    return info


def compose_wanted(slug_dir):
    """The page that won the rounds is recomposed (lib/compose) unless the job or the deployment says no: brief.json
    "compose": false, or SWARM_COMPOSE=0. Since 2026-11-10 this is the ordinary path — the form a visitor fills in has no
    such switch, so an opt-in was a path nobody reached. A job's own word comes first, then the deployment's. Under tests
    (LIVETEST) nothing is recomposed unless asked, so no test calls a model by default."""
    brief = A.J(slug_dir, 'brief.json') or {}; asked = brief.get('compose'); env = os.environ.get('SWARM_COMPOSE')
    if asked is True or asked is False: return asked
    if env in ('0', '1'): return env == '1'
    return not os.environ.get('LIVETEST')


def keep_plain(doc, record):
    """A page plan names the sections that stay quiet so the others can be seen. A composer after the first screen may
    still propose one of them; it is taken out of the composition before anything is drawn, and the record says which."""
    plain = set(((record.get('plan') or {}).get('plain')) or [])
    if not plain or not isinstance(doc, dict): return doc, []
    dropped = []
    for key in ('lists', 'pictures', 'words'):
        if isinstance(doc.get(key), list):
            kept = [e for e in doc[key] if not (isinstance(e, dict) and e.get('section') in plain)]
            dropped += [e.get('section') for e in doc[key] if isinstance(e, dict) and e.get('section') in plain]; doc[key] = kept
    if isinstance(doc.get('galleries'), list):
        kept = [g for g in doc['galleries'] if not (isinstance(g, dict) and plain & set(g.get('sections') or []))]
        dropped += [g['sections'][0] for g in doc['galleries'] if isinstance(g, dict) and plain & set(g.get('sections') or [])]; doc['galleries'] = kept
    if dropped: record.setdefault('kept_plain', []).extend(d for d in dropped if d not in record.get('kept_plain', []))
    left = any(doc.get(k) for k in ('lists', 'pictures', 'words', 'galleries'))
    if 'galleries' in doc and not doc['galleries']: doc.pop('galleries')
    return (doc if left else None), dropped


def layout_breaks(page_path):
    """What lib/qa/layout.mjs measures on the page: [{'kind', 'section', 'text', 'detail', 'widths'}], or None when it could not be measured."""
    try:
        r = subprocess.run(['node', os.path.join(ROOT, 'lib', 'qa', 'layout.mjs'), page_path], capture_output=True, text=True, timeout=150)
        return json.loads(r.stdout.strip().splitlines()[-1])['breaks']
    except Exception: return None


RANGES = {390: '(max-width:600px)', 768: '(min-width:601px) and (max-width:900px)', 1100: '(min-width:901px) and (max-width:1279px)',
          1440: '(min-width:1280px) and (max-width:1679px)', 1920: '(min-width:1680px)'}
FITTABLE = ('stacked-words', 'split-word', 'lone-mark', 'clipped')   # what a smaller size can cure
FIT_FLOOR = {'h1': 30, 'h2': 24, 'h3': 18}


def fit_headings(out, breaks, replace, rounds=3):
    """A heading that does not fit the room it was given is set smaller until it does — in that section, at the widths
    where it broke, never under a floor. The cure of last resort for any page, composed or not: the form that left the
    heading too little room is still wrong, but what leaves is whole. Returns (the rules written, what is still broken)."""
    import re
    sizes = {}   # (section, tag, width) → px now
    left = breaks
    for _ in range(rounds):
        todo = [b for b in left or [] if b.get('kind') in FITTABLE and b.get('section') and b.get('tag') in FIT_FLOOR]
        moved = False
        for b in todo:
            for width in b.get('widths') or []:
                key = (b['section'], b['tag'], width); now = sizes.get(key) or (b.get('sizes') or {}).get(str(width)) or (b.get('sizes') or {}).get(width)
                if not isinstance(now, (int, float)) or width not in RANGES: continue
                smaller = max(FIT_FLOOR[b['tag']], round(now * 0.82, 1))
                if smaller < now: sizes[key] = smaller; moved = True
        if not moved: break
        css = ''.join(f'@media{RANGES[w]}{{#{sid} {tag},#{sid} {tag}.{tag}{{font-size:{px}px!important}}}}' for (sid, tag, w), px in sorted(sizes.items()) if re.fullmatch(r'[A-Za-z][\w-]*', sid))
        with open(out, encoding='utf-8') as f: page = f.read()
        page = re.sub(r'<style id="fit-css">.*?</style>', '', page, flags=re.S)
        head = page.find('</head>')
        if head < 0: break
        replace(page[:head] + f'<style id="fit-css">{css}</style>' + page[head:])
        left = layout_breaks(out)
        if left is None: break
    return [{'section': sid, 'tag': tag, 'width': w, 'px': px} for (sid, tag, w), px in sorted(sizes.items())], left


def guard_layout(out, replace):
    """The last thing done to any page that ships: measured at five widths, headings that do not fit set smaller, and
    what is still broken written down. {'breaks': found, 'fitted': rules, 'left': still broken} — None when unmeasured."""
    found = layout_breaks(out)
    if found is None: return None
    fitted, left = fit_headings(out, found, replace) if found else ([], found)
    return {'breaks': found, 'fitted': fitted, 'left': left}


def mend_layout(out, before, replace):
    """No broken typesetting leaves the loop. The composed page is measured at five widths; a section below the first
    screen in which something is broken — a heading stacked a word to a line, a word split, a paragraph in a sliver of a
    column, text cut off or lying over other text — is put back as it stood before it was composed, and the page is
    measured again. `before` is the page as it stood after the first screen was drawn. Returns the record:
    {'breaks': found first, 'reverted': [ids], 'left': what is still broken after}; 'left' in the first screen or the
    frame of the page is for the caller to judge."""
    import sections as SECTIONS
    found = layout_breaks(out)
    record = {'breaks': found, 'reverted': [], 'left': found}
    if not found: return record
    with open(out, encoding='utf-8') as f: page = f.read()
    was = {s['id']: before[s['span'][0]:s['span'][1]] for s in SECTIONS.sections(before) if s.get('id')}
    for sec in sorted((s for s in SECTIONS.sections(page) if s.get('id') in {b['section'] for b in found} and s['id'] in was), key=lambda s: -s['span'][0]):
        if page[sec['span'][0]:sec['span'][1]] == was[sec['id']]: continue   # it was broken before anything was composed: not this pass's to mend
        page = page[:sec['span'][0]] + was[sec['id']] + page[sec['span'][1]:]; record['reverted'].append(sec['id'])
    if record['reverted']:
        replace(page); record['left'] = layout_breaks(out)
    if record['left']:   # what putting sections back did not cure: a heading that does not fit is set smaller
        record['fitted'], record['left'] = fit_headings(out, record['left'], replace)
        with open(out, encoding='utf-8') as f: page = f.read()
    now = {s['id']: page[s['span'][0]:s['span'][1]] for s in SECTIONS.sections(page) if s.get('id')}
    # what is still broken and is the composition's doing: the first screen it drew, or a section it changed that could not be put back
    record['own'] = [b for b in record['left'] or [] if b.get('section') == 'top' or (b.get('section') in now and b['section'] in was and now[b['section']] != was[b['section']])]
    return record


def compose_first_screen(slug_dir, out, deadline=None):
    """Recompose the page at `out` (lib/compose) — its first screen, then the lists below it, then the sections that show a
    picture, then the sections that are words only, each a document that is validated, measured on its own render and refused whole if it breaks anything — and
    write composition.json. The page file is replaced only by what passed; a part that did not pass leaves that part of
    the page as it was. The pictures are composed only while there is time left in the job (`deadline`, a clock time).
    Returns the record: {'drawn', 'attempts', 'concept', 'face', 'measured', 'wishes', 'log', 'ir', 'lists', 'pictures', 'words'};
    'drawn' is true when any part was drawn."""
    if os.path.join(ROOT, 'lib', 'compose') not in sys.path: sys.path.insert(0, os.path.join(ROOT, 'lib', 'compose'))
    import compose as COMPOSE, render_ir as IR
    def replace(page):
        page = RULES.budget(page)   # the page's budget of rules, counted again with the recomposed sections in it
        with open(out + '.composed', 'w', encoding='utf-8') as f: f.write(page)
        os.replace(out + '.composed', out)
    with open(out, encoding='utf-8') as f: page = f.read()
    images = A.J(slug_dir, 'images.json') or []
    result = COMPOSE.compose(page, images, job_dir=slug_dir, page_path=out, concepts=COMPOSE_CONCEPTS)
    ir = result.get('ir')
    record = {'drawn': False, 'attempts': result.get('attempts'), 'concept': (ir or {}).get('note'), 'face': ((ir or {}).get('hero') or {}).get('face'),
              'measured': result.get('measured'), 'wishes': result.get('wishes'), 'log': result.get('log'), 'ir': ir, 'lists': None, 'pictures': None, 'words': None,
              **{k: result[k] for k in ('concepts', 'chosen', 'verdict') if k in result}}
    if ir:
        composed, report = IR.transplant(page, ir, images)
        if report['drawn']: replace(composed); page = composed; record['drawn'] = True
    after_first_screen = page   # what each section below was before any composer touched it: where a broken one goes back to
    record['direction'] = result.get('direction') if record['drawn'] else None
    record['plan'] = result.get('plan') if record['drawn'] else None
    def directed():
        """One page, one direction: what the first screen's composer asked of the rest of the page, its typeface, and what
        the composers before this one already chose — so that each continues the page instead of starting again."""
        said = [record['direction']] if record.get('direction') else ([f'The first screen: {record["concept"]}'] if record['drawn'] and record.get('concept') else [])
        if record.get('face'): said.append(f'The page is set in the typeface "{record["face"].get("id")}".')
        for part in ('lists', 'pictures', 'words'):
            done = record.get(part) or {}
            if done.get('drawn') and done.get('forms'): said.append(f'Already composed — {part}: ' + ', '.join(f'"{k}" as {v}' for k, v in done['forms'].items()) + (f'. Their idea: {done["concept"]}' if done.get('concept') else ''))
        return ' '.join(said) or None
    try:   # the lists are composed on the page as it now stands, so that they are seen under the first screen they follow
        import compose_lists as COMPOSE_LISTS, lists as LISTS
        chosen = COMPOSE_LISTS.compose(page, out, direction=directed()); doc = chosen.get('doc'); doc, quiet = keep_plain(doc, record)
        record['lists'] = {'drawn': False, 'attempts': chosen.get('attempts'), 'concept': (doc or {}).get('note'), 'forms': {l['section']: l['form'] for l in (doc or {}).get('lists', [])},
                           'measured': chosen.get('measured'), 'log': chosen.get('log'), 'doc': doc}
        if doc:
            composed, report = LISTS.transplant(page, doc)
            if report['drawn']: replace(composed); record['lists']['drawn'] = True; record['drawn'] = True
    except Exception as e: record['lists'] = {'drawn': False, 'error': str(e)[:160]}
    if deadline is not None and time.time() > deadline: record['pictures'] = {'drawn': False, 'error': 'no time left in this job'}
    else:
        try:   # what each picture below the first screen does, on the page as it now stands
            import compose_pictures as COMPOSE_PICTURES, pictures as PICTURES
            with open(out, encoding='utf-8') as f: page = f.read()
            chosen = COMPOSE_PICTURES.compose(page, out, images=images, direction=directed()); doc = chosen.get('doc'); doc, quiet = keep_plain(doc, record)
            record['pictures'] = {'drawn': False, 'attempts': chosen.get('attempts'), 'concept': (doc or {}).get('note'), 'forms': {**{p['section']: p['form'] for p in (doc or {}).get('pictures', [])}, **{g['sections'][0]: 'gallery' for g in (doc or {}).get('galleries', [])}},
                                  'measured': chosen.get('measured'), 'log': chosen.get('log'), 'doc': doc}
            if doc:
                composed, report = PICTURES.transplant(page, doc, images)
                if report['drawn']: replace(composed); record['pictures']['drawn'] = True; record['drawn'] = True
        except Exception as e: record['pictures'] = {'drawn': False, 'error': str(e)[:160]}
    if deadline is not None and time.time() > deadline: record['words'] = {'drawn': False, 'error': 'no time left in this job'}
    else:
        try:   # the sections that are words only — price lists, menus, a paragraph under its heading — on the page as it now stands
            import compose_words as COMPOSE_WORDS, words as WORDS
            with open(out, encoding='utf-8') as f: page = f.read()
            chosen = COMPOSE_WORDS.compose(page, out, direction=directed()); doc = chosen.get('doc'); doc, quiet = keep_plain(doc, record)
            record['words'] = {'drawn': False, 'attempts': chosen.get('attempts'), 'concept': (doc or {}).get('note'), 'forms': {w['section']: w['form'] for w in (doc or {}).get('words', [])},
                               'measured': chosen.get('measured'), 'log': chosen.get('log'), 'doc': doc}
            if doc:
                composed, report = WORDS.transplant(page, doc)
                if report['drawn']: replace(composed); record['words']['drawn'] = True; record['drawn'] = True
        except Exception as e: record['words'] = {'drawn': False, 'error': str(e)[:160]}
    if record.get('drawn') and record.get('plan') and os.environ.get('SWARM_DEVICE', '1') != '0':
        try:   # what the first screen did to its headline, repeated on the sections the plan names — by rule, since no form can say it
            import device as DEVICE
            with open(out, encoding='utf-8') as f: page = f.read()
            carried, report = DEVICE.carry(page, record['plan'], record.get('ir'))
            record['device'] = report
            if report['drawn']: replace(carried)
        except Exception as e: record['device'] = {'drawn': False, 'error': str(e)[:160]}
    wanted = os.environ.get('SWARM_LAYOUT', '0' if os.environ.get('LIVETEST') else '1') != '0'
    if record.get('drawn') and wanted:
        try:
            record['layout'] = mend_layout(out, after_first_screen, replace)
            for sid in (record['layout'] or {}).get('reverted') or []:   # the record says what the page is: a section put back carries no device
                if isinstance(record.get('device'), dict):
                    record['device'].get('sections', {}).pop(sid, None)
                    if record['device'].get('event') == sid: record['device']['event'] = None
                for part in ('lists', 'pictures', 'words'):
                    if isinstance(record.get(part), dict) and isinstance(record[part].get('forms'), dict): record[part]['forms'].pop(sid, None)
        except Exception as e: record['layout'] = {'error': str(e)[:160]}
    with open(os.path.join(slug_dir, 'composition.json'), 'w', encoding='utf-8') as f: json.dump(record, f, indent=1, ensure_ascii=False)
    return record


def composed_candidate(slug_dir, out, best_score, best_broken, grade, deadline=None, reference=None, winner=None):
    """The composed page is one more candidate, held to the loop's own rule. `grade()` → (contract report, critic report)
    for the page at `out`. `reference()` → the page it would replace as the critic reads it now: {'taste', 'score'} (or
    the blended number alone). With `winner` — the round it would replace: taste, contract, broken — the decision is made
    on two tracks: the composed page stands when it breaks no hard promise the winner kept, does not lose the technical
    bar the winner cleared, and the critic reads it at least as high. Without it, or under SWARM_DECIDE=blend, the one
    blended number decides as before. Returns the decision; when 'kept' is false the caller puts the winner's files back."""
    record = compose_first_screen(slug_dir, out, deadline)
    decision = {'kept': False, 'drawn': record['drawn'], 'attempts': record.get('attempts'), 'concept': record.get('concept'), 'face': record.get('face'), 'before': best_score,
                'first_screen': bool(record.get('ir')), 'lists': (record.get('lists') or {}).get('forms') if (record.get('lists') or {}).get('drawn') else None,
                'pictures': (record.get('pictures') or {}).get('forms') if (record.get('pictures') or {}).get('drawn') else None,
                'words': (record.get('words') or {}).get('forms') if (record.get('words') or {}).get('drawn') else None}
    if not record['drawn']:
        decision['why'] = 'no composition passed validation and measurement'; return decision
    layout = record.get('layout') or {}
    if layout.get('reverted'): decision['layout_reverted'] = layout['reverted']
    if layout.get('own'):   # broken typesetting is not weighed against taste: the page does not go out
        decision['layout'] = layout['own']
        decision['why'] = 'its layout is broken: ' + '; '.join(f"{b['kind']} in \"{b.get('section')}\" at {b.get('widths')} ({b.get('detail')})" for b in layout['own'][:3]); return decision
    con, rep = grade()
    taste = rep.get('score') if isinstance(rep, dict) and isinstance(rep.get('score'), (int, float)) else None
    if taste is None or not isinstance(con.get('score'), (int, float)):
        decision['why'] = 'the composed page could not be graded'; return decision
    score = round(0.55 * taste + 0.45 * con['score']); failed = con.get('failed', [])
    against = reference() if reference else None   # the page it would replace, read again now by the same critic: like against like
    rival_taste = against.get('taste') if isinstance(against, dict) else None
    if isinstance(against, dict): against = against.get('score')
    if isinstance(against, (int, float)): decision['reference'] = against; best_score = against
    hard = lambda ids: {i for i in ids if any(i.endswith(h) or i == h for h in HARD)}
    newly = sorted(hard(f['id'] for f in failed) - hard(f['id'] for f in (best_broken or [])))
    decision.update(score=score, taste=taste, contract=con['score'], broken=failed, critic=rep)
    two_tracks = DECIDE == 'gates' and isinstance(winner, dict) and isinstance(winner.get('taste'), (int, float))
    if two_tracks:
        if not isinstance(rival_taste, (int, float)): rival_taste = winner['taste']   # the winner could not be read again: what its round recorded
        mine, rival = standing(taste, con['score'], failed), standing(rival_taste, winner.get('contract'), winner.get('broken'))
        decision.update(decided_by='gates', reference_taste=rival_taste)
    if newly: decision['why'] = 'it breaks ' + ', '.join(newly)
    elif two_tracks and rival['technical'] and not mine['technical']: decision['why'] = f"its contract is {con['score']}, under the technical bar the page it would replace clears"
    elif two_tracks and taste < rival_taste: decision['why'] = f'the critic reads it at {taste}, the page it would replace at {rival_taste}'
    elif not two_tracks and score < best_score: decision['why'] = f'it scores {score}, the page it would replace {best_score}'
    else: decision['kept'] = True
    return decision


def recompose(slug_dir, out, log, best_score, best_round, best_manifest, best_files, snapshot_dir, deadline=None):
    """Offer the winning page a composed first screen and keep whichever page scores higher. Returns the (score, round,
    manifest) of the page that stands. A composed page that is kept becomes one more round in the log, with the critic's
    and the contract's reports of that page; a refused one leaves every file of the winner exactly as it was."""
    winner = next((r for r in log['rounds'] if r.get('k') == best_round), {})
    kept_page = out + '.ref.html'; reread = ThreadPoolExecutor(1)
    try:
        # One reading of a page moves about four points either way, and the winner's score is one reading from its round.
        # So the winner is read again — twice, by the critic as it is now — while the page is composed, and the composed
        # page is read twice too: the decision compares two averages of the same kind.
        # Both pages are measured in a browser before they are read, and the critic is handed what was measured: it does
        # not estimate what a browser has counted (the Standard, §5.3).
        shutil.copyfile(out, kept_page)
        def read_again():
            found = measured(slug_dir, kept_page, os.path.join(slug_dir, 'measure-ref'))
            return C.critique_twice(slug_dir, kept_page, A.MODEL, 'critic-shots-ref', **({'measured': found['findings']} if found else {}))
        again = reread.submit(read_again)
        def reference():
            try: rep = again.result(timeout=240)
            except Exception: return None
            taste = rep.get('score') if isinstance(rep, dict) else None
            if not isinstance(taste, (int, float)) or taste < 0 or not isinstance(winner.get('contract'), (int, float)): return None
            return {'taste': taste, 'score': round(0.55 * taste + 0.45 * winner['contract'])}
        def grade():
            in_time = deadline is None or time.time() < deadline + 30
            with ThreadPoolExecutor(2) as ex:
                fcon = ex.submit(contract, slug_dir, out); fmeasured = ex.submit(measured, slug_dir, out) if in_time else None
                con = fcon.result(); found = fmeasured.result() if fmeasured else None
            return con, C.critique_twice(slug_dir, out, A.MODEL, **({'measured': found['findings']} if found else {}))
        decision = composed_candidate(slug_dir, out, best_score, winner.get('broken'), grade, deadline, reference, winner)
        decision['before'] = best_score   # what the round recorded; `reference` is the same page as the critic reads it now
    except Exception as e:
        decision = {'kept': False, 'drawn': False, 'before': best_score, 'why': 'failed: ' + str(e)[:120]}
    finally:
        reread.shutdown(wait=False)
        for leftover in (kept_page,):
            if os.path.exists(leftover): os.remove(leftover)
        for folder in ('critic-shots-ref', 'measure-ref'): shutil.rmtree(os.path.join(slug_dir, folder), ignore_errors=True)
    rep = decision.pop('critic', None); cfail = decision.pop('broken', None)
    if isinstance(rep, dict):   # what the critic said of the composed page is kept whether or not the page is: a refusal is where there is most to learn
        decision['verdict'] = str(rep.get('verdict') or '')[:1500]; decision['axes'] = rep.get('axes') if isinstance(rep.get('axes'), dict) else None
        if isinstance(rep.get('levels'), dict): decision['levels'] = rep['levels']; decision['page_level'] = rep.get('page_level')
        if isinstance(rep.get('findings'), list): decision['findings'] = rep['findings']
    if decision['kept']:
        k = max(r['k'] for r in log['rounds']) + 1
        fixes = [f for f in (rep.get('fixes') if isinstance(rep.get('fixes'), list) else []) if isinstance(f, dict)]
        log['rounds'].append({'k': k, 'composed': True, 'score': decision['score'], 'taste': decision['taste'], 'contract': decision['contract'], 'axes': rep.get('axes') if isinstance(rep.get('axes'), dict) else None, 'broken': cfail, 'fixes': fixes, 'verdict': rep.get('verdict'),
                              **{key: rep[key] for key in ('levels', 'page_level', 'findings') if rep.get(key) is not None}})
        with open(os.path.join(slug_dir, 'critic.json'), 'w') as f:
            json.dump({**rep, 'score': decision['score'], 'taste': decision['taste'], 'contract': decision['contract'], 'broken': cfail, 'round': k, 'best': decision['score'], 'composed': True}, f, indent=1, ensure_ascii=False)
        best_score, best_round = decision['score'], k; best_manifest = dict(best_manifest, html=digest(out))
        if decision.get('first_screen'): ev('Concept', 'first screen recomposed: ' + str(decision.get('concept') or '')[:110])
        if decision.get('lists'): ev('Concept', 'lists recomposed: ' + ', '.join(f'{k} as {v}' for k, v in decision['lists'].items())[:110])
        if decision.get('words'): ev('Concept', 'sections of words recomposed: ' + ', '.join(f'{k} as {v}' for k, v in decision['words'].items())[:100])
        if decision.get('pictures'): ev('Visual', 'pictures recomposed: ' + ', '.join(f'{k} as {v}' for k, v in decision['pictures'].items())[:110])
        ev('Critic', f"composed page kept: {decision['score']}/100 (was {decision['before']}" + (f", read again {decision['reference']}" if decision.get('reference') is not None else '') + f") · taste {decision['taste']} · contract {decision['contract']}")
    else:   # the winner's page, documents, contract, critic and screenshots go back exactly as they were
        for path, data in best_files.items():
            with open(path, 'wb') as f: f.write(data)
        restore_shots(slug_dir, snapshot_dir)
        if best_manifest['html'] != digest(out): raise RuntimeError('the winning page could not be restored after a refused composition')
        ev('Concept', 'page left as the rounds made it: ' + str(decision.get('why') or '')[:100])
    log['composition'] = decision
    try:
        record = A.J(slug_dir, 'composition.json') or {}
        record.update({key: decision.get(key) for key in ('kept', 'why', 'before', 'reference', 'reference_taste', 'decided_by', 'score', 'taste', 'contract', 'first_screen', 'verdict', 'axes', 'levels', 'page_level', 'findings')})
        with open(os.path.join(slug_dir, 'composition.json'), 'w', encoding='utf-8') as f: json.dump(record, f, indent=1, ensure_ascii=False)
    except Exception: pass
    return best_score, best_round, best_manifest


def snapshot_shots(slug_dir, snapshot_dir):
    """Keep only the current best's screenshots on disk, never in memory."""
    saved = os.path.join(snapshot_dir, 'critic-shots')
    if os.path.isdir(saved): shutil.rmtree(saved)
    os.makedirs(saved)
    source = os.path.join(slug_dir, 'critic-shots')
    if os.path.isdir(source):
        for name in os.listdir(source):
            src = os.path.join(source, name)
            if name.lower().endswith(('.png', '.jpg')) and os.path.isfile(src) and not os.path.islink(src):
                shutil.copy2(src, os.path.join(saved, name))

def restore_shots(slug_dir, snapshot_dir):
    saved = os.path.join(snapshot_dir, 'critic-shots')
    if not os.path.isdir(saved): raise RuntimeError('best-round screenshot snapshot is missing')
    target = os.path.join(slug_dir, 'critic-shots')
    if not os.path.isdir(target) and not os.listdir(saved): return
    os.makedirs(target, exist_ok=True)
    for name in os.listdir(target):
        dest = os.path.join(target, name)
        if name.lower().endswith(('.png', '.jpg')) and (os.path.isfile(dest) or os.path.islink(dest)):
            os.remove(dest)
    for name in os.listdir(saved): shutil.copy2(os.path.join(saved, name), os.path.join(target, name))

def main():
    with tempfile.TemporaryDirectory(prefix='swarm-best-') as snapshot_dir:
        return _main(snapshot_dir)

COMPOSE_BY = 540   # seconds into the loop after which the page is no longer recomposed: the server stops the loop at 900
COMPOSE_PICTURES_BY = 700   # and after which the pictures below the first screen are left as the template drew them
COMPOSE_CONCEPTS = 1 if os.environ.get('SWARM_COMPOSE_CONCEPTS') == '1' else 3   # first screens drawn before one is chosen

def _main(snapshot_dir):
    started = time.time()
    slug_dir, bp = sys.argv[1], sys.argv[2]; args = sys.argv[3:]
    out = args[args.index('--out') + 1] if '--out' in args else os.path.join(slug_dir, f'bp-{bp}.html')
    rounds = int(args[args.index('--rounds') + 1]) if '--rounds' in args else 3
    studio = studio_wanted(slug_dir)
    if studio: rounds = 1   # the round's page is the fallback; the page that ships is composed after it
    target = int(args[args.index('--target') + 1]) if '--target' in args else 80
    if rounds < 1: raise ValueError('at least one review round is required')
    log = {'rounds': [], 'blueprint': bp}
    if not os.path.exists(os.path.join(slug_dir, 'factsheet.json')): safe('Reader', A.reader, slug_dir)
    fs_ = A.J(slug_dir, 'factsheet.json') or {}
    if fs_: ev('Reader', f"{fs_.get('what', '')[:90]}"); ev('Reader', f"{len(fs_.get('facts', []))} facts · {len(fs_.get('offers', []))} offers · {len(fs_.get('quotes', []))} quotes")
    # round 0: the specialists shape the director's document
    safe('Concept', A.concept, slug_dir, '', bp)
    # the mood (paper, ink, accent) is chosen once, here, so the Visual editor commissions in the same colours the renderer will use
    try:
        with A._document_lock:
            d0 = A.J(slug_dir, 'direction.json'); brief0 = A.J(slug_dir, 'brief.json') or {}; inv0 = A.J(slug_dir, 'inventory.json') or {}
            if d0 is not None and brief0.get('keepColours', True) is False and not isinstance(d0.get('mood'), dict):
                d0['mood'] = MOODS.choose(d0.get('kind') or 'service', inv0, d0.get('mode'), seed=brief0.get('url') or (d0.get('brand') or {}).get('name')); A.W(slug_dir, 'direction.json', d0)
                ev('Concept', f"mood: {d0['mood']['id']} · {d0['mood']['why']}")
    except Exception as e: ev('Concept', 'mood skipped: ' + str(e)[:80])
    relock(slug_dir)
    d = A.J(slug_dir, 'direction.json'); sw = d.get('swarm') or {}
    if sw.get('idea'): ev('Concept', 'idea: ' + sw['idea'])
    ev('Concept', 'moves: ' + ', '.join(f"{b['id']}→{(b.get('ui') or {}).get('move', 'auto')}" for b in d['beats']))
    # the four specialists read Concept's plan and each patch their own fields by beat id under the document lock:
    # they run at once (one model round-trip instead of four in a row)
    with ThreadPoolExecutor(max_workers=4) as ex:
        list(ex.map(lambda j: safe(*j), [('UX', A.ux, slug_dir), ('Visual', A.visual, slug_dir), ('Copy', A.copy, slug_dir), ('UI', A.ui, slug_dir, '', bp)]))
    d = A.J(slug_dir, 'direction.json')
    ev('UX', 'order: ' + ' → '.join(b['type'] for b in d['beats'])); ev('Copy', 'h1: ' + str(d['hero'].get('h1', '')).replace('<em>', '').replace('</em>', ''))
    vis = (d.get('swarm') or {}).get('visual') or {}
    for x in (vis.get('generated') or [])[:3]: ev('Visual', 'commissioned: ' + x)
    for x in (vis.get('gen_errors') or [])[:1]: ev('Visual', 'generation failed: ' + x)
    for x in (vis.get('need') or [])[:2]: ev('Visual', 'missing visual: ' + x)
    render_manifest = checked_render(slug_dir, bp, out); ev('Render', f'{bp} · round 0')
    best_score, best_key, best_round, best_files, best_bp, best_manifest = -1, None, None, None, None, None; best_stand = None
    for k in range(1, rounds + 1):
        t = time.time()
        # the contract (two viewports) and the critic's look (screenshots + model) are independent: grade both at once
        with ThreadPoolExecutor(2) as ex:
            fcon = ex.submit(contract, slug_dir, out); frep = ex.submit(C.critique, slug_dir, out, A.MODEL, (k < rounds))  # desktop-only, short waits until the final look
            con = fcon.result(); cfail = con.get('failed', [])
            ev('Contract', f"round {k}: {con.get('score')}/100 · {len(cfail)} broken promise(s)")
            for f in cfail[:4]: ev('Contract', f"✗ {f['id']}: {f['detail']}")
            try: rep = frep.result()
            except Exception as e:
                # a critic that fails in round 2 or 3 must not throw away a page that already passed round 1
                if best_key is not None: ev('Critic', 'skipped: ' + str(e)[:90] + ' — keeping the best round so far'); break
                raise RuntimeError('critic failed: ' + str(e)) from e
        if not isinstance(rep, dict): rep = {}
        taste = rep.get('score', -1) if isinstance(rep.get('score'), (int, float)) else -1
        if taste < 0:
            if best_key is not None: ev('Critic', 'invalid score — keeping the best round so far'); break
            raise RuntimeError('critic returned an invalid score')
        fixes = [f for f in (rep.get('fixes') if isinstance(rep.get('fixes'), list) else []) if isinstance(f, dict)]
        score = round(0.55 * taste + 0.45 * con['score']) if con.get('score', -1) >= 0 and taste >= 0 else taste
        ev('Critic', f'round {k}: taste {taste} · contract {con.get("score")} → {score}/100 · {len(fixes)} defects · {round(time.time() - t)}s'); ev('Critic', str(rep.get('verdict', ''))[:140])
        for f in cfail: fixes.append({'op': 'note', 'agent': owner_of(f['id']), 'beat': '', 'reason': f"CONTRACT BROKEN — {f['id']}: {f['detail']}"})
        log['rounds'].append({'k': k, 'score': score, 'taste': taste, 'contract': con.get('score'), 'axes': rep.get('axes') if isinstance(rep.get('axes'), dict) else None, 'broken': cfail, 'fixes': fixes, 'verdict': rep.get('verdict'),
                              **{key: rep[key] for key in ('levels', 'page_level', 'findings') if rep.get(key) is not None}})
        # Which round stands is decided on two tracks, never on their sum (`beats`); `score` stays the number a visitor is shown.
        rank = (score, not cfail, -len(fixes)); stand = standing(taste, con.get('score'), cfail)
        if best_key is None or (rank > best_key if DECIDE == 'blend' else beats(stand, best_stand)):
            best_score, best_key, best_round, best_bp, best_manifest = score, rank, k, bp, render_manifest; best_stand = stand
        json.dump({**rep, 'score': score, 'taste': taste, 'contract': con.get('score'), 'broken': cfail, 'round': k, 'best': best_score}, open(os.path.join(slug_dir, 'critic.json'), 'w'), indent=1, ensure_ascii=False)
        if best_round == k:
            paths = [out] + [os.path.join(slug_dir, name) for name in ('direction.json', 'images.json', 'contract.json', 'critic.json')]
            best_files = {path: open(path, 'rb').read() for path in paths if os.path.exists(path)}
            snapshot_shots(slug_dir, snapshot_dir)
            # progressive delivery: the best page so far goes out now; later rounds only replace it if they win
            try:
                draft = os.path.join(slug_dir, 'draft.html'); shutil.copyfile(out, draft)
                print(json.dumps({"draft": {"round": k, "score": score, "path": draft}}), flush=True)
            except Exception as e: ev('Render', 'draft not published: ' + str(e)[:80])
        if (score >= target and taste >= 70 and not cfail) or k == rounds: break  # good enough, taste not carried by the contract alone, nothing mechanically broken: stop spending
        # RESTART, not patch: a weak first round means the idea or the form is wrong — throw it away, keep the facts, start over once
        if k == 1 and score < 45 and not log.get('restarted'):
            log['restarted'] = True; alt = args[args.index('--alt') + 1] if '--alt' in args else ''
            why = f"RESTART: the first attempt scored {score}/100 with blueprint {bp} and idea '{(A.J(slug_dir, 'direction.json').get('swarm') or {}).get('idea', '')}'. The critic said: {str(rep.get('verdict', ''))[:300]}. Choose a DIFFERENT idea and different moves; do not repeat the failed ones."
            d0 = A.J(slug_dir, 'direction.json')
            if alt and alt != bp and os.path.exists(os.path.join(ROOT, 'lib/blueprints', alt + '.bp.json')): bp = alt; d0['blueprint'] = alt; A.W(slug_dir, 'direction.json', d0); ev('Concept', f'restart with blueprint {alt}')
            else: ev('Concept', 'restart with a new idea')
            for b_ in d0['beats']: (b_.get('ui') or {}).pop('move', None)
            A.W(slug_dir, 'direction.json', d0)
            safe('Concept', A.concept, slug_dir, why, bp)
            with ThreadPoolExecutor(max_workers=3) as ex:
                list(ex.map(lambda j: safe(*j), [('UX', A.ux, slug_dir, why), ('Visual', A.visual, slug_dir, why), ('UI', A.ui, slug_dir, why, bp)]))
            relock(slug_dir)
            d = A.J(slug_dir, 'direction.json'); sw = d.get('swarm') or {}
            if sw.get('idea'): ev('Concept', 'idea: ' + sw['idea'])
            render_manifest = checked_render(slug_dir, bp, out); ev('Render', f'{bp} · restart'); continue
        if len(log['rounds']) >= 2:
            previous = log['rounds'][-2]
            before = standing(previous.get('taste'), previous.get('contract'), previous.get('broken'))
            if (rank <= (previous['score'], not previous['broken'], -len(previous['fixes']))) if DECIDE == 'blend' else not beats(stand, before):
                ev('Critic', 'no gain this round — stopping'); break  # another round costs the same and the last one bought nothing
        # route: every defect goes to its owner with the critic's reason
        notes = route_fixes(fixes, A.J(slug_dir, 'direction.json') or {})
        applied = 0  # the critic only routes; owners change the document
        for owner, ns in notes.items():
            if ns: ev(owner.upper() if owner in ('ux', 'ui') else owner.capitalize(), f'{len(ns)} note(s) from the critic')
        # Concept owns the shared creative plan. Finish its repair before the
        # specialists read that plan; otherwise they can act on stale guidance.
        if notes.get('concept'):
            applied += safe('Concept', A.concept, slug_dir, '\n'.join(notes['concept']), bp)
        jobs = [(n, getattr(A, n), '\n'.join(notes[n])) for n in ('copy', 'ui', 'visual', 'ux') if notes.get(n)]
        with ThreadPoolExecutor(max_workers=4) as ex:
            res = list(ex.map(lambda j: (j[0], safe(j[0].upper() if j[0] in ('ux', 'ui') else j[0].capitalize(), j[1], slug_dir, j[2], *([bp] if j[0] == 'ui' else []))), jobs))
        if applied + sum(r for _, r in res) == 0: ev('Critic', 'nothing more the team can change'); break
        render_manifest = checked_render(slug_dir, bp, out); ev('Render', f'{bp} · round {k}')
    # Keep the selected render and the inputs and reports that describe it together.
    if best_files:
        for path, data in best_files.items():
            with open(path, 'wb') as f: f.write(data)
        restore_shots(slug_dir, snapshot_dir)
        if best_round != log['rounds'][-1]['k']: ev('Critic', f'kept round {best_round} with {best_score}/100')
    if isinstance(best_manifest, dict) and (best_manifest['fingerprints'] != fingerprints(slug_dir, best_bp) or best_manifest['html'] != digest(out)):
        raise RuntimeError('best snapshot changed after render')
    # Opt-in: an art director recomposes the first screen of the page that won. The composed page is one more candidate.
    if studio and isinstance(best_manifest, dict) and best_files and time.time() - started < STUDIO_BY:
        try:
            made = studio_page(slug_dir, out); log['studio'] = made
            if made.get('kept'):
                best_manifest = dict(best_manifest, html=digest(out))
                ev('Concept', f"studio page: variant {made['kept']} of {len(made['variants'])} — " + ', '.join(f"{v['tag']}: {v['type']}/{v['scheme']}" for v in made['variants'])[:120])
            else: ev('Concept', 'studio page not kept: ' + str(made.get('why'))[:100])
        except Exception as e:
            log['studio'] = {'kept': None, 'why': 'failed: ' + str(e)[:160]}; ev('Concept', 'studio page failed: ' + str(e)[:100])
            if isinstance(best_manifest, dict) and best_manifest['html'] != digest(out):   # never leave a half-written page behind
                for path, data in best_files.items():
                    with open(path, 'wb') as f: f.write(data)
    elif compose_wanted(slug_dir) and isinstance(best_manifest, dict) and best_files and time.time() - started < COMPOSE_BY:
        best_score, best_round, best_manifest = recompose(slug_dir, out, log, best_score, best_round, best_manifest, best_files, snapshot_dir, deadline=started + COMPOSE_PICTURES_BY)
    # Whatever page won — a template round or the composed one — is measured as typesetting before anything else reads it.
    if os.environ.get('SWARM_LAYOUT', '0' if os.environ.get('LIVETEST') else '1') != '0':
        def _put(page):
            with open(out + '.fit', 'w', encoding='utf-8') as f: f.write(page)
            os.replace(out + '.fit', out)
        try:
            guard = guard_layout(out, _put)
            if guard is not None:
                log['layout'] = guard
                if guard['fitted'] and isinstance(best_manifest, dict): best_manifest = dict(best_manifest, html=digest(out))   # the page that ships is the fitted one
                with open(os.path.join(slug_dir, 'layout.json'), 'w', encoding='utf-8') as f: json.dump(guard, f, indent=1, ensure_ascii=False)
                ev('Layout', (f"{len(guard['breaks'])} break(s) measured at five widths" if guard['breaks'] else 'no break at five widths') + (f" · {len(guard['fitted'])} heading size(s) fitted" if guard['fitted'] else '') + (f" · still broken: " + ', '.join(f"{b['kind']} in {b.get('section')}" for b in guard['left'][:3]) if guard['left'] else ''))
            else: ev('Layout', 'the page could not be measured')
        except Exception as e: ev('Layout', 'unavailable: ' + str(e)[:90])
    # Audit the selected render, after rolling back any weaker candidate.
    # A text match is not a semantic guarantee; unmatched sections require review.
    try:
        coverage = Coverage.write_coverage(slug_dir, out)
        summary = coverage['summary']
        log['coverage'] = summary
        ev('Coverage', f"{summary['sections_needing_review']}/{summary['sections_total']} source sections need review; {summary['routes_linked']}/{summary['routes_total']} source pages linked")
    except Exception as e:
        ev('Coverage', 'unavailable: ' + str(e)[:90])
        log['coverage'] = {'error': str(e)[:200]}
        with open(os.path.join(slug_dir, 'coverage.json'), 'w', encoding='utf-8') as f:
            json.dump({'scope': 'single_page_preview', 'error': str(e)[:200]}, f)
    # The skeleton of the page that ships (which forms, in which order): comparable across jobs without a model.
    try:
        import fingerprint as FP
        with open(out, encoding='utf-8') as f: fp = FP.fingerprint(f.read())
        with open(os.path.join(slug_dir, 'fingerprint.json'), 'w', encoding='utf-8') as f: json.dump(fp, f, indent=1)
        log['fingerprint'] = {k: fp[k] for k in ('hero', 'body', 'digest', 'body_digest')}
    except Exception as e: ev('Render', 'fingerprint unavailable: ' + str(e)[:80])
    # What a browser measures on the page that ships — while it loads, scrolls and moves — and what the Standard says of
    # it. Reported beside the page; the critic's own findings for the round that ships stand next to the measured ones.
    report = measured(slug_dir, out) if time.time() - started < MEASURE_BY else None
    if report:
        shipped = next((r for r in log['rounds'] if r.get('k') == best_round), {})
        reviewed = shipped.get('findings') if isinstance(shipped.get('findings'), list) else []
        try:
            with open(os.path.join(slug_dir, 'findings.json'), 'w', encoding='utf-8') as f:
                json.dump({'round': best_round, 'measured': report['findings'], 'reviewed': reviewed, 'gaps': [x for x in reviewed if (x.get('correction') or {}).get('op') == 'gap'],
                           'technical': report['technical'], 'readings': report['readings']}, f, indent=1, ensure_ascii=False)
        except OSError: pass
        log['measure'] = {'findings': [f"{x['id']}@{x['view']}" for x in report['findings']], 'technical': report['technical']}
        failed_checks = [c['id'] for c in report['technical'] if not c['pass']]
        ev('Measure', f"{len(report['findings'])} findings against the Standard · " + (('measured checks failed: ' + ', '.join(failed_checks)) if failed_checks else 'measured checks pass'))
        for x in report['findings'][:4]: ev('Measure', f"{x['id']} {x['evidence']['reading']}: {json.dumps(x['evidence']['value'], ensure_ascii=False)[:40]} (expected {x['evidence']['expected']})")
    else: ev('Measure', 'the page was not measured')
    card = scorecard(log, best_round, report)
    if card:
        still = (log.get('layout') or {}).get('left') or []
        if still:   # typesetting that is still broken is a hard failure of the technical track, whatever the contract scored
            card['technical']['hard_failures'] = list(card['technical'].get('hard_failures') or []) + [f"layout: {b['kind']} in {b.get('section')} at {b.get('widths')}" for b in still[:5]]
            card['technical']['pass'] = False
        log['scores'] = card
        with open(os.path.join(slug_dir, 'scores.json'), 'w', encoding='utf-8') as f: json.dump(card, f, indent=1)
        tech = card['technical']
        tech_note = f"clears {tech['min']}" if tech['pass'] else ('broken: ' + ', '.join(tech['hard_failures'][:2]) if tech['hard_failures'] else f"below {tech['min']}")
        ev('Critic', f"design {card['taste']}/100 ({'clears' if card['creative']['pass'] else 'below'} {card['creative']['min']}) · technical {card['contract']}/100 ({tech_note})")
    log['best'] = best_score; log['best_round'] = best_round; log['best_blueprint'] = best_bp
    json.dump(log, open(os.path.join(slug_dir, 'swarm.json'), 'w'), indent=1, ensure_ascii=False)
    print(json.dumps({"done": {"score": best_score, "rounds": len(log['rounds']), "best_blueprint": best_bp, "render_manifest": best_manifest, "scores": log.get('scores')}}), flush=True)

if __name__ == '__main__': main()
