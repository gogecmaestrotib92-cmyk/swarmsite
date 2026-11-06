-- Swarmsite · Supabase schema (run once in the SQL editor)
create extension if not exists pgcrypto;
create table if not exists jobs (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz default now(),
  url text not null,
  slug text,
  status text not null default 'queued',          -- queued | running | done | failed
  step text,                                       -- current step id
  steps jsonb not null default '[]',               -- [{id,label,status,at,ms,note}]
  options jsonb not null default '{}',             -- {keepFont, world, video}
  result jsonb,                                    -- {previewUrl, beforeUrl, direction, qa}
  error text,
  user_id uuid,
  email text
);
create index if not exists jobs_status_created on jobs(status, created_at);
create index if not exists jobs_user on jobs(user_id);
alter table jobs enable row level security;
-- previews bucket is public; create it in Storage → "previews" (public)
