# How it works

Everything is one file: `index.html`. No build step, no dependencies to install, no framework. Roughly 250 lines of CSS, 60 lines of markup, 180 lines of JavaScript, and a data array.

This document explains the parts you'd need to understand to change it.

---

## The shape of the thing

```
index.html
├── <style>          design tokens + layout, ~250 lines
├── <body>           static shell: header, sticky bar, empty <main>, panels
└── <script>
    ├── config       SUPABASE_URL, SUPABASE_ANON_KEY, ENABLE_GITHUB_LOGIN
    ├── DATA         the reading order (generated, ~250 items)
    ├── storage      readLocal / writeLocal / pushCloud / persist
    ├── auth         adopt / onSession
    ├── render       build() once, paint() on every change
    └── boot
```

The only runtime dependency is the Supabase client from jsDelivr, and it's only used when you've filled in the config. With the config empty the page still works — `CLOUD` evaluates false and everything falls back to `localStorage`.

---

## The data model

`DATA` is an array of sections:

```js
{
  id: "weave",
  tier: 2,
  title: "The alternating weave",
  sub: "F4 #600–611 × FF #12–23 · order specified by Hickman",
  series: "https://www.marvel.com/comics/series/...",   // optional
  items: [ ... ]
}
```

And each item:

| Field  | Meaning |
|--------|---------|
| `id`   | stable key, e.g. `fantastic-four-604` — **see below** |
| `t`    | title, e.g. `Fantastic Four` |
| `n`    | issue number, e.g. `#604` |
| `note` | one-line annotation, shown under the title |
| `star` | 0, 1, or 2 — renders as ★ or ★★ |
| `opt`  | 1 shows an "optional" pill |
| `url`  | direct Marvel link, where one exists |

Tiers are per-section, not per-item, because skippability in this run is a property of whole runs rather than individual issues.

### Why the IDs are strings

Progress is stored as a list of item IDs. The first version used **array positions** — ticking *Avengers* #35 saved the number `183`.

That works until the list changes. Insert one issue near the front and every position after it shifts by one, so everybody's saved progress silently points at the wrong comics. Nothing errors; the data just quietly becomes wrong. That's the worst kind of bug.

So IDs are now slugs derived from the title and issue number:

```
fantastic-four-604
new-avengers-16
secret-wars-9
```

Now you can insert, delete and reorder freely. A saved ID either matches an item or it doesn't, and `clean()` drops the ones that don't.

Keys are generated from `t` and `n`, so changing either **breaks saved progress for that issue**. If you rename `Fantastic Four` to `Fantastic Four (1998)`, every one of those IDs changes. Either accept the loss or add an explicit `id` override on the item.

### Migration from the old format

`migrate()` runs once at boot. If it finds v1 positional data and no v2 data, it maps the old integers through `ORDER` (the flattened item list) and writes v2. The old key is left alone as a fallback.

That mapping is only correct because the list hasn't changed since v1. It's a one-shot fix, not a general mechanism — after this, positional data can't be interpreted.

The import box accepts both formats for the same reason: an all-integer array is treated as legacy and mapped through `ORDER`; anything else is treated as keys.

---

## Rendering

Two functions, deliberately separated.

**`build()`** runs once. It generates all the markup for sections and the tick strip via `innerHTML`, and attaches a single delegated `change` listener on `#list` rather than 250 individual ones.

**`paint()`** runs after every change. It walks the DOM and syncs visual state — checkboxes, strikethroughs, tick marks, per-section counts, tier totals, the export code.

`paint()` is O(n) over 250 items on every checkbox click. That's a few milliseconds and not worth optimising; the simplicity of "recompute everything" is worth more than the microseconds saved by targeted updates.

All interpolated text goes through `esc()`. The data is authored by you rather than user-supplied, so this is defence in depth rather than a live concern — but `innerHTML` with unescaped strings is a habit worth not having.

### The tick strip

250 flex children with `flex: 1 1 0; min-width: 0`, so they divide the available width evenly regardless of count. Tier 1 marks are drawn taller. Three-pixel transparent spacers separate sections.

It's the one deliberately expressive element. Hickman's books are known for Rian Hughes' infographic title pages, and the strip is the same idea: the whole structure as a single legible object.

---

## Storage and sync

Three layers, in order of precedence.

**`localStorage`** is always written, signed in or not. It's the source of truth when signed out and a cache when signed in, so a network failure never loses a tick.

**Supabase** is written when a session exists, debounced 700ms. Rapid ticking produces one request rather than ten. Writes are `upsert` on `user_id`, so the row is created on first save.

**The export code** is `btoa(JSON.stringify([...done]))` — the same data, portable by copy-paste. It exists because not everyone wants an account.

### The merge on first sign-in

Someone ticks 40 issues signed out, then signs in. Their local progress shouldn't vanish, and their account's progress shouldn't be overwritten either.

`adopt()` handles it: on first sign-in for a given user ID it takes the **union** of local and server, pushes that, and sets a `hsw:merged:<uid>` flag. On every subsequent sign-in the server is authoritative and local is just refreshed from it.

The union is the right call once — you can't have unread something you never read — but it's wrong repeatedly, because un-ticking on device A would be undone by device B's stale local copy. Hence the flag.

There's no conflict resolution beyond that. Two devices ticking simultaneously is last-write-wins, and the loser's tick is lost. For a reading tracker that's an acceptable failure; if it mattered, `read_ids` would need to be a set of rows with timestamps rather than one array column.

The column is `text[]`, matching the string IDs above. It was `int[]` when IDs were positional — if you see `400` responses on `/rest/v1/progress`, that mismatch is the first thing to check.

---

## Groups

Two tables, both keyed to `auth.users`, so membership travels with the account
rather than the browser: `groups` (code, name, start and target date) and
`group_members` (`group_id` + `user_id` primary key, display name, color index).
The only thing kept in `localStorage` is `hsw:group`, which remembers *which* of
your groups is on screen when you're in more than one.

### The recursion trap

The obvious policy on `group_members` — "you may read rows of groups you belong
to" — has to query `group_members` to answer, which re-triggers the policy, and
Postgres errors out. Both membership tests are therefore `security definer`
functions (`is_group_member`, `shares_group_with`) that run as the owner and skip
RLS on the inner read.

### Joining without exposing the table

There's deliberately no select policy that matches a group by code. If there
were, anyone could enumerate `groups` by guessing six characters. Instead
`join_group(code, name)` is a `security definer` function: it resolves the code,
inserts your membership row, and returns the group. The only way to see a group
is to already be in it.

Codes come from a 32-character alphabet with `0`, `O`, `1` and `I` removed, and
`new_group_code()` re-rolls on collision.

### Drawing the stack

`paintStack()` sorts members by issues read, then computes `deepest[]` — for each
of the 250 columns, the index of the furthest-back layer that still has that
issue ticked. A layer's mark stretches to the bottom of the stack only where
`deepest[idx] === i`, which is exactly "nobody behind me is still showing here."
That's what keeps the leader's bar from painting over everyone else.

Your own layer reads from the live `done` set through `readsOf()` rather than a
copy taken at load. `done` is *reassigned* by reset, import and the first-sign-in
merge, so a cached reference would quietly go stale.

### Freshness

No realtime channel. Members are re-fetched every 45 seconds while the tab is
visible, on `visibilitychange`, and on demand from the Refresh button. Your own
layer updates instantly because it's reading `done` directly.

The stack rebuilds all 250 × *n* marks on every tick. At four readers that's a
thousand spans per click, still comfortably under a frame; if groups ever got
large enough to matter, the fix is to redraw only the layers whose `deepest[]`
entries changed.

### What the security actually is

The anon key in the source is public by design. It identifies the project, not a user, and Supabase expects it in client code.

The protection is **row-level security**, enforced by Postgres:

```sql
create policy "read own" on progress for select using (auth.uid() = user_id);
```

`auth.uid()` comes from the signed JWT that Supabase issues at sign-in. It can't be forged without the project's secret, which never leaves Supabase's servers. So a user's request can only ever touch their own row, no matter what the client sends — the check happens in the database, after the client has had its say.

This is why "the login is in the JavaScript" is fine here and wasn't fine in the pre-Supabase version. The client isn't being trusted to enforce anything. It just presents a token, and the server decides.

If you remove those policies while leaving RLS off, the anon key becomes a public read-write handle on the whole table. Don't.

---

## Regenerating the list

`DATA` is pasted into the file, but it's generated. The generator (`gen.py`, kept outside this repo) builds sections programmatically so that ranges like *Secret Warriors* #1–28 are loops rather than 28 hand-typed lines, then asserts that all 250 keys are unique before writing.

If you're hand-editing `DATA` instead, the invariants to preserve:

- every `id` unique across the whole array
- `tier` is 1, 2, or 3
- section `id` is a valid HTML id (it's used for `<details id="d-...">`)

Nothing validates these at runtime. Duplicate IDs will make two checkboxes move together, which is confusing and silent.

---

## Known limitations

**No offline queue.** A failed cloud write shows "Offline — saved on this device" and isn't retried until the next tick. Local data is intact, so nothing is lost, but a sign-in on another device before the next tick would show stale state.

**No realtime.** Two open tabs won't see each other's changes until reload.

**Magic-link rate limits.** Supabase's built-in mailer allows only a few auth emails per hour on the free tier. Fine for personal use; you'll need SMTP for anything more.

**Font loading.** Google Fonts is a third-party request and a privacy consideration if you care. Self-host the two families to remove it.

**Marvel links.** 27 of 250 items link to specific issues; the rest link to a series. That's not laziness — Marvel's site only renders the 20 most recent issues of any series server-side, and pagination and year-filter parameters are ignored. The remainder can't be enumerated from outside.
