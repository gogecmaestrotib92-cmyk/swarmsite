"""The job budget: every model call is counted in the job directory and the cap stops the next call, never mid-call."""
import os, sys, json, importlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))
import budget as B

class U:  # SDK-like usage object
    def __init__(s, i, o): s.input_tokens, s.output_tokens, s.cache_creation_input_tokens, s.cache_read_input_tokens = i, o, 0, 0

def test_no_job_dir_is_a_noop(monkeypatch, tmp_path):
    monkeypatch.delenv('SWARM_JOB_DIR', raising=False)
    B.check('x'); B.charge(U(10, 10), 'x')  # nothing raised, nothing written
    assert not list(tmp_path.iterdir())

def test_counts_and_caps(monkeypatch, tmp_path):
    monkeypatch.setenv('SWARM_JOB_DIR', str(tmp_path)); monkeypatch.setenv('JOB_MAX_CALLS', '3'); monkeypatch.setenv('JOB_MAX_TOKENS', '1000000')
    for _ in range(3): B.check('agent'); B.charge(U(100, 20), 'agent')
    b = json.load(open(tmp_path / 'budget.json'))
    assert b['calls'] == 3 and b['in'] == 300 and b['out'] == 60 and b['by'] == {'agent': 3}
    try: B.check('agent'); assert False, 'cap must stop the fourth call'
    except B.BudgetExceeded as e: assert '3 model calls' in str(e)

def test_token_cap(monkeypatch, tmp_path):
    monkeypatch.setenv('SWARM_JOB_DIR', str(tmp_path)); monkeypatch.setenv('JOB_MAX_CALLS', '100'); monkeypatch.setenv('JOB_MAX_TOKENS', '500')
    B.charge({'input_tokens': 400, 'output_tokens': 100}, 'd')
    try: B.check('d'); assert False
    except B.BudgetExceeded as e: assert 'tokens' in str(e)
    assert 'calls' in B.summary()
