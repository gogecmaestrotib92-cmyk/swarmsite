/* bucket.mjs — the template path keeps packages, data, edits and visitors' photographs in one bucket that must never be
   public. On boot, with templates mode on, the worker makes sure it exists as a private bucket: it is created when it
   is missing; when it exists and is public, templates mode is refused (logged with why) and the old engine works on.
   storage: a Supabase client's `storage` (getBucket, createBucket). */
export async function ensurePrivateBucket(storage, name, log = console.log) {
  try {
    const { data, error } = await storage.getBucket(name);
    if (!error && data) {
      if (data.public) { log(`bucket ${name} is public: templates mode refused (it would hand out packages, data and visitors' photographs); make it private and restart`); return { ok: false, why: 'public' }; }
      log(`bucket ${name} ok`); return { ok: true, created: false };
    }
    const made = await storage.createBucket(name, { public: false });
    if (made.error) { log(`bucket ${name} could not be created: templates mode refused (${String(made.error.message || made.error).slice(0, 160)})`); return { ok: false, why: 'create' }; }
    log(`bucket ${name} created`); return { ok: true, created: true };
  } catch (e) { log(`bucket ${name} could not be checked: templates mode refused (${String(e.message || e).slice(0, 160)})`); return { ok: false, why: 'check' }; }
}
