"""SEO-safe mode: the rebuild keeps the words, the headings' keywords, the internal links and the head of a page that already ranks."""
import json, os, sys, shutil, tempfile, unittest, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'lib')); sys.path.insert(0, str(ROOT / 'lib/render')); sys.path.insert(0, str(ROOT / 'lib/swarm'))
import seo as SEO
import render_bp as render
import agents

class SeoSafeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, self.tmp, True)
        for name, src in [('direction.json', 'tests/direction.sample.json'), ('images.json', 'tests/images.sample.json'), ('inventory.json', 'tests/inventory.seo.sample.json')]:
            shutil.copy(ROOT / src, Path(self.tmp) / name)

    def render(self, mode):
        Path(self.tmp, 'brief.json').write_text(json.dumps({'mode': mode}))
        out = Path(self.tmp, f'{mode}.html'); render.build(self.tmp, 'tengile', str(out)); return out.read_text()

    def test_keywords_and_coverage(self):
        self.assertEqual(SEO.keywords('Restoran Franš — bašta u srcu Beograda'), ['restoran', 'franš', 'bašta', 'srcu', 'beograda'])
        self.assertGreaterEqual(SEO.keyword_coverage('Catering y eventos en Alcorcón', 'Eventos que se recuerdan en Alcorcón'), .6)
        self.assertEqual(SEO.text_coverage('', 'anything'), 1.0)

    def test_safe_mode_carries_head_archive_and_links(self):
        html = self.render('seo-safe')
        self.assertIn('<link rel="canonical" href="https://frans.rs/">', html)
        self.assertIn('hreflang="en"', html); self.assertIn('application/ld+json', html); self.assertIn('"@type": "Restaurant"', html)
        self.assertIn('id="more"', html)  # the archive keeps every source section the page did not place
        for title in ('Jelovnik i vinska karta', 'Proslave i poslovni ručkovi', 'Česta pitanja'): self.assertIn(title, html)
        self.assertIn('besplatan parking', html)  # FAQ answers survive
        for href in ('https://frans.rs/jelovnik', 'https://frans.rs/proslave', 'https://frans.rs/rezervacija'): self.assertIn(href, html)
        self.assertNotIn('instagram.com', html.split('id="more"')[1].split('</section>')[0])  # external links are not "lost internal links"
        self.assertIn('</h2></summary>', html)  # archived headings stay headings

    def test_free_mode_is_the_studio_page(self):
        html = self.render('free')
        self.assertNotIn('id="more"', html); self.assertNotIn('rel="canonical"', html); self.assertNotIn('application/ld+json', html)

    def test_copy_agent_cannot_drop_h1_keywords_in_safe_mode(self):
        Path(self.tmp, 'brief.json').write_text(json.dumps({'mode': 'seo-safe'}))
        n = agents.apply_copy(self.tmp, {'edits': [{'path': 'hero.h1', 'value': 'Dinner worth the drive'}]})
        self.assertEqual(n, 0)
        n = agents.apply_copy(self.tmp, {'edits': [{'path': 'hero.h1', 'value': 'Restoran Franš: <em>bašta</em> Beograda'}]})
        self.assertEqual(n, 1)
        Path(self.tmp, 'brief.json').write_text(json.dumps({'mode': 'free'}))
        self.assertEqual(agents.apply_copy(self.tmp, {'edits': [{'path': 'hero.h1', 'value': 'Dinner worth the drive'}]}), 1)

    def test_contract_reports_the_seo_diff(self):
        html = self.render('seo-safe')
        r = subprocess.run(['node', str(ROOT / 'lib/qa/contract.mjs'), str(Path(self.tmp, 'seo-safe.html')), '--dir', self.tmp], capture_output=True, text=True, env={**os.environ, 'LIVETEST': '1'}, timeout=240)
        self.assertEqual(r.returncode, 0, r.stderr[-400:])
        rep = json.load(open(Path(self.tmp, 'contract.json'))); seo = rep['seo']
        self.assertEqual(seo['mode'], 'seo-safe'); self.assertGreaterEqual(seo['text_kept'], .95)
        self.assertEqual(seo['links']['kept'], seo['links']['total']); self.assertTrue(all(seo['meta'].values()))
        ids = {i['id'] for i in rep['items']}; self.assertTrue({'seo-text-kept', 'seo-h1-keywords', 'seo-links-kept', 'seo-meta'} <= ids)

if __name__ == '__main__': unittest.main()
