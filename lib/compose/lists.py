"""lists.py — a list section drawn in another form: validated whole, drawn with the page's own type, put in place.

Most of a page below its first screen is lists, and the production renderer has one form for each kind. A list
composition names sections of the page and says how each is drawn — as a ledger of large numerals, as staggered
columns, as a bento of tiles with one item featured — and where its heading sits. Like a hero composition it cannot
say anything: every item, in its order, with its tag, title, body, picture and link, comes from the page through
lib/compose/sections.py. The section keeps its id, its band, its own heading block and everything it holds after the
list (its buttons, its links to the source), byte for byte.

  validate(doc, page_html)        → [{'code', 'at', 'message'}]        ([] = may be drawn)
  transplant(page_html, doc)      → (page_html, {'drawn', 'errors', 'sections'})
  a document: {"ir": "0.2", "lists": [{"section": id, "form": ledger|stagger|bento, "head": top|left|sticky,
               "numerals": big|outline|small|none, "cols": 2|3, "feature": item position, "title": md|lg}]}
Deterministic, no network, no model. A document that fails is refused whole and the page comes back untouched."""
import html as H, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sections as SECTIONS
import validate as V

e = lambda s: H.escape(str(s if s is not None else ''), quote=True)
FORMS = ('ledger', 'stagger', 'bento')
HEADS = ('top', 'left', 'sticky')
NUMERALS = ('big', 'outline', 'small', 'none')
TITLES = ('md', 'lg')
KEYS = {'section', 'form', 'head', 'numerals', 'cols', 'feature', 'title'}


def numbering(items):
    """Are these tags only the items' own positions (01, 02, 03 …)? Then they are numbering and may be drawn any way or
    left out. Anything else — "14 days", "60+", a "39" on the first card — is a fact of the business and is always shown."""
    return all(re.fullmatch(r'\d{1,2}', i['tag'] or '') and int(i['tag']) == n + 1 for n, i in enumerate(items) if i['tag'])

CSS = """
.sec.lc .lc-wrap{display:grid;gap:clamp(28px,4vw,64px);grid-template-columns:minmax(0,1fr)}
.sec.lc .lc-head .gh{margin-bottom:0}
.sec.lc .lc-list{list-style:none;margin:0;padding:0;display:grid;gap:var(--gutter,32px);min-width:0}
.sec.lc .lc-item{min-width:0;overflow-wrap:break-word;margin:0}
.sec.lc .lc-item p{margin:0;max-width:52ch}
.sec.lc .lc-title{margin:0;text-wrap:balance}.sec.lc .lc-t-lg .lc-title{font-size:clamp(24px,2.6vw,40px);line-height:1.04}
.sec.lc .lc-tag{display:block;font-family:var(--display);font-weight:var(--h1-w,500);line-height:.9;letter-spacing:var(--h1-ls,-.02em);font-variant-numeric:tabular-nums;white-space:nowrap}
.sec.lc .lc-n-small .lc-tag{font-family:var(--label);font-weight:400;font-size:var(--lab-px,12px);letter-spacing:var(--lab-ls,.08em);line-height:1.4;color:var(--muted)}
.sec.lc .lc-n-outline .lc-tag{-webkit-text-stroke:max(1px,.016em) currentColor;-webkit-text-fill-color:transparent}
.sec.lc .lc-item .link{display:inline-block;margin-top:10px}
.sec.lc .lc-item figure{margin:0 0 14px;overflow:hidden;border-radius:var(--radius,0)}.sec.lc .lc-item figure img{display:block;width:100%;height:auto}
@media(min-width:901px){
.sec.lc .lc-head-left,.sec.lc .lc-head-sticky{grid-template-columns:minmax(0,4fr) minmax(0,8fr);align-items:start}
.sec.lc .lc-head-left .gh,.sec.lc .lc-head-sticky .gh{display:block;border-bottom:0;padding-bottom:0;text-align:left}
.sec.lc .lc-head-left .gh *,.sec.lc .lc-head-sticky .gh *{text-align:left!important;margin-left:0!important;margin-right:0!important}
.sec.lc .lc-head-left .gh .lede,.sec.lc .lc-head-sticky .gh .lede{margin-top:16px}
.sec.lc .lc-head-sticky .lc-head{position:sticky;top:calc(var(--nav-h,64px) + 28px)}
}
.sec.lc-ledger .lc-list{gap:0}
.sec.lc-ledger .lc-item{display:grid;grid-template-columns:minmax(0,2.4fr) minmax(0,4fr) minmax(0,5fr);column-gap:var(--gutter,32px);align-items:baseline;padding:clamp(18px,2.4vw,34px) 0;border-top:1px solid var(--line)}
.sec.lc-ledger .lc-item:last-child{border-bottom:1px solid var(--line)}
.sec.lc-ledger .lc-tag{font-size:clamp(34px,4.4vw,72px)}
.sec.lc-ledger .lc-n-none .lc-item{grid-template-columns:minmax(0,5fr) minmax(0,6fr)}
.sec.lc-ledger .lc-head-left .lc-item,.sec.lc-ledger .lc-head-sticky .lc-item{grid-template-columns:minmax(0,2fr) minmax(0,6fr)}
.sec.lc-ledger .lc-head-left .lc-item p,.sec.lc-ledger .lc-head-sticky .lc-item p{grid-column:2;margin-top:8px}
.sec.lc-ledger .lc-head-left .lc-tag,.sec.lc-ledger .lc-head-sticky .lc-tag{font-size:clamp(28px,3.2vw,52px)}
.sec.lc-stagger .lc-list{grid-template-columns:repeat(var(--n,2),minmax(0,1fr));row-gap:clamp(40px,5vw,84px);column-gap:clamp(28px,5vw,96px)}
.sec.lc-stagger .lc-tag{font-size:clamp(44px,5.6vw,96px);margin-bottom:.2em}
.sec.lc-stagger .lc-title{margin-bottom:10px}
.sec.lc-stagger .lc-item{border-top:1px solid var(--line);padding-top:clamp(14px,1.6vw,22px)}
.sec.lc-bento .lc-list{grid-template-columns:repeat(6,minmax(0,1fr));gap:clamp(10px,1.2vw,18px)}
.sec.lc-bento .lc-item{grid-column:span var(--span,2);grid-row:span var(--rows,1);display:flex;flex-direction:column;justify-content:flex-end;gap:8px;min-height:clamp(150px,14vw,210px);padding:clamp(18px,2vw,30px);border:1px solid var(--line);border-radius:max(var(--radius,0px),10px)}
.sec.lc-bento .lc-tag{font-size:clamp(30px,3.4vw,56px);margin-bottom:auto;padding-bottom:18px}
.sec.lc-bento .lc-feature{background:var(--accent);color:var(--on-accent,var(--paper));border-color:transparent}
.sec.lc-bento .lc-feature .lc-tag{font-size:clamp(54px,7vw,120px);color:inherit;-webkit-text-fill-color:currentColor;-webkit-text-stroke:0}
.sec.lc-bento .lc-feature .lc-title{font-size:clamp(26px,3vw,46px);line-height:1.02}
.sec.lc-bento .lc-n-small .lc-feature .lc-tag{font-family:var(--display);color:inherit}
.sec.lc-bento .lc-ordinal .lc-feature .lc-tag{font-size:clamp(30px,3.4vw,56px)}.sec.lc-bento .lc-ordinal .lc-feature .lc-title{font-size:clamp(34px,4.6vw,76px);line-height:.98;max-width:14ch}
@media(min-width:901px){.sec.lc-stagger .lc-list[style*="--n:2"] .lc-item:nth-child(even),.sec.lc-stagger .lc-list[style*="--n:3"] .lc-item:nth-child(3n+2){margin-top:clamp(36px,5.5vw,92px)}}
@media(max-width:900px){
.sec.lc .lc-list{grid-template-columns:minmax(0,1fr)!important}
.sec.lc-ledger .lc-item{grid-template-columns:minmax(0,1fr)!important;row-gap:8px}.sec.lc-ledger .lc-item p{grid-column:auto!important;margin-top:0!important}
.sec.lc-bento .lc-item{grid-column:auto;grid-row:auto;min-height:0}
}
"""


def _spans(count, feature):
    """Tile sizes of a bento on a six-column grid: the featured item four columns wide and two rows tall, the next two
    stacked beside it, the rest three to a row; a last row of one or two is stretched so that no cell is left empty."""
    out = [(2, 1)] * count; out[feature] = (4, 2)
    rest = [i for i in range(count) if i != feature][2:]; left = len(rest) % 3
    if left == 1: out[rest[-1]] = (6, 1)
    elif left == 2: out[rest[-1]] = out[rest[-2]] = (3, 1)
    return out


def _read(page_html):
    """{section id: (section record, content or the reason it cannot be read)} for the list sections of the page."""
    found = {}
    for sec in SECTIONS.sections(page_html):
        if not sec['kind'] or not sec['id']: continue
        try: found[sec['id']] = (sec, SECTIONS.from_section(page_html[sec['span'][0]:sec['span'][1]]))
        except ValueError as err: found[sec['id']] = (sec, str(err))
    return found


def validate(doc, page_html):
    errors = []
    def err(code, at, message): errors.append({'code': code, 'at': at, 'message': message})
    if not isinstance(doc, dict) or doc.get('ir') not in V.ACCEPTED or not isinstance(doc.get('lists'), list) or not doc['lists'] or len(doc['lists']) > 12 or set(doc) - {'ir', 'lists', 'note'}:
        err('IL001', 'ir', f'a list composition is {{"ir": "{V.VERSION}", "lists": [1–12 objects]}}'); return errors
    page = _read(page_html); named = []
    for i, entry in enumerate(doc['lists']):
        where = f'lists[{i}]'
        if not isinstance(entry, dict): err('IL001', where, 'each list is an object'); continue
        extra = set(entry) - KEYS
        if extra:   # as for the first screen: a field that could carry words does not exist
            err('IL011' if extra & {'text', 'content', 'html', 'label', 'href', 'value', 'title_text', 'items', 'heading'} else 'IL001', where, f'unknown fields {sorted(extra)}: a composition places what the page says, it does not contain it')
        sid = entry.get('section'); where = f'lists[{sid}]' if isinstance(sid, str) else where
        if not isinstance(sid, str) or sid not in page: err('IL010', where, f'no list section "{sid}" on this page; the lists are {sorted(page)}'); continue
        if sid in named: err('IL010', where, f'section "{sid}" is named twice')
        named.append(sid)
        _, content = page[sid]
        if isinstance(content, str): err('IL010', where, f'section "{sid}" cannot be recomposed: {content}'); continue
        items = content['items']; form = entry.get('form'); head = entry.get('head', 'top'); numerals = entry.get('numerals', 'big')
        if form not in FORMS: err('IL020', where, f'form is one of {FORMS}')
        if head not in HEADS: err('IL020', where, f'head is one of {HEADS}')
        if numerals not in NUMERALS: err('IL020', where, f'numerals is one of {NUMERALS}')
        if entry.get('title', 'md') not in TITLES: err('IL020', where, f'title is one of {TITLES}')
        cols = entry.get('cols')
        if cols is not None and (form != 'stagger' or not (isinstance(cols, int) and not isinstance(cols, bool) and cols in (2, 3))): err('IL020', where, 'cols belongs to the staggered form and is 2 or 3')
        feature = entry.get('feature')
        if feature is not None and (form != 'bento' or not (isinstance(feature, int) and not isinstance(feature, bool) and 0 <= feature < len(items))): err('IL020', where, f'feature belongs to the bento and is the position of one of its {len(items)} items, 0 first')
        if form == 'bento' and len(items) < 3: err('IL021', where, f'a bento needs three items or more; this list has {len(items)}')
        if form == 'stagger' and content['kind'] == 'numbers': err('IL021', where, 'figures stepped against each other read as unfinished: a ledger, or tiles with the figure that matters most large')
        if form == 'bento' and head != 'top': err('IL021', where, 'a bento takes the whole width: its heading sits on top')
        if head == 'sticky' and len(items) < 4: err('IL021', where, f'a heading that stays while the list scrolls needs a list long enough to scroll past: four items or more, this one has {len(items)}')
        if form == 'stagger' and head != 'top' and entry.get('cols', 2) == 3: err('IL021', where, 'three staggered columns need the whole width: put the heading on top or use two columns')
        if numerals == 'none' and not numbering(items):
            err('IL022', where, 'the tags of this list are facts (' + ', '.join(repr(i['tag']) for i in items if i['tag'])[:80] + '), not numbering: they cannot be hidden')
    return errors


def render_section(sec, content, entry):
    """The <section> for one validated list entry: the section's own id, band and heading block, its items in their order."""
    form, head, numerals = entry['form'], entry.get('head', 'top'), entry.get('numerals', 'big')
    items = content['items']; feature = entry.get('feature', 0) if form == 'bento' else None
    spans = _spans(len(items), feature) if form == 'bento' else None
    out = []
    for i, item in enumerate(items):
        style = f' style="--span:{spans[i][0]};--rows:{spans[i][1]}"' if spans else ''
        hidden = numerals == 'none' or not item['tag']
        tag = '' if hidden else f'<span class="lc-tag">{e(item["tag"])}</span>'
        picture = f'<figure><img src="{e(item["picture"]["src"])}" alt="{e(item["picture"].get("alt", ""))}"></figure>' if item.get('picture') else ''
        link = f'<a class="link" href="{e(item["link"]["href"])}">{e(item["link"]["label"])}</a>' if item.get('link') else ''
        body = f'<p>{e(item["body"])}</p>' if item['body'] else ''
        out.append(f'<li class="lc-item{" lc-feature" if i == feature else ""}"{style}>{picture}{tag}<h3 class="h3 lc-title">{e(item["title"])}</h3>{body}{link}</li>')
    kept = [c for c in content['classes'] if c not in ('lc',) and not c.startswith('lc-')]
    classes = ' '.join(kept + ['lc', f'lc-{form}'])
    cols = f' style="--n:{entry.get("cols", 2)}"' if form == 'stagger' else ''
    return (f'<section class="{e(classes)}" id="{e(sec["id"])}" data-lc="{V.VERSION}"><div class="wrap lc-wrap lc-head-{head}">'
            f'<div class="lc-head">{content["head"]}</div>'
            f'<ol class="lc-list lc-n-{numerals} lc-t-{entry.get("title", "md")}{" lc-ordinal" if numbering(items) else ""}"{cols} data-move="stagger-in">{"".join(out)}</ol>'
            f'{content["tail"]}</section>')   # the tail closes the wrap and carries whatever else the section holds: its buttons, its links to the source


def transplant(page_html, doc):
    """Draw every list of the document in place of its section. Validated first against the page itself; a document
    that fails leaves the page untouched and says why."""
    errors = validate(doc, page_html)
    if errors: return page_html, {'drawn': False, 'errors': errors, 'sections': []}
    page = _read(page_html); out = page_html; done = []
    for entry in sorted(doc['lists'], key=lambda x: -page[x['section']][0]['span'][0]):   # from the bottom up: earlier spans stay true
        sec, content = page[entry['section']]; start, end = sec['span']
        out = out[:start] + render_section(sec, content, entry) + out[end:]; done.append(entry['section'])
    if 'id="lc-css"' not in out:
        head = out.find('</head>')
        if head < 0: return page_html, {'drawn': False, 'errors': [{'code': 'IL000', 'at': 'page', 'message': 'the page has no </head> to carry the list stylesheet'}], 'sections': []}
        out = out[:head] + f'<style id="lc-css">{CSS}</style>' + out[head:]
    return out, {'drawn': True, 'errors': [], 'sections': sorted(done)}


if __name__ == '__main__':
    if len(sys.argv) != 4: raise SystemExit(__doc__)
    with open(sys.argv[1]) as f: document = json.load(f)
    with open(sys.argv[2], encoding='utf-8') as f: page_html = f.read()
    result, report = transplant(page_html, document)
    with open(sys.argv[3], 'w', encoding='utf-8') as f: f.write(result)
    for problem in report['errors']: print(f"{problem['code']} {problem['at']}: {problem['message']}")
    print(json.dumps({'drawn': report['drawn'], 'sections': report['sections']}))
    raise SystemExit(0 if report['drawn'] else 1)
