"""butter/render.py — one pure function: render(d) -> a complete page.

The build (section order, grid, measures, type scale, spacing, radii, motion, phone layout) was measured on the
reference's home page at 1440x900 and 390x844 on 2026-11-12 (see NOTES.md; raw captures in ref/ and probe/).
Nothing of the reference's code, words, pictures, icons, logos or typefaces is here. The client's data fills it;
a section whose data is missing is left out whole. No model call, no file reads, no client logic.
"""
import html
import json

FONTS = ('https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;500'
         '&family=Geist+Mono:wght@400&display=swap')
P = '../../'  # media paths in the data are relative to templates/


# ───────────────────────── colour: the reference's relations (ground 250, soft 237, ink 15, button 30, panel 10)
def _rgb(h):
    h = (h or '#000').strip().lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _hex(c):
    return '#%02x%02x%02x' % tuple(max(0, min(255, round(v))) for v in c)


def _mix(a, b, t):
    """t of a over b"""
    a, b = _rgb(a), _rgb(b)
    return _hex(tuple(a[i] * t + b[i] * (1 - t) for i in range(3)))


def _lum(h):
    def f(v):
        v /= 255
        return v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4
    r, g, b = _rgb(h)
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b)


def _con(a, b):
    x, y = sorted((_lum(a), _lum(b)), reverse=True)
    return (x + .05) / (y + .05)


def _raise(ink, bg, start, floor):
    """the reference's muted tones are ink at 30-40 %; raised here until they read at `floor` on `bg`"""
    t = start
    while _con(_mix(ink, bg, t), bg) < floor and t < 1:
        t += .02
    return _mix(ink, bg, min(t, 1))


def _theme(bg, ink, accent, extra):
    soft = _mix(ink, bg, .055)                      # 237 on 250
    glow = [c for c in [accent] + list(extra or []) if c and _con(c, bg) >= 1.6][:3] or [ink]
    while len(glow) < 3:
        glow.append(glow[-1])
    v = {'bg': bg, 'ink': ink, 'soft': soft, 'soft2': _mix(ink, bg, .10), 'top': _mix(ink, bg, .15),
         'btn': _mix(ink, bg, .94), 'btntx': _mix(bg, ink, .94), 'panel': _mix(ink, bg, .98 if _lum(bg) >= .2 else .10),
         'mute': _raise(ink, soft, .40, 4.6), 'dim': _raise(ink, soft, .30, 3.05),
         'veil': 'rgba(%d,%d,%d,.2)' % _rgb(_mix(ink, bg, .8)),
         'g1': glow[0], 'g2': glow[1], 'g3': glow[2], 'bgc': '%d,%d,%d' % _rgb(bg), 'sfc': '%d,%d,%d' % _rgb(soft)}
    return ';'.join('--%s:%s' % kv for kv in v.items())


def _over(tone, bg, ink):
    """ink and veil for text laid over a picture: light ink on a dark picture, dark ink on a light one"""
    light, dark = (bg, ink) if _lum(bg) > _lum(ink) else (ink, bg)
    tx, veil = (light, dark) if tone == 'dark' else (dark, light)
    return {'tx': tx, 'veil': '%d,%d,%d' % _rgb(veil), 'dim': _raise(tx, veil, .55, 8)}


# ───────────────────────── small helpers
def e(s):
    return html.escape(str(s or ''), quote=True)


def _words(text, cls='w'):
    return ' '.join('<span class="%s" style="--i:%d">%s</span>' % (cls, i, e(w)) for i, w in enumerate(str(text).split()))


def _img(m, cls='', lazy=True, alt=None, slot=None):
    a = e(m.get('alt', '') if alt is None else alt)
    wh = (' width="%s" height="%s"' % (m['w'], m['h'])) if m.get('w') and m.get('h') else ''
    return '<img class="%s" src="%s%s"%s alt="%s"%s%s decoding="async">' % (
        cls, P, e(m['src']), wh, a, ' loading="lazy"' if lazy else '', (' data-slot="%s"' % slot) if slot else '')


def _btn(link, kind='dark', arrow=False, cls=''):
    if not link or not link.get('t'):
        return ''
    return '<a class="btn %s %s" href="%s"><span>%s</span>%s</a>' % (
        kind, cls, e(link.get('h', '#')), e(link['t']), '<i aria-hidden="true">→</i>' if arrow else '')


def _shape(m):
    if m.get('shape') == 'book':
        return 'book'
    return 'tall' if (m.get('h') or 0) > (m.get('w') or 1) else 'wide'


CSS = r"""
*{box-sizing:border-box;margin:0;padding:0}
html{-webkit-text-size-adjust:100%;text-size-adjust:100%}
body{background:var(--bg);color:var(--ink);font-family:'Inter Tight','Helvetica Neue',Arial,sans-serif;font-size:18px;line-height:1.5;font-weight:400;-webkit-font-smoothing:antialiased;overflow-x:hidden}
img,video{display:block;max-width:100%;height:auto}
a{color:inherit;text-decoration:none}
button{font:inherit;color:inherit;background:none;border:0;cursor:pointer;text-align:left}
ul{list-style:none}
:focus-visible{outline:2px solid currentColor;outline-offset:3px;border-radius:4px}
:root{--gut:4.5906vw;--gap:25px;--ez:cubic-bezier(.2,.715,.205,.99);--ez2:cubic-bezier(.835,.12,.225,.77);--rad:32px}
.wrap{padding:0 var(--gut)}
.grid{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));column-gap:var(--gap)}
h1,h2,h3,h4{font-weight:400;overflow-wrap:break-word}
.h1{font-size:min(7.47vw,143px);line-height:.992;letter-spacing:-.02em}
.h2{font-size:min(4.194vw,80px);line-height:.97;letter-spacing:-.021em}
.h3{font-size:min(3.156vw,60px);line-height:.96;letter-spacing:-.027em}
.h4{font-size:max(20px,min(1.7vw,32px));line-height:1.15;letter-spacing:.002em}
.body{font-size:20.75px;line-height:24px;letter-spacing:.043em}
.small{font-size:16px;line-height:21px;letter-spacing:.042em}
.cap{font-family:'Geist Mono','IBM Plex Mono',ui-monospace,monospace;font-size:13.5px;line-height:24px;letter-spacing:.036em;color:var(--mute)}
.mute{color:var(--mute)}
.skip{position:absolute;left:8px;top:8px;z-index:60;background:var(--btn);color:var(--btntx);padding:10px 14px;border-radius:8px;transform:translateY(-63px);transition:transform .2s var(--ez)}
.skip:focus{transform:none}

/* buttons: 50 high, radius 16, 8/30; a soft coloured light swells behind on hover (.4s) */
.btn{position:relative;display:inline-flex;align-items:center;justify-content:center;gap:16px;min-height:50px;padding:8px 30px;border-radius:16px;font-size:16px;line-height:21px;letter-spacing:.044em;max-width:100%;text-align:center;text-wrap:balance;isolation:isolate}
.btn::before{content:"";position:absolute;inset:1px;border-radius:inherit;z-index:-2;opacity:0;transform:scaleY(.9);background:var(--g1);box-shadow:0 0 4px var(--g1),1px 1px 2px var(--g1),1px 2px 2px var(--g2),1px 4px 6px var(--g3),1px 6px 10px var(--g1);transition:transform .4s var(--ez),opacity .4s linear}
.btn::after{content:"";position:absolute;inset:0;border-radius:inherit;z-index:-1;background:var(--btn)}
.btn:hover::before,.btn:focus-visible::before{opacity:1;transform:none}
.btn:active{transform:translateY(1px)}
.btn.dark{color:var(--btntx)}
.btn.light{color:var(--ink)}.btn.light::after{background:var(--soft)}
.btn.onsoft{color:var(--ink)}.btn.onsoft::after{background:var(--bg)}
.btn.sq{width:50px;padding:8px;flex:none}
.btn.sm{min-height:39px;padding:8px 16px;border-radius:10px}
.btn i{font-style:normal;font-size:17px;line-height:1}

/* bar: fixed, two soft pills; the left one closes to logo + toggle once the page has moved 100px */
.hd{position:fixed;inset:0 0 auto 0;height:88px;z-index:50;pointer-events:none}
.hd-in{display:flex;justify-content:space-between;align-items:center;padding:24px 30px 0;height:88px}
.pill{position:relative;display:flex;align-items:center;height:64px;padding:16.5px 22px;pointer-events:auto}
.pill::before{content:"";position:absolute;left:0;top:0;height:100%;width:100%;border-radius:16px;background:var(--soft);transition:width .5s var(--ez)}
.pill>*{position:relative}
.logo{display:flex;align-items:center;gap:10px;font-size:19px;font-weight:500;letter-spacing:-.01em;white-space:nowrap}
.logo img{height:23px;width:auto}
.logo img.mark{height:26px;border-radius:6px}
.nav{display:flex;gap:25px;margin-left:51px;transition:opacity .5s var(--ez)}
.nav a,.acct a.tl{font-size:16px;line-height:20px;letter-spacing:.044em;white-space:nowrap;transition:opacity .5s var(--ez)}
.nav a:hover,.acct a.tl:hover{opacity:.55}
.tog{width:23px;height:31px;margin-left:25px;border-radius:5px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5px;transition:transform .5s var(--ez)}
.tog b{width:3px;height:3px;border-radius:50%;background:var(--ink);transition:transform .5s var(--ez)}
.tog[aria-expanded=true] b:first-child{transform:translate(-4px,4px)}
.tog[aria-expanded=true] b:last-child{transform:translate(4px,-4px)}
.acct{display:flex;align-items:center;gap:16px;background:var(--soft);border-radius:16px;padding:10.5px 12px 10.5px 22px;pointer-events:auto}
.acct:not(:has(.tl)){padding-left:12px}
.hd.shut .pill::before{width:var(--shutw,250px)}
.hd.shut .nav{opacity:0;pointer-events:none}
.hd.shut .tog{transform:translateX(var(--shift,0px))}
.drop{position:absolute;left:0;right:0;top:72px;background:var(--soft);border-radius:16px;padding:14px 14px 22px;opacity:0;visibility:hidden;transform:scale(.98);transform-origin:top center;clip-path:inset(0 0 100% 0 round 16px);transition:opacity .8s var(--ez),transform .5s var(--ez),clip-path .5s var(--ez),visibility 0s .5s;max-height:calc(100vh - 110px);overflow:auto}
.hd.open .drop{opacity:1;visibility:visible;transform:none;clip-path:inset(0 round 16px);transition-delay:0s}
.hd.open .pill::before{width:100%}
.hd.open .nav{opacity:0;pointer-events:none}
.hd.open .tog{transform:none}
.drop li a{display:flex;justify-content:space-between;align-items:baseline;gap:24px;padding:22px 8px;font-size:16px;line-height:20px;letter-spacing:.044em;transition:opacity .5s var(--ez),padding-left .5s var(--ez)}
.drop li+li a{border-top:1px solid var(--soft2)}
.drop li a:hover{padding-left:14px}
.drop li a span{font-size:13px;line-height:16px;letter-spacing:.044em;color:var(--mute);text-align:right;max-width:60%}
.drop .only-m{display:none}
.shade{position:fixed;inset:0;background:var(--veil);opacity:0;pointer-events:none;transition:opacity .5s var(--ez);z-index:40}
.shade.on{opacity:1;pointer-events:auto}

/* opening: one screen, ground shaded from the top, the picture hangs at the top centre, type under it */
.hero{position:relative;min-height:100vh;display:flex;background:linear-gradient(var(--top),var(--bg));overflow:hidden}
.hero .sky{position:absolute;left:0;top:0;width:100%;height:100%;object-fit:cover;object-position:50% 0;-webkit-mask-image:linear-gradient(#000 22%,transparent 92%);mask-image:linear-gradient(#000 22%,transparent 92%)}
.hero .skyv{position:absolute;inset:0;background:linear-gradient(rgba(var(--ov),0) 12%,rgba(var(--ov),.8) 32%,rgba(var(--ov),.9) 50%,rgba(var(--ov),.86) 74%,rgba(var(--ov),.5))}
.hero-c{position:relative;width:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:30px;padding:200px 0 140px;text-align:center}
.hero h1{max-width:100%}
.hero .sub{display:flex;flex-direction:column;align-items:center;gap:30px}
.hero .h4{max-width:34em}

/* band of marks: one muted line, then a row that runs by itself */
.tick{padding:50px 0;overflow:hidden}
.tick .note{text-align:center;color:var(--mute);margin-bottom:60px}
.mq{overflow:hidden}
.mq-t{display:flex;width:max-content;animation:mq var(--mqd,60s) linear infinite}
.mq-g{display:flex;align-items:center;flex:none}
.tick .mq-g>*{margin-right:100px;height:36px;display:flex;align-items:center;white-space:nowrap}
.tick .mq-g img{height:36px;width:auto}
@keyframes mq{to{transform:translateX(-50%)}}

/* statement, then the dark slab the tiles fly into */
.stm{overflow:hidden;overflow:clip}
.stm-a{min-height:100vh;display:flex;align-items:center;justify-content:center;padding:40px 0;text-align:center}
.stm-a h2{max-width:18em}
.ph{display:none;width:1.142em;height:1.142em;vertical-align:-.2em;margin:0 .1em}
.stm-b{min-height:100vh;display:flex;align-items:center;justify-content:center;padding:40px 0}
.slab{width:100%;background:var(--panel);border-radius:min(3.2vw,60px);padding:19.6px;display:flex;gap:16px;box-shadow:0 30px 60px -20px rgba(0,0,0,.28),0 60px 90px -40px rgba(0,0,0,.2)}
.slab{position:relative}
.slab .bk{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:50% 100%;border-radius:inherit;opacity:.5}
.slot{position:relative;flex:1;aspect-ratio:1}
.tile{position:absolute;inset:0;border-radius:25%;overflow:hidden;transform-origin:0 0;will-change:transform;background:var(--c,var(--soft2))}
.tile img{width:100%;height:100%;object-fit:cover;object-position:50% 28%}   /* a screen's working part, not its top bar */

/* three stories: big sentence and the product, whole */
.st{padding:16.5vw 0}
.st .grid{align-items:center}
.st .tx{grid-column:1/7}
.st .md{grid-column:8/13;display:flex;justify-content:center}
.st.two .md{grid-column:1/7;grid-row:1}
.st.two .tx{grid-column:8/13}
.st .cap{margin-bottom:25px;display:block}
.shot{border-radius:var(--rad);width:auto;height:auto;max-width:100%}
.shot.book{border-radius:6px}
.st.one .shot{max-height:60.4vw}
.st.two .shot{max-height:47.7vw}
.s3{position:relative}
.s3-track{display:flex;flex-direction:column;gap:50px;padding:0 var(--gut)}
.s3 .tx{display:flex;flex-direction:column;justify-content:center}
.s3 .md{display:flex;align-items:center;justify-content:center}

/* cards in a row that can be pulled sideways */
.sec{padding:140px 0}
.hdrow{display:flex;justify-content:space-between;align-items:flex-end;gap:40px;margin-bottom:60px}
.hdrow .l{max-width:45%}
.hdrow .l .body{margin-top:25px}
.hdrow .cap{display:block;margin-bottom:25px}
.rail{display:flex;gap:var(--gap);overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none;margin:0 calc(var(--gut) * -1);padding:0 var(--gut);scroll-padding:0 var(--gut)}
.rail::-webkit-scrollbar{display:none}
.card{flex:0 0 calc((100% - 3 * var(--gap)) / 4);scroll-snap-align:start;min-width:0}
.card .pic{position:relative;aspect-ratio:308/401;border-radius:var(--rad);overflow:hidden;background:var(--soft);margin-bottom:20px}
.card .pic img{width:100%;height:100%;object-fit:cover}
.card .pic::after{content:"";position:absolute;inset:0;background:rgba(var(--bgc),.38)}
.card h3{margin-bottom:20px}

/* three ways: the product at the left, a list that opens at the right */
.hl .grid{align-items:center}
.hl .md{grid-column:1/7;display:grid;justify-items:center;align-items:center;min-height:49vw}
.hl .md>div{grid-area:1/1;display:flex;justify-content:center}
.hl .shot{max-height:49vw}
.hl .tx{grid-column:8/13}
.hl .cap{display:block;margin-bottom:25px}
.acc-h{display:block;padding-bottom:25px}
.acc-b{display:block;width:100%;color:var(--dim);transition:color .5s var(--ez2)}
.acc-b:hover,.acc-i.on .acc-b{color:var(--ink)}
.acc-c{overflow:hidden}
.acc-c>div{padding-bottom:20px;max-width:26em}
.acc-c p+p{margin-top:12px}
.acc-c .btn{margin-top:22px}
.q .acc-b{font-size:min(2.894vw,55px);line-height:.96;letter-spacing:-.008em;color:inherit}

.st .tx .body,.s3 .tx .body{margin-top:25px;max-width:26em}
.fg li{padding-bottom:29px}
.fg li:last-child{padding-bottom:0}
.fg .v{font-size:min(4.194vw,80px);line-height:.97;letter-spacing:-.021em;margin-bottom:10px}
.fg .body{max-width:24em}
.fq-f .bk.flip{transform:scaleX(-1)}
.cl .wrap{display:flex;flex-direction:column;align-items:center;text-align:center}
.cl h2{max-width:19em}
.cl .body{margin-top:25px;max-width:30em}
.cl .btn{margin-top:40px}
/* gallery: a soft field, upright pictures running by */
.gal-f{background:var(--soft);border-radius:var(--rad);padding:50px 0}
.gal .mq-t{animation-duration:var(--mqd,50s)}
.gi{flex:none;width:308px;margin-right:var(--gap);padding:50px 0;border-radius:20px;display:grid;justify-items:center;gap:30px;transition:background-color 1s var(--ez)}
.gi:hover{background:var(--soft2)}
.gi .im{width:216px;height:384px;display:flex;align-items:center;justify-content:center}
.gi img{width:auto;height:auto;max-width:216px;max-height:384px;border-radius:8px}
.gi img.book{border-radius:3px}
.gi p{text-align:center;max-width:216px}

/* head, text and one picture */
.ab .grid{align-items:center;row-gap:60px}
.ab .tx{grid-column:1/6;display:flex;flex-direction:column;gap:25px}
.ab .md{grid-column:7/13;display:flex;justify-content:center}
.ab .shot,.ab video{max-height:44.5vw;width:auto}
.ab.solo .tx{grid-column:1/8}

/* two soft cards */
.db .grid{row-gap:var(--gap)}
.dc{grid-column:span 6;background:var(--soft);border-radius:var(--rad);display:flex;flex-direction:column;justify-content:space-between;gap:60px;overflow:hidden}
.dc.full{min-height:min(49.9vw,760px);gap:25px}
.dc.one{grid-column:1/13;min-height:0}
.dc-t{display:flex;justify-content:space-between;gap:20px;padding:50px 50px 0}
.dc-m{position:relative;padding:0 50px}
.dc-m.pic{flex:1;display:flex;flex-direction:column;justify-content:center;padding:44px 50px;min-height:230px}
.dc-m .bk{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.dc-m .vl{position:absolute;inset:0;background:linear-gradient(var(--soft),rgba(var(--sfc),.66) 34px,rgba(var(--sfc),.66) calc(100% - 34px),var(--soft))}
.dc-m>p{position:relative}
.dc-m .h1{line-height:1}
.dc-m .body{margin-top:14px}
.dc-b{padding:0 50px 50px;display:flex;flex-direction:column;gap:12px;max-width:575px}
.dc-b li{position:relative;padding-left:18px}
.dc-b li::before{content:"";position:absolute;left:0;top:9px;width:4px;height:4px;border-radius:50%;background:currentColor}
.db .note{margin-top:40px;max-width:46em}

/* questions over a picture that fills the field */
.fq-f{position:relative;border-radius:var(--rad);overflow:hidden;min-height:49vw;background:var(--soft);color:var(--ftx,var(--ink));display:flex}
.fq-f .bk{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.fq-f .vl{position:absolute;inset:0;background:linear-gradient(90deg,rgba(var(--fv),0) 18%,rgba(var(--fv),.95) 46%,rgba(var(--fv),.96))}
.fq-f .grid{position:relative;width:100%;padding:50px;align-items:center}
.fq-f .tx{grid-column:7/13}
.fq-f .cap{display:block;margin-bottom:25px;color:var(--fdim,var(--mute))}
.fq-f.plain .tx{grid-column:1/9}
.q .acc-c .body{color:inherit}
.q .acc-i{border:0}

/* foot */
.ft{position:relative;background:var(--soft);padding:160px 0 60px;overflow:hidden}
.ft>.bk{position:absolute;left:0;bottom:0;width:100%;height:78%;object-fit:cover;object-position:50% 0;transform:scaleY(-1)}
.ft>.vl{position:absolute;inset:0;background:linear-gradient(var(--soft) 24%,rgba(var(--sfc),.62) 58%,rgba(var(--sfc),.9) calc(100% - 150px),rgba(var(--sfc),.93))}
.ft>.wrap{position:relative}
.ft.pic .legal{color:var(--ink)}
.ft .cols{row-gap:50px}
.ft .cols ul{grid-column:span 2;display:flex;flex-direction:column;gap:5px}
.ft .cols a{display:inline-block;transition:padding-left .5s var(--ez),opacity .5s var(--ez)}
.ft .cols a:hover{padding-left:6px}
.ft .big{display:block;margin:70px 0 40px;overflow:hidden}
.ft .big img{width:100%;height:auto}
.ft .big span{display:inline-block;font-weight:500;letter-spacing:-.045em;line-height:.86;white-space:nowrap;font-size:var(--fs,12vw);padding-bottom:.06em}
.ft .legal{display:flex;justify-content:space-between;gap:20px;color:var(--mute)}
.ft .legal p{max-width:44em}

/* arrival: only once scripts run (html.js); without them everything simply stands */
.js .rs{opacity:0;transform:translateY(30px);transition:transform .8s cubic-bezier(0,0,0,1) var(--d,0s),opacity .528s linear var(--d,0s)}
.js .rl{opacity:0;transform:translateY(14.4px);transition:transform .7s var(--ez) var(--d,0s),opacity .5s linear var(--d,0s)}
.js .rw .w{display:inline-block;opacity:0;transform:translateY(.55em);transition:transform .8s var(--ez) calc(var(--i) * 35ms),opacity .6s linear calc(var(--i) * 35ms)}
.js .rf .w{opacity:0;transition:opacity .7s linear calc(var(--i) * 30ms)}
.js .in.rs,.js .in.rl,.js .in .w,.js .in.rw .w,.js .in.rf .w{opacity:1;transform:none}
.hero h1 .w{display:inline-block;animation:fade .7s linear both;animation-delay:calc(.25s + var(--i) * 60ms)}
.hero .h4{animation:rise .6s var(--ez) .55s both}
.hero .btn{animation:slide .8s cubic-bezier(0,0,0,1) .65s both}
@keyframes fade{from{opacity:0}}
@keyframes rise{from{opacity:0;transform:translateY(17px)}}
@keyframes slide{from{opacity:0;transform:translateY(30px)}}
.js .fly .ph{display:inline-block}
.sw>div{-webkit-mask-image:linear-gradient(to left,#000 25%,transparent 75%);mask-image:linear-gradient(to left,#000 25%,transparent 75%);-webkit-mask-size:400% 100%;mask-size:400% 100%;-webkit-mask-position:0% 0;mask-position:0% 0;transition:-webkit-mask-position .6s var(--ez2),mask-position .6s var(--ez2);z-index:0}
.sw>div.on{-webkit-mask-position:100% 0;mask-position:100% 0;z-index:2}

@media (min-width:1000px){
 .js .s3.pin{height:calc(51.1vw + 68.26vw)}
 .js .s3.pin .s3-in{position:sticky;top:calc(50vh - 25.55vw);height:51.1vw;overflow:hidden}
 .js .s3.pin .s3-track{flex-direction:row;gap:0;width:150vw;height:100%;transform:translateX(calc(var(--p,0) * -50vw));will-change:transform}
 .js .s3.pin .tx{flex:0 0 50vw;padding-right:5.8vw}
 .js .s3.pin .md{flex:0 0 calc(100vw - 2 * var(--gut))}
 .js .s3.pin .shot{max-height:51.1vw}
 .s3:not(.pin) .s3-track,.no-js .s3 .s3-track{padding-top:120px;padding-bottom:120px}
}
@media (max-width:999px){
 :root{--gut:25.58px;--rad:24px}
 .hd{height:76px}.hd-in{padding:12px 24px 0;height:76px}
 .pill{flex:1;justify-content:space-between}
 .nav,.acct{display:none}
 .hd.shut .pill::before{width:100%}.hd.shut .tog{transform:none}
 .drop{top:72px;padding:14px 14px 16px}.drop .only-m{display:block}.drop .only-d{display:none}.drop li a{padding:9px 8px}.drop li+li a{border-top:0}
 .drop li a span{display:none}
 .h1{font-size:clamp(40px,14.545vw,112px);line-height:1.09;letter-spacing:-.02em}
 .h2{font-size:clamp(30px,8.31vw,64px);line-height:.92}
 .h3{font-size:clamp(28px,8.25vw,62px);line-height:1}
 .h4{font-size:20px;line-height:24px}
 .body{font-size:20px;line-height:24px}
 .cap{font-size:12px}
 .hero-c{padding:150px 0 120px}
 .stm-a{min-height:0;padding:185px 0 150px}
 .stm-b{min-height:0;padding:40px 0 190px}
 .slab{padding:5px;gap:4px;border-radius:22px}
 .st{padding:120px 0}
 .st .tx,.st .md,.st.two .md,.st.two .tx,.hl .md,.hl .tx,.ab .tx,.ab .md,.ab.solo .tx{grid-column:1/13;grid-row:auto}
 .st .grid,.hl .grid,.ab .grid{row-gap:46px}
 .st.one .shot,.st.two .shot,.hl .shot,.ab .shot,.ab video{max-height:118vw}
 .st.one .md{justify-content:flex-end}
 .s3{padding:60px 0 120px}
 .sec{padding:100px 0}
 .hdrow{flex-direction:column;align-items:flex-start;gap:30px;margin-bottom:31px}
 .hdrow .l{max-width:none}
 .card{flex:0 0 min(306px,82vw)}
 .hl .tx{grid-row:1}
 .hl .md{min-height:0}
 .q .acc-b{font-size:clamp(24px,6.9vw,52px);line-height:1}
 .fg .v{font-size:clamp(30px,8.31vw,64px)}
 .dc,.dc.full{grid-column:1/13;min-height:0;gap:40px}
 .dc-t{padding:30px 30px 0}.dc-m{padding:0 30px}.dc-m.pic{padding:36px 30px}.dc-b{padding:0 30px 30px}
 .fq-f{min-height:0}
 .fq-f .grid{padding:250px 30px 30px}
 .fq-f .tx,.fq-f.plain .tx{grid-column:1/13}
 .fq-f.plain .grid{padding-top:30px}
 .fq-f .vl{background:linear-gradient(rgba(var(--fv),0) 60px,rgba(var(--fv),.94) 225px,rgba(var(--fv),.95))}
 .ft{padding:160px 0 70px}
 .ft .cols ul{grid-column:span 6}
 .ft .legal{flex-direction:column}
}
@media (prefers-reduced-motion:reduce){
 *,*::before,*::after{animation:none!important;transition:none!important;scroll-behavior:auto!important}
 .js .rs,.js .rl,.js .rw .w,.js .rf .w{opacity:1;transform:none}
 .mq-t{flex-wrap:wrap;justify-content:center;width:auto;row-gap:24px}
 .mq-g[aria-hidden]{display:none}
 .mq-g{flex-wrap:wrap;justify-content:center;row-gap:24px}
}
"""

JS = r"""
(function(){
var H=document.documentElement,rm=matchMedia('(prefers-reduced-motion: reduce)').matches;
H.classList.add('js');
var $=function(s,r){return (r||document).querySelector(s)},$$=function(s,r){return [].slice.call((r||document).querySelectorAll(s))};
function clamp(v){return v<0?0:v>1?1:v}
/* arrival: when the top edge is about a tenth of the screen in */
if('IntersectionObserver' in window&&!rm){
  var io=new IntersectionObserver(function(es){es.forEach(function(x){if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target)}})},{rootMargin:'100000px 0px -9% 0px'});
  $$('.rs,.rl,.rw,.rf').forEach(function(n){io.observe(n)});
}else{$$('.rs,.rl,.rw,.rf').forEach(function(n){n.classList.add('in')})}
/* bar */
var hd=$('.hd'),pill=$('.pill'),tog=$('.tog'),shade=$('.shade'),nav=$('.nav');
function barFit(){ if(!pill||!tog)return; var was=hd.className; hd.classList.remove('shut'); tog.style.transition='none';
  var lg=$('.logo',pill).getBoundingClientRect(),pr=pill.getBoundingClientRect(),tr=tog.getBoundingClientRect();
  var w=Math.round(lg.right-pr.left+25+tr.width+22+60); hd.style.setProperty('--shutw',w+'px'); hd.style.setProperty('--shift',(pr.left+w-22-tr.width-tr.left)+'px');
  hd.className=was; tog.offsetWidth; tog.style.transition=''; }
function setOpen(o){hd.classList.toggle('open',o);shade.classList.toggle('on',o);tog.setAttribute('aria-expanded',o?'true':'false')}
if(tog){tog.addEventListener('click',function(){setOpen(!hd.classList.contains('open'))});shade.addEventListener('click',function(){setOpen(false)});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&hd.classList.contains('open')){setOpen(false);tog.focus()}});
  $$('.drop a').forEach(function(a){a.addEventListener('click',function(){setOpen(false)})});}
/* runs: the row moves at a set speed whatever its length */
$$('.mq-t').forEach(function(t){var v=+t.getAttribute('data-v')||100;function fit(){t.style.setProperty('--mqd',(t.scrollWidth/2/v).toFixed(1)+'s')}fit();addEventListener('load',fit);
  if('IntersectionObserver' in window)new IntersectionObserver(function(es){t.style.animationPlayState=es[0].isIntersecting?'running':'paused'}).observe(t);});
/* lists that open */
$$('.accs').forEach(function(box){var its=$$('.acc-i',box),sw=box.getAttribute('data-sw')?$$('#'+box.getAttribute('data-sw')+'>div'):[];
  function open(k,first){its.forEach(function(it,i){var c=$('.acc-c',it),b=$('.acc-b',it),on=i===k;
      if(!first&&!rm){var h0=c.getBoundingClientRect().height;c.style.height='auto';c.hidden=!on?false:false;var h1=on?$('div',c).getBoundingClientRect().height:0;c.style.height=h0+'px';c.offsetHeight;c.style.transition='height .25s ease';c.style.height=h1+'px';
        c.style.visibility='visible';(function(c,on){setTimeout(function(){c.style.transition='';c.style.height=on?'auto':'0px';c.style.visibility=on?'visible':'hidden'},270)})(c,on);}
      else{c.style.height=on?'auto':'0px';c.style.visibility=on?'visible':'hidden'}
      it.classList.toggle('on',on);b.setAttribute('aria-expanded',on?'true':'false');if(sw[i])sw[i].classList.toggle('on',on);});}
  its.forEach(function(it,i){$('.acc-b',it).addEventListener('click',function(){if(!it.classList.contains('on'))open(i)})});open(0,true);});
/* film */
$$('video').forEach(function(v){if(rm){v.removeAttribute('autoplay');v.pause();v.controls=true}else if('IntersectionObserver' in window){new IntersectionObserver(function(es){if(es[0].isIntersecting){var p=v.play();if(p&&p.catch)p.catch(function(){v.controls=true})}else v.pause()}).observe(v)}});
/* foot: the name fills the width */
function bigFit(){var im=$('.ft .big img');if(im&&im.naturalWidth){im.style.width='';var hh=Math.floor(im.parentNode.clientWidth*im.naturalHeight/im.naturalWidth);im.style.width=(hh*im.naturalWidth/im.naturalHeight).toFixed(2)+'px'}var s=$('.ft .big span');if(!s)return;s.style.setProperty('--fs','100px');var w=s.scrollWidth,W=s.parentNode.clientWidth;if(w)s.style.setProperty('--fs',Math.floor(100*W/w*.985)+'px')}
/* scroll-led: bar, tiles, the held story */
var stm=$('.stm'),tiles=$$('.tile'),phs=$$('.ph'),h2=stm&&$('.stm-a h2',stm),s3=$('.s3.pin'),s3in=s3&&$('.s3-in',s3),tick=false;
if(stm&&!rm&&tiles.length&&phs.length===tiles.length)stm.classList.add('fly');else stm=null;
function frame(){tick=false;var y=scrollY,vh=innerHeight;
  if(hd&&!hd.classList.contains('open'))hd.classList.toggle('shut',y>100);
  if(stm){var gone=.052*vh-h2.getBoundingClientRect().top,dur=.267*vh,step=.023*vh;
    if(gone<3*vh)tiles.forEach(function(t,i){var p=clamp((gone-i*step)/dur);if(p>=1){t.style.transform='';return}
      var s=t.parentNode.getBoundingClientRect(),h=phs[i].getBoundingClientRect(),k=h.width/s.width;p=p<.5?2*p*p:1-2*(1-p)*(1-p);var q=1-p;
      t.style.transform='translate('+((h.left-s.left)*q).toFixed(1)+'px,'+((h.top-s.top)*q).toFixed(1)+'px) scale('+(k+(1-k)*p).toFixed(4)+') rotate('+((i%2?-1:1)*8*Math.sin(Math.PI*p)).toFixed(2)+'deg)';});}
  if(s3&&!rm){var r=s3.getBoundingClientRect(),ih=s3in.offsetHeight,d=r.height-ih;if(d>4)s3.style.setProperty('--p',clamp(((vh-ih)/2-r.top)/d).toFixed(4));}}
function req(){if(!tick){tick=true;requestAnimationFrame(frame)}}
function relay(){barFit();bigFit();req()}
addEventListener('scroll',req,{passive:true});addEventListener('resize',relay);addEventListener('load',relay);
if(document.fonts&&document.fonts.ready)document.fonts.ready.then(relay);
relay();
})();
"""


def render(d: dict) -> str:
    g = d.get
    brand, pal, hero, media = g('brand') or {}, g('palette') or {}, g('hero') or {}, g('media') or {}
    bg, ink, accent = pal.get('ground', '#fafafa'), pal.get('ink', '#0f0f0f'), pal.get('accent', pal.get('ink', '#0f0f0f'))
    made = media.get('made') or {}
    nav, links = g('nav') or [], g('links') or []
    signin, cta = g('signin') or {}, g('cta') or {}
    out = []

    # ── which picture goes where (see NOTES.md, "Image slots")
    steps = [s for s in ((g('steps') or {}).get('items') or []) if s.get('k') or s.get('title')]
    known = {m['src']: m for k in ('screens', 'phones', 'photos') for m in (media.get(k) or []) if m.get('src')}
    in_steps = {s.get('img') for s in steps}
    def _up(m):
        return m.get('src') not in in_steps and (m.get('h') or 0) > (m.get('w') or 0) and not m.get('small')
    free_phones = [m for m in (media.get('phones') or []) if _up(m)]
    s1 = free_phones[0] if free_phones else None
    gal = [m for m in free_phones[1:] + (media.get('photos') or []) if _up(m)]
    gal = gal if len(gal) >= 3 else []
    screens = list(media.get('screens') or [])
    s2 = screens.pop(0) if screens else None
    s3 = screens.pop(0) if screens else None
    video = media.get('video')
    about_m = None if video else (screens.pop(0) if screens else None)
    blur, land, sheet, sky = made.get('blur') or [], made.get('land') or [], made.get('sheet') or [], made.get('sky')
    has_sky = bool(sky and sky.get('src'))

    # ── 0 bar
    logo = brand.get('logo')
    if logo:
        lg = '<img class="%s" src="%s%s" alt="%s">' % ('' if brand.get('logo_wordmark') else 'mark', P, e(logo), e(brand.get('name')) if brand.get('logo_wordmark') else '')
        if not brand.get('logo_wordmark'):
            lg += '<span>%s</span>' % e(brand.get('name'))
    else:
        lg = '<span>%s</span>' % e(brand.get('name'))
    drop_rows = ''.join('<li class="only-m"><a href="%s">%s</a></li>' % (e(n.get('h', '#')), e(n['t'])) for n in nav if n.get('t'))
    navset = {(n.get('t'), n.get('h')) for n in nav}
    drop_rows += ''.join('<li%s><a href="%s">%s%s</a></li>' % (' class="only-d"' if (l.get('t'), l.get('h')) in navset else '', e(l.get('h', '#')), e(l['t']), ('<span>%s</span>' % e(l['d'])) if l.get('d') else '') for l in links if l.get('t'))
    drop_rows += ''.join('<li class="only-m"><a href="%s">%s</a></li>' % (e(x.get('h', '#')), e(x['t'])) for x in (signin, cta) if x.get('t'))
    out.append('<a class="skip" href="#main">%s</a>' % e((hero.get('title') or brand.get('name') or '')[:60]))
    out.append('<div class="shade"></div><header class="hd"><div class="wrap"><div class="hd-in"><div class="pill">'
               '<a class="logo" href="%s" aria-label="%s">%s</a>' % (e(brand.get('home', '#')), e(brand.get('name')), lg)
               + ('<nav class="nav" aria-label="%s">%s</nav>' % (e(brand.get('name')), ''.join('<a href="%s">%s</a>' % (e(n.get('h', '#')), e(n['t'])) for n in nav if n.get('t'))) if nav else '')
               + ('<button class="tog" type="button" aria-label="Menu" aria-expanded="false" aria-controls="drop"><b></b><b></b></button>'
                  '<ul class="drop" id="drop">%s</ul>' % drop_rows if drop_rows else '')
               + '</div>'
               + ('<div class="acct">%s%s</div>' % (('<a class="tl" href="%s">%s</a>' % (e(signin.get('h', '#')), e(signin['t']))) if signin.get('t') else '', _btn(cta, 'dark', cls='sm')) if (signin.get('t') or cta.get('t')) else '')
               + '</div></div></header><main id="main">')

    # ── 1 opening
    if hero.get('title'):
        ov = ''
        pic = ''
        if sky and sky.get('src'):
            o = _over(sky.get('tone'), bg, ink)
            ov = ' style="--ov:%s;color:%s"' % (o['veil'], o['tx'])
            pic = _img(sky, 'sky', lazy=False, alt='', slot='opening-sky') + '<div class="skyv"></div>'
        out.append('<section class="hero"%s%s>%s<div class="wrap" style="display:flex;width:100%%"><div class="hero-c">'
                   '<h1 class="h1">%s</h1>' % (ov, '' if pic else ' data-slot="opening-sky"', pic, _words(hero['title']))
                   + ('<div class="sub">%s%s</div>' % (('<p class="h4">%s</p>' % e(hero['text'])) if hero.get('text') else '', _btn(hero.get('primary'), 'dark'))
                      if (hero.get('text') or (hero.get('primary') or {}).get('t')) else '')
                   + '</div></div></section>')

    # ── 2 band of marks
    marks = [('<img src="%s%s" alt="%s" loading="lazy">' % (P, e(l['src']), e(l.get('alt', ''))) if isinstance(l, dict) else '<span class="h4">%s</span>' % e(l))
             for l in (g('logos') or []) if (l.get('src') if isinstance(l, dict) else l)]
    note = hero.get('note')
    if not marks:
        marks = ['<span class="h4">%s</span>' % e(t) for t in (g('trust') or []) if t and t != note]
    if marks:
        reps = max(1, -(-12 // len(marks)))
        grp = ''.join(marks) * reps
        out.append('<section class="tick">' + ('<div class="wrap"><p class="body note rl">%s</p></div>' % e(note) if note else '')
                   + '<div class="mq"><div class="mq-t" data-v="150"><div class="mq-g">%s</div><div class="mq-g" aria-hidden="true">%s</div></div></div></section>' % (grp, grp))

    # ── 3 statement and the slab of tiles
    if hero.get('text2'):
        ws = str(hero['text2']).split()
        # the tiles are things to look at, so they are the client's own: product screens, then phone screens, then photographs
        # (never a library picture, never a bare colour — owner, 2026-11-13). A client with none has the statement without tiles.
        md_ = g('media') or {}
        own = [x for k in ('screens', 'phones', 'photos') for x in (md_.get(k) or []) if isinstance(x, dict) and x.get('src') and not x.get('lettering')]
        tiles = [dict(x, shot=1) for x in own[:5]] if len(own) >= 2 else []
        n = min(len(tiles), max(0, len(ws) // 3))
        tiles = tiles[:n]
        at = {}
        for k in range(n):
            pos = min(len(ws), max(1, round((k + .3) * len(ws) / n)))
            while pos in at and pos < len(ws):
                pos += 1
            at[pos] = k
        parts = []
        for i, w in enumerate(ws):
            parts.append('<span class="w" style="--i:%d">%s</span>' % (i, e(w)))
            if (i + 1) in at:
                parts.append('<span class="ph" aria-hidden="true"></span>')
        slab = ''
        if tiles:
            slab = '<div class="stm-b"><div class="slab">%s%s</div></div>' % (_img(sky, 'bk', alt='', slot='slab-sky') if (sky and sky.get('src')) else '', ''.join(
                '<div class="slot"><div class="tile"%s>%s</div></div>' % (
                    (' style="--c:%s"' % e(t['c'])) if t.get('c') else '',
                    _img(t, alt='', slot='tile-own') if t.get('src') else '') for t in tiles))
        out.append('<section class="stm"><div class="wrap"><div class="stm-a"><h2 class="h2 rf">%s</h2></div>%s</div></section>' % (' '.join(parts), slab))

    # ── 4-6 three stories: a feature's own words beside a general view of the product (alt stays the picture's alt)
    feats = g('features') or {}
    fit = [f for f in (feats.get('items') or []) if f.get('t')]
    slots = [(k, m) for k, m in (('one', s1), ('two', s2), ('held', s3)) if m]
    while slots and len(fit) - len(slots) < 3:
        slots.pop()
    told, fit = fit[:len(slots)], fit[len(slots):]
    for (k, m), f in zip(slots, told):
        tx = '<div class="tx"><h2 class="h2 rf">%s</h2>%s</div>' % (_words(f['t']), ('<p class="body rl">%s</p>' % e(f['d'])) if f.get('d') else '')
        md = '<div class="md rs">%s</div>' % _img(m, 'shot ' + _shape(m))
        if k == 'held':
            out.append('<section class="s3 pin"><div class="s3-in"><div class="s3-track">%s%s</div></div></section>' % (tx, md))
        else:
            out.append('<section class="st %s"><div class="wrap"><div class="grid">%s%s</div></div></section>' % (k, tx, md))

    # ── 7 cards
    if fit:
        crops = ['0% 0%', '100% 0%', '50% 0%', '22% 100%', '78% 0%', '50% 100%', '100% 100%', '0% 100%']
        cards = ''
        cown = [x for k in ('screens', 'phones', 'photos') for x in ((g('media') or {}).get(k) or []) if isinstance(x, dict) and x.get('src') and not x.get('lettering')]
        for i, f in enumerate(fit):
            # a card's picture is a thing to look at: the client's own screens and photographs in turn, each in another crop;
            # a client with fewer than two has cards of words (never a crop of a library picture — owner, 2026-11-13)
            x = cown[i % len(cown)] if len(cown) >= 2 else None
            pic = ('<div class="pic">%s</div>' % _img(x, alt='', slot='card-own').replace('<img ', '<img style="object-position:%s" ' % crops[i % len(crops)], 1)) if x else ''
            cards += '<li class="card rs" style="--d:%dms">%s<h3 class="h4">%s</h3>%s</li>' % (
                min(i, 4) * 80, pic, e(f['t']), ('<p class="small mute">%s</p>' % e(f['d'])) if f.get('d') else '')
        head = ''
        if feats.get('title') or feats.get('text'):
            head = '<div class="hdrow"><div class="l">%s%s</div>%s</div>' % (
                ('<h2 class="h3 rw">%s</h2>' % _words(feats['title'])) if feats.get('title') else '',
                ('<p class="body mute rl">%s</p>' % e(feats['text'])) if feats.get('text') else '', _btn(cta, 'light', arrow=True, cls='rs'))
        out.append('<section class="sec"><div class="wrap">%s<ul class="rail"%s>%s</ul></div></section>' % (head, ' tabindex="0"' if len(fit) > 4 else '', cards))

    # ── 8 ways: the list that opens
    if steps:
        st = g('steps') or {}
        withpic = [s for s in steps if s.get('img')]
        sw = ''
        if len(withpic) == len(steps):
            sw = '<div class="md sw rs" id="sw-ways">%s</div>' % ''.join(
                '<div%s>%s</div>' % (' class="on"' if i == 0 else '', _img(known.get(s['img'], {'src': s['img'], 'alt': ''}),
                                                                           'shot ' + ('book' if s.get('shape') == 'book' else _shape(known.get(s['img'], {}))))) for i, s in enumerate(steps))
        its = ''
        for i, s in enumerate(steps):
            body = ''.join('<p class="body">%s</p>' % e(x) for x in (s.get('title') if s.get('k') else None, s.get('text')) if x)
            its += ('<div class="acc-i"><h3 class="acc-h"><button class="acc-b h2" type="button" aria-expanded="%s" aria-controls="way-%d">%s</button></h3>'
                    '<div class="acc-c" id="way-%d"><div>%s%s</div></div></div>' % ('true' if i == 0 else 'false', i, e(s.get('k') or s.get('title')), i, body, _btn(s.get('cta'), 'light', arrow=True)))
        out.append('<section class="sec hl"><div class="wrap"><div class="grid">%s<div class="tx" style="%s">%s<div class="accs" data-sw="%s">%s</div></div></div></div></section>' % (
            sw, '' if sw else 'grid-column:1/13', ('<p class="cap rl">%s</p>' % e(st['title'])) if st.get('title') else '', 'sw-ways' if sw else '', its))

    # ── 9 gallery
    if gal:
        reps = max(1, -(-10 // len(gal)))
        grp = ''.join('<div class="gi"><div class="im">%s</div>%s</div>' % (
            _img(m, _shape(m)), '') for m in gal) * reps
        out.append('<section class="sec gal"><div class="wrap"><div class="gal-f rs"><div class="mq"><div class="mq-t" data-v="100"><div class="mq-g">%s</div>'
                   '<div class="mq-g" aria-hidden="true">%s</div></div></div></div></div></section>' % (grp, grp))

    # ── 10 head, text, one picture
    stt = g('statement') or {}
    if stt.get('title') or stt.get('text'):
        if video and video.get('src'):
            md = ('<video class="shot" src="%s%s" poster="%s%s" width="%s" height="%s" muted loop playsinline autoplay preload="none" aria-label="%s"></video>'
                  % (P, e(video['src']), P, e(video.get('poster', '')), video.get('w', ''), video.get('h', ''), e(video.get('alt', ''))))
        elif about_m:
            md = _img(about_m, 'shot ' + _shape(about_m))
        else:
            md = ''
        out.append('<section class="sec ab%s"><div class="wrap"><div class="grid"><div class="tx">%s%s</div>%s</div></div></section>' % (
            '' if md else ' solo', ('<h2 class="h3 rw">%s</h2>' % _words(stt['title'])) if stt.get('title') else '',
            ('<p class="body rl">%s</p>' % e(stt['text'])) if stt.get('text') else '', ('<div class="md rs">%s</div>' % md) if md else ''))

    # ── 10b figures, in the build of the reference's large-name list
    figs = [f for f in (g('figures') or []) if f.get('v')]
    if figs:
        style, pic = '', ''
        if has_sky:
            o = _over(sky.get('tone'), bg, ink)
            style = ' style="--fv:%s;--ftx:%s;--fdim:%s"' % (o['veil'], o['tx'], o['dim'])
            pic = _img(sky, 'bk flip', alt='', slot='figures-backdrop') + '<div class="vl"></div>'
        out.append('<section class="sec"><div class="wrap"><div class="fq-f rs%s"%s%s>%s<div class="grid"><ul class="tx fg">%s</ul></div></div></div></section>' % (
            '' if pic else ' plain', style, '' if pic else ' data-slot="figures-backdrop"', pic, ''.join(
                '<li><p class="v">%s</p>%s</li>' % (e(f['v']), ('<p class="body">%s</p>' % e(f['l'])) if f.get('l') else '') for f in figs)))

    # ── 11 two soft cards
    plans = g('plans') or {}
    pit = [p for p in (plans.get('items') or []) if p.get('name')]
    if pit:
        cs = ''
        for i, p in enumerate(pit):
            arrow = ('<a class="btn onsoft sq" href="%s" aria-label="%s"><i aria-hidden="true">→</i></a>' % (e(p['cta'].get('h', '#')), e(p['cta']['t']))) if (p.get('cta') or {}).get('t') else ''
            rows = ''.join('<li>%s</li>' % e(r) for r in (p.get('rows') or []))
            cs += ('<article class="dc rs%s" style="--d:%dms"><div class="dc-t"><h3 class="h3">%s</h3>%s</div>%s<div class="dc-b small mute">%s%s</div></article>' % (
                (' one' if len(pit) == 1 else '') + (' full' if rows else ''), (i % 2) * 100, e(p['name']), arrow,
                ('<div class="dc-m%s">%s<p class="h1">%s</p>%s</div>' % (' pic' if has_sky else '', (_img(sky, 'bk', alt='', slot='plan-sky').replace('<img ', '<img style="object-position:%s" ' % ('0% 100%', '100% 100%')[i % 2], 1) + '<div class="vl"></div>') if has_sky else '',
                                                                 e(p['price']), ('<p class="body">%s</p>' % e(p['per'])) if p.get('per') else '')) if p.get('price') else '',
                ('<p>%s</p>' % e(p['line'])) if p.get('line') else '', ('<ul>%s</ul>' % rows) if rows else ''))
        head = ''
        if plans.get('title') or plans.get('text'):
            head = '<div class="hdrow"><div class="l">%s%s</div></div>' % (
                ('<h2 class="h3 rw">%s</h2>' % _words(plans['title'])) if plans.get('title') else '',
                ('<p class="body mute rl">%s</p>' % e(plans['text'])) if plans.get('text') else '')
        out.append('<section class="sec db"><div class="wrap">%s<div class="grid">%s</div>%s</div></section>' % (
            head, cs, ('<p class="small mute note rl">%s</p>' % e(plans['note'])) if plans.get('note') else ''))

    # ── 12 questions over a picture
    faq = g('faq') or {}
    qs = [q for q in (faq.get('items') or []) if q.get('q') and q.get('a')]
    if qs:
        bkp = sky if (sky and sky.get('src')) else None
        style, pic = '', ''
        if bkp:
            o = _over(bkp.get('tone'), bg, ink)
            style = ' style="--fv:%s;--ftx:%s;--fdim:%s"' % (o['veil'], o['tx'], o['dim'])
            pic = _img(bkp, 'bk', alt='', slot='questions-backdrop') + '<div class="vl"></div>'
        its = ''.join('<div class="acc-i"><h3 class="acc-h"><button class="acc-b" type="button" aria-expanded="%s" aria-controls="q-%d">%s</button></h3>'
                      '<div class="acc-c" id="q-%d"><div><p class="body">%s</p></div></div></div>' % ('true' if i == 0 else 'false', i, e(q['q']), i, e(q['a'])) for i, q in enumerate(qs))
        out.append('<section class="sec"><div class="wrap"><div class="fq-f rs%s"%s%s>%s<div class="grid"><div class="tx q">%s<div class="accs">%s</div></div></div></div></div></section>' % (
            '' if pic else ' plain', style, '' if pic else ' data-slot="questions-backdrop"', pic, ('<p class="cap">%s</p>' % e(faq['title'])) if faq.get('title') else '', its))

    # ── 12b close, in the build of the reference's centred head with one button under it
    close = g('close') or {}
    if close.get('title'):
        out.append('<section class="sec cl"><div class="wrap"><h2 class="h3 rw">%s</h2>%s%s</div></section>' % (
            _words(close['title']), ('<p class="body rl">%s</p>' % e(close['text'])) if close.get('text') else '', _btn(close.get('cta'), 'dark', arrow=True, cls='rs')))

    out.append('</main>')

    # ── 13 foot
    foot = g('foot') or {}
    cols = [[(n.get('t'), n.get('h')) for n in nav if n.get('t')], [(l.get('t'), l.get('h')) for l in links if l.get('t')],
            [(x.get('t'), x.get('h')) for x in (signin, cta) if x.get('t')], [(l.get('t'), l.get('h')) for l in (foot.get('links') or []) if l.get('t')]]
    seen, uniq = set(), []
    for c in cols:
        c2 = [(t, h) for t, h in c if not ((t, h) in seen or seen.add((t, h)))]
        uniq.append(c2)
    cols = uniq
    colh = ''.join('<ul>%s</ul>' % ''.join('<li><a class="body" href="%s">%s</a></li>' % (e(h or '#'), e(t)) for t, h in c) for c in cols if c)
    if logo and brand.get('logo_wordmark'):
        big = '<img src="%s%s" alt="" loading="lazy">' % (P, e(logo))
    else:
        nm = str(brand.get('name') or '')
        big = '<span style="--fs:%.2fvw">%s</span>' % ((100 - 9.2) / max(1, len(nm) * .56), e(nm)) if nm else ''
    out.append('<footer class="ft%s">%s<div class="wrap">%s%s<div class="legal body">%s%s</div></div></footer>' % (
        ' pic' if has_sky else '', (_img(sky, 'bk', alt='', slot='foot-sky') + '<div class="vl"></div>') if has_sky else '',
        ('<div class="grid cols">%s</div>' % colh) if colh else '',
        ('<a class="big" href="%s" aria-label="%s">%s</a>' % (e(brand.get('home', '#')), e(brand.get('name')), big)) if big else '',
        ('<p>%s</p>' % e(foot['legal'])) if foot.get('legal') else '', ('<p class="small">%s</p>' % e(foot['text'])) if foot.get('text') else ''))

    title = ' — '.join(x for x in (brand.get('name'), hero.get('kicker') or hero.get('title')) if x)
    return ('<!doctype html><html lang="%s" class="no-js"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>%s</title><meta name="description" content="%s"><link rel="preconnect" href="https://fonts.googleapis.com">'
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="%s"><style>%s</style></head>'
            '<body style="%s">%s<script>document.documentElement.classList.remove("no-js");%s</script></body></html>' % (
                e(g('lang') or 'en'), e(title), e(hero.get('text') or ''), FONTS, CSS, _theme(bg, ink, accent, pal.get('extra')), ''.join(out), JS))
