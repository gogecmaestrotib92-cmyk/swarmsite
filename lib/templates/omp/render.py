"""omp — rebuilt from https://omp.dentist (a neighbourhood dental practice; type-led).
render(d) -> one self-contained page. Pure: no file reads, no model, nothing computed but the placing of the data.
The reference's build: page in two halves of 50 %, 16px gutters, a light serif at 56/30px with a 15.33px mono for
everything said in sentences, pill buttons, ruled accordion rows, colour fields with one centred sentence, a foot in
the ink colour that ends in the name set as wide as the page. See NOTES.md for what was measured and what was changed."""
import html, re

PRE = '../../'
# A photograph may fill an upright half of the page (the reference's 720×900 beside type) when it is not enlarged at
# 1440×900 and the half (4:5) still shows 60 % or more of its width, i.e. it is no wider than 4:3. A 3:2 picture would
# lose half of itself and a 2.9:1 banner three quarters: those run across the page as bands instead.
HALF_MAX_RATIO = 1.34
HALF_MIN_W, HALF_MIN_H = 720, 900
UI = {  # the only words that are not the client's: the reference's own two control labels, by page language
    'en': ('MORE', 'LESS', 'Menu', 'Close'), 'de': ('MEHR', 'WENIGER', 'Menü', 'Schließen'),
    'fr': ('PLUS', 'MOINS', 'Menu', 'Fermer'), 'es': ('MÁS', 'MENOS', 'Menú', 'Cerrar'),
    'it': ('PIÙ', 'MENO', 'Menu', 'Chiudi'), 'nl': ('MEER', 'MINDER', 'Menu', 'Sluiten'),
    'pt': ('MAIS', 'MENOS', 'Menu', 'Fechar'), 'sr': ('VIŠE', 'MANJE', 'Meni', 'Zatvori'),
}


def e(s):
    return html.escape(str(s if s is not None else ''), quote=True)


def _rgb(h):
    h = (h or '#000').lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    try:
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return (0, 0, 0)


def _hex(c):
    return '#%02x%02x%02x' % tuple(max(0, min(255, round(v))) for v in c)


def _mix(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def _lum(c):
    def f(v):
        v /= 255
        return v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4
    return .2126 * f(c[0]) + .7152 * f(c[1]) + .0722 * f(c[2])


def _cr(a, b):
    la, lb = _lum(a), _lum(b)
    return (max(la, lb) + .05) / (min(la, lb) + .05)


def _units(s):
    """rough advance width of a string in em for a light text serif — only the no-script fallback size depends on it"""
    u = 0.0
    for ch in s:
        if ch in ' .,:;\'’!|ijlt·-–':
            u += .3
        elif ch in 'mwMW':
            u += .86
        elif ch in 'frI1':
            u += .38
        elif ch.isupper() or ch.isdigit() or ch in '&@':
            u += .68
        else:
            u += .53
    return max(u, .5)


def _wordmark_lines(name):
    """The reference sets its three-word name in two lines, 720 wide and 240 high (1:3). The client's name is broken
    into 1–3 lines so that its block comes nearest that proportion."""
    words = name.split()
    if not words:
        return []
    best = None
    n = len(words)
    cands = [[name]]
    for i in range(1, n):
        cands.append([' '.join(words[:i]), ' '.join(words[i:])])
        for j in range(i + 1, n):
            cands.append([' '.join(words[:i]), ' '.join(words[i:j]), ' '.join(words[j:])])
    for c in cands:
        mx = max(_units(x) for x in c)
        ratio = .8 * len(c) / mx
        mn = min(_units(x) for x in c)
        score = abs(ratio - 1 / 3) + .12 * (mx - mn) / mx  # nearest the reference's proportion, lines of like length
        if best is None or score < best[0]:
            best = (score, c, mx)
    return best[1], best[2]


def _sentences(t):
    return [s for s in re.split(r'(?<=[.!?…])\s+', (t or '').strip()) if s]


def _a(link, cls, extra=''):
    if not link or not link.get('t'):
        return ''
    # a label that ends in an ellipsis (the client's sign for "opens a dialog") reads as cut off on a button: the dots go
    t = re.sub(r'\s*(…|\.\.\.)\s*$', '', link['t']) or link['t']
    return f'<a class="{cls}" href="{e(link.get("h") or "#")}"{extra}>{e(t)}</a>'


def render(d: dict) -> str:
    g = d.get
    brand = g('brand') or {}
    name = brand.get('name') or ''
    lang = (g('lang') or 'en')[:2]
    more, less, menu_w, close_w = UI.get(lang, ('+', '–', 'Menu', '×'))
    pal = g('palette') or {}
    ground, ink, accent = _rgb(pal.get('ground') or '#ffffff'), _rgb(pal.get('ink') or '#222222'), _rgb(pal.get('accent') or '#888888')
    # the reference's relations: white page · a faint cream for every second section · one pale saturated field ·
    # the ink as the dark field, the buttons and the foot
    cream = _mix(ground, accent, .06)
    t = .30
    tint = _mix(ground, accent, t)
    while _cr(tint, ink) < 7 and t > .04:
        t -= .03
        tint = _mix(ground, accent, t)
    on_ink = _mix(ground, accent, .04)

    hero, place, contact = g('hero') or {}, g('place') or {}, g('contact') or {}
    media = g('media') or {}
    photos = [p for p in (media.get('photos') or []) if p.get('src') and p.get('w') and p.get('h')]

    # ---- pictures: each once, by role and size. A band runs across the page, so it wants 1600px; a picture from
    # 1100px is still taken and then stands no wider than its own pixels. Portraits belong to their people only.
    used = set()

    def pick(roles):
        pool = [p for p in photos if p['src'] not in used and not p.get('small') and p.get('role') != 'portrait'
                and p.get('role') != 'product' and p['w'] >= 1100 and p['w'] >= p['h']]
        if not pool:
            return None
        pool.sort(key=lambda p: (0 if p['w'] >= 1600 else 1, roles.index(p.get('role')) if p.get('role') in roles else len(roles)))
        used.add(pool[0]['src'])
        return pool[0]

    def band(p, cls='', eager=False):
        if not p:
            return ''
        lazy = '' if eager else ' loading="lazy"'
        narrow = f' style="--ar:{p["w"]}/{p["h"]};max-width:{p["w"]}px"' if p['w'] < 1600 else f' style="--ar:{p["w"]}/{p["h"]}"'
        return (f'<figure class="band {cls}" data-slot="photo"{narrow}><img src="{PRE}{e(p["src"])}" width="{p["w"]}" height="{p["h"]}" '
                f'alt="{e(p.get("alt") or "")}"{lazy} decoding="async"></figure>')

    def pick_half(roles):
        pool = [p for p in photos if p['src'] not in used and not p.get('small') and p.get('role') not in ('portrait', 'product')
                and p['w'] >= HALF_MIN_W and p['h'] >= HALF_MIN_H and p['w'] / p['h'] <= HALF_MAX_RATIO]
        if not pool:
            return None
        pool.sort(key=lambda p: (roles.index(p.get('role')) if p.get('role') in roles else len(roles), abs(p['w'] / p['h'] - .8)))
        used.add(pool[0]['src'])
        return pool[0]

    def pic_half(p, cls='', eager=False):
        lazy = '' if eager else ' loading="lazy"'
        return (f'<figure class="pic {cls}" data-slot="photo-half"><img src="{PRE}{e(p["src"])}" width="{p["w"]}" height="{p["h"]}" '
                f'alt="{e(p.get("alt") or "")}"{lazy} decoding="async"></figure>')

    nq = len([q for q in (g('quotes') or []) if q.get('q')])
    RA = ['room', 'people', 'exterior', 'action', 'work', 'workshop', 'landscape', 'bar', 'other', 'detail']
    RB = ['room', 'workshop', 'people', 'work', 'action', 'bar', 'detail', 'other', 'exterior']
    RD = ['detail', 'work', 'room', 'people', 'other', 'exterior']
    # halves first, where the reference has them (opening · after the statement · beside each of the two quotes) …
    hA, hB = pick_half(RA), pick_half(RB)
    hQ = [pick_half(RD) if nq > 0 else None, pick_half(RD) if nq > 1 else None]
    # … and a band across the page where no photograph can fill a half
    pA = None if hA else pick(RA)
    pB = None if hB else pick(RB)
    pC = pick(['exterior', 'landscape', 'room', 'work', 'other', 'detail'])
    pD = None if hQ[0] else pick(RD)

    # ---- the name set large
    wm = _wordmark_lines(name) if name else None

    def wordmark(cls, per_vw, minus_px):
        if not wm:
            return ''
        lines, mx = wm
        fs = f'calc(({per_vw}vw - {minus_px}px) / {mx * 1.1:.3f})'
        return (f'<div class="wm {cls}" style="font-size:{fs}" data-fit>' + ''.join(f'<span>{e(x)}</span>' for x in lines) + '</div>')

    out = []
    # ---- 1 opening
    h1 = hero.get('title') or (g('statement') or {}).get('title') or name
    btns = _a(hero.get('primary') or g('cta'), 'btn') + _a(hero.get('secondary'), 'btn line')
    note = hero.get('note') or ''
    ph = place.get('phone') or contact.get('phone') or {}
    if note:
        if ph.get('t') and ph.get('h') and ph['t'].replace(' ', '') in note.replace(' ', ''):
            btns += f'<a class="tel" href="{e(ph["h"])}">{e(note)}</a>'
        else:
            btns += f'<span class="tel">{e(note)}</span>'
    oar = f' style="--oar:{pA["w"] / pA["h"]:.4f}"' if pA else ''
    out.append(f'<section class="open{" halved" if hA else ""}"{oar}>' + '<div class="open-type"><div class="open-l"><div class="open-text">'
               f'<h1>{e(h1)}</h1>'
               + ''.join(f'<p>{e(x)}</p>' for x in (hero.get('text'), hero.get('text2')) if x)
               + '</div>' + (f'<div class="btns">{btns}</div>' if btns else '') + '</div>'
               + f'<div class="open-r" aria-hidden="true">{wordmark("wm-open", 50, 0)}</div></div>'
               + (pic_half(hA, 'pic-open', True) if hA else band(pA, 'band-open', True)) + '</section>')

    # ---- 2 header: comes after the opening and then stays
    nav = [n for n in (g('nav') or []) if n.get('t')]
    keep, chars = [], 0
    for n in nav:
        if chars + len(n['t']) + 3 > 72:
            break
        keep.append(n)
        chars += len(n['t']) + 3
    links = ''.join(f'<li><a href="{e(n.get("h") or "#")}">{e(n["t"])}</a></li>' for n in keep)
    all_links = ''.join(f'<li><a href="{e(n.get("h") or "#")}">{e(n["t"])}</a></li>' for n in nav)
    out.append(f'<header class="hd"><a class="hd-name" href="{e(brand.get("home") or "#")}">{e(name)}</a>'
               + (f'<nav class="hd-nav" aria-label="{e(menu_w)}"><ul>{links}</ul></nav>' if links else '')
               + (f'<details class="hd-m"><summary aria-label="{e(menu_w)}"><i></i><i></i><i></i></summary><div class="hd-mp"><a class="hd-mname" href="{e(brand.get("home") or "#")}">{e(name)}</a><ul>{all_links}</ul></div></details>' if all_links else '')
               + '</header>')

    # ---- 3 the statement field
    st = g('statement') or {}
    if st.get('text'):
        ss = _sentences(st['text'])
        intro, rest = [], []
        for s in ss:
            if not intro or (len(' '.join(intro)) < 140 and len(' '.join(intro + [s])) <= 300):
                if rest:
                    rest.append(s)
                else:
                    intro.append(s)
            else:
                rest.append(s)
        out.append('<section class="field tint"><div class="exp"><div class="exp-in">'
                   + (f'<h2 class="lab"><u>{e(st["title"])}</u></h2>' if st.get('title') else '')
                   + f'<p class="big">{e(" ".join(intro))}</p></div>'
                   + (f'<div class="exp-more" data-more><div class="exp-pad"><p class="big">{e(" ".join(rest))}</p></div></div>'
                      f'<div class="exp-btn" hidden><button class="btn" type="button" data-more-btn data-more-t="{e(more)} +" data-less-t="{e(less)} -" aria-expanded="false">{e(more)} +</button></div>' if rest else '')
                   + '</div></section>')

    def half(title, text, button, right, cls='', hid=''):
        left = ((f'<h2 class="h">{e(title)}</h2>' if title else '') + (f'<p>{e(text)}</p>' if text else ''))
        return (f'<section class="grid {cls}"><div class="col"><div class="tl">{left}</div>'
                + (f'<div class="tl-btn rv">{button}</div>' if button else '') + f'</div><div class="col">{right}</div></section>')

    alt = [0]

    def ground_cls():
        alt[0] += 1
        return '' if alt[0] % 2 else 'cream'

    # ---- 4 picture, then the practice in headed paragraphs (reference: picture half | text half)
    steps = g('steps') or {}
    items = [s for s in (steps.get('items') or []) if s.get('text') or s.get('title')]
    if not hB:
        out.append(band(pB))
    if items or steps.get('text') or hB:
        blocks = ''
        for s in items:
            lab = s.get('k') or s.get('title')
            blocks += ((f'<h3 class="lab"><u>{e(lab)}</u></h3>' if lab else '') + (f'<p>{e(s["text"])}</p>' if s.get('text') else '')
                       + (f'<p class="more-l">{_a(s.get("cta"), "pill")}</p>' if (s.get('cta') or {}).get('t') and (s.get('cta') or {}).get('h') else ''))
        if hB:
            head = (f'<h2 class="h">{e(steps["title"])}</h2>' if steps.get('title') else '') + (f'<p>{e(steps["text"])}</p>' if steps.get('text') else '')
            out.append(f'<section class="split">{pic_half(hB)}<div class="txt">' + (f'<div class="tl">{head}</div>' if head else '')
                       + (f'<div class="tl blocks">{blocks}</div>' if blocks else '') + '</div></section>')
        else:
            out.append(half(steps.get('title'), steps.get('text'), '', f'<div class="tl blocks">{blocks}</div>', 'top16'))

    # ---- 5 the people
    team = g('team') or {}
    people = list(team.get('items') or [])
    for grp in team.get('groups') or []:
        people += grp.get('items') or []
    people = [p for p in people if p.get('name')]
    if people:
        withp = [p for p in people if p.get('img')]
        without = [p for p in people if not p.get('img')]
        pw = {p['src']: p for p in photos}
        tiles = ''
        for p in withp:
            ph_ = pw.get(p['img']) or {}
            w_, h_ = ph_.get('w') or 400, ph_.get('h') or 400
            extra = ''
            if p.get('text') or p.get('phone') or p.get('email'):
                lines = ''.join(f'<p>{e(x)}</p>' for x in (p.get('text'),) if x)
                if p.get('phone'):
                    lines += f'<p><a href="tel:{e(re.sub(r"[^0-9+]", "", p["phone"]))}">{e(p["phone"])}</a></p>'
                if p.get('email'):
                    lines += f'<p><a href="mailto:{e(p["email"])}">{e(p["email"])}</a></p>'
                extra = (f'<details class="ov"><summary><span class="pill">{e(more)}</span><b class="x" aria-label="{e(close_w)}"></b></summary><div class="ov-in"><div class="ov-l">'
                         + (f'<p class="lab"><u>{e(p["role"])}</u></p>' if p.get('role') else '')
                         + f'<p class="ov-name">{e(p["name"])}</p><div class="ov-t">{lines}</div></div>'
                         f'<img class="ov-img" src="{PRE}{e(p["img"])}" width="{w_}" height="{h_}" alt="" loading="lazy" style="--mw:{w_}px"></div></details>')
            tiles += (f'<li class="tile"><img src="{PRE}{e(p["img"])}" width="{w_}" height="{h_}" alt="{e(p["name"])}" loading="lazy" decoding="async">'
                      f'<div class="tile-t"><h3 class="h3">{e(p["name"])}</h3>' + (f'<p class="role">{e(p["role"])}</p>' if p.get('role') else '') + extra + '</div></li>')
        rows = ''
        for p in without:
            c = ''
            if p.get('phone'):
                c += f'<a href="tel:{e(re.sub(r"[^0-9+]", "", p["phone"]))}">{e(p["phone"])}</a>'
            if p.get('email'):
                c += f'<a href="mailto:{e(p["email"])}">{e(p["email"])}</a>'
            rows += (f'<li class="rv"><h3 class="h3">{e(p["name"])}</h3>' + (f'<p class="role">{e(p["role"])}</p>' if p.get('role') else '')
                     + (f'<p class="pt">{e(p["text"])}</p>' if p.get('text') else '') + (f'<p class="pc">{c}</p>' if c else '') + '</li>')
        out.append('<section class="team"><div class="team-b">'
                   + (f'<h2 class="h rv">{e(team["title"])}</h2>' if team.get('title') else '')
                   + (f'<p class="team-x">{e(team["text"])}</p>' if team.get('text') else '')
                   + (f'<ul class="tiles" data-tiles>{tiles}</ul><div class="dots" data-dots aria-hidden="true"></div>' if tiles else '')
                   + (f'<ul class="plist">{rows}</ul>' if rows else '') + '</div></section>')

    # ---- 6 what is offered: ruled rows that open
    def acc(head, body):
        if not body:
            return f'<div class="row rv"><div class="row-h">{head}</div></div>'
        return f'<details class="acc rv"><summary><span class="row-h">{head}</span><i class="plus"></i></summary><div class="acc-c"><div class="acc-p">{body}</div></div></details>'

    def prices(it_list):
        li = ''
        for it in it_list:
            label = e(it.get('name') or '') + (f' <span class="nt">· {e(it["note"])}</span>' if it.get('note') else '')
            if it.get('state'):
                label += f' <span class="nt">· {e(it["state"])}</span>'
            ps = [(None, it['price'])] if it.get('price') else []
            ps += [(x.get('label'), x.get('price')) for x in (it.get('prices') or []) if x.get('price')]
            if not ps:
                li += f'<li><span>{label}</span></li>'
            for lb, pr in ps:
                li += f'<li><span>{label}{(" <span class=nt>· " + e(lb) + "</span>") if lb else ""}</span><b>{e(pr)}</b></li>'
            if it.get('text'):
                li += f'<li class="sub"><span>{e(it["text"])}</span></li>'
            for r in it.get('rows') or []:
                li += f'<li class="sub"><span>{e(r)}</span></li>'
        return f'<ul class="pr">{li}</ul>' if li else ''

    cat = g('catalogue') or {}
    groups = [x for x in (cat.get('groups') or []) if x.get('items') or x.get('text')]
    cat_names = {(it.get('name') or '').strip().lower() for x in groups for it in (x.get('items') or [])}
    feats = g('features') or {}
    fitems = [f for f in (feats.get('items') or []) if f.get('t')]
    cta = g('cta') or hero.get('primary')
    if fitems and not all(f['t'].strip().lower() in cat_names for f in fitems):
        body = ''.join(acc(e(f['t']), f'<p>{e(f["d"])}</p>' if f.get('d') else '') for f in fitems)
        out.append(half(feats.get('title'), feats.get('text'), _a(cta, 'btn'), f'<div class="accs">{body}</div>', ground_cls()))
    if groups:
        by_group = all((it.get('price') or it.get('prices')) for x in groups for it in (x.get('items') or [])) and len(groups) > 1
        if by_group:
            body = ''
            for x in groups:
                inner = (f'<p>{e(x["text"])}</p>' if x.get('text') else '') + prices(x.get('items') or [])
                body += acc(e(x.get('t') or ''), inner)
            out.append(half(cat.get('title'), cat.get('text'), _a(cta, 'btn'),
                            f'<div class="accs">{body}</div>' + (f'<p class="cnote">{e(cat["note"])}</p>' if cat.get('note') else ''), ground_cls()))
        else:
            for i, x in enumerate(groups):
                body = ''
                for it in x.get('items') or []:
                    inner = (f'<p>{e(it["text"])}</p>' if it.get('text') else '')
                    pr = {k: v for k, v in it.items() if k != 'text'}
                    if it.get('price') or it.get('prices') or it.get('rows') or it.get('note') or it.get('state'):
                        pr['name'] = it.get('note') or ''
                        pr['note'] = None
                        inner += prices([pr])
                    head = e(it.get('name') or '') + (f'<span class="hp">{e(it["price"])}</span>' if it.get('price') else '')
                    body += acc(head, inner)
                title = x.get('t') or (cat.get('title') if i == 0 else '')
                text = x.get('text') or (cat.get('text') if i == 0 else '')
                out.append(half(title, text, _a(cta, 'btn') if i == 0 else '',
                                f'<div class="accs">{body}</div>' + (f'<p class="cnote">{e(cat["note"])}</p>' if cat.get('note') and i == len(groups) - 1 else ''), ground_cls()))

    # ---- plans and questions are never dropped: the same ruled rows
    plans = g('plans') or {}
    pitems = [p for p in (plans.get('items') or []) if p.get('name')]
    if pitems:
        body = ''
        for p in pitems:
            head = e(p['name']) + (f'<span class="hp">{e(p.get("price"))}{(" <small>" + e(p["per"]) + "</small>") if p.get("per") else ""}</span>' if p.get('price') else '')
            inner = ((f'<p>{e(p["line"])}</p>' if p.get('line') else '')
                     + ('<ul class="pr">' + ''.join(f'<li><span>{e(r)}</span></li>' for r in p.get('rows') or []) + '</ul>' if p.get('rows') else '')
                     + (f'<p class="more-l">{_a(p.get("cta"), "pill")}</p>' if (p.get('cta') or {}).get('t') else ''))
            body += f'<div class="row open rv"><div class="row-h">{head}</div><div class="acc-p">{inner}</div></div>'
        out.append(half(plans.get('title'), plans.get('text'), '', f'<div class="accs">{body}</div>' + (f'<p class="cnote">{e(plans["note"])}</p>' if plans.get('note') else ''), ground_cls()))
    faq = g('faq') or {}
    qitems = [q for q in (faq.get('items') or []) if q.get('q')]
    if qitems:
        body = ''.join(acc(e(q['q']), f'<p>{e(q["a"])}</p>' if q.get('a') else '') for q in qitems)
        out.append(half(faq.get('title'), '', '', f'<div class="accs">{body}</div>', ground_cls()))

    # ---- credentials: the reference's headed paragraphs, in both halves
    creds = [c for c in (g('credentials') or []) if c.get('t')]
    if creds:
        cb = ''
        for c in creds:
            lab = e(c['t'])
            lab = f'<a href="{e(c["h"])}">{lab}</a>' if c.get('h') else lab
            cb += f'<div class="cred"><h3 class="lab"><u>{lab}</u></h3>' + (f'<p>{e(c["text"])}</p>' if c.get('text') else '') + '</div>'
        out.append(f'<section class="creds {ground_cls()}">{cb}</section>')

    # ---- 7 how to reach them (reference: heading and button | its drawing — the drawing is not taken)
    def hours_html(hs):
        r = ''.join(f'<tr><th scope="row">{e(h.get("days"))}</th><td>{e(h.get("open") or "")}{"–" if h.get("open") and h.get("close") else ""}{e(h.get("close") or "")}</td></tr>' for h in hs or [] if h.get('days'))
        return f'<table class="hrs">{r}</table>' if r else ''

    def addr_lines(a):
        a = a or {}
        return [x for x in (a.get('street'), ' '.join(x for x in (a.get('postcode'), a.get('city')) if x), a.get('region'), a.get('country')) if x]

    close = g('close') or {}
    rows = ''
    locs = [l for l in (g('locations') or []) if l.get('name') or l.get('address')]
    if locs:
        for l in locs:
            nm = e(l.get('name') or (addr_lines(l.get('address')) or [''])[0])
            nm = f'<a href="{e(l["h"])}">{nm}</a>' if l.get('h') else nm
            b = '<p>' + '<br>'.join(e(x) for x in addr_lines(l.get('address'))) + '</p>' if addr_lines(l.get('address')) else ''
            if l.get('phone'):
                b += f'<p><a href="tel:{e(re.sub(r"[^0-9+]", "", l["phone"]))}">{e(l["phone"])}</a></p>'
            if l.get('email'):
                b += f'<p><a href="mailto:{e(l["email"])}">{e(l["email"])}</a></p>'
            b += hours_html(l.get('hours'))
            if l.get('note'):
                b += f'<p class="gap">{e(l["note"])}</p>'
            rows += f'<div class="row open rv"><div class="row-h">{nm}</div><div class="acc-p">{b}</div></div>'
    else:
        al = addr_lines(place.get('address'))
        if al:
            rows += (f'<div class="row open rv"><div class="row-h">{e(al[0])}</div><div class="acc-p">' + ('<p>' + '<br>'.join(e(x) for x in al[1:]) + '</p>' if al[1:] else '')
                     + hours_html(place.get('hours')) + '</div></div>')
        elif place.get('hours'):
            rows += f'<div class="row open rv"><div class="acc-p">{hours_html(place["hours"])}</div></div>'
    if ph.get('t'):
        hd = f'<a href="{e(ph["h"])}">{e(ph["t"])}</a>' if ph.get('h') else e(ph['t'])
        rows += f'<div class="row open rv"><div class="row-h">{hd}</div>' + (f'<div class="acc-p"><p>{e(ph["note"])}</p></div>' if ph.get('note') else '') + '</div>'
    em = place.get('email') or contact.get('email')
    if em:
        rows += f'<div class="row open rv"><div class="row-h"><a href="mailto:{e(em)}">{e(em)}</a></div></div>'
    for r in contact.get('routes') or []:
        if r.get('t'):
            hd = f'<a href="{e(r["h"])}">{e(r["t"])}</a>' if r.get('h') else e(r['t'])
            rows += f'<div class="row open rv"><div class="row-h">{hd}</div>' + (f'<div class="acc-p"><p>{e(r["note"])}</p></div>' if r.get('note') else '') + '</div>'
    fm = contact.get('form') or {}
    cbtn = _a(close.get('cta') or place.get('booking') or cta, 'btn')
    if fm.get('t') and fm.get('h') and fm.get('h') != (close.get('cta') or {}).get('h'):
        cbtn += _a(fm, 'btn line')
    if close.get('title') or close.get('text') or rows:
        out.append(band(pC))
        out.append(half(close.get('title'), close.get('text'), cbtn, f'<div class="accs">{rows}</div>' if rows else '', 'cream reach'))

    # ---- 8 what clients said: one centred sentence on a colour field (reference: field half | picture half)
    quotes = [q for q in (g('quotes') or []) if q.get('q')]
    fields = ['dark', 'tint', 'creamf']
    for i, q in enumerate(quotes[:3]):
        by = ' · '.join(x for x in (q.get('name'), q.get('role')) if x)
        txt = q['q'].strip()
        if not re.match(r'^[“"„«]', txt):
            txt = '“' + txt + '”'
        fig = f'<figure class="q rv"><blockquote>{e(txt)}</blockquote>' + (f'<figcaption>{e(by)}</figcaption>' if by else '') + '</figure>'
        if i < 2 and hQ[i]:
            fld = f'<div class="field quote {fields[i]}">{fig}</div>'
            out.append('<section class="split qs">' + (fld + pic_half(hQ[i]) if i == 0 else pic_half(hQ[i]) + fld) + '</section>')
        else:
            out.append(f'<section class="field quote {fields[i]}">{fig}</section>')
        if i == 0:
            out.append(band(pD))
    if not quotes:
        out.append(band(pD))

    # ---- 9 foot
    c1 = ''
    if em:
        c1 += f'<p><a href="mailto:{e(em)}">{e(em)}</a></p>'
    if ph.get('t'):
        c1 += f'<p><a href="{e(ph.get("h") or "#")}">{e(ph["t"])}</a></p>'
    for s in place.get('social') or []:
        if s.get('t') and s.get('h'):
            c1 += f'<p><a href="{e(s["h"])}">{e(s["t"])}</a></p>'
    c2 = ''.join(f'<p>{e(x)}</p>' for x in ([name] if name else []) + addr_lines(place.get('address')))
    c3 = hours_html(place.get('hours')) + (f'<p>{e(ph["note"])}</p>' if ph.get('note') and place.get('hours') else '')
    foot = g('foot') or {}
    c4 = ''.join(f'<p><a href="{e(l.get("h") or "#")}">{e(l["t"])}</a></p>' for l in foot.get('links') or [] if l.get('t'))
    small = ''.join(f'<p>{e(x)}</p>' for x in (foot.get('text'), foot.get('legal')) if x)
    footer = ('<footer class="ft"><ul class="ft-c">' + f'<li>{c1}</li><li>{c2}</li><li>{c3}</li><li class="r">{c4}</li></ul>'
              + (f'<div class="ft-s">{small}</div>' if small else '') + wordmark('wm-ft', 100, 32) + '</footer>')

    css = CSS.replace('__GROUND__', _hex(ground)).replace('__INK__', _hex(ink)).replace('__CREAM__', _hex(cream)).replace('__TINT__', _hex(tint)).replace('__ONINK__', _hex(on_ink)).replace('__GRGB__', '%d,%d,%d' % tuple(round(v) for v in ground))
    desc = hero.get('text') or (g('statement') or {}).get('text') or ''
    return (f'<!doctype html><html lang="{e(g("lang") or "en")}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{e(name)}{" — " + e(hero["title"]) if hero.get("title") else ""}</title><meta name="description" content="{e(desc[:160])}">'
            '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400&family=Newsreader:opsz,wght@6..72,300&display=swap">'
            f'<style>{css}</style></head><body><main>{"".join(out)}</main>{footer}<script>{JS}</script></body></html>')


CSS = r"""
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:__GROUND__;color:__INK__;font-family:"DM Mono",ui-monospace,Menlo,Consolas,monospace;font-weight:400;font-size:14px;line-height:1.5;-webkit-font-smoothing:antialiased;overflow-x:hidden}
h1,h2,h3,p,ul,figure,blockquote,table{margin:0;padding:0;font-weight:400}
ul{list-style:none}
img{display:block;max-width:100%;height:auto}
a{color:inherit;text-decoration:none}
p a,.row-h a,.lab a,.ft a,.tel{text-underline-offset:4px}
p a:hover,.row-h a:hover,.ft a:hover,.hd a:hover,a.tel:hover{text-decoration:underline 1px}
:focus-visible{outline:2px solid currentColor;outline-offset:3px;border-radius:2px}
::selection{background:__INK__;color:__GROUND__}
.h,h1,.big,.wm,.ov-name{font-family:"Newsreader","Iowan Old Style","Palatino Linotype",Georgia,serif;font-weight:300;letter-spacing:-.022em;font-size:32px;line-height:1.2}
.h3,.row-h,.hd-name,.hd-mname{font-family:"Newsreader","Iowan Old Style","Palatino Linotype",Georgia,serif;font-weight:300;letter-spacing:-.02em;font-size:24px;line-height:1.2}
.lab{font-family:inherit;font-size:inherit;line-height:1.2;letter-spacing:0;margin-bottom:16px}
.lab u{text-decoration:underline 1px;text-underline-offset:6px}
.btn,.pill{display:inline-block;font:inherit;font-size:12px;line-height:1.8;padding:12.8px 19.2px 11.2px;border-radius:22px;background:__INK__;color:__GROUND__;border:1px solid __INK__;cursor:pointer;transition:background-color .3s cubic-bezier(.645,.045,.355,1),color .3s cubic-bezier(.645,.045,.355,1)}
.btn.line,.pill{background:transparent;color:__INK__}
.pill{padding:3.2px 16px 1.6px}
.btn:hover{background:transparent;color:__INK__}
.btn.line:hover,.pill:hover{background:__INK__;color:__GROUND__}
.btn:active,.pill:active{transform:translateY(1px)}
.btns{display:flex;flex-wrap:wrap;align-items:center;gap:12px 12px;margin-top:40px}
.tel{margin-left:8px}

/* 1 opening */
.open{display:flex;flex-direction:column}
.open-type{display:flex;flex-direction:column;justify-content:space-between;min-height:100svh}
.open-l{padding:16px}
.open-text h1{line-height:1;margin-bottom:16px;max-width:15em}
.open-text p{max-width:482px}
.open-text p+p{margin-top:1.5em}
.wm{line-height:.8;white-space:nowrap;text-align:center;letter-spacing:-.035em;padding:.14em 0 .2em}
.wm span{display:block}
.wm-open span{animation:wmin .7s cubic-bezier(.83,0,.17,1) both}
.wm-open span:nth-child(2){animation-delay:.1s;--from:60%}
.wm-open span:nth-child(3){animation-delay:.05s;--from:60%}
@keyframes wmin{from{transform:translateY(var(--from,-60%));opacity:0}to{transform:none;opacity:1}}
.band{position:relative;width:100%;aspect-ratio:1/1;margin-inline:auto;overflow:hidden;background:__CREAM__}
.band img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:50% 28%}

/* a photograph as one half of the page, edge to edge, as tall as its section (reference: 720×900) */
.split{display:flex;flex-direction:column}
.pic{position:relative;margin:0;aspect-ratio:1/1;overflow:hidden;background:__CREAM__}
.pic-open{aspect-ratio:3/4}
.pic img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:50% 35%}
.split .txt{padding:32px 0 16px}
.split .txt .tl{padding-top:0;padding-bottom:32px}
.qs .pic{order:-1}

/* 2 header */
main{position:relative}
.hd{position:sticky;top:0;z-index:5;height:60px;margin-bottom:-60px;display:flex;align-items:center;justify-content:center;padding:0 8px;background:rgba(__GRGB__,.72);-webkit-backdrop-filter:saturate(180%) blur(10px);backdrop-filter:saturate(180%) blur(10px)}
.hd-name,.hd-nav{display:none}
.hd-m{width:100%}
.hd-m summary{list-style:none;width:50px;height:50px;margin:5px auto;display:flex;flex-direction:column;justify-content:center;align-items:center;gap:6px;cursor:pointer}
.hd-m summary::-webkit-details-marker{display:none}
.hd-m summary i{display:block;width:25px;height:1.5px;background:__INK__;transition:transform .3s cubic-bezier(.645,.045,.355,1),opacity .3s}
.hd-m[open] summary i:nth-child(1){transform:translateY(7.5px) rotate(45deg)}
.hd-m[open] summary i:nth-child(2){opacity:0}
.hd-m[open] summary i:nth-child(3){transform:translateY(-7.5px) rotate(135deg)}
.hd:has(.hd-m[open]){height:auto;align-items:flex-start;background:rgba(__GRGB__,.94)}
.hd-mp{text-align:center;padding:8px 0 24px}
.hd-mname{display:block;margin-bottom:24px}
.hd-mp li{margin-bottom:16px}

/* 3 colour fields */
.field{display:flex;flex-direction:column;justify-content:center;align-items:center;padding:64px 0}
.tint{background:__TINT__}
.creamf{background:__CREAM__}
.dark{background:__INK__;color:__ONINK__}
.exp{width:100%;max-width:135ch;margin:0 auto;text-align:center}
.exp-in{padding:64px 16px 0}
.big{line-height:1}
.exp-more{padding:0 16px;overflow:hidden}
.exp-pad{padding-top:48px}
.exp-btn{padding:48px}
.quote{min-height:50vh}
.q{text-align:center;padding:0 16px;max-width:60ch}
.q blockquote{font-family:"Newsreader","Iowan Old Style",Georgia,serif;font-weight:300;letter-spacing:-.022em;font-size:32px;line-height:1.2}
.q figcaption{margin-top:32px}

/* halves */
.grid{display:flex;flex-direction:column;padding:60px 0 0}
.grid.cream,.creds.cream{background:__CREAM__}
.col{min-width:0}
.tl{padding:32px 16px}
.tl .h{margin-bottom:48px}
.tl p{max-width:90%}
.tl p+p{margin-top:1.5em}
.tl-btn{padding:0 16px 48px;display:flex;flex-wrap:wrap;gap:12px}
.blocks .lab{margin-top:24px}
.blocks .lab:first-child{margin-top:0}
.more-l{margin-top:16px!important}
.accs{margin:16px}
.acc,.row{border-top:1px solid __INK__;position:relative}
.acc summary{list-style:none;cursor:pointer;display:flex;justify-content:space-between;align-items:center;gap:16px;padding:14px 0}
.acc summary::-webkit-details-marker{display:none}
.row>.row-h{padding:14px 0}
.row-h{line-height:1;display:flex;flex-wrap:wrap;justify-content:space-between;align-items:baseline;gap:16px;flex:1;min-width:0;overflow-wrap:anywhere}
.hp{white-space:nowrap}
.hp small{font-family:"DM Mono",monospace;font-size:14px;letter-spacing:0}
.plus{flex:none;position:relative;width:40px;height:28px}
.plus::before,.plus::after{content:"";position:absolute;left:30%;top:50%;width:40%;height:1px;background:__INK__;transition:transform .3s cubic-bezier(.645,.045,.355,1)}
.plus::after{transform:rotate(90deg)}
.acc[open] .plus::after{transform:rotate(180deg)}
.acc-c{overflow:hidden}
.acc-p{padding:16px 8px 32px 0}
.row .acc-p{padding-top:0}
.acc-p p+p{margin-top:1.5em}
.acc-p p+.pr{margin-top:32px}
.acc-p .hrs{margin-top:1.5em}
.pr li{display:flex;justify-content:space-between;gap:24px}
.pr li b{font-weight:400;white-space:nowrap;text-align:right}
.pr li.sub{opacity:1;padding-left:16px}
.cnote{margin:16px;max-width:90%}
.gap{margin-top:1.5em!important}
.hrs{border-collapse:collapse}
.hrs th{font-weight:400;text-align:left;padding:0 24px 0 0;vertical-align:top;white-space:nowrap}
.hrs td{padding:0;white-space:nowrap}
.reach{padding-bottom:16px}
.creds{padding:60px 0 32px}
.cred{padding:0 16px 32px}
.cred p{max-width:90%}

/* 5 people */
.team{background:__CREAM__;padding:48px 0 64px}
.team .h{text-align:center;margin-bottom:32px;padding:0 16px}
.team-x{text-align:center;max-width:60ch;margin:0 auto 32px;padding:0 16px}
.tiles{display:flex;gap:16px;overflow-x:auto;scroll-snap-type:x mandatory;padding:0 16px;scrollbar-width:none}
.tiles::-webkit-scrollbar{display:none}
.tile{flex:0 0 286px;scroll-snap-align:center;display:flex;flex-direction:column}
.tile>img{width:100%;border-radius:10px 10px 0 0}
.tile-t{background:__GROUND__;padding:8px 8px 16px;flex:1}
.tile .ov{margin-top:16px}
.dots{display:flex;justify-content:center;align-items:center;gap:19px;height:24px;margin-top:32px}
.dots i{width:5px;height:5px;border-radius:50%;background:__INK__;border:1px solid __INK__;transition:transform .2s linear,background-color .2s linear}
.dots i.on{transform:scale(2);background:transparent;border-width:.5px}
.plist{margin:48px 16px 0}
.plist li{border-top:1px solid __INK__;padding:16px 0}
.plist .pt{margin-top:8px;max-width:60ch}
.plist .pc{margin-top:8px;display:flex;flex-wrap:wrap;gap:0 24px}
.ov summary{list-style:none;cursor:pointer;display:inline-block}
.ov summary::-webkit-details-marker{display:none}
.ov .x{display:none}
.ov[open] summary{position:fixed;z-index:11;top:8px;right:8px;width:60px;height:60px}
.ov[open] summary .pill{display:none}
.ov[open] .x{display:block;position:absolute;inset:0}
.x::before,.x::after{content:"";position:absolute;left:15%;top:50%;width:70%;height:1px;background:__INK__;transform:rotate(45deg)}
.x::after{transform:rotate(-45deg)}
.ov-in{position:fixed;z-index:10;inset:0;overflow:auto;padding:16px;background:rgba(__GRGB__,.9);-webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);display:flex;flex-direction:column;justify-content:space-between;gap:32px;animation:ovin .3s cubic-bezier(.645,.045,.355,1)}
@keyframes ovin{from{opacity:0}to{opacity:1}}
.ov-l{padding-right:56px}
.ov-name{margin:32px 0}
.ov-t p{max-width:60ch}
.ov-t p+p{margin-top:1.5em}
.ov-img{align-self:flex-end;width:auto;max-width:min(60vw,var(--mw,400px))}

/* 9 foot */
.ft{background:__INK__;color:__ONINK__;padding:60px 16px 16px}
.ft-c{display:flex;flex-direction:column;gap:16px}
.ft-c li:empty{display:none}
.ft-s{margin-top:32px;max-width:90ch}
.ft-s p+p{margin-top:.75em}
.wm-ft{margin-top:120px}

/* reveal: only when scripts run */
.js .rv{opacity:0;translate:0 20px;transition:opacity .6s cubic-bezier(.42,0,.58,1),translate .6s cubic-bezier(.42,0,.58,1)}
.js .rv.in{opacity:1;translate:0 0}

@media (min-width:720px){
body{font-size:calc(12px + .2315vw)}
.h,h1,.big,.ov-name{font-size:calc(8px + 3.33333vw)}
.q blockquote{font-size:calc(17.3333px + 2.03704vw)}
.h3,.row-h,.hd-name{font-size:calc(18px + .833333vw)}
.btn,.pill{font-size:calc(10.6667px + .185185vw)}
.hp small{font-size:calc(12px + .2315vw)}
.open-type{flex-direction:row;align-items:stretch;min-height:0}
.open:has(.band) .open-type{min-height:calc(100svh - min(62svh,100vw / (var(--oar,2.9))))}
.open:not(:has(.band)) .open-type{min-height:100svh}
.open-l,.open-r{flex:0 0 50%;min-width:0}
.open-r{display:flex;flex-direction:column;justify-content:flex-end}
.open.halved{flex-direction:row}
.open.halved .open-type{flex:0 0 50%;flex-direction:column;justify-content:space-between;min-height:100svh}
.open.halved .open-l,.open.halved .open-r{flex:none}
.open.halved>.pic{flex:0 0 50%;min-width:0}
.split{flex-direction:row;align-items:stretch}
.split>*{flex:0 0 50%;min-width:0}
.pic,.pic-open{aspect-ratio:auto;min-height:100svh}
.split .txt{padding:16px 0}
.split .txt .tl{padding-bottom:48px}
.split .field.quote{min-height:100svh;padding:96px 0}
.qs .pic{order:0}
.band{aspect-ratio:var(--ar);max-height:100svh}
.band-open{max-height:62svh}
.hd{justify-content:space-between;padding:16px}
.hd-m{display:none}
.hd-name{display:block;flex:1;line-height:.8;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;padding:.2em 0}
.hd-nav{display:block;flex:1;padding-left:16px}
.hd-nav ul{display:flex;justify-content:space-between;gap:16px;white-space:nowrap}
.field{padding:192px 0;min-height:100vh}
.field.quote{padding:160px 0;min-height:0}
.exp-in{padding:64px 80px 0}
.exp-more{padding:0 80px}
.q{padding:0 96px;max-width:calc(60ch + 192px)}
.grid{flex-direction:row}
.col{flex:0 0 50%}
.tl{padding:0 16px 16px}
.tl-btn{padding:34px 16px 48px}
.top16{padding-top:16px}
.team{padding:32px 0}
.team-b{padding:160px 112px}
.team .h{margin-bottom:80px;padding:0}
.team-x{margin:-48px auto 80px}
.tiles{flex-wrap:wrap;overflow:visible;padding:0}
.tile{flex:0 0 calc(25% - 12px)}
.tile-t{padding:16px}
.dots{display:none}
.plist{margin:80px 0 0;column-count:2;column-gap:32px}
.plist li{break-inside:avoid}
.creds{display:flex;flex-wrap:wrap;padding:76px 0 44px}
.cred{flex:0 0 50%}
.ov-in{flex-direction:row;align-items:flex-end}
.ov-l{flex:0 0 55%;align-self:flex-start;padding-right:0}
.ov-img{max-width:min(25vw,var(--mw,400px))}
.ov[open] summary{width:150px;height:150px;top:-30px;right:-30px}
.x::before,.x::after{left:30%;width:40%}
.ft-c{flex-direction:row;gap:0}
.ft-c li{flex:2}
.ft-c li:nth-child(3){flex:1.4}
.ft-c li.r{text-align:right}
.ft-c li:empty{display:block}
.wm-ft{margin-top:240px}
}
@media (min-width:1800px){
body{font-size:16.2px}
.h,h1,.big,.ov-name{font-size:68px}
.q blockquote{font-size:54px}
.h3,.row-h,.hd-name{font-size:33px}
.btn,.pill{font-size:14px}
}
@media (prefers-reduced-motion:reduce){
*,*::before,*::after{animation:none!important;transition:none!important}
.js .rv{opacity:1;translate:none}
}
"""

JS = r"""
(function(){var D=document,R=D.documentElement;R.classList.add('js');
var calm=matchMedia('(prefers-reduced-motion:reduce)').matches;
/* the name fills its measure: the longest line sets the size */
function fit(){D.querySelectorAll('[data-fit]').forEach(function(w){var cw=w.clientWidth;if(!cw)return;var fs=parseFloat(getComputedStyle(w).fontSize),mx=0;
w.querySelectorAll('span').forEach(function(s){s.style.display='inline-block';mx=Math.max(mx,s.getBoundingClientRect().width);s.style.display='';});
if(mx>0)w.style.fontSize=(fs*(cw*.975)/mx).toFixed(2)+'px';});}
fit();if(D.fonts&&D.fonts.ready)D.fonts.ready.then(fit);addEventListener('load',fit);var rt;addEventListener('resize',function(){clearTimeout(rt);rt=setTimeout(fit,120);});
/* things come in once when they enter the window: .6s ease-in-out, 20px */
var rv=[].slice.call(D.querySelectorAll('.rv'));
if('IntersectionObserver' in window&&!calm){var io=new IntersectionObserver(function(es){es.forEach(function(x){if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target);}});});rv.forEach(function(x){io.observe(x);});}
else rv.forEach(function(x){x.classList.add('in');});
/* rows open over .25s */
D.querySelectorAll('details.acc').forEach(function(d){var s=d.querySelector('summary'),c=d.querySelector('.acc-c'),busy=null;
s.addEventListener('click',function(ev){if(calm||!c.animate)return;ev.preventDefault();if(busy)busy.cancel();
var o={duration:250,easing:'cubic-bezier(.4,0,.2,1)'};
if(d.open&&!d.hasAttribute('data-closing')){d.setAttribute('data-closing','');d.classList.add('shut');var h=c.offsetHeight;busy=c.animate({height:[h+'px','0px']},o);busy.onfinish=function(){d.open=false;d.removeAttribute('data-closing');d.classList.remove('shut');busy=null;};}
else{d.removeAttribute('data-closing');d.classList.remove('shut');d.open=true;var h2=c.offsetHeight;busy=c.animate({height:['0px',h2+'px']},o);busy.onfinish=function(){busy=null;};}});});
/* the statement's second half opens over .7s */
D.querySelectorAll('[data-more]').forEach(function(m){var wrap=m.parentNode.querySelector('.exp-btn'),b=wrap&&wrap.querySelector('[data-more-btn]');if(!b)return;
wrap.hidden=false;m.style.height='0px';m.setAttribute('aria-hidden','true');m.style.visibility='hidden';var open=false,an=null;
b.addEventListener('click',function(){open=!open;b.textContent=open?b.getAttribute('data-less-t'):b.getAttribute('data-more-t');b.setAttribute('aria-expanded',open);
var full=m.scrollHeight;if(an)an.cancel();m.style.visibility='visible';m.setAttribute('aria-hidden',!open);
if(calm||!m.animate){m.style.height=open?'auto':'0px';if(!open)m.style.visibility='hidden';return;}
an=m.animate({height:open?['0px',full+'px']:[full+'px','0px']},{duration:700,easing:'cubic-bezier(.4,0,.2,1)'});
m.style.height=open?'auto':'0px';an.onfinish=function(){if(!open)m.style.visibility='hidden';an=null;};});});
/* a person's sheet: Escape closes it, the page behind does not scroll */
var ovs=[].slice.call(D.querySelectorAll('details.ov'));
ovs.forEach(function(o){o.addEventListener('toggle',function(){if(o.open)ovs.forEach(function(x){if(x!==o)x.open=false;});D.body.style.overflow=ovs.some(function(x){return x.open;})?'hidden':'';});});
addEventListener('keydown',function(ev){if(ev.key==='Escape'){ovs.forEach(function(o){if(o.open){o.open=false;o.querySelector('summary').focus();}});var m=D.querySelector('.hd-m[open]');if(m)m.open=false;}});
/* phone: the row of people is swiped; dots say where */
D.querySelectorAll('[data-tiles]').forEach(function(t){var dots=t.parentNode.querySelector('[data-dots]'),n=t.children.length;if(!dots||n<2)return;
for(var i=0;i<n;i++)dots.appendChild(D.createElement('i'));
function on(){var w=t.children[0].getBoundingClientRect().width+16,k=Math.max(0,Math.min(n-1,Math.round(t.scrollLeft/w)));for(var i=0;i<n;i++)dots.children[i].classList.toggle('on',i===k);}
t.addEventListener('scroll',on,{passive:true});on();});
})();
"""
