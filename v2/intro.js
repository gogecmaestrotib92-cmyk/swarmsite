(function(){
  const intro=document.createElement('div'); intro.id='sw-intro';
  intro.innerHTML=`<div class="sw-intro-top"><span class="sw-pill">BEFORE</span><span>sportbotai.com · audit score 28/100 · 2,400 words · 17 sections</span><span class="sw-pill alt">v2 · Concept C1 Blueprint · 7 beats · ~620 words</span></div>
  <img src="data:image/jpeg;base64,IMG" alt="current site">
  <div class="sw-toggles"><span class="sw-tg-label">Brand</span>
  <label><input type="checkbox" id="tg-font" checked><span>Keep my font <b>Barlow Condensed</b></span></label>
  <span class="sw-tg-label">Colour world</span><!--WORLDS-->
  <label class="locked"><input type="checkbox" checked disabled><span>Keep my logo</span></label></div>
  <div class="sw-intro-cta"><button id="sw-start">Rebuild with the swarm →</button><button id="sw-skip" class="ghost">Skip to result</button><p>Agents: Audit · Concept · Beats · Hero artefact · Type · Motion · Ending · QA</p></div>`;
  const st=document.createElement('style'); st.textContent=`#sw-intro{position:fixed;inset:0;z-index:10000;background:#0B0B0C;color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:22px;font:500 14px system-ui,sans-serif;padding:24px}
  #sw-intro img{width:min(1100px,88vw);max-height:52vh;object-fit:cover;object-position:top;border-radius:8px;box-shadow:0 30px 80px rgba(0,0,0,.6);opacity:.92}
  .sw-intro-top{display:flex;gap:14px;align-items:center;opacity:.85;flex-wrap:wrap;justify-content:center;text-align:center}
  .sw-pill{background:#fff;color:#111;font-weight:700;font-size:11px;letter-spacing:.14em;padding:5px 9px;border-radius:999px}
  .sw-pill.alt{background:#10B981;color:#06281C;letter-spacing:.02em;font-weight:600}
  .sw-intro-cta{text-align:center;display:flex;flex-direction:column;gap:10px;align-items:center}
  #sw-start{background:#fff;color:#111;border:0;border-radius:999px;padding:16px 28px;font:700 16px system-ui;cursor:pointer}#sw-start:hover{background:#10B981}
  #sw-skip{background:transparent;color:#fff;border:1px solid rgba(255,255,255,.3);border-radius:999px;padding:10px 18px;font:600 13px system-ui;cursor:pointer}
  .sw-toggles{display:flex;gap:18px;align-items:center;flex-wrap:wrap;justify-content:center;font-size:13px;opacity:.9}
  .sw-tg-label{font-size:10px;letter-spacing:.16em;opacity:.5}
  .sw-toggles label{display:flex;gap:8px;align-items:center;cursor:pointer;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.14);border-radius:999px;padding:7px 12px}
  .sw-toggles label.locked{opacity:.5;cursor:default}.sw-toggles input{accent-color:#10B981}.sw-toggles b{font-weight:700}
  .sw-toggles i{display:inline-block;width:10px;height:10px;border-radius:50%;margin:0 4px 0 6px;vertical-align:-1px}
  .sw-toggles .sw{padding:5px 10px 5px 6px}.sw-toggles .sw input{position:absolute;opacity:0;width:0;height:0}.sw-toggles .sw i{width:18px;height:18px;margin:0;outline:3px solid;outline-offset:2px;border-radius:50%}.sw-toggles .sw:has(input:checked){border-color:#fff;background:rgba(255,255,255,.14)}.sw-toggles .sw span{text-transform:capitalize}
  .sw-intro-cta p{opacity:.55;margin-top:6px;font-size:12.5px}#sw-intro.out{transition:opacity .6s;opacity:0;pointer-events:none}`;
  document.head.appendChild(st); document.body.appendChild(intro);
  const go=skip=>{const h=document.documentElement; h.dataset.font=document.getElementById('tg-font').checked?'brand':'concept'; h.dataset.world=(document.querySelector('input[name=world]:checked')||{}).value||'brand'; intro.classList.add('out'); setTimeout(()=>intro.remove(),650); const s=new Swarm({agents:24,onDone:()=>setTimeout(()=>{Moves.init();window.Artefacts&&Artefacts.init()},200)}); if(skip){s.skip=true;} s.run();};
  document.getElementById('sw-start').onclick=()=>go(false);
  document.getElementById('sw-skip').onclick=()=>go(true);
})();