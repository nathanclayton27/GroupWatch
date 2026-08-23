#!/usr/bin/env python3
"""Generate properties/lost.json — every numbered episode, six seasons.

    python3 tools/make_lost.py

One row per numbered episode, 121 rows, counting the two-part premieres and
finales exactly as the season tables do: the tables file each of those as one
entry spanning two episode numbers (the infoboxes count both), so both
numbers get a row here and the rows say how they aired. The two parts of the
pilot aired on separate nights; every other pair aired as one double-length
broadcast. The Missing Pieces mobisodes are not episodes of the broadcast run
and are excluded.

Episode titles and airdates are machine-read from the six Wikipedia
"Lost season N" articles' {{Episode list}} rows by
scratch/agent-tv2/fetch_lost.py, which asserts each season's numbering
against the article's own infobox episode count (season 1 says 25, pilot
parts included); the committed result is tools/data/lost.json. This script
re-asserts the numbering before it writes anything.

Nothing is weighted: an episode counts as one.
"""
import json
import pathlib
import re

SLUG = "lost"
EXPECT = {1: 25, 2: 24, 3: 23, 4: 14, 5: 17, 6: 18}
TOTAL = 121


def year_span(rows):
    ys = sorted({int(r["air"][:4]) for r in rows if r.get("air")})
    assert ys, "no airdates"
    if ys[0] == ys[-1]:
        return str(ys[0])
    a, b = ys[0], ys[-1]
    return "%d–%02d" % (a, b % 100) if a // 100 == b // 100 else "%d–%d" % (a, b)


def main():
    data = json.loads((pathlib.Path(__file__).resolve().parent / "data"
                       / "lost.json").read_text(encoding="utf-8"))

    for n, want in EXPECT.items():
        rows = data[str(n)]
        assert [r["e"] for r in rows] == list(range(1, want + 1)), \
            "season %d numbering incomplete" % n

    doubles = 0

    def section(n):
        nonlocal doubles
        rows = data[str(n)]
        items = []
        for i, r in enumerate(rows):
            row = {"id": "lost-s%d-%d" % (n, r["e"]), "t": r["t"],
                   "n": str(r["e"])}
            if r.get("np") == 2:
                partner = rows[i + 1] if r["pi"] == 1 else rows[i - 1]
                assert partner["t"] == r["t"] and partner.get("np") == 2
                if partner["air"] != r["air"]:
                    # only the pilot: its parts aired a week apart
                    assert r["t"] == "Pilot"
                    row["note"] = "Part %d of the two-part pilot" % r["pi"]
                else:
                    row["note"] = ("Aired with the %s episode as one "
                                   "double-length broadcast"
                                   % ("next" if r["pi"] == 1 else "previous"))
                doubles += 1
            items.append(row)
        return {"id": "s%d" % n, "title": "Season %d" % n,
                "sub": "%s · %d episodes" % (year_span(rows), len(rows)),
                "items": items}

    sections = [section(n) for n in range(1, 7)]
    sections[0]["open"] = True
    # the pilot plus seven double-length premiere/finale blocks, two rows
    # each: Exodus (Parts 2 & 3), Live Together Die Alone, Through the
    # Looking Glass, There's No Place Like Home (Parts 2 & 3), The
    # Incident, LA X, The End
    assert doubles == 16, doubles

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert all(re.fullmatch(r"[a-z0-9-]+", i) for i in ids)
    assert len(ids) == TOTAL, len(ids)

    prop = {
        "slug": SLUG,
        "title": "Lost",
        "subtitle": "every numbered episode, six seasons",
        "kind": "tv",
        "order": 81,
        "year": "2004–10",
        "blurb": "All 121 episodes in broadcast order — six seasons, one "
                 "island, counted the way the season tables count them.",
        "unit": {"one": "episode", "many": "episodes"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": "#1B2D20",
        "accentDark": "#96E8A9",
        "tiers": False,
        "notes": [
            ["Counted as the tables count.", "Two-part premieres and "
             "finales carry two episode numbers even where they aired as "
             "one long broadcast; each number is a row here, noted on the "
             "row — 121 in all."],
            ["The mobisodes are out.", "Lost: Missing Pieces (2007–08) is "
             "a set of thirteen web shorts, not episodes of the broadcast "
             "run, and is not listed."],
            "Episode titles and airdates machine-read from the six "
            "Wikipedia season articles (Lost season 1–6); each season's "
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
