"""rerender.py <evidence dir> <out dir> — draw every saved plan again with the scenes as they now are (no model call)."""
import glob, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _evidence as E, scenes as S
src, out = sys.argv[1], sys.argv[2]; images = {i['id']: i for i in (E.J(src, 'images.json') or []) if i.get('data')}
for tag in sorted({re.search(r'plan-(\w)-', f).group(1) for f in glob.glob(os.path.join(out, 'plan-*-*.json'))}):
    plan = json.load(open(sorted(glob.glob(os.path.join(out, f'plan-{tag}-*.json')))[-1], encoding='utf-8'))
    open(os.path.join(out, f'page-{tag}.html'), 'w', encoding='utf-8').write(S.page(plan, images)); print(out, tag)
