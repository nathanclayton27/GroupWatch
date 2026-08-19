# How it works

The single technical document for GroupWatch. It replaces the old
`HANDOFF.md`, `HOW-IT-WORKS.md` and `PLAN.md`, which described the app when it
tracked one hardcoded reading order and had drifted badly out of date. Three
overlapping documents is how that happened; there is one now.

---

## The shape of the thing

```
groupwatch/
├── properties/
│   ├── index.json          generated manifest — do not hand-edit
│   ├── fma-brotherhood.json
│   ├── hickman-secret-wars.json
│   └── cates-venom.json
├── src/
│   ├── build.py            validates properties, writes the manifest
│   ├── template.html       markup, CSS, JS — the thing you edit
│   └── reading_order.py    authoring source for the Hickman order only
├── tools/                  one generator per property that needs one
├── schema.sql              fresh database
├── migrate-*.sql           run once each, on an existing database
└── index.html              generated, committed, served
```

**`index.html` is generated. Don't edit it.** It is committed anyway, because
GitHub Pages has no build step of its own.

```
src/template.html  +  properties/index.json  →  python3 src/build.py  →  index.html
```

Property *bodies* are not inlined. The page boots, reads `?p=<slug>`, and
`fetch`es that property's JSON. Only the manifest — title, kind, year, counts,
accents — is baked into the page, because the switcher needs it before first
paint.

**That means you must serve over http.** `fetch` is blocked on `file://`, so
opening the file directly gives you a page that cannot load anything. Use
`python3 -m http.server 8000`. This was already true for auth; it is now true
for the data as well.

---

## Adding a property

Drop a JSON file into `properties/` and rebuild. Nothing else.

```json
{
  "slug": "must-equal-the-filename",
  "title": "Some Show",
  "subtitle": "optional, shown under the title",
  "kind": "anime",
  "year": "2019",
  "order": 4,
  "blurb": "One sentence for the picker.",
  "unit":  { "one": "episode", "many": "episodes" },
  "verb":  { "base": "watch", "past": "watched", "ing": "watching" },
  "accent": "#B0472E",
  "accentDark": "#E8874F",
  "itemOrder": "number-first",
  "tiers": false,
  "sections": [ … ]
}
```

| Field | Effect |
|---|---|
| `slug` | the `?p=` value and the `property_id` in the database. **Never change it.** |
| `unit` | drives all copy — "42 episodes", "3 issues behind" |
| `verb` | drives the rest — "Watching with other people", "read" vs "watched" |
| `accent` / `accentDark` | one per theme; see *Accents* below |
| `itemOrder` | `number-first` renders `12  One is All, All is One`; the default renders `Fantastic Four #570` |
| `tiers` | `false` hides the tier columns entirely |
| `order` | menu and picker position; ties break on title |
| `rules` | renders a house-rules panel |
| `notes` | footer prose. `["Heading.", "body"]` pairs, or a bare string |
| `forGroup` | per-group copy overrides, keyed by join code |
| `schedule` | dated windows — see *Pace* |

Sections take `id`, `title`, `sub`, optional `tier`, `intro`, `links`, `start`.
Items take `id`, `t`, `n`, and optional `note`, `star`, `opt`, `url`.

### The ID rule

`item.id` is a stable key, and progress is stored as a list of them.

- **Reordering and moving items between sections is safe.** The ID travels with
  the item.
- **Renaming an ID silently destroys saved progress.** Everyone who ticked it
  loses the tick, with no error anywhere.

Prefix IDs with the property (`fmab-1`, `venom-ac-3`). `build.py` fails the
build on duplicates — a duplicate would make two checkboxes move together,
silently, which is the worst kind of bug.

`build.py` also fails on a slug that doesn't match its filename, a missing
`unit`, and a section id that isn't a valid HTML id.

---

## Rendering

**`build()`** runs once: all markup for sections and the strip via `innerHTML`,
plus a single delegated `change` listener rather than one per item.

**`paint()`** runs after every change and syncs everything visual — checkboxes,
strikethroughs, marks, counts, the export code, the schedule line, the group
stack. Recomputing everything is a few milliseconds and worth more than the
microseconds targeted updates would save.

All interpolated text goes through `esc()`. That matters more than it used to:
display names are supplied by other people now, not just by you.

### The strip

Marks are `flex: 1 1 0; min-width: 0`, so they divide the width evenly at any
count. Tier-1 marks are drawn taller where a property has tiers. Three-pixel
transparent spacers separate sections.

### Which section opens

Before you have marked anything, the property's own default — a section with
`start`, else the first with links, else the first section. After that, the
furthest section you have touched, or the next unfinished one if you have
cleared it.

This runs on the first `paint()`, not at boot, because at boot the session has
not resolved and no progress exists yet. A once-per-load guard stops it
fighting you when you collapse something mid-session.

### Accents

Every colour in the palette has a light and a dark value. A property therefore
carries `accent` and `accentDark`, and `applyAccent()` picks between them from
`prefers-color-scheme`, re-running when the system theme changes. Setting one
accent for both themes flattens the palette and leaves dark mode wearing the
light tone.

---

## Groups

Two tables, both keyed to `auth.users`, so membership follows the account
rather than the browser: `groups` (code, name, property, dates, shift) and
`group_members` (`group_id` + `user_id`, display name, colour index).

`localStorage` holds only `gw:group:<slug>` — which of your groups is on
screen, per property, when you are in more than one.

### The recursion trap

The obvious policy on `group_members` — "you may read rows of groups you belong
to" — has to query `group_members` to answer, which re-triggers the policy, and
Postgres errors out. Both membership tests are therefore `security definer`
functions (`is_group_member`, `is_group_owner`, `shares_group_with`) that run as
the owner and skip RLS on the inner read. Don't inline them back into policies.

### Joining without exposing the table

There is deliberately no select policy matching a group by code. If there were,
anyone could enumerate `groups` by guessing six characters. `join_group()` is a
`security definer` function that resolves the code and inserts your membership.
The only way to see a group is to already be in it.

Codes use a 32-character alphabet with `0`, `O`, `1` and `I` removed, so they
survive being read aloud, and `new_group_code()` re-rolls on collision.

### Property scoping

`shares_group_with(other, property)` takes the property as an argument and joins
through `groups`. Without that join, someone in your Fullmetal Alchemist group
could read your Secret Wars progress.

### Drawing the stack

`paintStack()` sorts members by count, then computes `deepest[]` — for each
column, the index of the furthest-back layer that still has that item ticked.

**Fill to the bottom where nothing is behind you.** A read mark stretches from
its layer's top to the bottom of the stack only where `deepest[idx] === i`.
Otherwise the readers behind still show as bands beneath it.

**Don't punch holes.** An unread mark is a short grey nub. Where a reader
*behind* has a stretched mark, a front layer's nub sits on top of it and cuts a
grey gap through their bar. `veil` suppresses it where `deepest[idx] > i`. This
was a real shipped bug; with two readers and one barely started, the whole bar
looked broken.

Your own layer reads the live `done` set through `readsOf()`, never a copy taken
at load — `done` is reassigned wholesale by reset, import and the first-sign-in
merge, so a cached reference goes stale in silence.

### Freshness

No realtime channel. Members are re-fetched every 45 seconds while the tab is
visible, on `visibilitychange`, and from the Refresh button. Your own layer
updates instantly because it reads `done` directly.

The stack rebuilds every mark for every reader on each tick. At 250 items and
four readers that is a thousand spans per click, comfortably inside a frame. A
much longer property or a large group would want redrawing only the layers whose
`deepest[]` entries changed. Don't optimise it until it hurts.

---

## Pace

Two models.

**Linear.** A group with a `target_date` gets a straight line from `start_date`,
and `expected = TOTAL × elapsed`.

**Windows.** A property can declare dated windows with cumulative targets:

```json
"schedule": { "kind": "windows", "windows": [
  { "start": "2026-07-15", "end": "2026-07-28", "through": 20, "label": "…" }
]}
```

`through` is the cumulative count due by the **end** of that window.

**Behind is measured against the last window that has closed**, not
interpolated inside the open one — you have until a window's end date, and
finishing early is meant to buy you off days. Interpolating would nag people who
are exactly on schedule. Two markers appear on the strip: a solid rule at what
is overdue, a lighter one at the current window's goal.

A group's owner can slide the whole schedule with `schedule_shift_days`. Every
window moves together, so the pace is unchanged and only the dates differ. On a
property with no schedule, the owner sets, changes or removes a plain finish
date instead; removing it removes pace tracking with it.

---

## Storage

Three layers, in precedence order.

1. **`localStorage`**, always written first, keyed `gw:v1:<slug>`. A network
   failure never costs a tick.
2. **Supabase**, when a session exists, debounced 700ms, upserted on
   `(user_id, property_id)`.
3. **The export code**, `btoa(JSON.stringify([...done]))`, for moving progress
   without an account.

Sync failures are non-fatal by design: they surface in the status indicator and
log with a `[tracker]` prefix, and the local write already happened.

On first sign-in for a given user and property, `adopt()` takes the **union** of
local and server, pushes it, and sets a `gw:merged:<uid>:<slug>` flag. The union
is right once — you cannot unread something you never read — and wrong
repeatedly, because un-ticking on device A would be undone by device B's stale
copy.

`migrate()` walks two older key formats forward for the Hickman property:
positional integers → slug IDs → the per-property key.

---

## What the security actually is

The anon key in the source is public by design. It identifies the project, not
a user, and Supabase expects it in client code.

The protection is row-level security, enforced by Postgres. `auth.uid()` comes
from the signed JWT issued at sign-in and cannot be forged without the project's
secret, which never leaves Supabase. A request can only ever touch rows the
policies allow, no matter what the client sends.

Joining a group makes your progress readable by that group, for that property.
That is what the shared strip is. Leaving ends it.

If you remove the policies while leaving RLS off, the anon key becomes a public
read-write handle on the whole database. Don't.

---

## Deploying

```bash
python3 src/build.py
git add -A && git commit -m "…" && git push
```

Pages redeploys in under a minute. **Forget the build and the manifest goes
stale**, so a new property never appears in the switcher.

`.vscode/tasks.json` has Build, Serve and Build-and-serve, reachable via
*Run Task*. Build is the default — `Cmd/Ctrl+Shift+B`.

Worth a hook if you will be at this a while:

```bash
cat > .git/hooks/pre-commit <<'EOF'
#!/bin/sh
python3 src/build.py && git add index.html properties/index.json
EOF
chmod +x .git/hooks/pre-commit
```

---

## Gotchas

**`progress.read_ids` must be `text[]`, not `int[]`.** It was `int[]` when IDs
were array positions. An old snippet gives you `400` on every write.

**Keep JSON pretty-printed.** Compact output turns every rebuild into one
enormous changed line and makes review impossible.

**Supabase's built-in mailer allows about two auth emails an hour.** Not enough
to sign in as a second person and test a group. GitHub OAuth costs no emails —
the provider needs enabling in Supabase and the callback is
`https://<project-ref>.supabase.co/auth/v1/callback`.

**Add `http://localhost:8000/**` to Authentication → URL Configuration →
Redirect URLs**, or magic links bounce to the production Site URL. Links already
sent have the destination baked in; request a new one after changing it.

**GitHub email privacy breaks account linking.** A GitHub account returning a
`users.noreply.github.com` address won't match your magic-link email, so
Supabase creates a separate user with separate progress. Copy the export code
before switching auth methods.

**Marvel only exposes the 20 most recent issues of a series**, and `?offset`,
`?limit` and `?byYear` are ignored. That is why most links are series-level.
Look series ids up rather than constructing them — the numeric id is what
resolves and the slug after it is decoration, so a guessed id lands silently on
somebody else's comic.

**`forGroup` is presentation, not secrecy.** Property files are served
publicly. It hides copy from the page, not from anyone who opens the JSON.
