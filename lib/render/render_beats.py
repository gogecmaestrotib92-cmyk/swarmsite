"""render_beats.py — draws a direction.json (beats document) into one self-contained HTML page.
Generalised from master run 01 (frans.rs). Two voices: serif (place/service/luxury) and sans (software/product).
Usage: python3 lib/render/render_beats.py out/<slug> [hero.mp4]  → out/<slug>/index.html"""
import json, os, sys, base64, html as H
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'lib', 'colour'))
from palette import palette, css as palette_css
e = lambda s: H.escape(str(s if s is not None else ''))

FONT_LINKS = {
    'serif': "family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Fraunces:ital,opsz,wght,SOFT,WONK@0,9..144,300..600,0..100,0..1;1,9..144,300..600,0..100,0..1&family=Instrument+Serif:ital@0;1&family=Instrument+Sans:wght@400;500;600",
    'sans': "family=Instrument+Sans:wght@400;500;600&family=Space+Grotesk:wght@300..700&family=Bricolage+Grotesque:wght@400..800&family=JetBrains+Mono:wght@400;500",
}

def b64file(p, mime):
    return f'data:{mime};base64,' + base64.b64encode(open(p, 'rb').read()).decode()

def build(slug_dir, video_path=None):
    d = json.load(open(os.path.join(slug_dir, 'direction.json')))
    images = {i.get('id', str(n)): i for n, i in enumerate(json.load(open(os.path.join(slug_dir, 'images.json'))))} if os.path.exists(os.path.join(slug_dir, 'images.json')) else {}
    assets = json.load(open(os.path.join(slug_dir, 'assets.json'))) if os.path.exists(os.path.join(slug_dir, 'assets.json')) else {}
    logo = (assets.get('logo') or {}).get('data') or (open(os.path.join(slug_dir, 'logo.txt')).read() if os.path.exists(os.path.join(slug_dir, 'logo.txt')) else '')
    moves = open(os.path.join(ROOT, 'lib/motion/moves.js')).read()
    swarm = open(os.path.join(ROOT, 'lib/motion/swarm.js')).read()
    used = set()
    def pick_best(prefer_hero=True):
        pool = [i for i in images.values() if i.get('data') and i.get('id', '') not in used] or [i for i in images.values() if i.get('data')]
        if not pool: return None
        pool.sort(key=lambda i: (not (i.get('heroGrade') if prefer_hero else True), -(i.get('w', 0) * i.get('h', 0))))
        return pool[0]
    def img(k, fallback=True):
        """Resolve an image id from direction.json; tolerate wrong/missing ids (LLM) by falling back to the best unused photo."""
        it = images.get(k) if k else None
        if not it and k:  # director may have used the src or a loose name
            it = next((i for i in images.values() if k in (i.get('src', ''), i.get('alt', '')) or k == str(i.get('id'))), None)
        if not it and fallback: it = pick_best()
        if not it: return ''
        used.add(it.get('id', '')); return it.get('data', '')
    voice = d.get('voice', 'serif'); b = d['brand']; mode = d.get('mode', 'light'); concept = d.get('concept', 'C8')
    base_hex = b.get('accent') or b.get('ink') or '#0F2A14'
    pal = palette(base_hex, concept, mode)
    # brand-stated paper/ink override the derived ones
    tok = pal['tokens'].copy()
    if b.get('paper'): tok['paper'] = b['paper']
    if b.get('ink'): tok['ink'] = b['ink']
    worlds = [('brand', base_hex)] + [(n, h) for n, h in [('terracotta', '#B4533A'), ('navy', '#1F3A5F'), ('plum', '#5B2A3E'), ('forest', '#0F2A14')] if h.lower() != base_hex.lower()][:3]
    world_css = ''.join(palette_css(palette(h, concept, mode), f'html[data-world="{n}"]') + '\n' for n, h in worlds[1:])
    world_css += f'html[data-world="ink"]{{--paper:{tok["ink"]};--ink:{tok["paper"]};--muted:color-mix(in srgb,{tok["paper"]} 60%,transparent);--line:color-mix(in srgb,{tok["paper"]} 18%,transparent)}}\n'
    display = b.get('font_hint') if b.get('keep_font') and b.get('font_hint') else ('Cormorant Garamond' if voice == 'serif' else 'Space Grotesk')
    fonts_link = 'https://fonts.googleapis.com/css2?' + FONT_LINKS[voice] + ('&family=' + display.replace(' ', '+') + ':wght@400;500;600;700' if display not in ('Cormorant Garamond', 'Space Grotesk', 'Instrument Sans') else '') + '&display=swap'
    serif = voice == 'serif'

    def beat_html(bt):
        t = bt['type']; i = bt.get('id', t)
        if t == 'quote':
            return f'<section class="sec quote" id="{e(i)}"><div class="wrap"><span class="lab">{e(bt.get("label"))}</span><h2 class="big" data-move="scale-settle">{e(bt.get("big"))}</h2><p class="body" data-move="word-blur-in">{e(bt.get("body"))}</p>{("<p class=\"who lab\">" + e(bt["who"]) + "</p>") if bt.get("who") else ""}</div></section>'
        if t == 'photo':
            cap = bt.get('cap') or ['', '']
            src = img(bt.get('image'))
            return f'<section class="sec tight" id="{e(i)}"><div class="wrap"><div class="gh"><div><span class="lab">{e(bt.get("label"))}</span><h2 class="h2" style="margin-top:16px" data-move="masked-line-reveal">{e(bt.get("h2"))}</h2></div><p class="lede">{e(bt.get("lede"))}</p></div><div class="garden one"><div>{('<div class="bigimg" data-move="clip-reveal"><img src="' + src + '" alt=""></div>') if src else ''}<div class="cap"><span class="lab">{e(cap[0])}</span><span class="lab">{e(cap[1] if len(cap) > 1 else "")}</span></div></div></div></div></section>'
        if t == 'ledger':
            items = ''.join(f'<li><span class="d">{e(n)}</span><span class="dots"></span><span class="p">{e(p)}</span></li>' for n, p in bt.get('items', []))
            src = img(bt.get('image'), fallback=False) if bt.get('image') else ''
            photo = f'<div class="photo" data-move="clip-reveal"><img src="{src}" alt=""></div>' if src else ''
            ctas = (f'<a class="btn solid" href="{e(bt.get("cta_href") or "#")}">{e(bt["cta"])} <span class="ar">→</span></a>' if bt.get('cta') else '') + (f'<a class="btn" href="{e(bt.get("cta2_href") or "#")}">{e(bt["cta2"])}</a>' if bt.get('cta2') else '')
            return f'<section class="sec" id="{e(i)}"><div class="wrap"><div class="menu"><div><span class="lab">{e(bt.get("label"))}</span><h2 class="h2" style="margin-top:16px" data-move="masked-line-reveal">{e(bt.get("h2"))}</h2><p class="lede" style="margin-top:22px">{e(bt.get("lede"))}</p>{photo}</div><div><ul class="ledger" data-move="stagger-in">{items}</ul><div style="margin-top:28px;display:flex;gap:14px;flex-wrap:wrap">{ctas}</div></div></div></div></section>'
        if t == 'facts':
            facts = ''.join(f'<div class="f"><b data-move="number-scramble">{e(n)}</b><span class="lab light">{e(l)}</span></div>' for n, l in bt.get('facts', []))
            src = img(bt.get('image'))
            return f'<div class="band{"" if src else " nophoto"}" id="{e(i)}" data-move="parallax" data-parallax="8">{("<img src=\"" + src + "\" alt=\"\">") if src else ""}<div class="wrap">{facts}</div></div>'
        if t == 'cells':
            cells = ''.join(f'<div><span class="lab">{e(a)}</span><b class="num" data-move="number-scramble">{e(n)}</b><span class="lab">{e(s)}</span></div>' for a, n, s in bt.get('cells', []))
            return f'<section class="sec" id="{e(i)}"><div class="wrap"><div class="gh"><div><span class="lab">{e(bt.get("label"))}</span><h2 class="h2" style="margin-top:16px" data-move="masked-line-reveal">{e(bt.get("h2"))}</h2></div><p class="lede">{e(bt.get("lede"))}</p></div><div class="cells" data-move="stagger-in">{cells}</div></div></section>'
        if t == 'steps':
            steps = ''.join(f'<li><span class="lab">0{n+1}</span><span class="st">{e(s)}</span></li>' for n, s in enumerate(bt.get('steps', [])))
            return f'<section class="sec" id="{e(i)}"><div class="wrap"><span class="lab">{e(bt.get("label"))}</span><h2 class="h2" style="margin:16px 0 36px" data-move="masked-line-reveal">{e(bt.get("h2"))}</h2><ol class="steps" data-move="stagger-in">{steps}</ol><p class="lede" style="margin-top:28px">{e(bt.get("note"))}</p></div></section>'
        if t == 'form':
            fields = ''.join(f'<label><span class="lab light">{e(f)}</span><input placeholder="{e(f)}"></label>' for f in bt.get('fields', []))
            alt = ''.join(f'<span>{e(a)}</span>' for a in bt.get('alt', []))
            src = img(bt.get('image'), fallback=False) if bt.get('image') else ''
            photo = f'<div class="photo" data-move="clip-reveal"><img src="{src}" alt=""></div>' if src else '<div></div>'
            return f'<section class="sec res" id="{e(i)}"><div class="wrap"><div class="grid">{photo}<div><span class="lab light">{e(bt.get("label"))}</span><h2 class="h2" style="margin-top:16px" data-move="masked-line-reveal">{e(bt.get("h2"))}</h2><form class="form" onsubmit="return false">{fields}<div class="full"><a class="btn light solid" href="#">{e(bt.get("cta"))} <span class="ar">→</span></a></div></form><div class="alt">{alt}</div></div></div></div></section>'
        if t == 'faq':
            items = ''.join(f'<details{" open" if n == 0 else ""}><summary>{e(q)}</summary><p>{e(a)}</p></details>' for n, (q, a) in enumerate(bt.get('items', [])))
            return f'<section class="sec tight faq" id="{e(i)}"><div class="wrap" style="max-width:860px"><span class="lab">{e(bt.get("label"))}</span><div style="margin-top:20px">{items}</div></div></section>'
        return ''

    h = d['hero']; nav = d['nav']; en = d.get('ending', {})
    hero_media = f'<video autoplay muted loop playsinline poster="{img(h.get("media"))}"><source src="{b64file(video_path, "video/mp4")}" type="video/mp4"></video>' if video_path and os.path.exists(video_path) else (f'<img src="{img(h.get("media"))}" alt="">' if img(h.get('media')) else '')
    h1 = e(h['h1']).replace('&lt;em&gt;', '<em class="it">').replace('&lt;/em&gt;', '</em>')
    links = ''.join(f'<a href="{e(u)}">{e(l)}</a>' for u, l in nav.get('links', [])[:4])
    cols = ''.join(f'<div><h5>{e(t)}</h5><ul>{"".join("<li>" + e(x) + "</li>" for x in items)}</ul></div>' for t, items in en.get('cols', []))
    lg = assets.get('logo') or {}; lr = (lg.get('w') or 0) / (lg.get('h') or 1) if lg.get('w') and lg.get('h') else 0
    maskable = logo.startswith('data:image/svg')  # SVG: fine as a mask. Raster: only if it has real transparency.
    if logo.startswith('data:image/') and not logo.startswith('data:image/svg'):
        try:
            import base64, io
            from PIL import Image
            raw = base64.b64decode(logo.split(',', 1)[1]); im = Image.open(io.BytesIO(raw)); lr = lr or im.width / max(1, im.height)
            if 'A' in im.getbands():
                a = im.getchannel('A'); hist = a.histogram(); opaque = sum(hist[128:]) / max(1, sum(hist)); maskable = 0.03 < opaque < 0.85
        except Exception:
            maskable = False
    lh = 44 if lr >= 1.2 else 62; lw = min(200, max(44, round(lh * lr))) if lr else (44 if not lr else 160)
    if logo and maskable: mark = f'<span class="mark" style="width:{lw}px;height:{lh}px;-webkit-mask-image:url(\'{logo}\');mask-image:url(\'{logo}\')"></span>'
    elif logo: mark = f'<img class="logo-img" src="{logo}" alt="{e(b["name"])}" style="height:{lh}px;width:auto;max-width:200px;display:block">'
    else: mark = f'<span class="wordmark">{e(b["name"])}</span>'
    beats = '\n'.join(beat_html(bt) for bt in d['beats'])
    worlds_ui = ''.join(f'<label><input type="radio" name="bw" value="{n}"{" checked" if k == 0 else ""}><i style="background:{palette(hx, concept, mode)["tokens"]["ink"]};outline-color:{palette(hx, concept, mode)["tokens"]["paper"]}"></i><span>{"Njihove" if n == "brand" else n}</span></label>' for k, (n, hx) in enumerate(worlds)) + '<label><input type="radio" name="bw" value="ink"><i style="background:#F4EFE3;outline-color:#111"></i><span>Tamno</span></label>'
    fonts_ui = f'<label><input type="radio" name="bf" value="brand" checked><span>{e(display)}</span></label>' + (''.join(f'<label><input type="radio" name="bf" value="{v}"><span>{l}</span></label>' for v, l in (('fraunces', 'Fraunces'), ('instrument', 'Instrument Serif'))) if serif else ''.join(f'<label><input type="radio" name="bf" value="{v}"><span>{l}</span></label>' for v, l in (('bricolage', 'Bricolage'), ('instrument-sans', 'Instrument Sans'))))

    css = f'''
:root{{--on-photo:#F4EFE3;--serif:'{display}',Georgia,serif;--sans:'Instrument Sans',system-ui,sans-serif;--mono:'JetBrains Mono',ui-monospace,monospace;--gutter:clamp(20px,4.5vw,72px);--max:1440px}}
{palette_css(pal)}
:root{{--paper:{tok['paper']};--ink:{tok['ink']}}}
{world_css}
html[data-font="fraunces"]{{--serif:'Fraunces',Georgia,serif}}html[data-font="fraunces"] .h1,html[data-font="fraunces"] .h2,html[data-font="fraunces"] .quote .big,html[data-font="fraunces"] .giant{{font-variation-settings:"WONK" 1,"SOFT" 40;letter-spacing:-.03em}}
html[data-font="instrument"]{{--serif:'Instrument Serif',Georgia,serif}}
html[data-font="bricolage"]{{--serif:'Bricolage Grotesque',system-ui,sans-serif}}html[data-font="instrument-sans"]{{--serif:'Instrument Sans',system-ui,sans-serif}}
*{{box-sizing:border-box;margin:0;padding:0}}html{{scroll-behavior:auto}}html,body{{overflow-x:hidden}}
body{{background:var(--paper);color:var(--ink);font-family:var(--sans);font-size:16px;line-height:1.5;-webkit-font-smoothing:antialiased}}
img,video{{display:block;max-width:100%}}a{{color:inherit;text-decoration:none}}
.wrap{{max-width:var(--max);margin:0 auto;padding:0 var(--gutter);width:100%;min-width:0}}
.lab{{font-family:{'var(--serif)' if serif else 'var(--mono)'};font-weight:500;font-size:{'13px' if serif else '11px'};letter-spacing:{'.22em' if serif else '.12em'};text-transform:uppercase;color:var(--muted)}}
.lab.light{{color:rgba(244,239,227,.72)}}.it{{font-style:italic}}
h1,h2,h3{{font-family:var(--serif);font-weight:{'400' if serif else '500'};line-height:1.02;letter-spacing:{'-.015em' if serif else '-.03em'}}}
.h1{{font-size:clamp(52px,7.4vw,124px)}}.h2{{font-size:clamp(40px,5.2vw,84px)}}
.lede{{font-family:{'var(--serif)' if serif else 'var(--sans)'};font-size:clamp(19px,1.5vw,25px);line-height:1.35;max-width:38ch}}
.btn{{display:inline-flex;align-items:center;gap:14px;font-family:{'var(--serif)' if serif else 'var(--sans)'};font-size:{'18px' if serif else '15px'};font-weight:500;letter-spacing:.03em;padding:16px 26px;border:1px solid currentColor;border-radius:999px;min-height:44px;transition:background .3s,color .3s,transform .35s cubic-bezier(.2,.8,.2,1)}}
.btn.solid{{background:var(--ink);color:var(--paper);border-color:var(--ink)}}.btn.light{{color:var(--on-photo)}}.btn.light.solid{{background:var(--on-photo);color:#111;border-color:var(--on-photo)}}
.btn:hover{{transform:translateY(-2px)}}.btn:active{{transform:scale(.97);transition:transform 100ms ease-out}}.btn .ar{{transition:transform .35s}}.btn:hover .ar{{transform:translateX(4px)}}
.nav{{position:fixed;inset:0 0 auto 0;z-index:50;padding:22px 0;color:var(--on-photo);transition:background .4s,color .4s,padding .4s}}
.nav .wrap{{display:flex;align-items:center;justify-content:space-between;gap:24px}}
.nav .mark{{display:block;width:44px;height:62px;background:currentColor;-webkit-mask-size:contain;mask-size:contain;-webkit-mask-repeat:no-repeat;mask-repeat:no-repeat;-webkit-mask-position:center;mask-position:center}}
.nav .wordmark{{font-family:var(--serif);font-size:24px;letter-spacing:-.02em}}
.nav .links{{display:flex;gap:34px;font-family:{'var(--serif)' if serif else 'var(--sans)'};font-size:{'17px' if serif else '15px'};letter-spacing:.04em}}
.nav .links a{{position:relative;min-height:44px;display:inline-flex;align-items:center}}.nav .links a::after{{content:"";position:absolute;left:0;right:100%;bottom:6px;border-bottom:1px solid currentColor;transition:right .4s cubic-bezier(.2,.8,.2,1)}}.nav .links a:hover::after{{right:0}}
.nav.solid{{background:color-mix(in srgb,var(--paper) 78%,transparent);backdrop-filter:blur(16px) saturate(180%);color:var(--ink);padding:14px 0;box-shadow:0 1px 0 var(--line)}}
.nav.solid .mark{{transform:scale(.8);transform-origin:left center}}.nav.solid .btn{{color:var(--ink);border-color:var(--ink)}}
@media(prefers-reduced-transparency:reduce){{.nav.solid{{background:var(--paper);backdrop-filter:none}}}}
.hero{{position:relative;min-height:100svh;display:grid;align-content:end;color:var(--on-photo);overflow:hidden}}
.hero .media{{position:absolute;inset:0;z-index:0;background:var(--ink)}}.hero .media video,.hero .media img{{width:100%;height:100%;object-fit:cover;object-position:center 30%;transform:scale(1.04)}}
.hero .media::after{{content:"";position:absolute;inset:0;background:linear-gradient(180deg,color-mix(in srgb,var(--ink) 55%,transparent) 0%,color-mix(in srgb,var(--ink) 15%,transparent) 35%,color-mix(in srgb,var(--ink) 35%,transparent) 65%,color-mix(in srgb,var(--ink) 92%,transparent) 100%)}}
.hero .wrap{{position:relative;z-index:1;padding-top:140px;padding-bottom:clamp(40px,6vw,72px);display:grid;grid-template-columns:1fr auto;gap:40px;align-items:end}}
.hero .cat{{display:flex;gap:28px;flex-wrap:wrap;margin-bottom:26px}}.hero .h1{{max-width:11ch}}.hero .lede{{margin-top:26px;color:var(--on-photo);opacity:.85}}
.hero .ctas{{display:flex;gap:14px;margin-top:34px;flex-wrap:wrap}}.hero .side{{display:grid;gap:10px;text-align:right}}.hero .side .big{{font-family:var(--serif);font-size:clamp(48px,6vw,96px);line-height:.9}}
.sec{{padding:clamp(80px,10vw,150px) 0}}.sec.tight{{padding:clamp(48px,6vw,88px) 0}}
.quote{{text-align:center}}.quote .big{{font-family:var(--serif);font-style:{'italic' if serif else 'normal'};font-size:clamp(56px,9vw,150px);line-height:.95;letter-spacing:-.02em;max-width:14ch;margin:24px auto 0}}
.quote p.body{{font-family:{'var(--serif)' if serif else 'var(--sans)'};font-size:clamp(20px,1.7vw,27px);line-height:1.4;max-width:46ch;margin:40px auto 0}}.quote .who{{margin-top:22px}}
.gh{{display:grid;grid-template-columns:1fr 1fr;gap:40px;align-items:end;margin-bottom:clamp(32px,4vw,64px)}}
.garden.one{{display:grid}}.bigimg{{aspect-ratio:21/10;overflow:hidden}}.bigimg img{{width:100%;height:100%;object-fit:cover}}.cap{{display:flex;justify-content:space-between;gap:16px;margin-top:14px;flex-wrap:wrap}}
.menu{{display:grid;grid-template-columns:5fr 7fr;gap:clamp(32px,5vw,96px);align-items:start}}
.ledger{{list-style:none}}.ledger li{{display:flex;align-items:baseline;gap:10px;padding:16px 0;border-bottom:1px solid var(--line);font-family:var(--serif);font-size:clamp(19px,1.5vw,24px)}}
.ledger .dots{{flex:1;border-bottom:1px dotted var(--line);transform:translateY(-6px)}}.ledger .p{{font-variant-numeric:tabular-nums;white-space:nowrap}}
.menu .photo{{aspect-ratio:1;overflow:hidden;margin-top:12px}}.menu .photo img,.res .photo img{{width:100%;height:100%;object-fit:cover}}
.band{{position:relative;min-height:78vh;display:grid;align-items:end;overflow:hidden;color:var(--on-photo)}}.band.nophoto{{background:var(--ink);min-height:48vh}}.band img{{position:absolute;inset:0;width:100%;height:112%;object-fit:cover}}
.band::after{{content:"";position:absolute;inset:0;background:linear-gradient(180deg,color-mix(in srgb,var(--ink) 5%,transparent),color-mix(in srgb,var(--ink) 85%,transparent))}}
.band .wrap{{position:relative;z-index:1;padding-bottom:clamp(40px,6vw,72px);display:grid;grid-template-columns:repeat(3,1fr);gap:24px;align-items:end}}
.band .f b{{display:block;font-family:var(--serif);font-size:clamp(48px,6vw,104px);line-height:.9;letter-spacing:-.02em;margin-bottom:10px;font-variant-numeric:tabular-nums}}
.cells{{display:grid;grid-template-columns:repeat(3,1fr);border:1px solid var(--line)}}.cells>div{{padding:28px 24px;border-right:1px solid var(--line);border-bottom:1px solid var(--line);min-height:170px;display:flex;flex-direction:column;justify-content:space-between;gap:16px}}.cells>div:nth-child(3n){{border-right:0}}
.cells .num{{font-family:var(--serif);font-size:clamp(44px,5vw,80px);line-height:1;font-variant-numeric:tabular-nums}}
.steps{{list-style:none;display:grid;gap:0}}.steps li{{display:grid;grid-template-columns:60px 1fr;gap:20px;padding:26px 0;border-top:1px solid var(--line);align-items:baseline}}.steps .st{{font-family:var(--serif);font-size:clamp(26px,3vw,44px);line-height:1.05}}
.res{{background:var(--ink);color:var(--paper)}}.res .grid{{display:grid;grid-template-columns:5fr 7fr;gap:clamp(32px,5vw,96px);align-items:center}}.res .photo{{aspect-ratio:4/5;overflow:hidden}}
.form{{display:grid;grid-template-columns:1fr 1fr;gap:18px 28px;margin-top:36px}}.form label{{display:grid;gap:8px}}
.form input{{background:transparent;border:0;border-bottom:1px solid color-mix(in srgb,var(--paper) 35%,transparent);color:var(--paper);font-family:var(--serif);font-size:22px;padding:10px 0;outline:0;border-radius:0;min-height:44px}}.form input::placeholder{{color:color-mix(in srgb,var(--paper) 40%,transparent)}}
.form .full{{grid-column:1/3}}.res .alt{{margin-top:28px;display:flex;gap:28px;flex-wrap:wrap;color:color-mix(in srgb,var(--paper) 75%,transparent);font-family:var(--serif);font-size:18px}}
.res .lab.light{{color:color-mix(in srgb,var(--paper) 70%,transparent)}}.res .btn.light{{color:var(--paper)}}.res .btn.light.solid{{background:var(--paper);color:var(--ink);border-color:var(--paper)}}
.faq details{{border-top:1px solid var(--line);padding:18px 0}}.faq details:last-child{{border-bottom:1px solid var(--line)}}.faq summary{{cursor:pointer;list-style:none;display:flex;justify-content:space-between;font-family:var(--serif);font-size:clamp(20px,1.6vw,26px);min-height:44px;align-items:center}}
.faq summary::after{{content:"+";color:var(--muted)}}.faq details[open] summary::after{{content:"–"}}.faq p{{margin-top:10px;color:var(--muted);max-width:62ch;font-size:17px}}
.end{{padding:clamp(72px,9vw,130px) 0 28px;overflow:hidden}}.end .cols{{display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:32px;padding-bottom:48px;border-bottom:1px solid var(--line)}}
.end h5{{font-family:{'var(--serif)' if serif else 'var(--mono)'};font-weight:500;font-size:{'13px' if serif else '11px'};letter-spacing:.2em;text-transform:uppercase;color:var(--muted);margin-bottom:14px}}.end ul{{list-style:none;font-family:{'var(--serif)' if serif else 'var(--sans)'};font-size:{'19px' if serif else '15px'};line-height:1.7}}
.giant{{font-family:var(--serif);font-style:{'italic' if serif else 'normal'};font-size:clamp(100px,22vw,380px);line-height:.78;letter-spacing:-.03em;margin:40px 0 0;color:var(--ink);overflow-wrap:anywhere}}
.end .legal{{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-top:22px;font-size:12.5px;color:var(--muted)}}
.bp{{position:fixed;left:16px;bottom:16px;z-index:60;background:rgba(17,17,17,.92);color:#F4EFE3;backdrop-filter:blur(10px);border-radius:14px;padding:12px 14px;font:500 12px/1.3 var(--sans);display:grid;gap:10px;box-shadow:0 20px 50px rgba(0,0,0,.35);max-width:min(92vw,440px)}}
.bp .row{{display:flex;gap:8px;align-items:center;flex-wrap:wrap}}.bp .t{{opacity:.6;letter-spacing:.14em;text-transform:uppercase;font-size:10px;min-width:52px}}
.bp label{{display:inline-flex;gap:6px;align-items:center;padding:6px 10px;border:1px solid rgba(244,239,227,.25);border-radius:999px;cursor:pointer;min-height:32px}}.bp label:has(input:checked){{background:#F4EFE3;color:#111;border-color:#F4EFE3}}
.bp input{{position:absolute;opacity:0;width:0;height:0}}.bp i{{width:12px;height:12px;border-radius:50%;display:inline-block;outline:2px solid rgba(255,255,255,.35)}}.bp .x{{position:absolute;right:8px;top:6px;background:none;border:0;color:inherit;opacity:.6;cursor:pointer;font-size:16px}}
@media(max-width:900px){{.nav .links{{display:none}}.hero .wrap{{grid-template-columns:1fr;padding-top:110px}}.hero .side{{text-align:left}}.hero .h1{{font-size:clamp(44px,12vw,72px)}}.gh,.menu,.res .grid{{grid-template-columns:1fr}}.bigimg{{aspect-ratio:4/3}}.band .wrap{{grid-template-columns:1fr;gap:18px}}.form{{grid-template-columns:1fr}}.form .full{{grid-column:auto}}.end .cols{{grid-template-columns:1fr 1fr}}.quote .big{{font-size:13vw}}.cells{{grid-template-columns:1fr}}.cells>div{{border-right:0}}.steps li{{grid-template-columns:40px 1fr}}}}
'''
    html = f'''<!DOCTYPE html><html lang="{e(d.get('lang', 'en'))}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(b['name'])} — {e(h.get('category'))}</title><link rel="preconnect" href="https://fonts.googleapis.com"><link href="{fonts_link}" rel="stylesheet">
<style>{css}</style></head><body>
<nav class="nav" id="nav"><div class="wrap"><a href="#" aria-label="{e(b['name'])}">{mark}</a><div class="links">{links}</div><a class="btn light" href="#{e(next((bt['id'] for bt in d['beats'] if bt['type'] == 'form'), ''))}">{e(nav.get('cta'))} <span class="ar">→</span></a></div></nav>
<section class="hero" data-move="hero-intro"><div class="media">{hero_media}</div><div class="wrap"><div><div class="cat"><span class="lab light">{e(h.get('category'))}</span><span class="lab light">{e(h.get('fact'))}</span></div><h1 class="h1">{h1}</h1><p class="lede">{e(h.get('lede'))}</p><div class="ctas"><a class="btn light solid" href="#{e(next((bt['id'] for bt in d['beats'] if bt['type'] == 'form'), ''))}">{e(h.get('cta'))} <span class="ar">→</span></a>{("<a class=\"btn light\" href=\"#" + e(d['beats'][1]['id'] if len(d['beats']) > 1 else '') + "\">" + e(h['cta2']) + "</a>") if h.get('cta2') else ''}</div></div></div></section>
{beats}
<footer class="end" id="kontakt"><div class="wrap"><div class="cols">{cols}</div><div class="giant" data-move="giant-scrub" aria-hidden="true">{e(b['name'])}</div><div class="legal"><span>{e(en.get('legal'))}</span><span>{e(en.get('next'))}</span></div></div></footer>
<div class="bp" id="bp"><button class="x" id="bpx" aria-label="close">×</button><div class="row"><span class="t">Font</span>{fonts_ui}</div><div class="row"><span class="t">Boje</span>{worlds_ui}</div></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script><script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script><script src="https://unpkg.com/lenis@1.1.18/dist/lenis.min.js"></script>
<script>{moves}</script>
<script>{swarm}</script>
<script>/* Preview mode: the swarm visibly builds this page (inside the Swarmsite app, or with ?swarm). The kit itself loads normally. */
addEventListener('load',()=>{{ try{{ if(PREVIEW) new Swarm({{agents:innerWidth<900?8:18,speed:1,hud:true,sectionSelector:'section,.band,footer',boxSel:'.btn,.photo,.bigimg,.cells>div,.form input,.form textarea,.form select,.menu li,.steps li,.faq details,.ledger li,.card,.fact',onDone:()=>{{ try{{ scrollTo(0,0); Moves.init(); }}catch(e){{}} }}}}).run(); }}catch(e){{ try{{Moves.init();}}catch(_){{}} }} }});</script>
<script>const PREVIEW=(self!==top||/[?&]swarm/.test(location.search))&&!matchMedia('(prefers-reduced-motion:reduce)').matches;
addEventListener('load',()=>{{if(!PREVIEW)Moves.init();const nav=document.getElementById('nav');const onS=()=>nav.classList.toggle('solid',scrollY>innerHeight*.75);onS();addEventListener('scroll',onS,{{passive:true}});
document.querySelectorAll('#bp input').forEach(i=>i.addEventListener('change',e=>{{const h=document.documentElement;if(e.target.name==='bf'){{if(e.target.value==='brand')delete h.dataset.font;else h.dataset.font=e.target.value;}}else{{if(e.target.value==='brand')delete h.dataset.world;else h.dataset.world=e.target.value;}}}}));document.getElementById('bpx').onclick=()=>document.getElementById('bp').remove();}});</script>
</body></html>'''
    out = os.path.join(slug_dir, 'index.html'); open(out, 'w').write(html); return out, len(html)

if __name__ == '__main__':
    print(build(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None))
