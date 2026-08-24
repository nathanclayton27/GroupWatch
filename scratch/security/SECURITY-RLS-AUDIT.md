# clubd — RLS and access-control audit (CLU-34)

Hostile audit of the Postgres/PostgREST layer behind clubd.watch, authorised by
the project owner, against his own production project.

**Scope.** Every `.sql` file in the repo root — `schema.sql` and the ten
`migrate-*.sql` files, including `migrate-add-thumbs.sql`, which landed while
this audit was running — plus the query paths in `src/template.html` that show
which of those doors are actually used. Live probing was limited to
unauthenticated `GET` requests with the publishable key that ships in the page
source. No write of any kind was issued, no RPC was called that could write, and
no real user data appears anywhere below: every probe returned zero rows, and
exposure is described as shape, never contents.

**Verdict in one line.** Two critical holes, both of the same kind — an UPDATE
policy that pins the owner column and leaves the columns that decide *who may
read what* wide open. Both are reasoned from policy text, not demonstrated,
because demonstrating them requires a write.

**The single worst thing.** A group's creator can change that group's
`property_id` after people have joined, and immediately read every member's
progress for the property they switched to. It needs no guessing, no leaked
identifier and no cooperation from the victim beyond having joined one group.

Proposed fixes are in `migrate-fix-rls-column-locks.sql`, in this project's
house style: threat first, reasoning next, idempotent, safe to re-run, with the
one part that needs a front-end change fenced off behind a run-order banner.

---

## Findings by severity

### CRITICAL 1 — a group's owner can retarget it at any property and harvest members' progress

**Table.** `groups` · **Policy.** `schema.sql:110`

```sql
create policy "creator updates group" on groups
  for update using (auth.uid() = created_by)
              with check (auth.uid() = created_by);
```

**Attack.** Mallory creates a group for some harmless list, posts the code, and
people join. She then issues one request:

```
PATCH /rest/v1/groups?id=eq.<her group>   {"property_id": "<any slug>"}
```

`property_id` is named by neither clause, so both pass. The membership rows do
not move — everyone who joined is still in the group — but the group now claims
to be about a different list. `shares_group_with(other, prop)` joins through
`groups.property_id`, so from that instant

```
GET /rest/v1/progress?property_id=eq.<the new slug>&select=user_id,read_ids
```

returns every member's progress for a list they never agreed to share. That
includes a password-gated list: the gated slugs are public in the property
manifest, only the contents are encrypted, so Mallory can aim at one by name and
read the tick history of anyone in her group who holds the password — without
holding it herself.

This is precisely the leak `migrate-to-multiproperty.sql` was written to close
("someone in your Fullmetal Alchemist group could read your Secret Wars
progress"). The scoping it added is correct; the value it scopes on is
attacker-controlled.

`code` is open the same way — an invite code already handed out can be silently
re-pointed at a different group, or freed back into the pool. `created_by` is
the one column the `with check` does pin, so ownership cannot be handed off.

**Confirmed?** Statically. Confirming it requires a write, which was out of
bounds; the reasoning is Postgres UPDATE semantics (USING tests the old row,
WITH CHECK the new one, neither restricts columns) applied to the policy text.

**Fix.** A BEFORE UPDATE trigger, the pattern this project already uses for
`tick_events`. Full version in the migration; the load-bearing part:

```sql
create or replace function groups_guard_update()
returns trigger language plpgsql as $$
begin
  if current_user not in ('anon', 'authenticated') then return new; end if;
  if new.property_id is distinct from old.property_id then
    raise exception 'a group cannot change property — make a new group instead';
  end if;
  if new.code is distinct from old.code then
    raise exception 'a join code cannot be changed';
  end if;
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
```

The five columns the app actually writes — `name`, `start_date`, `target_date`,
`schedule_shift_days`, `schedule_start` — are untouched, so nothing in
`saveGroup()` or the post-`create_group()` follow-up writes changes.

---

### CRITICAL 2 — a membership row can walk itself into any group, bypassing the join rate limit and owner removal

**Table.** `group_members` · **Policy.** `schema.sql:120`

```sql
create policy "rename self" on group_members
  for update using (auth.uid() = user_id)
              with check (auth.uid() = user_id);
```

**Attack.** The policy exists so you can change your `display_name`. `group_id`
is named by neither clause:

```
PATCH /rest/v1/group_members?user_id=eq.<me>   {"group_id": "<target group>"}
```

Your membership row relocates. `is_group_member(target)` now answers true, which
hands you the group's row (including its code), its full roster, and — through
`shares_group_with()` — every member's progress for that property.

Three things this defeats at once:

- **`join_group()` and its brand-new rate limit.** No code is presented, so
  `guard_group_join_rate()` never runs. The cap added yesterday in
  `migrate-add-rate-limits.sql` guards a door that has a second door beside it.
- **`owner removes member`.** Removal deletes a row; it cannot forget an id.
  Anyone who was ever in a group knows its UUID — it is written to
  `localStorage` under `GKEY` and returned by every `loadGroups()` roster fetch —
  so a removed member can walk straight back in, repeatedly. Ban is not
  enforceable.
- **The gated-list group.** Everyone who has ever unlocked a password-gated list
  is in its group and holds its id forever.

A row to mutate costs nothing: `create_group()` mints one, is not rate limited,
and has no cap on how many groups one account may create.

The mitigating factor, stated fairly: group ids are `gen_random_uuid()` and the
`groups` select policy requires membership, so ids are not enumerable. The
attack needs an id you already have. Every past member has one.

**Confirmed?** Statically, for the same reason as Critical 1.

**Fix.**

```sql
create or replace function group_members_guard_update()
returns trigger language plpgsql as $$
begin
  if current_user not in ('anon', 'authenticated') then return new; end if;
  if new.group_id is distinct from old.group_id then
    raise exception 'a membership row cannot change groups — join or leave instead';
  end if;
  if new.user_id is distinct from old.user_id then
    raise exception 'a membership row cannot change owner';
  end if;
  if new.joined_at is distinct from old.joined_at then
    raise exception 'joined_at is not editable';
  end if;
  return new;
end $$;

drop trigger if exists group_members_update_guard on group_members;
create trigger group_members_update_guard
  before update on group_members
  for each row execute function group_members_guard_update();
```

`display_name` and `color_index` stay editable, so `wireName()` is unaffected.
The guard steps aside for roles other than `anon`/`authenticated`, so
`join_group()`'s `on conflict do update set display_name` — which runs as the
definer's owner — still works, and the SQL editor can still correct data.

---

### HIGH 3 — `profiles` is a public user directory to anyone with an account

**Table.** `profiles` · **Policy.** `migrate-add-friends.sql:20`

```sql
create policy "profiles readable when signed in" on public.profiles
  for select using (auth.role() = 'authenticated');
```

**Attack.** One request — `GET /rest/v1/profiles?select=user_id,username,fcode`
— returns the whole table to any signed-in person. Two consequences:

- **Friend codes stop being secrets.** The migration's own header justifies the
  open read with "a friend code is a share-secret, useless without being handed
  to you". The policy hands every code to everyone with an account. Combined
  with the fact that `friendships` accepts a unilateral insert of
  `(attacker, victim)` with no cap and no block list, and that a declined
  request can be re-sent immediately, the directory is a spam list with a
  delivery mechanism attached: every user's inbox, on demand, repeatedly.
- **Email local-parts leak.** `mirrorProfile()` writes
  `username: acctName() || (user.email || '').split('@')[0]`, so for every user
  who has not chosen a name, `profiles.username` *is* the local part of their
  email address, paired with a stable `user_id`.

Narrowing the policy is necessary but not sufficient. A friend code is four
characters from a 32-symbol alphabet — 32⁴ = 1,048,576 — and the point lookup
`?fcode=eq.CLB·XXXX` has no rate limit at all. The whole space sweeps in about a
day at ten requests a second, so the lookup has to move behind a function that
counts misses.

**Confirmed?** The anonymous half is confirmed live: an unauthenticated request
returns HTTP 200 with zero rows, so `anon` is correctly excluded. The
authenticated half is static — confirming it needs an account, and creating one
writes a real user into the production auth store.

**Fix.** Part 2 of the migration, which needs a front-end change first (the exact
patch is written into the file). In outline: replace the blanket policy with
own-row plus already-connected-in-either-direction, and route code lookup
through a definer RPC that charges misses against the existing
`rate_limit_guard` / `rate_limit_note` plumbing at 20/hour and 60/day.

```sql
drop policy if exists "profiles readable when signed in" on public.profiles;

create policy "read own profile" on public.profiles
  for select using (auth.uid() = user_id);

create policy "read connected profiles" on public.profiles
  for select using (
    exists (select 1 from public.friendships f
            where (f.a = auth.uid() and f.b = profiles.user_id)
               or (f.b = auth.uid() and f.a = profiles.user_id))
  );
```

`fetchFriendEdges()` needs no change — it looks profiles up by ids that came out
of your own edges, which the second policy covers exactly. Only
`friendByCode()` moves to the RPC.

---

### MEDIUM 4 — the mutual-friends progress policy is not property-scoped

**Table.** `progress` · **Policy.** `migrate-add-friend-shelves.sql:5`

The policy correctly demands **both** directions of the friendship — this is the
one thing the brief flagged as most likely to be wrong, and it is right. A
one-directional "friend" gets nothing.

What it does not do is scope to a property, unlike the group policy sitting
beside it. A mutual friend therefore reads *every* progress row you own,
including the row for a password-gated list. `friendShelves()` filters
`m.secret` in JavaScript — "gated lists are invisible, always" — but the server
has already sent the row, so a raw PostgREST query returns it: confirmation that
you hold the password for a gated list, plus the exact `read_ids` you have
ticked, where the UI only ever shows a count.

Calibrated honestly: the gated property's *slug and title are already public* in
the manifest (only `secret.blob` is encrypted), so this is not a "which list"
leak. It is a "who is in on it, and how far along" leak, plus the raw item ids.
Elsewhere in the repo item ids are opaque ordinals (`columbo-1`), which would
make the id list uninformative — but the gated file's ids live inside the blob
and I could not read them. If that file uses descriptive ids, this becomes a
contents leak and should be re-rated High.

**Confirmed?** Statically.

**Fix.** Give the server a list of gated slugs it can consult, without putting
any slug in the repo. Part 1 §5 of the migration adds `private_properties`
(RLS on, no policies, privileges revoked — the `rate_events` pattern), reads it
through a definer function, and rewrites the policy:

```sql
drop policy if exists "mutual friends read progress" on public.progress;
create policy "mutual friends read progress" on public.progress
  for select using (
    not is_private_property(progress.property_id)
    and exists (select 1 from public.friendships f1
                where f1.a = auth.uid() and f1.b = progress.user_id)
    and exists (select 1 from public.friendships f2
                where f2.a = progress.user_id and f2.b = auth.uid())
  );
```

The table starts empty, which makes the new policy identical to the old one, so
this is inert until the owner inserts a slug by hand in the SQL editor. Group
members stay unaffected — joining a gated list's group requires the password, so
that consent is real.

---

### MEDIUM 5 — `revoke ... from anon` on the RPCs does not do what it reads as doing

**Functions.** `create_group`, `join_group`, `join_or_create_group`,
`new_group_code`

Postgres grants `EXECUTE` on functions in `public` to `PUBLIC` by default, and
Supabase's default privileges add `anon` and `authenticated` on top. Every older
migration says only:

```sql
revoke all on function join_group(text, text) from anon;
grant  execute on function join_group(text, text) to authenticated;
```

That removes the second grant and leaves the first, and `anon` is a member of
`PUBLIC` — so anon has retained EXECUTE on all three join/create RPCs the whole
time. It has not mattered, because each opens with
`if auth.uid() is null then raise exception 'must be signed in…'`. The security
is in the function body; the revoke is decoration.

`migrate-add-rate-limits.sql` gets this exactly right for its own four helpers
and says why in a comment. The older files predate that understanding.

**Confirmed?** Live, by analogy. The three definer helpers that were *never*
revoked — `is_group_member`, `is_group_owner`, `shares_group_with` — answer an
anonymous caller with HTTP 200 and `false`, proving the browser roles reach
definer functions in `public` by default. The join/create RPCs were not called,
because calling them was explicitly out of bounds.

**Fix.** Three-way revoke, in Part 1 §3:

```sql
revoke all on function join_group(text, text) from public, anon;
grant execute on function join_group(text, text) to authenticated;
-- same for create_group and join_or_create_group
revoke all on function new_group_code() from public, anon, authenticated;
```

**Do not extend this to the three policy helpers.** RLS policy expressions are
evaluated with the privileges of the role running the query, so `authenticated`
and `anon` both need EXECUTE on `is_group_member`, `is_group_owner` and
`shares_group_with`, or every select on `groups`, `group_members` and `progress`
fails with "permission denied for function" instead of returning an empty set.
They are safe to leave open: each derives its subject from `auth.uid()` and
accepts no argument that lets a caller ask about anyone but themselves. The
worst they offer an authenticated caller is a self-scoped oracle — "do I share a
group with user X on property P" — which needs a `user_id` they would have to
harvest via finding 3 first.

---

### MEDIUM 6 — `search_path = public` on six definer functions omits `pg_temp`

**Functions.** `is_group_member`, `is_group_owner`, `shares_group_with`,
`new_group_code`, `create_group`, `join_or_create_group` (the schema.sql and
pre-rate-limit versions)

When `pg_temp` is not listed explicitly, Postgres searches the session's
temporary schema **first** for relation names — before `pg_catalog`, before
`public`. Anyone who could get a temp table named `groups` or `group_members`
onto a pooled connection would choose what these definer functions read.

Not exploitable today: nothing in clubd creates temp tables, and there is no RPC
that runs arbitrary SQL. This is the sweep `migrate-add-rate-limits.sql` already
identified ("The rest of the project's functions still say plain `public`;
worth a sweep some day").

**Confirmed?** Statically; it is a property of the function definitions.

**Fix.** Part 1 §6 re-declares the three policy helpers with
`set search_path = public, pg_temp` and unchanged bodies. `create_group` and
`join_or_create_group` were already re-declared with the right `search_path` by
`migrate-add-rate-limits.sql` — only `create_group` still carries the old
setting, and it is re-declared here too.

---

### MEDIUM 7 — no cap on friend requests, group creation, or event volume

- **Friend requests.** `friendships` accepts `(auth.uid(), anyone)` with no
  rate limit, no cap and no block list. A declined request can be re-inserted
  immediately, forever. Amplified to every user at once by finding 3.
- **Group creation.** `create_group()` is not rate limited. Unlimited groups per
  account, each a row in `groups` plus one in `group_members` — and, per
  Critical 2, each a fresh handle for relocating a membership row.
- **`tick_events` and `progress`.** An authenticated user may insert unbounded
  `tick_events` rows for themselves and store an unbounded `read_ids` array. Own
  rows only, so this is storage abuse rather than a breach.

`migrate-add-rate-limits.sql` built exactly the plumbing these need
(`rate_limit_guard` / `rate_limit_note`); it is currently wired to the join path
only. **Not fixed in the migration** — capping writes changes behaviour for real
users and deserves its own card with its own numbers, rather than an audit
picking thresholds unilaterally.

---

### LOW 8 — `anon` holds INSERT/UPDATE/DELETE on every table; RLS is the only guard

A fresh Supabase project grants `anon` and `authenticated` full DML on new
tables in `public`. `rate_events` is the one table where the privileges were
revoked as well as RLS enabled ("Two locks, deliberately") — and that is the one
table live probing found genuinely sealed: HTTP 401, `42501 permission denied for
table rate_events`. Every other table relies on RLS alone, so a single
"disable RLS for a minute to debug" would expose anonymous writes.

Nothing in clubd writes while signed out; every write site in
`src/template.html` returns early when `user` is null. Fixed in Part 1 §4:

```sql
revoke insert, update, delete on table progress      from anon;
-- …tick_events, groups, group_members, profiles, friendships
```

SELECT is deliberately left in place: RLS already returns zero rows to anon
(verified live), and revoking it would turn a query that races the session into
a hard error instead of an empty result.

---

### LOW 9 — nobody can delete their own history

`progress` and `tick_events` have SELECT/INSERT/UPDATE policies and **no DELETE
policy at all**. `b-reset` clears `localStorage` only. There is no server-side
path for a user to erase their reading history, and no account-deletion routine
in any migration. Not an attack — the inverse, an attacker cannot delete either
— but it is a live erasure-request problem for a site with a privacy page.

---

### LOW 10 — friend codes are client-minted, unvalidated and collision-fragile

`newFcode()` draws 4 characters client-side and `mirrorProfile()` upserts them;
the only server-side check is the unique index on `profiles.fcode`. Neither
`fcode` nor `username` has a length limit, a format check or a server-side
generator, so both are arbitrary user-controlled strings of unbounded size that
render in other people's inboxes. (They render *escaped* — `esc()` covers
`& < > "` and every interpolation site uses it — so there is no stored XSS.)

Separately, a 32⁴ space drawn client-side hits a ~50% collision chance somewhere
around 1,200 users by the birthday bound, and a collision surfaces as a `23505`
that sets `FBROKEN = true`, silently disabling the entire friends feature for
that user. Robustness rather than security, but it fails in a way nobody will
report.

---

### INFORMATIONAL — what is right

Worth writing down, because these are the parts a future change must not
regress:

- **`rate_events` is genuinely unreachable.** Live-confirmed: `anon` gets 401 /
  `42501`, and RLS-on-with-zero-policies plus revoked privileges is the correct
  belt-and-braces. The design note about a miss having to return NULL rather
  than raise (because PostgREST rolls the transaction back and the counter never
  moves) is a real insight and correctly implemented.
- **The mutual-friend check requires both directions.** The highest-risk thing
  the brief asked about is correct. A unilateral `(attacker, victim)` row grants
  no reads. RLS on `friendships` does not sabotage the check either: the
  attacker can see both rows the policy needs to test, so it neither
  false-positives nor fails closed.
- **`friendships` cannot be tampered with third-party.** Insert is pinned to
  `auth.uid() = a`; the two delete policies together allow only edges that touch
  you. An edge between two other people is untouchable in both directions.
- **`groups` cannot be enumerated by code.** There is deliberately no
  select-by-code policy, so codes resolve only through `join_group()`, which is
  now rate limited.
- **`tick_events` column guard.** The trigger that limits UPDATE to `kind` is
  exactly the right pattern for "RLS cannot restrict columns" — and is the
  pattern the two criticals above are missing.
- **`progress` writes are correct.** Insert and update both pin
  `auth.uid() = user_id` on both sides, so an upsert against someone else's row
  fails on the insert check and again on the update policy.
- **No secret key anywhere in the tracked tree.** A search for `service_role`,
  `sb_secret_`, `SUPABASE_SERVICE` and JWT-shaped literals across HTML, JS,
  JSON, Python, YAML, Markdown and SQL found nothing outside `scratch/`, which
  was not opened. The key in the page source is the publishable key, which is
  meant to be there.
- **The gated property ships encrypted.** Its file carries only
  `secret.{blob,iv,salt,kdf,iter,v}` with no plaintext `sections`, so the gate
  is not theatre.
- **No schema drift found.** Probing ~20 plausible undocumented table names in
  `public` returned 404 for every one, so the repo's SQL appears to be the whole
  public surface. `thumbs` is the one file written but not yet run — see the
  thumbs review at the end, which is a review of the real policy rather than a
  prediction.

---

## Verdict matrix

Four questions per table. **anon** = unauthenticated holder of the publishable
key. **stranger** = any signed-in account with no relationship to the victim.
**one-way friend** = an attacker who inserted `(attacker, victim)` unilaterally.
**group member** = someone in a group with the victim.

| Table | anon | signed-in stranger | one-way "friend" | group member | Self-grantable? |
|---|---|---|---|---|---|
| `progress` | **nothing** (live: 200, 0 rows). No write — every policy needs `auth.uid()` | own rows only; no read or write of anyone else's | **nothing** — the policy demands both directions ✅ | co-members' rows **for that group's property** — but the property is owner-controlled (**C1**) | membership is (**C2**) |
| `tick_events` | nothing | own rows only | nothing | nothing | n/a |
| `groups` | nothing | nothing — no select policy but membership | nothing | full row incl. code; **creator may rewrite `property_id` / `code` (C1)** | yes, via **C2** |
| `group_members` | nothing | nothing | nothing | full roster (`user_id`, `display_name`, `color_index`) for their groups | **yes — own row's `group_id` is writable (C2)** |
| `profiles` | **nothing** (live-confirmed) | **the entire table (F3)** — every `user_id`, `username`, `fcode` | same | same | n/a |
| `friendships` | nothing | may insert `(self, victim)` — by design; reads/deletes only edges touching self | same | same | n/a — one-way edges grant nothing |
| `rate_events` | **401 permission denied** (live-confirmed) | unreachable — RLS on, zero policies, privileges revoked | unreachable | unreachable | no; counter cannot be read or reset |

### The specific attacks the brief asked about

| Attack | Verdict |
|---|---|
| Read an arbitrary user's `progress` from a known `user_id` | **Blocked** directly. **Works indirectly** via C1 (retarget your group at any property) or C2 (walk into a group whose id you know). |
| Enumerate `profiles` to harvest codes/usernames wholesale | **Works** for any signed-in account (F3). **Blocked** for anon — live-confirmed. |
| Write to or delete another user's `progress` / `tick_events` / `group_members` row | **Blocked.** Writes are pinned both sides. The one exception is a group owner deleting a `group_members` row, which is intended. |
| Forge a `friendships` row in the victim's direction | **Blocked** — insert is pinned to `auth.uid() = a`. Inserting `(attacker, victim)` is allowed and intended, and grants nothing. |
| Delete someone else's friendship | **Blocked** — the two delete policies together cover only edges touching you. |
| Hijack or rename a group you did not create | **Blocked** — `created_by` gates update and cannot be reassigned. |
| Change another member's `display_name` | **Blocked** — `rename self` pins `auth.uid() = user_id`. |
| Read `rate_events` or reset your own counter | **Blocked**, and correctly so — live-confirmed 401. |
| Escalate through a `security definer` function | **Blocked** as to impersonation — every one derives its subject from `auth.uid()` and none takes an argument letting a caller act as someone else. Two weaknesses found: ineffective revokes (F5) and `search_path` missing `pg_temp` (F6). |

---

## What I could not test, and why

An audit that hides its blind spots is worse than useless. These are mine.

1. **No authenticated session was ever created.** Signing up writes a real user
   into the production auth store, so I did not. Every "signed-in stranger",
   "friend" and "group member" verdict above — including both criticals and
   finding 3, i.e. the entire top of this report — is read off the policy text
   and Postgres semantics, **not observed**. Only the `anon` column of the
   matrix is empirically confirmed.

2. **No write was issued, so neither critical is demonstrated.** The claim is
   that a `PATCH` changing `group_members.group_id` or `groups.property_id`
   passes USING and WITH CHECK because neither clause names the column. That
   follows directly from how Postgres evaluates UPDATE under RLS, and from RLS
   having no column granularity — which this repo already knows, since
   `tick_events` carries a trigger for exactly that reason. It is nonetheless
   inference. The cheapest way to settle both is two `PATCH`es from a throwaway
   account against a throwaway group.

3. **`join_group`, `join_or_create_group` and `create_group` were not called.**
   Explicitly out of bounds, and join attempts now spend a real rate-limit
   budget. So finding 5's claim that `revoke … from anon` leaves the PUBLIC
   grant intact is confirmed only for the three helpers that were never revoked
   at all; for the three that were, it is inference from the same privilege
   model.

4. **I read the repo, not the database.** Every verdict assumes the live
   project's policies match the `.sql` files. A policy created, altered or
   dropped by hand in the SQL editor without a matching file is invisible to
   this audit, and `pg_policies` is not reachable through PostgREST. The one
   check I could run — probing ~20 plausible undocumented table names — found
   none, which is weak evidence of no drift, not proof. **Worth running
   `select * from pg_policies where schemaname = 'public'` in the SQL editor and
   diffing it against the files.** That single query would convert most of this
   report from static to confirmed.

5. **The gated property's blob was not decrypted,** so I cannot say whether its
   item ids are opaque ordinals (as everywhere else in the repo) or descriptive.
   That is the difference between finding 4 being Medium and being High.

6. **GoTrue configuration was not verified.** Auth rate limits, the per-address
   cooldown, OTP expiry, redirect-URL wildcards, whether anonymous sign-ins are
   off, whether custom SMTP is configured — all dashboard state, none of it
   reachable from SQL or from an anonymous probe. The runbook at the top of
   `migrate-add-rate-limits.sql` is thorough; **nothing tells me any of it has
   been applied.** Several findings above lean on "an attacker needs an account,
   and accounts cost a confirmed email" — that assumption is only as good as
   those settings.

7. **Out of scope entirely:** Supabase Storage, Realtime (a table exposed to the
   Realtime publication is a second read path with its own RLS evaluation), Edge
   Functions, the `auth` schema, database roles and default privileges as
   actually configured, HTTP security headers, and the static site's own supply
   chain (`supabase.min.js` is loaded from a CDN without SRI).

8. **Load and timing were not examined.** Request volume was kept deliberately
   low, so nothing here says anything about timing side channels or about how
   the policies behave under concurrency.

---

## The thumbs policy — reviewed, not predicted

`migrate-add-thumbs.sql` landed in the repo mid-audit (commit `624e15c`) and has
**not been run against production yet** — a live probe still returns
`PGRST205, could not find the table 'public.thumbs' in the schema cache`. So this
is a review of the real file with time to change it, which is the best possible
moment.

**It gets the hard parts right.** Listing them because they must not regress:

- **Both directions of the friendship are required** for
  `mutual friends read thumbs`. This was the single thing most likely to be
  wrong and it is correct. A unilateral `(attacker, victim)` row grants nothing.
- **There is no friend WRITE policy**, and the file says out loud that there
  never should be.
- **Own rows are pinned on both sides** of the UPDATE policy, so `user_id`
  cannot be reassigned — the row cannot be pushed into someone else's identity.
- **Deny-by-default for anon**: `auth.uid()` is NULL under the publishable key,
  so every policy matches nothing.
- **The counts are not exposed by opening the base table.** Friend pills are
  computed from rows the mutual policy already allows, so there is no
  world-readable "who liked what" surface. This was the trap I most expected and
  it was avoided.
- **The `NULL`-is-distinct trap is handled**: `unique (user_id, property_id,
  coalesce(item_id, ''))` is the right index, and the comment explaining why a
  plain three-column unique would let the whole-list thumb be stored twice is
  correct.

**One real finding, inherited by the copy.** The file says it deliberately copies
the friend-shelves policy "rather than reinvented" — and it copies finding 4
along with it. `mutual friends read thumbs` is **not property-scoped**, so a
mutual friend can read your thumbs on a password-gated list: `item_id` values
that come from inside the encrypted blob, each with an up/down beside it. That is
strictly more than the progress case leaks, because a direction rides along with
every id.

`friendThumbs()` only ever queries the currently-open property, so the UI does
not show this — but the policy is the boundary, and a hostile client simply asks
for a different `property_id`. Fixed in Part 1 §5b of the migration, guarded on
the table existing so the file is runnable in either order:

```sql
drop policy if exists "mutual friends read thumbs" on public.thumbs;
create policy "mutual friends read thumbs" on public.thumbs
  for select using (
    not is_private_property(thumbs.property_id)
    and exists (select 1 from public.friendships f1
                where f1.a = auth.uid() and f1.b = thumbs.user_id)
    and exists (select 1 from public.friendships f2
                where f2.a = thumbs.user_id and f2.b = auth.uid())
  );
```

**Two smaller notes.**

- **No `revoke` on the table**, so `anon` will arrive holding Supabase's default
  INSERT/UPDATE/DELETE and RLS will be the only lock — finding 8, on a table that
  has not shipped yet and could ship correct. Added to §5b:
  `revoke insert, update, delete on table public.thumbs from anon`.
- **`property_id` and `item_id` are free text with no foreign key** (correctly —
  the catalogue is static files). The unique index therefore bounds one opinion
  per *real* thing but bounds nothing at all against invented keys: a client can
  insert unlimited rows with made-up slugs. Same class as finding 7's
  `tick_events` note, and the same answer — the `rate_limit_*` plumbing already
  exists. Not fixed here; it belongs on the same card as the other write caps.

**On the UPDATE policy specifically:** it has the same shape as the two criticals
— `using (auth.uid() = user_id) with check (auth.uid() = user_id)`, leaving
`property_id`, `item_id` and `direction` unpinned — but it is **not** a hole
here, and it would be crying wolf to call it one. Every column on this table is
the caller's own data, and none of them is a key that relocates the row into
someone else's trust domain the way `group_members.group_id` and
`groups.property_id` are. Rewriting your own thumb is what the feature is for.
Worth knowing only that the policy appears unused: the front end deletes and
re-inserts, for the `ON CONFLICT` reason the file explains, so it could be
dropped as unnecessary surface.

**The general rule the criticals teach, for whatever ships next:** a `with check`
that names the owner is not a whole policy. Ask separately whether any *other*
column in the row decides who may read it — a `group_id`, a `property_id`, a
visibility flag. If one does, RLS cannot protect it and it needs a trigger guard,
the way `tick_events` already does.
