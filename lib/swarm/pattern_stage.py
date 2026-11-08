"""Select structurally verified section compositions before rendering.

The selector runs in an isolated, time-limited process. If it fails, section
moves fall back to the renderer's defaults. Hero moves are not covered here.
"""
import copy
import hashlib
import json
import os
import signal
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / 'experiments' / 'design-patterns'
INPUTS = ('direction.json', 'images.json', 'assets.json', 'inventory.json', 'brief.json', 'hero.mp4')


def verify_transition(previous, candidate, blueprint, env):
    proc = subprocess.Popen([sys.executable, str(EXPERIMENT / 'validate_transition.py'),
                             str(previous), str(candidate), blueprint], cwd=ROOT, env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)
    try:
        _, err = proc.communicate(timeout=30)
    except subprocess.TimeoutExpired:
        try: os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError: pass
        proc.communicate()
        raise RuntimeError('pattern transition verification timed out')
    if proc.returncode:
        raise RuntimeError('pattern transition rejected: ' + err.strip()[:160])


def apply_verified_patterns(directory, blueprint, fingerprints, timeout=60):
    directory = Path(directory)
    def snapshot():
        files = ('catalog.json', 'choose_patterns.py', 'explore.py', 'render_check.py', 'validate_transition.py', 'verify_selected.py')
        return (fingerprints(str(directory), blueprint),
                {name: hashlib.sha256((EXPERIMENT / name).read_bytes()).hexdigest() for name in files})
    before = snapshot()
    original = json.loads((directory / 'direction.json').read_text())
    baseline = copy.deepcopy(original)
    for beat in baseline.get('beats', []):
        if isinstance(beat, dict) and isinstance(beat.get('ui'), dict):
            beat['ui'].pop('move', None)
    selected = baseline
    choices = []
    reason = 'no verified choices'
    with tempfile.TemporaryDirectory(prefix='swarm-pattern-stage-') as tmp:
        staged = Path(tmp) / 'inputs'
        staged.mkdir()
        previous = Path(tmp) / 'previous'
        previous.mkdir()
        for name in INPUTS[1:]:
            source = directory / name
            if source.is_file():
                shutil.copyfile(source, staged / name)
                shutil.copyfile(source, previous / name)
        (staged / 'direction.json').write_text(json.dumps(baseline, ensure_ascii=False))
        (previous / 'direction.json').write_text(json.dumps(original, ensure_ascii=False))
        env = dict(os.environ, TMPDIR=tmp)
        proc = subprocess.Popen([sys.executable, str(EXPERIMENT / 'choose_patterns.py'), str(staged), blueprint, '--preview'],
                                cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, start_new_session=True)
        try:
            stdout, _ = proc.communicate(timeout=timeout)
            if proc.returncode != 0:
                reason = 'selector unavailable'
            else:
                result = json.loads(stdout)
                choices = result.get('choices') or []
                if choices:
                    candidate_dir = Path(result['trial_directory']).resolve()
                    if Path(tmp).resolve() not in candidate_dir.parents:
                        raise ValueError('preview outside isolated workspace')
                    candidate = json.loads((candidate_dir / 'direction.json').read_text())
                    catalog = json.loads((EXPERIMENT / 'catalog.json').read_text())
                    permitted = {(p['id'], p['version']): p['move'] for p in catalog['patterns']}
                    expected = copy.deepcopy(baseline)
                    by_id = {b['id']: b for b in expected['beats']}
                    seen = set()
                    if len(choices) > 3: raise ValueError('too many choices')
                    for choice in choices:
                        beat, key = choice['beat'], (choice['pattern'], choice['version'])
                        if beat in seen or beat not in by_id or key not in permitted: raise ValueError('invalid choice')
                        seen.add(beat)
                        by_id[beat].setdefault('ui', {})['move'] = permitted[key]
                    if candidate != expected: raise ValueError('unexpected changes in selection')
                    selected = candidate
                    reason = 'verified selections'
        except subprocess.TimeoutExpired:
            try: os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError: pass
            proc.communicate()
            reason = 'selector timed out'
        except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
            choices = []
            reason = 'selector result rejected'
        (staged / 'direction.json').write_text(json.dumps(selected, ensure_ascii=False))
        verify_transition(previous, staged, blueprint, env)
        if snapshot() != before:
            raise RuntimeError('pattern inputs changed during selection')
        # Write the complete validated direction atomically. Any unexpected
        # selector result uses the default baseline, never unverified moves.
        fd, name = tempfile.mkstemp(prefix='.direction-', dir=directory)
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as out:
                json.dump(selected, out, ensure_ascii=False, indent=1)
            os.replace(name, directory / 'direction.json')
        finally:
            if os.path.exists(name): os.unlink(name)
    return {'choices': choices, 'reason': reason}
