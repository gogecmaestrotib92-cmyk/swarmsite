"""slots.py — where a made (library) picture may stand on a page: behind things, never as a thing to look at.

The rule (owner, 2026-11-13): a CONTENT slot — a tile, an inset, a card's picture, a device, the picture of a step or of
a feature: anything the page presents as something to look at — takes the client's own material, in this order: product
screens and phone screens, then the client's photographs, then a picture tied to that feature or step. A made picture
of the library is for BACKDROPS and atmosphere only: the ground of a section, the band behind text, the field of an
opening. A template whose content slot the client cannot fill drops or re-flows that device; it never fills it from
the library.

    uses(html) -> [{'src', 'slot', 'how'}]      every library picture a rendered page shows, with the slot it stands in
                                                (its own `data-slot`, else `class:<its class>`, else its wrapper's mark, else `?`)
    undeclared(slug, html) -> [use …]           those that stand in a slot the template has not declared a backdrop
    BACKDROPS                                   made_slots.json: {template: [slot names that are grounds]} — every slot
                                                of every template that takes a library picture is listed there, looked at
                                                and named a backdrop; a slot that is not listed is a content slot

tests/test_templates_slots.py renders every template on every made-up client with a full family of made pictures and
fails when a library picture stands in an undeclared slot. No browser, no network.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIBRARY = 'media/library/'
BACKDROPS = json.loads((HERE / 'made_slots.json').read_text(encoding='utf-8'))
_PATH = re.compile(r'media/library/[^"\')\s]+')


def uses(html):
    out = []
    for m in _PATH.finditer(html):
        lt = html.rfind('<', 0, m.start())
        gt = html.find('>', m.end())
        tag = html[lt:gt if gt != -1 else m.end()]                  # the whole tag the path stands in
        own = re.search(r'data-slot="([^"]+)"', tag)
        cls = (re.search(r'class="([^"]*)"', tag) or [None, ''])[1].split(' ')[0]
        how = 'css' if 'url(' in html[max(0, m.start() - 8):m.start()] else (re.match(r'<(\w+)', tag) or [None, '?'])[1]
        # an unmarked picture takes the mark of the box it was just opened in (a wrapper's data-slot within 300 characters
        # before it); a picture set by a style rule is a background by construction; else '?' — never a declared backdrop
        before = html[max(0, lt - 300):lt]
        near = [m2 for m2 in re.finditer(r'data-slot="([^"]+)"', before) if '</' not in before[m2.end():]]   # a box still open, not one already closed
        in_style = tag.startswith('<style')
        slot = own.group(1) if own and not in_style else ('class:' + cls if cls and how != 'css' else 'css-background' if in_style else near[-1].group(1) if near else '?')
        out.append({'src': m.group(0), 'slot': re.sub(r'-?\d+', '', slot), 'how': how})   # panel-1, panel-2 … are one slot
    return out


def undeclared(slug, html):
    ok = set(BACKDROPS.get(slug) or [])
    return [u for u in uses(html) if u['slot'] not in ok]
