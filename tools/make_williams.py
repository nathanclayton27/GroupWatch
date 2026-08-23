#!/usr/bin/env python3
"""Generate properties/robin-williams.json.

    python3 tools/make_williams.py

Robin Williams' film roles in release order, one row per film, from
Wikipedia's "List of Robin Williams performances" film table with runtimes
from Wikidata. The table's own notes ride along where they are factual (film
debut, voice roles, posthumous releases); everything else stays quiet.

Three rows have no resolvable runtime — a 1987 TV film, a 2011 short and a
2023 studio-anniversary short — and weigh nothing rather than a guess.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib.prop import slug

SLUG = "robin-williams"

ERAS = [
    ("start", "Out of stand-up", 1977, 1986,
     "Popeye, The World According to Garp, Moscow on the Hudson — the decade "
     "where the comedian keeps testing whether he is allowed to act."),
    ("run", "The run", 1987, 1999,
     "Good Morning Vietnam through Bicentennial Man: the Oscar, the genie, "
     "Mrs. Doubtfire — the stretch everyone can quote."),
    ("dark", "The darker turn", 2000, 2009,
     "One Hour Photo and Insomnia sit in the middle of this — the run where "
     "he kept choosing the unsettling part."),
    ("late", "The last films", 2010, 2023,
     "The final decade, the posthumous releases, and one last short."),
]


def main():
    films = json.loads((pathlib.Path(__file__).resolve().parent / "data"
                        / "williams.json").read_text(encoding="utf-8"))
    for f in films:
        f["t"] = f["t"].replace("''", "").strip()
    films.sort(key=lambda f: (f["year"], f["t"]))

    sections = []
    for key, title, lo, hi, intro in ERAS:
        got = [f for f in films if lo <= f["year"] <= hi]
        if not got:
            continue
        items = []
        for f in got:
            bits = []
            note = (f.get("tablenote") or "").strip()
            keep = any(k in note.lower() for k in
                       ("debut", "voice", "posthumous", "cameo", "uncredited",
                        "documentary", "short film", "television film"))
            if keep and note:
                bits.append(note.rstrip("."))
            if not f.get("runtime"):
                bits.append("No runtime on record — weighs nothing")
            items.append({
                "id": "rw-%d-%s" % (f["year"], slug(f["t"])),
                "t": f["t"], "n": str(f["year"]),
                "w": round((f.get("runtime") or 0) / 60.0, 2),
                **({"note": " · ".join(bits)} if bits else {}),
            })
        hours = sum(x["w"] for x in items)
        sec = {"id": key, "title": title,
               "sub": "%d–%d · %d films · %d hours"
                      % (got[0]["year"], got[-1]["year"], len(got), round(hours)),
               "intro": intro, "items": items}
        if key == "start":
            sec["open"] = True
        assert all(a["n"] <= b["n"] for a, b in zip(items, items[1:]))
        sections.append(sec)

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert len(ids) == len(films), (len(ids), len(films))
    hours = sum(x["w"] for s in sections for x in s["items"])

    prop = {
        "slug": SLUG,
        "title": "Robin Williams",
        "subtitle": "the film roles, in release order",
        "kind": "films",
        "order": 55,
        "year": "1977–2023",
        "blurb": "%d films across five decades — about %d hours, from the "
                 "stand-up years to the posthumous releases." % (len(films), round(hours)),
        "unit": {"one": "film", "many": "films"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "accent": "#8A4A2E",
        "accentDark": "#E89A6F",
        "tiers": False,
        "notes": [
            ["Films only.", "The television work, the theater, and the "
             "stand-up specials are their own bodies of work; this is the "
             "filmography, and the table's own factual notes — a debut, a "
             "voice role, a posthumous release — ride along where they help."],
            ["Bar widths are runtimes.", "From Wikidata for 71 of the 74; the "
             "three without one weigh nothing rather than a guess, and say so."],
            "Filmography from Wikipedia's List of Robin Williams "
            "performances; runtimes from Wikidata.",
        ],
        "sections": sections,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")
    print("wrote %s.json — %d films, %d hours" % (SLUG, len(ids), round(hours)))
    for s in sections:
        print("   %-20s %2d  %s" % (s["title"], len(s["items"]), s["sub"][:44]))


if __name__ == "__main__":
    main()
