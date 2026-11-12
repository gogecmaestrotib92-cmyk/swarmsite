"""form.py — "a site from nothing": what a visitor typed into one form, and the photographs they uploaded with one
answer each ("what is in this picture?"), as the same contract data the adapter writes (schema.json). Then the same
select → three previews as a captured site (lib/templates/job.py build --form).

Nothing is invented: a field left empty is a section left out; no sentence, label, price or hour is written that the
visitor did not write. The one thing chosen for them is where a typed thing goes — what they offer is a menu for a
restaurant, features for software, a priced list for anyone else — and that rule is written down in `rules`.

    from_form(form, photos_dir=None) -> (data, {'gaps': [...], 'rules': [...], 'media': {rel: file}})

The form (web/start.html sends it as JSON; every field optional but `name`):
    name, sentence                         the business's name, and one sentence of what it does (the page's h1)
    kind                                   one of KINDS (the fixed words of needs.schema.json)
    niche                                  a few words of what kind of business (chooses made pictures; never shown)
    lang                                   the page's language, e.g. 'en'
    accent                                 a colour of theirs, '#rrggbb'
    offers_title, offers: [{name, price, note}]
    link: {t, h}                           the one button: booking, sign-up, order — their words, their address
    contact: {street, postcode, city, country, phone, email, hours: [{days, open, close}]}
    steps_title, steps: [{title, text}]    how it works / how to book, in their steps (at most 6)
    figures: [{v, l}]                      numbers they stand behind: "2 000", "families served since 1998" (at most 4)
    photos: [{file, role, alt, offer, step}]  an uploaded file; role = the answer to "what is in this picture?" (ROLES);
                                           offer / step = the index of the offer or step it shows (pairs it with that block)
    logo: {file}
"""
import json
import re
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
KINDS = json.loads((HERE / 'needs.schema.json').read_text(encoding='utf-8'))['properties']['niche']['items']['enum']
PLACE = {'restaurant', 'hotel', 'venue', 'shop'}          # a place with a door: address, hours and the booking link are its `place`
FOOD = {'restaurant'}                                      # what it offers is a menu
SOFT = {'software', 'app'}                                 # what it offers are features
# "what is in this picture?" — the answers the form offers, and where each goes in the data
ROLES = {'dish': ('photos', 'dish'), 'room': ('photos', 'room'), 'bar': ('photos', 'bar'), 'exterior': ('photos', 'exterior'),
         'team': ('photos', 'people'), 'people': ('photos', 'people'), 'portrait': ('photos', 'portrait'), 'work': ('photos', 'work'),
         'workshop': ('photos', 'workshop'), 'product': ('photos', 'product'), 'detail': ('photos', 'detail'), 'landscape': ('photos', 'landscape'),
         'action': ('photos', 'action'), 'other': ('photos', 'other'), 'screen': ('screens', None), 'phone': ('phones', None)}
IMAGE = {'.jpg', '.jpeg', '.png', '.webp'}
MAX = {'name': 80, 'sentence': 160, 'niche': 120, 'offers_title': 80, 'offer.name': 120, 'offer.price': 40, 'offer.note': 300, 'link.t': 40,
       'alt': 200, 'street': 120, 'postcode': 20, 'city': 80, 'country': 60, 'phone': 40, 'email': 120, 'days': 40, 'time': 12}
OFFERS, PHOTOS, HOURS = 40, 24, 14


def _s(v, n):
    """a typed text: one line, trimmed, cut at n characters; '' when it is not text"""
    return re.sub(r'\s+', ' ', v).strip()[:n] if isinstance(v, str) else ''


def _link(h):
    """an address the visitor typed, made safe: http(s), mailto or tel only; a bare host gets https://"""
    h = _s(h, 500)
    if not h:
        return ''
    if re.match(r'^(https?:|mailto:|tel:)', h, re.I):
        return h if not re.search(r'[\s"<>]', h) else ''
    if re.match(r'^[a-z0-9-]+(\.[a-z0-9-]+)+(/\S*)?$', h, re.I):
        return 'https://' + h
    return ''


def size(raw):
    """(w, h) of a JPEG, PNG or WebP from its bytes; None when it is none of them"""
    if raw[:8] == b'\x89PNG\r\n\x1a\n' and len(raw) >= 24:
        return struct.unpack('>II', raw[16:24])
    if raw[:4] == b'RIFF' and raw[8:12] == b'WEBP':
        k = raw[12:16]
        if k == b'VP8 ' and len(raw) >= 30:
            w, h = struct.unpack('<HH', raw[26:30])
            return w & 0x3fff, h & 0x3fff
        if k == b'VP8L' and len(raw) >= 25:
            b = int.from_bytes(raw[21:25], 'little')
            return (b & 0x3fff) + 1, ((b >> 14) & 0x3fff) + 1
        if k == b'VP8X' and len(raw) >= 30:
            return int.from_bytes(raw[24:27], 'little') + 1, int.from_bytes(raw[27:30], 'little') + 1
        return None
    if raw[:2] == b'\xff\xd8':
        i = 2
        while i + 9 < len(raw):
            if raw[i] != 0xff:
                i += 1
                continue
            m = raw[i + 1]
            if m in (0xd8, 0x01) or 0xd0 <= m <= 0xd7:
                i += 2
                continue
            n = struct.unpack('>H', raw[i + 2:i + 4])[0]
            if m in (0xc0, 0xc1, 0xc2, 0xc3, 0xc5, 0xc6, 0xc7, 0xc9, 0xca, 0xcb, 0xcd, 0xce, 0xcf):
                h, w = struct.unpack('>HH', raw[i + 5:i + 9])
                return w, h
            i += 2 + n
    return None


def _picture(f, photos_dir, i, media, gaps, what):
    """an uploaded file as a picture of the data: {src, w, h}, its bytes to be written at src; None when unusable"""
    name = _s(f, 200)
    if not name or not photos_dir or '/' in name or '\\' in name or name.startswith('.'):
        gaps.append('%s %s: no uploaded file of that name' % (what, i + 1))
        return None
    p = Path(photos_dir) / name
    ext = p.suffix.lower()
    if ext not in IMAGE or not p.is_file():
        gaps.append('%s %s: not an uploaded picture (jpg, png or webp)' % (what, i + 1))
        return None
    wh = size(p.read_bytes()[:65536])
    if not wh or min(wh) < 1:
        gaps.append('%s %s: the file is not a picture that could be read' % (what, i + 1))
        return None
    rel = 'media/upload/%s-%d%s' % (what, i + 1, '.jpg' if ext == '.jpeg' else ext)
    media[rel] = name
    return {'src': rel, 'w': int(wh[0]), 'h': int(wh[1])}


def from_form(form, photos_dir=None):
    f = form if isinstance(form, dict) else {}
    gaps, rules, media = [], [], {}
    d = {}
    name = _s(f.get('name'), MAX['name'])
    sentence = _s(f.get('sentence'), MAX['sentence'])
    if not name:
        raise ValueError('a site needs at least its name')
    d['brand'] = {'name': name, 'logo': None}
    if f.get('lang'):
        lang = _s(f['lang'], 12).lower()
        if re.match(r'^[a-z]{2,3}(-[a-z0-9]{2,8})?$', lang):
            d['lang'] = lang
    kind = _s(f.get('kind'), 20).lower()
    if kind in KINDS:
        d['kind'] = kind
    else:
        gaps.append('kind: none chosen; only templates for any kind of business are offered' if not kind else 'kind: "%s" is not one of the list' % kind)
        kind = ''
    niche = _s(f.get('niche'), MAX['niche'])
    if niche:
        d['niche'] = niche
    elif kind:
        d['niche'] = kind
        rules.append('niche: the kind chosen stands for it (the visitor wrote no words of their own)')
    accent = _s(f.get('accent'), 7).lower()
    if re.match(r'^#[0-9a-f]{6}$', accent):
        d['palette'] = {'ground': '#ffffff', 'ink': '#151515', 'accent': accent}
        rules.append('palette: their colour is the accent, on a white page with near-black text (the editor changes it)')
    d['hero'] = {'title': sentence or name}
    if not sentence:
        gaps.append('hero.title: no sentence of what the business does; the name stands as the headline')
    link = f.get('link') if isinstance(f.get('link'), dict) else {}
    lt, lh = _s(link.get('t'), MAX['link.t']), _link(link.get('h'))
    if lt and lh:
        d['hero']['primary'] = {'t': lt, 'h': lh}
    elif lt or lh or _s(link.get('h'), 500):
        gaps.append('link: a button needs both its words and an address that opens (http, https, mailto or tel); left out')

    # what they offer: a menu, features or a priced list, by the kind of business
    items = []
    for i, o in enumerate((f.get('offers') or [])[:OFFERS] if isinstance(f.get('offers'), list) else []):
        o = o if isinstance(o, dict) else {}
        nm = _s(o.get('name'), MAX['offer.name'])
        if not nm:
            continue
        it = {'name': nm, '_i': i}
        if _s(o.get('price'), MAX['offer.price']):
            it['price'] = _s(o.get('price'), MAX['offer.price'])
        if _s(o.get('note'), MAX['offer.note']):
            it['note'] = _s(o.get('note'), MAX['offer.note'])
        items.append(it)
    title = _s(f.get('offers_title'), MAX['offers_title'])

    # photographs, each with the answer to "what is in this picture?"
    pics, by_offer = {'photos': [], 'screens': [], 'phones': []}, {}
    for i, p in enumerate((f.get('photos') or [])[:PHOTOS] if isinstance(f.get('photos'), list) else []):
        p = p if isinstance(p, dict) else {}
        pic = _picture(p.get('file'), photos_dir, i, media, gaps, 'photo')
        if not pic:
            continue
        role = _s(p.get('role'), 20).lower()
        where, r = ROLES.get(role, ('photos', None))
        if role and role in ROLES and r:
            pic['role'] = r
        elif not role:
            gaps.append('photo %d: no answer to "what is in this picture?"; it is used where any picture may go' % (i + 1))
        alt = _s(p.get('alt'), MAX['alt'])
        if alt:
            pic['alt'] = alt
        pics[where].append(pic)
        if isinstance(p.get('offer'), int) and not isinstance(p.get('offer'), bool):
            by_offer.setdefault(p['offer'], pic['src'])
    for it in items:
        if it['_i'] in by_offer:
            it['img'] = by_offer[it['_i']]
    items = [{k: v for k, v in it.items() if k != '_i'} for it in items]
    if items:
        if kind in FOOD:
            d.setdefault('place', {})['menu'] = {'sections': [{'t': title, 'items': items} if title else {'t': 'Menu', 'items': items}]}
            if not title:
                gaps.append('place.menu: no title for the list; "Menu" heads it')
            rules.append('offers: a restaurant\'s list is its menu (place.menu)')
        elif kind in SOFT:
            d['features'] = {**({'title': title} if title else {}), 'items': [{'t': it['name'], **({'d': it['note']} if it.get('note') else {})} for it in items]}
            rules.append('offers: software\'s list is its features (features.items); a price typed there is left out — plans are not asked here')
            if any(it.get('price') for it in items):
                gaps.append('features: prices were typed for software features; left out (a feature has no price)')
        else:
            d['catalogue'] = {**({'title': title} if title else {}), 'groups': [{'items': items}]}
            rules.append('offers: a priced or listed offer is the catalogue (catalogue.groups)')
    else:
        gaps.append('offers: none typed; no list of what is offered')
    media_out = {k: v for k, v in pics.items() if v}
    if media_out:
        d['media'] = media_out
    else:
        gaps.append('media: no photographs uploaded; only templates that need none are offered')
    lg = f.get('logo') if isinstance(f.get('logo'), dict) else {}
    if lg.get('file'):
        pic = _picture(lg.get('file'), photos_dir, 0, media, gaps, 'logo')
        if pic:
            d['brand']['logo'] = pic['src']

    # how it works, in their steps; numbers they stand behind — each only as typed
    steps = []
    for s in (f.get('steps') or [])[:6] if isinstance(f.get('steps'), list) else []:
        s = s if isinstance(s, dict) else {}
        t = _s(s.get('title'), MAX['offer.name'])
        if t:
            steps.append({'title': t, **({'text': _s(s.get('text'), MAX['offer.note'])} if _s(s.get('text'), MAX['offer.note']) else {})})
    for i, p in enumerate(f.get('photos') or [] if isinstance(f.get('photos'), list) else []):   # a picture may show a step
        st = p.get('step') if isinstance(p, dict) else None
        src = next((x['src'] for x in pics['photos'] + pics['screens'] + pics['phones'] if x['src'].startswith('media/upload/photo-%d.' % (i + 1))), None)
        if isinstance(st, int) and not isinstance(st, bool) and 0 <= st < len(steps) and src and 'img' not in steps[st]:
            steps[st]['img'] = src
    if steps:
        d['steps'] = {**({'title': _s(f.get('steps_title'), MAX['offers_title'])} if _s(f.get('steps_title'), MAX['offers_title']) else {}), 'items': steps}
    figs = []
    for g in (f.get('figures') or [])[:4] if isinstance(f.get('figures'), list) else []:
        g = g if isinstance(g, dict) else {}
        v, l = _s(g.get('v'), 24), _s(g.get('l'), 80)
        if v:
            figs.append({'v': v, **({'l': l} if l else {})})
        elif l:
            gaps.append('figures: "%s" has no number; left out' % l)
    if figs:
        d['figures'] = figs

    # how to reach them
    c = f.get('contact') if isinstance(f.get('contact'), dict) else {}
    addr = {k: _s(c.get(k), MAX[k]) for k in ('street', 'postcode', 'city', 'country') if _s(c.get(k), MAX[k])}
    phone = _s(c.get('phone'), MAX['phone'])
    ph = {'t': phone, 'h': 'tel:' + re.sub(r'[^\d+]', '', phone)} if phone and re.search(r'\d{5}', re.sub(r'\D', '', phone)) else None
    if phone and not ph:
        gaps.append('contact.phone: "%s" has too few digits to dial; left out' % phone)
    email = _s(c.get('email'), MAX['email'])
    if email and not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
        gaps.append('contact.email: not an address; left out')
        email = ''
    hours = []
    for h in (c.get('hours') or [])[:HOURS] if isinstance(c.get('hours'), list) else []:
        h = h if isinstance(h, dict) else {}
        days, op, cl = _s(h.get('days'), MAX['days']), _s(h.get('open'), MAX['time']), _s(h.get('close'), MAX['time'])
        if days and op and cl:
            hours.append({'days': days, 'open': op, 'close': cl})
        elif days or op or cl:
            gaps.append('hours: a line needs its days, opening and closing; "%s" left out' % ' '.join(x for x in (days, op, cl) if x))
    if kind in PLACE:
        pl = d.setdefault('place', {})
        if addr:
            pl['address'] = addr
        if ph:
            pl['phone'] = ph
        if email:
            pl['email'] = email
        if hours:
            pl['hours'] = hours
        if d['hero'].get('primary'):
            pl['booking'] = dict(d['hero']['primary'])
        rules.append('contact: a place with a door keeps its address, phone, hours and booking link in `place`')
    else:
        if ph or email:
            d['contact'] = {**({'phone': ph} if ph else {}), **({'email': email} if email else {})}
        if addr or hours:
            d['locations'] = [{'name': name, **({'address': addr} if addr else {}), **({'phone': ph} if ph else {}), **({'email': email} if email else {}), **({'hours': hours} if hours else {})}]
    if not (addr or ph or email or hours):
        gaps.append('contact: no way to reach them was typed; no contact section')
    return d, {'gaps': gaps, 'rules': rules, 'media': media}


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    data, notes = from_form(json.loads(Path(sys.argv[1]).read_text(encoding='utf-8')), sys.argv[2] if len(sys.argv) > 2 else None)
    print(json.dumps({'data': data, **notes}, ensure_ascii=False))
