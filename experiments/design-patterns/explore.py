"""List renderer-verified pattern candidates without changing a job's files.

This is a local experiment, not a selector in the production swarm. A passing
candidate proves only the bounded structural checks in render_check.py.
"""
import argparse
import json
from pathlib import Path

from render_check import CATALOG, check


def explore(directory, blueprint):
    direction = json.loads((Path(directory) / 'direction.json').read_text())
    beats = direction.get('beats') if isinstance(direction, dict) else None
    if not isinstance(beats, list): raise ValueError('direction has no beat list')
    ids = [b.get('id') for b in beats if isinstance(b, dict)]
    if len(ids) != len(beats) or any(not isinstance(i, str) or not i for i in ids) or len(set(ids)) != len(ids):
        raise ValueError('beat identifiers must be unique, nonempty strings')
    results = []
    for beat in beats:
        for pattern in CATALOG['patterns']:
            if beat.get('type') not in pattern['allowed_beat_types'] or direction.get('kind') not in pattern['allowed_site_kinds']:
                continue
            result = check(directory, blueprint, beat['id'], pattern['id'], pattern['version'])
            results.append({'beat': beat['id'], 'pattern': pattern['id'], 'version': pattern['version'],
                            'accepted': bool(result.get('accepted')), 'reason': result.get('reason')})
    return {'blueprint': blueprint, 'candidates': results,
            'limitations': 'Structural dry run against the current snapshot; does not assess design, semantics or source coverage.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('directory'); parser.add_argument('blueprint')
    args = parser.parse_args()
    print(json.dumps(explore(args.directory, args.blueprint), ensure_ascii=False, indent=2))
