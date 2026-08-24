#!/usr/bin/env python3
"""Generate properties/spielberg.json.

    python3 tools/make_spielberg.py

Every feature Steven Spielberg directed, in release order. The inclusion rule
is decided in scratch/spielberg/build_data.py, which builds tools/data/
spielberg.json from the Wikipedia filmography and Wikidata: director credits
only, so Duel counts (a TV movie extended and released theatrically) while
producer-only credits, the Twilight Zone segment, and the partially lost
Firelight do not.

Weights are Wikidata runtimes (P2047) in hours; release dates are P577. The
data file preserves the filmography table's order, which is release order
within each year — this script keeps that order and only groups by era.
"""
import json
import pathlib

SLUG = "spielberg"

ERAS = [
    ("television", "Out of television", 0, 1979,
     "A Universal television contract, a TV movie good enough for cinemas, "
     "and then Jaws — the film the summer blockbuster is named after. 1941 "
     "is the closest thing here to a flop."),
    ("eighties", "The Amblin years", 1980, 1990,
     "Indiana Jones and E.T. at the box office, and — with The Color Purple "
     "and Empire of the Sun — the first films made to prove he could do "
     "something else."),
    ("nineties", "The nineties", 1991, 1998,
     "Jurassic Park and Schindler's List opened six months apart. Both of "
     "his Best Director Oscars come from this stretch."),
    ("aughts", "Two a year", 1999, 2008,
     "Twice in this run — 2002 and 2005 — a summer science-fiction picture "
     "and a December drama in the same year."),
    ("teens", "The history plays", 2009, 2018,
     "Lincoln, Bridge of Spies and The Post in the middle, the animated "
     "Tintin at one end and Ready Player One at the other."),
    ("late", "Late Spielberg", 2019, 9999,
     "His first musical, then the closest thing to a memoir he has made — "
     "and, fifty-five years after Duel, film thirty-five."),
]

NOTE = {
    "Duel": "A television movie, extended and released to cinemas abroad — "
            "that theatrical cut is why it counts",
    "The Sugarland Express": "His theatrical directing debut",
    "A.I. Artificial Intelligence":
        "Also sits on the Stanley Kubrick list — Kubrick developed it for "
        "years before handing it to Spielberg",
    "The Adventures of Tintin": "Animated — the only one",
}


def slug(t):
    keep = "".join(c.lower() if c.isalnum() else "-" for c in t)
    while "--" in keep:
        keep = keep.replace("--", "-")
    return keep.strip("-")


def main():
    data = pathlib.Path(__file__).resolve().parent / "data"
    films = json.loads((data / "spielberg.json").read_text(encoding="utf-8"))

    # the data file is in release order already; trust it, verify the years
    assert all(a["year"] <= b["year"] for a, b in zip(films, films[1:])), \
        "data file is out of year order"
    missing = [f["title"] for f in films if not f["runtime"]]
    assert not missing, "films with no Wikidata runtime: %s" % missing

    sections = []
    for key, title, lo, hi, intro in ERAS:
        got = [f for f in films if lo <= f["year"] <= hi]
        if not got:
            continue
        items = []
        for f in got:
            items.append({
                "id": "sp-%d-%s" % (f["year"], slug(f["title"])),
                "t": f["title"], "n": str(f["year"]),
                "w": round(f["runtime"] / 60.0, 2),
                **({"note": NOTE[f["title"]]} if f["title"] in NOTE else {}),
            })
        sec = {"id": key, "title": title,
               "sub": "%d–%d · %d films · %d hours"
                      % (got[0]["year"], got[-1]["year"], len(got),
                         round(sum(f["runtime"] for f in got) / 60.0)),
               "items": items}
        if intro:
            sec["intro"] = intro
        if key == "television":
            sec["open"] = True
        sections.append(sec)

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert len(ids) == len(films), (len(ids), len(films))
    assert len(films) == 35, "expected 35 directed features, got %d" % len(films)
    for s in sections:
        assert all(a["n"] <= b["n"] for a, b in zip(s["items"], s["items"][1:])), \
            "%s is out of year order" % s["title"]

    hours = sum(f["runtime"] for f in films) / 60.0

    prop = {
        "slug": SLUG,
        "title": "Steven Spielberg",
        "subtitle": "the films he directed, in release order",
        "kind": "films",
        "popularity": 84,
        "year": "1971–",
        "blurb": "Every feature he directed, Duel through Disclosure Day — "
                 "%d films, about %d hours." % (len(films), round(hours)),
        "unit": {"one": "film", "many": "films"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "accent": "#7A4A1E",
        "accentDark": "#E0A265",
        "tiers": False,
        "notes": [
            ["Directed features only.", "If he only produced it — Poltergeist, "
             "The Goonies, Back to the Future — it is not here. Duel counts: "
             "shot for television, then extended and released to cinemas. "
             "Twilight Zone: The Movie does not — he directed one of its four "
             "segments, not the film. Nor does Firelight, the 1964 amateur "
             "feature, which is partially lost and cannot be watched."],
            ["Bar widths are runtimes.", "From Wikidata, in hours — about %d "
             "in all. Every one of the %d films has a real runtime; the "
             "generator refuses to build without them."
             % (round(hours), len(films))],
            "Filmography from Wikipedia; runtimes and release dates from "
            "Wikidata.",
        ],
        "sections": sections,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json" % SLUG)
    print("  %d films, %.0f hours" % (len(films), hours))
    for s in sections:
        print("   %-22s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
