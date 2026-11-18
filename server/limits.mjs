/* limits.mjs — how many previews one address may start in an hour, counted where every instance of the worker sees it.

   The count used to live in each instance's memory: with two instances a visitor had twice the limit, with five, five
   times — and the limit is what stands between one address and our model credit. Now a job started by a visitor who
   is not signed in carries a key made from their address (`options.ip_key`: an HMAC, never the address itself), and
   the limit is the number of jobs with that key made in the last hour, asked of the database the instances share.

     ipKey(ip, secret)  → 32 hex characters; the same on every instance that has the same secret, not reversible
     makeIpLimit({ perHour, countSince(key, sinceIso) → Promise<number>, now, warn })
       → { key(ip), limited(ip) → Promise<boolean> }

   The memory of this instance is still asked first: it answers at once for an address hammering one instance, and it
   is what is left when the database cannot be asked (the limit is then per instance, as it was, and a warning is
   logged — never an open door, never a visitor turned away because a count failed).
   Two requests of one address arriving at two instances in the same instant can both be let through at the limit's
   edge: the guard is against hammering, and one job over is not that. */
import crypto from 'node:crypto';

export const ipKey = (ip, secret) => crypto.createHmac('sha256', String(secret || 'swarmsite')).update(String(ip || '')).digest('hex').slice(0, 32);

export function makeIpLimit({ perHour, countSince, secret = '', now = () => Date.now(), warn = () => {}, maxKeys = 5000 }) {
  const hits = new Map();   // key → [times], this instance only
  const key = ip => ipKey(ip, secret);
  const here = k => { const t = now(), h = (hits.get(k) || []).filter(x => t - x < 3600e3); hits.set(k, h);
    if (hits.size > maxKeys) for (const [a, v] of hits) if (!v.length || t - v[v.length - 1] > 3600e3) hits.delete(a);
    if (h.length >= perHour) return true; h.push(t); return false; };
  return { key,
    async limited(ip) { const k = key(ip);
      if (here(k)) return true;
      try { const n = await countSince(k, new Date(now() - 3600e3).toISOString()); return Number(n) >= perHour; }
      catch (e) { warn('ip limit: counted on this instance only — ' + String(e?.message || e).slice(0, 160)); return false; } } };
}
