#!/usr/bin/env python3
"""Generate properties/gilmore-girls.json — the run, plus the 2016 revival.

    python3 tools/make_gilmore-girls.py

One row per episode, 157 rows: all 153 episodes of the 2000-2007 series, then
the four chapters of Gilmore Girls: A Year in the Life as their own final
section. Nothing in the seven season tables spans two episode numbers, so
rows and episodes match one for one.

The revival sits after season seven rather than inside it, the way the films
sit between the right seasons on the X-Files property: it is a separate
Netflix release made nine years later, and burying it as "season eight"
would misfile both the gap and the length.

Episode titles and airdates are machine-read from the seven "Gilmore Girls
(season N)" articles by scratch/agent-tv3/extract_tv3.py, which asserts every
season's numbering contiguous and equal to the list page's own Series
overview counts (153 in the lede); the revival's four chapters and its
88-102 minute runtime range come from that miniseries' own article. The
committed result is tools/data/gilmore-girls-episodes.json.

Nothing is weighted: an episode and a revival chapter count one each. Four
very wide marks next to 153 thin ones would read worse than 157 even ones,
and no per-episode runtimes exist to weight the other 153 by.
"""
import datetime
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop

SLUG = "gilmore-girls"
SEASONS = 7
RUN_TOTAL = 153
REVIVAL = 4


def main():
    data = json.loads((pathlib.Path(__file__).resolve().parent / "data"
                       / ("%s-episodes.json" % SLUG)).read_text(encoding="utf-8"))
    assert data["stated"]["lede"] == RUN_TOTAL, data["stated"]["lede"]
    assert len(data["seasons"]) == SEASONS, len(data["seasons"])
    rev = data["revival"]
    assert rev["num_episodes"] == REVIVAL and len(rev["chapters"]) == REVIVAL

    sections = []
    for n in range(1, SEASONS + 1):
        rows = data["seasons"][str(n)]
        items = []
        for r in rows:
            assert r["e"] == r["e2"], (n, r)      # no merged entries here
            item = {"id": "%s-s%de%d" % (SLUG, n, r["e"]), "t": r["t"],
                    "n": str(r["e"])}
            bits = []
            if n == 1 and r["e"] == 1:
                bits.append("Series premiere")
            if r.get("bdpilot"):
                bits.append("Written as a backdoor pilot for a spin-off "
                            "called %s" % r["bdpilot"])
            if n == SEASONS and r["e"] == len(rows):
                bits.append("Finale of the original run")
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
        if n == SEASONS:
            sec["intro"] = ("The move to The CW, and the only season without "
                            "Amy Sherman-Palladino or Daniel Palladino as "
                            "showrunner or writer.")
        sections.append(sec)

    finale = datetime.date.fromisoformat(
        data["seasons"][str(SEASONS)][-1]["d"])
    released = datetime.date.fromisoformat(rev["released"])
    gap = (released - finale).days // 365
    assert gap == 9, gap
    assert rev["runtime"] == "88–102 minutes", rev["runtime"]

    sections.append({
        "id": "ayitl", "title": "A Year in the Life",
        "sub": "2016 · %d episodes" % REVIVAL,
        "intro": "Four feature-length chapters, %s each, released together on "
                 "Netflix nine years after the finale." % rev["runtime"],
        "items": [{"id": "%s-ayitl-%d" % (SLUG, c["e"]), "t": c["t"],
                   "n": str(c["e"])} for c in rev["chapters"]],
    })

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == RUN_TOTAL + REVIVAL, len(ids)
    covered = sum(r["e2"] - r["e"] + 1 for v in data["seasons"].values()
                  for r in v)
    assert covered == RUN_TOTAL, covered
    assert sections[0]["items"][0]["t"] == "Pilot"
    assert sections[SEASONS - 1]["items"][-1]["t"] == "Bon Voyage"
    assert [x["t"] for x in sections[-1]["items"]] == \
        ["Winter", "Spring", "Summer", "Fall"]
    assert data["networks"] == {"1-6": "The WB", "7": "The CW"}
    assert data["s7_no_palladino"] is True

    p = {
        "slug": SLUG,
        "title": "Gilmore Girls",
        "subtitle": "seven seasons, then the four-chapter revival",
        "kind": "tv",
        "popularity": 65,
        "year": "2000–2016",
        "blurb": "All 153 episodes of the original run in broadcast order, "
                 "plus the four chapters of A Year in the Life as their own "
                 "final section.",
        "unit": {"one": "episode", "many": "episodes"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": "#5C4033",
        "accentDark": "#E8B87A",
        "tiers": False,
        "notes": [
            ["The revival is its own section.", "A Year in the Life is four "
             "feature-length chapters made nine years after the finale and "
             "released together on Netflix, so it sits after season seven "
             "rather than inside it."],
            ["Two networks, one run.", "Seasons one to six aired on The WB; "
             "the seventh and last aired on The CW after the merger."],
            ["Season seven is the odd one out.", "It is the only season with "
             "neither Amy Sherman-Palladino nor Daniel Palladino as "
             "showrunner or writer."],
            ["Nothing is weighted.", "An episode and a revival chapter count "
             "one each — 157 even marks read better than four very wide ones "
             "beside 153 thin ones, and no per-episode runtimes exist to "
             "weight the rest by."],
            "Episode titles and airdates machine-read from the seven "
            "Wikipedia season articles and from the revival's own article; "
            "every season's numbering is asserted contiguous and equal to the "
            "episode list's own counts before this builds.",
        ],
        "sections": sections,
    }

    out = prop.write(p)
    print("wrote %s — %d rows (%d episodes + %d revival chapters)"
          % (out.name, len(ids), covered, REVIVAL))
    for s in sections:
        print("   %-20s %3d  %s" % (s["title"], len(s["items"]), s["sub"]))
    for s in sections:
        for x in s["items"]:
            if x.get("note"):
                print("   note  %-30s %s" % (x["t"][:30], x["note"]))


if __name__ == "__main__":
    main()
