# GroupWatch

A group tracker for anything you work through in order — a comic run, an anime,
a show, a film series.

Tick off what you've read or watched. Share a six-character code and everyone's
progress stacks onto a single strip, a colour per person, so you can see at a
glance who's ahead and who's fallen behind.

**[Open it →](https://nathanclayton27.github.io/groupwatch/)**

## What's in it

Nineteen lists, from an eight-episode show to a 1,190-chapter manga.

**Comics.** *Amazing Spider-Man* (Amazing Fantasy #15 to Civil War), *Civil
War* (the 2006 event interleaved), *Spider-Man After Civil War*, *Ultimate
Marvel* (the whole line, 693 issues), *Everything Dies: Secret Wars*
(Hickman's Marvel run), *Venom* (Cates and Stegman), and *One Piece* in
manga form.

**Screen.** *MCU Anthology* — every Marvel film from *Blade* to *Avengers:
Doomsday* in release order with the shows slotted in — *DC Anthology*, the
live-action equivalent, tracked season by season, and *Studio Ghibli*, every
feature in release order with Miyazaki's as the spine. Plus *Fullmetal
Alchemist: Brotherhood*, *Monster*, *Evangelion*, *One Piece*, *One Pace*,
*Friday Night Lights* and *Lanterns*.

**Games.** *Kingdom Hearts*, in release order, weighted by how long each
entry takes, and *Nasuverse* — Fate, Tsukihime, Melty Blood and the rest,
organised by medium.

The button in the top left switches between them, with a search box. First
visit shows a picker; after that it opens whatever you had last.

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
  "accentDark": "#E8874F",
  "tiers": false,
  "sections": [
    { "id": "s1", "title": "Season 1", "sub": "episodes 1–12",
      "items": [ { "id": "show-1", "t": "Episode", "n": "1" } ] }
  ]
}
```

Optional: `verb` (drives “watching” vs “reading”), `itemOrder`, `schedule`
(dated windows), `rules`, `notes` (footer prose), `order` (menu position),
`forGroup` (per-group copy), `paceTiers` and `paceLabel` (which tiers the
finish date covers), `weightUnit`, `itemTiers`; per-section `intro`, `links`
and `open` (per-section links render inline up to two, then collapse into a
dropdown); per-item `note`, `star`, `opt`, `url`, `w` (how long it takes —
the bars are sized by it) and `tier`. Full reference in
[HOW-IT-WORKS.md](HOW-IT-WORKS.md).

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

Venom order compiled from How To Love Comics, Comic Book Treasury, Comic Book
Herald and comicbookreadingorders.com.

Spider-Man order, era boundaries and star ratings from a checklist written for
the group; its annotations were rewritten rather than copied, because it spoils
freely. Civil War order from How To Love Comics, cross-checked against
comicbookreadingorders.com. Ultimate Marvel order from Comic Book Herald.

MCU Anthology built from Wikipedia's live-action Marvel features table, and DC
Anthology from the equivalent DC film and television tables including the
imprints, with runtimes, release dates and episode counts read from Wikidata.
Studio Ghibli from Wikipedia's List of Studio Ghibli works, with directors,
runtimes and release dates from Wikidata.

Kingdom Hearts order and priorities from a rundown by a longtime player; hours
from HowLongToBeat. Nasuverse assembled from the Type-Moon release history.

This is an index of issue and episode numbers, not a reader or a player.

## License

MIT.
