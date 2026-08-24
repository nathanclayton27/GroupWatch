#!/usr/bin/env python3
"""Generate properties/jojo.json — the David Production anime, part by part.

    python3 tools/make_jojo.py

One row per episode, 190 rows across six parts, one section per part.
Phantom Blood and Battle Tendency share the 2012 season, so their rows keep
that season's continuous numbering (1-9 and 10-26); every later part was
broadcast with its own count and numbers from 1. A note places all six in the
overall numbering.

Episode titles are machine-read from the five Wikipedia season articles by
scratch/jojo/fetch_episodes.py, which asserts every part's numbering complete
and normalises it to the overall 1-190; the committed result is
tools/data/jojo.json. Dual-titled rows keep the original broadcast title, not
the localized rename that dodges the music trademarks.

Nothing is weighted: 190 equal marks, and the part boundaries in the strip do
the rest.
"""
import json
import pathlib

SLUG = "jojo"

# key, title, years — key order is watch order
PARTS = [
    ("pb", "Phantom Blood", "2012"),
    ("bt", "Battle Tendency", "2012–13"),
    ("sc", "Stardust Crusaders", "2014–15"),
    ("diu", "Diamond Is Unbreakable", "2016"),
    ("gw", "Golden Wind", "2018–19"),
    ("so", "Stone Ocean", "2021–22"),
]

# where each part sits in the overall numbering; pb/bt display these numbers
# because they are one 2012 season, later parts display theirs from 1
OVERALL = {"pb": (1, 9), "bt": (10, 26), "sc": (27, 74),
           "diu": (75, 113), "gw": (114, 152), "so": (153, 190)}


def main():
    data = json.loads((pathlib.Path(__file__).resolve().parent / "data"
                       / "jojo.json").read_text(encoding="utf-8"))

    sections = []
    for key, title, years in PARTS:
        lo, hi = OVERALL[key]
        eps = data[key]
        assert [x["o"] for x in eps] == list(range(lo, hi + 1)), \
            "%s: expected overall %d-%d, got %d rows" % (key, lo, hi, len(eps))
        shown = (lambda o: o) if key in ("pb", "bt") else (lambda o: o - lo + 1)
        items = [{"id": "jojo-%s-%d" % (key, shown(x["o"])),
                  "t": x["t"], "n": str(shown(x["o"]))} for x in eps]
        sec = {"id": key, "title": title,
               "sub": "%s · %d episodes" % (years, len(items)),
               "items": items}
        if key == "pb":
            sec["open"] = True
        if key == "bt":
            sec["intro"] = ("The back half of the 2012 season — the "
                            "numbering carries straight on from Phantom "
                            "Blood.")
        sections.append(sec)

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert len(ids) == 190, len(ids)
    counts = {s["id"]: len(s["items"]) for s in sections}
    assert counts == {"pb": 9, "bt": 17, "sc": 48, "diu": 39, "gw": 39,
                      "so": 38}, counts

    prop = {
        "slug": SLUG,
        "title": "JoJo's Bizarre Adventure",
        "subtitle": "every episode of the David Production anime",
        "kind": "anime",
        "popularity": 71,
        "year": "2012–2022",
        "blurb": "All 190 episodes of the David Production anime in order — "
                 "six parts, six JoJos, one bloodline.",
        "unit": {"one": "episode", "many": "episodes"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": "#7A2E5F",
        "accentDark": "#E080BF",
        "tiers": False,
        "notes": [
            ["Each part stands on the last but tells its own story.",
             "A new JoJo, a new era and a mostly new cast every time; "
             "earlier parts pay off later, but every part opens fresh, and "
             "a part boundary is a clean place to pause."],
            ["Where each part sits in the overall numbering.",
             "Phantom Blood is episodes 1–9 and Battle Tendency 10–26 — one "
             "2012 season split between them, so their rows keep that "
             "numbering; Stardust Crusaders runs 27–74, Diamond Is "
             "Unbreakable 75–113, Golden Wind 114–152 and Stone Ocean "
             "153–190, each numbered from 1 as broadcast."],
            ["The manga continues past the anime.",
             "Stone Ocean closes the animated run here; the manga carries "
             "on with Steel Ball Run and JoJolion, and a manga page can "
             "exist later if wanted."],
            "Episode titles machine-read from the five Wikipedia season "
            "articles; every part's numbering is asserted complete before "
            "this builds. Where a release renamed an episode to dodge a "
            "music trademark, the broadcast title stays.",
        ],
        "sections": sections,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json — %d episodes in %d parts"
          % (SLUG, len(ids), len(sections)))
    for s in sections:
        print("   %-24s %3d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
