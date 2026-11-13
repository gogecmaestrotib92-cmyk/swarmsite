"""cerebrium/render.py — one pure function: render(d) -> a complete page.

The build (section order, grid, measures, type, spacing, motion, phone layout) was measured on the reference's home page
at 1440 and 390 on 2026-11-12 (see NOTES.md and probe/). Nothing of the reference's code, words, pictures, icons, logos
or typefaces is here. The client's data fills it; a section whose data is missing is left out whole. No model call.
"""
import html
import re

FONTS = ('https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@300;400&family=Inter:wght@400;500'
         '&family=IBM+Plex+Mono:wght@400;500&display=swap')
M = '../../'


# ───────────────────────── colour: the reference's dark / light / accent relations, applied to the client's palette
def _rgb(h):
    h = (h or '#000').strip().lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _hex(c):
    return '#%02x%02x%02x' % tuple(max(0, min(255, round(v))) for v in c)


def _mix(a, b, t):
    """t of a over b"""
    a, b = _rgb(a), _rgb(b)
    return _hex(tuple(a[i] * t + b[i] * (1 - t) for i in range(3)))


def _lum(h):
    def f(v):
        v /= 255
        return v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4
    r, g, b = _rgb(h)
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b)


def _con(a, b):
    la, lb = _lum(a), _lum(b)
    return (max(la, lb) + .05) / (min(la, lb) + .05)


def _toward(c, to, ground, want):
    """c mixed toward `to` in small steps until it reads on `ground` at `want`:1"""
    for i in range(0, 21):
        m = _mix(to, c, i / 20)
        if _con(m, ground) >= want:
            return m
    return to


def _rgba(h, a):
    r, g, b = _rgb(h)
    return f'rgba({r},{g},{b},{a})'


def palette(p):
    g, k, acc = p.get('ground') or '#ffffff', p.get('ink') or '#111111', p.get('accent') or '#ff4a8b'
    dark, lite = (g, k) if _lum(g) < _lum(k) else (k, g)
    paper = _mix('#ffffff', lite, .6)            # reference: white panel
    mist = lite                                  # reference: slate-50 panel
    card = _mix(dark, mist, .07)                 # slate-100 cards on it
    tile = _mix(dark, mist, .13)                 # slate-200
    mute = _toward(_mix(dark, mist, .68), dark, card, 4.6)   # slate-500 text, held readable on the card
    acc_ink = dark if _con(dark, acc) >= _con(lite, acc) else lite
    acc_dk = _mix(dark, acc, .14) if acc_ink == lite else _mix('#000000', acc, .12)
    acc_d = _toward(acc, lite, dark, 4.6)        # accent as type on the dark ground
    acc_l = _toward(acc, dark, mist, 3.1)        # accent as large type on the light panels
    return dict(dark=dark, lite=lite, paper=paper, mist=mist, card=card, tile=tile, mute=mute, acc=acc, acc_ink=acc_ink,
                acc_dk=acc_dk, acc_d=acc_d, acc_d2=_mix(lite, acc_d, .3), acc_l=acc_l, acc_l2=_mix(dark, acc_l, .25),
                line=_mix(dark, mist, .2), navbg=_rgba(_mix(lite, dark, .12), .45), glass=_rgba(dark, .35),
                glass2=_rgba(dark, .55), veil1=_rgba(dark, .52), veil2=_rgba(dark, .7), veil3=_rgba(dark, .78), lite75=_mix(lite, dark, .8),
                lite_btn=_mix(dark, lite, .1), lite_btn2=_mix(dark, lite, .2))


# ───────────────────────── small parts
def e(s):
    return html.escape(str(s if s is not None else ''), quote=True)


def _made(d, kind, i):
    xs = ((d.get('media') or {}).get('made') or {}).get(kind) or []
    if isinstance(xs, dict):
        xs = [xs]
    return xs[i % len(xs)] if xs else None


def _mark(title):
    """The reference sets one word (or phrase) of each large heading in the accent. Which word is not in the data, so the
    rule is mechanical: the longest word. Returns html with every word in its own span (the load flicker runs per word)."""
    words = str(title or '').split()
    if not words:
        return ''
    core = [re.sub(r'^\W+|\W+$', '', w) for w in words]
    k = max(range(len(words)), key=lambda i: (len(core[i]), -i))
    out = []
    for i, w in enumerate(words):
        cls = 'w a' if i == k and len(words) > 1 else 'w'
        out.append(f'<span class="{cls}" style="--i:{i}">{e(w)}</span>')
    return ' '.join(out)


def _btn(link, kind, extra=''):
    if not link or not link.get('t'):
        return ''
    return (f'<a class="btn {kind}{extra}" href="{e(link.get("h") or "#")}"><span class="fill" aria-hidden="true"></span>'
            f'<span class="sc">{e(link["t"])}</span></a>')


ARROW = ('<svg class="ar" viewBox="0 0 24 24" width="24" height="24" aria-hidden="true"><path d="M4 12h15M13 6l6 6-6 6" '
         'fill="none" stroke="currentColor" stroke-width="1.5"/></svg>')


def _dots():
    return '<div class="dots" aria-hidden="true">' + '<i></i>' * 140 + '</div>'


def _bd(pic):
    """A dark section is a window onto one fixed picture (the reference's fixed canvas). No picture → the plain ground."""
    if not pic:
        return '<div class="bd" data-slot="backdrop"></div>'
    return (f'<div class="bd" data-slot="backdrop"><div class="bw"><img src="{M}{e(pic["src"])}" alt="" '
            f'width="{pic.get("w", 1344)}" height="{pic.get("h", 752)}" decoding="async"></div></div>')


# ───────────────────────── sections
def header(d):
    b = d.get('brand') or {}
    word = bool(b.get('logo_wordmark') and b.get('logo'))
    logo = ''
    if b.get('logo'):
        logo = (f'<img src="{M}{e(b["logo"])}" alt="{e(b.get("name")) if word else ""}" height="28"'
                f'{" class=wm" if word else ""}>')
    name = '' if word else f'<span>{e(b.get("name"))}</span>'
    nav = [n for n in (d.get('nav') or []) if n.get('t')]
    links = ''.join(f'<li><a href="{e(n.get("h") or "#")}"><span class="sc">{e(n["t"])}</span></a></li>' for n in nav)
    sign, cta = d.get('signin'), d.get('cta')
    menu = ''
    if nav or sign or cta:
        rows = ''.join(f'<a href="{e(n.get("h") or "#")}">{e(n["t"])}</a>' for n in nav)
        menu = ('<details class="menu"><summary class="btn glass"><span class="sc">Menu</span><i aria-hidden="true"></i>'
                '</summary><div class="sheet">' + rows + '<div class="row">' + _btn(sign, 'soft') + _btn(cta, 'acc')
                + '</div></div></details>')
    return (f'<header class="hd" id="hd"><a class="logo" href="{e(b.get("home") or "#")}">{logo}{name}</a>'
            + (f'<ul class="nav">{links}</ul>' if links else '')
            + f'<div class="acts">{_btn(sign, "soft")}{_btn(cta, "acc")}</div>{menu}</header>')


def hero(d):
    h = d.get('hero') or {}
    if not h.get('title'):
        return ''
    n = len(h['title'])
    size = ' long' if n > 48 else ''
    ps = ''.join(f'<p>{e(t)}</p>' for t in (h.get('text'), h.get('text2')) if t)
    btns = _btn(h.get('primary'), 'acc') + _btn(h.get('secondary'), 'glass')
    trust = [t for t in (d.get('trust') or []) if t]
    logos = [l for l in (d.get('logos') or []) if isinstance(l, dict) and l.get('src')]
    mq = ''
    if logos:
        cells = ''.join(f'<img src="{M}{e(l["src"])}" alt="{e(l.get("alt"))}" height="52">' for l in logos)
        mq = f'<div class="mq"><div class="mqt" data-mq>{cells * 4}</div></div>'
    elif trust:
        cells = ''.join(f'<span>{e(t)}</span>' for t in trust)
        mq = (f'<div class="mq"><div class="mqt" data-mq><div class="mqs">{cells}</div>'
              + f'<div class="mqs" aria-hidden="true">{cells}</div>' * 3 + '</div></div>')
    return (f'<section class="dk hero">{_bd(_made(d, "land", 0))}<div class="wrap first"><h1 class="h1{size} flick">'
            f'{_mark(h["title"])}</h1><div class="side">{ps}<div class="btns">{btns}</div></div></div>{mq}{_dots()}'
            '</section>')


def panel_one(d):
    st, sp = d.get('statement') or {}, d.get('steps') or {}
    items = [i for i in (sp.get('items') or []) if i.get('title') or i.get('text')]
    intro = ''
    if st.get('title'):
        t = st.get('text') or ''
        left = f'<p class="{"lead" if len(t) <= 110 else "body"}">{e(t)}</p>' if t else '<span></span>'
        intro = f'<div class="wrap intro">{left}<h2 class="big">{_mark(st["title"])}</h2></div>'
    why = ''
    if items:
        screens = (d.get('media') or {}).get('screens') or []
        lab = f'<p class="lab"><i></i>{e(sp["title"])}</p>' if sp.get('title') else ''
        lis, cards = '', ''
        for i, it in enumerate(items):
            lis += f'<li><a href="#why-{i}"{" class=on" if i == 0 else ""}>{e(it.get("k") or it.get("title"))}</a></li>'
            src, alt, shape = it.get('img'), it.get('title') or '', it.get('shape') or 'screen'
            w = hgt = None
            for m in ((d.get('media') or {}).get('phones') or []) + ((d.get('media') or {}).get('photos') or []) + screens:
                if m.get('src') == src:
                    w, hgt, alt = m.get('w'), m.get('h'), m.get('alt') or alt
            if not src and screens:
                s = screens[i % len(screens)]
                src, w, hgt, alt, shape = s['src'], s.get('w'), s.get('h'), s.get('alt') or alt, 'screen'
            vis = ''
            if src:
                g = _made(d, 'land', 0)   # the page's one motif, another crop per card, held quiet toward the dark ground
                ground = (f'<img class="g c{i % 4}" src="{M}{e(g["src"])}" alt="" width="{g.get("w", 1344)}" '
                          f'height="{g.get("h", 752)}" loading="lazy" decoding="async">') if g else ''
                dim = f' width="{w}" height="{hgt}"' if w and hgt else ''
                vis = (f'<div class="vis {e(shape)}" data-slot="ground">{ground}<img class="s" src="{M}{e(src)}" '
                       f'alt="{e(alt)}"{dim} loading="lazy" decoding="async"></div>')
            cta = it.get('cta') or {}
            link = (f'<a class="tl" href="{e(cta.get("h") or "#")}"><span class="sc">{e(cta["t"])}</span></a>'
                    if cta.get('t') else '')
            cards += (f'<article class="fc" id="why-{i}">{vis}<h3>{e(it.get("title"))}</h3><p>{e(it.get("text"))}</p>'
                      f'{link}</article>')
        why = (f'<div class="wrap why"><div class="stick">{lab}<ul class="idx">{lis}</ul></div>'
               f'<div class="fcs">{cards}</div></div>')
    if not intro and not why:
        return ''
    return f'<section class="panel paper">{intro}{why}</section>'


def dark_two(d):
    f = d.get('features') or {}
    items = [i for i in (f.get('items') or []) if i.get('t')]
    links = [l for l in (d.get('links') or []) if l.get('t')]
    sec = ''
    if f.get('title') or items:
        text = f'<p class="sub">{e(f["text"])}</p>' if f.get('text') else ''
        rows = ''.join(f'<li><h3>{e(i["t"])}</h3>' + (f'<p>{e(i["d"])}</p>' if i.get('d') else '') + '</li>' for i in items)
        sec = (f'<div class="wrap sec"><div class="lft"><h2 class="h2">{_mark(f.get("title"))}</h2>{text}'
               f'<div class="btns">{_btn(d.get("cta"), "acc")}</div></div><ul class="pts">{rows}</ul></div>')
    built = ''
    if links:
        cs = ''.join(f'<a class="lc" href="{e(l.get("h") or "#")}"><h3>{e(l["t"])}</h3>'
                     + (f'<p>{e(l["d"])}</p>' if l.get('d') else '') + ARROW + '</a>' for l in links)
        built = f'<div class="wrap lcs">{cs}</div>'
    if not sec and not built:
        return ''
    return f'<section class="dk two">{_bd(_made(d, "land", 0))}{sec}{_dots() if sec and built else ""}{built}</section>'


def panel_two(d):
    pl, fq, fg = d.get('plans') or {}, d.get('faq') or {}, [x for x in (d.get('figures') or []) if x.get('v')]
    plans = [p for p in (pl.get('items') or []) if p.get('name')]
    qs = [q for q in (fq.get('items') or []) if q.get('q') and q.get('a')]
    a = b = c = ''
    if plans:
        head = f'<h2 class="big">{_mark(pl["title"])}</h2>' if pl.get('title') else ''
        text = f'<p class="lead">{e(pl["text"])}</p>' if pl.get('text') else ''
        cards = ''
        for p in plans:
            rows = ''.join(f'<li>{e(r)}</li>' for r in (p.get('rows') or []))
            cta = p.get('cta') or d.get('cta')
            cards += (f'<article class="pc{" mk" if p.get("marked") else ""}">'
                      + (f'<p class="tag">{e(p["per"])}</p>' if p.get('per') else '')
                      + (f'<p class="price">{e(p["price"])}</p>' if p.get('price') else '')
                      + f'<h3>{"<i></i>" if p.get("marked") else ""}{e(p["name"])}</h3>'
                      + (f'<p class="ln">{e(p["line"])}</p>' if p.get('line') else '')
                      + (f'<ul>{rows}</ul>' if rows else '')
                      + f'<div class="pf">{_btn(cta, "acc" if p.get("marked") else "white")}</div></article>')
        note = f'<p class="note">{e(pl["note"])}</p>' if pl.get('note') else ''
        a = (f'<div class="wrap plans"><div class="ph">{head}{text}</div>'
             f'<div class="pcs n{min(len(plans), 3)}{"" if any(p.get("rows") or p.get("line") for p in plans) else " bare"}">{cards}</div>{note}</div>')
    if qs:
        lab = f'<p class="lab"><i></i>{e(fq["title"])}</p>' if fq.get('title') else '<span></span>'
        rows = ''.join(f'<details class="q"><summary><span>{e(q["q"])}</span>{ARROW}</summary><p>{e(q["a"])}</p></details>'
                       for q in qs)
        half = (len(qs) + 1) // 2
        rows_l = ''.join(f'<details class="q"><summary><span>{e(q["q"])}</span>{ARROW}</summary><p>{e(q["a"])}</p></details>'
                         for q in qs[:half])
        rows_r = rows[len(rows_l):]
        b = f'<div class="wrap rows">{lab}<div class="col">{rows_l}</div><div class="col">{rows_r}</div></div>'
    if fg:
        cards = ''
        for i, x in enumerate(fg):
            pic = _made(d, 'land', 0)   # the same motif as the opening, in another crop per card
            img = (f'<img class="c{(i + 2) % 4}" src="{M}{e(pic["src"])}" alt="" width="{pic.get("w", 1344)}" height="{pic.get("h", 752)}" '
                   'loading="lazy" decoding="async">') if pic else ''
            tone = (pic or {}).get('tone') or 'none'
            cards += (f'<article class="bc"><div class="pic {e(tone)}" data-slot="picture">{img}<p class="v">{e(x["v"])}</p>'
                      f'</div><div class="bb"><p>{e(x.get("l"))}</p></div></article>')
        c = f'<div class="wrap figs n{min(len(fg), 4)}">{cards}</div>'
    if not (a or b or c):
        return ''
    return f'<section class="panel mist">{a}{b}{c}</section>'


def footer(d):
    b, cl, ft = d.get('brand') or {}, d.get('close') or {}, d.get('foot') or {}
    word = bool(b.get('logo_wordmark') and b.get('logo'))
    logo = (f'<img src="{M}{e(b["logo"])}" alt="{e(b.get("name")) if word else ""}" height="26"{" class=wm" if word else ""}>'
            if b.get('logo') else '')
    name = '' if word else f'<span>{e(b.get("name"))}</span>'
    col1 = ''.join(f'<li><a href="{e(n.get("h") or "#")}">{e(n["t"])}</a></li>' for n in (d.get('nav') or []) if n.get('t'))
    seen = {n.get('h') for n in (d.get('nav') or [])}
    extra = [x for x in (d.get('links') or []) + [d.get('signin') or {}, d.get('cta') or {}] if x.get('t') and x.get('h') not in seen]
    uniq, col2 = set(), ''
    for x in extra:
        if x['h'] in uniq:
            continue
        uniq.add(x['h'])
        col2 += f'<li><a href="{e(x["h"])}">{e(x["t"])}</a></li>'
    cols = ''.join(f'<ul>{c}</ul>' for c in (col1, col2) if c)
    close = ''
    if cl.get('title'):
        close = (f'<div class="cl"><p class="ct">{e(cl["title"])}</p>'
                 + (f'<p class="cx">{e(cl["text"])}</p>' if cl.get('text') else '')
                 + f'<div class="btns">{_btn(cl.get("cta"), "acc")}{_btn(d.get("signin"), "glass")}</div></div>')
    legal = ''.join(f'<a href="{e(x.get("h") or "#")}">{e(x["t"])}</a>' for x in (ft.get('links') or []) if x.get('t'))
    small = f'<p class="fx">{e(ft["text"])}</p>' if ft.get('text') else ''
    return (f'<footer class="dk ft">{_bd(_made(d, "land", 0))}<div class="wrap fg"><a class="logo" href="{e(b.get("home") or "#")}">'
            f'{logo}{name}</a><div class="fr"><div class="fcols">{cols}</div>{close}</div></div>'
            f'<div class="wrap fb">{small}<div class="fl"><p>{e(ft.get("legal"))}</p><nav>{legal}</nav></div></div></footer>')


# ───────────────────────── the page
def render(d: dict) -> str:
    c = palette(d.get('palette') or {})
    b = d.get('brand') or {}
    hro = d.get('hero') or {}
    vars_ = ';'.join(f'--{k.replace("_", "-")}:{v}' for k, v in c.items())
    body = header(d) + '<main>' + hero(d) + panel_one(d) + dark_two(d) + panel_two(d) + '</main>' + footer(d)
    desc = hro.get('text') or ''
    return ('<!doctype html><html lang="' + e(d.get('lang') or 'en') + '"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{e(b.get("name"))} — {e(hro.get("title"))}</title><meta name="description" content="{e(desc)}">'
            '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            f'<link rel="stylesheet" href="{FONTS}"><style>:root{{{vars_}}}{CSS}</style></head><body>{body}'
            f'<script>{JS}</script></body></html>')


CSS = r"""
*{box-sizing:border-box;margin:0;padding:0}html{-webkit-text-size-adjust:100%}
body{background:var(--dark);color:var(--dark);font:400 16px/1.5 Inter,system-ui,sans-serif;-webkit-font-smoothing:antialiased;overflow-x:clip}
img{display:block;max-width:100%;height:auto}a{color:inherit;text-decoration:none}ul{list-style:none}
:focus-visible{outline:2px solid currentColor;outline-offset:3px;border-radius:7px}
.wrap{padding:0 40px;max-width:1920px;margin:0 auto}
.mono,.btn .sc,.nav a,.lab,.tag,.tl,.fl nav a{font:400 13px/1.07 "IBM Plex Mono",ui-monospace,monospace;letter-spacing:-.025em;text-transform:uppercase}
/* header: fixed, leaves going down, returns going up — transform .2s cubic-bezier(.645,.045,.355,1) */
.hd{position:absolute;inset:0 0 auto 0;z-index:150;height:82px;padding:14px 40px;display:flex;align-items:center;gap:12px;color:var(--lite);transition:transform .2s cubic-bezier(.645,.045,.355,1)}
.hd.pin{position:fixed}.hd :focus-visible{outline-color:var(--lite)}.hd.st{background:color-mix(in srgb,var(--dark) 88%,transparent);-webkit-backdrop-filter:blur(16px);backdrop-filter:blur(16px)}.hd.lt{background:var(--paper);box-shadow:0 1px 0 var(--line);color:var(--dark)}.hd.lt .logo{color:var(--dark)}.hd.lt .logo img.wm{filter:none}.hd.lt .nav{background:var(--card);-webkit-backdrop-filter:none;backdrop-filter:none}.hd.lt .nav a{color:var(--dark)}.hd.lt .btn.glass{background:var(--card);color:var(--dark);-webkit-backdrop-filter:none;backdrop-filter:none}.hd.lt .btn.glass .fill{background:var(--tile)}.hd.lt .btn.soft{background:var(--card)}.hd.lt .btn.soft .fill{background:var(--tile)}.hd.lt :focus-visible{outline-color:var(--dark)}.hd.away{transform:translateY(-100%)}.hd:focus-within{transform:none}
.logo{display:inline-flex;align-items:center;gap:14px;font:400 26px/1.5 Inter,sans-serif;letter-spacing:-.025em;color:var(--lite);margin-right:auto}
.logo img{height:28px;width:auto}.logo img.wm{filter:brightness(0) invert(1)}
.nav{position:absolute;left:calc(50% + 4px);top:14px;height:54px;display:flex;align-items:center;gap:28px;padding:0 24px;border-radius:7px;background:var(--navbg);-webkit-backdrop-filter:blur(17.5px);backdrop-filter:blur(17.5px)}
.nav a{display:block;padding:20px 0;color:var(--lite);white-space:nowrap}
.acts{display:flex;gap:12px}
.menu{display:none}
/* buttons: 54 high, r7, a darker fill grows from scale(.9,.7) in .2s; the label scrambles on hover */
.btn{position:relative;isolation:isolate;overflow:hidden;display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:54px;padding:0 20px;border-radius:7px;border:0;cursor:pointer;white-space:nowrap;transition:transform .2s cubic-bezier(.645,.045,.355,1)}
.btn .fill{position:absolute;inset:8px 6px;z-index:-1;border-radius:7px;transform:scale3d(.9,.7,1);opacity:0;transition:transform .2s cubic-bezier(.645,.045,.355,1),opacity .2s cubic-bezier(.645,.045,.355,1)}
.btn:hover .fill,.btn:focus-visible .fill{transform:none;opacity:1}.btn:active{transform:scale(.97)}
.btn.acc{background:var(--acc);color:var(--acc-ink)}.btn.acc .fill{background:var(--acc-dk)}
.btn.glass{background:var(--glass);color:var(--lite);-webkit-backdrop-filter:blur(16px);backdrop-filter:blur(16px)}.btn.glass .fill{background:var(--glass2)}
.btn.soft{background:var(--lite-btn);color:var(--dark)}.btn.soft .fill{background:var(--lite-btn2)}
.btn.white{background:var(--paper);color:var(--dark)}.btn.white .fill{background:var(--tile)}
.btns{display:flex;flex-wrap:wrap;gap:16px}
/* dark sections: windows onto one fixed picture, veiled toward the dark ground */
.dk{position:relative;z-index:0;color:var(--lite);background:var(--dark)}
.bd{position:absolute;inset:0;z-index:-1;clip-path:inset(0);overflow:hidden}
.bw{position:fixed;left:0;top:0;width:100%;height:100vh;height:100lvh;overflow:hidden}.bd img{width:100%;height:100%;max-width:none;object-fit:cover}
.bd::after{content:"";position:fixed;inset:0;background:linear-gradient(180deg,var(--veil1),var(--veil2))}
.two .bd img{transform:scale(1.7);transform-origin:100% 100%}
.dk :focus-visible{outline-color:var(--lite)}
/* opening */
.hero{padding-bottom:132px}
.first{min-height:100vh;min-height:100svh;display:grid;grid-template-columns:repeat(12,1fr);column-gap:20px;align-items:end;padding-top:140px;padding-bottom:82px}
.h1{grid-column:1/7;font:300 86px/1 "Hanken Grotesk",sans-serif;letter-spacing:-.03em;text-wrap:balance}
.h1.long{font-size:72.6px}
.w{display:inline-block}
.dk .w.a{background:linear-gradient(90deg,var(--acc-d),var(--acc-d2));-webkit-background-clip:text;background-clip:text;color:transparent;padding-bottom:.08em;margin-bottom:-.08em}
.panel .w.a{background:linear-gradient(90deg,var(--acc-l),var(--acc-l2));-webkit-background-clip:text;background-clip:text;color:transparent;padding-bottom:.08em;margin-bottom:-.08em}
@keyframes flick{0%{opacity:0}30%{opacity:.34}50%{opacity:1}70%{opacity:.27}100%{opacity:1}}
.flick .w{animation:flick .45s steps(1,end) both;animation-delay:calc(.15s + var(--i)*45ms)}
.side{grid-column:9/13}
.side p{max-width:325px;font-size:17px;line-height:1.35;letter-spacing:.01em}.side p+p{margin-top:12px}
.side .btns{margin-top:30px}.btn{flex:none}
/* the row that moves with the scroll */
.mq{overflow:hidden;margin-top:83px;height:52px}
.mqt{display:flex;align-items:center;width:max-content;height:52px;gap:80px;will-change:transform}
.mqt img{height:52px;width:auto}.mqs{display:flex;gap:80px}
.mqs span{font:300 26.5px/52px "Hanken Grotesk",sans-serif;letter-spacing:-.025em;white-space:nowrap}
/* the dot field: 72px cells, a 2px dot each; a 34px accent square scales in where the pointer is */
.dots{display:grid;grid-template-columns:repeat(auto-fill,72px);grid-auto-rows:72px;justify-content:center;height:360px;overflow:hidden;margin-top:82px}
.dots i{position:relative;display:block}
.dots i::after{content:"";position:absolute;left:50%;top:50%;width:2px;height:2px;margin:-1px;border-radius:50%;background:var(--lite)}
.dots i::before{content:"";position:absolute;left:50%;top:50%;width:34px;height:34px;margin:-17px;border-radius:7px;background:var(--acc);opacity:.85;transform:scale(0);transition:transform .2s cubic-bezier(.645,.045,.355,1)}
.dots i:hover::before,.dots i.on::before{transform:none}
/* light panels: r32, laid 60px over the dark above and below */
.panel{position:relative;z-index:1;margin:-60px 0;border-radius:32px;padding:82px 0}
.paper{background:var(--paper)}.mist{background:var(--mist)}
.panel :focus-visible{outline-color:var(--dark)}
.intro{display:grid;grid-template-columns:1fr 1fr;gap:20px;align-items:start}
.lead{font-size:26.5px;line-height:1.35;letter-spacing:-.025em;max-width:480px}
.body{font-size:18px;line-height:1.5;letter-spacing:.01em;max-width:480px}
.big{font:300 72.6px/1.05 "Hanken Grotesk",sans-serif;letter-spacing:-.03em;text-wrap:balance}
.lab{display:flex;align-items:center;gap:8px;line-height:14px}.lab i{flex:none;width:6px;height:6px;border-radius:50%;background:currentColor}
.intro+.why{margin-top:129px}
.why{display:grid;grid-template-columns:1fr 1fr;gap:20px;align-items:start}
.stick{position:sticky;top:98px}
.idx{margin-top:48px}
.idx a{display:inline-block;font:300 43.9px/1.15 "Hanken Grotesk",sans-serif;letter-spacing:-.04em;color:var(--mute);opacity:.72;transition:color .2s cubic-bezier(.4,0,.2,1),opacity .2s cubic-bezier(.4,0,.2,1)}
.idx a.on,.idx a:hover{color:var(--dark);opacity:1}
.fcs{display:grid;gap:82px}
.fc{scroll-margin-top:98px}
.vis{position:relative;overflow:hidden;border-radius:15px;background:var(--dark);min-height:583px;padding:48px;display:flex;align-items:center;justify-content:center}
.vis .g,.pic img{position:absolute;width:200%;height:200%;max-width:none;object-fit:cover}.c0{left:0;top:-100%}.c1{left:-100%;top:-100%}.c2{left:-100%;top:0}.c3{left:-40%;top:-50%}
.vis::before{content:"";position:absolute;inset:0;z-index:1;background:var(--veil1)}
.vis .s{position:relative;z-index:2;width:auto;height:auto;max-width:100%;max-height:487px;border-radius:10px}
.vis.screen{min-height:0}
.fc h3{margin-top:24px;font-size:26.5px;font-weight:400;line-height:1.35;letter-spacing:-.025em;max-width:570px}
.fc p{margin-top:15px;font-size:18px;line-height:1.5;letter-spacing:.01em;max-width:570px}
.tl{display:inline-block;margin-top:24px;padding:6px 0;color:var(--mute);text-decoration:underline;text-underline-offset:3px}
/* second dark section */
.two{padding:189px 0 169px}
.sec{display:grid;grid-template-columns:1fr 1fr;gap:20px;align-items:start}
.h2{font:300 57.4px/1.05 "Hanken Grotesk",sans-serif;letter-spacing:-.04em;max-width:520px;text-wrap:balance}
.sub{margin-top:24px;max-width:460px;font-weight:500;color:var(--lite75)}
.lft .btns{margin-top:36px}
.pts{display:grid;gap:50px}
.pts h3{font-size:26.5px;font-weight:400;line-height:1.35;letter-spacing:-.025em}
.pts p{margin-top:3px;max-width:460px;font-weight:500;color:var(--lite75)}
.two .dots{margin-top:164px}
.lcs{display:grid;grid-template-columns:repeat(2,minmax(0,570px));gap:20px;justify-content:center;margin-top:129px}
.sec+.lcs{margin-top:129px}
.lc{position:relative;display:block;min-height:167px;padding:16px 56px 16px 16px;border-radius:10px;background:var(--mist);color:var(--dark);transition:background-color .2s cubic-bezier(.4,0,.2,1)}
.lc:hover{background:var(--paper)}
.lc h3{font-size:21.3px;font-weight:400;line-height:1.35;letter-spacing:-.025em}
.lc p{margin-top:6px;font-size:17px;line-height:1.35;letter-spacing:.01em;color:var(--mute)}
.lc .ar{position:absolute;right:12px;bottom:12px;color:var(--mute);transition:transform .2s cubic-bezier(.4,0,.2,1)}.lc:hover .ar{transform:translateX(4px)}
/* second light panel */
.ph .big{max-width:900px}.ph .lead{margin-top:40px}
.pcs{display:grid;gap:15px;margin-top:82px}.pcs.n1{grid-template-columns:minmax(0,670px)}.pcs.n2{grid-template-columns:1fr 1fr;gap:20px}.pcs.n3{grid-template-columns:repeat(3,1fr)}
.pc{display:flex;flex-direction:column;min-height:596px;padding:20px;border-radius:10px;background:var(--card)}
.pcs.bare .pc{min-height:0}.pcs.bare .pc h3{margin-top:24px}.pcs.bare .pf{margin-top:32px}
.pc.mk{background:var(--paper)}
.tag{color:var(--mute);line-height:14px}
.price{margin-top:64px;font:300 72.6px/1.05 "Hanken Grotesk",sans-serif;letter-spacing:-.03em}
.pc h3{display:flex;align-items:center;gap:10px;margin-top:64px;font-size:26.5px;font-weight:400;line-height:1.35;letter-spacing:-.025em}
.pc h3 i{width:6px;height:6px;border-radius:50%;background:var(--acc-l)}
.ln{margin-top:4px;font-size:18px;line-height:1.5;letter-spacing:.01em;color:var(--mute)}
.pc ul{margin-top:24px}.pc li{padding:12px 0;border-top:1px solid var(--line);font-size:15px;line-height:1.3;letter-spacing:.01em}
.pf{margin-top:auto;padding-top:32px}
.note{margin-top:20px;max-width:670px;font-size:15px;line-height:1.3;letter-spacing:.01em;color:var(--mute)}
.rows{display:grid;grid-template-columns:444px 1fr 1fr;gap:0 16px;align-items:start}
.plans+.rows,.plans+.figs,.rows+.figs{margin-top:134px}
.q{border-bottom:1px solid var(--line)}
.q summary{display:flex;align-items:center;justify-content:space-between;gap:16px;min-height:76px;padding:20px 0;cursor:pointer;list-style:none;font-size:26.5px;line-height:1.35;letter-spacing:-.025em}
.q summary::-webkit-details-marker{display:none}
.q summary span{transition:transform .2s cubic-bezier(.4,0,.2,1)}.q summary:hover span{transform:translateX(6px)}
.q .ar{flex:none;transition:transform .2s cubic-bezier(.4,0,.2,1)}.q[open] .ar{transform:rotate(90deg)}
.q p{padding:0 40px 24px 0;font-size:18px;line-height:1.5;letter-spacing:.01em}
.figs{display:grid;gap:20px}.figs.n1{grid-template-columns:minmax(0,440px)}.figs.n2{grid-template-columns:repeat(2,minmax(0,440px))}.figs.n3{grid-template-columns:repeat(3,1fr)}.figs.n4{grid-template-columns:repeat(4,1fr)}
.bc{display:flex;flex-direction:column;border-radius:10px;overflow:hidden;background:var(--paper)}
.pic{position:relative;aspect-ratio:440/372;display:grid;place-items:center;background:var(--dark);color:var(--lite);overflow:hidden}

.pic::after{content:"";position:absolute;inset:0;background:var(--veil1)}
.pic.light{color:var(--dark)}.pic.light::after{background:var(--lite);opacity:.55}
.pic .v{position:relative;z-index:1;font:300 72.6px/1.05 "Hanken Grotesk",sans-serif;letter-spacing:-.03em;white-space:nowrap}
.figs.n4 .pic .v{font-size:57.4px}
.bb{flex:1;padding:20px 20px 28px;font-size:20px;line-height:1.35;letter-spacing:-.02em}
/* foot */
.ft{padding:108px 0 0}
.fg{display:grid;grid-template-columns:1fr 1fr;gap:20px;align-items:start}
.ft .logo{font-size:24px;margin:0;justify-self:start}.ft .logo img{height:26px}
.fcols{display:grid;grid-template-columns:1fr 1fr;gap:20px;min-height:256px}
.fcols a{display:inline-block;padding:3px 0 6px;font-size:15px;line-height:1.3;letter-spacing:.01em}.fcols a:hover,.fl a:hover{text-decoration:underline;text-underline-offset:3px}
.cl{margin-top:200px}
.ct{font:300 36.1px/1.15 Inter,sans-serif;letter-spacing:-.025em;max-width:670px;text-wrap:balance}
.cx{margin-top:16px;max-width:460px;font-weight:500;color:var(--lite75)}
.cl .btns{margin-top:24px}
.fb{margin-top:120px;padding-bottom:42px}
.fx{max-width:670px;margin-bottom:24px;font-size:13px;line-height:1.5;color:var(--lite75)}
.fl{display:flex;justify-content:space-between;align-items:center;gap:24px;padding-top:34px;border-top:1px solid color-mix(in srgb,var(--lite) 22%,transparent)}
.fl p{font-size:17px;line-height:1.35;letter-spacing:.01em}.fl nav{display:flex;flex-wrap:wrap;gap:8px 24px}.fl nav a{padding:6px 0}
@media (max-width:1100px){
.wrap{padding:0 15px}
.hd{height:72px;padding:15px}.nav,.acts{display:none}.logo{font-size:22px;gap:10px}.logo img{height:24px}
.menu{display:block;position:relative}.menu summary{list-style:none;min-height:42px;padding:0 14px}.menu summary::-webkit-details-marker{display:none}
.menu summary i{width:10px;height:10px;background:radial-gradient(circle,currentColor 1.6px,transparent 2px) 0 0/5px 5px}
.sheet{position:absolute;right:0;top:50px;width:min(330px,calc(100vw - 30px));padding:10px;border-radius:7px;background:var(--paper);color:var(--dark);display:grid}
.sheet>a{padding:14px 12px;font-size:18px;line-height:1.35;border-bottom:1px solid var(--line)}.sheet .row{display:grid;gap:8px;margin-top:10px}.sheet :focus-visible{outline-color:var(--dark)}
.btn{min-height:42px;padding:0 14px}.btn .fill{inset:6px 5px}.btns{gap:16px}
.hero{padding-bottom:72px}
.first{display:block;min-height:0;padding-top:max(140px,calc(100svh - 420px));padding-bottom:40px}
.h1,.h1.long{font-size:45px;max-width:560px}.side{max-width:560px;margin-top:32px}.side p{max-width:none;font-size:16px}
.mq{margin-top:60px}.mqs span{font-size:22px}.mqt,.mqs{gap:48px}
.dots{grid-template-columns:repeat(6,1fr);grid-auto-rows:calc(100vw/6);height:calc(100vw/6*4);margin-top:60px}
.panel{margin:-30px 0;padding:40px 0}
.intro{display:flex;flex-direction:column-reverse;gap:24px}.big{font-size:40px}.lead{font-size:20px}.body{font-size:17px}
.intro+.why{margin-top:68px}.why{display:block}.stick{position:static}.idx{display:none}.stick .lab{margin-bottom:28px}
.fcs{gap:56px}.vis{min-height:0;padding:24px}.vis .s{max-height:448px}
.fc h3{font-size:25px;font-weight:300;line-height:1.15;max-width:none}.fc p{font-size:17px;max-width:none}
.two{padding:100px 0 94px}.sec{display:block}.h2{font-size:40px}.pts{margin-top:72px;gap:50px}.pts h3{font-size:20px}.pts p{max-width:none}
.two .dots{margin-top:72px}.lcs,.sec+.lcs{grid-template-columns:1fr;gap:15px;margin-top:56px}.lc{min-height:114px}.lc h3{font-size:18px}.lc p{font-size:16px}
.ph .lead{margin-top:24px}.pcs,.pcs.n2,.pcs.n3{grid-template-columns:1fr;gap:15px;margin-top:56px}.pc{min-height:454px}.price{font-size:40px;margin-top:48px}.pc h3{margin-top:48px;font-size:20px}.ln{font-size:17px}
.plans+.rows,.plans+.figs,.rows+.figs{margin-top:96px}
.rows{display:block}.rows .lab{margin-bottom:31px}.q summary{min-height:55px;padding:14px 0;font-size:20px}.q p{font-size:17px;padding-right:0}
.figs,.figs.n2,.figs.n3,.figs.n4{display:flex;gap:15px;overflow-x:auto;scroll-snap-type:x mandatory;padding:0 15px;scroll-padding:0 15px;scrollbar-width:none}.figs::-webkit-scrollbar{display:none}
.bc{flex:0 0 298px;scroll-snap-align:start}.pic .v,.figs.n4 .pic .v{font-size:45px}
.ft{padding:60px 0 0}.fg{display:block}.fr{margin-top:40px}.fcols{min-height:0}.cl{margin-top:96px}.ct{font-size:25px}.fb{margin-top:48px;padding-bottom:28px}
.fl{flex-direction:column-reverse;align-items:flex-start;gap:20px;padding-top:28px}.fl nav{flex-direction:column;gap:6px}.fl p{align-self:flex-end;margin-top:-34px}.fl:has(nav:empty) p{align-self:flex-start;margin-top:0}
}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}.hd.away{transform:none}.mqt{transform:none!important}html{scroll-behavior:auto}}
"""

JS = r"""(function(){
var rm=matchMedia('(prefers-reduced-motion:reduce)').matches,doc=document;
/* header: away going down, back going up */
var hd=doc.getElementById('hd'),last=0,pn=doc.querySelectorAll('.panel'),mn=doc.querySelector('.menu');if(hd)hd.classList.add('pin');
function lt(){if(!hd)return;var m=hd.offsetHeight/2,on=false;for(var i=0;i<pn.length;i++){var r=pn[i].getBoundingClientRect();if(r.top<=m&&r.bottom>=m)on=true}hd.classList.toggle('lt',on);hd.classList.toggle('st',scrollY>10)}lt();addEventListener('resize',lt);
/* the row moves with the scroll: about .29px per scrolled px, with a short lag */
var mq=doc.querySelector('[data-mq]'),cur=0,raf=0;
function tick(){raf=0;var t=-.29*scrollY;cur+=(t-cur)*.12;if(Math.abs(t-cur)<.3)cur=t;mq.style.transform='translate3d('+cur.toFixed(1)+'px,0,0)';if(cur!==t)raf=requestAnimationFrame(tick)}
addEventListener('scroll',function(){var y=scrollY;lt();if(hd&&!rm){if(y>last&&y>120){hd.classList.add('away');if(mn)mn.open=false}else if(y<last)hd.classList.remove('away')}last=y;if(mq&&!rm&&!raf)raf=requestAnimationFrame(tick)},{passive:true});
/* label scramble on hover: letters resolve left to right */
var A='ABCDEFGHIJKLMNOPQRSTUVWXYZ';
function scr(el){if(rm||el._t)return;var s=el.getAttribute('data-t')||el.textContent,n=0;el.setAttribute('data-t',s);el.setAttribute('aria-label',s);
el._t=setInterval(function(){n+=1;var o='';for(var i=0;i<s.length;i++)o+=i<n||s[i]===' '||!/[a-z0-9]/i.test(s[i])?s[i]:A[Math.random()*26|0];el.textContent=o;if(n>=s.length){clearInterval(el._t);el._t=0;el.textContent=s}},30)}
[].forEach.call(doc.querySelectorAll('.btn,.nav a,.tl'),function(a){var el=a.querySelector('.sc');if(!el)return;var w=el.getBoundingClientRect().width;a.addEventListener('mouseenter',function(){if(!el.style.minWidth&&w){el.style.display='inline-block';el.style.minWidth=Math.ceil(el.getBoundingClientRect().width)+'px'}scr(el)})});
/* dot field: now and then a cell lights by itself */
if(!rm){[].forEach.call(doc.querySelectorAll('.dots'),function(g){var seen=false;if('IntersectionObserver' in window)new IntersectionObserver(function(es){seen=es[0].isIntersecting}).observe(g);
setInterval(function(){if(!seen)return;var w=g.clientWidth,cols=Math.max(1,Math.round(w/(g.firstChild.offsetWidth||72))),rows=Math.round(g.clientHeight/(g.firstChild.offsetHeight||72)),c=g.children[(Math.random()*rows|0)*cols+(Math.random()*cols|0)];if(!c)return;c.classList.add('on');setTimeout(function(){c.classList.remove('on')},1800)},700)})}
/* the list beside the cards follows the card in view */
var ls=doc.querySelectorAll('.idx a');
if(ls.length&&'IntersectionObserver' in window){var io=new IntersectionObserver(function(es){es.forEach(function(x){if(!x.isIntersecting)return;var id=x.target.id;[].forEach.call(ls,function(a){a.classList.toggle('on',a.getAttribute('href')==='#'+id)})})},{rootMargin:'-35% 0px -55% 0px'});
[].forEach.call(doc.querySelectorAll('.fc'),function(c){io.observe(c)})}
[].forEach.call(ls,function(a){a.addEventListener('click',function(ev){var t=doc.getElementById(a.getAttribute('href').slice(1));if(!t)return;ev.preventDefault();t.scrollIntoView({behavior:rm?'auto':'smooth',block:'start'})})});
/* phone menu closes on Escape and on a link */
var m=doc.querySelector('.menu');if(m){doc.addEventListener('keydown',function(ev){if(ev.key==='Escape')m.open=false});m.addEventListener('click',function(ev){if(ev.target.closest('.sheet a'))m.open=false})}
})();"""
