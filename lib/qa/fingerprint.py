"""fingerprint.py — the structural fingerprint of a rendered page: which section forms it uses, in which order.

Two pages built on one template share a fingerprint whatever their words, pictures and colours are, so the distance
between two fingerprints is a cheap, model-free answer to "is this the same template again?". It grades nothing about
taste: a page can be original and bad. It only says how alike two skeletons are.

  signature(html)   every <section> in page order as "class.tokens[data-sig]" (without `sec` and the colour band)
  body(sig)         the signature without the hero and without the closing (call to action, archive)
  similarity(a, b)  0..1 on two signatures; 1.0 = same forms in the same order
  compare(pages)    signatures, pairwise similarity and the number of distinct skeletons for a set of pages

Usage: python3 lib/qa/fingerprint.py page.html [more.html ...] [--write fingerprint.json]
Deterministic, no network, no model."""
import hashlib, json, os, re, sys
from difflib import SequenceMatcher
from html.parser import HTMLParser

# Classes that say how a section is coloured or spaced, not what it is.
IGNORED = re.compile(r'^(sec|band-[\w-]+|compact|atmos|light|flip)$')
CLOSING = ('cta', 'overlay.cta-ov', 'archive', 'end')


class _Sections(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.found = []

    def handle_starttag(self, tag, attrs):
        if tag != 'section': return
        a = dict(attrs)
        tokens = [c for c in str(a.get('class') or '').split() if not IGNORED.match(c)]
        if not tokens: tokens = ['section']
        sig = a.get('data-sig')
        self.found.append('.'.join(tokens) + (f'[{sig}]' if sig else ''))


def signature(html):
    """Every <section> of the page, in order. Scripts and styles are skipped by the parser; text is ignored."""
    parser = _Sections()
    parser.feed(str(html or ''))
    return parser.found


def body(sig):
    """The sections between the hero and the closing: where two pages on one template look alike or do not."""
    out = list(sig)
    if out and out[0].startswith('hero'): out = out[1:]
    while out and out[-1].split('[')[0].startswith(CLOSING): out = out[:-1]
    return out


def digest(sig):
    return hashlib.sha1('\n'.join(sig).encode('utf-8')).hexdigest()[:12]


def similarity(a, b):
    """1.0 when both pages use the same forms in the same order; 0.0 when they share none. Two empty bodies are alike."""
    a, b = list(a), list(b)
    if not a and not b: return 1.0
    return round(SequenceMatcher(None, a, b, autojunk=False).ratio(), 3)


def fingerprint(html):
    sig = signature(html); inner = body(sig)
    return {'signature': sig, 'body': inner, 'hero': sig[0] if sig and sig[0].startswith('hero') else None,
            'digest': digest(sig), 'body_digest': digest(inner), 'sections': len(sig)}


def compare(pages):
    """pages: {name: html}. Returns each fingerprint, the pairwise similarity of the bodies and of the whole pages,
    and how many distinct skeletons the set holds."""
    prints = {name: fingerprint(html) for name, html in pages.items()}
    names = sorted(prints)
    pairs = []
    for i, x in enumerate(names):
        for y in names[i + 1:]:
            pairs.append({'a': x, 'b': y, 'body': similarity(prints[x]['body'], prints[y]['body']),
                          'page': similarity(prints[x]['signature'], prints[y]['signature'])})
    scores = [p['body'] for p in pairs]
    return {'pages': prints, 'pairs': pairs,
            'distinct_bodies': len({p['body_digest'] for p in prints.values()}),
            'distinct_pages': len({p['digest'] for p in prints.values()}),
            'mean_body_similarity': round(sum(scores) / len(scores), 3) if scores else None,
            'max_body_similarity': max(scores) if scores else None}


if __name__ == '__main__':
    args = sys.argv[1:]
    target = args[args.index('--write') + 1] if '--write' in args else None
    files = [a for i, a in enumerate(args) if a != '--write' and (i == 0 or args[i - 1] != '--write')]
    if not files: raise SystemExit(__doc__)
    def read(path):
        with open(path, encoding='utf-8') as f: return f.read()
    result = fingerprint(read(files[0])) if len(files) == 1 else compare({os.path.basename(os.path.dirname(os.path.abspath(f))) + '/' + os.path.basename(f): read(f) for f in files})
    if target:
        with open(target, 'w', encoding='utf-8') as f: json.dump(result, f, indent=1)
    print(json.dumps(result if len(files) > 1 else {k: result[k] for k in ('hero', 'body', 'digest', 'sections')}))
