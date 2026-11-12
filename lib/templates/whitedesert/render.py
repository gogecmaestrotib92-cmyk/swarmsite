"""whitedesert — a template for places (restaurants, lodges, venues), rebuilt from the measured build of
https://white-desert.com (2026-11-12). render(d) -> one self-contained page. Pure: no file reads, no model call.
Photographs lead; where the client has none the slot falls back to a plain ground from the palette (never media.made,
never a glow). See NOTES.md for what each section takes and what was measured."""
import html as _h, json, math, re, unicodedata

PRE = '../../'
ROLE = {'exterior': 0, 'room': 1, 'bar': 2, 'people': 3, 'other': 4, 'dish': 5}


def e(s): return _h.escape(str(s or ''), quote=True)
def _rgb(c): c = c.lstrip('#'); c = ''.join(x * 2 for x in c) if len(c) == 3 else c; return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))
def _hex(t): return '#%02x%02x%02x' % tuple(max(0, min(255, round(v))) for v in t)
def _mix(a, b, t): A, B = _rgb(a), _rgb(b); return _hex(tuple(A[i] + (B[i] - A[i]) * t for i in range(3)))
def _lum(c): return sum(k * ((v / 255 / 12.92) if v / 255 <= .03928 else ((v / 255 + .055) / 1.055) ** 2.4) for k, v in zip((.2126, .7152, .0722), _rgb(c)))
def _cr(a, b): la, lb = sorted((_lum(a), _lum(b)), reverse=True); return (la + .05) / (lb + .05)
def _on(bg, *cands): return max(cands, key=lambda c: _cr(bg, c))


def _theme(p):
    g, ink, acc = p.get('ground') or '#ffffff', p.get('ink') or '#1f2a44', p.get('accent') or p.get('ink') or '#1f2a44'
    if _lum(g) < _lum(ink): g, ink = ink, g          # the reference stands on a light ground with dark ink
    dark = _mix(ink, '#000000', .72)                   # its near-black band (9,11,16 beside ink 31,42,68)
    if _cr(dark, g) < 12: dark = '#0b0c0f'
    muted = ink; t = .5                                # its 50 % ink small print, raised until 4.6:1 on the ground
    while t > 0 and _cr(_mix(ink, g, t), g) < 5.8: t -= .02
    muted = _mix(ink, g, max(t, 0))
    foot = _mix(g, _mix(ink, acc, .15), .1)            # its warm foot ground: a step darker than the page
    tile = _mix(foot, g, .45)
    fmuted = ink; t = .5
    while t > 0 and _cr(_mix(ink, foot, t), foot) < 5.8: t -= .02
    fmuted = _mix(ink, foot, max(t, 0))
    extras = [c for c in (p.get('extra') or []) if isinstance(c, str) and c.startswith('#')]
    slabs = [_mix(dark, g, t) for t in (.1, 0, .05)]   # card grounds: one tone in three quiet steps, never a hue per card
    return dict(g=g, ink=ink, acc=acc, onacc=_on(acc, '#ffffff', '#0b0c0f'), dark=dark, muted=muted, foot=foot, tile=tile,
                fmuted=fmuted, slabs=slabs, strip=_mix(g, ink, .07))


def _fit(text, width_vw, max_h_vw, cap_vw, max_lines):
    """size (vw) and measure (em) for a line of condensed capitals so that it fills the width as the reference's one
    word does. .47em is the mean advance of Oswald capitals measured on the reference (1165 px / 10 letters / 256 px)."""
    words = str(text).split(); n = len(' '.join(words)); best = None
    for k in range(1, max_lines + 1):
        L = max(len(w) for w in words)
        while True:
            lines, cur = 1, 0
            for w in words:
                if cur and cur + 1 + len(w) > L: lines += 1; cur = len(w)
                else: cur += (1 if cur else 0) + len(w)
            if lines <= k: break
            L += 1
        size = min(cap_vw, width_vw / (L * .47 + .2), max_h_vw / lines)
        if best is None or size > best[0] + .01: best = (size, L)
        if size >= cap_vw - .01: break
    return round(best[0], 2), round(best[1] * .47 + .6, 2)


def _a(o, cls='', inner=None, extra=''):
    if not o or not o.get('t'): return ''
    h = o.get('h'); tag = 'a' if h else 'span'
    return f'<{tag} class="{cls}"' + (f' href="{e(h)}"' if h else '') + f'{extra}>{inner if inner is not None else e(o["t"])}</{tag}>'


def _img(ph, cls='', lazy=True, pos=''):
    return (f'<img class="{cls}" src="{PRE}{e(ph["src"])}" width="{ph["w"]}" height="{ph["h"]}" alt="{e(ph.get("alt"))}"'
            + (' loading="lazy" decoding="async"' if lazy else ' fetchpriority="high"') + (f' style="object-position:{pos}"' if pos else '') + '>')


def _by_page(photos, href, taken, dish_first=False):
    """The photograph the client's own site shows on the page a card links to (`photos[].page` == the link) — the data's
    only statement of which picture belongs to which room or menu section. First view before a second, large before small."""
    if not href: return None
    c = [p for p in photos if p.get('page') and p['page'].rstrip('/') == href.rstrip('/') and p['src'] not in taken]
    c.sort(key=lambda p: ((p.get('role') == 'dish') != dish_first, bool(re.search(r'-\d+\.\w+$', p['src'])), bool(p.get('small')), -(p['w'] * p['h'])))
    return c[0] if c else None


def _plain(t): return ''.join(c for c in unicodedata.normalize('NFD', str(t or '').lower()) if c.isalnum() or c == ' ')


def _by_name(photos, name, taken):
    """A dish photograph whose description begins with the dish's own name (used to choose, never shown as words)."""
    n = _plain(name)
    return next((p for p in photos if n and p.get('role') == 'dish' and p['src'] not in taken and _plain(p.get('alt')).startswith(n)), None)


def render(d: dict) -> str:
    T = _theme(d.get('palette') or {})
    brand, hero, place = d.get('brand') or {}, d.get('hero') or {}, d.get('place') or {}
    media = d.get('media') or {}; photos = [p for p in media.get('photos') or [] if p.get('src') and p.get('w') and p.get('h')]
    bysrc = {p['src']: p for p in photos}
    booking = place.get('booking') if (place.get('booking') or {}).get('h') else d.get('cta')
    nav = [n for n in d.get('nav') or [] if n.get('t')]

    # ── spaces (the reference's camps): place.spaces, else the steps the page already tells ──
    steps = d.get('steps') or {}
    spaces = [dict(title=s.get('title'), text=s.get('text'), img=s.get('img'), cta=s.get('cta')) for s in (place.get('spaces') or steps.get('items') or []) if s.get('title')]
    used = {s['img'] for s in spaces if s.get('img')}

    # ── photographs: each slot CHOOSES by role, size and proportion; a picture is used once; most of a large set is never shown.
    # No picture is ever enlarged: every frame is capped at its picture's own pixels (CSS --pw/--ph).
    # 1 the opening: the place itself (outside, room, bar), not small, the one that covers most of a 1440x900 screen at its own size
    place_rank = lambda p: ROLE.get(p.get('role'), 4)
    backs = [p for p in photos if not p.get('small') and p.get('role') != 'dish' and p['src'] not in used]
    slot = {}
    if backs: slot['hero'] = min(backs, key=lambda p: (place_rank(p) > 2, -round(min(p['w'], 1440) * min(p['h'], 900) / 129600), place_rank(p), -p['w'] * p['h']))
    else:
        any_big = sorted([p for p in photos if not p.get('small')], key=lambda p: (p.get('role') == 'dish', p['src'] in used, -p['w'] * p['h']))
        if any_big: slot['hero'] = any_big[0]
    if slot.get('hero'): used.add(slot['hero']['src'])
    # 2 a room without a picture of its own takes the one its own page shows (all rooms, or none: a row is not mixed)
    if spaces and not any(s.get('img') for s in spaces):
        got = set(used); picks = []
        for s_ in spaces:
            p = _by_page(photos, (s_.get('cta') or {}).get('h'), got)
            if p: got.add(p['src'])
            picks.append(p)
        if all(picks):
            for s_, p in zip(spaces, picks): s_['img'] = p['src']
            used |= {p['src'] for p in picks}
    # 3 the strip's cards: a menu section takes a dish its own page shows; a section listed dish by dish takes its first dish's picture
    menu = place.get('menu') or {}; sec_pic = {}
    for k, s_ in enumerate(menu.get('sections') or []):
        p = _by_page(photos, s_.get('h'), used, dish_first=True) or next((q for q in (_by_name(photos, it.get('name'), used) for it in s_.get('items') or []) if q), None)
        if p: sec_pic[k] = p; used.add(p['src'])
    # 4 the tall banner (upright first), the closing band and the rooms' opening (wide): what is left of the large pictures, dishes last
    free = sorted([p for p in photos if not p.get('small') and p['src'] not in used], key=lambda p: (p.get('role') == 'dish', place_rank(p), -p['w'] * p['h']))
    for name in ('tall', 'close', 'open'):
        c = [p for p in free if p.get('role') != 'dish' or (name == 'tall' and not any(q.get('role') != 'dish' for q in free))]
        if not c: break
        pick = (next((p for p in c if p['h'] >= p['w'] * .9), None) if name == 'tall' else next((p for p in c if p['w'] >= p['h'] * 1.2), None)) or (c[0] if name == 'tall' else None)
        if not pick: continue
        slot[name] = pick; free = [p for p in free if p is not pick]; used.add(pick['src'])
    def cap(p): return f'--pw:{p["w"]}px;--ph:{p["h"]}px'

    css, body = [], []

    # ── 0 bar ──
    left, right = nav[:3], nav[3:5]
    logo = (f'<img class="logo" src="{PRE}{e(brand["logo"])}" alt="" width="40" height="40">' if brand.get('logo') else '')
    bar = ('<header class="bar" id="bar"><nav class="bar-in" aria-label="' + e(brand.get('name')) + '">'
           '<ul class="tiles l">' + ''.join(f'<li>{_a(n, "tile")}</li>' for n in left) + '</ul>'
           f'<a class="brand" href="{e(brand.get("home") or "#")}">{logo}<span>{e(brand.get("name"))}</span></a>'
           '<ul class="tiles r">' + ''.join(f'<li class="opt">{_a(n, "tile")}</li>' for n in right) + (f'<li>{_a(booking, "tile go")}</li>' if booking else '') + '</ul></nav></header>')
    body.append(bar)
    if booking: body.append(_a(booking, 'tab', extra=' id="tab" tabindex="-1" aria-hidden="true"'))

    # ── 1 opening ──
    title = hero.get('title') or brand.get('name') or ''
    sd, md_ = _fit(title, 80.9, 24, 17.78, 2); sm, mm = _fit(title, 92, 64, 20.5, 5)
    hp = slot.get('hero')
    hero_btn = hero.get('secondary') if (hero.get('secondary') or {}).get('t') else hero.get('primary')
    body.append(f'<section class="hero{"" if hp else " bare"}" data-tone="dark"><div class="hero-pin">'
                + (f'<div class="hero-bg" style="{cap(hp)}">{_img(hp, "", False)}</div>' if hp else '')
                + '<div class="hero-in"><div class="hero-mid">' + (f'<p class="tagline">{e(hero.get("text"))}</p>' if hero.get('text') else '<span></span>')
                + (_a(hero_btn, 'btn line') if hero_btn else '') + '</div>'
                + f'<h1 class="mega" id="mega" style="--sd:{sd}vw;--md:{md_}em;--sm:{sm}vw;--mm:{mm}em">{e(title)}</h1></div>'
                + '<div class="mist" id="mist" aria-hidden="true"></div></div></section>')
    body.append('<div class="page">')

    # ── 2 statement ──
    st = d.get('statement') or {}
    if st.get('title'):
        body.append('<section class="intro" data-tone="light"><div class="g12"><div class="intro-col">'
                    + (f'<p class="ital">{e(hero.get("kicker"))}</p>' if hero.get('kicker') else '')
                    + f'<h2 class="state fade" data-fade>{e(st["title"])}</h2></div></div></section>')

    # ── 3 tall banner ──
    tp = slot.get('tall'); tl, tt = hero.get('text2'), st.get('text')
    if tp or tl or tt:
        ratio = (tp['h'] / tp['w']) if tp else 0
        body.append(f'<section class="tall{"" if tp else " bare"}" data-tone="light"' + (f' style="--r:{min(ratio, .9375):.4f};{cap(tp)}"' if tp else '') + '>'
                    + (_img(tp, 'fill') + '<div class="tall-veil"></div>' if tp else '')
                    + ('<div class="g12"><div class="tall-col"' + (' data-drift' if tp else '') + '>' + (f'<p class="lab">{e(tl)}</p>' if tl else '') + (f'<p class="small">{e(tt)}</p>' if tt else '') + '</div></div>' if (tl or tt) else '')
                    + '</section>')

    # ── 4+5 what is offered: events, then the menu's sections ──
    cards = []
    for ev in place.get('events') or []:
        if ev.get('what'): cards.append(dict(title=ev['what'], meta=[ev.get('price'), ev.get('when')], text=ev.get('where'), cta=ev.get('cta')))
    for s in menu.get('sections') or []:
        if s.get('t'): cards.append(dict(title=s['t'], meta=[], items=s.get('items') or [], h=s.get('h'), pic=sec_pic.get((menu.get('sections') or []).index(s))))
    cards = cards[:8]
    feat_title = (d.get('features') or {}).get('title') if (menu.get('sections')) else ''
    menu_link = next((n for n in (d.get('links') or []) + nav if menu.get('h') and n.get('h') == menu['h'] and n.get('t')), None)
    if cards:
        if feat_title: body.append(f'<section class="head" data-tone="light"><h2 class="h60">{e(feat_title)}</h2></section>')
        out = []
        for i, c in enumerate(cards):
            bg = T['slabs'][i % len(T['slabs'])]; fg = _on(bg, '#ffffff', '#0b0c0f'); cpic = c.get('pic')
            meta = [m for m in c.get('meta') or [] if m not in (None, '')]
            link = c.get('cta') if (c.get('cta') or {}).get('h') else ({'t': c['title'], 'h': c['h']} if c.get('h') else None)
            ttl = (f'<a class="stretch" href="{e(c["h"])}">{e(c["title"])}</a>' if c.get('h') and not c.get('cta') else e(c['title']))
            rows = ''.join(f'<li><span>{e(it.get("name"))}</span><span>{e(it.get("price"))}</span></li>' for it in (c.get('items') or [])[:6] if it.get('name'))
            out.append(f'<article class="card{" on" if i == len(cards) - 1 else ""}" style="--bg:{bg};--fg:{fg}" tabindex="-1">' + (f'<div class="card-bg" style="--cw:{cpic["w"]}px">{_img(cpic, "fill")}</div>' if cpic else '') + '<div class="card-in">'
                       f'<h3 class="card-t">{ttl}</h3><div class="card-f">'
                       + (f'<p class="card-m">' + ''.join(f'<span>{e(m)}</span>' for m in meta) + '</p>' if meta else '')
                       + (f'<p class="card-x">{e(c["text"])}</p>' if c.get('text') else '') + (f'<ul class="card-l">{rows}</ul>' if rows else '')
                       + (f'<a class="card-go stretch" href="{e(link["h"])}">{e(link["t"])}</a>' if c.get('cta') and link else '')
                       + '</div></div></article>')
        body.append(f'<section class="flick-wrap{"" if feat_title else " lone"}" data-tone="light"><div class="flick n{len(cards)}" id="flick"' + (f' style="--fh:{min(c["pic"]["h"] for c in cards if c.get("pic"))}px"' if any(c.get('pic') for c in cards) else '') + '>' + ''.join(out) + '</div>'
                    + (f'<p class="flick-more">{_a(menu_link, "btn ink")}</p>' if menu_link and menu.get('sections') else '') + '</section>')

    # ── 6 a voice ──
    quotes = [q for q in d.get('quotes') or [] if q]
    def _q(q): return (dict(text=q) if isinstance(q, str) else dict(text=q.get('text') or q.get('q') or q.get('quote'), name=q.get('name') or q.get('by'), role=q.get('role') or q.get('title')))
    if quotes and _q(quotes[0])['text']:
        q = _q(quotes[0])
        body.append('<section class="voice" data-tone="light"><div class="g12"><blockquote class="voice-col"><span class="qm" aria-hidden="true">“</span>'
                    f'<p class="voice-t">{e(q["text"])}</p>' + (f'<footer><span>{e(q.get("name"))}</span>' + (f'<span class="mut">{e(q.get("role"))}</span>' if q.get('role') else '') + '</footer>' if q.get('name') else '') + '</blockquote></div></section>')

    # ── 7 spaces: a held screen, the cards pass sideways ──
    if spaces:
        imgs = [bysrc.get(s['img']) for s in spaces]
        ws = [p['w'] for p in imgs if p]
        W = min([680] + ws) if ws else 680                      # no picture is shown wider than its own pixels
        Hc = min([p['h'] for p in imgs if p] or [9999])
        compact = W < 560
        op = slot.get('open'); q2 = _q(quotes[1]) if len(quotes) > 1 else None
        cs = []
        for i, (s, p) in enumerate(zip(spaces, imgs)):
            bg = T['slabs'][i % len(T['slabs'])]; fg = '#ffffff' if p else _on(bg, '#ffffff', '#0b0c0f')
            inner = ((_img(p, 'fill') + f'<span class="sp-veil{" low" if (s.get("cta") or {}).get("t") else ""}"></span>') if p else '') + '<div class="sp-txt">' + f'<h3 class="sp-t">{e(s["title"])}</h3>' + (f'<p class="sp-x">{e(s["text"])}</p>' if s.get('text') else '') + (f'<p class="sp-c">{e(s["cta"]["t"])}</p>' if (s.get('cta') or {}).get('t') else '') + '</div>'
            tag, href = ('a', f' href="{e(s["cta"]["h"])}"') if (s.get('cta') or {}).get('h') else ('div', '')
            cs.append(f'<div class="sp-panel"><{tag} class="sp-card"{href}><div class="sp-card-in{"" if p else " bare"}" style="--bg:{bg};--fg:{fg}">{inner}</div></{tag}></div>')
        body.append(f'<section class="spaces{" compact" if compact else ""}" id="spaces" data-tone="dark" style="--cw:{W}px;--chh:{Hc}px">'
                    '<div class="sp-pin"><div class="sp-open">' + (_img(op, 'fill') + '<span class="sp-shade"></span>' if op else '')
                    + (f'<h2 class="sp-h" id="sp-h">{e(steps.get("title"))}</h2>' if steps.get('title') else '')
                    + (f'<div class="g12 sp-note" id="sp-note"><p class="small">{e(steps.get("text"))}</p></div>' if steps.get('text') else '') + '</div>'
                    '<div class="sp-strips" aria-hidden="true"><i></i><i></i><i></i></div>'
                    '<div class="sp-track" id="sp-track"><div class="sp-lead"></div>' + ''.join(cs)
                    + (f'<div class="sp-panel last"><blockquote class="sp-q"><p>{e(q2["text"])}</p>' + (f'<footer>{e(q2.get("name"))}</footer>' if q2.get('name') else '') + '</blockquote></div>' if q2 and q2.get('text') else '<div class="sp-tail"></div>')
                    + '</div></div></section>')

    # ── 8 the giant mark ──
    if place.get('since'):
        gs, gm = _fit(place['since'], 98, 40, 22.2, 1)
        body.append(f'<section class="giant" data-tone="light" aria-hidden="true"><p class="mega" data-slow style="--sd:{gs}vw;--md:99em;--sm:{min(gs * 1.6, 51)}vw;--mm:99em">{e(place["since"])}</p></section>')

    # ── 9 where and when ──
    ad, ph, hours = place.get('address') or {}, place.get('phone') or {}, [h for h in place.get('hours') or [] if h.get('days')]
    if ad.get('street') or ph.get('t') or hours:
        l1 = ' '.join(x for x in (ad.get('postcode'), ad.get('city')) if x); l2 = ', '.join(x for x in (ad.get('region'), ad.get('country')) if x)
        tel = f'<a href="{e(ph["h"])}">{e(ph["t"])}</a>' if ph.get('h') else e(ph.get('t'))
        mail = f'<a href="mailto:{e(place["email"])}">{e(place["email"])}</a>' if place.get('email') else ''
        facts = [(h['days'], ' – '.join(x for x in (h.get('open'), h.get('close')) if x)) for h in hours][:3]
        if len(facts) < 3 and ph.get('t'): facts.append((l1 if not hours else '', tel))
        side = [x for x in [place.get('takeaway')] + (place.get('social') or []) if x and x.get('t')]
        body.append('<section class="where" data-tone="light"><div class="where-head"><div class="rule"></div><div class="g12 wh">'
                    f'<p class="corner">{e(l1)}' + (f'<br>{e(l2)}' if l2 else '') + '</p>'
                    '<div class="wh-c">' + (f'<h2 class="h42">{e(ad.get("street") or ad.get("city"))}</h2>' if (ad.get('street') or ad.get('city')) else '') + (f'<p class="small mut">{e(hero.get("note"))}</p>' if hero.get('note') else '') + '</div>'
                    f'<p class="corner r">{tel if (hours and ph.get("t")) else ""}' + (f'<br>{mail}' if mail and hours else mail) + '</p></div></div>'
                    '<div class="where-dark" data-tone="dark"><div class="g12 wd">'
                    + (f'<dl class="facts{"" if side else " row"}">' + ''.join(f'<div class="fact">' + (f'<dt class="ital">{e(k)}</dt>' if k else '<dt class="sr">·</dt>') + f'<dd>{v if v.startswith("<a") else e(v)}</dd></div>' for k, v in facts) + '</dl>' if facts else '')
                    + ('<ul class="side">' + ''.join(f'<li>{_a(x)}</li>' for x in side) + '</ul>' if side else '') + '</div></div></section>')

    # ── 10 closing banner ──
    cl = d.get('close') or {}; cp = slot.get('close')
    if cl.get('title'):
        body.append(f'<section class="close{"" if cp else " bare"}" data-tone="{"dark" if cp else "light"}"' + (f' style="{cap(cp)}"' if cp else '') + '>' + (_img(cp, 'fill') + '<span class="close-shade"></span>' if cp else '')
                    + f'<div class="close-in"><h2 class="h42">{e(cl["title"])}</h2>' + _a(cl.get('cta') or booking, 'btn line' if cp else 'btn ink') + '</div></section>')

    # ── 11 foot ──
    foot = d.get('foot') or {}; lists = [x for x in menu.get('lists') or [] if x.get('t')]
    cols = ['<ul class="fl">' + ''.join(f'<li>{_a(n)}</li>' for n in nav) + '</ul>' if nav else '',
            ((f'<p class="ital">{e(menu_link["t"])}</p>' if menu_link else '') + '<ul class="fl">' + ''.join(f'<li>{_a(x)}</li>' for x in lists[:10]) + '</ul>') if lists else '',
            '<ul class="fl">' + ''.join(f'<li>{_a(x)}</li>' for x in (foot.get('links') or []) if x.get('t')) + '</ul>' if foot.get('links') else '']
    tiles = []
    if booking: tiles.append(_a(booking, 'ft go wide'))
    half = [x for x in [menu_link if menu_link else None, ({'t': ph['t'], 'h': ph.get('h')} if ph.get('t') else None)] if x]
    tiles += [_a(x, 'ft' + (' wide' if len(half) == 1 else '')) for x in half]
    if place.get('email'): tiles.append(_a({'t': place['email'], 'h': 'mailto:' + place['email']}, 'ft wide'))
    elif (place.get('takeaway') or {}).get('t'): tiles.append(_a(place['takeaway'], 'ft wide'))
    notices = ''.join('<div class="notice">' + (f'<img src="{PRE}{e(n["img"])}" width="{n["w"]}" height="{n["h"]}" alt="" loading="lazy">' if n.get('img') else '') + '<div>' + ''.join(f'<p>{e(t)}</p>' for t in n.get('text') or []) + '</div></div>' for n in place.get('notices') or [])
    ws_ = round(min(13, 94 / (max(len(brand.get('name') or ''), 1) * .56 + .3)), 2)
    body.append('<footer class="foot" data-tone="light"><div class="g12 foot-top"><div class="foot-brand">' + (logo.replace('class="logo"', 'class="logo big"') if logo else '')
                + (f'<p class="fine">{e(foot.get("text"))}</p>' if foot.get('text') else '') + '</div>'
                + ''.join(f'<div class="foot-col">{c}</div>' for c in cols if c) + (f'<div class="foot-tiles">{"".join(tiles)}</div>' if tiles else '') + '</div>'
                + (f'<div class="notices">{notices}</div>' if notices else '')
                + f'<p class="word" aria-hidden="true" style="--ws:{ws_}vw">{e(brand.get("name"))}</p>'
                + '<div class="foot-bot">' + (f'<p class="ital">{e(foot.get("legal"))}</p>' if foot.get('legal') else '<span></span>') + '</div></footer>')
    body.append('</div>')
    body.append('<div class="lines" aria-hidden="true">' + '<i></i>' * 9 + '</div>')

    return ('<!doctype html><html lang="' + e(d.get('lang') or 'en') + '"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{e(brand.get("name"))}' + (f' — {e(hero.get("kicker"))}' if hero.get('kicker') else '') + '</title>'
            + (f'<meta name="description" content="{e(hero.get("text"))}">' if hero.get('text') else '')
            + '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;1,500&family=Inter+Tight:wght@400;500&family=Oswald:wght@400;500&display=swap">'
            '<style>' + CSS.replace('/*VARS*/', f'--g:{T["g"]};--ink:{T["ink"]};--acc:{T["acc"]};--onacc:{T["onacc"]};--dark:{T["dark"]};--mut:{T["muted"]};--foot:{T["foot"]};--tile:{T["tile"]};--fmut:{T["fmuted"]};--strip:{T["strip"]};') + '</style></head><body>'
            + '<noscript><style>.flick{flex-wrap:wrap;height:auto;max-height:none;gap:10px}.flick .card{flex:1 1 30%;min-height:240px}.flick .card-in{position:relative;width:auto;opacity:1;min-height:240px}</style></noscript>' + ''.join(body) + '<script>' + JS + '</script></body></html>')


CSS = r"""
:root{/*VARS*/--serif:"Cormorant Garamond","Cormorant",Garamond,"Times New Roman",serif;--sans:"Inter Tight",Inter,system-ui,sans-serif;--cond:Oswald,"Arial Narrow",Impact,sans-serif;--ez:cubic-bezier(.5,1,.89,1);--vh:100vh}
@supports(height:100svh){:root{--vh:100svh}}
*,*:before,*:after{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--g);color:var(--ink);font:500 16px/1.4 var(--sans);-webkit-font-smoothing:antialiased;overflow-x:clip}
img{display:block;max-width:100%;height:auto}a{color:inherit;text-decoration:none}ul,dl,dd,h1,h2,h3,p,blockquote{margin:0;padding:0}ul{list-style:none}
:focus-visible{outline:2px solid var(--ink);outline-offset:3px;box-shadow:0 0 0 7px var(--g)}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
.fill{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.g12{margin:0 12px;display:grid;grid-template-columns:repeat(12,1fr)}
.ital{font:italic 500 18px/1.2 var(--serif)}.small{font:500 14px/1.5 var(--sans)}.mut{color:var(--mut)}
.lab{font:500 18px/1.2 var(--cond);text-transform:uppercase}
.h42{font:400 42px/1 var(--serif);text-transform:uppercase;text-wrap:balance}.h60{font:400 60px/1 var(--serif);text-transform:uppercase;text-align:center;text-wrap:balance}
/* fixed hairlines of the reference's grid: 1px, 10 %, difference */
.lines{position:fixed;inset:0;z-index:40;pointer-events:none;opacity:.1;mix-blend-mode:difference}
.lines i{position:absolute;top:0;bottom:0;width:1px;background:#fff}
.lines i:nth-child(1){left:12px}.lines i:nth-child(2){left:60px}.lines i:nth-child(3){left:calc(12px + (100% - 24px)/6)}.lines i:nth-child(4){left:calc(12px + (100% - 24px)/3)}.lines i:nth-child(5){left:50%}.lines i:nth-child(6){left:calc(12px + (100% - 24px)*2/3)}.lines i:nth-child(7){left:calc(12px + (100% - 24px)*5/6)}.lines i:nth-child(8){right:60px}.lines i:nth-child(9){right:12px}
/* bar */
.bar{position:fixed;top:0;left:0;right:0;z-index:50;height:80px;padding:20px;transition:transform .25s ease-out;color:#fff}
.bar.away{transform:translateY(-100%)}.bar:focus-within{transform:none}
.bar-in{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:12px}
.tiles{display:flex;gap:6px}.tiles.r{justify-content:flex-end}
.tile,.brand{background:rgba(12,14,20,.72);-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px);border-radius:2px}
.tile{display:flex;align-items:center;justify-content:center;min-width:120px;height:40px;padding:0 16px;-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px);font:400 16px/1 var(--sans);white-space:nowrap;transition:all .3s var(--ez)}
.tile:hover{background:var(--acc);color:var(--onacc)}
.bar.light{color:var(--ink)}.bar.light .tile,.bar.light .brand{background:color-mix(in srgb,var(--ink) 9%,var(--g))}.bar.light .tile:hover{background:var(--acc);color:var(--onacc)}
.brand{display:flex;align-items:center;gap:10px;height:40px;padding:0 16px;font:500 15px/1 var(--cond);letter-spacing:.14em;text-transform:uppercase;white-space:nowrap}
.logo{width:40px;height:40px;border-radius:2px;background:#fff;object-fit:contain}.logo.big{width:82px;height:82px}
.tab{position:fixed;right:0;top:50%;z-index:45;writing-mode:vertical-rl;transform:translate(100%,-50%) rotate(180deg);min-height:200px;width:60px;display:flex;align-items:center;justify-content:center;background:var(--acc);color:var(--onacc);font:500 14px/1 var(--sans);border-radius:0 2px 2px 0;transition:transform .45s cubic-bezier(.76,0,.24,1)}
.tab.in{transform:translate(0,-50%) rotate(180deg)}
/* opening: held for two screens while the ground rises over it */
.hero{position:relative;height:calc(var(--vh)*3);background:var(--dark);color:#fff}
.hero-pin{position:sticky;top:0;height:var(--vh);overflow:hidden}
.hero-bg{position:absolute;inset:0;margin:auto;max-width:var(--pw);max-height:var(--ph)}.hero-bg img{width:100%;height:100%;object-fit:cover}
.hero-bg:after{content:"";position:absolute;inset:0;background:linear-gradient(rgba(0,0,0,.6),rgba(0,0,0,.58) 40%,rgba(0,0,0,.6))}
.hero-in{position:absolute;inset:0;animation:rise 1.4s cubic-bezier(.16,1,.3,1) both,show 1.4s ease both}
@keyframes rise{from{transform:translateY(180px)}}@keyframes show{from{opacity:0}}
.hero-mid{position:absolute;left:60px;right:60px;top:47.5%;display:flex;justify-content:space-between;align-items:flex-start;gap:24px}
.tagline{font:italic 500 18px/1.2 var(--serif);max-width:294px;text-wrap:balance}
.mega{font:400 var(--sd)/1 var(--cond);text-transform:uppercase;text-align:center;max-width:var(--md);margin:0 auto;text-wrap:balance}
.hero .mega{position:absolute;left:0;right:0;bottom:24px;padding:0 12px;will-change:transform,filter}
.mist{position:absolute;left:0;right:0;top:0;height:calc(var(--vh)*1.9);transform:translateY(var(--vh));background:linear-gradient(to bottom,transparent,var(--g) 46%);will-change:transform}
.btn{display:inline-flex;align-items:center;justify-content:center;min-width:160px;height:50px;padding:0 32px;border-radius:2px;font:500 14px/1.5 var(--sans);transition:all .3s var(--ez);white-space:nowrap}
.btn.line{border:1px solid rgba(255,255,255,.45);color:#fff;background:rgba(0,0,0,.18)}.btn.line:hover{background:#fff;border-color:#fff;color:#0b0c0f}
.hero .btn{min-width:188px;height:44px}
.btn.ink{border:1px solid color-mix(in srgb,var(--ink) 35%,transparent);color:var(--ink)}.btn.ink:hover{background:var(--ink);color:var(--g)}
.page{position:relative;z-index:2;margin-top:calc(var(--vh)*-1);background:var(--g)}
/* statement */
.intro{padding:320px 0 160px}.intro-col{grid-column:5/11;display:flex;flex-direction:column;gap:32px}
.state{font:400 42px/1 var(--serif);text-transform:uppercase;text-indent:16.6%}
.fade{position:relative;color:var(--ink)}.fade:after{content:"";position:absolute;inset:-4px 0;pointer-events:none;background:linear-gradient(to bottom,transparent var(--f,100%),color-mix(in srgb,var(--g) 84%,transparent) calc(var(--f,100%) + 34%))}
/* tall banner */
.tall{position:relative;max-width:var(--pw);margin:0 auto;height:calc(min(100vw,var(--pw))*var(--r));overflow:hidden}
.tall-veil{position:absolute;left:0;right:0;top:0;height:min(48%,470px);background:linear-gradient(to bottom,var(--g) 0,color-mix(in srgb,var(--g) 96%,transparent) 66%,transparent)}
.tall .g12{position:relative}
/* the words on the banner stand on a soft pad of the page ground, however long they are and whatever the picture is */
.tall:not(.bare) .tall-col{position:relative;isolation:isolate}.tall:not(.bare) .tall-col:before{content:"";position:absolute;inset:110px -34px -34px;background:color-mix(in srgb,var(--g) 92%,transparent);filter:blur(16px);z-index:-1}.tall-col{grid-column:3/5;padding-top:139px;display:flex;flex-direction:column;gap:20px}
.tall.bare{height:auto;max-width:none;padding:0 0 40px}.tall.bare .tall-col{padding-top:0}
/* offered */
.head{padding:320px 12px 160px}
.flick-wrap{padding:0 12px}.flick-wrap.lone{padding-top:160px}.flick.n1{height:480px;min-height:0}.flick{display:flex;height:85vh;min-height:min(520px,var(--fh,765px));max-height:min(765px,var(--fh,765px));overflow:hidden}
.card{position:relative;flex:1 1 0;min-width:0;overflow:hidden;background:var(--bg);color:var(--fg);transition:flex-grow .6s cubic-bezier(.4,0,.2,1);cursor:pointer}
.card-bg{position:absolute;top:0;bottom:0;right:0;width:100%;max-width:var(--cw)}
.card-bg:after{content:"";position:absolute;inset:0;background:color-mix(in srgb,var(--bg) 50%,transparent);transition:opacity .5s ease}
.card.on .card-bg:after{background:linear-gradient(90deg,var(--bg),color-mix(in srgb,var(--bg) 66%,transparent) 50%,color-mix(in srgb,var(--bg) 30%,transparent))}
.card.on{flex-grow:4}.flick.n1 .card{flex-grow:1}
.card-in{position:absolute;inset:0;width:max(432px,33vw);padding:44px;display:flex;flex-direction:column;justify-content:space-between;opacity:0;transition:opacity .3s ease}
.card.on .card-in{opacity:1;transition:opacity .5s ease .25s}
.card-t{font:italic 500 42px/1 var(--serif);max-width:320px;text-wrap:balance}
.card-f{display:flex;flex-direction:column;gap:20px;max-width:344px}
.card-m{display:flex;gap:16px;font:500 16px/1 var(--sans)}.card-m span+span{padding-left:16px;border-left:1px solid currentColor}
.card-x{font:500 16px/1.4 var(--sans)}
.card-l li{display:flex;justify-content:space-between;gap:16px;font:500 14px/1.5 var(--sans);padding:5px 0;border-top:1px solid color-mix(in srgb,currentColor 28%,transparent)}
.card-go{font:500 14px/1.5 var(--sans);text-decoration:underline;text-underline-offset:4px}
.stretch:after{content:"";position:absolute;inset:0}
.card:not(.on) .stretch:after{pointer-events:none}
.flick-more{display:flex;justify-content:center;padding-top:56px}
.voice{padding:320px 0}.voice-col{grid-column:5/9}.qm{font:400 36px/0 var(--serif)}.voice-t{font:italic 500 22px/1.2 var(--serif);text-indent:16.6%;margin:12px 0 24px}.voice footer{display:flex;flex-direction:column;font:500 14px/1.5 var(--sans)}
/* spaces — the plain build (no script, or reduced motion): opening block, then the cards in a row that wraps */
.spaces{position:relative;background:var(--dark);color:#fff;margin-top:160px}
.sp-open{position:relative;min-height:70vh;display:flex;align-items:center;justify-content:center;overflow:hidden;padding:120px 24px}
.sp-shade{position:absolute;inset:0;background:rgba(0,0,0,.45)}
.sp-h{position:relative;font:500 90px/1.1 var(--serif);text-transform:uppercase;text-align:center;max-width:820px;text-wrap:balance}
.sp-note{position:absolute;left:0;right:0;bottom:48px;margin:0 12px}.sp-note p{grid-column:11/13;padding-right:48px}
.sp-strips{display:none}
.sp-track{display:flex;flex-wrap:wrap;justify-content:center;gap:40px;padding:80px 20px;background:var(--strip);color:var(--ink)}
.sp-lead,.sp-tail{display:none}
.sp-card{display:block;padding:20px;border-radius:6px;background:color-mix(in srgb,var(--ink) 7%,transparent)}
.sp-card-in{position:relative;width:min(var(--cw),calc(100vw - 80px));aspect-ratio:680/500;max-height:var(--chh);border-radius:2px;overflow:hidden;background:var(--bg);color:var(--fg);transition:opacity .3s var(--ez)}
.sp-veil{position:absolute;inset:0;background:linear-gradient(to bottom,rgba(0,0,0,.74),rgba(0,0,0,.6) 38%,rgba(0,0,0,0) 72%)}
.sp-veil.low{background:linear-gradient(to bottom,rgba(0,0,0,.74),rgba(0,0,0,.6) 38%,rgba(0,0,0,0) 62%,rgba(0,0,0,.72) 84%,rgba(0,0,0,.8))}
.sp-card-in.bare .sp-txt{justify-content:flex-start}
.sp-txt{position:absolute;inset:0;padding:40px;display:flex;flex-direction:column;align-items:center;text-align:center;gap:32px}
.sp-t{font:400 42px/1 var(--serif);text-transform:uppercase;text-wrap:balance}.sp-x{font:500 14px/1.4 var(--sans);max-width:480px}
.sp-c{margin-top:auto;font:500 14px/1.4 var(--cond);text-transform:uppercase;letter-spacing:.02em}
a.sp-card:hover .sp-card-in{opacity:.94}
.spaces.compact .sp-t{font-size:26px}.spaces.compact .sp-txt{padding:28px 20px;gap:14px}
.sp-q{max-width:472px;text-align:center;font:italic 500 32px/1.2 var(--serif)}.sp-q footer{margin-top:24px;font:500 12px/1 var(--sans);letter-spacing:.1em;text-transform:uppercase;font-style:normal}
.sp-panel.last{display:flex;align-items:center;justify-content:center;width:100%;padding:60px 20px}
/* spaces — the held build */
.spaces.pin{height:var(--sh)}
.spaces.pin .sp-pin{position:sticky;top:0;height:var(--vh);overflow:hidden;overflow:clip;background:var(--dark)}
.spaces.pin .sp-open{position:absolute;inset:0;min-height:0;padding:0}
.spaces.pin .sp-h{will-change:transform}
.spaces.pin .sp-note{bottom:auto;top:57%}
.spaces.pin .sp-strips{display:block;position:absolute;inset:0}
.spaces.pin .sp-strips i{position:absolute;top:0;bottom:0;width:33.4%;background:var(--strip);transform:scaleX(var(--w,0));transform-origin:100% 50%}
.spaces.pin .sp-strips i:nth-child(1){left:0}.spaces.pin .sp-strips i:nth-child(2){left:33.3%}.spaces.pin .sp-strips i:nth-child(3){left:66.6%}
.spaces.pin .sp-track{position:absolute;top:0;left:0;height:100%;flex-wrap:nowrap;gap:0;padding:0;background:none;justify-content:flex-start;align-items:center;will-change:transform}
.spaces.pin .sp-lead{display:block;flex:0 0 100vw}.spaces.pin .sp-tail{display:block;flex:0 0 calc(50vw - (var(--cw) + 240px)/2)}
.spaces.pin .sp-panel{flex:0 0 calc(var(--cw) + 240px);display:flex;justify-content:center}
.spaces.pin .sp-panel.last{flex:0 0 100vw;color:var(--ink)}
.spaces.pin .sp-card-in{width:var(--cw)}
/* giant mark */
.giant{padding:140px 12px 70px;overflow:hidden;background:var(--strip)}.giant .mega{line-height:.9;color:color-mix(in srgb,var(--ink) 62%,var(--strip));will-change:transform}
/* where */
.where-head{padding:0 0 78px;background:var(--g)}.giant + .where .where-head{padding-top:0}
.rule{height:1px;margin:0 12px 11px;background:color-mix(in srgb,var(--ink) 50%,transparent)}
.wh{align-items:start}.corner{grid-column:span 4;font:500 13px/1.3 var(--cond);letter-spacing:.02em;color:var(--mut)}.corner.r{text-align:right;grid-column:9/13}.tab ~ .page .corner.r{padding-right:60px}
.corner a:hover,.fl a:hover,.side a:hover{color:var(--acc)}
.wh-c{grid-column:5/9;grid-row:1;text-align:center;display:flex;flex-direction:column;gap:20px;align-items:center}
.where-dark{background:var(--dark);color:#fff;padding:96px 28px}.wd{margin:0 12px;align-items:end}
.facts{grid-column:1/5;padding:32px 20px;border-radius:6px;background:color-mix(in srgb,#fff 9%,transparent)}
.fact{padding:24px 0;border-top:1px dashed rgba(255,255,255,.3)}.fact:first-child{padding-top:0;border-top:0}.fact:last-child{padding-bottom:0}
.fact dd{font:400 42px/1.5 var(--sans);text-transform:uppercase;white-space:nowrap}.fact dd a:hover{color:var(--acc)}
.facts.row{grid-column:1/13;display:grid;grid-auto-flow:column;grid-auto-columns:1fr;padding:32px 20px}.facts.row .fact{padding:0 28px;border-top:0;border-left:1px dashed rgba(255,255,255,.3)}.facts.row .fact:first-child{padding-left:0;border-left:0}
.side{grid-column:9/12;display:flex;flex-direction:column;gap:14px;font:400 16px/1.2 var(--cond);text-transform:uppercase}
/* closing */
.close{position:relative;height:var(--vh);max-width:var(--pw);max-height:var(--ph);margin:0 auto;display:flex;align-items:center;justify-content:center;overflow:hidden;background:var(--dark);color:#fff}
.close.bare{height:auto;max-width:none;max-height:none;padding:200px 0;background:var(--strip);color:var(--ink)}
.close-shade{position:absolute;inset:0;background:rgba(0,0,0,.5)}
.close-in{position:relative;max-width:714px;padding:0 48px;display:flex;flex-direction:column;align-items:center;gap:30px;text-align:center}
/* foot */
.foot{background:var(--foot);padding:10px 0 0}
.foot-top{padding:10px 0 60px;gap:0 12px;align-items:start}
.foot-brand{grid-column:span 2;padding:20px 10px;display:flex;flex-direction:column;gap:20px}.fine{font:500 12px/1.5 var(--sans);color:var(--fmut)}
.foot-col{grid-column:span 2;padding:10px}.foot-col .ital{margin-bottom:10px}
.fl{font:500 14px/1.5 var(--sans);color:var(--fmut)}.fl li{padding:1px 0}
.foot-tiles{grid-column:9/13;display:grid;grid-template-columns:1fr 1fr;gap:10px;padding:10px 10px 0 0}
.ft{display:flex;align-items:center;justify-content:center;height:110px;padding:0 16px;border-radius:2px;background:var(--tile);font:500 14px/1.5 var(--sans);text-align:center;transition:all .3s var(--ez);overflow-wrap:anywhere}
.ft.wide{grid-column:1/3}.ft.go{background:var(--acc);color:var(--onacc)}.ft:hover{background:var(--ink);color:var(--g)}
.notices{margin:0 22px 40px;display:flex;flex-direction:column;gap:24px}.notice{display:flex;gap:24px;align-items:flex-start;font:500 12px/1.5 var(--sans);color:var(--fmut);max-width:900px}.notice img{width:200px;flex:none}.notice p+p{margin-top:6px}
.word{font:500 var(--ws)/1 var(--cond);text-transform:uppercase;letter-spacing:.06em;white-space:nowrap;text-align:center;overflow:hidden;padding:0 20px;margin:0}
.foot-bot{margin:19px 12px 0;padding:20px 30px;min-height:86px;display:flex;align-items:center;justify-content:center;border-left:1px solid rgba(255,255,255,.4);border-right:1px solid rgba(255,255,255,.4);text-align:center}
@media(max-width:1180px){.tiles .opt{display:none}}
@media(max-width:1180px){.fact dd{font-size:32px}}
@media(max-width:980px){.facts.row{display:block}.facts.row .fact{padding:24px 0;border-left:0;border-top:1px dashed rgba(255,255,255,.3)}.facts.row .fact:first-child{padding-top:0;border-top:0}.tiles.l{display:none}.bar-in{grid-template-columns:auto 1fr}.wd .facts{grid-column:1/8}.side{grid-column:9/13}.foot-brand,.foot-col{grid-column:span 4}.foot-tiles{grid-column:1/13;padding:20px 10px}}
@media(max-width:760px){
.lines i:nth-child(2),.lines i:nth-child(8){display:none}.lines i:nth-child(3){left:60px}.lines i:nth-child(7){left:auto;right:60px}
.bar{padding:15px 20px;height:80px}.bar-in{padding:5px;border-radius:2px;background:rgba(12,14,20,.72);-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px);gap:8px}
.bar.light .bar-in{background:color-mix(in srgb,var(--ink) 9%,var(--g))}
.brand,.bar.light .brand{background:none;-webkit-backdrop-filter:none;backdrop-filter:none}.brand{padding:0 0 0 8px;font-size:13px;letter-spacing:.08em;min-width:0;white-space:normal;line-height:1.15}.logo{width:32px;height:32px}
.tile{min-width:80px;font:500 14px/1 var(--sans);background:none;-webkit-backdrop-filter:none;backdrop-filter:none}.tile.go{background:var(--acc);color:var(--onacc)}
.bar.light .tile{background:none}.bar.light .tile.go{background:var(--acc)}
.tab{display:none}.tab ~ .page .corner.r{padding-right:0}
.hero-in{display:flex;flex-direction:column;justify-content:flex-end;padding:0 0 24px}.hero-mid{position:static;margin:0 62px 12px;flex-direction:column;align-items:stretch;text-align:center;gap:min(169px,13vh)}
.hero-bg:after{background:rgba(0,0,0,.6)}.tagline{font-size:20px;max-width:none}.hero .btn{width:100%}
.mega{font-size:var(--sm);max-width:var(--mm)}.hero .mega{position:static}
.intro{padding:200px 0 100px}.intro-col{grid-column:1/13;margin:0 47px}.state{font-size:26px}
.tall{height:auto;min-height:0;padding-bottom:calc(100vw*var(--r)*1.9)}.tall .fill{top:auto;bottom:0;height:calc(100vw*var(--r)*2.2);max-height:min(1266px,var(--ph))}
.tall-veil{top:auto;bottom:calc(100vw*var(--r)*1.4);height:calc(100vw*var(--r)*.8);background:linear-gradient(to bottom,var(--g) 45%,transparent)}
.tall-col{grid-column:1/13;margin:0 47px;padding:126px 0 40px;position:relative;z-index:1}.tall.bare{padding:0 0 20px}.tall.bare .tall-col{padding:0}
.head{padding:200px 12px 48px}.h60{font-size:32px}.h42{font-size:26px}
.flick-wrap.lone{padding-top:80px}.flick,.flick.n1{flex-direction:column;height:auto;max-height:none;min-height:0;gap:10px;overflow:visible}
.card,.card.on{flex:none;border-radius:4px}.card .card-bg:after,.card.on .card-bg:after{background:color-mix(in srgb,var(--bg) 68%,transparent)}.card-in{position:relative;inset:auto;width:auto;min-height:150px;padding:20px;opacity:1;gap:60px}
.voice{padding:160px 0}.voice-col{grid-column:1/13;margin:0 47px}
.spaces{margin-top:100px}.sp-h{font-size:32px}.sp-note p{grid-column:1/13;margin:0 47px}.spaces.pin .sp-note{top:16%}
.sp-t{font-size:26px}.sp-txt{padding:40px 20px;gap:20px}
.sp-card-in{aspect-ratio:310/398}
.spaces.pin .sp-panel{flex:0 0 100vw}.spaces.pin .sp-card-in{width:min(var(--cw),calc(100vw - 80px))}.spaces.pin .sp-tail{display:none}
.giant{padding-top:100px}
.wh{row-gap:60px}.corner{grid-column:1/7}.corner.r{grid-column:7/13}.wh-c{grid-column:1/13;grid-row:2;margin:0 46px}.where-head{padding-bottom:60px}
.where-dark{padding:60px 10px}.wd{margin:0;row-gap:40px}.wd .facts,.side{grid-column:1/13}.fact dd{font-size:32px}.facts.row{display:block}.facts.row .fact{padding:24px 0;border-left:0;border-top:1px dashed rgba(255,255,255,.3)}.facts.row .fact:first-child{padding-top:0;border-top:0}.facts.row .fact:last-child{padding-bottom:0}.side{padding:0 20px}
.close-in{padding:0 48px}.close.bare{padding:140px 0}
.foot-top{padding:40px 48px}.foot-brand,.foot-col{grid-column:1/13;padding:0 0 30px}.foot-tiles{grid-column:1/13;padding:10px 0 0;margin:0 -36px}.ft{height:100px}
.notice{flex-direction:column}.notices{margin:0 22px 40px}
.foot-bot{padding:20px 10px}
}
@media(prefers-reduced-motion:reduce){*,*:before,*:after{animation:none!important;transition:none!important}.hero{height:var(--vh)}.page{margin-top:0}.mist{display:none}.fade:after{display:none}}
"""

JS = r"""
(function(){var D=document,W=window,R=D.documentElement,rm=W.matchMedia('(prefers-reduced-motion: reduce)').matches;
var bar=D.getElementById('bar'),tab=D.getElementById('tab'),mega=D.getElementById('mega'),mist=D.getElementById('mist'),sp=D.getElementById('spaces');
var tones=[].slice.call(D.querySelectorAll('[data-tone]')),fades=[].slice.call(D.querySelectorAll('[data-fade]')),drift=[].slice.call(D.querySelectorAll('[data-drift]')),slow=[].slice.call(D.querySelectorAll('[data-slow]'));
var last=0,vh=innerHeight,vw=innerWidth,travel=0,LEAD=1100,RATE=.565;
function size(){vh=innerHeight;vw=innerWidth;if(!sp)return;if(rm){sp.classList.remove('pin');return}
 sp.classList.add('pin');var tr=D.getElementById('sp-track');travel=Math.max(0,tr.scrollWidth-vw);sp.style.setProperty('--sh',Math.round(vh+LEAD+travel/RATE)+'px')}
function tick(){var y=W.scrollY||R.scrollTop;
 /* the bar leaves on the way down and returns on the way up */
 if(bar){if(y>last&&y>80)bar.classList.add('away');else if(y<last)bar.classList.remove('away');
  var t='dark';for(var i=0;i<tones.length;i++){var r=tones[i].getBoundingClientRect();if(r.top<=40&&r.bottom>40)t=tones[i].getAttribute('data-tone')}bar.classList.toggle('light',t==='light')}
 if(tab){var ft=D.querySelector('.foot');tab.classList.toggle('in',y>vh*2-200&&!(ft&&ft.getBoundingClientRect().top<vh*.5+110))}
 if(!rm){
  /* opening: title drifts up at .3 and blurs to 10px over two screens; the ground rises at .9 */
  if(y<vh*3.2){if(mega){mega.style.transform='translate3d(0,'+(-.3*Math.min(y,vh*2))+'px,0)';mega.style.filter='blur('+(Math.min(y/(vh*2),1)*10).toFixed(2)+'px)'}
   if(mist)mist.style.transform='translate3d(0,'+(vh-.9*Math.min(y,vh*2))+'px,0)'}
  /* statement: the ink runs down the lines as they rise through the screen */
  fades.forEach(function(el){var r=el.getBoundingClientRect();if(r.bottom<-50||r.top>vh+50)return;var f=(vh*.72-r.top)/(r.height||1);el.style.setProperty('--f',Math.max(-34,Math.min(100,f*100)).toFixed(1)+'%')});
  drift.forEach(function(el){var p=el.closest('section').getBoundingClientRect();if(p.bottom<0||p.top>vh)return;el.style.transform='translate3d(0,'+Math.max(0,Math.min(175,(vh-p.top)*.13-40)).toFixed(1)+'px,0)'});
  slow.forEach(function(el){var p=el.parentNode.getBoundingClientRect();if(p.bottom<0||p.top>vh)return;el.style.transform='translate3d(0,'+(Math.min(0,-p.top)*.31).toFixed(1)+'px,0)'});
  if(sp&&sp.classList.contains('pin')){var d=-sp.getBoundingClientRect().top;if(d>-vh*1.2&&d<vh+LEAD+travel/RATE+vh){
   var h=D.getElementById('sp-h'),n=D.getElementById('sp-note'),tr=D.getElementById('sp-track'),st=sp.querySelectorAll('.sp-strips i');
   if(h){var s=d<0?1+Math.min(-d,vh)/vh*.46:1-Math.min(d,vh)/vh*.333;h.style.transform='scale('+s.toFixed(4)+')'}
   if(n)n.style.transform='translate3d(0,'+(-1.07*Math.max(0,Math.min(d,vh*1.2))).toFixed(1)+'px,0)';
   var w=Math.max(0,Math.min(1,(d-LEAD)/Math.min(1300,travel/RATE*.3||1300)));for(var i=0;i<st.length;i++)st[i].style.setProperty('--w',w.toFixed(4));
   tr.style.transform='translate3d('+(-Math.max(0,Math.min(travel,(d-LEAD)*RATE))).toFixed(1)+'px,0,0)'}}
 }
 last=y;busy=false}
var busy=false;function ask(){if(!busy){busy=true;requestAnimationFrame(tick)}}
W.addEventListener('scroll',ask,{passive:true});W.addEventListener('resize',function(){size();ask()});
if(D.fonts&&D.fonts.ready)D.fonts.ready.then(function(){size();ask()});W.addEventListener('load',function(){size();ask()});
size();tick();
/* a room card reached with the keyboard is brought to the middle of the held screen (the track only moves with the page) */
if(sp)sp.addEventListener('focusin',function(ev){var c=ev.target.closest&&ev.target.closest('.sp-panel');if(!c||!sp.classList.contains('pin')||!(ev.target.matches&&ev.target.matches(':focus-visible')))return;
 var x=Math.max(0,Math.min(travel,c.offsetLeft+c.offsetWidth/2-vw/2));requestAnimationFrame(function(){var pn=sp.querySelector('.sp-pin');if(pn)pn.scrollLeft=0;W.scrollTo(0,sp.getBoundingClientRect().top+(W.scrollY||R.scrollTop)+LEAD+x/RATE)})});
/* the strip of cards: the one under the pointer (or pressed, or focused) opens */
var fl=D.getElementById('flick');if(fl){var cs=[].slice.call(fl.children);function open(c){cs.forEach(function(x){x.classList.toggle('on',x===c)})}
 cs.forEach(function(c){c.addEventListener('mouseenter',function(){if(innerWidth>760)open(c)});c.addEventListener('focusin',function(){open(c)});c.addEventListener('click',function(){open(c)})})}
})();
"""
