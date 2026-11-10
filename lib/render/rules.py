"""rules.py — a page has a budget of rules, and it is spent where the content is tabular.

  budget(html, limit=16) → html

The eleven references carry 0–16 hairlines a page (median 1); ours carried 17–50, a line between every row of every
list (SWARMSITE_DESIGN_REFERENCE_RESEARCH.md, D.3-7, E.1-G3). So the rows of a page are counted section by section and
the rules are kept where rows are a table — a price list first, then questions, then the archive — until the budget
is spent. Every other list keeps its rows and loses its lines: space separates them (`quiet-rules`).
Deterministic, no model, the same answer on the same page; SWARM_RULES=all leaves every rule in place."""
import os, re

LIMIT = 16
ORDER = ('ledger', 'faq', 'archive')   # where a rule separates rows of a table; everything else comes after, in page order
LISTS = {'indexlist', 'ladder', 'ledger', 'faq', 'archive', 'lc', 'wc', 'cards', 'numbers'}
STYLE = ('<style id="quiet-rules">.sec.quiet-rules li,.sec.quiet-rules details,.sec.quiet-rules .arch,.sec.quiet-rules .wc-body{border-top-width:0!important;border-bottom-width:0!important}'
         '.sec.quiet-rules li+li,.sec.quiet-rules details+details{margin-top:clamp(6px,.9vw,14px)}</style>')
OPEN = re.compile(r'<(section|footer)\b([^>]*?)\bclass="([^"]*)"([^>]*)>')


def budget(html, limit=LIMIT):
    if os.environ.get('SWARM_RULES') == 'all' or not isinstance(html, str): return html
    html = re.sub(r'(<(?:section|footer)\b[^>]*?\bclass="[^"]*?) quiet-rules"', r'\1"', html)
    found = []
    for m in OPEN.finditer(html):
        classes = m.group(3).split(); end = html.find('</' + m.group(1) + '>', m.end())
        if 'sec' not in classes or not LISTS & set(classes): continue
        body = html[m.end():end if end > 0 else len(html)]; rows = len(re.findall(r'<li\b|<details\b', body))
        if rows: found.append({'at': m.start(3), 'rows': rows, 'rank': next((i for i, name in enumerate(ORDER) if name in classes), len(ORDER))})
    spent, quiet = 0, []
    for section in sorted(found, key=lambda s: (s['rank'], s['at'])):
        if spent + section['rows'] <= limit: spent += section['rows']
        else: quiet.append(section['at'])
    for at in sorted(quiet, reverse=True):
        close = html.index('"', at); html = html[:close] + ' quiet-rules' + html[close:]
    if quiet and 'id="quiet-rules"' not in html: html = html.replace('</head>', STYLE + '</head>', 1)
    return html
