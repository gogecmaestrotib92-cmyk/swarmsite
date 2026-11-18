-- Optional, safe to apply at any time (before or after the deploy): the hourly limit of an address and the day's
-- ceiling both count jobs by when they were made, on every POST /jobs. Without this index each count reads the whole
-- table; with few thousand rows that is nothing, with hundreds of thousands it is the slowest part of starting a job.
create index if not exists jobs_created on public.jobs(created_at);
