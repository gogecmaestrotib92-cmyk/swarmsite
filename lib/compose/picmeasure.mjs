/* picmeasure.mjs — what only a browser knows about the composed picture sections of a page.
   node lib/compose/picmeasure.mjs page.html      → one JSON line
   {"desktop": [{"id", "form",          one entry per composed picture section, and one ("form": "hero-backdrop") for a first screen whose picture is its ground
                 "scale": how far past its pixels the picture is drawn (the larger of width and height when it is cropped), "limit",
                 "contrast": {"ratio", "need", "text"} | null   the words that read worst against what is really behind them — the
                                                               picture under its veil, pictured with the words hidden — on a backdrop,
                 "heading_out": px the heading runs out of its block of words,
                 "overlap": px² the words lie on the picture in a form where they stand beside it}], "mobile": [...]}
   Motion is off and scroll-revealed pieces are forced visible, the way the contract and the screenshots do it. */
import { chromium } from 'playwright'; import fs from 'node:fs'; import path from 'node:path';
const file = path.resolve(process.argv[2]);
const mac = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const chromePath = process.env.CHROME_PATH || (fs.existsSync(mac) ? mac : '/usr/bin/google-chrome');
const browser = await chromium.launch({ executablePath: fs.existsSync(chromePath) ? chromePath : undefined, args: ['--no-sandbox', '--disable-gpu'].concat(process.env.LIVETEST ? ['--proxy-server=direct://', '--proxy-bypass-list=*'] : []) });
const out = {};
for (const [name, vp] of [['desktop', { width: 1440, height: 900 }], ['mobile', { width: 390, height: 844 }]]) {
  const ctx = await browser.newContext({ viewport: vp }); const page = await ctx.newPage();
  await page.route(/^https?:\/\//, r => /fonts\.gstatic|fonts\.googleapis|cdnjs|unpkg/.test(r.request().url()) && process.env.LIVETEST ? r.abort() : r.continue()).catch(() => {});
  await page.goto('file://' + file + '?nomotion=1'); await page.evaluate(() => document.fonts && document.fonts.ready).catch(() => {}); await page.waitForTimeout(350);
  await page.addStyleTag({ content: '[data-move],.sec *:not(.ps-s):not(.sp-f):not(.ps-s *):not(.sp-f *){opacity:1!important;transform:none!important;clip-path:none!important;filter:none!important}.nav{display:none!important}' }).catch(() => {});
  const seen = await page.evaluate(() => {
    const canvas = document.createElement('canvas'); canvas.width = canvas.height = 1; const c2 = canvas.getContext('2d', { willReadFrequently: true });
    const rgb = colour => { c2.clearRect(0, 0, 1, 1); c2.fillStyle = colour; c2.fillRect(0, 0, 1, 1); return [...c2.getImageData(0, 0, 1, 1).data]; };
    const cut = (a, b) => Math.max(0, Math.min(a.right, b.right) - Math.max(a.left, b.left)) * Math.max(0, Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top));
    const reads = el => { const r = el.getBoundingClientRect(); const cs = getComputedStyle(el); return { x: r.left + scrollX, y: r.top + scrollY, w: r.width, h: r.height, colour: rgb(cs.color), size: parseFloat(cs.fontSize) || 16, weight: parseInt(cs.fontWeight, 10) || 400, text: (el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 40) }; };
    const found = [];
    const hero = document.querySelector('.hero.ir.ir-has-backdrop'); const ground = hero && hero.querySelector('.ir-backdrop'); const picture = ground && ground.querySelector('img');
    if (picture) {   // a first screen whose picture is its ground: the same two questions — is it within its pixels, do the words read on it
      const nw = picture.naturalWidth, nh = picture.naturalHeight; const field = hero.getBoundingClientRect();
      const texts = [...hero.querySelectorAll('.ir-on-scrim h1, .ir-on-scrim .lede, .ir-on-scrim .lab, .ir-on-scrim a.btn.ghost, .ir-on-scrim h1 em.ir-mk-accent')].filter(el => { const r = el.getBoundingClientRect(); return r.width > 4 && r.height > 4 && (el.textContent || '').trim(); }).map(reads);
      found.push({ id: hero.id || 'top', form: 'hero-backdrop', scale: nw && nh ? +Math.max(picture.offsetWidth / nw, picture.offsetHeight / nh).toFixed(3) : null, limit: 1.35, heading_out: 0, overlap: 0, texts, field: { x: field.left + scrollX, y: field.top + scrollY, w: field.width, h: field.height } });
    }
    return found.concat([...document.querySelectorAll('section[data-pc]')].map(sec => {
      const form = sec.dataset.form || ''; const fig = sec.querySelector('.pc-fig'); const img = fig && fig.querySelector('img'); const words = sec.querySelector('.pc-words');
      if (!fig || !img || !words) return { id: sec.id, form, missing: true };
      const box = { width: img.offsetWidth, height: img.offsetHeight } /* the laid-out size: a tilt does not make a picture larger */; const nw = img.naturalWidth, nh = img.naturalHeight; const contain = getComputedStyle(img).objectFit === 'contain';
      const scale = nw && nh ? (contain ? Math.min(box.width / nw, box.height / nh) : Math.max(box.width / nw, box.height / nh)) : null;
      const wb = words.getBoundingClientRect(); const fb = fig.getBoundingClientRect(); let headingOut = 0; const h2 = words.querySelector('h2');
      if (h2) { const range = document.createRange(); range.selectNodeContents(h2); for (const r of range.getClientRects()) headingOut = Math.max(headingOut, r.right - wb.right, wb.left - r.left); }
      const onPicture = form === 'backdrop' || (form === 'bleed' && !!sec.dataset.over);   // forms whose words stand on the picture, or reach into its dissolved edge
      const texts = !onPicture ? [] : [...words.querySelectorAll('h2, p, li, .lab, a.btn.ghost, a:not(.btn)')].filter(el => {
        const r = el.getBoundingClientRect(); return r.width > 4 && r.height > 4 && (el.textContent || '').trim() && ![...el.children].some(k => /^(P|LI|UL|OL|DIV|H2)$/.test(k.tagName));
      }).map(el => { const r = el.getBoundingClientRect(); const cs = getComputedStyle(el); return { x: r.left + scrollX, y: r.top + scrollY, w: r.width, h: r.height, colour: rgb(cs.color), size: parseFloat(cs.fontSize) || 16, weight: parseInt(cs.fontWeight, 10) || 400, text: (el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 40) }; });
      const field = (sec.querySelector('.pc-field') || sec).getBoundingClientRect();
      return { id: sec.id, form, scale: scale === null ? null : +scale.toFixed(3), limit: parseFloat(fig.dataset.limit || '1.35'), heading_out: Math.max(0, Math.round(headingOut)),
               overlap: ['bleed', 'stage', 'offset', 'panorama'].includes(form) && !sec.dataset.over ? Math.round(cut(wb, fb)) : 0, texts, field: { x: field.left + scrollX, y: field.top + scrollY, w: field.width, h: field.height } };
    }));
  });
  const onPicture = seen.filter(s => s.texts && s.texts.length);
  if (onPicture.length) {   // what is really behind the words: the section pictured with its words hidden
    await page.addStyleTag({ content: 'section[data-pc] .pc-words,.hero.ir.ir-has-backdrop .ir-text,.hero.ir.ir-has-backdrop .ir-actions{visibility:hidden!important}' });
    for (const s of onPicture) {
      const clip = { x: Math.max(0, Math.floor(s.field.x)), y: Math.max(0, Math.floor(s.field.y)), width: Math.max(1, Math.min(vp.width, Math.ceil(s.field.w))), height: Math.max(1, Math.min(4000, Math.ceil(s.field.h))) };
      const png = (await page.screenshot({ type: 'png', fullPage: true, clip })).toString('base64');
      s.contrast = await page.evaluate(async ({ png, texts, origin }) => {
        const img = new Image(); img.src = 'data:image/png;base64,' + png; await img.decode();
        const c = document.createElement('canvas'); c.width = img.naturalWidth; c.height = img.naturalHeight; const g = c.getContext('2d', { willReadFrequently: true }); g.drawImage(img, 0, 0);
        const lin = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
        const lum = p => 0.2126 * lin(p[0]) + 0.7152 * lin(p[1]) + 0.0722 * lin(p[2]);
        let worst = null;
        for (const t of texts) {
          const x = Math.max(0, Math.floor(t.x - origin.x)), y = Math.max(0, Math.floor(t.y - origin.y)); const w = Math.min(c.width - x, Math.ceil(t.w)), h = Math.min(c.height - y, Math.ceil(t.h));
          if (w < 2 || h < 2) continue;
          const data = g.getImageData(x, y, w, h).data; const ls = [];
          for (let i = 0; i < data.length; i += 4 * 3) ls.push(lum([data[i], data[i + 1], data[i + 2]]));
          ls.sort((a, b) => a - b); const own = lum(t.colour);
          const behind = own > 0.4 ? ls[Math.min(ls.length - 1, Math.floor(ls.length * 0.95))] : ls[Math.floor(ls.length * 0.05)];   // the lightest ground light words must stand on, the darkest for dark words
          const ratio = (Math.max(own, behind) + 0.05) / (Math.min(own, behind) + 0.05); const need = t.size >= 24 || (t.size >= 18.66 && t.weight >= 700) ? 3 : 4.5;
          if (!worst || ratio / need < worst.ratio / worst.need) worst = { ratio: +ratio.toFixed(2), need, text: t.text };
        }
        return worst;
      }, { png, texts: s.texts, origin: { x: clip.x, y: clip.y } });
    }
  }
  out[name] = seen.map(({ texts, field, ...rest }) => ({ contrast: null, ...rest }));
  await ctx.close();
}
await browser.close(); console.log(JSON.stringify(out));
