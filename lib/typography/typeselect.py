"""Font + palette selection rules.

select(concept_id, mode, assets, audit) -> dict with display/body/mono fonts,
google-fonts link, accent and paper/ink family, plus a 'why' trail the swarm
HUD can show ("Typography · kept Barlow Condensed (brand font with character)").
"""
import json, os, re
HERE = os.path.dirname(__file__)
FONTS = json.load(open(os.path.join(HERE, 'fonts.json')))
PALETTES = json.load(open(os.path.join(HERE, 'palettes.json')))

SYSTEM = {'system-ui', 'inter', 'arial', 'helvetica', 'roboto', 'open sans', 'montserrat',
          'poppins', 'lato', 'segoe ui', '-apple-system', 'sans-serif', 'nunito', 'raleway'}
CHARACTER = re.compile(r'condensed|serif|mono|display|rounded|grotesk|grotesque|narrow|wide|black', re.I)

def _by_name(n):
    for f in FONTS['fonts']:
        if f['name'].lower() == n.lower():
            return f

def _first(role, concept, exclude=()):
    for f in FONTS['fonts']:
        if role in f['role'] and concept in f['concepts'] and f['source'] == 'google' and f['name'] not in exclude:
            return f
    for f in FONTS['fonts']:
        if role in f['role'] and f['source'] == 'google':
            return f

def _hex_ok(h):
    return bool(h) and re.fullmatch(r'#[0-9a-fA-F]{6}', h)

def _lum(h):
    r, g, b = [int(h[i:i+2], 16)/255 for i in (1, 3, 5)]
    f = lambda c: c/12.92 if c <= .03928 else ((c+.055)/1.055)**2.4
    return .2126*f(r)+.7152*f(g)+.0722*f(b)

def contrast(a, b):
    la, lb = _lum(a), _lum(b)
    return (max(la, lb)+.05)/(min(la, lb)+.05)

def select(concept, mode, assets, audit=None):
    why = []
    fonts = assets.get('fonts', {}) if assets else {}
    brand_display = (fonts.get('display') or '').strip()
    brand_body = (fonts.get('body') or '').strip()

    # --- display ---
    if brand_display and brand_display.lower() not in SYSTEM and CHARACTER.search(brand_display) and _by_name(brand_display):
        display = _by_name(brand_display)
        why.append(f"kept brand display font {display['name']} (has character)")
    elif brand_display and brand_display.lower() not in SYSTEM and CHARACTER.search(brand_display):
        display = {'name': brand_display, 'source': 'client', 'license': 'client-owned', 'pair_body': None, 'pair_mono': None}
        why.append(f"kept client font {brand_display} (self-hosted on their site)")
    else:
        display = _first('display', concept)
        why.append(f"replaced {brand_display or 'default'} display with {display['name']} ({concept} pairing)")

    # --- body ---
    body_name = display.get('pair_body') if display.get('pair_body') not in (None, '—') else None
    if not body_name:
        body_name = _first('body', concept)['name']
    if brand_body and brand_body.lower() in SYSTEM:
        why.append(f"replaced system body ({brand_body}) with {body_name}")
    body = _by_name(body_name) or {'name': body_name}

    # --- mono ---
    mono_name = display.get('pair_mono') or _first('mono', concept)['name']
    mono = _by_name(mono_name)

    # --- palette ---
    pal = next((p for p in PALETTES['palettes'] if p['concept'] == concept and p['mode'] == mode), None) \
        or next(p for p in PALETTES['palettes'] if p['concept'] == concept)
    accent = (assets or {}).get('palette', {}).get('brandAccent')
    if _hex_ok(accent):
        c = contrast(accent, pal['paper'])
        if c >= 3:
            why.append(f"kept brand accent {accent} ({c:.1f}:1 on paper)")
            accent_on_text = True
        else:
            why.append(f"brand accent {accent} only {c:.1f}:1 on paper → surfaces only, no accent text")
            accent_on_text = False
    else:
        accent = pal['accent'] or pal['ink']
        accent_on_text = True
        why.append(f"no usable brand accent → palette accent {accent}")

    gf = [n for n in (display['name'], body['name'], mono['name']) if _by_name(n) and _by_name(n)['source'] == 'google']
    link = 'https://fonts.googleapis.com/css2?' + '&'.join(
        'family=' + n.replace(' ', '+') + ':wght@300;400;500;600;700;800' for n in gf) + '&display=swap'

    return {
        'display': display['name'], 'body': body['name'], 'mono': mono['name'],
        'display_license': display.get('license'), 'fonts_link': link,
        'paper': pal['paper'], 'ink': pal['ink'], 'muted': pal['muted'], 'line': pal['line'], 'panel': pal['panel'],
        'accent': accent, 'accent_on_text': accent_on_text, 'palette_id': pal['id'], 'why': why,
    }

if __name__ == '__main__':
    import sys
    a = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else {}
    print(json.dumps(select(sys.argv[1], sys.argv[2], a), indent=2))
