#!/usr/bin/env python3
"""Generate properties/fallout.json.

    python tools/make_fallout.py

The mainline Fallout games in release order, the major story DLC for 3, New
Vegas and 4 as optional rows with their own hours, and the two early-2000s
spin-offs in an optional classics sidebar.

The game list and years were machine-read from Wikipedia (the franchise
article plus the Fallout 3 DLC, New Vegas and Fallout 4 articles —
scratch/agent-games2/verify_wiki.py). Hours are HowLongToBeat main-story
figures — story only, the house standard — read from tools/data/fallout.json,
collected by scratch/agent-games2/fetch_hltb.py and verified by name and
year there; this generator refuses a record whose name is not what it
expects. Only DLC that HLTB carries as its own entry got a row.

Tiers:
  1  the mainline single-player games — 1, 2, 3, New Vegas, 4
  2  the story DLC, each with its own hours
  3  the classics sidebar and 76
"""
import json
import pathlib

SLUG = "fallout"

# id, data key, expected HLTB name, display year, section, tier, note, opt
# (HLTB suffixes some DLC entries with a literal " DLC" — inconsistently, so
# the check strips it rather than expecting it)
ROSTER = [
    ("fo-1", "fo1", "Fallout", 1997, "originals", 1,
     "The isometric Interplay original — turn-based, talky, and still the "
     "foundation everything later stands on", 0),
    ("fo-2", "fo2", "Fallout 2", 1998, "originals", 1,
     "Bigger, stranger, direct sequel", 0),
    ("fo-tactics", "tactics", "Fallout Tactics: Brotherhood of Steel", 2001,
     "classics", 3,
     "Squad-tactics spin-off by Micro Forté — combat missions rather than "
     "an RPG, and loosely attached to the main line", 1),
    ("fo-bos", "fobos", "Fallout: Brotherhood of Steel", 2004, "classics", 3,
     "The console action spin-off, Interplay's last — outside the main "
     "line", 1),
    ("fo-3", "fo3", "Fallout 3", 2008, "capital", 1,
     "The Bethesda reinvention — first person, the Capital Wasteland", 0),
    ("fo-3-anchorage", "fo3-anchorage", "Fallout 3: Operation Anchorage",
     2009, "capital", 2, "Simulation combat detour", 1),
    ("fo-3-pitt", "fo3-pitt", "Fallout 3: The Pitt", 2009, "capital", 2,
     "Industrial Pittsburgh, and the DLC with the dilemma", 1),
    ("fo-3-broken-steel", "fo3-broken-steel", "Fallout 3: Broken Steel",
     2009, "capital", 2,
     "Continues past the main quest's end and raises the level cap — the "
     "one most worth it", 1),
    ("fo-3-point-lookout", "fo3-point-lookout",
     "Fallout 3: Point Lookout", 2009, "capital", 2,
     "The swamp, and the best-regarded of the five", 1),
    ("fo-3-zeta", "fo3-zeta", "Fallout 3: Mothership Zeta", 2009,
     "capital", 2, "The alien abduction one", 1),
    ("fo-nv", "fnv", "Fallout: New Vegas", 2010, "mojave", 1,
     "Obsidian's Mojave — many hands from the Interplay originals, and "
     "most people's favourite", 0),
    ("fo-nv-dead-money", "fnv-dead-money",
     "Fallout: New Vegas - Dead Money", 2010, "mojave", 2,
     "The heist in the Sierra Madre — starts the four-part DLC arc", 1),
    ("fo-nv-honest-hearts", "fnv-honest-hearts",
     "Fallout: New Vegas - Honest Hearts", 2011, "mojave", 2,
     "Zion National Park", 1),
    ("fo-nv-owb", "fnv-owb", "Fallout: New Vegas - Old World Blues",
     2011, "mojave", 2, "The science one, and the funniest", 1),
    ("fo-nv-lonesome-road", "fnv-lonesome-road",
     "Fallout: New Vegas - Lonesome Road", 2011, "mojave", 2,
     "Closes the courier's story — play it last", 1),
    ("fo-4", "fo4", "Fallout 4", 2015, "boston", 1,
     "The Commonwealth", 0),
    ("fo-4-automatron", "fo4-automatron", "Fallout 4: Automatron", 2016,
     "boston", 2, "The short robot questline", 1),
    ("fo-4-far-harbor", "fo4-far-harbor", "Fallout 4: Far Harbor", 2016,
     "boston", 2, "The Maine island — Fallout 4's biggest story add-on", 1),
    ("fo-4-nuka-world", "fo4-nuka-world", "Fallout 4: Nuka-World", 2016,
     "boston", 2, "The raider theme park, and the last story DLC", 1),
    ("fo-76", "fo76", "Fallout 76", 2018, "boston", 3,
     "Online and ongoing — multiplayer Appalachia, patched into having a "
     "story after launch. Optional by nature.", 1),
]

SECTIONS = [
    ("originals", "The Interplay originals",
     "Isometric, turn-based, and shorter than their reputation suggests."),
    ("classics", "The classics sidebar",
     "The two early-2000s spin-offs, here for the record — neither is "
     "anyone's homework."),
    ("capital", "Fallout 3",
     "The Bethesda era opens. The five DLC are optional rows with their "
     "own hours."),
    ("mojave", "New Vegas",
     "Obsidian's year-later miracle and its four-part DLC arc."),
    ("boston", "Fallout 4 to 76",
     "The Commonwealth, its three story add-ons, and the online one."),
]


def norm(s):
    s = (s or "").replace("’", "'").replace("–", "-").replace("—", "-")
    s = " ".join(s.casefold().split())
    return s[:-4] if s.endswith(" dlc") else s


def main():
    data = json.loads((pathlib.Path(__file__).resolve().parent / "data"
                       / "fallout.json").read_text(encoding="utf-8"))

    rows = {}
    used = set()
    for iid, key, expect, year, sec, tier, note, opt in ROSTER:
        rec = data.get(key)
        assert rec, "no HLTB record for %s" % key
        assert norm(rec["name"]) == norm(expect), \
            "record mismatch for %s: %r" % (key, rec["name"])
        assert abs(int(rec["year"]) - year) <= 1, \
            "year mismatch for %s: wiki %d, hltb %s" % (key, year, rec["year"])
        used.add(key)
        w = rec["main_h"] if rec["main_h"] else 0
        x = {"id": iid, "t": expect, "n": str(year), "w": w, "tier": tier,
             "sec": sec, "year": year}
        if note:
            x["note"] = note
        if opt:
            x["opt"] = 1
        rows.setdefault(sec, []).append(x)
    assert used == set(data), "cache keys unused: %r" % (set(data) - used)

    sections = []
    for key, title, intro in SECTIONS:
        got = rows[key]
        assert got == sorted(got, key=lambda e: e["year"]), key
        hours = sum(e["w"] for e in got)
        span = ("%d" % got[0]["year"] if got[0]["year"] == got[-1]["year"]
                else "%d–%d" % (got[0]["year"], got[-1]["year"]))
        sec = {"id": key, "title": title,
               "sub": "%s · %d %s · %d hours story"
                      % (span, len(got),
                         "entry" if len(got) == 1 else "entries",
                         round(hours)),
               "intro": intro,
               "items": [{k: v for k, v in e.items()
                          if k in ("id", "t", "n", "w", "tier", "opt", "note")}
                         for e in got]}
        if key == "originals":
            sec["open"] = True
        sections.append(sec)

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert len(ids) == len(ROSTER) == 20, (len(ids),)
    tiers = {t: [x for s in sections for x in s["items"] if x["tier"] == t]
             for t in (1, 2, 3)}
    assert len(tiers[1]) == 5, "mainline should be 5, got %d" % len(tiers[1])
    assert len(tiers[2]) == 12, "story DLC should be 12, got %d" % len(tiers[2])
    assert len(tiers[3]) == 3, "tier 3 should be 3, got %d" % len(tiers[3])

    hours = sum(x["w"] for s in sections for x in s["items"])
    spine = sum(x["w"] for x in tiers[1])

    prop = {
        "slug": SLUG,
        "title": "Fallout",
        "subtitle": "the mainline games in release order, story DLC included",
        "kind": "games",
        "popularity": 78,
        "year": "1997–",
        "blurb": "5 mainline games, 12 story DLC and 3 asides — about %d "
                 "hours of story, %d of it the mainline." % (round(hours),
                                                             round(spine)),
        "unit": {"one": "game", "many": "games"},
        "verb": {"base": "play", "past": "played", "ing": "playing"},
        "itemOrder": "number-first",
        "accent": "#23538F",
        "accentDark": "#D9A045",
        "tiers": True,
        "itemTiers": True,
        "paceTiers": [1],
        "paceLabel": "the DLC, the classics sidebar and 76",
        "notes": [
            ["Release order, five games of spine.", "Every Fallout is a "
             "fresh start — new wasteland, new lead — so nothing here "
             "requires anything else. The order is when they came out; the "
             "connections are texture, not homework."],
            ["The DLC rows are real entries.", "Only add-ons HowLongToBeat "
             "tracks as separate games got rows: Fallout 3's five, New "
             "Vegas's four-part arc, and Fallout 4's three story add-ons. "
             "Fallout 4's workshop packs add no story and are not listed. "
             "All DLC is optional and each row carries its own hours."],
            ["The classics sidebar.", "Fallout Tactics (2001) is a "
             "squad-tactics spin-off, Brotherhood of Steel (2004) a console "
             "action game — the two Interplay-era side roads, listed "
             "factually and skippable freely."],
            ["76 is its own animal.", "Online, multiplayer and ongoing; the "
             "hours shown are its main questline as HLTB measures it, not "
             "an ending in the single-player sense."],
            ["Hours are story only.", "HowLongToBeat main-story figures — "
             "the critical path, no side quests. These are games built for "
             "wandering, so treat every number as a floor."],
            "Game list and years from Wikipedia's Fallout articles; hours "
            "from HowLongToBeat main-story figures, matched by name and "
            "year.",
        ],
        "sections": sections,
    }

    out = (pathlib.Path(__file__).resolve().parent.parent / "properties"
           / ("%s.json" % SLUG))
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json" % SLUG)
    print("  %d sections, %d rows, %d hours (%d mainline)"
          % (len(sections), len(ids), round(hours), round(spine)))
    for s in sections:
        print("   %-26s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
