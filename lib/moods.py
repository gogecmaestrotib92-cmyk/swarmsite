"""moods.py — curated palettes per kind of business, chosen from the site's own colour DNA.

Structure comes from the house (house.py); colour comes from here. Each mood is a complete system — page paper, ink
(text and the dark band), one accent, one secondary surface — tuned for contrast, in the register the awarded sites
use: one accent on one word, the button and the labels, never a flood. When the owner keeps their colours the
renderer uses their palette verbatim; otherwise the hue of their own accent (buttons, saturated backgrounds)
picks the nearest mood of the blueprint's mode, so a blue brand stays in a blue world without us copying its blue.
"""
import colorsys, re

# paper = page background, ink = text / dark band (repaired for contrast by colour_policy), accent, alt = secondary surface
MOODS = {
    'software': [
        {'id': 'dark-infra', 'mode': 'dark', 'paper': '#0F1320', 'ink': '#0F1320', 'accent': '#FF488B', 'alt': '#172B76'},
        {'id': 'night-cobalt', 'mode': 'dark', 'paper': '#0B0F17', 'ink': '#0B0F17', 'accent': '#4C8DFF', 'alt': '#10203A'},
        {'id': 'terminal', 'mode': 'dark', 'paper': '#0A0F0C', 'ink': '#0A0F0C', 'accent': '#2AF6A0', 'alt': '#10261B'},
        {'id': 'ember', 'mode': 'dark', 'paper': '#120D0B', 'ink': '#120D0B', 'accent': '#FF6A3D', 'alt': '#2A1510'},
        {'id': 'violet', 'mode': 'dark', 'paper': '#0E0B17', 'ink': '#0E0B17', 'accent': '#A78BFA', 'alt': '#1E1537'},
        {'id': 'quiet-light', 'mode': 'light', 'paper': '#FAFAFA', 'ink': '#1A1A1A', 'accent': '#2563EB', 'alt': '#EEF2FF'},
        {'id': 'quiet-lime', 'mode': 'light', 'paper': '#FAFAF7', 'ink': '#161616', 'accent': '#4D7C0F', 'alt': '#F1F5E6'},
        {'id': 'quiet-rose', 'mode': 'light', 'paper': '#FCFAFA', 'ink': '#1A1416', 'accent': '#BE185D', 'alt': '#FBE7EF'},
        {'id': 'quiet-amber', 'mode': 'light', 'paper': '#FBFAF7', 'ink': '#1C1A14', 'accent': '#B45309', 'alt': '#FAF0DC'},
    ],
    'place': [
        {'id': 'warm-paper', 'mode': 'light', 'paper': '#F6F1E7', 'ink': '#1F2A1C', 'accent': '#6B7A2A', 'alt': '#E9E1D0'},
        {'id': 'terracotta', 'mode': 'light', 'paper': '#FBF4EE', 'ink': '#2B1A14', 'accent': '#C2552D', 'alt': '#F1DED2'},
        {'id': 'sea', 'mode': 'light', 'paper': '#F4F7F8', 'ink': '#0F2A3A', 'accent': '#1B6E8A', 'alt': '#E1ECF0'},
        {'id': 'blush', 'mode': 'light', 'paper': '#FBF1F1', 'ink': '#2A1518', 'accent': '#B23A48', 'alt': '#F3DCDC'},
        {'id': 'saffron', 'mode': 'light', 'paper': '#FBF6EC', 'ink': '#241C10', 'accent': '#B7791F', 'alt': '#F3E7CB'},
        {'id': 'night-dining', 'mode': 'dark', 'paper': '#151311', 'ink': '#151311', 'accent': '#C9A24A', 'alt': '#221E19'},
        {'id': 'night-wine', 'mode': 'dark', 'paper': '#140F12', 'ink': '#140F12', 'accent': '#D06A7A', 'alt': '#22171C'},
    ],
    'service': [
        {'id': 'editorial-ivory', 'mode': 'light', 'paper': '#F7F4EE', 'ink': '#141414', 'accent': '#7A1F2B', 'alt': '#ECE6DA'},
        {'id': 'swiss', 'mode': 'light', 'paper': '#FFFFFF', 'ink': '#0A0A0A', 'accent': '#E4002B', 'alt': '#F2F2F2'},
        {'id': 'dusk', 'mode': 'light', 'paper': '#F3F4F6', 'ink': '#1C2330', 'accent': '#3B5BDB', 'alt': '#E5E8F0'},
        {'id': 'sage', 'mode': 'light', 'paper': '#F4F6F1', 'ink': '#1E2A22', 'accent': '#3E7A5A', 'alt': '#E2E8DC'},
        {'id': 'ochre', 'mode': 'light', 'paper': '#F8F5EE', 'ink': '#1F1B14', 'accent': '#C27C1A', 'alt': '#EFE6D2'},
        {'id': 'graphite', 'mode': 'dark', 'paper': '#161616', 'ink': '#161616', 'accent': '#E8D8B0', 'alt': '#222222'},
        {'id': 'graphite-blue', 'mode': 'dark', 'paper': '#111418', 'ink': '#111418', 'accent': '#7FB3FF', 'alt': '#1B2129'},
    ],
    'product': [
        {'id': 'studio-white', 'mode': 'light', 'paper': '#FFFFFF', 'ink': '#111111', 'accent': '#111111', 'alt': '#F3F3F3'},
        {'id': 'sun', 'mode': 'light', 'paper': '#FFF8EC', 'ink': '#1C1A16', 'accent': '#D98E04', 'alt': '#F7E9C8'},
        {'id': 'coral', 'mode': 'light', 'paper': '#FFF5F2', 'ink': '#1E1512', 'accent': '#E0472B', 'alt': '#FBE0D8'},
        {'id': 'forest', 'mode': 'light', 'paper': '#F2F6F2', 'ink': '#152018', 'accent': '#2E6B3F', 'alt': '#DFE9E0'},
        {'id': 'cobalt', 'mode': 'light', 'paper': '#F4F6FB', 'ink': '#0F1A33', 'accent': '#1D4ED8', 'alt': '#E3E9F7'},
        {'id': 'plum', 'mode': 'light', 'paper': '#FAF5FB', 'ink': '#1D1320', 'accent': '#7E22CE', 'alt': '#EEDFF4'},
        {'id': 'obsidian', 'mode': 'dark', 'paper': '#0D0D0F', 'ink': '#0D0D0F', 'accent': '#FFFFFF', 'alt': '#1A1A1E'},
        {'id': 'obsidian-amber', 'mode': 'dark', 'paper': '#0F0E0C', 'ink': '#0F0E0C', 'accent': '#F5B942', 'alt': '#1C1915'},
    ],
}


def _rgb(c):
    c = str(c or '').strip().split(' ')[0]
    m = re.fullmatch(r'#?([0-9a-fA-F]{6})', c)
    if not m: return None
    h = m.group(1); return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def hsl(c):
    r = _rgb(c)
    if not r: return None
    h, l, s = colorsys.rgb_to_hls(*r)
    return (h * 360, s, l)


def brand_accent(inventory):
    """The site's own accent: the most used saturated colour among its buttons, then its saturated backgrounds."""
    cols = (inventory or {}).get('colors') or {}
    def cands(key):
        out = []
        for it in cols.get(key) or []:
            c = it.get('c') if isinstance(it, dict) else it; n = it.get('n', 1) if isinstance(it, dict) else 1
            if not isinstance(c, str) or ' a' in c: continue  # 'a0' = transparent overlay colour, not a brand colour
            v = hsl(c)
            if v and v[1] >= .35 and .12 <= v[2] <= .85: out.append((n, c, v))
        return sorted(out, reverse=True)
    for key in ('buttons', 'bg', 'text'):
        c = cands(key)
        if c: return c[0][1]
    return None


def site_mode(inventory):
    cols = (inventory or {}).get('colors') or {}
    bgs = [(it.get('n', 1), hsl(it.get('c'))) for it in cols.get('bg') or [] if isinstance(it, dict) and hsl(it.get('c')) and ' a' not in str(it.get('c'))]
    if not bgs: return None
    dark = sum(n for n, v in bgs if v[2] < .4); light = sum(n for n, v in bgs if v[2] >= .4)
    return 'dark' if dark > light else 'light'


def hue_distance(a, b):
    d = abs(a - b) % 360; return min(d, 360 - d)


def choose(kind, inventory=None, mode=None):
    """The mood for this site: same mode as the blueprint, nearest hue to the brand's own accent, else the kind's default."""
    moods = MOODS.get(kind) or MOODS['service']
    mode = mode or site_mode(inventory) or 'light'
    pool = [m for m in moods if m['mode'] == mode] or moods
    accent = brand_accent(inventory)
    chosen = pool[0]; why = 'default'
    if accent:
        h = hsl(accent)[0]
        scored = sorted(pool, key=lambda m: hue_distance(h, hsl(m['accent'])[0]) if hsl(m['accent'])[1] >= .2 else 999)
        best = scored[0]
        if hsl(best['accent'])[1] >= .2 and hue_distance(h, hsl(best['accent'])[0]) <= 45: chosen = best; why = f'brand accent {accent}'
    return {**chosen, 'why': why, 'brand_accent': accent}
