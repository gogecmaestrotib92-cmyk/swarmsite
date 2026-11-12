"""lettering.py — does a client's photograph carry words drawn into it (a flyer, a crest, a poster, a screenshot)?

    words(path) -> [str] | None        the words OCR reads with confidence; None when no OCR is installed
    mark(data, folder) -> {src: [words]}   sets `lettering: true` on each of data.media.photos whose file carries
                                           two or more words; `lettering: false` on the rest when OCR could read them

A template that sets type over a photograph or uses it as a ground leaves out one marked `lettering: true` (iip,
dawnsaunders read the mark). Tesseract is the reader (installed in the worker image); without it nothing is marked
and the templates fall back on the alt. No model, no network.
"""
import re
import shutil
import subprocess
from pathlib import Path

MIN_CONF = 70


def words(path, timeout=20):
    exe = shutil.which('tesseract')
    if not exe:
        return None
    try:
        r = subprocess.run([exe, str(path), 'stdout', '--psm', '11', 'tsv'], capture_output=True, timeout=timeout)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        return []                                                   # a file OCR cannot open is read as carrying no words
    out = []
    for line in r.stdout.decode('utf-8', 'replace').splitlines()[1:]:
        col = line.split('\t')
        if len(col) < 12:
            continue
        try:
            conf = float(col[10])
        except ValueError:
            continue
        w = col[11].strip()
        # a word: three letters or more, mostly letters, read with confidence — not the noise OCR finds in grass or a crowd
        if conf >= MIN_CONF and len(re.sub(r'[^A-Za-zÀ-ÿ]', '', w)) >= 3 and len(re.sub(r'[^A-Za-zÀ-ÿ]', '', w)) >= len(w) * .7:
            out.append(w)
    return out


def mark(data, folder):
    found = {}
    for p in ((data.get('media') or {}).get('photos') or []):
        f = Path(folder) / str(p.get('src') or '')
        if not p.get('src') or not f.is_file():
            continue
        ws = words(f)
        if ws is None:
            return found                                             # no OCR here: nothing is marked
        p['lettering'] = len(ws) >= 2
        if ws:
            found[p['src']] = ws[:12]
    return found
