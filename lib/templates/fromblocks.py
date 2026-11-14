"""fromblocks.py — the page's data completed from the capture's numbered blocks (step 3 of "blocks by number").

Called by the adapter at its end, only when the capture folder holds both blocks.json and assign.json (the switch:
production writes no assign.json yet, so nothing there changes). The adapter's own rules read a page flattened to
text; this reads what the browser laid out, so it is the part that cannot lose a passage:

  1. a place the adapter's rules left empty is filled from the reader's placement by number (assign.py) — only where
     the blocks fit the place as they stand: nothing is cut to fit;
  2. the further sections the reader listed by number (a heading and the blocks under it) are carried, in page
     order, as `more.sections`, which every template sets below its own sections (more.py). A sentence the page
     already says is not said twice. What the reader left out is counted (`_adapter.blocks.left`).

Pure: the same data, blocks and placement give the same result. No model call.
"""
import re

import assign as A

MAX_SECTIONS = 40       # what one page carries under its template; what is past it is counted in `_adapter.blocks.over`
LABEL = 60           # a block this short that is no sentence is a label
FIT = {'statement': 420, 'item': 260, 'name': 80, 'quote': 420}


def _strings(d):
    out = []

    def walk(v, top=False):
        if isinstance(v, dict):
            for k, x in v.items():
                if not str(k).startswith('_') and not (top and k == 'more'):
                    walk(x)
        elif isinstance(v, list):
            for x in v:
                walk(x)
        elif isinstance(v, str):
            out.append(v)
    walk(d, True)
    return out


def _list(items):
    """a list as paragraphs: short labels in one line, sentences each on its own"""
    if not items:
        return []
    return [' · '.join(items)] if all(len(i) <= LABEL for i in items) else list(items)


def _label(t):
    """a short block that is not a sentence: a name, a number, an address, a price — one of a set, not a paragraph"""
    return len(t) <= LABEL and not re.search(r'[.!?]["”’)]?$', t)


def complete(d, seed, key, sentences, pics_of, rules):
    blocks = (seed.get('blocks') or {}).get('blocks') or []
    asg = seed.get('assign') or {}
    if not blocks or not isinstance(asg, dict) or 'raw' not in asg:
        return
    res = A.resolve(asg.get('raw'), blocks)
    page = res['page']
    filled = []

    # 1. places the adapter left empty, where the blocks fit them whole
    st = page.get('statement')
    if 'statement' not in d and st and 40 <= len(st['text']) <= FIT['statement'] and '\n' not in st['text'] and key(st['title']) != key(d['hero'].get('title')):
        d['statement'] = {'title': st['title'], 'text': st['text']}
        filled.append('statement')
    ft = page.get('features')
    if not d.get('features') and ft and 3 <= len(ft['items']) <= 16 and all(len(i['t']) <= FIT['name'] and len(i['d']) <= FIT['item'] and '\n' not in i['d'] for i in ft['items']):
        worded = sum(1 for i in ft['items'] if i['d']) >= len(ft['items']) / 2
        if worded and len(ft['items']) > 9:
            pass                                             # more worded items than a template's list holds: they stand below, each whole
        else:
            d['features'] = {**({'title': ft['title']} if ft['title'] and len(ft['title']) <= 120 else {}), 'items': [{'t': i['t'], 'd': i['d']} for i in ft['items']]}
            filled.append('features')
    sp = page.get('steps')
    if not d.get('steps') and sp and 2 <= len(sp['items']) <= 6 and all(len(i['title']) <= FIT['name'] and len(i['text']) <= FIT['item'] and '\n' not in i['text'] for i in sp['items']):
        d['steps'] = {**({'title': sp['title']} if sp['title'] and len(sp['title']) <= 120 else {}), 'items': [{'title': i['title'], 'text': i['text']} for i in sp['items']]}
        filled.append('steps')
    qs = [q for q in page.get('quotes') or [] if 20 <= len(q['q']) <= FIT['quote'] and '\n' not in q['q']]
    if not d.get('quotes') and qs:
        d['quotes'] = [{'q': q['q'], 'name': q['name'], 'quote': q['q'], 'by': q['name'], **({'role': q['role']} if q['role'] else {})} for q in qs[:6]]
        filled.append('quotes')
    fg = page.get('figures')
    if not d.get('figures') and fg and all(len(f['v']) <= 40 and len(f['l']) <= 60 for f in fg):
        d['figures'] = [{'v': f['v'], 'l': f['l']} for f in fg[:6]]
        filled.append('figures')

    # 2. the further sections the reader chose, each under its own heading; a sentence the data already says is not said twice
    have = [key(s) for s in _strings(d)]
    have = [h for h in have if h]
    said = lambda s: bool(key(s)) and any(key(s) in h for h in have)
    out, words_carried, kept_old = [], 0, []
    # a place the reader made that the data did not take (the adapter's own rules had filled it, or the blocks do not
    # fit it whole) is not lost: it stands below as sections of its own, before the reader's further sections
    back = []
    if 'statement' not in filled and st and st['text']:
        back.append({'title': st['title'], 'parts': [('p', x) for x in st['text'].split('\n\n')]})
    for name, run, tk, dk in (('features', ft, 't', 'd'), ('steps', sp, 'title', 'text')):
        if name not in filled and run:
            if run.get('text'):
                back.append({'title': run['title'], 'parts': [('p', x) for x in run['text'].split('\n\n')]})
            worded = [i for i in run['items'] if i[dk]]
            back += [{'title': i[tk], 'parts': [('p', x) for x in i[dk].split('\n\n')]} for i in worded]
            bare = [i[tk] for i in run['items'] if not i[dk]]
            if len(bare) >= 3:
                back.append({'title': '' if worded or run.get('text') else run['title'], 'parts': [('li', x) for x in bare]})
    for sec in back + res['rest']:
        head = sec['title']
        paras, items = [], []
        for k, t in sec['parts']:
            t = re.sub(r'(…|\.\.\.)\s*\S+(?:\s\S+){0,2}$', '…', t)        # a teaser's own control after its cut ("… See more") is not its words
            if said(t) or (re.search(r'(…|\.\.\.)$', t) and len(t) <= 80):    # said already, or a scrap the page itself cut short
                continue
            if k == 'p' and len(t) > 200:                    # a passage the data says the opening of: the rest of it, by sentence
                t = ' '.join(x for x in sentences(t) if not said(x))
                if not t:
                    continue
            if k == 'li' or _label(t):                       # labels standing together are one line, not a column of one-word paragraphs
                items.append(t)
            else:
                paras += _list(items)
                items = []
                paras.append(t)
        text = '\n\n'.join(paras + _list(items))
        own = pics_of(head) if head else []
        if len(text) < 40 and not (own and head and not said(head)):   # pictures stand under a heading of their own, never under none
            continue
        out.append({'title': ('' if said(head) else head)[:160], 'text': text, **({'imgs': own} if own else {})})
        words_carried += len(text.split())
    words_total = res['measure']['words']
    # what the adapter's own rules had carried below and the blocks' sections do not say stays (no page says less than before)
    told = [key(x['title']) for x in out] + [key(x['text']) for x in out] + have
    for x in ((d.get('more') or {}).get('sections') or []):
        t, body = key(x.get('title')), [p for p in sentences(x.get('text') or '') if key(p)]
        if (t and any(t == k for k in told)) or (body and sum(1 for p in body if any(key(p) in k for k in told)) >= len(body) / 2):
            continue
        if not t and not body:
            continue
        out.append(x)
        kept_old.append(x.get('title') or '')
    over = max(0, len(out) - MAX_SECTIONS)
    if out:
        d['more'] = {'sections': out[:MAX_SECTIONS]}
    else:
        d.pop('more', None)
    d['_adapter']['blocks'] = {'filled': filled, 'sections': len(out[:MAX_SECTIONS]), 'over': over, 'words': words_total, 'carried_below': words_carried,
                               'skipped': res['measure']['skipped'], 'left': res['measure']['left'], 'kept_from_flat': len(kept_old)}
    rules.append('blocks: %s; %d section(s) of the page\'s own blocks stand under the template\'s sections%s' % (
        ('filled ' + ', '.join(filled)) if filled else 'no empty place filled', len(out[:MAX_SECTIONS]), (' (%d more are past what one page carries)' % over) if over else ''))
