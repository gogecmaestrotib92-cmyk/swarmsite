"""Builds lib/motion/kitchen-sink.html — every move and artefact on one page, C1 dark tokens, Lenis on.
python3 lib/motion/kitchen-sink.py"""
import os, subprocess, json, base64
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
tok = subprocess.run(['python3', '-I', os.path.join(ROOT, 'lib/css/tokens.py'), 'C1', 'dark', '#10B981', 'Barlow Condensed'], capture_output=True, text=True).stdout
tok = '\n'.join(l for l in tok.splitlines() if not l.startswith('/*'))
comp = open(os.path.join(ROOT, 'lib/css/components.css')).read()
moves = open(os.path.join(ROOT, 'lib/motion/moves.js')).read()
arts = open(os.path.join(ROOT, 'lib/artefacts/artefacts.js')).read()
imgs = {i['id']: i['data'] for i in json.load(open(os.path.join(ROOT, 'lib/audit/sportbot_images.json')))}
ladder = json.dumps([{"name": "1xBet", "v": 1.98}, {"name": "Betfair", "v": 1.97}, {"name": "DraftKings", "v": 1.95}, {"name": "Pinnacle", "v": 1.93}, {"name": "bet365", "v": 1.91}, {"name": "Unibet (FR)", "v": 1.70}])
curve = json.dumps([0, .8, .3, 1.4, 2.1, 1.6, 2.9, 3.4, 2.8, 4.1, 5.0, 4.4, 5.9, 6.3, 7.8, 7.1, 8.6, 9.9, 9.2, 10.8, 11.5, 12.2, 11.7, 13.46])

def sec(n, name, body, extra=''):
    return f'<section class="sec ks" id="{name}" {extra}><div class="wrap"><span class="label"><span class="sq"></span>{n:02d} — {name}</span>{body}</div></section>'

body = '\n'.join([
f'''<nav class="nav" data-nav><div class="wrap"><a class="wordmark" href="#">Moves<em>v2</em></a><div class="links"><a href="#masked-line-reveal">Text</a><a href="#pinned-steps">Pin</a><a href="#clip-reveal">Image</a><a href="#price-ladder">Artefacts</a></div><a class="btn primary arrow" href="#">Hover me</a></div></nav>
<section class="hero" data-move="hero-intro" style="min-height:100svh;display:grid;align-content:center"><div class="wrap"><div><div class="cat"><span class="label"><span class="sq"></span>Kitchen sink · 21 moves · 4 artefacts</span></div><h1 class="display h1">Every move, tuned once, used everywhere.</h1><p class="lede">Scroll slowly. Lenis smooths the wheel, GSAP drives the reveals, nothing bounces. Hover the buttons and the links.</p><div class="ctas"><a class="btn primary arrow" href="#masked-line-reveal">Start the tour</a><a class="link arrow" href="#">A link that draws</a></div></div><div class="artefact frame marks" style="padding:24px"><i class="m"></i><div class="card dark"><div class="top"><span class="label">hero-intro</span><span class="label">on load</span></div><div class="row"><span>label → h1 lines → lede → buttons → artefact</span><b class="num">1.4s</b></div><div class="verdict">One choreography, expo.out, staggered.<strong>Nothing after 1.6s</strong></div></div></div></div></section>''',
sec(1, 'masked-line-reveal', '<h2 class="display h2" data-move="masked-line-reveal" style="margin-top:16px;max-width:18ch">Lines rise inside a clipped box and settle flat.</h2>'),
sec(2, 'word-blur-in', '<p class="big-body" data-move="word-blur-in" style="margin-top:16px">Each word sharpens from a blur, forty-five milliseconds apart, so a paragraph reads itself in.</p>'),
sec(3, 'letter-reveal', '<h2 class="display h2" data-move="letter-reveal" style="margin-top:16px">SKEW STRAIGHTENS</h2>'),
sec(4, 'highlight-swipe', '<p class="big-body" data-move="highlight-swipe" style="margin-top:16px">The highlighter grows behind <mark>the one phrase that matters</mark> and stops.</p>'),
sec(5, 'text-scrub', '<p class="big-body" data-move="text-scrub" style="margin-top:16px;max-width:40ch">Words colour in with the scroll, tied to the wheel, so reading speed is the scroll speed. The same selection is not paid the same everywhere. We line the books up and mark the best one.</p>'),
sec(6, 'number-scramble', '<div class="cells" style="--cols:3;margin-top:16px" data-move="stagger-in"><div><span class="label">ROI</span><b class="num" data-move="number-scramble">+3.3%</b><span class="label">640 closes</span></div><div><span class="label">Units</span><b class="num" data-move="number-scramble">+13.46u</b><span class="label">664 settled</span></div><div><span class="label">Analyses</span><b class="num" data-move="number-scramble">28,139</b><span class="label">and counting</span></div></div>'),
sec(7, 'pinned-steps', '<div class="pinned" data-move="pinned-steps" style="margin-top:24px"><div class="steps"><div data-step>Go deep on one match.</div><div data-step>Have the whole slate scanned.</div><div data-step>Check a bet you already like.</div></div><div class="panels"><div data-panel class="frame marks" style="padding:20px"><i class="m"></i><div class="card dark"><div class="top"><span class="label">Panel 01</span></div><div class="row"><span>Fritz to win</span><b class="num">3.80</b></div></div></div><div data-panel class="frame marks" style="padding:20px"><i class="m"></i><div class="card dark"><div class="top"><span class="label">Panel 02</span></div><div class="row"><span>Under 2.5</span><b class="num">+12.6%</b></div></div></div><div data-panel class="frame marks" style="padding:20px"><i class="m"></i><div class="card dark"><div class="top"><span class="label">Panel 03</span></div><div class="row best"><span>1xBet</span><b class="num">1.98</b></div></div></div></div></div>', 'style="align-content:start"'),
sec(8, 'clip-reveal', f'<div data-move="clip-reveal" style="margin-top:16px;aspect-ratio:2.36;max-height:60vh"><img src="{imgs["stadium-bowl"]}" alt="" style="width:100%;height:100%;object-fit:cover"></div>'),
f'<div class="band dark" data-move="parallax" data-parallax="10"><img src="{imgs["roof-gantry"]}" alt=""><div class="wrap"><div><span class="label">09 — parallax</span><div class="giant-n" data-move="number-scramble">34</div></div><span class="label">image drifts slower than the page</span></div></div>',
sec(10, 'pinned-zoom', f'<div data-move="pinned-zoom" data-zoom="1.6" data-origin="50% 35%" style="margin-top:16px;overflow:hidden;height:70vh"><img src="{imgs["stadium-bowl"]}" alt="" style="width:100%;height:100%;object-fit:cover;filter:grayscale(1) brightness(1.3)"></div>', 'style="align-content:start"'),
sec(11, 'card-deck-peel', '<div data-move="card-deck-peel" style="margin-top:24px;min-height:60vh"><div class="frame marks" style="padding:32px;background:var(--panel)"><i class="m"></i><h3 class="h2 display">Card one peels away.</h3></div><div class="frame marks" style="padding:32px;background:var(--panel)"><i class="m"></i><h3 class="h2 display">Card two follows.</h3></div><div class="frame marks" style="padding:32px;background:var(--panel)"><i class="m"></i><h3 class="h2 display">Card three stays.</h3></div></div>', 'style="align-content:start"'),
sec(12, 'draw-on-scroll', '<svg data-move="draw-on-scroll" viewBox="0 0 600 200" style="width:100%;max-width:720px;margin-top:16px;overflow:visible" fill="none" stroke="var(--accent)" stroke-width="2"><path d="M10 150 C120 20, 220 220, 320 90 S 520 40, 590 120"/><circle cx="320" cy="90" r="8"/><line x1="10" y1="180" x2="590" y2="180" stroke="var(--line)"/></svg>'),
'<div class="marquee" data-move="marquee" data-duration="30" style="border-top:1px solid var(--line);border-bottom:1px solid var(--line)"><div class="leagues"><span>13 — marquee</span><span>·</span><span>slows on hover</span><span>·</span><span>Premier League</span><span>·</span><span>NBA</span><span>·</span><span>NFL</span><span>·</span></div></div>',
f'<section class="sec" id="mask-switch" style="padding:0;min-height:80vh;background:var(--accent);color:var(--accent-contrast)" data-move="mask-switch"><div class="wrap" style="padding:80px 0"><span class="label" style="color:inherit"><span class="sq"></span>14 — mask-switch</span><h2 class="display h2">The next world opens through a circle.</h2></div></section>',
sec(15, 'rotating-headline', '<h2 class="display h2" style="margin-top:16px">Same bet. <span data-move="rotating-headline" data-phrases=\'["Better price.","Better book.","Better number."]\'>Better price.</span></h2>'),
sec(16, 'stagger-in', '<ul class="rows" data-move="stagger-in" style="margin-top:16px"><li><span class="label">A</span><span class="h3">Row one</span><p>Children arrive seventy milliseconds apart.</p></li><li><span class="label">B</span><span class="h3">Row two</span><p>Same ease as everything else.</p></li><li><span class="label">C</span><span class="h3">Row three</span><p>No bounce, no overshoot.</p></li></ul>'),
sec(17, 'scale-settle', '<div class="frame marks" data-move="scale-settle" style="padding:40px;margin-top:16px;background:var(--panel)"><i class="m"></i><h3 class="display h2">Big things settle from 1.05 to 1.</h3></div>'),
sec(18, 'price-ladder', f'<div class="frame marks" style="padding:24px;margin-top:16px;max-width:720px"><i class="m"></i><div data-artefact="price-ladder" data-ladder=\'{ladder}\'></div></div>'),
sec(19, 'ledger-curve', f'<div style="height:260px;margin-top:16px;max-width:720px"><div data-artefact="ledger-curve" data-curve=\'{curve}\' data-label="+13.46u"></div></div>'),
sec(20, 'gap-meter', '<div data-artefact="gap-meter" data-gap=\'{"a":1.86,"b":1.96,"la":"Your price","lb":"Fair price","verb":"gap"}\' style="margin-top:16px;max-width:720px"></div>'),
sec(21, 'live-counter', '<b class="num" style="font-size:clamp(56px,8vw,120px)" data-artefact="live-counter" data-counter="28139" data-rate="0.9"></b><p class="label">grows while you watch · 0.9 / min</p>'),
'<footer class="ending"><div class="wrap"><div class="giant outline" data-move="giant-scrub" aria-hidden="true">Moves</div><div class="next"><span>22 — giant-scrub: the wordmark slides up and tightens</span><span>end</span></div></div></footer>',
])

html = f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Moves v2 — kitchen sink</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800&family=Instrument+Sans:wght@400..700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>{tok}
{comp}
.ks{{min-height:70svh;align-content:center}}.ks .label{{display:block}}
html,body{{overflow-x:hidden}}.marquee{{overflow:hidden}}.leagues{{display:flex;white-space:nowrap;width:max-content}}.leagues span{{padding:0 8px}}
.hero .cat{{margin-bottom:22px}}
@media(max-width:700px){{.ks{{min-height:0;padding:56px 0}}.hero .wrap{{gap:28px}}.hero .h1{{font-size:clamp(44px,13vw,64px)}}.big-body{{font-size:20px}}.band .giant-n{{font-size:88px}}.ending .giant{{font-size:19vw}}[data-move~="card-deck-peel"]{{min-height:0!important}}[data-move~="pinned-zoom"]{{height:48vh!important}}}}.hero .lede{{margin-top:24px;max-width:46ch}}.hero .ctas{{margin-top:28px;display:flex;gap:18px;align-items:center;flex-wrap:wrap}}
</style></head><body class="tx-grid tx-grain">
{body}
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
<script src="https://unpkg.com/lenis@1.1.18/dist/lenis.min.js"></script>
<script>{moves}</script>
<script>{arts}</script>
<script>addEventListener('load',()=>{{Moves.init();Artefacts.init();}});</script>
</body></html>'''
out = os.path.join(ROOT, 'lib/motion/kitchen-sink.html'); open(out, 'w').write(html); print(out, len(html))
