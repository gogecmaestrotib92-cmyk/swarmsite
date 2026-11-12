#!/usr/bin/env python3
"""import_template.py <slug> [<slug> …] [--from DIR] [--force] — bring a finished reference template into the library.

Copies `render.py`, `NOTES.md` and (when it exists) `needs.json` from the research folder into `lib/templates/<slug>/`,
unchanged, then holds the copy to what every template in the library must keep (lib/templates/registry.py `audit`):
a pure function with no reach outside, every fixture client in tests/fixtures/templates/ renders to one page with one
h1, nothing reading 'None'/'undefined', under 50 ms, and every media path of the data can be re-based. A template that
fails is not left in the library. Nothing else of the research folder is copied (its `out/`, `pairs/`, `ref/` hold the
reference's own imagery).

The research folder is not in git. It is looked for at --from, then $SWARMSITE_TEMPLATES_SRC, then
`bench/runs/_research/templates` of this checkout, then of the main checkout when this is a worktree.

A template without needs.json is imported but is NOT offered to clients until it has one (selection reads needs.json).

RECIPE — importing one research template (one agent, one template, one branch and PR; several can run side by side)
  0. Start from a fresh worktree of origin/main (or the template stack until it is merged). Never write in the research
     folder: what a template lacks is reported back to whoever owns the research copy, not fixed there.
  1. Read <research>/<slug>/NOTES.md and needs.json. The template is ready only if NOTES says it was looked at, at 1440
     and 390, on at least two clients.
  2. python3 scripts/import_template.py <slug>            (--force replaces a copy already in lib/templates/<slug>)
     It copies render.py, NOTES.md and needs.json, unchanged, and runs `audit` on every fixture client:
       - render(d) is a pure function: none of registry._FORBIDDEN imported (network, files, processes, clock, chance),
         the data it is given unchanged, two renders of the same data byte for byte the same;
       - each client renders to a whole page with exactly one h1, no 'None' / 'undefined', under 50 ms;
       - every media path of the data can be re-based (registry.rebase);
       - needs.json, when present, is a JSON object.
     A refused import changes nothing; with --force the old copy is kept until the new one has passed.
  3. needs.json in the strict form: python3 scripts/normalise_needs.py lib/templates/<slug>/needs.json
     It must name `niche` with the fixed words of lib/templates/needs.schema.json (software, app, restaurant, hotel,
     clinic, law, service, shop, school, person, corporate, nonprofit, venue). Without that, the template is never
     offered. List what the script says it could not carry over in the PR.
  4. The gate on its own fixtures: python3 -m pytest tests/test_templates_registry.py tests/test_templates_select.py -q
  5. The stress run: python3 lib/templates/stress.py <slug> --client tests/fixtures/templates/<client>.json --out DIR --json
     for each fixture client of its niche (tallyfern / quillmoor for software, casaolmo for a restaurant; add a made-up
     one for a niche that has none, never a real client's data). Every variant (plans 1/3/5, features 2/9, steps 1/6,
     a 12-word h1, a 40-character button, no faq, no photographs) must pass the gate (lib/qa/template_gate.mjs:
     sideways, errors, distorted, h1, legible, overlap). Paste the table into the PR. A variant that fails is a defect
     of the template: report it, do not patch render.py in the library.
  6. npm test and scripts/livetest.sh 80, then the PR: the template, its stress table, what normalise_needs lost.
     Never merge or deploy.
"""
import json
import shutil
import subprocess
import sys
import importlib.util
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIB = ROOT / 'lib' / 'templates'
FIXTURES = ROOT / 'tests' / 'fixtures' / 'templates'
FILES = ('render.py', 'NOTES.md', 'needs.json')
REL = Path('bench') / 'runs' / '_research' / 'templates'


def registry():
    spec = importlib.util.spec_from_file_location('swarmsite_templates_registry', LIB / 'registry.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def source(arg=None):
    cands = [arg, os.environ.get('SWARMSITE_TEMPLATES_SRC'), ROOT / REL]
    try:                                                         # a worktree: the main checkout holds the untracked folder
        common = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', '--path-format=absolute', '--git-common-dir'],
                                capture_output=True, text=True, timeout=10).stdout.strip()
        if common:
            cands.append(Path(common).parent / REL)
    except (OSError, subprocess.SubprocessError):
        pass
    for c in cands:
        if c and Path(c).is_dir():
            return Path(c)
    raise SystemExit('research folder not found; pass --from DIR')


def clients():
    return {p.stem: json.loads(p.read_text(encoding='utf-8')) for p in sorted(FIXTURES.glob('*.json'))}


def bring(slug, src, R, force=False):
    """-> (ok, lines)"""
    if not R.SLUG.match(slug):
        return False, ['not a slug: %r' % slug]
    frm, to = src / slug, LIB / slug
    if not (frm / 'render.py').is_file():
        return False, ['%s has no render.py' % frm]
    if to.exists() and not force:
        return False, ['lib/templates/%s exists already; --force replaces it' % slug]
    kept = None
    if to.exists():                                               # keep the old copy until the new one has passed
        kept = to.with_name(to.name + '.replaced')
        if kept.exists():
            shutil.rmtree(kept)
        to.rename(kept)
    to.mkdir(parents=True)
    copied = []
    for f in FILES:
        if (frm / f).is_file():
            shutil.copyfile(frm / f, to / f)
            copied.append(f)
    R._modules.pop(str(to), None)
    bad = R.audit(slug, clients())
    if (to / 'needs.json').is_file() and R.needs(slug) is None:
        bad.append('needs.json is not a JSON object')
    if bad:
        shutil.rmtree(to)
        if kept:
            kept.rename(to)
        return False, ['refused, nothing changed:'] + ['  ' + b for b in bad]
    if kept:
        shutil.rmtree(kept)
    lines = ['copied ' + ', '.join(copied)]
    if 'NOTES.md' not in copied:
        lines.append('no NOTES.md in the research folder')
    if 'needs.json' not in copied:
        lines.append('no needs.json: in the library, but not offered to clients until it has one')
    return True, lines


def main(argv):
    args, src_arg, force = [], None, False
    it = iter(argv)
    for a in it:
        if a == '--from':
            src_arg = next(it, None)
        elif a == '--force':
            force = True
        elif a.startswith('-'):
            raise SystemExit(__doc__)
        else:
            args.append(a)
    if not args:
        raise SystemExit(__doc__)
    src, R, fail = source(src_arg), registry(), 0
    for slug in args:
        ok, lines = bring(slug, src, R, force)
        print(('✓ ' if ok else '✗ ') + slug + ': ' + lines[0])
        for ln in lines[1:]:
            print('  ' + ln)
        fail |= not ok
    return int(fail)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
