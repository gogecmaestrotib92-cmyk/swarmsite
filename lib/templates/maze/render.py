"""maze/render.py — one pure function: render(d) -> a complete page built to the measures of the reference home page
(36 x 40px column field at 1440, light-weight grotesque set very large and tight, rounded cards on a quiet ground, one
bright band, a pinned opening that turns its tiles into a pixel disc). No client, no model call, no network at render."""
import html, json, colorsys

M = '../../'
FONT = 'Inter Tight'            # open-licence stand-in for the reference's commercial light grotesque


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


def colours(p):
    G, I, A = p.get('ground', '#f5f3ef'), p.get('ink', '#1c1c1c'), p.get('accent', '#d9f56b')
    dark = lum(G) < .2
    card = mix(G, I, .07) if dark else mix(G, '#ffffff', .7)
    chip = mix(G, I, .1)
    line = mix(G, I, .2)
    muted = I
    for t in (.5, .45, .4, .35, .3, .25, .2, .15, .1):          # the quiet grey of the reference, kept readable
        m = mix(I, G, t)
        if min(con(m, G), con(m, card), con(m, chip)) >= 4.6:
            muted = m
            break
    tone = A                                                     # accent that carries ink text (the disc)
    for t in (0, .15, .3, .4, .5, .6, .7, .8):
        tone = mix(A, G, t)
        if con(tone, I) >= 4.6:
            break
    onA = best(A, I, G)
    if con(A, onA) < 4.6:                                        # a mid-tone accent carries neither colour: it is taken away
        away = '#000000' if lum(onA) > lum(A) else '#ffffff'     # from its text until the text reads 4.6:1 (band, marked price)
        A = next((x for x in (mix(A, away, t / 20) for t in range(1, 21)) if con(x, onA) >= 4.6), away)
    soft = mix(A, card, .8)
    deep, on_deep = (tone, I) if dark else (I, G)
    hov = mix(I, G, .18)
    tabs = []
    for x in (p.get('extra') or []) + [tone]:
        on = best(x, I, G)
        if con(x, on) >= 4.5 and x.lower() not in [t[0].lower() for t in tabs]:
            tabs.append((x, on))
    return dict(G=G, I=I, A=A, card=card, chip=chip, line=line, muted=muted, tone=tone, onA=onA, soft=soft, deep=deep,
                on_deep=on_deep, hov=hov, tabs=tabs, dark=dark)


def fl(lo, hi):
    """fluid size between the two measured widths (390 and 1440)"""
    s = (hi - lo) / 10.5
    return f'clamp({lo}px,{lo - s * 3.9:.2f}px + {s:.3f}vw,{hi}px)'


def step(text, sizes):
    n = len(text or '')
    for lim, v in sizes:
        if n <= lim:
            return v
    return sizes[-1][1]


def made(d, kind):
    """pictures made for the client, by kind (CONTRACT.md "Made pictures"); a list, empty when the kind is absent"""
    m = ((d.get('media') or {}).get('made') or {}).get(kind) or []
    return [x for x in (m if isinstance(m, list) else [m]) if x.get('src')]


def _hue(h):
    r, g, b = (v / 255 for v in _rgb(h))
    return colorsys.rgb_to_hsv(r, g, b)[0] * 360


def calm(blurs, c, n):
    """the quiet ones of the client's blurs for the plan panels: never a light picture on a dark page; of the rest, the
    n with the least colour in them and nearest the accent's hue (a vivid red or orange panel is not taken), in their
    own order. The reference has one single-colour picture per plan, so several hues are its own device."""
    ok = [m for m in blurs if not (c['dark'] and m.get('tone') == 'light')]
    def score(m):
        try:
            rgb = _rgb(m.get('mean') or '')
            dh = abs(_hue(m['mean']) - _hue(c['A'])) % 360
            return (max(rgb) - min(rgb)) + min(dh, 360 - dh) * .5
        except Exception:
            return 999
    keep = sorted(ok, key=score)[:max(1, n)]
    return [m for m in ok if m in keep]


def mean_lum(m):
    try:
        return lum(m.get('mean') or '')
    except Exception:
        return .02 if m.get('tone') == 'dark' else .6


def over(m, c):
    """(veil, ink) for text laid over picture m: the veil goes toward the page colour of the picture's own tone
    (the ground when their tones agree, otherwise the ink colour), and the text takes the other one"""
    dark_pic = m.get('tone') != 'light'
    return (c['G'], c['I']) if dark_pic == c['dark'] else (c['I'], c['G'])


def veil_for(m, veil, ink, want, least=0.0):
    """smallest share of the veil colour over the picture's mean colour that gives `want`:1 for the ink"""
    mean = m.get('mean') or ('#222222' if m.get('tone') != 'light' else '#dddddd')
    for a in (0, .1, .2, .3, .4, .5, .6, .7, .8, .9):
        if a >= least and con(mix(mean, veil, a), ink) >= want:
            return a
    return .9


def rgba(h, a):
    r, g, b = _rgb(h)
    return f'rgba({r},{g},{b},{a:.2f})'


def bg_pic(m, slot, cls='bd'):
    """a made picture as the ground of its box: covers it, never the subject"""
    return (f'<img class="{cls}" src="{M}{e(m["src"])}" width="{int(m.get("w") or 0) or ""}" height="{int(m.get("h") or 0) or ""}" alt="" '
            f'loading="lazy" decoding="async" data-slot="{slot}">')


PW = 177                        # width of the reference's portrait tile at 1440; no portrait tile is set narrower
ARROW = '<svg class="arr" viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><path d="M2.5 8h10M8.5 4l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
CHEV = '<svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><path d="M4 6l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
CHECK = '<svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><circle cx="8" cy="8" r="6.4" fill="none" stroke="currentColor" stroke-width="1"/><path d="M5.4 8.2l1.8 1.8 3.4-3.6" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def pic(m, cls='', lazy=True, style=''):
    """a picture shown whole, at its own proportion"""
    if not m:
        return ''
    return (f'<img class="{cls}" src="{M}{e(m["src"])}" width="{int(m.get("w") or 0) or ""}" height="{int(m.get("h") or 0) or ""}" '
            f'alt="{e(m.get("alt"))}"{" loading=lazy decoding=async" if lazy else ""}{f" style={chr(34)}{style}{chr(34)}" if style else ""}>')


def asp(m):
    return (m.get('w') or 1) / (m.get('h') or 1)


def btn(c, kind='dark', big=False):
    if not c or not c.get('t'):
        return ''
    return f'<a class="btn {kind}{" big" if big else ""}" href="{e(c.get("h") or "#")}">{e(c["t"])}</a>'


def tag(t):
    return f'<span class="tag"><i></i>{e(t)}</span>' if t else ''


# ---------- sections ----------
def s_header(d, c):
    b = d.get('brand') or {}
    hero = d.get('hero') or {}
    note = hero.get('note')
    sec = hero.get('secondary') or {}
    bar = ''
    if note:
        link = f'<a href="{e(sec.get("h"))}">{e(sec["t"])} {ARROW}</a>' if sec.get('t') else ''
        bar = f'<div class="bar"><div class="wrap"><p>{e(note)}</p>{link}</div></div>'
    logo = ''
    if b.get('logo'):
        logo = f'<img src="{M}{e(b["logo"])}" alt="{e(b.get("name")) if b.get("logo_wordmark") else ""}" height="24">'
    name = '' if b.get('logo_wordmark') and b.get('logo') else f'<span>{e(b.get("name"))}</span>'
    nav = ''.join(f'<a href="{e(n.get("h"))}">{e(n.get("t"))}</a>' for n in d.get('nav') or [])
    si = d.get('signin') or {}
    signin = f'<a class="signin" href="{e(si.get("h"))}">{e(si["t"])}</a>' if si.get('t') else ''
    cta = btn(d.get('cta'))
    return f'''<div class="top" id="top">{bar}<header class="hd"><div class="wrap">
<a class="logo" href="{e(b.get("home") or "#")}">{logo}{name}</a>
<nav class="nav" aria-label="Primary">{nav}</nav>
<div class="acts">{signin}{cta}</div>
<button class="burger" type="button" aria-expanded="false" aria-controls="menu" aria-label="Menu"><i></i><i></i><i></i></button>
</div></header>
<div class="menu" id="menu" hidden><nav aria-label="Menu">{nav}{signin}</nav>{cta}</div></div>'''


def hero_tiles(d):
    """the opening cluster: top row = one portrait at the reference's portrait width + the first screen, bottom-aligned;
    bottom row = film and screens justified by ratio. A portrait only joins the bottom row if it still comes out at
    least PW wide there (a phone screen does not: it would be unreadable at that height)."""
    md = d.get('media') or {}
    L = list(md.get('screens') or [])
    P = []
    for x in list(md.get('phones') or []) + list(md.get('photos') or []):
        (P if asp(x) < 1 else L).append(x)
    v = md.get('video')
    top, bot = [], []
    port = P.pop(0) if P else None
    big = L.pop(0) if L else None
    if port:
        top.append(('port', port, min(PW, 384 * asp(port))))
    if big:
        top.append(('big', big, min(540 - (top[0][2] + 20 if top else 0), 310 * asp(big))))
    rowh = lambda tot, n: min(280, (840 - 20 * (n - 1)) / tot)
    fits = lambda xs: all(asp(m) >= 1 or rowh(sum(asp(q) for _, q in xs), len(xs)) * asp(m) >= PW for _, m in xs)
    if v:
        bot.append(('video', v))
    if L and asp(L[0]) < 2.4:
        bot.append(('img', L.pop(0)))
    while P and len(bot) < 4:
        trial = bot[:1] + [('img', P[0])] + bot[1:]
        if not fits(trial):
            break
        bot = trial; P.pop(0)
    while sum(asp(m) for _, m in bot) < 2.9 and len(bot) < 4:
        more = [x for x in L if asp(x) < 2.4]
        if not more:
            break
        trial = bot + [('img', more[0])]
        if not fits(trial) or rowh(sum(asp(m) for _, m in trial), len(trial)) < 240:
            break
        bot = trial; L.remove(more[0])
    return top, bot, sum(asp(m) for _, m in bot)


def tile(kind, m, lazy=False, w=None):
    a = asp(m)
    if kind == 'video':
        inner = (f'<video src="{M}{e(m["src"])}" poster="{M}{e(m.get("poster"))}" width="{m.get("w")}" height="{m.get("h")}" muted loop playsinline preload="metadata" '
                 f'aria-label="{e(m.get("alt"))}" data-auto></video>')
    else:
        inner = pic(m, lazy=lazy)
    return f'<figure class="tile {kind}" style="--r:{a:.4f}{f";--w:{w:.0f}" if w else ""}">{inner}</figure>'


def s_hero(d, c):
    h = d.get('hero') or {}
    st = d.get('steps') or {}
    top, bot, tot = hero_tiles(d)
    title = h.get('title') or ''
    hs = step(title, [(30, 130), (46, 104), (999, 84)])
    hm = step(title, [(30, 52), (46, 44), (999, 38)])
    tiles_top = f'<div class="tiles t1">{"".join(tile(k, m, w=w) for k, m, w in top)}</div>' if top else ''
    tiles_bot = f'<div class="tiles t2" style="--sum:{tot:.3f};--n:{len(bot)}">{"".join(tile(k, m) for k, m in bot)}</div>' if bot else ''
    text = ' '.join(x for x in (h.get('text'), h.get('text2')) if x)
    lead = f'<p class="lead ld">{e(text)}</p>' if text else ''
    acts = btn(h.get('secondary'), 'pill') + btn(h.get('primary'))
    acts = f'<div class="row ld">{acts}</div>' if acts else ''
    sceneb = ''
    if st.get('title'):
        t2 = f'<p class="lead2">{e(st.get("text"))}</p>' if st.get('text') else ''
        sceneb = f'''<div class="scene b"><div class="bt"><h2 class="d2" style="--fs:{step(st["title"], [(40, 90), (64, 72), (999, 58)])}">{e(st["title"])}</h2>{t2}</div></div>'''
    return f'''<section class="pin{'' if sceneb else ' solo'}" id="pin"><div class="stage">
<canvas class="disc" aria-hidden="true"></canvas>
<div class="scene a{' hast1' if top else ''}"><div class="wrap">
<div class="r1"><h1 class="d1" style="--fs:{hs};--fm:{hm}">{e(title)}</h1>{tiles_top}</div>
<div class="r2"><div class="copy">{lead}{acts}</div>{tiles_bot}</div>
</div></div>
{sceneb}
<span class="more" aria-hidden="true">{CHEV}</span>
</div></section>'''


def s_steps(d, c):
    st = d.get('steps') or {}
    items = [i for i in st.get('items') or [] if i.get('k') or i.get('title')]
    if not items:
        return ''
    cols = c['tabs'] or [(c['card'], c['I'])]
    ml = max(len(i.get('k') or i.get('title') or '') for i in items)
    fs = max(30, min(90, int((1280 - 40 * (len(items) - 1)) / len(items) * .9 / (.47 * max(ml, 1)))))
    tabs, panes = '', ''
    for n, i in enumerate(items):
        bg, on = cols[n % len(cols)]
        tabs += (f'<button class="tab" type="button" role="tab" id="st{n}" aria-controls="sp{n}" aria-selected="{"true" if n == 0 else "false"}" '
                 f'tabindex="{0 if n == 0 else -1}" data-bg="{bg}" data-on="{on}" data-dim="{mix(bg, on, .74)}"><i style="background:{c["A"]}"></i><span>{e(i.get("k") or i.get("title"))}</span><b></b></button>')
        cta = i.get('cta') or {}
        link = f'<a class="tl" href="{e(cta.get("h"))}">{e(cta["t"])} {ARROW}</a>' if cta.get('t') else ''
        img = ''
        if i.get('img'):
            md = d.get('media') or {}
            known = {m['src']: m for m in (md.get('screens') or []) + (md.get('phones') or []) + (md.get('photos') or [])}
            m = known.get(i['img'], {'src': i['img'], 'alt': i.get('title')})
            img = f'<div class="shot {e(i.get("shape") or "")}">{pic(m)}</div>'
        panes += (f'<div class="pane{" on" if n == 0 else ""}" role="tabpanel" id="sp{n}" aria-labelledby="st{n}"{"" if n == 0 else " inert"}>'
                  f'<div class="pt"><h3 class="h46">{e(i.get("title"))}</h3><p>{e(i.get("text"))}</p>{link}</div>{img}</div>')
    bg, on = cols[0]
    return f'''<section class="sec steps"><div class="wrap"><div class="card tabcard" style="--bg:{bg};--on:{on};--dim:{mix(bg, on, .74)}">
<div class="tabs" role="tablist" style="--n:{len(items)};--tf:{fs}px">{tabs}</div>
<div class="panes">{panes}</div></div></div></section>'''


def s_links(d, c):
    ls = [l for l in d.get('links') or [] if l.get('t')]
    if not ls:
        return ''
    md = d.get('media') or {}
    scr = md.get('screens') or []
    m = scr[2] if len(scr) > 2 else (scr[-1] if scr else None)
    chips, panes = '', ''
    for n, l in enumerate(ls):
        chips += (f'<button class="chipb" type="button" role="tab" id="lt{n}" aria-controls="lp{n}" aria-selected="{"true" if n == 0 else "false"}" '
                  f'tabindex="{0 if n == 0 else -1}">{e(l["t"])}</button>')
        big = l['t']                       # the reference sets a title at this size and the description in grey under it
        desc = f'<p class="lead2">{e(l["d"])}</p>' if l.get('d') else ''
        panes += (f'<div class="pane{" on" if n == 0 else ""}" role="tabpanel" id="lp{n}" aria-labelledby="lt{n}"{"" if n == 0 else " inert"}>'
                  f'<div class="lt"><h2 class="d2" style="--fs:{step(big, [(22, 90), (40, 72), (999, 58)])}">{e(big)}</h2>{desc}</div>'
                  f'<div class="row"><a class="btn pill" href="{e(l.get("h"))}">{e(l["t"])}</a></div></div>')
    shot = f'<div class="lshot">{pic(m)}</div>' if m else ''
    return f'''<section class="sec links"><div class="wrap"><div class="card linkcard{'' if m else ' nopic'}"><div class="rise">
<div class="lcol"><div class="chips" role="tablist">{chips}</div><div class="panes">{panes}</div></div>{shot}
</div></div></div></section>'''


def s_statement(d, c):
    s = d.get('statement') or {}
    trust = [t for t in d.get('trust') or [] if t]
    if not s.get('title') and not s.get('text') and not trust:
        return ''
    head = ''
    if s.get('title') or s.get('text'):
        big, small = (s.get('title'), s.get('text')) if s.get('title') else (s.get('text'), '')
        head = f'<div class="say"><h2 class="h58 blur" style="--fs:{step(big, [(180, 58), (999, 46)])}">{e(big)}</h2>{f"<p class=lead2>{e(small)}</p>" if small else ""}</div>'
    rows = ''
    if trust:
        half = (len(trust) + 1) // 2
        for n, part in enumerate([trust[:half], trust[half:]] if len(trust) > 3 else [trust]):
            if not part:
                continue
            reps = max(2, -(-8 // len(part)))
            grp = ''.join(f'<span class="wc">{e(t)}</span>' for t in part * reps)
            rows += f'<div class="mq{" rev" if n else ""}"><div class="mg">{grp}</div><div class="mg" aria-hidden="true">{grp}</div></div>'
        rows = f'<div class="mqs">{rows}</div>'
    return f'''<section class="band" id="band"><div class="bandbg"></div><div class="wrap">{head}</div>{rows}</section>'''


def s_features(d, c):
    f = d.get('features') or {}
    items = [i for i in f.get('items') or [] if i.get('t') or i.get('d')]
    if not items and not f.get('title'):
        return ''
    head = ''
    if f.get('title'):
        sub = '<p>' + e(f.get('text')) + '</p>' if f.get('text') else ''
        head = f'<div class="fh"><h2 class="h58">{e(f["title"])}</h2>{sub}{btn(d.get("cta"))}</div>'
    cards = ''.join(f'<div class="fc">{tag(i.get("t"))}<p>{e(i.get("d"))}</p></div>' for i in items)
    return f'''<section class="feat"><div class="wrap"><div class="fbox">{head}<div class="fg">{cards}</div></div></div></section>'''


def s_plans(d, c):
    p = d.get('plans') or {}
    items = [i for i in p.get('items') or [] if i.get('name')]
    if not items:
        return ''
    band = ''
    if p.get('title'):
        sub = '<p class="lead2">' + e(p.get('text')) + '</p>' if p.get('text') else ''
        band = f'<div class="pband"><div class="pbt"><h2 class="h58">{e(p["title"])}</h2>{sub}</div></div>'
    blurs = calm(made(d, 'blur'), c, min(len(items), 2))    # two hues at most, as on the reference; more plans take them in turn
    cards = ''
    for n, i in enumerate(items):
        bg, on = (c['A'], c['onA']) if i.get('marked') else (c['chip'], c['I'])
        img, pcls, pv = '', '', ''
        if blurs:                                                # one calm hue per plan, wrapping round
            m = blurs[n % len(blurs)]
            veil, on = over(m, c)
            bg = m.get('mean') or bg
            img, pcls = bg_pic(m, 'plan'), ' pic'
            pv = f';--pv:{rgba(veil, max(.55, veil_for(m, veil, on, 7)))}'
        rows = ''.join(f'<li>{CHECK}<span>{e(r)}</span></li>' for r in i.get('rows') or [])
        rows = f'<ul class="rows">{rows}</ul>' if rows else ''
        cards += f'''<div class="plan"><div class="ptop"><div class="pl"><div class="pn"><h3 class="h58">{e(i["name"])}</h3>{f"<p>{e(i.get('line'))}</p>" if i.get("line") else ""}</div>{btn(i.get("cta"))}</div>
<div class="price{pcls}" style="background:{bg};color:{on}{pv}">{img}<strong>{e(i.get("price"))}</strong>{f"<span>{e(i.get('per'))}</span>" if i.get("per") else ""}</div></div>{rows}</div>'''
    # 1 plan: one card; 2 or 4: the reference's two-across card; 3, 5 and more: three across, wrapping, and the card
    # stacks (picture panel with the price on top, name and button under it) because 430 px cannot hold both side by side
    pc = 1 if len(items) == 1 else 2 if len(items) in (2, 4) else 3
    note = f'<p class="pnote">{e(p["note"])}</p>' if p.get('note') else ''
    return f'''<section class="sec plans"><div class="wrap">{band}<div class="pgrid{" few" if pc == 3 else ""}{" one" if len(items) == 1 else ""}" style="--n:{pc}">{cards}</div>{note}</div></section>'''


def s_figures(d, c):
    fg = [f for f in d.get('figures') or [] if f.get('v')]
    if not fg:
        return ''
    GL, GH = .14, .22                                             # share of the text colour in a glass card, at rest and under the pointer

    def holds(base, on, want):
        """does `on` read `want`:1 on a glass card (rest and hover) laid over `base`?"""
        return min(con(mix(base, on, GL), on), con(mix(base, on, GH), on)) >= want
    cards = ''.join(f'<div class="glass"><strong style="--fs:{step(f["v"], [(5, 90), (8, 72), (999, 46)])}">{e(f["v"])}</strong><p>{e(f.get("l"))}</p></div>' for f in fg)
    land = made(d, 'land')
    cands = [land[i] for i in (2, 0) if i < len(land)]           # water, else the ridge: whichever is darker
    if not cands:
        on = c['on_deep']                                         # plain ground: taken away from its text until the cards hold 4.6:1
        away = '#000000' if lum(on) > lum(c['deep']) else '#ffffff'
        deep = next((x for x in (mix(c['deep'], away, t / 20) for t in range(21)) if holds(x, on, 4.6)), away)
        return f'''<section class="figs" data-slot="backdrop" style="background:{deep};--deep:{deep}"><div class="wrap"><div class="gl" style="--n:{len(fg)}">{cards}</div></div></section>'''
    m = min(cands, key=mean_lum)
    dk, lt = (c['G'], c['I']) if c['dark'] else (c['I'], c['G'])   # the backdrop is always darkened, as the reference's is
    mean = m.get('mean') or dk
    a = .9
    for t in (.6, .65, .7, .75, .8, .85):  # low key: mean at or under ~25% (sRGB) and 7:1 for the text
        x = mix(mean, dk, t)
        if lum(x) <= .051 and con(x, lt) >= 7 and holds(x, lt, 5.5):
            a = t
            break
    return f'''<section class="figs pic" data-slot="backdrop" style="background:{mix(mean, dk, a)};color:{lt};--ond:{lt};--fv:{rgba(dk, a)}">{bg_pic(m, "backdrop")}<div class="wrap"><div class="gl" style="--n:{len(fg)}">{cards}</div></div></section>'''


def s_faq(d, c):
    f = d.get('faq') or {}
    items = [i for i in f.get('items') or [] if i.get('q') and i.get('a')]
    if not items:
        return ''
    head = f'<h2 class="h58">{e(f["title"])}</h2>' if f.get('title') else ''
    qs = ''.join(f'<details class="q"><summary><span>{e(i["q"])}</span>{CHEV}</summary><p>{e(i["a"])}</p></details>' for i in items)
    return f'''<section class="sec faq"><div class="wrap"><div class="fbox">{f'<div class="fh">{head}</div>' if head else ''}<div class="qs">{qs}</div></div></div></section>'''


def s_close(d, c):
    cl = d.get('close') or {}
    if not cl.get('title'):
        return ''
    md = d.get('media') or {}
    pool = (md.get('photos') or []) + (md.get('phones') or []) + (md.get('screens') or [])
    trail = ''.join(f'<span class="tr" style="--r:{asp(m):.4f}">{pic(m)}</span>' for m in pool[:5])
    t = cl['title']
    return f'''<section class="close" id="close"><div class="trail" aria-hidden="true">{trail}</div><div class="wrap">
<h2 class="d1" style="--fs:{step(t, [(30, 130), (46, 104), (999, 84)])};--fm:{step(t, [(30, 52), (46, 44), (999, 38)])}">{e(t)}</h2>
{f'<p class="lead2">{e(cl.get("text"))}</p>' if cl.get('text') else ''}
<div class="row">{btn(cl.get('cta'), 'dark', True)}</div></div></section>'''


def s_foot(d, c):
    b = d.get('brand') or {}
    ft = d.get('foot') or {}
    col = lambda xs: '<div class="fcol">' + ''.join(f'<a href="{e(x.get("h"))}">{e(x.get("t"))}</a>' for x in xs if x.get('t')) + '</div>' if xs else ''
    extra = [x for x in (d.get('signin'), d.get('cta')) if x and x.get('t')]
    cols = col(d.get('nav') or []) + col(d.get('links') or []) + col(extra)
    name = b.get('name') or ''
    ws = min(26, 185 / max(len(name), 1))
    legal = ''.join(f'<span>{e(ft.get("legal"))}</span>' if ft.get('legal') else '') + ''.join(f'<a href="{e(x.get("h"))}">{e(x.get("t"))}</a>' for x in ft.get('links') or [])
    return f'''<footer class="ft"><div class="wrap">
<div class="fcols">{cols}{f'<p class="fnote">{e(ft["text"])}</p>' if ft.get('text') else ''}</div>
{f'<div class="word" aria-hidden="true" style="--ws:{ws:.2f}vw">{e(name)}</div>' if name else ''}
{f'<div class="legal">{legal}</div>' if legal else ''}</div></footer>'''


# ---------- the page ----------
CSS = r'''
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}body{margin:0;background:var(--g);color:var(--i);font:400 17px/1.41 "FONT",ui-sans-serif,system-ui,sans-serif;letter-spacing:-.005em;-webkit-font-smoothing:antialiased;overflow-x:clip}
img,video,canvas{display:block;max-width:100%}img,video{height:auto}h1,h2,h3,p,figure,ul{margin:0}ul{padding:0;list-style:none}a{color:inherit;text-decoration:none}button{font:inherit;color:inherit;letter-spacing:inherit;background:none;border:0;padding:0;cursor:pointer}
:focus-visible{outline:2px solid currentColor;outline-offset:3px;border-radius:4px}
.wrap{width:min(1360px,100% - 80px);margin-inline:auto}
.d1{font-weight:300;font-size:calc(var(--fs)*1px);line-height:1.05;letter-spacing:-.045em;text-wrap:balance}
.d2{font-weight:300;font-size:calc(var(--fs,90)*1px);line-height:1;letter-spacing:-.04em;text-wrap:balance}
.h58{font-weight:300;font-size:calc(var(--fs,58)*1px);line-height:1.1;letter-spacing:-.035em;text-wrap:balance}
.h46{font-weight:300;font-size:46px;line-height:1.15;letter-spacing:-.015em}
.lead{font-weight:300;font-size:28px;line-height:1.3;letter-spacing:-.02em;color:var(--mu)}
.lead2{font-weight:300;font-size:22px;line-height:1.4;letter-spacing:-.015em;color:var(--mu)}
.row{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:40px;padding:8px 16px;font-size:17px;line-height:1;border-radius:8px;border:1px solid transparent;transition:color .15s cubic-bezier(.4,0,.2,1),background-color .15s cubic-bezier(.4,0,.2,1),border-color .15s cubic-bezier(.4,0,.2,1),transform .15s cubic-bezier(.4,0,.2,1);text-align:center}
.btn.dark{background:var(--i);color:var(--g)}.btn.dark:hover{background:var(--hov)}
.btn.pill{border-radius:999px;border-color:var(--mu);background:color-mix(in srgb,var(--card) 70%,transparent);color:var(--i);backdrop-filter:blur(2px)}.btn.pill:hover{background:var(--card);border-color:var(--i)}
.btn:active{transform:scale(.97)}
.btn.big{min-height:80px;padding:4px 44px;font-size:28px;font-weight:300;border-radius:16px}.btn.big.pill{border-radius:999px}
.tag{display:inline-flex;align-items:center;gap:8px;padding:8px 12px;border:1px solid var(--mu);border-radius:4px;font-size:12px;line-height:1;letter-spacing:.03em;text-transform:uppercase}.tag i{flex:none;width:8px;height:8px;border-radius:2px;background:currentColor}
.arr{flex:none;transition:transform .15s cubic-bezier(.4,0,.2,1)}a:hover>.arr{transform:translateX(3px)}
/* top: announcement bar + header, fixed; leaves on the way down, returns on the way up (.5s) */
.top{position:fixed;inset:0 0 auto 0;z-index:50;transition:transform .5s cubic-bezier(.4,0,.2,1)}.top.away{transform:translateY(-100%)}
.bar{background:var(--i);color:var(--g)}.bar .wrap{display:flex;justify-content:center;align-items:center;gap:24px;min-height:49px;padding:12px 0}.bar a{display:inline-flex;align-items:center;gap:6px;white-space:nowrap}
.hd{background:var(--card)}.hd .wrap{display:flex;align-items:center;gap:32px;height:80px}
.logo{display:inline-flex;align-items:center;gap:10px;font-size:24px;font-weight:500;letter-spacing:-.04em}.logo img{height:24px;width:auto}
.nav{display:flex;flex:1;gap:0}.nav a,.menu nav a{padding:12px 16px;border-radius:8px;font-size:14px;letter-spacing:.03em;text-transform:uppercase;line-height:1.05;transition:background-color .15s}.nav a:hover,.menu nav a:hover{background:var(--chip)}
.acts{display:flex;align-items:center;gap:8px}.signin{padding:8px}
.burger{display:none;width:40px;height:40px;margin-right:-8px;flex-direction:column;justify-content:center;align-items:center;gap:5px}.burger i{display:block;width:18px;height:1.5px;background:currentColor}
.menu{background:var(--card);padding:8px 16px 20px;border-top:1px solid var(--ln)}.menu nav{display:grid;margin-bottom:12px}.menu nav a{padding:14px 8px}.menu .btn{width:100%}
/* the pinned opening: 200vh of travel; the stage holds two scenes and the disc */
.pin{position:relative;height:200vh}.pin.solo{height:auto}
.stage{position:sticky;top:0;height:100vh;min-height:560px;overflow:clip}.pin.solo .stage{position:relative;height:auto;min-height:100vh}
.disc{position:absolute;inset:0;width:100%;height:100%;pointer-events:none}
.scene.a{position:relative;padding-top:calc(var(--top) + min(134px,11vh));will-change:transform}
.scene.b{position:absolute;inset:0;display:grid;place-items:center;text-align:center;padding:0 16px;opacity:0;visibility:hidden}
.bt{width:min(800px,100%)}.bt .lead2{width:min(520px,100%);margin:24px auto 0;color:var(--i)}
.r1{display:flex;justify-content:space-between;align-items:flex-end;gap:20px}.r1 h1{flex:0 1 800px;max-width:800px}
.r2{display:flex;justify-content:space-between;align-items:flex-start;gap:40px;margin-top:20px}.copy{flex:0 0 400px}.copy .row{margin-top:31px}
.tiles{display:flex;gap:20px}.tile{position:relative;border-radius:8px;overflow:hidden;background:var(--card);box-shadow:0 0 0 1px color-mix(in srgb,var(--i) 8%,transparent);will-change:transform}
.tile img,.tile video{width:100%;height:auto}.tile::after{content:"";position:absolute;inset:0;background:var(--a);opacity:var(--k,0);pointer-events:none}
.t1{flex:none;align-items:flex-end}.t1 .tile{flex:none;width:calc(var(--w)*1px)}
.t2{flex:0 1 840px;max-width:calc(280px*var(--sum) + (var(--n) - 1)*20px);margin-left:auto}.t2 .tile{flex:var(--r) 1 0;min-width:0}
.more{position:absolute;left:50%;bottom:44px;translate:-50% 0;display:grid;place-items:center;width:56px;height:40px;border-radius:999px;background:color-mix(in srgb,var(--card) 70%,transparent);backdrop-filter:blur(2px)}.pin.solo .more{display:none}
/* opening load: lines rise and settle, tiles arrive from above and below */
@keyframes up{from{opacity:0;transform:translateY(var(--d,100px))}to{opacity:1;transform:none}}
.js .ln{display:inline-block;animation:up 1.1s cubic-bezier(.16,1,.3,1) both;animation-delay:calc(var(--l)*90ms + 80ms)}
.js .ld{animation:up 1.1s cubic-bezier(.16,1,.3,1) both;animation-delay:.34s;--d:70px}.js .row.ld{animation-delay:.42s}
.js .tile{animation:up 1.2s cubic-bezier(.16,1,.3,1) both;animation-delay:calc(var(--o)*90ms + .2s);--d:calc(var(--dir)*360px)}
/* cards */
.sec{padding:80px 0}.card{background:var(--card);border-radius:20px}
.tabcard{padding:40px;background:var(--bg);color:var(--on);transition:background-color .5s cubic-bezier(.4,0,.2,1),color .5s cubic-bezier(.4,0,.2,1)}
.tabs{display:grid;grid-template-columns:repeat(var(--n),1fr);gap:40px}
.tab{position:relative;display:flex;align-items:center;min-height:106px;padding:8px 20px;border-radius:16px;text-align:left;overflow:hidden;transition:background-color .5s cubic-bezier(.4,0,.2,1),color .5s cubic-bezier(.4,0,.2,1);color:var(--dim)}
.tab span{font-weight:300;font-size:var(--tf);line-height:1;letter-spacing:-.04em}.tab i{display:none}
.tab:hover{color:var(--on)}.tab[aria-selected=true]{background:color-mix(in srgb,var(--on) 12%,transparent);color:var(--on)}
.tab b{position:absolute;left:0;bottom:0;height:1px;width:100%;background:currentColor;transform:scaleX(0);transform-origin:0 50%}
.tab[aria-selected=true] b.run{animation:prog 12s linear forwards}@keyframes prog{to{transform:scaleX(1)}}
.panes{display:grid;margin-top:40px}.pane{grid-area:1/1;opacity:0;visibility:hidden;transition:opacity .5s cubic-bezier(.4,0,.2,1),visibility 0s .5s}.pane.on{opacity:1;visibility:visible;transition:opacity .5s cubic-bezier(.4,0,.2,1)}
.tabcard .pane{display:grid;grid-template-columns:400px 1fr;gap:80px;min-height:550px;align-items:start}
.pt{display:flex;flex-direction:column;gap:16px;align-items:flex-start}.tl{display:inline-flex;align-items:center;gap:4px;margin-top:0}
.shot{display:flex;align-items:center;justify-content:center;height:550px;--sh:550px}.shot img{width:auto;height:auto;max-width:100%;max-height:var(--sh);border-radius:12px;box-shadow:0 30px 60px -30px rgba(0,0,0,.45)}.shot.phone img{border-radius:22px}.shot.book img{border-radius:4px}
/* link card: chips, a large line, one screen shown whole on the same ground */
.linkcard{border-radius:16px;padding:40px;overflow:clip}.rise{display:grid;grid-template-columns:minmax(0,560px) minmax(0,640px);justify-content:space-between;gap:40px;align-items:center;min-height:560px}
.nopic .rise{grid-template-columns:minmax(0,900px)}
.lcol{display:flex;flex-direction:column;justify-content:space-between;gap:48px;align-self:stretch}.chips{display:flex;flex-wrap:wrap;gap:8px}
.chipb{padding:12px 16px;border-radius:8px;background:var(--g);font-size:14px;line-height:1.05;letter-spacing:.03em;text-transform:uppercase;transition:background-color .5s cubic-bezier(.4,0,.2,1)}.chipb:hover,.chipb[aria-selected=true]{background:var(--chip)}
.linkcard .panes{margin:0}.linkcard .pane{display:flex;flex-direction:column;gap:24px;justify-content:flex-end;transition-duration:1s}.lt{display:flex;flex-direction:column;gap:24px}.lt .lead2{max-width:480px}
.lshot img{width:100%;border-radius:12px;box-shadow:0 0 0 1px color-mix(in srgb,var(--i) 10%,transparent)}
/* the bright band: ground fades to the accent, the statement clears line by line, two rows of word chips run against each other */
.band{position:relative;padding:120px 0;color:var(--ona);overflow:clip}.bandbg{position:absolute;inset:0;background:var(--a);opacity:var(--bo,1)}.band>.wrap{position:relative}
.say{max-width:1080px;margin-left:40px;margin-bottom:80px}.say .lead2{color:inherit;max-width:640px;margin-top:32px}
.blur .w{display:inline-block;will-change:filter,opacity}
.mqs{position:relative;display:flex;flex-direction:column;gap:16px;width:min(1360px,100% - 80px);margin-inline:auto;overflow:hidden;-webkit-mask-image:linear-gradient(90deg,transparent,#000 8%,#000 92%,transparent);mask-image:linear-gradient(90deg,transparent,#000 8%,#000 92%,transparent)}
.mq{display:flex;width:max-content}.mg{display:flex;gap:20px;padding-right:20px;animation:mq 60s linear infinite}.mq.rev .mg{animation-direction:reverse}.band.idle .mg{animation:none}@keyframes mq{to{transform:translateX(-100%)}}
.wc{padding:12px;border-radius:8px;background:var(--card);color:var(--i);font-weight:300;font-size:46px;line-height:1.15;letter-spacing:-.015em;white-space:nowrap}
/* features: a quiet box on the band's fading ground, small tagged cards */
.feat{background:linear-gradient(var(--a),var(--g) 70%);padding-bottom:80px}.fbox{background:var(--g);border-radius:16px;padding:112px 80px}
.fh{display:flex;flex-direction:column;align-items:center;gap:24px;text-align:center;max-width:960px;margin:0 auto 40px}.fh p{max-width:440px}
.fg{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}.fc{display:flex;flex-direction:column;align-items:flex-start;gap:16px;padding:16px;border-radius:12px;background:var(--card)}.fc p{font-weight:300;font-size:22px;line-height:1.4;letter-spacing:-.015em}
/* plans */
.pband{border-radius:16px;background:var(--soft);padding:54px 40px;margin-bottom:20px}.pbt{max-width:640px;display:flex;flex-direction:column;gap:24px}.pband .lead2{color:var(--i)}
.pgrid{display:grid;grid-template-columns:repeat(var(--n),minmax(0,1fr));gap:20px}.pgrid.one{max-width:670px}
.pgrid.few .ptop{flex-direction:column-reverse;gap:24px}.pgrid.few .pl{padding-top:0;gap:24px}.pgrid.few .price{flex:none;min-height:220px}.pgrid.few .pn .h58{font-size:46px}
.plan .h58,.pn p,.price strong,.price span{overflow-wrap:anywhere}.plan .btn{max-width:100%}.plan{min-width:0;display:flex;flex-direction:column;gap:40px;padding:20px;border-radius:16px;background:var(--card)}
.ptop{display:flex;gap:40px;justify-content:space-between}.pl{display:flex;flex-direction:column;justify-content:space-between;gap:29px;align-items:flex-start;padding-top:96px;flex:1}.pn p{margin-top:8px;font-weight:300;font-size:22px;line-height:1.4;letter-spacing:-.015em}
.price{position:relative;overflow:hidden;flex:0 0 260px;min-height:378px;border-radius:8px;padding:20px;display:flex;flex-direction:column;justify-content:flex-end;gap:8px}
.bd{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}.price.pic::after{content:"";position:absolute;inset:0;background:linear-gradient(to top,var(--pv) 0,var(--pv) 30%,transparent 62%)}.price strong,.price span{position:relative;z-index:1}.price strong{font-weight:300;font-size:58px;line-height:1;letter-spacing:-.055em}.price span{font-size:15px;line-height:1.4}
.rows{border-top:1px solid var(--ln);padding-top:24px;display:grid;gap:12px}.rows li{display:flex;gap:12px;font-size:15px;line-height:1.4}.rows svg{flex:none;margin-top:2px}
.pnote{margin-top:20px;max-width:900px;font-size:15px;color:var(--mu)}
/* figures on the backdrop slot */
.figs{position:relative;overflow:clip;background:var(--deep);color:var(--ond);padding:160px 0}.figs.pic>.bd{filter:saturate(.45)}.figs.pic::after{content:"";position:absolute;inset:0;background:var(--fv)}.figs>.wrap{position:relative;z-index:1}.gl{display:grid;grid-template-columns:repeat(var(--n),minmax(0,1fr));gap:20px;max-width:calc(var(--n)*407px - 20px);margin-inline:auto}
.glass{display:flex;flex-direction:column;justify-content:space-between;gap:16px;min-height:341px;padding:20px;border-radius:12px;background:color-mix(in srgb,var(--ond) 14%,transparent);backdrop-filter:blur(40px);transition:background-color .5s cubic-bezier(.4,0,.2,1)}.glass:hover{background:color-mix(in srgb,var(--ond) 22%,transparent)}
.glass strong{font-weight:300;font-size:calc(var(--fs)*1px);line-height:1;letter-spacing:-.06em;white-space:nowrap}
/* faq */
.faq .fbox{background:var(--card);padding:80px}.qs{max-width:960px;margin:0 auto}.q{border-top:1px solid var(--ln)}.q:last-child{border-bottom:1px solid var(--ln)}
.q summary{display:flex;justify-content:space-between;align-items:center;gap:24px;padding:22px 0;cursor:pointer;list-style:none;font-weight:300;font-size:22px;line-height:1.4;letter-spacing:-.015em}.q summary::-webkit-details-marker{display:none}.q summary svg{flex:none;transition:transform .3s cubic-bezier(.4,0,.2,1)}.q[open] summary svg{transform:rotate(180deg)}.q p{padding:0 40px 24px 0;max-width:760px;color:var(--mu)}
/* close: the largest line, centred; pictures trail the pointer behind it */
.close{position:relative;padding:208px 0;text-align:center;overflow:clip}.close .wrap{position:relative;display:flex;flex-direction:column;align-items:center;gap:32px}.close h2{max-width:1000px}.close .lead2{max-width:560px}
.trail{position:absolute;inset:0;pointer-events:none}.tr{position:absolute;left:0;top:0;width:calc(150px*var(--r));max-width:220px;opacity:0;transition:opacity .4s;border-radius:6px;overflow:hidden;will-change:transform}.tr img{width:100%}.trail.on .tr{opacity:1}
/* foot */
.ft{border-top:1px solid var(--ln);padding:64px 0}.fcols{display:grid;grid-template-columns:repeat(4,240px);gap:32px 0}.fcol{display:grid;gap:8px;align-content:start;justify-items:start}.fcol a{padding:4px 8px;border-radius:8px;transition:background-color .15s}.fcol a:hover{background:var(--chip)}
.fnote{grid-column:span 1;font-size:14px;line-height:1.5;color:var(--mu);max-width:340px;justify-self:end}.fcols:has(.fcol:nth-child(3)) .fnote{grid-column:4}
.word{margin-top:48px;font-weight:500;font-size:min(var(--ws),252px);line-height:.86;letter-spacing:-.06em;white-space:nowrap}
.legal{display:flex;flex-wrap:wrap;gap:2px 16px;padding-top:48px;font-size:12px;letter-spacing:.03em;color:var(--mu)}.legal a{text-transform:uppercase}.legal a:hover{color:var(--i)}
@media (max-width:1100px){.wrap,.mqs{width:calc(100% - 32px)}
.d1{font-size:calc(var(--fm)*1px)}.d2{font-size:44px;letter-spacing:-.05em}.h58,.price strong{font-size:32.77px}.h46{font-size:24px;line-height:1.2;letter-spacing:-.04em}.lead{font-size:20px}.lead2,.fc p,.pn p,.q summary{font-size:18px}body,.btn{font-size:15px}
.hd .wrap{height:49px;justify-content:space-between}.nav,.acts{display:none}.burger{display:flex}.bar .wrap{justify-content:flex-start;flex-wrap:wrap;gap:2px 16px}.bar p{flex-basis:100%}.bar:not(:has(a)) p{flex-basis:auto}
.scene.a{padding-top:calc(var(--top) + 54px)}.scene.a>.wrap{display:flex;flex-direction:column}.r1,.r2{display:contents}.r1 h1{flex:none;max-width:none}.copy{flex:none;order:1;margin-top:20px}.copy .row{margin-top:16px;flex-wrap:nowrap}.copy .btn{flex:1}
.t1{order:2;margin-top:32px;gap:12px}.t1 .tile.port{width:36%}.t1 .tile.big{flex:1 1 0;width:auto;min-width:0}.t1 .tile:only-child{width:100%;flex:none}.t1 .tile.port:only-child{width:36%}
.t2{order:3;max-width:none;margin:40px 0 0;gap:12px}.t2 .tile:nth-child(n+3){display:none}.hast1 .t2{display:none}.linkcard .d2{font-size:32.77px;line-height:1.1}.more{bottom:20px}
.sec{padding:32px 0}.tabcard,.linkcard{padding:16px;border-radius:16px}.tabs{display:flex;flex-wrap:wrap;gap:4px}.tab{min-height:45px;padding:8px;border-radius:8px;gap:8px}.tab span{font-size:24px;line-height:1.2;letter-spacing:-.03em}.tab i{display:block;width:8px;height:8px;border-radius:2px;flex:none}
.panes{margin-top:16px}.tabcard .pane{display:flex;flex-direction:column-reverse;gap:24px;min-height:0}.shot{height:300px;width:100%;--sh:300px}
.rise{display:flex;flex-direction:column;align-items:stretch;min-height:0;gap:32px}.lcol{gap:40px}.chips{flex-wrap:nowrap;overflow-x:auto;margin-right:-16px;padding-right:16px;scrollbar-width:none}.chipb{white-space:nowrap;padding:11px 16px}
.band{padding:64px 0}.say{margin:0 16px 48px}.wc{font-size:24px;line-height:1.2;padding:10px 12px}.mqs{gap:8px}.mg{gap:8px;padding-right:8px}
.feat{padding-bottom:32px}.fbox,.faq .fbox{padding:64px 12px}.fg{grid-template-columns:1fr;gap:12px}.fc{padding:12px}
.pband{padding:32px 16px}.pgrid,.pgrid.few{grid-template-columns:minmax(0,1fr)}.pgrid.few .pn .h58{font-size:32.77px}.pgrid.few .price{min-height:180px}.ptop{flex-direction:column-reverse;gap:24px}.pl{padding-top:0}.price{flex:none;min-height:180px}.price.pic::after{background:linear-gradient(to top,var(--pv) 0,var(--pv) 60%,transparent 100%)}
.figs{padding:64px 0}.gl{display:flex;max-width:none;overflow-x:auto;scroll-snap-type:x mandatory;margin-right:-16px;padding-right:16px;scrollbar-width:none}.glass{flex:0 0 280px;min-height:256px;scroll-snap-align:start}.glass strong{font-size:calc(min(var(--fs),58)*1px)}
.close{padding:120px 0}.btn.big{min-height:56px;font-size:20px;padding:4px 28px}.tr{width:calc(90px*var(--r))}
.ft{padding:40px 0}.fcols{grid-template-columns:1fr 1fr;gap:32px 16px}.fnote,.fcols:has(.fcol:nth-child(3)) .fnote{grid-column:1/-1;justify-self:start}.word{margin-top:32px}.legal{padding-top:32px}}
/* stillness when asked for, and when the opening does not fit the window */
.still .pin,.pin.flat{height:auto}.still .stage,.pin.flat .stage{position:relative;height:auto;min-height:0;overflow:visible}.still .scene.a,.pin.flat .scene.a{padding-bottom:64px}
.still .scene.b,.pin.flat .scene.b{position:relative;inset:auto;opacity:1;visibility:visible;min-height:100vh}.still .disc,.pin.flat .disc{top:auto;bottom:0;height:100vh}.still .more,.pin.flat .more{display:none}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important;scroll-behavior:auto!important}.top.away{transform:none}.tr{display:none}.mq{flex-wrap:wrap}.mq .mg[aria-hidden]{display:none}.mq .mg{flex-wrap:wrap;width:100%}.mq{width:100%}.wc{white-space:normal}}
'''

JS = r'''
(()=>{const D=document,R=D.documentElement,$=(s,r=D)=>r.querySelector(s),$$=(s,r=D)=>[...r.querySelectorAll(s)];
const still=matchMedia('(prefers-reduced-motion:reduce)').matches;R.classList.add('js');if(still)R.classList.add('still');
const cl=v=>v<0?0:v>1?1:v,io=t=>t<.5?2*t*t:1-Math.pow(-2*t+2,2)/2,out=t=>1-Math.pow(1-t,3);
const top=$('#top'),setTop=()=>R.style.setProperty('--top',top.offsetHeight+'px');setTop();
/* words into lines: the opening headline rises line by line; the band statement clears line by line */
const split=(el,c)=>{const t=el.textContent;el.setAttribute('aria-label',t);el.textContent='';t.split(/\s+/).filter(Boolean).forEach((w,i,a)=>{const s=D.createElement('span');s.className=c;s.textContent=w;s.setAttribute('aria-hidden','true');el.append(s,i<a.length-1?' ':'');});return $$('.'+c,el)};
const lines=ws=>{let y=null,l=-1;ws.forEach(w=>{const t=w.offsetTop;if(y===null||Math.abs(t-y)>4){l++;y=t}w._l=l;w.style.setProperty('--l',l)});return l+1};
const h1=$('.scene.a h1');let hw=[];if(h1&&!still){hw=split(h1,'ln');lines(hw)}
$$('.t1 .tile').forEach((t,i)=>{t.style.setProperty('--o',i);t.style.setProperty('--dir',-1)});$$('.t2 .tile').forEach((t,i)=>{t.style.setProperty('--o',i+2);t.style.setProperty('--dir',1)});
$$('.tile').forEach(t=>t.addEventListener('animationend',()=>{t.style.animation='none'}));
$$('video[data-auto]').forEach(v=>{if(!still&&v.offsetParent){v.autoplay=true;v.play().catch(()=>{})}});
/* header leaves going down, returns going up */
let ly=0;const head=()=>{const y=scrollY;if(!still&&!$('.burger[aria-expanded=true]'))top.classList.toggle('away',y>ly&&y>120);ly=y};
const bg=$('.burger'),menu=$('#menu');if(bg)bg.addEventListener('click',()=>{const o=bg.getAttribute('aria-expanded')!=='true';bg.setAttribute('aria-expanded',o);menu.hidden=!o});
/* the pinned opening */
const pin=$('#pin'),stage=$('.stage'),A=$('.scene.a'),B=$('.scene.b'),cv=$('.disc'),more=$('.more');let cells=[],cw=0,ch=0,lastC=-1,tiles=[],cur=0,flat=false,raf=0;
const tone=getComputedStyle(R).getPropertyValue('--tone').trim();
const build=()=>{if(!cv||!B)return;const r=cv.getBoundingClientRect(),dpr=Math.min(devicePixelRatio||1,1.5);cw=r.width;ch=r.height;cv.width=cw*dpr;cv.height=ch*dpr;const x=cv.getContext('2d');x.setTransform(dpr,0,0,dpr,0,0);
 const s=cw<700?8:10,Rd=cw<700?Math.min(cw*.58,ch*.34):Math.min(310,ch*.36),cx=cw/2,cy=ch/2;cells=[];let seed=7;const rnd=()=>(seed=(seed*16807)%2147483647)/2147483647;
 for(let gy=Math.floor((cy-Rd)/s)*s;gy<cy+Rd;gy+=s)for(let gx=Math.floor((cx-Rd)/s)*s;gx<cx+Rd;gx+=s){const d=Math.hypot(gx+s/2-cx,gy+s/2-cy)/Rd;if(d<=1)cells.push([gx,gy,d,rnd(),s])}lastC=-1};
const draw=c=>{if(!cells.length||Math.abs(c-lastC)<.004)return;lastC=c;const x=cv.getContext('2d');x.clearRect(0,0,cw,ch);if(c<=0)return;x.fillStyle=tone;x.strokeStyle=tone;x.lineWidth=1;const lim=c*1.5;
 for(const[gx,gy,d,n,s]of cells){const v=d+n*.5;if(v<lim){if(v>lim-.12&&c<1)x.strokeRect(gx+1.5,gy+1.5,s-3,s-3);else x.fillRect(gx,gy,s+.5,s+.5)}}};
const measure=()=>{setTop();if(!pin)return;flat=still||!B||A.offsetHeight>innerHeight+2&&innerWidth>1100;pin.classList.toggle('flat',flat&&!still&&!!B);build();
 const sr=stage.getBoundingClientRect();tiles=$$('.tile',A).map(t=>{const p=t.style.transform;t.style.transform='none';const r=t.getBoundingClientRect();t.style.transform=p;return[t,sr.left+sr.width/2-(r.left+r.width/2),sr.top+sr.height/2-(r.top+r.height/2)]});
 if(flat){draw(1);A.style.cssText='';B&&(B.style.cssText='');tiles.forEach(([t])=>{t.style.transform='';t.style.opacity='';t.style.setProperty('--k',0)})}else paint(true)};
const paint=force=>{if(!pin||flat||!B)return;const r=pin.getBoundingClientRect(),span=r.height-innerHeight,tgt=cl(-r.top/span)*900;cur=force?tgt:cur+(tgt-cur)*.16;if(Math.abs(tgt-cur)<.3)cur=tgt;const Y=cur;
 const a=cl((Y-60)/160),b=io(cl((Y-90)/300)),c=cl((Y-240)/300),d=cl((Y-500)/240);
 const copy=$('.copy',A);h1&&(h1.style.opacity=1-a,h1.style.transform=`translateY(${-55*a}px)`);copy&&(copy.style.opacity=1-cl((Y-110)/160),copy.style.transform=`translateY(${-50*cl((Y-110)/160)}px)`);
 tiles.forEach(([t,dx,dy],i)=>{const k=cl(b*1.12-i*.03);t.style.transform=k?`translate(${dx*k*.82}px,${dy*k*.82}px) scale(${1-.86*k})`:'';t.style.setProperty('--k',cl(k*3));t.style.opacity=1-cl((k-.82)/.18)});
 A.inert=a>=1;A.style.visibility=Y>420?'hidden':'';const av=$('video',A);if(av){if(Y>420){av.paused||av.pause()}else if(av.paused&&av.offsetParent&&av.dataset.auto!==undefined&&r.bottom>0)av.play().catch(()=>{})}draw(c);
 B.style.visibility=d>0?'visible':'hidden';B.style.opacity=d;B.inert=d<.5;$('.bt',B).style.transform=`translateY(${(1-out(d))*200}px)`;more&&(more.style.opacity=1-cl((Y-800)/80));
 if(cur!==tgt){cancelAnimationFrame(raf);raf=requestAnimationFrame(()=>paint())}};
/* the band */
const band=$('#band'),bbg=$('.bandbg'),bl=$('.blur');let bw=[];if(bl&&!still){bw=split(bl,'w');}
const bpad=band?parseFloat(getComputedStyle(band).paddingTop)||0:0;/* the ground is whole before the first line of the band is on screen: its text is set for the accent, not for the page */
const bandPaint=()=>{if(!band||still)return;const r=band.getBoundingClientRect(),vh=innerHeight;if(r.bottom<-200||r.top>vh+200)return;bbg.style.setProperty('--bo',cl((vh-r.top)/Math.max(24,Math.min(vh*.2,bpad-8))));
 if(bw.length){const br=bl.getBoundingClientRect();bw.forEach(w=>{const y=br.top+w.offsetTop-bl.offsetTop+(w.offsetParent===bl?bl.offsetTop:0),p=out(cl((vh*.82-y)/(vh*.3)));w.style.opacity=.5+.5*p;w.style.filter=p<1?`blur(${(8*(1-p)).toFixed(2)}px)`:''})}};
/* tabs: both tab sets; the first runs on a 12s clock with a line that fills */
const tabset=(root,auto)=>{if(!root)return;const ts=$$('[role=tab]',root),ps=$$('[role=tabpanel]',root),card=root.closest('.card')||root;let i=0,tm=0,seen=false,hold=false;
 const go=(n,user)=>{i=(n+ts.length)%ts.length;ts.forEach((t,k)=>{const on=k===i;t.setAttribute('aria-selected',on);t.tabIndex=on?0:-1;const b=$('b',t);if(b){b.classList.remove('run');if(on&&auto&&!still&&!hold){void b.offsetWidth;b.classList.add('run')}}});
  ps.forEach((p,k)=>{p.classList.toggle('on',k===i);p.inert=k!==i});const t=ts[i];if(t.dataset.bg){card.style.setProperty('--bg',t.dataset.bg);card.style.setProperty('--on',t.dataset.on);card.style.setProperty('--dim',t.dataset.dim)}if(user)ts[i].focus({preventScroll:true});clock()};
 const clock=()=>{clearTimeout(tm);if(auto&&!still&&seen&&!hold&&ts.length>1)tm=setTimeout(()=>go(i+1),12000)};
 ts.forEach((t,k)=>{t.addEventListener('click',()=>go(k));t.addEventListener('keydown',e=>{if(e.key==='ArrowRight'){e.preventDefault();go(i+1,true)}if(e.key==='ArrowLeft'){e.preventDefault();go(i-1,true)}})});
 if(auto){card.addEventListener('focusin',()=>{hold=true;clearTimeout(tm);$$('b',root).forEach(b=>b.classList.remove('run'))});new IntersectionObserver(es=>{seen=es[0].isIntersecting;if(seen)go(i);else{clearTimeout(tm);$$('b',root).forEach(b=>b.classList.remove('run'))}},{threshold:.3}).observe(card)}};
tabset($('.tabcard'),true);tabset($('.linkcard'),false);
/* close: pictures follow the pointer, each a little later than the one before */
const cs=$('#close'),tr=$('.trail'),trs=$$('.tr');if(cs&&trs.length&&!still&&matchMedia('(hover:hover)').matches){let mx=0,my=0,on=false,id=0;const ps=trs.map(()=>[0,0]);const off=[[-150,-130],[-70,-170],[10,-120],[80,-60],[-110,-40]];
 const loop=()=>{trs.forEach((t,k)=>{const p=ps[k],f=.2-k*.03;p[0]+=(mx+off[k][0]-p[0])*f;p[1]+=(my+off[k][1]-p[1])*f;t.style.transform=`translate(${p[0]}px,${p[1]}px)`});if(on)id=requestAnimationFrame(loop)};
 cs.addEventListener('pointermove',e=>{const r=cs.getBoundingClientRect();mx=e.clientX-r.left;my=e.clientY-r.top;if(!on){on=true;ps.forEach(p=>{p[0]=mx;p[1]=my});tr.classList.add('on');loop()}});cs.addEventListener('pointerleave',()=>{on=false;tr.classList.remove('on');cancelAnimationFrame(id)})}
/* nothing runs off screen: the word rows stand still and films pause until they are back in view */
if(band&&'IntersectionObserver' in window)new IntersectionObserver(es=>band.classList.toggle('idle',!es[0].isIntersecting)).observe(band);
if('IntersectionObserver' in window){const vo=new IntersectionObserver(es=>es.forEach(x=>{const v=x.target;if(x.isIntersecting){if(!still&&v.dataset.auto!==undefined)v.play().catch(()=>{})}else v.pause()}));$$('video').forEach(v=>vo.observe(v))}
/* the link card rises 40px and fades in over the first quarter of its entry, tied to the scroll (set from the scroll
   handler, not a scroll-timeline animation, so nothing is left running while the card is elsewhere) */
const rs=$('.rise'),rc=rs&&rs.parentElement;const risePaint=()=>{if(!rs||still)return;const r=rc.getBoundingClientRect(),vh=innerHeight;if(r.top>vh+200||r.bottom<-200)return;const k=cl((vh-r.top)/(r.height*.25));rs.style.opacity=k<1?k:'';rs.style.transform=k<1?`translateY(${(40*(1-k)).toFixed(1)}px)`:''};
let tick=false;addEventListener('scroll',()=>{if(tick)return;tick=true;requestAnimationFrame(()=>{tick=false;head();paint();bandPaint();risePaint()})},{passive:true});
let rt=0;addEventListener('resize',()=>{clearTimeout(rt);rt=setTimeout(()=>{hw.length&&lines(hw);measure();bandPaint()},120)});
measure();bandPaint();risePaint();if(D.fonts&&D.fonts.ready)D.fonts.ready.then(()=>{hw.length&&lines(hw);measure();bandPaint()});addEventListener('load',()=>{measure();bandPaint()});
})();
'''


def render(d: dict) -> str:
    c = colours(d.get('palette') or {})
    b = d.get('brand') or {}
    hero = d.get('hero') or {}
    v = (f'--g:{c["G"]};--i:{c["I"]};--a:{c["A"]};--card:{c["card"]};--chip:{c["chip"]};--ln:{c["line"]};--mu:{c["muted"]};--tone:{c["tone"]};'
         f'--ona:{c["onA"]};--soft:{c["soft"]};--deep:{c["deep"]};--ond:{c["on_deep"]};--hov:{c["hov"]};--top:{129 if hero.get("note") else 80}px')
    body = ''.join(f(d, c) for f in (s_header, s_hero, s_steps, s_links, s_statement, s_features, s_plans, s_figures, s_faq, s_close, s_foot))
    title = ' — '.join(x for x in (b.get('name'), hero.get('title')) if x)
    fam = FONT.replace(' ', '+')
    return f'''<!doctype html><html lang="{e(d.get("lang") or "en")}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(hero.get("text"))}"><meta name="theme-color" content="{c["G"]}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family={fam}:wght@300;400;500&display=swap" rel="stylesheet">
<style>:root{{{v}}}{CSS.replace("FONT", FONT)}</style></head><body>
{body}
<script>{JS}</script></body></html>'''
