"""supaste/render.py — one pure function: render(d) -> a complete page built to the measures of the reference
(a centred bar hanging from the top edge, an opening on a sky with a landscape at its foot, a stack of soft r30 cards
each holding one centred heading and one wide picture stage, a three-column card grid, one price card with a segment
switch, a two-column question list, link cards, an inverse foot with the name set very large).
No client, no model call, no file read, no network at render."""
import html
import re

M = '../../'
SANS = 'Inter'                 # the reference's sans is Inter Display — Inter is SIL OFL; its optical-size axis gives the display cut
SERIF = 'Instrument Serif'     # the reference's own second face, SIL OFL, italic


def e(s):
    return html.escape(str(s or ''), quote=True)


# ---------- colour: the client's palette goes in; the reference's relations are kept ----------
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


def quiet(ink, *grounds):
    """the reference sets secondary text at 60% of the ink; kept, but never below 4.6:1 on the grounds it stands on"""
    for t in (.4, .35, .3, .25, .2, .15, .1, .05, 0):
        m = mix(ink, grounds[0], t)
        if min(con(m, g) for g in grounds) >= 4.6:
            return m
    return ink


def colours(p):
    G, I, A = p.get('ground', '#ffffff'), p.get('ink', '#000000'), p.get('accent', '#0080ff')
    card = mix(G, I, .031)          # #f7f7f7 on white
    chip = mix(G, I, .11)           # #e3e3e3 on white
    return dict(G=G, I=I, A=A, card=card, chip=chip, mu=quiet(I, card, G), imu=quiet(G, I), word=mix(I, G, .07),
                light=G if lum(G) > lum(I) else I, dark=I if lum(G) > lum(I) else G)


# ---------- small parts ----------
def asp(m):
    return (m.get('w') or 1) / (m.get('h') or 1)


def pic(m, cls='', lazy=True, alt=None):
    if not m:
        return ''
    a = m.get('alt') if alt is None else alt
    return (f'<img{f" class={chr(34)}{cls}{chr(34)}" if cls else ""} src="{M}{e(m["src"])}" width="{int(m.get("w") or 0) or ""}" '
            f'height="{int(m.get("h") or 0) or ""}" alt="{e(a)}"{" loading=lazy decoding=async" if lazy else ""}>')


def back(m, slot, pos=''):
    """a made picture used as a backdrop: decorative, fills its parent"""
    if not m:
        return f'<span class="bk" data-slot="{slot}"></span>'
    return (f'<img class="bk" data-slot="{slot}" src="{M}{e(m["src"])}" width="{int(m.get("w") or 0) or ""}" height="{int(m.get("h") or 0) or ""}" '
            f'alt="" loading="lazy" decoding="async"{f" style={chr(34)}object-position:{pos}{chr(34)}" if pos else ""}>')


def btn(c, cls='', small=False):
    if not c or not c.get('t'):
        return ''
    return f'<a class="btn{" sm" if small else ""}{" " + cls if cls else ""}" href="{e(c.get("h") or "#")}">{e(c["t"])}</a>'


def el(tag, text, cls=''):
    """an element, or nothing when its text is missing"""
    return f'<{tag}{f" class={chr(34)}{cls}{chr(34)}" if cls else ""}>{e(text)}</{tag}>' if text else ''


def split2(t):
    """the reference's headline is two lines, the second in the serif italic: split at a sentence end, else at the middle"""
    t = (t or '').strip()
    m = re.search(r'[.!?]\s+(?=\S)', t)
    if m:
        return t[:m.start() + 1], t[m.end():]
    w = t.split()
    if len(w) < 2:
        return t, ''
    k = min(range(1, len(w)), key=lambda i: abs(len(' '.join(w[:i])) - len(' '.join(w[i:]))))
    return ' '.join(w[:k]), ' '.join(w[k:])


def step(n, sizes):
    for lim, v in sizes:
        if n <= lim:
            return v
    return sizes[-1][1]


def logo(b, c):
    """the reference shows a 30px rounded app tile and the name; a wordmark logo stands alone on a ground-coloured tile"""
    if not b.get('logo'):
        return f'<span class="nm">{e(b.get("name"))}</span>'
    if b.get('logo_wordmark'):
        return f'<span class="lw"><img src="{M}{e(b["logo"])}" alt="{e(b.get("name"))}" height="18"></span>'
    return f'<img class="li" src="{M}{e(b["logo"])}" alt="" width="30" height="30"><span class="nm">{e(b.get("name"))}</span>'


CHECK = '<svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true"><circle cx="12" cy="12" r="9.25" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M8.2 12.3l2.6 2.6 5-5.4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
PLUS = '<svg class="pl" viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><path d="M8 1.5v13M1.5 8h13" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>'


def lead_land(made, tone):
    """the page's one picture — the landscape that stands at the foot of the opening and comes back, in another crop,
    behind every stage and behind the price card (the reference shows one and the same hills in all of these).
    A page takes the first of its own tone; a dark page never takes a light one."""
    land = made.get('land') or []
    xs = [land[i] for i in (0, 5, 1) if i < len(land) and land[i].get('src')]
    own = [m for m in xs if m.get('tone') == tone]
    return own[0] if own else (xs[0] if xs and tone == 'light' else None)


class Pool:
    """the lead picture's neighbours in the series, for the wide link cards: each used once, own tone first, wrapping
    round only when there are more cards than pictures; a dark page never takes a light one"""

    def __init__(self, made, tone, lead):
        land = made.get('land') or []
        xs = [land[i] for i in (1, 2, 5, 3, 4, 0) if i < len(land) and land[i].get('src') and land[i] is not lead]
        self.xs = [m for m in xs if m.get('tone') == tone] + ([m for m in xs if m.get('tone') != tone] if tone == 'light' else [])
        self.lead = lead
        self.n = 0
        self.k = 0

    def again(self):
        """the lead picture and the crop it takes this time"""
        self.k += 1
        return self.lead, ('50% 62%', '30% 40%', '70% 78%', '50% 30%')[(self.k - 1) % 4]

    def take(self):
        if not self.xs:
            return None
        m = self.xs[self.n % len(self.xs)]
        self.n += 1
        return m


# ---------- sections ----------
def s_nav(d, c):
    b = d.get('brand') or {}
    links = [n for n in d.get('nav') or [] if n.get('t')]
    si = d.get('signin') or {}
    if si.get('t'):
        links = links + [si]
    nav = ''.join(f'<a href="{e(n.get("h"))}">{e(n["t"])}</a>' for n in links)
    cta = btn(d.get('cta'), 'inv', True)
    return f'''<header class="top" id="top"><div class="bar ears">
<a class="logo" href="{e(b.get("home") or "#")}">{logo(b, c)}</a>
<nav class="nav" aria-label="Primary">{nav}</nav>{cta}
<button class="burger" type="button" aria-expanded="false" aria-controls="menu" aria-label="Menu"><i></i><i></i><i></i></button>
<div class="menu" id="menu" hidden><nav aria-label="Menu">{nav}</nav>{cta}</div>
</div></header>'''


def hero_media(d):
    md = d.get('media') or {}
    scr = (md.get('screens') or [None])[0]
    used = {i.get('img') for i in (d.get('steps') or {}).get('items') or []}
    side = next((m for m in (md.get('phones') or []) + (md.get('photos') or []) if m.get('src') not in used and asp(m) < 1), None)
    return scr, side


def s_hero(d, c, land):
    h = d.get('hero') or {}
    if not h.get('title'):
        return ''
    T, V = c['I'], c['G']                              # the words stand on the page's own ground, above the picture
    a, b = split2(h['title'])
    need = max(len(a) * .54, len(b) * .40, 1)          # widest line in em: bold sans ≈ .54em a letter, the serif italic ≈ .40
    fs, fm = min(80, int(1040 / need)), min(50, int(340 / need))
    kick = f'<p class="kick ch">{e(h["kicker"])}</p>' if h.get('kicker') else ''
    text = ' '.join(x for x in (h.get('text'), h.get('text2')) if x)
    lead = f'<p class="lead up">{e(text)}</p>' if text else ''
    acts = btn(h.get('primary'), 'hp') + btn(h.get('secondary'), 'hs')
    acts = f'<div class="acts up">{acts}</div>' if acts else ''
    note = f'<p class="hnote up">{e(h["note"])}</p>' if h.get('note') else ''
    scr, side = hero_media(d)
    mock = ''
    if scr:
        s2 = f'<figure class="side {e(side.get("shape") or "phone")}">{pic(side, lazy=False)}</figure>' if side else ''
        mock = f'<div class="mock up{" duo" if side else ""}"><figure class="scr">{pic(scr, lazy=False)}</figure>{s2}</div>'
    bg = ''
    if land:
        bg += (f'<div class="hland"><img data-slot="land-lead" src="{M}{e(land["src"])}" width="{land.get("w") or ""}" '
               f'height="{land.get("h") or ""}" alt=""></div>')
    return f'''<section class="hero" style="--t:{T};--v:{V};--fs:{fs}px;--fm:{fm}px"><div class="hbg" aria-hidden="true">{bg}</div>
<div class="wrap"><div class="hcopy">{kick}
<h1 class="h1"><span class="l1 ch">{e(a)}</span>{f' <span class="l2 ch">{e(b)}</span>' if b else ''}</h1>
{lead}{acts}{note}</div>{mock}</div></section>'''


def s_intro(d, c):
    s = d.get('statement') or {}
    trust = [t for t in d.get('trust') or [] if t]
    logos = [l for l in d.get('logos') or [] if isinstance(l, dict) and l.get('src')]
    if not (s.get('title') or s.get('text') or trust or logos):
        return ''
    marks = ''
    if logos:
        marks = '<div class="marks">' + ''.join(f'<span class="mark">{pic(l)}</span>' for l in logos) + '</div>'
    head = ''
    if s.get('title') or s.get('text') or trust:
        chips = f'<ul class="chips">{"".join(f"<li>{e(t)}</li>" for t in trust)}</ul>' if trust else ''
        head = (f'<div class="head w740">{el("h2", s.get("title"), "h2")}'
                f'{el("p", s.get("text"), "sub")}{chips}</div>')
    return marks + head


def stage(m, bgp, slot, video=False):
    bg, pos = bgp
    if video:
        inner = (f'<video src="{M}{e(m["src"])}" poster="{M}{e(m.get("poster"))}" width="{m.get("w")}" height="{m.get("h")}" muted loop playsinline '
                 f'preload="metadata" aria-label="{e(m.get("alt"))}" data-auto></video>')
    else:
        inner = pic(m)
    return f'<div class="stage" style="--r:{asp(m):.4f}">{back(bg, slot, pos)}{inner}</div>'


def card_head(title, text='', extra=''):
    return (f'<div class="chd"><h3 class="h3" style="--fs:{step(len(title or ""), [(46, 50), (70, 42), (999, 34)])}px">{e(title)}</h3>'
            f'{f"<p>{e(text)}</p>" if text else ""}{extra}</div>')


def s_tiles(d, c):
    st = d.get('steps') or {}
    items = [i for i in st.get('items') or [] if i.get('title')]
    if not items:
        return ''
    md = d.get('media') or {}
    known = {m['src']: m for m in (md.get('screens') or []) + (md.get('phones') or []) + (md.get('photos') or [])}
    tone = 'light' if lum(c['G']) > lum(c['I']) else 'dark'
    bg = next((f for f in (md.get('made') or {}).get('field') or [] if f.get('src') and f.get('tone') == tone), None)
    tiles = ''
    for n, i in enumerate(items):
        T, V = (c['I'], c['G']) if bg else (c['I'], c['card'])
        m = known.get(i.get('img'), {'src': i['img'], 'alt': i.get('title')}) if i.get('img') else None
        cta = i.get('cta') or {}
        link = f'<a class="tl" href="{e(cta.get("h"))}">{e(cta["t"])}</a>' if cta.get('t') else ''
        shot = f'<div class="tp {e(i.get("shape") or "")}" style="--r:{asp(m):.4f}">{pic(m)}</div>' if m else ''
        tiles += (f'<article class="tile{" flip" if n % 2 else ""}{"" if bg else " plain"}" style="--t:{T};--v:{V}">{back(bg, "field", ("50% 50%", "0% 100%", "100% 0%", "50% 100%")[n % 4])}'
                  f'<i class="tv"></i><div class="tt"><h4>{e(i["title"])}</h4>{el("p", i.get("text"))}{link}</div>{shot}</article>')
    head = card_head(st.get('title'), st.get('text'), btn(d.get('cta'))) if st.get('title') else ''
    return f'<section class="card rv">{head}<div class="tiles" style="--n:{min(len(items), 4)}">{tiles}</div></section>'


def s_quote(q):
    if isinstance(q, str):
        q = {'text': q}
    text = q.get('text') or q.get('q') or q.get('quote')
    if not text:
        return ''
    who = q.get('name') or q.get('by')
    role = q.get('role') or q.get('title')
    by = f'<footer><strong>{e(who)}</strong>{f"<span>{e(role)}</span>" if role else ""}</footer>' if who else ''
    return f'<blockquote class="quote rv"><p>{e(text)}</p>{by}</blockquote>'


def s_stack(d, c, pool):
    md = d.get('media') or {}
    cards = []
    if md.get('video'):
        v = md['video']
        cards.append(f'<section class="card rv">{card_head(v.get("alt")) if v.get("alt") else ""}{stage(v, pool.again(), "land-lead", True)}</section>')
    t = s_tiles(d, c)
    if t:
        cards.append(t)
    for m in (md.get('screens') or [])[1:]:
        cards.append(f'<section class="card rv">{card_head(m.get("alt")) if m.get("alt") else ""}{stage(m, pool.again(), "land-lead")}</section>')
    quotes = [s_quote(q) for q in d.get('quotes') or []]
    out = []
    for n, x in enumerate(cards):
        out.append(x)
        if n >= 2 and quotes:                       # the reference sets a quote after the third and the fourth card
            out.append(quotes.pop(0))
    out += quotes
    fg = [f for f in d.get('figures') or [] if f.get('v')]
    if fg:
        cells = ''.join(f'<div class="card fig rv"><h4 class="fv">{e(f["v"])}</h4>{el("p", f.get("l"))}</div>' for f in fg)
        out.append(f'<div class="duo2">{cells}</div>')
    return f'<div class="stack">{"".join(out)}</div>' if out else ''


def s_features(d, c):
    f = d.get('features') or {}
    items = [i for i in f.get('items') or [] if i.get('t') or i.get('d')]
    if not items and not f.get('title'):
        return ''
    head = ''
    if f.get('title'):
        head = f'<div class="head">{el("h2", f.get("title"), "h2")}{el("p", f.get("text"), "sub")}</div>'
    cells = ''.join(f'<div class="card use rv">{el("h4", i.get("t"), "h4")}{el("p", i.get("d"))}</div>' for i in items)
    grid = f'<div class="g3">{cells}</div>' if cells else ''
    return f'<section class="sec" id="features"><div class="wrap">{head}{grid}</div></section>'


def s_plans(d, c, land):
    p = d.get('plans') or {}
    items = [i for i in p.get('items') or [] if i.get('name')]
    if not items:
        return ''
    b = d.get('brand') or {}
    head = ''
    if p.get('title'):
        head = f'<div class="head">{el("h2", p.get("title"), "h2")}{el("p", p.get("text"), "sub")}</div>'
    on = next((n for n, i in enumerate(items) if i.get('marked')), 0)
    segs, panes = '', ''
    for n, i in enumerate(items):
        segs += (f'<button class="sg" type="button" role="tab" id="pt{n}" aria-controls="pp{n}" aria-selected="{"true" if n == on else "false"}" '
                 f'tabindex="{0 if n == on else -1}">{e(i["name"])}</button>')
        rows = ''.join(f'<li>{CHECK}<span>{e(r)}</span></li>' for r in i.get('rows') or [])
        price = e(i.get('price'))
        panes += (f'<div class="pp{" on" if n == on else ""}" role="tabpanel" id="pp{n}" aria-labelledby="pt{n}"><h3 class="pn">{e(i["name"])}</h3>'
                  f'<p class="price"><strong style="--fs:{step(len(i.get("price") or ""), [(4, 80), (6, 64), (8, 52), (999, 40)])}px">{price}</strong>{el("span", i.get("per"))}</p>'
                  f'{el("p", i.get("line"), "pline")}'
                  f'{f"<ul class=rows>{rows}</ul>" if rows else ""}{btn(i.get("cta"))}</div>')
    # the switch is one row while every name fits its share of the narrowest card (phone: 286 px inside, 14px/600
    # letters ≈ 8.5 px, 16 px padding); otherwise its segments stand one under another, so no name is cut or spills
    col = len(items) * max(len(i['name']) * 8.5 + 16 for i in items) > 286
    seg = f'<div class="seg{" col" if col else ""}" role="tablist" style="--n:{len(items)};--k:{on}"><i class="thumb"></i>{segs}</div>' if len(items) > 1 else ''
    note = f'<p class="pnote">{e(p["note"])}</p>' if p.get('note') else ''
    bg = (f'<div class="pbg" aria-hidden="true"><img data-slot="land-lead" src="{M}{e(land["src"])}" width="{land.get("w") or ""}" '
          f'height="{land.get("h") or ""}" alt="" loading="lazy" decoding="async"></div>') if land else ''
    return f'''<section class="sec plans" id="plans">{bg}<div class="wrap">{head}
<div class="pc{' one' if len(items) < 2 else ''} rv"><div class="ptab ears"><span class="logo">{logo(b, c)}</span></div>{seg}<div class="pps">{panes}</div></div>{note}</div></section>'''


def s_faq(d, c):
    f = d.get('faq') or {}
    items = [i for i in f.get('items') or [] if i.get('q') and i.get('a')]
    if not items:
        return ''
    head = f'<div class="head"><h2 class="h2">{e(f["title"])}</h2></div>' if f.get('title') else ''
    half = (len(items) + 1) // 2
    col = lambda xs: '<div class="qc">' + ''.join(f'<details class="q rv"><summary>{PLUS}<span>{e(i["q"])}</span></summary><div class="qa"><p>{e(i["a"])}</p></div></details>' for i in xs) + '</div>'
    return f'<section class="sec faq" id="faq"><div class="wrap">{head}<div class="qs">{col(items[:half])}{col(items[half:]) if items[half:] else ""}</div></div></section>'


def s_links(d, c, pool):
    ls = [l for l in d.get('links') or [] if l.get('t')]
    if not ls:
        return ''
    cards = ''
    for l in ls:
        bg = pool.take()
        T, V = (c['I'], c['card'])
        big = l.get('d') or l['t']
        cards += (f'<article class="card lk rv{"" if bg else " plain"}" style="--t:{T};--v:{V}">{back(bg, "land")}<i class="lv"></i>'
                  f'<div class="lt"><h3 class="h3" style="--fs:{step(len(big), [(34, 50), (60, 40), (999, 32)])}px">{e(big)}</h3>{btn({"t": l["t"], "h": l.get("h")})}</div></article>')
    return f'<section class="sec links"><div class="wrap"><div class="lks">{cards}</div></div></section>'


def s_foot(d, c):
    b = d.get('brand') or {}
    ft = d.get('foot') or {}
    cl = d.get('close') or {}
    a, bb = split2(cl.get('title'))
    tag = f'<p class="ftag"><span>{e(a)}</span>{f" <em>{e(bb)}</em>" if bb else ""}</p>' if cl.get('title') else ''
    col = lambda xs: '<nav class="fcol">' + ''.join(f'<a href="{e(x.get("h"))}">{e(x.get("t"))}</a>' for x in xs if x.get('t')) + '</nav>' if [x for x in xs if x.get('t')] else ''
    seen, groups = set(), []                         # three columns as in the reference; a link is listed once
    for xs in (d.get('nav') or [], d.get('links') or [], [d.get('signin') or {}] + list(ft.get('links') or [])):
        g = [x for x in xs if x.get('t') and x.get('h') not in seen]
        seen.update(x.get('h') for x in g)
        groups.append(g)
    cols = ''.join(col(g) for g in groups)
    name = b.get('name') or ''
    ws = min(22.2, 148 / max(len(name), 1))
    return f'''<footer class="ft"><div class="lip ears" aria-hidden="true"></div><div class="wrap fin">
<div class="fl"><a class="logo" href="{e(b.get("home") or "#")}">{logo(b, c)}</a>{tag}
{f'<p class="ftx">{e(cl["text"])}</p>' if cl.get('text') else ''}{btn(cl.get('cta'), 'inv', True)}
{f'<p class="fsm">{e(ft["legal"])}</p>' if ft.get('legal') else ''}{f'<p class="fsm">{e(ft["text"])}</p>' if ft.get('text') else ''}</div>
{cols}</div>
{f'<div class="word" aria-hidden="true" style="--ws:{ws:.2f}vw">{e(name)}</div>' if name else ''}</footer>'''


# ---------- the page ----------
CSS = r'''
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}body{margin:0;background:var(--g);color:var(--i);font:400 16px/1.4 "SANS",ui-sans-serif,system-ui,sans-serif;font-optical-sizing:auto;letter-spacing:-.01em;-webkit-font-smoothing:antialiased;overflow-x:clip}
img,video{display:block;max-width:100%;height:auto}h1,h2,h3,h4,p,figure,ul,blockquote{margin:0}ul{padding:0;list-style:none}a{color:inherit;text-decoration:none}button{font:inherit;color:inherit;letter-spacing:inherit;background:none;border:0;padding:0;cursor:pointer}
:focus-visible{outline:2px solid currentColor;outline-offset:3px;border-radius:6px}
.wrap{width:min(1120px,100% - 40px);margin-inline:auto}
.bk{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;max-width:none}
/* type: 80 / 60 / 50 / 30, weight 700, line-height 1, tracking -.05em — as measured */
.h2{font-weight:700;font-size:60px;line-height:1;letter-spacing:-.05em;text-wrap:balance}
.h3{font-weight:700;font-size:var(--fs,50px);line-height:1;letter-spacing:-.05em;text-wrap:balance}
.h4{font-weight:700;font-size:30px;line-height:1;letter-spacing:-.05em}
.sub{font-size:20px;line-height:1.4;color:var(--mu);text-wrap:pretty}
.btn{display:inline-flex;align-items:center;justify-content:center;min-height:52px;padding:15px 30px;border-radius:20px;background:var(--i);color:var(--g);font-weight:600;font-size:16px;line-height:1.4;letter-spacing:0;text-align:center;transition:background-color .3s,color .3s}
.btn:hover{background:color-mix(in srgb,var(--i) 80%,transparent)}
.btn.sm{min-height:33px;padding:8px 16px;border-radius:8px;font-size:12px}
.btn.inv{background:var(--g);color:var(--i)}.btn.inv:hover{background:color-mix(in srgb,var(--g) 80%,transparent)}
/* the bar: hangs from the top edge, centred, with two 20px ears turning out into the edge */
.ears{position:relative}.ears::before,.ears::after{content:"";position:absolute;top:0;width:20px;height:20px;pointer-events:none}
.ears::before{right:calc(100% - .5px);background:radial-gradient(circle at 0 100%,transparent 19.5px,var(--ec) 20px)}.ears::after{left:calc(100% - .5px);background:radial-gradient(circle at 100% 100%,transparent 19.5px,var(--ec) 20px)}
.top{position:fixed;inset:0 0 auto 0;z-index:50;display:flex;justify-content:center;pointer-events:none}
.bar{--ec:var(--i);pointer-events:auto;display:flex;align-items:center;gap:40px;min-height:53px;padding:10px;background:var(--i);color:var(--g);border-radius:0 0 16px 16px}
.logo{display:inline-flex;align-items:center;gap:10px;font-weight:600;font-size:16px;letter-spacing:-.02em;line-height:1.2;white-space:nowrap}
.li{height:30px;width:auto;max-width:none;border-radius:8px}.lw{display:inline-flex;align-items:center;height:30px;padding:0 10px;border-radius:8px;background:var(--g)}.lw img{height:18px;width:auto;max-width:none}.lw,.li{flex:none}
.nav{display:flex;gap:20px}.nav a,.menu nav a{font-weight:500;font-size:14px;line-height:1.2;letter-spacing:-.02em;color:var(--imu);white-space:nowrap;transition:color .3s}.nav a:hover,.menu nav a:hover{color:color-mix(in srgb,var(--g) 80%,var(--i))}
.burger{display:none;width:40px;height:40px;flex-direction:column;justify-content:center;align-items:center;gap:6px}.burger i{display:block;width:20px;height:1.5px;background:currentColor;opacity:.6}
.menu{position:absolute;left:0;right:0;top:100%;margin-top:-16px;padding:26px 20px 20px;background:var(--i);border-radius:0 0 16px 16px}.menu nav{display:grid;gap:18px;margin-bottom:20px}.menu nav a{font-size:16px}.menu .btn{width:100%;min-height:44px;font-size:14px}
/* opening: sky above, a landscape along the foot that fades into the page; text 600 wide, centred */
.hero{position:relative;overflow:clip;color:var(--t)}.hbg{position:absolute;inset:0}
.hland{position:absolute;inset:auto 0 0 0;height:820px;overflow:hidden;-webkit-mask-image:linear-gradient(transparent,#000 48%,#000 72%,transparent);mask-image:linear-gradient(transparent,#000 48%,#000 72%,transparent)}
.hland img{width:100%;height:100%;max-width:none;object-fit:cover;transform-origin:50% 50%;will-change:transform}
.hero .wrap{position:relative;display:flex;flex-direction:column;align-items:center;gap:60px;padding:140px 0 200px}
.hcopy{display:flex;flex-direction:column;align-items:center;gap:20px;text-align:center;width:100%}
.kick{font-weight:600;font-size:20px;line-height:1.25;letter-spacing:-.02em}
.h1{font-weight:700;font-size:var(--fs);line-height:1;letter-spacing:-.05em;max-width:1040px}.h1 span{display:block}
.h1 .l2,.ftag em{font-family:"SERIF",ui-serif,Georgia,serif;font-style:italic;font-weight:400}
.lead{max-width:600px;font-size:20px;line-height:1.4;text-wrap:pretty}
.acts{display:flex;flex-wrap:wrap;justify-content:center;gap:20px}
.hp{background:var(--t);color:var(--v)}.hp:hover{background:color-mix(in srgb,var(--t) 80%,transparent)}.hs{background:color-mix(in srgb,var(--v) 90%,var(--t));color:var(--t)}.hs:hover{background:color-mix(in srgb,var(--v) 80%,transparent)}
.hnote{font-size:12px;line-height:1.6;letter-spacing:0}
.mock{width:100%;display:flex;justify-content:center;align-items:flex-start;gap:20px}
.scr{flex:1 1 0;min-width:0;max-width:1120px}.scr img{width:100%;border-radius:20px;box-shadow:0 30px 60px -30px rgba(0,0,0,.45)}
.side{flex:0 0 23.2%;margin-top:57px;will-change:transform}.side img{width:100%;border-radius:30px;box-shadow:0 30px 60px -30px rgba(0,0,0,.45)}
.side.book img{border-radius:6px}
/* sections */
.sec{position:relative;padding:100px 0}.sec .wrap,.body .wrap{display:flex;flex-direction:column;gap:60px}.body{padding:100px 0}
.head{display:flex;flex-direction:column;align-items:center;gap:20px;text-align:center;width:min(600px,100%);margin-inline:auto}.head.w740{width:min(740px,100%)}
.marks{display:flex;flex-wrap:wrap;justify-content:center;gap:10px}.mark{display:grid;place-items:center;width:90px;height:90px;border-radius:100px;background:var(--card);overflow:hidden}.mark img{max-width:56px;max-height:56px;width:auto}
.chips{display:flex;flex-wrap:wrap;justify-content:center;gap:10px}.chips li{padding:5px 10px;border-radius:30px;background:var(--card);font-weight:500;font-size:12px;line-height:1.6;letter-spacing:0;color:var(--mu)}
/* the stack of cards: ground + 3% ink, r30, 40 inside, 20 between */
.stack{display:flex;flex-direction:column;gap:20px}
.card{position:relative;background:var(--card);border-radius:30px;padding:40px;display:flex;flex-direction:column;gap:40px;overflow:clip}
.chd{display:flex;flex-direction:column;align-items:center;gap:20px;text-align:center}.chd p{color:var(--mu);text-wrap:pretty;max-width:1040px}
.stage{position:relative;display:grid;place-items:center;padding:52px clamp(20px,10%,104px);border-radius:20px;overflow:hidden;background:var(--chip)}
.stage>img:not(.bk),.stage>video{position:relative;width:min(100%,calc(var(--mh,560px)*var(--r)));height:auto;border-radius:12px;box-shadow:0 30px 60px -24px rgba(0,0,0,.5)}
.tiles{display:grid;grid-template-columns:repeat(var(--n),minmax(0,1fr));gap:10px}
.tile{position:relative;display:flex;flex-direction:column;min-height:547px;border-radius:30px;overflow:hidden;color:var(--t);background:var(--chip)}.tile.flip{flex-direction:column-reverse}
.tv{position:absolute;inset:0;background:linear-gradient(var(--v),color-mix(in srgb,var(--v) 86%,transparent) 34%,transparent 62%)}.tile.flip .tv{background:linear-gradient(0deg,var(--v),color-mix(in srgb,var(--v) 86%,transparent) 34%,transparent 62%)}.tile.plain .tv{display:none}
.tt{position:relative;display:flex;flex-direction:column;align-items:center;gap:10px;padding:36px 24px;text-align:center}
.tt h4{font-weight:700;font-size:28px;line-height:1.1;letter-spacing:-.04em;text-wrap:balance}.tt p{font-size:15px;line-height:1.4;text-wrap:pretty}.tl{font-weight:600;font-size:14px;text-decoration:underline;text-underline-offset:3px}
.tp{position:relative;flex:1;display:flex;align-items:flex-end;justify-content:center;padding:0 24px 28px;min-height:0}.tile.flip .tp{align-items:flex-start;padding:28px 24px 0}
.tp img{width:min(100%,calc(var(--mh,330px)*var(--r)));height:auto;border-radius:14px;box-shadow:0 24px 48px -20px rgba(0,0,0,.5)}.tp.phone img{border-radius:22px}.tp.book img{border-radius:4px}
.quote{width:min(500px,100%);margin:0 auto;padding:80px 0;display:flex;flex-direction:column;gap:14px}.quote p{color:var(--mu)}.quote footer{display:flex;flex-direction:column}.quote strong{font-weight:600}.quote span{font-size:12px;color:var(--mu)}
.duo2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px}
.fig{gap:20px;align-items:center;text-align:center}.fv{font-weight:700;font-size:50px;line-height:1;letter-spacing:-.05em}.fig p{color:var(--mu);max-width:470px;text-wrap:pretty}
.g3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}.use{gap:20px}.use p{color:var(--mu)}
/* price: one card with the brand on a tab, a segment switch, the price, rows; the opening's sky upside down behind its foot */
.pbg{position:absolute;inset:310px 0 200px 0;overflow:hidden;-webkit-mask-image:linear-gradient(transparent,#000 45%,#000 72%,transparent);mask-image:linear-gradient(transparent,#000 45%,#000 72%,transparent)}.pbg img{width:100%;height:100%;max-width:none;object-fit:cover;object-position:50% 70%}
.plans .wrap{position:relative;gap:40px}
.pc{position:relative;width:min(400px,100%);margin-inline:auto;background:var(--card);border-radius:40px;padding:80px 40px 40px}
.ptab{--ec:var(--i);position:absolute!important;top:0;left:50%;translate:-50% 0;display:flex;align-items:center;min-height:50px;padding:10px 20px 10px 10px;background:var(--i);color:var(--g);border-radius:0 0 16px 16px;max-width:calc(100% - 100px)}.ptab .logo{pointer-events:none}
.seg{position:relative;display:grid;grid-template-columns:repeat(var(--n),minmax(0,1fr));padding:2px;border-radius:14px;background:var(--g);margin-bottom:20px}
html:not(.js) .seg{display:none}.sg{position:relative;min-height:36px;padding:6px 8px;border-radius:13px;font-weight:600;font-size:14px;line-height:1.2;letter-spacing:-.02em;transition:color .3s}.sg[aria-selected=true]{color:var(--g)}
.thumb{position:absolute;top:2px;bottom:2px;left:2px;width:calc((100% - 4px)/var(--n));border-radius:13px;background:var(--i);transform:translateX(calc(var(--k)*100%));transition:transform .45s cubic-bezier(.2,.8,.2,1)}
.seg.col{grid-template-columns:minmax(0,1fr)}.seg.col .thumb{right:2px;bottom:auto;width:auto;height:calc((100% - 4px)/var(--n));transform:translateY(calc(var(--k)*100%))}
.pps{display:grid}.pp{display:flex;flex-direction:column;gap:20px}.pp+.pp{margin-top:40px}
.js .pp{grid-area:1/1;margin:0;opacity:0;visibility:hidden;transform:translateY(12px);transition:opacity .3s,transform .45s cubic-bezier(.2,.8,.2,1),visibility 0s .3s}.js .pp.on{opacity:1;visibility:visible;transform:none;transition:opacity .3s,transform .45s cubic-bezier(.2,.8,.2,1)}
.pn{font-weight:600;font-size:16px;line-height:1.2;letter-spacing:-.02em}.js .pc:not(.one) .pn{display:none}
.price{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;min-height:80px;text-align:center}.price strong{font-weight:700;font-size:var(--fs);line-height:1;letter-spacing:-.05em}.price span{font-size:14px;color:var(--mu)}
.pline{padding:16px;border-radius:10px;background:var(--g);font-weight:500;font-size:14px;line-height:1.3;letter-spacing:0}
.rows{display:grid;gap:10px}.rows li{display:flex;gap:10px;font-size:14px;line-height:1.6;letter-spacing:0}.rows svg{flex:none;color:color-mix(in srgb,var(--i) 28%,transparent)}
.pp .btn{width:100%}.pnote{width:min(400px,100%);margin-inline:auto;text-align:center;font-size:14px;line-height:1.4;color:var(--mu)}
/* questions: two columns of 490, rows r20 */
.qs{display:grid;grid-template-columns:repeat(2,minmax(0,490px));justify-content:center;gap:20px;align-items:start}.qc{display:flex;flex-direction:column;gap:20px}
.q{border-radius:20px;background:var(--card);padding:0 20px}
.q summary{position:relative;display:block;padding:20px 0 20px 40px;font-size:14px;line-height:1.6;letter-spacing:0;cursor:pointer;list-style:none}.q summary::-webkit-details-marker{display:none}
.pl{position:absolute;left:0;top:25px;transition:transform .5s cubic-bezier(.2,.8,.2,1)}.q[open] .pl{transform:rotate(45deg)}
.qa{overflow:hidden}.qa p{padding:0 0 20px 40px;color:var(--mu)}
/* link cards: text in the left half; the picture is the card's own backdrop */
.lks{display:flex;flex-direction:column;gap:60px}
.lk{min-height:444px;justify-content:center;color:var(--t)}.lv{position:absolute;inset:0;background:linear-gradient(90deg,var(--v) 0,var(--v) 40%,color-mix(in srgb,var(--v) 92%,transparent) 46%,color-mix(in srgb,var(--v) 72%,transparent) 53%,color-mix(in srgb,var(--v) 40%,transparent) 63%,color-mix(in srgb,var(--v) 14%,transparent) 75%,transparent 90%)}.lk.plain .lv{display:none}
.lt{position:relative;display:flex;flex-direction:column;align-items:flex-start;gap:28px;width:min(510px,100%)}.lt .h3{text-align:left}.lt .btn{min-width:240px}
/* foot: inverse; the page ends in a rounded lip that hangs into it; the name very large in ink + 7% */
.ft{position:relative;background:var(--i);color:var(--g);overflow:hidden}
.lip{--ec:var(--g);position:absolute!important;top:0;left:50%;translate:-50% 0;width:min(1120px,100% - 80px);height:40px;background:var(--g);border-radius:0 0 30px 30px}
.fin{display:flex;gap:40px;padding:100px 0 40px}.fcol:empty{display:none}.fl{flex:0 1 400px;display:flex;flex-direction:column;align-items:flex-start;gap:20px}
.ftag{font-weight:700;font-size:30px;line-height:1;letter-spacing:-.05em}.ftag span,.ftag em{display:block}
.ftx{font-size:14px;line-height:1.4;color:var(--imu)}.fsm{font-size:12px;line-height:1.6;letter-spacing:0;color:var(--imu)}
.fcol{flex:0 0 200px;display:flex;flex-direction:column;align-items:flex-start;gap:15px}.fcol a{font-weight:500;font-size:14px;line-height:1.2;letter-spacing:-.02em;transition:color .3s}.fcol a:hover{color:var(--imu)}
.word{font-weight:700;font-size:min(var(--ws),320px);line-height:1;letter-spacing:-.03em;color:var(--word);white-space:nowrap;text-align:center;margin-bottom:-.06em;user-select:none}
/* arrival: letters clear one after another (blur 10 → 0, 10px rise); blocks rise 30px; cards rise 30px when half a screen of them shows */
@keyframes chr{from{opacity:0;transform:translateY(10px);filter:blur(10px)}to{opacity:1;transform:none;filter:blur(0)}}
@keyframes up{from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:none}}
.js .c{display:inline-block;animation:chr .65s cubic-bezier(.2,.75,.25,1) both;animation-delay:calc(var(--k)*45ms + .15s)}.js .w{display:inline-block;white-space:nowrap}
.js .up{animation:up .9s cubic-bezier(.2,.75,.25,1) both;animation-delay:.9s}.js .acts.up{animation-delay:1s}.js .hnote.up{animation-delay:1.05s}.js .mock.up{animation-delay:1.1s}
.js .rv{opacity:0;transform:translateY(30px);transition:opacity .9s cubic-bezier(.2,.75,.25,1),transform .9s cubic-bezier(.2,.75,.25,1)}.js .rv.in{opacity:1;transform:none}
@media (max-width:999px){
.h2{font-size:38px}.h3{font-size:min(var(--fs,32px),32px)}.h4{font-size:19px}.sub,.lead{font-size:16px}
.top{padding:0 20px}.bar{flex:1;justify-content:space-between;min-height:50px;padding:5px 10px;gap:12px}.nav,.bar>.btn{display:none}.burger{display:flex}
.hero .wrap{padding:100px 0 110px;gap:40px}.h1{font-size:var(--fm)}.acts{flex-direction:column;align-self:stretch;gap:10px}.acts .btn{width:100%}
.hland{height:420px}.mock{gap:8px}.scr img{border-radius:10px}.side{margin-top:20px}.side img{border-radius:12px}.side.book img{border-radius:3px}
.sec,.body{padding:60px 0}.body{padding-top:20px}
.card{padding:30px}.chd p,.use p,.fig p{font-size:14px}.stage{padding:24px 16px}.stage{--mh:320px}.stage>img:not(.bk),.stage>video{border-radius:8px}
.tiles{grid-template-columns:1fr}.tile{min-height:0}.tt h4{font-size:24px}.tp{--mh:260px}.tt{padding:28px 20px}
.duo2,.g3,.qs{grid-template-columns:minmax(0,1fr)}.fv{font-size:38px}.quote{padding:40px 0}
.pc{padding:80px 30px 30px}.pbg{inset:260px 0 160px 0}
.lks{gap:20px}.lk{min-height:0;padding-bottom:210px}.lv{background:linear-gradient(var(--v) 0,var(--v) 50%,color-mix(in srgb,var(--v) 55%,transparent) 66%,transparent 90%)}.lt{gap:20px}.lt .btn{width:100%}
.lip{width:calc(100% - 80px)}.fin{flex-direction:column;padding:70px 0 40px}.fl{flex:none;margin:0}.fcol{flex:none}}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important;scroll-behavior:auto!important}.js .rv{opacity:1;transform:none}.hland img,.side{transform:none!important}}
'''

JS = r'''
(()=>{const D=document,R=D.documentElement,$=(s,r=D)=>r.querySelector(s),$$=(s,r=D)=>[...r.querySelectorAll(s)];
const still=matchMedia('(prefers-reduced-motion:reduce)').matches;R.classList.add('js');
/* letters: each word kept whole, each letter its own span; the sentence stays readable to a screen reader */
if(!still){let k=0;$$('.ch').forEach(el=>{const t=el.textContent;el.setAttribute('aria-label',t);el.setAttribute('role','text');el.textContent='';t.split(/\s+/).filter(Boolean).forEach((w,i,a)=>{const s=D.createElement('span');s.className='w';s.setAttribute('aria-hidden','true');
 for(const ch of w){const c=D.createElement('span');c.className='c';c.textContent=ch;c.style.setProperty('--k',k++);s.append(c)}el.append(s,i<a.length-1?' ':'')})});
 $$('.c').forEach(c=>c.addEventListener('animationend',()=>{c.style.animation='none'}))}
/* menu on the phone */
const bg=$('.burger'),menu=$('#menu');if(bg)bg.addEventListener('click',()=>{const o=bg.getAttribute('aria-expanded')!=='true';bg.setAttribute('aria-expanded',o);menu.hidden=!o});
if(menu)menu.addEventListener('click',e=>{if(e.target.closest('a')){bg.setAttribute('aria-expanded','false');menu.hidden=true}});
$$('video[data-auto]').forEach(v=>{if(!still){v.autoplay=true;v.play().catch(()=>{})}else v.controls=true});
/* scroll: the landscape grows 1.447% and sinks 7.24px per 100px; the second picture settles 50px between 300 and 600 */
const land=$('.hland img'),side=$('.side'),hero=$('.hero'),cl=v=>v<0?0:v>1?1:v;
const paint=()=>{if(still||!hero)return;const y=scrollY;if(y>hero.offsetHeight+200)return;if(land)land.style.transform=`translateY(${(y*.0724).toFixed(2)}px) scale(${(1+y*.0001447).toFixed(4)})`;
 if(side){const p=cl((y-300)/300),s=innerWidth<1000?.4:1;side.style.transform=`translateY(${(50*s*(1-p)*(1-p)).toFixed(2)}px)`}};
let tick=false;addEventListener('scroll',()=>{if(tick)return;tick=true;requestAnimationFrame(()=>{tick=false;paint();sweep()})},{passive:true});
/* cards arrive once the upper half of the window reaches them; whatever has been passed is shown */
const rv=$$('.rv');const sweep=()=>{const vh=innerHeight,end=scrollY+vh>=R.scrollHeight-4;for(let i=rv.length;i--;){const el=rv[i],r=el.getBoundingClientRect();if(end||r.top<vh*.5||r.bottom<vh){el.classList.add('in');rv.splice(i,1)}}};
if(still)rv.splice(0).forEach(el=>el.classList.add('in'));
/* price switch */
const seg=$('.seg');if(seg){const ts=$$('.sg',seg),ps=$$('.pp');const go=(n,f)=>{n=(n+ts.length)%ts.length;seg.style.setProperty('--k',n);ts.forEach((t,k)=>{t.setAttribute('aria-selected',k===n);t.tabIndex=k===n?0:-1});ps.forEach((p,k)=>{p.classList.toggle('on',k===n);p.inert=k!==n});if(f)ts[n].focus()};
 ts.forEach((t,k)=>{t.addEventListener('click',()=>go(k));t.addEventListener('keydown',e=>{if(e.key==='ArrowRight'){e.preventDefault();go(k+1,true)}if(e.key==='ArrowLeft'){e.preventDefault();go(k-1,true)}})});ps.forEach(p=>{p.inert=!p.classList.contains('on')})}
/* questions open and close over half a second */
$$('.q').forEach(q=>{const s=$('summary',q),a=$('.qa',q);let an=null;s.addEventListener('click',e=>{if(still||!a.animate)return;e.preventDefault();if(an)an.cancel();const open=!q.open;if(open)q.open=true;const h=a.scrollHeight;
 an=a.animate({height:open?['0px',h+'px']:[h+'px','0px'],opacity:open?[0,1]:[1,0]},{duration:500,easing:'cubic-bezier(.2,.8,.2,1)'});an.onfinish=()=>{if(!open)q.open=false;an=null};if(!open){q.classList.add('shut');an.finished.then(()=>q.classList.remove('shut'),()=>{})}})});
paint();sweep();addEventListener('load',()=>{paint();sweep()});addEventListener('resize',()=>{paint();sweep()});
})();
'''


def render(d: dict) -> str:
    c = colours(d.get('palette') or {})
    b = d.get('brand') or {}
    hero = d.get('hero') or {}
    made = (d.get('media') or {}).get('made') or {}
    tone = 'light' if lum(c['G']) > lum(c['I']) else 'dark'
    land = lead_land(made, tone)
    pool = Pool(made, tone, land)
    v = (f'--g:{c["G"]};--i:{c["I"]};--a:{c["A"]};--card:{c["card"]};--chip:{c["chip"]};--mu:{c["mu"]};--imu:{c["imu"]};--word:{c["word"]}')
    intro, stack = s_intro(d, c), s_stack(d, c, pool)
    body = f'<section class="body" id="product"><div class="wrap">{intro}{stack}</div></section>' if intro or stack else ''
    page = s_nav(d, c) + '<main>' + s_hero(d, c, land) + body + s_features(d, c) + s_plans(d, c, land) + s_faq(d, c) + s_links(d, c, pool) + '</main>' + s_foot(d, c)
    title = ' — '.join(x for x in (b.get('name'), hero.get('title')) if x)
    return f'''<!doctype html><html lang="{e(d.get("lang") or "en")}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(hero.get("text"))}"><meta name="theme-color" content="{c["G"]}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@1&family=Inter:opsz,wght@14..32,400..700&display=swap" rel="stylesheet">
<style>:root{{{v}}}::selection{{background:var(--a);color:{c["I"] if con(c["A"], c["I"]) >= con(c["A"], c["G"]) else c["G"]}}}{CSS.replace("SANS", SANS).replace("SERIF", SERIF)}</style></head><body>
{page}
<script>{JS}</script></body></html>'''
