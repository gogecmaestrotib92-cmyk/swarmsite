"""budget.py — one ledger per job: how many model calls and tokens this job has spent, and the hard caps.
Every model call in the pipeline (agents.ask, direct.py, critic.py, site_map via agents.ask) goes through `charge()`.
The ledger is a file in the job directory (the pipeline is several Python processes), found through SWARM_JOB_DIR
which the server sets per job. Without SWARM_JOB_DIR (local runs, tests) accounting is skipped.
Caps come from env: JOB_MAX_CALLS (default 60) and JOB_MAX_TOKENS (input+output, default 3,000,000)."""
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

def check(who=''):
    """Raise before a call when the job is already over its cap, so the cap is never exceeded by a whole call."""
    p = _path()
    if not p: return
    b = read(p); max_calls, max_tokens = caps()
    if b['calls'] >= max_calls: raise BudgetExceeded(f'job budget: {b["calls"]} model calls (cap {max_calls}) before {who or "next call"}')
    if b['in'] + b['out'] >= max_tokens: raise BudgetExceeded(f'job budget: {b["in"] + b["out"]} tokens (cap {max_tokens}) before {who or "next call"}')

def charge(usage, who=''):
    """Record one call's usage. `usage` is the SDK usage object or a dict; missing fields count as 0."""
    p = _path()
    if not p: return
    g = lambda k: int(getattr(usage, k, None) or (usage.get(k) if isinstance(usage, dict) else 0) or 0)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p + '.lock', 'w') as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        b = read(p)
        b['calls'] += 1; b['in'] += g('input_tokens') + g('cache_creation_input_tokens'); b['out'] += g('output_tokens'); b['cache_read'] += g('cache_read_input_tokens')
        by = b.setdefault('by', {}); by[who or '?'] = by.get(who or '?', 0) + 1; b['at'] = time.time()
        tmp = p + '.tmp'
        with open(tmp, 'w') as f: json.dump(b, f)
        os.replace(tmp, p)

def summary():
    b = read(); mc, mt = caps()
    return f"{b['calls']}/{mc} calls · {(b['in'] + b['out']) // 1000}k/{mt // 1000}k tokens"
