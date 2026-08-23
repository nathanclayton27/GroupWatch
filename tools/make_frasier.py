#!/usr/bin/env python3
"""Generate properties/frasier.json — the original 1993-2004 run.

    python3 tools/make_frasier.py

One row per entry in the eleven season articles' episode tables: 256 rows
covering all 264 numbered episodes. Eight hour-long entries are numbered as
two episodes each by the lists and sit here as one row spanning both
numbers, exactly as the season articles file them; two of those (Adventures
in Paradise, Mother Load) aired their parts a week apart. "Goodnight,
Seattle" closes the run as episodes 263-264.

Deliberately excluded: the 2023 Paramount+ revival (a different series with
its own episode list), and two unnumbered clip specials the source pages
carry — the 200th-episode outtakes reel (2001) and Analyzing the Laughter
(2004) — which sit outside the run's 264 numbered episodes.

Episode titles and airdates are machine-read from the eleven "Frasier season
N" articles by scratch/agent-tv1/extract_sitcoms.py, which asserts every
season's numbering contiguous and equal to the list page's own counts (264
in the lede); the committed result is tools/data/frasier-episodes.json.
"""
import json
import pathlib

SLUG = "frasier"


def main():
    data = json.loads((pathlib.Path(__file__).resolve().parent / "data"
                       / "frasier-episodes.json").read_text(encoding="utf-8"))

    sections = []
    for n in range(1, 12):
        rows = data["seasons"][str(n)]
        items = []
        for r in rows:
            span = ("%d" % r["e"]) if r["e"] == r["e2"] else "%d–%d" % (r["e"], r["e2"])
            row = {"id": "fra-s%d-%d" % (n, r["e"]), "t": r["t"],
                   "n": "S%dE%s" % (n, span)}
            if r["e"] != r["e2"]:
                row["note"] = ("Aired as one hour-long episode" if r["oneNight"]
                               else "Two parts, aired a week apart")
            if r["t"] == "Goodnight, Seattle":
                row["note"] = "The series finale, aired as one hour-long episode"
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
    assert len(ids) == 256, len(ids)
    covered = sum(r["e2"] - r["e"] + 1 for v in data["seasons"].values() for r in v)
    assert covered == 264, covered
    finale = sections[-1]["items"][-1]
    assert finale["t"] == "Goodnight, Seattle" and finale["id"] == "fra-s11-23"
    assert [s["title"] for s in data["skipped"]] == ["200th Special Outtakes"]

    prop = {
        "slug": SLUG,
        "title": "Frasier",
        "subtitle": "the original run — eleven seasons, 1993–2004",
        "kind": "tv",
        "order": 76,
        "year": "1993–2004",
        "blurb": "All 264 episodes of the original run in broadcast order — "
                 "eleven seasons of tossed salads and scrambled eggs.",
        "unit": {"one": "episode", "many": "episodes"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "accent": "#46586B",
        "accentDark": "#E2D3A8",
        "tiers": False,
        "notes": [
            ["256 rows, 264 episodes.", "Eight hour-long entries are numbered "
             "as two episodes each by the episode lists and sit here as one "
             "row spanning both numbers, exactly as the season articles file "
             "them."],
            ["The 2023 revival is not listed.", "This is the original "
             "1993–2004 run. The Paramount+ revival is a different series "
             "with its own episode list, and it is deliberately excluded."],
            ["Two clip specials are skipped.", "The unnumbered 200th-episode "
             "outtakes reel (2001) and the Analyzing the Laughter "
             "retrospective (2004) sit outside the run's 264 numbered "
             "episodes and are not listed."],
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
