# GroupWatch

A group tracker for anything you work through in order — a comic run, an anime,
a show, a film series.

Tick off what you've read or watched. Share a six-character code and everyone's
progress stacks onto a single strip, a colour per person, so you can see at a
glance who's ahead and who's fallen behind.

**[Open it →](https://nathanclayton27.github.io/groupwatch/)**

## What's in it

**Fullmetal Alchemist: Brotherhood** — HD DVD Anime Club Round 4. 64 episodes
across six arcs on the club schedule, 15 July to 25 August 2026.

**Everything Dies** — Jonathan Hickman's Marvel run. 250 issues from *Fantastic
Four* #570 through *Secret Wars* #9, in the order they're meant to be read.

The button in the top left switches between them. First visit shows a picker;
after that it opens whatever you had last.

## Reading groups

Sign in, name yourself, then either create a group or enter a code someone sent
you. Codes are six characters with no `0`, `O`, `1` or `I`, so they survive
being read aloud.

Once you're in a group the strip changes: instead of your progress alone it
draws one layer per person, stacked, sorted so whoever's furthest sits on top.
Colours identify people; the legend names them.

**Joining a group makes your progress readable by the people in it** — for that
property only. That's what the shared strip is. Leaving ends it.

## Schedules

A property can carry a real schedule of dated windows, each with a cumulative
target. FMA:B has one: through episode 20 by 28 July, through 30 by 4 August,
and so on.

Behind is measured against the last window that has **closed**, not interpolated
inside the open one — you have until a window's end date, and finishing early
buys you off days. Two markers appear on the strip: a solid rule at what's
overdue, a lighter one at the current window's goal.

A group's creator can slide the whole schedule forward or back. Every arc moves
together, so the pace is unchanged and only the dates differ.

## Adding a property

Drop a JSON file in `properties/` and rebuild.

```json
{
  "slug": "must-match-the-filename",
  "title": "Some Show",
  "kind": "anime",
  "year": "2019",
  "blurb": "One sentence for the picker.",
  "unit": { "one": "episode", "many": "episodes" },
  "accent": "#B0472E",
  "tiers": false,
  "sections": [
    { "id": "s1", "title": "Season 1", "sub": "episodes 1–12",
      "items": [ { "id": "show-1", "t": "Episode", "n": "1" } ] }
  ]
}
```

Optional: `schedule` (dated windows), `rules` (house rules panel), `notes`
(footer prose), `order` (menu position), per-section `intro` and `links`,
per-item `note`, `star`, `opt`, `url`.

**Item ids are load-bearing.** Progress is stored as a list of them, so
reordering is safe but renaming silently destroys saved ticks. Prefix them with
the property slug. The build fails on duplicates.

```bash
python3 src/build.py          # validates properties, writes the manifest
python3 -m http.server 8000
```

Serve it over http. Property data is fetched at runtime and `file://` blocks
fetch.

## Setting up the backend

Optional. Without it everything works, progress just doesn't sync across
devices.

1. Create a project at [supabase.com](https://supabase.com).
2. In the SQL editor, run [`schema.sql`](schema.sql). *Migrating an existing
   single-property install instead? Run
   [`migrate-to-multiproperty.sql`](migrate-to-multiproperty.sql).*
3. Authentication → URL Configuration: set **Site URL** to your Pages URL and
   add it under **Redirect URLs**. Add `http://localhost:8000/**` too, or local
   sign-in bounces to production.
4. Fill in `SUPABASE_URL` and `SUPABASE_ANON_KEY` at the top of the script in
   `src/template.html`.

Commit both — the anon key is meant to be public, and the row-level security
policies are what actually protect the data. Every query runs as the signed-in
user.

Sign-in is a magic link by default. Supabase's built-in mailer allows only about
two auth emails an hour, which is not enough to test a group with two accounts —
enable the GitHub provider and set `ENABLE_GITHUB_LOGIN = true` instead. The
callback URL is `https://<project-ref>.supabase.co/auth/v1/callback`.

## Credits

Hickman reading order compiled from [Comic Book
Herald](https://www.comicbookherald.com/), [Crushing
Krisis](https://crushingkrisis.com/) and [How To Love
Comics](https://www.howtolovecomics.com/); the *Fantastic Four*/*FF* weave
follows the order Hickman specified for the omnibus.

This is an index of issue and episode numbers, not a reader or a player.

## License

MIT.
