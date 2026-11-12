"""runningcharity/render.py — one pure function: render(d) -> a complete page.

Build measured on therunningcharity.org (home, FAQ, choose-a-run, how-it-works, who-we-are, locations) at 1440 and 390
on 2026-11-12 — see NOTES.md. Nothing of the reference's code, words, pictures, icons, logos or typefaces is here.
The client's data fills it; a section whose data is missing is left out whole. No model call, no file reads.
"""
import html
import re

FONTS = ('https://fonts.googleapis.com/css2?family=League+Gothic&family=Work+Sans:wght@400;600;700&display=swap')
WORDS = {  # accessible names only and the one price word; never invented copy
    'en': ('Menu', 'Close', 'from', 'Read more'), 'es': ('Menú', 'Cerrar', 'desde', 'Leer más'),
    'de': ('Menü', 'Schließen', 'ab', 'Weiterlesen'), 'fr': ('Menu', 'Fermer', 'dès', 'Lire la suite'),
    'it': ('Menu', 'Chiudi', 'da', 'Leggi di più'), 'sr': ('Meni', 'Zatvori', 'od', 'Više')}
FOLD_AT = 200    # a text longer than this shows its first sentence; the rest opens in place
FOLD_LIST = 12   # a catalogue or team longer than this shows its groups; each opens in place
_W = WORDS['en']


# ───────────────────────── helpers
def e(s):
    return html.escape(str(s if s is not None else ''), quote=True)


def _rgb(h):
    h = (h or '#000').strip().lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    try:
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return (0, 0, 0)


def _hex(c):
    return '#%02x%02x%02x' % tuple(max(0, min(255, round(v))) for v in c)


def _mix(a, b, t):
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


def _deepen(c, grounds, toward='#000000', need=4.7):
    """the colour c, darkened toward `toward` only as far as needed to read `need`:1 on every ground"""
    t = 1.0
    while t > 0 and min(_con(_mix(c, toward, t), g) for g in grounds) < need:
        t -= .04
    return _mix(c, toward, max(t, 0))


def _first_sentence(t):
    m = re.match(r'(.+?[.!?…])(\s+)(?=[A-Z0-9“"(¿¡ÁÉÍÓÚÄÖÜ])', t, re.S)
    return (m.group(1), t[m.end():]) if m and len(t) - m.end() > 40 else (t, '')


def _fold(t, cls='body', extra=''):
    """long copy: the first sentence stays, the rest (and `extra`, e.g. a list) opens in place under the reference's
    round toggle. Nothing is dropped; without script <details> still opens."""
    t = str(t or '').strip()
    if not t and not extra:
        return ''
    head, rest = _first_sentence(t) if len(t) > FOLD_AT else (t, '')
    if not rest and not extra:
        return _paras(t, cls)
    if not rest and len(t) <= FOLD_AT and extra.count('<li') <= 3:
        return _paras(t, cls) + extra
    return (f'<p class="{cls}">{e(head)}</p><details class="more"><summary aria-label="{e(_W[3])}">'
            f'<span class="tog" aria-hidden="true"></span></summary><div class="more-b">{_paras(rest, cls)}{extra}</div></details>')


def _a(link, cls='', extra=''):
    if not link or not link.get('t'):
        return ''
    h = link.get('h') or ''
    if not h:
        return f'<span class="{cls}"{extra}>{e(link["t"])}</span>'
    return f'<a class="{cls}" href="{e(h)}"{extra}>{e(link["t"])}</a>'


def _m(src):
    return '../../' + src if src and not re.match(r'(https?:|data:|/)', src) else (src or '')


def _paras(t, cls=''):
    if not t:
        return ''
    parts = [p.strip() for p in re.split(r'\n\s*\n', str(t)) if p.strip()]
    return ''.join(f'<p class="{cls}">{e(p)}</p>' for p in parts)


# ───────────────────────── pictures
class Pics:
    """the client's own photographs, each used once; chosen by size, proportion and role, never all of them"""

    def __init__(self, d):
        ph = [p for p in ((d.get('media') or {}).get('photos') or []) if p.get('src') and p.get('w') and p.get('h')]
        self.all = ph
        self.used = set()
        # pictures a block already names as its own (catalogue items, team portraits) are reserved for that block
        cat = d.get('catalogue') or {}
        for g in cat.get('groups') or []:
            for it in g.get('items') or []:
                if it.get('img'):
                    self.used.add(it['img'])
        for p in _people(d):
            if p.get('img'):
                self.used.add(p['img'])

    def take(self, min_w, ar_lo, ar_hi, roles_no=('portrait',), prefer=None):
        best = None
        for p in self.all:
            if p['src'] in self.used or p.get('small') or p['w'] < min_w:
                continue
            ar = p['w'] / p['h']
            if not (ar_lo <= ar <= ar_hi) or (p.get('role') in roles_no):
                continue
            if prefer and p.get('role') not in prefer:
                if best is None:
                    best = p
                continue
            best = p
            break
        if best:
            self.used.add(best['src'])
        return best

    def info(self, src):
        for p in self.all:
            if p['src'] == src:
                return p
        return None


def _people(d):
    t = d.get('team') or {}
    out = list(t.get('items') or [])
    for g in t.get('groups') or []:
        out += list(g.get('items') or [])
    return out


def _img(p, cls, sizes, slot, eager=False, pos='50% 50%'):
    if not p:
        return ''
    lazy = '' if eager else ' loading="lazy"'
    return (f'<img class="{cls} f" data-slot="{slot}" src="{e(_m(p["src"]))}" width="{p["w"]}" height="{p["h"]}" '
            f'alt="{e(p.get("alt", ""))}" sizes="{sizes}" style="object-position:{pos}"'
            f'{lazy} decoding="async">')


# ───────────────────────── sections
def _header(d, W):
    b = d.get('brand') or {}
    word = f'<span class="logo-word">{e(b.get("name", ""))}</span>'
    if b.get('logo') and b.get('logo_wordmark'):
        logo = f'<img class="logo-img" src="{e(_m(b["logo"]))}" alt="{e(b.get("name", ""))}">'
    elif b.get('logo'):  # a mark without the name beside it: the reference's logo is a mark and a two-line wordmark
        logo = f'<img class="logo-img mark" src="{e(_m(b["logo"]))}" alt="">{word}'
    else:
        logo = word
    home = b.get('home') or '#top'
    nav = ''.join(f'<li><a href="{e(n.get("h") or "#")}">{e(n.get("t"))}</a></li>' for n in (d.get('nav') or []) if n.get('t'))
    cta = d.get('cta') or {}
    pill = _a(cta, 'pill') if cta.get('t') else ''
    sign = _a(d.get('signin') or {}, 'navlink')
    return f'''<header class="hd" id="top"><div class="hd-in">
<a class="logo" href="{e(home)}">{logo}</a>
<nav class="nav" aria-label="{e(b.get("name", ""))}"><ul>{nav}</ul>{sign}{pill}</nav>
<button class="burger" type="button" aria-expanded="false" aria-controls="drawer" aria-label="{W[0]}"><span></span><span></span><span></span></button>
</div></header>
<div class="drawer" id="drawer" hidden><ul>{nav}</ul>{sign}{pill}</div>'''


def _hero(d, P):
    h = d.get('hero') or {}
    if not h.get('title'):
        return ''
    pic = P.take(1200, 1.0, 2.6, roles_no=('portrait', 'people'))
    pic = pic or P.take(1200, .6, 2.6)
    t = h['title']
    big = ' long' if len(t) > 70 else ''
    kick = f'<p class="sub">{e(h["kicker"])}</p>' if h.get('kicker') else ''
    txt = f'<p class="lead">{e(h["text"])}</p>' if h.get('text') else ''
    btns = _a(h.get('primary') or {}, 'pill') + _a(h.get('secondary') or {}, 'tlink')
    btns = f'<div class="acts">{btns}</div>' if btns else ''
    note = f'<p class="note">{e(h["note"])}</p>' if h.get('note') else ''
    media = (f'<figure class="half right">{_img(pic, "cover", "(max-width:800px) 100vw, 50vw", "hero", eager=True)}</figure>'
             if pic else '')
    return f'''<section class="hero{" has-pic" if pic else " no-pic"}">{media}<div class="wrap"><div class="col">
{kick}<h1 class="h1{big}">{e(t)}</h1>{txt}{btns}{note}</div></div></section>'''


def _split_fig(v):
    m = re.match(r'^(\D{0,2}?)([\d][\d.,]*)(.*)$', str(v).strip())
    if not m:
        return '', '', str(v)
    return m.group(1), m.group(2), m.group(3)


def _stats(d):
    figs = [f for f in (d.get('figures') or []) if f.get('v')]
    st = d.get('statement') or {}
    if not figs and not st.get('title'):
        return ''
    left = ''
    if st.get('title') or st.get('text'):
        left = (f'<div class="st-l">{"<h2 class=st-h>" + e(st["title"]) + "</h2>" if st.get("title") else ""}'
                f'{"<p class=st-t>" + e(st["text"]) + "</p>" if st.get("text") else ""}</div>')
    items = ''
    for f in figs:
        pre, num, suf = _split_fig(f['v'])
        if num and re.fullmatch(r'(19|20)\d\d', num) and not pre and not suf.strip():  # a year is not counted up
            n, s = f'<span class="n">{e(num)}</span>', ''
        elif num:
            n = f'<span class="n">{e(pre)}<span class="cnt" data-to="{e(num)}">{e(num)}</span></span>'
            s = f'<span class="sfx">{e(suf)}</span>' if suf.strip() else ''
        if not num:
            n, s = f'<span class="n word">{e(f["v"])}</span>', ''
        items += f'<div class="fig"><p class="fv">{n}{s}</p>{"<p class=fl>" + e(f["l"]) + "</p>" if f.get("l") else ""}</div>'
    cols = len(figs) if len(figs) <= 4 else 3
    grid = f'<div class="figs" style="--cols:{cols}">{items}</div>' if figs else ''
    return f'<section class="stats{" solo" if not figs else ""}"><div class="st-in">{left}{grid}</div></section>'


def _imgtext(title, text, cta, pic, side, slot, extra=''):
    if not title and not text:
        return ''
    t = f'<h2 class="h2">{e(title)}</h2>' if title else ''
    body = _paras(text, 'body')
    btn = f'<div class="acts">{_a(cta, "pill")}</div>' if cta and cta.get('t') else ''
    media = (f'<figure class="half {side}">{_img(pic, "cover", "(max-width:800px) 100vw, 50vw", slot)}</figure>' if pic else '')
    return f'''<section class="it {side}-pic{" has-pic" if pic else " no-pic"}">{media}<div class="wrap"><div class="col">{t}{body}{btn}{extra}</div></div></section>'''


def _steps_list(d):
    s = d.get('steps') or {}
    items = [i for i in (s.get('items') or []) if i.get('title') or i.get('text')]
    if not items:
        return ''
    if len(items) > 4:  # many roles stand in the reference's two-up (two centred columns) rather than one long list
        cols, last_k = [], None
        for n, i in enumerate(items, 1):
            k = i.get('k')
            kk = f'<p class="sub">{e(k)}</p>' if k and k != i.get('title') else ''
            cta = i.get('cta') or {}
            link = f'<p>{_a(cta, "tlink")}</p>' if cta.get('t') else ''
            cols.append(f'<article class="cc">{kk}<h3 class="cc-t">{n}. {e(i.get("title") or k)}</h3><div class="cc-b">{_fold(i.get("text"))}{link}</div></article>')
        return _two_up(cols, 'feat steps2')
    out, last_k = '', None
    for n, i in enumerate(items, 1):
        k = i.get('k')
        kk = f'<p class="sub">{e(k)}</p>' if k and k != last_k and k != i.get('title') else ''
        last_k = k
        cta = i.get('cta') or {}
        link = f'<p>{_a(cta, "tlink")}</p>' if cta.get('t') else ''
        out += f'<div class="step">{kk}<h3 class="h3">{n}. {e(i.get("title") or k)}</h3>{_fold(i.get("text"))}{link}</div>'
    return f'<section class="how"><div class="narrow">{out}</div></section>'


def _band(d, P, W):
    """the wide photograph band with the moving line (reference: the 1000-mile band)"""
    c = d.get('catalogue') or {}
    title = c.get('title') or (d.get('statement') or {}).get('title')
    if not title:
        return ''
    line = c.get('note') if c.get('title') else ''
    pic = P.take(1500, 1.25, 2.7, roles_no=('portrait', 'people')) or P.take(1500, 1.25, 2.7)
    words = e(title.rstrip('.') + '.')
    reps = max(4, 64 // max(1, len(title)))
    track = ''.join(f'<span{" aria-hidden=true" if i else ""}>{words}</span>' for i in range(reps))
    img = _img(pic, 'cover', '100vw', 'band') if pic else ''
    line = f'<p class="band-l">{e(line)}</p>' if line else ''
    return f'''<section class="band{" has-pic" if pic else " no-pic"}">{img}<div class="veil"></div>
<div class="band-c"><h2 class="mq" data-speed="128"><span class="mq-t" style="--dur:{len(title) * reps * 33 / 128 / 2:.1f}s">{track}{track}</span></h2>{line}</div></section>'''


def _cat_item_card(it, P, W):
    p = P.info(it.get('img')) if it.get('img') else None
    if p and p.get('small') and p['w'] < 369:
        p = None
    img = f'<figure class="c-img">{_img(p, "cover", "(max-width:800px) 100vw, 369px", "item")}</figure>' if p else ''
    name = it.get('name') or ''
    big = ' big' if len(name) <= 10 else ''
    title = (f'<a class="c-link" href="{e(it["h"])}">{e(name)}</a>' if it.get('h') else e(name))
    price = ''
    if it.get('price'):
        pr = it['price']
        if it.get('from') and not re.match(r'(?i)(from|ab|desde|dès|da|od)\b', pr):
            pr = f'{W[2]} {pr}'
        price = f'<p class="price">{e(pr)}</p>'
    state = f'<p class="state">{e(it["state"])}</p>' if it.get('state') else ''
    note = f'<p class="cnote">{e(it["note"])}</p>' if it.get('note') else ''
    prices = ''
    if it.get('prices'):
        prices = '<dl class="prices">' + ''.join(
            f'<div><dt>{e(x.get("label"))}</dt><dd>{e(x.get("price"))}</dd></div>' for x in it['prices']) + '</dl>'
    rows = ''
    if it.get('rows'):
        rows = '<ul class="rows">' + ''.join(f'<li>{e(r)}</li>' for r in it['rows']) + '</ul>'
    txt = _fold(it.get('text'), 'ctext', rows)
    return (f'<article class="card{" no-img" if not p else ""}">{img}<div class="c-body"><h4 class="c-t{big}">{title}</h4>'
            f'{price}{state}{note}{prices}{txt}</div></article>')


def _cat_item_row(it, W):
    name = it.get('name') or ''
    title = f'<a href="{e(it["h"])}">{e(name)}</a>' if it.get('h') else e(name)
    pr = it.get('price') or ''
    if pr and it.get('from') and not re.match(r'(?i)(from|ab|desde|dès|da|od)\b', pr):
        pr = f'{W[2]} {pr}'
    sub = ' · '.join(x for x in (it.get('note'), it.get('state')) if x)
    prices = ''
    if it.get('prices'):
        prices = '<p class="r-more">' + ' · '.join(f'{e(x.get("label"))} {e(x.get("price"))}' for x in it['prices']) + '</p>'
    rows = ('<ul class="r-rows">' + ''.join(f'<li>{e(r)}</li>' for r in it['rows']) + '</ul>') if it.get('rows') else ''
    return (f'<li class="row"><div class="r-top"><span class="r-n">{title}</span>{"<span class=r-p>" + e(pr) + "</span>" if pr else ""}</div>'
            f'{"<p class=r-sub>" + e(sub) + "</p>" if sub else ""}{prices}{_fold(it.get("text"), "r-text", rows)}</li>')


def _catalogue(d, P, W):
    c = d.get('catalogue') or {}
    groups = [g for g in (c.get('groups') or []) if g.get('items')]
    if not groups:
        return ''
    head = ''
    if c.get('text'):
        head = f'<div class="intro">{_paras(c["text"], "body")}</div>'
    fold = sum(len(g['items']) for g in groups) > FOLD_LIST
    out, since_band = '', 0
    for g in groups:
        items = g['items']
        with_img = sum(1 for i in items if i.get('img') and (P.info(i['img']) or {}).get('w', 0) >= 369)
        gt = g.get('t') or ''
        gtitle = (f'<a href="{e(g["h"])}">{e(gt)}</a>' if g.get('h') else e(gt))
        gtext = _paras(g.get('text'), 'body')
        if fold:
            if with_img * 2 >= len(items):
                inner = f'{gtext}<div class="cards">{"".join(_cat_item_card(i, P, W) for i in items)}</div>'
            else:
                inner = f'<div class="narrow">{gtext}<ul class="list">{"".join(_cat_item_row(i, W) for i in items)}</ul></div>'
            link = f'<p class="fg-l">{_a({"t": gt, "h": g["h"]}, "tlink")}</p>' if g.get('h') and gt else ''
            out += (f'<details class="fg"><summary><span class="fg-tx"><span class="fg-t">{e(gt)}</span>'
                    f'<span class="fg-m">{e(_group_meta(items))}</span></span><span class="tog" aria-hidden="true"></span></summary>'
                    f'<div class="fg-b">{inner}{link}</div></details>')
            continue
        if with_img * 2 >= len(items):
            cards = ''.join(_cat_item_card(i, P, W) for i in items)
            out += f'<div class="grp cards-grp">{"<h3 class=gt>" + gtitle + "</h3>" if gt else ""}{gtext}<div class="cards">{cards}</div></div>'
            since_band = 0
        else:
            rows = ''.join(_cat_item_row(i, W) for i in items)
            out += f'<div class="grp rows-grp"><div class="narrow">{"<h3 class=gt>" + gtitle + "</h3>" if gt else ""}{gtext}<ul class="list">{rows}</ul></div></div>'
            since_band += len(items)
            if since_band >= 14:  # a long price list is broken by one of the client's own photographs when one is left
                pic = P.take(1500, 1.4, 3.2)
                if pic:
                    out += f'<div class="strip">{_img(pic, "cover", "100vw", "list-break")}</div>'
                    since_band = 0
    note = f'<p class="cat-note">{e(c["note"])}</p>' if c.get('note') else ''
    if fold:
        out = f'<div class="folds">{out}</div>'
    return f'<section class="cat{" folded" if fold else ""}">{head}{out}{note}</section>'


_CUR = re.compile(r'€|£|\$|CHF|EUR|GBP|USD|RSD|din\.?|kn|zł|Kč|kr')


def _amount(p):
    m = re.search(r'\d[\d.,\s]*', p or '')
    if not m:
        return None
    n = m.group(0).strip().replace(' ', '')
    if re.fullmatch(r'\d{1,3}([.,]\d{3})+', n):
        n = re.sub(r'[.,]', '', n)
    else:
        n = n.replace(',', '.')
    try:
        return float(n)
    except ValueError:
        return None


def _group_meta(items):
    """a folded group's line: its count, and the client's own lowest and highest price when every item has a price in one
    currency; otherwise its first names"""
    n = len(items)
    prices = [i.get('price') or '' for i in items]
    curs = {tuple(_CUR.findall(p)) for p in prices}
    amts = [_amount(p) for p in prices]
    if all(prices) and len(curs) == 1 and next(iter(curs)) and all(a is not None for a in amts):
        lo = prices[amts.index(min(amts))]
        hi = prices[amts.index(max(amts))]
        return f'{n} · {lo}' + (f' – {hi}' if hi != lo else '')
    names = [i.get('name') for i in items if i.get('name')]
    return f'{n} · ' + ', '.join(names[:3]) + (' …' if len(names) > 3 else '')


def _faq(d):
    f = d.get('faq') or {}
    items = [i for i in (f.get('items') or []) if i.get('q')]
    if not items:
        return ''
    lis = ''.join(
        f'<details class="qa"{" open" if n == 0 else ""}><summary><span class="q">{e(i["q"])}</span><span class="tog" aria-hidden="true"></span></summary>'
        f'<div class="ans">{_paras(i.get("a"), "body")}</div></details>' for n, i in enumerate(items))
    t = f'<h2 class="acc-t">{e(f["title"])}</h2>' if f.get('title') else ''
    return f'<section class="faq"><div class="narrow">{t}<div class="acc">{lis}</div></div></section>'


def _two_up(blocks, cls=''):
    blocks = [b for b in blocks if b]
    if not blocks:
        return ''
    return f'<section class="two {cls}"><div class="two-in">{"".join(blocks)}</div></section>'


def _col(title, body, h=None):
    if not title and not body:
        return ''
    t = (f'<a href="{e(h)}">{e(title)}</a>' if h else e(title)) if title else ''
    return f'<article class="cc">{"<h3 class=cc-t>" + t + "</h3>" if t else ""}<div class="cc-b">{body}</div></article>'


def _addr(a):
    if not a:
        return ''
    line1 = a.get('street') or ''
    line2 = ' '.join(x for x in (a.get('postcode'), a.get('city')) if x)
    line3 = ', '.join(x for x in (a.get('region'), a.get('country')) if x)
    return '<p>' + '<br>'.join(e(x) for x in (line1, line2, line3) if x) + '</p>'


def _hours(hs):
    if not hs:
        return ''
    return '<p>' + '<br>'.join(e(f'{x.get("days", "")} {x.get("open", "")}–{x.get("close", "")}'.strip()) for x in hs) + '</p>'


def _tel(p):
    if not p:
        return ''
    if isinstance(p, dict):
        return f'<p><a class="tlink" href="{e(p.get("h") or "tel:" + re.sub(r"[^+0-9]", "", p.get("t", "")))}">{e(p.get("t"))}</a></p>' + (
            f'<p class="small">{e(p["note"])}</p>' if p.get('note') else '')
    return f'<p><a class="tlink" href="tel:{e(re.sub(r"[^+0-9]", "", str(p)))}">{e(p)}</a></p>'


def _mail(m):
    return f'<p><a class="tlink" href="mailto:{e(m)}">{e(m)}</a></p>' if m else ''


def _reach(d):
    cols = []
    locs = d.get('locations') or []
    pl = d.get('place') or {}
    if locs:
        for l in locs:
            body = _addr(l.get('address')) + _tel(l.get('phone')) + _mail(l.get('email')) + _hours(l.get('hours')) + _fold(l.get('note'))
            cols.append(_col(l.get('name'), body, l.get('h')))
    elif pl.get('address') or pl.get('phone'):
        a = pl.get('address') or {}
        body = (_addr(a) + _tel(pl.get('phone')) + _mail(pl.get('email')) + _hours(pl.get('hours'))
                + (f'<p>{_a(pl["booking"], "tlink")}</p>' if (pl.get('booking') or {}).get('t') else ''))
        cols.append(_col(a.get('city') or (d.get('brand') or {}).get('name'), body))
    c = d.get('contact') or {}
    if c:
        routes = ''.join(
            f'<p>{_a({"t": r.get("t"), "h": r.get("h")}, "tlink")}{("<br><span class=small>" + e(r["note"]) + "</span>") if r.get("note") and r.get("note") != r.get("t") else ""}</p>'
            for r in (c.get('routes') or []) if r.get('t') and not _is_social(r))
        form = f'<p>{_a(c["form"], "tlink")}</p>' if (c.get('form') or {}).get('t') else ''
        ph = c.get('phone') or {}
        body = (f'<p class="small">{e(ph["note"])}</p>' if ph.get('note') else '') + _mail(c.get('email')) + form + routes
        if ph.get('t') or body:
            cols.append(_col(ph.get('t'), body, ph.get('h')))
    for cr in d.get('credentials') or []:
        if cr.get('t'):
            body = _fold(cr.get('text')) + (f'<p class="small">{e(cr["year"])}</p>' if cr.get('year') else '')
            cols.append(_col(cr['t'], body, cr.get('h')))
    return _two_up(cols, 'reach')


SOCIAL = re.compile(r'(?i)facebook|instagram|twitter|youtube|tiktok|bsky|bluesky|linkedin|x\.com')


def _is_social(r):
    return bool(SOCIAL.search((r.get('h') or '') + ' ' + (r.get('t') or '')))


def _team(d):
    t = d.get('team') or {}
    people = [p for p in _people(d) if p.get('name')]
    if not people:
        return ''
    cards = ''
    for p in people:
        img = (f'<img class="tm-img f" data-slot="portrait" src="{e(_m(p["img"]))}" alt="{e(p["name"])}" loading="lazy">' if p.get('img') else '')
        name = f'<a href="{e(p["h"])}">{e(p["name"])}</a>' if p.get('h') else e(p['name'])
        cards += (f'<article class="tm{" has-img" if img else ""}">{img}<h3 class="tm-n">{name}</h3>'
                  f'{"<p class=tm-r>" + e(p["role"]) + "</p>" if p.get("role") else ""}{_fold(p.get("text"), "tm-x")}'
                  f'{_mail(p.get("email"))}{_tel(p.get("phone")) if p.get("phone") else ""}</article>')
    head = ''
    if t.get('title') or t.get('text'):
        head = (f'<div class="intro">{"<h2 class=h2c>" + e(t["title"]) + "</h2>" if t.get("title") else ""}'
                f'{_paras(t.get("text"), "body")}</div>')
    if len(people) > FOLD_LIST:
        groups = (t.get('groups') or []) or [{'t': t.get('title') or '', 'items': people}]
        out = ''
        for g in groups:
            ps = [p for p in g.get('items') or [] if p.get('name')]
            if not ps:
                continue
            sub = ''.join(c for c in re.findall(r'<article class="tm.*?</article>', cards, re.S) if any(f'>{e(p["name"])}<' in c for p in ps))
            meta = f'{len(ps)} · ' + ', '.join(p['name'] for p in ps[:3]) + (' …' if len(ps) > 3 else '')
            out += (f'<details class="fg"><summary><span class="fg-tx"><span class="fg-t">{e(g.get("t") or "")}</span>'
                    f'<span class="fg-m">{e(meta)}</span></span><span class="tog" aria-hidden="true"></span></summary>'
                    f'<div class="fg-b"><div class="tm-grid">{sub}</div></div></details>')
        return f'<section class="team">{head}<div class="folds">{out}</div></section>'
    return f'<section class="team">{head}<div class="tm-grid">{cards}</div></section>'


def _links(d):
    ls = [l for l in (d.get('links') or []) if l.get('t')]
    if not ls:
        return ''
    cards = ''.join(
        f'<article class="lk">{"<a class=lk-a href=" + chr(34) + e(l["h"]) + chr(34) + ">" if l.get("h") else "<div class=lk-a>"}'
        f'<h3 class="lk-t">{e(l["t"])}</h3>{"<p class=lk-d>" + e(l["d"]) + "</p>" if l.get("d") else ""}'
        f'{"</a>" if l.get("h") else "</div>"}</article>' for l in ls)
    return f'<section class="links"><div class="lk-grid">{cards}</div></section>'


def _plans(d):
    p = d.get('plans') or {}
    items = [i for i in (p.get('items') or []) if i.get('name')]
    if not items:
        return ''
    cards = ''
    for i in items:
        rows = ('<ul class="rows">' + ''.join(f'<li>{e(r)}</li>' for r in i.get('rows') or []) + '</ul>') if i.get('rows') else ''
        price = f'<p class="price">{e(i.get("price", ""))}{" <span>" + e(i["per"]) + "</span>" if i.get("per") else ""}</p>' if i.get('price') else ''
        cards += (f'<article class="card no-img{" marked" if i.get("marked") else ""}"><div class="c-body"><h4 class="c-t{" big" if len(i["name"]) <= 10 else ""}">{e(i["name"])}</h4>'
                  f'{price}{"<p class=cnote>" + e(i["line"]) + "</p>" if i.get("line") else ""}{rows}'
                  f'{"<div class=acts>" + _a(i["cta"], "pill") + "</div>" if (i.get("cta") or {}).get("t") else ""}</div></article>')
    head = ''
    if p.get('title') or p.get('text'):
        head = f'<div class="intro">{"<h2 class=h2c>" + e(p["title"]) + "</h2>" if p.get("title") else ""}{_paras(p.get("text"), "body")}</div>'
    note = f'<p class="cat-note">{e(p["note"])}</p>' if p.get('note') else ''
    return f'<section class="cat plans">{head}<div class="grp cards-grp"><div class="cards">{cards}</div></div>{note}</section>'


def _quotes(d):
    qs = [q for q in (d.get('quotes') or []) if (q.get('text') if isinstance(q, dict) else q)]
    if not qs:
        return ''
    out = ''
    for q in qs:
        if isinstance(q, dict):
            who = ', '.join(x for x in (q.get('name') or q.get('who'), q.get('role')) if x)
            out += _col(None, f'<blockquote class="body">{e(q.get("text"))}</blockquote>' + (f'<p class="small">{e(who)}</p>' if who else ''))
        else:
            out += _col(None, f'<blockquote class="body">{e(q)}</blockquote>')
    return f'<section class="two"><div class="two-in">{out}</div></section>'


def _close(d):
    c = d.get('close') or {}
    if not c.get('title') and not c.get('text'):
        return ''
    btn = f'<div class="acts c">{_a(c.get("cta") or {}, "pill")}</div>' if (c.get('cta') or {}).get('t') else ''
    return (f'<section class="close"><div class="narrow c">{"<h2 class=close-t>" + e(c["title"]) + "</h2>" if c.get("title") else ""}'
            f'{_paras(c.get("text"), "body")}{btn}</div></section>')


def _supporters(d):
    logos = [l for l in (d.get('logos') or []) if (l.get('src') if isinstance(l, dict) else l)]
    tr = [t for t in (d.get('trust') or []) if t]
    if logos:
        inner = ''.join(f'<img class="sup-logo" src="{e(_m(l["src"] if isinstance(l, dict) else l))}" alt="{e(l.get("alt", "") if isinstance(l, dict) else "")}" loading="lazy">' for l in logos)
    elif tr:
        inner = ''.join(f'<span class="sup-w">{e(t)}</span>' for t in tr)
    else:
        return ''
    return f'<section class="sup"><div class="sup-in">{inner}</div></section>'


def _foot(d, W):
    b = d.get('brand') or {}
    f = d.get('foot') or {}
    name = b.get('name') or ''
    track = ''.join(f'<span{" aria-hidden=true" if i else ""}>{e(name)}</span>' for i in range(8))
    nav = [n for n in (d.get('nav') or []) if n.get('t')]
    cols = ''
    if nav:
        cols += '<div class="fc"><ul>' + ''.join(f'<li><a href="{e(n.get("h") or "#")}">{e(n["t"])}</a></li>' for n in nav) + '</ul></div>'
    ls = [l for l in (d.get('links') or []) if l.get('t') and l.get('h')]
    if ls:
        cols += '<div class="fc"><ul>' + ''.join(f'<li><a href="{e(l["h"])}">{e(l["t"])}</a></li>' for l in ls) + '</ul></div>'
    reach = []
    c = d.get('contact') or {}
    pl = d.get('place') or {}
    ph = (c.get('phone') or {}).get('t') or ((pl.get('phone') or {}).get('t') if isinstance(pl.get('phone'), dict) else pl.get('phone'))
    em = c.get('email') or pl.get('email')
    if ph:
        reach.append(f'<li><a href="tel:{e(re.sub(r"[^+0-9]", "", ph))}">{e(ph)}</a></li>')
    if em:
        reach.append(f'<li><a href="mailto:{e(em)}">{e(em)}</a></li>')
    soc = [r for r in (c.get('routes') or []) if r.get('h') and _is_social(r)] + list(pl.get('social') or [])
    seen = set()
    for s in soc:
        if s.get('t') and s['t'] not in seen:
            seen.add(s['t'])
            reach.append(f'<li><a href="{e(s.get("h"))}">{e(s["t"])}</a></li>')
    if reach:
        cols += '<div class="fc"><ul>' + ''.join(reach) + '</ul></div>'
    text = f'<p class="ft-x">{e(f["text"])}</p>' if f.get('text') else ''
    legal = e(f.get('legal') or '') or e(name)
    fl = ''.join(f'<a href="{e(l.get("h") or "#")}">{e(l.get("t"))}</a>' for l in (f.get('links') or []) if l.get('t'))
    return f'''<footer class="ft"><div class="mq mq-s" aria-hidden="true"><span class="mq-t" style="--dur:{len(name) * 8 * 15 / 133 / 2:.1f}s">{track}{track}</span></div>
<div class="ft-in"><div class="fcols">{cols}</div>{text}</div>
<div class="ft-b"><div class="ft-bi"><p>{legal}</p><div class="fl">{fl}</div></div></div></footer>'''


# ───────────────────────── page
def render(d: dict) -> str:
    global _W
    W = WORDS.get((d.get('lang') or 'en')[:2], WORDS['en'])
    _W = W
    pal = d.get('palette') or {}
    ground = pal.get('ground') or '#ffffff'
    ink = pal.get('ink') or '#111111'
    extras = [x for x in (pal.get('extra') or []) if isinstance(x, str) and x.startswith('#')]
    dark_ground = _lum(ground) < .45
    if dark_ground:  # the reference is a light page; a dark client keeps its relations inverted
        ground, ink = '#ffffff', '#111111'
    cands = [ink] + extras + ([pal.get('accent')] if pal.get('accent') else [])
    head = min([c for c in cands if _con(c, ground) >= 7] or [ink], key=_lum)  # headings: the darkest of the palette
    dk = min(cands + ['#111111'], key=_lum) if min(_lum(c) for c in cands) < .03 else _mix(head, '#000000', .55)
    alt = _mix(ground, ink, .955)  # the reference's #f7f7f7 sections beside its white
    card = '#ffffff' if _lum(ground) < .97 else _mix(ground, '#ffffff', .5)
    acc0 = pal.get('accent') or '#ff6d25'
    acc = _deepen(acc0, [ground, alt, '#ffffff'])          # accent words on the light grounds
    pill = _deepen(acc0, ['#ffffff'], need=4.6)             # white words on the pill
    acc_dk = acc0 if _con(acc0, dk) >= 4.5 else _mix(acc0, '#ffffff', .45)
    if _con(acc_dk, dk) < 4.5:
        acc_dk = '#ffffff'
    body_ink = ink if _con(ink, alt) >= 4.6 else head

    P = Pics(d)
    b = d.get('brand') or {}
    parts = [_header(d, W), '<main id="main">', _hero(d, P), _stats(d)]
    s = d.get('steps') or {}
    st_cta = None
    parts.append(_imgtext(s.get('title'), s.get('text'), st_cta, P.take(1000, 1.2, 2.7) if (s.get('title') or s.get('text')) else None, 'left', 'steps'))
    parts.append(_steps_list(d))
    parts.append(_band(d, P, W))
    parts.append(_catalogue(d, P, W))
    parts.append(_plans(d))
    f = d.get('features') or {}
    parts.append(_imgtext(f.get('title'), f.get('text'), None, P.take(1000, 1.2, 2.7) if (f.get('title') or f.get('text')) else None, 'right', 'features'))
    fi = [i for i in (f.get('items') or []) if i.get('t')]
    parts.append(_two_up([_col(i['t'], _fold(i.get('d')), i.get('h')) for i in fi], 'feat'))
    parts.append(_quotes(d))
    parts.append(_faq(d))
    parts.append(_team(d))
    parts.append(_links(d))
    parts.append(_reach(d))
    parts.append(_close(d))
    parts.append(_supporters(d))
    parts.append('</main>')
    parts.append(_foot(d, W))
    body = '\n'.join(p for p in parts if p)

    css = CSS.replace('/*VARS*/', f'--g:{ground};--ink:{body_ink};--hd:{head};--dk:{dk};--alt:{alt};--card:{card};'
                                  f'--acc:{acc};--pill:{pill};--accdk:{acc_dk}')
    title = e(b.get('name') or (d.get('hero') or {}).get('title') or '')
    desc = e((d.get('hero') or {}).get('text') or '')
    return f'''<!doctype html><html lang="{e(d.get("lang") or "en")}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><meta name="description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}"><style>{css}</style>
<script>document.documentElement.classList.add('js')</script></head><body>
{body}
<script>{JS}</script></body></html>'''


CSS = r'''
:root{/*VARS*/;--f:'Work Sans','Helvetica Neue',Arial,sans-serif;--fc:'League Gothic','Oswald','Arial Narrow',sans-serif;--ease:cubic-bezier(.455,.03,.515,.955)}
*{box-sizing:border-box;margin:0;padding:0}
html{-webkit-text-size-adjust:100%;scroll-padding-top:100px}
body{background:var(--g);color:var(--ink);font:400 16px/1.4 var(--f);overflow-x:hidden}
img{display:block;max-width:100%}
a{color:inherit}
ul{list-style:none}
:focus-visible{outline:2px solid var(--acc);outline-offset:3px}
.ft :focus-visible,.band :focus-visible{outline-color:#fff}
html.js img.f{opacity:0;transition:opacity .5s .15s}
html.js img.f.in{opacity:1}
/* header — fixed, 85 tall, white, soft shadow (measured) */
.hd{position:fixed;top:0;left:0;right:0;z-index:50;background:#fff;box-shadow:0 1px 4px rgba(0,0,0,.16)}
.hd-in{height:85px;display:flex;align-items:center;justify-content:space-between;padding:0 62px}
.logo{display:flex;align-items:center;text-decoration:none;color:var(--hd);min-width:0}
.logo-img.mark{width:46px;height:46px;object-fit:cover;margin-right:8px}
.logo-img{height:46px;width:auto;max-width:220px;object-fit:contain}
.logo-word{font:400 34px/.95 var(--fc);text-transform:uppercase;letter-spacing:.005em;max-width:16ch}
.nav{display:flex;align-items:center;gap:20px}
.nav ul{display:flex}
.nav li a,.navlink{display:flex;align-items:center;height:85px;padding:0 15px;font-size:18px;line-height:25px;text-decoration:none;color:#111;transition:color .3s}
.nav li a:hover,.navlink:hover{color:var(--acc)}
.pill{display:inline-flex;align-items:center;justify-content:center;min-height:50px;padding:13px 30px 12px;border-radius:50px;background:var(--pill);color:#fff;font:400 18px/25px var(--f);text-decoration:none;transition:background .3s;text-align:center;max-width:100%;overflow-wrap:anywhere}
.pill:hover{background:color-mix(in srgb,var(--pill) 82%,#fff)}
.nav .pill{margin-left:15px;white-space:nowrap}
.burger{display:none;width:44px;height:44px;border:0;background:none;cursor:pointer;flex-direction:column;justify-content:center;align-items:center;gap:5px}
.burger span{display:block;width:20px;height:2px;background:#111;transition:transform .3s,opacity .3s}
.burger[aria-expanded=true] span:nth-child(1){transform:translateY(7px) rotate(45deg)}
.burger[aria-expanded=true] span:nth-child(2){opacity:0}
.burger[aria-expanded=true] span:nth-child(3){transform:translateY(-7px) rotate(-45deg)}
.drawer{position:fixed;top:70px;left:0;right:0;z-index:49;background:#fff;padding:10px 22px 30px;box-shadow:0 3px 12px rgba(0,0,0,.16);transform:translateY(0);transition:transform .4s var(--ease)}
.drawer li a{display:block;padding:12px 0;font-size:18px;text-decoration:none;color:#111;border-bottom:1px solid rgba(0,0,0,.15)}
.drawer .pill{margin-top:22px}
main{padding-top:85px}
/* type — measured */
.sub{color:var(--acc);font-size:18px;line-height:25px;margin-bottom:17px}
.h1{font:400 66px/55px var(--fc);letter-spacing:-.01em;text-transform:uppercase;color:var(--hd);margin-bottom:17px;overflow-wrap:break-word}
.h1.long{font-size:52px;line-height:47px}
.h2{font:400 44px/39px var(--fc);letter-spacing:-.01em;text-transform:uppercase;color:var(--hd);margin-bottom:25px;overflow-wrap:break-word}
.h2c{font:400 66px/55px var(--fc);letter-spacing:-.01em;text-transform:uppercase;color:var(--hd);margin-bottom:25px;text-align:center}
.h3{font:400 36px/39px var(--fc);letter-spacing:-.01em;text-transform:uppercase;color:var(--hd);margin:20px 0}
.body,.lead{font-size:18px;line-height:25px;margin-bottom:20px}
.note,.small{font-size:15px;line-height:21px;opacity:1}
.tlink{color:var(--acc);font-size:18px;line-height:25px;text-decoration:none;transition:color .3s;overflow-wrap:anywhere}
.tlink:hover{color:var(--hd);text-decoration:underline}
.acts{display:flex;flex-wrap:wrap;align-items:center;gap:14px 28px;margin:4px 0 18px}
.acts.c{justify-content:center}
.wrap{width:100%;max-width:1190px;margin:0 auto;padding:0 14px;position:relative}
.narrow{max-width:567px;margin:0 auto}
/* hero — text column 468 at 139; picture: the reference's 567 square beside the text becomes the edge-to-edge right half */
.hero{position:relative;background:#fff;min-height:807px;display:flex;align-items:center;padding:120px 0}
.hero .col{width:468px;max-width:100%}
.hero .note{margin-top:6px}
.half{position:absolute;top:0;bottom:0;width:50%;margin:0;overflow:hidden;background:var(--alt)}
.half.right{right:0}.half.left{left:0}
.half img{width:100%;height:100%;object-fit:cover}
.hero.no-pic .col{width:700px}
/* impact stats — white, inner pad 43/50; left 340; four figures */
.stats{background:#fff}
.st-in{display:grid;grid-template-columns:340px 1fr;gap:72px;padding:43px 50px 46px;max-width:1440px;margin:0 auto}
.stats.solo .st-in{grid-template-columns:1fr;max-width:640px}
.st-h{font:400 57.6px/50.7px var(--fc);letter-spacing:-.02em;text-transform:uppercase;color:var(--hd);margin-bottom:19px}
.st-t{font-size:16px;line-height:24px;color:var(--ink)}
.figs{display:grid;grid-template-columns:repeat(var(--cols),minmax(0,1fr));gap:40px 28px;align-content:center}
.fv{color:var(--acc);font:400 54.7px/48px var(--fc);letter-spacing:-.025em;margin-bottom:12px;white-space:nowrap}
.fv .n.word{white-space:normal;font-size:40px;line-height:40px}
.sfx{font-size:34px;line-height:30px;margin-left:3px}
.fl{font-size:14px;line-height:20px;color:var(--ink)}
/* image-text — #f7f7f7 ground, pad 120; text 468 at 833 (or 139); the 567×378 picture becomes the full-height half */
.it{position:relative;background:var(--alt);padding:120px 0;min-height:618px;display:flex;align-items:center}
.it .col{width:468px;max-width:100%}
.it.left-pic .col{margin-left:694px}
.it.no-pic .col{width:567px;margin:0 auto}
/* how-it-works list — 567 column at 437 */
.how{background:var(--alt);padding:0 0 100px}
.how .narrow{padding:0 14px;max-width:595px}
.it.left-pic + .how,.it + .how{margin-top:0}
.step{border-top:1px solid rgba(0,0,0,.15);padding:4px 0 6px}
.step:first-child{border-top:0}
.step .sub{margin:24px 0 -8px}
/* the band — 702 tall, pad 255, a moving line of 79px oblique type */
.band{position:relative;min-height:702px;display:flex;align-items:center;justify-content:center;overflow:hidden;background:var(--dk);color:#fff;text-align:center}
.band>img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.band .veil{position:absolute;inset:0;background:color-mix(in srgb,var(--dk) 52%,transparent)}
.band.no-pic .veil{display:none}
.band-c{position:relative;width:100%;padding:0 0 10px}
.mq{overflow:hidden;white-space:nowrap;font:italic 400 79px/55px var(--fc);text-transform:uppercase;letter-spacing:-.01em;color:#fff;padding:8px 0}
.mq-t{display:inline-flex;animation:mq var(--dur,19s) linear infinite}
.mq-t span{padding-right:20px}
@keyframes mq{to{transform:translateX(-50%)}}
.band-l{font-size:18px;line-height:25px;margin:22px auto 0;max-width:567px;padding:0 22px;color:#fff}
/* catalogue — the shop cards: white, shadow .16 0 3 12, square picture, centred 66/36px title, price in accent */
.cat{padding:120px 0 40px;background:var(--g)}
.cat .intro,.team .intro{max-width:567px;margin:0 auto 40px;text-align:center;padding:0 14px}
.grp{max-width:1190px;margin:0 auto 80px;padding:0 14px}
.gt{font:400 44px/39px var(--fc);letter-spacing:-.01em;text-transform:uppercase;color:var(--hd);margin:0 0 32px}
.gt a{text-decoration:none}.gt a:hover{color:var(--acc)}
.cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:56px 28px}
.card{background:var(--card);box-shadow:0 3px 12px rgba(0,0,0,.16);transition:box-shadow .3s;text-align:center;display:flex;flex-direction:column}
.card:hover{box-shadow:0 3px 15px rgba(0,0,0,.26)}
.card.marked{outline:2px solid var(--acc)}
.c-img{aspect-ratio:1/1;overflow:hidden;margin:0 0 42px}
.c-img img{width:100%;height:100%;object-fit:cover}
.card.no-img .c-body{padding-top:40px}
.c-body{padding:0 20px 40px}
.c-t{font:400 36px/39px var(--fc);letter-spacing:-.01em;text-transform:uppercase;color:var(--hd);margin-bottom:18px;overflow-wrap:break-word}
.c-t.big{font-size:66px;line-height:55px}
.c-t a{text-decoration:none}.c-t a:hover{color:var(--acc)}
.price{color:var(--acc);font-size:18px;line-height:25px;margin-bottom:20px}
.state{color:var(--acc);font-size:15px;line-height:21px;margin:-12px 0 16px;text-transform:uppercase;letter-spacing:.05em;font-weight:700}
.cnote{font-size:15px;line-height:21px;margin:-10px 0 18px}
.prices{margin:0 auto 22px;max-width:280px;text-align:left}
.prices div{display:flex;justify-content:space-between;gap:12px;border-bottom:1px solid rgba(0,0,0,.15);padding:7px 0;font-size:16px;line-height:22px}
.prices dd{color:var(--acc);white-space:nowrap}
.ctext{font-size:18px;line-height:25px;margin-bottom:20px}
.rows{text-align:left;font-size:15px;line-height:21px;border-top:1px solid rgba(0,0,0,.15)}
.rows li{border-bottom:1px solid rgba(0,0,0,.15);padding:8px 0}
.list{border-top:1px solid rgba(0,0,0,.15);margin-top:16px}
.row{border-bottom:1px solid rgba(0,0,0,.15);padding:15px 0}
.r-top{display:flex;justify-content:space-between;align-items:baseline;gap:20px;font-size:22px;line-height:25px}
.r-n a{text-decoration:none}.r-n a:hover{color:var(--acc)}
.r-p{color:var(--acc);white-space:nowrap}
.r-sub,.r-more{font-size:15px;line-height:21px;margin-top:6px}
.r-text{font-size:16px;line-height:23px;margin-top:8px}
.r-rows{font-size:15px;line-height:21px;margin-top:6px}
.r-rows li::before{content:'– '}
.cat-note{max-width:567px;margin:0 auto;text-align:center;font-size:18px;line-height:25px;padding:0 14px 60px}
.strip{height:420px;margin:0 0 80px;overflow:hidden}.strip img{width:100%;height:100%;object-fit:cover}
/* two-up — two centred columns 369 wide (at 238 and 833) */
.two{padding:100px 0;background:var(--g)}
.two.feat{background:var(--alt);padding-top:0}
.two-in{max-width:1190px;margin:0 auto;padding:0 14px;display:grid;grid-template-columns:repeat(2,369px);justify-content:space-evenly;gap:70px 28px}
.cc{text-align:center}
.cc-t{font:400 36px/39px var(--fc);letter-spacing:-.01em;text-transform:uppercase;color:var(--hd);margin-bottom:30px;overflow-wrap:break-word}
.cc-t a{text-decoration:none}.cc-t a:hover{color:var(--acc)}
.cc-b p,.cc-b blockquote{font-size:18px;line-height:25px;margin-bottom:14px;overflow-wrap:break-word}
.cc-b .small{font-size:15px;line-height:21px}
/* faq — the accordion: 44px group title, ruled rows, 22px questions, 36px round toggle in the accent */
.faq{padding:120px 14px 100px;background:var(--g)}
.acc-t{font:400 44px/39px var(--fc);letter-spacing:-.01em;text-transform:uppercase;color:var(--hd);margin-bottom:26px}
.acc{border-top:1px solid rgba(0,0,0,.15)}
.qa{border-bottom:1px solid rgba(0,0,0,.15)}
.qa summary{list-style:none;display:flex;justify-content:space-between;align-items:center;gap:20px;padding:15px 0;cursor:pointer;font-size:22px;line-height:25px;color:var(--ink)}
.qa summary::-webkit-details-marker{display:none}
.tog{flex:0 0 36px;height:36px;border-radius:50%;background:var(--pill);position:relative}
.tog::before,.tog::after{content:'';position:absolute;left:50%;top:50%;background:#fff;transform:translate(-50%,-50%)}
.tog::before{width:15.5px;height:2px}.tog::after{width:2px;height:15.5px;transition:transform .3s}
.qa[open] .tog::after{transform:translate(-50%,-50%) scaleY(0)}
.ans{padding:20px 0 5px;overflow:hidden}
/* long copy and long lists open in place under the accordion's round toggle */
.more{margin:-8px 0 18px}
.more>summary{list-style:none;cursor:pointer;display:inline-flex;padding:4px 0}
.more>summary::-webkit-details-marker{display:none}
.more .tog{width:28px;height:28px;flex:0 0 28px}
.more[open] .tog::after{transform:translate(-50%,-50%) scaleY(0)}
.more-b{padding-top:12px}
.card .more>summary,.cc .more>summary{justify-content:center}
.folds{max-width:1190px;margin:0 auto;padding:0 14px;border-top:1px solid rgba(0,0,0,.15)}
.fg{border-bottom:1px solid rgba(0,0,0,.15)}
.fg>summary{list-style:none;display:flex;justify-content:space-between;align-items:center;gap:24px;padding:22px 0;cursor:pointer}
.fg>summary::-webkit-details-marker{display:none}
.fg-tx{display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 28px}
.fg-t{font:400 44px/39px var(--fc);letter-spacing:-.01em;text-transform:uppercase;color:var(--hd)}
.fg-m{font-size:18px;line-height:25px;color:var(--ink)}
.fg[open] .tog::after{transform:translate(-50%,-50%) scaleY(0)}
.fg-b{padding:10px 0 60px}
.fg-b .narrow{padding:0}
.fg-l{text-align:center;margin-top:28px}
.team .folds{margin-top:10px}
/* team — five across, 219 wide; names 22px condensed, roles 15px; no portrait → type only */
.team{padding:120px 0 80px;background:var(--g)}
.tm-grid{max-width:1190px;margin:0 auto;padding:0 14px;display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:40px 24px}
.tm-img{width:100%;aspect-ratio:1/1;object-fit:cover;margin-bottom:14px}
.tm-n{font:400 22px/24px var(--fc);letter-spacing:.01em;text-transform:uppercase;color:var(--hd);margin-bottom:6px}
.tm-n a{text-decoration:none}
.tm-r{font-size:15px;line-height:21px;margin-bottom:6px}
.tm-x{font-size:15px;line-height:21px;margin-bottom:6px}
.tm .tlink{font-size:15px;line-height:21px}
/* links — the news cards: shadowed, content padding 32, 36px titles */
.links{padding:100px 0;background:var(--g)}
.lk-grid{max-width:1190px;margin:0 auto;padding:0 14px;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:28px}
.lk{background:var(--card);box-shadow:0 3px 12px rgba(0,0,0,.16);transition:box-shadow .3s}
.lk:hover{box-shadow:0 3px 15px rgba(0,0,0,.26)}
.lk-a{display:block;padding:32px;height:100%;text-decoration:none}
.lk-t{font:400 36px/39px var(--fc);letter-spacing:-.01em;text-transform:uppercase;color:var(--hd);margin-bottom:14px;overflow-wrap:break-word}
.lk-a:hover .lk-t{color:var(--acc)}
.lk-d{font-size:18px;line-height:25px}
/* close — the newsletter block: centred 52px title, 18px text, one pill */
.close{padding:120px 14px;background:var(--g)}
.c{text-align:center}
.close-t{font:400 52px/59px var(--fc);letter-spacing:-.01em;text-transform:uppercase;color:var(--hd);margin-bottom:10px}
.close .body{margin-bottom:30px}
/* supporters strip */
.sup{border-top:1px solid rgba(0,0,0,.15);padding:40px 14px 70px;background:var(--g)}
.sup-in{max-width:1000px;margin:0 auto;display:flex;flex-wrap:wrap;justify-content:center;align-items:center;gap:14px 40px}
.sup-w{font-size:15px;line-height:21px}
.sup-logo{height:60px;width:auto}
/* foot — #111, pad 60; moving 34px oblique line; columns 198 apart; 15px links at 60% white */
.ft{background:var(--dk);color:#fff;padding-top:60px}
.mq-s{font-size:34px;line-height:48px;padding:0}
.mq-s .mq-t span{padding-right:6px}
.ft-in{max-width:1190px;margin:56px auto 0;padding:0 14px}
.fcols{display:flex;flex-wrap:wrap;gap:30px 0}
.fc{width:198px;padding-right:20px}
.fc:last-child{width:auto;min-width:198px}
.fc li{font-size:15px;line-height:21px}
.fc a{color:rgba(255,255,255,.72);text-decoration:none;transition:color .3s;overflow-wrap:anywhere}
.fc li:first-child a{color:#fff}
.fc a:hover{color:var(--accdk)}
.ft-x{font-size:15px;line-height:21px;color:rgba(255,255,255,.72);margin-top:28px}
.ft-b{border-top:1px solid rgba(255,255,255,.15);margin-top:60px;padding:30px 0}
.ft-bi{max-width:1190px;margin:0 auto;padding:0 14px;display:flex;justify-content:space-between;gap:20px 40px;flex-wrap:wrap;font-size:15px;line-height:21px;color:rgba(255,255,255,.72)}
.fl{display:flex;gap:27px;flex-wrap:wrap}
.fl a{color:rgba(255,255,255,.72);text-decoration:none;transition:color .3s}
.fl a:hover{color:var(--accdk)}
/* in between */
@media (max-width:1200px){
 .hd-in{padding:0 30px}.nav li a{padding:0 10px;font-size:16px}
 .it.left-pic .col{margin-left:auto}
 .tm-grid{grid-template-columns:repeat(4,minmax(0,1fr))}
}
@media (max-width:1060px){
 .nav{display:none}.burger{display:flex}
}
/* phone — measured at 390 */
@media (max-width:800px){
 .hd-in{height:70px;padding:0 22px}
 .logo-img{height:36px;max-width:170px}.logo-img.mark{width:36px;height:36px}
 .logo-word{font-size:27px}
 main{padding-top:70px}
 .sub{font-size:15px;line-height:21px;margin-bottom:12px}
 .h1,.h1.long{font-size:38px;line-height:33px}
 .h2{font-size:32px;line-height:28px;margin-bottom:18px}
 .h2c{font-size:38px;line-height:33px;margin-bottom:15px}
 .h3{font-size:26px;line-height:24px}
 .body,.lead{font-size:15px;line-height:21px;margin-bottom:18px}
 .tlink{font-size:15px;line-height:21px}
 .wrap{padding:0 22px}
 .hero{display:block;min-height:0;padding:0 0 35px}
 .half{position:relative;width:100%;height:auto;aspect-ratio:4/3}
 .hero .half{aspect-ratio:1/1;margin-bottom:20px}
 .hero.no-pic{padding-top:40px}
 .hero .col,.it .col,.hero.no-pic .col{width:auto}
 .st-in{grid-template-columns:1fr;gap:34px;padding:30px 22px 34px}
 .figs{grid-template-columns:repeat(2,minmax(0,1fr));gap:30px 20px}
 .fv{font-size:42px;line-height:40px;white-space:normal}
 .sfx{font-size:26px}
 .it{display:block;min-height:0;padding:0 0 40px}
 .it.no-pic{padding-top:40px}
 .it .half{margin-bottom:25px}
 .it.left-pic .col,.it.no-pic .col{margin:0}
 .how{padding-bottom:40px}
 .band{min-height:420px}
 .mq{font-size:49px;line-height:55px}
 .band-l{font-size:15px;line-height:21px}
 .cat{padding:40px 0 10px}
 .grp{padding:0 22px;margin-bottom:50px}
 .gt,.acc-t,.fg-t{font-size:32px;line-height:28px;margin-bottom:20px}
 .fg-t{margin:0}.fg-m{font-size:15px;line-height:21px}.folds{padding:0 22px}.fg>summary{padding:16px 0}
 .cards{grid-template-columns:1fr;gap:24px}
 .c-t.big{font-size:52px;line-height:46px}
 .c-img{aspect-ratio:346/260;margin-bottom:24px}
 .ctext{font-size:15px;line-height:21px}
 .r-top{font-size:18px}
 .strip{height:240px;margin-bottom:50px}
 .two{padding:40px 0}
 .two-in{grid-template-columns:1fr;padding:0 22px;gap:40px}
 .cc-t{font-size:26px;line-height:24px;margin-bottom:15px}
 .cc-b p,.cc-b blockquote{font-size:15px;line-height:21px}
 .faq{padding:40px 22px}
 .qa summary{font-size:18px}
 .team{padding:40px 0}
 .tm-grid{grid-template-columns:repeat(2,minmax(0,1fr));padding:0 12px;gap:30px 24px}
 .tm-n{font-size:18px;line-height:20px}
 .links{padding:40px 0}
 .lk-grid{grid-template-columns:1fr;padding:0 22px;gap:24px}
 .lk-a{padding:16px 22px 22px}
 .lk-t{font-size:26px;line-height:28px}
 .lk-d{font-size:15px;line-height:21px}
 .close{padding:100px 22px}
 .close-t{font-size:38px;line-height:40px}
 .ft{padding-top:45px}
 .ft-in{margin-top:36px;padding:0 22px}
 .fc{width:50%}.fc li{font-size:13px;line-height:19px}
 .ft-b{margin-top:45px;padding:20px 0}
 .ft-bi{padding:0 22px;font-size:13px;line-height:19px;flex-direction:column}
}
@media (prefers-reduced-motion:reduce){
 *{transition:none!important;animation:none!important}
 html.js img.f{opacity:1}
 .mq{white-space:normal}.mq-t{display:block;text-align:center}.mq-t span[aria-hidden]{display:none}
 .mq-s{display:none}
}
'''

JS = r'''
(function(){
var rm=matchMedia('(prefers-reduced-motion: reduce)').matches;
document.querySelectorAll('img.f').forEach(function(i){function s(){i.classList.add('in')}if(i.complete)s();else{i.addEventListener('load',s);i.addEventListener('error',s)}});
var b=document.querySelector('.burger'),dr=document.getElementById('drawer');
if(b&&dr){b.addEventListener('click',function(){var o=b.getAttribute('aria-expanded')==='true';b.setAttribute('aria-expanded',String(!o));dr.hidden=o;});
 document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!dr.hidden){dr.hidden=true;b.setAttribute('aria-expanded','false');b.focus()}});}
// moving lines: the measured speed (128 px/s in the band, 133 px/s in the foot), whatever the words' width
document.querySelectorAll('.mq-t').forEach(function(t){var sp=t.closest('.mq-s')?133:128;var w=t.scrollWidth/2;if(w>0)t.style.setProperty('--dur',(w/sp).toFixed(2)+'s');});
// figures count up once when they come into view (measured: 0→final in about 1.8 s, easing out)
if(!rm&&'IntersectionObserver' in window){
 var io=new IntersectionObserver(function(es){es.forEach(function(en){if(!en.isIntersecting)return;io.unobserve(en.target);var el=en.target,raw=el.getAttribute('data-to'),sep=raw.indexOf(',')>-1?',':(/\.\d{3}/.test(raw)?'.':''),n=parseFloat(raw.replace(/[.,](?=\d{3}(\D|$))/g,''));if(!isFinite(n)||raw.length>9)return;var t0=performance.now();
  function fmt(v){var s=String(Math.round(v));return sep?s.replace(/\B(?=(\d{3})+(?!\d))/g,sep):s}
  function step(t){var k=Math.min(1,(t-t0)/1800),v=n*(1-Math.pow(1-k,3));el.textContent=k<1?fmt(v):raw;if(k<1)requestAnimationFrame(step)}requestAnimationFrame(step);});},{threshold:.3});
 document.querySelectorAll('.cnt').forEach(function(c){io.observe(c)});}
// accordion: opening slides the answer (the reference's slide, about .3 s)
if(!rm)document.querySelectorAll('.qa summary').forEach(function(s){s.addEventListener('click',function(ev){var d=s.parentNode,a=d.querySelector('.ans');if(!a)return;ev.preventDefault();
 if(d.open){var h=a.scrollHeight;a.animate([{height:h+'px'},{height:'0px'}],{duration:300,easing:'ease'}).onfinish=function(){d.open=false};}
 else{d.open=true;var h2=a.scrollHeight;a.animate([{height:'0px'},{height:h2+'px'}],{duration:300,easing:'ease'});}});});
})();
'''
