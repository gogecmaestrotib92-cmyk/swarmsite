"""lineofsight — the build of lineofsight.co (a vision-care practice: one monospaced face in capitals, a ruled page,
a pinned first photograph that is pulled into focus by the scroll) with a client's data written in.
render(d) -> one self-contained page. Pure: no file reads, no model, no network at render time.
Niche: clinic (and other businesses with a door, people and a list of services). Pictures: the client's own photographs."""
from html import escape as E

UP = '../../'
ROMAN = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII']
LABELS = {'de': {'addr': 'Adr.', 'tel': 'Tel.', 'mail': 'E.', 'menu': 'Menü', 'prev': 'Zurück', 'next': 'Weiter', 'skip': 'Zum Inhalt', 'play': 'Film abspielen'},
          'en': {'addr': 'Addr.', 'tel': 'Tel.', 'mail': 'E.', 'menu': 'Menu', 'prev': 'Previous', 'next': 'Next', 'skip': 'Skip to content', 'play': 'Play film'}}
SOCIAL = {'facebook': 'FB.', 'instagram': 'IG.', 'linkedin': 'IN.', 'youtube': 'YT.', 'twitter': 'X.', 'x': 'X.', 'tiktok': 'TT.', 'pinterest': 'PT.', 'whatsapp': 'WA.'}


def _lum(hx):
    hx = (hx or '#000').lstrip('#')
    if len(hx) == 3: hx = ''.join(c * 2 for c in hx)
    try: r, g, b = (int(hx[i:i + 2], 16) / 255 for i in (0, 2, 4))
    except ValueError: return 0.0
    f = lambda v: v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b)


def _t(o, k='t'):
    return (o or {}).get(k) or '' if isinstance(o, dict) else ''


def render(d: dict) -> str:
    lang = (d.get('lang') or 'en')[:2]
    L = LABELS.get(lang, LABELS['en'])
    brand = d.get('brand') or {}
    name = brand.get('name') or ''
    pal = d.get('palette') or {}
    G, K = pal.get('ground') or '#ffffff', pal.get('ink') or '#111111'
    if abs(_lum(G) - _lum(K)) < .35: K = '#0c0c0c' if _lum(G) > .4 else '#fffbeb'   # a palette whose ink cannot carry the page
    media = d.get('media') or {}
    photos = [p for p in (media.get('photos') or []) if p.get('src')]
    by = {p['src']: p for p in photos}
    hero, steps, stm, close, foot = d.get('hero') or {}, d.get('steps') or {}, d.get('statement') or {}, d.get('close') or {}, d.get('foot') or {}
    place, contact, team, cat = d.get('place') or {}, d.get('contact') or {}, d.get('team') or {}, d.get('catalogue') or {}
    feats, plans, faq = d.get('features') or {}, d.get('plans') or {}, d.get('faq') or {}
    cta = d.get('cta') or hero.get('primary') or place.get('booking') or {}

    # ---- photographs: each once, by role, size and proportion --------------------------------------------------
    people = list(team.get('items') or []) + [i for g in (team.get('groups') or []) for i in (g.get('items') or [])]
    step_items = [s for s in (steps.get('items') or []) if s.get('title') or s.get('k') or s.get('text')]
    used = set(s.get('img') for s in step_items if s.get('img')) | set(p.get('img') for p in people if p.get('img'))
    projects = []
    for pr in (d.get('projects') or []):
        if not (pr.get('title') or pr.get('text')): continue
        ph = next((s for s in (pr.get('photos') or []) if s not in used and s in by), None)
        if ph: used.add(ph)
        projects.append((pr, ph))
    pool = [p for p in photos if p['src'] not in used and not p.get('small') and p.get('role') not in ('portrait', 'people')]

    def take(roles, minw, minh):
        c = [p for p in pool if (p.get('w') or 0) >= minw and (p.get('h') or 0) >= minh]
        if not c: return None
        rank = lambda p: (roles.index(p.get('role')) if p.get('role') in roles else len(roles), -(p.get('w') or 0) * (p.get('h') or 0))
        p = sorted(c, key=rank)[0]; pool.remove(p); return p

    # slots are 1440x900 covers: a source is enlarged at most 1.3 times (so 1108x690 at the least)
    p_hero = take(['room', 'exterior', 'work', 'landscape', 'workshop', 'bar', 'product', 'dish', 'action'], 1108, 690)
    p_about = take(['detail', 'workshop', 'room', 'landscape', 'work', 'exterior'], 1108, 690) if (stm.get('title') or stm.get('text')) else None
    video = media.get('video') if isinstance(media.get('video'), dict) and (media.get('video') or {}).get('src') else None
    p_wide = None if video else take(['exterior', 'work', 'room', 'landscape', 'workshop', 'product'], 1040, 400)
    has_list = bool(cat.get('groups') or feats.get('items'))
    p_list = take(['detail', 'room', 'work', 'workshop', 'product', 'exterior'], 600, 690) if has_list else None

    def img(p, cls='', lazy=True, sizes=''):
        return (f'<img class="{cls}" src="{UP}{E(p["src"])}" width="{p.get("w") or ""}" height="{p.get("h") or ""}" alt="{E(p.get("alt") or "")}"'
                f'{" loading=lazy" if lazy else ""} decoding="async">')

    bar = '<i class="bar"></i>'
    tri = '<i class="tri"></i>'

    def btn(o, cls=''):
        if not (_t(o) and o.get('h')): return ''
        return f'<a class="btn rv {cls}" href="{E(o["h"])}"><span>{E(o["t"])}</span>{tri}</a>'

    def ruler(cls): return f'<div class="rl {cls}" aria-hidden="true"><i></i></div>'

    # ---- header -----------------------------------------------------------------------------------------------
    nav = [n for n in (d.get('nav') or []) if _t(n) and n.get('h')]
    for extra in (d.get('signin'), cta):
        if extra and _t(extra) and extra.get('h') and not any(n['t'] == extra['t'] for n in nav): nav.append(extra)
    home = brand.get('home') or '#top'

    def navlist(cls, items, cur=True):
        if not items: return ''
        out = []
        for i, n in enumerate(items):
            c = ' aria-current="page"' if cur and i == 0 else ''
            out.append(f'<a href="{E(n["h"])}" style="--i:{i}"{c}><span>{E(n["t"])}</span>{tri}</a>')
        return f'<nav class="{cls}">{"".join(out)}</nav>'

    header = (f'<header class="hd"><a class="lg" href="{E(home)}">{E(name)}</a>'
              + (f'<button class="tg" type="button" aria-expanded="false" aria-controls="nv"><span>{L["menu"]}</span></button>'
                 f'<div class="nvw" id="nv">{navlist("nv", nav)}</div>' if nav else '') + '</header>')

    # ---- first screen ------------------------------------------------------------------------------------------
    title = hero.get('title') or name
    s_hero = (f'<section class="hero{" pic" if p_hero else ""}" id="top"><div class="hero_in">'
              + (f'<div class="hero_im" data-slot="hero"><div class="hero_ph">{img(p_hero, lazy=False)}</div></div><div class="hero_ov"></div>' if p_hero else '')
              + f'<div class="hero_hd"><h1 class="b"><i class="ln"></i>{bar}{E(title)}</h1></div>{ruler("rl-h")}</div></section>')

    out = []
    # ---- what the business is (the reference's opening sentence) ----------------------------------------------
    if hero.get('text') or hero.get('kicker'):
        k = f'<strong>{E(hero["kicker"])}</strong> ' if hero.get('kicker') else ''
        t2 = f'<p class="bd desc2">{E(hero["text2"])}</p>' if hero.get('text2') else ''
        out.append(f'<div class="c desc"><div class="b">{bar}<p class="th">{k}{E(hero.get("text") or "")}</p>{t2}</div></div>')

    # ---- the three staggered cards -----------------------------------------------------------------------------
    if step_items:
        intro = ''
        if steps.get('title') or steps.get('text'):
            intro = ('<div class="intro"><i class="ln"></i>'
                     + (f'<div class="b">{bar}<h2 class="th"><strong>{E(steps["title"])}</strong></h2></div>' if steps.get('title') else '')
                     + (f'<p class="bd">{E(steps["text"])}</p>' if steps.get('text') else '') + '</div>')
        cards = []
        for i, s in enumerate(step_items):
            p = by.get(s.get('img') or '')
            head = s.get('title') or s.get('k') or ''
            cards.append(f'<li class="k{i % 3}" style="grid-row:{i + 1}"><div class="b">{bar}<span class="ix">{ROMAN[i % 12]}.</span><h3 class="tl">{E(head)}</h3></div>'
                         + (f'<div class="tim fx" data-slot="step">{img(p)}</div>' if p else '')
                         + (f'<p class="bd">{E(s["text"])}</p>' if s.get('text') else '') + btn(s.get('cta')) + '</li>')
        out.append(f'<div class="c steps">{intro}<ol class="thumbs n{min(len(cards), 3)}">{"".join(cards)}</ol></div>')

    # ---- the band over a full-width photograph ------------------------------------------------------------------
    about = []
    if stm.get('title') or stm.get('text'): about.append((stm.get('title') or '', stm.get('text') or ''))
    if about and not cat.get('groups'):
        about += [(f.get('t') or '', f.get('d') or '') for f in (feats.get('items') or []) if f.get('t') and f.get('d')][:2]
        feat_skip = len(about) - 1
    else: feat_skip = 0
    if about:
        lis = ''.join(f'<li class="{"on" if i == (1 if len(about) > 1 else 0) else ""}" tabindex="-1"><i class="ln"></i>'
                      + (f'<div class="b">{bar}<h2 class="tl"><strong>{E(t)}</strong></h2></div>' if t else '<span></span>')
                      + (f'<div class="b">{bar}<p class="bd">{E(x)}</p></div>' if x else '') + '</li>' for i, (t, x) in enumerate(about))
        out.append(f'<section class="about{" pic" if p_about else ""}">'
                   + (f'<div class="about_im" data-slot="about">{img(p_about)}</div>' if p_about else '')
                   + f'<div class="c about_in"><ul class="n{len(about)}">{lis}</ul>{btn(cta)}</div></section>')

    # ---- the wide film or photograph ----------------------------------------------------------------------------
    if video:
        r = (video.get('w') or 16) / (video.get('h') or 9)
        po = f' poster="{UP}{E(video["poster"])}"' if video.get('poster') else ''
        out.append(f'<div class="c wide" data-slot="film"><div class="wide_in" style="aspect-ratio:{max(1.2, min(r, 2.9)):.3f}">'
                   f'<video src="{UP}{E(video["src"])}"{po} controls playsinline preload="metadata" aria-label="{E(video.get("alt") or L["play"])}"></video></div></div>')
    elif p_wide:
        r = (p_wide.get('w') or 16) / (p_wide.get('h') or 9)
        out.append(f'<div class="c wide" data-slot="wide"><div class="wide_in" style="aspect-ratio:{max(1.5, min(r, 2.9)):.3f}">{img(p_wide)}</div></div>')

    # ---- ruled grid: short facts -------------------------------------------------------------------------------
    def grid(cells):
        return f'<div class="c"><ul class="lg3">{"".join(cells)}</ul></div>' if cells else ''
    figs = [f for f in (d.get('figures') or []) if f.get('v')]
    out.append(grid([f'<li><div><b class="th">{E(str(f["v"]))}</b>' + (f'<span class="bd">{E(f["l"])}</span>' if f.get('l') else '') + '</div></li>' for f in figs]))
    out.append(grid([f'<li><div><span class="tl">{E(t)}</span></div></li>' for t in (d.get('trust') or []) if isinstance(t, str) and t.strip()]))
    logos = []
    for lg in (d.get('logos') or []):
        if isinstance(lg, dict) and lg.get('src'):
            logos.append(f'<li><div><img class="lgi" src="{UP}{E(lg["src"])}" alt="{E(lg.get("alt") or lg.get("name") or "")}" loading="lazy"></div></li>')
        elif isinstance(lg, (str, dict)) and (lg if isinstance(lg, str) else lg.get('name') or lg.get('t')):
            logos.append(f'<li><div><span class="tl">{E(lg if isinstance(lg, str) else lg.get("name") or lg.get("t"))}</span></div></li>')
    out.append(grid(logos))

    # ---- lists that open: services, questions (the reference's services page) ----------------------------------
    def row(nm, text='', price='', rows=(), prices=(), h='', note='', state=''):
        pr = f'<b class="pr">{E(price)}</b>' if price else ''
        st = f' <em class="st">{E(state)}</em>' if state else ''
        body = ''
        if text: body += f'<p>{E(text)}</p>'
        if prices: body += '<dl class="pl">' + ''.join(f'<div><dt>{E(x.get("label") or "")}</dt><dd>{E(x.get("price") or "")}</dd></div>' for x in prices if x.get('price')) + '</dl>'
        if rows: body += '<ul class="rw">' + ''.join(f'<li>{E(str(x))}</li>' for x in rows if x) + '</ul>'
        if note: body += f'<p>{E(note)}</p>'
        if body:
            if h: body += f'<p><a class="more" href="{E(h)}">{E(nm)}</a></p>'
            return f'<details class="ac"><summary><span>{E(nm)}{st}</span>{pr}{tri}</summary><div class="ac_c">{body}</div></details>'
        if h: return f'<a class="ac lk" href="{E(h)}"><span class="sm"><span>{E(nm)}{st}</span>{pr}{tri}</span></a>'
        return f'<div class="ac"><span class="sm"><span>{E(nm)}{st}</span>{pr}</span></div>'

    def listing(cls, title, text, groups, pic=None, note=''):
        body = ''
        for gt, gtext, rws in groups:
            if not rws: continue
            body += '<div class="grp">' + (f'<div class="b">{bar}<h3 class="tl"><strong>{E(gt)}</strong></h3></div>' if gt else '') \
                    + (f'<p class="bd gtx">{E(gtext)}</p>' if gtext else '') + f'<div class="acs">{"".join(rws)}</div></div>'
        if not body: return ''
        hd = ''
        if title or text:
            hd = f'<div class="b lhd">{bar}<h2 class="th">' + (f'<strong>{E(title)}</strong>' if title else '') + '</h2>' \
                 + (f'<p class="bd">{E(text)}</p>' if text else '') + '</div>'
        ph = f'<div class="ls_im" data-slot="list"><div>{img(pic)}</div></div>' if pic else ''
        nt = f'<p class="bd lnote">{E(note)}</p>' if note else ''
        return f'<section class="ls {cls}{" pic" if pic else ""}">{ph}<div class="c ls_in">{hd}<div class="ls_b">{body}{nt}</div></div></section>'

    if cat.get('groups'):
        gs = []
        for g in cat['groups']:
            rws = [row(i.get('name') or '', i.get('text') or '', i.get('price') or '', i.get('rows') or (), i.get('prices') or (), i.get('h') or '', i.get('note') or '', i.get('state') or '')
                   for i in (g.get('items') or []) if i.get('name')]
            gs.append((g.get('t') or '', g.get('text') or '', rws))
        out.append(listing('cat', cat.get('title') or '', cat.get('text') or '', gs, p_list, cat.get('note') or ''))
    elif feats.get('items'):
        rws = [row(f.get('t') or '', f.get('d') or '') for f in feats['items'][0:] if f.get('t')]
        rws = rws[feat_skip:] if feat_skip and len(rws) > feat_skip else rws
        out.append(listing('cat', feats.get('title') or '', feats.get('text') or '', [('', '', rws)], p_list))

    # ---- plans: the reference's ruled columns -------------------------------------------------------------------
    pit = [p for p in (plans.get('items') or []) if p.get('name') or p.get('price')]
    if pit:
        cols = ''
        for p in pit:
            rws = ''.join(f'<li>{E(str(x))}</li>' for x in (p.get('rows') or []) if x)
            cols += (f'<li class="{"mk" if p.get("marked") else ""}"><div class="b">{bar}<h3 class="tl">{E(p.get("name") or "")}</h3></div>'
                     + (f'<p class="pp"><b class="th">{E(str(p["price"]))}</b>' + (f' <span class="ts">{E(p["per"])}</span>' if p.get('per') else '') + '</p>' if p.get('price') else '')
                     + (f'<p class="bd">{E(p["line"])}</p>' if p.get('line') else '') + (f'<ul class="rw">{rws}</ul>' if rws else '') + btn(p.get('cta')) + '</li>')
        hd = ''
        if plans.get('title') or plans.get('text'):
            hd = f'<div class="b lhd">{bar}<h2 class="th"><strong>{E(plans.get("title") or "")}</strong></h2>' + (f'<p class="bd">{E(plans["text"])}</p>' if plans.get('text') else '') + '</div>'
        out.append(f'<section class="c plans">{hd}<ul class="pls">{cols}</ul>' + (f'<p class="bd lnote">{E(plans["note"])}</p>' if plans.get('note') else '') + '</section>')

    # ---- people: the reference's team row ----------------------------------------------------------------------
    def slider(cls, cards, label):
        return (f'<div class="sl {cls}"><div class="sl_t" tabindex="0" role="group" aria-label="{E(label)}">{"".join(cards)}</div>'
                f'<div class="sl_n"><button type="button" class="pv" aria-label="{L["prev"]}" disabled>←</button><button type="button" class="nx" aria-label="{L["next"]}">→</button></div></div>')

    if people:
        first = next((by.get(p.get('img') or '') for p in people if by.get(p.get('img') or '')), None)
        ratio = max(2 / 3, min((first.get('w') or 1) / (first.get('h') or 1), 1)) if first else 1
        cards = []
        for p in people:
            if not p.get('name'): continue
            ph = by.get(p.get('img') or '')
            lines = ''.join(f'<p class="ts"><a href="{E(pre + str(v))}">{E(str(v))}</a></p>' for pre, v in (('tel:', p.get('phone')), ('mailto:', p.get('email'))) if v)
            nm = f'<a href="{E(p["h"])}">{E(p["name"])}</a>' if p.get('h') else E(p['name'])
            cards.append('<article class="pc">' + (f'<div class="pim" style="aspect-ratio:{ratio:.3f}">{img(ph)}</div>' if ph else '')
                         + f'<h3 class="tl"><strong>{nm}</strong></h3>' + (f'<p class="ts">{E(p["role"])}</p>' if p.get('role') else '')
                         + (f'<p class="bd">{E(p["text"])}</p>' if p.get('text') else '') + lines + '</article>')
        hd = ''
        if team.get('title') or team.get('text'):
            hd = f'<div class="c"><div class="b lhd">{bar}' + (f'<h2 class="th"><strong>{E(team["title"])}</strong></h2>' if team.get('title') else '') \
                 + (f'<p class="bd">{E(team["text"])}</p>' if team.get('text') else '') + '</div></div>'
        out.append(f'<section class="team">{hd}{slider("ppl", cards, team.get("title") or name)}</section>')

    # ---- named pieces of work: the same row, the reference's card picture ---------------------------------------
    if projects:
        first = next((by[ph] for _, ph in projects if ph), None)
        ratio = max(.8, min((first.get('w') or 1) / (first.get('h') or 1), 1.5)) if first else 1
        cards = []
        for pr, ph in projects:
            t = f'<a href="{E(pr["h"])}">{E(pr.get("title") or "")}</a>' if pr.get('h') else E(pr.get('title') or '')
            cards.append('<article class="pc">' + (f'<div class="pim" style="aspect-ratio:{ratio:.3f}">{img(by[ph])}</div>' if ph else '')
                         + f'<h3 class="tl"><strong>{t}</strong></h3>' + (f'<p class="bd">{E(pr["text"])}</p>' if pr.get('text') else '') + '</article>')
        out.append(f'<section class="team">{slider("prj", cards, name)}</section>')

    # ---- questions ----------------------------------------------------------------------------------------------
    fq = [q for q in (faq.get('items') or []) if q.get('q') and q.get('a')]
    if fq: out.append(listing('faq', faq.get('title') or '', '', [('', '', [row(q['q'], q['a']) for q in fq])]))

    # ---- credentials --------------------------------------------------------------------------------------------
    creds = []
    for c in (d.get('credentials') or []):
        if not c.get('t'): continue
        inner = f'<span class="tl">{E(c["t"])}</span>' + (f'<span class="bd">{E(c["text"])}</span>' if c.get('text') else '') + (f'<span class="ts">{E(str(c["year"]))}</span>' if c.get('year') else '')
        creds.append(f'<li><a href="{E(c["h"])}">{inner}</a></li>' if c.get('h') else f'<li><div>{inner}</div></li>')
    out.append(grid(creds))

    # ---- what people say ---------------------------------------------------------------------------------------
    qs = []
    for q in (d.get('quotes') or []):
        if isinstance(q, str): q = {'q': q}
        if not q.get('q'): continue
        who = ', '.join(x for x in (q.get('name'), q.get('role')) if x)
        qs.append(f'<figure class="qc"><blockquote class="tl">{E(q["q"])}</blockquote>' + (f'<figcaption class="tl">— {E(who)}</figcaption>' if who else '') + '</figure>')
    if qs: out.append(f'<section class="quotes">{slider("qts", qs, name)}</section>')

    # ---- the closing sentence and the ruler ---------------------------------------------------------------------
    phone = place.get('phone') or contact.get('phone') or {}
    if isinstance(phone, str): phone = {'t': phone, 'h': 'tel:' + phone.replace(' ', '')}
    push = ''
    if close.get('title'): push += f'<div class="b">{bar}<h2 class="tl"><strong>{E(close["title"])}</strong></h2>'
    else: push += f'<div class="b">{bar}'
    if phone.get('t'): push += f'<p class="tl"><a class="ph" href="{E(phone.get("h") or "#")}"><strong>{E(phone["t"])}</strong></a></p>'
    push += '</div>'
    if close.get('text'): push += f'<p class="bd">{E(close["text"])}</p>'
    push += btn(close.get('cta') or cta)
    form = contact.get('form') or {}
    if form.get('h') and form.get('t') and form.get('h') != (close.get('cta') or cta or {}).get('h'): push += btn(form)
    out.append(f'<div class="c"><div class="push"><i class="ln"></i>{push}</div></div>{ruler("rl-b")}')

    # ---- foot ---------------------------------------------------------------------------------------------------
    def addr(a):
        l1 = a.get('street') or ''
        if lang == 'en':   # English order: town, county, postcode
            l2 = ', '.join(x for x in (a.get('city'), a.get('region')) if x) + (' ' + a['postcode'] if a.get('postcode') else '')
            l3 = a.get('country') or ''
        else:
            l2 = ' '.join(x for x in (a.get('postcode'), a.get('city')) if x)
            l3 = ', '.join(x for x in (a.get('region'), a.get('country')) if x)
        return [x for x in (l1, l2, l3) if x]
    rows = []
    a = addr(place.get('address') or {})
    small = []
    for loc in (d.get('locations') or []):
        la = ', '.join(addr(loc.get('address') or {}))
        bits = [x for x in (loc.get('name'), la, loc.get('phone') if isinstance(loc.get('phone'), str) else _t(loc.get('phone')), loc.get('email'), loc.get('note')) if x]
        if bits: small.append(E(': '.join(bits[:1]) + (': ' if len(bits) > 1 else '') + ' · '.join(bits[1:])))
        small += [E(f'{h.get("days") or ""}: {h.get("open") or ""} – {h.get("close") or ""}') for h in (loc.get('hours') or []) if h.get('days')]
    hrs = [E(f'{h.get("days") or ""}: {h.get("open") or ""}' + (f' – {h["close"]}' if h.get('close') else '')) for h in (place.get('hours') or []) if h.get('days')]
    if phone.get('note'): hrs.append(E(phone['note']))
    if a or small or hrs:
        dd = ''.join(f'<p class="tl">{E(x)}</p>' for x in a) + ''.join(f'<p class="bd mu">{x}</p>' for x in small + hrs)
        rows.append((L['addr'], dd, 'ad'))
    if phone.get('t'): rows.append((L['tel'], f'<p class="tl"><a href="{E(phone.get("h") or "#")}">{E(phone["t"])}</a></p>', ''))
    mail = place.get('email') or contact.get('email')
    if mail: rows.append((L['mail'], f'<p class="tl"><a href="mailto:{E(mail)}">{E(mail)}</a></p>', ''))
    for s in (place.get('social') or []):
        if not (_t(s) and s.get('h')): continue
        key = s['t'].strip().lower()
        shown = s['h'].split('://')[-1].replace('www.', '').rstrip('/')
        rows.append((SOCIAL.get(key, key[:2].upper() + '.'), f'<p class="tl"><a href="{E(s["h"])}" aria-label="{E(s["t"])}">{E(shown)}</a></p>', ''))
    for r in (contact.get('routes') or []):
        if _t(r) and r.get('h'):
            rows.append(('→', f'<p class="tl"><a href="{E(r["h"])}">{E(r["t"])}</a></p>' + (f'<p class="bd mu">{E(r["note"])}</p>' if r.get('note') else ''), ''))
    dl = ''
    first_small = True
    for lab, dd, cls in rows:
        gap = ' gp' if (cls != 'ad' and first_small and dl) else ''
        if cls != 'ad': first_small = False
        dl += f'<div class="{cls}{gap}"><dt class="tl b">{bar}<strong>{E(lab)}</strong></dt><dd>{dd}</dd></div>'
    flinks = [l for l in (foot.get('links') or []) if _t(l) and l.get('h')]
    nmlen = max(len(name), 8)
    small_print = ' · '.join(x for x in (foot.get('text'), foot.get('legal')) if x)
    footer = ('<footer class="ft"><div class="c ft_in"><i class="ln"></i>' + (f'<dl>{dl}</dl>' if dl else '<span></span>')
              + f'<div class="ft_n">{navlist("fn", nav)}{navlist("fn", flinks, cur=False)}</div>'
              + f'<a class="ft_lg" href="{E(home)}" style="font-size:min(2.25rem,calc((100vw - 3.5rem) / {nmlen * .78:.1f}))">{E(name)}</a>'
              + (f'<small class="ts">{E(small_print)}</small>' if small_print else '') + '</div></footer>')

    desc = hero.get('text') or stm.get('text') or ''
    body = ''.join(x for x in out if x)
    return f'''<!doctype html>
<html lang="{E(lang)}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(name)}{" — " + E(hero["title"]) if hero.get("title") else ""}</title>
<meta name="description" content="{E(desc[:160])}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Geist+Mono:wght@400;600;700&display=swap" rel="stylesheet">
<style>{CSS.replace('__G__', G).replace('__K__', K)}</style>
</head>
<body>
<a class="skip" href="#main">{L["skip"]}</a>
{header}
<main>
{s_hero}
<div class="page" id="main"><i class="pln"></i>
{body}
</div>
</main>
{footer}
<script>{JS}</script>
</body>
</html>'''


CSS = r'''
:root{--g:__G__;--k:__K__;--mu:color-mix(in srgb,var(--g) 80%,var(--k));--ix:color-mix(in srgb,var(--k) 74%,var(--g));
--mg:2.5rem;--bx:-1.5rem;--gap:3rem;--sec:9rem;--tk:39px;
--fh:clamp(18px,1.751vw,28px);--fl:clamp(13px,1.4384vw,23px);--fb:.8125rem;--fs:max(11px,.6875rem);
--eo:cubic-bezier(.215,.61,.355,1);--eio:cubic-bezier(.38,.005,.215,1)}
*,*::before,*::after{box-sizing:border-box}
html{font-size:16px;-webkit-text-size-adjust:100%}
body{margin:0;background:var(--g);color:var(--k);font:400 var(--fb)/1.4 "Geist Mono","DM Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
letter-spacing:.144em;text-transform:uppercase;overflow-wrap:break-word;hyphens:auto;-webkit-font-smoothing:antialiased}
h1,h2,h3,p,ul,ol,dl,dd,figure,blockquote{margin:0;padding:0;font-weight:400;font-size:inherit}
ul,ol{list-style:none}a{color:inherit;text-decoration:none}img,video{display:block;max-width:100%}
strong,b{font-weight:600}em{font-style:normal}
:focus-visible{outline:2px solid currentColor;outline-offset:2px}
.lg:focus-visible,.tg:focus-visible,.nv a:focus-visible,.fn a:focus-visible,.btn:focus-visible,.ac summary:focus-visible,a.ac:focus-visible,.skip:focus-visible{outline-offset:-5px}
.th{font-size:var(--fh);line-height:1.4;hyphens:manual}.tl{font-size:var(--fl);line-height:1.4;hyphens:manual}.bd{font-size:var(--fb);line-height:1.4}.ts{font-size:var(--fs);line-height:1.4}
.c{position:relative;margin:0 var(--mg)}
.skip{position:fixed;left:1rem;top:-4rem;z-index:99;background:var(--k);color:var(--g);padding:.75rem 1.5rem}.skip:focus{top:1rem}
.b{position:relative}.bar{position:absolute;left:var(--bx);top:0;bottom:0;width:5px;background:currentColor}
.ln{position:absolute;left:var(--bx);top:0;bottom:0;width:1px;background:currentColor}
.tri{flex:none;width:10px;height:10px;background:currentColor;clip-path:polygon(0 0,100% 50%,0 100%);transition:transform .5s var(--eo)}
.js .bar{transform:scaleY(0);transform-origin:top;transition:transform .75s var(--eio)}.js .in>.bar,.js .in.bar{transform:none}
/* buttons */
.btn{display:flex;align-items:center;justify-content:space-between;gap:1.5rem;min-height:44px;padding:12px 24px;border:1px solid var(--k);background:var(--k);color:var(--g);font-size:var(--fb);line-height:1.4}
.btn:hover{background:var(--g);color:var(--k)}
.js .btn.rv{clip-path:inset(0 100% 0 0);transition:clip-path .75s var(--eio)}.js .btn.rv.in{clip-path:inset(0)}
/* header */
.hd{position:absolute;inset:0 0 auto 0;z-index:50;height:0}
.js .hd{position:fixed}
.lg{position:absolute;left:24px;top:24px;min-height:36px;max-width:calc(100vw - 400px);display:flex;align-items:center;padding:6px 14px 6px 24px;background:var(--k);color:var(--g);border-left:1px solid var(--g)}
.tg{display:none;position:absolute;right:24px;top:24px;width:300px;height:44px;padding:0 30px;background:var(--k);color:var(--g);border:0;border-left:1px solid var(--g);border-right:1px solid var(--g);font:inherit;letter-spacing:inherit;text-transform:inherit;text-align:left;cursor:pointer}
.js .tg{display:block}
.nvw{position:absolute;right:24px;top:24px;width:300px;clip-path:inset(0 -4px -4px -4px)}
.nv a,.fn a{display:flex;align-items:center;justify-content:space-between;gap:1rem;min-height:44px;padding:12px 24px;background:var(--k);color:var(--g);border-left:1px solid var(--g);border-right:1px solid var(--g);transition:transform .5s var(--eo)}
.nv a .tri,.fn a .tri{opacity:0}
.nv a[aria-current],.fn a[aria-current],.nv a:hover,.fn a:hover{background:var(--g);color:var(--k);border-color:var(--k)}
.nv a[aria-current] .tri,.fn a[aria-current] .tri,.nv a:hover .tri,.fn a:hover .tri{opacity:1;transform:rotate(180deg)}
.js .hd.red:not(.open) .nvw{visibility:hidden;transition:visibility 0s .5s}
.js .hd.red:not(.open) .nv a{transform:translateY(calc(-100% * (var(--i) + 1) - 4px))}
/* rulers */
.rl{overflow:hidden;height:32px}.rl i{display:block;height:32px;width:calc(100% + 30vw);will-change:transform;
background:repeating-linear-gradient(90deg,currentColor 0 1px,transparent 1px calc(var(--tk) * 3)) 24px 0/100% 32px no-repeat,repeating-linear-gradient(90deg,currentColor 0 1px,transparent 1px var(--tk)) 24px 16px/100% 16px no-repeat}
/* first screen */
.hero{position:relative;background:var(--k);color:var(--g)}
.hero_in{position:relative;height:100vh;height:100svh;overflow:hidden}
.js:not(.rm) .hero.pic{height:300vh;height:300svh}.js:not(.rm) .hero.pic .hero_in{position:sticky;top:0}
.js:not(.rm) .hero.pic+.page{margin-top:-100vh;margin-top:-100svh}
.hero_im{position:absolute;inset:0}.hero_ph{position:absolute;inset:0;will-change:transform,filter}
.hero_ph img{width:100%;height:100%;object-fit:cover}
.hero_im::after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,color-mix(in srgb,var(--k) 66%,transparent) 0,color-mix(in srgb,var(--k) 66%,transparent) 50%,transparent 82%),color-mix(in srgb,var(--k) 20%,transparent)}
.hero_ov{position:absolute;inset:0;background:var(--k);opacity:0}
.hero_hd{position:absolute;inset:0 0 56px 0;padding:50vh var(--mg) 0;padding-top:50svh}
.hero h1{position:relative;height:100%;max-width:649px;font-size:var(--fh);font-weight:600;line-height:1.28}
.hero h1 .bar{bottom:auto;height:1.28em}.hero h1 .ln{transform-origin:top}
.rl-h{position:absolute;left:0;right:0;bottom:24px}
/* page */
.page{position:relative;z-index:2;background:var(--g);padding-top:6rem;overflow:clip}
.pln{position:absolute;left:24px;top:24px;bottom:0;width:1px;background:var(--k);z-index:0}
.desc{padding-bottom:calc(var(--sec) * 2)}.desc .th{max-width:880px}.desc2{max-width:600px;margin-top:1.5rem}
.steps{margin-bottom:6rem}
.intro{position:relative;margin-left:calc((100% - 2 * var(--gap)) / 3 + var(--gap));padding-bottom:var(--sec)}
.intro .bd{max-width:416px;margin-top:1.5rem}
.thumbs{position:relative;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:var(--gap)}
.thumbs::before,.thumbs::after{content:"";position:absolute;top:0;bottom:0;width:1px;background:var(--k);left:calc((100% - 2 * var(--gap)) / 3 + var(--gap) / 2)}
.thumbs::after{left:calc((100% - 2 * var(--gap)) / 3 * 2 + var(--gap) * 1.5)}
.thumbs li{display:flex;flex-direction:column;min-width:0}.thumbs .k0{grid-column:2}.thumbs .k1{grid-column:1}.thumbs .k2{grid-column:3}
.ix{display:block;color:var(--ix);font-size:var(--fb);line-height:1.5}
.tim{margin-top:1.5rem;aspect-ratio:416/521;overflow:hidden}.tim img{width:100%;height:100%;object-fit:cover;will-change:transform,filter}
.thumbs .bd{margin-top:1.5rem}.thumbs .btn{margin-top:1.5rem}
/* band */
.about{position:relative;min-height:100vh;min-height:100svh;display:flex;background:var(--k);color:var(--g)}
.about_im{position:absolute;inset:0}.about_im img{width:100%;height:100%;object-fit:cover}
.about_im::after{content:"";position:absolute;inset:0;background:color-mix(in srgb,var(--k) 80%,transparent)}
.about:not(.pic) .btn{border-color:var(--g)}
.about_in{flex:1;display:flex;flex-direction:column;justify-content:flex-end;padding:10rem 0 24px;min-width:0}
.about ul{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:var(--gap);align-items:end;min-height:534px;margin-bottom:8.5rem}
.about li{position:relative;display:flex;flex-direction:column;justify-content:space-between;gap:3rem;margin-left:116px;max-width:300px;min-height:332px;outline:0}
.about li:nth-child(2),.about .n1 li{min-height:534px}.about li:nth-child(3){min-height:433px}
.about li>.ln,.about li .bar{opacity:.3;transition:opacity .5s var(--eo)}.about li.on>.ln,.about li.on .bar{opacity:1}
.about li .b{transition:opacity .5s var(--eo);opacity:.82}.about li.on .b{opacity:1}
/* wide picture */
.wide{margin-top:3rem}.wide_in{border:1px solid var(--k);overflow:hidden;background:var(--k)}.wide_in img,.wide_in video{width:100%;height:100%;object-fit:cover}
/* ruled grid */
.lg3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));row-gap:24px;margin:var(--sec) -24px 0}
.lg3 li{position:relative;min-height:155px;display:flex}
.lg3 li::before{content:"";position:absolute;left:0;right:0;top:0;height:1px;background:var(--k)}.lg3 li::after{content:"";position:absolute;right:0;top:0;bottom:0;width:1px;background:var(--k)}
.lg3 li>*{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:.5rem;padding:24px;text-align:center;min-width:0}
.lg3 a:hover{background:var(--k);color:var(--g)}.lgi{max-width:186px;max-height:93px;object-fit:contain}
/* lists that open */
.ls{position:relative;margin-top:var(--sec)}
.ls_in{display:block;padding:0 0 0 calc(50% - var(--mg) + 16px)}
.ls.pic .ls_in{padding-top:3rem;padding-bottom:3rem}
.ls_im{position:absolute;left:0;top:0;bottom:0;width:calc(50% - 48px);z-index:1}
.ls_im>div{position:sticky;top:0;height:100vh;height:100svh;max-height:100%;overflow:hidden}.ls_im img{width:100%;height:100%;object-fit:cover}
.lhd{margin-bottom:5rem}.lhd .bd{max-width:600px;margin-top:1.5rem}
.grp+.grp{margin-top:6rem}.grp>.b{margin-bottom:3rem}.gtx{max-width:600px;margin:-1.5rem 0 3rem}
.acs{margin:0 -24px}
.ac{display:block;position:relative;border-top:1px solid var(--k)}
.ac::before,.ac::after{content:"";position:absolute;top:0;bottom:24px;width:1px;background:var(--k);left:0}.ac::after{left:auto;right:0}
.ac summary,.ac .sm{display:flex;align-items:flex-start;justify-content:space-between;gap:1.5rem;padding:12px 12px 48px 24px;font-size:var(--fl);line-height:1.4;cursor:pointer;list-style:none}
.ac div.sm,.ac>span.sm{cursor:default}.ac summary::-webkit-details-marker{display:none}
.ac summary>span:first-child,.ac .sm>span:first-child{flex:1;min-width:0}
.ac .tri{margin-top:.6em;transform:rotate(180deg)}.ac[open] .tri{transform:rotate(90deg)}.ac.lk .tri{transform:none}
.ac .pr{flex:none;max-width:45%;text-align:right}.st{color:var(--ix);font-size:var(--fb)}
.ac[open],.ac.lk:hover{background:var(--k);color:var(--g)}.ac[open] .st,.ac.lk:hover .st{color:var(--mu)}
.ac_c{padding:0 72px 36px 24px;color:var(--mu);font-size:var(--fb);line-height:1.4;max-width:696px}.ac_c>*+*{margin-top:.8rem}
.more{text-decoration:underline;text-underline-offset:3px;color:var(--g)}
.pl div{display:flex;justify-content:space-between;gap:1rem;padding:.4rem 0;border-top:1px solid color-mix(in srgb,currentColor 40%,transparent)}
.rw li{padding:.4rem 0;border-top:1px solid color-mix(in srgb,currentColor 40%,transparent)}
.lnote{margin-top:3rem;max-width:600px}
/* plans */
.plans{margin-top:var(--sec)}
.pls{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:var(--gap)}
.pls li{position:relative;display:flex;flex-direction:column;gap:1.5rem;min-width:0;padding-bottom:1.5rem}
.pls li::after{content:"";position:absolute;left:-24px;top:0;bottom:0;width:1px;background:var(--k)}
.pls li.mk{background:var(--k);color:var(--g);padding:1.5rem;margin:-1.5rem 0 0}.pls li.mk .bar{display:none}.pls li.mk .btn{border-color:var(--g)}
.pls .btn{margin-top:auto}.pp .ts{white-space:nowrap}
/* rows that slide */
.team,.quotes{margin-top:var(--sec)}.team .lhd{margin-bottom:3rem}
.sl_t{display:flex;overflow-x:auto;scroll-snap-type:x proximity;scrollbar-width:none;padding:0 24px;scroll-padding:0 24px}.sl_t::-webkit-scrollbar{display:none}
.sl_n{display:flex;justify-content:flex-end;gap:24px;margin:24px 48px 0 0}
.sl_n button{width:72px;height:46px;border:1px solid var(--k);background:var(--g);color:var(--k);font:inherit;cursor:pointer}
.sl_n button:hover:not(:disabled){background:var(--k);color:var(--g)}.sl_n button:disabled{opacity:.25;cursor:default}
.sl.fit .sl_n{display:none}
.pc{flex:none;width:348px;padding:0 24px;scroll-snap-align:start;border-left:1px solid var(--k)}.pc:first-child{border-left:0}
.prj .pc{width:464px}
.pim{overflow:hidden;margin-bottom:24px}.pim img{width:100%;height:100%;object-fit:cover}
.pc .ts{margin-top:.25rem}.pc .bd{margin-top:1rem}
.qc{flex:none;width:min(880px,calc(100vw - 48px));min-height:414px;margin-right:24px;scroll-snap-align:start;background:var(--k);color:var(--g);padding:96px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3rem;text-align:center}
/* closing */
.push{position:relative;margin:var(--sec) 0 0 calc(25% - 34px);max-width:648px;padding:0 48px 8rem 0}
.push>.bd{max-width:600px;margin-top:1.5rem}.push .btn{max-width:416px;margin-top:1.5rem}
.ph{text-decoration:underline;text-underline-offset:4px}.ph:hover{opacity:.6}
.rl-b{margin-bottom:24px;position:relative}
/* foot */
.ft{position:relative;z-index:2;background:var(--k);color:var(--g);padding:3rem 0 6rem}
.ft_in{display:grid;grid-template-columns:minmax(0,2fr) minmax(0,1fr);gap:3rem var(--gap);align-items:start}
.ft_in>.ln{top:-3rem;bottom:0}
.ft dl>div{display:grid;grid-template-columns:184px minmax(0,1fr);column-gap:48px}.ft dl>div.gp,.ft dl>.ad+div{margin-top:6rem}.ft dl>.ad+div~div{margin-top:0}
.ft dt{align-self:start}.mu{color:var(--mu);margin-top:.8rem}.ft dd .tl+.bd{margin-top:1.25rem}
.ft dd a:hover,.ft small a:hover,.pc a:hover{opacity:.6}
.fn+.fn{margin-top:3rem}
.ft_lg{align-self:end;white-space:nowrap;line-height:1.1;margin-left:var(--bx);margin-top:8rem}
.ft small{align-self:end;color:var(--mu)}
@media (max-width:1099px){.about li{margin-left:24px}.ft dl>div{grid-template-columns:110px minmax(0,1fr);column-gap:24px}.qc{padding:64px 48px}.lg{max-width:calc(100vw - 380px)}}
@media (max-width:699px){
html{font-size:14px}:root{--mg:1.5rem;--bx:-1rem;--sec:6rem;--tk:30px}
.lg{left:14px;top:14px;min-height:32px;max-width:calc(100vw - 134px);padding:5px 10px 5px 14px}
.tg{right:15px;top:14px;width:90px;height:39px;padding:0 20px}
.nvw{left:15px;right:15px;top:14px;width:auto}.nv a,.fn a{min-height:39px;padding:10px 20px}
.hero_im::after{background:linear-gradient(180deg,transparent 0,color-mix(in srgb,var(--k) 66%,transparent) 36%,color-mix(in srgb,var(--k) 66%,transparent) 100%),color-mix(in srgb,var(--k) 20%,transparent)}
.hero_hd{inset:0 0 42px 0}.rl-h{bottom:14px}.rl i{background-position:14px 0,14px 16px}
.page{padding-top:5rem}.pln{left:14px;top:14px}
.desc{padding-bottom:6rem}.desc .th{max-width:18rem}
.intro{margin-left:6.4rem;padding-bottom:6rem}
.thumbs{display:block}.thumbs::before,.thumbs::after{display:none}.thumbs li+li{margin-top:3.4rem}
.about{min-height:100svh}.about_in{padding:6rem 0 21px}
.about ul{display:block;min-height:0;margin-bottom:4rem}.about li,.about li:nth-child(n),.about .n1 li{margin-left:0;max-width:none;min-height:0;gap:2rem}.about li+li{margin-top:5rem}
.wide{margin-top:2rem}
.lg3{grid-template-columns:repeat(2,minmax(0,1fr));margin:var(--sec) -14px 0;row-gap:0}.lg3 li{min-height:95px}.lg3 li>*{padding:16px 10px}
.ls_in,.ls.pic .ls_in{padding:0}.ls_im{position:relative;width:auto;height:68vw;margin-bottom:4rem}.ls_im>div{position:static;height:100%}
.lhd{margin-bottom:3rem}.grp+.grp{margin-top:4rem}.grp>.b{margin-bottom:2rem}
.acs{margin:0 -14px}.ac summary,.ac .sm{padding:7px 7px 28px 14px}.ac_c{padding:0 42px 21px 14px}.ac::before,.ac::after{bottom:14px}
.pls{display:block}.pls li+li{margin-top:4rem}.pls li::after{display:none}
.sl_t{padding:0 7px;scroll-padding:0 7px}.sl_n{margin:14px 28px 0 0;gap:14px}.sl_n button{height:41px}
.pc{width:min(300px,78vw);padding:0 14px}.prj .pc{width:min(334px,84vw)}
.qc{width:calc(100vw - 28px);min-height:322px;margin-right:14px;padding:56px 42px;gap:2rem}
.push{margin:var(--sec) 0 0 .5rem;padding:0 0 5rem}.push .btn{max-width:none}
.rl-b{margin-bottom:14px}
.ft{padding:6rem 0 4rem}.ft_in{display:block}.ft_in>.ln{top:-6rem}
.ft dl>div{grid-template-columns:4.5rem minmax(0,1fr);column-gap:1.9rem}.ft dl>div.gp,.ft dl>.ad+div{margin-top:4rem}
.ft_n{margin-top:10rem}.fn+.fn{margin-top:2rem}.ft_lg{display:block;margin-top:10rem}.ft small{display:block;margin-top:4rem}
}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{transition:none!important;animation:none!important;scroll-behavior:auto!important}
.js .bar{transform:none}.js .btn.rv{clip-path:none}}
@media print{.hd{position:absolute}}
'''

JS = r'''(function(){var d=document,h=d.documentElement,w=window;h.classList.add('js');
var rm=w.matchMedia&&w.matchMedia('(prefers-reduced-motion: reduce)').matches;if(rm)h.classList.add('rm');
var q=function(s,e){return (e||d).querySelector(s)},qa=function(s,e){return [].slice.call((e||d).querySelectorAll(s))};
var hd=q('.hd'),tg=q('.tg'),nw=q('.nvw');
function setOpen(o){if(!hd||!tg)return;hd.classList.toggle('open',o);tg.setAttribute('aria-expanded',o?'true':'false')}
function red(){if(hd)hd.classList.toggle('red',w.scrollY>40||w.innerWidth<700);if(hd&&!hd.classList.contains('red'))setOpen(false)}
if(tg){tg.addEventListener('click',function(){var o=!hd.classList.contains('open');setOpen(o);if(o){var a=q('a',nw);a&&a.focus()}});
 if(w.matchMedia('(hover:hover)').matches){tg.addEventListener('mouseenter',function(){setOpen(true)});nw.addEventListener('mouseleave',function(){setOpen(false)})}
 d.addEventListener('keydown',function(e){if(e.key==='Escape'&&hd.classList.contains('open')){setOpen(false);tg.focus()}});
 nw.addEventListener('click',function(e){if(e.target.closest('a'))setOpen(false)});
 d.addEventListener('click',function(e){if(hd.classList.contains('open')&&!e.target.closest('.hd'))setOpen(false)});
 nw.addEventListener('focusout',function(e){if(!e.relatedTarget||!e.relatedTarget.closest||!e.relatedTarget.closest('.hd'))setOpen(false)})}
var ph=q('.hero.pic .hero_ph'),ov=q('.hero.pic .hero_ov'),hr=q('.hero.pic .rl-h i'),hl=q('.hero.pic h1 .ln'),fx=qa('.fx img'),br=q('.rl-b i');
function cl(v){return v<0?0:v>1?1:v}
function run(){red();if(rm)return;var vh=w.innerHeight,y=w.scrollY;
 if(ph&&y<vh*2.2){var t=cl(y/vh),e=1-Math.pow(1-t,3),t2=cl(y/vh-1);
  ph.style.filter=e<.999?'blur('+(15*(1-e)).toFixed(2)+'px)':'none';
  ph.style.transform='translate3d(0,'+(-.25*vh*t2).toFixed(1)+'px,0) scale('+(1+.1*(1-e)).toFixed(4)+')';
  ov.style.opacity=t2.toFixed(3);hr.style.transform='translate3d('+(-.2417*w.innerWidth*e).toFixed(1)+'px,0,0)';hl.style.transform='scaleY('+(1-t2).toFixed(3)+')'}
 for(var i=0;i<fx.length;i++){var r=fx[i].parentNode.getBoundingClientRect();if(r.bottom<-50||r.top>vh+50)continue;var p=cl((vh-r.top)/(vh*.5));
  fx[i].style.filter=p<.999?'blur('+(10*(1-p)).toFixed(2)+'px)':'none';fx[i].style.transform='scale('+(1+.1*(1-p)).toFixed(4)+')'}
 if(br){var b=br.parentNode.getBoundingClientRect();if(b.top<vh&&b.bottom>0)br.style.transform='translate3d('+(-Math.min(.249*(vh-b.top),w.innerWidth*.29)).toFixed(1)+'px,0,0)'}}
w.addEventListener('scroll',run,{passive:true});w.addEventListener('resize',run);run();
var rv=qa('.b,.btn.rv');
if('IntersectionObserver' in w&&!rm){var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{rootMargin:'0px 0px -6% 0px'});rv.forEach(function(e){io.observe(e)})}
else rv.forEach(function(e){e.classList.add('in')});
qa('.about ul').forEach(function(u){var li=qa('li',u);function on(x){li.forEach(function(l){l.classList.toggle('on',l===x)})}
 li.forEach(function(l){l.addEventListener('mouseenter',function(){on(l)});l.addEventListener('focusin',function(){on(l)});l.addEventListener('click',function(){on(l)})})});
qa('.sl').forEach(function(s){var t=q('.sl_t',s),pv=q('.pv',s),nx=q('.nx',s);
 function st(){var m=t.scrollWidth-t.clientWidth;s.classList.toggle('fit',m<4);pv.disabled=t.scrollLeft<4;nx.disabled=t.scrollLeft>m-4}
 function go(k){var c=t.firstElementChild,stp=c?c.getBoundingClientRect().width+(parseFloat(getComputedStyle(c).marginRight)||0):300;t.scrollBy({left:k*stp,behavior:rm?'auto':'smooth'})}
 pv.addEventListener('click',function(){go(-1)});nx.addEventListener('click',function(){go(1)});t.addEventListener('scroll',st,{passive:true});w.addEventListener('resize',st);st();w.addEventListener('load',st)});
})();'''
