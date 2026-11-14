/* progress.js — how far a job is, as a share of the time it usually takes: the ring under the working screen's heading.

   Progress.of(job, typical, now) -> { pct, done }
     job      the public job: steps [{id, status, at}] — `at` is when a step was last set (running: when it began)
     typical  seconds each step usually takes, by id — the worker's own medians of its recent jobs (GET /config
              `typical`); where it says nothing, TYPICAL below (medians of eleven real jobs, 2026-11-13/14)
     now      ms

   The ring counts down to the moment the designs are shown: the steps up to `publish` (the downloads are prepared
   after the chooser is already open). A finished step counts whole. The running step counts by its own clock against
   its usual time, up to nine tenths; past its usual time it creeps toward — and never reaches — the whole, so the
   ring says 100 only when the work is done, and a slow site is not shown as stuck or as finished. */
(function (root) {
  const TYPICAL = { form: 2, capture: 77, read: 19, choose: 68, publish: 11, package: 111 };
  function of(job, typical, now) {
    const all = (job && job.steps) || [], cut = all.findIndex(s => s.id === 'publish'), steps = cut >= 0 ? all.slice(0, cut + 1) : all;
    if (!steps.length) return { pct: 0, done: false };
    const known = steps.map(s => +((typical || {})[s.id]) || TYPICAL[s.id] || 0).filter(Boolean), mean = known.length ? known.reduce((a, b) => a + b, 0) / known.length : 30;
    let sum = 0, total = 0, done = 0;
    for (const s of steps) { const w = +((typical || {})[s.id]) || TYPICAL[s.id] || mean; total += w;
      if (s.status === 'done') { sum += w; done++; }
      else if (s.status === 'running') { const e = Math.max(0, (now - Date.parse(s.at || '')) / 1000 || 0); sum += w * (e <= w ? .9 * e / w : .9 + .09 * (1 - Math.exp(-(e - w) / w))); } }
    const finished = done === steps.length || job.status === 'done';
    return { pct: finished ? 100 : Math.min(99, Math.floor(100 * sum / total)), done: finished };
  }
  const api = { of, TYPICAL };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.Progress = api;
})(typeof window !== 'undefined' ? window : globalThis);
