"""held_index.py — a studio template, authored whole: its own markup, its own stylesheet, its own motion.

Not a recipe for the shared renderer. One page design rebuilt from the measured mechanics of a reference (see
bench/runs/_research/references/cerebrium/evidence.json, 2026-11-10): a light display face at 86/72/57/44 px against
26/18/16 px text and 13 px mono labels; three grounds (night, paper, mist) and one accent; a first screen whose headline
sits low-left over a full-bleed drawn backdrop with the lede and actions low-right; a section held for three screens —
an index of claims on the left that lights up one at a time, the product shown in panels on the right; boxes at 10 and
15 px corners, actions 54 px tall at 7 px; headline lines that rise 80 px out of a mask in 275 ms, 34 ms apart;
reveals that fade in 300 ms over 12 px, 70 ms apart.

What is NOT taken: the reference's pictures, words, colours, faces or marks. The backdrop is drawn here from the
client's own accent; the faces are open-licence; the palette is the client's.

  render(content, images) → one self-contained HTML document
  SLOTS                    → what `content` holds (the filler writes it; nothing else is drawn)

For: software and services with real product screens or real numbers to show. Needs: 3–5 claims, each with a
picture of the product or a set of true figures. Without them the held section has nothing to hold."""
import html as H, re

e = lambda s: H.escape(str(s if s is not None else ''), quote=True)

SLOTS = {
    'brand': {'name': 'str', 'accent': '#hex', 'night': '#hex (the dark ground)', 'lang': 'en'},
    'nav': [{'label': 'str', 'url': 'url'}], 'action': {'label': 'str', 'url': 'url'}, 'action2': {'label': 'str', 'url': 'url'},
    'hero': {'h1': 'str — one phrase wrapped in *asterisks* takes the accent', 'lede': 'str', 'note': 'str (mono, optional)'},
    'proof': ['short true facts, mono, 4–8'],
    'statement': {'small': 'str', 'big': 'str with one *accent phrase*'},
    'index': {'label': 'str', 'items': [{'title': 'str ≤ 28 chars', 'h3': 'str', 'body': 'str', 'panel': {'kind': 'image|bars|rows', 'image': 'id', 'chip': 'str', 'foot': 'str', 'bars': [{'label': 'str', 'value': 'str', 'share': '0–1'}], 'rows': [{'k': 'str', 'v': 'str'}]}}]},
    'ground': {'label': 'str', 'h2': 'str with *accent*', 'points': [{'title': 'str', 'body': 'str'}]},
    'cards': {'h2': 'str with *accent*', 'items': [{'kicker': 'str', 'title': 'str', 'url': 'url'}]},
    'directory': {'label': 'str', 'links': [{'label': 'str', 'url': 'url'}]},
    'closing': {'line': 'str', 'note': 'str'},
    'footer': {'columns': [{'title': 'str', 'links': [{'label': 'str', 'url': 'url'}]}], 'legal': 'str'},
}


def _mark(text):
    """*phrase* → the accent; everything else escaped."""
    parts = re.split(r'\*([^*]+)\*', str(text or ''))
    return ''.join(f'<em>{e(p)}</em>' if i % 2 else e(p) for i, p in enumerate(parts))


def _lines(text, per=3):
    """A headline as masked lines, a few words each, so each can rise on its own; the browser still wraps inside a line."""
    words = _mark(text)
    return f'<span class="ln"><span>{words}</span></span>'


def _rgb(hexcode):
    h = str(hexcode or '#000000').lstrip('#'); h = ''.join(c * 2 for c in h) if len(h) == 3 else h.ljust(6, '0')[:6]
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _backdrop(accent):
    """The first screen's ground: bands of light drawn from the client's accent — arcs with a lit edge, grain over them.
    Drawn, not photographed and not generated: it claims nothing about the product."""
    r, g, b = _rgb(accent); c = lambda a, k=1.0: f'rgba({int(r * k)},{int(g * k)},{int(b * k)},{a})'
    arcs = ''.join(
        f'<path d="M{x0} 1000 C {x0 + 180} {520 - i * 26}, {x0 + 420} {300 - i * 38}, {x0 + 760} {360 - i * 18} S {x0 + 1180} {700}, {x0 + 1500} 1100" fill="none" stroke="url(#bd{i % 3})" stroke-width="{150 - i * 12}" stroke-linecap="round" opacity="{0.9 - i * 0.09:.2f}"/>'
        for i, x0 in enumerate((-160, 120, 420, 700, 980)))
    return f'''<svg class="bd" viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
<defs>
<linearGradient id="bd0" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="{c(0, .2)}"/><stop offset=".45" stop-color="{c(.55, .42)}"/><stop offset=".8" stop-color="{c(.9, .62)}"/><stop offset="1" stop-color="{c(.25, .3)}"/></linearGradient>
<linearGradient id="bd1" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="{c(0, .15)}"/><stop offset=".5" stop-color="{c(.42, .3)}"/><stop offset="1" stop-color="{c(.7, .5)}"/></linearGradient>
<linearGradient id="bd2" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="{c(0, .1)}"/><stop offset=".6" stop-color="{c(.3, .22)}"/><stop offset="1" stop-color="{c(.5, .36)}"/></linearGradient>
<linearGradient id="bdl" x1="0" y1="1" x2="1" y2="0"><stop offset=".35" stop-color="rgba(255,255,255,0)"/><stop offset=".62" stop-color="rgba(255,255,255,.95)"/><stop offset=".8" stop-color="rgba(255,255,255,0)"/></linearGradient>
<radialGradient id="bdg" cx=".78" cy=".42" r=".6"><stop offset="0" stop-color="{c(.34, .55)}"/><stop offset="1" stop-color="{c(0)}"/></radialGradient>
<filter id="bdb"><feGaussianBlur stdDeviation="7"/></filter><filter id="bdn"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" stitchTiles="stitch"/><feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .11 0"/></filter>
</defs>
<rect width="1440" height="900" fill="url(#bdg)"/>
<g class="bd-arcs" transform="translate(360 0)">{arcs}
<path d="M560 520 C 660 380, 760 330, 860 340" fill="none" stroke="url(#bdl)" stroke-width="16" stroke-linecap="round" filter="url(#bdb)"/>
<path d="M560 520 C 660 380, 760 330, 860 340" fill="none" stroke="url(#bdl)" stroke-width="5" stroke-linecap="round"/></g>
<rect width="1440" height="900" filter="url(#bdn)"/></svg>'''


def _panel(p, images):
    kind = p.get('kind'); chip = f'<span class="chip">{e(p["chip"])}</span>' if p.get('chip') else ''; foot = f'<span class="foot">{e(p["foot"])}</span>' if p.get('foot') else ''
    if kind == 'image' and p.get('image') in images:
        im = images[p['image']]
        body = f'<img src="{im["data"]}" alt="{e(p.get("alt") or "")}" width="{int(im.get("w") or 1200)}" height="{int(im.get("h") or 700)}" loading="lazy">'
        return f'<figure class="panel panel-img">{chip}<div class="shot">{body}</div>{foot}</figure>'
    if kind == 'bars' and p.get('bars'):
        rows = ''.join(f'<li><span class="k">{e(b.get("label"))}</span><span class="bar"><i style="--w:{max(.04, min(1, float(b.get("share") or .5))):.3f}"></i></span><span class="v">{e(b.get("value"))}</span></li>' for b in p['bars'][:6])
        return f'<figure class="panel panel-bars">{chip}<ul class="bars">{rows}</ul>{foot}</figure>'
    rows = ''.join(f'<li><span class="k">{e(r.get("k"))}</span><span class="v">{e(r.get("v"))}</span></li>' for r in (p.get('rows') or [])[:7])
    return f'<figure class="panel panel-rows">{chip}<ul class="rows">{rows}</ul>{foot}</figure>' if rows else ''


CSS = """
*{box-sizing:border-box;margin:0}html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
:root{--night:%(night)s;--paper:#fff;--mist:%(mist)s;--ink:%(ink)s;--accent:%(accent)s;--on-accent:%(on_accent)s;--mute:%(mute)s;--line:%(line)s;
--display:'Geist','Inter Tight',system-ui,sans-serif;--text:'Geist','Inter',system-ui,sans-serif;--mono:'Geist Mono',ui-monospace,monospace;
--pad:clamp(20px,2.8vw,40px);--ease:cubic-bezier(.2,.7,.2,1)}
body{font-family:var(--text);font-size:18px;line-height:1.5;color:var(--ink);background:var(--night);-webkit-font-smoothing:antialiased;overflow-x:clip}
a{color:inherit;text-decoration:none}img{display:block;max-width:100%%;height:auto}ul,ol{list-style:none;padding:0}
.skip{position:absolute;left:-999px}.skip:focus{left:16px;top:16px;z-index:99;background:var(--paper);color:var(--ink);padding:10px 14px;border-radius:7px}
:focus-visible{outline:2px solid var(--accent);outline-offset:3px}
.lab{font-family:var(--mono);font-size:13px;line-height:1.3;letter-spacing:.02em;text-transform:uppercase;display:inline-flex;align-items:center;gap:10px}
.lab.dot::before{content:"";width:6px;height:6px;border-radius:50%%;background:currentColor}
.btn{display:inline-flex;align-items:center;justify-content:center;min-height:54px;padding:0 22px;border-radius:7px;font-family:var(--mono);font-size:13px;letter-spacing:.06em;text-transform:uppercase;white-space:nowrap;background:var(--accent);color:var(--on-accent);transition:transform .16s var(--ease),filter .2s}
.btn:hover{filter:brightness(1.08)}.btn:active{transform:scale(.97)}.btn.quiet{background:color-mix(in srgb,var(--night) 70%%,#fff 8%%);color:#fff}.btn.pale{background:var(--mist);color:var(--ink)}
em{font-style:normal;color:var(--accent)}
/* bar */
.bar-top{position:fixed;inset:0 0 auto 0;z-index:20;display:flex;align-items:center;justify-content:space-between;gap:16px;padding:14px var(--pad)}
.mark{white-space:nowrap;font-family:var(--display);font-size:clamp(20px,1.9vw,27px);font-weight:400;letter-spacing:-.02em;color:#fff;mix-blend-mode:difference}
.pill{display:flex;align-items:center;gap:8px}.pill nav{display:flex;gap:4px;padding:0 10px;min-height:54px;align-items:center;border-radius:7px;background:color-mix(in srgb,var(--night) 86%%,#fff 6%%);color:#fff}
.pill nav a{font-family:var(--mono);font-size:13px;letter-spacing:.06em;text-transform:uppercase;padding:12px 14px;opacity:.86}.pill nav a:hover{opacity:1}
/* first screen */
.first{position:relative;min-height:100svh;display:grid;align-content:end;color:#fff;padding:120px var(--pad) clamp(36px,6.4vh,72px);isolation:isolate;overflow:hidden}
.bd{position:absolute;inset:0;width:100%%;height:100%%;z-index:-1}.bd-arcs{transform-box:fill-box;transform-origin:60%% 60%%;animation:drift 26s ease-in-out infinite alternate}
@keyframes drift{from{transform:translate(360px,0) rotate(0)}to{transform:translate(330px,-18px) rotate(-2.2deg)}}
.first-in{display:grid;grid-template-columns:minmax(0,1.55fr) minmax(0,1fr);gap:clamp(24px,5vw,96px);align-items:end}
.h1{font-family:var(--display);font-weight:300;font-size:clamp(44px,5.98vw,104px);line-height:1;letter-spacing:-.03em;text-wrap:balance;max-width:13ch}
.first .side{max-width:30ch;padding-bottom:.6em}.first .lede{font-size:clamp(17px,1.25vw,19px);line-height:1.38}.first .acts{display:flex;flex-wrap:wrap;gap:14px;margin-top:28px}
.first .note{margin-top:22px;opacity:.7}
.ln{display:block;overflow:hidden;padding-bottom:.12em;margin-bottom:-.12em}.ln>span{display:block}
/* proof */
.proof{color:#fff;border-top:1px solid color-mix(in srgb,#fff 12%%,transparent);overflow:hidden;padding:26px 0}.proof ul{display:flex;gap:clamp(32px,5vw,88px);width:max-content;animation:slide 46s linear infinite;padding-left:var(--pad)}
.proof li{font-family:var(--mono);font-size:13px;letter-spacing:.06em;text-transform:uppercase;white-space:nowrap;opacity:.82}@keyframes slide{to{transform:translateX(-50%%)}}
/* paper sheet */
.sheet{background:var(--paper);color:var(--ink);border-radius:15px 15px 0 0;padding:clamp(56px,8vw,128px) var(--pad) clamp(56px,7vw,112px)}
.statement{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:clamp(24px,4vw,64px);align-items:start;margin-bottom:clamp(72px,11vw,176px)}
.statement .small{font-size:clamp(18px,1.5vw,22px);line-height:1.3;max-width:20ch;letter-spacing:-.01em}
.statement .big{font-family:var(--display);font-weight:300;font-size:clamp(36px,5vw,76px);line-height:1.05;letter-spacing:-.03em;text-wrap:balance}
/* the held index */
.index{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:clamp(24px,4vw,64px);align-items:start}
.index .held{position:sticky;top:clamp(96px,14vh,150px)}.index .held .lab{margin-bottom:clamp(28px,5vw,64px)}
.index .names li{font-family:var(--display);font-weight:300;font-size:clamp(28px,3.05vw,46px);line-height:1.14;letter-spacing:-.035em;color:color-mix(in srgb,var(--ink) 24%%,var(--paper));transition:color .35s var(--ease)}
.index .names li.on{color:var(--ink)}.index .names a{display:block}
.index .item{padding-bottom:clamp(64px,9vw,144px)}.index .item:last-child{padding-bottom:0}
.index .item .name-m{display:none}
.index .item h3{font-family:var(--display);font-weight:400;font-size:clamp(22px,1.85vw,27px);line-height:1.2;letter-spacing:-.025em;margin-top:clamp(20px,2.4vw,32px)}
.index .item p{font-size:clamp(17px,1.25vw,18px);line-height:1.5;margin-top:14px;max-width:46ch;color:color-mix(in srgb,var(--ink) 86%%,var(--paper))}
.panel{position:relative;background:var(--mist);border-radius:10px;padding:clamp(52px,5vw,72px) clamp(16px,2.4vw,36px);display:grid;gap:14px;min-height:clamp(260px,36vw,560px);align-content:center}
.panel .chip{position:absolute;top:12px;left:12px;font-family:var(--mono);font-size:13px;letter-spacing:.04em;text-transform:uppercase;background:var(--ink);color:var(--paper);padding:8px 10px;border-radius:6px;max-width:calc(100%% - 24px)}
.panel .foot{position:absolute;left:12px;right:12px;bottom:12px;font-family:var(--mono);font-size:13px;letter-spacing:.03em;text-transform:uppercase;background:var(--paper);padding:8px 10px;border-radius:6px;overflow-wrap:anywhere}
.panel .shot{border-radius:10px;overflow:hidden;box-shadow:0 0 0 1px color-mix(in srgb,var(--ink) 10%%,transparent);background:var(--paper)}.panel .shot img{width:100%%}
.bars,.rows{display:grid;gap:10px;background:color-mix(in srgb,var(--paper) 62%%,transparent);border-radius:10px;padding:clamp(16px,2vw,28px)}
.bars li{display:grid;grid-template-columns:minmax(0,9rem) minmax(0,1fr) auto;gap:14px;align-items:center;font-family:var(--mono);font-size:13px;text-transform:uppercase;letter-spacing:.03em}
.bars .bar{height:26px;border-radius:5px;background:color-mix(in srgb,var(--ink) 8%%,transparent);overflow:hidden}.bars .bar i{display:block;height:100%%;width:calc(var(--w) * 100%%);background:linear-gradient(90deg,color-mix(in srgb,var(--accent) 55%%,var(--mist)),var(--accent));border-radius:5px;transform-origin:left;transition:transform .9s var(--ease)}
.bars .v{font-family:var(--display);font-size:clamp(20px,2vw,30px);letter-spacing:-.02em;text-transform:none}
.rows li{display:flex;justify-content:space-between;gap:16px;align-items:baseline;padding:12px 0;border-top:1px solid color-mix(in srgb,var(--ink) 10%%,transparent)}.rows li:first-child{border-top:0}
.rows .k{font-family:var(--mono);font-size:13px;text-transform:uppercase;letter-spacing:.03em}.rows .v{font-family:var(--display);font-size:clamp(20px,2vw,30px);letter-spacing:-.02em;text-align:right}
/* night ground */
.ground{color:#fff;padding:clamp(72px,10vw,160px) var(--pad);display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:clamp(24px,4vw,64px);align-items:start}
.ground h2{font-family:var(--display);font-weight:300;font-size:clamp(34px,3.6vw,56px);line-height:1.08;letter-spacing:-.03em;margin-top:22px;max-width:13ch}.ground .acts{display:flex;flex-wrap:wrap;gap:14px;margin-top:32px}
.ground .points{display:grid;gap:clamp(26px,3vw,44px)}.ground .points h3{font-family:var(--display);font-weight:400;font-size:clamp(20px,1.6vw,24px);letter-spacing:-.02em;display:flex;gap:12px;align-items:baseline}
.ground .points h3::before{content:"";width:9px;height:9px;border-radius:2px;background:var(--accent);flex:none;transform:translateY(-1px)}.ground .points p{margin-top:8px;font-size:16px;line-height:1.5;opacity:.78;max-width:48ch;padding-left:21px}
/* mist sheet: cards and directory */
.mist{background:var(--mist);color:var(--ink);border-radius:15px 15px 0 0;padding:clamp(64px,8vw,128px) var(--pad)}
.mist h2{font-family:var(--display);font-weight:300;font-size:clamp(36px,5vw,76px);line-height:1.05;letter-spacing:-.03em;max-width:16ch;text-wrap:balance}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%%,17rem),1fr));gap:14px;margin-top:clamp(40px,6vw,88px)}
.card{display:grid;align-content:space-between;gap:clamp(48px,7vw,120px);min-height:clamp(220px,24vw,380px);background:var(--paper);border-radius:10px;padding:clamp(18px,1.8vw,26px);transition:transform .25s var(--ease)}.card:hover{transform:translateY(-4px)}
.card b{font-family:var(--display);font-weight:400;font-size:clamp(20px,1.7vw,25px);line-height:1.2;letter-spacing:-.02em;display:block}.card .go{margin-top:14px;opacity:.6}
.dir{margin-top:clamp(64px,9vw,144px);display:grid;grid-template-columns:minmax(0,1fr) minmax(0,2fr);gap:clamp(24px,4vw,64px);align-items:start}
.dir ul{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%%,16rem),1fr));column-gap:clamp(24px,3vw,48px)}
.dir li a{display:flex;justify-content:space-between;gap:16px;align-items:center;min-height:56px;border-bottom:1px solid var(--line);font-size:clamp(17px,1.35vw,20px);letter-spacing:-.01em;transition:padding .25s var(--ease)}.dir li a::after{content:"→";font-family:var(--mono);opacity:.5}.dir li a:hover{padding-left:8px}
/* closing and footer */
.end{color:#fff;padding:clamp(64px,8vw,128px) var(--pad) 28px}
.end .cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%%,11rem),1fr));gap:clamp(24px,4vw,64px);padding-bottom:clamp(72px,11vw,176px)}.end .cols h2{font-size:15px;font-weight:400;opacity:.6;margin-bottom:12px}.end .cols a{display:block;font-size:15px;padding:5px 0;opacity:.9}.end .cols a:hover{opacity:1;text-decoration:underline;text-underline-offset:.25em}
.closing{display:grid;justify-items:end;text-align:right;gap:22px}.closing p.line{font-family:var(--display);font-weight:300;font-size:clamp(28px,2.6vw,40px);line-height:1.15;letter-spacing:-.03em;max-width:24ch;text-wrap:balance}.closing .acts{display:flex;flex-wrap:wrap;gap:14px;justify-content:flex-end}
.legal{margin-top:clamp(48px,6vw,88px);display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;font-family:var(--mono);font-size:13px;text-transform:uppercase;letter-spacing:.04em;opacity:.7}
/* motion: nothing is hidden unless the script says it can animate */
.js .ln>span{transform:translateY(105%%);transition:transform .275s var(--ease)}.js .in .ln>span{transform:none}.js .ln:nth-child(2)>span{transition-delay:34ms}
.js [data-rise]{opacity:0;transform:translateY(12px);transition:opacity .3s ease,transform .3s var(--ease);transition-delay:calc(var(--i,0) * 70ms)}.js [data-rise].in{opacity:1;transform:none}
.js .bars .bar i{transform:scaleX(0)}.js .in .bars .bar i,.js .bars.in .bar i{transform:none}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}.js .ln>span,.js [data-rise],.js .bars .bar i{opacity:1!important;transform:none!important}}
@media (max-width:900px){
.pill nav{display:none}.first-in,.statement,.index,.ground,.dir{grid-template-columns:minmax(0,1fr)}.first .side{max-width:36ch;padding-bottom:0}
.index .held{position:static}.index .names{display:none}.index .held .lab{margin-bottom:24px}.index .item .name-m{display:block;font-family:var(--display);font-weight:300;font-size:clamp(30px,8vw,44px);line-height:1.1;letter-spacing:-.035em;margin-bottom:18px}
.closing{justify-items:start;text-align:left}.closing .acts{justify-content:flex-start}.bars li{grid-template-columns:minmax(0,6.5rem) minmax(0,1fr) auto}
}
@media (max-width:480px){.btn{padding:0 16px}.bar-top .btn.pale{display:none}.bar-top .btn{min-height:44px;font-size:12px;letter-spacing:.04em;max-width:56vw;overflow:hidden;text-overflow:ellipsis;display:inline-block;line-height:44px}}
"""

JS = """
document.documentElement.classList.add('js');
const seen=new IntersectionObserver(es=>es.forEach(x=>{if(x.isIntersecting){x.target.classList.add('in');seen.unobserve(x.target)}}),{rootMargin:'0px 0px -8% 0px',threshold:.12});
document.querySelectorAll('[data-rise],.h1,.bars,.panel').forEach(el=>seen.observe(el));
requestAnimationFrame(()=>document.querySelectorAll('.first .h1,.first [data-rise]').forEach(el=>el.classList.add('in')));
const names=[...document.querySelectorAll('.index .names li')],items=[...document.querySelectorAll('.index .item')];
if(names.length){const pick=new IntersectionObserver(es=>es.forEach(x=>{if(x.isIntersecting){const i=items.indexOf(x.target);names.forEach((n,k)=>n.classList.toggle('on',k===i))}}),{rootMargin:'-42% 0px -42% 0px'});items.forEach(i=>pick.observe(i));names[0].classList.add('on')}
"""


def _css(tokens):
    css = CSS
    for k, v in tokens.items(): css = css.replace('%(' + k + ')s', v)
    return css.replace('%%', '%')


def _contrast_ink(hexcode):
    r, g, b = (v / 255 for v in _rgb(hexcode)); lin = lambda v: v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4
    return '#0b0d12' if .2126 * lin(r) + .7152 * lin(g) + .0722 * lin(b) > .32 else '#ffffff'


def render(content, images=None):
    """The page. `images`: {id: {'data', 'w', 'h'}}. A slot that is empty leaves its part out; nothing is invented to fill it."""
    images = images or {}; c = content; b = c.get('brand') or {}
    accent = b.get('accent') or '#ff488b'; night = b.get('night') or '#101421'
    nr, ng, nb = _rgb(night); mix = lambda t: '#%02x%02x%02x' % tuple(int(255 - (255 - v) * t) for v in (nr, ng, nb))
    tokens = {'night': night, 'accent': accent, 'on_accent': _contrast_ink(accent), 'mist': mix(.075), 'ink': '#%02x%02x%02x' % tuple(min(255, int(v * 1.0 + 6)) for v in (nr, ng, nb)), 'mute': mix(.45), 'line': mix(.16)}
    act = c.get('action') or {}; act2 = c.get('action2') or {}
    btn = lambda a, cls='': f'<a class="btn {cls}" href="{e(a.get("url"))}">{e(a.get("label"))}</a>' if a.get('label') and a.get('url') else ''
    nav = ''.join(f'<a href="{e(n["url"])}">{e(n["label"])}</a>' for n in (c.get('nav') or [])[:5] if n.get('label') and n.get('url'))
    hero = c.get('hero') or {}
    out = [f'<a class="skip" href="#main">Skip to content</a><header class="bar-top"><a class="mark" href="#top">{e(b.get("name"))}</a><div class="pill">' + (f'<nav aria-label="Primary">{nav}</nav>' if nav else '') + f'{btn(act2, "pale")}{btn(act)}</div></header><main id="main">']
    out.append(f'<section class="first" id="top">{_backdrop(accent)}<div class="first-in"><h1 class="h1">{_lines(hero.get("h1"))}</h1><div class="side"><p class="lede" data-rise style="--i:2">{e(hero.get("lede"))}</p>'
               f'<div class="acts" data-rise style="--i:3">{btn(act)}{btn(act2, "quiet")}</div>' + (f'<p class="lab note" data-rise style="--i:4">{e(hero["note"])}</p>' if hero.get('note') else '') + '</div></div></section>')
    proof = [p for p in c.get('proof') or [] if str(p).strip()][:8]
    if len(proof) >= 3:
        row = ''.join(f'<li>{e(p)}</li>' for p in proof)
        out.append(f'<section class="proof" aria-label="In short"><ul>{row}<span aria-hidden="true" style="display:contents">{row}</span></ul></section>')
    st = c.get('statement') or {}; ix = c.get('index') or {}; items = [i for i in ix.get('items') or [] if i.get('title')][:5]
    sheet = []
    if st.get('big'): sheet.append(f'<div class="statement"><p class="small" data-rise>{e(st.get("small"))}</p><h2 class="big" data-rise style="--i:1">{_mark(st["big"])}</h2></div>')
    if len(items) >= 2:
        names = ''.join(f'<li><a href="#claim-{k + 1}">{e(i["title"])}</a></li>' for k, i in enumerate(items))
        body = ''.join(f'<article class="item" id="claim-{k + 1}"><p class="name-m">{e(i["title"])}</p><div data-rise>{_panel(i.get("panel") or {}, images)}</div>' + (f'<h3 data-rise style="--i:1">{e(i["h3"])}</h3>' if i.get('h3') else '') + (f'<p data-rise style="--i:2">{e(i["body"])}</p>' if i.get('body') else '') + '</article>' for k, i in enumerate(items))
        sheet.append(f'<div class="index"><div class="held"><p class="lab dot">{e(ix.get("label"))}</p><ol class="names">{names}</ol></div><div class="items">{body}</div></div>')
    if sheet: out.append(f'<section class="sheet" id="product">{"".join(sheet)}</section>')
    gr = c.get('ground') or {}
    if gr.get('h2'):
        pts = ''.join(f'<li data-rise style="--i:{k}"><h3>{e(p.get("title"))}</h3><p>{e(p.get("body"))}</p></li>' for k, p in enumerate((gr.get('points') or [])[:5]) if p.get('title'))
        out.append(f'<section class="ground" id="ground"><div><p class="lab dot">{e(gr.get("label"))}</p><h2>{_mark(gr["h2"])}</h2><div class="acts">{btn(act)}{btn(act2, "quiet")}</div></div><ul class="points">{pts}</ul></section>')
    cards = c.get('cards') or {}; d = c.get('directory') or {}; mist = []
    if cards.get('h2'):
        tiles = ''.join(f'<a class="card" href="{e(t.get("url"))}" data-rise style="--i:{k % 4}"><span class="lab">{e(t.get("kicker"))}</span><span><b>{e(t.get("title"))}</b><span class="lab go">→</span></span></a>' for k, t in enumerate((cards.get('items') or [])[:6]) if t.get('title') and t.get('url'))
        mist.append(f'<h2 data-rise>{_mark(cards["h2"])}</h2>' + (f'<div class="cards">{tiles}</div>' if tiles else ''))
    links = [l for l in d.get('links') or [] if l.get('label') and l.get('url')][:14]
    if links: mist.append(f'<div class="dir"><p class="lab dot">{e(d.get("label"))}</p><ul>' + ''.join(f'<li><a href="{e(l["url"])}">{e(l["label"])}</a></li>' for l in links) + '</ul></div>')
    if mist: out.append(f'<section class="mist" id="more">{"".join(mist)}</section>')
    out.append('</main>')
    ft = c.get('footer') or {}; cl = c.get('closing') or {}
    cols = ''.join(f'<div><h2>{e(col.get("title"))}</h2>' + ''.join(f'<a href="{e(l["url"])}">{e(l["label"])}</a>' for l in (col.get('links') or [])[:8] if l.get('label') and l.get('url')) + '</div>' for col in (ft.get('columns') or [])[:4])
    out.append(f'<footer class="end" id="end">' + (f'<div class="cols">{cols}</div>' if cols else '') + (f'<div class="closing"><p class="line" data-rise>{e(cl["line"])}</p><div class="acts" data-rise style="--i:1">{btn(act)}{btn(act2, "quiet")}</div></div>' if cl.get('line') else '')
               + f'<div class="legal"><span>{e(ft.get("legal"))}</span><span>{e(cl.get("note"))}</span></div></footer>')
    head = (f'<!doctype html><html lang="{e(b.get("lang") or "en")}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(c.get("title") or b.get("name"))}</title>'
            f'<meta name="description" content="{e(c.get("description") or hero.get("lede"))}"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link href="https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500&family=Geist+Mono:wght@400;500&display=swap" rel="stylesheet">'
            f'<style>{_css(tokens)}</style></head><body>')
    return head + ''.join(out) + f'<script>{JS}</script></body></html>'
