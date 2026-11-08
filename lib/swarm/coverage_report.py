"""Evidence-based coverage report for a single-page preview.

An exact source heading appearing in HTML is only a textual signal: it does not
prove that all meaning or details survived. Absence requires human review,
because the director may paraphrase it. Source pages are only marked as linked
when the preview points to the original URL; they are never claimed as built.
"""
import html
import json
import os
import re
import unicodedata
from html.parser import HTMLParser
from urllib.parse import urlsplit, urlunsplit


class PreviewText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.links = []
        self.ignored = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if self.ignored:
            if tag not in ('area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'):
                self.ignored.append(tag)
            return
        style = str(attrs.get('style') or '').replace(' ', '').lower()
        hidden = tag in ('head', 'script', 'style', 'template', 'noscript', 'svg', 'textarea') or 'hidden' in attrs or str(attrs.get('aria-hidden') or '').lower() == 'true' or 'display:none' in style or 'visibility:hidden' in style
        if hidden:
            if tag not in ('area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'):
                self.ignored.append(tag)
            return
        if tag == 'a' and attrs.get('href'):
            self.links.append(attrs['href'])

    def handle_endtag(self, tag):
        if self.ignored and self.ignored[-1] == tag:
            self.ignored.pop()

    def handle_data(self, text):
        if not self.ignored:
            self.parts.append(text)


def normalize(text):
    text = unicodedata.normalize('NFKC', html.unescape(str(text or ''))).casefold()
    return ' '.join(re.findall(r'\w+', text, re.UNICODE))


def normalized_url(url):
    try:
        value = urlsplit(str(url or ''))
        if value.scheme.lower() not in ('http', 'https') or not value.hostname:
            return ''
        scheme, host = value.scheme.lower(), value.hostname.lower()
        port = value.port
        netloc = (f'[{host}]' if ':' in host else host) + ((':' + str(port)) if port and (scheme, port) not in (('http', 80), ('https', 443)) else '')
        return urlunsplit((scheme, netloc, value.path.rstrip('/') or '/', value.query, ''))
    except (ValueError, TypeError):
        return ''


def build_coverage(inventory, rendered_html):
    inventory = inventory if isinstance(inventory, dict) else {}
    source = inventory.get('sourceCoverage')
    catalog = source if isinstance(source, dict) else {}
    sections = catalog.get('sections')
    routes = catalog.get('routes')
    fallback_sections = not isinstance(sections, list)
    fallback_routes = not isinstance(routes, list)
    if fallback_sections:
        # Older captures did not save section boundaries; use only their H2s
        # as an incomplete hint, never as a complete page inventory.
        sections = [{'id': f'heading-{i}', 'title': h.get('text'), 'sourceUrl': inventory.get('url')}
                    for i, h in enumerate((inventory.get('copy') or {}).get('headings') or [])
                    if isinstance(h, dict) and str(h.get('tag', '')).upper() == 'H2']
    if fallback_routes:
        routes = [{'url': p.get('url'), 'label': p.get('navLabel') or p.get('title'), 'status': 'visited'}
                  for p in (inventory.get('sourcePages') or []) if isinstance(p, dict)]
    parser = PreviewText()
    parser.feed(str(rendered_html or ''))
    text = ' ' + normalize(' '.join(parser.parts)) + ' '
    links = {normalized_url(link) for link in parser.links}
    links.discard('')
    result_sections, seen_sections = [], set()
    for i, sec in enumerate(sections):
        if not isinstance(sec, dict): continue
        title = str(sec.get('title') or '').strip()
        key = normalize(title)
        section_id = str(sec.get('id') or f'section-{i + 1}')
        if not key or section_id in seen_sections: continue
        seen_sections.add(section_id)
        heading_found = len(key) >= 3 and (' ' + key + ' ') in text
        faq = []
        for entry in sec.get('faq') or []:
            if not isinstance(entry, dict): continue
            question = str(entry.get('question') or '').strip()
            answer = str(entry.get('answer') or '').strip()
            source_status = str(entry.get('status') or 'unavailable')
            if not question: continue
            if source_status != 'readable' or not answer:
                faq_status, evidence = 'source_unavailable', 'answer was not available in the source capture'
            elif entry.get('answerTruncated') or entry.get('questionTruncated'):
                faq_status, evidence = 'source_incomplete', 'captured question or answer was truncated; completeness cannot be checked'
            elif normalize(question) and normalize(answer) and (' ' + normalize(question) + ' ') in text and (' ' + normalize(answer) + ' ') in text:
                faq_status, evidence = 'text_detected', 'exact question and answer text found in HTML; visibility and functionality are unverified'
            else:
                faq_status, evidence = 'needs_review', 'question or answer text not found exactly; it may be paraphrased or omitted'
            faq.append({'question': question, 'source_status': source_status, 'status': faq_status, 'evidence': evidence})
        testimonials = []
        for item in sec.get('testimonials') or []:
            if not isinstance(item, dict): continue
            quote = str(item.get('text') or '').strip()
            attribution = str(item.get('attribution') or '').strip()
            source_links = item.get('links') if isinstance(item.get('links'), list) else []
            incomplete = (item.get('status') != 'candidate' or not quote or not attribution or
                          any(item.get(k) for k in ('textTruncated', 'attributionTruncated', 'linksTruncated')))
            link_keys = [normalized_url(link.get('url')) for link in source_links if isinstance(link, dict)]
            quote_found = (normalize(quote) and normalize(attribution) and
                     (' ' + normalize(quote) + ' ') in text and (' ' + normalize(attribution) + ' ') in text and
                     len(link_keys) == len(source_links) and all(key and key in links for key in link_keys))
            testimonials.append({'attribution': attribution or 'Unattributed quote',
                                 'status': 'source_incomplete' if incomplete else 'text_detected' if quote_found else 'needs_review'})
        panels = []
        faq_questions = {normalize(item.get('question')) for item in sec.get('faq') or [] if isinstance(item, dict)}
        for panel in sec.get('panels') or []:
            if not isinstance(panel, dict): continue
            trigger = str(panel.get('trigger') or '').strip()
            if not trigger or normalize(trigger) in faq_questions: continue
            panel_text = str(panel.get('text') or '').strip()
            source_links = panel.get('links') if isinstance(panel.get('links'), list) else []
            incomplete = (panel.get('status') != 'candidate' or not panel_text or
                          any(panel.get(k) for k in ('triggerTruncated', 'textTruncated', 'linksTruncated')))
            link_keys = [normalized_url(link.get('url')) for link in source_links if isinstance(link, dict)]
            panel_found = (normalize(panel_text) and (' ' + normalize(panel_text) + ' ') in text and
                     len(link_keys) == len(source_links) and all(key and key in links for key in link_keys))
            panels.append({'trigger': trigger, 'status': 'source_incomplete' if incomplete else 'text_detected' if panel_found else 'needs_review',
                           'source_excerpt': panel_text,
                           'source_links': [{'url': str(link.get('url') or ''), 'label': str(link.get('label') or '')}
                                            for link in source_links if isinstance(link, dict) and normalized_url(link.get('url'))]})
        result_sections.append({'id': section_id, 'title': title,
                                'source_url': str(sec.get('sourceUrl') or inventory.get('url') or ''),
                                'source_kind': str(sec.get('kind') or 'unknown'),
                                'source_text_truncated': bool(sec.get('textTruncated')),
                                'status': 'text_detected' if heading_found else 'needs_review',
                                'evidence': 'exact heading text found in HTML' if heading_found else 'exact heading not found; it may have been paraphrased or omitted',
                                'faq': faq, 'faq_truncated': bool(sec.get('faqTruncated')),
                                'testimonials': testimonials, 'panels': panels,
                                'evidence_truncated': bool(sec.get('testimonialsTruncated') or sec.get('panelsTruncated'))})
    result_routes, seen_routes = [], set()
    for route in routes:
        if not isinstance(route, dict): continue
        url = str(route.get('url') or '').strip()
        key = normalized_url(url)
        if not key or key in seen_routes: continue
        seen_routes.add(key)
        capture_status = str(route.get('status') or 'unknown')
        final_key = normalized_url(route.get('finalUrl')) if capture_status == 'visited' else ''
        result_routes.append({'url': url, 'label': str(route.get('label') or ''),
                              'capture_status': capture_status,
                              'reason': str(route.get('reason') or ''),
                              'status': 'linked_to_source' if key in links or (final_key and final_key in links) else 'not_linked'})
    detected = sum(sec['status'] == 'text_detected' for sec in result_sections)
    linked = sum(route['status'] == 'linked_to_source' for route in result_routes)
    faq_items = [item for sec in result_sections for item in sec['faq']]
    testimonial_items = [item for sec in result_sections for item in sec['testimonials']]
    panel_items = [item for sec in result_sections for item in sec['panels']]
    return {
        'scope': 'single_page_preview',
        'limitations': [
            'A detected heading is only a text match, not proof that the full section or its details were preserved.',
            'A heading without an exact match may be paraphrased or omitted and needs review.',
            'FAQ text matches do not prove that an answer is complete, visible or usable; unavailable and truncated source answers cannot be verified.',
            'Source routes are original pages, not regenerated subpages. Link checks only verify the preview HTML.',
            'The source catalog covers discovered public links and captured sections, not a complete sitemap.',
        ],
        'source_catalog_fallback': fallback_sections or fallback_routes,
        'source_catalog_truncated': bool(catalog.get('sectionsTruncated') or catalog.get('routesTruncated')),
        'faq_catalog_truncated': any(sec['faq_truncated'] for sec in result_sections),
        'evidence_catalog_truncated': any(sec['evidence_truncated'] for sec in result_sections),
        'sections': result_sections,
        'routes': result_routes,
        'summary': {'sections_total': len(result_sections), 'sections_text_detected': detected,
                    'sections_needing_review': len(result_sections) - detected,
                    'routes_total': len(result_routes), 'routes_linked': linked,
                    'routes_not_linked': len(result_routes) - linked,
                    'faq_total': len(faq_items),
                    'faq_text_detected': sum(item['status'] == 'text_detected' for item in faq_items),
                    'faq_needing_review': sum(item['status'] == 'needs_review' for item in faq_items),
                    'faq_source_unavailable': sum(item['status'] == 'source_unavailable' for item in faq_items),
                    'faq_source_incomplete': sum(item['status'] == 'source_incomplete' for item in faq_items),
                    'testimonials_total': len(testimonial_items),
                    'testimonials_text_detected': sum(item['status'] == 'text_detected' for item in testimonial_items),
                    'panels_total': len(panel_items),
                    'panels_text_detected': sum(item['status'] == 'text_detected' for item in panel_items)},
    }


def write_coverage(slug_dir, html_path):
    inventory_path = os.path.join(slug_dir, 'inventory.json')
    with open(inventory_path, encoding='utf-8') as f: inventory = json.load(f)
    with open(html_path, encoding='utf-8') as f: rendered_html = f.read()
    result = build_coverage(inventory, rendered_html)
    with open(os.path.join(slug_dir, 'coverage.json'), 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    return result
