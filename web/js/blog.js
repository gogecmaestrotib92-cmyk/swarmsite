/* blog.js — the two things a guide's page does: the phone menu, and the address field that leads to /app (as on the landing). */
(function(){
var bg=document.querySelector('.burger'),mn=document.getElementById('menu');
var menu=function(o){mn.hidden=!o;bg.setAttribute('aria-expanded',o?'true':'false')};
if(bg&&mn){bg.addEventListener('click',function(){menu(mn.hidden)});
  addEventListener('keydown',function(e){if(e.key==='Escape'&&!mn.hidden){menu(false);bg.focus()}});
  mn.addEventListener('click',function(e){if(e.target.closest('a'))menu(false)});
  matchMedia('(min-width:992px)').addEventListener('change',function(m){if(m.matches)menu(false)})}
window.go=function(e){e.preventDefault();var v=e.target.querySelector('input').value.trim();if(!v)return;
  location.href='/app?url='+encodeURIComponent(v.replace(/^https?:\/\//,''))};
})();
