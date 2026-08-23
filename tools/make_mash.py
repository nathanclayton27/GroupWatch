#!/usr/bin/env python3
"""Generate properties/mash.json — every episode of M*A*S*H.

    python3 tools/make_mash.py

One row per entry in the eleven season articles' episode tables: 251 rows
covering all 256 numbered episodes. Five early-season hour-long broadcasts
(Welcome to Korea, Bug Out, Fade Out Fade In, Our Finest Hour, That's Show
Biz) are numbered as two episodes each by the lists and sit here as one row
spanning both numbers, exactly as the season articles file them — which is
also why the M*A*S*H episode list's own lede counts 251. "Goodbye, Farewell
and Amen" is the 256th and final episode, one two-and-a-half-hour broadcast.

Episode titles and airdates are machine-read from the eleven "M*A*S*H
(season N)" articles by scratch/agent-tv1/extract_sitcoms.py, which asserts
every season's numbering contiguous and equal to the list page's own counts;
the committed result is tools/data/mash-episodes.json.
"""
import json
import pathlib

SLUG = "mash"


def main():
    data = json.loads((pathlib.Path(__file__).resolve().parent / "data"
                       / "mash-episodes.json").read_text(encoding="utf-8"))

    sections = []
    for n in range(1, 12):
        rows = data["seasons"][str(n)]
        items = []
        for r in rows:
            span = ("%d" % r["e"]) if r["e"] == r["e2"] else "%d–%d" % (r["e"], r["e2"])
            row = {"id": "mash-s%d-%d" % (n, r["e"]), "t": r["t"],
                   "n": "S%dE%s" % (n, span)}
            if r["e"] != r["e2"]:
                row["note"] = ("Aired as one hour-long episode" if r["oneNight"]
                               else "Two parts, aired separately")
            if r["t"] == "Goodbye, Farewell and Amen":
                row["note"] = "The series finale — one two-and-a-half-hour broadcast"
            items.append(row)
        count = sum(r["e2"] - r["e"] + 1 for r in rows)
        sec = {"id": "s%d" % n, "title": "Season %d" % n,
               "sub": "%s · %d episodes" % (data["years"][str(n)], count),
               "items": items}
        if n == 1:
            sec["open"] = True
        sections.append(sec)

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert len(ids) == 251, len(ids)
    covered = sum(r["e2"] - r["e"] + 1 for v in data["seasons"].values() for r in v)
    assert covered == 256, covered
    finale = sections[-1]["items"][-1]
    assert finale["t"] == "Goodbye, Farewell and Amen" and finale["id"] == "mash-s11-16"

    prop = {
        "slug": SLUG,
        "title": "M*A*S*H",
        "subtitle": "all 256 episodes, eleven seasons",
        "kind": "tv",
        "order": 74,
        "year": "1972–1983",
        "blurb": "The 4077th in broadcast order — 256 episodes over eleven "
                 "seasons, for a war that lasted three years.",
        "unit": {"one": "episode", "many": "episodes"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "accent": "#4B5320",
        "accentDark": "#A9B46A",
        "tiers": False,
        "notes": [
            ["251 rows, 256 episodes.", "Five hour-long broadcasts are "
             "numbered as two episodes each by the episode lists and sit "
             "here as one row spanning both numbers — the same counting that "
             "makes the list article say 251."],
            ["The finale runs long.", "Goodbye, Farewell and Amen aired as a "
             "single two-and-a-half-hour broadcast and closes the list as "
             "episode 256."],
            "Episode titles and airdates machine-read from the eleven "
            "Wikipedia season articles; every season's numbering is asserted "
            "contiguous and equal to the episode list's own counts before "
            "this builds.",
        ],
        "sections": sections,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json — %d rows covering %d episodes" % (SLUG, len(ids), covered))
    for s in sections:
        print("   %-10s %3d  %s" % (s["title"], len(s["items"]), s.get("sub", "")))


if __name__ == "__main__":
    main()
