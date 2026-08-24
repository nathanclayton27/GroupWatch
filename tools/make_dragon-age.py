#!/usr/bin/env python3
"""Generate properties/dragon-age.json.

    python tools/make_dragon-age.py

All four Dragon Age games in release order, with the two expansions
HowLongToBeat tracks as separate entries — Awakening and Trespasser — as
optional rows with their own hours.

The game list and years were machine-read from Wikipedia (the Dragon Age
series article plus the Inquisition article —
scratch/agent-games2/verify_wiki.py). Hours are HowLongToBeat main-story
figures — story only, the house standard — read from
tools/data/dragon-age.json, collected by
scratch/agent-games2/fetch_hltb.py and verified by name and year there;
this generator refuses a record whose name is not what it expects.

Tiers:
  1  the four games
  2  the expansions
"""
import json
import pathlib

SLUG = "dragon-age"

# id, data key, expected HLTB name, display year, section, tier, note, opt
ROSTER = [
    ("da-origins", "origins", "Dragon Age: Origins", 2009, "ferelden", 1,
     "Six openings, one Blight — BioWare in full old-school CRPG mode", 0),
    ("da-awakening", "awakening", "Dragon Age: Origins - Awakening", 2010,
     "ferelden", 2,
     "The expansion — a year on, in Amaranthine", 1),
    ("da-2", "da2", "Dragon Age II", 2011, "ferelden", 1,
     "One city, ten years — a deliberately smaller frame", 0),
    ("da-inquisition", "inquisition", "Dragon Age: Inquisition", 2014,
     "thedas", 1, "The big one — and the sky has a hole in it", 0),
    ("da-trespasser", "trespasser", "Dragon Age: Inquisition - Trespasser",
     2015, "thedas", 2,
     "The epilogue DLC — closes Inquisition's story and points at the "
     "next game; skip it only if you are stopping here", 1),
    ("da-veilguard", "veilguard", "Dragon Age: The Veilguard", 2024,
     "thedas", 1,
     "Ten years later, picking up the thread Trespasser left", 0),
]

SECTIONS = [
    ("ferelden", "Origins to Kirkwall",
     "The Blight and its aftermath — the CRPG and the chamber piece."),
    ("thedas", "Inquisition to Veilguard",
     "The world goes wide, and the long-game plot comes due."),
]


def norm(s):
    s = (s or "").replace("’", "'").replace("–", "-").replace("—", "-")
    s = " ".join(s.casefold().split())
    return s[:-4] if s.endswith(" dlc") else s


def main():
    data = json.loads((pathlib.Path(__file__).resolve().parent / "data"
                       / "dragon-age.json").read_text(encoding="utf-8"))

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
        assert w > 0, "every Dragon Age row needs hours (%s)" % key
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
        sec = {"id": key, "title": title,
               "sub": "%d–%d · %d entries · %d hours story"
                      % (got[0]["year"], got[-1]["year"], len(got),
                         round(hours)),
               "intro": intro,
               "items": [{k: v for k, v in e.items()
                          if k in ("id", "t", "n", "w", "tier", "opt", "note")}
                         for e in got]}
        if key == "ferelden":
            sec["open"] = True
        sections.append(sec)

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert len(ids) == len(ROSTER) == 6, (len(ids),)
    tiers = {t: [x for s in sections for x in s["items"] if x["tier"] == t]
             for t in (1, 2)}
    assert len(tiers[1]) == 4, "games should be 4, got %d" % len(tiers[1])
    assert len(tiers[2]) == 2, "expansions should be 2, got %d" % len(tiers[2])

    hours = sum(x["w"] for s in sections for x in s["items"])
    spine = sum(x["w"] for x in tiers[1])

    prop = {
        "slug": SLUG,
        "title": "Dragon Age",
        "subtitle": "all four games in release order, expansions included",
        "kind": "games",
        "popularity": 58,
        "year": "2009–",
        "blurb": "4 games and 2 expansions — about %d hours of story, %d "
                 "of it the games themselves." % (round(hours), round(spine)),
        "unit": {"one": "game", "many": "games"},
        "verb": {"base": "play", "past": "played", "ing": "playing"},
        "itemOrder": "number-first",
        "accent": "#33567E",
        "accentDark": "#E15A5A",
        "tiers": True,
        "itemTiers": True,
        "paceTiers": [1],
        "paceLabel": "the two expansions",
        "notes": [
            ["One world, new leads.", "Each game hands you a new "
             "protagonist, but the world remembers — companions recur and "
             "choices echo forward. Release order is the intended order; "
             "the Dragon Age Keep site rebuilds your history if you join "
             "late or switch platforms."],
            ["The expansion rows.", "Only the add-ons HowLongToBeat tracks "
             "as separate entries got rows: Awakening and Trespasser, both "
             "optional, both with their own hours. Trespasser is the one "
             "with consequences — it is Inquisition's true ending and the "
             "bridge to The Veilguard. Smaller DLC rides along inside the "
             "modern editions."],
            ["Hours are story only.", "HowLongToBeat main-story figures — "
             "and Inquisition in particular is famous for burying its "
             "story under optional map-clearing. The number shown is the "
             "critical path, not the Hinterlands."],
            "Game list and years from Wikipedia's Dragon Age articles; "
            "hours from HowLongToBeat main-story figures, matched by name "
            "and year.",
        ],
        "sections": sections,
    }

    out = (pathlib.Path(__file__).resolve().parent.parent / "properties"
           / ("%s.json" % SLUG))
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json" % SLUG)
    print("  %d sections, %d rows, %d hours (%d the games)"
          % (len(sections), len(ids), round(hours), round(spine)))
    for s in sections:
        print("   %-26s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
