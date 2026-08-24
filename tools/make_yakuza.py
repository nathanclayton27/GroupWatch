#!/usr/bin/env python3
"""Generate properties/yakuza.json.

    python tools/make_yakuza.py

The mainline Yakuza / Like a Dragon saga in release order, with the Kiwami
remakes, the Judgment pair, the samurai games and the two recent gaiden.

Hours are HowLongToBeat main-story figures — story only — read from
tools/data/yakuza.json, which was collected by scratch/yakuza/fetch_hltb.py
and verified there by name AND release year (the generator refuses a record
whose name is not what it expects).  Kenzan! never left Japan and carries no
HLTB record; it weighs nothing rather than a guess.

Tiers are necessity, Metal Gear style:
  1  the Kiryu/Ichiban saga spine — including the Kiwami remakes, because
     the PS2 originals never left the PS2 and Kiwami is how 1 and 2 are
     actually played now
  2  the Judgment pair, the detective sibling series
  3  the PS2 originals, the samurai games, and the recent extras

Two ordering quirks, both deliberate: display years are first-release
(Japanese) years, which is the order the series actually came out in; and
HLTB keeps one Ishin! entry under the remake's international title with the
2014 original's year on it, so that row alone tolerates the year mismatch.
"""
import json
import pathlib

SLUG = "yakuza"

# key in the data file, expected HLTB name, display title, display year,
# tier, note, opt.  A key of None means no HLTB record (weight 0).
ROSTER = [
    ("y1", "Yakuza", "Yakuza", 2005, 3,
     "The PS2 original. Kiwami retells it — see the note below.", 1),
    ("y2", "Yakuza 2", "Yakuza 2", 2006, 3,
     "The PS2 original; Kiwami 2 retells it.", 1),
    (None, None, "Ryū ga Gotoku Kenzan!", 2008, 3,
     "Samurai spin-off set in 1605 Kyoto. Never localized, so it weighs "
     "nothing here.", 1),
    ("y3", "Yakuza 3", "Yakuza 3", 2009, 1, "", 0),
    ("y4", "Yakuza 4", "Yakuza 4", 2010, 1, "", 0),
    ("y5", "Yakuza 5", "Yakuza 5", 2012, 1,
     "The sprawler — five playable leads, five cities.", 0),
    ("y0", "Yakuza 0", "Yakuza 0", 2015, 1,
     "The chronological start — 1988, before everything. The famous "
     "alternative first game; see the note below.", 0),
    ("kiwami", "Yakuza Kiwami", "Yakuza Kiwami", 2016, 1,
     "Remake of the first game, and the way most people now play 1 — it "
     "carries the spine tier for that reason.", 0),
    ("y6", "Yakuza 6: The Song of Life", "Yakuza 6: The Song of Life",
     2016, 1, "", 0),
    ("kiwami2", "Yakuza Kiwami 2", "Yakuza Kiwami 2", 2017, 1,
     "Remake of 2 on the Dragon Engine — the way most people now play 2.",
     0),
    ("judgment", "Judgment", "Judgment", 2018, 2,
     "The detective spin-off line begins — same city, standalone story.",
     0),
    ("y7", "Yakuza: Like a Dragon", "Yakuza: Like a Dragon", 2020, 1,
     "The handover: Ichiban arrives and the series turns RPG.", 0),
    ("lost-judgment", "Lost Judgment", "Lost Judgment", 2021, 2, "", 0),
    ("ishin", "Like a Dragon: Ishin!", "Like a Dragon: Ishin!", 2023, 3,
     "The samurai spin-off, finally localized — a 2023 remake of the "
     "2014 Japan-only original.", 1),
    ("gaiden", "Like a Dragon Gaiden: The Man Who Erased His Name",
     "Like a Dragon Gaiden: The Man Who Erased His Name", 2023, 1,
     "Short Kiryu chapter between 6 and Infinite Wealth — Infinite Wealth "
     "assumes you have seen it.", 0),
    ("y8", "Like a Dragon: Infinite Wealth",
     "Like a Dragon: Infinite Wealth", 2024, 1, "", 0),
    ("pirate", "Like a Dragon: Pirate Yakuza in Hawaii",
     "Like a Dragon: Pirate Yakuza in Hawaii", 2025, 3,
     "Majima's own gaiden, set after Infinite Wealth.", 1),
    ("kiwami3", "Yakuza Kiwami 3 & Dark Ties",
     "Yakuza Kiwami 3 & Dark Ties", 2026, 3,
     "Remake of 3 plus Dark Ties, a new side story set just before it.", 1),
]

ERAS = [
    ("ps2", "The PS2 originals", 2005, 2007,
     "Where it started, and the two games the Kiwami remakes retell. Here "
     "for completeness; most groups will tick the remakes instead."),
    ("ps3", "The PS3 era", 2008, 2014,
     "The saga finds its shape — and its habit of sprawling."),
    ("kiwami-era", "Zero and the Kiwami years", 2015, 2017,
     "The prequel that became the standard entry point, and the remakes "
     "built in its image."),
    ("handover", "Judgment and the handover", 2018, 2022,
     "A detective sibling series arrives, and the saga hands the lead from "
     "Kiryu to Ichiban."),
    ("yearly", "The one-a-year era", 2023, 9999,
     "RGG Studio at full cadence — a samurai remake, two gaiden, and the "
     "biggest game in the series."),
]


def main():
    data = json.loads((pathlib.Path(__file__).resolve().parent / "data"
                       / "yakuza.json").read_text(encoding="utf-8"))

    entries = []
    used = set()
    for key, expect, title, year, tier, note, opt in ROSTER:
        if key is None:
            w = 0
            iid = "yak-kenzan"
        else:
            rec = data.get(key)
            assert rec, "no HLTB record for %s" % key
            assert rec["name"].lower() == expect.lower(), (
                "record mismatch for %s: %r" % (key, rec["name"]))
            # HLTB's one Ishin entry wears the 2014 original's year; the row
            # shows the localized 2023 remake on purpose
            ok_years = (2014, 2023) if key == "ishin" else (year,)
            assert rec["year"] in ok_years, (
                "year mismatch for %s: %r" % (key, rec["year"]))
            w = rec["main_h"]
            iid = "yak-%s" % key
            used.add(key)
        x = {"id": iid, "t": title, "n": str(year), "w": w, "tier": tier,
             "year": year}
        if note:
            x["note"] = note
        if opt:
            x["opt"] = 1
        entries.append(x)

    assert used == set(data), "cache keys unused: %r" % (set(data) - used)

    sections = []
    for key, title, lo, hi, intro in ERAS:
        got = [e for e in entries if lo <= e["year"] <= hi]
        assert got, "empty era %s" % key
        hours = sum(e["w"] for e in got)
        span = ("%d" % got[0]["year"] if got[0]["year"] == got[-1]["year"]
                else "%d–%d" % (got[0]["year"], got[-1]["year"]))
        sec = {"id": key, "title": title,
               "sub": "%s · %d %s · %d hours story"
                      % (span, len(got),
                         "game" if len(got) == 1 else "games", round(hours)),
               "items": [{k: v for k, v in e.items()
                          if k in ("id", "t", "n", "w", "tier", "opt", "note")}
                         for e in got]}
        if intro:
            sec["intro"] = intro
        if key == "ps2":
            sec["open"] = True
        sections.append(sec)

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert len(ids) == len(ROSTER) == 18, (len(ids),)
    tiers = {t: [x for s in sections for x in s["items"] if x["tier"] == t]
             for t in (1, 2, 3)}
    assert len(tiers[1]) == 10, "spine should be 10 games, got %d" % len(tiers[1])
    assert len(tiers[2]) == 2, "Judgment pair should be 2, got %d" % len(tiers[2])
    assert len(tiers[3]) == 6, "tier 3 should be 6, got %d" % len(tiers[3])

    hours = sum(x["w"] for s in sections for x in s["items"])
    spine = sum(x["w"] for x in tiers[1])

    prop = {
        "slug": SLUG,
        "title": "Yakuza / Like a Dragon",
        "subtitle": "the mainline saga in release order, Judgment and the "
                    "samurai games included",
        "kind": "games",
        "popularity": 60,
        "year": "2005–",
        "blurb": "%d games in release order — about %d hours of story, %d "
                 "of it the saga spine." % (len(ids), round(hours),
                                            round(spine)),
        "unit": {"one": "game", "many": "games"},
        "verb": {"base": "play", "past": "played", "ing": "playing"},
        "itemOrder": "number-first",
        "accent": "#8A1F3A",
        "accentDark": "#E86A8F",
        "tiers": True,
        "itemTiers": True,
        "paceTiers": [1, 2],
        "paceLabel": "the PS2 originals, samurai games and extras",
        "notes": [
            ["The 0-first debate.", "Release order starts at 1; Yakuza 0 is "
             "the chronological start and the most common modern entry "
             "point. Starting at 0 is the smoothest on-ramp and makes two "
             "later games land differently; starting at 1 meets the cast "
             "the way 2005 did and saves 0 for when its backstory hits "
             "hardest. Both orders are legitimate — this list is release "
             "order, with 0 marked."],
            ["Kiwami over the PS2 pair.", "The 2005–06 originals never left "
             "the PS2, so the Kiwami remakes are how the stories of 1 and 2 "
             "are actually played now. The remakes carry the spine tier "
             "here; the originals sit in tier 3 for the archaeologists. "
             "Tick one version of each, not both."],
            ["The Judgment pair.", "A sibling series rather than a chapter "
             "— same city, standalone detective stories. Skip it and the "
             "saga still reads; play it and Kamurocho gets deeper. A "
             "finish date covers tiers 1 and 2, and the checkbox adds the "
             "rest."],
            ["The samurai games.", "Kenzan! (2008) never left Japan and "
             "weighs nothing here. Ishin! reached the west as the 2023 "
             "remake — the one on this list; its 2014 original was also "
             "Japan-only."],
            ["Left off, on purpose.", "Dead Souls (non-canon), the "
             "Kurohyō pair (Japan-only PSP), Fist of the North Star: Lost "
             "Paradise (a licensed crossover) and the remaster collections "
             "and Director's Cuts of games already listed."],
            ["Hours are story only.", "HowLongToBeat main-story figures — "
             "no substories, no completionist padding. In this series the "
             "substories are half the point, so treat every figure as a "
             "floor."],
            "Hours from HowLongToBeat, matched by name and release year.",
        ],
        "sections": sections,
    }

    out = (pathlib.Path(__file__).resolve().parent.parent / "properties"
           / ("%s.json" % SLUG))
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json" % SLUG)
    print("  %d sections, %d games, %d hours (%d spine, %d with Judgment)"
          % (len(sections), len(ids), round(hours), round(spine),
             round(spine + sum(x["w"] for x in tiers[2]))))
    for s in sections:
        print("   %-28s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
