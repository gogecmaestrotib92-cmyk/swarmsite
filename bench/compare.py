"""compare.py — a blind side-by-side of two engine variants, and the tally of the answers.

  python3 bench/compare.py build <variantA> <variantB> [--seed 7] [--viewports desktop,mobile]
      → bench/runs/compare-<A>-vs-<B>/index.html  (open it in a browser; answers stay in that browser until exported)
        bench/runs/compare-<A>-vs-<B>/key.json    (which side was which — do not open before judging)
  python3 bench/compare.py score <compare-dir> <answers.json>
      → per question: how often each variant was preferred, with a 95% interval on the share

The page never names a variant: pictures are copied under neutral names and sides are shuffled per pair with a seed.
Each pair is one site at one viewport. The six questions are the ones in SWARMSITE_PRODUCT_STRATEGY.md §4.3."""
import hashlib, html, json, math, os, random, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__)); RUNS = os.path.join(HERE, 'runs')
QUESTIONS = [('professional', 'Which looks more professional?'), ('typography', 'Which has stronger typography?'),
             ('identity', 'Which has a more distinctive visual identity?'), ('fit', 'Which better represents this business?'),
             ('template', 'Which feels less template-driven?'), ('studio', 'Which would you expect from a professional design studio?')]

PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Blind comparison</title><style>
:root{--paper:#f6f4ef;--ink:#16150f;--line:#d9d5ca;--muted:#6b675c;--pick:#16150f;--pick-ink:#f6f4ef}
@media(prefers-color-scheme:dark){:root{--paper:#14130f;--ink:#efece3;--line:#34322b;--muted:#a09c8f;--pick:#efece3;--pick-ink:#14130f}}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.45 system-ui,-apple-system,Segoe UI,sans-serif}
header{position:sticky;top:0;z-index:2;background:var(--paper);border-bottom:1px solid var(--line);padding:10px 16px;display:flex;gap:12px;align-items:center;flex-wrap:wrap}
header b{font-weight:600}header .grow{flex:1}button{font:inherit;color:inherit;background:none;border:1px solid var(--line);border-radius:6px;padding:7px 12px;cursor:pointer}
button:hover{border-color:var(--ink)}button.on{background:var(--pick);color:var(--pick-ink);border-color:var(--pick)}button:disabled{opacity:.35;cursor:default}
main{padding:16px;max-width:1500px;margin:0 auto}.meta{color:var(--muted);margin:0 0 10px}.meta a{color:inherit}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:12px}.pair.mobile{max-width:900px;margin:0 auto}
.side{border:1px solid var(--line);border-radius:8px;overflow:hidden;background:#fff}.side h2{margin:0;padding:6px 10px;font-size:13px;font-weight:600;color:var(--muted);background:var(--paper);border-bottom:1px solid var(--line)}
.scroll{height:72vh;overflow:auto}.scroll img{display:block;width:100%;height:auto}
.q{display:grid;grid-template-columns:1fr auto;gap:8px 16px;align-items:center;padding:10px 0;border-bottom:1px solid var(--line)}.q:last-child{border:0}
.q p{margin:0}.q div{display:flex;gap:6px;flex-wrap:wrap}.questions{margin-top:14px}
@media(max-width:700px){.q{grid-template-columns:1fr}.scroll{height:56vh}main{padding:10px}}
</style></head><body>
<header><b>Blind comparison</b><span id="where"></span><span class="grow"></span><button id="prev">Back</button><button id="next">Next</button><button id="export">Download answers</button></header>
<main><p class="meta" id="meta"></p><div class="pair" id="pair"></div><div class="questions" id="questions"></div></main>
<script>
const PAIRS = __PAIRS__, QUESTIONS = __QUESTIONS__, ID = __ID__;
const KEY = 'swarmsite-blind-' + ID; let state = {}; try { state = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) {}
let at = 0; const $ = s => document.querySelector(s);
function save() { try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {} }
function answered(i) { return QUESTIONS.every(q => (state[PAIRS[i].id] || {})[q[0]]); }
function count() { $('#where').textContent = `${at + 1} / ${PAIRS.length} · ${PAIRS.filter((_, i) => answered(i)).length} answered`; }
function questions() {  // only the buttons change when an answer is given: the two pictures keep their place
  const p = PAIRS[at];
  $('#questions').innerHTML = QUESTIONS.map(q => `<div class="q"><p>${q[1]}</p><div>${['left', 'same', 'right'].map(v => `<button data-q="${q[0]}" data-v="${v}" class="${(state[p.id] || {})[q[0]] === v ? 'on' : ''}">${v === 'same' ? 'No difference' : v === 'left' ? 'Left' : 'Right'}</button>`).join('')}</div></div>`).join('');
  count();
}
function show() {
  const p = PAIRS[at];
  $('#meta').innerHTML = `${p.viewport} · the original site, for reference: <a href="${p.url}" target="_blank" rel="noopener">${p.host}</a>`;
  $('#pair').className = 'pair ' + p.viewport;
  $('#pair').innerHTML = ['left', 'right'].map(s => `<div class="side"><h2>${s === 'left' ? 'Left' : 'Right'}</h2><div class="scroll"><img src="${p[s]}" alt="${s} page"></div></div>`).join('');
  const boxes = document.querySelectorAll('.scroll'); let lock = false;  // the two pictures scroll together, by share of their height
  boxes.forEach((b, i) => b.addEventListener('scroll', () => { if (lock) return; lock = true; const o = boxes[1 - i]; o.scrollTop = b.scrollTop / Math.max(1, b.scrollHeight - b.clientHeight) * (o.scrollHeight - o.clientHeight); requestAnimationFrame(() => lock = false); }));
  questions(); $('#prev').disabled = at === 0; $('#next').disabled = at === PAIRS.length - 1; scrollTo(0, 0);
}
document.addEventListener('click', e => { const b = e.target.closest('button[data-q]'); if (!b) return; const p = PAIRS[at]; (state[p.id] = state[p.id] || {})[b.dataset.q] = b.dataset.v; save(); questions(); });
$('#prev').onclick = () => { if (at > 0) { at--; show(); } }; $('#next').onclick = () => { if (at < PAIRS.length - 1) { at++; show(); } };
$('#export').onclick = () => { const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([JSON.stringify({ comparison: ID, at: new Date().toISOString(), answers: state }, null, 1)], { type: 'application/json' })); a.download = 'answers-' + ID + '.json'; a.click(); };
show();
</script></body></html>"""


def build(a, b, seed=7, viewports=('desktop', 'mobile')):
    with open(os.path.join(HERE, 'sites.json')) as f: sites = json.load(f)['sites']
    out = os.path.join(RUNS, f'compare-{a}-vs-{b}'); shutil.rmtree(out, ignore_errors=True); os.makedirs(out)
    rng = random.Random(seed); pairs, key, skipped = [], {}, []
    for site in sites:
        for viewport in viewports:
            pa, pb = (os.path.join(RUNS, v, site['id'], f'{viewport}.jpg') for v in (a, b))
            if not (os.path.exists(pa) and os.path.exists(pb)): skipped.append(f"{site['id']}/{viewport}"); continue
            same = hashlib.sha1(open(pa, 'rb').read()).hexdigest() == hashlib.sha1(open(pb, 'rb').read()).hexdigest()
            if same: skipped.append(f"{site['id']}/{viewport} (identical pictures)"); continue
            pid = f'p{len(pairs) + 1:02d}'; left_is_a = rng.random() < .5
            names = {'left': f'{pid}-l.jpg', 'right': f'{pid}-r.jpg'}
            shutil.copyfile(pa if left_is_a else pb, os.path.join(out, names['left'])); shutil.copyfile(pb if left_is_a else pa, os.path.join(out, names['right']))
            url = site['url'] if str(site.get('url', '')).lower().startswith(('http://', 'https://')) else ''
            host = url.split('//')[-1].strip('/').replace('www.', '')
            pairs.append({'id': pid, 'viewport': viewport, 'url': html.escape(url, quote=True), 'host': html.escape(host), **names})
            key[pid] = {'site': site['id'], 'viewport': viewport, 'left': a if left_is_a else b, 'right': b if left_is_a else a}
    rng.shuffle(pairs)
    ident = hashlib.sha1(json.dumps([a, b, seed, sorted(key)]).encode()).hexdigest()[:10]
    page = PAGE.replace('__PAIRS__', json.dumps(pairs)).replace('__QUESTIONS__', json.dumps(QUESTIONS)).replace('__ID__', json.dumps(ident))
    with open(os.path.join(out, 'index.html'), 'w', encoding='utf-8') as f: f.write(page)
    with open(os.path.join(out, 'key.json'), 'w') as f: json.dump({'comparison': ident, 'variants': [a, b], 'seed': seed, 'pairs': key}, f, indent=1)
    return out, len(pairs), skipped


def interval(wins, n):
    """Wilson 95% interval on a share; honest at small n, where a plain ± would run past 0 or 1."""
    if not n: return (0.0, 0.0)
    z = 1.96; p = wins / n; d = 1 + z * z / n; mid = (p + z * z / (2 * n)) / d; half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(max(0, mid - half), 3), round(min(1, mid + half), 3))


def score(directory, answers_path):
    with open(os.path.join(directory, 'key.json')) as f: key = json.load(f)
    with open(answers_path) as f: answers = json.load(f)
    if answers.get('comparison') != key['comparison']: raise SystemExit('these answers belong to a different comparison')
    a, b = key['variants']; table = {}
    for pid, given in (answers.get('answers') or {}).items():
        sides = key['pairs'].get(pid)
        if not sides: continue
        for q, v in given.items():
            row = table.setdefault(q, {a: 0, b: 0, 'same': 0})
            if v in ('left', 'right'): row[sides[v]] += 1
            elif v == 'same': row['same'] += 1
    report = {'variants': [a, b], 'pairs_answered': len(answers.get('answers') or {}), 'questions': {}}
    for q, label in QUESTIONS:
        row = table.get(q, {a: 0, b: 0, 'same': 0}); decided = row[a] + row[b]
        report['questions'][q] = {'question': label, a: row[a], b: row[b], 'no_difference': row['same'],
                                  f'share_{b}': round(row[b] / decided, 3) if decided else None, 'interval_95': interval(row[b], decided)}
    return report


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) >= 3 and args[0] == 'build':
        seed = int(args[args.index('--seed') + 1]) if '--seed' in args else 7
        views = tuple(args[args.index('--viewports') + 1].split(',')) if '--viewports' in args else ('desktop', 'mobile')
        out, n, skipped = build(args[1], args[2], seed, views)
        print(f'{n} pairs → {os.path.join(out, "index.html")}' + (f' · skipped: {", ".join(skipped)}' if skipped else ''))
    elif len(args) == 3 and args[0] == 'score':
        print(json.dumps(score(args[1], args[2]), indent=1))
    else: raise SystemExit(__doc__)
