(()=>{
const q=s=>[...document.querySelectorAll(s)];
const cs=e=>getComputedStyle(e);
const fam=e=>cs(e).fontFamily.split(',')[0].replace(/["']/g,'').trim();
const libs={gsap:!!window.gsap,ScrollTrigger:!!(window.ScrollTrigger||(window.gsap&&gsap.plugins&&gsap.plugins.scrollTrigger)),lenis:!!(window.Lenis||document.documentElement.classList.contains('lenis')||q('.lenis').length),locomotive:!!(window.LocomotiveScroll||q('[data-scroll-container]').length),barba:!!window.barba,three:!!window.THREE||!!q('canvas').length,swiper:!!window.Swiper||!!q('.swiper').length,webflow:!!document.documentElement.getAttribute('data-wf-site'),next:!!window.__NEXT_DATA__||!!q('#__next').length,nuxt:!!window.__NUXT__||!!q('#__nuxt').length,framer:!!q('[data-framer-name]').length,splitText:!!q('[class*="char"],[class*="split"],[class*="word"]').length,aos:!!q('[data-aos]').length,customCursor:!!q('[class*="cursor"]').filter(e=>cs(e).position==='fixed').length};
const typo={};
const sample=(sel,label)=>{q(sel).slice(0,40).forEach(e=>{const r=e.getBoundingClientRect();if(!e.textContent.trim()||r.width===0)return;const c=cs(e);const k=label+' | '+fam(e)+' '+c.fontWeight+' '+Math.round(parseFloat(c.fontSize))+'px/'+(parseFloat(c.lineHeight)/parseFloat(c.fontSize)).toFixed(2)+' ls:'+c.letterSpacing+' '+(c.textTransform!=='none'?c.textTransform:'');typo[k]=(typo[k]||0)+1;});};
sample('h1','h1');sample('h2','h2');sample('h3','h3');sample('p','p');sample('a,button','link/btn');
q('span,div,small,label').filter(e=>e.children.length===0&&e.textContent.trim().length>1&&e.textContent.trim().length<40).slice(0,300).forEach(e=>{const c=cs(e);const fs=parseFloat(c.fontSize);if(fs<=13){const k='label | '+fam(e)+' '+c.fontWeight+' '+Math.round(fs)+'px ls:'+c.letterSpacing+' '+(c.textTransform!=='none'?c.textTransform:'');typo[k]=(typo[k]||0)+1;}});
const typoTop=Object.entries(typo).sort((a,b)=>b[1]-a[1]).slice(0,22).map(([k,v])=>k+' ×'+v);
const bg={},fg={};
q('*').slice(0,3000).forEach(e=>{const c=cs(e);const b=c.backgroundColor;if(b&&!/rgba\(\d+, \d+, \d+, 0\)/.test(b)){const r=e.getBoundingClientRect();if(r.width*r.height>5000)bg[b]=(bg[b]||0)+Math.round(r.width*r.height/10000);}if(e.children.length===0&&e.textContent.trim())fg[c.color]=(fg[c.color]||0)+1;});
const hex=s=>{const m=s.match(/\d+/g);if(!m)return s;return '#'+m.slice(0,3).map(n=>(+n).toString(16).padStart(2,'0')).join('')+(m[3]&&m[3]!=='1'?' a'+m[3]:'');};
const top=(o,n)=>Object.entries(o).sort((a,b)=>b[1]-a[1]).slice(0,n).map(([k,v])=>hex(k)+' ('+v+')');
const root=document.querySelector('main')||document.body;
let blocks=[...root.children];if(blocks.length<4){blocks=blocks.flatMap(b=>b.children.length>2?[...b.children]:[b]);}
const secs=blocks.filter(b=>b.getBoundingClientRect().height>150).slice(0,30).map(b=>{const c=cs(b);const h=b.querySelector('h1,h2,h3');return{tag:b.tagName.toLowerCase()+(b.id?'#'+b.id:'')+(b.className&&typeof b.className==='string'?'.'+b.className.trim().split(/\s+/).slice(0,2).join('.'):''),h:Math.round(b.getBoundingClientRect().height),pad:Math.round(parseFloat(c.paddingTop))+'/'+Math.round(parseFloat(c.paddingBottom)),words:b.innerText.trim().split(/\s+/).filter(Boolean).length,img:b.querySelectorAll('img,video,canvas,picture').length,head:h?h.innerText.trim().replace(/\s+/g,' ').slice(0,70):''}});
const widths={};q('div,section,main,header').forEach(e=>{const w=Math.round(e.getBoundingClientRect().width);if(w>700&&w<innerWidth-40)widths[w]=(widths[w]||0)+1;});
const container=Object.entries(widths).sort((a,b)=>b[1]-a[1]).slice(0,3).map(([w,n])=>w+'px×'+n);
const anim={transitions:q('*').filter(e=>cs(e).transitionDuration!=='0s').length,animations:q('*').filter(e=>cs(e).animationName!=='none').length,willChange:q('*').filter(e=>cs(e).willChange!=='auto').length,fixedEls:q('*').filter(e=>cs(e).position==='fixed').length,stickyEls:q('*').filter(e=>cs(e).position==='sticky').length,mixBlend:q('*').filter(e=>cs(e).mixBlendMode!=='normal').length};
const h1=document.querySelector('h1');
const out={url:location.href,title:document.title,viewport:innerWidth+'x'+innerHeight,pageHeight:document.documentElement.scrollHeight,libs:Object.entries(libs).filter(([k,v])=>v).map(([k])=>k),fonts:[...new Set(q('h1,h2,h3,p,a,span,li,button').slice(0,500).map(fam))],typography:typoTop,bgColors:top(bg,8),textColors:top(fg,6),container,sections:secs,media:{img:q('img').length,video:q('video').length,canvas:q('canvas').length,svg:q('svg').length},text:{totalWords:document.body.innerText.trim().split(/\s+/).length,h1:h1?h1.innerText.trim().replace(/\s+/g,' ').slice(0,120):'',headings:q('h1,h2,h3').length},anim,navLinks:q('nav a,header a').map(a=>a.innerText.trim()).filter(t=>t&&t.length<25).slice(0,12)};
document.body.innerHTML='<article><pre>'+JSON.stringify(out,null,1).replace(/</g,'&lt;')+'</pre></article>';
return 'ok';
})();
