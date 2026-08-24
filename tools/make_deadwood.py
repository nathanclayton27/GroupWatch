#!/usr/bin/env python3
"""Generate properties/deadwood.json — three seasons and the film.

    python3 tools/make_deadwood.py

All 36 episodes across the three 12-episode seasons, one row each, plus
Deadwood: The Movie (2019) as a final one-row section. The unit is "entry"
rather than "episode" because the film is in the list — the same call
x-files makes.

Episode titles and airdates are machine-read from Wikipedia's "List of
Deadwood episodes" — one page carries all three seasons and the film — by
scratch/agent-tv2/fetch_deadwood.py, which asserts the page's own stated
total ("36 episodes over three 12-episode seasons") and the film's premiere
date; the committed result is tools/data/deadwood.json. This script
re-asserts the numbering before it writes anything.

Nothing is weighted: an episode and the film count one each.
"""
import json
import pathlib
import re

SLUG = "deadwood"
TOTAL = 37  # 36 episodes + the film


def year_span(rows):
    ys = sorted({int(r["air"][:4]) for r in rows if r.get("air")})
    assert ys, "no airdates"
    if ys[0] == ys[-1]:
        return str(ys[0])
    a, b = ys[0], ys[-1]
    return "%d–%02d" % (a, b % 100) if a // 100 == b // 100 else "%d–%d" % (a, b)


def main():
    data = json.loads((pathlib.Path(__file__).resolve().parent / "data"
                       / "deadwood.json").read_text(encoding="utf-8"))

    for n in (1, 2, 3):
        rows = data[str(n)]
        assert [r["e"] for r in rows] == list(range(1, 13)), \
            "season %d numbering incomplete" % n
    assert data["movie"]["t"] == "Deadwood: The Movie"
    assert data["movie"]["air"] == "2019-05-31"

    def section(n):
        rows = data[str(n)]
        return {"id": "s%d" % n, "title": "Season %d" % n,
                "sub": "%s · 12 episodes" % year_span(rows),
                "items": [{"id": "dw-s%d-%d" % (n, r["e"]),
                           "t": r["t"], "n": str(r["e"])} for r in rows]}

    sections = [section(n) for n in (1, 2, 3)]
    sections[0]["open"] = True
    sections.append({
        "id": "movie", "title": "The Movie",
        "sub": "2019 · the finale, thirteen years on",
        "items": [{"id": "dw-movie-2019", "t": data["movie"]["t"],
                   "n": "2019"}],
    })

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert all(re.fullmatch(r"[a-z0-9-]+", i) for i in ids)
    assert len(ids) == TOTAL, len(ids)

    prop = {
        "slug": SLUG,
        "title": "Deadwood",
        "subtitle": "three seasons and the film that ends it",
        "kind": "tv & film",
        "popularity": 53,
        "year": "2004–19",
        "blurb": "All 36 episodes and the 2019 film in broadcast order — "
                 "three seasons of the camp, then the goodbye.",
        "unit": {"one": "entry", "many": "entries"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": "#4C3B26",
        "accentDark": "#C9A227",
        "tiers": False,
        "notes": [
            ["The film closes it.", "HBO ended the series after season 3 "
             "in 2006; Deadwood: The Movie arrived in 2019 and is the "
             "final row."],
            ["Nothing is weighted.", "An episode and the film count one "
             "each — 37 even marks."],
            "Episode titles and airdates machine-read from Wikipedia's "
            "List of Deadwood episodes; the page's own stated total (36 "
            "episodes over three 12-episode seasons) and the film's "
            "premiere date are asserted before this builds.",
        ],
        "sections": sections,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json — %d rows (36 episodes + the film)" % (SLUG, len(ids)))
    for s in sections:
        print("   %-10s %3d  %s" % (s["title"], len(s["items"]),
                                    s.get("sub", "")))


if __name__ == "__main__":
    main()
