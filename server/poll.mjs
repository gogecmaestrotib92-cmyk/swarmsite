/* poll.mjs — how the slots of one instance ask the queue for work.

   Each slot of a worker used to ask for itself every 2.5 s, so an instance with 8 slots asked an empty queue some three
   times a second, and five such instances fifteen. Here one slot asks at a time: it says when the queue may be asked
   again (`idleMs` from now) and the others wait for that moment. The slot that is handed a job wakes the waiting ones at
   once, because a job seldom arrives alone — so a burst is taken as fast as the claims answer, and an empty queue costs
   one question each `idleMs` for the instance, whatever its number of slots.

     makeClaimer({ claim() → Promise<job | null>, idleMs, now }) → { next() → Promise<job> }
   `next()` answers only with a job; a claim that throws is thrown to the caller (who waits and asks again). */
export function makeClaimer({ claim, idleMs = 2500, now = () => Date.now() }) {
  let emptyUntil = 0; const waiting = new Set();
  const idle = ms => new Promise(r => { let t; const done = () => { clearTimeout(t); waiting.delete(done); r(); }; t = setTimeout(done, ms); waiting.add(done); });
  return { async next() {
    for (;;) {
      const wait = emptyUntil - now(); if (wait > 0) { await idle(wait); continue; }
      emptyUntil = now() + idleMs;   // this slot asks; the others wait for its answer
      const job = await claim();
      if (job) { emptyUntil = 0; for (const w of [...waiting]) w(); return job; }
    }
  } };
}
