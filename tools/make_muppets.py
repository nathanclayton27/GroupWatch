#!/usr/bin/env python3
"""Generate properties/muppets.json — the Muppet films, plus the shows.

    python tools/make_muppets.py

Films: the eight theatrical features from Wikipedia's List of The Muppets
productions, in release order, weighted by the runtimes that same table
carries. Television: one row per series from the article's Series and
Animated series tables — n is the years it ran, the note carries network and
episode count (read from each series' own article infobox), and nothing is
weighted, because a series-level row is a commitment, not an hour.

Data: tools/data/muppets.json, built by scratch/agent-canons/collect_muppets.py.
"""
import json
import pathlib

SLUG = "muppets"
ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = pathlib.Path(__file__).resolve().parent / "data" / "muppets.json"
OUT = ROOT / "properties" / ("%s.json" % SLUG)


def slug(t):
    import unicodedata
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    keep = "".join(c.lower() if (c.isalnum() and c.isascii()) else "-"
                   for c in t)
    while "--" in keep:
        keep = keep.replace("--", "-")
    return keep.strip("-")


def series_item(s, anim):
    yrs = ("%d–%d" % (s["start"], s["end"])) if s["end"] != s["start"] \
        else str(s["start"])
    bits = []
    if s["network"]:
        bits.append(s["network"])
    if s.get("episodes"):
        bits.append("%s episodes" % s["episodes"])
    if anim:
        bits.append("animated")
    return {
        "id": "mup-tv-%d-%s" % (s["start"], slug(s["t"])),
        "t": s["t"], "n": yrs,
        **({"note": " · ".join(bits)} if bits else {}),
    }


def main():
    d = json.loads(DATA.read_text(encoding="utf-8"))
    films = d["films"]
    assert len(films) == 8, len(films)
    assert all(f["runtime"] for f in films)
    assert [f["year"] for f in films] == sorted(f["year"] for f in films)

    film_items = [{
        "id": "mup-%d-%s" % (f["year"], slug(f["t"])),
        "t": f["t"], "n": str(f["year"]),
        "w": round(f["runtime"] / 60.0, 2),
    } for f in films]
    fh = sum(x["w"] for x in film_items)

    # one combined TV list, in premiere order, animation flagged on the row
    tv = [(s, False) for s in d["series"]] + [(s, True) for s in d["animated"]]
    tv.sort(key=lambda p: (p[0]["start"], p[0]["t"]))
    tv_items = [series_item(s, anim) for s, anim in tv]

    sections = [
        {"id": "films", "title": "The theatrical films",
         "sub": "1979–2014 · 8 films · %d hours" % round(fh),
         "intro": "Every Muppet feature that played in theaters, in release "
                  "order — from The Muppet Movie to the 2010s revival.",
         "open": True,
         "items": film_items},
        {"id": "television", "title": "The shows",
         "sub": "1955–2023 · %d series, one row each" % len(tv_items),
         "intro": "One tick per series, from Sam and Friends to The Muppets "
                  "Mayhem. A row here means the show, however much of it you "
                  "choose to watch — episode counts ride on the notes. These "
                  "weigh nothing on the bar.",
         "items": tv_items},
    ]

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), \
        "duplicate ids: %s" % sorted({i for i in ids if ids.count(i) > 1})[:6]
    assert len(ids) == len(films) + len(tv_items)

    prop = {
        "slug": SLUG,
        "title": "The Muppets",
        "subtitle": "the films in release order, plus the shows",
        "kind": "films & series",
        "order": 64,
        "year": "1955–2023",
        "blurb": "All 8 theatrical Muppet films — about %d hours — plus one "
                 "row per television series, The Muppet Show included."
                 % round(fh),
        "unit": {"one": "entry", "many": "entries"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "accent": "#3E7A33",
        "accentDark": "#7FC95E",
        "tiers": False,
        "notes": [
            ["Films are hours, shows are rows.",
             "The eight features carry runtime weights straight from "
             "Wikipedia's own table. A series row is one tick for the whole "
             "series and weighs nothing, so the finish line stays about the "
             "films."],
            ["Made-for-TV movies are not here.",
             "It's a Very Merry Muppet Christmas Movie, The Muppets' Wizard "
             "of Oz and the other television films are their own shelf; this "
             "list keeps to the theatrical eight and the series."],
            "Films and series from Wikipedia's List of The Muppets "
            "productions; episode counts from each series' own article.",
        ],
        "sections": sections,
    }

    with OUT.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")
    print("wrote %s.json — 8 films (%d h) + %d series"
          % (SLUG, round(fh), len(tv_items)))
    for s in sections:
        print("   %-22s %2d  %s" % (s["title"], len(s["items"]), s["sub"][:48]))


if __name__ == "__main__":
    main()
