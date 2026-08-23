#!/usr/bin/env python3
"""Generate properties/bottle-episodes.json — TV's famous stuck-in-a-room hours.

    python tools/make_bottle.py

One row per notable bottle episode: every member of Wikipedia's own
Category:Bottle television episodes, plus the two episodes the Bottle episode
article's citations name (Archer's "Vision Quest", BoJack's "Free Churro").
Rows read Time Loops style — Show — "Title", n = SxE — and every season and
number was checked against the show's episode tables where they exist
(scratch/agent-canons/collect_bottle_2.py, verify_eps parser).

Data: tools/data/bottle-episodes.json.
"""
import json
import pathlib
import unicodedata

SLUG = "bottle-episodes"
ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = pathlib.Path(__file__).resolve().parent / "data" / ("%s.json" % SLUG)
OUT = ROOT / "properties" / ("%s.json" % SLUG)

ERAS = [
    ("classics", "The classics", None, 1999,
     "Doctor Who locks its TARDIS doors in 1964; Trek, Homicide and Friends "
     "learn the same trick."),
    ("aughts", "The 2000s", 2000, 2009, ""),
    ("tens", "The 2010s", 2010, 2019,
     "Fly, Cooperative Calligraphy, The Box — the decade the bottle episode "
     "became a brag."),
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
    eps = d["episodes"]
    assert all(r["year"] for r in eps), \
        [r["t"] for r in eps if not r["year"]]
    assert all(r.get("special") or (r["s"] is not None and r["e"] is not None)
               for r in eps)

    sections = []
    for key, title, lo, hi, intro in ERAS:
        got = [r for r in eps
               if (lo is None or r["year"] >= lo)
               and (hi is None or r["year"] <= hi)]
        assert got, key
        got.sort(key=lambda r: (r["year"], r["show"], r["t"]))
        items = [{
            "id": "be-%d-%s" % (r["year"], slug(r["show"] + "-" + r["t"])),
            "t": "%s — “%s”" % (r["show"], r["t"]),
            "n": "Special" if r.get("special")
                 else ("S%d · serial %d" % (r["s"], r["e"]))
                 if r.get("serial") else "S%dE%d" % (r["s"], r["e"]),
            "note": str(r["year"])
                    + (" · a between-seasons special" if r.get("special")
                       else "")
                    + (" · numbered by broadcast; written earlier in the "
                       "season" if r.get("airorder") else ""),
        } for r in got]
        sec = {"id": key, "title": title,
               "sub": "%d–%d · %d episodes" % (got[0]["year"], got[-1]["year"],
                                               len(got)),
               "items": items}
        if intro:
            sec["intro"] = intro
        if key == "classics":
            sec["open"] = True
        sections.append(sec)

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), \
        "duplicate ids: %s" % sorted({i for i in ids if ids.count(i) > 1})[:6]
    assert len(ids) == len(eps)
    shows = {r["show"] for r in eps}
    n_table = sum(1 for r in eps if r["via"] != "infobox")

    prop = {
        "slug": SLUG,
        "title": "Bottle Episodes",
        "subtitle": "one set, one cast, forty minutes",
        "kind": "episodes",
        "order": 71,
        "year": "%d–%d" % (min(r["year"] for r in eps),
                           max(r["year"] for r in eps)),
        "blurb": "%d famous bottle episodes across %d shows — the stuck-in-a-"
                 "room hours TV brags about. One row each, any order."
                 % (len(eps), len(shows)),
        "unit": {"one": "episode", "many": "episodes"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "accent": "#A8681C",
        "accentDark": "#EBAE4A",
        "tiers": False,
        "random": True,
        "notes": [
            ["What counts.",
             "An episode shot cheap and small on standing sets — the term is "
             "Outer Limits producer Leslie Stevens', for shows pulled \"right "
             "out of a bottle\". The rows are Wikipedia's own bottle-episode "
             "category, plus the two episodes the encyclopedia's article "
             "cites by name. Three episodes merely TITLED \"Bottle Episode\" "
             "(Supergirl, Harley Quinn, The Simpsons) are gags about literal "
             "bottles, and the article says so — they are not here."],
            ["Every number is checked.",
             "Each row's season and episode were read from the episode's own "
             "article and %d of %d were confirmed against the show's episode "
             "tables; a mismatch fails the build rather than shipping a "
             "wrong number." % (n_table, len(eps))],
            ["Spoiler physics.",
             "Bottle episodes tend to land hardest mid-show — Fly means more "
             "with two seasons of Breaking Bad behind it. Tick them as your "
             "watches reach them, or dip in cold for the sitcom ones."],
            "From Wikipedia's Category:Bottle television episodes and the "
            "Bottle episode article; numbers verified against episode "
            "tables.",
        ],
        "sections": sections,
    }

    with OUT.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")
    print("wrote %s.json — %d episodes, %d shows" % (SLUG, len(eps), len(shows)))
    for s in sections:
        print("   %-14s %2d  %s" % (s["title"], len(s["items"]), s["sub"][:44]))


if __name__ == "__main__":
    main()
