"""scenes.py — whole compositions, authored: what a page is made of when devices alone are not enough.

The first page built from the device library used ten devices and still read as a stock skeleton with effects on it:
dead space beside a held list, screenshots shrunk past reading, the same beat five times (see REFACTOR.md, 2026-11-11).
A device is an ingredient. A SCENE is a finished composition — its layout, the devices it uses, the size its pictures
must be shown at, what it does on a phone — written once and measured, with slots for a client's own material.

A page is: one type system (TYPE), one palette (palette()), an opening, three to five scenes in the order of the
client's story, quiet passages between them, a close. The art director chooses and fills; it draws nothing.

  SCENES                {id: {'name', 'role', 'needs', 'slots', 'devices'}}   + render functions
  TYPE                  type systems of different character (open-licence faces only)
  palette(accent, night, scheme) → tokens, contrast-checked
  page(plan, images)    → one self-contained HTML document"""
import html as H, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'devices'))
import registry as LIB

e = lambda s: H.escape(str(s if s is not None else ''), quote=True)


STROKE = '<svg viewBox="0 0 100 12" preserveAspectRatio="none" aria-hidden="true"><path d="M1 8C16 3 31 11 50 6S84 3 99 7" pathLength="1"/></svg>'


def mark(text):
    """The marked phrase of a line. It always carries the stroke of the `draw` device; the page shows the stroke only
    where its plan asks for a drawn mark (body class mark-drawn), and colours the phrase otherwise."""
    parts = re.split(r'\*([^*]+)\*', str(text or '')); return ''.join(f'<em class="dv-draw">{e(p)}{STROKE}</em>' if i % 2 else e(p) for i, p in enumerate(parts))


def lines(text, cls='display', most=4):
    """A display line as masked rows: the writer breaks it with ' / ' (two to four rows); each row rises on its own."""
    rows = [r.strip() for r in str(text or '').split(' / ') if r.strip()] or ['']
    merged = []
    for r in rows:
        if merged and len(re.sub(r'[*\W]', '', r)) <= 3: merged[-1] += ' ' + r   # "11" alone on a line is an orphan, not a row
        else: merged.append(r)
    rows = merged
    while len(rows) > most:   # more rows than a heading holds is a column of words: the two neighbours that are shortest together become one
        k = min(range(len(rows) - 1), key=lambda i: len(rows[i]) + len(rows[i + 1])); rows[k:k + 2] = [rows[k] + ' ' + rows[k + 1]]
    longest = max((len(w) for r in rows for w in re.sub(r'\*', '', r).split()), default=6)
    widest = max((len(re.sub(r'\*', '', r)) for r in rows), default=6)   # the longest row, for a heading whose rows must each stay on one line
    return f'<span class="dv-lines {cls}" style="--lw:{max(4, longest)};--lr:{len(rows)};--lc:{max(4, widest)}">' + ' '.join(f'<span class="dv-ln"><span>{mark(r)}</span></span>' for r in rows) + '</span>'


# ---- type: systems of different character. k = how many px of font-size one character of the longest word needs room for ----
TYPE = {
    'light-grotesk': {'name': 'Light grotesque — calm, exact, technical', 'display': "'Geist',system-ui,sans-serif", 'w': 300, 'ls': '-.035em', 'lh': '.98', 'case': 'none', 'k': 1.9, 'text': "'Geist',system-ui,sans-serif", 'mono': "'Geist Mono',ui-monospace,monospace", 'gf': 'Geist:wght@300;400;500&family=Geist+Mono:wght@400;500'},
    'condensed-caps': {'name': 'Condensed capitals — loud, sporting, poster', 'display': "'Barlow Condensed',Impact,sans-serif", 'w': 800, 'ls': '-.01em', 'lh': '.86', 'case': 'uppercase', 'k': 2.7, 'text': "'IBM Plex Sans',system-ui,sans-serif", 'mono': "'IBM Plex Mono',ui-monospace,monospace", 'gf': 'Barlow+Condensed:wght@700;800&family=IBM+Plex+Sans:wght@400;500&family=IBM+Plex+Mono:wght@400;500'},
    'display-serif': {'name': 'Display serif — editorial, warm, considered', 'display': "'Instrument Serif',Georgia,serif", 'w': 400, 'ls': '-.02em', 'lh': '.95', 'case': 'none', 'k': 2.2, 'text': "'Inter',system-ui,sans-serif", 'mono': "'JetBrains Mono',ui-monospace,monospace", 'gf': 'Instrument+Serif:ital@0;1&family=Inter:wght@400;500&family=JetBrains+Mono:wght@400;500'},
    'tight-bold': {'name': 'Tight bold grotesque — confident, product, direct', 'display': "'Inter Tight',system-ui,sans-serif", 'w': 700, 'ls': '-.045em', 'lh': '1', 'case': 'none', 'k': 1.8, 'text': "'Inter',system-ui,sans-serif", 'mono': "'JetBrains Mono',ui-monospace,monospace", 'gf': 'Inter+Tight:wght@600;700&family=Inter:wght@400;500&family=JetBrains+Mono:wght@400;500'},
    'soft-serif': {'name': 'Soft old-style serif — hospitality, craft, slow', 'display': "'Fraunces',Georgia,serif", 'w': 400, 'ls': '-.03em', 'lh': '.96', 'case': 'none', 'k': 2.0, 'text': "'Figtree',system-ui,sans-serif", 'mono': "'DM Mono',ui-monospace,monospace", 'gf': 'Fraunces:opsz,wght@9..144,300;9..144,400&family=Figtree:wght@400;500&family=DM+Mono:wght@400;500'},
    'wide-geometric': {'name': 'Geometric grotesque — design-led, modern, a little odd', 'display': "'Space Grotesk',system-ui,sans-serif", 'w': 400, 'ls': '-.06em', 'lh': '.86', 'case': 'none', 'k': 1.75, 'text': "'Space Grotesk',system-ui,sans-serif", 'mono': "'Space Mono',ui-monospace,monospace", 'gf': 'Space+Grotesk:wght@400;500&family=Space+Mono:wght@400'},
}


def _rgb(h):
    h = str(h or '#000').lstrip('#'); h = ''.join(c * 2 for c in h) if len(h) == 3 else h.ljust(6, '0')[:6]
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _lum(h):
    lin = lambda v: v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4; r, g, b = (lin(v / 255) for v in _rgb(h)); return .2126 * r + .7152 * g + .0722 * b


def contrast(a, b):
    x, y = sorted((_lum(a), _lum(b)), reverse=True); return (x + .05) / (y + .05)


def _mix(a, b, t):
    return '#%02x%02x%02x' % tuple(round(x + (y - x) * t) for x, y in zip(_rgb(a), _rgb(b)))


SCHEMES = ('paper', 'night', 'tint', 'tone')


def palette(accent, night='#0e0f12', scheme='paper'):
    """The page's colours from the client's own two: its signature colour and its darkest ground. `paper`: white with
    ink; `night`: the client's dark with light ink; `tint`: a paper carrying a breath of the accent. Text always clears
    4.5:1; where the accent cannot carry text on the ground it is kept for fills and the ink takes the emphasis."""
    night = night if _lum(night) < .018 else _mix(accent, '#050506', .9)   # a grey is not a night: the dark ground is near black with a breath of the brand
    if scheme == 'tone':   # three steps of one tone — pale, middle, near black — as measured on squared-media.nl (28% / 20% / 52% of the page)
        import colorsys
        r, g, b = (v / 255 for v in _rgb(accent)); h, _, _ = colorsys.rgb_to_hls(r, g, b); hx = lambda l, sat: '#%02x%02x%02x' % tuple(round(v * 255) for v in colorsys.hls_to_rgb(h, l, sat))
        paper, ground2, night, ink = hx(.865, .2), hx(.735, .16), hx(.045, .1), hx(.085, .16)
        em = ink if contrast(accent, paper) < 3 else accent
        return {'paper': paper, 'ink': ink, 'accent': accent, 'em': em, 'on_accent': max(('#0b0c0f', '#ffffff'), key=lambda c: contrast(c, accent)), 'ground2': ground2,
                'mute': _mix(ink, paper, .3), 'line': _mix(paper, ink, .16), 'night': night, 'on_night': hx(.92, .12), 'lead': night, 'on_lead': hx(.92, .12), 'scheme': scheme}
    if scheme == 'night': paper, ink = night, '#f1f1ee'
    elif scheme == 'tint': paper, ink = _mix('#ffffff', accent, .07), _mix(night, '#000000', .2)
    else: paper, ink = '#ffffff', _mix(night, '#000000', .1)
    ground2 = _mix(paper, ink, .06 if scheme != 'night' else .08)
    em = accent if contrast(accent, paper) >= 3 else ink   # a marked word must be readable: large type needs 3:1
    return {'paper': paper, 'ink': ink, 'accent': accent, 'em': em, 'on_accent': max(('#0b0c0f', '#ffffff'), key=lambda c: contrast(c, accent)), 'ground2': ground2,
            'mute': _mix(ink, paper, .38), 'line': _mix(paper, ink, .14), 'night': night, 'on_night': '#f1f1ee', 'scheme': scheme,
            # the surface that stands out from the page: the night on a light page — and on a night page, where the night is the page itself, the accent (lifted, where the accent itself is too dark to stand out)
            **((lambda lead: {'lead': lead, 'on_lead': max(('#0b0c0f', '#ffffff'), key=lambda c: contrast(c, lead))})(accent if contrast(accent, night) >= 2.2 else em) if scheme == 'night' else {'lead': night, 'on_lead': '#f1f1ee'})}


def backdrop(accent):
    """A ground drawn from the client's accent: wide arcs with a lit edge and grain. Drawn, not photographed and not generated; it claims nothing."""
    r, g, b = _rgb(accent); c = lambda a, k=1.0: f'rgba({int(r * k)},{int(g * k)},{int(b * k)},{a})'
    arcs = ''.join(f'<path d="M{x0} 1000 C {x0 + 180} {520 - i * 26}, {x0 + 420} {300 - i * 38}, {x0 + 760} {360 - i * 18} S {x0 + 1180} 700, {x0 + 1500} 1100" fill="none" stroke="url(#bd{i % 3})" stroke-width="{150 - i * 12}" stroke-linecap="round" opacity="{0.9 - i * 0.09:.2f}"/>' for i, x0 in enumerate((-160, 120, 420, 700, 980)))
    grads = ''.join(f'<linearGradient id="bd{n}" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="{c(0, .2)}"/><stop offset=".5" stop-color="{c(a, k)}"/><stop offset="1" stop-color="{c(a * .5, k * .7)}"/></linearGradient>' for n, (a, k) in enumerate(((.8, .6), (.55, .42), (.36, .3))))
    return (f'<svg viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice" aria-hidden="true"><defs>{grads}<radialGradient id="bdg" cx=".78" cy=".42" r=".6"><stop offset="0" stop-color="{c(.32, .5)}"/><stop offset="1" stop-color="{c(0)}"/></radialGradient>'
            '<filter id="bdn"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" stitchTiles="stitch"/><feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .1 0"/></filter></defs>'
            f'<rect width="1440" height="900" fill="url(#bdg)"/><g transform="translate(360 0)">{arcs}</g><rect width="1440" height="900" filter="url(#bdn)"/></svg>')


# ---- scenes ----
SCENES = {}


def scene(id, **meta):
    def wrap(fn): SCENES[id] = {**meta, 'id': id, 'render': fn}; return fn
    return wrap


def _btn(a, cls=''):
    return f'<a class="btn dv-roll {cls}" href="{e(a.get("url"))}">{e(a.get("label"))}</a>' if isinstance(a, dict) and a.get('label') and a.get('url') else ''


def _shot(images, pid, alt=''):
    im = images.get(pid)
    return f'<img src="{im["data"]}" alt="{e(alt)}" width="{int(im.get("w") or 1200)}" height="{int(im.get("h") or 700)}" loading="lazy">' if im else ''


@scene('open-statement', name='Opening: one statement on an empty ground', role='open', devices=['line-rise', 'rise-stagger', 'magnet', 'fact-ticker'],
       needs='a headline of 5–9 words that can break into 2–3 rows', slots={'kicker': 'mono label ≤ 40 chars', 'h1': 'rows split by " / ", one *marked phrase*', 'lede': '≤ 2 sentences', 'note': 'mono, optional', 'facts': '4–8 true facts ≤ 40 chars, optional'})
def _open_statement(s, ctx):
    facts = [f for f in s.get('facts') or [] if str(f).strip()][:8]
    tick = f'<div class="dv-tick mono open-tick"><ul>{"".join(f"<li>{e(f)}</li>" for f in facts)}</ul></div>' if len(facts) >= 4 else ''
    return (f'<section class="sc open" id="top"><div class="wrap"><p class="mono kicker" data-rise>{e(s.get("kicker"))}</p><h1>{lines(s.get("h1"))}</h1>'
            f'<div class="open-foot"><p class="lede" data-rise style="--i:1">{e(s.get("lede"))}</p><div class="acts" data-rise style="--i:2">{_btn(ctx["action"], "dv-magnet")}{_btn(ctx.get("action2"), "quiet")}</div>'
            + (f'<p class="mono note" data-rise style="--i:3">{e(s["note"])}</p>' if s.get('note') else '') + f'</div></div>{tick}</section>')


@scene('open-picture', name='Opening: a statement, then the picture grows to the edges', role='open', devices=['line-rise', 'rise-stagger', 'grow-to-bleed'],
       needs='one strong wide picture (≥ 1400 px, not a screenshot with small text)', slots={'kicker': 'mono', 'h1': 'rows split by " / "', 'lede': '≤ 2 sentences', 'image': 'picture id', 'alt': 'what the picture shows'})
def _open_picture(s, ctx):
    im = ctx['images'].get(s.get('image')) or {}; wide = ' wide' if (im.get('w') or 0) > 2.05 * (im.get('h') or 1) else ''   # a strip of a picture is given height, cropped at its sides
    return (f'<section class="sc open open-pic" id="top"><div class="wrap"><p class="mono kicker" data-rise>{e(s.get("kicker"))}</p><h1>{lines(s.get("h1"))}</h1>'
            f'<div class="open-foot"><p class="lede" data-rise style="--i:1">{e(s.get("lede"))}</p><div class="acts" data-rise style="--i:2">{_btn(ctx["action"], "dv-magnet")}{_btn(ctx.get("action2"), "quiet")}</div></div></div>'
            f'<figure class="dv-grow{wide}">{_shot(ctx["images"], s.get("image"), s.get("alt"))}</figure></section>')


@scene('held-product', name='The product, claim by claim, held', role='show', devices=['held-index', 'figure-bars', 'scramble', 'rise-stagger'],
       needs='3–5 claims; each with a real screenshot shown LARGE (prefer the tight crops) or 2–5 comparable real figures or 3–6 label/value rows',
       slots={'label': 'mono', 'intro': 'one sentence standing under the list', 'items': [{'title': '≤ 26 chars', 'say': 'one or two sentences', 'panel': {'kind': 'image|bars|rows', 'image': 'id', 'alt': '', 'chip': 'mono caption', 'bars': [{'label': '', 'value': '', 'share': '0–1'}], 'rows': [{'k': '', 'v': ''}]}}]})
def _held_product(s, ctx):
    items = [i for i in s.get('items') or [] if i.get('title')][:5]

    def panel(p):
        chip = f'<span class="mono chip">{e(p["chip"])}</span>' if p.get('chip') else ''
        if p.get('kind') == 'image' and p.get('image') in ctx['images']: return f'<figure class="panel panel-img">{chip}<div class="shot" style="max-width:{int((ctx["images"][p["image"]].get("w") or 1200) * 1.15)}px">{_shot(ctx["images"], p["image"], p.get("alt"))}</div></figure>'   # a screenshot is never drawn wider than it is: stretched pixels read as a blur
        if p.get('kind') == 'bars' and p.get('bars'):
            rows = ''.join(f'<li><span class="k">{e(b.get("label"))}</span><span class="b"><i style="--w:{max(.04, min(1, float(b.get("share") or .5))):.3f}"></i></span><span class="v">{e(b.get("value"))}</span></li>' for b in p['bars'][:5])
            return f'<figure class="panel">{chip}<ul class="dv-bars mono">{rows}</ul></figure>'
        rows = ''.join(f'<li><span class="mono">{e(r.get("k"))}</span><b>{e(r.get("v"))}</b></li>' for r in (p.get('rows') or [])[:6])
        return f'<figure class="panel">{chip}<ul class="kv">{rows}</ul></figure>' if rows else ''
    names = ''.join(f'<li>{e(i["title"])}</li>' for i in items)
    body = ''.join(f'<article class="dv-held-item"><p class="dv-held-m">{e(i["title"])}</p>{panel(i.get("panel") or {})}<p class="say" data-rise>{e(i.get("say"))}</p></article>' for i in items)
    return (f'<section class="sc held" id="product"><div class="wrap dv-held"><div class="dv-held-side"><p class="mono kicker"><span class="dv-scramble">{e(s.get("label"))}</span></p><ol class="dv-held-names">{names}</ol>'
            + (f'<p class="held-intro">{e(s["intro"])}</p>' if s.get('intro') else '') + f'</div><div class="dv-held-items">{body}</div></div></section>')


@scene('figures', name='The numbers, very large', role='prove', devices=['count-up', 'rise-stagger', 'line-rise'],
       needs='2–4 true numbers that are an argument on their own, each with a caption', slots={'label': 'mono', 'h2': 'rows split by " / "', 'figures': [{'value': 'the number exactly as the client writes it', 'unit': 'prefix/suffix, optional', 'caption': '≤ 60 chars'}], 'note': 'the caveat the client itself states, optional'})
def _figures(s, ctx):
    def fig(k, f):
        v = str(f.get('value') or ''); m = re.match(r'^([^\d\-−]*)([\d.,]+)(.*)$', v)
        num = f'{e(m.group(1))}<span class="dv-count" data-to="{e(m.group(2).replace(",", ""))}">{e(m.group(2))}</span>{e(m.group(3))}' if m else e(v)
        return f'<li data-rise style="--i:{k}"><p class="fig">{num}<small>{e(f.get("unit"))}</small></p><p class="cap">{e(f.get("caption"))}</p></li>'
    shown = [f for f in (s.get('figures') or [])[:4] if f.get('value')]; figs = ''.join(fig(k, f) for k, f in enumerate(shown))
    widest = max((len(str(f.get('value') or '')) + len(str(f.get('unit') or '')) * .4 for f in shown), default=3)
    return (f'<section class="sc figures alt" id="record"><div class="wrap"><p class="mono kicker">{e(s.get("label"))}</p><h2>{lines(s.get("h2"), "h2")}</h2><ul class="figs" style="--n:{max(1, len(shown))};--c:{max(3, widest):.1f}">{figs}</ul>'
            + (f'<p class="mono note">{e(s["note"])}</p>' if s.get('note') else '') + '</div></section>')


@scene('rail', name='One phrase crossing the screen', role='breathe', devices=['side-rail'], needs='a phrase of 3–7 words that is the client\'s own position', slots={'words': 'the phrase', 'again': 'a second short phrase, optional'})
def _rail(s, ctx):
    words = [w for w in (s.get('words'), s.get('again'), s.get('words')) if w]
    return f'<section class="sc rail-sc" aria-label="{e(s.get("words"))}"><div class="dv-rail" style="--rate:.42"><div class="dv-rail-row">' + ''.join(f'<span class="{"hollow" if k % 2 else ""}">{e(w)}</span>' for k, w in enumerate(words)) + '</div></div></section>'


@scene('stage', name='One screen of the product, shown whole and large', role='show', devices=['depth', 'rise-stagger'],
       needs='one whole screenshot at least 1200 px wide that reads at size', slots={'label': 'mono', 'h2': 'rows split by " / "', 'say': '≤ 2 sentences', 'image': 'id', 'alt': '', 'chips': ['2–4 mono facts about what is on the screen']})
def _stage(s, ctx):
    chips = ''.join(f'<li class="mono">{e(c)}</li>' for c in (s.get('chips') or [])[:4])
    return (f'<section class="sc stage" id="see"><div class="wrap stage-head"><div><p class="mono kicker">{e(s.get("label"))}</p><h2>{lines(s.get("h2"), "h2")}</h2></div><p class="lede" data-rise>{e(s.get("say"))}</p></div>'
            f'<div class="wrap"><figure class="stage-fig" data-rise><div class="shot">{_shot(ctx["images"], s.get("image"), s.get("alt"))}</div>' + (f'<ul class="chips">{chips}</ul>' if chips else '') + '</figure></div></section>')


@scene('stack', name='Plans or steps that pile up', role='decide', devices=['stack-cards', 'rise-stagger'], needs='3–5 plans or steps, each with a name, a figure and one sentence',
       slots={'label': 'mono', 'h2': 'rows split by " / " — it must match the number of cards', 'cards': [{'kicker': 'mono (price, limit, step number)', 'title': '', 'say': 'one sentence', 'points': ['≤ 3 short facts'], 'action': {'label': '', 'url': ''}}]})
def _stack(s, ctx):
    def card(c):
        pts = ''.join(f'<li>{e(p)}</li>' for p in (c.get('points') or [])[:3])
        return (f'<article class="dv-card card"><div><p class="mono kicker">{e(c.get("kicker"))}</p><h3>{e(c.get("title"))}</h3></div><div class="card-say"><p>{e(c.get("say"))}</p>' + (f'<ul>{pts}</ul>' if pts else '')
                + f'</div><div class="card-act">{_btn(c.get("action"), "small")}</div></article>')
    return f'<section class="sc stack-sc" id="plans"><div class="wrap"><p class="mono kicker">{e(s.get("label"))}</p><h2>{lines(s.get("h2"), "h2")}</h2><div class="dv-stack">{"".join(card(c) for c in (s.get("cards") or [])[:5] if c.get("title"))}</div></div></section>'


@scene('ledger', name='Plain answers in a ruled table', role='quiet', devices=['rise-stagger'], needs='3–6 questions a buyer really asks, with the client\'s own answers', slots={'label': 'mono', 'h2': 'one short line', 'rows': [{'q': '', 'a': '≤ 2 sentences'}]})
def _ledger(s, ctx):
    rows = ''.join(f'<div class="row" data-rise style="--i:{k % 3}"><h3>{e(r.get("q"))}</h3><p>{e(r.get("a"))}</p></div>' for k, r in enumerate((s.get('rows') or [])[:6]) if r.get('q'))
    return f'<section class="sc ledger" id="answers"><div class="wrap ledger-in"><div><p class="mono kicker">{e(s.get("label"))}</p><h2 class="h3x">{e(s.get("h2"))}</h2></div><div class="rows">{rows}</div></div></section>'


@scene('index', name='The rest of the site, as a designed index', role='quiet', devices=['rise-stagger'], needs='6–12 secondary pages with short names', slots={'label': 'mono', 'links': [{'label': '≤ 32 chars', 'url': ''}]})
def _index(s, ctx):
    links = ''.join(f'<li><a href="{e(l["url"])}">{e(l["label"])}</a></li>' for l in (s.get('links') or [])[:12] if l.get('label') and l.get('url'))
    return f'<section class="sc index" id="more"><div class="wrap index-in"><p class="mono kicker">{e(s.get("label"))}</p><ul>{links}</ul></div></section>'


@scene('close', name='The close: one line, the action, the name', role='close', devices=['line-rise', 'magnet', 'end-mark'], needs='one line that asks for the action',
       slots={'line': 'rows split by " / "', 'note': 'mono, optional', 'columns': [{'title': '', 'links': [{'label': '', 'url': ''}]}], 'legal': 'as the client writes it', 'wordmark': 'true to end on the name set across the footer'})
def _close(s, ctx):
    cols = ''.join(f'<div><p class="mono">{e(c.get("title"))}</p>' + ''.join(f'<a href="{e(l["url"])}">{e(l["label"])}</a>' for l in (c.get('links') or [])[:7] if l.get('label') and l.get('url')) + '</div>' for c in (s.get('columns') or [])[:4])
    name = ctx['brand'].get('name') or ''
    markw = f'<div class="dv-endmark{" low" if re.search("[gjpqyQ,;ç]", name) else ""}" style="--chars:{max(4, len(name))}" aria-hidden="true">{e(name)}</div>' if s.get('wordmark') and 3 <= len(name) <= 14 else ''
    return (f'<footer class="sc close night" id="end"><div class="wrap"><h2>{lines(s.get("line"))}</h2><div class="acts" data-rise>{_btn(ctx["action"], "dv-magnet")}{_btn(ctx.get("action2"), "quiet")}</div>'
            + (f'<p class="mono note">{e(s["note"])}</p>' if s.get('note') else '') + (f'<div class="cols">{cols}</div>' if cols else '') + f'<p class="mono legal">{e(s.get("legal"))}</p></div>{markw}</footer>')


@scene('open-atmosphere', name='Opening: a statement over a field of the brand\'s own colour', role='open', devices=['line-rise', 'rise-stagger', 'magnet', 'depth'],
       needs='nothing but a headline — the ground is drawn from the accent, or is the commissioned atmosphere picture when one is given (id "atmos")', slots={'kicker': 'mono', 'h1': 'rows split by " / "', 'lede': '≤ 2 sentences', 'note': 'mono, optional'})
def _open_atmosphere(s, ctx):
    bg = f'<figure class="atmos dv-depth" style="--rate:.12">{_shot(ctx["images"], "atmos")}</figure>' if 'atmos' in ctx['images'] else f'<div class="atmos">{backdrop(ctx["brand"].get("accent") or "#2f6bff")}</div>'
    return (f'<section class="sc open open-atmos night" id="top">{bg}<div class="wrap"><p class="mono kicker" data-rise>{e(s.get("kicker"))}</p><h1>{lines(s.get("h1"))}</h1>'
            f'<div class="open-foot"><p class="lede" data-rise style="--i:1">{e(s.get("lede"))}</p><div class="acts" data-rise style="--i:2">{_btn(ctx["action"], "dv-magnet")}{_btn(ctx.get("action2"), "quiet")}</div>'
            + (f'<p class="mono note" data-rise style="--i:3">{e(s["note"])}</p>' if s.get('note') else '') + '</div></div></section>')


@scene('window', name='One photograph, wide, moving slowly behind its frame', role='show', devices=['depth', 'rise-stagger'],
       needs='one photograph at least 1200 px wide that can be cropped to a wide frame', slots={'image': 'id', 'alt': 'what it shows', 'caption': 'mono, ≤ 60 chars', 'say': 'one or two sentences set large beside the caption, optional'})
def _window(s, ctx):
    return (f'<section class="sc window"><figure class="dv-depth win" style="--rate:-.14">{_shot(ctx["images"], s.get("image"), s.get("alt"))}</figure>'
            f'<div class="wrap win-foot"><p class="mono">{e(s.get("caption"))}</p>' + (f'<p class="say" data-rise>{e(s["say"])}</p>' if s.get('say') else '') + '</div></section>')


@scene('gallery', name='Photographs, one at a time, uncovered from the side', role='show', devices=['slides', 'line-rise'],
       needs='3–8 photographs of similar proportion, each at least 800 px wide (never screenshots)', slots={'label': 'mono', 'h2': 'rows split by " / "', 'images': [{'image': 'id', 'alt': ''}]})
def _gallery(s, ctx):
    pics = ''.join(_shot(ctx['images'], p.get('image'), p.get('alt')) for p in (s.get('images') or [])[:8] if p.get('image') in ctx['images'])
    return (f'<section class="sc gallery" id="gallery"><div class="wrap"><p class="mono kicker">{e(s.get("label"))}</p><h2>{lines(s.get("h2"), "h2")}</h2>'
            f'<div class="dv-slides" style="--ratio:16/9"><div class="dv-slides-view">{pics}</div><p class="dv-slides-ui mono"><button data-step="-1" aria-label="Previous">←</button><span class="dv-slides-n"></span><button data-step="1" aria-label="Next">→</button></p></div></div></section>')


@scene('collage', name='Photographs laid over one another, each moving at its own pace', role='show', devices=['depth', 'clip-reveal', 'line-rise', 'rise-stagger'],
       needs='exactly 3 of the client\'s own photographs, sharp and at least 900 px wide (never screenshots, never stills from film), and one short statement', slots={'label': 'mono', 'h2': 'rows split by " / "', 'say': '≤ 2 sentences', 'pictures': [{'image': 'id', 'alt': ''}]})
def _collage(s, ctx):
    pics = [p for p in (s.get('pictures') or []) if p.get('image') in ctx['images']][:3]
    if len(pics) < 3: return ''
    pics.sort(key=lambda p: -(ctx['images'][p['image']].get('w') or 0))   # the widest picture is the ground the others lie on
    figs = ''.join(f'<figure class="co-{k} dv-depth dv-clip" style="--rate:{r}">{_shot(ctx["images"], p["image"], p.get("alt"))}</figure>' for k, (p, r) in enumerate(zip(pics, ('-.06', '.1', '-.14'))))
    return (f'<section class="sc collage" id="look"><div class="wrap"><p class="mono kicker">{e(s.get("label"))}</p><h2>{lines(s.get("h2"), "h2")}</h2><div class="co">{figs}</div>'
            + (f'<p class="lede co-say" data-rise>{e(s["say"])}</p>' if s.get('say') else '') + '</div></section>')


@scene('open-product', name='Opening for software: a quiet line, and the product itself running off the first screen', role='open', devices=['line-rise', 'rise-stagger', 'magnet', 'frame', 'lift'],
       needs='one real screenshot of the product: a wide one at least 1000 px across (shown in a window), or an upright phone screenshot (shown in a phone). A headline of 4–9 words',
       slots={'kicker': 'mono label ≤ 40 chars', 'h1': 'rows split by " / ", one *marked phrase*', 'lede': '≤ 2 sentences', 'image': 'id of the screenshot', 'alt': 'what the screenshot shows', 'align': '"left" (wide screenshot) or "centre" (phone)', 'ground': 'optional: id of one of the client\'s own wide, sharp photographs to lie behind the product'})
def _open_product(s, ctx):
    im = ctx['images'].get(s.get('image'))
    if not im: return ''
    tall = .42 <= (im.get('w') or 1) / max(1, im.get('h') or 1) <= .62; centre = ' centre' if s.get('align') == 'centre' or tall else ''
    g = ctx['images'].get(s.get('ground')); ground = f'<img class="op-ground" src="{g["data"]}" alt="" width="{int(g.get("w") or 1400)}" height="{int(g.get("h") or 700)}">' if g and g is not im and not g.get('shot') else ''
    frame = (f'<figure class="dv-phone">{_shot(ctx["images"], s.get("image"), s.get("alt"))}</figure>' if tall else f'<figure class="dv-window dv-lift">{_shot(ctx["images"], s.get("image"), s.get("alt"))}</figure>')
    return (f'<section class="sc open open-prod{centre}" id="top"><div class="wrap"><p class="mono kicker" data-rise>{e(s.get("kicker"))}</p><h1>{lines(s.get("h1"))}</h1>'
            f'<div class="open-foot"><p class="lede" data-rise style="--i:1">{e(s.get("lede"))}</p><div class="acts" data-rise style="--i:2">{_btn(ctx["action"], "dv-magnet")}{_btn(ctx.get("action2"), "quiet")}</div></div></div>'
            f'<div class="op-stage{" tall" if tall else ""}{" has-ground" if ground else ""}">{ground}{frame}</div></section>')


@scene('plans', name='The plans, side by side', role='decide', devices=['rise-stagger', 'line-rise'], needs='2–4 plans exactly as the client states them: name, price, who it is for, what is in it. Never a plan, a price or a limit the client does not publish',
       slots={'label': 'mono', 'h2': 'rows split by " / "', 'plans': [{'name': '', 'price': 'as written, e.g. "$20"', 'per': 'e.g. "/ month", optional', 'for': 'one line: who it is for', 'points': ['≤ 7 short facts'], 'action': {'label': '', 'url': ''}, 'marked': 'true on the one plan the client itself marks'}], 'note': 'mono, the client\'s own small print, optional'})
def _plans(s, ctx):
    plans = [p for p in (s.get('plans') or []) if p.get('name')][:4]
    if len(plans) < 2: return ''
    def card(k, p):
        pts = ''.join(f'<li>{e(x)}</li>' for x in (p.get('points') or [])[:7] if x)
        return (f'<article class="pl{" is-marked" if p.get("marked") in (True, "true") else ""}" data-rise style="--i:{k}"><p class="mono pl-name">{e(p["name"])}</p><p class="pl-price">{e(p.get("price"))}'
                + (f'<small>{e(p["per"])}</small>' if p.get('per') else '') + '</p>' + (f'<p class="pl-for">{e(p["for"])}</p>' if p.get('for') else '') + _btn(p.get('action') or ctx['action'], 'small' if p.get('marked') in (True, 'true') else 'small quiet')
                + (f'<ul class="pl-points">{pts}</ul>' if pts else '') + '</article>')
    return (f'<section class="sc plans" id="pricing"><div class="wrap"><p class="mono kicker">{e(s.get("label"))}</p><h2>{lines(s.get("h2"), "h2")}</h2><div class="pl-grid" style="--n:{len(plans)}">{"".join(card(k, p) for k, p in enumerate(plans))}</div>'
            + (f'<p class="mono note">{e(s["note"])}</p>' if s.get('note') else '') + '</div></section>')


@scene('compare', name='What each plan holds, row by row', role='decide', devices=['rise-stagger', 'line-rise'], needs='the client\'s own comparison of 2–4 plans or options: 6–30 rows in 1–5 groups, each cell "yes", "no" or the short value the client gives',
       slots={'label': 'mono', 'h2': 'rows split by " / "', 'columns': ['plan names, 2–4'], 'groups': [{'title': '', 'rows': [{'name': '', 'values': ['"yes" | "no" | a short value — one per column']}]}]})
def _compare(s, ctx):
    cols = [str(c) for c in (s.get('columns') or []) if c][:4]
    if len(cols) < 2: return ''
    def cell(v):
        v = str(v if v is not None else '').strip()
        if v.lower() in ('yes', 'true', '✓'): return '<td><span class="cmp-y" aria-label="yes">✓</span></td>'
        if v.lower() in ('no', 'false', '', '—', '-'): return '<td><span class="cmp-n" aria-label="no">—</span></td>'
        return f'<td>{e(v)}</td>'
    body = ''
    for g in (s.get('groups') or [])[:5]:
        rows = [r for r in (g.get('rows') or []) if r.get('name') and len(r.get('values') or []) == len(cols)][:12]
        if not rows: continue
        body += (f'<tr class="cmp-g"><th colspan="{len(cols) + 1}" scope="colgroup">{e(g.get("title"))}</th></tr>' if g.get('title') else '') + ''.join(f'<tr><th scope="row">{e(r["name"])}</th>{"".join(cell(v) for v in r["values"])}</tr>' for r in rows)
    if not body: return ''
    head = '<tr><td></td>' + ''.join(f'<th scope="col">{e(c)}</th>' for c in cols) + '</tr>'
    return (f'<section class="sc compare" id="compare"><div class="wrap"><p class="mono kicker">{e(s.get("label"))}</p><h2>{lines(s.get("h2"), "h2")}</h2><div class="cmp" tabindex="0" role="region" aria-label="{e(s.get("label") or "Comparison")}"><table style="--n:{len(cols)}"><thead>{head}</thead><tbody>{body}</tbody></table></div></div></section>')


@scene('features', name='What it does, each in a card with the real interface in it', role='show', devices=['rise-stagger', 'line-rise', 'frame'],
       needs='3–5 things the product does, each with its own real screenshot or tight crop of the interface (a phone-shaped one stands in a phone). Never an icon, never a drawn interface',
       slots={'label': 'mono', 'h2': 'rows split by " / "', 'items': [{'title': '≤ 32 chars', 'say': 'one or two sentences', 'image': 'id of a screenshot or crop', 'alt': ''}]})
def _features(s, ctx):
    items = [i for i in (s.get('items') or []) if i.get('title') and i.get('image') in ctx['images']][:5]
    if len(items) < 3: return ''
    def card(k, i):
        im = ctx['images'][i['image']]; phone = .42 <= (im.get('w') or 1) / max(1, im.get('h') or 1) <= .62
        pic = (f'<div class="ft-pic ft-phone"><figure class="dv-phone">{_shot(ctx["images"], i["image"], i.get("alt"))}</figure></div>' if phone
               else f'<div class="ft-pic" style="max-width:{int((im.get("w") or 1200) * 1.15)}px;--w:{int(im.get("w") or 1200)}px"><figure class="ft-shot">{_shot(ctx["images"], i["image"], i.get("alt"))}</figure></div>')
        return f'<article class="ft ft-{k}" data-rise style="--i:{k % 3}"><div class="ft-words"><h3>{e(i["title"])}</h3>' + (f'<p>{e(i["say"])}</p>' if i.get('say') else '') + f'</div>{pic}</article>'
    return (f'<section class="sc features" id="features"><div class="wrap"><p class="mono kicker">{e(s.get("label"))}</p><h2>{lines(s.get("h2"), "h2")}</h2>'
            f'<div class="ft-grid ft-n{len(items)}">{"".join(card(k, i) for k, i in enumerate(items))}</div></div></section>')


@scene('carte', name='A menu or price list set like a printed card', role='decide', devices=['rise-stagger'], needs='6–24 items with their prices or values, in 1–4 groups, exactly as the client lists them',
       slots={'label': 'mono', 'h2': 'rows split by " / "', 'groups': [{'title': '', 'items': [{'name': '', 'note': 'optional, ≤ 70 chars', 'price': 'as written'}]}], 'action': {'label': '', 'url': ''}})
def _carte(s, ctx):
    def group(g):
        rows = ''.join(f'<li><span class="nm"><b>{e(i.get("name"))}</b>' + (f'<small>{e(i["note"])}</small>' if i.get('note') else '') + f'</span><span class="pr">{e(i.get("price"))}</span></li>' for i in (g.get('items') or [])[:10] if i.get('name'))
        return f'<div class="grp" data-rise><h3 class="mono">{e(g.get("title"))}</h3><ul>{rows}</ul></div>' if rows else ''
    sizes = [len([i for i in (g.get('items') or [])[:10] if i.get('name')]) for g in (s.get('groups') or [])[:4]]
    flow = ' flow' if sum(sizes) >= 4 and max(sizes) > .6 * sum(sizes) else ''   # one long group beside a short one leaves half the band empty: let the long one run on into the next column, as a printed card does
    return (f'<section class="sc carte alt" id="menu-card"><div class="wrap"><p class="mono kicker">{e(s.get("label"))}</p><h2>{lines(s.get("h2"), "h2")}</h2><div class="grps{flow}">{"".join(group(g) for g in (s.get("groups") or [])[:4])}</div>'
            + (f'<div class="acts">{_btn(s.get("action"), "quiet")}</div>' if s.get('action') else '') + '</div></section>')


@scene('visit', name='Where and when, set large', role='decide', devices=['line-rise', 'rise-stagger', 'magnet'], needs='an address and opening hours (or how to get in touch), as the client states them',
       slots={'label': 'mono', 'where': 'the address or place, rows split by " / "', 'rows': [{'k': 'e.g. a day or "Phone"', 'v': 'as written'}], 'action': {'label': 'e.g. Reserve', 'url': ''}})
def _visit(s, ctx):
    rows = ''.join(f'<li><span class="mono">{e(r.get("k"))}</span><b>{e(r.get("v"))}</b></li>' for r in (s.get('rows') or [])[:9] if r.get('k'))
    return (f'<section class="sc visit" id="visit"><div class="wrap visit-in"><div><p class="mono kicker">{e(s.get("label"))}</p><h2>{lines(s.get("where"), "h2", 3)}</h2><div class="acts" data-rise>{_btn(s.get("action") or ctx["action"], "dv-magnet")}</div></div>'
            f'<ul class="kv" data-rise style="--i:1">{rows}</ul></div></section>')


@scene('statement', name='The thesis, read word by word', role='turn', devices=['read-along'],
       needs='one paragraph of 20–60 words in the client\'s own terms — what it believes, why it exists', slots={'label': 'mono', 'text': 'the paragraph, plain (no asterisks)', 'by': 'mono: who says it, optional'})
def _statement(s, ctx):
    return (f'<section class="sc statement"><div class="wrap"><p class="mono kicker">{e(s.get("label"))}</p><p class="dv-read thesis">{e(s.get("text"))}</p>'
            + (f'<p class="mono note">{e(s["by"])}</p>' if s.get('by') else '') + '</div></section>')


@scene('rooms', name='Words held while the photographs pass', role='show', devices=['held-pictures', 'clip-reveal', 'line-rise', 'rise-stagger'],
       needs='2–4 of the client\'s own photographs (at least 700 px wide, never screenshots), each with a short caption', slots={'label': 'mono', 'h2': 'rows split by " / "', 'say': '≤ 3 sentences', 'action': {'label': '', 'url': ''}, 'pictures': [{'image': 'id', 'alt': '', 'caption': 'mono ≤ 50 chars'}]})
def _rooms(s, ctx):
    pics = ''.join(f'<figure><div class="dv-clip">{_shot(ctx["images"], p.get("image"), p.get("alt"))}</div><figcaption class="mono">{e(p.get("caption"))}</figcaption></figure>' for p in (s.get('pictures') or [])[:4] if p.get('image') in ctx['images'])
    return (f'<section class="sc rooms" id="place"><div class="wrap dv-split"><div class="dv-split-side"><p class="mono kicker">{e(s.get("label"))}</p><h2>{lines(s.get("h2"), "h2 h2s")}</h2><p class="lede" data-rise>{e(s.get("say"))}</p>'
            + (f'<div class="acts" data-rise style="--i:1">{_btn(s.get("action"), "quiet")}</div>' if s.get('action') else '') + f'</div><div class="dv-split-flow">{pics}</div></div></section>')


@scene('steps', name='How it goes, in numbered steps', role='show', devices=['rise-stagger', 'line-rise'], needs='3–5 steps the client itself describes, each a short title and one sentence',
       slots={'label': 'mono', 'h2': 'rows split by " / "', 'steps': [{'title': '≤ 30 chars', 'say': 'one sentence'}]})
def _steps(s, ctx):
    st = [x for x in (s.get('steps') or [])[:5] if x.get('title')]
    items = ''.join(f'<li data-rise style="--i:{k}"><span class="num">{k + 1:02d}</span><h3>{e(x["title"])}</h3><p>{e(x.get("say"))}</p></li>' for k, x in enumerate(st))
    return f'<section class="sc steps" id="how"><div class="wrap"><p class="mono kicker">{e(s.get("label"))}</p><h2>{lines(s.get("h2"), "h2")}</h2><ol class="step-row" style="--n:{len(st)}">{items}</ol></div></section>'


@scene('voices', name='What people say, one voice at a time', role='prove', devices=['rise-stagger'], needs='1–3 REAL testimonials that are in the evidence, word for word, with the name as given — never written, never paraphrased into a quote',
       slots={'label': 'mono', 'quotes': [{'text': 'the client\'s visitor\'s words exactly', 'name': 'as given', 'role': 'as given, optional'}]})
def _voices(s, ctx):
    qs = ''.join(f'<figure class="voice" data-rise style="--i:{k}"><blockquote>{e(q.get("text"))}</blockquote><figcaption class="mono">{e(q.get("name"))}' + (f' · {e(q["role"])}' if q.get('role') else '') + '</figcaption></figure>' for k, q in enumerate((s.get('quotes') or [])[:3]) if q.get('text') and q.get('name'))
    return f'<section class="sc voices alt"><div class="wrap"><p class="mono kicker">{e(s.get("label"))}</p><div class="voice-row">{qs}</div></div></section>' if qs else ''


@scene('faq', name='Many questions, opened one at a time', role='quiet', devices=['rise-stagger'], needs='6–12 questions with the client\'s own answers (for fewer, use "ledger")', slots={'label': 'mono', 'h2': 'one short line', 'rows': [{'q': '', 'a': ''}]})
def _faq(s, ctx):
    rows = ''.join(f'<details><summary><span>{e(r.get("q"))}</span></summary><p>{e(r.get("a"))}</p></details>' for r in (s.get('rows') or [])[:12] if r.get('q') and r.get('a'))
    return f'<section class="sc ledger faq" id="answers"><div class="wrap ledger-in"><div><p class="mono kicker">{e(s.get("label"))}</p><h2 class="h3x">{e(s.get("h2"))}</h2></div><div class="acc">{rows}</div></div></section>'


@scene('scatter', name='Pictures laid out loose, each a different size', role='show', devices=['clip-reveal', 'tilt', 'rise-stagger', 'line-rise'],
       needs='3–5 of the client\'s own photographs or product pictures (never screenshots of a website), each with a name and a short tag', slots={'label': 'mono', 'h2': 'rows split by " / "', 'items': [{'image': 'id', 'alt': '', 'title': '≤ 30 chars', 'tag': 'mono ≤ 24 chars', 'url': 'optional link'}]})
def _scatter(s, ctx):
    # Rows that close: a large picture with two stacked beside it (a trio), or two side by side, one wider (a pair), or
    # three across. Every picture fills its place, cropped to it, so no row leaves a hole — the first version drew each
    # picture at its own proportion in a wide span, and a tall one beside a short one left half a screen of nothing.
    # Which place a picture takes follows how wide it stays crisp (`sharp_w`, measured): the place is given in px at 1440.
    wide = lambda i: int(ctx['images'][i['image']].get('sharp_w') or (ctx['images'][i['image']].get('w') or 0) * (.5 if ctx['images'][i['image']].get('soft') else 1))
    its = sorted([i for i in (s.get('items') or [])[:5] if i.get('image') in ctx['images'] and wide(i) >= 330], key=lambda i: -wide(i))
    if len(its) < 3: return ''
    n = len(its); big = wide(its[0]) * 1.25 >= 800
    rows = {3: ['trio'] if big else ['thirds'], 4: ['pair', 'pair'], 5: ['trio', 'pair'] if big else ['pair', 'thirds']}[n]
    ROOM = {'trio': (800, 460, 460), 'pair': (760, 540), 'thirds': (430, 430, 430)}
    out, k = [], 0
    for r, kind in enumerate(rows):
        cells = ''
        for slot, room in enumerate(ROOM[kind]):
            it = its[k]; k += 1; own = wide(it) * 1.25
            inner = f'<div class="dv-clip">{_shot(ctx["images"], it.get("image"), it.get("alt"))}</div><figcaption><b>{e(it.get("title"))}</b><span class="mono">{e(it.get("tag"))}</span></figcaption>'
            body = f'<a href="{e(it["url"])}">{inner}</a>' if it.get('url') else inner
            hold = f' style="max-width:{int(own)}px"' if own < room else ''   # a picture without the detail for its place is kept at the width it is crisp at
            cells += f'<figure class="dv-tilt sc-it sc-{slot}"{hold} data-rise>{body}</figure>'
        out.append(f'<div class="sc-row sc-{kind}{" flip" if r % 2 else ""}">{cells}</div>')
    return f'<section class="sc scatter" id="work"><div class="wrap"><p class="mono kicker">{e(s.get("label"))}</p><h2>{lines(s.get("h2"), "h2")}</h2><div class="sc-grid">{"".join(out)}</div></div></section>'


@scene('bento', name='Facts in tiles of different sizes', role='show', devices=['rise-stagger', 'count-up', 'line-rise'],
       needs='4–6 short true facts or capabilities; one of them a number or a picture that deserves the large tile', slots={'label': 'mono', 'h2': 'rows split by " / "', 'tiles': [{'title': '≤ 34 chars', 'say': 'one sentence, optional', 'figure': 'a number as written, optional', 'image': 'id, optional (only the first tile)'}]})
def _bento(s, ctx):
    tiles = [t for t in (s.get('tiles') or [])[:6] if t.get('title')]
    def tile(k, t):
        pic = f'<div class="b-pic">{_shot(ctx["images"], t.get("image"), "")}</div>' if k == 0 and t.get('image') in ctx['images'] else ''
        fig = f'<p class="b-fig">{e(t["figure"])}</p>' if t.get('figure') else ''
        return f'<article class="b-tile b-{k}{" b-shown" if pic else " b-bare" if k == 0 and not fig else " b-plain" if not fig else ""}" data-rise style="--i:{k % 3}">{pic}{fig}<h3>{e(t["title"])}</h3>' + (f'<p>{e(t["say"])}</p>' if t.get('say') else '') + '</article>'
    return f'<section class="sc bento" id="what"><div class="wrap"><p class="mono kicker">{e(s.get("label"))}</p><h2>{lines(s.get("h2"), "h2")}</h2><div class="b-grid b-n{len(tiles)}">{"".join(tile(k, t) for k, t in enumerate(tiles))}</div></div></section>' if len(tiles) >= 4 else ''


@scene('kinetic-line', name='A statement whose rows slide apart', role='breathe', devices=['kinetic'], needs='a statement of 2–3 rows of 1–3 words each, the client\'s own position', slots={'rows': ['row one', 'row two', 'row three (optional)']})
def _kinetic_line(s, ctx):
    rows = [str(r).strip() for r in (s.get('rows') or [])[:3] if str(r).strip()]
    return (f'<section class="sc kinetic-sc" aria-label="{e(" ".join(rows))}"><p class="dv-kinetic">' + ''.join(f'<span class="dv-k{" hollow" if k % 2 else ""}">{e(r)}</span>' for k, r in enumerate(rows)) + '</p></section>') if len(rows) >= 2 else ''


CSS = """
*{box-sizing:border-box;margin:0}html{-webkit-text-size-adjust:100%}
body{font-family:var(--text);font-size:clamp(15px,1.11vw,17px);line-height:1.5;color:var(--ink);background:var(--paper);-webkit-font-smoothing:antialiased;overflow-x:clip}
a{color:inherit}img{display:block;max-width:100%;height:auto;background:var(--ground2)}ul,ol{list-style:none;padding:0}
::selection{background:var(--accent);color:var(--on-accent)}html{scroll-padding-top:96px;scroll-behavior:smooth}h1,h2,h3{text-wrap:balance;font-weight:inherit}p{text-wrap:pretty}body{font-variant-numeric:tabular-nums;font-kerning:normal;text-rendering:optimizeLegibility}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
:focus-visible{outline:2px solid var(--accent);outline-offset:3px}
.skip{position:absolute;left:-999px}.skip:focus{left:16px;top:16px;z-index:99;background:var(--paper);color:var(--ink);padding:10px 14px}
.wrap{padding-inline:var(--pad);max-width:1760px;margin-inline:auto}.sc{padding-block:clamp(72px,9.4vw,156px)}
.sc:not(.night):not(.open):not(.keep)+.sc:not(.night){padding-top:clamp(16px,2.4vw,40px)}
.mono{font-family:var(--mono);font-size:12px;line-height:1.35;letter-spacing:.08em;text-transform:uppercase}.kicker{color:var(--mute);margin-bottom:clamp(20px,2.4vw,36px)}.note{color:var(--mute);margin-top:22px}
em{font-style:normal;color:var(--em)}em svg{display:none}.mark-drawn .display em,.mark-drawn .h2 em{color:inherit;white-space:nowrap}.mark-drawn .display em svg,.mark-drawn .h2 em svg{display:block}.dv-ln:has(.dv-draw){padding-bottom:.34em;margin-bottom:-.34em}.display-serif em,.soft-serif em{font-style:italic}
.display,.h2{display:block;font-family:var(--display);font-weight:var(--dw);letter-spacing:var(--dls);line-height:var(--dlh);text-transform:var(--dcase)}
.display{font-size:min(clamp(48px,11.6vw,196px),calc((100vw - 2 * var(--pad)) / var(--lw,8) * var(--k)))}
.h2{font-size:min(clamp(40px,8.2vw,140px),calc((100vw - 2 * var(--pad)) / var(--lw,8) * var(--k)))}
.lede{font-size:clamp(16px,1.3vw,20px);line-height:1.42;max-width:38ch}
.btn{display:inline-flex;align-items:center;justify-content:center;min-height:54px;padding:0 24px;border-radius:999px;background:var(--accent);color:var(--on-accent);font-family:var(--mono);font-size:12px;letter-spacing:.08em;text-transform:uppercase;text-decoration:none;white-space:nowrap;transition:transform .2s var(--ease),filter .2s}
.btn:hover{filter:brightness(1.07)}.btn:active{transform:scale(.97)}.btn.quiet{background:none;color:inherit;box-shadow:inset 0 0 0 1px var(--line)}.btn.small{min-height:44px;padding:0 18px}
.acts{display:flex;flex-wrap:wrap;gap:12px}
/* bar */
.bar{position:fixed;inset:0 0 auto 0;z-index:40;display:flex;align-items:center;justify-content:space-between;gap:16px;padding:14px var(--pad);mix-blend-mode:normal}
.bar .name{color:var(--ink);background:color-mix(in srgb,var(--paper) 82%,transparent);backdrop-filter:blur(14px);padding:9px 16px;margin-left:-16px;border-radius:999px;transition:background-color .3s;font-family:var(--display);font-weight:var(--dw);text-transform:var(--dcase);letter-spacing:var(--dls);font-size:clamp(20px,1.7vw,26px);text-decoration:none;white-space:nowrap}
.bar-r{display:flex;align-items:center;gap:10px}.bar-links{display:flex;gap:6px;padding:0 8px;min-height:44px;align-items:center;border-radius:999px;background:color-mix(in srgb,var(--paper) 82%,transparent);backdrop-filter:blur(14px)}
.bar-links a{font-family:var(--mono);font-size:12px;letter-spacing:.08em;text-transform:uppercase;text-decoration:none;padding:10px 12px}.bar .btn{min-height:44px;padding:0 18px}.dv-menu-btn{display:none}.bar.is-solid .name,.bar.is-solid .bar-links{background:none;backdrop-filter:none}.bar.is-solid{inset:10px 10px auto 10px;border-radius:18px;padding:10px calc(var(--pad) - 10px);box-shadow:0 0 0 1px var(--line),0 10px 40px -20px rgba(0,0,0,.35)}.bar{transition:inset .35s var(--ease),border-radius .35s var(--ease),padding .35s var(--ease),transform .4s var(--ease),background-color .3s}
/* open */
.open{min-height:100svh;display:grid;align-content:end;padding-top:clamp(120px,16vh,200px);padding-bottom:0}.open .wrap{width:100%;padding-bottom:clamp(40px,6vh,80px)}
.open-foot{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:clamp(24px,4vw,64px);align-items:end;margin-top:clamp(28px,4vw,64px)}.open-foot .note{grid-column:1/-1;margin-top:0}
.open-tick{border-top:1px solid var(--line);padding:22px 0;color:var(--mute)}.open-pic{padding-bottom:clamp(88px,13vw,224px)}.open-pic .dv-grow{margin-top:clamp(40px,6vw,96px)}
@media (min-width:701px){.open-pic{min-height:0;align-content:start;padding-top:clamp(104px,13svh,150px)}.open-pic .wrap{padding-bottom:0}.open-pic .display{font-size:max(48px,min(clamp(48px,11.6vw,196px),calc((100vw - 2 * var(--pad)) / var(--lw,8) * var(--k)),calc(34svh / var(--lr,2))))}.open-pic .open-foot{margin-top:clamp(30px,4.6svh,56px)}.mark-drawn .open-foot{margin-top:clamp(40px,6.4svh,76px)}.open-pic .dv-grow{margin-top:clamp(28px,5svh,56px)}.open-pic .dv-grow.wide img{aspect-ratio:2/1;object-fit:cover}}
/* held product */
.held{background:var(--ground2)}.dv-held{grid-template-columns:minmax(0,5fr) minmax(0,7fr)!important}.dv-held-names li{font-family:var(--display);font-weight:var(--dw);text-transform:var(--dcase);letter-spacing:var(--dls);font-size:clamp(30px,3.6vw,60px)!important;line-height:1.04!important}
.held-intro{margin-top:clamp(24px,3vw,44px);max-width:30ch;color:var(--mute)}.dv-held-item{display:grid;gap:clamp(18px,2vw,28px)}.say{font-size:clamp(17px,1.5vw,22px);line-height:1.38;max-width:34ch}
.panel{position:relative;background:var(--paper);border-radius:14px;padding:clamp(16px,2vw,28px);display:grid;gap:14px;margin:0}.panel-img{padding:clamp(10px,1vw,14px)}.panel .chip{color:var(--mute)}
.shot{border-radius:9px;overflow:hidden;box-shadow:0 0 0 1px var(--line)}.shot img{width:100%}
.dv-bars li{font-size:12px}.dv-bars .v{font-family:var(--display);font-weight:var(--dw);font-size:clamp(22px,2.2vw,34px);letter-spacing:var(--dls)}
.kv li{display:flex;justify-content:space-between;gap:20px;align-items:baseline;padding:14px 0;border-top:1px solid var(--line)}.kv li:first-child{border-top:0}.kv b{font-family:var(--display);font-weight:var(--dw);font-size:clamp(22px,2.2vw,34px);letter-spacing:var(--dls);text-align:right;text-transform:var(--dcase)}
/* figures */
.alt{background:var(--paper)}.figs{container-type:inline-size;display:grid;grid-template-columns:repeat(var(--n,3),minmax(0,1fr));gap:clamp(32px,5vw,88px) clamp(24px,3vw,56px);margin-top:clamp(48px,7vw,120px);border-top:1px solid var(--line);padding-top:clamp(28px,3vw,48px)}
.fig{font-family:var(--display);font-weight:var(--dw);letter-spacing:var(--dls);line-height:.9;font-size:min(clamp(48px,8vw,136px),calc((100cqw / var(--n,3) - 32px) / var(--c,4) * var(--k) * .6));text-transform:var(--dcase);white-space:nowrap}.fig small{font-size:.32em;letter-spacing:0;margin-left:.2em;color:var(--mute)}.cap{margin-top:14px;max-width:26ch;color:var(--mute)}
/* rail */
.rail-sc{padding-block:clamp(40px,6vw,96px)}.dv-rail-row span{font-family:var(--display);font-weight:var(--dw);text-transform:var(--dcase);letter-spacing:var(--dls);line-height:1;font-size:clamp(72px,15vw,260px);white-space:nowrap}
.dv-rail-row .hollow{color:transparent;-webkit-text-stroke:max(1px,.012em) var(--ink)}
/* stage */
.stage{background:var(--night);color:var(--on-night);--line:color-mix(in srgb,var(--on-night) 16%,transparent);--mute:color-mix(in srgb,var(--on-night) 62%,transparent);--em:var(--accent)}
.stage-head{display:grid;grid-template-columns:minmax(0,7fr) minmax(0,4fr);gap:clamp(24px,4vw,64px);align-items:end;margin-bottom:clamp(40px,6vw,96px)}.stage-fig{margin:0}.stage-fig .shot{border-radius:14px}.chips{display:flex;flex-wrap:wrap;gap:8px 28px;margin-top:18px;color:var(--mute)}
/* stack */
.stack-sc h2{margin-bottom:clamp(40px,6vw,96px)}.card{background:var(--ground2);border-radius:18px;padding:clamp(24px,3vw,48px);display:grid;grid-template-columns:minmax(0,4fr) minmax(0,5fr) auto;gap:clamp(20px,3vw,48px);align-items:start;min-height:clamp(150px,13vw,210px);box-shadow:0 -1px 0 var(--paper)}
.card h3{font-family:var(--display);font-weight:var(--dw);text-transform:var(--dcase);letter-spacing:var(--dls);line-height:1;font-size:clamp(32px,4vw,64px)}.card .kicker{margin-bottom:14px}.card-say ul{margin-top:14px;display:grid;gap:6px;color:var(--mute)}.card-say li::before{content:"— "}
/* ledger, index */
.ledger-in{display:grid;grid-template-columns:minmax(0,4fr) minmax(0,8fr);gap:clamp(24px,4vw,64px)}.h3x{font-family:var(--display);font-weight:var(--dw);text-transform:var(--dcase);letter-spacing:var(--dls);line-height:1.02;font-size:clamp(30px,3.6vw,60px);max-width:12ch}
.rows .row{display:grid;grid-template-columns:minmax(0,5fr) minmax(0,6fr);gap:clamp(16px,2.4vw,40px);padding:clamp(18px,2vw,28px) 0;border-top:1px solid var(--line)}.rows h3{font:500 clamp(16px,1.3vw,19px)/1.35 var(--text)}.rows p{color:var(--mute)}
.index{padding-block:clamp(56px,7vw,112px);background:var(--ground2)}.index-in{display:grid;grid-template-columns:minmax(0,4fr) minmax(0,8fr);gap:clamp(24px,4vw,64px)}.index ul{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,15rem),1fr));column-gap:clamp(24px,3vw,48px)}
.index a{display:flex;justify-content:space-between;align-items:center;gap:12px;min-height:54px;border-bottom:1px solid var(--line);text-decoration:none;transition:padding .25s var(--ease)}.index a::after{content:"→";font-family:var(--mono);opacity:.45}.index a:hover{padding-left:8px}
/* atmosphere, window, gallery, carte, visit */
.open-atmos{position:relative;isolation:isolate;overflow:hidden}.atmos{position:absolute;inset:0;z-index:-1;margin:0}.atmos svg,.atmos img{width:100%;height:100%;object-fit:cover}.open-atmos .atmos::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,transparent 30%,color-mix(in srgb,var(--night) 70%,transparent))}
.open-atmos .btn.quiet{box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--on-night) 30%,transparent)}
.window{padding-block:0}.win{margin:0;aspect-ratio:21/9;max-height:92svh;width:100%}.win img{height:100%;object-fit:cover}.win-foot{display:grid;grid-template-columns:minmax(0,4fr) minmax(0,8fr);gap:clamp(24px,4vw,64px);padding-block:clamp(20px,2.4vw,36px) 0;color:var(--mute)}.window+.sc{padding-top:clamp(64px,8vw,128px)}.win-foot .say{color:var(--ink);max-width:38ch;font-size:clamp(16px,1.3vw,20px)}
.gallery h2{margin-bottom:clamp(40px,6vw,96px)}
.co{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));align-items:start;margin-top:clamp(40px,6vw,96px)}.co figure{margin:0;border-radius:14px;grid-row:1}.co img{width:100%;height:100%;object-fit:cover}.co-0{grid-column:1/9;aspect-ratio:3/2}.co-1{grid-column:8/13;aspect-ratio:4/5;margin-top:clamp(64px,12vw,220px)!important;z-index:1;border:clamp(6px,.7vw,12px) solid var(--paper)}.co-2{grid-column:2/6;align-self:end;aspect-ratio:1;z-index:2;border:clamp(6px,.7vw,12px) solid var(--paper)}.co-say{margin-top:clamp(28px,4vw,56px);margin-left:auto}
@media (max-width:700px){.co{display:block}.co figure{margin-top:14px!important;aspect-ratio:4/3;border:0}}.dv-slides-view{border-radius:14px}
.grps{columns:2 22rem;column-gap:clamp(32px,5vw,96px);margin-top:clamp(48px,7vw,120px)}.grp{break-inside:avoid;margin-bottom:clamp(40px,5vw,72px)}.grps.flow .grp{break-inside:auto}.grps.flow li{break-inside:avoid}.grps.flow h3{break-after:avoid}.grp h3{color:var(--mute);padding-bottom:14px;border-bottom:1px solid var(--ink)}
.grp li{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:20px;align-items:baseline;padding:14px 0;border-bottom:1px solid var(--line)}.grp b{font-weight:500;font-size:clamp(17px,1.4vw,21px)}.grp small{display:block;color:var(--mute);font-size:14px;margin-top:3px}.grp .pr{font-family:var(--mono);font-size:14px;white-space:nowrap}.carte .acts{margin-top:clamp(32px,4vw,56px)}
.visit-in{display:grid;grid-template-columns:minmax(0,7fr) minmax(0,5fr);gap:clamp(32px,5vw,96px);align-items:end}.visit .acts{margin-top:clamp(28px,4vw,56px)}.visit-in>div{container-type:inline-size}.visit .h2{font-size:min(clamp(30px,5.2vw,92px),calc(100cqw / var(--lc,16) * var(--k) * .92))}
/* statement, rooms, steps, voices, faq */
.thesis{font-family:var(--display);font-weight:var(--dw);letter-spacing:var(--dls);text-transform:var(--dcase);line-height:1.06;font-size:clamp(30px,4.6vw,84px);max-width:30ch;text-wrap:pretty}.statement .note{margin-top:clamp(24px,3vw,44px)}
.h2s{font-size:min(clamp(36px,5.2vw,92px),calc((100vw - 2 * var(--pad)) / var(--lw,8) * var(--k)))}.rooms .lede{margin-top:clamp(20px,2.4vw,36px)}.rooms .acts{margin-top:clamp(20px,2.4vw,36px)}
.dv-split-flow figure{margin:0}.dv-split-flow .dv-clip{border-radius:14px}.dv-split-flow img{width:100%}.dv-split-flow figcaption{margin-top:12px;color:var(--mute)}
.step-row{display:grid;grid-template-columns:repeat(var(--n,3),minmax(0,1fr));gap:clamp(24px,3vw,56px);margin-top:clamp(48px,7vw,120px);counter-reset:none}.step-row li{border-top:1px solid var(--ink);padding-top:clamp(18px,2vw,28px)}
.step-row .num{display:block;font-family:var(--mono);font-size:12px;letter-spacing:.08em;color:var(--mute);margin-bottom:clamp(40px,6vw,96px)}.step-row h3{font-family:var(--display);font-weight:var(--dw);text-transform:var(--dcase);letter-spacing:var(--dls);line-height:1.02;font-size:clamp(26px,2.6vw,42px);text-wrap:balance}.step-row p{margin-top:12px;color:var(--mute);max-width:30ch}
.voice-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,22rem),1fr));gap:clamp(40px,6vw,96px)}.voice{margin:0}.voice blockquote{font-family:var(--display);font-weight:var(--dw);letter-spacing:var(--dls);line-height:1.12;font-size:clamp(24px,2.7vw,44px);text-wrap:balance;quotes:"“" "”"}.voice blockquote::before{content:open-quote}.voice blockquote::after{content:close-quote}.voice figcaption{margin-top:22px;color:var(--mute)}
.acc details{border-top:1px solid var(--line)}.acc details:last-child{border-bottom:1px solid var(--line)}.acc summary{list-style:none;cursor:pointer;display:flex;justify-content:space-between;gap:20px;align-items:baseline;padding:clamp(16px,1.8vw,24px) 0;font:500 clamp(16px,1.3vw,19px)/1.35 var(--text)}.acc summary::-webkit-details-marker{display:none}
.acc summary::after{content:"+";font-family:var(--mono);color:var(--mute);transition:transform .3s var(--ease)}.acc details[open] summary::after{transform:rotate(45deg)}.acc details p{color:var(--mute);max-width:60ch;padding:0 0 clamp(18px,2vw,26px)}
/* scatter, bento, kinetic */
.sc-grid{display:grid;gap:clamp(40px,5vw,84px);margin-top:clamp(48px,7vw,120px)}.sc-row{display:grid;gap:clamp(14px,1.6vw,26px) clamp(16px,2vw,32px);align-items:stretch}
.sc-pair{grid-template-columns:7fr 5fr}.sc-pair.flip{grid-template-columns:5fr 7fr}.sc-pair.flip .sc-0{order:2}.sc-thirds{grid-template-columns:repeat(3,minmax(0,1fr))}
.sc-trio{grid-template-columns:7fr 4fr;grid-template-rows:1fr 1fr}.sc-trio .sc-0{grid-row:1/3}.sc-trio.flip{grid-template-columns:4fr 7fr}.sc-trio.flip .sc-0{grid-column:2;grid-row:1/3}.sc-trio.flip .sc-1,.sc-trio.flip .sc-2{grid-column:1}
.sc-it{margin:0;width:100%;display:flex;flex-direction:column;min-width:0}.sc-it>a{display:flex;flex-direction:column;flex:1;text-decoration:none}.sc-it .dv-clip{flex:1;min-height:0}.sc-it img{width:100%;height:100%;object-fit:cover}
.sc-pair .sc-0 .dv-clip{aspect-ratio:16/10;flex:none}.sc-thirds .dv-clip{aspect-ratio:4/5;flex:none}.sc-trio .sc-1 .dv-clip,.sc-trio .sc-2 .dv-clip{aspect-ratio:3/2;flex:none}.sc-it[style]{justify-self:center;align-self:center}.sc-it[style] .dv-clip{flex:none;aspect-ratio:4/3}
.sc-it .dv-clip{border-radius:24px}.sc-it figcaption{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:baseline;gap:10px 16px;margin-top:14px}.sc-it b{font-family:var(--display);font-weight:var(--dw);text-transform:var(--dcase);letter-spacing:var(--dls);font-size:clamp(22px,2.2vw,36px);line-height:1}.sc-it .mono{color:var(--mute);border:1px solid var(--line);border-radius:999px;padding:6px 12px;white-space:nowrap;max-width:100%;overflow:hidden;text-overflow:ellipsis}
.b-grid{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:clamp(10px,1.2vw,18px);margin-top:clamp(48px,7vw,120px)}.b-tile{grid-column:span 2;background:var(--ground2);border-radius:24px;padding:clamp(20px,2.4vw,36px);display:flex;flex-direction:column;justify-content:flex-end;min-height:clamp(200px,20vw,320px);overflow:hidden;position:relative}
.b-0{grid-column:span 4;grid-row:span 2;background:var(--lead);color:var(--on-lead)}.b-n5 .b-3,.b-n5 .b-4{grid-column:span 3}.b-n4 .b-3{grid-column:span 6;min-height:clamp(140px,12vw,200px)}.b-n4 .b-1,.b-n4 .b-2{grid-column:span 2}.b-n6 .b-5{grid-column:span 2}
.b-tile h3{font-family:var(--display);font-weight:var(--dw);text-transform:var(--dcase);letter-spacing:var(--dls);line-height:1.02;font-size:clamp(22px,2.1vw,34px)}.b-0 h3{font-size:clamp(28px,3.4vw,56px)}.b-bare,.b-plain{justify-content:space-between}.b-plain h3{font-size:clamp(24px,2.5vw,40px);max-width:14ch}.b-plain{min-height:clamp(180px,16vw,260px)}.b-plain p{margin-top:clamp(20px,3vw,48px)}.b-bare h3{font-size:clamp(40px,6vw,104px);line-height:.94;max-width:11ch}.b-bare p{max-width:30ch;font-size:clamp(16px,1.2vw,19px)}.b-tile p{margin-top:10px;color:var(--mute);max-width:34ch}.b-0 p{color:color-mix(in srgb,var(--on-lead) 78%,transparent)}
.b-fig{font-family:var(--display);font-weight:var(--dw);letter-spacing:var(--dls);line-height:.9;font-size:clamp(48px,7vw,120px)!important;color:inherit!important;margin:0 0 auto!important}.b-shown{background:#0b0c0f;color:#f1f1ee}.b-shown p{color:rgba(241,241,238,.8)}.b-pic{position:absolute;inset:0}.b-pic img{width:100%;height:100%;object-fit:cover;opacity:.55}.b-pic~*{position:relative}
.kinetic-sc{padding-block:clamp(56px,8vw,128px)}.dv-k{font-family:var(--display);font-weight:var(--dw);text-transform:var(--dcase);letter-spacing:var(--dls);line-height:.9;font-size:clamp(56px,13.5vw,230px);text-align:center}.dv-k.hollow{color:transparent;-webkit-text-stroke:max(1px,.012em) var(--ink)}
/* what is kept for search, one quiet row */
.keep{padding-block:clamp(16px,2vw,28px)}.keep-all>summary{list-style:none;cursor:pointer;display:flex;justify-content:space-between;align-items:center;min-height:44px;color:var(--mute)}.keep-all>summary::-webkit-details-marker{display:none}.keep-all>summary::after{content:"+";font-family:var(--mono)}.keep-all[open]>summary::after{content:"–"}
.keep-links{display:flex;flex-wrap:wrap;gap:6px 24px;margin-top:20px;color:var(--mute)}.keep-links a{display:inline-flex;min-height:44px;align-items:center}
/* close */
.night{background:var(--night);color:var(--on-night);--line:color-mix(in srgb,var(--on-night) 16%,transparent);--mute:color-mix(in srgb,var(--on-night) 62%,transparent);--em:var(--accent)}
.close{padding-bottom:0;overflow:hidden}.close .acts{margin-top:clamp(28px,4vw,64px)}.close .cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,11rem),1fr));gap:clamp(24px,4vw,64px);margin-top:clamp(72px,10vw,160px);padding-top:28px;border-top:1px solid var(--line)}
.close .cols p{color:var(--mute);margin-bottom:12px}.close .cols a{display:block;padding:5px 0;text-decoration:none}.close .cols a:hover{text-decoration:underline;text-underline-offset:.25em}.legal{color:var(--mute);padding:clamp(40px,5vw,72px) 0 28px}
.dv-endmark{font-family:var(--display);font-weight:var(--dw);text-transform:var(--dcase);color:var(--on-night);opacity:.94}
@media (max-width:900px){
.bar-links{display:none}.dv-menu-btn{display:inline-flex;align-items:center}.bar .btn{display:none}.open{min-height:0;align-content:start;padding-top:clamp(104px,22vw,150px)}.open-pic{padding-bottom:clamp(56px,10vw,96px)}.figs{grid-template-columns:repeat(min(var(--n,3),2),minmax(0,1fr))}.fig{font-size:min(clamp(44px,13vw,96px),calc((100cqw / 2 - 24px) / var(--c,4) * var(--k) * .6))}
.open-foot,.stage-head,.ledger-in,.index-in,.rows .row,.win-foot,.visit-in{grid-template-columns:minmax(0,1fr)}.step-row{grid-template-columns:minmax(0,1fr)}.sc-row{display:block}.sc-it{margin:0 0 clamp(28px,7vw,48px);max-width:none!important}.sc-it .dv-clip{aspect-ratio:4/3!important;flex:none}.b-grid{grid-template-columns:minmax(0,1fr)}.b-tile,.b-0{grid-column:auto!important;grid-row:auto;min-height:0}.b-0{min-height:220px}.dv-k{font-size:clamp(44px,14vw,96px);text-align:left;padding-inline:var(--pad)}.step-row .num{margin-bottom:18px}.win{aspect-ratio:4/3}.dv-held{grid-template-columns:minmax(0,1fr)!important}
.card{grid-template-columns:minmax(0,1fr);min-height:0}.dv-held-m{font-family:var(--display);font-weight:var(--dw)!important;text-transform:var(--dcase);letter-spacing:var(--dls)!important}
}
/* software: the product is the picture, the type is quiet (harvest-saas 2026-11-11: h1 64 px median, 8 reveals a page) */
.open-prod{min-height:0;align-content:start;padding-top:clamp(104px,13svh,150px);padding-bottom:0;overflow:hidden}.open-prod .wrap{padding-bottom:0}.open-prod .open-foot{margin-top:clamp(24px,3.4svh,40px)}
.open-prod.centre .wrap{text-align:center}.open-prod.centre .display{margin-inline:auto}.open-prod.centre .open-foot{grid-template-columns:minmax(0,1fr);justify-items:center}.open-prod.centre .lede{margin-inline:auto}.open-prod.centre .acts{justify-content:center}
.op-stage{margin:clamp(32px,5svh,64px) var(--pad) 0;padding:clamp(18px,4vw,64px) clamp(14px,5vw,88px) 0;border-radius:20px 20px 0 0;background:linear-gradient(160deg,color-mix(in srgb,var(--accent) 26%,var(--ground2)),color-mix(in srgb,var(--accent) 7%,var(--ground2)) 62%);max-height:max(52svh,360px);overflow:hidden}.op-stage .dv-window{border-radius:12px 12px 0 0}
.op-stage.tall{display:grid;justify-items:center;padding-inline:clamp(14px,4vw,64px)}.op-stage.tall .dv-phone{--pw:clamp(230px,25vw,350px)}
.pl-grid{display:grid;grid-template-columns:repeat(var(--n,3),minmax(0,1fr));gap:clamp(10px,1.2vw,18px);margin-top:clamp(40px,5vw,80px);align-items:stretch}.pl{display:flex;flex-direction:column;gap:14px;padding:clamp(20px,2.2vw,32px);border-radius:18px;box-shadow:inset 0 0 0 1px var(--line)}
.pl.is-marked{background:var(--lead);color:var(--on-lead);box-shadow:none;--line:color-mix(in srgb,var(--on-lead) 22%,transparent);--mute:color-mix(in srgb,var(--on-lead) 72%,transparent)}.pl-name{color:var(--mute)}.pl-price{font-family:var(--display);font-weight:var(--dw);letter-spacing:var(--dls);line-height:1;font-size:clamp(34px,3.4vw,52px)}.pl-price small{font-family:var(--mono);font-size:12px;letter-spacing:.04em;margin-left:8px;color:var(--mute)}
.pl-for{color:var(--mute);min-height:3em}.pl .btn{align-self:flex-start}.pl-points{display:grid;gap:9px;margin-top:8px;padding-top:18px;border-top:1px solid var(--line);font-size:15px}.pl-points li{padding-left:22px;position:relative}.pl-points li::before{content:"✓";position:absolute;left:0;font-size:12px;top:.2em;color:var(--mute)}.plans .note{margin-top:22px}
.cmp{margin-top:clamp(40px,5vw,80px);overflow-x:auto}.cmp table{width:100%;min-width:calc(220px + var(--n,3) * 120px);border-collapse:collapse;table-layout:fixed;font-size:15px}.cmp thead td{width:38%}.cmp thead th{position:sticky;top:0;text-align:left;font-family:var(--mono);font-size:12px;letter-spacing:.08em;text-transform:uppercase;font-weight:400;padding:14px 12px;background:var(--paper);box-shadow:inset 0 -1px 0 var(--line)}
.cmp tbody th{text-align:left;font-weight:400;padding:13px 12px 13px 0;width:38%}.cmp td{padding:13px 12px;color:var(--mute)}.cmp tbody tr{border-bottom:1px solid var(--line)}.cmp-g th{font-family:var(--display);font-weight:var(--dw);font-size:clamp(18px,1.5vw,22px);padding-top:clamp(28px,3vw,44px)!important;color:var(--ink)}.cmp-y{color:var(--ink)}.cmp-n{opacity:.45}
.scale-product .display{font-size:min(clamp(38px,4.7vw,80px),calc((100vw - 2 * var(--pad)) / var(--lw,8) * var(--k)));line-height:1.03}.scale-product .h2{font-size:min(clamp(30px,3.3vw,56px),calc((100vw - 2 * var(--pad)) / var(--lw,8) * var(--k)));line-height:1.06}.scale-product .thesis{font-size:clamp(24px,2.6vw,44px);line-height:1.14}.scale-product .sc{padding-block:clamp(64px,7vw,120px)}.scale-product .open-prod{padding-bottom:0}
.op-stage.has-ground{position:relative;isolation:isolate;background:var(--night);padding-top:clamp(44px,9vw,150px)}.op-ground{position:absolute;inset:0;z-index:-1;width:100%;height:100%;object-fit:cover}.op-stage.has-ground::before{content:"";position:absolute;inset:0;z-index:-1;background:linear-gradient(180deg,transparent 40%,rgba(0,0,0,.35))}
/* the client's character decides how much moves and how loud the type is — not its trade */
.dv .scale-product [data-rise]{transition-duration:.26s}.dv .scale-product [data-rise]:not(.is-in){transform:translateY(22px)}   /* harvest-saas home pages: travel 22 px median (n=7), 248 ms; fade 258 ms (n=10) */
.dv .ft[data-rise],.dv .pl[data-rise],.dv .b-tile[data-rise]{transition-duration:.55s;transition-delay:calc(var(--i,0) * 90ms)}.dv .ft[data-rise]:not(.is-in),.dv .pl[data-rise]:not(.is-in),.dv .b-tile[data-rise]:not(.is-in){transform:translateY(40px) scale(.985)}   /* a card is a thing that arrives: each as it enters, its neighbours a beat apart */
.dv .ch-calm .ft[data-rise]:not(.is-in),.dv .ch-calm .pl[data-rise]:not(.is-in),.dv .ch-calm .b-tile[data-rise]:not(.is-in){transform:translateY(22px)}.dv .ch-calm .ft[data-rise],.dv .ch-calm .pl[data-rise]{transition-duration:.3s;transition-delay:calc(var(--i,0) * 60ms)}   /* a calm brand's cards arrive too, quietly: how far and how long follows the character */
.scale-product.ch-energetic .display,.scale-product.ch-playful .display{font-size:min(clamp(44px,6.4vw,112px),calc((100vw - 2 * var(--pad)) / var(--lw,8) * var(--k)));line-height:.98}.scale-product.ch-energetic .h2,.scale-product.ch-playful .h2{font-size:min(clamp(34px,4.4vw,76px),calc((100vw - 2 * var(--pad)) / var(--lw,8) * var(--k)))}
@media (max-width:900px){.pl-grid{grid-template-columns:minmax(0,1fr)}.pl-for{min-height:0}.op-stage{margin-inline:0;border-radius:0;max-height:none;padding-bottom:0}.op-stage.tall .dv-phone{--pw:min(72vw,300px)}.cmp tbody th{width:auto;min-width:150px}}
.ft-grid{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:clamp(10px,1.2vw,18px);margin-top:clamp(40px,5vw,80px)}.ft{grid-column:span 6;display:flex;flex-direction:column;gap:clamp(20px,2.4vw,36px);background:var(--ground2);border-radius:22px;padding:clamp(20px,2.4vw,36px) clamp(20px,2.4vw,36px) 0;overflow:hidden;min-height:clamp(320px,34vw,520px)}
.ft-0{grid-column:span 7}.ft-1{grid-column:span 5}.ft-n3 .ft-2{grid-column:span 12;flex-direction:row;align-items:flex-end;min-height:0}.ft-n3 .ft-2 .ft-words{flex:0 0 34%;padding-bottom:clamp(20px,2.4vw,36px)}.ft-n3 .ft-2 .ft-pic{flex:1}.ft-n5 .ft-2,.ft-n5 .ft-3,.ft-n5 .ft-4{grid-column:span 4}.ft-n4 .ft-2{grid-column:span 5}.ft-n4 .ft-3{grid-column:span 7}
.ft h3{font-family:var(--display);font-weight:var(--dw);text-transform:var(--dcase);letter-spacing:var(--dls);line-height:1.04;font-size:clamp(22px,2.2vw,36px);max-width:16ch}.ft p{margin-top:10px;color:var(--mute);max-width:40ch}
.ft-pic{margin-top:auto;width:100%}.ft-shot{margin:0;border-radius:10px 10px 0 0;overflow:hidden;box-shadow:0 0 0 1px var(--line);max-height:clamp(200px,24vw,380px)}.ft-shot img{display:block;width:max(100%,min(var(--w,100%),860px));max-width:none;height:auto}   /* the interface is shown near its own size and cut by the card, not shrunk until its words cannot be read */.ft-phone{display:grid;justify-items:center;max-height:clamp(240px,28vw,420px);overflow:hidden}.ft-phone .dv-phone{--pw:clamp(170px,17vw,250px)}
@media (max-width:900px){.ft,.ft-0,.ft-1,.ft-2,.ft-3,.ft-4{grid-column:1/-1!important;min-height:0;flex-direction:column!important;align-items:stretch!important}.ft-n3 .ft-2 .ft-words{padding-bottom:0}}
"""


def page(plan, images):
    """The document: the plan's type system and palette, its scenes in its order, the library's code for the devices they use."""
    brand = plan.get('brand') or {}; t = TYPE.get(plan.get('type')) or TYPE['light-grotesk']; p = palette(brand.get('accent') or '#2f6bff', brand.get('night') or '#0e0f12', plan.get('scheme') if plan.get('scheme') in SCHEMES else 'paper')
    ctx = {'images': images, 'brand': brand, 'action': plan.get('action') or {}, 'action2': plan.get('action2')}
    body, used = [], {'overlay-menu', 'rise-stagger', 'roll', 'progress', 'bar-tuck', 'grain', 'curtain-foot'}
    for sc in plan.get('scenes') or []:
        meta = SCENES.get(sc.get('scene'))
        if not meta: continue
        html = meta['render'](sc.get('slots') or {}, ctx)
        if html and sc.get('cover') in (True, 'true') and body and html.startswith('<section class="'): html = html.replace('<section class="', '<section class="dv-cover ', 1); used.add('cover')
        if html: body.append(html); used |= set(meta['devices'])
    if plan.get('eased'): used.add('eased-scroll')
    drawn = plan.get('mark') == 'drawn'; quiet = plan.get('scale') == 'product'
    if drawn: used.add('draw')
    css, js = LIB.bundle(sorted(used))
    nav = [n for n in plan.get('nav') or [] if n.get('label') and n.get('url')][:5]
    links = ''.join(f'<a href="{e(n["url"])}">{e(n["label"])}</a>' for n in nav)
    tokens = (f":root{{--paper:{p['paper']};--ink:{p['ink']};--accent:{p['accent']};--em:{p['em']};--on-accent:{p['on_accent']};--ground2:{p['ground2']};--mute:{p['mute']};--line:{p['line']};--night:{p['night']};--on-night:{p['on_night']};--lead:{p['lead']};--on-lead:{p['on_lead']};"
              f"--display:{t['display']};--dw:{t['w']};--dls:{t['ls']};--dlh:{t['lh']};--dcase:{t['case']};--k:{t['k']};--text:{t['text']};--mono:{t['mono']};--pad:clamp(20px,3.4vw,56px)}}")
    main = [b for b in body if '<footer' not in b]; foot = [b for b in body if '<footer' in b]
    under = ''.join(foot).replace('<footer class="', '<footer class="dv-under ', 1)   # named outside the f-string: nested quotes there need Python 3.12
    return (f'<!doctype html><html lang="{e(brand.get("lang") or "en")}"{" data-eased-scroll" if plan.get("eased") else ""}><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(plan.get("title") or brand.get("name"))}</title>'
            f'<meta name="description" content="{e(plan.get("description"))}"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family={t["gf"]}&display=swap" rel="stylesheet">'
            f'<style>{tokens}{CSS}{css}</style></head><body class="{e(plan.get("type") or "light-grotesk")}{" mark-drawn" if drawn else ""}{" scale-product" if quiet else ""}{" ch-" + plan["character"] if plan.get("character") in ("calm", "energetic", "warm", "refined", "playful") else ""}"><a class="skip" href="#main">Skip to content</a>'
            f'<div class="dv-progress" aria-hidden="true"></div><header class="bar dv-tuck"><a class="name" href="#top">{e(brand.get("name"))}</a><div class="bar-r">' + (f'<nav class="bar-links" aria-label="Primary">{links}</nav>' if links else '')
            + f'{_btn(ctx["action"])}<button class="dv-menu-btn mono" aria-expanded="false" aria-controls="menu">Menu</button></div></header>'
            f'<nav class="dv-menu" id="menu" aria-label="Menu">{links}<a class="btn" href="{e((ctx["action"] or {}).get("url") or "#top")}">{e((ctx["action"] or {}).get("label") or "")}</a></nav>'
            f'<main id="main" class="dv-sheet">{"".join(main)}</main>{under}<div class="dv-grain" aria-hidden="true"></div><script>{js}</script></body></html>')


def keep(page_html, inventory):
    """The client's search standing, kept without being shown as a dump: every source section whose words the page does
    not already carry, and every same-site link the page lost, in ONE quiet row before the close that a reader may open;
    the source's canonical address and structured data in the head. Nothing a search engine read on the old page is
    missing from this one. Deterministic; returns the page."""
    import seo as SEO
    text = re.sub(r'<[^>]+>', ' ', re.sub(r'<(script|style)\b.*?</\1>', ' ', page_html, flags=re.S))
    items = []
    for sec in SEO.source_sections(inventory):
        words = ' '.join(str(sec.get('text') or '').split())
        if len(words.split()) < 8 or SEO.text_coverage(words, text) >= .85: continue
        faq = ''.join(f'<p><b>{e(q.get("question"))}</b> {e(q.get("answer"))}</p>' for q in (sec.get('faq') or []) if isinstance(q, dict) and q.get('answer'))
        items.append(f'<details><summary><span>{e(sec.get("title"))}</span></summary><p>{e(words[:6000])}</p>{faq}</details>')
    rest = SEO.leftover(inventory, text + ' ' + ' '.join(re.sub(r'<[^>]+>', ' ', i) for i in items))
    if rest: items.append(f'<details><summary><span>{e((inventory or {}).get("title") or (inventory or {}).get("url") or "")[:90]}</span></summary>' + ''.join(f'<p>{e(piece)}</p>' for piece in rest) + '</details>')
    hrefs = {h.rstrip('/') for h in re.findall(r'href="([^"]+)"', page_html)}
    lost = [l for l in SEO.internal_links(inventory) if str(l.get('href') or '').rstrip('/') not in hrefs]
    links = ''.join(f'<li><a href="{e(l["href"])}">{e(l["text"])}</a></li>' for l in lost)
    out = page_html
    if items or links:
        lang = str((inventory or {}).get('lang') or '').lower().split('-')[0]
        title = {'sr': 'Više o nama', 'hr': 'Više o nama', 'es': 'Más información', 'fr': 'En savoir plus', 'de': 'Mehr erfahren', 'it': 'Maggiori informazioni', 'pt': 'Mais informações'}.get(lang, 'More about us')
        block = (f'<section class="sc keep" id="more-about"><div class="wrap"><details class="keep-all"><summary><span class="mono">{e(title)}</span></summary><div class="acc">{"".join(items)}</div>'
                 + (f'<ul class="keep-links">{links}</ul>' if links else '') + '</details></div></section>')
        at = out.find('</main>'); out = out[:at] + block + out[at:] if at >= 0 else out
    seo = (inventory or {}).get('seo') or {}; head = ''
    if seo.get('canonical') and 'rel="canonical"' not in out: head += f'<link rel="canonical" href="{e(seo["canonical"])}">'
    if 'application/ld+json' not in out:   # the source's structured data, as the source wrote it
        for raw in ((seo.get('structuredData') or {}).get('raw') or seo.get('jsonld') or [])[:6]:
            if not isinstance(raw, str): raw = __import__('json').dumps(raw, ensure_ascii=False)
            try: __import__('json').loads(raw)
            except ValueError: continue
            head += '<script type="application/ld+json">' + raw.replace('</', '<\\/') + '</script>'
    if head: out = out.replace('</head>', head + '</head>', 1)
    return out


def catalogue():
    return {'scenes': [{k: v for k, v in m.items() if k != 'render'} for m in SCENES.values()], 'type': {k: v['name'] for k, v in TYPE.items()}, 'schemes': {'paper': 'white ground, dark ink', 'night': "the client's dark ground, light ink", 'tint': 'a paper carrying a breath of the accent', 'tone': 'three steps of one muted tone from the brand colour: a pale ground, a middle ground, near black'}}
