"""words.py — a section that is words only, drawn so that it is not one more grey block of text.

A page without photographs is mostly these: a price ledger, a menu, opening hours, a paragraph under its heading. The
production renderer draws each the same way — the heading in a narrow column, the rows beside it — and five of them in
a row is what makes such a page read as a form. A words composition names such sections and gives each a form of its
own: the heading as a poster across the width with what it introduces set under it to one side; the rows in two
columns like a printed menu; a short section as a centred statement — and, on any of them, a ground of colour that
breaks the run. Like every composition it cannot say anything: the heading block and what it introduces come from the
page through lib/compose/sections.py, byte for byte, and the section keeps its id and everything after its words.

  validate(doc, page_html)   → [{'code', 'at', 'message'}]        ([] = may be drawn)
  transplant(page_html, doc) → (page_html, {'drawn', 'errors', 'sections'})
  readable(page_html)        → {section id: (section record, content | reason)} for the sections of words of the page
  a document: {"ir": "0.2", "words": [{"section": id, "form": poster|columns|statement, "title": md|lg|xl,
               "ground": band|accent|ink|alt, "side": left|right}]}
Deterministic, no network, no model. A document that fails is refused whole and the page comes back untouched."""
import html as H, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import content as CONTENT
import pictures as PICTURES
import sections as SECTIONS
import validate as V

e = lambda s: H.escape(str(s if s is not None else ''), quote=True)
FORMS = ('poster', 'columns', 'statement')
GROUNDS = ('band', 'accent', 'ink', 'alt')   # band: the section's own ground
TITLES = PICTURES.TITLES
SIDES = ('left', 'right')
KEYS = {'section', 'form', 'title', 'ground', 'side'}
COLUMN_ROWS = 4          # fewer rows than this do not fill two columns
STATEMENT_CHARS = 280    # a statement is short: more than this is a section to read, not a line to take in
STATEMENT_ROWS = 2

CSS = """
.sec.wc .wc-wrap{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));column-gap:var(--gutter,32px);row-gap:clamp(24px,3.5vw,56px);align-items:start}
.sec.wc .wc-head,.sec.wc .wc-body{grid-column:1/-1;min-width:0;padding:0;margin:0;overflow-wrap:break-word}
.sec.wc .wc-body .rows li b{flex-shrink:0;max-width:100%;overflow-wrap:break-word}
.sec.wc .wc-head .h2{text-wrap:balance;overflow-wrap:normal;margin-top:14px}.sec.wc .wc-head .lede,.sec.wc .wc-head .cap{margin-top:clamp(14px,1.6vw,24px);max-width:48ch}
.sec.wc.wc-t-md .wc-head .h2{font-size:min(calc(clamp(28px,3.2vw,46px) * var(--face-grow,1)),calc((100vw - 48px) / var(--lw,8) * 1.72))!important;line-height:1.06}
.sec.wc.wc-t-lg .wc-head .h2{font-size:min(calc(clamp(34px,4.4vw,64px) * var(--face-grow,1)),calc((100vw - 48px) / var(--lw,8) * 1.72))!important;line-height:1.02}
.sec.wc.wc-t-xl .wc-head .h2{font-size:min(calc(clamp(40px,6.2vw,96px) * var(--face-grow,1)),calc((100vw - 48px) / var(--lw,8) * 1.72))!important;line-height:.98;letter-spacing:var(--h1-ls,-.03em)}
.sec.wc .wc-body>:first-child{margin-top:0}
.sec.wc.wc-f-poster .wc-body{grid-column:6/-1;border-top:1px solid var(--line);padding-top:clamp(18px,2vw,28px)}.sec.wc.wc-f-poster.wc-side-left .wc-body{grid-column:1/8}
.sec.wc.wc-f-columns .wc-body ul,.sec.wc.wc-f-columns .wc-body ol{display:block;column-count:2;column-gap:clamp(32px,6vw,96px)}.sec.wc.wc-f-columns .wc-body li{break-inside:avoid}
.sec.wc.wc-f-statement .wc-head,.sec.wc.wc-f-statement .wc-body{grid-column:3/11;text-align:center}
.sec.wc.wc-f-statement .wc-head>*,.sec.wc.wc-f-statement .wc-body>*{margin-left:auto;margin-right:auto}.sec.wc.wc-f-statement .ctas{justify-content:center}.sec.wc.wc-f-statement .h2{text-align:center!important}
.sec.wc.wc-g-accent{background:var(--accent);color:var(--on-accent,var(--paper))}.sec.wc.wc-g-ink{background:var(--ink);color:var(--paper)}.sec.wc.wc-g-alt{background:color-mix(in srgb,var(--ink) 7%,var(--paper));color:var(--ink)}
.sec.wc.wc-grounded{--line:color-mix(in srgb,currentColor 26%,transparent);--muted:currentColor}
.sec.wc.wc-grounded .h2,.sec.wc.wc-grounded .lab,.sec.wc.wc-grounded .lede,.sec.wc.wc-grounded .cap,.sec.wc.wc-grounded p,.sec.wc.wc-grounded li,.sec.wc.wc-grounded li *{color:inherit}
.sec.wc.wc-grounded .wc-wrap a:not(.btn){color:inherit}
.sec.wc.wc-g-accent .btn{background:var(--on-accent,var(--paper));color:var(--accent);border-color:var(--on-accent,var(--paper))}.sec.wc.wc-g-ink .btn{background:var(--paper);color:var(--ink);border-color:var(--paper)}
.sec.wc.wc-g-alt .btn{background:var(--ink);color:var(--paper);border-color:var(--ink)}.sec.wc.wc-grounded .btn.ghost{background:transparent;color:inherit;border-color:currentColor}
@media(max-width:900px){
.sec.wc .wc-wrap{display:block}.sec.wc .wc-body{margin-top:24px}
.sec.wc.wc-f-columns .wc-body ul,.sec.wc.wc-f-columns .wc-body ol{column-count:1}
}
"""


def readable(page_html):
    """{section id: (section record, content or the reason it cannot be read)} for the sections of the page that are
    neither a list nor a picture section: the ones that are words only, and why the others are not."""
    found = {}
    for sec in SECTIONS.sections(page_html)[1:]:
        if sec['kind'] or not sec['id']: continue
        try: found[sec['id']] = (sec, SECTIONS.from_words(page_html[sec['span'][0]:sec['span'][1]]))
        except ValueError as err: found[sec['id']] = (sec, str(err))
    return found


def room(entry, page):
    """The width in CSS px the heading has at a 1440 screen in this form."""
    inner = min(1440, page.get('container', 1300)) - 2 * page.get('frame', 40)
    return inner * 8 / 12 if entry.get('form') == 'statement' else inner


def validate(doc, page_html):
    errors = []
    def err(code, at, message): errors.append({'code': code, 'at': at, 'message': message})
    if not isinstance(doc, dict) or doc.get('ir') not in V.ACCEPTED or not isinstance(doc.get('words'), list) or not doc['words'] or len(doc['words']) > 12 or set(doc) - {'ir', 'words', 'note'}:
        err('IW001', 'ir', f'a words composition is {{"ir": "{V.VERSION}", "words": [1–12 objects]}}'); return errors
    page = readable(page_html); tokens = CONTENT.page_of(page_html); named = []
    for i, entry in enumerate(doc['words']):
        where = f'words[{i}]'
        if not isinstance(entry, dict): err('IW001', where, 'each entry is an object'); continue
        extra = set(entry) - KEYS
        if extra:   # as everywhere in a composition: a field that could carry words does not exist
            err('IW011' if extra & {'text', 'content', 'html', 'label', 'href', 'value', 'heading', 'rows', 'body', 'items'} else 'IW001', where, f'unknown fields {sorted(extra)}: a composition places what the page says, it does not contain it')
        sid = entry.get('section'); where = f'words[{sid}]' if isinstance(sid, str) else where
        if not isinstance(sid, str) or sid not in page: err('IW010', where, f'no section of words "{sid}" on this page; they are {sorted(k for k, v in page.items() if not isinstance(v[1], str))}'); continue
        if sid in named: err('IW010', where, f'section "{sid}" is named twice')
        named.append(sid)
        _, content = page[sid]
        if isinstance(content, str): err('IW010', where, f'section "{sid}" cannot be recomposed: {content}'); continue
        form = entry.get('form'); before = len(errors)
        if form not in FORMS: err('IW020', where, f'form is one of {FORMS}')
        if entry.get('title', 'lg') not in TITLES: err('IW020', where, f'title is one of {TITLES}')
        if entry.get('ground', 'band') not in GROUNDS: err('IW020', where, f'ground is one of {GROUNDS} (band: the section\'s own)')
        if 'side' in entry and (form != 'poster' or entry['side'] not in SIDES): err('IW020', where, f'side belongs to the poster and is one of {SIDES}: where what the heading introduces is set under it')
        if len(errors) > before: continue
        if form == 'columns' and content['rows'] < COLUMN_ROWS: err('IW021', where, f'two columns want rows to fill them: this section has {content["rows"]}, a column takes at least {COLUMN_ROWS // 2}')
        if form == 'statement' and (content['chars'] > STATEMENT_CHARS or content['rows'] > STATEMENT_ROWS):
            err('IW021', where, f'a statement is short — up to {STATEMENT_CHARS} characters and {STATEMENT_ROWS} rows; this section says {content["chars"]} characters in {content["rows"]} rows: poster or columns')
        if entry.get('ground', 'band') != 'band' and content['band'] == {'accent': 'accent', 'ink': 'dark', 'alt': 'alt'}[entry['ground']]: err('IW021', where, f'this section already stands on that ground: "ground" changes it, or stays "band"')
        why = PICTURES._heading_fits({'form': 'words', 'title': entry.get('title', 'lg')}, {'words': {'heading': content['heading']}}, tokens, room(entry, tokens))
        if why: err('IW044', where, why)
    return errors


def render_section(sec, content, entry):
    """The <section> for one validated entry: the section's own id and classes, its heading block and what the heading
    introduces, each verbatim, and everything it held after them."""
    form = entry['form']; ground = entry.get('ground', 'band')
    kept = [c for c in content['classes'] if c != 'wc' and not c.startswith('wc-') and not (ground != 'band' and c.startswith('band-'))]   # a new ground replaces the band it stood on
    classes = kept + ['wc', 'wc-f-' + form, 'wc-t-' + entry.get('title', 'lg')] + ([f'wc-g-{ground}', 'wc-grounded'] if ground != 'band' else []) + (['wc-side-' + entry['side']] if entry.get('side') else [])
    holder = ''.join(' ' + c for c in content['holder'] if not c.startswith('wc-'))
    return (f'<section class="{e(" ".join(classes))}" id="{e(sec["id"])}" data-wc="{V.VERSION}" data-form="{form}"><div class="wrap wc-wrap">'
            f'<div class="wc-head{e(holder)}">{content["head"]}</div><div class="wc-body{e(holder)}" data-move="fade-rise">{content["body"]}</div></div>{content["tail"]}</section>')


def transplant(page_html, doc):
    """Draw every section of the document in place of the template's. Validated first against the page itself; a document
    that fails leaves the page untouched and says why."""
    errors = validate(doc, page_html)
    if errors: return page_html, {'drawn': False, 'errors': errors, 'sections': []}
    page = readable(page_html); out = page_html; done = []
    for entry in sorted(doc['words'], key=lambda x: -page[x['section']][0]['span'][0]):   # from the bottom up: earlier spans stay true
        sec, content = page[entry['section']]; start, end = sec['span']
        out = out[:start] + render_section(sec, content, entry) + out[end:]; done.append(entry['section'])
    if 'id="wc-css"' not in out:
        head = out.find('</head>')
        if head < 0: return page_html, {'drawn': False, 'errors': [{'code': 'IW000', 'at': 'page', 'message': 'the page has no </head> to carry the stylesheet'}], 'sections': []}
        out = out[:head] + f'<style id="wc-css">{CSS}</style>' + out[head:]
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
