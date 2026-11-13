"""A deploy reaches every visitor at once: no script or stylesheet of web/ may sit in a browser's cache for days.
(2026-11-12: swarmsite.si served /js/* with max-age=604800, and the owner's Chrome kept a deadlocking auth.js for a week
after the fix was live.) Every <script src> and <link rel=stylesheet> of our own in web/*.html is either versioned by
its content (?v=<hash>) or served under a vercel.json rule that makes the browser ask again (max-age=0)."""
import json
import re
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent / 'web'


def rules():
    """(regex, cache-control) for each header rule of vercel.json, its source read as Vercel reads it"""
    out = []
    for r in json.loads((WEB / 'vercel.json').read_text())['headers']:
        cc = next((h['value'] for h in r['headers'] if h['key'].lower() == 'cache-control'), None)
        if cc is None:
            continue
        src = re.escape(r['source']).replace(r'\(\.\*\)', '(.*)').replace(r'\\\.', r'\.')
        out.append((re.compile('^' + src + '$'), cc))
    return out


def cache_of(path):
    """what Vercel sends for a path: the last matching rule wins"""
    got = None
    for rx, cc in rules():
        if rx.match(path):
            got = cc
    return got


def fresh(cc):
    m = re.search(r'max-age=(\d+)', cc or '')
    return cc is None or (m and int(m.group(1)) == 0) or 'no-cache' in cc   # no rule: Vercel's default for static files is max-age=0, must-revalidate


def assets():
    for page in sorted(WEB.glob('*.html')):
        html = page.read_text(encoding='utf-8')
        for tag in re.findall(r'<script\b[^>]*\bsrc="([^"]+)"', html) + [h for t in re.findall(r'<link\b[^>]*>', html) if re.search(r'rel="?stylesheet', t) for h in re.findall(r'href="([^"]+)"', t)]:
            if tag.startswith('/') and not tag.startswith('//'):
                yield page.name, tag


def test_the_rules_read_as_vercel_reads_them():
    assert cache_of('/js/auth.js').startswith('public, max-age=0') and cache_of('/css/site.css').startswith('public, max-age=0')
    assert 'immutable' in cache_of('/fonts/figtree.woff2') and cache_of('/visuals/paper-fold.webp') == 'public, max-age=604800'


def test_every_script_and_stylesheet_of_ours_is_versioned_or_asked_for_again():
    stale = [f'{page}: {url} ({cache_of(url.split("?")[0])})' for page, url in assets()
             if not re.search(r'[?&]v=[0-9a-f]{8,}', url) and not fresh(cache_of(url.split('?')[0]))]
    assert not stale, 'kept in browsers after a deploy: ' + '; '.join(stale)


def test_header_css_and_config_js_are_covered_too():
    assert fresh(cache_of('/header.css')) and fresh(cache_of('/config.js'))
