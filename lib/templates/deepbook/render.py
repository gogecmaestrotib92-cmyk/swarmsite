"""deepbook/render.py — one pure function: render(d) -> a complete page built to the measures of the reference home page,
measured at 1440 and 390 on 2026-11-12 (see NOTES.md): a dark sticky bar, a 16:9 picture opening with the title laid over
it, four figures, two product panels, a typed heading over a stack of folder tabs, a picture banner, a ruled fact list,
an accordion, and an accent-coloured close and foot. Nothing of the reference's code, words, pictures, icons, logos or
typefaces is in here. No client, no model call, no file read, no network at render."""
import html

M = '../../'
FONT = 'Wix Madefor Display'   # open-licence stand-in for the reference's commercial grotesque (see NOTES.md)


def e(s):
    return html.escape(str(s or ''), quote=True)


# ---------- colour: the client's palette goes in; the reference's relations of canvas / dark / accent are kept ----------
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


def best(bg, *c):
    return max(c, key=lambda x: con(bg, x))


def rgba(h, a):
    r, g, b = _rgb(h)
    return 'rgba(%d,%d,%d,%.2f)' % (r, g, b, a)


def colours(p):
    G, I, A = p.get('ground') or '#ffffff', p.get('ink') or '#000000', p.get('accent') or '#1e6ef3'
    D, L = (G, I) if lum(G) < lum(I) else (I, G)                 # the dark of the bar, and its inverse
    line = mix(G, I, .14)                                        # border and "surface" are one colour in the reference
    tint = mix(G, line, .3)                                      # ground of the fact-list section
    muted = I
    for t in (.5, .45, .4, .35, .3, .25, .2, .15, .1, 0):        # the reference's grey reads 4.6:1 on its canvas
        m = mix(I, G, t)
        if min(con(m, G), con(m, tint)) >= 4.6:
            muted = m
            break
    At = A                                                       # accent as text on the canvas
    for t in (0, .1, .2, .3, .4, .5, .6, .7, .8, 1):
        At = mix(A, I, t)
        if min(con(At, G), con(At, tint)) >= 4.5:
            break
    AtL = A                                                      # accent as large bold text (3:1 is enough from 24px)
    for t in (0, .1, .2, .3, .4, .5, .6, .7, .8, 1):
        AtL = mix(A, I, t)
        if con(AtL, G) >= 3.1:
            break
    onA = best(A, I, G)
    for x in (onA, D, L, '#000000', '#ffffff'):
        if con(A, x) >= 4.5:
            onA = x
            break
    toward = '#ffffff' if lum(onA) < lum(A) else '#000000'       # folders step away from their text, as the reference's do
    folders = [mix(A, toward, t) for t in (0, .1, .2)]
    Ah = mix(A, '#000000', .12)                                  # hover of the main button: a shade darker
    if con(Ah, onA) < 4.5:
        Ah = mix(A, '#ffffff', .14)
    navc = mix(L, D, .14)
    cap = mix(L, D, .1)                                          # the closing key: a light cap in a dark rim
    cap_ink = mix(D, L, .28)
    while con(cap, cap_ink) < 7 and cap_ink != D:                # 7:1, so the label also holds over the cap's own shading
        cap_ink = mix(cap_ink, D, .3) if con(cap, mix(cap_ink, D, .3)) > con(cap, cap_ink) else D
    return dict(G=G, I=I, A=A, D=D, L=L, line=line, tint=tint, muted=muted, At=At, AtL=AtL, onA=onA, folders=folders, Ah=Ah,
                edge=mix(A, onA, .3), navc=navc, sech=mix(line, I, .08), cap=cap, cap_ink=cap_ink, rim=mix(A, '#000000', .62),
                focA=onA)


def fl(lo, hi):
    """a size running straight between the two measured widths, 390 and 1440"""
    s = (hi - lo) / 10.5
    return 'clamp(%spx,%.2fpx + %.3fvw,%spx)' % (lo, lo - s * 3.9, s, hi)


# ---------- pictures ----------
def made(d, kind):
    m = ((d.get('media') or {}).get('made') or {}).get(kind) or []
    return [x for x in (m if isinstance(m, list) else [m]) if isinstance(x, dict) and x.get('src')]


def pick(lst, i):
    return lst[i % len(lst)] if lst else None


def over(m, c):
    """(veil, ink) for text laid over picture m: light ink on a dark picture, dark ink on a light one"""
    return (c['D'], c['L']) if (m or {}).get('tone') != 'light' else (c['L'], c['D'])


def veil_for(m, veil, ink, want=4.5, least=0.0):
    mean = (m or {}).get('mean') or ('#222222' if (m or {}).get('tone') != 'light' else '#dddddd')
    for a in (0, .1, .2, .3, .4, .5, .6, .7, .8, .9):
        if a >= least and con(mix(mean, veil, a), ink) >= want:
            return a
    return .9


def pic(m, cls, slot, lazy=True, alt=''):
    return '<img class="%s" src="%s%s" width="%s" height="%s" alt="%s"%s decoding="async" data-slot="%s">' % (
        cls, M, e(m['src']), int(m.get('w') or 0) or '', int(m.get('h') or 0) or '', e(alt),
        ' loading="lazy"' if lazy else ' fetchpriority="high"', slot)


# ---------- text set for the measured motion ----------
def words(text, cls='w'):
    """each word in its own inline box, so lines can rise one after the other and words can fade in turn"""
    return ' '.join('<span class="%s">%s</span>' % (cls, e(w)) for w in str(text or '').split())


def typed(text):
    """a heading that is typed out: every character in its own box, words kept whole; read aloud as plain text"""
    out = []
    for w in str(text or '').split():
        out.append('<span class="tw">%s</span>' % ''.join('<span class="tc">%s</span>' % e(ch) for ch in w))
    return '<span class="ty-t" aria-hidden="true">%s<span class="cur"></span></span>' % ' '.join(out)


def link(x, cls, extra=''):
    return '<a class="%s" href="%s"%s>%s</a>' % (cls, e(x.get('h') or '#'), extra, e(x.get('t')))


def ulink(x, cls):
    return '<a class="ul %s" href="%s"><span>%s</span></a>' % (cls, e(x.get('h') or '#'), e(x.get('t')))


# ---------- sections ----------
def s_bar(d, c):
    b = d.get('brand') or {}
    wm = bool(b.get('logo') and b.get('logo_wordmark'))
    logo = '<img class="%s" src="%s%s" alt="%s">' % ('wm' if wm else 'mk', M, e(b['logo']), e(b.get('name')) if wm else '') if b.get('logo') else ''
    name = '' if wm else '<span>%s</span>' % e(b.get('name'))
    items = [x for x in (d.get('nav') or []) if x.get('t')]
    if (d.get('signin') or {}).get('t'):
        items.append(d['signin'])
    nav = '<nav class="nv">%s</nav>' % ''.join(ulink(x, 'nl') for x in items) if items else '<span></span>'
    cta = '<div class="hc">%s</div>' % link(d['cta'], 'bt bt-s') if (d.get('cta') or {}).get('t') else '<span></span>'
    long = len((d.get('cta') or {}).get('t') or '') > 16          # a long call leaves the mark too little room on a phone
    return '<header class="hd"><div class="pc hd-in%s"><a class="br" href="%s">%s%s</a>%s%s</div></header>' % (' hd-l' if long else '', e(b.get('home') or '#'), logo, name, nav, cta)


def s_hero(d, c):
    h = dict(d.get('hero') or {})
    h['title'] = h.get('title') or (d.get('brand') or {}).get('name')  # the page's one heading: the title, else the name
    if not h.get('title'):
        return ''
    m = pick(made(d, 'land'), 0)
    veil, ink = over(m, c) if m else (c['D'], c['L'])
    a = veil_for(m, veil, ink, 4.5, .25) if m else 0
    n = len(h['title'])
    ts = '6.6vw' if n <= 36 else '5.6vw' if n <= 60 else '4.6vw'
    sub = h.get('text') or ''
    ss = 'max(14px,3.9vw)' if len(sub) <= 36 else 'max(14px,2.7vw)'
    back = (pic(m, 'bd', 'hero-backdrop:land', lazy=False) + '<span class="vl" style="background:%s"></span>' % rgba(veil, a)) if m else ''
    return ('<section class="hero" style="--hi:%s;--ts:%s;--ss:%s" data-slot-tone="%s">%s<div class="hero-t"><h1>%s</h1>%s</div></section>'
            % (ink, ts, ss, (m or {}).get('tone', 'none'), back, _hero_words(h['title']),
               '<p class="hero-s">%s</p>' % e(sub) if sub else ''))


def _hero_words(t):
    return ' '.join('<span class="hw"><span>%s</span></span>' % e(w) for w in str(t).split())


def s_figures(d, c):
    fs = [f for f in (d.get('figures') or []) if f.get('v')]
    if not fs:
        return ''
    cells = ''.join('<div class="mt"><dd class="mf" aria-label="%s"><span class="mv" data-pp="14" aria-hidden="true">%s</span></dd><dt class="ml" data-words>%s</dt></div>'
                    % (e(f['v']), e(f['v']), words(f.get('l'))) for f in fs)
    return '<section class="mts"><dl class="pc mtg" data-g style="--n:%d">%s</dl></section>' % (min(len(fs), 4), cells)


def s_products(d, c):
    pl = d.get('plans') or {}
    items = [x for x in (pl.get('items') or []) if x.get('name')]
    if not items:
        return ''
    md = d.get('media') or {}
    screens = [x for x in (md.get('screens') or []) if x.get('src')]
    # one ground for every panel, as on the reference (there: one flat accent): the page's own landscape series, the soft
    # square one a device stands on, in a different crop per panel, held quiet toward the page ground
    bl = pick(made(d, 'land'), 3)
    wrong = bl and lum(c['G']) < .18 and bl.get('tone') == 'light'      # a dark page never takes a light picture as a panel
    va = (.72 if wrong else .38) if bl else 0
    crops = ('50% 18%', '50% 82%', '50% 50%')
    out = []
    for i, x in enumerate(items):
        sc = screens[i] if i < len(screens) else None
        inner = ((pic(bl, 'bd', 'panel-%d:land' % (i + 1)).replace('<img ', '<img style="object-position:%s" ' % crops[i % 3], 1)
                  + '<span class="vl" style="background:%s"></span>' % rgba(c['G'], va)) if bl else '') + (pic(sc, 'sc', 'panel-%d:screen' % (i + 1), alt=sc.get('alt')) if sc else '')
        frame = '<div class="pf%s zi" data-g><div class="par" data-par=".06">%s</div></div>' % ('' if bl else ' pf-0', inner)
        price = ' '.join(str(v) for v in (x.get('price'), x.get('per')) if v)
        desc = ''.join(['<span class="pr" data-lines>%s</span>' % words(price) if price else '', '<span data-lines>%s</span>' % words(x['line']) if x.get('line') else ''])
        rows = [r for r in (x.get('rows') or []) if r]
        ul = '<ul class="frs" data-g>%s</ul>' % ''.join('<li class="fr rv" style="--dl:%.2fs"><p data-words>%s</p></li>' % (j * .17, words(r)) for j, r in enumerate(rows)) if rows else ''
        out.append('<article class="pp">%s<div class="pi" data-g><h2 class="rv" style="--y:12px;--d:.5s">%s</h2>%s</div>%s</article>'
                   % (frame, e(x['name']), '<p class="pd">%s</p>' % desc if desc else '', ul))
    ctas = [x for x in items if (x.get('cta') or {}).get('t')]
    lead = next((x for x in ctas if x.get('marked')), ctas[0] if ctas else None)
    cta = '<div class="pcta rv" data-g style="--y:8px;--d:.45s">%s</div>' % link(lead['cta'], 'bt bt-2') if lead else ''
    note = '<p class="pn" data-g data-lines>%s</p>' % words(pl['note']) if pl.get('note') else ''
    return '<section class="prs"><div class="pc"><div class="pg">%s</div>%s%s</div></section>' % (''.join(out), cta, note)


def s_steps(d, c):
    st = d.get('steps') or {}
    items = [x for x in (st.get('items') or []) if x.get('title') or x.get('k')]
    if not items and not st.get('title'):
        return ''
    h = d.get('hero') or {}
    acts = ''
    if (h.get('primary') or {}).get('t'):
        acts += link(h['primary'], 'bt')
    if (h.get('secondary') or {}).get('t'):
        acts += link(h['secondary'], 'tl')
    intro = '<div class="pc sin">%s%s%s</div>' % (
        '<h2 class="ty hs" data-g aria-label="%s">%s</h2>' % (e(st['title']), typed(st['title'])) if st.get('title') else '',
        '<p class="ld" data-g data-lines>%s</p>' % words(st['text']) if st.get('text') else '',
        '<div class="sa">%s</div>' % acts if acts else '')
    fo = ''
    n = len(items)
    for i, x in enumerate(items):
        col = c['folders'][min(i, 2)] if i < 3 else c['folders'][2]
        fo += ('<article class="fo%s%s" style="--fc:%s;--z:%d"><span class="fb"></span><div class="fh"><div class="ft"><span class="fs">%s</span>'
               '<h3><span class="fn">%02d</span><span>%s</span></h3><span class="fs fs-r">%s</span></div></div>%s</article>'
               % (' fo-r' if i % 2 else '', ' fo-l' if i == n - 1 else '', col, i + 1, SHOULDER, i + 1, e(x.get('title') or x.get('k')), SHOULDER,
                  '<p class="fd">%s</p>' % e(x.get('text')) if x.get('text') else '<p class="fd"></p>'))
    stack = '<div class="fst" data-folders style="--fn:%d">%s</div>' % (n, fo) if items else ''
    return '<section class="stp">%s%s</section>' % (intro, stack)


SHOULDER = ('<svg viewBox="0 0 96 72" preserveAspectRatio="none" aria-hidden="true"><path class="sf" d="M0 72C48 72 48 0 96 0V72Z"/>'
            '<path class="se" d="M0 72C48 72 48 0 96 0"/></svg>')
PLUS = '<svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true"><path d="M5 12h14"/><path class="pv" d="M12 5v14"/></svg>'


def s_banner(d, c):
    st, ft = d.get('statement') or {}, d.get('features') or {}
    title = st.get('title') or ft.get('title')
    if not title:
        return ''
    m = pick(made(d, 'land'), 5)
    veil, ink = over(m, c) if m else (c['D'], c['L'])
    a = max(.55, veil_for(m, veil, ink, 4.5)) if m else 0
    back = ''
    if m:
        back = ('<div class="par" data-par=".06">%s</div><span class="bsh" style="--v1:%s;--v2:%s;--v0:%s"></span>'
                % (pic(m, 'bd', 'banner:land'), rgba(veil, a), rgba(veil, min(.95, a + .1)), rgba(veil, 0)))
    return ('<section class="bn" style="--hi:%s;background:%s">%s<div class="pc bn-c"><h2 class="ty hs" data-g aria-label="%s">%s</h2></div></section>'
            % (ink, veil if m else c['D'], back, e(title), typed(title)))


def s_facts(d, c):
    st, ft = d.get('statement') or {}, d.get('features') or {}
    text = st.get('text') if st.get('title') else ft.get('text')
    items = [x for x in (ft.get('items') or []) if x.get('t')]
    m = pick(made(d, 'land'), 2)
    cta = d.get('cta') or {}
    if not (text or items):
        return ''
    long = any(len(x.get('d') or '') > 40 for x in items)
    rows = ''.join('<div class="fc rv" style="--dl:%.2fs"><dt>%s</dt>%s</div>' % (i * .18, e(x['t']), '<dd>%s</dd>' % e(x['d']) if x.get('d') else '')
                   for i, x in enumerate(items))
    return ('<section class="cd"><div class="cdc">%s%s%s%s</div></section>' % (
        '<p class="cdp" data-g data-lines>%s</p>' % words(text) if text else '',
        '<dl class="fcs%s" data-g>%s</dl>' % (' fcs-l' if long else '', rows) if rows else '',
        '<div class="cdf zi" data-g><div class="par" data-par=".055">%s</div></div>' % pic(m, 'bd', 'facts-picture:land') if m else '',
        '<div class="cdb">%s</div>' % link(cta, 'bt') if cta.get('t') else ''))


def s_faq(d, c):
    fq = d.get('faq') or {}
    items = [x for x in (fq.get('items') or []) if x.get('q') and x.get('a')]
    if not items:
        return ''
    rows = ''.join('<details class="fi rv" style="--dl:%.3fs"%s><summary><h3>%s</h3><span class="tg">%s</span></summary><div class="an"><div class="an-c"><p>%s</p></div></div></details>'
                   % (i * .066, ' open' if i == 0 else '', e(x['q']), PLUS, e(x['a'])) for i, x in enumerate(items))
    head = '<div class="fqi"><h2 class="hdsp" data-g data-lines>%s</h2></div>' % words(fq['title']) if fq.get('title') else '<div class="fqi"></div>'
    return '<section class="fq"><div class="pc fql">%s<div class="fqs" data-g data-faq>%s</div></div></section>' % (head, rows)


def s_close(d, c):
    cl = d.get('close') or {}
    if not cl.get('title'):
        return ''
    md = d.get('media') or {}
    v = md.get('video') or {}
    p = None
    if v.get('src'):
        media = ('<video class="cm" src="%s%s"%s width="%s" height="%s" muted loop playsinline autoplay preload="metadata" aria-label="%s" data-slot="close:film"></video>'
                 % (M, e(v['src']), ' poster="%s%s"' % (M, e(v['poster'])) if v.get('poster') else '', v.get('w') or '', v.get('h') or '', e(v.get('alt'))))
    else:
        for k in ('photos', 'phones', 'screens'):
            lst = [x for x in (md.get(k) or []) if x.get('src')]
            if lst:
                p = lst[0] if k != 'screens' else lst[-1]
                break
        media = pic(p, 'cm' + (' cm-p' if p.get('h', 0) > p.get('w', 0) else ''), 'close:' + (p.get('shape') or 'screen'), alt=p.get('alt')) if p else ''
    cta = cl.get('cta') or {}
    key = '<a class="key" href="%s"><span class="kc">%s</span></a>' % (e(cta.get('h') or '#'), e(cta['t'])) if cta.get('t') else ''
    return ('<section class="cl"><div class="pc cl-c"><h2 class="ty hdsp" data-g aria-label="%s">%s</h2>%s%s</div></section>'
            % (e(cl['title']), typed(cl['title']), '<div class="cmw%s">%s</div>' % ('' if media else ' cmw-0', media), key))


def s_foot(d, c):
    b, f = d.get('brand') or {}, d.get('foot') or {}
    wm = bool(b.get('logo') and b.get('logo_wordmark'))
    logo = '<img class="%s" src="%s%s" alt="%s" loading="lazy">' % ('wm' if wm else 'mk', M, e(b['logo']), e(b.get('name'))) if b.get('logo') else '<span class="fnm">%s</span>' % e(b.get('name'))
    seen, groups = set(), []
    for src in (d.get('nav') or [], d.get('links') or [], [d.get('signin') or {}, d.get('cta') or {}]):
        g = []
        for x in src:
            k = (x.get('t'), x.get('h'))
            if x.get('t') and k not in seen and (x.get('h'),) not in seen:
                seen.add(k)
                seen.add((x.get('h'),))
                g.append(x)
        if g:
            groups.append(g)
    cols = ''.join('<ul class="fg" data-g>%s</ul>' % ''.join('<li class="rv" style="--y:14px;--d:.28s;--dl:%.2fs">%s</li>' % (j * .117, ulink(x, 'fk')) for j, x in enumerate(g)) for g in groups)
    m = pick(made(d, 'land'), 1)
    veil, ink = over(m, c) if m else (c['A'], c['onA'])
    legal = [x for x in (f.get('links') or []) if x.get('t')]
    low = ''
    if f.get('text') or legal or m:
        back = ('<div class="fpw" data-foot><div class="fpl">%s</div></div><span class="fsh" style="--v0:%s;--v1:%s;--v2:%s"></span>'
                % (pic(m, 'bd', 'foot:land'), rgba(veil, 0), rgba(veil, .7), rgba(veil, .94))) if m else ''
        low = ('<div class="fbt%s" style="--hi:%s">%s<div class="pc flg">%s%s</div></div>'
               % ('' if m else ' fbt-0', ink, back, '<p>%s</p>' % e(f['text']) if f.get('text') else '<span></span>',
                  '<ul>%s</ul>' % ''.join('<li>%s</li>' % ulink(x, 'fk2') for x in legal) if legal else ''))
    return ('<footer class="ftr"><div class="pc ftt"><div class="fbr"><a class="fhm" href="%s">%s</a>%s</div><nav class="fnv" aria-label="%s">%s</nav></div>%s</footer>'
            % (e(b.get('home') or '#'), logo, '<p>%s</p>' % e(f['legal']) if f.get('legal') else '', e(b.get('name')), cols, low))


CSS = r'''
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
@media (prefers-reduced-motion:no-preference){html{scroll-behavior:smooth}}
html{background:__D__;color:__I__;font-family:"__FONT__",Arial,sans-serif;font-synthesis:none;-webkit-font-smoothing:antialiased;-webkit-text-size-adjust:100%;scroll-padding-top:calc(var(--hh) + 1px)}
:root{--gt:__GT__;--sp:__SP__;--spc:__SPC__;--hh:__HH__;--body:__BODY__;--lead:__LEAD__;--title:__TITLE__;--sect:__SECT__;--disp:__DISP__;--eo:cubic-bezier(.215,.61,.355,1);--bz:cubic-bezier(.23,1,.32,1)}
body{background:__G__;color:__I__;font-size:16px;line-height:1.5;overflow-x:clip}
img,video{display:block;max-width:100%}a{color:inherit;text-decoration:none}ul{list-style:none}h1,h2,h3{font-weight:700}
.pc{width:min(calc(100% - var(--gt)*2),1280px);margin-inline:auto}
:focus-visible{outline:2px solid __At__;outline-offset:4px;border-radius:4px}
.hd :focus-visible,.hero :focus-visible,.bn :focus-visible{outline-color:__L__}.fst :focus-visible,.cl :focus-visible,.ftr :focus-visible{outline-color:__onA__}.fbt :focus-visible{outline-color:var(--hi)}
/* buttons: 52 high, 4 radius; lift 3px, grow 3.5% and drop a hard 5px shadow on hover; sink 2px on press */
.bt{display:inline-flex;align-items:center;justify-content:center;min-height:52px;padding:8px 28px;border-radius:4px;background:__A__;color:__onA__;font-weight:700;font-size:16px;line-height:1.25;text-align:center;transition:background-color .2s ease-out,translate .22s var(--bz),scale .22s var(--bz),box-shadow .22s ease-out}
.bt-s{min-height:44px;padding:6px 20px;font-size:14px;white-space:nowrap}.bt-2{background:__LINE__;color:__I__}
.bt:active{transition-duration:.1s;translate:0 2px;scale:.97;box-shadow:0 0 rgba(0,0,0,0)}
@media (hover:hover) and (pointer:fine){.bt:hover{translate:0 -3px;scale:1.035;box-shadow:0 5px 0 rgba(0,0,0,.24);background:__Ah__}.bt-2:hover{background:__SECH__}.bt:active{translate:0 2px;scale:.97;box-shadow:0 0 rgba(0,0,0,0)}}
/* links with a 1px line that grows from the left in .24s */
.ul span{position:relative}.ul span::after{content:"";position:absolute;left:0;right:0;bottom:-.15em;height:1px;background:currentColor;transform:scaleX(0);transform-origin:0 50%}
.ul:focus-visible span::after{transform:scaleX(1)}
@media (hover:hover) and (pointer:fine){.ul span::after{transition:transform .24s var(--bz)}.ul:hover span::after{transform:scaleX(1)}}
/* bar */
.hd{position:sticky;top:0;z-index:40;background:__D__;color:__L__;border-bottom:1px solid __HDL__}
.hd-in{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:center;gap:24px;min-height:var(--hh)}
.br{display:inline-flex;align-items:center;gap:10px;min-height:44px;min-width:0;font-weight:700;font-size:__BRS__;line-height:1;justify-self:start}
.br img{flex:none}.br img.mk{height:26px;width:auto;border-radius:5px}.br img.wm{width:auto;height:auto;max-height:22px;max-width:220px;__WMF__}
/* the mark is never squeezed (it is the client's own drawing, in its own proportion); a long call wraps beside it */
@media (max-width:1023px){.hd-in{grid-template-columns:minmax(0,max-content) minmax(min-content,1fr)}.hd-l .bt-s{white-space:normal}}
@media (max-width:479px){.hd-l{gap:14px}.hd-l .bt-s{padding-inline:12px}.hd-l .br img.wm{max-height:18px;max-width:150px}}
.nv{display:none;align-items:center;gap:32px}.nl{display:inline-flex;align-items:center;min-height:44px;color:__NAVC__;white-space:nowrap}
@media (hover:hover){.nl:hover{color:__L__}}
.hc{justify-self:end}
@media (min-width:1024px){.hd-in{grid-template-columns:minmax(0,1fr) auto minmax(0,1fr)}.nv{display:flex}}
/* opening: a 16:9 picture, the title laid over it at the film's own scale */
.hero{position:relative;isolation:isolate;aspect-ratio:16/9;background:__D__;color:var(--hi);display:flex;align-items:center;justify-content:center;overflow:hidden;text-align:center}
.bd{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center}
.hero .bd,.hero .vl{z-index:-1}.vl{position:absolute;inset:0}
.hero-t{width:86vw;padding-top:6.2vw}
.hero h1{font-size:var(--ts);line-height:1.09;letter-spacing:-.02em;text-wrap:balance}
.hw{display:inline-block;overflow:hidden;vertical-align:top;padding-bottom:.12em;margin-bottom:-.12em}.hw>span{display:inline-block}
.hero-s{font-size:var(--ss);line-height:1.3;margin-top:1.9vw;text-wrap:balance}
/* figures */
.mts{padding-block:var(--sp)}
.mtg{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:48px 24px}
.mt{display:flex;flex-direction:column;align-items:center;gap:__MGAP__;text-align:center;min-width:0}
.mf{order:1;display:flex;align-items:center;justify-content:center;width:100%;height:__MFH__}
.mv{display:inline-block;font-weight:700;color:__AtL__;font-size:__MVS__;line-height:1;font-variant-numeric:lining-nums tabular-nums;white-space:nowrap}
.ml{order:2;font-weight:700;font-size:__MLS__;line-height:1.5;max-width:100%}
@media (min-width:1024px){.mtg{grid-template-columns:repeat(var(--n),minmax(0,1fr));gap:48px 32px}}
/* product panels */
.prs{padding-bottom:var(--sp)}
.pg{display:grid;grid-template-columns:minmax(0,1fr);gap:64px 32px}
.pp{display:grid;gap:__PPG__;align-content:start;min-width:0}
.pf{position:relative;overflow:hidden;aspect-ratio:624/349;background:__G__}.pf-0{background:__LINE__}
.par{position:absolute;left:0;right:0;top:-6%;height:112%;will-change:transform}
.sc{position:absolute;inset:0;margin:auto;width:auto;height:auto;max-width:78%;max-height:70%;border-radius:4px}
.pi h2{font-size:var(--title);line-height:1.15;color:__MUTED__}
.pd{margin-top:12px;font-size:var(--body);line-height:1.6;color:__MUTED__}.pd>span{display:block}.pd .pr{color:__I__;font-weight:700}
.frs{display:grid;gap:12px;grid-auto-rows:1fr;isolation:isolate}
.fr{display:flex;align-items:center;min-height:80px;padding:20px;border:1px solid __LINE__;background:__G__}
.fr p{font-weight:700;line-height:1.5}
.pcta{display:flex;justify-content:center;margin-top:var(--spc)}
.pn{margin:24px auto 0;max-width:75ch;text-align:center;font-size:14px;line-height:1.5;color:__MUTED__}
@media (min-width:768px){.pg{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (hover:hover) and (pointer:fine) and (prefers-reduced-motion:no-preference){.fr{transition:scale .24s ease-out,filter .24s ease-out;filter:opacity(1)}.frs:has(>.fr:hover)>.fr:not(:hover){filter:opacity(.45);scale:.975}.frs>.fr:hover{scale:1.025}}
/* typed heading, lede, actions */
.sin{padding-bottom:48px}
.hs{font-size:var(--sect);line-height:1.08}.hdsp{font-size:var(--disp);line-height:1.05}
.ty{position:relative}.ty-t{display:block}.tw{display:inline-block;white-space:nowrap}
.cur{display:none;position:absolute;left:0;top:0;width:.52em;height:.86em;background:currentColor;pointer-events:none}
.sin .hs{margin-bottom:24px;max-width:22em}
.ld{font-size:var(--lead);line-height:1.5;color:__MUTED__;max-width:832px}
.sa{display:flex;flex-wrap:wrap;align-items:center;gap:16px 24px;margin-top:24px}
.tl{color:__At__;text-decoration:underline;text-underline-offset:.2em;min-height:44px;display:inline-flex;align-items:center}
/* folder tabs */
.fst{--cv:56px;--sprd:24px;display:block;isolation:isolate;overflow:clip;color:__onA__;padding-bottom:calc(var(--sprd)*(var(--fn) - 1))}
.fo{position:relative;z-index:var(--z);display:grid;grid-template-columns:var(--gt) minmax(0,1fr) var(--gt);will-change:transform}
.fb{position:absolute;z-index:-1;left:0;right:0;top:calc(var(--th) + 16px);height:calc(100% + 400px);background:var(--fc)}
.fo-l .fb{height:calc(100% - var(--th) - 16px + var(--sprd)*(var(--fn) - 1))}
.fst{--th:64px}
.fh{grid-column:1/-1;position:relative;padding-top:16px;display:grid;grid-template-columns:subgrid}
.fh::before{content:"";position:absolute;left:0;right:0;bottom:0;height:1px;background:__EDGE__}
.ft{grid-column:1/-1;justify-self:start;position:relative;display:grid;grid-template-columns:var(--cv) minmax(0,auto) var(--cv);min-height:var(--th);max-width:100%}
.fs{position:relative}.fs svg{position:absolute;left:0;top:0;width:100%;height:100%;overflow:visible}.fs-r{transform:scaleX(-1)}
.sf{fill:var(--fc)}.se{fill:none;stroke:__EDGE__;stroke-width:1px;vector-effect:non-scaling-stroke}
.fo h3{display:block;align-content:center;padding:8px 4px;background:var(--fc);border-top:1px solid __EDGE__;font-size:__FLS__;line-height:1.3}
.fn{margin-right:8px;font-variant-numeric:tabular-nums}
.fd{grid-column:2;display:flex;align-items:center;font-size:var(--body);line-height:1.6;padding:28px 0 44px calc(var(--cv) + 4px - var(--gt));overflow-wrap:anywhere}
.fo-l .fd{padding-bottom:64px}
@media (min-width:1024px){.fst{--cv:96px;--sprd:48px;--th:72px}
.fo{grid-template-columns:var(--gt) minmax(0,1fr) minmax(0,1fr) var(--gt)}
.fo+.fo{margin-top:-88px}
.ft{grid-column:2/-1}.fo-r .ft{grid-column:3/-1}
.fo h3{display:flex;align-items:center;gap:10px;padding:8px}.fn{margin-right:0}
.fd{grid-column:2;min-height:88px;padding:16px 16px 0 104px}.fo-r .fd{grid-column:3}.fo-l .fd{grid-column:2/4;padding-bottom:0}
.fo-l.fo-r .fd{grid-column:3}}
/* picture banner */
.bn{position:relative;isolation:isolate;overflow:hidden;display:flex;align-items:flex-end;min-height:__BNH__;color:var(--hi)}
.bn .par{z-index:-2}.bsh{position:absolute;inset:0;z-index:-1;background:linear-gradient(var(--v1) 20%,var(--v2))}
.bn-c{padding-block:48px 32px}
@media (max-width:767px){.bn{min-height:384px}}
@media (min-width:768px){.bsh{background:linear-gradient(90deg,var(--v1),var(--v0) 78%),linear-gradient(var(--v0) 40%,var(--v2))}}
/* fact list */
.cd{background:__TINT__;padding-block:var(--sp)}
.cdc{width:min(calc(100% - var(--gt)*2),1024px);margin-inline:auto}
.cdp{font-size:var(--body);line-height:1.6;color:__MUTED2__;max-width:75ch;margin-bottom:32px}
.fcs{display:grid;gap:8px;padding:8px;border-radius:8px;background:__G__}
.fc{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);align-items:center;gap:12px;min-height:72px;padding:16px;border:1px solid __LINE__;background:__G__;font-size:var(--body);line-height:1.6}
.fc dt{color:__MUTED__}.fc dd{font-weight:700;text-align:right}
.fcs-l .fc{grid-template-columns:minmax(0,1fr);gap:4px}.fcs-l dt{color:__I__;font-weight:700}.fcs-l dd{color:__MUTED__;font-weight:400;text-align:left}
.cdf{position:relative;overflow:hidden;aspect-ratio:1584/672;margin-top:var(--spc)}
.cdb{display:flex;justify-content:center;margin-top:32px}
@media (min-width:768px){.fc{gap:16px;padding:16px 24px}.fcs-l .fc{grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:16px}}
/* accordion */
.fq{padding-block:var(--sp)}
.fql{display:grid;grid-template-columns:minmax(0,1fr);gap:32px}
.fqs{border-top:1px solid __LINE__;min-width:0}
.fi{position:relative;border-bottom:1px solid __LINE__}
.fi summary{display:flex;justify-content:space-between;align-items:center;gap:24px;min-height:104px;padding-block:24px;cursor:pointer;list-style:none;-webkit-tap-highlight-color:transparent}
.fi summary::-webkit-details-marker{display:none}
.fi h3{font-size:var(--lead);line-height:1.4}
.tg{flex:0 0 44px;height:44px;display:grid;place-items:center;border:1px solid __LINE__;border-radius:4px;color:__At__;transition:background-color .18s ease-out,border-color .18s ease-out,color .18s ease-out}
.tg svg{stroke:currentColor;stroke-width:1.5;fill:none}.pv{transform-origin:12px 12px;transition:transform .18s ease-out}
.fi[open]:not([data-st="closing"]) summary{color:__At__}
.fi[open]:not([data-st="closing"]) .tg{background:__A__;border-color:__A__;color:__onA__}
.fi[open]:not([data-st="closing"]) .pv{transform:scaleY(0)}
@media (hover:hover){.fi summary:hover{color:__At__}.fi summary:hover .tg{border-color:__At__}}
.an{overflow:hidden}.an-c{padding:0 68px 28px 0;font-size:16px;line-height:1.6;color:__MUTED__}.an-c p{max-width:65ch;overflow-wrap:anywhere}
@media (min-width:1024px){.fql{grid-template-columns:minmax(0,1fr) minmax(0,2fr);gap:72px}}
@media (max-width:767px){.an-c{padding-right:0}}
/* close */
.cl{background:__A__;color:__onA__;padding-block:var(--sp) var(--spc)}
.cl-c{display:flex;flex-direction:column;align-items:center}
.cl h2{text-align:center;text-wrap:balance;max-width:1024px}
.cmw{margin-block:var(--spc) 24px;width:min(100%,544px);display:flex;justify-content:center}.cmw-0{margin-block:24px 0}
.cm{width:100%;height:auto;border-radius:4px}.cm-p{width:auto;height:__CMH__;max-width:none}
/* the closing key: sinks when pressed, no easing */
.key{display:inline-block;padding:5px 5px 17px;border-radius:10px;background:__RIM__;min-width:__KW__;max-width:100%;-webkit-tap-highlight-color:transparent;user-select:none}
.kc{display:flex;align-items:center;justify-content:center;min-height:__KH__;padding:8px 28px;border-radius:7px;background:__CAP__;color:__CAPINK__;font-weight:700;font-size:__KS__;line-height:1.2;text-align:center;box-shadow:inset 0 2px 0 rgba(255,255,255,.7),inset 0 -6px 0 rgba(0,0,0,.14),0 10px 0 __CAPSIDE__}
.key:active .kc{transform:translateY(9px);box-shadow:inset 0 2px 0 rgba(255,255,255,.7),inset 0 -3px 0 rgba(0,0,0,.14),0 1px 0 __CAPSIDE__}
.key:focus-visible{outline-offset:5px}
/* foot */
.ftr{background:__A__;color:__onA__}
.ftt{display:grid;gap:48px;padding-block:var(--spc) 48px}
.fhm{display:inline-flex;align-items:center;min-height:48px}.fhm img.mk{height:48px;width:auto;border-radius:9px}.fhm img.wm{width:auto;height:auto;max-height:30px;max-width:100%;__WMF2__}.fnm{font-weight:700;font-size:28px}
.fbr p{margin-top:24px;font-size:14px;line-height:1.5}
.fnv{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:40px 24px;align-content:start}
.fk{display:inline-flex;align-items:center;min-height:44px;font-weight:700;font-size:var(--body);line-height:1.6}
.fbt{position:relative;isolation:isolate;display:flex;align-items:flex-end;min-height:__FBH__;color:var(--hi)}.fbt-0{min-height:0}
.fpw{position:absolute;inset:0;z-index:-2;overflow:clip;-webkit-mask-image:linear-gradient(transparent,#000 38%);mask-image:linear-gradient(transparent,#000 38%)}
.fpl{position:absolute;inset:0;will-change:transform}.fpl .bd{object-position:50% 0}
.fsh{position:absolute;inset:0;z-index:-1;background:linear-gradient(var(--v0) 35%,var(--v1) 75%,var(--v2))}
.flg{display:flex;flex-direction:column;gap:12px;padding-block:32px;font-size:14px;line-height:1.5}
.flg p{max-width:78ch}.flg ul{display:flex;gap:24px}.fk2{display:inline-flex;align-items:center;min-height:44px}
@media (min-width:1024px){.ftt{grid-template-columns:304px minmax(0,1fr);gap:64px;padding-bottom:64px}.fnv{grid-template-columns:repeat(4,minmax(0,1fr))}
.flg{flex-direction:row;justify-content:space-between;align-items:flex-end;gap:48px}}
/* motion — every hidden state sits behind .js, which the script sets only after it has set itself up */
@media (prefers-reduced-motion:no-preference){
.hd{animation:bar .9s var(--bz) .15s both}@keyframes bar{from{transform:translateY(-100%)}}
.hw>span{animation:rise .5s var(--eo) calc(.3s + var(--l,0)*.17s) both}@keyframes rise{from{transform:translateY(112%)}}
.hero-s{animation:fade .35s ease-out 1.2s both}@keyframes fade{from{opacity:0}}
.js .rv{opacity:0;transform:translateY(var(--y,18px))}
.js .in .rv,.js .in.rv{opacity:1;transform:none;transition:opacity var(--d,.6s) var(--eo) var(--dl,0s),transform var(--d,.6s) var(--eo) var(--dl,0s)}
.js .fc.rv{transform:translateY(-12px) scale(1.04)}.js .in .fc.rv{transform:none}
.js .fi.rv{--d:.38s}
.js [data-lines] .w{display:inline-block;opacity:0;transform:translateY(12px)}
.js .in [data-lines] .w,.js .in[data-lines] .w{opacity:1;transform:none;transition:opacity .85s var(--eo) calc(var(--l,0)*.117s),transform .85s var(--eo) calc(var(--l,0)*.117s)}
.js [data-words] .w{opacity:0}
.js .in [data-words] .w{opacity:1;transition:opacity .18s ease-out calc(var(--dl,0s) + var(--k,0)*.065s)}
.js .mv{opacity:0}.js .in .mv{opacity:1;transition:opacity .65s var(--eo) calc(var(--c,0)*.3s)}
.js .zi .bd,.js .zi .sc{transform:scale(1.035)}.js .zi.in .bd,.js .zi.in .sc{transform:none;transition:transform 1s var(--eo)}
.js .ty .tc{opacity:0}.js .ty .tc.on{opacity:1}
.js .ty .cur.on{display:block;animation:blink .7s steps(1) infinite}@keyframes blink{50%{opacity:0}}
.an{transition:height .47s cubic-bezier(.65,0,.35,1),opacity .47s cubic-bezier(.65,0,.35,1)}
}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}.bt:hover,.bt:active{translate:none;scale:none}}
'''

JS = r'''
(function(){
var R=document.documentElement,rm=matchMedia('(prefers-reduced-motion: reduce)').matches;
function $(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s))}
if(rm)$('video').forEach(function(v){v.removeAttribute('autoplay');v.pause();v.controls=true});
/* accordion: one open at a time; the open one closes while the next opens */
$('[data-faq]').forEach(function(box){var items=$('details',box);
function shut(it){if(!it.open||it.dataset.st==='closing')return;var a=it.querySelector('.an');if(rm){it.open=false;return}
it.dataset.st='closing';a.style.height=a.offsetHeight+'px';a.offsetHeight;a.style.height='0px';a.style.opacity='0';
var done=function(){it.open=false;it.removeAttribute('data-st');a.style.height='';a.style.opacity='';a.removeEventListener('transitionend',end);clearTimeout(t)},end=function(ev){if(ev.propertyName==='height')done()},t=setTimeout(done,600);a.addEventListener('transitionend',end)}
function show(it){var a=it.querySelector('.an');it.open=true;if(rm)return;it.dataset.st='opening';a.style.height='0px';a.style.opacity='0';a.offsetHeight;a.style.height=a.scrollHeight+'px';a.style.opacity='1';
var done=function(){it.removeAttribute('data-st');a.style.height='';a.style.opacity='';a.removeEventListener('transitionend',end);clearTimeout(t)},end=function(ev){if(ev.propertyName==='height')done()},t=setTimeout(done,600);a.addEventListener('transitionend',end)}
items.forEach(function(it){it.querySelector('summary').addEventListener('click',function(ev){ev.preventDefault();if(it.dataset.st)return;
if(it.open){shut(it)}else{items.forEach(function(o){if(o!==it)shut(o)});show(it)}})})});
if(rm||!('IntersectionObserver' in window)||!window.requestAnimationFrame)return;
/* which line a word stands on: lines rise one after the other */
function lines(box,sel){var top=null,l=-1;$(sel,box).forEach(function(w){var t=w.offsetTop;if(top===null||Math.abs(t-top)>4){l++;top=t}w.style.setProperty('--l',l)})}
$('.hero h1').forEach(function(h){lines(h,'.hw')});$('.hw').forEach(function(w){w.firstChild.style.setProperty('--l',getComputedStyle(w).getPropertyValue('--l'))});
$('[data-lines]').forEach(function(b){lines(b,'.w')});
$('[data-words]').forEach(function(b){$('.w',b).forEach(function(w,k){w.style.setProperty('--k',k)})});
$('.mt').forEach(function(m,i){m.style.setProperty('--c',i%4)});
/* figures: digits run while the number fades in, settling from the left */
function run(el,delay){var txt=el.textContent,n=txt.length,t0=null,dur=900;function f(t){if(t0===null)t0=t+delay;var p=(t-t0)/dur;if(p<0){requestAnimationFrame(f);return}
if(p>=1){el.textContent=txt;return}var s='';for(var i=0;i<n;i++){var ch=txt.charAt(i);s+=(/[0-9]/.test(ch)&&i/n>p)?String(Math.floor(Math.random()*10)):ch}el.textContent=s;setTimeout(function(){requestAnimationFrame(f)},45)}requestAnimationFrame(f)}
/* typed headings: the block cursor shows, the characters come one each 60 ms, the cursor stays a moment and goes */
function type(h){var cs=$('.tc',h),cur=h.querySelector('.cur'),i=0;if(!cur||!cs.length)return;
function place(){var hb=h.getBoundingClientRect(),c=cs[Math.min(i,cs.length-1)],b=c.getBoundingClientRect();cur.style.transform='translate('+((i<cs.length?b.left:b.right)-hb.left+(i<cs.length?0:2))+'px,'+(b.top-hb.top+b.height*.1)+'px)'}
place();cur.classList.add('on');setTimeout(function step(){if(i<cs.length){cs[i].classList.add('on');i++;place();setTimeout(step,60)}else{setTimeout(function(){cur.classList.remove('on')},380)}},230)}
var io=new IntersectionObserver(function(es){es.forEach(function(en){if(!en.isIntersecting)return;var t=en.target;io.unobserve(t);t.classList.add('in');
if(t.classList.contains('ty'))type(t);$('.mv',t).forEach(function(v){run(v,(+getComputedStyle(v.closest('.mt')).getPropertyValue('--c')||0)*300)})})},{rootMargin:'0px 0px -10% 0px',threshold:.05});
$('[data-g]').forEach(function(g){io.observe(g)});
/* scroll-led movement, eased toward its target each frame: pictures +-6% of their frame, figures +-14px, folders close up, the foot picture settles */
var par=$('[data-par]').map(function(el){return{el:el,box:el.parentElement,k:+el.dataset.par,v:null}}),
    pp=$('[data-pp]').map(function(el){return{el:el,box:el.parentElement,px:+el.dataset.pp,v:null}}),
    st=$('[data-folders]').map(function(el){return{el:el,fo:$('.fo',el),v:null}}),
    ft=$('[data-foot]').map(function(el){return{el:el,l:el.firstElementChild,v:null}});
function cl(x){return x<0?0:x>1?1:x}
function ease(o,t){o.v=o.v===null?t:o.v+(t-o.v)*.14;if(Math.abs(o.v-t)<.02)o.v=t;return o.v}
function frame(){var vh=innerHeight;
par.forEach(function(o){var r=o.box.getBoundingClientRect();if(r.bottom<-200||r.top>vh+200)return;var p=cl((vh-r.top)/(vh+r.height));o.el.style.transform='translate3d(0,'+ease(o,(.5-p)*2*o.k*r.height).toFixed(2)+'px,0)'});
pp.forEach(function(o){var r=o.box.getBoundingClientRect();if(r.bottom<-200||r.top>vh+200)return;var p=cl((vh-r.top)/(vh+r.height));o.el.style.transform='translate3d(0,'+ease(o,(.5-p)*2*o.px).toFixed(2)+'px,0)'});
st.forEach(function(o){var r=o.el.getBoundingClientRect();if(r.bottom<-200||r.top>vh+300)return;var s=parseFloat(getComputedStyle(o.el).getPropertyValue('--sprd'))||24,p=ease(o,cl((vh-r.top)/(vh/2+r.height)));
o.fo.forEach(function(f,i){f.style.transform=i?'translate3d(0,'+(i*s*(1-p)).toFixed(2)+'px,0)':''})});
ft.forEach(function(o){var r=o.el.getBoundingClientRect();if(r.top>vh+200)return;var p=cl((vh-r.top)/r.height);o.l.style.transform='translate3d(0,'+ease(o,(1-p)*20).toFixed(2)+'px,0)'});
requestAnimationFrame(frame)}
requestAnimationFrame(frame);
R.classList.add('js');
})();
'''


def render(d: dict) -> str:
    c = colours(d.get('palette') or {})
    b = d.get('brand') or {}
    body = ''.join(f(d, c) for f in (s_hero, s_figures, s_products, s_steps, s_banner, s_facts, s_faq, s_close))
    wmf = 'filter:brightness(0) invert(1)' if lum(c['L']) > .5 else ''
    wmf2 = 'filter:brightness(0)' + (' invert(1)' if lum(c['onA']) > .5 else '')
    muted2 = mix(c['muted'], c['I'], .1)
    rep = {
        'FONT': FONT, 'G': c['G'], 'I': c['I'], 'A': c['A'], 'D': c['D'], 'L': c['L'], 'LINE': c['line'], 'TINT': c['tint'],
        'MUTED2': muted2, 'MUTED': c['muted'], 'At': c['At'], 'AtL': c['AtL'], 'onA': c['onA'], 'Ah': c['Ah'], 'SECH': c['sech'], 'EDGE': c['edge'],
        'NAVC': c['navc'], 'HDL': rgba(c['L'], .12), 'WMF2': wmf2, 'WMF': wmf, 'CAPSIDE': mix(c['cap'], '#000000', .32),
        'CAPINK': c['cap_ink'], 'CAP': c['cap'], 'RIM': c['rim'],
        'GT': fl(20, 80), 'SPC': fl(40, 71.2), 'SP': fl(64, 126.4), 'HH': fl(76, 88), 'BODY': fl(16.14, 18), 'LEAD': fl(18, 22),
        'TITLE': fl(24, 36), 'SECT': fl(32, 52.8), 'DISP': fl(40, 71.2), 'BRS': fl(20, 22), 'MGAP': fl(16, 20), 'MFH': fl(128, 144),
        'MVS': fl(32, 41.76), 'MLS': fl(14, 16), 'PPG': fl(24, 32), 'FLS': fl(18, 26.64), 'BNH': 'clamp(320px,21.15vw,512px)',
        'FBH': 'clamp(384px,34.43vw,661px)', 'CMH': fl(340, 529), 'KW': fl(192, 230), 'KH': fl(60, 72), 'KS': fl(18, 20),
    }
    css = CSS
    for k in sorted(rep, key=len, reverse=True):
        css = css.replace('__%s__' % k, str(rep[k]))
    h = d.get('hero') or {}
    title = ' — '.join(x for x in (b.get('name'), h.get('kicker') or h.get('title')) if x)
    desc = ' '.join(x for x in (h.get('text'), h.get('text2')) if x)
    return ('<!doctype html><html lang="%s"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>%s</title>%s<meta name="theme-color" content="%s">'
            '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=%s:wght@400;700&display=swap">'
            '<style>%s</style></head><body>%s<main>%s</main>%s<script>%s</script></body></html>'
            % (e(d.get('lang') or 'en'), e(title), '<meta name="description" content="%s">' % e(desc) if desc else '', c['D'],
               FONT.replace(' ', '+'), css, s_bar(d, c), body, s_foot(d, c), JS))
