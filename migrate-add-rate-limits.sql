-- clubd — cap brute-force attempts on the group-join path (CLU-35)
--
-- Run ONCE in the Supabase SQL editor. Additive and safe to re-run.
--
-- ===========================================================================
-- RUN ORDER — READ THIS FIRST. THE FRONT END GOES OUT BEFORE THE SQL.
-- ===========================================================================
--
-- This migration changes ONE contract: join_group() no longer raises "no group
-- with that code" for a code that does not exist. It records the miss and
-- returns NULL instead. Why it has to is explained under "Why a miss returns
-- NULL" below — the short version is that a function that raises cannot count
-- anything, because the raise rolls its own bookkeeping back.
--
-- The front end has to learn to read a NULL result as "no such code" BEFORE
-- this runs, in two places in src/template.html:
--
--   1. the $('b-gjoin').onclick handler (the "join by code" box), and
--   2. joinSecretGroup(), whose fallback chain tries join_group() first and
--      only reaches join_or_create_group() when the first call FAILS.
--
-- (2) is the one that actually breaks: if join_group() returns NULL quietly,
-- the chain stops there and the first person through a password-gated list
-- never creates its group. Deploy the front-end patch, confirm a wrong code
-- still says "No group has that code", THEN run this file.
--
-- Everything else here is inert until someone abuses the join box, and the
-- cap itself (the raise) works with any front end — a raised error already
-- reaches error.message, which is exactly what the existing handler shows.
--
-- The patch, both sites, in full:
--
--   1) $('b-gjoin').onclick — after `const joined = ...`, insert:
--
--        if(!joined){ flash('No group has that code.','gmsg'); return; }
--
--      Its existing `if(error)` branch already prints error.message for
--      anything that is not /no group/i, so the cap's sentence shows as-is.
--      Optional polish: branch on error.hint === 'rate_limited' to disable the
--      button for a minute instead of only flashing.
--
--   2) joinSecretGroup() — the loop currently treats "no error" as success:
--
--        const { error } = await sb.rpc(fn, args);
--        if(!error){ ...success... }
--
--      it needs the data too, so a NULL result falls through to the next
--      attempt instead of ending the chain:
--
--        const { data, error } = await sb.rpc(fn, args);
--        if(!error && data){ ...success... }
--        last = error || { message: 'no group with that code' };
--
-- ===========================================================================
-- RUNBOOK — the half a migration cannot do: GoTrue's auth rate limits
-- ===========================================================================
--
-- CLU-35 also covers "magic-link requests per address". None of that lives in
-- Postgres. GoTrue's limits are project settings, so they are dashboard
-- clicks, and nothing below can be set from SQL. Labels move between dashboard
-- releases — where a label is worth double-checking it is marked VERIFY THE
-- LABEL, meaning: the setting exists, but the exact wording may have changed.
--
-- A. Authentication -> Rate Limits
--    Dashboard -> your project -> Authentication (left nav) -> Rate Limits.
--    (VERIFY THE LABEL: on some releases this page sits under
--    Authentication -> Configuration -> Rate Limits, or under Project
--    Settings -> Auth. Same fields either way.)
--
--    - "Rate limit for sending emails"  (per hour, project-wide)
--      Recommend 30/hour once custom SMTP is configured.
--      Trade-off: this is a project-wide ceiling, not per address — set it too
--      low and a burst of genuine sign-ins on a busy evening starts bouncing
--      for everyone, and the person who got refused has no way to tell.
--      NOTE: Supabase's built-in email sender is throttled to a couple of
--      messages an hour and is explicitly not for production. If clubd is
--      still on it, raising this number changes nothing — the fix is custom
--      SMTP (Resend, SES, Postmark), not this field.
--
--    - "Rate limit for token verifications" (per 5 minutes, per IP)
--      Default 30. This is the one that caps magic-link/OTP redemption
--      guessing. Leave at 30, or 15 if you ever see abuse.
--      Trade-off: it counts per IP, so an office, a school or a phone carrier
--      NAT shares one budget — going much below 15 starts locking out
--      innocent people who happen to share an exit address.
--
--    - "Rate limit for sign ups and sign ins" (per 5 minutes, per IP)
--      Default 30. Recommend 10 for a project this size.
--      Trade-off: same shared-IP caveat; 10 is still ~3 magic links a minute
--      from one address, far above what a real person needs.
--
--    - "Rate limit for token refreshes" (per 5 minutes, per IP)
--      Default 150. Leave alone. Refreshes are automatic and bursty; capping
--      them logs real users out mid-session for no security gain.
--
--    - "Rate limit for anonymous users" (per hour, per IP)
--      Only matters if anonymous sign-ins are enabled. clubd does not use
--      them — confirm the provider is OFF (section C) and this is moot.
--
-- B. The per-address cooldown (the actual answer to "per address")
--    Authentication -> Sign In / Providers -> Email  (VERIFY THE LABEL: older
--    dashboards call this Authentication -> Providers -> Email; the setting
--    has also appeared on Authentication -> Emails -> SMTP Settings).
--    Field: "Minimum interval between emails being sent"  (GOTRUE_SMTP_MAX_
--    FREQUENCY), default 60 seconds.
--    Recommend keeping 60s. This is the only GoTrue limit keyed to the ADDRESS
--    rather than the IP: one magic link per minute per email, full stop.
--    Trade-off: raise it to 120s+ and the common real-world case — someone
--    mistypes their address, fixes it, and asks again — makes them sit and
--    wait, which reads as the site being broken.
--
--    While on that page: "Email OTP Expiration" (VERIFY THE LABEL) should be
--    3600 seconds or less. Supabase's own security advisor flags anything over
--    an hour. Shorter is safer; below ~15 minutes and links start expiring
--    before people finish switching to their mail app.
--
-- C. Confirm the shape of the auth surface
--    Authentication -> Sign In / Providers: only Email (magic link) and Google
--    should be enabled. Anonymous sign-ins OFF. Every provider left on is a
--    door with its own rate limits.
--
-- D. Authentication -> URL Configuration
--    Keep "Redirect URLs" to the exact origins clubd runs on (the live domain
--    and, if you need it, one localhost entry). Wildcards here let someone
--    aim a genuine magic link at a site they control.
--    Trade-off: too strict and a preview deploy silently fails to sign in.
--
-- E. CAPTCHA — the strongest control for magic-link spam, and the most
--    intrusive. Authentication -> Settings -> "Enable Captcha protection"
--    (VERIFY THE LABEL; the provider list is hCaptcha and Cloudflare
--    Turnstile). Turnstile is close to invisible for real users.
--    Trade-off: it needs a front-end change to attach the token to the
--    sign-in call, so it is not a dashboard-only fix. Worth turning on only
--    if email abuse actually shows up; the per-address cooldown in B plus the
--    per-IP caps in A cover the normal case.
--
-- ===========================================================================
-- The SQL half: what this does and why these numbers
-- ===========================================================================
--
-- THE THREAT. A join code is six characters from a 32-symbol alphabet
-- (0/O/1/I removed) = 32^6 = 1,073,741,824 codes. Guessing one is silly, but
-- "silly" is not "impossible", and the payoff is real: a correct guess joins
-- you to a group, and group membership is what lets you read other members'
-- progress rows for that property. So cap the grinding.
--
-- THE CAPS. Two tiers, both counted per user, both counting only attempts
-- that did NOT find a group:
--
--   10 misses per 15 minutes   — the burst cap. Stops a script cold.
--   40 misses per 24 hours     — the sustained cap. Stops a patient script.
--
-- Why those numbers. A person typing a code off a phone screen needs one or
-- two tries; ten in a quarter of an hour is already far past frustrated, and
-- correct codes cost nothing at all — only misses are recorded, so someone who
-- joins ten groups in a row never touches the counter. On the other side, 40
-- guesses a day against 1.07e9 codes means a single account expects its first
-- hit after roughly 73,000 years, and every guess costs a confirmed email
-- address because join_group() refuses anonymous callers. An attacker who
-- automates account creation to widen that is fighting GoTrue's per-IP sign-up
-- limits (section A) as well: even a thousand throwaway accounts each spending
-- their full daily budget is 40,000 guesses a day, which is still ~73 years
-- for one expected hit. The cap is not the only thing standing in the way; it
-- just removes the "leave it running for a year" option.
--
-- WHY A MISS RETURNS NULL. PostgREST runs every RPC in one transaction and
-- rolls it back when the function raises. So a function that records a failed
-- attempt and then raises records nothing at all — the INSERT dies with the
-- transaction, the counter never moves, and the cap never fires. That is
-- security theatre, and it is not obvious from reading the code, which is why
-- it is written down here. The only outcomes that can be counted are the ones
-- whose transaction COMMITS. So:
--
--   join_group() with an unknown code   -> record the miss, return NULL.
--   join_or_create_group() with an
--     unknown code                      -> it CREATES the group, which already
--                                          commits, so the miss is recorded on
--                                          the way through and nothing about
--                                          its contract changes.
--   cap exceeded                        -> raise. Nothing needs recording on
--                                          this path, so the rollback costs
--                                          nothing, and the front end gets a
--                                          real error to show.
--
-- The one outcome left uncounted is join_or_create_group()'s "that code
-- belongs to a different property", which still raises. Reaching it requires
-- guessing a code that genuinely exists — the thing the caps are there to
-- prevent — so a guesser who lands on it has already spent their budget on the
-- ~1.07e9 misses it took to get there.
--
-- ERROR SHAPE. The cap raises with SQLSTATE PT429, which PostgREST maps to
-- HTTP 429, and with a message written for a human to read verbatim:
-- "Too many attempts — wait a minute and try again." The hint is the stable
-- machine-readable half ('rate_limited'), so the front end can branch on
-- error.hint or error.code instead of matching on prose.
--
-- CLEANUP. Every recorded miss also deletes that user's rows older than 24
-- hours — index-driven, a handful of rows, paid for by the abuser rather than
-- by a background job. That alone bounds an active user, but it never runs for
-- someone who stops attempting, so their last few rows would sit forever.
-- prune_rate_events() sweeps those; schedule it daily if pg_cron is enabled
-- (one-liner at the bottom of this file), or run it by hand now and then. The
-- table is small either way: it only ever holds failed join attempts from the
-- last day.

-- --------------------------------------------------------------- the table --

create table if not exists rate_events (
  user_id uuid        not null references auth.users (id) on delete cascade,
  kind    text        not null,
  at      timestamptz not null default now()
);

-- the only question ever asked of this table: "how many of THIS user's THIS
-- kind of attempts landed since T?" — so the index answers it end to end and
-- the count never touches the heap for other users.
create index if not exists rate_events_user_kind_at
  on rate_events (user_id, kind, at desc);

-- the sweep asks a different question: "everything older than T, whoever it
-- belongs to?"
create index if not exists rate_events_at_idx
  on rate_events (at);

alter table rate_events enable row level security;

-- Two locks, deliberately. RLS is on and NO policy is ever created for this
-- table, so every direct select/insert/update/delete by anon or authenticated
-- finds zero rows and refuses every write — a user can neither read their own
-- attempt history nor forge a clean one. The security definer functions below
-- run as this table's owner and bypass RLS, which is the only way in.
--
-- The revokes are not belt-and-braces padding: a fresh Supabase project ships
-- ALTER DEFAULT PRIVILEGES granting anon and authenticated full access to new
-- tables in public, so this table arrives world-writable-ish and RLS is the
-- only thing standing in front of it. Take the privileges away too, so a
-- future "disable RLS for a minute to debug" cannot quietly expose it.
revoke all on table rate_events from public;
revoke all on table rate_events from anon;
revoke all on table rate_events from authenticated;

-- ------------------------------------------------------------- the helpers --

-- Every function below sets `search_path = public, pg_temp`, including the two
-- join functions further down. Naming pg_temp explicitly puts it LAST; left
-- off, Postgres searches the caller's temporary schema FIRST for relation and
-- type names, so anyone who could get a temp table called `rate_events` or
-- `groups` created on a pooled connection would choose what these security
-- definer functions read. Nothing in clubd can create one today — there is no
-- RPC that makes temp tables — so this is not a live hole, it is closing the
-- door while it is already open. (Function names are never resolved through
-- pg_temp, so only the table lookups were ever exposed.) The rest of the
-- project's functions still say plain `public`; worth a sweep some day.

-- Raises when this user is over p_max attempts of p_kind inside p_window.
-- Returns quietly otherwise. Never writes.
create or replace function rate_limit_guard(
  p_kind text, p_max integer, p_window interval, p_message text
) returns void language plpgsql security definer set search_path = public, pg_temp as $$
declare
  uid uuid := auth.uid();
  n   integer;
begin
  if uid is null then
    return;                      -- callers check auth themselves; nothing to count
  end if;

  select count(*) into n
  from rate_events
  where user_id = uid
    and kind    = p_kind
    and at      > now() - p_window;

  if n >= p_max then
    -- PT429 is PostgREST's "use this HTTP status" convention: the client gets
    -- 429, error.message is the sentence below, error.hint is the stable tag.
    raise exception using
      errcode = 'PT429',
      message = p_message,
      hint    = 'rate_limited';
  end if;
end $$;

-- Records one attempt and pays the cleanup cost for its own user.
create or replace function rate_limit_note(p_kind text)
returns void language plpgsql security definer set search_path = public, pg_temp as $$
declare uid uuid := auth.uid();
begin
  if uid is null then
    return;
  end if;

  insert into rate_events (user_id, kind) values (uid, p_kind);

  -- 24 hours is the longest window any cap uses, so anything older can never
  -- affect a decision. Scoped to this user: bounded work on an indexed prefix.
  delete from rate_events
  where user_id = uid
    and at < now() - interval '24 hours';
end $$;

-- The caps for the group-join path, in one place so both entry points cannot
-- drift apart. Numbers justified in the header.
create or replace function guard_group_join_rate()
returns void language plpgsql security definer set search_path = public, pg_temp as $$
begin
  perform rate_limit_guard(
    'join', 10, interval '15 minutes',
    'Too many attempts — wait a minute and try again.');
  perform rate_limit_guard(
    'join', 40, interval '24 hours',
    'Too many join attempts today — try again tomorrow.');
end $$;

-- Housekeeping for users who stopped attempting and so never pay the
-- per-write cleanup again. Returns how many rows it removed.
create or replace function prune_rate_events()
returns integer language plpgsql security definer set search_path = public, pg_temp as $$
declare n integer;
begin
  delete from rate_events where at < now() - interval '24 hours';
  get diagnostics n = row_count;
  return n;
end $$;

-- None of the four are callable from the browser. They are plumbing for the
-- join functions, and a user who could call rate_limit_note() directly could
-- fill their own budget to lock themselves out, or worse, call it for a
-- pattern of kinds nobody audits. Functions in public are granted to PUBLIC by
-- default, and Supabase's default privileges add anon/authenticated on top, so
-- all three have to come off explicitly.
revoke all on function rate_limit_guard(text, integer, interval, text) from public;
revoke all on function rate_limit_guard(text, integer, interval, text) from anon;
revoke all on function rate_limit_guard(text, integer, interval, text) from authenticated;

revoke all on function rate_limit_note(text) from public;
revoke all on function rate_limit_note(text) from anon;
revoke all on function rate_limit_note(text) from authenticated;

revoke all on function guard_group_join_rate() from public;
revoke all on function guard_group_join_rate() from anon;
revoke all on function guard_group_join_rate() from authenticated;

revoke all on function prune_rate_events() from public;
revoke all on function prune_rate_events() from anon;
revoke all on function prune_rate_events() from authenticated;

-- ------------------------------------------------------- the join path --

-- Unchanged from schema.sql except for the two rate-limit lines and the miss
-- returning NULL instead of raising. Same signature and same return type, so
-- this is a genuine CREATE OR REPLACE: existing grants survive and re-running
-- the file is a no-op.
create or replace function join_group(
  p_code text, p_display_name text
) returns groups language plpgsql security definer set search_path = public, pg_temp as $$
declare
  g     groups;
  taken int;
  want  text := upper(btrim(coalesce(p_code, '')));
begin
  if auth.uid() is null then
    raise exception 'must be signed in to join a group';
  end if;

  -- before the lookup, so a blocked caller learns nothing about the code
  perform guard_group_join_rate();

  -- A code that cannot exist is still a guess. Charging it keeps the
  -- accounting honest and costs a real person nothing: the join box already
  -- refuses anything that is not six characters before it gets here.
  if want !~ '^[A-HJ-NP-Z2-9]{6}$' then
    perform rate_limit_note('join');
    return null;
  end if;

  select * into g from groups where code = want;
  if not found then
    perform rate_limit_note('join');
    -- NOT `raise`. See "Why a miss returns NULL" in the header: raising here
    -- would roll the line above back and the cap would never fire.
    return null;
  end if;

  select count(*) into taken from group_members where group_id = g.id;

  insert into group_members (group_id, user_id, display_name, color_index)
  values (g.id, auth.uid(),
          coalesce(nullif(btrim(p_display_name), ''), 'Reader'),
          taken)
  on conflict (group_id, user_id)
    do update set display_name = excluded.display_name;

  return g;
end $$;

-- Unchanged from migrate-add-join-or-create.sql except for the two rate-limit
-- lines. Its contract does not move at all: the create path already commits,
-- so the attempt can be recorded on the way through.
create or replace function join_or_create_group(
  p_code text, p_name text, p_property_id text, p_display_name text
) returns groups language plpgsql security definer set search_path = public, pg_temp as $$
declare
  g     groups;
  taken int;
  want  text := upper(btrim(coalesce(p_code, '')));
begin
  if auth.uid() is null then
    raise exception 'must be signed in to join a group';
  end if;

  perform guard_group_join_rate();

  if want !~ '^[A-HJ-NP-Z2-9]{6}$' then
    raise exception 'a join code is six characters from the code alphabet';
  end if;
  if coalesce(btrim(p_property_id), '') = '' then
    raise exception 'a group needs a property';
  end if;

  select * into g from groups where code = want;

  if not found then
    -- The code did not resolve. This function's answer to that is to create
    -- the group rather than fail, which is the whole point of it — but from
    -- the code space's point of view it is still a miss, and unlike
    -- join_group()'s miss this transaction commits, so the record sticks.
    -- Grinding this function is the cheaper attack of the two (every guess
    -- "succeeds" and leaves a junk group behind), and this is what stops it.
    perform rate_limit_note('join');

    insert into groups (code, name, property_id, created_by)
    values (want,
            coalesce(nullif(btrim(p_name), ''), 'Reading group'),
            p_property_id,
            auth.uid())
    returning * into g;
  elsif g.property_id is distinct from p_property_id then
    -- the same code cannot mean two different lists, or joining one would
    -- quietly hand out read access to progress on the other
    raise exception 'that code belongs to a different property';
  end if;

  select count(*) into taken from group_members where group_id = g.id;

  insert into group_members (group_id, user_id, display_name, color_index)
  values (g.id, auth.uid(),
          coalesce(nullif(btrim(p_display_name), ''), 'Reader'),
          taken)
  on conflict (group_id, user_id) do nothing;

  return g;
end $$;

-- Re-stated rather than assumed. CREATE OR REPLACE preserves the grants that
-- schema.sql and migrate-add-join-or-create.sql set, but a fresh database that
-- ran this file early would not have them, and a function in public is
-- executable by PUBLIC until told otherwise.
revoke all on function join_group(text, text) from anon;
revoke all on function join_or_create_group(text, text, text, text) from anon;
grant execute on function join_group(text, text) to authenticated;
grant execute on function join_or_create_group(text, text, text, text) to authenticated;

-- ------------------------------------------------------------ housekeeping --

-- Optional. If pg_cron is enabled on this project (Database -> Extensions ->
-- pg_cron), this sweeps the leftovers of users who stopped attempting. Safe to
-- skip entirely — the per-write cleanup already bounds anyone still active.
--
--   create extension if not exists pg_cron;
--   select cron.schedule('prune-rate-events', '17 4 * * *',
--                        $$select prune_rate_events()$$);
--
-- Undo with:  select cron.unschedule('prune-rate-events');

-- Check it worked:
--   select count(*) from rate_events;                  -- 0 on a fresh install
--   select relrowsecurity from pg_class
--    where relname = 'rate_events';                    -- t
--   select count(*) from pg_policies
--    where tablename = 'rate_events';                  -- 0, and that is correct
--
-- The full proof, including making the cap actually fire, is in
-- scratch/qa2/ratelimit_notes.md.
