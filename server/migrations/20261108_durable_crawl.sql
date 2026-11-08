-- Apply before deploying a worker that uses durable crawl checkpoints.
-- The bucket is private: only the service role can read source captures.
alter table public.jobs add column if not exists lease_owner uuid;
alter table public.jobs add column if not exists lease_until timestamptz;
alter table public.jobs add column if not exists retry_count integer not null default 0;
alter table public.jobs add column if not exists retry_after timestamptz;
create index if not exists jobs_lease_expiry on public.jobs(status, lease_until);
insert into storage.buckets (id, name, public)
values ('crawl-checkpoints', 'crawl-checkpoints', false)
on conflict (id) do update set public = false;

-- One atomic claim, including expired leases; never take an unexpired run.
create or replace function public.claim_swarmsite_job(p_worker_id uuid, p_lease_seconds integer default 120)
returns setof public.jobs language sql security definer set search_path = public as $$
  update public.jobs j
     set status = 'running', lease_owner = p_worker_id,
         lease_until = clock_timestamp() + make_interval(secs => greatest(30, least(p_lease_seconds, 600)))
   where j.id = (
     select id from public.jobs
      where (status = 'queued' and (retry_after is null or retry_after <= clock_timestamp()))
         or (status = 'running' and lease_until < clock_timestamp())
      order by created_at for update skip locked limit 1
   ) returning j.*;
$$;
revoke all on function public.claim_swarmsite_job(uuid, integer) from public, anon, authenticated;
grant execute on function public.claim_swarmsite_job(uuid, integer) to service_role;
