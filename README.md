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

**2.** In the SQL editor, run:

```sql
create table progress (
  user_id    uuid primary key references auth.users on delete cascade,
  read_ids   text[] not null default '{}',
  updated_at timestamptz default now()
);

alter table progress enable row level security;

create policy "read own"   on progress for select using (auth.uid() = user_id);
create policy "write own"  on progress for insert with check (auth.uid() = user_id);
create policy "update own" on progress for update using (auth.uid() = user_id)
                                              with check (auth.uid() = user_id);
```

**3.** Authentication → URL Configuration: set **Site URL** to your Pages URL, and add it under **Redirect URLs**.

**4.** In `index.html`, fill in the two constants at the top of the script:

```js
const SUPABASE_URL      = 'https://xxxxx.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbG...';
```

Both are in Supabase under Settings → API. Commit them — the anon key is meant to be public, and the row-level security policies above are what actually protect the data. Every query runs as the signed-in user, and the policies mean a user can only ever reach their own row.

Sign-in is a magic link by default: enter an email, get a link, click it. No passwords anywhere. For GitHub sign-in instead, enable the GitHub provider in Supabase and set `ENABLE_GITHUB_LOGIN = true`.

Supabase's free tier sends a limited number of auth emails per hour. For anything beyond personal use, plug in an SMTP provider under Authentication → Emails.

## Changing the list

The reading order is the `DATA` array at the top of the script — sections, each with an `items` list. Add, remove and reorder freely; counts and the tick strip recompute themselves.

One caveat: progress is stored as **positions in the list**, so inserting an issue in the middle shifts everything after it and saved progress will point at the wrong issues. Append at the end where you can. `HOW-IT-WORKS.md` covers the fix if you need to restructure properly.

## Credits

Reading order compiled from [Comic Book Herald](https://www.comicbookherald.com/), [Crushing Krisis](https://crushingkrisis.com/) and [How To Love Comics](https://www.howtolovecomics.com/). The *Fantastic Four*/*FF* weave follows the order Hickman specified for the omnibus.

Comics and characters are Marvel's. This is an index of issue numbers, not a reader.

## License

MIT.
