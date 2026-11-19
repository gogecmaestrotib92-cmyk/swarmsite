/* admin.mjs — the owner's page of numbers: who may ask for them, and how they are counted. No secret here: the one that
   opens the page is the deployment's variable ADMIN_TOKEN (Railway → the service → Variables), set by the owner, never
   written to code, a log or an answer. Without it — or with one shorter than 16 characters — nobody is let in.

     makeAdminGate({ env, now })  → check({ ip, authorization }) → { status: 200 | 401 | 429 | 503, error? }
     summarise({ events, jobs, paid, days, now, tz })  → what web/admin.html draws

   Visitors are the people who are not us: a browser that has opened the owner's page is counted apart (`own`), and so is
   every job it starts; a job nobody's page was seen opening for is `unseen`. Every number is a count of rows that exist: of `events` (server/track.mjs) and of `jobs`. A day before the first
   event was ever written has null — "no data" — for what only events can say, never 0. A failed job's reason passes
   scrub() (server/designs.mjs): the page never names a template. Nothing here calls a model. */
import crypto from 'node:crypto';
import { scrub } from './designs.mjs';
import { PAGE_NAMES, REFUSALS } from './track.mjs';

export const adminToken = env => { const t = String(env?.ADMIN_TOKEN || '').trim(); return t.length >= 16 ? t : ''; };
const same = (a, b) => { const h = s => crypto.createHash('sha256').update(String(s)).digest(); return crypto.timingSafeEqual(h(a), h(b)); };

export function makeAdminGate({ env, now = () => Date.now(), maxFails = 10, windowMs = 15 * 60e3 }) {
  const fails = new Map();   // address → [times of wrong tries], this instance
  return function check({ ip = '', authorization = '' } = {}) {
    const token = adminToken(env); if (!token) return { status: 503, error: 'The admin page is not switched on: ADMIN_TOKEN is not set (16 characters or more).' };
    const t = now(), f = (fails.get(ip) || []).filter(x => t - x < windowMs);
    if (f.length >= maxFails) return { status: 429, error: 'Too many wrong tries. Wait fifteen minutes.' };
    const m = String(authorization || '').match(/^Bearer\s+(\S{1,512})$/);
    if (m && same(m[1], token)) return { status: 200 };
    f.push(t); fails.set(ip, f); if (fails.size > 5000) fails.clear();
    return { status: 401, error: 'Wrong or missing key.' };
  };
}

export const dayIn = (ms, tz) => { try { return new Intl.DateTimeFormat('en-CA', { timeZone: tz, year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date(ms)); } catch { return new Date(ms).toISOString().slice(0, 10); } };
const lastDays = (n, now, tz) => { const out = []; for (let i = n - 1; i >= 0; i--) { const d = dayIn(now - i * 86400e3, tz); if (out[out.length - 1] !== d) out.push(d); } return out; };   // a clock change can repeat a day: once is enough
const siteOf = url => { const u = String(url || ''); if (u.startsWith('form:')) return 'form'; try { return new URL(u).hostname.replace(/^www\./, ''); } catch { return u.slice(0, 60); } };
const reason = e => scrub(String(e || 'no reason was written').replace(/\s+/g, ' ').trim()).slice(0, 240);
const top = (map, n) => [...map.entries()].map(([key, set]) => ({ key, visitors: set.size })).sort((a, b) => b.visitors - a.visitors || (a.key < b.key ? -1 : 1)).slice(0, n);

/* events: rows of `events`, or null when the table could not be read. jobs: {id, created_at, status, error, url, source,
   engine, vk} made in the window. paid: {id, paid} of every job with a payment (result.paid: {slug: {at}}). */
export function summarise({ events, jobs = [], paid = [], days = 14, now = Date.now(), tz = 'Europe/Ljubljana', firstEventAt = null }) {
  const list = lastDays(days, now, tz), idx = new Map(list.map((d, i) => [d, i])), has = Array.isArray(events);
  const first = firstEventAt ? dayIn(Date.parse(firstEventAt), tz) : null;   // the day recording began: before it there is nothing to count
  const known = d => has && first !== null && d >= first;
  const rows = list.map(d => ({ day: d, recorded: known(d), views: known(d) ? 0 : null, visitors: known(d) ? 0 : null, pages: known(d) ? Object.fromEntries(PAGE_NAMES.map(p => [p, 0])) : null,
    own: known(d) ? 0 : null, guest_started: known(d) ? 0 : null, guest_done: known(d) ? 0 : null, guest_failed: known(d) ? 0 : null, own_started: known(d) ? 0 : null, unseen_started: known(d) ? 0 : null,
    started: 0, done: 0, failed: 0, waiting: 0, opened: known(d) ? 0 : null, edited: known(d) ? 0 : null, kept: known(d) ? 0 : null, pay_started: known(d) ? 0 : null, paid: 0, downloaded: known(d) ? 0 : null,
    refused: known(d) ? Object.fromEntries([...REFUSALS, 'other'].map(r => [r, 0])) : null }));
  const sets = list.map(() => ({ own: new Set(), visitors: new Set(), opened: new Set(), edited: new Set(), kept: new Set(), pay_started: new Set(), downloaded: new Set() }));
  const all = { own: new Set(), visitors: new Set(), opened: new Set(), edited: new Set(), kept: new Set(), pay_started: new Set(), downloaded: new Set() };
  const refs = new Map(), camps = new Map(), pageVisitors = Object.fromEntries(PAGE_NAMES.map(p => [p, new Set()]));
  const put = (map, key, v) => { if (!map.has(key)) map.set(key, new Set()); map.get(key).add(v); };
  const STEP = { design_opened: 'opened', edit: 'edited', edit_kept: 'kept', pay_started: 'pay_started', download: 'downloaded' };
  // Us and them. A browser that has opened the owner's page marks its reports (detail = own); its key of the day is ours,
  // and so is a job started under that key. A job under a visitor's key is a visitor's. A job under no key we saw a page
  // opened with — a script, a test, a blocked counter, a day before recording — is neither: it is counted as unseen.
  const ownKeys = new Set(), guestKeys = new Set();
  for (const e of has ? events : []) if (e.visitor && (e.name === 'visit' || e.name === 'design_opened')) (e.detail === 'own' ? ownKeys : guestKeys).add(e.visitor);
  for (const k of ownKeys) guestKeys.delete(k);
  const whose = j => !j?.vk ? 'unseen' : ownKeys.has(j.vk) ? 'own' : guestKeys.has(j.vk) ? 'guest' : 'unseen', jobWho = new Map(jobs.map(j => [j.id, whose(j)]));
  const ours = e => e.detail === 'own' || (e.visitor && ownKeys.has(e.visitor)) || (e.job && jobWho.get(e.job) === 'own');
  for (const e of has ? events : []) {
    const i = idx.get(dayIn(Date.parse(e.at), tz)); if (i === undefined || !rows[i].recorded) continue; const r = rows[i];
    if (ours(e)) { if (e.name === 'visit') { const who = (e.visitor || 'unknown') + '@' + r.day; sets[i].own.add(who); all.own.add(who); } continue; }
    if (e.name === 'visit') {
      // one person on one day is one visitor, whatever the hour: the key is made new each UTC day, so the day is part of it
      const who = (e.visitor || 'unknown') + '@' + r.day; r.views++; sets[i].visitors.add(who); all.visitors.add(who);
      const p = PAGE_NAMES.includes(e.page) ? e.page : 'other'; r.pages[p]++; pageVisitors[p].add(who);
      put(refs, e.ref || '(direct or unknown)', who);
      if (e.src || e.campaign || e.medium) put(camps, [e.src || '–', e.medium || '–', e.campaign || '–'].join(' / '), who);
    } else if (e.name === 'job_refused') { r.refused[REFUSALS.includes(e.detail) ? e.detail : 'other']++; }
    else if (STEP[e.name] && e.job) { sets[i][STEP[e.name]].add(e.job); all[STEP[e.name]].add(e.job); }
  }
  rows.forEach((r, i) => { if (!r.recorded) return; r.visitors = sets[i].visitors.size; r.own = sets[i].own.size; for (const k of ['opened', 'edited', 'kept', 'pay_started', 'downloaded']) r[k] = sets[i][k].size; });
  const failed = [];
  for (const j of jobs) {
    const i = idx.get(dayIn(Date.parse(j.created_at), tz)); if (i === undefined) continue; const r = rows[i];
    r.started++; if (j.status === 'done') r.done++; else if (j.status === 'failed') { r.failed++; failed.push({ at: j.created_at, who: r.recorded ? jobWho.get(j.id) : null, site: siteOf(j.url), from: j.source === 'form' ? 'form' : 'address', reason: reason(j.error) }); } else r.waiting++;
    if (r.recorded) { const w = jobWho.get(j.id); if (w === 'own') r.own_started++; else if (w === 'unseen') r.unseen_started++; else { r.guest_started++; if (j.status === 'done') r.guest_done++; else if (j.status === 'failed') r.guest_failed++; } }
  }
  let paidTotal = 0;
  for (const j of paid) if (jobWho.get(j.id) !== 'own') for (const p of Object.values(j?.paid && typeof j.paid === 'object' ? j.paid : {})) { const t = Date.parse(p?.at); if (!Number.isFinite(t)) continue; const i = idx.get(dayIn(t, tz)); if (i !== undefined) { rows[i].paid++; paidTotal++; } }
  const sum = k => rows.reduce((a, r) => a + (r[k] || 0), 0), anyRecorded = rows.some(r => r.recorded), ev = k => anyRecorded ? all[k].size : null, rec = k => anyRecorded ? sum(k) : null;
  const refusedTotal = anyRecorded ? Object.fromEntries([...REFUSALS, 'other'].map(k => [k, rows.reduce((a, r) => a + (r.refused ? r.refused[k] : 0), 0)])) : null;
  return {
    generated_at: new Date(now).toISOString(), tz, days: list.length, recording_since: firstEventAt || null, events_readable: has,
    total: { views: anyRecorded ? sum('views') : null, visitors: ev('visitors'), own: ev('own'), guest_started: rec('guest_started'), guest_done: rec('guest_done'), guest_failed: rec('guest_failed'), own_started: rec('own_started'), unseen_started: rec('unseen_started'), started: sum('started'), done: sum('done'), failed: sum('failed'), waiting: sum('waiting'),
      opened: ev('opened'), edited: ev('edited'), kept: ev('kept'), pay_started: ev('pay_started'), paid: paidTotal, downloaded: ev('downloaded') },
    by_day: rows,
    pages: anyRecorded ? PAGE_NAMES.map(p => ({ key: p, views: rows.reduce((a, r) => a + (r.pages ? r.pages[p] : 0), 0), visitors: pageVisitors[p].size })).filter(p => p.views) : null,
    sources: anyRecorded ? top(refs, 15) : null, campaigns: anyRecorded ? top(camps, 15) : null,
    failed: failed.sort((a, b) => (a.at < b.at ? 1 : -1)).slice(0, 25), refused: refusedTotal,
  };
}
