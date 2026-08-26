#!/usr/bin/env python3
"""Generate properties/satoshi-kon.json.

    python3 tools/make_satoshi_kon.py

Everything Satoshi Kon directed: the four features (runtimes from Wikidata),
Paranoia Agent's thirteen episodes at 24 minutes each, and the one-minute
Ani*Kuri15 short Good Morning (Ohayō) — the Satoshi Kon article's own
television table dates it 2008 and calls it a 1-minute short, which is also
its weight.

Not here: the films he only wrote or animated on (Roujin Z, Memories'
Magnetic Rose segment, Patlabor 2 layouts), and the three episodes of the
1993 JoJo's Bizarre Adventure OVA — episode direction on someone else's
series. Dreaming Machine, unfinished at his death in 2010, gets a note
instead of a row: there is nothing to watch.
"""
import json
import pathlib

SLUG = "satoshi-kon"

FILM_INTRO = ("Four features in nine years, every one of them about a "
              "boundary failing — performer and role, actress and century, "
              "dream and machine. All from Madhouse, all complete "
              "in themselves.")

FILM_NOTE = {
    "Perfect Blue": "His debut feature",
    "Paprika": "His last completed feature",
}


def slug(t):
    keep = "".join(c.lower() if c.isalnum() else "-" for c in t)
    while "--" in keep:
        keep = keep.replace("--", "-")
    return keep.strip("-")


def main():
    data = pathlib.Path(__file__).resolve().parent / "data"
    d = json.loads((data / "satoshi-kon.json").read_text(encoding="utf-8"))
    films, pa, short = d["films"], d["paranoia"], d["short"]
    assert len(films) == 4 and all(f["runtime"] for f in films), films
    assert len(pa["episodes"]) == 13, len(pa["episodes"])
    assert short["minutes"] == 1 and short["year"] == 2008, short

    fitems = []
    for f in films:
        it = {"id": "sk-%d-%s" % (f["year"], slug(f["t"])),
              "t": f["t"], "n": str(f["year"]),
              "w": round(f["runtime"] / 60.0, 2)}
        if f["t"] in FILM_NOTE:
            it["note"] = FILM_NOTE[f["t"]]
        fitems.append(it)
    fh = sum(f["runtime"] for f in films) / 60.0

    epw = round(24 / 60.0, 2)
    eitems = [{"id": "sk-pa-%d" % e["n"], "t": e["t"], "n": str(e["n"]),
               "w": epw} for e in pa["episodes"]]

    sections = [
        {"id": "films", "title": "The four films",
         "sub": "1997–2006 · 4 films · %d hours" % round(fh),
         "intro": FILM_INTRO, "items": fitems, "open": True},
        {"id": "paranoia", "title": "Paranoia Agent",
         "sub": "2004 · 13 episodes · %d hours" % round(13 * 24 / 60.0),
         "intro": "The one television series — built from ideas that "
                  "wouldn't fit in the films, and aired between Tokyo "
                  "Godfathers and Paprika. Episodes weigh 24 minutes each.",
         "items": eitems},
        {"id": "ohayo", "title": "Ohayō",
         "sub": "2008 · one minute",
         "intro": "A one-minute short made for the Ani*Kuri15 television "
                  "anthology — the last thing he finished.",
         "items": [{"id": "sk-2008-ohayo", "t": "Ohayō (Good Morning)",
                    "n": "2008", "w": round(1 / 60.0, 2),
                    "note": "1-minute short for the Ani*Kuri15 television "
                            "anthology"}]},
    ]

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert len(ids) == 18, len(ids)
    for s in sections:
        ns = [x["n"] for x in s["items"]]
        key = [int(n) for n in ns]
        assert key == sorted(key), "%s out of order" % s["title"]

    hours = sum(x["w"] for s in sections for x in s["items"])

    prop = {
        "slug": SLUG,
        "title": "Satoshi Kon",
        "subtitle": "everything he directed",
        "kind": "anime",
        "popularity": 45,
        # Not a story, so not a sequence: the order these came out in
        # is a fact about the maker, not an instruction to the viewer
        # (Nathan, CLU-372). Prerequisites, where any exist, live in
        # tools/data/sequences.json and are enforced separately.
        "random": True,
        "year": "1997–2008",
        "blurb": "Four films, thirteen episodes of Paranoia Agent, and a "
                 "one-minute short — the complete directed work, about %d "
                 "hours." % round(hours),
        "unit": {"one": "entry", "many": "entries"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "accent": "#8B3A85",
        "accentDark": "#E794DC",
        "tiers": False,
        "notes": [
            ["This is the whole thing.", "Kon died in 2010, at 46, with "
             "four features, one series and a short finished. It all fits "
             "in a week, and none of it is skippable."],
            ["Dreaming Machine has no row.", "His fifth feature was in "
             "production at Madhouse when he died and was never completed "
             "— by 2013 only 600 of 1,500 shots were animated, and the "
             "studio has declined to finish it with another director in "
             "his place. There is nothing to watch, so there is nothing "
             "to tick."],
            ["Bar widths are runtimes.", "Film runtimes from Wikidata; "
             "Paranoia Agent episodes weigh a flat 24 minutes; the short "
             "weighs its one minute."],
            "Filmography and the Good Morning short from Wikipedia's "
            "Satoshi Kon article; episode list from List of Paranoia "
            "Agent episodes; film runtimes from Wikidata.",
        ],
        "sections": sections,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")
    print("wrote %s.json — %d entries, %.2f hours" % (SLUG, len(ids), hours))
    for s in sections:
        print("   %-16s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
