"""more.py — the part of a client's page a template has no place for, carried under the template's own sections.

A template is a fixed build: one opening, one statement, one list, one close, a few picture places. A client's landing
with twenty sections and thirty pictures kept five and four (owner, 2026-11-13: "pretty, and two lines"). This module
adds, to any template's page, what was left:

    data['more'] = {'sections': [{'title', 'text', 'imgs'}, …]}   the sections the adapter could place nowhere, in page order,
                                                            each in the client's own words, whole
    the client's photographs the template's page does not ask for → one strip, edge to edge

It is written into the page by registry (before </main>, else before the last <footer>), so every template has it and
none had to be edited. It brings no colour and no typeface of its own: the ground and the ink are the page's (it
inherits them; where the page's ink does not read on the ground under it, near-black or near-white by that ground), and its headings take the family, weight, case and tracking of the page's own h2 — read once, at load,
from the page itself — so it reads as that design's text, not as a second site under it. Words are never set beside a
boxed picture: the words are a column, the pictures are a strip across the whole width (owner's rule, 2026-11-10).

Pure: the same data and page give the same bytes. No model, no network.
"""
import html
import re

BASE = '../../'
MAX_SECTIONS, MAX_PHOTOS, MIN_PHOTOS = 12, 8, 3

CSS = """
.sw-more{position:relative;z-index:1;padding:clamp(56px,9vw,128px) 0 clamp(40px,6vw,88px);color:inherit}
.sw-more-in{max-width:1200px;margin:0 auto;padding:0 clamp(20px,4vw,48px)}
.sw-more-in+.sw-more-in{margin-top:clamp(48px,7vw,104px)}
.sw-more-row{display:grid;grid-template-columns:minmax(0,5fr) minmax(0,7fr);gap:clamp(16px,4vw,64px);align-items:start}
.sw-more-row+.sw-more-row{margin-top:clamp(40px,6vw,88px)}
.sw-more h2{margin:0;font-size:clamp(26px,3.2vw,44px);line-height:1.08;color:inherit;text-wrap:balance;overflow-wrap:anywhere}
.sw-more h3{margin:0 0 .6em;font-size:clamp(20px,1.7vw,26px);line-height:1.15;color:inherit;text-wrap:balance;overflow-wrap:anywhere}
.sw-more p{margin:0;font-size:clamp(16px,1.25vw,19px);line-height:1.6;color:inherit;max-width:62ch;opacity:.86}
.sw-more p+p{margin-top:1em}
.sw-more-grid{display:grid;grid-template-columns:repeat(var(--c,3),minmax(0,1fr));gap:clamp(32px,4vw,64px) clamp(24px,4vw,56px)}
.sw-more-grid p{font-size:clamp(15px,1.1vw,17px)}
.sw-more-pic{display:block;width:100%;margin:clamp(24px,3vw,48px) 0 0}.sw-more-pic+.sw-more-in{margin-top:clamp(48px,7vw,104px)}
.sw-more-pic img{display:block;width:100%;height:auto;max-height:78vh;object-fit:cover}
.sw-more-own{margin:clamp(20px,3vw,40px) 0 0}.sw-more-own img{display:block;width:100%;height:auto;max-height:80vh;object-fit:contain;object-position:left top}
.sw-strip{position:relative;z-index:1;display:grid;grid-template-columns:repeat(var(--n,4),minmax(0,1fr));gap:4px;margin:0;padding:0 0 clamp(40px,6vw,88px)}
.sw-strip img{display:block;width:100%;height:100%;aspect-ratio:4/3;object-fit:cover}
@media (max-width:900px){.sw-more-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:760px){.sw-more-row{grid-template-columns:minmax(0,1fr);gap:12px}.sw-more-grid{grid-template-columns:minmax(0,1fr)}.sw-strip{grid-template-columns:repeat(2,minmax(0,1fr))}}
"""

# the band's headings take the page's own heading face: read from its first h2 (else its h1) once the page has loaded
JS = ("(function(){var m=document.querySelectorAll('.sw-more h2,.sw-more h3');if(!m.length)return;var s=null,c=document.querySelectorAll('h2,h1');"
      "for(var i=0;i<c.length;i++){if(!c[i].closest('.sw-more')){s=c[i];if(c[i].tagName==='H2')break}}if(!s)return;var k=getComputedStyle(s);"
      "for(var j=0;j<m.length;j++){var e=m[j].style;e.fontFamily=k.fontFamily;e.fontWeight=k.fontWeight;e.fontStyle=k.fontStyle;"
      "e.textTransform=k.textTransform;e.letterSpacing=m[j].tagName==='H2'?k.letterSpacing:'normal'}})();")

# the band's ink is the page's, unless the page's ink does not read on the ground the band stands on (a template whose
# body carries one colour and whose sections each set their own): then it is near-black or near-white, by that ground
INK_JS = ("(function(){var b=document.querySelector('.sw-more');if(!b)return;var n=function(c){var m=(c||'').match(/[\\d.]+/g);return m?m.map(Number):null},"
          "g=null;for(var e=b;e;e=e.parentElement){var c=n(getComputedStyle(e).backgroundColor);if(c&&(c.length<4||c[3]>.5)){g=c;break}}if(!g)g=[255,255,255];"
          "var f=function(v){v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)},L=function(c){return .2126*f(c[0])+.7152*f(c[1])+.0722*f(c[2])},"
          "k=n(getComputedStyle(b).color)||[0,0,0],x=L(g),y=L(k),r=(Math.max(x,y)+.05)/(Math.min(x,y)+.05);if(r<7)b.style.color=x>.4?'#111111':'#f5f5f5'})();")

SHORT = 260     # a section whose words are this short is a note, not a passage: notes stand together as a grid


def _e(s):
    return html.escape(str(s or ''), quote=True)


def _paras(text):
    parts = [p.strip() for p in re.split(r'\n{2,}', str(text or '')) if p.strip()]
    return ''.join('<p>%s</p>' % _e(p) for p in parts)


def unused_photos(d, page):
    """the client's photographs the page does not ask for, in the data's order (never a made picture, a screen or a logo)"""
    out, seen = [], set()
    for p in ((d.get('media') or {}).get('photos') or []):
        src = p.get('src') if isinstance(p, dict) else None
        if not src or src in seen or (BASE + src) in page or (BASE + html.escape(src, quote=True)) in page:
            continue
        seen.add(src)
        out.append(p)
    return out


def _img(p):
    return '<img src="%s%s" alt="%s" width="%d" height="%d" loading="lazy" decoding="async">' % (BASE, _e(p['src']), _e(p.get('alt')), int(p.get('w') or 4), int(p.get('h') or 3))


def groups(secs):
    """the sections in page order as the band sets them: ('grid', [notes…]) for a run of two or more short ones,
    ('row', section) for a passage, a section with pictures of its own, or a short one standing alone. The rhythm is
    the content's own: nothing is set as twelve like rows (the measured references vary how a long page is told; see
    lib/devices held-index, which asks for three to five items with something to show — a run of bare notes is a
    grid, not that)."""
    out, run = [], []

    def flush():
        if len(run) >= 2:
            out.append(('grid', list(run)))
        else:
            out.extend(('row', x) for x in run)
        run.clear()
    for x in secs:
        if x['text'] and len(x['text']) <= SHORT and not x.get('imgs'):
            run.append(x)
        else:
            flush()
            out.append(('row', x))
    flush()
    return out


def band(d, page):
    """the markup to add to `page` for the data's leftover sections and unused photographs ('' when there are none)"""
    asked = lambda src: (BASE + src) in page or (BASE + html.escape(src, quote=True)) in page
    secs, own = [], set()
    for x in ((d.get('more') or {}).get('sections') or [])[:MAX_SECTIONS]:
        if not isinstance(x, dict) or not x.get('title'):
            continue
        # a section's own pictures, unless the template's page (or a section before it) already shows them
        imgs = [p for p in x.get('imgs') or [] if isinstance(p, dict) and p.get('src') and not asked(p['src']) and p['src'] not in own]
        own.update(p['src'] for p in imgs)
        if x.get('text') or imgs:
            secs.append({'title': x['title'], 'text': str(x.get('text') or ''), 'imgs': imgs})
    pics = [p for p in unused_photos(d, page) if p['src'] not in own][:MAX_PHOTOS]
    if len(pics) < MIN_PHOTOS:
        pics = []
    if not secs and not pics:
        return ''
    out = ['<style>%s</style>' % CSS.strip().replace('\n', '')]
    if secs:
        parts = []
        for kind, g in groups(secs):
            if kind == 'grid':
                cells = ''.join('<div><h3>%s</h3>%s</div>' % (_e(x['title']), _paras(x['text'])) for x in g)
                parts.append('<div class="sw-more-in"><div class="sw-more-grid" style="--c:%d">%s</div></div>' % (2 if len(g) in (2, 4) else 3, cells))
                continue
            parts.append('<div class="sw-more-in"><div class="sw-more-row"><h2>%s</h2><div>%s</div></div></div>' % (_e(g['title']), _paras(g['text'])))
            wide = lambda p: int(p.get('w') or 0) >= 1200 and int(p.get('w') or 0) >= 1.2 * int(p.get('h') or 1)
            if len(g['imgs']) == 1 and wide(g['imgs'][0]):           # one large landscape picture: across the whole width
                parts.append('<figure class="sw-more-pic">%s</figure>' % _img(g['imgs'][0]))
            elif len(g['imgs']) == 1:                                 # a small or upright one (a cover, a portrait) at its own size, never blown up
                parts.append('<div class="sw-more-in"><figure class="sw-more-own" style="max-width:%dpx">%s</figure></div>' % (min(int(g['imgs'][0].get('w') or 640), 720), _img(g['imgs'][0])))
            elif g['imgs']:                                           # two to four: one row across the whole width
                parts.append('<div class="sw-strip sw-more-pic" style="--n:%d;padding-bottom:0">%s</div>' % (len(g['imgs']), ''.join(_img(p) for p in g['imgs'])))
        out.append('<section class="sw-more" data-more>%s</section>' % ''.join(parts))
    if pics:
        n = 4 if len(pics) >= 8 else 3 if len(pics) in (3, 6) else 4 if len(pics) == 4 else 3
        pics = pics[:len(pics) - len(pics) % n] if len(pics) % n and len(pics) > n else pics
        out.append('<div class="sw-strip" data-more style="--n:%d">%s</div>' % (n, ''.join(_img(p) for p in pics)))
    if secs:
        out.append('<script>%s%s</script>' % (JS, INK_JS))
    return ''.join(out)


def add(d, page):
    """`page` with the band written in: before </main> or before the last <footer>, whichever comes first"""
    b = band(d, page)
    if not b:
        return page
    spots = [i for i in (page.rfind('</main>'), page.rfind('<footer')) if i >= 0]   # a foot inside <main> comes first: the band stands above it
    i = min(spots) if spots else page.rfind('</body>')
    return page if i < 0 else page[:i] + b + page[i:]
