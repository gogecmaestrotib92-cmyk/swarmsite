"""clicky/render.py — one pure function: render(d) -> a complete page built to the measures of the reference
(a desktop: a 53px menu bar, a dotted ground with small draggable windows round a centred headline, one large film
frame, feature rows where a typed request bubble sits beside a window on a wallpaper, a notes window, a wall of small
windows, plan windows on a sky, a terminal window, a list of questions, a foot with the name set in blocks).
No client, no model call, no file reads, no network at render."""
import html

M = '../../'
FONT = 'Inter'                  # the reference's own face (SIL OFL)
MONO = 'Geist Mono'             # the reference's own mono (SIL OFL)
BLOCK = 'Pixelify Sans'         # stand-in for the reference's name built from blocks, at the foot only


def e(s):
    return html.escape(str(s or ''), quote=True)


# ---------- colour: the client's palette goes in, the reference's light/dark/accent relations are kept ----------
def _rgb(h):
    h = h.lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _hex(c):
    return '#%02x%02x%02x' % tuple(max(0, min(255, round(v))) for v in c)


def mix(a, b, t):
    A, B = _rgb(a), _rgb(b)
    return _hex(tuple(A[i] + (B[i] - A[i]) * t for i in range(3)))


def lum(h):
    def f(v):
        v /= 255
        return v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4
    r, g, b = _rgb(h)
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b)


def con(a, b):
    x, y = lum(a), lum(b)
    return (max(x, y) + .05) / (min(x, y) + .05)


def best(bg, *cands):
    return max(cands, key=lambda c: con(bg, c))


def rgba(h, a):
    r, g, b = _rgb(h)
    return f'rgba({r},{g},{b},{a:.2f})'


def quiet(ink, grounds, start, want=4.6):
    """the reference's grey text (ink at 60 / 50 / 40 %), held readable on every ground it stands on"""
    t = start
    while t > 0:
        m = mix(ink, grounds[0], t)
        if min(con(m, g) for g in grounds) >= want:
            return m
        t -= .04
    return ink


def colours(p):
    G, I, A = p.get('ground', '#f5f5f5'), p.get('ink', '#000000'), p.get('accent', '#0f7fff')
    dark = lum(G) < .2
    card = mix(G, I, .08) if dark else mix(G, '#ffffff', .85)
    clo, chi = (mix(G, I, .12), mix(G, I, .22)) if dark else (mix(G, I, .13), mix(G, I, .03))
    veilg = mix(G, card, .5)
    mu = quiet(I, [G, card, clo], .4, 5.0)                      # 60% ink: body copy under a heading
    mu2 = quiet(I, [G, card, clo], .5, 5.8)                     # 50–40% ink: captions, notes
    link = A
    for t in (0, .1, .2, .3, .4, .5, .6, .7, .8):                # the accent as a text link
        link = mix(A, I, t)
        if min(con(link, G), con(link, card)) >= 4.6:
            break
    mark = next((mix(A, I, t) for t in (0, .1, .2, .3, .4, .5, .6) if con(mix(A, I, t), G) >= 3.1), I)   # the name at the foot: large type, 3:1
    p1, p2, p3 = mix(A, '#ffffff', .82), mix(A, '#ffffff', .5), mix(A, '#ffffff', .46)
    pon = best(p3, '#000000', '#ffffff')
    pbd = mix(A, '#000000', .55)
    if dark:
        s1, s2, s3, sbd = mix(G, I, .28), mix(G, I, .18), mix(G, I, .14), mix(G, I, .5)
    else:
        s1, s2, s3, sbd = mix(card, '#ffffff', .6), mix(G, I, .05), mix(G, I, .1), mix(G, I, .62)
    edge = mix(G, I, .34) if dark else I
    term = mix(G, I, .09) if dark else mix(I, '#000000', .25)
    if lum(term) > .08:
        term = '#1a1a1a'
    ton = '#ffffff'
    tmu = quiet(ton, [mix(term, G, .06)], .5, 5.6)
    btc = quiet(I, [clo, chi, mix(clo, A, .2), mix(chi, A, .2)], .5, 4.7)
    hues = []
    for x in [A] + list(p.get('extra') or []):
        if x.lower() not in [h.lower() for h in hues] and con(x, G) > 1.15:
            hues.append(x)
    return dict(G=G, I=I, A=A, dark=dark, card=card, clo=clo, chi=chi, mu=mu, mu2=mu2, link=link, p1=p1, p2=p2, p3=p3,
                pon=pon, pbd=pbd, s1=s1, s2=s2, s3=s3, sbd=sbd, edge=edge, term=term, ton=ton, tmu=tmu, hues=hues or [A], btc=btc,
                veilg=veilg, mark=mark)


def made(d, kind):
    """pictures made for the client, by kind (CONTRACT.md "Made pictures"); a list, empty when the kind is absent"""
    m = ((d.get('media') or {}).get('made') or {}).get(kind) or []
    return [x for x in (m if isinstance(m, list) else [m]) if x.get('src')]


def asp(m):
    return (m.get('w') or 16) / (m.get('h') or 10)


def pic(m, lazy=True, cls=''):
    """a picture shown whole, at its own proportion"""
    return (f'<img{f" class={chr(34)}{cls}{chr(34)}" if cls else ""} src="{M}{e(m["src"])}" width="{int(m.get("w") or 0) or ""}" '
            f'height="{int(m.get("h") or 0) or ""}" alt="{e(m.get("alt"))}"{" loading=lazy decoding=async" if lazy else ""} draggable="false">')


def bg_pic(m, slot, lazy=True, at=''):
    """a made picture as the ground of its box: covers it, never the subject"""
    return (f'<img class="bd" src="{M}{e(m["src"])}" width="{int(m.get("w") or 0) or ""}" height="{int(m.get("h") or 0) or ""}" alt="" '
            f'{"loading=lazy decoding=async " if lazy else ""}data-slot="{slot}"{f" style={chr(34)}object-position:{at}{chr(34)}" if at else ""} draggable="false">')


def family(d, c):
    """ONE picture family for the page (CONTRACT.md): the reference repeats a single landscape wallpaper behind every row
    and carries its sky on behind the plans. So: `land` only — one wallpaper (the valley) for every row and, held quiet,
    for the notes band; its wide, empty neighbour behind the plans. A dark page never takes a light picture as a ground."""
    land = made(d, 'land')
    ok = lambda m: not (c['dark'] and m.get('tone') == 'light')
    wall = next((land[i] for i in (1, 0, 5) if i < len(land) and ok(land[i])), None)
    wide = next((land[i] for i in (5, 0) if i < len(land) and ok(land[i]) and asp(land[i]) >= 1.5), None)
    return wall, wide


DOTS = '<span class="dots" aria-hidden="true"><i></i><i></i><i></i></span>'
CHECK = ('<svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><circle cx="8" cy="8" r="8" fill="currentColor"/>'
         '<path d="M4.6 8.3l2.3 2.2 4.5-4.8" fill="none" stroke="var(--ck)" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>')
PLUS = '<svg class="pl" viewBox="0 0 20 20" width="20" height="20" aria-hidden="true"><path d="M10 3.5v13M3.5 10h13" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>'
TAIL = ('<svg class="tail" viewBox="0 0 18 16" width="18" height="16" aria-hidden="true"><path d="M1 .5C6 4.5 10 3 13.5.5c-1.6 3.4-.9 7 1 9.600 1.200 1.700.4 3.400-1.800 2.900C8.500 12 3.500 8 1 .5z" '
        'fill="var(--bt)" stroke="var(--bb)" stroke-width="1"/><path d="M1.500.300C6 3.800 10 2.600 13.200.300" fill="none" stroke="var(--bt)" stroke-width="2.200"/></svg>')


def btn(c, kind='sec', extra=''):
    if not c or not c.get('t'):
        return ''
    return f'<a class="btn {kind}{extra}" href="{e(c.get("h") or "#")}"><span>{e(c["t"])}</span></a>'


def size(text, steps):
    n = len(text or '')
    for lim, v in steps:
        if n <= lim:
            return v
    return steps[-1][1]


# ---------- sections ----------
def s_menubar(d, c):
    b = d.get('brand') or {}
    word = bool(b.get('logo') and b.get('logo_wordmark'))
    name = '' if word or not b.get('name') else f'<a class="mbn" href="{e(b.get("home") or "#")}">{e(b["name"])}</a>'
    links = ''.join(f'<a href="{e(n.get("h"))}">{e(n.get("t"))}</a>' for n in d.get('nav') or [] if n.get('t'))
    logo = ''
    if b.get('logo'):
        logo = (f'<a class="mlg{" word" if word else ""}" href="{e(b.get("home") or "#")}"{"" if word else " aria-hidden=true tabindex=-1"}>'
                f'<img src="{M}{e(b["logo"])}" alt="{e(b.get("name")) if word else ""}"></a>')
    si, ct = d.get('signin') or {}, d.get('cta') or {}
    signin = f'<a class="msi" href="{e(si.get("h"))}">{e(si["t"])}</a>' if si.get('t') else ''
    cta = f'<a class="mct" href="{e(ct.get("h"))}">{e(ct["t"])}</a>' if ct.get('t') else ''
    panel = ''.join(f'<a href="{e(n.get("h"))}">{e(n.get("t"))}</a>' for n in (d.get('nav') or []) + ([si] if si.get('t') else []) if n.get('t'))
    burger = ('<button class="mtg" type="button" aria-expanded="false" aria-controls="mcc" aria-label="Menu"><i></i><i></i></button>' if panel else '')
    return f'''<header class="mb" id="top"><div class="mr">
<nav class="ml" aria-label="Primary">{name}{links}</nav>{logo}
<div class="mrr">{signin}{cta}{burger}</div></div></header>
{f'<nav class="mcc" id="mcc" aria-label="Menu" hidden>{panel}</nav>' if panel else ''}'''


SLOTS = [  # the five small windows of the opening at 1440: anchor, offset, top, outer width for a landscape / a portrait picture
    # … and the tallest its picture may stand (the reference's own screens are 97, 114, 201, 244 and 119 high)
    ('L', 'c', -193, 25, 182, 120, 110), ('L', 'r', 194, 62, 250, 140, 135), ('P', 'l', 125, 75, 200, 123, 250),
    ('P', 'r', 31, 378, 210, 147, 300), ('L', 'l', 38, 405, 222, 132, 190)]


def hero_media(d):
    md = d.get('media') or {}
    used = {i.get('img') for i in (d.get('steps') or {}).get('items') or []}
    key = lambda m: m.get('src') in used                               # pictures the feature rows do not show come first
    alls = [x for x in (md.get('screens') or []) + (md.get('phones') or []) + (md.get('photos') or []) if x.get('src')]
    land = [x for x in alls if 1 <= asp(x) <= 2.6]
    port = sorted([x for x in alls if asp(x) < 1], key=key)
    v = md.get('video')
    big = None
    if v and v.get('src'):
        big = ('video', v)
    elif land:
        big = ('img', land.pop(0))
    land.sort(key=key)
    wins = []
    for kind, anchor, off, top, wl, wp, hmax in SLOTS:
        pool = (land, port) if kind == 'L' else (port, land)
        m = pool[0].pop(0) if pool[0] else (pool[1].pop(0) if pool[1] else None)
        if not m:
            continue
        w = round(min((wl if asp(m) >= 1 else wp) - 10, hmax * asp(m))) + 10
        pos = {'c': f'left:calc(50% + var(--u)*{off})', 'l': f'left:calc(var(--u)*{off})', 'r': f'right:calc(var(--u)*{off})'}[anchor]
        wins.append((m, w, pos, top))
    return big, wins


def s_hero(d, c):
    h = d.get('hero') or {}
    big, wins = hero_media(d)
    title = h.get('title') or (d.get('brand') or {}).get('name') or ''
    fs = size(title, [(12, 88), (24, 72), (999, 56)])
    fm = size(title, [(12, 56), (999, 36)])
    wh = ''
    for n, (m, w, pos, top) in enumerate(wins):
        cap = f'<figcaption class="cap" title="{e(m["alt"])}">{e(m["alt"])}</figcaption>' if m.get('alt') else ''
        wh += (f'<figure class="win" style="{pos};top:calc(var(--u)*{top});--w:{w};--n:{n + 4}"><div class="fr"><div class="bar">{DOTS}</div>'
               f'<div class="scr">{pic(m, lazy=False)}</div></div>{cap}</figure>')
    sub = f'<p class="sub">{e(h["text"])}</p>' if h.get('text') else ''
    sub2 = f'<p class="sub2">{e(h["text2"])}</p>' if h.get('text2') else ''
    note = next((t for t in d.get('trust') or [] if t and t != h.get('note')), '')
    b1, b2 = btn(h.get('primary'), 'pri'), btn(h.get('secondary'))
    if b1:
        b1 = f'<div class="bc">{b1}{f"<p class=bsub>{e(note)}</p>" if note else ""}</div>'
    if b2:
        b2 = f'<div class="bc">{b2}</div>'
    btns = f'<div class="btns">{b1}{b2}</div>' if b1 or b2 else ''
    bh = ''
    if big:
        k, m = big
        if k == 'video':
            poster = ' poster="%s%s"' % (M, e(m['poster'])) if m.get('poster') else ''
            inner = (f'<video src="{M}{e(m["src"])}"{poster} width="{m.get("w")}" height="{m.get("h")}" '
                     f'muted loop playsinline preload="metadata" tabindex="0" aria-label="{e(m.get("alt"))}" data-auto></video>')
        else:
            inner = pic(m, lazy=False)
        cap = f'<figcaption class="cap">{e(m["alt"])}</figcaption>' if m.get('alt') else ''
        bh = f'<figure class="big" style="--bw:{min(800, 520 * asp(m)):.0f}"><div class="fr">{inner}</div>{cap}</figure>'
    return f'''<section class="hero"><div class="wins">{wh}</div>
<div class="head"><div class="hg"><h1 style="--fs:{fs};--fm:{fm}">{e(title)}</h1>{sub}{sub2}</div>{btns}</div>
{bh}</section>'''


def s_steps(d, c):
    st = d.get('steps') or {}
    items = [i for i in st.get('items') or [] if i.get('title') or i.get('k')]
    if not items:
        return ''
    md = d.get('media') or {}
    known = {m['src']: m for m in (md.get('screens') or []) + (md.get('phones') or []) + (md.get('photos') or []) if m.get('src')}
    wallp = family(d, c)[0]                                         # one wallpaper for every row, as on the reference
    crops = ('50% 62%', '50% 38%', '50% 82%')                       # … seen through a different part of it each time
    brand = (d.get('brand') or {}).get('name')
    bt = '<span class="bt">%s</span>' % e(brand) if brand else ''
    head = ''
    if st.get('title'):
        sub = '<p>%s</p>' % e(st['text']) if st.get('text') else ''
        head = f'<div class="sh rv"><h2 class="h56">{e(st["title"])}</h2>{sub}</div>'
    rows = ''
    heights = [14, 15, 16, 13, 12, 14, 11, 10, 11, 17, 22, 11]
    for n, i in enumerate(items):
        bars = ''.join(f'<i style="--h:{heights[(k + n * 5) % 12]}px"></i>' for k in range(12))
        req = f'<p class="bub req">{TAIL}<span class="tx">{e(i.get("k"))}</span></p>' if i.get('k') else ''
        cta = i.get('cta') or {}
        rep = f'<a class="bub rep" href="{e(cta.get("h"))}"><span>{e(cta["t"])}</span></a>' if cta.get('t') else ''
        convo = f'<div class="mid"><div class="convo">{req}{rep}</div></div>' if req or rep else '<div class="mid"></div>'
        copy = ('<div class="copy">' + ('<h3>%s</h3>' % e(i['title']) if i.get('title') else '')
                + ('<p>%s</p>' % e(i['text']) if i.get('text') else '') + '</div>')
        shot = ''
        if i.get('img'):
            m = known.get(i['img'], {'src': i['img'], 'alt': i.get('title')})
            wall = bg_pic(wallp, 'wallpaper', at=crops[n % 3]) if wallp else ''
            shot = (f'<div class="shot"><div class="desk{"" if wall else " plain"}">{wall}</div><figure class="fig" style="--r:{asp(m):.4f}">'
                    f'<div class="bar">{DOTS}{bt}</div><div class="scr">{pic(m)}</div></figure></div>')
        rows += (f'<div class="row{" r" if n % 2 else ""}{"" if shot else " noshot"}"><div class="txt"><div class="wave" aria-hidden="true">'
                 f'<span class="wb">{bars}</span></div>{convo}{copy}</div>{shot}</div>')
    return f'''<section class="feat{' hashead' if head else ''}" id="feat">{head}<div class="rows">{rows}</div></section>'''


def s_statement(d, c):
    s = d.get('statement') or {}
    if not s.get('title') and not s.get('text'):
        return ''
    b = d.get('brand') or {}
    wallp = family(d, c)[0]                                         # the rows' wallpaper again, held quiet toward the ground
    band = f'<div class="band">{bg_pic(wallp, "band", at="50% 30%")}</div>' if wallp else ''
    ps = ''
    if s.get('title'):
        ps += f'<h2 class="np"><span class="ink">{e(s["title"])}</span></h2>'
    if s.get('text'):
        ps += f'<p class="np">{e(s["text"])}<span class="caret" aria-hidden="true"></span></p>'
    sign = ''
    if b.get('logo') or b.get('name'):
        word = b.get('logo') and b.get('logo_wordmark')
        img = f'<img src="{M}{e(b["logo"])}" alt="{e(b.get("name")) if word else ""}" loading="lazy">' if b.get('logo') else ''
        sign = '<div class="sign">' + img + ('' if word else '<span>%s</span>' % e(b.get('name'))) + '</div>'
    return f'''<section class="dream{'' if band else ' noband'}">{band}
<div class="note rv"><div class="tb">{DOTS}{f'<span class="bt">{e(b.get("name"))}</span>' if b.get('name') else ''}</div>
<div class="doc">{ps}{sign}</div></div></section><div class="stroke" aria-hidden="true"></div>'''


def s_wall(d, c):
    f = d.get('features') or {}
    items = [i for i in f.get('items') or [] if i.get('t') or i.get('d')]
    figs = [x for x in d.get('figures') or [] if x.get('v')]
    h = d.get('hero') or {}
    if not items and not figs and not f.get('title'):
        return ''
    head = ''
    if f.get('title'):
        t = e(f['title'])
        ghost = f'<span aria-hidden="true">{t}</span>'
        head = f'<h2 class="mq rv"><span class="mqt">{ghost * 2}<span class="on">{t}</span>{ghost * 2}</span></h2>'
        if f.get('text'):
            head += f'<p class="fsub rv">{e(f["text"])}</p>'
    cards = ''
    hues = c['hues']
    for n, i in enumerate(items):
        cards += (f'<article class="fc"><div class="fbar" style="--hue:{rgba(hues[n % len(hues)], .2)}">{DOTS}</div><div class="fbd">'
                  + ('<h3>%s</h3>' % e(i['t']) if i.get('t') else '') + ('<p>%s</p>' % e(i['d']) if i.get('d') else '') + '</div></article>')
    for n, x in enumerate(figs):
        cards += (f'<article class="fc"><div class="fbar" style="--hue:{rgba(hues[(n + len(items)) % len(hues)], .2)}">{DOTS}</div><div class="fbd">'
                  f'<strong class="fv">{e(x["v"])}</strong>' + ('<p>%s</p>' % e(x['l']) if x.get('l') else '') + '</div></article>')
    wall = f'<div class="wall rv" style="--n:{min(3, max(1, len(items) + len(figs)))}">{cards}</div>' if cards else ''
    ban = ''
    ct = d.get('cta') or {}
    if h.get('note'):
        link = f' <a href="{e(ct.get("h"))}">{e(ct["t"])}</a>' if ct.get('t') else ''
        ban = f'<div class="ban rv"><p>{e(h["note"])}{link}</p></div>'
    return f'''<section class="fb" id="fb">{head}{wall}{ban}</section>'''


def s_plans(d, c):
    p = d.get('plans') or {}
    items = [i for i in p.get('items') or [] if i.get('name')]
    cl = d.get('close') or {}
    term = ''
    if cl.get('title'):
        term = (f'<div class="term rv"><div class="bar">{DOTS}</div><div class="tp"><div class="tc"><h2>{e(cl["title"])}<span class="blk" aria-hidden="true"></span></h2>'
                + ('<p>%s</p>' % e(cl['text']) if cl.get('text') else '') + f'</div>{btn(cl.get("cta"), "sec", " mono")}</div></div>')
    if not items and not term:
        return ''
    wide = family(d, c)[1]
    skyh, ink = '', c['I']
    if wide and items:
        m = wide
        darkpic = m.get('tone') != 'light'
        veil, ink = (c['G'], c['I']) if darkpic == c['dark'] else (c['I'], c['G'])
        mean = m.get('mean') or ('#222222' if darkpic else '#dddddd')
        # the picture where it comes nearest the text colour: the upper third of this landscape is its open sky, taken
        # as half-way from the picture's mean to the text colour; the veil is solved to hold the text against that
        worst = mix(mean, ink, .5)
        a = next((t for t in (.2, .3, .4, .5, .6, .7, .8) if con(mix(worst, veil, t), ink) >= 4.6), .85)
        skyh = (f'<div class="sky" style="--sv:{rgba(veil, a)};--sv0:{rgba(veil, 0)};--sr:{asp(m):.4f}">{bg_pic(m, "backdrop")}</div>')
    head = ''
    if items and (p.get('title') or p.get('text')):
        head = (f'<div class="ph rv" style="color:{ink}">' + ('<h2 class="h56">%s</h2>' % e(p['title']) if p.get('title') else '')
                + ('<p>%s</p>' % e(p['text']) if p.get('text') else '') + '</div>')
    cards = ''
    for i in items:
        rows = ''.join(f'<li>{CHECK}<span>{e(r)}</span></li>' for r in i.get('rows') or [])
        rows = f'<div class="dv"></div><ul class="inc">{rows}</ul>' if rows else ''
        per = f'<p class="pn">{e(i["per"])}</p>' if i.get('per') else ''
        cards += (f'<article class="pc{" mk" if i.get("marked") else ""}"><div class="bar">{DOTS}</div><div class="pbd">'
                  f'<h3 class="pt">{e(i["name"])}</h3>' + ('<p class="pl2">%s</p>' % e(i['line']) if i.get('line') else '') + '<div class="dv"></div>'
                  f'<div class="pp"><strong class="pv">{e(i.get("price"))}</strong>{per}{btn(i.get("cta"), "pri" if i.get("marked") else "sec")}</div>{rows}</div></article>')
    cards = f'<div class="cards rv">{cards}</div>' if cards else ''
    note = f'<p class="pnote">{e(p["note"])}</p>' if items and p.get('note') else ''
    return f'''<section class="pr{' hassky' if skyh else ''}{' hasterm' if term else ''}{'' if items else ' solo'}" id="pr">{skyh}{head}{cards}{term}{note}</section>'''


def s_faq(d, c):
    f = d.get('faq') or {}
    items = [i for i in f.get('items') or [] if i.get('q') and i.get('a')]
    if not items:
        return ''
    head = f'<h2 class="h56 rv">{e(f["title"])}</h2>' if f.get('title') else ''
    qs = ''
    for n, i in enumerate(items):
        qs += (f'<div class="q{" open" if n == 0 else ""}"><h3><button type="button" class="qb" aria-expanded="{"true" if n == 0 else "false"}" aria-controls="fa{n}">'
               f'<span>{e(i["q"])}</span>{PLUS}</button></h3><div class="aw" id="fa{n}"><div class="ac"><p>{e(i["a"])}</p></div></div></div>')
    return f'''<div class="stroke" aria-hidden="true"></div><section class="faq" id="faq">{head}<div class="ql rv">{qs}</div></section>'''


def s_foot(d, c):
    b = d.get('brand') or {}
    ft = d.get('foot') or {}
    col = lambda xs: ('<div class="fcol">' + ''.join(f'<a href="{e(x.get("h"))}">{e(x.get("t"))}</a>' for x in xs if x.get('t')) + '</div>') if [x for x in xs if x.get('t')] else ''
    extra = [x for x in (d.get('signin'), d.get('cta')) if x and x.get('t')]
    cols = col(d.get('nav') or []) + col(d.get('links') or []) + col(extra)
    if ft.get('text'):
        cols += f'<div class="fcol"><p>{e(ft["text"])}</p></div>'
    name = b.get('name') or ''
    legal = ' · '.join([e(ft['legal'])] if ft.get('legal') else [])
    links = ''.join(f'<a href="{e(x.get("h"))}">{e(x.get("t"))}</a>' for x in ft.get('links') or [] if x.get('t'))
    return f'''<footer class="foot">{f'<nav class="fl" aria-label="Footer">{cols}</nav>' if cols else ''}
{f'<div class="mark rv" aria-hidden="true" style="--ms:{min(30, 128 / max(len(name), 1)):.2f}vw">{e(name)}</div>' if name else ''}
{f'<p class="fcopy"><span>{legal}</span>{links}</p>' if legal or links else ''}</footer>'''


# ---------- the page ----------
CSS = r'''
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--g);color:var(--i);font:400 16px/1.5 "FONT",ui-sans-serif,system-ui,sans-serif;letter-spacing:-.03em;-webkit-font-smoothing:antialiased;overflow-x:clip}
img,video{display:block;max-width:100%;height:auto}h1,h2,h3,p,figure,ul{margin:0}ul{padding:0;list-style:none}a{color:inherit;text-decoration:none}
button{font:inherit;color:inherit;letter-spacing:inherit;background:none;border:0;padding:0;cursor:pointer}
:focus-visible{outline:2px solid var(--lk);outline-offset:3px;border-radius:4px}
:root{--u:min(1px,calc(100vw/1440))}
.h56{font-weight:500;font-size:56px;line-height:1.2;letter-spacing:-.03em;text-wrap:balance}
.dots{display:flex;gap:5px;flex:none}.dots i{width:12px;height:12px;border-radius:50%;box-shadow:inset 0 0 0 .5px rgba(0,0,0,.22)}
.dots i:nth-child(1){background:#ff5f57}.dots i:nth-child(2){background:#febc2e}.dots i:nth-child(3){background:#28c840}
.bar{position:relative;display:flex;align-items:center;height:20px;padding:0 4px 8px}
.bt{position:absolute;left:50%;top:-1px;transform:translateX(-50%);max-width:calc(100% - 110px);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:12px;line-height:18px;color:var(--btc)}
.cap{font-size:12px;line-height:18px;color:var(--mu2);text-align:center;text-wrap:balance}
.win .cap{max-width:100%;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bd{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
/* buttons: a glossy pill, 40 high; the first in the accent's tints, the second in window grey */
.btn{position:relative;display:inline-flex;align-items:center;justify-content:center;height:40px;padding:0 20px 1px;border-radius:999px;border:1px solid var(--sbd);background:linear-gradient(var(--s1),var(--s2) 42%,var(--s3));color:var(--i);box-shadow:0 10px 24px rgba(0,0,0,.12);font-size:18px;line-height:27px;font-weight:500;white-space:nowrap;overflow:hidden;transition:transform .12s ease,opacity .15s ease}
.btn::before{content:"";position:absolute;left:13px;right:13px;top:3px;height:12px;border-radius:999px;background:linear-gradient(var(--gl),transparent);pointer-events:none}
.btn span{position:relative}.btn.pri{border-color:var(--pbd);background:linear-gradient(var(--p1),var(--p2) 50%,var(--p3) 80%,var(--p2));color:var(--pon)}.btn.pri::before{background:linear-gradient(rgba(255,255,255,.8),transparent)}
.btn:hover{opacity:.8}.btn:active{transform:scale(.97)}.btn.mono{font-family:"MONO",ui-monospace,monospace;letter-spacing:-.03em}
/* menu bar */
.mb{position:sticky;top:0;z-index:200;background:var(--g);border-bottom:1px solid var(--ln);padding:0 24px}
.mr{display:flex;align-items:center;gap:20px;height:52px}.ml{flex:1;display:flex;align-items:center;gap:16px;min-width:0}
.ml a,.msi{font-size:14px;line-height:14px;color:var(--mu);white-space:nowrap;transition:transform .12s ease}.ml a:hover,.msi:hover{color:var(--i)}.ml a:active,.msi:active,.mct:active{transform:scale(.97)}.ml .mbn{color:var(--i);font-weight:500}
.mlg{flex:none;display:block}.mlg img{height:30px;width:auto;transform-origin:50% 100%;animation:squish 7s ease infinite}.mlg.word img{height:20px}
@keyframes squish{0%,60%,62.5%,65.14%,67.64%,100%{transform:none}61.05%,66.19%{transform:scaleY(.95) scaleX(1.011)}}
.mrr{flex:1;display:flex;justify-content:flex-end;align-items:center;gap:16px}.mct{font-size:14px;line-height:21px;font-weight:500;color:var(--lk);white-space:nowrap;transition:transform .12s ease,opacity .15s ease}.mct:hover{opacity:.8}
.mtg{display:none;width:32px;height:32px;flex-direction:column;align-items:center;justify-content:center;gap:5px}.mtg i{display:block;width:20px;height:7px;border-radius:999px;border:1.5px solid currentColor}
.mcc{position:fixed;inset:53px 0 0 0;z-index:190;background:var(--g);padding:26px 20px 28px;display:grid;grid-template-columns:1fr 1fr;gap:6px 4px;align-content:start;overflow:auto}.mcc[hidden]{display:none}
.mcc a{display:flex;align-items:center;justify-content:center;min-height:84px;padding:8px;border-radius:24px;border:1px solid var(--ln3);background:var(--card);font-weight:500;text-align:center}
/* the opening: dotted ground, small windows round the headline, one large frame */
.hero{position:relative;padding-bottom:59px;background-image:radial-gradient(var(--dot) 1px,transparent 1.3px);background-size:34.24px 34px}
.wins{position:absolute;inset:0;overflow:clip}
@keyframes hin{from{opacity:0;translate:0 8px}to{opacity:1;translate:0 0}}
.win{position:absolute;display:flex;flex-direction:column;align-items:center;gap:6px;width:calc(var(--u)*var(--w));touch-action:none;user-select:none;animation:hin .45s ease-out both;animation-delay:calc(var(--n)*16ms + .11s)}
.win .fr,.fig,.note{border:1px solid var(--edge2);border-radius:8px;background:linear-gradient(90deg,var(--clo),var(--chi) 50%,var(--clo))}
.win .fr{width:100%;padding:8px 4px 4px;filter:drop-shadow(0 10px 12px rgba(0,0,0,.12));transition:transform .12s ease;cursor:grab}.win.held .fr{transform:scale(.97);cursor:grabbing}
.scr{border-radius:4px;overflow:hidden;background:var(--clo)}.scr img{width:100%}
.head{position:relative;z-index:2;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:32px;min-height:526px;padding:200px 20px 32px;text-align:center;pointer-events:none;animation:hin .45s ease-out .05s both}.head>*{pointer-events:auto}
.hg{display:flex;flex-direction:column;align-items:center;gap:8px;max-width:calc(var(--u)*640)}
h1{font-weight:500;font-size:calc(var(--u)*var(--fs));line-height:1.1;letter-spacing:-.03em;text-wrap:balance}
.sub{font-size:20px;line-height:30px;text-wrap:balance}.sub2{max-width:520px;color:var(--mu);text-wrap:pretty}
.btns{display:flex;flex-wrap:wrap;justify-content:center;align-items:flex-start;gap:16px}.bc{display:flex;flex-direction:column;align-items:center;gap:8px}.bsub{font-size:12px;line-height:18px;color:var(--mu2)}
.big{position:relative;z-index:2;display:flex;flex-direction:column;align-items:center;gap:6px;width:min(100% - 40px,var(--bw)*1px);margin:0 auto;animation:hin .45s ease-out both}
.big .fr{width:100%;border-radius:16px;border:1px solid var(--edge);overflow:hidden;background:var(--clo);box-shadow:0 10px 24px rgba(0,0,0,.12)}.big .fr>*{width:100%}.big video{cursor:pointer}
/* feature rows: wave, a request bubble that is typed, the answer; a window on the wallpaper */
.feat{padding:0 0 128px}.feat.hashead{padding-top:69px}
.sh,.ph{display:flex;flex-direction:column;align-items:center;gap:12px;text-align:center;padding:0 20px}.sh{margin-bottom:64px}.sh p,.ph p,.fsub{max-width:720px;font-size:20px;line-height:30px;text-wrap:pretty}
.rows{display:flex;flex-direction:column;align-items:center;gap:48px;padding:0 64px}
.row{position:relative;display:flex;align-items:center;gap:64px;width:min(1090px,100%);min-height:474px;transform-origin:50% 50%;transition:opacity .35s,transform .4s cubic-bezier(.22,1,.36,1)}.row.r{flex-direction:row-reverse}
.js .row.dim{opacity:.3;transform:scale(.8)}
.txt{position:relative;z-index:1;flex:0 0 336px;align-self:stretch;display:flex;flex-direction:column;padding:16px 16px 16px 32px}.row.r .txt{padding:16px 32px 16px 16px}
.wave{display:flex;justify-content:center;height:86px}.row.r .wave{justify-content:flex-end}
.wb{display:flex;align-items:center;gap:10px;height:28px;-webkit-mask-image:linear-gradient(90deg,transparent,#000 22%,#000 78%,transparent);mask-image:linear-gradient(90deg,transparent,#000 22%,#000 78%,transparent)}
.wb i{display:block;width:8px;height:var(--h);border-radius:24px;background:var(--i);transition:background .3s ease}.row.silent .wb i{background:var(--wq)}
.mid{flex:1;display:flex;flex-direction:column;justify-content:center;min-height:214px}.convo{display:flex;flex-direction:column;align-items:flex-start;gap:24px}.row.r .convo{align-items:flex-end}
.bub{position:relative;display:inline-flex;align-items:center;min-height:53px;max-width:296px;padding:12px 20px;border-radius:25.5px;border:1px solid var(--bb);font-size:24px;line-height:28.8px;box-shadow:0 10px 24px rgba(0,0,0,.12)}
.bub::before{content:"";position:absolute;left:16px;right:16px;top:3px;height:12px;border-radius:999px;background:linear-gradient(rgba(255,255,255,.8),transparent);pointer-events:none}
.bub.req{--bb:var(--pbd);--bt:var(--p2);background:linear-gradient(var(--p1),var(--p2) 50%,var(--p3) 80%,var(--p2));color:var(--pon);transition:opacity .22s ease,transform .3s ease}
.bub.rep{--bb:var(--sbd);background:linear-gradient(var(--s1),var(--s2) 42%,var(--s3));color:var(--i);transition:opacity .3s ease,transform .35s cubic-bezier(.22,1,.36,1),visibility 0s}.bub.rep::before{background:linear-gradient(var(--gl),transparent)}.bub.rep:hover{opacity:.8}.bub.rep:active{transform:scale(.97)}
.js .row:not(.ans) .rep{opacity:0;transform:translateY(6px);visibility:hidden}
.tail{position:absolute;right:6px;bottom:-11px;overflow:visible}.tx{position:relative;min-height:28.8px;overflow-wrap:anywhere}
.tx.typing::after,.caret{content:"";display:inline-block;width:1px;height:1em;margin-left:2px;vertical-align:-.12em;background:currentColor;animation:blink 1s step-end infinite}
@keyframes blink{50%{opacity:0}}
.copy{display:flex;flex-direction:column;gap:8px}.row.r .copy{align-items:flex-end;text-align:right}.copy h3{font-size:20px;line-height:30px;font-weight:500}.copy p{color:var(--mu)}
.shot{flex:1;display:flex;align-items:center;justify-content:center;min-width:0;padding:8px 9px;--mh:422px}
.desk{position:absolute;inset:0;border-radius:16px;border:1px solid var(--edge);overflow:hidden;background:var(--card);box-shadow:0 8px 19.2px rgba(0,0,0,.12)}
.desk::after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,var(--veil) 0,var(--veil) 400px,var(--veil0) 560px)}.row.r .desk::after{background:linear-gradient(270deg,var(--veil) 0,var(--veil) 400px,var(--veil0) 560px)}
.fig{position:relative;z-index:1;width:min(100%,var(--mh)*var(--r) + 10px);padding:8px 4px 4px;border-color:var(--edge);filter:drop-shadow(0 10px 12px rgba(0,0,0,.12))}
/* the notes window on its band */
.dream{position:relative;padding:113px 20px 100px}.band{position:absolute;left:0;right:0;top:120px;height:511px;overflow:hidden}
.band .bd{opacity:.42}
.band::after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,var(--g) 0,var(--g0) 150px,var(--g0) calc(100% - 150px),var(--g) 100%),linear-gradient(var(--g) 0,var(--g0) 28%,var(--g0) 72%,var(--g) 100%)}
.note{position:relative;width:min(480px,100%);margin:0 auto;overflow:hidden;background:linear-gradient(90deg,var(--at),var(--at)),linear-gradient(90deg,var(--clo),var(--chi) 50%,var(--clo));box-shadow:0 10px 24px rgba(0,0,0,.12)}
.tb{position:relative;display:flex;height:30px;padding:10px}.tb .dots i{width:10px;height:10px}.tb .bt{top:6px}
.doc{display:flex;flex-direction:column;gap:10px;min-height:340px;padding:20px 24px;background:var(--card)}.np{font-weight:400;font-size:20px;line-height:30px;color:var(--mu)}
.ink{color:var(--i);background:var(--ah);border-radius:2px;padding:1px 2px;-webkit-box-decoration-break:clone;box-decoration-break:clone}
.sign{display:flex;align-items:center;gap:12px;margin-top:auto;padding-top:24px}.sign img{height:32px;width:auto}
.stroke{width:min(1090px,100% - 40px);height:16px;margin:0 auto;background:linear-gradient(90deg,var(--ln3) 50%,transparent 0) 0 0/4px 2px repeat-x}
/* the wall of small windows */
.fb{display:flex;flex-direction:column;align-items:center;gap:64px;padding:104px 20px}
.mq{width:100vw;margin:0 -20px;overflow:hidden;font-weight:500;font-size:56px;line-height:1.2;letter-spacing:-.03em;-webkit-mask-image:linear-gradient(90deg,transparent,#000 14%,#000 86%,transparent);mask-image:linear-gradient(90deg,transparent,#000 14%,#000 86%,transparent)}
.mqt{display:flex;justify-content:center;gap:24px;white-space:nowrap;will-change:transform}.mqt span{flex:none;color:var(--gh)}.mqt .on{color:var(--i)}
.fsub{margin-top:-40px;text-align:center}
.wall{width:min(1090px,100%);columns:var(--n);column-gap:16px}
.fc{display:block;break-inside:avoid;margin:0 0 16px;border-radius:8px;overflow:clip;background:var(--card);box-shadow:0 4px 12px rgba(0,0,0,.08)}
.fbar{display:flex;align-items:center;height:32px;padding:10px;background:linear-gradient(90deg,var(--hue),var(--hue)),linear-gradient(90deg,var(--clo),var(--chi) 50%,var(--clo))}
.fbd{display:flex;flex-direction:column;gap:16px;padding:16px}.fbd h3{font-weight:400;font-size:14px;line-height:1.2}.fbd p{font-weight:300;font-size:16px;line-height:24px}.fv{font-weight:500;font-size:28px;line-height:28px}
.ban{width:min(1090px,100%);margin-top:-32px;padding:4px;border-radius:8px;border:1px solid var(--ln2);background:linear-gradient(var(--gs),var(--gs));box-shadow:0 10px 24px rgba(0,0,0,.12),inset 0 1px 1px var(--hl);-webkit-backdrop-filter:blur(12px) saturate(1.4);backdrop-filter:blur(12px) saturate(1.4)}
.ban p{padding:16px;text-align:center;font-size:20px;line-height:30px;font-weight:500}.ban a{color:var(--lk);display:inline-block;transition:transform .12s ease,opacity .15s ease}.ban a:hover{opacity:.8}.ban a:active{transform:scale(.97)}
/* plans on the sky, and the terminal window */
.pr{position:relative;display:flex;flex-direction:column;align-items:center;padding:140px 20px 0}.pr.solo{padding-top:0}
.sky{position:absolute;inset:0 0 0 0;border-radius:16px;overflow:hidden;background:var(--g)}.pr.hasterm .sky{bottom:112px}
.sky .bd{height:min(100%,max(100vw/var(--sr),760px));object-position:50% 0;-webkit-mask-image:linear-gradient(#000 40%,transparent);mask-image:linear-gradient(#000 40%,transparent)}
.sky::after{content:"";position:absolute;inset:0;background:linear-gradient(var(--sv) 0,var(--sv) 380px,var(--sv0) 640px)}
.ph{position:relative;margin-bottom:96px}
.cards{position:relative;display:flex;justify-content:center;align-items:stretch;gap:16px;width:min(1082px,100%)}
.pc{position:relative;flex:0 1 350px;display:flex;flex-direction:column;padding:8px 4px 4px;border-radius:8px;background:linear-gradient(var(--gs),var(--gs));box-shadow:0 10px 24px rgba(0,0,0,.12),inset 0 1px 1px var(--hl),inset 0 0 0 1px var(--hl2);-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px)}
.pc.mk{background:linear-gradient(var(--a6),var(--a0) 40%),linear-gradient(var(--gs),var(--gs))}
.pbd{flex:1;border-radius:4px;background:linear-gradient(var(--card) 25%,var(--cardt) 100%);text-align:center}
.pt{padding:24px 24px 16px;font-size:28px;line-height:28px;font-weight:500}.pl2{padding:0 24px 16px;font-size:20px;line-height:1.2;text-wrap:balance}
.dv{height:16px;margin:0 20px;background:linear-gradient(90deg,var(--ln3) 50%,transparent 0) 0 50%/4px 1px repeat-x}
.pp{display:flex;flex-direction:column;align-items:center;gap:16px;padding:24px}.pv{font-weight:500;font-size:56px;line-height:56px;letter-spacing:-.03em}.pn{margin-top:-4px;font-size:14px;line-height:1.2}
.inc{display:flex;flex-direction:column;gap:16px;padding:16px 24px 24px;text-align:left;--ck:var(--card)}.inc li{display:flex;gap:12px;font-size:16px;line-height:1.3;font-weight:500}.inc svg{flex:none;margin-top:2px}
.term{position:relative;width:min(1082px,100%);margin-top:17px;padding:0 4px 4px;border-radius:8px;background:var(--term);color:var(--ton);box-shadow:0 10px 24px rgba(0,0,0,.12);font-family:"MONO",ui-monospace,monospace}.pr.solo .term{margin-top:0}
.term .bar{height:26px;padding:8px}.term .dots i{width:10px;height:10px}
.tp{display:flex;align-items:center;gap:24px;padding:20px}.tc{flex:1;display:flex;flex-direction:column;gap:4px;min-width:0}.tc h2{font-size:20px;line-height:30px;font-weight:500}.tc p{max-width:480px;color:var(--tmu)}
.blk{display:inline-block;width:.55em;height:1em;margin-left:.35em;vertical-align:-.14em;background:currentColor;animation:blink 1s step-end infinite}
.pnote{position:relative;width:min(1082px,100%);margin-top:12px;font-size:12px;line-height:1.5;color:var(--mu2);text-align:center}
.pr.hasterm{padding-bottom:0}.pr:not(.hasterm).hassky{padding-bottom:104px}
/* questions */
.faq{display:flex;flex-direction:column;align-items:center;padding:144px 20px 40px;text-align:center}.pr+.faq,.pr+.stroke{margin-top:16px}
.ql{display:flex;flex-direction:column;gap:8px;width:min(834px,100%);margin-top:64px;text-align:left}
.q{padding:20px;border-radius:8px;background:var(--card);cursor:pointer}.q h3{font:inherit}
.qb{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;width:100%;text-align:left;font-size:20px;line-height:1.2;font-weight:500}.pl{flex:none;transition:transform .2s ease}.q.open .pl{transform:rotate(45deg)}
.aw{display:grid;grid-template-rows:1fr;transition:grid-template-rows .2s ease,visibility 0s}.ac{overflow:hidden}.ac p{max-width:480px;padding-top:8px;color:var(--mu)}
.js .q:not(.open) .aw{grid-template-rows:0fr;visibility:hidden;transition:grid-template-rows .2s ease,visibility 0s .2s}
/* foot */
.foot{padding:144px 20px 18px;overflow:clip}.fl{display:flex;gap:31px;width:min(1090px,100%);margin:0 auto}.fcol{flex:0 1 249px;display:flex;flex-direction:column;align-items:flex-start;gap:12px;min-width:0}
.fcol a,.fcol p{color:var(--mu)}.fcol a{transition:transform .12s ease}.fcol a:hover{color:var(--i)}.fcol a:active{transform:scale(.97)}
.mark{margin:24px auto 0;text-align:center;font-family:"BLOCK",ui-monospace,monospace;font-weight:700;font-size:min(var(--ms),300px);line-height:1;letter-spacing:0;white-space:nowrap;color:var(--mk)}
.fcopy{display:flex;flex-wrap:wrap;justify-content:center;gap:4px 16px;margin-top:24px;font-size:12px;line-height:16px;letter-spacing:-.02em;color:var(--mu2)}.fcopy a:hover{color:var(--i)}
/* arrival: 22px up, from .965, .55s / .7s */
.js .rv{opacity:0;translate:0 22px;scale:.965}.js .rv.in{opacity:1;translate:0 0;scale:1;transition:opacity .55s ease,scale .7s cubic-bezier(.2,.7,.25,1),translate .7s cubic-bezier(.2,.7,.25,1)}
.js .mark.rv{translate:none;scale:.82}.js .mark.rv.in{transition:scale .62s cubic-bezier(.2,.9,.25,1),opacity .5s ease}
@media (max-width:1023px){
.mb{padding:0 20px}.mr{gap:12px}.ml,.msi{display:none}.mlg img{height:28px}.mlg.word img{height:18px}.mtg{display:flex}.mlg{order:-1}.mrr{min-width:0}.mct{min-width:0;overflow:hidden;text-overflow:ellipsis}
.wins{display:none}.head{min-height:0;padding:84px 20px 0;gap:31px}.hg{max-width:none}h1{font-size:calc(var(--fm)*1px)}.sub{font-size:18px;line-height:27px}
.btns{flex-direction:column;align-items:center}.big{margin-top:12px}.hero{padding-bottom:22px}.h56,.mq{font-size:36px}.sh p,.ph p,.fsub{font-size:17px;line-height:1.5}
.feat,.feat.hashead{padding:40px 0 0}.sh{margin-bottom:0}.rows{align-items:stretch;gap:0;padding:0}
.row,.row.r{flex-direction:column;align-items:stretch;gap:0;width:100%;min-height:0;padding:0 20px 40px;transition:opacity .35s,transform .35s}.rows .row:first-child{padding-top:40px}
.row+.row{background:linear-gradient(90deg,var(--ln3) 50%,transparent 0) 20px 0/4px 2px repeat-x;background-size:4px 2px;background-clip:content-box}
.js .row.dim{opacity:1;transform:none}
.txt,.row.r .txt{display:contents}.copy,.row.r .copy{order:1;align-items:flex-start;text-align:left;padding:16px 0 40px}.copy h3{font-size:24px;line-height:31.2px}
.shot{order:2;position:relative;flex:none;padding:6px;--mh:300px}.desk{border-radius:12px}.desk::after,.row.r .desk::after{display:none}.fig{padding:6px 3px 3px;border-radius:6px}
.wave,.row.r .wave{order:3;height:auto;margin:40px 0;justify-content:center}.mid{order:4;min-height:0}.convo,.row.r .convo{align-items:stretch}.bub{font-size:20px;line-height:1.35;min-height:46px;padding:11px 17px}.bub.req{align-self:flex-end;max-width:90%}.bub.rep{align-self:flex-start;max-width:90%}
.dream{padding:40px 20px}.band{top:60px;height:420px}.doc{padding:20px;gap:12px;min-height:0}.np{font-size:17px;line-height:24.65px}
.fb{padding:40px 20px;gap:36px}.mqt{gap:16px}.fsub{margin-top:-16px}.wall{columns:1}.ban{margin-top:0}.ban p{font-size:18px;line-height:27px;padding:20px 16px}.fbd p{font-size:15px;line-height:22.5px}
.pr{padding:64px 20px 0}.ph{margin-bottom:40px}.cards{flex-direction:column;align-items:center;gap:20px}.pc{flex:none;width:100%;max-width:400px}.pv{font-size:44px;line-height:44px}
.tp{flex-direction:column;align-items:flex-start;gap:14px;padding:12px}.term .btn{max-width:100%;white-space:normal;height:auto;min-height:40px;line-height:1.2;padding:8px 20px}.pr.hasterm .sky{bottom:160px}
.faq{padding:96px 20px 40px}.ql{margin-top:40px}.q{padding:18px}.qb{font-size:18px}.ac p{font-size:15px;line-height:22.5px}
.foot{padding:40px 20px 24px}.fl{display:grid;grid-template-columns:1fr 1fr;gap:32px 24px}.fcol{gap:10px}.mark{margin-top:28px}}
@media (max-width:1023px) and (min-width:640px){.rows,.dream,.fb,.pr,.faq{padding-left:max(20px,50% - 300px);padding-right:max(20px,50% - 300px)}.rows{padding-left:0;padding-right:0}.row,.row.r{padding-left:max(20px,50% - 300px);padding-right:max(20px,50% - 300px)}.mq{margin:0 calc(50% - 50vw)}}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;scroll-behavior:auto!important}.js .row.dim{transform:none}.rv,.js .rv{opacity:1;translate:none;scale:none;transition:none}.btn,.win .fr,.bub,.pl,.aw{transition:none!important}}
'''

JS = r'''
(()=>{const D=document,R=D.documentElement,$=(s,r=D)=>r.querySelector(s),$$=(s,r=D)=>[...r.querySelectorAll(s)];
const still=matchMedia('(prefers-reduced-motion:reduce)').matches;R.classList.add('js');
/* arrival */
const rv=$$('.rv');if('IntersectionObserver' in window&&!still){const io=new IntersectionObserver(es=>es.forEach(x=>{if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target)}}),{threshold:.08,rootMargin:'0px 0px -6% 0px'});rv.forEach(x=>io.observe(x))}else rv.forEach(x=>x.classList.add('in'));
/* small windows: picked up (.97), carried, left where they are dropped */
let zi=10;$$('.win').forEach(w=>{let sx=0,sy=0,ox=0,oy=0,on=false;
 w.addEventListener('pointerdown',ev=>{if(ev.button)return;on=true;sx=ev.clientX-ox;sy=ev.clientY-oy;w.classList.add('held');w.style.zIndex=++zi;w.setPointerCapture(ev.pointerId)});
 w.addEventListener('pointermove',ev=>{if(!on)return;ox=ev.clientX-sx;oy=ev.clientY-sy;w.style.transform=`translate(${ox}px,${oy}px)`});
 const end=()=>{on=false;w.classList.remove('held')};w.addEventListener('pointerup',end);w.addEventListener('pointercancel',end)});
/* film */
$$('video[data-auto]').forEach(v=>{if(!still){v.autoplay=true;v.play().catch(()=>{})}const tog=()=>{v.paused?v.play().catch(()=>{}):v.pause()};v.addEventListener('click',tog);v.addEventListener('keydown',ev=>{if(ev.key===' '||ev.key==='Enter'){ev.preventDefault();tog()}})});
/* menu on the phone */
const tg=$('.mtg'),mc=$('#mcc');if(tg&&mc){const set=o=>{tg.setAttribute('aria-expanded',o);mc.hidden=!o};tg.addEventListener('click',()=>set(tg.getAttribute('aria-expanded')!=='true'));mc.addEventListener('click',ev=>{if(ev.target.closest('a'))set(false)});D.addEventListener('keydown',ev=>{if(ev.key==='Escape')set(false)});matchMedia('(min-width:1024px)').addEventListener('change',()=>set(false))}
/* feature rows: the one nearest the middle of the window speaks, the others step back */
const rows=$$('.row');let act=null;const tm=new Map();
const stop=r=>{(tm.get(r)||[]).forEach(clearInterval);tm.set(r,[]);const tx=$('.tx',r);if(tx){tx.textContent=tx.dataset.t;tx.classList.remove('typing')}};
const speak=r=>{const tx=$('.tx',r),bars=$$('.wb i',r),ids=[];tm.set(r,ids);r.classList.remove('silent','ans');
 const done=()=>{ids.push(setTimeout(()=>{r.classList.add('silent');clearInterval(wv)},500));ids.push(setTimeout(()=>{r.classList.add('ans');tx&&tx.classList.remove('typing')},950))};
 const wv=setInterval(()=>bars.forEach(b=>b.style.setProperty('--h',(8+Math.random()*Math.random()*20).toFixed(0)+'px')),110);ids.push(wv);
 if(!tx){done();return}const t=tx.dataset.t;let n=0;tx.textContent='';tx.classList.add('typing');const ty=setInterval(()=>{n++;tx.textContent=t.slice(0,n);if(n>=t.length){clearInterval(ty);done()}},33);ids.push(ty)};
rows.forEach(r=>{const tx=$('.tx',r);if(tx)tx.dataset.t=tx.textContent;if(still)r.classList.add('ans','silent')});
const focus=()=>{if(!rows.length)return;const vh=innerHeight,a=rows[0].getBoundingClientRect(),z=rows[rows.length-1].getBoundingClientRect();let best=null,bd=1e9;
 if(a.top<vh*.62&&z.bottom>vh*.2)rows.forEach(r=>{const q=r.getBoundingClientRect(),dd=Math.abs(q.top+q.height/2-vh/2);if(dd<bd){bd=dd;best=r}});
 if(best===act)return;if(act&&!still){stop(act);act.classList.add('ans','silent')}act=best;rows.forEach(r=>r.classList.toggle('dim',!!best&&r!==best&&rows.length>1));if(best&&!still)speak(best)};
/* the running headline follows the scroll */
const mq=$('.mqt');const run=()=>{if(!mq||still)return;const q=mq.parentNode.getBoundingClientRect();if(q.bottom<-100||q.top>innerHeight+100)return;mq.style.transform=`translateX(${((q.top+q.height/2-innerHeight*.1)*.16).toFixed(1)}px)`};
/* questions: one open at a time */
const qs=$$('.q');qs.forEach(q=>q.addEventListener('click',ev=>{if(ev.target.closest('a'))return;const o=!q.classList.contains('open');qs.forEach(x=>{x.classList.toggle('open',x===q&&o);$('.qb',x).setAttribute('aria-expanded',x===q&&o)})}));
let tick=false;const on=()=>{if(tick)return;tick=true;requestAnimationFrame(()=>{tick=false;focus();run()})};addEventListener('scroll',on,{passive:true});addEventListener('resize',on);focus();run();
})();
'''


def render(d: dict) -> str:
    c = colours(d.get('palette') or {})
    b = d.get('brand') or {}
    hero = d.get('hero') or {}
    G, I, A, dk = c['G'], c['I'], c['A'], c['dark']
    v = (f'--g:{G};--g0:{rgba(G, 0)};--i:{I};--a:{A};--card:{c["card"]};--cardt:{rgba(c["card"], .8)};--clo:{c["clo"]};--chi:{c["chi"]};'
         f'--mu:{c["mu"]};--mu2:{c["mu2"]};--lk:{c["link"]};--p1:{c["p1"]};--p2:{c["p2"]};--p3:{c["p3"]};--pon:{c["pon"]};--pbd:{c["pbd"]};'
         f'--s1:{c["s1"]};--s2:{c["s2"]};--s3:{c["s3"]};--sbd:{c["sbd"]};--edge:{c["edge"]};--edge2:{rgba(I, .22 if dk else .3)};'
         f'--ln:{rgba(I, .08 if dk else .05)};--ln2:{rgba(I, .12 if dk else .08)};--ln3:{rgba(I, .28)};--dot:{rgba(I, .16 if dk else .13)};'
         f'--gl:{rgba("#ffffff", .16 if dk else .8)};--hl:{rgba("#ffffff", .14 if dk else .8)};--hl2:{rgba("#ffffff", .08 if dk else .25)};'
         f'--gs:{rgba(c["card"], .5 if dk else .3)};--gh:{mix(I, G, .6)};--wq:{mix(I, G, .72)};--veil:{rgba(G, .96)};--veil0:{rgba(G, 0)};'
         f'--at:{rgba(A, .2)};--ah:{rgba(A, .35)};--a6:{rgba(A, .6)};--a0:{rgba(A, 0)};--term:{rgba(c["term"], .96)};--btc:{c["btc"]};--ton:{c["ton"]};--tmu:{c["tmu"]};--mk:{c["mark"]}')
    body = ''.join(f(d, c) for f in (s_menubar, s_hero, s_steps, s_statement, s_wall, s_plans, s_faq, s_foot))
    title = ' — '.join(x for x in (b.get('name'), hero.get('title')) if x)
    fams = (f'family={FONT}:wght@300;400;500&family={MONO.replace(" ", "+")}:wght@400;500&family={BLOCK.replace(" ", "+")}:wght@700')
    css = CSS.replace('FONT', FONT).replace('MONO', MONO).replace('BLOCK', BLOCK)
    return f'''<!doctype html><html lang="{e(d.get("lang") or "en")}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(hero.get("text"))}"><meta name="theme-color" content="{G}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?{fams}&display=swap" rel="stylesheet">
<style>:root{{{v}}}{css}</style></head><body>
{body}
<script>{JS}</script></body></html>'''
