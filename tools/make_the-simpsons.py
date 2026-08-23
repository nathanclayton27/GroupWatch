#!/usr/bin/env python3
"""Generate properties/the-simpsons.json — the golden age, seasons 1-8 only.

    python3 tools/make_the-simpsons.py

One row per episode, 178 rows. The cutoff after season 8 is deliberate and
the property note says where it falls; nothing past "The Secret War of Lisa
Simpson" is listed. Treehouse of Horror episodes carry a small factual note.

Episode titles and airdates are machine-read from the eight Wikipedia
"The Simpsons season N" articles' {{Episode list}} rows by
scratch/agent-tv2/fetch_simpsons.py, which asserts each season's numbering
against the article's own infobox episode count; the committed result is
tools/data/the-simpsons.json. This script re-asserts the numbering before it
writes anything.

Nothing is weighted: an episode counts as one.
"""
import json
import pathlib
import re

SLUG = "the-simpsons"
EXPECT = {1: 13, 2: 22, 3: 24, 4: 22, 5: 22, 6: 25, 7: 25, 8: 25}
TOTAL = 178
TREEHOUSES = 7  # one per season 2-8


def year_span(rows):
    ys = sorted({int(r["air"][:4]) for r in rows if r.get("air")})
    assert ys, "no airdates"
    if ys[0] == ys[-1]:
        return str(ys[0])
    a, b = ys[0], ys[-1]
    return "%d–%02d" % (a, b % 100) if a // 100 == b // 100 else "%d–%d" % (a, b)


def main():
    data = json.loads((pathlib.Path(__file__).resolve().parent / "data"
                       / "the-simpsons.json").read_text(encoding="utf-8"))

    for n, want in EXPECT.items():
        rows = data[str(n)]
        assert [r["e"] for r in rows] == list(range(1, want + 1)), \
            "season %d numbering incomplete" % n

    treehouses = 0

    def section(n):
        nonlocal treehouses
        items = []
        for r in data[str(n)]:
            row = {"id": "simp-s%d-%d" % (n, r["e"]), "t": r["t"],
                   "n": str(r["e"])}
            if r["t"].startswith("Treehouse of Horror"):
                row["note"] = "The annual Halloween anthology — three " \
                              "stand-alone segments"
                treehouses += 1
            items.append(row)
        rows = data[str(n)]
        return {"id": "s%d" % n, "title": "Season %d" % n,
                "sub": "%s · %d episodes" % (year_span(rows), len(rows)),
                "items": items}

    sections = [section(n) for n in range(1, 9)]
    sections[0]["open"] = True
    assert treehouses == TREEHOUSES, treehouses

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert all(re.fullmatch(r"[a-z0-9-]+", i) for i in ids)
    assert len(ids) == TOTAL, len(ids)

    prop = {
        "slug": SLUG,
        "title": "The Simpsons",
        "subtitle": "the golden age — seasons 1–8",
        "kind": "tv",
        "order": 79,
        "year": "1989–97",
        "blurb": "Seasons 1 through 8, one row per episode — 178 episodes "
                 "of the golden age, and nothing after.",
        "unit": {"one": "episode", "many": "episodes"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": "#C2477E",
        "accentDark": "#F2C744",
        "tiers": False,
        "notes": [
            ["The cutoff is deliberate.", "The list ends after season 8 — "
             "\"Homer's Enemy\" territory, where the conventional golden-age "
             "line is drawn."],
            ["Treehouse of Horror counts one each.", "The Halloween "
             "anthologies are regular episodes of their seasons and sit in "
             "broadcast position, noted on the row."],
            "Episode titles and airdates machine-read from the eight "
            "Wikipedia season articles (The Simpsons season 1–8); each "
            "season's numbering is asserted against the article's own "
            "episode count before this builds.",
        ],
        "sections": sections,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json — %d episodes in %d sections (%d Treehouses noted)"
          % (SLUG, len(ids), len(sections), treehouses))
    for s in sections:
        print("   %-10s %3d  %s" % (s["title"], len(s["items"]),
                                    s.get("sub", "")))


if __name__ == "__main__":
    main()
