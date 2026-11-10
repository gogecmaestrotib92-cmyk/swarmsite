"""standard.py — the measurable half of SWARMSITE_STUDIO_QUALITY_STANDARD.md, as code.

  readings(evidence)  → the numbers of one page that the Standard has a threshold for (what lib/qa/inspect.mjs measured)
  findings(evidence)  → every reading outside its threshold, as a finding: defect id, area, evidence, reason, correction,
                        expectation — the six parts the Standard asks of a finding (§7). Measured, never estimated.
  technical(evidence) → the Track T checks a browser measures beyond the contract (reduced motion, headline in time,
                        layout shift, letters). Reported; the contract's hard promises remain the gate.
  page_level(levels)  → a page level from area levels by the Standard's rule (§5.2).

No model is called here and nothing here edits a page. A threshold lives in one place, THRESHOLDS, with where it comes
from; changing one is a change to the Standard and is made there first. The reference ranges quoted in a finding are
the eleven third-party references measured on 2026-11-10 (SWARMSITE_DESIGN_REFERENCE_RESEARCH.md, Part D)."""
import re

AREAS = ('art_direction', 'typography', 'composition', 'hierarchy', 'imagery', 'originality', 'motion', 'content', 'responsive')
WEIGHTS = {'art_direction': 10, 'typography': 10, 'composition': 8, 'hierarchy': 6, 'imagery': 6, 'originality': 12, 'motion': 8, 'content': 26, 'responsive': 14}   # §5.1
BANDS = ((90, 4), (70, 3), (55, 2), (0, 1))   # §3: the critic's 0–100 scale → level

# id → (area, track, what the reading is, the threshold in words, the references' range, why it reads as a defect, the correction)
CATALOGUE = {
    'TYP-01': ('typography', 'C', 'families carrying text', 'at most 3', 'references 1–3, median 2', 'more faces than a system needs: the page has no single voice [S 37]', 'one pairing from the type registry'),
    'TYP-03': ('typography', 'C', 'headline ÷ body size', 'at most 2 (a picture-led page), 4.5–10, or at least 12', 'references fall into three regimes with nothing between them', 'scale that is neither quiet, classic nor a poster was not decided [S 37]', "the headline's size one step up or down, and the section titles with it"),
    'TYP-04': ('typography', 'C', 'largest type, leading and tracking', 'leading at most 1.1; tracking at most 0', 'references: leading 0.5–1.05, tracking −0.03 to +0.003 em', 'display type set loose falls apart into lines and letters', 'the renderer sets display type tight; not a model\'s choice'),
    'TYP-05': ('typography', 'C', 'characters per line of running text', '40–75 at 1440, 25–50 at 390', 'references 45–72 (median 58) at 1440, 27–48 at 390', 'a line too short breaks every phrase; too long loses the next line [S 34]', 'a wider or narrower text block'),
    'TYP-06': ('typography', 'C', 'headline lines', 'at most 3 at 1440, at most 5 at 390', 'references 1–3 at 1440, 1–5 at 390', 'a headline that long is a paragraph set large', 'fewer words, a smaller size step, or breaks set by sense'),
    'TYP-10': ('typography', 'T', 'letters a face does not draw itself, or accents written as separate marks', 'none', 'not measured on the references', 'a fallback letter or a loose accent in the middle of a word is a misprint', 'a face that draws the content\'s alphabet; the text in composed form'),
    'TYP-11': ('typography', 'C', 'body size', 'at least 14 px', 'references 14–25.9 px, median 16', 'running text below 14 px is small print', 'the renderer\'s body size'),
    'CMP-01': ('composition', 'C', 'outer margin', 'at most 7% of the width', 'references 1–6%', 'content boxed in the middle of the screen with wide empty margins [S 37]', 'the renderer\'s frame; columns to the outer edge'),
    'CMP-03': ('composition', 'C', 'share of text set centred', 'at most 20%, more only on a poster page', 'references: none on 6 of 11, at most 20% on 9', 'centred by default: flush left is the default, centred is for a statement [S 37]', 'flush left; centre only a statement'),
    'CMP-06': ('composition', 'C', 'what leads the first screen', 'a picture over at least 40% of the screen, or a headline across at least 60% of the width', 'references: a picture over 82% or more on 9 of 11; headline width median 81%', 'a small picture beside a narrow headline: neither image nor type leads', 'the first-screen composition: a full-bleed picture, or the headline across the width'),
    'CMP-08': ('composition', 'C', 'changes of ground down the page', 'at most 5', 'references 0–5, median 1', 'a striped page: every section announces itself and none stands out', 'one ground carries the page; a change of ground marks a change of subject'),
    'CMP-09': ('composition', 'C', 'rules on the page', 'at most 16', 'references 0–16, median 1', 'ruled everywhere: a hairline between every row of every section', 'space instead of rules; ruled rows only where the items are tabular'),
    'CMP-10': ('composition', 'C', 'characters per screen (median section)', 'at most 400', 'references 30–400, median 230', 'every screen equally full: nothing is given room', 'fewer words per section, or more space around them'),
    'HIE-02': ('hierarchy', 'C', 'filled buttons on the first screen', 'at most 5', 'references 0–5: none on 5 of 11, one on 3', 'several filled buttons compete; one action is primary [S 16]', 'one filled action; the rest as text links'),
    'HIE-06': ('hierarchy', 'T', 'the page has one h1', 'exactly one', 'three references have none — a lapse of theirs', 'a page without a headline element has no stated subject', 'the first screen\'s headline as the h1'),
    'IMG-02': ('imagery', 'C', 'pictures with a CSS shadow', 'none on a photograph', 'references: 0 of 248 pictures', 'a shadow turns a picture into a card lying on the page', 'no shadow; a product screen keeps one hairline ring'),
    'IMG-03': ('imagery', 'C', 'corner radii of pictures', 'one radius value per page', 'references: no rounded picture on 6 of 11 pages; one radius on most of the rest', 'several corner radii look assembled from parts', 'one radius for the page'),
    'IMG-04': ('imagery', 'C', 'pictures that leave their column', 'at least one, on a page with three or more', 'references: at least one on 8 of 11', 'every picture inside its column: none is given the screen', 'a picture form that runs to the edge or fills the section'),
    'MOT-01': ('motion', 'C', 'share of elements that reveal', 'at most 65%', 'references 0–65%; under 15% on 5 of 11', 'everything enters the same way: motion says nothing', 'reveal headings and pictures only'),
    'MOT-02': ('motion', 'C', 'reveal travel and fade', 'travel at most 32 px; fade 150–800 ms', 'references: travel 6–26 px (median 12), fade 151–784 ms', 'reveals that travel far or last long make the page feel slow', 'the renderer\'s reveal distance and duration'),
    'MOT-03': ('motion', 'T', 'headline fully visible after navigation', 'within 1.5 s', 'references 0.95–4.65 s where animated', 'a hidden headline is not an LCP candidate and delays the first impression [S 57]', 'the headline visible by 1.5 s; the intro animates something else'),
    'MOT-04': ('motion', 'C', 'a section held in place', 'at most 5 screens at 1440; at most 2 at 390', 'references: 3–8 screens on 5 of 11; kept on a phone by 3 of 7', 'a hold takes the scroll away from the visitor [S 7]', 'a shorter hold; released on a phone'),
    'MOT-05': ('motion', 'T', 'reveals on load when the visitor asks for less motion', 'none', 'most references ignore the request; WCAG does not [S 54, 2.3.3]', 'motion the visitor asked not to see', 'the page\'s reveals switched off under prefers-reduced-motion'),
    'MOT-09': ('motion', 'C', 'smoothed scrolling on a phone', 'none', 'references: 0 of 11 at 390', 'smoothing fights the thumb', 'native scrolling at 390'),
    'RSP-01': ('responsive', 'C', 'phone page length against the desktop page, in screens', 'at most 1.6 ×', 'references 0.8–1.5 ×', 'a phone page far longer than the desktop page was stacked, not composed', 'the forms\' phone arrangements'),
    'TEC-16': ('motion', 'T', 'layout shift on load', 'at most 0.1', 'good CLS is ≤ 0.1 [S 56]', 'content that jumps while it loads', 'dimensions on pictures; reveals that animate transform and opacity only [S 59]'),
}

REVIEWED = {
    'ART-01': ('art_direction', 'the page does not do what its own direction says'), 'ART-02': ('art_direction', 'the idea lives on the first screen only; below it the page reverts to stock sections'),
    'ART-03': ('art_direction', 'two scale regimes on one page without intent'), 'ART-04': ('art_direction', 'decoration that does not come from the subject'),
    'TYP-02': ('typography', 'a display face seen everywhere'), 'TYP-08': ('typography', 'emphasis by weight, colour and italic at once'), 'TYP-09': ('typography', 'a heading smaller than the items under it, or a headline that is not the largest type on its screen'),
    'CMP-04': ('composition', 'a picture boxed beside a column of text'), 'CMP-05': ('composition', 'one form repeated down the page'), 'CMP-07': ('composition', 'nothing ever crosses a boundary: every element inside its column and its band'),
    'HIE-01': ('hierarchy', 'two elements compete for first place on a screen'), 'HIE-03': ('hierarchy', 'the first screen does not say what this is within three seconds'),
    'HIE-04': ('hierarchy', 'label, heading, text and caption are not distinguishable'), 'HIE-05': ('hierarchy', 'an action that looks like text, or text that looks like an action'),
    'IMG-01': ('imagery', 'a picture boxed beside text'), 'IMG-06': ('imagery', 'a picture that does not belong to its section'), 'IMG-08': ('imagery', 'a crop that cuts the subject'),
    'ORG-01': ('originality', 'the structure of a known template'), 'ORG-02': ('originality', 'a trend imitated without relation to the subject'), 'ORG-03': ('originality', 'no device of its own'),
    'MOT-06': ('motion', 'no motion system: unrelated durations and easings'), 'MOT-08': ('motion', 'a long sequence that cannot be skipped or interrupted'),
    'USE-01': ('content', 'two sections say the same thing'), 'USE-02': ('content', 'a claim far from its proof; price before proof'), 'USE-03': ('content', 'too many words on a screen'),
    'USE-04': ('content', 'a screen with no visible next step'), 'USE-06': ('content', 'a link where the visitor expects a form, or the reverse'),
    'RSP-02': ('responsive', 'a headline broken one word per line on the phone'), 'RSP-03': ('responsive', 'a picture reduced to a thumbnail on the phone'), 'RSP-04': ('responsive', 'the desktop composition merely stacked on the phone'),
}

THRESHOLDS = {'families': 3, 'quiet': 2.0, 'classic': (4.5, 10.0), 'poster': 12.0, 'display_leading': 1.1, 'line_1440': (40, 75), 'line_390': (25, 50), 'h1_lines_1440': 3, 'h1_lines_390': 5,
              'body_px': 14, 'margin': 0.07, 'centred': 0.2, 'first_picture': 0.4, 'headline_width': 0.6, 'ground_changes': 5, 'rules': 16, 'density': 400, 'filled_buttons': 5,
              'reveal_share': 0.65, 'travel_px': 32, 'fade_ms': (150, 800), 'headline_ms': 1500, 'hold_1440': 5.0, 'hold_390': 2.0, 'phone_lag_ms': 300, 'phone_length': 1.6, 'cls': 0.1}


def _mid(values):
    values = sorted(v for v in values if isinstance(v, (int, float)))
    return values[len(values) // 2] if values else None


def _view(view):
    """The numbers of one view (1440 or 390) of an evidence file, or None when the view was not read."""
    if not isinstance(view, dict) or not view.get('type') or not view.get('sections'): return None
    kinds = view['type']; largest = max(kinds, key=lambda t: t['px'])
    def running(t):
        uses = sum(t['where'].values()) or 1; return t['chars'] * sum(n for k, n in t['where'].items() if k in ('p', 'li', 'blockquote')) / uses
    body = max([t for t in kinds if 12 <= t['px'] <= 30 and running(t) > 0], key=running, default=None)
    h1 = (view.get('headings') or {}).get('h1'); sections = view['sections']; pictures = view.get('pictures') or []; surfaces = view.get('surfaces') or {}
    grounds = [s['ground'] for s in sections]; edges = [e['at'] for e in (view.get('alignment') or {}).get('edges') or []]
    load, scroll = view.get('load') or {}, view.get('scroll') or {}; shown = scroll.get('reveals') or {}; first = view.get('first_screen') or {}
    rules = surfaces.get('rules'); letters = view.get('letters') or {}
    radii = sorted({p['radius'] for p in pictures if p.get('radius') not in (None, '', '0px')})
    held = [float(k) for k in ((scroll.get('held') or {}).get('screens') or {})]
    settled = (load.get('reveals') or {}).get('h1_settles_ms')
    return {
        'screens': view.get('page_screens'), 'families': sorted({t['family'] for t in kinds if t['chars'] >= 20 and not re.match(r'(-apple-system|system-ui|ui-)', t['family'])}),
        'largest_px': largest['px'], 'largest_leading': largest.get('leading'), 'largest_tracking': largest.get('tracking_em'), 'body_px': body['px'] if body else None,
        'h1_px': h1['px'] if h1 else None, 'h1_lines': h1['lines'] if h1 else None, 'h1_width': h1['w'] if h1 else None, 'h1_count': 1 if h1 else 0,
        'headline_to_body': round((h1['px'] if h1 else largest['px']) / body['px'], 1) if body else None, 'largest_to_body': round(largest['px'] / body['px'], 1) if body else None,
        'chars_per_line': _mid([p['per_line'] for p in view.get('paragraphs') or []]), 'sections': len(sections), 'ground_changes': sum(1 for a, b in zip(grounds, grounds[1:]) if a != b),
        'chars_per_screen': _mid([s['chars_per_screen'] for s in sections]), 'centred': (view.get('alignment') or {}).get('text_centred_share'), 'margin': next((e for e in edges if e > 0), None),
        'first_picture': (first.get('largest_picture') or {}).get('share_of_screen') or 0, 'filled_buttons': first.get('filled_buttons'),
        'pictures': len(pictures), 'pictures_bleed': sum(1 for p in pictures if p.get('bleeds')), 'pictures_shadowed': sum(1 for p in pictures if p.get('shadow')), 'picture_radii': radii,
        'pictures_square': sum(1 for p in pictures if p.get('radius') in (None, '', '0px')), 'rules': (sum(rules.values()) if isinstance(rules, dict) else surfaces.get('hairlines')),
        'reveals': shown.get('elements'), 'followed': scroll.get('elements_followed'), 'fade_ms': (shown.get('fade_ms') or [None, None])[1], 'travel_px': (shown.get('travel_px') or [None, None])[1],
        'held_screens': max(held) if held else 0, 'lag_ms': _mid(scroll.get('lag_ms') or []),
        'headline_ms': (settled + (load.get('session') or {}).get('began_ms', 0)) if isinstance(settled, (int, float)) else None,
        'cls': (view.get('lab') or {}).get('cls_on_load'), 'lcp_ms': ((view.get('lab') or {}).get('lcp') or {}).get('ms'),
        'targets': view.get('targets'),
        'letters_not_drawn': sorted({ch for f in letters.get('by_family') or [] for ch in f.get('not_drawn_by_it') or []}), 'accents_apart': letters.get('accents_as_separate_marks') or [],
    }


def readings(evidence):
    """{'desktop': {...}, 'mobile': {...}, 'reduced_motion': {...}} — only what the Standard has a threshold for."""
    views = (evidence or {}).get('views') or {}
    return {'desktop': _view(views.get('desktop')), 'mobile': _view(views.get('mobile')), 'reduced_motion': (evidence or {}).get('reduced_motion'), 'profile': (evidence or {}).get('profile'), 'failed': (evidence or {}).get('failed') or []}


def _finding(fid, view, value, note=''):
    area, track, what, need, seen, why, fix = CATALOGUE[fid]
    return {'id': fid, 'area': area, 'track': track, 'view': view, 'evidence': {'reading': what, 'value': value, 'expected': need, 'references': seen}, 'reason': why,
            'correction': fix, 'expectation': f'{what}: {need}', 'confidence': 'measured', **({'note': note} if note else {})}


def findings(evidence):
    """Every reading outside its threshold. Order: Track T first, then by area as the Standard lists them."""
    r = readings(evidence); d, m, T, out = r['desktop'], r['mobile'], THRESHOLDS, []
    if d:
        if len(d['families']) > T['families']: out.append(_finding('TYP-01', 1440, d['families']))
        ratio = d['headline_to_body']; lo, hi = T['classic']
        if ratio is not None and (T['quiet'] < ratio < lo or hi < ratio < T['poster']): out.append(_finding('TYP-03', 1440, ratio, 'measured on the h1' if d['h1_px'] else 'no h1: measured on the largest type'))
        if d['largest_px'] >= 40 and ((d['largest_leading'] or 0) > T['display_leading'] or (d['largest_tracking'] or 0) > 0.005): out.append(_finding('TYP-04', 1440, {'leading': d['largest_leading'], 'tracking_em': d['largest_tracking']}))
        if d['chars_per_line'] is not None and not T['line_1440'][0] <= d['chars_per_line'] <= T['line_1440'][1]: out.append(_finding('TYP-05', 1440, d['chars_per_line']))
        if (d['h1_lines'] or 0) > T['h1_lines_1440']: out.append(_finding('TYP-06', 1440, d['h1_lines']))
        if d['letters_not_drawn'] or d['accents_apart']: out.append(_finding('TYP-10', 1440, {'not_drawn_by_their_face': d['letters_not_drawn'], 'accents_as_separate_marks': d['accents_apart']}))
        if d['body_px'] is not None and d['body_px'] < T['body_px']: out.append(_finding('TYP-11', 1440, d['body_px']))
        if d['margin'] is not None and d['margin'] > T['margin']: out.append(_finding('CMP-01', 1440, d['margin']))
        poster = ratio is not None and ratio >= T['poster']
        if (d['centred'] or 0) > T['centred'] and not poster: out.append(_finding('CMP-03', 1440, d['centred']))
        if d['first_picture'] < T['first_picture'] and (d['h1_width'] or 0) < T['headline_width']: out.append(_finding('CMP-06', 1440, {'largest_picture_share': d['first_picture'], 'headline_width': d['h1_width']}))
        if d['ground_changes'] > T['ground_changes']: out.append(_finding('CMP-08', 1440, d['ground_changes']))
        if (d['rules'] or 0) > T['rules']: out.append(_finding('CMP-09', 1440, d['rules']))
        if (d['chars_per_screen'] or 0) > T['density']: out.append(_finding('CMP-10', 1440, d['chars_per_screen']))
        if (d['filled_buttons'] or 0) > T['filled_buttons']: out.append(_finding('HIE-02', 1440, d['filled_buttons']))
        if not d['h1_count']: out.append(_finding('HIE-06', 1440, 0))
        if d['pictures_shadowed']: out.append(_finding('IMG-02', 1440, d['pictures_shadowed']))
        if len(d['picture_radii']) > 1: out.append(_finding('IMG-03', 1440, d['picture_radii']))
        if d['pictures'] >= 3 and not d['pictures_bleed']: out.append(_finding('IMG-04', 1440, {'pictures': d['pictures'], 'edge_to_edge': 0}))
        if d['followed'] and d['reveals'] is not None and d['reveals'] / d['followed'] > T['reveal_share']: out.append(_finding('MOT-01', 1440, round(d['reveals'] / d['followed'], 2)))
        slow = d['fade_ms'] is not None and not T['fade_ms'][0] <= d['fade_ms'] <= T['fade_ms'][1]; far = (d['travel_px'] or 0) > T['travel_px']
        if slow or far: out.append(_finding('MOT-02', 1440, {'travel_px': d['travel_px'], 'fade_ms': d['fade_ms']}))
        if d['headline_ms'] is not None and d['headline_ms'] > T['headline_ms']: out.append(_finding('MOT-03', 1440, d['headline_ms']))
        if d['held_screens'] > T['hold_1440']: out.append(_finding('MOT-04', 1440, d['held_screens']))
        if (d['cls'] or 0) > T['cls']: out.append(_finding('TEC-16', 1440, d['cls']))
    if m:
        if m['chars_per_line'] is not None and not T['line_390'][0] <= m['chars_per_line'] <= T['line_390'][1]: out.append(_finding('TYP-05', 390, m['chars_per_line']))
        if (m['h1_lines'] or 0) > T['h1_lines_390']: out.append(_finding('TYP-06', 390, m['h1_lines']))
        if m['held_screens'] > T['hold_390']: out.append(_finding('MOT-04', 390, m['held_screens']))
        if (m['lag_ms'] or 0) > T['phone_lag_ms']: out.append(_finding('MOT-09', 390, m['lag_ms']))
        if (m['cls'] or 0) > T['cls']: out.append(_finding('TEC-16', 390, m['cls']))
        if d and d['screens'] and m['screens'] and m['screens'] / d['screens'] > T['phone_length']: out.append(_finding('RSP-01', 390, round(m['screens'] / d['screens'], 2)))
    calm = r['reduced_motion'] or {}
    if (calm.get('reveals_on_load') or 0) > 0 and (calm.get('reveals_on_load_normally') or 0) > 0: out.append(_finding('MOT-05', 1440, {'with_reduce_motion': calm['reveals_on_load'], 'normally': calm['reveals_on_load_normally']}))
    order = {a: i for i, a in enumerate(AREAS)}
    return sorted(out, key=lambda f: (f['track'] != 'T', order.get(f['area'], 99), f['id'], f['view']))


def technical(evidence):
    """Track T, the part a browser measures beyond the contract: [{id, check, pass, value, need}]. A check that could
    not be read is left out, never guessed."""
    r = readings(evidence); d, m, T, out = r['desktop'], r['mobile'], THRESHOLDS, []
    calm = r['reduced_motion']
    if isinstance(calm, dict) and calm.get('reveals_on_load') is not None:
        out.append({'id': 'T-13', 'check': 'reduce-motion: nothing reveals on load', 'pass': not (calm['reveals_on_load'] and calm.get('reveals_on_load_normally')), 'value': calm['reveals_on_load'], 'need': 0})
    if d:
        if d['headline_ms'] is not None: out.append({'id': 'T-15', 'check': 'headline visible in time', 'pass': d['headline_ms'] <= T['headline_ms'], 'value': d['headline_ms'], 'need': f"≤ {T['headline_ms']} ms"})
        out.append({'id': 'T-19', 'check': 'every letter drawn by its own face', 'pass': not (d['letters_not_drawn'] or d['accents_apart']), 'value': {'not_drawn': d['letters_not_drawn'], 'apart': d['accents_apart']}, 'need': 'none'})
    if m and isinstance(m.get('targets'), dict) and m['targets'].get('counted'):
        out.append({'id': 'T-10', 'check': 'targets at least 24 px on a phone', 'pass': m['targets']['under_24_px'] == 0, 'value': m['targets'], 'need': 'none under 24 px (WCAG 2.5.8); 44 px is the comfortable size'})
    for name, v in (('1440', d), ('390', m)):
        if v and v['cls'] is not None: out.append({'id': 'T-16', 'check': f'layout shift on load at {name}', 'pass': v['cls'] <= T['cls'], 'value': v['cls'], 'need': f"≤ {T['cls']}"})
    return out


def level_of(score):
    """The level of a 0–100 reading on the critic's scale (§3), or None."""
    if not isinstance(score, (int, float)) or isinstance(score, bool) or score < 0: return None
    return next(level for floor, level in BANDS if score >= floor)


def page_level(levels):
    """§5.2: the weighted mean of the area levels, never more than one level above the weakest area, and level 3 only
    with art direction and typography both at 3. `levels`: {area: 1–4}; areas not read are left out."""
    read = {a: float(v) for a, v in (levels or {}).items() if a in WEIGHTS and isinstance(v, (int, float)) and not isinstance(v, bool) and 1 <= v <= 4}
    if not read: return None
    mean = sum(WEIGHTS[a] * v for a, v in read.items()) / sum(WEIGHTS[a] for a in read)
    level = int(min(mean, min(read.values()) + 1) * 2 + 0.5) / 2   # to the half
    if level >= 3 and min(read.get('art_direction', 0), read.get('typography', 0)) < 3: level = 2.5
    return level
