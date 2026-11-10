"""render_ir.py — draw a validated hero composition and put it in place of the page's hero.

The same composition and the same page always give the same bytes. The composed hero reuses the page's own tokens and
classes (`--paper`, `--display`, `.h1`, `.lab`, `.lede`, `.btn`), so it belongs to the page it sits in; it adds the
grid that places the pieces and the treatments a composition may ask for. Every word and link comes from the
production hero through lib/compose/content.py and is escaped here. A composition that does not validate is never
drawn: `transplant` returns the page untouched and says why.

A typeface chosen by the composition is a decision for the whole page: `transplant` sets the page's display face
(every heading follows it) and loads it from the registry's stylesheet. Treatments are drawn with properties the page's
own measuring tools leave alone — `rotate`, blend modes, radii — never `transform`, `filter`, `clip-path` or `opacity`,
which the contract and the screenshots switch off: what is measured is what a visitor sees. Motion is the page's own
library (lib/motion/moves.js) asked for by name; with motion off the composition is simply at rest.

  render_hero(ir, content)        → the <section> for a composition that validate() accepts
  transplant(page_html, ir, images) → (page_html, report)     report = {'drawn': bool, 'errors': [...]}
  python3 lib/compose/render_ir.py <composition.json> <page.html> <images.json> <out.html>
Deterministic, no network, no model."""
import html as H, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import content as CONTENT
import validate as V
FACES = V.FACES

e = lambda s: H.escape(str(s if s is not None else ''), quote=True)

ROWS = {'auto': 'auto', '1fr': '1fr', '2fr': '2fr', 'min': 'min-content'}  # fr rows grow with their content: a hero has a minimum height, never a fixed one
GAP = {'sm': '16px', 'md': '24px', 'lg': '40px'}
HEIGHT = {'auto': 'auto', 'screen': '100svh', 'tall': '120svh'}
SIZE = {'xl': 'clamp(36px,4.6vw,68px)', 'xxl': 'clamp(46px,7.4vw,112px)', 'mega': 'clamp(54px,12.2vw,200px)'}
BAND = {'paper': '', 'dark': ' band-dark', 'alt': ' band-alt', 'accent': ' band-accent'}
SURFACE = {'paper': ('var(--paper)', 'var(--ink)'), 'dark': ('var(--band-paper)', 'var(--band-ink)'), 'alt': ('var(--alt,var(--paper))', 'var(--alt-ink,var(--ink))'), 'accent': ('var(--accent)', 'var(--on-accent,var(--paper))')}

# The grid and nothing else: type, colour and buttons are the page's own. The first lines are the manners of set type, for
# the whole page: headings balanced, paragraphs without orphans, figures that line up, the optical size following the size.
CSS = """
h1,h2,h3{text-wrap:balance}p,li{text-wrap:pretty}body{font-optical-sizing:auto;font-kerning:normal}
.rows b,.num,.lc-tag,.idx,.ladder-n,time{font-variant-numeric:tabular-nums}
.hero.ir{display:flex;min-height:var(--ir-minh,auto);padding-top:calc(var(--nav-h,64px) + clamp(20px,3vw,44px));padding-bottom:clamp(28px,5vw,80px)}
.hero.ir .ir-grid{flex:1;display:grid;grid-template-columns:repeat(12,minmax(0,1fr));grid-template-rows:var(--ir-rows);column-gap:var(--ir-gap);row-gap:var(--ir-gap)}
.hero.ir .ir-n{grid-column:var(--c0)/var(--c1);grid-row:var(--r0)/var(--r1);z-index:var(--z,1);align-self:var(--self,start);min-width:0;container-type:inline-size;margin:0}
.hero.ir .ir-h{font-size:min(var(--ir-size),calc(100cqw / var(--fit,5)));line-height:var(--h1-lh,1);margin:0;text-wrap:balance;overflow-wrap:normal}
.hero.ir .ir-h .ir-l{display:block;font-size:calc(var(--ls,1) * 1em);padding-left:var(--ind,0)}
.hero.ir .ir-h em.ir-mk{font-style:normal;color:inherit}
.hero.ir .ir-h em.ir-mk-accent{color:var(--accent-word,var(--accent))}
.hero.ir .ir-h em.ir-mk-italic{font-style:italic}
.hero.ir .ir-h em.ir-mk-outline{color:var(--ir-bg);-webkit-text-stroke:max(1.5px,.018em) var(--ir-fg);paint-order:stroke fill}
.hero.ir .ir-h em.ir-mk-underline{text-decoration:underline;text-decoration-color:var(--accent);text-decoration-thickness:.07em;text-underline-offset:.12em;text-decoration-skip-ink:none}
.hero.ir .ir-h em.ir-mk-box{background:var(--accent);color:var(--on-accent,var(--paper));padding:0 .14em;margin:0 -.04em;box-decoration-break:clone;-webkit-box-decoration-break:clone}
.hero.ir .ir-n .lede{margin-top:0}.hero.ir .ir-n .lede.ir-lg{font-size:clamp(20px,1.9vw,28px);line-height:1.3}
.hero.ir .ir-n .ctas{margin-top:0}.hero.ir .ir-n .cat{margin-bottom:0}
.hero.ir .ir-al-center{text-align:center}.hero.ir .ir-al-center>*{margin-left:auto;margin-right:auto}.hero.ir .ir-al-center .ctas{justify-content:center}
.hero.ir .ir-al-end{text-align:right}.hero.ir .ir-al-end>*{margin-left:auto}.hero.ir .ir-al-end .ctas,.hero.ir .ir-al-end .cat{justify-content:flex-end}
.hero.ir .ir-al-center .cat{justify-content:center}
.hero.ir .ir-plate>*{width:fit-content;padding:.1em .3em .16em 0}
.hero.ir .ir-plate-paper>*{background:var(--ir-bg);color:var(--ir-fg)}.hero.ir .ir-plate-ink>*{background:var(--ir-fg);color:var(--ir-bg);padding-left:.3em}
.hero.ir .ir-media{position:relative;overflow:hidden;border-radius:var(--radius,0);aspect-ratio:var(--ratio);align-self:var(--self,start)}
.hero.ir .ir-media img{display:block;width:100%;height:100%;object-fit:cover;object-position:var(--focal,50% 50%)}
.hero.ir .ir-media.ir-contain{overflow:visible;aspect-ratio:auto}.hero.ir .ir-media.ir-contain img{height:auto;object-fit:contain}
.hero.ir .ir-frame-browser{border-radius:8px;box-shadow:0 0 0 1px color-mix(in srgb,currentColor 14%,transparent),0 24px 60px -24px rgba(0,0,0,.22);overflow:hidden}
.hero.ir .ir-frame-paper{background:#fff;padding:clamp(10px,1.4vw,22px);box-shadow:0 0 0 1px color-mix(in srgb,currentColor 14%,transparent),0 24px 60px -24px rgba(0,0,0,.22)}
.hero.ir .ir-scrim::after{content:"";position:absolute;inset:0;z-index:3;background:linear-gradient(180deg,rgba(0,0,0,.34),rgba(0,0,0,.16) 45%,rgba(0,0,0,.52))}
.hero.ir .ir-tone{isolation:isolate;background:#808080}.hero.ir .ir-tone img{mix-blend-mode:luminosity}.hero.ir .ir-tone-tint{background:var(--accent)}
.hero.ir .ir-media>i,.hero.ir .ir-layer>i{position:absolute;inset:0;pointer-events:none}
.hero.ir .ir-t-light{z-index:1;background:var(--ir-light);mix-blend-mode:multiply}.hero.ir .ir-t-dark{z-index:2;background:var(--ir-dark);mix-blend-mode:lighten}
.hero.ir .ir-grain{z-index:2;mix-blend-mode:overlay;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='240' height='240'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.8' numOctaves='2' seed='7' stitchTiles='stitch'/%3E%3CfeColorMatrix values='0 0 0 0 .5 0 0 0 0 .5 0 0 0 0 .5 0 0 0 .6 0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")}
.hero.ir .ir-shape-soft{border-radius:clamp(18px,2.4vw,36px)}.hero.ir .ir-shape-arch{border-radius:999px 999px 0 0}.hero.ir .ir-shape-circle{border-radius:50%}.hero.ir .ir-shape-pill{border-radius:999px}
.hero.ir .ir-shadow-soft{box-shadow:0 24px 60px -24px rgba(0,0,0,.22)}.hero.ir .ir-shadow-hard{box-shadow:clamp(8px,1vw,16px) clamp(8px,1vw,16px) 0 var(--accent)}
.hero.ir .ir-stack{position:relative;overflow:visible;aspect-ratio:var(--box);align-self:var(--self,start)}
.hero.ir .ir-layer{position:absolute;display:block;overflow:hidden;border-radius:var(--radius,0);background:var(--ir-bg);box-shadow:0 0 0 1px color-mix(in srgb,currentColor 12%,transparent),0 20px 50px -24px rgba(0,0,0,.24)}
.hero.ir .ir-layer img{display:block;width:100%;height:100%;object-fit:cover;object-position:var(--focal,50% 50%)}
.hero.ir .ir-stack.ir-contain .ir-layer{background:#fff}.hero.ir .ir-stack.ir-contain .ir-layer img{object-fit:contain}
.hero.ir .ir-stack.ir-frame-browser,.hero.ir .ir-stack.ir-frame-paper{border:0;box-shadow:none;background:none;padding:0;overflow:visible}
.hero.ir .ir-stack.ir-frame-browser .ir-layer{border-radius:8px}.hero.ir .ir-stack.ir-frame-paper .ir-layer{border:clamp(6px,.8vw,12px) solid #fff}
.hero.ir .ir-stack.ir-shape-soft{border-radius:0}.hero.ir .ir-stack.ir-shape-soft .ir-layer{border-radius:clamp(14px,1.8vw,28px)}
.hero.ir .ir-on-scrim,.hero.ir .ir-on-scrim .lab,.hero.ir .ir-on-scrim .lede{color:var(--on-photo,#F4EFE3)}.hero.ir .ir-on-scrim .btn.ghost{color:var(--on-photo,#F4EFE3);border-color:var(--on-photo,#F4EFE3)}
.hero.ir .ir-bleed-right{margin-right:calc(-1 * (var(--frame,24px) + max(0px,(100vw - var(--container,1300px)) / 2)))}
.hero.ir .ir-bleed-left{margin-left:calc(-1 * (var(--frame,24px) + max(0px,(100vw - var(--container,1300px)) / 2)))}
.hero.ir .ir-rule{height:1px;background:var(--line);align-self:var(--self,start)}
.hero.ir.ir-has-backdrop{position:relative;isolation:isolate;overflow:hidden;background:#15130f}
.hero.ir .ir-backdrop{position:absolute;inset:0;width:100%;height:100%;align-self:stretch;z-index:0;margin:0;aspect-ratio:auto;border-radius:0}
.hero.ir .ir-backdrop.ir-scrim::after{background:linear-gradient(180deg,rgba(12,10,8,.52),rgba(12,10,8,.3) 42%,rgba(12,10,8,.68))}
.hero.ir .ir-backdrop.ir-scrim-deep::after{background:linear-gradient(180deg,rgba(12,10,8,.76),rgba(12,10,8,.62) 42%,rgba(12,10,8,.86))}
.hero.ir.ir-has-backdrop .ir-grid{position:relative;z-index:1}
@media(max-width:900px){
.hero.ir{min-height:auto}
.hero.ir .ir-grid{display:flex;flex-direction:column;gap:22px}
.hero.ir .ir-n{order:var(--sm,0);align-self:stretch}
.hero.ir .ir-media{margin-left:0;margin-right:0;aspect-ratio:var(--sm-ratio,var(--ratio))}
.hero.ir .ir-al-end{text-align:left}.hero.ir .ir-al-end>*{margin-left:0}.hero.ir .ir-al-end .ctas,.hero.ir .ir-al-end .cat{justify-content:flex-start}
.hero.ir .ir-plate>*{background:none;color:inherit;padding:0;width:auto}
.hero.ir .ir-h:not(.ir-keep-sm){font-size:min(var(--ir-size),calc(100cqw / var(--fit-sm,5)))}
.hero.ir .ir-h:not(.ir-keep-sm) .ir-l{display:inline;font-size:inherit;padding-left:0}.hero.ir .ir-h:not(.ir-keep-sm) .mv-line-in{display:inline}
.hero.ir .ir-media{rotate:none!important}
.hero.ir .ir-on-scrim,.hero.ir .ir-on-scrim .lab,.hero.ir .ir-on-scrim .lede{color:inherit}.hero.ir .ir-on-scrim .btn.ghost{color:inherit;border-color:currentColor}
.hero.ir.ir-has-backdrop{min-height:min(100svh,720px)}.hero.ir .ir-backdrop{aspect-ratio:auto}
.hero.ir.ir-has-backdrop .ir-on-scrim,.hero.ir.ir-has-backdrop .ir-on-scrim .lab,.hero.ir.ir-has-backdrop .ir-on-scrim .lede{color:var(--on-photo,#F4EFE3)}.hero.ir.ir-has-backdrop .ir-on-scrim .btn.ghost{color:var(--on-photo,#F4EFE3);border-color:var(--on-photo,#F4EFE3)}
}
"""


def _place(node, rows, phone_index):
    c0, c1, r0, r1 = V.area(node, rows)
    at = node['at']
    return f'--c0:{c0};--c1:{c1};--r0:{r0};--r1:{r1};--z:{at.get("z", 1)};--self:{at.get("self", "start")};--sm:{phone_index}'


def _run(text, em, mark):
    """One run of a word: emphasised runs are an <em>, drawn the way the composition marks them (the page's own way when it says nothing)."""
    if not em: return e(text)
    return f'<em class="ir-mk ir-mk-{mark}">{e(text)}</em>' if mark else f'<em>{e(text)}</em>'


def _headline(node, segments):
    """(inner HTML, lines as text) of the headline. Words marked by position replace the headline's own emphasis; a
    headline broken by hand is made of line spans the page's motion library already understands (.mv-line / .mv-line-in)."""
    words = CONTENT.words(segments); mark = node.get('mark'); marked = node.get('mark_words')
    if marked is not None: words = [[(''.join(t for t, _ in w), i in marked)] for i, w in enumerate(words)]
    drawn = [''.join(_run(text, em, mark) for text, em in w) for w in words]
    plain = [''.join(t for t, _ in w) for w in words]
    lines = node.get('lines')
    if not lines: return ' '.join(drawn), None
    out, texts, at = [], [], 0
    for i, count in enumerate(lines):
        scale = (node.get('scale') or [1] * len(lines))[i]; indent = (node.get('indent') or [0] * len(lines))[i]
        style = ';'.join(([f'--ls:{scale:g}'] if scale != 1 else []) + ([f'--ind:{indent * 0.5 / scale:.3g}em'] if indent else []))
        out.append(f'<span class="ir-l mv-line"' + (f' style="{style}"' if style else '') + f'><span class="mv-line-in">{" ".join(drawn[at:at + count])}</span></span>')
        texts.append(' '.join(plain[at:at + count])); at += count
    return ' '.join(out), texts


def _picture(m):
    return f'<img src="{e(m["src"])}" alt="{e(m.get("alt", ""))}">'


def _toning(node):
    """The layers that tone a photograph, drawn over it: its light mapped to the lighter of the page's two colours, its dark to the darker."""
    return ('<i class="ir-t-light"></i><i class="ir-t-dark"></i>' if node.get('tone') == 'duotone' else '') + ('<i class="ir-grain"></i>' if node.get('grain') else '')


MOVES = {'rise': 'fade-rise', 'clip': 'clip-reveal', 'settle': 'scale-settle'}   # names in lib/motion/moves.js
MEASURED_SLACK = 1.015   # a measured line gets a hair of room: sub-pixel rounding must never wrap it
ESTIMATE_SLACK = 1.12    # an estimated one gets the tenth an average can be off by


def render_hero(ir, content):
    """The hero <section> for a composition that validate() accepts. Call validate() first; this function assumes it passed."""
    hero = ir['hero']; rows = hero['rows']; nodes = hero['nodes']
    phone = (hero.get('sm') or {}).get('order') or [n['id'] for n in nodes]
    areas = {n['id']: V.area(n, len(rows)) for n in nodes}
    face, upper = V.face_of(hero, content); advance = FACES.advance(face, upper)
    # text that sits on a scrimmed picture reads in the on-photo colour
    def on_scrim(node):
        return not node.get('plate') and any(m.get('t') == 'media' and m.get('scrim') and V.overlap(areas[node['id']], areas[m['id']]) for m in nodes)
    out, under = [], []
    for node in nodes:
        style = _place(node, len(rows), phone.index(node['id'])); kind = node['t']; nid = e(node['id'])
        if kind == 'text':
            role = node['as']; align = node.get('align', 'start'); value = content['text'][node['src']]
            classes = ['ir-n', 'ir-text', f'ir-al-{align}'] + ([f'ir-plate ir-plate-{node["plate"]}'] if node.get('plate') else []) + (['ir-on-scrim'] if on_scrim(node) else [])
            if role == 'h1':
                inner_html, lines = _headline(node, value)
                # the widest line and the widest word, in em: measured in a browser when the composition carries `fit`, else
                # estimated from the face's average advance and given room for the estimate being an average
                measured = node.get('fit'); slack = MEASURED_SLACK if measured else ESTIMATE_SLACK
                longest_word = (measured['word'] if measured else max((len(''.join(t for t, _ in w)) for w in CONTENT.words(value)), default=6) * advance) * slack
                fit = V.headline_em(node, content, face, upper) * slack; classes_h, attrs = 'h1 ir-h', ''
                if lines:   # the lines are kept on a phone only when they are short enough to stay readable there
                    keep = max(len(t) for t in lines) <= 12 and not node.get('indent') and not node.get('scale')
                    classes_h += ' ir-lined' + (' ir-keep-sm' if keep else ''); attrs = ' data-split="l"'
                measure = f';max-width:{node["measure"]}ch' if node.get('measure') and not lines else ''
                inner = f'<h1 class="{classes_h}"{attrs} style="--ir-size:{SIZE[node.get("size", "xxl")]};--fit:{fit:.3f};--fit-sm:{longest_word:.3f}{measure}">{inner_html}</h1>'
            elif role == 'lede':
                measure = f' style="max-width:{node["measure"]}ch"' if node.get('measure') else ''
                inner = f'<p class="lede{" ir-lg" if node.get("size") == "lg" else ""}"{measure}>{e(value)}</p>'
            else:
                inner = f'<div class="cat"><span class="lab">{e(value)}</span></div>'
            out.append(f'<div class="{" ".join(classes)}" data-node="{nid}" style="{style}">{inner}</div>')
        elif kind == 'actions':
            buttons = ''
            for address in node['src']:
                a = content['actions'][address]
                buttons += f'<a class="btn{" ghost" if a.get("ghost") else ""}" href="{e(a["href"])}">{e(a["label"])}' + ('' if a.get('ghost') else ' <span class="ar">→</span>') + '</a>'
            classes = ['ir-n', 'ir-actions', f'ir-al-{node.get("align", "start")}'] + (['ir-on-scrim'] if on_scrim(node) else [])
            out.append(f'<div class="{" ".join(classes)}" data-node="{nid}" style="{style}"><div class="ctas">{buttons}</div></div>')
        elif kind == 'media':
            fit = V.fit_of(node, content); focal = node.get('focal', [0.5, 0.5]); tone = node.get('tone', 'none'); shape = node.get('shape', 'rect')
            look = (['ir-contain'] if fit == 'contain' else []) + ([f'ir-frame-{node["frame"]}'] if node.get('frame', 'none') != 'none' else []) + ([f'ir-shape-{shape}'] if shape != 'rect' else [])
            toned = (['ir-tone'] + (['ir-tone-tint'] if tone == 'tint' else [])) if tone != 'none' else []
            if node.get('bleed') == 'full':   # the ground of the whole first screen: under the grid, edge to edge, the navigation on it
                named = ([MOVES[node['enter']]] if node.get('enter', 'none') != 'none' else []) + (['parallax'] if node.get('scroll') == 'parallax' else [])
                move = (f' data-move="{" ".join(named)}"' + (' data-parallax="6"' if 'parallax' in named else '')) if named else ''
                under.append(f'<figure class="{" ".join(["ir-media", "ir-backdrop", "ir-scrim"] + (["ir-scrim-deep"] if node.get("scrim") == "deep" else []) + toned)}" data-node="{nid}"{move} style="--focal:{round(focal[0] * 100)}% {round(focal[1] * 100)}%">{_picture(content["media"][node["src"]])}{_toning(node)}</figure>')
                continue
            style += f';--ratio:{node["ratio"]};--focal:{round(focal[0] * 100)}% {round(focal[1] * 100)}%'
            if isinstance(node['src'], list):   # a stack: every layer inside the node's own box, the first picture named in front
                box, layers, _ = V.stack_layout(node['stack'], len(node['src']), node['ratio']); inner = ''
                for address, layer in zip(node['src'], layers):
                    place = f'left:{layer["left"] * 100:.2f}%;top:{layer["top"] * 100:.2f}%;width:{layer["width"] * 100:.2f}%;height:{layer["height"] * 100:.2f}%;z-index:{layer["z"]}' + (f';rotate:{layer["rotate"]}deg' if layer['rotate'] else '')
                    inner += f'<span class="{" ".join(["ir-layer"] + toned)}" style="{place}">{_picture(content["media"][address])}{_toning(node)}</span>'
                move = ' data-move="stagger-in" data-stagger=".12"' if node.get('enter', 'none') != 'none' else ''
                out.append(f'<figure class="{" ".join(["ir-n", "ir-stack", "ir-stack-" + node["stack"]] + look)}" data-node="{nid}"{move} style="{style};--box:{box:.4f}">{inner}</figure>')
                continue
            classes = ['ir-n', 'ir-media'] + look + toned + (['ir-scrim'] if node.get('scrim') else []) + ([f'ir-bleed-{node["bleed"]}'] if node.get('bleed', 'none') != 'none' else []) \
                + ([f'ir-shadow-{node["shadow"]}'] if node.get('shadow', 'none') != 'none' else [])
            if node.get('tilt'): style += f';rotate:{node["tilt"]}deg'
            named = ([MOVES[node['enter']]] if node.get('enter', 'none') != 'none' else []) + (['parallax'] if node.get('scroll') == 'parallax' else [])
            move = (f' data-move="{" ".join(named)}"' + (' data-parallax="7"' if 'parallax' in named else '')) if named else ''
            out.append(f'<figure class="{" ".join(classes)}" data-node="{nid}"{move} style="{style}">{_picture(content["media"][node["src"]])}{_toning(node)}</figure>')
        elif kind == 'shape':
            out.append(f'<div class="ir-n ir-rule" data-node="{nid}" style="{style}" aria-hidden="true"></div>')
    bg, fg = SURFACE[hero.get('surface', 'paper')]
    dark, light = ('var(--paper)', 'var(--ink)') if content.get('page', {}).get('dark') else ('var(--ink)', 'var(--paper)')
    grid_style = f'--ir-rows:{" ".join(ROWS[r] for r in rows)};--ir-gap:{GAP[hero.get("gap", "md")]};--ir-minh:{HEIGHT[hero.get("height", "auto")]};--ir-bg:{bg};--ir-fg:{fg};--ir-dark:{dark};--ir-light:{light}'
    ground = ' has-media ir-has-backdrop' if under else ''   # has-media: the page's own script then sets the navigation in the on-photo colour over it
    return (f'<section class="sec hero ir{BAND[hero.get("surface", "paper")]}{ground}" id="top" data-ir="{V.VERSION}" data-enter="{e(hero.get("enter", "none"))}" style="{grid_style}">'
            f'{"".join(under)}<div class="wrap ir-grid">{"".join(out)}</div></section>')


def face_head(hero, content):
    """What the page's <head> gains when the composition sets the page in a registry face: its stylesheet and the page's
    display tokens — family, weights, tracking, leading, case. Every heading of the page follows; nothing else changes."""
    chosen = hero.get('face'); system = hero.get('type') or {}
    if not chosen and not system: return ''
    loaded, tokens, extra = [], [], ''
    if chosen:
        face = FACES.get(chosen['id']); weight = chosen.get('weight', face['display']); lo, hi = face['weights']; loaded.append(face)
        h3 = min(hi, max(lo, content.get('page', {}).get('h3_weight') or weight))
        case = chosen.get('case') or ('upper' if face.get('upper') else 'none')
        tokens.append(f"--display:{FACES.stack(face)};--h1-w:{weight};--h2-w:{weight};--h3-w:{h3};--h1-ls:{face['ls']};--h2-ls:{face['ls']};"
                      f"--h1-lh:{face['lh']};--h2-lh:{max(face['lh'], 1.0)};--h1-tt:{'uppercase' if case == 'upper' else 'none'}")
        width = face.get('avg_upper' if case == 'upper' else 'avg') or 0.46; grow = min(1.3, 0.46 / width)
        if width <= 0.37: extra = f'.h3{{font-size:calc(var(--h3) * {grow:.2f})}}.qa summary{{font-size:min(calc(var(--h3) * {grow:.2f}),{round(24 * grow)}px)}}'   # a narrow face sets small at a size meant for a wide one: the small headings grow with it
    for role in ('body', 'label'):   # the page's running text and its small print follow the system the composition chose
        if system.get(role): face = FACES.get(system[role]); loaded.append(face); tokens.append(f'--{role}:{FACES.stack(face)}')
    sheets = ''.join(f'<link id="ir-face{n or ""}" href="{e(url)}" rel="stylesheet">' for n, url in enumerate(FACES.links(loaded)))
    return f'<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>{sheets}<style id="ir-face-css">:root{{{";".join(tokens)}}}{extra}</style>'


def transplant(page_html, ir, images=None):
    """Put a composed hero in place of the page's hero. The composition is validated against the page's own hero first;
    if it fails, the page comes back untouched with the reasons — never a half-applied or silently altered composition."""
    try: content = CONTENT.from_page(page_html, images or [])
    except ValueError as err: return page_html, {'drawn': False, 'errors': [{'code': 'IR000', 'at': 'page', 'message': str(err)}]}
    errors = V.validate(ir, content)
    if errors: return page_html, {'drawn': False, 'errors': errors}
    start, end = content['span']; section = render_hero(ir, content)
    page = page_html[:start] + section + page_html[end:]
    if 'id="ir-css"' not in page:
        head = page.find('</head>')
        if head < 0: return page_html, {'drawn': False, 'errors': [{'code': 'IR000', 'at': 'page', 'message': 'the page has no </head> to carry the composition stylesheet'}]}
        page = page[:head] + f'<style id="ir-css">{CSS}</style>' + face_head(ir['hero'], content) + page[head:]
    return page, {'drawn': True, 'errors': [], 'placed': {'text': sorted(content['text']), 'actions': sorted(content['actions']),
                                                             'media': [n['src'] for n in ir['hero']['nodes'] if n.get('t') == 'media']}}


if __name__ == '__main__':
    if len(sys.argv) != 5: raise SystemExit(__doc__)
    with open(sys.argv[1]) as f: composition = json.load(f)
    with open(sys.argv[2], encoding='utf-8') as f: page_html = f.read()
    with open(sys.argv[3]) as f: page_images = json.load(f)
    result, report = transplant(page_html, composition, page_images)
    with open(sys.argv[4], 'w', encoding='utf-8') as f: f.write(result)
    for problem in report['errors']: print(f"{problem['code']} {problem['at']}: {problem['message']}")
    print(json.dumps({'drawn': report['drawn'], 'problems': len(report['errors'])}))
    raise SystemExit(0 if report['drawn'] else 1)
