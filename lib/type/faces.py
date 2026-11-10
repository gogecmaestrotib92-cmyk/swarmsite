"""faces.py — the registry of display typefaces a page may be set in (faces.json).

Every face is free to ship (SIL Open Font License, served by Google Fonts); the css2 spec and the widths in the file
are checked and measured by lib/type/measure.mjs, never guessed. A face that is not in the file cannot be chosen.

  all()            → the faces a page may choose, in file order
  get(face_id)     → one face or None
  known(family)    → the measured widths of a family, whether it can be chosen or is only one pages are already set in
  stack(face)      → the CSS font-family value
  link(face)       → the stylesheet URL; links(faces) → the stylesheets for several faces, one request per source
  of_role(role)    → the faces that may be chosen as 'display', 'body' or 'label'; pairings() → systems known to sit well together
  advance(face, upper=False) → mean advance of one headline character in em (a wide default for an unknown face)
The advance is an average: a real line can be a tenth wider or narrower. What sizes a headline in the end is the
measurement of its own words in a browser (lib/compose/measure.mjs); this number is the estimate before that.
Deterministic, no network."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ADVANCE = 0.6    # a face we have not measured is assumed wide: a headline sized for it never overflows
DEFAULT_UPPER = 0.74
_cache = None


def _registry():
    global _cache
    if _cache is None:
        with open(os.path.join(HERE, 'faces.json'), encoding='utf-8') as f: _cache = json.load(f)
    return _cache


def all():
    return _registry()['faces']


def known(family):
    if not family: return None
    wanted = str(family).casefold()
    return next((f for f in all() + _registry().get('known', []) if f['family'].casefold() == wanted), None)


def get(face_id):
    return next((f for f in all() if f['id'] == face_id), None)


def of_role(role):
    """The faces that may be chosen for a role: 'display' (headings), 'body' (running text), 'label' (the small print:
    labels, numerals, captions). A face without `roles` is a display face."""
    return [f for f in all() if role in f.get('roles', ['display'])]


def pairings():
    """Systems of faces that are known to sit well together: [{'id', 'display', 'body', 'label', 'voice'}]."""
    return _registry().get('pairings', [])


def stack(face):
    return f"'{face['family']}',{face['fallback']}"


def link(face):
    return face.get('css') or f"https://fonts.googleapis.com/css2?family={face['gf']}&display=swap"


def links(faces):
    """The stylesheets that load these faces: every Google family in one request, a face from another source by its own."""
    seen, google, other = set(), [], []
    for f in faces:
        if not f or f['family'] in seen: continue
        seen.add(f['family']); (other if f.get('css') else google).append(f)
    return ([f"https://fonts.googleapis.com/css2?family={'&family='.join(f['gf'] for f in google)}&display=swap"] if google else []) + [f['css'] for f in other]


def advance(face, upper=False):
    default = DEFAULT_UPPER if upper else DEFAULT_ADVANCE
    if not face: return default
    return face.get('avg_upper' if upper else 'avg') or default
