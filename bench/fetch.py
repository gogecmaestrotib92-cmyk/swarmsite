"""fetch.py — freeze the benchmark inputs: download the artefacts of each site's job into bench/seed/<id>/.

The benchmark compares engines on identical input. That input is the set of files a finished job leaves behind
(what was captured, what the reader and the director wrote). They are fetched once and never regenerated, so every
engine variant starts from the same capture and the same words.

Usage: python3 bench/fetch.py [site-id ...]      (no arguments: every site in bench/sites.json that has a job)
Reads only; needs no credentials. bench/seed/ is not committed (third-party text and images)."""
import json, os, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
INPUTS = ('brief.json', 'inventory.json', 'assets.json', 'images.json', 'geometry.json', 'audit.json', 'mobile.json', 'factsheet.json', 'direction.json')
RECORDS = ('critic.json', 'contract.json', 'coverage.json', 'swarm.json', 'index.html')  # what the engine made at the time: the shipped baseline


def fetch(site, api, force=False):
    target = os.path.join(HERE, 'seed', site['id']); os.makedirs(target, exist_ok=True)
    got, missing = [], []
    for name in INPUTS + RECORDS:
        path = os.path.join(target, name)
        if os.path.exists(path) and not force: got.append(name); continue
        try:
            with urllib.request.urlopen(f"{api}/jobs/{site['job']}/art/{name}", timeout=90) as r: data = r.read()
        except Exception as e:
            missing.append(f'{name} ({str(e)[:40]})'); continue
        with open(path, 'wb') as f: f.write(data)
        got.append(name)
    with open(os.path.join(target, 'source.json'), 'w') as f:
        json.dump({'id': site['id'], 'url': site['url'], 'job': site['job'], 'captured': site.get('captured')}, f, indent=1)
    required = [n for n in ('inventory.json', 'images.json', 'direction.json') if n not in got]
    return got, missing, required


def main():
    with open(os.path.join(HERE, 'sites.json')) as f: doc = json.load(f)
    api = os.environ.get('SWARMSITE_API') or doc['api']
    args = sys.argv[1:]; force = '--force' in args; wanted = [a for a in args if not a.startswith('--')]
    failed = 0
    for site in doc['sites']:
        if wanted and site['id'] not in wanted: continue
        if not site.get('job'): print(f"– {site['id']}: no job recorded"); continue
        got, missing, required = fetch(site, api, force)
        if required: failed += 1
        print(f"{'✗' if required else '✓'} {site['id']}: {len(got)} files" + (f" · missing {', '.join(missing)}" if missing else ''))
    raise SystemExit(1 if failed else 0)


if __name__ == '__main__': main()
