// Set this to the Railway service URL once deployed (no trailing slash).
window.SWARMSITE_API = window.SWARMSITE_API || 'https://swarmsite-production.up.railway.app';

// Accounts (Supabase Auth). Both values are PUBLIC by design — the project's address and its anon key are sent to every
// browser; what an account may read is decided on the server. Leave `anon` empty and the site works without accounts.
window.SWARMSITE_SUPABASE = window.SWARMSITE_SUPABASE || { url: 'https://xzwudmqtniwavonsapdq.supabase.co', anon: 'sb_publishable_CuY7wTGenNGSHDNUs51eAg_vBX-Carl' };   // the project's publishable key: Supabase marks it "can be safely shared publicly"; the secret key lives only in Railway
// Which ways to sign in are offered, in this order. 'email' sends a link; 'github' and 'google' need the provider switched on in Supabase.
window.SWARMSITE_LOGIN = window.SWARMSITE_LOGIN || ['email'];   // add 'github' and 'google' here once each is switched on in Supabase (Authentication → Sign In / Providers)
