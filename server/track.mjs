/* track.mjs — who came and what they did, written down by us, on our own server and database. No third party's script,
   no cookie, nothing kept in the visitor's browser, and never an address: a visitor is counted by a key made from their
   address and browser with the day mixed in (an HMAC), so the same person is another key tomorrow and nobody can be
   followed from one day into the next. That is why the site needs no consent banner (privacy.html: "cookieless analytics").

   What is written is only what leaves no row anywhere else (table `events`, server/migrations/20261119_events.sql):
     visit           a page was opened              (the page's own script, web/js/track.js → POST /e)
     design_opened   a design looked at full screen (the same script)
     job_refused     POST /jobs turned a visitor away: detail = rate_limit | queue_full | day_budget
     edit            a design was changed in the editor (once a job a day an instance)
     edit_kept       edits were kept
     pay_started     a Stripe Checkout was opened
     download        a package was handed out
   Jobs, how they ended, why they failed and what was paid for are already in `jobs`; they are read from there.

   Recording never costs a visitor anything: record() only puts a row in memory and returns; rows are written a second
   later in one insert; a write that fails is counted and dropped, never retried into a queue that grows, never thrown.

     isBot(ua)                          a crawler, a link preview, a script, a monitor, a headless browser
     pageOf(path)                       landing | app | start | edit | dashboard | login | blog | privacy | terms | other
     refHost(ref, own)                  the host a visitor came from ('' for our own pages and for anything not a host)
     visitorKey(ip, ua, secret, day)    24 hex characters, another one each day
     cleanBeacon(body)                  what a page may tell us, or null
     makeTracker({ insert, secret, now, flushMs, warn }) → { record, once, beacon, refused, visitor, flush, counts } */
import crypto from 'node:crypto';

export const SERVER_EVENTS = ['job_refused', 'edit', 'edit_kept', 'pay_started', 'download'];
export const PAGE_EVENTS = ['visit', 'design_opened'];   // the only names a page may send
export const REFUSALS = ['rate_limit', 'queue_full', 'day_budget'];
const BOT = /bot\b|bot[\/;) _-]|crawl|spider|slurp|headless|lighthouse|pagespeed|page speed|preview|monitor|uptime|pingdom|curl|wget|python|node-fetch|undici|axios|go-http|java\/|okhttp|httpclient|libwww|phantom|puppeteer|playwright|selenium|scrapy|facebookexternalhit|whatsapp|telegram|slack|discord|gptbot|chatgpt|claude|anthropic|perplexity|bytespider|semrush|ahrefs|mj12|dotbot|petalbot|yandex|baiduspider|duckduck|bingpreview|google-inspectiontool|vercel-screenshot/i;
export const isBot = ua => { const s = String(ua || ''); return s.length < 20 || s.length > 600 || BOT.test(s); };

const PAGES = [[/^\/(index(\.html)?)?$/, 'landing'], [/^\/app(\.html)?\/?$/, 'app'], [/^\/start(\.html)?\/?$/, 'start'], [/^\/edit(\.html)?\/?$/, 'edit'], [/^\/dashboard(\.html)?\/?$/, 'dashboard'],
  [/^\/login(\.html)?\/?$/, 'login'], [/^\/blog(\/|$)/, 'blog'], [/^\/privacy(\.html)?\/?$/, 'privacy'], [/^\/terms(\.html)?\/?$/, 'terms']];
export const PAGE_NAMES = [...PAGES.map(p => p[1]), 'other'];
// a page by its kind, never its address: a query string (a job's id, an email in a link) is not ours to keep
export const pageOf = p => { const s = String(p || '').split(/[?#]/)[0].toLowerCase(); return (PAGES.find(([re]) => re.test(s)) || [0, 'other'])[1]; };

const OWN = /(^|\.)swarmsite\.si$|^localhost$|^127\.|(^|\.)vercel\.app$|(^|\.)railway\.app$/;
// where a visitor came from, as a host only (a referrer's path and query can name a person or a search)
export function refHost(ref) {
  let h = String(ref || '').trim().toLowerCase(); if (!h) return '';
  if (/^[a-z][a-z0-9+.-]*:\/\//.test(h)) { try { h = new URL(h).hostname; } catch { return ''; } }
  h = h.replace(/^www\./, '').replace(/\.$/, '');
  if (h.length > 80 || !/^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+$/.test(h) || OWN.test(h)) return '';
  return h;
}
// a campaign tag as its author wrote it, cut to what a tag is; anything else is dropped
const tag = v => { const s = String(v ?? '').trim().toLowerCase().slice(0, 60); return /^[a-z0-9][a-z0-9 ._+-]*$/.test(s) ? s : ''; };
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;

export const utcDay = ms => new Date(ms).toISOString().slice(0, 10);
export const visitorKey = (ip, ua, secret, day) => crypto.createHmac('sha256', String(secret || 'swarmsite') + '|visitor|' + day).update(String(ip || '') + '|' + String(ua || '')).digest('hex').slice(0, 24);

// what a page may tell us: one of two names, where it is, where the visitor came from, the campaign's tags, a job's id
export function cleanBeacon(body) {
  let b = body; if (Buffer.isBuffer(b)) b = b.toString('utf8');
  if (typeof b === 'string') { if (b.length > 2000) return null; try { b = JSON.parse(b); } catch { return null; } }
  if (!b || typeof b !== 'object' || Array.isArray(b) || !PAGE_EVENTS.includes(b.n)) return null;
  const job = UUID.test(String(b.j || '')) ? String(b.j) : null;
  if (b.n === 'design_opened' && !job) return null;
  return { name: b.n, page: pageOf(b.p), ref: refHost(b.r) || null, src: tag(b.s) || null, medium: tag(b.m) || null, campaign: tag(b.c) || null, job };
}

export function makeTracker({ insert, secret = '', now = () => Date.now(), flushMs = 1000, warn = () => {}, maxBuffer = 2000, perVisitorPerHour = 120, perHour = 20000, timer = true }) {
  const counts = { recorded: 0, failed: 0, dropped: 0, bots: 0, since: now(), last_error_at: null };
  let buf = [], pending = null, hour = 0, inHour = 0, seen = new Map(), onceKeys = new Set(), onceDay = '', warnedAt = 0;
  const flush = async () => {
    pending = null; if (!buf.length) return; const rows = buf; buf = [];
    try { await insert(rows); counts.recorded += rows.length; }
    catch (e) { counts.failed += rows.length; counts.last_error_at = now();
      if (now() - warnedAt > 600e3) { warnedAt = now(); try { warn('track: ' + rows.length + ' events not written — ' + String(e?.message || e).slice(0, 120)); } catch { /* a log that fails is not a visitor's problem */ } } }
  };
  const record = ev => {
    try {
      if (!ev || ![...SERVER_EVENTS, ...PAGE_EVENTS].includes(ev.name)) return false;
      if (buf.length >= maxBuffer) { counts.dropped++; return false; }
      buf.push({ at: new Date(now()).toISOString(), name: ev.name, page: ev.page || null, visitor: ev.visitor || null, ref: ev.ref || null, src: ev.src || null, medium: ev.medium || null,
        campaign: ev.campaign || null, job: ev.job && UUID.test(String(ev.job)) ? String(ev.job) : null, detail: ev.detail ? String(ev.detail).slice(0, 40) : null });
      if (timer && !pending) { pending = setTimeout(() => { flush().catch(() => {}); }, flushMs); pending.unref?.(); }
      return true;
    } catch { counts.dropped++; return false; }
  };
  const visitor = req => { try { return visitorKey(String(req?.headers?.['x-forwarded-for'] || req?.socket?.remoteAddress || '').split(',')[0].trim(), req?.headers?.['user-agent'] || '', secret, utcDay(now())); } catch { return null; } };
  return { record, flush, visitor, counts: () => ({ ...counts, waiting: buf.length }),
    // the same thing happening again to the same job today is one row (an editor draws the page on every change)
    once(name, job, extra = {}) { const d = utcDay(now()); if (d !== onceDay || onceKeys.size > 20000) { onceKeys = new Set(); onceDay = d; }
      const k = name + ':' + job; if (onceKeys.has(k)) return false; onceKeys.add(k); return record({ ...extra, name, job }); },
    refused(req, why) { return record({ name: 'job_refused', detail: REFUSALS.includes(why) ? why : 'other', visitor: visitor(req) }); },
    // a page's own report. Never throws, never waits; a crawler's and a flood's are counted and dropped.
    beacon(req) {
      try {
        const ua = String(req?.headers?.['user-agent'] || ''); if (isBot(ua)) { counts.bots++; return false; }
        const ev = cleanBeacon(req?.body); if (!ev) { counts.dropped++; return false; }
        // the hour's count is by address alone (as a key), so a script that names a new browser each time is still one sender;
        // and an instance writes no more than `perHour` page reports an hour, whoever sends them
        const v = visitor(req), h = Math.floor(now() / 3600e3); if (h !== hour) { hour = h; inHour = 0; seen = new Map(); } if (seen.size > 50000) seen = new Map();
        const who = visitor({ headers: { 'x-forwarded-for': req?.headers?.['x-forwarded-for'] }, socket: req?.socket }), n = (seen.get(who) || 0) + 1; seen.set(who, n);
        if (n > perVisitorPerHour || ++inHour > perHour) { counts.dropped++; return false; }
        return record({ ...ev, visitor: v });
      } catch { counts.dropped++; return false; }
    } };
}
