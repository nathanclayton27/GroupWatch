# GroupWatch — handoff

Everything needed to start this repo in a fresh VS Code session.

---

## What it is

A group tracker for **any** property. Pick a thing — a comic run, an anime, a
show, a film series — tick off what you've read or watched, and join a group
with a six-character code. Everyone's progress then stacks onto a single strip
so you can see, at a glance, who's ahead and who's fallen behind a shared
finish date.

The mechanic is proven. It already runs at
[nathanclayton27/secretwars](https://github.com/nathanclayton27/secretwars) for
one 250-issue Hickman reading order. **GroupWatch is that, generalized to many
properties, with a property switcher in the top left.**

Everything in this document that describes the strip, the groups, the join
codes or the row-level security is a description of working, shipped code — not
a proposal. Port it rather than reinventing it. The parts that are genuinely new
are the property switcher, the data format, and the multi-property schema.

---

## Decisions already made

| Decision | Choice | Why |
|---|---|---|
| Backend | **Reuse the existing Supabase project**, fold Secret Wars in as property #1 | One login, one set of groups, no second project to keep in sync. Costs a migration on live data. |
| Property data | **One JSON file per property** | Adding a show is dropping in a file. No Python needed to author. |
| Data delivery | **Fetched at runtime**, not inlined | With many properties, inlining every item into one HTML file gets fat fast. |
| Routing | **`?p=slug` query param**, never the hash | Supabase puts auth tokens in the URL hash. Routing there collides with sign-in. |

---

## Repo layout

```
groupwatch/
├── properties/
│   ├── index.json                 ← generated manifest, do not hand-edit
│   ├── hickman-secret-wars.json
│   └── fma-brotherhood.json       ← written, see the bottom of this doc
├── src/
│   ├── build.py                   ← validates properties, writes the manifest
│   └── template.html              ← markup, CSS, JS
├── tools/
│   └── make_fmab.py               ← one-off generator for the FMA:B schedule
├── schema.sql                     ← run once in the Supabase SQL editor
├── migrate-to-multiproperty.sql   ← run once, against the existing project
├── index.html                     ← generated, committed, served
├── README.md
└── HANDOFF.md
```

`properties/fma-brotherhood.json` and `tools/make_fmab.py` already exist
alongside this document — copy them into the new repo as-is.

Same shape as secretwars: `src/` is authored, `index.html` is generated and
committed anyway because GitHub Pages has no build step.

**Difference from secretwars:** the property data is no longer inlined into
`index.html`. The page boots, reads `?p=`, and `fetch`es that property's JSON.
`build.py` therefore does far less than it used to — it validates the property
files and writes the manifest, and that's it.

One consequence: **you must use a local server, never `file://`.** `fetch` on a
`file://` origin is blocked. That was already true for auth; now it's true for
the data too.

---

## The property file

```json
{
  "slug": "fma-brotherhood",
  "title": "Fullmetal Alchemist: Brotherhood",
  "kind": "anime",
  "year": "2009–2010",
  "blurb": "One sentence for the property picker.",
  "unit": { "one": "episode", "many": "episodes" },
  "accent": "#B0472E",
  "tiers": false,
  "sections": [
    {
      "id": "s1",
      "title": "The Elric Brothers",
      "sub": "episodes 1–14 · the setup",
      "tier": 1,
      "intro": "Optional prose block, shown above the list.",
      "links": [
        { "label": "Crunchyroll", "url": "https://..." }
      ],
      "items": [
        {
          "id": "fmab-1",
          "t": "Fullmetal Alchemist",
          "n": "E1",
          "note": "optional one-line annotation",
          "star": 1,
          "opt": 0,
          "url": "https://optional-direct-link"
        }
      ]
    }
  ],
  "schedule": {
    "unitsPerWeek": 4,
    "note": "Optional. Seeds a group's suggested finish date."
  }
}
```

### Fields that matter

| Field | Notes |
|---|---|
| `slug` | Must equal the filename. It's the `?p=` value and the `property_id` in the database. **Never change it** — it's the key everyone's progress hangs off. |
| `unit` | Drives all copy: "42 episodes", "3 issues behind". Set it per property. |
| `tiers` | `false` hides the tier stats entirely. Secret Wars uses tiers; FMA:B almost certainly shouldn't. |
| `accent` | Optional per-property accent colour. Falls back to the site default. |
| `star` / `opt` | Carried over from secretwars — ★ highlights and an "optional" pill. |
| `schedule` | Optional. Used to *suggest* a finish date when creating a group; the group's actual `target_date` is still what pace is measured against. |

### The ID rule — read this one

`item.id` is a stable key. Progress is stored as a list of these strings, so:

- **Reordering and moving items between sections is safe.** The ID travels with
  the item.
- **Renaming an ID silently destroys saved progress.** Everyone who ticked that
  item loses the tick, with no error.

Prefix every ID with the property slug (`fmab-1`, not `1`) so IDs stay unique if
you ever merge or cross-reference properties. `build.py` must assert uniqueness
within a property and fail the build on a duplicate — a duplicate makes two
checkboxes move together, silently.

---

## Database

One Supabase project, shared with the existing tracker. **Two SQL files: run the
migration first, then the schema.**

### Step 1 — migrate the existing tables

`progress` and `groups` are currently single-property. They need a
`property_id`.

```sql
-- progress becomes one row per (user, property)
alter table progress add column if not exists property_id text not null
  default 'hickman-secret-wars';
alter table progress drop constraint progress_pkey;
alter table progress add primary key (user_id, property_id);
alter table progress alter column property_id drop default;

-- a group is for exactly one property
alter table groups add column if not exists property_id text not null
  default 'hickman-secret-wars';
alter table groups alter column property_id drop default;
```

The defaults backfill every existing row to the Hickman property, then are
dropped so future inserts must be explicit. **Your current progress and any
existing groups survive this** — they just become "the Secret Wars property".

### Step 2 — fix the cross-property privacy hole

This one is easy to miss and it matters. The shipped policy is:

```sql
create policy "read group progress" on progress
  for select using (shares_group_with(user_id));
```

With multiple properties, that lets someone in your *FMA:B* group read your
*Secret Wars* progress. The membership test has to be property-scoped:

```sql
create or replace function shares_group_with(other uuid, prop text)
returns boolean language sql security definer stable set search_path = public as $$
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

drop policy "read group progress" on progress;
create policy "read group progress" on progress
  for select using (shares_group_with(user_id, property_id));
```

### Step 3 — everything else carries over unchanged

Copy `schema.sql` from secretwars wholesale. It already contains:

- `groups` / `group_members`, keyed to `auth.users` so membership follows the
  account rather than the browser
- `is_group_member()` and `shares_group_with()` as **`security definer`**
  functions
- `create_group()` / `join_group()` RPCs
- code generation over a 32-character alphabet with `0`, `O`, `1`, `I` removed

`create_group` needs one new parameter — `p_property_id` — and should insert it.

### Two traps that are already solved, don't re-solve them

**RLS recursion.** The obvious policy on `group_members` ("you may read rows of
groups you belong to") has to query `group_members` to answer itself, which
re-triggers the policy and errors out. That is why the membership tests are
`security definer` functions. Don't try to inline them back into the policies.

**Code enumeration.** There is deliberately no select policy matching a group by
code. If there were, anyone could enumerate `groups` by guessing six characters.
`join_group()` resolves the code as the definer instead. The only way to see a
group is to already be in it.

---

## The layered strip

This is the hard-won part. It went through six design rounds; the rules below
are the ones that survived. Port them exactly.

### What a layer means

Mark *n* is item *n*, lit only if that person ticked it. **Positional, not
cumulative.** A reader who has watched only episode 40 shows one mark at
position 40 and nothing before it. That looks odd at first and it is correct —
it means the strip lines up with the checklist below it, and you can see someone
skipping ahead or reading out of order.

The rejected alternative was filling each layer from the left by count. It draws
a tidier bar and lies about position.

### Geometry

- One layer per reader, all the same height (34px), absolutely positioned
- Stacked with a vertical offset so each peeks out below the one in front
- Offset is 14px up to four readers, then `max(6, round(56/(n-1)))` so large
  groups don't grow a skyscraper
- Sorted by count descending — **whoever has read most is the front/top layer**,
  re-sorted live as people tick
- Colours come from an eight-entry palette (`--m1`…`--m8`) with separate light
  and dark values; a member's `color_index` is assigned at join time and stored,
  so their colour doesn't change when someone overtakes them

### The two rules that make it readable

Compute, for each column, the **deepest** layer still showing there:

```js
const deepest = ORDER.map(id => {
  for (let i = reads.length - 1; i >= 0; i--) if (reads[i].has(id)) return i;
  return -1;
});
```

**Rule 1 — fill to the bottom where nothing is behind you.** A read mark
stretches from its own layer's top down to the bottom of the whole stack only
where `deepest[idx] === i`. Otherwise it stays a normal 34px mark, so the
readers behind still show as bands beneath it.

```js
const full = on && deepest[idx] === i;
```

**Rule 2 — don't punch holes.** An unread mark is a short grey nub at the bottom
of its own layer. Where a reader *behind* has a stretched mark, a front layer's
grey nub sits on top of it (front layers have the higher z-index) and cuts a
grey gap straight through their bar. Suppress it:

```js
const veil = !on && deepest[idx] > i;
```

```css
.stack .tick.on.full { align-self: flex-start; height: var(--fillH); }
.stack .tick.veil    { background: transparent; }
```

Rule 2 was a real shipped bug. With two readers and one barely started, the
whole bar looked broken.

### Live progress

Your own layer must read the live `done` set through a helper, **not** a copy
taken at load time:

```js
function readsOf(m){ return (user && m.id === user.id) ? done : m.read; }
```

`done` is reassigned wholesale by reset, import, and the first-sign-in merge. A
cached reference goes stale silently.

### Legend

Names live in a legend below the strip, never on the strip itself — colour is
what identifies people. Show the percentage **and** the raw count, and render
`<1%` rather than `0%` for any nonzero progress, or one item out of hundreds
looks identical to not having started.

---

## Pace

There are **two** pace models. The shipped tracker has the first; FMA:B needs
the second, and it's the more interesting one.

### Linear — a group with just a finish date

A group has `start_date` and `target_date`; expected progress today is a
straight line between them.

```js
const frac = clamp01((Date.now() - start) / (end - start));
const expected = Math.round(TOTAL * frac);
```

Each member is tagged **on pace** or *n* **behind**, and a thin vertical rule is
drawn on the strip at `frac * 100%`.

### Windows — a property with a real schedule

This is what the FMA:B club actually runs on. The property declares dated arc
windows, each with a cumulative target:

```json
"schedule": {
  "kind": "windows",
  "windows": [
    { "start": "2026-07-15", "end": "2026-07-28", "through": 20,
      "label": "Chapters 1–2: Hunt for the Stone & Shadow of the Homunculi" },
    { "start": "2026-07-29", "end": "2026-08-04", "through": 30, "label": "…" }
  ]
}
```

`through` is the cumulative item count due by the **end** of that window, not
the count within it. That makes the arithmetic trivial and unambiguous.

**Behind is measured against the last window that has closed, not the current
one.** The club's rule is that you have until a window's end date, and finishing
early buys you off days. Interpolating inside the open window would nag people
who are entirely on schedule.

```js
const today = todayISO();
const closed = windows.filter(w => w.end < today);
const due    = closed.length ? closed[closed.length - 1].through : 0;
const current = windows.find(w => w.start <= today && today <= w.end);

const behind = Math.max(0, due - count);          // overdue right now
const target = current ? current.through : TOTAL; // where you're heading
```

Two markers on the strip, not one:

- a solid rule at `due` — everything left of it is overdue
- a lighter rule at `current.through` — this window's goal, with its end date

Show the current window's label and end date near the strip. "Chapter 4: The
Wall of Briggs, through episode 43 by August 11" tells someone everything they
need in one line.

Edge cases to handle: before the first window starts (nothing is due), after the
last window ends (everything is), and gaps between windows if a schedule ever
has them.

### Which model applies

If the property has `schedule.kind === "windows"`, use windows and let the group
inherit the schedule's first start and last end as its own dates. Otherwise fall
back to linear against the group's `target_date`. A group should be able to opt
out of a property's schedule and set its own finish date — a group starting in
September shouldn't be told it's 64 episodes behind.

---

## The property switcher

A button in the **top left**, always visible. Clicking it opens a menu of every
property in `properties/index.json` — title, kind, year, and your own progress
in each. Choosing one navigates to `?p=slug`.

Notes:

- The current property's slug is the single source of truth for the whole page.
  Read it once at boot, default to the first entry in the manifest if absent or
  unknown.
- Switching is a **full navigation**, not a client-side swap. Simpler, and it
  makes the URL shareable and the back button correct.
- The button should show the current property's title, so it reads as "you are
  here, click to move" rather than an anonymous hamburger.
- Groups are per-property. Switching properties switches which group's strip you
  see. Make that legible in the UI or it will confuse people.

---

## Storage model

Three layers, in precedence order — carried over unchanged and worth preserving:

1. **`localStorage`** is always written first, signed in or not, keyed per
   property (`gw:v1:<slug>`). A network failure therefore never loses a tick.
2. **Supabase** is written when a session exists, debounced 700ms.
3. **An export code** — `btoa(JSON.stringify([...done]))` — for moving progress
   by hand without an account.

Sync failures are non-fatal by design: they surface in a status indicator and
log to the console with a `[tracker]` prefix, and the local write already
happened.

On first sign-in for a given user id, take the **union** of local and server
progress, push it, and set a `merged:<uid>:<slug>` flag. The union is right
once — you can't unread something you never read — and wrong repeatedly, because
un-ticking on device A would be undone by device B's stale local copy.

---

## Build and deploy

```bash
python3 src/build.py     # validates properties, writes properties/index.json
python3 -m http.server 8000
```

`build.py` should fail loudly on: duplicate item IDs within a property, a `slug`
that doesn't match its filename, a missing `unit`, and a section `id` that isn't
a valid HTML id.

Deploy is the secretwars flow — build, commit, push, Pages redeploys in under a
minute. **If you forget the build step the manifest goes stale** and a new
property won't appear in the switcher.

Keep JSON output pretty-printed (`indent=2`). Compact output turns every rebuild
into one enormous changed line and makes review impossible.

---

## Inherited gotchas

**`read_ids` must be `text[]`, not `int[]`.** It was `int[]` in the very first
version when IDs were array positions. An old snippet gives you `400` on every
write.

**The anon key belongs in the source.** It's publishable; row-level security is
what protects the data. Removing the RLS policies while leaving RLS disabled
would turn it into a public read-write handle.

**Supabase's built-in mailer allows roughly two auth emails an hour.** Not
enough to sign in as a second person and test a group. GitHub OAuth costs no
emails — enable the provider and set `ENABLE_GITHUB_LOGIN = true`. The callback
URL is `https://<project-ref>.supabase.co/auth/v1/callback`.

**Add `http://localhost:8000/**` to Authentication → URL Configuration →
Redirect URLs** or magic links bounce to the production Site URL instead of your
local page. Links already sent have the destination baked in — request a new one
after changing it.

**GitHub email privacy breaks account linking.** If a GitHub account returns a
`users.noreply.github.com` address, it won't match the magic-link email and
Supabase creates a *separate* user with separate progress. Copy the export code
before switching auth methods.

---

## Performance note

The stack rebuilds every mark for every reader on each tick — at 250 items and
four readers that's a thousand spans per click, comfortably under a frame. A
much longer property, or a large group, may need redrawing only the layers whose
`deepest[]` entries actually changed. Don't optimise this until it's a problem.

There is no realtime channel. Members are re-fetched every 45 seconds while the
tab is visible, on `visibilitychange`, and from a Refresh button. Your own layer
updates instantly because it reads `done` directly.

---

## Order of work

1. Scaffold the repo and `src/template.html` by copying secretwars' generated
   `index.html` and pulling the inlined `DATA` out into a fetch.
2. Write `properties/hickman-secret-wars.json` by dumping the existing `DATA`
   array to JSON. Verify the old tracker's IDs are preserved exactly, or every
   existing user loses their progress.
3. Run the migration SQL, then the updated schema.
4. Add the property switcher and `?p=` routing.
5. Add `properties/fma-brotherhood.json`.
6. Test with two accounts in one group before calling it done.

Step 2 is the one with real consequences. Everything else is recoverable.

---

## The FMA:B property — already written

`properties/fma-brotherhood.json` exists, generated by `tools/make_fmab.py` from
the HD DVD Anime Club Round 4 calendar. 64 episodes, five windows:

| Window | Arc | Episodes | Through |
|---|---|---|---|
| Jul 15 – Jul 28 | Chapters 1–2: Hunt for the Stone & Shadow of the Homunculi | 1–20 | 20 |
| Jul 29 – Aug 4 | Chapter 3: Sins of the Father | 21–30 | 30 |
| Aug 5 – Aug 11 | Chapter 4: The Wall of Briggs | 31–43 | 43 |
| Aug 12 – Aug 18 | Chapter 5: The Uprising | 44–53 | 53 |
| Aug 19 – Aug 25 | Chapter 6: The Promised Day | 54–64 | 64 |

All dates are 2026. The generator asserts the total is 64 and that no item ID
repeats, so a bad edit fails loudly.

Three things to know about it:

**Chapters 1 and 2 are one section.** The calendar gives them a single shared
window, and I don't know where the club draws the boundary between them. If you
want them split, add the episode number where Chapter 2 begins to `ARCS` in the
generator and rerun.

**Episode titles are deliberately absent.** Items render as "Episode 1" through
"Episode 64". I left the real titles out rather than risk writing 64 of them
from memory and getting some wrong. Add them to each item's `t`, or as a `note`,
whenever you have a reliable list.

**The club bylaws are in the file** as a `rules` array — pace yourself, discuss,
early finishers get off days, don't transmute your mom. Render them on the
property page; they're the character of the thing, not boilerplate.

---

## Still open

- **Episode titles** for FMA:B, as above.
- **The Secret Wars property file** — dump the existing `DATA` array to JSON
  with its IDs preserved exactly. This is the one step that can destroy live
  progress if done carelessly.
- **A default property.** Decide what loads at `/` with no `?p=`. Most recently
  visited, or a picker page.
