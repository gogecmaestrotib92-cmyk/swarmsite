"""compose.py — have the model compose the hero of every benchmark site (or the ones named), from the `shipped` render.

  python3 bench/compose.py [site-id ...] [--no-review]
  python3 bench/compose.py --fit [site-id ...]     measure the headlines of the compositions already written, in a browser, and
                                                   write the measurement into them — no model call
Writes bench/runs/_compositions/<site>.json (+ .log.json with every attempt, the validator's reasons and the model's
wishes) and a budget per site. Then `python3 bench/run.py modelled` renders and measures them.
Needs ANTHROPIC_API_KEY and bench/runs/shipped/ (run `bench/run.py shipped` first). Spends model calls: about three per site."""
import json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'lib', 'compose')); sys.path.insert(0, os.path.join(ROOT, 'lib'))
import compose as COMPOSE
import budget as B


def refit(sites, wanted, out):
    for site in sites:
        path = os.path.join(out, site['id'] + '.json'); page = os.path.join(HERE, 'runs', 'shipped', site['id'], 'page.html')
        if (wanted and site['id'] not in wanted) or not os.path.exists(path) or not os.path.exists(page): continue
        with open(path, encoding='utf-8') as f: ir = json.load(f)
        with open(page, encoding='utf-8') as f: html = f.read()
        with open(os.path.join(HERE, 'seed', site['id'], 'images.json')) as f: images = json.load(f)
        fitted = COMPOSE.fit(html, ir, images, os.path.dirname(page))
        with open(path, 'w', encoding='utf-8') as f: json.dump(fitted, f, indent=1, ensure_ascii=False)
        h1 = next((n for n in fitted['hero']['nodes'] if n.get('as') == 'h1'), {})
        print(f"{'✓' if h1.get('fit') else '–'} {site['id']:22s} fit {h1.get('fit')}", flush=True)


def main():
    args = sys.argv[1:]; review = '--no-review' not in args; wanted = [a for a in args if not a.startswith('--')]
    with open(os.path.join(HERE, 'sites.json')) as f: sites = json.load(f)['sites']
    out = os.path.join(HERE, 'runs', '_compositions'); os.makedirs(out, exist_ok=True); total = 0.0; wishes = []
    if '--fit' in args: return refit(sites, wanted, out)
    for site in sites:
        if wanted and site['id'] not in wanted: continue
        page = os.path.join(HERE, 'runs', 'shipped', site['id'], 'page.html'); seed = os.path.join(HERE, 'seed', site['id'])
        if not os.path.exists(page): print(f"– {site['id']}: no shipped render"); continue
        ledger = os.path.join(out, 'budget', site['id'] + '-' + time.strftime('%H%M%S')); os.makedirs(ledger, exist_ok=True); os.environ['SWARM_JOB_DIR'] = ledger
        with open(page, encoding='utf-8') as f: html = f.read()
        with open(os.path.join(seed, 'images.json')) as f: images = json.load(f)
        t = time.time(); result = COMPOSE.compose(html, images, job_dir=seed, page_path=page, model=os.environ.get('COMPOSE_MODEL') or None, review=review)
        spent = B.read(os.path.join(ledger, 'budget.json')); total += spent.get('usd', 0)
        if result['ir']:
            with open(os.path.join(out, site['id'] + '.json'), 'w', encoding='utf-8') as f: json.dump(result['ir'], f, indent=1, ensure_ascii=False)
        with open(os.path.join(out, site['id'] + '.log.json'), 'w', encoding='utf-8') as f:
            json.dump({'drawn': result['drawn'], 'attempts': result['attempts'], 'seconds': round(time.time() - t), 'calls': spent.get('calls'), 'usd': spent.get('usd'), 'log': result['log'], 'wishes': result['wishes']}, f, indent=1, ensure_ascii=False)
        wishes += [dict(w, site=site['id']) for w in result['wishes']]
        stages = ' → '.join(f"{s['stage']}{'✗' if s['errors'] else '✓'}" for s in result['log'])
        print(f"{'✓' if result['drawn'] else '✗'} {site['id']:22s} {stages:34s} {round(time.time() - t):>3}s ${spent.get('usd', 0):.3f}  {(result['ir'] or {}).get('note', '')[:110]}", flush=True)
    with open(os.path.join(out, 'wishes.json'), 'w', encoding='utf-8') as f: json.dump(wishes, f, indent=1, ensure_ascii=False)
    print(f'total ${total:.2f} · {len(wishes)} wishes for primitives the format lacks → {os.path.join(out, "wishes.json")}')


if __name__ == '__main__': main()
