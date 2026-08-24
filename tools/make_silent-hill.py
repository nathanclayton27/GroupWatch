#!/usr/bin/env python3
"""Generate properties/silent-hill.json.

    python3 tools/make_silent-hill.py

Mainline Silent Hill in release order: the four Team Silent games, the
wandering years after them, and the 2024 revival.

Which games count and their release years come from Wikipedia's Silent
Hill article (scratch/agent-games1/wiki/silent-hill.wiki) — its Main
series and Remakes sections, plus The Short Message. Silent Hill f is not
a row: Wikipedia's page classes it as a spin-off, sourced to the game's
own producer, and this list is mainline. Hours are HowLongToBeat
main-story figures — story only, the house standard — read from
tools/data/silent-hill.json, collected by
scratch/agent-games1/fetch_hltb.py and verified by name (this generator
refuses a record whose name is not what it expects, and cross-checks
HLTB's release year against Wikipedia's; the 2024 remake shares the 2001
game's name on HLTB and is told apart by year).

Tiers, per the house rule (1 = the essential path, 2 = worthwhile side
entries): 1 is Silent Hill 1–4 plus the 2024 remake; 2 is everything
after Team Silent plus the free Short Message.
"""
import json
import pathlib

SLUG = "silent-hill"

# key in the data file, display title, Wikipedia year, tier, note, opt
TEAM_SILENT = [
    ("sh1", "Silent Hill", 1999, 1,
     "PS1. Harry Mason, the fog, the school — where the town starts.", 0),
    ("sh2", "Silent Hill 2", 2001, 1,
     "James Sunderland and the letter. The series' peak, and its own "
     "story — the 2024 row rebuilds it.", 0),
    ("sh3", "Silent Hill 3", 2003, 1,
     "Heather's story — the one direct sequel, continuing the first "
     "game", 0),
    ("sh4", "Silent Hill 4: The Room", 2004, 1,
     "Room 302 and the hole in the bathroom wall; Team Silent's last", 0),
]

AFTER = [
    ("origins", "Silent Hill: Origins", 2007, 2,
     "PSP prequel to the first game", 0),
    ("homecoming", "Silent Hill: Homecoming", 2008, 2,
     "The first western-built entry", 0),
    ("shattered", "Silent Hill: Shattered Memories", 2009, 2,
     "A reimagining of the first game — the therapy-session one, and the "
     "best of this stretch", 0),
    ("downpour", "Silent Hill: Downpour", 2012, 2,
     "Murphy Pendleton, rain, and the last of the old line", 0),
]

REVIVAL = [
    ("short-message", "Silent Hill: The Short Message", 2024, 2,
     "Free on PS5 — a short standalone story, and the series waking back "
     "up", 1),
    ("sh2-remake", "Silent Hill 2 (2024)", 2024, 1,
     "Bloober Team's remake — the modern door into the story; ticking "
     "either version counts", 0),
]

# expected HLTB names where they differ from the display title
EXPECT = {"sh2-remake": ["Silent Hill 2", "Silent Hill 2 Remake",
                         "Silent Hill 2 (2024)"]}

SECTIONS = [
    ("team-silent", "Team Silent",
     "Four games in six years from the studio the series is measured "
     "against.", TEAM_SILENT),
    ("after", "After Team Silent",
     "Outside studios carry the town, 2007–2012 — worthwhile side trips, "
     "none required.", AFTER),
    ("revival", "The revival",
     "Konami returns to the town in 2024.", REVIVAL),
]


def norm(s):
    s = (s or "").replace("’", "'").replace("–", "-")
    return " ".join(s.casefold().split())


def main():
    data = json.loads((pathlib.Path(__file__).resolve().parent / "data"
                       / "silent-hill.json").read_text(encoding="utf-8"))

    sections = []
    for sec_id, sec_title, intro, roster in SECTIONS:
        years = [y for _, _, y, _, _, _ in roster]
        assert years == sorted(years), "%s roster out of release order" % sec_id
        items = []
        for key, title, year, tier, note, opt in roster:
            rec = data.get(key)
            assert rec, "no HLTB record for %s" % key
            want = {norm(n) for n in EXPECT.get(key, [title])}
            assert norm(rec["name"]) in want, \
                "record mismatch for %s: %r" % (key, rec["name"])
            assert abs(int(rec["year"]) - year) <= 1, \
                "year mismatch for %s: wiki %d, hltb %s" % (key, year, rec["year"])
            x = {"id": "sh-%s" % key, "t": title, "n": str(year),
                 "w": rec["main_h"], "tier": tier}
            if note:
                x["note"] = note
            if opt:
                x["opt"] = 1
            items.append(x)
        hours = sum(x["w"] for x in items)
        span = ("%d" % years[0] if years[0] == years[-1]
                else "%d–%d" % (years[0], years[-1]))
        sections.append({
            "id": sec_id, "title": sec_title,
            "sub": "%s · %d games · %d hours story"
                   % (span, len(items), round(hours)),
            "intro": intro,
            "items": items,
        })
    sections[0]["open"] = True

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert len(ids) == len(TEAM_SILENT) + len(AFTER) + len(REVIVAL) == 10, \
        (len(ids),)
    t1 = [x for s in sections for x in s["items"] if x["tier"] == 1]
    assert len(t1) == 5, "the essential path is 1-4 plus the remake"

    hours = sum(x["w"] for s in sections for x in s["items"])
    spine = sum(x["w"] for x in t1)

    prop = {
        "slug": SLUG,
        "title": "Silent Hill",
        "subtitle": "the mainline series in release order",
        "kind": "games",
        "popularity": 69,
        "year": "1999–",
        "blurb": "%d games — about %d hours of story, %d of it the "
                 "essential path." % (len(ids), round(hours), round(spine)),
        "unit": {"one": "game", "many": "games"},
        "verb": {"base": "play", "past": "played", "ing": "playing"},
        "itemOrder": "number-first",
        "accent": "#6B655E",
        "accentDark": "#C97455",
        "tiers": True,
        "itemTiers": True,
        "paceTiers": [1],
        "paceLabel": "the later games and the free side story",
        "notes": [
            ["Tiers.", "1 is the essential path — Silent Hill 1 through 4 "
             "plus the 2024 remake, about %d hours; 2 is the post-Team "
             "Silent years and the free Short Message. A finish date "
             "covers tier 1 and the checkbox adds the rest."
             % round(spine)],
            ["Mostly standalone.", "Only Silent Hill 3 is a direct sequel "
             "(to the first game); everything else is its own story in "
             "the same town. Release order is the natural order all the "
             "same."],
            ["Getting the old games, honestly.", "Konami has delisted or "
             "never re-released most of the pre-2024 catalogue — the "
             "Team Silent games have no modern storefront release apart "
             "from Silent Hill 4 on GOG, and Origins, Shattered Memories "
             "and Downpour remain on their original platforms. Budget "
             "for original hardware or the remake."],
            ["Scope.", "Mainline only. Wikipedia classes Silent Hill f "
             "(2025) as a spin-off — its producer's word — and the "
             "arcade, mobile and Book of Memories side games sit outside "
             "this list with it."],
            ["Hours are story only.", "HowLongToBeat main-story figures — "
             "one ending, no UFO runs."],
            "Game list and years from Wikipedia's Silent Hill article; "
            "hours from HowLongToBeat main-story figures, verified by "
            "name.",
        ],
        "sections": sections,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json" % SLUG)
    print("  %d sections, %d games, %d hours (%d essential)"
          % (len(sections), len(ids), round(hours), round(spine)))
    for s in sections:
        print("   %-18s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
