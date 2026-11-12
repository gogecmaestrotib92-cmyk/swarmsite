"""capture.py <dir> [product|empty] — writes a made-up capture (the files lib/pipeline/capture.mjs and the reader leave in
a job folder) for the template job's tests: the product page of tests/test_templates_adapt.py, with a features section
added so that a template of the library fits it. Invented names and words; no real business."""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('adapt_tests', ROOT / 'tests' / 'test_templates_adapt.py')
T = importlib.util.module_from_spec(spec)
spec.loader.exec_module(T)


def product():
    seed = T.product()
    inv = seed['inventory']
    feats = [('Receipts, read for you', 'Printed or handwritten, each amount beside the picture it came from.'),
             ('Headings that fit a stall', 'Stock, rent, pay, fuel and fees, and your own in a line.'),
             ('A copy for your accountant', 'CSV or PDF, sent from the app, and they need no account.')]
    text = 'What you get ' + ' '.join('%s %s' % f for f in feats)
    inv['copy']['headings'][2:2] = [{'tag': 'H2', 'text': 'WHAT YOU GET'}] + [{'tag': 'H3', 'text': t} for t, _ in feats]
    inv['copy']['text'] += ' ' + text
    inv['sourceCoverage']['sections'].insert(2, {'id': 'home-9', 'title': 'WHAT YOU GET', 'headingLevel': 'H2', 'kind': 'section', 'text': text, 'faq': [], 'testimonials': [], 'sourceActions': []})
    seed['factsheet']['facts'] += ['3 stalls share one ledger']
    return seed


if __name__ == '__main__':
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    seed = product() if (sys.argv[2:] or ['product'])[0] == 'product' else {'inventory': {'url': 'https://empty.example/', 'title': 'Empty', 'copy': {'h1': '', 'text': ''}}, 'images': []}
    for k, v in seed.items():
        (out / (k + '.json')).write_text(json.dumps(v, ensure_ascii=False), encoding='utf-8')
    print(out)
