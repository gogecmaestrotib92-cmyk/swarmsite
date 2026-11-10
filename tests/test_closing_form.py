"""The closing call to action is shaped by what the page is: a short line stands left with its action beside it,
a page of rounded corners gets a panel, and a closing with a form keeps the centred form."""
import json, os, shutil, subprocess, sys, tempfile
ROOT = os.path.join(os.path.dirname(__file__), '..')


def render(bp, change):
    tmp = tempfile.mkdtemp()
    for name in ('direction', 'images', 'assets', 'inventory'):
        shutil.copy(os.path.join(ROOT, 'tests', f'{name}.sample.json'), os.path.join(tmp, f'{name}.json'))
    path = os.path.join(tmp, 'direction.json'); d = json.load(open(path, encoding='utf-8'))
    def walk(o):
        if isinstance(o, dict):
            if o.get('type') == 'form': change(o)
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(d); json.dump(d, open(path, 'w', encoding='utf-8'))
    out = os.path.join(tmp, 'page.html')
    subprocess.run([sys.executable, os.path.join(ROOT, 'lib', 'render', 'render_bp.py'), tmp, bp, out], check=True, capture_output=True)
    page = open(out, encoding='utf-8').read(); shutil.rmtree(tmp)
    return page[page.index('<section class="sec cta'):].split('>', 1)[0]


def no_fields(short):
    def change(beat): beat.pop('fields', None); beat['h2'] = 'Start today' if short else 'A much longer closing sentence that asks the reader to do a thing now'
    return change


def test_a_short_line_stands_left_and_a_rounded_page_gets_a_panel():
    assert 'cta-line' in render('butter', no_fields(True)) and 'cta-inset' in render('butter', no_fields(True))


def test_a_square_page_keeps_the_full_band():
    tag = render('atelier', no_fields(True)); assert 'cta-line' in tag and 'cta-inset' not in tag


def test_a_long_line_stays_centred():
    assert 'cta-line' not in render('atelier', no_fields(False))


def test_a_form_keeps_its_own_closing():
    assert 'cta-line' not in render('butter', lambda beat: None)


def test_an_action_carries_one_arrow():
    """A label that brings its own arrow from the client's page (here in the direction and in the inventory alike) is drawn with one."""
    tmp = tempfile.mkdtemp()
    for name in ('direction', 'images', 'assets', 'inventory'):
        text = open(os.path.join(ROOT, 'tests', f'{name}.sample.json'), encoding='utf-8').read()
        open(os.path.join(tmp, f'{name}.json'), 'w', encoding='utf-8').write(text.replace('Rezerviši sto', 'Rezerviši sto →'))
    out = os.path.join(tmp, 'page.html')
    subprocess.run([sys.executable, os.path.join(ROOT, 'lib', 'render', 'render_bp.py'), tmp, 'atelier', out], check=True, capture_output=True)
    page = open(out, encoding='utf-8').read(); shutil.rmtree(tmp)
    assert 'Rezerviši sto <span class="ar">' in page and '→ <span class="ar">' not in page
