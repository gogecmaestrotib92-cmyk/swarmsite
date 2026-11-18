"""more.py — the part of a client's page a template has no place for, carried under the template's own sections.

A template is a fixed build: one opening, one statement, one list, one close, a few picture places. A client's landing
with twenty sections and thirty pictures kept five and four (owner, 2026-11-13: "pretty, and two lines"). This module
adds, to any template's page, what was left:

    data['more'] = {'sections': [{'title', 'text', 'imgs'}, …]}   the sections the adapter could place nowhere, in page order,
                                                            each in the client's own words, whole
    the client's photographs the template's page does not ask for → one strip, edge to edge

It is written into the page by registry, so every template has it and none had to be edited.

What is not designed does not go on the page (owner, 2026-11-15: the product is the look; a section is left out rather
than set badly). Measured wide on 2026-11-17 (six software sites, three designs each, beside their references): on a
long landing the band was 46–66 % of the page's words — 31 and 43 grey cards of every length, three to four screens of
them after the page's closing call, where no reference has anything. So the band is one designed part and no more:

    one even grid of two, three, four or six cards, each a heading over a few lines — a section with no heading, with
    more than CARD_MAX characters, with more than two paragraphs or made of a run of labels is not a card and is not
    on the page (its words stay in the data: `more.sections`);
    it stands before the page's closing call, not after it: a page ends on its call and its foot.

A card brings no colour and no typeface of its own: its ground and rule are the page's ink at 5 % and 12 %, its corner
is the corner of the page's own buttons, its heading takes the family, weight, case and tracking of the page's own h2
— read once, at load, from the page itself; where the page's ink does not read on the ground under the band, near-black
or near-white by that ground. A section's pictures are never boxed in its card (owner's rule, 2026-11-10): they stand
with the client's other unused photographs in one strip, edge to edge — photographs only: one marked small, dim or
carrying lettering (a crest, a flyer) is not in it.

Pure: the same data and page give the same bytes. No model, no network.
"""
import html
import re

BASE = '../../'
MAX_SECTIONS, MAX_PHOTOS, MIN_PHOTOS = 40, 8, 3

CSS = """
.sw-more{position:relative;z-index:1;padding:clamp(56px,8vw,120px) 0 clamp(40px,6vw,88px);color:inherit}
.sw-more-in{max-width:1240px;margin:0 auto;padding:0 clamp(20px,4vw,48px)}
.sw-cards{display:grid;grid-template-columns:repeat(var(--c,3),minmax(0,1fr));gap:clamp(14px,1.6vw,22px);align-items:stretch}
.sw-card{display:block;margin:0;padding:clamp(22px,2.2vw,32px);border-radius:var(--sw-r,16px);
background:color-mix(in srgb,currentColor 5%,transparent);border:1px solid color-mix(in srgb,currentColor 12%,transparent)}
.sw-card h3{margin:0 0 .7em;font-size:clamp(19px,1.5vw,24px);line-height:1.15;color:inherit;text-wrap:balance;overflow-wrap:anywhere}
.sw-card p{margin:0;font-size:clamp(15px,1.05vw,16.5px);line-height:1.6;color:inherit;opacity:.84;overflow-wrap:anywhere}
.sw-card p+p{margin-top:.9em}
.sw-strip{position:relative;z-index:1;display:grid;grid-template-columns:repeat(var(--n,4),minmax(0,1fr));gap:4px;margin:0;padding:0 0 clamp(40px,6vw,88px)}
.sw-strip img{display:block;width:100%;height:100%;aspect-ratio:4/3;object-fit:cover}
@media (max-width:1080px){.sw-cards.sw-six{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:700px){.sw-cards,.sw-cards.sw-six{grid-template-columns:minmax(0,1fr)}.sw-strip{grid-template-columns:repeat(2,minmax(0,1fr))}}
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

CARD_MIN, CARD_MAX = 40, 280    # a card holds a few lines: under that it says nothing, over it it is a passage
TITLE_WORDS = 9                 # a card's heading is a heading, not a sentence
CLOSE_WORDS = 60                # a page's last section with a call and no more words than this is its closing call


def _e(s):
    return html.escape(str(s or ''), quote=True)


def _labels(para):
    """is the paragraph a run of short labels (`A · B · C`) and not a sentence?"""
    items = [i.strip() for i in para.split(' · ')]
    return len(items) >= 3 and all(i and len(i) <= 60 for i in items)


def cards(d):
    """the leftover sections that stand as cards, in page order: (shown, not shown). A card is a heading of at most
    TITLE_WORDS words over CARD_MIN–CARD_MAX characters in one or two paragraphs of running words; the grid is even —
    six, four, three or two of them, never one and never an odd row."""
    fit, rest = [], []
    for x in ((d.get('more') or {}).get('sections') or []):
        if not isinstance(x, dict) or not (x.get('title') or x.get('text')):
            continue
        title, text = str(x.get('title') or '').strip(), str(x.get('text') or '').strip()
        paras = [q.strip() for q in re.split(r'\n{2,}', text) if q.strip()]
        ok = bool(title) and len(title.split()) <= TITLE_WORDS and CARD_MIN <= len(text) <= CARD_MAX and len(paras) <= 2 and not any(_labels(q) for q in paras)
        (fit if ok else rest).append({'title': title, 'text': text, 'paras': paras})
    n = 6 if len(fit) >= 6 else 4 if len(fit) >= 4 else len(fit) if len(fit) >= 2 else 0
    return fit[:n], fit[n:] + rest


def unused_photos(d, page):
    """the client's photographs the page does not ask for, in the data's order (never a made picture, a screen or a logo;
    never one marked small, dim or lettered: a strip is photographs that read)"""
    out, seen = [], set()
    for p in ((d.get('media') or {}).get('photos') or []):
        src = p.get('src') if isinstance(p, dict) else None
        if not src or src in seen or p.get('small') or p.get('dim') or p.get('lettering') or (BASE + src) in page or (BASE + html.escape(src, quote=True)) in page:
            continue
        seen.add(src)
        out.append(p)
    return out


def _img(p):
    return '<img src="%s%s" alt="%s" width="%d" height="%d" loading="lazy" decoding="async">' % (BASE, _e(p['src']), _e(p.get('alt')), int(p.get('w') or 4), int(p.get('h') or 3))


def band(d, page):
    """the markup to add to `page` for the data's leftover sections and unused photographs ('' when there are none)"""
    secs, _ = cards(d)
    pics = unused_photos(d, page)[:MAX_PHOTOS]
    if len(pics) < MIN_PHOTOS:
        pics = []
    if not secs and not pics:
        return ''
    out = ['<style>%s</style>' % CSS.strip().replace('\n', '')]
    if secs:
        n = len(secs)
        out.append('<section class="sw-more" data-more><div class="sw-more-in"><div class="sw-cards%s" style="--c:%d">%s</div></div></section>' % (
            ' sw-six' if n == 6 else '', 2 if n in (2, 4) else 3,
            ''.join('<article class="sw-card"><h3>%s</h3>%s</article>' % (_e(x['title']), ''.join('<p>%s</p>' % _e(q) for q in x['paras'])) for x in secs)))
    if pics:
        n = 4 if len(pics) >= 8 else 3 if len(pics) in (3, 6) else 4 if len(pics) == 4 else 3
        pics = pics[:len(pics) - len(pics) % n] if len(pics) % n and len(pics) > n else pics
        out.append('<div class="sw-strip" data-more style="--n:%d">%s</div>' % (n, ''.join(_img(p) for p in pics)))
    if secs:
        out.append('<script>%s%s</script>' % (JS, INK_JS))
    return ''.join(out)


def _close(page, end):
    """where the page's closing call begins, when the page ends on one: the last section closed before `end` with
    nothing said between it and `end` — or the section `end` lies in, on a page whose foot stands inside its closing
    section — with no section inside it, a link or a button in it and at most CLOSE_WORDS words; -1 when the page's
    last section is something else (questions, plans, a list)"""
    stack, last = [], None
    for m in re.finditer(r'<section\b[^>]*>|</section>', page[:end]):
        if m.group(0).startswith('</'):
            if stack:
                last = (stack.pop(), m.end())
        else:
            stack.append(m.start())
    if stack:
        last = (stack[-1], end)
    if not last:
        return -1
    a, b = last
    plain = lambda t: html.unescape(re.sub(r'<[^>]+>', ' ', re.sub(r'<(script|style|svg|noscript)\b[\s\S]*?</\1>', ' ', t))).split()
    inner = page[a:b]
    if plain(page[b:end]) or inner.count('<section') > 1 or len(plain(inner)) > CLOSE_WORDS or not re.search(r'<(?:a|button)\b', inner):
        return -1
    return a


def add(d, page):
    """`page` with the band written in: before the page's closing call when it ends on one, else before </main> or
    before the last <footer>, whichever comes first"""
    b = band(d, page)
    if not b:
        return page
    spots = [i for i in (page.rfind('</main>'), page.rfind('<footer')) if i >= 0]   # a foot inside <main> comes first: the band stands above it
    i = min(spots) if spots else page.rfind('</body>')
    if i < 0:
        return page
    c = _close(page, i)
    i = c if c >= 0 else i
    return page[:i] + b + page[i:]
