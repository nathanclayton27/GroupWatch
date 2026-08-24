#!/usr/bin/env python3
"""Generate properties/golden-girls.json — the NBC run, 1985-1992.

    python3 tools/make_golden-girls.py

One row per entry in the seven season articles' episode tables: 169 rows
covering all 180 numbered episodes. Eleven entries are numbered as two
episodes each by the lists and sit here as one row spanning both numbers,
exactly as the season articles file them — seven aired as a single hour-long
broadcast (the seven the list page's lede counts), the other four as two
parts a week apart. "One Flew Out of the Cuckoo's Nest" closes the run as
episodes 25-26 of season seven.

Deliberately excluded: the spin-offs and sequel — The Golden Palace, Empty
Nest and Nurses are separate series with their own episode lists — and The
Golden Girls: Their Greatest Moments, a 2003 clip special that aired on
Lifetime eleven years after the finale. The seven Empty Nest crossovers that
fall inside this run are rows here, marked as such.

Episode titles and airdates are machine-read from the seven "The Golden
Girls (season N)" articles by scratch/agent-tv3/extract_tv3.py, which asserts
every season's numbering contiguous and equal to the list page's own Series
overview counts (180 in the lede); the committed result is
tools/data/golden-girls-episodes.json. This script re-asserts the totals, the
seven-hour-long count and the week-apart gaps before it writes anything.

Nothing is weighted: every row counts one, hour-long entries included.
"""
import datetime
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop

SLUG = "golden-girls"
SEASONS = 7
TOTAL = 180
ROWS = 169
HOUR_LONG = 7          # the count the list page's lede states
SPECIAL_YEAR = 2003


def main():
    data = json.loads((pathlib.Path(__file__).resolve().parent / "data"
                       / ("%s-episodes.json" % SLUG)).read_text(encoding="utf-8"))
    assert data["stated"]["lede"] == TOTAL, data["stated"]["lede"]
    assert len(data["seasons"]) == SEASONS, len(data["seasons"])

    sections, hour, split, xovers = [], [], [], []
    for n in range(1, SEASONS + 1):
        rows = data["seasons"][str(n)]
        items = []
        for i, r in enumerate(rows):
            span = (str(r["e"]) if r["e"] == r["e2"]
                    else "%d–%d" % (r["e"], r["e2"]))
            item = {"id": "%s-s%de%d" % (SLUG, n, r["e"]), "t": r["t"],
                    "n": span}
            bits = []
            if n == 1 and r["e"] == 1:
                bits.append("Series premiere")
            if r.get("bdpilot"):
                bits.append("A backdoor pilot for %s" % r["bdpilot"])
            if r.get("xover"):
                bits.append("Crossover with %s" % r["xover"])
            if r["e"] != r["e2"]:
                if r["oneNight"]:
                    hour.append((n, r["t"]))
                    bits.append("Aired as one hour-long episode")
                else:
                    gap = (datetime.date.fromisoformat(r["d2"])
                           - datetime.date.fromisoformat(r["d"])).days
                    assert gap == 7, (n, r["t"], gap)
                    split.append((n, r["t"]))
                    bits.append("Two parts, aired a week apart")
            if r.get("xover"):
                xovers.append((n, r["t"]))
            if n == SEASONS and i == len(rows) - 1:
                bits.insert(0, "Series finale")
            note = prop.join_bits(*bits)
            if note:
                item["note"] = note
            items.append(item)
        count = sum(r["e2"] - r["e"] + 1 for r in rows)
        assert count == data["stated"]["per_season"][str(n)], (n, count)
        sec = {"id": "s%d" % n, "title": "Season %d" % n,
               "sub": "%s · %d episodes" % (data["years"][str(n)], count),
               "items": items}
        if n == 1:
            sec["open"] = True
        sections.append(sec)

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == ROWS, len(ids)
    covered = sum(r["e2"] - r["e"] + 1 for v in data["seasons"].values()
                  for r in v)
    assert covered == TOTAL, covered
    assert len(hour) == HOUR_LONG, hour
    assert len(split) == (TOTAL - ROWS) - HOUR_LONG, split
    assert len(hour) + len(split) == TOTAL - ROWS, (hour, split)
    assert len(xovers) == 7, xovers
    finale = sections[-1]["items"][-1]
    assert finale["t"] == "One Flew Out of the Cuckoo's Nest", finale["t"]
    assert finale["n"] == "25–26", finale["n"]
    assert finale["note"].startswith("Series finale")
    assert sections[0]["items"][0]["t"] == "The Engagement"
    assert [s["t"] for s in data["skipped"]] == \
        ["The Golden Girls: Their Greatest Moments"]
    assert data["skipped"][0]["y"] == SPECIAL_YEAR
    last_year = int(data["seasons"][str(SEASONS)][-1]["d"][:4])
    assert SPECIAL_YEAR - last_year == 11, (SPECIAL_YEAR, last_year)

    p = {
        "slug": SLUG,
        "title": "The Golden Girls",
        "subtitle": "all seven seasons on NBC, 1985–1992",
        "kind": "tv",
        "popularity": 63,
        "year": "1985–1992",
        "blurb": "All 180 episodes in broadcast order — seven seasons in "
                 "Miami, with the hour-long entries kept whole.",
        "unit": {"one": "episode", "many": "episodes"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": "#1F7A7A",
        "accentDark": "#FDDA4C",
        "tiers": False,
        "notes": [
            ["169 rows, 180 episodes.", "Eleven entries are numbered as two "
             "episodes each by the episode lists and sit here as one row "
             "spanning both numbers. Seven of them aired as a single "
             "hour-long broadcast; the other four aired as two parts a week "
             "apart, and each row says which."],
            ["The spin-offs are not listed.", "The Golden Palace, Empty Nest "
             "and Nurses are separate series with their own episode lists. "
             "The seven Empty Nest crossovers that fall inside this run are "
             "rows here and are marked where they land."],
            ["The 2003 retrospective is skipped.", "The Golden Girls: Their "
             "Greatest Moments is a clip special that aired on Lifetime "
             "eleven years after the finale, outside the run's 180 "
             "episodes."],
            ["Nothing is weighted.", "Every row counts one, hour-long "
             "entries included — 169 even marks read better than eleven "
             "slightly wider ones."],
            "Episode titles and airdates machine-read from the seven "
            "Wikipedia season articles; every season's numbering is asserted "
            "contiguous and equal to the episode list's own counts before "
            "this builds.",
        ],
        "sections": sections,
    }

    out = prop.write(p)
    print("wrote %s — %d rows covering %d episodes" % (out.name, len(ids), covered))
    for s in sections:
        print("   %-10s %3d rows  %s" % (s["title"], len(s["items"]), s["sub"]))
    print("   hour-long (%d): %s" % (len(hour), ", ".join(t for _, t in hour)))
    print("   two-part  (%d): %s" % (len(split), ", ".join(t for _, t in split)))
    print("   crossovers(%d): %s" % (len(xovers), ", ".join(t for _, t in xovers)))


if __name__ == "__main__":
    main()
