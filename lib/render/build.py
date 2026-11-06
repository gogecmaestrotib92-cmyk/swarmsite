"""build.py — assemble a full swarm page for one concept.
python3 -I lib/render/build.py C2 light lib/render/content_sportbot.json lib/audit/sportbot_assets.json before_hero.jpg out.html"""
import sys, os, json, base64, subprocess
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'lib', 'render')); sys.path.insert(0, os.path.join(ROOT, 'lib', 'typography')); sys.path.insert(0, os.path.join(ROOT, 'lib', 'colour'))
from palette import palette, css as palette_css
from render import render
from typeselect import select

CONCEPT_ACCENT = {'C1': '#FA3600', 'C2': '#A8FFCB', 'C3': '#FD4401', 'C4': '#BEFF8B', 'C5': '#111111', 'C6': '#E6E9E8', 'C7': '#FF2E8A', 'C8': '#E8522B'}
CONCEPT_NAME = {'C1': 'Blueprint', 'C2': 'Swiss grid', 'C3': 'Flat colour', 'C4': 'Pastel editorial', 'C5': 'Calm SaaS', 'C6': 'Black luxury', 'C7': 'Dark infra', 'C8': 'Themed world'}
FONT_LINKS = json.load(open(os.path.join(ROOT, 'lib', 'typography', 'fonts.json')))  # names only; links built below

def gf(name): return 'family=' + name.replace(' ', '+') + ':wght@300;400;500;600;700;800'

def contrast_text(hexc):
    h = hexc.lstrip('#'); r, g, b = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    return '#0B0B0B' if (0.2126 * r + 0.7152 * g + 0.0722 * b) > 0.45 else '#FFFFFF'

def build(concept, mode, content_path, assets_path, before_img, out, images_path=None):
    content = json.load(open(content_path)); assets = json.load(open(assets_path))
    images = {i.get('id', str(n)): i for n, i in enumerate(json.load(open(images_path)))} if images_path and os.path.exists(images_path) else {}
    content['_images'] = {k: True for k in images}
    sel = select(concept, mode, assets)
    concepts = json.load(open(os.path.join(ROOT, 'lib', 'concepts', 'concepts.json')))['concepts'][concept]
    concept_display = concepts['fonts']['display']
    # tokens: brand selection as base
    tok = subprocess.run(['python3', '-I', os.path.join(ROOT, 'lib', 'css', 'tokens.py'), concept, mode, sel['accent'], sel['display']], capture_output=True, text=True).stdout
    tok = '\n'.join(l for l in tok.splitlines() if not l.startswith('/*'))
    # colour as a world: full token set derived from the hue (palette.py), one block per selectable world
    WORLDS = [('brand', sel['accent']), ('concept', CONCEPT_ACCENT[concept]), ('red', '#E63946'), ('blue', '#1D5CFF'), ('amber', '#FDCB40')]
    worlds_meta = []
    for i, (name, hx) in enumerate(WORLDS):
        pal = palette(hx, concept, mode); selector = ':root' if i == 0 else f'html[data-world="{name}"]'
        tok += '\n' + palette_css(pal, selector); worlds_meta.append({'name': name, 'hex': pal['tokens']['accent'], 'paper': pal['tokens']['paper'], 'checks': pal['checks']})
    tok += f"""
html[data-font="concept"]{{--font-display:'{concept_display}',system-ui,sans-serif;--display-weight:{concepts['fonts'].get('display_weight', 600)}}}
"""
    sel['accent_on_text'] = True  # palette.py guarantees a text-safe --accent-ink
    if not sel['accent_on_text']:
        tok += "\n.accent{color:inherit;background:var(--accent);padding:0 .08em;box-decoration-break:clone}.num.accent{background:none;color:inherit;text-decoration:underline;text-decoration-thickness:.08em;text-underline-offset:.1em;text-decoration-color:var(--accent)}\n"
    body, page_css, body_cls = render(content, concept)
    fonts = sorted({sel['display'], sel['body'], sel['mono'], concept_display})
    link = 'https://fonts.googleapis.com/css2?' + '&'.join(gf(f) for f in fonts) + '&display=swap'
    comp = open(os.path.join(ROOT, 'lib', 'css', 'components.css')).read()
    moves = open(os.path.join(ROOT, 'lib', 'motion', 'moves.js')).read() + '\n' + open(os.path.join(ROOT, 'lib', 'artefacts', 'artefacts.js')).read()
    swarm = open(os.path.join(ROOT, 'swarm.js')).read().replace(
        "const BOX_SEL = '.card, .record, .rows li, .ways > div, .plans > div, .lifetime, .faq details, .rg, .stores a, .pricelist li, .stats .grid div, .btn, nav';",
        "const BOX_SEL = '.card, .cells > div, .g > *, .tile, .dcard, .frame, .rows li, .trow, .lifetime > div, .faq details, .btn, .pillb, .nav, .c3nav .bar, .marquee, .pillbar';")
    img = base64.b64encode(open(before_img, 'rb').read()).decode()
    intro = open(os.path.join(ROOT, 'v2', 'intro.js')).read().replace('IMG', img)
    a = content['audit']; b = content['brand']
    intro = intro.replace('v2 · Concept C1 Blueprint · 7 beats · ~620 words', f'Concept {concept} {CONCEPT_NAME[concept]} · 7 beats · ~620 words')
    intro = intro.replace(f'audit score 28/100 · 2,400 words · 17 sections', f"audit score {a['score']}/100 · {a['words']:,} words · {a['sections']} sections")
    intro = intro.replace('Keep my font <b>Barlow Condensed</b>', f'Keep my font <b>{sel["display"]}</b>')
    sw = ''.join(f'<label class="sw"><input type="radio" name="world" value="{w["name"]}"{" checked" if i == 0 else ""}><i style="background:{w["hex"]};outline-color:{w["paper"]}"></i><span>{w["name"]}</span></label>' for i, w in enumerate(worlds_meta))
    intro = intro.replace('<!--WORLDS-->', sw)
    why = ' · '.join(sel['why'])
    html = f"""<!DOCTYPE html>
<html lang="en" data-font="brand" data-color="brand">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{b['name']} — Concept {concept} {CONCEPT_NAME[concept]}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="{link}" rel="stylesheet">
<style>
{tok}
{comp}
.teams{{font-family:var(--font-display);font-size:24px;font-weight:700;text-transform:uppercase;line-height:1.05;margin:4px 0 14px}}
.note-conflict{{font-family:var(--font-mono);font-size:10.5px;letter-spacing:.08em;text-transform:uppercase;color:#E06A4A;margin-top:12px}}
.sec-head{{display:grid;grid-template-columns:1fr 1fr;gap:48px;align-items:end;margin-bottom:48px}}.sec-head .label{{display:block;margin-bottom:16px}}
html,body{{overflow-x:hidden;max-width:100vw}}.marquee{{overflow:hidden}}.deck{{overflow:hidden}}.leagues{{display:flex;white-space:nowrap;width:max-content}}.leagues span{{padding:0 8px}}
@media(max-width:900px){{.sec-head{{grid-template-columns:1fr;gap:16px}}}}
{page_css}
</style>
</head>
<body class="{body_cls}">
<!-- typography rules: {why} -->
{body}
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
<script>{moves}</script>
<script>{swarm}</script>
<script>{intro}</script>
</body></html>"""
    html = html.replace('{{LOGO}}', assets['logo']['data'])
    import re as _re
    html = _re.sub(r'\{\{IMG:([a-z0-9-]+)\}\}', lambda m: images.get(m.group(1), {}).get('data', ''), html)
    open(out, 'w').write(html); print(out, len(html), '|', why)

if __name__ == '__main__':
    build(*sys.argv[1:8])
