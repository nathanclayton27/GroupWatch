#!/usr/bin/env python3
"""Generate properties/twilight-zone.json — the 1959 original, every episode.

    python3 tools/make_twilight-zone.py

One row per episode, 156 rows across the five 1959-1964 seasons. It is an
anthology, so the property sets random:true — the "Pick one for me" button is
the intended way in, and a note says so. Season 4 is the hour-long season and
its section intro states that factually.

Episode titles and airdates are machine-read from the five Wikipedia
"The Twilight Zone season N" articles' {{Episode list}} rows by
scratch/agent-tv2/fetch_twilight.py, which asserts each season's numbering
against the article's own infobox episode count; the committed result is
tools/data/twilight-zone.json. This script re-asserts the numbering before it
writes anything.

Nothing is weighted: an episode counts as one, even the hour-long ones —
episode count is the unit, and the season 4 intro carries the length fact.
"""
import json
import pathlib
import re

SLUG = "twilight-zone"
EXPECT = {1: 36, 2: 29, 3: 37, 4: 18, 5: 36}
TOTAL = 156


def year_span(rows):
    ys = sorted({int(r["air"][:4]) for r in rows if r.get("air")})
    assert ys, "no airdates"
    if ys[0] == ys[-1]:
        return str(ys[0])
    a, b = ys[0], ys[-1]
    return "%d–%02d" % (a, b % 100) if a // 100 == b // 100 else "%d–%d" % (a, b)


def main():
    data = json.loads((pathlib.Path(__file__).resolve().parent / "data"
                       / "twilight-zone.json").read_text(encoding="utf-8"))

    for n, want in EXPECT.items():
        rows = data[str(n)]
        assert [r["e"] for r in rows] == list(range(1, want + 1)), \
            "season %d numbering incomplete" % n

    def section(n):
        rows = data[str(n)]
        sec = {"id": "s%d" % n, "title": "Season %d" % n,
               "sub": "%s · %d episodes" % (year_span(rows), len(rows)),
               "items": [{"id": "tz-s%d-%d" % (n, r["e"]),
                          "t": r["t"], "n": str(r["e"])} for r in rows]}
        return sec

    sections = [section(n) for n in range(1, 6)]
    sections[0]["open"] = True
    sections[3]["intro"] = ("The hour-long season: CBS ran these eighteen "
                            "episodes at double the usual length before "
                            "returning to the half hour for season 5.")

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert all(re.fullmatch(r"[a-z0-9-]+", i) for i in ids)
    assert len(ids) == TOTAL, len(ids)

    prop = {
        "slug": SLUG,
        "title": "The Twilight Zone",
        "subtitle": "the original series — five seasons, 1959–1964",
        "kind": "tv",
        "order": 78,
        "year": "1959–64",
        "blurb": "All 156 episodes of the 1959 original — standalone doors "
                 "into the fifth dimension, built for the random picker.",
        "unit": {"one": "episode", "many": "episodes"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": "#443E63",
        "accentDark": "#B4ABDE",
        "tiers": False,
        "random": True,
        "notes": [
            ["An anthology wants the picker.", "Every episode stands alone, "
             "so the Pick one for me button is the intended front door — no "
             "arc to spoil, no order to owe."],
            ["Season 4 ran long.", "Its eighteen episodes were broadcast at "
             "an hour instead of the usual half hour; they still count one "
             "each."],
            "Episode titles and airdates machine-read from the five "
            "Wikipedia season articles (The Twilight Zone season 1–5); each "
            "season's numbering is asserted against the article's own "
            "episode count before this builds.",
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
