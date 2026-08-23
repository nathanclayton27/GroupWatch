#!/usr/bin/env python3
"""Generate properties/real-time-films.json — films that run on the clock.

    python tools/make_realtime.py

Every film on the list in Wikipedia's "Real time (media)" article — the
series, episodes and radio entries screened out — in decade-ish sections.
Unweighted grab bag: the runtime IS the premise, so it rides on every note
instead of the bar. Random button intended.

Data: tools/data/real-time-films.json via
scratch/agent-canons/collect_realtime.py.
"""
import json
import pathlib
import unicodedata

SLUG = "real-time-films"
ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = pathlib.Path(__file__).resolve().parent / "data" / ("%s.json" % SLUG)
OUT = ROOT / "properties" / ("%s.json" % SLUG)

ERAS = [
    ("clock", "The clock starts", None, 1949,
     "Dreyer, Hitchcock and the noirs discover that screen minutes can be "
     "story minutes."),
    ("midcentury", "Midcentury", 1950, 1969,
     "High Noon and 12 Angry Men make the ticking clock respectable."),
    ("lull", "The long lull", 1970, 1999, ""),
    ("aughts", "The 2000s", 2000, 2009,
     "Russian Ark does it in one take; 24's film spin-off does it with a "
     "countdown."),
    ("tens", "The 2010s", 2010, 2019, ""),
    ("twenties", "The 2020s", 2020, None, ""),
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
            if f.get("runtime"):
                bits.append("%d min on the clock" % f["runtime"])
            else:
                bits.append("runtime unverified")
            if f.get("tvfilm") or "Movie" in (f.get("marker") or ""):
                bits.append("a TV film")
            items.append({"id": "rtf-%d-%s" % (f["year"], slug(f["t"])),
                          "t": f["t"], "n": str(f["year"]),
                          "note": " · ".join(bits)})
        sec = {"id": key, "title": title,
               "sub": "%d–%d · %d films" % (got[0]["year"], got[-1]["year"],
                                            len(got)),
               "items": items}
        if intro:
            sec["intro"] = intro
        if key == "clock":
            sec["open"] = True
        sections.append(sec)

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), \
        "duplicate ids: %s" % sorted({i for i in ids if ids.count(i) > 1})[:6]
    assert len(ids) == len(films)
    n_series = sum(1 for e in d["excluded"]
                   if "series" in e["why"] or "episode" in e["why"])

    prop = {
        "slug": SLUG,
        "title": "Real Time",
        "subtitle": "films where screen minutes are story minutes",
        "kind": "films",
        "order": 70,
        "year": "%d–%d" % (min(f["year"] for f in films),
                           max(f["year"] for f in films)),
        "blurb": "%d films that unfold in real time, from Wikipedia's own "
                 "list — the runtime is the plot, so it's on every note. Any "
                 "order." % len(films),
        "unit": {"one": "film", "many": "films"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "accent": "#B4292F",
        "accentDark": "#F0E6C8",
        "tiers": False,
        "random": True,
        "notes": [
            ["The runtime is the point.",
             "A real-time film's length is its story's length, so minutes "
             "sit on every note (Wikidata durations, the film's own article "
             "where Wikidata is silent) and nothing is weighted — this is a "
             "grab bag, not a schedule."],
            ["Films only.",
             "Wikipedia's list mixes in TV — 24, The Bear's \"Review\", a "
             "radio soap opera. The %d series, episodes and broadcasts were "
             "screened out, and a couple of series hiding behind bare years "
             "(The Pitt, Adolescence) were caught by their Wikidata typing. "
             "Made-for-TV films stay, flagged." % n_series],
            "From the list in Wikipedia's \"Real time (media)\"; runtimes "
            "from Wikidata and film articles.",
        ],
        "sections": sections,
    }

    with OUT.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")
    print("wrote %s.json — %d films (%d excluded)"
          % (SLUG, len(films), len(d["excluded"])))
    for s in sections:
        print("   %-18s %2d  %s" % (s["title"], len(s["items"]), s["sub"][:44]))


if __name__ == "__main__":
    main()
