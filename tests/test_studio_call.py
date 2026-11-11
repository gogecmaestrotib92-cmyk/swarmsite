"""A composing call that comes back as prose, or runs out of room, is asked once more before the variant is given up."""
import os, sys, types
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib', 'studio'))
import _evidence as E

TOOL = {'name': 'compose_page', 'description': 'd', 'input_schema': {'type': 'object', 'properties': {}}}


def fake(answers, sent):
    class Block:
        def __init__(self, kind, value): self.type = kind; self.text = value if kind == 'text' else ''; self.input = value if kind == 'tool_use' else None
    class Stream:
        def __init__(self, kw): sent.append(kw); self.kw = kw
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def get_final_message(self):
            stop, kind, value = answers.pop(0)
            return types.SimpleNamespace(content=[Block(kind, value)], stop_reason=stop, usage=types.SimpleNamespace(input_tokens=10, output_tokens=5, cache_creation_input_tokens=0, cache_read_input_tokens=0))
    client = types.SimpleNamespace(messages=types.SimpleNamespace(stream=lambda **kw: Stream(kw)))
    return types.SimpleNamespace(Anthropic=lambda: client)


def run(monkeypatch, answers):
    sent = []; monkeypatch.setitem(sys.modules, 'anthropic', fake(answers, sent)); E.USAGE.clear()
    return sent


def test_prose_is_answered_by_naming_the_tool(monkeypatch):
    sent = run(monkeypatch, [('end_turn', 'text', 'Here is my plan…'), ('tool_use', 'tool_use', {'scenes': []})])
    assert E.call('s', 'c', 'a-compose-0', tool=TOOL) == {'scenes': []}
    assert len(sent) == 2 and sent[1]['messages'][-1]['role'] == 'user' and 'compose_page' in sent[1]['messages'][-1]['content'] and len(E.USAGE) == 2


def test_an_answer_cut_off_gets_more_room(monkeypatch):
    sent = run(monkeypatch, [('max_tokens', 'text', ''), ('tool_use', 'tool_use', {'ok': 1})])
    assert E.call('s', 'c', 'a', tool=TOOL, max_tokens=1000) == {'ok': 1}
    assert sent[1]['max_tokens'] > 1000 and len(sent[1]['messages']) == 1


def test_two_failures_say_how_each_stopped_and_a_refusal_is_not_pressed(monkeypatch):
    run(monkeypatch, [('end_turn', 'text', 'x'), ('end_turn', 'text', 'y')])
    try: E.call('s', 'c', 'a', tool=TOOL); raise AssertionError('should have failed')
    except RuntimeError as err: assert 'end_turn' in str(err)
    sent = run(monkeypatch, [('refusal', 'text', '')])
    try: E.call('s', 'c', 'a', tool=TOOL); raise AssertionError('should have failed')
    except RuntimeError as err: assert 'refusal' in str(err) and len(sent) == 1


def test_nothing_is_composed_from_nothing_and_an_empty_page_is_not_clean(tmp_path, monkeypatch):
    import studio as ST, scenes as S
    sent = run(monkeypatch, [])
    try: ST.build(str(tmp_path / 'missing'), str(tmp_path / 'out')); raise AssertionError('should have refused')
    except RuntimeError as err: assert 'no text' in str(err) and not sent, 'refused before any model call'
    plan = {'brand': {'name': '', 'accent': ''}, 'scenes': [{'scene': 'open-statement', 'slots': {'h1': ''}}, {'scene': 'close', 'slots': {'line': ''}}]}
    bad = ST.check(plan, S.page(plan, {}), {'links': []}, set(), {})
    assert 'the opening has no headline' in bad['structure'] and 'the page says almost nothing' in bad['structure']


def test_a_picture_without_detail_is_soft_kept_small_and_never_shown_across_the_screen():
    import base64, io, studio as ST, scenes as S
    from PIL import Image, ImageDraw, ImageFilter
    sharp = Image.new('RGB', (1200, 800), '#ddd'); d = ImageDraw.Draw(sharp)
    for k in range(0, 1200, 24): d.line([(k, 0), (1200 - k, 800)], fill='#111', width=3)
    def uri(im): b = io.BytesIO(); im.save(b, 'PNG'); return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()
    blurred = sharp.filter(ImageFilter.GaussianBlur(14))
    assert E.soft(uri(blurred)) and not E.soft(uri(sharp)) and not E.soft('data:image/png;base64,AAAA'), 'a picture that cannot be read is not called soft'
    images = {'a': {'id': 'a', 'data': uri(blurred), 'w': 1200, 'h': 800, 'soft': True}, **{k: {'id': k, 'data': uri(sharp), 'w': 1200, 'h': 800, 'soft': False} for k in 'bc'}}
    plan = {'brand': {'name': 'X', 'accent': '#2af6a0'}, 'scenes': [{'scene': 'open-statement', 'slots': {'h1': 'A / line'}}, {'scene': 'window', 'slots': {'image': 'a'}},
            {'scene': 'scatter', 'slots': {'h2': 'Work', 'items': [{'image': k, 'title': k.upper(), 'tag': 't'} for k in 'abc']}}, {'scene': 'close', 'slots': {'line': 'End'}}]}
    page = S.page(plan, images)
    assert any('out of focus' in x for x in ST.check(plan, page, {'links': []}, set(), images)['pictures'])
    grid = page.split('class="sc-grid"')[1]
    assert grid.index('<b>A</b>') > grid.index('<b>B</b>') and 'max-width:max(17.5rem,744px)' in grid, 'the soft picture takes the smallest place and stays under its own size'
