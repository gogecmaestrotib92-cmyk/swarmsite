"""dawnsaunders — template rebuilt from the measured build of https://dawnsaunders.com (an author and speaker's own site).
render(d) -> one self-contained page. Pure: no file reads, no model call. See NOTES.md for measures and decisions.

The reference stands a cut-out portrait through a giant first name. A client has ordinary photographs, so the first
screen here is built for one: the portrait fills an arch window that rises from the bottom edge to the foot of the
giant word, in front of the reference's own half disc."""
import html, re

M = '../../'


def esc(s): return html.escape(str(s if s is not None else ''), quote=True)


# ── colour ──────────────────────────────────────────────────────────────────────────────────────────────────────────
def _rgb(h):
    h = (h or '#000').strip().lstrip('#')
    if len(h) == 3: h = ''.join(c * 2 for c in h)
    try: return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError: return (0, 0, 0)


def _hex(c): return '#%02x%02x%02x' % tuple(max(0, min(255, round(v))) for v in c)


def _lum(c):
    def f(v):
        v /= 255
        return v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4
    return .2126 * f(c[0]) + .7152 * f(c[1]) + .0722 * f(c[2])


def _con(a, b):
    la, lb = _lum(a), _lum(b)
    return (max(la, lb) + .05) / (min(la, lb) + .05)


def _mix(a, b, t): return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def _toward(c, target, bg, need):
    """c moved toward target until it reads `need`:1 on bg"""
    for i in range(0, 21):
        m = _mix(c, target, i / 20)
        if _con(m, bg) >= need: return m
    return target


def _soft(fg, bg, t, need=4.6):
    """fg held back toward bg by t (the reference's 60–75 % inks), as far as the contrast allows"""
    while t > 0:
        m = _mix(fg, bg, t)
        if _con(m, bg) >= need: return m
        t -= .05
    return fg


# ── words ───────────────────────────────────────────────────────────────────────────────────────────────────────────
def _sentences(s): return [x for x in re.split(r'(?<=[.!?…])\s+', (s or '').strip()) if x]


def _fit(s, limit):
    """whole sentences of s up to limit characters (always the first one)"""
    out = ''
    for x in _sentences(s):
        if out and len(out) + 1 + len(x) > limit: break
        out = (out + ' ' + x).strip()
    return out


def _dot(title, cls='dot'):
    """the reference ends its headings on a coloured full stop; a heading that already ends on a mark has that mark coloured"""
    t = (title or '').strip()
    if not t: return ''
    if t[-1] in '.?!…': return esc(t[:-1]) + f'<span class="{cls}">{esc(t[-1])}</span>'
    return esc(t) + f'<span class="{cls}">.</span>'


def _word(s, limit=9):
    s = (s or '').strip().rstrip('.!?')
    if len(s) <= limit: return s
    return s.split()[0] if s.split() else s


def _link(o, cls, extra=''):
    if not o or not o.get('t'): return ''
    h = o.get('h')
    return f'<a class="{cls}" href="{esc(h)}">{esc(o["t"])}{extra}</a>' if h else f'<span class="{cls}">{esc(o["t"])}</span>'


LETTERED = re.compile(r'\bwords?\b|\blettering\b|\bcaption\b|\blogo\b|\broundel\b|\bsign\b|"[^"]{3,}"|“[^”]{3,}”', re.I)


def render(d: dict) -> str:
    g = lambda o, k, v=None: (o or {}).get(k) or v
    brand = d.get('brand') or {}
    name = (brand.get('name') or '').strip()
    lang = d.get('lang') or 'en'
    pal = d.get('palette') or {}
    ground, ink, acc = _rgb(pal.get('ground') or '#ffffff'), _rgb(pal.get('ink') or '#111111'), _rgb(pal.get('accent') or '#f7bc35')
    D, L = (ink, ground) if _lum(ink) < _lum(ground) else (ground, ink)
    if _con(D, L) < 7: D, L = _mix(D, (0, 0, 0), .6), _mix(L, (255, 255, 255), .6)
    A = acc if min(_con(acc, D), _con(acc, L)) > 1.25 else _mix(acc, L if _lum(acc) < .3 else D, .35)
    onA = D if _con(D, A) >= _con(L, A) else L
    if _con(onA, A) < 4.6: onA = (0, 0, 0) if _con((0, 0, 0), A) > _con((255, 255, 255), A) else (255, 255, 255)
    other = L if onA == D else D
    wordA = other if _con(other, A) >= 3.1 else onA           # the giant word on the accent ground (the reference: white on yellow)
    onA_soft = _soft(onA, A, .4)
    A_onD = _toward(A, L, D, 4.6)                              # accent as ink on the dark ground
    A_onL = _toward(A, D, L, 4.6)                              # accent as ink on the light ground
    D2, D3 = _mix(D, L, .05), _mix(D, L, .13)                  # the reference's rgb(12) card and rgb(34) band ground on black
    L_soft_onD = _soft(L, D, .25); L_soft_onD2 = _soft(L, D2, .25)
    D_soft_onL = _soft(D, L, .4)
    spA = _mix(A, onA, .08); spA_t = onA if _con(onA, spA) >= 4.6 else ((0, 0, 0) if _lum(spA) > .2 else (255, 255, 255))
    spL = _mix(L, D, .07)
    DsQ = _soft(D, spL, .4)
    A_onD2 = _toward(A, L, D2, 4.6)
    V = {'D': D, 'L': L, 'A': A, 'onA': onA, 'wordA': wordA, 'onAs': onA_soft, 'AonD': A_onD, 'AonL': A_onL, 'D2': D2, 'D3': D3,
         'LsD': L_soft_onD, 'LsD2': L_soft_onD2, 'DsL': D_soft_onL, 'spA': spA, 'spAt': spA_t, 'spL': spL, 'DsQ': DsQ, 'AonD2': A_onD2}
    css_vars = ';'.join(f'--{k}:{_hex(v)}' for k, v in V.items()) + ';--Drgb:%d,%d,%d;--Lrgb:%d,%d,%d' % (*[round(x) for x in D], *[round(x) for x in L])

    # ── pictures: by role, size and proportion; each once ───────────────────────────────────────────────────────────
    media = d.get('media') or {}
    photos = [p for p in (media.get('photos') or []) if p.get('src') and p.get('w') and p.get('h')]
    by_src = {p['src']: p for p in photos}
    used = set()
    team = d.get('team') or {}
    people = list(team.get('items') or [])
    for grp in team.get('groups') or []:
        for it in grp.get('items') or []: people.append(dict(it, _group=grp.get('t')))
    team_imgs = {p.get('img') for p in people if p.get('img')}
    steps = d.get('steps') or {}
    step_items = [s for s in (steps.get('items') or []) if s.get('title') or s.get('text')]
    step_imgs = {s.get('img') for s in step_items if s.get('img') in by_src}
    lettered = lambda p: bool(p.get('lettered') or p.get('text') or LETTERED.search(p.get('alt') or ''))

    def img(p, cls='', pos=None, eager=False):
        st = f' style="object-position:{pos}"' if pos else ''
        return (f'<img class="{cls}" src="{M}{esc(p["src"])}" width="{p["w"]}" height="{p["h"]}" alt="{esc(p.get("alt") or "")}"'
                f'{st}{"" if eager else " loading=lazy"} decoding="async">')

    # first screen: only a photograph of the person (or the people); never a landscape, so a picture with lettering
    # baked in cannot land there
    hero_pic = None
    me = next((p for p in people if p.get('img') in by_src and (p.get('name') or '').strip().lower() == name.lower()), None)
    if not me and len([p for p in people if p.get('img') in by_src]) == 1 and len(people) == 1: me = people[0]
    if me: hero_pic = by_src[me['img']]
    if not hero_pic:
        c = [p for p in photos if p.get('role') in ('people', 'portrait') and p['src'] not in team_imgs and p['src'] not in step_imgs and min(p['w'], p['h']) >= 480]
        c.sort(key=lambda p: (lettered(p), p.get('role') != 'people', -p['w'] * p['h']))
        hero_pic = c[0] if c else None
    if hero_pic: used.add(hero_pic['src'])

    def free(p): return p['src'] not in used and p['src'] not in team_imgs and p['src'] not in step_imgs and p.get('role') not in ('product',)

    # the band: a wide photograph, large enough for 1400 px across (scaled up by no more than 1.6)
    band_pic, band_ar = None, 1.4
    c = []
    for p in photos:
        if not free(p) or p.get('small'): continue
        ar = max(1.4, min(2.4, p['w'] / p['h']))
        if max(1400 / p['w'], 1400 / ar / p['h']) <= 1.6: c.append((lettered(p), -p['w'], p, ar))
    if c:
        c.sort(key=lambda x: x[:2]); band_pic, band_ar = c[0][2], c[0][3]; used.add(band_pic['src'])
    # the closing pair: one more photograph as a whole card (690 × 700 at 1440; a small one is held to its own pixels)
    pair_pic = None
    c = [p for p in photos if free(p) and p.get('role') != 'portrait' and p['w'] >= 600 and p['h'] >= 500 and .6 <= p['w'] / p['h'] <= 2.2]
    c.sort(key=lambda p: (lettered(p), -min(p['w'], p['h'])))
    if c: pair_pic = c[0]; used.add(pair_pic['src'])

    out = []
    nav = [n for n in (d.get('nav') or []) if n.get('t')][:7]
    cta = d.get('cta') or g(d.get('hero'), 'primary') or {}
    hero = d.get('hero') or {}

    # ── header ──────────────────────────────────────────────────────────────────────────────────────────────────────
    nm = name.split()
    logo = f'<b>{esc(nm[0])}</b>{esc(" " + " ".join(nm[1:]) if len(nm) > 1 else "")}' if nm else ''
    links = ''.join(f'<a href="{esc(n.get("h") or "#")}">{esc(n["t"])}</a>' for n in nav)
    out.append(f'''<a class="skip" href="#main">{esc(name)} ↓</a>
<header class="nav"><a class="logo" href="{esc(brand.get("home") or "#")}">{logo}</a>
{f'<nav class="nl" aria-label="{esc(name)}">{links}</nav>' if links else ''}
{_link(cta, "btn nc")}
{f'<details class="burger"><summary aria-label="Menu"><i></i><i></i><i></i></summary><nav>{links}{_link(cta, "btn")}</nav></details>' if links else ''}
</header><main id="main">''')

    # ── 1 first screen ──────────────────────────────────────────────────────────────────────────────────────────────
    first = (nm[0] if nm else '').lower()
    n1 = max(len(first) + .5, 4.4)
    text, text2 = (hero.get('text') or '').strip(), (hero.get('text2') or '').strip()
    side = _fit(text, 340)
    rest = text[len(side):].strip()
    t2_side = text2 if text2 and len(text2) <= 120 else ''
    lead_in = ' '.join(x for x in (rest, '' if t2_side else text2) if x)
    arch = ''
    if hero_pic:
        aw, ah = hero_pic['w'], hero_pic['h']
        arch = f'<div class="arch" data-slot="portrait" style="--pw:{aw}px;--ph:{ah}px"><i class="hd"></i><div class="win">{img(hero_pic, eager=True, pos="50% 22%")}</div></div>'
    else:
        arch = ''   # no portrait: the first screen is the word and the two columns of type, no empty disc
    out.append(f'''<section class="hero{'' if hero_pic else ' nopic'}">
<div class="gw" aria-hidden="true" style="--n:{n1:.1f}">{esc(first)}<i>.</i></div>
<div class="hg"><div class="hl">{f'<h1>{esc(hero.get("title") or name)}</h1>'}{f'<p>{esc(t2_side)}</p>' if t2_side else ''}</div>
{arch}
<div class="hr">{f'<p>{esc(side)}</p>' if side else ''}</div></div></section>''')

    # ── 2 the statement in the half disc ────────────────────────────────────────────────────────────────────────────
    st = d.get('statement') or {}
    if st.get('title') or st.get('text'):
        ttl = '' if (band_pic and st.get('text')) else (st.get('title') or '').strip()   # the title stands on the band when there is one
        body = _fit(st.get('text') or '', max(120, 380 - len(ttl)))
        n = len(ttl) + len(body)
        tier = 0 if n <= 190 else 1 if n <= 270 else 2
        out.append(f'''<section class="stmt t{tier}"><i class="sun" data-r></i><div class="sw" data-r style="--dl:.16s"><p>{f'<strong>{esc(ttl)}</strong> ' if ttl else ''}{esc(body)}</p></div>
{f'<p class="lead" data-r>{esc(lead_in)}</p>' if lead_in else ''}</section>''')
    elif lead_in:
        out.append(f'<section class="stmt bare"><p class="lead" data-r>{esc(lead_in)}</p></section>')

    # ── 3 heading + the cards ───────────────────────────────────────────────────────────────────────────────────────
    if steps.get('title') or steps.get('text'):
        out.append(f'''<section class="hd2"><div data-r>{f'<h2>{esc(steps["title"])}</h2>' if steps.get('title') else ''}{f'<p>{esc(steps["text"])}</p>' if steps.get('text') else ''}</div></section>''')
    if step_items:
        cards = []
        nsi = len(step_items)
        for i, s in enumerate(step_items):
            dark = (i % 2 == 1) if (i // 2) % 2 == 0 else (i % 2 == 0)
            wide = nsi % 2 == 1 and i == nsi - 1
            w = _word(s.get('title') or s.get('k') or '').lower()
            nw = max(len(w) + .5, 4.4)
            p = by_src.get(s.get('img')) if s.get('img') not in used else None
            if p: used.add(p['src'])
            pic = f'<div class="cp" data-slot="step">{img(p)}</div>' if p else ''
            btn = _link(s.get('cta'), 'btn sm')
            cards.append(f'''<article class="card {'dk' if dark else 'ac'}{' wide' if wide else ''}{' pic' if p else ''}" data-r style="--dl:{.08 * (i % 2):.2f}s">
<div class="ct"><div class="cw" aria-hidden="true" style="--n:{nw:.1f}">{esc(w)}<i>.</i></div>{'' if wide else pic}
{f'<span class="meta">{esc(s["k"])}</span>' if s.get('k') and s.get('k').strip().lower() != (s.get('title') or '').strip().lower() else ''}
{f'<h3>{esc(s["title"])}</h3>' if s.get('title') else ''}{f'<p>{esc(s["text"])}</p>' if s.get('text') else ''}{f'<div class="bs">{btn}</div>' if btn else ''}</div>{pic if wide else ''}</article>''')
        out.append(f'<section class="cards">{"".join(cards)}</section>')

    # ── 4 the photograph band ───────────────────────────────────────────────────────────────────────────────────────
    band_title = (st.get('title') or '').strip() if (band_pic and st.get('title')) else ''
    if band_pic:
        ss = _sentences(band_title)
        sent = (esc(ss[0]) + (f' <span>{esc(" ".join(ss[1:]))}</span>' if len(ss) > 1 else '')) if ss else ''
        b2 = hero.get('secondary') or {}
        out.append(f'''<section class="band"><div class="bi" data-r data-slot="band" style="--ar:{band_ar:.3f}">{img(band_pic)}<i class="veil"></i>
{f'<div class="bt">{f"<p>{sent}</p>" if sent else "<span></span>"}{_link(b2, "btn wh sm")}</div>' if (sent or b2.get('t')) else ''}</div></section>''')

    # ── 5 figures and voices on the accent ground ───────────────────────────────────────────────────────────────────
    figures = [f for f in (d.get('figures') or []) if f.get('v')][:4]
    quotes = [q for q in (d.get('quotes') or []) if q.get('q')][:10]
    acc_n = [0]

    def accordion(items, kind):
        """the reference's shelf: spines with a name set upright, one open panel; radio inputs, so it works without script"""
        acc_n[0] += 1; aid = f'a{acc_n[0]}'; n = len(items)
        ins = ''.join(f'<input class="ar" type="radio" name="{aid}" id="{aid}-{i}"{" checked" if i == 0 else ""} aria-label="{esc(it["spine"])}">' for i, it in enumerate(items))
        its = []
        for i, it in enumerate(items):
            ql = len(it.get('text') or '')
            sz = 'q0' if ql <= 300 else 'q1' if ql <= 620 else 'q2'
            pic = f'<div class="pp" data-slot="portrait">{img(it["img"], pos="50% 20%")}</div>' if it.get('img') else ''
            body = f'<q>{esc(it["text"])}</q>' if kind == 'quote' else esc(it.get('text') or '')
            its.append(f'''<div class="it{' hp' if pic else ''}"><label class="spine" for="{aid}-{i}"><span>{esc(it["spine"])}</span><i></i></label>
<div class="pan"><div class="pt"><span class="pa">{esc(it.get("tl") or "")}</span><span class="pb">{esc(it.get("tr") or "")}</span></div>
<p class="{sz}">{body}</p><div class="pf"><b>{esc(it.get("name") or "")}</b>{it.get("foot") or ""}</div></div>{pic}</div>''')
        dots = ''.join(f'<label for="{aid}-{i}"></label>' for i in range(n)) if n > 1 else ''
        return f'<div class="accw" data-acc style="--n:{n}">{ins}<div class="acc" data-r style="--dl:.16s">{"".join(its)}</div>{f"<div class=dots>{dots}</div>" if dots else ""}</div>'

    if figures or quotes:
        figs = ''.join(f'<div class="fg"><b>{esc(f["v"])}</b><span>{esc(f.get("l") or "")}</span></div>' for f in figures)
        qa = accordion([{'spine': q.get('name') or q.get('role') or str(i + 1), 'tl': q.get('title'), 'tr': q.get('role'), 'text': q['q'], 'name': q.get('name')} for i, q in enumerate(quotes)], 'quote') if quotes else ''
        out.append(f'''<section class="voices">{f'<div class="fgs" data-r style="--k:{len(figures)}">{figs}</div>' if figs else ''}{qa}</section>''')

    # ── 6 ledgers on the light ground: prices, plans, people, credentials ───────────────────────────────────────────
    def row(title, sub='', right='', left=None, h=None):
        tag, hr = ('a', f' href="{esc(h)}"') if h else ('div', '')
        lc = f'<span class="rl">{left}</span>' if left is not None else ''
        return (f'<{tag} class="row{" l3" if left is not None else ""}"{hr}>{lc}<span class="rm"><span class="rt">{esc(title)}</span>'
                f'{f"<span class=rs>{sub}</span>" if sub else ""}</span>{f"<span class=rr>{right}</span>" if right else ""}</{tag}>')

    def ledger(head, right, cls=''):
        return f'<div class="lg {cls}" data-r><div class="ll">{head}</div><div class="lr">{right}</div></div>'

    def feat(top_l='', top_r='', title='', text='', more='', cls=''):
        top = f'<div class="ft"><span>{esc(top_l)}</span><span>{esc(top_r)}</span></div>' if (top_l or top_r) else ''
        return f'<div class="fc {cls}">{top}{f"<div class=fh>{esc(title)}</div>" if title else ""}{f"<p>{esc(text)}</p>" if text else ""}{more}</div>'

    light = []
    cat = d.get('catalogue') or {}
    groups = [gr for gr in (cat.get('groups') or []) if gr.get('items') or gr.get('text')]
    if groups:
        blocks = []
        if cat.get('title') or cat.get('text'):
            blocks.append(f'''<div class="lh" data-r>{f'<h2>{_dot(cat.get("title"))}</h2>' if cat.get('title') else ''}{f'<p>{esc(cat["text"])}</p>' if cat.get('text') else ''}</div>''')
        featured = False
        for gr in groups:
            rows = []
            for it in gr.get('items') or []:
                if not it.get('name'): continue
                prices = it.get('prices') or []
                price = esc(it.get('price') or '') + ''.join(f'<span class="pl"><em>{esc(p.get("label") or "")}</em> {esc(p.get("price") or "")}</span>' for p in prices)
                if it.get('state'): price += f'<span class="pl"><em>{esc(it["state"])}</em></span>'
                sub = ' · '.join(esc(x) for x in (it.get('note'), it.get('text')) if x)
                if it.get('rows'): sub += ''.join(f'<span class="ri">{esc(r)}</span>' for r in it['rows'])
                if not featured and it.get('price') and not prices and it.get('text'):
                    featured = True
                    rows.append(feat(it['name'], it.get('note') or '', it['price'], it.get('text') or ''))
                else:
                    rows.append(row(it['name'], sub, price, h=it.get('h')))
            more = _link({'t': gr.get('t'), 'h': gr.get('h')}, 'btn', '<span class="ar2" aria-hidden="true">→</span>') if gr.get('h') and gr.get('t') else ''
            head = f'''{f'<h3>{_dot(gr.get("t"))}</h3>' if gr.get('t') else ''}{f'<p>{esc(gr["text"])}</p>' if gr.get('text') else ''}{more}'''
            blocks.append(ledger(head, ''.join(rows)))
        if cat.get('note'): blocks.append(f'<p class="ln" data-r>{esc(cat["note"])}</p>')
        light.append(''.join(blocks))

    plans = d.get('plans') or {}
    pitems = [p for p in (plans.get('items') or []) if p.get('name')]
    if pitems:
        cards = []
        for p in pitems:
            rows_ = ''.join(f'<li>{esc(r)}</li>' for r in (p.get('rows') or []))
            more = (f'<ul>{rows_}</ul>' if rows_ else '') + (f'<div class="bs">{_link(p.get("cta"), "btn sm")}</div>' if g(p.get('cta'), 't') else '')
            cards.append(feat(p['name'], p.get('per') or '', p.get('price') or '', p.get('line') or '', more, '' if p.get('marked') else 'q'))
        head = f'''{f'<h2>{_dot(plans.get("title"))}</h2>' if plans.get('title') else ''}{f'<p>{esc(plans["text"])}</p>' if plans.get('text') else ''}'''
        light.append(ledger(head, ''.join(cards) + (f'<p class="ln">{esc(plans["note"])}</p>' if plans.get('note') else ''), 'big'))

    creds = [c for c in (d.get('credentials') or []) if c.get('t')]
    trust = [t for t in (d.get('trust') or []) if t]

    def cred_rows():
        rs = []
        for c in creds:
            left = f'<img src="{M}{esc(c["img"])}" alt="" loading="lazy">' if c.get('img') else esc(c.get('year') or '')
            rs.append(row(c['t'], esc(c.get('text') or ''), esc(c.get('year') or '') if c.get('img') else '', left=left, h=c.get('h')))
        return ''.join(rs)

    if people:
        with_pic = [p for p in people if p.get('img') in by_src and p['img'] not in used][:10]
        if len(people) == 1: with_pic = []
        rest_people = [p for p in people if p not in with_pic]
        blocks = []
        solo = len(people) == 1
        if not solo and (team.get('title') or team.get('text')):
            blocks.append(f'''<div class="lh" data-r>{f'<h2>{_dot(team.get("title"))}</h2>' if team.get('title') else ''}{f'<p>{esc(team["text"])}</p>' if team.get('text') else ''}</div>''')
        if with_pic:
            items = []
            for p in with_pic:
                used.add(p['img'])
                foot = ''.join(f'<a href="{h}">{esc(t)}</a>' for h, t in (('tel:' + re.sub(r'[^\d+]', '', p.get('phone') or ''), p.get('phone')), ('mailto:' + esc(p.get('email') or ''), p.get('email'))) if t)
                items.append({'spine': p.get('name'), 'tl': p.get('role'), 'tr': p.get('_group'), 'text': p.get('text') or '', 'name': p.get('name'), 'foot': foot, 'img': by_src[p['img']]})
            blocks.append(accordion(items, 'person'))
        if solo:
            p = people[0]
            more = ''.join(f'<a class="fl" href="{h}">{esc(t)}<span aria-hidden="true">→</span></a>' for h, t in (('tel:' + re.sub(r'[^\d+]', '', p.get('phone') or ''), p.get('phone')), ('mailto:' + esc(p.get('email') or ''), p.get('email'))) if t)
            tl = ''.join(f'<p class="tr">{esc(t)}</p>' for t in trust if t.strip().lower() != (p.get('role') or '').strip().lower())
            trust = []
            head = f'''<h2>{_dot(p.get("name") or team.get("title"))}</h2>{f'<p>{esc(p["role"])}</p>' if p.get('role') else ''}{tl}{_link({'t': hero.get('secondary', {}).get('t'), 'h': hero.get('secondary', {}).get('h')}, 'btn', '<span class="ar2" aria-hidden="true">→</span>') if g(hero.get('secondary'), 't') and not band_pic else ''}'''
            blocks.append(ledger(head, (feat(text=p.get('text') or '', more=more) if (p.get('text') or more) else '') + cred_rows(), 'big'))
            creds = []
        elif rest_people:
            rows = []
            for p in rest_people:
                right = ''.join(f'<span class="pl">{esc(x)}</span>' for x in (p.get('phone'), p.get('email')) if x)
                sub = ' · '.join(esc(x) for x in (p.get('role'), p.get('text')) if x)
                rows.append(row(p.get('name') or '', sub, right, h=p.get('h')))
            blocks.append(f'<div class="lg one" data-r><div class="lr two">{"".join(rows)}</div></div>')
        light.append(''.join(blocks))

    if creds or (trust and not creds and not (len(people) == 1)):
        head = ''.join(f'<p class="tr">{esc(t)}</p>' for t in trust)
        body = cred_rows() if creds else ''
        if creds: light.append(ledger(head, body))
        else: light.append(f'<div class="lg one" data-r><div class="lr">{"".join(row(t) for t in trust)}</div></div>')
        trust_done = True
    else:
        trust_done = False
    solo_trust = ''
    if trust and not trust_done:
        solo_trust = f'<div class="lg one" data-r><div class="lr two">{"".join(row(t) for t in trust)}</div></div>'
        light.append(solo_trust)
    for blk in light:
        out.append(f'<section class="light">{blk}</section>')

    # ── 7 the question rows on the dark ground: what is offered, then the questions ─────────────────────────────────
    def qa(title, text, items, open_first):
        rows = ''.join(f'''<details{' open' if (open_first and i == 0) else ''}><summary><h3>{esc(q)}</h3><i aria-hidden="true"></i></summary><div class="an"><p>{esc(a)}</p></div></details>''' if a else f'<div class="nd"><h3>{esc(q)}</h3></div>' for i, (q, a) in enumerate(items))
        return f'''<section class="qa"><div class="qi" data-r><div class="ql">{f'<h2>{esc(title)}</h2>' if title else ''}{f'<p>{esc(text)}</p>' if text else ''}</div><div class="qr">{rows}</div></div></section>'''

    feats = d.get('features') or {}
    fi = [(f.get('t'), f.get('d')) for f in (feats.get('items') or []) if f.get('t')]
    if fi: out.append(qa(feats.get('title'), feats.get('text'), fi, True))
    faq = d.get('faq') or {}
    qi = [(f.get('q'), f.get('a')) for f in (faq.get('items') or []) if f.get('q')]
    if qi: out.append(qa(faq.get('title'), None, qi, False))

    # ── 8 the closing pair: the call and how to reach, beside a whole photograph ────────────────────────────────────
    close = d.get('close') or {}
    contact = d.get('contact') or {}
    place = d.get('place') or {}
    lines = []
    ph = contact.get('phone') or place.get('phone') or {}
    if ph.get('t'): lines.append(('<a href="%s">%s</a>' % (esc(ph.get('h') or 'tel:' + re.sub(r'[^\d+]', '', ph['t'])), esc(ph['t'])), ph.get('note')))
    em = contact.get('email') or place.get('email')
    if em: lines.append((f'<a href="mailto:{esc(em)}">{esc(em)}</a>', None))
    ad = place.get('address') or {}
    adr = ', '.join(esc(x) for x in (ad.get('street'), ' '.join(y for y in (ad.get('postcode'), ad.get('city')) if y), ad.get('region'), ad.get('country')) if x)
    if adr: lines.append((adr, None))
    for hh in place.get('hours') or []:
        if hh.get('days'): lines.append((esc(hh['days']), ' – '.join(x for x in (hh.get('open'), hh.get('close')) if x)))
    seen_h = {('mailto:' + em) if em else None}
    foot_h = {l.get('h') for l in ((d.get('foot') or {}).get('links') or []) + (place.get('social') or [])}
    for r in contact.get('routes') or []:
        if not r.get('t') or (r.get('h') in seen_h and not r.get('note')) or (r.get('h') in foot_h and not r.get('note')): continue
        if r.get('h') in seen_h and r.get('note'):
            lines = [(a, b or r['note']) if ('mailto:' in a and r['h'].startswith('mailto:')) else (a, b) for a, b in lines]; continue
        seen_h.add(r.get('h'))
        lines.append((f'<a href="{esc(r["h"])}">{esc(r["t"])}</a>' if r.get('h') else esc(r['t']), r.get('note')))
    note = hero.get('note')
    if note and not any(note == b or note in a for a, b in lines): lines.append((esc(note), None))
    if close.get('title') or close.get('text') or lines:
        btns = _link(close.get('cta') or cta, 'btn sm') + _link(contact.get('form'), 'btn sm ol') + (_link(place.get('booking'), 'btn sm ol') if g(place.get('booking'), 'h') != g(close.get('cta') or cta, 'h') else '')
        ls = ''.join(f'<li>{a}{f"<em>{esc(b)}</em>" if b else ""}</li>' for a, b in lines)
        pc = ''
        if pair_pic:
            pc = f'<div class="pcard" data-slot="pair" style="--pw:{pair_pic["w"]}px;--ph:{pair_pic["h"]}px">{img(pair_pic, pos="50% 40%")}</div>'
        out.append(f'''<section class="pair"><div class="pg{'' if pc else ' solo'}" data-r{f' style="--pw:{pair_pic["w"]}px"' if pair_pic and pair_pic.get('small') else ''}><div class="inv">{f'<h2>{esc(close["title"])}</h2>' if close.get('title') else ''}{f'<p>{esc(close["text"])}</p>' if close.get('text') else ''}{f'<div class="bs">{btns}</div>' if btns else ''}{f'<ul class="reach">{ls}</ul>' if ls else ''}</div>{pc}</div></section>''')

    locs = [l for l in (d.get('locations') or []) if l.get('name')]
    if locs:
        cols = []
        for l in locs:
            a = l.get('address') or {}
            adr = '<br>'.join(esc(x) for x in (a.get('street'), ' '.join(y for y in (a.get('postcode'), a.get('city')) if y), a.get('country')) if x)
            hrs = '<br>'.join(esc(' '.join(x for x in (hh.get('days'), ' – '.join(y for y in (hh.get('open'), hh.get('close')) if y)) if x)) for hh in (l.get('hours') or []))
            tel = f'<a href="tel:{esc(re.sub(r"[^0-9+]", "", l["phone"]))}">{esc(l["phone"])}</a>' if l.get('phone') else ''
            mail = f'<a href="mailto:{esc(l["email"])}">{esc(l["email"])}</a>' if l.get('email') else ''
            nm_ = f'<a class="ln2" href="{esc(l["h"])}">{esc(l["name"])}</a>' if l.get('h') else f'<span class="ln2">{esc(l["name"])}</span>'
            cols.append(f'''<div class="loc">{nm_}{f'<p>{adr}</p>' if adr else ''}{f'<p>{tel}{"<br>" if tel and mail else ""}{mail}</p>' if (tel or mail) else ''}{f'<p>{hrs}</p>' if hrs else ''}{f'<p class="no">{esc(l["note"])}</p>' if l.get('note') else ''}</div>''')
        out.append(f'<section class="locs"><div class="lc" data-r>{"".join(cols)}</div></section>')
    out.append('</main>')

    # ── 9 foot ──────────────────────────────────────────────────────────────────────────────────────────────────────
    foot = d.get('foot') or {}
    col2 = [l for l in (d.get('links') or []) if l.get('t') and l.get('h')] or nav
    seen, col3 = set(), []
    for l in (foot.get('links') or []) + (place.get('social') or []):
        if l.get('t') and l.get('h') and l['h'] not in seen: seen.add(l['h']); col3.append(l)
    flogo = f'<b>{esc(nm[0])}</b>{esc(" " + " ".join(nm[1:]) if len(nm) > 1 else "")}' if nm else ''
    nf = max(len(name) + .6, 6)
    out.append(f'''<footer class="foot"><div class="fgr" data-r><div class="f1"><div class="logo">{flogo}</div>{f'<p>{esc(foot["text"])}</p>' if foot.get('text') else ''}</div>
<div class="f2">{''.join(f'<a href="{esc(l["h"])}">{esc(l["t"])}</a>' for l in col2)}</div>
<div class="f2">{''.join(f'<a href="{esc(l["h"])}">{esc(l["t"])}</a>' for l in col3)}</div>
{f'<p class="lgl">{esc(foot["legal"])}</p>' if foot.get('legal') else ''}</div>
<div class="fw" aria-hidden="true" data-r style="--n:{nf:.1f}"><i class="fs"></i>{esc(name.lower())}<em>.</em></div></footer>''')

    title = name + (' — ' + hero['title'] if hero.get('title') else '')
    return f'''<!doctype html><html lang="{esc(lang)}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc((hero.get('text') or '')[:160])}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Figtree:wght@300;400;500;600;700&family=Forum&display=swap" rel="stylesheet">
<style>:root{{{css_vars}}}{CSS}</style></head><body>{''.join(out)}<script>{JS}</script></body></html>'''


CSS = r'''
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{margin:0;background:var(--D);color:var(--D);font:400 16px/1.4 Figtree,system-ui,sans-serif;overflow-x:clip;-webkit-font-smoothing:antialiased;--u:min(1vw,19.2px);--e:cubic-bezier(.2,.8,.2,1)}
img{display:block;max-width:100%}a{color:inherit;text-decoration:none}h1,h2,h3,p,ul{margin:0}ul{padding:0;list-style:none}
:focus-visible{outline:3px solid var(--D);outline-offset:2px;box-shadow:0 0 0 7px var(--L);border-radius:4px}.btn:focus-visible{border-radius:999px}
.ar:focus-visible{box-shadow:none}
.skip{position:absolute;left:12px;top:-60px;z-index:200;background:var(--D);color:var(--L);padding:12px 18px;border-radius:999px;font:600 15px/1 Figtree,sans-serif;transition:top .2s}.skip:focus{top:12px}
.btn{display:inline-flex;align-items:center;gap:10px;background:var(--D);color:var(--L);border:1px solid var(--D);border-radius:999px;padding:17px 28px;font:600 16px/1.1 Figtree,sans-serif;transition:transform .25s,background-color .25s,color .25s,border-color .25s;max-width:100%;text-align:center}
.btn:hover{transform:translateY(-2px)}.btn.sm{padding:14px 24px;font-size:14px}
.btn.ol{background:transparent;color:inherit;border-color:currentColor}.btn.wh{background:var(--L);color:var(--D);border-color:var(--L)}
.dot{color:var(--AonL)}
html.js [data-r]{opacity:0;transform:translateY(22px);transition:opacity .8s ease var(--dl,.08s),transform .8s var(--e) var(--dl,.08s)}
html.js [data-r].in{opacity:1;transform:none}
/* header: fixed, accent ground, 84 high (64 on a phone) */
.nav{position:fixed;inset:0 0 auto 0;z-index:50;height:84px;padding:0 56px;display:flex;align-items:center;justify-content:space-between;gap:24px;background:var(--A);color:var(--onA)}
.logo{font:400 34px/1 Figtree,sans-serif;letter-spacing:-.035em;white-space:nowrap;text-transform:lowercase}.logo b{font-weight:700}
.nl{display:flex;gap:34px;font:500 20px/1 Figtree,sans-serif;white-space:nowrap}.nl a{padding:4px 0 6px;border-bottom:2px solid transparent;transition:border-color .35s}.nl a:hover{border-color:currentColor}
.nav .nc{background:var(--onA);color:var(--A);border-color:var(--onA);font:500 20px/1 Figtree,sans-serif;padding:13px 24px;white-space:nowrap}
.nav .nc:hover{background:var(--A);color:var(--onA)}
.burger{display:none}
@media(max-width:1240px){.nl{gap:22px;font-size:17px}.logo{font-size:28px}.nav .nc{font-size:17px}}
@media(max-width:1020px){.nl,.nav .nc{display:none}.burger{display:block}
 .burger summary{list-style:none;width:44px;height:44px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;cursor:pointer}.burger summary::-webkit-details-marker{display:none}
 .burger summary i{width:24px;height:2px;border-radius:2px;background:currentColor;transition:transform .25s}
 .burger[open] summary i:nth-child(1){transform:translateY(8px) rotate(45deg)}.burger[open] summary i:nth-child(2){opacity:0}.burger[open] summary i:nth-child(3){transform:translateY(-8px) rotate(-45deg)}
 .burger nav{position:absolute;left:0;right:0;top:100%;background:var(--A);padding:8px 20px 28px;display:flex;flex-direction:column;gap:4px;font:300 28px/1.2 Figtree,sans-serif;letter-spacing:-.02em;max-height:calc(100vh - 64px);overflow:auto}
 .burger nav a{padding:10px 0}.burger nav .btn{align-self:flex-start;margin-top:12px;background:var(--onA);color:var(--A);border-color:var(--onA);font:600 16px/1.1 Figtree,sans-serif;letter-spacing:0;padding:16px 26px}}
/* first screen */
.hero{position:relative;background:var(--A);color:var(--onA);min-height:max(100vh,calc(var(--u)*62.5));padding-top:84px;overflow:hidden;display:flex;flex-direction:column}
.gw{position:relative;z-index:1;margin-top:-10px;text-align:center;font:300 calc(var(--u)*min(34,150/var(--n)))/.8 Figtree,sans-serif;letter-spacing:-.05em;color:var(--wordA);white-space:nowrap;height:calc(var(--u)*27.2);text-transform:lowercase}
.gw i,.cw i,.fw em{font-style:normal;color:var(--onA)}
.hg{flex:1;display:grid;grid-template-columns:1fr calc(var(--u)*44.5) 1fr;gap:36px;padding:0 56px;align-items:center;position:relative}
.hl,.hr{position:relative;z-index:3;padding-bottom:calc(var(--u)*8);display:flex;flex-direction:column;gap:14px}
.hero h1{font:300 calc(var(--u)*2.9)/1.1 Figtree,sans-serif;letter-spacing:-.02em;text-wrap:balance}
.hl p,.hr p{font:400 calc(var(--u)*1.45)/1.45 Forum,serif}.hl{grid-column:1}.hr{grid-column:3;max-width:340px;justify-self:end}
.arch{position:absolute;z-index:2;left:50%;bottom:0;transform:translateX(-50%);width:min(calc(var(--u)*44.5),var(--pw,9999px));height:min(calc(100% + var(--u)*4.6),var(--ph,9999px))}
.arch .hd{position:absolute;z-index:0;left:50%;bottom:0;transform:translateX(-50%);width:calc(var(--u)*52);aspect-ratio:2/1;border-radius:999px 999px 0 0;background:var(--D)}
.arch .win{position:absolute;inset:0;z-index:1;border-radius:999px 999px 0 0;overflow:hidden;background:var(--D2)}
.arch .win img{width:100%;height:100%;object-fit:cover}
.hero.nopic{min-height:0}.hero.nopic .hg{grid-template-columns:1fr 1fr;padding-top:calc(var(--u)*4)}.hero.nopic .hl,.hero.nopic .hr{padding-bottom:calc(var(--u)*7)}.hero.nopic .hr{grid-column:2}
/* statement */
.stmt{position:relative;background:var(--D);padding:0 56px calc(var(--u)*11.5);overflow:hidden}
.sun{position:absolute;left:50%;top:-1px;width:calc(var(--u)*74);aspect-ratio:2/1;border-radius:0 0 999px 999px;background:var(--A);margin-left:calc(var(--u)*-37)}
html.js .sun[data-r]{transform:none;transition:opacity .6s ease .08s}
.sw{position:relative;max-width:1100px;margin:0 auto;padding-top:56px;min-height:calc(var(--u)*33);display:flex;flex-direction:column;align-items:center}
.sw p{max-width:calc(var(--u)*62);text-align:center;font:300 calc(var(--u)*3.6)/1.12 Figtree,sans-serif;letter-spacing:-.03em;color:var(--onA);text-wrap:balance}.sw strong{font-weight:700}
.stmt.t1 .sw p{font-size:calc(var(--u)*3.05);max-width:calc(var(--u)*58)}.stmt.t2 .sw p{font-size:calc(var(--u)*2.5);max-width:calc(var(--u)*55)}
.lead{position:relative;max-width:760px;margin:calc(var(--u)*7) auto 0;text-align:center;font:400 22px/1.55 Forum,serif;color:var(--LsD)}
.stmt.bare{padding-top:100px}.stmt.bare .lead{margin-top:0}
/* heading */
.hd2{background:var(--D);color:var(--L);padding:calc(var(--u)*2) 56px 80px;text-align:center}.hd2>div{display:flex;flex-direction:column;align-items:center;gap:18px}
.hd2 h2{font:300 calc(var(--u)*4.4)/1 Figtree,sans-serif;letter-spacing:-.035em;max-width:900px;text-wrap:balance}.hd2 p{font:400 26px/1.55 Forum,serif;color:var(--LsD);max-width:640px}
/* cards */
.cards{background:var(--D);padding:0 20px;display:grid;grid-template-columns:1fr 1fr;gap:20px}
.card{position:relative;border-radius:32px;overflow:hidden;min-width:0}
.card.ac{background:var(--A);color:var(--onA)}.card.dk{background:var(--D2);color:var(--L)}
.ct{display:flex;flex-direction:column;align-items:center;text-align:center;padding:calc(var(--u)*5) 0 calc(var(--u)*5.2);height:100%}
.ct>*{margin-left:calc(var(--u)*3);margin-right:calc(var(--u)*3)}
.cw{font:300 calc(var(--u)*min(17,74/var(--n)))/.8 Figtree,sans-serif;letter-spacing:-.05em;white-space:nowrap;height:calc(var(--u)*13.6);text-transform:lowercase;color:var(--wordA)}
.card.dk .cw{color:var(--L)}.card.dk .cw i{color:var(--AonD2)}
.cp{align-self:stretch;margin:calc(var(--u)*1) 0 0!important;height:calc(var(--u)*33.3);max-height:640px;overflow:hidden}.cp img{width:100%;height:100%;object-fit:cover}
.meta{margin-top:calc(var(--u)*3.3);font:400 18px/1.3 Forum,serif;color:var(--onAs)}.card.dk .meta{color:var(--LsD2)}
.card h3{margin-top:14px;font:300 calc(var(--u)*2.8)/1.04 Figtree,sans-serif;letter-spacing:-.03em;max-width:520px}.cp+h3,.cw+h3{margin-top:calc(var(--u)*3.3)}
.card p{margin-top:14px;font:400 22px/1.55 Forum,serif;max-width:520px}.card.dk p{color:var(--LsD2)}
.bs{display:flex;flex-wrap:wrap;gap:10px;margin-top:22px}.ct .bs{justify-content:center}
.card.ac .btn{background:var(--onA);color:var(--A);border-color:var(--onA)}.card.dk .btn{background:var(--AonD2);color:var(--D);border-color:var(--AonD2)}
.card.wide{grid-column:1/-1}.card.wide.pic{display:grid;grid-template-columns:1fr 1fr}.card.wide .cp{margin:0!important;height:100%;min-height:calc(var(--u)*36);max-height:none}
/* band */
.band{background:var(--D);padding:20px}
.bi{position:relative;border-radius:32px;overflow:hidden;background:var(--D3);aspect-ratio:var(--ar);min-height:560px;max-height:1000px;width:100%}
.bi img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;filter:brightness(.72)}
.veil{position:absolute;inset:0;background:linear-gradient(rgba(var(--Drgb),.1) 30%,rgba(var(--Drgb),.9) 100%),linear-gradient(0deg,rgba(0,0,0,.6),rgba(0,0,0,0) 62%)}
.bt{position:absolute;inset:auto 0 0 0;padding:56px;display:flex;align-items:flex-end;justify-content:space-between;gap:32px}
.bt p{max-width:1100px;font:300 calc(var(--u)*6)/.98 Figtree,sans-serif;letter-spacing:-.04em;color:#fff;text-wrap:balance}.bt p span{color:var(--Aband,#fff)}
.bt .btn{flex:none;background:#fff;color:#000;border-color:#fff}
/* figures + shelf */
.voices{background:var(--A);color:var(--onA);padding:140px 56px;overflow:hidden}
.fgs{display:grid;grid-template-columns:repeat(var(--k),minmax(0,1fr));gap:24px 40px;margin-bottom:56px}
.fg{display:flex;align-items:flex-start;gap:14px;font:400 18px/1.3 Forum,serif;min-width:0}.fg b{font:300 44px/1 Figtree,sans-serif;letter-spacing:-.04em;white-space:nowrap}.fg span{padding-top:3px;max-width:260px}
.accw{container-type:inline-size;--open:calc((100cqw - (var(--n) - 1)*12px)*10/(9 + var(--n)))}
.ar{position:absolute;opacity:0;width:1px;height:1px;pointer-events:none}
.acc{display:flex;gap:12px;align-items:stretch;min-height:520px}
.it{position:relative;flex:1 1 0;min-width:0;border-radius:24px;overflow:hidden;background:var(--sp1);color:var(--sp1t);transition:flex .7s var(--e),background .5s,color .5s}
.it:nth-child(even){background:var(--sp2);color:var(--sp2t)}
.voices{--sp1:var(--spA);--sp1t:var(--spAt);--sp2:var(--L);--sp2t:var(--D);--opbg:var(--D);--opt:var(--L);--opa:var(--AonD);--ops:var(--LsD)}
.light{--sp1:var(--spL);--sp1t:var(--D);--sp2:var(--A);--sp2t:var(--onA);--opbg:var(--D);--opt:var(--L);--opa:var(--AonD);--ops:var(--LsD)}
.spine{position:absolute;inset:0;z-index:2;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:22px 0;cursor:pointer}
.spine span{writing-mode:vertical-rl;transform:rotate(180deg);font:500 14px/1 Figtree,sans-serif;letter-spacing:.14em;text-transform:uppercase;white-space:nowrap;max-height:calc(100% - 40px);overflow:hidden}
.spine i{position:absolute;bottom:22px;width:8px;height:8px;border-radius:50%;background:currentColor;opacity:.35}
.pan{width:var(--open);min-height:520px;padding:calc(var(--u)*3);display:flex;flex-direction:column;justify-content:space-between;gap:20px;visibility:hidden;opacity:0}
.it.hp .pan{width:calc(var(--open)*.6)}
.pp{position:absolute;top:0;bottom:0;left:calc(var(--open)*.6);width:calc(var(--open)*.4);visibility:hidden;opacity:0}.pp img{width:100%;height:100%;object-fit:cover}
.pt{display:flex;justify-content:space-between;gap:16px;font:400 18px/1.3 Forum,serif;min-height:23px}.pa{color:var(--opa)}.pb{color:var(--ops);text-align:right}
.pan p{font:400 calc(var(--u)*2.1)/1.35 Forum,serif;max-width:820px}.pan p.q1{font-size:max(19px,calc(var(--u)*1.55));line-height:1.42}.pan p.q2{font-size:18px;line-height:1.45}
.pan q{quotes:auto}
.pf{display:flex;flex-wrap:wrap;gap:6px 20px;align-items:baseline;font:400 17px/1.3 Forum,serif}.pf b{font:600 15px/1.2 Figtree,sans-serif;color:var(--opa)}.pf a{text-decoration:underline;text-underline-offset:3px}
.dots{display:flex;gap:8px;margin-top:20px}.dots label{width:8px;height:8px;border-radius:999px;background:currentColor;opacity:.3;cursor:pointer;transition:width .4s,opacity .4s}
.ar:focus-visible~.acc{outline:3px solid var(--D);outline-offset:4px;box-shadow:0 0 0 9px var(--L);border-radius:24px}
/* ledgers */
.light{background:var(--L);color:var(--D);padding:100px 56px}.light+.light{padding-top:0}
.lh{display:flex;flex-direction:column;gap:22px;margin-bottom:64px}.lh h2,.lg.big .ll h2{font:300 calc(var(--u)*5.4)/1 Figtree,sans-serif;letter-spacing:-.035em;text-wrap:balance}
.lh p,.ll p{font:400 21.6px/1.5 Forum,serif;max-width:480px}.lh p{max-width:640px}
.lg{display:grid;grid-template-columns:1fr 1fr;gap:calc(var(--u)*6);align-items:start}.lg+.lg,.lh+.accw,.accw+.lg{margin-top:72px}.lg+.lh,.accw+.lh{margin-top:100px}
.ll{position:sticky;top:110px;display:flex;flex-direction:column;align-items:flex-start;gap:22px;min-width:0}
.ll h3{font:300 calc(var(--u)*3.6)/1.02 Figtree,sans-serif;letter-spacing:-.03em;text-wrap:balance}
.ll .tr{font:300 clamp(21px,calc(var(--u)*1.9),28px)/1.25 Figtree,sans-serif;letter-spacing:-.02em;max-width:520px;padding-bottom:22px;border-bottom:1px solid rgba(var(--Drgb),.12);width:100%}.ll .tr:last-child{border:0}
.lr{display:flex;flex-direction:column;min-width:0}.lg.one{display:block}.lr.two{display:grid;grid-template-columns:1fr 1fr;column-gap:calc(var(--u)*6)}
.fc{background:var(--A);color:var(--onA);border-radius:28px;padding:36px;margin-bottom:20px;display:flex;flex-direction:column;gap:18px}
.fc.q{background:var(--spL);color:var(--D)}.fc.q .btn{background:var(--D);color:var(--L)}
.ft{display:flex;justify-content:space-between;gap:16px;font:400 17px/1.2 Forum,serif}.ft span:last-child{color:var(--onAs);text-align:right}.fc.q .ft span:last-child{color:var(--DsQ)}
.fh{font:300 calc(var(--u)*3)/1.05 Figtree,sans-serif;letter-spacing:-.03em;overflow-wrap:anywhere}.fc p{font:400 21.6px/1.5 Forum,serif}
.fc ul{display:flex;flex-direction:column;gap:6px;font:400 18px/1.4 Forum,serif}.fc li{padding-left:18px;position:relative}.fc li::before{content:"";position:absolute;left:0;top:.6em;width:6px;height:6px;border-radius:50%;background:currentColor}
.fc .btn{background:var(--onA);color:var(--A);border-color:transparent}.fl{display:inline-flex;gap:8px;font:600 14px/1.2 Figtree,sans-serif;overflow-wrap:anywhere}.fl+.fl{margin-top:-6px}
.row{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:20px;align-items:baseline;padding:16px 0;border-top:1px solid rgba(var(--Drgb),.12);transition:padding-left .3s}
a.row:hover{padding-left:12px}.row.l3{grid-template-columns:52px minmax(0,1fr) auto}
.rl{font:400 17px/1 Forum,serif;color:var(--AonL);align-self:start;padding-top:6px}.rl img{width:52px;height:auto}
.rt{display:block;font:300 clamp(21px,calc(var(--u)*1.9),28px)/1.15 Figtree,sans-serif;letter-spacing:-.02em}
.rs{display:block;margin-top:6px;font:400 17px/1.45 Forum,serif;color:var(--DsL)}.ri{display:block}
.rr{font:400 19px/1.3 Forum,serif;text-align:right;max-width:240px;overflow-wrap:anywhere}.pl{display:block}.pl em{font-style:normal;color:var(--DsL)}
.ln{margin-top:28px;font:400 17px/1.5 Forum,serif;color:var(--DsL);max-width:720px}
.ar2{font-weight:600}
/* question rows */
.qa{background:var(--D);color:var(--L);padding:43px 56px calc(var(--u)*8)}.qa+.qa{padding-top:0}
.qi{position:relative;max-width:1200px;margin:0 auto;padding-top:72px;display:flex;align-items:flex-start;gap:72px}
.qi::before{content:"";position:absolute;left:0;right:0;top:0;height:1px;background:linear-gradient(90deg,rgba(var(--Lrgb),0),rgba(var(--Lrgb),.35) 20%,rgba(var(--Lrgb),.35) 80%,rgba(var(--Lrgb),0))}
.ql{flex:1 1 300px;display:flex;flex-direction:column;gap:18px;min-width:0}.ql h2{font:300 calc(var(--u)*4.2)/1.02 Figtree,sans-serif;letter-spacing:-.035em;text-wrap:balance}
.ql p,.an p{font:400 21.6px/1.55 Forum,serif;color:var(--LsD)}
.qr{flex:2 1 520px;min-width:0;border-top:1px solid rgba(var(--Lrgb),.2)}.qr details,.qr .nd{border-bottom:1px solid rgba(var(--Lrgb),.2)}
.qr summary,.qr .nd{list-style:none;display:flex;align-items:center;justify-content:space-between;gap:24px;padding:28px 0;cursor:pointer}.qr .nd{cursor:default}.qr summary::-webkit-details-marker{display:none}
.qr h3{font:300 clamp(21px,calc(var(--u)*1.9),28px)/1.25 Figtree,sans-serif;letter-spacing:-.02em}
.qr summary i{flex:none;position:relative;width:42px;height:42px;border-radius:999px;border:1px solid rgba(var(--Lrgb),.35);transition:background-color .3s,border-color .3s,color .3s}
.qr summary i::before,.qr summary i::after{content:"";position:absolute;left:50%;top:50%;width:14px;height:1.5px;margin:-.75px 0 0 -7px;background:currentColor;transition:transform .3s}
.qr summary i::after{transform:rotate(90deg)}.qr details[open] summary i::after{transform:rotate(0)}
.qr summary:hover i{background:var(--L);color:var(--D)}
.an{padding:0 58px 30px 0}
/* closing pair */
.pair{background:var(--D);padding:20px 20px 0}
.pg{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,min(1fr,var(--pw,4000px)));grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:20px;align-items:stretch}.pg.solo{grid-template-columns:1fr}
.pg[style*="--pw"]{grid-template-columns:minmax(0,1fr) min(calc(50% - 10px),var(--pw))}
.inv{background:var(--A);color:var(--onA);border-radius:32px;padding:calc(var(--u)*4.5) calc(var(--u)*3);display:flex;flex-direction:column;justify-content:center;gap:14px;min-height:calc(var(--u)*40)}
.pg.solo .inv{min-height:0;padding:calc(var(--u)*6) calc(var(--u)*3)}
.inv h2{font:300 calc(var(--u)*4.4)/1 Figtree,sans-serif;letter-spacing:-.035em;text-wrap:balance}.inv>p{font:400 26px/1.5 Forum,serif;max-width:560px}
.inv .btn{background:var(--onA);color:var(--A);border-color:var(--onA)}.inv .btn.ol{background:transparent;color:var(--onA)}.inv .bs{margin-top:8px}
.reach{margin-top:18px;display:flex;flex-direction:column;font:400 20px/1.4 Forum,serif;max-width:560px}.reach li{display:flex;flex-wrap:wrap;justify-content:space-between;gap:2px 20px;padding:10px 0;border-top:1px solid color-mix(in srgb,var(--onA) 22%,transparent)}
.reach a{text-decoration:underline;text-underline-offset:3px;overflow-wrap:anywhere}.reach em{font-style:normal;color:var(--onAs)}
.pcard{position:relative;border-radius:32px;overflow:hidden;background:var(--D2);min-height:320px;max-height:var(--ph)}.pcard img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.locs{background:var(--D);color:var(--L);padding:100px 56px 0}.lc{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:48px}
.loc{display:flex;flex-direction:column;gap:12px;font:400 17.3px/1.5 Forum,serif;color:var(--LsD)}.ln2{font:500 19px/1 Figtree,sans-serif;color:var(--L);margin-bottom:6px}.loc a:not(.ln2){text-decoration:underline;text-underline-offset:3px}
/* foot */
.foot{background:var(--D);color:var(--L);padding:140px 56px 0;overflow:hidden}
.fgr{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:48px;padding-bottom:100px;align-items:start}
.f1{display:flex;flex-direction:column;gap:28px}.foot .logo{font-size:36px;white-space:normal}.foot .logo b{color:var(--AonD)}.f1 p{font:400 17.3px/1.5 Forum,serif;color:var(--LsD)}
.f2{display:flex;flex-direction:column;gap:14px;font:500 19px/1 Figtree,sans-serif}.f2 a:hover{color:var(--AonD)}
.lgl{grid-column:1/-1;font:400 15.8px/1.5 Forum,serif;color:var(--LsD);max-width:860px}
.fw{position:relative;z-index:0;text-align:center;font:300 calc(var(--u)*min(17,172/var(--n)))/.9 Figtree,sans-serif;letter-spacing:-.05em;white-space:nowrap;height:1.02em;color:var(--L)}
.fw em{font-style:normal;color:var(--AonD)}
.fs{position:absolute;z-index:-1;left:50%;top:-.06em;width:calc(var(--u)*40.8);aspect-ratio:2/1;margin-left:calc(var(--u)*-20.4);border-radius:999px 999px 0 0;background:var(--A)}
.fw{text-shadow:none}
/* phone build (the reference at 390) */
@media(max-width:820px){
 .nav{height:64px;padding:0 20px}.logo{font-size:24px}
 .hero{padding-top:64px;min-height:0;display:block}
 .gw{height:27.2vw;padding:0 20px}
 .hg{display:flex;flex-direction:column;align-items:stretch;gap:0;padding:0}
 .arch{position:relative;order:-1;left:auto;bottom:auto;transform:none;margin:-4vw auto 0;width:min(88vw,var(--pw,9999px));height:min(102vw,var(--ph,9999px))}
 .arch .hd{width:114vw}.hero.nopic .hg{padding-top:0}
 .hl,.hr{padding:28px 20px 0;max-width:none;justify-self:auto}.hr{padding:14px 20px 40px}.hl:last-child{padding-bottom:40px}
 .hero h1{font-size:9vw;line-height:1.04;letter-spacing:-.035em}.hl p,.hr p{font-size:18.7px;line-height:1.5}
 .stmt{padding:0 20px 56px}.sun{width:150vw;margin-left:-75vw}.stmt.t1 .sun{width:190vw;margin-left:-95vw}.stmt.t2 .sun{width:240vw;margin-left:-120vw}
 .sw{padding-top:8px;min-height:75vw}.stmt.t1 .sw{min-height:95vw}.stmt.t2 .sw{min-height:120vw}
 .sw p,.stmt.t1 .sw p,.stmt.t2 .sw p{font-size:5.6vw;line-height:1.1;max-width:78vw}.stmt.t2 .sw p{font-size:5vw}
 .lead{font-size:18.7px;margin-top:48px}
 .hd2{padding:8px 20px 32px}.hd2 h2{font-size:9vw;line-height:1.04}.hd2 p{font-size:18.7px}
 .cards{grid-template-columns:1fr;padding:0 12px;gap:12px}.ct{padding:40px 0 44px}.ct>*{margin-left:20px;margin-right:20px}
 .cw{font-size:calc(1vw*min(34,150/var(--n)));height:27.2vw}.cp{height:62vw;margin-top:8px!important}.meta{margin-top:28px}.cp+h3,.cw+h3{margin-top:28px}
 .card h3{font-size:26px}.card p{font-size:18.7px}.card.wide.pic{display:block}.card.wide .cp{height:62vw;min-height:0}
 .band{padding:12px}.bi{aspect-ratio:auto;min-height:0;height:max(420px,108vw)}.bt{padding:28px;flex-direction:column;align-items:flex-start;gap:20px}.bt p{font-size:9vw;line-height:1.04}
 .voices{padding:56px 20px}.fgs{grid-template-columns:1fr;margin-bottom:32px}.fg span{max-width:none}
 .acc{flex-direction:column;min-height:0}.it{flex:none;min-height:64px}.spine{flex-direction:row;justify-content:flex-start;gap:12px;padding:0 20px}
 .spine span{writing-mode:horizontal-tb;transform:none;max-height:none;max-width:calc(100% - 30px);text-overflow:ellipsis;line-height:1.3}.spine i{position:static}
 .pan,.it.hp .pan{display:none;width:auto;min-height:460px;padding:24px}.it.hp .pan{min-height:0}.pan p,.pan p.q1,.pan p.q2{font-size:18.7px;line-height:1.4}
 .pp{position:relative;left:auto;width:100%;height:78vw;display:none}
 .light{padding:56px 20px}.lh{margin-bottom:36px}.lh h2,.lg.big .ll h2{font-size:9vw;line-height:1.04}.lh p,.ll p,.fc p{font-size:18.7px}
 .lg{grid-template-columns:1fr;gap:32px}.lg+.lg,.lh+.accw,.accw+.lg{margin-top:48px}.lg+.lh,.accw+.lh{margin-top:64px}.ll{position:static}.ll h3{font-size:30px}.lr.two{grid-template-columns:1fr}
 .fc{padding:24px}.fh{font-size:30px}.row{grid-template-columns:1fr}.row.l3{grid-template-columns:52px minmax(0,1fr)}.rr{text-align:left;max-width:none}.row.l3 .rr{grid-column:2}
 .qa{padding:24px 20px 64px}.qi{flex-direction:column;gap:28px;padding-top:40px}.ql,.qr{flex:none;width:100%}.ql h2{font-size:9vw;line-height:1.04}.ql p,.an p{font-size:18.7px}.qr h3{font-size:24px}.an{padding-right:0}
 .pair{padding:12px 12px 0}.pg,.pg[style*="--pw"]{grid-template-columns:1fr;gap:12px}.inv,.pg.solo .inv{padding:40px 28px;min-height:0}.inv h2{font-size:8vw;line-height:1.06}.inv>p{font-size:18.7px}.reach{font-size:18px}
 .pcard{height:min(95vw,var(--ph));width:min(100%,var(--pw));margin:0 auto}
 .locs{padding:56px 20px 0}.lc{grid-template-columns:1fr;gap:36px}
 .foot{padding:64px 20px 0}.fgr{grid-template-columns:1fr;gap:36px;padding-bottom:56px}.foot .logo{font-size:30px}.f1 p{font-size:18.7px}
 .fw{font-size:calc(1vw*min(17,172/var(--n)))}.fs{width:40.8vw;margin-left:-20.4vw}
}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*,*::before,*::after{transition:none!important;animation:none!important}html.js [data-r]{opacity:1;transform:none}}
'''
# the open item of each shelf, by position (radio inputs stand before the shelf, so the rule is written per index)
CSS += ''.join(
    f'.ar:nth-of-type({i}):checked~.acc .it:nth-child({i}){{flex:10 1 0;background:var(--opbg);color:var(--opt)}}'
    f'.ar:nth-of-type({i}):checked~.acc .it:nth-child({i}) .spine{{opacity:0;pointer-events:none}}'
    f'.ar:nth-of-type({i}):checked~.acc .it:nth-child({i}) .pan,.ar:nth-of-type({i}):checked~.acc .it:nth-child({i}) .pp{{visibility:visible;opacity:1;transition:opacity .5s ease .25s}}'
    f'.ar:nth-of-type({i}):checked~.dots label:nth-child({i}){{width:28px;opacity:1}}'
    f'@media(max-width:820px){{.ar:nth-of-type({i}):checked~.acc .it:nth-child({i}){{flex:none}}.ar:nth-of-type({i}):checked~.acc .it:nth-child({i}) .pan{{display:flex}}.ar:nth-of-type({i}):checked~.acc .it:nth-child({i}) .pp{{display:block}}.ar:nth-of-type({i}):checked~.acc .it:nth-child({i}) .spine{{display:none}}}}'
    for i in range(1, 11))

JS = r'''
(function(){var h=document.documentElement,rm=matchMedia('(prefers-reduced-motion: reduce)').matches;h.classList.add('js');
var els=[].slice.call(document.querySelectorAll('[data-r]'));
if(!('IntersectionObserver' in window)||rm){els.forEach(function(e){e.classList.add('in')})}
else{var io=new IntersectionObserver(function(en){en.forEach(function(x){if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target)}})},{rootMargin:'0px 0px -4% 0px'});els.forEach(function(e){io.observe(e)})}
/* the shelf moves on by itself about every 5.3 s (measured), while it is on screen */
if(!rm)[].forEach.call(document.querySelectorAll('[data-acc]'),function(w){var r=w.querySelectorAll('.ar');if(r.length<2)return;var on=false,t;
 function go(){clearInterval(t);t=setInterval(function(){if(!on||document.hidden)return;var i=0;for(var k=0;k<r.length;k++)if(r[k].checked)i=k;r[(i+1)%r.length].checked=true},5300)}
 if('IntersectionObserver' in window)new IntersectionObserver(function(e){on=e[0].isIntersecting},{threshold:.4}).observe(w);else on=true;
 w.addEventListener('change',go);go()});
/* the phone menu closes when a link in it is taken */
var b=document.querySelector('.burger');if(b)b.addEventListener('click',function(e){if(e.target.closest('nav a'))b.open=false});
})();
'''
