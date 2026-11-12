"""linearity/render.py — one pure function: render(d) -> a complete page.

The build (section order, grid, measures, type, spacing, motion, phone layout) was measured on the reference's home page
at 1440x900 and 390x844 on 2026-11-12 (see NOTES.md and probe/). Nothing of the reference's code, words, pictures, icons,
logos or typefaces is here. The client's data fills it; a section whose data is missing is left out whole. No model call,
no client logic, no file reads.

The reference sets every measure in rem and scales the root with the viewport (13.714px at 1440, 16.64px at 390); this
template does the same, so the rem values below are the reference's own.
"""
import html

FONTS = ('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,500;12..96,700'
         '&family=Inter:wght@400;500;600&display=swap')
M = '../../'


def e(s):
    return html.escape(str(s if s is not None else ''), quote=True)


# ───────────────────────── colour: the reference's relations (ground / ink / muted / glass / one hot accent)
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
    x, y = sorted((_lum(a), _lum(b)), reverse=True)
    return (x + .05) / (y + .05)


def _held(ink, bg, t, floor):
    """ink at t over bg, raised until it reads at `floor` on bg and on the glass panels (bg + 10 % ink)"""
    glass = _mix(ink, bg, .10)
    while t < 1 and (_con(_mix(ink, bg, t), bg) < floor or _con(_mix(ink, bg, t), glass) < floor):
        t += .02
    return _mix(ink, bg, min(t, 1))


def _theme(p):
    bg, ink, acc = p.get('ground') or '#000000', p.get('ink') or '#ffffff', p.get('accent') or p.get('ink') or '#ffffff'
    if _con(acc, bg) < 1.6:
        acc = ink
    on = ink if _con(ink, acc) >= _con(bg, acc) else bg
    far = '#000000' if _lum(on) > .5 else '#ffffff'
    n = 0
    while _con(on, acc) < 4.6 and n < 14:          # the accent is pushed away from its label until the label reads
        acc = _mix(far, acc, .08)
        n += 1
    v = {
        'bg': bg, 'ink': ink, 'acc': acc, 'on': on,
        'mute': _held(ink, bg, .55, 4.7),            # reference: white at 40–60 %
        'dim': _held(ink, bg, .42, 3.1),             # reference: the grey words of the opening line (large type)
        'glow': _mix('#ffffff' if _lum(acc) < .6 else bg, acc, .42),   # reference: a lighter inner light on the hot button
        'i': '%d,%d,%d' % _rgb(ink), 'g': '%d,%d,%d' % _rgb(bg), 'a': '%d,%d,%d' % _rgb(acc),
    }
    return ';'.join('--%s:%s' % kv for kv in v.items())


# ───────────────────────── small parts
def btn(x, kind='glass', cls=''):
    """the reference's pill: a halo ring behind it, the label twice so it rolls up on hover"""
    if not x or not x.get('t'):
        return ''
    t = e(x['t'])
    return (f'<a class="btn {kind} {cls}" href="{e(x.get("h") or "#")}"><span class="roll"><span>{t}</span>'
            f'<span aria-hidden="true">{t}</span></span></a>')


def pair(a, b):
    """glass pill first, hot pill second — the order the reference keeps in every section"""
    s = btn(a, 'glass') + btn(b, 'hot')
    return f'<div class="btns">{s}</div>' if s else ''


def pic(x, cls='', lazy=True, sizes=''):
    if not x or not x.get('src'):
        return ''
    wh = f' width="{int(x["w"])}" height="{int(x["h"])}"' if x.get('w') and x.get('h') else ''
    return (f'<img class="{cls}" src="{M}{e(x["src"])}" alt="{e(x.get("alt") or "")}"{wh}'
            f'{" loading=lazy" if lazy else ""} decoding="async">')


def pool(d):
    """every picture the client has, each once: portraits and screens interleaved"""
    md = d.get('media') or {}
    a = [x for x in (md.get('phones') or []) + (md.get('photos') or []) if x.get('src')]
    b = [x for x in (md.get('screens') or []) if x.get('src')]
    out, seen = [], set()
    for i in range(max(len(a), len(b))):
        for L in (a, b):
            if i < len(L) and L[i]['src'] not in seen:
                seen.add(L[i]['src'])
                out.append(L[i])
    return out


ARROW_DN = '<svg viewBox="0 0 16 16" width="1em" height="1em" aria-hidden="true"><path d="M8 3v9.5M4 8.8l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
PLAY = '<svg viewBox="0 0 16 16" width="1em" height="1em" aria-hidden="true"><path d="M4.5 2.8v10.4L13 8z" fill="currentColor"/></svg>'


# ───────────────────────── sections
def s_top(d):
    b = d.get('brand') or {}
    logo = ''
    if b.get('logo'):
        logo = f'<img src="{M}{e(b["logo"])}" alt="{e(b.get("name")) if b.get("logo_wordmark") else ""}">'
    name = '' if b.get('logo_wordmark') and b.get('logo') else f'<span>{e(b.get("name"))}</span>'
    nav = ''.join(f'<a href="{e(n.get("h"))}">{e(n.get("t"))}</a>' for n in d.get('nav') or [] if n.get('t'))
    si = d.get('signin') or {}
    signin = f'<a class="signin" href="{e(si.get("h"))}">{e(si["t"])}</a>' if si.get('t') else ''
    c = d.get('cta') or {}
    long = len(c.get('t') or '') > 16          # a long label does not fit beside the logo on a phone: it moves into the menu
    cta = btn(c, 'glass', 'sm long' if long else 'sm')
    menu = ''
    if long and c.get('h'):
        signin += f'<a class="m-cta" href="{e(c["h"])}">{e(c["t"])}</a>'
    if nav or signin:
        menu = (f'<details class="menu"><summary aria-label="Menu"><i></i><i></i></summary>'
                f'<nav aria-label="Menu">{nav}{signin}</nav></details>')
    return f'''<header class="top" id="top">
<a class="logo" href="{e(b.get("home") or "#")}">{logo}{name}</a>
<nav class="nav" aria-label="Primary">{nav}</nav>
<div class="acts">{signin}{cta}{menu}</div>
</header>'''


def s_hero(d):
    h = dict(d.get('hero') or {})
    h['title'] = h.get('title') or (d.get('brand') or {}).get('name')  # the page's one heading: the client's title, else its name
    if not h.get('title'):
        return ''
    steps = [s.get('k') for s in ((d.get('steps') or {}).get('items') or []) if s.get('k')]
    pill = ''
    if steps:
        words = ''.join(f'<span class="pw{" on" if i == 0 else ""}">{e(w)}</span>' for i, w in enumerate(steps))
        pill = f'<span class="pill" aria-hidden="true">{words}</span>'
    # the kicker and its changing pill words stand in the line above the heading, outside it: the h1 is the client's
    # title whole, as every template's is
    sent = f'<p class="sent"><span class="w">{e(h["kicker"])}</span>{pill}</p>' if h.get('kicker') else ''
    # the reference has a glass prompt panel here; with a client's sentence in it, it looked like an input that is not
    # one — so the sentence stands as a plain line of display type and there is no panel and no round button
    box = f'<p class="say">{e(h["text"])}</p>' if h.get('text') else ''
    note = f'<p class="note">{e(h["text2"])}</p>' if h.get('text2') else ''
    md = d.get('media') or {}
    v = md.get('video') or {}
    play = ''
    if v.get('src'):
        play = (f'<button class="play" type="button" data-film aria-haspopup="dialog"><span class="pb gb">{PLAY}</span>'
                f'<span class="shim">{e(v.get("alt") or "")}</span></button>')
    trust = [t for t in d.get('trust') or [] if t]
    mq = ''
    if trust:
        row = ''.join(f'<span>{e(t)}</span>' for t in trust)
        mq = (f'<div class="mq"><div class="mq-t"><div class="mq-r">{row}</div>'
              f'<div class="mq-r" aria-hidden="true">{row}</div></div></div>')
    award = f'<p class="award">{e(h["note"])}</p>' if h.get('note') else ''
    bar = ''
    if play or mq or award:
        bar = f'<div class="bar">{play or "<span></span>"}{mq or "<span></span>"}{award or "<span></span>"}</div>'
    st = d.get('statement') or {}
    scene = ''
    thumbs = ''
    if st.get('title'):
        p = f'<p>{e(st["text"])}</p>' if st.get('text') else ''
        scene = f'<div class="scene"><h2 class="h2">{e(st["title"])}</h2>{p}</div>'
        ps = pool(d)
        if ps:
            thumbs = '<div class="thumbs" aria-hidden="true">' + ''.join(
                f'<figure class="th" style="--r:{x["w"] / x["h"]:.4f}">{pic(x, lazy=i > 3)}</figure>'
                for i, x in enumerate(ps) if x.get('w') and x.get('h')) + '</div>'
    film = ''
    if v.get('src'):
        post = f' poster="{M}{e(v["poster"])}"' if v.get('poster') else ''
        film = (f'<dialog class="film" aria-label="{e(v.get("alt") or "")}"><video src="{M}{e(v["src"])}"{post} controls '
                f'playsinline preload="none" width="{int(v.get("w") or 16)}" height="{int(v.get("h") or 9)}"></video>'
                f'<form method="dialog"><button class="x" aria-label="×">×</button></form></dialog>')
    return f'''<section class="hero" data-scene="hero">
<div class="hero-pin">{sky(d, "hero")}
<div class="hero-main">
<div class="hero-c">
<div class="hl">{sent}<h1 class="claim">{e(h["title"])}</h1></div>
{box}{note}{pair(h.get("secondary"), h.get("primary"))}
</div>
<div class="hero-b"><a class="hint" href="#after-hero" aria-label="↓">{ARROW_DN}</a>{bar}</div>
</div>
{scene}{thumbs}
</div>{film}
</section><span id="after-hero"></span>'''


def sky(d, where, at='center top'):
    """the one picture family of the page: the client's made sky. The reference holds a moving field of light behind the
    whole page; ours is the same sky again in each open space of the page (`where`: hero, how, caps, plans, close), in
    another crop each time (`at`), always clear of small text. '' when the client has no sky, and on a dark page
    when the sky is a light picture (CONTRACT.md: a dark page never takes a light picture as a ground)."""
    pal = d.get('palette') or {}
    m = ((d.get('media') or {}).get('made') or {}).get('sky') or {}
    if not (isinstance(m, dict) and m.get('src')):
        return ''
    if _lum(pal.get('ground') or '#000000') < .45 and m.get('tone') == 'light':
        return ''
    return (f'<div class="sky sk-{where}" data-slot="sky" aria-hidden="true">'
            f'<i style="background-image:url({M}{e(m["src"])});background-position:{at}"></i></div>')


def s_how(d):
    s = d.get('steps') or {}
    items = [x for x in s.get('items') or [] if x.get('title') or x.get('k')]
    if not items:
        return ''
    md = d.get('media') or {}
    meta = {x['src']: x for x in (md.get('screens') or []) + (md.get('phones') or []) + (md.get('photos') or []) if x.get('src')}
    pics, lis = '', ''
    for i, x in enumerate(items):
        m = meta.get(x.get('img') or '')
        if x.get('img'):
            m = dict(m or {'src': x['img']})
            m.setdefault('alt', x.get('title') or '')
            pics += f'<div class="how-p{" on" if i == 0 else ""}" data-i="{i}">{pic(m, lazy=True)}</div>'
        c = x.get('cta') or {}
        link = f'<a class="tl" href="{e(c.get("h"))}">{e(c["t"])}</a>' if c.get('t') else ''
        lis += (f'<li class="ac{" on" if i == 0 else ""}"><span class="ic"><b>{i + 1}</b>'
                f'<svg viewBox="0 0 48 48" aria-hidden="true"><rect x="1" y="1" width="46" height="46" rx="11" pathLength="100"/></svg></span>'
                f'<div class="ac-t"><h3>{e(x.get("k") or x.get("title"))}</h3><div class="ac-b"><div>'
                f'{"<p class=ac-h>" + e(x["title"]) + "</p>" if x.get("k") and x.get("title") else ""}'
                f'<p>{e(x.get("text"))}</p>{link}</div></div></div></li>')
    head = f'<h2 class="h2">{e(s["title"])}</h2>' if s.get('title') else ''
    h = d.get('hero') or {}
    return f'''<section class="how" data-scene="how" data-n="{len(items)}">
<div class="how-pin">{sky(d, "how", "left 70%")}<div class="how-g">
<div class="how-w">{pics}</div>
<div class="how-x"><div class="how-h">{head}{pair(h.get("secondary"), h.get("primary"))}</div>
<ol class="acl">{lis}</ol><div class="dots" aria-hidden="true">{"<i></i>" * len(items)}</div></div>
</div></div>
</section>'''


def s_figures(d):
    fs = [f for f in d.get('figures') or [] if f.get('v')]
    if not fs:
        return ''
    cards = ''.join(f'<li class="card gb"><p class="fv">{e(f["v"])}</p><p class="fl">{e(f.get("l"))}</p></li>' for f in fs)
    return f'<section class="figs"><ul class="cards n{min(len(fs), 4)}">{cards}</ul></section>'


def s_caps(d):
    links = [x for x in d.get('links') or [] if x.get('t')]
    f = d.get('features') or {}
    feats = [x for x in f.get('items') or [] if x.get('t')]
    if not links and not feats:
        return ''
    md = d.get('media') or {}
    vis = [x for x in (md.get('screens') or []) if x.get('src')] or pool(d)
    panels = ''
    for i, x in enumerate(links):
        big = x.get('d') or x['t']
        b = btn({'t': x['t'], 'h': x.get('h')}, 'glass') if x.get('d') else ''
        v = f'<div class="pv">{pic(vis[i % len(vis)])}</div>' if vis else ''
        panels += (f'<article class="pn"><div class="pt"><h2 class="h2">{"" if not x.get("h") or b else ""}{e(big)}</h2>'
                   f'{"<div class=btns>" + b + "</div>" if b else ""}</div>{v}</article>')
    ring = ''
    if feats:
        ps = pool(d)
        tiles = ''
        if ps:
            n = 8
            tiles = ''.join(f'<figure class="wt" style="--k:{k}">{pic(ps[k % len(ps)])}</figure>' for k in range(n))
        b = d.get('brand') or {}
        mark = f'<img src="{M}{e(b["logo"])}" alt="">' if b.get('logo') else ''
        lis = ''.join(
            f'<li class="ac{" on" if i == 0 else ""}"><span class="ic"><b>{i + 1}</b>'
            f'<svg viewBox="0 0 48 48" aria-hidden="true"><rect x="1" y="1" width="46" height="46" rx="11" pathLength="100"/></svg></span>'
            f'<div class="ac-t"><h3>{e(x["t"])}</h3><div class="ac-b"><div><p>{e(x.get("d"))}</p></div></div></div></li>'
            for i, x in enumerate(feats))
        head = f'<h2 class="h2">{e(f["title"])}</h2>' if f.get('title') else ''
        txt = f'<p class="lead">{e(f["text"])}</p>' if f.get('text') else ''
        h = d.get('hero') or {}
        ring = f'''<section class="ring" data-n="{len(feats)}">
<div class="wheel" aria-hidden="true"><div class="orb"></div><div class="hub"><span class="ticks"></span>{mark}</div><div class="wts">{tiles}</div></div>
<div class="ring-x"><div class="ring-h">{head}{txt}{pair(h.get("secondary"), h.get("primary"))}</div>
<ol class="acl">{lis}</ol><div class="dots" aria-hidden="true">{"<i></i>" * len(feats)}</div></div>
</section>'''
    track = f'<div class="pns">{panels}</div>' if panels else ''
    dots = f'<div class="dots pdots" aria-hidden="true">{"<i></i>" * len(links)}</div>' if len(links) > 1 else ''
    return f'''<div class="caps" data-scene="caps">
<div class="caps-pin">{sky(d, "caps", "right 40%")}<div class="caps-row">{track}{dots}{ring}</div></div>
</div>'''


def s_plans(d):
    p = d.get('plans') or {}
    items = [x for x in p.get('items') or [] if x.get('name')]
    if not items:
        return ''
    cards = ''
    for x in items:
        rows = ''.join(f'<li>{e(r)}</li>' for r in x.get('rows') or [])
        rows = f'<ul class="rows">{rows}</ul>' if rows else ''
        price = ''
        if x.get('price'):
            per = f'<span class="per">{e(x["per"])}</span>' if x.get('per') else ''
            price = f'<p class="price"><span class="pv2">{e(x["price"])}</span>{per}</p>'
        line = f'<p class="pl-d">{e(x["line"])}</p>' if x.get('line') else ''
        cards += (f'<li class="card plan gb{" mk" if x.get("marked") else ""}"><h3>{e(x["name"])}</h3>{line}{price}'
                  f'{btn(x.get("cta"), "hot" if x.get("marked") else "glass", "wide")}{rows}</li>')
    head = f'<h2 class="h2">{e(p["title"])}</h2>' if p.get('title') else ''
    txt = f'<p class="lead">{e(p["text"])}</p>' if p.get('text') else ''
    free = ''
    if p.get('note'):
        free = f'<div class="free gb"><p>{e(p["note"])}</p>{btn(d.get("cta"), "glass")}</div>'
    return f'''<section class="plans" id="plans">
<div class="sh">{head}{txt}</div>
<div class="pz">{sky(d, "plans", "center 30%")}<ul class="cards pc n{min(len(items), 4)}">{cards}</ul>{free}</div>
</section>'''


def s_faq(d):
    f = d.get('faq') or {}
    items = [x for x in f.get('items') or [] if x.get('q') and x.get('a')]
    if not items:
        return ''
    rows = ''.join(
        f'<div class="q{" on" if i == 0 else ""}"><h3><button type="button" aria-expanded="{"true" if i == 0 else "false"}" '
        f'aria-controls="fa{i}"><span>{e(x["q"])}</span><i aria-hidden="true"></i></button></h3>'
        f'<div class="a" id="fa{i}"><div><p>{e(x["a"])}</p></div></div></div>' for i, x in enumerate(items))
    head = f'<div class="faq-h"><h2 class="h2">{e(f["title"])}</h2></div>' if f.get('title') else '<div></div>'
    return f'<section class="faq">{head}<div class="faq-l">{rows}</div></section>'


def s_close(d):
    c = d.get('close') or {}
    if not c.get('title'):
        return ''
    txt = f'<p class="lead">{e(c["text"])}</p>' if c.get('text') else ''
    b = btn(c.get('cta'), 'hot')
    return f'<section class="close">{sky(d, "close", "center 60%")}<h2 class="h1">{e(c["title"])}</h2>{txt}{"<div class=btns>" + b + "</div>" if b else ""}</section>'


def s_foot(d):
    b = d.get('brand') or {}
    f = d.get('foot') or {}
    cols = []
    for group in (d.get('nav') or [], [{'t': x.get('t'), 'h': x.get('h')} for x in d.get('links') or []],
                  [x for x in (d.get('signin'), d.get('cta')) if x]):
        seen, ls = set(), ''
        for x in group:
            if x.get('t') and x.get('h') and (x['t'], x['h']) not in seen:
                seen.add((x['t'], x['h']))
                ls += f'<li><a href="{e(x["h"])}">{e(x["t"])}</a></li>'
        if ls:
            cols.append(f'<ul>{ls}</ul>')
    name = b.get('name') or ''
    n = max(len(name), 4)
    word = f'<p class="word" aria-hidden="true" style="--n:{n}">{e(name)}</p>' if name else ''
    txt = f'<p class="ft">{e(f["text"])}</p>' if f.get('text') else ''
    legal = f'<span>{e(f["legal"])}</span>' if f.get('legal') else ''
    fl = ''.join(f'<a href="{e(x.get("h"))}">{e(x.get("t"))}</a>' for x in f.get('links') or [] if x.get('t'))
    return f'''<footer class="foot">
<div class="fcols">{"".join(cols)}</div>
{word}{txt}
<div class="legal">{legal}<span class="fl">{fl}</span></div>
</footer>'''


# ───────────────────────── the page
CSS = r'''
*,*::before,*::after{box-sizing:border-box}
html{font-size:clamp(14px,calc(100vw / 23.4375),17.5px);-webkit-text-size-adjust:100%;scroll-behavior:smooth}
@media (min-width:1024px){html{font-size:min(16px,calc(100vw / 105))}}
body{margin:0;background:var(--bg);color:var(--ink);font:400 1rem/1.5 Inter,system-ui,sans-serif;-webkit-font-smoothing:antialiased;overflow-x:clip}
img,video{display:block;max-width:100%;height:auto}
a{color:inherit;text-decoration:none}
h1,h2,h3,p,ul,ol,figure{margin:0;padding:0}ul,ol{list-style:none}
button{font:inherit;color:inherit;background:none;border:0;padding:0;cursor:pointer}
:focus-visible{outline:2px solid var(--ink);outline-offset:3px;border-radius:4px}
.hot:focus-visible{outline-offset:4px}
main,.foot{position:relative;z-index:1}main>*{position:relative;z-index:2}main>.hero{z-index:1}
/* the field behind the page: the client's made sky, strongest in the upper right, falling to the ground */
.sky{position:absolute;z-index:-1;overflow:hidden;pointer-events:none}
.sky i{position:absolute;inset:0;background-size:cover}
.sk-hero{inset:0 0 auto 0;height:100vh;height:100svh;z-index:0}
.sk-hero i{inset:-6%;animation:drift 26s ease-in-out infinite alternate}
.sk-hero::after{content:"";position:absolute;inset:0;background:radial-gradient(92% 82% at 100% 0%,rgba(var(--g),.3) 0%,rgba(var(--g),.78) 30%,rgba(var(--g),.96) 52%,rgb(var(--g)) 68%)}
/* the same sky in the page's later open spaces; each is an ellipse that ends inside its own box (no edge, no seam) and
   lies where no small text stands: under the steps' picture, in the lower left of the sideways run, round the plan
   cards (which are solid for it), and between the closing button and the foot */
.sk-how,.sk-caps{display:none}
.pz{position:relative}
.sk-plans{inset:-3.5rem -2.5rem -7.5rem -2.5rem;-webkit-mask:radial-gradient(64% 50% at 50% 46%,#000 0,rgba(0,0,0,.6) 45%,transparent 100%);mask:radial-gradient(64% 50% at 50% 46%,#000 0,rgba(0,0,0,.6) 45%,transparent 100%)}
.sk-close{left:0;right:0;bottom:-8rem;height:22rem;-webkit-mask:radial-gradient(52% 50% at 50% 52%,#000 0,rgba(0,0,0,.55) 40%,transparent 100%);mask:radial-gradient(52% 50% at 50% 52%,#000 0,rgba(0,0,0,.55) 40%,transparent 100%)}
.plans:has(.sky) .card,.plans:has(.sky) .free{background:linear-gradient(rgba(var(--i),.05),rgba(var(--i),.05)),var(--bg);-webkit-backdrop-filter:none;backdrop-filter:none}
@keyframes drift{to{transform:translate3d(-2.5%,2%,0) scale(1.06)}}
.h2,.h1,.hl,.card h3,.fv,.pv2,.word,.ac-h{font-family:"Bricolage Grotesque",Inter,system-ui,sans-serif}
.h2{font-size:3.25rem;font-weight:400;line-height:1;letter-spacing:-.012em;text-wrap:balance}
.h1{font-size:5.5rem;font-weight:400;line-height:1;letter-spacing:-.016em;text-wrap:balance}
.lead{color:var(--mute);font-size:1rem;line-height:1.5;text-wrap:pretty}
/* glass: the reference's panel — 5–10 % ink, an inner light, a hairline whose highlight travels round it in 4 s */
.gb{position:relative;background:rgba(var(--i),.05);box-shadow:0 .125rem .125rem rgba(0,0,0,.15),inset 0 0 .6875rem rgba(var(--i),.16);-webkit-backdrop-filter:blur(.75rem);backdrop-filter:blur(.75rem)}
.gb::before{content:"";position:absolute;inset:0;border-radius:inherit;padding:max(1px,.0625rem);pointer-events:none;background:conic-gradient(from var(--ga,0deg),rgba(var(--i),.12) 0 30%,rgba(var(--i),.5) 40%,rgba(var(--i),.12) 50% 80%,rgba(var(--i),.5) 90%,rgba(var(--i),.12));-webkit-mask:linear-gradient(#000 0 0) content-box exclude,linear-gradient(#000 0 0);mask:linear-gradient(#000 0 0) content-box exclude,linear-gradient(#000 0 0);animation:ga 4s linear infinite}
@property --ga{syntax:"<angle>";inherits:false;initial-value:0deg}
@keyframes ga{to{--ga:360deg}}
.gb:hover::before{animation-play-state:paused}
/* buttons */
.btns{display:flex;flex-wrap:wrap;align-items:center;gap:1.25rem}
.btn{position:relative;display:inline-flex;align-items:center;justify-content:center;height:3rem;padding:0 1.5rem;border-radius:999px;font-size:.875rem;font-weight:500;line-height:1.5;white-space:nowrap;transition:transform .15s,background-color .4s cubic-bezier(.4,0,.2,1),box-shadow .4s cubic-bezier(.4,0,.2,1)}
.btn::before{content:"";position:absolute;inset:-.375rem;border-radius:2.75rem;background:rgba(var(--i),.05);border:1px solid rgba(var(--i),.06);z-index:-1}
.btn.glass{background:rgba(var(--i),.05);color:var(--ink);box-shadow:0 .125rem .125rem rgba(0,0,0,.15),inset 0 0 .6875rem rgba(var(--i),.16),inset 0 0 0 1px rgba(var(--i),.2);-webkit-backdrop-filter:blur(.25rem);backdrop-filter:blur(.25rem)}
.btn.hot{background:var(--acc);color:var(--on);box-shadow:0 .125rem .125rem rgba(0,0,0,.15),inset 0 -.3125rem 1.0625rem var(--glow),inset 0 0 0 1px var(--glow)}
.btn.glass:hover{background:rgba(var(--i),.12)}.btn.hot:hover{box-shadow:0 .125rem .125rem rgba(0,0,0,.15),inset 0 -.6rem 1.4rem var(--glow),inset 0 0 0 1px var(--glow)}
.btn:active{transform:scale(.97)}
.btn.sm{height:2.75rem;padding:0 1.25rem}.btn.wide{display:flex;width:100%}
.roll{display:grid;overflow:hidden;height:1.5em}
.roll span{grid-area:1/1;transition:transform .65s cubic-bezier(.785,.135,.15,.86)}
.roll span+span{transform:translateY(100%);visibility:hidden}
.btn:hover .roll span{transform:translateY(-100%)}.btn:hover .roll span+span{transform:none;visibility:visible}
.tl{display:inline-block;margin-top:.5rem;font-size:.875rem;font-weight:500;text-decoration:underline;text-underline-offset:.2em;text-decoration-color:rgba(var(--i),.4);transition:text-decoration-color .3s}.tl:hover{text-decoration-color:var(--ink)}
/* top */
.top{position:fixed;inset:0 0 auto 0;z-index:50;height:7.125rem;padding:0 2.5rem;display:grid;grid-template-columns:auto 1fr auto;align-items:center;gap:2rem;transition:transform .3s,background-color .3s}
.top.away{transform:translateY(-100%)}
.top.solid{background:linear-gradient(rgba(var(--g),.94) 55%,rgba(var(--g),0))}
.logo{display:inline-flex;align-items:center;gap:.6rem;font:500 1.5rem/1 "Bricolage Grotesque",Inter,sans-serif;letter-spacing:-.02em}
.logo img{flex:none;height:1.6rem;width:auto;max-width:none}
.nav{display:flex;gap:1.75rem;font-size:1rem}
.nav a,.signin{transition:opacity .3s}.nav a:hover,.signin:hover{opacity:.6}
.acts{display:flex;align-items:center;gap:1.9rem}
.signin{font-size:.875rem;font-weight:500}
.menu{display:none}.acts>.m-cta{display:none}
/* opening */
.hero{position:relative}
.hero-pin{position:relative;min-height:100vh;min-height:100svh}

.hero-main,.scene,.thumbs{position:relative;z-index:1}
.hero-main{min-height:100vh;min-height:100svh;display:flex;flex-direction:column;padding:7.125rem 2.5rem 0;text-align:center}
.hero-c{flex:none;margin:auto;width:100%;max-width:60rem;display:flex;flex-direction:column;align-items:center;padding:1rem 0}
.hl{display:flex;flex-direction:column;align-items:center;gap:.7rem;margin-bottom:2.5rem;font-weight:500}
.sent{display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:.4rem .65rem;font-size:2.5rem;line-height:1.16;letter-spacing:-.01em;color:var(--dim)}
.pill{position:relative;display:inline-grid;align-items:center;height:1.36em;padding:0 .52em;border-radius:999px;background:rgba(var(--a),.3);color:var(--ink);box-shadow:inset 0 0 0 1px rgba(var(--i),.16),0 .125rem .5rem rgba(0,0,0,.18);-webkit-backdrop-filter:blur(.5rem);backdrop-filter:blur(.5rem);line-height:1;white-space:nowrap;transition:width .36s cubic-bezier(.32,.72,0,1)}
.pw{grid-area:1/1;display:none}.pw.on{display:block}
.js .pw{display:block;opacity:0;filter:blur(.4rem);transform:translateY(.4rem);transition:opacity .26s,transform .36s cubic-bezier(.32,.72,0,1),filter .3s;justify-self:start}
.js .pw.on{opacity:1;filter:none;transform:none}.js .pw.next{transform:translateY(-.4rem)}
.claim{font-size:3.3rem;font-weight:700;line-height:1.1;letter-spacing:-.01em;text-wrap:balance}
.say{max-width:35.6875rem;font-size:1.5rem;line-height:1.35;letter-spacing:-.01em;text-wrap:balance}
.note{max-width:29.5rem;margin:1.2rem auto 1.25rem;font-size:.75rem;line-height:1.4;color:var(--mute);text-wrap:pretty}
.say+.btns,.hl+.btns{margin-top:1.7rem}
.hero .btns{justify-content:center}
.hero-b{flex:none;display:flex;flex-direction:column;align-items:center}
.hint{display:grid;place-items:center;width:2.5rem;height:2.5rem;margin-bottom:1rem;font-size:.9rem;animation:bounce 1s infinite}
@keyframes bounce{0%,100%{transform:translateY(-25%);animation-timing-function:cubic-bezier(.8,0,1,1)}50%{transform:none;animation-timing-function:cubic-bezier(0,0,.2,1)}}
.bar{width:100%;display:grid;grid-template-columns:minmax(0,1fr) minmax(0,42.5rem) minmax(0,1fr);align-items:center;gap:2rem;min-height:4.5rem;border-top:1px solid rgba(var(--i),.1);text-align:left}
.play{display:inline-flex;align-items:center;gap:.75rem;justify-self:start;font-size:.875rem}
.pb{display:grid;place-items:center;width:4.25rem;height:3rem;border-radius:.75rem;background:rgba(var(--i),.15);font-size:1rem;transition:transform .15s}
.play:active .pb{transform:scale(.95)}
.shim{color:var(--mute)}
.shim{animation:shim 6s linear infinite}
@keyframes shim{0%,55%,100%{color:var(--mute)}78%{color:var(--ink)}}
.mq{overflow:hidden;-webkit-mask:linear-gradient(90deg,transparent,#000 12%,#000 88%,transparent);mask:linear-gradient(90deg,transparent,#000 12%,#000 88%,transparent)}
.mq-t{display:flex;width:max-content}
.mq-r{display:flex;gap:2rem;padding-right:2rem;animation:mq 19s linear infinite;font-size:.875rem;color:var(--mute);white-space:nowrap}
@keyframes mq{to{transform:translateX(-100%)}}
.award{justify-self:end;text-align:right;font-size:.875rem;color:var(--ink);opacity:.9}
/* second scene of the opening: the statement, with the client's pictures passing */
.scene{padding:6rem 2.5rem 2rem;text-align:center;display:flex;flex-direction:column;align-items:center}
.scene .h2{max-width:40rem;margin-bottom:1.5rem}.scene p{max-width:38.75rem;color:var(--mute);text-wrap:pretty}
.thumbs{display:flex;flex-wrap:wrap;justify-content:center;align-items:center;gap:1.25rem;padding:2rem 2.5rem 6rem}
.th{width:clamp(7rem,calc(11rem * var(--r)),17rem)}
.th img{width:100%;border-radius:.25rem}
.film{padding:0;border:0;background:transparent;max-width:min(92vw,70rem);overflow:visible}
.film::backdrop{background:rgba(var(--g),.86);-webkit-backdrop-filter:blur(.5rem);backdrop-filter:blur(.5rem)}
.film video{width:auto;max-width:92vw;max-height:84vh;border-radius:1rem}
.film .x{position:absolute;top:-2.75rem;right:0;width:2.25rem;height:2.25rem;border-radius:50%;background:rgba(var(--i),.12);color:var(--ink);font-size:1.25rem;line-height:1}
/* how it works */
.how{position:relative;padding:6.25rem 0}
.how-g{display:grid;grid-template-columns:49.375rem 27.75rem;justify-content:center;column-gap:7.6rem;align-items:center;padding:0 2.5rem}
.how-w{position:relative;display:grid;place-items:center;height:35rem}
.how-p{grid-area:1/1;display:grid;place-items:center;width:100%;height:100%;opacity:0;transition:opacity .5s linear}
.how-p.on{opacity:1}
.how-p img{width:auto;height:auto;max-width:100%;max-height:35rem;border-radius:1rem;box-shadow:0 0 0 1px rgba(var(--i),.12),0 0 0 .3125rem rgba(var(--i),.05)}
.how-h .h2{margin-bottom:2.375rem}.how-h .btns{margin-bottom:4.125rem}
.acl{display:flex;flex-direction:column;gap:.25rem}
.ac{display:flex;align-items:flex-start;padding:1.25rem;border-radius:18px;transition:background-color .5s linear}
.ic{position:relative;flex:none;display:grid;place-items:center;width:3rem;height:3rem;margin-right:1.3rem;border-radius:.75rem;background:rgba(var(--i),.06);font:500 1rem/1 "Bricolage Grotesque",Inter,sans-serif}
.ic b{font-weight:500;color:var(--mute);transition:color .5s}
.ic svg{position:absolute;inset:0;width:100%;height:100%;overflow:visible;display:none}
.ic rect{fill:none;stroke:var(--ink);stroke-width:1.5;stroke-dasharray:100;stroke-dashoffset:calc(100 - var(--p,0) * 100)}
.ac-t{flex:1;min-width:0;display:flex;flex-direction:column;justify-content:center;min-height:3rem}
.ac h3{font:500 1rem/1.5 Inter,system-ui,sans-serif;transition:color .5s}
.ac-b{display:grid;grid-template-rows:1fr;transition:grid-template-rows .5s linear,opacity .5s linear}
.ac-b>div{overflow:hidden}
.ac-b p{padding-top:.375rem;font-size:.875rem;line-height:1.55;color:var(--mute)}
.ac-b .ac-h{color:var(--ink);font-size:1.125rem;line-height:1.25;padding-top:.25rem}
.dots{display:none}
/* figures (no counterpart on the reference; built from its plan card) */
.figs{padding:3.75rem 2.5rem 6.25rem}
.cards{display:grid;gap:1rem;justify-content:center}
.cards.n1{grid-template-columns:minmax(0,24.25rem)}.cards.n2{grid-template-columns:repeat(2,minmax(0,24.25rem))}.cards.n3{grid-template-columns:repeat(3,minmax(0,24.25rem))}.cards.n4{grid-template-columns:repeat(4,minmax(0,24.25rem))}
.card{border-radius:1.5rem;padding:2.5rem 2.75rem;text-align:center;overflow:hidden}
.card::after{content:"";position:absolute;top:-2.3rem;left:-2.3rem;width:4.625rem;height:4.625rem;border-radius:50%;background:rgba(var(--i),.5);filter:blur(2.6rem);pointer-events:none}
.fv{font-size:3.25rem;line-height:1;letter-spacing:-.012em}.fl{margin-top:.9rem;font-size:.875rem;line-height:1.5;color:var(--mute);text-wrap:pretty}
/* the sideways run of panels, then the wheel */
.caps{position:relative}
.caps-row{display:flex;flex-direction:column;gap:7.5rem;padding:6.25rem 2.5rem}
.pns{display:flex;flex-direction:column;gap:7.5rem}
.pn{display:flex;align-items:center;justify-content:space-between;gap:4rem}
.pt{flex:0 1 35rem;display:flex;flex-direction:column;gap:1.2rem;min-width:0}
.pt .btns{margin-top:1.4rem}
.pv{flex:0 1 auto;min-width:0}
.pv img{width:auto;height:auto;max-width:min(46rem,100%);max-height:29.5rem;border-radius:1rem;box-shadow:0 0 0 1px rgba(var(--i),.12),0 0 0 .3125rem rgba(var(--i),.05)}
.ring{position:relative;display:grid;grid-template-columns:1fr 36.75rem;gap:4rem;align-items:center}
.wheel{position:relative}
.orb,.hub{display:none}
.wts{display:flex;flex-wrap:wrap;gap:1rem;align-items:center}
.wt{flex:0 1 auto}.wt img{width:auto;height:auto;max-height:13rem;max-width:16rem;border-radius:.25rem}
.wt:nth-child(n+5){display:none}
.ring-h{margin-bottom:2.5rem}.ring-h .h2{line-height:1.1}.ring-h .lead{margin-top:1.2rem}.ring-h .btns{margin-top:2rem}
/* plans */
.plans{padding:9rem 2.5rem 8.125rem}
.sh{max-width:40rem;margin:0 auto 4rem;text-align:center}.sh .h2{margin-bottom:2rem}
.plan{display:flex;flex-direction:column;align-items:center}
.plan h3{font-size:1.5rem;font-weight:500;line-height:1.4}
.pl-d{margin-top:.25rem;min-height:3rem;color:var(--mute);text-wrap:pretty}
.price{display:flex;flex-direction:column;align-items:center;margin:1.6rem 0 0}
.pv2{font-size:3.25rem;line-height:1.1;letter-spacing:-.012em}.per{margin-top:.5rem;font-size:.875rem;color:var(--mute)}
.plan .btn{margin:1.75rem 0}
.rows{align-self:stretch;display:flex;flex-direction:column;gap:.375rem;text-align:left;font-size:.875rem;line-height:1.5}
.rows li{position:relative;padding:.25rem 0 .25rem 1rem}
.rows li::before{content:"";position:absolute;left:0;top:.8em;width:.375rem;height:.375rem;border-radius:50%;background:var(--acc)}
.free{display:flex;align-items:center;justify-content:space-between;gap:2rem;max-width:calc(4 * 24.25rem + 3rem);margin:2rem auto 0;padding:2rem;border-radius:1.5rem;background:rgba(var(--i),.03)}
.free p{max-width:60rem;font-size:.875rem;line-height:1.5;color:var(--mute);text-wrap:pretty}.free .btn{flex:none}
/* questions */
.faq{display:grid;grid-template-columns:31.6rem 49.375rem;justify-content:center;column-gap:6.4rem;align-items:start;padding:6.25rem 2.5rem}
.faq-h{position:sticky;top:8rem;padding-top:3.75rem}
.q{border-bottom:1px solid rgba(var(--i),.1)}
.q button{display:flex;justify-content:space-between;align-items:center;gap:.9375rem;width:100%;padding:1.25rem 0;text-align:left;font-size:1.125rem;line-height:1.4}
.q h3{font:inherit}
.q i{position:relative;flex:none;width:1.875rem;height:1.875rem;border:1px solid rgba(var(--i),.25);border-radius:50%;transition:transform .3s}
.q i::before,.q i::after{content:"";position:absolute;left:50%;top:50%;width:.625rem;height:1.5px;margin:-.75px 0 0 -.3125rem;background:var(--ink);border-radius:1px}
.q i::after{transform:rotate(90deg)}
.q.on i{transform:rotate(45deg)}
.a{display:grid;grid-template-rows:1fr;transition:grid-template-rows .3s}
.a>div{overflow:hidden}.a p{max-width:40rem;padding-bottom:1.25rem;color:var(--mute);text-wrap:pretty}
.js .q:not(.on) .a{grid-template-rows:0fr}.js .q:not(.on) .a>div{visibility:hidden}
/* close */
.close{padding:7.5rem 2.5rem;text-align:center;display:flex;flex-direction:column;align-items:center}
.close .h1{max-width:75.5rem}.close .lead{margin-top:.75rem;font-size:1.125rem;max-width:44rem}.close .btns{margin-top:4rem;justify-content:center}
/* foot */
.foot{position:relative;z-index:1;padding:7.5rem 2.5rem 2.5rem}
.fcols{display:grid;grid-template-columns:repeat(4,17.75rem);gap:1.25rem;justify-content:end;margin-bottom:5rem}
.fcols ul{display:flex;flex-direction:column;gap:.875rem;font-size:.875rem}
.fcols a,.legal a{color:var(--mute);transition:color .2s}.fcols a:hover,.legal a:hover{color:var(--ink)}
.word{font-weight:500;font-size:min(24rem,calc((100vw - 5rem) / (var(--n) * .43)));line-height:.86;letter-spacing:-.045em;white-space:nowrap;text-align:center;padding:1.25rem 0 .5rem;border-top:1px solid rgba(var(--i),.1);overflow:hidden}
.ft{max-width:62rem;margin-top:2rem;font-size:.875rem;line-height:1.5;color:var(--mute)}
.legal{display:flex;justify-content:space-between;gap:2rem;margin-top:3.125rem;font-size:.875rem;color:var(--mute)}
.fl{display:flex;flex-wrap:wrap;gap:.75rem 2.5rem}

/* ── the scroll scenes: only with scripts and without a reduced-motion preference ── */
.mo .hero{height:var(--hh,400vh);margin-bottom:-100vh;margin-bottom:-100svh}
.mo .hero-pin{position:sticky;top:0;height:100vh;height:100svh;overflow:hidden}
.mo .hero-main{position:absolute;inset:0;z-index:2;will-change:opacity}
.mo .hero-c{will-change:transform}
.mo .scene{position:absolute;inset:0;z-index:2;justify-content:center;padding:0 2.5rem;opacity:0;pointer-events:none}
.mo .thumbs{position:absolute;inset:0;z-index:1;display:block;padding:0}
.mo .th{position:absolute;top:0;left:0;width:var(--w);will-change:transform;transform:translate3d(var(--x),110vh,0)}
@media (min-width:1024px){
.mo .how{height:var(--hh,700vh);padding:0}
.mo .how-pin{position:sticky;top:0;height:100vh;display:flex;align-items:center;overflow:hidden}
.mo .sk-how{display:block;inset:0;-webkit-mask:radial-gradient(38% 34% at 24% 116%,#000 0,rgba(0,0,0,.6) 45%,transparent 100%);mask:radial-gradient(38% 34% at 24% 116%,#000 0,rgba(0,0,0,.6) 45%,transparent 100%)}
.mo .sk-caps{display:block;inset:0;-webkit-mask:radial-gradient(42% 40% at 0% 112%,#000 0,rgba(0,0,0,.6) 45%,transparent 100%);mask:radial-gradient(42% 40% at 0% 112%,#000 0,rgba(0,0,0,.6) 45%,transparent 100%)}
.mo .how-g{width:100%;align-items:start}
.mo .how-w{will-change:transform;margin-top:2.9rem}
.mo .how-x{will-change:opacity}
.mo .ac:not(.on) .ac-b{grid-template-rows:0fr;opacity:0}
.mo .ac.on{background:rgba(var(--i),.04);box-shadow:inset 0 0 0 1px rgba(var(--i),.07)}
.mo .ac:not(.on) h3{color:var(--mute)}.mo .ac.on .ic b{color:var(--ink)}
.mo .ac.on .ic svg{display:block}
.mo .caps{height:var(--hh,900vh)}
.mo .caps-pin{position:sticky;top:0;height:100vh;overflow:hidden}
.mo .caps-row{flex-direction:row;align-items:center;gap:0;height:100%;width:max-content;padding:0;will-change:transform}
.mo .pns{flex-direction:row;gap:14rem;padding-left:0}
.mo .pn{flex:none;gap:6rem;justify-content:flex-start}
.mo .pt{flex:none;width:max-content;max-width:35rem}
.mo .pv{flex:none}.mo .pv img{max-width:46rem}
.mo .pns~.ring{margin-left:22rem}
.mo .ring{flex:none;width:100vw;height:100vh;display:block}
.mo .wheel{position:absolute;left:5rem;top:50%;width:0;height:0}
.mo .orb{display:block;position:absolute;left:-24.125rem;top:-24.125rem;width:48.25rem;height:48.25rem;border:.125rem solid rgba(var(--i),.06);border-radius:50%}
.mo .hub{display:grid;place-items:center;position:absolute;left:-11.75rem;top:-11.75rem;width:23.5rem;height:23.5rem}
.mo .hub img{width:auto;max-width:10.1875rem;max-height:6rem}
.mo .ticks{position:absolute;inset:0;border-radius:50%;border:1px dashed rgba(var(--i),.22);will-change:transform}
.mo .ticks::after{content:"";position:absolute;right:1.4rem;top:50%;width:.5rem;height:.5rem;border-radius:50%;background:var(--ink)}
.mo .wts{display:block}
.mo .wt,.mo .wt:nth-child(n+5){display:block;position:absolute;left:0;top:0;will-change:transform}
.mo .wt img{max-height:28rem;max-width:21rem;border-radius:.25rem}
.mo .ring-x{position:absolute;left:65.8rem;top:0;bottom:0;width:36.75rem;display:flex;flex-direction:column;justify-content:center}
.mo .ring-h .lead{display:none}
}
/* ── phone and tablet: the reference stacks, and turns the lists into swipe rows with dots ── */
@media (max-width:1023px){
.sk-hero::after{background:radial-gradient(150% 42% at 100% 0%,rgba(var(--g),.55) 0%,rgba(var(--g),.84) 26%,rgba(var(--g),.97) 44%,rgb(var(--g)) 60%)}
.top{height:4.5rem;padding:0 1.25rem;grid-template-columns:auto 1fr;gap:1rem}
.top .nav,.top .signin{display:none}.acts{justify-self:end;gap:.75rem}
.logo{font-size:1.35rem}.logo img{height:1.5rem}.top .btn.long{display:none}
.btn.sm{height:2.5rem;padding:0 1.1rem}
.menu{display:block;position:relative}
.menu summary{display:grid;place-content:center;gap:.3rem;width:2.5rem;height:2.5rem;border-radius:50%;background:rgba(var(--i),.08);box-shadow:inset 0 0 0 1px rgba(var(--i),.16);list-style:none;cursor:pointer}
.menu summary::-webkit-details-marker{display:none}
.menu summary i{display:block;width:.95rem;height:1.5px;background:var(--ink);transition:transform .3s}
.menu[open] summary i:first-child{transform:translateY(.19rem) rotate(45deg)}.menu[open] summary i:last-child{transform:translateY(-.19rem) rotate(-45deg)}
.menu nav{position:absolute;right:0;top:3.1rem;min-width:13rem;display:flex;flex-direction:column;gap:.25rem;padding:.75rem;border-radius:1.25rem;background:var(--bg);box-shadow:inset 0 0 0 1px rgba(var(--i),.16),0 1rem 2.5rem rgba(0,0,0,.35)}
.menu nav a{display:block;padding:.6rem .75rem;border-radius:.6rem;font-size:1rem;opacity:1}
.h2{font-size:1.75rem}.h1{font-size:2.25rem}
.lead,.scene p{font-size:.875rem}
.btn{font-size:.875rem;height:2.75rem;padding:0 1.6rem}.btns{gap:.8rem}
.hero-main{padding:4.5rem 1.25rem 0}
.hl{gap:.42rem;margin-bottom:1.5rem}
.sent{flex-direction:column;font-size:1.5rem;gap:.42rem}
.claim{font-size:1.77rem}
.say{font-size:1.125rem}
.note{font-size:.75rem;margin:1.5rem auto 1.4rem}
.bar{grid-template-columns:auto minmax(0,1fr);gap:1rem;min-height:4rem}
.play .shim,.award{display:none}.pb{width:2.5rem;height:1.875rem;border-radius:.5rem;font-size:.7rem}
.bar>span:first-child{display:none}.bar:has(>span:first-child){grid-template-columns:minmax(0,1fr)}
.mq-r{gap:1.25rem;padding-right:1.25rem}
.scene{padding:4rem 1.25rem 1.5rem}.scene .h2{max-width:17rem;margin-bottom:1.2rem}.scene p{max-width:17rem}
.mo .scene{padding:0 1.25rem}
.thumbs{padding:1rem 1.25rem 4rem;gap:.75rem}.th{width:clamp(5rem,calc(7rem * var(--r)),10rem)}
.how{padding:4rem 0}
.how-g{display:flex;flex-direction:column;padding:0;text-align:center}
.how-x{display:contents}
.how-h{order:1;padding:0 1.25rem}.how-h .h2{margin-bottom:1.5rem}.how-h .btns{justify-content:center;margin-bottom:2.5rem}
.how-w{order:2;width:100%;height:22rem;padding:0 1.25rem}
.how-p img{max-height:22rem;max-width:100%;border-radius:.75rem}
.acl{order:3;flex-direction:row;gap:0;width:100%;margin-top:1.5rem;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none;-webkit-overflow-scrolling:touch}
.acl::-webkit-scrollbar{display:none}
.ac{flex:0 0 100%;scroll-snap-align:center;flex-direction:column;align-items:center;padding:0 2.75rem;text-align:center}
.ic{margin:0 0 .9rem}.ac-t{min-height:0}
.ac-b p{padding-top:.25rem}
.js .dots{order:4;display:flex;justify-content:center;gap:.5rem;margin-top:1.5rem}
.dots i{width:.375rem;height:.375rem;border-radius:50%;background:rgba(var(--i),.3);transition:background-color .3s}.dots i.on{background:var(--ink)}
.figs{padding:1rem 1.25rem 4rem}
.cards,.cards.n2,.cards.n3,.cards.n4{grid-template-columns:repeat(2,minmax(0,1fr));gap:.75rem}
.figs .card{padding:1.5rem 1rem}.fv{font-size:1.75rem}
.caps-row{padding:4rem 0;gap:4rem}
.pns{flex-direction:row;gap:0;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none}
.pns::-webkit-scrollbar{display:none}
.pn{flex:0 0 100%;scroll-snap-align:center;flex-direction:column;justify-content:flex-start;gap:2.5rem;padding:0 1.25rem;text-align:center}
.pt{flex:none;align-items:center}.pt .btns{justify-content:center;margin-top:.6rem}
.pv img{max-height:18rem;border-radius:.75rem}
.js .pdots{order:0;margin-top:-2rem}
.ring{display:flex;flex-direction:column;gap:0;text-align:center}
.ring-x{display:contents}
.ring-h{order:1;padding:0 1.25rem;margin-bottom:2.5rem}.ring-h .btns{justify-content:center;margin-top:1.5rem}
.wheel{order:2;padding:0 1.25rem}.wts{justify-content:center}.wt:nth-child(n+2){display:none}.wt img{max-height:13rem;max-width:100%}
.ring .acl{margin-top:1.75rem}
.sk-plans{inset:-2.2rem -1.25rem -4.5rem -1.25rem}.sk-close{bottom:-4rem;height:15rem}
.plans{padding:5rem 1.25rem}.sh{margin-bottom:2.5rem}.sh .h2{margin-bottom:.75rem}
.plans .cards{grid-template-columns:minmax(0,22rem)}
.card{padding:2rem 1.75rem}.plan h3{font-size:1.5rem}.pv2{font-size:1.75rem}
.free{flex-direction:column;align-items:flex-start;padding:1.5rem;max-width:22rem}
.faq{display:block;padding:2.5rem 1.25rem}.faq-h{position:static;padding:0;margin-bottom:2.5rem}
.q button{font-size:1rem;padding:1rem 0}.a p{font-size:.875rem}
.close{padding:5rem 1.25rem}.close .lead{font-size:1rem}.close .btns{margin-top:2.5rem}
.foot{padding:4rem 1.25rem 2rem}
.fcols{grid-template-columns:repeat(2,minmax(0,1fr));justify-content:stretch;gap:2rem 1.25rem;margin-bottom:3rem}
.fcols ul{font-size:1rem}
.word{font-size:min(8rem,calc((100vw - 2.5rem) / (var(--n) * .43)))}
.legal{flex-direction:column;align-items:center;gap:1rem;text-align:center;margin-top:2rem}.fl{justify-content:center}
.ft{text-align:center}
}
/* on a phone a pill never runs past the box it stands in: a label longer than the box takes a second line (the hover
   roll has no hover to answer there, so its second copy is not drawn) */
@media (max-width:1023px){.btn{max-width:100%;height:auto;min-height:2.75rem;padding-block:.55rem;white-space:normal;text-align:center}.btn .roll{height:auto}.btn .roll>span[aria-hidden]{display:none}.btn.sm{min-height:2.5rem;padding-block:.45rem}}
@media (max-width:1023px) and (min-width:700px){.plans .cards.n2,.plans .cards.n3,.plans .cards.n4{grid-template-columns:repeat(2,minmax(0,22rem))}.figs .cards{grid-template-columns:repeat(4,minmax(0,1fr))}.free{max-width:45rem}}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important;scroll-behavior:auto!important}.mq{-webkit-mask:none;mask:none}.mq-t{width:auto}.mq-r{flex-wrap:wrap;justify-content:center;padding:0;gap:.5rem 1.5rem}.mq-r+.mq-r{display:none}.hint{display:none}}
'''

JS = r'''
(()=>{const R=document.documentElement,still=matchMedia('(prefers-reduced-motion:reduce)').matches;R.classList.add('js');
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
const cl=(v,a=0,b=1)=>Math.min(b,Math.max(a,v)),io=t=>t<.5?2*t*t:1-Math.pow(-2*t+2,2)/2,seg=(u,a,b)=>cl((u-a)/(b-a));
/* top: away going down, back going up (measured: .3s) */
const top=$('.top');let ly=scrollY;addEventListener('scroll',()=>{const y=scrollY;if(top){if(y>220&&y>ly+2)top.classList.add('away');else if(y<ly-2||y<220)top.classList.remove('away');top.classList.toggle('solid',y>220);}ly=y;},{passive:true});
const menu=$('.menu');if(menu)menu.addEventListener('click',e=>{if(e.target.closest('nav a'))menu.open=false;});
/* film */
const film=$('.film'),pl=$('[data-film]');if(film&&pl&&film.showModal){const v=$('video',film);pl.addEventListener('click',()=>{film.showModal();v.play().catch(()=>{});});film.addEventListener('close',()=>v.pause());film.addEventListener('click',e=>{if(e.target===film)film.close();});}
/* questions */
$$('.q button').forEach(b=>b.addEventListener('click',()=>{const q=b.closest('.q'),on=!q.classList.contains('on');q.classList.toggle('on',on);b.setAttribute('aria-expanded',on);}));
/* the pill in the opening line: one word every 3.3 s (measured), out down and blurred, in from above */
const pill=$('.pill');if(pill){const ws=$$('.pw',pill);const fit=w=>{pill.style.width=(w.offsetWidth+parseFloat(getComputedStyle(pill).paddingLeft)*2)+'px';};
 const set=()=>fit(ws.find(w=>w.classList.contains('on'))||ws[0]);set();if(document.fonts&&document.fonts.ready)document.fonts.ready.then(set);addEventListener('resize',set);
 if(!still&&ws.length>1){let i=0;setInterval(()=>{if(document.hidden)return;const a=ws[i];i=(i+1)%ws.length;const b=ws[i];a.classList.remove('on');b.classList.add('next');void b.offsetWidth;setTimeout(()=>{b.classList.remove('next');b.classList.add('on');fit(b);},120);},3300);}}
/* swipe rows: dots follow */
$$('.acl,.pns').forEach(row=>{const par=row.classList.contains('pns')?row.parentElement:row.parentElement,dots=$$(row.classList.contains('pns')?'.pdots i':':scope > .dots i',par);if(!dots.length)return;
 const sec=row.closest('.how,.ring');const upd=()=>{if(!row.clientWidth||row.scrollWidth<=row.clientWidth+4){return;}const i=Math.round(row.scrollLeft/row.clientWidth);dots.forEach((d,k)=>d.classList.toggle('on',k===i));if(sec&&sec.classList.contains('how'))$$('.how-p',sec).forEach(p=>p.classList.toggle('on',+p.dataset.i===i));};
 dots.forEach((d,k)=>d.classList.toggle('on',k===0));row.addEventListener('scroll',upd,{passive:true});});
if(still)return;R.classList.add('mo');
const wide=matchMedia('(min-width:1024px)');
/* ── scene 1: the opening holds; its content shrinks and leaves; the statement arrives while pictures pass ── */
const hero=$('.hero'),hm=$('.hero-main'),hc=$('.hero-c'),sc=$('.scene'),ths=$$('.th');let HE=1200;
/* holds, in px of scroll at a 900-high window — each the least that still shows its content (the reference: 4410 / 1300+1200 a row / .891 px sideways per px, 900 a row) */
const H0=250,HS=420,HT=120,SP=1.6,RS=330,RT=260;
const how=$('.how'),hw=$('.how-w'),hx=$('.how-x'),caps=$('.caps'),row=$('.caps-row'),ring=$('.ring');let CT=0,CR=0;
function lay(){const vw=innerWidth,vh=innerHeight,k=vh/900,rem=parseFloat(getComputedStyle(R).fontSize),w=wide.matches;
 if(hero){ /* lanes measured at 1440: two cut by the edges, two nearer the middle; the middle stays free for the words */
  const lanes=w?[[-.052,.125],[.905,.135],[.155,.135],[.705,.135],[-.045,.14],[.875,.15],[.165,.125],[.715,.125]]:[[0,0],[0,0]];
  ths.forEach((t,i)=>{const r=parseFloat(t.style.getPropertyValue('--r'))||1;let x,wd;
   if(w){const L=lanes[i%8];wd=L[1]*vw*(r<.8?.82:1);if(r>1.2)wd=Math.min(wd*1.08,.14*vw);x=L[0]*vw;if(i%4===1||i%8===5)x=Math.min(x,vw-wd*.62);}
   else{wd=(r<.8?.2:r>2.4?.5:.27)*vw;x=i%2?vw-Math.min(wd*.62,54):-(wd-Math.min(wd*.62,54));}
   t.style.setProperty('--w',wd+'px');t.style.setProperty('--x',x+'px');t._h=wd/r;t._x=x;t._y0=i*(w?90:120);t._s=(w&&(i%4>1))?1.3:1.08;});
  HE=sc?1800:700;hero.style.setProperty('--hh',(HE*k+vh)+'px');}
 if(how){const n=+how.dataset.n||1;how.style.setProperty('--hh',w?((H0+HS*n+HT)*k+vh)+'px':'auto');}
 if(caps){if(w&&row){row.style.transform='none';CR=ring?ring.offsetLeft:Math.max(0,row.scrollWidth-vw*.6);CT=CR+51.125*rem;const n=ring?(+ring.dataset.n||1):0;
   caps.style.setProperty('--hh',(CT/SP-607*k+n*RS*k+(ring?RT*k:0)+vh)+'px');caps.style.marginBottom=ring?'-30vh':'';}else{caps.style.setProperty('--hh','auto');caps.style.marginBottom='';if(row)row.style.transform='';}}
 tick(true);}
let cur=-1;
function tick(force){const y=scrollY,vh=innerHeight,k=vh/900,w=wide.matches,rem=parseFloat(getComputedStyle(R).fontSize);
 if(hero){const u=(y-hero.offsetTop)/k;if(u<HE+900||force){
  const sk=$('.sky',hero);if(sk)sk.style.opacity=1-seg(u,HE-560,HE-200);const o=1-seg(u,250,600);hm.style.opacity=o;hm.style.visibility=o<=0?'hidden':'';hc.style.transform='scale('+(1-.4*io(seg(u,200,700)))+')';
  if(sc){const so=seg(u,520,720)*(1-seg(u,HE-560,HE-260));sc.style.opacity=so;const tb=$('.thumbs',hero);if(tb)tb.style.opacity=1-seg(u,HE-560,HE-260);sc.style.pointerEvents=so>.6?'auto':'none';}
  ths.forEach(t=>{const ty=(900+t._y0-(u-350)*t._s)*k;t.style.transform='translate3d('+t._x+'px,'+ty+'px,0)';});}}
 if(how&&w){const u=(y-how.offsetTop)/k,n=+how.dataset.n||1;if(u>-900&&u<H0+HS*n+1300||force){
  hw.style.transform='translate3d('+(18.96*rem*(1-io(seg(u,-700,-60))))+'px,0,0)';const a=io(seg(u,-560,-40));hx.style.opacity=a;hx.style.transform='translate3d('+(2.9*rem*(1-a))+'px,0,0)';
  const f=(u-H0)/HS,i=cl(Math.floor(f),0,n-1);$$('.ac',how).forEach((li,j)=>{li.classList.toggle('on',j===i);li.style.setProperty('--p',j===i?cl(f-i):0);});$$('.how-p',how).forEach(p=>p.classList.toggle('on',+p.dataset.i===i));}}
 else if(how&&force){hw.style.transform='';hx.style.opacity='';hx.style.transform='';}
 if(caps&&w&&row){const u=(y-caps.offsetTop)/k,x0=51.125*rem,trav=cl((u+607)*SP*k,0,CT),x=x0-trav;row.style.transform='translate3d('+x+'px,0,0)';
  if(ring){const n=+ring.dataset.n||1,ua=(CT/SP)/k-607,f=(u-ua)/RS,i=cl(Math.floor(f),0,n-1);if(i!==cur||force){cur=i;$$('.ac',ring).forEach((li,j)=>li.classList.toggle('on',j===i));}
   $$('.ac',ring).forEach((li,j)=>li.style.setProperty('--p',j===i?cl(f-i):0));
   const ang=-(u-ua)/RS*45,R0=43*rem;$$('.wt',ring).forEach(t=>{const kk=+t.style.getPropertyValue('--k'),a=(kk*45+ang-15)*Math.PI/180,c=Math.cos(a),s=Math.sin(a),sc2=.66+.34*(c+1)/2;
    t.style.transform='translate3d('+(R0*c)+'px,'+(R0*s)+'px,0) translate(-50%,-50%) scale('+sc2+')';t.style.visibility=c<-.25?'hidden':'';});
   const tk=$('.ticks',ring);if(tk)tk.style.transform='rotate('+(-ang*1.2)+'deg)';
   ring.style.opacity=1-seg(u,ua+n*RS+60,ua+n*RS+RT);}}
 else if(caps&&force&&row){row.style.transform='';if(ring){ring.style.opacity='';$$('.wt',ring).forEach(t=>{t.style.transform='';t.style.visibility='';});}}}
document.addEventListener('focusin',ev=>{const t=ev.target,k=innerHeight/900,w=wide.matches,rem=parseFloat(getComputedStyle(R).fontSize);if(!t.closest)return;let y=null;
 if(w&&how&&how.contains(t)){const li=t.closest('.ac');y=how.offsetTop+(li?H0+HS*$$('.ac',how).indexOf(li)+HS/3:H0+40)*k;}
 else if(w&&caps&&caps.contains(t)){const li=t.closest('.ac'),pn=t.closest('.pn'),ua=(CT/SP)/k-607;if(pn)y=caps.offsetTop+(Math.max(0,pn.offsetLeft+51.125*rem-innerWidth*.12)/(SP*k)-607)*k;else if(ring&&ring.contains(t))y=caps.offsetTop+(ua+(li?$$('.ac',ring).indexOf(li)*RS+RS/3:40))*k;}
 else if(hero&&hero.contains(t)&&scrollY>hero.offsetTop+400*k)y=hero.offsetTop;
 if(y!==null){scrollTo({top:Math.max(0,y),behavior:'instant'});tick();}});
let raf=0;addEventListener('scroll',()=>{if(!raf)raf=requestAnimationFrame(()=>{raf=0;tick();});},{passive:true});
let lt=0;$$('.caps img,.thumbs img').forEach(im=>{if(!im.complete)im.addEventListener('load',()=>{clearTimeout(lt);lt=setTimeout(lay,60);},{once:true});});
addEventListener('resize',lay);addEventListener('load',lay);if(document.fonts&&document.fonts.ready)document.fonts.ready.then(lay);lay();
})();
'''


def render(d: dict) -> str:
    b = d.get('brand') or {}
    h = d.get('hero') or {}
    title = ' — '.join(x for x in (b.get('name'), h.get('title')) if x)
    desc = h.get('text') or ''
    body = ''.join((s_hero(d), s_how(d), s_figures(d), s_caps(d), s_plans(d), s_faq(d), s_close(d)))
    return f'''<!doctype html>
<html lang="{e(d.get("lang") or "en")}" style="{_theme(d.get("palette") or {})}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<style>{CSS}</style>
</head>
<body>
{s_top(d)}
<main>
{body}
</main>
{s_foot(d)}
<script>{JS}</script>
</body>
</html>'''
