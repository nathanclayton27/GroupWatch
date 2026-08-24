#!/usr/bin/env python3
"""Generate properties/carpenter.json.

    python3 tools/make_carpenter.py

John Carpenter's 21 directed features in release order — 18 theatrical, and
the three television films (Someone's Watching Me!, Elvis, Body Bags) as
optional rows, marked the way the filmography's own table marks them.

Everything he only wrote, produced or scored for other people stays out, as
do the shorts and the television episodes.
"""
import json
import pathlib

SLUG = "carpenter"

ERAS = [
    ("indie", "The independent years", 1974, 1981,
     "Dark Star grown out of a student film, a siege picture, and "
     "Halloween — the cheap one that built the slasher decade. Two "
     "television films from the same stretch ride along as optional "
     "rows."),
    ("studio", "The studio years", 1982, 1988,
     "The Thing through They Live: six studio genre pictures, the first "
     "of them despised on release and canonised since."),
    ("late", "The long retreat", 1992, 2010,
     "An invisible-man picture, a Lovecraft riff, a remake, two sequels "
     "of a kind, and a gap of nine years before The Ward — his last "
     "feature to date."),
]


def slug(t):
    keep = "".join(c.lower() if c.isalnum() else "-" for c in t)
    while "--" in keep:
        keep = keep.replace("--", "-")
    return keep.strip("-")


def main():
    data = pathlib.Path(__file__).resolve().parent / "data"
    films = json.loads((data / "carpenter.json").read_text(encoding="utf-8"))
    assert len(films) == 21, len(films)
    assert sum(f["tv"] for f in films) == 3, [f["t"] for f in films if f["tv"]]
    films.sort(key=lambda f: (f["year"], f["t"]))
    assert all(f["runtime"] for f in films), \
        [f["t"] for f in films if not f["runtime"]]

    sections = []
    for key, title, lo, hi, intro in ERAS:
        got = [f for f in films if lo <= f["year"] <= hi]
        assert got, title
        items = []
        for f in got:
            it = {"id": "jc-%d-%s" % (f["year"], slug(f["t"])),
                  "t": f["t"], "n": str(f["year"]),
                  "w": round(f["runtime"] / 60.0, 2)}
            if f["tv"]:
                it["opt"] = 1
                it["note"] = "Television film"
            items.append(it)
        nf = sum(1 for f in got if not f["tv"])
        ntv = len(got) - nf
        sub = "%d–%d · %d features" % (got[0]["year"], got[-1]["year"], nf)
        if ntv:
            sub += " + %d TV film%s" % (ntv, "s" if ntv > 1 else "")
        sub += " · %d hours" % round(sum(f["runtime"] for f in got) / 60.0)
        sec = {"id": key, "title": title, "sub": sub, "intro": intro,
               "items": items}
        if key == "indie":
            sec["open"] = True
        sections.append(sec)

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert len(ids) == 21, len(ids)
    for s in sections:
        assert all(a["n"] <= b["n"] for a, b in zip(s["items"], s["items"][1:])), \
            "%s is out of year order" % s["title"]

    hours = sum(x["w"] for s in sections for x in s["items"])

    prop = {
        "slug": SLUG,
        "title": "John Carpenter",
        "subtitle": "the directed features",
        "kind": "films",
        "popularity": 61,
        "year": "1974–2010",
        "blurb": "Eighteen theatrical features and three optional TV films, "
                 "Dark Star to The Ward — about %d hours." % round(hours),
        "unit": {"one": "film", "many": "films"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "accent": "#1F6E91",
        "accentDark": "#72CDEE",
        "tiers": False,
        "notes": [
            ["The TV films are optional rows.", "Someone's Watching Me!, "
             "Elvis and Body Bags are features he directed for television — "
             "the filmography's own table lists them with the rest and "
             "marks them, so this list does the same."],
            ["Directing only.", "The films he wrote, produced or scored "
             "for other directors — Halloween sequels included — are not "
             "here, and neither are the shorts or the television "
             "episodes."],
            ["Bar widths are runtimes.", "From Wikidata, in hours, for "
             "all 21."],
            "Filmography from Wikipedia's John Carpenter filmography; "
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
