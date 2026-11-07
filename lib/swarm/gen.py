"""gen.py — commissioned visuals. When the client's site has too few real pictures, the Visual agent orders an ORIGINAL
illustration / 3D render / abstract texture in the brand's colours (never a fake interface, never text, never faces).
Backend: Higgsfield platform API. Needs HIGGSFIELD_KEY="<key_id>:<key_secret>" in the environment.
Usage: python3 lib/swarm/gen.py "prompt" 16:9 out.jpg"""
import os, sys, time, json, urllib.request, urllib.error

MODEL_URL = os.environ.get('HIGGSFIELD_MODEL_URL', 'https://platform.higgsfield.ai/higgsfield-ai/soul/standard')
AR = {'16:9': '16:9', '4:3': '4:3', '1:1': '1:1', '3:4': '3:4', '9:16': '9:16', '3:2': '3:2', '2:3': '2:3'}

def enabled(): return bool(os.environ.get('HIGGSFIELD_KEY', '').strip())

def _req(url, data=None, method=None):
    key = os.environ['HIGGSFIELD_KEY'].strip()
    req = urllib.request.Request(url, data=json.dumps(data).encode() if data is not None else None, method=method or ('POST' if data is not None else 'GET'))
    req.add_header('Authorization', 'Key ' + key); req.add_header('Content-Type', 'application/json'); req.add_header('Accept', 'application/json')
    with urllib.request.urlopen(req, timeout=60) as r: return json.loads(r.read().decode())

def generate(prompt, ar='16:9', timeout=180):
    """Returns JPEG/PNG bytes or raises."""
    body = {'prompt': prompt[:1500], 'aspect_ratio': AR.get(ar, '16:9'), 'resolution': '720p'}
    sub = _req(MODEL_URL, body)
    status_url = sub.get('status_url') or (f"https://api.higgsfield.ai/requests/{sub.get('request_id') or sub.get('id')}/status")
    t0 = time.time(); wait = 2
    while time.time() - t0 < timeout:
        st = _req(status_url)
        s = st.get('status')
        if s == 'completed':
            imgs = st.get('images') or []
            if not imgs: raise RuntimeError('no images in result')
            with urllib.request.urlopen(imgs[0]['url'], timeout=60) as r: return r.read()
        if s in ('failed', 'nsfw', 'canceled'): raise RuntimeError(f'generation {s}: {st.get("error")}')
        time.sleep(wait); wait = min(8, wait * 1.5)
    raise RuntimeError('generation timeout')

if __name__ == '__main__':
    data = generate(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else '16:9'); open(sys.argv[3] if len(sys.argv) > 3 else 'gen.jpg', 'wb').write(data); print('ok', len(data))
