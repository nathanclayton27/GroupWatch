#!/usr/bin/env python3
"""Generate properties/x-files.json.

    python3 tools/make_xfiles.py

The X-Files season by season plus the two films, in release order: seasons
1-9 (1993-2002), Fight the Future (1998) between seasons 5 and 6, I Want to
Believe (2008) after season 9, and the revival seasons 10 (2016) and 11
(2018). One row per season, one per film - 13 rows.

Sources, all in tools/data/xfiles.json:
  - Per-season episode counts and air dates from the series-overview table
    ({{Series overview}}) in the wikitext of Wikipedia's "List of The X-Files
    episodes", fetched via the API (scratch/x-files/fetch.py).
  - Film runtimes from Wikidata P2047 (Q1129381, Q421875), fetched via
    wbgetentities (scratch/x-files/fetch_films.py). Film release dates come
    from the same series-overview table, because Wikidata's P577 for the 1998
    film is year-precision only.

Judgment calls:
  - Season weights are episode count x 45 minutes, in hours - a declared
    convention, not a measured runtime; the footer says so. Films weigh their
    real runtimes.
  - I Want to Believe closes the middle era rather than opening the revival:
    release order puts it six years after the finale and eight before season
    10, and it belongs to the film-and-later-seasons stretch it follows.
  - The 1998 film is titled "The X-Files: Fight the Future" here, as the
    series-overview table itself labels it, because a row reading only
    "The X-Files" inside The X-Files list would say nothing.
"""
import json
import pathlib

SLUG = "x-files"
EP_MIN = 45  # declared minutes per episode; seasons weigh eps * this, in hours

EPISODE_LIST = "https://en.wikipedia.org/wiki/List_of_The_X-Files_episodes"


def years(start, end):
    """'1993-09-10','1994-05-13' -> '1993–94'; same year collapses; keeps
    '1999–2000' whole where the century turns."""
    a, b = start[:4], end[:4]
    if a == b:
        return a
    return "%s–%s" % (a, b if a[:2] != b[:2] else b[2:])


def season_row(s):
    return {
        "id": "xf-s%d" % s["n"],
        "t": "Season %d" % s["n"],
        "n": years(s["start"], s["end"]),
        "note": "%d episodes" % s["episodes"],
        "w": round(s["episodes"] * EP_MIN / 60.0, 2),
    }


def film_row(f, note):
    return {
        "id": "xf-film-%s" % f["key"],
        "t": f["title"],
        "n": f["released"][:4],
        "note": note,
        "w": round(f["runtime_min"] / 60.0, 2),
    }


def main():
    data = pathlib.Path(__file__).resolve().parent / "data"
    src = json.loads((data / "xfiles.json").read_text(encoding="utf-8"))
    seasons = {s["n"]: s for s in src["seasons"]}
    films = {f["key"]: f for f in src["films"]}

    f98, f08 = films["1998"], films["2008"]
    assert f98["after_season"] == 5 and f08["after_season"] == 9

    sections = [
        {
            "id": "original", "title": "The original run",
            "sub": "1993–98 · seasons 1–5 · %d episodes"
                   % sum(seasons[n]["episodes"] for n in range(1, 6)),
            "links": [{"label": "Episode list", "url": EPISODE_LIST}],
            "open": True,
            "items": [season_row(seasons[n]) for n in range(1, 6)],
        },
        {
            "id": "films-and-later", "title": "The films and seasons 6–9",
            "sub": "1998–2008 · both films around %d more episodes"
                   % sum(seasons[n]["episodes"] for n in range(6, 10)),
            "links": [
                {"label": "Fight the Future",
                 "url": "https://en.wikipedia.org/wiki/The_X-Files_(film)"},
                {"label": "I Want to Believe",
                 "url": "https://en.wikipedia.org/wiki/"
                        "The_X-Files:_I_Want_to_Believe"},
            ],
            "items": (
                [film_row(f98, "The first film · 121 minutes · "
                               "released between seasons 5 and 6")]
                + [season_row(seasons[n]) for n in range(6, 10)]
                + [film_row(f08, "The second film · 104 minutes · "
                                 "released six years after the series ended")]
            ),
        },
        {
            "id": "revival", "title": "The revival",
            "sub": "2016–18 · seasons 10 and 11 · %d episodes"
                   % sum(seasons[n]["episodes"] for n in (10, 11)),
            "links": [{"label": "Episode list", "url": EPISODE_LIST}],
            "items": [season_row(seasons[n]) for n in (10, 11)],
        },
    ]

    # -- asserts ------------------------------------------------------------
    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert set(ids) == ({"xf-s%d" % n for n in range(1, 12)}
                        | {"xf-film-1998", "xf-film-2008"}), sorted(ids)
    assert len(ids) == 13, len(ids)

    eps = sum(s["episodes"] for s in src["seasons"])
    assert eps == 218, eps
    for s in src["seasons"]:
        row = next(x for x in (i for sec in sections for i in sec["items"])
                   if x["id"] == "xf-s%d" % s["n"])
        assert row["note"] == "%d episodes" % s["episodes"], row

    # release order across the whole list: sort key is season start / film
    # release date, and it must already be in order
    when = {("xf-s%d" % s["n"]): s["start"] for s in src["seasons"]}
    when.update({("xf-film-%s" % f["key"]): f["released"]
                 for f in src["films"]})
    dates = [when[i] for i in ids]
    assert dates == sorted(dates), "rows out of release order"

    hours = sum(x["w"] for s in sections for x in s["items"])
    assert all(x["w"] > 0 for s in sections for x in s["items"])
    assert abs(hours - (eps * EP_MIN / 60.0
                        + (f98["runtime_min"] + f08["runtime_min"]) / 60.0)) < 0.05

    # -- property -----------------------------------------------------------
    prop = {
        "slug": SLUG,
        "title": "The X-Files",
        "subtitle": "eleven seasons and both films, in release order",
        "kind": "tv & films",
        "order": 26,
        "year": "1993–2018",
        "blurb": "%d episodes across 11 seasons, with the two films where "
                 "they landed — about %d hours." % (eps, round(hours)),
        "unit": {"one": "entry", "many": "entries"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": "#275E6B",
        "accentDark": "#6FC0D0",
        "tiers": False,
        "notes": [
            ["Mythology and monster-of-the-week both live here.",
             "The show famously splits into an ongoing mythology and "
             "standalone episodes, but a season row holds both — this "
             "list tracks whole seasons and does not filter the distinction."],
            ["Season bars are episode count × 45 minutes.",
             "A declared convention, not a measured runtime — network "
             "hours varied. The films weigh their real runtimes, from "
             "Wikidata."],
            "Episode counts and air dates from the series-overview table on "
            "Wikipedia's List of The X-Files episodes; film runtimes from "
            "Wikidata.",
        ],
        "sections": sections,
    }

    out = (pathlib.Path(__file__).resolve().parent.parent
           / "properties" / ("%s.json" % SLUG))
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json" % SLUG)
    print("  %d rows, %d episodes, %.2f hours" % (len(ids), eps, hours))
    for s in sections:
        print("   %-28s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
