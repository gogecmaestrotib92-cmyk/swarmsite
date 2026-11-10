"""sections.py — what a list section says, by address, read off the page the production renderer built.

Below the first screen most of a page is lists: an index of features, a row of cards. The production renderer draws
each in the one form its blueprint has. A list composition (lib/compose/lists.py) draws the same items in another form;
like a hero composition it places what is there and cannot change it. This file reads what is there:

  sections(page_html)            → [{'id', 'classes', 'kind', 'span': (start, end)}] for every <section> after the hero
  from_section(section_html)     → {'kind': 'indexlist'|'cards', 'band', 'head': HTML of the section's own heading block,
                                    'items': [{'tag', 'title', 'body', 'picture': {'src', 'alt'} | None, 'link': {'href', 'label'} | None}],
                                    'tail': HTML of everything the section holds after its list (its own buttons, its links to the source), verbatim}
  from_picture(section_html)     → {'kind': 'picture', 'band', 'classes', 'words': {'html', 'classes', 'chars', 'rows', 'heading': its h2 as plain text},
                                    'picture': {'src', 'alt'}, 'first': 'words'|'picture', 'tail'}
                                   a section that is its words and one picture side by side: the words block verbatim, the
                                   picture, and everything the section holds after them (lib/compose/pictures.py draws it)
A section this file cannot read whole (an item with markup it does not know) is refused with ValueError: a composition
never draws a list it could not read completely. Deterministic, no network, no model."""
import html as H, re
from html.parser import HTMLParser

LIST_KINDS = ('indexlist', 'cards', 'ladder', 'numbers', 'faq')   # an index, a row of cards, steps, figures, questions: each is a heading block and items
SAFE_URL = re.compile(r'^(https?://|mailto:|tel:|#)', re.I)
VOID = ('img', 'br', 'source', 'hr', 'input', 'meta', 'link')


def sections(page_html):
    """Every top-level <section class="sec …"> of the page with its id, classes and span; the hero is the first."""
    out, depth, open_at = [], 0, None
    for tag in re.finditer(r'<section\b[^>]*>|</section>', page_html):
        if tag.group(0) != '</section>':
            if depth == 0: open_at = tag
            depth += 1
        else:
            depth -= 1
            if depth == 0 and open_at is not None:
                classes = (re.search(r'class="([^"]*)"', open_at.group(0)) or [None, ''])[1].split()
                sid = (re.search(r'\bid="([^"]*)"', open_at.group(0)) or [None, None])[1]
                if 'sec' in classes:
                    out.append({'id': sid, 'classes': classes, 'kind': next((k for k in LIST_KINDS if k in classes), None), 'span': (open_at.start(), tag.end())})
                open_at = None
    return out


class _List(HTMLParser):
    """Reads an index list, a row of cards, steps, figures or questions: each item's tag (a number, a label or a figure),
    title, body, picture and link. `loose`: the items are the list's direct children, whatever they are called."""
    def __init__(self, loose=False):
        super().__init__(convert_charrefs=True); self.loose = loose
        self.items = []; self.item = None; self.field = None; self.depth = 0; self.item_depth = None; self.link = None; self.unknown = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs); classes = (a.get('class') or '').split()
        if tag not in VOID: self.depth += 1
        if self.item is None:
            if (tag == 'li' and (set(classes) & {'index-row', 'ladder-step'})) or (tag in ('div', 'a', 'article') and 'card' in classes) or tag == 'details' or (self.loose and tag == 'div' and self.depth == 2):
                self.item = {'tag': '', 'title': '', 'body': '', 'picture': None, 'link': None}; self.item_depth = self.depth
                if tag == 'a' and SAFE_URL.match(a.get('href') or ''): self.item['link'] = {'href': a['href'], 'label': ''}
            return
        if tag == 'br' and self.field: self.item[self.field] += ' '   # a line break separates words
        if tag == 'img':
            if self.item['picture'] is None and (a.get('src') or '').startswith('data:image/'): self.item['picture'] = {'src': a['src'], 'alt': a.get('alt') or ''}
        elif tag in ('h3', 'summary'): self.field = 'title'
        elif tag == 'p' and 'num-label' in classes and not self.item['title']: self.field = 'title'   # a figure's label is what it is called
        elif tag == 'p': self.field = 'body' if not self.item['body'] else 'more'
        elif tag in ('span', 'b') and (set(classes) & {'idx', 'num', 'lab', 'ladder-n'}) and self.field is None: self.field = 'tag'
        elif tag == 'a' and SAFE_URL.match(a.get('href') or '') and self.item['link'] is None: self.link = {'href': a['href'], 'label': ''}
        elif tag in ('figure', 'div', 'span', 'em', 'strong', 'b', 'i', 'br', 'small', 'a'): pass
        else: self.unknown.append(tag)

    def handle_endtag(self, tag):
        if tag in VOID: return
        if self.item is not None:
            if tag in ('h3', 'p', 'summary') or (tag in ('span', 'b') and self.field == 'tag'): self.field = None
            if tag == 'a' and self.link is not None:
                self.link['label'] = ' '.join(self.link['label'].split())
                if self.link['label']: self.item['link'] = self.link
                self.link = None
            if self.depth == self.item_depth:
                clean = lambda s: ' '.join(str(s).split())
                self.item.update(tag=clean(self.item['tag']), title=clean(self.item['title']), body=clean(self.item['body']))
                self.items.append(self.item); self.item = None; self.field = None
        self.depth -= 1

    def handle_data(self, data):
        if self.item is None: return
        if self.link is not None: self.link['label'] += data
        if self.field == 'more': self.item['body'] += ' ' + data
        elif self.field: self.item[self.field] += data
        elif data.strip() and self.link is None: self.unknown.append('text:' + data.strip()[:20])


def _element_end(html, start):
    """Index just past the element that opens at `start` (an <ol> or a <div>), nested elements of the same name counted."""
    name = 'ol' if html.startswith('<ol', start) else 'div'; depth = 0
    for tag in re.finditer(rf'<{name}\b|</{name}>', html[start:]):
        depth += -1 if tag.group(0).startswith('</') else 1
        if depth == 0: return start + tag.end()
    raise ValueError('the list is not closed')


def from_section(section_html):
    """The content of one list section. Raises ValueError when it is not a list this file reads whole: every byte of the
    section is either its opening, its heading block, its list or what follows the list — nothing is left unaccounted for."""
    head = re.match(r'<section class="([^"]*)"[^>]*>', section_html)
    if not head or not section_html.endswith('</section>'): raise ValueError('not a section')
    classes = head.group(1).split(); kind = next((k for k in LIST_KINDS if k in classes), None)
    if not kind: raise ValueError('not a list section')
    band = next((c[5:] for c in classes if c.startswith('band-')), 'paper')
    wrap = re.match(r'\s*<div class="wrap[^"]*">', section_html[head.end():])
    if not wrap: raise ValueError('the section does not open the way this reader knows')
    inside = head.end() + wrap.end()
    body_at = re.search(r'<ol class="index-list"|<div class="grid"|<ol class="ladder-list"|<div class="nums"|<div class="qa"', section_html)
    if not body_at or body_at.start() < inside: raise ValueError('the list itself was not found')
    heading = section_html[inside:body_at.start()]
    if heading.strip() and not (re.match(r'\s*<div(?: class="gh[^"]*")?>', heading) and heading.count('<div') == heading.count('</div>')):
        raise ValueError('the section has something before its list that is not its heading block')
    end = _element_end(section_html, body_at.start())
    tail = section_html[end:-len('</section>')]
    if not tail.lstrip().startswith('</div>') or tail.count('</div>') - len(re.findall(r'<div\b', tail)) != 1:
        raise ValueError('what follows the list in its section is not balanced the way this reader knows')
    parser = _List(loose=kind == 'numbers'); parser.feed(section_html[body_at.start():end])
    if parser.unknown: raise ValueError('the list has markup this reader does not know: ' + ', '.join(sorted(set(parser.unknown))[:4]))
    items = [i for i in parser.items if i['title'] or i['body']]
    if len(items) != len(parser.items) or len(items) < 2: raise ValueError('the list has fewer than two readable items')
    return {'kind': kind, 'band': band, 'classes': classes, 'head': heading, 'items': items, 'tail': tail}


def _blocks(html, start):
    """The elements that sit side by side from `start` up to the tag that closes the element they are in:
    ([(name, opening tag, inner start, inner end, end)], where that closing tag begins). Anything between them that is
    not whitespace is refused: a block is read whole or the section is not read."""
    out, i = [], start
    while True:
        while i < len(html) and html[i].isspace(): i += 1
        if html.startswith('</', i): return out, i
        tag = re.compile(r'<([a-z][a-z0-9]*)\b[^>]*>').match(html, i)
        if not tag: raise ValueError('the section holds text or markup outside its blocks')
        name = tag.group(1)
        if name in VOID: out.append((name, tag.group(0), tag.end(), tag.end(), tag.end())); i = tag.end(); continue
        depth, end = 0, None
        for t in re.compile(rf'<{name}\b[^>]*>|</{name}>').finditer(html, i):
            depth += -1 if t.group(0).startswith('</') else 1
            if depth == 0: out.append((name, tag.group(0), tag.end(), t.start(), t.end())); end = t.end(); break
        if end is None: raise ValueError('an element of the section is not closed')
        i = end


def _one_picture(name, inner):
    """{'src', 'alt'} when this block is one embedded picture and nothing else — a <figure>, or a holder around one."""
    inner = inner.strip()
    if name == 'div':
        holder = re.fullmatch(r'<figure\b[^>]*>(.*)</figure>', inner, re.S)
        if not holder: return None
        inner = holder.group(1).strip()
    elif name != 'figure': return None
    img = re.fullmatch(r'<img\b([^>]*)>', inner)
    if not img: return None
    src = re.search(r'\bsrc="(data:image/[^"]*)"', img.group(1)); alt = re.search(r'\balt="([^"]*)"', img.group(1))
    return {'src': src.group(1), 'alt': H.unescape(alt.group(1)) if alt else ''} if src else None


def from_picture(section_html):
    """The content of a section that is its words and one picture. Raises ValueError when it is anything else: every byte
    of the section is its opening, its block of words (kept verbatim), its one picture, or what follows them (kept verbatim)."""
    head = re.match(r'<section class="([^"]*)"([^>]*)>', section_html)
    if not head or not section_html.endswith('</section>'): raise ValueError('not a section')
    classes = head.group(1).split()
    if 'hero' in classes or 'data-sig' in head.group(2) or any(k in classes for k in LIST_KINDS): raise ValueError('not a picture section')
    if 'data-pc' in head.group(2): raise ValueError('this section is already composed')
    if 'cta' in classes or any(c.startswith('cta-') for c in classes): raise ValueError('the closing call to action is not a picture section')
    band = next((c[5:] for c in classes if c.startswith('band-')), 'paper')
    def record(words, word_classes, picture, first, tail, parts=None):
        if '<img' in words or '<section' in words or not re.sub(r'<[^>]+>', '', words).strip(): raise ValueError('the block beside the picture is not a block of words this reader knows')
        plain = ' '.join(H.unescape(re.sub(r'<[^>]+>', ' ', words)).split())
        return {'kind': 'picture', 'band': band, 'classes': classes,
                'words': {'html': words, 'classes': word_classes, 'chars': len(plain), 'rows': len(re.findall(r'<li\b', words)), 'parts': parts,
                          'heading': ' '.join(H.unescape(re.sub(r'<[^>]+>', ' ', (re.search(r'<h2\b[^>]*>(.*?)</h2>', words, re.S) or [None, ''])[1])).split())},
                'picture': picture, 'first': first, 'tail': tail}
    over = _heading_over_photo(section_html, head.end())
    if over: return record(over['words'], ['photo-caption'], over['picture'], 'picture', over['tail'])
    wrap = re.match(r'\s*<div class="wrap[^"]*"[^>]*>', section_html[head.end():])
    if not wrap: raise ValueError('the section does not open the way this reader knows')
    blocks, close = _blocks(section_html, head.end() + wrap.end())
    if not section_html.startswith('</div>', close): raise ValueError('the section is not closed the way this reader knows')
    tail = section_html[close + len('</div>'):-len('</section>')]
    if len(re.findall(r'<div\b', tail)) != tail.count('</div>'): raise ValueError('what follows the picture in its section is not balanced the way this reader knows')
    if not 2 <= len(blocks) <= 4: raise ValueError(f'the section holds {len(blocks)} blocks side by side: a picture section is its words and one picture')
    pictures = [_one_picture(name, section_html[a:b]) for name, _, a, b, _ in blocks]
    if sum(p is not None for p in pictures) != 1: raise ValueError('the section is not its words and one picture')
    at = next(i for i, p in enumerate(pictures) if p); said = [b for i, b in enumerate(blocks) if i != at]; parts = None
    if len(said) == 1: name, opening, a, b, _ = said[0]; words = section_html[a:b]
    else:   # several blocks of words (a heading block and its rows): kept whole, in their order, as one block
        parts = [section_html[a - len(opening):end] for _, opening, a, _, end in said]; words = ''.join(parts); name, opening = 'div', ''
    if name != 'div': raise ValueError('the block beside the picture is not a block of words this reader knows')
    return record(words, (re.search(r'class="([^"]*)"', opening) or [None, ''])[1].split(), pictures[at], 'picture' if at == 0 else 'words', tail, parts)


def _heading_over_photo(section_html, start):
    """The template's other photo form — the picture across the section with its heading set on it, the caption under
    it: {'words', 'picture', 'tail'}, the words being the caption's own blocks with the heading in its place after the
    label. None when the section is not that."""
    try:
        top, close = _blocks(section_html, start)
        if section_html[close:] != '</section>' or len(top) < 2 or top[0][0] != 'figure' or top[1][1] != '<div class="wrap">': return None
        inner, _ = _blocks(section_html, top[0][2]); held, _ = _blocks(section_html, top[1][2])
    except ValueError: return None
    if not (len(inner) == 2 and inner[0][0] == 'img' and inner[1][1] == '<div class="wrap over">' and len(held) == 1 and held[0][1] == '<div class="photo-caption">'): return None
    picture = _one_picture('figure', inner[0][1])
    if not picture: return None
    heading = section_html[inner[1][2]:inner[1][3]]; caption = section_html[held[0][2]:held[0][3]]
    label = re.match(r'\s*<span class="lab">.*?</span>', caption, re.S); at = label.end() if label else 0
    return {'words': caption[:at] + heading + caption[at:], 'picture': picture, 'tail': section_html[top[1][4]:close]}
