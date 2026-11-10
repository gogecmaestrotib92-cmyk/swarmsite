"""On a phone running text steps down from a desk size and a section's heading keeps its rank over the words under it."""
import os, re, shutil, subprocess, sys, tempfile
ROOT = os.path.join(os.path.dirname(__file__), '..')


def css_of(bp):
    tmp = tempfile.mkdtemp()
    for name in ('direction', 'images', 'assets', 'inventory'):
        shutil.copy(os.path.join(ROOT, 'tests', f'{name}.sample.json'), os.path.join(tmp, f'{name}.json'))
    out = os.path.join(tmp, 'page.html')
    subprocess.run([sys.executable, os.path.join(ROOT, 'lib', 'render', 'render_bp.py'), tmp, bp, out], check=True, capture_output=True)
    page = open(out, encoding='utf-8').read(); shutil.rmtree(tmp)
    return page


def phone_body(page):
    return float(re.search(r'@media\(max-width:600px\)\{:root\{--body-px:([\d.]+)px\}', page).group(1))


def test_a_large_desk_size_steps_down_on_a_phone():
    assert phone_body(css_of('butter')) == 18      # 21 px grotesque at a desk
    assert phone_body(css_of('white-desert')) == 20   # 22 px serif at a desk: drawn narrower, keeps more


def test_a_size_that_already_fits_is_left_alone():
    assert phone_body(css_of('atelier')) == 16


def test_a_section_heading_has_a_floor_on_a_phone():
    assert 'font-size:min(max(var(--fs),32px)' in css_of('atelier')
