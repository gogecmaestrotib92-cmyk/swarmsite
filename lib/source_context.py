"""Bound model context per page while retaining the complete capture on disk."""

def model_pages(inventory):
    pages = []
    source_pages = inventory.get('sourcePages') or []
    # Share the context budget across pages instead of cutting a serialized
    # document at an arbitrary point and silently losing the later pages.
    n = max(1, len(source_pages))
    body_limit = max(200, min(1200, 120000 // n))
    section_limit = max(60, min(400, 120000 // n // 12))
    for page in source_pages:
        if not isinstance(page, dict):
            continue
        sections = [s for s in page.get('sections') or [] if isinstance(s, dict)]
        copy = page.get('copy') or {}
        pages.append({
            'url': page.get('url'), 'title': page.get('title'), 'navLabel': page.get('navLabel'),
            'copy': {'h1': copy.get('h1'), 'text': str(copy.get('text') or '')[:body_limit],
                     'textTruncated': bool(copy.get('textTruncated') or len(str(copy.get('text') or '')) > body_limit)},
            'sectionsFound': page.get('sectionsFound', len(sections)),
            'sectionsTruncated': bool(page.get('sectionsTruncated') or len(sections) > 12),
            'sections': [{**{k: s.get(k) for k in ('id', 'title', 'kind', 'sourceUrl')},
                          'text': str(s.get('text') or '')[:section_limit],
                          'textTruncated': bool(s.get('textTruncated') or len(str(s.get('text') or '')) > section_limit),
                          'faq': [{'question': str(q.get('question') or '')[:200],
                                   'answer': str(q.get('answer') or '')[:400],
                                   'status': q.get('status'),
                                   'truncated': bool(q.get('questionTruncated') or q.get('answerTruncated') or len(str(q.get('question') or '')) > 200 or len(str(q.get('answer') or '')) > 400)}
                                  for q in (s.get('faq') or [])[:2] if isinstance(q, dict)],
                          'faqTruncated': bool(s.get('faqTruncated') or len(s.get('faq') or []) > 2)}
                         for s in sections[:12]],
            'actions': (page.get('actions') or [])[:15], 'forms': (page.get('forms') or [])[:5],
        })
    return pages

def model_analysis(state, budget=100000):
    """Expose bounded model observations with explicit source and omission flags."""
    if not isinstance(state, dict): return None
    entries = [state.get('batches', {}).get(k) for k in state.get('ordered_keys', [])]
    entries = [e for e in entries if isinstance(e, dict)]
    observations = [o for e in entries for o in e.get('observations', []) if isinstance(o, dict)]
    total_observations = len(observations)
    # Keep the prompt bounded even for sites with thousands of pages. Spread
    # retained observations across the run, preserving the earliest, usually
    # highest-priority pages, and explicitly report omissions.
    if total_observations > 300:
        head=observations[:60]; tail=observations[60:]
        observations = head + [tail[i * (len(tail) - 1) // 239] for i in range(240)]
    per = max(40, min(1000, budget // max(1, len(observations))))
    result=[]
    for obs in observations:
        facts=obs.get('facts') if isinstance(obs.get('facts'),list) else []
        source=' | '.join(x for x in facts if isinstance(x,str))
        uncertainties=obs.get('uncertainties') if isinstance(obs.get('uncertainties'),list) else []
        unknown=' | '.join(x for x in uncertainties if isinstance(x,str))
        ids=obs.get('section_ids') if isinstance(obs.get('section_ids'),list) else []
        result.append({'source_url':str(obs.get('source_url') or '')[:2000], 'section_ids':ids[:10],
                       'observations':source[:per], 'uncertainties':unknown[:per//2],
                       'truncated':len(source)>per or len(unknown)>per//2 or len(ids)>10})
    usage = [u for entry in entries for u in (entry.get('usage') or []) if isinstance(u,dict)]
    totals = {key:sum(int(u.get(key) or 0) for u in usage) for key in ('input_tokens','output_tokens','cache_creation_input_tokens','cache_read_input_tokens')}
    return {'complete':bool(state.get('complete')), 'batches_completed':state.get('completed'), 'batches_total':state.get('total'),
            'usage_recorded_calls':len(usage), 'token_usage':totals,
            'missing_pages':sum(len(e.get('missing_urls') or []) for e in entries),
            'missing_sections':sum(len(ids) for e in entries for ids in (e.get('missing_sections') or {}).values()),
            'observations_total':total_observations, 'observations_in_context':len(result),
            'context_truncated':total_observations>len(result) or any(o['truncated'] for o in result), 'observations':result}
