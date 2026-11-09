"""render_ir.py — draw a validated hero composition and put it in place of the page's hero.

The same composition and the same page always give the same bytes. The composed hero reuses the page's own tokens and
classes (`--paper`, `--display`, `.h1`, `.lab`, `.lede`, `.btn`), so it belongs to the page it sits in; it adds only
the grid that places the pieces. Every word and link comes from the production hero through lib/compose/content.py
and is escaped here. A composition that does not validate is never drawn: `transplant` returns the page untouched and
says why.

  render_hero(ir, content)        → the <section> for a composition that validate() accepts
  transplant(page_html, ir, images) → (page_html, report)     report = {'drawn': bool, 'errors': [...]}
  python3 lib/compose/render_ir.py <composition.json> <page.html> <images.json> <out.html>
Deterministic, no network, no model."""
import html as H, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import content as CONTENT
import validate as V

e = lambda s: H.escape(str(s if s is not None else ''), quote=True)

ROWS = {'auto': 'auto', '1fr': '1fr', '2fr': '2fr', 'min': 'min-content'}  # fr rows grow with their content: a hero has a minimum height, never a fixed one
GAP = {'sm': '16px', 'md': '24px', 'lg': '40px'}
HEIGHT = {'auto': 'auto', 'screen': '100svh', 'tall': '120svh'}
SIZE = {'xl': 'clamp(36px,4.6vw,68px)', 'xxl': 'clamp(46px,7.4vw,112px)', 'mega': 'clamp(54px,12.2vw,200px)'}
BAND = {'paper': '', 'dark': ' band-dark', 'alt': ' band-alt', 'accent': ' band-accent'}
SURFACE = {'paper': ('var(--paper)', 'var(--ink)'), 'dark': ('var(--band-paper)', 'var(--band-ink)'), 'alt': ('var(--alt,var(--paper))', 'var(--alt-ink,var(--ink))'), 'accent': ('var(--accent)', 'var(--on-accent,var(--paper))')}

# The grid and nothing else: type, colour and buttons are the page's own.
CSS = """
.hero.ir{display:flex;min-height:var(--ir-minh,auto);padding-top:calc(var(--nav-h,64px) + clamp(20px,3vw,44px));padding-bottom:clamp(28px,5vw,80px)}
.hero.ir .ir-grid{flex:1;display:grid;grid-template-columns:repeat(12,minmax(0,1fr));grid-template-rows:var(--ir-rows);column-gap:var(--ir-gap);row-gap:var(--ir-gap)}
.hero.ir .ir-n{grid-column:var(--c0)/var(--c1);grid-row:var(--r0)/var(--r1);z-index:var(--z,1);align-self:var(--self,start);min-width:0;container-type:inline-size;margin:0}
.hero.ir .ir-h{font-size:min(var(--ir-size),calc(100cqw / var(--lw,8) * 1.72));line-height:var(--h1-lh,1);margin:0;text-wrap:balance;overflow-wrap:normal}
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
.hero.ir .ir-frame-browser{border:1px solid var(--line);border-radius:max(10px,var(--radius,0));box-shadow:0 30px 80px -40px color-mix(in srgb,var(--ink) 55%,transparent);overflow:hidden}
.hero.ir .ir-frame-paper{background:#fff;padding:clamp(10px,1.4vw,22px);box-shadow:0 30px 80px -40px color-mix(in srgb,var(--ink) 55%,transparent)}
.hero.ir .ir-scrim::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.34),rgba(0,0,0,.16) 45%,rgba(0,0,0,.52))}
.hero.ir .ir-on-scrim,.hero.ir .ir-on-scrim .lab,.hero.ir .ir-on-scrim .lede{color:var(--on-photo,#F4EFE3)}.hero.ir .ir-on-scrim .btn.ghost{color:var(--on-photo,#F4EFE3);border-color:var(--on-photo,#F4EFE3)}
.hero.ir .ir-bleed-right{margin-right:calc(-1 * (var(--frame,24px) + max(0px,(100vw - var(--container,1300px)) / 2)))}
.hero.ir .ir-bleed-left{margin-left:calc(-1 * (var(--frame,24px) + max(0px,(100vw - var(--container,1300px)) / 2)))}
.hero.ir .ir-rule{height:1px;background:var(--line);align-self:var(--self,start)}
@media(max-width:900px){
.hero.ir{min-height:auto}
.hero.ir .ir-grid{display:flex;flex-direction:column;gap:22px}
.hero.ir .ir-n{order:var(--sm,0);align-self:stretch}
.hero.ir .ir-media{margin-left:0;margin-right:0;aspect-ratio:var(--sm-ratio,var(--ratio))}
.hero.ir .ir-al-end{text-align:left}.hero.ir .ir-al-end>*{margin-left:0}.hero.ir .ir-al-end .ctas,.hero.ir .ir-al-end .cat{justify-content:flex-start}
.hero.ir .ir-plate>*{background:none;color:inherit;padding:0;width:auto}
.hero.ir .ir-on-scrim,.hero.ir .ir-on-scrim .lab,.hero.ir .ir-on-scrim .lede{color:inherit}.hero.ir .ir-on-scrim .btn.ghost{color:inherit;border-color:currentColor}
}
"""


def _place(node, rows, phone_index):
    c0, c1, r0, r1 = V.area(node, rows)
    at = node['at']
    return f'--c0:{c0};--c1:{c1};--r0:{r0};--r1:{r1};--z:{at.get("z", 1)};--self:{at.get("self", "start")};--sm:{phone_index}'


def _headline(segments):
    return ''.join(f'<em>{e(text)}</em>' if em else e(text) for text, em in segments)


def _longest_word(segments):
    words = ''.join(text for text, _ in segments).split()
    return max((len(w) for w in words), default=6)


def render_hero(ir, content):
    """The hero <section> for a composition that validate() accepts. Call validate() first; this function assumes it passed."""
    hero = ir['hero']; rows = hero['rows']; nodes = hero['nodes']
    phone = (hero.get('sm') or {}).get('order') or [n['id'] for n in nodes]
    by_id = {n['id']: n for n in nodes}
    areas = {n['id']: V.area(n, len(rows)) for n in nodes}
    # text that sits on a scrimmed picture reads in the on-photo colour
    def on_scrim(node):
        return not node.get('plate') and any(m.get('t') == 'media' and m.get('scrim') and V.overlap(areas[node['id']], areas[m['id']]) for m in nodes)
    out = []
    for node in nodes:
        style = _place(node, len(rows), phone.index(node['id'])); kind = node['t']; nid = e(node['id'])
        if kind == 'text':
            role = node['as']; align = node.get('align', 'start'); value = content['text'][node['src']]
            classes = ['ir-n', 'ir-text', f'ir-al-{align}'] + ([f'ir-plate ir-plate-{node["plate"]}'] if node.get('plate') else []) + (['ir-on-scrim'] if on_scrim(node) else [])
            if role == 'h1':
                measure = f';max-width:{node["measure"]}ch' if node.get('measure') else ''
                inner = f'<h1 class="h1 ir-h" style="--ir-size:{SIZE[node.get("size", "xxl")]};--lw:{_longest_word(value)}{measure}">{_headline(value)}</h1>'
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
            m = content['media'][node['src']]; fit = node.get('fit', 'cover'); focal = node.get('focal', [0.5, 0.5])
            classes = ['ir-n', 'ir-media'] + (['ir-contain'] if fit == 'contain' else []) + ([f'ir-frame-{node["frame"]}'] if node.get('frame', 'none') != 'none' else []) \
                + (['ir-scrim'] if node.get('scrim') else []) + ([f'ir-bleed-{node["bleed"]}'] if node.get('bleed', 'none') != 'none' else [])
            style += f';--ratio:{node["ratio"]};--focal:{round(focal[0] * 100)}% {round(focal[1] * 100)}%'
            out.append(f'<figure class="{" ".join(classes)}" data-node="{nid}" style="{style}"><img src="{e(m["src"])}" alt="{e(m.get("alt", ""))}"></figure>')
        elif kind == 'shape':
            out.append(f'<div class="ir-n ir-rule" data-node="{nid}" style="{style}" aria-hidden="true"></div>')
    bg, fg = SURFACE[hero.get('surface', 'paper')]
    grid_style = f'--ir-rows:{" ".join(ROWS[r] for r in rows)};--ir-gap:{GAP[hero.get("gap", "md")]};--ir-minh:{HEIGHT[hero.get("height", "auto")]};--ir-bg:{bg};--ir-fg:{fg}'
    return (f'<section class="sec hero ir{BAND[hero.get("surface", "paper")]}" id="top" data-ir="{V.VERSION}" data-enter="{e(hero.get("enter", "none"))}" style="{grid_style}">'
            f'<div class="wrap ir-grid">{"".join(out)}</div></section>')


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
        page = page[:head] + f'<style id="ir-css">{CSS}</style>' + page[head:]
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
