#!/usr/bin/env python3
"""Generate properties/berserk-manga.json.

    python tools/make_berserk-manga.py

The manga by volume — all 43 collected so far, ongoing — sectioned by the
five story arcs. Volume numbers, release years and the arc boundaries come
from tools/data/berserk-manga.json, built by
scratch/agent-anime/harvest_berserk.py from Wikipedia's "List of Berserk
chapters": each arc's start is the volume whose chapter list carries the
article's own "beginning of the X Arc" marker, cross-checked against the
volume ranges in the article lead. Arcs hand over mid-volume, so a
boundary volume is filed under the arc that begins in it.

Unweighted: a volume is a volume.
"""
import json
import pathlib

SLUG = "berserk-manga"

DATA = pathlib.Path(__file__).resolve().parent / "data" / (SLUG + ".json")
OUT = pathlib.Path(__file__).resolve().parent.parent / "properties" / (SLUG + ".json")

WIKI = "https://en.wikipedia.org/wiki/"

ARCS = [
    ("Black Swordsman", "bs", "The Black Swordsman",
     "The opening arc: Guts alone on the road, and the shape of the world "
     "he moves through."),
    ("Golden Age", "golden", "The Golden Age",
     "The long look back — the Band of the Hawk, Griffith, and how Guts "
     "came to be what the first volumes show."),
    ("Conviction", "conviction", "Conviction",
     "The Black Swordsman again, now with somewhere to go — the Tower of "
     "Conviction and what gathers there."),
    ("Falcon of the Millennium Empire", "falcon",
     "Falcon of the Millennium Empire",
     "The longest arc: a changed world, a war behind it, and a company "
     "slowly forming around Guts."),
    ("Fantasia", "fantasia", "Fantasia",
     "The arc Miura left unfinished — Elf Island and after. Continued "
     "since 2022 by Studio Gaga, supervised by Kouji Mori."),
]


def main():
    d = json.loads(DATA.read_text(encoding="utf-8"))
    vols = {v["n"]: v for v in d["vols"]}
    begin = d["arc_begin"]
    assert begin == d["lead_begin"], (begin, d["lead_begin"])
    total = len(vols)
    assert sorted(vols) == list(range(1, total + 1))

    starts = [begin[a[0]] for a in ARCS]
    assert starts == sorted(starts) and starts[0] == 1
    ends = [s - 1 for s in starts[1:]] + [total]

    sections = []
    for (key, sid, title, intro), lo, hi in zip(ARCS, starts, ends):
        items = []
        for n in range(lo, hi + 1):
            v = vols[n]
            items.append({"id": "bsk-v%d" % n, "t": "Volume", "n": str(n),
                          "note": "%d · Dark Horse %d" % (v["jp"], v["en"])})
        sections.append({
            "id": sid,
            "title": title,
            "sub": "volumes %d–%d · %d–%d"
                   % (lo, hi, vols[lo]["jp"], vols[hi]["jp"]),
            "intro": intro,
            "links": [{"label": "The chapter list",
                       "url": WIKI + "List_of_Berserk_chapters"}],
            "items": items,
        })
    sections[0]["open"] = True

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert len(ids) == total, (len(ids), total)

    prop = {
        "slug": SLUG,
        "title": "Berserk",
        "subtitle": "Kentaro Miura · the manga, by volume",
        "kind": "manga",
        "order": 87,
        "year": "1989–",
        "blurb": "All %d collected volumes across the five arcs, from the "
                 "Black Swordsman to Fantasia — ongoing." % total,
        "unit": {"one": "volume", "many": "volumes"},
        "verb": {"base": "read", "past": "read", "ing": "reading"},
        "itemOrder": "number-first",
        "accent": "#2A1215",
        "accentDark": "#E03A3A",
        "tiers": False,
        "notes": [
            ["Miura and after.", "Kentaro Miura died in 2021; volume 41 "
             "collects the final chapters he made. Since 2022 the series "
             "has continued drawn by Studio Gaga — his assistants and "
             "apprentices — supervised by his friend Kouji Mori, and those "
             "volumes are listed like any other."],
            ["Arcs hand over mid-volume.", "The Golden Age begins partway "
             "through volume 3, Falcon of the Millennium Empire ends "
             "partway through 35 — each boundary volume is filed under the "
             "arc that begins in it, matching the markers on Wikipedia's "
             "chapter list."],
            ["Ongoing.", "Chapters 383–386 are serialized but not yet "
             "collected, so no volume lists them yet; rerun the generator "
             "when volume 44 lands. One chapter (83, \"God of the "
             "Abyss (2)\") was omitted from volume 13 and belongs to no "
             "volume at all."],
            ["Editions.", "Rows are the Japanese tankōbon numbering, which "
             "Dark Horse's English volumes match one for one; each row "
             "notes both years. The three-in-one deluxe hardcovers are the "
             "same content repackaged and are not rows."],
            "Volumes, years and arc boundaries machine-read from "
            "Wikipedia's List of Berserk chapters; the arc markers are "
            "checked against the ranges in the article lead before this "
            "builds.",
        ],
        "sections": sections,
    }

    with OUT.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json — %d volumes" % (SLUG, total))
    for s in sections:
        print("   %-34s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
