"""registry.py — the device library: what award-level pages do, measured, and written once as our own code.

A device is one thing a visitor sees happen — a headline rising out of a mask, a list held while its panels pass, cards
stacking as the page moves — with: where it was seen and what was measured there (our instrument, lib/qa/inspect.mjs;
never the model's memory), the markup it expects, its stylesheet and script, what material it needs, when to use it and
when not, and what it goes with. The code is ours: mechanics are taken, never a site's own code, pictures or words.

  DEVICES            {id: device}
  demo(ids=None)     one standalone page that shows the devices, for a human eye and for lib/qa/layout.mjs
  bundle(ids)        (css, js) for a page built from these devices — each device's code once, in a stable order
  catalogue()        the library as a builder reads it: id, what it is, needs, use/avoid, the markup contract

Every device is still and complete without JavaScript and under prefers-reduced-motion: the script only adds the class
that lets motion start. `measured` holds numbers from evidence files; a device with `measured: None` was written from
common practice and says so — it is a candidate until a harvest confirms its numbers.

Shared tokens a page provides: --ink, --paper, --accent, --ease (default cubic-bezier(.2,.7,.2,1))."""

BASE_CSS = """
:root{--ease:cubic-bezier(.2,.7,.2,1)}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
@media (prefers-reduced-motion:reduce){.dv [data-rise],.dv .dv-lines .dv-ln>span,.dv .dv-bars .b i{opacity:1!important;transform:none!important}}
"""
BASE_JS = """
const D=document,R=D.documentElement;R.classList.add('dv');
const calm=matchMedia('(prefers-reduced-motion: reduce)').matches;
const waiting=new Set(),io=new IntersectionObserver(es=>es.forEach(x=>{if(x.isIntersecting||x.boundingClientRect.bottom<0)show(x.target)}),{rootMargin:'0px 0px -8% 0px',threshold:.12});
const show=el=>{el.classList.add('is-in');io.unobserve(el);waiting.delete(el)};
const seen={observe:el=>{waiting.add(el);io.observe(el)}};
const each=(q,f)=>D.querySelectorAll(q).forEach(f);
const onScroll=f=>{let t=0;const run=()=>{t=0;f()};addEventListener('scroll',()=>{t||(t=requestAnimationFrame(run))},{passive:true});addEventListener('resize',run);run()};
const progress=el=>{const r=el.getBoundingClientRect(),h=innerHeight;return Math.min(1,Math.max(0,(h-r.top)/(r.height+h)))};
onScroll(()=>waiting.forEach(el=>{if(el.getBoundingClientRect().top<innerHeight*.9)show(el)}));   /* nothing a visitor has scrolled to stays hidden, however fast they went */
const through=el=>{const r=el.getBoundingClientRect();return Math.min(1,Math.max(0,-r.top/Math.max(1,r.height-innerHeight)))};
"""

DEVICES = {}


def device(**d):
    DEVICES[d['id']] = d
    return d


device(id='line-rise', name='Headline lines rise out of a mask', kind='text',
       sees='Each line of a headline slides up from behind an invisible edge, one after another.',
       measured={'source': 'cerebrium, load, 2026-11-10', 'travel_px': [61, 82], 'duration_ms': [167, 275], 'gap_ms': [34, 66], 'masked': True, 'lines': 7, 'harvest': 'sixteen Sites of the Month measured 2026-11-11 (bench/runs/_research/harvest/SUMMARY.md)', 'seen_in': 'masked text reveals on 9 of 16; a load choreography on 11 of 16, settling in 456–5695 ms'},
       needs='a headline of 2–4 lines', use='the first screen and the one or two largest statements of a page', avoid='body text; more than three times a page',
       pairs=['rise-stagger', 'held-index'], markup='<h1 class="dv-lines"><span class="dv-ln"><span>line one</span></span><span class="dv-ln"><span>line two</span></span></h1>',
       css=""".dv-ln{display:block;overflow:hidden;padding-bottom:.12em;margin-bottom:-.12em}.dv-ln>span{display:block}
.dv .dv-lines .dv-ln>span{transform:translateY(105%);transition:transform .275s var(--ease);transition-delay:calc(var(--n,0) * 40ms)}.dv .dv-lines.is-in .dv-ln>span{transform:none}""",
       js="each('.dv-lines',h=>{[...h.querySelectorAll('.dv-ln')].forEach((l,i)=>l.style.setProperty('--n',i));seen.observe(h)});")

device(id='rise-stagger', name='Things arrive in order', kind='reveal',
       sees='A paragraph, then the buttons, then a note fade in and settle a few pixels upward, a beat apart.',
       measured={'source': 'cerebrium, scroll, 2026-11-10', 'fade_ms': [267, 350], 'travel_px': [9, 12], 'gap_ms': [67, 101], 'elements': 24, 'harvest': 'sixteen Sites of the Month measured 2026-11-11 (bench/runs/_research/harvest/SUMMARY.md)', 'seen_in': '16 of 16 fade, 13 of 16 travel, 10 of 16 staggered', 'fade_ms_median_by_site': [107, 635], 'travel_px_median_by_site': [8, 64], 'gap_ms_median_by_site': [34, 149]},
       needs='2–6 sibling elements', use='supporting text and actions beside a headline; rows of a list', avoid='whole sections at once; anything the visitor must read immediately on a phone',
       pairs=['line-rise'], markup='<p data-rise style="--i:0">…</p><div data-rise style="--i:1">…</div>',
       css=""".dv [data-rise]{opacity:0;transform:translateY(12px);transition:opacity .3s ease,transform .3s var(--ease);transition-delay:calc(var(--i,0) * 70ms)}.dv [data-rise].is-in{opacity:1;transform:none}""",
       js="each('[data-rise]',el=>seen.observe(el));")

device(id='held-index', name='A list held while its panels pass', kind='scroll',
       sees='Short claims stand still on the left; on the right a panel for each scrolls by, and the claim it belongs to lights up.',
       measured={'source': 'cerebrium, scroll, 2026-11-10', 'held_screens': 3.2, 'items': 4, 'name_px': 43.9, 'name_tracking_em': -0.05, 'name_weight': 300, 'harvest': 'sixteen Sites of the Month measured 2026-11-11 (bench/runs/_research/harvest/SUMMARY.md)', 'seen_in': '11 of 16 hold something while scrolling', 'longest_hold_screens': [0.5, 13]},
       needs='3–5 claims, each with a picture of the product or a set of true figures', use='the centre of a product page: what it does, shown', avoid='fewer than three items; items without anything to show',
       pairs=['line-rise', 'rise-stagger', 'figure-bars'],
       markup='<div class="dv-held"><div class="dv-held-side"><ol class="dv-held-names"><li>Claim</li>…</ol></div><div class="dv-held-items"><article class="dv-held-item"><p class="dv-held-m">Claim</p>…panel…</article>…</div></div>',
       css=""".dv-held{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:clamp(24px,4vw,64px);align-items:start}.dv-held-side{position:sticky;top:clamp(96px,14vh,150px)}
.dv-held-names{list-style:none;padding:0;margin:0}.dv-held-names li{font-weight:300;font-size:clamp(28px,3.05vw,46px);line-height:1.14;letter-spacing:-.035em;color:color-mix(in srgb,var(--ink) 24%,var(--paper));transition:color .35s var(--ease)}.dv-held-names li.is-on{color:var(--ink)}
.dv-held-item{padding-bottom:clamp(64px,9vw,144px)}.dv-held-item:last-child{padding-bottom:0}.dv-held-m{display:none}
@media (max-width:900px){.dv-held{grid-template-columns:minmax(0,1fr)}.dv-held-side{position:static}.dv-held-names{display:none}.dv-held-m{display:block;font-weight:300;font-size:clamp(30px,8vw,44px);line-height:1.1;letter-spacing:-.035em;margin:0 0 18px}}""",
       js="""each('.dv-held',h=>{const n=[...h.querySelectorAll('.dv-held-names li')],it=[...h.querySelectorAll('.dv-held-item')];if(!n.length)return;n[0].classList.add('is-on');
const pick=new IntersectionObserver(es=>es.forEach(x=>{if(x.isIntersecting){const i=it.indexOf(x.target);n.forEach((m,k)=>m.classList.toggle('is-on',k===i))}}),{rootMargin:'-42% 0px -42% 0px'});it.forEach(i=>pick.observe(i))});""")

device(id='fact-ticker', name='A slow line of facts', kind='text',
       sees='One row of short facts in small capitals drifts sideways without end.',
       measured={'source': 'cerebrium (logo row), 2026-11-10', 'note': 'presence and placement under the first screen; speed not measured'},
       needs='4–8 true facts under 40 characters each (or logos the client really has)', use='directly under the first screen, once', avoid='sentences; anything that must be read',
       pairs=['line-rise'], markup='<div class="dv-tick"><ul><li>fact</li>…</ul></div>',
       css=""".dv-tick{overflow:hidden}.dv-tick ul{display:flex;gap:clamp(32px,5vw,88px);width:max-content;list-style:none;padding:0;margin:0}.dv-tick li{white-space:nowrap}
.dv .dv-tick ul{animation:dv-tick 46s linear infinite}@keyframes dv-tick{to{transform:translateX(-50%)}}""",
       js="each('.dv-tick ul',u=>{if(!calm&&!u.dataset.x){u.dataset.x=1;[...u.children].forEach(c=>{const k=c.cloneNode(true);k.setAttribute('aria-hidden','true');u.appendChild(k)})}});")

device(id='side-rail', name='A row that moves sideways as the page moves down', kind='scroll',
       sees='While you scroll through a section, a row of large words or cards slides across the screen.',
       measured={'source': 'butter, scroll, 2026-11-10', 'per_px_scrolled': [-0.28, -0.47], 'screens_wide': 0.5, 'elements_with_scroll': 19, 'harvest': 'sixteen Sites of the Month measured 2026-11-11 (bench/runs/_research/harvest/SUMMARY.md)', 'seen_in': '7 of 16'},
       needs='a short phrase set very large, or 4–8 cards', use='one change of pace in the middle of a page', avoid='twice on a page; with long text',
       pairs=['rise-stagger'], markup='<div class="dv-rail" style="--rate:.4"><div class="dv-rail-row">…large words or cards…</div></div>',
       css=""".dv-rail{overflow:hidden}.dv-rail-row{display:flex;gap:clamp(20px,3vw,56px);width:max-content;will-change:transform}
@media (prefers-reduced-motion:reduce){.dv-rail{overflow-x:auto}.dv-rail-row{transform:none!important}}""",
       js="if(!calm)onScroll(()=>each('.dv-rail',r=>{const row=r.firstElementChild,rate=parseFloat(getComputedStyle(r).getPropertyValue('--rate'))||.38,max=Math.max(0,row.scrollWidth-r.clientWidth);row.style.transform=`translate3d(${-Math.min(max,progress(r)*(r.offsetHeight+innerHeight)*rate)}px,0,0)`}));")

device(id='stack-cards', name='Cards that stack as you scroll', kind='scroll',
       sees='Each card stops under the last one a little lower, so they pile up; the ones beneath shrink slightly.',
       measured=None, seen='named by the Awwwards jury on a Site of the Day ("Cards stack on scroll"); numbers not yet measured',
       needs='3–6 cards of similar height, each a complete thought', use='steps, plans, case studies', avoid='cards taller than the screen; on a phone with long cards',
       pairs=['rise-stagger'], markup='<div class="dv-stack"><article class="dv-card">…</article>…</div>',
       css=""".dv-stack{display:grid;gap:clamp(16px,2vw,28px)}.dv-card{position:sticky;top:calc(clamp(84px,12vh,128px) + var(--k,0) * 14px);transform-origin:50% 0;will-change:transform}
@media (max-width:700px),(prefers-reduced-motion:reduce){.dv-card{position:static;transform:none!important}}""",
       js="""each('.dv-stack',s=>[...s.children].forEach((c,k)=>c.style.setProperty('--k',k)));
if(!calm)onScroll(()=>each('.dv-stack',s=>{const cs=[...s.children];cs.forEach((c,k)=>{const nx=cs[k+1];if(!nx)return;const top=parseFloat(getComputedStyle(c).top)||0,gap=nx.getBoundingClientRect().top-top;const t=Math.min(1,Math.max(0,1-gap/c.offsetHeight));c.style.transform=`scale(${1-t*.045})`})}));""")

device(id='grow-to-bleed', name='A picture that grows to the full width', kind='media',
       sees='A framed picture sits inset with rounded corners; as it comes up the screen it widens until it touches both edges.',
       measured={'source': 'harvest 2026-11-11: an element changes size with scroll on 12 of 16 sites (1–97 elements a site)', 'note': 'how far and over what distance was not extracted; our 72% → 100% over half a screen is our own choice'},
       needs='one strong, wide picture or video at least 1600 px wide', use='the one picture the page is about', avoid='screenshots with small text; more than once',
       pairs=['line-rise'], markup='<figure class="dv-grow"><img …></figure>',
       css=""".dv-grow{margin:0 auto;width:calc(72% + var(--g,0) * 28%);border-radius:calc((1 - var(--g,0)) * 18px);overflow:hidden}.dv-grow img,.dv-grow video{display:block;width:100%;height:auto}
@media (max-width:700px),(prefers-reduced-motion:reduce){.dv-grow{width:100%;border-radius:0}}""",
       js="if(!calm)onScroll(()=>each('.dv-grow',f=>f.style.setProperty('--g',Math.min(1,progress(f)*2.1).toFixed(3))));")

device(id='magnet', name='A button that leans toward the pointer', kind='pointer',
       sees='The main button drifts a few pixels toward the cursor when it comes near, and settles back when it leaves.',
       measured=None, seen='common on agency sites; numbers not yet measured',
       needs='one primary action', use='the one action that matters, at most twice a page', avoid='touch screens (it does nothing there); rows of several buttons',
       pairs=[], markup='<a class="btn dv-magnet" href="…">Action</a>',
       css=".dv-magnet{transition:transform .35s var(--ease)}",
       js="if(!calm&&matchMedia('(hover:hover)').matches)each('.dv-magnet',b=>{b.addEventListener('pointermove',e=>{const r=b.getBoundingClientRect();b.style.transform=`translate(${((e.clientX-r.left)/r.width-.5)*12}px,${((e.clientY-r.top)/r.height-.5)*10}px)`});b.addEventListener('pointerleave',()=>b.style.transform='')});")

device(id='scramble', name='A label that resolves from noise', kind='text',
       sees='A small mono label flickers through random letters for a moment and lands on its word.',
       measured={'source': 'cerebrium, 2026-11-10', 'note': 'four elements of this kind on the page; timing not measured'},
       needs='labels of one to three words in a mono face', use='section labels, two to five on a page', avoid='headlines, sentences, anything over 24 characters',
       pairs=['held-index'], markup='<span class="dv-scramble">LABEL</span>',
       css=".dv-scramble{font-variant-numeric:tabular-nums}",
       js="""if(!calm)each('.dv-scramble',el=>{const word=el.textContent,pool='ABCDEFGHJKLMNPRSTUVXYZ0123456789';el.setAttribute('aria-label',word);
new IntersectionObserver((es,o)=>es.forEach(x=>{if(!x.isIntersecting)return;o.disconnect();let f=0;const n=word.length,t=setInterval(()=>{f++;el.textContent=[...word].map((c,i)=>c===' '||i<f/2?c:pool[(Math.random()*pool.length)|0]).join('');if(f>=n*2){clearInterval(t);el.textContent=word}},28)}),{threshold:.6}).observe(el)});""")

device(id='figure-bars', name='Figures drawn as bars that fill', kind='data',
       sees='A few true numbers stand in a panel, each with a bar that grows to its length when it comes into view.',
       measured={'source': 'cerebrium (latency panel), 2026-11-10', 'note': 'panel geometry: 10 px corners, mono labels 13 px; fill timing not measured'},
       needs='2–5 real figures that can be compared, each with its share of the longest', use='inside a product panel in place of a screenshot the client does not have', avoid='figures that are not comparable; invented scales',
       pairs=['held-index'], markup='<ul class="dv-bars"><li><span class="k">label</span><span class="b"><i style="--w:.62"></i></span><span class="v">42 s</span></li>…</ul>',
       css=""".dv-bars{list-style:none;padding:0;margin:0;display:grid;gap:10px}.dv-bars li{display:grid;grid-template-columns:minmax(0,9rem) minmax(0,1fr) auto;gap:14px;align-items:center}
.dv-bars .b{height:26px;border-radius:5px;background:color-mix(in srgb,var(--ink) 8%,transparent);overflow:hidden}.dv-bars .b i{display:block;height:100%;width:calc(var(--w) * 100%);border-radius:5px;background:var(--accent);transform-origin:left;transition:transform .9s var(--ease)}
.dv .dv-bars .b i{transform:scaleX(0)}.dv .dv-bars.is-in .b i{transform:none}@media (max-width:600px){.dv-bars li{grid-template-columns:minmax(0,6.5rem) minmax(0,1fr) auto}}""",
       js="each('.dv-bars',b=>seen.observe(b));")

device(id='end-mark', name='The name set across the whole footer', kind='text',
       sees='At the very end the brand name fills the width of the screen, cut off slightly by the bottom edge.',
       measured=None, seen='on several of the twelve measured references as a closing wordmark; one option among closings, not a default',
       needs='a brand name of 3–14 characters', use='a page that ends quietly and wants one last gesture', avoid='long names; pages that already close on a large line',
       pairs=[], markup='<div class="dv-endmark" style="--chars:9" aria-hidden="true">Brand name</div>',
       css=".dv-endmark{font-weight:500;line-height:.8;letter-spacing:-.04em;white-space:nowrap;text-align:center;overflow:hidden;font-size:calc(165vw / var(--chars,10));margin-bottom:-.12em}",
       js="")

device(id='peek', name='A picture that follows the pointer over a list', kind='pointer',
       sees='Moving over the rows of a list, a small picture for the row under the cursor appears beside it and follows.',
       measured=None, seen='common on agency and editorial indexes; numbers not yet measured',
       needs='a list of 4–10 rows, each with its own picture', use='work, case studies, a menu of dishes with photographs', avoid='touch screens (rows fall back to plain links); rows without pictures',
       pairs=['rise-stagger'], markup='<ul class="dv-peek"><li><a href="…" data-peek="img:ID or url">Row</a></li>…</ul>',
       css=".dv-peek-img{position:fixed;left:0;top:0;width:clamp(180px,22vw,340px);aspect-ratio:4/3;object-fit:cover;border-radius:10px;pointer-events:none;opacity:0;transform:translate(-50%,-50%) scale(.92);transition:opacity .2s ease,transform .3s var(--ease);z-index:30}.dv-peek-img.is-on{opacity:1;transform:translate(-50%,-50%) scale(1)}",
       js="""if(!calm&&matchMedia('(hover:hover)').matches)each('.dv-peek',l=>{const im=D.createElement('img');im.className='dv-peek-img';im.alt='';D.body.appendChild(im);
l.addEventListener('pointermove',e=>{im.style.left=e.clientX+24+'px';im.style.top=e.clientY+'px'});
l.querySelectorAll('[data-peek]').forEach(a=>{a.addEventListener('pointerenter',()=>{im.src=a.dataset.peek;im.classList.add('is-on')});a.addEventListener('pointerleave',()=>im.classList.remove('is-on'))})});""")


device(id='depth', name='Layers that move at different speeds', kind='scroll',
       sees='A picture drifts a little slower or faster than the page, so it seems to sit behind or in front of the text.',
       measured={'source': 'harvest 2026-11-11', 'seen_in': '9 of 16', 'rate_median_by_site': [-0.47, 0.68], 'typical': [-0.14, 0.47], 'elements': [1, 65]},
       needs='a picture or a large shape with room to move inside its frame', use='two or three pictures on a page, each in a frame that crops it', avoid='text blocks; screenshots that must be read; phones',
       pairs=['grow-to-bleed', 'rise-stagger'], markup='<figure class="dv-depth" style="--rate:-.14"><img …></figure>',
       css=""".dv-depth{overflow:hidden}.dv-depth>*{display:block;width:100%;height:auto;will-change:transform;transform:translate3d(0,calc(var(--y,0) * 1px),0) scale(1.16)}
@media (max-width:700px),(prefers-reduced-motion:reduce){.dv-depth>*{transform:none!important}}""",
       js="if(!calm)onScroll(()=>each('.dv-depth',f=>{const r=f.getBoundingClientRect(),rate=parseFloat(getComputedStyle(f).getPropertyValue('--rate'))||-.14;f.style.setProperty('--y',((r.top+r.height/2-innerHeight/2)*rate).toFixed(1))}));")

device(id='eased-scroll', name='A page that glides to a stop', kind='scroll',
       sees='After each turn of the wheel the page keeps moving for a moment and settles, instead of stopping dead.',
       measured={'source': 'harvest 2026-11-11', 'seen_in': '12 of 16 (the page moves on 366–1158 ms after input, median per site; an unsmoothed page measures 0)', 'settle_ms_median_by_site': [366, 1158]},
       needs='nothing', use='long pages with held scenes and depth, on a desk', avoid='touch screens (never), pages with forms or long reading; it is off under reduced motion and whenever a key or the scrollbar is used',
       pairs=['held-index', 'depth', 'side-rail'], markup='<html data-eased-scroll>',
       css="html[data-eased-scroll].dv-easing{scroll-behavior:auto}",
       js="""if(!calm&&matchMedia('(hover:hover) and (pointer:fine)').matches&&R.hasAttribute('data-eased-scroll')){let to=scrollY,now=scrollY,run=0;R.classList.add('dv-easing');
const step=()=>{now+=(to-now)*.12;if(Math.abs(to-now)<.5){now=to;run=0;scrollTo(0,now);return}scrollTo(0,now);run=requestAnimationFrame(step)};
addEventListener('wheel',e=>{if(e.ctrlKey||e.defaultPrevented||e.target.closest('[data-native-scroll],textarea,select'))return;e.preventDefault();if(!run){to=now=scrollY}to=Math.max(0,Math.min(R.scrollHeight-innerHeight,to+e.deltaY*(e.deltaMode?32:1)));run||(run=requestAnimationFrame(step))},{passive:false});
addEventListener('scroll',()=>{if(!run){to=now=scrollY}},{passive:true})}""")

# What the measured pages have in common as whole pages — the builder's ground rules, each with its evidence.
RULES = {
    'source': 'sixteen Sites of the Month measured 2026-11-11 with lib/qa/inspect.mjs at 1440; ranges are across sites; bench/runs/_research/harvest/SUMMARY.md',
    'display_px': {'range': [57, 194], 'typical': [110, 180], 'note': 'the largest type on the page; 11 of 16 set it at 80 px or more'},
    'display_leading': {'range': [0.8, 1.2], 'typical': [0.8, 0.95]}, 'display_tracking_em': {'range': [-0.064, 0.32], 'typical': [-0.06, -0.02]},
    'text_px': {'range': [10, 20.2], 'typical': [12, 16], 'note': 'the size most of the text is set in — small against a very large display'},
    'families': {'range': [1, 5], 'typical': [1, 2]}, 'grounds': {'range': [1, 4], 'typical': [1, 3], 'note': 'few changes of ground; nine of sixteen use one or two'},
    'page_screens': {'range': [3, 90.5], 'typical': [15, 28], 'note': 'long pages: scenes held and scrubbed, not stacked blocks'},
    'motion': {'reveal_on_scroll': '16 of 16', 'eased_scroll': '12 of 16', 'something_held': '11 of 16', 'size_with_scroll': '12 of 16', 'parallax': '9 of 16', 'sideways': '7 of 16', 'load_choreography': '11 of 16', 'custom_cursor': '0 of 16'},
    'material': {'video': '9 of 16', 'canvas': '13 of 16', 'pictures_that_bleed': '9 of 16', 'note': 'most of these pages rest on film or rendered scenes made for them — a page without such material leans on type and held scenes'},
}


def bundle(ids):
    """The stylesheet and the script of a page that uses these devices."""
    use = [DEVICES[i] for i in DEVICES if i in set(ids)]
    return BASE_CSS + '\n'.join(d['css'] for d in use), BASE_JS + '\n'.join(d['js'] for d in use if d.get('js'))


def catalogue():
    """The library as a builder reads it — everything but the code, which it gets by naming the device."""
    return [{k: d.get(k) for k in ('id', 'name', 'kind', 'sees', 'needs', 'use', 'avoid', 'pairs', 'markup')} | {'measured': bool(d.get('measured') and d['measured'].get('source'))} for d in DEVICES.values()]


def demo(ids=None):
    """One page with every device in use, on plain content — to be looked at and to be measured."""
    ids = list(ids or DEVICES); css, js = bundle(ids)
    pic = lambda w, h, c: f"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {w} {h}'><rect width='{w}' height='{h}' fill='%23{c}'/><circle cx='{w * .7:.0f}' cy='{h * .4:.0f}' r='{h * .3:.0f}' fill='%23ffffff' fill-opacity='.25'/></svg>"
    blocks = {
        'line-rise': '<h1 class="dv-lines big"><span class="dv-ln"><span>Every device</span></span><span class="dv-ln"><span>measured once,</span></span><span class="dv-ln"><span>written once</span></span></h1>',
        'rise-stagger': '<p data-rise style="--i:0" class="lede">A paragraph arrives first, in three hundred milliseconds.</p><p data-rise style="--i:1"><a class="btn dv-magnet" href="#end">The action follows</a></p><p data-rise style="--i:2" class="mono">Then the note</p>',
        'fact-ticker': '<div class="dv-tick mono"><ul><li>Twelve references measured</li><li>Five widths checked</li><li>No word invented</li><li>Reduced motion honoured</li><li>Own code only</li></ul></div>',
        'held-index': '<div class="dv-held"><div class="dv-held-side"><p class="mono"><span class="dv-scramble">WHAT IT DOES</span></p><ol class="dv-held-names"><li>First claim</li><li>Second claim</li><li>Third claim</li></ol></div><div class="dv-held-items">'
                      + ''.join(f'<article class="dv-held-item"><p class="dv-held-m">{n} claim</p><div class="panel"><ul class="dv-bars mono"><li><span class="k">One</span><span class="b"><i style="--w:.9"></i></span><span class="v">90</span></li><li><span class="k">Two</span><span class="b"><i style="--w:.55"></i></span><span class="v">55</span></li><li><span class="k">Three</span><span class="b"><i style="--w:.3"></i></span><span class="v">30</span></li></ul></div><p class="lede">What this claim means, in a sentence a visitor can check against the panel.</p></article>' for n in ('First', 'Second', 'Third')) + '</div></div>',
        'side-rail': '<div class="dv-rail" style="--rate:.4"><div class="dv-rail-row huge"><span>One change of pace</span><span>in the middle</span><span>of a page</span><span>and no more</span></div></div>',
        'stack-cards': '<div class="dv-stack">' + ''.join(f'<article class="dv-card card"><p class="mono">0{k}</p><h2>Step {k}</h2><p>Each card is a complete thought and they are all about as tall.</p></article>' for k in (1, 2, 3, 4)) + '</div>',
        'grow-to-bleed': f'<figure class="dv-grow"><img src="{pic(1600, 800, "3a6ff2")}" alt="" width="1600" height="800"></figure>',
        'depth': f'<figure class="dv-depth" style="--rate:-.14;margin:0;aspect-ratio:21/9;border-radius:15px"><img src="{pic(1600, 900, "2aa66b")}" alt="" width="1600" height="900"></figure>',
        'peek': '<ul class="dv-peek list">' + ''.join(f'<li><a href="#end" data-peek="{pic(800, 600, c)}">{t}</a></li>' for t, c in (('First piece of work', 'e85d3a'), ('Second piece of work', '2aa66b'), ('Third piece of work', '7a4de0'), ('Fourth piece of work', '222222'))) + '</ul>',
        'end-mark': '<div class="dv-endmark" style="--chars:7" aria-hidden="true">Library</div>'}
    order = ['line-rise', 'rise-stagger', 'fact-ticker', 'held-index', 'side-rail', 'stack-cards', 'grow-to-bleed', 'depth', 'peek', 'end-mark']
    body = ''.join(f'<section id="{i}"><p class="mono tag">{i}</p>{blocks[i]}</section>' for i in order if i in ids and i in blocks)
    page_css = """*{box-sizing:border-box}body{margin:0;--ink:#101421;--paper:#fff;--accent:#ff488b;font:18px/1.5 'Geist',system-ui,sans-serif;color:var(--ink);background:var(--paper)}
section{padding:clamp(56px,9vw,140px) clamp(20px,2.8vw,40px)}.big{font-weight:300;font-size:clamp(44px,6vw,104px);line-height:1;letter-spacing:-.03em;margin:0}.huge span{font-weight:300;font-size:clamp(56px,11vw,180px);letter-spacing:-.04em;white-space:nowrap}
.mono{font-family:'Geist Mono',ui-monospace,monospace;font-size:13px;letter-spacing:.04em;text-transform:uppercase}.tag{opacity:.5;margin:0 0 24px}.lede{max-width:44ch}
.btn{display:inline-flex;align-items:center;min-height:54px;padding:0 22px;border-radius:7px;background:var(--accent);color:#101421;text-decoration:none}
.panel{background:#eef2f5;border-radius:10px;padding:clamp(28px,4vw,56px)}.card{background:#eef2f5;border-radius:15px;padding:clamp(24px,3vw,48px);min-height:300px;box-shadow:0 -1px 0 #fff}.card h2{font-weight:300;font-size:clamp(28px,3vw,44px);margin:8px 0}
.list{list-style:none;padding:0;margin:0}.list a{display:block;padding:18px 0;border-bottom:1px solid #d9dee6;font-size:clamp(22px,2.4vw,34px);color:inherit;text-decoration:none}"""
    return ('<!doctype html><html lang="en" data-eased-scroll><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Device library</title>'
            '<link href="https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500&family=Geist+Mono:wght@400;500&display=swap" rel="stylesheet">'
            f'<style>{page_css}{css}</style></head><body><main>{body}</main><div id="end"></div><script>{js}</script></body></html>')


if __name__ == '__main__':
    import json, sys
    if len(sys.argv) > 1 and sys.argv[1] == 'demo':
        open(sys.argv[2], 'w', encoding='utf-8').write(demo()); print(sys.argv[2])
    else: print(json.dumps(catalogue(), indent=1))
