"""artdir.py — art direction for the one commissioned visual a page may carry: an atmosphere, never an object.

The words on the page stay the site's, and so do its pictures. A generated picture set beside a paragraph is
filler — the thing awarded pages never do — so a commission is allowed in exactly one place: as the defocused
backdrop behind one statement, where it reads as light and material, not as an illustration of anything.
Places (restaurants, hotels) get no generated imagery at all: a photograph of a dining room that does not exist
is a lie; those pages are built from their own photographs only.
"""
import re

STYLE = {
    # photographic material studies only: physically plausible, the kind of macro a studio shoots for a brand; never a glossy 3D blob
    'software': 'macro photograph of a real material that stands for precision — brushed aluminium, etched glass, graph paper, a lens, a circuit trace — shallow depth of field, one directional light, restrained, physically plausible',
    'service': 'editorial still-life photograph of an architectural material — stone, paper, linen, brushed metal, timber grain — raking natural light, calm negative space, physically plausible',
    'product': 'studio macro photograph of the material or texture the product is made of, seamless backdrop, soft gradient light, physically plausible',
}

# generated imagery is the last resort for an empty slot, never the hero: the hero is the product or the type
SUBJECT = {
    'photo': 'a single material surface in close-up',
    'features': 'a single material surface in close-up, with a clear focal edge',
    'steps': 'a single material surface in close-up, with a clear focal edge',
    'cells': 'a single material surface in close-up',
    'quote': 'a calm material surface with generous negative space',
    'testimonials': 'a calm material surface with generous negative space',
}

NEGATIVE = 'Photograph, not a render: no 3D render, no glossy blobs, no neon, no gradients floating in space, no text, no letters, no numbers, no logos, no user interface, no screens, no watermark, no people, no faces, no hands.'


def colours(mood):
    if not isinstance(mood, dict): return ''
    names = {'paper': 'backdrop', 'accent': 'accent', 'alt': 'secondary surface'}
    return ', '.join(f"{names[k]} {mood[k]}" for k in ('paper', 'accent', 'alt') if mood.get(k))


def allowed(kind):
    return kind in STYLE


def prompt(kind, beat_type, mood, idea='', brand=''):
    """A complete commission prompt. `idea` is the section's heading or the editor's one-line need (never pasted as text)."""
    if not allowed(kind) or beat_type == 'hero': return ''  # the hero is never generated
    subj = SUBJECT.get(beat_type, SUBJECT['photo'])
    idea = re.sub(r'<[^>]+>', '', str(idea or '')).strip()
    parts = [f'Original commissioned visual for a {kind} website' + (f' ({brand})' if brand else '') + ':',
             f'{subj}' + (f', evoking "{idea[:80]}"' if idea else '') + '.',
             STYLE[kind] + '.',
             ('Palette: ' + colours(mood) + ' — the material sits in the backdrop tone; the accent appears only as a light or an edge.') if colours(mood) else 'Restrained palette, one accent.',
             NEGATIVE]
    return ' '.join(parts)


ATMOS = 'defocused, abstract, the material fills the frame edge to edge with no object or subject in the centre, one soft directional light from one side, low contrast, made to sit behind large text as a wash of the page\'s own colour — light if the backdrop tone is light, dark if it is dark'


def atmos_prompt(kind, mood, idea='', brand=''):
    """The one commission a page may carry: a backdrop behind a statement. `idea` is the statement itself (never pasted as text)."""
    if not allowed(kind): return ''
    idea = re.sub(r'<[^>]+>', '', str(idea or '')).strip()
    parts = [f'Atmospheric backdrop for a {kind} website' + (f' ({brand})' if brand else '') + ':',
             STYLE[kind] + ', ' + ATMOS + (f', evoking "{idea[:80]}"' if idea else '') + '.',
             ('Palette: ' + colours(mood) + ' — the picture lives in the backdrop tone and the secondary surface; the accent is a light or an edge, present but not loud.') if colours(mood) else 'The page\'s own palette, one accent as light.',
             NEGATIVE]
    return ' '.join(parts)


def ratio_for(beat_type, slot_hint=''):
    if beat_type == 'hero': return '16:9'
    if beat_type in ('features', 'steps'): return '16:9'
    return '4:3'
