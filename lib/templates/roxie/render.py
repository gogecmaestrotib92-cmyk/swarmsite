"""roxie/render.py — one pure function: render(d) -> a complete page. A template for ONE PERSON or a small practice
led by its own photographs.

The build (a first screen that is one photograph with a single bold line at its centre and the name set across its
whole width at the foot; the name shrinking into the header as the page moves; the accent band with a ruled list that
opens; centred sentences; the half-and-half row; ruled section labels; rows of cards in two alternating sizes; the
four-column foot; measures, type scale, spacing, motion, the phone build) was measured on the reference's home page at
1440 and 390 on 2026-11-12 (see NOTES.md). Nothing of the reference's code, words, pictures, logo or typefaces is here.
The client's data fills it; a section whose data is missing is left out whole. No model call, no file reads.
"""
import html

FONTS = ('https://fonts.googleapis.com/css2?family=Arimo:wght@400;500;700&family=Cormorant:wght@500'
         '&family=Newsreader:ital,opsz,wght@0,6..72,360;1,6..72,360&display=swap')
WORDS = {  # 0-3 accessible names only (never visible); 4 the one visible function word, set before a price marked `from`
    'en': ('Menu', 'Close', 'Previous', 'Next', 'from'), 'de': ('Menü', 'Schließen', 'Zurück', 'Weiter', 'ab'),
    'fr': ('Menu', 'Fermer', 'Précédent', 'Suivant', 'dès'), 'es': ('Menú', 'Cerrar', 'Anterior', 'Siguiente', 'desde'),
    'it': ('Menu', 'Chiudi', 'Precedente', 'Successivo', 'da'), 'pt': ('Menu', 'Fechar', 'Anterior', 'Seguinte', 'desde'),
    'sr': ('Meni', 'Zatvori', 'Prethodno', 'Sledeće', 'od'),
}


# ───────────────────────── colour: the reference's relations (one ground, a paler and a deeper step of it, one accent band)
def _rgb(h):
    h = (h or '#000').strip().lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _hex(c):
    return '#%02x%02x%02x' % tuple(max(0, min(255, round(v))) for v in c)


def _mix(a, b, t):
    """t of a, the rest b"""
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


def _theme(p):
    g = p.get('ground') or '#ffffff'
    ink = p.get('ink') or '#111111'
    acc = p.get('accent') or ink
    light = _lum(g) >= _lum(ink)
    pole, anti = ('#000000', '#ffffff') if light else ('#ffffff', '#000000')
    t = 0.0
    while _con(ink, g) < 9 and t < 1:  # body text is set at 10-15px: it must read well on the ground and its two steps
        t += .04
        ink = _mix(pole, p.get('ink') or '#111111', t)
    pale, foot = _mix(ink, g, .022), _mix(ink, g, .06)  # reference: #fff / #faf9f7 / #f2efeb
    # ink on the accent band: whichever of the page's ink and its opposite reads better; the accent gives way if neither does
    on = max((ink, anti, pole), key=lambda c: _con(c, acc))
    t = 0.0
    a2 = acc
    while _con(on, a2) < 4.7 and t < 1:
        t += .03
        a2 = _mix('#ffffff' if _lum(on) < .5 else '#000000', acc, t)
    # the veil over a photograph: the page's own ground, as thick as the darkest (or lightest) pixel needs for the ink
    pink = pole
    a = .3
    while _con(_mix(g, pole, a), pink) < 4.7 and a < .95:
        a += .01
    return {'g': g, 'ink': ink, 'pale': pale, 'foot': foot, 'acc': a2, 'on': on, 'pink': pink,
            'veil': 'rgba(%d,%d,%d,%.2f)' % (*_rgb(g), a + .03), 'veil0': 'rgba(%d,%d,%d,.10)' % _rgb(g),
            'grgb': '%d,%d,%d' % _rgb(g)}


# ───────────────────────── small helpers
def e(s):
    return html.escape(str(s or ''), quote=True)


def src(p):
    return '../../' + p if p and not p.startswith(('http:', 'https:', 'data:', '/')) else (p or '')


def a(link, cls='', inner=None):
    """a link when the data has an address, plain words when it has none"""
    if not link or not link.get('t'):
        return ''
    t = inner if inner is not None else e(link['t'])
    c = f' class="{cls}"' if cls else ''
    return f'<a{c} href="{e(link["h"])}">{t}</a>' if link.get('h') else f'<span{c}>{t}</span>'


def img(p, cls='', lazy=True, cap=True, pos=''):
    """a photograph; `cap` keeps it from ever being shown wider than its own pixels"""
    st = []
    if cap and p.get('w'):
        st.append(f'max-width:{int(p["w"])}px')
    if pos:
        st.append(f'object-position:{pos}')
    out = '<img'
    if cls:
        out += ' class="%s"' % cls
    out += ' src="%s" alt="%s"' % (e(src(p['src'])), e(p.get('alt')))
    if p.get('w') and p.get('h'):
        out += ' width="%d" height="%d"' % (int(p['w']), int(p['h']))
    if lazy:
        out += ' loading="lazy"'
    out += ' decoding="async"'
    if st:
        out += ' style="%s"' % ';'.join(st)
    return out + '>' 


def el(tag, cls, inner, raw=False):
    """<tag class=cls>inner</tag>, or nothing when there is nothing to say"""
    if not inner:
        return ''
    return '<%s class="%s">%s</%s>' % (tag, cls, inner if raw else e(inner), tag)


def label(t, row=True, tag='h2'):
    """the small capital label; `row` = with the rule under it across the measure"""
    if not t:
        return ''
    return f'<div class="lrow"><{tag} class="lab">{e(t)}</{tag}></div>' if row else f'<{tag} class="lab">{e(t)}</{tag}>'


def more(link):
    """the bold capital link under a centred sentence"""
    return a(link, 'more') if link and link.get('t') else ''


# ───────────────────────── photographs: each once, by role, size and proportion
class Pics:
    def __init__(self, d):
        self.all = [p for p in ((d.get('media') or {}).get('photos') or []) if p.get('src')]
        self.by = {p['src']: p for p in self.all}
        self.used = set()
        named = set()
        for it in ((d.get('steps') or {}).get('items') or []):
            named.add(it.get('img'))
        for it in _people(d):
            named.add(it.get('img'))
        for pr in d.get('projects') or []:
            named.update(pr.get('photos') or [])
        for c in d.get('credentials') or []:
            named.add(c.get('img'))
        self.named = named

    def take(self, s, minw=0):
        p = self.by.get(s)
        if not p or s in self.used or (p.get('w') or 0) < minw:
            return None
        self.used.add(s)
        return p

    def opening(self):
        """the first screen: a wide photograph that is not small and not a person's own portrait; one no section has
        already named for itself comes first"""
        ok = [p for p in self.all if not p.get('small') and (p.get('w') or 0) >= 1400 and (p.get('w') or 0) > (p.get('h') or 1)
              and p.get('role') not in ('product', 'detail') and p['src'] not in self.used]
        ok.sort(key=lambda p: (p['src'] in self.named,))
        if ok:
            self.used.add(ok[0]['src'])
            return ok[0]
        return None

    def free(self):
        """a photograph for the row of opening words: one that no section names, wide enough for half a screen, never
        a portrait (portraits belong to their people) and never a product shot"""
        ok = [p for p in self.all if p['src'] not in self.used and p['src'] not in self.named and (p.get('w') or 0) >= 600
              and (p.get('w') or 0) >= .9 * (p.get('h') or 1) and p.get('role') not in ('portrait', 'people', 'product', 'detail')]
        ok.sort(key=lambda p: (bool(p.get('small')),))
        if ok:
            self.used.add(ok[0]['src'])
            return ok[0]
        return None


def _people(d):
    t = d.get('team') or {}
    out = list(t.get('items') or [])
    for g in t.get('groups') or []:
        out += g.get('items') or []
    return [p for p in out if p.get('name')]


# ───────────────────────── sections
def header(d, W):
    nav = [n for n in (d.get('nav') or []) if n.get('t')]
    cta = d.get('cta') if (d.get('cta') or {}).get('t') else None
    if cta and any(n.get('h') == cta.get('h') or n['t'] == cta['t'] for n in nav):
        cta = None
    items = nav + ([cta] if cta else [])
    brand = d.get('brand') or {}
    name = e(brand.get('name'))
    links = ''.join(f'<li>{a(n)}</li>' for n in items)
    opener = navh = menu = ''
    if items:
        opener = f'<a class="opener" href="#menu" aria-label="{W[0]}" aria-controls="menu" aria-expanded="false"><span></span><span></span><span></span></a>'
        navh = f'<nav class="nav" aria-label="{W[0]}"><ul>{links}</ul></nav>'
        menu = f'<div class="menu" id="menu"><a class="mclose" href="#" aria-label="{W[1]}"></a><nav aria-label="{W[0]}"><ul>{links}</ul></nav></div>'
    n = len(name.replace(' ', '')) * .74 + name.count(' ') * .26 or 1
    return f'''<header class="hd" id="hd" style="--n:{n:.2f}">
<div class="wrap hd-in">
{opener}
<a class="logo" href="{e(brand.get('home') or '#')}"><span>{name}</span></a>
{navh}
</div>
</header>
{menu}'''


def hero(d, pics):
    h = d.get('hero') or {}
    name = (d.get('brand') or {}).get('name') or ''
    p = pics.opening()
    n = len(name.replace(' ', '')) * .74 + name.count(' ') * .26 or 1
    title = el('h1', 'say', h.get('title')) or el('h1', 'say sr', name)
    back = img(p, 'bg', lazy=False, cap=False) + '<div class="hveil"></div>' if p else ''
    return f'''<section class="hero{' pic' if p else ''}" data-slot="hero">
{back}
{title}
<div class="big" id="big" aria-hidden="true" style="--n:{n:.2f}"><span>{e(name)}</span></div>
</section>'''


def _row(name, sub, body, link, W):
    """one ruled line of a list: opens when it has more to say, is a link when it only has an address, plain otherwise"""
    t = f'<span class="t">{e(name)}</span>' + (f' <span class="s">{e(sub)}</span>' if sub else '')
    if body:
        return f'<details class="row"><summary><h3>{t}</h3><i class="plus" aria-hidden="true"></i></summary><div class="open"><div class="open-in">{body}</div></div></details>'
    if link:
        return f'<div class="row"><h3><a href="{e(link)}">{t}</a></h3></div>'
    return f'<div class="row"><h3>{t}</h3></div>'


def _ps(*parts):
    return ''.join(f'<p>{e(x)}</p>' for x in parts if x)


def offer(d, W):
    """the accent band: everything priced or listed — catalogue groups, then plans — as the reference's opening list"""
    cat = d.get('catalogue') or {}
    plans = d.get('plans') or {}
    blocks = []
    groups = [g for g in (cat.get('groups') or []) if g.get('items')]
    for i, g in enumerate(groups):
        lab = g.get('t') or (cat.get('title') if i == 0 else '')
        txt = g.get('text') or (cat.get('text') if i == 0 and not g.get('t') else '')
        rows = []
        for it in g['items']:
            if not it.get('name'):
                continue
            price = it.get('price') or ''
            if price and it.get('from') and not price.lower().startswith(W[4]):
                price = f'{W[4]} {price}'
            body = _ps(it.get('note'), it.get('text'))
            body += _ps(*(' — '.join(v for v in (x.get('label'), x.get('price')) if v) for x in it.get('prices') or []))
            body += _ps(*(it.get('rows') or []))
            body += _ps(it.get('state'))
            if body and it.get('h'):
                body += f'<a class="more" href="{e(it["h"])}">{e(it["name"])}</a>'
            rows.append(_row(it['name'], price, body, it.get('h'), W))
        if not rows:
            continue
        head = (f'<a href="{e(g["h"])}">{e(lab)}</a>' if g.get('h') and lab else e(lab))
        blocks.append('<div class="lblock">%s%s<div class="list">%s</div></div>' % (el('h2', 'lab', head, raw=True), el('p', 'ltext', txt), ''.join(rows)))
    items = [p for p in (plans.get('items') or []) if p.get('name')]
    if items:
        rows = []
        for it in items:
            price = ' '.join(x for x in (it.get('price'), it.get('per')) if x)
            body = _ps(it.get('line'), *(it.get('rows') or []))
            if (it.get('cta') or {}).get('t'):
                body += a(it['cta'], 'more')
            rows.append(_row(it['name'], price, body, None, W))
        blocks.append('<div class="lblock">%s%s<div class="list">%s</div>%s</div>' % (el('h2', 'lab', plans.get('title')), el('p', 'ltext', plans.get('text')), ''.join(rows), el('p', 'lnote', plans.get('note'))))
    if not blocks:
        return ''
    note = el('div', 'lblock', el('p', 'lnote', cat.get('note')), raw=True)
    return '<section class="band" data-slot="offer"><div class="wrap">%s%s</div></section>' % (''.join(blocks), note)


def plain_list(lab, rows, slot, cls=''):
    if not rows:
        return ''
    return '<section class="lsec %s" data-slot="%s"><div class="wrap"><div class="lblock">%s<div class="list">%s</div></div></div></section>' % (cls, slot, el('h2', 'lab', lab), ''.join(rows))


def centred(kicker, text, link, slot, cls=''):
    if not text:
        return ''
    size = ' long' if len(text) > 170 else ''
    return f'''<section class="cen {cls}" data-slot="{slot}"><div class="wrap">
{el('p', 'lab', kicker)}
<h2 class="ital{size}">{e(text)}</h2>
{more(link)}
</div></section>'''


def split(lab, title, paras, links, note, p, slot):
    """the half-and-half row. The reference stands a picture in the right half beside the words; here the photograph is
    the ground of the section's right side and sinks into the page's own ground toward the words (owner's rule)."""
    if not (title or paras):
        return ''
    ls = ''.join(a(l, 'ul') for l in links if l and l.get('t'))
    pic = '<div class="spic" style="max-width:%dpx">%s</div>' % (int(p.get('w') or 4000), img(p, cap=False, pos='50% 30%' if p.get('role') in ('portrait', 'people') else '')) if p else ''
    return f'''<section class="split{' pic' if p else ''}" data-slot="{slot}">
{pic}
<div class="stext">
{label(lab, tag='p') if lab else '<div class="lrow none"></div>'}
<div class="sbody">
{el('h2', 'serif', title)}
{_ps(*paras)}
{el('p', 'slinks', ls, raw=True)}
{el('p', 'snote', note)}
</div>
</div>
</section>'''


def head(lab, title, text):
    """a ruled label, then a centred heading and a centred paragraph (the reference's products heading)"""
    if not (lab or title or text):
        return ''
    return label(lab) + el('div', 'chead', el('h2', 'serif', title) + _ps(text), raw=True)


def cards(items, W, kind):
    """a row of cards in two alternating sizes, moved sideways when they do not fit"""
    cs = []
    for i, c in enumerate(items):
        cs.append('<article class="card %s%s">%s</article>' % ('lg' if i % 2 else 'sm', '' if c.get('pic') else ' nopic', c['html']))
    return f'''<div class="car {kind}" data-car>
<button class="arr prev" type="button" aria-label="{W[2]}" hidden></button>
<div class="track" tabindex="0">{''.join(cs)}</div>
<button class="arr next" type="button" aria-label="{W[3]}" hidden></button>
</div>'''


def projects(d, pics, W):
    items = []
    for pr in d.get('projects') or []:
        if not pr.get('title'):
            continue
        p = None
        for s in pr.get('photos') or []:
            p = pics.take(s, 300)
            if p:
                break
        if not p:
            continue
        t = f'<a href="{e(pr["h"])}">{e(pr["title"])}</a>' if pr.get('h') else e(pr['title'])
        items.append({'pic': 1, 'html': '<div class="cimg">%s</div><div class="cd"><h3 class="ct">%s</h3>%s</div>' % (img(p), t, _ps(pr.get('text')))})
    if not items:
        return ''
    return f'<section class="psec" data-slot="projects"><div class="wrap">{cards(items, W, "prod")}</div></section>'


def team(d, pics, W, people):
    t = d.get('team') or {}
    items = []
    for m in people:
        p = pics.take(m.get('img')) if m.get('img') else None
        reach = ''.join(f'<a class="ul" href="{e(h)}">{e(x)}</a>' for x, h in (
            ((m.get('phone') or {}).get('t') if isinstance(m.get('phone'), dict) else m.get('phone'),
             (m.get('phone') or {}).get('h') if isinstance(m.get('phone'), dict) else 'tel:' + str(m.get('phone') or '').replace(' ', '')),
            (m.get('email'), 'mailto:' + str(m.get('email')))) if x)
        nm = f'<a href="{e(m["h"])}">{e(m["name"])}</a>' if m.get('h') else e(m['name'])
        pic = '<div class="cimg">%s</div>' % img(p, pos='50% 28%') if p else ''
        items.append({'pic': p, 'html': '<h3 class="pt">%s</h3>%s<div class="cd">%s%s%s</div>' % (nm, pic, el('p', 'role', m.get('role')), _ps(m.get('text')), el('p', 'slinks', reach, raw=True))})
    if not items:
        return ''
    return '<section class="tsec" data-slot="team"><div class="wrap">%s%s</div></section>' % (head(t.get('title'), '', t.get('text')), cards(items, W, 'people'))


def quotes(d):
    qs = [q for q in (d.get('quotes') or []) if q.get('q')]
    if not qs:
        return ''
    out = []
    for q in qs:
        n = len(q['q'])
        cls = 'caps' if n <= 170 else ('serif' if n <= 300 else 'read')
        who = ', '.join(x for x in (q.get('name'), q.get('role')) if x)
        out.append('<figure class="q">%s<blockquote class="%s">%s</blockquote></figure>' % (el('figcaption', 'lab', who), cls, e(q['q'])))
    return '<section class="mis pale" data-slot="quotes"><div class="wrap">%s</div></section>' % ''.join(out)


def closing(d):
    c = d.get('close') or {}
    if not c.get('title'):
        return ''
    return f'''<section class="mis" data-slot="close"><div class="wrap">
<h2 class="caps">{e(c["title"])}</h2>
{el('p', 'ctext', c.get('text'))}
{more(c.get('cta'))}
</div></section>'''


def marks(d):
    """the row where the reference shows a line of marks: the client's own logo files, or its short claims in type"""
    logos = [l for l in (d.get('logos') or []) if isinstance(l, dict) and l.get('src')]
    trust = [t for t in (d.get('trust') or []) if t]
    if logos:
        inner = ''.join('<li><img src="%s" alt="%s" loading="lazy"></li>' % (e(src(l['src'])), e(l.get('alt') or l.get('name'))) for l in logos)
    elif trust:
        inner = ''.join(f'<li>{e(t)}</li>' for t in trust)
    else:
        return ''
    return f'<section class="marks pale" data-slot="trust"><div class="wrap"><ul>{inner}</ul></div></section>'


def footer(d):
    f = d.get('foot') or {}
    pl = d.get('place') or {}
    ct = d.get('contact') or {}
    seen = set()

    def once(h):
        k = (h or '').rstrip('/').lower()
        if not k or k in seen:
            return False
        seen.add(k)
        return True

    reach = []
    ph = ct.get('phone') or pl.get('phone') or {}
    if ph.get('t'):
        reach.append('<a href="%s">%s</a>%s' % (e(ph.get('h') or 'tel:' + ph['t'].replace(' ', '')), e(ph['t']), '<span>%s</span>' % e(ph['note']) if ph.get('note') else ''))
        once(ph.get('h'))
    em = ct.get('email') or pl.get('email')
    if em:
        reach.append(f'<a href="mailto:{e(em)}">{e(em)}</a>')
        once('mailto:' + em)
    for r in ct.get('routes') or []:
        if r.get('t') and r.get('note') and r.get('h', '').startswith('mailto:'):
            reach.append(f'<span>{e(r["note"])}</span>')
    if (ct.get('form') or {}).get('h') and once(ct['form']['h']):
        reach.append(a(ct['form']))
    if (pl.get('booking') or {}).get('h') and once(pl['booking']['h']):
        reach.append(a(pl['booking']))
    ad = pl.get('address') or {}
    adr = [x for x in (ad.get('street'), ' '.join(x for x in (ad.get('postcode'), ad.get('city')) if x), ad.get('region'), ad.get('country')) if x]
    where = ''.join(f'<span>{e(x)}</span>' for x in adr)
    hours = ''.join('<span>%s %s</span>' % (e(h.get('days')), e('–'.join(x for x in (h.get('open'), h.get('close')) if x))) for h in pl.get('hours') or [])
    for loc in d.get('locations') or []:
        la = loc.get('address') or {}
        where += '<span class="gap"></span>' + ''.join(f'<span>{e(x)}</span>' for x in (loc.get('name'), la.get('street'), ' '.join(x for x in (la.get('postcode'), la.get('city')) if x), loc.get('phone') if isinstance(loc.get('phone'), str) else (loc.get('phone') or {}).get('t'), loc.get('note')) if x)
    social = [r for r in (ct.get('routes') or []) + (pl.get('social') or []) if r.get('t') and r.get('h') and not r['h'].startswith('mailto:') and once(r['h'])]
    legal = [l for l in (f.get('links') or []) if l.get('t') and l.get('h') and once(l['h'])]
    more_links = [l for l in (d.get('links') or []) if l.get('t') and l.get('h') and once(l['h'])]
    col4 = ''.join(f'<p>{x}</p>' for x in reach) + (f'<p class="adr">{where}</p>' if where else '') + (f'<p class="adr">{hours}</p>' if hours else '')
    lab4 = (d.get('cta') or {}).get('t') if col4 else ''
    return f'''<footer class="ft" data-slot="foot"><div class="wrap fgrid">
<div class="f1">{_ps(f.get('text'))}</div>
<div class="f2">{el('ul', 'fl', ''.join('<li>%s</li>' % a(l) for l in legal), raw=True)}{el('p', 'legal', f.get('legal'))}</div>
<div class="f3">{el('ul', 'fl', ''.join('<li>%s</li>' % a(l) for l in social + more_links), raw=True)}</div>
<div class="f4">{el('p', 'flab', lab4)}{col4}</div>
</div></footer>'''


# ───────────────────────── the page
def render(d: dict) -> str:
    T = _theme(d.get('palette') or {})
    W = WORDS.get((d.get('lang') or 'en')[:2], WORDS['en'])
    pics = Pics(d)
    h = d.get('hero') or {}
    st = d.get('statement') or {}
    steps = d.get('steps') or {}
    people = _people(d)
    solo = people[0] if len(people) == 1 else None

    s_hero = hero(d, pics)
    # pictures the sections name for themselves are taken before the free one is chosen
    solo_pic = pics.take(solo.get('img')) if solo and solo.get('img') else None
    step_rows = []
    for it in steps.get('items') or []:
        if not (it.get('title') or it.get('text')):
            continue
        step_rows.append((it, pics.take(it.get('img'), 600) if it.get('img') else None))
    s_projects = projects(d, pics, W)
    s_team = team(d, pics, W, people) if len(people) > 1 else ''
    intro_pic = pics.free() if (h.get('text') or h.get('text2')) else None

    s_intro = split(h.get('kicker'), '', [h.get('text'), h.get('text2')], [h.get('primary'), h.get('secondary') if (h.get('secondary') or {}).get('h') != (h.get('primary') or {}).get('h') else None], h.get('note'), intro_pic, 'intro')
    s_solo = ''
    if solo:
        reach = [{'t': solo.get('email'), 'h': 'mailto:' + str(solo.get('email'))}] if solo.get('email') else []
        s_solo = split(solo.get('role'), solo.get('name'), [solo.get('text')], reach, '', solo_pic, 'person')
    short = steps.get('text') and len(steps['text']) <= 120
    s_steps_head = ''
    if step_rows and (steps.get('title') or steps.get('text')):
        hd = head(steps.get('title'), steps.get('text'), '') if short else head('', steps.get('title'), steps.get('text'))
        s_steps_head = '<section class="hsec" data-slot="steps-head"><div class="wrap">%s</div></section>' % hd
    s_steps = ''.join(split(it.get('k'), it.get('title'), [it.get('text')], [it.get('cta')], '', p, 'step') for it, p in step_rows)

    feats = [f for f in ((d.get('features') or {}).get('items') or []) if f.get('t')]
    cat_names = {it.get('name') for g in ((d.get('catalogue') or {}).get('groups') or []) for it in g.get('items') or []}
    s_feat = ''
    if feats and not (all(not f.get('d') for f in feats) and all(f['t'] in cat_names for f in feats)):
        s_feat = plain_list((d.get('features') or {}).get('title'), [_row(f['t'], '', _ps(f.get('d')), None, W) for f in feats], 'features')
    creds = [c for c in (d.get('credentials') or []) if c.get('t')]
    rows = []
    for c in creds:
        badge = pics.by.get(c.get('img')) or ({'src': c['img'], 'alt': ''} if c.get('img') else None)
        body = _ps(c.get('year'), c.get('text'))
        if badge:
            body += '<img class="badge" src="%s" alt="%s" loading="lazy">' % (e(src(badge['src'])), e(badge.get('alt')))
        if body and c.get('h'):
            body += f'<a class="more" href="{e(c["h"])}">{e(c["t"])}</a>'
        rows.append(_row(c['t'], '', body, c.get('h'), W))
    s_creds = plain_list('', rows, 'credentials')
    faq = d.get('faq') or {}
    s_faq = plain_list(faq.get('title'), [_row(q['q'], '', _ps(q.get('a')), None, W) for q in (faq.get('items') or []) if q.get('q')], 'faq')

    link = h.get('secondary') if not (h.get('text') or h.get('text2')) else None
    body = ''.join([
        s_hero, offer(d, W),
        centred(st.get('title'), st.get('text') or '', link, 'statement') if st.get('text') else centred('', st.get('title') or '', link, 'statement'),
        s_intro, s_solo, s_steps_head, s_steps, s_projects, s_feat, s_team, quotes(d), s_creds, s_faq, marks(d), closing(d),
    ])
    name = (d.get('brand') or {}).get('name') or ''
    desc = h.get('text') or st.get('text') or ''
    css = CSS
    for k, v in T.items():
        css = css.replace('{{' + k + '}}', v)
    return f'''<!doctype html>
<html lang="{e(d.get('lang') or 'en')}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(' — '.join(x for x in (name, h.get('title')) if x))}</title>
<meta name="description" content="{e(desc[:200])}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<style>{css}</style>
</head>
<body>
{header(d, W)}
<main>
{body}
</main>
{footer(d)}
<script>{JS}</script>
</body>
</html>'''


# 1rem = 14.6834px at 1440 (the reference sets everything from the width of the window: 1.01968vw; on the phone 2.581vw
# = 10.066px at 390). Grid: 12 columns, 1rem gutters, 2rem margins (phone 1.4rem).
CSS = r'''
*,*::before,*::after{box-sizing:border-box}
html{font-size:max(11.5px,1.01968vw);-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{margin:0;background:{{g}};color:{{ink}};font-family:Arimo,"Helvetica Neue",Helvetica,Arial,sans-serif;font-size:1rem;line-height:1.2;-webkit-font-smoothing:antialiased;animation:in .5s cubic-bezier(.25,.1,.25,1) both}
@keyframes in{from{opacity:0}to{opacity:1}}
h1,h2,h3,p,ul,figure,blockquote{margin:0;padding:0;font-weight:400}
ul{list-style:none}
img{display:block;max-width:100%;height:auto}
a{color:inherit;text-decoration:none}
:focus-visible{outline:2px solid currentColor;outline-offset:3px}
.wrap{padding:0 2rem;position:relative}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%)}
.pale{background:{{pale}}}
.lab{font-size:.8086rem;line-height:1;letter-spacing:.05em;text-transform:uppercase;font-weight:400}
.lrow{padding:2rem 0 .92rem;border-bottom:1px solid {{ink}}}
.lrow.none{border:0;padding:0}
.serif{font-family:Newsreader,"Times New Roman",serif;font-weight:360;font-size:2.7435rem;line-height:1.02;letter-spacing:.02em}
.ital{font-family:Newsreader,"Times New Roman",serif;font-weight:360;font-style:italic;font-size:3.448rem;line-height:1.07;letter-spacing:.015em}
.ital.long{font-size:2.7435rem;line-height:1.1}
.caps{font-family:Cormorant,"Cormorant Garamond",Georgia,serif;font-weight:500;font-size:3.087rem;line-height:.92;letter-spacing:.009em;text-transform:uppercase}
.more{display:inline-block;font-weight:700;text-transform:uppercase;letter-spacing:.02em;border-bottom:1px solid currentColor;padding-bottom:.15rem;transition:border-color .15s cubic-bezier(.25,.1,.25,1)}
.ul{display:inline-block;border-bottom:1px solid currentColor;padding-bottom:.08rem;transition:border-color .15s cubic-bezier(.25,.1,.25,1)}
.more:hover,.ul:hover{border-bottom-color:transparent}

/* header: nothing but the photograph at the very top; the bar and its menu arrive with the first movement */
.hd{position:fixed;inset:0 0 auto 0;z-index:500;background:{{g}};padding:2.15rem 0 .75rem;transition:background-color .15s cubic-bezier(.25,.1,.25,1)}
.hd-in{display:flex;align-items:baseline;justify-content:space-between;gap:2.5rem}
.logo{font-family:Cormorant,"Cormorant Garamond",Georgia,serif;font-weight:500;font-size:1.36rem;line-height:.9;text-transform:uppercase;white-space:nowrap;flex:none}
.nav ul{display:flex;flex-wrap:wrap;justify-content:flex-end;gap:.5rem 2.5rem}
.nav a{font-size:.74rem;line-height:1.2;letter-spacing:.05em;text-transform:uppercase;border-bottom:1px solid transparent;transition:border-color .15s cubic-bezier(.25,.1,.25,1)}
.nav a:hover{border-bottom-color:currentColor}
.opener{display:none}
.menu{display:none}
.js.top .hd:not(:focus-within){background:transparent}
.js.top .hd:not(:focus-within) .nav,.js.top .hd:not(:focus-within) .opener{opacity:0}
.nav,.opener{transition:opacity .15s cubic-bezier(.25,.1,.25,1)}
.js.scrub .logo{visibility:hidden}

/* first screen */
.hero{position:relative;height:100vh;height:100svh;min-height:34rem;overflow:hidden;background:{{pale}}}
.hero .bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:50% 0}
.hveil{position:absolute;inset:0;background:linear-gradient(180deg,{{veil0}} 0,{{veil0}} 20%,{{veil}} 40%,{{veil}} 100%)}
.say{position:absolute;left:5rem;right:5rem;top:50%;transform:translateY(-35%);text-align:center;font-weight:700;font-size:1.5786rem;line-height:.9687;letter-spacing:.01em;text-transform:uppercase;color:{{ink}}}
.hero.pic .say,.hero.pic .big{color:{{pink}}}
.say.sr{left:auto;right:auto;top:auto;transform:none}
.big{position:absolute;left:2rem;bottom:2rem;z-index:501;font-family:Cormorant,"Cormorant Garamond",Georgia,serif;font-weight:500;text-transform:uppercase;white-space:nowrap;line-height:.74;font-size:calc((100vw - 4rem) / var(--n));transform-origin:0 0;will-change:transform}
.big span{display:inline-block;padding-top:.04em}
.big.fix{position:fixed;bottom:auto}

/* the accent band and every ruled list */
.band{background:{{acc}};color:{{on}};padding:4.75rem 0 3.75rem}
.lsec{padding:4.75rem 0 5.5rem}
.lblock{margin-left:25.3%}
.lblock+.lblock{margin-top:4.75rem}
.lblock .lab{display:block;margin-bottom:2.1rem}
.lblock .lab a{border-bottom:1px solid transparent;transition:border-color .15s}
.lblock .lab a:hover{border-bottom-color:currentColor}
.ltext{max-width:46.5rem;margin:-.6rem 0 2.1rem}
.lnote{max-width:46.5rem;margin-top:1.4rem}
.list{border-top:1px solid currentColor;margin-left:-33.87%;padding-left:0}
.row{border-bottom:1px solid currentColor;padding-left:25.3%}
.row h3,.row summary h3{font-weight:500;font-size:2.109rem;line-height:1.14;letter-spacing:.021em;padding:.62rem 0 .58rem;max-width:calc(100% - 13rem)}
.row h3 .s{white-space:nowrap}
.row h3 a{transition:opacity .15s}
.row h3 a:hover{opacity:.6}
.row summary{display:flex;justify-content:space-between;align-items:flex-start;cursor:pointer;list-style:none;position:relative}
.row summary::-webkit-details-marker{display:none}
.plus{position:absolute;right:11rem;top:1rem;width:1.1rem;height:1.1rem}
.plus::before,.plus::after{content:"";position:absolute;left:0;top:50%;width:100%;height:2px;margin-top:-1px;background:currentColor;transition:transform .25s cubic-bezier(.25,.1,.25,1)}
.plus::after{transform:rotate(90deg)}
details[open]>summary .plus::after{transform:rotate(0)}
.open{overflow:hidden}
.open-in{padding:2.3rem 0 3.5rem;max-width:46.5rem}
.open-in p+.more,.open-in img+.more{margin-top:.55rem}
.open-in .more{font-size:1rem}
.badge{width:6.5rem;max-width:100%;margin:.8rem 0}

/* centred sentence */
.cen{padding:5.5rem 0;text-align:center}
.cen .lab{margin-bottom:2.6rem;line-height:1.19}
.cen .ital{max-width:70.25rem;margin:0 auto}
.cen .more{margin-top:2.75rem}

/* half and half: words on the pale ground, the photograph the ground of the right side */
.split{position:relative;background:{{pale}};min-height:48.63rem;display:flex}
.spic{position:absolute;top:0;right:0;bottom:0;width:62.5%;display:flex;justify-content:flex-end}
.spic img{width:100%;height:100%;object-fit:cover}
.spic::after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,{{pale}} 0,rgba({{grgb}},0) 30%);pointer-events:none}
.stext{position:relative;z-index:1;width:50%;padding:0 2rem 2rem;display:flex;flex-direction:column;justify-content:space-between}
.stext .lrow{padding-top:2rem}
.sbody{max-width:27rem;padding-top:6rem}
.sbody .serif+p{margin-top:1.25rem}
.sbody p+p{margin-top:.9rem}
.slinks{display:flex;flex-wrap:wrap;gap:.5rem 1.6rem;margin-top:1.25rem!important}
.snote{margin-top:1.25rem!important}
.split+.split{border-top:1px solid {{g}}}
.split:not(.pic){min-height:0}
.split:not(.pic) .stext{width:100%}
.split:not(.pic) .sbody{padding-top:7.3rem;padding-bottom:3rem}

/* ruled label, centred heading, cards */
.hsec{padding-bottom:7.3rem}
.chead{text-align:center;max-width:46.5rem;margin:7.3rem auto 0}
.chead .serif+p{margin-top:1.15rem}
.chead p{max-width:30.7rem;margin:0 auto}
.psec{padding:7.3rem 0 5.09rem}
.tsec{padding:0 0 5.86rem}
.tsec .chead{margin-top:5rem}
.car{position:relative;margin:0 -2rem}
.track{display:flex;gap:1rem;overflow-x:auto;padding:0 2rem;scroll-snap-type:x proximity;scroll-padding:0 2rem;scrollbar-width:none;align-items:flex-start}
.track::-webkit-scrollbar{display:none}
.card{flex:none;scroll-snap-align:start}
.card.sm{width:calc((100vw - 4rem - 11rem) / 12 * 2 + 1rem)}
.card.lg{width:calc((100vw - 4rem - 11rem) / 12 * 3 + 2rem)}
.prod .cimg{overflow:hidden}
.prod .sm .cimg{aspect-ratio:218/241}
.prod .lg .cimg{aspect-ratio:335/417}
.cimg img{width:100%;height:100%;object-fit:cover;max-width:none!important}
.cd{padding-top:1.2rem}
.ct{font-size:1rem;line-height:1.2;letter-spacing:.03em;font-weight:400}
.ct a,.pt a{border-bottom:1px solid transparent;transition:border-color .15s}
.ct a:hover,.pt a:hover{border-bottom-color:currentColor}
.cd p{margin-top:.5rem}
.arr{position:absolute;top:calc(50% - 2rem);width:2rem;height:2rem;border:0;background:none;color:inherit;cursor:pointer;padding:0;z-index:2}
.arr.prev{left:0}.arr.next{right:0}
.arr::before{content:"";position:absolute;left:.72rem;top:.6rem;width:.75rem;height:.75rem;border-left:1px solid currentColor;border-bottom:1px solid currentColor;transform:rotate(45deg)}
.arr.next::before{left:.4rem;transform:rotate(-135deg)}
.people .track{padding-top:8.5rem}
.people .card.sm .cimg{margin-top:calc(((100vw - 4rem - 11rem) / 12 + 1rem) * 9 / 32)}
.people .card.sm{width:calc((100vw - 4rem - 11rem) / 12 * 3 + 2rem)}
.people .card.lg{width:calc((100vw - 4rem - 11rem) / 12 * 4 + 3rem)}
.people .cimg{aspect-ratio:16/9;overflow:hidden}
.pt{font-weight:700;font-size:1rem;line-height:1.2;letter-spacing:.02em;text-transform:uppercase;padding-bottom:3.55rem}
.people .nopic .pt{padding-bottom:1.2rem}
.people .cimg img{transition:filter .3s cubic-bezier(.25,.1,.25,1)}
.people .card:hover .cimg img{filter:grayscale(1)}
.role{letter-spacing:.03em}

/* quotation / closing words */
.mis{padding:5.5rem 0;text-align:center}
.mis .wrap>*{max-width:70.25rem;margin-left:auto;margin-right:auto}
.q+.q{margin-top:6rem}
.q .lab{display:block;margin-bottom:2.6rem;line-height:1.19}
.q .serif{line-height:1.08}
.read{font-family:Newsreader,"Times New Roman",serif;font-weight:360;font-size:1.577rem;line-height:1.26;letter-spacing:.015em;max-width:46.5rem;margin:0 auto}
.mis .ctext{max-width:30.7rem;margin-top:1.6rem}
.mis .more{margin-top:2.75rem}

/* the row of marks */
.marks{padding:4.5rem 0 4.25rem}
.marks ul{display:flex;flex-wrap:wrap;gap:1.4rem 2.5rem;align-items:center}
.marks li{letter-spacing:.03em}
.marks img{height:1.43rem;width:auto}

/* foot */
.ft{background:{{foot}};padding:19.4rem 0 2rem}
.fgrid{display:grid;grid-template-columns:repeat(12,1fr);column-gap:1rem;align-items:stretch}
.f1{grid-column:1/4}.f2{grid-column:5/8;display:flex;flex-direction:column;justify-content:space-between;gap:2rem}.f3{grid-column:8/10}.f4{grid-column:10/13}
.ft a{border-bottom:1px solid transparent;transition:border-color .15s}
.ft a:hover{border-bottom-color:currentColor}
.ft li{line-height:1.27}
.f4 p{line-height:1.27}
.f4 p>span,.f4 p>a{display:block;width:fit-content}
.f4 .flab{margin-bottom:1.1rem}
.f4 .adr{margin-top:1.1rem}
.f4 .gap{height:.8rem}

@media (max-width:1023px){
html{font-size:clamp(10.066px,2.581vw,13.5px)}
body{font-size:1.2rem;line-height:1.25;letter-spacing:.028em}
.wrap{padding:0 1.4rem}
.lab{font-size:1rem}
.lrow{padding:3.2rem 0 .6rem}
.serif{font-size:2.6rem}
.ital,.ital.long,.caps{font-size:2.3rem;line-height:1.26}
.more{font-size:1rem;letter-spacing:.02em}
.hd{padding:1.4rem 0;height:4.6rem}
.hd-in{justify-content:center;align-items:center;height:1.8rem}
.nav{display:none}
.logo{font-size:min(2.7rem,calc((100vw - 11rem) / var(--n)));line-height:.8}
.opener{display:block;position:absolute;left:1.4rem;top:.05rem;width:2rem;height:1.7rem}
.opener span{position:absolute;left:0;width:100%;height:1.5px;background:currentColor;top:0;transition:transform .25s cubic-bezier(.25,.1,.25,1),opacity .2s}
.opener span:nth-child(2){top:calc(50% - .75px)}.opener span:nth-child(3){top:auto;bottom:0}
.open-menu .opener span:nth-child(1){transform:translateY(.8rem) rotate(45deg)}
.open-menu .opener span:nth-child(2){opacity:0}
.open-menu .opener span:nth-child(3){transform:translateY(-.8rem) rotate(-45deg)}
.menu{display:flex;position:fixed;inset:0;z-index:499;background:{{g}};padding:3.2rem 1.4rem;align-items:flex-end;transform:translateY(-100%);visibility:hidden;transition:transform .6s cubic-bezier(.23,1,.32,1) .1s,visibility 0s .7s}
.menu:target,.open-menu .menu{transform:none;visibility:visible;transition:transform .6s cubic-bezier(.23,1,.32,1) .1s,visibility 0s}
.menu nav{width:100%}
.menu ul{border-top:1px solid {{ink}}}
.menu li{border-bottom:1px solid {{ink}}}
.menu li a{display:block;font-weight:500;font-size:2rem;line-height:1.25;letter-spacing:.021em;padding:.65rem 0 .7rem}
.mclose{position:absolute;inset:0 0 auto 0;height:4.6rem}
.js .mclose{display:none}
.open-menu .hd,.open-menu.top .hd{background:{{g}}}
.open-menu.top .hd .opener{opacity:1!important}
.say{left:1.4rem;right:1.4rem;font-size:1.1rem}
.hero .bg{object-position:58% 50%}
.big{left:1.4rem;bottom:1.4rem;font-size:calc((100vw - 2.8rem) / var(--n));transform-origin:50% 0}
.band{padding:12rem 0 9.1rem}
.lsec{padding:9rem 0}
.lblock,.row{margin-left:0;padding-left:0}
.list{margin-left:0}
.lblock+.lblock{margin-top:7rem}
.lblock .lab{margin-bottom:2.4rem}
.ltext,.lnote{max-width:none}
.row h3,.row summary h3{font-size:2rem;padding:1rem 0 1.05rem;max-width:calc(100% - 2.6rem)}
.plus{right:0;top:1.55rem;width:1.2rem;height:1.2rem}
.open-in{padding:.8rem 0 2.4rem;max-width:none}
.cen{padding:9rem 0}
.cen .lab{margin-bottom:2.9rem}
.cen .more,.mis .more{margin-top:2rem}
.split{display:flex;flex-direction:column;min-height:0}
.stext{width:auto;padding:0 1.4rem 1.4rem;display:block}
.stext .lrow{padding-top:1.8rem;padding-bottom:.7rem}
.sbody{max-width:none;padding-top:21.5rem}
.split:not(.pic) .sbody{padding-top:9rem}
.sbody .serif+p{margin-top:.8rem}
.slinks{margin-top:2.8rem!important}
.spic{position:relative;order:2;width:100%;aspect-ratio:1/1;display:block;margin:0 auto}
.spic::after{display:none}
.hsec{padding-bottom:6.7rem}
.chead{margin-top:7.3rem}
.psec{padding:7.3rem 0 8.5rem}
.car{margin:0 -1.4rem}
.track{gap:4rem;padding:0 calc(50vw - 10rem);scroll-snap-type:x mandatory;scroll-padding:0}
.card{scroll-snap-align:center}
.card.sm,.card.lg{width:20rem}
.prod .sm .cimg,.prod .lg .cimg{aspect-ratio:201/228}
.cd{padding-top:1rem}
.tsec{padding-bottom:9rem}
.people .track{padding:9rem calc(50vw - 13.95rem) 0;align-items:flex-start}
.people .card.sm,.people .card.lg{width:27.9rem}
.people .card.sm .cimg{margin-top:0}
.pt{text-align:center;padding-bottom:2.2rem}
.mis{padding:9rem 0 9.5rem}
.q+.q{margin-top:7rem}
.read{font-size:1.6rem;line-height:1.3}
.marks{padding:7rem 0}
.marks ul{gap:1.2rem 3rem}
.ft{padding:9rem 0 1.9rem;font-size:1rem;letter-spacing:0;line-height:1.2}
.fgrid{grid-template-columns:repeat(9,1fr);row-gap:3.4rem}
.f4{grid-column:1/10;grid-row:1}.f1{grid-column:1/10;grid-row:2}.f2{grid-column:1/5;grid-row:3}.f3{grid-column:6/10;grid-row:3}
}
@media (prefers-reduced-motion:reduce){
html{scroll-behavior:auto}
body{animation:none}
*,*::before,*::after{transition-duration:.01ms!important}
}
'''

JS = r'''
(function(){
var H=document.documentElement,hd=document.getElementById('hd'),big=document.getElementById('big'),logo=hd&&hd.querySelector('.logo span'),hero=document.querySelector('.hero');
var still=matchMedia('(prefers-reduced-motion: reduce)').matches;
H.classList.add('js');
/* the name is set across the whole measure, whatever its length */
function fit(){if(!big)return;var s=big.firstElementChild;big.style.fontSize='';big.style.transform='';big.classList.remove('fix');var w=s.getBoundingClientRect().width,box=hero.clientWidth-2*big.offsetLeft;if(w>0){big.style.fontSize=(parseFloat(getComputedStyle(big).fontSize)*box/w)+'px';}}
/* the name shrinks into the header as the first screen leaves: position and size follow the scroll one to one */
var G=null;
function geo(){if(!big||!logo||still){G=null;return;}var lr=logo.getBoundingClientRect(),br;big.style.transform='';big.classList.remove('fix');br=big.getBoundingClientRect();var y=scrollY;
G={t0:br.top+y,tEnd:lr.top,s:lr.width/br.width};G.yEnd=Math.max(1,hero.offsetHeight-hd.offsetHeight-lr.height);}
function onScroll(){var y=scrollY;H.classList.toggle('top',y<2);if(!G)return;var p=Math.min(1,Math.max(0,y/G.yEnd));
if(p>=1){H.classList.remove('scrub');big.style.visibility='hidden';return;}
H.classList.add('scrub');big.style.visibility='';var s=1+(G.s-1)*p,vt=G.t0+(G.tEnd-G.t0)*p;
big.style.transform='translate3d(0,'+(vt+y-G.t0)+'px,0) scale('+s+')';}
function all(){fit();geo();onScroll();}
all();addEventListener('scroll',onScroll,{passive:true});addEventListener('resize',all);
if(document.fonts&&document.fonts.ready)document.fonts.ready.then(all);addEventListener('load',all);
if(document.fonts&&document.fonts.addEventListener)document.fonts.addEventListener('loadingdone',all);
if(window.ResizeObserver&&logo)new ResizeObserver(all).observe(logo);
/* phone menu */
var op=document.querySelector('.opener');
if(op){var set=function(o){H.classList.toggle('open-menu',o);op.setAttribute('aria-expanded',o?'true':'false');};
op.addEventListener('click',function(ev){ev.preventDefault();set(!H.classList.contains('open-menu'));});
addEventListener('keydown',function(ev){if(ev.key==='Escape')set(false);});
document.querySelectorAll('.menu a').forEach(function(x){x.addEventListener('click',function(){set(false);});});}
/* a list line opens and closes over .3s */
document.querySelectorAll('details.row').forEach(function(dt){var sm=dt.querySelector('summary'),box=dt.querySelector('.open');if(still||!box.animate)return;
sm.addEventListener('click',function(ev){ev.preventDefault();var o=dt.open;if(!o)dt.open=true;var h=box.scrollHeight;
var an=box.animate([{height:(o?h:0)+'px'},{height:(o?0:h)+'px'}],{duration:300,easing:'cubic-bezier(.25,.1,.25,1)'});an.onfinish=function(){if(o)dt.open=false;};});});
/* rows of cards: arrows only when the row is longer than the page */
document.querySelectorAll('[data-car]').forEach(function(c){var t=c.querySelector('.track'),pv=c.querySelector('.prev'),nx=c.querySelector('.next');
function upd(){var over=t.scrollWidth>t.clientWidth+4&&innerWidth>1023;pv.hidden=!over||t.scrollLeft<4;nx.hidden=!over||t.scrollLeft>t.scrollWidth-t.clientWidth-4;if(!over)t.removeAttribute('tabindex');}
function go(k){t.scrollBy({left:k*t.clientWidth*.6,behavior:still?'auto':'smooth'});}
pv.addEventListener('click',function(){go(-1);});nx.addEventListener('click',function(){go(1);});t.addEventListener('scroll',upd,{passive:true});addEventListener('resize',upd);upd();addEventListener('load',upd);});
})();
'''
