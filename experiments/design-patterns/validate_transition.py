"""Reject loss of previously rendered content when changing section moves."""
import json
import sys
import tempfile
from pathlib import Path
from render_check import render, sections, byid, norm


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        yield str(value)
    elif isinstance(value, (list, tuple)):
        for item in value: yield from strings(item)
    elif isinstance(value, dict):
        for key, item in value.items():
            if key not in ('id', 'type', 'ui', 'image', 'href', 'url', 'source_sections'):
                yield from strings(item)


def validate(original, candidate, blueprint):
    original, candidate = Path(original), Path(candidate)
    direction = json.loads((original / 'direction.json').read_text())
    with tempfile.TemporaryDirectory(prefix='swarm-pattern-compare-') as tmp:
        old = render(original, blueprint, Path(tmp) / 'old.html')
        new = render(candidate, blueprint, Path(tmp) / 'new.html')
        if [s.attrs.get('id') for s in sections(old)] != [s.attrs.get('id') for s in sections(new)]:
            raise ValueError('section order changed')
        for beat in direction.get('beats', []):
            section_id = beat.get('id')
            a, b = byid(old, section_id), byid(new, section_id)
            if not a or not b: raise ValueError('section absent or ambiguous')
            old_text, new_text = norm(a.text()), norm(b.text())
            if any(norm(value) and norm(value) in old_text and norm(value) not in new_text for value in strings(beat)):
                raise ValueError('rendered section content was lost')
            for tag, attr in (('a', 'href'), ('img', 'src'), ('source', 'src')):
                def values(section):
                    return {node.attrs.get(attr) for node in section.find(lambda n: n.tag == tag) if node.attrs.get(attr)}
                if not values(a).issubset(values(b)): raise ValueError('rendered section link or media was lost')
    return True

if __name__ == '__main__':
    try:
        validate(*sys.argv[1:])
        print('transition verified')
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
