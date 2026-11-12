"""innerflow — the build of https://innerflow.es (a movement studio; measured 2026-11-12 at 1440 and 390) as a template
for service businesses with their own photographs. One pure function, no file reads, no model call. See NOTES.md.

Order of the page: floating bar · pinned opening on a vertically smeared photograph · statement + intro on the light
ground · outline cards on a photograph (catalogue) · the slideshow band (steps) · ruled, numbered rows (catalogue texts,
faq) · the dark part: statement, people on pale cards, labelled quotes, film or project slideshow, plans, closing ·
foot with the name set large, address, ruled contact rows."""
import html, re

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500&family=Space+Mono&display=swap" rel="stylesheet">')
# words for controls only (aria-labels); nothing here is display copy
WORDS = {'en': ('Menu', 'Close', 'Previous', 'Next'), 'de': ('Menü', 'Schließen', 'Zurück', 'Weiter'), 'es': ('Menú', 'Cerrar', 'Anterior', 'Siguiente'),
         'fr': ('Menu', 'Fermer', 'Précédent', 'Suivant'), 'it': ('Menu', 'Chiudi', 'Precedente', 'Successivo'), 'nl': ('Menu', 'Sluiten', 'Vorige', 'Volgende'),
         'pt': ('Menu', 'Fechar', 'Anterior', 'Seguinte'), 'sr': ('Meni', 'Zatvori', 'Prethodno', 'Sledeće'), 'sl': ('Meni', 'Zapri', 'Nazaj', 'Naprej')}
HOME = {'home', 'start', 'startseite', 'inicio', 'accueil', 'početna', 'domov'}
NO_BACKDROP = {'portrait', 'people', 'product', 'dish'}


def e(s):
    return html.escape(str(s or ''), quote=True)


def _rgb(h):
    h = (h or '').strip().lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    try:
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    except Exception:
        return (128, 128, 128)


def _hex(c):
    return '#%02x%02x%02x' % tuple(max(0, min(255, round(v))) for v in c)


def _mix(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def _lum(c):
    f = lambda v: v / 3294.6 if v <= 10 else ((v / 255 + .055) / 1.055) ** 2.4
    return .2126 * f(c[0]) + .7152 * f(c[1]) + .0722 * f(c[2])


def _con(a, b):
    x, y = _lum(a), _lum(b)
    return (max(x, y) + .05) / (min(x, y) + .05)


def _theme(p):
    g, k, a = _rgb(p.get('ground') or '#ffffff'), _rgb(p.get('ink') or '#2a3537'), _rgb(p.get('accent') or p.get('ink') or '#2a3537')
    light = _lum(g) >= .2
    if light:
        G, K = g, k
        if _con(G, K) < 7:
            K = _mix(K, (0, 0, 0), .5)
        D, F, W = _mix(K, (0, 0, 0), .27), K, (255, 255, 255)        # reference: band (30,39,43) is the ink (42,53,55) taken down; the foot is the ink
    else:
        G, K = g, k
        if _con(G, K) < 7:
            K = (255, 255, 255)
        D, F, W = _mix(G, (0, 0, 0), .4), _mix(G, (0, 0, 0), .2), K
    A = a                                                            # pale accent for the dark band: the accent lifted until it reads as the reference's (213,225,194) on (30,39,43)
    t = 0.0
    while _con(A, D) < 9 and t < 1:
        t += .05
        A = _mix(a, (255, 255, 255), t)
    base = G if light else (236, 235, 230)
    cink = K if light else D
    tints = []
    for s in (.34, .14, .24, .44):                                   # one hue, four strengths (the reference's four pale card grounds, held to one family)
        c = _mix(base, a, s)
        while _con(c, cink) < 7:
            c = _mix(c, (255, 255, 255), .15)
        tints.append(_hex(c))
    return dict(G=_hex(G), K=_hex(K), D=_hex(D), F=_hex(F), W=_hex(W), A=_hex(A), Kr='%d,%d,%d' % tuple(round(v) for v in K), Dr='%d,%d,%d' % tuple(round(v) for v in D),
                Wr='%d,%d,%d' % tuple(round(v) for v in W), Gr='%d,%d,%d' % tuple(round(v) for v in _mix(G, K, .05)), tints=tints, cink=_hex(cink), light=light,
                BB=_hex(D if light else K), BF=_hex(W if light else G))


def _lnk(o):
    return (o.get('t'), o.get('h')) if isinstance(o, dict) and o.get('t') else (None, None)


def _a(t, h, cls='', extra=''):
    if not t:
        return ''
    ext = ' rel="noopener"' if h and re.match(r'https?:', h) else ''
    return '<a class="%s" href="%s"%s%s>%s</a>' % (cls, e(h or '#'), ext, extra, e(t))


def _paras(*texts, cls=''):
    return ''.join('<p%s>%s</p>' % (' class="%s"' % cls if cls else '', e(t)) for t in texts if t)


def _img(src, alt, cls='', extra='', dims=None):
    wh = ' width="%d" height="%d"' % dims if dims else ''
    return '<img class="%s" src="../../%s" alt="%s"%s loading="lazy" decoding="async"%s>' % (cls, e(src), e(alt), wh, extra)


def _price(it):
    out = []
    if it.get('price'):
        out.append(e(it['price']))
    for p in it.get('prices') or []:
        out.append('%s %s' % (e(p.get('label')), e(p.get('price'))))
    if it.get('state'):
        out.append(e(it['state']))
    return out


CSS = r'''
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--G);color:var(--K);font:400 16px/1.45 "Space Grotesk",system-ui,-apple-system,"Segoe UI",sans-serif;-webkit-font-smoothing:antialiased;overflow-x:clip}
img{display:block;max-width:100%}a{color:inherit;text-decoration:none}p{margin:0}h1,h2,h3{margin:0;font-weight:400}ul{margin:0;padding:0;list-style:none}button{font:inherit;color:inherit;background:none;border:0;padding:0;cursor:pointer}
.mono{font-family:"Space Mono",ui-monospace,Menlo,monospace}
.wrap{padding:0 80px;max-width:1600px;margin:0 auto}
:focus-visible{outline:2px solid currentColor;outline-offset:3px;border-radius:3px}
.skip{position:absolute;left:-999px}.skip:focus{left:24px;top:24px;z-index:99;background:var(--G);color:var(--K);padding:8px 12px}
/* bar: fixed 16 in, 60 high, 5 radius, tinted ground with a 15px blur behind */
.hd{position:fixed;z-index:50;top:16px;left:16px;right:16px;height:60px;border-radius:5px;background:rgba(var(--Gr),.78);-webkit-backdrop-filter:blur(15px);backdrop-filter:blur(15px);color:var(--K);display:flex;align-items:center;justify-content:space-between;padding:0 30px;gap:20px}
.hd-logo{font-size:26px;line-height:1;letter-spacing:-.02em;font-weight:500;white-space:nowrap;display:flex;align-items:center;min-width:0}.hd-logo img{height:36px;width:auto;mix-blend-mode:multiply}
.hd-r{display:flex;align-items:center;gap:20px;min-width:0}.hd-nav{display:flex;gap:20px;font-size:14px;letter-spacing:.005em;white-space:nowrap}.hd-nav a{padding:20px 0}.hd-nav a:hover{opacity:.6}
.pill{display:inline-flex;align-items:center;justify-content:center;height:25px;padding:1px 12px 0;border:1px solid currentColor;border-radius:500px;font-size:14px;line-height:1;font-weight:500;text-transform:uppercase;white-space:nowrap;transition:color .1s ease-in-out,background-color .1s ease-in-out,border-color .1s ease-in-out}
.hd .pill:hover{background:var(--K);color:var(--G);border-color:var(--K)}
.hd-tg{width:30px;height:44px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;margin-right:-10px}.hd-tg i{display:block;width:11px;height:1.5px;background:currentColor}
/* opening: one screen, pinned while the page slides over it */
.hero{position:relative;z-index:0;min-height:100vh;min-height:100svh;display:flex;align-items:flex-end;background:var(--D);color:var(--W);padding:110px 0 70px;overflow:hidden}
.js .hero{position:sticky;top:var(--ht,0px)}
.hero-pic{position:absolute;inset:0;overflow:hidden}.hero-pic img{position:absolute;left:-2%;top:-20%;width:104%;max-width:none;height:140%;object-fit:cover;filter:url(#vb) brightness(.74) saturate(.92)}
.hero-pic::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(var(--Dr),.78) 0,rgba(var(--Dr),.5) 14%,rgba(var(--Dr),.5) 82%,rgba(var(--Dr),.85) 100%)}
.hero .wrap{position:relative;width:100%}
.hero-top{display:flex;align-items:center;justify-content:space-between;gap:40px}
.hero h1{font-size:var(--h1);line-height:1;letter-spacing:-.0023em;max-width:1088px}
.hero-note{font-size:12px;line-height:18px;white-space:nowrap}
.hero-links{margin-top:clamp(40px,16.7vh,150px);display:flex;flex-direction:column;align-items:flex-start;font-size:30px;line-height:43.5px}.hero-links a:hover,.more:hover{opacity:.7}
.hero-text{margin-top:50px;max-width:648px}.hero-text p+p{margin-top:12px}
.hero-end{margin-top:50px;display:flex;align-items:flex-end;justify-content:space-between;gap:30px}
.btns{display:flex;flex-wrap:wrap;gap:15px}
.btn{display:inline-flex;align-items:center;justify-content:center;min-width:260px;height:50px;padding:0 30px;border:1px solid transparent;border-radius:500px;font-size:14px;font-weight:500;text-transform:uppercase;text-align:center;line-height:1.1;transition:color .1s ease-in-out,background-color .1s ease-in-out,border-color .1s ease-in-out}
.btn-w{background:var(--W);color:var(--D)}.btn-w:hover{background:var(--A);border-color:var(--A)}
.btn-ow{border-color:var(--W);color:var(--W)}.btn-ow:hover{background:var(--W);color:var(--D)}
.btn-k{background:var(--BB);color:var(--BF)}.btn-k:hover{background:var(--A);color:var(--D);border-color:var(--A)}
.btn-ok{border-color:var(--K);color:var(--K)}.btn-ok:hover{background:var(--K);color:var(--G);border-color:transparent}
.hero-go{font-size:16px;line-height:23.2px;white-space:nowrap;padding:4px 0}
.page>section:not(.hero),.ft{position:relative;z-index:1}
/* statement and intro on the ground */
.st{background:var(--G);padding:70px 0 43px}
.kick{font-size:15px;line-height:23.4px;letter-spacing:.7px;text-transform:uppercase}
.st h2,.big{font-size:60px;line-height:1;letter-spacing:-.0023em}
.st h2{max-width:680px;margin-top:25px}
.rule{display:flex;margin-top:100px}.rule i{flex:1;height:0;border-top:1px solid currentColor}.rule i:first-child{opacity:.25}
.two{display:grid;grid-template-columns:1fr 1fr;column-gap:40px;margin-top:50px}
.lead p{font-size:25px;line-height:35px}.lead p+p{margin-top:20px}
.st .btns{margin-top:50px}
.figs{display:flex;flex-wrap:wrap;gap:30px 50px;align-self:start}.figs b{display:block;font-weight:400;font-size:60px;line-height:1}.figs span{display:block;margin-top:10px;font-size:12px;letter-spacing:.6px;text-transform:uppercase}
.intro{margin-top:150px;align-items:start}
.bar-h{font-size:60px;line-height:1;letter-spacing:-.0023em;display:flex;align-items:flex-start}.bar-h::before{content:"";flex:none;width:11px;height:46px;background:var(--A);margin:3px 27px 0 0}
.intro h3,.h40{font-size:40px;line-height:46.8px}.intro h3+p,.intro p+p{margin-top:25px}
.more{display:inline-block;font-size:30px;line-height:43.5px;margin-top:60px}
/* outline cards on a photograph */
.gr{background:var(--F);color:#fff;padding:70px 0;overflow:hidden}
.gr-pics{position:absolute;inset:-200px 0 0 0;will-change:transform}.gr-pics img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;filter:brightness(.8);transition:opacity .3s ease-in-out}.gr-pics img+img{opacity:0}.gr-pics img.on{opacity:1}
.gr-veil{position:absolute;inset:0;background:rgba(var(--Dr),.56)}
.gr .wrap{position:relative}
.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:63px 15px}
.cards.c2{grid-template-columns:repeat(2,1fr)}.cards.c1{grid-template-columns:minmax(0,632px)}
.card{position:relative;display:block;min-height:251px;padding:25px;border:1px solid #fff;border-radius:10px;-webkit-backdrop-filter:blur(0);backdrop-filter:blur(0);transition:backdrop-filter .3s ease-in-out,-webkit-backdrop-filter .3s ease-in-out,background-color .3s ease-in-out}
.card-t{font-size:25px;line-height:35px;padding-right:34px}
.card-c{margin-top:25px;opacity:0;transition:opacity .3s ease-in-out}.card-c ul{columns:2;column-gap:40px}.card-c li{break-inside:avoid}.card-c p+p,.card-c ul+p,.card-c p+ul{margin-top:10px}
.card-x{position:absolute;right:22px;top:22px;font-size:26px;line-height:1;opacity:0;transition:opacity .3s ease-in-out}
.card:hover,.card:focus-visible,.card:focus-within{-webkit-backdrop-filter:blur(15px);backdrop-filter:blur(15px);background:rgba(var(--Dr),.28)}
.card:hover .card-c,.card:focus-visible .card-c,.card:focus-within .card-c,.card:hover .card-x,.card:focus-visible .card-x{opacity:1}
@media (hover:none){.card-c{opacity:1}.card.has{background:rgba(var(--Dr),.28)}}
/* slideshow band */
.sl{background:var(--D);color:var(--W);overflow:hidden}
.sl-pics{position:absolute;inset:0}.sl-pic{position:absolute;inset:0;overflow:hidden}.sl-pic img{width:100%;height:100%;object-fit:cover}
.sl-pic+.sl-pic{display:none}.js .sl-pic{display:block;transform:translateX(100%)}.js .sl-pic.on{transform:none}
.sl-veil{position:absolute;inset:0;background:linear-gradient(90deg,rgba(var(--Dr),.9) 0,rgba(var(--Dr),.84) 34%,rgba(var(--Dr),.3) 60%,rgba(var(--Dr),.08) 100%)}
.sl-body{position:relative;min-height:795px;padding-top:150px;padding-bottom:110px;display:flex;flex-direction:column;align-items:flex-start}
.sl-texts{display:grid;max-width:414px}.sl-text{grid-area:1/1}.js .sl-text{visibility:hidden;opacity:0;transition:opacity .3s ease-in-out,visibility 0s .3s}.js .sl-text.on{visibility:visible;opacity:1;transition:opacity .3s ease-in-out}
html:not(.js) .sl-text{grid-area:auto;margin-bottom:50px}
.sl-text p{margin-top:25px}.sl-text .go{display:inline-block;margin-top:20px;border-bottom:1px solid currentColor}
.sl-nav{display:none;gap:10px;margin-top:25px;font-size:16px;line-height:23.2px}.js .sl-nav{display:flex}.sl-nav button{padding:6px 8px;margin:-6px -8px}.sl-nav button:hover{opacity:.6}
.sl-num{display:none;gap:10px;margin-top:auto;padding-top:60px}.js .sl-num{display:flex}.sl-num b{font-weight:400;font-size:130px;line-height:1;letter-spacing:-.03em}.sl-num span{font-size:12px;line-height:1;margin-top:10px}
.sl.plain{background:var(--G);color:var(--K)}.sl.plain .sl-body{min-height:0;padding-top:150px;padding-bottom:150px}
/* ruled, numbered rows (the reference's question list) */
.fq{background:var(--G);padding:150px 0}.fq+.fq{padding-top:0}
.fq-g{display:grid;grid-template-columns:290px 1fr;column-gap:40px;align-items:start}
.fq-i{border-top:1px solid rgba(var(--Kr),.25);padding:25px 0}.fq-i:first-child{border-top:0;padding-top:0}
.fq-i summary{display:grid;grid-template-columns:100px 1fr 20px;align-items:baseline;cursor:pointer;list-style:none}.fq-i summary::-webkit-details-marker{display:none}
.fq-n{font-size:12px}.fq-q{font-size:18px;line-height:25.2px}.fq-q small{font-size:16px;margin-left:14px;white-space:nowrap}
.fq-p{position:relative;width:13px;height:13px;align-self:center;justify-self:end}.fq-p::before,.fq-p::after{content:"";position:absolute;left:0;top:6px;width:13px;height:1px;background:currentColor}.fq-p::after{transform:rotate(90deg)}.fq-i[open] .fq-p::after{display:none}
.fq-a{margin:15px 20px 0 100px;max-width:720px}.fq-a p+p,.fq-a ul{margin-top:10px}.fq-a li{padding-left:16px;position:relative}.fq-a li::before{content:"";position:absolute;left:2px;top:10px;width:4px;height:4px;border-radius:50%;background:currentColor}
.fq-row{display:grid;grid-template-columns:100px 1fr auto;align-items:baseline;column-gap:0}
/* the dark part */
.dk{background:var(--D);color:var(--W);padding:100px 0}
.dk>.wrap>:first-child{margin-top:0}
.pale{color:var(--A);max-width:983px}
.dk .bullets{font-size:18px;line-height:24.84px;text-transform:uppercase;padding-left:20px;list-style:disc}.dk .txt{font-size:18px;line-height:24.84px;max-width:524px}.dk .bullets+.txt{margin-top:25px}
.team{display:grid;grid-template-columns:repeat(4,1fr);gap:15px;margin-top:100px}
.team.c3{grid-template-columns:repeat(3,1fr)}.team.c2{grid-template-columns:repeat(2,minmax(0,417px))}.team.c1{grid-template-columns:minmax(0,417px)}
.tm{background:var(--t);color:var(--cink);border-radius:10px;padding:40px;display:flex;flex-direction:column}
.tm-pic{width:100%;overflow:hidden}.tm-pic img{width:100%;height:100%;object-fit:cover}
.tm-cap{margin-top:25px;text-align:center;font-size:15px;line-height:23.4px;letter-spacing:.7px;text-transform:uppercase}.tm-pic+.tm-cap{margin-top:25px}
.tm-role{text-align:center;font-size:14px;line-height:20px;margin-top:4px}.tm-text{margin-top:20px}.tm-more{margin-top:14px;font-size:14px}.tm-more a{border-bottom:1px solid currentColor}
.tm.type .tm-cap{margin-top:auto}
.lab{margin-top:100px;font-size:12px;line-height:18px;letter-spacing:.6px;text-transform:uppercase}.lab+.rule{margin-top:25px}
.qt{margin:0;grid-column:2}.qt p{font-size:25px;line-height:35px}.qt footer{margin-top:25px;max-width:524px}
.slot{margin-top:150px;position:relative;aspect-ratio:16/9;overflow:hidden;background:var(--F)}.slot video{width:100%;height:100%;object-fit:cover;display:block}
.slot .sl-pic img{filter:none}.slot-veil{position:absolute;z-index:1;left:0;right:0;bottom:0;height:46%;background:linear-gradient(0deg,rgba(var(--Dr),.9),rgba(var(--Dr),.62) 45%,rgba(var(--Dr),0));pointer-events:none}
.slot-cap{position:absolute;z-index:2;left:40px;right:40px;bottom:30px;display:flex;align-items:flex-end;justify-content:space-between;gap:30px;color:#fff}.slot-cap .sl-texts{max-width:none}.slot-cap .sl-text{font-size:25px;line-height:35px}
.slot-cap .sl-nav{margin:0;align-items:center;gap:16px}.slot-cap .sl-c{font-size:12px}
html:not(.js) .slot-cap .sl-text+.sl-text{display:none}
.plans-h{margin-top:150px;display:flex;justify-content:space-between;align-items:flex-end;gap:40px}.plans-h h3{font-size:25px;line-height:35px}.plans-h p{max-width:620px}
.plans{display:grid;grid-template-columns:repeat(3,1fr);gap:15px;margin-top:40px}
.pl{position:relative;border:1px solid var(--W);border-radius:4px;padding:28px 20px 22px;text-align:center;display:flex;flex-direction:column;align-items:center}
.pl-n{text-transform:uppercase}.pl-p{font-size:40px;line-height:1.1;margin-top:8px}.pl-r{width:150px;border-top:1px solid rgba(var(--Wr),.3);margin:14px 0 10px}.pl-per,.pl-l{font-size:14px;line-height:20px}.pl-per{opacity:.8}.pl-l{margin-top:8px}
.pl ul{margin-top:10px;font-size:14px;line-height:20px}.pl li+li{margin-top:4px}.pl .pill{margin-top:18px;height:34px;padding:0 18px}.pl .pill:hover{background:var(--W);color:var(--D)}
.pl-tag{position:absolute;top:-10px;left:50%;transform:translateX(-50%);background:var(--A);color:var(--D);font-size:12px;line-height:18px;padding:0 8px;text-transform:uppercase;white-space:nowrap}
.plans-note{margin-top:20px;font-size:14px;opacity:.85}
.close{margin-top:150px;text-align:center;display:flex;flex-direction:column;align-items:center}
.close-s{display:flex;align-items:center;gap:8px;max-width:760px}.close-s::before{content:"";flex:none;width:8px;height:8px;border-radius:50%;background:currentColor}
.close h2{margin-top:25px;max-width:1000px}.close-t{margin-top:25px;max-width:648px}.close .btns{margin-top:25px;justify-content:center}
/* foot */
.ft{background:var(--F);color:var(--W)}
.ft-mark{padding:100px 0;overflow:hidden}.ft-mark div{font-size:min(213px,calc((100vw - 160px) / var(--n)));line-height:.86;letter-spacing:-.045em;white-space:nowrap;font-weight:500;color:rgba(0,0,0,.26)}
.ft-main{padding:40px 0}.ft-line{font-size:40px;line-height:46.8px;max-width:900px}
.ft-cols{display:grid;grid-template-columns:220px 220px 1fr 400px;margin-top:40px;align-items:start}
.ft-l a{display:flex;align-items:center;gap:6px;padding:1px 0;font-size:12px;line-height:17.4px;text-transform:uppercase}.ft-l a::before{content:"\2192"}.ft-l a:hover{opacity:.6}
.ft-d{grid-column:4}.ft-d .kick{margin-bottom:14px}.ft-row{display:flex;justify-content:space-between;gap:20px;min-height:34px;padding:5px 0;border-bottom:1px solid currentColor}.ft-row+.ft-row{margin-top:8px}.ft-row a:hover{opacity:.6}
.ft-loc{margin-top:26px}
.ft-end{padding:40px 0;font-size:12px;line-height:18px;color:rgba(var(--Wr),.74)}.ft-end .wrap{display:flex;flex-wrap:wrap;justify-content:space-between;gap:6px 30px}.ft-end a{text-decoration:underline;text-underline-offset:2px}.ft-end a+a{margin-left:10px}
/* menu: full screen, fades .3s linear */
.mn{position:fixed;inset:0;z-index:80;background:rgba(var(--Dr),.9);-webkit-backdrop-filter:blur(30px);backdrop-filter:blur(30px);color:#fff;opacity:0;visibility:hidden;transition:opacity .3s linear,visibility 0s .3s;overflow:auto}
.mn.on{opacity:1;visibility:visible;transition:opacity .3s linear}
.mn-in{margin-left:49.5%;padding:30px 95px 60px 0;min-height:100%}
.mn-top{display:flex;justify-content:flex-end;padding-bottom:42px;border-bottom:1px solid rgba(255,255,255,.4)}.mn-x{display:flex;align-items:center;gap:20px;font-size:14px}.mn-x::after{content:"\00d7";font-size:44px;line-height:26px;font-weight:400}
.mn ul{margin-top:20px}.mn li a{display:block;font-size:18px;line-height:35.3px}.mn li a:hover{opacity:.6}
.mn-s{margin-top:34px;font-size:18px}.mn-s a::before{content:"\2192\00a0\00a0"}.mn .btn{margin-top:40px}
/* reveals: fade .5s ease-out, with a 50px rise or a 10px drop, 200ms apart */
@keyframes f{from{opacity:0}to{opacity:1}}@keyframes up{from{transform:translateY(50px)}to{transform:none}}@keyframes dn{from{transform:translateY(-10px)}to{transform:none}}
.js.mo .r{opacity:0}.js.mo .r.in{opacity:1;animation:f .5s ease-out var(--dl,0s) both}.js.mo .r.up.in{animation:f .5s ease-out var(--dl,0s) both,up .5s ease-out var(--dl,0s) both}.js.mo .r.dn.in{animation:f .5s ease-out var(--dl,0s) both,dn .5s ease-out var(--dl,0s) both}
@media (max-width:1180px){.hd-nav{display:none}.cards{grid-template-columns:repeat(2,1fr)}.team{grid-template-columns:repeat(3,1fr)}.ft-cols{grid-template-columns:180px 180px 1fr 360px}}
@media (max-width:959px){
.wrap{padding:0 16px}.hd{top:12px;padding:0 16px}.hd .pill{display:none}.hd-logo{font-size:20px}.hd-logo img{height:30px}.hd-tg{margin-right:-6px}
.hero{padding:100px 0 40px}.hero h1{font-size:var(--h1m)}.hero-note{display:none}.hero-links{font-size:28px;line-height:40.6px;margin-top:clamp(30px,8.4vh,71px)}.hero-text{margin-top:50px}.hero .btns{display:none}.hero-end{justify-content:flex-start}
.st{padding:40px 0}.kick{font-size:12px;line-height:18.72px}.st h2,.big{font-size:35px}.rule{margin-top:40px}.rule i+i{display:none}.two{grid-template-columns:1fr;row-gap:30px}.two>.empty{display:none}
.lead p{font-size:16px;line-height:22.4px}.btn{min-width:260px}.btns{flex-direction:column;align-items:flex-start}
.intro{margin-top:70px}.bar-h{font-size:35px}.bar-h::before{width:7px;height:28px;margin:2px 14px 0 0}.intro h3,.h40{font-size:25px;line-height:29.25px}.more{font-size:18px;line-height:26.1px;margin-top:16px}
.gr{padding:40px 0}.cards{gap:40px 15px}.card{min-height:93px;padding:10px;-webkit-backdrop-filter:none;backdrop-filter:none}.card-t{font-size:16px;line-height:22.4px;padding-right:0}.card-x{display:none}.card.has{grid-column:1/-1;padding:14px}.card-c{margin-top:12px;opacity:1}.card.has{background:rgba(var(--Dr),.28)}
.sl{background:var(--G);color:var(--K);padding:50px 0}.sl-body{min-height:0;padding-top:0;padding-bottom:0}.sl-texts{max-width:none}.sl-pics{position:relative;inset:auto;height:300px;margin:50px 16px 0;overflow:hidden}.sl-veil,.sl-num{display:none!important}.sl{display:flex;flex-direction:column}.sl .wrap{order:-1;width:100%}
.sl.plain .sl-body{padding-top:0;padding-bottom:0}
.fq{padding:50px 0}.fq-g{grid-template-columns:1fr;row-gap:30px}.fq-i summary,.fq-row{grid-template-columns:40px 1fr 20px}.fq-a{margin-left:40px}
.dk{padding:40px 0}.dk .bullets{font-size:16px;line-height:22.08px}.dk .bullets li+li{margin-top:10px}
.team{display:flex;gap:15px;margin:60px -16px 0;padding:0 16px;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none}.team::-webkit-scrollbar{display:none}.tm{flex:none;width:83%;max-width:296px;padding:30px;scroll-snap-align:center}.tm-cap{font-size:12px;line-height:18.72px}
.lab{margin-top:60px}.qt{grid-column:1}.qt p{font-size:16px;line-height:22.4px}
.slot{margin-top:70px;aspect-ratio:16/9!important}.slot-cap{left:14px;right:14px;bottom:12px}.slot-cap .sl-text{font-size:16px;line-height:22.4px}.slot-veil{height:60%}
.plans-h{margin-top:70px;flex-direction:column;align-items:flex-start;gap:10px}.plans{grid-template-columns:1fr}
.close{margin-top:88px}.close .btns{align-items:center}
.ft{display:flex;flex-direction:column}.ft-mark{order:2;padding:40px 0 0}.ft-mark div{font-size:min(60px,calc((100vw - 32px) / var(--n)))}.ft-end{order:3}
.ft-line{font-size:25px;line-height:29.25px}.ft-cols{grid-template-columns:1fr 1fr;row-gap:40px}.ft-d{grid-column:1/-1}
.mn-in{margin-left:0;padding:22px 16px 50px}
}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}.js .hero{position:relative;top:0}html{scroll-behavior:auto}}
'''

JS = r'''
(function(){var d=document,h=d.documentElement,rm=matchMedia('(prefers-reduced-motion:reduce)').matches;h.classList.add('js');if(!rm)h.classList.add('mo');
var $=function(s,c){return (c||d).querySelector(s)},$$=function(s,c){return [].slice.call((c||d).querySelectorAll(s))};
/* opening stays pinned while the page slides over it; a taller-than-screen opening scrolls to its end first */
var hero=$('.hero');function fit(){if(hero)h.style.setProperty('--ht',Math.min(0,innerHeight-hero.offsetHeight)+'px')}fit();addEventListener('resize',fit);addEventListener('load',fit);
/* reveals */
var rs=$$('.r');if(!rm&&'IntersectionObserver' in window){var io=new IntersectionObserver(function(en){var k=0;en.forEach(function(x){if(x.isIntersecting){x.target.style.setProperty('--dl',(k++*.2)+'s');x.target.classList.add('in');io.unobserve(x.target)}})},{rootMargin:'0px 0px -4% 0px'});rs.forEach(function(x){io.observe(x)})}else rs.forEach(function(x){x.classList.add('in')});
/* scroll-linked: opening links drift up 18px; the card photograph travels 200px across its passage (linear, as measured) */
var hl=$$('.hero-links,.hero-text'),gp=$('.gr-pics'),gr=$('.gr'),tick=0;
function onS(){tick=0;var y=scrollY;if(hl.length&&y<1200){var t=-18*Math.min(1,y/400);hl.forEach(function(x){x.style.transform='translateY('+t.toFixed(1)+'px)'})}
if(gp){var r=gr.getBoundingClientRect();if(r.bottom>-50&&r.top<innerHeight+50){var p=Math.max(0,Math.min(1,(innerHeight-r.top)/(r.height+innerHeight)));gp.style.transform='translateY('+(p*200).toFixed(1)+'px)'}}}
if(!rm){addEventListener('scroll',function(){if(!tick)tick=requestAnimationFrame(onS)},{passive:true});onS()}
/* a card with its own photograph puts it behind the whole grid */
$$('.card[data-i]').forEach(function(c){var im=$('.gr-pics img[data-i="'+c.getAttribute('data-i')+'"]');if(!im)return;function on(){$$('.gr-pics img.on').forEach(function(x){x.classList.remove('on')});im.classList.add('on')}c.addEventListener('mouseenter',on);c.addEventListener('focus',on)});
/* slideshows: the incoming picture pushes the old one out sideways, .75s, decelerating; no autoplay */
$$('[data-sl]').forEach(function(s){var ps=$$('.sl-pic',s),ts=$$('.sl-text',s),n=Math.max(ps.length,ts.length),num=$('[data-n]',s),i=0;if(n<2)return;
function go(j,dir){j=(j+n)%n;if(j===i)return;var a=ps[i],b=ps[j];if(a&&b){var T=rm?'none':'transform .75s cubic-bezier(.165,.84,.44,1)';b.style.transition='none';b.style.transform='translateX('+(dir*100)+'%)';b.classList.add('on');b.offsetWidth;b.style.transition=T;a.style.transition=T;b.style.transform='translateX(0)';a.style.transform='translateX('+(-dir*100)+'%)';a.classList.remove('on')}
if(ts[i])ts[i].classList.remove('on');if(ts[j])ts[j].classList.add('on');i=j;if(num)num.textContent=(j<9?'0':'')+(j+1)}
$$('[data-go]',s).forEach(function(b){b.addEventListener('click',function(){var k=+b.getAttribute('data-go');go(i+k,k)})});
var x0=null;s.addEventListener('touchstart',function(ev){x0=ev.touches[0].clientX},{passive:true});s.addEventListener('touchend',function(ev){if(x0===null)return;var dx=ev.changedTouches[0].clientX-x0;x0=null;if(Math.abs(dx)>50)go(i+(dx<0?1:-1),dx<0?1:-1)},{passive:true})});
/* menu */
var mn=$('.mn'),tg=$('.hd-tg'),mx=$('.mn-x');if(mn&&tg){function set(o){mn.classList.toggle('on',o);tg.setAttribute('aria-expanded',o);if(o){mn.removeAttribute('inert');mx.focus()}else{mn.setAttribute('inert','');tg.focus()}d.body.style.overflow=o?'hidden':''}
mn.setAttribute('inert','');tg.addEventListener('click',function(){set(true)});mx.addEventListener('click',function(){set(false)});d.addEventListener('keydown',function(ev){if(ev.key==='Escape'&&mn.classList.contains('on'))set(false)});$$('a',mn).forEach(function(a){a.addEventListener('click',function(){set(false)})})}
})();
'''


def render(d: dict) -> str:
    lang = (d.get('lang') or 'en')[:2].lower()
    w_menu, w_close, w_prev, w_next = WORDS.get(lang, WORDS['en'])
    T = _theme(d.get('palette') or {})
    brand = d.get('brand') or {}
    name = brand.get('name') or ''
    hero = d.get('hero') or {}
    place = d.get('place') or {}
    contact = d.get('contact') or {}
    media = d.get('media') or {}
    photos = [p for p in (media.get('photos') or []) if p.get('src')]
    by_src = {p['src']: p for p in photos}

    def dims(src):
        p = by_src.get(src) or {}
        return (int(p['w']), int(p['h'])) if p.get('w') and p.get('h') else None

    def alt(src):
        return (by_src.get(src) or {}).get('alt') or ''

    # ---- data, normalised ----
    steps = d.get('steps') or {}
    step_items = [s for s in (steps.get('items') or []) if s.get('title') or s.get('text')]
    cat = d.get('catalogue') or {}
    groups = [g for g in (cat.get('groups') or []) if g.get('items')]
    cat_title, cat_text, cat_note = cat.get('title'), cat.get('text'), cat.get('note')
    feats = d.get('features') or {}
    if not groups and feats.get('items'):
        groups = [{'items': [{'name': f.get('t'), 'text': f.get('d')} for f in feats['items'] if f.get('t')]}]
        cat_title, cat_text = cat_title or feats.get('title'), cat_text or feats.get('text')
    grouped = len([g for g in groups if g.get('t')]) >= 2
    team = d.get('team') or {}
    people = list(team.get('items') or [])
    for g in team.get('groups') or []:
        people += g.get('items') or []
    people = [p for p in people if p.get('name')]
    projects = [p for p in (d.get('projects') or []) if p.get('title') and p.get('photos')]
    quotes = [q if isinstance(q, dict) else {'q': q} for q in (d.get('quotes') or [])]
    quotes = [q for q in quotes if q.get('q')]
    plans = d.get('plans') or {}
    plan_items = [p for p in (plans.get('items') or []) if p.get('name')]
    faq = d.get('faq') or {}
    faq_items = [q for q in (faq.get('items') or []) if q.get('q')]
    creds = [c for c in (d.get('credentials') or []) if c.get('t')]
    video = media.get('video') or None
    phone = place.get('phone') or contact.get('phone') or {}
    email = place.get('email') or contact.get('email')
    addr = place.get('address') or {}

    # ---- photographs: by role and size, each once ----
    used = set()
    for s in step_items:
        if s.get('img'):
            used.add(s['img'])
    for g in groups:
        if g.get('img'):
            used.add(g['img'])
        for it in g['items']:
            if it.get('img'):
                used.add(it['img'])
    for p in people:
        if p.get('img'):
            used.add(p['img'])
    for p in projects:
        used.update(x if isinstance(x, str) else (x or {}).get('src') for x in p['photos'])
    free = [p for p in photos if p['src'] not in used and not p.get('small') and p.get('role') not in NO_BACKDROP and (p.get('w') or 0) >= (p.get('h') or 0)]

    def take(minw):
        for p in free:
            if (p.get('w') or 0) >= minw:
                free.remove(p)
                return p
        return None
    hero_pic = take(1600) or take(1200)          # smeared, so a 1200 picture is enough
    grid_pic = take(1600) or take(1400)

    # ---- links that exist in the data, by address (so a "more" link carries the client's own words) ----
    known = {}
    for o in [hero.get('primary'), hero.get('secondary'), d.get('cta'), (d.get('close') or {}).get('cta')] + list(d.get('nav') or []) + list(d.get('links') or []):
        t, h_ = _lnk(o)
        if t and h_ and h_ not in known:
            known[h_] = t
    nav = [(n.get('t'), n.get('h')) for n in (d.get('nav') or []) if n.get('t')]
    nav_in = [n for n in nav if n[0].strip().lower() not in HOME and n[1] != brand.get('home')]
    cta_t, cta_h = _lnk(d.get('cta'))
    sign_t, sign_h = _lnk(d.get('signin'))
    p1_t, p1_h = _lnk(hero.get('primary'))
    p2_t, p2_h = _lnk(hero.get('secondary'))
    if not p1_t:
        p1_t, p1_h = cta_t, cta_h

    # ---- bar + menu ----
    logo = (_img(brand['logo'], name, extra=' loading="eager"').replace(' loading="lazy"', '') if brand.get('logo') else e(name))
    pills = ''
    if phone.get('t'):
        pills += _a(phone['t'], phone.get('h') or 'tel:' + re.sub(r'[^+\d]', '', phone['t']), 'pill')
    pills += _a(sign_t, sign_h, 'pill') + _a(cta_t, cta_h, 'pill')
    head = ('<header class="hd"><a class="hd-logo" href="#top" aria-label="%s">%s</a><div class="hd-r"><nav class="hd-nav" aria-label="%s">%s</nav>%s'
            '<button class="hd-tg" type="button" aria-label="%s" aria-expanded="false" aria-controls="mn"><i></i><i></i></button></div></header>'
            % (e(name), logo, e(name), ''.join(_a(t, h_) for t, h_ in nav_in[:5]), pills, e(w_menu)))
    menu = ('<div class="mn" id="mn" role="dialog" aria-modal="true" aria-label="%s"><div class="mn-in"><div class="mn-top"><button class="mn-x" type="button">%s</button></div>'
            '<ul>%s</ul>%s%s</div></div>'
            % (e(w_menu), e(w_close), ''.join('<li>%s</li>' % _a(t, h_) for t, h_ in nav),
               '<p class="mn-s">%s</p>' % _a(sign_t, sign_h) if sign_t else ('<p class="mn-s">%s</p>' % _a(phone['t'], phone.get('h') or '#') if phone.get('t') else ''),
               _a(cta_t, cta_h, 'btn btn-ow')))

    # ---- opening ----
    S = []
    title = hero.get('title') or name
    n = len(title)
    h1 = (60, 50) if n <= 34 else ((52, 40) if n <= 60 else (44, 32))
    note = ' '.join(x for x in [(addr.get('city') + '.') if addr.get('city') else '', hero.get('note') or ''] if x)
    first_target = '#about'
    S.append('<section class="hero" id="top">%s<div class="wrap"><div class="hero-top"><h1 class="r">%s</h1>%s</div>%s%s<div class="hero-end">%s%s</div></div></section>' % (
        '<div class="hero-pic">%s</div>' % _img(hero_pic['src'], hero_pic.get('alt'), extra=' data-slot="opening" fetchpriority="high"').replace(' loading="lazy"', '') if hero_pic else '',
        e(title), '<div class="hero-note mono r">%s</div>' % e(note) if note else '',
        '<div class="hero-links">%s</div>' % ''.join(_a(t + ' →', h_) for t, h_ in nav_in[:2]) if nav_in else '',
        '<div class="hero-text">%s</div>' % _paras(hero.get('text'), hero.get('text2')) if (hero.get('text') or hero.get('text2')) else '',
        '<div class="btns">%s%s</div>' % (_a(p1_t, p1_h, 'btn btn-w'), _a(p2_t, p2_h, 'btn btn-ow')) if (p1_t or p2_t) else '<span></span>',
        '<a class="hero-go r up" href="%s" aria-label="%s">↓</a>' % (first_target, e((d.get('statement') or {}).get('title') or cat_title or name))))

    # ---- statement + intro ----
    st = d.get('statement') or {}
    figs = [f for f in (d.get('figures') or []) if f.get('v')]
    has_st = st.get('title') or st.get('text')
    link_h = next((g.get('h') for g in groups if g.get('h')), None)
    more = _a(known[link_h] + ' →', link_h, 'more r up') if link_h in known else ''
    intro_h3 = steps.get('title') if steps.get('title') != cat_title else None
    intro = ''
    if cat_title or intro_h3 or steps.get('text'):
        intro = '<div class="two intro" id="services"><div>%s%s</div><div>%s%s</div></div>' % (
            '<h2 class="bar-h r dn">%s</h2>' % e(cat_title) if cat_title else '', more,
            '<h3 class="r up">%s</h3>' % e(intro_h3) if intro_h3 else '', _paras(steps.get('text')))
    if has_st or intro:
        top = ''
        if has_st:
            top = '%s%s<div class="rule"><i></i><i></i></div><div class="two">%s<div><div class="lead r up">%s</div>%s</div></div>' % (
                '<p class="kick mono r up">%s</p>' % e(hero.get('kicker')) if hero.get('kicker') and st.get('title') else '',
                '<h2 class="r dn">%s</h2>' % e(st.get('title') or hero.get('kicker')) if (st.get('title') or hero.get('kicker')) else '',
                '<div class="figs">%s</div>' % ''.join('<div><b>%s</b>%s</div>' % (e(f['v']), '<span class="mono">%s</span>' % e(f.get('l')) if f.get('l') else '') for f in figs[:4]) if figs else '<div class="empty"></div>',
                _paras(st.get('text')),
                '<div class="btns r up">%s%s</div>' % (_a(cta_t or p1_t, cta_h or p1_h, 'btn btn-k'), _a(p2_t, p2_h, 'btn btn-ok')) if (cta_t or p1_t or p2_t) else '')
        S.append('<section class="st" id="about"><div class="wrap">%s%s</div></section>' % (top, intro))

    # ---- outline cards on a photograph ----
    rows_groups = []          # what the cards cannot hold goes to the ruled rows below
    cards, pics = [], []
    slider_imgs = {s.get('img') for s in step_items if s.get('img')}
    if groups:
        if grouped:
            for gi, g in enumerate(groups):
                lis = ''.join('<li>%s%s</li>' % (e(it.get('name')), ' — ' + ', '.join(_price(it)) if _price(it) else '') for it in g['items'] if it.get('name'))
                cards.append((g.get('t') or '', '<ul>%s</ul>' % lis + _paras(g.get('text')), g.get('h'), g.get('img')))
                if any(it.get('text') or it.get('rows') or it.get('note') for it in g['items']):
                    rows_groups.append((g.get('t') or cat_title, g['items']))
        else:
            long_items = []
            for g in groups:
                for it in g['items']:
                    if not it.get('name'):
                        continue
                    pr = _price(it)
                    body = ''.join('<p>%s</p>' % x for x in pr) + _paras(it.get('note'))
                    if it.get('rows'):
                        body += '<ul>%s</ul>' % ''.join('<li>%s</li>' % e(r) for r in it['rows'])
                    txt = it.get('text') or ''
                    if txt and len(txt) <= 380:
                        body += _paras(txt)
                    elif txt:
                        long_items.append(it)
                    cards.append((it['name'], body, it.get('h'), it.get('img')))
            if long_items:
                rows_groups.append((cat_title, long_items))
        ch = []
        for i, (t, body, h_, img) in enumerate(cards):
            own = img and img not in slider_imgs and not (by_src.get(img) or {}).get('small') and (dims(img) or (0, 0))[0] >= 1200
            if own:
                pics.append(_img(img, '', extra=' data-i="%d" data-slot="card"' % i))
            inner = '<div class="card-t">%s</div>%s%s' % (e(t), '<div class="card-c">%s</div>' % body if body else '', '<span class="card-x" aria-hidden="true">↗</span>' if h_ else '')
            attrs = 'class="card%s"%s' % (' has' if body else '', ' data-i="%d"' % i if own else '')
            ch.append('<a %s href="%s"%s>%s</a>' % (attrs, e(h_), ' rel="noopener"' if re.match(r'https?:', h_) else '', inner) if h_ else '<div %s tabindex="0">%s</div>' % (attrs, inner))
        S.append('<section class="gr"%s>%s<div class="wrap"><div class="cards%s">%s</div>%s</div></section>' % (
            '' if intro else ' id="services"',
            '<div class="gr-pics">%s%s</div><div class="gr-veil"></div>' % (_img(grid_pic['src'], grid_pic.get('alt'), 'on', ' data-slot="cards"') if grid_pic else '', ''.join(pics)) if (grid_pic or pics) else '',
            ' c%d' % len(ch) if len(ch) < 3 else '', ''.join(ch), '<p class="plans-note">%s</p>' % e(cat_note) if cat_note else ''))

    # ---- slideshow band: steps ----
    if step_items:
        has_pics = any(s.get('img') for s in step_items)
        pp, tt = [], []
        for i, s in enumerate(step_items):
            if has_pics:
                pp.append('<div class="sl-pic%s">%s</div>' % (' on' if i == 0 else '', _img(s['img'], alt(s['img']), extra=' data-slot="slide"') if s.get('img') else ''))
            ct, chh = _lnk(s.get('cta')) if isinstance(s.get('cta'), dict) else (None, None)
            tt.append('<div class="sl-text%s">%s%s%s</div>' % (' on' if i == 0 else '', '<h3 class="h40">%s</h3>' % e(s.get('title')) if s.get('title') else '', _paras(s.get('text')),
                                                           _a(ct + ' →', chh, 'go') if ct and chh else ''))
        many = len(step_items) > 1
        S.append('<section class="sl%s" id="work" data-sl>%s<div class="wrap"><div class="sl-body"><div class="sl-texts" aria-live="polite">%s</div>%s%s</div></div></section>' % (
            '' if has_pics else ' plain', '<div class="sl-pics">%s<div class="sl-veil"></div></div>' % ''.join(pp) if has_pics else '', ''.join(tt),
            '<div class="sl-nav"><button type="button" data-go="-1" aria-label="%s">←</button><button type="button" data-go="1" aria-label="%s">→</button></div>' % (e(w_prev), e(w_next)) if many else '',
            '<div class="sl-num" aria-hidden="true"><b data-n>01</b><span>/%02d</span></div>' % len(step_items) if many else ''))

    # ---- ruled rows: catalogue texts, then questions ----
    def rows(head_t, items, kind):
        out = []
        for i, it in enumerate(items):
            if kind == 'faq':
                q_, a_ = e(it.get('q')), _paras(it.get('a'))
            else:
                pr = _price(it)
                q_ = e(it.get('name')) + ('<small class="mono">%s</small>' % ', '.join(pr) if pr else '')
                a_ = _paras(it.get('text'), it.get('note')) + ('<ul>%s</ul>' % ''.join('<li>%s</li>' % e(r) for r in it['rows']) if it.get('rows') else '')
                if not it.get('name'):
                    continue
            num = '<span class="fq-n mono">%02d</span>' % (i + 1)
            if a_:
                out.append('<details class="fq-i"><summary>%s<span class="fq-q">%s</span><span class="fq-p" aria-hidden="true"></span></summary><div class="fq-a">%s</div></details>' % (num, q_, a_))
            else:
                out.append('<div class="fq-i"><div class="fq-row">%s<span class="fq-q">%s</span></div></div>' % (num, q_))
        return '<section class="fq"><div class="wrap fq-g"><div>%s</div><div>%s</div></div></section>' % ('<h3 class="h40 r up">%s</h3>' % e(head_t) if head_t else '', ''.join(out)) if out else ''
    for t, its in rows_groups:
        S.append(rows(t, its, 'cat'))
    if faq_items:
        S.append(rows(faq.get('title'), faq_items, 'faq').replace('<section class="fq">', '<section class="fq" id="faq">'))

    # ---- the dark part ----
    D = []
    big = feats.get('text') or cat_text
    if big and len(big) <= 150:
        D.append('<h2 class="big pale r dn">%s</h2>' % e(big))
    trust = [t for t in (d.get('trust') or []) if t]
    if people or trust or team.get('text'):
        D.append('<div class="rule"><i></i><i></i></div><div class="two" id="people"><div>%s</div><div class="r up">%s%s</div></div>' % (
            '<h2 class="bar-h r dn">%s</h2>' % e(team.get('title')) if team.get('title') else '',
            '<ul class="bullets">%s</ul>' % ''.join('<li>%s</li>' % e(t) for t in trust) if trust else '', _paras(team.get('text'), cls='txt')))
    if people:
        cs = []
        for i, p in enumerate(people):
            pic = ''
            if p.get('img'):
                wh = dims(p['img'])
                ar = max(.8, min(1.3334, wh[0] / wh[1])) if wh else 1
                pic = '<div class="tm-pic" style="aspect-ratio:%.4f">%s</div>' % (ar, _img(p['img'], p['name'], extra=' data-slot="portrait"'))
            reach = ' '.join(x for x in [_a(p.get('phone'), 'tel:' + re.sub(r'[^+\d]', '', p.get('phone') or '')) if p.get('phone') else '', _a(p.get('email'), 'mailto:' + (p.get('email') or '')) if p.get('email') else ''] if x)
            cs.append('<div class="tm%s" style="--t:%s">%s<div class="tm-cap mono">%s</div>%s%s%s</div>' % (
                '' if pic else ' type', T['tints'][i % 4], pic, e(p['name']), '<div class="tm-role">%s</div>' % e(p.get('role')) if p.get('role') else '',
                '<p class="tm-text">%s</p>' % e(p.get('text')) if p.get('text') else '', '<p class="tm-more">%s</p>' % reach if reach else ''))
        nc = len(cs)
        D.append('<div class="team c%d r dn">%s</div>' % (nc if nc < 4 else (3 if nc in (5, 6, 9) else 4), ''.join(cs)))
    for q in quotes:
        who = q.get('name') or ''
        D.append('%s<div class="rule"><i></i><i></i></div><div class="two"><div class="empty"></div><blockquote class="qt r up"><p>%s</p>%s</blockquote></div>' % (
            '<p class="lab mono r up">%s</p>' % e(who) if who else '<div class="lab"></div>', e(q['q']), '<footer>%s</footer>' % e(q.get('role')) if q.get('role') else ''))
    for c in creds:
        D.append('%s<div class="rule"><i></i><i></i></div><div class="two"><div class="empty"></div><div class="qt r up"><p>%s</p>%s</div></div>' % (
            '<p class="lab mono r up">%s</p>' % e(c.get('year')) if c.get('year') else '<div class="lab"></div>',
            _a(c['t'], c['h']) if c.get('h') else e(c['t']), '<footer>%s</footer>' % e(c.get('text')) if c.get('text') else ''))
    if video and video.get('src'):
        D.append('<div class="slot"><video src="../../%s"%s controls playsinline preload="metadata" aria-label="%s" data-slot="film"></video></div>' % (
            e(video['src']), ' poster="../../%s"' % e(video['poster']) if video.get('poster') else '', e(video.get('alt') or name)))
    else:
        seen, sl = set(used) - {x if isinstance(x, str) else (x or {}).get('src') for p in projects for x in p['photos']} | slider_imgs, []
        for p in projects:
            for x in p['photos']:
                src = x if isinstance(x, str) else (x or {}).get('src')
                if src and src not in seen and not (by_src.get(src) or {}).get('small'):
                    seen.add(src)
                    sl.append((p['title'], src))
        if not sl:                                   # no film, no projects: up to four of the photographs still unused, uncaptioned
            sl = [('', p_['src']) for p_ in [x for x in free if (x.get('w') or 0) >= 1280][:4]]
        if sl:
            rs_ = sorted((dims(src) or (16, 9))[0] / (dims(src) or (16, 9))[1] for _, src in sl)
            ar_ = max(16 / 9, min(2.4, rs_[len(rs_) // 2]))
            cap = any(t for t, _ in sl)
            D.append('<div class="slot" style="aspect-ratio:%.4f" data-sl>%s%s<div class="slot-cap"><div class="sl-texts" aria-live="polite">%s</div>%s</div></div>' % (ar_,
                ''.join('<div class="sl-pic%s">%s</div>' % (' on' if i == 0 else '', _img(src, alt(src), extra=' data-slot="project"')) for i, (t, src) in enumerate(sl)),
                '<div class="slot-veil"></div>' if (cap or len(sl) > 1) else '',
                ''.join('<div class="sl-text%s">%s</div>' % (' on' if i == 0 else '', e(t)) for i, (t, src) in enumerate(sl)) if cap else '',
                '<div class="sl-nav"><span class="sl-c mono" aria-hidden="true"><span data-n>01</span>/%02d</span><button type="button" data-go="-1" aria-label="%s">←</button><button type="button" data-go="1" aria-label="%s">→</button></div>' % (len(sl), e(w_prev), e(w_next)) if len(sl) > 1 else ''))
    if plan_items:
        ps = []
        for p in plan_items:
            ct, chh = _lnk(p.get('cta')) if isinstance(p.get('cta'), dict) else (p.get('cta'), None)
            ps.append('<div class="pl">%s<div class="pl-n">%s</div>%s<div class="pl-r"></div>%s%s%s%s</div>' % (
                '<span class="pl-tag mono">%s</span>' % e(p['marked']) if isinstance(p.get('marked'), str) and p.get('marked') else '',
                e(p['name']), '<div class="pl-p">%s</div>' % e(p.get('price')) if p.get('price') else '', '<div class="pl-per">%s</div>' % e(p.get('per')) if p.get('per') else '',
                '<div class="pl-l">%s</div>' % e(p.get('line')) if p.get('line') else '', '<ul>%s</ul>' % ''.join('<li>%s</li>' % e(r) for r in p['rows']) if p.get('rows') else '',
                _a(ct, chh or cta_h, 'pill') if ct else ''))
        D.append('<div class="plans-h" id="plans">%s%s</div><div class="plans">%s</div>%s' % (
            '<h3>%s</h3>' % e(plans.get('title')) if plans.get('title') else '', _paras(plans.get('text')), ''.join(ps), '<p class="plans-note">%s</p>' % e(plans.get('note')) if plans.get('note') else ''))
    cl = d.get('close') or {}
    if cl.get('title'):
        c_t, c_h = _lnk(cl.get('cta'))
        short = cl.get('text') and len(cl['text']) <= 90
        second = (p2_t, p2_h) if p2_h and p2_h != c_h else ((phone.get('t'), phone.get('h')) if phone.get('t') and phone.get('h') else (None, None))
        D.append('<div class="close" id="contact">%s<h2 class="big r dn">%s</h2>%s<div class="btns r up">%s%s</div></div>' % (
            '<p class="close-s r up">%s</p>' % e(cl['text']) if short else '', e(cl['title']), '<p class="close-t r up">%s</p>' % e(cl['text']) if cl.get('text') and not short else '',
            _a(c_t or cta_t, c_h or cta_h, 'btn btn-ow'), _a(second[0], second[1], 'btn btn-ow')))
    if D:
        S.append('<section class="dk"><div class="wrap">%s</div></section>' % ''.join(D))

    # ---- foot ----
    ft = d.get('foot') or {}
    if lang == 'en':
        line = ', '.join(x for x in [addr.get('street'), addr.get('city'), addr.get('region'), addr.get('postcode')] if x)
    else:
        line = ', '.join(x for x in [addr.get('street'), ' '.join(x for x in [addr.get('postcode'), addr.get('city')] if x), addr.get('region')] if x)

    def detail(pl, ph, em, with_booking):
        r = []
        if ph.get('t'):
            r.append('<div class="ft-row">%s%s</div>' % (_a(ph['t'], ph.get('h') or 'tel:' + re.sub(r'[^+\d]', '', ph['t'])), '<span>%s</span>' % e(ph.get('note')) if ph.get('note') else ''))
        if em:
            r.append('<div class="ft-row">%s</div>' % _a(em, 'mailto:' + em))
        for h_ in pl.get('hours') or []:
            r.append('<div class="ft-row"><span>%s</span><span>%s</span></div>' % (e(h_.get('days')), e(' – '.join(x for x in [h_.get('open'), h_.get('close')] if x))))
        if with_booking:
            b_t, b_h = _lnk(pl.get('booking'))
            f_t, f_h = _lnk(contact.get('form'))
            for t, h_ in ((b_t, b_h), (f_t, f_h)):
                if t and h_:
                    r.append('<div class="ft-row">%s<span aria-hidden="true">→</span></div>' % _a(t, h_))
            for rt in contact.get('routes') or []:
                if rt.get('t'):
                    r.append('<div class="ft-row">%s%s</div>' % (_a(rt['t'], rt.get('h')) if rt.get('h') else e(rt['t']), '<span>%s</span>' % e(rt.get('note')) if rt.get('note') else ''))
        return ''.join(r)
    det = detail(place, phone, email, True)
    locs = ''
    for lo in d.get('locations') or []:
        la = lo.get('address') or {}
        ll = ', '.join(x for x in [la.get('street'), ' '.join(x for x in [la.get('postcode'), la.get('city')] if x)] if x)
        lph = lo.get('phone') if isinstance(lo.get('phone'), dict) else ({'t': lo.get('phone')} if lo.get('phone') else {})
        locs += '<div class="ft-loc">%s%s%s%s</div>' % ('<p class="kick mono">%s</p>' % e(lo.get('name')) if lo.get('name') else '', '<div class="ft-row"><span>%s</span></div>' % e(ll) if ll else '',
                                                    detail(lo, lph, lo.get('email'), False), '<div class="ft-row"><span>%s</span></div>' % e(lo.get('note')) if lo.get('note') else '')
    extra = [(l.get('t'), l.get('h')) for l in (d.get('links') or []) if l.get('t') and l.get('h') and l['h'] not in {h_ for _, h_ in nav} and l['h'] not in {c[2] for c in cards}]
    col1 = ''.join(_a(t, h_) for t, h_ in nav)
    col2 = ''.join(_a(s.get('t'), s.get('h')) for s in (place.get('social') or []) if s.get('t') and s.get('h')) + ''.join(_a(t, h_) for t, h_ in extra[:6])
    mark_n = max(6, len(name)) * .56
    legal = ' '.join(x for x in [e(ft.get('legal')) if ft.get('legal') else '', ''.join(_a(l.get('t'), l.get('h')) for l in (ft.get('links') or []) if l.get('t'))] if x)
    foot = ('<footer class="ft">%s<div class="ft-main"><div class="wrap">%s<div class="ft-cols">%s%s%s</div></div></div>%s</footer>' % (
        '<div class="ft-mark" aria-hidden="true"><div class="wrap"><div style="--n:%.2f">%s</div></div></div>' % (mark_n, e(name)) if name else '',
        '<p class="ft-line">%s</p>' % e(line) if line else '',
        '<div class="ft-l mono">%s</div>' % col1 if col1 else '<div></div>', '<div class="ft-l mono">%s</div>' % col2 if col2 else '<div></div>',
        '<div class="ft-d">%s%s</div>' % (det, locs) if (det or locs) else '',
        '<div class="ft-end"><div class="wrap"><span>%s</span><span>%s</span></div></div>' % (e(ft.get('text')), legal) if (ft.get('text') or legal) else ''))

    desc = hero.get('text') or (d.get('statement') or {}).get('text') or ''
    ptitle = name + (' — ' + hero['kicker'] if hero.get('kicker') and hero['kicker'] != name else '')
    root = ':root{--G:%(G)s;--K:%(K)s;--D:%(D)s;--F:%(F)s;--W:%(W)s;--A:%(A)s;--Kr:%(Kr)s;--Dr:%(Dr)s;--Wr:%(Wr)s;--Gr:%(Gr)s;--cink:%(cink)s;--BB:%(BB)s;--BF:%(BF)s' % T
    root += ';--h1:%dpx;--h1m:%dpx}' % h1
    svg = '<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><filter id="vb" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB"><feGaussianBlur stdDeviation="3 110"/></filter></svg>'
    return ('<!doctype html>\n<html lang="%s">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n<title>%s</title>\n%s%s\n<style>%s%s</style>\n</head>\n'
            '<body>\n<a class="skip" href="#about" aria-label="%s">↓</a>\n%s\n%s\n<main class="page">\n%s\n</main>\n%s\n%s\n<script>%s</script>\n</body>\n</html>\n'
            % (e(lang), e(ptitle), '<meta name="description" content="%s">\n' % e(desc[:300]) if desc else '', FONTS, root, CSS, e(name), svg, head, '\n'.join(s for s in S if s), foot, menu, JS))
