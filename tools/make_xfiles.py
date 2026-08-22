#!/usr/bin/env python3
"""Generate properties/x-files.json — every episode, plus the films in place.

    python3 tools/make_xfiles.py

One row per episode, 217 rows covering all 218 episodes — the season nine
finale aired as a single double-length broadcast and is one row spanning
19–20, exactly as the season article files it. The films sit between the right
seasons as one-row sections: Fight the Future between seasons 5 and 6, I Want
to Believe after season 9.

Episode titles and airdates are machine-read from the eleven "The X-Files
season N" articles' {{Episode list}} rows by scratch/x-files/episodes_full.py,
which asserts every season's numbering is fully covered; the committed result
is tools/data/xfiles_episodes.json.

Nothing is weighted: an episode and a film count one each, which keeps 219
rows legible and the films visible instead of two slightly wider marks.

This replaced a season-per-row version that shipped briefly; the film ids
(xf-film-1998, xf-film-2008) are preserved from it, the season ids are not.
"""
import json
import pathlib

SLUG = "x-files"

SEASON_YEARS = {1: "1993–94", 2: "1994–95", 3: "1995–96", 4: "1996–97",
                5: "1997–98", 6: "1998–99", 7: "1999–2000", 8: "2000–01",
                9: "2001–02", 10: "2016", 11: "2018"}


def main():
    data = json.loads((pathlib.Path(__file__).resolve().parent / "data"
                       / "xfiles_episodes.json").read_text(encoding="utf-8"))

    def season_section(n, intro=""):
        eps = data[str(n)]
        items = []
        for x in eps:
            span = str(x["e"]) if x["e"] == x["e2"] else "%d–%d" % (x["e"], x["e2"])
            row = {"id": "xf-s%de%d" % (n, x["e"]), "t": x["t"], "n": span}
            if x["e"] != x["e2"]:
                row["note"] = "Aired as one double-length episode"
            items.append(row)
        count = sum(x["e2"] - x["e"] + 1 for x in eps)
        sec = {"id": "s%d" % n, "title": "Season %d" % n,
               "sub": "%s · %d episodes" % (SEASON_YEARS[n], count),
               "items": items}
        if intro:
            sec["intro"] = intro
        return sec

    sections = [season_section(1)]
    sections[0]["open"] = True
    sections += [season_section(n) for n in range(2, 6)]
    sections.append({
        "id": "film1", "title": "Fight the Future",
        "sub": "1998 · the film, between seasons 5 and 6",
        "items": [{"id": "xf-film-1998", "t": "The X-Files: Fight the Future",
                   "n": "1998"}],
    })
    sections += [season_section(n) for n in range(6, 10)]
    sections.append({
        "id": "film2", "title": "I Want to Believe",
        "sub": "2008 · the second film, six years after the finale",
        "items": [{"id": "xf-film-2008", "t": "The X-Files: I Want to Believe",
                   "n": "2008"}],
    })
    sections += [season_section(10,
        "Fourteen years on. Six episodes, then ten more two years later.")]
    sections.append(season_section(11))

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    eps = sum(1 for i in ids if not i.startswith("xf-film"))
    assert eps == 217, eps
    assert len(ids) == 219, len(ids)
    covered = sum(x["e2"] - x["e"] + 1 for v in data.values() for x in v)
    assert covered == 218, covered

    prop = {
        "slug": SLUG,
        "title": "The X-Files",
        "subtitle": "every episode, with the films where they belong",
        "kind": "tv & films",
        "order": 26,
        "year": "1993–2018",
        "blurb": "All 218 episodes and both films in broadcast order — eleven "
                 "seasons, two eras, one basement office.",
        "unit": {"one": "entry", "many": "entries"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": "#275E6B",
        "accentDark": "#6FC0D0",
        "tiers": False,
        "notes": [
            ["The films sit where you watch them.", "Fight the Future was "
             "written as the bridge between seasons 5 and 6 and sits there; "
             "I Want to Believe came six years after the finale and eight "
             "before the revival, so it closes the original era."],
            ["One row aired double.", "The season nine finale was a single "
             "double-length broadcast, so it is one row spanning 19–20 — "
             "217 rows covering 218 episodes."],
            ["Mythology and monster-of-the-week are not filtered.", "The "
             "distinction is real but every abridged path through this show "
             "is someone's argument; the list is the whole thing, in order."],
            ["Nothing is weighted.", "An episode and a film count one each — "
             "219 marks read better than two slightly wider ones."],
            "Episode titles and airdates machine-read from the eleven "
            "Wikipedia season articles; every season's numbering is asserted "
            "complete before this builds.",
        ],
        "sections": sections,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json — %d rows (%d episode rows + 2 films)"
          % (SLUG, len(ids), eps))
    for s in sections:
        print("   %-18s %3d  %s" % (s["title"], len(s["items"]), s.get("sub", "")[:36]))


if __name__ == "__main__":
    main()
