"""wilsonharle — a law firm's page set in one quiet face on a dark room: a slow slideshow with the firm's sentence on it,
an index of what it does beside large ruled rows, then the parts its sub-pages are made of (text beside a full-height
photograph, tinted tiles, portrait tiles, a ruled fee list, the address in large type).
Measured on https://wilsonharle.com (home, /people, /services, /contact, /pages/about-us) on 2026-11-12. See NOTES.md.
render(d) is pure: no file reads, no model, one self-contained page."""
from html import escape as _e

PRE = '../../'          # a page in <slug>/out/ reaches media/ two levels up
MONO = True             # every photograph of the reference is black-and-white; the client's are shown without colour


# ---------- small helpers ----------
def e(s): return _e(str(s or ''), quote=True)
def _hex(c):
    c = (c or '').strip().lstrip('#')
    if len(c) == 3: c = ''.join(x * 2 for x in c)
    try: return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))
    except Exception: return (128, 128, 128)
def _css(c): return '#%02x%02x%02x' % tuple(max(0, min(255, round(v))) for v in c)
def _mix(a, b, t): return tuple(a[i] * (1 - t) + b[i] * t for i in range(3))
def _lum(c):
    f = lambda v: v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4
    r, g, b = (f(v / 255) for v in c); return .2126 * r + .7152 * g + .0722 * b
def _con(a, b):
    x, y = _lum(a), _lum(b); return (max(x, y) + .05) / (min(x, y) + .05)
def _toward(c, to, against, need):
    """c moved toward `to` in small steps until it reads `need`:1 against `against`."""
    t = 0.0
    while _con(_mix(c, to, t), against) < need and t < 1: t += .04
    return _mix(c, to, min(t, 1))
def _a(o, cls='', extra=''):
    if not o or not o.get('t'): return ''
    h = o.get('h')
    if not h: return f'<span class="{cls}">{e(o["t"])}</span>'
    return f'<a class="{cls}" href="{e(h)}"{extra}>{e(o["t"])}</a>'
def _tel(s): return 'tel:' + ''.join(ch for ch in str(s) if ch.isdigit() or ch == '+')
def _img(p, cls='', eager=False, pos=None):
    st = f' style="object-position:{pos}"' if pos else ''
    lazy = '' if eager else ' loading="lazy"'
    return (f'<img class="{cls}" src="{e(PRE + p["src"])}" width="{int(p.get("w") or 0)}" height="{int(p.get("h") or 0)}" '
            f'alt="{e(p.get("alt"))}"{lazy} decoding="async"{st}>')
def _addr(a):
    if not a: return []
    l1 = a.get('street'); l2 = ' '.join(x for x in [a.get('postcode'), a.get('city')] if x)
    l3 = ', '.join(x for x in [a.get('region'), a.get('country')] if x)
    return [x for x in [l1, l2, l3] if x]
def _hours(hs):
    out = []
    for h in hs or []:
        t = ' – '.join(x for x in [h.get('open'), h.get('close')] if x)
        out.append(' '.join(x for x in [h.get('days'), t] if x))
    return [x for x in out if x]


# ---------- photographs: each slot takes one by role, size and proportion; each picture once ----------
def _pick(d):
    ph = [p for p in ((d.get('media') or {}).get('photos') or []) if p.get('src') and p.get('w') and p.get('h')]
    team = d.get('team') or {}
    people = list(team.get('items') or []) + [m for g in team.get('groups') or [] for m in g.get('items') or []]
    owner = {m['img']: m for m in people if m.get('img')}
    badge = {c.get('img') for c in d.get('credentials') or [] if c.get('img')}
    free = [p for p in ph if p['src'] not in owner and p['src'] not in badge and not p.get('small')
            and p.get('role') not in ('portrait', 'product')]
    used, slot = set(), {}
    def take(test, prefer=()):
        c = [p for p in free if p['src'] not in used and test(p)]
        c.sort(key=lambda p: (0 if p.get('role') in prefer else 1))
        if c: used.add(c[0]['src']); return c[0]
    # the slideshow: wide photographs that fill 1328 px without being enlarged much (from 1300), three at most;
    # a person's own wide portrait may stand there with the name beside it, as on the reference
    slides = []
    for p in ph:
        if len(slides) == 3: break
        if p['w'] >= 1300 and p['w'] / p['h'] >= 1.2 and not p.get('small') and p['src'] not in badge and p.get('role') != 'product':
            if p['src'] in owner or p in free: slides.append(p); used.add(p['src'])
    slot['slides'] = [(p, owner.get(p['src'])) for p in slides]
    # the column beside the firm's own words: upright first, else a picture tall enough to fill it
    slot['about'] = take(lambda p: p['h'] > p['w'] and p['w'] >= 600) or take(lambda p: p['h'] >= 760 and p['w'] >= 600)
    quad = lambda p: p['w'] >= 720 and p['h'] >= 360          # 720×450 at the top right of a section
    slot['people'] = take(quad, ('people', 'room', 'workshop'))
    slot['services'] = take(quad, ('work', 'action', 'room', 'workshop', 'detail'))
    slot['contact'] = take(lambda p: p['w'] >= 1000 and p['h'] >= 600, ('exterior', 'room', 'landscape'))
    return slot, owner


CSS = r"""
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;overflow-x:clip}
body{margin:0;background:var(--g);color:var(--t);font:300 16px/22px var(--sans);overflow-x:clip;-webkit-font-smoothing:antialiased}
img{display:block;max-width:100%}
a{color:inherit;text-decoration:none}
h1,h2,h3,h4,p,ul,ol,dl,dd,figure,blockquote{margin:0;padding:0}
ul,ol{list-style:none}
:focus-visible{outline:2px solid var(--a);outline-offset:4px;border-radius:2px}
.mono img.ph{filter:grayscale(1)}
.w{padding:0 56px;position:relative;z-index:1}
.serif{font-family:var(--serif);font-weight:400}
.lab{font:400 16px/20px var(--sans);color:var(--l)}
.st{font:400 28px/38px var(--serif);letter-spacing:-.4px;color:var(--t)}
.lk{font:400 16px/16px var(--sans);color:var(--l);transition:color .5s}
.lk:hover{color:var(--a)}
/* header: 142 high, sticks 38 above the window so 104 stay; its ground stops 14 px short of both edges, 5 px corners below */
.hd{position:sticky;top:-38px;z-index:50;height:142px}
.hd-in{margin:0 14px;height:100%;background:var(--g);border-radius:0 0 5px 5px;display:flex;justify-content:space-between;align-items:flex-start;padding:0 56px;gap:40px}
.brand{font:400 var(--bs)/22px var(--serif);letter-spacing:var(--bt);text-transform:uppercase;color:var(--l);margin-top:60px;white-space:nowrap}
.nav-d{display:flex;flex-wrap:wrap;justify-content:flex-end;gap:10px clamp(20px,3.3vw,48px);margin-top:67px;padding-right:14px;flex:1 1 0;min-width:0}
.nav-d a{font:400 14px/14px var(--serif);color:var(--t);transition:color .525s;white-space:nowrap}
.nav-d a:hover{color:var(--a)}
.nav-m{display:none}
/* first screen: a 90vh room, 56 px in from both sides; photographs fade out and in on it; the sentence stays */
.hero{padding-bottom:165px}
.sl{position:relative;background:var(--k);height:90vh;min-height:560px;max-height:900px;overflow:hidden;animation:in 2.4s linear .3s both}
.sl.bare{height:auto;min-height:0;max-height:none;padding-top:150px}
@keyframes in{from{opacity:0}to{opacity:1}}
.slide{position:absolute;inset:0;opacity:0;transition:opacity 1.5s ease-in-out}
.slide.on{opacity:1}
.slide img{width:100%;height:100%;object-fit:cover;object-position:50% 18%}
.cap{position:absolute;right:56px;bottom:80px;z-index:3;display:flex;align-items:center;gap:16px;font:400 16px/16px var(--sans);color:#fff}
.cap i{width:160px;height:1px;background:rgb(var(--tr)/.2)}
.copy{position:absolute;left:0;right:0;bottom:0;z-index:2;padding:190px 56px 80px}
.sl.pic .copy{background:linear-gradient(to top,rgb(var(--kr)/.93) 0,rgb(var(--kr)/.86) calc(100% - 190px),rgb(var(--kr)/.72) calc(100% - 150px),rgb(var(--kr)/.5) calc(100% - 105px),rgb(var(--kr)/.26) calc(100% - 60px),rgb(var(--kr)/.09) calc(100% - 25px),rgb(var(--kr)/0) 100%)}
.sl.bare .copy{position:relative;padding-top:0}
.copy h1,.copy .st{font:400 28px/38px var(--serif);letter-spacing:-.4px;color:var(--t);max-width:810px}
.copy .acts{display:flex;flex-wrap:wrap;gap:14px 36px;margin-top:30px;align-items:baseline;max-width:810px}
.copy .acts span{font:300 16px/16px var(--sans);color:var(--t)}
.sl.capd .copy{padding-right:420px}
/* index: 454 | 30 | 844 */
.ix{display:flex;gap:30px;align-items:flex-start;padding-bottom:60px}
.ix>.c1{flex:0 0 454px;max-width:454px}
.ix>.c2{flex:1 1 0;min-width:0}
.ix .lab{line-height:16px;margin-bottom:57px}
.sv li{margin-bottom:17px;max-width:350px}
.sv a,.sv span{font:300 16px/22px var(--sans);color:var(--t);transition:color .4s}
.sv a:hover{color:var(--a)}
.sv p{font:300 16px/22px var(--sans);color:var(--t)}
.c1 .gt{font:300 16px/22px var(--sans);color:var(--t);max-width:350px}
.c1 .lab:has(+ .gt){margin-bottom:24px}
.rows{margin-top:-27px}
.row{display:flex;gap:40px;justify-content:space-between;align-items:flex-start;padding:32px 0;border-bottom:1px solid rgb(var(--tr)/.2)}
.row .m{min-width:0;flex:1 1 auto}
.row .rt{font:400 28px/38px var(--serif);letter-spacing:-1px;color:var(--t);transition:color .6s;overflow-wrap:anywhere}
a.row:hover .rt,.row a.rt:hover{color:var(--a)}
.row .rn{font:400 16px/22px var(--sans);color:var(--l);margin-top:6px}
.row .rd{font:300 16px/22px var(--sans);color:var(--t);margin-top:10px;max-width:656px}
.row ul.rd li{padding-left:16px;position:relative}
.row ul.rd li::before{content:"";position:absolute;left:0;top:11px;width:6px;height:1px;background:var(--t)}
.row .rp{flex:0 0 auto;max-width:46%;text-align:right;font:400 28px/38px var(--serif);letter-spacing:-1px;color:var(--t)}
.row .rp small{display:block;font:300 16px/22px var(--sans);letter-spacing:0;color:var(--t)}
.row .rp .lk{display:inline-block;margin-top:14px;letter-spacing:0}
.more{display:inline-block;padding:30px 0}
.note{font:300 16px/22px var(--sans);color:var(--t);margin-top:30px;max-width:656px}
.qt .rt{letter-spacing:0}
.qt.long .rt{font-size:19px;line-height:28px;letter-spacing:0}
.qt .by{display:flex;align-items:center;gap:16px;margin-top:22px;font:400 16px/20px var(--sans);color:var(--l)}
.qt .by i{flex:0 0 auto;width:160px;height:1px;background:rgb(var(--tr)/.2)}
details.row{display:block}
details.row summary{cursor:pointer;list-style:none}
details.row summary::-webkit-details-marker{display:none}
details.row summary:hover{color:var(--a)}
details.row .ans{font:400 16px/23px var(--serif);color:var(--t);max-width:656px;margin-top:18px}
/* a section that opens like the reference's sub-pages: label, 59, a 28px sentence 656 wide, 80, then its grid */
.sec{position:relative;padding:80px 0 60px}
.sec .hdg{max-width:656px;margin-bottom:80px}
.sec .hdg .lab{margin-bottom:59px}
.sec .hdg.nost .lab{margin-bottom:0}
.bd{position:sticky;top:0;height:450px;margin-bottom:-450px;z-index:0;pointer-events:none}
.bd img{position:absolute;right:0;top:0;width:50vw;height:450px;object-fit:cover;opacity:var(--bo);-webkit-mask-image:linear-gradient(to right,transparent,#000 30%),linear-gradient(to top,transparent,#000 34%);-webkit-mask-composite:source-in;mask-image:linear-gradient(to right,transparent,#000 30%),linear-gradient(to top,transparent,#000 34%);mask-composite:intersect}
.bd.full{height:100vh;margin-bottom:-100vh}
.bd.full img{left:0;width:100%;height:100%;opacity:.1;-webkit-mask-image:none;mask-image:none}
.sec.hasbd{padding-top:0}
.sec.hasbd>.w{padding-top:80px}
.tiles{display:grid;gap:16px}
.tiles.t4{grid-template-columns:repeat(4,minmax(0,1fr))}
.tiles.t3{grid-template-columns:repeat(3,minmax(0,1fr))}
.tile{position:relative;min-height:300px;border-radius:5px;overflow:hidden;display:flex;flex-direction:column;justify-content:space-between;gap:28px;padding:20px 24px 22px}
.tile.sv-t{background-color:var(--r);color:var(--g);transition:background-color .2s}
.tile.sv-t:hover{background-color:var(--f)}
.tile h3{font:400 24px/30px var(--serif);max-width:280px;overflow-wrap:anywhere}
.tile p{font:400 14px/20px var(--sans)}
.tile.pp{background:var(--k);padding:0;justify-content:flex-end;color:var(--t);aspect-ratio:1/1}
.tile.pp img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:50% 20%;transition:opacity .2s}
.tile.pp:hover img{opacity:.65}
.tile.pp .tx{position:relative;padding:64px 24px 18px;background:linear-gradient(to top,rgb(var(--kr)/.94) 0,rgb(var(--kr)/.88) calc(100% - 64px),rgb(var(--kr)/.5) calc(100% - 32px),rgb(var(--kr)/0) 100%)}
.tile.pp h3{font:400 19px/25px var(--serif);max-width:none}
.tile.pp .ro{font:400 19px/25px var(--serif)}
.pt .ct{font:300 14px/20px var(--sans);color:var(--t);margin:10px 0 14px;overflow-wrap:anywhere}
.pt .ct a{display:block}
.pt a:hover,.pl a:hover{color:var(--a)}
.gl{margin:60px 0 30px}
.gl:first-child{margin-top:0}
.pl{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:0 16px;margin-top:60px}
.tiles+.pl{margin-top:60px}
.pl li{padding:18px 0 20px;border-top:1px solid rgb(var(--tr)/.2);overflow-wrap:anywhere}
.pl h3{font:400 19px/25px var(--serif);color:var(--t)}
.pl p{font:300 16px/22px var(--sans);color:var(--t)}
.pl .ct{font-size:14px;line-height:20px;margin-top:6px}
/* text beside a full-height photograph: side list 156 | 40 | text 546 | 40 | picture to the window's edge */
.ab{display:grid;grid-template-columns:156px 546px minmax(0,1fr);column-gap:40px;padding:0 0 0 56px;position:relative;z-index:1;margin-bottom:60px}
.ab.nopic{grid-template-columns:156px 546px}
.ab.noside{grid-template-columns:546px minmax(0,1fr)}
.ab.noside.nopic{grid-template-columns:546px}
.side{padding-top:100px}
.side ul{border-top:1px solid rgb(var(--tr)/.2)}
.side li{border-bottom:1px solid rgb(var(--tr)/.2)}
.side a,.side span{display:block;padding:17px 0 18px;font:300 16px/22px var(--sans);color:var(--t);transition:color .4s;overflow-wrap:anywhere}
.side a:hover{color:var(--a)}
.abt{padding:94px 0 60px}
.abt .sm{font:400 14px/20px var(--sans);color:var(--t);margin-bottom:10px}
.abt h2{font:400 36px/38px var(--serif);color:var(--t);margin-bottom:50px;overflow-wrap:anywhere}
.abt h2 a{transition:color .5s}.abt h2 a:hover{color:var(--a)}
.abt p.tx{font:400 16px/23px var(--serif);color:var(--t);margin-bottom:20px}
.abt .acts{display:flex;flex-wrap:wrap;gap:14px 36px;margin-top:30px}
.abt .acts a.pl2{font:300 16px/22px var(--sans);color:var(--t);overflow-wrap:anywhere}
.abt .acts a.pl2:hover{color:var(--a)}
.fig{margin-top:50px;border-top:1px solid rgb(var(--tr)/.2)}
.fig li{display:flex;gap:24px;align-items:baseline;padding:16px 0 17px;border-bottom:1px solid rgb(var(--tr)/.2)}
.fig b{flex:0 0 132px;font:400 28px/38px var(--serif);letter-spacing:-1px;color:var(--t);overflow-wrap:anywhere}
.fig span{font:300 16px/22px var(--sans);color:var(--t)}
.abp{position:relative;min-height:900px}
.abp img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.abp.sm-pic{min-height:0;align-self:start;justify-self:end;width:100%}
/* contact: the address and the telephone in 28px, the rest in 16px, on a photograph held at a tenth */
.ct-sec{position:relative;min-height:735px;padding:0 0 60px}
.ct-sec>.w{padding-top:150px}
.ct-sec .hdg{max-width:656px;margin-bottom:70px}
.ct-sec .hdg .lab{margin-bottom:59px}
.ct-sec .hdg .acts{margin-top:30px}
.big{display:block;font:400 28px/38px var(--serif);color:var(--t);max-width:520px;margin-bottom:40px;transition:color .5s;overflow-wrap:anywhere}
a.big:hover{color:var(--a)}
.big small{display:block;font:300 16px/22px var(--sans)}
.dt{max-width:350px;font:300 16px/22px var(--sans);color:var(--t);margin-top:10px}
.dt p{margin-bottom:22px}
.dt a.em{font-size:18px}
.dt a:hover{color:var(--a)}
.offs{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:40px 16px;margin-top:70px}
.off h3{font:400 28px/38px var(--serif);letter-spacing:-1px;color:var(--t);margin-bottom:14px}
.off p{font:300 16px/22px var(--sans);color:var(--t);margin-bottom:12px;max-width:380px;overflow-wrap:anywhere}
.off a:hover{color:var(--a)}
.cr{margin-top:90px}
.cr .lab{margin-bottom:30px}
.cr ul{border-top:1px solid rgb(var(--tr)/.2)}
.cr li{display:flex;gap:30px;align-items:center;justify-content:space-between;padding:20px 0;border-bottom:1px solid rgb(var(--tr)/.2)}
.cr h3{font:400 19px/25px var(--serif);color:var(--t)}
.cr p{font:300 16px/22px var(--sans);color:var(--t);max-width:760px}
.cr img{flex:0 0 auto;width:auto;height:auto;max-height:84px;max-width:150px;border-radius:2px}
.cr a:hover{color:var(--a)}
/* foot: a rule, the name at the left, 14px lines at the right */
.ft{padding:40px 56px 0;position:relative;z-index:1;background:var(--g)}
.ft-in{border-top:1px solid rgb(var(--tr)/.2);margin-top:67px;padding:40px 0 42px;display:flex;justify-content:space-between;align-items:flex-end;gap:60px}
.ft .brand{margin:0}
.ft .r{text-align:right;max-width:720px;font:400 14px/20px var(--serif);color:var(--t)}
.ft .r p{margin-top:8px}
.ft .r p:first-child{margin-top:0}
.ft .fl{display:flex;flex-wrap:wrap;justify-content:flex-end;gap:6px 24px}
.ft a{transition:color .5s}
.ft a:hover{color:var(--a)}
@media (max-width:1180px){.tiles.t4{grid-template-columns:repeat(3,minmax(0,1fr))}.ix>.c1{flex-basis:320px}.ab{grid-template-columns:156px minmax(0,546px) minmax(0,1fr)}.ab.nopic{grid-template-columns:156px minmax(0,546px)}}
@media (max-width:991px){
.w{padding:0 14px}
.hd{height:126px;top:-28px}
.hd-in{margin:0;padding:0 18px;border-radius:0}
.brand{margin-top:52px;font-size:var(--bsm);letter-spacing:var(--btm);position:relative;z-index:3;white-space:normal;min-width:0;line-height:18px}
.nav-d{display:none}
.nav-m{display:block;margin-top:38px;flex:0 0 auto}
.nav-m summary{list-style:none;cursor:pointer;width:50px;height:41px;position:relative;z-index:3;display:block;margin-right:-12px}
.nav-m summary::-webkit-details-marker{display:none}
.nav-m summary i{position:absolute;left:13px;width:25px;height:1px;background:var(--t);top:13px}
.nav-m summary i:nth-child(2){top:19px}.nav-m summary i:nth-child(3){top:25px}
.nav-m .menu{position:fixed;left:0;right:0;top:0;height:100vh;height:100dvh;background:var(--g);z-index:2;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:20px;padding:110px 14px 40px;overflow:auto}
.nav-m .menu a{font:400 26px/26px var(--serif);color:var(--t);text-align:center}
.sl{height:90vh;min-height:520px}
.copy{padding:150px 20px 20px}
.sl.pic .copy{background:linear-gradient(to top,rgb(var(--kr)/.93) 0,rgb(var(--kr)/.86) calc(100% - 150px),rgb(var(--kr)/.7) calc(100% - 115px),rgb(var(--kr)/.45) calc(100% - 75px),rgb(var(--kr)/.2) calc(100% - 40px),rgb(var(--kr)/0) 100%)}
.sl.capd .copy{padding-right:20px}
.sl.bare{padding-top:90px}
.copy h1,.copy .st{font-size:20px;line-height:27px}
.cap{position:static;margin-top:26px;gap:0}.cap i{display:none}
.ix{flex-direction:column;gap:46px;padding:0 28px 60px}
.ix.home{flex-direction:column-reverse;gap:80px}
.ix .c1:empty{display:none}
.side{order:3}
.ix>.c1,.ix>.c2{flex:none;width:100%;max-width:none}
.row{flex-direction:column;gap:12px}
.row .rt{font-size:24px;line-height:34px}
.row .rp{max-width:none;text-align:left;font-size:24px;line-height:34px}
.qt .by i{width:60px}
.st{font-size:27px;line-height:35px}
.tiles.t4,.tiles.t3{grid-template-columns:minmax(0,1fr)}
.tile h3{font-size:22px;line-height:27px}

.pl{grid-template-columns:minmax(0,1fr)}
.ab,.ab.nopic,.ab.noside,.ab.noside.nopic{display:flex;flex-direction:column;padding:0 14px}
.abp{order:-1;min-height:360px;height:360px}
.abp.sm-pic{height:auto;min-height:0}
.abt{padding:40px 0 40px}
.abt .sm{margin-top:54px}
.abt h2{font-size:26px;line-height:34px;margin-bottom:60px}
.side{padding-top:0;padding-bottom:20px}
.fig b{flex-basis:104px;font-size:24px;line-height:34px}
.big{font-size:27px;line-height:35px}
.offs{grid-template-columns:minmax(0,1fr)}
.cr li{flex-direction:column;align-items:flex-start;gap:14px}
.ft{padding:40px 28px 0}
.ft-in{flex-direction:column;align-items:center;gap:22px;padding-bottom:36px}
.ft .r{text-align:center}.ft .fl{justify-content:center}
}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}html{scroll-behavior:auto}}
"""

JS = r"""
(function(){
var s=[].slice.call(document.querySelectorAll('.slide'));
if(s.length>1&&!matchMedia('(prefers-reduced-motion: reduce)').matches){var i=0;
/* measured: every 6 s the photograph fades to the dark over 1.5 s (ease-in-out) and the next comes up over 1.5 s */
setInterval(function(){if(document.hidden)return;s[i].classList.remove('on');i=(i+1)%s.length;var n=s[i];setTimeout(function(){n.classList.add('on')},1500)},6000);}
var m=document.querySelector('.nav-m');
if(m){m.addEventListener('click',function(ev){if(ev.target.closest('.menu a'))m.open=false});
document.addEventListener('keydown',function(ev){if(ev.key==='Escape'&&m.open){m.open=false;m.querySelector('summary').focus()}});}
})();
"""


def render(d: dict) -> str:
    d = d or {}
    g = lambda k: d.get(k) or {}
    brand, hero, pal = g('brand'), g('hero'), g('palette')
    name = brand.get('name') or ''
    # ---- colour: the reference is a dark room with pale ink, a still darker pit under pictures, and one accent that
    # only appears when something is pointed at. The client's darker colour becomes the room, the lighter the ink.
    c1, c2 = _hex(pal.get('ground') or '#181717'), _hex(pal.get('ink') or '#fff4d9')
    G, T = (c1, c2) if _lum(c1) < _lum(c2) else (c2, c1)
    while _lum(G) > .03: G = _mix(G, (0, 0, 0), .1)
    T = _toward(T, (255, 255, 255), G, 12)
    K = _mix(G, (0, 0, 0), .62)
    L = _mix(T, (255, 255, 255), .7)
    A0 = _hex(pal.get('accent') or '#fc0000')
    A = _toward(A0, T, G, 4.6)
    # the dim photograph at a section's top right: as bright as the reference's (.45) unless a white pixel of it would
    # take the ink under 4.6:1
    bo = .45
    while bo > .12 and _con(T, _mix(G, (255, 255, 255), bo)) < 4.7: bo -= .03
    # tiles: one family — the accent stepped toward the ink — held at 60 % over the room, full when pointed at
    def tile(i):
        full = _mix(A0, T, (0, .5, .82, .28, .66, .14)[i % 6])
        t = 0.0
        while t < 1:
            f = _mix(full, T, t); rest = _mix(G, f, .6)
            if _con(rest, G) >= 4.6: break
            t += .05
        return _css(rest), _css(f)
    slot, owner = _pick(d)
    P = []

    # ---- header
    nav = [n for n in d.get('nav') or [] if n and n.get('t')]
    cta = g('cta')
    if cta.get('t') and not any((n.get('t') or '').strip().lower() == cta['t'].strip().lower() for n in nav): nav = nav + [cta]
    links_html = ''.join(f'<a href="{e(n.get("h") or "#")}">{e(n["t"])}</a>' for n in nav)
    n = max(len(name), 1)
    bs = 17 if n <= 26 else max(11, round(17 * 26 / n, 1)); bsm = 14 if n <= 17 else max(10.5, round(14 * 17 / n, 1))
    home = brand.get('home') or '#'
    P.append(f'<header class="hd"><div class="hd-in"><a class="brand" href="{e(home)}">{e(name)}</a>'
             + (f'<nav class="nav-d" aria-label="{e(name)}">{links_html}</nav>'
                f'<details class="nav-m"><summary aria-label="Menu"><i></i><i></i><i></i></summary><nav class="menu">{links_html}</nav></details>' if nav else '')
             + '</div></header>')

    # ---- first screen
    P.append('<main>')
    slides = slot['slides']
    title = hero.get('title') or name
    acts = ''.join(x for x in [_a(hero.get('primary'), 'lk'), _a(hero.get('secondary'), 'lk')] if x)
    note = hero.get('note')
    if note:
        ph = (g('place').get('phone') or g('contact').get('phone') or {})
        acts += (f'<a class="lk" href="{e(ph.get("h") or _tel(note))}">{e(note)}</a>' if note.strip()[:1] in '+0123456789(' and sum(ch.isdigit() for ch in note) >= 6
                 else f'<span>{e(note)}</span>')
    sl = ''
    capd = False
    for i, (p, who) in enumerate(slides):
        cap = ''
        if who and who.get('name'):
            capd = True
            cap = f'<p class="cap"><i></i>{e(who["name"])}{", " + e(who["role"]) if who.get("role") else ""}</p>'
        sl += f'<div class="slide{" on" if i == 0 else ""}">{_img(p, "ph", eager=(i == 0))}{cap}</div>'
    P.append(f'<section class="hero w"><div class="sl {"pic" if slides else "bare"}{" capd" if capd else ""}">{sl}<div class="copy"><h1>{e(title)}</h1>'
             + (f'<p class="st">{e(hero["text"])}</p>' if hero.get('text') else '')
             + (f'<p class="acts">{acts}</p>' if acts else '') + '</div></div></section>')

    # ---- index: what the firm does (names) beside large ruled rows
    feats = [f for f in g('features').get('items') or [] if f and f.get('t')]
    steps = [s for s in g('steps').get('items') or [] if s and (s.get('title') or s.get('k'))]
    tiles_on = bool(feats)
    c1h = c2h = ''
    if feats:
        c1h = (f'<h2 class="lab">{e(g("features").get("title"))}</h2>' if g('features').get('title') else '') + '<ul class="sv">' + ''.join(
            f'<li><a href="#s{i}">{e(f["t"])}</a></li>' for i, f in enumerate(feats)) + '</ul>'
    if steps:
        rows = ''
        for s in steps:
            h = (s.get('cta') or {}).get('h')
            inner = f'<div class="m"><h3 class="rt">{e(s.get("title") or s.get("k"))}</h3>' + (f'<p class="rd">{e(s["text"])}</p>' if s.get('text') else '') + '</div>'
            rows += f'<a class="row" href="{e(h)}">{inner}</a>' if h else f'<div class="row">{inner}</div>'
        c2h = (f'<h2 class="lab">{e(g("steps").get("title"))}</h2>' if g('steps').get('title') else '') + f'<div class="rows">{rows}</div>'
        if g('steps').get('text'): c2h += f'<p class="note">{e(g("steps")["text"])}</p>'
    if c1h or c2h:
        P.append(f'<section class="ix home w"><div class="c1">{c1h}</div><div class="c2">{c2h}</div></section>')

    # ---- text beside a full-height photograph (the firm's own words; and a person, when the team is one or two)
    def about(small, head, paras, pic, side='', extra='', small_pic=False, sid='', href=None):
        cls = 'ab' + ('' if pic else ' nopic') + ('' if side else ' noside')
        col = ''
        if pic:
            st = f' style="max-width:{int(pic["w"])}px;aspect-ratio:{int(pic["w"])}/{int(pic["h"])}"' if small_pic else ''
            col = f'<div class="abp{" sm-pic" if small_pic else ""}"{st}>{_img(pic, "ph")}</div>'
        return (f'<section class="{cls}"{" id=" + sid if sid else ""}>{side}<div class="abt">' + (f'<p class="sm">{e(small)}</p>' if small else '')
                + ((f'<h2><a href="{e(href)}">{e(head)}</a></h2>' if href else f'<h2>{e(head)}</h2>') if head else '') + ''.join(f'<p class="tx">{e(t)}</p>' for t in paras if t) + extra + f'</div>{col}</section>')
    stm = g('statement')
    lks = [l for l in d.get('links') or [] if l and l.get('t')]
    figs = [f for f in d.get('figures') or [] if f and f.get('v')]
    if stm.get('title') or stm.get('text'):
        side = ('<nav class="side"><ul>' + ''.join(f'<li>{_a(l)}</li>' for l in lks) + '</ul></nav>') if lks else ''
        fig = ('<ul class="fig">' + ''.join(f'<li><b>{e(f["v"])}</b><span>{e(f.get("l"))}</span></li>' for f in figs) + '</ul>') if figs else ''
        P.append(about(hero.get('kicker'), stm.get('title'), [stm.get('text')], slot['about'], side, fig, sid='about'))

    # ---- services: tinted tiles, four across
    if tiles_on and any(f.get('d') for f in feats):
        ft = g('features')
        bdp = slot['services']
        tl = ''
        for i, f in enumerate(feats):
            rest, full = tile(i)
            tl += (f'<div class="tile sv-t" id="s{i}" style="--r:{rest};--f:{full}">'
                   f'<h3>{e(f["t"])}</h3>' + (f'<p>{e(f["d"])}</p>' if f.get('d') else '') + '</div>')
        hd = (f'<h2 class="lab">{e(ft.get("title"))}</h2>' if ft.get('title') else '') + (f'<p class="st">{e(ft["text"])}</p>' if ft.get('text') else '')
        P.append(f'<section class="sec{" hasbd" if bdp else ""}" id="services">' + (f'<div class="bd">{_img(bdp, "ph")}</div>' if bdp else '')
                 + '<div class="w">' + (f'<div class="hdg{"" if ft.get("text") else " nost"}">{hd}</div>' if hd else '') + f'<div class="tiles t4">{tl}</div></div></section>')
    elif tiles_on:
        pass  # names only: the index list above is all there is to say

    # ---- fees: the catalogue and the plans in the large ruled rows
    def price_cell(it):
        out = ''
        if it.get('price'): out += e(it['price'])
        for p in it.get('prices') or []:
            out += f'<small>{e(p.get("label"))}</small>{e(p.get("price"))}'
        if it.get('per'): out += f'<small>{e(it["per"])}</small>'
        if it.get('state'): out += f'<small>{e(it["state"])}</small>'
        return out
    def fee_row(it, nm):
        m = f'<h3 class="rt">' + (f'<a class="rt" href="{e(it["h"])}">{e(nm)}</a>' if it.get('h') else e(nm)) + '</h3>'
        if it.get('note'): m += f'<p class="rn">{e(it["note"])}</p>'
        for k in ('line', 'text'):
            if it.get(k): m += f'<p class="rd">{e(it[k])}</p>'
        if it.get('rows'): m += '<ul class="rd">' + ''.join(f'<li>{e(r)}</li>' for r in it['rows'] if r) + '</ul>'
        pc = price_cell(it)
        if it.get('cta') and (it['cta'] or {}).get('t'): pc += ('<br>' if pc else '') + _a(it['cta'], 'lk')
        return f'<div class="row"><div class="m">{m}</div>' + (f'<div class="rp">{pc}</div>' if pc else '') + '</div>'
    cat = g('catalogue')
    groups = [gr for gr in cat.get('groups') or [] if gr and gr.get('items')]
    if groups:
        if cat.get('title') or cat.get('text'):
            P.append('<section class="sec" id="fees" style="padding-bottom:0"><div class="w"><div class="hdg' + ('' if cat.get('text') else ' nost') + '">'
                     + (f'<h2 class="lab">{e(cat["title"])}</h2>' if cat.get('title') else '') + (f'<p class="st">{e(cat["text"])}</p>' if cat.get('text') else '') + '</div></div></section>')
        for gi, gr in enumerate(groups):
            lab = _a({'t': gr.get('t'), 'h': gr.get('h')}) if gr.get('t') else ''
            c1 = (f'<h2 class="lab">{lab}</h2>' if lab else '') + (f'<p class="gt">{e(gr["text"])}</p>' if gr.get('text') else '')
            rws = ''.join(fee_row(it, it.get('name')) for it in gr['items'] if it and it.get('name'))
            tail = f'<p class="note">{e(cat["note"])}</p>' if cat.get('note') and gi == len(groups) - 1 else ''
            P.append(f'<section class="ix w"><div class="c1">{c1}</div><div class="c2"><div class="rows">{rws}</div>{tail}</div></section>')
    plans = g('plans')
    pit = [p for p in plans.get('items') or [] if p and p.get('name')]
    if pit:
        c1 = (f'<h2 class="lab">{e(plans.get("title"))}</h2>' if plans.get('title') else '') + (f'<p class="gt">{e(plans["text"])}</p>' if plans.get('text') else '')
        rws = ''.join(fee_row(p, p['name']) for p in pit)
        P.append(f'<section class="ix w" id="plans"><div class="c1">{c1}</div><div class="c2"><div class="rows">{rws}</div>'
                 + (f'<p class="note">{e(plans["note"])}</p>' if plans.get('note') else '') + '</div></section>')

    # ---- people
    team = g('team')
    tg = [(None, team.get('items') or [])] if team.get('items') else [(x.get('t'), x.get('items') or []) for x in team.get('groups') or []]
    allp = [m for _, it in tg for m in it if m and m.get('name')]
    def contacts(m):
        c = []
        if m.get('phone'): c.append(f'<a href="{e(_tel(m["phone"]))}">{e(m["phone"])}</a>')
        if m.get('email'): c.append(f'<a href="mailto:{e(m["email"])}">{e(m["email"])}</a>')
        return c
    byimg = {p['src']: p for p in ((d.get('media') or {}).get('photos') or []) if p.get('src')}
    slide_srcs = {p['src'] for p, _ in slides}
    if allp and len(allp) <= 2:
        if team.get('title') or team.get('text'):
            P.append('<section class="sec" style="padding-bottom:0"><div class="w"><div class="hdg' + ('' if team.get('text') else ' nost') + '">'
                     + (f'<h2 class="lab">{e(team["title"])}</h2>' if team.get('title') else '') + (f'<p class="st">{e(team["text"])}</p>' if team.get('text') else '') + '</div></div></section>')
        for m in allp:
            pic = byimg.get(m.get('img')) if m.get('img') not in slide_srcs else None
            if pic and pic.get('w', 0) < 600: pic = None
            ct = contacts(m)
            ex = ('<p class="acts">' + ''.join(x.replace('<a href', '<a class="pl2" href') for x in ct) + '</p>') if ct else ''
            P.append(about(m.get('role'), m['name'], [m.get('text')], pic, '', ex, small_pic=bool(pic and (pic.get('small') or pic.get('h', 0) < 900)), sid='people', href=m.get('h')))
    elif allp:
        bdp = slot['people']
        body = ''
        for gt, items in tg:
            items = [m for m in items if m and m.get('name')]
            if not items: continue
            if gt: body += f'<h3 class="lab gl">{e(gt)}</h3>'
            withp = [m for m in items if m.get('img') and byimg.get(m['img'], {}).get('w', 0) >= 362]
            rest = [m for m in items if m not in withp]
            if withp:
                body += '<div class="tiles t4">'
                for m in withp:
                    ct = ''.join(contacts(m))
                    nm = f'<a href="{e(m["h"])}">{e(m["name"])}</a>' if m.get('h') else e(m['name'])
                    body += (f'<div class="pt"><div class="tile pp">{_img(byimg[m["img"]], "ph")}<div class="tx"><h3>{nm}</h3>' + (f'<p class="ro">{e(m["role"])}</p>' if m.get('role') else '')
                             + '</div></div>' + (f'<p class="ct">{ct}</p>' if ct else '') + '</div>')
                body += '</div>'
            if rest:
                body += '<ul class="pl">'
                for m in rest:
                    ct = ' · '.join(contacts(m))
                    nm = f'<a href="{e(m["h"])}">{e(m["name"])}</a>' if m.get('h') else e(m['name'])
                    body += f'<li><h3>{nm}</h3>' + (f'<p>{e(m["role"])}</p>' if m.get('role') else '') + (f'<p class="ct">{ct}</p>' if ct else '') + '</li>'
                body += '</ul>'
        hd = (f'<h2 class="lab">{e(team.get("title"))}</h2>' if team.get('title') else '') + (f'<p class="st">{e(team["text"])}</p>' if team.get('text') else '')
        P.append(f'<section class="sec{" hasbd" if bdp else ""}" id="people">' + (f'<div class="bd">{_img(bdp, "ph")}</div>' if bdp else '')
                 + '<div class="w">' + (f'<div class="hdg{"" if team.get("text") else " nost"}">{hd}</div>' if hd else '') + body + '</div></section>')

    # ---- what clients said, in the rows; the name on the slideshow's caption line
    qs = [q for q in d.get('quotes') or [] if q and q.get('q')]
    if qs:
        rws = ''
        for q in qs:
            by = ', '.join(x for x in [q.get('name'), q.get('role')] if x)
            rws += (f'<figure class="row qt{" long" if len(q["q"]) > 220 else ""}"><div class="m"><blockquote class="rt">{e(q["q"])}</blockquote>'
                    + (f'<figcaption class="by"><i></i><span>{e(by)}</span></figcaption>' if by else '') + '</div></figure>')
        P.append(f'<section class="ix w" id="quotes" style="padding-top:60px"><div class="c1"></div><div class="c2"><div class="rows">{rws}</div></div></section>')

    # ---- questions
    faq = g('faq')
    fq = [q for q in faq.get('items') or [] if q and q.get('q')]
    if fq:
        rws = ''.join(f'<details class="row"><summary class="rt">{e(q["q"])}</summary><p class="ans">{e(q.get("a"))}</p></details>' for q in fq)
        P.append(f'<section class="ix w" id="faq" style="padding-top:60px"><div class="c1">' + (f'<h2 class="lab">{e(faq["title"])}</h2>' if faq.get('title') else '')
                 + f'</div><div class="c2"><div class="rows">{rws}</div></div></section>')

    # ---- contact
    place, con, close = g('place'), g('contact'), g('close')
    locs = [l for l in d.get('locations') or [] if l]
    creds = [c for c in d.get('credentials') or [] if c and c.get('t')]
    addr = _addr(place.get('address'))
    phone = place.get('phone') or con.get('phone') or {}
    email = place.get('email') or con.get('email')
    blk = ''
    hd = (f'<h2 class="lab">{e(close["title"])}</h2>' if close.get('title') else '') + (f'<p class="st">{e(close["text"])}</p>' if close.get('text') else '')
    ca = [x for x in [_a(close.get('cta'), 'lk'), _a(place.get('booking'), 'lk'), _a(con.get('form'), 'lk')] if x]
    seen, ca2 = set(), []
    for x in ca:
        if x not in seen: seen.add(x); ca2.append(x)
    if hero.get('text2'): hd += f'<p class="note">{e(hero["text2"])}</p>'
    if ca2: hd += '<p class="acts copyacts" style="display:flex;flex-wrap:wrap;gap:14px 36px">' + ''.join(ca2) + '</p>'
    if hd: blk += f'<div class="hdg">{hd}</div>'
    if addr and not locs: blk += f'<p class="big">{"<br>".join(e(x) for x in addr)}</p>'
    if phone.get('t'):
        blk += f'<a class="big" href="{e(phone.get("h") or _tel(phone["t"]))}">{e(phone["t"])}' + (f'<small>{e(phone["note"])}</small>' if phone.get('note') else '') + '</a>'
    dt = ''
    if email: dt += f'<p><a class="em" href="mailto:{e(email)}">{e(email)}</a></p>'
    hrs = _hours(place.get('hours'))
    if hrs and not locs: dt += '<p>' + '<br>'.join(e(x) for x in hrs) + '</p>'
    for r in con.get('routes') or []:
        if not r or not r.get('t'): continue
        dt += '<p>' + _a(r) + (f'<br>{e(r["note"])}' if r.get('note') else '') + '</p>'
    soc = [s for s in place.get('social') or [] if s and s.get('t')]
    if soc: dt += '<p>' + '<br>'.join(_a(s) for s in soc) + '</p>'
    if dt: blk += f'<div class="dt">{dt}</div>'
    if locs:
        o = ''
        for l in locs:
            o += '<div class="off">' + (f'<h3>{_a({"t": l.get("name"), "h": l.get("h")})}</h3>' if l.get('name') else '')
            a = _addr(l.get('address'))
            if a: o += '<p>' + '<br>'.join(e(x) for x in a) + '</p>'
            c = contacts(l)
            if c: o += '<p>' + '<br>'.join(c) + '</p>'
            h = _hours(l.get('hours'))
            if h: o += '<p>' + '<br>'.join(e(x) for x in h) + '</p>'
            if l.get('note'): o += f'<p>{e(l["note"])}</p>'
            o += '</div>'
        blk += f'<div class="offs">{o}</div>'
    if creds:
        c = ''
        for x in creds:
            t = _a({'t': x['t'], 'h': x.get('h')})
            pic = byimg.get(x.get('img')) or ({'src': x['img'], 'w': 0, 'h': 0, 'alt': ''} if x.get('img') else None)
            im = ''
            if pic:
                wh = f' width="{int(pic["w"])}" height="{int(pic["h"])}"' if pic.get('w') else ''
                im = f'<img src="{e(PRE + pic["src"])}"{wh} alt="{e(pic.get("alt") or x["t"])}" loading="lazy" decoding="async">'
            yr = f' · {e(x["year"])}' if x.get('year') and str(x['year']) not in x['t'] else ''
            c += f'<li><div><h3>{t}{yr}</h3>' + (f'<p>{e(x["text"])}</p>' if x.get('text') else '') + f'</div>{im}</li>'
        blk += f'<div class="cr"><ul>{c}</ul></div>'
    if blk:
        bdp = slot['contact']
        P.append('<section class="ct-sec" id="contact">' + (f'<div class="bd full">{_img(bdp, "ph")}</div>' if bdp else '') + f'<div class="w">{blk}</div></section>')
    P.append('</main>')

    # ---- foot
    foot = g('foot')
    r = ''
    if foot.get('text') and not (addr or locs): r += f'<p>{e(foot["text"])}</p>'
    fl = [l for l in foot.get('links') or [] if l and l.get('t')]
    if fl: r += '<p class="fl">' + ''.join(_a(l) for l in fl) + '</p>'
    if foot.get('legal'): r += f'<p>{e(foot["legal"])}</p>'
    P.append(f'<footer class="ft"><div class="ft-in"><a class="brand" href="{e(home)}">{e(name)}</a>' + (f'<div class="r">{r}</div>' if r else '') + '</div></footer>')

    root = (':root{' + f'--g:{_css(G)};--t:{_css(T)};--l:{_css(L)};--k:{_css(K)};--a:{_css(A)};'
            + f'--tr:{" ".join(str(round(v)) for v in T)};--kr:{" ".join(str(round(v)) for v in K)};--bo:{bo:.2f};'
            + f'--bs:{bs}px;--bt:{".42em" if n <= 26 else ".3em"};--bsm:{bsm}px;--btm:{".36em" if n <= 17 else ".22em"};'
            + "--serif:'Tenor Sans','Optima','Candara',sans-serif;--sans:'DM Sans',system-ui,sans-serif}")
    desc = hero.get('text') or stm.get('text') or ''
    return ('<!doctype html><html lang="' + e(d.get('lang') or 'en') + '"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            + f'<title>{e(name)}{" — " + e(hero["title"]) if hero.get("title") else ""}</title>' + (f'<meta name="description" content="{e(desc[:160])}">' if desc else '')
            + '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            + '<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400&family=Tenor+Sans&display=swap" rel="stylesheet">'
            + f'<style>{root}{CSS}</style></head><body class="{"mono" if MONO else ""}">' + ''.join(P) + f'<script>{JS}</script></body></html>')
