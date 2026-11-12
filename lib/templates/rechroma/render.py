"""rechroma/render.py — one pure function: render(d) -> a complete page.

The build (section order, grid, measures, type, spacing, radii, motion, phone layout) was measured on the reference's
home page at 1440×900 and 390×844 on 2026-11-12 (see NOTES.md and probe/). Nothing of the reference's code, words,
pictures, icons or logo is here. The client's data fills it; a section whose data is missing is left out whole.
No model call, no file reads, no client logic.
"""
import html
import json

FONTS = ('https://fonts.googleapis.com/css2?family=Geist+Pixel&family=Geist+Mono:wght@400;500'
         '&family=Geist:wght@400;500&display=swap')


# ───────────────────────── colour: the reference's relations (ground / raised face / ink ring / inverse / lamp)
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


def _theme(p):
    """Reference: ground L.8, raised face L.9, ink L.3, small text L.4, ring L.1 (darker than the ink), inverse button
    L.4 with L.95 text, pressed L.5 with white text, lamp and hover tint in the one accent. The same relations are
    built from the client's ground, ink and accent; on a dark ground the ring is drawn in the ink's direction."""
    bg, ink, acc = p.get('ground') or '#c4c4c4', p.get('ink') or '#333333', p.get('accent') or p.get('ink') or '#333333'
    light = _lum(bg) >= .45
    if light:
        face = _mix('#ffffff', bg, .5)
        ring = _mix('#000000', ink, .5)
        glint, hik = '255,255,255', 1.0
        inv, invtx = _mix(ink, bg, .82), _mix('#ffffff', bg, .75)
        press, presstx = _mix(ink, bg, .62), '#ffffff'
        plate = bg
    else:
        face = _mix(ink, bg, .13)
        ring = _mix(ink, bg, .62)
        glint, hik = '%d,%d,%d' % _rgb(bg), .14
        inv, invtx = _mix(ink, bg, .88), bg
        press, presstx = _mix(ink, bg, .5), bg
        plate = _mix(ink, bg, .035)
    t = .8
    while min(_con(_mix(ink, bg, t), bg), _con(_mix(ink, bg, t), face)) < 4.6 and t < 1:
        t += .02
    mute = _mix(ink, bg, min(t, 1))
    k = .34
    while k > 0 and _con(mute, _mix(acc, face, k)) < 4.6:
        k -= .04
    hov = _mix(acc, face, max(k, 0))
    k = .3
    while k > 0 and _con(invtx, _mix(acc, inv, k)) < 4.6:
        k -= .04
    invhov = _mix(acc, inv, max(k, 0))
    extra = [x for x in (p.get('extra') or []) if x]
    acc2 = next((c for c in extra[:1] + [acc] if _con(c, plate) >= 3 and _con(c, ink) > 1.25), ink)
    blocks = []
    for c in [acc] + extra + [_mix(ink, bg, .5), _mix(acc, bg, .5)]:
        if c.lower() not in [b.lower() for b in blocks] and _con(c, bg) > 1.15:
            blocks.append(c)

    def hi(a):
        return 'rgba(255,255,255,%.3f)' % (a * hik)

    def lo(a):
        return 'rgba(0,0,0,%.3f)' % a
    v = {'bg': bg, 'ink': ink, 'mute': mute, 'face': face, 'ring': ring, 'plate': plate, 'inv': inv, 'invtx': invtx,
         'invhov': invhov, 'press': press, 'presstx': presstx, 'hov': hov, 'acc': acc, 'acc2': acc2,
         'ledoff': _mix(ink, bg, .5), 'glow': _mix(acc, '#ffffff', .4) if light else _mix(acc, bg, .7),
         'hovhi': _mix(acc, '#ffffff', .45) if light else _mix(acc, face, .5),
         'sh-up': '-3px -3px 10px %s,8px 8px 16px %s,inset 1px 1px 2px %s' % (hi(.4), lo(.3), hi(.7)),
         'sh-inv': '-3px -3px 10px %s,8px 8px 16px %s,inset 1px 1px 2px %s' % (hi(.2), lo(.3), hi(.7)),
         'sh-down': '-1px -1px 5px %s,2px 2px 4px %s,inset 2px 2px 8px %s' % (hi(.1), lo(.3), lo(.35)),
         'sh-plate': '-2px -2px 8px %s,2px 2px 4px %s,inset 1px 1px 3px %s' % (hi(.3), lo(.25), hi(1)),
         'sh-ring': 'inset 1px 1px 3px rgba(%s,.9),inset -1px -1px 3px rgba(%s,.9)' % (glint, glint),
         'sh-nav': '-3px -3px 16px %s,5px 5px 8px %s,-2px 1px 4px %s,2px 1px 4px %s,inset 1px 1px 3px %s' % (
             hi(.4), lo(.4), lo(.25), lo(.25), hi(1)),
         'sh-led': 'inset -2px -2px 4px %s,inset 2px 2px 2px %s' % (hi(.5), lo(.4))}
    return ';'.join('--%s:%s' % kv for kv in v.items()), blocks, ring


# ───────────────────────── the name in blocks: a plain 5-row block alphabet (not the reference's own letterforms)
_G = {
    'A': '.##. #..# #### #..# #..#', 'B': '###. #..# ###. #..# ###.', 'C': '.### #... #... #... .###',
    'D': '###. #..# #..# #..# ###.', 'E': '#### #... ###. #... ####', 'F': '#### #... ###. #... #...',
    'G': '.### #... #.## #..# .###', 'H': '#..# #..# #### #..# #..#', 'I': '### .#. .#. .#. ###',
    'J': '..## ...# ...# #..# .##.', 'K': '#..# #.#. ##.. #.#. #..#', 'L': '#... #... #... #... ####',
    'M': '#...# ##.## #.#.# #...# #...#', 'N': '#..# ##.# #.## #..# #..#', 'O': '.##. #..# #..# #..# .##.',
    'P': '###. #..# ###. #... #...', 'Q': '.##. #..# #..# #.#. .#.#', 'R': '###. #..# ###. #.#. #..#',
    'S': '.### #... .##. ...# ###.', 'T': '### .#. .#. .#. .#.', 'U': '#..# #..# #..# #..# .##.',
    'V': '#...# #...# .#.#. .#.#. ..#..', 'W': '#...# #...# #.#.# ##.## #...#', 'X': '#..# #..# .##. #..# #..#',
    'Y': '#.# #.# .#. .#. .#.', 'Z': '#### ...# .##. #... ####',
    '0': '### #.# #.# #.# ###', '1': '.# ## .# .# .#', '2': '### ..# ### #.. ###', '3': '### ..# ### ..# ###',
    '4': '#.# #.# ### ..# ..#', '5': '### #.. ### ..# ###', '6': '### #.. ### #.# ###', '7': '### ..# ..# ..# ..#',
    '8': '### #.# ### #.# ###', '9': '### #.# ### ..# ###',
    '.': '. . . . #', '-': '.. .. ## .. ..', '+': '... .#. ### .#. ...', ':': '. # . # .', '!': '# # # . #',
    "'": '# # . . .', '’': '# # . . .', '/': '..# ..# .#. #.. #..', '&': '.#.. #.#. .#.# #.#. .#.#',
}


def _blocks(name):
    cells, x = [], 0
    for ch in (name or '').upper():
        if ch == ' ':
            x += 2
            continue
        g = _G.get(ch)
        if not g:
            continue
        rows = g.split(' ')
        for r, row in enumerate(rows):
            for c, v in enumerate(row):
                if v == '#':
                    cells.append((x + c, r))
        x += len(rows[0]) + 1
    return cells, max(x - 1, 0)


# ───────────────────────── small drawn marks (own; squares on a grid, as the reference builds its arrow from squares)
def _sq(cells, s, g, cls=''):
    return ''.join('<rect x="%s" y="%s" width="%s" height="%s"%s/>' % (c * g, r * g, s, s, (' style="--i:%d"' % i) if cls else '')
                   for i, (c, r) in enumerate(cells))


ARROW_R = '<svg class="ia" viewBox="0 0 18 15" width="18" height="15" aria-hidden="true">%s</svg>' % _sq(
    [(0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (4, 1), (4, 3), (3, 0), (3, 4)], 3, 3)
ARROW_D = [(3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (2, 6), (4, 6), (1, 5), (5, 5), (0, 4), (6, 4)]
CHECK = ('<svg class="ck" viewBox="0 0 18 18" width="18" height="18" aria-hidden="true"><circle cx="9" cy="9" r="7.4" fill="none" '
         'stroke="currentColor" stroke-width="1.4"/><path d="M5.7 9.4l2.2 2.2 4.4-4.8" fill="none" stroke="currentColor" '
         'stroke-width="1.4" stroke-linecap="square"/></svg>')
BURGER = ('<svg viewBox="0 0 18 18" width="18" height="18" aria-hidden="true"><path d="M3 5h12M3 9h12M3 13h12" stroke="currentColor" '
          'stroke-width="1.5" fill="none"/></svg>')

CSS = r"""
*{box-sizing:border-box}
html{background:var(--bg);-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:400 16px/1.3 Geist,system-ui,-apple-system,sans-serif;-webkit-font-smoothing:antialiased;overflow-x:hidden}
img,video,svg,canvas{display:block}
a{color:inherit}
h1,h2,h3,p,ul{margin:0;padding:0}
.px{font-family:'Geist Pixel','Geist Mono',ui-monospace,Menlo,monospace;font-weight:400;font-synthesis:none}
.mono{font-family:'Geist Mono',ui-monospace,Menlo,monospace}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);clip-path:inset(50%);white-space:nowrap}
:focus-visible{outline:2px solid var(--ink);outline-offset:3px;border-radius:4px}

/* button: 1px ring, raised face inside (36 high, r7, mono 14/500 +1.25, upper) */
.btn{position:relative;isolation:isolate;display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:36px;padding:9px 13px;border:0;border-radius:7px;background:var(--ring);color:var(--mute);font:500 14px/1.15 'Geist Mono',ui-monospace,Menlo,monospace;letter-spacing:1.25px;text-transform:uppercase;text-decoration:none;cursor:pointer;transition:color .15s ease;-webkit-tap-highlight-color:transparent}
.btn::before{content:"";position:absolute;inset:1px;z-index:-1;border-radius:6px;background:var(--face);box-shadow:var(--sh-up);transition:background-color .15s ease,box-shadow .15s ease}
.btn:hover::before{background:var(--hov);box-shadow:-3px -3px 10px transparent,8px 8px 16px rgba(0,0,0,.3),inset 3px 3px 2px var(--hovhi)}
.btn:active{color:var(--presstx)}
.btn:active::before{background:var(--press);box-shadow:var(--sh-down)}
.btn.inv{color:var(--invtx)}
.btn.inv::before{background:var(--inv);box-shadow:var(--sh-inv)}
.btn.inv:hover::before{background:var(--invhov)}
.btn.inv:active{color:var(--presstx)}
.btn.inv:active::before{background:var(--press);box-shadow:var(--sh-down)}
.btn .ia{fill:currentColor;flex:none}
.btn.wide{display:flex;flex-direction:column;align-items:flex-start;justify-content:space-between;width:100%;min-height:88px}
.btn.wide .ia{align-self:flex-end}

/* plate: 4px ring, face inset 4, r16/r12, pad 28 */
.plate{position:relative;isolation:isolate;padding:28px;border-radius:16px;background:var(--ring);box-shadow:var(--sh-ring)}
.plate::before{content:"";position:absolute;inset:4px;z-index:-1;border-radius:12px;background:var(--plate);box-shadow:var(--sh-plate)}

/* nav: two floating plates 72 high, 8 from the edges */
.nv{position:fixed;z-index:60;top:8px;left:8px;right:8px;display:flex;justify-content:space-between;align-items:flex-start;gap:4px;pointer-events:none}
.js .nv{opacity:0;transform:translateY(-88px);transition:opacity .18s ease-out,transform .72s cubic-bezier(.34,1.56,.64,1)}
.js .nv.on,.js .nv:focus-within{opacity:1;transform:none}
.nv-l,.nv-r{position:relative;display:flex;align-items:center;height:72px;border-radius:12px;background:var(--plate);pointer-events:auto}
.nv-l::after,.nv-r::after{content:"";position:absolute;inset:0;border-radius:12px;box-shadow:var(--sh-nav);pointer-events:none}
.nv-l{padding:0 24px;gap:10px;text-decoration:none;color:var(--ink);font-size:20px;line-height:1;min-width:120px;justify-content:center}
.nv-l img{height:24px;width:auto}
.nv-l img.wmk{height:18px;max-width:200px}
.nv-r{padding:0 24px;gap:16px}
.tg{display:grid;grid-auto-flow:column;grid-auto-columns:1fr;gap:1px;padding:1px;border-radius:7px;background:var(--ring)}
.tg a{display:flex;align-items:center;justify-content:space-between;gap:10px;min-height:34px;padding:8px 12px;border-radius:6px;background:var(--face);box-shadow:var(--sh-up);color:var(--mute);font:500 14px/1.15 'Geist Mono',ui-monospace,Menlo,monospace;letter-spacing:1.25px;text-transform:uppercase;text-decoration:none;white-space:nowrap;transition:background-color .15s ease,color .15s ease,box-shadow .15s ease}
.tg a:hover{background:var(--hov)}
.tg a:active{background:var(--press);color:var(--presstx);box-shadow:var(--sh-down)}
.tg a:focus-visible{position:relative;z-index:1}
.led{flex:none;width:12px;height:12px;border-radius:50%;border:1px solid var(--mute);background:var(--ledoff);box-shadow:var(--sh-led);transition:background-color .15s ease,box-shadow .15s ease}
a:hover>.led,a:focus-visible>.led,a:active>.led{background:var(--acc);box-shadow:0 0 6px var(--glow),var(--sh-led)}
.mn{display:none;position:relative}
.mn summary{list-style:none;width:44px;padding:9px 0}
.mn summary::-webkit-details-marker{display:none}
.mn-p{position:absolute;top:44px;right:0;display:flex;flex-direction:column;gap:4px;min-width:159px;padding:4px;border-radius:8px;background:var(--face);box-shadow:var(--sh-up)}
.mn-p a{display:block;padding:8px 12px;border-radius:8px;color:var(--mute);font:500 14px/1.15 'Geist Mono',ui-monospace,Menlo,monospace;letter-spacing:1.25px;text-transform:uppercase;text-decoration:none;white-space:nowrap;transition:background-color .15s ease,color .15s ease}
.mn-p a:hover{background:var(--hov)}
.mn-p a:active{background:var(--press);color:var(--presstx)}
.mn-p hr{width:100%;height:4px;margin:4px 0;border:0;border-radius:99px;box-shadow:var(--sh-led)}

/* opening: stage pinned for .8 of a screen; name in blocks, h1 right-aligned from the middle of the screen */
.hero{position:relative;height:140vh;height:calc(100svh + 40vh)}
.stage{position:sticky;top:0;height:100vh;height:100svh;overflow:hidden;background:var(--bg)}
.bd{position:absolute;inset:0;background:#050505;opacity:0;pointer-events:none;transition:opacity 1.6s cubic-bezier(.45,0,.55,1)}
.js.intro .bd{opacity:1;transition:none}
.stage canvas{position:absolute;inset:0;width:100%;height:100%;display:none}
.js.cv .stage canvas{display:block}
.wm{position:absolute;left:50%;bottom:calc(50% + 72px);transform:translateX(-50%);width:min(calc(80vw - 80px),var(--wmw));height:auto;fill:var(--ring)}
.js.cv .wm{visibility:hidden}
.hc{position:absolute;top:50%;left:10%;right:10%;display:flex;flex-direction:column;align-items:flex-end;gap:16px}
.hc h1{max-width:640px;font-size:50px;line-height:60px;text-align:right;color:var(--ink)}
.hl{max-width:544px;font-size:20px;line-height:1.3;text-align:right;color:var(--ink)}
/* typed copy: the sentence stays real text, one span a word; the letters are let through one by one by a mask */
.w{display:inline-block;white-space:nowrap;padding:.14em 0;margin:-.14em 0}
.js:not(.go) .hc h1{opacity:0}
.js .hc .btn,.js .hc .hl{opacity:0;transition:opacity .4s ease .25s,color .15s ease}
.js.go .hc .btn,.js.go .hc .hl{opacity:1}
.ar{position:absolute;left:0;right:0;bottom:90px;display:flex;justify-content:center;pointer-events:none}
.ar svg{fill:var(--mute)}
.js:not(.go) .ar{opacity:0}
.js.go .ar rect{animation:sq 4.3s linear infinite backwards;animation-delay:calc(var(--i)*65ms)}
@keyframes sq{0%{opacity:0}1.5%{opacity:1}97%{opacity:1}100%{opacity:0}}

/* story — stacked build (phone, no scripts, reduced motion) */
.story{padding:104px 16px 64px}
.list{display:grid;gap:70px}
.pn{display:grid;gap:48px;align-items:center}
.cp{display:grid;gap:10px;align-content:center}
.cp .ld,.cp h2{font-size:39px;line-height:.98;color:var(--ink)}
.cp .tx{font-size:26.5px;line-height:1.04;color:var(--ink)}
.dm .plate{display:flex;align-items:center;justify-content:center;padding:20px}
.dm img,.dm video{width:auto;height:auto;max-width:100%;max-height:70vh;border-radius:6px}

/* pricing */
.pr{padding:80px 16px 0}
.pr-h{display:flex;flex-direction:column;gap:16px;min-height:96px;justify-content:center;margin-bottom:16px}
.pr-h h2,.cl h2,.fq h2{font-size:32px;line-height:1.3;color:var(--ink)}
.pr-h p,.cl-c p{font-size:20px;line-height:1.3;color:var(--ink);max-width:573px}
.plans{display:grid;gap:24px}
.plans .plate{display:flex;padding:20px}
.plan{display:flex;flex-direction:column;gap:24px;width:100%}
.plan header{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:flex-start;gap:12px 24px}.plan header .price{margin-left:auto}
.plan h3{font-size:32px;line-height:1.3;color:var(--ink)}
.plan.mk h3{color:var(--acc2)}
.price{display:flex;flex-direction:column;align-items:flex-end;text-align:right}
.price b{font-weight:400;font-size:50px;line-height:1;color:var(--ink);white-space:nowrap}
.price span,.lbl{margin-top:5.6px;font:400 14px/1.3 'Geist Mono',ui-monospace,Menlo,monospace;letter-spacing:.75px;text-transform:uppercase;color:var(--mute)}
.plan ul{display:flex;flex-direction:column;gap:12.8px;list-style:none}
.plan li{display:flex;align-items:flex-start;gap:10.4px;font:400 16px/1.3 'Geist Mono',ui-monospace,Menlo,monospace;color:var(--ink)}
.ck{flex:none;margin-top:1.3px}
.nt{font:400 12.24px/1.3 'Geist Mono',ui-monospace,Menlo,monospace;color:var(--mute)}
.plan .act{margin-top:auto}
.pr>.in>.nt{margin-top:24px;max-width:684px}
.js .rv{opacity:0;transition:opacity .6s ease}
.js .rv.in,.js .rv:focus-within{opacity:1}

/* figures: one plate, each figure the reference's price pairing (50px number, mono label under it) */
.fg{padding:80px 16px 0}
.fgs{display:grid;gap:28px;list-style:none;padding:8px}
.fgs li{display:flex;flex-direction:column;min-width:0}
.fgs b{font-weight:400;font-size:40px;line-height:1;color:var(--ink);white-space:nowrap}

/* features: head as the pricing head, one plate of checked rows (the plan rows, with a name over each) */
.fe{padding:80px 16px 0}
.fts{display:grid;gap:28px;list-style:none;padding:8px}
.fts li{display:flex;align-items:flex-start;gap:10.4px;min-width:0}
.fts .ck{margin-top:4px;color:var(--ink)}
.fts h3{font-size:20px;line-height:1.3;color:var(--ink)}
.fts p{margin-top:6px;font:400 16px/1.3 'Geist Mono',ui-monospace,Menlo,monospace;color:var(--ink)}

/* questions: head left, one plate right; a row is a toggle with the reference's lamp, lit while open */
.fq{padding:80px 16px 0}
.fq-g{display:grid;gap:16px}
.qs{padding:0 8px}
.qs hr{height:1px;margin:0;border:0;background:var(--mute);opacity:.45}
.qs summary{display:flex;align-items:center;justify-content:space-between;gap:24px;padding:16px 0;list-style:none;cursor:pointer;font-size:20px;line-height:1.3;color:var(--ink)}
.qs summary::-webkit-details-marker{display:none}
.qs details[open] .led,.qs summary:hover .led{background:var(--acc);box-shadow:0 0 6px var(--glow),var(--sh-led)}
.qs details p{padding:0 36px 20px 0;max-width:68ch;font:400 16px/1.3 'Geist Mono',ui-monospace,Menlo,monospace;color:var(--ink)}

/* close */
.cl{padding:80px 16px 64px;display:flex;align-items:center}
.cl-g{display:grid;gap:32px;width:100%}
.cl-c{display:flex;flex-direction:column;gap:16px}
.cl .plate{padding:20px}
.cl .plate>div{padding:16px}

/* foot */
.ft{padding:0 16px 12px}
.ft-g{display:grid;grid-template-columns:1fr auto;gap:24px 16px;padding:16px;align-items:center}
.ft-m{grid-row:2;display:flex;align-items:center;gap:10px;font-size:20px;line-height:1;color:var(--ink);text-decoration:none}
.ft-m img{height:32px;width:auto;max-width:200px}
.ft-m img.wmk{height:18px}
.ft-l{grid-column:2;display:flex;flex-wrap:wrap;justify-content:flex-end;gap:16px}
.ft-l a,.ft-c{font:400 14px/1.3 'Geist Mono',ui-monospace,Menlo,monospace;letter-spacing:.75px;text-transform:uppercase;color:var(--ink);text-decoration:none}
.ft-l a:hover{text-decoration:underline}
.ft-c{grid-column:2;grid-row:2;text-align:right}
.ft .nt{padding:0 16px 16px;max-width:760px}

@media (max-width:899px){
  .nv-l{padding:0 16px;min-width:0}
  .nv-l img{height:20px}
  .nv-l img.wmk{height:14px;max-width:152px}
  .nv-r{padding:0 12px}
  .nv-r>.tg,.nv-r>.btn{display:none}
  .mn{display:block}
  .wm{width:80vw;bottom:calc(65% + 64px)}
  .hc{top:35%}
  .hc h1{font-size:37px;line-height:1.15}
  .ar{bottom:116px}
}
@media (min-width:900px){
  .story{padding:96px 24px}
  .list{gap:120px}
  .pn{grid-template-columns:573fr 776fr;gap:43px}
  .cp{gap:16px}
  .cp .ld,.cp h2{font-size:50px;line-height:60px}
  .cp .tx{font-size:34px;line-height:44.2px}
  .cp h2+.tx{max-width:544px}
  .dm .plate{padding:28px}
  .dm img,.dm video{max-height:min(634px,calc(100vh - 178px))}
  .pin .story{padding:0}
  .pin .pinbox{position:sticky;top:0;height:100vh;padding:96px 24px 24px;overflow:hidden}
  .pin .list{position:relative;display:block;height:100%}
  .pin .pn{position:absolute;inset:0}
  .pin .cp.two>*{grid-area:1/1;align-self:center}
  .pin .dm{will-change:transform,opacity}
  .pin .dm .pic{will-change:transform,opacity}
  .hl{font-size:24px}
  .pr{padding:96px 24px 24px}
  .fg{padding:96px 24px 24px}
  .fgs{grid-template-columns:repeat(var(--n),minmax(0,1fr));gap:43px;padding:14.4px}
  .fgs b{font-size:50px}
  .fe{padding:96px 24px 24px}
  .fts{grid-template-columns:repeat(var(--n),minmax(0,1fr));gap:32.4px 43px;padding:14.4px}
  .fts h3{font-size:24px}
  .fq{padding:96px 24px 24px}
  .fq-g{grid-template-columns:573fr 776fr;gap:43px;align-items:start}
  .fq-g.solo{grid-template-columns:minmax(0,776px)}
  .qs{padding:0 14.4px}
  .qs summary{font-size:24px;padding:20px 0}
  .pr>.in{width:100%}
  .pr-h{margin-bottom:24px}
  .pr-h h2,.cl h2,.fq h2,.plan h3{font-size:40px}
  .pr-h p,.cl-c p{font-size:24px}
  .plans{grid-template-columns:repeat(auto-fit,minmax(320px,1fr))}
  .plans.one{grid-template-columns:minmax(0,684px)}
  .plans .plate{padding:28px}
  .plan{padding:14.4px;gap:32.4px}
  .cl{padding:96px 24px 72px}
  .cl-g{grid-template-columns:573fr 776fr;gap:43px;align-items:center}
  .cl .plate{padding:28px}
  .cl .plate>div{padding:32px}
  .ft{padding:0 24px 24px}
  .ft-g{grid-template-columns:1fr auto 1fr;padding:24px}
  .ft-m{grid-row:auto}
  .ft-l{grid-column:auto;justify-content:center}
  .ft-c{grid-column:auto;grid-row:auto}
  .ft .nt{padding:0 24px 24px}
}
@media (prefers-reduced-motion:reduce){
  *,*::before,*::after{transition:none!important;animation:none!important}
  .w{-webkit-mask-image:none!important;mask-image:none!important}
}
"""

JS = r"""
(function(){
var D=document,H=D.documentElement,W=window,reduce=W.matchMedia('(prefers-reduced-motion: reduce)').matches;
var $=function(s,r){return (r||D).querySelector(s)},$$=function(s,r){return [].slice.call((r||D).querySelectorAll(s))};
var cl=function(v,a,b){return v<a?a:v>b?b:v},vh=function(){return W.innerHeight};
var PAL=__PAL__;

/* nav: in once the page has moved 150px (measured: out at 100, in at 200) */
var nv=$('.nv');function nav(){if(nv)nv.classList.toggle('on',W.scrollY>150)}
var mn=$('.mn');if(mn){D.addEventListener('click',function(e){if(mn.open&&!mn.contains(e.target))mn.open=false});D.addEventListener('keydown',function(e){if(e.key==='Escape'&&mn.open){mn.open=false;$('summary',mn).focus()}})}

/* typed copy. The sentence stays real text in the page's ink — one span a word, so a reader, a search and the
   readability gate all get whole words — and the letters are let through one after another by a mask on the word
   (one hard-edged stop per letter, at the letter's measured edges). Nothing is hidden by colour or by opacity. */
function split(el){var t=el.textContent,ws=[],n=0;el.textContent='';t.split(/(\s+)/).forEach(function(w){if(!w)return;if(/^\s+$/.test(w)){el.appendChild(D.createTextNode(' '));return}var s=D.createElement('span');s.className='w';s.textContent=w;el.appendChild(s);ws.push({el:s,i:n,n:w.length,x:null,k:'1'});n+=w.length});el._w=ws;el._n=n}
function edges(w){var tn=w.el.firstChild,q=w.el.getBoundingClientRect(),r=D.createRange(),x=[0];for(var i=0;i<w.n;i++){var v=(i+1)/w.n;if(q.width>0){r.setStart(tn,i);r.setEnd(tn,i+1);var c=r.getBoundingClientRect();if(c.width>0)v=(c.right-q.left)/q.width}x.push(cl(v,x[i],1))}x[w.n]=1;w.x=x}
function mask(w,m){w.el.style.webkitMaskImage=m;w.el.style.maskImage=m}
function reveal(el,a,b,t,win){var ws=el._w;if(!ws)return;var N=el._n,d=Math.min(win||70,b-a),sp=b-a-d;
  for(var j=0;j<ws.length;j++){var w=ws[j],o=[],all=1,none=1,i;for(i=0;i<w.n;i++){var v=Math.round(cl((t-a-(N>1?sp*(w.i+i)/(N-1):0))/d,0,1)*20)/20;o.push(v);if(v<1)all=0;if(v>0)none=0}
    var k=all?'1':none?'0':o.join();if(k===w.k)continue;w.k=k;
    if(all)mask(w,'none');else if(none)mask(w,'linear-gradient(transparent,transparent)');else{if(!w.x)edges(w);var p=[];for(i=0;i<w.n;i++)p.push('rgba(0,0,0,'+o[i]+') '+(w.x[i]*100).toFixed(1)+'% '+(w.x[i+1]*100).toFixed(1)+'%');mask(w,'linear-gradient(90deg,'+p.join()+')')}}}
function whole(el){(el._w||[]).forEach(function(w){w.x=null;if(w.k!=='1'){w.k='1';mask(w,'none')}})}

/* opening */
var stage=$('.stage'),cv=$('.stage canvas'),wm=$('.wm'),hc=$('.hc'),h1=$('.hc h1'),cells=wm?$$('rect',wm).map(function(r,i){return {x:+r.getAttribute('x'),y:+r.getAttribute('y'),a:(i*0.618034)%1,b:(i*0.381966+.31)%1,c:PAL[(i*7+3)%PAL.length]}}):[];
var t0=performance.now(),introLen=reduce?0:1000,ctx=cv&&cv.getContext?cv.getContext('2d'):null,ring=[0,0,0];
function rgb(h){h=h.replace('#','');return [parseInt(h.substr(0,2),16),parseInt(h.substr(2,2),16),parseInt(h.substr(4,2),16)]}
if(ctx&&cells.length){H.classList.add('cv');ring=rgb(getComputedStyle(H).getPropertyValue('--ring').trim()||'#000000')}
function drawBlocks(){if(!ctx||!cells.length)return;var r=stage.getBoundingClientRect(),q=wm.getBoundingClientRect(),dpr=Math.min(W.devicePixelRatio||1,2),w=Math.round(r.width*dpr),h=Math.round(r.height*dpr);
  if(cv.width!==w||cv.height!==h){cv.width=w;cv.height=h}ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,r.width,r.height);
  var cols=+wm.getAttribute('data-cols'),s=q.width/cols,ox=q.left-r.left,oy=q.top-r.top,tau=performance.now()-t0,y=cl(W.scrollY,0,1e6),V=vh();
  var fade=1-cl((y-.16*V)/(.22*V),0,1);if(fade<=0)return;
  for(var i=0;i<cells.length;i++){var c=cells[i],X=ox+c.x*s,Y=oy+c.y*s,fill=introLen?cl((tau-300-c.b*500)/200,0,1):1,line=introLen?cl((tau-c.a*600)/60,0,1):1;if(!line)continue;
    var m=cl((y/(.12*V))*1.6-c.a*.6,0,1),k=rgb(c.c),col='rgba('+Math.round(ring[0]+(k[0]-ring[0])*m)+','+Math.round(ring[1]+(k[1]-ring[1])*m)+','+Math.round(ring[2]+(k[2]-ring[2])*m)+','+(fill*fade)+')';
    ctx.fillStyle=col;ctx.fillRect(X,Y,s+.5,s+.5);ctx.strokeStyle='rgba(255,255,255,'+((fill<1?.34:.1)*fade)+')';ctx.lineWidth=1;ctx.strokeRect(X+.5,Y+.5,s-1,s-1)}}
function hero(){if(!stage)return;var y=W.scrollY,V=vh();if(hc)hc.style.opacity=String(cl(1-y/(.4*V),0,1));drawBlocks()}
var ar=$('.ar');function room(){if(ar&&hc)ar.style.visibility=hc.getBoundingClientRect().bottom>ar.getBoundingClientRect().top-12?'hidden':''}
if(h1&&!reduce){split(h1);reveal(h1,0,1,-1)}
function type1(){var g0=performance.now(),len=(h1._n-1)*20+340;(function f(){var t=performance.now()-g0;reveal(h1,0,len,t,340);if(t<len)requestAnimationFrame(f);else whole(h1)})()}
if(reduce){H.classList.remove('intro');H.classList.add('go')}
else{(function loop(){drawBlocks();if(performance.now()-t0<introLen+300)requestAnimationFrame(loop)})();
  setTimeout(function(){H.classList.remove('intro')},900);setTimeout(function(){H.classList.add('go');if(h1)type1()},2300)}

/* story */
var story=$('.story'),panels=$$('.pn'),sched=[],total=0,pinned=false;
panels.forEach(function(pn){pn._dm=$('.dm',pn);pn._pic=$('.pic',pn);pn._els=$$('.cp>*',pn);if(!reduce)pn._els.forEach(split)});
function set(el,k,v){if(el&&el.style[k]!==v)el.style[k]=v}
function spring(e){return e>=1?0:1.57*Math.exp(-6.5*e)*Math.cos(7*e-.88)*(1-e*e*e)}
/* lengths in px of scroll at a 900 screen. Each hold is the least that shows its content once: a plate lands in 300
   while its head types (180) and its paragraph after it (280–310); the finished panel stands for about 150, then
   leaves in 290. The reference holds 4080 / 3600 / 4300 / 2420 for the same four panels. */
function plan(){sched=[];var S=0,n=panels.length;panels.forEach(function(pn,i){var two=pn._els.length>1&&$('.cp',pn).classList.contains('two'),first=i===0,last=i===n-1,k=first?0:60,L=k+(two?(last?870:1220):(last?450:820));sched.push({S:S,L:L,k:k,two:two,first:first,last:last});S+=L-80});total=n?S+80:0}
function pinOn(){return !reduce&&panels.length&&W.innerWidth>=900&&W.innerHeight>=560}
function layout(){var p=pinOn();if(p!==pinned){pinned=p;H.classList.toggle('pin',p);panels.forEach(function(pn){[pn,pn._dm,pn._pic].concat(pn._els).forEach(function(el){if(el){el.style.opacity='';el.style.transform='';el.style.visibility=''}})})}
  panels.forEach(function(pn){pn._els.forEach(function(el){(el._w||[]).forEach(function(w){w.x=null;if(w.k!=='1'&&w.k!=='0')w.k=''})})});
  if(pinned){plan();story.style.height=(vh()+total*vh()/900)+'px'}else if(story)story.style.height='';room()}
function storyPinned(){var V=vh(),u=(W.scrollY-(story.getBoundingClientRect().top+W.scrollY))*900/V;u=cl(u,-1,total);
  panels.forEach(function(pn,i){var s=sched[i],t=u-s.S,L=s.L,k=s.k,vis=(s.first||t>-10)&&(s.last||t<L+10);set(pn,'visibility',vis?'visible':'hidden');if(!vis)return;
    var dm=pn._dm,pic=pn._pic,y=0,op=1,ph=dm?dm.offsetHeight:0,Din=V/2+ph/2+120,Dout=V/2+ph/2+60;
    if(!s.first&&t<300){var e=cl(t/300,0,1);y=Din*spring(e);op=cl(e/.4,0,1)}
    else if(!s.last&&t>L-310){if(t<L-220)y=46*Math.sin(cl((t-(L-310))/90,0,1)*Math.PI/2);else{var q=cl((t-(L-220))/200,0,1);y=46-(46+Dout)*q*q*q;op=1-Math.pow(q,2.5)}}
    if(dm){set(dm,'transform','translate3d(0,'+y.toFixed(1)+'px,0)');set(dm,'opacity',op.toFixed(2))}
    if(pic){var a=s.first?40:240,g=cl((t-a)/260,0,1),z=1-Math.pow(1-g,3);set(pic,'transform','scale('+(.4+.6*z).toFixed(3)+')');set(pic,'opacity',cl(g*3,0,1).toFixed(2))}
    var els=pn._els,out=s.last?1:1-cl((t-(L-290))/100,0,1);
    if(s.two){var o0=1-cl((t-k-380)/90,0,1);reveal(els[0],k+30,k+210,t);set(els[0],'opacity',o0.toFixed(2));set(els[0],'visibility',o0>0?'':'hidden');
      reveal(els[1],k+480,k+790,t);set(els[1],'opacity',out.toFixed(2));set(els[1],'visibility',t>k+470&&out>0?'':'hidden')}
    else els.forEach(function(el,j){if(els.length>1&&j===0)reveal(el,k+30,k+210,t);else reveal(el,k+(els.length>1?100:30),k+(els.length>1?380:310),t);set(el,'opacity',out.toFixed(2))})})}
function storyStacked(){if(reduce)return;var V=vh();panels.forEach(function(pn){pn._els.forEach(function(el){var r=el.getBoundingClientRect();if(r.bottom<-200||r.top>V+200)return;var q=(V*.86-r.top)/(r.height+V*.3);reveal(el,0,1000,q*1000,200)})})}
function tick(){nav();hero();if(!story)return;if(pinned)storyPinned();else storyStacked()}
var raf=0;function on(){if(!raf)raf=requestAnimationFrame(function(){raf=0;tick()})}
layout();tick();W.addEventListener('scroll',on,{passive:true});W.addEventListener('resize',function(){layout();on()});W.addEventListener('load',function(){layout();on()});
if(D.fonts&&D.fonts.ready)D.fonts.ready.then(function(){layout();on()});

/* plan heads and actions come up when seen */
var rv=$$('.rv');if('IntersectionObserver' in W&&!reduce){var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{rootMargin:'0px 0px -8% 0px'});rv.forEach(function(e){io.observe(e)})}else rv.forEach(function(e){e.classList.add('in')});
})();
"""


def render(d: dict) -> str:
    e = lambda s: html.escape(str(s or ''), quote=True)
    m = lambda p: p if str(p).startswith(('http:', 'https:', 'data:', '/')) else '../../' + str(p)
    b = d.get('brand') or {}
    name = b.get('name') or ''
    theme, pal, _ring = _theme(d.get('palette') or {})
    media = d.get('media') or {}
    sizes = {x.get('src'): x for k in ('screens', 'phones', 'photos') for x in (media.get(k) or []) if isinstance(x, dict)}

    def lnk(x, cls='', inner=None):
        return '<a class="%s" href="%s">%s</a>' % (cls, e(x.get('h') or '#'), inner if inner is not None else e(x.get('t')))

    def logo(cls=''):
        if b.get('logo'):
            wmk = b.get('logo_wordmark')
            im = '<img%s src="%s" alt="%s">' % (' class="wmk"' if wmk else '', e(m(b['logo'])), e(name) if wmk else '')
            return im + ('' if wmk else '<span class="px">%s</span>' % e(name))
        return '<span class="px">%s</span>' % e(name)

    # ── nav
    navs = [x for x in (d.get('nav') or []) if x.get('t')][:5]
    door = d.get('signin') if (d.get('signin') or {}).get('t') else d.get('cta') if (d.get('cta') or {}).get('t') else None
    tg = '<div class="tg">%s</div>' % ''.join(lnk(x, '', '%s<i class="led"></i>' % e(x['t'])) for x in navs) if navs else ''
    menu = ''
    if navs or door:
        menu = '<details class="mn"><summary class="btn" aria-label="%s">%s</summary><div class="mn-p">%s%s%s</div></details>' % (
            e(name), BURGER, ''.join(lnk(x) for x in navs), '<hr>' if navs and door else '', lnk(door) if door else '')
    right = '<div class="nv-r">%s%s%s</div>' % (tg, lnk(door, 'btn inv') if door else '', menu) if (tg or door) else ''
    nav = '<nav class="nv" aria-label="%s"><a class="nv-l" href="%s">%s</a>%s</nav>' % (e(name), e(b.get('home') or '#'), logo(), right)

    # ── opening
    hero = d.get('hero') or {}
    cells, cols = _blocks(name)
    wm = ''
    if cells:
        wm = '<svg class="wm" style="--wmw:%dpx" viewBox="0 0 %d 5" data-cols="%d" role="img" aria-label="%s">%s</svg>' % (
            cols * 33, cols, cols, e(name), ''.join('<rect x="%d" y="%d" width="1.02" height="1.02"/>' % c for c in cells))
    h1 = '<h1 class="px">%s</h1>' % e(hero.get('title') or name)
    pri = hero.get('primary') if (hero.get('primary') or {}).get('t') else d.get('cta') if (d.get('cta') or {}).get('t') else None
    arrow = '<div class="ar" aria-hidden="true"><svg viewBox="0 0 40 46" width="40" height="46">%s</svg></div>' % _sq(ARROW_D, 4, 6, 'i')
    opening = ('<section class="hero"><div class="stage"><div class="bd"></div><canvas aria-hidden="true"></canvas>%s'
               '<div class="hc">%s%s%s</div>%s</div></section>') % (
        wm, h1, '<p class="hl px">%s</p>' % e(hero['text']) if hero.get('text') else '', lnk(pri, 'btn', '<span>%s</span>%s' % (e(pri['t']), ARROW_R)) if pri else '', arrow)

    # ── story: the statement, then each step; a product picture whole inside a plate
    def pic(x):
        if not x:
            return ''
        if x.get('poster') is not None or str(x.get('src', '')).endswith(('.mp4', '.webm')):
            return ('<div class="dm"><div class="plate"><video class="pic" src="%s"%s width="%s" height="%s" autoplay muted loop playsinline '
                    'aria-label="%s"></video></div></div>') % (e(m(x['src'])), ' poster="%s"' % e(m(x['poster'])) if x.get('poster') else '',
                                                              e(x.get('w') or ''), e(x.get('h') or ''), e(x.get('alt')))
        wh = ' width="%s" height="%s"' % (e(x['w']), e(x['h'])) if x.get('w') and x.get('h') else ''
        return '<div class="dm"><div class="plate"><img class="pic" src="%s" alt="%s"%s decoding="async"></div></div>' % (
            e(m(x['src'])), e(x.get('alt')), wh)

    panels = []
    st = d.get('statement') or {}
    if st.get('title') or st.get('text'):
        lead = next((x for x in [media.get('video')] + (media.get('screens') or []) + (media.get('phones') or []) + (media.get('photos') or []) if x and x.get('src')), None)
        two = bool(st.get('title') and st.get('text'))
        cp = ('<p class="ld px">%s</p>' % e(st['title']) if st.get('title') else '') + ('<p class="tx px">%s</p>' % e(st['text']) if st.get('text') else '')
        panels.append('<article class="pn"><div class="cp%s">%s</div>%s</article>' % (' two' if two else '', cp, pic(lead)))
    for it in ((d.get('steps') or {}).get('items') or []):
        if not (it.get('title') or it.get('text')):
            continue
        x = dict(sizes.get(it.get('img')) or {}, src=it['img']) if it.get('img') else None
        if x and not x.get('alt'):
            x['alt'] = it.get('title') or ''
        cp = ('<h2 class="px">%s</h2>' % e(it['title']) if it.get('title') else '') + ('<p class="tx px">%s</p>' % e(it['text']) if it.get('text') else '')
        panels.append('<article class="pn"><div class="cp">%s</div>%s</article>' % (cp, pic(x)))
    story = '<section class="story"><div class="pinbox"><div class="list">%s</div></div></section>' % ''.join(panels) if panels else ''

    # ── figures: one plate; each figure is the reference's price pairing (the number at 50, a mono label under it)
    figs = [x for x in (d.get('figures') or []) if x.get('v')]
    figures = ''
    if figs:
        figures = '<section class="fg"><div class="plate"><ul class="fgs" style="--n:%d">%s</ul></div></section>' % (
            min(len(figs), 4), ''.join('<li><b class="px">%s</b>%s</li>' % (
                e(x['v']), '<span class="lbl">%s</span>' % e(x['l']) if x.get('l') else '') for x in figs))

    # ── features: the pricing head, then one plate of checked rows (the plan rows, each with its name over it)
    fe = d.get('features') or {}
    fits = [x for x in (fe.get('items') or []) if x.get('t')]
    features = ''
    if fits:
        head = ''
        if fe.get('title') or fe.get('text'):
            head = '<div class="pr-h">%s%s</div>' % ('<h2 class="px">%s</h2>' % e(fe['title']) if fe.get('title') else '',
                                                   '<p class="px">%s</p>' % e(fe['text']) if fe.get('text') else '')
        features = '<section class="fe">%s<div class="plate"><ul class="fts" style="--n:%d">%s</ul></div></section>' % (
            head, min(len(fits), 3), ''.join('<li>%s<div><h3 class="px">%s</h3>%s</div></li>' % (
                CHECK, e(x['t']), '<p>%s</p>' % e(x['d']) if x.get('d') else '') for x in fits))

    # ── questions: head left, one plate right; each row a toggle with the lamp, the first one open
    fq = d.get('faq') or {}
    qs = [x for x in (fq.get('items') or []) if x.get('q') and x.get('a')]
    faq = ''
    if qs:
        rows = '<hr>'.join('<details%s><summary><span class="px">%s</span><i class="led"></i></summary><p>%s</p></details>' % (
            ' open' if i == 0 else '', e(x['q']), e(x['a'])) for i, x in enumerate(qs))
        faq = '<section class="fq"><div class="fq-g%s">%s<div class="plate"><div class="qs">%s</div></div></div></section>' % (
            '' if fq.get('title') else ' solo', '<h2 class="px">%s</h2>' % e(fq['title']) if fq.get('title') else '', rows)

    # ── pricing
    pl = d.get('plans') or {}
    items = [p for p in (pl.get('items') or []) if p.get('name')]
    pricing = ''
    if items:
        cards = []
        for p in items:
            price = ''
            if p.get('price'):
                price = '<p class="price rv"><b class="px">%s</b>%s</p>' % (e(p['price']), '<span>%s</span>' % e(p['per']) if p.get('per') else '')
            rows = ''.join('<li>%s<span>%s</span></li>' % (CHECK, e(r)) for r in (p.get('rows') or []) if r)
            c = p.get('cta') or {}
            cards.append('<article class="plate"><div class="plan%s"><header><h3 class="px rv">%s</h3>%s</header>%s%s%s</div></article>' % (
                ' mk' if p.get('marked') else '', e(p['name']), price, '<ul>%s</ul>' % rows if rows else '',
                '<p class="nt">%s</p>' % e(p['line']) if p.get('line') else '',
                '<div class="act rv">%s</div>' % lnk(c, 'btn wide', '<span>%s</span>%s' % (e(c['t']), ARROW_R)) if c.get('t') else ''))
        head = ''
        if pl.get('title') or pl.get('text'):
            head = '<div class="pr-h">%s%s</div>' % ('<h2 class="px">%s</h2>' % e(pl['title']) if pl.get('title') else '',
                                                   '<p class="px">%s</p>' % e(pl['text']) if pl.get('text') else '')
        pricing = '<section class="pr"><div class="in">%s<div class="plans%s">%s</div>%s</div></section>' % (
            head, ' one' if len(cards) == 1 else '', ''.join(cards), '<p class="nt">%s</p>' % e(pl['note']) if pl.get('note') else '')

    # ── close (the reference's last section: head and text left, a plate with the one action right)
    c = d.get('close') or {}
    close = ''
    if c.get('title'):
        cc = c.get('cta') if (c.get('cta') or {}).get('t') else None
        close = '<section class="cl"><div class="cl-g"><div class="cl-c"><h2 class="px">%s</h2>%s</div>%s</div></section>' % (
            e(c['title']), '<p class="px">%s</p>' % e(c['text']) if c.get('text') else '',
            '<div class="plate"><div>%s</div></div>' % lnk(cc, 'btn wide', '<span>%s</span>%s' % (e(cc['t']), ARROW_R)) if cc else '')

    # ── foot
    f = d.get('foot') or {}
    links = ''.join(lnk(x) for x in (f.get('links') or []) if x.get('t'))
    foot = '<footer class="ft"><div class="ft-g"><a class="ft-m" href="%s">%s</a><div class="ft-l">%s</div><div class="ft-c">%s</div></div>%s</footer>' % (
        e(b.get('home') or '#'), logo(), links, e(f.get('legal')), '<p class="nt">%s</p>' % e(f['text']) if f.get('text') else '')

    title = ' — '.join(x for x in (name, hero.get('title')) if x)
    desc = hero.get('text') or st.get('title') or ''
    head_js = ("(function(){var h=document.documentElement;h.classList.add('js');"
               "if(!matchMedia('(prefers-reduced-motion: reduce)').matches)h.classList.add('intro')})()")
    return ('<!doctype html><html lang="%s"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>%s</title>%s<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link rel="stylesheet" href="%s"><style>:root{%s}%s</style><script>%s</script></head><body>%s<main>%s%s%s%s%s%s%s</main>%s<script>%s</script></body></html>') % (
        e(d.get('lang') or 'en'), e(title), '<meta name="description" content="%s">' % e(desc) if desc else '', FONTS, theme, CSS, head_js,
        nav, opening, story, figures, features, pricing, faq, close, foot, JS.replace('__PAL__', json.dumps(pal or [_ring])))
