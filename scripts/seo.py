#!/usr/bin/env python3
"""seo.py — what a search engine and a shared link read of swarmsite.si, written from one place.

    python3 scripts/seo.py           write
    python3 scripts/seo.py --check   exit 1 when a written file is not what this script would write (tests/test_seo.py)
    python3 scripts/seo.py --cards   write, then photograph the sharing cards (scripts/og_cards.mjs; needs Chrome)

It writes
    web/blog/index.html, web/blog/<slug>.html   from content/blog/<slug>.html — an article is its text and a few facts
                                                 about it (a JSON comment at the top); the page round it is made here
    web/blog/feed.xml                            the articles as RSS
    web/sitemap.xml                              every page a search engine may list, each with the day it last changed
    the structured-data block of web/index.html  the questions and answers are read off the page's own FAQ, the price
                                                 off its own price, so the block can never say what the page does not
The blog is on the shared layer of every page (web/css/site.css) with its own sheet (web/css/blog.css) and a few lines
of script (web/js/blog.js). Nothing here calls a model. An article states a fact about another company's service only
with its source in "sources"; the generator prints them at the foot of the article.
"""
import datetime
import html
import json
import os
import re
import subprocess
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
WEB = os.path.join(ROOT, 'web')
SRC = os.path.join(ROOT, 'content', 'blog')
SITE = 'https://swarmsite.si'
NAME = 'Swarmsite'
BLOG_TITLE = 'Notes on redesigning a website'
BLOG_DESC = 'Practical guides from Swarmsite: redesigning a website without losing what works, putting it online, and making a landing page for an app.'
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;1,400&amp;family=Figtree:wght@400;500;600;700;800&amp;family=Shrikhand&amp;display=swap" rel="stylesheet">')
PAGES = [('/', '2026-11-25'), ('/blog', None), ('/privacy', '2026-11-06'), ('/terms', '2026-11-20')]   # the pages a search engine may list beside the articles, each with the day its words last changed (set by hand when they do)

e = lambda s: html.escape(str(s), quote=True)
read = lambda p: open(p, encoding='utf-8').read()
CHEV = '<svg class="chev" viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><path d="M6 3.5 10.5 8 6 12.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def letters(t):
    """a button's label as the shared layer wants it: letters that lean in turn under the pointer"""
    return '<span class="lt" aria-hidden="true">' + ''.join(c if c == ' ' else f'<span class="ch" style="--i:{i}">{e(c)}</span>' for i, c in enumerate(t)) + '</span>'


def long_date(d):
    y, m, day = map(int, d.split('-'))
    return f'{day} {datetime.date(y, m, 1):%B} {y}'


def posts():
    out = []
    for f in sorted(os.listdir(SRC)):
        if not f.endswith('.html'):
            continue
        raw = read(os.path.join(SRC, f))
        m = re.match(r'\s*<!--(\{.*?\})-->\s*', raw, re.S)
        if not m:
            raise SystemExit(f'{f}: an article starts with its facts, a JSON comment')
        p = json.loads(m.group(1))
        p['slug'], p['body'] = f[:-5], raw[m.end():].strip()
        for k in ('title', 'description', 'standfirst', 'kicker', 'date', 'ground', 'tone', 'shot', 'shot_alt'):
            if not p.get(k):
                raise SystemExit(f'{f}: no "{k}"')
        words = len(re.sub(r'<[^>]+>', ' ', p['body']).split())
        p['minutes'], p['words'] = max(2, round(words / 220)), words
        p['url'] = f'{SITE}/blog/{p["slug"]}'
        p['updated'] = p.get('updated') or p['date']
        out.append(p)
    return sorted(out, key=lambda p: (p['date'], p['slug']), reverse=True)


def ld(*things):
    return '<script type="application/ld+json">' + json.dumps({'@context': 'https://schema.org', '@graph': list(things)}, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + '</script>'


ORG = {'@type': 'Organization', '@id': SITE + '/#org', 'name': NAME, 'url': SITE + '/', 'email': 'hello@swarmsite.si',
       'logo': {'@type': 'ImageObject', 'url': SITE + '/logo/swarmsite-mark.png', 'width': 963, 'height': 963}}
WEBSITE = {'@type': 'WebSite', '@id': SITE + '/#site', 'url': SITE + '/', 'name': NAME, 'inLanguage': 'en', 'publisher': {'@id': SITE + '/#org'}}


def head(title, desc, path, card, kind='website', extra=''):
    url = SITE + path
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}"><meta property="og:url" content="{url}"><meta property="og:type" content="{kind}"><meta property="og:site_name" content="{NAME}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{SITE}{card}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#f4f2ec">
<link rel="icon" type="image/png" href="/favicon.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="alternate" type="application/rss+xml" title="{NAME} — {e(BLOG_TITLE.lower())}" href="/blog/feed.xml">
{FONTS}
<link rel="stylesheet" href="/css/site.css">
<link rel="stylesheet" href="/css/blog.css">
{extra}
</head>
'''


def nav(here=False):
    cur = ' aria-current="page"' if here else ''
    return f'''<body><a class="skip" href="#main">Skip to content</a><header class="nv nav"><div class="nvb">
<a class="logo" href="/" aria-label="Swarmsite, front page"><img src="/logo/swarmsite-mark-96.webp" srcset="/logo/swarmsite-mark-96.webp 1x, /logo/swarmsite-mark-192.webp 2x" width="26" height="26" alt=""><span aria-hidden="true">swarmsite</span></a>
<nav class="nvl" aria-label="Primary"><div class="seg"><a href="/#how">How it works</a><a href="/#price">Price</a></div><span class="nvr grp"><a href="/blog"{cur}>Blog</a></span></nav>
<a class="btn nb" href="/" aria-label="Try it free">{letters('Try it free')}</a>
<button class="burger" type="button" aria-expanded="false" aria-controls="menu" aria-label="Menu"><i></i><i></i><i></i></button>
</div><div class="menu" id="menu" hidden><nav aria-label="Menu"><a href="/#how">How it works</a><a href="/#price">Price</a><a href="/blog"{cur}>Blog</a><a href="/#faq">FAQ</a></nav></div></header>
'''


def cover(p, cls='', lazy=True, h=2):
    """an article's picture, in the landing's manner: one of our own interface's screens, whole, on a made ground"""
    load = ' loading="lazy" decoding="async"' if lazy else ' fetchpriority="high" decoding="async"'
    return (f'<span class="cov tone-{p["tone"]}{" " + cls if cls else ""}"><img class="mk" src="/visuals/{p["ground"]}.webp" width="1400" height="784" alt=""{load}>'
            f'<img class="shot" src="/visuals/{p["shot"]}.webp" width="1200" height="750" alt="{e(p["shot_alt"])}"{load}></span>')


def card(p, lead=False, level=2):
    return (f'<a class="pc{" lead" if lead else ""}" href="/blog/{p["slug"]}">{cover(p, lazy=not lead)}'
            f'<span class="tag">{e(p["kicker"])} · {p["minutes"]} min read</span><h{level} class="{"h-m" if lead else "h-s"}">{e(p["title"])}</h{level}>'
            f'<p class="pd">{e(p["description"])}</p><span class="more">Read the guide {CHEV}</span></a>')


CTA = f'''<section class="cta" aria-labelledby="ctah"><div class="wrap"><div class="cbox"><h2 class="h-m" id="ctah">See your website <em>in a new design.</em></h2><p class="lead">Paste your address. Three designs made from your own words and pictures, free to look at.</p>
<form class="urlf" onsubmit="go(event)"><span class="pre" aria-hidden="true">https://</span><input aria-label="Your website address" placeholder="yourwebsite.com" autocomplete="url" inputmode="url" required><button class="btn" type="submit" aria-label="Create my designs">{letters('Create my designs')}</button></form>
<p class="small">Your site stays as it is. 79 € once, only for the design you keep.</p></div></div></section>'''

FOOT = '''<footer class="ft"><div class="wrap"><div class="fcols"><ul><li><a href="/#how">How it works</a></li><li><a href="/#price">Price</a></li><li><a href="/#faq">FAQ</a></li></ul><ul><li><a href="/blog">Blog</a></li><li><a href="/blog/feed.xml">RSS</a></li></ul><ul><li><a href="/login">Log in</a></li><li><a href="/">Try it free</a></li></ul><ul><li><a href="/privacy">Privacy</a></li><li><a href="/terms">Terms</a></li><li><a href="mailto:hello@swarmsite.si">Contact</a></li></ul></div><div class="big" aria-hidden="true" style="--fs:min(12.6vw,182px)">swarmsite</div><div class="legal"><span>© 2026 Swarmsite</span></div></div></footer>
<script src="/js/blog.js" defer></script><script src="/js/track.js" defer></script>
<script src="/js/nav-account.js" defer></script>
</body></html>
'''


def contents(body):
    """the article's h2s get an id each, and a short list of them opens the article"""
    seen, items = set(), []

    def one(m):
        t = re.sub(r'<[^>]+>', '', m.group(1))
        i = re.sub(r'[^a-z0-9]+', '-', html.unescape(t).lower()).strip('-')[:48].rstrip('-')
        while i in seen:
            i += '-2'
        seen.add(i)
        items.append((i, t))
        return f'<h2 id="{i}">{m.group(1)}</h2>'
    body = re.sub(r'<h2>(.*?)</h2>', one, body, flags=re.S)
    toc = '<nav class="toc" aria-label="In this guide"><p class="tag">In this guide</p><ol>' + ''.join(f'<li><a href="#{i}">{t}</a></li>' for i, t in items) + '</ol></nav>'
    return body, toc


def tables(body):
    """each cell carries the name of its column, so a narrow screen can set a row as a block (blog.css)"""
    def one(m):
        heads = [html.unescape(re.sub(r'<[^>]+>', '', h)).strip() for h in re.findall(r'<th\b[^>]*>(.*?)</th>', m.group(0).split('</thead>')[0], re.S)]

        def row(r):
            cells = iter(range(len(heads)))
            return re.sub(r'<(td|th)\b([^>]*)>', lambda c: (lambda i: f'<{c.group(1)}{c.group(2)}' + (f' data-label="{e(heads[i])}"' if c.group(1) == 'td' and i and heads[i] else '') + '>')(next(cells, 0)), r.group(0))
        head, rest = m.group(0).split('</thead>', 1)
        return head + '</thead>' + re.sub(r'<tr>.*?</tr>', row, rest, flags=re.S)
    return re.sub(r'<table>.*?</table>', one, body, flags=re.S)


def article(p, others):
    body, toc = contents(tables(p['body']))
    src = ''
    if p.get('sources'):
        src = '<section class="src" aria-labelledby="srch"><h2 id="srch">Sources</h2><p>What this guide says about another company’s service was read from its own documentation on ' + long_date(p['updated']) + '.</p><ul>' + ''.join(f'<li><a href="{e(u)}" rel="noopener">{e(t)}</a></li>' for t, u in p['sources']) + '</ul></section>'
    data = ld({'@type': 'BlogPosting', '@id': p['url'] + '#article', 'headline': p['title'], 'description': p['description'], 'datePublished': p['date'], 'dateModified': p['updated'],
               'inLanguage': 'en', 'wordCount': p['words'], 'image': f'{SITE}/og/{p["slug"]}.jpg', 'mainEntityOfPage': p['url'], 'author': {'@id': SITE + '/#org'}, 'publisher': {'@id': SITE + '/#org'}, 'isPartOf': {'@id': SITE + '/#site'}},
              {'@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': 1, 'name': NAME, 'item': SITE + '/'}, {'@type': 'ListItem', 'position': 2, 'name': 'Blog', 'item': SITE + '/blog'}, {'@type': 'ListItem', 'position': 3, 'name': p['title'], 'item': p['url']}]},
              ORG, WEBSITE)
    meta = f'<meta property="article:published_time" content="{p["date"]}"><meta property="article:modified_time" content="{p["updated"]}">\n'
    return (head(f'{p.get("title_tag") or p["title"]} — {NAME}', p['description'], f'/blog/{p["slug"]}', f'/og/{p["slug"]}.jpg', 'article', meta + data) + nav() +
            f'''<main id="main"><article><header class="ah"><div class="wrap"><p class="crumb"><a href="/blog">Blog</a><span aria-hidden="true"> / </span>{e(p["kicker"])}</p>
<h1 class="h-l">{e(p["title"])}</h1><p class="lead">{e(p["standfirst"])}</p><p class="small meta"><time datetime="{p["date"]}">{long_date(p["date"])}</time> · {p["minutes"]} min read</p></div></header>
<div class="wrap">{cover(p, 'wide', lazy=False)}</div>
<div class="body">{toc}
{body}
{src}</div></article>
{CTA}
<section class="next" aria-labelledby="nexth"><div class="wrap"><h2 class="h-m" id="nexth">Read next</h2><div class="pgrid2">{"".join(card(o, level=3) for o in others[:2])}</div></div></section></main>
''' + FOOT)


def index(ps):
    data = ld({'@type': 'Blog', '@id': SITE + '/blog#blog', 'url': SITE + '/blog', 'name': f'{NAME} — {BLOG_TITLE.lower()}', 'description': BLOG_DESC, 'inLanguage': 'en', 'publisher': {'@id': SITE + '/#org'},
               'blogPost': [{'@type': 'BlogPosting', 'headline': p['title'], 'url': p['url'], 'datePublished': p['date'], 'dateModified': p['updated']} for p in ps]}, ORG, WEBSITE)
    return (head(f'{BLOG_TITLE} — {NAME}', BLOG_DESC, '/blog', '/og/blog.jpg', 'website', data) + nav(True) +
            f'''<main id="main"><header class="bh"><div class="wrap"><p class="tag">Blog</p><h1 class="h-xl">Notes on <em>redesigning a website</em></h1><p class="lead">Short, practical guides: what to keep when a site is redesigned, how to put the new one online, and what a page for a new app has to say.</p></div></header>
<section class="posts" aria-label="Guides"><div class="wrap">{card(ps[0], lead=True)}<div class="pgrid2">{"".join(card(p) for p in ps[1:])}</div></div></section>
{CTA}</main>
''' + FOOT)


def feed(ps):
    rfc = lambda d: datetime.datetime.strptime(d, '%Y-%m-%d').strftime('%a, %d %b %Y 08:00:00 +0000')
    items = ''.join(f'<item><title>{e(p["title"])}</title><link>{p["url"]}</link><guid isPermaLink="true">{p["url"]}</guid><pubDate>{rfc(p["date"])}</pubDate><description>{e(p["description"])}</description></item>\n' for p in ps)
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>{NAME} — {e(BLOG_TITLE.lower())}</title><link>{SITE}/blog</link>'
            f'<atom:link href="{SITE}/blog/feed.xml" rel="self" type="application/rss+xml"/><description>{e(BLOG_DESC)}</description><language>en</language><lastBuildDate>{rfc(max(p["updated"] for p in ps))}</lastBuildDate>\n{items}</channel></rss>\n')


def sitemap(ps):
    rows = [(SITE + path, d or max(p['updated'] for p in ps)) for path, d in PAGES] + [(p['url'], p['updated']) for p in ps]
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
            ''.join(f'<url><loc>{loc}</loc><lastmod>{d}</lastmod></url>\n' for loc, d in rows) + '</urlset>\n')


def home_data(page):
    """the front page's structured data, read off the front page: its questions, its answers, its price"""
    text = lambda h: html.unescape(' '.join(re.sub(r'<[^>]+>', ' ', h).split()))
    faq = [(text(q), text(a)) for q, a in re.findall(r'<summary><span>(.*?)</span>.*?<p class="a">(.*?)</p>', page, re.S)]
    price = re.search(r'<p class="price">\s*(\d+)\s*€', page)
    desc = re.search(r'<meta name="description" content="([^"]+)"', page)
    if not faq or not price or not desc:
        raise SystemExit('index.html: no FAQ, price or description to read')
    return ld(ORG, WEBSITE,
              {'@type': 'SoftwareApplication', '@id': SITE + '/#app', 'name': NAME, 'url': SITE + '/', 'applicationCategory': 'DesignApplication', 'operatingSystem': 'Web', 'description': html.unescape(desc.group(1)),
               'publisher': {'@id': SITE + '/#org'}, 'offers': {'@type': 'Offer', 'price': price.group(1), 'priceCurrency': 'EUR', 'description': 'One-time payment for the design you keep. The three previews are free.'}},
              {'@type': 'FAQPage', '@id': SITE + '/#faq', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faq]})


def home(page):
    block = home_data(page)
    if '<script type="application/ld+json">' in page:
        return re.sub(r'<script type="application/ld\+json">.*?</script>', lambda m: block, page, count=1, flags=re.S)
    return page.replace('</head>', block + '\n</head>', 1)


def build():
    ps = posts()
    out = {os.path.join(WEB, 'blog', 'index.html'): index(ps), os.path.join(WEB, 'blog', 'feed.xml'): feed(ps)}
    for p in ps:
        out[os.path.join(WEB, 'blog', p['slug'] + '.html')] = article(p, [o for o in ps if o is not p])
    out[os.path.join(WEB, 'sitemap.xml')] = sitemap(ps)
    ix = os.path.join(WEB, 'index.html')
    out[ix] = home(read(ix))
    return ps, out


def cards(ps):
    """what scripts/og_cards.mjs photographs: one card for each page that can be shared"""
    home_title = html.unescape(re.search(r'<meta property="og:title" content="([^"]+)"', read(os.path.join(WEB, 'index.html'))).group(1))
    return ([{'file': 'home.jpg', 'kicker': 'swarmsite.si', 'title': 'A better website. Built from yours.', 'ground': 'paper-fold', 'tone': 'light', 'shot': 'ui-designs', 'page': home_title},
             {'file': 'blog.jpg', 'kicker': 'Blog', 'title': BLOG_TITLE, 'ground': 'titanium-arc', 'tone': 'dark', 'shot': 'ui-reading'}] +
            [{'file': p['slug'] + '.jpg', 'kicker': p['kicker'], 'title': p['title'], 'ground': p['ground'], 'tone': p['tone'], 'shot': p['shot']} for p in ps])


def main(argv):
    ps, out = build()
    if '--check' in argv:
        stale = [os.path.relpath(f, ROOT) for f, s in out.items() if not os.path.exists(f) or read(f) != s]
        extra = [f for f in os.listdir(os.path.join(WEB, 'blog')) if f.endswith('.html') and os.path.join(WEB, 'blog', f) not in out] if os.path.isdir(os.path.join(WEB, 'blog')) else []
        missing = [c['file'] for c in cards(ps) if not os.path.exists(os.path.join(WEB, 'og', c['file']))]
        for f in stale:
            print('not what scripts/seo.py writes:', f)
        for f in extra:
            print('a page of web/blog with no article in content/blog:', f)
        for f in missing:
            print('no sharing card (python3 scripts/seo.py --cards):', f)
        return 1 if stale or extra or missing else 0
    os.makedirs(os.path.join(WEB, 'blog'), exist_ok=True)
    for f, s in out.items():
        if not os.path.exists(f) or read(f) != s:
            open(f, 'w', encoding='utf-8').write(s)
            print('wrote', os.path.relpath(f, ROOT))
    if '--cards' in argv:
        os.makedirs(os.path.join(WEB, 'og'), exist_ok=True)
        return subprocess.run(['node', os.path.join(ROOT, 'scripts', 'og_cards.mjs')], input=json.dumps(cards(ps)), text=True, cwd=ROOT).returncode
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
