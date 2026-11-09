#!/usr/bin/env python3
"""validate.py — is every Design DNA record what it claims to be? Standard library only.

Usage   python3 design_dna/validate.py          exit 0 and one line, or exit 1 and a list of what is wrong
        validate_record(record) -> [problems]    for one record already in memory (tests seed defects through this)
        validate_all() -> {id or '(library)': [problems]}

What is checked, per record:
  shape        design_dna/schema.json: required fields, types, enums. Read by the small interpreter below, which refuses
               a schema keyword it does not implement.
  files        every file pointer anywhere in the record ('lib/…', 'dna/…', 'design_dna/…', with or without '#/pointer')
               names a file that exists, and its pointer resolves inside that file; a recipe pointer names a recipe.
  evidence     the blueprint is this id's; `authored` means exactly "no raw capture"; a screenshot folder that exists
               for the id is registered; a capture date or pixel ratio is not stated without a file that shows it.
  pointers     every pointer under `evidence` / `matched` of a principle, a computed value or a need resolves inside
               the record to a value that is not null.
  fonts        delivery_face, delivery_class and delivery_fallback are what font_for in lib/render/render_bp.py returns.
  authored     an authored record claims nothing measured, has no principles and no derived needs.
  prose        a prose object holds exactly the text its pointer holds, or is withheld.
  source text  no heading, button or label text of a raw capture is in the record: no shared run of 60 characters, and
               no whole text of 12 characters or more.
  principles   derived by a rule that exists in build.py, under that rule's id, ids unique; temper tags point at them.
  stale        the sha256 of each input still matches.
And for the library: one record per blueprint, none without one, and the files on disk are what build.py writes today.
"""
import importlib.util, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCHEMA = 'design_dna/schema.json'
RUN = 60                                        # a shared run this long with a source text is a copy
MEASURED_CLAIMS = ('measured', 'measured-desktop', 'partial', 'present')
FILE_REF = re.compile(r'^(lib|dna|design_dna|docs)/[^#\s]+(#.*)?$')


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, filename))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


build = _load('design_dna_build', 'build.py')


# ── a JSON Schema interpreter for the keywords schema.json uses ───────────────────────────────────────────────────────
class SchemaError(Exception):
    pass


ANNOTATIONS = {'$schema', '$id', 'title', 'description', '$defs', '$comment'}
KEYWORDS = {'type', 'enum', 'const', 'pattern', 'minimum', 'maximum', 'required', 'properties', 'additionalProperties', 'items', 'minItems', '$ref'}


def _is(value, t):
    if t == 'null': return value is None
    if t == 'boolean': return isinstance(value, bool)
    if t == 'integer': return isinstance(value, int) and not isinstance(value, bool)
    if t == 'number': return isinstance(value, (int, float)) and not isinstance(value, bool)
    if t == 'string': return isinstance(value, str)
    if t == 'array': return isinstance(value, list)
    if t == 'object': return isinstance(value, dict)
    raise SchemaError('unknown type %r' % t)


def _same(a, b):
    if isinstance(a, bool) or isinstance(b, bool) or a is None or b is None: return a is b
    return a == b


def check_schema(value, schema, root, path='', out=None):
    out = [] if out is None else out
    unknown = set(schema) - KEYWORDS - ANNOTATIONS
    if unknown: raise SchemaError('schema keyword(s) not implemented by validate.py: %s (at %s)' % (', '.join(sorted(unknown)), path or '/'))
    if '$ref' in schema:
        ref = schema['$ref']
        if not ref.startswith('#/$defs/') or ref[8:] not in root.get('$defs', {}): raise SchemaError('unresolvable $ref %r' % ref)
        check_schema(value, root['$defs'][ref[8:]], root, path, out)
    where = path or '(record)'
    if 'type' in schema:
        types = schema['type'] if isinstance(schema['type'], list) else [schema['type']]
        if not any(_is(value, t) for t in types):
            out.append('%s: expected %s, found %s' % (where, ' or '.join(types), json.dumps(value, ensure_ascii=False)[:60])); return out
    if 'const' in schema and not _same(value, schema['const']): out.append('%s: must be %s' % (where, json.dumps(schema['const'])))
    if 'enum' in schema and not any(_same(value, e) for e in schema['enum']):
        out.append('%s: %s is not one of %s' % (where, json.dumps(value, ensure_ascii=False)[:60], json.dumps(schema['enum'])))
    if 'pattern' in schema and isinstance(value, str) and not re.search(schema['pattern'], value): out.append('%s: %r does not match %s' % (where, value[:80], schema['pattern']))
    if _is(value, 'number'):
        if 'minimum' in schema and value < schema['minimum']: out.append('%s: %s is below %s' % (where, value, schema['minimum']))
        if 'maximum' in schema and value > schema['maximum']: out.append('%s: %s is above %s' % (where, value, schema['maximum']))
    if isinstance(value, dict):
        for key in schema.get('required', []):
            if key not in value: out.append('%s: required field "%s" is missing' % (where, key))
        props = schema.get('properties', {}); extra = schema.get('additionalProperties', True)
        for key, sub in value.items():
            here = (path + '.' if path else '') + key
            if key in props: check_schema(sub, props[key], root, here, out)
            elif extra is False: out.append('%s: field not in the schema' % here)
            elif isinstance(extra, dict): check_schema(sub, extra, root, here, out)
    if isinstance(value, list):
        if len(value) < schema.get('minItems', 0): out.append('%s: needs at least %d item(s)' % (where, schema['minItems']))
        if 'items' in schema:
            for i, sub in enumerate(value): check_schema(sub, schema['items'], root, '%s[%d]' % (path, i), out)
    return out


# ── walking a record ─────────────────────────────────────────────────────────────────────────────────────────────────
def walk(node, path=''):
    """Every (path, value) in the record, containers included."""
    yield path, node
    if isinstance(node, dict):
        for k, v in node.items(): yield from walk(v, (path + '.' if path else '') + k)
    elif isinstance(node, list):
        for i, v in enumerate(node): yield from walk(v, '%s[%d]' % (path, i))


def squash(text):
    return re.sub(r'\s+', ' ', text).strip().lower()


class Context:
    """What every record is checked against; built once."""
    def __init__(self, root=None):
        self.root = root or ROOT
        self.schema = build.read_json(SCHEMA, self.root)
        self.blueprints = build.blueprint_ids(self.root)
        self.texts = build.all_source_texts(self.root)
        self.runs = {s[i:i + RUN] for s in map(squash, self.texts) for i in range(len(s) - RUN + 1)}
        self.whole = sorted({t for t in self.texts if len(t) >= build.NOTE_QUOTE_MIN})
        self.rules = {pid: (fn.__name__, tag) for pid, tag, fn in build.RULES}
        self.recipes = set(build.recipe_ids())


def check_file_ref(ref, ctx):
    """None when the file (and its pointer) is there, else what is wrong."""
    path, _, frag = ref.partition('#')
    full = os.path.join(ctx.root, path)
    if not os.path.exists(full): return 'no such file: %s' % path
    if not frag: return None
    if path == build.RECIPES: return None if frag in ctx.recipes else 'no recipe "%s" in %s' % (frag, path)
    if not path.endswith('.json'): return 'pointer into a file that is not JSON: %s' % ref
    try: build.resolve_file_pointer(ref, ctx.root)
    except KeyError as err: return str(err).strip('\'"')
    return None


def validate_record(rec, ctx=None):
    ctx = ctx or Context()
    out = check_schema(rec, ctx.schema, ctx.schema)
    if out: return out                                    # the checks below assume the shape
    rid = rec['id']; ev = rec['evidence']; authored = rec['status'] == 'authored'

    # files: anything that looks like a file pointer must be one
    for path, value in walk(rec):
        if isinstance(value, str) and FILE_REF.match(value):
            problem = check_file_ref(value, ctx)
            if problem: out.append('%s: %s' % (path, problem))
    for key in rec['built_from']:
        problem = check_file_ref(key, ctx) if FILE_REF.match(key) else 'not a file pointer'
        if problem: out.append('built_from["%s"]: %s' % (key, problem))

    # evidence: which files stand behind the record
    if ev['blueprint'] != '%s/%s.bp.json' % (build.BP_DIR, rid): out.append('evidence.blueprint: must be %s/%s.bp.json' % (build.BP_DIR, rid))
    if ev['raw'] is not None and ev['raw'] != '%s/%s.json' % (build.RAW_DIR, rid): out.append('evidence.raw: must be %s/%s.json or null' % (build.RAW_DIR, rid))
    if authored and ev['raw'] is not None: out.append('status: authored, yet a raw capture is listed')
    if not authored and ev['raw'] is None: out.append('status: %s needs a raw capture in evidence.raw' % rec['status'])
    shots = ev['screenshots']; files = shots['desktop'] + shots['mobile'] + shots['unclassified']
    on_disk = os.path.isdir(os.path.join(ctx.root, 'dna', rid))
    if on_disk and shots['dir'] != 'dna/' + rid: out.append('evidence.screenshots.dir: dna/%s exists and is not registered in design_dna/evidence.json' % rid)
    for f in files:
        if not shots['dir'] or not f.startswith(shots['dir'] + '/'): out.append('evidence.screenshots: %s is outside the registered folder' % f)
    src = rec['source']
    if src['captured_at'] is not None and not src.get('captured_at_source'): out.append('source.captured_at: a date needs captured_at_source, a file that shows it')
    if src['dpr'] is not None and not src.get('dpr_source'): out.append('source.dpr: a pixel ratio needs dpr_source, a file that shows it')
    if (src['viewport']['w'] is None) != (src['viewport']['w_source'] is None): out.append('source.viewport.w: a width and its source go together')
    if (src['viewport']['h'] is None) != (src['viewport']['h_source'] is None): out.append('source.viewport.h: a height and its source go together')
    if (src['url'] is None) != (src['url_source'] is None): out.append('source.url: a url and its source go together')

    # completeness: no claim without the evidence for it
    comp = rec['completeness']
    if comp['mobile'] != 'missing': out.append('completeness.mobile: "%s", but no record can hold a mobile capture yet' % comp['mobile'])
    if comp['screenshots'] == 'missing' and files: out.append('completeness.screenshots: "missing", yet screenshot files are listed')
    if comp['screenshots'] != 'missing' and not files: out.append('completeness.screenshots: "%s", yet no screenshot file is listed' % comp['screenshots'])
    if comp['screenshots'] == 'present' and not (shots['desktop'] and shots['mobile'] and src['captured_at'] and src['viewport']['w']):
        out.append('completeness.screenshots: "present" needs desktop and mobile files, a capture date and a viewport width')
    if authored:
        for key in sorted(comp):
            if comp[key] in MEASURED_CLAIMS: out.append('completeness.%s: "%s" on an authored record; nothing was measured' % (key, comp[key]))
        if rec['principles']: out.append('principles: an authored record cannot carry principles; they are derived from measurements')
        if rec['fits']['needs'] is not None: out.append('fits.needs: an authored record has no measured layout to derive needs from')
    for block in ('typography', 'composition', 'imagery'):
        want = 'authored' if authored else 'measured'
        if rec[block]['basis'] != want: out.append('%s.basis: "%s" on a record whose status is %s' % (block, rec[block]['basis'], rec['status']))

    # pointers into the record
    for path, node in walk(rec):
        if not isinstance(node, dict): continue
        for key in ('evidence', 'matched'):
            if path == '' and key == 'evidence': continue           # the top-level evidence block is files, not pointers
            if not isinstance(node.get(key), list): continue
            for p in node[key]:
                try: value = build.resolve_internal(rec, p)
                except KeyError: out.append('%s.%s: pointer "%s" does not resolve inside the record' % (path, key, p)); continue
                if value is None: out.append('%s.%s: pointer "%s" points at a null; a missing value is not evidence' % (path, key, p))

    # fonts: what ships is what the renderer says ships
    for level in build.LEVELS:
        lv = rec['typography'][level]
        if lv is None:
            if level not in rec['typography']['levels_missing']: out.append('typography.%s: null without a reason in levels_missing' % level)
            continue
        name, cls, missed = build.delivery(lv['source_face'])
        if lv['delivery_face'] != name: out.append('typography.%s.delivery_face: "%s", but font_for(%r) in %s returns "%s"' % (level, lv['delivery_face'], lv['source_face'], build.RENDERER, name))
        if lv['delivery_class'] != cls: out.append('typography.%s.delivery_class: "%s", but font_for returns "%s"' % (level, lv['delivery_class'], cls))
        if lv['delivery_fallback'] != missed: out.append('typography.%s.delivery_fallback: does not match font_for' % level)
        if authored != (lv['source']['raw'] is None): out.append('typography.%s.source.raw: %s' % (level, 'an authored level cannot cite a capture' if authored else 'a measured level must cite the capture'))

    # prose: carried, never written
    for path, node in walk(rec):
        if not (isinstance(node, dict) and node.get('kind') == 'prose'): continue
        if (node.get('text') is None) != (node.get('withheld') is not None): out.append('%s: a prose object holds its text or says why it is withheld, not both and not neither' % path)
        if node.get('text') is None: continue
        try: held = build.resolve_file_pointer(node['source'], ctx.root)
        except KeyError: continue                                    # already reported under files
        if held != node['text']: out.append('%s: text is not what %s holds' % (path, node['source']))

    # source text: third-party words stay out
    for path, value in walk(rec):
        if not isinstance(value, str): continue
        s = squash(value)
        if any(s[i:i + RUN] in ctx.runs for i in range(len(s) - RUN + 1)): out.append('%s: holds %d or more characters of a source heading, button or label' % (path, RUN))
        elif any(t in value for t in ctx.whole): out.append('%s: quotes a source heading, button or label' % path)

    # principles and what hangs off them
    seen = set()
    for i, p in enumerate(rec['principles']):
        if p['id'] in seen: out.append('principles[%d].id: "%s" appears twice' % (i, p['id']))
        seen.add(p['id'])
        if p['id'] not in ctx.rules: out.append('principles[%d].id: "%s" is not produced by any rule in build.py' % (i, p['id']))
        elif ctx.rules[p['id']][0] != p['rule']: out.append('principles[%d].rule: "%s" does not produce "%s"' % (i, p['rule'], p['id']))
    for i, t in enumerate(rec['fits']['temper']):
        if t['principle'] not in seen: out.append('fits.temper[%d]: principle "%s" is not in this record' % (i, t['principle']))
        elif ctx.rules.get(t['principle'], (None, None))[1] != t['tag']: out.append('fits.temper[%d]: tag "%s" is not the tag of "%s"' % (i, t['tag'], t['principle']))
    for kind in rec['fits']['also']:
        if kind in rec['fits']['kinds']: out.append('fits.also: "%s" is already in kinds' % kind)

    # stale: an input changed after the record was built
    for key, digest in sorted(rec['built_from'].items()):
        path, _, frag = key.partition('#')
        try: now = build.sha256_json(build.resolve_file_pointer(key, ctx.root)) if frag else build.sha256_file(path, ctx.root)
        except (KeyError, OSError): continue                         # already reported under files
        if now != digest: out.append('built_from["%s"]: the input has changed since the record was built; run python3 design_dna/build.py' % key)
    wanted = {ev['blueprint'], build.ptr(build.EVIDENCE, 'references', rid)} | ({ev['raw']} if ev['raw'] else set())
    if set(rec['built_from']) != wanted: out.append('built_from: must name exactly %s' % ', '.join(sorted(wanted)))
    return out


def load_records(root=None):
    folder = os.path.join(root or ROOT, build.OUT_DIR); out = {}
    for name in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
        if name.endswith('.json'):
            with open(os.path.join(folder, name), encoding='utf-8') as f: out[name[:-5]] = json.load(f)
    return out


def validate_all(root=None):
    ctx = Context(root); records = load_records(ctx.root); report = {}; lib = []
    for rid, rec in records.items():
        problems = validate_record(rec, ctx)
        if rec.get('id') != rid: problems.insert(0, 'id: the file is named %s.json' % rid)
        if problems: report[rid] = problems
    for rid in ctx.blueprints:
        if rid not in records: lib.append('no record for blueprint %s' % rid)
    for rid in records:
        if rid not in ctx.blueprints: lib.append('record %s has no blueprint' % rid)
    try: lib += ['%s is not what build.py writes today; run python3 design_dna/build.py' % p for p in build.stale(ctx.root)]
    except build.BuildError as err: lib.append('build.py cannot build from the current inputs: %s' % err)
    if lib: report['(library)'] = lib
    return report


def main():
    try: report = validate_all()
    except SchemaError as err:
        print('design_dna: %s' % err); return 1
    if not report:
        print('design_dna: %d records valid' % len(load_records())); return 0
    total = sum(len(v) for v in report.values())
    print('design_dna: %d problem%s' % (total, '' if total == 1 else 's'))
    for rid in sorted(report):
        for problem in report[rid]: print('  %s: %s' % (rid, problem))
    return 1


if __name__ == '__main__':
    sys.exit(main())
