-- Friends foundation (CLU-69): run once in the Supabase SQL editor.
--
-- profiles is the public half of the handshake: it maps a friend code to
-- its owner so a typed or linked code can find them, and carries the
-- display username. Each user maintains only their own row; every signed
-- in user may read the table (a friend code is a share-secret, useless
-- without being handed to you).
create table if not exists public.profiles (
  user_id    uuid primary key references auth.users(id) on delete cascade,
  fcode      text unique,
  username   text,
  updated_at timestamptz not null default now()
);
alter table public.profiles enable row level security;

create policy "insert own profile" on public.profiles
  for insert with check (auth.uid() = user_id);
create policy "update own profile" on public.profiles
  for update using (auth.uid() = user_id);
create policy "profiles readable when signed in" on public.profiles
  for select using (auth.role() = 'authenticated');

-- friendships: one row per DIRECTION. A friendship is live when both
-- directions exist — mutual by construction, no request inbox. You may
-- only ever write or remove your own direction.
create table if not exists public.friendships (
  a          uuid not null references auth.users(id) on delete cascade,
  b          uuid not null references auth.users(id) on delete cascade,
  created_at timestamptz not null default now(),
  primary key (a, b),
  check (a <> b)
);
alter table public.friendships enable row level security;

create policy "add own direction" on public.friendships
  for insert with check (auth.uid() = a);
create policy "see edges touching you" on public.friendships
  for select using (auth.uid() = a or auth.uid() = b);
create policy "remove own direction" on public.friendships
  for delete using (auth.uid() = a);
