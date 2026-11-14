"""A page that speaks to the API as the visitor loads the sign-in library before auth.js.

auth.js is switched on only when `window.supabase` is there (Auth.enabled). The editor loaded auth.js without the
library, so every request from it went without the visitor's token: a signed-in visitor pressing "Prepare my
download" was answered 401, sent to the sign-in page and from there straight back (owner, on production, 2026-11-14)."""
import re
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent / 'web'


def test_every_page_with_auth_js_loads_the_sign_in_library_first():
    pages = [p for p in sorted(WEB.glob('*.html')) if '/js/auth.js' in p.read_text(encoding='utf-8')]
    assert {p.name for p in pages} >= {'app.html', 'edit.html', 'dashboard.html', 'login.html'}
    for p in pages:
        s = p.read_text(encoding='utf-8')
        lib, auth = s.find('supabase.min.js'), s.find('/js/auth.js')
        assert 0 <= lib < auth, '%s: the sign-in library is loaded before auth.js' % p.name
        tag = lambda at: s[s.rfind('<script', 0, at):s.find('>', at)]
        assert ('defer' in tag(lib)) == ('defer' in tag(auth)) or 'defer' not in tag(lib), '%s: auth.js must not run before the library' % p.name
        assert not re.search(r'<script[^>]*\basync\b[^>]*supabase', s), p.name
