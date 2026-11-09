#!/usr/bin/env python3
"""retrieve.py — which measured references fit a brand. Deterministic: no model, no network, no embedding.
Standard library only; reads design_dna/references/*.json and nothing else.

    retrieve(brand, k=4)       -> [{id, score, components, reasons, gaps, applies, card}], best first
    brand_from_job(job_dir)    -> brand
    python3 design_dna/retrieve.py <job dir> [--k N] [--json]

brand   {"kind": "place" | "service" | "software" | "product",
         "subtype": "restaurant" | ... | None,
         "photographs": int, "screenshots": int,     stills the brand owns
         "has_video": bool,
         "mode": "light" | "dark" | None,            None = no preference
         "temper": [tag, ...]}                       tags from TEMPER_TAGS below; unknown tags never match

Score = kind + imagery + temper + mode + video + subtype, at most 100.

  kind     40   brand.kind is one of the reference's kinds (the blueprint's class). Not a filter.
  imagery  30   need = fits.needs.images_min, the sections of the reference that hold a large still.
                supply = photographs + screenshots: the capture cannot tell a photograph from a screenshot, so a
                still is a still.
                  need > supply : 30 × (supply + 1) / (need + 1)                      the brand cannot fill the layout
                  need ≤ supply : 30 × (1 − 0.5 × (min(supply, 8) − min(need, 8)) / 8)  the layout leaves pictures unused
  temper   10   10 × (brand.temper tags found on the reference) / (brand.temper tags given); 0 when none are given.
  mode     10   brand.mode equals the reference's measured surface (composition.surface.mode); 0 when no preference.
  video     5   brand.has_video equals "the reference's first section holds a video" (fits.needs.video).
  subtype   5   a word of brand.subtype is a word of the reference's archetype label. The label is a hand annotation
                in the blueprint, so this is worth little.

Which principles apply (`applies`, a list of principle ids)
  A principle of a reference applies to a brand when the brand asks for it or owns what it takes:
  - its temper tag is in brand.temper;
  - dark-page, when brand.mode is dark;
  - image-led, portrait-media, landscape-media, full-bleed-media, when the brand's stills cover the reference's need
    and there is at least one;
  - type-led, when the brand has no stills;
  - video-first-section, when the brand has a video.
  Principles about type and page length ask nothing of a brand's assets, so they are in the card but never the
  reason a reference is let in.

Who is eligible
  - A reference whose status is `authored` is never returned: it is a recipe, not evidence.
  - A reference of the brand's own kind is always eligible; an unmet need lowers its score and is named in `gaps`.
  - A reference of another kind is eligible only when the brand can meet its image need (need ≤ supply) and at
    least one of its principles applies. Retrieval is by fit, not by class.

Order: score, highest first; ties by id. Scores are rounded to two places before sorting, so the order is stable.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REFERENCES = os.path.join(HERE, 'references')
WEIGHTS = {'kind': 40, 'imagery': 30, 'temper': 10, 'mode': 10, 'video': 5, 'subtype': 5}
SUPPLY_CAP = 8
KINDS = ('place', 'service', 'software', 'product')
# The temper vocabulary: one tag per principle rule in build.py (a test keeps the two lists equal).
TEMPER_TAGS = ('high-contrast-type', 'even-type', 'light-weight', 'heavy-weight', 'uppercase', 'tight-tracking', 'tight-leading',
               'one-family', 'asymmetric', 'full-bleed', 'portrait-imagery', 'landscape-imagery', 'image-led', 'type-led',
               'video-led', 'pinned', 'dark', 'long', 'compact')


def load_records(folder=None):
    folder = folder or REFERENCES; out = []
    for name in sorted(os.listdir(folder)):
        if name.endswith('.json'):
            with open(os.path.join(folder, name), encoding='utf-8') as f: out.append(json.load(f))
    return out


def normalise(brand):
    """The brand as retrieval reads it. Missing fields mean "none" or "no preference"."""
    if not isinstance(brand, dict): raise TypeError('brand must be a dict')
    def count(key):
        v = brand.get(key) or 0
        if isinstance(v, bool) or not isinstance(v, int) or v < 0: raise ValueError('brand.%s must be a non-negative integer' % key)
        return v
    mode = brand.get('mode') if brand.get('mode') in ('light', 'dark') else None
    temper = [t for t in (brand.get('temper') or []) if isinstance(t, str)]
    return {'kind': brand.get('kind'), 'subtype': brand.get('subtype') or None, 'photographs': count('photographs'), 'screenshots': count('screenshots'),
            'has_video': bool(brand.get('has_video')), 'mode': mode, 'temper': sorted(set(temper))}


def _val(node):
    return node['value'] if node else None


def card(rec):
    """The compact DNA card a creative director is given: what was measured, what it adds up to, what is missing."""
    typ = rec['typography']; comp = rec['composition']; s = comp['summary']; im = rec['imagery']
    def level(x):
        return None if not x else {k: x[k] for k in ('source_face', 'delivery_face', 'px', 'weight', 'tracking', 'leading', 'case')}
    return {
        'id': rec['id'], 'status': rec['status'], 'kinds': rec['fits']['kinds'], 'archetype': rec['fits']['archetype'],
        'completeness': rec['completeness'],
        'missing': sorted(k for k, v in rec['completeness'].items() if v == 'missing'),
        'typography': {'display': level(typ['display']), 'h2': level(typ['h2']), 'body': level(typ['body']),
                       'display_to_body': _val(typ['ratios']['display_to_body']), 'display_to_h2': _val(typ['ratios']['display_to_h2'])},
        'composition': {'sections': _val(s['sections']), 'page_screens': _val(s['page_screens']), 'pacing': _val(s['pacing']),
                        'surface': comp['surface']['mode'] if comp['surface'] else None,
                        'offset_heading_share': _val(s['offset_heading_share']), 'bleed_section_share': _val(s['bleed_section_share']),
                        'roles': [sec['role'] for sec in comp['sections']],
                        'viewport_width': comp['fraction_base']['basis'] if comp['fraction_base'] else None},
        'imagery': {'image_sections': _val(im['image_sections']), 'portrait_share': _val(im['portrait_share']),
                    'landscape_share': _val(im['landscape_share']), 'video_first_section': _val(im['video_first_section'])},
        'needs': {k: rec['fits']['needs'][k] for k in ('images_min', 'video')} if rec['fits']['needs'] else None,
        'temper': [t['tag'] for t in rec['fits']['temper']],
        'principles': [{'id': p['id'], 'statement': p['statement'], 'confidence': p['confidence']} for p in rec['principles']],
        'caveats': [c['code'] for c in rec['evidence']['caveats']],
    }


def _n(x):
    return ('%.2f' % x).rstrip('0').rstrip('.')


def score(brand, rec):
    """(components, reasons, gaps) for one eligible record. reasons name what matched, gaps what did not."""
    b = brand; fits = rec['fits']; needs = fits['needs']; comp = {}; why = []; gaps = []
    kinds = fits['kinds']
    if b['kind'] in kinds:
        comp['kind'] = float(WEIGHTS['kind']); why.append('kind: a %s reference for a %s brand (+%s)' % ('/'.join(kinds), b['kind'], _n(comp['kind'])))
    else:
        comp['kind'] = 0.0; gaps.append('kind: a %s reference, the brand is %s' % ('/'.join(kinds), b['kind']))

    need = needs['images_min']; supply = b['photographs'] + b['screenshots']
    if need > supply:
        frac = (supply + 1) / (need + 1)
        gaps.append('imagery: %d sections hold a large still, the brand has %d' % (need, supply))
    else:
        frac = 1 - 0.5 * (min(supply, SUPPLY_CAP) - min(need, SUPPLY_CAP)) / SUPPLY_CAP
    comp['imagery'] = round(WEIGHTS['imagery'] * frac, 2)
    if need <= supply:
        why.append('imagery: %d still%s for %d image-bearing section%s (+%s)' % (supply, '' if supply == 1 else 's', need, '' if need == 1 else 's', _n(comp['imagery'])))

    have = {t['tag'] for t in fits['temper']}; asked = b['temper']; shared = [t for t in asked if t in have]
    comp['temper'] = round(WEIGHTS['temper'] * len(shared) / len(asked), 2) if asked else 0.0
    if shared: why.append('temper: %s (+%s)' % (', '.join(shared), _n(comp['temper'])))
    if asked and len(shared) < len(asked): gaps.append('temper: not %s' % ', '.join(t for t in asked if t not in have))

    surface = rec['composition']['surface']['mode'] if rec['composition']['surface'] else None
    comp['mode'] = float(WEIGHTS['mode']) if b['mode'] and b['mode'] == surface else 0.0
    if comp['mode']: why.append('mode: a %s page, as asked (+%s)' % (surface, _n(comp['mode'])))
    elif b['mode']: gaps.append('mode: a %s page, the brand asks for %s' % (surface or 'not recorded', b['mode']))

    comp['video'] = float(WEIGHTS['video']) if needs['video'] == b['has_video'] else 0.0
    if comp['video']: why.append('video: %s (+%s)' % ('opens on video and the brand has one' if needs['video'] else 'no video in the first section and none to place', _n(comp['video'])))
    else: gaps.append('video: %s' % ('the first section holds a video, the brand has none' if needs['video'] else 'the brand has a video, the first section holds none'))

    words = {w for w in str(b['subtype'] or '').lower().replace('-', ' ').split() if len(w) > 2}
    label = {w for w in str(fits['archetype'] or '').lower().replace('-', ' ').split() if len(w) > 2}
    hit = sorted(words & label)
    comp['subtype'] = float(WEIGHTS['subtype']) if hit else 0.0
    if hit: why.append('subtype: "%s" is in the archetype label %s (+%s)' % (', '.join(hit), fits['archetype'], _n(comp['subtype'])))
    return comp, why, gaps


IMAGERY_PRINCIPLES = ('image-led', 'portrait-media', 'landscape-media', 'full-bleed-media')


def applies(brand, rec):
    """Ids of the reference's principles that the brand asks for or owns the material for, in record order."""
    need = rec['fits']['needs']['images_min']; supply = brand['photographs'] + brand['screenshots']
    tag_of = {t['principle']: t['tag'] for t in rec['fits']['temper']}; out = []
    for p in rec['principles']:
        pid = p['id']
        if (tag_of.get(pid) in brand['temper']
                or (pid == 'dark-page' and brand['mode'] == 'dark')
                or (pid in IMAGERY_PRINCIPLES and supply >= max(need, 1))
                or (pid == 'type-led' and supply == 0)
                or (pid == 'video-first-section' and brand['has_video'])):
            out.append(pid)
    return out


def eligible(brand, rec):
    if rec['status'] == 'authored' or rec['fits']['needs'] is None: return False
    if brand['kind'] in rec['fits']['kinds']: return True
    return rec['fits']['needs']['images_min'] <= brand['photographs'] + brand['screenshots'] and bool(applies(brand, rec))


def retrieve(brand, k=4, records=None):
    b = normalise(brand); out = []
    for rec in (load_records() if records is None else records):
        if not eligible(b, rec): continue
        comp, why, gaps = score(b, rec)
        out.append({'id': rec['id'], 'score': round(sum(comp.values()), 2), 'components': comp, 'reasons': why, 'gaps': gaps,
                    'applies': applies(b, rec), 'card': card(rec)})
    out.sort(key=lambda r: (-r['score'], r['id']))
    return out[:max(0, int(k))]


def brand_from_job(job_dir):
    """The brand dict from a job folder: direction.json (kind, mode), images.json (what the brand owns), hero.mp4.
    A photograph is an image with data that is not a page screenshot (`shot`), not generated (`gen`), not a crop of
    another image (`crop_of`) and at least 600px wide — the same cut lib/swarm/agents.py makes. A screenshot is an
    image with data that is a `shot` and not a crop."""
    def read(name, default):
        path = os.path.join(job_dir, name)
        if not os.path.isfile(path): return default
        with open(path, encoding='utf-8') as f: return json.load(f)
    direction = read('direction.json', {}) or {}
    images = read('images.json', []) or []
    if isinstance(images, dict): images = list(images.values())
    images = [i for i in images if isinstance(i, dict) and i.get('data') and not i.get('crop_of')]
    photographs = [i for i in images if not i.get('shot') and not i.get('gen') and (i.get('w') or 0) >= 600]
    screenshots = [i for i in images if i.get('shot') and not i.get('gen')]
    return {'kind': direction.get('kind'), 'subtype': None, 'photographs': len(photographs), 'screenshots': len(screenshots),
            'has_video': os.path.isfile(os.path.join(job_dir, 'hero.mp4')),
            'mode': direction.get('mode') if direction.get('mode') in ('light', 'dark') else None, 'temper': []}


def card_text(result):
    """A result as a few plain lines, for a prompt or a terminal."""
    c = result['card']; d = c['typography']['display'] or {}; L = []
    L.append('%s  score %s  (%s, %s)' % (result['id'], _n(result['score']), '/'.join(c['kinds']), c['status']))
    for r in result['reasons']: L.append('  + ' + r)
    for g in result['gaps']: L.append('  - ' + g)
    if result['applies']: L.append('  applies to this brand: ' + ', '.join(result['applies']))
    if d: L.append('  display: %s → ships as %s, %spx, weight %s, tracking %s, leading %s, case %s' % (
        d.get('source_face'), d.get('delivery_face'), d.get('px'), d.get('weight'), d.get('tracking'), d.get('leading'), d.get('case')))
    co = c['composition']
    L.append('  page: %s sections over %s screens, %s surface; pacing %s' % (co['sections'], co['page_screens'], co['surface'], co['pacing']))
    for p in c['principles']: L.append('  · [%s] %s' % (p['confidence'], p['statement']))
    L.append('  not measured: %s%s' % (', '.join(c['missing']) or 'nothing marked missing', ('; caveats: ' + ', '.join(c['caveats'])) if c['caveats'] else ''))
    return '\n'.join(L)


def main(argv):
    usage = 'usage: python3 design_dna/retrieve.py <job dir> [--k N] [--json]'
    k = 4; as_json = False; paths = []; i = 0
    while i < len(argv):
        a = argv[i]
        if a == '--json': as_json = True
        elif a == '--k' and i + 1 < len(argv) and argv[i + 1].isdigit(): k = int(argv[i + 1]); i += 1
        elif a.startswith('--'): paths = []; break
        else: paths.append(a)
        i += 1
    if len(paths) != 1:
        print(usage, file=sys.stderr); return 2
    job = paths[0]
    if not os.path.isdir(job):
        print('not a folder: %s' % job, file=sys.stderr); return 2
    brand = brand_from_job(job); results = retrieve(brand, k)
    if as_json:
        print(json.dumps({'brand': brand, 'results': results}, indent=1, sort_keys=True, ensure_ascii=False)); return 0
    print('brand: ' + json.dumps(brand, sort_keys=True))
    for r in results: print(); print(card_text(r))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
