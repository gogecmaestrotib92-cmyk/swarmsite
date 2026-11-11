/* auth.mjs — who is asking, and what an account may still start. No secrets here: the server verifies the visitor's own
   Supabase session token with the service client it already holds; the browser only ever has the project's public key.

   bearer(req)                 the token of an Authorization: Bearer header, or ''
   makeUserOf(sb)              async req → { id, email } | null   (verified by Supabase; cached for a minute per token)
   allowance({used, free, paid})  → { used, free, left, allowed }
   mine(row)                   a job as its owner's dashboard lists it (never the whole result) */

export const bearer = req => { const m = String(req?.headers?.authorization || '').match(/^Bearer\s+([A-Za-z0-9._~+/=-]{20,4096})$/); return m ? m[1] : ''; };

export function makeUserOf(sb, ttlMs = 60000, now = () => Date.now()) {
  const seen = new Map();   // token → { user, at }
  return async req => {
    const token = bearer(req); if (!token) return null;
    const hit = seen.get(token); if (hit && now() - hit.at < ttlMs) return hit.user;
    let user = null;
    try { const { data, error } = await sb.auth.getUser(token); if (!error && data?.user?.id) user = { id: data.user.id, email: String(data.user.email || '').toLowerCase() || null }; } catch { user = null; }
    if (seen.size > 2000) for (const [k, v] of seen) if (now() - v.at >= ttlMs) seen.delete(k);
    seen.set(token, { user, at: now() });
    return user;
  };
}

export const allowance = ({ used = 0, free = 0, paid = false } = {}) => { const u = Math.max(0, Number(used) || 0), f = Math.max(0, Number(free) || 0); return { used: u, free: f, left: Math.max(0, f - u), allowed: !!paid || u < f }; };

export const mine = row => {
  const r = row?.result || {}; const studio = r.studio || {};
  return { id: row.id, url: row.url, status: row.status, step: row.step || null, created_at: row.created_at, seconds: r.seconds ?? null,
    preview: typeof r.previewUrl === 'string' ? r.previewUrl : null, before: typeof r.beforeUrl === 'string' ? r.beforeUrl : null,
    designs: Array.isArray(studio.variants) ? studio.variants.filter(v => v && v.clean).length : (r.previewUrl ? 1 : 0) };
};
