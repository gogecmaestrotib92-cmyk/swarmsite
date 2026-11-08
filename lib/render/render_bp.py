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
    try:
        sys.path.insert(0, os.path.join(ROOT, 'lib/templates')); from recipes import RECIPES, FALLBACK
    except Exception: RECIPES, FALLBACK = {}, {}
    RECIPE = RECIPES.get(bp_id)
    j = lambda n: json.load(open(os.path.join(slug_dir, n))) if os.path.exists(os.path.join(slug_dir, n)) else None
    d = j('direction.json'); assets = j('assets.json') or {}; brief = j('brief.json') or {}; inventory = j('inventory.json') or {}
    images = {i.get('id', str(n)): i for n, i in enumerate(j('images.json') or [])}
    bp = json.load(open(os.path.join(ROOT, 'lib/blueprints', bp_id + '.bp.json')))
    b = d['brand']; h = d['hero']; en = d.get('ending') if isinstance(d.get('ending'), dict) else {}
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
        for feature in bt0.get('features') or []:
            image_id = feature.get('image') if isinstance(feature, dict) else None
            if isinstance(image_id, str) and image_id in images:
                reserved.setdefault(image_id, bt0['id'])
    if h.get('media') and images.get(h['media']): reserved.setdefault(h['media'], '__hero__')
    def free_for(it, bt=None):
        owners = {reserved[k] for k in family(it.get('id')) if k in reserved}
        owner = bt.get('id') if bt is not None else '__hero__'
        return not owners or owners == {owner}
    soft = d.get('kind') in ('software', 'product')
    def dark_background_texture(it):
        lum = it.get('lum')
        if not it.get('bg') or not it.get('data') or (isinstance(lum, (int, float)) and lum > 40): return False
        try:
            from PIL import Image, ImageStat
            import io
            raw = base64.b64decode(it['data'].split(',', 1)[1])
            image = Image.open(io.BytesIO(raw)).convert('L').resize((64, 64))
            stats = ImageStat.Stat(image)
            return stats.mean[0] <= 40 and stats.stddev[0] < 8
        except Exception: return False
    def symbolic_asset(it):
        # SVGs can be rasterized by capture, so their data URI may say JPEG.
        # A source logo or icon is not a substitute for a story photograph.
        from urllib.parse import urlsplit, unquote
        source = str(it.get('src') or '')
        try: source_path = unquote(urlsplit(source).path).lower()
        except ValueError: source_path = source.split('?', 1)[0].lower()
        if source_path.endswith('.svg') or 'svg' in str(it.get('data') or '')[:30].lower(): return True
        markers = source_path + ' ' + str(it.get('alt') or '')
        return bool(re.search(r'(?i)(?:^|[/_.\-\s])(logo|icon|favicon|wordmark|brandmark|badge)(?:$|[/_.\-\s])', markers))
    def photo_like(it, minw=500):
        # a picture that can stand in a card or a frame: real pixels, not a page screenshot, not a banner strip or a logo, not vector art
        if not it.get('data') or it.get('shot') or is_used(it.get('id')) or it.get('w', 0) < minw or dark_background_texture(it): return False
        if symbolic_asset(it): return False
        ar = it.get('w', 1) / max(1, it.get('h', 1)); return .55 <= ar <= 2.0
    def img(k=None, prefer_hero=False, want_shot=None):
        it = images.get(k) if k else None
        if it and is_used(it.get('id')) and not prefer_hero: it = None
        if not it:
            available = [i for i in images.values() if i.get('data') and not dark_background_texture(i)]
            pool = [i for i in available if not is_used(i.get('id')) and reserved.get(i.get('id')) is None] or [i for i in available if not is_used(i.get('id'))] or (available if prefer_hero else [])
            if want_shot is True: pool = [i for i in pool if i.get('shot')] or pool
            if want_shot is False: pool = [i for i in pool if not i.get('shot')] or pool
            # hero: real photos first; software bodies: UI section shots first; places: photos first
            pool.sort(key=lambda i: (bool(i.get('shot')) if (prefer_hero or not soft) else not i.get('shot'), not (i.get('heroGrade') if prefer_hero else True), -(i.get('w', 0) * i.get('h', 0)))); it = pool[0] if pool else None
        if not it: return ''
        used.update(family(it.get('id'))); return it.get('data', '')

    def source_alt(src):
        # Reuse the source author's alt text for actual content photographs.
        # Do not invent descriptions for generated visuals, screenshots or
        # derived crops: their content may differ from the source image.
        for it in images.values():
            if it.get('data') != src or it.get('gen') or it.get('shot') or it.get('crop_of'):
                continue
            alt = it.get('alt')
            if isinstance(alt, str) and alt.strip(): return e(' '.join(alt.split()))
        return ''

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
    # Only link to destinations captured from the source. The generated page has no submission backend.
    pages = [inventory] + (inventory.get('sourcePages') or [])
    actions = [a for page in pages for a in page.get('actions', [])
               if isinstance(a, dict) and ('#' not in str(a.get('href') or '') or a.get('fragment_navigable') is True)]
    source_forms = [f for page in pages for f in page.get('forms', []) if isinstance(f, dict)]
    def safe_url(url):
        return url if isinstance(url, str) and re.match(r'^(https?://|mailto:|tel:)', url, re.I) and not re.search(r'[\x00-\x20]', url) else ''
    captured = {safe_url(a.get('href')) for a in actions}
    captured_forms = {safe_url(f.get('source_url')) for f in source_forms}
    def action_url(label='', preferred='', include_forms=False):
        preferred = safe_url(preferred)
        if preferred and (preferred in captured or (include_forms and preferred in captured_forms)): return preferred
        label = str(label or '').strip().casefold()
        match = next((safe_url(a.get('href')) for a in actions if str(a.get('text') or '').strip().casefold() == label and safe_url(a.get('href'))), '')
        if match or not include_forms or not label: return match
        return next((safe_url(f.get('source_url')) for f in source_forms if str(f.get('text') or '').strip().casefold() == label and safe_url(f.get('source_url'))), '')
    contact = forms[0] if forms else {}
    contact_target = action_url(contact.get('cta') or h.get('cta'), contact.get('cta_href') or h.get('cta_href'), include_forms=True)
    def cta_html(light=False, label=None, href=None):
        label = label or h.get('cta') or d.get('nav', {}).get('cta') or 'Contact'
        target = href if href is not None else ('#' + form_id if forms and contact_target else action_url(label, h.get('cta_href')))
        return f'<a class="btn{" light" if light else ""}" href="{e(target)}">{e(label)} <span class="ar">→</span></a>' if target else ''
    def secondary_cta(light=False):
        label = h.get('cta2')
        target = action_url(label, h.get('cta2_href')) if label else ''
        return f'<a class="btn ghost{" light" if light else ""}" href="{e(target)}">{e(label)}</a>' if target else ''
    # This mapping is evidence from the page itself, not model-generated URLs.
    source_sections = {str(s.get('id')): s for s in (inventory.get('sourceCoverage') or {}).get('sections', [])
                       if isinstance(s, dict) and s.get('id')}
    emitted_source_sections = set()
    source_owner = {}
    def assign_source_owners(renderable_beats):
        source_owner.clear()
        for beat in renderable_beats:
            sections_for_beat = beat.get('source_sections') if isinstance(beat.get('source_sections'), list) else []
            for source_id in dict.fromkeys(map(str, sections_for_beat)):
                sec = source_sections.get(source_id)
                if not sec: continue
                # Reuse the section's real FAQ/testimonial component when available;
                # otherwise a dedicated single-source beat beats a broad grouping.
                score = (30 if sec.get('faq') and beat.get('type') == 'faq' else 0) + (30 if sec.get('testimonials') and beat.get('type') == 'testimonials' else 0) + (10 if len(sections_for_beat) == 1 else 0)
                if source_id not in source_owner or score > source_owner[source_id][0]: source_owner[source_id] = (score, beat.get('id'))
    def captured_source_actions(rendered, bt):
        from html.parser import HTMLParser
        from urllib.parse import urlsplit
        class Anchors(HTMLParser):
            def __init__(self): super().__init__(convert_charrefs=True); self.open = None; self.pairs = set()
            def handle_starttag(self, tag, attrs):
                if tag == 'a': self.open = [dict(attrs).get('href', ''), []]
            def handle_data(self, text):
                if self.open is not None: self.open[1].append(text)
            def handle_endtag(self, tag):
                if tag == 'a' and self.open is not None:
                    label = re.sub(r'\s*→\s*$', '', ' '.join(''.join(self.open[1]).split())).casefold()
                    self.pairs.add((self.open[0], label)); self.open = None
        anchors = Anchors(); anchors.feed(rendered)
        for key in ('cta', 'cta2'):
            label = bt.get(key)
            url = action_url(label, bt.get(key + '_href'), include_forms=True) if label else ''
            if url: anchors.pairs.add((url, ' '.join(str(label).split()).casefold()))
        lang = str(inventory.get('lang') or '').lower().split('-')[0]
        heading = {'es':'Enlaces originales','sr':'Originalni linkovi','hr':'Izvorne poveznice','fr':'Liens originaux','de':'Originale Links','pt':'Links originais','it':'Link originali'}.get(lang, 'Original links')
        sources = bt.get('source_sections'); sources = sources if isinstance(sources, list) else []
        groups = []
        for sid in sources:
            sid = str(sid)
            sec = source_sections.get(sid)
            if sid in emitted_source_sections or not sec or sec.get('sourceActionsVersion') != 1: continue
            if source_owner.get(sid, (None, None))[1] != bt.get('id'): continue
            if sec.get('headingLevel') not in ('H2', 'H3') or sec.get('kind') == 'unheaded': continue
            title = str(sec.get('title') or '').strip()
            if not title: continue
            links = []
            evidence = sec.get('sourceActions') if isinstance(sec.get('sourceActions'), list) else []
            for a in evidence[:20]:
                if not isinstance(a, dict): continue
                label, url = a.get('label'), a.get('url')
                if not isinstance(label, str) or not label.strip() or len(label) > 160 or not isinstance(url, str) or re.search(r'[\x00-\x20\x7f]', url): continue
                try:
                    u = urlsplit(url); host = (u.hostname or '').lower(); _port = u.port
                    host = host.rstrip('.')
                    if u.scheme not in ('http', 'https') or not host or u.username or u.password or host == 'localhost' or host.endswith(('.local','.internal','.localhost')) or ':' in host or re.fullmatch(r'\d+\.\d+\.\d+\.\d+', host): continue
                except ValueError: continue
                pair = (url, ' '.join(label.split()).casefold())
                if pair in anchors.pairs: continue
                anchors.pairs.add(pair)
                links.append(f'<li><a href="{e(url)}" target="_blank" rel="noopener noreferrer">{e(label)} ↗</a></li>')
            emitted_source_sections.add(sid)
            if links: groups.append(f'<div><p class="source-actions-label">{e(heading)} · {e(title)}</p><ul>{"".join(links)}</ul></div>')
        return f'<aside class="wrap source-actions">{"".join(groups)}</aside>' if groups else ''
    def section_extras(rendered, bt):
        # All list/photo/quote renderers share the same source-backed actions.
        # Ledger and form already render their own actions.
        if not rendered or '</section>' not in rendered: return rendered
        source_actions_html = captured_source_actions(rendered, bt)
        if bt['type'] in ('ledger', 'form'):
            return rendered.rsplit('</section>', 1)[0] + source_actions_html + '</section>' if source_actions_html else rendered
        note = bt.get('note') if bt['type'] == 'steps' else ''
        note_html = f'<p class="section-note">{e(note)}</p>' if note else ''
        links = []
        for key in ('cta', 'cta2'):
            label = bt.get(key)
            target = action_url(label, bt.get(key + '_href'), include_forms=True) if label else ''
            if target:
                links.append(f'<a class="btn" href="{e(target)}">{e(label)} <span class="ar">→</span></a>')
        actions_html = f'<div class="section-actions">{"".join(links)}</div>' if links else ''
        if not note_html and not actions_html and not source_actions_html: return rendered
        extra = (f'<div class="wrap section-extras">{note_html}{actions_html}</div>' if note_html or actions_html else '') + source_actions_html
        return rendered.rsplit('</section>', 1)[0] + extra + '</section>'
    lab = lambda t, light=False: f'<span class="lab{" light" if light else ""}">{e(t)}</span>' if t else ''
    pos = {bt['id']: i + 1 for i, bt in enumerate(d.get('beats', []))}
    for bt in d.get('beats', []):
        if bt.get('label'):
            core = re.sub(r'^\s*0?\d{1,2}\s*[/.·—–-]?\s*', '', str(bt['label'])).strip()
            bt['label'] = f"{pos[bt['id']]:02d} — {core}" if core and re.match(r'^\s*0?\d{1,2}\b', str(bt['label'])) else (core or bt['label'])

    def band_of(sec, bt=None):
        return (bt or {}).get('band') or sec.get('band') or 'paper'
    def head_style(sec, key='head', bt=None):
        hd = sec.get(key) or {}; px_ = ((bt or {}).get('ui') or {}).get('h2_px') or hd.get('px') or H2.get('px'); px_ = min(px_, 96); st = [f'font-size:{clampf(px_)}']
        if hd.get('lh'): st.append(f'line-height:{hd["lh"]}')
        if hd.get('tt') == 'uppercase': st.append('text-transform:uppercase')
        if hd.get('it'): st.append('font-style:italic')
        if hd.get('al') in ('center',): st.append('text-align:center;margin-left:auto;margin-right:auto')
        if hd.get('wf'): st.append(f'max-width:{min(100, max(46, round(hd["wf"] * 100 + 2)))}%')
        if hd.get('ls') is not None: st.append(f'letter-spacing:{hd["ls"]}em')
        return ';'.join(st)
    def col_style(sec):
        hd = sec.get('head') or {}; x = hd.get('x') or 0
        return f'--statement-offset:{round(max(0, x - G["gutter"] / 1440) * 100)}%' if x > 0.3 and hd.get('al') != 'center' else ''

    def hero():
        media = sec_media(bp['sections'][0]); light = bool(media)
        vid = os.path.join(slug_dir, 'hero.mp4')
        hm = images.get(h.get('media')) or {}
        if hm and ('svg' in str(hm.get('data', ''))[:30] or hm.get('w', 0) < (700 if soft else 1000) or not (.5 <= hm.get('w', 1) / max(1, hm.get('h', 1)) <= 2.4) or (hm.get('shot') and not soft) or dark_background_texture(hm)): hm = {}  # a texture, vector, banner, small image or page screenshot is not a hero photo
        cand = hm or next((i for i in sorted(images.values(), key=lambda i: -(i.get('w', 0) * i.get('h', 0))) if photo_like(i, 900) and reserved.get(i.get('id')) in (None, '__hero__')), None)
        src = img(cand['id'], True) if cand else img(None, True)
        if media and src:
            m = f'<div class="media"><img src="{src}" alt="{source_alt(src)}"></div>' if not os.path.exists(vid) else f'<div class="media"><video autoplay muted loop playsinline poster="{src}"><source src="data:video/mp4;base64,{base64.b64encode(open(vid, "rb").read()).decode()}" type="video/mp4"></video></div>'
        else: m = ''
        hd = bp['sections'][0].get('head') or D
        y = hd.get('y'); place = 'end' if (y or .6) > .5 else 'start'
        al = (h.get('ui') or {}).get('align') or ('center' if hd.get('al') == 'center' else 'start')
        h1 = e(h['h1']).replace('&lt;em&gt;', '<em>').replace('&lt;/em&gt;', '</em>')
        nw = len(re.sub(r'<[^>]+>', '', h['h1']).split()); hpx = hd.get('px') or D.get('px', 72)
        if nw >= 6: hpx = min(hpx, 84)
        if nw >= 8: hpx = min(hpx, 68)
        hui = h.get('ui') or {}; hpx = round(hpx * {'S': .72, 'M': .88, 'L': 1}.get(hui.get('size', ''), 1))
        nch = len(re.sub(r'<[^>]+>', '', h['h1'])); upper = (hd.get('tt') == 'uppercase'); hpx = max(56, min(hpx, int(3 * 1150 / ((0.7 if upper else 0.56) * max(12, nch)))))
        hsty = head_style(bp['sections'][0]); hsty = re.sub(r'font-size:[^;]+', f'--hero-size:{clampf(hpx)}', hsty); hsty = re.sub(r'max-width:[^;]+', 'max-width:14ch', hsty); hsty = re.sub(r'text-align:[^;]+;?|margin-(left|right):auto;?', '', hsty) + ';text-wrap:balance' + (';text-align:center;margin-left:auto;margin-right:auto' if al == 'center' else ';text-align:left')
        cat = f'<div class="cat">{lab(h.get("category"), light)}{lab(h.get("fact"), light)}</div>'
        shot = (not media) and d.get('kind') == 'software' and src
        body_ = f'<div class="wrap hero-in al-{al} place-{place}">{cat}<h1 class="h1" style="{hsty}">{h1}</h1><p class="lede{" light" if light else ""}">{e(h.get("lede"))}</p><div class="ctas">{cta_html(light)}{secondary_cta(light)}</div></div>'
        if not media and src and not hui.get('move') and d.get('kind') in ('place', 'service', 'product') and (images.get(h.get('media')) or {}).get('w', 0) >= 900: hui = {**hui, 'move': 'split'}
        if RECIPE and not (h.get('ui') or {}).get('move'): hui = {**hui, 'move': RECIPE.get('hero', hui.get('move'))}
        mv = hui.get('move')
        if mv == 'centre':
            hsty2 = hsty.replace('text-align:left', 'text-align:center') + ';margin-left:auto;margin-right:auto;max-width:16ch'
            shotp = (f'<div class="wrap shotwrap"><div class="shotframe"><img src="{src}" alt="{source_alt(src)}"></div></div>' if soft else f'<div class="wrap"><figure class="inset-v" data-sig="parallax"><img src="{src}" alt="{source_alt(src)}"></figure></div>') if src else ''
            return f'<section class="sec hero centre{" shot" if shotp else ""}" id="top"><div class="wrap hero-in al-center">{cat}<h1 class="h1" style="{hsty2}">{h1}</h1><p class="lede" style="margin-left:auto;margin-right:auto;text-align:center">{e(h.get("lede"))}</p><div class="ctas" style="justify-content:center">{cta_html()}{secondary_cta()}</div></div>{shotp}</section>'
        if mv in ('photo', 'poster', 'inset') and src:
            over = mv in ('photo', 'poster'); inset = mv == 'inset'
            ppx = min(hpx * 1.25, int(2 * 1150 / ((0.7 if upper else 0.56) * max(12, nch)))) if mv == 'poster' else hpx
            h1s = hsty if not over else re.sub(r'--hero-size:[^;]+', f'--hero-size:{clampf(ppx)}', hsty)
            body_ = f'<div class="wrap hero-in al-{al}{" light" if over else ""}">{cat}<h1 class="h1" style="{h1s}">{h1}</h1><p class="lede">{e(h.get("lede"))}</p><div class="ctas">{cta_html()}{secondary_cta()}</div></div>'
            if inset: return f'<section class="sec hero inset" id="top">{body_}<div class="wrap"><figure class="inset-v" data-sig="parallax"><img src="{src}" alt="{source_alt(src)}"></figure></div></section>'
            return f'<section class="sec hero has-media {mv}" id="top" style="min-height:100svh"><div class="media"><img src="{src}" alt="{source_alt(src)}"></div>{body_}</section>'
        if hui.get('move') == 'split' and src:
            # SIGNATURE split hero: words left, the product right, full height; the product drifts up slower than the page
            spx = min(hpx, int(3 * 640 / ((0.7 if upper else 0.56) * max(12, nch)))); hsty2 = re.sub(r'--hero-size:[^;]+', f'--hero-size:{clampf(spx)}', re.sub(r'max-width:[^;]+', 'max-width:11ch', hsty))
            left = f'<div class="split-l">{cat}<h1 class="h1" style="{hsty2}">{h1}</h1><p class="lede">{e(h.get("lede"))}</p><div class="ctas">{cta_html()}{secondary_cta()}</div></div>'
            right = f'<div class="split-r"><div class="shotframe tall{" product-shot" if d.get("kind") == "software" else ""}" data-sig="parallax"><img src="{src}" alt="{source_alt(src)}"></div></div>'
            return f'<section class="sec hero split" id="top"><div class="wrap split-wrap">{left}{right}</div></section>'
        if shot: body_ += f'<div class="wrap shotwrap"><div class="shotframe"><img src="{src}" alt="{source_alt(src)}"></div></div>'
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

    ZOOMS = [('50% 50%', 1.0), ('30% 35%', 1.3), ('70% 40%', 1.3), ('50% 70%', 1.25), ('25% 65%', 1.35), ('75% 70%', 1.3)]
    def pick_visuals(bt, n, strict=False):
        """Use the assigned image for strict moves, with alternate crops for their frames."""
        out_ = []
        if strict:
            own = images.get(bt.get('image'))
            if not own or not own.get('data') or own.get('w', 0) < 760 or is_used(own.get('id')) or not free_for(own, bt) or dark_background_texture(own): return []
            src = img(own['id'])
            return [(src, ZOOMS[i % len(ZOOMS)]) for i in range(n)]
        if bt.get('image') and images.get(bt['image']) and not is_used(bt['image']) and images[bt['image']].get('w', 0) >= 500: out_.append((img(bt['image']), ZOOMS[0]))
        pool = [i for i in images.values() if i.get('data') and not is_used(i.get('id')) and free_for(i, bt) and i.get('w', 0) >= 600]
        pool.sort(key=lambda i: (not i.get('detail'), not i.get('gen'), -(i.get('w', 0) * i.get('h', 0))))
        for it in pool:
            if len(out_) >= n: break
            out_.append((img(it['id']), ZOOMS[0]))
        return out_

    def sticky_product(sec, bt):
        """SIGNATURE: text blocks scroll on the left, the product stays pinned on the right and swaps per block."""
        items = beat_items(bt)
        if len(items) < 2 or len(items) > 5: return numbers(sec, bt) if bt['type'] == 'facts' else cards(sec, bt)
        vis = pick_visuals(bt, len(items), strict=True)
        if not vis: return numbers(sec, bt) if bt['type'] == 'facts' else cards(sec, bt)
        rows = ''
        for i, (title, body) in enumerate(items):
            # Steps already use the ordinal as their internal title. Put the
            # actual step in the heading, rather than displaying 01 twice.
            heading, description = (body, '') if bt['type'] == 'steps' else (title, body)
            paragraph = f'<p>{e(description)}</p>' if description else ''
            rows += f'<div class="sp-row" data-i="{i}"><span class="lab">{e(f"0{i + 1}")}</span><h3 class="h3">{e(heading)}</h3>{paragraph}</div>'
        product_shot = d.get('kind') == 'software'
        frames = ''.join(f'<figure class="sp-f{" on" if i == 0 else ""}" data-i="{i}"><img src="{vis[i % len(vis)][0]}" alt="" style="object-position:{"center" if product_shot else vis[i % len(vis)][1][0]};transform:scale({1 if product_shot else vis[i % len(vis)][1][1]})"></figure>' for i in range(len(items)))
        return f'<section class="sec sticky band-{band_of(sec, bt)}" id="{e(bt["id"])}" data-sig="sticky"><div class="wrap">{ghead(sec, bt)}<div class="sp"><div class="sp-text">{rows}</div><div class="sp-pin"><div class="sp-stage{" product-shot" if product_shot else ""}">{frames}</div></div></div></div></section>'

    def marquee(sec, bt):
        """SIGNATURE: a slow ticker of the beat's own words (titles / facts / prices); doubles as a breath between screens."""
        items = beat_items(bt)
        # A ticker is for short phrases, not a substitute for a long list or
        # a component with detailed descriptions. Never silently trim it.
        if bt['type'] in ('features', 'steps', 'faq') or len(items) > 10:
            return cards(sec, bt)
        words_ = [f'{t}' if b_ is None or b_ == '' else f'{t} — {b_}' for t, b_ in items] or [bt.get('h2') or b['name']]
        if any(len(str(w).split()) > 12 for w in words_): return cards(sec, bt)
        while 0 < len(words_) < 6: words_ = words_ + words_  # a ticker needs a track longer than the screen: repeat short lists
        track = ''.join(f'<span class="mq-i">{e(w)}<i>✦</i></span>' for w in words_)
        head = ghead(sec, bt)
        own = bt.get('image') if bt.get('type') not in ('facts', 'cells') and bt.get('image') and images.get(bt['image']) and photo_like(images[bt['image']], minw=900) else None
        lead_src = img(own) if own else ''
        lead = f'<figure class="lead" style="aspect-ratio:{max(1.3, min(2.4, images[own]["w"] / max(1, images[own]["h"])))}"><img src="{lead_src}" alt="{source_alt(lead_src)}"></figure>' if lead_src else ''
        static = ''.join(f'<li><span>{e(t)}</span>{("<span>" + e(body) + "</span>") if body is not None and body != "" else ""}</li>' for t, body in items)
        heading = f'<div class="wrap">{head}{lead}</div>' if head or lead else ''
        return f'<section class="sec marquee band-{band_of(sec, bt)}" id="{e(bt["id"])}" data-sig="marquee">{heading}<div class="mq" aria-hidden="true"><div class="mq-track">{track}{track}</div></div><div class="marquee-static"><ul class="wrap">{static}</ul></div></section>'

    def pinned_sequence(sec, bt):
        """SIGNATURE: the section pins; each step takes over the screen as you scroll (number, sentence, visual)."""
        items = beat_items(bt)
        def static_fallback():
            if bt['type'] == 'facts': return numbers(sec, bt)
            ui = dict(bt.get('ui') or {})
            # A single column described the pinned stage, not its card fallback.
            if ui.get('cols') == 1 and len(items) >= 3: ui.pop('cols', None)
            # Keep only a deliberately assigned, available image. Do not let
            # the generic steps fallback pick a different, unrelated image.
            assigned = ui.get('lead') or bt.get('image')
            image = images.get(assigned) if isinstance(assigned, str) else None
            usable = (image and image.get('data') and image.get('w', 0) >= 900
                      and not is_used(assigned) and free_for(image, bt) and not dark_background_texture(image))
            ui['lead'] = assigned if usable else ''
            return cards(sec, {**bt, 'ui': ui})
        # Pinning gives this section a fixed scroll height. Its sticky stage
        # can cover content appended after the stage, so use a normal flow for
        # beats with an additional note or action.
        source_ids = bt.get('source_sections') if isinstance(bt.get('source_sections'), list) else []
        has_source_actions = any(source_owner.get(str(sid), (None, None))[1] == bt.get('id') and
                                 source_sections.get(str(sid), {}).get('sourceActionsVersion') == 1 and
                                 bool(source_sections.get(str(sid), {}).get('sourceActions')) for sid in source_ids)
        if bt.get('note') or bt.get('cta') or bt.get('cta2') or has_source_actions:
            return static_fallback()
        if len(items) < 2 or len(items) > 5: return static_fallback()
        # A section-level photo is not evidence that it depicts an individual offer.
        vis = [] if bt['type'] in ('features', 'facts') else pick_visuals(bt, len(items), strict=True)
        slides = ''
        for i, (title, body) in enumerate(items):
            numeric = bt['type'] != 'features' and bool(re.search(r'\d', str(title)))
            if bt['type'] == 'facts':
                value = str(title).strip()
                numeric = len(value) <= 12 and bool(re.fullmatch(r'[\d\s.,%+\-–/:€$£]+', value))
            number = title if numeric else '' if bt['type'] == 'facts' else f'0{i + 1}'
            heading = body if numeric else title
            description = f'<p class="lede">{e(body)}</p>' if not numeric and body else ''
            number_html = f'<b class="num">{e(number)}</b>' if number else ''
            picture = ''
            if bt['type'] == 'features':
                feature = bt['features'][i]
                image_id = feature.get('image')
                image = images.get(image_id) if isinstance(image_id, str) else None
                usable = image and image.get('data') and image.get('w', 0) >= 600 and not is_used(image_id) and free_for(image, bt) and not dark_background_texture(image) and (not image.get('shot') or image.get('detail') or image.get('gen'))
                if usable:
                    src = img(image_id)
                    image_width = image.get('w', 0)
                    try:
                        from PIL import Image
                        import io
                        with Image.open(io.BytesIO(base64.b64decode(src.split(',', 1)[1]))) as source:
                            image_width = source.width
                    except Exception: pass
                    picture = f'<figure class="ps-v item-visual" style="--ps-image-max:{round(image_width * 1.35)}px"><img src="{src}" alt="{source_alt(src)}"></figure>'
            elif vis:
                src, (position, zoom) = vis[i % len(vis)]
                picture = f'<figure class="ps-v"><img src="{src}" alt="" style="object-position:{position};transform:scale({zoom})"></figure>'
            heading_style = 'font-size:var(--h3);max-width:22ch' if picture else 'font-size:clamp(32px,4vw,56px);max-width:100%'
            slides += f'<div class="ps-s{" on" if i == 0 else ""}{" no-visual" if not picture else ""}" data-i="{i}"><div class="ps-t">{number_html}<h3 class="h2" style="{heading_style}">{e(heading)}</h3>{description}</div>{picture}</div>'
        return f'<section class="sec pinned band-{band_of(sec, bt)}" id="{e(bt["id"])}" data-sig="pinned" data-n="{len(items)}"><div class="ps-sticky"><div class="wrap">{ghead(sec, bt)}<div class="ps-stage">{slides}</div><div class="ps-dots">{"".join("<i></i>" for _ in items)}</div></div></div></section>'

    def type_wall(sec, bt):
        """SIGNATURE: one statement in giant type; the words light up one by one as you scroll through it."""
        big = bt.get('big') if bt['type'] == 'quote' else ''
        body = bt.get('body') if bt['type'] == 'quote' else (bt.get('lede') or bt.get('h2') or '')
        text = big or body
        if not big and (len(str(text).split()) < 10 or len(str(text).split()) > 48): return statement_v(sec, bt, 'wide')
        ws = ''.join(f'<span class="tw-w">{e(w)}</span> ' for w in str(text).split())
        caption = f'<p class="tw-caption">{e(body)}</p>' if big and body and big != body else ''
        who = f'<p class="lab who">{e(bt["who"])}</p>' if bt.get('who') else ''
        prominent = bool(big and len(str(big)) <= 30 and len(str(big).split()) <= 6)
        return f'<section class="sec typewall band-{band_of(sec, bt)}" id="{e(bt["id"])}" data-sig="typewall"><div class="tw-sticky"><div class="wrap{" tw-prominent" if prominent else ""}">{lab(bt.get("label"))}<h2 class="tw{" tw-title" if big else ""}">{ws}</h2>{caption}{who}</div></div></section>'

    def story(sec, bt, flip=False):
        """Text beside a visual, alternating sides; the visual reveals with a clip."""
        if bt['type'] == 'photo':
            own = images.get(bt.get('image'))
            if not own or not photo_like(own, 500) or not free_for(own, bt):
                return photo_sec(sec, bt)
            src = img(own['id'])
            image_width = own.get('w', 0)
            image_height = own.get('h', 0)
            try:
                from PIL import Image
                import io
                with Image.open(io.BytesIO(base64.b64decode(src.split(',', 1)[1]))) as source:
                    image_width = source.width
                    image_height = source.height
            except Exception: pass
            details = ''.join(f'<li>{e(item)}</li>' for item in (bt.get('cap') or []) if item)
            details = f'<ul class="photo-details">{details}</ul>' if details else ''
            heading_style = re.sub(r'max-width:[^;]+;?', '', head_style(sec, bt=bt))
            heading_style = re.sub(r'font-size:', '--story-heading-size:', heading_style)
            lede_html = f'<p class="lede">{e(bt.get("lede"))}</p>' if bt.get('lede') else ''
            text = f'<div class="st-t">{lab(bt.get("label"))}<h2 class="h2" style="{heading_style}">{e(bt.get("h2") or "")}</h2>{lede_html}{details}</div>'
            ratio = image_width / max(1, image_height)
            figure = f'<figure class="st-v" style="--story-image-max:{round(image_width * 1.35)}px;--story-ratio:{ratio:.6f};aspect-ratio:{ratio:.6f}"><img src="{src}" alt="{source_alt(src)}"></figure>'
            caps = bt.get('cap') or []
            headline = str(bt.get('h2') or '')
            lede = str(bt.get('lede') or '')
            editorial = (d.get('kind') == 'place' and image_width >= 900 and 1.2 <= ratio <= 2
                         and bool(headline) and len(headline) <= 40 and all(len(w) <= 15 for w in headline.split())
                         and len(str(bt.get('label') or '')) <= 40 and len(lede) <= 140
                         and len(caps) <= 2 and all(len(str(item)) <= 30 for item in caps)
                         and len(headline) + len(lede) + sum(len(str(item)) for item in caps) <= 200)
            cls = ' story-editorial' if editorial else ''
            style = f' style="--editorial-image-max:{round(image_width * 1.35)}px"' if editorial else ''
            return f'<section class="sec story story-photo{cls} band-{band_of(sec, bt)}" id="{e(bt["id"])}"{style}><div class="wrap st">{text}{figure}</div></section>'
        if bt['type'] == 'quote': bt = {**bt, 'h2': bt.get('big') or '', 'lede': bt.get('body') or '', 'label': bt.get('label') or bt.get('who') or ''}
        items = beat_items(bt)
        def without_story_image():
            # Cards must not independently reintroduce the rejected image or
            # auto-pick a different screenshot through lead_fig().
            return cards(sec, {**bt, 'ui': {**(bt.get('ui') or {}), 'lead': ''}})
        assigned = bt.get('image')
        own = images.get(assigned) if assigned else None
        assigned_usable = (own and own.get('data') and not is_used(assigned) and free_for(own, bt)
                           and own.get('w', 0) >= 640 and not dark_background_texture(own) and not symbolic_asset(own))
        if len(items) > 4:
            if bt['type'] == 'facts': return numbers(sec, bt)
            lead = (bt.get('ui') or {}).get('lead')
            if (assigned and not assigned_usable) or (lead and images.get(lead) and symbolic_asset(images[lead])): return without_story_image()
            return cards(sec, bt)
        if assigned:
            # A missing, reserved, tiny or symbolic assigned visual is not
            # permission to pick an unrelated fallback image for this beat.
            if not assigned_usable: return without_story_image()
            src = img(assigned)
        else:
            pool = [i for i in images.values() if photo_like(i, 640) and free_for(i, bt)]
            src = img(pool[0]['id']) if pool else ''
        if not src: return without_story_image()
        lst = ''.join(f'<li><b>{e(t)}</b><span>{e(b_)}</span></li>' for t, b_ in items)
        lede_html = f'<p class="lede">{e(bt.get("lede"))}</p>' if bt.get('lede') else ''
        txt = f'<div class="st-t">{lab(bt.get("label"))}<h2 class="h2" style="{re.sub(r"max-width:[^;]+;?", "", head_style(sec, bt=bt))}">{e(bt.get("h2") or "")}</h2>{lede_html}<ul class="st-l">{lst}</ul></div>'
        fig = f'<figure class="st-v"><img src="{src}" alt="{source_alt(src)}"></figure>'
        return f'<section class="sec story{" flip" if flip else ""} band-{band_of(sec, bt)}" id="{e(bt["id"])}"><div class="wrap st">{txt}{fig}</div></section>'

    def photo_caption(bt, title=True):
        if not bt: return ''
        heading = f'<h2 class="h2" style="{head_style({}, bt=bt)}">{e(bt["h2"])}</h2>' if title and bt.get('h2') else ''
        lede = f'<p class="cap">{e(bt["lede"])}</p>' if bt.get('lede') else ''
        details = ''.join(f'<li>{e(item)}</li>' for item in (bt.get('cap') or []) if item)
        details = f'<ul class="photo-details">{details}</ul>' if details else ''
        return f'<div class="photo-caption">{lab(bt.get("label"))}{heading}{lede}{details}</div>' if heading or lede or details or bt.get('label') else ''

    def photo_text_only(sec, bt):
        caption = photo_caption(bt)
        return f'<section class="sec photo band-{band_of(sec, bt)}" id="{e(bt["id"])}"><div class="wrap">{caption}</div></section>' if bt and caption else ''

    def big_photos(n, bt=None, minw=700):
        out_ = []
        if bt and bt.get('image') and images.get(bt['image']) and photo_like(images[bt['image']], minw): out_.append(img(bt['image']))
        pool = sorted([i for i in images.values() if photo_like(i, minw) and free_for(i, bt)], key=lambda i: -i.get('w', 0) * i.get('h', 0))
        for it in pool:
            if len(out_) >= n: break
            out_.append(img(it['id']))
        return out_
    def photo_pair(sec, bt=None):
        ps = big_photos(2, bt)
        if len(ps) < 2: return photo_sec(sec, bt) if ps else photo_text_only(sec, bt)
        cap = f'<div class="wrap">{photo_caption(bt)}</div>' if bt else ''
        return f'<section class="sec photos" id="{e(bt["id"]) if bt else ""}"><div class="wrap pair"><figure style="width:58%;aspect-ratio:1.25"><img src="{ps[0]}" alt="{source_alt(ps[0])}"></figure><figure style="width:38%;aspect-ratio:.85;margin-top:12%"><img src="{ps[1]}" alt="{source_alt(ps[1])}"></figure></div>{cap}</section>'
    def collage(sec, bt=None):
        ps = big_photos(3, bt)
        if len(ps) < 2: return photo_sec(sec, bt) if ps else photo_text_only(sec, bt)
        tiles = ''.join(f'<figure class="c{i + 1}"><img src="{p_}" alt="{source_alt(p_)}"></figure>' for i, p_ in enumerate(ps))
        return f'<section class="sec collage" id="{e(bt["id"]) if bt else ""}"><div class="wrap cl">{tiles}</div><div class="wrap">{photo_caption(bt)}</div></section>'
    def overlay(sec, bt=None, variant=''):
        ps = big_photos(1, bt, minw=1100)  # edge to edge at 1440: anything narrower upscales into a blur
        if not ps: return statement(sec, ('lede', bt)) if bt and bt.get('lede') else ''
        bt = bt or {}; title = bt.get('h2') or bt.get('big') or ''; items = beat_items(bt) if bt else []
        if not title and not bt.get('lede'):  # a filler picture is a picture, not a chapter: no brand name stamped on it
            return f'<section class="sec overlay chapter bare" id="{e(bt.get("id", ""))}" data-sig="parallax"><figure class="ov-bg"><img src="{ps[0]}" alt=""></figure></section>'
        rows = ''.join(f'<li><span>{e(t)}</span><i></i><b>{e(x)}</b></li>' for t, x in items) if bt.get('type') in ('ledger', 'facts') else ''
        lede_html = f'<p class="lede">{e(bt.get("lede"))}</p>' if bt.get('lede') else ''
        rows_html = f'<ul class="rows light">{rows}</ul>' if rows else ''
        return f'<section class="sec overlay{" chapter" if variant == "chapter" else ""}" id="{e(bt.get("id", ""))}" data-sig="parallax"><figure class="ov-bg"><img src="{ps[0]}" alt=""></figure><div class="wrap ov-in light">{lab(bt.get("label"), True)}<h2 class="h2 light" style="{re.sub(r"max-width:[^;]+;?", "", head_style(sec))}">{e(title)}</h2>{lede_html}{rows_html}</div></section>'
    def quote_band(sec, bt, variant=''):
        text = bt.get('body') or bt.get('lede') or ''; who = f'<p class="lab who">{e(bt["who"])}</p>' if bt.get('who') else ''
        band = 'accent' if variant == 'accent' else 'dark'
        return f'<section class="sec qband band-{band}{" center" if variant == "centre" else ""}" id="{e(bt["id"])}"><div class="wrap"><p class="qb">{e(text)}</p>{who}</div></section>'
    def rail(sec, bt):
        items = beat_items(bt); cands = [i for i in images.values() if photo_like(i) and free_for(i, bt)]
        # Long lists need a normal responsive grid, not a hidden-scrollbar
        # horizontal rail where later items are easily missed on phones.
        if len(items) > 8: return cards(sec, bt)
        ps = [img(i['id']) for i in cands[:len(items)]] if len(cands) >= min(3, len(items)) else []  # a rail with pictures on some cards and not others looks broken: all or none
        cards_ = ''
        for i, (t, x) in enumerate(items):
            figure = f'<figure><img src="{ps[i]}" alt="{source_alt(ps[i])}"></figure>' if i < len(ps) and ps[i] else ''
            cards_ += f'<article class="rc">{figure}<span class="lab">{e(f"0{i + 1}")}</span><h3 class="h3">{e(t)}</h3><p>{e(x)}</p></article>'
        return f'<section class="sec railsec band-{band_of(sec, bt)}" id="{e(bt["id"])}"><div class="wrap">{ghead(sec, bt)}</div><div class="rail" data-sig="rail"><div class="rail-in">{cards_}</div></div></section>'
    def numbers(sec, bt):
        items = beat_items(bt)
        if not items: return ''
        cells_ = ''.join(f'<div><b class="num">{e(t)}</b><p>{e(x)}</p></div>' for t, x in items)
        return f'<section class="sec numbers band-{band_of(sec, bt)}" id="{e(bt["id"])}"><div class="wrap">{ghead(sec, bt)}<div class="nums" style="--n:{min(4, len(items))}">{cells_}</div></div></section>'
    def stickers(sec, bt):
        items = beat_items(bt)
        if len(items) > 8 or any(body is not None and body != '' for _, body in items): return cards(sec, bt)
        pills = ''.join(f'<span class="stk" style="--r:{(i % 5 - 2) * 2.2}deg">{e(t)}</span>' for i, (t, _) in enumerate(items))
        lede = bt.get('lede') or (items[0][1] if items else '')
        lede_html = f'<p class="lede" style="margin:28px auto 0">{e(lede)}</p>' if lede else ''
        return f'<section class="sec stickers band-accent" id="{e(bt["id"])}"><div class="wrap center">{lab(bt.get("label"))}<h2 class="h2" style="{re.sub(r"max-width:[^;]+;?", "", head_style(sec))}">{e(bt.get("h2") or "")}</h2><div class="stks">{pills}</div>{lede_html}</div></section>'
    def product_row(sec, bt):
        items = beat_items(bt); n = min(4, max(2, len(items)))
        cards_ = ''
        for i, (t, x) in enumerate(items):
            pc = next((i for i in images.values() if photo_like(i) and free_for(i, bt)), None); pic = img(pc['id']) if pc else ''
            figure = f'<figure><img src="{pic}" alt="{source_alt(pic)}"></figure>' if pic else '<figure class="ph"></figure>'
            cards_ += f'<article class="pr">{figure}<div class="pr-t"><h3 class="h3">{e(t)}</h3><b>{e(x)}</b></div></article>'
        return f'<section class="sec products band-{band_of(sec, bt)}" id="{e(bt["id"])}"><div class="wrap">{ghead(sec, bt)}<div class="prs" style="--n:{n}">{cards_}</div></div></section>'
    def statement_v(sec, bt, variant=''):
        kind = 'quote' if bt['type'] == 'quote' else 'lede'
        if kind == 'lede' and not bt.get('lede'): return ''
        sec2 = dict(sec); hd = dict(sec.get('head') or {})
        if variant == 'right': hd['x'] = .45; hd['wf'] = .55; hd['al'] = 'left'
        if variant == 'left': hd['x'] = 0; hd['wf'] = .6; hd['al'] = 'left'
        if variant == 'wide': hd['x'] = 0; hd['wf'] = .9; hd['al'] = 'left'
        if variant == 'upper': hd['tt'] = 'uppercase'; hd['al'] = 'center'; hd['wf'] = .9
        sec2['head'] = hd; return statement(sec2, (kind, bt))
    SIG = {'sticky-product': sticky_product, 'marquee': marquee, 'pinned-sequence': pinned_sequence, 'type-wall': type_wall, 'story': story}

    def statement(sec, item):
        kind, bt = item; text = bt.get('body') if kind == 'quote' else bt.get('lede'); big = bt.get('big') if kind == 'quote' else bt.get('h2')
        if kind == 'quote' and not big and text and len(str(text).split()) <= 14: big, text = text, ''  # one short line is the statement itself, set big — not a caption in a band
        who = f'<p class="lab who">{e(bt["who"])}</p>' if kind == 'quote' and bt.get('who') else ''
        hd = sec.get('head') or {}; px_ = hd.get('px') or H2['px']
        inner = f'{lab(bt.get("label"))}<h2 class="h2" style="{head_style(sec)}">{e(big)}</h2>' if big and px_ >= 40 else lab(bt.get('label'))
        body_px = (sec.get('body') or {}).get('px') or BO['px']
        centered = (hd.get('al') == 'center')
        return f'<section class="sec statement band-{band_of(sec, bt)}" id="{e(bt["id"])}" style="min-height:{(min(1.0, max(.5, sec.get("screens", .8))) * 100) if len(str(text or "").split()) > 45 else 0}svh"><div class="wrap{" center" if centered else ""}" style="{col_style(sec)}">{inner}<p class="big-p" style="font-size:{clampf(max(body_px, 22), .7)}{";margin-left:auto;margin-right:auto" if centered else ""}">{e(text)}</p>{who}</div></section>'

    def photo_sec(sec, bt=None):
        ms = sec_media(sec) or [{'ar': 1.6, 'wf': 1, 'bleed': True}]
        if not bt and len(ms) >= 2 and ms[0].get('wf', 1) < .7:
            candidates = [i for i in images.values() if i.get('data') and not is_used(i.get('id')) and free_for(i, bt)]
            candidates.sort(key=lambda i: (i.get('id') != (bt or {}).get('image'), bool(i.get('shot')), -(i.get('w', 0) * i.get('h', 0))))
            selected = []
            for it in candidates:
                if not is_used(it.get('id')): selected.append(img(it['id']))
                if len(selected) == 2: break
            if selected:
                tiles = ''.join(f'<figure style="width:{round(m["wf"] * 100)}%;aspect-ratio:{m["ar"]}"><img src="{src}" alt="{source_alt(src)}"></figure>' for m, src in zip(ms, selected))
                cap = photo_caption(bt)
                caption = f'<div class="wrap">{cap}</div>' if cap else ''
                return f'<section class="sec photos band-{sec.get("band") or "paper"}" id="{e(bt["id"]) if bt else ""}"><div class="wrap pair">{tiles}</div>{caption}</section>'
            return photo_text_only(sec, bt) if bt else ''
        m = ms[0]; bleed = m.get('bleed') or m.get('wf', 1) > .95
        want = bt.get('image') if bt else None
        if bt and not want: return photo_text_only(sec, bt)
        # A square or portrait photograph paired with a heading works better as
        # one editorial composition than as a giant picture followed by a
        # caption below the fold. Leave panoramas and explicit overlays alone.
        own = images.get(want) if want else None
        if bt and soft and own and own.get('shot'):
            # Product UI is content, not a photographic backdrop. The heading
            # must not overlay the screenshot: its unknown colours make text
            # illegible, and cover-cropping can remove important UI details.
            if not own.get('data') or own.get('w', 0) < 400 or is_used(want) or not free_for(own, bt):
                return photo_text_only(sec, bt)
            src = img(want)
            image_width = own.get('w', 0)
            try:
                from PIL import Image
                import io
                with Image.open(io.BytesIO(base64.b64decode(src.split(',', 1)[1]))) as source:
                    image_width = source.width
            except Exception: pass
            caption = photo_caption(bt)
            return f'<section class="sec photo ui-photo band-{band_of(sec, bt)}" id="{e(bt["id"])}"><div class="wrap">{caption}<figure class="ui-shot" style="max-width:{int(image_width)}px"><img src="{src}" alt="{source_alt(src)}"></figure></div></section>'
        if (bt and own and d.get('kind') != 'software' and not sec.get('head')
                and (bt.get('h2') or bt.get('lede')) and photo_like(own, 500)
                and free_for(own, bt) and own.get('w', 0) / max(1, own.get('h', 0)) < 1.5):
            return story(sec, bt)
        if want and images.get(want) and images[want].get('w', 0) < 900:
            # a photo screen is wrap-wide or wider: never from a small source — but a beat that names its own picture (the founders, the room)
            # must not get a different one from the pool; the small picture sits at its natural size beside the caption instead
            it = images[want]
            if it.get('data') and it.get('w', 0) >= 400 and not is_used(it.get('id')) and free_for(it, bt) and bt.get('lede'):
                ar = max(.7, min(1.9, it['w'] / max(1, it['h']))); src = img(want)
                return f'<section class="sec photo inset band-{band_of(sec, bt)}" id="{e(bt["id"])}"><div class="wrap inset-wrap"><figure style="width:min(100%,{it["w"]}px);aspect-ratio:{ar:.3f}"><img src="{src}" alt="{source_alt(src)}"></figure>{photo_caption(bt)}</div></section>'
            return photo_text_only(sec, bt)
        big_pool = [i for i in images.values() if free_for(i, bt) and (photo_like(i, 900) if not soft else (i.get('data') and i.get('w', 0) >= 900 and not is_used(i.get('id'))))]
        if not want and not big_pool: bleed = False
        if d.get('kind') == 'software': bleed = False  # a product screenshot bled edge to edge reads as a dark void; software photos sit in a framed, contained figure
        if want:
            it = images.get(want)
            if not it or not it.get('data') or is_used(want) or not free_for(it, bt): return photo_text_only(sec, bt)
            src = img(want)
        elif big_pool:
            big_pool.sort(key=lambda i: (not i.get('shot') if (soft and not bleed) else bool(i.get('shot')), -(i.get('w', 0) * i.get('h', 0)))); it = big_pool[0]; src = img(it['id'])
        else: return photo_text_only(sec, bt)
        if not src: return photo_text_only(sec, bt)
        # Use the embedded pixel dimensions so older inventories with original
        # dimensions cannot stretch a downsampled image beyond its resolution.
        image_width = it.get('w', 0)
        try:
            from PIL import Image
            import io
            with Image.open(io.BytesIO(base64.b64decode(src.split(',', 1)[1]))) as source:
                image_width = source.width
        except Exception: pass
        max_width = round(image_width * 1.35)
        if max_width < 1440: bleed = False
        size = f'max-width:{max_width}px;margin:0 auto' if bleed else f'width:calc(100% - 2 * var(--frame));max-width:{max_width}px;margin:0 auto;border-radius:var(--radius);overflow:hidden'
        head = f'<div class="wrap over"><h2 class="h2 light" style="{head_style(sec)}">{e(bt["h2"])}</h2></div>' if bt and bt.get('h2') and sec.get('head') else ''
        cap = f'<div class="wrap">{photo_caption(bt, title=not head)}</div>' if bt else ''
        return f'<section class="sec photo{" bleed" if bleed else ""}" id="{e(bt["id"]) if bt else ""}"><figure style="aspect-ratio:{max(1.1, min(2.4, m["ar"]))};{size}"><img src="{src}" alt="{source_alt(src)}">{head}</figure>{cap}</section>'

    def ghead(sec, bt, light=False):
        if not bt.get('h2'):
            label = lab(bt.get('label'), light)
            lede = f'<p class="lede">{e(bt.get("lede"))}</p>' if bt.get('lede') else ''
            return f'<div class="gh one">{label}{lede}</div>' if lede else label
        st = re.sub(r'max-width:[^;]+;?', '', head_style(sec, bt=bt)); hm = (bt.get('ui') or {}).get('head')
        lede_html = f'<p class="lede">{e(bt.get("lede"))}</p>' if bt.get('lede') else ''
        if hm == 'center': return f'<div class="gh one center">{lab(bt.get("label"), light)}<h2 class="h2" style="{st}">{e(bt.get("h2"))}</h2>{lede_html}</div>'
        if hm == 'left': return f'<div class="gh one">{lab(bt.get("label"), light)}<h2 class="h2" style="{st}">{e(bt.get("h2"))}</h2>{lede_html}</div>'
        return f'<div class="gh"><div>{lab(bt.get("label"), light)}<h2 class="h2" style="{st}">{e(bt.get("h2"))}</h2></div>{lede_html or "<div></div>"}</div>'

    def lead_fig(ui_, bt):
        src = ''; it = None
        if ui_.get('lead'):
            lead = images.get(ui_['lead'])
            if not lead or not lead.get('data') or is_used(ui_['lead']) or not free_for(lead, bt) or lead.get('w', 0) < 900 or dark_background_texture(lead) or symbolic_asset(lead): return ''  # a lead is a full-width frame: never from a small source, a logo or a flat texture
            it = lead; src = img(ui_['lead'])
        elif ui_.get('lead') == '': return ''
        elif bt.get('image'):
            own = images.get(bt['image'])
            if not own or not own.get('data') or is_used(bt['image']) or not free_for(own, bt) or own.get('w', 0) < 900 or dark_background_texture(own) or symbolic_asset(own): return ''
            it = own; src = img(bt['image'])
        elif bt['type'] == 'facts':
            pool = [i for i in images.values() if photo_like(i, 600) and free_for(i, bt)]
            if pool: it = pool[0]; src = img(it['id'])
        elif bt['type'] == 'steps' and soft:
            pool = [i for i in images.values() if i.get('shot') and i.get('data') and not is_used(i.get('id')) and free_for(i, bt)]
            if pool: it = max(pool, key=lambda i: i.get('w', 0) * i.get('h', 0)); src = img(it['id'])
        if not src or not it: return ''
        if it.get('shot'):
            # A product UI is information, not a background: keep the entire
            # image and let its intrinsic size cap prevent upscaling.
            return f'<figure class="lead lead-shot"><img src="{src}" alt="{source_alt(src)}"></figure>'
        raw_ar = it.get('w', 16) / max(1, it.get('h', 9)); ar = max(1.0, min(2.4, raw_ar))
        narrow = raw_ar < 1.25  # a portrait or square picture is shown at its own shape, centred, not cropped to a banner
        return f'<figure class="lead{" narrow" if narrow else ""}" style="aspect-ratio:{ar}"><img src="{src}" alt="{source_alt(src)}" style="object-position:{"top" if narrow else "center"}"></figure>'

    def faq(sec, bt):
        rows = ''.join(f'<details><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in bt.get('items', []))
        bt = dict(bt); bt.setdefault('h2', 'Questions'); bt['h2'] = bt['h2'] or 'Questions'
        lede_html = f'<p class="lede">{e(bt["lede"])}</p>' if bt.get('lede') else ''
        return f'<section class="sec faq band-{band_of(sec, bt)}" id="{e(bt["id"])}"><div class="wrap two"><div>{lab(bt.get("label"))}<h2 class="h2" style="{re.sub(r"max-width:[^;]+;?", "", head_style(sec))}">{e(bt["h2"])}</h2>{lede_html}</div><div class="qa">{rows}</div></div></section>'

    def testimonials(sec, bt):
        from urllib.parse import urlsplit
        cards_ = []
        for item in bt.get('testimonials') or []:
            text, attribution, links = item.get('text'), item.get('attribution'), item.get('links') or []
            if not isinstance(text, str) or not text.strip() or not isinstance(attribution, str) or not attribution.strip() or len(links) > 1: continue
            link_html = ''
            if links:
                link = links[0]
                try:
                    url = urlsplit(link.get('url') or '')
                    if url.scheme not in ('http', 'https') or not url.hostname or url.username or url.password or not link.get('label'): continue
                except (ValueError, AttributeError): continue
                link_html = f'<a href="{e(link["url"])}">{e(link["label"])}</a>'
            cards_.append(f'<figure class="review-card"><blockquote>{e(text)}</blockquote><figcaption><span>{e(attribution)}</span>{link_html}</figcaption></figure>')
        if not cards_: return ''
        return f'<section class="sec reviews band-{band_of(sec, bt)}" id="{e(bt["id"])}"><div class="wrap">{ghead(sec, bt)}<div class="review-grid">{"".join(cards_)}</div></div></section>'

    def cards(sec, bt):
        if bt['type'] == 'faq': return faq(sec, bt)
        ms = sec_media(sec); n = max(2, min(4, len(ms) or 3)); ar = (ms[0]['ar'] if ms else 0.82)
        lead = ''; ui_ = bt.get('ui') or {}
        lead = lead_fig(ui_, bt)
        k = len(bt.get('features') or bt.get('cells') or bt.get('steps') or bt.get('facts') or bt.get('items') or [])
        if k in (3, 6, 9): n = 3
        elif k in (2, 4) and n > 2: n = 2 if k == 2 else 4
        elif k == 5: n = 3
        # A single-column marquee is a ticker setting, not a layout for the
        # cards used when the ticker cannot carry the beat's full content.
        # Preserve deliberate one-column card layouts selected as cards.
        ticker_fallback = ui_.get('move') == 'marquee' and ui_.get('cols') == 1 and k >= 3
        if not ticker_fallback: n = ui_.get('cols') or n
        variant = ui_.get('variant', '')
        if variant == 'wide2': n = 2
        items = []
        if bt['type'] == 'features': items = [(f.get('title'), f.get('body'), True, f.get('image')) for f in bt.get('features', [])]
        elif bt['type'] == 'cells': items = [(c[0], c[2] if len(c) > 2 else '', c[1], None) for c in bt.get('cells', [])]
        elif bt['type'] == 'steps': items = [(f'0{i + 1}', s, True, None) for i, s in enumerate(bt.get('steps', []))]
        elif bt['type'] == 'facts': items = [(f[0], f[1], None, None) for f in bt.get('facts', [])]
        elif bt['type'] == 'faq': items = [(q, a, None, None) for q, a in bt.get('items', [])]
        elif bt['type'] == 'ledger': return ledger(sec, bt)
        # Numeric facts should read as a typographic feature, not small card
        # headings with unrelated ordinal numbers beside them.
        numeric_facts = bt['type'] == 'facts' and bool(items) and all(
            re.fullmatch(r'[\d\s.,:/%+−–-]+', str(t or '')) and len(str(t)) <= 12 for t, _, _, _ in items)
        cells = ''
        for i, (t, body_, num, image_id) in enumerate(items):
            image = images.get(image_id) if isinstance(image_id, str) else None
            usable = image and image.get('data') and image.get('w', 0) >= 600 and not is_used(image_id) and free_for(image, bt) and not dark_background_texture(image) and (not image.get('shot') or image.get('detail') or image.get('gen'))
            src = img(image_id) if usable and not lead else ''
            pic = f'<figure style="aspect-ratio:{ar}"><img src="{src}" alt="{source_alt(src)}"></figure>' if src else ''
            value = str(num) if bt['type'] == 'cells' and num is not None else ''
            big = (f'<b class="num">{e(value)}</b>' if re.search(r'\d', value) else f'<span class="lab">{e(value)}</span>') if value.strip() else ''
            cells += f'<div class="card">{pic}{lab(f"0{i + 1}") if not big and bt["type"] != "steps" and not numeric_facts else ""}{big}<h3 class="h3">{e(t)}</h3><p>{e(body_)}</p></div>'
        return f'<section class="sec cards band-{band_of(sec, bt)}{" compact" if ui_.get("compact") else ""}{" facts-cards" if numeric_facts else ""}" id="{e(bt["id"])}"><div class="wrap">{ghead(sec, bt)}{lead}<div class="grid" style="--n:{n}">{cells}</div></div></section>'

    def ledger(sec, bt):
        its = list(bt.get('items', []))
        def price_class(p): return ' class="price-short"' if len(str(p)) <= 16 and re.fullmatch(r'[\d\s.,€$£¥%+−–-]+', str(p)) else ''
        def price_row(a, p):
            row_class = ' class="price-long"' if len(str(p)) > 9 else ''
            return f'<li{row_class}><span>{e(a)}</span><i></i><b{price_class(p)}>{e(p)}</b></li>'
        rows = ''.join(price_row(a, p) for a, p in its)
        link = cta_html(label=bt.get('cta'), href=action_url(bt.get('cta'), bt.get('cta_href'), include_forms=True))
        second_label = bt.get('cta2')
        second_target = action_url(second_label, bt.get('cta2_href'), include_forms=True) if second_label else ''
        if second_target:
            link += f'<a class="btn ghost" href="{e(second_target)}">{e(second_label)} <span class="ar">→</span></a>'
        own = images.get(bt.get('image'))
        visual = ''
        if own and photo_like(own, 600) and free_for(own, bt):
            src = img(own['id'])
            image_width, image_height = own['w'], own['h']
            try:
                from PIL import Image
                import io
                with Image.open(io.BytesIO(base64.b64decode(src.split(',', 1)[1]))) as source:
                    image_width, image_height = source.size
            except Exception: pass
            ar = max(.7, min(2.0, image_width / max(1, image_height)))
            visual = f'<figure class="lead ledger-visual" style="aspect-ratio:{ar:.3f};--ledger-image-max:{round(image_width * 1.35)}px;--ledger-image-height-max:{round(image_height * 1.35)}px"><img src="{src}" alt="{source_alt(src)}"></figure>'
        heading_style = re.sub(r'text-align:[^;]+;?|margin-(left|right):auto;?|max-width:[^;]+;?', '', head_style(sec, bt=bt))
        if not (bt.get('ui') or {}).get('h2_px'):
            heading_style = re.sub(r'font-size:[^;]+', 'font-size:clamp(36px,4.4vw,64px)', heading_style)
        label = str(bt.get('label') or '').strip()
        label_core = re.sub(r'^\s*0?\d{1,2}\s*[/.·—–-]?\s*', '', label).strip()
        eyebrow = '' if label_core.casefold() == str(bt.get('h2') or '').strip().casefold() else lab(label)
        text_intro = f'{eyebrow}<h2 class="h2" style="{heading_style}">{e(bt.get("h2"))}</h2><p class="lede">{e(bt.get("lede"))}</p>'
        intro = text_intro + visual
        move = (bt.get('ui') or {}).get('move')
        if move == 'cards':
            cols = (bt.get('ui') or {}).get('cols')
            cols = min(4, max(1, cols)) if isinstance(cols, int) and not isinstance(cols, bool) else 3
            amount_pattern = re.compile(r'^\s*(.+?)\s*·\s*((?:[$€£¥]|USD|EUR|GBP)\s*\d+(?:[.,]\d+)*|\d+(?:[.,]\d+)*\s*(?:[$€£¥]|USD|EUR|GBP)|free|custom)\s*$', re.I)
            def price_card(name, price):
                match = amount_pattern.fullmatch(name) if isinstance(name, str) else None
                if not match: return f'<li><span>{e(name)}</span><b>{e(price)}</b></li>'
                unit = f'<small>{e(price)}</small>' if price is not None and price != '' else ''
                return f'<li><span>{e(match.group(1).strip())}</span><div class="ledger-price"><b>{e(match.group(2))}</b>{unit}</div></li>'
            cards_ = ''.join(price_card(name, price) for name, price in its)
            return f'<section class="sec ledger ledger-cards band-{band_of(sec, bt)}" id="{e(bt["id"])}"><div class="wrap"><div class="ledger-cards-intro">{intro}</div><ul class="ledger-card-list" data-cols="{cols}" style="--ledger-cols:{cols}">{cards_}</ul><div class="ctas">{link}</div></div></section>'
        ticker = ''
        if move == 'marquee' and its:
            labels = [f'{name} — {price}' if price else str(name) for name, price in its[:10]]
            track = ''.join(f'<span class="mq-i">{e(label)}<i>✦</i></span>' for label in labels)
            ticker = f'<div class="mq ledger-ticker" aria-hidden="true"><div class="mq-track">{track}{track}</div></div>'
        if move == 'story' and visual:
            return f'<section class="sec ledger ledger-story band-{band_of(sec, bt)}" id="{e(bt["id"])}"><div class="wrap two"><div class="ledger-story-content">{text_intro}<ul class="rows">{rows}</ul><div class="ctas">{link}</div></div><div class="ledger-story-media">{visual}</div></div></section>'
        if move == 'sticky-product' and visual:
            return f'<section class="sec ledger ledger-sticky band-{band_of(sec, bt)}" id="{e(bt["id"])}"><div class="wrap two"><div class="ledger-sticky-content">{text_intro}<ul class="rows">{rows}</ul><div class="ctas">{link}</div></div>{visual}</div></section>'
        return f'<section class="sec ledger band-{band_of(sec, bt)}" id="{e(bt["id"])}">{ticker}<div class="wrap two{" no-visual" if not visual else ""}"><div class="ledger-intro">{intro}</div><div><ul class="rows">{rows}</ul><div class="ctas">{link}</div></div></div></section>'

    def two_col(sec, bt):
        cols_ = beat_items(bt)
        if len(cols_) > (3 if bt['type'] == 'steps' else 2):
            return numbers(sec, bt) if bt['type'] == 'facts' else cards(sec, bt)
        inner = ''.join(f'<div><h3 class="h2" style="{head_style(sec)}">{e(t)}</h3><p class="big-p" style="font-size:{clampf(BO["px"] + 2, .8)}">{e(x)}</p></div>' for t, x in cols_)
        ui_ = bt.get('ui') or {}; lead = lead_fig(ui_, bt)
        return f'<section class="sec twocol band-{band_of(sec, bt)}{" compact" if (bt.get("ui") or {}).get("compact") else ""}" id="{e(bt["id"])}"><div class="wrap">{ghead(sec, bt)}{lead}<div class="cols" style="--n:{len(cols_)}">{inner}</div></div></section>'

    cta_title_used = []
    def cta(sec, bt=None):
        title = (bt or {}).get('h2') or en.get('tag') or h.get('cta') or b['name']
        cta_title_used.append(title)
        title_style = head_style(sec, bt=bt)
        if len(str(title)) <= 35 and len(str(title).split()) <= 6:
            title_style = re.sub(r'font-size:[^;]+', 'font-size:clamp(42px,6vw,88px)', title_style)
        label = (bt or {}).get('cta') or h.get('cta')
        form = f'<div class="ctas">{cta_html(label=label, href=contact_target)}</div>'
        alt = ''.join(f'<span class="lab">{e(a)}</span>' for a in (bt or {}).get('alt', []))
        own = (bt or {}).get('image') or ((bt or {}).get('ui') or {}).get('lead')
        left = [images[own]] if own and images.get(own) and photo_like(images[own], 900) and free_for(images[own], bt) else []
        if (bt or {}).get('fields') and left:
            pic = img(left[0]['id'])
            return f'<section class="sec cta band-dark cta-pic" id="{e((bt or {}).get("id") or form_id)}"><div class="wrap cta2"><figure class="cta-v"><img src="{pic}" alt=""></figure><div class="cta-t">{lab((bt or {}).get("label"))}<h2 class="h2" style="{re.sub(r"text-align:[^;]+;?|margin-(left|right):auto;?", "", title_style)}">{e(title)}</h2>{form}<div class="alts">{alt}</div></div></div></section>'
        return f'<section class="sec cta band-dark" id="{e((bt or {}).get("id") or form_id)}" style="min-height:{min(.5, sec.get("screens", 1)) * 100}svh"><div class="wrap center">{lab((bt or {}).get("label"))}<h2 class="h2" style="{title_style}">{e(title)}</h2>{form}<div class="alts">{alt}</div></div></section>'

    def footer(sec):
        def text(value): return value.strip() if isinstance(value, str) else ''
        cols = en.get('cols') if isinstance(en.get('cols'), list) else []
        cols_ = ''
        for col in cols[:4]:
            if not isinstance(col, (list, tuple)) or len(col) != 2: continue
            title, items = text(col[0]), col[1] if isinstance(col[1], list) else []
            lines = ''.join(f'<li>{e(text(item))}</li>' for item in items if text(item))
            if not title and not lines: continue
            heading = f'<h5 class="lab">{e(title)}</h5>' if title else ''
            listing = f'<ul>{lines}</ul>' if lines else ''
            cols_ += f'<div>{heading}{listing}</div>'
        # Only fall back to links that can actually navigate from this preview
        # or were captured from the source, never invented footer destinations.
        links = ''
        if not cols_:
            present_ids = {'top'} | set(re.findall(r'<section\b[^>]*\bid="([^"]+)"', ''.join(out)))
            nav = d.get('nav') if isinstance(d.get('nav'), dict) else {}
            nav_items = nav.get('links') if isinstance(nav.get('links'), list) else []
            for item in nav_items:
                if not isinstance(item, (list, tuple)) or len(item) != 2: continue
                href, label = text(item[0]), text(item[1])
                if not label: continue
                fragment = href[1:] if href.startswith('#') else ''
                if fragment and re.fullmatch(r'[A-Za-z][\w:.-]*', fragment) and e(fragment) in present_ids:
                    target = '#' + fragment
                else:
                    target = action_url(label, href, include_forms=True) if href and not href.startswith('#') else ''
                if target: links += f'<li><a href="{e(target)}">{e(label)}</a></li>'
        band = sec.get('band') or ('dark' if C.get('bands') and C['bands'][-1] == 'dark' else 'paper')
        tag = text(en.get('tag'))
        if not tag or tag in cta_title_used: tag = text(b.get('name'))
        tagline = f'<p class="big-p">{e(tag)}</p>' if tag else ''
        columns = f'<div class="fcols">{cols_}</div>' if cols_ else ''
        navigation = f'<ul class="footer-nav">{links}</ul>' if links else ''
        legal = ''.join(f'<span>{e(text(en.get(key)))}</span>' for key in ('legal', 'next') if text(en.get(key)))
        legal = f'<div class="legal">{legal}</div>' if legal else ''
        if not (tagline or columns or navigation or legal): return ''
        return f'<footer class="sec end band-{band}" id="end"><div class="wrap">{tagline}{columns}{navigation}{legal}</div></footer>'

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
    if RECIPE:
        COMP = {'sticky-product': lambda sec, bt, v: sticky_product(sec, bt), 'pinned-sequence': lambda sec, bt, v: pinned_sequence(sec, bt), 'type-wall': lambda sec, bt, v: type_wall(sec, bt),
                'marquee': lambda sec, bt, v: marquee(sec, bt), 'story': lambda sec, bt, v: story(sec, bt), 'cards': lambda sec, bt, v: cards(sec, {**bt, 'ui': {**(bt.get('ui') or {}), 'variant': v}}),
                'two-col': lambda sec, bt, v: two_col(sec, bt), 'ledger': lambda sec, bt, v: ledger(sec, bt), 'faq': lambda sec, bt, v: faq(sec, bt), 'statement': lambda sec, bt, v: statement_v(sec, bt, v),
                'quote-band': lambda sec, bt, v: quote_band(sec, bt, v), 'photo': lambda sec, bt, v: photo_sec({**sec, 'media': [{'ar': 1.9 if v != 'tall' else 1.1, 'wf': 1, 'bleed': v == 'bleed'}]}, bt),
                'photo-pair': lambda sec, bt, v: photo_pair(sec, bt), 'collage': lambda sec, bt, v: collage(sec, bt), 'overlay': lambda sec, bt, v: overlay(sec, bt, v), 'rail': lambda sec, bt, v: rail(sec, bt),
                'numbers': lambda sec, bt, v: numbers(sec, bt), 'stickers': lambda sec, bt, v: stickers(sec, bt), 'product-row': lambda sec, bt, v: product_row(sec, bt), 'testimonials': lambda sec, bt, v: testimonials(sec, bt)}
        # beats that would render as an echo or an empty frame are not content: a quote that repeats the h1, a list with no rows, a label that is just the brand
        def _norm(t): return re.sub(r'[^a-z0-9]+', '', re.sub(r'<[^>]+>', '', str(t or '')).lower())
        h1n = _norm(h.get('h1'))
        def _sane(bt):
            bt['label'] = re.sub(r'^\s*\d{1,2}\s*[—–/·.-]\s*', '', str(bt.get('label') or ''))  # the template decides the order, so it owns the numbering
            if _norm(bt.get('label')) == _norm(b['name']): bt['label'] = ''
            if bt['type'] == 'quote':
                big, body = bt.get('big') or '', bt.get('body') or ''
                if _norm(big) and _norm(big) == h1n: bt['big'] = ''; big = ''
                return bool(_norm(big) or (_norm(body) and _norm(body) != h1n))
            if bt['type'] in ('features', 'steps', 'cells', 'ledger', 'facts', 'faq'): return len(beat_items(bt)) >= 1
            return True
        beats = [bt for bt in beats if _sane(bt)]
        remaining = [bt for bt in beats if bt['type'] != 'form']; form_bt = next((bt for bt in beats if bt['type'] == 'form'), None)
        renderable = [bt for bt in remaining if bt['type'] != 'testimonials' or testimonials({}, bt)] + ([form_bt] if form_bt else [])
        assign_source_owners(renderable)
        def sec_for(comp):
            fam = 'statement' if comp in ('statement', 'quote-band', 'type-wall') else 'photo' if comp in ('photo', 'photo-pair', 'collage', 'overlay') else 'cta' if comp.startswith('cta') else 'list'
            return take(fam)
        def component_for(bt, fallback):
            kind = bt['type']; move = (bt.get('ui') or {}).get('move'); count = len(beat_items(bt))
            if kind == 'testimonials': return 'testimonials'
            if kind == 'ledger': return 'ledger'
            if kind == 'photo': return 'story' if move == 'story' else 'photo'
            if move == 'type-wall' and kind == 'quote': return move
            if move == 'sticky-product' and kind in ('features', 'steps', 'cells', 'facts') and 2 <= count <= 5: return move
            if move == 'pinned-sequence' and kind in ('steps', 'features', 'facts'): return move
            if move == 'story' and kind in ('features', 'steps', 'cells', 'facts') and count <= 4: return move
            if move == 'marquee' and kind in ('cells', 'facts') and 0 < count <= 10 and all(len(str(t).split()) <= 5 for t, _ in beat_items(bt)): return move
            if move == 'cards' and kind in ('features', 'steps', 'cells', 'facts', 'faq'): return move
            if kind in ('features', 'steps', 'cells', 'facts', 'faq') and fallback in ('statement', 'quote-band', 'type-wall'):
                return 'numbers' if kind == 'facts' else 'cards'
            if fallback == 'pinned-sequence' and not 2 <= count <= 5: return 'cards'
            if kind == 'facts' and fallback == 'overlay': return 'numbers'
            return fallback
        # Match each recipe slot to a real direction beat, then follow the UX agent's narrative order.
        plan = []; claimed = []
        for slot in RECIPE['slots']:
            accepts = ['photo' if t == 'photo*' else t for t in slot['accepts']]
            bt = next((x for x in remaining if (x['type'] in accepts or x['type'] == 'testimonials' and 'quote' in accepts) and x not in claimed), None)
            if bt is not None: claimed.append(bt)
            plan.append((slot, bt))
        order = {bt['id']: i for i, bt in enumerate(beats)}
        movable = [i for i, (sl, bt) in enumerate(plan) if bt is not None and i > 0]
        pairs = sorted([plan[i] for i in movable], key=lambda pr: order.get(pr[1]['id'], 99))  # slot and beat travel together: the component stays the one chosen for that beat
        for i, pr in zip(movable, pairs): plan[i] = pr
        for slot, bt in plan:
            comp = slot['comp']; v = slot.get('variant', '')
            if bt is None: continue
            comp = component_for(bt, comp)
            sec = sec_for(comp); html_ = COMP.get(comp, COMP['cards'])(sec, bt, v)
            if html_: out.append(section_extras(html_, bt)); remaining.remove(bt); used_beats.add(bt['id'])
            if slot.get('band') and not bt.get('band'): out[-1] = re.sub(r'(class="sec [^"]*?)band-\w+', lambda m: m.group(1) + f'band-{slot["band"]}', out[-1], count=1) if re.search(r'class="sec [^"]*band-\w+', out[-1]) else out[-1].replace('class="sec ', f'class="sec band-{slot["band"]} ', 1)
        for bt in remaining:  # whatever the recipe had no slot for, in the fallback component for its type — unless the page is already full
            comp = component_for(bt, FALLBACK.get(bt['type'], 'cards')); html_ = COMP.get(comp, COMP['cards'])(sec_for(comp), bt, '')
            if html_: out.append(section_extras(html_, bt)); used_beats.add(bt['id'])
        closing = RECIPE.get('closing', 'cta')
        own = images.get((form_bt or {}).get('image'))
        ps = [img(own['id'])] if closing == 'cta-photo' and own and photo_like(own, 1100) and free_for(own, form_bt) else []
        if ps:
            title = (form_bt or {}).get('h2') or en.get('tag') or h.get('cta') or b['name']; cta_title_used.append(title)
            label = (form_bt or {}).get('cta') or h.get('cta')
            form = f'<div class="ctas">{cta_html(label=label, href=contact_target)}</div>'
            alt = ''.join(f'<span class="lab">{e(a)}</span>' for a in (form_bt or {}).get('alt', []))
            photo_title_style = re.sub(r'max-width:[^;]+;?', '', head_style(take('cta')))
            if len(str(title)) <= 35 and len(str(title).split()) <= 6:
                photo_title_style = re.sub(r'font-size:[^;]+', 'font-size:clamp(42px,6vw,88px)', photo_title_style)
            out.append(f'<section class="sec overlay cta-ov" id="{e((form_bt or {}).get("id") or form_id)}" data-sig="parallax"><figure class="ov-bg"><img src="{ps[0]}" alt=""></figure><div class="wrap ov-in light center">{lab((form_bt or {}).get("label"), True)}<h2 class="h2 light" style="{photo_title_style};text-align:center;margin:0 auto">{e(title)}</h2>{form}<div class="alts">{alt}</div></div></section>')
        else: out.append(cta(take('cta'), form_bt))
        if form_bt: out[-1] = section_extras(out[-1], form_bt)
        out.append(footer(bp['sections'][-1] if bp['sections'][-1]['role'].startswith('footer') else {}))
    def default_move(role, t):
        # the winner's own section vocabulary → our signature component
        if 'sticky' in role and t in ('features', 'steps', 'cells'): return 'sticky-product'
        if role.startswith(('ticker', 'marquee', 'gallery-marquee', 'logo')): return 'marquee'
        if role.startswith('pinned') and t == 'steps': return 'pinned-sequence'
        if role.startswith(('story', 'tabs-media', 'photo-half-text')) and t in ('features', 'steps', 'cells', 'facts'): return 'story'
        return ''
    if not RECIPE:
        renderable_types = ('quote', 'photo', 'ledger', 'features', 'cells', 'steps', 'facts', 'faq', 'form', 'testimonials')
        assign_source_owners([bt for bt in beats if bt.get('type') in renderable_types and (bt.get('type') != 'testimonials' or testimonials({}, bt))])
    for bt in ([] if RECIPE else beats):
        t = bt['type']; mv = (bt.get('ui') or {}).get('move') or ''
        if t == 'testimonials':
            html_ = testimonials(take('list'), bt)
            if html_: out.append(section_extras(html_, bt)); used_beats.add(bt['id'])
            continue
        if mv == 'auto' or not mv:
            fam = 'statement' if t == 'quote' else 'photo' if t == 'photo' else 'cta' if t == 'form' else 'list'
            pool = pools[fam]; peek = pool[taken[fam] % len(pool)] if pool else DEF[fam]
            mv = default_move(peek['role'], t) if not mv else ''
        if mv in SIG and (t != 'quote' or mv in ('type-wall', 'story')) and t not in ('photo', 'form', 'ledger'):
            fam = 'statement' if t == 'quote' else 'list'; sec = take(fam)
            rendered = SIG[mv](sec, bt, flip) if mv == 'story' else SIG[mv](sec, bt)
            out.append(section_extras(rendered, bt)); flip = not flip if mv == 'story' else flip; used_beats.add(bt['id']); continue
        if t == 'quote' and mv == 'type-wall': sec = take('statement'); out.append(section_extras(type_wall(sec, bt), bt)); used_beats.add(bt['id']); continue
        if t == 'quote': sec = take('statement'); out.append(statement(sec, ('quote', bt)))
        elif t == 'photo': sec = take('photo'); out.append(photo_sec(sec, bt))
        elif t == 'ledger': sec = take('list'); out.append(ledger(sec, bt))
        elif t in ('features', 'cells', 'steps', 'facts', 'faq'):
            sec = take('list'); r = sec['role']
            if (r.startswith(('two-audiences', 'double')) and t in ('steps', 'features', 'cells')) or (t == 'steps' and r.startswith('feature')): out.append(two_col(sec, bt))
            else: out.append(cards(sec, bt))
        elif t == 'form': sec = take('cta'); out.append(cta(sec, bt)); cta_done = True
        else: continue
        out[-1] = section_extras(out[-1], bt)
        used_beats.add(bt['id'])
    if not RECIPE:
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
*{{box-sizing:border-box;margin:0;padding:0}}html{{scroll-behavior:auto}}html,body{{overflow-x:clip}}.sec[id],footer[id]{{scroll-margin-top:100px}}
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
.section-extras{{position:relative;z-index:1;margin-top:28px;overflow-wrap:anywhere}}.section-note{{max-width:var(--body-max);line-height:1.5}}.section-actions{{display:flex;flex-wrap:wrap;gap:12px}}.section-note+.section-actions{{margin-top:16px}}.section-actions .btn{{max-width:100%;overflow-wrap:anywhere}}.overlay .section-extras{{color:#fff;padding-bottom:clamp(40px,6vw,80px)}}.overlay .section-actions .btn,.band-accent .section-actions .btn{{background:#fff;color:#111}}
.source-actions{{position:relative;z-index:1;margin-top:28px;overflow-wrap:anywhere}}.overlay .source-actions{{color:#fff;padding-bottom:clamp(40px,6vw,80px)}}.source-actions>div{{padding-top:16px;border-top:1px solid currentColor}}.source-actions>div+div{{margin-top:20px}}.source-actions-label{{font-size:max(12px,var(--lab-px));opacity:.75}}.source-actions ul{{list-style:none;display:flex;flex-wrap:wrap;gap:4px 20px;margin-top:8px}}.source-actions a{{display:inline-flex;align-items:center;min-height:40px;text-decoration:underline;text-underline-offset:.2em;overflow-wrap:anywhere}}
.nav{{position:fixed;inset:0 0 auto 0;z-index:50;padding:18px 0;transition:background var(--slow),color var(--slow)}}.nav .wrap{{display:flex;align-items:center;justify-content:space-between;gap:24px}}.nav .links{{display:flex;gap:28px;font-size:15px}}.nav.solid{{background:color-mix(in srgb,var(--paper) 86%,transparent);color:var(--ink);backdrop-filter:blur(14px)}}.nav.solid .btn{{background:var(--ink);color:var(--paper);border-color:var(--ink)}}.nav.on-photo:not(.solid){{color:var(--on-photo)}}.nav.on-photo:not(.solid) .btn{{background:var(--on-photo);color:#111}}.nav .logo{{height:{min(56, max(28, (bp.get('nav') or {}).get('h', 56) - 20))}px;width:auto}}.nav .wordmark{{font-family:var(--display);font-size:22px}}
.hero{{position:relative;display:grid;align-content:end;overflow:hidden;padding-top:120px}}.hero .media{{position:absolute;inset:0;z-index:0;background:var(--ink)}}.hero .media img,.hero .media video{{width:100%;height:100%;object-fit:cover}}.hero.has-media .media::after{{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(0,0,0,.46),transparent 75%),linear-gradient(180deg,rgba(0,0,0,.42),rgba(0,0,0,.22) 40%,rgba(0,0,0,.58))}}
.hero .hero-in{{position:relative;z-index:1;padding-bottom:clamp(40px,6vw,80px)}}.hero .h1{{font-size:var(--hero-size);overflow-wrap:anywhere}}@media(max-width:600px){{.hero .h1{{font-size:min(var(--hero-size),16vw)}}}}.hero.has-media{{color:var(--on-photo)}}.hero.has-media .cat .lab{{color:var(--on-photo);font-size:max(13px,var(--lab-px))}}.hero.has-media .h1,.hero.has-media .lede,.hero.has-media .cat{{text-shadow:0 1px 8px rgba(0,0,0,.55)}}.hero.has-media .btn.ghost{{color:var(--on-photo);border-color:var(--on-photo)}}.hero .cat{{display:flex;gap:26px;flex-wrap:wrap;margin-bottom:22px}}.hero .al-center{{text-align:center;justify-items:center;display:grid}}.hero .place-start{{align-self:start;padding-top:40px}}.hero .ctas{{display:flex;gap:12px;flex-wrap:wrap;margin-top:30px}}
.hero.shot{{align-content:start;padding-top:104px;min-height:auto!important}}.hero.shot .hero-in{{padding-bottom:0}}.hero.shot .cat{{margin-bottom:14px}}.hero.shot .lede{{margin-top:14px}}.hero.shot .ctas{{margin-top:20px}}.shotwrap{{padding-top:clamp(22px,3vw,36px);padding-bottom:0}}.shotframe{{border-radius:max(12px,var(--radius)) max(12px,var(--radius)) 0 0;overflow:hidden;border:1px solid var(--line);border-bottom:0;box-shadow:0 30px 80px color-mix(in srgb,var(--ink) 14%,transparent)}}.shotframe img{{width:100%;max-height:72vh;object-fit:cover;object-position:top center}}
.sec{{padding:clamp(64px,9vw,140px) 0;display:grid;grid-template-columns:minmax(0,1fr);align-content:center}}.band-dark{{background:var(--band-paper);color:var(--band-ink);--muted:color-mix(in srgb,var(--band-ink) 68%,transparent);--line:color-mix(in srgb,var(--band-ink) 22%,transparent)}}.band-dark .lab{{color:color-mix(in srgb,var(--band-ink) 62%,transparent)}}.band-dark .btn{{background:var(--band-ink);color:var(--band-paper)}}.band-alt{{background:color-mix(in srgb,var(--ink) 6%,var(--paper))}}
.statement .who{{margin-top:22px}}.statement .wrap{{padding-left:max(var(--frame),var(--statement-offset,0px))}}.statement .wrap.center{{text-align:center;display:grid;justify-items:center}}
.photos .pair{{display:flex;gap:var(--gutter);align-items:flex-start}}.photos figure{{overflow:hidden;border-radius:var(--radius)}}.photos figure img,.photo figure img{{width:100%;height:100%;object-fit:cover}}.photo figure{{position:relative;margin:0;max-height:92svh}}.inset-wrap{{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:var(--gutter);align-items:end}}.inset-wrap figure{{overflow:hidden;border-radius:var(--radius)}}.inset-wrap .cap{{font-size:clamp(20px,1.6vw,26px);color:inherit}}@media(max-width:820px){{.inset-wrap{{grid-template-columns:1fr}}}}.photo.bleed{{padding:0}}.photo .over{{position:absolute;inset:auto 0 0 0;padding-bottom:clamp(28px,4vw,56px);color:var(--on-photo)}}.h2.light{{color:var(--on-photo)}}.cap{{margin-top:14px;max-width:var(--body-max);color:var(--muted)}}.caps{{display:flex;gap:24px;align-items:baseline;flex-wrap:wrap;padding-top:14px}}.photo-caption{{padding:clamp(24px,3vw,40px) 0}}.photo-caption .h2{{margin-top:14px;overflow-wrap:anywhere}}.photo-details{{display:flex;flex-wrap:wrap;gap:12px 24px;list-style:none;margin-top:18px}}
.photo.ui-photo .ui-shot{{width:100%;overflow:hidden;border-radius:var(--radius)}}.photo.ui-photo .ui-shot img{{display:block;width:auto;max-width:100%;height:auto;max-height:92svh;object-fit:contain;margin:0 auto}}
.gh{{display:grid;grid-template-columns:1.1fr .9fr;gap:var(--gutter);align-items:end;margin-bottom:clamp(28px,4vw,48px)}}.gh .h2{{text-align:left!important;margin-left:0!important;margin-top:14px;max-width:18ch;text-wrap:balance}}.gh .lede{{margin-top:0}}
.sec.compact{{padding:clamp(40px,5vw,72px) 0;min-height:auto!important}}.gh.one{{display:block;max-width:var(--body-max)}}.gh.one .h2{{max-width:none}}.gh.one.center{{text-align:center;margin-left:auto;margin-right:auto}}.gh.one.center .h2{{text-align:center!important;margin-left:auto!important;margin-right:auto}}.gh.one .lede{{margin-top:16px}}.gh.one.center .lede{{margin-left:auto;margin-right:auto}}
figure.lead{{overflow:hidden;border-radius:var(--radius);margin:0 0 clamp(28px,4vw,48px);border:1px solid var(--line);max-height:78vh}}figure.lead.narrow{{width:min(100%,640px);margin-left:auto;margin-right:auto}}figure.lead.ledger-visual{{margin-top:28px}}figure.lead img{{width:100%;height:100%;object-fit:cover;object-position:top}}figure.lead.lead-shot{{width:fit-content;max-width:100%;margin-left:auto;margin-right:auto;border-radius:0}}figure.lead.lead-shot img{{width:auto;height:auto;max-width:100%;max-height:calc(78vh - 2px);object-fit:contain}}
.faq .two{{display:grid;grid-template-columns:.8fr 1.2fr;gap:var(--gutter)}}.qa details{{border-top:1px solid var(--line);padding:16px 0}}.qa details:last-child{{border-bottom:1px solid var(--line)}}.qa summary{{cursor:pointer;list-style:none;font-family:var(--display);font-weight:var(--h3-w);font-size:min(var(--h3),24px);display:flex;justify-content:space-between;gap:16px}}.qa summary::after{{content:"+";font-weight:300}}.qa details[open] summary::after{{content:"–"}}.qa details p{{margin-top:10px;color:var(--muted);max-width:60ch}}
.grid{{display:grid;grid-template-columns:repeat(var(--n),1fr);gap:var(--gutter)}}.card figure{{overflow:hidden;border-radius:var(--radius);margin-bottom:16px}}.card figure img{{width:100%;height:100%;object-fit:cover}}.card .h3{{margin-top:8px;font-size:min(var(--h3),28px)}}.card p{{margin-top:10px;color:var(--muted);max-width:34ch}}.card .num{{display:block;font-family:var(--display);font-weight:var(--h2-w);font-size:var(--h2);line-height:1;letter-spacing:-.02em}}
.review-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr));gap:var(--gutter)}}.review-card{{min-width:0;margin:0;padding:24px;border:1px solid var(--line);border-radius:var(--radius);display:flex;flex-direction:column;gap:20px;overflow-wrap:anywhere}}.review-card blockquote{{flex:1;font-size:var(--body-px);line-height:1.5}}.review-card figcaption{{display:flex;flex-wrap:wrap;gap:6px 12px;color:var(--muted);font-size:.9em}}.review-card a{{color:inherit;text-decoration:underline;text-underline-offset:3px}}
.ledger .two{{display:grid;grid-template-columns:.9fr 1.1fr;gap:var(--gutter)}}.ledger .two.no-visual{{grid-template-columns:minmax(0,1fr);max-width:min(var(--container),1000px)}}.ledger .two>*{{min-width:0}}.rows{{list-style:none}}.rows li{{display:flex;align-items:baseline;gap:12px;padding:14px 0;border-top:1px solid var(--line);font-size:calc(var(--body-px) + 2px)}}.rows li span{{min-width:0;overflow-wrap:anywhere}}.rows li i{{flex:1;border-bottom:1px dotted var(--line)}}.rows li b{{flex-shrink:0;font-weight:500;font-variant-numeric:tabular-nums}}.rows li.big{{padding:22px 0}}.rows li.big b{{font-family:var(--display);font-weight:var(--h2-w);font-size:clamp(32px,5vw,72px);line-height:1;letter-spacing:-.02em}}.ledger .ctas{{margin-top:26px}}@media(max-width:600px){{.rows li.big{{display:grid;grid-template-columns:minmax(0,1fr);gap:8px}}.rows li.big i{{display:none}}.rows li.big b{{font-size:clamp(40px,15vw,72px)}}}}
.ledger .rows li b{{min-width:0;flex-shrink:1;overflow-wrap:anywhere}}
.ledger .rows li b.price-short{{white-space:nowrap;overflow-wrap:normal;flex-shrink:0}}
.ledger .rows li.price-long{{flex-wrap:wrap}}
.ledger .rows li.price-long b{{max-width:100%;white-space:normal;overflow-wrap:anywhere;flex-shrink:0;margin-left:auto}}
@media(max-width:320px){{.ledger .rows li{{flex-wrap:wrap}}.ledger .rows li b.price-short{{max-width:100%;white-space:normal;overflow-wrap:anywhere;margin-left:auto}}}}
.ledger .ctas{{display:flex;gap:12px;flex-wrap:wrap}}
.ledger .ctas .btn{{min-height:max(var(--btn-h),44px);max-width:100%;overflow-wrap:anywhere}}
.ledger .ctas .btn.ghost{{background:transparent;color:inherit;border-color:currentColor}}
.ledger .h2{{overflow-wrap:anywhere;text-wrap:balance}}
.ledger-story .ledger-story-content .rows{{margin-top:clamp(32px,4vw,56px)}}
.ledger-story .ledger-story-media{{align-self:start}}
.ledger-story .ledger-story-media .ledger-visual{{margin:0;max-height:none}}
@media(max-width:820px){{.ledger-story .ledger-story-media .ledger-visual{{margin-top:28px}}}}
.ledger-sticky .two{{grid-template-columns:minmax(0,.94fr) minmax(0,1.06fr);align-items:start}}
.ledger-sticky .ledger-sticky-content .rows{{margin-top:36px}}
.ledger-sticky .rows li{{padding:25px 0}}
.ledger-sticky figure.ledger-visual{{position:sticky;top:110px;align-self:start;justify-self:center;margin:0;width:100%;max-width:calc(var(--ledger-image-max) / var(--ledger-density,1));height:min(62vh,600px,calc(var(--ledger-image-height-max) / var(--ledger-density,1)));max-height:none;aspect-ratio:auto!important}}
@media(min-resolution:1.01dppx){{.ledger-sticky .ledger-visual{{--ledger-density:2}}}}
@media(min-resolution:2.01dppx){{.ledger-sticky .ledger-visual{{--ledger-density:3}}}}
@media(min-resolution:3.01dppx){{.ledger-sticky .ledger-visual{{--ledger-density:4}}}}
.no-motion .ledger-sticky .ledger-visual{{position:static}}
@media(prefers-reduced-motion:reduce){{.ledger-sticky .ledger-visual{{position:static}}}}
.ledger-cards-intro{{max-width:760px}}
.ledger-cards>.wrap{{container-type:inline-size}}
.ledger-card-list{{--ledger-card-gap:clamp(12px,2vw,24px);display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,max(250px,calc((100% + var(--ledger-card-gap)) / var(--ledger-cols) - var(--ledger-card-gap)))),1fr));gap:var(--ledger-card-gap);list-style:none;margin-top:clamp(32px,5vw,72px)}}
.ledger-card-list li{{min-width:0;display:flex;flex-direction:column;justify-content:space-between;gap:24px;padding:clamp(20px,2.2vw,28px);border:1px solid var(--line);border-radius:var(--radius);overflow-wrap:anywhere}}
.ledger-card-list li span{{font-size:calc(var(--body-px) + 2px)}}
.ledger-card-list li b{{font-family:var(--display);font-size:clamp(24px,2.1vw,30px);font-weight:var(--h2-w);font-variant-numeric:tabular-nums}}
.ledger-card-list .ledger-price{{display:flex;flex-direction:column;gap:4px;min-width:0}}
.ledger-card-list .ledger-price b{{font-size:clamp(30px,3vw,42px)}}
.ledger-card-list .ledger-price small{{font-size:clamp(15px,var(--body-px),22px);line-height:1.4;overflow-wrap:anywhere}}
@media(min-width:601px){{@container (min-width:550px) and (max-width:1071px){{.ledger-card-list[data-cols="4"]:has(>li:nth-child(4):last-child){{grid-template-columns:repeat(2,minmax(0,1fr))}}}}}}
.ledger-ticker{{margin-bottom:clamp(32px,5vw,64px)}}
@media(max-width:900px){{.ledger-sticky .two{{display:grid;grid-template-columns:minmax(0,1fr);gap:0}}.ledger-sticky .ledger-sticky-content{{display:contents}}.ledger-sticky .ledger-sticky-content .lab{{order:1}}.ledger-sticky .ledger-sticky-content h2{{order:2}}.ledger-sticky .ledger-sticky-content .lede{{order:3}}.ledger-sticky figure.ledger-visual{{order:4;position:static;margin:24px 0;height:min(180px,calc(var(--ledger-image-height-max) / var(--ledger-density,1)))}}.ledger-sticky .ledger-sticky-content .rows{{order:5;margin-top:0}}.ledger-sticky .ledger-sticky-content .ctas{{order:6}}.ledger-sticky .rows li{{padding:12px 0}}}}
@media(max-width:600px){{.ledger-card-list{{grid-template-columns:minmax(0,1fr)}}}}
.twocol .cols{{display:grid;grid-template-columns:repeat(var(--n),1fr);gap:var(--gutter);margin-top:30px}}.twocol .cols .h2{{font-size:var(--h3)}}
.cta .center{{text-align:center;display:grid;justify-items:center;gap:clamp(22px,2vw,30px)}}.cta .h2{{max-width:16ch;text-wrap:balance;overflow-wrap:anywhere}}.cta .btn{{font-size:max(var(--btn-px),16px);min-height:max(var(--btn-h),48px)}}.cta .alts .lab{{font-size:clamp(13px,1vw,16px);line-height:1.5;color:color-mix(in srgb,var(--band-ink) 82%,transparent);overflow-wrap:anywhere}}.form{{display:grid;grid-template-columns:1fr 1fr;gap:12px;width:min(640px,100%);text-align:left}}.form label{{display:grid;gap:6px}}.form label span{{font-family:var(--label);font-size:var(--lab-px);letter-spacing:var(--lab-ls);text-transform:uppercase;opacity:.7}}.form input{{min-height:46px;border:1px solid color-mix(in srgb,currentColor 30%,transparent);background:transparent;color:inherit;padding:0 12px;border-radius:max(4px,min(12px,var(--btn-r)));font:inherit}}.form .btn{{grid-column:1/-1;justify-content:center}}.alts{{display:flex;gap:18px;flex-wrap:wrap;justify-content:center}}
.giant{{padding:40px 0 0;overflow:hidden}}.gw{{font-family:var(--display);font-weight:var(--h1-w);font-size:min(22vw,{round(165 / max(4, len(b['name'])), 1)}vw);line-height:.85;letter-spacing:-.03em;white-space:nowrap;text-transform:var(--h1-tt)}}
.end{{padding-top:clamp(48px,6vw,80px);padding-bottom:28px}}.end .fcols{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:var(--gutter);margin-top:48px;padding-top:40px;border-top:1px solid var(--line)}}.end .fcols>*{{min-width:0}}.end li{{overflow-wrap:anywhere}}.end ul{{list-style:none;margin-top:10px;display:grid;gap:6px}}.end ul.footer-nav{{display:flex;flex-wrap:wrap;gap:12px 24px;margin-top:24px}}.end .legal{{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-top:40px;font-family:var(--label);font-size:var(--lab-px);color:var(--muted)}}
/* template components */
.hero.centre{{min-height:auto;padding-top:120px}}.hero.centre .hero-in{{text-align:center;display:grid;justify-items:center}}
.hero.has-media{{background:#111}}.hero.poster .lede,.hero.photo .lede{{max-width:44ch;width:auto}}.hero.poster .hero-in{{display:grid;justify-items:center;text-align:center}}.hero.photo .hero-in,.hero.poster .hero-in{{position:relative;z-index:1}}.hero-in.light .lede{{color:rgba(255,255,255,.86)}}.hero-in.light .btn.ghost{{color:#fff;border-color:rgba(255,255,255,.5)}}.hero.poster .h1{{letter-spacing:-.035em}}
.hero.inset{{min-height:auto;padding-bottom:0}}.inset-v{{margin:clamp(28px,4vw,56px) 0 0;border-radius:var(--radius);overflow:hidden;aspect-ratio:1.8}}.inset-v img{{width:100%;height:100%;object-fit:cover}}
.collage .cl{{display:grid;grid-template-columns:1.2fr .8fr;grid-template-rows:auto auto;gap:var(--gutter)}}.collage figure{{margin:0;overflow:hidden;border-radius:var(--radius)}}.collage figure img{{width:100%;height:100%;object-fit:cover}}.collage .c1{{grid-row:1/3;aspect-ratio:.9}}.collage .c2{{aspect-ratio:1.3}}.collage .c3{{aspect-ratio:1.3}}
.overlay{{position:relative;padding:0;min-height:88svh;background:#121212;color:#fff;display:grid;align-content:end;overflow:hidden}}.overlay.chapter{{min-height:72svh;align-content:center}}.ov-bg{{position:absolute;inset:0;margin:0}}.ov-bg::after{{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.05),rgba(0,0,0,.55))}}.ov-bg img{{width:100%;height:100%;object-fit:cover}}.ov-in{{position:relative;z-index:1;padding:clamp(48px,7vw,110px) var(--frame) clamp(40px,6vw,80px);color:#fff}}.ov-in .lede{{color:rgba(255,255,255,.82)}}.ov-in .h2{{color:#fff}}.ov-in.center{{text-align:center;display:grid;justify-items:center}}.rows.light li{{border-color:rgba(255,255,255,.25);color:#fff}}.rows.light li i{{border-color:rgba(255,255,255,.25)}}.cta-ov .ov-in{{padding-block:clamp(48px,7vw,90px);gap:18px}}.cta-ov .alts{{gap:8px 18px}}.cta-ov .alts .lab{{color:rgba(255,255,255,.9);font-size:max(12px,var(--lab-px));line-height:1.4;overflow-wrap:anywhere}}.cta-ov .form{{margin:28px auto 0}}.cta-ov .ov-bg::after{{background:linear-gradient(180deg,rgba(0,0,0,.45),rgba(0,0,0,.78))}}.cta-ov .form input,.cta-ov .form textarea,.cta-ov .form select{{background:rgba(0,0,0,.35);color:#fff;border-color:rgba(255,255,255,.35)}}.cta-ov .form ::placeholder{{color:rgba(255,255,255,.6)}}.overlay.bare::after{{display:none}}
.qband{{padding:clamp(72px,10vw,150px) 0}}.qband .qb{{font-family:var(--display);font-weight:var(--h2-w);font-size:clamp(28px,4.2vw,64px);line-height:1.12;letter-spacing:-.02em;max-width:24ch}}.qband.center .qb{{margin:0 auto;text-align:center}}.qband.center .who{{text-align:center}}.band-accent{{background:var(--accent);color:#fff}}.band-accent .lab{{color:rgba(255,255,255,.7)}}
.railsec{{overflow:hidden}}.rail{{overflow-x:auto;scrollbar-width:thin;padding:0 var(--frame)}}.rail-in{{display:flex;gap:var(--gutter);width:max-content}}.rc{{width:min(360px,78vw);display:grid;gap:10px;align-content:start}}.rc figure{{margin:0 0 6px;aspect-ratio:.82;border-radius:var(--radius);overflow:hidden}}.rc figure img{{width:100%;height:100%;object-fit:cover}}.rc p{{color:var(--muted)}}
.no-motion .rail-in{{width:auto;display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr))}}.no-motion .rc{{width:auto}}
@media(max-width:900px),(prefers-reduced-motion:reduce){{.rail-in{{width:auto;display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr))}}.rc{{width:auto}}}}
.facts-cards .card{{border-top:1px solid var(--line);padding-top:clamp(16px,2vw,28px)}}.facts-cards .card .h3{{font-family:var(--display);font-weight:var(--h1-w);font-size:clamp(40px,5.2vw,84px);line-height:1;letter-spacing:-.03em;overflow-wrap:anywhere}}.facts-cards .card p{{margin-top:12px}}
.nums{{display:grid;grid-template-columns:repeat(var(--n),minmax(0,1fr));gap:var(--gutter);border-top:1px solid var(--line);padding-top:28px}}.nums .num{{display:block;font-family:var(--display);font-weight:var(--h1-w);font-size:clamp(48px,7vw,120px);line-height:.95;letter-spacing:-.03em;overflow-wrap:anywhere}}.nums p{{margin-top:12px;color:var(--muted)}}@media(max-width:600px){{.numbers .nums{{grid-template-columns:1fr}}}}
.stickers{{padding:clamp(72px,10vw,140px) 0}}.stks{{display:flex;flex-wrap:wrap;gap:12px;justify-content:center;margin-top:30px;max-width:900px;margin-left:auto;margin-right:auto}}.stk{{display:inline-block;padding:14px 22px;border-radius:999px;background:#fff;color:#111;font-family:var(--display);font-weight:var(--h3-w);font-size:clamp(16px,1.6vw,24px);transform:rotate(var(--r));box-shadow:0 10px 30px rgba(0,0,0,.18)}}.stickers .h2{{text-align:center;margin:0 auto}}.stickers .lede{{color:rgba(255,255,255,.85);text-align:center}}
.prs{{display:grid;grid-template-columns:repeat(var(--n),minmax(0,1fr));gap:var(--gutter)}}.prs>*,.nums>*,.cl>*,.grid>*,.cols>*,.rc{{min-width:0}}.sec img{{max-width:100%}}.pr figure{{margin:0;aspect-ratio:.8;border-radius:var(--radius);overflow:hidden;background:color-mix(in srgb,var(--ink) 6%,var(--paper))}}.pr figure img{{width:100%;height:100%;object-fit:cover}}.pr-t{{display:flex;justify-content:space-between;gap:12px;margin-top:12px;align-items:baseline}}.pr-t b{{font-weight:500;white-space:nowrap}}
@media(max-width:900px){{.collage .cl,.nums,.prs{{grid-template-columns:1fr 1fr}}.collage .c1{{grid-row:auto}}.overlay{{min-height:70svh}}}}
/* signature components */
.cta-ov{{align-content:center}}.cta-ov .ov-in{{gap:clamp(20px,2.2vw,32px)}}.cta-ov .h2{{max-width:16ch;text-wrap:balance;overflow-wrap:anywhere}}.cta-ov .btn{{font-size:max(var(--btn-px),16px);min-height:max(var(--btn-h),48px)}}.cta-ov .alts{{max-width:70ch}}
.hero.split{{padding-top:96px;min-height:100svh;align-content:center}}.split-wrap{{display:grid;grid-template-columns:1fr 1.1fr;gap:var(--gutter);align-items:center}}.split-l .lede{{margin-top:18px}}.split-l .ctas{{margin-top:26px}}.shotframe.tall{{border-radius:max(12px,var(--radius));border:1px solid var(--line);box-shadow:0 40px 100px color-mix(in srgb,var(--ink) 16%,transparent);overflow:hidden}}.shotframe.tall img{{width:100%;height:min(82vh,900px);object-fit:cover;object-position:left top}}.shotframe.tall.product-shot img{{display:block;width:100%;height:auto;max-height:min(82vh,900px);object-fit:contain}}
.sp{{display:grid;grid-template-columns:1fr 1.15fr;gap:calc(var(--gutter) * 1.5);align-items:stretch}}.sp-row{{min-height:46vh;display:grid;align-content:center;gap:12px;max-width:40ch;opacity:.28;transition:opacity .5s var(--ease)}}.sp-row.on{{opacity:1}}.sp-row .h3{{font-size:min(var(--h2),44px)}}.sp-row p{{color:var(--muted);font-size:calc(var(--body-px) + 1px)}}.sp-pin{{position:relative}}.sp-stage{{position:sticky;top:12vh;height:76vh;border-radius:max(12px,var(--radius));overflow:hidden;border:1px solid var(--line);background:color-mix(in srgb,var(--ink) 6%,var(--paper))}}.sp-f{{position:absolute;inset:0;margin:0;opacity:0;transform:scale(1.03);transition:opacity .6s var(--ease),transform .9s var(--ease)}}.sp-f.on{{opacity:1;transform:none}}.sp-f img{{width:100%;height:100%;object-fit:cover;object-position:top;transition:transform 1.2s var(--ease)}}.sp-stage.product-shot .sp-f img{{object-fit:contain}}
.marquee{{padding:clamp(28px,4vw,56px) 0;overflow:hidden}}.marquee .gh{{margin-bottom:24px}}.mq{{overflow:hidden;border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:18px 0}}.mq-track{{display:flex;gap:0;width:max-content;animation:mq 46s linear infinite}}.mq-i{{display:inline-flex;align-items:center;gap:28px;padding:0 14px 0 28px;font-family:var(--display);font-weight:var(--h2-w);font-size:min(var(--h2),56px);letter-spacing:-.02em;white-space:nowrap}}.mq-i i{{font-style:normal;font-size:.45em;color:var(--accent)}}@keyframes mq{{to{{transform:translateX(-50%)}}}}.marquee:hover .mq-track{{animation-play-state:paused}}
.marquee-static{{position:absolute;width:1px;height:1px;padding:0;overflow:hidden;clip-path:inset(50%);white-space:nowrap}}
.marquee-static ul{{list-style:none}}
.no-motion .marquee .mq{{display:none}}.no-motion .marquee-static{{position:static;width:auto;height:auto;padding:0;overflow:visible;clip-path:none;white-space:normal}}.no-motion .marquee-static li{{display:flex;flex-wrap:wrap;gap:.4em 1em;padding:14px 0;border-top:1px solid var(--line);overflow-wrap:anywhere}}
@media(prefers-reduced-motion:reduce){{.marquee .mq{{display:none}}.marquee-static{{position:static;width:auto;height:auto;padding:0;overflow:visible;clip-path:none;white-space:normal}}.marquee-static li{{display:flex;flex-wrap:wrap;gap:.4em 1em;padding:14px 0;border-top:1px solid var(--line);overflow-wrap:anywhere}}}}
.pinned,.typewall,.sticky,.railsec{{display:block;align-content:start}}.pinned{{padding:0}}.ps-sticky{{position:sticky;top:0;height:100svh;display:grid;align-content:center;overflow:hidden}}.ps-stage{{position:relative;min-height:52vh}}.ps-s{{position:absolute;inset:0;display:grid;grid-template-columns:1fr 1fr;gap:var(--gutter);align-items:center;opacity:0;transform:translateY(24px);transition:opacity .5s var(--ease),transform .7s var(--ease);pointer-events:none}}.ps-s.on{{opacity:1;transform:none}}.ps-t .num{{display:block;font-family:var(--display);font-weight:var(--h1-w);font-size:clamp(64px,10vw,160px);line-height:.9;letter-spacing:-.03em;color:inherit}}.ps-t .h2{{margin-top:18px}}.ps-v{{margin:0;border-radius:max(12px,var(--radius));overflow:hidden;border:1px solid var(--line);aspect-ratio:1.3}}.ps-v img{{width:100%;height:100%;object-fit:cover}}.ps-dots{{display:flex;gap:8px;margin-top:28px}}.ps-dots i{{width:28px;height:2px;background:var(--line)}}.ps-dots i.on{{background:var(--ink)}}.band-dark .ps-dots i.on{{background:var(--band-ink)}}
.typewall{{padding:0}}.tw-sticky{{position:sticky;top:0;min-height:100svh;display:grid;align-content:center}}.tw{{font-family:var(--display);font-weight:var(--h2-w);font-size:clamp(28px,4.6vw,72px);line-height:1.08;letter-spacing:-.02em;max-width:min(92%,30ch);margin-top:22px;text-wrap:balance;overflow-wrap:anywhere}}.tw-title{{font-size:clamp(40px,8vw,120px)}}.tw-caption{{max-width:60ch;margin-top:24px}}.tw-prominent{{text-align:center}}.tw-prominent .tw-title{{font-size:clamp(40px,11.1vw,160px);max-width:100%;margin-left:auto;margin-right:auto}}.tw-prominent .tw-caption{{margin-left:auto;margin-right:auto}}.tw-w{{opacity:1;transition:opacity .25s}}.tw-animated .tw-w{{opacity:.35}}.tw-animated .tw-w.on{{opacity:1}}.typewall .who{{margin-top:28px}}
.ps-t .h2,.ps-t .num{{overflow-wrap:anywhere}}.ps-s.no-visual{{grid-template-columns:minmax(0,1fr)}}.ps-s.no-visual .ps-t{{text-align:center}}.ps-v.item-visual{{width:100%;max-width:var(--ps-image-max);justify-self:center}}@media(min-resolution:1.1dppx){{.ps-v.item-visual{{max-width:calc(var(--ps-image-max) / 2)}}}}@media(min-resolution:2.1dppx){{.ps-v.item-visual{{max-width:calc(var(--ps-image-max) / 3)}}}}@media(min-resolution:3.1dppx){{.ps-v.item-visual{{max-width:calc(var(--ps-image-max) / 4)}}}}
.cta2{{display:grid;grid-template-columns:1fr 1fr;gap:calc(var(--gutter) * 1.5);align-items:center}}.cta-v{{margin:0;border-radius:max(12px,var(--radius));overflow:hidden;aspect-ratio:1.05}}.cta-v img{{width:100%;height:100%;object-fit:cover}}.cta-t{{display:grid;gap:22px}}.cta-t .form{{text-align:left}}.cta-t .alts{{justify-content:flex-start}}
.st{{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:calc(var(--gutter) * 1.5);align-items:center}}.story.flip .st-t{{order:2}}.st-l{{list-style:none;margin-top:28px;display:grid;gap:14px}}.st-l li{{display:grid;grid-template-columns:minmax(120px,.35fr) 1fr;gap:16px;padding-top:12px;border-top:1px solid var(--line)}}.st-l b{{font-weight:500}}.st-l span{{color:var(--muted)}}.st-v{{margin:0;border-radius:max(12px,var(--radius));overflow:hidden;border:1px solid var(--line);aspect-ratio:1.15}}.st-v img{{width:100%;height:100%;object-fit:cover;object-position:top}}.story-photo .st-t{{min-width:0;overflow-wrap:anywhere}}.story-photo .st-v{{width:100%;max-width:min(var(--story-image-max),calc(78svh * var(--story-ratio)));justify-self:center}}@media(min-resolution:1.1dppx){{.story-photo .st-v{{max-width:min(calc(var(--story-image-max) / 2),calc(78svh * var(--story-ratio)))}}}}@media(min-resolution:2.1dppx){{.story-photo .st-v{{max-width:min(calc(var(--story-image-max) / 3),calc(78svh * var(--story-ratio)))}}}}@media(min-resolution:3.1dppx){{.story-photo .st-v{{max-width:min(calc(var(--story-image-max) / 4),calc(78svh * var(--story-ratio)))}}}}
.story-photo .h2{{font-size:min(var(--story-heading-size),clamp(28px,4vw,72px))}}
@media(max-width:900px){{.story-photo .h2{{font-size:min(var(--story-heading-size),clamp(28px,8.2vw,72px))}}}}
/* Wide place photographs can carry an editorial chapter with readable text. */
@media(min-width:901px) and (min-height:701px){{
.story-editorial{{padding:20px 0}}
.story-editorial .st{{display:grid;grid-template-columns:minmax(0,1fr);gap:0;width:calc(100% - 2 * clamp(16px,5vw,72px));max-width:min(var(--editorial-image-max),calc(78svh * 1.6));padding:0;margin:0 auto;container-type:inline-size}}
.story-editorial .st-v{{grid-area:1/1;position:relative;width:100%;max-width:none;aspect-ratio:1.6!important;border:0;border-radius:0}}
.story-editorial .st-v img{{object-position:center}}
.story-editorial .st-t{{grid-area:1/1;z-index:1;align-self:end;width:min(760px,75%);padding:clamp(28px,4vw,56px);background:linear-gradient(90deg,rgba(0,0,0,.82) calc(100% - 28px),transparent);color:#fff}}
.story-editorial .st-t .h2{{color:#fff;text-align:left!important}}
.story-editorial .st-t .lab,.story-editorial .st-t .lede{{color:#fff}}
}}
@media(min-width:901px) and (min-height:701px){{
@container(min-width:701px){{
@supports ((mask-image:linear-gradient(black,transparent)) or (-webkit-mask-image:linear-gradient(black,transparent))){{
.story-editorial .st-t{{position:relative;isolation:isolate;background:none;--scrim-fade:clamp(28px,4vw,56px)}}
.story-editorial .st-t::before{{content:"";position:absolute;inset:0;z-index:-1;pointer-events:none;background:linear-gradient(90deg,rgba(0,0,0,.82) calc(100% - var(--scrim-fade)),transparent);-webkit-mask-image:linear-gradient(to bottom,transparent,#000 var(--scrim-fade));mask-image:linear-gradient(to bottom,transparent,#000 var(--scrim-fade))}}
}}
}}
}}
@media(min-width:901px) and (min-height:701px) and (min-resolution:1.1dppx){{.story-editorial .st{{max-width:min(calc(var(--editorial-image-max) / 2),calc(78svh * 1.6))}}}}
@media(min-width:901px) and (min-height:701px) and (min-resolution:2.1dppx){{.story-editorial .st{{max-width:min(calc(var(--editorial-image-max) / 3),calc(78svh * 1.6))}}}}
@media(min-width:901px) and (min-height:701px) and (min-resolution:3.1dppx){{.story-editorial .st{{max-width:min(calc(var(--editorial-image-max) / 4),calc(78svh * 1.6))}}}}
@container(max-width:700px){{.story-editorial .st-v{{aspect-ratio:var(--story-ratio)!important}}.story-editorial .st-t{{grid-area:2/1;align-self:start;width:100%;padding:28px 0 0;background:none;color:inherit}}.story-editorial .st-t .h2{{color:inherit}}.story-editorial .st-t .lab,.story-editorial .st-t .lede{{color:inherit}}}}
@media(max-width:900px),(max-height:700px){{.story-editorial{{padding:32px 0}}.story-editorial .st{{display:flex;flex-direction:column;gap:0}}.story-editorial .st-v{{order:0}}.story-editorial .st-t{{order:1;width:100%;padding-top:28px}}}}
@media(max-width:900px){{.statement .wrap{{padding-left:max(16px,calc(var(--frame) * .5))}}.split-wrap,.sp,.ps-s,.st,.cta2{{grid-template-columns:1fr}}.story.flip .st-t{{order:0}}.sp-pin{{order:-1}}.sp-stage{{position:relative;top:auto;height:52vh}}.sp-row{{min-height:auto;padding:22px 0;opacity:1}}.ps-s{{align-content:start}}.ps-v{{aspect-ratio:1.6}}.shotframe.tall img{{height:52vh}}.mq-i{{font-size:28px}}.nav .links{{display:none}}.nav .wrap{{gap:12px}}.nav .wrap>a:first-child{{min-width:0;max-width:28vw;flex:0 0 auto}}.nav .logo{{height:auto;max-height:56px;max-width:min(115px,28vw)}}.nav .wordmark{{font-size:clamp(16px,5vw,22px);overflow-wrap:anywhere}}.nav .btn{{min-width:0;padding-inline:8px;overflow-wrap:anywhere;justify-content:center}}.nav .btn .ar{{flex-shrink:0}}.gh,.ledger .two,.faq .two,.photos .pair{{grid-template-columns:1fr;display:grid}}.photos figure{{width:100%!important}}.grid{{grid-template-columns:1fr}}.twocol .cols{{grid-template-columns:1fr}}.end .fcols{{grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr))}}.form{{grid-template-columns:1fr}}.hero{{padding-top:100px}}.wrap{{padding:0 max(16px,calc(var(--frame) * .5))}}}}
@media(max-width:900px){{.shotframe.tall.product-shot img{{height:auto;max-height:52vh}}}}
.no-motion .ps-sticky{{position:static;height:auto;display:block;overflow:visible}}.no-motion .ps-stage{{min-height:0;display:grid;gap:clamp(40px,6vw,80px)}}.no-motion .ps-s{{position:static;inset:auto;opacity:1;transform:none;pointer-events:auto}}.no-motion .ps-dots{{display:none}}.no-motion *,.no-motion *::before,.no-motion *::after{{transition:none!important;animation:none!important}}@media(prefers-reduced-motion:reduce){{*{{transition:none!important;animation:none!important}}}}
'''
    moves_attr = lambda n: f' data-move="{n}"'
    def meta_text(value):
        if not isinstance(value, str): return ''
        return ' '.join(re.sub(r'<[^>]*>', '', value).split())
    source_seo = inventory.get('seo') if isinstance(inventory.get('seo'), dict) else {}
    page_title = meta_text(inventory.get('title')) or meta_text(b.get('name'))
    # If the source has no description, use the page's own visible lede.
    # Never copy the source canonical or robots onto a temporary preview.
    page_description = meta_text(source_seo.get('description')) or meta_text(h.get('lede'))
    description_tag = f'<meta name="description" content="{e(page_description)}">' if page_description else ''
    language = next((value.strip() for value in (d.get('lang'), inventory.get('lang')) if isinstance(value, str) and re.fullmatch(r'[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*', value.strip())), '')
    lang_attr = f' lang="{e(language)}"' if language else ''
    html = f'''<!DOCTYPE html><html{lang_attr}><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{e(page_title)}</title>{description_tag}{fonts_link}<style>{css}</style></head>
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
  document.querySelectorAll('[data-sig="typewall"]').forEach(sec=>{{ const ws=[...sec.querySelectorAll('.tw-w')]; sec.classList.add('tw-animated'); sec.style.height='150vh'; ScrollTrigger.create({{trigger:sec,start:'top top',end:'bottom bottom',onUpdate:st=>{{ const k=Math.round(st.progress*ws.length); ws.forEach((w,i)=>w.classList.toggle('on',i<k)); }}}}); }});
  document.querySelectorAll('[data-sig="parallax"]').forEach(el=>gsap.fromTo(el,{{y:40}},{{y:-40,ease:'none',scrollTrigger:{{trigger:el,start:'top bottom',end:'bottom top',scrub:true}}}}));
  ScrollTrigger.refresh(); }}
const NOMOTION=/[?&]nomotion/.test(location.search)||matchMedia('(prefers-reduced-motion:reduce)').matches; const PREVIEW=!NOMOTION&&(self!==top||/[?&]swarm/.test(location.search));
if(NOMOTION){{ document.documentElement.classList.add('no-motion'); document.querySelectorAll('[data-move]').forEach(el=>el.removeAttribute('data-move')); document.querySelectorAll('.tw-w,.sp-row').forEach(el=>el.classList.add('on')); document.querySelectorAll('.ps-s,.sp-f').forEach((el,i)=>el.classList.toggle('on',el.dataset.i==='0')); }}
addEventListener('load',()=>{{ const nav=document.getElementById('nav'); const solidFrom=document.querySelector('.hero.has-media')?innerHeight*.7:0; if(solidFrom) nav.classList.add('on-photo'); const onS=()=>nav.classList.toggle('solid',scrollY>solidFrom); onS(); addEventListener('scroll',onS,{{passive:true}});
  if(NOMOTION) return;
  try{{ if(PREVIEW) new Swarm({{agents:innerWidth<900?8:18,speed:1,hud:true,sectionSelector:'section,footer',boxSel:'.btn,.card,figure,.rows li,.form input',onDone:()=>{{ try{{ scrollTo(0,0); Moves.init(); Sig(); }}catch(e){{}} }}}}).run(); else {{ Moves.init(); Sig(); }} }}catch(e){{ try{{Moves.init(); Sig();}}catch(_){{}} }} }});
</script></body></html>'''
    out_path = out_path or os.path.join(slug_dir, f'index.{bp_id}.html'); open(out_path, 'w').write(html); return out_path

if __name__ == '__main__':
    print(build(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None))
