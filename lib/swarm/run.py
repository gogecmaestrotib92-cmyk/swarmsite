"""run.py — the swarm loop. After the Designer (direct.py) has written direction.json:
  round 0: Reader (if not yet) → UX → Copy → UI → Visual → render
  round k: Critic looks at the render → routes each defect to its owner (copy / ui / visual / ux) → owners fix in parallel → bounded critic ops → render
Stops at --target score or --rounds. Prints one JSON line per event (the server turns them into swarm events) and a final {"done":…} line.
Opt-in, after the rounds (brief.json "compose": true, or SWARM_COMPOSE=1): the first screen of the winning page and the lists
below it are recomposed (lib/compose) and the composed page is kept only if it scores at least as high as the page it would replace.
Usage: python3 lib/swarm/run.py out/<slug> <blueprint-id> --out bp-<id>.html [--rounds 3] [--target 80]"""
import json, os, sys, time, subprocess, traceback, shutil, tempfile, hashlib
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'lib/swarm')); sys.path.insert(0, os.path.join(ROOT, 'lib/qa')); sys.path.insert(0, os.path.join(ROOT, 'lib'))
import agents as A
import critic as C
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

def scorecard(log, best_round):
    """Taste and contract of the round that ships, side by side, and whether each clears its own bar.
    Reported, not enforced: what ships is decided by the loop above. Here a high contract never stands in for taste —
    the two are never added up. Bars: GATE_TECHNICAL (default 90, and no hard failure) and GATE_CREATIVE (default 70)."""
    rec = next((r for r in log.get('rounds', []) if r.get('k') == best_round), None)
    if not rec: return None
    def bar(name, default):
        try: return int(os.environ.get(name) or default)
        except ValueError: return default
    technical_min, creative_min = bar('GATE_TECHNICAL', 90), bar('GATE_CREATIVE', 70)
    contract, taste = rec.get('contract'), rec.get('taste')
    hard = [str(f.get('id')) for f in rec.get('broken') or [] if isinstance(f, dict) and any(h in str(f.get('id')) for h in HARD)]
    number = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool)
    return {'round': best_round, 'taste': taste, 'contract': contract, 'blended': rec.get('score'), 'axes': rec.get('axes'),
            'technical': {'pass': bool(number(contract) and contract >= technical_min and not hard), 'min': technical_min, 'hard_failures': hard},
            'creative': {'pass': bool(number(taste) and taste >= creative_min), 'min': creative_min},
            'enforced': False}

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

def compose_wanted(slug_dir):
    """An art director recomposes the first screen only when the job asks for it (brief.json: "compose": true) or the
    deployment does (SWARM_COMPOSE=1). Without either, nothing in lib/compose runs."""
    brief = A.J(slug_dir, 'brief.json') or {}
    return os.environ.get('SWARM_COMPOSE') == '1' or brief.get('compose') is True


def compose_first_screen(slug_dir, out):
    """Recompose the page at `out` (lib/compose) — its first screen, then the lists below it, each a document that is
    validated, measured on its own render and refused whole if it breaks anything — and write composition.json. The page
    file is replaced only by what passed; a part that did not pass leaves that part of the page as it was.
    Returns the record: {'drawn', 'attempts', 'concept', 'face', 'measured', 'wishes', 'log', 'ir', 'lists'}; 'drawn' is
    true when either part was drawn."""
    if os.path.join(ROOT, 'lib', 'compose') not in sys.path: sys.path.insert(0, os.path.join(ROOT, 'lib', 'compose'))
    import compose as COMPOSE, render_ir as IR
    def replace(page):
        with open(out + '.composed', 'w', encoding='utf-8') as f: f.write(page)
        os.replace(out + '.composed', out)
    with open(out, encoding='utf-8') as f: page = f.read()
    images = A.J(slug_dir, 'images.json') or []
    result = COMPOSE.compose(page, images, job_dir=slug_dir, page_path=out, concepts=COMPOSE_CONCEPTS)
    ir = result.get('ir')
    record = {'drawn': False, 'attempts': result.get('attempts'), 'concept': (ir or {}).get('note'), 'face': ((ir or {}).get('hero') or {}).get('face'),
              'measured': result.get('measured'), 'wishes': result.get('wishes'), 'log': result.get('log'), 'ir': ir, 'lists': None,
              **{k: result[k] for k in ('concepts', 'chosen', 'verdict') if k in result}}
    if ir:
        composed, report = IR.transplant(page, ir, images)
        if report['drawn']: replace(composed); page = composed; record['drawn'] = True
    try:   # the lists are composed on the page as it now stands, so that they are seen under the first screen they follow
        import compose_lists as COMPOSE_LISTS, lists as LISTS
        chosen = COMPOSE_LISTS.compose(page, out); doc = chosen.get('doc')
        record['lists'] = {'drawn': False, 'attempts': chosen.get('attempts'), 'concept': (doc or {}).get('note'), 'forms': {l['section']: l['form'] for l in (doc or {}).get('lists', [])},
                           'measured': chosen.get('measured'), 'log': chosen.get('log'), 'doc': doc}
        if doc:
            composed, report = LISTS.transplant(page, doc)
            if report['drawn']: replace(composed); record['lists']['drawn'] = True; record['drawn'] = True
    except Exception as e: record['lists'] = {'drawn': False, 'error': str(e)[:160]}
    with open(os.path.join(slug_dir, 'composition.json'), 'w', encoding='utf-8') as f: json.dump(record, f, indent=1, ensure_ascii=False)
    return record


def composed_candidate(slug_dir, out, best_score, best_broken, grade):
    """The composed page is one more candidate, held to the loop's own rule: it replaces the winner only if the contract
    and the critic, looking at its own render, score it at least as high and it breaks no hard promise the winner kept.
    `grade()` → (contract report, critic report) for the page at `out`. Returns the decision; when 'kept' is false the
    caller puts the winner's files back."""
    record = compose_first_screen(slug_dir, out)
    decision = {'kept': False, 'drawn': record['drawn'], 'attempts': record.get('attempts'), 'concept': record.get('concept'), 'face': record.get('face'), 'before': best_score,
                'first_screen': bool(record.get('ir')), 'lists': (record.get('lists') or {}).get('forms') if (record.get('lists') or {}).get('drawn') else None}
    if not record['drawn']:
        decision['why'] = 'no composition passed validation and measurement'; return decision
    con, rep = grade()
    taste = rep.get('score') if isinstance(rep, dict) and isinstance(rep.get('score'), (int, float)) else None
    if taste is None or not isinstance(con.get('score'), (int, float)):
        decision['why'] = 'the composed page could not be graded'; return decision
    score = round(0.55 * taste + 0.45 * con['score']); failed = con.get('failed', [])
    hard = lambda ids: {i for i in ids if any(i.endswith(h) or i == h for h in HARD)}
    newly = sorted(hard(f['id'] for f in failed) - hard(f['id'] for f in (best_broken or [])))
    decision.update(score=score, taste=taste, contract=con['score'], broken=failed, critic=rep)
    if newly: decision['why'] = 'it breaks ' + ', '.join(newly)
    elif score < best_score: decision['why'] = f'it scores {score}, the page it would replace {best_score}'
    else: decision['kept'] = True
    return decision


def recompose(slug_dir, out, log, best_score, best_round, best_manifest, best_files, snapshot_dir):
    """Offer the winning page a composed first screen and keep whichever page scores higher. Returns the (score, round,
    manifest) of the page that stands. A composed page that is kept becomes one more round in the log, with the critic's
    and the contract's reports of that page; a refused one leaves every file of the winner exactly as it was."""
    winner = next((r for r in log['rounds'] if r.get('k') == best_round), {})
    try:
        def grade():
            with ThreadPoolExecutor(2) as ex:
                fcon = ex.submit(contract, slug_dir, out); frep = ex.submit(C.critique, slug_dir, out, A.MODEL, False)
                return fcon.result(), frep.result()
        decision = composed_candidate(slug_dir, out, best_score, winner.get('broken'), grade)
    except Exception as e:
        decision = {'kept': False, 'drawn': False, 'before': best_score, 'why': 'failed: ' + str(e)[:120]}
    rep = decision.pop('critic', None); cfail = decision.pop('broken', None)
    if decision['kept']:
        k = max(r['k'] for r in log['rounds']) + 1
        fixes = [f for f in (rep.get('fixes') if isinstance(rep.get('fixes'), list) else []) if isinstance(f, dict)]
        log['rounds'].append({'k': k, 'composed': True, 'score': decision['score'], 'taste': decision['taste'], 'contract': decision['contract'], 'axes': rep.get('axes') if isinstance(rep.get('axes'), dict) else None, 'broken': cfail, 'fixes': fixes, 'verdict': rep.get('verdict')})
        with open(os.path.join(slug_dir, 'critic.json'), 'w') as f:
            json.dump({**rep, 'score': decision['score'], 'taste': decision['taste'], 'contract': decision['contract'], 'broken': cfail, 'round': k, 'best': decision['score'], 'composed': True}, f, indent=1, ensure_ascii=False)
        best_score, best_round = decision['score'], k; best_manifest = dict(best_manifest, html=digest(out))
        if decision.get('first_screen'): ev('Concept', 'first screen recomposed: ' + str(decision.get('concept') or '')[:110])
        if decision.get('lists'): ev('Concept', 'lists recomposed: ' + ', '.join(f'{k} as {v}' for k, v in decision['lists'].items())[:110])
        ev('Critic', f"composed page kept: {decision['score']}/100 (was {decision['before']}) · taste {decision['taste']} · contract {decision['contract']}")
    else:   # the winner's page, documents, contract, critic and screenshots go back exactly as they were
        for path, data in best_files.items():
            with open(path, 'wb') as f: f.write(data)
        restore_shots(slug_dir, snapshot_dir)
        if best_manifest['html'] != digest(out): raise RuntimeError('the winning page could not be restored after a refused composition')
        ev('Concept', 'page left as the rounds made it: ' + str(decision.get('why') or '')[:100])
    log['composition'] = decision
    try:
        record = A.J(slug_dir, 'composition.json') or {}
        record.update({key: decision.get(key) for key in ('kept', 'why', 'before', 'score', 'taste', 'contract', 'first_screen')})
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
COMPOSE_CONCEPTS = 1 if os.environ.get('SWARM_COMPOSE_CONCEPTS') == '1' else 3   # first screens drawn before one is chosen

def _main(snapshot_dir):
    started = time.time()
    slug_dir, bp = sys.argv[1], sys.argv[2]; args = sys.argv[3:]
    out = args[args.index('--out') + 1] if '--out' in args else os.path.join(slug_dir, f'bp-{bp}.html')
    rounds = int(args[args.index('--rounds') + 1]) if '--rounds' in args else 3
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
    best_score, best_key, best_round, best_files, best_bp, best_manifest = -1, None, None, None, None, None
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
        log['rounds'].append({'k': k, 'score': score, 'taste': taste, 'contract': con.get('score'), 'axes': rep.get('axes') if isinstance(rep.get('axes'), dict) else None, 'broken': cfail, 'fixes': fixes, 'verdict': rep.get('verdict')})
        # taste leads: the combined score already carries the contract at 45%; a broken promise only breaks a tie
        rank = (score, not cfail, -len(fixes))
        if best_key is None or rank > best_key:
            best_score, best_key, best_round, best_bp, best_manifest = score, rank, k, bp, render_manifest
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
            if rank <= (previous['score'], not previous['broken'], -len(previous['fixes'])):
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
    if compose_wanted(slug_dir) and isinstance(best_manifest, dict) and best_files and time.time() - started < COMPOSE_BY:
        best_score, best_round, best_manifest = recompose(slug_dir, out, log, best_score, best_round, best_manifest, best_files, snapshot_dir)
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
    card = scorecard(log, best_round)
    if card:
        log['scores'] = card
        with open(os.path.join(slug_dir, 'scores.json'), 'w', encoding='utf-8') as f: json.dump(card, f, indent=1)
        tech = card['technical']
        tech_note = f"clears {tech['min']}" if tech['pass'] else ('broken: ' + ', '.join(tech['hard_failures'][:2]) if tech['hard_failures'] else f"below {tech['min']}")
        ev('Critic', f"design {card['taste']}/100 ({'clears' if card['creative']['pass'] else 'below'} {card['creative']['min']}) · technical {card['contract']}/100 ({tech_note})")
    log['best'] = best_score; log['best_round'] = best_round; log['best_blueprint'] = best_bp
    json.dump(log, open(os.path.join(slug_dir, 'swarm.json'), 'w'), indent=1, ensure_ascii=False)
    print(json.dumps({"done": {"score": best_score, "rounds": len(log['rounds']), "best_blueprint": best_bp, "render_manifest": best_manifest, "scores": log.get('scores')}}), flush=True)

if __name__ == '__main__': main()
