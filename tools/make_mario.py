#!/usr/bin/env python3
"""Generate properties/mario.json.

    python3 tools/make_mario.py

The Super Mario mainline platformers in release order, 2D and 3D — Super
Mario Bros. through Wonder, the Lost Levels and the handheld Land/World
games included.

Which games count and their release years come from Wikipedia's Super Mario
series article (scratch/agent-games1/wiki/mario.wiki; the series list is the
authority). Hours are HowLongToBeat main-story figures — story only, the
house standard — read from tools/data/mario.json, collected by
scratch/agent-games1/fetch_hltb.py and verified by name: this generator
refuses a record whose name is not what it expects, and cross-checks HLTB's
release year against Wikipedia's.

Scope cut, on purpose: mainline platformers only. No RPGs, no karts, no
parties, no sports, no Maker, no Run — the note says so. Bowser's Fury is an
add-on campaign on the Switch release of 3D World, not a series entry, and
rides as a note on that row.
"""
import json
import pathlib

SLUG = "mario"

# key in the data file, display title, Wikipedia year, note
ROSTER_2D = [
    ("smb", "Super Mario Bros.", 1985,
     "NES. Where the whole grammar starts — run right, jump well."),
    ("lost-levels", "Super Mario Bros.: The Lost Levels", 1986,
     "Japan's SMB2 — the same engine, tuned cruel. Reached the west in "
     "All-Stars."),
    ("smb2", "Super Mario Bros. 2", 1988,
     "The western sequel, rebuilt from Doki Doki Panic — four characters, "
     "throwable turnips"),
    ("smb3", "Super Mario Bros. 3", 1988,
     "The overworld map, the suits, and the high-water mark of the NES"),
    ("land", "Super Mario Land", 1989,
     "Game Boy launch, made without Miyamoto — tiny and strange"),
    ("world", "Super Mario World", 1990,
     "SNES launch. Dinosaur Land, the cape, and Yoshi's debut."),
    ("land2", "Super Mario Land 2: 6 Golden Coins", 1992,
     "Wario's debut, as the villain who stole the castle"),
    ("nsmb", "New Super Mario Bros.", 2006,
     "DS. Side-scrolling Mario returns after a fourteen-year gap."),
    ("nsmb-wii", "New Super Mario Bros. Wii", 2009,
     "Four players on one couch, chaos included"),
    ("nsmb2", "New Super Mario Bros. 2", 2012,
     "3DS. The coin-obsessed one."),
    ("nsmb-u", "New Super Mario Bros. U", 2012,
     "Wii U launch; the Switch Deluxe re-release is the easy way to it now"),
    ("wonder", "Super Mario Bros. Wonder", 2023,
     "Switch. The Wonder Flower bends every level once; the elephant is "
     "real."),
]

ROSTER_3D = [
    ("sm64", "Super Mario 64", 1996,
     "N64. The 3D template — for the series and for everyone else."),
    ("sunshine", "Super Mario Sunshine", 2002,
     "GameCube. Isle Delfino and the FLUDD pack; the prickly one."),
    ("galaxy", "Super Mario Galaxy", 2007,
     "Wii. Gravity as level design."),
    ("galaxy2", "Super Mario Galaxy 2", 2010,
     "Built from the ideas Galaxy had no room for — leaner and harder"),
    ("3d-land", "Super Mario 3D Land", 2011,
     "3DS. 3D Mario distilled into handheld courses."),
    ("3d-world", "Super Mario 3D World", 2013,
     "Wii U, four players, the cat suit; the Switch release added the "
     "Bowser's Fury side campaign"),
    ("odyssey", "Super Mario Odyssey", 2017,
     "Switch. The capture hat and the open moons."),
]

SECTIONS = [
    ("d2", "The 2D line",
     "Side-scrolling Mario, NES to Switch — the series' spine in its "
     "original plane.", ROSTER_2D),
    ("d3", "The 3D line",
     "Seven games since 1996, no two built alike.", ROSTER_3D),
]

def norm(s):
    s = (s or "").replace("’", "'").replace("–", "-")
    return " ".join(s.casefold().split())


def main():
    data = json.loads((pathlib.Path(__file__).resolve().parent / "data"
                       / "mario.json").read_text(encoding="utf-8"))

    sections = []
    for sec_id, sec_title, intro, roster in SECTIONS:
        years = [y for _, _, y, _ in roster]
        assert years == sorted(years), "%s roster out of release order" % sec_id
        items = []
        for key, title, year, note in roster:
            rec = data.get(key)
            assert rec, "no HLTB record for %s" % key
            assert norm(rec["name"]) == norm(title), \
                "record mismatch for %s: %r" % (key, rec["name"])
            assert abs(int(rec["year"]) - year) <= 1, \
                "year mismatch for %s: wiki %d, hltb %s" % (key, year, rec["year"])
            x = {"id": "mario-%s" % key, "t": title, "n": str(year),
                 "w": rec["main_h"]}
            if note:
                x["note"] = note
            items.append(x)
        hours = sum(x["w"] for x in items)
        sections.append({
            "id": sec_id, "title": sec_title,
            "sub": "%d–%d · %d games · %d hours story"
                   % (years[0], years[-1], len(items), round(hours)),
            "intro": intro,
            "items": items,
        })
    sections[0]["open"] = True

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert len(ids) == len(ROSTER_2D) + len(ROSTER_3D) == 19, (len(ids),)

    hours = sum(x["w"] for s in sections for x in s["items"])

    prop = {
        "slug": SLUG,
        "title": "Super Mario",
        "subtitle": "the mainline platformers in release order, 2D and 3D",
        "kind": "games",
        "popularity": 94,
        "year": "1985–",
        "blurb": "All %d mainline platformers, Super Mario Bros. to Wonder "
                 "— about %d hours of story." % (len(ids), round(hours)),
        "unit": {"one": "game", "many": "games"},
        "verb": {"base": "play", "past": "played", "ing": "playing"},
        "itemOrder": "number-first",
        "accent": "#C7231E",
        "accentDark": "#5C94FC",
        "tiers": False,
        "notes": [
            ["Platformers only.", "This is the Super Mario series proper — "
             "the games where you run and jump. No RPGs, no karts, no "
             "parties, no sports, no Maker, no Run. Remakes and "
             "compilations (All-Stars, 3D All-Stars, the Advance ports) "
             "aren't separate rows; play any version and tick the "
             "original."],
            ["Two lines, one release order.", "The 2D and 3D games sit in "
             "their own sections because they are different crafts, each "
             "in release order. Almost nothing carries over between games "
             "— start anywhere, though 1985 is a fine place."],
            ["Hours are story only.", "HowLongToBeat main-story figures — "
             "credits, not completion. Odyssey's moons and Wonder's "
             "badges can double the number; that is on you."],
            "Game list and years from Wikipedia's Super Mario series "
            "article; hours from HowLongToBeat main-story figures, "
            "verified by name.",
        ],
        "sections": sections,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json" % SLUG)
    print("  %d sections, %d games, %d hours story"
          % (len(sections), len(ids), round(hours)))
    for s in sections:
        print("   %-14s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
