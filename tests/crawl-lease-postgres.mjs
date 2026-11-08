import assert from 'node:assert/strict';import {execFileSync,spawn} from 'node:child_process';import crypto from 'node:crypto';
const db='swarm_lease_test_'+crypto.randomBytes(4).toString('hex');const run=(...args)=>execFileSync('psql',['-X','-v','ON_ERROR_STOP=1','-d',db,...args],{encoding:'utf8'}).trim();
execFileSync('createdb',[db]);
try {run('-c',`create extension if not exists pgcrypto; create table public.jobs(id uuid primary key, created_at timestamptz default now(), status text not null); create schema storage; create table storage.buckets(id text primary key,name text,public boolean);`);
 run('-f','server/migrations/20261108_durable_crawl.sql');
 run('-c',`insert into jobs(id,status) values ('00000000-0000-0000-0000-000000000001','queued'),('00000000-0000-0000-0000-000000000002','queued');`);
 const q=id=>new Promise((resolve,reject)=>{const p=spawn('psql',['-X','-A','-t','-v','ON_ERROR_STOP=1','-d',db,'-c',`select id from public.claim_swarmsite_job('${id}',120)`]);let out='',err='';p.stdout.on('data',c=>out+=c);p.stderr.on('data',c=>err+=c);p.on('close',code=>code?reject(new Error(err)):resolve(out.trim()));});
 const ownerA='00000000-0000-0000-0000-000000000011',ownerB='00000000-0000-0000-0000-000000000012';const [a,b]=await Promise.all([q(ownerA),q(ownerB)]);assert.ok(a&&b&&a!==b,'concurrent workers claim different jobs');
 assert.equal(await q(ownerB),'','unexpired running jobs cannot be stolen');
 run('-c',`insert into jobs(id,status,retry_after) values ('00000000-0000-0000-0000-000000000003','queued',now()+interval '1 minute')`);
 assert.equal(await q(ownerB),'','backoff keeps a temporary failure out of the ready queue');
 run('-c',`update jobs set retry_after=now()-interval '1 second' where id='00000000-0000-0000-0000-000000000003'`);
 assert.equal(await q(ownerB),'00000000-0000-0000-0000-000000000003','retry becomes claimable when backoff ends');
 run('-c',`update jobs set lease_until=now()-interval '1 second' where id='${a}'`);assert.equal(await q(ownerB),a,'expired job is reclaimed');
 assert.equal(run('-A','-t','-c',`with changed as (update jobs set status='done' where id='${a}' and status='running' and lease_owner='${ownerA}' returning id) select count(*) from changed`),'0','stale worker cannot complete reclaimed job');
 assert.equal(run('-A','-t','-c',`select public from storage.buckets where id='crawl-checkpoints'`),'f','checkpoint bucket is private');
 assert.throws(()=>run('-c',`set role anon; select id from public.claim_swarmsite_job('${ownerB}',120)`),'anonymous callers cannot claim jobs');
 console.log('PostgreSQL lease claims are exclusive, recover expiry, and reject stale owners');
}finally {execFileSync('dropdb',[db]);}
