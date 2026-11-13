"""ddsks — the build of ddsks.dk (a performing-arts school; photograph-led) with a client's data written in.
render(d) -> one self-contained page. Pure: no file reads, no model, no client-specific branch.
Measures are the reference's at 1440 and 390 (see NOTES.md). Pictures are the client's own photographs only."""
from html import escape as _e

UI = {  # interface words only (never client facts); falls back to English
    'menu': {'en': 'Menu', 'de': 'Menü', 'es': 'Menú', 'fr': 'Menu', 'it': 'Menu', 'da': 'Menu', 'nl': 'Menu', 'pt': 'Menu', 'sr': 'Meni', 'sl': 'Meni'},
    'close': {'en': 'Close', 'de': 'Schließen', 'es': 'Cerrar', 'fr': 'Fermer', 'it': 'Chiudi', 'da': 'Luk', 'nl': 'Sluiten', 'pt': 'Fechar', 'sr': 'Zatvori', 'sl': 'Zapri'},
    'top': {'en': 'Back to top', 'de': 'Nach oben', 'es': 'Volver arriba', 'fr': 'Haut de page', 'it': 'Torna su', 'da': 'Til toppen', 'nl': 'Naar boven', 'pt': 'Voltar ao topo', 'sr': 'Na vrh', 'sl': 'Na vrh'},
}


# ---------- colour ----------
def _rgb(h):
    h = (h or '#000000').lstrip('#')
    if len(h) == 3: h = ''.join(c * 2 for c in h)
    try: return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError: return (0, 0, 0)
def _hex(c): return '#%02x%02x%02x' % tuple(max(0, min(255, round(v))) for v in c)
def _lum(c):
    f = lambda v: v / 3294.6 if v <= 10.0164 else ((v / 255 + .055) / 1.055) ** 2.4
    return .2126 * f(c[0]) + .7152 * f(c[1]) + .0722 * f(c[2])
def _con(a, b):
    x, y = _lum(a), _lum(b)
    return (max(x, y) + .05) / (min(x, y) + .05)
def _mix(a, b, t): return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))
def _toward(c, target, ground, need):
    """c moved toward target until it reads on ground at `need`:1"""
    for i in range(0, 21):
        m = _mix(c, target, i / 20)
        if _con(m, ground) >= need: return m
    return target


# ---------- small parts ----------
def _a(v): return _e(str(v if v is not None else ''), quote=True)
def _src(p): return p if str(p).startswith(('http:', 'https:', 'data:', '../../')) else '../../' + str(p)
ARROW = '<svg class="ar" viewBox="0 0 24 10" width="24" height="10" aria-hidden="true"><path d="M0 5h22M18 1l4 4-4 4" fill="none" stroke="currentColor" stroke-width="2"/></svg>'
def _ci(kind):
    g = {'go': '<path d="M2 7h10M8 3l4 4-4 4"/>', 'down': '<path d="M2 5l5 5 5-5"/>', 'up': '<path d="M2 9l5-5 5 5"/>',
         'dots': '<path d="M7 2v.01M7 7v.01M7 12v.01" stroke-width="2.6" stroke-linecap="round"/>', 'x': '<path d="M3 3l8 8M11 3l-8 8"/>'}[kind]
    return f'<span class="ci ci-{kind}" aria-hidden="true"><svg viewBox="0 0 14 14" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">{g}</svg></span>'
def _more(t, h, cls=''):
    if not (t and h): return ''
    return f'<a class="more {cls}" href="{_a(h)}">{_e(t)}{ARROW}</a>'
def _img(p, cls='', sizes='', slot='', lazy=True, style=''):
    return (f'<img class="{cls}" src="{_a(_src(p["src"]))}" width="{int(p.get("w") or 0) or ""}" height="{int(p.get("h") or 0) or ""}" alt="{_a(p.get("alt") or "")}"'
            + (' loading="lazy"' if lazy else '') + ' decoding="async"' + (f' data-slot="{slot}"' if slot else '') + (f' style="{style}"' if style else '') + '>')
def _clamp(v, lo, hi): return max(lo, min(hi, v))


CSS = r"""
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--ink);font:400 18px/24px "Hanken Grotesk",Arial,sans-serif;-webkit-font-smoothing:antialiased;overflow-x:hidden}
img{display:block;max-width:100%;height:auto}
a{color:inherit;text-decoration:none}
h1,h2,h3,h4,p,ul,ol,figure,blockquote,dl,dd{margin:0;padding:0}
ul,ol{list-style:none}
button{font:inherit;color:inherit;background:none;border:0;padding:0;cursor:pointer}
:focus-visible{outline:2px solid currentColor;outline-offset:4px}
.c{font-family:"League Gothic","Arial Narrow",Impact,sans-serif;font-weight:400;text-transform:uppercase;letter-spacing:.012em}
.wrap{width:80vw;margin:0 auto;position:relative}
.skip{position:absolute;left:-999px;top:0;background:var(--paper);color:var(--ink);padding:10px 14px;z-index:99}
.skip:focus{left:10px;top:10px}
.sm{font-size:20px;line-height:20px}
.meta{font-size:14px;line-height:20px;color:var(--meta)}
.txtlink{color:var(--link)}
.txtlink:hover{text-decoration:underline}

/* icons */
.ci{display:inline-grid;place-items:center;width:32px;height:32px;border-radius:50%;box-shadow:inset 0 0 0 2px currentColor;flex:none;transition:background-color .2s cubic-bezier(.77,0,.175,1),color .2s cubic-bezier(.77,0,.175,1)}
.ar{display:inline-block;margin-left:10px;vertical-align:middle;position:relative;top:-2px;transition:transform .2s cubic-bezier(.25,.46,.45,.94)}
.more{display:inline-block;font-family:"League Gothic","Arial Narrow",Impact,sans-serif;text-transform:uppercase;letter-spacing:.012em;font-size:20px;line-height:20px}
a:hover>.ar,a:hover .more .ar,.more:hover .ar{transform:translateX(10px)}

/* header: links fixed, a paper bar behind them that the opening picture covers */
.hd-bar{position:absolute;top:0;left:0;right:0;height:65px;background:var(--paper);z-index:20}
.hd{position:absolute;top:0;left:0;right:0;z-index:40;color:var(--ink);pointer-events:none}
.js .hd-bar,.js .hd{position:fixed}
.has-pic .hd{color:#fff}
.has-pic.past .hd{color:var(--ink)}
.has-pic.open .hd,.open .hd{color:#fff}
.hd .wrap{height:65px}
.hd a,.hd button{pointer-events:auto;transition:color .1s cubic-bezier(.25,.46,.45,.94)}
.brand{position:absolute;left:0;top:30px;font-size:20px;line-height:20px;letter-spacing:.1em;max-width:36%;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.hd-ph{position:absolute;left:59.322%;top:30px;font-size:20px;line-height:20px}
.hd-r{position:absolute;right:0;top:30px;display:flex;gap:25px}
.hd-r>*{position:relative;display:block;padding-right:42px;font-size:20px;line-height:20px;white-space:nowrap}
.hd-r .ci{position:absolute;right:0;top:-6px}
.hd-r>*:hover .ci{background:currentColor}
.hd-r>*:hover .ci svg{stroke:var(--paper)}
.has-pic:not(.past) .hd-r>*:hover .ci svg,.open .hd-r>*:hover .ci svg{stroke:var(--dark)}
.mb .ci-x{display:none}
.open .mb{color:var(--acc-d)}
.open .mb .ci-dots{display:none}
.open .mb .ci-x{display:inline-grid;background:#fff;color:var(--dark);box-shadow:none}

/* menu: the whole screen, dark, numbered */
.mn{position:fixed;inset:0;z-index:30;background:var(--dark);color:#fff;opacity:0;visibility:hidden;transition:opacity .2s cubic-bezier(.25,.46,.45,.94),visibility 0s .2s;overflow:auto}
.open .mn{opacity:1;visibility:visible;transition:opacity .2s cubic-bezier(.25,.46,.45,.94)}
.mn ol{margin:0 0 0 33.8983%;padding:280px 0 80px;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));column-gap:2.5641%;grid-auto-flow:column;grid-template-rows:repeat(var(--rows),auto)}
.mn li{min-height:150px;position:relative;padding-left:30px}
.mn li span{position:absolute;left:0;top:6px;font-size:16px;line-height:16px}
.mn li a{font-size:40px;line-height:40px;display:inline-block;transition:color .1s cubic-bezier(.25,.46,.45,.94)}
.mn li a:hover{color:var(--acc-d)}

/* opening */
.hero{position:relative;z-index:25;height:800px;color:#fff;margin-bottom:80px}
.hero .bg,.band .bg{position:absolute;top:0;left:50%;width:100vw;height:100%;margin-left:-50vw;object-fit:cover;max-width:none}
.hero .top{position:absolute;top:0;left:50%;width:100vw;margin-left:-50vw;height:190px;background:linear-gradient(to bottom,rgb(var(--dk)/.74) 0,rgb(var(--dk)/.7) 70px,rgb(var(--dk)/0) 100%)}
.hero .wrap{height:100%}
.ht{position:absolute;left:0;bottom:100px;width:100%}
.ht::before{content:"";position:absolute;left:-10vw;right:-10vw;top:-170px;bottom:-100px;background:linear-gradient(to bottom,rgb(var(--dk)/0) 0,rgb(var(--dk)/.6) 150px,rgb(var(--dk)/.66) 60%,rgb(var(--dk)/.78) 80%)}
.ht>*{position:relative}
.hero h1{font-size:80px;line-height:70px;letter-spacing:-.2px;width:74.5763%;margin-bottom:40px;text-wrap:balance}
.hero p{font-size:24px;line-height:30px;font-weight:300;width:66.1017%;margin-left:33.8983%}
.hero .more{margin:30px 0 0 33.8983%;transition:color .1s}
.hero.plain{height:auto;color:var(--ink);padding-top:150px;z-index:auto}
.hero.plain .ht{position:static}
.hero.plain .ht::before{display:none}
.hero.plain h1{font-size:clamp(50px,calc(10vw - 10px),130px);line-height:.854;margin-left:25.4237%;width:74.5763%;margin-bottom:80px}
.hero.plain p{margin-left:25.4237%}
.hero.plain .more{margin-left:25.4237%}

/* running parts */
.sec{margin-bottom:110px}
.lab{font-size:20px;line-height:20px;margin-bottom:60px;font-weight:400}
.lab.tight{margin-bottom:25px}
.lab+.man{margin-top:-30px}
.man{font-size:24px;line-height:30px;font-weight:300;margin:0 0 60px 25.4237%;width:66.1017%}
.intro{margin:0 0 110px 25.4237%;width:49.1319%}
.intro p{margin-bottom:24px}
.intro .meta{margin-bottom:24px}

/* the staggered teasers */
.t{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));column-gap:1.6949%;align-items:start;position:relative;color:inherit}
.t .im{grid-row:1;overflow:visible;transition:transform .1s ease-in;position:relative}
.t .im img{width:100%;height:100%;object-fit:cover}
.t .tx{grid-row:1;margin-top:40px;position:relative}
.t h3{font-size:60px;line-height:55px;margin-bottom:20px;transition:color .1s cubic-bezier(.25,.46,.45,.94);overflow-wrap:break-word}
.t .tx p{margin-bottom:30px}
.t.ka .im{grid-column:8/13;justify-self:end}
.t.ka .tx{grid-column:3/8;margin-bottom:30px}
.t.kb .im{grid-column:1/5;justify-self:start}
.t.kb .tx{grid-column:5/10;margin-bottom:160px}
.t.kc{margin-top:-130px;z-index:2}
.t.kc .im{grid-column:4/9;justify-self:start}
.t.kc .tx{grid-column:9/13;text-align:right}
.t.kb+.t.ka,.t.kc+.t.ka{margin-top:30px}
.t.nopic .tx{margin-bottom:60px}
.t.nopic.kc{margin-top:0}
a.t:hover h3{color:var(--link)}
a.t:hover .im{transform:scale(1.05)}

/* picture bands */
.band{position:relative;color:#fff;padding:90px 0 300px;margin-bottom:110px;overflow:hidden;background:var(--dark)}
.band.fig{padding-bottom:210px}
.band.plain,.band.lk{padding:80px 0 70px}
.bc{position:relative}
.band.pic .bc::before{content:"";position:absolute;left:-10vw;right:-10vw;top:-90px;bottom:-150px;background:linear-gradient(to bottom,rgb(var(--dk)/.76) 0,rgb(var(--dk)/.74) calc(100% - 190px),rgb(var(--dk)/0) 100%)}
.band.lk.pic .bc::before{top:-80px;bottom:-70px;background:rgb(var(--dk)/.8)}
.bc>*{position:relative}
.band .lab{margin-bottom:20px}
.band h2.big{font-size:80px;line-height:70px;width:87.3264%;text-wrap:balance}
.band .lead{font-size:24px;line-height:30px;font-weight:300;width:66.1017%;margin:40px 0 0 33.8983%}
.figs{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));column-gap:1.6949%;row-gap:40px;margin-top:60px}
.figs b{display:block;font-size:80px;line-height:70px;font-weight:400}
.figs span{display:block;margin-top:10px;max-width:274px}
.biglinks{display:flex;flex-wrap:wrap;gap:30px 1.6949%;margin-top:40px}
.biglinks a{display:flex;gap:20px;align-items:flex-start;font-size:40px;line-height:40px;min-width:32.2%;overflow-wrap:anywhere;transition:color .1s cubic-bezier(.25,.46,.45,.94)}
.biglinks .ci{margin-top:4px}
.biglinks a:hover,.lks a:hover .ti{color:var(--acc-d)}
.lks{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));column-gap:2.0408%;row-gap:30px;margin-left:16.9492%}
.lks a{display:flex;gap:20px;align-items:flex-start}
.lks .ci{margin-top:4px}
.lks .ti{display:block;font-size:40px;line-height:40px;transition:color .1s cubic-bezier(.25,.46,.45,.94)}
.lks .de{display:block;font-size:14px;line-height:20px;margin-top:10px}

/* drawers (questions, price groups) */
.acs{margin-left:16.9492%;width:57.6389%}
.ac{margin-bottom:22px}
.ac summary{display:flex;gap:20px;align-items:flex-start;cursor:pointer;list-style:none;font-size:40px;line-height:40px;transition:color .1s cubic-bezier(.25,.46,.45,.94)}
.ac summary::-webkit-details-marker{display:none}
.ac summary .ci{margin-top:4px;transition:transform .2s cubic-bezier(.77,0,.175,1)}
.ac[open] summary .ci{transform:rotate(180deg)}
.ac summary:hover{color:var(--link)}
.ac .bd{padding:20px 0 28px 52px}
.ac .bd>p{margin-bottom:24px}
.row{display:grid;grid-template-columns:minmax(0,1fr) auto;column-gap:24px;padding-bottom:18px}
.row .nm{font-size:20px;line-height:24px}
.row a.nm:hover{color:var(--link)}
.row .pr{font-size:20px;line-height:24px;text-align:right;white-space:nowrap}
.row .meta{grid-column:1/-1}
.row .nt{grid-column:1}
.row .nt.pn{grid-column:1/-1;text-align:right}
.row .st{grid-column:2;text-align:right}
.row ul{grid-column:1/-1;font-size:14px;line-height:20px;color:var(--meta)}

/* cards in three columns */
.cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));column-gap:1.6949%;row-gap:40px}
.card h3{font-size:40px;line-height:40px;max-width:73.85%;overflow-wrap:break-word}
.card p{margin-top:10px}
.cards.sp .card{display:grid;grid-row:span 3;grid-template-rows:subgrid;row-gap:0}
.cards.sp h3{align-self:end;margin-bottom:10px}
.cards.sp .im{overflow:hidden}
.cards.sp .im img{width:100%;height:100%;object-fit:cover}
.cards.sp p{margin-top:8px}
.plan .pn.mk{color:var(--link)}
.plan .pp{font-size:80px;line-height:70px;margin-top:20px}
.plan .pp small{font-size:20px;line-height:20px;margin-left:8px}
.plan ul{margin-top:20px}
.plan li{margin-bottom:6px}
.plan .more{margin-top:24px}

/* people, credentials: two columns from the third column on */
.two{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));column-gap:2.0408%;row-gap:50px;margin-left:16.9492%}
.two .pe>div{padding-right:8%}
.two.one{grid-template-columns:minmax(0,1fr)}
.two.one .ph{width:21.2%}
.pe{display:flex;gap:4.1%;align-items:flex-start}
.pe .ph{width:37.5%;max-width:176px;aspect-ratio:4/5;flex:none;overflow:hidden}
.pe .ph img{width:100%;height:100%;object-fit:cover}
.pe .bdg{width:88px;flex:none}
.pe h3{font-size:40px;line-height:40px;overflow-wrap:break-word}
.pe .ro{font-size:20px;line-height:20px;margin-top:10px}
.pe .tx{margin-top:10px}
.pe .ct{margin-top:8px;font-size:14px;line-height:20px}
.pe a.h:hover{color:var(--link)}
.sub{font-size:20px;line-height:20px;margin:0 0 30px 16.9492%}
.two+.sub{margin-top:60px}
.qs{margin:0 0 0 25.4237%;width:66.1017%}
.qs blockquote{font-size:24px;line-height:30px;font-weight:300;margin-bottom:20px}
.qs figure{margin-bottom:60px}
.qs figcaption{font-size:20px;line-height:20px}

/* foot */
.ft-m{background:var(--grey);padding:40px 0 45px}
.ft-m.gap{margin-top:100px}
.ft-g{display:grid;grid-template-columns:23.7% 15.2% 23.7%;column-gap:1.7%;margin-left:16.9492%}
.ft h2{font-size:20px;line-height:20px;margin-bottom:10px;font-weight:400}
.ft li{font-family:"League Gothic","Arial Narrow",Impact,sans-serif;letter-spacing:.012em;font-size:20px;line-height:20px;margin-bottom:10px;overflow-wrap:anywhere}
.ft li a:hover{color:var(--link)}
.ft li small{font-size:inherit;color:var(--meta)}
.ft-b{padding:30px 0 100px}
.ft-b .ft-g{align-items:start}
.ft-b p,.ft-b li{font-family:"League Gothic","Arial Narrow",Impact,sans-serif;letter-spacing:.012em;text-transform:uppercase;font-size:20px;line-height:20px;margin:0;color:var(--meta)}
.ft-b p+p{margin-top:10px}
.ft-b a:hover{color:var(--ink)}
.ft-logo{width:auto;height:64px;margin-bottom:20px}
.tt{position:fixed;left:0;right:0;bottom:0;z-index:28;background:var(--paper);padding:15px 0 30px;transform:translateY(100%);transition:transform .5s cubic-bezier(.25,.46,.45,.94);display:none}
.js .tt{display:block}
.tt.in{transform:none}
.tt a{float:right;position:relative;padding-right:42px;font-size:20px;line-height:20px}
.tt .ci{position:absolute;right:0;top:-6px}
.tt a:hover .ci{background:var(--ink)}
.tt a:hover .ci svg{stroke:var(--paper)}

/* things rise 50px into place as they enter (only when scripts run) */
.js .rv{opacity:0;transform:translateY(50px)}
.js .rv.in{opacity:1;transform:none;transition:opacity .4s cubic-bezier(.25,.46,.45,.94) var(--d,0s),transform .4s cubic-bezier(.25,.46,.45,.94) var(--d,0s)}
.js a.t.rv.in .im{transition:transform .1s ease-in}

@media (max-width:1000px){.hd-ph{display:none}}
@media (max-width:800px){
 .wrap{width:90vw}
 .hero{height:600px;margin-bottom:45px}
 .ht{bottom:auto;top:100px}
 .ht::before{left:-5vw;right:-5vw;top:-100px;bottom:-140px;background:linear-gradient(to bottom,rgb(var(--dk)/.76) 0,rgb(var(--dk)/.74) calc(100% - 160px),rgb(var(--dk)/0) 100%)}
 .hero .top{display:none}
 .hero h1{font-size:60px;line-height:55px}
 .hero p{width:65.5172%;margin-left:34.4828%}
 .hero .more{margin-left:34.4828%}
 .hero.plain{padding-top:110px}
 .t h3{font-size:40px;line-height:40px}
 .t .tx{margin-top:20px}
 .band.pic .bc::before,.band.lk.pic .bc::before{left:-5vw;right:-5vw}
 .band h2.big{font-size:60px;line-height:55px;width:100%}
 .figs b{font-size:60px;line-height:55px}
 .acs{margin-left:0;width:100%}
 .two,.lks{margin-left:0;grid-template-columns:repeat(2,minmax(0,1fr));column-gap:6%}
 .sub{margin-left:0}
 .man,.qs,.intro{margin-left:0;width:100%}
 .mn ol{margin-left:0;padding-top:160px}
 .ft-g{margin-left:0;grid-template-columns:repeat(3,minmax(0,1fr));column-gap:4%}
 .tt{padding-bottom:15px}
}
@media (max-width:500px){
 .hd-bar,.hd .wrap{height:50px}
 .brand{top:15px;max-width:calc(100% - 100px)}
 .hd-r{top:9px;gap:10px}
 .hd-r>*{padding:0;width:32px;height:32px;font-size:0;line-height:0;color:inherit}
 .hd-r .ci{top:0}
 .hero{height:100vh;height:100svh;min-height:560px}
 .hero h1{font-size:40px;line-height:40px;width:100%;margin-bottom:20px;letter-spacing:-.2px}
 .hero p{font-size:22px;line-height:27px;width:100%;margin-left:0}
 .hero .more{margin:20px 0 0}
 .hero.plain{height:auto;min-height:0;padding-top:100px}
 .hero.plain h1{margin-left:0;width:100%;margin-bottom:40px;line-height:1}
 .hero.plain p,.hero.plain .more{margin-left:0}
 .sec{margin-bottom:80px}
 .intro{margin-bottom:80px}
 .lab{margin-bottom:40px}
 .lab.tight{margin-bottom:25px}
 .lab+.man{margin-top:-15px}
 .man{font-size:22px;line-height:27px;margin-bottom:40px}
 .t{display:block;margin:0 0 45px!important}
 .t .im{display:none}
 .t .tx{margin:0!important;text-align:left!important}
 .t h3{font-size:30px;line-height:30px}
 .t .tx p{margin-bottom:20px}
 .band{padding:60px 0 120px;margin-bottom:80px}
 .band.fig{padding-bottom:120px}
 .band.plain,.band.lk{padding:60px 0 50px}
 .band.pic .bc::before{top:-60px;bottom:-110px;background:linear-gradient(to bottom,rgb(var(--dk)/.78) 0,rgb(var(--dk)/.76) calc(100% - 110px),rgb(var(--dk)/0) 100%)}
 .band.lk.pic .bc::before{top:-60px;bottom:-50px}
 .band h2.big{font-size:40px;line-height:40px}
 .band .lead{font-size:22px;line-height:27px;width:100%;margin:20px 0 0}
 .figs{grid-template-columns:repeat(2,minmax(0,1fr));column-gap:6%;row-gap:30px;margin-top:40px}
 .figs b{font-size:40px;line-height:40px}
 .biglinks{display:block;margin-top:40px}
 .biglinks a{font-size:30px;line-height:30px;margin-bottom:20px}
 .biglinks .ci,.lks .ci,.ac summary .ci{margin-top:-1px}
 .lks,.two{display:block}
 .lks a{margin-bottom:26px}
 .lks .ti{font-size:30px;line-height:30px}
 .two>*{margin-bottom:40px}
 .ac summary{font-size:30px;line-height:30px}
 .ac .bd{padding-left:0}
 .cards{display:block}
 .cards>*{margin-bottom:50px}
 .cards.sp .card{display:block}
 .card h3,.pe h3{font-size:30px;line-height:30px}
 .plan .pp{font-size:60px;line-height:55px}
 .qs blockquote{font-size:22px;line-height:27px}
 .mn ol{display:block;padding:100px 0 60px}
 .mn li{min-height:0;margin-bottom:40px}
 .mn li a{font-size:30px;line-height:30px}
 .ft-g{grid-template-columns:repeat(2,minmax(0,1fr));row-gap:30px}
 .ft-b{padding-bottom:80px}
 .ft-b .ft-g{display:block}
 .ft-b .ft-g>*{margin-bottom:30px}
}
@media (prefers-reduced-motion:reduce){
 *,*::before,*::after{transition:none!important;animation:none!important;scroll-behavior:auto!important}
 .js .rv{opacity:1;transform:none}
 a.t:hover .im{transform:none}
}
"""

JS = r"""
(function(){var R=document.documentElement,h=document.querySelector('.hero.pic'),mb=document.querySelector('.mb'),mn=document.getElementById('menu');
function past(){R.classList.toggle('past',!h||scrollY>h.offsetHeight-40)}
addEventListener('scroll',past,{passive:true});addEventListener('resize',past);past();
function set(o){R.classList.toggle('open',o);mb.setAttribute('aria-expanded',o);mb.setAttribute('aria-label',o?mb.dataset.c:mb.dataset.o);if(mn){mn.setAttribute('aria-hidden',!o);if(o){var a=mn.querySelector('a');a&&setTimeout(function(){a.focus()},60)}}}
if(mb&&mn){mb.addEventListener('click',function(e){e.preventDefault();set(!R.classList.contains('open'))});
 addEventListener('keydown',function(e){if(e.key==='Escape'&&R.classList.contains('open')){set(false);mb.focus()}});
 mn.addEventListener('click',function(e){if(e.target.closest('a'))set(false)})}
var rv=[].slice.call(document.querySelectorAll('.rv'));
if(!('IntersectionObserver' in window)||matchMedia('(prefers-reduced-motion:reduce)').matches){rv.forEach(function(e){e.classList.add('in')})}
else{var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{rootMargin:'0px 0px -12% 0px'});rv.forEach(function(e){io.observe(e)});
 var f=document.querySelector('.ft'),tt=document.querySelector('.tt');if(f&&tt)new IntersectionObserver(function(es){tt.classList.toggle('in',es[0].isIntersecting)}).observe(f)}
var tl=document.querySelector('.tt a');tl&&tl.addEventListener('click',function(e){e.preventDefault();scrollTo({top:0,behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'auto':'smooth'})});
})();
"""


def render(d: dict) -> str:
    g = lambda o, *ks: (lambda v: v)(_get(o, ks))
    lang = (d.get('lang') or 'en')[:2].lower()
    ui = lambda k: UI[k].get(lang, UI[k]['en'])
    brand = d.get('brand') or {}
    pal = d.get('palette') or {}
    paper, ink, acc = _rgb(pal.get('ground') or '#ffffff'), _rgb(pal.get('ink') or '#000000'), _rgb(pal.get('accent') or pal.get('ink') or '#000000')
    if _con(paper, ink) < 7: ink = _toward(ink, (0, 0, 0) if _lum(paper) > .4 else (255, 255, 255), paper, 7)
    base = ink if _lum(ink) < _lum(paper) else paper
    dark = _toward(base, (0, 0, 0), (255, 255, 255), 16)
    link = acc if _con(acc, paper) >= 4.5 else _toward(acc, ink, paper, 4.5)
    grey = _mix(paper, ink, .06)
    if _con(link, grey) < 4.5: link = _toward(link, ink, grey, 4.5)
    meta = _toward(_mix(ink, paper, .3), ink, grey, 4.6)
    acc_d = _toward(acc, (255, 255, 255), dark, 4.6)

    # ---------- pictures: the client's own photographs, each once ----------
    media = d.get('media') or {}
    photos = [p for p in (media.get('photos') or []) if p.get('src') and p.get('w') and p.get('h')]
    by_src = {p['src']: p for p in photos}
    used = set()
    def take(src):
        p = by_src.get(src)
        if not p or src in used: return None
        used.add(src); return p
    steps = d.get('steps') or {}
    step_items = [dict(it, _p=take(it.get('img'))) for it in (steps.get('items') or []) if it.get('title') or it.get('text')]
    place = d.get('place') or {}
    spaces = [dict(s, _p=take(s.get('img'))) for s in (place.get('spaces') or []) if s.get('title') or s.get('text')]
    team = d.get('team') or {}
    tgroups = team.get('groups') or ([{'t': '', 'items': team.get('items')}] if team.get('items') else [])
    tgroups = [{'t': gr.get('t') or '', 'items': [dict(p, _p=take(p.get('img'))) for p in (gr.get('items') or []) if p.get('name')]} for gr in tgroups]
    tgroups = [gr for gr in tgroups if gr['items']]
    for gr in (d.get('catalogue') or {}).get('groups') or []:
        for it in gr.get('items') or []: used.add(it.get('img'))
    wide = sorted([p for p in photos if p['src'] not in used and not p.get('small') and p['w'] >= 1100 and p['w'] / p['h'] >= 1.2
                   and p.get('role') not in ('portrait', 'product')], key=lambda p: -p['w'])
    slot = {}
    for name in ('hero', 'close', 'statement', 'links'):
        if wide: slot[name] = wide.pop(0); used.add(slot[name]['src'])
    rooms = [p for p in photos if p['src'] not in used and p.get('role') in ('room', 'bar', 'exterior', 'workshop', 'detail')]

    def bg(name):
        p = slot.get(name)
        return _img(p, 'bg', slot=name, lazy=name != 'hero') if p else ''

    out = []
    # ---------- header and menu ----------
    nav = [n for n in (d.get('nav') or []) if n.get('t') and n.get('h')]
    cta = d.get('cta') or {}
    phone = (place.get('phone') or {}) or ((d.get('contact') or {}).get('phone') or {})
    home = brand.get('home') or '#top'
    hd = [f'<a class="brand c" href="{_a(home)}">{_e(brand.get("name") or "")}</a>']
    if phone.get('t') and phone.get('h'): hd.append(f'<a class="hd-ph c" href="{_a(phone["h"])}">{_e(phone["t"])}</a>')
    r = []
    if cta.get('t') and cta.get('h'): r.append(f'<a class="c" href="{_a(cta["h"])}">{_e(cta["t"])}{_ci("go")}</a>')
    if nav: r.append(f'<a class="mb c" href="#foot" role="button" aria-expanded="false" aria-controls="menu" aria-label="{_a(ui("menu"))}" data-o="{_a(ui("menu"))}" data-c="{_a(ui("close"))}">{_e(ui("menu"))}{_ci("dots")}{_ci("x")}</a>')
    hd.append('<div class="hd-r">' + ''.join(r) + '</div>')
    out.append('<div class="hd-bar"></div><header class="hd"><div class="wrap">' + ''.join(hd) + '</div></header>')
    if nav:
        items = nav + ([d['signin']] if (d.get('signin') or {}).get('t') and d['signin'].get('h') else [])
        rows = (len(items) + 1) // 2
        out.append(f'<nav class="mn" id="menu" aria-hidden="true" aria-label="{_a(ui("menu"))}"><div class="wrap"><ol style="--rows:{rows}">'
                   + ''.join(f'<li><span class="c">{i + 1:02d}</span><a class="c" href="{_a(n["h"])}">{_e(n["t"])}</a></li>' for i, n in enumerate(items)) + '</ol></div></nav>')

    out.append('<main id="main">')
    # ---------- opening ----------
    hero = d.get('hero') or {}
    title = hero.get('title') or brand.get('name') or ''
    pr = hero.get('primary') or {}
    hpic = slot.get('hero')
    out.append(f'<section class="hero {"pic" if hpic else "plain"}" id="top">{bg("hero")}{"<div class=top></div>" if hpic else ""}<div class="wrap"><div class="ht">'
               f'<h1 class="c">{_e(title)}</h1>' + (f'<p>{_e(hero["text"])}</p>' if hero.get('text') else '') + _more(pr.get('t'), pr.get('h')) + '</div></div></section>')
    sec = hero.get('secondary') or {}
    if hero.get('text2') or hero.get('note'):
        out.append('<div class="wrap"><div class="intro rv">' + (f'<p>{_e(hero["text2"])}</p>' if hero.get('text2') else '')
                   + (f'<p class="meta">{_e(hero["note"])}</p>' if hero.get('note') else '') + _more(sec.get('t'), sec.get('h')) + '</div></div>')

    def label(t, tight=False, text=''):
        s = f'<h2 class="lab c{" tight" if tight and not text else ""}">{_e(t)}</h2>' if t else ''
        return s + (f'<p class="man">{_e(text)}</p>' if text else '')

    # ---------- steps: the staggered teasers ----------
    if step_items:
        h = ['<section class="sec"><div class="wrap">', label(steps.get('title'), True, steps.get('text') or '')]
        for i, it in enumerate(step_items):
            p, kind = it['_p'], 'abca'[i % 4]
            c = it.get('cta') or {}
            im = ''
            if p:
                ar = _clamp(p['w'] / p['h'], .79, 1.6)
                if kind == 'b' and not p.get('small') and p['h'] >= 600: ar = .791   # the reference's second teaser is its upright one (371×469)
                st = f'aspect-ratio:{ar:.4f};width:100%' + (f';max-width:{p["w"]}px' if p.get('small') or p['w'] < 700 else '')
                im = f'<div class="im" style="{st}">{_img(p, slot="step")}</div>'
            tx = ('<div class="tx">' + (f'<h3 class="c">{_e(it.get("title") or "")}</h3>' if it.get('title') else '') + (f'<p>{_e(it["text"])}</p>' if it.get('text') else '')
                  + (f'<span class="more">{_e(c["t"])}{ARROW}</span>' if c.get('t') and c.get('h') else '') + '</div>')
            cls = f't k{kind} rv' + ('' if p else ' nopic')
            h.append(f'<a class="{cls}" href="{_a(c["h"])}">{im}{tx}</a>' if c.get('h') else f'<div class="{cls}">{im}{tx}</div>')
        h.append('</div></section>'); out.append(''.join(h))

    # ---------- statement (+ figures): a picture band ----------
    st = d.get('statement') or {}
    figs = [f for f in (d.get('figures') or []) if f.get('v')]
    if st.get('title') or st.get('text') or figs:
        pic = slot.get('statement')
        h = [f'<section class="band {"pic" if pic else "plain"}{" fig" if figs else ""}">{bg("statement")}<div class="wrap"><div class="bc rv">']
        if st.get('title'): h.append(f'<h2 class="big c">{_e(st["title"])}</h2>')
        if st.get('text'): h.append(f'<p class="lead">{_e(st["text"])}</p>')
        if figs: h.append('<dl class="figs">' + ''.join(f'<div><dt class="c"><b>{_e(f["v"])}</b></dt><dd><span>{_e(f.get("l") or "")}</span></dd></div>' for f in figs) + '</dl>')
        h.append('</div></div></section>'); out.append(''.join(h))

    def acc_item(summary, body, open_=False):
        return f'<details class="ac rv"{" open" if open_ else ""}><summary class="c">{_ci("down")}<span>{_e(summary)}</span></summary><div class="bd">{body}</div></details>'

    # ---------- catalogue: what is offered and what it costs, in the reference's drawers ----------
    cat = d.get('catalogue') or {}
    cgroups = [gr for gr in (cat.get('groups') or []) if gr.get('items') or gr.get('text')]
    if cgroups:
        h = ['<section class="sec" id="prices"><div class="wrap">', label(cat.get('title'), False, cat.get('text') or ''), '<div class="acs">']
        for gr in cgroups:
            b = [f'<p>{_e(gr["text"])}</p>'] if gr.get('text') else []
            for it in gr.get('items') or []:
                if not it.get('name'): continue
                nm = f'<a class="nm c" href="{_a(it["h"])}">{_e(it["name"])}</a>' if it.get('h') else f'<span class="nm c">{_e(it["name"])}</span>'
                rw = [nm, f'<span class="pr c">{_e(it.get("price") or "")}</span>']
                if it.get('note') or it.get('state'):
                    rw.append((f'<span class="meta nt pn">{_e(it["note"])}</span>' if it.get('note') and it.get('price') else f'<span class="meta nt">{_e(it.get("note") or "")}</span>')
                              + (f'<span class="meta st" style="grid-column:1/-1">{_e(it["state"])}</span>' if it.get('state') else ''))
                for pp in it.get('prices') or []:
                    rw.append(f'<span class="meta nt">{_e(pp.get("label") or "")}</span><span class="pr c">{_e(pp.get("price") or "")}</span>')
                if it.get('text'): rw.append(f'<span class="meta">{_e(it["text"])}</span>')
                if it.get('rows'): rw.append('<ul>' + ''.join(f'<li>{_e(x)}</li>' for x in it['rows']) + '</ul>')
                b.append('<div class="row">' + ''.join(rw) + '</div>')
            if gr.get('h') and gr.get('t'): b.append(_more(gr['t'], gr['h']))
            h.append(acc_item(gr.get('t') or cat.get('title') or '', ''.join(b), open_=len(cgroups) == 1))
        if cat.get('note'): h.append(f'<p class="meta">{_e(cat["note"])}</p>')
        h.append('</div></div></section>'); out.append(''.join(h))

    # ---------- plans (tiers) in the three-column cards ----------
    plans = d.get('plans') or {}
    pitems = [p for p in (plans.get('items') or []) if p.get('name')]
    if pitems:
        h = ['<section class="sec"><div class="wrap">', label(plans.get('title'), False, plans.get('text') or ''), '<div class="cards">']
        for i, p in enumerate(pitems):
            c = p.get('cta') or {}
            h.append(f'<div class="card plan rv" style="--d:{(i % 3) * .15:.2f}s"><h3 class="c pn{" mk" if p.get("marked") else ""}">{_e(p["name"])}</h3>'
                     + (f'<div class="pp c">{_e(p["price"])}' + (f'<small>{_e(p["per"])}</small>' if p.get('per') else '') + '</div>' if p.get('price') else '')
                     + (f'<p class="meta">{_e(p["line"])}</p>' if p.get('line') else '')
                     + ('<ul>' + ''.join(f'<li>{_e(x)}</li>' for x in p['rows']) + '</ul>' if p.get('rows') else '')
                     + (_more(c.get('t'), c.get('h')) if isinstance(c, dict) else '') + '</div>')
        h.append('</div>' + (f'<p class="meta" style="margin-top:40px">{_e(plans["note"])}</p>' if plans.get('note') else '') + '</div></section>'); out.append(''.join(h))

    # ---------- features: three columns of type ----------
    feats = d.get('features') or {}
    fitems = [f for f in (feats.get('items') or []) if f.get('t')]
    if fitems:
        out.append('<section class="sec"><div class="wrap">' + label(feats.get('title'), False, feats.get('text') or '') + '<div class="cards">'
                   + ''.join(f'<div class="card rv" style="--d:{(i % 3) * .15:.2f}s"><h3 class="c">{_e(f["t"])}</h3>' + (f'<p>{_e(f["d"])}</p>' if f.get('d') else '') + '</div>' for i, f in enumerate(fitems))
                   + '</div></div></section>')

    # ---------- the house: spaces with their pictures, then further rooms (pictures only) ----------
    if spaces:
        cells = []
        def pic(p, sl):
            ar = _clamp(p['w'] / p['h'], 1.3, 1.9)
            return f'<div class="im" style="aspect-ratio:{ar:.4f};max-width:{p["w"]}px">{_img(p, slot=sl)}</div>'
        for s in spaces:
            cells.append((f'<h3 class="c">{_e(s.get("title") or "")}</h3>', pic(s['_p'], 'space') if s['_p'] else '<div></div>', f'<p class="meta">{_e(s.get("text") or "")}</p>'))
        if all(s['_p'] for s in spaces):
            n = min(len(rooms), max(0, 6 - len(spaces)))
            while n and (len(spaces) + n) % 3: n -= 1
            for p in rooms[:n]:
                used.add(p['src']); cells.append(('<div></div>', pic(p, 'room'), '<div></div>'))
        out.append('<section class="sec"><div class="wrap"><div class="cards sp">'
                   + ''.join(f'<div class="card rv" style="--d:{(i % 3) * .15:.2f}s">{a}{b}{c}</div>' for i, (a, b, c) in enumerate(cells)) + '</div></div></section>')

    # ---------- people ----------
    if tgroups:
        h = ['<section class="sec"><div class="wrap">', label(team.get('title'), False, team.get('text') or '')]
        for gr in tgroups:
            if gr['t']: h.append(f'<h3 class="sub c">{_e(gr["t"])}</h3>')
            solo = len(gr['items']) == 1
            h.append('<div class="two one">' if solo else '<div class="two">')
            for i, p in enumerate(gr['items']):
                ph = f'<div class="ph">{_img(p["_p"], slot="portrait")}</div>' if p['_p'] else ''
                nm = f'<a class="h" href="{_a(p["h"])}">{_e(p["name"])}</a>' if p.get('h') else _e(p['name'])
                t = p.get('text') or ''
                ct = ' · '.join(x for x in [f'<a class="txtlink" href="{_a(p["phone"] if str(p["phone"]).startswith("tel:") else "tel:" + str(p["phone"]).replace(" ", ""))}">{_e(p["phone"])}</a>' if p.get('phone') else '',
                                            f'<a class="txtlink" href="mailto:{_a(p["email"])}">{_e(p["email"])}</a>' if p.get('email') else ''] if x)
                h.append(f'<div class="pe rv" style="--d:{(i % 2) * .15:.2f}s">{ph}<div><h3 class="c">{nm}</h3>' + (f'<p class="ro c">{_e(p["role"])}</p>' if p.get('role') else '')
                         + (f'<p class="tx{"" if solo else " meta"}">{_e(t)}</p>' if t else '') + (f'<p class="ct">{ct}</p>' if ct else '') + '</div></div>')
            h.append('</div>')
        h.append('</div></section>'); out.append(''.join(h))

    # ---------- credentials ----------
    creds = [c for c in (d.get('credentials') or []) if c.get('t')]
    if creds:
        h = ['<section class="sec"><div class="wrap"><div class="two">']
        for i, c in enumerate(creds):
            bdg = f'<img class="bdg" src="{_a(_src(c["img"]))}" alt="" loading="lazy" data-slot="badge">' if c.get('img') else ''
            nm = f'<a class="h" href="{_a(c["h"])}">{_e(c["t"])}</a>' if c.get('h') else _e(c['t'])
            h.append(f'<div class="pe rv" style="--d:{(i % 2) * .15:.2f}s">{bdg}<div><h3 class="c">{nm}</h3>' + (f'<p class="ro c">{_e(c["year"])}</p>' if c.get('year') else '')
                     + (f'<p class="tx meta">{_e(c["text"])}</p>' if c.get('text') else '') + '</div></div>')
        h.append('</div></div></section>'); out.append(''.join(h))

    # ---------- his or her own words ----------
    quotes = [q for q in (d.get('quotes') or []) if q.get('q')]
    if quotes:
        out.append('<section class="sec"><div class="wrap"><div class="qs">' + ''.join(
            f'<figure class="rv"><blockquote>{_e(q["q"])}</blockquote>' + (f'<figcaption class="c">{_e(" · ".join(x for x in [q.get("name"), q.get("role")] if x))}</figcaption>' if q.get('name') or q.get('role') else '') + '</figure>'
            for q in quotes) + '</div></div></section>')

    # ---------- questions ----------
    faq = d.get('faq') or {}
    qitems = [q for q in (faq.get('items') or []) if q.get('q') and q.get('a')]
    if qitems:
        out.append('<section class="sec"><div class="wrap">' + label(faq.get('title')) + '<div class="acs">'
                   + ''.join(acc_item(q['q'], f'<p>{_e(q["a"])}</p>') for q in qitems) + '</div></div></section>')

    # ---------- further pages: the dark band of links ----------
    links = [l for l in (d.get('links') or []) if l.get('t') and l.get('h')]
    if links:
        pic = slot.get('links')
        out.append(f'<section class="band lk {"pic" if pic else "plain"}">{bg("links")}<div class="wrap"><div class="bc rv"><div class="lks">'
                   + ''.join(f'<a href="{_a(l["h"])}">{_ci("go")}<span><span class="ti c">{_e(l["t"])}</span>' + (f'<span class="de">{_e(l["d"])}</span>' if l.get('d') else '') + '</span></a>' for l in links)
                   + '</div></div></div></section>')

    # ---------- close: the last picture band, joined to the foot ----------
    close = d.get('close') or {}
    contact = d.get('contact') or {}
    email = place.get('email') or contact.get('email') or ''
    has_close = bool(close.get('title') or close.get('text'))
    if has_close:
        pic = slot.get('close')
        cc = close.get('cta') or {}
        bl = []
        if cc.get('t') and cc.get('h'): bl.append((cc['t'], cc['h']))
        if phone.get('t') and phone.get('h'): bl.append((phone['t'], phone['h']))
        if email: bl.append((email, 'mailto:' + email))
        out.append(f'<section class="band {"pic" if pic else "plain"}" style="margin-bottom:0">{bg("close")}<div class="wrap"><div class="bc rv">'
                   + (f'<h2 class="big c">{_e(close["title"])}</h2>' if close.get('title') else '') + (f'<p class="lead">{_e(close["text"])}</p>' if close.get('text') else '')
                   + ('<div class="biglinks">' + ''.join(f'<a class="c" href="{_a(h_)}">{_ci("go")}<span>{_e(t_)}</span></a>' for t_, h_ in bl) + '</div>' if bl else '')
                   + '</div></div></section>')
    out.append('</main>')

    # ---------- foot ----------
    foot = d.get('foot') or {}
    ad = place.get('address') or {}
    c1 = [x for x in [ad.get('street'), ' '.join(x for x in [ad.get('postcode'), ad.get('city')] if x), ad.get('region'), ad.get('country')] if x]
    c1 = [f'<li>{_e(x)}</li>' for x in c1]
    if phone.get('t') and phone.get('h'): c1.append(f'<li><a href="{_a(phone["h"])}">{_e(phone["t"])}</a>' + (f' <small>{_e(phone["note"])}</small>' if phone.get('note') else '') + '</li>')
    if email: c1.append(f'<li><a href="mailto:{_a(email)}">{_e(email)}</a></li>')
    for hh in place.get('hours') or []:
        if hh.get('days'): c1.append(f'<li>{_e(hh["days"])} <small>{_e(" – ".join(x for x in [hh.get("open"), hh.get("close")] if x))}</small></li>')
    c3 = []
    bk = place.get('booking') or {}
    form = contact.get('form') or {}
    for r_ in contact.get('routes') or []:
        if r_.get('t') and r_.get('h'): c3.append(f'<li><a href="{_a(r_["h"])}">{_e(r_["t"])}</a>' + (f' <small>{_e(r_["note"])}</small>' if r_.get('note') else '') + '</li>')
    for s in place.get('social') or []:
        if s.get('t') and s.get('h'): c3.append(f'<li><a href="{_a(s["h"])}" rel="noopener">{_e(s["t"])}</a></li>')
    head3 = form if form.get('t') and form.get('h') else (bk if bk.get('t') and bk.get('h') else (cta if cta.get('t') and cta.get('h') else {}))
    logo = f'<img class="ft-logo" src="{_a(_src(brand["logo"]))}" alt="" loading="lazy" data-slot="logo">' if brand.get('logo') else ''
    cols = [f'<div>{logo}<h2 class="c">{_e(brand.get("name") or "")}</h2><ul>{"".join(c1)}</ul></div>']
    cols.append(f'<div id="foot"><h2 class="c">{_e(ui("menu"))}</h2><ul>' + ''.join(f'<li><a href="{_a(n["h"])}">{_e(n["t"])}</a></li>' for n in nav) + '</ul></div>' if nav else '<div id="foot"></div>')
    if c3 or head3:
        cols.append('<div>' + (f'<h2 class="c"><a href="{_a(head3["h"])}">{_e(head3["t"])}</a></h2>' if head3 else '') + f'<ul>{"".join(c3)}</ul></div>')
    b1 = ''.join(f'<p>{_e(x)}</p>' for x in [foot.get('text'), foot.get('legal')] if x)
    b3 = ''.join(f'<li><a href="{_a(l["h"])}">{_e(l["t"])}</a></li>' for l in (foot.get('links') or []) if l.get('t') and l.get('h'))
    out.append(f'<footer class="ft"><div class="ft-m{"" if has_close else " gap"}"><div class="wrap"><div class="ft-g rv">{"".join(cols)}</div></div></div>'
               + (f'<div class="ft-b"><div class="wrap"><div class="ft-g rv"><div>{b1}</div><div></div><ul>{b3}</ul></div></div></div>' if b1 or b3 else '<div class="ft-b"></div>') + '</footer>')
    out.append(f'<div class="tt"><div class="wrap"><a class="c" href="#top">{_e(ui("top"))}{_ci("up")}</a></div></div>')

    vars_ = (f':root{{--paper:{_hex(paper)};--ink:{_hex(ink)};--dark:{_hex(dark)};--dk:{round(dark[0])} {round(dark[1])} {round(dark[2])};--link:{_hex(link)};'
             f'--acc-d:{_hex(acc_d)};--grey:{_hex(grey)};--meta:{_hex(meta)}}}')
    desc = hero.get('text') or st.get('text') or ''
    return ('<!doctype html><html lang="' + _a(d.get('lang') or 'en') + '" class="' + ('has-pic' if hpic else 'no-pic') + '"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{_e(brand.get("name") or title)}{" — " + _e(title) if brand.get("name") and title and title != brand.get("name") else ""}</title>'
            + (f'<meta name="description" content="{_a(desc[:300])}">' if desc else '')
            + '<script>document.documentElement.classList.add("js")</script>'
            '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@300;400&family=League+Gothic&display=swap" rel="stylesheet">'
            f'<style>{vars_}{CSS}</style></head><body><a class="skip" href="#main">{_e(brand.get("name") or "")} ↓</a>'
            + ''.join(out) + f'<script>{JS}</script></body></html>')


def _get(o, ks):
    for k in ks:
        if not isinstance(o, dict): return None
        o = o.get(k)
    return o
