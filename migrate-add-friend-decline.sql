-- Friend request inbox (decline support): run once in the Supabase SQL
-- editor. Declining an incoming request deletes the OTHER person's
-- direction — an edge pointing at you — which the original policy
-- (delete only your own direction) did not allow.
create policy "decline an incoming direction" on public.friendships
  for delete using (auth.uid() = b);
