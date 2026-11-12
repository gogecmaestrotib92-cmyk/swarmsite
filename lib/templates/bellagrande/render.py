"""bellagrande — a template for places, rebuilt from the measured build of hotelbellagrande.com (home page, plus the
room card of its rooms page and the ruled list of its menu panel). render(d) -> one self-contained page. Pure: no
file reads, no client, no model call. See NOTES.md for every measure and every departure."""
import re
from html import escape as E

P = '../../'  # out/<client>.html reaches media as ../../media/...

WORDS = {  # accessible names only (never shown): the reference shows "Menu"/"Close", words the data does not have
    'es': ('Abrir el menú', 'Cerrar el menú', 'Menú', 'Contacto', 'Ir al contenido'),
    'en': ('Open menu', 'Close menu', 'Menu', 'Contact', 'Skip to content'),
}


def _rgb(h):
    h = h.lstrip('#')
    if len(h) == 3: h = ''.join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _hex(c): return '#%02x%02x%02x' % tuple(max(0, min(255, round(v))) for v in c)


def _lum(c):
    f = lambda v: v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4
    r, g, b = (f(v / 255) for v in c)
    return .2126 * r + .7152 * g + .0722 * b


def _cr(a, b):
    la, lb = _lum(a), _lum(b)
    return (max(la, lb) + .05) / (min(la, lb) + .05)


def _mix(a, b, t): return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def _quiet(ink, ground, want=4.6, most=.45):
    """ink taken toward the ground as far as the reference does (55 % ink) while it still reads at 4.6:1"""
    t = most
    while t > 0 and _cr(_mix(ink, ground, t), ground) < want: t -= .03
    return _mix(ink, ground, max(t, 0))


def _fit(p, W, H): return max(W / p['w'], H / p['h'])  # how far a picture is enlarged to cover W×H


def _two_lines(name):
    w = name.split()
    if len(w) < 2: return [name]
    best = min(range(1, len(w)), key=lambda i: max(len(' '.join(w[:i])), len(' '.join(w[i:]))))
    return [' '.join(w[:best]), ' '.join(w[best:])]


def _a(o, cls='', extra=''):
    if not o or not o.get('t'): return ''
    if not o.get('h'): return f'<span class="{cls}">{E(o["t"])}</span>'
    return f'<a class="{cls}" href="{E(o["h"])}"{extra}>{E(o["t"])}</a>'


def _btn(o, light=False):
    if not o or not o.get('t') or not o.get('h'): return ''
    return f'<a class="cta lab{" cta-l" if light else ""}" href="{E(o["h"])}"><span>{E(o["t"])}</span></a>'


def _img(p, cls='', eager=False, sizes=''):
    return (f'<img class="{cls}" src="{P}{E(p["src"])}" width="{p["w"]}" height="{p["h"]}" alt="{E(p.get("alt") or "")}"'
            f'{"" if eager else LAZY} decoding="async">')


H2 = '<h2 class="h2 dis">%s</h2>'
LAZY = ' loading="lazy"'

CSS = r"""
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--g);color:var(--i);font:400 16px/1.45 'Jost',system-ui,sans-serif;overflow-x:clip;-webkit-font-smoothing:antialiased}
img{display:block;max-width:100%;height:auto}
a{color:inherit}
h1,h2,h3,p,ul,ol,dl,dd,figure{margin:0;padding:0}
ul,ol{list-style:none}
button{font:inherit;color:inherit;background:none;border:0;padding:0;cursor:pointer}
:focus-visible{outline:2px solid currentColor;outline-offset:4px}
.skip{position:fixed;left:16px;top:-80px;z-index:90;background:var(--i);color:var(--g);padding:10px 16px}
.skip:focus{top:12px}
.dis{font-family:'Josefin Sans','Jost',sans-serif;font-weight:400;letter-spacing:.05em;text-transform:uppercase}
.lab{font:700 14px/1.4 'Josefin Sans','Jost',sans-serif;letter-spacing:.04em;text-transform:uppercase;text-decoration:none}
.tag{font-size:12px;line-height:1.4;letter-spacing:.04em;text-transform:uppercase}
.h2{font-size:clamp(36px,2.57vw + 26px,63px);line-height:1.2;text-align:center;text-wrap:balance;overflow-wrap:break-word}
.sub{font-size:clamp(18px,.86vw + 14.6px,27px);line-height:1.3}

/* header: 72 high, fixed, clear over the hero, ground + rule once the page has moved, away at the footer */
.hd{position:fixed;inset:0 0 auto 0;z-index:60;height:72px;padding:0 32px;display:grid;grid-template-columns:1fr auto 1fr;align-items:center;color:var(--i);transition:transform .2s cubic-bezier(.5,1,.89,1),opacity .2s ease,color .4s cubic-bezier(.45,0,.55,1)}
.hd::before{content:"";position:absolute;inset:0;z-index:-1;background:var(--g);border-bottom:1px solid var(--rule);opacity:1;transition:opacity .2s cubic-bezier(.45,0,.55,1)}
.js .hd{animation:hd-in .8s cubic-bezier(.25,1,.5,1) both}
@keyframes hd-in{from{transform:translateY(-100%)}to{transform:none}}
.js .hd.top::before,.js .hd.open::before{opacity:0}
.js .hd.top.on-pic:not(.open){color:var(--on)}
.js .hd.top.on-deep:not(.open){color:var(--oa)}
.js .hd.open{color:var(--oa)}
.hd.up:not(.open){transform:translateY(-100%)}
.hd-l{justify-self:start;display:flex;align-items:center;gap:24px}
.hd-r{justify-self:end}
.burger{width:44px;height:44px;margin-left:-10px;display:grid;place-items:center;position:relative}
.burger i{position:absolute;left:10px;right:10px;height:2px;background:currentColor;transition:transform .3s cubic-bezier(.45,0,.55,1)}
.burger i:first-child{transform:translateY(-4px)}.burger i:last-child{transform:translateY(4px)}
.hd.open .burger i:first-child{transform:rotate(45deg)}.hd.open .burger i:last-child{transform:rotate(-45deg)}
.no-js-hide{display:none}.js .no-js-hide{display:grid}
.mark{display:flex;align-items:center;justify-content:center;text-decoration:none;transform-origin:50% 0;transition:transform .6s cubic-bezier(.45,0,.55,1),opacity .4s cubic-bezier(.45,0,.55,1)}
.mark img{height:48px;width:auto}
.mark span{font-size:15px;line-height:1.2;text-align:center;max-width:46vw;padding-top:3px}
.js .hd.top .mark.has-img{transform:translateY(8px) scale(1.42)}
.js .hd.top:not(.open) .mark.is-name{opacity:0}
.hd .lab{padding:12px 0;display:inline-block}
.rows .cta-row,.hd.long .hd-r,.hd:not(.long) .burger.cta-only{display:none}.hd.long~.menu .rows .cta-row{display:block}

/* menu panel: the accent, list of ruled rows on the left half, a photograph on the right half */
.menu{position:fixed;inset:0;z-index:50;background:var(--a);color:var(--oa);display:flex;opacity:0;visibility:hidden;transform:translateY(-5vh);overflow:hidden auto;transition:opacity .3s cubic-bezier(.32,0,.67,0),transform .3s cubic-bezier(.32,0,.67,0),visibility 0s .3s}
.menu.open{opacity:1;visibility:visible;transform:none;transition:opacity .8s cubic-bezier(.25,1,.5,1),transform .8s cubic-bezier(.25,1,.5,1),visibility 0s}
.menu-c{flex:1 1 50%;min-width:0;padding:72px 32px 32px;display:flex;flex-direction:column;gap:38px}
.rows li{border-top:1px solid var(--rule-a)}
.rows a,.rows .row{display:flex;justify-content:space-between;align-items:baseline;gap:24px;padding:24.3px 0;font-size:23.4px;line-height:1.31;text-decoration:none;transition:opacity .2s cubic-bezier(.45,0,.55,1)}
.rows a:hover{opacity:.6}
.menu-info{margin-top:auto;display:grid;gap:0}
.menu-info a,.menu-info span{text-decoration-thickness:1px;text-underline-offset:3px;width:fit-content}
.menu-p{flex:1 1 50%;padding:72px 32px 32px}
.menu-p img{width:100%;height:100%;object-fit:cover}

/* hero: one screen, the photograph behind, the name across the foot, chevron */
.hero{position:relative;height:100vh;height:100svh;min-height:560px;display:flex;flex-direction:column;justify-content:flex-end;overflow:clip;background:var(--a);color:var(--oa)}
.hero.pic{background:#000;color:var(--on)}
.bg{position:absolute;inset:0}
.bg img{width:100%;height:100%;object-fit:cover}
.hero .bg::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.6) 0,rgba(0,0,0,.24) 14%,rgba(0,0,0,.04) 30%,rgba(0,0,0,.52) 52%,rgba(0,0,0,.72) 100%)}
.hero h1{position:relative;padding:0 32px;text-align:center;font-size:var(--h1);line-height:1;letter-spacing:.02em;font-weight:400}
.hero h1 span{display:block;white-space:nowrap}
.chev{position:relative;align-self:center;padding:40px 0;line-height:0;animation:blink 2s ease-in-out infinite}
.chev svg{width:24px;height:24px}
@keyframes blink{50%{opacity:.25}}

/* modules fade in once (1 s ease) — only when scripts run */
.js .ob{opacity:0;transition:opacity 1s ease}
.js .ob.seen{opacity:1}

/* headline module */
.hm{padding:120px 32px 40px;display:flex;flex-direction:column;align-items:center;gap:40px}
.hm .h2{max-width:907px}
.hm-t{max-width:640px;text-align:center}
.hm-t p{margin-bottom:16px}.hm-t p:last-child{margin-bottom:0}
.hm-t .cta{margin:24px 0 16px}
.hm-t .cta:last-child{margin-bottom:0}
.hours{font-variant-numeric:tabular-nums}.nb{white-space:nowrap}

/* the button: two 1 px frames, one drawn in from the sides and one from top and bottom; they meet on hover */
.cta{position:relative;display:inline-flex;justify-content:center;align-items:center;min-width:203px;padding:12px 48px;color:inherit;text-align:center;transition:color .2s cubic-bezier(.45,0,.55,1)}
.cta span{position:relative;top:1px}
.cta::before,.cta::after{content:"";position:absolute;border:1px solid var(--rule);transition:inset .2s,border-color .2s}
.cta::before{inset:0 4px}.cta::after{inset:4px 0}
.cta:hover::before,.cta:focus-visible::before{inset:5px;border-color:currentColor}
.cta:hover::after,.cta:focus-visible::after{inset:4px;border-color:currentColor}
.cta-l::before,.cta-l::after{border-color:rgba(255,255,255,.45)}

/* gallery of four upright tiles; pair of two large upright pictures */
.g4{margin:0 auto;width:calc(100% - 64px);max-width:1536px;padding:40px 0;display:grid;grid-template-columns:repeat(4,1fr);gap:32px}
.g4 img,.g2 img{width:100%;aspect-ratio:3/4;object-fit:cover}
.g2{margin:0 32px;padding:40px 0;display:grid;grid-template-columns:1fr 1fr;gap:32px}

/* content module: sub-head, paragraph, dashed lines, button */
.cm{padding:40px 32px}
.cm-band{margin-bottom:40px}
.cm-band img{width:100%;aspect-ratio:8/3;object-fit:cover}
.cm-g{display:grid;grid-template-columns:1fr 1fr;gap:24px 32px;align-items:start}
.cm-g>.sub{position:sticky;top:88px}
.cm-t{max-width:640px}
.cm-t p{margin-bottom:16px}
.cm-t .cta{margin:24px 0 0 -4px}
.cm+.cm{padding-top:24px}

/* image teaser: one screen of photograph, small line on top, tag + headline + button at the foot */
.te{position:relative;margin-top:40px;min-height:100vh;min-height:100svh;display:flex;flex-direction:column;justify-content:space-between;align-items:center;padding:40px 32px 64px;color:var(--on);overflow:clip;background:#000}
.te .bg::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.3) 0,rgba(0,0,0,.04) 20%,rgba(0,0,0,.04) 36%,rgba(0,0,0,.72) 62%,rgba(0,0,0,.84) 100%)}
.te>*:not(.bg){position:relative}
.te-top{font-size:16px;letter-spacing:.04em;text-transform:uppercase;text-align:center;max-width:640px;padding-top:40px}
.te-b{margin-top:auto;max-width:907px;display:flex;flex-direction:column;align-items:center;text-align:center}
.te-b .tag{margin-bottom:24px}
.te-b .cta{margin-top:48px}

/* cards (the reference's room card): double frame, tag, name, text, picture 3:2, ruled foot with the call */
.rg{margin:0 32px;padding:80px 0;display:grid;grid-template-columns:1fr 1fr;gap:40px 32px}
.rc{position:relative;display:flex;flex-direction:column;min-width:0}
.rc::before,.rc::after{content:"";position:absolute;border:1px solid var(--rule);pointer-events:none}
.rc::before{inset:0}.rc::after{inset:8px}
.rc-top{padding:48px 48px 24px;display:flex;flex-direction:column;align-items:center;text-align:center}
.rc-top .tag{line-height:1}
.rc h3{font-size:clamp(26px,1.81vw + 19px,45px);line-height:1.25;padding:24px 0;text-wrap:balance;overflow-wrap:anywhere}
.rc-top p.tx{color:var(--q);max-width:576px}
.rc-top .more{margin-top:24px}
.rc-pic{margin:24px 36px 0;display:flex;justify-content:center}
.rc-pic img{width:100%;aspect-ratio:3/2;object-fit:cover}
.rc-list{margin:8px 48px 0;align-self:stretch}
.rc-list li{display:flex;justify-content:space-between;gap:24px;align-items:baseline;padding:14px 0;border-top:1px solid var(--rule)}
.rc-list a{text-decoration:none}.rc-list a:hover{text-decoration:underline;text-underline-offset:3px}
.rc-list .pr{white-space:nowrap;font-variant-numeric:tabular-nums}
.rc-list small{display:block;font-size:12px;letter-spacing:.04em;text-transform:uppercase;color:var(--q)}
.rc-bot{margin:auto 32px 0;padding-top:24px}
.rc-bot div{border-top:1px solid var(--rule);padding:24px 24px 32px;text-align:center}
.rc-bot a{display:inline-block}
.rc-bot a:hover,.more:hover{opacity:.6}
.rc-end{height:48px}

/* ruled index (the menu panel's rows) in two columns */
.ix{margin:0 32px;padding:40px 0 0;columns:2;column-gap:64px}
.ix li{break-inside:avoid}
.ix li{border-top:1px solid var(--rule)}
.ix .n{font:400 16px/1.45 'Jost',sans-serif;letter-spacing:0;color:var(--q);font-variant-numeric:tabular-nums}
.rg.tight{padding-top:40px}
.faq summary{cursor:pointer;list-style:none}.faq summary::-webkit-details-marker{display:none}
.faq details p{padding:0 0 24px;max-width:640px}

.full{padding-top:40px}
.full img{width:100%;aspect-ratio:3/2;object-fit:cover}

/* footer: the accent, a square card of the page ground with the name and the contact lines, then the link row */
.ft{background:var(--a);color:var(--oa);margin-top:40px}
.ft-c{position:relative;padding:32px;min-height:var(--fh);display:flex}
.ft-card{position:relative;width:400px;min-height:400px;align-self:flex-start;background:var(--g);color:var(--i);padding:32px;display:flex;flex-direction:column;justify-content:space-between;gap:40px;text-align:center}
.ft-name{font-size:var(--fn);line-height:1.12;text-wrap:balance}
.ft-name img{margin:0 auto;max-height:102px;width:auto}
.ft-info{display:grid;gap:12px;font-size:16px;line-height:1.15;letter-spacing:.04em;text-transform:uppercase;justify-items:center}
.ft-info a{text-decoration:none}.ft-info a:hover{text-decoration:underline;text-underline-offset:3px}
.ft-b{padding:16px 32px}
.ft-b .lab{display:inline-block;padding:16px 0}
.ft-b .lab[href]:hover{opacity:.6}
.ft-news{margin-bottom:16px}
.ft-m{display:flex;justify-content:space-between;gap:16px 32px;flex-wrap:wrap}
.ft-m ul{display:flex;flex-wrap:wrap;gap:0 32px}
.ft-legal{padding:8px 0 16px;font-size:12px;letter-spacing:.04em;text-transform:uppercase}
.notice{display:grid;grid-template-columns:200px 1fr;gap:32px;padding:24px 0;border-top:1px solid var(--rule-a);font-size:12px;line-height:1.5}
.notice img{background:#fff}
.notice p{margin-bottom:8px;max-width:760px}

@media (max-width:820px){
 .lab{font-size:12px}.tag{font-size:11px}
 .hd{height:62px;padding:0 16px}
 .mark img{height:40px}.mark span{font-size:12px;max-width:52vw}
 .menu-c{padding:62px 16px 32px;gap:20px}.menu-p{display:none}
 .rows a,.rows .row{font-size:18px;line-height:1.3;padding:19.8px 0}
 .menu .rows a{justify-content:center;text-align:center}
 .menu-info{padding-top:32px}
 .hero h1{padding:0 16px}.chev{padding:24px 0}
 .hm{padding:80px 16px 24px}
 .hm-t .cta,.cm-t .cta{display:flex;margin-left:0}
 .g4{width:calc(100% - 32px);padding:24px 0;grid-template-columns:1fr 1fr;gap:16px}
 .g2{margin:0 16px;padding:24px 0;grid-template-columns:1fr;gap:40px}
 .g2 img{width:74%}.g2 img:nth-child(2){margin-left:auto}
 .cm{padding:24px 16px}.cm-band{margin-bottom:16px}.cm-band img{aspect-ratio:3/2}
 .cm-g{grid-template-columns:1fr;gap:20px}.cm-g>.sub{position:static}
 .te{margin-top:24px;padding:24px 16px 40px}
 .te-top{padding-top:44px}
 .te-b{align-items:stretch}.te-b .tag{margin-bottom:16px}.te-b .cta{margin-top:32px}
 .rg{margin:0 16px;padding:56px 0;grid-template-columns:1fr;gap:24px}
 .rg.tight{padding-top:24px}
 .rc-top{padding:32px 32px 16px}.rc h3{padding:16px 0}.rc-top .more{margin-top:16px}
 .rc-pic{margin:16px 24px 0}.rc-list{margin:8px 24px 0}
 .rc-bot{margin:auto 24px 0;padding-top:16px}.rc-bot div{padding:16px 20px 20px}.rc-end{height:32px}
 .ix{margin:0 16px;padding-top:24px;columns:1}
 .full{padding-top:24px}
 .ft{margin-top:24px}
 .ft-c{padding:16px;min-height:var(--fhm);justify-content:center;align-items:center}
 .ft-card{width:286px;min-height:286px;padding:16px;align-self:center;gap:24px}
 .ft-info{gap:8px}
 .ft-b{padding:24px 16px}.ft-b .lab{padding:12px 0}
 .ft-m{display:block}
 .ft-m ul{display:grid;grid-template-columns:1fr 1fr;gap:0 16px}
 .notice{grid-template-columns:1fr;gap:16px}.notice img{max-width:200px}
}
@media (prefers-reduced-motion:reduce){
 *,*::before,*::after{animation:none!important;transition:none!important}
 .js .ob{opacity:1}
}
"""

JS = r"""
(function(){var d=document,h=d.querySelector('.hd'),m=d.querySelector('.menu'),b=d.querySelector('.burger'),f=d.querySelector('.ft');
var hl=h.querySelector('.hd-r .lab');function fit(){if(!hl)return;h.classList.remove('long');var lh=parseFloat(getComputedStyle(hl).lineHeight)||20;var pd=parseFloat(getComputedStyle(hl).paddingTop)+parseFloat(getComputedStyle(hl).paddingBottom);h.classList.toggle('long',hl.offsetHeight-pd>lh*1.5);}
fit();addEventListener('resize',fit);if(document.fonts&&document.fonts.ready)document.fonts.ready.then(fit);
function sc(){var y=window.scrollY||0;h.classList.toggle('top',y<10);if(f)h.classList.toggle('up',f.getBoundingClientRect().top<=h.offsetHeight);}
sc();addEventListener('scroll',sc,{passive:true});addEventListener('resize',sc);
function set(o){m.classList.toggle('open',o);h.classList.toggle('open',o);b.setAttribute('aria-expanded',o?'true':'false');b.setAttribute('aria-label',o?b.dataset.close:b.dataset.open);if(o){m.removeAttribute('inert')}else{m.setAttribute('inert','')}d.documentElement.style.overflow=o?'hidden':'';}
if(b&&m){set(false);b.addEventListener('click',function(){set(!m.classList.contains('open'))});
m.addEventListener('click',function(e){if(e.target.closest('a'))set(false)});
addEventListener('keydown',function(e){if(e.key==='Escape'&&m.classList.contains('open')){set(false);b.focus()}});}
var os=d.querySelectorAll('.ob');if('IntersectionObserver' in window){var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('seen');io.unobserve(e.target)}})},{rootMargin:'0px 0px -8% 0px'});os.forEach(function(o){io.observe(o)})}else{os.forEach(function(o){o.classList.add('seen')})}
})();
"""


def render(d: dict) -> str:
    g = lambda o, *k: (g(o.get(k[0]) or {}, *k[1:]) if len(k) > 1 else (o.get(k[0]) if isinstance(o, dict) else None)) if k else o
    lang = d.get('lang') or 'en'
    W = WORDS.get(lang, WORDS['en'])
    brand, pal, place = d.get('brand') or {}, d.get('palette') or {}, d.get('place') or {}
    hero, st, steps, feats, close, foot = (d.get(k) or {} for k in ('hero', 'statement', 'steps', 'features', 'close', 'foot'))
    name = brand.get('name') or ''

    # colours: the reference's relations (quiet ground, black ink, the accent only as a field), the client's palette
    G, I, A = _rgb(pal.get('ground') or '#ffffff'), _rgb(pal.get('ink') or '#000000'), _rgb(pal.get('accent') or '#cc663c')
    OA = I if _cr(I, A) >= _cr(G, A) else G
    while _cr(OA, A) < 4.6 and A != OA:  # the field must carry its own text
        A = _mix(A, G if OA == I else I, .08)
        if _cr(OA, A) >= 4.6 or max(abs(A[i] - (G if OA == I else I)[i]) for i in range(3)) < 2: break
    ON = G if _lum(G) > .6 else (I if _lum(I) > .6 else (255, 255, 255))
    rule = lambda fg: 'rgba(%d,%d,%d,.15)' % fg
    Q = _quiet(I, G)

    # photographs: nothing twice; a picture that would be enlarged more than a quarter is not used for that slot
    photos = [p for p in (g(d, 'media', 'photos') or []) if p.get('src') and p.get('w') and p.get('h')]
    spaces = [s for s in (place.get('spaces') or []) if s.get('title')]
    cards = spaces or [{'tag': s.get('k'), 'title': s.get('title'), 'text': s.get('text'), 'img': s.get('img'), 'cta': s.get('cta')}
                       for s in (steps.get('items') or []) if s.get('title')]
    card_src = {c.get('img') for c in cards if c.get('img')}
    by_src = {p['src']: p for p in photos}
    used = set()

    stem = lambda p: re.sub(r'(-\d+)?\.\w+$', '', p['src'])  # "x.jpg" and "x-2.jpg" are two views of one subject
    stems = set()

    def take(Wd, Hd, roles=None, n=1, allow_card=False, tile=False):
        """backdrops and bands: large photographs only, enlarged at most a quarter. tiles: any photograph that is not enlarged."""
        pool = [p for p in photos if p['src'] not in used and (allow_card or p['src'] not in card_src)
                and ((tile and _fit(p, Wd, Hd) <= 1) or (not p.get('small') and _fit(p, Wd, Hd) <= 1.25))]
        if roles: pool.sort(key=lambda p: (roles.index(p.get('role')) if p.get('role') in roles else len(roles), _fit(p, Wd, Hd)))
        got = []
        for p in pool:
            if len(got) == n: break
            if stem(p) in stems or stem(p) in {stem(q) for q in got}: continue
            got.append(p)
        if len(got) < n: return [] if n > 1 else None
        used.update(p['src'] for p in got); stems.update(stem(p) for p in got)
        return got if n > 1 else got[0]

    p_hero = take(1440, 900, ['room', 'exterior', 'bar', 'people', 'other', 'dish']) or take(1440, 900, None, 1, True)
    if p_hero and p_hero['src'] in card_src: card_src.discard(p_hero['src'])
    p_spaces = take(1440, 900, ['room', 'exterior', 'bar', 'people', 'other']) if cards else None
    menu = place.get('menu') or {}
    has_menu = bool(menu.get('h') or menu.get('sections') or menu.get('lists'))
    p_menu = take(1440, 900, ['dish', 'bar', 'people', 'other']) if has_menu else None
    p_full = take(1440, 960, ['exterior', 'room', 'bar', 'other', 'people', 'dish'])
    p_band = take(1376, 516, None) if (st.get('title') or st.get('text')) else None
    places_first, dishes_first = ['room', 'exterior', 'bar', 'people', 'other', 'dish'], ['dish', 'bar', 'people', 'other', 'room', 'exterior']
    g4a = take(360, 480, places_first, 4, tile=True)
    g2 = take(672, 896, None, 2, tile=True)
    g4m = [] if g2 else (take(360, 480, dishes_first, 4, tile=True) if has_menu else [])  # no two large uprights: a row of four stands in for the pair
    g4b = take(360, 480, dishes_first, 4, tile=True)
    p_foot = take(1440, 748, None)

    # ── header and menu panel
    cta = d.get('cta') or place.get('booking') or {}
    nav = [n for n in (d.get('nav') or []) if n.get('t') and n.get('h')]
    seen_h = {n['h'] for n in nav}
    extra = [l for l in (d.get('links') or []) if l.get('t') and l.get('h') and l['h'] not in seen_h]
    logo = brand.get('logo')
    mark = (f'<a class="mark has-img" href="#top" aria-label="{E(name)}"><img src="{P}{E(logo)}" alt="{E(name)}"></a>' if logo
            else f'<a class="mark is-name dis" href="#top"><span>{E(name)}</span></a>')
    addr = place.get('address') or {}
    addr_t = ', '.join(x for x in [addr.get('street'), ' '.join(x for x in [addr.get('postcode'), addr.get('city')] if x)] if x)
    phone, email = place.get('phone') or {}, place.get('email')
    info = []
    if email: info.append(f'<a href="mailto:{E(email)}">{E(email)}</a>')
    if addr_t: info.append(f'<span>{E(addr_t)}</span>')
    if phone.get('t'): info.append(f'<a href="{E(phone["h"])}">{E(phone["t"])}</a>' if phone.get('h') else f'<span>{E(phone["t"])}</span>')
    menu_rows = ''.join(f'<li><a class="dis" href="{E(n["h"])}">{E(n["t"])}</a></li>' for n in nav + extra)
    # the header's booking label stands on one line in its cell; where it would wrap (a long label on a phone) it leaves
    # the header for the menu, which then carries it as its last row (the script decides by measuring, at every width)
    only_cta = not menu_rows                                    # the menu exists only to carry the long label
    if cta.get('h') and cta.get('t') and cta['h'] not in seen_h | {l['h'] for l in extra}:
        menu_rows += f'<li class="cta-row"><a class="dis" href="{E(cta["h"])}">{E(cta["t"])}</a></li>'
    header = f'''<a class="skip" href="#main">{E(W[4])}</a>
<header class="hd top{" on-pic" if p_hero else " on-deep"}">
<div class="hd-l">{f'<button class="burger no-js-hide{" cta-only" if only_cta else ""}" type="button" aria-controls="menu" aria-expanded="false" aria-label="{E(W[0])}" data-open="{E(W[0])}" data-close="{E(W[1])}"><i></i><i></i></button>' if menu_rows else ''}</div>
{mark}
<div class="hd-r">{_a(cta, 'lab') if cta.get('h') else ''}</div>
</header>'''
    panel = f'''<nav class="menu" id="menu" aria-label="{E(W[2])}">
<div class="menu-c"><ul class="rows">{menu_rows}</ul>{f'<div class="menu-info">{"".join(info)}</div>' if info else ''}</div>
{f'<div class="menu-p">{_img(p_hero)}</div>' if p_hero else ''}
</nav>''' if menu_rows else ''

    # ── 1 hero
    lines = _two_lines(name) if name else []
    longest = max((len(l) for l in lines), default=8)
    h1_d = min(10.4, 95.5 / (longest * .68 + .5))  # vw; the reference's wordmark fills 1376 of 1440 at 112 px capitals
    h1_m = min(13.5, 91.8 / (longest * .68 + .5))
    hero_html = f'''<section class="hero{" pic" if p_hero else ""}" id="top">
{f'<div class="bg">{_img(p_hero, eager=True)}</div>' if p_hero else ''}
<h1 class="dis">{"".join(f"<span>{E(l)}</span>" for l in lines)}</h1>
<a class="chev" href="#main" aria-label="{E(W[4])}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" aria-hidden="true"><path d="M3 8l9 8 9-8"/></svg></a>
</section>'''

    def headline(title, paras, btn='', after='', tag=''):
        if not title and not any(paras): return ''
        body = ''.join(f'<p>{E(p)}</p>' for p in paras if p) + btn + after
        return (f'<section class="hm ob">{f"<p class=tag>{E(tag)}</p>" if tag else ""}{H2 % E(title) if title else ""}'
                f'{f"<div class=hm-t>{body}</div>" if body else ""}</section>')

    def teaser(pic, title, tag, btn_o, top=''):
        return (f'<section class="te ob"><div class="bg">{_img(pic)}</div>{f"<p class=te-top>{E(top)}</p>" if top else ""}'
                f'<div class="te-b">{f"<p class=tag>{E(tag)}</p>" if tag else ""}<h2 class="h2 dis">{E(title)}</h2>{_btn(btn_o, True)}</div></section>')

    def gal4(ps): return f'<div class="g4 ob">{"".join(_img(p) for p in ps)}</div>' if ps else ''

    # ── 2 headline: what the place is
    note = hero.get('note')
    if note and phone.get('h') and phone.get('t') and phone['t'] in note:
        note_html = '<p>' + E(note).replace(E(phone['t']), f'<a href="{E(phone["h"])}">{E(phone["t"])}</a>') + '</p>'
    else: note_html = f'<p>{E(note)}</p>' if note else ''
    s_head = headline(hero.get('title'), [hero.get('text'), hero.get('text2')], _btn(hero.get('primary') or cta), note_html)

    # ── 4 content module: statement + trust
    sec = hero.get('secondary') or {}
    sec_for_menu = bool(sec.get('h') and menu.get('h') and sec['h'] == menu['h'])

    def content(sub, paras, dashes, btn='', band=None):
        if not sub and not paras: return ''
        t = ''.join(f'<p>{E(p)}</p>' for p in paras if p) + ''.join(f'<p>- {E(x)}</p>' for x in dashes if x) + btn
        return (f'<section class="cm ob">{f"<div class=cm-band>{_img(band)}</div>" if band else ""}<div class="cm-g">'
                f'<h2 class="sub dis">{E(sub or "")}</h2><div class="cm-t">{t}</div></div></section>')
    s_cm = content(st.get('title'), [st.get('text')], d.get('trust') or [], '' if sec_for_menu else _btn(sec), p_band) if (st.get('title') or st.get('text')) else ''

    # ── 5 spaces
    booking = place.get('booking') or d.get('cta') or {}

    def card(tag, title, text='', pic=None, more=None, foot_o=None, rows=None):
        pic_html = ''
        if pic:
            mw = f' style="max-width:{pic["w"]}px"' if pic.get('small') or pic['w'] < 600 else ''
            pic_html = f'<div class="rc-pic"><div{mw}>{_img(pic)}</div></div>'
        rows_html = ''
        if rows:
            li = []
            for r in rows:
                nm = f'<a href="{E(r["h"])}">{E(r["name"])}</a>' if r.get('h') else E(r.get('name') or '')
                sm = '<small>' + E(r['note']) + '</small>' if r.get('note') else ''
                pr = '<span class="pr">' + E(r['price']) + '</span>' if r.get('price') else ''
                li.append('<li><span>' + nm + sm + '</span>' + pr + '</li>')
            rows_html = f'<ul class="rc-list">{"".join(li)}</ul>'
        bot = f'<div class="rc-bot"><div>{_a(foot_o, "lab")}</div></div>' if foot_o and foot_o.get('t') and foot_o.get('h') else '<div class="rc-end"></div>'
        return (f'<article class="rc"><div class="rc-top">{f"<p class=tag>{E(tag)}</p>" if tag else ""}<h3 class="dis">{E(title)}</h3>'
                f'{f"<p class=tx>{E(text)}</p>" if text else ""}{_a(more, "lab more") if more else ""}</div>{pic_html}{rows_html}{bot}</article>')
    s_spaces = ''
    if cards:
        t, tg = steps.get('title'), steps.get('text')
        if t: s_spaces += teaser(p_spaces, t, tg, None) if p_spaces else headline(t, [tg])
        s_spaces += '<div class="rg ob' + (' tight' if t and not p_spaces else '') + '">' + ''.join(
            card(c.get('tag'), c['title'], c.get('text'), by_src.get(c.get('img')) if c.get('img') not in used else None,
                 None, c.get('cta') or booking) for c in cards) + '</div>'

    # ── 6 menu
    s_menu = ''
    if has_menu:
        L = next((l for l in (d.get('links') or []) + nav if l.get('h') and l['h'] == menu.get('h')), {})
        mt = L.get('t') or feats.get('title')
        mb = sec if sec_for_menu else ({'t': L.get('t'), 'h': menu.get('h')} if menu.get('h') and L.get('t') else None)
        if mt: s_menu += teaser(p_menu, mt, L.get('d'), mb) if p_menu else headline(mt, [L.get('d')], _btn(mb))
        idx = [s for s in (menu.get('sections') or []) if s.get('t') and not s.get('items')] + [s for s in (menu.get('lists') or []) if s.get('t')]
        if idx:
            s_menu += '<ul class="ix rows ob">' + ''.join(
                '<li>' + (f'<a class="dis" href="{E(s["h"])}">' if s.get('h') else '<span class="row dis">') + f'<span>{E(s["t"])}</span>'
                + (f'<span class="n">{E(str(s["count"]))}</span>' if s.get('count') else '') + ('</a>' if s.get('h') else '</span>') + '</li>' for s in idx) + '</ul>'
        full = [s for s in (menu.get('sections') or []) if s.get('t') and s.get('items')]
        if full:
            s_menu += '<div class="rg ob tight">' + ''.join(card(None, s['t'], '', None, None, None, s['items']) for s in full) + '</div>'

    # ── plans and questions (a place seldom has them; never dropped when it does)
    plans, faq = d.get('plans') or {}, d.get('faq') or {}
    s_plans = ''
    if plans.get('items'):
        s_plans = headline(plans.get('title'), [plans.get('text')]) + '<div class="rg ob tight">' + ''.join(
            card(' · '.join(x for x in [pl.get('price'), pl.get('per')] if x), pl.get('name') or '', pl.get('line'), None, None, pl.get('cta'),
                 [{'name': r} for r in (pl.get('rows') or [])]) for pl in plans['items']) + '</div>' + (f'<p class="hm-t" style="margin:0 auto;padding:0 16px">{E(plans["note"])}</p>' if plans.get('note') else '')
    s_faq = ''
    if faq.get('items'):
        s_faq = headline(faq.get('title'), []) + '<ul class="ix rows faq ob" style="columns:1;max-width:907px;margin-inline:auto;padding-inline:16px">' + ''.join(
            f'<li><details><summary class="row dis"><span>{E(q.get("q") or "")}</span></summary><p>{E(q.get("a") or "")}</p></details></li>' for q in faq['items']) + '</ul>'

    cat = d.get('catalogue') or {}
    s_cat = ''
    if cat.get('groups'):
        s_cat = headline(cat.get('title'), [cat.get('text')]) + '<div class="rg ob tight">' + ''.join(
            card(None, gr.get('t') or '', gr.get('text'), None, None, None,
                 [{'name': it.get('name'), 'price': it.get('price') or it.get('from'), 'note': it.get('note') or it.get('state'), 'h': it.get('h')}
                  for it in (gr.get('items') or []) if it.get('name')]) for gr in cat['groups'] if gr.get('t')) + '</div>'

    # ── 8 events as content modules
    s_events = ''.join(content(ev.get('what'), [ev.get('when')], [x for x in [ev.get('price'), ev.get('where')] if x], _btn(ev.get('cta')))
                       for ev in (place.get('events') or []) if ev.get('what'))

    # ── 9 closing headline with the hours
    hours = [h for h in (place.get('hours') or []) if h.get('days')]
    hrs = ''.join(f'<p class="hours">{E(h["days"])} · <span class="nb">{E(" – ".join(x for x in [h.get("open"), h.get("close")] if x))}</span></p>' for h in hours)
    s_close = headline(close.get('title'), [close.get('text')], _btn(close.get('cta') or booking), hrs)

    # ── 12 footer
    fl = max((len(l) for l in lines), default=8)
    fn_d, fn_m = min(45, 336 / (fl * .7 + .5)), min(36, 254 / (fl * .7 + .5))
    f_name = (f'<img src="{P}{E(logo)}" alt="{E(name)}">' if logo else '') + ''.join(f'<span style="display:block">{E(l)}</span>' for l in lines)
    f_info = info + [f'<span class="hours">{E(h["days"])} · <span class="nb">{E(" – ".join(x for x in [h.get("open"), h.get("close")] if x))}</span></span>' for h in hours]
    take_o = place.get('takeaway') or {}
    f_links = []
    seen = set()
    for l in nav + [x for x in (foot.get('links') or []) if x.get('t') and x.get('h')]:
        if l['h'] in seen: continue
        seen.add(l['h']); f_links.append(l)
    social = [s for s in (place.get('social') or []) if s.get('t') and s.get('h') and s['h'] not in seen]
    notices = ''.join(
        f'<div class="notice">{_img({"src": n["img"], "w": n.get("w") or 800, "h": n.get("h") or 800, "alt": ""}) if n.get("img") else "<span></span>"}'
        f'<div>{"".join(f"<p>{E(t)}</p>" for t in (n.get("text") or []))}</div></div>' for n in (place.get('notices') or []))
    footer = f'''<footer class="ft">
<div class="ft-c">{f'<div class="bg">{_img(p_foot)}</div>' if p_foot else ''}
<div class="ft-card"><p class="ft-name dis">{f_name}</p>{f'<div class="ft-info">{"".join(f_info)}</div>' if f_info else ''}</div></div>
<div class="ft-b">
{f'<div class="ft-news">{_a(take_o, "lab")}</div>' if take_o.get('t') and take_o.get('h') else ''}
<nav class="ft-m" aria-label="{E(W[3])}"><ul>{"".join(f"<li>{_a(l, 'lab')}</li>" for l in f_links)}</ul>{f"<ul>{''.join(f'<li>{_a(s, chr(108)+chr(97)+chr(98))}</li>' for s in social)}</ul>" if social else ''}</nav>
{f'<p class="ft-legal">{E(foot["legal"])}</p>' if foot.get('legal') else ''}
{notices}
</div>
</footer>'''

    body = ''.join([
        hero_html, '<main id="main">', s_head, gal4(g4a), s_cm, s_spaces, s_menu,
        f'<div class="g2 ob">{"".join(_img(p) for p in g2)}</div>' if g2 else gal4(g4m),
        s_cat, s_plans, s_events, s_faq, s_close, gal4(g4b),
        f'<div class="full ob">{_img(p_full)}</div>' if p_full else '', '</main>', footer])

    root = (f':root{{--g:{_hex(G)};--i:{_hex(I)};--a:{_hex(A)};--oa:{_hex(OA)};--on:{_hex(ON)};--q:{_hex(Q)};--rule:{rule(tuple(int(v) for v in I))};'
            f'--rule-a:{rule(tuple(int(v) for v in OA))};--h1:{h1_d:.2f}vw;--fn:{fn_d:.1f}px;--fh:{"748px" if p_foot else "0px"};--fhm:{"437px" if p_foot else "0px"}}}'
            f'@media (max-width:820px){{:root{{--h1:{h1_m:.2f}vw;--fn:{fn_m:.1f}px}}}}')
    desc = hero.get('text') or st.get('text') or ''
    return f'''<!doctype html>
<html lang="{E(lang)}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(name)}</title>
{f'<meta name="description" content="{E(desc)}">' if desc else ''}
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Josefin+Sans:wght@300;400;700&family=Jost:wght@400;500&display=swap" rel="stylesheet">
<style>{root}{CSS}</style>
<script>document.documentElement.classList.add('js')</script>
</head>
<body>
{header}
{panel}
{body}
<script>{JS}</script>
</body>
</html>'''
