"""QA agent — runs the built page in headless Chrome at 1440x900 and 390x844 and checks the rules in
lib/rules/rhythm.md + copy.md. Rule ids mirror taste-skill's checker where we adopted them.
Usage: python3 lib/qa/check.py v3/c1.html [--json]"""
import sys, os, re, json, subprocess, tempfile, html as H

BANNED = ['seamless', 'effortless', 'cutting-edge', 'unlock', 'elevate', 'supercharge', 'reimagine', 'next-generation', 'game-changing',
          'powerful', 'robust', 'easy', 'simple', 'quick', 'very', 'just', 'really', 'significantly', 'typically', 'generally', 'learn more', 'discover', 'explore']
PROBE = r"""
<script>
window.__qa = async function(){
  const H = innerHeight, W = innerWidth;
  const secs=[...document.querySelectorAll('main > section, body > section, body > nav, body > footer, section.hero')].filter((s,i,a)=>a.indexOf(s)===i);
  const out={H,W,scrollW:document.documentElement.scrollWidth,sections:[],h1:(document.querySelector('h1')||{}).textContent||'',buttons:[...document.querySelectorAll('a.btn,.pillb,.cta')].map(b=>(b.getAttribute('aria-label')||(()=>{const c=b.cloneNode(true);c.querySelectorAll('[aria-hidden="true"]').forEach(x=>x.remove());return c.textContent})()).trim()).filter(Boolean),links:document.querySelectorAll('footer a, footer li').length};
  for(const s of secs){ if(s.tagName==='NAV') continue; const r=s.getBoundingClientRect(); const top=r.top+scrollY;
    const cl=s.cloneNode(true); cl.querySelectorAll('.card,.marquee,.dcard .card,.sw-hud').forEach(x=>x.remove()); document.body.appendChild(cl); const words=(cl.innerText||'').split(/\s+/).filter(Boolean).length; cl.remove();
    const moves=s.querySelectorAll('[data-move]').length;
    const held=el=>{for(let n=el.parentElement;n&&n!==document.body;n=n.parentElement){if(getComputedStyle(n).overflowX!=='visible'){const b=n.getBoundingClientRect();if(b.left>=-1&&b.right<=W+1)return true}}return false};  /* cut or scrolled by a box that is itself on screen: a strip, a crop, a row that slides — not a spill */
    const ovEls=[...s.querySelectorAll('*')].filter(el=>!el.closest('.marquee,.sw-hud,#sw-intro,[aria-hidden="true"]') && !held(el) && el.getClientRects().length && (()=>{const b=el.getBoundingClientRect();return b.width>0 && (b.right>W+1||b.left<-1)})()); const over=ovEls.length; const overEls=ovEls.slice(0,4).map(el=>el.tagName.toLowerCase()+(el.className&&typeof el.className==='string'?'.'+el.className.split(' ')[0]:'')+'@'+Math.round(el.getBoundingClientRect().right));
    const heads=[...s.querySelectorAll('h1,h2')].map(h=>h.textContent.trim());
    out.sections.push({id:s.id||s.className.split(' ')[0]||s.tagName,top:Math.round(top),h:Math.round(r.height),screens:+(r.height/H).toFixed(2),words,moves,over,heads,overEls}); }
  const t=document.createElement('pre'); t.id='__qa'; t.textContent=JSON.stringify(out); document.body.appendChild(t);
};
setTimeout(()=>window.__qa(), 2500);
</script>
"""

def chrome_bin():
    """System Chrome if present, else Playwright's bundled Chromium (the worker image), else whatever is on PATH."""
    for c in (os.environ.get('CHROME_PATH'), '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser'):
        if c and os.path.exists(c): return c
    try:
        out = subprocess.run(['node', '-e', "console.log(require('playwright').chromium.executablePath())"], capture_output=True, text=True, timeout=20, cwd=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))).stdout.strip()
        if out and os.path.exists(out): return out
    except Exception: pass
    return 'google-chrome'

def run(path, w, h):
    src = open(path).read()
    src = src.replace('document.getElementById(\'sw-start\').onclick=()=>go(false);', 'document.getElementById("sw-start").onclick=()=>go(false);setTimeout(()=>go(true),200);')
    src = src.replace('</body>', PROBE + '</body>')
    tmp = tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, dir='/tmp'); tmp.write(src); tmp.close()
    dom = subprocess.run([chrome_bin(), '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars', f'--window-size={w},{h}',
                          '--virtual-time-budget=9000', '--dump-dom', 'file://' + tmp.name], capture_output=True, text=True, timeout=90).stdout
    m = re.search(r'<pre id="__qa">(.*?)</pre>', dom, re.S)
    os.unlink(tmp.name)
    return json.loads(H.unescape(m.group(1))) if m else None

def check(path):
    findings = []
    text = re.sub(r'<script.*?</script>|<style.*?</style>', '', open(path).read(), flags=re.S)
    plain = re.sub(r'<[^>]+>', ' ', text).lower()
    for b in BANNED:
        n = len(re.findall(r'\b' + re.escape(b) + r'\b', plain))
        if n: findings.append(('banned-words', 'med', f'"{b}" ×{n}'))
    for w, h in ((1440, 900), (390, 844)):
        d = run(path, w, h)
        if not d: findings.append(('probe', 'high', f'no QA data at {w}')); continue
        tag = f'@{w}'
        if d['scrollW'] > d['W'] + 1: findings.append(('spill', 'high', f'{tag} page scrolls sideways: {d["scrollW"]}px > {d["W"]}px'))
        secs = d['sections']
        hero = next((s for s in secs if 'hero' in s['id']), None)
        if hero:
            nxt = [s for s in secs if s['top'] > hero['top'] + 10]
            if nxt and nxt[0]['top'] < d['H'] - 4: findings.append(('hero-fill', 'high', f'{tag} section "{nxt[0]["id"]}" shows on the first screen at y={nxt[0]["top"]} (H={d["H"]})'))
        for s in secs:
            if s['screens'] > 2.15: findings.append(('section-height', 'med', f'{tag} "{s["id"]}" is {s["screens"]} screens — split or cut'))
            if w == 1440 and s['words'] > 110 and 'ending' not in s['id']: findings.append(('words-per-screen', 'med', f'{tag} "{s["id"]}" {s["words"]} words (budget ~80 outside cards)'))
            if s['moves'] > 8: findings.append(('motion-budget', 'low', f'{tag} "{s["id"]}" has {s["moves"]} moves'))
            if s['over']: findings.append(('off-viewport', 'high', f'{tag} "{s["id"]}": {s["over"]} elements cross the viewport edge: {", ".join(s.get("overEls", []))}'))
            for hd in s['heads']:
                if hd.endswith('?') and 'faq' not in s['id']: findings.append(('heading-question', 'low', f'{tag} "{hd}"'))
        if w == 1440:
            h1w = len(d['h1'].split())
            if h1w > 8: findings.append(('h1-length', 'med', f'H1 has {h1w} words'))
            if d['links'] > 14: findings.append(('link-count', 'low', f'footer has {d["links"]} links/items'))
            labels = [b for b in d['buttons'] if not re.match(r'^(book|buy|order|pre-order|reserve|try|start|get|download|compare|see|watch|read|find|join|subscribe|sign up|contact|configure|add|send|email|request|check|go|replay|skip|rebuild)', b.lower())]
            english = (re.search(r'<html[^>]*\blang="([a-zA-Z-]+)"', open(path).read(2000)) or [None, 'en'])[1].lower().startswith('en')   # the list of verbs is English: a Spanish or Serbian label is not judged by it
            if labels and english: findings.append(('button-labels', 'low', 'not verb+object: ' + ', '.join(sorted(set(labels))[:6])))
        print(f'-- {tag} H={d["H"]} scrollW={d["scrollW"]}')
        for s in secs: print(f'   {s["id"]:<10} top={s["top"]:<6} h={s["h"]:<5} screens={s["screens"]:<5} words={s["words"]:<4} moves={s["moves"]} over={s["over"]}')
    return findings

if __name__ == '__main__':
    f = check(sys.argv[1])
    score = 100 - sum({'high': 12, 'med': 6, 'low': 3}[s] for _, s, _ in f)
    print(f'\nQA score {max(score, 0)}/100 · {len(f)} findings')
    for cid, sev, msg in f: print(f'  [{sev:<4}] {cid:<18} {msg}')
    if '--json' in sys.argv: json.dump({'score': score, 'findings': f}, open(sys.argv[1] + '.qa.json', 'w'), indent=1)
