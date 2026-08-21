#!/usr/bin/env python3
"""Generate properties/ultimate-marvel.json.

    python3 tools/make_ultimate.py

The whole Ultimate universe in reading order, from Ultimate Spider-Man #1 to
the line's end, transcribed from the Comic Book Herald Ultimate Marvel reading
order supplied by Nathan.

    https://www.comicbookherald.com/the-complete-marvel-reading-order-guide/ultimate-marvel-universe-reading-order/

Tracked issue by issue rather than by run: the whole point of this order is the
interleaving — Spider-Man, X-Men, Ultimates and Fantastic Four cut into each
other constantly, and a list of runs would throw away the only thing that is
hard to work out for yourself.

Where the source calls something inessential or out of continuity it is marked
optional rather than removed, so the order stays intact. Its commentary is kept
as notes on the entry it belongs to, trimmed but not editorialised.
"""
import json
import pathlib
import re

SLUG = "ultimate-marvel"

# Marvel series pages, all checked. Nine of the sixty-five series, but they are
# the long-running ones and cover most of the issues here; the rest are minis
# and annuals whose ids would each need a separate lookup, and Marvel Unlimited
# finds any of them by exact title.
SERIES_URL = {
    "Ultimate Spider-Man":
        "https://www.marvel.com/comics/series/466/ultimate_spider-man_(2000_-_2009)",
    "Ultimate X-Men":
        "https://www.marvel.com/comics/series/474/ultimate_xmen_2001_2009",
    "Ultimate Fantastic Four":
        "https://www.marvel.com/comics/series/702/ultimate_fantastic_four_2003_2009",
    "Ultimates":
        "https://www.marvel.com/comics/series/664/ultimates_2002_-_2003",
    "Ultimates (v2)":
        "https://www.marvel.com/comics/series/709/ultimates_2_(2004_-_2006)",
    "Ultimate Marvel Team-Up":
        "https://www.marvel.com/comics/series/2311/ultimate_marvel_team-up_(2001_-_2002)",
    "Ultimate Comics Spider-Man (2011)":
        "https://www.marvel.com/comics/series/13831/ultimate_comics_spider-man_2011_-_2013",
    "Ultimate Comics X-Men":
        "https://www.marvel.com/comics/series/13108/ultimate_comics_xmen_2011_2013",
    "All-New Ultimates":
        "https://www.marvel.com/comics/series/18524/allnew_ultimates_2014_2015",
    "Ultimate Comics Ultimates":
        "https://www.marvel.com/comics/series/13936/ultimate_comics_ultimates__(2011_-_present)",
    "Ultimate Comics Spider-Man":
        "https://www.marvel.com/comics/series/8509/ultimate_spiderman_2009_2012",
    "Ultimate Fallout":
        "https://www.marvel.com/comics/series/14807/ultimate_fallout_2011",
    "Ultimate Six":
        "https://www.marvel.com/comics/series/419/ultimate_six_2003_2004",
    "Ultimate Nightmare":
        "https://www.marvel.com/comics/series/760/ultimate_nightmare_(2004_-_2005)",
    "Ultimate Secret":
        "https://www.marvel.com/comics/series/838/ultimate_secret_2005",
    "Ultimate Power":
        "https://www.marvel.com/comics/series/1124/ultimate_power_(2006_-_2008)",
    "Ultimate Vision":
        "https://www.marvel.com/comics/series/3255/ultimate_vision_2006_-_2007",
}


def r(a, b):
    return [str(n) for n in range(a, b + 1)]


# (series, issue labels, note, optional)
ORDER = [
    ("intro", "Intro to the Ultimate U", "2000–2003 · where the line starts", [
        ("Ultimate Spider-Man", r(1, 13), "", 0),
        ("Ultimate Daredevil & Elektra", r(1, 4),
         "All flashback. You could read it later, when Daredevil turns up in "
         "Ultimate Marvel Team-Up; the source prefers it here as an origin.", 1),
        ("Ultimate Elektra", r(1, 5),
         "Another flashback, published well after much of what follows. Neither "
         "Daredevil nor Elektra matters much to the Spider-Man, X-Men and "
         "Ultimates stories, so this can wait.", 1),
        ("Ultimate Iron Man", r(1, 5),
         "Flashback origins the source calls pretty inessential, and which "
         "readers have argued are out of continuity outright.", 1),
        ("Ultimate Iron Man II", r(1, 5), "", 1),
        ("Ultimate Marvel Team-Up", r(1, 8), "", 0),
        ("Ultimate X-Men", r(1, 6), "", 0),
        ("Ultimate Spider-Man", r(14, 21), "", 0),
        ("Ultimate Marvel Team-Up", r(10, 16), "", 0),
        ("Ultimate X-Men", r(7, 14), "", 0),
        ("Ultimate Spider-Man", r(22, 27), "", 0),
        ("Ultimates", r(1, 3), "", 0),
        ("Ultimate X-Men", r(15, 20), "", 0),
        ("Ultimate Spider-Man", r(28, 32), "", 0),
        ("Ultimates", r(4, 13), "", 0),
        ("Ultimate Fantastic Four", r(1, 6),
         "Did not launch until 2003, well after The Ultimates — the team is "
         "mentioned in passing in Ultimates #2 — but the source prefers their "
         "origin here.", 0),
        ("Ultimate Marvel Team-Up", ["9"],
         "Out of continuity. A Fantastic Four story that never lines up with the "
         "Ultimate Fantastic Four that followed.", 1),
        ("Ultimate Spider-Man", r(33, 39), "", 0),
        ("Ultimate X-Men", r(21, 25), "", 0),
        ("Ultimate War", r(1, 4), "", 0),
    ]),
    ("afterwar", "After the Ultimate War", "2003–2004", [
        ("Ultimate X-Men", r(26, 33), "", 0),
        ("Ultimate Spider-Man", r(40, 45), "", 0),
        ("Ultimate X-Men", r(34, 39), "", 0),
        ("Ultimate Spider-Man", ["46"], "", 0),
        ("Ultimate Six", r(1, 7), "", 0),
        ("Ultimate Spider-Man", r(47, 49), "", 0),
        ("Ultimate X-Men", r(40, 53), "", 0),
        ("Ultimate Spider-Man", r(50, 59), "", 0),
        ("Ultimate Fantastic Four", r(7, 18), "", 0),
        ("Ultimate Spider-Man", r(60, 69), "", 0),
    ]),
    ("gahlaktus", "The Gah Lak Tus Trilogy", "2004–2006", [
        ("Ultimate Nightmare", r(1, 5), "", 0),
        ("Ultimate X-Men", r(54, 60), "", 0),
        ("Ultimate X-Men Annual", ["1"], "", 0),
        ("Ultimate Spider-Man", r(70, 77), "", 0),
        ("Ultimates Annual", ["1"], "", 0),
        ("Ultimate Secret", r(1, 4), "", 0),
        ("Ultimate Vision", ["0"],
         "The Vision story ran as short strips across the whole line — a piece in "
         "Ultimate Spider-Man #86, and so on. Marvel Unlimited has it collected "
         "here, which reads far better.", 0),
        ("Ultimates (v2)", r(1, 5), "", 0),
        ("Ultimate X-Men", r(61, 65), "", 0),
        ("Ultimate Fantastic Four", r(19, 26), "", 0),
        ("Ultimate Fantastic Four Annual", ["1"], "", 0),
        ("Ultimate Extinction", r(1, 5), "", 0),
        ("Ultimate Wolverine vs. Hulk", r(1, 6),
         "Published well after Ultimates v2, but the source puts it before that "
         "run concludes.", 0),
        ("Ultimates (v2)", r(6, 13), "", 0),
        ("Ultimate Spider-Man", r(78, 85), "", 0),
        ("Ultimate Spider-Man Annual", ["1"], "", 0),
        ("Ultimate Spider-Man", r(86, 90), "", 0),
    ]),
    ("ultpower", "Countdown to Ultimate Power", "2006–2007", [
        ("Ultimate X-Men", r(66, 74), "", 0),
        ("Ultimate X-Men Annual", ["2"], "", 0),
        ("Ultimate X-Men / Fantastic Four", ["1"],
         "In Marvel Unlimited this one is filed as “Ultimate X-Men/Fantastic Four”", 0),
        ("Ultimate X-Men / Fantastic Four", ["2"],
         "and this one as “Ultimate Fantastic Four/X-Men”", 0),
        ("Ultimate Fantastic Four", r(27, 32), "", 0),
        ("Ultimate Fantastic Four Annual", ["2"], "", 0),
        ("Ultimate Spider-Man", r(91, 96), "", 0),
        ("Ultimate Spider-Man Annual", ["2"], "", 0),
        ("Ultimates Annual", ["2"], "", 0),
        ("Ultimate Spider-Man", r(97, 105), "", 0),
        ("Ultimate Power", r(1, 9), "", 0),
        ("Ultimate X-Men", r(75, 80), "", 0),
    ]),
    ("ulthuman", "Countdown to Ultimate Human", "2007–2008", [
        ("Ultimate Fantastic Four", r(33, 46), "", 0),
        ("Ultimate Vision", r(1, 5), "", 0),
        ("Ultimate Spider-Man", r(106, 117), "", 0),
        ("Ultimate X-Men", r(81, 89), "", 0),
        ("Ultimate Fantastic Four", r(47, 53), "", 0),
        ("Ultimate Spider-Man", r(118, 122), "", 0),
        ("Ultimate Spider-Man Annual", ["3"], "", 0),
        ("Ultimate Fantastic Four", r(54, 57), "", 0),
        ("Ultimate Human", r(1, 4), "", 0),
    ]),
    ("march", "March to Ultimatum", "2008", [
        ("Ultimate Spider-Man", r(123, 128), "", 0),
        ("The Ultimates (v3)", r(1, 5), "", 0),
        ("Squadron Supreme", r(1, 6), "", 0),
        ("Ultimate X-Men", r(90, 97), "", 0),
        ("Ultimate Origins", r(1, 5), "", 0),
        ("Ultimate Hulk Annual", ["1"], "", 0),
        ("Ultimate X-Men/Fantastic Four Annual", ["1"], "", 0),
        ("Ultimate Fantastic Four/X-Men Annual", ["1"], "", 0),
    ]),
    ("ultimatum", "Ultimatum", "2008–2009 · the line's first ending", [
        ("Ultimate Spider-Man", ["129"], "", 0),
        ("Ultimatum", ["1"], "", 0),
        ("Ultimate Spider-Man", ["130"], "", 0),
        ("Ultimate X-Men", ["98"], "", 0),
        ("Ultimatum", ["2"], "", 0),
        ("Ultimate Fantastic Four", ["58"], "", 0),
        ("Ultimate Spider-Man", ["131"], "", 0),
        ("Ultimate Fantastic Four", ["59"], "", 0),
        ("Ultimate X-Men", ["99"], "", 0),
        ("Ultimatum", ["3"], "", 0),
        ("Ultimate Spider-Man", ["132"], "", 0),
        ("Ultimate Fantastic Four", ["60"], "", 0),
        ("Ultimate X-Men", ["100"], "", 0),
        ("Ultimatum", ["4"], "", 0),
        ("Ultimate Spider-Man", ["133"], "", 0),
        ("Ultimatum", ["5"], "", 0),
        ("Ultimatum: Fantastic Four Requiem", ["1"], "", 0),
        ("Ultimatum: X-Men Requiem", ["1"], "", 0),
        ("Ultimatum: Spider-Man Requiem", ["1", "2"], "", 0),
    ]),
    ("afterult", "After Ultimatum", "2009–2010", [
        ("Ultimate Comics X", r(1, 5), "", 0),
        ("Ultimate Comics Armor Wars", r(1, 4), "", 0),
        ("Ultimate Comics Spider-Man", r(1, 6), "", 0),
        ("Ultimate Comics Avengers", r(1, 6), "", 0),
        ("Ultimate Comics Spider-Man", r(7, 15), "", 0),
        ("Ultimate Comics Avengers 2", r(1, 6), "", 0),
    ]),
    ("enemy", "Ultimate Enemy Begins", "2010–2011", [
        ("Ultimate Enemy", r(1, 4), "", 0),
        ("Ultimate Mystery", r(1, 4), "", 0),
        ("Ultimate Doom", r(1, 4), "", 0),
        ("Ultimate Comics Captain America", r(1, 4), "", 0),
        ("Ultimate Comics New Ultimates", r(1, 5), "", 0),
        ("Ultimate Comics Thor", r(1, 4), "", 0),
        ("Ultimate Comics Avengers 3", r(1, 6), "", 0),
    ]),
    ("deathofsm", "Death of Spider-Man", "2011", [
        ("Ultimate Comics Spider-Man", r(150, 156),
         "The numbering jumps back to the original count for the 150th issue.", 0),
        ("Ultimate Comics Avengers vs. New Ultimates", r(1, 2), "", 0),
        ("Ultimate Comics Spider-Man", ["157"], "", 0),
        ("Ultimate Comics Avengers vs. New Ultimates", r(3, 4), "", 0),
        ("Ultimate Comics Spider-Man", r(158, 160), "", 0),
        ("Ultimate Comics Avengers vs. New Ultimates", r(5, 6), "", 0),
        ("Ultimate Fallout", r(1, 6), "", 0),
        ("Ultimate Comics Spider-Man (2011)", r(1, 5), "", 0),
        ("Ultimate Comics Spider-Man (2011)", r(7, 12),
         "The source skips #6 here; it is not listed anywhere in the order.", 0),
        ("Spider-Men", r(1, 5), "", 0),
    ]),
    ("dividedcd", "Countdown to Divided We Fall", "2012", [
        ("Ultimate Comics Hawkeye", r(1, 4), "", 0),
        ("Ultimate Comics Ultimates", r(1, 6), "", 0),
        ("Ultimate Comics X-Men", r(1, 13), "", 0),
        ("Ultimate Comics Ultimates", r(7, 12), "", 0),
    ]),
    ("divided", "Divided We Fall / United We Stand", "2012–2013", [
        ("Ultimate Comics X-Men", ["14"], "", 0),
        ("Ultimate Comics Ultimates", r(13, 14), "", 0),
        ("Ultimate Comics Spider-Man (2011)", r(13, 14), "", 0),
        ("Ultimate Comics X-Men", ["15"], "", 0),
        ("Ultimate Comics Ultimates", ["15"], "", 0),
        ("Ultimate Comics Spider-Man (2011)", r(15, 16), "", 0),
        ("Ultimate Comics Ultimates", ["16"], "", 0),
        ("Ultimate Comics X-Men", r(16, 17), "", 0),
        ("Ultimate Comics Spider-Man (2011)", ["17"], "", 0),
        ("Ultimate Comics Ultimates", r(17, 18), "", 0),
        ("Ultimate Comics X-Men", ["18", "18.1"], "", 0),
        ("Ultimate Comics Spider-Man (2011)", ["18"], "", 0),
        ("Ultimate Comics Ultimates", ["18.1"], "", 0),
    ]),
    ("cataclysmcd", "Countdown to Cataclysm", "2013", [
        ("Ultimate Comics Spider-Man (2011)", ["16.1"] + r(19, 22), "", 0),
        ("Ultimate Comics X-Men", r(19, 22), "", 0),
        ("Ultimate Comics Ultimates", r(19, 24), "", 0),
        ("Ultimate Comics Wolverine", r(1, 4), "", 0),
        ("Ultimate Comics X-Men", r(23, 33), "", 0),
        ("Ultimate Comics Iron Man", r(1, 4), "", 0),
        ("Ultimate Comics Ultimates", r(25, 30), "", 0),
        ("Ultimate Comics Spider-Man (2011)", r(23, 28), "", 0),
    ]),
    ("cataclysm", "Cataclysm", "2013–2014", [
        ("Hunger", r(1, 4), "", 0),
        ("Cataclysm Point One", ["0.1"], "", 0),
        ("Cataclysm: Ultimate Comics Spider-Man", ["1"], "", 0),
        ("Cataclysm: Ultimate X-Men", r(1, 3), "", 0),
        ("Cataclysm: The Ultimates' Last Stand", ["1"], "", 0),
        ("Cataclysm: Ultimates", ["1"], "", 0),
        ("Cataclysm: The Ultimates' Last Stand", ["2"], "", 0),
        ("Cataclysm: Ultimates", r(2, 3), "", 0),
        ("Cataclysm: Ultimate Comics Spider-Man", r(2, 3), "", 0),
        ("Cataclysm: The Ultimates' Last Stand", r(3, 5), "", 0),
        ("Survive", ["1"], "", 0),
    ]),
    ("aftercat", "After Cataclysm", "2014–2015 · the last of the line", [
        ("Ultimate FF", r(1, 6), "", 0),
        ("All-New Ultimates", r(1, 12), "", 0),
        ("Miles Morales: Ultimate Spider-Man", r(1, 12), "", 0),
    ]),
]


def slug(t):
    s = re.sub(r"[^a-z0-9]+", "-", t.lower())
    return s.strip("-")


def main():
    sections, seen = [], {}
    for sid, title, sub, blocks in ORDER:
        items = []
        for series, nums, note, opt in blocks:
            for i, n in enumerate(nums):
                key = "u-%s-%s" % (slug(series), n)
                # A collision means the same issue was transcribed twice, which
                # is a mistake in the order above, not something to paper over
                # with a suffix — the source lists each issue exactly once.
                assert key not in seen, "%s #%s appears twice" % (series, n)
                seen[key] = True
                x = {"id": key, "t": series, "n": "#" + n}
                if note and i == 0:
                    x["note"] = note
                if opt:
                    x["opt"] = 1
                items.append(x)
        # The header carries every series in *this* section that has a known
        # page, in the order they first appear. Picking only the biggest put
        # "Ultimate Spider-Man" on seven of the fifteen headers, which is noise
        # rather than navigation.
        links, seen_here = [], set()
        for series, _, _, _ in blocks:
            if series in SERIES_URL and series not in seen_here:
                seen_here.add(series)
                links.append({"label": series, "url": SERIES_URL[series]})
        sections.append({"id": sid, "title": title, "sub": sub, "items": items,
                         **({"open": True} if sid == "intro" else {}),
                         **({"links": links} if links else {})})

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    total = len(ids)
    opt = sum(1 for s in sections for x in s["items"] if x.get("opt"))
    series = sorted({x["t"] for s in sections for x in s["items"]})

    prop = {
        "slug": SLUG,
        "title": "Ultimate Marvel",
        "subtitle": "the whole Ultimate universe, in order",
        "kind": "comics",
        "order": 16,
        "year": "2000–2015",
        "blurb": "%d issues across %d series, interleaved the way the line was "
                 "meant to be read." % (total, len(series)),
        "unit": {"one": "issue", "many": "issues"},
        "verb": {"base": "read", "past": "read", "ing": "reading"},
        "tiers": False,
        "notes": [
            ["The interleaving is the point.", "Spider-Man, X-Men, the Ultimates "
             "and the Fantastic Four cut into each other constantly, and working "
             "out that order is the only genuinely hard part of reading this "
             "line. Every issue is listed in the position it goes."],
            ["What's marked optional.", "The %d optional issues are the ones the "
             "source calls inessential or out of continuity — the Daredevil and "
             "Elektra flashbacks, both Ultimate Iron Man series, and Ultimate "
             "Marvel Team-Up #9. They're left in place rather than removed so the "
             "order stays intact." % opt],
            ["Where it ends.", "The line finishes here and its ending is Secret "
             "Wars, which is its own list. The 2024 Ultimate Spider-Man is a "
             "different universe again and is not part of this."],
            ["Links.", "Each section header links to the series it actually "
             "contains, so the links change as you move down the page. %d of the "
             "%d series have a known page; the rest are minis and annuals, and "
             "Marvel gives every series an arbitrary database id that has to be "
             "looked up one at a time. Marvel Unlimited finds any of them by "
             "exact title." % (len(SERIES_URL), len(series))],
            "Order transcribed from the Comic Book Herald Ultimate Marvel "
            "reading order. Its commentary is kept as notes on the entry it "
            "belongs to.",
        ],
        "sections": sections,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json" % SLUG)
    print("  %d sections, %d issues, %d series, %d optional"
          % (len(sections), total, len(series), opt))
    for s in sections:
        print("   %-36s %4d issues" % (s["title"][:36], len(s["items"])))


if __name__ == "__main__":
    main()
