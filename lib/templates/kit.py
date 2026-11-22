"""kit.py — the design a client takes away: the page of the package, taken apart into parts they can build with.

    parts(page) -> {'lang', 'html_attrs', 'tokens', 'css', 'js', 'body_attrs', 'wrap', 'sections': [{'name', 'html', 'inside'}]}
    kit(page, measured=None, name='') -> {path: bytes}     the files of design/, to stand beside index.html in the package
    python3 lib/templates/kit.py <unpacked package folder> [measured.json]     writes <folder>/design/

Owner's direction, 2026-11-19: the client downloads a design to build their own site in; the ready page is one thing
inside it. package.build() puts these files in every package beside index.html.

The kit is read from the package's own index.html — the page that was compared with the preview — and from nothing
else, so it works for every template without a line in any of them:

    design/tokens.css        the page's variables (colours and whatever else the template set on <html>), one a line
    design/design.css        every rule of the page, its typefaces first (pointing at ../fonts/)
    design/design.js         the page's script, when it has one
    design/sections/NN-name.html   each part of the page on its own: a whole document that links the three files above
    design/page.html         the page put together again from those parts and only from them
    design/DESIGN.md         the look in words and numbers, for the person and for the AI tool they build with

Two promises, both measured and neither assumed:
    1. page.html looks like the preview, screen by screen (the parts lose nothing) — lib/qa/package_compare.mjs holds
       every package to it before delivery: a kit whose page differs refuses the package;
    2. each section on its own looks like its place in the page (a part can be taken without the page round it) —
       lib/qa/kit_compare.mjs reports it section by section; one that does not hold alone is named. Not a gate.

No model call, no network, no browser: text in, text out. `measured` (what kit_compare.mjs --measure read in a browser:
the sizes, faces, radii and widths the page actually sets) only makes DESIGN.md richer; without it the file still holds
the tokens, the faces and the rules.
"""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
SKIP = {'script', 'style', 'template', 'noscript', 'link', 'meta'}
WRAPS = {'main'}
_REL = re.compile(r'^(?![a-z][a-z0-9+.-]*:|//|#|/|\?)', re.I)          # an address relative to the page's own folder


class KitError(Exception):
    """A page the kit cannot be taken from: no body, or nothing in it to take."""


class _Outline(HTMLParser):
    """where every element of <body> starts and ends, as offsets into the page"""

    def __init__(self, page):
        super().__init__(convert_charrefs=False)
        self.page, self.lines, self.stack, self.tree, self.body = page, [0], [], [], None
        for m in re.finditer(r'\n', page):
            self.lines.append(m.end())
        self.feed(page)
        self.close()

    def _at(self):
        line, col = self.getpos()
        return self.lines[line - 1] + col

    def _node(self, tag, attrs, start, end=None):
        node = {'tag': tag, 'attrs': dict(attrs), 'start': start, 'end': end, 'open_end': start + len(self.get_starttag_text() or ''), 'kids': []}
        (self.stack[-1]['kids'] if self.stack else self.tree).append(node)
        if tag == 'body':
            self.body = node
        return node

    def handle_starttag(self, tag, attrs):
        start = self._at()
        if tag in VOID:
            self._node(tag, attrs, start, start + len(self.get_starttag_text() or ''))
            return
        self.stack.append(self._node(tag, attrs, start))

    def handle_startendtag(self, tag, attrs):
        start = self._at()
        self._node(tag, attrs, start, start + len(self.get_starttag_text() or ''))

    def handle_endtag(self, tag):
        if not any(n['tag'] == tag for n in self.stack):
            return
        at = self._at()
        end = self.page.find('>', at) + 1
        while self.stack:
            n = self.stack.pop()
            n['end'] = end if n['tag'] == tag else at          # an element left open ends where its parent does
            n['close_start'] = at
            if n['tag'] == tag:
                break

    def close(self):
        super().close()
        for n in self.stack:
            n['end'] = n['close_start'] = len(self.page)
        self.stack = []


def _attrs_text(page, node):
    """the attributes of an element as the page wrote them"""
    m = re.match(r'<[^\s>/]+(.*?)/?>$', page[node['start']:node['open_end']], re.S)
    return (m.group(1) if m else '').strip()


def _name(node, seen):
    a = node['attrs']
    base = (a.get('id') or (a.get('class') or '').split(' ')[0] or node['tag'] or 'part').lower()
    base = re.sub(r'[^a-z0-9]+', '-', base).strip('-')[:24] or 'part'
    n, k = base, 2
    while n in seen:
        n, k = '%s-%d' % (base, k), k + 1
    seen.add(n)
    return n


def rebase(markup, prefix):
    """every address in `markup` that is relative to the page's folder, written from `prefix` folders further in"""
    if not prefix:
        return markup
    one = lambda u: prefix + u if u and _REL.match(u) else u

    def attr(m):
        name, q, val = m.group(1), m.group(2), m.group(3)
        if name.lower() in ('srcset', 'imagesrcset', 'data-srcset'):
            val = ', '.join(' '.join([one(p.split()[0])] + p.split()[1:]) for p in (x.strip() for x in val.split(',')) if p)
        elif name.lower() == 'style':
            val = _css_urls(val, prefix)
        elif name.lower() == 'href' and not re.search(r'\.(?:jpe?g|png|webp|avif|gif|svg|mp4|webm|mov|woff2?|css|js|pdf)(?:[?#]|$)', val, re.I):
            return m.group(0)                                   # a link to a page of the client's own is left as written
        else:
            val = one(val)
        return '%s=%s%s%s' % (name, q, val, q)
    return re.sub(r'\b(src|poster|href|srcset|imagesrcset|data-src|data-srcset|data-poster|data-bg|style)=(["\'])(.*?)\2', attr, markup, flags=re.S | re.I)


def _css_urls(css, prefix):
    def u(m):
        q, val = m.group(1), m.group(2).strip()
        return 'url(%s%s%s)' % (q, prefix + val if _REL.match(val) and not val.startswith('data:') else val, q)
    return re.sub(r'url\(\s*(["\']?)([^)"\']+)\1\s*\)', u, css)


def parts(page):
    o = _Outline(page)
    if not o.body:
        raise KitError('the page has no body')
    html_node = next((n for n in o.tree if n['tag'] == 'html'), None)
    html_attrs = dict(html_node['attrs']) if html_node else {}
    tokens = []
    for decl in (html_attrs.get('style') or '').split(';'):
        k, _, v = decl.partition(':')
        if k.strip().startswith('--') and v.strip():
            tokens.append((k.strip(), v.strip()))
    rest_style = ';'.join(d.strip() for d in (html_attrs.get('style') or '').split(';') if d.strip() and not d.strip().startswith('--'))
    css = [m.group(2) for m in re.finditer(r'<style\b([^>]*)>(.*?)</style>', page, re.S | re.I)]
    scripts, outside_js, early = [], [], []
    for m in re.finditer(r'<script\b([^>]*)>(.*?)</script>', page, re.S | re.I):
        if 'data-sw-tablet' in m.group(1):                             # sets the page's size before anything is drawn (tablet.py): it stays first in <body>
            early.append(m.group(0))
        elif re.search(r'\bsrc=', m.group(1), re.I):
            outside_js.append(m.group(1).strip())
        elif not re.search(r'type=["\']?application/(?:ld\+)?json', m.group(1), re.I) and m.group(2).strip():
            scripts.append(m.group(2))
    head = page[:o.body['start']]
    links = re.findall(r'<link\b[^>]*\brel=["\']?(?:stylesheet|preconnect)\b[^>]*>', head, re.I)        # a page that still loads its faces from outside keeps those lines
    seen, sections, wrap = set(), [], None
    for kid in o.body['kids']:
        if kid['tag'] in SKIP:
            continue
        if kid['tag'] in WRAPS and any(k['tag'] not in SKIP for k in kid['kids']):
            wrap = {'tag': kid['tag'], 'attrs': _attrs_text(page, kid)}
            for k in kid['kids']:
                if k['tag'] not in SKIP:
                    sections.append({'name': _name(k, seen), 'html': page[k['start']:k['end']], 'inside': True})
        else:
            sections.append({'name': _name(kid, seen), 'html': page[kid['start']:kid['end']], 'inside': False})
    if not sections:
        raise KitError('the body holds nothing to take')
    return {'lang': html_attrs.get('lang') or 'en', 'html_style': rest_style, 'html_class': html_attrs.get('class') or '', 'tokens': tokens, 'css': css, 'js': scripts,
            'outside_js': outside_js, 'links': links, 'early': early, 'body_attrs': _attrs_text(page, o.body), 'wrap': wrap, 'sections': sections}


def _doc(p, chosen, up, title):
    """a whole document made of the kit's files and the sections given, `up` folders below design/"""
    back = '../' * up
    out, open_wrap = [], False
    for s in chosen:
        if p['wrap'] and s['inside'] and not open_wrap:
            out.append('<%s%s>' % (p['wrap']['tag'], (' ' + p['wrap']['attrs']) if p['wrap']['attrs'] else ''))
            open_wrap = True
        if open_wrap and not s['inside']:
            out.append('</%s>' % p['wrap']['tag'])
            open_wrap = False
        out.append(rebase(s['html'], back + '../'))
    if open_wrap:
        out.append('</%s>' % p['wrap']['tag'])
    html_bits = ' lang="%s"' % p['lang'] + (' class="%s"' % p['html_class'] if p['html_class'] else '') + (' style="%s"' % p['html_style'] if p['html_style'] else '')
    return ('<!doctype html>\n<html%s>\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n<title>%s</title>\n'
            '%s<link rel="stylesheet" href="%sdesign.css">\n<link rel="stylesheet" href="%stokens.css">\n</head>\n<body%s>%s\n%s\n%s</body>\n</html>\n') % (
        html_bits, title, ''.join(l + '\n' for l in p.get('links') or []), back, back, (' ' + p['body_attrs']) if p['body_attrs'] else '', ''.join(p.get('early') or []), '\n'.join(out),
        ('<script src="%sdesign.js"></script>\n' % back) if p['js'] else '')


def _faces(css):
    """the typefaces the page loads (its @font-face families) and the stacks its rules name, most used first"""
    loaded = list(dict.fromkeys(m.strip(' "\'') for m in re.findall(r'@font-face\s*{[^}]*?font-family\s*:\s*([^;}]+)', css, re.I)))
    stacks = {}
    for m in re.findall(r'font-family\s*:\s*([^;}]+)', re.sub(r'@font-face\s*{[^}]*}', '', css), re.I):
        k = ' '.join(m.split())
        stacks[k] = stacks.get(k, 0) + 1
    for m in re.findall(r'\bfont\s*:\s*[^;}]*?\d[\w.%]*(?:/[\w.%]+)?\s+([^;}]+)', css):
        k = ' '.join(m.split())
        stacks[k] = stacks.get(k, 0) + 1
    return loaded, sorted(stacks, key=lambda k: -stacks[k])


_USE = (('background', 'grounds'), ('color', 'text'), ('border', 'lines'), ('outline', 'lines'), ('shadow', 'shadows'), ('fill', 'drawings'), ('stroke', 'drawings'),
        ('gradient', 'grounds'), ('decoration', 'underlines'), ('caret', 'text'))


def token_use(css, token):
    """what a variable is used for, read off the rules that name it: 'text (14), grounds (6)' — counted, not guessed"""
    seen = {}
    for prop, val in re.findall(r'([a-z-]+)\s*:\s*([^;{}]*var\(\s*%s\b[^;{}]*)' % re.escape(token), css):
        if prop.startswith('--'):
            continue
        word = next((w for k, w in _USE if k in prop or (k == 'gradient' and 'gradient' in val)), None) or prop
        seen[word] = seen.get(word, 0) + 1
    return ', '.join('%s (%d)' % (k, n) for k, n in sorted(seen.items(), key=lambda kv: -kv[1])[:3])


def design_md(p, name, measured=None):
    css = '\n'.join(p['css'])
    loaded, stacks = _faces(css)
    m = measured or {}
    L = ['# %s — the design' % (name or 'Your site'), '',
         'This folder is the look of your page, taken apart so you can build the rest of your site in it. The finished',
         'page is `../index.html`; everything here is what that page is made of, and nothing else.', '',
         '## What is here', '',
         '| File | What it is |', '|---|---|',
         '| `tokens.css` | The colours and other values the whole design hangs on. Change one here and it changes everywhere. |',
         '| `design.css` | Every style of the page, typefaces included. Link it on every page you build. |']
    if p['js']:
        L.append('| `design.js` | The page\'s movement and behaviour. Link it at the end of `<body>`. |')
    L += ['| `sections/` | Each part of the page as its own file: open one, copy the part you need. |',
          '| `page.html` | The whole page put together from those parts: the starting point for a new page. |', '',
          '## Start a new page', '',
          '1. Copy `page.html` and give it the new page\'s name.',
          '2. Delete the sections the new page does not need; keep the first and the last (the top bar and the foot).',
          '3. Change the words and pictures inside the sections you kept. Leave the class names as they are: the look hangs on them.',
          '4. For a part the page does not have yet, start from the nearest section in `sections/` rather than from nothing.', '',
          '## The sections', '', '| File | Part |', '|---|---|']
    for i, s in enumerate(p['sections'], 1):
        head = re.search(r'<h[1-3]\b[^>]*>(.*?)</h[1-3]>', s['html'], re.S | re.I)
        said = ' '.join(re.sub(r'<[^>]+>', ' ', head.group(1)).split())[:70] if head else ''
        L.append('| `sections/%02d-%s.html` | %s |' % (i, s['name'], said or '—'))
    L += ['', '## Tokens', '']
    if p['tokens']:
        L += ['| Name | Value | Where the design uses it |', '|---|---|---|'] + ['| `%s` | `%s` | %s |' % (k, v.replace('|', '\\|'), token_use(css, k) or 'not used by a rule') for k, v in p['tokens']]
    else:
        L.append('This design sets no variables on the page; its values stand in `design.css`.')
    L += ['', '## Typefaces', '']
    if loaded:
        L.append('Loaded from `../fonts/`: ' + ', '.join('**%s**' % f for f in loaded) + '.')
    if stacks:
        L += ['', 'Stacks the styles name, most used first:', ''] + ['- `%s`' % s for s in stacks[:4]]
    if m.get('type'):
        L += ['', '## Type as it is set (measured at 1440 px wide)', '', '| What it is | Set on | Face | Size | Weight | Line height | Tracking | Example |', '|---|---|---|---|---|---|---|---|']
        for t in m['type']:
            L.append('| %s | `%s` | %s | %s px | %s | %s | %s | %s |' % (t.get('role'), t.get('on') or '', t.get('family'), t.get('size'), t.get('weight'), t.get('line'), t.get('tracking'), (t.get('example') or '').replace('|', ' ')[:48]))
    if m.get('radii'):
        L += ['', '## Corners', '', 'The radii the page uses, most used first: ' + ', '.join('`%s` (%d×)' % (r['value'], r['count']) for r in m['radii'][:6]) + '.']
    if (m.get('width') or {}).get('content'):
        L += ['', '## Measure', '', 'At 1440 px the content runs %s px wide.' % m['width'].get('content')]
    sizes = len({t.get('size') for t in m.get('type') or []})
    L += ['', '## Rules that keep it looking like this', '',
          '- Colours come from `tokens.css` and nowhere else. A new colour is a new token, decided once, not a value typed into a page.',
          '- ' + ('The page sets type in %d sizes. A new heading or paragraph takes one of them.' % sizes if sizes else 'A new heading or paragraph takes a size the page already uses.'),
          '- ' + ('Typefaces: %s. No third one.' % ' and '.join(loaded[:2]) if loaded else 'No typeface beyond the ones `design.css` names.'),
          '- Corners, shadows and borders are the ones in `design.css`. Do not round, shade or outline a new block by eye.',
          '- Spacing between sections is the sections\' own. Do not add margins round a section to "give it air".',
          '- A new part is built from the classes of an existing one. If nothing fits, say so and decide the new part once, in `design.css`.', '',
          '## For the AI tool you build with', '',
          'Paste this to Cursor, Claude Code or whichever tool writes your pages:', '',
          '> This site has a finished design in the `design/` folder. Read `design/DESIGN.md`, `design/tokens.css` and the files in',
          '> `design/sections/` before you write anything. Build every page from those sections and the classes in',
          '> `design/design.css`. Do not add colours, typefaces, font sizes, radii, shadows or gradients that are not already',
          '> there, and do not restyle existing classes. If a page needs a part the design does not have, stop and show me',
          '> the nearest existing section and what you would change in it.', '']
    return '\n'.join(L)


def kit(page, measured=None, name=''):
    p = parts(page)
    css = _css_urls('\n'.join(p['css']), '../')
    files = {'design/design.css': css.strip() + '\n',
             'design/tokens.css': '/* the values the design hangs on: change one here and it changes on every page that links this file */\n:root{\n'
                                  + ''.join('  %s: %s;\n' % kv for kv in p['tokens']) + '}\n'}
    if p['js']:
        files['design/design.js'] = '\n;\n'.join(s.strip() for s in p['js']) + '\n'
    for i, s in enumerate(p['sections'], 1):
        files['design/sections/%02d-%s.html' % (i, s['name'])] = _doc(p, [s], 1, '%s — %s' % (name or 'Design', s['name']))
    files['design/page.html'] = _doc(p, p['sections'], 0, name or 'New page')
    files['design/DESIGN.md'] = design_md(p, name, measured)
    files['design/kit.json'] = json.dumps({'sections': ['%02d-%s' % (i, s['name']) for i, s in enumerate(p['sections'], 1)], 'tokens': len(p['tokens']),
                                            'script': bool(p['js']), 'outside_scripts': p['outside_js']}, indent=1) + '\n'
    return {k: v.encode('utf-8') for k, v in files.items()}


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('usage: python3 lib/templates/kit.py <unpacked package folder> [measured.json]')
    folder = Path(sys.argv[1])
    measured = json.loads(Path(sys.argv[2]).read_text(encoding='utf-8')) if len(sys.argv) > 2 else None
    data = json.loads((folder / 'data.json').read_text(encoding='utf-8')) if (folder / 'data.json').is_file() else {}
    made = kit((folder / 'index.html').read_text(encoding='utf-8'), measured, (data.get('brand') or {}).get('name') or '')
    for rel, body in made.items():
        f = folder / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(body)
    print(json.dumps({'files': sorted(made), 'bytes': sum(len(b) for b in made.values())}))
