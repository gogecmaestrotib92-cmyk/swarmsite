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


def mark(text):
    parts = re.split(r'\*([^*]+)\*', str(text or '')); return ''.join(f'<em>{e(p)}</em>' if i % 2 else e(p) for i, p in enumerate(parts))


def lines(text, cls='display'):
    """A display line as masked rows: the writer breaks it with ' / ' (two to four rows); each row rises on its own."""
    rows = [r.strip() for r in str(text or '').split(' / ') if r.strip()] or ['']
    longest = max((len(w) for r in rows for w in re.sub(r'\*', '', r).split()), default=6)
    return f'<span class="dv-lines {cls}" style="--lw:{max(4, longest)}">' + ''.join(f'<span class="dv-ln"><span>{mark(r)}</span></span>' for r in rows) + '</span>'


# ---- type: systems of different character. k = how many px of font-size one character of the longest word needs room for ----
TYPE = {
    'light-grotesk': {'name': 'Light grotesque — calm, exact, technical', 'display': "'Geist',system-ui,sans-serif", 'w': 300, 'ls': '-.035em', 'lh': '.98', 'case': 'none', 'k': 1.9, 'text': "'Geist',system-ui,sans-serif", 'mono': "'Geist Mono',ui-monospace,monospace", 'gf': 'Geist:wght@300;400;500&family=Geist+Mono:wght@400;500'},
    'condensed-caps': {'name': 'Condensed capitals — loud, sporting, poster', 'display': "'Barlow Condensed',Impact,sans-serif", 'w': 800, 'ls': '-.01em', 'lh': '.86', 'case': 'uppercase', 'k': 2.7, 'text': "'IBM Plex Sans',system-ui,sans-serif", 'mono': "'IBM Plex Mono',ui-monospace,monospace", 'gf': 'Barlow+Condensed:wght@700;800&family=IBM+Plex+Sans:wght@400;500&family=IBM+Plex+Mono:wght@400;500'},
    'display-serif': {'name': 'Display serif — editorial, warm, considered', 'display': "'Instrument Serif',Georgia,serif", 'w': 400, 'ls': '-.02em', 'lh': '.95', 'case': 'none', 'k': 2.2, 'text': "'Inter',system-ui,sans-serif", 'mono': "'JetBrains Mono',ui-monospace,monospace", 'gf': 'Instrument+Serif:ital@0;1&family=Inter:wght@400;500&family=JetBrains+Mono:wght@400;500'},
    'tight-bold': {'name': 'Tight bold grotesque — confident, product, direct', 'display': "'Inter Tight',system-ui,sans-serif", 'w': 700, 'ls': '-.045em', 'lh': '.92', 'case': 'none', 'k': 1.8, 'text': "'Inter',system-ui,sans-serif", 'mono': "'JetBrains Mono',ui-monospace,monospace", 'gf': 'Inter+Tight:wght@600;700&family=Inter:wght@400;500&family=JetBrains+Mono:wght@400;500'},
    'soft-serif': {'name': 'Soft old-style serif — hospitality, craft, slow', 'display': "'Fraunces',Georgia,serif", 'w': 400, 'ls': '-.03em', 'lh': '.96', 'case': 'none', 'k': 2.0, 'text': "'Figtree',system-ui,sans-serif", 'mono': "'DM Mono',ui-monospace,monospace", 'gf': 'Fraunces:opsz,wght@9..144,300;9..144,400&family=Figtree:wght@400;500&family=DM+Mono:wght@400;500'},
    'wide-geometric': {'name': 'Geometric grotesque — design-led, modern, a little odd', 'display': "'Space Grotesk',system-ui,sans-serif", 'w': 500, 'ls': '-.04em', 'lh': '.94', 'case': 'none', 'k': 1.75, 'text': "'Space Grotesk',system-ui,sans-serif", 'mono': "'Space Mono',ui-monospace,monospace", 'gf': 'Space+Grotesk:wght@400;500&family=Space+Mono:wght@400'},
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


SCHEMES = ('paper', 'night', 'tint')


def palette(accent, night='#0e0f12', scheme='paper'):
    """The page's colours from the client's own two: its signature colour and its darkest ground. `paper`: white with
    ink; `night`: the client's dark with light ink; `tint`: a paper carrying a breath of the accent. Text always clears
    4.5:1; where the accent cannot carry text on the ground it is kept for fills and the ink takes the emphasis."""
    night = night if _lum(night) < .08 else '#0e0f12'
    if scheme == 'night': paper, ink = night, '#f1f1ee'
    elif scheme == 'tint': paper, ink = _mix('#ffffff', accent, .07), _mix(night, '#000000', .2)
    else: paper, ink = '#ffffff', _mix(night, '#000000', .1)
    ground2 = _mix(paper, ink, .06 if scheme != 'night' else .08)
    em = accent if contrast(accent, paper) >= 3 else ink   # a marked word must be readable: large type needs 3:1
    return {'paper': paper, 'ink': ink, 'accent': accent, 'em': em, 'on_accent': '#0b0c0f' if _lum(accent) > .32 else '#ffffff', 'ground2': ground2,
            'mute': _mix(ink, paper, .38), 'line': _mix(paper, ink, .14), 'night': night, 'on_night': '#f1f1ee', 'scheme': scheme}


# ---- scenes ----
SCENES = {}


def scene(id, **meta):
    def wrap(fn): SCENES[id] = {**meta, 'id': id, 'render': fn}; return fn
    return wrap


def _btn(a, cls=''):
    return f'<a class="btn {cls}" href="{e(a.get("url"))}">{e(a.get("label"))}</a>' if isinstance(a, dict) and a.get('label') and a.get('url') else ''


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
    return (f'<section class="sc open open-pic" id="top"><div class="wrap"><p class="mono kicker" data-rise>{e(s.get("kicker"))}</p><h1>{lines(s.get("h1"))}</h1>'
            f'<div class="open-foot"><p class="lede" data-rise style="--i:1">{e(s.get("lede"))}</p><div class="acts" data-rise style="--i:2">{_btn(ctx["action"], "dv-magnet")}{_btn(ctx.get("action2"), "quiet")}</div></div></div>'
            f'<figure class="dv-grow">{_shot(ctx["images"], s.get("image"), s.get("alt"))}</figure></section>')


@scene('held-product', name='The product, claim by claim, held', role='show', devices=['held-index', 'figure-bars', 'scramble', 'rise-stagger'],
       needs='3–5 claims; each with a real screenshot shown LARGE (prefer the tight crops) or 2–5 comparable real figures or 3–6 label/value rows',
       slots={'label': 'mono', 'intro': 'one sentence standing under the list', 'items': [{'title': '≤ 26 chars', 'say': 'one or two sentences', 'panel': {'kind': 'image|bars|rows', 'image': 'id', 'alt': '', 'chip': 'mono caption', 'bars': [{'label': '', 'value': '', 'share': '0–1'}], 'rows': [{'k': '', 'v': ''}]}}]})
def _held_product(s, ctx):
    items = [i for i in s.get('items') or [] if i.get('title')][:5]

    def panel(p):
        chip = f'<span class="mono chip">{e(p["chip"])}</span>' if p.get('chip') else ''
        if p.get('kind') == 'image' and p.get('image') in ctx['images']: return f'<figure class="panel panel-img">{chip}<div class="shot">{_shot(ctx["images"], p["image"], p.get("alt"))}</div></figure>'
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
    figs = ''.join(fig(k, f) for k, f in enumerate((s.get('figures') or [])[:4]) if f.get('value'))
    return (f'<section class="sc figures alt" id="record"><div class="wrap"><p class="mono kicker">{e(s.get("label"))}</p><h2>{lines(s.get("h2"), "h2")}</h2><ul class="figs">{figs}</ul>'
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
    markw = f'<div class="dv-endmark" style="--chars:{max(4, len(name))}" aria-hidden="true">{e(name)}</div>' if s.get('wordmark') and 3 <= len(name) <= 14 else ''
    return (f'<footer class="sc close night" id="end"><div class="wrap"><h2>{lines(s.get("line"))}</h2><div class="acts" data-rise>{_btn(ctx["action"], "dv-magnet")}{_btn(ctx.get("action2"), "quiet")}</div>'
            + (f'<p class="mono note">{e(s["note"])}</p>' if s.get('note') else '') + (f'<div class="cols">{cols}</div>' if cols else '') + f'<p class="mono legal">{e(s.get("legal"))}</p></div>{markw}</footer>')


CSS = """
*{box-sizing:border-box;margin:0}html{-webkit-text-size-adjust:100%}
body{font-family:var(--text);font-size:clamp(15px,1.11vw,17px);line-height:1.5;color:var(--ink);background:var(--paper);-webkit-font-smoothing:antialiased;overflow-x:clip}
a{color:inherit}img{display:block;max-width:100%;height:auto}ul,ol{list-style:none;padding:0}
:focus-visible{outline:2px solid var(--accent);outline-offset:3px}
.skip{position:absolute;left:-999px}.skip:focus{left:16px;top:16px;z-index:99;background:var(--paper);color:var(--ink);padding:10px 14px}
.wrap{padding-inline:var(--pad);max-width:1760px;margin-inline:auto}.sc{padding-block:clamp(88px,13vw,224px)}
.mono{font-family:var(--mono);font-size:12px;line-height:1.35;letter-spacing:.08em;text-transform:uppercase}.kicker{color:var(--mute);margin-bottom:clamp(20px,2.4vw,36px)}.note{color:var(--mute);margin-top:22px}
em{font-style:normal;color:var(--em)}.display-serif em,.soft-serif em{font-style:italic}
.display,.h2{display:block;font-family:var(--display);font-weight:var(--dw);letter-spacing:var(--dls);line-height:var(--dlh);text-transform:var(--dcase)}
.display{font-size:min(clamp(48px,11.6vw,196px),calc((100vw - 2 * var(--pad)) / var(--lw,8) * var(--k)))}
.h2{font-size:min(clamp(40px,8.2vw,140px),calc((100vw - 2 * var(--pad)) / var(--lw,8) * var(--k)))}
.lede{font-size:clamp(16px,1.3vw,20px);line-height:1.42;max-width:38ch}
.btn{display:inline-flex;align-items:center;justify-content:center;min-height:54px;padding:0 24px;border-radius:999px;background:var(--accent);color:var(--on-accent);font-family:var(--mono);font-size:12px;letter-spacing:.08em;text-transform:uppercase;text-decoration:none;white-space:nowrap;transition:transform .2s var(--ease),filter .2s}
.btn:hover{filter:brightness(1.07)}.btn:active{transform:scale(.97)}.btn.quiet{background:none;color:inherit;box-shadow:inset 0 0 0 1px var(--line)}.btn.small{min-height:44px;padding:0 18px}
.acts{display:flex;flex-wrap:wrap;gap:12px}
/* bar */
.bar{position:fixed;inset:0 0 auto 0;z-index:40;display:flex;align-items:center;justify-content:space-between;gap:16px;padding:14px var(--pad);mix-blend-mode:normal}
.bar .name{font-family:var(--display);font-weight:var(--dw);text-transform:var(--dcase);letter-spacing:var(--dls);font-size:clamp(20px,1.7vw,26px);text-decoration:none;white-space:nowrap}
.bar-r{display:flex;align-items:center;gap:10px}.bar-links{display:flex;gap:6px;padding:0 8px;min-height:44px;align-items:center;border-radius:999px;background:color-mix(in srgb,var(--paper) 82%,transparent);backdrop-filter:blur(14px)}
.bar-links a{font-family:var(--mono);font-size:12px;letter-spacing:.08em;text-transform:uppercase;text-decoration:none;padding:10px 12px}.bar .btn{min-height:44px;padding:0 18px}.dv-menu-btn{display:none}
/* open */
.open{min-height:100svh;display:grid;align-content:end;padding-top:clamp(120px,16vh,200px);padding-bottom:0}.open .wrap{width:100%;padding-bottom:clamp(40px,6vh,80px)}
.open-foot{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:clamp(24px,4vw,64px);align-items:end;margin-top:clamp(28px,4vw,64px)}.open-foot .note{grid-column:1/-1;margin-top:0}
.open-tick{border-top:1px solid var(--line);padding:22px 0;color:var(--mute)}.open-pic{padding-bottom:clamp(88px,13vw,224px)}.open-pic .dv-grow{margin-top:clamp(40px,6vw,96px)}
/* held product */
.held{background:var(--ground2)}.dv-held{grid-template-columns:minmax(0,5fr) minmax(0,7fr)!important}.dv-held-names li{font-family:var(--display);font-weight:var(--dw);text-transform:var(--dcase);letter-spacing:var(--dls);font-size:clamp(30px,3.6vw,60px)!important;line-height:1.04!important}
.held-intro{margin-top:clamp(24px,3vw,44px);max-width:30ch;color:var(--mute)}.dv-held-item{display:grid;gap:clamp(18px,2vw,28px)}.say{font-size:clamp(17px,1.5vw,22px);line-height:1.38;max-width:34ch}
.panel{position:relative;background:var(--paper);border-radius:14px;padding:clamp(16px,2vw,28px);display:grid;gap:14px;margin:0}.panel-img{padding:clamp(10px,1vw,14px)}.panel .chip{color:var(--mute)}
.shot{border-radius:9px;overflow:hidden;box-shadow:0 0 0 1px var(--line)}.shot img{width:100%}
.dv-bars li{font-size:12px}.dv-bars .v{font-family:var(--display);font-weight:var(--dw);font-size:clamp(22px,2.2vw,34px);letter-spacing:var(--dls)}
.kv li{display:flex;justify-content:space-between;gap:20px;align-items:baseline;padding:14px 0;border-top:1px solid var(--line)}.kv li:first-child{border-top:0}.kv b{font-family:var(--display);font-weight:var(--dw);font-size:clamp(22px,2.2vw,34px);letter-spacing:var(--dls);text-align:right;text-transform:var(--dcase)}
/* figures */
.alt{background:var(--paper)}.figs{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,15rem),1fr));gap:clamp(32px,5vw,88px) clamp(24px,3vw,56px);margin-top:clamp(48px,7vw,120px);border-top:1px solid var(--line);padding-top:clamp(28px,3vw,48px)}
.fig{font-family:var(--display);font-weight:var(--dw);letter-spacing:var(--dls);line-height:.9;font-size:clamp(56px,8vw,136px);text-transform:var(--dcase);white-space:nowrap}.fig small{font-size:.32em;letter-spacing:0;margin-left:.2em;color:var(--mute)}.cap{margin-top:14px;max-width:26ch;color:var(--mute)}
/* rail */
.rail-sc{padding-block:clamp(40px,6vw,96px)}.dv-rail-row span{font-family:var(--display);font-weight:var(--dw);text-transform:var(--dcase);letter-spacing:var(--dls);line-height:1;font-size:clamp(72px,15vw,260px);white-space:nowrap}
.dv-rail-row .hollow{color:transparent;-webkit-text-stroke:max(1px,.012em) var(--ink)}
/* stage */
.stage{background:var(--night);color:var(--on-night);--line:color-mix(in srgb,var(--on-night) 16%,transparent);--mute:color-mix(in srgb,var(--on-night) 62%,transparent);--em:var(--accent)}
.stage-head{display:grid;grid-template-columns:minmax(0,7fr) minmax(0,4fr);gap:clamp(24px,4vw,64px);align-items:end;margin-bottom:clamp(40px,6vw,96px)}.stage-fig{margin:0}.stage-fig .shot{border-radius:14px}.chips{display:flex;flex-wrap:wrap;gap:8px 28px;margin-top:18px;color:var(--mute)}
/* stack */
.stack-sc h2{margin-bottom:clamp(40px,6vw,96px)}.card{background:var(--ground2);border-radius:18px;padding:clamp(24px,3vw,48px);display:grid;grid-template-columns:minmax(0,4fr) minmax(0,5fr) auto;gap:clamp(20px,3vw,48px);align-items:start;min-height:clamp(220px,22vw,340px);box-shadow:0 -1px 0 var(--paper)}
.card h3{font-family:var(--display);font-weight:var(--dw);text-transform:var(--dcase);letter-spacing:var(--dls);line-height:1;font-size:clamp(32px,4vw,64px)}.card .kicker{margin-bottom:14px}.card-say ul{margin-top:14px;display:grid;gap:6px;color:var(--mute)}.card-say li::before{content:"— "}
/* ledger, index */
.ledger-in{display:grid;grid-template-columns:minmax(0,4fr) minmax(0,8fr);gap:clamp(24px,4vw,64px)}.h3x{font-family:var(--display);font-weight:var(--dw);text-transform:var(--dcase);letter-spacing:var(--dls);line-height:1.02;font-size:clamp(30px,3.6vw,60px);max-width:12ch}
.rows .row{display:grid;grid-template-columns:minmax(0,5fr) minmax(0,6fr);gap:clamp(16px,2.4vw,40px);padding:clamp(18px,2vw,28px) 0;border-top:1px solid var(--line)}.rows h3{font:500 clamp(16px,1.3vw,19px)/1.35 var(--text)}.rows p{color:var(--mute)}
.index{padding-block:clamp(56px,7vw,112px);background:var(--ground2)}.index-in{display:grid;grid-template-columns:minmax(0,4fr) minmax(0,8fr);gap:clamp(24px,4vw,64px)}.index ul{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,15rem),1fr));column-gap:clamp(24px,3vw,48px)}
.index a{display:flex;justify-content:space-between;align-items:center;gap:12px;min-height:54px;border-bottom:1px solid var(--line);text-decoration:none;transition:padding .25s var(--ease)}.index a::after{content:"→";font-family:var(--mono);opacity:.45}.index a:hover{padding-left:8px}
/* close */
.night{background:var(--night);color:var(--on-night);--line:color-mix(in srgb,var(--on-night) 16%,transparent);--mute:color-mix(in srgb,var(--on-night) 62%,transparent);--em:var(--accent)}
.close{padding-bottom:0;overflow:hidden}.close .acts{margin-top:clamp(28px,4vw,64px)}.close .cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,11rem),1fr));gap:clamp(24px,4vw,64px);margin-top:clamp(72px,10vw,160px);padding-top:28px;border-top:1px solid var(--line)}
.close .cols p{color:var(--mute);margin-bottom:12px}.close .cols a{display:block;padding:5px 0;text-decoration:none}.close .cols a:hover{text-decoration:underline;text-underline-offset:.25em}.legal{color:var(--mute);padding:clamp(40px,5vw,72px) 0 28px}
.dv-endmark{font-family:var(--display);font-weight:var(--dw);text-transform:var(--dcase);color:var(--on-night);opacity:.94}
@media (max-width:900px){
.bar-links{display:none}.dv-menu-btn{display:inline-flex;align-items:center}.bar .btn{display:none}
.open-foot,.stage-head,.ledger-in,.index-in,.rows .row{grid-template-columns:minmax(0,1fr)}.dv-held{grid-template-columns:minmax(0,1fr)!important}
.card{grid-template-columns:minmax(0,1fr);min-height:0}.dv-held-m{font-family:var(--display);font-weight:var(--dw)!important;text-transform:var(--dcase);letter-spacing:var(--dls)!important}
}
"""


def page(plan, images):
    """The document: the plan's type system and palette, its scenes in its order, the library's code for the devices they use."""
    brand = plan.get('brand') or {}; t = TYPE.get(plan.get('type')) or TYPE['light-grotesk']; p = palette(brand.get('accent') or '#2f6bff', brand.get('night') or '#0e0f12', plan.get('scheme') if plan.get('scheme') in SCHEMES else 'paper')
    ctx = {'images': images, 'brand': brand, 'action': plan.get('action') or {}, 'action2': plan.get('action2')}
    body, used = [], {'overlay-menu', 'rise-stagger'}
    for sc in plan.get('scenes') or []:
        meta = SCENES.get(sc.get('scene'))
        if not meta: continue
        html = meta['render'](sc.get('slots') or {}, ctx)
        if html: body.append(html); used |= set(meta['devices'])
    if plan.get('eased'): used.add('eased-scroll')
    css, js = LIB.bundle(sorted(used))
    nav = [n for n in plan.get('nav') or [] if n.get('label') and n.get('url')][:5]
    links = ''.join(f'<a href="{e(n["url"])}">{e(n["label"])}</a>' for n in nav)
    tokens = (f":root{{--paper:{p['paper']};--ink:{p['ink']};--accent:{p['accent']};--em:{p['em']};--on-accent:{p['on_accent']};--ground2:{p['ground2']};--mute:{p['mute']};--line:{p['line']};--night:{p['night']};--on-night:{p['on_night']};"
              f"--display:{t['display']};--dw:{t['w']};--dls:{t['ls']};--dlh:{t['lh']};--dcase:{t['case']};--k:{t['k']};--text:{t['text']};--mono:{t['mono']};--pad:clamp(20px,3.4vw,56px)}}")
    main = [b for b in body if '<footer' not in b]; foot = [b for b in body if '<footer' in b]
    return (f'<!doctype html><html lang="{e(brand.get("lang") or "en")}"{" data-eased-scroll" if plan.get("eased") else ""}><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(plan.get("title") or brand.get("name"))}</title>'
            f'<meta name="description" content="{e(plan.get("description"))}"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family={t["gf"]}&display=swap" rel="stylesheet">'
            f'<style>{tokens}{CSS}{css}</style></head><body class="{e(plan.get("type") or "light-grotesk")}"><a class="skip" href="#main">Skip to content</a>'
            f'<header class="bar"><a class="name" href="#top">{e(brand.get("name"))}</a><div class="bar-r">' + (f'<nav class="bar-links" aria-label="Primary">{links}</nav>' if links else '')
            + f'{_btn(ctx["action"])}<button class="dv-menu-btn mono" aria-expanded="false" aria-controls="menu">Menu</button></div></header>'
            f'<nav class="dv-menu" id="menu" aria-label="Menu">{links}<a href="{e((ctx["action"] or {}).get("url") or "#top")}">{e((ctx["action"] or {}).get("label") or "")}</a></nav>'
            f'<main id="main">{"".join(main)}</main>{"".join(foot)}<script>{js}</script></body></html>')


def catalogue():
    return {'scenes': [{k: v for k, v in m.items() if k != 'render'} for m in SCENES.values()], 'type': {k: v['name'] for k, v in TYPE.items()}, 'schemes': {'paper': 'white ground, dark ink', 'night': "the client's dark ground, light ink", 'tint': 'a paper carrying a breath of the accent'}}
