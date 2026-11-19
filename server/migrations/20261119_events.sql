-- Apply once in the Supabase SQL editor; safe before or after the deploy and safe to run twice. Until it is applied
-- the worker counts every event as "not written" and the owner's page says the table is missing — nothing else changes.
--
-- What a visit leaves (server/track.mjs). No address, no cookie id, no email: `visitor` is a key that is made new
-- every day and cannot be turned back into an address; `ref` is a host only; `page` is a kind of page, never a URL.
create table if not exists public.events (
  id bigint generated always as identity primary key,
  at timestamptz not null default now(),
  name text not null,        -- visit | design_opened | job_refused | edit | edit_kept | pay_started | download
  page text,                 -- landing | app | start | edit | dashboard | login | blog | privacy | terms | other
  visitor text,              -- a daily key, never an address
  ref text,                  -- the host a visitor came from
  src text, medium text, campaign text,   -- utm_source, utm_medium, utm_campaign
  job uuid,
  detail text                -- job_refused: rate_limit | queue_full | day_budget
);
create index if not exists events_at on public.events(at);
-- Row level security with no policy: only the worker's service role reads or writes; a browser's key sees nothing.
alter table public.events enable row level security;
revoke all on public.events from anon, authenticated;
