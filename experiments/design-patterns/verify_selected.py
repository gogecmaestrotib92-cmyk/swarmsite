"""Confirm selected section moves also render on an alternate blueprint."""
import json
import sys
from pathlib import Path
from render_check import CATALOG, check


def verify(directory, blueprint):
    direction = json.loads((Path(directory) / 'direction.json').read_text())
    for beat in direction.get('beats', []):
        move = (beat.get('ui') or {}).get('move')
        if not move or move == 'auto': continue
        patterns = [p for p in CATALOG['patterns'] if p['move'] == move
                    and beat.get('type') in p['allowed_beat_types']
                    and direction.get('kind') in p['allowed_site_kinds']]
        if not any(check(directory, blueprint, beat['id'], p['id'], p['version']).get('accepted') for p in patterns):
            raise ValueError('selected section move unavailable on alternative blueprint')
    return True

if __name__ == '__main__':
    try:
        verify(*sys.argv[1:])
        print('selected section moves verified')
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
