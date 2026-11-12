"""glossar/render.py — one pure function: render(d) -> a complete page.

The build (section order, grid, measures, type, spacing, radii, motion, phone layout) was measured on the reference's
home page at 1440 and 390 on 2026-11-12 (see NOTES.md). Nothing of the reference's code, words, pictures, icons, logos
or typefaces is here. The client's data fills it; a section whose data is missing is left out whole. No model call, no
client logic.
"""
import html
import math
import re

FONTS = 'https://fonts.googleapis.com/css2?family=Inter:wght@400..700&display=swap'


# ───────────────────────── colour: the reference's light/dark/accent relations, applied to the client's palette
def _rgb(h):
    h = (h or '#000').strip().lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


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
    x, y = sorted((_lum(a), _lum(b)), reverse=True)
    return (x + .05) / (y + .05)


def _raise(ink, grounds, t, floor=4.6):
    """ink at share t over each ground, raised until it reads at `floor` on all of them"""
    while t < 1 and any(_con(_mix(ink, g, t), g) < floor for g in grounds):
        t += .02
    return min(t, 1)


def _on(c, ground, ink):
    """a fill and the text that stands on it: the better of ground/ink, the fill pushed away until 4.5:1"""
    tx = max((ground, ink), key=lambda x: _con(x, c))
    far = '#000000' if _lum(tx) > _lum(c) else '#ffffff'
    n = 0
    while _con(tx, c) < 4.6 and n < 14:
        c = _mix(far, c, .08)
        n += 1
    return c, tx


def _theme(ground, ink, accent, extra):
    """Reference relations: page on its ground; panels 4 % of ink; muted text 57 % of ink; bar and word cards in full
    ink with the ground as their text; the buy bar and the chip in the accent; small tags 12 % of ink."""
    panel = _mix(ink, ground, .04)
    card = _mix(ground, ink, .2)           # top of the word card's gradient (reference #333 over #000)
    acc, acctx = _on(accent, ground, ink)
    t = .6
    while t < 1 and min(_con(_mix(ground, ink, t), card), _con(_mix(ground, ink, t), ink)) < 4.8:
        t += .02
    cm = _mix(ground, ink, min(t, 1))
    v = {
        'bg': ground, 'ink': ink, 'panel': panel, 'acc': acc, 'acctx': acctx,
        'mute': _mix(ink, panel, _raise(ink, (ground, panel), .57)),
        'dim': _mix(ink, ground, .18), 'hair': _mix(ink, ground, .1), 'tag': _mix(ink, panel, .1),
        'tagtx': _mix(ink, panel, _raise(ink, (_mix(ink, panel, .1),), .8)),
        'plus': _mix(ink, ground, .055), 'hov': _mix(ink, ground, .09),
        'grad': _mix(ink, ground, _raise(ink, (ground,), .6)),
        'card': card, 'cardmute': cm,
        'menu': _mix(ground, ink, .1), 'menuline': _mix(ground, ink, .16),
        'inka': '%d,%d,%d' % _rgb(ink), 'bga': '%d,%d,%d' % _rgb(ground),
    }
    return ';'.join('--%s:%s' % kv for kv in v.items())


def _hues(ground, ink, accent, extra):
    """the fills of the coloured pills: the accent and the palette's other colours that stand off the page"""
    out = []
    for c in dict.fromkeys([accent] + list(extra or [])):
        try:
            if _con(c, ground) < 1.35:
                continue
            out.append(_on(c, ground, ink))
        except (ValueError, IndexError):
            continue
    return out or [(ink, ground)]


# ───────────────────────── small helpers
def e(s):
    return html.escape(str(s if s is not None else ''), quote=True)


def m(p):
    """media paths in the data are relative to templates/; a page in <slug>/out/ reaches them two levels up"""
    p = str(p or '')
    return p if re.match(r'^(https?:)?//|^data:', p) else '../../' + p


def img(o, cls='', lazy=True, alt=None):
    wh = ' width="%s" height="%s"' % (e(o['w']), e(o['h'])) if o.get('w') and o.get('h') else ''
    return '<img%s src="%s" alt="%s"%s%s decoding="async">' % (
        ' class="%s"' % cls if cls else '', e(m(o.get('src'))), e(o.get('alt', '') if alt is None else alt), wh, ' loading="lazy"' if lazy else '')


def _made(d, kind, i):
    xs = ((d.get('media') or {}).get('made') or {}).get(kind) or []
    xs = [x for x in (xs if isinstance(xs, list) else [xs]) if isinstance(x, dict) and x.get('src')]
    return xs[i % len(xs)] if xs else None


def words(s, cls='w'):
    return ' '.join('<span class="%s">%s</span>' % (cls, e(w)) for w in str(s or '').split())


def rise(s, step=.06, start=0.0):
    """each word in a mask of its own, rising into place one after the other"""
    return ' '.join('<span class="m"><span style="--d:%.2fs">%s</span></span>' % (start + i * step, e(w)) for i, w in enumerate(str(s or '').split()))


ARROW = ('<svg viewBox="0 0 16 14" width="15" height="13" aria-hidden="true"><path d="M1 7h13M8.5 1.5 14 7l-5.5 5.5" fill="none" '
         'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def logo(d, cls):
    b = d.get('brand') or {}
    if not b.get('logo'):
        return ''
    wm = bool(b.get('logo_wordmark'))
    return '<img class="%s%s" src="%s" alt="%s" decoding="async">' % (cls, ' wm' if wm else '', e(m(b['logo'])), e(b.get('name', '')) if wm else '')


def pill(link, chip='', chip_link=None, cls=''):
    """the reference's one button: a full-ink pill, 48 high, with an accent chip set inside its right end"""
    if not link or not link.get('t'):
        return ''
    if chip_link and chip_link.get('t'):
        return '<div class="pill two %s"><a class="pl" href="%s">%s</a><a class="chip" href="%s">%s</a></div>' % (
            cls, e(link.get('h') or '#'), e(link['t']), e(chip_link.get('h') or '#'), e(chip_link['t']))
    return '<a class="pill %s%s" href="%s"><span class="pl">%s</span>%s</a>' % (
        cls, ' has' if chip else ' bare', e(link.get('h') or '#'), e(link['t']), '<span class="chip">%s</span>' % e(chip) if chip else '')


# ───────────────────────── sections (reference order)
def s_top(d):
    b = d.get('brand') or {}
    cta = d.get('cta') or {}
    links = [n for n in (d.get('nav') or []) + [d.get('signin') or {}] if n.get('t')]
    menu = btn = ''
    if links:
        btn = '<button class="mb" type="button" aria-expanded="false" aria-controls="menu" aria-label="Menu"><i></i><i></i></button>'
        menu = '<div class="menu-w" id="menu"><div><div class="menu">%s</div></div></div>' % ''.join(
            '<a href="%s" style="--i:%d">%s</a>' % (e(n.get('h') or '#'), i, e(n['t'])) for i, n in enumerate(links))
    buy = ''
    if cta.get('t'):
        buy = '<a class="buy" href="%s"><span>%s</span><span class="tile">%s%s</span></a>' % (e(cta.get('h') or '#'), e(cta['t']), ARROW, ARROW)
    return ('<div class="navres" aria-hidden="true"></div><div class="scrim" aria-hidden="true"></div>'
            '<header class="top"><nav class="bar" aria-label="Primary"><div class="bar-h"><a class="brand" href="%s">%s</a>%s</div>%s</nav>%s</header>') % (
        e(b.get('home') or '#'), e(b.get('name', '')), btn, menu, buy)


def s_open(d):
    h = d.get('hero') or {}
    if not h.get('title'):
        return ''
    n = len(h['title'].split())
    lines = [x for x in (h.get('text'), h.get('text2')) if x]
    lede = '<p class="lede">%s</p>' % ' '.join('<span class="m"><span style="--d:%.2fs">%s</span></span>' % (.22 + n * .06 + i * .1, e(x)) for i, x in enumerate(lines)) if lines else ''
    return '<section class="open">%s<div class="open-t"><h1>%s</h1>%s</div>%s</section>' % (
        logo(d, 'icon'), rise(h['title'], .06, .12), lede, pill(h.get('primary'), chip_link=h.get('secondary'), cls='grow'))


def s_stage(d):
    st = d.get('steps') or {}
    items = [x for x in st.get('items') or [] if x.get('text') or x.get('title')]
    if not items:
        return ''
    md = d.get('media') or {}
    known = {x.get('src'): x for k in ('phones', 'photos', 'screens') for x in md.get(k) or []}
    arts = ''
    for i, x in enumerate(items):
        main = x.get('text') or x.get('title')
        side = [v for v in ((x.get('k'), x.get('title')) if x.get('text') else (x.get('k'),)) if v]
        fig = ''
        if x.get('img'):
            o = dict(known.get(x['img']) or {}, src=x['img'])
            fig = '<figure class="st-f %s">%s</figure>' % (e(x.get('shape') or ''), img(o, '', i > 0))
        arts += '<article class="st" data-rv data-i="%d"><p class="st-t">%s</p>%s%s</article>' % (
            i, words(main), fig, '<p class="st-r">%s</p>' % '<br>'.join(words(v) for v in side) if side else '')
    return ('<section class="stage" id="stage" style="--n:%d"><div class="st-pin"><div class="st-card"><i class="rule" aria-hidden="true"></i>%s</div></div></section>') % (len(items), arts)


def s_tones(d, hues):
    s = d.get('statement') or {}
    trust = [x for x in d.get('trust') or [] if x]
    if not s.get('title') and not trust:
        return ''
    head = ''
    if s.get('title'):
        head = '<h2 class="h2 two-tone"><span class="m"><span style="--d:0s">%s</span></span>%s</h2>' % (
            e(s['title']), '<span class="m"><span class="mu" style="--d:.12s">%s</span></span>' % e(s['text']) if s.get('text') else '')
    pills = ''
    if trust:
        pills = '<ul class="tones">%s</ul>' % ''.join(
            '<li style="background:%s;color:%s;--d:%.2fs">%s</li>' % (hues[i % len(hues)][0], hues[i % len(hues)][1], .4 + i * .04, e(x)) for i, x in enumerate(trust))
    return '<section class="lev" data-rv><div class="lev-in">%s%s</div></section>' % (head, pills)


def s_show(d):
    f = d.get('features') or {}
    items = [x for x in f.get('items') or [] if x.get('t')]
    md = d.get('media') or {}
    screens = [x for x in md.get('screens') or [] if x.get('src')]
    if not items and not screens:
        return ''
    used = {x.get('img') for x in (d.get('steps') or {}).get('items') or []}
    side = next((x for x in (md.get('phones') or []) + (md.get('photos') or []) if x.get('src') and x['src'] not in used and (x.get('h') or 0) > (x.get('w') or 1)), None)
    if not side and len(screens) > 1:
        side = screens[1]
    head = '<h2 class="h2 gr" data-rv>%s</h2>' % rise(f['title'], .07) if f.get('title') else ''
    stagegrid = ''
    if screens:
        pic = _made(d, 'land', 1)
        back = ('<img class="bk" data-slot="showcase-backdrop" data-par="60" src="%s" alt="" width="%s" height="%s" loading="lazy" decoding="async">' % (
            e(m(pic['src'])), e(pic.get('w', '')), e(pic.get('h', ''))) if pic else '')
        stagegrid = '<div class="show-g"><div class="show-p%s"%s>%s<div class="show-s">%s</div></div>%s</div>' % (
            ' pic' if pic else '', '' if pic else ' data-slot="showcase-backdrop"', back, img(screens[0]),
            '<div class="show-2" data-par="58">%s</div>' % img(side) if side else '')
    rows = ''.join('<div class="pair"><h3>%s</h3>%s</div>' % (e(x['t']), '<p>%s</p>' % e(x['d']) if x.get('d') else '') for x in items)
    return '<section class="show">%s%s%s</section>' % (head, stagegrid, '<div class="pairs">%s</div>' % rows if rows else '')


def s_cards(d):
    figs = [x for x in d.get('figures') or [] if isinstance(x, dict) and x.get('v')]
    if not figs:
        return ''
    h = d.get('hero') or {}
    head = ''
    if h.get('kicker') or h.get('note'):
        a, b = (h.get('kicker'), h.get('note')) if h.get('kicker') else (h.get('note'), None)
        head = '<h2 class="h2 c" data-rv="up">%s%s</h2>' % (e(a), '<br><span class="mu">%s</span>' % e(b) if b else '')
    n = len(figs)
    mid = {(n - 1) // 2, n // 2}
    cards = ''.join('<article class="wc%s" style="--k:%s;--d:%.2fs"><h3>%s</h3>%s</article>' % (
        ' mid' if i in mid else '', ('%.1f' % (i - (n - 1) / 2)), i * .08, e(x['v']), '<p>%s</p>' % e(x['l']) if x.get('l') else '') for i, x in enumerate(figs))
    return '<section class="panel comp">%s<div class="fan" data-rv style="--n:%d">%s</div></section>' % (head, n, cards)


def s_plans(d):
    p = d.get('plans') or {}
    items = [x for x in p.get('items') or [] if x.get('name')]
    if not items:
        return ''
    head = ''
    if p.get('title'):
        head = '<h2 class="h2 c">%s%s</h2>' % (e(p['title']), '<br><span class="mu">%s</span>' % e(p['text']) if p.get('text') else '')
    cols = ''
    for x in items:
        rows = ''.join('<li>%s</li>' % e(r) for r in x.get('rows') or [])
        cta = x.get('cta') or {}
        btn = pill(cta, chip=x.get('price') or '', cls='' if x.get('marked') else 'plain') if cta.get('t') else (
            '<p class="price">%s</p>' % e(x['price']) if x.get('price') else '')
        cols += '<div class="plan"><h3>%s</h3>%s%s<div class="plan-b">%s%s</div></div>' % (
            e(x['name']), '<p class="ln">%s</p>' % e(x['line']) if x.get('line') else '', '<ul>%s</ul>' % rows if rows else '',
            btn, '<p class="per">%s</p>' % e(x['per']) if x.get('per') else '')
    return '<section class="panel plans">%s<div class="plan-g">%s</div>%s</section>' % (
        head, cols, '<p class="pnote">%s</p>' % e(p['note']) if p.get('note') else '')


def s_faq(d):
    f = d.get('faq') or {}
    items = [x for x in f.get('items') or [] if x.get('q')]
    if not items:
        return ''
    qs = ''.join(('<div class="qa"><h3><button type="button" aria-expanded="false" aria-controls="qa%d"><span>%s</span><i class="pm" aria-hidden="true"></i></button></h3>'
                  '<div class="qa-b" id="qa%d"><div><p>%s</p></div></div></div>') % (i, e(x['q']), i, e(x.get('a', ''))) for i, x in enumerate(items))
    return '<section class="panel faq">%s<div class="qas" style="--r:%d">%s</div></section>' % (
        '<h2 class="h2 c">%s</h2>' % e(f['title']) if f.get('title') else '', math.ceil(len(items) / 2), qs)


def s_close(d):
    c = d.get('close') or {}
    if not c.get('title'):
        return ''
    n = len(c['title'].split())
    return '<section class="end" data-rv>%s<div class="open-t"><h2 class="h2 gr">%s</h2>%s</div>%s</section>' % (
        logo(d, 'icon'), rise(c['title'], .04, .1),
        '<p class="lede"><span class="m"><span style="--d:%.2fs">%s</span></span></p>' % (.2 + n * .04, e(c['text'])) if c.get('text') else '',
        pill(c.get('cta'), cls='grow'))


def s_foot(d):
    b, f = d.get('brand') or {}, d.get('foot') or {}
    tags = [x for x in d.get('links') or [] if x.get('t')]
    small = [x for x in f.get('links') or [] if x.get('t')]
    row = lambda xs: '<div class="tags">%s</div>' % ''.join('<a href="%s">%s</a>' % (e(x.get('h') or '#'), e(x['t'])) for x in xs) if xs else ''
    pic = _made(d, 'land', 5)
    back = ''
    if pic:
        back = ('<div class="ft-bk" aria-hidden="true"><img data-slot="foot-backdrop" src="%s" alt="" width="%s" height="%s" loading="lazy" decoding="async"><i></i></div>' % (
            e(m(pic['src'])), e(pic.get('w', '')), e(pic.get('h', ''))))
    home = '<a class="ft-logo" href="%s">%s%s</a>' % (e(b.get('home') or '#'), logo(d, 'fl'), '' if b.get('logo') and b.get('logo_wordmark') else '<span>%s</span>' % e(b.get('name', '')))
    return '<footer class="ft%s">%s<div class="ft-card">%s%s%s%s</div></footer>' % (
        ' pic' if pic else '', back, home, '<div class="ft-tags">%s%s</div>' % (row(tags), row(small)) if tags or small else '',
        '<p class="ft-l">%s</p>' % e(f['legal']) if f.get('legal') else '', '<p class="ft-t">%s</p>' % e(f['text']) if f.get('text') else '')


CSS = r"""
*{box-sizing:border-box;margin:0;padding:0}html{background:var(--bg);-webkit-text-size-adjust:100%}
body{font:400 16px/1.5 var(--f);color:var(--ink);background:var(--bg);-webkit-font-smoothing:antialiased;overflow-x:clip}
a{color:inherit;text-decoration:none}img,video{display:block;max-width:100%;height:auto}ul{list-style:none}button{font:inherit;color:inherit;background:none;border:0;cursor:pointer;text-align:left}
:root{--f:'Inter',system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;--e:cubic-bezier(.16,1,.3,1);--x:cubic-bezier(.19,1,.22,1)}
:focus-visible{outline:2px solid var(--ink);outline-offset:3px;border-radius:6px}.top :focus-visible{outline-color:var(--bg)}.buy:focus-visible{outline-color:var(--ink)}
.h2{font:510 32px/1.2 var(--f);text-wrap:balance}.h2.c{text-align:center;max-width:680px;margin-inline:auto}.mu{color:var(--mute)}
.gr .m>span,.gr.h2>.m>span{background:linear-gradient(var(--ink),var(--grad));-webkit-background-clip:text;background-clip:text;color:transparent}
/* a word or a line behind a mask of its own, rising 110 % into place: .7s, cubic-bezier(.19,1,.22,1) */
.m{display:inline-block;overflow:hidden;vertical-align:top;padding:.08em 0}.m>span{display:inline-block}
/* THE BAR: fixed, 480 wide, centred, 14 from the top; full-ink strip 58 high, radius 12, the name in the middle; under it the accent strip 54 high. It leaves when the page goes down and returns when it comes back up. */
.navres{height:132px}.top{position:fixed;z-index:50;top:0;left:0;right:0;padding-top:14px;display:flex;flex-direction:column;align-items:center;gap:6px;pointer-events:none;transition:opacity .18s var(--e),transform .42s var(--e),visibility 0s}
.top>*{pointer-events:auto;width:min(480px,calc(100% - 24px))}.top.away{opacity:0;transform:translateY(-148px);visibility:hidden;transition:opacity .18s var(--e),transform .42s var(--e),visibility 0s .42s}
.bar{background:var(--ink);color:var(--bg);border-radius:12px;border:1px solid rgba(var(--bga),.1);overflow:hidden;transition:border-radius .58s var(--e)}
.bar-h{position:relative;height:56px;display:flex;align-items:center;justify-content:center}.brand{font:500 22px/1 var(--f);padding:6px 10px;max-width:calc(100% - 120px);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.mb{position:absolute;right:11px;top:6px;width:44px;height:44px;display:grid;place-content:center;gap:5px}.mb i{display:block;width:28px;height:1.5px;background:currentColor;border-radius:2px;transition:transform .42s var(--e)}
.mopen .mb i:first-child{transform:translateY(3.25px)}.mopen .mb i:last-child{transform:translateY(-3.25px)}
.menu-w{display:grid;grid-template-rows:0fr;visibility:hidden;transition:grid-template-rows .58s var(--e),visibility 0s .58s}.menu-w>div{overflow:hidden;min-height:0}
.menu{max-height:calc(100vh - 170px);overflow-y:auto;margin:16px 9px 9px;padding:8px 8px 10px;border-radius:12px;background:var(--menu);border:1px solid rgba(var(--bga),.1);display:flex;flex-direction:column;opacity:0;transform:translateY(-8px) scale(.985);transition:opacity .28s var(--e),transform .58s var(--e)}
.menu a{display:flex;align-items:center;height:62px;padding:0 10px;border-radius:8px;font:460 22px/1 var(--f);transition:background-color .24s var(--e)}.menu a+a{box-shadow:0 -1px 0 var(--menuline);margin-top:12px;position:relative}.menu a+a::before{content:"";position:absolute;inset:-6px 0 auto}
.menu a:hover{background:rgba(var(--bga),.08)}
.mopen .bar{border-radius:18px}.mopen .menu-w{grid-template-rows:1fr;visibility:visible;transition-delay:0s}.mopen .menu{opacity:1;transform:none}
html:not(.js) .top{position:absolute}html:not(.js) .bar:focus-within .menu-w,html:not(.js) .bar:hover .menu-w{grid-template-rows:1fr;visibility:visible}html:not(.js) .bar:focus-within .menu,html:not(.js) .bar:hover .menu{opacity:1;transform:none}
.scrim{position:fixed;inset:0;z-index:40;background:rgba(0,0,0,.32);opacity:0;visibility:hidden;transition:opacity .38s var(--e),visibility 0s .38s}.scrim.on{opacity:1;visibility:visible;transition-delay:0s}
.buy{display:flex;align-items:center;justify-content:space-between;gap:12px;height:54px;padding:0 7px 0 22px;border-radius:12px;background:var(--acc);color:var(--acctx);border:1px solid rgba(var(--bga),.1);font:500 15px/1 var(--f);transition:box-shadow .2s ease-in-out}
.buy>span:first-child{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;line-height:1.3}.buy:hover{box-shadow:inset 0 0 0 999px rgba(0,0,0,.08)}
.tile{position:relative;flex:none;width:40px;height:40px;border-radius:7px;overflow:hidden;background:color-mix(in srgb,currentColor 18%,transparent);box-shadow:inset 0 0 0 1px color-mix(in srgb,currentColor 8%,transparent)}
.tile svg{position:absolute;left:50%;top:50%;margin:-6.5px 0 0 -7.5px;transition:transform .3s cubic-bezier(.5,.5,.3,1) .1s}.tile svg+svg{transform:translateX(-40px)}.buy:hover .tile svg{transform:translateX(40px)}.buy:hover .tile svg+svg{transform:none}
/* OPENING: 116 under the bar; mark 86 (radius 20); 28; display 40/48 weight 510; 17; text 17/25.5 muted; 28; the pill */
.open,.end{display:flex;flex-direction:column;align-items:center;gap:28px;text-align:center;padding:116px 16px 0}
.icon{width:auto;height:auto;max-width:min(300px,80%);max-height:86px}.icon.wm{width:auto;height:auto;max-height:34px;max-width:min(300px,80%);margin:26px 0}
.open-t{display:flex;flex-direction:column;align-items:center;gap:17px;max-width:809px}
h1{font:510 40px/1.2 var(--f);text-wrap:balance}.lede{font:480 17px/1.5 var(--f);color:var(--mute);display:flex;flex-direction:column;max-width:809px}.lede .m{padding:0}
/* the pill: 48 high, 6 inside, label 15 weight 510 at 22 from the left; the chip 36 high, 14 at the sides, in the accent */
.pill{display:inline-flex;align-items:center;gap:12px;min-height:48px;padding:6px 6px 6px 22px;border-radius:999px;background:var(--ink);color:var(--bg);font:510 15px/1.2 var(--f);letter-spacing:-.01em;max-width:100%;transition:box-shadow .2s cubic-bezier(.07,.3,.1,.9)}
.pill.bare{padding-right:22px}.pill.two{padding-left:0}.pill.two .pl{padding:9px 0 9px 22px}.pill .pl{min-width:0}
.pill:hover{box-shadow:inset 0 0 0 999px rgba(var(--bga),.13)}
.chip{display:inline-flex;align-items:center;min-height:36px;padding:4px 14px;border-radius:999px;background:var(--acc);color:var(--acctx);border:1px solid rgba(var(--bga),.1);white-space:nowrap;transition:box-shadow .2s cubic-bezier(.07,.3,.1,.9)}a.chip:hover{box-shadow:inset 0 0 0 999px rgba(0,0,0,.1)}
.pill.plain .chip{background:rgba(var(--bga),.16);color:var(--bg)}
/* load: mark .75s, words .7s one after another, text .72s, the pill opens from a 48 circle in .64s and its label follows */
@keyframes wordin{from{opacity:0;transform:translateY(110%)}to{opacity:1;transform:none}}
@keyframes iconin{from{opacity:0;transform:translateY(22px) scale(.7)}to{opacity:1;transform:none}}
@keyframes pillin{0%{opacity:0;clip-path:inset(0 calc(50% - 24px) round 999px);transform:translateY(18px) scale(.96)}18%{opacity:1}100%{opacity:1;clip-path:inset(0 0 round 999px);transform:none}}
@keyframes labin{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}
.open .icon{animation:iconin .75s var(--x) both}.open .m>span{animation:wordin .7s var(--x) var(--d,0s) both}
.open .grow{animation:pillin .64s cubic-bezier(.2,.9,.28,1) .62s both}.open .grow .pl,.open .grow .chip{animation:labin .34s cubic-bezier(.2,.9,.28,1) 1.1s both}
/* THE STAGE. Without script, with reduced motion and under 900 px it is the reference's phone build: one panel a step — statement, the screen whole, a muted remark. */
.stage{margin-top:136px;padding:0 12px}.st-card{display:flex;flex-direction:column;gap:20px;max-width:760px;margin:0 auto}.rule{display:none}
.st{background:var(--panel);border-radius:28px;padding:52px 26px;display:flex;flex-direction:column;align-items:center;gap:48px;text-align:center}
.st-t{font:510 21px/1.3 var(--f);max-width:23em}.st-r{font:510 20px/1.3 var(--f);letter-spacing:-.0075em;color:var(--mute)}
.st-f{line-height:0}.st-f img{width:auto;max-width:100%;max-height:655px;border-radius:12px}.st-f.phone img{border-radius:clamp(22px,9%,36px)}
/* pinned (script, 900 px and up): one screen held for 90vh a step; panel 24/23 from the edges, radius 40; statement 24/28.8 at the left behind a 2 x 86 rule that fills with the scroll; the screen in the middle at 84.4 % of the height; remark at the right. Words stand at 18 % and light one by one as the page moves. */
.stage.pin{height:calc(100vh + var(--n)*90vh);padding:0}.pin .st-pin{position:sticky;top:0;height:100vh;padding:24px 23px;overflow:hidden}
.pin .st-card{position:relative;display:block;height:100%;max-width:none;background:var(--panel);border-radius:40px;overflow:hidden}
.pin .rule{display:block;position:absolute;z-index:2;left:59px;top:50%;width:2px;height:86px;margin-top:-43px;border-radius:999px;background:linear-gradient(rgba(var(--inka),.92) var(--p,0%),rgba(var(--inka),.18) var(--p,0%))}
.pin .st{position:absolute;inset:0;background:none;border-radius:0;padding:0 59px;display:grid;grid-template-columns:minmax(0,374px) minmax(0,1fr) minmax(0,317px);gap:24px;align-items:center;text-align:left;pointer-events:none}
.pin .st-t{grid-column:1;padding-left:31px;font-size:24px;line-height:1.2;max-width:none;text-wrap:wrap;opacity:var(--o,0);transform:translateY(var(--y,36px))}
.pin .st-r{grid-column:3;font-size:24px;line-height:1.2;letter-spacing:0;color:var(--ink);opacity:var(--o,0);transform:translateY(calc(var(--y,36px)*.667))}
.pin .st-f{grid-column:2;justify-self:center;opacity:var(--fo,0)}.pin .st-f img{max-height:calc(84.4vh - 0px);max-width:min(100%,38vw)}
.pin .w{opacity:.18}.pin .w.on{opacity:1}
/* statement + pills: a square of 860 with the block in its middle; head 32/38.4, the first sentence in ink and the rest muted, 680 wide; pills 54 high, 12 apart */
.lev{min-height:860px;display:flex;align-items:center;justify-content:center;padding:96px 24px}.lev-in{width:min(680px,100%)}
.two-tone .m{display:block;padding:0}.two-tone .m>span{display:block}
.tones{display:flex;flex-wrap:wrap;gap:12px;margin:48px -5px 0}.tones li{display:flex;align-items:center;min-height:54px;padding:12px 30px 14px;border-radius:999px;border:1px solid rgba(var(--bga),.1);font:510 22px/1.18 var(--f)}
/* showcase: 80 at the sides; head 32; 41; a picture panel 816 x 621, radius 24, the screen whole on it; a second screen 340 wide at the right, both drifting with the scroll; then pairs on a 244 | 540 grid: 22/33 beside 20/30 muted */
.show{margin:48px 80px 0}.show-g{display:grid;grid-template-columns:minmax(0,816fr) minmax(0,432fr);gap:32px;align-items:center;margin-top:41px}
.show-p{position:relative;aspect-ratio:816/621;border-radius:24px;overflow:hidden;background:var(--panel);display:grid;place-items:center;isolation:isolate}
.bk{position:absolute;inset:0;z-index:-1;width:100%;height:100%;max-width:none;object-fit:cover;transform:scale(1.12) translateY(var(--py,0px))}
.show-s{width:calc(100% - 112px);height:calc(100% - 96px);display:grid;place-items:center}.show-s img{width:auto;max-width:100%;max-height:100%;border-radius:12px;box-shadow:0 0 0 1px rgba(var(--inka),.2)}
.show-2{justify-self:end;width:min(340px,100%);transform:translateY(var(--py,0px))}.show-2 img{width:auto;max-width:100%;max-height:621px;margin-left:auto;border-radius:16px;box-shadow:0 0 0 1px rgba(var(--inka),.14)}
.pairs{display:grid;gap:28px;margin-top:32px;max-width:816px}.pair{display:grid;grid-template-columns:244px minmax(0,540px);gap:32px}.pair h3{font:510 22px/1.5 var(--f);letter-spacing:-.01em}.pair p{font:510 20px/1.5 var(--f);letter-spacing:-.01em;color:var(--mute)}
.show>.h2+.pairs{margin-top:41px}
/* panels: edge to edge, radius 40, 4 % of ink; 210 above the head */
.panel{background:var(--panel);border-radius:40px;margin-top:80px;padding:210px 80px 230px}.show+.panel{margin-top:250px}
/* word cards: 248 square, radius 36, 24 inside, full ink falling from a lighter top; they overlap by 12 and close up like a fan as the section arrives */
.comp{padding:210px 20px 250px;overflow:clip}.fan{display:flex;justify-content:center;margin-top:96px;padding:2px 0}
.wc{position:relative;flex:none;width:248px;height:248px;margin:0 -6px;padding:24px;border-radius:36px;border:1px solid rgba(var(--bga),.1);background:linear-gradient(var(--card),var(--ink));color:var(--bg);display:flex;flex-direction:column;justify-content:space-between;gap:12px;
 transform:translate(calc(var(--k)*var(--sp,0px)),var(--dy,0px)) scale(var(--sc,1));opacity:var(--op,1)}
.wc.mid{z-index:1;filter:drop-shadow(0 4px 95px rgba(0,0,0,.35))}.wc h3{font:590 30px/1.08 var(--f);overflow-wrap:anywhere}.wc p{font:400 17px/1.36 var(--f);color:var(--cardmute)}
/* plans: built from the reference's own parts — the panel, its white tiles of radius 12, and the pill with the price in its chip */
.plan-g{display:grid;grid-template-columns:repeat(2,minmax(0,620px));justify-content:center;gap:16px 40px;margin-top:80px}.plan-g:has(.plan:only-child){grid-template-columns:minmax(0,620px)}
.plan{background:var(--bg);border-radius:12px;padding:28px;display:flex;flex-direction:column}.plan h3{font:510 22px/1.5 var(--f);letter-spacing:-.01em}.plan .ln{font:480 16px/1.5 var(--f);color:var(--mute)}
.plan ul{margin-top:16px}.plan li{padding:12px 0;border-top:1px solid var(--hair);font:480 16px/1.5 var(--f);color:var(--mute)}
.plan-b{margin-top:auto;padding-top:24px;display:flex;align-items:center;gap:10px 16px;flex-wrap:wrap}.per{font:480 14px/1.5 var(--f);color:var(--mute)}.price{font:510 22px/1.5 var(--f)}
.pnote{max-width:680px;margin:40px auto 0;text-align:center;font:480 16px/1.5 var(--f);color:var(--mute)}
/* questions: two columns of 620, 40 between, 16 between rows; tile radius 12; question 17/20.4 weight 510 at 20 x 28; a 28 round with a plus that turns to a minus; answer 16/24 muted */
.qas{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));grid-template-rows:repeat(var(--r),auto);grid-auto-flow:column;gap:16px 40px;align-items:start;margin-top:80px}
.qa{background:var(--bg);border-radius:12px;overflow:hidden}.qa button{display:flex;align-items:center;justify-content:space-between;gap:24px;width:100%;padding:20px 28px;border-radius:12px;font:510 17px/1.2 var(--f);transition:background-color .32s var(--e)}
.qa button:hover{background:var(--hov)}.qa button:focus-visible{outline-offset:-3px}
.pm{position:relative;flex:none;width:28px;height:28px;border-radius:50%;background:var(--plus)}.pm::before,.pm::after{content:"";position:absolute;left:13px;top:8px;width:2px;height:12px;border-radius:2px;background:var(--ink);transform:rotate(90deg)}
.pm::after{transform:none;transition:transform .3s var(--e)}[aria-expanded=true] .pm::after{transform:rotate(90deg)}
.qa-b p{padding:12px 72px 24px 28px;font:480 16px/1.5 var(--f);color:var(--mute)}
.js .qa-b{display:grid;grid-template-rows:0fr;opacity:0;visibility:hidden;transition:grid-template-rows .38s var(--e),opacity .24s,visibility 0s .38s}.js .qa-b>div{overflow:hidden;min-height:0}
.js .qa.on .qa-b{grid-template-rows:1fr;opacity:1;visibility:visible;transition-delay:0s}
/* the close: 740 high, its block in the middle; mark 90; head 34/40.8 */
.end{min-height:740px;justify-content:center;padding:120px 16px;margin-top:120px}.end .icon{max-height:90px}.end .icon.wm{max-height:34px}.end .h2{font-size:34px;max-width:13.5em}
/* FOOT: a panel 40 from the sides, radius 24, 56/48 inside, standing on the top of a wide picture that fades out of the page and settles as the page ends */
.ft{position:relative;margin-top:180px;overflow:hidden}.ft.pic{padding-bottom:633px}
.ft-bk{position:absolute;left:0;right:0;top:178px;bottom:0;overflow:hidden;transform-origin:50% 50%}.ft-bk img{position:absolute;inset:0;width:100%;height:100%;max-width:none;object-fit:cover}
.ft-bk i{position:absolute;inset:0;background:linear-gradient(rgb(var(--bga)) 0,rgba(var(--bga),.86) 4%,rgba(var(--bga),.5) 14%,rgba(var(--bga),.16) 26%,rgba(var(--bga),0) 40%)}
.ft-card{position:relative;margin:0 40px;padding:56px 48px 48px;border-radius:24px;background:var(--panel);display:grid;gap:32px;justify-items:start}
.ft-logo{display:flex;align-items:center;gap:12px;font:510 22px/1 var(--f)}.fl{width:auto;height:auto;max-height:44px;max-width:min(300px,100%)}.fl.wm{max-height:30px}
.ft-tags{display:grid;gap:8px}.tags{display:flex;flex-wrap:wrap;gap:6px}.tags a{display:flex;align-items:center;min-height:30px;padding:3px 56px 4px 8px;border-radius:6px;background:var(--tag);color:var(--tagtx);border:1px solid rgba(var(--inka),.12);font:400 14px/1.5 var(--f);transition:background-color .2s cubic-bezier(.07,.3,.1,.9)}
.tags a:hover{background:var(--dim)}.ft-l,.ft-t{font:400 14px/1.5 var(--f);color:var(--mute);max-width:640px}.ft-l+.ft-t{margin-top:-20px}
/* arrivals (only once script is there to let them in) */
.js [data-rv] .m>span{opacity:0;transform:translateY(110%)}.js [data-rv].in .m>span{animation:wordin .7s var(--x) var(--d,0s) both}
.js .lev .tones li{opacity:0;transform:translateY(18px)}.js .lev.in .tones li{opacity:1;transform:none;transition:opacity .5s var(--x) var(--d),transform .6s var(--x) var(--d)}
.js [data-rv=up]{opacity:0;transform:translateY(22px);transition:opacity .8s var(--x),transform 1.2s var(--x)}.js [data-rv=up].in{opacity:1;transform:none}
.js .end .icon{opacity:0}.js .end.in .icon{animation:iconin .75s var(--x) both}.js .end .grow{opacity:0}.js .end.in .grow{animation:pillin .64s cubic-bezier(.2,.9,.28,1) .5s both}.js .end.in .grow .pl{animation:labin .34s cubic-bezier(.2,.9,.28,1) .9s both}
.js .stage:not(.pin) .st{opacity:0;transform:translateY(22px) scale(.96);transition:opacity .68s var(--x),transform .68s var(--x)}.js .stage:not(.pin) .st.in{opacity:1;transform:none}
@media (max-width:1100px){.show{margin-inline:40px}.panel{padding-inline:40px}.pair{grid-template-columns:200px minmax(0,1fr)}}
/* PHONE (measured at 390): bar 12 from the edges, 52 and 50 high; display 31; heads 26; one column; word cards stacked 4 apart; questions in one column; foot tags full width */
@media (max-width:899px){.navres{height:124px}.top{padding-top:12px}.bar-h{height:50px}.brand{font-size:19px}.mb{top:3px;right:6px}.buy{height:50px;border-radius:10px;padding:0 6px 0 16px}.tile{width:36px;height:36px}.menu a{font-size:21px}
.open{padding-top:96px;gap:26px}.icon{max-height:76px}.open-t{gap:14px}h1{font-size:31px}.lede{display:block;max-width:330px}.lede .m{display:inline;overflow:visible}.lede .m>span{display:inline}
.pill{font-size:14.5px;padding-left:18px;gap:10px}.pill.two .pl{padding-left:18px}.pill.two{flex-wrap:wrap;justify-content:center;border-radius:28px}.chip{padding-inline:12px}
.h2{font-size:26px}.lev{min-height:660px;padding:72px 24px}.tones{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:18px 0 0}.tones li{justify-content:center;text-align:center;min-height:46px;padding:10px 14px;font-size:17px}.tones li:last-child:nth-child(odd){grid-column:1/-1}
.show{margin:48px 16px 0}.show .h2{text-align:center}.show-g{grid-template-columns:1fr;gap:44px;margin-top:49px}.show-p{aspect-ratio:358/503;border-radius:32px}.show-s{width:calc(100% - 40px);height:calc(100% - 64px)}.show-2{justify-self:center}.show-2 img{margin:0 auto;max-height:520px}
.pairs{margin-top:44px;gap:32px}.pair{grid-template-columns:1fr;gap:14px;text-align:center}.pair p{font-size:17px;letter-spacing:-.012em;padding:0 21px}
.panel,.comp{padding:88px 24px;margin-top:80px}.show+.panel{margin-top:140px}.faq,.plans{border-radius:32px;padding-inline:32px}
.fan{flex-direction:column;align-items:center;gap:4px;margin-top:46px}.wc{margin:0;transform:none;opacity:1}.wc.mid{filter:none}
.js .fan .wc{opacity:0;transform:translateY(12px) scale(.88);transition:opacity .55s var(--e) var(--d),transform .7s var(--e) var(--d)}.js .fan.in .wc{opacity:1;transform:none}
.plan-g,.qas{grid-template-columns:1fr;grid-auto-flow:row;grid-template-rows:none;margin-top:60px}.plan{padding:22px 18px}.plan li{font-size:15px}.pnote{font-size:15px}
.qa button{padding:18px;gap:18px;font-size:16px}.qa-b p{padding:12px 64px 22px 18px;font-size:15px}
.end{min-height:560px;gap:32px;padding:80px 16px;margin-top:32px}.end .h2{font-size:26px}
.ft{margin-top:104px}.ft.pic{padding-bottom:570px}.ft-bk{top:auto;height:720px}.ft-card{margin:0 12px;padding:36px 20px 28px;gap:24px}.ft-tags,.tags{display:grid;width:100%;gap:8px}.tags a{min-height:32px;padding:4px 12px}.ft-card{justify-items:stretch}}
@media (min-width:900px) and (max-height:620px){.pin .st-t,.pin .st-r{font-size:19px}}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}html{scroll-behavior:auto}
.js [data-rv] .m>span,.js .end .icon,.js .end .grow,.js .lev .tones li,.js [data-rv=up],.js .stage .st,.js .fan .wc{opacity:1!important;transform:none!important}}
"""

JS = r"""
(() => { const D = document, R = D.documentElement, calm = matchMedia('(prefers-reduced-motion:reduce)').matches, $ = (s, r) => (r || D).querySelector(s), $$ = (s, r) => [...(r || D).querySelectorAll(s)], cl = (v, a, b) => Math.max(a, Math.min(b, v));
/* the bar leaves when the page goes down past 80 and returns on the first move back up; its list opens under the name and dims the page */
const top = $('.top'), mb = $('.mb'), scrim = $('.scrim'); let last = scrollY;
const menu = o => { top.classList.toggle('mopen', o); scrim.classList.toggle('on', o); mb.setAttribute('aria-expanded', o); };
if (mb) { mb.addEventListener('click', () => menu(!top.classList.contains('mopen'))); scrim.addEventListener('click', () => menu(false)); D.addEventListener('keydown', ev => { if (ev.key === 'Escape' && top.classList.contains('mopen')) { menu(false); mb.focus(); } }); }
top.addEventListener('focusin', () => top.classList.remove('away'));
/* arrivals: once, when a block is a little way into the window */
const rv = $$('[data-rv]'); if (calm || !('IntersectionObserver' in window)) rv.forEach(x => x.classList.add('in')); else { const io = new IntersectionObserver(es => es.forEach(x => { if (x.isIntersecting) { x.target.classList.add('in'); io.unobserve(x.target); } }), { rootMargin: '0px 0px -12% 0px', threshold: .12 }); rv.forEach(x => io.observe(x)); }
/* questions: one open at a time */
const qa = $$('.qa'); qa.forEach(q => $('button', q).addEventListener('click', () => { const o = !q.classList.contains('on'); qa.forEach(x => { x.classList.toggle('on', x === q && o); $('button', x).setAttribute('aria-expanded', x === q && o); }); }));
/* the stage (900 px and up, motion welcome): held for 90vh a step; everything is set from the scroll position itself, with no easing */
const sec = $('#stage'), arts = sec ? $$('.st', sec) : [], n = arts.length, mq = matchMedia('(min-width:900px)'); let pinned = false;
const W = arts.map(a => ({ t: $$('.st-t .w', a), r: $$('.st-r .w', a) }));
const pin = () => { pinned = !!sec && !calm && mq.matches && n > 0; if (sec) { sec.classList.toggle('pin', pinned); if (!pinned) arts.forEach((a, i) => { a.removeAttribute('style'); W[i].t.concat(W[i].r).forEach(w => w.classList.remove('on')); }); } };
const par = $$('[data-par]'), fan = $('.fan'), fb = $('.ft-bk'); let q = false;
const frame = () => { q = false; const vh = innerHeight, y = scrollY;
  if (!top.classList.contains('mopen') && !top.querySelector(':focus-visible')) { if (y > last + 2 && y > 80) top.classList.add('away'); else if (y < last - 2 || y <= 80) top.classList.remove('away'); } last = y;
  if (pinned) { const S = vh * .9, u = cl(-sec.getBoundingClientRect().top / S, -1, n), per = 15 / 810; $('.rule', sec).style.setProperty('--p', (cl(u / n, 0, 1) * 100).toFixed(2) + '%');
    arts.forEach((a, i) => { const t = u - i, into = i === 0 ? 1 : cl(t / .07, 0, 1), out = i === n - 1 ? 0 : cl((t - .9) / .1, 0, 1), o = into * (1 - out);
      a.style.setProperty('--o', o.toFixed(3)); a.style.setProperty('--fo', o.toFixed(3)); a.style.setProperty('--y', ((1 - into) * 36 - out * 36).toFixed(1) + 'px'); a.style.visibility = o > 0 ? 'visible' : 'hidden';
      const a1 = Math.floor((t + .012) / per), a2 = Math.floor((t - .66) / per); W[i].t.forEach((w, j) => w.classList.toggle('on', j < a1)); W[i].r.forEach((w, j) => w.classList.toggle('on', j < a2)); }); }
  if (!calm) { par.forEach(p => { const r = p.parentElement.getBoundingClientRect(), k = cl((vh - r.top) / (vh + r.height), 0, 1); p.style.setProperty('--py', ((k * 2 - 1) * +p.dataset.par).toFixed(1) + 'px'); });
    if (fan && innerWidth >= 900) { const r = fan.getBoundingClientRect(), k = 1 - cl((vh * .53 + 492 - (r.top + r.height / 2)) / 492, 0, 1); $$('.wc', fan).forEach(c => { const mid = c.style.getPropertyValue('--k') === '0.0'; c.style.setProperty('--sp', (236 * k).toFixed(1) + 'px'); c.style.setProperty('--sc', (mid ? 1 + .2 * k : 1 - .08 * k).toFixed(3)); c.style.setProperty('--dy', (mid ? 0 : 8 * k).toFixed(1) + 'px'); c.style.setProperty('--op', (mid ? 1 : 1 - .16 * k).toFixed(3)); }); }
    else if (fan) $$('.wc', fan).forEach(c => c.removeAttribute('data-x') || ['--sp', '--sc', '--dy', '--op'].forEach(v => c.style.removeProperty(v)));
    if (fb) { const r = fb.parentElement.getBoundingClientRect(), end = R.scrollHeight - vh - y; fb.style.opacity = cl((vh * .74 - r.top) / 310, 0, 1).toFixed(3); fb.style.transform = 'scale(' + (1 + .15 * cl(end / 830, 0, 1)).toFixed(4) + ')'; } } };
const ask = () => { if (!q) { q = true; requestAnimationFrame(frame); } };
pin(); frame(); addEventListener('scroll', ask, { passive: true }); addEventListener('resize', () => { pin(); ask(); }); mq.addEventListener && mq.addEventListener('change', () => { pin(); ask(); });
})();
"""


def render(d: dict) -> str:
    pal = d.get('palette') or {}
    ground, ink = pal.get('ground') or '#ffffff', pal.get('ink') or '#050505'
    accent = pal.get('accent') or ink
    root = _theme(ground, ink, accent, pal.get('extra'))
    hues = _hues(ground, ink, accent, pal.get('extra'))
    b, h = d.get('brand') or {}, d.get('hero') or {}
    title = ' — '.join(x for x in (b.get('name'), h.get('kicker') or h.get('title')) if x)
    body = ''.join((s_open(d), s_stage(d), s_tones(d, hues), s_show(d), s_cards(d), s_plans(d), s_faq(d), s_close(d)))
    return ('<!DOCTYPE html>\n<html lang="%s">\n<head>\n<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">\n<title>%s</title>\n%s'
            '<script>document.documentElement.classList.add("js");addEventListener("error",function(){document.documentElement.classList.remove("js")})</script>\n'
            '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link href="%s" rel="stylesheet">\n'
            '<style>:root{%s}%s</style>\n</head>\n<body>\n%s\n<main id="main">%s</main>\n%s\n<script>%s</script>\n</body>\n</html>\n') % (
        e(d.get('lang') or 'en'), e(title), '<meta name="description" content="%s">\n' % e(h['text']) if h.get('text') else '', FONTS, root, CSS, s_top(d), body, s_foot(d), JS)
