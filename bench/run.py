"""run.py — render one engine variant over the frozen benchmark set and measure it. No model call.

Every variant starts from the same frozen files (bench/seed/<site>/), so a difference between two variants comes from
how the page is composed, never from a different capture or different words.

  shipped   the direction exactly as the job left it, through today's renderer
  house     the house lock applied: order and move of every section fixed per kind of business
  recipe    no house, per-section moves cleared: the chosen recipe's own slots decide the forms

Usage: python3 bench/run.py <variant> [site-id ...] [--no-shots]
Writes bench/runs/<variant>/<site>/{page.html, contract.json, fingerprint.json, result.json, desktop.jpg, mobile.jpg}
and bench/runs/<variant>/summary.json. Needs Python 3.12+, node and a Chrome (CHROME_PATH)."""
import copy, json, os, shutil, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'lib')); sys.path.insert(0, os.path.join(ROOT, 'lib', 'qa'))
import house as HOUSE
import fingerprint as FP

INPUTS = ('direction.json', 'images.json', 'assets.json', 'inventory.json', 'brief.json', 'hero.mp4')
# Promises whose failure means the page is broken for a visitor, not merely off-style.
HARD = ('no-overflow', 'no-empty-screens', 'contrast', 'actionable-cta', 'seo-text-kept', 'seo-links-kept')
MAC_CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'


def shipped(d): return d

def house(d):
    return HOUSE.lock(d, mode='lock')

def recipe(d):
    d.pop('house', None)
    for beat in d.get('beats', []):
        if isinstance(beat.get('ui'), dict): beat['ui'].pop('move', None)
    return d

VARIANTS = {'shipped': shipped, 'house': house, 'recipe': recipe}


def environment():
    env = dict(os.environ)
    if not env.get('CHROME_PATH') and os.path.exists(MAC_CHROME): env['CHROME_PATH'] = MAC_CHROME
    env.pop('LIVETEST', None)  # real fonts: the pictures are for people to judge
    return env


def run_site(site, variant, shots=True):
    seed = os.path.join(HERE, 'seed', site['id'])
    if not os.path.exists(os.path.join(seed, 'direction.json')): return {'site': site['id'], 'error': 'not fetched: run bench/fetch.py'}
    work = os.path.join(HERE, 'runs', variant, site['id'])
    shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
    for name in INPUTS:
        src = os.path.join(seed, name)
        if os.path.isfile(src): shutil.copyfile(src, os.path.join(work, name))
    with open(os.path.join(work, 'direction.json')) as f: frozen = json.load(f)
    direction = VARIANTS[variant](copy.deepcopy(frozen))
    with open(os.path.join(work, 'direction.json'), 'w') as f: json.dump(direction, f, ensure_ascii=False, indent=1)
    env = environment(); page = os.path.join(work, 'page.html'); result = {'site': site['id'], 'variant': variant, 'kind': direction.get('kind'), 'blueprint': site['blueprint'], 'mode': site.get('mode'), 'seconds': {}}
    t = time.time()
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'lib/render/render_bp.py'), work, site['blueprint'], page], capture_output=True, text=True, env=env, timeout=180)
    result['seconds']['render'] = round(time.time() - t, 1)
    if r.returncode: result['error'] = 'render: ' + r.stderr[-300:]; return result
    with open(page, encoding='utf-8') as f: html = f.read()
    result['bytes'] = len(html.encode('utf-8'))
    fp = FP.fingerprint(html); result['fingerprint'] = fp
    with open(os.path.join(work, 'fingerprint.json'), 'w') as f: json.dump(fp, f, indent=1)
    t = time.time()
    c = subprocess.run(['node', os.path.join(ROOT, 'lib/qa/contract.mjs'), page, '--dir', work], capture_output=True, text=True, env=env, timeout=300, cwd=ROOT)
    result['seconds']['contract'] = round(time.time() - t, 1)
    try:
        with open(os.path.join(work, 'contract.json')) as f: contract = json.load(f)
        failed = [x['id'] for x in contract.get('failed', [])]
        result['contract'] = contract.get('score'); result['failed'] = failed
        result['hard_failures'] = [i for i in failed if any(i.endswith(h) or i == h for h in HARD)]
    except (OSError, ValueError):
        result['contract'] = None; result['error'] = 'contract: ' + (c.stderr or c.stdout)[-300:]
    if shots:
        t = time.time()
        s = subprocess.run(['node', os.path.join(HERE, 'fullshot.mjs'), page, '--out', work], capture_output=True, text=True, env=env, timeout=300, cwd=ROOT)
        result['seconds']['shots'] = round(time.time() - t, 1)
        try: result['shots'] = json.loads(s.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError): result['shots_error'] = (s.stderr or s.stdout)[-300:]
    with open(os.path.join(work, 'result.json'), 'w') as f: json.dump(result, f, indent=1)
    return result


def summarise(variant, results):
    done = [r for r in results if r.get('fingerprint')]
    pages = {}
    for r in done:
        with open(os.path.join(HERE, 'runs', variant, r['site'], 'page.html'), encoding='utf-8') as f: pages[r['site']] = f.read()
    structure = FP.compare(pages) if len(pages) > 1 else None
    scores = [r['contract'] for r in done if isinstance(r.get('contract'), (int, float))]
    summary = {'variant': variant, 'sites': len(results), 'rendered': len(done),
               'contract': {'min': min(scores), 'median': sorted(scores)[len(scores) // 2], 'max': max(scores)} if scores else None,
               'technical_pass': sum(1 for r in done if isinstance(r.get('contract'), (int, float)) and r['contract'] >= 90 and not r.get('hard_failures')),
               'distinct_bodies': structure['distinct_bodies'] if structure else None,
               'mean_body_similarity': structure['mean_body_similarity'] if structure else None,
               'results': [{k: v for k, v in r.items() if k != 'fingerprint'} | ({'body': r['fingerprint']['body'], 'hero': r['fingerprint']['hero']} if r.get('fingerprint') else {}) for r in results]}
    with open(os.path.join(HERE, 'runs', variant, 'summary.json'), 'w') as f: json.dump(summary, f, indent=1)
    return summary


def main():
    args = sys.argv[1:]; shots = '--no-shots' not in args; args = [a for a in args if not a.startswith('--')]
    if not args or args[0] not in VARIANTS: raise SystemExit(__doc__)
    variant, wanted = args[0], args[1:]
    with open(os.path.join(HERE, 'sites.json')) as f: sites = json.load(f)['sites']
    results = []
    for site in sites:
        if wanted and site['id'] not in wanted: continue
        r = run_site(site, variant, shots); results.append(r)
        mark = '✗' if r.get('error') else '✓'
        print(f"{mark} {site['id']:22s} {site['blueprint']:14s} contract {r.get('contract')}  hard {r.get('hard_failures')}  " + (r.get('error') or ' | '.join((r.get('fingerprint') or {}).get('body', []))), flush=True)
    s = summarise(variant, results)
    print(f"{variant}: {s['rendered']}/{s['sites']} rendered · contract {s['contract']} · technical pass {s['technical_pass']} · distinct section sequences {s['distinct_bodies']} · mean similarity {s['mean_body_similarity']}")
    raise SystemExit(1 if any(r.get('error') for r in results) else 0)


if __name__ == '__main__': main()
