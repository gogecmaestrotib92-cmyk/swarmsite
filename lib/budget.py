"""budget.py — one ledger per job: how many model calls and tokens this job has spent, and the hard caps.
Every model call in the pipeline (agents.ask, direct.py, critic.py, site_map via agents.ask) goes through `charge()`.
The ledger is a file in the job directory (the pipeline is several Python processes), found through SWARM_JOB_DIR
which the server sets per job. Without SWARM_JOB_DIR (local runs, tests) accounting is skipped.
Caps come from env: JOB_MAX_CALLS (default 60) and JOB_MAX_TOKENS (input+output, default 3,000,000).
The ledger also keeps the job's cost in dollars at list price (`usd`): each call is priced by its model from
lib/prices.json (or the MODEL_PRICES env table). A model with no price is counted in `unpriced_calls`, never guessed,
so `usd` is a floor whenever that counter is not zero. Generated pictures are counted in `images` and priced only
when IMAGE_USD (dollars per picture) is set."""
import json, os, time, fcntl

class BudgetExceeded(RuntimeError): pass

def _path():
    d = os.environ.get('SWARM_JOB_DIR')
    return os.path.join(d, 'budget.json') if d else None

def caps():
    return int(os.environ.get('JOB_MAX_CALLS', '60') or 60), int(os.environ.get('JOB_MAX_TOKENS', '3000000') or 3000000)

def read(path=None):
    p = path or _path()
    if not p or not os.path.exists(p): return {'calls': 0, 'in': 0, 'out': 0, 'cache_read': 0, 'by': {}}
    try:
        with open(p) as f: return json.load(f)
    except Exception: return {'calls': 0, 'in': 0, 'out': 0, 'cache_read': 0, 'by': {}}

def prices():
    """List price per million tokens by model id: {"in", "out", "cache_read"}. MODEL_PRICES (JSON object) replaces the file."""
    raw = os.environ.get('MODEL_PRICES')
    if raw:
        try:
            table = json.loads(raw)
            if isinstance(table, dict): return table
        except ValueError: pass
    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prices.json')) as f: table = json.load(f).get('models')
        return table if isinstance(table, dict) else {}
    except (OSError, ValueError): return {}

def cost(model, tokens_in, tokens_out, cache_read=0):
    """Dollars for one call at list price, or None when this model has no price here."""
    p = prices().get(str(model or ''))
    number = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool) and v >= 0
    if not isinstance(p, dict) or not number(p.get('in')) or not number(p.get('out')): return None
    read_price = p['cache_read'] if number(p.get('cache_read')) else p['in'] * .1  # a cached token reads at about a tenth of the input price
    return (tokens_in * p['in'] + tokens_out * p['out'] + cache_read * read_price) / 1e6

def check(who=''):
    """Raise before a call when the job is already over its cap, so the cap is never exceeded by a whole call."""
    p = _path()
    if not p: return
    b = read(p); max_calls, max_tokens = caps()
    if b['calls'] >= max_calls: raise BudgetExceeded(f'job budget: {b["calls"]} model calls (cap {max_calls}) before {who or "next call"}')
    if b['in'] + b['out'] >= max_tokens: raise BudgetExceeded(f'job budget: {b["in"] + b["out"]} tokens (cap {max_tokens}) before {who or "next call"}')

def charge(usage, who='', model=None):
    """Record one call's usage and its cost. `usage` is the SDK usage object or a dict; missing fields count as 0.
    `model` is the id the call was made with; without it (or without a price for it) the call is counted as unpriced."""
    p = _path()
    if not p: return
    g = lambda k: int(getattr(usage, k, None) or (usage.get(k) if isinstance(usage, dict) else 0) or 0)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p + '.lock', 'w') as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        b = read(p)
        tokens_in = g('input_tokens') + g('cache_creation_input_tokens'); tokens_out = g('output_tokens'); cached = g('cache_read_input_tokens')
        b['calls'] += 1; b['in'] += tokens_in; b['out'] += tokens_out; b['cache_read'] += cached
        dollars = cost(model, tokens_in, tokens_out, cached)
        if dollars is None: b['unpriced_calls'] = b.get('unpriced_calls', 0) + 1
        else: b['usd'] = round(b.get('usd', 0) + dollars, 6)
        by = b.setdefault('by', {}); by[who or '?'] = by.get(who or '?', 0) + 1; b['at'] = time.time()
        tmp = p + '.tmp'
        with open(tmp, 'w') as f: json.dump(b, f)
        os.replace(tmp, p)

def charge_image(count=1):
    """Record generated pictures (not model calls: they do not count toward the caps). Priced only when IMAGE_USD is set."""
    p = _path()
    if not p or count <= 0: return
    try: price = float(os.environ.get('IMAGE_USD') or 0)
    except ValueError: price = 0
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p + '.lock', 'w') as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        b = read(p); b['images'] = b.get('images', 0) + count
        if price > 0: b['usd'] = round(b.get('usd', 0) + count * price, 6)
        else: b['unpriced_images'] = b.get('unpriced_images', 0) + count
        tmp = p + '.tmp'
        with open(tmp, 'w') as f: json.dump(b, f)
        os.replace(tmp, p)

def summary():
    b = read(); mc, mt = caps()
    text = f"{b['calls']}/{mc} calls · {(b['in'] + b['out']) // 1000}k/{mt // 1000}k tokens"
    if 'usd' in b: text += f" · ${b['usd']:.2f}" + ('+' if b.get('unpriced_calls') or b.get('unpriced_images') else '')
    return text
