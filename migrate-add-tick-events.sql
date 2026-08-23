-- Tick events: the when and the kind behind every tick.
-- Run once on an existing database; safe to run twice.
--
-- The progress table stays the source of truth for WHAT is ticked; this
-- table records WHEN each tick happened and whether it was live watching
-- or catching up on history. Stats (streaks, heatmaps, hours-this-month)
-- read only kind='live'; imports and mark-all write kind='backfill'.
-- kind is updatable so the activity page can reclassify after the fact —
-- which is the whole design: capture now, classify later. History that
-- was never captured can never be reconstructed, so this migration ships
-- before any stats UI exists.

create table if not exists tick_events (
  id          bigint generated always as identity primary key,
  user_id     uuid not null references auth.users (id) on delete cascade,
  property_id text not null,
  item_id     text not null,
  action      text not null default 'tick'
              check (action in ('tick', 'untick')),
  kind        text not null default 'live'
              check (kind in ('live', 'backfill')),
  at          timestamptz not null default now()
);

-- the queries that matter: "my events on this property, in order" and
-- "my events this month, newest first"
create index if not exists tick_events_user_prop_at
  on tick_events (user_id, property_id, at desc);
create index if not exists tick_events_user_at
  on tick_events (user_id, at desc);

alter table tick_events enable row level security;

-- Own rows only, for now. Friend visibility arrives with the friends
-- feature and will be a new policy through a security-definer check,
-- like the group policies — never by widening these.
drop policy if exists "insert own tick events" on tick_events;
create policy "insert own tick events" on tick_events
  for insert with check (auth.uid() = user_id);

drop policy if exists "read own tick events" on tick_events;
create policy "read own tick events" on tick_events
  for select using (auth.uid() = user_id);

-- reclassification: the activity page may flip kind (and nothing else).
-- Postgres RLS cannot limit columns, so the trigger enforces it.
drop policy if exists "reclassify own tick events" on tick_events;
create policy "reclassify own tick events" on tick_events
  for update using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

create or replace function tick_events_guard_update()
returns trigger language plpgsql as $$
begin
  if new.user_id      is distinct from old.user_id
     or new.property_id is distinct from old.property_id
     or new.item_id     is distinct from old.item_id
     or new.action      is distinct from old.action
     or new.at          is distinct from old.at then
    raise exception 'only kind may be reclassified';
  end if;
  return new;
end $$;

drop trigger if exists tick_events_update_guard on tick_events;
create trigger tick_events_update_guard
  before update on tick_events
  for each row execute function tick_events_guard_update();
