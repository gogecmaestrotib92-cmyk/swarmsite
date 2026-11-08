"""Bind a visual review to the exact image and section content it reviewed."""
import hashlib
import json

def ledger_lead_fingerprint(beat, image):
    """Digest all data used for the visual decision; never trust stale reviews."""
    source = {'review_version': 1, 'id': beat.get('id'), 'type': beat.get('type'), 'h2': beat.get('h2') or '',
              'label': beat.get('label') or '', 'lede': beat.get('lede') or '', 'items': beat.get('items'),
              'image_id': image.get('id'), 'image_data': image.get('data')}
    return hashlib.sha256(json.dumps(source, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
