"""What a search engine and a shared link read of swarmsite.si is written by scripts/seo.py and says only what the pages say.
Every page a search engine may list has a title, a description, its own address as canonical and a sharing card that is
there; a page kept out of search is not in the sitemap; the structured data repeats the page it is on; llms.txt quotes the
price the landing quotes; a guide states of the product only what the landing's own test holds the landing to."""
import json
import os
import re
import struct
import subprocess
import sys

ROOT = os.path.join(os.path.dirname(__file__), '..')
WEB = os.path.join(ROOT, 'web')
SITE = 'https://swarmsite.si'
read = lambda *p: open(os.path.join(ROOT, *p), encoding='utf-8').read()
text = lambda h: ' '.join(re.sub(r'<[^>]+>', ' ', re.sub(r'<(svg|script|style)\b.*?</\1>', '', h, flags=re.S)).split())
LOCS = re.findall(r'<loc>([^<]+)</loc>', read('web', 'sitemap.xml'))


def file_of(loc):
    p = loc[len(SITE):].strip('/')
    for f in (p + '.html', os.path.join(p, 'index.html')) if p else ('index.html',):
        if os.path.isfile(os.path.join(WEB, f)):
            return f
    raise AssertionError(f'{loc} is in the sitemap and is no file of web/')


def pages():
    out = []
    for d, _, fs in os.walk(WEB):
        if os.sep + 'vendor' in d or os.sep + 'examples' in d:
            continue
        out += [os.path.relpath(os.path.join(d, f), WEB) for f in fs if f.endswith('.html')]
    return sorted(out)


def data_of(page):
    return [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S)]


def test_what_is_written_is_what_the_script_writes():
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'seo.py'), '--check'], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_every_listed_page_can_be_found_read_and_shared():
    assert len(LOCS) == len(set(LOCS)) and SITE + '/' in LOCS and SITE + '/blog' in LOCS
    titles = {}
    for loc in LOCS:
        page = read('web', file_of(loc))
        head = page.split('</head>')[0]
        title = re.search(r'<title>([^<]+)</title>', head).group(1)
        desc = re.search(r'<meta name="description" content="([^"]+)"', head)
        assert 20 <= len(title) <= 80, (loc, len(title), title)
        assert desc and 70 <= len(desc.group(1)) <= 165, (loc, desc and len(desc.group(1)))
        assert re.search(r'<link rel="canonical" href="([^"]+)"', head).group(1) == loc, loc
        assert 'name="robots"' not in head, loc
        assert len(re.findall(r'<h1\b', page)) == 1, loc
        assert title not in titles, f'{loc} and {titles.get(title)} have one title'
        titles[title] = loc
        if '/blog' in loc or loc == SITE + '/':
            assert re.search(r'<meta property="og:url" content="([^"]+)"', head).group(1) == loc
            assert 'summary_large_image' in head and re.search(r'<meta property="og:title" content="[^"]{10,}"', head)
            card = re.search(r'<meta property="og:image" content="%s(/og/[^"]+)"' % re.escape(SITE), head).group(1)
            raw = open(os.path.join(WEB, card.lstrip('/')), 'rb').read()
            assert raw[:2] == b'\xff\xd8' and 20_000 < len(raw) < 300_000, card
            i = 2                                                     # the card is 1200×630: read off the JPEG's frame header
            while raw[i + 1] not in (0xC0, 0xC2):
                i += 2 + struct.unpack('>H', raw[i + 2:i + 4])[0]
            assert struct.unpack('>HH', raw[i + 5:i + 9]) == (630, 1200), card
            for d in data_of(page):
                assert d['@context'] == 'https://schema.org' and d['@graph']


def test_a_page_kept_out_of_search_is_not_listed_and_the_rest_are():
    listed = {file_of(loc) for loc in LOCS}
    for f in pages():
        hidden = 'name="robots" content="noindex' in read('web', f)
        assert hidden != (f in listed), f'{f}: {"kept out of search and in the sitemap" if hidden else "open to search and not in the sitemap"}'
    robots = read('web', 'robots.txt')
    assert f'Sitemap: {SITE}/sitemap.xml' in robots and 'Disallow: /\n' not in robots + '\n'


def test_the_front_pages_data_repeats_the_front_page():
    page = read('web', 'index.html')
    graph = {t['@type']: t for d in data_of(page) for t in d['@graph']}
    body = page.split('<body>', 1)[1]
    faq = [(text(q), text(a)) for q, a in re.findall(r'<summary><span>(.*?)</span>.*?<p class="a">(.*?)</p>', body, re.S)]
    assert len(faq) >= 4 and [(q['name'], q['acceptedAnswer']['text']) for q in graph['FAQPage']['mainEntity']] == [(q.replace('&amp;', '&'), a.replace('&amp;', '&')) for q, a in faq]
    offer = graph['SoftwareApplication']['offers']
    assert offer['priceCurrency'] == 'EUR' and f'{offer["price"]} €' in text(body)
    assert not re.search(r'"(aggregateRating|review|reviewCount|ratingValue)"', json.dumps(graph)), 'no rating or review is claimed: there is none'


def test_the_terms_state_the_offer_the_landing_states():
    terms, landing = text(read('web', 'terms.html').split('<body>', 1)[1]), text(read('web', 'index.html').split('<body>', 1)[1])
    price = re.search(r'<p class="price">\s*(\d+ €)', read('web', 'index.html')).group(1)
    assert price in terms and 'One-time payment' in landing and 'one-time payment' in terms
    assert not re.search(r'\bkit\b|monthly|per month|\$', terms, re.I) and 'no subscription' in terms.lower()
    assert not re.search(r'publish|name\.swarmsite\.si', terms, re.I) and 'We do not host it for you' in terms, 'hosting is not offered (owner, 2026-11-13)'


def test_the_front_page_keeps_its_proof_of_ownership():
    """Search Console verifies swarmsite.si by this tag (owner's account, 2026-11-19); taking it out loses the property"""
    assert re.search(r'<meta name="google-site-verification" content="[\w-]{20,}">', read('web', 'index.html').split('</head>')[0])


def test_llms_txt_quotes_the_landing():
    llms, words = read('web', 'llms.txt'), text(read('web', 'index.html').split('<body>', 1)[1])
    price = re.search(r'<p class="price">\s*(\d+ €)', read('web', 'index.html')).group(1)
    assert price in llms and price in words and '$' not in llms and not re.search(r'subscription|/month|per month', llms.replace('There is no subscription', ''), re.I)
    for u in re.findall(r'\((https://swarmsite\.si[^)]*)\)', llms):
        assert u in LOCS, f'llms.txt points at {u}, which the sitemap does not list'
    assert re.search(r"SCREENS = 6\b", read('lib', 'templates', 'job.py')) and 'up to six screenshots' in llms
    pkg = read('lib', 'templates', 'package.py')
    assert all(n in pkg for n in ('index.html', 'media/', 'fonts/', 'data.json', 'README.txt')) and 'data.json' in llms


def test_a_guide_says_of_the_product_only_what_the_landing_says():
    landing = text(read('web', 'index.html').split('<body>', 1)[1])
    names = [d for d in os.listdir(os.path.join(ROOT, 'lib', 'templates')) if os.path.isdir(os.path.join(ROOT, 'lib', 'templates', d)) and not d.startswith('_')] + ['wisprflow', 'wispr']
    guides = [f for f in pages() if f.startswith('blog' + os.sep)]
    assert len(guides) >= 4
    for f in guides + ['404.html']:
        src = read('web', f)
        seen = text(src.split('<body>', 1)[1])
        hit = [n for n in names if re.search(r'(?<![a-z0-9])%s(?![a-z0-9])' % re.escape(n), src.lower())]
        assert not hit, f'{f} names {hit}'
        assert not re.search(r'publish|name\.swarmsite\.si|we host|hosted by us', seen, re.I), f'{f}: hosting is not offered (owner, 2026-11-13)'
        for price in re.findall(r'\d+ ?€', seen):
            assert price in landing, f'{f} quotes {price}, the landing does not'
        assert not re.search(r'testimonial from|trusted by \d|rated \d', seen, re.I) or 'landing-page-for-your-app' in f
        for img in re.findall(r'<img\b[^>]*>', src):
            assert re.search(r'\bwidth="\d+"', img) and re.search(r'\bheight="\d+"', img), img
    for f in guides:
        if f.endswith('index.html'):
            continue
        src = read('web', f)
        post = next(t for d in data_of(src) for t in d['@graph'] if t['@type'] == 'BlogPosting')
        assert post['headline'] in text(src) and re.fullmatch(r'\d{4}-\d\d-\d\d', post['datePublished']) and post['author']['@id'] == SITE + '/#org'
        assert '/css/site.css' in src and '/css/blog.css' in src and not re.search(r'gsap|lenis|ScrollTrigger', src)
    source = lambda n: read('content', 'blog', n + '.html')
    assert 'up to six screenshots' in source('landing-page-for-your-app') and 'up to six screenshots' in landing
    for n in ('host-html-css-website', 'redesign-website-without-losing-seo'):
        assert len(json.loads(re.match(r'\s*<!--(\{.*?\})-->', source(n), re.S).group(1))['sources']) >= 3, f'{n}: what it says of another company\'s service has its source'
