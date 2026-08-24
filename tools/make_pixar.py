#!/usr/bin/env python3
"""Generate properties/pixar.json — every Pixar feature, in release order.

    python tools/make_pixar.py

Features from the "Released" table of Wikipedia's List of Pixar films (all 31,
Toy Story 1995 through Toy Story 5 2026), grouped by decade, weighted by
runtime. The classic theatrical shorts — the "Short films" table of List of
Pixar shorts, Andre & Wally B. through Bao — sit in an optional section at the
end, each noting the feature it was first released with.

Data: tools/data/pixar.json, built by scratch/agent-canons/collect_pixar.py
(wikitext parse + Wikidata P2047 runtimes, cached in pixar-runtimes.json).
"""
import json
import pathlib

SLUG = "pixar"
ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = pathlib.Path(__file__).resolve().parent / "data" / "pixar.json"
OUT = ROOT / "properties" / ("%s.json" % SLUG)

DECADES = [
    ("nineties", "The '90s", 1995, 1999,
     "Toy Story invents the studio; two more prove it was no fluke."),
    ("aughts", "The 2000s", 2000, 2009,
     "Monsters, Nemo, the Incredibles, a rat, a robot and a balloon house — "
     "the run people mean when they say Pixar."),
    ("tens", "The 2010s", 2010, 2019, ""),
    ("twenties", "The 2020s", 2020, 2026, ""),
]


def slug(t):
    import unicodedata
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    keep = "".join(c.lower() if (c.isalnum() and c.isascii()) else "-"
                   for c in t)
    while "--" in keep:
        keep = keep.replace("--", "-")
    return keep.strip("-")


def main():
    d = json.loads(DATA.read_text(encoding="utf-8"))
    feats, shorts = d["features"], d["shorts"]
    assert [f["num"] for f in feats] == list(range(1, len(feats) + 1))
    assert all(f["runtime"] for f in feats), "a feature without a runtime"

    sections = []
    for key, title, lo, hi, intro in DECADES:
        got = [f for f in feats if lo <= f["year"] <= hi]
        assert got, key
        items = [{
            "id": "px-%d-%s" % (f["year"], slug(f["t"])),
            "t": f["t"], "n": str(f["year"]),
            "w": round(f["runtime"] / 60.0, 2),
        } for f in got]
        hours = sum(x["w"] for x in items)
        sec = {"id": key, "title": title,
               "sub": "#%d–%d · %d films · %d hours"
                      % (got[0]["num"], got[-1]["num"], len(got), round(hours)),
               "items": items}
        if intro:
            sec["intro"] = intro
        if key == "nineties":
            sec["open"] = True
        sections.append(sec)

    sh_items = []
    for s in shorts:
        bits = []
        if s["with"]:
            bits.append("First released with %s" % s["with"])
        if s["runtime"]:
            bits.append("%d min" % s["runtime"])
        sh_items.append({
            "id": "px-s-%d-%s" % (s["year"], slug(s["t"])),
            "t": s["t"], "n": str(s["year"]), "opt": True,
            "w": round((s["runtime"] or 0) / 60.0, 2),
            **({"note": " · ".join(bits)} if bits else {}),
        })
    sections.append({
        "id": "shorts", "title": "The theatrical shorts",
        "sub": "%d shorts · optional, a couple of hours in all" % len(sh_items),
        "intro": "The classic shorts program — the ones that ran before the "
                 "features, Andre & Wally B. through Bao. All optional; each "
                 "row names the feature it was first attached to.",
        "items": sh_items,
    })

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), \
        "duplicate ids: %s" % sorted({i for i in ids if ids.count(i) > 1})[:6]
    assert len(ids) == len(feats) + len(shorts)
    fh = sum(f["runtime"] for f in feats) / 60.0

    prop = {
        "slug": SLUG,
        "title": "Pixar",
        "subtitle": "every feature, in release order",
        "kind": "films",
        "popularity": 90,
        "year": "1995–2026",
        "blurb": "All %d Pixar features in release order — about %d hours — "
                 "plus the %d classic theatrical shorts as optional extras."
                 % (len(feats), round(fh), len(shorts)),
        "unit": {"one": "film", "many": "films"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "accent": "#1E5FA8",
        "accentDark": "#F0C24B",
        "tiers": False,
        "notes": [
            ["Release order, nothing skipped.",
             "Every feature the studio has released, sequels and all, in the "
             "order they hit theaters. The shorts section at the end is "
             "optional — tick them as you meet them."],
            ["Bar widths are runtimes.",
             "From Wikidata (duration, P2047) for every feature and short."],
            "Features from Wikipedia's List of Pixar films; shorts from List "
            "of Pixar shorts; runtimes from Wikidata.",
        ],
        "sections": sections,
    }

    with OUT.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")
    print("wrote %s.json — %d features (%d hours) + %d shorts"
          % (SLUG, len(feats), round(fh), len(shorts)))
    for s in sections:
        print("   %-24s %2d  %s" % (s["title"], len(s["items"]), s["sub"][:48]))


if __name__ == "__main__":
    main()
