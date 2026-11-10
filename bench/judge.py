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
    started = time.time(); record = run.compose_first_screen(job, out)
    with ThreadPoolExecutor(2) as pool:
        graded = pool.submit(run.contract, job, out); seen = pool.submit(run.C.critique, job, out, run.A.MODEL, False)
        con, rep = graded.result(), seen.result()
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
              'shipped': {'taste': before.get('taste'), 'contract': before.get('contract'), 'score': before.get('score')}}
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
        print(f"{site:22s} composed taste {r['taste']} contract {r['contract']} → {r['blended']}   shipped taste {r['shipped']['taste']} contract {r['shipped']['contract']} → {r['shipped']['score']}   {r['seconds']}s ${r['usd'] or 0:.2f}", flush=True)
        print(f"   parts: first screen {'yes' if c['first_screen'] else 'no'} · lists {c['lists']} · pictures {c['pictures']} · words {c['words']}", flush=True)
        print('   ' + str(r['verdict'])[:900], flush=True)
