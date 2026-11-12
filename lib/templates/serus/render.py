"""serus/render.py — one pure function: render(d) -> a complete page built to the measures of the reference home page
(a quiet near-white ground, a 52px sticky bar, a centred serif line over one rounded ask-box, a slow trust row, very
large rounded picture cards each followed by a small centred row of points, a three-column tile grid, a link foot and a
small dark card that rises from the corner after the first scroll). No client, no model call, no network at render."""
import html, json, math

M = '../../'
SANS = 'Geist'           # the reference's own sans is open-licence (SIL OFL) and on Google Fonts
SERIF = 'Newsreader'     # open-licence stand-in for the reference's commercial soft serif (one 40px line)


def e(s):
    return html.escape(str(s or ''), quote=True)


# ---------- colour: the client's palette goes in, the reference's relations are kept ----------
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


def colours(p):
    G, I, A = p.get('ground', '#fafafa'), p.get('ink', '#0d0d0d'), p.get('accent', '#b8a4f8')
    dark = lum(G) < .2
    box = mix(G, I, .06) if dark else mix(G, '#ffffff', .8)      # the ask-box: one step lighter than the ground
    chip = mix(G, I, .07 if dark else .05)                       # 242 on 250
    pill = mix(G, I, .12 if dark else .08)                       # 235 on 250
    line = mix(G, I, .14 if dark else .09)
    grounds = (G, box, chip, pill)
    sec = mix(I, G, .3)                                          # the reference's 70% ink
    ter = I
    for t in (.55, .5, .45, .4, .35, .3, .25, .2):               # its 45% ink, held at 4.5:1 on every ground it meets
        m = mix(I, G, t)
        if min(con(m, g) for g in grounds) >= 4.6:
            ter = m
            break
    if min(con(sec, g) for g in grounds) < 4.6:
        sec = ter
    Dk, Lt = (G, I) if dark else (I, G)                          # darkest and lightest of the pair
    return dict(G=G, I=I, A=A, box=box, chip=chip, pill=pill, line=line, sec=sec, ter=ter, dark=dark,
                onA=best(A, Dk, Lt, '#171717'), Ahov=mix(A, '#ffffff', .3), Ihov=mix(I, G, .38),
                tint=mix(G, A, .16 if dark else .12), Dk=Dk, Lt=Lt, pillhov=mix(G, I, .2 if dark else .14))


ARROW = ('<svg viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.5" '
         'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4"/></svg>')
UP = ('<svg viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.5" '
      'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 13V3M4 7l4-4 4 4"/></svg>')
CHEV = ('<svg class="chev" viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2" '
        'aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>')
CLOSE = ('<svg viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.5" '
         'stroke-linecap="round" aria-hidden="true"><path d="M4 4l8 8M12 4l-8 8"/></svg>')


def split(items, n):
    """items shared out over n groups in order, as evenly as they go (7 over 3 -> 3,2,2)."""
    if not n:
        return []
    q, r = divmod(len(items), n)
    out, i = [], 0
    for k in range(n):
        m = q + (1 if k < r else 0)
        out.append(items[i:i + m])
        i += m
    return out


def render(d: dict) -> str:
    c = colours(d.get('palette') or {})
    brand = d.get('brand') or {}
    name = brand.get('name', '')
    hero = d.get('hero') or {}
    media = d.get('media') or {}
    made = media.get('made') or {}
    lands = made.get('land') or []
    nav = d.get('nav') or []
    signin, cta = d.get('signin') or {}, d.get('cta') or {}
    close = d.get('close') or {}
    ccta = close.get('cta') or {}
    prim, secd = hero.get('primary') or cta, hero.get('secondary') or {}

    def logo(h, cls=''):
        if not brand.get('logo'):
            return f'<span class="bname">{e(name)}</span>'
        img = f'<img class="{"wm" if brand.get("logo_wordmark") else "lm"}" src="{M}{e(brand["logo"])}" alt="{e(name) if brand.get("logo_wordmark") else ""}" style="height:{h}px;width:auto">'
        return img if brand.get('logo_wordmark') else img + f'<span class="bname">{e(name)}</span>'

    # ---- 0 bar ----
    dark_pill = ccta if ccta.get('t') and ccta.get('t') != cta.get('t') and ccta.get('h') != cta.get('h') else {}
    navl = ''.join(f'<li><a href="{e(n.get("h"))}">{e(n.get("t"))}</a></li>' for n in nav)
    mrows = ''.join(f'<li><a href="{e(n.get("h"))}">{e(n.get("t"))}</a></li>' for n in nav)
    mdark = secd if secd.get('t') else dark_pill
    bar = f'''<header class="bar"><nav class="barin" aria-label="Main">
<div class="bl"><a class="brand" href="{e(brand.get('home') or '#')}">{logo(24)}</a>{f'<ul class="links">{navl}</ul>' if navl else ''}</div>
<div class="br">{f'<a class="txt" href="{e(signin.get("h"))}">{e(signin.get("t"))}</a>' if signin.get('t') else ''}{f'<a class="pl pl-d" href="{e(dark_pill.get("h"))}">{e(dark_pill.get("t"))}</a>' if dark_pill else ''}{f'<a class="pl pl-a" href="{e(cta.get("h"))}">{e(cta.get("t"))}</a>' if cta.get('t') else ''}
<details class="menu"><summary aria-label="Menu"><span class="mi"></span></summary><div class="panel">{f'<ul>{mrows}</ul>' if mrows else ''}
{f'<a class="btn btn-d wide" href="{e(mdark.get("h"))}">{e(mdark.get("t"))}</a>' if mdark.get('t') else ''}{f'<a class="btn btn-o wide" href="{e(signin.get("h"))}">{e(signin.get("t"))}</a>' if signin.get('t') else ''}</div></details></div>
</nav></header>'''

    # ---- 1 opening: mark, one serif line that changes, the ask-box, a small note ----
    title = hero.get('title') or name
    lines = [title] + [s for s in (hero.get('kicker'), hero.get('text')) if s and len(s) <= 64 and s != title]
    longest = max(len(s) for s in lines)
    rows_d = max(1, math.ceil(longest / 38))        # ~38 characters of the serif at 40px fill the 672 column
    rows_m = max(1, math.ceil(longest / 24))        # ~24 at 30.4px fill 358
    steps = d.get('steps') or {}
    sitems = steps.get('items') or []
    feats = d.get('features') or {}
    fitems = feats.get('items') or []
    # the box is a display, not a field: each line is a step's short name over its title, in the page's ink, changed by
    # a fade (nothing is typed, no caret, nothing in it takes focus but its two links)
    asks = [[s.get('k') or '', s.get('title')] for s in sitems if s.get('title')] or [['', f.get('t')] for f in fitems if f.get('t')][:4]
    mark = '' if brand.get('logo_wordmark') or not brand.get('logo') else f'<img class="mark" src="{M}{e(brand["logo"])}" alt="">'
    ask = ''
    if prim.get('t'):
        ask = f'''<div class="ask">
{f'<p class="shown{" lab" if any(a[0] for a in asks) else ""}" data-shown>{f"<small>{e(asks[0][0])}</small>" if asks[0][0] else ""}<span>{e(asks[0][1])}</span></p>' if asks else ''}
<div class="askrow">{f'<a class="chipb" href="{e(secd.get("h"))}">{e(secd.get("t"))}</a>' if secd.get('t') else ''}<a class="send" href="{e(prim.get('h'))}"><span>{e(prim.get('t'))}</span>{ARROW}</a></div></div>'''
    opening = f'''<section class="open" style="--rd:{rows_d};--rm:{rows_m}"><div class="col">
<div class="h1w"><h1 aria-label="{e(title)}">{mark}<span class="line" data-lines='{e(json.dumps(lines, ensure_ascii=False))}'>{e(title)}</span></h1></div>
{ask}{f'<p class="note">{e(hero.get("note"))}</p>' if hero.get('note') else ''}</div></section>'''

    # ---- 2 trust row: marks if the client has them, otherwise its own short lines of proof ----
    logos, trust = d.get('logos') or [], d.get('trust') or []
    if logos:
        cells = ''.join(f'<li><img src="{M}{e(l.get("src"))}" alt="{e(l.get("alt"))}" style="height:24px;width:auto"></li>' if isinstance(l, dict) else f'<li>{e(l)}</li>' for l in logos)
    else:
        cells = ''.join(f'<li>{e(t)}</li>' for t in trust)
    row = f'<div class="trust"><div class="run"><ul>{cells}</ul><ul aria-hidden="true">{cells}</ul></div></div>' if cells else ''

    # ---- 3 picture cards, each followed by its row of points ----
    def head(t, x, tag='h2'):
        if not t:
            return ''
        return f'<div class="hd"><div><{tag} class="h28">{e(t)}</{tag}>{f"<p>{e(x)}</p>" if x else ""}</div></div>'

    groups = split(fitems, len(sitems)) if sitems else []
    order = [3, 4, 1, 5, 2, 0]
    cards = ''
    for i, s in enumerate(sitems):
        pic = lands[order[i % len(order)] % len(lands)] if lands else None
        tone = (pic or {}).get('tone') or ('dark' if c['dark'] else 'light')
        mean = (pic or {}).get('mean') or c['chip']
        ink, veil = ('#ffffff', '0,0,0') if tone == 'dark' else (c['Dk'], ','.join(str(v) for v in _rgb(c['Lt'])))
        pb, pf = (c['I'], c['G']) if con(c['I'], mean) >= con(c['G'], mean) else (c['G'], c['I'])
        ct = s.get('cta') or {}
        shot = ''
        if s.get('img'):
            alt = next((m.get('alt') for k in ('phones', 'screens', 'photos') for m in media.get(k) or [] if m.get('src') == s['img']), s.get('title'))
            shot = f'<span class="shot sh-{e(s.get("shape") or "screen")}"><img src="{M}{e(s["img"])}" alt="{e(alt)}" loading="lazy"></span>'
        else:
            shot = '<span class="shot"></span>'
        inner = f'''{f'<img class="bg" data-slot="card-backdrop" src="{M}{e(pic["src"])}" alt="" loading="lazy">' if pic else '<span class="bg" data-slot="card-backdrop"></span>'}<span class="veil"></span>
{f'<span class="cpill">{e(ct.get("t"))}<i>{ARROW}</i></span>' if ct.get('t') else '<span></span>'}{shot}
<span class="ctx"><h3 class="ch">{e(s.get('title'))}</h3>{f'<span class="cp">{e(s.get("text"))}</span>' if s.get('text') else ''}</span>'''
        style = f'--ci:{ink};--cv:{veil};--pb:{pb};--pf:{pf};--cm:{mean}'
        card = f'<a class="card" href="{e(ct.get("h"))}" style="{style}">{inner}</a>' if ct.get('h') else f'<div class="card" style="{style}">{inner}</div>'
        pts = ''.join(f'<div class="pt"><h4>{e(f.get("t"))}</h4><p>{e(f.get("d"))}</p></div>' for f in groups[i])
        cards += f'<div class="grp">{card}{f"""<div class="pts">{pts}</div>""" if pts else ""}</div>'
    if not sitems and fitems:
        pts = ''.join(f'<div class="pt"><h4>{e(f.get("t"))}</h4><p>{e(f.get("d"))}</p></div>' for f in fitems)
        cards = f'<div class="grp"><div class="pts">{pts}</div></div>'
    body2 = ''
    if row or cards:
        body2 = f'<section class="main2">{row}{head(steps.get("title"), steps.get("text")) if cards else ""}{f"""<div class="grps">{cards}</div>""" if cards else ""}</section>'

    # ---- 4 tile grid: the client's figures (the reference sets one of its tiles as a large grey figure) ----
    def tile(v):
        k = min(27, 130 / max(1, len(str(v))))
        return f'<span class="tile"><b style="font-size:{k:.1f}cqw">{e(v)}</b></span>'

    figs = d.get('figures') or []
    st = d.get('statement') or {}
    figsec = ''
    if figs or st.get('title'):
        g = ''.join(f'<div class="art">{tile(f.get("v"))}<h3>{e(f.get("l"))}</h3></div>' for f in figs)
        figsec = f'<section class="news">{head(st.get("title"), st.get("text"))}{f"""<div class="grid g{len(figs) if len(figs) in (4, 8) else 3}">{g}</div>""" if g else ""}</section>'

    # ---- 5 plans, set in the same tile grid ----
    plans = d.get('plans') or {}
    pitems = plans.get('items') or []
    plansec = ''
    if pitems:
        g = ''
        for p in pitems:
            rows = ''.join(f'<li>{e(r)}</li>' for r in p.get('rows') or [])
            pc = p.get('cta') or {}
            sub = ' · '.join(x for x in (p.get('per'),) if x)
            g += f'''<div class="art plan">{tile(p.get('price'))}<h3>{e(p.get('name'))}</h3>{f'<p class="when">{e(sub)}</p>' if sub else ''}{f'<p class="pline">{e(p.get("line"))}</p>' if p.get('line') else ''}{f'<ul class="rows">{rows}</ul>' if rows else ''}{f'<a class="btn {"btn-d" if p.get("marked") else "btn-g"}" href="{e(pc.get("h"))}">{e(pc.get("t"))}</a>' if pc.get('t') else ''}</div>'''
        plansec = f'<section class="news plans">{head(plans.get("title"), plans.get("text"))}<div class="grid g3">{g}</div>{f"""<p class="pnote">{e(plans.get("note"))}</p>""" if plans.get("note") else ""}</section>'

    # ---- 6 questions, set as the reference's opened phone menu: rows on hairlines with a small chevron ----
    faq = d.get('faq') or {}
    fq = faq.get('items') or []
    faqsec = ''
    if fq:
        r = ''.join(f'<details><summary><span>{e(q.get("q"))}</span>{CHEV}</summary><p>{e(q.get("a"))}</p></details>' for q in fq)
        faqsec = f'<section class="news faq">{head(faq.get("title"), "")}<div class="qa">{r}</div></section>'

    # ---- 7 the corner card ----
    pop = ''
    if close.get('title'):
        used = {order[i % len(order)] % len(lands) for i in range(len(sitems))} if lands else set()
        dl = [i for i, l in enumerate(lands) if l.get('tone') == 'dark']
        pi = next((i for i in dl if i not in used), dl[0] if dl else None)
        pp = lands[pi] if pi is not None else None
        plogo = ''
        if brand.get('logo'):
            plogo = f'<img class="plogo{" inv" if brand.get("logo_wordmark") else ""}" src="{M}{e(brand["logo"])}" alt="" style="height:{24 if brand.get("logo_wordmark") else 36}px;width:auto">'
        pop = f'''<aside class="pop" data-pop aria-label="{e(close.get('title'))}"><div class="popc">
{f'<img class="ppic" data-slot="corner-card" src="{M}{e(pp["src"])}" alt="" loading="lazy">' if pp else ''}<span class="pveil"></span>
<div class="pmark">{plogo}</div><div class="ptx"><h2>{e(close.get('title'))}</h2>{f'<p>{e(close.get("text"))}</p>' if close.get('text') else ''}</div>
{f'<a class="btn btn-w" href="{e(ccta.get("h"))}">{e(ccta.get("t"))}</a>' if ccta.get('t') else ''}</div>
<button class="px" type="button" data-pop-x aria-label="Close" hidden>{CLOSE}</button></aside>'''

    # ---- 8 foot ----
    foot = d.get('foot') or {}
    links = d.get('links') or []
    cols = []
    if nav:
        cols.append(''.join(f'<li><a href="{e(n.get("h"))}">{e(n.get("t"))}</a></li>' for n in nav))
    seen = {n.get('h') for n in nav}
    rest = [l for l in links if l.get('h') not in seen]
    if rest:
        cols.append(''.join(f'<li><a href="{e(l.get("h"))}">{e(l.get("t"))}</a></li>' for l in rest))
    acct = [x for x in (signin, cta) if x.get('t') and x.get('h') not in {l.get('h') for l in rest} | seen]
    uniq, hs = [], set()
    for x in acct:
        if x.get('h') not in hs:
            hs.add(x.get('h'))
            uniq.append(x)
    if uniq:
        cols.append(''.join(f'<li><a href="{e(x.get("h"))}">{e(x.get("t"))}</a></li>' for x in uniq))
    fl = ''.join(f'<a href="{e(l.get("h"))}">{e(l.get("t"))}</a>' for l in foot.get('links') or [])
    footer = f'''<footer class="foot"><div class="ftop"><div class="fa"><a class="brand" href="{e(brand.get('home') or '#')}">{logo(28)}</a>{f'<p>{e(foot.get("text"))}</p>' if foot.get('text') else ''}</div>
<div class="fcols">{''.join(f'<ul>{x}</ul>' for x in cols)}</div></div>
<div class="fbot"><p>{e(foot.get('legal'))}</p>{f'<div>{fl}</div>' if fl else ''}</div></footer>'''

    css = f'''
*,*::before,*::after{{box-sizing:border-box}}html{{-webkit-text-size-adjust:100%}}
body{{margin:0;background:{c['G']};color:{c['I']};font:400 16px/1.5 '{SANS}',system-ui,sans-serif;-webkit-font-smoothing:antialiased;overflow-x:clip}}
h1,h2,h3,h4,p,ul{{margin:0;padding:0}}ul{{list-style:none}}a{{color:inherit;text-decoration:none}}img{{display:block;max-width:100%}}
:focus-visible{{outline:2px solid {c['I']};outline-offset:2px;border-radius:6px}}
.bar{{position:sticky;top:0;z-index:30;background:{c['G']}}}
.barin{{height:52px;padding:8px;display:flex;justify-content:space-between;align-items:center}}
.bl{{display:flex;align-items:center;gap:40px;padding-left:8px;min-width:0;flex:0 1 auto}}.brand{{display:flex;align-items:center;gap:8px;min-width:0}}.brand img{{flex:none;max-width:none}}.br{{min-width:0}}.pl{{overflow:hidden;text-overflow:ellipsis}}
.bname{{font-size:17px;font-weight:500;letter-spacing:-.02em;white-space:nowrap}}
.links{{display:flex;gap:24px;align-items:center}}.links a{{font-size:13px;font-weight:500;line-height:16px;padding:8px 0;display:block;transition:opacity .15s cubic-bezier(.4,0,.2,1)}}.links a:hover{{opacity:.6}}
.br{{display:flex;align-items:center;gap:8px}}.txt{{font-size:13px;font-weight:500;padding-right:16px;transition:opacity .15s cubic-bezier(.4,0,.2,1);white-space:nowrap}}.txt:hover{{opacity:.6}}
.pl{{font-size:13px;font-weight:500;line-height:16px;padding:10px 16px;border-radius:999px;white-space:nowrap;transition:background-color .15s cubic-bezier(.4,0,.2,1),transform .15s}}
.pl-d{{background:{c['I']};color:{c['G']}}}.pl-d:hover{{background:{c['Ihov']}}}.pl-a{{background:{c['A']};color:{c['onA']}}}.pl-a:hover{{background:{c['Ahov']}}}
.pl:active,.btn:active,.send:active{{transform:scale(.97)}}
.menu{{display:none}}.menu summary{{list-style:none;width:40px;height:40px;border-radius:999px;display:grid;place-items:center;cursor:pointer}}.menu summary::-webkit-details-marker{{display:none}}
.mi,.mi::before{{display:block;width:16px;height:1.5px;background:currentColor;border-radius:2px;transition:transform .15s cubic-bezier(.4,0,.2,1)}}.mi{{transform:translateY(-3px)}}.mi::before{{content:"";transform:translateY(6px)}}
.menu[open] .mi{{transform:rotate(45deg)}}.menu[open] .mi::before{{transform:rotate(-90deg)}}
.panel{{position:absolute;left:0;right:0;top:100%;max-height:calc(100svh - 56px);overflow-y:auto;background:{c['G']};border-bottom:1px solid {c['line']};padding:8px 16px 24px;box-shadow:0 20px 25px -5px rgba(0,0,0,.1),0 8px 10px -6px rgba(0,0,0,.1)}}
.panel li+li{{border-top:1px solid {c['line']}}}.panel li a{{display:flex;align-items:center;height:41px;font-size:15px;font-weight:500}}.panel ul{{margin-bottom:16px}}
.btn{{display:inline-flex;align-items:center;justify-content:center;height:40px;padding:0 16px;border-radius:999px;font-size:15px;font-weight:500;line-height:1.5;transition:background-color .15s ease,color .15s ease,transform .15s ease;white-space:nowrap}}
.btn-d{{background:{c['I']};color:{c['G']}}}.btn-d:hover{{background:{c['Ihov']}}}.btn-g{{background:{c['pill']};color:{c['I']}}}.btn-g:hover{{background:{c['pillhov']}}}
.btn-o{{border:1px solid {c['line']};color:{c['I']}}}.btn-o:hover{{background:{c['chip']}}}.btn-w{{background:#fff;color:#171717}}.btn-w:hover{{background:#e6e6e6}}
.wide{{display:flex;width:100%;margin-top:8px}}
.open{{margin-top:56px;padding:96px 24px;display:flex;flex-direction:column;align-items:center;min-height:632px}}
.col{{width:100%;max-width:672px}}.h1w{{padding:16px 0 32px}}
h1{{display:flex;flex-direction:column;align-items:center;gap:16px;text-align:center;font:400 40px/1.15 '{SERIF}','Iowan Old Style',Georgia,serif;letter-spacing:-.017em;min-height:calc(52px + var(--rd) * 46px);font-optical-sizing:auto}}
.mark{{width:auto;height:auto;max-height:36px;max-width:180px;border-radius:8px}}.line{{display:block}}.line .w{{display:inline-block;white-space:nowrap}}.line .l{{display:inline-block}}
@keyframes lin{{from{{opacity:0;transform:translateY(2px)}}to{{opacity:1;transform:none}}}}@keyframes lout{{from{{opacity:1;transform:none}}to{{opacity:0;transform:translateY(-2px)}}}}
.ask{{position:relative;background:{c['box']};border:1px solid {c['line']};border-radius:32px;padding:10px 16px 16px;box-shadow:0 1px 2px rgba(0,0,0,.05)}}
.ask{{cursor:default}}.shown{{min-height:48px;padding:12px 4px;font-size:17px;line-height:24px;font-weight:450;color:{c['I']};transition:opacity .28s ease-out}}.shown.off{{opacity:0}}
.shown span{{display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}.shown small{{display:block;font-size:13px;line-height:16px;font-weight:500;color:{c['sec']}}}
.shown.lab{{min-height:56px;padding:8px 4px}}.shown.lab+.askrow{{margin-top:16px}}
.askrow{{margin-top:24px;min-height:48px;display:flex;gap:8px;align-items:flex-end}}
.chipb{{position:relative;z-index:1;height:36px;display:inline-flex;align-items:center;padding:0 12px;border-radius:12px;background:{c['chip']};color:{c['sec']};font-size:13px;font-weight:500;white-space:nowrap;transition:background-color .15s cubic-bezier(.4,0,.2,1)}}.chipb:hover{{background:{c['pill']}}}
.send{{margin-left:auto;height:48px;min-width:48px;padding:0 16px 0 20px;display:inline-flex;align-items:center;gap:8px;border-radius:999px;background:{c['I']};color:{c['G']};font-size:15px;font-weight:500;white-space:nowrap;transition:background-color .3s cubic-bezier(0,0,.2,1),transform .15s}}
.send:hover{{background:{c['Ihov']}}}
.note{{margin-top:24px;text-align:center;font-size:12px;line-height:16px;color:{c['ter']}}}
.main2{{padding:48px 24px 96px}}
.trust{{max-width:896px;margin:0 auto;padding:40px 0 48px;overflow:hidden;-webkit-mask-image:linear-gradient(90deg,transparent,#000 14%,#000 86%,transparent);mask-image:linear-gradient(90deg,transparent,#000 14%,#000 86%,transparent)}}
.run{{display:flex;width:max-content;animation:run 36s linear infinite}}.run ul{{display:flex;align-items:center;gap:80px;padding-right:80px;height:24px}}
.run li{{font-size:15px;font-weight:500;letter-spacing:-.019em;color:{c['ter']};white-space:nowrap}}@keyframes run{{to{{transform:translateX(-50%)}}}}
.hd{{display:flex;justify-content:space-between;align-items:flex-end;gap:16px;margin-bottom:32px}}.h28{{font-size:28px;line-height:1.3;font-weight:500;letter-spacing:-.01em}}
.hd p{{margin-top:8px;max-width:640px;font-size:15px;line-height:1.63;letter-spacing:-.019em;color:{c['sec']}}}
.grps{{display:grid;gap:64px}}.grp{{display:flex;flex-direction:column;gap:40px}}
.card{{position:relative;isolation:isolate;display:flex;flex-direction:column;aspect-ratio:16/10;border-radius:32px;overflow:hidden;padding:28px;color:var(--ci);background:var(--cm)}}
.bg{{position:absolute;inset:0;z-index:-2;width:100%;height:100%;object-fit:cover;transition:all .3s cubic-bezier(0,0,.2,1)}}
a.card:hover .bg{{transform:scale(1.03);opacity:.9}}
.veil{{position:absolute;inset:0;z-index:-1;background:linear-gradient(to top,rgba(var(--cv),.82) 0,rgba(var(--cv),.62) 18%,rgba(var(--cv),0) 46%)}}
.cpill{{align-self:flex-start;flex:none;height:56px;padding:0 10px 0 28px;display:inline-flex;align-items:center;gap:10px;border-radius:999px;background:var(--pb);color:var(--pf);font-size:17px;font-weight:500;white-space:nowrap}}
.cpill i{{width:36px;height:36px;border-radius:999px;display:grid;place-items:center;background:var(--pf);color:var(--pb)}}
.shot{{position:relative;flex:1;min-height:0;margin:20px 0 24px}}
.shot img{{position:absolute;inset:0;margin:auto;max-width:62%;max-height:100%;width:auto;height:auto;border-radius:14px;box-shadow:0 30px 60px -20px rgba(0,0,0,.45),0 0 0 1px rgba(0,0,0,.06)}}
.sh-phone img{{border-radius:22px}}.sh-book img{{border-radius:4px}}
.ctx{{display:block;max-width:600px}}.ch{{font-size:36px;line-height:1.15;font-weight:500;letter-spacing:-.02em}}.cp{{display:block;margin-top:4px;font-size:20px;line-height:1.4;font-weight:450;opacity:.92}}
.pts{{display:flex;flex-wrap:wrap;justify-content:center;gap:32px 16px;max-width:896px;width:100%;margin:0 auto;text-align:center}}
.pt{{width:212px}}.pt h4{{font-size:15px;line-height:24px;font-weight:500;letter-spacing:-.019em}}.pt p{{margin-top:4px;font-size:13px;line-height:16px;color:{c['sec']}}}
.news{{padding:96px 24px 112px}}.news+.news{{padding-top:0}}
.grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:48px 32px}}.grid.g4,.grid.g8{{grid-template-columns:repeat(4,minmax(0,1fr))}}
.art{{display:flex;flex-direction:column;align-items:flex-start}}
.tile{{container-type:inline-size;width:100%;aspect-ratio:16/9;border-radius:16px;background:{c['chip']};display:grid;place-items:center;overflow:hidden}}
.tile b{{font-weight:700;letter-spacing:-.04em;line-height:1;color:{c['ter']};white-space:nowrap}}
.art h3{{margin-top:20px;font-size:20px;line-height:1.4;font-weight:450}}.when{{margin-top:8px;font-size:13px;line-height:16px;color:{c['ter']}}}
.pline{{margin-top:12px;font-size:15px;line-height:1.63;letter-spacing:-.019em;color:{c['sec']}}}
.rows{{margin-top:12px}}.rows li{{font-size:13px;line-height:16px;color:{c['sec']};padding:9px 0;border-top:1px solid {c['line']}}}
.plan .btn{{margin-top:20px}}.pnote{{margin-top:48px;max-width:640px;font-size:13px;line-height:1.63;color:{c['ter']}}}
.qa{{max-width:896px}}.qa details{{border-top:1px solid {c['line']}}}.qa details:last-child{{border-bottom:1px solid {c['line']}}}
.qa summary{{list-style:none;display:flex;justify-content:space-between;align-items:center;gap:24px;min-height:52px;padding:12px 0;font-size:16px;line-height:1.5;font-weight:500;cursor:pointer}}.qa summary::-webkit-details-marker{{display:none}}
.chev{{flex:none;opacity:.5;transition:transform .15s cubic-bezier(.4,0,.2,1)}}.qa details[open] .chev{{transform:rotate(180deg)}}
.qa p{{padding:0 36px 20px 0;max-width:720px;font-size:15px;line-height:1.63;letter-spacing:-.019em;color:{c['sec']}}}
.pop{{position:relative;width:320px;max-width:calc(100% - 32px);margin:0 auto 96px}}
.popc{{position:relative;isolation:isolate;overflow:hidden;border-radius:24px;background:#0b0b0d;color:#fff;padding:16px 16px 24px;display:flex;flex-direction:column;align-items:center;gap:24px;box-shadow:inset 0 0 0 1px rgba(255,255,255,.1)}}
.ppic{{position:absolute;inset:0 0 auto 0;z-index:-2;width:100%;height:68%;object-fit:cover;opacity:.6}}
.pveil{{position:absolute;left:0;right:0;top:25%;bottom:0;z-index:-1;background:linear-gradient(to top,#0b0b0d 0,#0b0b0d 42%,rgba(11,11,13,.7) 62%,rgba(11,11,13,0) 100%)}}
.pmark{{height:112px;width:100%;display:grid;place-items:center}}.plogo{{border-radius:8px}}.plogo.inv{{filter:brightness(0) invert(1);border-radius:0}}
.ptx{{display:flex;flex-direction:column;align-items:center;gap:4px;text-align:center}}.ptx h2{{font-size:20px;line-height:1.25;font-weight:500}}.ptx p{{font-size:15px;line-height:1.6;letter-spacing:-.019em;color:rgba(255,255,255,.72)}}
.px{{position:absolute;top:12px;right:12px;width:32px;height:32px;border-radius:999px;border:0;background:transparent;color:rgba(255,255,255,.7);display:grid;place-items:center;cursor:pointer;transition:background-color .15s,color .15s}}.px:hover{{background:rgba(255,255,255,.1);color:#fff}}.px[hidden]{{display:none}}
.px:focus-visible,.popc .btn:focus-visible{{outline-color:#fff}}
.foot{{padding:64px 24px 24px}}.ftop{{display:grid;grid-template-columns:416px minmax(0,1fr);gap:80px}}
.fa{{display:flex;flex-direction:column;gap:24px;align-items:flex-start}}.fa p{{max-width:384px;font-size:15px;line-height:1.63;letter-spacing:-.019em;color:{c['sec']}}}
.fcols{{display:flex;justify-content:flex-end;gap:48px 128px;flex-wrap:wrap}}.fcols li+li{{margin-top:10px}}.fcols a{{display:inline-block;padding:4px 0;font-size:13px;line-height:16px;color:{c['sec']};transition:color .15s cubic-bezier(.4,0,.2,1)}}.fcols a:hover{{color:{c['I']}}}
.fbot{{margin-top:96px;padding:16px 0;display:flex;justify-content:space-between;align-items:center;gap:16px;font-size:13px;line-height:16px;color:{c['ter']}}}.fbot div{{display:flex;gap:24px}}.fbot a:hover{{color:{c['I']}}}
@media (min-width:1024px){{
.js .pop{{position:fixed;right:24px;bottom:24px;z-index:40;margin:0;opacity:0;transform:translateY(16px);pointer-events:none;transition:opacity .3s cubic-bezier(.4,0,.2,1),transform .3s cubic-bezier(.4,0,.2,1);box-shadow:0 25px 50px -12px rgba(0,0,0,.25);border-radius:24px}}
.js .pop[data-open]{{opacity:1;transform:none;pointer-events:auto}}.js .pop[data-gone]{{display:none}}}}
@media (max-width:1023px){{.ftop{{grid-template-columns:1fr;gap:48px}}.fcols{{justify-content:flex-start;gap:48px}}.fcols ul{{min-width:147px}}}}
@media (max-width:767px){{
.barin{{height:56px}}.bar .wm{{height:16px!important}}.pl{{padding:10px 12px}}.bl{{flex:none}}.links,.txt,.pl-d{{display:none}}.menu{{display:block}}
.open{{padding:96px 16px;min-height:593px}}h1{{font-size:30.4px;min-height:calc(52px + var(--rm) * 35px)}}
.card{{aspect-ratio:3/4;padding:20px}}.cpill{{height:40px;padding:0 6px 0 16px;gap:8px;font-size:15px}}.cpill i{{width:28px;height:28px}}
.shot{{margin:16px 0}}.shot img{{max-width:86%}}.sh-phone img,.sh-book img{{max-width:70%}}
.ch{{font-size:28.27px}}.cp{{font-size:16.155px}}.h28{{font-size:22.125px}}
.news{{padding:48px 16px 112px}}.grid,.grid.g4,.grid.g8{{grid-template-columns:1fr;gap:24px}}.art h3{{font-size:16.155px;margin-top:20px}}
.fbot{{flex-direction:column;text-align:center}}.fcols{{display:grid;grid-template-columns:1fr 1fr}}}}
@media (max-width:639px){{
.main2{{padding:48px 0 96px}}.hd{{padding:0 16px}}.card{{border-radius:0}}.pts{{display:grid;grid-template-columns:1fr 1fr;padding:0 16px;align-items:start}}.pt{{width:auto}}
.tile{{width:calc(100% + 32px);margin:0 -16px;border-radius:0}}.chipb{{display:none}}.send{{padding:0 14px 0 18px}}.shown{{font-size:16px}}.shown span{{white-space:normal}}}}
@media (prefers-reduced-motion:reduce){{
*,*::before,*::after{{transition:none!important}}.run{{animation:none;width:auto;flex-wrap:wrap;justify-content:center}}.run ul{{flex-wrap:wrap;justify-content:center;height:auto;gap:12px 40px;padding:0}}.run ul+ul{{display:none}}
.trust{{-webkit-mask-image:none;mask-image:none}}a.card:hover .bg{{transform:none}}.line .l{{animation:none!important}}}}
'''

    js = '''
(function(){var D=document,R=D.documentElement;R.classList.add('js');
var still=matchMedia('(prefers-reduced-motion: reduce)').matches;
/* the serif line: letters arrive one after another (0.28s ease-out each), stand, and leave the same way */
var L=D.querySelector('.line');if(L&&!still){var lines=[];try{lines=JSON.parse(L.getAttribute('data-lines'))||[]}catch(x){}
 if(lines.length>1){var k=0;var set=function(t,out){var h='',n=0;t.split(' ').forEach(function(w,wi,a){h+='<span class="w">';for(var i=0;i<w.length;i++){h+='<span class="l" style="animation:'+(out?'lout':'lin')+' .28s ease-out '+(n*(out?20:28))+'ms both">'+w[i].replace(/&/g,'&amp;').replace(/</g,'&lt;')+'</span>';n++}h+='</span>'+(wi<a.length-1?' ':'')});L.innerHTML=h;return n};
  var turn=function(){var n=lines[k].replace(/ /g,'').length;setTimeout(function(){set(lines[k],true);setTimeout(function(){k=(k+1)%lines.length;set(lines[k],false);turn()},280+n*20+60)},Math.max(1800,3450-(280+n*20+60)))};
  set(lines[0],false);turn()}}
/* the box shows its lines one after another: the line fades out (.28s), is replaced, fades in; each stands ~3.4s */
var T=D.querySelector('[data-shown]');if(T&&!still){var asks=__ASKS__;if(asks.length>1){var a=0;setInterval(function(){T.classList.add('off');setTimeout(function(){a=(a+1)%asks.length;
  var sm=T.querySelector('small'),sp=T.querySelector('span');if(sm)sm.textContent=asks[a][0];sp.textContent=asks[a][1];T.classList.remove('off')},300)},3450)}}
/* the corner card rises once the page has been scrolled past the opening, and can be sent away */
var P=D.querySelector('[data-pop]');if(P){var X=P.querySelector('[data-pop-x]');var wide=matchMedia('(min-width:1024px)');
  var sync=function(){X.hidden=!wide.matches;if(wide.matches&&scrollY>640)P.setAttribute('data-open','')};
  X.addEventListener('click',function(){P.removeAttribute('data-open');setTimeout(function(){P.setAttribute('data-gone','')},300)});
  addEventListener('scroll',sync,{passive:true});wide.addEventListener('change',sync);sync()}
/* the phone menu closes when a link in it is used or Escape is pressed */
var Mn=D.querySelector('.menu');if(Mn){Mn.addEventListener('click',function(ev){if(ev.target.closest('a'))Mn.open=false});D.addEventListener('keydown',function(ev){if(ev.key==='Escape')Mn.open=false})}
})();'''.replace('__ASKS__', json.dumps(asks, ensure_ascii=False).replace('</', '<\\/'))

    fonts = (f'<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
             f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400..700&family=Newsreader:opsz,wght@6..72,400&display=swap">')
    desc = hero.get('text') or ''
    return f'''<!doctype html><html lang="{e(d.get('lang') or 'en')}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(name)} — {e(title)}</title><meta name="description" content="{e(desc)}"><meta name="theme-color" content="{c['G']}">
{fonts}<style>{css}</style></head><body>
{bar}<main>{opening}{body2}{figsec}{plansec}{faqsec}{pop}</main>{footer}
<script>{js}</script></body></html>'''
