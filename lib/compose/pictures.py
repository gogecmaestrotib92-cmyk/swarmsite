"""pictures.py — a section that shows one picture, drawn the way a studio would use that picture.

The production renderer draws a picture section in the one form its blueprint has: a boxed picture and its words
beside it. A picture composition names such sections and says what the picture does instead: it becomes the ground the
words stand on, it runs off the edge of the screen from top to bottom, it crosses the page as a strip, it carries the
words on a card laid over its corner, it is cut to another proportion and hung off the line of the text, or — when it
is evidence of a product — it is shown whole on a stage. Like every composition it cannot say anything: the words
block, the picture and whatever the section holds after them come from the page through lib/compose/sections.py, byte
for byte, and the section keeps its id and its band.

What decides which forms a picture may take is the picture itself: its pixels (never shown past 1.35× of them, a
screenshot never past 1×), and whether it is a photograph or a screenshot (a screenshot is never cropped, toned or
written over). The validator knows the size each form would draw it at a 1440×900 screen before a pixel is drawn.

  validate(doc, page_html, images=None) → [{'code', 'at', 'message'}]        ([] = may be drawn)
  transplant(page_html, doc, images=None) → (page_html, {'drawn', 'errors', 'sections'})
  readable(page_html, images=None)      → {section id: content | reason} for the picture sections of the page, and for the
                                          sections of words that one of the job's unused pictures is offered to (`offers`)
  open_forms(content, page)             → the forms this section's picture may take, with what each would draw
  a document: {"ir": "0.2", "pictures": [{"section": id, "form": backdrop|bleed|panorama|card|offset|stage|inline, …}],
               "galleries": [{"sections": [ids of two to four neighbouring picture sections], "ratio", "title", "tone", "enter"}]}
               a gallery runs neighbouring photographs side by side in one row, each over its own heading and words
Deterministic, no network, no model. A document that fails is refused whole and the page comes back untouched."""
import base64, html as H, io, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import content as CONTENT
import sections as SECTIONS
import validate as V
FACES = V.FACES

e = lambda s: H.escape(str(s if s is not None else ''), quote=True)
FORMS = ('backdrop', 'bleed', 'panorama', 'card', 'offset', 'stage', 'inline')
COVERING = ('backdrop', 'bleed', 'panorama', 'card')   # forms that crop the picture to the space they give it
SIDES = ('left', 'right')
PLACES = ('bottom-left', 'bottom-right', 'top-left', 'center', 'left', 'right')
HEIGHTS = {'md': 62, 'lg': 78, 'screen': 100}             # the least a section stands, in hundredths of the screen's height
SCRIMS = ('soft', 'mid', 'deep')
PANORAMAS = ('2/1', '21/9', '3/1')
CARD_RATIOS = ('1/1', '4/5', '4/3', '3/2', '16/10', '16/9')
OFFSET_RATIOS = ('own',) + V.RATIOS
FRAMES = ('none', 'paper', 'browser')
GROUNDS = ('accent', 'ink', 'alt', 'own')   # own: the colour the picture's own edges share — the section takes it and the picture has no box
EDGES = ('fade', 'hard')
CROPS = ('whole', 'fade')
GALLERY_KEYS = {'sections', 'ratio', 'title', 'tone', 'enter'}
GALLERY_RATIOS = ('1/1', '4/5', '3/4', '4/3', '3/2')
GALLERY_WORDS = 320    # characters each section of a gallery may say: more makes columns of ragged length
DISSOLVE = 0.45        # how far apart in lightness (0–1) a picture's inner edge and its section's ground may be for the edge to dissolve
INLINE_WORDS = 140     # a picture set into the heading needs at least this many characters in its section
CROP_RATIO = 1.5   # the proportion a fading crop shows of a screen: wider than this and it is shown whole
PILLS = {'pill': 2.6, 'soft': 1.7, 'circle': 1.1}   # the width of a picture set into the heading, in em of the heading; it stands 1.1 em tall
PILL_EM = 1.1
TITLES = ('md', 'lg', 'xl')
TITLE_PX = {'md': 46.1, 'lg': 63.4, 'xl': 89.3}           # what each heading size comes to at a 1440 screen
ALIGN = ('start', 'center', 'end')
ANCHORS = ('top', 'middle', 'bottom')
DROPS = ('none', 'up', 'down')
WORDS = ('above', 'below')
VIEW = (1440, 900)
GUTTER = 32
WORDS_ON_PICTURE = 420   # characters a reader takes in over a photograph; more than that wants a plain ground
ROWS_ON_PICTURE = 4
MIN_PICTURE_PX = 240     # under this a picture is an icon, not a picture

COMMON = {'section', 'form', 'title', 'enter', 'picture'}   # picture: for a section of words, the address of the offered picture it takes
TREATED = {'tone', 'grain', 'focal', 'scroll'}
KEYS = {
    'backdrop': COMMON | TREATED | {'place', 'height', 'scrim'},
    'bleed': COMMON | TREATED | {'side', 'cols', 'height', 'align', 'edge', 'overlap'},
    'panorama': COMMON | TREATED | {'ratio', 'words'},
    'card': COMMON | TREATED | {'side', 'cols', 'ratio', 'anchor', 'bleed'},
    'offset': COMMON | (TREATED - {'scroll'}) | {'side', 'cols', 'ratio', 'shape', 'tilt', 'shadow', 'frame', 'drop', 'align'},
    'stage': COMMON | {'side', 'cols', 'ground', 'tilt', 'align', 'height', 'crop'},
    'inline': COMMON | {'tone', 'focal', 'at', 'shape'},
}
COLS = {'bleed': (5, 7), 'card': (7, 9), 'offset': (3, 7), 'stage': (5, 8)}
DEFAULT_COLS = {'bleed': 6, 'card': 8, 'offset': 5, 'stage': 6}

CSS = """
.sec.pc{--pc-bg:var(--paper);--pc-pad:clamp(56px,8vw,128px);--pc-edge:max(var(--frame,24px),calc((100vw - var(--container,1300px)) / 2 + var(--frame,24px)))}
.sec.pc.band-dark{--pc-bg:var(--band-paper)}.sec.pc.band-alt{--pc-bg:var(--alt,color-mix(in srgb,var(--ink) 6%,var(--paper)))}.sec.pc.band-accent{--pc-bg:var(--accent)}
.sec.pc .pc-fig{position:relative;margin:0;padding:0;width:auto;max-width:none;max-height:none;overflow:hidden;border:0;border-radius:0;aspect-ratio:auto;order:0;justify-self:stretch}
.sec.pc .pc-fig img{display:block;width:100%;height:100%;max-width:none;max-height:none;margin:0;object-fit:cover;object-position:var(--focal,50% 50%)}
.sec.pc .pc-fig>i{position:absolute;inset:0;pointer-events:none}
.sec.pc .pc-tone{isolation:isolate;background:#808080}.sec.pc .pc-tone img{mix-blend-mode:luminosity}.sec.pc .pc-tone-tint{background:var(--accent)}
.sec.pc .pc-t-light{z-index:1;background:var(--pc-light);mix-blend-mode:multiply}.sec.pc .pc-t-dark{z-index:2;background:var(--pc-dark);mix-blend-mode:lighten}
.sec.pc .pc-grain{z-index:2;mix-blend-mode:overlay;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='240' height='240'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.8' numOctaves='2' seed='7' stitchTiles='stitch'/%3E%3CfeColorMatrix values='0 0 0 0 .5 0 0 0 0 .5 0 0 0 0 .5 0 0 0 .6 0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")}
.sec.pc .pc-words{min-width:0;padding:0;margin:0;overflow-wrap:break-word;order:0}
.sec.pc .pc-words .rows li b{flex-shrink:0;max-width:100%;overflow-wrap:break-word}
.sec.pc .pc-words .h2{text-wrap:balance;overflow-wrap:normal}.sec.pc .pc-words .h2.light{color:inherit}
.sec.pc .pc-words .cap,.sec.pc .pc-words .lede{font-size:clamp(17px,1.35vw,21px);line-height:1.5;max-width:44ch;margin-top:clamp(14px,1.6vw,24px)}
.sec.pc.pc-t-md .pc-words .h2{font-size:min(clamp(28px,3.2vw,46px),calc((100vw - 48px) / var(--lw,8) * 1.72))!important;line-height:1.06}
.sec.pc.pc-t-lg .pc-words .h2{font-size:min(clamp(34px,4.4vw,64px),calc((100vw - 48px) / var(--lw,8) * 1.72))!important;line-height:1.02}
.sec.pc.pc-t-xl .pc-words .h2{font-size:min(clamp(40px,6.2vw,96px),calc((100vw - 48px) / var(--lw,8) * 1.72))!important;line-height:.98;letter-spacing:var(--h1-ls,-.03em)}
.sec.pc .pc-al-start{align-content:start;align-self:start}.sec.pc .pc-al-center{align-content:center;align-self:center}.sec.pc .pc-al-end{align-content:end;align-self:end}
.sec.pc.pc-flush{padding:0;display:block}
.sec.pc.pc-flush .pc-tail{padding:clamp(20px,3vw,40px) 0 clamp(40px,6vw,80px)}.sec.pc.pc-flush .pc-tail>:first-child{margin-top:0}
.sec.pc .pc-field{position:relative;display:grid;min-height:var(--pc-h,auto)}
.sec.pc .pc-col{display:grid;min-width:0;padding:var(--pc-pad) var(--pc-edge) var(--pc-pad) clamp(32px,6vw,104px)}
.sec.pc.pc-side-right .pc-col{padding:var(--pc-pad) clamp(32px,6vw,104px) var(--pc-pad) var(--pc-edge)}
.sec.pc .pc-col .pc-words{max-width:34rem}.sec.pc.pc-side-right .pc-col .pc-words{justify-self:end;width:100%}

.sec.pc.pc-f-backdrop .pc-field{overflow:hidden;isolation:isolate;background:#15130f;color:var(--on-photo,#F4EFE3)}
.sec.pc.pc-f-backdrop .pc-fig{position:absolute;inset:0;width:100%;height:100%;align-self:stretch;justify-self:stretch;z-index:0}
.sec.pc.pc-f-backdrop .pc-scrim{position:absolute;inset:0;z-index:1;pointer-events:none}
.sec.pc.pc-f-backdrop .pc-wrap{position:relative;z-index:2;display:grid;padding-top:clamp(48px,7vw,112px);padding-bottom:clamp(48px,7vw,112px);align-items:var(--pc-ay,end);justify-items:var(--pc-ax,start)}
.sec.pc.pc-f-backdrop .pc-words{max-width:min(100%,36rem);text-align:var(--pc-ta,left)}
.sec.pc.pc-f-backdrop .pc-words,.sec.pc.pc-f-backdrop .pc-words .h2,.sec.pc.pc-f-backdrop .pc-words .lab,.sec.pc.pc-f-backdrop .pc-words .cap,.sec.pc.pc-f-backdrop .pc-words .lede,.sec.pc.pc-f-backdrop .pc-words p,.sec.pc.pc-f-backdrop .pc-words li,.sec.pc.pc-f-backdrop .pc-words li *{color:var(--on-photo,#F4EFE3)}
.sec.pc.pc-f-backdrop .pc-words li{border-color:color-mix(in srgb,var(--on-photo,#F4EFE3) 34%,transparent)}
.sec.pc.pc-f-backdrop .pc-words .btn{background:var(--on-photo,#F4EFE3);color:#15130f;border-color:var(--on-photo,#F4EFE3)}
.sec.pc.pc-f-backdrop .pc-words .btn.ghost{background:transparent;color:var(--on-photo,#F4EFE3)}
.sec.pc.pc-f-backdrop .pc-words a:not(.btn){color:inherit}
.sec.pc.pc-f-backdrop .pc-words .cap,.sec.pc.pc-f-backdrop .pc-words .lede{max-width:34ch}
.sec.pc.pc-f-backdrop .pc-at-center .pc-words>*{margin-left:auto;margin-right:auto}.sec.pc.pc-f-backdrop .pc-at-center .pc-words ul{justify-content:center}

.sec.pc.pc-f-bleed .pc-field,.sec.pc.pc-f-stage .pc-field{grid-template-columns:minmax(0,var(--pc-pic)) minmax(0,1fr)}
.sec.pc.pc-f-bleed.pc-side-right .pc-field,.sec.pc.pc-f-stage.pc-side-right .pc-field{grid-template-columns:minmax(0,1fr) minmax(0,var(--pc-pic))}
.sec.pc.pc-f-bleed .pc-fig,.sec.pc.pc-f-stage .pc-panel{grid-row:1;grid-column:1}.sec.pc.pc-f-bleed .pc-col,.sec.pc.pc-f-stage .pc-col{grid-row:1;grid-column:2}
.sec.pc.pc-f-bleed.pc-side-right .pc-fig,.sec.pc.pc-f-stage.pc-side-right .pc-panel{grid-column:2}.sec.pc.pc-f-bleed.pc-side-right .pc-col,.sec.pc.pc-f-stage.pc-side-right .pc-col{grid-column:1}
.sec.pc.pc-f-bleed .pc-fig{height:100%}.sec.pc.pc-f-bleed .pc-fig img{position:absolute;inset:0}
.sec.pc.pc-f-bleed .pc-fade{z-index:3;background:linear-gradient(90deg,transparent 40%,var(--pc-bg) 100%)}.sec.pc.pc-f-bleed.pc-side-right .pc-fade{background:linear-gradient(270deg,transparent 40%,var(--pc-bg) 100%)}
.sec.pc.pc-f-bleed .pc-col{position:relative;z-index:4}
.sec.pc.pc-f-bleed.pc-over-1 .pc-col{margin-left:calc(-100vw / 12)}.sec.pc.pc-f-bleed.pc-over-2 .pc-col{margin-left:calc(-200vw / 12)}
.sec.pc.pc-f-bleed.pc-side-right.pc-over-1 .pc-col{margin-left:0;margin-right:calc(-100vw / 12)}.sec.pc.pc-f-bleed.pc-side-right.pc-over-2 .pc-col{margin-left:0;margin-right:calc(-200vw / 12)}
.sec.pc.pc-own .pc-field{background:var(--pc-ground)}.sec.pc.pc-own .pc-panel{background:none}.sec.pc.pc-own .pc-fig{box-shadow:none;border-radius:0}
.sec.pc .pc-inv,.sec.pc .pc-inv .h2,.sec.pc .pc-inv .lab,.sec.pc .pc-inv .cap,.sec.pc .pc-inv .lede,.sec.pc .pc-inv p,.sec.pc .pc-inv li,.sec.pc .pc-inv li *{color:var(--on-photo,#F4EFE3)}
.sec.pc .pc-inv li{border-color:color-mix(in srgb,var(--on-photo,#F4EFE3) 34%,transparent)}.sec.pc .pc-inv .btn{background:var(--on-photo,#F4EFE3);color:#15130f;border-color:var(--on-photo,#F4EFE3)}.sec.pc .pc-inv .btn.ghost{background:transparent;color:var(--on-photo,#F4EFE3)}
.sec.pc .pc-dk,.sec.pc .pc-dk .h2,.sec.pc .pc-dk .lab,.sec.pc .pc-dk .cap,.sec.pc .pc-dk .lede,.sec.pc .pc-dk p,.sec.pc .pc-dk li,.sec.pc .pc-dk li *{color:#15130f}
.sec.pc .pc-dk li{border-color:rgba(21,19,15,.3)}.sec.pc .pc-dk .btn{background:#15130f;color:#F4EFE3;border-color:#15130f}.sec.pc .pc-dk .btn.ghost{background:transparent;color:#15130f}
.sec.pc .pc-inv a:not(.btn),.sec.pc .pc-dk a:not(.btn){color:inherit}
.sec.pc.pc-f-gallery .pc-gal{display:grid;grid-template-columns:repeat(var(--n),minmax(0,1fr));column-gap:var(--gutter,32px);row-gap:clamp(32px,4vw,56px);align-items:start}
.sec.pc.pc-f-gallery .pc-gi{min-width:0;margin:0}.sec.pc.pc-f-gallery .pc-gi .pc-fig{aspect-ratio:var(--ratio);margin-bottom:clamp(16px,1.8vw,26px)}
.sec.pc.pc-f-gallery .pc-gi:nth-child(even){margin-top:clamp(28px,4.5vw,72px)}
.sec.pc.pc-f-inline .pc-words .h2{max-width:15em;line-height:1.16!important}
.sec.pc .pc-pill{display:inline-block;vertical-align:-.24em;height:1.1em;width:2.6em;border-radius:999px;margin:0 .08em}.sec.pc .pc-pill-soft{width:1.7em;border-radius:.16em}.sec.pc .pc-pill-circle{width:1.1em;border-radius:50%}
.sec.pc.pc-f-stage.pc-side-top .pc-field{display:block;min-height:0}.sec.pc.pc-f-stage.pc-side-top .pc-panel{padding:clamp(40px,6vw,96px) var(--pc-edge)}
.sec.pc.pc-f-stage.pc-side-top .pc-wrap{padding-top:clamp(32px,4.5vw,72px);padding-bottom:var(--pc-pad)}.sec.pc.pc-f-stage.pc-side-top.pc-tailed .pc-wrap{padding-bottom:0}
.sec.pc .pc-split{display:grid;grid-template-columns:minmax(0,5fr) minmax(0,6fr);column-gap:clamp(32px,8vw,128px);align-items:start}.sec.pc .pc-split .pc-wr>:first-child{margin-top:0}

.sec.pc.pc-f-panorama{padding:var(--pc-pad) 0;display:block}
.sec.pc.pc-f-panorama.pc-words-above:not(.pc-tailed){padding-bottom:0}.sec.pc.pc-f-panorama.pc-words-below{padding-top:0}
.sec.pc.pc-f-panorama .pc-fig{aspect-ratio:var(--ratio);width:100%}
.sec.pc.pc-f-panorama.pc-words-above .pc-fig{margin-top:clamp(32px,4.5vw,72px)}.sec.pc.pc-f-panorama.pc-words-below .pc-fig{margin-bottom:clamp(32px,4.5vw,72px)}
.sec.pc.pc-f-panorama .pc-split{align-items:end}
.sec.pc.pc-f-panorama .pc-tail{padding-top:clamp(20px,3vw,40px)}

.sec.pc.pc-f-card .pc-wrap,.sec.pc.pc-f-offset .pc-wrap{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));column-gap:var(--gutter,32px);align-items:center}
.sec.pc.pc-f-card .pc-fig{grid-row:1;grid-column:var(--c0)/var(--c1);aspect-ratio:var(--ratio);z-index:1}
.sec.pc.pc-f-card .pc-words{grid-row:1;grid-column:var(--w0)/var(--w1);z-index:2;background:var(--pc-bg);padding:clamp(24px,3vw,48px)}
.sec.pc.pc-f-card.pc-anchor-bottom .pc-words{align-self:end;padding-bottom:0}.sec.pc.pc-f-card.pc-anchor-top .pc-words{align-self:start;padding-top:0}
.sec.pc.pc-f-card.pc-anchor-middle .pc-words{align-self:center}
.sec.pc.pc-f-card.pc-side-right:not(.pc-anchor-middle) .pc-words{padding-left:0}.sec.pc.pc-f-card.pc-side-left:not(.pc-anchor-middle) .pc-words{padding-right:0}
.sec.pc.pc-f-card.pc-bleeds.pc-side-right .pc-fig{margin-right:calc(-1 * var(--pc-edge))}.sec.pc.pc-f-card.pc-bleeds.pc-side-left .pc-fig{margin-left:calc(-1 * var(--pc-edge))}

.sec.pc.pc-f-offset .pc-fig{grid-row:1;grid-column:var(--c0)/var(--c1);aspect-ratio:var(--ratio);width:min(100%,var(--pc-max));align-self:center}
.sec.pc.pc-f-offset.pc-side-right .pc-fig{justify-self:end}.sec.pc.pc-f-offset.pc-side-left .pc-fig{justify-self:start}
.sec.pc.pc-f-offset .pc-words{grid-row:1;grid-column:var(--w0)/var(--w1)}
.sec.pc.pc-f-offset .pc-drop-up{align-self:start;margin-top:calc(-1 * clamp(20px,4vw,64px))}.sec.pc.pc-f-offset .pc-drop-down{align-self:end;margin-bottom:calc(-1 * clamp(20px,4vw,64px))}
.sec.pc .pc-fig.pc-contain img{object-fit:contain}
.sec.pc .pc-shape-soft{border-radius:clamp(18px,2.4vw,36px)}.sec.pc .pc-shape-arch{border-radius:999px 999px 0 0}.sec.pc .pc-shape-circle{border-radius:50%}.sec.pc .pc-shape-pill{border-radius:999px}
.sec.pc .pc-shadow-soft{box-shadow:0 0 0 1px color-mix(in srgb,currentColor 14%,transparent)}.sec.pc .pc-shadow-hard{box-shadow:clamp(8px,1vw,16px) clamp(8px,1vw,16px) 0 var(--accent)}
.sec.pc .pc-frame-paper{background:#fff;padding:clamp(8px,1vw,16px);box-shadow:0 0 0 1px color-mix(in srgb,currentColor 14%,transparent)}
.sec.pc .pc-frame-browser{border-radius:8px;box-shadow:0 0 0 1px color-mix(in srgb,currentColor 14%,transparent)}

.sec.pc.pc-f-stage .pc-panel{display:grid;place-items:center;min-width:0;padding:clamp(32px,5vw,88px);background:var(--pc-ground)}
.sec.pc.pc-ground-accent{--pc-ground:var(--accent)}.sec.pc.pc-ground-ink{--pc-ground:var(--ink)}.sec.pc.pc-ground-ink.band-dark{--pc-ground:var(--band-ink)}
.sec.pc.pc-ground-alt{--pc-ground:color-mix(in srgb,var(--ink) 9%,var(--paper))}.sec.pc.pc-ground-alt.band-dark{--pc-ground:color-mix(in srgb,var(--band-ink) 12%,var(--band-paper))}
.sec.pc.pc-f-stage .pc-fig{justify-self:center;width:min(100%,var(--pc-max),calc(72svh * var(--pc-ar)));aspect-ratio:var(--ratio);border-radius:min(8px,max(4px,var(--radius,0px)))}
.sec.pc.pc-f-stage .pc-fig.pc-screen{border-radius:8px;box-shadow:0 0 0 1px color-mix(in srgb,currentColor 14%,transparent)}
.sec.pc.pc-f-stage .pc-fig.pc-crop{width:min(100%,var(--pc-max));aspect-ratio:var(--crop);border-radius:8px 8px 0 0;box-shadow:0 0 0 1px color-mix(in srgb,currentColor 14%,transparent)}
.sec.pc.pc-f-stage .pc-fig.pc-crop img{object-fit:cover;object-position:top}
.sec.pc.pc-f-stage .pc-cropfade{z-index:3;background:linear-gradient(180deg,transparent 58%,var(--pc-ground) 100%)}
.sec.pc.pc-f-stage.pc-cropped .pc-panel{padding-bottom:0;align-items:end}
@media(max-width:900px){
.sec.pc .pc-field{display:block;min-height:0}
.sec.pc .pc-col,.sec.pc.pc-side-right .pc-col{padding:32px min(var(--frame,24px),24px) 56px}.sec.pc .pc-col .pc-words{max-width:none}
.sec.pc.pc-f-backdrop .pc-field{display:grid;min-height:min(var(--pc-h),620px)}.sec.pc.pc-f-backdrop .pc-wrap{align-items:end;justify-items:start}.sec.pc.pc-f-backdrop .pc-words{text-align:left}
.sec.pc.pc-f-backdrop .pc-at-center .pc-words>*{margin-left:0}
.sec.pc.pc-f-bleed .pc-fig{height:auto;aspect-ratio:4/3}.sec.pc.pc-f-bleed .pc-fade{background:linear-gradient(180deg,transparent 55%,var(--pc-bg) 100%)!important}.sec.pc.pc-f-bleed .pc-col{margin:0!important}
.sec.pc.pc-f-panorama .pc-fig{aspect-ratio:3/2}.sec.pc .pc-split{grid-template-columns:minmax(0,1fr);row-gap:18px}
.sec.pc.pc-f-card .pc-wrap,.sec.pc.pc-f-offset .pc-wrap{display:flex;flex-direction:column;align-items:stretch;gap:28px}
.sec.pc.pc-f-gallery .pc-gal{grid-template-columns:minmax(0,1fr)}.sec.pc.pc-f-gallery .pc-gi:nth-child(even){margin-top:0}
.sec.pc.pc-f-card .pc-fig{margin-left:0!important;margin-right:0!important}
.sec.pc.pc-f-card .pc-words{margin:0!important;padding:0!important;background:none}
.sec.pc.pc-f-offset .pc-fig{rotate:none!important;margin-top:0;margin-bottom:0;align-self:flex-start}
.sec.pc.pc-f-stage .pc-panel{padding:28px min(var(--frame,24px),24px)}
}
"""


def _ratio(value):
    num, den = (int(v) for v in value.split('/')); return num / den


def _ground(src):
    """The colour a picture's own edges share, when they share one — a product on white, a render on black, a screen on
    its own dark: {'rgb': [r, g, b], 'dark': bool}. None when its edges are a scene, or the file cannot be opened here."""
    try:
        from PIL import Image, ImageStat
        with Image.open(io.BytesIO(base64.b64decode(src.split(',', 1)[1]))) as im:
            im = im.convert('RGB'); im.thumbnail((200, 200)); w, h = im.size; b = max(2, round(min(w, h) * 0.04))
            sides = [ImageStat.Stat(im.crop(box)) for box in ((0, 0, w, b), (0, h - b, w, h), (0, 0, b, h), (w - b, 0, w, h))]
    except Exception: return None
    mean = [sum(s.mean[i] for s in sides) / 4 for i in range(3)]
    if max(max(s.stddev) for s in sides) > 16 or max(abs(s.mean[i] - mean[i]) for s in sides for i in range(3)) > 14: return None
    return {'rgb': [round(v) for v in mean], 'dark': (0.2126 * mean[0] + 0.7152 * mean[1] + 0.0722 * mean[2]) / 255 < 0.45}


def _sides(src):
    """How light a picture is along its left and its right edge, 0–1: {'left', 'right'} — what a dissolving edge has to
    meet. None when the file cannot be opened here."""
    try:
        from PIL import Image, ImageStat
        with Image.open(io.BytesIO(base64.b64decode(src.split(',', 1)[1]))) as im:
            im = im.convert('L'); im.thumbnail((200, 200)); w, h = im.size; b = max(4, round(w * 0.12))
            return {'left': round(ImageStat.Stat(im.crop((0, 0, b, h))).mean[0] / 255, 3), 'right': round(ImageStat.Stat(im.crop((w - b, 0, w, h))).mean[0] / 255, 3)}
    except Exception: return None


def offered(page_html, images, sid):
    """The job's pictures that this page does not show yet and that a section of words may take: {address: picture}.
    A picture commissioned or captured for this very section (its id says so) is marked `meant`. A commissioned picture
    is offered only to the section it was made for; a detail cut from another picture is never offered beside it."""
    out = {}; token = lambda name: re.split(r'[^a-z0-9]+', str(name).lower())
    for i in images or []:
        if not isinstance(i, dict) or not i.get('data') or not i.get('id') or i['data'] in page_html or i.get('crop_of'): continue
        w, h = i.get('w'), i.get('h')
        if not (isinstance(w, (int, float)) and isinstance(h, (int, float)) and w >= 600 and h >= 300): continue
        name, sec = token(i['id']), token(sid); meant = any(name[k:k + len(sec)] == sec for k in range(len(name) - len(sec) + 1))
        if (i.get('gen') or i.get('shot')) and not meant: continue   # atmosphere made for another section, or a screen of something else: not this section's
        out['img:' + str(i['id'])] = {'src': i['data'], 'alt': ' '.join(str(i.get('alt') or '').split())[:200], 'w': w, 'h': h, 'shot': bool(i.get('shot')), 'gen': bool(i.get('gen')), 'meant': meant, 'ground': _ground(i['data']), 'sides': _sides(i['data'])}
    return out


def _with_picture(content, entry):
    """The section's content with the picture this entry gives it, when it has none of its own."""
    return content if content.get('picture') else dict(content, picture=content['offers'][entry['picture']])


def readable(page_html, images=None):
    """{section id: (section record, content or the reason it cannot be read)} for the sections of the page that hold a
    picture and are not lists. The picture's pixel size is read off the picture itself; whether it is a screenshot or a
    generated picture comes from images.json when it is given, else from how the template marked it."""
    by_data = {i.get('data'): i for i in (images or []) if isinstance(i, dict) and i.get('data')}
    found = {}
    for sec in SECTIONS.sections(page_html)[1:]:
        if sec['kind'] or not sec['id']: continue
        html = page_html[sec['span'][0]:sec['span'][1]]
        if '<img' not in html:   # a section of words: it may take one of the job's pictures that the page does not show yet
            given = offered(page_html, images, sec['id']) if images else {}
            if not given: continue
            try: said = SECTIONS.from_words(html)
            except ValueError: continue
            found[sec['id']] = (sec, {'kind': 'picture', 'band': said['band'], 'classes': said['classes'], 'picture': None, 'offers': given, 'first': 'words', 'tail': said['tail'],
                                      'words': {'html': said['head'] + said['body'], 'classes': said['holder'], 'chars': said['chars'], 'rows': said['rows'], 'heading': said['heading'],
                                                'parts': None if said['holder'] else [said['head'], said['body']]}})
            continue
        try: content = SECTIONS.from_picture(html)
        except ValueError as err: found[sec['id']] = (sec, str(err)); continue
        pic = content['picture']; known = by_data.get(pic['src'])
        sized = known and all(isinstance(known.get(k), (int, float)) and not isinstance(known.get(k), bool) and known[k] > 0 for k in ('w', 'h'))
        w, h = (known['w'], known['h']) if sized else CONTENT._size(pic['src'])   # images.json describes this very file; without it the file is opened
        marked = bool({'ui-photo', 'ui-photo-story'} & set(sec['classes'])) or bool(re.search(r'<figure class="[^"]*\b(ui-shot|assigned-visual|lead-shot)\b', html))
        pic.update(w=w, h=h, shot=bool(known.get('shot')) if known else marked, gen=bool(known and known.get('gen')), ground=_ground(pic['src']), sides=_sides(pic['src']))
        found[sec['id']] = (sec, content)
    return found


def geometry(entry, content, page):
    """What a form would do with this section's picture at a 1440×900 screen: {'box': (width, height) in CSS px the
    picture fills, 'fit': cover|contain, 'scale': how far past its pixels that shows it, 'words': the width its words get}.
    The stage draws a picture within its pixels by construction, so its scale is never above the limit."""
    form = entry['form']; pic = content['picture']; W, Hh = VIEW; w, h = pic['w'], pic['h']
    inner = min(W, page.get('container', 1300)) - 2 * page.get('frame', 40); edge = max(page.get('frame', 40), (W - page.get('container', 1300)) / 2 + page.get('frame', 40))
    cols = entry.get('cols', DEFAULT_COLS.get(form)); side = entry.get('side', 'right'); limit = 1.0 if pic['shot'] else V.UPSCALE
    span = lambda n, bleed='none': V.span_px((1, n + 1, 1, 2), page, bleed, GUTTER)
    if form == 'backdrop': box, fit, words = (W, HEIGHTS[entry.get('height', 'lg')] / 100 * Hh), 'cover', min(576, inner)
    elif form == 'bleed':
        width = W * cols / 12; box, fit = (width, HEIGHTS[entry.get('height', 'lg')] / 100 * Hh), 'cover'; words = min(544, W - width - edge - 86 + entry.get('overlap', 0) * W / 12)
    elif form == 'panorama': box, fit, words = (W, W / _ratio(entry.get('ratio', '21/9'))), 'cover', (inner - 115) * 5 / 11
    elif form == 'card':
        width = span(cols, side if entry.get('bleed') else 'none'); box, fit = (width, width / _ratio(entry.get('ratio', '3/2'))), 'cover'; words = span(_card_cols(cols)) - 86
    elif form == 'offset':
        own = entry.get('ratio', 'own') == 'own'; r = (w / h) if own else _ratio(entry['ratio'])
        width = min(span(cols), limit * (w if own else min(w, h * r))); box, fit = (width, width / r), ('contain' if own or pic['shot'] else 'cover'); words = span(_words_cols(cols))
        if entry.get('frame') == 'paper': box = (box[0] - 28, box[1] - 28)
    elif form == 'inline':   # set into the heading like a word: as tall as the heading's capitals
        size = TITLE_PX[entry.get('title', 'xl')]; box, fit, words = (size * PILLS[entry.get('shape', 'pill')], size * PILL_EM), 'cover', inner
    else:   # stage: the panel takes cols/12 of the screen; the picture sits inside it at no more than its pixels allow
        top = side == 'top'; panel = (W - 2 * edge) if top else W * cols / 12 - 2 * 72
        if entry.get('crop') == 'fade': width = min(panel, limit * w); box, fit = (width, width / CROP_RATIO), 'cover'
        else: width = min(panel, limit * w, 0.72 * Hh * w / h); box, fit = (width, width * h / w), 'contain'
        words = (inner - 115) * 5 / 11 if top else min(544, W - W * cols / 12 - edge - 86)
    scale = (min if fit == 'contain' else max)(box[0] / w, box[1] / h)
    return {'box': (round(box[0]), round(box[1])), 'fit': fit, 'scale': scale, 'limit': limit, 'words': words}


def _card_cols(cols): return min(6, 12 - cols + 2)     # the card lies over the picture's inner two columns
def _words_cols(cols): return max(4, min(7, 12 - cols - 1))   # one empty column between the picture and its words when there is room


def _heading_fits(entry, content, page, room):
    """None, or why the section's heading cannot be set at the size asked for in the room its form leaves it."""
    title = entry.get('title', 'xl' if entry['form'] == 'inline' else 'md')
    if not content['words']['heading']: return None
    face = FACES.known(page.get('display')); advance = FACES.advance(face, bool(page.get('upper')))
    longest = max(content['words']['heading'].split(), key=len); need = len(longest) * advance * TITLE_PX[title] * 1.08
    if need <= room: return None
    return f'its heading\'s longest word ("{longest}") is about {round(need)} px wide at title "{title}" and the words have {round(room)} px: use a smaller title or give the words more room'


def open_forms(content, page):
    """Which forms this section's picture may take with their default settings, and for each what it would draw:
    [{'form', 'box', 'scale'} …]. What the composer is shown, so that it chooses among what is possible."""
    out = []
    for form in FORMS:
        if content['picture'].get('gen') and form not in COVERING: continue
        # a bleed dissolves into its section when the picture's inner edge is as light as the ground: on one side, the other, or not at all
        variants = [({}, ''), ({'side': 'left'}, 'dissolves only with the picture on the left'), ({'edge': 'hard'}, 'hard edge only')] if form == 'bleed' else [({}, '')]
        for change, note in variants:
            entry = {'section': 'x', 'form': form, **change}
            if _refusals(entry, content, page): continue
            g = geometry(entry, content, page); out.append({'form': form, 'box': g['box'], 'scale': round(g['scale'], 2), **({'note': note} if note else {})}); break
    return out


def _refusals(entry, content, page):
    """Why this form does not suit this section's picture and words: [(code, message)]. Assumes the entry's fields are well formed."""
    out = []; form = entry['form']; pic = content['picture']; words = content['words']
    if not (isinstance(pic.get('w'), (int, float)) and isinstance(pic.get('h'), (int, float)) and pic['w'] > 0 and pic['h'] > 0):
        return [('IP063', 'the pixel size of this picture is unknown, so it cannot be checked against the space it would fill')]
    if pic['shot'] and form in COVERING + ('inline',):
        out.append(('IP062', f'this picture is a screenshot — evidence of the product, shown whole in its own colours. It is never cropped or written over: use "stage" or "offset", not "{form}"'))
    if pic['shot'] and form == 'offset' and (entry.get('ratio', 'own') != 'own' or entry.get('tone', 'none') != 'none' or entry.get('shape', 'rect') not in ('rect', 'soft') or entry.get('grain')):
        out.append(('IP062', 'a screenshot keeps its own proportion, colours and rectangle: ratio "own", no tone, no grain, shape rect or soft'))
    if form == 'backdrop' and (words['chars'] > WORDS_ON_PICTURE or words['rows'] > ROWS_ON_PICTURE):
        out.append(('IP021', f'this section says {words["chars"]} characters in {words["rows"]} list rows: more than a reader takes in over a photograph ({WORDS_ON_PICTURE} characters, {ROWS_ON_PICTURE} rows). Give the words a ground of their own: "card", "bleed" or "panorama"'))
    if form == 'inline' and not words['heading']: out.append(('IP021', 'a picture set into the heading needs a heading: this section has none'))
    if form == 'inline' and words['chars'] < INLINE_WORDS: out.append(('IP021', f'this section says {words["chars"]} characters: with its picture set into the heading it would be a thin band with a thumbnail in it. A picture in the heading is for a section with words to carry it ({INLINE_WORDS} characters or more); here show the picture as large as it can be — stage or offset'))
    if form == 'bleed' and entry.get('edge', 'fade') == 'fade':   # a dissolve needs the picture and the ground to be of one lightness where they meet
        ground = (page.get('grounds') or {}).get(content.get('band')); inner = (pic.get('sides') or {}).get('left' if entry.get('side', 'right') == 'right' else 'right')
        if ground is not None and inner is not None and abs(ground - inner) > DISSOLVE:
            out.append(('IP067', f'the picture is {"light" if inner > ground else "dark"} where it would dissolve into a {"dark" if inner > ground else "light"} section: the dissolve would turn to mud. Cut it clean ("edge": "hard"), put it on the other side, or choose another form'))
    if form == 'stage' and entry.get('ground') == 'own' and not pic.get('ground'):
        out.append(('IP067', 'the edges of this picture are a scene, not one colour: it has no ground of its own to give the section — "ground" accent, ink or alt, or a form that crops it'))
    if out: return out
    g = geometry(entry, content, page)
    if g['scale'] > g['limit'] + 1e-6:
        out.append(('IP060', f'this picture is {int(pic["w"])}×{int(pic["h"])} px and "{form}" would fill {g["box"][0]}×{g["box"][1]} px with it at a 1440 screen ({g["scale"]:.2f}× its pixels, limit {g["limit"]}×)'
                    + {'backdrop': ': a lower height, or a form that asks less of it', 'bleed': ': fewer columns, a lower height, or a form that asks less of it', 'panorama': ': a flatter ratio, or a form that asks less of it',
                       'card': ': fewer columns or another ratio', 'offset': ': fewer columns'}.get(form, '')))
    if g['box'][0] < MIN_PICTURE_PX and form != 'inline': out.append(('IP066', f'the picture would be drawn {g["box"][0]} px wide: under {MIN_PICTURE_PX} px it no longer reads as a picture'))
    why = _heading_fits(entry, content, page, g['words'])
    if why: out.append(('IP044', why))
    return out


def validate(doc, page_html, images=None):
    errors = []
    def err(code, at, message): errors.append({'code': code, 'at': at, 'message': message})
    shaped = isinstance(doc, dict) and doc.get('ir') in V.ACCEPTED and isinstance(doc.get('pictures', []), list) and isinstance(doc.get('galleries', []), list) and not set(doc) - {'ir', 'pictures', 'galleries', 'note'}
    if not shaped or not (doc.get('pictures') or doc.get('galleries')) or len(doc.get('pictures', [])) > 12 or len(doc.get('galleries', [])) > 4:
        err('IP001', 'ir', f'a picture composition is {{"ir": "{V.VERSION}", "pictures": [up to 12 objects], "galleries": [up to 4 objects]}} with at least one entry'); return errors
    page = readable(page_html, images); tokens = CONTENT.page_of(page_html); named = []; given = []
    whole = lambda v, lo, hi: isinstance(v, int) and not isinstance(v, bool) and lo <= v <= hi
    order = [s['id'] for s in SECTIONS.sections(page_html)]
    for i, run in enumerate(doc.get('galleries', [])):   # neighbouring photographs side by side in one row, each over its own heading and words
        where = f'galleries[{i}]'
        if not isinstance(run, dict) or set(run) - GALLERY_KEYS: err('IP001', where, f'a gallery is {{"sections": [ids], optional {sorted(GALLERY_KEYS - {"sections"})}}}'); continue
        ids = run.get('sections')
        if not (isinstance(ids, list) and 2 <= len(ids) <= 4 and all(isinstance(x, str) for x in ids) and len(set(ids)) == len(ids)): err('IP010', where, 'a gallery names two to four different sections, in the order of the page'); continue
        if run.get('ratio', '4/3') not in GALLERY_RATIOS: err('IP020', where, f'the ratio of a gallery\'s pictures is one of {GALLERY_RATIOS}')
        if run.get('title', 'md') not in TITLES[:2]: err('IP020', where, f'title in a gallery is one of {TITLES[:2]}')
        if run.get('tone', 'none') not in V.TONES: err('IP020', where, f'tone is one of {V.TONES}')
        if run.get('enter', 'none') not in V.MEDIA_ENTER: err('IP020', where, f'enter is one of {V.MEDIA_ENTER}')
        unknown = [x for x in ids if x not in page or isinstance(page[x][1], str) or not page[x][1].get('picture')]
        if unknown: err('IP010', where, f'{unknown} cannot be in a gallery: each of its sections is a picture section with its own picture; they are {sorted(k for k, v in page.items() if not isinstance(v[1], str) and v[1].get("picture"))}'); continue
        if any(x in named for x in ids): err('IP010', where, 'a section is in one gallery, once')
        named += ids
        if [order.index(x) for x in ids] != list(range(order.index(ids[0]), order.index(ids[0]) + len(ids))): err('IP010', where, f'the sections of a gallery follow each other on the page, in its order; the page runs {[x for x in order if x in page]}'); continue
        ratio = _ratio(run.get('ratio', '4/3')) if run.get('ratio', '4/3') in GALLERY_RATIOS else 4 / 3
        inner = min(VIEW[0], tokens.get('container', 1300)) - 2 * tokens.get('frame', 40); width = (inner - (len(ids) - 1) * GUTTER) / len(ids)
        for x in ids:
            c = page[x][1]; pic = c['picture']
            if pic['shot']: err('IP062', where, f'"{x}" shows a screenshot: a gallery crops its pictures to one proportion, and a screenshot is never cropped')
            elif not (isinstance(pic.get('w'), (int, float)) and isinstance(pic.get('h'), (int, float)) and pic['w'] > 0 and pic['h'] > 0): err('IP063', where, f'the pixel size of the picture of "{x}" is unknown')
            elif max(width / pic['w'], width / ratio / pic['h']) > V.UPSCALE + 1e-6:
                err('IP060', where, f'the picture of "{x}" is {int(pic["w"])}×{int(pic["h"])} px and a gallery of {len(ids)} would fill {round(width)}×{round(width / ratio)} px with it ({max(width / pic["w"], width / ratio / pic["h"]):.2f}× its pixels, limit {V.UPSCALE}×): another ratio, or more sections in the row')
            if c['words']['chars'] > GALLERY_WORDS or c['words']['rows'] > 3: err('IP021', where, f'"{x}" says {c["words"]["chars"]} characters in {c["words"]["rows"]} rows: a gallery column holds a heading and a few lines (up to {GALLERY_WORDS} characters, 3 rows)')
    for i, entry in enumerate(doc.get('pictures', [])):
        where = f'pictures[{i}]'
        if not isinstance(entry, dict): err('IP001', where, 'each picture is an object'); continue
        sid = entry.get('section'); where = f'pictures[{sid}]' if isinstance(sid, str) else where
        form = entry.get('form')
        if form not in FORMS: err('IP020', where, f'form is one of {FORMS}'); continue
        extra = set(entry) - KEYS[form]
        if extra:   # as everywhere in a composition: a field that could carry words does not exist
            carried = extra & {'text', 'content', 'html', 'label', 'href', 'value', 'heading', 'caption', 'alt', 'src', 'words_text'}
            err('IP011' if carried else 'IP001', where, f'unknown fields {sorted(extra)} for "{form}"' + (': a composition places what the page says and shows, it does not contain it' if carried else f'; it takes {sorted(KEYS[form] - {"section", "form"})}'))
        if not isinstance(sid, str) or sid not in page: err('IP010', where, f'no picture section "{sid}" on this page; the picture sections are {sorted(page)}'); continue
        if sid in named: err('IP010', where, f'section "{sid}" is named twice')
        named.append(sid)
        _, content = page[sid]
        if isinstance(content, str): err('IP010', where, f'section "{sid}" cannot be recomposed: {content}'); continue
        if content.get('picture'):
            if 'picture' in entry: err('IP001', where, 'this section shows its own picture: "picture" is for a section of words that takes one'); continue
        else:   # a section of words: it takes one of the pictures offered to it, and a picture is shown once
            address = entry.get('picture')
            if address not in content['offers']: err('IP010', where, f'section "{sid}" is words only: it needs "picture", one of {sorted(content["offers"])}'); continue
            if address in given: err('IP061', where, f'"{address}" is given to two sections; a picture appears once')
            given.append(address)
            if content['offers'][address]['gen'] and form not in COVERING: err('IP065', where, 'a picture commissioned for atmosphere is a ground, an edge or a strip — backdrop, bleed, panorama, card — never set down as an object or a print'); continue
            content = _with_picture(content, entry)
        before = len(errors)
        if entry.get('title', 'xl' if form == 'inline' else 'md') not in (TITLES[1:] if form == 'inline' else TITLES): err('IP020', where, f'title is one of {TITLES[1:] if form == "inline" else TITLES}')
        if entry.get('enter', 'none') not in V.MEDIA_ENTER: err('IP020', where, f'enter is one of {V.MEDIA_ENTER}')
        if entry.get('tone', 'none') not in V.TONES: err('IP020', where, f'tone is one of {V.TONES}')
        if entry.get('scroll', 'none') not in V.MEDIA_SCROLL: err('IP020', where, f'scroll is one of {V.MEDIA_SCROLL}')
        if not isinstance(entry.get('grain', False), bool): err('IP020', where, 'grain is true or false')
        focal = entry.get('focal', [0.5, 0.5])
        if not (isinstance(focal, list) and len(focal) == 2 and all(isinstance(v, (int, float)) and not isinstance(v, bool) and 0 <= v <= 1 for v in focal)): err('IP020', where, 'focal is [x, y], each 0..1: the part of the picture that stays in view when it is cropped')
        sides = SIDES + (('top',) if form == 'stage' else ())   # a stage may also stand across the top of its section, the words under it
        if 'side' in KEYS[form] and entry.get('side', 'right') not in sides: err('IP020', where, f'side is one of {sides}: where the picture stands')
        if form in COLS and not whole(entry.get('cols', DEFAULT_COLS[form]), *COLS[form]): err('IP020', where, f'cols for "{form}" is {COLS[form][0]}–{COLS[form][1]}: how many of the twelve columns the picture takes')
        if 'height' in KEYS[form]:   # the least the section stands: a stage may also take just the height of what it shows
            allowed = {'backdrop': ('md', 'lg', 'screen'), 'bleed': ('md', 'lg'), 'stage': ('auto', 'md', 'lg')}[form]
            if entry.get('height', allowed[0] if form == 'stage' else 'lg') not in allowed: err('IP020', where, f'height for "{form}" is one of {allowed}')
        if 'align' in KEYS[form] and entry.get('align', 'center') not in ALIGN: err('IP020', where, f'align is one of {ALIGN}: where the words stand against the picture, top to bottom')
        if form == 'bleed':
            over = entry.get('overlap', 0)
            if entry.get('edge', 'fade') not in EDGES: err('IP020', where, f'edge is one of {EDGES}: the picture\'s inner edge dissolves into the section, or is cut hard')
            if not whole(over, 0, 2): err('IP020', where, 'overlap is 0, 1 or 2: how many columns the words reach into the dissolved edge of the picture')
            elif over and entry.get('edge', 'fade') != 'fade': err('IP067', where, 'words reach onto the picture only where its edge dissolves: "edge": "fade"')
        elif form == 'inline':
            if entry.get('at', 'end') not in ('start', 'end'): err('IP020', where, 'at is start or end: where in the heading the picture is set')
            if entry.get('shape', 'pill') not in PILLS: err('IP020', where, f'shape is one of {tuple(PILLS)}')
        if form == 'backdrop':
            if entry.get('place', 'bottom-left') not in PLACES: err('IP020', where, f'place is one of {PLACES}: where the words stand on the picture')
            if entry.get('scrim', 'mid') not in SCRIMS: err('IP020', where, f'scrim is one of {SCRIMS}')
        elif form == 'panorama':
            if entry.get('ratio', '21/9') not in PANORAMAS: err('IP020', where, f'the ratio of a panorama is one of {PANORAMAS}')
            if entry.get('words', 'above') not in WORDS: err('IP020', where, f'words is one of {WORDS}')
        elif form == 'card':
            if entry.get('ratio', '3/2') not in CARD_RATIOS: err('IP020', where, f'the ratio of the picture under a card is one of {CARD_RATIOS}')
            if entry.get('anchor', 'bottom') not in ANCHORS: err('IP020', where, f'anchor is one of {ANCHORS}: where the card lies on the picture')
            if not isinstance(entry.get('bleed', False), bool): err('IP020', where, 'bleed is true or false')
        elif form == 'offset':
            shape, tilt, frame = entry.get('shape', 'rect'), entry.get('tilt', 0), entry.get('frame', 'none')
            if entry.get('ratio', 'own') not in OFFSET_RATIOS: err('IP020', where, f'ratio is one of {OFFSET_RATIOS} ("own": the picture\'s own proportion)')
            if shape not in V.SHAPES: err('IP020', where, f'shape is one of {V.SHAPES}')
            if entry.get('shadow', 'none') not in V.SHADOWS: err('IP020', where, f'shadow is one of {V.SHADOWS}')
            if frame not in FRAMES: err('IP020', where, f'frame is one of {FRAMES}')
            if entry.get('drop', 'none') not in DROPS: err('IP020', where, f'drop is one of {DROPS}: the picture hung above or below the line of the words')
            if not whole(tilt, -4, 4): err('IP020', where, 'tilt is a whole number of degrees, -4 to 4')
            if len(errors) == before:   # treatments that do not go together
                if shape == 'circle' and entry.get('ratio', 'own') != '1/1': err('IP067', where, 'a circle is a picture at ratio 1/1')
                if frame != 'none' and shape not in ('rect', 'soft'): err('IP067', where, 'a framed picture keeps a rectangular shape')
                if frame == 'browser' and not content['picture']['shot']: err('IP067', where, 'a browser frame is for a screenshot; a photograph takes "paper" or none')
                if entry.get('ratio', 'own') == 'own' and shape in ('arch', 'pill') and content['picture']['w'] > content['picture']['h']: err('IP067', where, f'an {shape} wants an upright picture: give it an upright ratio (3/4, 2/3, 4/5)')
        elif form == 'stage':
            if entry.get('ground', 'accent') not in GROUNDS: err('IP020', where, f'ground is one of {GROUNDS}: the colour of the stage')
            if not whole(entry.get('tilt', 0), -3, 3): err('IP020', where, 'tilt on a stage is a whole number of degrees, -3 to 3')
            if entry.get('crop', 'whole') not in CROPS: err('IP020', where, f'crop is one of {CROPS}: a screen shown whole, or its top at full size with the rest fading into the stage')
            elif entry.get('crop') == 'fade' and len(errors) == before:
                shown = content['picture']
                if not shown['shot']: err('IP067', where, 'a fading crop is how a product screen is shown — its top at full size, the rest running on; a photograph takes a form that crops it to its subject')
                elif entry.get('tilt'): err('IP067', where, 'a screen that fades into the stage stands straight: no tilt')
                elif shown.get('w') and shown.get('h') and shown['w'] / shown['h'] >= CROP_RATIO: err('IP067', where, f'this screen is already wider than the crop ({shown["w"]}×{shown["h"]}): show it whole')
        if len(errors) > before: continue
        for code, message in _refusals(entry, content, tokens): err(code, where, message)
    return errors


def _scrim(place, strength):
    """The veil between a backdrop and its words: thickest where the words stand, thin where the picture should show."""
    a = {'soft': .46, 'mid': .64, 'deep': .82}[strength]; c = lambda k: f'rgba(16,14,12,{a * k:.2f})'
    down = f'linear-gradient(180deg,{c(.16)} 0%,{c(.3)} 42%,{c(1)} 100%)'; up = f'linear-gradient(0deg,{c(.16)} 0%,{c(.3)} 42%,{c(1)} 100%)'
    left = f'linear-gradient(90deg,{c(.9)} 0%,{c(.5)} 44%,{c(0)} 84%)'; right = f'linear-gradient(270deg,{c(.9)} 0%,{c(.5)} 44%,{c(0)} 84%)'
    flat = lambda k: f'linear-gradient({c(k)},{c(k)})'
    return {'bottom-left': f'{left},{down}', 'bottom-right': f'{right},{down}', 'top-left': f'{left},{up}', 'center': flat(.84), 'left': f'{left},{flat(.34)}', 'right': f'{right},{flat(.34)}'}[place]


PLACE = {'bottom-left': ('end', 'start', 'left'), 'bottom-right': ('end', 'end', 'left'), 'top-left': ('start', 'start', 'left'),
         'center': ('center', 'center', 'center'), 'left': ('center', 'start', 'left'), 'right': ('center', 'end', 'left')}
MOVES = {'rise': 'fade-rise', 'clip': 'clip-reveal', 'settle': 'scale-settle'}


def render_section(sec, content, entry, page):
    """The <section> for one validated picture entry: the section's own id, band and classes, its words block verbatim,
    its picture once, and everything it held after them."""
    form = entry['form']; pic = content['picture']; words = content['words']; side = entry.get('side', 'right')
    tone = entry.get('tone', 'none') if form != 'stage' else 'none'; focal = entry.get('focal', [0.5, 0.5])
    toned = (['pc-tone'] + (['pc-tone-tint'] if tone == 'tint' else [])) if tone != 'none' else []
    layers = ('<i class="pc-t-light"></i><i class="pc-t-dark"></i>' if tone == 'duotone' else '') + ('<i class="pc-grain"></i>' if entry.get('grain') and form != 'stage' else '')
    named = ([MOVES[entry['enter']]] if entry.get('enter', 'none') != 'none' else []) + (['parallax'] if entry.get('scroll') == 'parallax' and form in COVERING else [])
    move = (f' data-move="{" ".join(named)}"' + (' data-parallax="6"' if 'parallax' in named else '')) if named else ''
    img = f'<img src="{e(pic["src"])}" alt="{e(pic["alt"])}">'
    focus = f'--focal:{round(focal[0] * 100)}% {round(focal[1] * 100)}%'
    wclass = ' '.join(['pc-words'] + [c for c in words['classes'] if not c.startswith('pc-')])
    block = lambda extra='', style='': f'<div class="{wclass}{extra}"{style}>{words["html"]}</div>'
    def figure(classes=(), style=''):
        names = ' '.join(['pc-fig'] + toned + list(classes)); styled = focus + (';' + style if style else '')
        return f'<figure class="{names}" data-limit="{1 if pic["shot"] else V.UPSCALE:g}"{move} style="{styled}">{img}{layers}</figure>'
    def split():
        """The words block with its heading to the left and what the heading introduces to the right, when it has both."""
        cut = words['html'].find('</h2>') + 5; parts = words.get('parts')
        if parts: left, right = parts[0], ''.join(parts[1:])   # several blocks of words: the first is the heading's
        else: left, right = words['html'][:cut], words['html'][cut:]
        if cut >= 5 and re.sub(r'<[^>]+>', '', right).strip() and len(re.findall(r'<div\b', left)) == left.count('</div>'):
            return f'<div class="{wclass} pc-split"><div class="pc-wh">{left}</div><div class="pc-wr">{right}</div></div>'
        return block()
    kept = [c for c in content['classes'] if c != 'pc' and not c.startswith('pc-')]
    classes = kept + ['pc', 'pc-f-' + form, 'pc-t-' + entry.get('title', 'xl' if form == 'inline' else 'md')]; attrs = ''
    dark, light = ('var(--paper)', 'var(--ink)') if page.get('dark') else ('var(--ink)', 'var(--paper)')
    tail = content['tail']; has_tail = bool(tail.strip())
    cols = entry.get('cols', DEFAULT_COLS.get(form))
    if form == 'backdrop':
        place = entry.get('place', 'bottom-left'); ay, ax, ta = PLACE[place]; classes += ['pc-flush']
        veil = _scrim(place, entry.get('scrim', 'mid')); tall = HEIGHTS[entry.get('height', 'lg')]
        body = (f'<div class="pc-field" style="--pc-h:{tall}svh">{figure()}<i class="pc-scrim" style="background:{veil}"></i>'
                f'<div class="wrap pc-wrap pc-at-{place}" style="--pc-ay:{ay};--pc-ax:{ax};--pc-ta:{ta}">{block()}</div></div>')
    elif form in ('bleed', 'stage'):
        classes += ['pc-flush', f'pc-side-{side}']; align = entry.get('align', 'center')
        own = ''; said = block()
        if form == 'bleed':
            shown = figure()
            if entry.get('edge', 'fade') == 'fade':   # the inner edge dissolves into the section's own ground; the words may reach into it
                shown = shown.replace('</figure>', '<i class="pc-fade"></i></figure>'); classes.append('pc-edge-fade')
                if entry.get('overlap'): classes.append('pc-over-%d' % entry['overlap']); attrs = ' data-over="%d"' % entry['overlap']
        else:
            classes.append('pc-ground-' + entry.get('ground', 'accent')); limit = 1.0 if pic['shot'] else V.UPSCALE
            if entry.get('ground') == 'own':   # the section takes the picture's own ground: no panel, no edge, the words in the colour that reads on it
                classes.append('pc-own'); own = ';--pc-ground:rgb(%d,%d,%d)' % tuple(pic['ground']['rgb']); said = block(' pc-inv' if pic['ground']['dark'] else ' pc-dk')
            style = f'--pc-max:{int(pic["w"] * limit)}px;--pc-ar:{pic["w"] / pic["h"]:.4f};--ratio:{int(pic["w"])}/{int(pic["h"])}' + (f';rotate:{entry["tilt"]}deg' if entry.get('tilt') else '')
            if entry.get('crop') == 'fade':   # a product screen at full size: its top, the rest fading into the ground it stands on
                classes.append('pc-cropped'); shown = '<div class="pc-panel">' + figure(['pc-screen', 'pc-crop'], style + f';--crop:{CROP_RATIO:g}').replace('</figure>', '<i class="pc-cropfade"></i></figure>') + '</div>'
            else: shown = f'<div class="pc-panel">{figure(["pc-contain"] + (["pc-screen"] if pic["shot"] else []), style)}</div>'
        height = entry.get('height', 'lg' if form == 'bleed' else 'auto'); tall = 'auto' if height == 'auto' else '%dsvh' % HEIGHTS[height]
        if form == 'stage' and side == 'top':   # the picture across the top on its ground, the words under it in two columns
            classes += ['pc-tailed'] * has_tail; body = f'<div class="pc-field" style="--pc-h:auto{own}">{shown}</div><div class="wrap pc-wrap">{split()}</div>'
        else: body = f'<div class="pc-field" style="--pc-pic:{cols / 12 * 100:.4f}%;--pc-h:{tall}{own}">{shown}<div class="pc-col pc-al-{align}">{said}</div></div>'
    elif form == 'panorama':
        where = entry.get('words', 'above'); classes += [f'pc-words-{where}'] + (['pc-tailed'] if has_tail else [])
        said = split()
        strip = figure([], '--ratio:' + entry.get('ratio', '21/9')); wrapped = f'<div class="wrap pc-wrap">{said}</div>'
        body = wrapped + strip if where == 'above' else strip + wrapped
    elif form == 'card':
        classes += ['pc-side-' + side, 'pc-anchor-' + entry.get('anchor', 'bottom')] + (['pc-bleeds'] if entry.get('bleed') else [])
        card = _card_cols(cols); c0, c1, w0, w1 = (13 - cols, 13, 1, 1 + card) if side == 'right' else (1, 1 + cols, 13 - card, 13)
        placed = ' style="--w0:%d;--w1:%d"' % (w0, w1); style = '--ratio:%s;--c0:%d;--c1:%d' % (entry.get('ratio', '3/2'), c0, c1)
        body = f'<div class="wrap pc-wrap">{figure([], style)}{block("", placed)}</div>'
    elif form == 'inline':   # the picture is set into the heading like a word; nothing else of the words block changes
        shape = entry.get('shape', 'pill'); names = ' '.join(['pc-fig', 'pc-pill', 'pc-pill-' + shape] + toned)
        pill = f'<span class="{names}" data-limit="{V.UPSCALE:g}"{move} style="{focus}">{img}{layers}</span>'; html = words['html']
        if entry.get('at', 'end') == 'end': at = html.find('</h2>'); html = html[:at] + ' ' + pill + html[at:]
        else: at = re.search(r'<h2\b[^>]*>', html).end(); html = html[:at] + pill + ' ' + html[at:]
        body = f'<div class="wrap pc-wrap"><div class="{wclass}">{html}</div></div>'
    else:   # offset
        classes.append(f'pc-side-{side}'); wide = _words_cols(cols); limit = 1.0 if pic['shot'] else V.UPSCALE
        c0, c1, w0, w1 = (13 - cols, 13, 1, 1 + wide) if side == 'right' else (1, 1 + cols, 13 - wide, 13)
        own = entry.get('ratio', 'own') == 'own'; ratio = f'{int(pic["w"])}/{int(pic["h"])}' if own else entry['ratio']
        look = (['pc-contain'] if own or pic['shot'] else []) + ['pc-%s-%s' % (k, entry[k]) for k, plain in (('shape', 'rect'), ('shadow', 'none'), ('frame', 'none'), ('drop', 'none')) if entry.get(k, plain) != plain]
        widest = int(limit * (pic['w'] if own else min(pic['w'], pic['h'] * _ratio(ratio))))   # on any screen: never wider than its pixels allow at this crop
        style = f'--ratio:{ratio};--c0:{c0};--c1:{c1};--pc-max:{widest}px' + (f';rotate:{entry["tilt"]}deg' if entry.get('tilt') else '')
        placed = ' style="--w0:%d;--w1:%d"' % (w0, w1); aligned = ' pc-al-' + entry.get('align', 'center')
        body = f'<div class="wrap pc-wrap">{figure(look, style)}{block(aligned, placed)}</div>'
    if has_tail: body += f'<div class="pc-tail">{tail}</div>' if form in ('backdrop', 'bleed', 'stage', 'panorama') else tail
    return f'<section class="{e(" ".join(classes))}" id="{e(sec["id"])}" data-pc="{V.VERSION}" data-form="{form}"{attrs} style="--pc-dark:{dark};--pc-light:{light}">{body}</section>'


def render_gallery(members, run, page):
    """One <section> for a run of neighbouring picture sections: their pictures side by side in one row, each over its own
    words block, verbatim. The row keeps the first section's id, band and classes; every other member keeps its id on its
    own column, so a link to it still lands on it; what each section held after its words follows the row."""
    first = members[0][1]; ratio = run.get('ratio', '4/3'); tone = run.get('tone', 'none')
    toned = (['pc-tone'] + (['pc-tone-tint'] if tone == 'tint' else [])) if tone != 'none' else []
    layers = '<i class="pc-t-light"></i><i class="pc-t-dark"></i>' if tone == 'duotone' else ''
    move = f' data-move="{MOVES[run["enter"]]}"' if run.get('enter', 'none') != 'none' else ''
    columns = []
    for n, (sec, content) in enumerate(members):
        pic = content['picture']; words = content['words']; names = ' '.join(['pc-fig'] + toned)
        wclass = ' '.join(['pc-words'] + [c for c in words['classes'] if not c.startswith('pc-')])
        anchor = f' id="{e(sec["id"])}"' if n else ''
        columns.append(f'<article class="pc-gi"{anchor}><figure class="{names}" data-limit="{V.UPSCALE:g}"{move}><img src="{e(pic["src"])}" alt="{e(pic["alt"])}">{layers}</figure><div class="{wclass}">{words["html"]}</div></article>')
    kept = [c for c in first['classes'] if c != 'pc' and not c.startswith('pc-')]; classes = kept + ['pc', 'pc-f-gallery', 'pc-t-' + run.get('title', 'md')]
    dark, light = ('var(--paper)', 'var(--ink)') if page.get('dark') else ('var(--ink)', 'var(--paper)')
    tails = ''.join(content['tail'] for _, content in members)
    return (f'<section class="{e(" ".join(classes))}" id="{e(members[0][0]["id"])}" data-pc="{V.VERSION}" data-form="gallery" style="--pc-dark:{dark};--pc-light:{light}">'
            f'<div class="wrap pc-gal" style="--n:{len(members)};--ratio:{ratio}">{"".join(columns)}</div>{tails}</section>')


def transplant(page_html, doc, images=None):
    """Draw every picture section of the document in place of the template's. Validated first against the page itself;
    a document that fails leaves the page untouched and says why."""
    errors = validate(doc, page_html, images)
    if errors: return page_html, {'drawn': False, 'errors': errors, 'sections': []}
    page = readable(page_html, images); tokens = CONTENT.page_of(page_html); out = page_html; done = []; redrawn = []
    for entry in doc.get('pictures', []):
        sec, content = page[entry['section']]; redrawn.append((sec['span'][0], sec['span'][1], render_section(sec, _with_picture(content, entry), entry, tokens), [entry['section']]))
    for run in doc.get('galleries', []):
        members = [page[x] for x in run['sections']]; redrawn.append((members[0][0]['span'][0], members[-1][0]['span'][1], render_gallery(members, run, tokens), run['sections']))
    for start, end, html, ids in sorted(redrawn, key=lambda x: -x[0]):   # from the bottom up: earlier spans stay true
        out = out[:start] + html + out[end:]; done += ids
    if 'id="pc-css"' not in out:
        head = out.find('</head>')
        if head < 0: return page_html, {'drawn': False, 'errors': [{'code': 'IP000', 'at': 'page', 'message': 'the page has no </head> to carry the picture stylesheet'}], 'sections': []}
        out = out[:head] + f'<style id="pc-css">{CSS}</style>' + out[head:]
    return out, {'drawn': True, 'errors': [], 'sections': sorted(done)}


if __name__ == '__main__':
    if len(sys.argv) not in (4, 5): raise SystemExit(__doc__)
    with open(sys.argv[1]) as f: document = json.load(f)
    with open(sys.argv[2], encoding='utf-8') as f: page_html = f.read()
    page_images = None
    if len(sys.argv) == 5:
        with open(sys.argv[4]) as f: page_images = json.load(f)
    result, report = transplant(page_html, document, page_images)
    with open(sys.argv[3], 'w', encoding='utf-8') as f: f.write(result)
    for problem in report['errors']: print(f"{problem['code']} {problem['at']}: {problem['message']}")
    print(json.dumps({'drawn': report['drawn'], 'sections': report['sections']}))
    raise SystemExit(0 if report['drawn'] else 1)
