"""feel.py — how every page answers a hand, the same in all templates: the behaviours a well-made app has, added under
a template's own (owner, 2026-11-23: "apple ponašanja za sve sajtove, pogotovo dashboard").

    add(page) -> page      one <style data-sw-feel> and one <script data-sw-feel> first in <head>; a page that has them is
                           returned as it is

What it adds, each only where the template has not said it already (measured 2026-11-23 over the 48 templates: 20 set a
press of their own, 18 set where an anchor lands, none answers "more contrast" or "less transparency", 15 blur what
lies behind a bar or a menu):

  a press       a surface (a button, a card: something with a fill, a border or a shadow) gives under the finger — drawn
                smaller by at most 6 px of its longer side, so a big card barely moves and a button visibly does — and
                springs back on release; a bare word that is a link dims while held. With reduced motion asked for, both
                only dim. Not on a page whose CSS sets an :active of its own: the template's press is its own.
  a tap         no grey flash of the phone's own over the element that already answered, and no wait for a double tap
                on what is pressed (touch-action: manipulation).
  an anchor     a link to a place on the page lands below a bar that stays at the top, not under it — unless the template
                sets its own scroll padding.
  less see-through   with "reduce transparency" or "increase contrast" asked for in the system, a bar or menu that blurs
                what lies behind it is made solid in its own colour (or the page's ground, where it had only the blur).
  more contrast links in running text are underlined.

Nothing here changes a page at rest: the gate's screenshots are the same with and without it. No timer runs, nothing is
fetched, and every part is skipped by a browser that lacks what it needs.
"""
import re

CSS = ('html{-webkit-tap-highlight-color:transparent}'
       ':where(a[href],button,[role=button],summary,label[for],input,select,textarea){touch-action:manipulation}'
       '@media (prefers-contrast:more){:where(p,li,dd,td,blockquote,figcaption) a[href]{text-decoration:underline!important;text-underline-offset:.15em}}')

JS = r'''(function(){var d=document,w=window,H=d.documentElement,mq=function(q){return !!(w.matchMedia&&w.matchMedia(q).matches)};
var PRESS=%(press)s,ANCHOR=%(anchor)s,T='a[href],button,[role=button],summary,label[for],input[type=submit],input[type=button]';
function rgb(c){var m=String(c||'').match(/^color\(srgb ([\d.e-]+) ([\d.e-]+) ([\d.e-]+)(?: \/ ([\d.e-]+))?\)$/);if(m)return[m[1]*255,m[2]*255,m[3]*255,m[4]===undefined?1:+m[4]];
m=String(c||'').match(/[\d.]+/g);return m&&m.length>=3?[+m[0],+m[1],+m[2],m.length>3?+m[3]:1]:null}
function surface(s){var b=rgb(s.backgroundColor);return(b&&b[3]>.05)||s.backgroundImage!=='none'||s.boxShadow!=='none'||(parseFloat(s.borderTopWidth)>0&&s.borderTopStyle!=='none')}
if(PRESS&&H.animate&&('scale' in H.style)){var held=null;
 d.addEventListener('pointerdown',function(e){if(e.button>0||!e.isPrimary)return;var t=e.target&&e.target.closest&&e.target.closest(T);if(!t||t.disabled||t.getAttribute('aria-disabled')==='true')return;
  var s=getComputedStyle(t),r=t.getBoundingClientRect();if(!r.width||!r.height||s.display==='inline'&&!surface(s)&&t.tagName!=='A')return;
  var still=mq('(prefers-reduced-motion: reduce)'),big=Math.max(r.width,r.height),k=1-Math.min(.03,6/big),a;
  if(surface(s)&&!still)a=t.animate([{scale:'1'},{scale:String(k)}],{duration:90,easing:'ease-out',fill:'forwards'});
  else a=t.animate([{opacity:getComputedStyle(t).opacity},{opacity:'.55'}],{duration:still?0:70,fill:'forwards'});
  held={t:t,a:a,still:still}},{passive:true});
 var up=function(){if(!held)return;var h=held;held=null;h.a.playbackRate=h.still?1e3:.45;h.a.reverse();h.a.finished.then(function(){h.a.cancel()},function(){})};
 ['pointerup','pointercancel','dragstart'].forEach(function(n){w.addEventListener(n,up,true)});w.addEventListener('blur',up)}
if(ANCHOR&&getComputedStyle(H).scrollPaddingTop==='auto')d.addEventListener('click',function(e){var a=e.target&&e.target.closest&&e.target.closest('a[href^="#"]');if(!a||a.getAttribute('href').length<2)return;
  var bottom=0;(d.elementsFromPoint?d.elementsFromPoint(w.innerWidth/2,1):[]).forEach(function(el){for(;el&&el!==H;el=el.parentElement){var p=getComputedStyle(el).position;if(p==='fixed'||p==='sticky'){var r=el.getBoundingClientRect();if(r.top<=1&&r.height<w.innerHeight/3)bottom=Math.max(bottom,r.bottom)}}});
  H.style.scrollPaddingTop=bottom?Math.round(bottom+12)+'px':''},true);
function solid(){if(!(mq('(prefers-reduced-transparency: reduce)')||mq('(prefers-contrast: more)')))return;var g=rgb(getComputedStyle(d.body).backgroundColor);if(!g||g[3]<.5)g=rgb(getComputedStyle(H).backgroundColor);if(!g||g[3]<.5)g=[255,255,255,1];
 d.querySelectorAll('body *').forEach(function(el){if(el.hasAttribute('data-sw-solid'))return;var s=getComputedStyle(el),f=s.backdropFilter||s.webkitBackdropFilter;if(!f||f==='none')return;
  var b=rgb(s.backgroundColor),c=b&&b[3]>.05?b:g;el.setAttribute('data-sw-solid','');el.style.setProperty('-webkit-backdrop-filter','none','important');el.style.setProperty('backdrop-filter','none','important');
  el.style.setProperty('background-color','rgb('+Math.round(c[0])+','+Math.round(c[1])+','+Math.round(c[2])+')','important')})}
var go=function(){solid();w.addEventListener('load',solid);['(prefers-reduced-transparency: reduce)','(prefers-contrast: more)'].forEach(function(q){var m=w.matchMedia&&w.matchMedia(q);m&&m.addEventListener&&m.addEventListener('change',solid)})};
d.readyState==='loading'?d.addEventListener('DOMContentLoaded',go):go()})();'''


def _css_of(page):
    return ' '.join(re.findall(r'<style\b[^>]*>(.*?)</style\s*>', page, re.S | re.I))


def add(page):
    if 'data-sw-feel' in page:
        return page
    i = page.find('<head')
    j = page.find('>', i) if i >= 0 else -1
    if j < 0:
        return page
    css = _css_of(page)
    press = ':active' not in css                                  # the template's own press stands
    anchor = not re.search(r'scroll-padding|scroll-margin', css)   # so does its own landing of an anchor
    js = JS % {'press': 'true' if press else 'false', 'anchor': 'true' if anchor else 'false'}
    return page[:j + 1] + '<style data-sw-feel>%s</style><script data-sw-feel>%s</script>' % (CSS, js) + page[j + 1:]
