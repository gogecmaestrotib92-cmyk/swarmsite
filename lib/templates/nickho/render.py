"""nickho — template rebuilt from https://nickho-motorsports.nl (a racing driver's own site), measured 2026-11-12.
render(d) -> one self-contained page. Pure: no file reads, no model call. See NOTES.md for the measures and the mapping.
The reference's build: a first screen that is one photograph under a dark veil with figures left, facts right, one
giant figure in the middle and the name bottom left; a white screen holding one centred statement in a condensed
display face; a black pinned sequence (title left, upright picture in the middle, words right, n/N); a carousel of
4:3 cards; a black ruled list with the value on the right; a centred call; a photograph that grows to the full window;
a ring of square pictures; a black contact section holding one white card; a white foot."""
import html, json, re

M = '../../'  # media paths in the data are relative to templates/; a page in <slug>/out/ reaches them two levels up


def e(s):
    return html.escape(str(s if s is not None else ''), quote=True)


# ---------- colour ----------
def _rgb(h):
    h = (h or '#000').lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    try:
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return (0, 0, 0)


def _hex(c):
    return '#%02x%02x%02x' % tuple(max(0, min(255, round(v))) for v in c)


def _lum(c):
    f = lambda v: (v / 255 / 12.92) if v / 255 <= .03928 else ((v / 255 + .055) / 1.055) ** 2.4
    return .2126 * f(c[0]) + .7152 * f(c[1]) + .0722 * f(c[2])


def _con(a, b):
    la, lb = _lum(a), _lum(b)
    return (max(la, lb) + .05) / (min(la, lb) + .05)


def _mix(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def _toward(c, to, bg, need):
    """c moved toward `to` in the smallest step at which it reads `need`:1 on bg."""
    for i in range(0, 21):
        m = _mix(c, to, i / 20)
        if _con(m, bg) >= need:
            return m
    return to


def _soft(ink, bg, t, need=4.6):
    """ink held back toward the ground (t = share of ground), but never below `need`:1."""
    while t > 0:
        m = _mix(ink, bg, t)
        if _con(m, bg) >= need:
            return m
        t -= .04
    return ink


# ---------- small parts ----------
CHEV = '<svg class="chev" viewBox="0 0 12 10" width="12" height="10" aria-hidden="true"><path d="M1 1l4 4-4 4M7 1l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>'


def btn(t, h, cls=''):
    if not t:
        return ''
    lab = e(t)
    return (f'<a class="btn {cls}" href="{e(h or "#")}"><span class="btn-l"><span>{lab}</span>'
            f'<span aria-hidden="true">{lab}</span></span>{CHEV}</a>')


def arrows(target, lang):
    prev, nxt = ('Previous', 'Next') if (lang or 'en').startswith('en') else ('‹', '›')
    return (f'<div class="nav2" data-for="{target}"><button type="button" class="arw" data-dir="-1" aria-label="{prev}">'
            f'<svg viewBox="0 0 12 10" width="12" height="10" aria-hidden="true"><path d="M5 1L1 5l4 4M11 1L7 5l4 4" fill="none" stroke="currentColor" stroke-width="1.4"/></svg></button>'
            f'<button type="button" class="arw" data-dir="1" aria-label="{nxt}">'
            f'<svg viewBox="0 0 12 10" width="12" height="10" aria-hidden="true"><path d="M1 1l4 4-4 4M7 1l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.4"/></svg></button></div>')


def sentences(s):
    return [x for x in re.split(r'(?<=[.!?…])\s+', (s or '').strip()) if x]


def paras(s, cls='p'):
    return ''.join(f'<p class="{cls}">{e(x)}</p>' for x in re.split(r'\n{2,}', (s or '').strip()) if x)


def render(d: dict) -> str:
    g = lambda k, dflt=None: d.get(k) if d.get(k) is not None else dflt
    lang = g('lang', 'en') or 'en'
    brand = g('brand', {}) or {}
    name = brand.get('name') or ''
    pal = g('palette', {}) or {}
    ground, ink, accent = _rgb(pal.get('ground') or '#ffffff'), _rgb(pal.get('ink') or '#111111'), _rgb(pal.get('accent') or pal.get('ink') or '#111111')
    # the reference's relations: white sections, black sections, one accent. The lighter of ground/ink is the light
    # ground, the darker one the dark ground (taken down until it reads as the reference's black does: 12:1 to white).
    L, K = (ground, ink) if _lum(ground) >= _lum(ink) else (ink, ground)
    if _lum(L) < .55:
        L = _mix(L, (255, 255, 255), .85)
    K = _toward(K, (0, 0, 0), (255, 255, 255), 12)
    W = (255, 255, 255)
    on_acc = (0, 0, 0) if _con((0, 0, 0), accent) >= _con(W, accent) else W
    if _con(on_acc, accent) < 4.5:  # a mid accent that carries neither black nor white well is deepened
        accent_btn = _toward(accent, (0, 0, 0), W, 4.6); on_acc = W
    else:
        accent_btn = accent
    acc_on_L = _toward(accent, K, L, 3.1)       # accent as large type on the light ground (50px display)
    acc_on_K = _toward(accent, W, K, 3.1)       # accent as a mark on the dark ground
    ink_L = _toward(K, (0, 0, 0), L, 7)         # text on light
    soft_L = _soft(ink_L, L, .5, 5.3)                # the reference's 50 % captions, held at 4.6:1
    soft_K = _soft(W, K, .2, 5.3)
    line_L = _mix(L, ink_L, .12); line_K = _mix(K, W, .2)
    field_L = _mix(L, ink_L, .05)
    ghost_L = _mix(L, ink_L, .045); ghost_K = _mix(K, W, .13)
    arw_L = _mix(L, ink_L, .05)
    card = W if _lum(L) < .93 else W            # the contact card is the reference's white

    media = g('media', {}) or {}
    photos = [p for p in (media.get('photos') or []) if p.get('src')]
    by_src = {p['src']: p for p in photos}
    used = set()

    def img(p, cls='', sizes='100vw', lazy=True, extra=''):
        if not p:
            return ''
        load = 'loading="lazy" decoding="async"' if lazy else 'fetchpriority="high"'
        return (f'<img class="{cls}" src="{M}{e(p["src"])}" width="{int(p.get("w") or 0) or ""}" height="{int(p.get("h") or 0) or ""}" '
                f'alt="{e(p.get("alt") or "")}" {load} {extra}>')

    hero = g('hero', {}) or {}
    steps = g('steps', {}) or {}
    step_items = [s for s in (steps.get('items') or []) if s.get('title') or s.get('text')]
    team = g('team', {}) or {}
    people = list(team.get('items') or [])
    for grp in team.get('groups') or []:
        people += grp.get('items') or []
    people = [p for p in people if p.get('name')]
    projects = [p for p in (g('projects', []) or []) if p.get('title')]

    # ---------- which photograph goes where (each once; never a loop over all of them) ----------
    step_src = [s.get('img') for s in step_items if s.get('img') in by_src]
    team_src = [p.get('img') for p in people if p.get('img') in by_src]

    def wide_ok(p):
        w, h = p.get('w') or 0, p.get('h') or 1
        return (not p.get('small')) and w >= 1400 and w / h >= 1.3 and p.get('role') not in ('portrait', 'product', 'detail', 'people')

    proj_first = {}
    claimed = set(step_src) | set(team_src)
    for i, pr in enumerate(projects):
        for s in pr.get('photos') or []:
            s = s.get('src') if isinstance(s, dict) else s
            if s in by_src and s not in claimed:
                proj_first[i] = s; claimed.add(s); break
    # the two wide slots (first screen, the growing band): a free wide photograph in the data's order; a step's own
    # picture only when it is a landscape (a view, not the step's subject) — that step then stands in type.
    wide = [p for p in photos if wide_ok(p) and (p['src'] not in claimed or (p['src'] in step_src and p.get('role') == 'landscape'))]
    hero_p = wide[0] if wide else None
    band_p = wide[1] if len(wide) > 1 else None
    vid = media.get('video') or None
    for p in (hero_p, band_p):
        if p:
            used.add(p['src'])
    for s in step_src + team_src + list(proj_first.values()):
        used.add(s)
    gallery = [p for p in photos if p['src'] not in used and p.get('role') not in ('portrait', 'people') and min(p.get('w') or 0, p.get('h') or 0) >= 270][:8]
    if len(gallery) < 3:
        gallery = []

    out = []
    A = out.append

    # ---------- header + full-screen menu ----------
    nav = [n for n in (g('nav', []) or []) if n.get('t')]
    cta = g('cta', {}) or {}
    foot = g('foot', {}) or {}
    contact = g('contact', {}) or {}
    place = g('place', {}) or {}
    socials = [x for x in (place.get('social') or []) if x.get('t')] or [x for x in (contact.get('routes') or []) if x.get('t') and not str(x.get('h', '')).startswith(('mailto:', 'tel:'))]
    email = contact.get('email') or place.get('email')
    menu_l = 'Menu' if lang.startswith('en') else 'Menu'
    A(f'<header class="hd"><a class="mark" href="#top">{e(name)}</a>'
      + (f'<button type="button" class="ham" aria-expanded="false" aria-controls="menu" aria-label="{menu_l}"><i></i><i></i></button>' if nav else '') + '</header>')
    if nav:
        A('<nav id="menu" class="menu" aria-label="' + menu_l + '"><div class="ln"></div><ul>'
          + ''.join(f'<li style="--k:{i}"><a href="{e(n.get("h") or "#")}">{e(n["t"])}</a></li>' for i, n in enumerate(nav[:7]))
          + '</ul><div class="menu-b">' + ''.join(f'<a href="{e(s.get("h") or "#")}">{e(s["t"])}</a>' for s in socials[:4])
          + (f'<a href="mailto:{e(email)}">{e(email)}</a>' if email else '') + '</div></nav>')

    A('<main id="top">')

    # ---------- 1 first screen ----------
    figs = [f for f in (g('figures', []) or []) if f.get('v')][:3]
    trust = [t for t in (g('trust', []) or []) if t][:3]
    big = figs[0]['v'] if figs and len(str(figs[0]['v'])) <= 4 else ''
    title = hero.get('title') or name
    tl = len(title)
    h1c = 'h1' + (' s2' if tl > 34 else '') + (' s3' if tl > 64 else '')
    A(f'<section class="hero dk{" nopic" if not hero_p else ""}" data-tone="dk">')
    if hero_p:
        A(f'<div class="hero-pic" data-slot="hero">{img(hero_p, "", "100vw", lazy=False)}</div><div class="hero-veil"></div>')
    A('<div class="ln"></div><div class="hero-g">')
    A('<div class="hero-in">')
    if big:
        A(f'<div class="hero-num" aria-hidden="true">{e(big)}</div>')
    A(f'<div class="hero-head"><h1 class="{h1c}">{e(title)}</h1>' + (f'<p class="p">{e(hero.get("text"))}</p>' if hero.get('text') else '') + '</div>')
    pr, se = hero.get('primary') or {}, hero.get('secondary') or {}
    if pr.get('t') or se.get('t') or hero.get('note'):
        A('<div class="hero-next">' + (f'<p class="p">{e(hero.get("note"))}</p>' if hero.get('note') else '') + '<div class="hero-btns">'
          + (f'<a class="tl" href="{e(se.get("h") or "#")}">{e(se["t"])}</a>' if se.get('t') else '') + btn(pr.get('t'), pr.get('h')) + '</div></div>')
    A('</div>')
    if figs or trust or hero.get('kicker'):
        A('<div class="hero-lists">')
        if figs:
            A('<ul class="stats">' + ''.join(f'<li><b>{e(f["v"])}</b><span>{e(f.get("l") or "")}</span></li>' for f in figs) + '</ul>')
        if trust or hero.get('kicker'):
            A('<ul class="facts">' + (f'<li class="k">{e(hero.get("kicker"))}</li>' if hero.get('kicker') else '') + ''.join(f'<li>{e(t)}</li>' for t in trust) + '</ul>')
        A('</div>')
    A('</div></section>')

    # ---------- 2 the statement ----------
    st = g('statement', {}) or {}
    if st.get('text') or st.get('title'):
        t_is_sentence = bool(st.get('title')) and bool(st.get('text')) and st['title'].strip()[-1:] in '.!?…'
        body = sentences(st.get('text') or st.get('title'))
        parts = []
        if t_is_sentence:
            parts.append(f'<em>{e(st["title"].strip())}</em>')
        for i, s_ in enumerate(body):
            parts.append(f'<em>{e(s_)}</em>' if (len(body) > 1 and i == len(body) - 1) else e(s_))
        n = len((st.get('title') or '') if t_is_sentence else '') + len(st.get('text') or st.get('title') or '')
        hid = f'<h2 class="vh">{e(st["title"])}</h2>' if (st.get('title') and st.get('text') and not t_is_sentence) else ''
        A(f'<section class="say lt" data-tone="lt"><div class="ln"></div><div class="wrap">{hid}<p class="say-t rv{" s2" if n > 260 else ""}{" s3" if n > 420 else ""}">{" ".join(parts)}</p>'
          + (f'<p class="p say-p">{e(hero.get("text2"))}</p>' if hero.get('text2') else '') + '</div></section>')
    elif hero.get('text2'):
        A(f'<section class="call lt" data-tone="lt"><div class="wrap"><p class="p say-p">{e(hero.get("text2"))}</p></div></section>')

    # ---------- the ruled list (the reference's calendar rows), used for everything that is a list with a value ----------
    def rows_section(tone, head, text, groups, note='', hlevel=2, ghost=''):
        """groups: [(title, text, link, [row html])]"""
        if not any(r for _, _, _, r in groups):
            return
        A(f'<section class="list {tone}" data-tone="{tone}"><div class="wrap">')
        if head:
            A(f'<h2 class="h2 c rv">{e(head)}</h2>')
        if text:
            A(f'<p class="p c lead">{e(text)}</p>')
        for gt, gx, gh, rws in groups:
            if not rws:
                continue
            A('<div class="grp">')
            if gt:
                tag = 'h3' if head else 'h2'
                inner = f'<a href="{e(gh)}">{e(gt)}</a>' if gh else e(gt)
                A(f'<{tag} class="h2 c rv">{inner}</{tag}>')
            if gx:
                A(f'<p class="p c lead">{e(gx)}</p>')
            A('<ul class="rows">' + ''.join(rws) + '</ul></div>')
        if note:
            A(f'<p class="p note">{e(note)}</p>')
        A('</div></section>')

    def row(title, sub='', text='', lines=(), right='', right_sub='', h='', extra='', tag='h3', mark=False):
        t = e(title)
        if h:
            t = f'<a href="{e(h)}">{t}</a>'
        return ('<li class="row"><div class="row-l">' + (f'<{tag} class="row-t">{"<i class=sq></i>" if mark else ""}{t}</{tag}>' if title else '')
                + (f'<p class="p row-s">{e(sub)}</p>' if sub else '') + (f'<p class="p row-x">{e(text)}</p>' if text else '')
                + ''.join(f'<p class="p row-x">{e(x)}</p>' for x in lines if x) + extra + '</div>'
                + (f'<div class="row-r">{right}{f"<span class=p>{e(right_sub)}</span>" if right_sub else ""}</div>' if (right or right_sub) else '') + '</li>')

    def price_html(it):
        o = ''
        if it.get('price'):
            pre = 'from ' if (it.get('from') is True and lang.startswith('en') and 'from' not in str(it['price']).lower()) else ''
            o += f'<b class="val">{e(pre + str(it["price"]))}</b>'
        for p_ in it.get('prices') or []:
            if p_.get('price'):
                o += f'<span class="val2"><span class="p">{e(p_.get("label") or "")}</span><b class="val">{e(p_["price"])}</b></span>'
        if it.get('state'):
            o += f'<span class="p st">{e(it["state"])}</span>'
        return o

    # ---------- 3 credentials (the reference's wall of marks; a client's are named, so they stand as ruled rows) ----------
    creds = [c for c in (g('credentials', []) or []) if c.get('t')]
    if creds:
        rws = []
        for c in creds:
            badge = ''
            if c.get('img'):
                bp = by_src.get(c['img'])
                badge = f'<img class="badge" src="{M}{e(c["img"])}" alt="" loading="lazy"' + (f' width="{bp["w"]}" height="{bp["h"]}"' if bp and bp.get('w') else '') + '>'
            rws.append(row(c['t'], '', c.get('text') or '', right=(badge + (f'<b class="val">{e(c["year"])}</b>' if c.get('year') else '')), h=c.get('h') or ''))
        rows_section('lt', '', '', [('', '', '', rws)])
    logos = [l for l in (g('logos', []) or []) if isinstance(l, dict) and l.get('src')]
    if logos:
        A('<section class="wall lt" data-tone="lt"><div class="ln"></div><div class="wrap"><ul class="marks">'
          + ''.join(f'<li><img src="{M}{e(l["src"])}" alt="{e(l.get("alt") or l.get("name") or "")}" loading="lazy"></li>' for l in logos[:24]) + '</ul></div></section>')

    # ---------- 4 the pinned sequence: the person, then the steps ----------
    slides = []
    if len(people) == 1:
        p_ = people[0]
        ex = ''.join(f'<a class="tl" href="{e(h_)}">{e(t_)}</a>' for t_, h_ in ((p_.get('phone'), 'tel:' + re.sub(r'[^+\d]', '', str(p_.get('phone') or ''))), (p_.get('email'), 'mailto:' + str(p_.get('email') or ''))) if t_)
        slides.append(dict(title=p_['name'], sub=p_.get('role') or '', text=p_.get('text') or '', img=by_src.get(p_.get('img')), extra=ex, portrait=True))
    for s_ in step_items:
        c_ = s_.get('cta') or {}
        ph = by_src.get(s_.get('img'))
        if ph and (ph is hero_p or ph is band_p):
            ph = None
        slides.append(dict(title=s_.get('title') or s_.get('k') or '', sub='', text=s_.get('text') or '', img=ph, extra=btn(c_.get('t'), c_.get('h')) if c_.get('t') else ''))
    if steps.get('title') or (steps.get('text') and slides):
        A(f'<section class="call lt intro" data-tone="lt"><div class="wrap">' + (f'<h2 class="h2 c rv">{e(steps.get("title"))}</h2>' if steps.get('title') else '')
          + (f'<p class="p c lead">{e(steps.get("text"))}</p>' if steps.get('text') else '') + '</div></section>')
    if slides:
        n = len(slides)
        A(f'<section class="seq dk" data-tone="dk"><div class="seq-g" style="--n:{n}">')
        for i, s_ in enumerate(slides):
            pic = f'<figure class="sl-p" style="grid-row:{i + 1}" data-slot="slide">{img(s_["img"], "", "(min-width:992px) 302px, 100vw")}</figure>' if s_['img'] else f'<div class="sl-p e" style="grid-row:{i + 1}"></div>'
            A(f'<article class="sl{" on" if i == 0 else ""}" style="--i:{i + 1}"><h3 class="sl-t h2">{e(s_["title"])}</h3>{pic}'
              f'<div class="sl-x">' + (f'<p class="p b">{e(s_["sub"])}</p>' if s_['sub'] else '') + paras(s_['text']) + (f'<div class="sl-a">{s_["extra"]}</div>' if s_['extra'] else '') + '</div></article>')
        if n > 1:
            A(f'<div class="sl-c" aria-hidden="true"><i class="sq"></i><b class="sl-n">1</b>/{n}</div>')
        A('</div></section>')

    # ---------- 5 carousels of 4:3 cards: projects, the people (when there are several) ----------
    def cards_section(cid, head, text, cards):
        if not cards:
            return
        A(f'<section class="media lt" data-tone="lt"' + (f' data-ghost="{e(head)}"' if head else '') + '><div class="wrap">'
          + '<div class="media-h">' + (f'<h2 class="h2 rv">{e(head)}</h2>' if head else '<span></span>') + (arrows(cid, lang) if len(cards) > 3 else (arrows(cid, lang).replace('class="nav2"', 'class="nav2 m-only"') if len(cards) > 1 else '')) + '</div>'
          + (f'<p class="p lead l">{e(text)}</p>' if text else '') + '</div>'
          + f'<div class="car" id="{cid}" tabindex="0"><ul class="car-t">' + ''.join(cards) + '</ul></div></section>')

    pcards = []
    for i, pr_ in enumerate(projects):
        ph = by_src.get(proj_first.get(i))
        if not ph and not pr_.get('text'):
            continue
        inner = (f'<span class="card-p" data-slot="card">{img(ph, "", "(min-width:768px) 416px, 85vw")}</span>' if ph else '') + f'<span class="card-n">{e(pr_["title"])}</span>' + (f'<span class="p card-c">{e(pr_.get("text"))}</span>' if pr_.get('text') else '')
        pcards.append(f'<li class="card">' + (f'<a href="{e(pr_["h"])}">{inner}</a>' if pr_.get('h') else f'<div>{inner}</div>') + '</li>')
    cards_section('car-p', '', '', pcards)
    if len(people) > 1:
        tcards = []
        for p_ in people:
            ph = by_src.get(p_.get('img'))
            ct = ''.join(f'<a class="tl" href="{e(h_)}">{e(t_)}</a>' for t_, h_ in ((p_.get('phone'), 'tel:' + re.sub(r'[^+\d]', '', str(p_.get('phone') or ''))), (p_.get('email'), 'mailto:' + str(p_.get('email') or ''))) if t_)
            tcards.append('<li class="card person"><div>' + (f'<span class="card-p" data-slot="portrait">{img(ph, "", "(min-width:768px) 416px, 85vw")}</span>' if ph else '')
                          + f'<h3 class="card-n">{e(p_["name"])}</h3>' + (f'<span class="p b">{e(p_.get("role"))}</span>' if p_.get('role') else '')
                          + (f'<span class="p card-c">{e(p_.get("text"))}</span>' if p_.get('text') else '') + ct + '</div></li>')
        cards_section('car-t', team.get('title') or '', team.get('text') or '', tcards)

    # ---------- 6 ruled lists: catalogue, plans, features, questions ----------
    tones = ['dk', 'lt']
    ti = 0
    cat = g('catalogue', {}) or {}
    cgroups = []
    cat_names = set()
    for gr in cat.get('groups') or []:
        rws = []
        for it in gr.get('items') or []:
            if not it.get('name'):
                continue
            cat_names.add(it['name'].strip().lower())
            rws.append(row(it['name'], it.get('note') or '', it.get('text') or '', it.get('rows') or (), right=price_html(it), h=it.get('h') or ''))
        cgroups.append((gr.get('t') or '', gr.get('text') or '', gr.get('h') or '', rws))
    if any(r for *_, r in cgroups):
        rows_section(tones[ti % 2], cat.get('title') or '', cat.get('text') or '', cgroups, cat.get('note') or ''); ti += 1
    plans = g('plans', {}) or {}
    pl = [p for p in (plans.get('items') or []) if p.get('name') or p.get('price')]
    if pl:
        rws = [row(p.get('name') or '', p.get('line') or '', '', p.get('rows') or (), right=(f'<b class="val">{e(p["price"])}</b>' if p.get('price') else ''), right_sub=p.get('per') or '',
                   extra=(f'<div class="sl-a">{btn((p.get("cta") or {}).get("t"), (p.get("cta") or {}).get("h"))}</div>' if (p.get('cta') or {}).get('t') else ''), mark=bool(p.get('marked'))) for p in pl]
        rows_section(tones[ti % 2], plans.get('title') or '', plans.get('text') or '', [('', '', '', rws)], plans.get('note') or ''); ti += 1
    feats = g('features', {}) or {}
    fi = [f for f in (feats.get('items') or []) if f.get('t')]
    if fi and not (cat_names and all(f['t'].strip().lower() in cat_names for f in fi)):
        rows_section(tones[ti % 2], feats.get('title') or '', feats.get('text') or '', [('', '', '', [row(f['t'], '', f.get('d') or '') for f in fi])]); ti += 1
    faq = g('faq', {}) or {}
    qs = [q for q in (faq.get('items') or []) if q.get('q')]
    if qs:
        rows_section(tones[ti % 2], faq.get('title') or '', '', [('', '', '', [row(q['q'], '', q.get('a') or '') for q in qs])]); ti += 1

    # ---------- 7 what others (or the person) say: the statement part again, one at a time ----------
    quotes = [q for q in (g('quotes', []) or []) if isinstance(q, dict) and q.get('q')]
    if quotes:
        A('<section class="quotes lt" data-tone="lt"><div class="ln"></div><div class="car q" id="car-q" tabindex="0"><ul class="car-t">')
        for q in quotes:
            n = len(q['q'])
            cls = 'qa' if n <= 170 else ('qb' if n <= 330 else 'qc')
            who = ' · '.join(x for x in (q.get('name'), q.get('role')) if x)
            A(f'<li class="qi"><figure><blockquote class="{cls}">{e(q["q"])}</blockquote>' + (f'<figcaption class="p b">{e(who)}</figcaption>' if who else '') + '</figure></li>')
        A('</ul></div>' + (f'<div class="wrap qn">{arrows("car-q", lang)}</div>' if len(quotes) > 1 else '') + '</section>')

    # ---------- 8 the call ----------
    close = g('close', {}) or {}
    if close.get('title') or close.get('text'):
        cc = close.get('cta') or {}
        A('<section class="call lt" data-tone="lt"><div class="ln"></div><div class="wrap">' + (f'<h2 class="h2 c rv">{e(close.get("title"))}</h2>' if close.get('title') else '')
          + (f'<p class="p c lead">{e(close.get("text"))}</p>' if close.get('text') else '') + (f'<div class="c">{btn(cc.get("t"), cc.get("h"))}</div>' if cc.get('t') else '') + '</div></section>')

    # ---------- 9 the picture that grows to the window ----------
    if vid and vid.get('src'):
        A(f'<section class="band lt" data-tone="lt"><div class="band-w" data-slot="band"><video src="{M}{e(vid["src"])}"' + (f' poster="{M}{e(vid["poster"])}"' if vid.get('poster') else '')
          + f' muted loop playsinline autoplay preload="metadata" aria-label="{e(vid.get("alt") or "")}"></video></div></section>')
    elif band_p:
        A(f'<section class="band lt" data-tone="lt"><div class="band-w" data-slot="band">{img(band_p, "", "100vw")}</div></section>')

    # ---------- 10 the ring of square pictures ----------
    if gallery:
        start = (len(gallery) - 1) // 2
        A(f'<section class="gal lt" data-tone="lt" data-ghost="{e(name)}"><div class="ring" id="ring" data-start="{start}" style="--i:{start}"><ul class="ring-t">'
          + ''.join(f'<li style="--k:{i}"{" class=on" if i == start else ""} data-slot="ring">{img(p, "", "270px")}</li>' for i, p in enumerate(gallery))
          + '</ul><div class="ring-f"></div><div class="dial" aria-hidden="true">' + ''.join(f'<i style="--k:{i}"{" class=on" if i == start else ""}></i>' for i in range(len(gallery))) + '<b class="sq"></b></div></div>'
          + f'<div class="ring-n">{arrows("ring", lang)}</div></section>')

    # ---------- 11 contact: one white card on the dark ground ----------
    boxes = []
    ph_ = contact.get('phone') or place.get('phone') or {}
    if ph_.get('t'):
        boxes.append(f'<a class="fld" href="{e(ph_.get("h") or "tel:" + re.sub(r"[^+0-9]", "", ph_["t"]))}">{e(ph_["t"])}</a>')
    if email:
        boxes.append(f'<a class="fld" href="mailto:{e(email)}">{e(email)}</a>')
    note = ph_.get('note') or ''
    for r_ in contact.get('routes') or []:
        if not r_.get('t'):
            continue
        if email and str(r_.get('h', '')).lower() == 'mailto:' + email.lower():
            note = note or r_.get('note') or ''
            continue
        boxes.append(f'<a class="fld" href="{e(r_.get("h") or "#")}">{e(r_["t"])}' + (f'<span>{e(r_["note"])}</span>' if r_.get('note') else '') + '</a>')
    if not (contact.get('routes')):
        for s_ in place.get('social') or []:
            if s_.get('t'):
                boxes.append(f'<a class="fld" href="{e(s_.get("h") or "#")}">{e(s_["t"])}</a>')

    def addr(a):
        return ', '.join(str(a[k]) for k in ('street', 'postcode', 'city', 'region', 'country') if a.get(k))
    wides = []
    if place.get('address'):
        wides.append(f'<p class="fld w">{e(addr(place["address"]))}</p>')
    for h_ in place.get('hours') or []:
        if h_.get('days'):
            wides.append(f'<p class="fld w">{e(h_["days"])}' + (f'<span>{e(" – ".join(x for x in (h_.get("open"), h_.get("close")) if x))}</span>' if h_.get('open') else '') + '</p>')
    for lc in g('locations', []) or []:
        if lc.get('name'):
            bits = [addr(lc.get('address') or {}), (lc.get('phone') or {}).get('t') if isinstance(lc.get('phone'), dict) else lc.get('phone'), lc.get('email'), lc.get('note')]
            wides.append(f'<p class="fld w"><b>{e(lc["name"])}</b><span>{e(" · ".join(str(b) for b in bits if b))}</span></p>')
    form = contact.get('form') or {}
    bk = place.get('booking') or {}
    c_btn = btn(form.get('t'), form.get('h')) if form.get('t') else (btn(bk.get('t'), bk.get('h')) if bk.get('t') else '')
    if boxes or wides or c_btn:
        ch = cta.get('t') or form.get('t') or ''
        A(f'<section class="contact dk" data-tone="dk"' + (f' data-ghost="{e(ch)}"' if ch else '') + '><div class="wrap"><div class="ccard"><div class="cc-l">'
          + (f'<h2 class="h2 rv">{e(ch)}</h2>' if ch else '') + (f'<p class="p">{e(note)}</p>' if note else '') + '</div><div class="cc-r">'
          + ''.join(boxes) + ''.join(wides) + (f'<div class="cc-b">{c_btn}</div>' if c_btn else '') + '</div></div></div></section>')

    A('</main>')

    # ---------- 12 foot ----------
    nav_t = {n['t'].strip().lower() for n in nav}
    links = [l for l in (g('links', []) or []) if l.get('t') and l['t'].strip().lower() not in nav_t]
    fl = [l for l in (foot.get('links') or []) if l.get('t')]
    cols = []
    if nav:
        cols.append(''.join(f'<li><a href="{e(n.get("h") or "#")}">{e(n["t"])}</a></li>' for n in nav))
    if links:
        cols.append(''.join(f'<li><a href="{e(l.get("h") or "#")}">{e(l["t"])}</a></li>' for l in links[:8]))
    if fl:
        cols.append(''.join(f'<li><a href="{e(l.get("h") or "#")}">{e(l["t"])}</a></li>' for l in fl))
    cc = ''
    if ph_.get('t'):
        cc += f'<li><a href="{e(ph_.get("h") or "#")}">{e(ph_["t"])}</a></li>'
    if email:
        cc += f'<li><a href="mailto:{e(email)}">{e(email)}</a></li>'
    if cc:
        cols.append(cc)
    A('<footer class="ft lt" data-tone="lt"><div class="ln"></div><div class="wrap"><div class="ft-g"><a class="ft-m" href="#top">' + e(name) + '</a>'
      + ''.join(f'<ul>{c}</ul>' for c in cols[:4]) + '</div><div class="ft-b">' + (f'<span>{e(foot.get("legal"))}</span>' if foot.get('legal') else '<span></span>')
      + (f'<span>{e(foot.get("text"))}</span>' if foot.get('text') else '') + '</div></div></footer>')

    css = CSS
    for k, v in dict(L=L, K=K, A=accent_btn, OA=on_acc, AL=acc_on_L, AK=acc_on_K, IL=ink_L, SL=soft_L, SK=soft_K, LL=line_L, LK=line_K, FL=field_L, GL=ghost_L, GK=ghost_K, RL=arw_L, CARD=card).items():
        css = css.replace('{{' + k + '}}', _hex(v))
    desc = hero.get('text') or st.get('text') or ''
    return ('<!doctype html><html lang="' + e(lang) + '"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{e(name)}{" — " + e(hero.get("title")) if hero.get("title") and hero.get("title") != name else ""}</title>'
            + (f'<meta name="description" content="{e(desc[:160])}">' if desc else '')
            + '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link href="https://fonts.googleapis.com/css2?family=Anton&display=swap" rel="stylesheet">'
                        f'<style>{css}</style></head><body>' + ''.join(out) + f'<script>{JS}</script></body></html>')


CSS = r"""
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{margin:0;background:{{L}};color:{{IL}};font:400 14px/1.4 "Helvetica Neue",Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased;overflow-x:hidden}
img,video{display:block;max-width:100%}
a{color:inherit;text-decoration:none}
ul{list-style:none;margin:0;padding:0}
h1,h2,h3,p,figure,blockquote{margin:0}
.vh{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.wrap{position:relative;padding:0 80px;max-width:1600px;margin:0 auto}
.p{font-size:14px;line-height:1.4}
.p.b,.b{font-weight:700}
.c{text-align:center}
.lt{background:{{L}};color:{{IL}}}
.dk{background:{{K}};color:#fff}
.lt :focus-visible{outline:2px solid {{IL}};outline-offset:3px}
.dk :focus-visible,.menu :focus-visible{outline:2px solid #fff;outline-offset:3px}
.menu :focus-visible{outline-color:{{OA}}}
section,footer{position:relative}
/* the seven hairlines that run down the reference's light and photographic sections */
.ln{position:absolute;inset:0;pointer-events:none;background:linear-gradient(90deg,{{LL}} 0 1px,transparent 1px) -1px 0/calc(100%/7) 100%;opacity:.45}
.dk .ln,.menu .ln{background-image:linear-gradient(90deg,rgba(255,255,255,.2) 0 1px,transparent 1px);opacity:1}
.menu .ln{opacity:.35}
/* display face */
.h1,.h2,.say-t,.row-t,.val,.hero-num,.stats b,.card-n,.mark,.ft-m,.btn,.menu a,.sl-c,.qa,.qb{font-family:Anton,"Arial Narrow",Impact,sans-serif;font-weight:400;text-transform:uppercase;letter-spacing:0}
.h1{font-size:50px;line-height:1.1}
.h1.s2{font-size:40px}.h1.s3{font-size:32px}
.h2{font-size:50px;line-height:1.1}
.lead{max-width:611px;margin:20px auto 0}
.lead.l{margin-left:0}
.sq{display:inline-block;width:12px;height:12px;background:{{AK}};margin-right:10px}
.lt .sq{background:{{AL}}}
/* button: accent block, 40 high, radius 4, the label rolls on hover (0.6s), the block gives on press (0.15s) */
.btn{display:inline-flex;align-items:center;gap:8px;min-height:40px;padding:12px 16px;border-radius:4px;background:{{A}};color:{{OA}};font-size:16px;line-height:1;transition:scale .15s cubic-bezier(.4,0,.2,1);max-width:100%}
.btn-l{display:grid;overflow:hidden;line-height:1;text-align:left}
.btn-l>span{grid-area:1/1;padding:1px 0;transition:translate .6s cubic-bezier(.19,1,.22,1)}
.btn-l>span+span{translate:0 110%;visibility:hidden}
.btn .chev{flex:none;transition:translate .6s cubic-bezier(.19,1,.22,1)}
@media(hover:hover){.btn:hover .btn-l>span{translate:0 -110%}.btn:hover .btn-l>span+span{translate:0 0;visibility:visible}.btn:hover .chev{translate:3px 0}}
.btn:active{scale:.96}
.tl{text-decoration:underline;text-underline-offset:3px;text-decoration-thickness:1px}
/* header */
.hd{position:absolute;inset:0 0 auto 0;z-index:30;height:0}
.mark{position:absolute;left:80px;top:30px;font-size:20px;line-height:30px;color:#fff;white-space:nowrap;max-width:calc(100vw - 220px);overflow:hidden;text-overflow:ellipsis}
.open .mark{color:{{OA}}}
.ham{position:fixed;right:80px;top:30px;width:30px;height:30px;border:0;border-radius:2px;background:{{A}};color:{{OA}};cursor:pointer;padding:0;display:none;z-index:2;transition:background .5s cubic-bezier(.7,0,.3,1) .3s,color .5s cubic-bezier(.7,0,.3,1) .3s}
.ready .ham{display:block}
.ready.open .ham{background:{{OA}};color:{{A}}}
.ham i{position:absolute;left:9px;right:9px;height:2px;background:currentColor;top:11px;transition:transform .5s cubic-bezier(.7,0,.3,1)}
.ham i+i{top:17px}
.open .ham i{transform:translateY(3px) rotate(45deg)}.open .ham i+i{transform:translateY(-3px) rotate(-45deg)}
.menu{display:none}
.ready .menu{display:flex;position:fixed;inset:0;z-index:20;background:{{A}};color:{{OA}};flex-direction:column;align-items:center;justify-content:center;transform:translateY(-101%);visibility:hidden;transition:transform .75s cubic-bezier(.7,0,.3,1),visibility 0s .75s}
.ready.open .menu{transform:none;visibility:visible;transition:transform .75s cubic-bezier(.7,0,.3,1)}
.menu ul{display:flex;flex-direction:column;align-items:center;gap:24px;position:relative}
.menu li{overflow:hidden}
.menu li a{display:block;font-size:64px;line-height:1;padding:0 7px;transform:translateY(105%);transition:transform .75s cubic-bezier(.7,0,.3,1) calc(var(--k)*.05s)}
.open .menu li a{transform:none}
.menu-b{position:absolute;left:0;right:0;bottom:0;padding:36px 40px;display:flex;gap:32px;justify-content:center;flex-wrap:wrap;font-size:14px}
/* 1 first screen */
.hero{min-height:100vh;overflow:hidden;display:flex}
.hero-pic,.hero-veil{position:absolute;inset:0}
.hero-pic img{width:100%;height:100%;object-fit:cover;filter:grayscale(1);scale:1.03;translate:var(--px,0) var(--py,0);transition:translate .8s cubic-bezier(.19,1,.22,1)}
/* the veil is laid for the brightest pixel a photograph can have: .64 under the small words at the sides, .5 under the giant figure, rising to .86 at the foot */
.hero-veil{background:linear-gradient(0deg,rgba(0,0,0,.72),rgba(0,0,0,0) 46%),linear-gradient(90deg,rgba(0,0,0,.66) 0,rgba(0,0,0,.66) 30%,rgba(0,0,0,.5) 42%,rgba(0,0,0,.5) 58%,rgba(0,0,0,.66) 70%,rgba(0,0,0,.66) 100%)}
.hero-g{position:relative;flex:1;display:grid;grid-template-columns:minmax(0,1fr) auto minmax(0,1fr);grid-template-rows:1fr auto;column-gap:40px;row-gap:48px;padding:80px 80px 60px;min-height:100vh}
.hero-in,.hero-lists{display:contents}
.stats{grid-area:1/1;align-self:start;margin-top:min(204px,22.6vh);display:grid;gap:22px;max-width:260px}
.stats b{display:block;font-size:32px;line-height:1}
.stats span{display:block;margin-top:6px;font-size:14px;line-height:1.4}
.facts{grid-area:1/3;align-self:start;justify-self:end;margin-top:min(204px,22.6vh);text-align:right;display:grid;gap:14px;max-width:240px}
.facts .k{font-weight:700}
.hero-num{grid-area:1/2;align-self:center;justify-self:center;font-size:200px;line-height:1;padding-top:6vh;color:#fff}
.hero-head{grid-area:2/1/3/3;align-self:end;max-width:547px}
.hero-head .p{margin-top:20px;max-width:420px}
.hero-next{grid-area:2/3;align-self:end;justify-self:end;text-align:right;max-width:420px}
.hero-next .p{margin-bottom:12px}
.hero-btns{display:flex;gap:20px;align-items:center;justify-content:flex-end;flex-wrap:wrap}
/* 2 the statement */
.say{min-height:100vh;display:flex;align-items:center;padding:128px 0}
.say .wrap{width:100%}
.say-t{font-size:50px;line-height:1.1;text-align:center;max-width:660px;margin:0 auto}
.say-t.s2{font-size:40px;max-width:720px}.say-t.s3{font-size:32px;max-width:760px}
.say-t em{font-style:normal;color:{{AL}}}
.say-p{max-width:611px;margin:40px auto 0;text-align:center}
/* the call */
.call{padding:192px 0}
.call .h2{max-width:640px;margin:0 auto}
.call .btn{margin-top:28px}
.call.intro{padding:128px 0 112px}
.call+.call,.say+.call,.list.lt+.call{padding-top:64px}
/* 4 the pinned sequence */
.seq-g{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));column-gap:16px;row-gap:42px;padding:233px 80px 305px;max-width:1600px;margin:0 auto}
.sl{display:contents}
.sl-t{grid-column:1/5;grid-row:var(--i);align-self:center}
.sl-p{grid-column:5/8;height:362px;overflow:hidden;position:relative}
.sl-p img{position:absolute;left:0;top:-10%;width:100%;height:120%;object-fit:cover}
.sl-x{grid-column:9/13;grid-row:var(--i);align-self:center}
.sl-x .p+.p{margin-top:12px}
.sl-a{margin-top:20px;display:flex;gap:16px;flex-wrap:wrap}
.sl-c{display:none;font-size:26px;line-height:1}
@media(min-width:992px){
.ready .sl-t,.ready .sl-x{grid-row:1/span var(--n);align-self:start;position:sticky;top:50vh;transform:translateY(-50%);opacity:0;visibility:hidden;transition:opacity .45s cubic-bezier(.19,1,.22,1),visibility 0s .45s}
.ready .sl.on .sl-t,.ready .sl.on .sl-x{opacity:1;visibility:visible;transition:opacity .45s cubic-bezier(.19,1,.22,1) .1s}
.ready .sl-p img{filter:grayscale(1);opacity:.32;transition:filter .5s,opacity .5s;translate:0 var(--py,0)}
.ready .sl.on .sl-p img{filter:none;opacity:1}
.ready .sl-c{display:block;grid-column:11/13;grid-row:1/span var(--n);justify-self:end;align-self:start;position:sticky;top:calc(100vh - 103px)}
}
/* 5 cards */
.media{padding:128px 0;overflow:hidden}
.media-h{display:flex;justify-content:space-between;align-items:flex-end;gap:24px}
.nav2{display:flex;gap:8px;flex:none}
.arw{width:76px;height:46px;border:0;border-radius:4px;background:{{RL}};color:{{IL}};cursor:pointer;display:grid;place-items:center;transition:transform .2s,opacity .2s}
.arw:active{transform:scale(.95)}
.arw[disabled]{opacity:.45;cursor:default}
.nav2{display:none}.ready .nav2{display:flex}
.car{margin-top:32px;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none;scroll-padding-left:80px;-webkit-overflow-scrolling:touch}
.car::-webkit-scrollbar{display:none}
.car-t{display:flex;gap:16px;padding:0 80px;width:max-content}
.card{width:416px;scroll-snap-align:start}
.card>a,.card>div{display:block}
.card-p{display:block;height:312px;overflow:hidden;margin-bottom:16px}
.card-p img{width:100%;height:100%;object-fit:cover;transition:filter .5s,scale .8s cubic-bezier(.19,1,.22,1)}
@media(hover:hover){.card-p img{filter:grayscale(1)}.card:hover .card-p img{filter:none;scale:1.03}}
.card-n{display:block;font-size:26px;line-height:1.05;margin:0}
.card .p{display:block;margin-top:8px}
.card-c{color:{{SL}}}
.card .tl{display:inline-block;margin:10px 16px 0 0}
.media[data-ghost]::before,.gal[data-ghost]::before,.contact[data-ghost]::before{content:attr(data-ghost);position:absolute;left:24px;top:8px;font:400 190px/1 Anton,"Arial Narrow",Impact,sans-serif;text-transform:uppercase;white-space:nowrap;color:{{GL}};transform-origin:0 0;transform:scaleX(var(--gx,1));pointer-events:none;-webkit-mask-image:linear-gradient(#000 30%,transparent 105%);mask-image:linear-gradient(#000 30%,transparent 105%)}
.contact[data-ghost]::before{color:{{GK}}}
.media,.gal,.contact{overflow:hidden}
/* 6 ruled list */
.list{padding:128px 0}
.list.lt+.list.lt,.call+.list.lt,.say+.list.lt{padding-top:32px}
.grp+.grp{margin-top:112px}
.rows{margin-top:64px}
.h2+.rows{margin-top:112px}
.row{display:flex;justify-content:space-between;align-items:flex-end;gap:40px;padding:0 0 10px;border-bottom:1px solid {{LK}}}
.lt .row{border-color:{{LL}}}
.row+.row{margin-top:32px}
.row-l{min-width:0;max-width:760px}
.row-t{font-size:26px;line-height:1;display:flex;align-items:baseline}
.row-t .sq{flex:none}
.row-s{margin-top:5px}
.row-x{margin-top:8px;color:{{SK}}}
.lt .row-x{color:{{SL}}}
.row-r{flex:none;text-align:right;display:grid;gap:6px;justify-items:end;max-width:42%}
.val{font-size:26px;line-height:1}
.val2{display:flex;gap:12px;align-items:baseline}
.badge{height:96px;width:auto;max-width:160px;object-fit:contain}
.note{margin-top:40px;max-width:760px;color:{{SK}}}
.lt .note{color:{{SL}}}
.row a:hover,.ft a:hover,.fld:hover{text-decoration:underline;text-underline-offset:3px}
/* wall of marks */
.wall{padding:128px 0}
.marks{display:grid;grid-template-columns:repeat(4,177px);justify-content:space-between;row-gap:32px}
.marks li{height:118px;display:grid;place-items:center}
.marks li:nth-child(4n+2),.marks li:nth-child(4n+3){transform:translateY(-86px)}
.marks img{width:89px;height:54px;object-fit:contain;filter:grayscale(1)}
/* 7 quotes */
.quotes{padding:128px 0}
.car.q{margin-top:0;scroll-padding-left:0}
.car.q .car-t{padding:0;gap:0;width:auto}
.qi{flex:0 0 100%;scroll-snap-align:start;display:grid;place-items:center;padding:0 80px}
.qi figure{max-width:760px;text-align:center}
.qa{font-size:40px;line-height:1.1}.qb{font-size:26px;line-height:1.15}
.qc{font-size:16px;line-height:1.55;max-width:640px;margin:0 auto}
.qi figcaption{margin-top:24px}
.qn{display:flex;justify-content:center;margin-top:40px}
/* 9 the growing picture */
.band{height:100vh;min-height:520px;display:flex;align-items:flex-end;justify-content:center;overflow:hidden}
.band-w{width:100%;height:100%;overflow:hidden;will-change:width,height}
.band-w img,.band-w video{width:100%;height:100%;object-fit:cover}
/* 10 ring */
.gal{padding:200px 0 128px}
.ring{overflow-x:auto;scrollbar-width:none}
.ring-t{display:flex;gap:16px;padding:0 80px;width:max-content}
.ring-t li{width:270px;height:270px;overflow:hidden;flex:none}
.ring-t img{width:100%;height:100%;object-fit:cover}
.ring-f,.dial,.ring-n{display:none}
.ready .ring{position:relative;height:512px;overflow:hidden}
.ready .ring-t{display:block;position:absolute;left:50%;top:715px;width:0;height:0;padding:0;transform:rotate(calc(var(--i)*-45deg));transition:transform .64s cubic-bezier(.19,1,.22,1)}
.ready .ring-t li{position:absolute;left:-135px;top:-135px;transform:rotate(calc(var(--k)*45deg)) translateY(-560px)}
.ready .ring-t img{filter:grayscale(1);transition:filter .5s}
.ready .ring-t li.on img{filter:none}
.ready .ring-f{display:block;position:absolute;left:0;right:0;bottom:0;height:192px;background:linear-gradient(0deg,{{L}},transparent);pointer-events:none}
.ready .dial{display:block;position:absolute;left:50%;bottom:22px;width:126px;height:68px;margin-left:-63px}
.dial i{position:absolute;left:50%;bottom:6px;width:2px;height:14px;margin-left:-1px;background:{{IL}};transform-origin:50% 100%;transform:rotate(calc((var(--k) - var(--i))*30deg)) translateY(-34px);transition:transform .64s cubic-bezier(.19,1,.22,1),background .3s,height .3s}
.dial i.on{background:{{AL}};height:22px;width:4px;margin-left:-2px}
.dial .sq{position:absolute;left:50%;bottom:0;margin:0 0 0 -6px;background:{{AL}}}
.ready .ring-n{display:flex;justify-content:center;margin-top:32px}
.ring-n .nav2{gap:16px}
/* 11 contact */
.contact{padding:128px 0}
.ccard{position:relative;max-width:1063px;margin:0 auto;background:{{CARD}};color:{{IL}};border-radius:8px;padding:64px;display:grid;grid-template-columns:258px minmax(0,1fr);gap:36px}
.ccard :focus-visible{outline:2px solid {{IL}};outline-offset:3px}
.cc-l .p{margin-top:8px;color:{{SL}}}
.cc-r{display:grid;grid-template-columns:1fr 1fr;gap:16px;align-content:start}
.fld{display:block;background:{{FL}};border-radius:4px;padding:10px 16px;min-height:37px;font-size:14px;line-height:1.3;overflow-wrap:anywhere;margin:0}
.fld.w{grid-column:1/-1}
.fld span{display:block;color:{{SL}};margin-top:2px}
.cc-b{grid-column:1/-1;margin-top:8px}
/* 12 foot */
.ft{padding:128px 0 32px}
.ft-g{display:grid;grid-template-columns:minmax(0,6fr) repeat(4,minmax(0,2fr));column-gap:16px;row-gap:40px}
.ft-m{font:400 32px/1 Anton,"Arial Narrow",Impact,sans-serif;text-transform:uppercase;align-self:start}
.ft ul{display:grid;gap:24px;align-content:start}
.ft li{min-width:0;overflow-wrap:anywhere}
.ft li a{color:{{SL}}}
.ft-b{display:flex;justify-content:space-between;gap:24px;flex-wrap:wrap;margin-top:128px;color:{{SL}}}
/* reveals: a heading rises from its own line as it enters (only when scripts run) */
.ready .rv{clip-path:inset(0 0 100% 0);transform:translateY(28px);transition:clip-path .9s cubic-bezier(.19,1,.22,1),transform .9s cubic-bezier(.19,1,.22,1)}
.ready .rv.in{clip-path:inset(-10% 0 -20% 0);transform:none}
/* tablet */
@media(max-width:991px){
.wrap{padding:0 40px}
.mark{left:40px}.ham{right:40px}
.hero-g{padding:80px 40px 48px;column-gap:24px}
.hero-num{font-size:150px}
.seq-g{display:block;padding:96px 40px;max-width:640px}
.sl{display:block}.sl+.sl{margin-top:72px}
.sl-p{height:auto;aspect-ratio:1/1;margin-bottom:24px}.sl-p.e{display:none}
.sl-p img{top:0;height:100%}
.sl-t{margin-bottom:12px}
.car{scroll-padding-left:40px}.car-t{padding:0 40px}.qi{padding:0 40px}
.ccard{grid-template-columns:1fr;padding:40px}
.ft-g{grid-template-columns:repeat(2,minmax(0,1fr))}.ft-m{grid-column:1/-1}
.marks{grid-template-columns:repeat(2,177px);justify-content:space-around}.marks li:nth-child(n){transform:none}.marks li:nth-child(2n){transform:translateY(40px)}
.m-only{display:flex}
}
@media(min-width:992px){.m-only{display:none!important}}
/* phone: the reference at 390 — 29 side margin, display 37, statement 29, body 15 */
@media(max-width:767px){
body,.p,.fld,.stats span{font-size:15px}
.wrap{padding:0 30px}
.mark{left:30px;top:27px;font-size:18px;max-width:calc(100vw - 110px)}.ham{right:30px;top:27px}
.h1,.h2{font-size:37px}.h1.s2{font-size:31px}.h1.s3{font-size:26px}
.menu li a{font-size:56px}.menu-b{padding:28px 30px;gap:20px}
.hero{display:block;min-height:0}
.hero-pic,.hero-veil{bottom:auto;height:100vh;height:100svh}
.hero-veil{background:linear-gradient(0deg,{{K}},rgba(0,0,0,.62) 46%,rgba(0,0,0,.5) 72%,rgba(0,0,0,.7) 100%)}
.hero .ln{bottom:auto;height:100svh;background-size:calc(100%/3) 100%}
.hero-g{display:block;padding:0;min-height:0}
.hero-in{display:grid;grid-template-rows:1fr auto auto;min-height:100vh;min-height:100svh;padding:73px 30px 30px}
.hero-num{grid-area:auto;font-size:146px;padding:0}
.hero-head{grid-area:auto;max-width:none}.hero-head .p{margin-top:14px;max-width:none}
.hero-next{grid-area:auto;justify-self:start;text-align:left;margin-top:24px}
.hero-btns{justify-content:flex-start;flex-direction:row-reverse}
.hero-lists{display:grid;gap:36px;padding:44px 30px 64px;position:relative;background:{{K}}}
.stats,.facts{grid-area:auto;margin:0;max-width:none;text-align:left;justify-self:start}
.say{min-height:0;padding:96px 0}
.say-t{font-size:29px}.say-t.s2{font-size:26px}.say-t.s3{font-size:23px}
.call{padding:96px 0}.call.intro{padding:80px 0 72px}
.seq-g{padding:72px 30px}
.sl+.sl{margin-top:64px}
.media,.list,.quotes,.contact,.wall{padding:80px 0}
.media-h{align-items:center}
.arw{width:70px;height:44px}
.car{scroll-padding-left:30px;margin-top:24px}.car-t{padding:0 30px}
.card{width:min(332px,calc(100vw - 58px))}.card-p{height:auto;aspect-ratio:4/3}
.card-n{font-size:22px}
.media[data-ghost]::before,.gal[data-ghost]::before,.contact[data-ghost]::before{font-size:110px;left:12px}
.rows{margin-top:40px}.h2+.rows{margin-top:56px}.grp+.grp{margin-top:72px}
.row{display:block;padding-bottom:15px}.row+.row{margin-top:18px}
.row-t{font-size:19px;line-height:1.05}.val{font-size:19px}
.row-r{text-align:left;justify-items:start;max-width:none;margin-top:8px}
.badge{height:72px;margin-top:6px}
.qi{padding:0 30px}.qa{font-size:29px}.qb{font-size:21px}
.band{height:70vh}
.gal{padding:120px 0 80px}
.ready .ring{height:440px}
.ready .ring-t{top:538px}
.ready .ring-t li,.ring-t li{width:236px;height:236px}
.ready .ring-t li{left:-118px;top:-118px;transform:rotate(calc(var(--k)*45deg)) translateY(-420px)}
.ccard{padding:30px;gap:24px}.cc-r{grid-template-columns:1fr}
.ft{padding:88px 0 28px}.ft ul{gap:18px}.ft-b{margin-top:72px;display:grid;gap:10px}
}
@media(prefers-reduced-motion:reduce){
html{scroll-behavior:auto}
*,*::before,*::after{transition-duration:.01ms!important;transition-delay:0s!important;animation:none!important}
.ready .rv{clip-path:none;transform:none}
.hero-pic img{translate:none!important;scale:1}
.ready .sl-p img{translate:none!important}
}
"""

JS = r"""
(function(){
var R=document.documentElement,mq=function(q){return window.matchMedia(q).matches},still=mq('(prefers-reduced-motion: reduce)');
var $=function(s,c){return Array.prototype.slice.call((c||document).querySelectorAll(s))};
/* menu */
var ham=document.querySelector('.ham'),menu=document.getElementById('menu');
function setMenu(o){R.classList.toggle('open',o);if(ham)ham.setAttribute('aria-expanded',o?'true':'false')}
if(ham&&menu){ham.addEventListener('click',function(){setMenu(!R.classList.contains('open'))});
 menu.addEventListener('click',function(ev){if(ev.target.closest('a'))setMenu(false)});
 document.addEventListener('keydown',function(ev){if(ev.key==='Escape'&&R.classList.contains('open')){setMenu(false);ham.focus()}})}
/* reveals */
var rv=$('.rv');
if('IntersectionObserver' in window&&!still){var io=new IntersectionObserver(function(es){es.forEach(function(x){if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target)}})},{rootMargin:'0px 0px -8% 0px'});rv.forEach(function(x){io.observe(x)})}
else rv.forEach(function(x){x.classList.add('in')});
/* ghost words are stretched to the width of the page, as the reference's are */
function ghosts(){$('[data-ghost]').forEach(function(s){var c=document.createElement('canvas').getContext('2d');var fs=parseFloat(getComputedStyle(s,'::before').fontSize)||190;c.font='400 '+fs+'px Anton, "Arial Narrow", Impact, sans-serif';var w=c.measureText(s.getAttribute('data-ghost').toUpperCase()).width;if(w>0){var l=parseFloat(getComputedStyle(s,'::before').left)||24;s.style.setProperty('--gx',Math.max(.5,Math.min(4,(s.clientWidth-2*l)/w)).toFixed(3))}})}
ghosts();if(document.fonts&&document.fonts.ready)document.fonts.ready.then(ghosts);window.addEventListener('resize',ghosts);
/* carousels and the ring */
$('.nav2').forEach(function(n){var t=document.getElementById(n.getAttribute('data-for'));if(!t)return;var b=$('.arw',n);
 if(t.id==='ring'){var li=$('.ring-t li',t),tk=$('.dial i',t),i=+t.getAttribute('data-start')||0;
  var go=function(k){i=Math.max(0,Math.min(li.length-1,k));t.style.setProperty('--i',i);li.forEach(function(x,j){x.classList.toggle('on',j===i)});tk.forEach(function(x,j){x.classList.toggle('on',j===i)});b[0].disabled=i===0;b[1].disabled=i===li.length-1};
  b.forEach(function(x){x.addEventListener('click',function(){go(i+(+x.getAttribute('data-dir')))})});
  li.forEach(function(x,j){x.addEventListener('click',function(){go(j)})});
  var sx=null;t.addEventListener('touchstart',function(ev){sx=ev.touches[0].clientX},{passive:true});t.addEventListener('touchend',function(ev){if(sx===null)return;var dx=ev.changedTouches[0].clientX-sx;if(Math.abs(dx)>40)go(i+(dx<0?1:-1));sx=null});
  go(i);return}
 var step=function(){var c=t.querySelector('.car-t > li');return c?c.getBoundingClientRect().width+(t.classList.contains('q')?0:16):t.clientWidth};
 var upd=function(){b[0].disabled=t.scrollLeft<4;b[1].disabled=t.scrollLeft>t.scrollWidth-t.clientWidth-4};
 b.forEach(function(x){x.addEventListener('click',function(){t.scrollBy({left:(+x.getAttribute('data-dir'))*step(),behavior:still?'auto':'smooth'})})});
 t.addEventListener('scroll',upd,{passive:true});window.addEventListener('resize',upd);upd()});
/* scroll work: the pinned sequence, the growing picture */
var sl=$('.sl'),num=document.querySelector('.sl-n'),band=document.querySelector('.band'),bw=band&&band.querySelector('.band-w'),tick=false;
function frame(){tick=false;var vh=window.innerHeight,i,r;
 if(sl.length&&mq('(min-width: 992px)')){var best=0,bd=1e9;sl.forEach(function(s,j){var p=s.querySelector('.sl-p');if(!p)return;var q=p.getBoundingClientRect(),c=q.top+q.height/2-vh/2;if(Math.abs(c)<bd){bd=Math.abs(c);best=j}
   var im=p.querySelector('img');if(im&&!still)im.style.setProperty('--py',(Math.max(-1,Math.min(1,c/vh))*-36).toFixed(1)+'px')});
  sl.forEach(function(s,j){s.classList.toggle('on',j===best)});if(num)num.textContent=best+1}
 if(bw){r=band.getBoundingClientRect();var p=still?1:Math.max(0,Math.min(1,(vh*.8-r.top)/(vh*.8)));var s=.7+.3*p;bw.style.width=(s*100).toFixed(2)+'%';bw.style.height=(s*100).toFixed(2)+'%';bw.style.borderRadius=(10*(1-p)).toFixed(1)+'px'}}
function ask(){if(!tick){tick=true;requestAnimationFrame(frame)}}
window.addEventListener('scroll',ask,{passive:true});window.addEventListener('resize',ask);frame();
/* only now, with every part wired, do the scripted states (hidden slides, rising headings, menu, ring) take over */
R.classList.add('ready');
/* the first picture leans a little with the pointer (the reference moves its picture in depth) */
var hp=document.querySelector('.hero-pic img');
if(hp&&!still&&mq('(hover: hover) and (pointer: fine)')){document.querySelector('.hero').addEventListener('pointermove',function(ev){hp.style.setProperty('--px',((ev.clientX/window.innerWidth-.5)*-16).toFixed(1)+'px');hp.style.setProperty('--py',((ev.clientY/window.innerHeight-.5)*-10).toFixed(1)+'px')})}
})();
"""
