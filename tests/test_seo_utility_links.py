"""The controls of a shop are not pages: the cart, the checkout and the customer's account are left out of the links a
redesign must keep, and a category tile whose anchor is only a count is named by its path. A product site's sign-up stays."""
import json, re, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'lib'))
import seo as SEO

INVENTORY = {'url': 'https://www.example.test/', 'actions': [
    {'text': '0', 'href': 'https://example.test/cesta/'}, {'text': 'CREATE AN ACCOUNT', 'href': 'https://example.test/mi-cuenta/?action=register'},
    {'text': 'Buy', 'href': 'https://example.test/shop/?add-to-cart=41'}, {'text': 'Checkout', 'href': 'https://example.test/checkout'},
    {'text': '8 products', 'href': 'https://example.test/categorias-productos/la-carta/del-mar/'}, {'text': '12', 'href': 'https://example.test/categorias/carnes-a-la-brasa/'},
    {'text': 'Start free', 'href': 'https://example.test/register?plan=pro'}, {'text': 'Sign in', 'href': 'https://example.test/login'},
    {'text': 'The cart of the house', 'href': 'https://example.test/menu/cart-of-the-day/'}, {'text': 'La carta', 'href': 'https://example.test/carta/'}]}


class UtilityLinks(unittest.TestCase):
    def test_the_shops_controls_are_not_links_to_keep(self):
        kept = {l['href']: l['text'] for l in SEO.internal_links(INVENTORY)}
        for gone in ('https://example.test/cesta/', 'https://example.test/mi-cuenta/?action=register', 'https://example.test/shop/?add-to-cart=41', 'https://example.test/checkout'): self.assertNotIn(gone, kept)
        self.assertEqual(kept['https://example.test/register?plan=pro'], 'Start free', 'a product site\'s sign-up is the point of its page'); self.assertIn('https://example.test/login', kept)
        self.assertIn('https://example.test/menu/cart-of-the-day/', kept, 'a page that only has the word in its name is a page'); self.assertIn('https://example.test/carta/', kept)

    def test_a_tile_whose_anchor_is_a_count_is_named_by_its_path(self):
        kept = {l['href']: l['text'] for l in SEO.internal_links(INVENTORY)}
        self.assertEqual(kept['https://example.test/categorias-productos/la-carta/del-mar/'], 'Del mar'); self.assertEqual(kept['https://example.test/categorias/carnes-a-la-brasa/'], 'Carnes a la brasa')

    def test_the_contract_grades_the_promise_on_the_same_list(self):
        source = (ROOT / 'lib/qa/contract.mjs').read_text(); listed = set(re.findall(r"'([a-z-]+)'", source[source.index('const UTILITY = new Set(['):source.index(']);', source.index('const UTILITY = new Set(['))]))
        self.assertEqual(listed, SEO.UTILITY_SEGMENTS, 'lib/seo.py and lib/qa/contract.mjs name the same controls')


if __name__ == '__main__': unittest.main()
