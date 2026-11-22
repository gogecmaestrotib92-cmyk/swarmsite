// flat.mjs — how much of a photographed part of a page is one tone. A part that drew nothing (an embed that failed to
// load, an empty box) is not a picture of the product.
// the share of a picture taken by its commonest tone (colours read in steps of 16); at or above FLAT_SHOT it shows nothing
export const FLAT_SHOT = .9;
export async function flatShot(page, dataUrl) {
  try {
    return await page.evaluate(async src => {
      const im = new Image(); im.src = src; await im.decode();
      const w = 96, h = Math.max(1, Math.round(96 * im.naturalHeight / im.naturalWidth)); const c = document.createElement('canvas'); c.width = w; c.height = h;
      const g = c.getContext('2d'); g.drawImage(im, 0, 0, w, h); const px = g.getImageData(0, 0, w, h).data; const n = {};
      for (let i = 0; i < px.length; i += 4) { const k = (px[i] >> 4) + '.' + (px[i + 1] >> 4) + '.' + (px[i + 2] >> 4); n[k] = (n[k] || 0) + 1; }
      return Math.max(...Object.values(n)) / (w * h); }, dataUrl);
  } catch { return 0; }
}

