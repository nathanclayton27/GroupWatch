# Everything Dies

A reading tracker for Jonathan Hickman's Marvel run — 250 issues from *Fantastic Four* #570 (2009) through *Secret Wars* #9 (2015), in the order they're meant to be read.

Hickman's saga runs across nine titles that interleave. *Avengers* and *New Avengers* alternate chapter by chapter; *Infinity* braids into both; *Fantastic Four* and *FF* tell one story from two angles. Publication order works, but the intended order is better and hard to hold in your head. This tracks it.

**[Open the tracker →](https://YOURNAME.github.io/REPO/)**

## What it does

- Every issue in reading order, grouped into 14 sections
- **Tiers**, so you know what's skippable — 1 is essential (122 issues), 2 is strongly recommended (61), 3 is genuinely optional (67). Tier 1 alone is a complete, coherent read.
- A tick strip showing all 250 issues at once, so you can see where you are
- Notes where they're needed: which issues retell each other, which are skippable, which are the high points
- Optional accounts, so progress follows you between phone and desktop
- **Reading groups** — share a six-character code and everyone's progress stacks onto one strip, a colored layer each, furthest along on top. Set a finish date and the group can see who's keeping up.

No spoilers beyond arc titles printed on the covers.

## Run it yourself

Everything is one file.

1. Fork or copy this repo.
2. Settings → Pages → Source: **Deploy from a branch**, `main` / `root`.
3. Live in about a minute.

That's a working tracker. Progress saves to each visitor's own browser, and there's a copy-paste code for moving between devices.

## Turn on accounts

Optional. Without it the tracker works fine; progress just doesn't sync across devices.

**1.** Create a free project at [supabase.com](https://supabase.com).

**2.** In the SQL editor, paste and run [`schema.sql`](schema.sql).

It creates `progress` (one row per reader), `groups` and `group_members`, the
row-level security policies for all three, and the two functions the join flow
uses. It's safe to run against a project that already has the original
`progress` table — that block is `if not exists` and its policies are guarded,
so re-running changes nothing.

**3.** Authentication → URL Configuration: set **Site URL** to your Pages URL, and add it under **Redirect URLs**.

**4.** In `index.html`, fill in the two constants at the top of the script:

```js
const SUPABASE_URL      = 'https://xxxxx.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbG...';
```

Both are in Supabase under Settings → API. Commit them — the anon key is meant to be public, and the row-level security policies above are what actually protect the data. Every query runs as the signed-in user, and the policies mean a user can only ever reach their own row.

Sign-in is a magic link by default: enter an email, get a link, click it. No passwords anywhere. For GitHub sign-in instead, enable the GitHub provider in Supabase and set `ENABLE_GITHUB_LOGIN = true`.

Supabase's free tier sends a limited number of auth emails per hour. For anything beyond personal use, plug in an SMTP provider under Authentication → Emails.

## Reading groups

Sign in, name yourself, and either create a group or enter a code someone sent
you. Creating one gives you a six-character code — `K4M7QX`, no `0`/`O`/`1`/`I`,
so it survives being read aloud. Anyone signed in who has the code can join.

Once you're in a group the strip at the top of the page changes: instead of your
progress alone it draws one layer per reader, stacked, sorted so whoever's read
the most sits on top. Colors identify people; the legend underneath names them.
Give the group a finish date and a vertical rule marks where everyone should be
today, with each reader tagged **on pace** or *n* **behind**.

**Joining a group makes your ticks readable by the people in it.** That's what
the shared strip is, and it's the one privacy consequence worth knowing about.
The `read group progress` policy scopes it to co-members — nobody else, signed in
or not, can read your row — and leaving the group ends it.

## Changing the list

The reading order is the `DATA` array at the top of the script — sections, each with an `items` list. Add, remove and reorder freely; counts and the tick strip recompute themselves.

One caveat: progress is stored as **positions in the list**, so inserting an issue in the middle shifts everything after it and saved progress will point at the wrong issues. Append at the end where you can. `HOW-IT-WORKS.md` covers the fix if you need to restructure properly.

## Credits

Reading order compiled from [Comic Book Herald](https://www.comicbookherald.com/), [Crushing Krisis](https://crushingkrisis.com/) and [How To Love Comics](https://www.howtolovecomics.com/). The *Fantastic Four*/*FF* weave follows the order Hickman specified for the omnibus.

Comics and characters are Marvel's. This is an index of issue numbers, not a reader.

## License

MIT.
