#!/usr/bin/env python3
"""Generate properties/elder-scrolls.json.

    python tools/make_elder-scrolls.py

The mainline Elder Scrolls games in release order, the five major expansions
as optional rows with their own hours, the two 1990s adventure detours, and
the MMO as an optional ongoing row.

The game list and years were machine-read from Wikipedia (The Elder Scrolls
article plus the Morrowind, Oblivion and Skyrim articles —
scratch/agent-games2/verify_wiki.py). Hours are HowLongToBeat main-story
figures — story only, the house standard — read from
tools/data/elder-scrolls.json, collected by
scratch/agent-games2/fetch_hltb.py and verified by name and year there;
this generator refuses a record whose name is not what it expects. Only
expansions HLTB carries as their own entries got rows.

Tiers:
  1  the mainline five — Arena, Daggerfall, Morrowind, Oblivion, Skyrim
  2  the major expansions, each with its own hours
  3  the adventure detours and Online
"""
import json
import pathlib

SLUG = "elder-scrolls"

# id, data key, expected HLTB name, display year, section, tier, note, opt
ROSTER = [
    ("tes-arena", "arena", "The Elder Scrolls: Arena", 1994, "dos", 1,
     "Where Tamriel starts — DOS-era, and free from Bethesda these days", 0),
    ("tes-daggerfall", "daggerfall", "The Elder Scrolls II: Daggerfall",
     1996, "dos", 1,
     "The gigantic one, also free now; the fan-built Daggerfall Unity is "
     "the usual way to run it", 0),
    ("tes-battlespire", "battlespire", "An Elder Scrolls Legend: Battlespire",
     1997, "adventures", 3,
     "A dungeon-crawl spin-off shipped under the 'Legend' banner", 1),
    ("tes-redguard", "redguard", "The Elder Scrolls Adventures: Redguard",
     1998, "adventures", 3,
     "The action-adventure one — a named hero and no character sheet", 1),
    ("tes-morrowind", "morrowind", "The Elder Scrolls III: Morrowind", 2002,
     "morrowind", 1,
     "Vvardenfell — where the series found its modern shape", 0),
    ("tes-tribunal", "tribunal", "The Elder Scrolls III: Tribunal", 2002,
     "morrowind", 2, "Expansion — the city of Mournhold", 1),
    ("tes-bloodmoon", "bloodmoon", "The Elder Scrolls III: Bloodmoon", 2003,
     "morrowind", 2, "Expansion — Solstheim, and werewolves", 1),
    ("tes-oblivion", "oblivion", "The Elder Scrolls IV: Oblivion", 2006,
     "oblivion", 1,
     "Cyrodiil. The 2025 Oblivion Remastered retells it one-to-one — play "
     "either edition and tick this row.", 0),
    ("tes-shivering", "shivering-isles",
     "The Elder Scrolls IV: Shivering Isles", 2007, "oblivion", 2,
     "Expansion — Sheogorath's realm, the best-regarded add-on in the "
     "series", 1),
    ("tes-skyrim", "skyrim", "The Elder Scrolls V: Skyrim", 2011, "skyrim",
     1, "Any of its many editions counts as this row", 0),
    ("tes-dawnguard", "dawnguard", "The Elder Scrolls V: Skyrim - Dawnguard",
     2012, "skyrim", 2, "Expansion — the vampire war", 1),
    ("tes-dragonborn", "dragonborn",
     "The Elder Scrolls V: Skyrim - Dragonborn", 2012, "skyrim", 2,
     "Expansion — back to Solstheim", 1),
    ("tes-eso", "eso", "The Elder Scrolls Online", 2014, "online", 3,
     "The MMO — online and ongoing, optional by nature; the hours are "
     "HLTB's figure for the base story", 1),
]

SECTIONS = [
    ("dos", "The DOS era",
     "Two free-these-days giants. Rougher than everything after, and "
     "nothing later requires them."),
    ("adventures", "The adventure detours",
     "Two late-'90s experiments, here for the record."),
    ("morrowind", "Morrowind", ""),
    ("oblivion", "Oblivion", ""),
    ("skyrim", "Skyrim", ""),
    ("online", "Tamriel, online", ""),
]


def norm(s):
    s = (s or "").replace("’", "'").replace("–", "-").replace("—", "-")
    return " ".join(s.casefold().split())


def main():
    data = json.loads((pathlib.Path(__file__).resolve().parent / "data"
                       / "elder-scrolls.json").read_text(encoding="utf-8"))

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
               "items": [{k: v for k, v in e.items()
                          if k in ("id", "t", "n", "w", "tier", "opt", "note")}
                         for e in got]}
        if intro:
            sec["intro"] = intro
        if key == "dos":
            sec["open"] = True
        sections.append(sec)

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert len(ids) == len(ROSTER) == 13, (len(ids),)
    tiers = {t: [x for s in sections for x in s["items"] if x["tier"] == t]
             for t in (1, 2, 3)}
    assert len(tiers[1]) == 5, "mainline should be 5, got %d" % len(tiers[1])
    assert len(tiers[2]) == 5, "expansions should be 5, got %d" % len(tiers[2])
    assert len(tiers[3]) == 3, "tier 3 should be 3, got %d" % len(tiers[3])

    hours = sum(x["w"] for s in sections for x in s["items"])
    spine = sum(x["w"] for x in tiers[1])

    prop = {
        "slug": SLUG,
        "title": "The Elder Scrolls",
        "subtitle": "Arena to Skyrim in release order, expansions included",
        "kind": "games",
        "popularity": 77,
        "year": "1994–",
        "blurb": "5 mainline games, 5 expansions and 3 asides — about %d "
                 "hours of story, %d of it the mainline." % (round(hours),
                                                             round(spine)),
        "unit": {"one": "game", "many": "games"},
        "verb": {"base": "play", "past": "played", "ing": "playing"},
        "itemOrder": "number-first",
        "accent": "#8A6A28",
        "accentDark": "#E3C46B",
        "tiers": True,
        "itemTiers": True,
        "paceTiers": [1],
        "paceLabel": "the expansions, the detours and Online",
        "notes": [
            ["Standalone by design.", "Every Elder Scrolls is a fresh "
             "province and a fresh nobody — nothing requires anything "
             "else, and starting at Morrowind or Skyrim is a long "
             "tradition. This is the release order, with the early pair "
             "kept honest rather than mandatory."],
            ["Expansions are rows.", "The five HowLongToBeat tracks as "
             "separate entries — Tribunal, Bloodmoon, Shivering Isles, "
             "Dawnguard, Dragonborn — each optional, each with its own "
             "hours. Smaller add-ons like Knights of the Nine ride along "
             "inside the modern editions and are not split out."],
            ["Remasters are notes, not rows.", "The 2025 Oblivion "
             "Remastered is the same story in better clothes; whichever "
             "edition you play, tick the one Oblivion row. Skyrim's many "
             "re-releases work the same way."],
            ["Online is optional by nature.", "The Elder Scrolls Online is "
             "an MMO with no ending; its row carries HLTB's base-story "
             "figure and stays out of the finish-date maths."],
            ["Hours are story only.", "HowLongToBeat main-story figures — "
             "the critical path through games famous for ignoring it. "
             "Treat every number as a floor."],
            "Game list and years from Wikipedia's Elder Scrolls articles; "
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
    print("  %d sections, %d rows, %d hours (%d mainline)"
          % (len(sections), len(ids), round(hours), round(spine)))
    for s in sections:
        print("   %-26s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
