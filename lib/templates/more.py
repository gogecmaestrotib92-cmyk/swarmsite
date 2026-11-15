"""more.py — the part of a client's page a template has no place for, carried under the template's own sections.

A template is a fixed build: one opening, one statement, one list, one close, a few picture places. A client's landing
with twenty sections and thirty pictures kept five and four (owner, 2026-11-13: "pretty, and two lines"). This module
adds, to any template's page, what was left:

    data['more'] = {'sections': [{'title', 'text', 'imgs'}, …]}   the sections the adapter could place nowhere, in page order,
                                                            each in the client's own words, whole
    the client's photographs the template's page does not ask for → one strip, edge to edge

It is written into the page by registry (before </main>, else before the last <footer>), so every template has it and
none had to be edited. Every section is a CARD — never bare paragraphs under a template: what is not designed does
not go on the page (owner, 2026-11-15, on a software page whose leftovers stood as plain text: the product is the look).
A card brings no colour and no typeface of its own: its ground and rule are the page's ink at 5 % and 12 %, its corner
is the corner of the page's own buttons, its heading takes the family, weight, case and tracking of the page's own h2
— read once, at load, from the page itself; where the page's ink does not read on the ground under the band, near-black
or near-white by that ground. Cards stand in columns that end level; a long card is a row of its own with its words in
two columns; a run of labels is a row of chips. A section's pictures are never boxed in its card (owner's rule,
2026-11-10): they stand with the client's other unused photographs in one strip, edge to edge.

Pure: the same data and page give the same bytes. No model, no network.
"""
import html
import re

BASE = '../../'
MAX_SECTIONS, MAX_PHOTOS, MIN_PHOTOS = 40, 8, 3

CSS = """
.sw-more{position:relative;z-index:1;padding:clamp(56px,8vw,120px) 0 clamp(40px,6vw,88px);color:inherit}
.sw-more-in{max-width:1240px;margin:0 auto;padding:0 clamp(20px,4vw,48px)}
.sw-cards{display:grid;grid-template-columns:repeat(var(--c,3),minmax(0,1fr));gap:clamp(14px,1.6vw,22px);align-items:start}
.sw-col{display:grid;gap:clamp(14px,1.6vw,22px);min-width:0}
.sw-card{display:block;margin:0;padding:clamp(22px,2.2vw,32px);border-radius:var(--sw-r,16px);
background:color-mix(in srgb,currentColor 5%,transparent);border:1px solid color-mix(in srgb,currentColor 12%,transparent)}
.sw-card h3{margin:0 0 .7em;font-size:clamp(19px,1.5vw,24px);line-height:1.15;color:inherit;text-wrap:balance;overflow-wrap:anywhere}
.sw-card p{margin:0;font-size:clamp(15px,1.05vw,16.5px);line-height:1.6;color:inherit;opacity:.84;overflow-wrap:anywhere}
.sw-card p+p,.sw-card p+ul,.sw-card ul+p{margin-top:.9em}
.sw-card.sw-lead p{font-size:clamp(17px,1.35vw,21px);line-height:1.5;opacity:1}
.sw-more-in>*+*{margin-top:clamp(14px,1.6vw,22px)}
.sw-wide .sw-card-body{column-count:2;column-gap:clamp(28px,4vw,64px)}.sw-wide .sw-card-body p{break-inside:avoid}.sw-wide h3{max-width:24em}
.sw-chips{display:flex;flex-wrap:wrap;gap:8px;margin:0;padding:0;list-style:none}
.sw-chips li{padding:.42em .85em;border-radius:999px;border:1px solid color-mix(in srgb,currentColor 18%,transparent);font-size:clamp(13px,.95vw,14.5px);line-height:1.25;opacity:.9}
.sw-strip{position:relative;z-index:1;display:grid;grid-template-columns:repeat(var(--n,4),minmax(0,1fr));gap:4px;margin:0;padding:0 0 clamp(40px,6vw,88px)}
.sw-strip img{display:block;width:100%;height:100%;aspect-ratio:4/3;object-fit:cover}
@media (max-width:1080px){.sw-cards{grid-template-columns:repeat(2,minmax(0,1fr))}.sw-cards[style*="--c:3"] .sw-col:last-child{grid-column:1/-1;grid-template-columns:repeat(2,minmax(0,1fr));align-items:start}}
@media (max-width:700px){.sw-wide .sw-card-body{column-count:1}.sw-cards,.sw-cards[style*="--c:3"] .sw-col:last-child{grid-template-columns:minmax(0,1fr)}.sw-strip{grid-template-columns:repeat(2,minmax(0,1fr))}}
"""

# the band's headings take the page's own heading face: read from its first h2 (else its h1) once the page has loaded
JS = ("(function(){var b=document.querySelector('.sw-more');if(b){var q=document.querySelectorAll('a,button'),r=0;for(var z=0;z<q.length&&z<60;z++){if(q[z].closest('.sw-more'))continue;var v=parseFloat(getComputedStyle(q[z]).borderTopLeftRadius)||0,h=q[z].getBoundingClientRect().height;if(v>0&&h>28){r=Math.min(v,h/2,24);break}}b.style.setProperty('--sw-r',(r||14)+'px')}var m=document.querySelectorAll('.sw-more h2,.sw-more h3');if(!m.length)return;var s=null,c=document.querySelectorAll('h2,h1');"
      "for(var i=0;i<c.length;i++){if(!c[i].closest('.sw-more')){s=c[i];if(c[i].tagName==='H2')break}}if(!s)return;var k=getComputedStyle(s);"
      "for(var j=0;j<m.length;j++){var e=m[j].style;e.fontFamily=k.fontFamily;e.fontWeight=k.fontWeight;e.fontStyle=k.fontStyle;"
      "e.textTransform=k.textTransform;e.letterSpacing=m[j].tagName==='H2'?k.letterSpacing:'normal'}})();")

# the band's ink is the page's, unless the page's ink does not read on the ground the band stands on (a template whose
# body carries one colour and whose sections each set their own): then it is near-black or near-white, by that ground
INK_JS = ("(function(){var b=document.querySelector('.sw-more');if(!b)return;var n=function(c){var m=(c||'').match(/[\\d.]+/g);return m?m.map(Number):null},"
          "g=null;for(var e=b;e;e=e.parentElement){var c=n(getComputedStyle(e).backgroundColor);if(c&&(c.length<4||c[3]>.5)){g=c;break}}if(!g)g=[255,255,255];"
          "var f=function(v){v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)},L=function(c){return .2126*f(c[0])+.7152*f(c[1])+.0722*f(c[2])},"
          "k=n(getComputedStyle(b).color)||[0,0,0],x=L(g),y=L(k),r=(Math.max(x,y)+.05)/(Math.min(x,y)+.05);if(r<7)b.style.color=x>.4?'#111111':'#f5f5f5'})();")

WIDE = 520      # a card with more words than this, or more than four paragraphs, is a row of its own
LEAD = 420      # what is set large under the opening is a few lines, never a screenful


def _e(s):
    return html.escape(str(s or ''), quote=True)


def _chips(para):
    """a paragraph that is a run of short labels (`A · B · C`) as a row of chips; '' when it is not one"""
    items = [i.strip() for i in para.split(' · ')]
    if len(items) < 3 or any(not i or len(i) > 60 for i in items):
        return ''
    return '<ul class="sw-chips">%s</ul>' % ''.join('<li>%s</li>' % _e(i) for i in items)


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


def band(d, page):
    """the markup to add to `page` for the data's leftover sections and unused photographs ('' when there are none)"""
    asked = lambda src: (BASE + src) in page or (BASE + html.escape(src, quote=True)) in page
    secs, own = [], set()
    for x in ((d.get('more') or {}).get('sections') or [])[:MAX_SECTIONS]:
        if not isinstance(x, dict) or not (x.get('title') or x.get('text')):
            continue
        # a section's own pictures, unless the template's page (or a section before it) already shows them
        imgs = [p for p in x.get('imgs') or [] if isinstance(p, dict) and p.get('src') and not asked(p['src']) and p['src'] not in own]
        imgs = []                                                  # in a card band a section's pictures go to the strip
        own.update(p['src'] for p in imgs)
        if x.get('text'):
            secs.append({'title': str(x.get('title') or ''), 'text': str(x.get('text') or ''), 'imgs': imgs})
    pics = [p for p in unused_photos(d, page) if p['src'] not in own][:MAX_PHOTOS]
    if len(pics) < MIN_PHOTOS:
        pics = []
    if not secs and not pics:
        return ''
    out = ['<style>%s</style>' % CSS.strip().replace('\n', '')]
    if secs:
        # Every section is a card in the page's own ink, corner and heading face — never bare paragraphs under the
        # template (owner, 2026-11-15: what is not designed does not go on the page). Cards stand in columns and
        # fill them top down, so a long passage beside short notes leaves no empty half of a screen. A section's
        # own pictures are not set in its card: they stand in the strip of photographs below.
        cards = []
        for n, x in enumerate(secs):
            body = ''.join(_chips(p) or '<p>%s</p>' % _e(p) for p in [q.strip() for q in re.split(r'\n{2,}', x['text']) if q.strip()])
            if not body:
                continue
            lead = not x['title'] and not cards and len(x['text']) <= LEAD
            paras = [q for q in re.split(r'\n{2,}', x['text']) if q.strip()]
            tall = 64 + (30 if x['title'] else 0) + sum(26 * (1 + len(q) // (34 if lead else 46)) + 14 for q in paras)   # how tall the card stands in a column, about
            wide = not lead and (len(x['text']) > WIDE or len(paras) > 4)
            cards.append((tall, wide, '<article class="sw-card%s">%s%s</article>' % (' sw-lead' if lead else ' sw-wide' if wide else '', '<h3>%s</h3>' % _e(x['title']) if x['title'] else '',
                                                                               '<div class="sw-card-body">%s</div>' % body if wide else body)))
        if cards:
            # in page order: cards stand in columns, each into the column that is shortest so far, so the columns end
            # level; a long card (a passage, a list of sentences) is a row of its own across the width with its words
            # in two columns — beside short cards it would leave a hole the height of itself
            rows, run = [], []

            def flush():
                if not run:
                    return
                n = 1 if len(run) == 1 else 2 if len(run) in (2, 4) else 3
                cols, high = [[] for _ in range(n)], [0.0] * n
                for tall, card in run:
                    k = high.index(min(high))
                    cols[k].append(card)
                    high[k] += tall
                rows.append('<div class="sw-cards" style="--c:%d">%s</div>' % (n, ''.join('<div class="sw-col">%s</div>' % ''.join(c) for c in cols)))
                run.clear()
            for tall, wide, card in cards:
                if wide:
                    flush()
                    rows.append(card)
                else:
                    run.append((tall, card))
            flush()
            out.append('<section class="sw-more" data-more><div class="sw-more-in">%s</div></section>' % ''.join(rows))
        else:
            secs = []
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
