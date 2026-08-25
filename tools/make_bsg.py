#!/usr/bin/env python3
"""Generate properties/battlestar-galactica.json — the 2004 series, in broadcast order.

    python3 tools/make_bsg.py

77 rows: the two nights of the 2003 miniseries, all 74 episodes across the four
seasons, and both television films sitting where they were broadcast — Razor
between seasons 3 and 4, The Plan after the finale. The unit is "entry" rather
than "episode" because the films are in the list, the same call deadwood and
x-files make.

ORDER: broadcast, the default. This show has famously argued alternative
running orders — almost all of them about where Razor and The Plan go, since
both are set earlier than they were shown — and this list is deliberately not
one of them. Nothing here needed a source to justify a departure, because there
is no departure: the sequence is the sequence Wikipedia's "List of Battlestar
Galactica (2004 TV series) episodes" files, section for section.

SCOPE: Caprica (2010) and Blood & Chrome (2012) are excluded. They are separate
series with their own runs, their own casts and their own reception; folding
them in would make this a franchise list rather than a list of the 2004 show.
The online webisode shorts are excluded on the same reasoning — released beside
the seasons rather than broadcast as part of them.

Titles, numbering and airdates are machine-read by scratch/bsg/fetch.py from
the list page and the four "Battlestar Galactica season N" articles it
transcludes; that script asserts the list page's own {{Series overview}} counts
(2 miniseries parts, then 13/20/20/21) and an unbroken 1-76 series numbering
across season 1 -> Razor -> season 4. The committed result is
scratch/bsg/bsg.json. This script re-asserts every count before it writes.

Two rows cover two numbered slots each, because one broadcast did: Razor
(series 54-55) and the finale's second and third parts (season 4's 20-21).

Nothing is weighted. Per-row runtimes are not published for the 74 episodes —
the series article gives one blanket "44 minutes" — while the miniseries runs
180 minutes and the two films 81 and 112. Weighting the three rows that do have
a published runtime and leaving the rest bare would silently count every bare
row as one hour, so no row carries a weight and every row counts as one.
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop  # noqa: E402

SLUG = "battlestar-galactica"
DATA = prop.ROOT / "scratch" / "bsg" / "bsg.json"

MINI = 2
EXPECT = {1: 13, 2: 20, 3: 20, 4: 21}
ROWS = 77

SEASON_SUB = {1: "2004–05", 2: "2005–06", 3: "2006–07", 4: "2008–09"}

SEASON_INTRO = {
    1: "First broadcast on Sky1 in the United Kingdom from October 2004; the "
       "Sci-Fi Channel ran the same thirteen from January 2005.",
    2: "Broadcast in two runs: ten episodes from July 2005, ten more from "
       "January 2006.",
    3: "Twenty episodes from October 2006 to March 2007, opening with a "
       "two-hour premiere.",
    4: "Broadcast in two runs: ten episodes from April 2008, the remaining "
       "eleven from January 2009. The finale's second and third parts went "
       "out together as one broadcast and are one row.",
}


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    assert data["stated"] == {"0": MINI, **{str(k): v for k, v in EXPECT.items()}}, \
        data["stated"]

    mini = data["miniseries"]
    assert len(mini) == MINI, len(mini)
    assert [m["air"] for m in mini] == ["2003-12-08", "2003-12-09"], mini

    # ---- every factual claim the section intros make, checked against the
    # airdates rather than trusted. Prose that nothing verifies is how a
    # generator ends up describing a broadcast pattern the data contradicts.
    def airs(n):
        return [r["air"] for r in data["seasons"][str(n)]]

    s1 = data["seasons"]["1"]
    assert all(r.get("air2") for r in s1), "season 1 lost its Sci-Fi dates"
    assert airs(1)[0].startswith("2004-10") and s1[0]["air2"].startswith("2005-01")
    assert sum(a[:4] == "2005" for a in airs(2)) == 10, airs(2)   # two runs of ten
    assert sum(a[:4] == "2006" for a in airs(2)) == 10, airs(2)
    assert airs(3)[0] == airs(3)[1] == "2006-10-06", airs(3)[:2]  # two-hour opener
    assert airs(3)[-1].startswith("2007-03"), airs(3)[-1]
    assert sum(a[:4] == "2008" for a in airs(4)) == 10, airs(4)
    assert sum(a[:4] == "2009" for a in airs(4)) == 10, airs(4)   # 10 rows, 11 eps

    sections = [{
        "id": "mini", "title": "Miniseries", "sub": "2003 · two nights",
        "intro": "The pilot miniseries, broadcast over two nights in December "
                 "2003. Its two halves carry no titles of their own — the rows "
                 "are the two nights.",
        "open": True,
        "items": [{"id": "bsg-mini-%d" % i, "t": "Night %d" % i, "n": str(i)}
                  for i in (1, 2)],
    }]

    def season_section(n):
        rows = data["seasons"][str(n)]
        span = []
        items = []
        for r in rows:
            span += list(range(r["e"], r["e2"] + 1))
            item = {"id": "bsg-s%de%d" % (n, r["e"]),
                    "t": r["titles"][0], "n": str(r["e"])}
            if r["e"] != r["e2"]:
                assert len(r["titles"]) == 2, r
                # "Daybreak (Part 2)" + "Daybreak (Part 3)" -> one row titled
                # by the parts it carries, NOT by the episode numbers it spans
                stem = r["titles"][0].split(" (Part")[0]
                pn = []
                for t in r["titles"]:
                    m = re.fullmatch(re.escape(stem) + r" \(Part (\d+)\)", t)
                    assert m, t
                    pn.append(int(m.group(1)))
                assert pn[1] == pn[0] + 1, pn
                item["t"] = "%s (Parts %d and %d)" % (stem, pn[0], pn[1])
                item["n"] = "%d–%d" % (r["e"], r["e2"])
                item["note"] = "Both parts went out as one broadcast"
            items.append(item)
        assert span == list(range(1, EXPECT[n] + 1)), (n, span)
        return {"id": "s%d" % n, "title": "Season %d" % n,
                "sub": "%s · %d episodes" % (SEASON_SUB[n], EXPECT[n]),
                "intro": SEASON_INTRO[n], "items": items}

    sections += [season_section(n) for n in (1, 2, 3)]

    razor = data["razor"]
    assert razor["titles"] == ["Razor"] and razor["overall"] == [54, 55], razor
    assert razor["air"] == "2007-11-24", razor
    sections.append({
        "id": "razor", "title": "Razor",
        "sub": "2007 · the first television film",
        "intro": "Feature length, first shown between seasons 3 and 4, and "
                 "kept in that slot here. Its story is set earlier than that — "
                 "inside season 2 — but it was made and broadcast after season "
                 "3 ended.",
        "items": [{"id": "bsg-razor", "t": "Battlestar Galactica: Razor",
                   "n": "2007"}],
    })

    sections.append(season_section(4))

    plan = data["plan"]
    assert plan["titles"] == ["The Plan"], plan
    assert plan["air"] == "2009-10-27" and plan["air2"] == "2010-01-10", plan
    sections.append({
        "id": "plan", "title": "The Plan",
        "sub": "2009 · the second television film",
        "intro": "Released on disc in October 2009 and broadcast on the Sci-Fi "
                 "Channel in January 2010 — after the finale either way, which "
                 "is where broadcast order puts it.",
        "items": [{"id": "bsg-plan", "t": "Battlestar Galactica: The Plan",
                   "n": "2009"}],
    })

    episodes = sum(len(x["items"]) for x in sections
                   if x["id"].startswith("s"))
    assert episodes == 73, episodes            # 74 episodes, 73 rows
    assert len(sections) == 7, len(sections)

    p = {
        "slug": SLUG,
        "title": "Battlestar Galactica",
        "subtitle": "the 2004 series, in broadcast order",
        "kind": "tv & film",
        "popularity": 62,
        "year": "2003–2009",
        "blurb": "The 2003 miniseries, all 74 episodes and both television "
                 "films in the order they were broadcast — 77 entries.",
        "unit": {"one": "entry", "many": "entries"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": "#24889E",
        "accentDark": "#EF5B3C",
        "tiers": False,
        "notes": [
            ["Broadcast order.", "The miniseries, then the four seasons, with "
             "each television film where it landed: Razor between seasons 3 "
             "and 4, The Plan after the finale. This show has famously argued "
             "alternative running orders, mostly about those two films; this "
             "list is not one of them."],
            ["Caprica and Blood & Chrome are not here.", "Both are separate "
             "series with their own runs and their own reception, and this is "
             "a list of the 2004 show. The online webisode shorts are out for "
             "the same reason — released beside the seasons rather than "
             "broadcast as part of them."],
            ["Nothing is weighted.", "An episode counts as one, and so does "
             "each night of the miniseries and each film, even though those "
             "run feature length. No per-episode runtimes are published for "
             "the 74 episodes, and weighting only the rows that do have a "
             "figure would quietly count every other row as an hour. 77 even "
             "marks instead."],
            "Titles, numbering and airdates machine-read from Wikipedia's "
            "List of Battlestar Galactica (2004 TV series) episodes and the "
            "four season articles it transcludes; the page's own series "
            "overview counts and the unbroken 1–76 series numbering are "
            "asserted before this builds.",
        ],
        "sections": sections,
    }

    ids = prop.validate(p)
    assert len(ids) == ROWS, len(ids)
    out = prop.write(p)

    print("wrote %s — %d rows (2 miniseries nights + 74 episodes in 73 rows "
          "+ 2 films)" % (out.name, len(ids)))
    for s in sections:
        print("   %-12s %3d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
