#!/usr/bin/env python3
"""Generate properties/fincher.json.

    python3 tools/make_fincher.py

David Fincher's twelve released features in list order. The Adventures of
Cliff Booth is out until it exists: its own article dates the release
November 25, 2026, so the collector dropped it rather than list a film
nobody can watch yet.

Also out: the producing and executive-producing credits, the music videos,
and the television work — this is the directed-features list.
"""
import json
import pathlib

SLUG = "fincher"

ERAS = [
    ("videos", "Out of music videos", 1992, 1999,
     "An Alien sequel he has disowned in all but name, then the three "
     "films that fixed the reputation: Seven, The Game, Fight Club."),
    ("procedural", "The procedural decade", 2002, 2011,
     "Panic Room through the Dragon Tattoo remake — Zodiac's decades of "
     "unsolved paperwork sit in the middle, and The Social Network won "
     "him his widest acclaim."),
    ("streaming", "Late, mostly Netflix", 2014, 2023,
     "Gone Girl, then two films made for Netflix — his father's Citizen "
     "Kane script, and a killer whose routine goes wrong."),
]


def slug(t):
    keep = "".join(c.lower() if c.isalnum() else "-" for c in t)
    while "--" in keep:
        keep = keep.replace("--", "-")
    return keep.strip("-")


def main():
    data = pathlib.Path(__file__).resolve().parent / "data"
    films = json.loads((data / "fincher.json").read_text(encoding="utf-8"))
    assert len(films) == 12, [f["t"] for f in films]
    films.sort(key=lambda f: (f["year"], f["t"]))
    assert all(f["runtime"] for f in films), \
        [f["t"] for f in films if not f["runtime"]]

    sections = []
    for key, title, lo, hi, intro in ERAS:
        got = [f for f in films if lo <= f["year"] <= hi]
        assert got, title
        sec = {"id": key, "title": title,
               "sub": "%d–%d · %d films · %d hours"
                      % (got[0]["year"], got[-1]["year"], len(got),
                         round(sum(f["runtime"] for f in got) / 60.0)),
               "intro": intro,
               "items": [{"id": "df-%d-%s" % (f["year"], slug(f["t"])),
                          "t": f["t"], "n": str(f["year"]),
                          "w": round(f["runtime"] / 60.0, 2)} for f in got]}
        if key == "videos":
            sec["open"] = True
        sections.append(sec)

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert len(ids) == 12, len(ids)
    for s in sections:
        assert all(a["n"] <= b["n"] for a, b in zip(s["items"], s["items"][1:])), \
            "%s is out of year order" % s["title"]

    hours = sum(x["w"] for s in sections for x in s["items"])

    prop = {
        "slug": SLUG,
        "title": "David Fincher",
        "subtitle": "the directed features",
        "kind": "films",
        "order": 59,
        "year": "1992–2023",
        "blurb": "Twelve features, Alien 3 to The Killer — about %d hours "
                 "of controlled dread." % round(hours),
        "unit": {"one": "film", "many": "films"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "accent": "#33484A",
        "accentDark": "#93B8BA",
        "tiers": False,
        "notes": [
            ["Twelve, not thirteen.", "The Adventures of Cliff Booth is "
             "dated November 25, 2026 by its own article and isn't out "
             "yet; it joins the list when it exists."],
            ["Features only.", "The music videos, the producing credits "
             "and the television work (Mindhunter, House of Cards) are "
             "other lists."],
            ["Bar widths are runtimes.", "From Wikidata, in hours, for "
             "all twelve."],
            "Filmography from Wikipedia's David Fincher filmography; "
            "runtimes from Wikidata.",
        ],
        "sections": sections,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")
    print("wrote %s.json — %d rows, %.1f hours" % (SLUG, len(ids), hours))
    for s in sections:
        print("   %-24s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
