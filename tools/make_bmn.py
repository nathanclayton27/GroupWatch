#!/usr/bin/env python3
"""Generate properties/bad-movie-night.json — the so-bad-it's-good canon.

    python tools/make_bmn.py

House-curated: the famous disasters people actually gather to watch, from Ed
Wood to Cats. Facts on every row — exact title, year, runtime, director —
are machine-read from each film's own Wikipedia article infobox by
scratch/agent-canons/collect_bmn.py. Unweighted grab bag, Random button
intended; runtimes ride on the notes.
"""
import json
import pathlib
import unicodedata

SLUG = "bad-movie-night"
ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = pathlib.Path(__file__).resolve().parent / "data" / ("%s.json" % SLUG)
OUT = ROOT / "properties" / ("%s.json" % SLUG)

ERAS = [
    ("drivein", "The drive-in era", None, 1966,
     "Ed Wood, Coleman Francis, and the fever dream of Manos — the founding "
     "texts, all mercifully short."),
    ("vhs", "The video-store era", 1967, 1991,
     "Too strange to die: rescued by late-night cable, rental shelves and "
     "riffing."),
    ("multiplex", "Multiplex disasters", 1992, 2007,
     "Real budgets, real stars, unreal results — The Room arrives in 2003."),
    ("meme", "The internet era", 2008, None,
     "Birdemic to Cats: the internet finds them the moment they land."),
]


# rows that need one honest line beyond director and runtime
EXTRA_NOTES = {
    "Cannibal Holocaust":
        "Group request — fair warning: infamous rather than funny, with "
        "real animal deaths and a court case",
}


def slug(t):
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    keep = "".join(c.lower() if c.isalnum() else "-" for c in t)
    while "--" in keep:
        keep = keep.replace("--", "-")
    return keep.strip("-")


def main():
    d = json.loads(DATA.read_text(encoding="utf-8"))
    films = d["films"]
    assert all(f["runtime"] and f["year"] for f in films)

    sections = []
    for key, title, lo, hi, intro in ERAS:
        got = [f for f in films
               if (lo is None or f["year"] >= lo)
               and (hi is None or f["year"] <= hi)]
        assert got, key
        got.sort(key=lambda f: (f["year"], f["t"]))
        items = []
        for f in got:
            bits = []
            if f["director"]:
                bits.append(f["director"].split(",")[0])
            bits.append("%d min" % f["runtime"])
            if f.get("tv"):
                bits.append("a TV film")
            if f["t"] in EXTRA_NOTES:
                bits.append(EXTRA_NOTES[f["t"]])
            items.append({"id": "bmn-%d-%s" % (f["year"], slug(f["t"])),
                          "t": f["t"], "n": str(f["year"]),
                          "note": " · ".join(bits)})
        sec = {"id": key, "title": title,
               "sub": "%d–%d · %d films" % (got[0]["year"], got[-1]["year"],
                                            len(got)),
               "intro": intro, "items": items}
        if key == "drivein":
            sec["open"] = True
        sections.append(sec)

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), \
        "duplicate ids: %s" % sorted({i for i in ids if ids.count(i) > 1})[:6]
    assert len(ids) == len(films)

    prop = {
        "slug": SLUG,
        "title": "Bad Movie Night",
        "subtitle": "so bad they're appointment viewing",
        "kind": "films",
        "order": 68,
        "year": "%d–%d" % (min(f["year"] for f in films),
                           max(f["year"] for f in films)),
        "blurb": "%d famously terrible films worth watching with people you "
                 "like — Plan 9 to Cats, best served loud. Any order."
                 % len(films),
        "unit": {"one": "film", "many": "films"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "accent": "#8E2A6F",
        "accentDark": "#E06AC0",
        "tiers": False,
        "random": True,
        "notes": [
            ["Every entry was added here — shout if it doesn't belong.",
             "There is no official canon of bad movies, so this whole list "
             "is the house's own picks; veto freely and nominate "
             "replacements. What is verified is the facts: every row's "
             "title, year, runtime and director are read from the film's "
             "own Wikipedia article, not typed from memory."],
            ["No order, no weights.",
             "A grab bag for group nights — hit Random. Runtimes sit on the "
             "notes so you can size an evening."],
            "Facts from each film's Wikipedia article infobox.",
        ],
        "sections": sections,
    }

    with OUT.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")
    print("wrote %s.json — %d films" % (SLUG, len(films)))
    for s in sections:
        print("   %-22s %2d  %s" % (s["title"], len(s["items"]), s["sub"][:44]))


if __name__ == "__main__":
    main()
