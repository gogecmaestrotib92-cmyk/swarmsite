/* payments.mjs — paying for a design (owner, 2026-11-12: previews free, payment at download). Stripe Checkout, one
   price (STRIPE_PRICE_ID) per job and design. A design paid by an account is downloaded and published by that account
   without paying again; PACKAGES_FREE=1 lets everything through, for testing.

   Without STRIPE_SECRET_KEY (and STRIPE_PRICE_ID) nothing here is switched on: the download and publish answer 402 as
   before, with no address to pay at, and the pages show no pay button. Keys live in Railway variables only; nothing here
   logs a key, a signature, an email or a card.

   Where it is kept: in the job record, beside its owner (jobs.user_id): result.paid[<slug>] = {user, session, at}. The
   webhook writes it; writing it twice for the same session changes nothing.

   Stripe events to subscribe the webhook to: checkout.session.completed, checkout.session.async_payment_succeeded. */

export const configured = env => !!(env.STRIPE_SECRET_KEY && env.STRIPE_PRICE_ID);
export const SLUG = /^[a-z0-9][a-z0-9_-]{0,63}$/;
export const paidBy = (row, slug, user) => !!user && row?.result?.paid?.[slug]?.user === user.id;

// the gate the download and publish pass after sign-in: free, paid, or 402 with where to pay when payment is on
export function payGate({ env, row, slug, user, what = 'download' }) {
  if (env.PACKAGES_FREE === '1' || paidBy(row, slug, user)) return null;
  return { status: 402, body: { error: `Payment is needed to ${what} this page.`, pay: true, ...(configured(env) ? { pay_url: '/pay', job: row?.id, slug } : {}) } };
}

// the official client, loaded only when the deployment has a key (the package is in server/package.json)
export async function stripeOf(env, load = () => import('stripe')) {
  if (!env.STRIPE_SECRET_KEY) return null;
  const S = (await load()).default;
  return new S(env.STRIPE_SECRET_KEY);
}

// where Checkout sends the visitor back: the page they paid from, on the site's own origin
export function returnUrls(env, row, slug, from) {
  const web = String(env.PUBLIC_APP || 'https://swarmsite.si').replace(/\/$/, '');
  const back = from === 'edit' ? `${web}/edit?job=${row.id}&slug=${slug}` : `${web}/app?job=${row.id}`;
  return { success_url: `${back}&paid=${slug}`, cancel_url: `${back}&paid=0` };
}

export async function checkout({ stripe, env, row, slug, user, from }) {
  const s = await stripe.checkout.sessions.create({
    mode: 'payment',
    line_items: [{ price: env.STRIPE_PRICE_ID, quantity: 1 }],
    client_reference_id: `${row.id}:${slug}`,
    ...(user.email ? { customer_email: user.email } : {}),
    metadata: { job: row.id, slug, user: user.id },
    ...returnUrls(env, row, slug, from),
  });
  return { url: s.url, id: s.id };
}

// a Stripe event, its signature checked against the raw body; a paid session marks its job and design paid
export async function webhook({ stripe, env, raw, signature, markPaid }) {
  let event;
  try { event = stripe.webhooks.constructEvent(raw, signature, env.STRIPE_WEBHOOK_SECRET); }
  catch { return { status: 400, body: { error: 'bad signature' } }; }
  if (event.type === 'checkout.session.completed' || event.type === 'checkout.session.async_payment_succeeded') {
    const s = event.data?.object || {};
    if (s.payment_status !== 'paid') return { status: 200, body: { received: true, paid: false } };   // a delayed payment: its success event comes later
    const m = s.metadata || {}; const [job, slug] = String(s.client_reference_id || '').split(':');
    if (!/^[0-9a-f-]{36}$/.test(job || '') || !SLUG.test(slug || '') || m.job !== job || m.slug !== slug || !m.user) return { status: 200, body: { received: true, ignored: true } };
    await markPaid({ job, slug, user: m.user, session: s.id });
    return { status: 200, body: { received: true, paid: true } };
  }
  return { status: 200, body: { received: true } };
}

// the record a payment leaves: idempotent per session; another payment for the same design is kept as the first
export function withPaid(result, { slug, user, session, at }) {
  const r = { ...(result || {}) }, paid = { ...(r.paid || {}) };
  if (paid[slug]?.user === user) return null;   // already paid by this account: nothing to write
  paid[slug] = { user, session, at };
  return { ...r, paid };
}
