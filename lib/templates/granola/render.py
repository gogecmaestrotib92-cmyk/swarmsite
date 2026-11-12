"""granola/render.py — one pure function: render(d) -> a complete page.
The build (order, grid, measures, type scale, motion) was measured on the reference at 1440 and 390 (see NOTES.md).
Nothing here is the reference's code, words, pictures or faces; nothing is decided per client except what the data says."""
import html
import math

SERIF = "'Besley', 'Rockwell', Georgia, serif"          # stand-in for the reference's slab (OFL)
SANS = "'Geist', 'Helvetica Neue', Arial, sans-serif"   # stand-in for the reference's grotesque (OFL)


# ---------- colour: the client's palette put into the reference's light/dark/accent relations ----------
def _rgb(h):
    h = h.lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _hex(c):
    return '#%02x%02x%02x' % tuple(max(0, min(255, round(v))) for v in c)


def _mix(a, b, t):
    a, b = _rgb(a), _rgb(b)
    return _hex(tuple(a[i] + (b[i] - a[i]) * t for i in range(3)))


def _lum(h):
    def f(v):
        v /= 255
        return v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4
    r, g, b = _rgb(h)
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b)


def _con(a, b):
    la, lb = _lum(a), _lum(b)
    return (max(la, lb) + .05) / (min(la, lb) + .05)


def _on(bg, *cands):
    return max(cands, key=lambda c: _con(bg, c))


def _muted(fg, bg):
    """secondary text: the reference's grey sits near 4.9:1 on its ground; never below 4.6:1 here."""
    for t in (.38, .3, .22, .14, .07, 0):
        c = _mix(fg, bg, t)
        if _con(c, bg) >= 4.6:
            return c
    return fg


# ---------- small helpers ----------
def e(s):
    return html.escape(str(s or ''), quote=True)


def m(p):
    return '../../' + p if p and not p.startswith(('http:', 'https:', 'data:', '../')) else (p or '')


def img(o, cls='', lazy=True):
    w, h = o.get('w'), o.get('h')
    dim = f' width="{w}" height="{h}" style="aspect-ratio:{w}/{h}"' if w and h else ''
    return (f'<img class="{cls}" src="{e(m(o.get("src")))}" alt="{e(o.get("alt"))}"{dim}'
            f'{" loading=lazy" if lazy else ""} decoding="async">')


def window(inner, cls=''):
    return f'<div class="win {cls}"><div class="bar" aria-hidden="true"><i></i><i></i><i></i></div>{inner}</div>'


def btn(c, kind='dark', extra=''):
    if not c or not c.get('t'):
        return ''
    return f'<a class="btn {kind} {extra}" href="{e(c.get("h") or "#")}">{e(c["t"])}</a>'


def big(s):
    n = len(s or '')
    return 'b1' if n <= 24 else 'b2' if n <= 38 else 'b3'


def chunks(items, k):
    """split items into k runs as even as possible, longer runs last"""
    k = max(1, min(k, len(items)))
    base, rest = divmod(len(items), k)
    out, i = [], 0
    for j in range(k):
        n = base + (1 if j >= k - rest else 0)
        out.append(items[i:i + n])
        i += n
    return out


def render(d):
    g = d.get
    brand, pal, hero = g('brand') or {}, g('palette') or {}, g('hero') or {}
    media = g('media') or {}
    screens, phones, photos, video = media.get('screens') or [], media.get('phones') or [], media.get('photos') or [], media.get('video')
    G, I, A = pal.get('ground', '#ffffff'), pal.get('ink', '#292929'), pal.get('accent', '#5b6f00')
    light = _lum(G) > .4
    surface = _mix(G, I, .045)
    card = _mix(G, '#ffffff', .55) if light else _mix(G, I, .09)
    stroke = _mix(G, I, .17)
    muted = _muted(I, G)
    on_a = _on(A, I, G)
    a_hover = _mix(A, on_a, .16)
    P = [x for x in (pal.get('extra') or []) if _con(x, G) >= 1.15] or [_mix(G, I, .12)]
    grey = _mix(G, I, .14)
    dims = {o['src']: o for o in screens + phones + photos if o.get('src')}
    # made pictures (CONTRACT "Made pictures"): picked by kind and index, wrapping round; absent kind -> plain palette ground
    made = media.get('made') or {}
    land, blur, sheet = made.get('land') or [], made.get('blur') or [], made.get('sheet') or []

    def pick(kind, i):
        return kind[i % len(kind)] if kind else None

    def ground(o, slot, fallback, lazy=True, pos=''):
        """attributes + inner picture for a slot: the made picture as cover ground, or the plain palette colour"""
        if not o or not o.get('src'):
            return f' data-slot="{slot}" style="background:{fallback}"', ''
        w, h = o.get('w'), o.get('h')
        dim = f' width="{w}" height="{h}"' if w and h else ''
        ps = f' style="object-position:{pos}"' if pos else ''
        return (f' data-slot="{slot}" style="background:{o.get("mean") or fallback}"',
                f'<img class="bgi" src="{e(m(o["src"]))}" alt=""{dim}{ps}'
                f'{" loading=lazy" if lazy else ""} decoding="async">')

    name = brand.get('name') or ''
    logo = (f'<img class="logo" src="{e(m(brand["logo"]))}" alt="{e(name)}">' if brand.get('logo') else '') + \
           ('' if brand.get('logo') and brand.get('logo_wordmark') else f'<span>{e(name)}</span>')
    nav, signin, cta = g('nav') or [], g('signin'), g('cta')
    short_cta = bool(cta and len(cta.get('t', '')) <= 12)

    # ---------- header ----------
    links = ''.join(f'<a href="{e(n.get("h"))}">{e(n.get("t"))}</a>' for n in nav)
    head = f'''<header class="hd" id="hd"><div class="pill">
<a class="brand" href="{e(brand.get('home') or '#')}">{logo}</a>
{f'<nav class="links" aria-label="Main">{links}</nav>' if links else ''}
<div class="acts">{btn(signin, 'line', 'sm sign') if signin else ''}{btn(cta, 'soft', 'sm go' + ('' if short_cta else ' long')) if cta else ''}
<button class="burger" id="burger" aria-expanded="false" aria-controls="menu" aria-label="Menu"><i></i><i></i></button></div>
</div>
<div class="menu" id="menu" hidden>{links}{f'<a href="{e(signin.get("h"))}">{e(signin.get("t"))}</a>' if signin else ''}{btn(cta, 'dark') if cta else ''}</div>
</header>'''

    # ---------- opening: headline left, the product window standing on three grounds right; pinned through screen two ----------
    hm = screens[0] if screens else None
    if hm:
        demo_inner = window(img(hm, lazy=False))
        ar = hm['w'] / hm['h'] if hm.get('w') and hm.get('h') else 1.6
    elif video:
        demo_inner = window(_video(video))
        ar = video['w'] / video['h'] if video.get('w') and video.get('h') else 1.6
    else:
        demo_inner, ar = '', 1.6
    demo_w = 460 if ar >= 1.3 else 400 if ar >= .9 else 330
    fa = ground(pick(sheet, 0) if sheet else None, 'open-back', P[0], lazy=False)
    fb = ground(sheet[1] if len(sheet) > 1 else None, 'open-left', A, lazy=False, pos='0 0')
    fc = ground(sheet[2] if len(sheet) > 2 else None, 'open-low', grey, lazy=False)
    pin = f'''<div class="pin" aria-hidden="false"><div class="pin-in"><div class="pin-col"><div class="demo" id="demo" style="--dw:{demo_w}px">
<div class="fl fl-c"{fc[0]}>{fc[1]}</div><div class="fl fl-a"{fa[0]}>{fa[1]}</div><div class="fl fl-b"{fb[0]}>{fb[1]}</div>
{demo_inner}</div></div></div></div>''' if demo_inner else ''
    lines = ''.join(f'<p>{e(t)}</p>' for t in (hero.get('text'), hero.get('text2')) if t)
    note = f'<p class="note"><svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><path d="M3 8.5l3.2 3.2L13 5" fill="none" stroke="currentColor" stroke-width="1.4"/></svg>{e(hero["note"])}</p>' if hero.get('note') else ''
    sec_hero = f'''<section class="hero"><div class="wrap"><div class="hero-txt">
<h1>{e(hero.get('title') or name)}</h1>
{f'<div class="lede">{lines}</div>' if lines else ''}
<div class="hero-cta">{btn(hero.get('primary') or cta, 'accent')}{note}</div>
</div></div></section>'''

    trust = g('trust') or []
    s2 = ''
    if hero.get('kicker') or trust:
        rows = ''.join(f'<p class="rule-row">{e(t)}</p>' for t in trust)
        s2 = f'''<section class="s2{' dense' if len(trust) > 4 else ''}"><div class="s2-in">
{f'<h2>{e(hero["kicker"])}</h2>' if hero.get('kicker') else ''}
{f'<div class="rules" style="--n:{max(len(trust) + 1, 6)}"><div class="rule-rows">{rows}</div></div>' if rows else ''}
</div></section>'''
    pile = f'<div class="pile{" has-s2" if s2 else ""}{" has-pin" if pin else ""}">{sec_hero}{pin}{"<div class=travel></div>" if pin else ""}</div>{s2}'

    # ---------- the very large statement that slides under the inverse band; the band carries its text and the figures ----------
    st, figs = g('statement') or {}, g('figures') or []
    sec_state = ''
    if st.get('title'):
        t = st['title']
        nl = 1 if len(t) <= 28 else 2
        per = math.ceil(len(t) / nl) + (0 if nl == 1 else 3)
        cells = ''.join(f'<div class="fig"><b>{e(f.get("v"))}</b><span>{e(f.get("l"))}</span></div>' for f in figs)
        band = f'''<div class="inv band" id="band"><div class="wrap">
{f'<p class="band-lead">{e(st["text"])}</p>' if st.get('text') else ''}
{f'<div class="figs n{min(len(figs), 6)}">{cells}</div>' if cells else ''}
</div></div>''' if (st.get('text') or cells) else ''
        sec_state = f'''<section class="state"><div class="state-top"><h2 id="huge" style="--per:{per};--perm:{min(per, 13)}">{e(t)}</h2></div>{band}</section>'''

    # ---------- steps: a sticky list of labels left, each step right with one square picture ----------
    steps = g('steps') or {}
    sec_steps = ''
    its = steps.get('items') or []
    if its:
        labels = ''.join(f'<button type="button" data-i="{i}"{" class=on" if i == 0 else ""}>{e(it.get("k") or it.get("title"))}<i><b></b></i></button>' for i, it in enumerate(its))
        body = ''
        for i, it in enumerate(its):
            pic = ''
            if it.get('img'):
                o = dict(dims.get(it['img']) or {}, src=it['img'])
                o.setdefault('alt', it.get('title'))
                shape = it.get('shape') or ('phone' if o.get('h', 1) > o.get('w', 1) * 1.6 else 'book' if o.get('h', 1) > o.get('w', 1) else 'screen')
                inner = window(img(o)) if shape == 'screen' else f'<div class="dev {e(shape)}">{img(o)}</div>'
                sa, si = ground(pick([land[j] for j in (3, 4, 2) if j < len(land)], i), f'step-{i}', P[i % len(P)])
                pic = f'<div class="sq"{sa}>{si}<div class="sq-in" data-drift>{inner}</div></div>'
            c = it.get('cta') or {}
            body += f'''<div class="step" id="step-{i}" data-step="{i}">
{f'<p class="step-k">{e(it["k"])}</p>' if it.get('k') else ''}<h3>{e(it.get('title'))}</h3>
{f'<p class="step-p">{e(it["text"])}</p>' if it.get('text') else ''}
{f'<a class="tl" href="{e(c.get("h"))}">{e(c["t"])}</a>' if c.get('t') else ''}{pic}</div>'''
        intro = f'''<div class="steps-intro"><div class="wrap two"><div></div><div><h2>{e(steps["title"])}</h2>{f'<p>{e(steps["text"])}</p>' if steps.get('text') else ''}</div></div></div>''' if steps.get('title') else ''
        sec_steps = f'''<section class="steps">{intro}<div class="wrap two"><div class="steps-nav-col"><div class="steps-nav" id="stepsnav">{labels}</div></div><div class="steps-body">{body}</div></div></section>'''

    # ---------- plans: the coloured band — a very large heading left, white cards right ----------
    plans = g('plans') or {}
    sec_plans = ''
    if plans.get('items'):
        cards = ''
        for p in plans['items']:
            rows = ''.join(f'<li>{e(r)}</li>' for r in (p.get('rows') or []))
            cards += f'''<div class="plan"><div class="plan-top"><h3>{e(p.get('name'))}</h3><p class="price"><b>{e(p.get('price'))}</b>{f'<span>{e(p["per"])}</span>' if p.get('per') else ''}</p></div>
{f'<p class="plan-line">{e(p["line"])}</p>' if p.get('line') else ''}{f'<ul>{rows}</ul>' if rows else ''}
{btn(p.get('cta'), 'dark' if p.get('marked') else 'line')}</div>'''
        sec_plans = f'''<section class="plans" style="--bg:{A};--fg:{on_a}"><div class="wrap plans-grid"><div class="plans-l"><div class="plans-stick">
{f'<h2 class="xl {big(plans.get("title"))}">{e(plans["title"])}</h2>' if plans.get('title') else ''}
{f'<p class="plans-t">{e(plans["text"])}</p>' if plans.get('text') else ''}{f'<p class="plans-n">{e(plans["note"])}</p>' if plans.get('note') else ''}
</div></div><div class="plans-r">{cards}</div></div></section>'''

    # ---------- quotes / logos: the reference's dark bands; written only when the data has them ----------
    quotes, logos = g('quotes') or [], g('logos') or []
    sec_quotes = ''
    if quotes:
        qs = ''
        for q in quotes:
            q = q if isinstance(q, dict) else {'text': q}
            qs += f'''<figure class="q"><blockquote>{e(q.get('text') or q.get('q'))}</blockquote>{f'<figcaption><span>{e(q.get("name"))}</span><span>{e(q.get("role"))}</span></figcaption>' if q.get('name') else ''}</figure>'''
        sec_quotes = f'<section class="inv quotes"><div class="q-row">{qs}</div></section>'
    sec_logos = ''
    if logos:
        ls = ''.join((f'<div class="lg">{img(l)}</div>' if isinstance(l, dict) else f'<div class="lg"><span>{e(l)}</span></div>') for l in logos)
        sec_logos = f'<section class="inv logos"><div class="wrap"><div class="lg-grid">{ls}</div></div></section>'

    # ---------- features: very large heading, then label | description rows under hairlines, each run closed by one large picture ----------
    feats = g('features') or {}
    sec_feats = ''
    fi = feats.get('items') or []
    rest = screens[1:] if hm else screens
    used = {it.get('img') for it in its}
    spare = [o for o in phones + photos if o.get('src') not in used]
    if feats.get('title') or fi:
        def row(it):
            return f'<div class="row"><h3>{e(it.get("t"))}</h3><p>{e(it.get("d"))}</p></div>'

        wide_land = [land[j] for j in (5, 1, 0) if j < len(land)]

        def pic(o, i):
            pa, pi = ground(pick(wide_land, i), f'feat-{i}', P[(i + 1) % len(P)])
            return f'<div class="pic"{pa}>{pi}{window(img(o))}</div>'
        groups = ''
        if fi and rest:
            for i, run in enumerate(chunks(fi, len(rest))):
                groups += f'<div class="grp">{"".join(row(r) for r in run)}{pic(rest[i], i)}</div>'
            for j in range(len(chunks(fi, len(rest))), len(rest)):
                groups += f'<div class="grp">{pic(rest[j], j)}</div>'
        elif fi:
            groups = f'<div class="grp">{"".join(row(r) for r in fi)}</div>'
        else:
            groups = ''.join(f'<div class="grp">{pic(o, i)}</div>' for i, o in enumerate(rest))
        extra_pic = ''
        if video and hm:
            left = ''
            if spare:
                o = spare.pop(0)
                la, li = ground(pick(blur, 0) or (land[3] if len(land) > 3 else None), 'split-left', P[0])
                left = f'<div class="pic side"{la}>{li}<div class="dev {"phone" if o["h"] > o["w"] * 1.6 else "book"}">{img(o)}</div></div>'
            # land[1], unless a feature picture of this section already shows it: then the first land the section has not used
            taken = {(5, 1, 0)[k % 3] for k in range(len(rest))} if len(land) > 5 else set()
            free = [j for j in (1, 4, 2, 3) if j < len(land) and j not in taken]
            ra, ri = ground(land[free[0]] if free else (land[1] if len(land) > 1 else None), 'split-right', grey)
            extra_pic += f'<div class="split{"" if left else " one"}">{left}<div class="pic"{ra}>{ri}{window(_video(video))}</div></div>'
        if spare:
            devs = ''.join(f'<div class="dev {"phone" if o.get("h", 1) > o.get("w", 1) * 1.6 else "book"}">{img(o)}</div>' for o in spare[:5])
            ha, hi = ground(pick(wide_land, len(rest)), 'shelf', P[-1] if len(P) > 1 else grey)
            extra_pic += f'<div class="pic shelf n{len(spare[:5])}"{ha}>{hi}{devs}</div>'
        if extra_pic:
            groups += f'<div class="grp">{extra_pic}</div>'
        sec_feats = f'''<section class="feats"><div class="wide">
{f'<h2 class="xl {big(feats.get("title"))}">{e(feats["title"])}</h2>' if feats.get('title') else ''}
{f'<p class="feats-t">{e(feats["text"])}</p>' if feats.get('text') else ''}
<div class="feats-cta">{btn(cta, 'dark')}</div>
<div class="grps">{groups}</div></div></section>'''

    # ---------- questions: the surface band — very large heading, rows under hairlines ----------
    faq = g('faq') or {}
    sec_faq = ''
    if faq.get('items'):
        rows = ''.join(f'<div class="row qa"><h3>{e(q.get("q"))}</h3><p>{e(q.get("a"))}</p></div>' for q in faq['items'])
        sec_faq = f'''<section class="faq"><div class="wrap">{f'<h2 class="xl {big(faq.get("title"))}">{e(faq["title"])}</h2>' if faq.get('title') else ''}<div class="faq-rows">{rows}</div></div></section>'''

    # ---------- close: a window-shaped card standing on full-width grounds ----------
    close = g('close') or {}
    sec_close = ''
    if close.get('title'):
        ca, ci = ground(sheet[1] if len(sheet) > 1 else None, 'close-left', A, pos='0 0')
        cb, cj = ground(pick(sheet, 0) if sheet else None, 'close-right', P[0])
        sec_close = f'''<section class="close"><div class="close-bg" aria-hidden="true"><i{ca}>{ci}</i><i{cb}>{cj}</i></div>
<div class="close-card"><div class="bar" aria-hidden="true"><i></i><i></i><i></i></div>
<h2 class="{big(close['title'])}">{e(close['title'])}</h2>{f'<p>{e(close["text"])}</p>' if close.get('text') else ''}
<div class="close-btns">{btn(close.get('cta'), 'dark')}{btn(hero.get('secondary'), 'line')}</div></div></section>'''

    # ---------- foot: link rows, small print, the name very large ----------
    foot, lk = g('foot') or {}, g('links') or []
    lrows = ''
    for l in lk:
        desc = '<span>%s</span>' % e(l.get('d')) if l.get('d') else ''
        lrows += '<a class="lrow" href="%s"><b>%s</b>%s</a>' % (e(l.get('h')), e(l.get('t')), desc)
    col1 = ''.join(f'<a href="{e(n.get("h"))}">{e(n.get("t"))}</a>' for n in nav)
    col2 = ''.join(f'<a href="{e(n.get("h"))}">{e(n.get("t"))}</a>' for n in ([signin] if signin else []) + (foot.get('links') or []) if n)
    sec_foot = f'''<footer class="ft"><div class="wrap">
<div class="ft-top">{f'<div class="lrows">{lrows}</div>' if lrows else '<div></div>'}<div class="ft-cols">{f'<div>{col1}</div>' if col1 else ''}{f'<div>{col2}</div>' if col2 else ''}</div></div>
<div class="ft-low">{f'<p>{e(foot["text"])}</p>' if foot.get('text') else '<span></span>'}{f'<p class="legal">{e(foot["legal"])}</p>' if foot.get('legal') else ''}</div>
{f'<div class="mark" id="mark" aria-hidden="true" style="--n:{max(len(name), 3)}"><span>{e(name)}</span></div>' if name else ''}
</div></footer>'''

    css = CSS.replace('__SERIF__', SERIF).replace('__SANS__', SANS)
    for k, v in {'G': G, 'I': I, 'A': A, 'ONA': on_a, 'AH': a_hover, 'SURF': surface, 'CARD': card, 'STROKE': stroke,
                 'MUTED': muted, 'IMUTED': _muted(G, I), 'AMUTED': _muted(on_a, A), 'SHADOW': '0,0,0' if light else '0,0,0',
                 'SOFT': _mix(G, I, .07)}.items():
        css = css.replace('__%s__' % k, v)
    title = f'{name} — {hero.get("title")}' if hero.get('title') else name
    return f'''<!doctype html>
<html lang="{e(g('lang') or 'en')}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
{f'<meta name="description" content="{e(hero.get("text"))}">' if hero.get('text') else ''}
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Besley:wght@400&family=Geist:wght@400;500;700&display=swap" rel="stylesheet">
<style>{css}</style>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
{head}
<main id="main">
{pile}
{sec_state}
{sec_logos}
{sec_steps}
{sec_plans}
{sec_quotes}
{sec_feats}
{sec_faq}
{sec_close}
</main>
{sec_foot}
<script>{JS}</script>
</body>
</html>'''


def _video(v):
    w, h = v.get('w'), v.get('h')
    dim = ' width="%s" height="%s" style="aspect-ratio:%s/%s"' % (w, h, w, h) if w and h else ''
    poster = ' poster="%s"' % e(m(v.get('poster'))) if v.get('poster') else ''
    return '<video src="%s"%s%s muted loop playsinline preload="metadata" data-auto aria-label="%s"></video>' % (
        e(m(v.get('src'))), poster, dim, e(v.get('alt')))


CSS = r'''
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;overflow-x:clip}
body{margin:0;background:__G__;color:__I__;font:400 16px/1.5 __SANS__;-webkit-font-smoothing:antialiased;overflow-x:clip;--bg:__G__;--fg:__I__;--mut:__MUTED__;--line:__STROKE__}
h1,h2,h3,p,ul,figure,blockquote{margin:0;padding:0}
ul{list-style:none}
img,video{display:block;max-width:100%}
a{color:inherit;text-decoration:none}
button{font:inherit;color:inherit;background:none;border:0;padding:0;cursor:pointer}
:focus-visible{outline:2px solid var(--fg);outline-offset:3px;border-radius:4px}
.skip{position:absolute;left:16px;top:-80px;background:__I__;color:__G__;padding:10px 16px;border-radius:999px;z-index:100}
.skip:focus{top:12px}
h1,h2,h3,.serif{font-family:__SERIF__;font-weight:400}
.wrap{width:100%;max-width:1280px;margin:0 auto;padding:0 40px}
.wide{width:100%;max-width:1280px;margin:0 auto}
.two{display:grid;grid-template-columns:1fr 1fr}
.inv{--bg:__I__;--fg:__G__;--mut:__IMUTED__;--line:color-mix(in srgb,__G__ 22%,__I__);background:var(--bg);color:var(--fg)}

/* buttons — 56 high, full radius, 16px; hover is a colour change only (measured) */
.btn{display:inline-flex;align-items:center;justify-content:center;height:56px;padding:0 24px;border-radius:999px;font:500 16px/1.13 __SANS__;letter-spacing:.01em;white-space:nowrap;border:1px solid transparent;transition:background-color .3s cubic-bezier(0,0,.2,1),color .3s cubic-bezier(0,0,.2,1),border-color .3s cubic-bezier(0,0,.2,1)}
.btn.accent{background:__A__;color:__ONA__}.btn.accent:hover{background:__AH__}
.btn.dark{background:var(--fg);color:var(--bg)}.btn.dark:hover{background:color-mix(in srgb,var(--fg) 84%,var(--bg))}
.btn.line{border-color:var(--fg);color:var(--fg)}.btn.line:hover{background:color-mix(in srgb,var(--fg) 8%,transparent)}
.btn.soft{background:color-mix(in srgb,var(--fg) 7%,transparent)}.btn.soft:hover{background:color-mix(in srgb,var(--fg) 13%,transparent)}
.btn.sm{height:40px;padding:0 13px;font-size:14px;font-weight:400;line-height:1.71}
.btn.sm.line{border-color:color-mix(in srgb,var(--fg) 22%,transparent);height:38px}
.tl{display:inline-block;margin-top:12px;text-decoration:underline;text-underline-offset:4px;text-decoration-thickness:1px}
.tl:hover{text-decoration-thickness:2px}

/* header — fixed 8px from the top, 56 high; on scroll it becomes a bordered pill with a soft shadow (0.3s ease-out) */
.hd{position:fixed;left:0;right:0;top:8px;z-index:50;padding:0 16px}
.pill{position:relative;display:flex;align-items:center;justify-content:space-between;height:56px;max-width:1217px;margin:0 auto;padding:0 8px;border:.5px solid transparent;border-radius:999px;transition:background-color .3s ease-out,border-color .3s ease-out,box-shadow .3s ease-out}
.hd.on .pill{background:__G__;border-color:__STROKE__;box-shadow:0 1px 2px rgba(0,0,0,.04),0 6px 20px rgba(0,0,0,.06)}
.brand{display:flex;align-items:center;gap:8px;font:500 19px/1 __SANS__;letter-spacing:-.02em;padding:0 8px;min-width:0}
.brand .logo{height:26px;width:auto}
.links{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);display:flex}
.links a{padding:6px 12px;font-size:14px;line-height:1.71;letter-spacing:.01em;border-radius:999px;transition:background-color .2s cubic-bezier(.4,0,.2,1)}
.links a:hover{background:color-mix(in srgb,__I__ 6%,transparent)}
.acts{display:flex;align-items:center;gap:4px}
.hd.on .go{background:__A__;color:__ONA__}.hd.on .go:hover{background:__AH__}
.burger{display:none;width:40px;height:40px;position:relative}
.burger i{position:absolute;left:11px;right:11px;height:1.5px;background:currentColor;top:16px;transition:transform .2s}
.burger i+i{top:23px}
.burger[aria-expanded=true] i{transform:translateY(3.5px) rotate(45deg)}.burger[aria-expanded=true] i+i{transform:translateY(-3.5px) rotate(-45deg)}
.menu{margin:8px 0 0;background:__G__;border:1px solid __STROKE__;border-radius:20px;padding:12px 16px 16px;box-shadow:0 6px 20px rgba(0,0,0,.08)}
.menu[hidden]{display:none}
.menu a:not(.btn){display:block;padding:13px 4px;border-bottom:1px solid __STROKE__;font-size:16px}
.menu .btn{width:100%;margin-top:16px;height:48px}

/* opening — two screens tall; the window is pinned 48px from the top through both */
.pile{position:relative;display:grid;grid-template-columns:minmax(0,1fr)}
.hero{grid-area:1/1;min-height:100vh;display:flex;align-items:center;padding:120px 0 0}
.hero .wrap{display:grid;grid-template-columns:720px 480px;gap:32px}
.hero-txt{display:flex;flex-direction:column;align-items:flex-start;gap:32px;max-width:590px}
h1{font-size:86.4px;line-height:.93;letter-spacing:-.02em;text-wrap:balance}
.lede p{font-size:20px;line-height:28px;max-width:30em}
.hero-cta{display:flex;flex-direction:column;align-items:flex-start;gap:24px}
.note{display:flex;align-items:center;gap:8px;font-size:13px;line-height:24px;letter-spacing:.01em;color:var(--mut)}
.travel{grid-area:2/1;height:100vh;display:none}
.pile.has-s2 .travel{display:block}
.pin{grid-area:1/1/3/2;position:sticky;z-index:2;top:48px;height:100vh;align-self:start;pointer-events:none;overflow:hidden;padding-top:40px}
.pin-in{height:100%;max-width:1280px;margin:0 auto;padding:0 40px;display:grid;grid-template-columns:1fr 1fr}
.pin-col{grid-column:2;display:flex;align-items:center;justify-content:center}
.demo{position:relative;width:var(--dw);transform:translate(0,-6vh) scale(1.2);will-change:transform}
.fl{position:absolute;left:50%;top:50%;border-radius:2px;overflow:hidden;will-change:transform,opacity}
.bgi{position:absolute;inset:0;width:100%;height:100%;max-width:none;object-fit:cover}
.demo .win{position:relative}
.fl-a{width:441px;height:552px;margin:-276px 0 0 -220px;transform:translate(24%,-6%)}
.fl-b{width:315px;height:572px;margin:-286px 0 0 -157px;transform:translate(-35%,10%)}
.fl-c{width:384px;height:682px;margin:-341px 0 0 -192px;transform:translate(23%,21%)}
.win{position:relative;background:__CARD__;border-radius:12px;overflow:hidden;box-shadow:0 0 0 1px color-mix(in srgb,__I__ 10%,transparent),0 20px 25px -5px rgba(0,0,0,.1),0 8px 10px -6px rgba(0,0,0,.1)}
.win img,.win video{width:100%;height:auto}
.bar{display:flex;align-items:center;gap:6.5px;height:44px;padding-left:15.5px}
.bar i{width:12px;height:12px;border-radius:50%;background:color-mix(in srgb,__I__ 18%,__CARD__)}
.win .bar{height:36px;padding-left:13px}.win .bar i{width:10px;height:10px}

/* screen two — heading, then facts on a ruled sheet (80px lines), dashed edges on the container */
/* it is drawn up under the pinned window only when there is one: without a screen or film it follows the opening */
.s2{height:100vh;min-height:760px}.pile.has-pin+.s2{margin-top:-100vh}
.s2-in{height:100%;max-width:1280px;margin:0 auto;border-left:1px dashed __STROKE__;border-right:1px dashed __STROKE__;padding-top:234px;--rh:80px}
.s2.dense .s2-in{--rh:64px}
.s2 h2{font-size:48px;line-height:1;padding:0 40px;max-width:680px;text-wrap:balance;margin-bottom:96px}
.rules{height:calc(var(--n)*var(--rh) + 1px);background:repeating-linear-gradient(to bottom,__STROKE__ 0 1px,transparent 1px var(--rh))}
.rule-row{display:flex;align-items:center;height:var(--rh);padding:0 40px;max-width:640px;font-size:14px;line-height:1.35;letter-spacing:.01em}

/* statement — very large, centred; it slides down under the inverse band as the band rises */
.state{position:relative;overflow:clip}
.state-top{display:flex;justify-content:center;padding:24px 40px}
#huge{font-size:min(160px,calc((100vw - 120px)/(var(--per)*.53)));line-height:1;letter-spacing:-.015em;text-align:center;text-wrap:balance;max-width:1320px;will-change:transform}
.band{position:relative;z-index:2;padding:16px 0 48px}
.band-lead{font:400 20px/1.4 __SERIF__;letter-spacing:.01em;text-align:center;max-width:39em;margin:0 auto;padding-top:48px;text-wrap:pretty}
.figs{display:grid;grid-template-columns:repeat(4,1fr);margin-top:32px}
.figs.n1{grid-template-columns:1fr}.figs.n2{grid-template-columns:repeat(2,1fr)}.figs.n3,.figs.n5,.figs.n6{grid-template-columns:repeat(3,1fr)}
.fig{position:relative;min-height:200px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;padding:24px 20px;text-align:center}
.fig b{font:400 56px/1 __SERIF__;letter-spacing:-.02em}
.fig span{font-size:14px;line-height:1.4;color:var(--mut);max-width:22em}
.fig+.fig::before{content:"";position:absolute;left:-7px;top:50%;width:15px;height:15px;transform:translateY(-50%);background:linear-gradient(var(--mut),var(--mut)) center/15px 1px no-repeat,linear-gradient(var(--mut),var(--mut)) center/1px 15px no-repeat;opacity:.7}

/* steps — intro heading in the right half; sticky label list left (96px), steps right, 96px apart */
.steps-intro{padding:160px 0}
.steps-intro h2{font-size:48px;line-height:1;letter-spacing:-.015em;text-wrap:balance}
.steps-intro p{margin-top:24px;max-width:448px}
.steps-nav{position:sticky;top:96px;display:flex;flex-direction:column;align-items:flex-start;gap:16px;padding:48px 0;max-width:320px}
.steps-nav button{position:relative;min-width:174px;text-align:left;font-size:14px;line-height:18px;letter-spacing:.01em;padding-bottom:7px;color:var(--mut);transition:color .5s cubic-bezier(.4,0,.2,1)}
.steps-nav button.on,.steps-nav button:hover{color:__I__}
.steps-nav i{position:absolute;left:0;right:0;bottom:0;height:1px;background:__STROKE__}
.steps-nav b{position:absolute;left:0;right:0;bottom:0;height:2px;background:__I__;transform:scaleX(0);transform-origin:0 50%}
.steps-nav b.out{transform-origin:100% 50%;transition:transform .5s ease}
.steps-body{display:flex;flex-direction:column;gap:96px;padding:48px 0 48px}
.step{scroll-margin-top:96px}
.step-k{display:none}
.step h3{font-size:24px;line-height:1.05;letter-spacing:-.01em}
.step-p{margin-top:8px;max-width:448px}
.sq{position:relative;aspect-ratio:1;margin-top:24px;border-radius:16px;overflow:hidden}
.sq-in{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;will-change:transform}
.sq .win{width:86%}
.dev{position:relative;overflow:hidden;box-shadow:0 0 0 1px color-mix(in srgb,__I__ 12%,transparent),0 20px 25px -5px rgba(0,0,0,.18),0 8px 10px -6px rgba(0,0,0,.14);flex:none}
.dev img{height:100%;width:auto;max-width:none}
.dev.phone{border-radius:22px}.dev.book{border-radius:3px}
.sq .dev.phone{height:84%}.sq .dev.book{height:80%}

/* plans — the coloured band */
.plans{background:var(--bg);color:var(--fg);--mut:__AMUTED__;--line:color-mix(in srgb,var(--fg) 22%,var(--bg));padding:112px 0;margin-top:48px}
.plans-grid{display:grid;grid-template-columns:584px minmax(0,1fr);gap:32px}
.plans-stick{position:sticky;top:120px}
.xl{line-height:.97;letter-spacing:-.02em;text-wrap:balance;max-width:10.2em}
.xl.b1{font-size:108px}.xl.b2{font-size:88px}.xl.b3{font-size:72px}
.plans-t{margin-top:32px;font-size:20px;line-height:28px;max-width:26em}
.plans-n{margin-top:20px;font-size:14px;line-height:1.5;max-width:36em;color:var(--mut)}
.plans-r{display:flex;flex-direction:column;gap:16px}
.plan{--bg:__CARD__;--fg:__I__;--mut:__MUTED__;--line:__STROKE__;background:var(--bg);color:var(--fg);border-radius:28px;padding:32px;box-shadow:0 8px 12px -4px rgba(0,0,0,.05)}
.plan-top{display:flex;align-items:baseline;justify-content:space-between;gap:16px;flex-wrap:wrap}
.plan h3{font-size:24px;line-height:1.05;letter-spacing:-.01em}
.price{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}
.price b{font:400 56px/1 __SERIF__;letter-spacing:-.02em}
.price span{font-size:14px;color:var(--mut)}
.plan-line{margin-top:12px;font-size:16px}
.plan ul{margin-top:20px;border-bottom:1px solid var(--line)}
.plan li{padding:12px 0;border-top:1px solid var(--line);font-size:14px;line-height:1.4;letter-spacing:.01em}
.plan .btn{margin-top:24px;height:48px}

/* quotes and logos (only when the data has them) */
.quotes{padding:112px 0;overflow:hidden}
.q-row{display:flex;gap:24px;overflow-x:auto;padding:0 max(40px,calc((100vw - 1200px)/2));scroll-snap-type:x mandatory;scrollbar-width:none}
.q{flex:none;width:min(700px,84vw);min-height:440px;border:1px solid var(--fg);padding:36px 56px;display:flex;flex-direction:column;justify-content:space-between;gap:52px;scroll-snap-align:start}
.q blockquote{font:400 36px/1.1 __SERIF__}.q figcaption span{display:block}.q figcaption span+span{color:var(--mut)}
.logos{padding:16px 0 48px}.lg-grid{display:grid;grid-template-columns:repeat(6,1fr)}
.lg{height:200px;display:flex;align-items:center;justify-content:center;padding:0 12px}.lg img{max-height:26px;width:auto}

/* features — rows under hairlines (820 | 448), then one large picture standing whole on a plain ground */
.feats{padding:128px 40px}
.feats-t{margin-top:32px;font-size:20px;line-height:28px;max-width:34em}
.feats-cta{margin-top:40px}
.grps{margin-top:128px;display:flex;flex-direction:column;gap:124px}
.row{display:grid;grid-template-columns:minmax(0,820fr) minmax(0,448fr);gap:12px;border-top:1px solid var(--line);padding:16px 0 40px}
.row h3{font-size:32px;line-height:1.05;letter-spacing:-.01em;text-wrap:pretty;max-width:18em;padding-right:24px}
.row p{font-size:22px;line-height:1.35}
.row.qa p{font-size:17px;line-height:1.55}
.pic{position:relative;overflow:hidden;border-radius:4px;display:flex;align-items:center;justify-content:center;padding:56px 40px;min-height:527px}
.grp .row+.pic,.grp .row+.split{margin-top:0}
.pic .win{width:60%}
.split{display:grid;grid-template-columns:minmax(0,439fr) minmax(0,833fr);gap:8px}
.split.one{grid-template-columns:1fr}
.split .pic .win{width:74%}
.pic.side .dev{height:420px}
.split+.shelf,.pic+.split{margin-top:8px}
.shelf{gap:4%;flex-wrap:wrap}
.shelf .dev{height:400px}

/* questions — the surface band */
.faq{background:__SURF__;padding:128px 0}
.faq-rows{margin-top:128px}

/* close — a window-shaped card (768 wide, 28 radius) standing on full-width grounds, running off the foot of the band */
.close{position:relative;min-height:749px;padding-top:96px;display:flex;justify-content:center;align-items:flex-end;overflow:hidden}
.close-bg{position:absolute;inset:0;display:grid;grid-template-columns:38fr 62fr}
.close-bg i{position:relative;overflow:hidden}
.close-bg i+i .bgi{transform:scale(1.08)}
.close-card{position:relative;width:768px;max-width:calc(100% - 80px);min-height:653px;background:__SURF__;border-radius:28px 28px 0 0;padding:28px 48px 96px;box-shadow:0 4px 50px rgba(54,54,53,.25)}
.close-card .bar{padding-left:0;height:20px}
.close-card h2{margin-top:76px;line-height:.98;letter-spacing:-.01em;text-wrap:balance}
.close-card h2.b1{font-size:88px}.close-card h2.b2{font-size:72px}.close-card h2.b3{font-size:60px}
.close-card p{margin-top:40px;font-size:24px;line-height:32px;max-width:26em}
.close-btns{margin-top:40px;display:flex;gap:20px;flex-wrap:wrap}

/* foot */
.ft{padding:64px 0 48px;background:__G__}
.ft-top{display:grid;grid-template-columns:1fr 1fr;gap:32px}
.lrow{display:grid;grid-template-columns:200px 1fr;gap:16px;align-items:baseline;padding:12px 0;border-top:1px solid var(--line);max-width:520px}
.lrow b{font:400 24px/.95 __SERIF__}
.lrow span{font-size:14px;line-height:1.4;color:var(--mut)}
.lrow:hover b{text-decoration:underline;text-underline-offset:5px;text-decoration-thickness:1px}
.ft-cols{display:flex;justify-content:flex-end;gap:96px}
.ft-cols div{display:flex;flex-direction:column;min-width:120px}
.ft-cols a{font-size:14px;line-height:30px}
.ft-cols a:hover{text-decoration:underline;text-underline-offset:4px}
.ft-low{display:flex;justify-content:space-between;align-items:flex-end;gap:40px;margin-top:64px;font-size:14px;line-height:1.5;color:var(--mut)}
.ft-low p{max-width:56em}.ft-low .legal{white-space:nowrap}
.mark{margin-top:56px;overflow:hidden;line-height:.8;padding:.06em 0 .1em}
.mark span{display:inline-block;font:700 calc(min(1200px,100vw - 80px)/(var(--n)*.6))/.9 __SANS__;letter-spacing:-.05em;white-space:nowrap;transform-origin:0 50%}

@media (max-width:1439px) and (min-width:1024px){h1{font-size:5.4vw}.hero-txt{max-width:36vw}.hero .wrap{grid-template-columns:1fr 1fr}.demo{--dw:clamp(300px,34vw,520px)!important}.plans-grid{grid-template-columns:1fr 1fr}.xl.b1{font-size:7.5vw}.xl.b2{font-size:6.1vw}.xl.b3{font-size:5vw}}

/* the phone build (measured at 390) */
@media (max-width:1023px){
.wrap{padding:0 16px}
.hd{top:0;padding:0}
.pill{border-radius:0;border-width:0 0 .5px;padding:0 8px 0 8px;max-width:none}
.hd.on .pill{box-shadow:none}
.links,.sign,.go.long{display:none}
.burger{display:block}
.menu{margin:8px 8px 0}
.btn{height:48px}
.btn.sm{height:40px}
.pile{display:block}
.hero{min-height:0;display:block;padding:96px 0 24px}
.hero .wrap{display:block}
h1{font-size:48px}
.lede p{font-size:18px}
.travel{display:block!important;height:46vh}
.pin{position:sticky;top:96px;height:auto;padding:24px 0 72px;overflow:hidden}
.pin-in{display:block;padding:0 16px;height:auto}
.demo{width:min(100%,var(--dw));margin:0 auto;transform:none}
.fl-a{width:286px;height:358px;margin:-179px 0 0 -143px;transform:translate(45%,8%)}.fl-b{width:215px;height:390px;margin:-195px 0 0 -107px;transform:translate(-45%,8%)}.fl-c{width:215px;height:382px;margin:-191px 0 0 -107px;transform:translate(40%,10%)}
.s2,.pile.has-pin+.s2{margin-top:0;height:auto;min-height:0;padding:0 0 80px}
.s2-in{border:0;display:block;padding-top:0;--rh:80px}
.s2.dense .s2-in{--rh:72px}
.s2 h2{font-size:36px;line-height:1.11;padding:0 16px;margin-bottom:64px}
.rule-row{padding:0 32px 0 16px;font-size:16px}
.state-top{padding:20px 16px}
#huge{font-size:min(96px,calc((100vw - 32px)/(var(--perm)*.6)))}
.band-lead{font-size:18px}
.figs,.figs.n3,.figs.n5,.figs.n6{grid-template-columns:1fr 1fr}
.fig{min-height:150px;padding:20px 8px}.fig b{font-size:40px}
.fig+.fig::before{display:none}
.two{display:block}
.steps-intro{padding:96px 0 48px}
.steps-intro h2{font-size:36px;line-height:1.11}
.steps-nav-col{display:none}
.steps-body{gap:0;padding:0}
.step{padding:48px 0}
.step-k{display:block;font:400 16px/20px __SERIF__;color:var(--mut);margin-bottom:8px}
.plans{padding:80px 0}
.plans-grid{display:block}
.plans-stick{position:static}
.plans-r{margin-top:48px}
.xl.b1{font-size:60px}.xl.b2{font-size:52px}.xl.b3{font-size:44px}
.plan{padding:24px 20px}.price b{font-size:44px}
.plan .btn{width:100%}
.feats{padding:80px 16px}
.feats-cta .btn{width:100%}
.grps{margin-top:80px;gap:80px}
.row{grid-template-columns:1fr;padding:17px 0 32px}
.row h3{font-size:24px;padding:0}
.row p{font-size:16px}.row.qa p{font-size:16px}
.pic{padding:24px 16px;min-height:0}
.pic .win,.split .pic .win{width:100%}
.split{grid-template-columns:1fr}
.pic.side{padding:32px 16px}.pic.side .dev{height:360px}
.shelf{gap:16px;padding:28px 16px}
.shelf .dev{height:auto;width:calc(50% - 8px)}.shelf .dev img{width:100%;height:auto}
.faq{padding:80px 0}.faq-rows{margin-top:64px}
.close{min-height:0;padding-top:72px}
.close-card{max-width:calc(100% - 80px);min-height:0;padding:20px 24px 56px}
.close-card h2{margin-top:36px}
.close-card h2.b1,.close-card h2.b2,.close-card h2.b3{font-size:36px}
.close-card p{margin-top:24px;font-size:16px;line-height:24px}
.close-btns{flex-direction:column;gap:12px;margin-top:28px}.close-btns .btn{width:100%;white-space:normal;text-align:center}
.ft-top{display:block}
.lrow{grid-template-columns:1fr;gap:4px;max-width:none}
.ft-cols{justify-content:flex-start;gap:48px;margin-top:40px}
.ft-low{display:block;margin-top:40px}.ft-low .legal{margin-top:16px}
.mark{margin-top:40px}
.mark span{font-size:calc((100vw - 32px)/(var(--n)*.6))}
}
@media (prefers-reduced-motion:reduce){
*{transition-duration:.01ms!important;animation:none!important;scroll-behavior:auto!important}
.pin{position:relative;grid-area:1/1;top:0}
.demo,.fl{will-change:auto}
#huge,.sq-in{transform:none!important}
}
'''

JS = r'''
(function(){
var doc=document,root=doc.documentElement,reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
var hd=doc.getElementById('hd'),burger=doc.getElementById('burger'),menu=doc.getElementById('menu');
function clamp(v){return v<0?0:v>1?1:v}
function bez(x1,y1,x2,y2){var cx=3*x1,bx=3*(x2-x1)-cx,ax=1-cx-bx,cy=3*y1,by=3*(y2-y1)-cy,ay=1-cy-by;return function(x){var t=x,i,f,dv;for(i=0;i<8;i++){f=((ax*t+bx)*t+cx)*t-x;dv=(3*ax*t+2*bx)*t+cx;if(Math.abs(dv)<1e-6)break;t-=f/dv}t=clamp(t);return((ay*t+by)*t+cy)*t}}
if(burger){burger.addEventListener('click',function(){var o=burger.getAttribute('aria-expanded')==='true';burger.setAttribute('aria-expanded',String(!o));menu.hidden=o});
 doc.addEventListener('keydown',function(ev){if(ev.key==='Escape'&&!menu.hidden){menu.hidden=true;burger.setAttribute('aria-expanded','false');burger.focus()}});
 menu.addEventListener('click',function(ev){if(ev.target.closest('a')){menu.hidden=true;burger.setAttribute('aria-expanded','false')}})}
doc.querySelectorAll('video[data-auto]').forEach(function(v){if(reduce){v.controls=true}else{v.autoplay=true;var p=v.play();if(p&&p.catch)p.catch(function(){v.controls=true})}});
var mark=doc.getElementById('mark');
function fit(){if(!mark)return;var s=mark.firstElementChild;s.style.transform='';var w=mark.clientWidth,sw=s.scrollWidth;if(sw>0)s.style.transform='scale('+(w/sw).toFixed(4)+')';mark.style.height=(s.offsetHeight*(w/sw)*.96)+'px'}
if(doc.fonts&&doc.fonts.ready)doc.fonts.ready.then(fit);addEventListener('resize',fit);fit();
var nav=doc.getElementById('stepsnav'),steps=[].slice.call(doc.querySelectorAll('[data-step]')),fills=nav?[].slice.call(nav.querySelectorAll('b')):[],labels=nav?[].slice.call(nav.querySelectorAll('button')):[];
labels.forEach(function(b,i){b.addEventListener('click',function(){steps[i].scrollIntoView({behavior:reduce?'auto':'smooth',block:'start'})})});
var demo=doc.getElementById('demo'),fl=demo?[].slice.call(demo.querySelectorAll('.fl')):[],huge=doc.getElementById('huge'),band=doc.getElementById('band'),drift=[].slice.call(doc.querySelectorAll('[data-drift]'));
var ease=bez(.7,0,.84,0),LG=[[23,21,.06],[24,-6,0],[-35,10,.12]],SM=[[40,10,.06],[45,8,0],[-45,8,.12]],mq=matchMedia('(min-width:1024px)'),wide=matchMedia('(min-width:1440px)'),tick=false;
function frame(){tick=false;var y=scrollY,vh=innerHeight,i;
 hd.classList.toggle('on',y>8);
 if(steps.length&&nav){var act=0;for(i=0;i<steps.length;i++){var r=steps[i].getBoundingClientRect(),p=clamp((vh/2-r.top)/r.height);if(r.top<=vh/2)act=i;var f=fills[i];if(reduce){f.style.transform='scaleX('+(act===i?1:0)+')';continue}
   if(p>=1){if(!f.classList.contains('out')){f.classList.add('out');f.style.transform='scaleX(0)'}}else{f.classList.remove('out');f.style.transform='scaleX('+p.toFixed(3)+')'}}
  labels.forEach(function(b,j){b.classList.toggle('on',j===act)})}
 if(reduce)return;
 if(demo){var lg=mq.matches,p=clamp(y/vh),v=y/vh,set=lg?LG:SM,end=lg?.55:.2;
  demo.style.transform=lg?'translate('+((wide.matches?12:0)*(1-p)).toFixed(2)+'%,'+(-6*(1-p)).toFixed(2)+'vh) scale('+(1.2-.2*p).toFixed(4)+')':'scale('+(1-.2*p).toFixed(4)+')';
  for(i=0;i<fl.length;i++){var s=set[i],q=ease(clamp((v-s[2])/.5));fl[i].style.transform='translate('+(s[0]*(1-q)).toFixed(2)+'%,'+(s[1]*(1-q)).toFixed(2)+'%) scale('+(1-(1-end)*q).toFixed(4)+')';fl[i].style.opacity=(1-clamp((v-.6)/.2)).toFixed(3)}}
 if(huge&&band){var b=band.getBoundingClientRect(),c=(vh-b.top)/(vh+b.height);huge.style.transform='translateY('+(130*clamp((c-.5)/.5)).toFixed(1)+'%)'}
 for(i=0;i<drift.length;i++){var d=drift[i].parentNode.getBoundingClientRect();if(d.bottom<0||d.top>vh)continue;var c2=clamp((vh-d.top)/(vh+d.height));drift[i].style.transform='translateY('+((.5-c2)*5).toFixed(2)+'%)'}
}
function req(){if(!tick){tick=true;requestAnimationFrame(frame)}}
addEventListener('scroll',req,{passive:true});addEventListener('resize',req);frame();
})();
'''
