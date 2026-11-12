"""recycle/render.py — one pure function: render(d) -> a complete page.

The build (section order, grid, measures, type scale, spacing, the relation of the grounds, the phone build, the motion)
was measured on re-cycle.org — home page plus its FAQ, volunteering, how-we-do-it and contact pages — at 1440 and 390 on
2026-11-12 (see NOTES.md). Nothing of the reference's code, words, pictures, icons, logo or colours is here; the two
typefaces it uses (Rubik, DM Sans) are open-licence and are loaded from Google Fonts. The client's data fills the page;
a section whose data is missing is left out whole. No file reads, no model call, no client-specific logic.
"""
import html
import re

FONTS = 'https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&family=Rubik:wght@400;800&display=swap'
PRE = '../../'


# ───────────────────────── colour: the reference's relations (deep ground / bright accent / pale tint / white), client's palette
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


def _rgba(h, a):
    return 'rgba(%d,%d,%d,%s)' % (*_rgb(h), a)


def _toward(c, target, ground, want):
    """c moved toward target, as little as needed, until it stands `want`:1 on ground"""
    for i in range(0, 21):
        m = _mix(target, c, i / 20)
        if _con(m, ground) >= want:
            return m
    return target


def _colours(pal):
    ground = pal.get('ground') or '#ffffff'
    ink = pal.get('ink') or '#343434'
    accent = pal.get('accent') or ink
    if _lum(ground) < _lum(ink):                       # a dark client: the page ground still has to be the light one here
        ground, ink = ink, ground
    dark = ink
    for i in range(0, 21):                             # the deep ground: the ink, pushed down until it is a ground (lum ≤ .05)
        dark = _mix('#000000', ink, i / 20)
        if _lum(dark) <= .05:
            break
    darker = _mix('#000000', dark, .5)
    # the accent as a ground: its own text must hold 4.5:1; moved the least it takes
    on_acc = dark if _con(dark, accent) >= _con('#ffffff', accent) else '#ffffff'
    if _con(on_acc, accent) < 4.6:
        accent = _toward(accent, '#000000' if on_acc == '#ffffff' else '#ffffff', on_acc, 4.6)
    acc_dk = _toward(accent, '#ffffff', dark, 5.2)     # the accent as ink on the deep ground
    acc_lt = _toward(accent, '#000000', ground, 4.6)   # the accent as ink on the page ground
    tint = _mix(accent, '#ffffff', .42)                # the pale second colour (the reference's light teal beside its lime)
    if _con(dark, tint) < 5:
        tint = _toward(tint, '#ffffff', dark, 5)
    pale = _mix(tint, '#ffffff', .28)
    card = '#ffffff' if _lum(ground) > .8 else _mix('#ffffff', ground, .06)
    return dict(ground=ground, ink=ink, dark=dark, darker=darker, acc=accent, on_acc=on_acc, acc_dk=acc_dk, acc_lt=acc_lt,
                tint=tint, pale=pale, card=card, alt=_mix(ink, ground, .035), rule=_rgba(ink, .2),
                light_acc=on_acc != '#ffffff')


# ───────────────────────── small helpers
def e(s):
    return html.escape(str(s if s is not None else ''), quote=True)


def _paras(s, cls=''):
    parts = [p.strip() for p in re.split(r'\n\s*\n|\n', str(s or '')) if p.strip()]
    c = f' class="{cls}"' if cls else ''
    return ''.join(f'<p{c}>{e(p)}</p>' for p in parts)


def _href(h):
    h = str(h or '').strip()
    return h if re.match(r'^(https?:|mailto:|tel:|#|/)', h) else ''


def _torn(seed, bottom):
    """a ragged horizontal edge, 1596 × 75 (the reference's measure), drawn here from a fixed sequence; tiles sideways"""
    x, pts, s, y = 0, [], seed, 40.0
    while x < 1596:
        s = (s * 1103515245 + 12345) % 2147483648
        a = s / 2147483648
        s = (s * 1103515245 + 12345) % 2147483648
        b = s / 2147483648
        y += (a - .5) * 9 + (40 - y) * .05
        if b > .86:
            y += (a - .5) * 24
        y = max(10, min(66, y))
        pts.append((x, y))
        x += 3 + b * 9
    y0 = pts[0][1]
    line = ' '.join(f'L{px:.0f} {py:.0f}' for px, py in pts[1:]) + f' L1596 {y0:.0f}'
    path = (f'M0 0 L0 {y0:.0f} {line} L1596 0Z' if bottom else f'M0 75 L0 {y0:.0f} {line} L1596 75Z')
    svg = f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1596 75' preserveAspectRatio='none'><path d='{path}'/></svg>"
    return 'url("data:image/svg+xml,' + svg.replace('<', '%3C').replace('>', '%3E').replace('#', '%23') + '")'


ARROW = '<svg class="arw" viewBox="0 0 16 16" aria-hidden="true"><path d="M2.5 8h11M9 3.5 13.5 8 9 12.5" fill="none" stroke="currentColor" stroke-width="1.7"/></svg>'
ARROW_UP = '<svg class="arw" viewBox="0 0 16 16" aria-hidden="true"><path d="M4 12 12 4M5.5 4H12v6.5" fill="none" stroke="currentColor" stroke-width="1.7"/></svg>'


def _btn(link, kind='pri', extra=''):
    if not link or not link.get('t'):
        return ''
    h = _href(link.get('h'))
    tag, at = ('a', f' href="{e(h)}"') if h else ('span', '')
    arrow = ARROW if kind == 'lnk' else ''
    return f'<{tag}{at} class="btn {kind} {extra}"><span>{e(link["t"])}</span>{arrow}</{tag}>'


# ───────────────────────── the page
def render(d: dict) -> str:
    d = d or {}
    C = _colours(d.get('palette') or {})
    brand = d.get('brand') or {}
    name = brand.get('name') or ''
    media = d.get('media') or {}
    photos = [p for p in (media.get('photos') or []) if p.get('src') and p.get('w') and p.get('h')]
    meta = {p['src']: p for p in photos}
    used = set()
    seen_h = set()

    def note_h(h):
        if h:
            seen_h.add(str(h).rstrip('/'))

    # pictures that the data gives to a named thing are kept for it
    cat = d.get('catalogue') or {}
    groups = [g for g in (cat.get('groups') or []) if g.get('items')]
    steps = d.get('steps') or {}
    team = d.get('team') or {}
    people = list(team.get('items') or []) + [p for g in (team.get('groups') or []) for p in (g.get('items') or [])]
    projects = [p for p in (d.get('projects') or []) if p.get('title')]
    reserved = set()
    for g in groups:
        for it in g['items']:
            reserved.add(it.get('img'))
    cat_imgs = set(reserved)
    s_imgs = [it.get('img') for it in (steps.get('items') or []) if it.get('title')]
    steps_tiles = bool(s_imgs) and all(meta.get(x) and meta[x]['w'] >= 440 and x not in cat_imgs for x in s_imgs) and len(set(s_imgs)) == len(s_imgs)
    if steps_tiles:
        reserved.update(s_imgs)
    for p in people:
        reserved.add(p.get('img'))
    for p in projects:
        for s in p.get('photos') or []:
            reserved.add(s if isinstance(s, str) else (s or {}).get('src'))

    def take(src, min_w=0):
        """a picture the data assigned: once on the page, never wider than its own pixels"""
        p = meta.get(src)
        if not p or src in used or p['w'] < min_w:
            return None
        used.add(src)
        return p

    def pick(ok, prefer=()):
        pool = [p for p in photos if p['src'] not in used and p['src'] not in reserved and not p.get('small')
                and p.get('role') != 'portrait' and ok(p)]
        for pref in prefer:
            for p in pool:
                if pref(p):
                    used.add(p['src'])
                    return p
        if pool:
            used.add(pool[0]['src'])
            return pool[0]
        return None

    def img(p, cls='', lazy=True, sizes=''):
        return (f'<img class="{cls}" src="{PRE}{e(p["src"])}" width="{p["w"]}" height="{p["h"]}" alt="{e(p.get("alt") or "")}"'
                f'{" loading=lazy" if lazy else ""} decoding="async">')

    role = lambda *r: (lambda p: p.get('role') in r)

    hero_p = pick(lambda p: p['w'] >= 1600 and p['w'] / p['h'] >= 1.2, [lambda p: p.get('role') not in ('people',)]) \
        or pick(lambda p: p['w'] >= 1400 and p['w'] / p['h'] >= 1.2)

    place = d.get('place') or {}
    contact = d.get('contact') or {}
    phone = contact.get('phone') or place.get('phone') or {}
    if isinstance(phone, str):
        phone = {'t': phone}
    email = contact.get('email') or place.get('email') or ''
    socials = [r for r in (contact.get('routes') or []) if r.get('t') and _href(r.get('h')) and not r.get('note')] + \
              [s for s in (place.get('social') or []) if s.get('t') and _href(s.get('h'))]
    nav = [n for n in (d.get('nav') or []) if n.get('t')]
    cta = d.get('cta') or {}
    signin = d.get('signin') or {}
    hero = d.get('hero') or {}
    for n in nav:
        note_h(n.get('h'))
    for l in (cta, signin, hero.get('primary') or {}, hero.get('secondary') or {}):
        note_h(l.get('h'))

    # ── top bar + header
    tb_l = ''
    if phone.get('t'):
        ph = _href(phone.get('h')) or 'tel:' + re.sub(r'[^\d+]', '', phone['t'])
        tb_l += f'<a href="{e(ph)}">{e(phone["t"])}</a>'
    if email:
        tb_l += f'<a href="mailto:{e(email)}">{e(email)}</a>'
    tb_r = ''.join(f'<a href="{e(s["h"])}">{e(s["t"])}</a>' for s in socials[:5])
    topbar = f'<div class="topbar"><div class="wrap"><div class="tl">{tb_l}</div><div class="tr">{tb_r}</div></div></div>' if (tb_l or tb_r) else ''
    logo = (f'<img src="{PRE}{e(brand["logo"])}" alt="{e(name)}">' if brand.get('logo') else f'<span>{e(name)}</span>')
    home = _href(brand.get('home')) or '#top'
    navh = ''.join(f'<a href="{e(_href(n.get("h")) or "#")}">{e(n["t"])}</a>' for n in nav)
    hbtn = _btn(signin, 'sec') + _btn(cta, 'pri')
    header = (f'<header class="hd"><div class="wrap"><a class="logo" href="{e(home)}">{logo}</a>'
              f'<nav class="nav" aria-label="{e(name)}">{navh}</nav><div class="hb">{hbtn}</div>'
              f'<a class="burger" href="#fnav" aria-label="Menu" aria-expanded="false"><i></i><i></i><i></i></a></div></header>')
    menu = (f'<div class="mm-ov" hidden></div><div class="mm" hidden aria-hidden="true"><div class="mm-top"><a class="logo" href="{e(home)}">{logo}</a>'
            f'<button class="mm-x" type="button" aria-label="Close"><i></i><i></i></button></div><nav class="mm-nav">{navh}</nav>'
            f'<div class="mm-b">{hbtn}</div></div>')

    # ── hero: full-bleed photograph, veil from the left and the top, two-tone heading, torn lower edge
    title = (hero.get('title') or name).strip()
    m = re.match(r'^(.{6,}?[.,:;!?—–])\s+(\S.{5,})$', title)
    n_ch = len(title)
    size = 'xl' if n_ch <= 34 else 'lg' if n_ch <= 64 else 'md'
    h1 = (f'<span>{e(m.group(1))}</span> <span class="a">{e(m.group(2))}</span>' if m else f'<span>{e(title)}</span>')
    hb = _btn(hero.get('primary') or cta, 'pri') + _btn(hero.get('secondary'), 'lnk')
    hero_html = (f'<div class="hero{" pic" if hero_p else ""}" id="top">'
                 + (f'<div class="hero-bg">{img(hero_p, "", False)}</div>' if hero_p else '')
                 + topbar + header
                 + f'<div class="wrap hero-in"><div class="hero-col"><h1 class="{size}">{h1}</h1>'
                 + _paras(hero.get('text'), 'lead')
                 + (f'<div class="btns">{hb}</div>' if hb else '')
                 + (f'<p class="hnote">{e(hero["note"])}</p>' if hero.get('note') else '')
                 + '</div></div></div>')

    S = []  # (class, html)

    # ── deep section: figures row + the statement beside a photograph that runs to the page edge
    figs = [f for f in (d.get('figures') or []) if f.get('v')]
    st = d.get('statement') or {}
    about = next((n for n in nav if re.search(r'about|über|sobre|propos|o nama|chi siamo', n['t'], re.I) and _href(n.get('h'))), None)
    body2 = hero.get('text2')
    trust = [t for t in (d.get('trust') or []) if t]
    blk = ''
    if figs:
        blk += '<div class="wrap"><div class="stats">' + ''.join(
            f'<div class="stat"><div class="v">{e(f["v"])}</div>' + (f'<p class="l">{e(f["l"])}</p>' if f.get('l') else '') + '</div>'
            for f in figs[:8]) + '</div></div>'
    if st.get('title') or st.get('text') or body2:
        sp = pick(lambda p: p['w'] >= 1000 and p['h'] >= 760,
                  [lambda p: p['h'] >= p['w'], role('workshop', 'exterior', 'room', 'bar', 'people', 'landscape')])
        t = ''
        if hero.get('kicker'):
            t += f'<p class="kick">{e(hero["kicker"])}</p>'
        if st.get('title'):
            t += f'<h2>{e(st["title"])}</h2>'
        t += _paras(st.get('text'), 'intro') + _paras(body2, 'body')
        if trust:
            t += '<p class="body b">' + ' · '.join(e(x) for x in trust) + '</p>'
        if about:
            t += f'<div class="btns">{_btn(about, "sec")}</div>'
        blk += (f'<div class="split{" haspic" if sp else ""}"><div class="split-t">{t}</div>'
                + (f'<div class="split-p">{img(sp)}</div>' if sp else '') + '</div>')
    if blk:
        S.append(('deep' + (' flush' if 'split haspic' in blk else ''), blk))

    # ── the appeal band on the tint, a photograph held faint behind it
    close = d.get('close') or {}
    if close.get('title') or close.get('text'):
        bp = pick(lambda p: p['w'] >= 1600 and p['w'] / p['h'] >= 1.3, [role('landscape', 'exterior'), lambda p: p['w'] / p['h'] >= 2])
        S.append(('band', (f'<div class="band-bg">{img(bp)}</div>' if bp else '')
                  + '<div class="wrap band-in">' + (f'<h2>{e(close["title"])}</h2>' if close.get('title') else '')
                  + _paras(close.get('text')) + (f'<div class="btns">{_btn(close.get("cta"), "pri")}</div>' if (close.get('cta') or {}).get('t') else '')
                  + '</div>'))
        note_h((close.get('cta') or {}).get('h'))

    # ── catalogue in the reference's article cards: one large, two beside it, the rest in pairs; bare names as its term chips
    if groups:
        cards, chips = [], []
        for g in groups:
            for it in g['items']:
                if not it.get('name'):
                    continue
                rich = any(it.get(k) for k in ('text', 'price', 'prices', 'rows', 'note', 'state')) or meta.get(it.get('img'))
                (cards if rich else chips).append((g, it))
        gh = next((g.get('h') for g in groups if g.get('h')), None)
        head_btn = next((n for n in nav if gh and str(n.get('h') or '').rstrip('/') == str(gh).rstrip('/')), None)

        def card(g, it, big):
            p = take(it.get('img'), 600 if big else 220)
            h = _href(it.get('h'))
            note_h(h)
            nm = f'<a href="{e(h)}">{e(it["name"])}</a>' if h else e(it['name'])
            top = (f'<span class="chip">{e(g["t"])}</span>' if g.get('t') else '') + (f'<span class="chip st">{e(it["state"])}</span>' if it.get('state') else '')
            pr = f'<span class="price">{e(it["price"])}</span>' if it.get('price') else ''
            x = f'<div class="c-top"><div class="chips">{top}</div>{pr}</div>' if (top or pr) else ''
            x += f'<h3>{nm}</h3>'
            if it.get('note'):
                x += f'<p class="c-note">{e(it["note"])}</p>'
            x += _paras(it.get('text'), 'c-text')
            if it.get('prices'):
                x += '<table class="c-prices">' + ''.join(f'<tr><th scope="row">{e(q.get("label"))}</th><td>{e(q.get("price"))}</td></tr>' for q in it['prices']) + '</table>'
            if it.get('rows'):
                x += '<ul class="c-rows">' + ''.join(f'<li>{e(r)}</li>' for r in it['rows']) + '</ul>'
            if h:
                x += f'<a class="c-go" href="{e(h)}" aria-label="{e(it["name"])}" tabindex="-1">{ARROW}</a>'
            kind = ('big' if big else 'row') + ('' if p else ' nopic') + (' long' if (it.get('text') or it.get('rows')) else '')
            return f'<article class="pc {kind}">' + (f'<div class="pc-i">{img(p)}</div>' if p else '') + f'<div class="pc-t">{x}</div></article>'

        grid = ''
        if len(cards) >= 3:
            grid = (f'<div class="pgrid lead3">{card(*cards[0], True)}<div class="pstack">{card(*cards[1], False)}{card(*cards[2], False)}</div></div>'
                    + ('<div class="pgrid">' + ''.join(card(g, it, False) for g, it in cards[3:]) + '</div>' if len(cards) > 3 else ''))
        elif cards:
            grid = f'<div class="pgrid n{len(cards)}">' + ''.join(card(g, it, True) for g, it in cards) + '</div>'
        chip_h = ''
        for g, it in chips:
            h = _href(it.get('h'))
            note_h(h)
            chip_h += f'<a class="term" href="{e(h)}">{e(it["name"])}</a>' if h else f'<span class="term">{e(it["name"])}</span>'
        tail = ''
        if chip_h or cat.get('note'):
            tail = '<div class="ptail">' + (f'<div class="terms">{chip_h}</div>' if chip_h else '') + (f'<p class="pnote">{e(cat["note"])}</p>' if cat.get('note') else '') + '</div>'
        S.append(('white cat', '<div class="wrap"><div class="shead"><div>'
                  + (f'<h2>{e(cat["title"])}</h2>' if cat.get('title') else '') + _paras(cat.get('text'), 'sub')
                  + '</div>' + (_btn(head_btn, 'pri') if head_btn else '') + '</div>' + grid + tail + '</div>'))

    # ── plans (the reference prices nothing on these pages): its deep numbered card, the price in the display face
    plans = d.get('plans') or {}
    pl = [p for p in (plans.get('items') or []) if p.get('name') or p.get('price')]
    if pl:
        def plan(p):
            x = (f'<p class="num">{e(p["name"])}</p>' if p.get('name') else '')
            if p.get('price'):
                x += f'<p class="pp">{e(p["price"])}' + (f' <span>{e(p["per"])}</span>' if p.get('per') else '') + '</p>'
            x += _paras(p.get('line'))
            if p.get('rows'):
                x += '<ul class="c-rows">' + ''.join(f'<li>{e(r)}</li>' for r in p['rows']) + '</ul>'
            x += _btn(p.get('cta'), 'pri' if p.get('marked') else 'sec', 'wide')
            return f'<div class="nc plan{" marked" if p.get("marked") else ""}">{x}</div>'
        S.append(('white plans', '<div class="wrap"><div class="shead"><div>' + (f'<h2>{e(plans["title"])}</h2>' if plans.get('title') else '')
                  + _paras(plans.get('text'), 'sub') + f'</div></div><div class="ncs n{min(len(pl), 4)}">' + ''.join(plan(p) for p in pl) + '</div>'
                  + (f'<p class="pnote">{e(plans["note"])}</p>' if plans.get('note') else '') + '</div>'))

    # ── features in white cards on the tint→accent ground, the quotes under them on the same ground
    feats = d.get('features') or {}
    fi = [f for f in (feats.get('items') or []) if f.get('t')]
    cat_names = {it.get('name') for g in groups for it in g['items']}
    if fi and not any(f.get('d') for f in fi) and all(f['t'] in cat_names for f in fi):
        fi = []   # the same names already stand in the catalogue, with nothing more said here
    quotes = [q for q in (d.get('quotes') or []) if q.get('q')]
    if fi:
        S.append(('grad', '<div class="wrap">' + (f'<h2 class="ctr">{e(feats["title"])}</h2>' if feats.get('title') else '')
                  + _paras(feats.get('text'), 'ctr-sub')
                  + f'<div class="wcs{" few" if len(fi) < 3 else ""}">' + ''.join(f'<div class="wc"><h3>{e(f["t"])}</h3>{_paras(f.get("d"))}</div>' for f in fi) + '</div></div>'))
    if quotes:
        sl = ''.join(f'<figure class="q"><blockquote><p>{e(q["q"])}</p></blockquote>'
                     + (f'<figcaption><b>{e(q["name"])}</b>' + (f'<span>{e(q["role"])}</span>' if q.get('role') else '') + '</figcaption>' if q.get('name') else '')
                     + '</figure>' for q in quotes)
        ctl = (f'<button class="qb prev" type="button" aria-label="‹">{ARROW}</button><button class="qb next" type="button" aria-label="›">{ARROW}</button>' if len(quotes) > 1 else '')
        S.append(('quotes' + (' aftergrad' if fi else ''), f'<div class="wrap qwrap"><div class="qmark" aria-hidden="true">“</div><div class="qs" tabindex="0">{sl}</div>{ctl}</div>'))

    # ── steps on the accent ground: photograph tiles when every step has its own picture, the deep numbered cards when not
    si = [s for s in (steps.get('items') or []) if s.get('title')]
    if si:
        all_pic = steps_tiles
        head = (f'<h2 class="ctr">{e(steps["title"])}</h2>' if steps.get('title') else '') + _paras(steps.get('text'), 'ctr-sub')
        if all_pic:
            def tile(s):
                p = take(s['img'])
                c = s.get('cta') or {}
                h = _href(c.get('h'))
                note_h(h)
                inner = (f'<div class="ti">{img(p)}</div><div class="tv"></div>'
                         + (f'<span class="tgo">{ARROW_UP}</span>' if h else '')
                         + f'<div class="tt"><h3>{e(s["title"])}</h3>{_paras(s.get("text"))}</div>')
                return f'<a class="tile" href="{e(h)}">{inner}</a>' if h else f'<div class="tile">{inner}</div>'
            n = len(si)
            S.append(('accent', f'<div class="wrap">{head}<div class="tiles t{n if n < 5 else 3 + n % 3}">' + ''.join(tile(s) for s in si) + '</div></div>'))
        else:
            def nc(i, s):
                c = s.get('cta') or {}
                note_h(c.get('h'))
                return (f'<div class="nc"><p class="num">{e(s.get("k") or "%02d" % (i + 1))}</p><h3>{e(s["title"])}</h3>{_paras(s.get("text"))}'
                        + _btn(c, 'lnk') + '</div>')
            S.append(('accent', f'<div class="wrap">{head}<div class="ncs n{min(len(si), 4)}">' + ''.join(nc(i, s) for i, s in enumerate(si)) + '</div></div>'))

    # ── projects: the reference's photograph tiles, on the pale ground
    pt = []
    for p in projects:
        ph = None
        for s in p.get('photos') or []:
            ph = take(s if isinstance(s, str) else (s or {}).get('src'), 440)
            if ph:
                break
        if ph:
            pt.append((p, ph))
    if pt:
        def ptile(p, ph):
            h = _href(p.get('h'))
            note_h(h)
            inner = (f'<div class="ti">{img(ph)}</div><div class="tv"></div>' + (f'<span class="tgo">{ARROW_UP}</span>' if h else '')
                     + f'<div class="tt"><h3>{e(p["title"])}</h3>{_paras(p.get("text"))}</div>')
            return f'<a class="tile" href="{e(h)}">{inner}</a>' if h else f'<div class="tile">{inner}</div>'
        n = len(pt)
        S.append(('pale', f'<div class="wrap"><div class="tiles t{n if n < 5 else 3 + n % 3}">' + ''.join(ptile(*x) for x in pt) + '</div></div>'))

    # ── people: picture-topped cards when they have portraits; in type over a deep photograph band when they have none
    if people or team.get('text'):
        with_p = [(p, take(p.get('img'), 400)) for p in people]
        if any(ph for _, ph in with_p):
            def person(p, ph):
                x = f'<h3>{e(p.get("name"))}</h3>' + (f'<p class="role">{e(p["role"])}</p>' if p.get('role') else '') + _paras(p.get('text'))
                ct = ''.join(f'<a href="{e(h)}">{e(t)}</a>' for t, h in ((p.get('phone'), 'tel:' + re.sub(r'[^\d+]', '', str(p.get('phone') or ''))), (p.get('email'), 'mailto:' + str(p.get('email') or ''))) if t)
                return f'<div class="tc">' + (f'<div class="tc-i">{img(ph)}</div>' if ph else '') + f'<div class="tc-t">{x}' + (f'<p class="tc-c">{ct}</p>' if ct else '') + '</div></div>'
            S.append(('pale team', '<div class="wrap"><div class="shead"><div>' + (f'<h2>{e(team["title"])}</h2>' if team.get('title') else '')
                      + _paras(team.get('text'), 'sub') + '</div></div><div class="tcs">' + ''.join(person(p, ph) for p, ph in with_p) + '</div></div>'))
        else:
            tp = pick(lambda p: p['w'] >= 1600 and p['w'] / p['h'] >= 1.2, [role('people'), role('workshop', 'room', 'exterior')])
            ppl = ''.join(f'<li><b>{e(p.get("name"))}</b>' + (f'<span>{e(p["role"])}</span>' if p.get('role') else '') + '</li>' for p in people if p.get('name'))
            S.append(('dband' + (' pic' if tp else ''), (f'<div class="band-bg">{img(tp)}</div>' if tp else '') + '<div class="wrap band-in">'
                      + (f'<h2>{e(team["title"])}</h2>' if team.get('title') else '') + _paras(team.get('text'))
                      + (f'<ul class="ppl">{ppl}</ul>' if ppl else '') + '</div>'))

    # ── questions: the reference's ruled rows with a plus
    faq = d.get('faq') or {}
    qa = [q for q in (faq.get('items') or []) if q.get('q') and q.get('a')]
    if qa:
        S.append(('white faq', '<div class="wrap">' + (f'<h2 class="h40">{e(faq["title"])}</h2>' if faq.get('title') else '') + '<div class="faqs">'
                  + ''.join(f'<details class="fq"><summary><span>{e(q["q"])}</span><i aria-hidden="true"></i></summary><div class="fa">{_paras(q["a"])}</div></details>' for q in qa)
                  + '</div></div>'))

    # ── where and how: doors, ways to reach, credentials — beside a photograph that runs to the page edge
    locs = [l for l in (d.get('locations') or []) if l.get('name') or l.get('address')]
    if not locs and (place.get('address') or place.get('hours')):
        locs = [dict(address=place.get('address'), phone=(place.get('phone') or {}).get('t') if isinstance(place.get('phone'), dict) else place.get('phone'),
                     email=place.get('email'), hours=place.get('hours') or [])]
    routes = [r for r in (contact.get('routes') or []) if r.get('t') and r.get('note')]
    creds = [c for c in (d.get('credentials') or []) if c.get('t')]
    if locs or routes or creds:
        x = ''
        for l in locs:
            a = l.get('address') or {}
            if isinstance(a, str):
                a = {'street': a}
            line = ', '.join(str(a[k]) for k in ('street', 'city', 'region', 'postcode', 'country') if a.get(k))
            lh = _href(l.get('h'))
            note_h(lh)
            nm = (f'<a href="{e(lh)}">{e(l["name"])}</a>' if lh else e(l['name'])) if l.get('name') else ''
            x += '<div class="loc">' + (f'<h3>{nm}</h3>' if nm else '') + (f'<p class="addr">{e(line)}</p>' if line else '')
            ct = ''
            if l.get('phone'):
                ct += f'<a href="tel:{e(re.sub(r"[^0-9+]", "", str(l["phone"])))}">{e(l["phone"])}</a>'
            if l.get('email'):
                ct += f'<a href="mailto:{e(l["email"])}">{e(l["email"])}</a>'
            x += f'<p class="lc">{ct}</p>' if ct else ''
            hrs = [h for h in (l.get('hours') or []) if h.get('days')]
            if hrs:
                x += '<table class="hours">' + ''.join(f'<tr><th scope="row">{e(h["days"])}</th><td>{e(h.get("open") or "")}{"–" + e(h["close"]) if h.get("close") else ""}</td></tr>' for h in hrs) + '</table>'
            x += _paras(l.get('note'), 'ln')
            x += '</div>'
        rows = ''
        for r in routes:
            h = _href(r.get('h'))
            rows += '<p class="rt"><b>' + (f'<a href="{e(h)}">{e(r["t"])}</a>' if h else e(r['t'])) + f'</b> {e(r["note"])}</p>'
        if phone.get('note'):
            rows = f'<p class="rt"><b>{e(phone.get("t"))}</b> {e(phone["note"])}</p>' + rows
        for c in creds:
            h = _href(c.get('h'))
            rows += '<p class="rt"><b>' + (f'<a href="{e(h)}">{e(c["t"])}</a>' if h else e(c['t'])) + '</b>' + (f' {e(c["year"])}' if c.get('year') else '') + (f' {e(c["text"])}' if c.get('text') else '') + '</p>'
        lp = pick(lambda p: p['w'] >= 1000 and p['h'] >= 760, [role('exterior', 'landscape', 'room', 'workshop', 'bar')])
        S.append(('alt visit' + (' haspic' if lp else ''), (f'<div class="split-p">{img(lp)}</div>' if lp else '')
                  + f'<div class="split-t"><div class="locs">{x}</div>' + (f'<div class="rts">{rows}</div>' if rows else '') + '</div>'))

    # ── further pages not linked above: the reference's two-column dotted list
    more = [l for l in (d.get('links') or []) if l.get('t') and _href(l.get('h')) and str(l['h']).rstrip('/') not in seen_h]
    if more:
        S.append(('pale more', '<div class="wrap"><div class="fl">' + ''.join(
            f'<div class="fli"><h3><a href="{e(l["h"])}">{e(l["t"])}</a></h3>{_paras(l.get("d"))}</div>' for l in more) + '</div></div>'))

    main = ''
    for i, (cls, inner) in enumerate(S):
        main += f'<section class="s {cls}{" first" if i == 0 else ""}{" last" if i == len(S) - 1 else ""}">{inner}</section>'

    # ── foot
    foot = d.get('foot') or {}
    words = name.split()
    slogan = (f'<span>{e(" ".join(words[:-1]))}</span> <span class="a">{e(words[-1])}</span>' if len(words) > 1 else f'<span>{e(name)}</span>')
    fnav = ''.join(f'<a href="{e(_href(n.get("h")) or "#")}">{e(n["t"])}</a>' for n in nav)
    ftxt = ''.join(f'<p>{e(x.strip())}</p>' for x in re.split(r'\s+·\s+', foot.get('text') or '') if x.strip())
    form = contact.get('form') or {}
    fbtn = _btn({'t': form.get('t'), 'h': form.get('h')}, 'pri', 'wide') if form.get('t') and _href(form.get('h')) else \
        (_btn({'t': email, 'h': 'mailto:' + email}, 'pri', 'wide nocap') if email else _btn(cta, 'pri', 'wide'))
    fright = ''
    if phone.get('t'):
        ph = _href(phone.get('h')) or 'tel:' + re.sub(r'[^\d+]', '', phone['t'])
        fright += f'<h3><a href="{e(ph)}">{e(phone["t"])}</a></h3>' + (f'<p>{e(phone["note"])}</p>' if phone.get('note') and not (locs or routes or creds) else '')
    fright += fbtn
    soc = ''.join(f'<a href="{e(s["h"])}">{e(s["t"])}</a>' for s in socials)
    legal = [x.strip() for x in re.split(r'\s+·\s+', foot.get('legal') or '') if x.strip()]
    flinks = ''.join(f'<a href="{e(_href(l.get("h")) or "#")}">{e(l["t"])}</a>' for l in (foot.get('links') or []) if l.get('t'))
    footer = (f'<footer class="ft{"" if S else " nomain"}"><div class="wrap"><div class="f1"><p class="slogan">{slogan}</p></div>'
              f'<div class="f2"><nav class="fc" id="fnav" aria-label="{e(name)}">{fnav}</nav><div class="fc fct">{ftxt}</div><div class="fr">{fright}</div></div>'
              + (f'<div class="f3">{soc}</div>' if soc else '')
              + '<div class="f4"><div class="lg">' + ''.join(f'<p>{e(x)}</p>' for x in legal) + f'</div><div class="fl2">{flinks}</div></div></div></footer>')

    css = CSS
    for k, v in dict(GROUND=C['ground'], INK=C['ink'], DARKER=C['darker'], DARK=C['dark'], ACCDK=C['acc_dk'], ACCLT=C['acc_lt'], ONACC=C['on_acc'],
                     ACC=C['acc'], TINT=C['tint'], PALE=C['pale'], CARD=C['card'], ALT=C['alt'], RULE=C['rule'],
                     VEIL9=_rgba(C['darker'], .9), VEIL8=_rgba(C['darker'], .8), VEIL7=_rgba(C['darker'], .72), VEIL5=_rgba(C['darker'], .62),
                     VEIL0=_rgba(C['darker'], 0), VEIL1=_rgba(C['darker'], .12), W8=_rgba('#ffffff', .82), W2=_rgba('#ffffff', .2),
                     TORNB=_torn(7, True), TORNT=_torn(23, False),
                     GRAD=(f'linear-gradient({C["tint"]},{C["acc"]})' if C['light_acc'] else f'linear-gradient({C["tint"]} 0,{C["tint"]} 30%,{C["acc"]} 100%)'),
                     QINK=(C['dark'] if C['light_acc'] else C['on_acc']), QBG=('transparent' if C['light_acc'] else C['acc'])).items():
        css = css.replace('{' + k + '}', v)
    desc = hero.get('text') or ''
    return (f'<!doctype html><html lang="{e(d.get("lang") or "en")}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{e(name)}</title><meta name="description" content="{e(desc[:300])}">'
            f'<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            f'<link rel="stylesheet" href="{FONTS}"><style>{css}</style></head><body>{hero_html}<main>{main}</main>{footer}{menu}<script>{JS}</script></body></html>')


CSS = r"""
*,*::before,*::after{box-sizing:border-box}html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{margin:0;background:{GROUND};color:{INK};font:400 18px/27px "DM Sans",system-ui,sans-serif;-webkit-font-smoothing:antialiased;overflow-x:hidden}
img{display:block;max-width:100%;height:auto}a{color:inherit;text-decoration:none}p{margin:0}h1,h2,h3{margin:0;font-family:Rubik,"DM Sans",sans-serif;font-weight:800;text-wrap:balance;overflow-wrap:break-word}
table{border-collapse:collapse}ul{margin:0;padding:0;list-style:none}
:focus-visible{outline:3px solid {ACCLT};outline-offset:3px}.hero :focus-visible,.deep :focus-visible,.ft :focus-visible,.mm :focus-visible,.pc :focus-visible,.nc :focus-visible,.dband :focus-visible,.tile:focus-visible{outline-color:#fff}
.accent :focus-visible,.topbar :focus-visible{outline-color:{ONACC}}
.wrap{padding:0 27px;margin:0 auto;max-width:1920px}
.arw{width:18px;height:18px;flex:none;transition:transform .15s cubic-bezier(.4,0,.2,1)}
/* buttons: 54 high, square, 2px edge, .15s */
.btn{display:inline-flex;align-items:center;justify-content:center;gap:9px;min-height:54px;padding:11.5px 18px;border:2px solid transparent;font:700 15.75px/22.5px "DM Sans",sans-serif;text-transform:capitalize;text-align:center;transition:all .15s cubic-bezier(.4,0,.2,1);overflow-wrap:anywhere;max-width:100%}
.btn.nocap{text-transform:none}.btn.pri{background:{ACC};color:{ONACC}}.btn.sec{background:{TINT};color:{DARK}}.btn.lnk{padding-left:0;padding-right:0;color:inherit}.btn.lnk .arw{color:{ACCDK}}
.btn.wide{width:100%}a.btn.pri:hover,a.btn.sec:hover{border-color:currentColor}a.btn:hover .arw{transform:translateX(4px)}a.btn:active{transform:translateY(1px)}
.btns{display:flex;flex-wrap:wrap;align-items:center;gap:9px 22px}
/* top bar */
.topbar{position:relative;z-index:3;background:{ACC};color:{ONACC};font-size:15.75px;line-height:22.5px;padding:18px 0}
.topbar .wrap{display:flex;justify-content:space-between;gap:27px}.topbar .tl,.topbar .tr{display:flex;gap:22px;flex-wrap:wrap}.topbar a:hover{text-decoration:underline}
/* header: lies over the opening picture, leaves with the page (not pinned) */
.hd{position:relative;z-index:3;color:#fff}.hd .wrap{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:18px;padding-top:36px;padding-bottom:18px}
.logo{font:800 31px/1 Rubik,sans-serif;letter-spacing:-.03em;text-transform:uppercase;max-width:300px;display:inline-block}.logo img{max-height:94px;width:auto}
.nav{display:flex;flex-wrap:wrap;justify-content:center;gap:0 14px}.nav a{font:600 15.75px/22.5px "DM Sans",sans-serif;padding:11.25px 6.75px}.nav a:hover{text-decoration:underline;text-decoration-color:{ACCDK};text-underline-offset:5px;text-decoration-thickness:2px}
.hb{display:flex;gap:9px;justify-content:flex-end}.burger{display:none}
/* hero */
.hero{position:relative;z-index:2;background:{DARK};color:#fff;min-height:855px;display:flex;flex-direction:column;margin-bottom:-75px;
-webkit-mask-image:linear-gradient(#000 0,#000 calc(100% - 75px),transparent calc(100% - 75px)),{TORNB};mask-image:linear-gradient(#000 0,#000 calc(100% - 75px),transparent calc(100% - 75px)),{TORNB};
-webkit-mask-size:100% 100%,1596px 75px;mask-size:100% 100%,1596px 75px;-webkit-mask-position:0 0,0 100%;mask-position:0 0,0 100%;-webkit-mask-repeat:no-repeat,repeat-x;mask-repeat:no-repeat,repeat-x}
.hero:not(.pic){min-height:0}.hero:not(.pic) .hero-in{padding-bottom:112px}.hero:not(.pic)+main .deep.first{padding-top:75px}
.hero-bg{position:absolute;inset:0;z-index:0}.hero-bg img{width:100%;height:100%;object-fit:cover}
.hero-bg::after{content:"";position:absolute;inset:0;background:linear-gradient(to right,{VEIL9} 0,{VEIL8} 42%,{VEIL0} 78%),linear-gradient({VEIL8} 0,{VEIL0} 45%),{VEIL1}}
.hero-in{position:relative;z-index:1;width:100%;flex:1;display:flex;align-items:center;padding-top:67.5px;padding-bottom:142.5px}
.hero-col{width:50%;max-width:820px;min-width:0}
h1{text-transform:uppercase;letter-spacing:-.01em}h1 span{display:block}h1 .a{color:{ACCDK}}
h1.xl{font-size:81px;line-height:67.5px}h1.lg{font-size:63px;line-height:56px}h1.md{font-size:49.5px;line-height:47px}
.lead{font-size:22.5px;line-height:31.5px;font-weight:600;margin-top:18px}.hero .btns{margin-top:54px}.hnote{font:500 13.5px/18px "DM Sans",sans-serif;letter-spacing:.675px;text-transform:uppercase;margin-top:22px}
/* sections */
.s{position:relative;padding:67.5px 0}.s.first{padding-top:142.5px}.s.last{padding-bottom:142.5px}
h2{font-size:54px;line-height:54px;letter-spacing:-1.35px;text-transform:uppercase}h2.h40{font-size:40.5px;line-height:45px;letter-spacing:-1px}
h3{font-size:22.5px;line-height:31.5px;letter-spacing:-.5625px}
.ctr{text-align:center}.ctr-sub{text-align:center;max-width:909px;margin:18px auto 0;font-size:20.25px;line-height:31.5px}
.shead{display:flex;justify-content:space-between;align-items:flex-start;gap:27px}.shead .sub{font-size:20.25px;line-height:31.5px;max-width:778px;margin-top:9px}.shead .btn{flex:none}
/* deep section: figures, then statement beside a photograph that runs to the page edge and to the section's foot */
.deep{background:{DARK};color:#f8f8f8;padding-top:60px}.deep.first{padding-top:135px}.deep.flush{padding-bottom:0}
.stats{display:flex;flex-wrap:wrap;gap:36px 45px}.stat{flex:1 1 200px;border-left:2px solid {ACCDK};padding-left:22.5px;min-width:0}
.stat .v{font:800 54px/54px Rubik,sans-serif;letter-spacing:-1.35px;overflow-wrap:anywhere}.stat .l{font:500 13.5px/18px "DM Sans",sans-serif;letter-spacing:.675px;text-transform:uppercase;margin-top:4px}
.split{display:grid;grid-template-columns:1fr 1fr;align-items:stretch}.stats+.split,.wrap+.split{margin-top:67.5px}
.split-t{padding:90px 63px 90px 27px;min-width:0;align-self:center}.split:not(.haspic) .split-t{grid-column:1/-1;max-width:960px}
.split-p{position:relative;min-height:520px}.split-p img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.kick{font:600 15.75px/22.5px "DM Sans",sans-serif;letter-spacing:1.575px;text-transform:uppercase;color:{ACCDK};margin-bottom:22.5px;display:flex;gap:9px;align-items:center}
.kick::before{content:"";width:11px;height:11px;border:2px solid currentColor;border-radius:50%;flex:none}
.intro{font-size:22.5px;line-height:36.5625px;margin-top:18px}.body{margin-top:18px}.body.b{font-weight:700}.split-t .btns{margin-top:45px}
/* band on the tint */
.band,.dband{padding:99px 0;overflow:hidden;text-align:center}.band{background:{TINT};color:{DARKER}}
.band-bg{position:absolute;inset:0}.band-bg img{width:100%;height:100%;object-fit:cover}.band .band-bg{opacity:.1}
.band-in{position:relative;max-width:954px}.band h2,.dband h2{font-size:40.5px;line-height:45px;letter-spacing:-1.0125px;text-transform:none}.band-in p{margin-top:18px}.band .btns,.dband .btns{justify-content:center;margin-top:36px}
.dband{background:{DARK};color:#fff}.dband .band-bg::after{content:"";position:absolute;inset:0;background:{VEIL8}}.dband h2{color:{ACCDK};text-transform:uppercase}.dband .band-in p{font-size:20.25px;line-height:31.5px}
.ppl{display:flex;flex-wrap:wrap;justify-content:center;gap:9px 45px;margin-top:31.5px}.ppl b{display:block;font:800 22.5px/31.5px Rubik,sans-serif;letter-spacing:-.5625px}.ppl span{font:500 13.5px/18px "DM Sans",sans-serif;letter-spacing:.675px;text-transform:uppercase;color:{ACCDK}}
/* catalogue cards */
.white{background:{GROUND}}.alt{background:{ALT}}.pale{background:{PALE};color:{DARK}}
.pgrid{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:45px}.pgrid+.pgrid{margin-top:18px}.pstack{display:grid;gap:18px;grid-auto-rows:1fr}.pgrid.n1{grid-template-columns:1fr}
.pc{position:relative;background:{DARK};color:#fff;display:flex;flex-direction:column;transition:background-color .15s cubic-bezier(.4,0,.2,1);min-width:0}.pc:hover{background:{DARKER}}
.pc-i{overflow:hidden;flex:none}.pc-i img{width:100%;height:100%;object-fit:cover;transition:transform .3s cubic-bezier(.4,0,.2,1)}.pc:hover .pc-i img{transform:scale(1.1)}
.pc.big .pc-i{height:360px;flex:1 0 360px}.pc.row{flex-direction:row}.pc.row .pc-i{width:33.333%;position:relative}.pc.row .pc-i img{position:absolute;inset:0}
.pc-t{padding:22.5px;display:flex;flex-direction:column;flex:1;min-width:0}
.c-top{display:flex;justify-content:space-between;align-items:flex-start;gap:18px;margin-bottom:13.5px}.chips{display:flex;flex-wrap:wrap;gap:9px}
.chip{background:{ACC};color:{ONACC};font:600 13.5px/18px "DM Sans",sans-serif;padding:4.5px 9px}.chip.st{background:{TINT};color:{DARK}}.pc:hover .chip{background:{TINT};color:{DARK}}
.price{font:800 22.5px/27px Rubik,sans-serif;color:{ACCDK};white-space:nowrap}
.pc h3 a::after{content:"";position:absolute;inset:0}.pc:hover h3 a{text-decoration:underline}.pc.big h3{font-size:33.75px;line-height:40.5px;letter-spacing:-.84375px}
.c-note{font:500 13.5px/18px "DM Sans",sans-serif;letter-spacing:.3375px;text-transform:uppercase;color:{ACCDK};margin-top:6px}
.c-text{font-size:15.75px;line-height:22.5px;margin-top:11px;color:{W8}}
.c-prices{width:100%;margin-top:13.5px;font-size:15.75px;line-height:22.5px}.c-prices th{text-align:left;font-weight:400;padding:6px 9px 6px 0}.c-prices td{text-align:right;font-weight:700;padding:6px 0;white-space:nowrap}.c-prices tr{border-top:1px solid {W2}}
.c-rows{margin-top:13.5px;font-size:15.75px;line-height:22.5px}.c-rows li{position:relative;padding-left:18px;margin-top:4.5px}.c-rows li::before{content:"";position:absolute;left:2px;top:9px;width:4px;height:4px;border-radius:50%;background:{ACCDK}}
.c-go{display:inline-flex;margin-top:auto;padding-top:18px;color:{ACCDK};align-self:flex-start}.pc:hover .c-go .arw{transform:translateX(4px)}
.ptail{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:18px 27px;margin-top:45px}.terms{display:flex;flex-wrap:wrap;gap:9px}
.term{border:2px solid {TINT};padding:4.5px 9px;font:500 15.75px/22.5px "DM Sans",sans-serif}a.term:hover{background:{TINT};color:{DARK}}.pnote{font-weight:700}.plans .pnote{margin-top:27px;font-weight:400;font-size:15.75px}
/* features: white cards on the tint→accent ground; quotes under them */
.grad{background:{GRAD};color:{DARK}}.wcs{display:flex;flex-wrap:wrap;justify-content:center;gap:45px;margin-top:45px}
.wc{flex:0 1 calc((100% - 90px)/3);min-width:260px;background:{CARD};color:{DARK};padding:36px 36px;text-align:center;box-shadow:0 25px 50px -12px rgba(0,0,0,.25)}.wcs.few .wc{flex-basis:calc((100% - 45px)/2)}
.wc p{font-size:15.75px;line-height:22.5px;margin-top:13.5px}
.quotes{background:{QBG};color:{QINK};padding:67.5px 0 45px}.quotes.aftergrad{margin-top:-1px}
.qwrap{position:relative}.qmark{font:800 108px/60px Rubik,sans-serif;text-align:center;height:45px;margin-bottom:36px}
.qs{display:flex;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none;gap:20px}.qs::-webkit-scrollbar{display:none}
.q{flex:0 0 100%;scroll-snap-align:center;margin:0;padding:0 90px;text-align:center;display:flex;flex-direction:column;align-items:center}
.q blockquote{margin:0;max-width:909px}.q blockquote p{font-size:27px;line-height:40.5px}.q figcaption{margin-top:31.5px;font-size:15.75px;line-height:22.5px;text-transform:uppercase}.q figcaption b{display:block;font-weight:700}
.qb{position:absolute;top:50%;width:54px;height:54px;border:0;background:{ACC};color:{ONACC};display:flex;align-items:center;justify-content:center;cursor:pointer;transition:transform .15s cubic-bezier(.4,0,.2,1);box-shadow:0 0 0 2px {ONACC} inset}
.qb.prev{left:36px}.qb.next{right:36px}.qb.prev .arw{transform:rotate(180deg)}.qb:hover{transform:scale(1.06)}.qb:active{transform:scale(.96)}
/* steps on the accent ground */
.accent{background:{ACC};color:{ONACC};padding:45px 0 67.5px}.accent.first{padding-top:142.5px}
.tiles{display:grid;grid-template-columns:repeat(12,1fr);gap:18px;margin-top:45px}.pale .tiles{margin-top:0}.tile{grid-column:span 4;position:relative;min-height:340px;display:flex;align-items:flex-end;color:#fff;overflow:hidden;box-shadow:0 10px 15px -3px rgba(0,0,0,.2)}
.tiles.t1 .tile{grid-column:span 12}.tiles.t2 .tile,.tiles.t4 .tile,.tiles.t5 .tile:nth-child(-n+2){grid-column:span 6}.tiles.t4 .tile:nth-child(n+5){grid-column:span 4}
.ti{position:absolute;inset:0}.ti img{width:100%;height:100%;object-fit:cover;transition:transform .3s cubic-bezier(.4,0,.2,1)}.tv{position:absolute;inset:0;background:linear-gradient(to top,{VEIL9} 0,{VEIL5} 55%,{VEIL1} 100%);transition:background-color .3s cubic-bezier(.4,0,.2,1)}
a.tile:hover .ti img{transform:scale(1.05)}a.tile:hover .tv{background-color:{VEIL5}}
.tt{position:relative;padding:31.5px;padding-right:90px;min-width:0}.tt h3{font-size:33.75px;line-height:40.5px;letter-spacing:-.84375px}.tt p{margin-top:13.5px;color:#fff}
.tgo{position:absolute;top:31.5px;right:31.5px;width:45px;height:45px;background:{ACC};color:{ONACC};display:flex;align-items:center;justify-content:center}
.ncs{display:flex;flex-wrap:wrap;justify-content:center;gap:22.5px;max-width:1206px;margin:45px auto 0}
.nc{flex:0 1 calc((100% - 67.5px)/4);min-width:240px;background:{DARK};color:#fff;padding:36px;text-align:center;display:flex;flex-direction:column;align-items:center}
.ncs.n1 .nc{flex-basis:480px}.ncs.n2 .nc{flex-basis:calc((100% - 22.5px)/2)}.ncs.n3 .nc{flex-basis:calc((100% - 45px)/3)}
.num{font:700 13.5px/18px "DM Sans",sans-serif;letter-spacing:.675px;text-transform:uppercase;color:{ACCDK};margin-bottom:13.5px}.nc h3{margin-bottom:18px}.nc p{font-size:15.75px;line-height:22.5px}.nc .btn.lnk{margin-top:auto;padding-top:18px;min-height:0}
.plan{text-align:left;align-items:stretch}.plan.marked{background:{DARKER};outline:4px solid {ACCDK};outline-offset:-4px}.pp{font:800 40.5px/45px Rubik,sans-serif!important;letter-spacing:-1px;margin-bottom:13.5px;overflow-wrap:anywhere}.pp span{display:block;margin-top:4px;font:500 13.5px/18px "DM Sans",sans-serif;letter-spacing:.675px;text-transform:uppercase}
.plan .c-rows{margin-bottom:27px}.plan .btn{margin-top:auto}.plan>p+p{margin-top:9px}
/* people */
.tcs{display:grid;grid-template-columns:repeat(3,1fr);gap:27px;margin-top:45px}.tc{background:{CARD};color:{DARK};min-width:0}.tc-i{height:370px;overflow:hidden}.tc-i img{width:100%;height:100%;object-fit:cover}
.tc-t{padding:27px}.tc .role{font:500 13.5px/18px "DM Sans",sans-serif;letter-spacing:.675px;text-transform:uppercase;margin-top:2px}.tc-t p:not(.role){font-size:15.75px;line-height:22.5px;margin-top:11px}.tc-c a{display:block;font-weight:700}
/* questions */
.faqs{margin-top:13.5px}.fq{border-bottom:1px solid {RULE};margin-bottom:9px}.fq summary{display:flex;justify-content:space-between;align-items:center;gap:18px;padding:9px 0;cursor:pointer;list-style:none}.fq summary::-webkit-details-marker{display:none}
.fq i{position:relative;width:18px;height:18px;flex:none;transition:transform .15s cubic-bezier(.4,0,.2,1)}.fq i::before,.fq i::after{content:"";position:absolute;left:0;right:0;top:8px;height:2px;background:currentColor}.fq i::after{transform:rotate(90deg)}.fq[open] i{transform:rotate(45deg)}
.fa{padding:0 13.5px 9px}.fa p{margin-bottom:13.5px}
/* where and how */
.visit{padding:0;display:grid;grid-template-columns:1fr 1fr}.visit .split-t{padding:90px 27px 90px 63px}.visit:not(.haspic){display:block}.visit:not(.haspic) .split-t{padding:67.5px 27px;max-width:1100px}.visit.last .split-t{padding-bottom:165px}
.locs{display:grid;gap:36px}.loc h3{font-size:33.75px;line-height:40.5px;letter-spacing:-.84375px;text-transform:uppercase}.addr{font-size:20.25px;line-height:31.5px;margin-top:9px}.loc:not(:has(h3)) .addr{font:800 33.75px/40.5px Rubik,sans-serif;letter-spacing:-.84375px}
.lc{display:flex;flex-wrap:wrap;gap:4px 22px;font-weight:700;margin-top:9px}.lc a:hover,.rt a:hover,.fli a:hover,.tc-c a:hover{text-decoration:underline}.ln{font-size:15.75px;line-height:22.5px;margin-top:11px}
.hours{margin-top:11px;font-size:15.75px}.hours th{text-align:left;font-weight:700;padding:4px 22px 4px 0}.hours tr{border-top:1px solid {RULE}}.loc h3 a{text-decoration:underline;text-decoration-color:{ACCLT};text-decoration-thickness:3px;text-underline-offset:5px}
.rts{margin-top:36px;padding-top:27px;border-top:1px solid {RULE}}.rt{margin-top:13.5px;font-size:15.75px;line-height:22.5px}.rt b{margin-right:4px}.rt a{text-decoration:underline;text-decoration-color:{ACCLT};text-underline-offset:3px}
/* further pages */
.fl{display:grid;grid-template-columns:1fr 1fr;gap:45px 90px}.fli{position:relative;padding-left:45px;min-width:0}.fli::before{content:"";position:absolute;left:0;top:9px;width:13px;height:13px;border-radius:50%;background:{TINT};box-shadow:0 0 0 4px {CARD}}.fli p{margin-top:13.5px}
/* foot */
.ft{position:relative;z-index:2;margin-top:-75px;padding-top:150px;color:#fff;background:linear-gradient(to top,{DARKER},{DARK});
-webkit-mask-image:linear-gradient(transparent 0,transparent 75px,#000 75px),{TORNT};mask-image:linear-gradient(transparent 0,transparent 75px,#000 75px),{TORNT};-webkit-mask-size:100% 100%,1596px 75px;mask-size:100% 100%,1596px 75px;-webkit-mask-position:0 0,0 0;mask-position:0 0,0 0;-webkit-mask-repeat:no-repeat,repeat-x;mask-repeat:no-repeat,repeat-x}
.slogan{font:800 54px/54px Rubik,sans-serif;letter-spacing:-2.7px;text-transform:uppercase}.slogan span{display:block}.slogan .a{color:{ACCDK}}.f1{padding-bottom:67.5px}
.f2{display:grid;grid-template-columns:200px 350px 1fr;gap:18px;padding-bottom:90px}.fc{display:flex;flex-direction:column;align-items:flex-start;font-size:15.75px;line-height:22.5px;color:{W8}}.fc a{padding:4.5px 0}.fc a:hover{color:#fff;text-decoration:underline}.fct p{padding:4.5px 0}
.fr{max-width:495px;width:100%;margin-left:auto;margin-right:152px}.fr h3{font-size:33.75px;line-height:40.5px}.fr p{margin-top:18px}.fr .btn{margin-top:27px}
.f3{display:flex;flex-wrap:wrap;gap:9px 27px;padding-bottom:45px;font-weight:700;color:{ACCDK}}.f3 a:hover{text-decoration:underline}
.f4{border-top:1px solid {W2};padding:36px 0;display:grid;grid-template-columns:1fr auto 1fr;gap:9px 27px;font-size:15.75px;line-height:22.5px}.lg p+p{font-size:13.5px;line-height:18px}
.fl2{display:flex;flex-wrap:wrap;align-content:flex-start}.fl2 a{padding:0 13.5px;border-left:1px solid {W2}}.fl2 a:first-child{border:0;padding-left:0}.fl2 a:hover{text-decoration:underline}
/* phone menu: panel slides in from the right .3s, overlay to .8 */
.mm-ov{position:fixed;inset:0;z-index:50;background:{DARKER};opacity:0;transition:opacity .3s cubic-bezier(.4,0,.2,1)}.mm-ov.on{opacity:.8}
.mm{position:fixed;inset:0;z-index:51;background:{DARK};color:#fff;transform:translateX(100%);transition:transform .3s cubic-bezier(.4,0,.2,1);display:flex;flex-direction:column;overflow-y:auto}.mm.on{transform:none}.mm[hidden],.mm-ov[hidden]{display:none}
.mm-top{display:flex;justify-content:space-between;align-items:center;padding:16px;border-bottom:1px solid {W2}}.mm-x{width:48px;height:48px;background:none;border:0;position:relative;cursor:pointer;color:{ACCDK}}.mm-x i{position:absolute;left:10px;right:10px;top:23px;height:2px;background:currentColor;transform:rotate(45deg)}.mm-x i+i{transform:rotate(-45deg)}
.mm-nav{display:flex;flex-direction:column;padding:16px}.mm-nav a{font:600 16px/24px "DM Sans",sans-serif;padding:16px}.mm-b{margin-top:auto;padding:16px;display:grid;gap:1px}.mm-b .btn{width:100%}
@media(max-width:1100px){.fr{margin-right:0}.nc{flex-basis:calc((100% - 22.5px)/2)!important}.wc{flex-basis:calc((100% - 45px)/2)}}
@media(max-width:899px){
body{font-size:16px;line-height:24px}.wrap{padding:0 12px}
.topbar{font-size:14px;line-height:20px;padding:12px 0}.topbar .tr{display:none}.topbar .tl{gap:6px 16px}
.hd .wrap{grid-template-columns:1fr auto;padding-top:16px;padding-bottom:8px}.nav,.hb{display:none}.logo{font-size:22px;max-width:230px}.logo img{max-height:63px}
.burger{display:flex;flex-direction:column;justify-content:center;gap:6px;width:48px;height:48px;padding:0 10px}.burger i{height:2px;background:#fff}
.hero{min-height:536px}.hero-in{padding-top:40px;padding-bottom:123px}.hero-col{width:100%}
.hero-bg::after{background:linear-gradient({VEIL8},{VEIL7})}
h1.xl{font-size:36px;line-height:32px}h1.lg{font-size:32px;line-height:30px}h1.md{font-size:27px;line-height:27px}
.lead{font-size:18px;line-height:28px;margin-top:16px}.hero .btns{margin-top:40px}.btn{min-height:48px;padding:10px 16px;font-size:14px;line-height:20px}
.s{padding:48px 0}.s.first{padding-top:123px}.s.last{padding-bottom:123px}
h2{font-size:36px;line-height:40px;letter-spacing:-.9px}h2.h40{font-size:30px;line-height:36px}h3{font-size:20px;line-height:28px;letter-spacing:-.5px}
.ctr-sub,.shead .sub{font-size:16px;line-height:24px}.shead{flex-direction:column;gap:20px}
.deep{padding-top:48px}.deep.first{padding-top:120px}.stats{display:grid;grid-template-columns:1fr 1fr;gap:40px 20px}.stat{padding-left:20px}.stat .v{font-size:30px;line-height:36px;letter-spacing:-.75px}.stat .l{font-size:12px;line-height:16px;letter-spacing:.6px}
.split,.visit{display:flex;flex-direction:column-reverse}.visit{flex-direction:column}.split-p{min-height:0;aspect-ratio:4/3}.split-t,.visit .split-t{padding:40px 12px 48px}.visit:not(.haspic) .split-t{padding:48px 12px}.visit.last .split-t{padding-bottom:123px}
.deep.flush .split{padding-bottom:0}.stats+.split,.wrap+.split{margin-top:48px}
.kick{font-size:14px;line-height:20px;letter-spacing:1.4px;margin-bottom:20px}.intro{font-size:20px;line-height:32.5px}.split-t .btns{margin-top:32px}
.band,.dband{padding:88px 0}.band-in{padding:0 48px}.band h2,.dband h2{font-size:24px;line-height:32px;letter-spacing:-.6px}.band-in p{font-size:14px;line-height:20px}.dband .band-in{padding:0 12px}.dband .band-in p{font-size:16px;line-height:24px}.band .btns{flex-direction:column}
.pgrid{grid-template-columns:1fr;gap:16px;margin-top:32px}.pstack{gap:16px;grid-auto-rows:auto}.pc.big .pc-i{height:206px}.pc-t{padding:20px}.pc.big h3{font-size:22px;line-height:28px;letter-spacing:-.45px}
.pc.row.long{flex-direction:column}.pc.row.long .pc-i{width:100%;height:206px}.chip{font-size:12px;line-height:16px;font-weight:500;padding:4px 8px}.price{font-size:18px}.c-note{font-size:12px;line-height:16px}
.c-text,.c-rows,.c-prices{font-size:14px;line-height:20px}.term{font-size:14px;line-height:20px;padding:4px 8px}.ptail{margin-top:24px}
.wcs{gap:24px;margin-top:32px}.wc,.wcs.few .wc{flex-basis:100%;padding:28px 20px}.wc p{font-size:14px;line-height:20px}
.quotes{padding:48px 0 40px}.q{padding:0 36px}.q blockquote p{font-size:20px;line-height:32px}.q figcaption{font-size:14px;line-height:20px}.qb{position:static;display:inline-flex;margin:24px 4px 0;width:48px;height:48px}.qwrap{text-align:center}
.accent{padding:40px 0 48px}.tiles{gap:16px;margin-top:32px}.tile,.tiles .tile{grid-column:span 12!important}.tt{padding:28px;padding-right:76px}.tt h3{font-size:30px;line-height:36px;letter-spacing:-.75px}.tt p{font-size:14px;line-height:20px}.tgo{top:28px;right:28px;width:40px;height:40px}
.ncs{gap:16px;margin-top:32px}.nc{flex-basis:100%!important;padding:28px 20px}.nc p{font-size:14px;line-height:20px}
.tcs{grid-template-columns:1fr;gap:16px;margin-top:32px}.tc-i{height:auto;aspect-ratio:6/5}.tc-t{padding:20px}
.loc h3,.loc:not(:has(h3)) .addr{font-size:24px;line-height:32px}.addr{font-size:16px;line-height:24px}
.fl{grid-template-columns:1fr;gap:28px}.fli{padding-left:32px}
.ft{padding-top:150px}.slogan{font-size:30px;line-height:30px;letter-spacing:-1.5px}.f1{padding-bottom:40px}.f2{grid-template-columns:1fr 1fr;gap:16px 16px;padding-bottom:40px}.fc{font-size:14px;line-height:20px}.fc a,.fct p{padding:4px 0}
.fr{grid-column:1/-1;margin:24px 0 0;max-width:none}.fr h3{font-size:24px;line-height:32px}.f3{padding-bottom:32px;font-size:14px}.f4{grid-template-columns:1fr;padding:24px 0;font-size:14px;line-height:20px}.fl2{order:-1}
}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{transition:none!important;animation:none!important;scroll-behavior:auto!important}}
"""

JS = r"""(function(){var d=document,mm=d.querySelector('.mm'),ov=d.querySelector('.mm-ov'),bg=d.querySelector('.burger');
function set(on){if(on){mm.hidden=ov.hidden=false;mm.offsetWidth;}mm.classList.toggle('on',on);ov.classList.toggle('on',on);mm.setAttribute('aria-hidden',!on);bg.setAttribute('aria-expanded',on);d.documentElement.style.overflow=on?'hidden':'';
if(on){mm.querySelector('.mm-x').focus();}else{setTimeout(function(){if(!mm.classList.contains('on'))mm.hidden=ov.hidden=true;},320);}}
if(mm&&bg){bg.addEventListener('click',function(e){e.preventDefault();set(true);});mm.querySelector('.mm-x').addEventListener('click',function(){set(false);bg.focus();});ov.addEventListener('click',function(){set(false);});
d.addEventListener('keydown',function(e){if(e.key==='Escape'&&mm.classList.contains('on')){set(false);bg.focus();}});mm.querySelectorAll('a').forEach(function(a){a.addEventListener('click',function(){set(false);});});}
d.querySelectorAll('.qwrap').forEach(function(w){var s=w.querySelector('.qs'),n=s.children.length;function go(k){var i=Math.round(s.scrollLeft/(s.clientWidth+20));i=(i+k+n)%n;
s.scrollTo({left:i*(s.clientWidth+20),behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'auto':'smooth'});}
var p=w.querySelector('.prev'),x=w.querySelector('.next');if(p)p.addEventListener('click',function(){go(-1);});if(x)x.addEventListener('click',function(){go(1);});});
})();"""
