#!/usr/bin/env python3
"""Generate properties/tarantino.json.

    python3 tools/make_tarantino.py

Quentin Tarantino's ten directed features in release order. The Kill Bill
situation is stated the way the filmography's own table states it — the two
volumes premiered as one film, The Whole Bloody Affair, in 2004 — and Death
Proof is its own row, marked as the half of Grindhouse it started as.

Left out, with reasons: The Man from Hollywood (a segment of Four Rooms),
his guest scene in Sin City, the unfinished My Best Friend's Birthday and
Love Birds In Bondage, and the television episodes (ER, CSI).
"""
import json
import pathlib

SLUG = "tarantino"

ERAS = [
    ("indie", "The independent years", 1992, 1997,
     "Reservoir Dogs on a borrowed-money budget, Pulp Fiction rewiring the "
     "decade, and Jackie Brown — the Elmore Leonard adaptation, and the one "
     "he never topped for patience."),
    ("genre", "Genre exercises", 2003, 2007,
     "The Kill Bill diptych — premiered as one film, released as two — and "
     "Death Proof, his half of the Grindhouse double feature."),
    ("history", "Rewriting history", 2009, 2019,
     "Four pictures that take history personally: the war film, the "
     "western twice over, and 1969 Los Angeles given a different ending."),
]

NOTE = {
    "Kill Bill: Volume 1":
        "Premiered with Volume 2 as one film, Kill Bill: The Whole Bloody "
        "Affair, in 2004",
    "Kill Bill: Volume 2":
        "The back half of The Whole Bloody Affair, released on its own",
    "Death Proof":
        "His segment of the Grindhouse double feature, weighed here at its "
        "standalone cut",
    "The Hateful Eight":
        "Weighed at the 187-minute roadshow cut",
}


def slug(t):
    keep = "".join(c.lower() if c.isalnum() else "-" for c in t)
    while "--" in keep:
        keep = keep.replace("--", "-")
    return keep.strip("-")


def main():
    data = pathlib.Path(__file__).resolve().parent / "data"
    films = json.loads((data / "tarantino.json").read_text(encoding="utf-8"))
    assert len(films) == 10, len(films)
    films.sort(key=lambda f: (f["year"], f["t"]))
    assert all(f["runtime"] for f in films), \
        [f["t"] for f in films if not f["runtime"]]

    sections = []
    for key, title, lo, hi, intro in ERAS:
        got = [f for f in films if lo <= f["year"] <= hi]
        assert got, title
        items = []
        for f in got:
            it = {"id": "qt-%d-%s" % (f["year"], slug(f["t"])),
                  "t": f["t"], "n": str(f["year"]),
                  "w": round(f["runtime"] / 60.0, 2)}
            if f["t"] in NOTE:
                it["note"] = NOTE[f["t"]]
            items.append(it)
        sec = {"id": key, "title": title,
               "sub": "%d–%d · %d films · %d hours"
                      % (got[0]["year"], got[-1]["year"], len(got),
                         round(sum(f["runtime"] for f in got) / 60.0)),
               "intro": intro, "items": items}
        if key == "indie":
            sec["open"] = True
        sections.append(sec)

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert len(ids) == 10, len(ids)
    for s in sections:
        assert all(a["n"] <= b["n"] for a, b in zip(s["items"], s["items"][1:])), \
            "%s is out of year order" % s["title"]

    hours = sum(x["w"] for s in sections for x in s["items"])

    prop = {
        "slug": SLUG,
        "title": "Quentin Tarantino",
        "subtitle": "the ten features, in release order",
        "kind": "films",
        "order": 57,
        "year": "1992–2019",
        "blurb": "All ten theatrical features — or nine, if you count Kill "
                 "Bill the way he does. About %d hours." % round(hours),
        "unit": {"one": "film", "many": "films"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "accent": "#2B2612",
        "accentDark": "#F2C93C",
        "tiers": False,
        "notes": [
            ["Ten films, or nine.", "Tarantino counts Kill Bill as a single "
             "film — it premiered that way, as The Whole Bloody Affair, at "
             "Cannes in 2004 — so ten theatrical releases make nine films "
             "by his arithmetic. Both volumes are rows here."],
            ["What isn't here.", "The Man from Hollywood (his quarter of "
             "Four Rooms), the scene he guest-directed in Sin City, the "
             "unfinished My Best Friend's Birthday, and the ER and CSI "
             "episodes. Segments and television are not features."],
            ["Bar widths are runtimes.", "From Wikidata, in hours. Where a "
             "film has more than one cut — Death Proof standalone, The "
             "Hateful Eight roadshow — the longer one is the weight."],
            "Filmography from Wikipedia's Quentin Tarantino filmography; "
            "runtimes from Wikidata.",
        ],
        "sections": sections,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")
    print("wrote %s.json — %d rows, %.1f hours" % (SLUG, len(ids), hours))
    for s in sections:
        print("   %-22s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
