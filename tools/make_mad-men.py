#!/usr/bin/env python3
"""Generate properties/mad-men.json — every episode, one row each.

    python3 tools/make_mad-men.py

All 92 episodes across seven seasons. Season 7 aired in two halves — seven
episodes in spring 2014, seven in spring 2015 — but its season article
numbers them 1-14 in one table, so it is one section here with the split
stated in the intro. The two-hour premieres of seasons 5 and 6 carry two
episode numbers in the tables (the infoboxes count both); each number is a
row here, noted on the row.

Episode titles and airdates are machine-read from the seven Wikipedia
"Mad Men season N" articles' {{Episode list}} rows by
scratch/agent-tv2/fetch_madmen.py, which asserts each season's numbering
against the article's own infobox episode count; the committed result is
tools/data/mad-men.json. This script re-asserts the numbering before it
writes anything.

Nothing is weighted: an episode counts as one.
"""
import json
import pathlib
import re

SLUG = "mad-men"
EXPECT = {1: 13, 2: 13, 3: 13, 4: 13, 5: 13, 6: 13, 7: 14}
TOTAL = 92


def year_span(rows):
    ys = sorted({int(r["air"][:4]) for r in rows if r.get("air")})
    assert ys, "no airdates"
    if ys[0] == ys[-1]:
        return str(ys[0])
    a, b = ys[0], ys[-1]
    return "%d–%02d" % (a, b % 100) if a // 100 == b // 100 else "%d–%d" % (a, b)


def main():
    data = json.loads((pathlib.Path(__file__).resolve().parent / "data"
                       / "mad-men.json").read_text(encoding="utf-8"))

    for n, want in EXPECT.items():
        rows = data[str(n)]
        assert [r["e"] for r in rows] == list(range(1, want + 1)), \
            "season %d numbering incomplete" % n

    # the 7A/7B split the intro states, straight from the air dates
    assert [r["e"] for r in data["7"] if r["air"] < "2015"] == list(range(1, 8))
    assert [r["e"] for r in data["7"] if r["air"] >= "2015"] == list(range(8, 15))

    doubles = 0

    def section(n):
        nonlocal doubles
        rows = data[str(n)]
        items = []
        for r in rows:
            row = {"id": "mm-s%d-%d" % (n, r["e"]), "t": r["t"],
                   "n": str(r["e"])}
            if r.get("np") == 2:
                row["note"] = ("Aired with the %s episode as one two-hour "
                               "premiere"
                               % ("next" if r["pi"] == 1 else "previous"))
                doubles += 1
            items.append(row)
        return {"id": "s%d" % n, "title": "Season %d" % n,
                "sub": "%s · %d episodes" % (year_span(rows), len(rows)),
                "items": items}

    sections = [section(n) for n in range(1, 8)]
    sections[0]["open"] = True
    sections[6]["intro"] = ("Aired in two halves — episodes 1–7 in spring "
                            "2014, 8–14 in spring 2015 — and numbered "
                            "straight through, the way the season table "
                            "files it.")
    assert doubles == 4, doubles  # seasons 5 and 6 premieres, two rows each

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert all(re.fullmatch(r"[a-z0-9-]+", i) for i in ids)
    assert len(ids) == TOTAL, len(ids)

    prop = {
        "slug": SLUG,
        "title": "Mad Men",
        "subtitle": "every episode across seven seasons",
        "kind": "tv",
        "popularity": 67,
        "year": "2007–15",
        "blurb": "All 92 episodes in broadcast order — seven seasons of "
                 "Sterling Cooper and what it becomes.",
        "unit": {"one": "episode", "many": "episodes"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": "#A63A31",
        "accentDark": "#C98B4B",
        "tiers": False,
        "notes": [
            ["Season 7 is one season.", "AMC split it across 2014 and "
             "2015; the table numbers its fourteen episodes straight "
             "through, so it is one section with the split stated in the "
             "intro."],
            ["Two premieres aired double.", "Seasons 5 and 6 each opened "
             "with a two-hour broadcast carrying two episode numbers; both "
             "numbers are rows here, noted on the row."],
            "Episode titles and airdates machine-read from the seven "
            "Wikipedia season articles (Mad Men season 1–7); each season's "
            "numbering is asserted against the article's own episode count "
            "before this builds.",
        ],
        "sections": sections,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json — %d episodes in %d sections (%d part-rows noted)"
          % (SLUG, len(ids), len(sections), doubles))
    for s in sections:
        print("   %-10s %3d  %s" % (s["title"], len(s["items"]),
                                    s.get("sub", "")))


if __name__ == "__main__":
    main()
