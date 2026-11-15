// focus.mjs — where on a product's screen the product is: a coarse map of detail (32 columns, rows to the picture's own
// proportion; each cell the sum of tone steps between neighbouring pixels in it, 0–99 of the picture's busiest cell).
// A template that shows a screen in a small frame finds on this map the part that fills its own frame's shape best and
// shows that part at a size that reads, not the whole screen shrunk to a smear (the windows design set a 767 px screen
// in a 200 px window: letters 3 px high; owner, 2026-11-15). Run in the page: page.evaluate(DETAIL, dataUri).
// No model call; the same picture gives the same map.
export const DETAIL = async d => {
  const im = new Image(); im.src = d; await im.decode();
  const C = 32, R = Math.max(8, Math.min(64, Math.round(C * im.height / im.width))), k = 5, W = C * k, H = R * k;
  const c = document.createElement('canvas'); c.width = W; c.height = H;
  const g = c.getContext('2d', { willReadFrequently: true }); g.drawImage(im, 0, 0, W, H); const px = g.getImageData(0, 0, W, H).data;
  const L = i => .3 * px[4 * i] + .59 * px[4 * i + 1] + .11 * px[4 * i + 2];
  const cell = new Float32Array(C * R); let top = 0;
  for (let y = 0; y < H - 1; y++) for (let x = 0; x < W - 1; x++) { const i = y * W + x, v = Math.abs(L(i) - L(i + 1)) + Math.abs(L(i) - L(i + W)), j = Math.floor(y / k) * C + Math.floor(x / k); cell[j] += v; }
  for (const v of cell) top = Math.max(top, v);
  if (!top) return null;
  const rows = []; for (let r = 0; r < R; r++) rows.push(Array.from(cell.slice(r * C, r * C + C), v => Math.round(99 * v / top)));
  return rows;
};
