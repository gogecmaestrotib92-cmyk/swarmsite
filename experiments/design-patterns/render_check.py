"""Isolated dry-run adapter; never changes source artifacts or deploys."""
import argparse
import base64
import copy
import io
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'lib'))
from visual_quality import empty_visual
from PIL import Image

CATALOG = json.loads(Path(__file__).with_name('catalog.json').read_text())

class Node:
    def __init__(self, tag='', attrs=()): self.tag, self.attrs, self.children = tag, dict(attrs), []
    def classes(self): return set(self.attrs.get('class', '').split())
    def text(self): return ''.join(x if isinstance(x, str) else x.text() for x in self.children)
    def find(self, pred):
        out = []
        if pred(self): out.append(self)
        for child in self.children:
            if isinstance(child, Node): out.extend(child.find(pred))
        return out

class Tree(HTMLParser):
    void = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
    def __init__(self): super().__init__(convert_charrefs=True); self.root = Node(); self.stack = [self.root]
    def handle_starttag(self, tag, attrs):
        n=Node(tag,attrs); self.stack[-1].children.append(n)
        if tag not in self.void: self.stack.append(n)
    def handle_startendtag(self, tag, attrs): self.stack[-1].children.append(Node(tag,attrs))
    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, 0, -1):
            if self.stack[i].tag == tag: self.stack = self.stack[:i]; return
    def handle_data(self, data): self.stack[-1].children.append(data)

def norm(value): return ' '.join(str(value or '').split())
def sections(tree): return tree.root.find(lambda n: n.tag == 'section' and n.attrs.get('id'))
def byid(tree, ident):
    hits = [x for x in sections(tree) if x.attrs.get('id') == ident]
    return hits[0] if len(hits)==1 else None

def rows_for(beat):
    kind = beat['type']
    if kind == 'features': return [(str(x.get('title') or ''), str(x.get('body') or '')) for x in beat['features']]
    if kind == 'facts': return [(str(x[0]), str(x[1])) for x in beat['facts']]
    return [(str(x[0]) if len(x)<2 else f'{x[1]} · {x[0]}', str(x[2]) if len(x)>2 else '') for x in beat['cells']]

def rendered_rows(section, container_class):
    containers = section.find(lambda n: container_class in n.classes())
    if len(containers) != 1: return None
    rows=[]
    for li in containers[0].find(lambda n:n.tag=='li'):
        columns=[x for x in li.children if isinstance(x,Node) and x.tag in ('b','span')]
        rows.append((norm(columns[0].text()) if columns else '', norm(columns[1].text()) if len(columns)>1 else ''))
    return rows

def links(tree):
    return sorted((n.attrs.get('href',''),norm(n.text())) for n in tree.root.find(lambda n:n.tag=='a'))

def preflight(pattern, direction, beat, images, bp):
    errors=[]
    if bp.get('class') != direction.get('kind'): errors.append('blueprint class does not match site kind')
    if beat.get('type') not in pattern['allowed_beat_types']: errors.append('unsupported beat type')
    if direction.get('kind') not in pattern['allowed_site_kinds']: errors.append('unsupported site kind')
    try: rows=rows_for(beat)
    except (KeyError, IndexError, TypeError, AttributeError): return errors+['malformed items']
    count=pattern['item_count'];
    if not count['min']<=len(rows)<=count['max']: errors.append('item count outside conservative bounds')
    if any(not norm(a) for a,_ in rows): errors.append('empty item title')
    if pattern['move']=='marquee':
        if beat.get('image'): errors.append('text-only marquee cannot replace explicitly assigned image')
        if any(len(a.split())>pattern['text']['max_title_words'] or len((a+' '+b).split())>pattern['text']['max_combined_words'] for a,b in rows): errors.append('text too long for actual marquee')
    else:
        if any(not isinstance(f,dict) or f.get('image') for f in beat.get('features',[])): errors.append('individual feature images require another layout')
        img=images.get(beat.get('image'))
        if not img or img.get('shot') is not True or not img.get('data') or empty_visual(img): errors.append('missing or empty assigned screenshot')
        else:
            try:
                with Image.open(io.BytesIO(base64.b64decode(img['data'].split(',',1)[1]))) as im: w,h=im.size
                a=pattern['asset'];ratio=w/max(1,h)
                if w<a['minimum_pixel_width'] or not a['aspect_ratio_min']<=ratio<=a['aspect_ratio_max']: errors.append('screenshot dimensions unsuitable')
            except Exception: errors.append('unreadable screenshot')
    return errors

def render(folder, bp, out):
    r=subprocess.run([os.environ.get('PYTHON',sys.executable),str(ROOT/'lib/render/render_bp.py'),str(folder),bp,str(out)],cwd=ROOT,capture_output=True,text=True,timeout=120)
    if r.returncode: raise RuntimeError('renderer failed: '+r.stderr[-300:])
    t=Tree();t.feed(out.read_text());return t

def check(slug_dir, bp_id, beat_id, pattern_id, version):
    if any(hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=digest for path,digest in CATALOG['engine_file_sha256'].items()): return {'accepted':False,'reason':'engine revision mismatch; revalidate catalog'}
    p=next((x for x in CATALOG['patterns'] if x['id']==pattern_id and x['version']==version),None)
    if not p:return {'accepted':False,'reason':'unknown pattern id/version'}
    directory=Path(slug_dir);d=json.loads((directory/'direction.json').read_text());imgs=json.loads((directory/'images.json').read_text())
    bp=json.loads((ROOT/'lib/blueprints'/f'{bp_id}.bp.json').read_text()) if bp_id.isascii() and bp_id.replace('-','').isalnum() and (ROOT/'lib/blueprints'/f'{bp_id}.bp.json').is_file() else {}
    matches=[x for x in d.get('beats',[]) if x.get('id')==beat_id]
    if len(matches)!=1:return {'accepted':False,'reason':'beat id missing or ambiguous'}
    beat=matches[0]; errors=preflight(p,d,beat,{i.get('id'):i for i in imgs},bp)
    if p.get('allowed_blueprints') and bp_id not in p['allowed_blueprints']: errors.append('pattern not available for this blueprint')
    if errors:return {'accepted':False,'reason':'; '.join(errors)}
    with tempfile.TemporaryDirectory(prefix='swarm-pattern-eval-') as temp:
        temp=Path(temp); base=temp/'base'; candidate=temp/'candidate';base.mkdir();candidate.mkdir()
        for name in ('assets.json','brief.json','inventory.json','images.json','hero.mp4'):
            if (directory/name).is_file():
                for dst in (base,candidate): shutil.copy2(directory/name,dst/name)
        (base/'direction.json').write_text(json.dumps(d,ensure_ascii=False));trial=copy.deepcopy(d);target=next(x for x in trial['beats'] if x['id']==beat_id);target.setdefault('ui',{})['move']=p['move'];(candidate/'direction.json').write_text(json.dumps(trial,ensure_ascii=False))
        original=render(base,bp_id,base/'render.html');result=render(candidate,bp_id,candidate/'render.html');old,new=byid(original,beat_id),byid(result,beat_id)
        if old is None or new is None:return {'accepted':False,'reason':'target section absent or ambiguous in real renderer'}
        if p['expected_render']['section_class'] not in new.classes():return {'accepted':False,'reason':'renderer chose a different component or fallback'}
        if rendered_rows(new,p['expected_render']['item_container']) != [(norm(a),norm(b)) for a,b in rows_for(beat)]:return {'accepted':False,'reason':'renderer changed or hid a content item'}
        for field in ('h2','lede','label'):
            if norm(beat.get(field)) and norm(beat[field]) not in norm(new.text()):return {'accepted':False,'reason':f'target {field} missing'}
        old_media=[n.attrs.get('src') for n in old.find(lambda x:x.tag in ('img','source')) if n.attrs.get('src')]
        if p['move']=='marquee' and old_media:return {'accepted':False,'reason':'text-only marquee would remove target media'}
        if p['move']=='story':
            expected=next(i['data'] for i in imgs if i.get('id')==beat.get('image'))
            if any(src!=expected for src in old_media):return {'accepted':False,'reason':'story would remove other target media'}
            actual=[n.attrs.get('src') for n in new.find(lambda x:x.tag=='img')]
            if actual!=[expected]:return {'accepted':False,'reason':'assigned screenshot not shown exactly once'}
        if links(original)!=links(result):return {'accepted':False,'reason':'renderer changed or lost link destinations/labels'}
        old_ids=[n.attrs['id'] for n in sections(original)];new_ids=[n.attrs['id'] for n in sections(result)]
        if old_ids!=new_ids:return {'accepted':False,'reason':'renderer changed section identities/order'}
        # Compare unaffected sections, not global page text: marquee deliberately
        # repeats its track while keeping one accessible copy in the static list.
        for ident in old_ids:
            if ident==beat_id:continue
            a,b=byid(original,ident),byid(result,ident)
            if a is None or b is None or norm(a.text())!=norm(b.text()):return {'accepted':False,'reason':f'unrelated section {ident} changed text'}
            media=lambda section: [(n.tag,n.attrs.get('src',''),n.attrs.get('poster','')) for n in section.find(lambda n:n.tag in ('img','video','source'))]
            if media(a)!=media(b):return {'accepted':False,'reason':f'unrelated section {ident} changed media'}
        return {'accepted':True,'pattern':p['id'],'version':p['version'],'beat':beat_id,'blueprint':bp_id,'fallback':p['fallback'],'limitations':'Dry run checks structure and links; it is not semantic, visual, accessibility or production approval.'}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('slug');ap.add_argument('blueprint');ap.add_argument('beat');ap.add_argument('pattern');ap.add_argument('--version',type=int,default=1);a=ap.parse_args()
    try: print(json.dumps(check(a.slug,a.blueprint,a.beat,a.pattern,a.version),ensure_ascii=False))
    except Exception as e: print(json.dumps({'accepted':False,'reason':'validation error: '+str(e)},ensure_ascii=False));sys.exit(1)
