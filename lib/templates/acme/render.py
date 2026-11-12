"""acme — a catalogue-first template for small shops, rebuilt from acmecups.nz (measured 2026-11-12 at 1440 and 390).

render(d) -> one self-contained page. Pure: no file reads, no clock, no model. See NOTES.md for the measures.
The build: a fixed 72 px bar of small bold condensed capitals with a running announcement; the shop's name fixed at the
left, 148 px over the first picture and 48 px for the rest of the page; a first screen that is one photograph with a
26 px sentence and one dark button at the right; a 30 px sentence beside a 14 px note; a row of ruled product cards
that moves one card per press; one group shown as words | products | a photograph that runs to the page edge; a
full-bleed photograph with a small accent panel; the whole catalogue as a sticky column of group names beside dense
ruled cards; a ruled strip of square cells with one text under it; a second full-bleed picture with a 30 px sentence;
ruled rows (label | title | words | picture to the edge); a ruled foot in halves.
"""
from html import escape as _e
import math

_FONTS = ('https://fonts.googleapis.com/css2?family=Arimo:wght@400;500;700'
          '&family=Roboto+Condensed:wght@700&display=swap')
_W = {  # words the build itself needs (controls); never client copy
    'en': ('Menu', 'Close', 'View all', 'Skip to content', 'Previous', 'Next'),
    'de': ('Menü', 'Schließen', 'Alle ansehen', 'Zum Inhalt', 'Zurück', 'Weiter'),
    'fr': ('Menu', 'Fermer', 'Tout voir', 'Aller au contenu', 'Précédent', 'Suivant'),
    'es': ('Menú', 'Cerrar', 'Ver todo', 'Ir al contenido', 'Anterior', 'Siguiente'),
    'it': ('Menu', 'Chiudi', 'Vedi tutto', 'Vai al contenuto', 'Precedente', 'Successivo'),
    'pt': ('Menu', 'Fechar', 'Ver tudo', 'Ir para o conteúdo', 'Anterior', 'Seguinte'),
    'nl': ('Menu', 'Sluiten', 'Alles bekijken', 'Naar inhoud', 'Vorige', 'Volgende'),
    'sr': ('Meni', 'Zatvori', 'Pogledaj sve', 'Na sadržaj', 'Prethodno', 'Sledeće'),
}
_ARROW = ('<svg class="ar" width="18" height="9" viewBox="0 0 18 9" aria-hidden="true">'
          '<path d="M0 4.5h17M13 .5l4 4-4 4" fill="none" stroke="currentColor"/></svg>')
_ROLES_HERO = ('product', 'dish', 'room', 'work', 'workshop', 'exterior', 'landscape', 'bar', 'detail', 'action', 'people', 'other')
_ROLES_TOLD = ('room', 'workshop', 'bar', 'work', 'exterior', 'landscape', 'action', 'people', 'detail', 'product', 'dish', 'other')
_ROLES_CLOSE = ('exterior', 'room', 'landscape', 'bar', 'workshop', 'people', 'action', 'work', 'detail', 'product', 'dish', 'other')
_ROLES_SIDE = ('product', 'detail', 'work', 'dish', 'workshop', 'room', 'bar', 'action', 'people', 'exterior', 'landscape', 'other')


# ---------- colour ----------
def _rgb(h, fallback=(0, 0, 0)):
    h = (h or '').strip().lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    try:
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    except (ValueError, IndexError):
        return fallback


def _hex(c):
    return '#%02x%02x%02x' % tuple(max(0, min(255, round(v))) for v in c)


def _lum(c):
    def f(v):
        v /= 255
        return v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4
    return .2126 * f(c[0]) + .7152 * f(c[1]) + .0722 * f(c[2])


def _con(a, b):
    la, lb = _lum(a), _lum(b)
    return (max(la, lb) + .05) / (min(la, lb) + .05)


def _mix(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def _toward(ground, ink, want):
    """the lightest step from the ground toward the ink that still reads at `want`:1 on the ground"""
    for i in range(20, 101, 2):
        c = _mix(ground, ink, i / 100)
        if _con(c, ground) >= want:
            return c
    return ink


def _veil(ground, ink, want):
    """opacity of a ground-coloured veil under which the ink reads at `want`:1 whatever the picture's pixel is"""
    worst = (0, 0, 0) if _lum(ground) > _lum(ink) else (255, 255, 255)
    for i in range(30, 100, 2):
        if _con(_mix(worst, ground, i / 100), ink) >= want:
            return i / 100
    return .98


# ---------- small helpers ----------
def _s(v):
    return v.strip() if isinstance(v, str) else ''


def _l(v):
    return v if isinstance(v, list) else []


def _o(v):
    return v if isinstance(v, dict) else {}


def _href(h):
    h = _s(h)
    return _e(h, quote=True) if h else '#'


def _ext(h):
    return ' rel="noopener"' if _s(h).startswith('http') else ''


def _src(p):
    p = _s(p)
    return p if p.startswith(('http:', 'https:', 'data:', '/')) else '../../' + p


def _btn(t, h, cls=''):
    if not _s(t):
        return ''
    return f'<a class="btn {cls}" href="{_href(h)}"{_ext(h)}><span>{_e(_s(t))}</span>{_ARROW}</a>'


def _lines(text):
    """a client's run of facts ("2 weeks 340 € · 3 weeks 500 €") set one under another"""
    return [x.strip() for x in _s(text).split(' · ') if x.strip()]


def render(d: dict) -> str:
    d = _o(d)
    lang = (_s(d.get('lang')) or 'en')[:2].lower()
    W = _W.get(lang, _W['en'])
    brand = _o(d.get('brand'))
    name = _s(brand.get('name'))
    pal = _o(d.get('palette'))
    ground = _rgb(pal.get('ground'), (254, 254, 254))
    ink = _rgb(pal.get('ink'), (0, 0, 0))
    if _con(ink, ground) < 7:
        ink = (0, 0, 0) if _lum(ground) > .4 else (255, 255, 255)
    accent = _rgb(pal.get('accent'), ink)
    if _con(accent, ground) < 1.25:
        accent = ink
    on_accent = ground if _con(ground, accent) >= 4.5 else (ink if _con(ink, accent) >= 4.5 else
                                                              ((0, 0, 0) if _lum(accent) > .3 else (255, 255, 255)))
    line = _mix(ground, ink, .24)
    soft = _mix(ground, ink, .11)
    mute = _toward(ground, ink, 3.1)       # the reference's grey of unpressed names, held to 3:1 (they are 36-48 px)
    tag = _toward(ground, ink, 4.7)        # the reference's grey of small labels, held to 4.5:1
    tint = _mix(ground, ink, .05)
    a_small = _veil(ground, ink, 4.7)
    a_big = _veil(ground, ink, 3.3)
    gr = '%d,%d,%d' % tuple(round(v) for v in ground)

    hero = _o(d.get('hero'))
    media = _o(d.get('media'))
    place = _o(d.get('place'))
    contact = _o(d.get('contact'))
    cat = _o(d.get('catalogue'))
    groups = [g for g in _l(cat.get('groups')) if isinstance(g, dict) and (_l(g.get('items')) or _s(g.get('t')))]

    # ---------- photographs: each once, by role, size and proportion ----------
    photos = [p for p in _l(media.get('photos')) if isinstance(p, dict) and _s(p.get('src'))]
    by_src = {p['src']: p for p in photos}
    steps = _o(d.get('steps'))
    step_items = [s for s in _l(steps.get('items')) if isinstance(s, dict)]
    team = _o(d.get('team'))
    people = [m for m in _l(team.get('items')) if isinstance(m, dict)]
    for tg in _l(team.get('groups')):
        people += [m for m in _l(_o(tg).get('items')) if isinstance(m, dict)]
    held = set()
    for s in step_items:
        held.add(_s(s.get('img')))
    for g in groups:
        held.add(_s(g.get('img')))
        for it in _l(g.get('items')):
            held.add(_s(_o(it).get('img')))
    for m in people:
        held.add(_s(m.get('img')))
    for c in _l(d.get('credentials')):
        held.add(_s(_o(c).get('img')))
    for sp in _l(place.get('spaces')):
        held.add(_s(_o(sp).get('img')))
    for pr in _l(d.get('projects')):
        for ph in _l(_o(pr).get('photos')):
            held.add(ph if isinstance(ph, str) else _s(_o(ph).get('src')))
    free = [p for p in photos if p['src'] not in held and p.get('role') != 'portrait']

    def dims(p):
        try:
            return float(p.get('w') or 0), float(p.get('h') or 0)
        except (TypeError, ValueError):
            return 0.0, 0.0

    def take(minw, minh, roles, ar):
        best, key = None, None
        for p in free:
            w, h = dims(p)
            if p.get('small') or w < minw or h < minh:
                continue
            r = p.get('role') or 'other'
            k = (roles.index(r) if r in roles else len(roles), abs(math.log((w / h) / ar)), -w * h)
            if key is None or k < key:
                best, key = p, k
        if best is not None:
            free.remove(best)
        return best

    def img(p, cls='', lazy=True, sizes=''):
        w, h = dims(p)
        wh = f' width="{int(w)}" height="{int(h)}"' if w and h else ''
        lz = ' loading="lazy"' if lazy else ''
        return (f'<img class="{cls}" src="{_e(_src(p["src"]), quote=True)}" alt="{_e(_s(p.get("alt")), quote=True)}"{wh}'
                f'{lz} decoding="async">')

    video = _o(media.get('video'))
    statement = _o(d.get('statement'))
    close = _o(d.get('close'))
    has_told = bool(_s(statement.get('title')) or _s(statement.get('text')))
    has_close = bool(_s(close.get('title')) or _s(close.get('text')))
    p_hero = take(1100, 690, _ROLES_HERO, 1.6)
    p_told = take(1100, 690, _ROLES_TOLD, 1.6) if has_told else None
    p_close = take(1100, 590, _ROLES_CLOSE, 1.9) if has_close and not _s(video.get('src')) else None

    # ---------- catalogue pieces ----------
    reserved = {_s(s.get('img')) for s in step_items if _s(s.get('img'))}   # the told rows keep their own pictures
    used_pics = set(reserved)

    def item_pic(it):
        s = _s(it.get('img'))
        if not s or s in used_pics:      # each photograph once on the page
            return None
        used_pics.add(s)
        return by_src.get(s) or {'src': s, 'alt': ''}

    def facts(it, cls):
        out = []
        if _s(it.get('note')):
            out.append(f'<p class="{cls}">{_e(_s(it["note"]))}</p>')
        rows = [(_s(_o(r).get('label')), _s(_o(r).get('price'))) for r in _l(it.get('prices'))]
        rows = [r for r in rows if r[0] or r[1]]
        if rows:
            out.append(f'<ul class="{cls} pr">' + ''.join(f'<li><span>{_e(a)}</span><b>{_e(b)}</b></li>' for a, b in rows) + '</ul>')
        ls = _lines(it.get('text')) + [_s(r) for r in _l(it.get('rows')) if _s(r)]
        if ls:
            out.append(f'<ul class="{cls}">' + ''.join(f'<li>{_e(x)}</li>' for x in ls) + '</ul>')
        return ''.join(out)

    def bar(it, inv=False):
        price, state = _s(it.get('price')), _s(it.get('state'))
        if not (price or state or _s(it.get('h'))):
            return ''
        left = f'<span>{_e(state)}</span>' if state else (_ARROW if _s(it.get('h')) else '<span></span>')
        return f'<span class="bar{" inv" if inv else ""}">{left}<b>{_e(price)}</b></span>'

    def card(it, cls, lvl, pic=True, inv=False):
        p = item_pic(it) if pic else None
        pw = dims(p)[0] if p else 0
        cap = f' style="max-width:{int(pw)}px"' if p and 0 < pw < 320 else ''
        inner = (f'<h{lvl} class="ct">{_e(_s(it.get("name")))}</h{lvl}>' + facts(it, 'cm')
                 + (f'<span class="ci"{cap}>{img(p)}</span>' if p else '') + bar(it, inv))
        h = _s(it.get('h'))
        if h:
            return f'<a class="{cls}" href="{_href(h)}"{_ext(h)}>{inner}</a>'
        return f'<div class="{cls}">{inner}</div>'

    def qty(n):
        return f'<sup class="qty">[{n}]</sup>' if n else ''

    feat_g = None
    for g in groups:
        if sum(1 for it in _l(g.get('items')) if _s(_o(it).get('img')) and _s(_o(it).get('img')) not in reserved) >= 2:
            feat_g = g
            break
    side_g = next((g for g in groups if g is not feat_g and _l(g.get('items'))), None)
    p_side = take(425, 525, _ROLES_SIDE, .81) if side_g else None

    # ---------- head, bar, name ----------
    nav = [n for n in _l(d.get('nav')) if isinstance(n, dict) and _s(n.get('t'))]
    signin, cta = _o(d.get('signin')), _o(d.get('cta'))
    kicker = _s(hero.get('kicker'))
    said = [x for x in ([kicker] if kicker and kicker.lower() != name.lower() else []) + [_s(t) for t in _l(d.get('trust'))] if x]
    seen, run = set(), []
    for x in said:   # the announcement and the client's short claims run in the bar, each once
        if not any(x.lower() in y.lower() or y.lower() in x.lower() for y in seen):
            seen.add(x)
            run.append(x)
    run_text = ' — '.join(run)
    mq = ''
    if run_text:
        dur = max(10, round(len(run_text) * .3))
        mq = (f'<div class="mq" style="--d:{dur}s"><span>{_e(run_text)}</span>'
              f'<span aria-hidden="true">{_e(run_text)}</span></div>')
    links = ''.join(f'<a href="{_href(n.get("h"))}"{_ext(n.get("h"))}>{_e(_s(n["t"]))}</a>' for n in nav[:7])
    right = ''
    if _s(signin.get('t')):
        right += f'<a class="nr" href="{_href(signin.get("h"))}"{_ext(signin.get("h"))}>{_e(_s(signin["t"]))}</a>'
    if _s(cta.get('t')):
        short = ' short' if len(_s(cta['t'])) <= 14 else ''
        right += f'<a class="nr call{short}" href="{_href(cta.get("h"))}"{_ext(cta.get("h"))}>{_e(_s(cta["t"]))}</a>'
    panel = links
    if _s(signin.get('t')):
        panel += f'<a href="{_href(signin.get("h"))}"{_ext(signin.get("h"))}>{_e(_s(signin["t"]))}</a>'
    if _s(cta.get('t')) and not any(_s(n['t']).lower() == _s(cta['t']).lower() for n in nav[:7]):
        panel += f'<a href="{_href(cta.get("h"))}"{_ext(cta.get("h"))}>{_e(_s(cta["t"]))}</a>'
    words = name.split() or ['']
    n_all = max(1, len(name))
    n_word = max(1, max(len(w) for w in words))
    logo = _s(brand.get('logo'))
    header = (f'<a class="skip" href="#main">{_e(W[3])}</a>'
              f'<header class="nav" id="nav"><div class="nav-in">'
              f'<button class="mt" type="button" aria-expanded="false" aria-controls="menu">'
              f'<span class="m-o">{_e(W[0])}</span><span class="m-c">{_e(W[1])}</span></button>'
              f'<nav class="nl" aria-label="{_e(W[0])}">{links}</nav>{mq}<div class="nrs">{right}</div></div>'
              f'<div class="menu" id="menu"><nav aria-label="{_e(W[0])}">{panel}</nav></div></header>')
    mark = (f'<a class="mark" href="{_href(brand.get("home"))}"{_ext(brand.get("home"))} '
            f'style="--n:{n_all};--nw:{n_word}">{_e(name)}</a>') if name else ''

    # ---------- 1 first screen ----------
    title = _s(hero.get('title')) or name
    tw = title.split()
    h1 = ''.join(f'<span class="w"><span style="animation-delay:{.3 + i * .12:.2f}s">{_e(w)}</span></span> ' for i, w in enumerate(tw))
    prim = _o(hero.get('primary'))
    sec = _o(hero.get('secondary'))
    mark_m = mark.replace('class="mark"', 'class="mark mark-m"')
    hero_html = (f'<section class="hero{"" if p_hero else " bare"}">'
                 + (f'<div class="hero-p">{img(p_hero, lazy=False)}</div><div class="hero-v" aria-hidden="true"></div>'
                    f'<div class="hero-vt" aria-hidden="true"><i></i></div>' if p_hero else '')
                 + f'<div class="hero-in">{mark_m}'
                   f'<div class="hero-c"><h1 aria-label="{_e(title, quote=True)}">{h1}</h1>'
                   f'{_btn(prim.get("t"), prim.get("h"), "dark")}</div></div></section>')

    # ---------- 2 the sentence and the note ----------
    intro = ''
    t1, t2, note = _s(hero.get('text')), _s(hero.get('text2')), _s(hero.get('note'))
    if t1 or t2 or note:
        rightcol = ''.join(f'<p>{_e(x)}</p>' for x in (t2, note) if x)
        if not t1:
            t1, rightcol = t2 or note, (f'<p>{_e(note)}</p>' if t2 and note else '')
        intro = (f'<section class="intro"><div class="intro-in"><p class="lead">{_e(t1)}</p>'
                 f'<div class="small">{rightcol}</div></div></section>')

    # ---------- 3 a row of cards (the first group that has its own pictures) ----------
    def rail(title_html, cards, more=''):
        return (f'<section class="feat"><div class="feat-h"><h2 class="title">{title_html}</h2>'
                f'<div class="feat-r">{more}<button class="arw prev" type="button" aria-label="{_e(W[4])}">{_ARROW}</button>'
                f'<button class="arw next" type="button" aria-label="{_e(W[5])}">{_ARROW}</button></div></div>'
                f'<div class="rail" tabindex="0">{cards}</div></section>')

    feat = ''
    if feat_g:
        its = [it for it in _l(feat_g.get('items')) if isinstance(it, dict) and _s(it.get('img')) and _s(it.get('img')) not in reserved]
        feat = rail(f'{_e(_s(feat_g.get("t")))}{qty(len(_l(feat_g.get("items"))))}',
                    ''.join(card(it, 'pc', 3) for it in its),
                    _btn(W[2], feat_g.get('h')) if _s(feat_g.get('h')) else '')

    # ---------- 5 one group: words | products | a photograph to the edge ----------
    side = ''
    if side_g:
        its = [it for it in _l(side_g.get('items')) if isinstance(it, dict) and _s(it.get('name'))]
        shown = its[:5]
        side = (f'<section class="one"><h2 class="title">{_e(_s(side_g.get("t")))}{qty(len(its))}</h2>'
                f'<div class="one-g{"" if p_side else " nop"}"><div class="one-t">'
                + (f'<p>{_e(_s(side_g.get("text")))}</p>' if _s(side_g.get('text')) else '')
                + (_btn(W[2], side_g.get('h')) if _s(side_g.get('h')) else '')
                + f'</div><div class="one-p">{"".join(card(it, "oc", 3, pic=False) for it in shown)}</div>'
                + (f'<div class="one-i">{img(p_side)}</div>' if p_side else '') + '</div></section>')

    # ---------- 6 a full-bleed photograph with the accent panel ----------
    told = ''
    if has_told:
        box = ((f'<h2>{_e(_s(statement.get("title")))}</h2>' if _s(statement.get('title')) else '')
               + (f'<p>{_e(_s(statement.get("text")))}</p>' if _s(statement.get('text')) else '')
               + _btn(sec.get('t'), sec.get('h'), 'onacc'))
        if p_told:
            told = f'<section class="told">{img(p_told)}<div class="told-b">{box}</div></section>'
        else:
            told = f'<section class="told flat"><div class="told-b">{box}</div></section>'

    # ---------- 7 the whole catalogue ----------
    cata = ''
    if groups:
        tabs, blocks, since = '', '', 0
        longest = max((len(w) for g in groups for w in _s(g.get('t')).split()), default=1)
        for i, g in enumerate(groups):
            its = [it for it in _l(g.get('items')) if isinstance(it, dict) and _s(it.get('name'))]
            gt = _s(g.get('t'))
            if gt:
                on = '' if tabs else ' class="on"'
                tabs += f'<a href="#g{i}"{on}>{_e(gt)}{qty(len(its))}</a>'
            pics = any(_s(it.get('img')) and _s(it.get('img')) not in used_pics for it in its)
            wide = (not pics) and any(len(_s(it.get('text'))) > 60 or _l(it.get('prices')) or _l(it.get('rows')) for it in its)
            est = 240 + math.ceil(len(its) / (2 if wide else 4)) * (243 if pics else 170)
            if since > 1500:      # a long list is broken by a photograph of the client's, when one is left
                band = take(1100, 400, _ROLES_TOLD, 2.2)
                if band:
                    blocks += f'<div class="band">{img(band)}</div>'
                    since = 0
            since += est
            blocks += (f'<div class="grp" id="g{i}">' + (f'<h3>{_e(gt)}</h3>' if gt else '')
                       + (f'<p class="desc">{_e(_s(g.get("text")))}</p>' if _s(g.get('text')) else '')
                       + (_btn(W[2], g.get('h')) if _s(g.get('h')) else '')
                       + (f'<div class="sg{" two" if wide else ""}">{"".join(card(it, "sc", 4) for it in its)}</div>' if its else '')
                       + '</div>')
        head = ''
        if _s(cat.get('title')) or _s(cat.get('text')):
            head = (f'<div class="sh"><h2 class="title">{_e(_s(cat.get("title")))}</h2>'
                    + (f'<p>{_e(_s(cat.get("text")))}</p>' if _s(cat.get('text')) else '') + '</div>')
        cnote = f'<p class="cnote">{_e(_s(cat.get("note")))}</p>' if _s(cat.get('note')) else ''
        tab_size = min(48, max(18, int(150 / (longest * .56))))
        cata = (f'<section class="cat-s">{head}<div class="cat"><div class="cat-side">'
                f'<nav class="tabs{"" if tab_size >= 40 else " sm"}" style="--ts:{tab_size}px">{tabs}</nav></div>'
                f'<div class="cat-main">{blocks}{cnote}</div></div></section>')

    # ---------- plans: the card row again ----------
    plans = _o(d.get('plans'))
    plan_items = [p for p in _l(plans.get('items')) if isinstance(p, dict) and (_s(p.get('name')) or _s(p.get('price')))]
    plans_html = ''
    if plan_items:
        cs = ''
        for p in plan_items:
            price = ' '.join(x for x in (_s(p.get('price')), _s(p.get('per'))) if x)
            c = _o(p.get('cta'))
            it = {'name': _s(p.get('name')), 'note': _s(p.get('line')), 'rows': _l(p.get('rows')), 'price': price,
                  'state': _s(c.get('t')), 'h': _s(c.get('h'))}
            cs += card(it, 'pc', 3, pic=False, inv=bool(p.get('marked')))
        plans_html = rail(_e(_s(plans.get('title'))), cs).replace('class="feat"', 'class="feat plans"')
        if _s(plans.get('text')) or _s(plans.get('note')):
            extra = ''.join(f'<p>{_e(_s(plans.get(k)))}</p>' for k in ('text', 'note') if _s(plans.get(k)))
            plans_html = plans_html.replace('</section>', f'<div class="feat-n">{extra}</div></section>')

    # ---------- 8 a ruled strip of cells with one text under it (features) ----------
    features = _o(d.get('features'))
    f_items = [f for f in _l(features.get('items')) if isinstance(f, dict) and _s(f.get('t'))]
    strip = ''
    if f_items or _s(features.get('title')):
        cells = ''.join(f'<button class="cell{" on" if i == 0 else ""}" type="button" data-i="{i}">'
                        f'<span class="tag">{i + 1:02d}</span><span class="cell-t">{_e(_s(f["t"]))}</span></button>'
                        for i, f in enumerate(f_items))
        pans = ''.join(f'<div class="pan{" on" if i == 0 else ""}" data-i="{i}"><h3>{_e(_s(f["t"]))}</h3>'
                       + (f'<p>{_e(_s(f.get("d")))}</p>' if _s(f.get('d')) else '') + '</div>' for i, f in enumerate(f_items))
        strip = ('<section class="strip">'
                 + (f'<div class="sh"><h2 class="title">{_e(_s(features.get("title")))}{qty(len(f_items))}</h2>'
                    + (f'<p>{_e(_s(features.get("text")))}</p>' if _s(features.get('text')) else '') + '</div>'
                    if _s(features.get('title')) or _s(features.get('text')) else '')
                 + (f'<div class="cells">{cells}</div><div class="pans">{pans}</div>' if f_items else '') + '</section>')

    # ---------- 9 the second full-bleed picture with a 30 px sentence ----------
    closing = ''
    if has_close:
        c = _o(close.get('cta'))
        words_ = ((f'<h2>{_e(_s(close.get("title")))}</h2>' if _s(close.get('title')) else '')
                  + (f'<p>{_e(_s(close.get("text")))}</p>' if _s(close.get('text')) else '') + _btn(c.get('t'), c.get('h')))
        if _s(video.get('src')):
            poster = f' poster="{_e(_src(video.get("poster")), quote=True)}"' if _s(video.get('poster')) else ''
            pic = (f'<video src="{_e(_src(video["src"]), quote=True)}"{poster} autoplay muted loop playsinline '
                   f'aria-label="{_e(_s(video.get("alt")), quote=True)}"></video>')
        else:
            pic = img(p_close) if p_close else ''
        closing = (f'<section class="close{"" if pic else " flat"}">{pic}'
                   + ('<div class="close-v" aria-hidden="true"></div>' if pic else '')
                   + f'<div class="close-in">{words_}</div></section>')

    # ---------- 10 ruled rows: label | title | words | picture to the edge ----------
    def rows(title_html, items):
        """items: (label, title, text, button_html, photo, link)"""
        if not items:
            return ''
        out = ''
        for lab, t, tx, b, p, h in items:
            big = p and not p.get('small') and dims(p)[0] >= 720
            tt = f'<a href="{_href(h)}"{_ext(h)}>{_e(t)}</a>' if h and not b else _e(t)
            body = ''.join(f'<p>{_e(x)}</p>' for x in (tx if isinstance(tx, list) else [tx]) if _s(x))
            pcls = 'row-i' + ('' if big else ' m-only')
            cap = '' if (big or not p) else f' style="max-width:{int(dims(p)[0])}px"'
            out += (f'<article class="row{" pic" if big else ""}"><div class="row-l">'
                    + (f'<span class="tag">{_e(lab)}</span>' if lab else '') + '</div>'
                    + f'<div class="row-c">{f"<h3>{tt}</h3>" if t else ""}'
                    + (f'<div class="row-x">{body}</div>' if body else '') + b + '</div>'
                    + (f'<div class="{pcls}"{cap}>{img(p)}</div>' if p else '')
                    + '</article>')
        head = f'<div class="rows-h"><h2 class="title">{title_html}</h2></div>' if title_html else ''
        return f'<section class="rows">{head}{out}</section>'

    told_rows = rows(_e(_s(steps.get('title'))),
                     [(_s(s.get('k')) if _s(s.get('title')) else '', _s(s.get('title')) or _s(s.get('k')), _s(s.get('text')),
                       _btn(_o(s.get('cta')).get('t'), _o(s.get('cta')).get('h')),
                       (by_src.get(_s(s.get('img'))) or ({'src': _s(s['img']), 'alt': '', 'small': True} if _s(s.get('img')) else None)),
                       '') for s in step_items if _s(s.get('title')) or _s(s.get('k')) or _s(s.get('text'))])
    if _s(steps.get('text')) and told_rows:
        told_rows = told_rows.replace('</h2></div>', f'</h2><p>{_e(_s(steps["text"]))}</p></div>', 1)

    # people: the dense ruled cards again
    team_html = ''
    if people:
        def person(m):
            p = by_src.get(_s(m.get('img'))) if _s(m.get('img')) else None
            ls = ''.join(f'<li>{_e(x)}</li>' for x in (_s(m.get('role')), _s(m.get('text'))) if x)
            if _s(m.get('phone')):
                ls += f'<li><a href="tel:{_e(_s(m["phone"]).replace(" ", ""), quote=True)}">{_e(_s(m["phone"]))}</a></li>'
            if _s(m.get('email')):
                ls += f'<li><a href="mailto:{_e(_s(m["email"]), quote=True)}">{_e(_s(m["email"]))}</a></li>'
            nm = _e(_s(m.get('name')))
            if _s(m.get('h')):
                nm = f'<a href="{_href(m["h"])}"{_ext(m["h"])}>{nm}</a>'
            return (f'<div class="sc">' + (f'<span class="ci face">{img(p)}</span>' if p else '')
                    + f'<h3 class="ct">{nm}</h3>' + (f'<ul class="cm">{ls}</ul>' if ls else '') + '</div>')
        team_html = ('<section class="strip team">'
                     + (f'<div class="sh"><h2 class="title">{_e(_s(team.get("title")))}{qty(len(people))}</h2>'
                        + (f'<p>{_e(_s(team.get("text")))}</p>' if _s(team.get('text')) else '') + '</div>'
                        if _s(team.get('title')) or _s(team.get('text')) else '')
                     + f'<div class="team-g"><div class="sg">{"".join(person(m) for m in people if _s(m.get("name")))}</div></div></section>')

    creds = rows('', [(_s(c.get('year')), _s(c.get('t')), _s(c.get('text')), '', None, _s(c.get('h')))
                      for c in _l(d.get('credentials')) if isinstance(c, dict) and _s(c.get('t'))])
    faq = _o(d.get('faq'))
    faq_html = rows(_e(_s(faq.get('title'))), [(f'{i + 1:02d}', _s(q.get('q')), _s(q.get('a')), '', None, '')
                                               for i, q in enumerate(x for x in _l(faq.get('items')) if isinstance(x, dict) and _s(x.get('q')))])
    q_items = []
    for q in _l(d.get('quotes')):
        if isinstance(q, str) and q.strip():
            q_items.append(('', q.strip(), '', '', None, ''))
        elif isinstance(q, dict) and (_s(q.get('text')) or _s(q.get('quote'))):
            who = ', '.join(x for x in (_s(q.get('name')), _s(q.get('role'))) if x)
            q_items.append(('', _s(q.get('text')) or _s(q.get('quote')), who, '', None, ''))
    quotes_html = rows('', q_items)

    def addr(a):
        a = _o(a)
        return [x for x in (_s(a.get('street')), ' '.join(x for x in (_s(a.get('postcode')), _s(a.get('city'))) if x),
                            ', '.join(x for x in (_s(a.get('region')), _s(a.get('country'))) if x)) if x]

    def hours(hs):
        out = []
        for h in _l(hs):
            h = _o(h)
            t = ' – '.join(x for x in (_s(h.get('open')), _s(h.get('close'))) if x)
            if _s(h.get('days')) or t:
                out.append((_s(h.get('days')), t))
        return out

    def ph(p):
        if isinstance(p, dict):
            return _s(p.get('t')), _s(p.get('h')) or 'tel:' + _s(p.get('t')).replace(' ', ''), _s(p.get('note'))
        return _s(p), ('tel:' + _s(p).replace(' ', '')) if _s(p) else '', ''

    loc_items = []
    for lc in _l(d.get('locations')):
        lc = _o(lc)
        tx = [', '.join(addr(lc.get('address')))] + [f'{a} {b}'.strip() for a, b in hours(lc.get('hours'))]
        tx += [x for x in (ph(lc.get('phone'))[0], _s(lc.get('email')), _s(lc.get('note'))) if x]
        if _s(lc.get('name')) or any(tx):
            loc_items.append(('', _s(lc.get('name')), [x for x in tx if x], '', None, _s(lc.get('h'))))
    locs = rows('', loc_items)

    # ---------- 11 the second ruled strip (figures) ----------
    figs = [f for f in _l(d.get('figures')) if isinstance(f, dict) and _s(f.get('v'))]
    figs_html = ''
    if figs:
        figs_html = ('<section class="figs"><div class="cells">'
                     + ''.join(f'<div class="fig"><b>{_e(_s(f["v"]))}</b>' + (f'<span>{_e(_s(f.get("l")))}</span>' if _s(f.get('l')) else '')
                               + '</div>' for f in figs) + '</div></section>')

    # ---------- foot ----------
    foot = _o(d.get('foot'))
    fl = ''
    a = addr(place.get('address'))
    if a:
        fl += '<p>' + '<br>'.join(_e(x) for x in a) + '</p>'
    reach = ''
    for src_ in (place, contact):
        t, h, n = ph(src_.get('phone'))
        if t and t not in reach:
            reach += f'<a href="{_e(h, quote=True)}">{_e(t)}</a>' + (f'<span>{_e(n)}</span>' if n else '')
        em = _s(src_.get('email'))
        if em and em not in reach:
            reach += f'<a href="mailto:{_e(em, quote=True)}">{_e(em)}</a>'
    for r in _l(contact.get('routes')):
        r = _o(r)
        if _s(r.get('t')):
            lab = f'{_s(r["t"])}: {_s(r["note"])}' if _s(r.get('note')) else _s(r['t'])
            reach += f'<a href="{_href(r.get("h"))}"{_ext(r.get("h"))}>{_e(lab)}</a>'
    if reach:
        fl += f'<p class="reach">{reach}</p>'
    hs = hours(place.get('hours'))
    if hs:
        fl += '<ul class="hrs">' + ''.join(f'<li><span>{_e(a_)}</span><span>{_e(b_)}</span></li>' for a_, b_ in hs) + '</ul>'
    bk = _o(place.get('booking'))
    form = _o(contact.get('form'))
    if _s(bk.get('t')):
        fl += _btn(bk.get('t'), bk.get('h'))
    elif _s(form.get('t')):
        fl += _btn(form.get('t'), form.get('h'))
    soc = ''.join(f'<a href="{_href(s.get("h"))}"{_ext(s.get("h"))}>{_e(_s(s["t"]))}</a>'
                  for s in _l(place.get('social')) if isinstance(s, dict) and _s(s.get('t')))
    if soc:
        fl += f'<p class="soc">{soc}</p>'
    legal = ''.join(f'<a href="{_href(x.get("h"))}"{_ext(x.get("h"))}>{_e(_s(x["t"]))}</a>'
                    for x in _l(foot.get('links')) if isinstance(x, dict) and _s(x.get('t')))
    small = (f'<div class="fine">' + (f'<p>{legal}</p>' if legal else '')
             + (f'<p>{_e(_s(foot.get("legal")))}</p>' if _s(foot.get('legal')) else '') + '</div>') if legal or _s(foot.get('legal')) else ''
    lk = [x for x in _l(d.get('links')) if isinstance(x, dict) and _s(x.get('t'))]
    half = math.ceil(len(lk) / 2) if len(lk) > 6 else len(lk)
    cols = [nav, lk[:half], lk[half:]]
    fcols = ''.join('<ul>' + ''.join(f'<li><a href="{_href(x.get("h"))}"{_ext(x.get("h"))}>{_e(_s(x["t"]))}</a></li>' for x in c) + '</ul>'
                    for c in cols if c)
    notices = ''
    for nt in _l(place.get('notices')):
        nt = _o(nt)
        if _s(nt.get('img')):
            notices += f'<img src="{_e(_src(nt["img"]), quote=True)}" alt="{_e(" ".join(_s(x) for x in _l(nt.get("text"))), quote=True)}" loading="lazy">'
        else:
            notices += ''.join(f'<p>{_e(_s(x))}</p>' for x in _l(nt.get('text')) if _s(x))
    footer = (f'<footer class="foot"><div class="foot-l"><div class="foot-a">{fl}{small}</div><div class="foot-e"></div></div>'
              f'<div class="foot-r"><div class="foot-c">{fcols}</div>'
              + (f'<p class="foot-d">{_e(_s(foot.get("text")))}</p>' if _s(foot.get('text')) else '')
              + (f'<div class="notices">{notices}</div>' if notices else '') + '</div></footer>')

    root = (f':root{{--g:{_hex(ground)};--k:{_hex(ink)};--acc:{_hex(accent)};--onacc:{_hex(on_accent)};--line:{_hex(line)};'
            f'--soft:{_hex(soft)};--mute:{_hex(mute)};--tag:{_hex(tag)};--tint:{_hex(tint)};'
            f'--vs:rgba({gr},{a_small});--vb:rgba({gr},{a_big});--vc:rgba({gr},{max(a_small, .9)});--v0:rgba({gr},0)}}')
    desc = _s(hero.get('text')) or title
    body = (header + (mark.replace('class="mark"', 'class="mark mark-d"') if mark else '') + '<main id="main">' + hero_html + intro + feat + side + told + cata + plans_html
            + strip + closing + told_rows + team_html + creds + faq_html + quotes_html + locs + figs_html + '</main>' + footer)
    return (f'<!doctype html><html lang="{_e(lang)}"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1"><title>{_e(name)}{" — " if name and title != name else ""}{_e(title if title != name else "")}</title>'
            f'<meta name="description" content="{_e(desc[:200], quote=True)}">'
            + (f'<link rel="icon" href="{_e(_src(logo), quote=True)}">' if logo else '')
            + f'<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
              f'<link rel="stylesheet" href="{_FONTS}"><style>{root}{_CSS}</style>'
              f'<script>document.documentElement.className="js top"</script></head><body>{body}<script>{_JS}</script></body></html>')


_CSS = r"""
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{margin:0;background:var(--g);color:var(--k);font:400 14px/20px Arimo,"Helvetica Neue",Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased;overflow-x:hidden}
img,video{display:block;max-width:100%}
a{color:inherit;text-decoration:none}
p,h1,h2,h3,h4,ul{margin:0;padding:0}
ul{list-style:none}
button{font:inherit;color:inherit;background:none;border:0;padding:0;cursor:pointer}
:focus-visible{outline:2px solid var(--k);outline-offset:2px}
.skip{position:absolute;left:-999px;top:0;z-index:2000;background:var(--k);color:var(--g);padding:10px 14px}
.skip:focus{left:8px;top:8px}
.title,.nav a,.nav button,.mq,.mark,.btn,.ct,.bar,.tabs a,.qty,.fig b,.cell-t{font-family:"Roboto Condensed","Helvetica Neue Condensed","Arial Narrow",Arial,sans-serif;font-weight:700;text-transform:uppercase}
.title{font-size:48px;line-height:1;max-width:75vw;overflow-wrap:anywhere}
.qty{font-size:13px;line-height:1;letter-spacing:.195px;vertical-align:top;margin-left:6px;position:relative;top:0}
.tag{display:inline-block;border:1px solid var(--line);border-radius:3px;padding:3px 2px 0;font:400 12px/12px Arimo,Helvetica,Arial,sans-serif;color:var(--tag);text-transform:none;letter-spacing:0;min-height:17px}
/* buttons: 31 high, 3 radius, 13 px bold condensed capitals, the arrow 18x9 */
.btn{display:inline-flex;align-items:center;gap:7px;min-height:31px;padding:9px 10px 7px;border:1px solid var(--soft);background:var(--soft);color:var(--k);border-radius:3px;font-size:13px;line-height:13px;letter-spacing:.26px;transition:.3s;max-width:100%}
.btn .ar{flex:none;position:relative;top:-1px}
.btn.dark{background:var(--k);border-color:var(--k);color:var(--g)}
.btn.onacc{background:var(--onacc);border-color:var(--onacc);color:var(--acc)}
@media(hover:hover){.btn:hover{background:var(--k);border-color:var(--k);color:var(--g)}.btn.dark:hover{background:var(--soft);border-color:var(--soft);color:var(--k)}.btn.onacc:hover{opacity:.85}}
.btn:active{transform:translateY(1px)}
/* bar */
.nav{position:fixed;inset:0 0 auto 0;z-index:900;background:var(--g);transition:background-color .3s}
.top .nav{background:transparent}
.nav-in{height:72px;padding:0 28px;display:flex;align-items:center;gap:28px;font-size:15px;line-height:15px}
.nl{display:flex;gap:17px;flex:1 1 auto;min-width:0;white-space:nowrap;overflow:hidden;mask-image:linear-gradient(to left,transparent 0,#000 24px)}
.nl a{flex:none}
.nl a,.nr{transition:opacity .3s;padding:6px 0}
@media(hover:hover){.nl a:hover,.nr:hover{opacity:.6}}
.nrs{display:flex;gap:17px;white-space:nowrap;flex:0 1 auto;min-width:0;overflow:hidden}
.nr.call{overflow:hidden;text-overflow:ellipsis}
.mq{display:flex;gap:4px;overflow:hidden;flex:0 1 231px;min-width:60px;max-width:231px;white-space:nowrap}
.mq span{flex:none;min-width:100%;padding-right:2em;animation:mq var(--d,10s) linear infinite}
@keyframes mq{to{transform:translateX(calc(-100% - 4px))}}
.mt{display:none}
.menu{display:none}
/* the name: fixed at 26/136, 148 px over the first picture, 48 px after it (0.3 s) */
.mark{font-size:48px;line-height:1;transition:font-size .3s;color:var(--k)}
.mark-d{position:fixed;left:26px;top:136px;z-index:890;font-size:min(48px,calc((12.5vw - 44px)/(var(--nw)*.6)));max-width:calc(12.5vw - 36px);background:var(--g);padding:2px 4px 0 0}
.top .mark-d{font-size:min(148px,calc(55vw/(var(--n)*.6)));max-width:none;white-space:nowrap;background:transparent}
.mark-m{display:none}
/* 1 first screen */
.hero{position:relative;height:100vh;min-height:620px;overflow:hidden}
.hero.bare{height:75vh;background:var(--g);border-bottom:1px solid var(--line)}
.hero-p{position:absolute;inset:0}
.hero-p img{width:100%;height:100%;object-fit:cover}
.hero-v{position:absolute;inset:0;background:linear-gradient(to left,var(--vb) 0,var(--vb) 41%,var(--v0) 58%)}
.hero-vt{position:absolute;inset:0;clip-path:inset(0)}
.hero-vt i{position:fixed;left:0;right:0;top:0;height:420px;background:linear-gradient(to bottom,var(--vs) 0,var(--vs) 72px,var(--vb) 120px,var(--vb) 300px,var(--v0) 100%)}
.hero-in{position:relative;height:100%}
.hero-c{position:absolute;left:61.67vw;top:43%;width:325px;max-width:34vw}
h1{font:500 26px/31.2px Arimo,Helvetica,Arial,sans-serif;margin-bottom:23px}
h1 .w{display:inline-block;overflow:hidden;vertical-align:top;padding-top:3px;margin-top:-3px}
h1 .w>span{display:inline-block;animation:up 1.2s cubic-bezier(.16,1,.3,1) both}
@keyframes up{from{transform:translateY(34px)}}
/* 2 */
.intro{padding:33px 26px 300px}
.intro-in{margin:0 calc(12.5vw - 26px);display:grid;grid-template-columns:minmax(0,624fr) minmax(0,357fr);gap:6.74vw}
.lead{font:500 30px/39px Arimo,Helvetica,Arial,sans-serif}
.small p{padding-right:20px}
.small p+p{margin-top:20px}
/* 3 card row */
.feat-h{display:flex;align-items:flex-start;justify-content:space-between;gap:24px;padding:0 26px 57px 12.36vw}
.feat-r{display:flex;gap:4px;align-items:center;flex:none;padding-top:2px}
.arw{width:34px;height:32px;border:1px solid var(--line);border-radius:2px;display:grid;place-items:center;transition:.3s}
.arw.prev .ar{transform:scaleX(-1)}
.arw[hidden]{display:none}
@media(hover:hover){.arw:hover{background:var(--k);color:var(--g);border-color:var(--k)}}
.rail{display:flex;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.rail::-webkit-scrollbar{display:none}
.pc{position:relative;flex:none;width:25vw;min-width:280px;scroll-snap-align:start;border-right:1px solid var(--line);padding:29px 28px 28px;display:flex;flex-direction:column;outline-offset:-2px}
.pc::after,.sc::after{content:"";position:absolute;inset:-1px;border:1px solid var(--k);opacity:0;transition:.3s;pointer-events:none}
.ct{font-size:20px;line-height:20px;max-width:82%;overflow-wrap:anywhere}
.cm{font-size:12px;line-height:15px;margin-top:13px}
.cm+.cm{margin-top:6px}
.cm.pr li{display:flex;justify-content:space-between;gap:10px}
.cm.pr b{font-weight:400;white-space:nowrap}
.ci{display:block;margin:6px auto 0;width:100%}
.pc .ci{margin-top:22px}
.pc .ci{aspect-ratio:1}
.ci img{width:100%;height:100%;object-fit:contain}
.bar{margin-top:auto;display:flex;justify-content:space-between;align-items:center;gap:10px;min-height:29px;border:1px solid var(--line);border-radius:2px;padding:9px 12px 5px;font-size:13px;line-height:13px;letter-spacing:.195px;transition:.3s}
.pc .cm:last-of-type,.pc .ct:last-child{margin-bottom:18px}
.pc .ci+.bar{margin-top:10px}
.bar b{font-weight:700;white-space:nowrap;margin-left:auto}
.bar.inv{background:var(--k);color:var(--g);border-color:var(--k)}
@media(hover:hover){a.pc:hover::after,a.sc:hover::after{opacity:1}a.pc:hover .bar,a.oc:hover .bar{background:var(--k);color:var(--g);border-color:var(--k)}a.pc:hover .bar.inv{background:var(--g);color:var(--k)}}
.feat.plans{padding-top:142px}
.feat-n{padding:24px 26px 0 30vw;max-width:calc(30vw + 620px)}
.feat-n p+p{margin-top:10px}
/* 5 one group */
.one{margin-top:158px;border-top:1px solid var(--line);padding-top:142px}
.feat+.one{margin-top:158px}
.one>.title{margin:0 26px 21px 12.5vw}
.one-g{display:grid;grid-template-columns:30.78% 30.78% 38.44%;border-top:1px solid var(--line);min-height:682px}
.one-g.nop{grid-template-columns:30.78% 30.78%}
.one-t{padding:36px 28px 40px 12.5vw}
.one-t p{max-width:221px;margin-bottom:33px}
.one-p{border-left:1px solid var(--k);border-right:1px solid var(--k);padding:40px 26px 60px;display:flex;flex-direction:column;gap:34px}
.oc{display:flex;flex-direction:column}
.oc .bar{margin-top:14px}
.one-i{position:relative;min-height:100%}
.one-i img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
/* 6 photograph with the accent panel */
.told{position:relative;height:900px;max-height:max(100vh,640px);overflow:hidden}
.told>img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.told-b{position:absolute;right:5.28vw;bottom:124px;width:391px;max-width:calc(100% - 32px);background:var(--acc);color:var(--onacc);padding:28px 24px 24px}
.told-b h2{font:500 21px/27.3px Arimo,Helvetica,Arial,sans-serif;margin-bottom:12px;max-width:303px}
.told-b p{max-width:303px}
.told-b .btn{margin-top:34px}
.told.flat{height:auto;max-height:none;padding:120px 26px;background:var(--tint)}
.told.flat .told-b{position:static;margin-left:auto;margin-right:calc(5.28vw - 26px)}
/* 7 the whole catalogue */
.sh{display:grid;grid-template-columns:25% 75%;padding-top:138px}
.sh .title{margin-left:12.5vw;grid-column:1/-1;max-width:75vw}
.sh p{grid-column:2;margin:22px 0 0 5vw;max-width:480px;font-size:16px;line-height:22.4px}
.cat-s .sh{padding-bottom:60px;border-bottom:1px solid var(--line)}
.cat{display:grid;grid-template-columns:25% 75%;border-bottom:1px solid var(--k)}
.cat-side{margin-left:12.5vw;border-right:1px solid var(--k);padding:135px 0}
.tabs{position:sticky;top:136px;display:flex;flex-direction:column;gap:5px;align-items:flex-start;padding-right:8px}
.tabs a{font-size:var(--ts,48px);line-height:1;color:var(--mute);transition:color .3s;overflow-wrap:anywhere}
.tabs a .qty{opacity:0;transition:.3s}
.tabs.sm a{color:var(--tag)}
.tabs a.on,.tabs.sm a.on{color:var(--k)}
.tabs a.on .qty{opacity:1}
@media(hover:hover){.tabs a:hover{color:var(--k)}}
.cat-main{padding:141px 0 120px 5vw;min-width:0}
.grp{scroll-margin-top:136px}
.grp+.grp,.band+.grp{margin-top:110px}
.grp h3,.pan h3{font:500 21px/27.3px Arimo,Helvetica,Arial,sans-serif}
.grp .desc{margin-top:21px;max-width:319px}
.grp .btn{margin-top:33px}
.sg{margin-top:38px;display:grid;grid-template-columns:repeat(4,11.875vw);border-top:1px solid var(--line);border-left:1px solid var(--line);width:max-content;max-width:100%}
.sg.two{grid-template-columns:repeat(2,23.75vw)}
.sc{position:relative;border-right:1px solid var(--k);border-bottom:1px solid var(--k);padding:14px 11px 11px;display:flex;flex-direction:column;min-width:0;outline-offset:-2px}
.sc .ct{font-size:15px;line-height:15px;letter-spacing:.225px;max-width:none}
.sc .cm{margin-top:4px}
.sc .ci{width:75%;aspect-ratio:1;margin-top:10px}
.sc .ci.face{order:-1;width:100%;margin:0 0 12px}
.sc .ci.face img{object-fit:cover}
.sc .bar{border:0;padding:0;min-height:13px;margin-top:auto;padding-top:14px}
.sc .cm a{text-decoration:underline;text-underline-offset:2px;overflow-wrap:anywhere}
.band{margin:110px 0 0;height:480px}
.band img{width:100%;height:100%;object-fit:cover}
.cnote{margin-top:40px;font-size:12px;line-height:16px;max-width:620px;padding-right:26px}
/* 8 ruled strip of cells */
.strip{padding-bottom:160px}
.cells{display:flex;margin-top:76px;border-top:1px solid var(--line);border-bottom:1px solid var(--line);overflow-x:auto;scrollbar-width:none}
.cells::-webkit-scrollbar{display:none}
.cell{position:relative;flex:1 0 177px;max-width:25vw;min-height:178px;border-left:1px solid var(--line);padding:38px 12px 12px;text-align:left;display:flex;align-items:center;outline-offset:-2px}
.cell .tag{position:absolute;top:8px;left:7px;transition:.3s}
.cell-t{font-size:15px;line-height:15px;letter-spacing:.225px;color:var(--tag);transition:.3s;overflow-wrap:anywhere}
.cell.on .cell-t{color:var(--k)}
.cell.on .tag{border-color:var(--k);color:var(--k)}
@media(hover:hover){.cell:hover .tag{border-color:var(--k);color:var(--k)}.cell:hover .cell-t{color:var(--k)}}
.pans{margin:43px 26px 0 30vw}
.pan{max-width:480px}
.pan p{margin-top:11px}
.js .pan{display:none}
.js .pan.on{display:block}
.pan+.pan{margin-top:36px}
.team-g{margin:60px 0 0 30vw}
.team .sg{margin-top:0}
/* 9 second full-bleed picture */
.close{position:relative;height:765px;overflow:hidden}
.close>img,.close>video{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.close-v{position:absolute;inset:0;background:linear-gradient(to right,var(--vc) 0,var(--vc) 46%,var(--v0) 76%)}
.close-in{position:relative;padding:142px 26px 60px 12.5vw;max-width:calc(12.5vw + 567px)}
.close h2{font:500 30px/39px Arimo,Helvetica,Arial,sans-serif}
.close p{font-size:16px;line-height:22.4px;margin-top:16px}
.close .btn{margin-top:36px}
.close.flat{height:auto;background:var(--tint)}
.close.flat .close-in{padding-bottom:142px}
/* 10 ruled rows */
.rows{margin-top:180px}
.strip+.rows,.rows+.rows{margin-top:0}
.rows-h{padding:0 12.5vw 20px;border-bottom:1px solid var(--k)}
.rows-h p{margin-top:16px;max-width:480px;font-size:16px;line-height:22.4px}
.rows:not(:has(.rows-h)){border-top:1px solid var(--k)}
.row{display:grid;grid-template-columns:25% 25% 50%;border-bottom:1px solid var(--k)}
.row.pic{min-height:547px}
.row-l{padding:28px 12px 28px 12.5vw}
.row-c{padding:26px 36px 40px 0;border-right:1px solid var(--k)}
.row-c h3{font:500 21px/27.3px Arimo,Helvetica,Arial,sans-serif;max-width:324px}
.row-c h3 a{text-decoration:underline;text-underline-offset:3px;text-decoration-thickness:1px}
.row-c .btn{margin-top:37px}
.row-x{margin-top:12px;max-width:324px}
.row-x p+p{margin-top:8px}
.row:not(.pic) .row-c{grid-column:2/4;border-right:0;display:grid;grid-template-columns:1fr 2fr;align-content:start}
.row:not(.pic) .row-c h3{grid-column:1;padding-right:36px}
.row:not(.pic) .row-x{grid-column:2;grid-row:1;margin-top:3px;padding:0 26px 0 28px;max-width:579px}
.row:not(.pic) .row-c .btn{grid-column:1;justify-self:start;margin-top:24px}
.row:not(.pic) .row-c h3:only-child{grid-column:1/-1;max-width:760px}
.row-i{position:relative}
.row-i img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.m-only{display:none}
/* 11 figures */
.figs .cells{margin-top:158px}
.fig{flex:1 0 177px;min-height:178px;border-left:1px solid var(--line);padding:40px 16px 16px;display:flex;flex-direction:column;justify-content:space-between;gap:24px}
.fig:first-child,.cell:first-child{border-left:0}
.fig b{font-size:48px;line-height:1;overflow-wrap:anywhere}
.fig span{font-size:12px;line-height:15px;max-width:230px}
/* foot */
.foot{display:grid;grid-template-columns:50% 50%;border-top:1px solid var(--line)}
.figs+.foot,main:has(.figs:last-child)+.foot{border-top:0}
.foot-l{display:grid;grid-template-columns:50% 50%}
.foot-a{padding:23px 28px 28px;border-right:1px solid var(--k);display:flex;flex-direction:column;gap:20px;min-height:480px;align-items:flex-start}
.foot-a .reach{display:flex;flex-direction:column;gap:3px}
.foot-a .reach span{font-size:12px;line-height:15px}
.foot-a a:not(.btn){text-decoration:underline;text-underline-offset:2px;text-decoration-thickness:1px;overflow-wrap:anywhere}
.hrs{width:100%;max-width:303px}
.hrs li{display:flex;justify-content:space-between;gap:12px}
.soc{display:flex;flex-wrap:wrap;gap:4px 14px}
.fine{margin-top:auto;font-size:10px;line-height:13px}
.fine p:first-child{display:flex;flex-wrap:wrap;gap:2px 16px}
.fine p+p{margin-top:4px}
.foot-r{padding:28px;border-left:1px solid var(--k);display:flex;flex-direction:column;gap:40px}
.foot-c{display:grid;grid-template-columns:204fr 249fr 210fr;gap:0 12px}
.foot-c a{display:inline-block;font-size:14px;line-height:18.2px;padding:2.5px 0}
@media(hover:hover){.foot-c a:hover{text-decoration:underline}}
.foot-d{margin-top:auto;max-width:551px}
.notices{display:flex;flex-wrap:wrap;gap:12px;font-size:10px;line-height:13px}
.notices img{max-height:60px;width:auto}
/* phone build (the reference changes at 1024) */
@media(max-width:1024px){
.title{font-size:36px;max-width:none}
.qty{margin-left:4px}
.nav-in{height:53px;padding:0 16px;gap:16px}
.nl{display:none}
.mt{display:block;flex:none;padding:6px 0}
.mt .m-c,.open .mt .m-o{display:none}
.open .mt .m-c{display:inline}
.mq{flex:1 1 auto;max-width:none;justify-content:flex-start}
.nrs .nr:not(.call.short){display:none}
.menu{display:block;position:fixed;inset:53px 0 0 0;background:var(--g);padding:115px 16px 40px;overflow:auto;visibility:hidden;opacity:0;transition:opacity .3s,visibility .3s}
.open .menu{visibility:visible;opacity:1}
.open .nav{background:var(--g)}
.menu a{display:block;font-size:36px;line-height:36px;padding:4px}
.mark-d{display:none}
.mark-m{display:block;position:absolute;left:16px;top:86px;right:16px;font-size:min(85px,calc((100vw - 32px)/(var(--nw)*.6)));overflow-wrap:anywhere}
.hero{height:100vh;height:100svh;min-height:560px}
.hero-v{background:linear-gradient(to top,var(--vs) 0,var(--vs) 36%,var(--v0) 52%),linear-gradient(to bottom,var(--vs) 0,var(--vs) 53px,var(--vb) 90px,var(--vb) 36%,var(--v0) 50%)}
.hero-vt i{height:53px;background:var(--vs)}
.hero.bare{min-height:520px}
.hero-c{left:16px;right:16px;top:auto;bottom:30px;width:auto;max-width:330px}
h1{font-size:22px;line-height:27px;margin-bottom:17px}
.intro{padding:31px 16px 158px}
.intro-in{margin:0;grid-template-columns:1fr;gap:34px}
.lead{font-size:22px;line-height:27.5px}
.small p{padding-right:29px}
.feat-h{padding:0 16px 34px;align-items:flex-end}
.feat-r .btn{display:none}
.rail{display:grid;grid-template-rows:auto auto;grid-auto-flow:column;grid-auto-columns:50vw}
.feat.plans .rail{display:flex}
.feat.plans .pc{width:78vw}
.pc{width:auto;min-width:0;padding:18px 16px 16px;border-bottom:1px solid var(--line)}
.pc:nth-child(even){border-bottom:0}
.ct{font-size:17px;line-height:17px;letter-spacing:.17px;max-width:none}
.pc .ci{width:80%}
.one{margin-top:81px;padding-top:68px}
.one>.title{margin:0 16px 32px}
.one-g,.one-g.nop{grid-template-columns:1fr;border-top:0;min-height:0}
.one-t{padding:0 16px 49px}
.one-t p{max-width:320px}
.one-p{margin:0 16px 28px;border:1px solid var(--line);border-left-color:var(--k);padding:27px 16px 20px}
.one-i{height:484px;min-height:0}
.told{height:800px;max-height:100vh;max-height:100svh}
.told-b{left:16px;right:16px;top:28px;bottom:auto;width:auto;max-width:none}
.told.flat{padding:68px 16px}
.told.flat .told-b{margin:0}
.sh{display:block;padding:67px 16px 0}
.sh .title{margin:0}
.sh p{margin:38px 0 0;max-width:300px}
.cat-s .sh{padding-bottom:40px}
.cat{display:block;padding:62px 0 40px}
.cat-s .sh+.cat{padding-top:30px}
.cat-side{margin:0;border-right:0;border-bottom:1px solid var(--k);padding:0 0 10px}
.tabs{position:static;flex-direction:row;gap:32px;overflow-x:auto;padding:2px 16px;scrollbar-width:none;white-space:nowrap}
.tabs::-webkit-scrollbar{display:none}
.tabs a{font-size:36px;flex:none}
.tabs.sm a{color:var(--mute)}
.tabs.sm a.on{color:var(--k)}
.cat-main{padding:66px 16px 0}
.grp{scroll-margin-top:70px}
.grp+.grp,.band+.grp{margin-top:72px}
.grp h3,.pan h3{font-size:19px;line-height:24.7px}
.grp .desc{max-width:none}
.sg,.sg.two{grid-template-columns:1fr 1fr;width:auto}
.sg.two{grid-template-columns:1fr}
.band{margin:72px -16px 0;height:300px}
.strip{padding-bottom:68px}
.cells{margin-top:61px}
.cell{flex:0 0 113px;min-height:114px;max-width:none;padding:30px 8px 8px}
.cell-t{font-size:13px;line-height:13px}
.cell .tag{top:6px;left:6px}
.pans{margin:40px 16px 0}
.team-g{margin:40px 16px 0}
.close{height:auto;min-height:515px}
.close-v{background:linear-gradient(to bottom,var(--vc) 0,var(--vc) 70%,var(--vs) 100%)}
.close-in{padding:53px 16px 60px 40px;max-width:none}
.close h2{font-size:22px;line-height:27.5px}
.close.flat .close-in{padding-bottom:53px}
.rows{margin-top:84px}
.rows-h{padding:0 16px 16px}
.row,.row.pic{grid-template-columns:125px 1fr;min-height:0}
.row-l{padding:27px 8px 0 16px}
.row-l .tag{overflow-wrap:anywhere}
.row-c,.row:not(.pic) .row-c{grid-column:2;display:block;padding:26px 16px 30px 0;border-right:0}
.row:not(.pic) .row-c h3{padding-right:0}
.row-c h3{font-size:19px;line-height:24.7px}
.row:not(.pic) .row-x{padding:0;margin-top:12px}
.row-i,.m-only{display:block;grid-column:1/-1;height:300px;width:100%;margin:0 auto}
.figs .cells{margin-top:84px;flex-wrap:wrap;border-bottom:0}
.fig{flex:1 0 50%;min-height:150px;padding:28px 16px 16px;border-bottom:1px solid var(--line)}
.fig:nth-child(odd){border-left:0}
.fig b{font-size:36px}
.foot{display:block}
.foot-l{display:block}
.foot-e{display:none}
.foot-a{border-right:0;min-height:0;padding:40px 16px 28px}
.fine{margin-top:20px}
.foot-r{border-left:0;border-top:1px solid var(--line);padding:32px 16px 28px}
.foot-c{grid-template-columns:1fr 1fr;gap:28px 12px}
}
@media(prefers-reduced-motion:reduce){
html{scroll-behavior:auto}
*,*::before,*::after{transition:none!important;animation:none!important}
.mq{flex-basis:auto;max-width:46vw}
.mq span{min-width:0;padding:0;overflow:hidden;text-overflow:ellipsis}
.mq span+span{display:none}
}
"""

_JS = r"""
(function(){var R=document.documentElement,q=function(s,e){return (e||document).querySelector(s)},qa=function(s,e){return [].slice.call((e||document).querySelectorAll(s))};
var hero=q('.hero'),calm=matchMedia('(prefers-reduced-motion: reduce)').matches;
/* the bar and the name change 100 px before the first screen ends (measured: 800 of 900) */
function top(){var lim=hero?hero.offsetHeight-100:0;R.classList.toggle('top',!!hero&&!hero.classList.contains('bare')&&scrollY<lim)}
top();addEventListener('scroll',top,{passive:true});addEventListener('resize',top);
/* phone menu */
var mt=q('.mt'),nav=q('#nav');if(mt){mt.addEventListener('click',function(){var o=R.classList.toggle('open');mt.setAttribute('aria-expanded',o)});
addEventListener('keydown',function(e){if(e.key==='Escape'&&R.classList.contains('open')){R.classList.remove('open');mt.setAttribute('aria-expanded','false');mt.focus()}});
qa('.menu a').forEach(function(a){a.addEventListener('click',function(){R.classList.remove('open');mt.setAttribute('aria-expanded','false')})})}
/* card rows: one card per press */
qa('.feat').forEach(function(f){var r=q('.rail',f),c=q('.pc',r);if(!r||!c)return;function go(d){r.scrollBy({left:d*c.getBoundingClientRect().width,behavior:calm?'auto':'smooth'})}
var p=q('.prev',f),n=q('.next',f);p.addEventListener('click',function(){go(-1)});n.addEventListener('click',function(){go(1)});
function st(){var none=r.scrollWidth<=r.clientWidth+2;p.hidden=n.hidden=none}st();addEventListener('resize',st)});
/* the strip of cells: a press shows that cell's words */
qa('.strip').forEach(function(s){var cs=qa('.cell',s),ps=qa('.pan',s);cs.forEach(function(c){c.setAttribute('aria-pressed',c.classList.contains('on'));c.addEventListener('click',function(){cs.forEach(function(x){var on=x===c;x.classList.toggle('on',on);x.setAttribute('aria-pressed',on)});ps.forEach(function(x){x.classList.toggle('on',x.dataset.i===c.dataset.i)})})})});
/* the column of group names marks the group in view */
var tabs=qa('.tabs a'),grps=tabs.map(function(a){return q(a.getAttribute('href'))});
if(tabs.length){var tk=false;function spy(){tk=false;var on=0;grps.forEach(function(g,i){if(g&&g.getBoundingClientRect().top<=innerHeight*.4)on=i});tabs.forEach(function(a,i){a.classList.toggle('on',i===on)})}
addEventListener('scroll',function(){if(!tk){tk=true;requestAnimationFrame(spy)}},{passive:true});spy()}
if(calm)qa('video').forEach(function(v){v.removeAttribute('autoplay');v.pause()});
})();
"""
