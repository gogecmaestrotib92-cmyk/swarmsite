"""compose_words.py — a model decides how the sections that are words only are drawn; this file keeps it honest.

The same loop as for the lists (compose_lists.py): the model sees each section of words as the template drew it and what
it holds, answers with a words composition (words.py) and nothing else; the validator's reasons go back once; the drawn
sections are pictured and the whole page graded by the contract, and what the composition newly breaks goes back once
with the pictures; a composition that still breaks the page is refused whole.

  compose(page_html, page_path, model=None, review=True, ask=None) → {'doc', 'drawn', 'attempts', 'log', 'measured'}
Needs ANTHROPIC_API_KEY for the default model call. Every call is charged to the job budget when SWARM_JOB_DIR is set."""
import json, os, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'lib', 'swarm')); sys.path.insert(0, os.path.join(ROOT, 'lib'))
import compose as HERO
import compose_lists as LISTED
import validate as V
import words as WORDS

SYSTEM = """You are the art director of a small studio. Parts of this page are composed already. What is left are the sections that are words only — a price list, a menu, opening hours, a paragraph under its heading — and a page-building template drew every one of them the same way: the heading in a narrow column, the rows beside it. Several of those in a row is what makes a page read as a form to fill in. You give each a form of its own. The words are fixed: you choose a form, you do not write.

How words-only sections read as designed:
- They are not all the same. Neighbours never take the same form on the same ground; the page gets a rhythm: a large quiet one, a short loud one, a dense one.
- poster: the heading very large across the width, what it introduces set under it to one side. For a section whose heading is the point.
- columns: the heading on top and the rows in two columns, like a printed menu. For a list of four rows or more.
- statement: everything centred and short, the heading large. For a section that says one thing and has a button — up to 280 characters and two rows.
- A ground of colour breaks a run of pale sections: "accent" for the one section a visitor should not scroll past (once or twice a page, never two neighbours), "ink" for a dark pause, "alt" for a quiet shift. A page of nothing but coloured grounds is as flat as a page with none.
- A section you leave out stays as the template drew it; leave one out only when its form is right as it is.

THE FORMAT — call write_words with "concept" (one sentence: the rhythm these sections give the page) and "words": one object per section you recompose:
- "section": its id, as given. "form": poster | columns | statement.
- "title": md | lg | xl — the heading's size. "ground": band | accent | ink | alt (band: the ground it already has).
- "side": left | right — for a poster, where what the heading introduces is set under it.
A composition that breaks a rule is refused whole and you are told why."""

ENTRY = {"type": "object", "required": ["section", "form"], "properties": {
    "section": {"type": "string"}, "form": {"type": "string", "enum": list(WORDS.FORMS)}, "title": {"type": "string", "enum": list(WORDS.TITLES)},
    "ground": {"type": "string", "enum": list(WORDS.GROUNDS)}, "side": {"type": "string", "enum": list(WORDS.SIDES)}}}
TOOL = {"name": "write_words", "description": "How the sections that are words only are drawn.", "input_schema": {"type": "object", "required": ["concept", "words"], "properties": {
    "concept": {"type": "string", "description": "one sentence: the rhythm these sections give the page"},
    "words": {"type": "array", "minItems": 1, "maxItems": 12, "items": ENTRY}}}}
MAX_PICTURED = 6


def brief(page_html):
    """What may be recomposed, as text: every section of words with what it holds, in the order of the page. → (text, [ids])"""
    lines, ids = ['THE PAGE, top to bottom (sections of words you may recompose are marked ▸):'], []
    page = WORDS.readable(page_html)
    for sec in WORDS.SECTIONS.sections(page_html):
        known = page.get(sec['id']); kind = next((k for k in sec['classes'] if k not in ('sec', 'compact', 'pc', 'lc', 'wc') and not k.startswith(('band-', 'pc-', 'lc-', 'wc-'))), 'section')
        if known and not isinstance(known[1], str):
            c = known[1]; ids.append(sec['id'])
            lines.append(f'▸ "{sec["id"]}" — {kind}, on the {c["band"]} band. Heading: "{c["heading"][:90]}". {c["chars"]} characters, {c["rows"]} rows' + (f', {c["buttons"]} button(s)' if c['buttons'] else '') + '.')
        else: lines.append(f'  "{sec["id"] or "-"}" — {kind}')
    return '\n'.join(lines), ids


SAME = {'ink': 'dark', 'accent': 'accent', 'alt': 'alt'}   # a ground and the band that already is that ground


def _to_doc(answer, page=None):
    """The document from the flat tool answer. Asking for the ground a section already stands on is asking for nothing:
    it is left out, as is a "side" on a form that has none. Everything else wrong is left for the validator to name."""
    words = answer.get('words')
    if isinstance(words, str) and words.strip()[:1] == '[':
        try: words = json.loads(words)
        except ValueError: pass
    if isinstance(words, list):   # "side" belongs to the poster: on another form it is not part of what was asked for
        stands = lambda w: (page or {}).get(w.get('section'), (None, {}))[1]
        same = lambda w: isinstance(stands(w), dict) and SAME.get(w.get('ground')) == stands(w).get('band')
        words = [{k: v for k, v in w.items() if v is not None and not (k == 'side' and w.get('form') != 'poster') and not (k == 'ground' and same(w))} if isinstance(w, dict) else w for w in words]
    return {'ir': V.VERSION, 'note': str(answer.get('concept') or '')[:300], 'words': words}


def compose(page_html, page_path, model=None, review=True, ask=None):
    """Compose the sections of words, correct once, look and revise once. Returns the last document that validates and breaks nothing, or none."""
    if ask is None:
        import agents; ask = agents.ask
    text, ids = brief(page_html); log, findings, best = [], None, None
    if not ids: return {'doc': None, 'drawn': False, 'attempts': 0, 'log': [{'stage': 'skip', 'errors': ['the page has no section of words that can be recomposed']}], 'measured': None}
    material = [{"type": "text", "text": text}]
    try:
        shots = LISTED.section_shots(page_path, ids[:MAX_PICTURED]) if review else {}
        for sid in ids[:MAX_PICTURED]:
            if sid in shots: material += [{"type": "text", "text": f'SECTION "{sid}" AS THE TEMPLATE DREW IT:'}, HERO._image_block(shots[sid], 900)]
    except Exception as e: material.append({"type": "text", "text": f'(the sections could not be pictured: {str(e)[:80]})'})

    def attempt(stage, extra):
        answer = ask(SYSTEM, material + extra + [{"type": "text", "text": "Call write_words."}], TOOL, model=model, max_tokens=2500)
        if not isinstance(answer, dict):
            entry = {'stage': stage, 'errors': ['no composition returned']}; log.append(entry); return None, ['none'], entry
        doc = _to_doc(answer, WORDS.readable(page_html)); errors = WORDS.validate(doc, page_html)
        entry = {'stage': stage, 'concept': doc['note'], 'errors': [f"{e['code']} {e['at']}: {e['message']}" for e in errors], **({'refused': doc['words']} if errors else {})}; log.append(entry)
        return doc, errors, entry

    doc, errors, entry = attempt('compose', [])
    if errors and doc is not None:
        doc, errors, entry = attempt('correct', [{"type": "text", "text": "YOUR PREVIOUS COMPOSITION WAS REFUSED:\n" + json.dumps(doc['words'], ensure_ascii=False) + "\nReasons:\n" + '\n'.join('- ' + e for e in entry['errors'][:12]) + "\nKeep the idea; fix exactly these."}])
    if doc is not None and not errors: best = doc
    if best:
        folder = os.path.dirname(os.path.abspath(page_path))
        def look_at(candidate):
            page, _ = WORDS.transplant(page_html, candidate)
            with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8', dir=folder) as f: f.write(page); drawn = f.name
            try:
                pictures = LISTED.section_shots(drawn, [w['section'] for w in candidate['words']][:MAX_PICTURED]) if review else {}
                found = HERO.measured(drawn)
            finally: os.unlink(drawn)
            return pictures, {k: v for k, v in found.items() if k not in baseline}
        try:
            baseline = HERO.measured(page_path)
            pictures, findings = look_at(best); entry['measured'] = findings
            if review:
                look = [{"type": "text", "text": "YOUR SECTIONS, AS DRAWN:\n" + json.dumps(best['words'], ensure_ascii=False)}]
                for sid, path in pictures.items(): look += [{"type": "text", "text": f'SECTION "{sid}":'}, HERO._image_block(path, 900)]
                must = {k: v for k, v in findings.items() if any(b in k for b in HERO.BREAKING)}; other = {k: v for k, v in findings.items() if k not in must}
                if must: look.append({"type": "text", "text": "MEASURED ON THIS RENDER — your sections break these; fix them, or none of it is shipped:\n" + '\n'.join(f'- {k}: {v}' for k, v in must.items())})
                if other: look.append({"type": "text", "text": "ALSO MEASURED — yours to weigh:\n" + '\n'.join(f'- {k}: {v}' for k, v in other.items())})
                look.append({"type": "text", "text": "Look at them as the art director. Is any section half empty, or a heading too large or too small for what follows it? Do two neighbours look the same? Is a coloured ground on the section that deserves it? "
                                                        "Return the sections you would ship: revised where the pictures or the measurements show a problem, unchanged if you would ship this."})
                revised, revised_errors, second = attempt('revise', look)
                if revised is not None and not revised_errors:
                    _, revised_findings = look_at(revised); second['measured'] = revised_findings
                    if HERO._standing(revised_findings) > HERO._standing(findings): second['errors'] = ['revision measured worse than the first composition: kept the first']
                    else: best, findings = revised, revised_findings
        except Exception as e:
            log.append({'stage': 'look', 'errors': ['not measured: ' + str(e)[:160]]}); best = None   # a ground of colour changes what text stands on: unmeasured, it is not shipped
        if best and HERO._broken(findings):
            log.append({'stage': 'refuse', 'errors': [f'the sections break the page on the render ({", ".join(HERO._broken(findings))}): not shipped']}); best = None
    return {'doc': best, 'drawn': best is not None, 'attempts': sum(1 for s in log if s['stage'] in ('compose', 'correct', 'revise')), 'log': log, 'measured': findings}


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) < 3 or args[1] != '--out': raise SystemExit('usage: compose_words.py <page.html> --out words.json [--no-review]')
    with open(args[0], encoding='utf-8') as f: html = f.read()
    result = compose(html, args[0], model=os.environ.get('COMPOSE_MODEL') or None, review='--no-review' not in args)
    if result['doc']:
        with open(args[2], 'w', encoding='utf-8') as f: json.dump(result['doc'], f, indent=1, ensure_ascii=False)
    print(json.dumps({'drawn': result['drawn'], 'attempts': result['attempts'], 'concept': (result['doc'] or {}).get('note')}, ensure_ascii=False))
    raise SystemExit(0 if result['drawn'] else 1)
