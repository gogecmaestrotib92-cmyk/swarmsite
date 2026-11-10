"""Words beside a picture keep a column a heading can be set in, and a heading that would run as single words is refused."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib', 'compose'))
import pictures as P

PAGE = {'container': 1300, 'frame': 40}
content = lambda heading, shot=True: {'picture': {'w': 1152, 'h': 615, 'shot': shot}, 'words': {'heading': heading, 'chars': 200, 'rows': 0}}


def test_the_words_column_never_falls_under_its_minimum():
    for cols in (6, 7, 8, 9):
        g = P.geometry({'form': 'stage', 'side': 'right', 'cols': cols}, content('A heading'), PAGE)
        assert g['words'] >= P.WORDS_MIN, cols


def test_the_stylesheet_holds_the_same_minimum_at_any_width():
    assert '--pc-words-min:calc(var(--pc-edge) + clamp(32px,6vw,104px) + 22.5rem)' in P.CSS and P.CSS.count('minmax(min(100%,var(--pc-words-min)),1fr)') == 2


def test_a_heading_that_would_run_as_single_words_is_refused():
    why = P._heading_fits({'form': 'stage', 'title': 'lg'}, content('What could your book earn for you this year'), PAGE, 360)
    assert why and 'lines' in why
    assert P._heading_fits({'form': 'stage', 'title': 'md'}, content('What could your book earn?'), PAGE, 360) is None
