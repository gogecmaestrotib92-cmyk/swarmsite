"""writer — reference template (home page build measured on writer.com, 2026-11-12; plan columns measured on its plans page).
render(d) -> one self-contained HTML page. Pure function: no client, no model call, nothing fetched.
Everything here is a measure or a behaviour; no word, picture, icon, logo or file of the reference is in it.
Face: Poppins (SIL OFL, Google Fonts) — the reference's own home-page face is this open one, so no stand-in was needed."""
from html import escape as e

# The reference opens on a made picture (a nebula / star field) and repeats that one motif down the page: the same
# star field in its step cards and behind its team section. So this template's motif is `sky`: the opening, the picture
# side of every step panel (another crop, held dim) and the features backdrop are `media.made.sky`; the quiet grounds
# (the figure cards) are `media.made.field` in the page's own tone. No `blur` hue, no `land`, no `sheet`.
# Where a kind is absent the slot is the plain palette ground — never a gradient standing in for a picture.

UI = {'en': ('Previous', 'Next', 'Menu'), 'sr': ('Prethodno', 'Sledeće', 'Meni'), 'sl': ('Nazaj', 'Naprej', 'Meni'), 'de': ('Zurück', 'Weiter', 'Menü')}


# ---------- colour: relations of the reference, the client's palette ----------
def _dark_page(d):
    g = ((d.get('palette') or {}).get('ground') or '#ffffff').lstrip('#')
    try: r, gg, b = (int(g[i:i + 2], 16) for i in (0, 2, 4))
    except Exception: return False
    return (0.2126 * r + 0.7152 * gg + 0.0722 * b) / 255 < .45
def _fit_page(pics, d):
    """On a dark page a large ground never takes a light picture (one bright panel in a dark page reads as a fault);
    when every picture is light the list is kept as it is."""
    if not _dark_page(d): return pics
    keep = [p for p in pics if p.get('tone') != 'light']
    return keep or pics

def _rgb(h):
    h = h.lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _hex(c):
    return '#%02x%02x%02x' % tuple(max(0, min(255, round(v))) for v in c)


def mix(a, b, t):
    """a moved t of the way towards b"""
    a, b = _rgb(a), _rgb(b)
    return _hex(tuple(a[i] + (b[i] - a[i]) * t for i in range(3)))


def rgba(h, a):
    r, g, b = _rgb(h)
    return f'rgba({r},{g},{b},{a})'


def _lum(h):
    def f(v):
        v /= 255
        return v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4
    r, g, b = _rgb(h)
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b)


def contrast(a, b):
    la, lb = _lum(a), _lum(b)
    return (max(la, lb) + .05) / (min(la, lb) + .05)


def toned(ink, ground, t, against, floor=4.6):
    """ink faded t towards the ground (the reference's greys), pulled back until it still reads on `against`"""
    while t > 0 and min(contrast(mix(ink, ground, t), s) for s in against) < floor:
        t -= .02
    return mix(ink, ground, max(t, 0))


def on(bg, a, b):
    return a if contrast(a, bg) >= contrast(b, bg) else b


def colours(p):
    g, ink, acc = p.get('ground', '#000000'), p.get('ink', '#ffffff'), p.get('accent', '#5551ff')
    extra = [x for x in p.get('extra', []) if x.lower() not in (g.lower(), ink.lower())] or [acc]
    c = {'g': g, 'ink': ink, 'acc': acc}
    c['alt'] = mix(g, ink, .035)        # reference: #09090b on #000
    c['card'] = mix(g, ink, .105)       # #1b1b1d
    c['panel'] = mix(g, ink, .095)      # #18181b
    c['line'] = mix(g, ink, .155)       # #27272a
    c['rule'] = mix(g, ink, .25)        # #3f3f46
    c['dot'] = mix(g, ink, .29)         # #4b4b52
    c['tint'] = mix(g, ink, .06)        # plan column, neutral
    c['tint2'] = mix(g, acc, .16)       # plan column, marked
    grounds = [g, c['alt'], c['card'], c['panel'], c['tint'], c['tint2']]
    c['soft'] = toned(ink, g, .10, grounds)    # #e4e7ed
    c['mute'] = toned(ink, g, .20, grounds)    # #ccccd1
    c['label'] = toned(ink, g, .37, grounds)   # #a1a1aa
    c['foot'] = toned(ink, g, .26, [g])        # #bdbdbd
    c['on_acc'] = on(acc, ink, g)
    c['acc_h'] = mix(acc, '#000000', .16)      # #5551ff -> #2e2ae8
    c['on_acc_h'] = on(c['acc_h'], ink, g)
    c['grey'] = mix(ink, g, .49)               # hover of the light closing button (#828282)
    c['on_grey'] = on(c['grey'], ink, g)
    c['hot'] = toned(mix(ink, acc, .16), g, 0, [g])  # link hover (#d6deff)
    c['x0'], c['x1'] = extra[0], extra[1 % len(extra)]
    return c


# ---------- small builders ----------
def M(path):
    return '../../' + path


def a(link, cls, inner=None):
    if not link or not link.get('t'):
        return ''
    return f'<a class="{cls}" href="{e(link.get("h") or "#")}">{inner if inner is not None else e(link["t"])}</a>'


def img(m, cls='', lazy=True):
    return (f'<img class="{cls}" src="{e(M(m["src"]))}" width="{m.get("w", "")}" height="{m.get("h", "")}" alt="{e(m.get("alt", ""))}"'
            f'{" loading=lazy decoding=async" if lazy else ""}>')


def made(d, kind):
    return ((d.get('media') or {}).get('made') or {}).get(kind)


def ground(m, slot, cls, lazy=True, style=''):
    """a made picture used as a ground: decorative, sized, never the subject"""
    return (f'<img class="{cls}" data-slot="{slot}" src="{e(M(m["src"]))}" width="{m.get("w", "")}" height="{m.get("h", "")}" alt="" aria-hidden="true"'
            f'{" loading=lazy" if lazy else ""} decoding=async{(" style=" + chr(34) + style + chr(34)) if style else ""}>')


def fields(d):
    """the quiet grounds in the page's own tone (a dark page takes dark fields, a light page light ones); may be empty"""
    want = 'dark' if _dark_page(d) else 'light'
    return [f for f in made(d, 'field') or [] if isinstance(f, dict) and f.get('src') and f.get('tone', want) == want]


# three crops of the sky for the step panels: the picture is set half as large again as the picture side and moved, so
# each card shows another part of it — the lower, quieter parts first (left, top in % of the picture side)
CROPS = ((-25, -50), (0, -22), (-50, -22))


ARROW = '<svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><path d="M2.5 8h11M9 3.5 13.5 8 9 12.5" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def dots(n):
    if n < 2:
        return ''
    return '<div class="dots">' + ''.join(f'<button type="button" aria-label="{i + 1}"{" aria-current=true" if i == 0 else ""}></button>' for i in range(n)) + '</div>'


def head(title, text='', kicker='', centre=False, big=False):
    if not title:
        return ''
    k = f'<p class="eyebrow">{e(kicker)}</p>' if kicker else ''
    t = f'<p class="lede{" lede-l" if big else ""}">{e(text)}</p>' if text else ''
    return f'<div class="title{" c" if centre else ""}">{k}<h2>{e(title)}</h2>{t}</div>'


# ---------- sections ----------
def s_header(d, ui):
    b = d.get('brand', {})
    logo = ''
    if b.get('logo'):
        logo = f'<img src="{e(M(b["logo"]))}" alt="{e(b.get("name", "")) if b.get("logo_wordmark") else ""}" class="{"wm" if b.get("logo_wordmark") else "mk"}">'
    name = '' if b.get('logo_wordmark') and b.get('logo') else f'<span>{e(b.get("name", ""))}</span>'
    nav = ''.join(f'<li>{a(n, "")}</li>' for n in d.get('nav', []) if n.get('t'))
    sign = f'<li>{a(d.get("signin"), "")}</li>' if d.get('signin') else ''
    cta = a(d.get('cta'), 'btn btn-s')
    return f'''<header class="hd" id="hd"><div class="hd-in">
<a class="logo" href="{e(b.get("home") or "#")}" aria-label="{e(b.get("name", ""))}">{logo}{name}</a>
<div class="hd-r"><nav class="menu" id="menu"><ul>{nav}{sign}</ul>{cta}</nav>
{a(d.get("cta"), "hd-cta")}<button class="burger" id="burger" type="button" aria-label="{e(ui[2])}" aria-expanded="false" aria-controls="menu"><i></i><i></i><i></i></button></div>
</div></header>'''


def s_hero(d):
    h = dict(d.get('hero') or {})
    h['title'] = h.get('title') or (d.get('brand') or {}).get('name')  # the page's one heading: the title, else the name
    if not h.get('title'):
        return ''
    ps = ''.join(f'<p>{e(t)}</p>' for t in (h.get('text'), h.get('text2')) if t)
    pri, sec = a(h.get('primary') or d.get('cta'), 'btn btn-h'), a(h.get('secondary'), 'btn btn-o btn-h2')
    row = f'<div class="go">{pri}{sec}</div>' if pri else ''
    sky = made(d, 'sky')
    sky = ground(sky, 'sky', 'sky', lazy=False) if sky and sky.get('src') else ''
    return f'<section class="hero{" has-sky" if sky else ""}">{sky}<div class="wrap"><div class="hero-copy"><h1>{e(h["title"])}</h1>{ps}{row}</div></div></section>'


def s_trust(d):
    logos, trust = d.get('logos') or [], d.get('trust') or []
    if logos:
        items = ''.join(img(l, 'lg') if isinstance(l, dict) and l.get('src') else f'<span>{e(l if isinstance(l, str) else l.get("name", ""))}</span>' for l in logos)
    elif trust:
        items = ''.join(f'<span>{e(t)}</span>' for t in trust)
    else:
        return ''
    note = (d.get('hero') or {}).get('note')
    lab = f'<p class="trust-l">{e(note)}</p>' if note else ''
    return f'<section class="trust"><div class="wrap">{lab}<div class="mq" data-mq><div class="mq-t"><div class="mq-g">{items}</div></div></div></div></section>'


def s_steps(d, col):
    s = d.get('steps') or {}
    items = [i for i in s.get('items', []) if i.get('title')]
    if not items:
        return ''
    sizes = {m['src']: m for k in ('screens', 'phones', 'photos') for m in (d.get('media') or {}).get(k, [])}
    slides = ''
    sky = _fit_page([x for x in [made(d, 'sky')] if isinstance(x, dict) and x.get('src')], d)
    sky = sky[0] if sky else None
    for n, i in enumerate(items):
        # as on the reference: the picture side of the card carries the opening's own picture again, in another crop and
        # held dim; the text side is the plain panel ground, so no text lies on a picture
        pic, cls, style = '', '', ''
        shot = ''
        if i.get('img'):
            m = sizes.get(i['img'], {'src': i['img']})
            tall = i.get('shape') in ('phone', 'book', 'portrait') or (m.get('h', 0) > m.get('w', 1))
            if sky:
                x, y = CROPS[n % len(CROPS)]
                pic, cls = f'<span class="pgw">{ground(sky, "panel-sky", "pg", style=f"left:{x}%;top:{y}%")}</span>', ' pic'
            shot = f'<div class="shot{" tall" if tall else ""}">{pic}{img({**m, "alt": m.get("alt", i.get("title", ""))})}</div>'
        k = f'<p class="k">{e(i["k"])}</p>' if i.get('k') else ''
        t = f'<p>{e(i["text"])}</p>' if i.get('text') else ''
        c = a(i.get('cta'), 'btn btn-o', e(i['cta']['t']) + ' <span aria-hidden="true">→</span>') if i.get('cta') else ''
        slides += f'<div class="slide"><article class="panel{"" if shot else " bare"}{cls}"{style}>{shot}<div class="copy">{k}<h3>{e(i["title"])}</h3>{t}{c}</div></article></div>'
    kick = (d.get('hero') or {}).get('kicker', '')
    return f'''<section class="band alt steps"><div class="wrap">{head(s.get("title"), s.get("text"), kick, big=True)}
<div class="sl" data-slider data-auto="8000"><div class="sl-t">{slides}</div></div>{dots(len(items))}</div></section>'''


def s_figures(d, ui):
    figs = [f for f in d.get('figures') or [] if f.get('v')]
    fl = fields(d)
    total = len(figs) + len(d.get('quotes') or [])
    def fg(k):
        # one quiet field runs behind the whole row: each card shows the next slice of it
        if not fl:
            return ''
        return f'<span class="fgw">{ground(fl[0], "figure-field", "fg", style=f"left:{-150 * k / max(1, total - 1):.1f}%")}</span>'
    cards = ''.join(f'<div class="slide"><div class="fig">{fg(k)}<p class="v">{e(f["v"])}</p><p class="l">{e(f.get("l", ""))}</p></div></div>' for k, f in enumerate(figs))
    k = len(figs) - 1
    for q in d.get('quotes') or []:
        k += 1
        if isinstance(q, str):
            q = {'q': q}
        text = q.get('q') or q.get('text') or q.get('quote')
        if not text:
            continue
        by = ''.join(f'<span>{e(q[k])}</span>' for k in ('name', 'by', 'role') if q.get(k))
        cards += f'<div class="slide"><figure class="fig quote">{fg(k)}<blockquote>{e(text)}</blockquote>{f"<figcaption>{by}</figcaption>" if by else ""}</figure></div>'
    if not cards:
        return ''
    return f'''<section class="band figs" data-rail><div class="sl rail" data-slider><div class="sl-t">{cards}</div></div>
<div class="arrows"><button type="button" class="prev" aria-label="{e(ui[0])}">{ARROW}</button><button type="button" class="next" aria-label="{e(ui[1])}">{ARROW}</button></div></section>'''


def s_features(d, used):
    f = d.get('features') or {}
    items = [i for i in f.get('items', []) if i.get('t')]
    if not items and not f.get('title'):
        return ''
    md = d.get('media') or {}
    slides = ''
    n = 0
    first = None   # the first thing shown; its proportion decides where the backdrop starts
    v = md.get('video')
    if v and v.get('src'):
        first = v
        slides += (f'<div class="slide"><figure class="scr"><video src="{e(M(v["src"]))}" poster="{e(M(v.get("poster", "")))}" width="{v.get("w", "")}" height="{v.get("h", "")}" '
                   f'muted loop playsinline preload="metadata" data-play aria-label="{e(v.get("alt", ""))}"></video><figcaption>{e(v.get("alt", ""))}</figcaption></figure></div>')
        n += 1
    for m in md.get('screens', []):
        if m['src'] in used:
            continue
        first = first or m
        slides += f'<div class="slide"><figure class="scr">{img(m)}<figcaption>{e(m.get("alt", ""))}</figcaption></figure></div>'
        n += 1
    show = f'<div class="show"><div class="sl" data-slider data-auto="8000"><div class="sl-t">{slides}</div></div>{dots(n)}</div>' if n else ''
    cards = ''.join(f'<div class="fc"><h3>{e(i["t"])}</h3>{"<p>" + e(i["d"]) + "</p>" if i.get("d") else ""}</div>' for i in items)
    grid = f'<div class="fgrid{" odd" if len(items) % 2 else ""}">{cards}</div>' if cards else ''
    sky = _fit_page([x for x in [made(d, 'sky')] if isinstance(x, dict) and x.get('src')], d)
    # a screen as wide as the picture would hide it: then the picture starts under the caption and dots and
    # shows round the cards, as the reference's does round its cards; no text lies on it
    r = (first.get('w') or 0) / (first.get('h') or 1) if first else 0
    ft = f'--ft:calc(min(954px,100vw - 30px)/{r:.3f} + 76px)' if r >= 1.4 else ''
    bk = ground(sky[0], 'features-sky', 'fbk', style=ft) if sky and (show or grid) else ''
    stage = f'<div class="fstage">{bk}{show}{grid}</div>' if (show or grid) else ''
    return f'<section class="band feats"><div class="wrap">{head(f.get("title"), f.get("text"), centre=True)}{stage}</div></section>'


def s_statement(d, used):
    s = d.get('statement') or {}
    if not s.get('title'):
        return ''
    scr = next((m for m in (d.get('media') or {}).get('screens', []) if m.get('src')), None)
    vis = ''
    if scr:
        used.add(scr['src'])
        vis = f'<div class="vis">{img(scr)}</div>'
    btn = a(d.get('cta'), 'btn btn-a', e(d['cta']['t']) + ' <span aria-hidden="true">→</span>') if d.get('cta') else ''
    return f'<section class="band adv"><div class="wrap">{head(s["title"], s.get("text"))}{f"<div class=acts>{btn}</div>" if btn else ""}{vis}</div></section>'


def s_plans(d):
    p = d.get('plans') or {}
    items = [i for i in p.get('items', []) if i.get('name')]
    if not items:
        return ''
    cols = ''
    for i in items:
        line = f'<p class="pl-line">{e(i.get("line") or "")}</p>'
        price = f'<p class="pl-price">{"<b>" + e(i["price"]) + "</b>" if i.get("price") else ""}{"<span>" + e(i["per"]) + "</span>" if i.get("per") else ""}</p>'
        rows = ''.join(f'<li>{e(r)}</li>' for r in i.get('rows') or [])
        cols += (f'<div class="pl{" marked" if i.get("marked") else ""}"><h3>{e(i["name"])}</h3>{line}{price}<div class="pl-b">{a(i.get("cta"), "btn btn-p")}</div>'
                 f'<ul>{rows}</ul></div>')
    note = f'<p class="pl-note">{e(p["note"])}</p>' if p.get('note') else ''
    return f'<section class="band alt plans"><div class="wrap">{head(p.get("title"), p.get("text"), centre=True)}<div class="pls n{min(len(items), 3)}">{cols}</div>{note}</div></section>'


def s_faq(d):
    f = d.get('faq') or {}
    items = [i for i in f.get('items', []) if i.get('q') and i.get('a')]
    if not items:
        return ''
    cards = ''.join(f'<div class="qc"><h3>{e(i["q"])}</h3><p>{e(i["a"])}</p></div>' for i in items)
    n = 3 if len(items) % 3 == 0 else (2 if len(items) > 1 else 1)
    return f'<section class="band alt faq"><div class="wrap">{head(f.get("title"), centre=True)}<div class="qgrid c{n}">{cards}</div></div></section>'


def s_links(d):
    links = [l for l in d.get('links') or [] if l.get('t')]
    if not links:
        return ''
    def item(l):
        return (f'<a class="res" href="{e(l.get("h") or "#")}"><h3>{e(l["t"])} <span aria-hidden="true">→</span></h3>'
                f'{"<p>" + e(l["d"]) + "</p>" if l.get("d") else ""}</a>')
    half = (len(links) + 1) // 2
    left, right = ''.join(map(item, links[:half])), ''.join(map(item, links[half:]))
    two = f'<i class="divider" data-seen aria-hidden="true"></i><div class="rcol">{right}</div>' if right else ''
    return f'<section class="band resources"><div class="wrap"><div class="rs"><div class="rcol">{left}</div>{two}</div></div></section>'


def s_close(d):
    c = d.get('close') or {}
    if not c.get('title'):
        return ''
    t = f'<p>{e(c["text"])}</p>' if c.get('text') else ''
    b1, b2 = a(c.get('cta') or d.get('cta'), 'btn btn-c1'), a((d.get('hero') or {}).get('secondary'), 'btn btn-c2')
    return f'<section class="close"><div class="close-in"><h2>{e(c["title"])}</h2>{t}<div class="close-b">{b1}{b2}</div></div></section>'


def s_footer(d):
    b, f = d.get('brand', {}), d.get('foot') or {}
    logo = f'<img src="{e(M(b["logo"]))}" alt="" class="{"wm" if b.get("logo_wordmark") else "mk"}" loading="lazy">' if b.get('logo') else f'<b>{e(b.get("name", ""))}</b>'
    cols = [d.get('nav') or [], [x for x in (d.get('signin'), d.get('cta')) if x], [{'t': l['t'], 'h': l.get('h')} for l in d.get('links') or []]]
    lists = ''.join('<ul>' + ''.join(f'<li>{a(l, "")}</li>' for l in c if l.get('t')) + '</ul>' for c in cols if c)
    mid = f'<div class="ft-mid"><p>{e(f["text"])}</p></div>' if f.get('text') else '<div class="ft-mid none"></div>'
    fl = '<span aria-hidden="true">|</span>'.join(a(l, '') for l in f.get('links') or [] if l.get('t'))
    return f'''<footer class="ft"><div class="wrap"><div class="ft-top"><div class="ft-logo">{logo}</div><div class="ft-lists">{lists}</div></div>
{mid}<div class="ft-bot"><p class="legal">{e(f.get("legal", ""))}</p>{f'<p class="ft-l">{fl}</p>' if fl else ""}</div></div></footer>'''


# ---------- the page ----------
def css(c):
    return f'''
*,*::before,*::after{{box-sizing:border-box}}
html{{-webkit-text-size-adjust:100%;overflow-x:clip}}
body{{margin:0;background:{c['g']};color:{c['ink']};font:400 16px/1.6 Poppins,system-ui,-apple-system,"Segoe UI",sans-serif;-webkit-font-smoothing:antialiased;overflow-x:clip}}
h1,h2,h3,p,ul,figure,blockquote{{margin:0;padding:0}}ul{{list-style:none}}
a{{color:inherit;text-decoration:none}}img,video{{display:block;max-width:100%;height:auto}}
button{{font:inherit;color:inherit;background:none;border:0;padding:0;cursor:pointer}}
:focus-visible{{outline:2px solid {c['ink']};outline-offset:3px;border-radius:4px}}
.btn:focus-visible,.arrows button:focus-visible,.dots button:focus-visible{{border-radius:82px}}
.wrap{{max-width:1080px;margin:0 auto;padding:0 15px}}
.band{{padding:90px 0;background:{c['g']}}}.band.alt{{background:{c['alt']}}}
/* buttons: pills; the fill darkens in .2s, nothing moves */
.btn{{display:inline-flex;align-items:center;justify-content:center;gap:.3em;border-radius:60px;font-weight:500;font-size:16px;line-height:1.6;padding:10px 24px;border:1px solid transparent;transition:background-color .2s,border-color .2s,color .2s;text-align:center}}
.btn-s{{font-size:14px;font-weight:600;line-height:1.5;padding:10px 17px;border-width:2px;border-radius:82px;background:{c['acc']};border-color:{c['acc']};color:{c['on_acc']};white-space:nowrap}}
.btn-a,.btn-h{{background:{c['acc']};color:{c['on_acc']}}}
.btn-s:hover,.btn-a:hover,.btn-h:hover{{background:{c['acc_h']};border-color:{c['acc_h']};color:{c['on_acc_h']}}}
.btn-o{{border-color:{c['soft']};color:{c['ink']}}}.btn-o:hover{{background:{c['acc_h']};border-color:{c['acc_h']};color:{c['on_acc_h']}}}
/* header: lies on the page at the top; past its own height it is pinned and drops in from above in .4s */
.hd{{position:absolute;top:0;left:0;right:0;z-index:50;transition:background-color .4s}}
.hd.pin{{position:fixed;background:{c['g']};animation:drop .4s ease}}
@keyframes drop{{from{{top:-100%}}to{{top:0}}}}
.hd-in{{height:83px;padding:0 25px;display:flex;align-items:center;justify-content:space-between;gap:24px}}
.logo{{display:flex;align-items:center;gap:10px;font-weight:600;font-size:18px;letter-spacing:-.01em;white-space:nowrap;flex:none}}
.logo .mk{{width:auto;height:auto;max-width:140px;max-height:35px}}.logo .wm{{height:26px;width:auto}}
.hd-r{{display:flex;align-items:center;justify-content:flex-end;flex:1;min-width:0}}.menu{{display:flex;align-items:center}}.menu ul{{display:flex;align-items:center}}
.menu ul a{{display:flex;align-items:center;height:83px;padding:0 15px;font-size:14px;font-weight:600;line-height:1.5;white-space:nowrap}}
.menu .btn-s{{margin-left:15px}}.hd-cta,.burger{{display:none}}
/* opening */
.hero{{position:relative;padding:180px 0 100px;overflow:hidden}}
/* the opening picture: a strip at the top edge whose sides and lower edge are masked away in a downward arc, so it has no edge on any ground */
.sky{{position:absolute;top:0;left:50%;width:min(1321px,92vw);max-width:none;height:258px;transform:translateX(-50%);object-fit:cover;object-position:50% 0;pointer-events:none;user-select:none;
-webkit-mask-image:radial-gradient(ellipse 50% 100% at 50% 0,#000 45%,transparent 100%),linear-gradient(rgba(0,0,0,.24) 62px,#000 140px);mask-image:radial-gradient(ellipse 50% 100% at 50% 0,#000 45%,transparent 100%),linear-gradient(rgba(0,0,0,.24) 62px,#000 140px);
-webkit-mask-composite:source-in;mask-composite:intersect}}
.hero-copy{{position:relative;max-width:700px;margin:0 auto;display:flex;flex-direction:column;align-items:center;text-align:center}}
h1{{font-size:64px;line-height:1;font-weight:500;letter-spacing:-.02em;text-wrap:balance}}
.hero-copy p{{max-width:470px;text-wrap:balance}}.hero-copy h1+p{{margin-top:16px}}
.go{{margin-top:26px;display:flex;flex-wrap:wrap;justify-content:center;gap:12px;max-width:100%}}
.btn-h,.btn-h2{{min-height:54px;padding:8px 28px;border-radius:50px;line-height:1.15}}
/* the running row: 60px a second, linear, stops under the pointer */
.trust{{padding-bottom:0}}.trust-l{{text-align:center;line-height:1.6}}
.mq{{height:100px;margin:0 15px;overflow:hidden;display:flex;align-items:center;-webkit-mask-image:linear-gradient(90deg,transparent,#000 12%,#000 88%,transparent);mask-image:linear-gradient(90deg,transparent,#000 12%,#000 88%,transparent)}}
.mq-t{{display:flex;flex:none;margin:0 auto}}.mq-g{{display:flex;align-items:center;flex:none}}
.mq-g>*{{flex:none;margin:0 28px;white-space:nowrap;font-size:18px;font-weight:500;letter-spacing:-.01em}}.mq-g .lg{{height:28px;width:auto}}
.mq.run .mq-t{{margin:0;animation:mq var(--mq,30s) linear infinite}}.mq.run:hover .mq-t{{animation-play-state:paused}}
@keyframes mq{{to{{transform:translateX(-50%)}}}}
/* section titles */
.eyebrow{{font-size:16px;font-weight:600;letter-spacing:3px;text-transform:uppercase;line-height:25px}}
h2{{font-size:40px;line-height:1.15;font-weight:500;letter-spacing:-.02em;max-width:707px;text-wrap:balance}}
.title .eyebrow+h2{{margin-top:16px}}
.lede{{margin-top:16px;max-width:673px;color:{c['soft']}}}.lede-l{{font-size:20px;color:{c['mute']}}}
.title.c{{text-align:center}}.title.c h2,.title.c .lede{{margin-left:auto;margin-right:auto}}
/* sliders: one panel a view, .6s ease, the next one every 8s, dragged by hand */
.sl{{overflow:hidden;touch-action:pan-y}}.sl-t{{display:flex;transition:transform .6s ease;will-change:transform}}.sl.drag .sl-t{{transition:none}}.sl[data-slider]{{cursor:grab}}.sl.drag{{cursor:grabbing}}
.slide{{flex:0 0 100%;margin-right:16px;min-width:0}}.slide:last-child{{margin-right:0}}
.sl img,.sl video{{-webkit-user-drag:none;user-select:none}}
.dots{{display:flex;justify-content:center;gap:17px;margin-top:20px}}
.dots button{{width:14px;height:14px;border-radius:50%;background:{c['dot']};transition:background-color .2s}}.dots button[aria-current]{{background:{c['ink']}}}
.steps .sl{{margin-top:60px}}
.panel{{position:relative;display:flex;min-height:427px;height:100%;border-radius:32px;border:1px solid {c['line']};background:{c['panel']};overflow:hidden}}
/* a panel with a made picture: the picture side (behind the screen) carries the sky again, dim, in its own crop, and
   dissolves toward the text side; the text side is the plain panel */
.shot{{position:relative}}.shot>img{{position:relative;z-index:1}}
.pgw{{position:absolute;inset:0;overflow:hidden;pointer-events:none;-webkit-mask-image:linear-gradient(90deg,#000 72%,transparent);mask-image:linear-gradient(90deg,#000 72%,transparent)}}
.pg{{position:absolute;width:150%;height:150%;max-width:none;object-fit:cover;opacity:.62}}
.shot{{flex:0 0 59.1%;display:flex;align-items:center;justify-content:center;padding:32px 40px;min-width:0}}
.shot>img{{width:auto;max-height:363px;border-radius:10px;box-shadow:0 18px 50px {rgba('#000000', .28)}}}
.shot.tall>img{{max-height:460px;border-radius:14px}}
.copy{{flex:1;align-self:center;padding:32px 35px 32px 30px;min-width:0}}.panel.bare .copy{{padding:48px;max-width:707px}}
.copy .k{{font-weight:500;color:{c['label']}}}
h3{{font-weight:500}}.copy h3{{font-size:32px;line-height:1.15;letter-spacing:-.02em;margin-top:15px;text-wrap:balance}}.copy .k+h3{{margin-top:15px}}.copy h3:first-child{{margin-top:0}}
.copy h3+p{{margin-top:9px;color:{c['mute']}}}.copy .btn{{margin-top:24px}}
/* figures: a row that runs off the right edge, moved by the two round buttons */
.figs{{overflow:hidden}}.rail{{padding:0 56px}}.rail .slide{{flex:0 0 488px;margin-right:30px}}
.fig{{position:relative;overflow:hidden;height:332px;border-radius:12px;background:{c['card']};padding:28px 30px;display:flex;flex-direction:column}}
.fig>p,.fig>blockquote,.fig>figcaption{{position:relative}}
/* figure cards: one quiet field behind the row, each card the next slice of it */
.fgw{{position:absolute;inset:0;overflow:hidden;pointer-events:none}}.fg{{position:absolute;top:0;width:250%;height:100%;max-width:none;object-fit:cover;object-position:50% 78%}}
.fig .v{{font-size:64px;line-height:1;font-weight:500;letter-spacing:-.02em;white-space:nowrap}}.fig .l{{margin-top:auto;font-size:18px;line-height:1.35;max-width:300px;color:{c['soft']}}}
.fig blockquote{{font-size:20px;line-height:1.3;max-width:330px}}.fig figcaption{{margin-top:auto;display:flex;flex-direction:column;font-size:16px;line-height:1.4}}.fig figcaption span:first-child{{font-size:20px;font-weight:500}}
.arrows{{display:flex;gap:10px;padding-left:56px;margin-top:46px}}
.arrows button{{width:40px;height:40px;border-radius:50%;border:1px solid {c['ink']};display:flex;align-items:center;justify-content:center;opacity:.5;transition:background .2s,opacity .2s,color .2s}}
.arrows .prev svg{{transform:rotate(180deg)}}.arrows button:hover:not(:disabled){{background:{c['ink']};color:{c['g']};opacity:1}}.arrows button:disabled{{opacity:.35;cursor:default}}
/* features: title, the product shown whole, then the centred cards */
.fstage{{position:relative;margin-top:60px}}.fstage>.show,.fstage>.fgrid:first-child,.fstage>.fbk+.fgrid{{margin-top:0}}.fstage>.show,.fstage>.fgrid{{position:relative;z-index:1}}
/* the features backdrop: the sky again, 954 wide as measured, from under the title down behind the upper cards; no edge */
.fbk{{position:absolute;top:var(--ft,-60px);left:50%;transform:translateX(-50%);width:min(954px,100%);max-width:none;height:min(950px,100% - var(--ft,-60px));object-fit:cover;object-position:50% 0;pointer-events:none;
-webkit-mask-image:linear-gradient(transparent,#000 9%,#000 62%,transparent),linear-gradient(90deg,transparent,#000 14%,#000 86%,transparent);mask-image:linear-gradient(transparent,#000 9%,#000 62%,transparent),linear-gradient(90deg,transparent,#000 14%,#000 86%,transparent);-webkit-mask-composite:source-in;mask-composite:intersect}}
.show{{max-width:954px;margin:60px auto 0}}.show .slide{{margin-right:30px;display:flex;align-items:center;justify-content:center}}
.scr{{display:flex;flex-direction:column;align-items:center;max-width:100%}}.scr img,.scr video{{width:auto;max-height:600px;border-radius:16px}}
.scr figcaption{{margin-top:14px;font-weight:500;color:{c['label']};text-align:center}}
.fgrid{{display:grid;grid-template-columns:345px 345px;justify-content:center;gap:16px;margin-top:60px}}
.fc{{background:{c['card']};border-radius:16px;padding:50px 32px;text-align:center}}.fc h3{{font-size:24px;line-height:1.25;text-wrap:balance}}.fc p{{margin-top:16px;color:{c['soft']}}}
.fgrid.odd .fc:last-child{{grid-column:1/-1;justify-self:center;width:345px}}
/* statement */
.acts{{margin-top:48px}}.vis{{margin-top:31px;border-radius:16px;overflow:hidden}}.vis img{{width:100%}}
/* plans: two soft columns (measured on the reference's plans page) */
.pls{{display:grid;grid-template-columns:repeat(2,minmax(0,460px));justify-content:center;gap:24px;margin-top:51px}}.pls.n1{{grid-template-columns:minmax(0,460px)}}.pls.n3{{grid-template-columns:repeat(3,minmax(0,1fr))}}
.pl{{background:{c['tint']};border-radius:16px;padding:28px 40px 52px;display:grid;grid-row:span 5;grid-template-rows:subgrid;row-gap:0;align-content:start}}.pl>:empty{{margin:0!important;padding:0!important}}.pl.marked{{background:{c['tint2']}}}
.pl h3{{font-size:24px;line-height:36px;font-weight:600;letter-spacing:3px;text-transform:uppercase}}.pl-line{{margin-top:10px;line-height:24px}}
.pl-price{{margin-top:22px;color:{c['soft']};font-size:14px;line-height:20px}}.pl-price b{{display:block;font-size:40px;line-height:1.15;font-weight:500;letter-spacing:-.02em;color:{c['ink']}}}
.pl-b{{margin-top:30px}}.btn-p{{min-width:266px;max-width:100%;min-height:44px;padding:8px 20px;border-radius:82px;background:{c['ink']};color:{c['g']};font-weight:600;line-height:24px;border:0}}
.btn-p:hover{{background:{c['acc_h']};color:{c['on_acc_h']}}}
.pl ul{{margin-top:44px;padding-left:35px;display:grid;gap:12px;align-content:start}}.pl li{{position:relative;padding-left:27px;font-size:14px;line-height:20px}}
.pl li::before{{content:"";position:absolute;left:2px;top:4px;width:11px;height:6px;border-left:1.5px solid;border-bottom:1.5px solid;transform:rotate(-45deg)}}
.pl-note{{margin:28px auto 0;max-width:673px;text-align:center;font-size:14px;line-height:20px;color:{c['soft']}}}
/* answers: the reference's left-set cards, heading and paragraph */
.faq{{padding-top:0}}.plans+.faq{{padding-top:0}}.qgrid{{display:grid;gap:8px;margin-top:51px}}.qgrid.c3{{grid-template-columns:repeat(3,1fr)}}.qgrid.c2{{grid-template-columns:repeat(2,1fr)}}
.qc{{background:{c['card']};border-radius:16px;padding:32px}}.qc h3{{font-size:24px;line-height:1.25;text-wrap:balance}}.qc p{{margin-top:16px;color:{c['soft']}}}
/* onward links: two columns and a rule that draws itself top to bottom when seen */
.rs{{position:relative;display:flex;gap:28px;align-items:flex-start}}.rcol{{flex:1;display:flex;flex-direction:column;gap:30px;min-width:0}}
.res{{display:block;max-width:400px;transition:color .3s}}.res:hover{{color:{c['hot']}}}.res h3{{font-size:24px;line-height:1.2}}.res p{{margin-top:8px;font-size:12px;line-height:16px}}
.divider{{position:absolute;left:50%;top:0;bottom:0;width:1px;overflow:hidden}}
.divider::before,.divider::after{{content:"";position:absolute;inset:0;transform:scaleY(0);transform-origin:top}}.divider::before{{background:{c['ink']}}}.divider::after{{background:{c['rule']}}}
.divider.seen::before{{animation:draw 1.4s linear forwards}}.divider.seen::after{{animation:wipe 1.8s linear forwards}}
@keyframes draw{{0%{{transform:scaleY(0)}}84%,100%{{transform:scaleY(1)}}}}@keyframes wipe{{0%,50%{{transform:scaleY(0)}}100%{{transform:scaleY(1)}}}}
/* closing band */
.close{{background:{c['panel']}}}.close-in{{max-width:700px;margin:0 auto;padding:86px 15px 105px;display:flex;flex-direction:column;align-items:center;text-align:center}}
.close h2{{font-size:44px;line-height:55px;max-width:540px}}.close p{{margin-top:14px;max-width:540px;color:{c['mute']}}}
.close-b{{margin-top:36px;display:flex;flex-wrap:wrap;justify-content:center;gap:12px}}
.btn-c1,.btn-c2{{font-weight:600;line-height:20px;padding:20px 24px;border:0;transition:.3s ease-in-out}}
.btn-c1{{background:{c['g']};color:{c['ink']}}}.btn-c2{{background:{c['ink']};color:{c['g']}}}.btn-c2:hover{{background:{c['grey']};color:{c['on_grey']}}}
/* foot */
.ft-top{{display:flex;padding:80px 0}}.ft-logo{{flex:0 0 190px}}.ft-logo .mk{{width:auto;height:auto;max-width:190px;max-height:82px}}.ft-logo .wm{{height:26px;width:auto;max-width:none}}.ft-logo:has(.wm){{flex-basis:auto;margin-right:56px}}
.ft-lists{{flex:1;display:flex;justify-content:space-between;gap:24px}}.ft-lists a{{display:inline-block;padding:9px 0;line-height:19px;color:{c['foot']};transition:color .2s}}.ft-lists a:hover{{color:{c['ink']}}}
.ft-mid{{border-top:1px solid {c['line']};border-bottom:1px solid {c['line']};padding:35px 0}}.ft-mid.none{{padding:0;border-bottom:0}}.ft-mid p{{max-width:673px;font-size:14px;line-height:1.6;color:{c['foot']}}}
.ft-bot{{display:flex;justify-content:space-between;align-items:center;gap:24px;padding:54px 0}}
.legal,.ft-l{{font-size:14px;font-weight:600;text-transform:uppercase;line-height:21px}}.legal{{letter-spacing:4.2px}}.ft-l{{letter-spacing:3px;display:flex;gap:8px}}
@media (max-width:1100px){{.menu ul a{{padding:0 10px}}.rail{{padding:0 20px}}.arrows{{padding-left:20px}}}}
@media (max-width:900px){{
.hd-in{{height:76px;padding:0 24px}}.logo{{font-size:15px;gap:8px}}.logo .mk{{max-width:110px;max-height:25px}}.logo .wm{{height:20px}}
.hd-cta{{display:block;font-size:13.8px;font-weight:600;margin-right:14px;white-space:nowrap;padding:8px 6px;min-width:0;overflow:hidden;text-overflow:ellipsis}}.hd-cta.cut{{display:none}}
.burger{{flex:none}}
.burger{{display:block;position:relative;width:36px;height:36px}}.burger i{{position:absolute;left:6px;width:24px;height:2px;background:{c['ink']};transition:transform .3s,opacity .2s}}
.burger i:nth-child(1){{top:10px}}.burger i:nth-child(2){{top:17px}}.burger i:nth-child(3){{top:24px}}
.open .burger i:nth-child(1){{transform:translateY(7px) rotate(45deg)}}.open .burger i:nth-child(2){{opacity:0}}.open .burger i:nth-child(3){{transform:translateY(-7px) rotate(-45deg)}}
.hd.open{{position:fixed;background:{c['g']}}}
.menu{{position:fixed;top:76px;left:0;right:0;bottom:0;background:{c['ink']};color:{c['g']};flex-direction:column;align-items:flex-start;padding:30px;overflow:auto;transform:translateX(105%);transition:transform .3s,visibility .3s;visibility:hidden}}
.open .menu{{transform:none;visibility:visible}}.menu ul{{flex-direction:column;align-items:flex-start;width:100%}}.menu ul a{{height:51px;padding:0}}.menu .btn-s{{margin:16px 0 0}}
.menu :focus-visible{{outline-color:{c['g']}}}
.panel{{flex-direction:column;min-height:0}}.shot{{flex:none;padding:28px 24px 0}}.shot>img{{max-height:246px;box-shadow:0 11px 30px {rgba('#000000', .28)}}}.shot.tall>img{{max-height:340px}}
.copy{{align-self:stretch;padding:30px 25px}}.panel.pic .shot{{padding-bottom:28px}}.pgw{{-webkit-mask-image:linear-gradient(#000 70%,transparent);mask-image:linear-gradient(#000 70%,transparent)}}.panel.bare .copy{{padding:30px 25px}}.copy h3{{font-size:26px;margin-top:16px}}.copy h3+p{{margin-top:8px}}
.pls,.pls.n3{{grid-template-columns:minmax(0,460px)}}.qgrid.c3,.qgrid.c2{{grid-template-columns:1fr;gap:15px}}
}}
@media (max-width:760px){{
.band{{padding:50px 0}}.hero{{padding:100px 0 50px}}.sky{{height:max(124px,32vw);width:100%}}
h1{{font-size:40px;letter-spacing:-.015em}}h2{{font-size:36px;letter-spacing:-.022em}}
.go{{flex-direction:column;align-items:stretch;gap:10px;min-width:219px}}.btn-h,.btn-h2{{padding:15px 22px}}
.trust-l{{font-size:13px}}.mq{{margin:0}}.mq-g>*{{margin:0 20px;font-size:16px}}
.eyebrow{{font-size:14px;letter-spacing:1.6px;line-height:21px}}.lede-l{{font-size:16px}}
.steps .sl{{margin-top:40px}}
.rail{{padding:0 20px}}.rail .slide{{flex-basis:min(360px,calc(100vw - 30px));margin-right:16px}}.fig{{height:240px;padding:22px 22px}}.fig .v{{font-size:48px}}.fig .l{{font-size:16px;max-width:260px}}.arrows{{padding-left:20px;margin-top:47px}}
.fstage{{margin-top:40px}}.fbk{{top:var(--ft,-40px);height:min(420px,100% - var(--ft,-40px))}}.show{{margin-top:40px}}.show .slide{{margin-right:16px}}.scr img,.scr video{{max-height:420px;border-radius:12px}}.scr figcaption{{font-size:14px}}
.fgrid{{grid-template-columns:1fr;margin-top:40px}}.fc{{padding:32px 24px}}.fgrid.odd .fc:last-child{{width:auto;justify-self:stretch}}
.adv{{padding:40px 0 48px}}.acts{{margin-top:32px}}.vis{{margin-top:28px;border-radius:12px}}
.pls{{margin-top:36px}}.pl{{padding:30px 15px}}.pl ul{{padding-left:20px}}.btn-p{{min-width:0;width:100%}}
.qgrid{{margin-top:36px}}.qc{{padding:24px}}
.resources{{padding:48px 0}}.rs{{flex-direction:column;gap:36px}}.divider{{display:none}}.res{{max-width:none}}.res h3{{font-size:20px}}.rcol{{gap:36px}}
.close-in{{padding:86px 15px 105px}}
.ft .wrap{{padding:0 32px}}.ft-top{{flex-direction:column;padding:49px 0;gap:24px}}.ft-logo{{flex:none}}.ft-lists{{flex-wrap:wrap;justify-content:flex-start;gap:20px 0}}.ft-lists ul{{flex:0 0 50%}}
.ft-lists a{{font-size:13px;padding:6px 0;line-height:16px;min-height:28px}}.ft-mid{{padding:24px 0}}.ft-mid.none{{padding:0}}
.ft-bot{{flex-direction:column-reverse;gap:16px;padding:32px 0;text-align:center}}.legal,.ft-l{{font-size:11.4px;line-height:17px}}.legal{{letter-spacing:3.4px}}.ft-l{{flex-wrap:wrap;justify-content:center}}
}}
@media (prefers-reduced-motion:reduce){{
*,*::before,*::after{{animation:none!important;transition:none!important;scroll-behavior:auto!important}}
.mq .mq-t{{flex-wrap:wrap;justify-content:center;margin:0 auto}}.mq{{height:auto;min-height:100px;padding:20px 0;-webkit-mask-image:none;mask-image:none}}.mq-g{{flex-wrap:wrap;justify-content:center;row-gap:10px}}.mq-g[aria-hidden]{{display:none}}
.divider::before{{display:none}}.divider::after{{transform:none}}
}}
'''


JS = r'''
(function(){
var still=matchMedia('(prefers-reduced-motion: reduce)').matches,doc=document;
/* header: pinned once the page has moved past it */
var hd=doc.getElementById('hd'),bg=doc.getElementById('burger');
function pin(){hd.classList.toggle('pin',scrollY>90)}
addEventListener('scroll',pin,{passive:true});pin();
/* phone: the header's own button gives way when the name and the button do not both fit (it is in the menu too) */
var hc=doc.querySelector('.hd-cta');function fit(){if(!hc)return;hc.classList.remove('cut');if(hc.scrollWidth>hc.clientWidth+1)hc.classList.add('cut')}
fit();addEventListener('resize',fit);if(doc.fonts&&doc.fonts.ready)doc.fonts.ready.then(fit);
if(bg){bg.addEventListener('click',function(){var o=hd.classList.toggle('open');bg.setAttribute('aria-expanded',o);doc.documentElement.style.overflow=o?'hidden':''});
doc.getElementById('menu').addEventListener('click',function(ev){if(ev.target.closest('a')){hd.classList.remove('open');bg.setAttribute('aria-expanded',false);doc.documentElement.style.overflow=''}});
addEventListener('keydown',function(ev){if(ev.key==='Escape'&&hd.classList.contains('open'))bg.click()})}
/* running row: 60px a second whatever its length */
function mq(m){if(still||m.classList.contains('run'))return;var t=m.firstElementChild,g=t.firstElementChild,w=g.getBoundingClientRect().width;if(!w)return;
var kids=[].slice.call(g.children),n=0;while(g.getBoundingClientRect().width<m.clientWidth+40&&n++<12)kids.forEach(function(k){var c=k.cloneNode(true);c.setAttribute('aria-hidden','true');if(c.tagName==='IMG')c.alt='';g.appendChild(c)});
var c2=g.cloneNode(true);c2.setAttribute('aria-hidden','true');t.appendChild(c2);t.style.setProperty('--mq',(g.getBoundingClientRect().width/60)+'s');m.classList.add('run')}
function mqs(){doc.querySelectorAll('[data-mq]').forEach(mq)}
if(doc.fonts&&doc.fonts.ready){doc.fonts.ready.then(mqs);setTimeout(mqs,2500)}else mqs();
/* sliders */
doc.querySelectorAll('[data-slider]').forEach(function(sl){
var t=sl.firstElementChild,s=[].slice.call(t.children),rail=sl.classList.contains('rail'),host=sl.parentElement,i=0,x=0,timer;
var ds=[].slice.call((host.querySelectorAll('.dots button'))),pv=host.querySelector('.prev'),nx=host.querySelector('.next');
if(s.length<2&&!rail){sl.style.cursor='auto';return}
function inner(){var c=getComputedStyle(sl);return sl.clientWidth-parseFloat(c.paddingLeft)-parseFloat(c.paddingRight)}
function max(){return Math.max(0,t.scrollWidth-inner())}
function pos(k){return Math.min(s[k].offsetLeft-s[0].offsetLeft,rail?max():1e9)}
function last(){if(!rail)return s.length-1;for(var k=0;k<s.length;k++)if(s[k].offsetLeft-s[0].offsetLeft>=max()-1)return k;return s.length-1}
function go(k,wrap){var L=last();i=wrap?(k+L+1)%(L+1):Math.max(0,Math.min(L,k));x=pos(i);t.style.transform='translate3d('+(-x)+'px,0,0)';
ds.forEach(function(d,j){if(j===i)d.setAttribute('aria-current','true');else d.removeAttribute('aria-current')});
if(pv)pv.disabled=i===0;if(nx)nx.disabled=i>=L;
s.forEach(function(el,j){var v=el.querySelector('video[data-play]');if(v&&!still){if(j===i&&seen)v.play().catch(function(){});else v.pause()}})}
var seen=false,auto=+sl.dataset.auto;
function arm(){clearInterval(timer);if(auto&&!still&&seen&&s.length>1)timer=setInterval(function(){if(!doc.hidden)go(i+1,true)},auto)}
ds.forEach(function(d,j){d.addEventListener('click',function(){go(j);arm()})});
if(pv)pv.addEventListener('click',function(){go(i-1)});if(nx)nx.addEventListener('click',function(){go(i+1)});
var down=null,moved=0;
sl.addEventListener('pointerdown',function(ev){if(ev.button)return;down={x:ev.clientX,y:ev.clientY};moved=0});
addEventListener('pointermove',function(ev){if(!down)return;var dx=ev.clientX-down.x;if(!moved&&Math.abs(dx)<8)return;moved=dx;sl.classList.add('drag');t.style.transform='translate3d('+(-x+dx)+'px,0,0)'});
function up(){if(!down)return;down=null;sl.classList.remove('drag');if(Math.abs(moved)>50)go(i+(moved<0?1:-1));else go(i);arm()}
addEventListener('pointerup',up);addEventListener('pointercancel',up);
sl.addEventListener('click',function(ev){if(Math.abs(moved)>8){ev.preventDefault();ev.stopPropagation();moved=0}},true);
sl.addEventListener('dragstart',function(ev){ev.preventDefault()});
addEventListener('resize',function(){sl.classList.add('drag');go(i);requestAnimationFrame(function(){sl.classList.remove('drag')})});
if('IntersectionObserver' in window)new IntersectionObserver(function(en){seen=en[0].isIntersecting;go(i);arm()},{threshold:.25}).observe(sl);else{seen=true;arm()}
go(0)});
/* a film outside a slider plays while it is in view */
if(still)doc.querySelectorAll('video[data-play]').forEach(function(v){v.controls=true});
/* the rule between the link columns draws once, when seen */
var dv=doc.querySelectorAll('[data-seen]');if('IntersectionObserver' in window){var io=new IntersectionObserver(function(en){en.forEach(function(n){if(n.isIntersecting){n.target.classList.add('seen');io.unobserve(n.target)}})},{threshold:.15});dv.forEach(function(n){io.observe(n)})}else dv.forEach(function(n){n.classList.add('seen')});
})();
'''


def render(d: dict) -> str:
    c = colours(d.get('palette') or {})
    ui = UI.get((d.get('lang') or 'en')[:2], UI['en'])
    used = set()
    statement = s_statement(d, used)           # takes the first screen; the rest go to the features show
    body = ''.join([s_header(d, ui), '<main>', s_hero(d), s_trust(d), s_steps(d, c), s_figures(d, ui), s_features(d, used), statement,
                    s_plans(d), s_faq(d), s_links(d), s_close(d), '</main>', s_footer(d)])
    b, h = d.get('brand', {}), d.get('hero') or {}
    title = ' — '.join(x for x in (b.get('name'), h.get('title')) if x)
    return f'''<!doctype html>
<html lang="{e(d.get("lang") or "en")}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(h.get("text") or "")}"><meta name="theme-color" content="{c["g"]}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap" rel="stylesheet">
<style>{css(c)}</style></head>
<body>{body}<script>{JS}</script></body></html>'''
