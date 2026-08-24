-- clubd — close the column-scoping holes in the RLS policies (CLU-34)
--
-- Run in the Supabase SQL editor. Every step is guarded and safe to re-run.
--
-- ===========================================================================
-- RUN ORDER — PART 1 IS SAFE NOW. PART 2 NEEDS A FRONT-END PATCH FIRST.
-- ===========================================================================
--
-- PART 1 changes nothing any legitimate client does today. It can go in
-- immediately, before or after any deploy.
--
-- PART 2 narrows who may read `profiles`, which BREAKS friend-code lookup
-- until src/template.html calls an RPC instead of querying the table. The
-- exact patch is written out above Part 2. Ship the front end, confirm
-- "add by code" still works, THEN run Part 2. Running it early leaves every
-- user unable to add a friend.
--
-- ===========================================================================
-- THE THREAT — why Part 1 exists
-- ===========================================================================
--
-- Postgres RLS answers "which ROWS may this person touch". It cannot answer
-- "which COLUMNS may they change". Two of this project's UPDATE policies pin
-- only the column that identifies the owner and leave every other column open,
-- including the columns that decide who may read what.
--
--   1. group_members: "rename self" is
--          for update using (auth.uid() = user_id)
--                      with check (auth.uid() = user_id)
--      It was written so you could change your display_name. But group_id is
--      not mentioned by either clause, so
--
--          update group_members set group_id = '<some other group>'
--           where user_id = auth.uid();
--
--      passes both. Your membership row walks into a group you were never
--      invited to. is_group_member() then answers true, which hands you that
--      group's row, its full roster, and — through shares_group_with() —
--      every member's progress for that property.
--
--      That path needs no code, so it goes around join_group() entirely and
--      with it the join rate limit added in migrate-add-rate-limits.sql. It
--      also undoes "owner removes member": anyone who was ever in a group
--      knows its id (it sits in localStorage and in every roster fetch) and
--      can walk back in after being removed, as often as they like. A row to
--      mutate is free — create_group() makes one and is not rate limited.
--
--   2. groups: "creator updates group" is
--          for update using (auth.uid() = created_by)
--                      with check (auth.uid() = created_by)
--      property_id is not mentioned, so a group's creator may retarget their
--      group at ANY property after people have joined it:
--
--          update groups set property_id = '<any slug>' where id = '<mine>';
--
--      shares_group_with(other, prop) joins through groups.property_id, so the
--      moment that column changes, the creator can read every member's
--      progress row for the new property. The member consented to share one
--      list and is now sharing a different one, silently. This re-opens by
--      hand exactly the cross-property leak migrate-to-multiproperty.sql was
--      written to close — the property scoping is correct, but the value it
--      scopes on is attacker-controlled. `code` is open the same way, so an
--      invite code already handed out can be re-pointed after the fact.
--
-- THE FIX. Column guards, enforced by BEFORE UPDATE triggers, which is the
-- pattern this project already uses for tick_events (see
-- migrate-add-tick-events.sql: "Postgres RLS cannot limit columns, so the
-- trigger enforces it"). Triggers rather than column-level GRANTs because a
-- trigger survives Supabase re-applying its default privileges, and because
-- it can say out loud what went wrong instead of failing as a bare permission
-- error. Column grants are a reasonable second lock; they are not added here
-- because a future default-privileges reset would silently restore them and
-- nobody would notice.
--
-- Both guards step aside for roles other than anon and authenticated, so the
-- SQL editor, service_role and any future definer function can still correct
-- data by hand. Browser clients get neither.

-- ===========================================================================
-- PART 1 — safe to run now
-- ===========================================================================

-- ------------------------------------------- 1. membership cannot relocate --

create or replace function group_members_guard_update()
returns trigger language plpgsql as $$
begin
  -- an admin correction from the SQL editor or a definer function is not the
  -- thing this guards against
  if current_user not in ('anon', 'authenticated') then
    return new;
  end if;
  if new.group_id is distinct from old.group_id then
    raise exception 'a membership row cannot change groups — join or leave instead';
  end if;
  if new.user_id is distinct from old.user_id then
    raise exception 'a membership row cannot change owner';
  end if;
  -- joined_at is a fact about the past
  if new.joined_at is distinct from old.joined_at then
    raise exception 'joined_at is not editable';
  end if;
  return new;
end $$;

drop trigger if exists group_members_update_guard on group_members;
create trigger group_members_update_guard
  before update on group_members
  for each row execute function group_members_guard_update();

-- ------------------------------------- 2. a group cannot change what it is --

create or replace function groups_guard_update()
returns trigger language plpgsql as $$
begin
  if current_user not in ('anon', 'authenticated') then
    return new;
  end if;
  -- the column shares_group_with() scopes on. Changing it re-aims every
  -- member's consent at a list they never agreed to share.
  if new.property_id is distinct from old.property_id then
    raise exception 'a group cannot change property — make a new group instead';
  end if;
  -- a code that has been handed out must keep meaning the same group
  if new.code is distinct from old.code then
    raise exception 'a join code cannot be changed';
  end if;
  -- with check already pins this to auth.uid(); saying so here means the rule
  -- does not depend on the policy staying the way it is
  if new.created_by is distinct from old.created_by then
    raise exception 'ownership is not transferable';
  end if;
  if new.id is distinct from old.id or new.created_at is distinct from old.created_at then
    raise exception 'identity columns are not editable';
  end if;
  return new;
end $$;

drop trigger if exists groups_update_guard on groups;
create trigger groups_update_guard
  before update on groups
  for each row execute function groups_guard_update();

-- The columns a group's creator may still change, unchanged from today:
-- name, start_date, target_date, schedule_shift_days, schedule_start. Those
-- are exactly the five src/template.html writes (saveGroup() and the two
-- follow-up writes after create_group()), so nothing in the app moves.

-- ----------------------------------------------- 3. function grant hygiene --

-- Functions in schema public are granted EXECUTE to PUBLIC by Postgres, and
-- Supabase's default privileges grant anon and authenticated on top. Earlier
-- files only ever said `revoke ... from anon`, which removes the second grant
-- and leaves the first — so anon has kept EXECUTE on the join and create RPCs
-- this whole time. It has not mattered, because each of those functions opens
-- with `if auth.uid() is null then raise`, but the revoke does not do what it
-- reads as doing, and the next RPC written to that pattern may not check.
-- migrate-add-rate-limits.sql got this right for its own four helpers; this
-- applies the same three-way revoke to the older ones.

revoke all on function create_group(text, date, text, text) from public, anon;
grant execute on function create_group(text, date, text, text) to authenticated;

revoke all on function join_group(text, text) from public, anon;
grant execute on function join_group(text, text) to authenticated;

revoke all on function join_or_create_group(text, text, text, text) from public, anon;
grant execute on function join_or_create_group(text, text, text, text) to authenticated;

-- only ever called from inside create_group(), which is definer-owned and so
-- runs as the owner; no browser role needs it
revoke all on function new_group_code() from public, anon, authenticated;

-- DELIBERATELY NOT REVOKED: is_group_member, is_group_owner and
-- shares_group_with. RLS policy expressions are evaluated with the privileges
-- of the role running the query, so `authenticated` — and `anon`, whose reads
-- must return an empty set rather than an error — need EXECUTE on all three or
-- every select on groups, group_members and progress fails with "permission
-- denied for function". They are safe to expose: each derives its subject from
-- auth.uid() and takes no argument that lets a caller ask about anyone but
-- themselves.

-- ------------------------------------ 4. anon should not hold write rights --

-- A fresh Supabase project grants anon and authenticated full DML on new
-- tables in public, so RLS is the only thing in front of every table here.
-- Nothing in clubd writes while signed out — every write site in
-- src/template.html returns early when `user` is null — so anon's write
-- privileges are pure surface area. Taking them away means a future "disable
-- RLS for a minute to debug" cannot turn into an anonymous write.
--
-- SELECT is left in place on purpose: RLS already returns zero rows to anon
-- (verified against the live project), and revoking it would turn a query that
-- races the session into a hard error instead of an empty result.

revoke insert, update, delete on table progress      from anon;
revoke insert, update, delete on table tick_events   from anon;
revoke insert, update, delete on table groups        from anon;
revoke insert, update, delete on table group_members from anon;
revoke insert, update, delete on table profiles      from anon;
revoke insert, update, delete on table friendships   from anon;

-- ------------------------- 5. friends must not see a gated list's progress --

-- "mutual friends read progress" is not scoped to a property, unlike the group
-- policy beside it. A mutual friend therefore reads EVERY progress row you
-- own, including the row for a password-gated list. The Friends page hides
-- gated lists in JavaScript ("gated lists are invisible, always") but the
-- server has already sent them, so a raw PostgREST query gets them anyway:
-- confirmation that you hold the password, and the item ids you have ticked.
--
-- The server has no idea which slugs are gated — that lives in the property
-- manifest — so this gives it a list. The table is unreachable from the
-- browser (RLS on, no policies, privileges revoked: the rate_events pattern)
-- and is read only through a definer function, because a policy that selected
-- from it directly would be filtered by its own RLS and fail closed.
--
-- It starts EMPTY, which makes the new policy identical to the old one. To
-- switch a list on, insert its slug in the SQL editor — the slug, nothing
-- else, and no need to name it in this repository:
--
--     insert into private_properties (property_id) values ('<slug>')
--       on conflict do nothing;
--
-- Group members are untouched: joining a gated list's group requires the
-- password, so that consent is real. This only closes the friends path.

create table if not exists public.private_properties (
  property_id text primary key,
  added_at    timestamptz not null default now()
);

alter table public.private_properties enable row level security;
revoke all on table public.private_properties from public, anon, authenticated;

create or replace function is_private_property(prop text)
returns boolean language sql security definer stable
set search_path = public, pg_temp as $$
  select exists (select 1 from private_properties where property_id = prop);
$$;

-- executable by the browser roles for the same reason the other policy
-- helpers are: the policy below is evaluated as the querying role. It answers
-- only "is this slug gated", which the public manifest already says.

drop policy if exists "mutual friends read progress" on public.progress;
create policy "mutual friends read progress" on public.progress
  for select using (
    not is_private_property(progress.property_id)
    and exists (select 1 from public.friendships f1
                where f1.a = auth.uid() and f1.b = progress.user_id)
    and exists (select 1 from public.friendships f2
                where f2.a = progress.user_id and f2.b = auth.uid())
  );

-- ------------------------- 5b. the same scope, for thumbs (CLU-43) --------

-- migrate-add-thumbs.sql copies the friend-shelves policy deliberately
-- ("the same shape as the friend shelves policy (CLU-72), deliberately copied
-- rather than reinvented") — which is the right instinct, and it inherits the
-- missing property scope along with the good parts. A mutual friend can read
-- your thumbs on a gated list: the item ids come from inside the encrypted
-- blob, and each carries an up/down beside it. The front end only ever asks
-- about the open property, but a hostile client asks about any of them.
--
-- Guarded on the table existing, because this file must be runnable whether or
-- not migrate-add-thumbs.sql has gone in yet. If thumbs arrives later, re-run
-- this file — it is idempotent and this block will pick it up.

do $$ begin
  if to_regclass('public.thumbs') is null then
    raise notice 'thumbs does not exist yet — re-run this file after migrate-add-thumbs.sql';
    return;
  end if;

  drop policy if exists "mutual friends read thumbs" on public.thumbs;
  create policy "mutual friends read thumbs" on public.thumbs
    for select using (
      not is_private_property(thumbs.property_id)
      and exists (select 1 from public.friendships f1
                  where f1.a = auth.uid() and f1.b = thumbs.user_id)
      and exists (select 1 from public.friendships f2
                  where f2.a = thumbs.user_id and f2.b = auth.uid())
    );

  -- same reasoning as §4: nothing writes a thumb while signed out
  execute 'revoke insert, update, delete on table public.thumbs from anon';
end $$;

-- ------------------------------------------------- 6. search_path sweep --

-- Every definer function should name pg_temp explicitly. Left off, Postgres
-- searches the caller's temporary schema FIRST for relation names, so anyone
-- who could get a temp table called `groups` or `group_members` onto a pooled
-- connection would choose what these functions read. Nothing in clubd creates
-- temp tables, so this is not a live hole — it is the sweep
-- migrate-add-rate-limits.sql said was worth doing some day. Bodies are
-- unchanged from schema.sql and migrate-to-multiproperty.sql.

create or replace function is_group_member(gid uuid)
returns boolean language sql security definer stable
set search_path = public, pg_temp as $$
  select exists (
    select 1 from group_members
    where group_id = gid and user_id = auth.uid()
  );
$$;

create or replace function is_group_owner(gid uuid)
returns boolean language sql security definer stable
set search_path = public, pg_temp as $$
  select exists (
    select 1 from groups
    where id = gid and created_by = auth.uid()
  );
$$;

create or replace function shares_group_with(other uuid, prop text)
returns boolean language sql security definer stable
set search_path = public, pg_temp as $$
  select exists (
    select 1
    from group_members a
    join group_members b using (group_id)
    join groups g on g.id = a.group_id
    where a.user_id = auth.uid()
      and b.user_id = other
      and g.property_id = prop
  );
$$;

-- ===========================================================================
-- PART 2 — DO NOT RUN UNTIL THE FRONT END IS PATCHED
-- ===========================================================================
--
-- THE THREAT. profiles carries every user's id, username and friend code, and
-- its read policy is
--
--     for select using (auth.role() = 'authenticated')
--
-- — every row, to every signed-in person. One request returns the entire user
-- directory. Two consequences, both live today:
--
--   * A friend code stops being a share-secret. The header of
--     migrate-add-friends.sql justifies the open read with "a friend code is a
--     share-secret, useless without being handed to you" — but the same policy
--     hands out every code to anyone with an account, so the codes are a
--     mailing list and the friend-request inbox is spammable at scale. There
--     is no cap on friendship inserts and no block list, so a declined request
--     can be re-sent immediately, forever.
--   * `username` defaults to the local part of the account's email address
--     (mirrorProfile(): `username: acctName() || user.email.split('@')[0]`),
--     so for anyone who has not chosen a name, this is a dump of email
--     prefixes paired with stable user ids.
--
-- Narrowing the policy alone is not enough. A code is four characters from a
-- 32-symbol alphabet — 32^4 = 1,048,576 — so an uncapped point lookup
-- (`?fcode=eq.CLB·XXXX`) sweeps the whole space in about a day at ten requests
-- a second. The lookup has to move behind a function that counts misses, on
-- the plumbing migrate-add-rate-limits.sql already installed.
--
-- THE CAPS. 20 misses an hour, 60 misses a day, both per user, hits free —
-- the same shape as the join caps and the same reasoning. Someone typing a
-- code off a phone needs one try; sixty misses in a day is far past any real
-- use, and at sixty a day one account expects its first hit on a stranger's
-- code after roughly 48 years.
--
-- THE FRONT-END PATCH, in full. In src/template.html, friendByCode() does:
--
--     const { data, error } = await sb.from('profiles')
--       .select('user_id,username,fcode').eq('fcode', code).maybeSingle();
--
-- replace those two lines with:
--
--     const { data: rows, error } = await sb.rpc('find_profile_by_code',
--                                                { p_code: code });
--     const data = Array.isArray(rows) ? rows[0] : rows;
--
-- Everything below that line already handles `!data` as "No one holds that
-- code", and the rate-limit refusal arrives as an error whose .message is a
-- finished sentence — the existing `if(error)` branch shows a generic string,
-- so worth changing that branch to print error.message when
-- error.hint === 'rate_limited'.
--
-- fetchFriendEdges() needs NO change: it looks up profiles by user_id for ids
-- that came out of your own friendship edges, and the new policy allows
-- exactly those.
--
-- Confirm on the live site that adding a friend by code still works, and only
-- then run what follows.

-- ---------------------------------------------------------------------------
-- Everything from here down is Part 2.
-- ---------------------------------------------------------------------------

-- One row per code, and only when the caller got the code right. Misses are
-- charged; hits are free.
create or replace function find_profile_by_code(p_code text)
returns table (user_id uuid, username text, fcode text)
language plpgsql security definer set search_path = public, pg_temp as $$
declare
  want text := btrim(coalesce(p_code, ''));
  hit  record;
begin
  if auth.uid() is null then
    raise exception 'must be signed in to look up a friend code';
  end if;

  -- before the lookup, so a blocked caller learns nothing about the code
  perform rate_limit_guard(
    'fcode', 20, interval '1 hour',
    'Too many code lookups — wait a while and try again.');
  perform rate_limit_guard(
    'fcode', 60, interval '24 hours',
    'Too many code lookups today — try again tomorrow.');

  select p.user_id, p.username, p.fcode into hit
  from profiles p where p.fcode = want;

  if not found then
    -- NOT `raise`: PostgREST rolls the whole call back when a function
    -- raises, and the miss we just recorded would go with it. Same reasoning
    -- as join_group() returning NULL — see migrate-add-rate-limits.sql.
    perform rate_limit_note('fcode');
    return;
  end if;

  user_id := hit.user_id; username := hit.username; fcode := hit.fcode;
  return next;
end $$;

revoke all on function find_profile_by_code(text) from public, anon;
grant execute on function find_profile_by_code(text) to authenticated;

-- The directory closes. You may read your own row, and the row of anyone an
-- edge already connects you to in either direction — which covers the friends
-- list, the pending-request inbox and the outgoing-request list, because each
-- of those is built from edges that touch you. Everyone else is invisible, and
-- reachable only by holding their code.
drop policy if exists "profiles readable when signed in" on public.profiles;

drop policy if exists "read own profile" on public.profiles;
create policy "read own profile" on public.profiles
  for select using (auth.uid() = user_id);

drop policy if exists "read connected profiles" on public.profiles;
create policy "read connected profiles" on public.profiles
  for select using (
    exists (select 1 from public.friendships f
            where (f.a = auth.uid() and f.b = profiles.user_id)
               or (f.b = auth.uid() and f.a = profiles.user_id))
  );

-- ===========================================================================
-- Check it worked
-- ===========================================================================
--
-- Part 1:
--   select tgname from pg_trigger
--    where tgname in ('groups_update_guard','group_members_update_guard');
--     -- both rows
--
--   -- as a signed-in user in the SQL editor's impersonation mode, or from a
--   -- browser console with a real session, each of these must now fail:
--   --   update group_members set group_id = <another group> where user_id = <you>;
--   --   update groups set property_id = 'anything' where id = <a group you made>;
--   -- and each of these must still succeed:
--   --   update group_members set display_name = 'x' where user_id = <you>;
--   --   update groups set name = 'x' where id = <a group you made>;
--
--   select count(*) from information_schema.role_table_grants
--    where grantee = 'anon' and privilege_type in ('INSERT','UPDATE','DELETE')
--      and table_name in ('progress','tick_events','groups','group_members',
--                         'profiles','friendships');            -- 0
--
--   select count(*) from private_properties;    -- 0 until a slug is inserted
--
-- Part 2:
--   select count(*) from pg_policies
--    where tablename = 'profiles' and cmd = 'SELECT';           -- 2
--   -- and, signed in as one user, a lookup of a stranger's code returns them
--   -- while `select count(*) from profiles` returns only your own row plus
--   -- your connections.
