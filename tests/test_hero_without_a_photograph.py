"""A hero gets a picture only if the picture can carry a hero. Seen on a real restaurant job: the only captured image
was an 800px funding notice (logos and a text block), nothing was assigned to the hero, and the renderer's last resort
took it anyway and stretched it across the first screen behind the headline. A place or a service without a photograph
opens with the typographic hero — whatever the blueprint's own hero looks like — never with an empty dark frame."""
import base64, io, json, os, re, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]


def notice(width=800, height=773):
    """A light graphic with rows of 'text': real pixels, not empty, and nothing a hero should show."""
    im = Image.new('RGB', (width, height), '#f4f4f4'); draw = ImageDraw.Draw(im)
    for y in range(60, height - 40, 46): draw.rectangle((60, y, width - 80 - (y % 7) * 30, y + 14), fill='#333333')
    draw.rectangle((60, 20, 220, 50), fill='#003399')
    out = io.BytesIO(); im.save(out, 'PNG'); return 'data:image/png;base64,' + base64.b64encode(out.getvalue()).decode()


def render(kind, blueprint, images, edit=None):
    with tempfile.TemporaryDirectory() as temp:
        job = Path(temp)
        for name in ('direction', 'inventory', 'assets'):
            src = ROOT / 'tests' / f'{name}.sample.json'
            if src.is_file(): shutil.copy(src, job / f'{name}.json')
        d = json.loads((job / 'direction.json').read_text()); d['kind'] = kind
        d['hero']['media'] = ''; d['hero'].setdefault('ui', {}).pop('move', None)
        for beat in d['beats']:
            beat.pop('image', None)
            if isinstance(beat.get('ui'), dict): beat['ui'].pop('lead', None)
        if edit: edit(d)
        (job / 'direction.json').write_text(json.dumps(d)); (job / 'images.json').write_text(json.dumps(images))
        out = job / 'page.html'
        r = subprocess.run([sys.executable, str(ROOT / 'lib/render/render_bp.py'), str(job), blueprint, str(out)], capture_output=True, text=True, env={**os.environ, 'LIVETEST': '1'})
        assert r.returncode == 0, r.stderr
        html = out.read_text()
        start = html.index('<section class="sec hero'); hero = html[start:html.index('</section>', start)]
        return hero, re.match(r'<section class="([^"]*)"', hero).group(1), html


class HeroWithoutAPhotograph(unittest.TestCase):
    def test_a_small_text_graphic_is_not_stretched_into_a_place_hero(self):
        data = notice()
        for blueprint in ('tengile', 'white-desert', 'belgrade-arbor', 'units'):
            hero, classes, html = render('place', blueprint, [{'id': 'img1', 'w': 800, 'h': 773, 'lum': 208, 'data': data, 'src': 'https://example.test/escritorio-1.png'}])
            self.assertIn('typo', classes.split(), f'{blueprint}: {classes}')
            self.assertNotIn('has-media', classes.split(), blueprint)
            self.assertNotIn(data, hero, f'{blueprint}: the notice must not be the hero picture')
            self.assertIn('<h1', hero)

    def test_no_image_at_all_is_the_typographic_hero_not_an_empty_frame(self):
        for kind, blueprint in (('place', 'tengile'), ('place', 'white-desert'), ('service', 'lpas'), ('service', 'aino'), ('service', 'atelier')):
            hero, classes, _ = render(kind, blueprint, [])
            self.assertIn('typo', classes.split(), f'{kind}/{blueprint}: {classes}')
            self.assertNotIn('has-media', classes.split(), f'{kind}/{blueprint}')
            self.assertNotIn('<img', hero)

    def test_a_real_photograph_still_makes_the_photo_hero(self):
        photos = json.loads((ROOT / 'tests' / 'images.sample.json').read_text())
        hero, classes, _ = render('place', 'tengile', photos)
        self.assertIn('has-media', classes.split(), classes); self.assertNotIn('typo', classes.split())
        self.assertIn('<img', hero)

    def test_an_assigned_photograph_is_still_honoured(self):
        photos = json.loads((ROOT / 'tests' / 'images.sample.json').read_text())
        def edit(d): d['hero']['media'] = photos[1]['id']
        hero, classes, _ = render('place', 'tengile', photos, edit)
        self.assertIn(photos[1]['data'], hero)

    def test_software_may_still_frame_what_it_has(self):
        shot = {'id': 'shot1', 'w': 1280, 'h': 800, 'shot': True, 'data': notice(1280, 800)}
        hero, classes, _ = render('software', 'cerebrium', [shot])
        self.assertIn(shot['data'], hero, 'a software page with only a section shot keeps showing it, framed')
        self.assertNotIn('typo', classes.split())

    def test_the_passed_over_graphic_is_not_placed_anywhere_as_a_photograph_of_the_place(self):
        data = notice()
        _, _, html = render('place', 'tengile', [{'id': 'img1', 'w': 800, 'h': 773, 'lum': 208, 'data': data}])
        self.assertNotRegex(html, r'class="media"><img src="' + re.escape(data[:60]))


if __name__ == '__main__':
    unittest.main()
