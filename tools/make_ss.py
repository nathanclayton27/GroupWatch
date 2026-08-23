#!/usr/bin/env python3
"""Generate properties/sight-and-sound.json — the 2022 critics' top 100.

    python tools/make_ss.py

The Sight and Sound Greatest Films of All Time, 2022 critics' poll, exactly
as the poll ranks it — 100 films, ties sharing a number and wearing the
poll's own "=" mark. Rank bands for sections, rank for n, runtimes for
weights. Random button on: it's a lifetime list, not a syllabus.

Data: tools/data/sight-and-sound.json via scratch/agent-canons/collect_ss.py
(BFI's own results page, top ten cross-checked against Wikipedia's article,
every film verified on Wikidata by year and director).
"""
import json
import pathlib
import unicodedata

SLUG = "sight-and-sound"
ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = pathlib.Path(__file__).resolve().parent / "data" / ("%s.json" % SLUG)
OUT = ROOT / "properties" / ("%s.json" % SLUG)

BANDS = [
    ("top", "1–10", 1, 10,
     "Jeanne Dielman unseated Vertigo in 2022 — the first film by a woman "
     "to top the poll in its seventy years."),
    ("b11", "11–25", 11, 25, ""),
    ("b26", "26–50", 26, 50, ""),
    ("b51", "51–100", 51, 100, ""),
]


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
    assert len(films) == 100, len(films)

    sections = []
    for key, title, lo, hi, intro in BANDS:
        got = [f for f in films if lo <= f["rank"] <= hi]
        assert got, key
        got.sort(key=lambda f: (f["rank"], f["t"]))
        items = []
        for f in got:
            year = f.get("wd_year") or f["year"]
            note = "%s, %d" % (f["director"], year)
            it = {"id": "ss-%d-%s" % (year, slug(f["t"])),
                  "t": f["t"],
                  "n": ("=%d" % f["rank"]) if f["tie"] else "#%d" % f["rank"],
                  "w": round((f["min"] or 0) / 60.0, 2),
                  "note": note}
            if not f["min"]:
                it["note"] += " · no runtime on record — weighs nothing"
            items.append(it)
        hours = sum(x["w"] for x in items)
        sec = {"id": key, "title": title,
               "sub": "%d films · %d hours" % (len(got), round(hours)),
               "items": items}
        if intro:
            sec["intro"] = intro
        if key == "top":
            sec["open"] = True
        sections.append(sec)

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), \
        "duplicate ids: %s" % sorted({i for i in ids if ids.count(i) > 1})[:6]
    assert len(ids) == 100
    hours = sum(x["w"] for s in sections for x in s["items"])
    ties = sorted({f["rank"] for f in films if f["tie"]})

    prop = {
        "slug": SLUG,
        "title": "Sight & Sound 100",
        "subtitle": "the 2022 critics' poll, as ranked",
        "kind": "films",
        "order": 66,
        "year": "%d–%d" % (min(f.get("wd_year") or f["year"] for f in films),
                           max(f.get("wd_year") or f["year"] for f in films)),
        "blurb": "The 100 greatest films of all time per Sight and Sound's "
                 "2022 critics' poll — about %d hours, ties and all. Watch "
                 "in any order; the ranks are the argument." % round(hours),
        "unit": {"one": "film", "many": "films"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "accent": "#33383D",
        "accentDark": "#E2554A",
        "tiers": False,
        "random": True,
        "notes": [
            ["Ties share a number, exactly as the poll prints them.",
             "An = on a rank means the poll's own tie — %d positions are "
             "shared, which is why some numbers never appear. Still 100 "
             "films." % len(ties)],
            ["Bar widths are runtimes.",
             "From Wikidata, with each film's own Wikipedia article filling "
             "the gaps — which is how the longest entry here keeps its full "
             "%d minutes instead of being capped."
             % max(f["min"] or 0 for f in films)],
            ["Where the list comes from.",
             "The ranked list is read from the BFI's own results page — the "
             "reference Wikipedia's record of the poll points to, since the "
             "encyclopedia's article keeps only the top ten. That top ten "
             "is cross-checked against the article, and every film on the "
             "hundred is verified against Wikidata by year and director "
             "before it gets a row."],
            "The 2022 Sight and Sound critics' poll, via bfi.org.uk; "
            "runtimes from Wikidata and Wikipedia.",
        ],
        "sections": sections,
    }

    with OUT.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")
    print("wrote %s.json — 100 films, %d hours" % (SLUG, round(hours)))
    for s in sections:
        print("   %-10s %3d  %s" % (s["title"], len(s["items"]), s["sub"][:44]))


if __name__ == "__main__":
    main()
