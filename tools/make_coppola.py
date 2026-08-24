#!/usr/bin/env python3
"""Generate properties/coppola.json.

    PYTHONIOENCODING=utf-8 python tools/make_coppola.py

The twenty-three features Francis Ford Coppola directed, Dementia 13 to
Megalopolis, in release order and weighted by runtime — plus New York Stories
as an optional row, the anthology he directed one segment of.

Captain EO is a short and stays out. So does everything from the source's
other tables: the films he only wrote (Patton, The Great Gatsby), only
produced (American Graffiti, The Virgin Suicides), only executive-produced
(THX 1138, Kagemusha, Mishima), and the Corman-era second-unit, assistant
director and re-edit credits the article files under Other roles — including
the uncredited reshoots on Supernova.

Row facts are all read, never typed: Registry inductions come from the
filmography table's own Notes column, the Palme d'Or and Oscar notes from
Wikidata P166, the re-cuts from the article's lede, runtimes from P2047 with
a P577 year gate. Apocalypse Now is weighted by the 1979 release, the
statement Wikidata marks as the prime version, rather than by Redux.

Data: scratch/agent-coppola/collect.py -> tools/data/coppola.json
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop
from gwlib.prop import join_bits, slug

SLUG = "coppola"

ERAS = [
    ("apprentice", "The apprenticeship", 1963, 1969,
     "Four features before The Godfather: a horror quickie shot fast, a New "
     "York comedy, a musical he was handed at Warner Bros., and a road "
     "picture of his own. He wrote three of the four, and the second-unit "
     "and assistant-director work of the same years is not on this list."),
    ("seventies", "The seventies", 1972, 1979,
     "Four films in eight years, and the reason the rest of the list exists. "
     "All four are in the National Film Registry; two of them took the Palme "
     "d'Or."),
    ("eighties", "The eighties", 1982, 1989,
     "The busiest stretch of his career — a studio musical that lost a "
     "fortune, two teenage pictures shot back to back, a jazz-club epic, a "
     "time-travel comedy and a car-maker's biography. New York Stories rides "
     "along as an optional row: he directed one segment of the three."),
    ("hired", "Work for hire", 1990, 1997,
     "A third Godfather, a studio horror picture, a comedy and a Grisham "
     "adaptation — then ten years without a film."),
    ("own", "His own money", 2007, 2024,
     "The late films, self-financed and made away from the studios: three in "
     "five years, then thirteen more before Megalopolis."),
]

# Phrasings for the re-cuts the lede lists, keyed on the film they belong to.
# The titles and years themselves come from the fetched article; The Godfather
# Part III's re-cut is not named here because its subtitle gives the film away.
RECUT_NOTE = {
    "Apocalypse Now": lambda rc: "Redux (%d) and the Final Cut (%d) run longer"
                                 % (rc[0][1], rc[1][1]),
    "The Outsiders": lambda rc: "Recut as The Complete Novel in %d" % rc[0][1],
    "The Cotton Club": lambda rc: "Recut as Encore in %d" % rc[0][1],
    "The Godfather Part III": lambda rc: "Recut and retitled in %d" % rc[0][1],
}

OSCARS = ("Best Picture", "Best Director")


def awards_bit(f):
    """"Palme d'Or at Cannes", "Best Picture and Best Director at the Oscars"
    — assembled from the P166 labels the collector kept."""
    bits = []
    if "Palme d'Or" in f["awards"]:
        bits.append("Palme d'Or at Cannes")
    won = [n for n in OSCARS if "Academy Award for %s" % n in f["awards"]]
    if won:
        bits.append("%s at the Oscars" % " and ".join(won))
    return join_bits(*bits)


def registry_bit(f):
    m = re.search(r"National Film Registry in ((?:19|20)\d{2})", f["tablenote"])
    return "National Film Registry, %s" % m.group(1) if m else ""


def main():
    data = pathlib.Path(__file__).resolve().parent / "data" / "coppola.json"
    films = json.loads(data.read_text(encoding="utf-8"))

    shorts = [f for f in films if f["kind"] == "short"]
    assert [f["t"] for f in shorts] == ["Captain EO"], shorts
    films = [f for f in films if f["kind"] != "short"]
    features = [f for f in films if f["kind"] == "feature"]
    segments = [f for f in films if f["kind"] == "segment"]
    assert len(features) == 23, len(features)      # the article's own count
    assert [f["t"] for f in segments] == ["New York Stories"], segments
    assert all(f["runtime"] for f in films), \
        [f["t"] for f in films if not f["runtime"]]
    assert films[0]["t"] == "Dementia 13" and films[-1]["t"] == "Megalopolis", \
        (films[0]["t"], films[-1]["t"])

    sections, placed = [], 0
    for key, title, lo, hi, intro in ERAS:
        got = [f for f in films if lo <= f["year"] <= hi]
        assert got, key
        placed += len(got)
        items = []
        for f in got:
            note = join_bits(awards_bit(f), registry_bit(f),
                             RECUT_NOTE[f["t"]](f["recuts"])
                             if f["t"] in RECUT_NOTE else "")
            it = {"id": "ffc-%d-%s" % (f["year"], slug(f["t"])),
                  "t": f["t"], "n": str(f["year"]),
                  "w": round(f["runtime"] / 60.0, 2)}
            if f["kind"] == "segment":
                it["opt"] = 1
                note = join_bits("Anthology film — he directed one segment of "
                                 "the three", note)
            if note:
                it["note"] = note
            items.append(it)
        nf = sum(1 for f in got if f["kind"] == "feature")
        sub = "%d–%d · %d feature%s" % (got[0]["year"], got[-1]["year"], nf,
                                        "s" if nf > 1 else "")
        if len(got) > nf:
            sub += " + 1 optional segment"
        sub += " · %d hours" % round(sum(f["runtime"] for f in got) / 60.0)
        sec = {"id": key, "title": title, "sub": sub, "intro": intro,
               "items": items}
        if key == "apprentice":
            sec["open"] = True
        sections.append(sec)

    assert placed == len(films), (placed, len(films))
    for s in sections:
        assert all(a["n"] <= b["n"] for a, b in zip(s["items"], s["items"][1:])), \
            "%s is out of year order" % s["title"]

    # the claims the era intros make, checked against the data rather than
    # trusted: three of the first four written, all four seventies films in
    # the Registry, two of them Palme d'Or winners
    first = [f for f in films if f["year"] <= 1969]
    assert sum(1 for f in first if f["wrote"]) == 3, first
    run = [f for f in films if 1972 <= f["year"] <= 1979]
    assert len(run) == 4 and all(registry_bit(f) for f in run), run
    assert sum(1 for f in run if "Palme d'Or" in f["awards"]) == 2, run
    assert films[-1]["year"] - [f for f in films if f["year"] < 2024][-1]["year"] \
        == 13

    mins = sum(f["runtime"] for f in films)
    fmins = sum(f["runtime"] for f in features)

    p = {
        "slug": SLUG,
        "title": "Francis Ford Coppola",
        "subtitle": "the directed features",
        "kind": "films",
        "order": 113,
        "year": "1963–2024",
        "blurb": "Twenty-three features from Dementia 13 to Megalopolis, plus "
                 "the anthology he directed a segment of — about %d hours."
                 % round(mins / 60.0),
        "unit": {"one": "film", "many": "films"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "accent": "#33231C",
        "accentDark": "#E0B36A",
        "tiers": False,
        "notes": [
            ["Directing only.", "The films he wrote for other directors, and "
             "the ones he produced or executive-produced — American Graffiti, "
             "THX 1138, Kagemusha, The Virgin Suicides — are not here. "
             "Neither is the second-unit, assistant-director and re-edit work "
             "of the Corman years, the uncredited reshoot work, the "
             "television, or Captain EO, which is a short."],
            ["New York Stories is an optional row.", "It is an anthology of "
             "three films by three directors; his is the segment Life Without "
             "Zoë. The filmography's own table lists it with the features, so "
             "it rides along, marked — and its bar is the whole anthology, "
             "which is what you would sit through."],
            ["Bar widths are runtimes.", "From Wikidata, in hours, for all %d "
             "rows — the %d features are about %d of the %d hours. Apocalypse "
             "Now is weighted by the 1979 release rather than by Redux; where "
             "a film has a later re-cut, the row says so."
             % (len(films), len(features), round(fmins / 60.0),
                round(mins / 60.0))],
            "Filmography from Wikipedia's Francis Ford Coppola filmography "
            "(the director table); runtimes, Palme d'Or and Oscar wins from "
            "Wikidata.",
        ],
        "sections": sections,
    }

    out = prop.write(p)
    ids = [x["id"] for s in sections for x in s["items"]]
    print("wrote %s — %d rows (%d features + 1 optional segment), %.1f hours"
          % (out.name, len(ids), len(features), mins / 60.0))
    for s in sections:
        print("   %-20s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
