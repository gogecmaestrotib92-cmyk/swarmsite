import base64
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'lib' / 'swarm'))
import agents

class ProductHeroReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.p = self.tmp.name
        im = Image.new('RGB', (800, 600), (40, 80, 140)); buf = io.BytesIO(); im.save(buf, 'PNG')
        self.image = {'id': 'visual', 'data': 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode(), 'w': 800, 'h': 600}
        agents.W(self.p, 'images.json', [self.image])
        agents.W(self.p, 'factsheet.json', {'business_understanding': {'offer': 'An analysis tool', 'visual_priority': 'Actual product interface'}})
        agents.W(self.p, 'direction.json', {'kind': 'software', 'hero': {'media': 'visual'}, 'beats': []})
    def test_rejects_decorative_visual_and_reuses_review_only_for_same_bytes(self):
        with patch.object(agents, 'ask', return_value={'decision':'NOT_PRODUCT','observed':'decorative'} ) as ask:
            agents.review_software_hero(self.p); self.assertFalse(agents.J(self.p,'direction.json')['hero']['visual_verified'])
            agents.review_software_hero(self.p); self.assertEqual(ask.call_count, 1)
            agents.W(self.p,'factsheet.json',{'business_understanding':{'offer':'A different product'}})
            agents.review_software_hero(self.p); self.assertEqual(ask.call_count, 2)
            im = Image.new('RGB',(800,600),(180,30,10)); buf=io.BytesIO(); im.save(buf,'PNG')
            self.image['data']='data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode(); agents.W(self.p,'images.json',[self.image])
            agents.review_software_hero(self.p); self.assertEqual(ask.call_count, 3)
    def test_missing_or_unavailable_review_fails_closed(self):
        with patch.object(agents, 'ask', side_effect=RuntimeError('unavailable')):
            agents.review_software_hero(self.p)
        self.assertFalse(agents.J(self.p,'direction.json')['hero']['visual_verified'])
    def test_restaurant_photo_is_not_reviewed_as_software(self):
        d=agents.J(self.p,'direction.json'); d['kind']='place'; agents.W(self.p,'direction.json',d)
        with patch.object(agents,'ask') as ask: agents.review_software_hero(self.p); ask.assert_not_called()

if __name__ == '__main__': unittest.main()
