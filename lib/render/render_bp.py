"""render_bp.py — build a page from a BLUEPRINT (form, measured from a winner) + DIRECTION (the client's content).
Usage: python3 lib/render/render_bp.py out/<slug> <blueprint-id> [out.html]
The blueprint decides: grid, type scale, colour relationships, media treatment, buttons, motion, section order + sizes.
The direction decides: every word, every image, the brand (font/colours/logo per the owner's brief)."""
import json, os, re, sys, html as H, base64
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'lib/colour'))
from palette import palette as mkpal

e = lambda s: H.escape(str(s if s is not None else ''), quote=True)

# Commercial faces in the winners → Google equivalents with the same stance (weight/width/mood), so the measured sizes still work.
FONT_MAP = {
    'diegrotesk': ('Instrument Sans', 'sans'), 'abc favorit': ('Inter Tight', 'sans'), 'suisse intl': ('Inter Tight', 'sans'), 'suisse intl mono': ('JetBrains Mono', 'mono'),
    'twkeverett': ('Instrument Sans', 'sans'), 'aeonik': ('Instrument Sans', 'sans'), 'abcplus': ('Instrument Sans', 'sans'), 'abcdiatype': ('JetBrains Mono', 'mono'),
    'pp fragment': ('Cormorant Garamond', 'serif'), 'editorialold': ('Instrument Serif', 'serif'), 'cardinal classic long': ('Instrument Serif', 'serif'),
    'inter': ('Inter Tight', 'sans'), 'inter tight': ('Inter Tight', 'sans'), 'work sans': ('Work Sans', 'sans'), 'oswald': ('Oswald', 'sans'),
    'mouse memoirs': ('Mouse Memoirs', 'sans'), 'modak': ('Modak', 'sans'), 'geistmono': ('JetBrains Mono', 'mono'), 'bt grotesk': ('Instrument Sans', 'sans'),
    'helvetica now display': ('Inter Tight', 'sans'), 'garamond narrow': ('Cormorant Garamond', 'serif'),
}
GF = {'Instrument Sans': 'Instrument+Sans:ital,wght@0,400..700;1,400..700', 'Inter Tight': 'Inter+Tight:ital,wght@0,300..700;1,300..700', 'JetBrains Mono': 'JetBrains+Mono:wght@400;500',
      'Cormorant Garamond': 'Cormorant+Garamond:ital,wght@0,300..700;1,300..700', 'Instrument Serif': 'Instrument+Serif:ital@0;1', 'Work Sans': 'Work+Sans:wght@300..600', 'Oswald': 'Oswald:wght@300..600',
      'Mouse Memoirs': 'Mouse+Memoirs', 'Modak': 'Modak', 'Fraunces': 'Fraunces:ital,opsz,wght@0,9..144,300..700;1,9..144,300..700', 'Bricolage Grotesque': 'Bricolage+Grotesque:opsz,wght@12..96,300..700', 'Space Grotesk': 'Space+Grotesk:wght@300..700'}

def font_for(name, fallback=('Instrument Sans', 'sans')):
    if not name: return fallback
    k = str(name).lower().strip()
    for key, v in FONT_MAP.items():
        if key in k: return v
    if any(w in k for w in ('serif', 'garamond', 'didone', 'editorial', 'fraunces', 'cormorant', 'playfair')): return ('Instrument Serif', 'serif')
    if 'mono' in k: return ('JetBrains Mono', 'mono')
    return (name, 'sans') if name in GF else fallback

def lum(h):
    h = (h or '#888888').lstrip('#'); r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16); return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255

def build(slug_dir, bp_id, out_path=None):
    j = lambda n: json.load(open(os.path.join(slug_dir, n))) if os.path.exists(os.path.join(slug_dir, n)) else None
    d = j('direction.json'); assets = j('assets.json') or {}; brief = j('brief.json') or {}
    images = {i.get('id', str(n)): i for n, i in enumerate(j('images.json') or [])}
    bp = json.load(open(os.path.join(ROOT, 'lib/blueprints', bp_id + '.bp.json')))
    b = d['brand']; h = d['hero']; en = d.get('ending', {})
    T, C, G, M, BT, MO = bp['type'], bp['colour'], bp['grid'], bp['media'], bp['button'], bp['motion']

    # ---- image pool (never an empty frame, never the same picture twice — even as a screenshot of itself or a crop) ----
    used = set()
    def dhash(it):
        try:
            from PIL import Image; import io
            raw = base64.b64decode(it['data'].split(',', 1)[1]); im = Image.open(io.BytesIO(raw)).convert('L').resize((9, 8))
            px = list(im.tobytes()); return ''.join('1' if px[r * 9 + c] > px[r * 9 + c + 1] else '0' for r in range(8) for c in range(8))
        except Exception: return None
    hashes = {k: dhash(i) for k, i in images.items() if i.get('data')}
    def family(k):
        it = images.get(k) or {}; fam = {k}
        if it.get('detail'): return fam  # a detail crop is its own picture
        if it.get('crop_of'): fam.add(it['crop_of'])
        h0 = hashes.get(k)
        if h0:
            for k2, h2 in hashes.items():
                if h2 and not images[k2].get('detail') and sum(a != b for a, b in zip(h0, h2)) <= 10: fam.add(k2)
        return fam
    def is_used(k): return bool(family(k) & used)
    reserved = {}  # image id → beat id that owns it
    for bt0 in d.get('beats', []):
        for k0 in (bt0.get('image'), (bt0.get('ui') or {}).get('lead')):
            if k0 and images.get(k0): reserved.setdefault(k0, bt0['id'])
    if h.get('media') and images.get(h['media']): reserved.setdefault(h['media'], '__hero__')
    def free_for(it, bt=None):
        o = reserved.get(it.get('id'))
        return o is None or (bt is not None and o == bt.get('id')) or (bt is None and o == '__hero__')
    soft = d.get('kind') in ('software', 'product')
    def img(k=None, prefer_hero=False, want_shot=None):
        it = images.get(k) if k else None
        if it and is_used(it.get('id')) and not prefer_hero: it = None
        if not it:
            pool = [i for i in images.values() if i.get('data') and not is_used(i.get('id')) and reserved.get(i.get('id')) is None] or [i for i in images.values() if i.get('data') and not is_used(i.get('id'))] or [i for i in images.values() if i.get('data')]
            if want_shot is True: pool = [i for i in pool if i.get('shot')] or pool
            if want_shot is False: pool = [i for i in pool if not i.get('shot')] or pool
            # hero: real photos first; software bodies: UI section shots first; places: photos first
            pool.sort(key=lambda i: (bool(i.get('shot')) if (prefer_hero or not soft) else not i.get('shot'), not (i.get('heroGrade') if prefer_hero else True), -(i.get('w', 0) * i.get('h', 0)))); it = pool[0] if pool else None
        if not it: return ''
        used.update(family(it.get('id'))); return it.get('data', '')

    # ---- fonts: blueprint stance, owner's font if they keep it ----
    disp_name, disp_kind = font_for((T.get('display') or {}).get('fam'))
    body_name, body_kind = font_for((T.get('body') or {}).get('fam'), ('Inter Tight', 'sans'))
    label_name, _ = font_for((T.get('label') or {}).get('fam'), ('JetBrains Mono', 'mono'))
    if brief.get('keepFont', True) and b.get('keep_font') and b.get('font_hint'):
        disp_name = b['font_hint']; disp_kind = 'serif' if any(w in disp_name.lower() for w in ('serif', 'garamond', 'fraunces', 'cormorant', 'playfair', 'editorial')) else 'sans'
    families = {disp_name, body_name, label_name}
    gf = '&family='.join(GF[f] for f in families if f in GF)
    fonts_link = f'<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family={gf}&display=swap" rel="stylesheet">' if gf else ''

    # ---- colour: owner's palette through the blueprint's relationships ----
    keep_col = brief.get('keepColours', True) and (b.get('accent') or b.get('ink'))
    mode = C.get('mode', 'light')
    seed = (b.get('accent') or b.get('ink') or C.get('accent') or C.get('ink') or '#222222') if keep_col else (C.get('accent') or C.get('ink') or '#222222')
    pal = mkpal(seed, d.get('concept', 'C1'), mode)['tokens']
    paper = (b.get('paper') if keep_col and b.get('paper') else pal['paper']); ink = (b.get('ink') if keep_col and b.get('ink') else pal['ink'])
    if mode == 'dark' and lum(paper) > 0.5: paper, ink = ink, paper
    if mode == 'light' and lum(paper) < 0.5: paper, ink = ink, paper
    accent = pal['accent']
    on_photo = '#F4EFE3'
    # dark band = inverted page
    band_paper, band_ink = (ink, paper)

    # ---- type scale (blueprint px → clamp on vw so it holds on phones) ----
    def clampf(px_, lo_ratio=.45): px_ = px_ or 48; lo = max(28, int(px_ * lo_ratio)); return f'clamp({lo}px,{round(px_ / 14.4, 2)}vw,{px_}px)'
    D = T.get('display') or {'px': 72, 'w': 400, 'ls': -0.02, 'lh': 1.0}; H2 = T.get('h2') or D; H3 = T.get('h3') or {'px': 24, 'w': 500, 'ls': 0, 'lh': 1.2}
    BO = T.get('body') or {'px': 17, 'lh': 1.4, 'maxw': 480}; LB = T.get('label') or {'px': 12, 'ls': .08, 'tt': 'uppercase'}
    display_w = D.get('w', 400) if disp_kind != 'serif' or D.get('w', 400) >= 300 else 400
    if disp_kind == 'serif' and disp_name == 'Instrument Serif': display_w = 400
    tt = lambda t: 'uppercase' if t.get('tt') == 'uppercase' else 'none'

    # ---- sections: allocate content into the blueprint's roles ----
    beats = list(d.get('beats', []))
    statements = []  # sentences a statement section can carry
    for bt in beats:
        if bt['type'] == 'quote' and bt.get('body'): statements.append(('quote', bt))
    lists = [bt for bt in beats if bt['type'] in ('features', 'cells', 'steps', 'ledger', 'facts', 'faq')]
    photos = [bt for bt in beats if bt['type'] == 'photo']
    forms = [bt for bt in beats if bt['type'] == 'form']
    form_id = forms[0]['id'] if forms else 'contact'
    cta_html = lambda light=False: f'<a class="btn{" light" if light else ""}" href="#{e(form_id)}">{e(h.get("cta") or d.get("nav", {}).get("cta") or "Contact")} <span class="ar">→</span></a>'
    lab = lambda t, light=False: f'<span class="lab{" light" if light else ""}">{e(t)}</span>' if t else ''
    pos = {bt['id']: i + 1 for i, bt in enumerate(d.get('beats', []))}
    for bt in d.get('beats', []):
        if bt.get('label'):
            core = re.sub(r'^\s*0?\d{1,2}\s*[/.·—–-]?\s*', '', str(bt['label'])).strip()
            bt['label'] = f"{pos[bt['id']]:02d} — {core}" if core and re.match(r'^\s*0?\d{1,2}\b', str(bt['label'])) else (core or bt['label'])

    def band_of(sec, bt=None):
        return (bt or {}).get('band') or sec.get('band') or 'paper'
    def head_style(sec, key='head', bt=None):
        hd = sec.get(key) or {}; px_ = ((bt or {}).get('ui') or {}).get('h2_px') or hd.get('px') or H2.get('px'); st = [f'font-size:{clampf(px_)}']
        if hd.get('lh'): st.append(f'line-height:{hd["lh"]}')
        if hd.get('tt') == 'uppercase': st.append('text-transform:uppercase')
        if hd.get('it'): st.append('font-style:italic')
        if hd.get('al') in ('center',): st.append('text-align:center;margin-left:auto;margin-right:auto')
        if hd.get('wf'): st.append(f'max-width:{min(100, max(46, round(hd["wf"] * 100 + 2)))}%')
        if hd.get('ls') is not None: st.append(f'letter-spacing:{hd["ls"]}em')
        return ';'.join(st)
    def col_style(sec):
        hd = sec.get('head') or {}; x = hd.get('x') or 0
        return f'margin-left:{round(max(0, x - G["gutter"] / 1440) * 100)}%' if x > 0.3 else ''

    def hero():
        media = sec_media(bp['sections'][0]); light = bool(media)
        vid = os.path.join(slug_dir, 'hero.mp4'); src = img(h.get('media'), True)
        if media and src:
            m = f'<div class="media"><img src="{src}" alt=""></div>' if not os.path.exists(vid) else f'<div class="media"><video autoplay muted loop playsinline poster="{src}"><source src="data:video/mp4;base64,{base64.b64encode(open(vid, "rb").read()).decode()}" type="video/mp4"></video></div>'
        else: m = ''
        hd = bp['sections'][0].get('head') or D
        y = hd.get('y'); place = 'end' if (y or .6) > .5 else 'start'
        al = (h.get('ui') or {}).get('align') or ('center' if hd.get('al') == 'center' else 'start')
        h1 = e(h['h1']).replace('&lt;em&gt;', '<em>').replace('&lt;/em&gt;', '</em>')
        nw = len(re.sub(r'<[^>]+>', '', h['h1']).split()); hpx = hd.get('px') or D.get('px', 72)
        if nw >= 6: hpx = min(hpx, 84)
        if nw >= 8: hpx = min(hpx, 68)
        hui = h.get('ui') or {}; hpx = round(hpx * {'S': .72, 'M': .88, 'L': 1}.get(hui.get('size', ''), 1))
        hsty = head_style(bp['sections'][0]); hsty = re.sub(r'font-size:[^;]+', f'font-size:{clampf(hpx)}', hsty); hsty = re.sub(r'max-width:[^;]+', 'max-width:14ch', hsty); hsty = re.sub(r'text-align:[^;]+;?|margin-(left|right):auto;?', '', hsty) + ';text-wrap:balance' + (';text-align:center;margin-left:auto;margin-right:auto' if al == 'center' else ';text-align:left')
        cat = f'<div class="cat">{lab(h.get("category"), light)}{lab(h.get("fact"), light)}</div>'
        shot = (not media) and d.get('kind') == 'software' and src
        body_ = f'<div class="wrap hero-in al-{al} place-{place}">{cat}<h1 class="h1" style="{hsty}">{h1}</h1><p class="lede{" light" if light else ""}">{e(h.get("lede"))}</p><div class="ctas">{cta_html(light)}{("<a class=\"btn ghost" + (" light" if light else "") + "\" href=\"#" + e(beats[0]["id"] if beats else "") + "\">" + e(h["cta2"]) + "</a>") if h.get("cta2") else ""}</div></div>'
        if not media and src and not hui.get('move') and d.get('kind') in ('place', 'service', 'product') and (images.get(h.get('media')) or {}).get('w', 0) >= 900: hui = {**hui, 'move': 'split'}
        if hui.get('move') == 'split' and src:
            # SIGNATURE split hero: words left, the product right, full height; the product drifts up slower than the page
            hsty2 = re.sub(r'max-width:[^;]+', 'max-width:11ch', hsty)
            left = f'<div class="split-l">{cat}<h1 class="h1" style="{hsty2}">{h1}</h1><p class="lede">{e(h.get("lede"))}</p><div class="ctas">{cta_html()}{("<a class=\"btn ghost\" href=\"#" + e(beats[0]["id"] if beats else "") + "\">" + e(h["cta2"]) + "</a>") if h.get("cta2") else ""}</div></div>'
            right = f'<div class="split-r"><div class="shotframe tall" data-sig="parallax"><img src="{src}" alt=""></div></div>'
            return f'<section class="sec hero split" id="top"><div class="wrap split-wrap">{left}{right}</div></section>'
        if shot: body_ += f'<div class="wrap shotwrap"><div class="shotframe"><img src="{src}" alt=""></div></div>'
        return f'<section class="sec hero{" has-media" if media else ""}{" shot" if shot else ""}" id="top" style="min-height:{min(2, bp["sections"][0].get("screens", 1)) * 100}svh">{m}{body_}</section>'

    def sec_media(sec): return [m for m in sec.get('media', []) if m.get('wf', 0) > .15 and .55 <= m.get('ar', 1) <= 2.6]

    def beat_items(bt):
        t = bt['type']
        if t == 'features': return [(f.get('title'), f.get('body')) for f in bt.get('features', [])]
        if t == 'steps': return [(f'0{i + 1}', x) for i, x in enumerate(bt.get('steps', []))]
        if t == 'cells': return [(c[0] if len(c) < 2 else f'{c[1]} · {c[0]}', c[2] if len(c) > 2 else '') for c in bt.get('cells', [])]
        if t == 'facts': return [(f[0], f[1]) for f in bt.get('facts', [])]
        if t == 'faq': return [(q, a) for q, a in bt.get('items', [])]
        if t == 'ledger': return [(a, p) for a, p in bt.get('items', [])]
        return []

    ZOOMS = [('50% 50%', 1.0), ('30% 35%', 1.6), ('70% 40%', 1.6), ('50% 70%', 1.5), ('25% 65%', 1.7), ('75% 70%', 1.6)]
    def pick_visuals(bt, n, strict=False):
        """Visuals for a multi-frame move. strict (sticky/pinned): only the beat's image, detail crops and commissioned art —
        never an unrelated screenshot; when short, the product image itself returns zoomed to a different region per frame."""
        out_ = []
        if bt.get('image') and images.get(bt['image']) and not is_used(bt['image']) and images[bt['image']].get('w', 0) >= (760 if strict else 500): out_.append((img(bt['image']), ZOOMS[0]))
        pool = [i for i in images.values() if i.get('data') and not is_used(i.get('id')) and free_for(i, bt) and i.get('w', 0) >= (760 if strict else 600) and (not strict or i.get('detail') or i.get('gen'))]
        pool.sort(key=lambda i: (not i.get('detail'), not i.get('gen'), -(i.get('w', 0) * i.get('h', 0))))
        for it in pool:
            if len(out_) >= n: break
            out_.append((img(it['id']), ZOOMS[0]))
        if strict and len(out_) < n:
            base = images.get(h.get('media')) or next((i for i in images.values() if i.get('heroGrade') and i.get('data')), None)
            if base:
                k = 1
                while len(out_) < n and k < len(ZOOMS): out_.append((base['data'], ZOOMS[k])); k += 1
        return out_

    def sticky_product(sec, bt):
        """SIGNATURE: text blocks scroll on the left, the product stays pinned on the right and swaps per block."""
        items = beat_items(bt)[:5]
        if len(items) < 2: return cards(sec, bt)
        vis = pick_visuals(bt, len(items), strict=True)
        if not vis: return cards(sec, bt)
        rows = ''.join(f'<div class="sp-row" data-i="{i}"><span class="lab">{e(f"0{i + 1}")}</span><h3 class="h3">{e(t)}</h3><p>{e(b_)}</p></div>' for i, (t, b_) in enumerate(items))
        frames = ''.join(f'<figure class="sp-f{" on" if i == 0 else ""}" data-i="{i}"><img src="{vis[i % len(vis)][0]}" alt="" style="object-position:{vis[i % len(vis)][1][0]};transform:scale({vis[i % len(vis)][1][1]})"></figure>' for i in range(len(items)))
        return f'<section class="sec sticky band-{band_of(sec, bt)}" id="{e(bt["id"])}" data-sig="sticky"><div class="wrap">{ghead(sec, bt)}<div class="sp"><div class="sp-text">{rows}</div><div class="sp-pin"><div class="sp-stage">{frames}</div></div></div></div></section>'

    def marquee(sec, bt):
        """SIGNATURE: a slow ticker of the beat's own words (titles / facts / prices); doubles as a breath between screens."""
        items = beat_items(bt)
        words_ = [f'{t}' if not b_ or bt['type'] in ('features', 'faq') else f'{t} — {b_}' for t, b_ in items][:10] or [bt.get('h2') or b['name']]
        track = ''.join(f'<span class="mq-i">{e(w)}<i>✦</i></span>' for w in words_)
        head = ghead(sec, bt) if bt.get('h2') else ''
        own = bt.get('image') if bt.get('image') and images.get(bt['image']) and not is_used(bt['image']) and images[bt['image']].get('w', 0) >= 900 else None
        lead = f'<figure class="lead" style="aspect-ratio:{max(1.3, min(2.4, images[own]["w"] / max(1, images[own]["h"])))}"><img src="{img(own)}" alt=""></figure>' if own else ''
        return f'<section class="sec marquee band-{band_of(sec, bt)}" id="{e(bt["id"])}" data-sig="marquee">{("<div class=\"wrap\">" + head + lead + "</div>") if (head or lead) else ""}<div class="mq"><div class="mq-track">{track}{track}</div></div></section>'

    def pinned_sequence(sec, bt):
        """SIGNATURE: the section pins; each step takes over the screen as you scroll (number, sentence, visual)."""
        items = beat_items(bt)[:5]
        if len(items) < 2: return cards(sec, bt)
        vis = pick_visuals(bt, len(items), strict=True)
        slides = ''.join(f'<div class="ps-s{" on" if i == 0 else ""}" data-i="{i}"><div class="ps-t"><b class="num">{e(t) if re.search(r"\d", str(t)) else f"0{i + 1}"}</b><h3 class="h2" style="font-size:var(--h3);max-width:22ch">{e(b_ if re.search(r"\d", str(t)) else t)}</h3>{("<p class=\"lede\">" + e(b_) + "</p>") if not re.search(r"\d", str(t)) and b_ else ""}</div>{("<figure class=\"ps-v\"><img src=\"" + vis[i % len(vis)][0] + "\" alt=\"\" style=\"object-position:" + vis[i % len(vis)][1][0] + ";transform:scale(" + str(vis[i % len(vis)][1][1]) + ")\"></figure>") if vis else ""}</div>' for i, (t, b_) in enumerate(items))
        return f'<section class="sec pinned band-{band_of(sec, bt)}" id="{e(bt["id"])}" data-sig="pinned" data-n="{len(items)}"><div class="ps-sticky"><div class="wrap">{ghead(sec, bt)}<div class="ps-stage">{slides}</div><div class="ps-dots">{"".join("<i></i>" for _ in items)}</div></div></div></section>'

    def type_wall(sec, bt):
        """SIGNATURE: one statement in giant type; the words light up one by one as you scroll through it."""
        text = bt.get('body') if bt['type'] == 'quote' else (bt.get('lede') or bt.get('h2') or '')
        big = bt.get('big') if bt['type'] == 'quote' else bt.get('h2')
        ws = ''.join(f'<span class="tw-w">{e(w)}</span> ' for w in str(text).split()[:48])
        who = f'<p class="lab who">{e(bt["who"])}</p>' if bt.get('who') else ''
        return f'<section class="sec typewall band-{band_of(sec, bt)}" id="{e(bt["id"])}" data-sig="typewall"><div class="tw-sticky"><div class="wrap">{lab(bt.get("label") or big)}<p class="tw">{ws}</p>{who}</div></div></section>'

    def story(sec, bt, flip=False):
        """Text beside a visual, alternating sides; the visual reveals with a clip."""
        if bt['type'] == 'quote': bt = {**bt, 'h2': bt.get('big') or '', 'lede': bt.get('body') or '', 'label': bt.get('label') or bt.get('who') or ''}
        items = beat_items(bt)[:4]
        own = bt.get('image') if bt.get('image') and images.get(bt['image']) and not is_used(bt['image']) and images[bt['image']].get('w', 0) >= 640 else None
        if own: src = img(own)
        else:
            pool = [i for i in images.values() if i.get('data') and not is_used(i.get('id')) and free_for(i, bt) and i.get('w', 0) >= 640 and (i.get('gen') or not i.get('shot'))]
            if bt['type'] in ('facts', 'quote') and not pool: return cards(sec, bt)
            src = img(pool[0]['id']) if pool else ''
        if not src: return cards(sec, bt)
        lst = ''.join(f'<li><b>{e(t)}</b><span>{e(b_)}</span></li>' for t, b_ in items)
        txt = f'<div class="st-t">{lab(bt.get("label"))}<h2 class="h2" style="{re.sub(r"max-width:[^;]+;?", "", head_style(sec, bt=bt))}">{e(bt.get("h2") or "")}</h2>{("<p class=\"lede\">" + e(bt.get("lede")) + "</p>") if bt.get("lede") else ""}<ul class="st-l">{lst}</ul></div>'
        fig = f'<figure class="st-v"><img src="{src}" alt=""></figure>'
        return f'<section class="sec story{" flip" if flip else ""} band-{band_of(sec, bt)}" id="{e(bt["id"])}"><div class="wrap st">{txt}{fig}</div></section>'

    SIG = {'sticky-product': sticky_product, 'marquee': marquee, 'pinned-sequence': pinned_sequence, 'type-wall': type_wall, 'story': story}

    def statement(sec, item):
        kind, bt = item; text = bt.get('body') if kind == 'quote' else bt.get('lede'); big = bt.get('big') if kind == 'quote' else bt.get('h2')
        who = f'<p class="lab who">{e(bt["who"])}</p>' if kind == 'quote' and bt.get('who') else ''
        hd = sec.get('head') or {}; px_ = hd.get('px') or H2['px']
        inner = f'{lab(bt.get("label"))}<h2 class="h2" style="{head_style(sec)}">{e(big)}</h2>' if big and px_ >= 40 else lab(bt.get('label'))
        body_px = (sec.get('body') or {}).get('px') or BO['px']
        centered = (hd.get('al') == 'center')
        return f'<section class="sec statement band-{band_of(sec, bt)}" id="{e(bt["id"])}" style="min-height:{(min(1.0, max(.5, sec.get("screens", .8))) * 100) if len(str(text or "").split()) > 45 else 0}svh"><div class="wrap{" center" if centered else ""}" style="{col_style(sec)}">{inner}<p class="big-p" style="font-size:{clampf(max(body_px, 22), .7)}{";margin-left:auto;margin-right:auto" if centered else ""}">{e(text)}</p>{who}</div></section>'

    def photo_sec(sec, bt=None):
        ms = sec_media(sec) or [{'ar': 1.6, 'wf': 1, 'bleed': True}]
        if len(ms) >= 2 and ms[0].get('wf', 1) < .7:
            tiles = ''.join(f'<figure style="width:{round(m["wf"] * 100)}%;aspect-ratio:{m["ar"]}"><img src="{img(want_shot=False)}" alt=""></figure>' for m in ms[:2])
            cap = f'<p class="cap">{e(bt.get("lede"))}</p>' if bt and bt.get('lede') else ''
            return f'<section class="sec photos band-{sec.get("band") or "paper"}" id="{e(bt["id"]) if bt else ""}"><div class="wrap pair">{tiles}</div>{"<div class=\"wrap\">" + cap + "</div>" if cap else ""}</section>'
        m = ms[0]; bleed = m.get('bleed') or m.get('wf', 1) > .95
        want = bt.get('image') if bt else None
        if want and images.get(want) and images[want].get('w', 0) < 900: want = None  # a photo screen is wrap-wide or wider: never from a small source
        big_pool = [i for i in images.values() if i.get('data') and i.get('w', 0) >= 900 and not is_used(i.get('id'))]
        if not want and not big_pool: bleed = False
        src = img(want, want_shot=(True if (soft and not bleed) else None)) if (want or big_pool) else img(want_shot=None)
        head = f'<div class="wrap over"><h2 class="h2 light" style="{head_style(sec)}">{e(bt["h2"])}</h2></div>' if bt and bt.get('h2') and sec.get('head') else ''
        cap = f'<div class="wrap"><div class="caps">{lab(bt.get("label"))}{("<p class=\"cap\">" + e(bt.get("lede")) + "</p>") if bt and bt.get("lede") else ""}</div></div>' if bt else ''
        return f'<section class="sec photo{" bleed" if bleed else ""}" id="{e(bt["id"]) if bt else ""}"><figure style="aspect-ratio:{max(1.1, min(2.4, m["ar"]))};{"" if bleed else "margin:0 var(--frame);border-radius:var(--radius);overflow:hidden"}"><img src="{src}" alt="">{head}</figure>{cap}</section>'

    def ghead(sec, bt, light=False):
        if not bt.get('h2'): return lab(bt.get('label'))
        st = re.sub(r'max-width:[^;]+;?', '', head_style(sec, bt=bt)); hm = (bt.get('ui') or {}).get('head')
        if hm == 'center': return f'<div class="gh one center">{lab(bt.get("label"), light)}<h2 class="h2" style="{st}">{e(bt.get("h2"))}</h2>{("<p class=\"lede\">" + e(bt.get("lede")) + "</p>") if bt.get("lede") else ""}</div>'
        if hm == 'left': return f'<div class="gh one">{lab(bt.get("label"), light)}<h2 class="h2" style="{st}">{e(bt.get("h2"))}</h2>{("<p class=\"lede\">" + e(bt.get("lede")) + "</p>") if bt.get("lede") else ""}</div>'
        return f'<div class="gh"><div>{lab(bt.get("label"), light)}<h2 class="h2" style="{st}">{e(bt.get("h2"))}</h2></div>{("<p class=\"lede\">" + e(bt.get("lede")) + "</p>") if bt.get("lede") else "<div></div>"}</div>'

    def lead_fig(ui_, bt):
        src = ''; it = None
        if ui_.get('lead') and images.get(ui_['lead']):
            if is_used(ui_['lead']) or images[ui_['lead']].get('w', 0) < 900: return ''  # a lead is a full-width frame: never from a small source
            it = images[ui_['lead']]; src = img(ui_['lead'])
        elif ui_.get('lead') == '': return ''
        elif bt.get('image') and images.get(bt['image']) and not is_used(bt['image']) and images[bt['image']].get('w', 0) >= 900: it = images[bt['image']]; src = img(bt['image'])
        elif bt['type'] == 'facts':
            pool = [i for i in images.values() if i.get('data') and not i.get('shot') and not is_used(i.get('id')) and free_for(i, bt) and i.get('w', 0) >= 600]
            if pool: it = pool[0]; src = img(it['id'])
        elif bt['type'] == 'steps' and soft:
            pool = [i for i in images.values() if i.get('shot') and i.get('data') and not is_used(i.get('id')) and free_for(i, bt)]
            if pool: it = max(pool, key=lambda i: i.get('w', 0) * i.get('h', 0)); src = img(it['id'])
        if not src or not it: return ''
        raw_ar = it.get('w', 16) / max(1, it.get('h', 9)); ar = max(1.0, min(2.4, raw_ar))
        narrow = raw_ar < 1.25  # a portrait or square picture is shown at its own shape, centred, not cropped to a banner
        return f'<figure class="lead{" narrow" if narrow else ""}" style="aspect-ratio:{ar}"><img src="{src}" alt="" style="object-position:{"top" if narrow else "center"}"></figure>'

    def faq(sec, bt):
        rows = ''.join(f'<details><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in bt.get('items', [])[:8])
        bt = dict(bt); bt.setdefault('h2', 'Questions'); bt['h2'] = bt['h2'] or 'Questions'
        return f'<section class="sec faq band-{band_of(sec, bt)}" id="{e(bt["id"])}"><div class="wrap two"><div>{lab(bt.get("label"))}<h2 class="h2" style="{re.sub(r"max-width:[^;]+;?", "", head_style(sec))}">{e(bt["h2"])}</h2>{("<p class=\"lede\">" + e(bt["lede"]) + "</p>") if bt.get("lede") else ""}</div><div class="qa">{rows}</div></div></section>'

    def cards(sec, bt):
        if bt['type'] == 'faq': return faq(sec, bt)
        ms = sec_media(sec); n = max(2, min(4, len(ms) or 3)); ar = (ms[0]['ar'] if ms else 0.82)
        lead = ''; ui_ = bt.get('ui') or {}
        lead = lead_fig(ui_, bt)
        k = len(bt.get('features') or bt.get('cells') or bt.get('steps') or bt.get('facts') or bt.get('items') or [])
        if k in (3, 6, 9): n = 3
        elif k in (2, 4) and n > 2: n = 2 if k == 2 else 4
        elif k == 5: n = 3
        n = ui_.get('cols') or n
        items = []
        if bt['type'] == 'features': items = [(f.get('title'), f.get('body'), True) for f in bt.get('features', [])]
        elif bt['type'] == 'cells': items = [(c[0], c[2] if len(c) > 2 else '', c[1]) for c in bt.get('cells', [])]
        elif bt['type'] == 'steps': items = [(f'0{i + 1}', s, True) for i, s in enumerate(bt.get('steps', []))]
        elif bt['type'] == 'facts': items = [(f[0], f[1], None) for f in bt.get('facts', [])]
        elif bt['type'] == 'faq': items = [(q, a, None) for q, a in bt.get('items', [])]
        elif bt['type'] == 'ledger': return ledger(sec, bt)
        avail = [i for i in images.values() if i.get('data') and not is_used(i.get('id')) and i.get('w', 0) >= 600 and (not i.get('shot') or i.get('detail') or i.get('gen'))]
        with_img = bool(ms) and bt['type'] in ('features', 'steps') and len(avail) >= min(len(items), 3) and not lead
        cells = ''
        for i, (t, body_, num) in enumerate(items[:8]):
            pic = (lambda sr: f'<figure style="aspect-ratio:{ar}"><img src="{sr}" alt=""></figure>' if sr else '')(img()) if with_img and i < len(avail) else ''
            big = f'<b class="num">{e(num)}</b>' if isinstance(num, str) and re.search(r'\d', num) else ''
            cells += f'<div class="card">{pic}{lab(f"0{i + 1}") if not big and bt["type"] != "steps" else ""}{big}<h3 class="h3">{e(t)}</h3><p>{e(body_)}</p></div>'
        return f'<section class="sec cards band-{band_of(sec, bt)}{" compact" if ui_.get("compact") else ""}" id="{e(bt["id"])}"><div class="wrap">{ghead(sec, bt)}{lead}<div class="grid" style="--n:{n}">{cells}</div></div></section>'

    def ledger(sec, bt):
        its = list(bt.get('items', []))
        pri = [x for x in its if re.search(r'\d', str(x[1]))]; rest = [x for x in its if x not in pri]
        its = (pri + rest)[:5]
        rows = ''.join(f'<li{" class=\"big\"" if i == 0 and re.search(r"\d", str(p)) else ""}><span>{e(a)}</span><i></i><b>{e(p)}</b></li>' for i, (a, p) in enumerate(its))
        return f'<section class="sec ledger band-{band_of(sec, bt)}" id="{e(bt["id"])}"><div class="wrap two"><div>{lab(bt.get("label"))}<h2 class="h2" style="{re.sub(r"text-align:[^;]+;?|margin-(left|right):auto;?|max-width:[^;]+;?", "", head_style(sec, bt=bt))}">{e(bt.get("h2"))}</h2><p class="lede">{e(bt.get("lede"))}</p></div><div><ul class="rows">{rows}</ul><div class="ctas">{cta_html()}</div></div></div></section>'

    def two_col(sec, bt):
        if bt['type'] == 'steps': cols_ = [(f'0{i + 1}', s) for i, s in enumerate(bt.get('steps', []))][:3]
        elif bt['type'] == 'features': cols_ = [(f.get('title'), f.get('body')) for f in bt.get('features', [])][:2]
        else: cols_ = [(c[0], c[2] if len(c) > 2 else '') for c in bt.get('cells', [])][:2]
        inner = ''.join(f'<div><h3 class="h2" style="{head_style(sec)}">{e(t)}</h3><p class="big-p" style="font-size:{clampf(BO["px"] + 2, .8)}">{e(x)}</p></div>' for t, x in cols_)
        ui_ = bt.get('ui') or {}; lead = lead_fig(ui_, bt)
        return f'<section class="sec twocol band-{band_of(sec, bt)}{" compact" if (bt.get("ui") or {}).get("compact") else ""}" id="{e(bt["id"])}"><div class="wrap">{ghead(sec, bt) if bt["type"] != "features" else lab(bt.get("label"))}{lead}<div class="cols" style="--n:{len(cols_)}">{inner}</div></div></section>'

    cta_title_used = []
    def cta(sec, bt=None):
        title = (bt or {}).get('h2') or en.get('tag') or h.get('cta') or b['name']
        cta_title_used.append(title)
        fields = ''.join(f'<label><span>{e(f)}</span><input placeholder="{e(f)}"></label>' for f in (bt or {}).get('fields', [])[:6])
        form = f'<form class="form" onsubmit="return false">{fields}<button class="btn">{e((bt or {}).get("cta") or h.get("cta"))} <span class="ar">→</span></button></form>' if fields else f'<div class="ctas">{cta_html()}</div>'
        alt = ''.join(f'<span class="lab">{e(a)}</span>' for a in (bt or {}).get('alt', []))
        own = (bt or {}).get('image') or ((bt or {}).get('ui') or {}).get('lead')
        left = ([images[own]] if own and images.get(own) and not is_used(own) else []) + [i for i in images.values() if i.get('data') and not is_used(i.get('id')) and not i.get('shot') and reserved.get(i.get('id')) is None and i.get('w', 0) >= 900 and .6 <= i.get('w', 1) / max(1, i.get('h', 1)) <= 2.0 and not i.get('logo')]
        if fields and left:
            pic = img(left[0]['id'])
            return f'<section class="sec cta band-dark cta-pic" id="{e((bt or {}).get("id") or form_id)}"><div class="wrap cta2"><figure class="cta-v"><img src="{pic}" alt=""></figure><div class="cta-t">{lab((bt or {}).get("label"))}<h2 class="h2" style="{re.sub(r"text-align:[^;]+;?|margin-(left|right):auto;?", "", head_style(sec))}">{e(title)}</h2>{form}<div class="alts">{alt}</div></div></div></section>'
        return f'<section class="sec cta band-dark" id="{e((bt or {}).get("id") or form_id)}" style="min-height:{min(.7, sec.get("screens", 1)) * 100}svh"><div class="wrap center">{lab((bt or {}).get("label"))}<h2 class="h2" style="{head_style(sec)}">{e(title)}</h2>{form}<div class="alts">{alt}</div></div></section>'

    def giant(sec): return f'<section class="sec giant"><div class="wrap"><div class="gw" aria-hidden="true">{e(b["name"])}</div></div></section>'

    def footer(sec):
        cols_ = ''.join(f'<div><h5 class="lab">{e(t)}</h5><ul>{"".join("<li>" + e(x) + "</li>" for x in items)}</ul></div>' for t, items in en.get('cols', [])[:4])
        band = sec.get('band') or ('dark' if C.get('bands') and C['bands'][-1] == 'dark' else 'paper')
        tag = en.get('tag') if en.get('tag') not in cta_title_used else (h.get('category') or b['name'])
        return f'<footer class="sec end band-{band}" id="end"><div class="wrap"><p class="big-p">{e(tag)}</p><div class="fcols">{cols_}</div><div class="legal"><span>{e(en.get("legal"))}</span><span>{e(en.get("next"))}</span></div></div></footer>'

    # allocate — in the DIRECTION's order (the UX agent owns the order); each beat takes the next blueprint section of its family,
    # so the page keeps the winner's forms and rhythms but tells the client's story in the right sequence
    FAM = {'statement': ('statement', 'quote', 'manifesto', 'pinned-intro', 'story-right'),
           'photo': ('photo', 'work-', 'photo-pair', 'collage', 'marquee-photos', 'pinned-zoom', 'chapter-title-photo', 'photo-half-text'),
           'list': ('cards', 'feature', 'cases', 'blog', 'card-rail', 'showcase', 'tabs-media', 'gallery', 'pinned-features', 'pinned-sequence', 'sticker', 'double', 'two-audiences', 'updates', 'logo', 'tabs'),
           'cta': ('cta', 'band-', 'security', 'itinerary', 'giant-title')}
    pools = {k: [] for k in FAM}
    for sec in bp['sections'][1:]:
        r = sec['role']
        if r.startswith('footer') or r == 'services-footer': continue
        for fam, pre in FAM.items():
            if r.startswith(pre): pools[fam].append(sec); break
    DEF = {'statement': {'role': 'statement', 'head': {'px': H2['px']}, 'screens': .8}, 'photo': {'role': 'photo', 'media': [{'ar': 1.6, 'wf': 1, 'bleed': False}], 'head': None},
           'list': {'role': 'cards', 'media': [], 'head': {'px': H2['px']}}, 'cta': {'role': 'cta', 'screens': .9, 'head': {'px': H2['px'], 'al': 'center'}}}
    taken = {k: 0 for k in FAM}
    def take(fam):
        pool = pools[fam]
        if not pool: return DEF[fam]
        sec = pool[taken[fam] % len(pool)]; taken[fam] += 1; return sec
    out = [hero()]; used_beats = set(); cta_done = False; flip = False
    def default_move(role, t):
        # the winner's own section vocabulary → our signature component
        if 'sticky' in role and t in ('features', 'steps', 'cells'): return 'sticky-product'
        if role.startswith(('ticker', 'marquee', 'gallery-marquee', 'logo')): return 'marquee'
        if role.startswith('pinned') and t == 'steps': return 'pinned-sequence'
        if role.startswith(('story', 'tabs-media', 'photo-half-text')) and t in ('features', 'steps', 'cells', 'facts'): return 'story'
        return ''
    for bt in beats:
        t = bt['type']; mv = (bt.get('ui') or {}).get('move') or ''
        if mv == 'auto' or not mv:
            fam = 'statement' if t == 'quote' else 'photo' if t == 'photo' else 'cta' if t == 'form' else 'list'
            pool = pools[fam]; peek = pool[taken[fam] % len(pool)] if pool else DEF[fam]
            mv = default_move(peek['role'], t) if not mv else ''
        if mv in SIG and (t != 'quote' or mv in ('type-wall', 'story')) and t not in ('photo', 'form'):
            fam = 'statement' if t == 'quote' else 'list'; sec = take(fam)
            out.append(SIG[mv](sec, bt, flip) if mv == 'story' else SIG[mv](sec, bt)); flip = not flip if mv == 'story' else flip; used_beats.add(bt['id']); continue
        if t == 'quote' and mv == 'type-wall': sec = take('statement'); out.append(type_wall(sec, bt)); used_beats.add(bt['id']); continue
        if t == 'quote': sec = take('statement'); out.append(statement(sec, ('quote', bt)))
        elif t == 'photo': sec = take('photo'); out.append(photo_sec(sec, bt))
        elif t == 'ledger': sec = take('list'); out.append(ledger(sec, bt))
        elif t in ('features', 'cells', 'steps', 'facts', 'faq'):
            sec = take('list'); r = sec['role']
            if (r.startswith(('two-audiences', 'double')) and t in ('steps', 'features', 'cells')) or (t == 'steps' and r.startswith('feature')): out.append(two_col(sec, bt))
            else: out.append(cards(sec, bt))
        elif t == 'form': sec = take('cta'); out.append(cta(sec, bt)); cta_done = True
        else: continue
        used_beats.add(bt['id'])
    # a photo slot the blueprint has that the story did not use, when the client has an unused photo
    if pools['photo'] and taken['photo'] == 0 and len([i for i in images.values() if not i.get('shot') and i.get('id') not in used and i.get('w', 0) >= 900]) >= 1 and d.get('kind') in ('place', 'service'):
        out.insert(2, photo_sec(pools['photo'][0]))
    for sec in bp['sections'][1:]:
        if sec['role'].startswith('giant'): out.append(giant(sec)); break
    if not cta_done: out.append(cta(take('cta'), None))
    out.append(footer(bp['sections'][-1] if bp['sections'][-1]['role'].startswith('footer') else {}))

    # ---- logo ----
    logo = (assets.get('logo') or {}).get('data', '')
    mark = f'<img class="logo" src="{logo}" alt="{e(b["name"])}">' if logo and brief.get('keepLogo', True) else f'<span class="wordmark">{e(b["name"])}</span>'
    nav_links = ''.join(f'<a href="{e(hr)}">{e(l)}</a>' for hr, l in d.get('nav', {}).get('links', [])[:4])
    moves = open(os.path.join(ROOT, 'lib/motion/moves.js')).read(); swarm = open(os.path.join(ROOT, 'lib/motion/swarm.js')).read()
    frame = G.get('frame') or G.get('gutter') or 40; container = G.get('container') or 1300; radius = M.get('radius', 0)
    css = f'''
:root{{--paper:{paper};--ink:{ink};--accent:{accent};--on-photo:{on_photo};--band-paper:{band_paper};--band-ink:{band_ink};--line:color-mix(in srgb,var(--ink) 16%,transparent);--muted:color-mix(in srgb,var(--ink) 62%,transparent);
--display:'{disp_name}',{'Georgia,serif' if disp_kind == 'serif' else 'system-ui,sans-serif'};--body:'{body_name}',system-ui,sans-serif;--label:'{label_name}',ui-monospace,monospace;
--frame:{frame}px;--gutter:{G.get('gutter', 40)}px;--container:{container}px;--radius:{radius}px;--ease:{MO.get('ease')};--fast:{MO.get('fast', .3)}s;--slow:{MO.get('slow', .8)}s;
--btn-h:{BT.get('h', 48)}px;--btn-r:{BT.get('radius', 999)}px;--btn-px:{BT.get('px', 15)}px;--btn-pad:{BT.get('pad', '0 20px')};--btn-tt:{'uppercase' if BT.get('tt') else 'none'};
--h1:{clampf(D.get('px', 72))};--h1-lh:{D.get('lh', 1.0)};--h1-ls:{D.get('ls', -0.02)}em;--h1-w:{display_w};--h1-tt:{tt(D)};--h2:{clampf(H2.get('px', 44))};--h2-lh:{H2.get('lh', 1.1)};--h2-ls:{H2.get('ls', -0.02)}em;--h2-w:{H2.get('w', display_w)};
--h3:{clampf(H3.get('px', 24), .8)};--h3-w:{H3.get('w', 500)};--body-px:{BO.get('px', 17)}px;--body-lh:{BO.get('lh', 1.4)};--body-max:{BO.get('maxw') or 520}px;--lab-px:{LB.get('px', 12)}px;--lab-ls:{LB.get('ls', .08)}em}}
*{{box-sizing:border-box;margin:0;padding:0}}html{{scroll-behavior:auto}}html,body{{overflow-x:clip}}
body{{background:var(--paper);color:var(--ink);font-family:var(--body);font-size:var(--body-px);line-height:var(--body-lh);-webkit-font-smoothing:antialiased}}
img,video{{display:block;max-width:100%}}a{{color:inherit;text-decoration:none}}
.wrap{{max-width:var(--container);margin:0 auto;padding:0 var(--frame);width:100%}}
.lab{{font-family:var(--label);font-size:var(--lab-px);letter-spacing:var(--lab-ls);text-transform:uppercase;color:var(--muted);display:inline-block}}.lab.light{{color:rgba(244,239,227,.78)}}
.h1{{font-family:var(--display);font-weight:var(--h1-w);font-size:var(--h1);line-height:var(--h1-lh);letter-spacing:var(--h1-ls);text-transform:var(--h1-tt)}}.h1 em{{font-style:italic;font-weight:inherit}}
.h2{{font-family:var(--display);font-weight:var(--h2-w);font-size:var(--h2);line-height:var(--h2-lh);letter-spacing:var(--h2-ls)}}.h3{{font-family:var(--display);font-weight:var(--h3-w);font-size:var(--h3);line-height:1.12;letter-spacing:-.01em}}
.lede{{font-size:calc(var(--body-px) + 3px);line-height:1.4;max-width:var(--body-max);margin-top:22px}}.lede.light{{color:var(--on-photo);opacity:.88}}
.big-p{{font-family:{'var(--display)' if disp_kind == 'serif' else 'var(--body)'};font-weight:{300 if disp_kind != 'serif' and D.get('w', 400) <= 300 else 400};line-height:1.25;max-width:min(100%,{min(1100, (BO.get('maxw') or 520) * 1.6)}px);margin-top:18px;letter-spacing:-.01em}}
.btn{{display:inline-flex;align-items:center;gap:10px;min-height:var(--btn-h);padding:var(--btn-pad);border-radius:var(--btn-r);font-family:var(--body);font-size:var(--btn-px);font-weight:{BT.get('w', 500)};text-transform:var(--btn-tt);background:var(--{'accent' if lum(accent) < .8 and abs(lum(accent) - lum(ink)) > .18 else 'ink'});color:{'var(--paper)' if not (lum(accent) < .8 and abs(lum(accent) - lum(ink)) > .18) else ('#111' if lum(accent) > .55 else '#fff')};border:1px solid transparent;transition:transform var(--fast) var(--ease),background var(--fast)}}
.btn.ghost{{background:transparent;color:var(--ink);border-color:var(--ink)}}.btn.light{{color:var(--on-photo);border-color:var(--on-photo);background:transparent}}.btn.light:not(.ghost){{background:var(--on-photo);color:#111;border-color:var(--on-photo)}}.btn:active{{transform:scale(.97)}}.btn .ar{{transition:transform var(--fast) var(--ease)}}.btn:hover .ar{{transform:translateX(4px)}}
.nav{{position:fixed;inset:0 0 auto 0;z-index:50;padding:18px 0;transition:background var(--slow),color var(--slow)}}.nav .wrap{{display:flex;align-items:center;justify-content:space-between;gap:24px}}.nav .links{{display:flex;gap:28px;font-size:15px}}.nav.solid{{background:color-mix(in srgb,var(--paper) 86%,transparent);backdrop-filter:blur(14px)}}.nav .logo{{height:{min(56, max(28, (bp.get('nav') or {}).get('h', 56) - 20))}px;width:auto}}.nav .wordmark{{font-family:var(--display);font-size:22px}}
.hero{{position:relative;display:grid;align-content:end;overflow:hidden;padding-top:120px}}.hero .media{{position:absolute;inset:0;z-index:0;background:var(--ink)}}.hero .media img,.hero .media video{{width:100%;height:100%;object-fit:cover}}.hero.has-media .media::after{{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.35),rgba(0,0,0,.08) 40%,rgba(0,0,0,.55))}}
.hero .hero-in{{position:relative;z-index:1;padding-bottom:clamp(40px,6vw,80px)}}.hero.has-media{{color:var(--on-photo)}}.hero .cat{{display:flex;gap:26px;flex-wrap:wrap;margin-bottom:22px}}.hero .al-center{{text-align:center;justify-items:center;display:grid}}.hero .place-start{{align-self:start;padding-top:40px}}.hero .ctas{{display:flex;gap:12px;flex-wrap:wrap;margin-top:30px}}
.hero.shot{{align-content:start;padding-top:104px;min-height:auto!important}}.hero.shot .hero-in{{padding-bottom:0}}.hero.shot .cat{{margin-bottom:14px}}.hero.shot .lede{{margin-top:14px}}.hero.shot .ctas{{margin-top:20px}}.shotwrap{{padding-top:clamp(22px,3vw,36px);padding-bottom:0}}.shotframe{{border-radius:max(12px,var(--radius)) max(12px,var(--radius)) 0 0;overflow:hidden;border:1px solid var(--line);border-bottom:0;box-shadow:0 30px 80px color-mix(in srgb,var(--ink) 14%,transparent)}}.shotframe img{{width:100%;max-height:72vh;object-fit:cover;object-position:top center}}
.sec{{padding:clamp(64px,9vw,140px) 0;display:grid;align-content:center}}.band-dark{{background:var(--band-paper);color:var(--band-ink);--muted:color-mix(in srgb,var(--band-ink) 68%,transparent);--line:color-mix(in srgb,var(--band-ink) 22%,transparent)}}.band-dark .lab{{color:color-mix(in srgb,var(--band-ink) 62%,transparent)}}.band-dark .btn{{background:var(--band-ink);color:var(--band-paper)}}.band-alt{{background:color-mix(in srgb,var(--ink) 6%,var(--paper))}}
.statement .who{{margin-top:22px}}.statement .wrap.center{{text-align:center;display:grid;justify-items:center}}
.photos .pair{{display:flex;gap:var(--gutter);align-items:flex-start}}.photos figure{{overflow:hidden;border-radius:var(--radius)}}.photos figure img,.photo figure img{{width:100%;height:100%;object-fit:cover}}.photo figure{{position:relative;margin:0}}.photo.bleed{{padding:0}}.photo .over{{position:absolute;inset:auto 0 0 0;padding-bottom:clamp(28px,4vw,56px);color:var(--on-photo)}}.h2.light{{color:var(--on-photo)}}.cap{{margin-top:14px;max-width:var(--body-max);color:var(--muted)}}.caps{{display:flex;gap:24px;align-items:baseline;flex-wrap:wrap;padding-top:14px}}
.gh{{display:grid;grid-template-columns:1.1fr .9fr;gap:var(--gutter);align-items:end;margin-bottom:clamp(28px,4vw,48px)}}.gh .h2{{text-align:left!important;margin-left:0!important;margin-top:14px;max-width:18ch;text-wrap:balance}}.gh .lede{{margin-top:0}}
.sec.compact{{padding:clamp(40px,5vw,72px) 0;min-height:auto!important}}.gh.one{{display:block;max-width:var(--body-max)}}.gh.one .h2{{max-width:none}}.gh.one.center{{text-align:center;margin-left:auto;margin-right:auto}}.gh.one.center .h2{{text-align:center!important;margin-left:auto!important;margin-right:auto}}.gh.one .lede{{margin-top:16px}}.gh.one.center .lede{{margin-left:auto;margin-right:auto}}
figure.lead{{overflow:hidden;border-radius:var(--radius);margin:0 0 clamp(28px,4vw,48px);border:1px solid var(--line);max-height:78vh}}figure.lead.narrow{{width:min(100%,640px);margin-left:auto;margin-right:auto}}figure.lead img{{width:100%;height:100%;object-fit:cover;object-position:top}}
.faq .two{{display:grid;grid-template-columns:.8fr 1.2fr;gap:var(--gutter)}}.qa details{{border-top:1px solid var(--line);padding:16px 0}}.qa details:last-child{{border-bottom:1px solid var(--line)}}.qa summary{{cursor:pointer;list-style:none;font-family:var(--display);font-weight:var(--h3-w);font-size:min(var(--h3),24px);display:flex;justify-content:space-between;gap:16px}}.qa summary::after{{content:"+";font-weight:300}}.qa details[open] summary::after{{content:"–"}}.qa details p{{margin-top:10px;color:var(--muted);max-width:60ch}}
.grid{{display:grid;grid-template-columns:repeat(var(--n),1fr);gap:var(--gutter)}}.card figure{{overflow:hidden;border-radius:var(--radius);margin-bottom:16px}}.card figure img{{width:100%;height:100%;object-fit:cover}}.card .h3{{margin-top:8px;font-size:min(var(--h3),28px)}}.card p{{margin-top:10px;color:var(--muted);max-width:34ch}}.card .num{{display:block;font-family:var(--display);font-weight:var(--h2-w);font-size:var(--h2);line-height:1;letter-spacing:-.02em}}
.ledger .two{{display:grid;grid-template-columns:.9fr 1.1fr;gap:var(--gutter)}}.rows{{list-style:none}}.rows li{{display:flex;align-items:baseline;gap:12px;padding:14px 0;border-top:1px solid var(--line);font-size:calc(var(--body-px) + 2px)}}.rows li i{{flex:1;border-bottom:1px dotted var(--line)}}.rows li b{{font-weight:500;font-variant-numeric:tabular-nums}}.rows li.big{{padding:22px 0}}.rows li.big b{{font-family:var(--display);font-weight:var(--h2-w);font-size:var(--h2);line-height:1;letter-spacing:-.02em}}.ledger .ctas{{margin-top:26px}}
.twocol .cols{{display:grid;grid-template-columns:repeat(var(--n),1fr);gap:var(--gutter);margin-top:30px}}.twocol .cols .h2{{font-size:var(--h3)}}
.cta .center{{text-align:center;display:grid;justify-items:center;gap:22px}}.cta .h2{{max-width:16ch}}.form{{display:grid;grid-template-columns:1fr 1fr;gap:12px;width:min(640px,100%);text-align:left}}.form label{{display:grid;gap:6px}}.form label span{{font-family:var(--label);font-size:var(--lab-px);letter-spacing:var(--lab-ls);text-transform:uppercase;opacity:.7}}.form input{{min-height:46px;border:1px solid color-mix(in srgb,currentColor 30%,transparent);background:transparent;color:inherit;padding:0 12px;border-radius:max(4px,min(12px,var(--btn-r)));font:inherit}}.form .btn{{grid-column:1/-1;justify-content:center}}.alts{{display:flex;gap:18px;flex-wrap:wrap;justify-content:center}}
.giant{{padding:40px 0 0;overflow:hidden}}.gw{{font-family:var(--display);font-weight:var(--h1-w);font-size:min(22vw,{round(165 / max(4, len(b['name'])), 1)}vw);line-height:.85;letter-spacing:-.03em;white-space:nowrap;text-transform:var(--h1-tt)}}
.end{{padding-top:clamp(48px,6vw,80px);padding-bottom:28px}}.end .fcols{{display:grid;grid-template-columns:repeat(4,1fr);gap:var(--gutter);margin-top:48px;padding-top:40px;border-top:1px solid var(--line)}}.end ul{{list-style:none;margin-top:10px;display:grid;gap:6px}}.end .legal{{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-top:40px;font-family:var(--label);font-size:var(--lab-px);color:var(--muted)}}
/* signature components */
.hero.split{{padding-top:96px;min-height:100svh;align-content:center}}.split-wrap{{display:grid;grid-template-columns:1fr 1.1fr;gap:var(--gutter);align-items:center}}.split-l .lede{{margin-top:18px}}.split-l .ctas{{margin-top:26px}}.shotframe.tall{{border-radius:max(12px,var(--radius));border:1px solid var(--line);box-shadow:0 40px 100px color-mix(in srgb,var(--ink) 16%,transparent);overflow:hidden}}.shotframe.tall img{{width:100%;height:min(82vh,900px);object-fit:cover;object-position:left top}}
.sp{{display:grid;grid-template-columns:1fr 1.15fr;gap:calc(var(--gutter) * 1.5);align-items:stretch}}.sp-row{{min-height:46vh;display:grid;align-content:center;gap:12px;max-width:40ch;opacity:.28;transition:opacity .5s var(--ease)}}.sp-row.on{{opacity:1}}.sp-row .h3{{font-size:min(var(--h2),44px)}}.sp-row p{{color:var(--muted);font-size:calc(var(--body-px) + 1px)}}.sp-pin{{position:relative}}.sp-stage{{position:sticky;top:12vh;height:76vh;border-radius:max(12px,var(--radius));overflow:hidden;border:1px solid var(--line);background:color-mix(in srgb,var(--ink) 6%,var(--paper))}}.sp-f{{position:absolute;inset:0;margin:0;opacity:0;transform:scale(1.03);transition:opacity .6s var(--ease),transform .9s var(--ease)}}.sp-f.on{{opacity:1;transform:none}}.sp-f img{{width:100%;height:100%;object-fit:cover;object-position:top;transition:transform 1.2s var(--ease)}}
.marquee{{padding:clamp(28px,4vw,56px) 0;overflow:hidden}}.marquee .gh{{margin-bottom:24px}}.mq{{overflow:hidden;border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:18px 0}}.mq-track{{display:flex;gap:0;width:max-content;animation:mq 46s linear infinite}}.mq-i{{display:inline-flex;align-items:center;gap:28px;padding:0 14px 0 28px;font-family:var(--display);font-weight:var(--h2-w);font-size:min(var(--h2),56px);letter-spacing:-.02em;white-space:nowrap}}.mq-i i{{font-style:normal;font-size:.45em;color:var(--accent)}}@keyframes mq{{to{{transform:translateX(-50%)}}}}.marquee:hover .mq-track{{animation-play-state:paused}}
.pinned{{padding:0}}.ps-sticky{{position:sticky;top:0;height:100svh;display:grid;align-content:center;overflow:hidden}}.ps-stage{{position:relative;min-height:52vh}}.ps-s{{position:absolute;inset:0;display:grid;grid-template-columns:1fr 1fr;gap:var(--gutter);align-items:center;opacity:0;transform:translateY(24px);transition:opacity .5s var(--ease),transform .7s var(--ease);pointer-events:none}}.ps-s.on{{opacity:1;transform:none}}.ps-t .num{{display:block;font-family:var(--display);font-weight:var(--h1-w);font-size:clamp(64px,10vw,160px);line-height:.9;letter-spacing:-.03em;color:var(--accent)}}.ps-t .h2{{margin-top:18px}}.ps-v{{margin:0;border-radius:max(12px,var(--radius));overflow:hidden;border:1px solid var(--line);aspect-ratio:1.3}}.ps-v img{{width:100%;height:100%;object-fit:cover}}.ps-dots{{display:flex;gap:8px;margin-top:28px}}.ps-dots i{{width:28px;height:2px;background:var(--line)}}.ps-dots i.on{{background:var(--ink)}}.band-dark .ps-dots i.on{{background:var(--band-ink)}}
.typewall{{padding:0}}.tw-sticky{{position:sticky;top:0;min-height:100svh;display:grid;align-content:center}}.tw{{font-family:var(--display);font-weight:var(--h2-w);font-size:clamp(28px,4.6vw,72px);line-height:1.08;letter-spacing:-.02em;max-width:22ch;margin-top:22px}}.tw-w{{opacity:.18;transition:opacity .25s}}.tw-w.on{{opacity:1}}.typewall .who{{margin-top:28px}}
.cta2{{display:grid;grid-template-columns:1fr 1fr;gap:calc(var(--gutter) * 1.5);align-items:center}}.cta-v{{margin:0;border-radius:max(12px,var(--radius));overflow:hidden;aspect-ratio:1.05}}.cta-v img{{width:100%;height:100%;object-fit:cover}}.cta-t{{display:grid;gap:22px}}.cta-t .form{{text-align:left}}.cta-t .alts{{justify-content:flex-start}}
.st{{display:grid;grid-template-columns:1fr 1fr;gap:calc(var(--gutter) * 1.5);align-items:center}}.story.flip .st-t{{order:2}}.st-l{{list-style:none;margin-top:28px;display:grid;gap:14px}}.st-l li{{display:grid;grid-template-columns:minmax(120px,.35fr) 1fr;gap:16px;padding-top:12px;border-top:1px solid var(--line)}}.st-l b{{font-weight:500}}.st-l span{{color:var(--muted)}}.st-v{{margin:0;border-radius:max(12px,var(--radius));overflow:hidden;border:1px solid var(--line);aspect-ratio:1.15}}.st-v img{{width:100%;height:100%;object-fit:cover;object-position:top}}
@media(max-width:900px){{.split-wrap,.sp,.ps-s,.st,.cta2{{grid-template-columns:1fr}}.story.flip .st-t{{order:0}}.sp-pin{{order:-1}}.sp-stage{{position:relative;top:auto;height:52vh}}.sp-row{{min-height:auto;padding:22px 0;opacity:1}}.ps-s{{align-content:start}}.ps-v{{aspect-ratio:1.6}}.shotframe.tall img{{height:52vh}}.mq-i{{font-size:28px}}.nav .links{{display:none}}.gh,.ledger .two,.faq .two,.photos .pair{{grid-template-columns:1fr;display:grid}}.photos figure{{width:100%!important}}.grid{{grid-template-columns:1fr}}.twocol .cols{{grid-template-columns:1fr}}.end .fcols{{grid-template-columns:1fr 1fr}}.form{{grid-template-columns:1fr}}.hero{{padding-top:100px}}.wrap{{padding:0 max(16px,calc(var(--frame) * .5))}}}}
@media(prefers-reduced-motion:reduce){{*{{transition:none!important;animation:none!important}}}}
'''
    moves_attr = lambda n: f' data-move="{n}"'
    html = f'''<!DOCTYPE html><html lang="{e(d.get("lang", "en"))}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{e(b["name"])}</title>{fonts_link}<style>{css}</style></head>
<body>
<nav class="nav{' solid' if not sec_media(bp['sections'][0]) else ''}" id="nav" data-nav><div class="wrap"><a href="#top">{mark}</a><div class="links">{nav_links}</div>{cta_html(bool(sec_media(bp['sections'][0])))}</div></nav>
{chr(10).join(out)}
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script><script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>{'<script src="https://unpkg.com/lenis@1.1.18/dist/lenis.min.js"></script>' if MO.get('smooth') else ''}
<script>{moves}</script><script>{swarm}</script>
<script>
// blueprint motion: reveal on scroll for every section's main pieces, with the winner's own easing/durations
document.querySelectorAll('.sec .h2, .sec .big-p, .sec .lede, .grid, .rows, .cols, .photo figure, .photos figure').forEach((el, i) => {{ if (!el.closest('.hero')) el.setAttribute('data-move', el.matches('figure') ? 'clip-reveal' : el.matches('.grid, .rows, .cols') ? 'stagger-in' : 'fade-rise'); }});
document.querySelector('.hero')?.setAttribute('data-move', 'hero-intro');
// signature motion (GSAP ScrollTrigger is on the page)
function Sig(){{ if(!window.gsap||!window.ScrollTrigger) return; gsap.registerPlugin(ScrollTrigger);
  document.querySelectorAll('[data-sig="sticky"]').forEach(sec=>{{ const rows=[...sec.querySelectorAll('.sp-row')], fr=[...sec.querySelectorAll('.sp-f')]; const set=i=>{{ rows.forEach((r,k)=>r.classList.toggle('on',k===i)); fr.forEach((f,k)=>f.classList.toggle('on',k===i)); }}; set(0);
    rows.forEach((r,i)=>ScrollTrigger.create({{trigger:r,start:'top 55%',end:'bottom 55%',onEnter:()=>set(i),onEnterBack:()=>set(i)}})); }});
  document.querySelectorAll('[data-sig="pinned"]').forEach(sec=>{{ const n=+sec.dataset.n||1; sec.style.height=(n*85+40)+'vh'; const sl=[...sec.querySelectorAll('.ps-s')], dots=[...sec.querySelectorAll('.ps-dots i')]; const set=i=>{{ sl.forEach((s,k)=>s.classList.toggle('on',k===i)); dots.forEach((d,k)=>d.classList.toggle('on',k<=i)); }}; set(0);
    ScrollTrigger.create({{trigger:sec,start:'top top',end:'bottom bottom',onUpdate:st=>set(Math.min(n-1,Math.floor(st.progress*n)))}}); }});
  document.querySelectorAll('[data-sig="typewall"]').forEach(sec=>{{ const ws=[...sec.querySelectorAll('.tw-w')]; sec.style.height='150vh'; ScrollTrigger.create({{trigger:sec,start:'top top',end:'bottom bottom',onUpdate:st=>{{ const k=Math.round(st.progress*ws.length); ws.forEach((w,i)=>w.classList.toggle('on',i<k)); }}}}); }});
  document.querySelectorAll('[data-sig="parallax"]').forEach(el=>gsap.fromTo(el,{{y:40}},{{y:-40,ease:'none',scrollTrigger:{{trigger:el,start:'top bottom',end:'bottom top',scrub:true}}}}));
  ScrollTrigger.refresh(); }}
const NOMOTION=/[?&]nomotion/.test(location.search); const PREVIEW=!NOMOTION&&(self!==top||/[?&]swarm/.test(location.search))&&!matchMedia('(prefers-reduced-motion:reduce)').matches;
if(NOMOTION){{ document.querySelectorAll('[data-move]').forEach(el=>el.removeAttribute('data-move')); document.querySelectorAll('.tw-w,.sp-row').forEach(el=>el.classList.add('on')); document.querySelectorAll('.ps-s,.sp-f').forEach((el,i)=>el.classList.toggle('on',el.dataset.i==='0')); }}
addEventListener('load',()=>{{ const nav=document.getElementById('nav'); const solidFrom=document.querySelector('.hero.has-media')?innerHeight*.7:0; const onS=()=>nav.classList.toggle('solid',scrollY>solidFrom); onS(); addEventListener('scroll',onS,{{passive:true}});
  try{{ if(PREVIEW) new Swarm({{agents:innerWidth<900?8:18,speed:1,hud:true,sectionSelector:'section,footer',boxSel:'.btn,.card,figure,.rows li,.form input',onDone:()=>{{ try{{ scrollTo(0,0); Moves.init(); Sig(); }}catch(e){{}} }}}}).run(); else {{ Moves.init(); Sig(); }} }}catch(e){{ try{{Moves.init(); Sig();}}catch(_){{}} }} }});
</script></body></html>'''
    out_path = out_path or os.path.join(slug_dir, f'index.{bp_id}.html'); open(out_path, 'w').write(html); return out_path

if __name__ == '__main__':
    print(build(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None))
