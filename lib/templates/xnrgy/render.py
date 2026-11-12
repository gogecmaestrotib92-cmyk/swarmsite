"""xnrgy — the build of https://xnrgyclub.com (a padel club; measured 2026-11-12 at 1440 and 390) as a template for
service businesses (club, gym, studio, salon, workshop) with their own photographs. One pure function, no file reads,
no model call. See NOTES.md.

Order of the page: fixed bar that leaves on the way down and returns on the way up · opening on a full photograph with
the title in two staggered halves and a dark block in the fourth column · facts on the dark ground · large picture
cards (steps) · quarter-column picture cards (projects, catalogue items with a picture) · dark half beside an
edge-to-edge photograph (statement) · ruled rows (catalogue, events, features) · people on the dark ground · plan cards
· moving headline, chips and quote cards · question rows · dark closing with a moving headline over a small picture ·
foot with large links."""
import html, math

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@300;400&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">')
# words for controls only (the menu button and its aria-labels); nothing here is display copy of the client
WORDS = {'en': ('Menu', 'Close'), 'de': ('Menü', 'Schließen'), 'es': ('Menú', 'Cerrar'), 'fr': ('Menu', 'Fermer'), 'it': ('Menu', 'Chiudi'),
         'nl': ('Menu', 'Sluiten'), 'pt': ('Menu', 'Fechar'), 'sr': ('Meni', 'Zatvori'), 'sl': ('Meni', 'Zapri'), 'da': ('Menu', 'Luk'), 'cs': ('Menu', 'Zavřít')}
HOME = {'home', 'start', 'startseite', 'inicio', 'accueil', 'početna', 'domov', 'hjem'}
CH = .6  # advance of one capital of the display face with its tracking, in em (measured on the reference: 666px / 6 / 187.5)


def e(s):
    return html.escape(str(s or ''), quote=True)


def _rgb(h):
    h = (h or '').strip().lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    try:
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    except Exception:
        return (128, 128, 128)


def _hex(c):
    return '#%02x%02x%02x' % tuple(max(0, min(255, round(v))) for v in c)


def _mix(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def _lum(c):
    f = lambda v: v / 3294.6 if v <= 10 else ((v / 255 + .055) / 1.055) ** 2.4
    return .2126 * f(c[0]) + .7152 * f(c[1]) + .0722 * f(c[2])


def _con(a, b):
    x, y = _lum(a), _lum(b)
    return (max(x, y) + .05) / (min(x, y) + .05)


def _rgba(c, a):
    return 'rgba(%d,%d,%d,%s)' % (round(c[0]), round(c[1]), round(c[2]), ('%.3f' % a).rstrip('0').rstrip('.'))


def _theme(pal):
    """The reference's relations — a light ground, one near-black band colour, one accent that fills buttons and sets
    the small labels — carried by the client's palette."""
    g, k, a = _rgb(pal.get('ground') or '#ebebeb'), _rgb(pal.get('ink') or '#000000'), _rgb(pal.get('accent') or '#192b88')
    if _con(g, k) < 7:
        k = (0, 0, 0) if _lum(g) > .4 else (255, 255, 255)
    light = _lum(g) >= _lum(k)
    if light:
        D = _mix(k, a, .14)
        while _lum(D) > .028:
            D = _mix(D, (0, 0, 0), .1)
        onD, card, V = g, (255, 255, 255), D
        if _con(onD, D) < 9:
            onD = _mix(onD, (255, 255, 255), .6)
    else:
        D, onD, card, V = _mix(g, k, .07), k, _mix(g, k, .1), _mix(g, (0, 0, 0), .5)
    acc = a
    for _ in range(40):  # the accent carries 10px labels on the ground and on the cards, and 12px button words
        if min(_con(acc, g), _con(acc, card), _con(acc, D) if not light else 9) >= 4.6:
            break
        acc = _mix(acc, k, .06)
    onA = max((g, k, (255, 255, 255), (0, 0, 0)), key=lambda c: _con(c, acc))
    for _ in range(40):
        if _con(onA, acc) >= 4.6:
            break
        acc = _mix(acc, (0, 0, 0) if _lum(onA) > .5 else (255, 255, 255), .06)
    al = .4  # the reference's veil over its film is 40 % black; ours is as strong as the brightest pixel needs
    while al < .86 and _con(onD, _mix(_mix((255, 255, 255), V, al), onD, .09)) < 4.6:  # .09: a grid hairline may run under a letter
        al += .01
    al3 = .3  # for the 50–112px moving headline over the small closing picture, 3:1
    while al3 < .8 and _con(onD, _mix(_mix((255, 255, 255), D, al3), onD, .09)) < 3.15:
        al3 += .01
    # dimmed words must hold on a grid hairline too (6 % dark on the ground, 9 % light on the band)
    dim = lambda fg, bg, ln=.09: next((t for t in (.45, .4, .34, .28, .2, .1, 0) if _con(_mix(fg, bg, t), _mix(bg, fg, ln)) >= 4.7), 0)
    return dict(g=g, k=k, D=D, onD=onD, card=card, acc=acc, onA=onA, V=V, al=al, al3=al3, light=light,
                kdim=_mix(k, g, dim(k, g)), cdim=_mix(k, card, dim(k, card)), ddim=_mix(onD, D, dim(onD, D)), panel=_mix(D, onD, .05))


class Pics:
    """The client's photographs: each shown once; a slot takes one by role, size and proportion."""

    def __init__(self, d):
        self.all = [p for p in ((d.get('media') or {}).get('photos') or []) if isinstance(p, dict) and p.get('src')]
        self.by = {p['src']: p for p in self.all}
        self.used = set()
        self.held = set()

    def hold(self, src):
        if src:
            self.held.add(src)

    def take(self, src):
        """A picture a block names (a step's, a person's). None when it was already shown."""
        if not src or src in self.used:
            return None
        self.used.add(src)
        return self.by.get(src) or {'src': src}

    def pick(self, roles, min_w, min_h, never=(), tall_ok=False):
        best = None
        for p in self.all:
            w, h = p.get('w') or 0, p.get('h') or 0
            if p['src'] in self.used or p['src'] in self.held or p.get('small') or w < min_w or h < min_h:
                continue
            r = p.get('role') or 'other'
            if r in never or (not tall_ok and h > w * 1.15):
                continue
            score = (roles.index(r) if r in roles else len(roles), -w)
            if best is None or score < best[0]:
                best = (score, p)
        if best:
            self.used.add(best[1]['src'])
            return best[1]
        return None


def _img(p, cls='', eager=False, sizes=None, style=''):
    wh = (' width="%d" height="%d"' % (p['w'], p['h'])) if p.get('w') and p.get('h') else ''
    return '<img%s src="../../%s" alt="%s"%s%s decoding="async"%s>' % (
        (' class="%s"' % cls) if cls else '', e(p['src']), e(p.get('alt')), wh, '' if eager else ' loading="lazy"', (' style="%s"' % style) if style else '')


def _paras(t, cls=''):
    c = (' class="%s"' % cls) if cls else ''
    return ''.join('<p%s>%s</p>' % (c, e(x.strip())) for x in str(t or '').replace('\r', '').split('\n\n') if x.strip())


def _btn(l, kind='p', extra=''):
    if not (isinstance(l, dict) and l.get('t')):
        return ''
    return '<a class="btn btn-%s%s" href="%s"><span>%s</span></a>' % (kind, extra, e(l.get('h') or '#'), e(l['t']))


def _split(title):
    """The reference sets its title in two halves, the first from the left edge, the second from the right."""
    w = str(title or '').split()
    if len(w) < 2:
        return ' '.join(w), ''
    best = min(range(1, len(w)), key=lambda i: abs(len(' '.join(w[:i])) - len(' '.join(w[i:]))) + (.5 if len(' '.join(w[:i])) < len(' '.join(w[i:])) else 0))
    return ' '.join(w[:best]), ' '.join(w[best:])


def _h1size(a, b):
    """Reference: 187.5px for six capitals on a 1300px measure. Longer titles keep the two halves and step down until
    each half sits in one line, then in two."""
    L = max(len(a), len(b), 1)
    one = 1300 / (L * CH)
    if one >= 104:
        return min(187.5, one), 1
    longest = max([len(x) for x in (a + ' ' + b).split()] + [1])
    two = 1300 / (max(math.ceil(L / 2) + 3, longest) * CH)
    if two >= 78:
        return min(150, two), 2
    three = 1300 / (max(math.ceil(L / 3) + 3, longest) * CH)
    return max(54, min(110, three)), 3


def _h1phone(a, b):
    """Reference: 95px, six capitals a line on 348px."""
    t = (a + ' ' + b).strip()
    longest = max([len(x) for x in t.split()] + [1])
    cpl = 6 if len(t) <= 14 else 9 if len(t) <= 30 else 13
    return max(30, min(95, 348 / (max(cpl, longest) * CH)))


def _marquee(text, tag, px=112.5):
    """The reference's moving headline: one line of copies with a middle dot between, 30px a second, linear."""
    t = str(text or '').strip()
    if not t:
        return ''
    w = len(t) * .64 * px + 110
    k = max(2, math.ceil(1700 / w) + 1)
    one = '<span class="mq-i">%s</span><span class="mq-d" aria-hidden="true">·</span>' % e(t)
    half = one * k
    return ('<div class="mq"><%s class="mq-t" style="animation-duration:%ds"><span class="mq-h">%s</span><span class="mq-h" aria-hidden="true">%s</span></%s></div>'
            % (tag, round(k * w / 30), half, half, tag))


def _addr(a):
    if not isinstance(a, dict):
        return ''
    l2 = ' '.join(x for x in (a.get('postcode'), a.get('city')) if x)
    return '<br>'.join(e(x) for x in (a.get('street'), l2, ', '.join(x for x in (a.get('region'), a.get('country')) if x)) if x)


def _hours(hs):
    out = []
    for h in hs or []:
        if isinstance(h, dict) and h.get('days'):
            out.append('<span class="hr"><span>%s</span><span>%s</span></span>' % (e(h['days']), e(' – '.join(x for x in (h.get('open'), h.get('close')) if x))))
        elif isinstance(h, str) and h:
            out.append('<span class="hr"><span>%s</span></span>' % e(h))
    return ''.join(out)


def _tel(p):
    if isinstance(p, dict) and p.get('t'):
        return p['t'], p.get('h') or 'tel:' + ''.join(c for c in p['t'] if c.isdigit() or c == '+'), p.get('note')
    if isinstance(p, str) and p:
        return p, 'tel:' + ''.join(c for c in p if c.isdigit() or c == '+'), None
    return None, None, None


def _row(name, price='', label='', text='', prices=(), rows=(), link=None, state='', linkword=''):
    """A ruled row of the reference's question list. With something to open it is a details row with the plus sign;
    with nothing to open it is the same row as a line (and a link when the client gives one)."""
    head = ''
    if label:
        head += '<span class="rw-l">%s</span>' % e(label)
    head += '<span class="rw-n">%s</span>' % e(name)
    tail = ''
    if state:
        tail += '<span class="rw-s">%s</span>' % e(state)
    if price:
        tail += '<span class="rw-p">%s</span>' % e(price)
    body = _paras(text)
    if prices:
        body += '<ul class="rw-pr">%s</ul>' % ''.join('<li><span>%s</span><b>%s</b></li>' % (e(p.get('label')), e(p.get('price'))) for p in prices if isinstance(p, dict))
    if rows:
        body += '<ul class="rw-li">%s</ul>' % ''.join('<li>%s</li>' % e(r) for r in rows if r)
    if body:
        if link:
            body += '<p><a class="lk" href="%s">%s</a></p>' % (e(link), e(linkword or name))
        return '<details class="rw"><summary><span class="rw-h">%s</span>%s<i class="pm" aria-hidden="true"></i></summary><div class="rw-a">%s</div></details>' % (head, tail, body)
    if link:
        return '<a class="rw rw-f" href="%s"><span class="rw-h">%s</span>%s<i class="ar" aria-hidden="true">↗</i></a>' % (e(link), head, tail)
    return '<div class="rw rw-f"><span class="rw-h">%s</span>%s</div>' % (head, tail)


def _rows_section(cls, title, text, groups, note='', eyebrow=''):
    """groups: [(title, text, [row html])]"""
    body = ''
    for gt, gx, rs in groups:
        if not rs:
            continue
        body += '<div class="rg">%s%s<div class="rws">%s</div></div>' % ('<h3 class="rg-t">%s</h3>' % e(gt) if gt else '', _paras(gx, 'rg-x'), ''.join(rs))
    if not body:
        return ''
    head = ('<p class="eb">%s</p>' % e(eyebrow) if eyebrow else '') + ('<h2 class="h2">%s</h2>' % e(title) if title else '') + _paras(text, 'ld')
    return '<section class="sec rowsec %s"><div class="w"><div class="mid">%s%s%s</div></div></section>' % (cls, '<div class="mid-h">%s</div>' % head if head else '', body, _paras(note, 'nt'))


def _spans(n):
    """Quarter columns filled without a ragged end: a short last row is widened (2+1+1, 2+2)."""
    if n <= 0:
        return []
    if n == 1:
        return [2]
    rows, left = [], n
    while left > 0:
        if left >= 4 and left != 5:
            rows.append([1, 1, 1, 1]); left -= 4
        elif left == 5:
            rows.append([2, 1, 1]); rows.append([2, 2]); left = 0
        elif left == 3:
            rows.append([2, 1, 1]); left = 0
        elif left == 2:
            rows.append([2, 2]); left = 0
        else:
            rows.append([2]); left = 0
    return [s for r in rows for s in r]


def render(d: dict) -> str:
    d = d or {}
    T = _theme(d.get('palette') or {})
    lang = (d.get('lang') or 'en')[:2].lower()
    W_MENU, W_CLOSE = WORDS.get(lang, WORDS['en'])
    brand = d.get('brand') or {}
    name = brand.get('name') or ''
    home = brand.get('home') or '#'
    hero = d.get('hero') or {}
    place = d.get('place') or {}
    contact = d.get('contact') or {}
    media = d.get('media') or {}
    P = Pics(d)

    # pictures that blocks name are kept for those blocks
    steps = d.get('steps') or {}
    st_items = [s for s in (steps.get('items') or []) if isinstance(s, dict) and (s.get('title') or s.get('text'))]
    spaces = [s for s in (place.get('spaces') or []) if isinstance(s, dict) and (s.get('title') or s.get('text'))]
    st_titles = {(s.get('title') or '').strip().lower() for s in st_items}
    if not st_items and spaces:
        st_items, spaces = spaces, []
    spaces = [s for s in spaces if (s.get('title') or '').strip().lower() not in st_titles]
    team = d.get('team') or {}
    people = [p for p in (team.get('items') or []) if isinstance(p, dict) and p.get('name')]
    for g in team.get('groups') or []:
        people += [p for p in (g.get('items') or []) if isinstance(p, dict) and p.get('name')]
    cat = d.get('catalogue') or {}
    cgroups = [g for g in (cat.get('groups') or []) if isinstance(g, dict)]
    projects = [p for p in (d.get('projects') or []) if isinstance(p, dict) and p.get('title')]
    creds = [c for c in (d.get('credentials') or []) if isinstance(c, dict) and c.get('t')]
    for s in st_items + spaces + people:
        P.hold(s.get('img'))
    for g in cgroups:
        P.hold(g.get('img'))
        for it in g.get('items') or []:
            P.hold(it.get('img') if isinstance(it, dict) else None)
    for pr in projects:
        for s in pr.get('photos') or []:
            P.hold(s if isinstance(s, str) else (s or {}).get('src'))
    for c in creds:
        P.hold(c.get('img'))

    # ---- bar ----
    nav = [n for n in (d.get('nav') or []) if isinstance(n, dict) and n.get('t') and n['t'].strip().lower() not in HOME][:7]
    cta = d.get('cta') if isinstance(d.get('cta'), dict) and (d.get('cta') or {}).get('t') else (hero.get('primary') if isinstance(hero.get('primary'), dict) else None)
    second = hero.get('secondary') if isinstance(hero.get('secondary'), dict) and hero['secondary'].get('t') else (d.get('signin') if isinstance(d.get('signin'), dict) else None)
    if second and cta and second.get('t') == cta.get('t'):
        second = None
    logo = ('<img class="logo-i" src="../../%s" alt="%s">' % (e(brand['logo']), e(name))) if brand.get('logo') else e(name)
    ph_t, ph_h, ph_n = _tel(place.get('phone') or contact.get('phone'))
    email = place.get('email') or contact.get('email')
    bar = ('<header class="hd" id="hd"><a class="logo" href="%s">%s</a><nav class="hd-n" aria-label="%s">%s</nav><div class="hd-b">%s%s</div>'
           '<button class="mb" type="button" aria-expanded="false" aria-controls="oc"><i aria-hidden="true"></i><span>%s</span></button></header>'
           % (e(home), logo, e(W_MENU), ''.join('<a href="%s">%s</a>' % (e(n.get('h') or '#'), e(n['t'])) for n in nav),
              _btn(second, 'o') if len(nav) <= 5 else '', _btn(cta, 'p'), e(W_MENU)))
    oc = ('<div class="oc dk" id="oc" hidden><div class="oc-h"><a class="logo" href="%s">%s</a><button class="oc-x" type="button" aria-label="%s"><i aria-hidden="true"></i></button></div>'
          '<div class="oc-b">%s<nav aria-label="%s">%s</nav>%s%s</div></div>'
          % (e(home), logo, e(W_CLOSE), _btn(cta, 'w', ' oc-c'), e(W_MENU), ''.join('<a href="%s">%s</a>' % (e(n.get('h') or '#'), e(n['t'])) for n in nav),
             '<a class="oc-t" href="%s">%s</a>' % (e(ph_h), e(ph_t)) if ph_t else '', _btn(second, 'o')))
    # The reference keeps a small button fixed at the lower left once the page has moved. It lies over whatever text
    # passes under it (measured on ours: a quote's name and a plan's note were covered), so it is not carried over;
    # the bar that returns on the way up holds the same button.
    floatb = ''

    # ---- opening ----
    a, b = _split(hero.get('title') or name)
    size, lines = _h1size(a, b)
    sizem = _h1phone(a, b)
    video = media.get('video') if isinstance(media.get('video'), dict) and (media.get('video') or {}).get('src') else None
    hp = None
    if not video:
        hp = P.pick(['exterior', 'landscape', 'work', 'room', 'workshop', 'action', 'bar', 'other', 'detail'], 1600, 800, never=('portrait', 'people', 'product', 'dish')) \
            or P.pick(['exterior', 'landscape', 'work', 'room', 'workshop', 'action', 'bar', 'other', 'detail'], 1200, 700, never=('portrait', 'people', 'product', 'dish'))
    if video:
        bg = '<video class="hero-m" data-slot="opening" autoplay muted loop playsinline%s aria-label="%s"><source src="../../%s"></video>' % (
            (' poster="../../%s"' % e(video['poster'])) if video.get('poster') else '', e(video.get('alt')), e(video['src']))
    elif hp:
        bg = _img(hp, 'hero-m', eager=True).replace('<img ', '<img data-slot="opening" fetchpriority="high" ')
    else:
        bg = ''
    ptxt = [x for x in (hero.get('text'), hero.get('text2')) if x]
    plen = sum(len(x) for x in ptxt)
    wide = plen > 180
    p_left = (.5 if wide else .7635) * 1300
    a_w = min(1300, len(a) * CH * size) if lines == 1 else 1300
    tuck = a_w < p_left - 40  # the reference's paragraph ends 35px below the top of the title's first half, beside it
    note = hero.get('note') if hero.get('note') and hero.get('note') != ph_t else ''
    hero_c = _btn(hero.get('primary') if isinstance(hero.get('primary'), dict) else cta, 'p') + _btn(second, 'o')
    if note:
        hero_c += '<span class="hero-n">%s</span>' % e(note)
    elif ph_t and hero.get('note'):
        hero_c += '<a class="hero-n" href="%s">%s</a>' % (e(ph_h), e(ph_t))
    opening = ('<section class="hero dk%s" style="--h1:%.2f;--h1m:%.1fpx"><div class="hero-bg">%s%s</div><div class="w hero-in"><div class="hero-t">'
               '<span class="box" aria-hidden="true"></span><h1 class="h1"><span class="h1a">%s</span>%s</h1>%s</div>%s</div></section>'
               % ('' if bg else ' hero-plain', size, sizem, bg, '<i class="veil"></i>' if bg else '', e(a), ' <span class="h1b">%s</span>' % e(b) if b else '',
                  '<div class="hero-c">%s</div>' % hero_c if hero_c else '',
                  '<div class="hero-p%s%s">%s</div>' % (' hero-pw' if wide else '', ' tuck' if tuck else '', ''.join('<p>%s</p>' % e(x) for x in ptxt)) if ptxt else ''))

    # ---- facts (the reference's dark row of label + value under a location's opening) ----
    figures = [f for f in (d.get('figures') or []) if isinstance(f, dict) and f.get('v')]
    trust = [t for t in (d.get('trust') or []) if isinstance(t, str) and t.strip()]
    facts = ''
    if figures:
        facts = ''.join('<div class="fc"><p class="fc-l">%s</p><p class="fc-v">%s</p></div>' % (e(f.get('l')), e(f['v'])) for f in figures)
    elif trust:
        facts = ''.join('<div class="fc"><p class="fc-v fc-t">%s</p></div>' % e(t) for t in trust)
        trust = []
    facts = '<section class="sec facts dk"><div class="w"><div class="g4">%s</div></div></section>' % facts if facts else ''

    # ---- large picture cards (the reference's two clubs) ----
    cards = ''
    if st_items or steps.get('title'):
        n = len(st_items)
        cols = 2 if n in (1, 2, 4) else 3
        longt = any(len(s.get('text') or '') > 120 for s in st_items)
        cs = ''
        for s in st_items:
            p = P.take(s.get('img'))
            pic = ''
            if p:
                cap = ('max-width:%dpx' % p['w']) if p.get('small') and p.get('w') else ''
                pic = '<div class="cd-m" data-slot="card">%s</div>' % _img(p, style=cap)
            ttl = s.get('title') or s.get('k') or ''
            cs += '<article class="cd%s">%s<h3 class="cd-t">%s</h3>%s%s</article>' % ('' if pic else ' cd-0', pic, e(ttl), _paras(s.get('text'), 'cd-x'),
                                                                                 '<div class="cd-b">%s</div>' % _btn(s.get('cta'), 'p') if isinstance(s.get('cta'), dict) and s['cta'].get('t') else '')
        usp = '<p class="usp">%s</p>' % ' · '.join(e(t) for t in trust) if trust else ''
        trust = []
        cards = ('<section class="sec cards"><div class="w">%s%s%s%s%s</div></section>'
                 % ('<p class="eb">%s</p>' % e(hero.get('kicker')) if hero.get('kicker') else '', '<h2 class="h2 h2-xl">%s</h2>' % e(steps.get('title')) if steps.get('title') else '',
                    _paras(steps.get('text'), 'ld'), usp, '<div class="cds cds-%d%s">%s</div>' % (cols, ' cds-long' if longt else '', cs) if cs else ''))

    # ---- quarter cards (the reference's four ways) and ruled rows: projects, spaces, catalogue ----
    def qcards(items, title='', text='', cls=''):
        """items: [(pic, label, title, text, link{t,h})]"""
        if not items:
            return ''
        sp = _spans(len(items))
        out = ''
        for (pic, label, ttl, tx, lk), s in zip(items, sp):
            m = '<div class="qc-m" data-slot="tile">%s</div>' % _img(pic, style=('max-width:%dpx' % pic['w']) if pic.get('small') and pic.get('w') else '') if pic else ''
            out += '<article class="qc qc-%d%s">%s%s<h3 class="qc-t">%s</h3>%s%s</article>' % (
                s, '' if pic else ' qc-0', m, '<p class="eb qc-l">%s</p>' % e(label) if label else '', e(ttl), _paras(tx, 'qc-x'),
                '<a class="lk" href="%s">%s</a>' % (e(lk.get('h') or '#'), e(lk['t'])) if isinstance(lk, dict) and lk.get('t') else '')
        head = ('<h2 class="h2">%s</h2>' % e(title) if title else '') + _paras(text, 'ld')
        return '<section class="sec quarters %s"><div class="w">%s<div class="qcs">%s</div></div></section>' % (cls, head, out)

    shown_text = {(s.get('text') or '').strip() for s in st_items}
    cat_cards, cat_groups, n_rows = [], [], 0
    for g in cgroups:
        rs = []
        for it in g.get('items') or []:
            if not isinstance(it, dict) or not it.get('name'):
                continue
            tx = it.get('text') or ''
            if tx.strip() in shown_text:
                tx = ''
            price = it.get('price') or ''
            if it.get('from') and price and not any(ch.isalpha() for ch in price.split()[0] if price.split()):
                price = price
            pic = P.take(it.get('img')) if it.get('img') and not (it.get('prices') or it.get('rows')) and len(tx) <= 260 else None
            if pic:
                cat_cards.append((pic, ' · '.join(x for x in (price, it.get('state')) if x), it['name'], tx or it.get('note') or '', {'t': it['name'], 'h': it['h']} if it.get('h') else None))
                continue
            rs.append(_row(it['name'], price=price, text='\n\n'.join(x for x in (tx, it.get('note')) if x), prices=it.get('prices') or (), rows=it.get('rows') or (),
                           link=it.get('h'), state=it.get('state') or ''))
        n_rows += len(rs)
        cat_groups.append((g.get('t'), g.get('text'), rs))
    cat_text = cat.get('text') or ''
    quarters = ''
    if cat_cards:
        quarters += qcards(cat_cards, cat.get('title') if not n_rows else '', cat_text if not n_rows else '')
    proj_cards = []
    for pr in projects:
        pic = None
        for s in pr.get('photos') or []:
            pic = P.take(s if isinstance(s, str) else (s or {}).get('src'))
            if pic:
                break
        proj_cards.append((pic, '', pr['title'], pr.get('text') or '', {'t': pr['title'], 'h': pr['h']} if pr.get('h') else None))
    proj_cards = [c for c in proj_cards if c[0] or c[3]] or ([] if not proj_cards else proj_cards)
    quarters += qcards(proj_cards, cls='q-proj')
    sp_cards = [(P.take(s.get('img')), '', s.get('title') or '', s.get('text') or '', None) for s in spaces]
    quarters += qcards(sp_cards)

    feats = d.get('features') or {}
    f_items = [f for f in (feats.get('items') or []) if isinstance(f, dict) and f.get('t')]
    cat_names = {(it.get('name') or '').strip().lower() for g in cgroups for it in (g.get('items') or []) if isinstance(it, dict)}
    if f_items and cat_names and all(f['t'].strip().lower() in cat_names for f in f_items):
        f_items = []
    rows_cat = _rows_section('cat', cat.get('title'), cat_text, cat_groups, cat.get('note') or '')
    rows_feat = _rows_section('feat', feats.get('title'), feats.get('text') if feats.get('text') != cat_text else '',
                              [(None, None, [_row(f['t'], text=f.get('d') or '') for f in f_items])]) if f_items else ''
    events = [ev for ev in (place.get('events') or []) if isinstance(ev, dict) and ev.get('what')]
    rows_ev = _rows_section('ev', '', '', [(None, None, [_row(ev['what'], price=ev.get('price') or '', label=ev.get('when') or '', text=ev.get('where') or '',
                                                           link=(ev.get('cta') or {}).get('h'), linkword=(ev.get('cta') or {}).get('t') or '') for ev in events])]) if events else ''
    menu = place.get('menu') or {}
    m_groups = []
    for s in menu.get('sections') or []:
        if not isinstance(s, dict):
            continue
        rs = [_row(it['name'], price=it.get('price') or '', text=it.get('note') or '', link=it.get('h')) for it in (s.get('items') or []) if isinstance(it, dict) and it.get('name')]
        if not rs and s.get('t'):
            m_groups.append((None, None, [_row(s['t'], link=s.get('h'))]))
        elif rs:
            m_groups.append((s.get('t'), None, rs))
    for s in menu.get('lists') or []:
        if isinstance(s, dict) and s.get('t'):
            m_groups.append((None, None, [_row(s['t'], link=s.get('h'))]))
    flat = [r for g in m_groups if g[0] is None for r in g[2]]
    m_groups = [g for g in m_groups if g[0] is not None] + ([(None, None, flat)] if flat else [])
    rows_menu = _rows_section('menu', '', '', m_groups) if m_groups else ''

    # ---- dark half beside an edge-to-edge photograph (the reference's event band) ----
    stm = d.get('statement') or {}
    band = ''
    if stm.get('title') or stm.get('text'):
        bp = P.pick(['workshop', 'room', 'detail', 'action', 'bar', 'work', 'exterior', 'landscape', 'other'], 720, 698, never=('portrait', 'people', 'product'), tall_ok=True)
        band = ('<section class="band dk%s"><div class="band-d"><div class="band-in"><h2 class="h2 rv">%s</h2><div class="band-x">%s</div></div></div>%s</section>'
                % ('' if bp else ' band-0', e(stm.get('title')), _paras(stm.get('text')), '<figure class="band-m" data-slot="half">%s</figure>' % _img(bp) if bp else ''))

    # ---- people (the reference's trainers: dark ground, label, name, text) ----
    ppl = ''
    if people:
        ps = ''
        for p in people:
            pic = P.take(p.get('img'))
            m = ''
            if pic:
                ar = (pic.get('w') or 4) / (pic.get('h') or 3)
                m = '<div class="pp-m" data-slot="portrait" style="aspect-ratio:%.3f">%s</div>' % (max(.8, min(1.5, ar)), _img(pic, style=('max-width:%dpx' % pic['w']) if pic.get('small') and pic.get('w') else ''))
            t2, h2, _n = _tel(p.get('phone'))
            links = ('<a class="lk" href="%s">%s</a>' % (e(h2), e(t2)) if t2 else '') + ('<a class="lk" href="mailto:%s">%s</a>' % (e(p['email']), e(p['email'])) if p.get('email') else '')
            nm = '<a href="%s">%s</a>' % (e(p['h']), e(p['name'])) if p.get('h') else e(p['name'])
            ps += '<article class="pp%s">%s%s<h3 class="qc-t">%s</h3>%s%s</article>' % ('' if m else ' pp-0', m, '<p class="eb">%s</p>' % e(p.get('role')) if p.get('role') else '', nm,
                                                                                    _paras(p.get('text'), 'qc-x'), '<p class="pp-l">%s</p>' % links if links else '')
        n = len(people)
        ppl = ('<section class="sec people dk"><div class="w">%s<div class="pps pps-%d%s">%s</div></div></section>'
               % ('<div class="pp-h">%s%s</div>' % ('<h2 class="h2">%s</h2>' % e(team.get('title')) if team.get('title') else '', _paras(team.get('text'), 'ld')) if team.get('title') or team.get('text') else '',
                  n if n <= 4 else 4, ' pps-long' if any(len(p.get('text') or '') > 160 for p in people) else '', ps))

    # ---- plans (the reference's membership cards: the marked one dark) ----
    plans = d.get('plans') or {}
    pl_items = [p for p in (plans.get('items') or []) if isinstance(p, dict) and p.get('name')]
    pls = ''
    if pl_items:
        marked = any(p.get('marked') for p in pl_items)
        for i, p in enumerate(pl_items):
            dark = bool(p.get('marked')) if marked else i == 0
            c = p.get('cta') if isinstance(p.get('cta'), dict) else None
            pls += ('<article class="pl%s">%s<h3 class="pl-n">%s</h3>%s%s%s%s</article>'
                    % (' pl-d dk' if dark else '', '<p class="pl-g">%s</p>' % e(p['marked']) if isinstance(p.get('marked'), str) else '', e(p['name']),
                       '<p class="pl-l">%s</p>' % e(p['line']) if p.get('line') else '',
                       '<p class="pl-p">%s%s</p>' % (e(p.get('price')), '<span>%s</span>' % e(p['per']) if p.get('per') else '') if p.get('price') else '',
                       '<ul class="pl-r">%s</ul>' % ''.join('<li>%s</li>' % e(r) for r in (p.get('rows') or []) if r) if p.get('rows') else '',
                       _btn(c, 'p' if dark else 'o', ' pl-b') if c and c.get('t') else ''))
        pls = ('<section class="sec plans"><div class="w">%s%s<div class="pls pls-%d">%s</div>%s</div></section>'
               % ('<h2 class="h2 h2-c">%s</h2>' % e(plans.get('title')) if plans.get('title') else '', _paras(plans.get('text'), 'ld ld-c'), min(len(pl_items), 3), pls, _paras(plans.get('note'), 'nt nt-c')))

    # ---- quotes (the reference's reviews: moving headline, chips, white cards with the accent on top) ----
    quotes = [q for q in (d.get('quotes') or []) if isinstance(q, dict) and q.get('q')]
    rev = ''
    if quotes or creds:
        chips = ''.join('<span class="chip"><span class="chip-t">%s</span>%s</span>' % (e(c['t']), '<b>%s</b>' % e(c['year']) if c.get('year') else '') for c in creds)
        qs = ''
        for q in quotes:
            who = ', '.join(x for x in (q.get('name'), q.get('role')) if x)
            qs += '<blockquote class="qt"><span class="qt-m" aria-hidden="true">“</span>%s<p class="qt-x">%s</p>%s</blockquote>' % (
                '<p class="qt-h">%s</p>' % e(q['title']) if q.get('title') else '', e(q['q']), '<cite>%s</cite>' % e(who) if who else '')
        cl = ''.join('<p>%s%s</p>' % ('<a class="lk-p" href="%s">%s</a> · ' % (e(c['h']), e(c['t'])) if c.get('h') else '', e(c.get('text'))) for c in creds if c.get('text'))
        rev = ('<section class="sec reviews">%s<div class="w">%s%s%s</div></section>'
               % (_marquee(name, 'h2'), '<div class="chips">%s</div>' % chips if chips else '',
                  '<div class="qts qts-%d">%s</div>' % (min(len(quotes), 3), qs) if qs else '', '<div class="rv-f">%s</div>' % cl if cl else ''))

    # ---- partner marks ----
    logos = [l for l in (d.get('logos') or []) if isinstance(l, dict) and l.get('src')]
    lg = ''
    if logos:
        lg = '<section class="sec partners"><div class="w"><div class="lgs">%s</div></div></section>' % ''.join('<img src="../../%s" alt="%s" loading="lazy">' % (e(l['src']), e(l.get('alt') or l.get('name'))) for l in logos)

    # ---- questions ----
    faq = d.get('faq') or {}
    fq = [f for f in (faq.get('items') or []) if isinstance(f, dict) and f.get('q')]
    faqs = _rows_section('faq', faq.get('title'), '', [(None, None, [_row(f['q'], text=f.get('a') or '') for f in fq])]) if fq else ''

    # ---- a picture band of the client's between two long lists (CONTRACT: picture share, rule 3) ----
    def pband():
        p = P.pick(['room', 'work', 'exterior', 'landscape', 'workshop', 'bar', 'detail', 'action', 'other'], 1440, 600, never=('portrait', 'people', 'product', 'dish'))
        return '<figure class="pband" data-slot="band">%s</figure>' % _img(p) if p else ''

    # ---- closing ----
    close = d.get('close') or {}
    cl = ''
    if close.get('title') or close.get('text'):
        av = P.pick(['detail', 'workshop', 'dish', 'product', 'other', 'room', 'bar', 'action', 'work', 'exterior', 'landscape'], 400, 400, never=('portrait', 'people'), tall_ok=True)
        cb = _btn(close.get('cta') if isinstance(close.get('cta'), dict) else cta, 'p')
        if ph_t:
            cb += '<a class="btn btn-o" href="%s"><span>%s</span></a>' % (e(ph_h), e(ph_t))
        cl = ('<section class="close dk%s">%s%s<div class="w"><div class="close-in">%s%s</div></div></section>'
              % ('' if av else ' close-0', '<figure class="close-m" data-slot="closing">%s<i></i></figure>' % _img(av) if av else '', _marquee(close.get('title'), 'h2'),
                 _paras(close.get('text')), '<div class="close-b">%s</div>' % cb if cb else ''))

    # ---- foot ----
    foot = d.get('foot') or {}
    seen = {n['t'].strip().lower() for n in nav}
    extra = []
    for l in (d.get('links') or []):
        if isinstance(l, dict) and l.get('t') and l['t'].strip().lower() not in seen and l['t'].strip().lower() not in HOME:
            seen.add(l['t'].strip().lower())
            extra.append(l)
    big = [(n['t'], n.get('h')) for n in nav] + [(l['t'], l.get('h')) for l in extra]
    half = math.ceil(len(big) / 2) if len(big) > 5 else len(big)
    col_a, col_b = big[:half], big[half:]
    bl = lambda xs: '<ul class="ft-big">%s</ul>' % ''.join('<li><a href="%s">%s</a></li>' % (e(h or '#'), e(t)) for t, h in xs) if xs else ''
    ftxt = foot.get('text') or ''
    addr = place.get('address') if isinstance(place.get('address'), dict) else None
    addr_html = _addr(addr) if addr and not (addr.get('postcode') and addr['postcode'] in ftxt) else ''
    c1 = '<a class="logo ft-logo" href="%s">%s</a>' % (e(home), logo)
    # the client's foot line is kept; where it carries the phone or the address of the mail, those parts become the links
    parts, in_txt = [x.strip() for x in ftxt.split(' · ') if x.strip()], set()
    if parts:
        fx = ''
        for x in parts:
            if ph_t and x == ph_t:
                fx += '<a class="ul" href="%s">%s</a>' % (e(ph_h), e(x)); in_txt.add('p')
            elif email and x == email:
                fx += '<a class="ul%s" href="mailto:%s">%s</a>' % (' sm' if len(x) > 26 else '', e(x), e(x)); in_txt.add('e')
            else:
                fx += '<span>%s</span>' % e(x)
        c1 += '<p class="ft-x">%s</p>' % fx
    lines1 = ''
    if ph_t and 'p' not in in_txt:
        lines1 += '<a class="ul" href="%s">%s</a>%s' % (e(ph_h), e(ph_t), '<span class="ft-n">%s</span>' % e(ph_n) if ph_n else '')
    if email and 'e' not in in_txt:
        lines1 += '<a class="ul%s" href="mailto:%s">%s</a>' % (' sm' if len(email) > 26 else '', e(email), e(email))
    for r in contact.get('routes') or []:
        if isinstance(r, dict) and r.get('t'):
            lines1 += ('<a class="ul" href="%s">%s</a>' % (e(r['h']), e(r['t'])) if r.get('h') else '<span>%s</span>' % e(r['t'])) + ('<span class="ft-n">%s</span>' % e(r['note']) if r.get('note') else '')
    form = contact.get('form') if isinstance(contact.get('form'), dict) and (contact.get('form') or {}).get('t') else None
    c1 += '<p class="ft-c">%s</p>' % lines1 if lines1 else ''
    hrs = _hours(place.get('hours'))
    blockA = ''
    if addr_html:
        blockA += '<p class="ft-a">%s</p>' % addr_html
    if hrs:
        blockA += '<p class="ft-h">%s</p>' % hrs
    soc = ''.join('<a class="ul" href="%s">%s</a>' % (e(s.get('h') or '#'), e(s['t'])) for s in (place.get('social') or []) if isinstance(s, dict) and s.get('t'))
    if soc:
        blockA += '<p class="ft-s">%s</p>' % soc
    navb = []
    for l in (place.get('booking'), form, cta):
        if isinstance(l, dict) and l.get('t') and l['t'] not in [x['t'] for x in navb]:
            navb.append(l)
    blockB = ''.join('<a class="ft-go" href="%s"><span>%s</span><i aria-hidden="true">↗</i></a>' % (e(l.get('h') or '#'), e(l['t'])) for l in navb[:2])
    locs = ''
    for l in d.get('locations') or []:
        if not isinstance(l, dict) or not l.get('name'):
            continue
        t3, h3, _n = _tel(l.get('phone'))
        locs += '<div class="lc"><h3 class="lc-n">%s</h3>%s%s%s%s%s</div>' % (
            '<a href="%s">%s</a>' % (e(l['h']), e(l['name'])) if l.get('h') else e(l['name']), '<p>%s</p>' % _addr(l.get('address')) if l.get('address') else '',
            '<p><a class="ul" href="%s">%s</a></p>' % (e(h3), e(t3)) if t3 else '', '<p><a class="ul" href="mailto:%s">%s</a></p>' % (e(l['email']), e(l['email'])) if l.get('email') else '',
            '<p class="ft-h">%s</p>' % _hours(l.get('hours')) if l.get('hours') else '', _paras(l.get('note')))
    notices = ''
    for nt in place.get('notices') or []:
        if isinstance(nt, dict):
            notices += '<div class="nc">%s%s</div>' % ('<img src="../../%s" alt=""%s loading="lazy">' % (e(nt['img']), ' width="%d" height="%d"' % (nt['w'], nt['h']) if nt.get('w') and nt.get('h') else '') if nt.get('img') else '',
                                                    ''.join('<p>%s</p>' % e(x) for x in (nt.get('text') or []) if x))
    footer = ('<footer class="ft dk"><div class="w"><div class="ft-g"><div class="ft-1">%s</div><div class="ft-3">%s</div><div class="ft-4">%s</div><div class="ft-3b">%s</div><div class="ft-4b">%s</div></div>%s%s'
              '<div class="ft-z">%s%s</div></div></footer>'
              % (c1, bl(col_a), bl(col_b), blockA, blockB, '<div class="lcs">%s</div>' % locs if locs else '', '<div class="ncs">%s</div>' % notices if notices else '',
                 '<p>%s</p>' % e(foot.get('legal')) if foot.get('legal') else '',
                 '<ul>%s</ul>' % ''.join('<li><a href="%s">%s</a></li>' % (e(l.get('h') or '#'), e(l['t'])) for l in (foot.get('links') or []) if isinstance(l, dict) and l.get('t')) if foot.get('links') else ''))

    # long lists are broken by a picture band when the client still has a wide photograph
    long_cat = n_rows >= 12
    body = (opening + facts + cards + quarters + band + rows_cat + (pband() if long_cat and (rows_feat or rows_ev or rows_menu or ppl) else '') + rows_feat + rows_ev + rows_menu
            + ppl + pls + rev + lg + (pband() if len(fq) >= 8 else '') + faqs + cl)

    css = CSS % dict(g=_hex(T['g']), k=_hex(T['k']), D=_hex(T['D']), onD=_hex(T['onD']), card=_hex(T['card']), acc=_hex(T['acc']), onA=_hex(T['onA']),
                     kdim=_hex(T['kdim']), cdim=_hex(T['cdim']), ddim=_hex(T['ddim']), panel=_hex(T['panel']), veil=_rgba(T['V'], T['al']),
                     veil0=_rgba(T['D'], 0), veil3=_rgba(T['D'], T['al3']), ln=_rgba(T['D'] if T['light'] else T['k'], .06), lnd=_rgba(T['onD'], .09),
                     rule=_rgba(T['D'] if T['light'] else T['k'], .12), cb=_rgba(T['k'], .08), chb=_rgba(T['k'], .15), pb=_rgba(T['onD'], .12),
                     plb=_rgba(T['k'], .14), scheme='light' if T['light'] else 'dark')
    return ('<!doctype html><html lang="%s"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>%s</title>'
            '<meta name="description" content="%s">%s<style>%s</style><script>document.documentElement.className="js"</script></head><body>%s%s%s<main id="main">%s</main>%s<script>%s</script></body></html>'
            % (e(lang), e(name + (' — ' + hero['title'] if hero.get('title') and hero['title'] != name else '')), e(hero.get('text')), FONTS, css, bar, oc, floatb, body, footer, JS))


CSS = r"""
:root{--g:%(g)s;--k:%(k)s;--D:%(D)s;--onD:%(onD)s;--card:%(card)s;--acc:%(acc)s;--onA:%(onA)s;--kdim:%(kdim)s;--cdim:%(cdim)s;--ddim:%(ddim)s;--ln:%(ln)s;--rule:%(rule)s;
--pad:4.86vw;--dis:"Inter Tight","Helvetica Neue",Helvetica,Arial,sans-serif;--mono:"Space Mono",ui-monospace,Menlo,monospace;color-scheme:%(scheme)s}
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%%}
body{margin:0;background:var(--g);color:var(--k);font:400 16.5px/1.47 var(--mono);overflow-x:hidden;-webkit-font-smoothing:antialiased}
img,video{display:block;max-width:100%%}
h1,h2,h3,p,ul,figure,blockquote{margin:0;padding:0}
ul{list-style:none}
a{color:inherit}
.w{position:relative;z-index:1;padding:0 var(--pad)}
main p,main h2,main h3,footer p,footer a,.eb{overflow-wrap:anywhere}
.h2,.cd-t,.qc-t,.fc-v,.pl-n{-webkit-hyphens:auto;hyphens:auto}
.pp-l a{max-width:100%%}
.dk{background:var(--D);color:var(--onD);--fo:var(--onD)}
:focus-visible{outline:2px solid var(--fo,var(--k));outline-offset:3px}
/* the three hairlines of the four-column grid run through every section */
.sec,.hero,.close,.ft{position:relative}
.sec::before,.hero::before,.close::before,.ft::before{content:"";position:absolute;z-index:0;top:0;bottom:0;left:var(--pad);right:var(--pad);pointer-events:none;
background:linear-gradient(var(--ln),var(--ln)) 23.65%% 0/1px 100%% no-repeat,linear-gradient(var(--ln),var(--ln)) 50%% 0/1px 100%% no-repeat,linear-gradient(var(--ln),var(--ln)) 76.35%% 0/1px 100%% no-repeat}
.dk.sec::before,.hero::before,.close::before,.ft::before{--ln:%(lnd)s}
.sec{padding:115px 0}
.h2{font:400 52.5px/1 var(--dis);text-transform:uppercase;overflow-wrap:break-word}
.h2-xl{font-size:75px;padding-top:4px}
.eb{font:400 10.5px/1.47 var(--mono);text-transform:uppercase;color:var(--acc);margin-bottom:31px}
.dk .eb{color:var(--onD)}
.ld{max-width:450px;margin-top:14px}
.ld+.ld{margin-top:12px}
.lk{font:700 12px/1.47 var(--mono);text-decoration:underline;text-underline-offset:2px;transition:color .25s ease-in-out}
.lk:hover{color:var(--acc)}
.dk .lk:hover{color:var(--onD);opacity:.75}
.ul{text-decoration:underline;text-underline-offset:3px}
/* buttons: square, 37.5 high, mono capitals; the other colour wipes in from the left in .3s */
.btn{position:relative;z-index:0;display:inline-flex;align-items:center;justify-content:center;min-height:37.5px;padding:6px 15px;font:400 12px/1.47 var(--mono);text-transform:uppercase;text-decoration:none;text-align:center;
color:var(--onA);background:var(--acc);border:1px solid var(--acc);overflow:hidden;transition:color .25s ease-in-out,border-color .25s ease-in-out;--fo:var(--k)}
.btn span{position:relative;overflow-wrap:anywhere}
.btn::after{content:"";position:absolute;z-index:-1;inset:-1px;background:var(--D);transform:scaleX(0);transform-origin:0 50%%;transition:transform .3s ease}
.btn:hover::after,.btn:focus-visible::after{transform:scaleX(1)}
.btn-p:hover{color:var(--onD);border-color:var(--D)}
.dk .btn{--fo:var(--onD)}
.dk .btn-p::after{background:var(--onD)}
.dk .btn-p:hover{color:var(--D);border-color:var(--onD)}
.btn-o{background:transparent;color:var(--k);border-color:var(--k)}
.btn-o::after{background:var(--acc)}
.btn-o:hover{color:var(--onA);border-color:var(--acc)}
.dk .btn-o{color:var(--onD);border-color:var(--onD)}
.dk .btn-o:hover{color:var(--onA);border-color:var(--acc)}
.btn-w{background:var(--onD);color:var(--D);border-color:var(--onD);font-weight:700}
.btn-w::after{background:var(--acc)}
.btn-w:hover{color:var(--onA);border-color:var(--acc)}
/* bar */
.hd{position:fixed;z-index:50;top:0;left:0;right:0;height:75px;padding:0 var(--pad);display:flex;align-items:center;color:var(--onD);--fo:var(--onD);transition:transform .25s ease-in-out .2s,background-color .25s ease-in-out .2s,height .25s ease-in-out .2s}
.hd.sc{transform:translateY(-100%%);background:var(--D)}
.hd.sc.up{transform:none;height:68px}
.hd:focus-within{transform:none}
.logo{font:400 17px/1.1 var(--dis);letter-spacing:.24em;text-transform:uppercase;text-decoration:none;flex:0 1 auto;max-width:23.65%%;padding-right:20px}
.hd .logo{width:calc((100vw - 2*var(--pad))*.2365);max-width:none;flex:none}
.logo-i{height:21px;width:auto}
.hd-n{display:flex;gap:30px;margin-left:32px;flex:1 1 auto;min-width:0}
.hd-n a{position:relative;font:400 12px/1.47 var(--mono);text-transform:uppercase;text-decoration:none;padding:3.75px 0;white-space:nowrap}
.hd-n a::before{content:"";position:absolute;left:0;right:0;bottom:0;height:1px;background:currentColor;transform:scaleX(0);transform-origin:0 50%%;transition:transform .25s ease}
.hd-n a:hover::before,.hd-n a:focus-visible::before{transform:scaleX(1)}
.hd-b{display:flex;gap:8px;margin-left:20px;flex:none}
.hd-b .btn{white-space:nowrap;max-width:260px}
.hd-b .btn span{overflow:hidden;text-overflow:ellipsis}
.hd .btn{--fo:var(--onD)}
.hd .btn-o{color:var(--onD);border-color:var(--onD)}
.hd .btn-p::after{background:var(--onD)}
.hd .btn-p:hover{color:var(--D);border-color:var(--onD)}
.mb,.oc-x{display:none;font:inherit;color:inherit;background:none;border:1px solid currentColor;cursor:pointer}
.oc{position:fixed;z-index:60;inset:0;overflow:auto;padding:20px 18px 40px;opacity:0;visibility:hidden;transform:translateY(-12px);transition:visibility .25s ease-in-out,opacity .25s ease-in-out,transform .25s ease-in-out}
.oc[hidden]{display:block}
.oc.on{opacity:1;visibility:visible;transform:none}
.oc-h{display:flex;align-items:center;justify-content:space-between;height:40px}
.oc-h .logo{max-width:none}
.oc-x{display:block;width:47px;height:40px;position:relative}
.oc-x i::before,.oc-x i::after{content:"";position:absolute;left:50%%;top:50%%;width:15px;height:1px;background:currentColor;transform:translate(-50%%,-50%%) rotate(45deg)}
.oc-x i::after{transform:translate(-50%%,-50%%) rotate(-45deg)}
.oc-b{padding-top:36px;display:flex;flex-direction:column;align-items:flex-start}
.oc-c{width:100%%;min-height:48px;font-size:15px}
.oc nav{width:100%%;margin-top:28px;border-top:1px solid var(--onD)}
.oc nav a{display:block;padding:16px 0;border-bottom:1px solid var(--onD);font:400 15px/1.47 var(--mono);text-transform:uppercase;text-decoration:none}
.oc-t{margin-top:34px;font:700 15px/1.47 var(--mono);text-decoration:none}
.oc .btn-o{margin-top:30px;min-height:40px;font-size:15px}
/* opening */
.hero{padding-bottom:75px;background:var(--g);isolation:isolate}
.hero-bg{position:absolute;z-index:-1;inset:0 0 75px 0;background:var(--D);overflow:hidden}
.hero-m{position:absolute;inset:0;width:100%%;height:100%%;object-fit:cover}
.veil{position:absolute;inset:0;background:%(veil)s}
.hero::before{bottom:75px}
.hero-in{display:flex;flex-direction:column;justify-content:flex-end;min-height:max(620px,calc(100svh));padding-top:118px;padding-bottom:14px}
.hero-p{order:1;align-self:flex-end;width:23.65%%;font-size:16px;line-height:1.6;margin-bottom:36px}
.hero-p.tuck{margin-bottom:-35px}
.hero-pw{width:50%%}
.hero-p p+p{margin-top:12px}
.hero-t{order:2;position:relative;display:grid;grid-template-columns:auto 1fr;column-gap:40px;align-items:center}
.h1{display:contents;font:300 calc(var(--h1)*1px)/1 var(--dis)}
.h1a,.h1b{display:block;font:300 min(calc(var(--h1)/14.4*1vw),calc(var(--h1)*1.3px))/1 var(--dis);letter-spacing:-.053em;text-transform:uppercase;position:relative;z-index:1;overflow-wrap:break-word;min-width:0;animation:rise .6s cubic-bezier(.22,.61,.36,1) .7s both}
.h1a{grid-column:1/-1;grid-row:1;padding-right:.05em}
.h1b{grid-column:2;grid-row:2;text-align:right;animation-delay:1.05s;padding-right:.04em}
.hero-c{grid-column:1;grid-row:2;position:relative;z-index:1;display:flex;flex-wrap:wrap;gap:11px;align-items:center;max-width:30vw;margin-top:-56px}
.hero-n{font:400 12px/1.47 var(--mono);flex-basis:100%%}
.box{position:absolute;z-index:0;left:76.35%%;right:calc(var(--pad)*-1);top:75px;bottom:-89px;background:var(--D)}
.hero-p{animation:fade .5s ease 1.6s both}
@keyframes rise{from{opacity:0;transform:translateY(100px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
/* facts */
.facts{padding:78px 0 90px}
.hero+.facts{margin-top:-75px;padding-top:153px}
.g4{display:grid;grid-template-columns:23.65fr 26.35fr 26.35fr 23.65fr;row-gap:44px}
.fc{padding-right:33px;min-width:0}
.fc-l{font:400 10.5px/1.47 var(--mono);text-transform:uppercase;color:var(--ddim);margin-bottom:13px}
.fc-v{font:400 25.5px/1.02 var(--dis);text-transform:uppercase;overflow-wrap:break-word}
/* large cards */
.cards{padding-bottom:43px}
.usp{font-size:13.5px;margin-top:14px;max-width:760px}
.cds{display:grid;gap:60px 30px;margin-top:60px}
.cds-2{grid-template-columns:1fr 1fr}
.cds-3{grid-template-columns:1fr 1fr 1fr}
.cd{min-width:0}
.cd-m{aspect-ratio:635/397;overflow:hidden;margin-bottom:22px;background:var(--rule)}
.cd-m img,.qc-m img,.pp-m img{width:100%%;height:100%%;object-fit:cover}
.cd-0{border-top:1px solid var(--k);padding-top:22px}
.cd-t{font:400 36px/1 var(--dis);text-transform:uppercase;overflow-wrap:break-word}
.cds-3 .cd-t{font-size:30px}
.cd-x{font-size:13.5px;margin-top:12px}
.cd-b{margin-top:26px;display:flex;flex-wrap:wrap;gap:11px}
/* quarter cards */
.quarters .h2+.qcs,.quarters .ld+.qcs{margin-top:59px}
.cards+.quarters.q-proj{padding-top:72px}
.qcs{display:grid;grid-template-columns:23.65fr 26.35fr 26.35fr 23.65fr;row-gap:56px}
.qc{padding-right:33px;min-width:0}
.qc-2{grid-column:span 2}
.qc-m{height:233px;overflow:hidden;margin-bottom:26px;background:var(--rule)}
.qc-0{border-top:1px solid var(--k);padding-top:22px}
.qc-l{margin-bottom:12px}
.qc-t{font:400 25.5px/1 var(--dis);text-transform:uppercase;overflow-wrap:break-word}
.qc-t a{text-decoration:none}
.qc-x{font-size:12.75px;margin-top:14px}
.qc-x+.qc-x{margin-top:9px}
.qc .lk{display:inline-block;margin-top:16px}
/* dark half and photograph */
.band{position:relative;display:flex;align-items:flex-start;background:var(--g)}
.band-d{width:50%%;min-height:773px;background:var(--D);padding:150px 40px 150px var(--pad);display:flex}
.band-in{max-width:520px}
.band .h2{padding-top:47px}
.band-x{max-width:311px;margin-top:67px;font-size:13.5px}
.band-x p+p{margin-top:12px}
.band-m{position:absolute;right:0;top:75px;bottom:0;width:50%%;overflow:hidden;background:var(--D)}
.band-m img{width:100%%;height:100%%;object-fit:cover}
.band-0 .band-d{width:100%%;min-height:0;padding:115px var(--pad)}
.band-0 .band-in{max-width:none;display:grid;grid-template-columns:1fr 1fr;width:100%%}
.band-0 .h2{padding-top:0}
.band-0 .band-x{margin-top:6px;max-width:450px}
.js .rv{opacity:0;transform:translateY(34px);transition:opacity .7s ease,transform .7s cubic-bezier(.22,.61,.36,1)}
.js .rv.in{opacity:1;transform:none}
/* ruled rows */
.mid{margin-left:23.65%%;width:52.7%%}
.mid-h{margin-bottom:56px}
.rg+.rg{margin-top:38px}
.rg-t{font:700 16.5px/1.47 var(--mono);margin-bottom:22px}
.rg-x{font-size:13.5px;margin:-10px 0 22px}
.rws{border-top:1px solid var(--k)}
.rw{display:block;border-bottom:1px solid var(--k);padding:9px 0;color:inherit;text-decoration:none}
.rw summary,.rw-f{display:flex;align-items:baseline;gap:18px;cursor:pointer;list-style:none}
.rw summary{padding:4.5px 0}
.rw-f{padding:13.5px 0;cursor:auto}
a.rw-f{cursor:pointer;transition:color .25s ease-in-out}
a.rw-f:hover{color:var(--acc)}
.rw summary::-webkit-details-marker{display:none}
.rw-h{flex:1 1 auto;min-width:0;overflow-wrap:break-word}
.rw-l{display:block;font:400 10.5px/1.47 var(--mono);text-transform:uppercase;color:var(--acc);margin-bottom:2px}
.rw-p{font-weight:700;flex:none;max-width:48%%;text-align:right}
.rw-s{font:400 10.5px/1.47 var(--mono);text-transform:uppercase;border:1px solid var(--k);padding:1px 7px;flex:none;align-self:center}
.pm{position:relative;flex:none;width:13px;height:13px;align-self:center}
.pm::before,.pm::after{content:"";position:absolute;left:0;top:6px;width:13px;height:1px;background:currentColor;transition:transform .25s ease-in-out}
.pm::after{transform:rotate(90deg)}
.rw[open] .pm::after{transform:none}
.ar{font-style:normal;flex:none}
.rw-a{padding:8px 34px 14px 0;font-size:13.5px}
.rw-a p+p,.rw-a ul+p,.rw-a p+ul{margin-top:10px}
.rw-pr li{display:flex;justify-content:space-between;gap:18px;padding:5px 0;border-top:1px solid var(--rule)}
.rw-li li{padding-left:16px;position:relative;margin-top:4px}
.rw-li li::before{content:"";position:absolute;left:0;top:.72em;width:7px;height:1px;background:currentColor}
.nt{font-size:12px;color:var(--kdim);margin-top:22px}
.rowsec+.rowsec{padding-top:0}
.pband{height:min(62vw,620px);overflow:hidden}
.pband img{width:100%%;height:100%%;object-fit:cover}
/* people */
.people{padding:112px 0 142px}
.pp-h{margin-left:23.65%%;margin-bottom:64px}
.pp-h .ld{max-width:560px}
.pps{display:grid;gap:56px 30px}
.pps-1{grid-template-columns:minmax(0,420px)}
.pps-2{grid-template-columns:repeat(2,minmax(0,1fr));max-width:900px}
.pps-3{grid-template-columns:repeat(3,minmax(0,1fr))}
.pps-4{grid-template-columns:repeat(4,minmax(0,1fr))}
.pp{min-width:0}
.pp-m{overflow:hidden;margin-bottom:24px;background:%(panel)s}
.pp-0{border-top:1px solid %(pb)s;padding-top:22px}
.pp .eb{margin-bottom:10px;color:var(--ddim)}
.pp-l{margin-top:16px;display:flex;flex-direction:column;gap:4px;align-items:flex-start}
/* plans */
.h2-c{font-size:36px;text-align:center}
.ld-c{margin:14px auto 0;text-align:center;font-size:13.5px}
.pls{display:grid;gap:22px;justify-content:center;margin-top:46px}
.pls-1{grid-template-columns:minmax(0,401px)}
.pls-2{grid-template-columns:repeat(2,minmax(0,401px))}
.pls-3{grid-template-columns:repeat(3,minmax(0,401px))}
.pl{position:relative;z-index:1;display:flex;flex-direction:column;padding:24px 23px;border:1px solid %(plb)s;background:var(--g);min-width:0}
.pl-d{background:var(--D);border-color:var(--D)}
.pl-g{align-self:flex-start;font:700 9.75px/1.47 var(--mono);text-transform:uppercase;background:var(--onD);color:var(--D);border-radius:20px;padding:3px 9px;margin-bottom:10px}
.pl:not(.pl-d) .pl-g{background:var(--acc);color:var(--onA)}
.pl-n{font:400 16.5px/1.1 var(--dis);text-transform:uppercase;overflow-wrap:break-word}
.pl-l{font-size:11.5px;color:var(--kdim);margin-top:8px}
.pl-d .pl-l,.pl-d .pl-p span{color:var(--ddim)}
.pl-p{font:700 22.5px/1.2 var(--mono);margin-top:18px;overflow-wrap:break-word}
.pl-p span{display:block;font:400 9.75px/1.47 var(--mono);color:var(--kdim);margin-top:6px}
.pl-r{font-size:11.5px;margin:16px 0 0;padding-left:16px}
.pl-r li+li{margin-top:5px}
.pl-b{margin-top:auto;width:100%%}
.pl-r+.pl-b,.pl-p+.pl-b,.pl-l+.pl-b,.pl-n+.pl-b{margin-top:auto}
.pl>*:nth-last-child(2):not(.pl-b){margin-bottom:22px}
.pl .pl-b{transform:translateY(0)}
.pl-r,.pl-p,.pl-l{margin-bottom:0}
.pl-b{margin-top:22px}
.nt-c{text-align:center;max-width:600px;margin-left:auto;margin-right:auto}
/* quotes */
.reviews{padding:142px 0 72px}
.mq{position:relative;z-index:1;overflow:hidden;white-space:nowrap}
.mq-t{display:inline-flex;font:300 112.5px/1.47 var(--dis);letter-spacing:2px;text-transform:uppercase;animation:mq 60s linear infinite;will-change:transform}
.mq-h{display:inline-flex;flex:none}
.mq-d{padding:0 .16em}
@keyframes mq{to{transform:translateX(-50%%)}}
.chips{display:flex;flex-wrap:wrap;justify-content:center;gap:10px;margin-top:53px}
.chip{display:inline-flex;align-items:center;gap:22px;background:var(--card);border:1px solid %(chb)s;padding:14px 24px;max-width:100%%}
.chip-t{font:400 12px/1.47 var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--acc)}
.chip b{font:400 24px/1 var(--dis)}
.qts{display:grid;gap:16px;margin-top:48px}
.qts-1{grid-template-columns:minmax(0,640px);justify-content:center}
.qts-2{grid-template-columns:repeat(2,minmax(0,1fr))}
.qts-3{grid-template-columns:repeat(3,minmax(0,1fr))}
.qt{display:flex;flex-direction:column;background:var(--card);border:1px solid %(cb)s;border-top:3px solid var(--acc);padding:28px 26px;min-height:283px;min-width:0}
.qt-m{font:700 64px/1 Georgia,"Times New Roman",serif;height:26px;color:var(--acc);overflow:hidden;margin-bottom:20px}
.qt-h{font:700 15px/1.6 var(--mono);margin-bottom:8px}
.qt-x{font-size:15px;line-height:1.6;margin-bottom:38px}
.qt cite{margin-top:auto;font:700 12px/1.47 var(--mono);letter-spacing:.04em;text-transform:uppercase;color:var(--cdim)}
.rv-f{margin-top:28px;border-top:1px solid var(--k);padding-top:18px;font-size:12px}
.rv-f p+p{margin-top:6px}
.lk-p{text-decoration:underline;text-underline-offset:2px}
.partners{padding:0 0 100px}
.lgs{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:20px 90px;border-top:1px solid var(--rule);border-bottom:1px solid var(--rule);padding:18.75px 0}
.lgs img{width:113px;height:90px;object-fit:contain;filter:grayscale(1);opacity:.7;transition:opacity .3s ease}
.lgs img:hover{opacity:1}
/* closing */
.close{overflow:hidden}
.close .mq{padding-top:203px}
.close-0 .mq{padding-top:110px}
.close-m{position:absolute;z-index:0;left:50%%;top:0;width:200px;height:278px;margin-left:-100px;overflow:hidden}
.close-m img{width:100%%;height:100%%;object-fit:cover}
.close-m i{position:absolute;inset:0;background:linear-gradient(%(veil0)s 0,%(veil0)s 52%%,%(veil3)s 72%%,%(veil3)s 100%%)}
.close-in{text-align:center;font-size:13.5px;padding-bottom:142px;border-bottom:1px solid var(--onD)}
.close-in p{max-width:560px;margin:0 auto}
.close-b{display:flex;flex-wrap:wrap;justify-content:center;gap:8px;margin-top:22px}
/* foot */
.ft{padding-top:125px}
.ft-g{display:grid;grid-template-columns:23.65fr 26.35fr 26.35fr 23.65fr;grid-template-areas:"a . c d" "a . e f";row-gap:62px}
.ft-1{grid-area:a;padding-right:20px;min-width:0}
.ft-3{grid-area:c;padding-right:33px;min-width:0}
.ft-4{grid-area:d;min-width:0}
.ft-3b{grid-area:e;padding-right:33px;min-width:0}
.ft-4b{grid-area:f;min-width:0}
.ft-logo{display:block;max-width:none;padding:0;font-size:22px;line-height:1.1}
.ft-x{margin-top:36px;overflow-wrap:break-word;display:flex;flex-direction:column;align-items:flex-start}
.ft .sm{font-size:14px}
.ft-c{margin-top:44px;display:flex;flex-direction:column;align-items:flex-start;overflow-wrap:anywhere}
.ft-n{font-size:12px;color:var(--ddim)}
.ft-big li+li{margin-top:26px}
.ft-big a{font:400 28.5px/1 var(--dis);text-transform:uppercase;text-decoration:none;transition:opacity .3s ease;overflow-wrap:break-word}
.ft-big a:hover{opacity:.6}
.ft-a,.ft-h,.ft-s{font-size:13.5px}
.ft-a+.ft-h,.ft-a+.ft-s,.ft-h+.ft-s{margin-top:18px}
.hr{display:flex;justify-content:space-between;gap:16px;max-width:340px}
.ft-s{display:flex;flex-wrap:wrap;gap:6px 20px;text-transform:capitalize}
.ft-go{display:flex;justify-content:space-between;align-items:center;gap:16px;padding:13.5px 0;border-bottom:1px solid var(--onD);text-decoration:none;transition:opacity .3s ease}
.ft-go:hover{opacity:.6}
.ft-go i{font-style:normal}
.lcs{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:36px 30px;margin-top:72px;font-size:13.5px}
.lc-n{font:400 25.5px/1 var(--dis);text-transform:uppercase;margin-bottom:12px}
.lc-n a{text-decoration:none}
.lc p+p{margin-top:8px}
.ncs{margin-top:60px;display:flex;flex-wrap:wrap;gap:24px;font-size:10.5px;color:var(--ddim)}
.nc{max-width:420px}
.nc img{background:#fff;max-height:70px;width:auto;margin-bottom:8px}
.ft-z{margin-top:140px;border-top:1px solid var(--onD);padding:22.5px 0;display:flex;flex-wrap:wrap;justify-content:space-between;gap:10px 30px;font:400 10.5px/1.5 var(--mono);text-transform:uppercase}
.ft-z ul{display:flex;flex-wrap:wrap;gap:6px 15px}
.ft-z a{text-decoration:none;transition:opacity .25s ease-in-out}
.ft-z a:hover{opacity:.6}
@media (max-width:1100px){
.hd-n{gap:18px;margin-left:16px}
.hd-b .btn-o{display:none}
.cds-3{grid-template-columns:1fr 1fr}
.pps-4,.pps-3{grid-template-columns:repeat(2,minmax(0,1fr))}
.pls-3{grid-template-columns:repeat(2,minmax(0,401px))}
.mid{margin-left:0;width:100%%;max-width:760px}
.pp-h{margin-left:0}
}
@media (max-width:860px){
:root{--pad:21px}
body{font-size:17px}
.sec::before,.hero::before,.close::before,.ft::before{background:linear-gradient(var(--ln),var(--ln)) 50%% 0/1px 100%% no-repeat}
.sec{padding:48px 0}
.h2,.h2-xl{font-size:30px;padding-top:1.5px}
.eb{font-size:13px;margin-bottom:19px}
.ld{margin-top:19px;max-width:none}
.hd{height:80px;padding:0 18px}
.hd.sc.up{height:68px}
.hd .logo{width:auto;flex:1 1 auto;min-width:0;font-size:15px;letter-spacing:.18em;overflow-wrap:anywhere}
.hd-n,.hd-b{display:none}
.mb{display:flex;align-items:center;gap:8px;height:40px;padding:0 15px;font:400 15px/1 var(--mono);text-transform:uppercase;flex:none}
.mb i{width:14px;height:6px;border-top:1px solid currentColor;border-bottom:1px solid currentColor}
.btn{min-height:40px;font-size:15px}
.hero{padding-bottom:0}
.hero-bg,.hero::before{bottom:0}
.hero-in{display:block;min-height:max(520px,calc(100svh - 150px));padding-top:197px;padding-bottom:24px}
.hero-t{display:block}
.h1a,.h1b{font-size:var(--h1m);letter-spacing:-.042em;text-align:left;padding-top:.05em}
.box{display:none}
.hero-c{max-width:none;margin-top:20px;gap:10px 15px}
.hero-p,.hero-p.tuck,.hero-pw{width:auto;margin:100px 0 0;font-size:15px;line-height:1.55}
.facts,.hero+.facts{margin-top:0;padding:44px 0 48px}
.g4,.qcs{grid-template-columns:1fr 1fr;column-gap:12px;row-gap:28px}
.fc,.qc{padding-right:0}
.fc-v{font-size:19px;line-height:1.1}
.fc-l{font-size:11px;margin-bottom:8px}
.cards{padding-bottom:24px}
.usp{font-size:12px}
.cds,.cds-3{grid-template-columns:1fr 1fr;gap:28px 12px;margin-top:40px}
.cds-long,.cds-long.cds-3{grid-template-columns:1fr}
.cd-m{aspect-ratio:168/140;margin-bottom:12px}
.cds-long .cd-m{aspect-ratio:635/397}
.cd-t,.cds-3 .cd-t{font-size:19px;line-height:1.1}
.cds-long .cd-t{font-size:24px}
.cd-x{font-size:11px;line-height:1.5;margin-top:6px}
.cds-long .cd-x{font-size:13px}
.cd-b{margin-top:22px}
.cd-b .btn{width:100%%;min-height:42px;font-size:11px;letter-spacing:.02em;padding:6px 8px}
.cds-long .cd-b .btn{width:auto;padding:6px 15px}
.quarters{padding:32px 0 48px}
.quarters .h2+.qcs,.quarters .ld+.qcs{margin-top:20px}
.cards+.quarters.q-proj{padding-top:20px}
.qc-2{grid-column:auto}
.qc-m{height:120px;margin-bottom:10px}
.qc-l{display:none}
.qc-t{font-size:18px}
.qc-x{font-size:12px;line-height:1.5;margin-top:6px}
.qc .lk{margin-top:8px}
.band{display:block}
.band-d,.band-0 .band-d{width:100%%;min-height:0;padding:50px 18px 49px}
.band .h2{padding-top:1.5px}
.band-x,.band-0 .band-x{max-width:none;margin-top:29px;font-size:15px}
.band-0 .band-in{display:block}
.band-m{display:none}
.mid{max-width:none}
.mid-h{margin-bottom:32px}
.rw summary,.rw-f{gap:12px}
.rw-a{padding-right:0;font-size:14px}
.people{padding:56px 0 64px}
.pp-h{margin-bottom:36px}
.pps,.pps-2,.pps-3,.pps-4{grid-template-columns:1fr 1fr;gap:32px 12px;max-width:none}
.pps-1,.pps.pps-long{grid-template-columns:1fr}
.h2-c{font-size:26px}
.pls,.pls-2,.pls-3{grid-template-columns:minmax(0,1fr);margin-top:30px}
.reviews{padding:50px 0 48px}
.mq-t{font-size:50px;letter-spacing:0}
.chips{margin-top:39px}
.chip{padding:12px 16px;gap:14px;flex-wrap:wrap;justify-content:center;text-align:center}
.qts,.qts-1,.qts-2,.qts-3{display:flex;gap:12px;margin:28px -21px 0;padding:0 21px 4px;overflow-x:auto;scroll-snap-type:x mandatory;scroll-padding-left:21px;-webkit-overflow-scrolling:touch}
.qt{flex:0 0 285px;scroll-snap-align:start;min-height:372px}
.qts-1 .qt{flex-basis:100%%}
.qt-m{font-size:80px;height:32px;margin-bottom:26px}
.rv-f{font-size:14px;margin-top:40px}
.partners{padding-bottom:64px}
.lgs{gap:16px 40px;justify-content:center}
.close .mq{padding-top:231px}
.close-0 .mq{padding-top:56px}
.close-m{width:195px;height:271px;margin-left:-98px}
.close-in{font-size:15px;padding:20px 0 50px}
.close-b{margin-top:40px;gap:10px}
.ft{padding-top:45px}
.ft-g{grid-template-columns:1fr 1fr;grid-template-areas:"a a" "c d" "f f" "e e";row-gap:44px;column-gap:12px}
.ft-1,.ft-3,.ft-3b{padding-right:0}
.ft-logo{font-size:18px}
.ft-big li+li{margin-top:35px}
.ft-big a{font-size:20px}
.ft-go{padding:15px 0}
.ft-a,.ft-h,.ft-s{font-size:15px}
.lcs{margin-top:48px;font-size:15px}
.ft-z{margin-top:46px;padding:45px 0;font-size:13px;flex-direction:column}
.ft-z ul{gap:7px 20px}
}
@media (prefers-reduced-motion:reduce){
*,*::before,*::after{animation:none!important;transition:none!important}
.js .rv{opacity:1;transform:none}
.mq{white-space:normal}
.mq-t{display:block;white-space:normal;font-size:clamp(34px,6vw,84px);line-height:1.1;padding:0 var(--pad);overflow-wrap:break-word}
.mq-h[aria-hidden],.mq-h .mq-d,.mq-h .mq-i~.mq-i{display:none}
.mq-h{display:block}
.hd.sc{transform:none}
}
"""

JS = r"""(function(){var d=document,h=d.getElementById('hd'),oc=d.getElementById('oc'),mb=d.querySelector('.mb'),x=d.querySelector('.oc-x'),ly=0,t=0;
function sc(){var y=window.scrollY||0;if(h){h.classList.toggle('sc',y>40);h.classList.toggle('up',y>40&&y<ly);}ly=y;t=0}
window.addEventListener('scroll',function(){if(!t)t=requestAnimationFrame(sc)},{passive:true});sc();
function menu(o){if(!oc)return;if(o){oc.hidden=false;oc.offsetWidth;}oc.classList.toggle('on',o);mb.setAttribute('aria-expanded',o?'true':'false');d.documentElement.style.overflow=o?'hidden':'';
if(o){setTimeout(function(){x.focus()},300)}else{setTimeout(function(){if(!oc.classList.contains('on'))oc.hidden=true},260);mb.focus()}}
if(mb&&oc){mb.addEventListener('click',function(){menu(true)});x.addEventListener('click',function(){menu(false)});
d.addEventListener('keydown',function(e){if(e.key==='Escape'&&oc.classList.contains('on'))menu(false)});
oc.addEventListener('click',function(e){if(e.target.closest&&e.target.closest('nav a'))menu(false)});}
var rv=[].slice.call(d.querySelectorAll('.rv'));
if(!('IntersectionObserver' in window)){rv.forEach(function(e){e.classList.add('in')})}else{var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{rootMargin:'0px 0px -12% 0px'});rv.forEach(function(e){io.observe(e)});
setTimeout(function(){rv.forEach(function(e){var r=e.getBoundingClientRect();if(r.top<innerHeight)e.classList.add('in')})},1500)}
})();"""
