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


def test_cost_in_dollars_by_model(monkeypatch, tmp_path):
    monkeypatch.setenv('SWARM_JOB_DIR', str(tmp_path)); monkeypatch.delenv('MODEL_PRICES', raising=False)
    B.charge(U(1_000_000, 100_000), 'direct', 'claude-sonnet-5-5')   # $2 per million in, $10 per million out
    b = json.load(open(tmp_path / 'budget.json'))
    assert b['usd'] == 3.0 and 'unpriced_calls' not in b
    B.charge({'input_tokens': 0, 'output_tokens': 0, 'cache_read_input_tokens': 1_000_000}, 'critic', 'claude-sonnet-5-5')
    assert json.load(open(tmp_path / 'budget.json'))['usd'] == 3.1    # cache reads at their own price
    assert '$3.10' in B.summary()

def test_a_model_without_a_price_is_counted_not_guessed(monkeypatch, tmp_path):
    monkeypatch.setenv('SWARM_JOB_DIR', str(tmp_path)); monkeypatch.delenv('MODEL_PRICES', raising=False)
    B.charge(U(500_000, 10_000), 'direct', 'some-model-nobody-priced'); B.charge(U(500_000, 10_000), 'direct')  # unknown id, and no id at all
    b = json.load(open(tmp_path / 'budget.json'))
    assert b['unpriced_calls'] == 2 and 'usd' not in b and b['calls'] == 2 and b['in'] == 1_000_000
    B.charge(U(1_000_000, 0), 'direct', 'claude-sonnet-5-5')
    b = json.load(open(tmp_path / 'budget.json'))
    assert b['usd'] == 2.0 and b['unpriced_calls'] == 2
    assert B.summary().endswith('$2.00+')   # the plus says: a floor, something was not priced

def test_price_table_can_be_replaced_from_the_environment(monkeypatch, tmp_path):
    monkeypatch.setenv('SWARM_JOB_DIR', str(tmp_path)); monkeypatch.setenv('MODEL_PRICES', json.dumps({'house-model': {'in': 1, 'out': 4}}))
    assert B.cost('house-model', 2_000_000, 500_000) == 4.0
    assert B.cost('house-model', 0, 0, 1_000_000) == 0.1            # no cache price given: a tenth of input
    assert B.cost('claude-sonnet-5-5', 1, 1) is None                # the env table replaces the file
    monkeypatch.setenv('MODEL_PRICES', 'not json'); assert B.cost('claude-sonnet-5-5', 1_000_000, 0) == 2.0
    monkeypatch.setenv('MODEL_PRICES', json.dumps({'bad': {'in': 'two', 'out': 4}})); assert B.cost('bad', 1, 1) is None

def test_generated_pictures_are_counted_and_priced_only_when_a_price_is_set(monkeypatch, tmp_path):
    monkeypatch.setenv('SWARM_JOB_DIR', str(tmp_path)); monkeypatch.delenv('IMAGE_USD', raising=False)
    B.charge_image(1); B.charge_image(0)
    b = json.load(open(tmp_path / 'budget.json'))
    assert b['images'] == 1 and b['unpriced_images'] == 1 and b['calls'] == 0 and 'usd' not in b
    monkeypatch.setenv('IMAGE_USD', '0.05'); B.charge_image(2)
    b = json.load(open(tmp_path / 'budget.json'))
    assert b['images'] == 3 and b['usd'] == 0.1 and b['unpriced_images'] == 1
    B.check('next')   # pictures never trip the model-call cap

def test_shipped_price_table_is_well_formed():
    import pathlib
    doc = json.load(open(pathlib.Path(__file__).resolve().parents[1] / 'lib' / 'prices.json'))
    assert doc['as_of'] and doc['models']['claude-sonnet-5-5'] == {'in': 2.0, 'out': 10.0, 'cache_read': 0.1}
    for name, p in doc['models'].items(): assert p['in'] > 0 and p['out'] >= p['in'], name
