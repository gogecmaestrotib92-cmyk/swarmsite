"""judge.py — the production path for a benchmark site, run here, so that what the critic says of a composed page can be read.

  python3 bench/judge.py <site-id> [<site-id> ...]

For each site: its frozen job (bench/seed/<site>) and its `shipped` render are copied to a working folder, the page is
composed exactly as a production job with `options.compose: true` composes it (lib/swarm/run.py compose_first_screen:
first screen, lists, pictures, sections of words), and the composed page is graded by the real contract and the real
critic. Writes bench/runs/judged/<site>/{page.html, judge.json} and prints one line per site: taste and contract of the
composed page beside the scores the shipped page got on production, then the critic's verdict.

A production job keeps the composed page only when it scores at least as high as the page it would replace, and until
2026-11-10 it did not keep what the critic said of a page it refused. This is where that is read.
Needs ANTHROPIC_API_KEY and bench/runs/shipped/ (`bench/run.py shipped`). Spends model calls: about $0.5 a site."""
import json, os, shutil, sys, tempfile, time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'lib', 'swarm')); sys.path.insert(0, os.path.join(ROOT, 'lib', 'compose')); sys.path.insert(0, os.path.join(ROOT, 'lib'))
import run
import budget as B


def judge(site):
    seed = os.path.join(HERE, 'seed', site); shipped = os.path.join(HERE, 'runs', 'shipped', site, 'page.html')
    if not os.path.isdir(seed) or not os.path.exists(shipped): raise SystemExit(f'{site}: no seed or no shipped render (run bench/fetch.py and bench/run.py shipped)')
    job = tempfile.mkdtemp(prefix='bench-judge-'); shutil.copytree(seed, job, dirs_exist_ok=True)
    for stale in ('budget.json', 'composition.json'):   # the working folder is a fresh job: what the frozen one spent and composed is not this run's
        if os.path.exists(os.path.join(job, stale)): os.remove(os.path.join(job, stale))
    out = os.path.join(job, 'bp-judge.html'); shutil.copyfile(shipped, out); os.environ['SWARM_JOB_DIR'] = job
    kept = out + '.ref.html'; shutil.copyfile(shipped, kept)   # the shipped page, read by the critic as it is now, twice — as a production job reads its winner
    os.environ['SWARM_MEASURE'] = '1'   # both pages are measured in a browser before they are read, as a production job does
    def read_again():
        found = run.measured(job, kept, os.path.join(job, 'measure-ref'))
        return run.C.critique_twice(job, kept, run.A.MODEL, 'critic-shots-ref', **({'measured': found['findings']} if found else {})), found
    with ThreadPoolExecutor(1) as side:
        again = side.submit(read_again)
        started = time.time(); record = run.compose_first_screen(job, out)
        with ThreadPoolExecutor(2) as pool:
            graded = pool.submit(run.contract, job, out); counted = pool.submit(run.measured, job, out)
            con, found = graded.result(), counted.result()
        rep = run.C.critique_twice(job, out, run.A.MODEL, **({'measured': found['findings']} if found else {}))
        try: now, found_before = again.result(timeout=300)
        except Exception: now, found_before = {}, None
    rep = rep if isinstance(rep, dict) else {}; con = con if isinstance(con, dict) else {}
    try:
        with open(os.path.join(seed, 'critic.json')) as f: before = json.load(f)
    except (OSError, ValueError): before = {}
    forms = lambda part: (record.get(part) or {}).get('forms') if (record.get(part) or {}).get('drawn') else None
    taste, contract = rep.get('score'), con.get('score')
    result = {'site': site, 'seconds': round(time.time() - started), 'usd': B.read(os.path.join(job, 'budget.json')).get('usd'),
              'composed': {'first_screen': bool(record.get('ir')), 'concept': record.get('concept'), 'face': record.get('face'), 'type': ((record.get('ir') or {}).get('hero') or {}).get('type'),
                           'direction': record.get('direction'), 'lists': forms('lists'), 'pictures': forms('pictures'), 'words': forms('words'),
                           'refused': {part: [step for step in ((record.get(part) or {}).get('log') or []) if step.get('errors') or step.get('changes')] for part in ('lists', 'pictures', 'words')}},
              'taste': taste, 'contract': contract, 'blended': round(0.55 * taste + 0.45 * contract) if isinstance(taste, (int, float)) and isinstance(contract, (int, float)) else None,
              'failed': [f.get('id') for f in con.get('failed', [])], 'axes': rep.get('axes'), 'verdict': rep.get('verdict'), 'fixes': rep.get('fixes'),
              'readings': rep.get('readings'), 'studio': rep.get('studio'), 'levels': rep.get('levels'), 'page_level': rep.get('page_level'), 'findings': rep.get('findings'),
              'measured': {'findings': [f"{f['id']}@{f['view']}" for f in found['findings']], 'checks_failed': [c['id'] for c in found['technical'] if not c['pass']], 'readings': found['readings']['desktop']} if found else None,
              'shipped': {'taste': before.get('taste'), 'contract': before.get('contract'), 'score': before.get('score'), 'taste_now': now.get('score') if isinstance(now, dict) else None, 'readings_now': now.get('readings') if isinstance(now, dict) else None,
                          'verdict_now': now.get('verdict') if isinstance(now, dict) else None, 'page_level_now': now.get('page_level') if isinstance(now, dict) else None,
                          'measured': [f"{f['id']}@{f['view']}" for f in found_before['findings']] if found_before else None}}
    dest = os.path.join(HERE, 'runs', 'judged', site); os.makedirs(dest, exist_ok=True)
    shutil.copyfile(out, os.path.join(dest, 'page.html'))
    with open(os.path.join(dest, 'judge.json'), 'w', encoding='utf-8') as f: json.dump(result, f, indent=1, ensure_ascii=False)
    shutil.rmtree(job, ignore_errors=True)
    return result


if __name__ == '__main__':
    sites = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not sites: raise SystemExit(__doc__)
    for site in sites:
        r = judge(site); c = r['composed']
        print(f"{site:22s} composed taste {r['taste']} {r['readings'] or ''} contract {r['contract']} → {r['blended']}   shipped, read now: taste {r['shipped']['taste_now']} {r['shipped']['readings_now'] or ''} (on production: {r['shipped']['taste']})   {r['seconds']}s ${r['usd'] or 0:.2f}", flush=True)
        print(f"   parts: first screen {'yes' if c['first_screen'] else 'no'} · lists {c['lists']} · pictures {c['pictures']} · words {c['words']}", flush=True)
        print(f"   level {r['page_level']} (shipped {r['shipped']['page_level_now']}) · measured, composed: {(r['measured'] or {}).get('findings')} · shipped: {r['shipped']['measured']}", flush=True)
        print('   findings: ' + ' | '.join(f"{f['id']} {f['beat']} → {f['correction']['op']}" for f in (r['findings'] or [])), flush=True)
        print('   ' + str(r['verdict'])[:900], flush=True)
