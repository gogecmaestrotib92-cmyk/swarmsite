"""fit.py — each slot of the contract holds what the slot is for.

The data reaches a design from several hands (the adapter's rules, the reader's page, the blocks an agent assigned, a
visitor's form), and each of them can set a true string in the wrong slot. Six software sites read beside their
references on 2026-11-17 showed the class: an age notice as a figure (`18+` over `only`), a question and its answer as
a trust phrase in the logo row, a heading cut into a figure (`8` over `Book Types, One Platform`), a step's own number
printed beside the design's number (`01 1`), a card that repeats another section's heading, two paragraphs run
together with no space (`cloud URL.Plays are drawn`).

fit(d) is the one place that says what a slot may hold, after every hand and before a design is chosen:

  steps.items[].k   a name for the step (DRAW), never its bare number: the design numbers the steps itself
  figures[]         a quantity and the words that say what is counted
  trust[]           one short assurance: no question, no second sentence
  links[]           a card of its own, not another section's heading again
  foot.legal        where an age notice stands (18+, 21+): it is the client's legal line and is never lost
  every text        a space after the stop that ends a sentence

Nothing is written here: a string moves, loses a number that the design prints anyway, or is left out. -> notes"""
import re

ORDINAL = re.compile(r'^(?:step|stage|phase|part|no\.?|korak|paso|schritt|étape|etape|fase)?\s*#?\s*0*\d{1,2}\s*[.):]?$', re.I)
LEADING = re.compile(r'^#?0*\d{1,2}\s*[—–\-·:.|)]+\s*(?=[^\d\s])')
AGE = re.compile(r'(?<!\d)(1[689]|21)\s?\+')
# words that cannot be what a number counts when they stand alone under it
BARE = {'only', 'and', 'or', 'more', 'plus', 'the', 'a', 'an', 'of', 'to', 'in', 'for', 'from', 'up', 'yes', 'no', 'new', 'min', 'max'}
GLUED = re.compile(r'(?<=[a-zà-ÿ]{2}[.!?])(?=[A-ZÀ-Ý][a-zà-ÿ]+[\s,])|(?<=[A-Z]{3}[.!?])(?=[A-ZÀ-Ý][a-zà-ÿ]+\s)')
TEXT_KEYS = {'text', 'text2', 'd', 'a', 'q', 'quote'}
TRUST_WORDS = 8


def _norm(s):
    return re.sub(r'\s+', ' ', s or '').strip() if isinstance(s, str) else ''


def _key(s):
    return re.sub(r'[^a-z0-9à-ÿ]+', ' ', _norm(s).lower()).strip()


def step_key(k, title=''):
    """the name a step carries beside its title, or '' when it is only the step's number (or the title again)"""
    k = _norm(k)
    if not k or ORDINAL.match(k):
        return ''
    k = LEADING.sub('', k).strip()
    return '' if not k or ORDINAL.match(k) or _key(k) == _key(title) else k


def figure(f):
    """-> (is a figure, the notice it is instead)"""
    v, l = _norm(f.get('v')), _norm(f.get('l'))
    whole = ('%s %s' % (v, l)).strip()
    if AGE.fullmatch(v) and (not l or l.split()[0].lower().strip('.,') in ('only', 'over', 'and', 'plus', 'years', 'year')):
        return False, whole
    if not v or not l or _key(l) in BARE:
        return False, ''
    if ',' in l or '?' in l:                                 # a heading or a sentence cut after its number
        return False, ''
    return True, ''


def trust(t):
    """-> (is a trust phrase, the notice it is instead)"""
    t = _norm(t)
    if not t:
        return False, ''
    if AGE.search(t):
        return False, t
    if '?' in t or re.search(r'[.!]\s+\S', t) or len(t.split()) > TRUST_WORDS:
        return False, ''
    return True, ''


def unglue(s):
    return GLUED.sub(' ', s) if isinstance(s, str) and len(s) > 40 else s


def _texts(node):
    """every running text of the contract, as (holder, key)"""
    if isinstance(node, dict):
        for k, v in node.items():
            if isinstance(v, str):
                if k in TEXT_KEYS:
                    yield node, k
            else:
                yield from _texts(v)
    elif isinstance(node, list):
        for v in node:
            yield from _texts(v)


def fit(d):
    notes, notices = [], []
    # every text: a space after the stop that ends a sentence
    n = 0
    for holder, k in _texts({k: v for k, v in d.items() if k not in ('media', 'brand', 'palette', 'made')}):
        new = unglue(holder[k])
        if new != holder[k]:
            holder[k] = new
            n += 1
    if n:
        notes.append('fit: %d text(s) had two sentences run together with no space; the space is set' % n)
    # steps: a bare number is not a step's name
    items = [s for s in ((d.get('steps') or {}).get('items') or []) if isinstance(s, dict)]
    cut = 0
    for s in items:
        if s.get('k') is None:
            continue
        k = step_key(s['k'], s.get('title'))
        if k != s['k']:
            cut += 1
            if k:
                s['k'] = k
            else:
                del s['k']
    if cut:
        notes.append('fit: steps.items[].k — %d step(s) carried their own number as a name; the design numbers them' % cut)
    # figures
    if isinstance(d.get('figures'), list):
        keep, out = [], []
        for f in d['figures']:
            ok, notice = figure(f) if isinstance(f, dict) else (False, '')
            (keep if ok else out).append(f)
            if notice:
                notices.append(notice)
        if out:
            d['figures'] = keep
            notes.append('fit: figures — not a quantity with what it counts, left out: ' + '; '.join('%s %s' % (f.get('v'), f.get('l')) if isinstance(f, dict) else str(f) for f in out)[:200])
    # trust
    if isinstance(d.get('trust'), list):
        keep, out = [], []
        for t in d['trust']:
            ok, notice = trust(t) if isinstance(t, str) else (False, '')
            (keep if ok else out).append(t)
            if notice:
                notices.append(notice)
        if out:
            d['trust'] = keep
            notes.append('fit: trust — not one short assurance (a question, two sentences, a notice), left out: ' + '; '.join(str(t) for t in out)[:200])
    # links: a card that only repeats another section's heading
    if isinstance(d.get('links'), list):
        heads = {_key(v.get('title')) for k, v in d.items() if isinstance(v, dict) and k != 'links' and v.get('title')}
        heads |= {_key(i.get('title') or i.get('t')) for k in ('steps', 'features') for i in ((d.get(k) or {}).get('items') or []) if isinstance(i, dict)}
        heads.discard('')
        out = [x for x in d['links'] if isinstance(x, dict) and _key(x.get('t')) in heads]
        if out:
            d['links'] = [x for x in d['links'] if not any(x is o for o in out)]
            notes.append('fit: links — %d card(s) repeat another section\'s heading and are left out: %s' % (len(out), '; '.join(_norm(x.get('t')) for x in out)[:160]))
    # an age notice is the client's legal line: it stands in the footer, once
    if notices:
        foot = d.get('foot') if isinstance(d.get('foot'), dict) else {}
        said = _key('%s %s' % (foot.get('legal') or '', foot.get('text') or ''))
        add = []
        for x in notices:
            x = x.rstrip(' .') + '.' if not x.endswith(('.', '!')) else x
            m = AGE.search(x)
            if m and re.search(r'(?<!\d)%s\s?\+' % m.group(1), '%s %s %s' % (foot.get('legal') or '', foot.get('text') or '', ' '.join(add))):
                continue
            if _key(x) not in said:
                add.append(x)
        if add:
            foot['legal'] = ' · '.join([p for p in [_norm(foot.get('legal'))] if p] + add)[:240]
            d['foot'] = foot
            notes.append('fit: foot.legal — the age notice the page printed among its figures or trust phrases stands in the legal line: ' + ' '.join(add)[:160])
    return notes
