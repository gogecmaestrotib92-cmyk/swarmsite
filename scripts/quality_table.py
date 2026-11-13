#!/usr/bin/env python3
"""quality_table.py <runs root> [--md] — what of each client's page reached the designs the engine showed.

Reads the folders a local job run leaves (<root>/<site>/capr/<capture>/…, <root>/<site>/tpl/…) and prints one row a
site: designs shown, sections of the client's page carried into the data (the adapter's own count), the words on the
shown pages against the words of the client's page, the client's pictures used against those written, and why the
designs held back were held. No browser, no model: it reads files. A row is flagged THIN when the fullest shown page
carries under 40 % of the client's words, or FEW when under three designs are shown — the two ways a job is "pretty
and empty" (owner, 2026-11-13). The thresholds are for the table, not a gate: they are to be set from a wide run."""
import glob
import html
import json
import os
import re
import sys


def words(markup):
    body = re.sub(r'<(script|style|noscript|svg)[\s\S]*?</\1>', ' ', markup)
    return html.unescape(re.sub(r'<[^>]+>', ' ', body)).split()


def row(site_dir):
    cap = next(iter(glob.glob(os.path.join(site_dir, 'capr', '*', ''))), None)
    tj = os.path.join(site_dir, 'tpl', 'templates.json')
    if not cap or not os.path.isfile(tj):
        return {'site': os.path.basename(site_dir), 'error': 'no capture' if not cap else 'no build'}
    inv = json.load(open(os.path.join(cap, 'inventory.json')))
    t = json.load(open(tj))
    client = len(((inv.get('copy') or {}).get('text') or '').split())
    ad = os.path.join(site_dir, 'tpl', 'adapter.json')
    cov = (json.load(open(ad)).get('coverage') if os.path.isfile(ad) else None) or {}
    media = [f for f in glob.glob(os.path.join(site_dir, 'tpl', 'media', '*')) if os.path.isfile(f) and not os.path.basename(f).startswith('logo')]
    pages = []
    for slug in t.get('shown') or []:
        src = open(os.path.join(site_dir, 'tpl', slug + '.html'), encoding='utf-8').read()
        used = {m for m in re.findall(r'media/([\w.-]+\.(?:jpe?g|png|webp|gif|avif))', src) if not m.startswith('logo')}
        pages.append({'words': len(words(src)), 'pictures': len(used)})
    held = {}
    for c in t.get('chosen') or []:
        for k in c.get('failed') or []:
            held[k] = held.get(k, 0) + 1
    best = max((p['words'] for p in pages), default=0)
    flags = [f for f, on in (('FEW', len(pages) < 3), ('THIN', client and best < client * .4)) if on]
    return {'site': os.path.basename(site_dir), 'shown': len(pages), 'sections': '%s/%s' % (cov.get('carried', '?'), cov.get('sections', '?')),
            'client_words': client, 'page_words': [p['words'] for p in pages], 'pictures': '%s of %d' % ('/'.join(str(p['pictures']) for p in pages) or '-', len(media)),
            'held': held, 'flags': flags, 'left': (cov.get('left') or [])[:6]}


def main(argv):
    md = '--md' in argv
    roots = [a for a in argv if not a.startswith('--')]
    if not roots:
        print(__doc__)
        return 2
    rows = [row(d) for d in sorted(glob.glob(os.path.join(roots[0], '*'))) if os.path.isdir(d) and glob.glob(os.path.join(d, 'capr'))]
    if md:
        print('| site | designs | sections carried | client words | words on each design | client pictures used | held back | flag |\n|---|---|---|---|---|---|---|---|')
    for r in rows:
        if r.get('error'):
            print(('| %s | %s |' if md else '%-30s %s') % (r['site'], r['error']))
            continue
        cells = [r['site'], str(r['shown']), r['sections'], str(r['client_words']), ' / '.join(map(str, r['page_words'])) or '-', r['pictures'],
                 ', '.join('%s×%d' % kv for kv in sorted(r['held'].items())) or '-', ' '.join(r['flags']) or '']
        print('| ' + ' | '.join(cells) + ' |' if md else '%-30s %s  %-6s %5s  %-18s %-16s %-28s %s' % tuple(cells))
    ok = [r for r in rows if not r.get('error')]
    print('\n%d sites · %d with three designs · %d THIN · %d FEW' % (len(ok), sum(r['shown'] >= 3 for r in ok), sum('THIN' in r['flags'] for r in ok), sum('FEW' in r['flags'] for r in ok)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
