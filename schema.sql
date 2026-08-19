-- Everything Dies — database schema
--
-- Run this in the Supabase SQL editor. It is safe to run on a project that
-- already has the original single-reader `progress` table: the first block is
-- skipped if that table exists, and everything after it is additive.
--
-- Groups let several people read the same order and see each other's progress
-- stacked on one strip. That means a group member can read your `progress` row.
-- Nobody outside your groups can, and joining is opt-in per group.

create extension if not exists pgcrypto;

-- ---------------------------------------------------------------- progress --

create table if not exists progress (
  user_id    uuid primary key references auth.users on delete cascade,
  read_ids   text[] not null default '{}',
  updated_at timestamptz default now()
);

alter table progress enable row level security;

do $$ begin
  create policy "read own"   on progress for select using (auth.uid() = user_id);
  create policy "write own"  on progress for insert with check (auth.uid() = user_id);
  create policy "update own" on progress for update using (auth.uid() = user_id)
                                                with check (auth.uid() = user_id);
exception when duplicate_object then null; end $$;

-- ------------------------------------------------------------------ groups --

create table if not exists groups (
  id          uuid primary key default gen_random_uuid(),
  code        text unique not null,
  name        text not null,
  start_date  date not null default current_date,
  target_date date,
  created_by  uuid references auth.users on delete set null,
  created_at  timestamptz default now()
);

create table if not exists group_members (
  group_id     uuid not null references groups on delete cascade,
  user_id      uuid not null references auth.users on delete cascade,
  display_name text not null,
  color_index  int not null default 0,
  joined_at    timestamptz default now(),
  primary key (group_id, user_id)
);

create index if not exists group_members_user_idx on group_members (user_id);

alter table groups        enable row level security;
alter table group_members enable row level security;

-- Membership tests run as the definer so the policies below can ask "is this
-- person in the group?" without the policy on group_members re-triggering
-- itself. A policy that selects from its own table recurses and errors out.

create or replace function is_group_member(gid uuid)
returns boolean language sql security definer stable set search_path = public as $$
  select exists (
    select 1 from group_members
    where group_id = gid and user_id = auth.uid()
  );
$$;

create or replace function shares_group_with(other uuid)
returns boolean language sql security definer stable set search_path = public as $$
  select exists (
    select 1
    from group_members a
    join group_members b using (group_id)
    where a.user_id = auth.uid() and b.user_id = other
  );
$$;

-- Policies. Note there is deliberately no plain select policy on `groups` by
-- code: a code you have not joined with is not readable, so the table cannot be
-- enumerated by guessing codes. Joining goes through join_group() below.

do $$ begin
  create policy "members read group" on groups
    for select using (is_group_member(id));

  create policy "creator updates group" on groups
    for update using (auth.uid() = created_by)
                with check (auth.uid() = created_by);

  create policy "creator deletes group" on groups
    for delete using (auth.uid() = created_by);

  create policy "members read roster" on group_members
    for select using (is_group_member(group_id));

  create policy "rename self" on group_members
    for update using (auth.uid() = user_id)
                with check (auth.uid() = user_id);

  create policy "leave group" on group_members
    for delete using (auth.uid() = user_id);

  -- the one privacy change: co-members can read each other's ticks
  create policy "read group progress" on progress
    for select using (shares_group_with(user_id));
exception when duplicate_object then null; end $$;

-- ------------------------------------------------------------------- rpcs --

-- Codes skip 0/O/1/I so they survive being read aloud or typed from a photo.
create or replace function new_group_code()
returns text language plpgsql security definer set search_path = public as $$
declare
  alphabet text := 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  c text;
  i int;
begin
  loop
    c := '';
    for i in 1..6 loop
      c := c || substr(alphabet, 1 + floor(random() * length(alphabet))::int, 1);
    end loop;
    exit when not exists (select 1 from groups where code = c);
  end loop;
  return c;
end $$;

create or replace function create_group(
  p_name text, p_target date, p_display_name text
) returns groups language plpgsql security definer set search_path = public as $$
declare g groups;
begin
  if auth.uid() is null then
    raise exception 'must be signed in to create a group';
  end if;

  insert into groups (code, name, target_date, created_by)
  values (
    new_group_code(),
    coalesce(nullif(btrim(p_name), ''), 'Reading group'),
    p_target,
    auth.uid()
  )
  returning * into g;

  insert into group_members (group_id, user_id, display_name, color_index)
  values (g.id, auth.uid(), coalesce(nullif(btrim(p_display_name), ''), 'Reader'), 0);

  return g;
end $$;

create or replace function join_group(
  p_code text, p_display_name text
) returns groups language plpgsql security definer set search_path = public as $$
declare
  g groups;
  taken int;
begin
  if auth.uid() is null then
    raise exception 'must be signed in to join a group';
  end if;

  select * into g from groups where code = upper(btrim(p_code));
  if not found then
    raise exception 'no group with that code';
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

revoke all on function create_group(text, date, text) from anon;
revoke all on function join_group(text, text)         from anon;
grant execute on function create_group(text, date, text) to authenticated;
grant execute on function join_group(text, text)         to authenticated;
