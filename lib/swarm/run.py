"""run.py — the swarm loop. After the Designer (direct.py) has written direction.json:
  round 0: Reader (if not yet) → UX → Copy → UI → Visual → render
  round k: Critic looks at the render → routes each defect to its owner (copy / ui / visual / ux) → owners fix in parallel → bounded critic ops → render
Stops at --target score or --rounds. Prints one JSON line per event (the server turns them into swarm events) and a final {"done":…} line.
Usage: python3 lib/swarm/run.py out/<slug> <blueprint-id> --out bp-<id>.html [--rounds 3] [--target 80]"""
import json, os, sys, time, subprocess, traceback
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'lib/swarm')); sys.path.insert(0, os.path.join(ROOT, 'lib/qa'))
import agents as A
import critic as C

def ev(role, text): print(json.dumps({"event": {"role": role, "text": str(text)[:140]}}, ensure_ascii=False), flush=True)

def render(slug_dir, bp, out):
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'lib/render/render_bp.py'), slug_dir, bp, out], capture_output=True, text=True, timeout=120)
    if r.returncode: raise RuntimeError('render: ' + r.stderr[-400:])
    return out

def safe(name, fn, *a):
    t = time.time()
    try: n = fn(*a); ev(name, f'{n if isinstance(n, int) else "ok"} change(s) · {round(time.time() - t)}s'); return n
    except Exception as e: ev(name, 'skipped: ' + str(e)[:90]); traceback.print_exc(file=sys.stderr); return 0

def main():
    slug_dir, bp = sys.argv[1], sys.argv[2]; args = sys.argv[3:]
    out = args[args.index('--out') + 1] if '--out' in args else os.path.join(slug_dir, f'bp-{bp}.html')
    rounds = int(args[args.index('--rounds') + 1]) if '--rounds' in args else 3
    target = int(args[args.index('--target') + 1]) if '--target' in args else 80
    log = {'rounds': [], 'blueprint': bp}
    if not os.path.exists(os.path.join(slug_dir, 'factsheet.json')): safe('Reader', A.reader, slug_dir)
    fs_ = A.J(slug_dir, 'factsheet.json') or {}
    if fs_: ev('Reader', f"{fs_.get('what', '')[:90]}"); ev('Reader', f"{len(fs_.get('facts', []))} facts · {len(fs_.get('offers', []))} offers · {len(fs_.get('quotes', []))} quotes")
    # round 0: the specialists shape the director's document
    safe('UX', A.ux, slug_dir); safe('Copy', A.copy, slug_dir); safe('UI', A.ui, slug_dir); safe('Visual', A.visual, slug_dir)
    d = A.J(slug_dir, 'direction.json')
    ev('UX', 'order: ' + ' → '.join(b['type'] for b in d['beats'])); ev('Copy', 'h1: ' + str(d['hero'].get('h1', '')).replace('<em>', '').replace('</em>', ''))
    vis = (d.get('swarm') or {}).get('visual') or {}
    for x in (vis.get('generated') or [])[:3]: ev('Visual', 'commissioned: ' + x)
    for x in (vis.get('gen_errors') or [])[:1]: ev('Visual', 'generation failed: ' + x)
    for x in (vis.get('need') or [])[:2]: ev('Visual', 'missing visual: ' + x)
    render(slug_dir, bp, out); ev('Render', f'{bp} · round 0')
    best = (-1, None)
    for k in range(1, rounds + 1):
        t = time.time()
        try: rep = C.critique(slug_dir, out, A.MODEL)
        except Exception as e: ev('Critic', 'skipped: ' + str(e)[:90]); break
        score = rep.get('score', -1); fixes = rep.get('fixes', [])
        ev('Critic', f'round {k}: {score}/100 · {len(fixes)} defects · {round(time.time() - t)}s'); ev('Critic', str(rep.get('verdict', ''))[:140])
        log['rounds'].append({'k': k, 'score': score, 'fixes': fixes, 'verdict': rep.get('verdict')})
        if score > best[0]: best = (score, open(out).read())
        json.dump({**rep, 'round': k, 'best': best[0]}, open(os.path.join(slug_dir, 'critic.json'), 'w'), indent=1, ensure_ascii=False)
        if score >= target or k == rounds: break
        # route: every defect goes to its owner with the critic's reason
        notes = {'copy': [], 'ui': [], 'visual': [], 'ux': []}
        for f in fixes:
            owner = f.get('agent') or {'shorten': 'copy', 'hero_h1': 'copy', 'swap_image': 'visual', 'hero_image': 'visual', 'band': 'ui', 'layout': 'ui', 'drop_beat': 'ux', 'reorder': 'ux', 'note': 'ui'}.get(f.get('op'), 'ui')
            notes.setdefault(owner, []).append(f"[{f.get('op')}] beat={f.get('beat', '')} {f.get('field', '')} {f.get('value', '') or f.get('image', '') or ''} — {f.get('reason', '')}")
        applied = C.apply(slug_dir, {'fixes': [f for f in fixes if f.get('op') in ('drop_beat', 'hero_image', 'band')]})  # structural ops stay bounded
        for owner, ns in notes.items():
            if ns: ev(owner.upper() if owner in ('ux', 'ui') else owner.capitalize(), f'{len(ns)} note(s) from the critic')
        jobs = [(n, getattr(A, n), '\n'.join(notes[n])) for n in ('copy', 'ui', 'visual', 'ux') if notes.get(n)]
        with ThreadPoolExecutor(max_workers=4) as ex:
            res = list(ex.map(lambda j: (j[0], safe(j[0].upper() if j[0] in ('ux', 'ui') else j[0].capitalize(), j[1], slug_dir, j[2])), jobs))
        if applied + sum(r for _, r in res) == 0: ev('Critic', 'nothing more the team can change'); break
        render(slug_dir, bp, out); ev('Render', f'{bp} · round {k}')
    # keep the best-scoring render if the last round regressed
    if best[1] and log['rounds'] and log['rounds'][-1]['score'] < best[0]: open(out, 'w').write(best[1]); ev('Critic', f'kept round with {best[0]}/100')
    log['best'] = best[0]; json.dump(log, open(os.path.join(slug_dir, 'swarm.json'), 'w'), indent=1, ensure_ascii=False)
    print(json.dumps({"done": {"score": best[0], "rounds": len(log['rounds'])}}), flush=True)

if __name__ == '__main__': main()
