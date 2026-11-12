"""dock/render.py — one pure function: render(d) -> a complete page built to the measures of the reference
(https://dock.cool, read 2026-11-12 at 1440x900 and 390x844; see NOTES.md). A floating pill header, a centred opening
set in a heavy tight grotesque over a landscape that fades into the page at top and bottom, a glass frame holding the
product, 30px-radius cards on a quiet ground, one inverse section where a wall of product pictures is pinned, zooms
out and folds into the app icon, a running strip of screens, raised plan cards, a two-column FAQ, a dark dock bar and
a foot with the name set across the whole width over a second landscape.
Nothing of the reference's code, words, pictures, icons, logos or typefaces is used. No client, no model call, no
file reads, no network at render."""
import html

M = '../../'
FONT = 'Inter'      # the reference sets "Inter Display" / Inter; Inter is SIL OFL and on Google Fonts with its optical-size axis


def e(s):
    return html.escape(str(s or ''), quote=True)


# ---------- colour: the client's palette goes in; the reference's relations of ground / surface / ink / accent stay ----------
def _rgb(h):
    h = (h or '#000').lstrip('#')
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


def rgba(h, a):
    r, g, b = _rgb(h)
    return f'rgba({r},{g},{b},{a:.2f})'


def quiet(ink, grounds, want=5.3):
    """the reference's grey text: ink let down toward the ground as far as every ground it stands on still allows"""
    for t in (.42, .36, .3, .24, .18, .12, .06, 0):
        m = mix(ink, grounds[0], t)
        if min(con(m, g) for g in grounds) >= want:
            return m
    return ink


def soft(ink, ground, want):
    """the name set large on the plain foot: ink let down toward the ground only as far as large type still reads (3:1)"""
    for t in (.6, .5, .4, .3, .2, .1, 0):
        m = mix(ink, ground, t)
        if con(m, ground) >= want:
            return m
    return ink


def colours(p):
    G, I, A = p.get('ground') or '#edeceb', p.get('ink') or '#000000', p.get('accent') or '#ccff00'
    dark = lum(G) < .2
    S = mix(G, I, .06) if dark else mix(G, '#ffffff', .6)          # cards: one step lighter than the canvas
    F = mix(G, I, .12) if dark else mix(G, '#ffffff', .92)         # the raised plan card and the header pill
    onA = max((I, G, '#000000', '#ffffff'), key=lambda x: con(A, x))
    # the inverse section and the dock bar: the ink as ground on a light page. On a dark page that made a white stretch
    # four screens long in a dark site, so there they are a raised dark ground (8 % ink) with the page's ink as text.
    D, oD = (mix(G, I, .08), I) if dark else (I, G)
    return dict(G=G, I=I, A=A, S=S, F=F, onA=onA, D=D, oD=oD, dark=dark,
                mut=quiet(I, [G, S, F]), mutD=quiet(oD, [D, mix(D, oD, .1)]),
                # the header pill is F at 80 % with a blur: whatever passes under it shows through by a fifth
                nav=quiet(I, [F] + [mix(F, x, .2) for x in (D, G, A, I, '#ffffff', '#000000')]),
                band=mix(G, I, .16), line=mix(G, I, .14), wq=soft(I, G, 3.2))


# ---------- pictures ----------
def made(d, kind):
    m = ((d.get('media') or {}).get('made') or {}).get(kind) or []
    return [x for x in (m if isinstance(m, list) else [m]) if isinstance(x, dict) and x.get('src')]


def pick(xs, prefs, used, tone=None):
    """one made picture by preferred index, skipping those already on the page; with `tone`, one of that tone first"""
    order = [i for i in prefs if i < len(xs)] + [i for i in range(len(xs)) if i not in prefs]
    order = [i for i in order if xs[i]['src'] not in used] or order
    if tone:
        order = [i for i in order if xs[i].get('tone') == tone] + [i for i in order if xs[i].get('tone') != tone]
    if not order:
        return None
    used.add(xs[order[0]]['src'])
    return xs[order[0]]


def veil_for(m, ground, ink, want):
    """share of the page ground laid over the picture's mean colour that gives `want`:1 for the ink"""
    mean = m.get('mean') or ('#222222' if m.get('tone') != 'light' else '#dddddd')
    for a in (.2, .3, .4, .5, .6, .7, .8, .9):
        if con(mix(mean, ground, a), ink) >= want:
            return a
    return .92


def asp(m):
    return (m.get('w') or 1) / (m.get('h') or 1)


def img(m, cls='', lazy=True, alt=None, extra=''):
    return ('<img%s src="%s%s" width="%s" height="%s" alt="%s"%s%s>' % (
        f' class="{cls}"' if cls else '', M, e(m['src']), int(m.get('w') or 0) or '', int(m.get('h') or 0) or '',
        e(m.get('alt') if alt is None else alt), ' loading="lazy" decoding="async"' if lazy else '', extra))


def rows_for(pics, width, height, gap=20):
    """how many rows the wall takes when its tiles are `height` tall and wrap inside `width`"""
    rows, x = 1, 0
    for p in pics:
        w = asp(p) * height
        if x and x + gap + w > width:
            rows, x = rows + 1, w
        else:
            x = x + (gap if x else 0) + w
    return rows


def wall_height(pics, width, room, top, gap=20):
    """the tallest tile height at which the whole wall fits in `room`"""
    for h in range(top, 60, -10):
        if max(asp(p) * h for p in pics) <= width and rows_for(pics, width, h, gap) * (h + gap) - gap <= room:
            return h
    return 70


ARROW = '<svg class="ar" viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
CHECK = '<svg viewBox="0 0 20 20" width="20" height="20" aria-hidden="true"><circle cx="10" cy="10" r="8.2" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M6.6 10.3l2.3 2.3 4.5-4.9" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def btn(c, cls='acc', arrow=False):
    if not c or not c.get('t'):
        return ''
    return f'<a class="btn {cls}" href="{e(c.get("h") or "#")}">{e(c["t"])}{ARROW if arrow else ""}</a>'


def brand_mark(b, cls='bm', lazy=False):
    logo = ''
    if b.get('logo'):
        wm = bool(b.get('logo_wordmark'))
        logo = '<img class="%s" src="%s%s" alt="%s"%s>' % ('wm' if wm else 'ic', M, e(b['logo']), e(b.get('name')) if wm else '', ' loading="lazy"' if lazy else '')
    name = '' if (b.get('logo') and b.get('logo_wordmark')) else f'<span>{e(b.get("name"))}</span>'
    return f'<a class="{cls}" href="{e(b.get("home") or "#")}">{logo}{name}</a>'


def head(title, text, cls='', wide=False, tag='h2'):
    if not title:
        return ''
    return (f'<header class="hd{" wide" if wide else ""}{" " + cls if cls else ""}"><{tag}>{e(title)}</{tag}>'
            + (f'<p class="lead">{e(text)}</p>' if text else '') + '</header>')


# ---------- sections ----------
def s_header(d, c):
    b = d.get('brand') or {}
    links = [n for n in (d.get('nav') or []) if n.get('t')]
    si = d.get('signin') or {}
    if si.get('t'):
        links = links + [si]
    nav = ''.join(f'<a href="{e(n.get("h") or "#")}">{e(n["t"])}</a>' for n in links)
    cta = d.get('cta') or {}
    small = f'<a class="btn acc sm" href="{e(cta.get("h") or "#")}">{e(cta["t"])}</a>' if cta.get('t') else ''
    mob = ''
    if links or small:
        mob = ('<details class="mn"><summary aria-label="Menu"><i></i><i></i></summary><div class="mn-p">'
               + (f'<nav aria-label="Menu"><ul>{"".join(f"<li><a href={chr(34)}{e(n.get(chr(104)) or chr(35))}{chr(34)}>{e(n[chr(116)])}</a></li>" for n in links)}</ul></nav>' if links else '')
               + small + '</div></details>')
    return (f'<header class="top"><div class="shell">{brand_mark(b)}'
            + (f'<nav class="nv" aria-label="Main">{nav}</nav>' if nav else '<span></span>') + f'<span class="dl">{small}</span>{mob}</div></header>')


def s_hero(d, c, used, upic):
    h = d.get('hero') or {}
    if not h.get('title'):
        return ''
    md = d.get('media') or {}
    eyebrow = ''
    if h.get('kicker'):
        k = str(h['kicker'])
        letters, i = '', 0
        for w in k.split(' '):
            letters += '<span class="w">' + ''.join(f'<span class="l" style="--i:{i + j}">{e(ch)}</span>' for j, ch in enumerate(w)) + '</span> '
            i += len(w)
        note = f'<span class="by" style="--i:{i + 1}">{e(h["note"])}</span>' if h.get('note') else ''
        dot = f'<span class="dot" style="--i:{i}"></span>' if note else ''
        eyebrow = f'<p class="eb"><span class="kw"><span class="vh">{e(k)}</span><span class="k" aria-hidden="true">{letters.strip()}</span></span>{dot}{note}</p>'
    text = ' '.join(x for x in (h.get('text'), h.get('text2')) if x)
    n = len(h['title'])
    size = 'h1a' if n <= 44 else 'h1b' if n <= 64 else 'h1c'
    trust = ''.join(f'<li>{e(t)}</li>' for t in (d.get('trust') or [])[:4])
    # the scene: a made landscape of the page's own tone, fading into the ground at top and bottom
    scene, fade = '', ''
    land = pick(made(d, 'land'), [0, 5, 1], upic, tone='dark' if c['dark'] else 'light')
    if land:
        a = max(.7, veil_for(land, c['G'], c['mut'], 4.9))
        gv = rgba(c['G'], a)
        scene = (f'<div class="scene" data-slot="land" style="--gv:{gv}">{img(land, "", lazy=False, alt="")}'
                 '<span class="f1"></span><span class="f2"></span></div>')
    # the glass frame: the product's first screen, whole
    first = next((x for k in ('screens', 'phones', 'photos') for x in md.get(k) or [] if x.get('src')), None)
    frame = ''
    if first:
        used.add(first['src'])
        frame = f'<figure class="glass" style="--w:{min(948, round(640 * asp(first)))}px">{img(first, "", lazy=False)}</figure>'
    return (f'<section class="hero"><div class="hero-c">{eyebrow}<h1 class="{size}">{e(h["title"])}</h1>'
            + (f'<p class="sub">{e(text)}</p>' if text else '') + btn(h.get('primary') or d.get('cta'), 'acc big')
            + (f'<ul class="tr">{trust}</ul>' if trust else '') + f'</div><div class="hero-b">{scene}{frame}</div></section>')


def s_features(d, c, used):
    f = d.get('features') or {}
    md = d.get('media') or {}
    if not f.get('title'):
        return ''
    chips = ''.join(f'<li>{e(x["t"])}</li>' for x in f.get('items') or [] if x.get('t'))
    media = ''
    v = md.get('video') or {}
    if v.get('src'):
        media = ('<figure class="fm" style="--a:%.4f"><video controls loop muted playsinline preload="metadata" width="%s" height="%s"%s aria-label="%s"><source src="%s%s" type="video/mp4"></video></figure>' % (
            asp(v), v.get('w') or '', v.get('h') or '', f' poster="{M}{e(v["poster"])}"' if v.get('poster') else '', e(v.get('alt')), M, e(v['src'])))
    else:
        s = next((x for x in md.get('screens') or [] if x.get('src') and x['src'] not in used), None)
        if s:
            used.add(s['src'])
            media = f'<figure class="fm" style="--a:{asp(s):.4f}">{img(s)}</figure>'
    return (f'<section class="sec feat"><div class="wrap">{head(f["title"], f.get("text"), wide=True)}'
            + (f'<ul class="chips">{chips}</ul>' if chips else '') + media + '</div></section>')


def s_quote(d, c):
    """the reference's single centred quote under the film — only when there is a quote"""
    qs = [q for q in d.get('quotes') or [] if isinstance(q, dict) and (q.get('text') or q.get('quote') or q.get('q'))]
    if not qs:
        return ''
    q = qs[0]
    by = q.get('name') or q.get('by')
    return ('<section class="one"><figure><blockquote>%s</blockquote>%s</figure></section>' % (
        e(q.get('text') or q.get('quote') or q.get('q')),
        f'<figcaption><strong>{e(by)}</strong>{f"<small>{e(q.get(chr(114) + chr(111) + chr(108) + chr(101)))}</small>" if q.get("role") else ""}</figcaption>' if by else ''))


def s_cards(d, c, used):
    s = d.get('steps') or {}
    md = d.get('media') or {}
    items = [x for x in s.get('items') or [] if x.get('title')]
    if not items:
        return ''
    known = {x.get('src'): x for k in ('phones', 'photos', 'screens') for x in md.get(k) or []}
    cards = ''
    for i, x in enumerate(items):
        pic = ''
        if x.get('img'):
            m = dict(known.get(x['img']) or {'src': x['img']})
            used.add(m['src'])
            tall = asp(m) < 1 if m.get('w') else x.get('shape') in ('phone', 'book')
            more = ''
            if tall and len(items) % 2 and i == len(items) - 1:
                # the card that spans both columns carries a row, as the reference's cards do: the client's other
                # pictures of the same kind that no step has taken
                taken = {y.get('img') for y in items}
                rest = [y for k in ('phones', 'photos') for y in md.get(k) or [] if y.get('src') and y['src'] not in taken and y.get('w') and asp(y) < 1]
                more = ''.join(img(y) for y in rest[:3])
            pic = f'<div class="cm{" tall" if tall else ""}">{img(m)}{more}</div>'
        cta = x.get('cta') or {}
        link = f'<p><a class="tl" href="{e(cta.get("h") or "#")}">{e(cta["t"])}</a></p>' if cta.get('t') else ''
        last = ' last' if len(items) % 2 and i == len(items) - 1 else ''
        cards += (f'<article class="card{last}" data-rv><div class="ct"><h3>{e(x["title"])}</h3>'
                  + (f'<p>{e(x["text"])}</p>' if x.get('text') else '') + link + f'</div>{pic}</article>')
    return f'<section class="sec cats"><div class="wrap">{head(s.get("title"), s.get("text"))}<div class="grid">{cards}</div></div></section>'


def s_statement(d, c, used, upic):
    s = d.get('statement') or {}
    md = d.get('media') or {}
    if not s.get('title'):
        return ''
    land = pick(made(d, 'land'), [1, 3, 4], upic)
    scr = next((x for x in md.get('screens') or [] if x.get('src') and x['src'] not in used), None)
    media = ''
    if land or scr:
        if scr:
            used.add(scr['src'])
        media = ('<figure class="stage" data-slot="land">' + (img(land, 'bg', alt='') if land else '')
                 + (img(scr, 'on') if scr else '') + '</figure>')
    return f'<section class="sec stmt"><div class="wrap">{head(s["title"], s.get("text"), wide=True)}{media}</div></section>'


def s_quotes(d, c):
    qs = [q for q in d.get('quotes') or [] if isinstance(q, dict) and (q.get('text') or q.get('quote') or q.get('q'))]
    if len(qs) < 2:
        return ''
    cols = ['', '']
    for i, q in enumerate(qs[1:] if len(qs) > 2 else qs):
        by = q.get('name') or q.get('by')
        cap = f'<figcaption><strong>{e(by)}</strong>{f"<span>{e(q.get(chr(114) + chr(111) + chr(108) + chr(101)))}</span>" if q.get("role") else ""}</figcaption>' if by else ''
        cols[i % 2] += f'<figure class="q" data-rv>{cap}<blockquote>{e(q.get("text") or q.get("quote") or q.get("q"))}</blockquote></figure>'
    return f'<section class="sec qs"><div class="wrap"><div class="qg"><div>{cols[0]}</div><div>{cols[1]}</div></div></div></section>'


def all_pics(d):
    md = d.get('media') or {}
    out, seen = [], set()
    for k in ('screens', 'phones', 'photos'):
        for x in md.get(k) or []:
            if x.get('src') and x.get('w') and x.get('h') and x['src'] not in seen:
                seen.add(x['src'])
                out.append(x)
    return out


def s_wall(d, c):
    cl = d.get('close') or {}
    if not cl.get('title'):
        return ''
    b = d.get('brand') or {}
    pics = all_pics(d)
    # screens and tall pictures dealt alternately so that every row of the wall mixes both
    wide, tall = [p for p in pics if asp(p) >= 1], [p for p in pics if asp(p) < 1]
    order = []
    while wide or tall:
        if wide:
            order.append(wide.pop(0))
        for _ in range(2):
            if tall:
                order.append(tall.pop(0))
    wall = ''
    if order:
        hd, hm = wall_height(order, 1120, 700, 300), wall_height(order, 350, 560, 200, 10)
        tiles = ''.join(f'<span style="--a:{asp(p):.4f}">{img(p, alt="")}</span>' for p in order)
        wall = f'<div class="wf" aria-hidden="true"><div class="wl" style="--th:{hd}px;--tm:{hm}px">{tiles}</div></div>'
    icon = ''
    if b.get('logo'):
        icon = '<span class="ai%s"><img src="%s%s" alt="" loading="lazy"></span>' % (' wm' if b.get('logo_wordmark') else '', M, e(b['logo']))
    return (f'<section class="cta" data-wall><div class="cta-in"><div class="cta-s">{wall}<div class="cta-c">{icon}<div class="cta-t">'
            f'<h2>{e(cl["title"])}</h2>' + (f'<p class="lead">{e(cl["text"])}</p>' if cl.get('text') else '')
            + btn(cl.get('cta') or d.get('cta'), 'acc big') + '</div></div></div></div></section>')


def s_strip(d, c, used):
    pics = all_pics(d)
    rest = [p for p in pics if p['src'] not in used]
    for p in pics:                                   # the reference runs three; top up with screens already shown
        if len(rest) >= 3:
            break
        if p not in rest:
            rest.append(p)
    if len(rest) < 2:
        return ''
    width = sum(400 * asp(p) + 20 for p in rest)
    reps = 1
    while width * reps < 2000:
        reps += 1
    one = ''.join(f'<figure class="gh" style="--a:{asp(p):.4f};background-image:var(--s{i})"'
                  + (f' role="img" aria-label="{e(p["alt"])}"' if p.get('alt') else ' aria-hidden="true"') + '></figure>' for i, p in enumerate(rest))
    # the repeats that make the strip endless are drawn from one custom property per picture, so each picture is one
    # file in the page (and in the one-file copy) however many times it passes
    ghost = ''.join(f'<figure class="gh" style="--a:{asp(p):.4f};background-image:var(--s{i})" aria-hidden="true"></figure>' for i, p in enumerate(rest))
    svars = ''.join(f'--s{i}:url({M}{e(p["src"])});' for i, p in enumerate(rest))
    return (f'<section class="strip" aria-label="Screens"><div class="sv"><div class="st" style="{svars}--dur:{width * reps / 50:.1f}s">'
            + one + ghost * (reps * 2 - 1) + '</div></div></section>')


def s_plans(d, c):
    p = d.get('plans') or {}
    items = [x for x in p.get('items') or [] if x.get('name')]
    if not items:
        return ''
    rows_any = any(x.get('rows') for x in items)
    cards = ''
    for x in items:
        rows = ''.join(f'<li>{CHECK}<span>{e(r)}</span></li>' for r in x.get('rows') or [])
        cta = x.get('cta') or {}
        cards += (f'<article class="plan{" ft" if x.get("marked") else ""}" data-rv><h3>{e(x["name"])}</h3>'
                  + (f'<p class="pr"><strong>{e(x["price"])}</strong></p>' if x.get('price') else '')
                  + (f'<p class="per">{e(x["per"])}</p>' if x.get('per') else '')
                  + (f'<p class="ln">{e(x["line"])}</p>' if x.get('line') else '')
                  + (f'<ul>{rows}</ul>' if rows else '')
                  + (f'<a class="btn {"acc" if x.get("marked") else "ink"} full" href="{e(cta.get("h") or "#")}">{e(cta["t"])}{ARROW}</a>' if cta.get('t') else '')
                  + '</article>')
    return (f'<section class="sec plans"><div class="wrap">{head(p.get("title"), p.get("text"), "ph")}'
            f'<div class="stg{"" if rows_any else " short"}"><div class="pc">{cards}</div></div>'
            + (f'<p class="pn">{e(p["note"])}</p>' if p.get('note') else '') + '</div></section>')


def s_faq(d, c):
    f = d.get('faq') or {}
    items = [x for x in f.get('items') or [] if x.get('q') and x.get('a')]
    if not items:
        return ''
    half = (len(items) + 1) // 2
    def col(xs):
        return '<div class="fc">' + ''.join(
            f'<details class="fq"><summary><i aria-hidden="true"></i><span>{e(x["q"])}</span></summary><div class="fa"><p>{e(x["a"])}</p></div></details>' for x in xs) + '</div>'
    return (f'<section class="sec faq"><div class="wrap">{head(f.get("title"), f.get("text"))}'
            f'<div class="fl">{col(items[:half])}{col(items[half:]) if items[half:] else ""}</div></div></section>')


def s_close(d, c):
    """the reference's closing: a strip of badges (logos) and the dock bar standing alone (figures)"""
    logos = [x for x in d.get('logos') or [] if isinstance(x, dict) and x.get('src')]
    figs = [x for x in d.get('figures') or [] if x.get('v')]
    if not logos and not figs:
        return ''
    lg = ''
    if logos:
        one = ''.join(img(x, 'lg') for x in logos)
        lg = f'<div class="bv"><div class="bt">{one}{one}</div></div>'
    dock = ''
    if figs:
        dock = '<dl class="dock">' + ''.join(
            f'<div><dt>{e(x["v"])}</dt>' + (f'<dd>{e(x["l"])}</dd>' if x.get('l') else '') + '</div>' for x in figs[:4]) + '</dl>'
    return f'<section class="end">{lg}{dock}</section>'


def s_foot(d, c, upic):
    b, f, h = d.get('brand') or {}, d.get('foot') or {}, d.get('hero') or {}
    cols = []
    for xs in (d.get('nav') or [], d.get('links') or [], (f.get('links') or []) + ([d['signin']] if (d.get('signin') or {}).get('t') else [])):
        xs = [x for x in xs if x.get('t')]
        if xs:
            cols.append('<ul>' + ''.join(f'<li><a href="{e(x.get("h") or "#")}">{e(x["t"])}</a></li>' for x in xs) + '</ul>')
    cta = d.get('cta') or {}
    land = pick(made(d, 'land'), [5, 2, 0], upic)
    # the name over the landscape takes the palette end that reads on that picture (the page colour on a dark page was
    # dark on a dark landscape)
    lo, hi = sorted((c['G'], c['I']), key=lum)
    wf, veil = '', ''
    if land:
        # measured, not assumed from the tone: the name stands on the picture's mean colour, which the foot's lower fade
        # takes up to 55 % toward the page ground; the end that reads best over that whole range is taken, and when
        # neither reaches 3:1 (large type) the end farthest from the ground is laid on a veil of the ground made just
        # strong enough
        mean = land.get('mean') or ('#222222' if land.get('tone') != 'light' else '#dddddd')
        worst = lambda x: min(con(x, mix(mean, c['G'], t)) for t in (0, .2, .4, .55))
        ink = max((lo, hi), key=worst)
        if worst(ink) < 3.2:
            ink = max((lo, hi), key=lambda x: con(x, c['G']))
            a = next((t for t in (.3, .4, .5, .6, .7, .8, .9) if con(ink, mix(mean, c['G'], t)) >= 3.4), .92)
            veil = '<span class="f3" style="--wv:%s"></span>' % rgba(c['G'], a)
        wf = ' style="--wf:%s"' % ink
    name = str(b.get('name') or '')
    word = ''
    if name:
        fs = min(320, round(1200 / (max(len(name), 3) * .56)))
        word = (f'<svg class="word" viewBox="0 0 1200 {round(fs * .96)}" aria-hidden="true"><text x="0" y="{round(fs * .8)}" font-size="{fs}" '
                f'textLength="1200" lengthAdjust="spacing">{e(name)}</text></svg>')
    return ('<footer class="ft"><div class="wrap fcn"><div class="fb">' + brand_mark(b, 'bm', lazy=True)
            + (f'<p class="tg">{e(h["kicker"])}</p>' if h.get('kicker') else '')
            + (f'<p class="fx">{e(f.get("text") or h.get("text"))}</p>' if (f.get('text') or h.get('text')) else '')
            + (f'<a class="btn acc sm" href="{e(cta.get("h") or "#")}">{e(cta["t"])}</a>' if cta.get('t') else '')
            + (f'<p class="lg2">{e(f["legal"])}</p>' if f.get('legal') else '') + '</div>'
            + (f'<nav class="fls" aria-label="Footer">{"".join(cols)}</nav>' if cols else '') + '</div>'
            + f'<div class="fbt{"" if land else " plain"}" data-slot="land">' + (img(land, 'fbg', alt='') + '<span class="f1"></span><span class="f2"></span>' if land else '')
            + veil + f'<div class="wrap"{wf}>{word}</div></div></footer>')


SPRING = ('linear(0 0%,.08125 5%,.24218 10%,.41161 15%,.56054 20%,.68051 25%,.77231 30%,.84018 35%,.88917 40%,.92389 45%,'
          '.94816 50%,.96493 55%,.97641 60%,.98421 65%,.98948 70%,.99302 75%,.99538 80%,.99695 85%,.998 90%,.99869 95%,1 100%)')

CSS = r'''
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{margin:0;background:var(--G);color:var(--I);font-family:"Inter",-apple-system,"Segoe UI",sans-serif;font-size:16px;line-height:1.4;font-optical-sizing:auto;-webkit-font-smoothing:antialiased;overflow-x:clip}
img,video,svg{display:block;max-width:100%}
img,video{height:auto}
a{color:inherit;text-decoration:none}
h1,h2,h3,p,ul,dl,dd,figure,blockquote{margin:0;padding:0}
ul{list-style:none}
:focus-visible{outline:2px solid var(--I);outline-offset:3px;border-radius:6px}
.cta :focus-visible{outline-color:var(--oD)}
video:focus-visible,video:focus,video:focus-within{outline:2px solid var(--I);outline-offset:-2px}
.fm:focus-within{outline:2px solid var(--I);outline-offset:3px}
.vh{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%);white-space:nowrap}
.skip{position:fixed;top:12px;left:12px;z-index:200;background:var(--I);color:var(--G);padding:10px 14px;border-radius:10px;transform:translateY(-200%)}
.skip:focus{transform:none}
.wrap{width:min(100% - 80px,1120px);margin-inline:auto}
/* buttons: 52 high, r20, 16/600; hover lifts 2px in .18s; press rounds the corners to 40 */
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:52px;padding:15px 30px;border-radius:20px;font-size:16px;font-weight:600;line-height:22.4px;text-align:center;transition:transform .18s cubic-bezier(.2,.7,.2,1),background-color .18s ease,color .18s ease,box-shadow .18s ease}
.btn:hover{transform:translateY(-2px)}
.btn:active{border-radius:40px}
.btn.acc{background:var(--A);color:var(--onA);box-shadow:0 10px 28px var(--Ag)}
.btn.acc:hover{box-shadow:0 12px 34px var(--Ag2)}
.btn.ink{background:var(--I);color:var(--G)}
.btn.sm{min-height:33px;padding:8px 16px;border-radius:8px;font-size:12px;font-weight:700;line-height:16.8px}
.btn.sm:active{border-radius:17px}
.btn.full{width:100%;padding:14px 16px;font-size:15px;line-height:21px;letter-spacing:-.16px}
.btn .ar{flex:none}
/* header: a pill fixed 20px from the top */
.top{position:fixed;top:20px;left:0;width:100%;z-index:100;pointer-events:none;animation:top-in 1s var(--spring) 1.5s backwards}
.shell{pointer-events:auto;position:relative;display:grid;grid-template-columns:auto minmax(0,1fr) auto;align-items:center;gap:40px;width:fit-content;min-width:min(100% - 40px,610px);max-width:calc(100% - 40px);height:52.8px;margin-inline:auto;padding:10px;border-radius:18px;background:var(--Fa);-webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);box-shadow:inset 1px 1px 1px var(--hl)}
.bm{display:inline-flex;align-items:center;gap:10px;font-size:16px;font-weight:600;line-height:19.2px;letter-spacing:-.32px;white-space:nowrap}
.bm .ic{height:30px;width:auto;max-width:none;border-radius:8px}
.bm .wm{height:20px;width:auto;max-width:none;margin-left:6px}
.nv{display:flex;gap:20px;justify-content:center;white-space:nowrap}
.nv a{font-size:14px;font-weight:500;line-height:16.8px;letter-spacing:-.28px;color:var(--nav);transition:color .15s}
.nv a:hover{color:var(--I)}
.mn{display:none}
/* hero */
.hero{position:relative;padding:142.5px 0 160px;text-align:center;overflow:clip}
.hero-b{position:relative;margin-top:61px;min-height:300px}
.scene{position:absolute;top:-442px;left:0;width:100%;height:800px;overflow:hidden;z-index:0}
.scene img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;animation:scene-in 1s cubic-bezier(.16,1,.3,1) backwards}
.scene span{position:absolute;left:0;right:0;z-index:1;pointer-events:none}
.scene .f1{top:0;height:454px;background:linear-gradient(180deg,var(--G) 0%,var(--G) 16%,var(--gv) 84%,var(--G0) 100%)}
.scene .f2{bottom:0;height:350px;background:linear-gradient(180deg,var(--G0) 0%,var(--G) 100%)}
.hero-c{position:relative;z-index:3;width:min(100% - 40px,680px);margin-inline:auto}
.eb{display:flex;flex-wrap:wrap;justify-content:center;align-items:center;gap:6px 10px;margin-bottom:22.5px;font-size:20px;line-height:25px;letter-spacing:-.4px;font-weight:600}
.eb .kw{position:relative;display:inline-flex;max-width:100%}.eb .kw .vh{left:0;top:0}
.eb .k{display:inline-flex;flex-wrap:wrap;justify-content:center;gap:0 .26em}
.eb .w{display:inline-flex}
.eb .l,.eb .dot,.eb .by{display:inline-block;animation:letter-in 1s var(--spring) calc(1.5s + var(--i)*.05s) backwards}
.eb .dot{width:4px;height:4px;border-radius:50%;background:currentColor}
.eb .by{font-weight:400}
h1{font-weight:700;text-wrap:balance;animation:rise 1s var(--spring) .3s backwards}
.h1a{font-size:80px;line-height:80px;letter-spacing:-4px}
.h1b{font-size:68px;line-height:68px;letter-spacing:-3.4px}
.h1c{font-size:56px;line-height:58px;letter-spacing:-2.8px}
.sub{margin-top:20px;font-size:20px;line-height:28px;letter-spacing:-.2px;color:var(--mut);text-wrap:pretty;animation:rise 1s var(--spring) 1s backwards}
.hero .btn{margin-top:20px;animation:rise 1s var(--spring) 1.5s backwards}
.tr{display:flex;flex-wrap:wrap;justify-content:center;gap:0 20px;margin-top:15px;font-size:12px;line-height:19.2px;color:var(--mut);animation:rise 1s var(--spring) 1.5s backwards}
.glass{position:relative;z-index:2;width:min(100% - 40px,var(--w));margin:0 auto;padding:10px;border-radius:30px;background:rgba(255,255,255,.2);-webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);box-shadow:inset 0 2px 4px rgba(255,255,255,.2),inset 0 4px 8px rgba(255,255,255,.25),inset 0 -20px 20px rgba(255,255,255,.12),inset 0 -1px rgba(255,255,255,.4);animation:rise 1s var(--spring) 1s backwards}
.glass::after{content:"";position:absolute;inset:0;border-radius:inherit;border:1px solid rgba(255,255,255,.6);pointer-events:none}
.glass img{width:100%;border-radius:20px}
/* section heads: 60/60 -3 bold, 20/28 under it */
.sec{padding-top:100px}
.hd{width:min(100%,600px);margin-inline:auto;text-align:center;display:flex;flex-direction:column;gap:20px}
.hd.wide{width:min(100%,700px)}
h2{font-size:60px;line-height:60px;letter-spacing:-3px;font-weight:700;text-wrap:balance}
.lead{font-size:20px;line-height:28px;letter-spacing:-.2px;text-wrap:pretty}
.ph .lead,.faq .lead{color:var(--mut)}
/* features: chips and the film */
.chips{display:flex;flex-wrap:wrap;justify-content:center;gap:10px;width:min(100%,700px);margin:20px auto 0}
.chips li{display:inline-flex;align-items:center;min-height:29.2px;padding:5px 10px;border-radius:30px;background:var(--S);font-size:12px;font-weight:500;line-height:19.2px}
.fm{width:min(100%,calc(730px*var(--a)));aspect-ratio:var(--a);margin:60px auto 0;border-radius:30px;overflow:hidden;background:var(--S)}
.fm img,.fm video{width:100%;height:100%;object-fit:contain}
.feat{padding-bottom:100px}
.one{padding:0 20px 100px}
.one figure{width:min(100%,500px);margin-inline:auto;text-align:center;display:flex;flex-direction:column;align-items:center;gap:20px}
.one blockquote{font-size:16px;line-height:22.4px;letter-spacing:-.16px}
.one figcaption,.q figcaption{display:flex;flex-direction:column;gap:5px;text-align:left}
.one strong,.q strong{font-size:16px;line-height:16px;letter-spacing:-.8px;font-weight:700}
.one small,.q span{font-size:12px;line-height:16.8px;letter-spacing:-.12px;color:var(--mut)}
/* cards: two columns of 550, r30, pad 40 */
.cats{padding-top:0;padding-bottom:200px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:60px}
.card{display:flex;flex-direction:column;align-items:flex-start;gap:20px;min-height:488px;padding:40px;border-radius:30px;background:var(--S);overflow:clip;min-width:0}
.ct{display:flex;flex-direction:column;gap:20px;width:100%}
.card h3{font-size:30px;line-height:30px;letter-spacing:-1.5px;font-weight:700;text-wrap:balance}
.card p{font-size:16px;line-height:22.4px;letter-spacing:-.16px}
.tl{font-weight:600;text-decoration:underline;text-underline-offset:.18em}
.cm{display:flex;flex-wrap:wrap;align-items:flex-start;gap:10px;width:100%;margin-top:auto}
.cm img{width:100%;border-radius:13px}
.cm.tall img{width:220px}
.card.last{grid-column:1/-1;min-height:0}
.card.last .ct{width:min(100%,470px)}
/* statement: head and one wide picture box 1120x730 r30 */
.stmt{padding-top:0;padding-bottom:100px}
.stage{position:relative;aspect-ratio:1120/730;margin-top:60px;border-radius:30px;overflow:hidden;background:var(--S);display:grid;place-items:center}
.stage .bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.stage .on{position:relative;width:auto;height:auto;max-width:66%;max-height:76%;border-radius:20px}
/* quotes wall */
.qs{padding-bottom:200px}
.qg{display:grid;grid-template-columns:1fr 1fr;gap:20px;align-items:start}
.qg>div{display:flex;flex-direction:column;gap:20px}
.q{display:flex;flex-direction:column;gap:20px;padding:40px;border-radius:30px;background:var(--S)}
.q blockquote{font-size:16px;line-height:22.4px;letter-spacing:-.16px;color:var(--mut)}
/* inverse section: the wall */
.cta{position:relative;background:var(--D);color:var(--oD);overflow:clip}
.cta-in{width:min(100%,1200px);margin-inline:auto;padding:100px 40px}
.cta-s{position:relative;display:flex;flex-direction:column;gap:60px}
.wf{display:flex;justify-content:center;align-items:center;pointer-events:none}
.wl{display:flex;flex-wrap:wrap;place-content:center;align-items:center;gap:20px;width:100%}
.wl span{flex:none;height:var(--th);aspect-ratio:var(--a)}
.wl img{width:100%;height:100%;border-radius:12px}
.cta-c{position:relative;z-index:2;display:flex;flex-direction:column;align-items:center;gap:40px;text-align:center}
.ai{display:grid;place-items:center;width:120px;height:120px}
.ai img{width:auto;height:auto;max-width:120px;max-height:120px;border-radius:26px}
.ai.wm{width:auto;height:120px;padding:0 34px;border-radius:26px;background:var(--G)}
.ai.wm img{width:auto;height:34px;max-width:none;border-radius:0}
.cta-t{display:flex;flex-direction:column;align-items:center;gap:20px;width:min(100%,600px)}
.cta .lead{color:var(--mutD)}
.cta .btn{margin-top:15px}
.js .cta-in{padding-top:0}
.js .cta-s{height:calc(var(--fh) + 300vh);display:block}
.js .wf{position:sticky;top:0;height:var(--fh);z-index:1}
.js .wl{will-change:transform,opacity;transform-origin:50% 50%}
.js .cta-c{position:absolute;left:0;right:0;top:calc(100% - var(--fh)/2 - 60px)}
.js .ai{will-change:transform,opacity}
/* running strip of screens: 400 high, gap 20, r20 */
.strip{height:700px;padding:200px 0 100px;overflow:clip}
.sv{height:400px;overflow:hidden}
.st{display:flex;gap:20px;width:max-content;height:400px;animation:run var(--dur) linear infinite}
.st figure{flex:none;height:400px;aspect-ratio:var(--a)}
.st img{width:100%;height:100%;border-radius:20px}.st .gh{border-radius:20px;background-size:100% 100%;background-repeat:no-repeat}
/* plans */
.plans{padding-bottom:100px}
.stg{position:relative;margin-top:56px;padding-block:0}
.stg::before{content:"";position:absolute;left:50%;top:0;width:100vw;height:640px;max-height:100%;transform:translateX(-50%);background:linear-gradient(180deg,var(--G) 0%,var(--band) 76%,var(--G) 100%)}
.pc{position:relative;display:flex;justify-content:center;align-items:center;gap:20px}
.plan{display:flex;flex-direction:column;flex:0 1 387px;min-width:0;min-height:540px;padding:32px 28px 28px;border-radius:32px;background:var(--S);border:1px solid var(--pl);box-shadow:0 12px 36px rgba(26,30,35,.04);text-align:center}
.plan.ft{min-height:620px;background:var(--F);box-shadow:0 20px 50px rgba(26,30,35,.1)}
.short .plan{min-height:0}
.short .plan.ft{padding-block:72px 68px}
.plan h3{font-size:25px;line-height:30px;letter-spacing:-1px;font-weight:650}
.pr{margin-top:62px}
.pr strong{font-size:60px;line-height:60px;letter-spacing:-3.3px;font-weight:700}
.per,.ln{margin-top:12px;font-size:12px;line-height:16.8px;color:var(--mut)}
.plan ul{display:flex;flex-direction:column;gap:14px;margin-top:32px;margin-bottom:40px;text-align:left}
.plan li{display:flex;gap:9px;align-items:flex-start;font-size:14px;line-height:21px;letter-spacing:-.14px}
.plan li svg{flex:none;color:var(--mut)}
.plan .btn{margin-top:auto}
.short .plan .btn{margin-top:40px}
.pn{position:relative;width:min(100%,750px);margin:72px auto 0;text-align:center;font-size:14px;line-height:22.4px;color:var(--mut)}
/* faq */
.fl{display:flex;gap:20px;align-items:flex-start;width:min(100%,1000px);margin:60px auto 0}
.fc{flex:1 1 0;min-width:0;display:flex;flex-direction:column;gap:20px}
.fq{border-radius:20px;background:var(--S);padding:0 20px;overflow:hidden}
.fq[open]{padding-bottom:20px}
.fq summary{position:relative;display:flex;align-items:center;gap:24px;padding:20px 0 20px 40px;cursor:pointer;list-style:none;font-size:14px;line-height:22.4px}
.fq summary::-webkit-details-marker{display:none}
.fq i{position:absolute;left:0;top:25px;width:16px;height:16px}
.fq i::before,.fq i::after{content:"";position:absolute;background:var(--I);border-radius:10px;width:16px;height:2px;top:7px;left:0}
.fq i::after{width:2px;height:16px;top:0;left:7px}
.fq[open] i{transform:rotate(45deg)}
.fa{padding:0 20px 0 40px}
.fa p{font-size:16px;line-height:25.6px;color:var(--mut)}
/* closing: the dock bar alone */
.end{padding:100px 20px 0;display:flex;flex-direction:column;align-items:center;gap:60px}
.bv{width:min(100%,1000px);overflow:hidden;-webkit-mask-image:linear-gradient(90deg,transparent,#000 48px,#000 calc(100% - 48px),transparent);mask-image:linear-gradient(90deg,transparent,#000 48px,#000 calc(100% - 48px),transparent)}
.bt{display:flex;gap:20px;width:max-content;align-items:center;animation:run 40s linear infinite}
.bt .lg{height:48px;width:auto}
.dock{display:flex;align-items:stretch;gap:10px;min-height:100px;max-width:min(100%,1120px);padding:10px;border-radius:30px;background:var(--D);color:var(--oD)}
.dock div{display:flex;flex-direction:column;justify-content:center;min-height:80px;padding:10px 20px;border-radius:20px;background:var(--oD1);box-shadow:inset 0 0 0 1px var(--oD1)}
.dock dt{font-size:30px;line-height:36px;font-weight:600;white-space:nowrap}
.dock dd{font-size:12px;line-height:14.4px;color:var(--mutD);max-width:210px}
/* foot */
.ft{position:relative;padding-top:100px;overflow:hidden}
.fcn{position:relative;z-index:2;display:flex;gap:32px;align-items:flex-start}
.fb{flex:0 0 274px;display:flex;flex-direction:column;align-items:flex-start}
.tg{margin-top:15px;font-size:20px;line-height:20px;letter-spacing:-1px;font-weight:700}
.fx{margin-top:20px;font-size:14px;line-height:19.6px;letter-spacing:-.14px}
.fb .btn{margin-top:20px}
.lg2{margin-top:20px;font-size:12px;line-height:19.2px}
.fls{display:flex;gap:32px;flex:1}
.fls ul{flex:0 0 137px;display:flex;flex-direction:column;gap:15px}
.fls a{font-size:14px;line-height:22.4px}
.fls a:hover,.tl:hover{text-decoration:underline;text-underline-offset:.18em}
.fbt{position:relative;margin-top:-10px;padding-top:150px}
.fbt.plain{padding-top:58px}
.fbg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.fbt span{position:absolute;left:0;right:0;z-index:1}
.fbt .f1{top:0;height:225px;background:linear-gradient(180deg,var(--G) 0%,var(--G0) 100%)}
.fbt .f2{bottom:0;height:200px;background:linear-gradient(180deg,var(--G0) 0%,var(--G55) 100%)}
.fbt .f3{top:60px;bottom:0;background:linear-gradient(180deg,var(--G0) 0,var(--wv) 90px)}
.word{position:relative;z-index:2;width:100%;height:auto;margin-bottom:-2.2%;overflow:visible}
.word text{fill:var(--wf,var(--G));font-weight:600;font-family:"Inter",sans-serif}
.plain .word text{fill:var(--wq)}
/* cards rise 30px and fade in over .76s when they come into view */
.js [data-rv]{opacity:0;transform:translateY(30px);transition:opacity .76s cubic-bezier(.16,1,.3,1),transform .76s cubic-bezier(.16,1,.3,1)}
.js [data-rv].in{opacity:1;transform:none}
@keyframes top-in{from{opacity:0;translate:0 -53px}}
@keyframes letter-in{from{opacity:0;filter:blur(10px);translate:0 10px}}
@keyframes rise{from{opacity:0;translate:0 30px}}
@keyframes scene-in{from{transform:scale(1.04)}to{transform:scale(1)}}
@keyframes run{to{transform:translateX(calc(-50% - 10px))}}
@media (max-width:1199px){
 .h1a{font-size:68px;line-height:68px;letter-spacing:-3.4px}
 h2{font-size:48px;line-height:48px;letter-spacing:-2.4px}
 .fls ul{flex:1 1 0}
}
@media (max-width:1000px){
 .nv,.dl{display:none}
 .shell{grid-template-columns:1fr auto;gap:10px;width:calc(100% - 40px);height:50px}
 .mn{display:block}
 .mn summary{display:grid;place-content:center;gap:6px;width:40px;height:40px;margin:-5px -5px -5px 0;list-style:none;cursor:pointer;position:relative;z-index:2}
 .mn summary::-webkit-details-marker{display:none}
 .mn summary i{display:block;width:20px;height:2px;border-radius:2px;background:var(--I)}
 .mn[open] summary i:first-child{transform:translateY(4px) rotate(45deg)}
 .mn[open] summary i:last-child{transform:translateY(-4px) rotate(-45deg)}
 .mn-p{position:absolute;top:-1px;left:-1px;right:-1px;z-index:1;display:flex;flex-direction:column;gap:40px;padding:93px 11px 11px;border-radius:18px;background:var(--F);box-shadow:inset 1px 1px 1px var(--hl),0 20px 50px rgba(26,30,35,.1)}
 .mn-p ul{display:flex;flex-direction:column;gap:30px;padding:0 20px}
 .mn-p li a{display:block;font-size:24px;line-height:24px}
 .mn-p .btn{width:100%}
 .mn[open]~*{visibility:hidden}
 .shell:has(.mn[open]) .bm{position:relative;z-index:2}
}
@media (max-width:809px){
 .wrap{width:calc(100% - 40px)}
 .hero{padding:123px 0 100px}
 .hero-b{margin-top:60px;min-height:200px}
 .scene{top:-320px;height:519px}
 .scene .f1{height:320px}
 .scene .f2{height:240px}
 .hero-c{width:calc(100% - 40px)}
 .eb{margin-bottom:17px}
 .eb .dot{display:none}
 .h1a{font-size:51px;line-height:51px;letter-spacing:-2.55px}
 .h1b{font-size:44px;line-height:45px;letter-spacing:-2.2px}
 .h1c{font-size:38px;line-height:40px;letter-spacing:-1.9px}
 .sub{font-size:16px;line-height:22.4px;letter-spacing:-.16px}
 .hero .btn{width:100%;padding-inline:12px;font-size:14px}
 .tr{margin-top:14px}
 .glass{padding:5px;border-radius:17px;width:min(100% - 58px,var(--w))}
 .glass img{border-radius:12px}
 .sec{padding-top:80px}
 .cats,.stmt{padding-top:0}
 h2{font-size:38px;line-height:38px;letter-spacing:-1.9px}
 .lead{font-size:16px;line-height:22.4px;letter-spacing:-.16px}
 .fm{margin-top:40px}
 .feat{padding-bottom:80px}
 .grid{grid-template-columns:1fr}
 .card{min-height:0;padding:30px}
 .card h3{font-size:19px;line-height:19px;letter-spacing:-.95px}
 .card p{font-size:14px;line-height:19.6px;letter-spacing:-.14px}
 .cm.tall img{width:calc(50% - 5px);max-width:170px}
 .cats{padding-bottom:80px}
 .stmt{padding-bottom:40px}
 .stage{margin-top:40px}
 .stage .on{max-width:80%;border-radius:10px}
 .qg{grid-template-columns:1fr}
 .q{padding:30px}
 .qs{padding-bottom:100px}
 .cta-in{padding:80px 20px}
 .wl{gap:10px}
 .wl span{height:var(--tm)}
 .wl img{border-radius:8px}
 .strip{height:700px}
 .plans{padding-top:60px}
 .pc{flex-direction:column;gap:32px}
 .plan{flex:none;width:100%;padding:32px 24px 28px;min-height:500px}
 .short .plan,.short .plan.ft{min-height:0}
 .stg::before{height:100%}
 .pn{margin-top:40px}
 .fl{flex-direction:column}
 .fc{width:100%;flex:none}
 .end{padding-top:80px}
 .dock{display:grid;grid-template-columns:1fr 1fr;width:100%}
 .dock div{padding:14px 16px}
 .dock dt{font-size:26px;line-height:32px}
 .dock dd{max-width:none}
 .ft .wrap{width:calc(100% - 80px)}
 .fcn{flex-direction:column}
 .fb{flex:none;width:100%}
 .fls{flex-direction:column;width:100%}
 .fls ul{flex:none}
 .fbt{padding-top:140px}
 .fbt .wrap{width:100%}
 .fbt .f2{height:146px}
}
@media (prefers-reduced-motion:reduce){
 html{scroll-behavior:auto}
 *,*::before,*::after{animation:none!important;transition:none!important}
 .js [data-rv]{opacity:1;transform:none}
 .sv,.bv{overflow-x:auto}
}
'''

JS = r'''
(function(){
var R=document.documentElement,still=matchMedia('(prefers-reduced-motion:reduce)').matches;
try{
/* FAQ: the answer opens over 450ms */
document.querySelectorAll('.fq').forEach(function(q){var s=q.querySelector('summary');if(!s||still||!q.animate)return;
 s.addEventListener('click',function(ev){ev.preventDefault();var a=q.offsetHeight,opening=!q.open;if(opening)q.open=true;
  var b=opening?q.offsetHeight:s.offsetHeight;if(!opening)q.style.paddingBottom='0px';
  var an=q.animate({height:[a+'px',b+'px']},{duration:450,easing:'cubic-bezier(.16,1,.3,1)'});
  an.onfinish=an.oncancel=function(){if(!opening)q.open=false;q.style.paddingBottom='';};});});
if(still||!window.requestAnimationFrame)return;
R.classList.add('js');
/* cards come in once their top is 12% above the bottom edge; anything already passed is shown too */
var rv=[].slice.call(document.querySelectorAll('[data-rv]')),rt=0;
var show=function(){rt=0;var lim=innerHeight*.88;rv=rv.filter(function(n){if(n.getBoundingClientRect().top<lim){n.classList.add('in');return false;}return true;});};
var want=function(){if(!rt&&rv.length)rt=requestAnimationFrame(show);};
addEventListener('scroll',want,{passive:true});addEventListener('resize',want);addEventListener('load',want);show();
/* the wall: pinned; 2x -> 1x while it clears, then folds to a tenth into the icon */
var sec=document.querySelector('[data-wall]');
if(sec){var wl=sec.querySelector('.wl'),ai=sec.querySelector('.ai'),sc=sec.querySelector('.cta-s'),tick=0;
 var cl=function(v){return v<0?0:v>1?1:v;};
 var draw=function(){tick=0;var vh=innerHeight,fh=Math.max(vh,880);R.style.setProperty('--fh',fh+'px');
  var top=sc.getBoundingClientRect().top,travel=sc.offsetHeight-fh,y=-top;
  var p1=cl((y+vh)/(vh+travel*.79)),p2=cl((y-travel*.79)/(travel*.33));
  if(wl){var s=p2>0?1-.9*p2:2-p1,o=p2>0?1-p2:p1;wl.style.transform='translateY('+(p2>0?0:(1-p1)*490*Math.min(1,vh/900))+'px) scale('+s+')';wl.style.opacity=o;}
  if(ai){var p3=cl((y+vh*.9)/(vh*.9+travel*1.086));ai.style.transform='translateY('+(1-p3)*300+'px) scale('+(1.5-.5*p3)+')';ai.style.opacity=p3;}};
 var ask=function(){if(!tick)tick=requestAnimationFrame(draw);};
 addEventListener('scroll',ask,{passive:true});addEventListener('resize',ask);draw();}
}catch(err){R.classList.remove('js');}
})();
'''


def render(d: dict) -> str:
    c = colours(d.get('palette') or {})
    b = d.get('brand') or {}
    h = d.get('hero') or {}
    used, upic = set(), set()
    hero = s_hero(d, c, used, upic)
    feat = s_features(d, c, used)
    cards = s_cards(d, c, used)
    stmt = s_statement(d, c, used, upic)
    body = (s_header(d, c) + '<main id="main">' + hero + feat + s_quote(d, c) + cards + stmt + s_quotes(d, c)
            + s_wall(d, c) + s_strip(d, c, used) + s_plans(d, c) + s_faq(d, c) + s_close(d, c) + '</main>' + s_foot(d, c, upic))
    v = (f':root{{--G:{c["G"]};--I:{c["I"]};--A:{c["A"]};--onA:{c["onA"]};--S:{c["S"]};--F:{c["F"]};--Fa:{rgba(c["F"], .8)};'
         f'--D:{c["D"]};--oD:{c["oD"]};--mut:{c["mut"]};--mutD:{c["mutD"]};--nav:{c["nav"]};--band:{c["band"]};'
         f'--Ag:{rgba(c["A"], .35)};--Ag2:{rgba(c["A"], .55)};--hl:{rgba("#ffffff", .08 if c["dark"] else 1)};'
         f'--pl:{rgba("#ffffff", .08 if c["dark"] else .8)};--G0:{rgba(c["G"], 0)};--G55:{rgba(c["G"], .55)};--oD1:{rgba(c["oD"], .1)};--wq:{c["wq"]};'
         f'--fh:max(100vh,880px);--spring:{SPRING}}}')
    title = ' — '.join(x for x in (b.get('name'), h.get('title')) if x)
    desc = h.get('text') or h.get('text2') or ''
    return ('<!doctype html><html lang="%s"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>%s</title>%s<meta name="theme-color" content="%s">'
            '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,400..700&display=swap" rel="stylesheet">'
            '<style>%s%s</style></head><body><a class="skip" href="#main">Skip to content</a>%s<script>%s</script></body></html>') % (
        e(d.get('lang') or 'en'), e(title), f'<meta name="description" content="{e(desc)}">' if desc else '', c['G'], v, CSS, body, JS)
