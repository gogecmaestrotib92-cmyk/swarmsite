"""normalize.py — raw measurement → clean blueprint the renderer can build from.
Usage: python3 lib/blueprint/normalize.py            (all raw/*.json → <slug>.bp.json)
A blueprint is FORM only: grid, type scale, colour relationships, media treatment, buttons, motion, and the
ordered list of section roles with their measured parameters. Content never lives here."""
import json, os, re, glob, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
RAW = os.path.join(ROOT, 'lib/blueprints/raw'); OUT = os.path.join(ROOT, 'lib/blueprints')

def px(v, d=None):
    try: return int(round(float(str(v).replace('px', ''))))
    except Exception: return d

def tracking(ls, size):
    """letter-spacing → em (so it scales with the client's sizes)."""
    if not ls or ls in ('normal',): return 0
    s = str(ls)
    if s.endswith('%'): return round(float(s[:-1]) / 100, 3)
    v = px(s, 0); return round(v / max(1, size), 3)

def role_of(sec):
    r = sec.get('role')
    if r: return r
    return 'hero' if sec.get('i') == 1 else 'section'

def type_roles(raw):
    """Pick display / h2 / h3 / body / label from heads+paras+scale (largest = display, etc.)."""
    heads = [h for s in raw['sections'] for h in s.get('heads', []) if h.get('px')]
    paras = [p for s in raw['sections'] for p in s.get('paras', []) if p.get('px')]
    labels = [l for s in raw['sections'] for l in s.get('labels', []) if l.get('px')]
    def T(h): return {'fam': h.get('fam'), 'px': h.get('px'), 'w': int(str(h.get('w', 400)).split()[0]) if str(h.get('w', '400')).split()[0].isdigit() else 400, 'ls': tracking(h.get('ls'), h.get('px', 16)), 'lh': float(h.get('lh', 1.1)) if str(h.get('lh', '1.1')) != 'NaN' else 1.0, 'tt': h.get('tt') if h.get('tt') in ('uppercase',) else None, 'it': h.get('it') == 'italic' or 'italic' in str(h.get('w', '')), 'al': h.get('al')}
    heads.sort(key=lambda h: -h['px'])
    display = T(heads[0]) if heads else None
    h2s = [h for h in heads if 28 <= h['px'] < (display['px'] if display else 999)]
    h2 = T(h2s[0]) if h2s else display
    h3s = [h for h in heads if 16 <= h['px'] < (h2['px'] if h2 else 40)]
    h3 = T(h3s[0]) if h3s else None
    body = None
    if paras:
        paras.sort(key=lambda p: -p.get('words', 0)); body = {'fam': paras[0].get('fam'), 'px': paras[0]['px'], 'lh': float(paras[0].get('lh', 1.4)), 'maxw': paras[0].get('maxw')}
    label = None
    if labels: label = {'fam': labels[0].get('fam'), 'px': labels[0]['px'], 'ls': tracking(labels[0].get('ls'), labels[0]['px']), 'tt': 'uppercase'}
    else:
        small = [h for h in heads if h['px'] <= 16 and h.get('tt') == 'uppercase']
        if small: label = {'fam': small[0].get('fam'), 'px': small[0]['px'], 'ls': tracking(small[0].get('ls'), small[0]['px']), 'tt': 'uppercase'}
    return {'display': display, 'h2': h2, 'h3': h3, 'body': body, 'label': label}

def colour_roles(raw):
    pal = [p for p in raw.get('palette', []) if p.get('h')]
    def lum(h):
        h = h.lstrip('#'); r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16); return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
    pal.sort(key=lambda p: -p.get('share', 0))
    paper = pal[0]['h'] if pal else '#ffffff'
    dark = [p['h'] for p in pal if lum(p['h']) < 0.25]; light = [p['h'] for p in pal if lum(p['h']) > 0.75]
    ink = next((p['ink'] for p in raw.get('palette', []) if p.get('ink') and str(p['ink']).startswith('#')), None) or (dark[0] if dark else '#111111')
    accent = next((p['h'] for p in pal if 0.2 < lum(p['h']) < 0.8 and p['h'] not in (paper, ink)), None)
    mode = 'dark' if lum(paper) < 0.3 else 'light'
    bands = [('dark' if s.get('bg') and lum(s['bg']) < 0.3 else 'light' if s.get('bg') else 'paper') for s in raw['sections']]
    return {'paper': paper, 'ink': ink, 'accent': accent, 'mode': mode, 'bands': bands, 'alt': light[1] if mode == 'light' and len(light) > 1 else (dark[1] if mode == 'dark' and len(dark) > 1 else None)}

def media_roles(raw):
    imgs = [i for s in raw['sections'] for i in s.get('imgs', []) if i.get('w') and i.get('h')]
    radii = [px(i.get('br'), 0) for i in imgs if i.get('br') and 'px' in str(i.get('br'))]
    aspects = sorted({round(i['w'] / i['h'], 2) for i in imgs if i['w'] > 150 and i['h'] > 100})
    bleed = any(i.get('bleed') for i in imgs)
    return {'radius': max(set(radii), key=radii.count) if radii else 0, 'aspects': aspects[:8], 'bleed': bleed, 'video_hero': any(i.get('tag') == 'VIDEO' for i in raw['sections'][0].get('imgs', [])) if raw['sections'] else False}

def button_roles(raw):
    b = next((b for s in raw['sections'] for b in s.get('btns', []) if b.get('h') and 30 <= b['h'] <= 70), None)
    if not b: return {'h': 48, 'pad': '0 20px', 'radius': 999, 'px': 15, 'w': 500, 'tt': None}
    br = b.get('br', '0'); radius = 999 if ('e+' in str(br) or px(br, 0) > 60 or br == 'pill') else px(br, 0)
    return {'h': b['h'], 'pad': b.get('pad', '0 20px'), 'radius': radius, 'px': b.get('px', 15), 'w': int(b.get('w', 500)) if str(b.get('w', '500')).isdigit() else 500, 'tt': b.get('tt') if b.get('tt') == 'uppercase' else None, 'filled': bool(b.get('bg'))}

def motion_roles(raw):
    m = raw.get('motion', {}); tr = m.get('transitions', [])
    eases = re.findall(r'cubic-bezier\([^)]+\)', ' '.join(tr)); ease = max(set(eases), key=eases.count) if eases else 'cubic-bezier(0.2,0.8,0.2,1)'
    durs = [float(x) for x in re.findall(r'(\d*\.?\d+)s', ' '.join(tr))]; slow = max([d for d in durs if d <= 2.5], default=0.8); fast = min([d for d in durs if d >= 0.15], default=0.3)
    return {'smooth': bool(m.get('libs', {}).get('lenis')), 'ease': ease, 'fast': fast, 'slow': slow, 'cursor': bool(m.get('customCursor')), 'idea': m.get('note', '')}

def section_params(sec, vh, W=1440):
    r = sec.get('rect', {}); h = r.get('h') or int(sec.get('screens', 1) * vh)
    heads = sec.get('heads', []); h0 = heads[0] if heads else {}
    hr = h0.get('rect', {})
    out = {'role': role_of(sec), 'screens': round(h / vh, 2), 'pad': sec.get('pad'), 'band': 'dark' if sec.get('bg') and sec['bg'] < '#444444' else ('alt' if sec.get('bg') else None)}
    if h0:
        out['head'] = {'px': h0.get('px'), 'w': int(str(h0.get('w', 400)).split()[0]) if str(h0.get('w', '400')).split()[0].isdigit() else 400, 'tt': h0.get('tt') if h0.get('tt') == 'uppercase' else None, 'it': h0.get('it') == 'italic', 'al': h0.get('al') or 'start', 'lh': float(h0.get('lh', 1.05)) if str(h0.get('lh', '1')) != 'NaN' else 1.0,
                       'x': round(hr.get('x', 0) / W, 3) if hr else None, 'y': round((hr.get('y', 0) - r.get('y', 0)) / max(1, h), 3) if hr and r else None, 'wf': round(hr.get('w', W) / W, 3) if hr else None, 'ls': tracking(h0.get('ls'), h0.get('px', 16))}
    if sec.get('paras'): p = sec['paras'][0]; out['body'] = {'px': p.get('px'), 'lh': float(p.get('lh', 1.4)), 'maxw': p.get('maxw')}
    ims = [i for i in sec.get('imgs', []) if i.get('w') and i.get('h') and i['w'] > 100]
    if ims: out['media'] = [{'ar': round(i['w'] / i['h'], 2), 'wf': round(i['w'] / W, 3), 'xf': round((i.get('x', 0)) / W, 3), 'bleed': bool(i.get('bleed')), 'video': i.get('tag') == 'VIDEO', 'radius': px(i.get('br'), 0) if 'px' in str(i.get('br', '')) else 0} for i in ims[:4]]
    if sec.get('lefts'): out['cols'] = [round(x / W, 3) for x in sec['lefts'] if 0 <= x < W][:5]
    if sec.get('note'): out['note'] = sec['note']
    if sec.get('words'): out['words'] = sec['words']
    return out

def normalize(path):
    raw = json.load(open(path)); slug = os.path.splitext(os.path.basename(path))[0]
    vh = raw.get('vh', 756); W = raw.get('vw', 1440)
    bp = {'id': slug, 'source': raw.get('url'), 'class': raw.get('class', 'unknown'), 'archetype': raw.get('archetype', ''), 'screens': raw.get('screens'),
          'grid': {'frame': raw.get('frame', raw.get('gutter', 40)), 'gutter': raw.get('gutter', 40), 'container': raw.get('container', (raw.get('maxw') or [1300])[0]), 'col': raw.get('col')},
          'type': type_roles(raw), 'colour': colour_roles(raw), 'media': media_roles(raw), 'button': button_roles(raw), 'motion': motion_roles(raw),
          'nav': {k: raw.get('nav', {}).get(k) for k in ('pos', 'h', 'links')} if raw.get('nav') else None,
          'sections': [section_params(s, vh, W) for s in raw['sections']]}
    out = os.path.join(OUT, slug + '.bp.json'); json.dump(bp, open(out, 'w'), indent=1, ensure_ascii=False); return bp

if __name__ == '__main__':
    files = sys.argv[1:] or sorted(glob.glob(os.path.join(RAW, '*.json')))
    for f in files:
        bp = normalize(f); t = bp['type']
        print(f"{bp['id']:16} {bp['class']:9} {bp['archetype']:24} display {t['display']['fam'] if t['display'] else '-'} {t['display']['px'] if t['display'] else ''}  body {t['body']['px'] if t['body'] else '-'}  {bp['colour']['mode']}  sections {len(bp['sections'])}  btn r{bp['button']['radius']}  ease {bp['motion']['ease']}")
