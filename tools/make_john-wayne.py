#!/usr/bin/env python3
"""Generate properties/john-wayne.json.

    python3 tools/make_john-wayne.py

John Wayne's acting roles in release order, one row per film, from the "As
actor" table of Wikipedia's John Wayne filmography. Same shape as the Nicolas
Cage and Robin Williams lists — era sections, the table's own factual notes
riding along — but three times the length and with a very different problem at
the front of it.

The whole point of this list is the first eleven years. Wayne was a prop man
at Fox who walked through other people's pictures, then a leading man for one
film, then a Poverty Row cowboy who shot eight westerns a year for Monogram.
That is fifty-odd rows before Stagecoach, most of them uncredited, several of
them Mascot serials, four of them gone. **They are all here**, because a
filmography that starts at Stagecoach is a highlight reel, not a filmography.
The rule is stated rather than applied quietly: everything the source's own
table lists is a row.

Three deliberate departures from the table, and only three:

  * The three rows it marks "TV series (Episode: ...)" are out — single
    episodes of other people's television series are not films, the same line
    the Cage list draws. Every short, serial, documentary and walk-on stays.
  * The separate "As himself" and "As producer only" tables are not read.
    Appearances as himself and pictures he only financed are not roles.
  * Alternate titles stay in the row's note. Dozens of these went out abroad
    or on reissue under another name; a second row for The Hawk would pair
    with nothing and count Ride Him, Cowboy twice.

**Unweighted, deliberately.** Runtimes were attempted for every row from one
source — Wikidata's P2047, gated on P577 so a title collision cannot donate a
runtime — and 164 of the 173 have one. The nine that do not are the three
Mascot serials (twelve chapters is not a sitting), a 1927 two-reel short, and
five entries with no article of their own. A partly weighted list is a lying
strip, and dropping nine films to buy a tidy hours figure would cost more than
the figure is worth, so every row weighs the same and the notes say why.
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib.prop import join_bits, slug, write

SLUG = "john-wayne"
DATA = pathlib.Path(__file__).resolve().parent / "data" / "john-wayne.json"

ERAS = [
    ("props", "Prop man and extra", 1926, 1929,
     "He was a Fox prop man who got put in front of the camera when a body "
     "was needed — a Yale football player, a flood extra, a 42nd Highlander. "
     "Almost every row here is uncredited, one is billed as Duke Morrison, "
     "and three of them no longer exist."),
    ("bigtrail", "The Big Trail and the fall", 1930, 1932,
     "Raoul Walsh handed him the lead in a widescreen epic and Fox dropped "
     "him three leads later. What follows is Columbia bit parts, two Mascot "
     "serials and a run of Warner Bros. westerns — the fastest fall in the "
     "list, and the reason for the next five years."),
    ("povertyrow", "Poverty Row", 1933, 1935,
     "Monogram and Lone Star, with a handful of Warner Bros. quickies mixed "
     "in and Republic taking over the last three: eight to eleven pictures a "
     "year, nearly all of them westerns. The densest stretch of the career "
     "by a distance."),
    ("republic", "Republic and Universal", 1936, 1938,
     "Republic westerns, then six pictures for Universal that took him off "
     "the horse — one about truck drivers, one about an ice hockey player — "
     "then back to Republic for the Three Mesquiteers series, which runs on "
     "into the next section."),
    ("stagecoach", "Stagecoach and the war years", 1939, 1945,
     "John Ford finally gave him a lead in February 1939 and everything "
     "changed — though he still owed Republic four more Mesquiteers pictures "
     "that year, which is why they sit right underneath it. Then the war "
     "films: Flying Tigers, The Fighting Seabees, They Were Expendable."),
    ("batjac", "Red River and The Quiet Man", 1946, 1955,
     "Howard Hawks, Ford's cavalry trilogy, an Academy Award nomination for "
     "Sands of Iwo Jima, and Ireland. He starts producing in here too, and "
     "the company he builds is Batjac."),
    ("searchers", "The Searchers to Katie Elder", 1956, 1965,
     "Ten years that open with The Searchers and hold Rio Bravo, Liberty "
     "Valance and two war epics — plus The Alamo, which he directed and "
     "produced as well as starred in."),
    ("shootist", "Rooster Cogburn and out", 1966, 1977,
     "El Dorado, the Oscar for True Grit, the late run of westerns and cop "
     "pictures, and The Shootist to finish. The last row is a 1977 credit he "
     "did not act in."),
]

# The source article's lead: "Wayne starred in his final film, The Shootist,
# in 1976, ending his acting career of 50 years". The table itself does not
# flag it, and the list should.
LAST = ("The Shootist", 1976)


def notebits(r):
    """A row's note: the table's own note, normalized, plus what the film's
    own article says about the print and the format."""
    bits = []
    for raw in (r["tablenote"] or "").split(";"):
        b = raw.strip().rstrip(".")
        if not b:
            continue
        b = re.sub(r"^aka ", "Also released as ", b)
        bits.append(b[0].upper() + b[1:])
    if r.get("serial"):
        n = r.get("chapters")
        bits.append("Serial in %d chapters" % n if n else "Serial")
    # The Oregon Trail's table note already says it is lost, in better words
    # than a generated bit; do not say it twice.
    if r.get("lost") == "lost" and "lost" not in (r["tablenote"] or "").lower():
        bits.append("Lost film — no print is known to survive")
    if (r["t"], r["year"]) == LAST:
        bits.append("His last film")
    return join_bits(*bits)


def main():
    films = json.loads(DATA.read_text(encoding="utf-8"))
    assert len(films) == 173, len(films)
    # The table is already in release order within each year and that order is
    # load-bearing: Stagecoach came out in February 1939, four months before
    # the Mesquiteers pictures that sit under it. Sorting on (year, title) —
    # which the Cage and Williams generators do, because their sources are
    # not ordered inside a year — would put Allegheny Uprising first and make
    # the section intro a lie. So: no re-sort, just a check.
    assert all(a["year"] <= b["year"] for a, b in zip(films, films[1:])), \
        "data file is out of year order"

    sourceable = sum(1 for f in films if f.get("runtime"))
    assert sourceable == 164, sourceable
    # All or nothing. One unsourceable runtime and the whole list goes
    # unweighted, so no row carries `w` and the strip stays honest.
    weighted = sourceable == len(films)
    assert not weighted, "runtimes now complete — reinstate w and the hours"

    lost = [f for f in films if f.get("lost") == "lost"]
    assert len(lost) == 4, [f["t"] for f in lost]

    sections, roster = [], {}
    for key, title, lo, hi, intro in ERAS:
        got = [f for f in films if lo <= f["year"] <= hi]
        assert got, title
        roster[key] = got
        items = []
        for f in got:
            it = {"id": "jw-%d-%s" % (f["year"], slug(f["t"])),
                  "t": f["t"], "n": str(f["year"])}
            note = notebits(f)
            if note:
                it["note"] = note
            if f.get("lost") == "lost":
                # A viewer cannot watch these. Doctor Who's wholly missing
                # serials are marked the same way: the row exists, and the
                # badge says not to wait on it.
                it["opt"] = True
            items.append(it)
        assert all(a["n"] <= b["n"] for a, b in zip(items, items[1:])), title
        sec = {"id": key, "title": title,
               "sub": "%d–%d · %d films" % (got[0]["year"], got[-1]["year"],
                                            len(got)),
               "intro": intro, "items": items}
        if key == "props":
            sec["open"] = True
        sections.append(sec)

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert len(ids) == len(films) == 173, (len(ids), len(films))

    prop = {
        "slug": SLUG,
        "title": "John Wayne",
        "subtitle": "the film roles, in release order",
        "kind": "films",
        "popularity": 72,
        "year": "1926–1977",
        "blurb": "%d films across fifty years — every uncredited walk-on, "
                 "Poverty Row western and Mascot serial the filmography "
                 "lists, from prop man to The Shootist." % len(films),
        "unit": {"one": "film", "many": "films"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "accent": "#A83E2C",
        "accentDark": "#F09070",
        "tiers": False,
        "notes": [
            ["Everything the table lists.", "All 173 rows of Wikipedia's "
             "\"As actor\" filmography, including the uncredited walk-ons of "
             "the Fox years, the two-reel shorts, the Poverty Row westerns "
             "and the three Mascot serials. Nothing is thinned out for being "
             "obscure. Three entries are left out and they are the only "
             "three: the rows the table itself marks as episodes of a "
             "television series. The separate \"as himself\" and "
             "\"producer only\" tables are not roles and are not here."],
            ["Four films cannot be watched.", "Their own articles file them "
             "as lost — no print is known to survive. They keep their row "
             "and are marked optional, because a viewer should be able to "
             "see that the film existed and that this is why it is missing."],
            ["The bars are all one width.", "Runtimes were attempted for "
             "every row from Wikidata and 164 of the 173 have one. The nine "
             "without are the three twelve-chapter serials, a two-reel short "
             "and five entries with no article of their own — so rather than "
             "guess a number or drop a film, this list carries no weights "
             "at all."],
            ["Release order, inside the year too.", "Rows follow the "
             "filmography table's own order rather than being re-sorted "
             "alphabetically, so a film that came out in February sits above "
             "one that came out in June."],
            ["Other titles ride in the note.", "Dozens of these went out "
             "abroad or on reissue under a second name. Where the table "
             "records one it is in the row's note; it never gets a row of "
             "its own."],
            "Filmography from Wikipedia's John Wayne filmography; runtimes "
            "from Wikidata; lost-film and serial status from each film's own "
            "article categories.",
        ],
        "sections": sections,
    }

    out = write(prop)
    print("wrote %s — %d films, unweighted (%d/%d runtimes sourceable)"
          % (out.name, len(ids), sourceable, len(films)))
    for s in sections:
        got = roster[s["id"]]
        rt = sum(1 for f in got if f.get("runtime"))
        print("   %-32s %3d  %-18s %d/%d runtimes"
              % (s["title"], len(s["items"]), s["sub"], rt, len(got)))
    print("   lost: %s" % ", ".join("%s (%d)" % (f["t"], f["year"])
                                    for f in lost))


if __name__ == "__main__":
    main()
