"""palette.py — colour as a WORLD, not an accent.
From one hue (any hex) + concept + mode, derive the full token set in OKLCH so every surface carries the hue:
paper (tinted), paper-2, ink (hue-darkened, never pure black), ink-soft, muted, line, grid, panel,
accent, accent-ink (text-safe version of the accent), accent-soft, accent-surface, photo-tint, chart-1/2, pos/neg.
Every pair is contrast-checked; the accent is pushed in lightness until it passes on its paper.
Each concept has a colour_weight: how much of the page is colour (C3 flat: surfaces; C1: 5% accent; C6: monochrome).
Usage: python3 lib/colour/palette.py '#E63946' C1 dark"""
import json, math, sys

# ---------- sRGB <-> OKLCH ----------
def _srgb_to_lin(c): return c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4
def _lin_to_srgb(c): c = max(0, min(1, c)); return 12.92 * c if c <= .0031308 else 1.055 * c ** (1 / 2.4) - .055
def hex_to_oklch(h):
    h = h.lstrip('#'); r, g, b = [_srgb_to_lin(int(h[i:i+2], 16) / 255) for i in (0, 2, 4)]
    l = .4122214708 * r + .5363325363 * g + .0514459929 * b; m = .2119034982 * r + .6806995451 * g + .1073969566 * b; s = .0883024619 * r + .2817188376 * g + .6299787005 * b
    l, m, s = l ** (1/3), m ** (1/3), s ** (1/3)
    L = .2104542553 * l + .7936177850 * m - .0040720468 * s; a = 1.9779984951 * l - 2.4285922050 * m + .4505937099 * s; bb = .0259040371 * l + .7827717662 * m - .8086757660 * s
    C = math.hypot(a, bb); H = math.degrees(math.atan2(bb, a)) % 360
    return L, C, H
def oklch_to_hex(L, C, H):
    a = C * math.cos(math.radians(H)); bb = C * math.sin(math.radians(H))
    l = L + .3963377774 * a + .2158037573 * bb; m = L - .1055613458 * a - .0638541728 * bb; s = L - .0894841775 * a - 1.2914855480 * bb
    l, m, s = l ** 3, m ** 3, s ** 3
    r = 4.0767416621 * l - 3.3077115913 * m + .2309699292 * s; g = -1.2684380046 * l + 2.6097574011 * m - .3413193965 * s; b = -.0041960863 * l - .7034186147 * m + 1.7076147010 * s
    return '#%02X%02X%02X' % tuple(round(_lin_to_srgb(x) * 255) for x in (r, g, b))
def in_gamut(L, C, H):
    a = C * math.cos(math.radians(H)); bb = C * math.sin(math.radians(H))
    l = (L + .3963377774 * a + .2158037573 * bb) ** 3; m = (L - .1055613458 * a - .0638541728 * bb) ** 3; s = (L - .0894841775 * a - 1.2914855480 * bb) ** 3
    r = 4.0767416621 * l - 3.3077115913 * m + .2309699292 * s; g = -1.2684380046 * l + 2.6097574011 * m - .3413193965 * s; b = -.0041960863 * l - .7034186147 * m + 1.7076147010 * s
    return all(-.001 <= x <= 1.001 for x in (r, g, b))
def clamp_chroma(L, C, H):
    while C > 0 and not in_gamut(L, C, H): C -= .004
    return max(C, 0)
def ok(L, C, H): return oklch_to_hex(L, clamp_chroma(L, C, H), H)

def lum(hexc):
    h = hexc.lstrip('#'); r, g, b = [_srgb_to_lin(int(h[i:i+2], 16) / 255) for i in (0, 2, 4)]
    return .2126 * r + .7152 * g + .0722 * b
def contrast(a, b): la, lb = lum(a), lum(b); return (max(la, lb) + .05) / (min(la, lb) + .05)

def text_safe(accent_L, C, H, paper, dark, target=4.5):
    """move the accent's lightness away from the paper until it reads as text"""
    L = accent_L
    for _ in range(60):
        hx = ok(L, C, H)
        if contrast(hx, paper) >= target: return hx
        L += .015 if dark else -.015
        if not 0.05 < L < 0.98: break
    return ok(L, C, H)

# ---------- per-concept colour weight & roles ----------
CONCEPTS = {
    # weight: how much hue goes into paper/ink; accent_use: where the accent is allowed
    'C1': dict(weight='low', paper_tint=.012, ink_tint=.03, accent_use=['one word', 'primary button', 'chart', 'photo duotone'], surfaces=0),
    'C2': dict(weight='mid', paper_tint=.0, ink_tint=.02, accent_use=['cells', 'highlight blocks'], surfaces=.2),
    'C3': dict(weight='high', paper_tint=.02, ink_tint=.0, accent_use=['cards', 'hero card', 'footer ground'], surfaces=.6, flat_set=True),
    'C4': dict(weight='mid', paper_tint=.02, ink_tint=.0, accent_use=['surface blocks'], surfaces=.3, pastel=True),
    'C5': dict(weight='low', paper_tint=.006, ink_tint=.0, accent_use=['primary button', 'links'], surfaces=0),
    'C6': dict(weight='mono', paper_tint=.0, ink_tint=.0, accent_use=['none — the ink is the accent'], surfaces=0),
    'C7': dict(weight='low', paper_tint=.02, ink_tint=.0, accent_use=['gradient on one word', 'glow'], surfaces=0),
    'C8': dict(weight='high', paper_tint=.03, ink_tint=.04, accent_use=['everything — it is a world'], surfaces=.5),
}

def palette(hexc, concept='C1', mode='dark'):
    L0, C0, H = hex_to_oklch(hexc); C0 = max(C0, .08)
    cfg = CONCEPTS.get(concept, CONCEPTS['C1']); dark = mode == 'dark'
    pt, it = cfg['paper_tint'], cfg['ink_tint']
    if cfg['weight'] == 'mono': pt = it = 0
    if dark:
        paper = ok(.17, pt * 1.6, H); paper2 = ok(.21, pt * 1.6, H); panel = ok(.23, pt * 1.8, H)
        ink = ok(.95, it * .4, H); ink_soft = ok(.80, it * .5, H); muted = ok(.62, it * .6, H)
        line = ok(.30, pt * 1.5, H); grid = ok(.24, pt * 1.5, H)
        accent = ok(max(L0, .62), C0, H)                      # readable on dark paper
    else:
        paper = ok(.965, pt, H); paper2 = ok(.94, pt * 1.2, H); panel = ok(.99, pt * .5, H) if cfg['weight'] != 'high' else ok(.985, pt * .8, H)
        ink = ok(.22, it, H); ink_soft = ok(.36, it, H); muted = ok(.55, it * .8, H)
        line = ok(.86, pt * 1.5, H); grid = ok(.90, pt * 1.5, H)
        accent = ok(min(L0, .70) if C0 > .12 else L0, C0, H)
    accent_ink = text_safe(hex_to_oklch(accent)[0], C0, H, paper, dark, 4.5)
    accent_contrast = '#0B0B0B' if lum(accent) > .28 else '#FFFFFF'
    accent_soft = ok(.30 if dark else .92, C0 * .5, H)
    accent_surface = ok(.26 if dark else .95, C0 * .35, H)
    photo_tint = ok(.45 if dark else .60, C0 * .9, H)
    chart2 = ok(.70 if dark else .55, C0 * .6, (H + 150) % 360)
    pos = accent_ink
    neg_h = 28 if min(abs(H - 28), 360 - abs(H - 28)) > 45 else 75   # warm red, unless the brand IS red → amber
    neg = text_safe(.62 if dark else .50, .17, neg_h, paper, dark, 4.5)
    flat = [ok(.80, .17, (H + k) % 360) for k in (0, 60, 150, 230)] if cfg.get('flat_set') else []
    pastel = [ok(.90, .12, H), ok(.90, .10, (H + 60) % 360), ok(.88, .10, (H + 200) % 360)] if cfg.get('pastel') else []
    tokens = dict(paper=paper, paper2=paper2, panel=panel, ink=ink, ink_soft=ink_soft, muted=muted, line=line, grid=grid,
                  accent=accent, accent_ink=accent_ink, accent_contrast=accent_contrast, accent_soft=accent_soft, accent_surface=accent_surface,
                  photo_tint=photo_tint, chart1=accent_ink, chart2=chart2, pos=pos, neg=neg)
    checks = {'ink/paper': round(contrast(ink, paper), 1), 'muted/paper': round(contrast(muted, paper), 1), 'accent_ink/paper': round(contrast(accent_ink, paper), 1),
              'accent_contrast/accent': round(contrast(accent_contrast, accent), 1), 'neg/paper': round(contrast(neg, paper), 1)}
    return dict(hue=round(H), chroma=round(C0, 3), concept=concept, mode=mode, weight=cfg['weight'], accent_use=cfg['accent_use'], surfaces=cfg['surfaces'],
                tokens=tokens, flat_set=flat, pastel=pastel, checks=checks)

def css(p, selector=':root'):
    t = p['tokens']
    return (f"{selector}{{--paper:{t['paper']};--paper-2:{t['paper2']};--panel:{t['panel']};--ink:{t['ink']};--ink-soft:{t['ink_soft']};--muted:{t['muted']};--line:{t['line']};--grid:{t['grid']};"
            f"--accent:{t['accent']};--accent-ink:{t['accent_ink']};--accent-contrast:{t['accent_contrast']};--accent-soft:{t['accent_soft']};--accent-surface:{t['accent_surface']};"
            f"--photo-tint:{t['photo_tint']};--chart-1:{t['chart1']};--chart-2:{t['chart2']};--pos:{t['pos']};--neg:{t['neg']};--mv-highlight:{t['accent']}}}")

if __name__ == '__main__':
    p = palette(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else 'C1', sys.argv[3] if len(sys.argv) > 3 else 'dark')
    print(json.dumps(p, indent=1)); print(css(p))
