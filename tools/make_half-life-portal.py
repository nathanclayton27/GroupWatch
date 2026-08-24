#!/usr/bin/env python3
"""Generate properties/half-life-portal.json.

    python3 tools/make_half-life-portal.py

Valve's story canon in release order: Half-Life and its two expansion
campaigns, Half-Life 2 and the Episodes, Alyx, and the two Portals — one
universe, two sections.

Which games exist and their release years come from Wikipedia's Half-Life
(series) and Portal (series) articles (scratch/agent-games1/wiki/). Hours
are HowLongToBeat main-story figures — story only, the house standard —
read from tools/data/half-life-portal.json, collected by
scratch/agent-games1/fetch_hltb.py and verified by name (this generator
refuses a record whose name is not what it expects, and cross-checks HLTB's
release year against Wikipedia's).

Alyx's VR requirement is stated as fact on the row. Uplink, Decay, Lost
Coast and the third-party Portal mods are not rows — notes say why.
"""
import json
import pathlib

SLUG = "half-life-portal"

# key in the data file, display title, Wikipedia year, note, opt
HALF_LIFE = [
    ("hl1", "Half-Life", 1998,
     "Black Mesa, the crowbar, and the silent physicist. The fan-built "
     "Black Mesa remake is a fine modern substitute — ticking it counts.",
     0),
    ("opposing-force", "Half-Life: Opposing Force", 1999,
     "Gearbox's expansion — the incident again, as a soldier sent to "
     "clean it up", 1),
    ("blue-shift", "Half-Life: Blue Shift", 2001,
     "The second expansion — the incident a third time, as a security "
     "guard", 1),
    ("hl2", "Half-Life 2", 2004,
     "City 17, the gravity gun, and the Combine."),
    ("episode-one", "Half-Life 2: Episode One", 2006,
     "Short, and straight out of the citadel", 0),
    ("episode-two", "Half-Life 2: Episode Two", 2007,
     "The one that ends mid-sentence — and stayed there thirteen years",
     0),
    ("alyx", "Half-Life: Alyx", 2020,
     "VR only, as a matter of fact — it requires a headset. Set five "
     "years before Half-Life 2; its ending re-opens Episode Two's.", 0),
]

PORTAL = [
    ("portal", "Portal", 2007,
     "Three hours of GLaDOS, shipped in the same Orange Box as Episode "
     "Two", 0),
    ("portal2", "Portal 2", 2011,
     "Longer, funnier, and the fuller story of Aperture", 0),
]

SECTIONS = [
    ("half-life", "Half-Life",
     "Gordon Freeman's war in release order — the expansions are other "
     "eyes on the same incident, optional.", HALF_LIFE),
    ("portal", "Portal",
     "Aperture Science, elsewhere in the same universe — two games, no "
     "homework required.", PORTAL),
]


def norm(s):
    s = (s or "").replace("’", "'").replace("–", "-")
    return " ".join(s.casefold().split())


def main():
    data = json.loads((pathlib.Path(__file__).resolve().parent / "data"
                       / "half-life-portal.json").read_text(encoding="utf-8"))

    sections = []
    for sec_id, sec_title, intro, roster in SECTIONS:
        years = [r[2] for r in roster]
        assert years == sorted(years), "%s roster out of release order" % sec_id
        items = []
        for row in roster:
            key, title, year, note = row[0], row[1], row[2], row[3]
            opt = row[4] if len(row) > 4 else 0
            rec = data.get(key)
            assert rec, "no HLTB record for %s" % key
            assert norm(rec["name"]) == norm(title), \
                "record mismatch for %s: %r" % (key, rec["name"])
            assert abs(int(rec["year"]) - year) <= 1, \
                "year mismatch for %s: wiki %d, hltb %s" % (key, year, rec["year"])
            x = {"id": "hlp-%s" % key, "t": title, "n": str(year),
                 "w": rec["main_h"]}
            if note:
                x["note"] = note
            if opt:
                x["opt"] = 1
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
    assert len(ids) == len(HALF_LIFE) + len(PORTAL) == 9, (len(ids),)

    hours = sum(x["w"] for s in sections for x in s["items"])

    prop = {
        "slug": SLUG,
        "title": "Half-Life & Portal",
        "subtitle": "Valve's story canon in release order",
        "kind": "games",
        "popularity": 71,
        "year": "1998–",
        "blurb": "%d games in one universe — about %d hours of story, "
                 "cliffhanger included." % (len(ids), round(hours)),
        "unit": {"one": "game", "many": "games"},
        "verb": {"base": "play", "past": "played", "ing": "playing"},
        "itemOrder": "number-first",
        "accent": "#CC6A00",
        "accentDark": "#3D9BE8",
        "tiers": False,
        "notes": [
            ["One universe, two doors.", "Portal happens in the same world "
             "as Half-Life — Aperture Science to Black Mesa's east — and "
             "either section works as a way in. Playing Portal 2 before "
             "the Half-Life games spoils nothing; the nods only land "
             "harder the other way around."],
            ["The expansions are optional.", "Opposing Force and Blue "
             "Shift replay the Black Mesa incident from other posts — "
             "worthwhile, skippable, and marked as such."],
            ["Alyx is VR, full stop.", "It requires a VR headset; there "
             "is no flat-screen version from Valve. It sits last in "
             "release order and earns the spot — its ending rewrites the "
             "cliffhanger Episode Two left."],
            ["Hours are story only.", "HowLongToBeat main-story figures. "
             "Not rows: Uplink and Lost Coast are demos, Decay was a "
             "PS2-only co-op extra, and the Portal fan campaigns are "
             "other people's games."],
            "Game lists and years from Wikipedia's Half-Life (series) and "
            "Portal (series) articles; hours from HowLongToBeat "
            "main-story figures, verified by name.",
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
        print("   %-12s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
