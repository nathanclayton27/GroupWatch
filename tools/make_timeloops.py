#!/usr/bin/env python3
"""Generate properties/time-loops.json — the group's Groundhog Day collection.

    python3 tools/make_timeloops.py

Films and single episodes built on the same day happening again, assembled in
the group's Discord thread and grown a little here. Every entry was verified
against Wikipedia before it got a row — scratch/loops/collect.py resolved the
films to Wikidata runtimes and read each episode's season and number out of
its own article or season list, which is how the Tales of the Walking Dead
entry became "Blair / Gina" S1E2 rather than the episode a contributor half
remembered.

House additions — entries the site added beyond the thread — are marked, so
the group can veto them. Nothing is weighted: a 32-minute short, a 101-minute
film and a 45-minute episode all count one, because this is a grab bag, not a
schedule.
"""
import json
import pathlib

SLUG = "time-loops"

# (title, year, runtime min, note, house_addition)
FILMS = [
    ("Groundhog Day", 1993, 101, "Where the name comes from", 0),
    ("12:01", 1993, 92, "The TV movie that aired the same year — its short-film "
     "ancestor predates Groundhog Day", 1),
    ("Run Lola Run", 1998, 81, "Three runs at twenty minutes", 0),
    ("Triangle", 2009, 99, "The horror one people argue about", 1),
    ("Source Code", 2011, 93, "Eight minutes at a time", 0),
    ("Edge of Tomorrow", 2014, 113, "", 0),
    ("ARQ", 2016, 98, "", 0),
    ("Before I Fall", 2017, 99, "", 1),
    ("Happy Death Day", 2017, 96, "The loop as a slasher", 0),
    ("The Endless", 2017, 111, "Loops inside loops, on a cult compound", 1),
    ("Happy Death Day 2U", 2019, 100, "", 0),
    ("Palm Springs", 2020, 90, "", 0),
    ("Boss Level", 2020, 104, "", 0),
    ("Two Distant Strangers", 2020, 32, "The Oscar-winning short", 0),
    ("A Map of Tiny Perfect Things", 2021, 99, "", 0),
]

# (show, episode title, S, E, year, note, house_addition)
EPISODES = [
    ("Star Trek: The Next Generation", "Cause and Effect", 5, 18, 1992, "", 0),
    ("Xena: Warrior Princess", "Been There, Done That", 3, 2, 1997, "", 1),
    ("The X-Files", "Monday", 6, 14, 1999, "", 0),
    ("Stargate SG-1", "Window of Opportunity", 4, 6, 2000, "", 0),
    ("Buffy the Vampire Slayer", "Life Serial", 6, 5, 2001, "", 1),
    ("Supernatural", "Mystery Spot", 3, 11, 2008, "", 0),
    ("Fringe", "White Tulip", 2, 18, 2010, "", 1),
    ("Doctor Who", "Heaven Sent", 9, 11, 2015, "", 0),
    ("Legends of Tomorrow", "Here I Go Again", 3, 11, 2018, "", 0),
    ("Agents of S.H.I.E.L.D.", "As I Have Always Been", 7, 9, 2020, "", 0),
    ("Tales of the Walking Dead", "Blair / Gina", 1, 2, 2022,
     "The series' time-loop episode", 0),
]


def slug(t):
    keep = "".join(c.lower() if c.isalnum() else "-" for c in t)
    while "--" in keep:
        keep = keep.replace("--", "-")
    return keep.strip("-")


HOUSE = "Added here — shout if it doesn't belong"


def main():
    film_items = []
    for t, year, mins, note, house in sorted(FILMS, key=lambda f: (f[1], f[0])):
        bits = [b for b in (note, "%d min" % mins, HOUSE if house else "") if b]
        film_items.append({
            "id": "loop-f-%d-%s" % (year, slug(t)),
            "t": t, "n": str(year), "note": " · ".join(bits),
        })

    ep_items = []
    for show, t, s, e, year, note, house in sorted(EPISODES, key=lambda x: (x[4], x[0])):
        bits = [b for b in (note, HOUSE if house else "") if b]
        ep_items.append({
            "id": "loop-e-%d-%s" % (year, slug(show + "-" + t)),
            "t": "%s — “%s”" % (show, t), "n": "S%dE%d" % (s, e),
            **({"note": " · ".join(bits)} if bits else {}),
        })

    sections = [
        {"id": "films", "title": "The films",
         "sub": "1993–2021 · %d films, one of them a short" % len(FILMS),
         "open": True, "items": film_items},
        {"id": "episodes", "title": "Single episodes",
         "sub": "1992–2022 · %d shows, one loop each" % len(EPISODES),
         "intro": "One episode per show — the season and number are on the "
                  "row, so nobody has to watch anything else to get there.",
         "items": ep_items},
        {"id": "series", "title": "A whole series about it",
         "sub": "when one episode was never going to be enough",
         "items": [{"id": "loop-s-2019-russian-doll", "t": "Russian Doll",
                    "n": "2019–22",
                    "note": "Two seasons; the first is the loop"}]},
    ]

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert len(ids) == len(FILMS) + len(EPISODES) + 1, len(ids)
    house = sum(1 for s in sections for x in s["items"]
                if HOUSE in (x.get("note") or ""))
    assert house == sum(f[4] for f in FILMS) + sum(e[6] for e in EPISODES)

    prop = {
        "slug": SLUG,
        "title": "Time Loops",
        "subtitle": "the same day, again — films and single episodes",
        "kind": "films & episodes",
        "order": 36,
        "year": "1992–",
        "blurb": "%d films, %d single episodes and one whole series where the "
                 "day repeats. Assembled by the group; watch in any order."
                 % (len(FILMS), len(EPISODES)),
        "unit": {"one": "entry", "many": "entries"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "accent": "#6B2E7A",
        "accentDark": "#C08FE0",
        "tiers": False,
        "random": True,
        "notes": [
            ["No order.", "Nothing here leads to anything else — pick "
             "whatever tonight feels like. Nothing is weighted either: a "
             "32-minute short and a two-hour film count one each, because "
             "this is a grab bag, not a schedule."],
            ["Single episodes stand alone.", "Each row names its show, "
             "season and episode; the loop episodes were built to work cold, "
             "which is most of why people love them."],
            ["House additions are marked.", "%d entries were added beyond "
             "the group's thread and say so on the row — veto freely." % house],
            "Assembled by the group in Discord. Every entry was verified "
            "against Wikipedia before it got a row — including which Tales "
            "of the Walking Dead episode the loop one actually is.",
        ],
        "sections": sections,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json — %d entries (%d house additions)" % (SLUG, len(ids), house))
    for s in sections:
        print("   %-24s %2d  %s" % (s["title"], len(s["items"]), s["sub"][:44]))


if __name__ == "__main__":
    main()
