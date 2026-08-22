#!/usr/bin/env python3
"""Generate properties/breaking-bad.json — the whole universe, one shared page.

    python3 tools/make_bb.py

One row per episode, unweighted: Breaking Bad's 62 episodes across five
seasons, then El Camino as a one-row section at its 2019 release point, then
Better Call Saul's 63 episodes across six seasons. Release order throughout —
Breaking Bad completed sixteen months before Better Call Saul began, and El
Camino arrived between Saul's fourth and fifth seasons, which is where it
sits. The airdates in the data file are asserted to bracket it.

Episode titles and airdates are machine-read from the eleven per-season
Wikipedia articles by scratch/bb/fetch.py, which asserts every season's
numbering is fully covered; the committed result is tools/data/bb.json.
"""
import json
import pathlib

SLUG = "breaking-bad"
EL_CAMINO = "2019-10-11"

EXPECT = {"bb": {1: 7, 2: 13, 3: 13, 4: 13, 5: 16},
          "bcs": {1: 10, 2: 10, 3: 10, 4: 10, 5: 10, 6: 13}}
SHOW_TITLE = {"bb": "Breaking Bad", "bcs": "Better Call Saul"}


def years(eps):
    y0, y1 = int(eps[0]["air"][:4]), int(eps[-1]["air"][:4])
    if y0 == y1:
        return "%d" % y0
    if y0 // 100 == y1 // 100:
        return "%d–%02d" % (y0, y1 % 100)
    return "%d–%d" % (y0, y1)


def main():
    data = json.loads((pathlib.Path(__file__).resolve().parent / "data"
                       / "bb.json").read_text(encoding="utf-8"))

    def season_section(show, n, intro=""):
        eps = data[show][str(n)]
        assert [x["e"] for x in eps] == list(range(1, EXPECT[show][n] + 1)), \
            "%s season %d incomplete" % (show, n)
        sec = {"id": "%s-s%d" % (show, n),
               "title": "%s · Season %d" % (SHOW_TITLE[show], n),
               "sub": "%s · %d episodes" % (years(eps), len(eps)),
               "items": [{"id": "%s-s%de%d" % (show, n, x["e"]),
                          "t": x["t"], "n": str(x["e"])} for x in eps]}
        if intro:
            sec["intro"] = intro
        return sec

    assert data["bcs"]["4"][-1]["air"] < EL_CAMINO < data["bcs"]["5"][0]["air"], \
        "El Camino no longer falls between Better Call Saul seasons 4 and 5"
    assert data["bb"]["5"][-1]["air"] < data["bcs"]["1"][0]["air"], \
        "Breaking Bad did not finish before Better Call Saul began"

    sections = [season_section("bb", n) for n in range(1, 6)]
    sections[0]["open"] = True
    sections += [season_section("bcs", 1,
        "The spin-off — made after Breaking Bad ended, set before it began.")]
    sections += [season_section("bcs", n) for n in range(2, 5)]
    sections.append({
        "id": "elcamino", "title": "El Camino",
        "sub": "2019 · the film, between Better Call Saul seasons 4 and 5",
        "items": [{"id": "bb-film-2019", "t": "El Camino: A Breaking Bad Movie",
                   "n": "2019"}],
    })
    sections += [season_section("bcs", n) for n in range(5, 7)]

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert sum(1 for i in ids if i.startswith("bb-s")) == 62
    assert sum(1 for i in ids if i.startswith("bcs-s")) == 63
    assert len(ids) == 126, len(ids)

    prop = {
        "slug": SLUG,
        "title": "Breaking Bad",
        "subtitle": "the whole universe in release order — with El Camino "
                    "and Better Call Saul",
        "kind": "tv & film",
        "order": 43,
        "year": "2008–2022",
        "blurb": "All 62 episodes, El Camino, and Better Call Saul's 63 — "
                 "one universe, 126 entries, in the order it arrived.",
        "unit": {"one": "entry", "many": "entries"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": "#2E5F2E",
        "accentDark": "#7FC97F",
        "tiers": False,
        "notes": [
            ["Release order, on purpose.", "The recommended-orders debate is "
             "real — Better Call Saul is set earlier, and starting there has "
             "its advocates. This page is the order it all arrived, because "
             "each show builds its reveals on what the audience of the other "
             "had already seen."],
            ["El Camino sits at its release date.", "It arrived between "
             "Better Call Saul's fourth and fifth seasons — six years after "
             "Breaking Bad ended — and that is where it sits, not stitched "
             "onto the finale."],
            ["Nothing is weighted.", "An episode and a film count one each — "
             "126 even marks read better than one slightly wider one."],
            "Episode titles and airdates machine-read from the eleven "
            "Wikipedia season articles across both shows; every season's "
            "numbering is asserted complete before this builds.",
        ],
        "sections": sections,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json — %d rows (62 + El Camino + 63)" % (SLUG, len(ids)))
    for s in sections:
        print("   %-28s %3d  %s" % (s["title"], len(s["items"]),
                                    s.get("sub", "")[:44]))


if __name__ == "__main__":
    main()
