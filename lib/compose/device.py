"""device.py — the first screen's gesture of type, carried down the page.

A composed first screen treats its headline: a line stepped to the right of the one above, one word marked (in the
accent, in italic, hollow, underlined, on a plate). Production shows what happens next: the plan names the sections
that should carry that device, and they come out with the same flat heading as every other section — nothing in a list,
picture or words form can say "step this heading". So the carrying is not left to a composer. This pass reads the
treatment off the first screen that was drawn and gives the same treatment to the heading of each section the plan
names as a carrier, and to the plan's event; when the event is the closing call to action, the closing becomes the
page's one plate of accent with its line set large.

  treatment(ir)                     → {'mark': one of MARKS | None, 'step': half-ems the second line is pushed | 0}
  carry(page_html, plan, ir)        → (page_html, {'drawn', 'treatment', 'sections': {id: what was done}, 'event'})

It writes no word: a heading is the page's own text, cut into two lines at a space and one of its own words wrapped.
A heading that already carries markup, or is centred, is not stepped. Deterministic, no network, no model."""
import html as H, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sections as SECTIONS

MARKS = ('accent', 'italic', 'outline', 'underline', 'box')
STEP_WORDS = (3, 9)      # a heading of fewer words has nothing to step; a longer one is a sentence, not a gesture
CSS = """
.sec .h2 .dv-l{display:block}.sec .h2 .dv-l+.dv-l{padding-left:calc(var(--dv-step,0) * .5em)}
.sec .h2.dv-stepped{text-wrap:wrap;max-width:none}
.sec .pc-col .h2 .dv-l,.sec .lc-head-left .h2 .dv-l,.sec .lc-head-sticky .h2 .dv-l{display:inline;padding-left:0}
.sec .h2 em.dv-mk{font-style:normal;color:inherit}
.sec .h2 em.dv-mk-accent{color:var(--accent-word,var(--accent))}.sec.band-accent .h2 em.dv-mk-accent,.sec.wc-g-accent .h2 em.dv-mk-accent,.sec.dv-event .h2 em.dv-mk-accent{color:inherit;font-style:italic}
.sec.band-accent .h2 em.dv-mk-underline,.sec.wc-g-accent .h2 em.dv-mk-underline,.sec.dv-event .h2 em.dv-mk-underline{text-decoration-color:currentColor}
.sec.band-accent .h2 em.dv-mk-box,.sec.wc-g-accent .h2 em.dv-mk-box,.sec.dv-event .h2 em.dv-mk-box{background:var(--on-accent,var(--paper));color:var(--accent)}
.sec .h2 em.dv-mk-italic{font-style:italic}
.sec .h2 em.dv-mk-outline{color:transparent;-webkit-text-stroke:max(1.2px,.018em) currentColor}
.sec .h2 em.dv-mk-underline{text-decoration:underline;text-decoration-color:var(--accent);text-decoration-thickness:.07em;text-underline-offset:.12em;text-decoration-skip-ink:none}
.sec .h2 em.dv-mk-box{background:var(--accent);color:var(--on-accent,var(--paper));padding:0 .14em;margin:0 -.04em;box-decoration-break:clone;-webkit-box-decoration-break:clone}
.sec.cta.dv-event{--band-paper:var(--accent);--band-ink:var(--on-accent,var(--paper));background:var(--accent);color:var(--on-accent,var(--paper));min-height:min(88svh,900px)!important}
.sec.cta.dv-event.cta-inset{background:var(--paper)}.sec.cta.dv-event.cta-inset>.wrap{background:var(--accent);color:var(--on-accent,var(--paper));min-height:min(80svh,820px);align-content:center}
.sec.cta.dv-event:not(.hero) .h2.h2[style]{font-size:min(clamp(44px,8.4vw,136px),calc((100vw - 48px) / var(--lw,8) * 1.72))!important;line-height:.96;max-width:min(100%,18ch)!important;text-wrap:balance}
.sec.cta.dv-event .btn{background:var(--on-accent,var(--paper));color:var(--accent);border-color:var(--on-accent,var(--paper))}
.sec.cta.dv-event .lab,.sec.cta.dv-event .alts .lab{color:inherit;opacity:.8}
@media(max-width:600px){.sec .h2 .dv-l+.dv-l{padding-left:calc(var(--dv-step,0) * .25em)}.sec.cta.dv-event{min-height:0!important;padding-top:clamp(72px,18vw,120px);padding-bottom:clamp(72px,18vw,120px)}.sec.cta.dv-event.cta-inset>.wrap{min-height:0}}
"""
_word = lambda w: re.sub(r'^\W+|\W+$', '', w, flags=re.U)


def treatment(ir):
    """What the drawn first screen did to its headline, as the rest of the page can repeat it."""
    found = {'mark': None, 'step': 0}
    def walk(o):
        if isinstance(o, dict):
            if o.get('as') == 'h1':
                if o.get('mark') in MARKS: found['mark'] = o['mark']
                ind = [i for i in o.get('indent') or [] if isinstance(i, int)]
                if len(ind) > 1 and max(ind) > min(ind): found['step'] = min(4, max(ind) - min(ind))
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(ir)
    return found


def _cut(words):
    """Where a heading breaks into two lines: the space that leaves the two closest in length, the first not the longer by much."""
    best, at = None, None
    for i in range(1, len(words)):
        a, b = len(' '.join(words[:i])), len(' '.join(words[i:]))
        cost = abs(a - b) + (2 if a > b else 0)
        if best is None or cost < best: best, at = cost, i
    return at


def _heading(section_html):
    """(start, end, attributes, inner) of the section's own h2 when it is plain text."""
    m = re.search(r'<h2\b([^>]*)>(.*?)</h2>', section_html, re.S)
    if not m or '<' in m.group(2) or 'class="h2' not in m.group(1) and "class='h2" not in m.group(1): return None
    return m.start(), m.end(), m.group(1), m.group(2)


def _draw(attrs, inner, treat, word, centred):
    words = inner.split(); done = {}
    if not words: return None, done
    marked = None
    if treat.get('mark'):
        bare = [_word(H.unescape(w)) for w in words]
        marked = next((i for i, b in enumerate(bare) if word and _word(str(word)) and b.casefold() == _word(str(word)).casefold()), None)
        if marked is None: marked = max(range(len(words)), key=lambda i: (len(bare[i]) >= 4, i))   # no word named: the last word of some length
        w = words[marked]; core = re.match(r'^(\W*)(.*?)(\W*)$', w, re.S | re.U)
        words[marked] = f'{core.group(1)}<em class="dv-mk dv-mk-{treat["mark"]}">{core.group(2)}</em>{core.group(3)}' if core and core.group(2) and '&' not in w else f'<em class="dv-mk dv-mk-{treat["mark"]}">{w}</em>'
        done['mark'] = treat['mark']; done['word'] = bare[marked]
    step = treat.get('step') or 0
    if step and not centred and STEP_WORDS[0] <= len(words) <= STEP_WORDS[1]:
        at = _cut([re.sub(r'<[^>]+>', '', w) for w in words])
        body = f'<span class="dv-l">{" ".join(words[:at])}</span> <span class="dv-l">{" ".join(words[at:])}</span>'
        attrs = re.sub(r'class=(["\'])h2', r'class=\1h2 dv-stepped', attrs, count=1)
        attrs = re.sub(r'style="', f'style="--dv-step:{step};', attrs, count=1) if 'style="' in attrs else attrs + f' style="--dv-step:{step}"'
        done['step'] = step
    else: body = ' '.join(words)
    return (f'<h2{attrs}>{body}</h2>' if done else None), done


def carry(page_html, plan, ir):
    """The page with the first screen's treatment on the heading of every carrier and of the event."""
    report = {'drawn': False, 'treatment': None, 'sections': {}, 'event': None}
    treat = treatment(ir); report['treatment'] = treat
    if not isinstance(plan, dict) or not (treat['mark'] or treat['step']): return page_html, report
    wanted = {c['section']: c.get('word') for c in plan.get('carriers') or [] if isinstance(c, dict) and c.get('section')}
    event = (plan.get('event') or {}).get('section')
    if event: wanted.setdefault(event, (plan.get('event') or {}).get('word'))
    out = page_html
    for sec in sorted((s for s in SECTIONS.sections(page_html) if s.get('id') in wanted), key=lambda s: -s['span'][0]):   # from the bottom up: earlier spans stay true
        start, end = sec['span']; body = out[start:end]; classes = sec.get('classes') or []
        closing = sec['id'] == event and 'cta' in classes and not any(c in classes for c in ('cta-pic', 'cta-ov')) and '<form' not in body
        head = _heading(body)
        if head:
            a, b, attrs, inner = head
            centred = (bool(re.search(r'text-align:\s*center', attrs)) or 'wc-f-statement' in classes or ('cta' in classes and 'cta-line' not in classes)
                       or bool(re.search(r'class="[^"]*\bcenter\b[^"]*"[^<]*(?:<span\b[^>]*>[^<]*</span>\s*)*$', body[:a])))   # centred by the block that holds it
            drawn, done = _draw(attrs, inner, treat, wanted[sec['id']], centred)
            if drawn: body = body[:a] + drawn + body[b:]; report['sections'][sec['id']] = done
        if closing:
            body = re.sub(r'(<h2\b[^>]*\bstyle=")([^"]*)"', lambda m: m.group(1) + re.sub(r'max-width:[^;"]+;?', '', m.group(2)) + '"', body, count=1)
            body = re.sub(r'(<section\b[^>]*\bclass=")([^"]*)"', lambda m: f'{m.group(1)}{m.group(2)} dv-event"', body, count=1)
            report['event'] = sec['id']; report['sections'].setdefault(sec['id'], {})['event'] = 'closing plate'
        out = out[:start] + body + out[end:]
    if not report['sections']: return page_html, report
    if 'id="dv-css"' not in out:
        head = out.find('</head>')
        if head < 0: return page_html, report
        out = out[:head] + f'<style id="dv-css">{CSS}</style>' + out[head:]
    report['drawn'] = True
    return out, report
