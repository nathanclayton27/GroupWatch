#!/usr/bin/env python3
"""Generate properties/star-wars-games.json.

    python3 tools/make_starwars_games.py

The games, on their own page. They were a section of the Star Wars list and
before that were interleaved with the films by year; sixty-eight of them buried
whatever they sat next to, and they are a parallel thing rather than a step in
the same sequence.

Titles and years come from Wikipedia's "List of Star Wars video games", read by
scratch/starwars/parse_games.py. Everything made under Disney is here, plus a
long run of older titles asked for by name.

Anything released before 25 April 2014 is Legends: that is the day the Expanded
Universe stopped being canon, which is not the same as the October 2012
takeover, so a 2013 game is no more canon than a 1998 one. Lego sits outside
any continuity and is marked separately.

No weights. No source for how long a Star Wars game takes was confirmed, and a
made-up number would go straight into everyone's pace.
"""
import json
import pathlib

SLUG = "star-wars-games"
CANON_FROM = 2014

DECADES = [
    ("d1990", "The nineties", 1990, 1999,
     "The best run LucasArts ever had: the flight sims, Dark Forces, Jedi "
     "Knight, Rogue Squadron, and the Super Star Wars trilogy on the SNES."),
    ("d2000", "The two thousands", 2000, 2009,
     "The prequel tie-ins, Knights of the Old Republic, Battlefront, Republic "
     "Commando — the widest the catalogue ever got."),
    ("d2010", "The twenty-tens", 2010, 2019,
     "The licence goes to EA, the Expanded Universe becomes Legends, and the "
     "output narrows to a handful of big releases and a lot of mobile."),
    ("d2020", "The twenty-twenties", 2020, 2999,
     "Ubisoft, Respawn and a widening field again."),
]


def slug(t):
    keep = "".join(c.lower() if c.isalnum() else "-" for c in t)
    while "--" in keep:
        keep = keep.replace("--", "-")
    return keep.strip("-")


def main():
    data = pathlib.Path(__file__).resolve().parent / "data" / "starwars.json"
    games = json.loads(data.read_text(encoding="utf-8"))["games"]
    games.sort(key=lambda g: (g["year"], g["t"]))

    sections = []
    for key, title, lo, hi, intro in DECADES:
        got = [g for g in games if lo <= g["year"] <= hi]
        if not got:
            continue
        items = []
        for g in got:
            lego = g["t"].lower().startswith("lego")
            legends = g["year"] < CANON_FROM
            if lego:
                tags, note = ["Lego"], "Outside any continuity"
            elif legends:
                tags, note = ["Legends"], "Legends"
            else:
                tags, note = ["Canon"], "Canon"
            items.append({
                "id": "swg-%d-%s" % (g["year"], slug(g["t"])),
                "t": g["t"], "n": str(g["year"]),
                "note": note, "tags": tags,
            })
        nl = sum(1 for x in items if x["tags"] == ["Legends"])
        sections.append({
            "id": key, "title": title,
            "sub": "%d–%d · %d game%s%s"
                   % (got[0]["year"], got[-1]["year"], len(got),
                      "" if len(got) == 1 else "s",
                      " · %d Legends" % nl if nl else ""),
            "intro": intro, "items": items,
        })
    sections[0]["open"] = True

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), \
        "duplicate ids: %s" % sorted({i for i in ids if ids.count(i) > 1})[:5]
    assert len(ids) == len(games), (len(ids), len(games))
    for s in sections:
        nums = [int(x["n"]) for x in s["items"]]
        assert nums == sorted(nums), "%s is out of year order" % s["title"]

    counts = {}
    for s in sections:
        for x in s["items"]:
            counts[x["tags"][0]] = counts.get(x["tags"][0], 0) + 1

    prop = {
        "slug": SLUG,
        "title": "Star Wars Games",
        "subtitle": "the whole catalogue, in release order",
        "kind": "games",
        "popularity": 64,
        "year": "1992–",
        "blurb": "%d games in the order they came out — %d Legends, %d canon, "
                 "%d Lego." % (len(games), counts.get("Legends", 0),
                               counts.get("Canon", 0), counts.get("Lego", 0)),
        "unit": {"one": "game", "many": "games"},
        "verb": {"base": "play", "past": "played", "ing": "playing"},
        "itemOrder": "number-first",
        "accent": "#7A5A1E",
        "accentDark": "#D9B45C",
        "tiers": False,
        "filter": {
            "key": "canon", "label": "Show", "mode": "exclude",
            "values": ["Canon", "Legends", "Lego"],
        },
        "notes": [
            ["Legends means before 25 April 2014.", "That is the day the Expanded "
             "Universe stopped being canon. It is not the October 2012 takeover, "
             "which is the date people usually reach for — a 2013 game is no more "
             "canon than a 1998 one. Lego is its own thing and sits outside both."],
            ["Turning parts of it off.", "The chips at the top drop a whole "
             "category, so “just the canon ones” or “no Lego” "
             "is one click. It hides rows and redraws the bar; it never unticks "
             "anything."],
            ["No weights.", "No source for how long a Star Wars game takes was "
             "confirmed, so every game counts as one entry rather than wearing a "
             "made-up number. That keeps the bar honest and means a finish date "
             "paces you by count."],
            ["What is not here.", "Things that never shipped, browser and Roblox "
             "toys, board games, crossovers into other studios' games, and five "
             "aimed at small children. Galaxy of Heroes is mobile but is not one "
             "of those, and stays."],
            "Titles and years from Wikipedia's list of Star Wars video games. "
            "The films and television are a separate list.",
        ],
        "sections": sections,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json" % SLUG)
    print("  %d sections, %d games — %s" % (len(sections), len(ids),
          ", ".join("%s %d" % kv for kv in sorted(counts.items()))))
    for s in sections:
        print("   %-22s %3d  %s" % (s["title"], len(s["items"]), s["sub"][:44]))


if __name__ == "__main__":
    main()
