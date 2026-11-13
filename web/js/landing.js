/* landing.js — the landing's movement: the library template's own script (render.py JS, as measured: words on the two
   paths at 80px/s, the pinned stage, the feature titles, the menu, the phone bar), then ours: the three ways in and the
   address field. Reduced motion: no pin, the words stand still. Scripts off: the stacked build, every step and answer shown. */
(function(){
var R=document.documentElement,still=matchMedia('(prefers-reduced-motion:reduce)').matches;R.classList.add('js');
var cl=function(v,a,b){return v<a?a:v>b?b:v},lerp=function(a,b,t){return a+(b-a)*t};
/* words running along the two paths: 80px a second, the ribbon continues where the looped line ends */
var rib=document.querySelector('.rib');
if(rib&&!still){var tp=rib.querySelectorAll('textPath'),p1=rib.querySelector('.p1'),t1=rib.querySelector('.t1');
  var go=function(){var reps=+rib.dataset.reps||2,U=t1.getComputedTextLength()/reps,L1=p1.getTotalLength(),t0=performance.now(),seen=true;
    if(!U||!isFinite(U))return;
    if('IntersectionObserver' in window)new IntersectionObserver(function(en){seen=en[0].isIntersecting},{rootMargin:'100px'}).observe(rib);
    (function tick(now){if(seen){var ph=((now-t0)/1000*80)%U;tp[0].setAttribute('startOffset',(ph-U).toFixed(1));tp[1].setAttribute('startOffset',((((ph+L1)%U)+U)%U-U).toFixed(1))}requestAnimationFrame(tick)})(t0)};
  (document.fonts&&document.fonts.ready?document.fonts.ready:Promise.resolve()).then(go)}
/* the pinned stage */
var st=document.querySelector('.stage');
if(st&&!still&&st.querySelector('.vis')){
  var mq=matchMedia('(min-width:992px) and (min-height:620px)'),pin=st.querySelector('.pin'),track=st.querySelector('.track'),green=st.querySelector('.green'),
      kc=st.querySelector('.kc'),slot=st.querySelector('.vslot'),vis=st.querySelector('.vis'),vlab=vis.querySelector('.vlab'),
      tbs=[].slice.call(st.querySelectorAll('.tb')),arts=[].slice.call(st.querySelectorAll('.st')),lays=[].slice.call(vis.querySelectorAll('.lay[data-i]')),
      n=arts.length,on=false,vh,P,travel,ch,a0=200,a1,a2=400,a3=600,a4,per=930,cur=-1,tgt=0,raf=0,act=-2;
  /* the card's height above its resting place while the heading passes (measured on the reference, by share of the way) */
  var KEY=[[0,151],[.157,185],[.27,204],[.38,217],[.49,222],[.61,218],[.72,206],[.83,187],[.945,85],[1,0]];
  var key=function(t){for(var i=1;i<KEY.length;i++)if(t<=KEY[i][0]){var a=KEY[i-1],b=KEY[i];return lerp(a[1],b[1],(t-a[0])/(b[0]-a[0]))}return 0};
  var setup=function(){on=mq.matches;st.classList.toggle('pinned',on);
    if(!on){st.style.removeProperty('--P');track.style.transform='';if(kc){kc.style.width='';kc.style.marginRight='';kc.style.opacity=''}return}
    vh=innerHeight;ch=Math.min(468,vh-160);travel=vh+432;a1=kc?600:0;a4=travel+70;P=a0+a1+a2+a3+a4+n*per;
    st.style.setProperty('--P',P+'px');st.style.setProperty('--travel',travel+'px');st.style.setProperty('--ch',ch+'px');
    st.style.setProperty('--gap',cl((innerWidth-992)*.23+24,24,128)+'px');cur=-1;frame()};
  var draw=function(y,top){
    var pA=a1?cl((y-a0)/a1,0,1):1,pS=cl((y-a0-a1-a2)/a3,0,1),s=cl((y-a0-a1-a2-a3)/a4,0,1)*travel;
    if(kc){var w=325*(1-pA);kc.style.width=Math.max(72,w)+'px';kc.style.marginRight=Math.min(0,w-72)+'px';kc.style.opacity=cl(w/72,0,1)}
    track.style.transform='translate3d(0,'+(-s)+'px,0)';
    green.style.setProperty('--rt',cl(top,0,80)+'px');green.style.setProperty('--rb',cl(s,0,80)+'px');
    var pr=pin.getBoundingClientRect(),sr=slot.getBoundingClientRect(),fy=(vh-ch)/2,fx=pr.width/2-200;
    var x=sr.left-pr.left,yy=sr.top-pr.top+s,w2=sr.width,h2=sr.height;      /* the slot, as if the track had not moved */
    var e2=pS*pS*(3-2*pS);
    var o0=Math.max(151,yy-fy),tt=s/travel;                               /* never above where the picture stood: a long heading keeps its text clear */
    var X=lerp(x,fx,e2),W=lerp(w2,400,e2),H=lerp(h2,ch,e2),Y=pS<1?lerp(yy,fy+o0,e2):fy+key(tt)+(o0-151)*(1-tt)*(1-tt);
    vis.style.transform='translate3d('+X+'px,'+Y+'px,0)';vis.style.width=W+'px';vis.style.height=H+'px';vis.style.borderRadius=lerp(40,16,e2)+'px';
    if(vlab)vlab.style.opacity=cl(1-pS*3,0,1);
    var t0=a0+a1+a2+a3+a4,i=y>=t0-150?cl(Math.floor((y-t0)/per),0,n-1):-1;
    if(i!==act){act=i;tbs.forEach(function(b,k){b.classList.toggle('on',k===i);b.setAttribute('aria-current',k===i?'true':'false')});
      arts.forEach(function(a,k){a.classList.toggle('on',k===i)});lays.forEach(function(l,k){l.classList.toggle('on',k===i||(i<0&&false))})}
  };
  var frame=function(){raf=0;if(!on)return;var r=st.getBoundingClientRect();tgt=cl(-r.top,0,P);
    if(cur<0)cur=tgt;cur+=(tgt-cur)*.22;if(Math.abs(tgt-cur)<.5)cur=tgt;draw(cur,r.top);if(cur!==tgt)raf=requestAnimationFrame(frame)};
  var kick=function(){if(!raf)raf=requestAnimationFrame(frame)};
  addEventListener('scroll',kick,{passive:true});addEventListener('resize',function(){setup()});
  if(mq.addEventListener)mq.addEventListener('change',setup);
  tbs.forEach(function(b,k){b.addEventListener('click',function(){if(!on)return;var top=st.getBoundingClientRect().top+scrollY;scrollTo({top:top+a0+a1+a2+a3+a4+k*per+20,behavior:'smooth'})})});
  setup();addEventListener('load',setup);
}
/* quotes: cards travel left to right on a rising curve through the middle of a pinned screen (measured: 1.18px per px of scroll,
   y = 450 - 329*tanh(1.5*(x-720)/1100) at 900 high, about 700 between cards) */
var qs=document.querySelector('.qs'),lgm=document.querySelector('.lgm');
if(lgm)lgm.style.setProperty('--t',(lgm.scrollWidth/2/46).toFixed(1)+'s');
if(qs&&!still&&matchMedia('(min-width:992px)').matches){var qc=[].slice.call(qs.querySelectorAll('.qc')),qr=0,qoff=[],acc=0;
  qs.classList.add('run');qc.forEach(function(el,i){qoff.push(acc+el.offsetWidth/2);acc+=el.offsetWidth+140});
  var Q=(acc-qc[0].offsetWidth/2)/1.18+400;qs.style.setProperty('--Q',Q+'px');
  var qd=function(){qr=0;var r=qs.getBoundingClientRect(),d=cl(-r.top,-innerHeight,Q+innerHeight),W=innerWidth,H=innerHeight;
    qc.forEach(function(el,i){var x=W/2+d*1.18-(qoff[i]-qoff[0]),y=H/2-H*.366*Math.tanh(1.5*(x-W/2)/(W*.76));el.style.transform='translate3d('+(x-el.offsetWidth/2)+'px,'+(y-el.offsetHeight/2)+'px,0)'})};
  addEventListener('scroll',function(){if(!qr)qr=requestAnimationFrame(qd)},{passive:true});addEventListener('resize',qd);qd()}
/* features: the title nearest the middle is the one in ink, and the card shows its picture */
var fis=[].slice.call(document.querySelectorAll('.feat .fi')),fls=[].slice.call(document.querySelectorAll('.fl2'));
if(fis.length){var fa=-1,fr=0,ff=function(){fr=0;var m=innerHeight*.42,b=0,bd=1e9;fis.forEach(function(el,i){var r=el.getBoundingClientRect(),d=Math.abs(r.top+r.height/2-m);if(d<bd){bd=d;b=i}});
    if(b!==fa){fa=b;fis.forEach(function(el,i){el.classList.toggle('on',i===b)});var s=fis[b].dataset.s;fls.forEach(function(l){l.classList.toggle('on',l.dataset.s===s)})}};
  addEventListener('scroll',function(){if(!fr)fr=requestAnimationFrame(ff)},{passive:true});addEventListener('resize',ff);ff()}
/* menu */
var bg=document.querySelector('.burger'),mn=document.getElementById('menu');
var menu=function(o){if(!bg||!mn)return;mn.hidden=!o;bg.setAttribute('aria-expanded',o?'true':'false')};
if(bg&&mn){bg.addEventListener('click',function(){menu(mn.hidden)});
  addEventListener('keydown',function(e){if(e.key==='Escape'&&!mn.hidden){menu(false);bg.focus()}});   /* ours: Escape closes it, a link in it closes it */
  mn.addEventListener('click',function(e){if(e.target.closest('a'))menu(false)})}
/* ours — the first action. Three ways in, the same weight: a site (the address, the designs start at once), a first version
   of an app (the address, then its screenshots on /app), no site (the short form on /start). Every link to #top ends in
   the address field. The field leads to /app?url=…, with what the visitor chose beside it. */
var tabs=[].slice.call(document.querySelectorAll('.ways [data-way]')),way='site',field=document.getElementById('url');
var setWay=function(w,focus){way=w;tabs.forEach(function(t){t.setAttribute('aria-selected',String(t.dataset.way===w));t.tabIndex=t.dataset.way===w?0:-1});
  document.querySelectorAll('[data-for]').forEach(function(el){el.hidden=el.dataset.for.split(' ').indexOf(w)<0});
  var hint=document.getElementById('wayHint');if(hint&&hint.dataset[w])hint.textContent=hint.dataset[w];
  if(focus){var t=w==='none'?document.querySelector('.alt [data-for] a, .alt a'):field;if(t)t.focus()}};
tabs.forEach(function(t,i){t.addEventListener('click',function(){setWay(t.dataset.way,false)});
  t.addEventListener('keydown',function(e){var k=e.key==='ArrowRight'||e.key==='ArrowDown'?1:e.key==='ArrowLeft'||e.key==='ArrowUp'?-1:0;if(!k)return;e.preventDefault();var n=tabs[(i+k+tabs.length)%tabs.length];setWay(n.dataset.way,false);n.focus()})});
if(tabs.length){var w0=(location.hash.match(/^#(site|app|none)$/)||[])[1];setWay(w0||'site',false)}
document.addEventListener('click',function(e){var a=e.target.closest('a[href="#top"],a[href="#app"],a[href="#site"],a[href="#none"]');if(!a||!field)return;e.preventDefault();var w=a.getAttribute('href').slice(1);
  if(w!=='top')setWay(w,false);scrollTo({top:0,behavior:still?'auto':'smooth'});setTimeout(function(){(way==='none'?document.querySelector('.alt a'):field).focus({preventScroll:true})},still?0:350)});
window.go=function(e){e.preventDefault();var v=e.target.querySelector('input').value.trim();if(!v)return;
  var q='/app?url='+encodeURIComponent(v.replace(/^https?:\/\//,'')),k=document.getElementById('kind'),g=document.getElementById('goal');
  if(way==='app')q+='&with=screens';if(k&&k.value)q+='&niche='+encodeURIComponent(k.value);if(g&&g.value.trim())q+='&goal='+encodeURIComponent(g.value.trim().slice(0,80));
  location.href=q};
/* phone bar */
var ab=document.querySelector('.appbar');
var nv=document.querySelector('.nv'),ly=scrollY,dn=false,gone=false,ph=matchMedia('(max-width:991px)');
/* phone, as measured: on the way down the nav box leaves and the bottom bar comes in; on the way up they swap back */
addEventListener('scroll',function(){var y=scrollY;if(Math.abs(y-ly)<6)return;dn=y>ly&&y>120;ly=y;var a=dn&&ph.matches&&(!mn||mn.hidden);if(nv)nv.classList.toggle('away',a);if(ab&&!gone)ab.classList.toggle('up',a)},{passive:true});
if(ab){ab.hidden=false;
  ab.querySelector('.abx').addEventListener('click',function(){gone=true;ab.classList.remove('up');setTimeout(function(){ab.hidden=true},450)})}
})();
