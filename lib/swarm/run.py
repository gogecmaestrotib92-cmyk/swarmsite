"""run.py — the swarm loop. After the Designer (direct.py) has written direction.json:
  round 0: Reader (if not yet) → UX → Copy → UI → Visual → render
  round k: Critic looks at the render → routes each defect to its owner (copy / ui / visual / ux) → owners fix in parallel → bounded critic ops → render
Stops at --target score or --rounds. Prints one JSON line per event (the server turns them into swarm events) and a final {"done":…} line.
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

def _main(snapshot_dir):
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
        log['rounds'].append({'k': k, 'score': score, 'taste': taste, 'contract': con.get('score'), 'broken': cfail, 'fixes': fixes, 'verdict': rep.get('verdict')})
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
    log['best'] = best_score; log['best_round'] = best_round; log['best_blueprint'] = best_bp
    json.dump(log, open(os.path.join(slug_dir, 'swarm.json'), 'w'), indent=1, ensure_ascii=False)
    print(json.dumps({"done": {"score": best_score, "rounds": len(log['rounds']), "best_blueprint": best_bp, "render_manifest": best_manifest}}), flush=True)

if __name__ == '__main__': main()
