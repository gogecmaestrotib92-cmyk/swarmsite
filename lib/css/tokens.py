"""tokens.py — emit CSS :root tokens for a concept + mode + brand accent.
Usage: python3 tokens.py C1 dark '#10B981'  > tokens.css"""
import json, sys, os

FONT_LINKS = {
    "Space Grotesk": "Space+Grotesk:wght@300..700", "Instrument Sans": "Instrument+Sans:wght@400..700", "JetBrains Mono": "JetBrains+Mono:wght@400;500",
    "Geist Mono": "Geist+Mono:wght@400;500", "IBM Plex Mono": "IBM+Plex+Mono:wght@400;500", "Archivo": "Archivo:wght@400..900",
    "Bricolage Grotesque": "Bricolage+Grotesque:wght@400..800", "Manrope": "Manrope:wght@400..700", "Syne": "Syne:wght@400..800",
    "Fraunces": "Fraunces:opsz,wght@9..144,300..700", "Barlow Condensed": "Barlow+Condensed:wght@600;700;800",
}

def contrast_text(hexc):
    h = hexc.lstrip('#'); r, g, b = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    return '#0B0B0B' if (0.2126 * r + 0.7152 * g + 0.0722 * b) > 0.45 else '#FFFFFF'

def tokens(concept_id, mode, accent, display_override=None):
    lib = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'concepts', 'concepts.json')))
    c = lib['concepts'][concept_id]
    m = c['modes'].get(mode) or next(iter(c['modes'].values()))
    f = dict(c['fonts']);
    if display_override: f['display'] = display_override
    t = c['type']
    fonts = sorted({f['display'], f['body'], f['mono']})
    link = "https://fonts.googleapis.com/css2?" + "&".join("family=" + FONT_LINKS[x] for x in fonts if x in FONT_LINKS) + "&display=swap"
    css = f""":root{{
  --paper:{m.get('paper')}; --ink:{m.get('ink')}; --muted:{m.get('muted', 'color-mix(in srgb,' + m.get('ink') + ' 55%,transparent)')};
  --line:{m.get('line', 'color-mix(in srgb,' + m.get('ink') + ' 14%,transparent)')}; --grid:{m.get('grid', 'color-mix(in srgb,' + m.get('ink') + ' 8%,transparent)')};
  --panel:{m.get('panel', m.get('card', 'color-mix(in srgb,' + m.get('paper') + ' 85%,' + m.get('ink') + ')'))};
  --accent:{accent}; --accent-ink:{accent}; --accent-contrast:{contrast_text(accent)}; --mv-highlight:{accent};
  --font-display:'{f['display']}',system-ui,sans-serif; --font-body:'{f['body']}',system-ui,sans-serif; --font-mono:'{f['mono']}',ui-monospace,monospace;
  --display-weight:{c.get('fonts', {}).get('display_weight', 600)}; --h1:{t['h1']}; --h1-lh:{t['h1_lh']}; --h1-tt:{t['h1_tt']}; --h2:{t['h2']};
  --label-size:11px; --radius:{c.get('radius', '2px').split(' ')[0]}; --grain:{c.get('texture', {}).get('paper_grain', c.get('texture', {}).get('grain', c.get('texture', {}).get('film_grain', 0)))};
  --gutter:clamp(20px,4vw,56px); --max:1360px;
}}"""
    return css, link, c

if __name__ == '__main__':
    css, link, c = tokens(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
    print('/* ' + c['name'] + ' */'); print('/* fonts: ' + link + ' */'); print(css)
