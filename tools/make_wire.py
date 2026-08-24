#!/usr/bin/env python3
"""Generate properties/the-wire.json — every episode, one row each.

    python3 tools/make_wire.py

All 60 episodes across five seasons, one row per episode with its real title.
Each season's intro names the institution that season turns on — the street,
the port, city hall, the schools, the paper. That is the show's published
structure, not a spoiler, and the intros say nothing beyond it.

Episode titles and airdates are machine-read from the five "The Wire
(season N)" articles' {{Episode list}} rows by scratch/wire/fetch.py, which
asserts every season's numbering is fully covered; the committed result is
tools/data/wire.json. This script re-asserts the numbering before it writes
anything.

Nothing is weighted: an episode counts as one.
"""
import json
import pathlib

SLUG = "the-wire"
EXPECT = {1: 13, 2: 12, 3: 12, 4: 13, 5: 10}
TOTAL = 60

INTROS = {
    1: "The corners: the drug trade and the detail assigned to it.",
    2: "The port: the docks and the union.",
    3: "City hall: reform and the political machine.",
    4: "The schools: the classrooms and the kids in them.",
    5: "The paper: the newsroom covering all of it.",
}


def year_span(rows):
    ys = sorted({int(r["air"][:4]) for r in rows if r.get("air")})
    assert ys, "no airdates"
    if ys[0] == ys[-1]:
        return str(ys[0])
    a, b = ys[0], ys[-1]
    return "%d–%02d" % (a, b % 100) if a // 100 == b // 100 else "%d–%d" % (a, b)


def main():
    data = json.loads((pathlib.Path(__file__).resolve().parent / "data"
                       / "wire.json").read_text(encoding="utf-8"))

    sections = []
    for n in range(1, 6):
        rows = data[str(n)]
        assert [r["e"] for r in rows] == list(range(1, EXPECT[n] + 1)), \
            "season %d numbering incomplete" % n
        sections.append({
            "id": "s%d" % n, "title": "Season %d" % n,
            "sub": "%s · %d episodes" % (year_span(rows), len(rows)),
            "intro": INTROS[n],
            "items": [{"id": "wire-s%de%d" % (n, r["e"]), "t": r["t"],
                       "n": str(r["e"])} for r in rows]})
    sections[0]["open"] = True

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert len(ids) == TOTAL, len(ids)
    assert sum(len(v) for v in data.values()) == TOTAL

    prop = {
        "slug": SLUG,
        "title": "The Wire",
        "subtitle": "every episode, one institution at a time",
        "kind": "tv",
        "popularity": 74,
        "year": "2002–2008",
        "blurb": "All 60 episodes in broadcast order — five seasons of "
                 "Baltimore, a different institution each year.",
        "unit": {"one": "episode", "many": "episodes"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": "#2E4A5F",
        "accentDark": "#7FA8C9",
        "tiers": False,
        "notes": [
            ["Each season has a beat.", "The street, the port, city hall, "
             "the schools, the paper — the section intros name the "
             "institution a season turns on and nothing more."],
            ["Nothing is weighted.", "An episode counts as one — 60 equal "
             "marks."],
            "Episode titles and airdates machine-read from the five "
            "Wikipedia season articles; every season's numbering is "
            "asserted complete before this builds.",
        ],
        "sections": sections,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json — %d episodes in %d sections" % (SLUG, len(ids),
                                                          len(sections)))
    for s in sections:
        print("   %-10s %3d  %s" % (s["title"], len(s["items"]),
                                    s.get("sub", "")))


if __name__ == "__main__":
    main()
