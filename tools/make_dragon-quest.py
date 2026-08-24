#!/usr/bin/env python3
"""Generate properties/dragon-quest.json.

    python tools/make_dragon-quest.py

Mainline Dragon Quest, I through XI, in release order. Spin-offs (Monsters,
Builders, Heroes, the roguelikes) are cut and the cut is noted. Display
years are original Japanese release years — the order the series actually
came out in; HowLongToBeat stamps several entries with the year of the
western or remade edition it names, so each row carries an acceptable HLTB
year range rather than an exact match.

The game list and years were machine-read from Wikipedia's Dragon Quest
article (scratch/agent-games2/verify_wiki.py). Hours are HowLongToBeat
main-story figures — story only, the house standard — read from
tools/data/dragon-quest.json, collected by
scratch/agent-games2/fetch_hltb.py and verified by name and year there;
this generator refuses a record whose name is not what it expects.

Dragon Quest X is the MMO and never left Japan (nor did its Offline cut) —
it ships unweighted with a factual note rather than a guessed number, the
house rule for unverifiable hours.
"""
import json
import pathlib

SLUG = "dragon-quest"

# id, data key, expected HLTB names, display title, display JP year,
# acceptable HLTB years, section, note, opt
ROSTER = [
    ("dq-1", "dq1", ["Dragon Quest", "Dragon Warrior"], "Dragon Quest",
     1986, (1986, 1989), "erdrick",
     "Where the JRPG starts — an evening by modern standards. The HD-2D "
     "remake pairs it with II.", 0),
    ("dq-2", "dq2", ["Dragon Quest II: Luminaries of the Legendary Line",
                     "Dragon Warrior II"],
     "Dragon Quest II: Luminaries of the Legendary Line", 1987,
     (1987, 1990), "erdrick", "First party, first ships", 0),
    ("dq-3", "dq3", ["Dragon Quest III: The Seeds of Salvation",
                     "Dragon Warrior III"],
     "Dragon Quest III: The Seeds of Salvation", 1988, (1988, 1992),
     "erdrick",
     "The era's peak, and a prequel that closes the Erdrick arc. The 2024 "
     "HD-2D remake is the modern way in — any edition ticks this row.", 0),
    ("dq-4", "dq4", ["Dragon Quest IV: Chapters of the Chosen",
                     "Dragon Warrior IV"],
     "Dragon Quest IV: Chapters of the Chosen", 1990, (1990, 2008),
     "zenithian",
     "Five chapters, five casts. The DS remake is the usual edition now.",
     0),
    ("dq-5", "dq5", ["Dragon Quest V: Hand of the Heavenly Bride"],
     "Dragon Quest V: Hand of the Heavenly Bride", 1992, (1992, 2009),
     "zenithian",
     "Three decades of one life, and the series' most-loved story; the DS "
     "remake is the usual edition", 0),
    ("dq-6", "dq6", ["Dragon Quest VI: Realms of Revelation"],
     "Dragon Quest VI: Realms of Revelation", 1995, (1995, 2011),
     "zenithian", "Closes the Zenithian arc; DS remake likewise", 0),
    ("dq-7", "dq7", ["Dragon Quest VII: Fragments of the Forgotten Past",
                     "Dragon Warrior VII"],
     "Dragon Quest VII: Fragments of the Forgotten Past", 2000,
     (2000, 2001), "wander", "The longest, by a distance", 0),
    ("dq-8", "dq8", ["Dragon Quest VIII: Journey of the Cursed King"],
     "Dragon Quest VIII: Journey of the Cursed King", 2004, (2004, 2005),
     "wander",
     "Fully 3D at last, and the west's usual first Dragon Quest", 0),
    ("dq-9", "dq9", ["Dragon Quest IX: Sentinels of the Starry Skies"],
     "Dragon Quest IX: Sentinels of the Starry Skies", 2009, (2009, 2010),
     "wander", "The DS one, built for playing alongside people", 0),
    ("dq-10", "dq10", ["Dragon Quest X", "Dragon Quest X Offline",
                       "Dragon Quest X: Rise of the Five Tribes",
                       "Dragon Quest X: Rise of the Five Tribes Offline"],
     "Dragon Quest X", 2012, (2012, 2022), "modern",
     "The MMO, and the one that never left Japan — the Offline cut "
     "stayed there too. Ongoing by design; unweighted here rather than "
     "guessed.", 1),
    ("dq-11", "dq11", ["Dragon Quest XI: Echoes of an Elusive Age"],
     "Dragon Quest XI: Echoes of an Elusive Age", 2017, (2017, 2018),
     "modern",
     "XI S (2019) is the definitive edition — either ticks this row", 0),
]

SECTIONS = [
    ("erdrick", "The Erdrick trilogy",
     "Three NES games, one loosely shared legend — and III looping back "
     "to before I."),
    ("zenithian", "The Zenithian trilogy",
     "The SNES-era arc, best played today in its DS remakes."),
    ("wander", "VII to IX",
     "Three standalone eras — PlayStation sprawl, PS2 polish, DS "
     "invention."),
    ("modern", "X and XI",
     "The Japan-only MMO, and the modern classic that runs everywhere."),
]


def norm(s):
    s = (s or "").replace("’", "'").replace("–", "-").replace("—", "-")
    return " ".join(s.casefold().split())


def main():
    data = json.loads((pathlib.Path(__file__).resolve().parent / "data"
                       / "dragon-quest.json").read_text(encoding="utf-8"))

    rows = {}
    used = set()
    for iid, key, expects, title, year, ok_years, sec, note, opt in ROSTER:
        rec = data.get(key)
        assert rec, "no HLTB record for %s" % key
        assert norm(rec["name"]) in {norm(e) for e in expects}, \
            "record mismatch for %s: %r" % (key, rec["name"])
        assert ok_years[0] <= int(rec["year"]) <= ok_years[1], \
            "year mismatch for %s: hltb %s" % (key, rec["year"])
        used.add(key)
        w = rec["main_h"] if rec["main_h"] and key != "dq10" else 0
        assert w > 0 or key == "dq10", "missing hours for %s" % key
        x = {"id": iid, "t": title, "n": str(year), "w": w, "year": year}
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
               "sub": "%d–%d · %d games · %d hours story"
                      % (got[0]["year"], got[-1]["year"], len(got),
                         round(hours)),
               "intro": intro,
               "items": [{k: v for k, v in e.items()
                          if k in ("id", "t", "n", "w", "opt", "note")}
                         for e in got]}
        if key == "erdrick":
            sec["open"] = True
        sections.append(sec)

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert len(ids) == len(ROSTER) == 11, (len(ids),)

    hours = sum(x["w"] for s in sections for x in s["items"])

    prop = {
        "slug": SLUG,
        "title": "Dragon Quest",
        "subtitle": "the mainline eleven in release order",
        "kind": "games",
        "popularity": 56,
        "year": "1986–",
        "blurb": "Mainline I through XI — about %d hours of story, from "
                 "one-evening NES quests to the hundred-hour XI."
                 % round(hours),
        "unit": {"one": "game", "many": "games"},
        "verb": {"base": "play", "past": "played", "ing": "playing"},
        "itemOrder": "number-first",
        "accent": "#1D5FB8",
        "accentDark": "#F0953F",
        "tiers": False,
        "notes": [
            ["Standalone by design.", "Every numbered Dragon Quest is its "
             "own story — the two loose trilogies share a world, not a "
             "plot. Start anywhere; this is the release order, with III's "
             "prequel twist the one reason the Erdrick arc rewards being "
             "played as it came out."],
            ["Remakes are notes, not rows.", "The HD-2D remakes of III "
             "(2024) and I & II, the DS versions of IV–VI, and XI S are "
             "the same stories in better clothes — play whichever edition "
             "and tick the one row."],
            ["X, factually.", "Dragon Quest X is an MMO that never left "
             "Japan, and its Offline version stayed there too. The row "
             "exists because the mainline number does; it weighs nothing "
             "here rather than carrying a guessed figure, and skipping it "
             "breaks nothing."],
            ["Spin-offs are cut.", "Monsters, Builders, Heroes, the "
             "Mystery Dungeon games and the rest are their own series — "
             "this list is the numbered eleven only."],
            ["Hours are story only.", "HowLongToBeat main-story figures — "
             "the credits, not the post-game, and Dragon Quest post-games "
             "are famously half the meal. Treat the numbers as floors."],
            "Game list and years from Wikipedia's Dragon Quest article; "
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
    print("  %d sections, %d games, %d hours" % (len(sections), len(ids),
                                                 round(hours)))
    for s in sections:
        print("   %-24s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
