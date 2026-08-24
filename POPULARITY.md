# Popularity

Every list in `properties/` carries one required field:

```json
"popularity": 83
```

A whole number from 0 to 100. It is the only thing that decides where a list
sits in the catalogue — the splash picker, the card wall, the order the
manifest ships in. It replaced the old hand-assigned `order` field, which the
build now refuses outright.

---

## What the number is

**A documented editorial ranking of how widely known the underlying work is.**
It is a judgement, made by a person, written down where a reviewer can argue
with it in a diff. It is not a measurement, and this file exists so nobody
mistakes it for one.

## What it is explicitly NOT

- **Not view counts.** clubd measures nothing and phones nothing home.
- **Not user data.** No tick, no join, no session anywhere touches this number.
  Nothing a member does moves a list up the catalogue.
- **Not a quality rating.** *Bad Movie Night* is 16 because almost nobody has
  heard of the list, not because the films are bad — although they are.
  *Sight & Sound 100* is 50 and is, by its own poll, the best films ever made.
- **Not a bet on the future.** A brand-new show scores low because it is new
  and unproven, not because it will flop. Raise it later if it lands.
- **Not sacred.** If a value is wrong, change it and say why in the commit.

---

## The scale, and why 0–100

0–100 because it reads as a familiar percentile-shaped band that needs no
legend, and because it is wide enough to seat 124 lists in meaningful groups
without forcing every list to a unique integer. That last part matters: the
old `order` field demanded a unique position per list, which is a second
hand-maintained list of numbers, and it drifted — three pairs of lists ended
up sharing an `order` value and the linter carried a permanent allowlist for
them. Here, **two lists sharing a value is legal and expected.** The build
breaks ties on title, deterministically, so the catalogue never shuffles
between builds.

Pick from the band, then nudge within it. Do not reach for false precision:
the difference between 71 and 72 is noise and everyone should treat it as
noise.

| Band | Means | Examples now |
|---|---|---|
| **90–100** | Household name well outside its own audience. Someone who has never seen a frame can name it. | Star Wars 97, Disney 96, MCU 95, Super Mario 94, The Simpsons 93 |
| **80–89** | Very widely known; a mainstream audience recognises the title on sight. | Dragon Ball 89, James Bond 88, X-Men 86, Fullmetal Alchemist: Brotherhood 83 |
| **70–79** | The canonical "anyone into this has heard of it", with real spill outside the medium. | Ghibli 79, Doctor Who 77, Halo 76, Cowboy Bebop 73 |
| **60–69** | Well known inside its medium or fandom, thin outside it. | Muppets 69, Coen Brothers 67, Gundam 65, Criterion 63 |
| **40–59** | Enthusiast territory: needs a sentence of explanation to a general audience. | Universal Monsters 56, Ultimate Marvel 52, Nasuverse 47, Everything Dies: Secret Wars 44 |
| **25–39** | Deep cut. A subset, a fan project, a thematic survey, or a brand-new thing with no track record. | Urusei Yatsura 38, Time Loops 36, One Pace 33, Lanterns 29 |
| **1–24** | House lists and in-jokes. Made for this group, not for a general audience. | Bad Movie Night 16, the locked list 10 |
| **0** | Unused. Reserved so "no value" can never be confused with "zero". |  |

---

## The signals behind a value

Six things go into it. Three are things you can look up in this repo; three
are judgement calls, and they are labelled as such because pretending
otherwise would be a lie about what this number is.

1. **Cultural footprint of the underlying work — JUDGEMENT.** The dominant
   signal, and the one that cannot be measured from here. It is informed by
   observable public facts — whether a work ran on network television for a
   decade, took a major award, anchored a billion-dollar film series, is
   stocked in ordinary bookshops — but the number itself is a person's read of
   how far the name travels. Nobody here has audience data, and nobody should
   write a value as though they do.
2. **Flagship or derived cut — MEASURABLE from this repo.** When two lists
   cover the same franchise, the one carrying the primary line scores higher
   than the one carrying a subset, spin-off or recut. *One Piece* 91 over
   *One Piece (manga)* 80 over *One Pace* 33 (a fan recut of the first).
   *James Bond* 88 over *James Bond Games* 40. *Amazing Spider-Man* 87 over
   *Spider-Man After Civil War* 37. You can check this by reading the
   catalogue; it is not an opinion.
3. **Where the more-consumed medium sits — JUDGEMENT.** Where a franchise has
   two flagship-ish lists in different media, the more widely consumed medium
   takes the higher number. *Dragon Ball* the anime 89 over the manga 78. This
   is a call, and reasonable people rank it the other way.
4. **Breadth of the list — MEASURABLE.** The entry count that `src/build.py`
   already computes. A mild nudge inside a band, never a driver: a 1,418-row
   *Criterion Collection* is a bigger undertaking than a 6-row *Dragon Age*
   and reads as more of a catalogue centrepiece. It does not promote a list
   into a band it does not otherwise belong in — *Zombie Films* has 605 rows
   and scores 52.
5. **Track record — MEASURABLE from the `year` field.** An open-ended range
   (`"1999–"`) means the thing is still producing; a list whose entire range
   is the current year is brand new and unproven. *Lanterns* (2026, 8
   episodes) is 29 and *President Curtis* (2026, 10 episodes) is 26 for this
   reason alone, and both should be revisited once they have aired.
6. **House or private — MEASURABLE.** A list made for this group rather than
   for a general audience sits in the bottom band: the locked list, and the
   joke-shaped ones. This is a fact about the list's purpose, not a slight.

### What was NOT used as a signal

The old `order` values. The head of that file (roughly the first 30) read as a
genuine curator priority list, but everything below it was clustered by medium
— all the games together, then all the TV, then the books — which carries no
information about how well known anything is. Re-expressing it onto this scale
would have imported the clustering and dressed it up as a ranking. The values
here were assigned from the six signals above and cross-checked against the old
head, not derived from it.

---

## The pins

Two lists open the catalogue regardless of what their popularity says:

```python
# src/build.py
PINNED = ("hickman-secret-wars", "fma-brotherhood")
```

They land at positions 1 and 2. This is a deliberate, visible exception, and it
is a separate mechanism from the number on purpose. The alternative — quietly
writing `"popularity": 99` on both — would have made the data lie in order to
make the constraint come true, and every future reader of `hickman-secret-wars`
would have believed a 250-issue Jonathan Hickman reading order is as widely
known as *Star Wars*. It is not. It scores **44**: comics readers know it,
nobody else does, and without the pin it sorts to position **109 of 124**.
*Fullmetal Alchemist: Brotherhood* scores **83** and sorts to **17**.

Both keep their honest numbers. The pin is the club saying "these go on our
front page anyway", which is a statement about clubd, not about the works.

`tools/qa_lint.py` carries the same list and fails if either pin is missing
from the shipped catalogue's top 6.

---

## Choosing a value for a new list

1. Find the band above. Ask: *who could name this without being told?*
   Everyone → 90s. Anyone who watches films → 70s. Anyone in this specific
   fandom → 60s. People who would have to be told what it is → 40s and below.
2. Check whether the catalogue already carries the franchise. If your list is
   a subset, spin-off, recut or side-medium of one that is already here, it
   goes **below** the one it derives from. Look it up; do not guess.
3. Nudge for size and track record — a couple of points, not a band.
4. Look at three or four neighbours at that value in `properties/index.json`
   and ask whether your list honestly belongs beside them. If it looks
   embarrassing next to them in either direction, move it.
5. Write the number in the generator (`tools/make_<x>.py`), in the same slot
   the other generators use, so re-running it reproduces the JSON exactly.
   Never hand-edit `properties/<slug>.json` for a generated list.
6. Say in the commit message why you picked it. That sentence is the entire
   audit trail this field has.

There is no default and there is no fallback. `src/build.py` fails the build
and `tools/qa_lint.py` reports a finding if the field is missing, is not a
whole number, or falls outside 0–100 — because a list that quietly inherited a
default would sit at one end of the catalogue or the other and nobody would
ever notice it was an accident.

---

## Where it is enforced

| Where | What it does |
|---|---|
| `src/build.py` → `load_property` | Fails the build on a missing, non-integer or out-of-range value, and on any surviving `order` key |
| `src/build.py` → `PINNED` | The pinned head of the catalogue |
| `src/build.py` → the catalogue sort | `(pin, -popularity, title)` |
| `src/build.py` → the manifest | Ships `popularity` on every entry, so the number that produced the order is readable in the artifact it produced |
| `tools/make_secret.py` | Refuses to encrypt a list whose plaintext has no popularity |
| `tools/qa_lint.py` | Reports missing/invalid values, surviving `order` keys, a manifest whose popularities or order have drifted from the files, and either pin falling out of the top 6 |
