"""compose_lists.py — a model chooses how the lists below the first screen are drawn; this file keeps it honest.

The same loop as for the first screen (compose.py): the model sees each list as the template drew it and what it holds,
answers with a list composition (lists.py) and nothing else; the validator's reasons go back once; the drawn sections
are pictured and the whole page graded by the contract, and what the composition newly breaks goes back once with the
pictures; a composition that still breaks the page is refused whole and the page keeps the template's lists.

  compose(page_html, page_path, model=None, review=True, ask=None) → {'doc', 'drawn', 'attempts', 'log', 'measured'}
Needs ANTHROPIC_API_KEY for the default model call. Every call is charged to the job budget when SWARM_JOB_DIR is set."""
import json, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'lib', 'swarm')); sys.path.insert(0, os.path.join(ROOT, 'lib'))
import compose as HERO
import lists as LISTS
import validate as V

SYSTEM = """You are the art director of a small studio. The first screen of this page is composed. Below it the page is mostly lists — an index of features, a row of cards — and a page-building template drew each of them in the one form it has. You decide how the lists that would gain from it are drawn instead. The words are fixed: you choose a form, you do not write.

How lists read as designed rather than assembled:
- The form says what kind of list it is. A sequence or an index reads as a ledger. A handful of parallel things read as columns. A set of facts where one matters most reads as tiles with that one large.
- Two lists that follow each other never take the same form, and a page does not need every list changed: a list you leave out stays as the template drew it.
- One idea runs down the page. If the numerals are large and hollow in one list, they are not small and grey in the next; if one heading stands to the left of its list, think about whether the next one should too.
- A heading that stays while its list scrolls is for a long list (six items or more) — it gives the list a spine.
- The featured tile of a bento takes the accent colour: feature the fact a visitor should remember, not the first one.

THE FORMAT — call write_lists with "concept" (one sentence: the idea that runs through these lists) and "lists": one object per list you recompose:
- "section": the list's id, as given.
- "form": ledger | stagger | bento.
  · ledger: one item per row across the width — its numeral or tag large at the left, its title, its body — ruled with hairlines.
  · stagger: two or three columns ("cols": 2 or 3) whose items step down against each other, the numeral large above each title.
  · bento: tiles on a grid; "feature" is the position (0 first) of the one drawn large on the accent colour. Three items or more; its heading sits on top.
- "head": top | left | sticky — where the list's own heading block sits: above it, in a column to its left, or to its left and staying in view while the list scrolls (four items or more).
- "numerals": big | outline | small | none — how each item's number or tag is drawn (outline: hollow figures). Tags that are facts ("14 days", "60+") are never hidden.
- "title": md | lg — the size of the item titles.
A composition that breaks a rule is refused whole and you are told why."""

ENTRY = {"type": "object", "required": ["section", "form"], "properties": {
    "section": {"type": "string"}, "form": {"type": "string", "enum": list(LISTS.FORMS)}, "head": {"type": "string", "enum": list(LISTS.HEADS)},
    "numerals": {"type": "string", "enum": list(LISTS.NUMERALS)}, "cols": {"type": "integer"}, "feature": {"type": "integer"}, "title": {"type": "string", "enum": list(LISTS.TITLES)}}}
TOOL = {"name": "write_lists", "description": "How the lists below the first screen are drawn.", "input_schema": {"type": "object", "required": ["concept", "lists"], "properties": {
    "concept": {"type": "string", "description": "one sentence: the idea that runs through these lists"},
    "lists": {"type": "array", "minItems": 1, "maxItems": 12, "items": ENTRY}}}}
MAX_PICTURED = 6   # sections shown to the model as drawn; the rest are described



def section_shots(page_path, ids):
    """One picture per section id at 1440, motion off, navigation hidden (lib/compose/secshots.mjs): {id: path}."""
    out = tempfile.mkdtemp(prefix='compose-sections-')
    r = subprocess.run(['node', os.path.join(HERE, 'secshots.mjs'), page_path, out] + list(ids), cwd=ROOT, capture_output=True, text=True, timeout=240)
    if r.returncode: raise RuntimeError('sections could not be pictured: ' + (r.stderr or r.stdout)[-300:])
    return {i: os.path.join(out, i + '.jpg') for i in ids if os.path.exists(os.path.join(out, i + '.jpg'))}


def brief(page_html):
    """What may be recomposed, as text: every list with what it holds, in the order of the page. → (text, [section ids])"""
    lines, ids = ['THE PAGE, top to bottom (lists you may recompose are marked ▸):'], []
    page = LISTS._read(page_html)
    for sec in LISTS.SECTIONS.sections(page_html):
        known = page.get(sec['id'])
        if known and not isinstance(known[1], str):
            c = known[1]; ids.append(sec['id']); tags = [i['tag'] for i in c['items'] if i['tag']]
            heading = ' '.join(re.sub(r'<[^>]+>', ' ', c['head']).split())[:110]
            facts = not LISTS.numbering(c['items'])
            lines.append(f'▸ "{sec["id"]}" — {c["kind"]}, {len(c["items"])} items, on the {c["band"]} band. Heading: "{heading}". '
                         f'Tags: {", ".join(tags[:6]) or "none"}{" (facts: cannot be hidden)" if facts else " (numbering)" if tags else ""}. '
                         f'Titles {min(len(i["title"]) for i in c["items"])}–{max(len(i["title"]) for i in c["items"])} characters, bodies {min(len(i["body"]) for i in c["items"])}–{max(len(i["body"]) for i in c["items"])}.'
                         + (f' {sum(1 for i in c["items"] if i["picture"])} items have a picture.' if any(i['picture'] for i in c['items']) else ''))
        else:
            kind = next((k for k in sec['classes'] if k not in ('sec', 'compact') and not k.startswith('band-')), 'section')
            lines.append(f'  "{sec["id"] or "-"}" — {kind}' + (f' (a list that cannot be recomposed: {known[1]})' if known else ''))
    return '\n'.join(lines), ids


def _to_doc(answer):
    lists = answer.get('lists')
    if isinstance(lists, str) and lists.strip()[:1] == '[':
        try: lists = json.loads(lists)
        except ValueError: pass
    return {'ir': V.VERSION, 'note': str(answer.get('concept') or '')[:300], 'lists': lists}


def compose(page_html, page_path, model=None, review=True, ask=None):
    """Compose the lists, correct once, look and revise once. Returns the last document that validates and breaks nothing, or none."""
    if ask is None:
        import agents; ask = agents.ask
    text, ids = brief(page_html); log, findings, best = [], None, None
    if not ids: return {'doc': None, 'drawn': False, 'attempts': 0, 'log': [{'stage': 'skip', 'errors': ['the page has no list that can be recomposed']}], 'measured': None}
    material = [{"type": "text", "text": text}]
    try:
        shots = section_shots(page_path, ids[:MAX_PICTURED]) if review else {}
        for sid in ids[:MAX_PICTURED]:
            if sid in shots: material += [{"type": "text", "text": f'LIST "{sid}" AS THE TEMPLATE DREW IT:'}, HERO._image_block(shots[sid], 900)]
    except Exception as e: material.append({"type": "text", "text": f'(the lists could not be pictured: {str(e)[:80]})'})

    def attempt(stage, extra):
        answer = ask(SYSTEM, material + extra + [{"type": "text", "text": "Call write_lists."}], TOOL, model=model, max_tokens=3000)
        if not isinstance(answer, dict):
            entry = {'stage': stage, 'errors': ['no composition returned']}; log.append(entry); return None, ['none'], entry
        doc = _to_doc(answer); errors = LISTS.validate(doc, page_html)
        entry = {'stage': stage, 'concept': doc['note'], 'errors': [f"{e['code']} {e['at']}: {e['message']}" for e in errors], **({'refused': doc['lists']} if errors else {})}; log.append(entry)
        return doc, errors, entry

    doc, errors, entry = attempt('compose', [])
    if errors and doc is not None:
        doc, errors, entry = attempt('correct', [{"type": "text", "text": "YOUR PREVIOUS COMPOSITION WAS REFUSED:\n" + json.dumps(doc['lists'], ensure_ascii=False) + "\nReasons:\n" + '\n'.join('- ' + e for e in entry['errors'][:12]) + "\nKeep the idea; fix exactly these."}])
    if doc is not None and not errors: best = doc
    if best:
        folder = os.path.dirname(os.path.abspath(page_path))
        def look_at(candidate):
            page, _ = LISTS.transplant(page_html, candidate)
            with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8', dir=folder) as f: f.write(page); drawn = f.name
            try:
                named = [l['section'] for l in candidate['lists']]
                pictures = section_shots(drawn, named[:MAX_PICTURED]) if review else {}
                found = HERO.measured(drawn)
            finally: os.unlink(drawn)
            return pictures, {k: v for k, v in found.items() if k not in baseline}
        try:
            baseline = HERO.measured(page_path)
            pictures, findings = look_at(best); entry['measured'] = findings
            if review:
                look = [{"type": "text", "text": "YOUR LISTS, AS DRAWN:\n" + json.dumps(best['lists'], ensure_ascii=False)}]
                for sid, path in pictures.items(): look += [{"type": "text", "text": f'LIST "{sid}":'}, HERO._image_block(path, 900)]
                must = {k: v for k, v in findings.items() if any(b in k for b in HERO.BREAKING)}; other = {k: v for k, v in findings.items() if k not in must}
                if must: look.append({"type": "text", "text": "MEASURED ON THIS RENDER — your lists break these; fix them, or none of it is shipped:\n" + '\n'.join(f'- {k}: {v}' for k, v in must.items())})
                if other: look.append({"type": "text", "text": "ALSO MEASURED — yours to weigh:\n" + '\n'.join(f'- {k}: {v}' for k, v in other.items())})
                look.append({"type": "text", "text": "Look at them as the art director. Is any list cramped, sparse, lopsided, or is a tile nearly empty? Do two neighbours look the same? Does one idea run through them? "
                                                        "Return the lists you would ship: revised where the pictures or the measurements show a problem, unchanged if you would ship this."})
                revised, revised_errors, second = attempt('revise', look)
                if revised is not None and not revised_errors:
                    _, revised_findings = look_at(revised); second['measured'] = revised_findings
                    if HERO._standing(revised_findings) > HERO._standing(findings): second['errors'] = ['revision measured worse than the first composition: kept the first']
                    else: best, findings = revised, revised_findings
        except Exception as e: log.append({'stage': 'look', 'errors': ['review skipped: ' + str(e)[:160]]})
        if HERO._broken(findings):
            log.append({'stage': 'refuse', 'errors': [f'the lists break the page on the render ({", ".join(HERO._broken(findings))}): not shipped']}); best = None
    return {'doc': best, 'drawn': best is not None, 'attempts': sum(1 for s in log if s['stage'] in ('compose', 'correct', 'revise')), 'log': log, 'measured': findings}


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) < 3 or args[1] != '--out': raise SystemExit('usage: compose_lists.py <page.html> --out lists.json [--no-review]')
    with open(args[0], encoding='utf-8') as f: html = f.read()
    result = compose(html, args[0], model=os.environ.get('COMPOSE_MODEL') or None, review='--no-review' not in args)
    if result['doc']:
        with open(args[2], 'w', encoding='utf-8') as f: json.dump(result['doc'], f, indent=1, ensure_ascii=False)
    print(json.dumps({'drawn': result['drawn'], 'attempts': result['attempts'], 'concept': (result['doc'] or {}).get('note')}, ensure_ascii=False))
    raise SystemExit(0 if result['drawn'] else 1)
