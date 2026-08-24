#!/usr/bin/env python3
"""Generate properties/the-sopranos.json — every episode, one row each.

    python3 tools/make_sopranos.py

All 86 episodes across six seasons, one row per episode with its real title.
Season six aired in two parts and its Wikipedia season article files it that
way — twelve episodes in 2006, nine in 2007 — so it is two sections here,
"Season 6, Part I" and "Season 6, Part II", numbered 1–21 continuously the
way the source numbers them.

Episode titles and airdates are machine-read from the six "The Sopranos
(season N)" articles' {{Episode list}} rows by scratch/sopranos/fetch.py,
which asserts every season's numbering is fully covered; the committed result
is tools/data/sopranos.json. This script re-asserts the numbering before it
writes anything.

Nothing is weighted: an episode counts as one.
"""
import json
import pathlib

SLUG = "the-sopranos"
EXPECT = {1: 13, 2: 13, 3: 13, 4: 13, 5: 13, 6: 21}
TOTAL = 86


def year_span(rows):
    ys = sorted({int(r["air"][:4]) for r in rows if r.get("air")})
    assert ys, "no airdates"
    if ys[0] == ys[-1]:
        return str(ys[0])
    a, b = ys[0], ys[-1]
    return "%d–%02d" % (a, b % 100) if a // 100 == b // 100 else "%d–%d" % (a, b)


def main():
    data = json.loads((pathlib.Path(__file__).resolve().parent / "data"
                       / "sopranos.json").read_text(encoding="utf-8"))

    for n in EXPECT:
        rows = data[str(n)]
        assert [r["e"] for r in rows] == list(range(1, EXPECT[n] + 1)), \
            "season %d numbering incomplete" % n

    def section(n, sec_id, title, rows):
        return {"id": sec_id, "title": title,
                "sub": "%s · %d episodes" % (year_span(rows), len(rows)),
                "items": [{"id": "sop-s%de%d" % (n, r["e"]),
                           "t": r["t"], "n": str(r["e"])} for r in rows]}

    sections = [section(n, "s%d" % n, "Season %d" % n, data[str(n)])
                for n in range(1, 6)]
    sections[0]["open"] = True

    s6 = data["6"]
    p1 = [r for r in s6 if r.get("part") == 1]
    p2 = [r for r in s6 if r.get("part") == 2]
    assert [r["e"] for r in p1] == list(range(1, 13)), "part I is episodes 1-12"
    assert [r["e"] for r in p2] == list(range(13, 22)), "part II is episodes 13-21"
    sections.append(section(6, "s6p1", "Season 6, Part I", p1))
    sections.append(section(6, "s6p2", "Season 6, Part II", p2))

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert len(ids) == TOTAL, len(ids)
    assert sum(len(v) for v in data.values()) == TOTAL

    prop = {
        "slug": SLUG,
        "title": "The Sopranos",
        "subtitle": "every episode across six seasons",
        "kind": "tv",
        "popularity": 81,
        "year": "1999–2007",
        "blurb": "All 86 episodes in broadcast order — six seasons, two "
                 "families, one New Jersey.",
        "unit": {"one": "episode", "many": "episodes"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": "#6B1F1F",
        "accentDark": "#D97070",
        "tiers": False,
        "notes": [
            ["Season six aired in two parts.", "Twelve episodes in 2006 and "
             "nine in 2007, numbered 1–21 as one season — listed here the "
             "way HBO aired it and the way its season article files it."],
            ["Nothing is weighted.", "An episode counts as one — 86 equal "
             "marks."],
            "Episode titles and airdates machine-read from the six Wikipedia "
            "season articles; every season's numbering is asserted complete "
            "before this builds.",
        ],
        "sections": sections,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json — %d episodes in %d sections" % (SLUG, len(ids),
                                                          len(sections)))
    for s in sections:
        print("   %-20s %3d  %s" % (s["title"], len(s["items"]),
                                    s.get("sub", "")))


if __name__ == "__main__":
    main()
