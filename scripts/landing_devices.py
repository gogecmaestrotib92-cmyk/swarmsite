"""landing_devices.py — our own landing carries the engine's devices, the same code a client's page is built with.

  python3 scripts/landing_devices.py          write the devices named in web/index.html into it
  python3 scripts/landing_devices.py --check  exit 1 when the page's copy differs from the library (the test runs this)

web/index.html names the devices it uses in <style id="dv-css" data-devices="line-rise,rise-stagger,…">. This writes
lib/devices/registry.py's stylesheet for exactly those into that element and their script into <script id="dv-js">,
inline, as lib/studio/scenes.py does for a composed page: the script is what adds the class that lets motion start, so
it must run before the first paint or a headline would be seen, taken away and brought back. Nothing here is edited by
hand — change a device in the library, run this, and the landing moves with every client page."""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'lib', 'devices'))
import registry as LIB

PAGE = os.path.join(ROOT, 'web', 'index.html')
STYLE = re.compile(r'(<style id="dv-css" data-devices="([^"]*)">)(.*?)(</style>)', re.S)
SCRIPT = re.compile(r'(<script id="dv-js">)(.*?)(</script>)', re.S)


def devices(html):
    """The ids the page names, in the order it names them. An id the library does not have is an error, not a silence."""
    found = STYLE.search(html)
    if not found: raise SystemExit('web/index.html has no <style id="dv-css" data-devices="…">')
    ids = [i.strip() for i in found.group(2).split(',') if i.strip()]
    unknown = [i for i in ids if i not in LIB.DEVICES]
    if unknown: raise SystemExit(f'web/index.html names devices the library does not have: {unknown}')
    return ids


def filled(html):
    """The page with the library's code for its devices in place. The script stands in a block of its own, so its names are not the page's."""
    css, js = LIB.bundle(devices(html))
    html = STYLE.sub(lambda m: m.group(1) + css + m.group(4), html, count=1)
    if not SCRIPT.search(html): raise SystemExit('web/index.html has no <script id="dv-js">')
    return SCRIPT.sub(lambda m: m.group(1) + '{' + js + '}' + m.group(3), html, count=1)


if __name__ == '__main__':
    now = open(PAGE, encoding='utf-8').read(); want = filled(now)
    if '--check' in sys.argv:
        if now != want: print('web/index.html does not carry the library\'s current devices — run python3 scripts/landing_devices.py'); sys.exit(1)
        print('web/index.html carries the library\'s devices:', ', '.join(devices(now)))
    else:
        open(PAGE, 'w', encoding='utf-8').write(want); print('written:', ', '.join(devices(now)), f'({len(want) - len(now):+d} bytes)')
