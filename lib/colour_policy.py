"""Experimental palette resolver; no writes or network; known opaque tokens only."""
import re

def norm(v):
 if not isinstance(v,str):return None
 v=v.strip()
 if re.fullmatch(r'#[0-9a-fA-F]{3}',v):return '#'+''.join(x*2 for x in v[1:]).upper()
 if re.fullmatch(r'#[0-9a-fA-F]{6}',v):return v.upper()
 return None

def rgb(c):return tuple(int(c[i:i+2],16) for i in (1,3,5))
def linear(c):
 c=c/255
 return c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4
def luminance(c):
 r,g,b=map(linear,rgb(c));return .2126*r+.7152*g+.0722*b
def contrast(a,b):
 a,b=luminance(a),luminance(b);return (max(a,b)+.05)/(min(a,b)+.05)
def bw(bg):return max(('#000000','#FFFFFF'),key=lambda c:contrast(c,bg))
def text_for(bg,preferred):return preferred if preferred and contrast(preferred,bg)>=4.5 else bw(bg)
def muted_for(bg,fg):
 # Keep the existing muted feel when it passes for normal text; otherwise
 # use the full text colour. Do not invent a hue for neutral colours.
 mixed='#'+''.join(f'{round(a*.62+b*.38):02X}' for a,b in zip(rgb(fg),rgb(bg)))
 return mixed if contrast(mixed,bg)>=4.5 else fg

def resolve(bp):
 """Only for explicit opt-out: preserve valid measured blueprint tokens.

 Keep the measured surface and repair illegible foregrounds. Contrast checks
 cover known opaque text/component roles, not photography or arbitrary CSS.
 """
 paper=norm(bp.get('paper'));ink=norm(bp.get('ink'));accent=norm(bp.get('accent'));fallback=[]
 if not paper:
  paper='#111111' if bp.get('mode')=='dark' else '#FFFFFF';fallback.append('paper')
 if not ink:fallback.append('ink_missing')
 safe_ink=text_for(paper,ink)
 if safe_ink!=ink:fallback.append('ink_contrast')
 ink=safe_ink
 if not accent:accent=ink
 alt=norm(bp.get('alt')) or paper
 on_alt=text_for(alt,ink);on_accent=text_for(accent,ink)
 def button_for(surface, surface_ink):
  return (accent,on_accent) if contrast(accent,surface)>=3 else (surface_ink,surface)
 button,button_ink=button_for(paper,ink)
 alt_button,alt_button_ink=button_for(alt,on_alt)
 if on_alt!=ink:fallback.append('alt_ink_contrast')
 if on_accent!=ink:fallback.append('accent_ink_contrast')
 return {'paper':paper,'ink':ink,'accent':accent,'alt':alt,'alt_ink':on_alt,'accent_ink':on_accent,
  'button':button,'button_ink':button_ink,'alt_button':alt_button,'alt_button_ink':alt_button_ink,
  'accent_button':on_accent,'accent_button_ink':accent,'muted':muted_for(paper,ink),
  'alt_muted':muted_for(alt,on_alt),'accent_muted':muted_for(accent,on_accent),
  'dark_muted':muted_for(ink,paper),'fallback':fallback}
