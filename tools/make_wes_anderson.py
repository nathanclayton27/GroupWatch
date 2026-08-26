#!/usr/bin/env python3
"""Generate properties/wes-anderson.json.

    PYTHONIOENCODING=utf-8 python tools/make_wes_anderson.py

Every feature Wes Anderson has directed, in release order — the thirteen rows
of the Feature films table in Wikipedia's "Wes Anderson filmography", Bottle
Rocket (1996) to The Phoenician Scheme (2025). Every one of those rows is a
bare {{yes}} in the Director column; the Producer only and Executive producer
only bullet lists beside the table are not.

WHY FOUR SECTIONS, AND WHERE THE LINES FALL

The divisions are all things the sources state, not moods:

  * 1996–2001 — the three features Owen Wilson co-wrote. His name is on the
    screenplay of Bottle Rocket, Rushmore and The Royal Tenenbaums and on no
    Anderson film after them, which makes the boundary a fact rather than a
    feeling.
  * 2004–2012 — four films with new co-writers: Noah Baumbach on two, Roman
    Coppola on two, Jason Schwartzman alongside Coppola on one of those. The
    first of the two stop-motion features sits here.
  * 2014–2021 — from The Grand Budapest Hotel on, the screenplay credit is
    his alone over a shared *story* credit, and these three all went out
    through Fox Searchlight / Searchlight.
  * 2023–2025 — the two Focus Features pictures with the Netflix compilation
    between them. The sole-screenplay credit continues, so the line here is
    the distributor, which is where the change actually is.

THE SHORTS: NOT SHIPPED, AND THIS IS WHY

The default was an optional tail section for Hotel Chevalier, Castello
Cavalcanti and the Roald Dahl shorts. They do not enumerate into a weighted
list, and the collector's data is what says so rather than a preference:

  * three of the ten cannot be weighted from the one runtime source at all.
    Do You Like to Read? and Asteroid City: Location Featurette have no
    Wikidata item; Castello Cavalcanti's item has no P2047. An unweighted row
    in a weighted list is silently counted as one hour downstream, which is a
    guessed runtime landing in real finish-date maths;
  * four of the seven that can be weighted — the Dahl quartet — are already
    on this list, as the 2024 feature The Wonderful Story of Henry Sugar and
    Three More, which IS those four shorts. Listing them again would count
    the same 88 minutes twice;
  * that leaves Hotel Chevalier, the 1993 Bottle Rocket short and Cousin Ben
    Troop Screening. Three of ten is a subset, not the shorts.

So the features are weighted and the shorts are absent, and the notes on the
shipped list say all of this so a reader can argue it back. The alternative —
shipping all ten unweighted alongside weighted features — is the exact bug
this project has already been bitten by.

RUNTIMES

All thirteen from Wikidata P2047 and nothing else, each gated on a P577
publication year within a year of the filmography's year. Twelve carry P2047
directly. The Wonderful Story of Henry Sugar and Three More has none of its
own but declares its parts (P527) — exactly the four 2023 Dahl shorts — and
each of those carries P2047, so its runtime is the sum of its own declared
parts: 37 + 17 + 17 + 17 = 88. Same property, same database, read rather than
typed, and the asserts below allow that route for exactly one row.

Data: scratch/wesanderson/collect.py -> scratch/wesanderson/wes_anderson_data.json
Accent: scratch/wesanderson/accent.py
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop
from gwlib.prop import slug

SLUG = "wes-anderson"
DATA = (pathlib.Path(__file__).resolve().parent.parent / "scratch" /
        "wesanderson" / "wes_anderson_data.json")

ERAS = [
    ("wilson", "Written with Owen Wilson", 1996, 2001,
     "The three features Anderson and Owen Wilson wrote together: a debut "
     "for Columbia, expanded from a short of their own, then two for "
     "Touchstone. No Anderson screenplay after these carries Wilson's name."),
    ("cowriters", "New co-writers, and the first puppets", 2004, 2012,
     "Four films and three new names on the screenplay: Noah Baumbach on "
     "two, Roman Coppola on two, Jason Schwartzman beside Coppola on one of "
     "those. Fantastic Mr. Fox is the first of his two stop-motion features "
     "and the first of his two Roald Dahl adaptations."),
    ("searchlight", "Sole screenplay, and Searchlight", 2014, 2021,
     "From The Grand Budapest Hotel on, the screenplay credit is his alone "
     "over a story credit shared with Hugo Guinness, Roman Coppola, Jason "
     "Schwartzman and Kunichi Nomura in turn. All three of these went out "
     "through Searchlight, and Isle of Dogs is the second of the two "
     "stop-motion features."),
    ("focus", "Focus, and a Netflix detour", 2023, 2025,
     "Asteroid City and The Phoenician Scheme went out through Focus "
     "Features. Between them sits the odd one on the filmography: four "
     "shorts made for Netflix out of Roald Dahl, released together as a "
     "single feature."),
]

# Row notes say what the film IS. The stop-motion pair is not typed here —
# it is read out of the data and cross-checked below against two independent
# signals before either note is allowed to say the words.
NOTES = {
    "Bottle Rocket": "Expanded from his own short film of the same name",
    "Fantastic Mr. Fox": "Stop-motion animation · from the Roald Dahl novel",
    "Isle of Dogs": "Stop-motion animation",
    "The Wonderful Story of Henry Sugar and Three More":
        "The four 2023 Roald Dahl shorts, released together as one film",
}


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    films, shorts = data["features"], data["shorts"]

    # ---- the list itself ---------------------------------------------------
    assert len(films) == 13, len(films)
    assert films[0]["t"] == "Bottle Rocket" and films[0]["year"] == 1996, films[0]
    assert films[-1]["t"] == "The Phoenician Scheme" and films[-1]["year"] == 2025, \
        films[-1]
    assert all(f["year"] <= g["year"] for f, g in zip(films, films[1:])), \
        "features are not in release order"
    assert len({f["year"] for f in films}) == 13, "two features share a year"
    # he directed all thirteen and wrote all thirteen; the table's own columns
    assert all(f["wrote"] for f in films), \
        [f["t"] for f in films if not f["wrote"]]

    # ---- runtimes: one source, and the one exception named ------------------
    assert all(f["runtime"] for f in films), \
        "unweighted row in a weighted list: %s" \
        % [f["t"] for f in films if not f["runtime"]]
    assert all(f["qid"] and f["year_gate"] for f in films), \
        [f["t"] for f in films if not (f["qid"] and f["year_gate"])]
    # Every runtime is P2047. Exactly one row reaches it through the item's own
    # P527 parts, and that row is the compilation; if a second one ever needs
    # that route, or if this one stops needing it, the build stops here rather
    # than quietly mixing two kinds of number.
    direct = [f for f in films if f["runtime_src"] == "P2047"]
    parted = [f for f in films if f["runtime_src"] == "P2047-sum-of-P527-parts"]
    assert len(direct) + len(parted) == len(films), \
        "a runtime came from somewhere other than P2047: %s" \
        % [(f["t"], f["runtime_src"]) for f in films
           if f["runtime_src"] not in ("P2047", "P2047-sum-of-P527-parts")]
    assert len(parted) == 1 and parted[0]["year"] == 2024, \
        [f["t"] for f in parted]
    comp = parted[0]
    assert comp["t"] == "The Wonderful Story of Henry Sugar and Three More", comp["t"]
    assert len(comp["parts"]) == 4, comp["parts"]
    assert all(p["runtime"] for p in comp["parts"]), comp["parts"]
    assert comp["runtime"] == sum(p["runtime"] for p in comp["parts"]) == 88, \
        (comp["runtime"], comp["parts"])
    # the four parts are the four Dahl shorts the Short films table lists
    dahl = {s["t"] for s in shorts
            if "Roald Dahl" in s["tablenote"] and s["year"] == 2023}
    assert dahl == {p["label"] for p in comp["parts"]}, \
        (sorted(dahl), sorted(p["label"] for p in comp["parts"]))
    # The Phoenician Scheme's item carries a deprecated 120 beside a live 105.
    # Deprecated is Wikidata saying the value is wrong; the note on the shipped
    # list says so, so the build checks the situation still exists.
    ps = films[-1]
    ranks = {(s["amount"], s["rank"]) for s in ps["p2047_seen"]}
    assert (120.0, "deprecated") in ranks and (105.0, "normal") in ranks, ranks
    assert ps["runtime"] == 105, ps["runtime"]

    # ---- the two animated ones, agreed on by two independent signals ---------
    animated = [f for f in films if "Q202866" in f["p31"]]
    leadsays = [f for f in films
                if "stop-motion" in (f["article"].get("lead") or "").lower()]
    assert [f["t"] for f in animated] == [f["t"] for f in leadsays] == \
        ["Fantastic Mr. Fox", "Isle of Dogs"], \
        ([f["t"] for f in animated], [f["t"] for f in leadsays])
    # ...and only those two rows are allowed to say "Stop-motion"
    assert {t for t, n in NOTES.items() if "Stop-motion" in n} == \
        {f["t"] for f in animated}

    # ---- the claims the era intros make, checked rather than trusted ---------
    def cowriters(f):
        a = f["article"]
        return a.get("writer") or a.get("screenplay") or ""

    wilson = [f for f in films if "Wilson" in cowriters(f)]
    assert [f["t"] for f in wilson] == \
        ["Bottle Rocket", "Rushmore", "The Royal Tenenbaums"], \
        [f["t"] for f in wilson]
    assert all(f["year"] <= 2001 for f in wilson)
    assert "short film of the same name" in films[0]["article"]["lead"], \
        films[0]["article"]["lead"][:200]
    assert "Columbia Pictures" in films[0]["article"].get("studio", ""), \
        films[0]["article"].get("studio")
    assert all("Touchstone" in f["article"].get("studio", "")
               for f in films if f["t"] in ("Rushmore", "The Royal Tenenbaums"))

    mid = [f for f in films if 2004 <= f["year"] <= 2012]
    assert len(mid) == 4, [f["t"] for f in mid]
    assert [f["t"] for f in mid if "Baumbach" in cowriters(f)] == \
        ["The Life Aquatic with Steve Zissou", "Fantastic Mr. Fox"]
    assert [f["t"] for f in mid if "Roman Coppola" in cowriters(f)] == \
        ["The Darjeeling Limited", "Moonrise Kingdom"]
    assert [f["t"] for f in mid if "Schwartzman" in cowriters(f)] == \
        ["The Darjeeling Limited"]
    dahlfilms = [f for f in films if "Dahl" in f["article"].get("based_on", "")]
    assert [f["t"] for f in dahlfilms] == \
        ["Fantastic Mr. Fox",
         "The Wonderful Story of Henry Sugar and Three More"], \
        [f["t"] for f in dahlfilms]

    late = [f for f in films if f["year"] >= 2014]
    assert len(late) == 6, [f["t"] for f in late]
    # sole screenplay from 2014 on: the field says his name and nobody else's
    assert all(f["article"].get("screenplay") == "Wes Anderson" for f in late), \
        [(f["t"], f["article"].get("screenplay")) for f in late]
    assert not any(f["article"].get("writer") for f in late), \
        [f["t"] for f in late if f["article"].get("writer")]
    storytellers = " ".join(f["article"].get("story", "") for f in late)
    for name in ("Hugo Guinness", "Roman Coppola", "Jason Schwartzman",
                 "Kunichi Nomura"):
        assert name in storytellers, name
    searchlight = [f for f in films
                   if "Searchlight" in f["article"].get("distributor", "")]
    assert [f["t"] for f in films if 2014 <= f["year"] <= 2021] == \
        ["The Grand Budapest Hotel", "Isle of Dogs", "The French Dispatch"]
    assert all("Searchlight" in f["article"]["distributor"]
               for f in films if 2014 <= f["year"] <= 2021), \
        [(f["t"], f["article"].get("distributor")) for f in searchlight]
    recent = [f for f in films if f["year"] >= 2023]
    assert [f["t"] for f in recent
            if "Focus Features" in f["article"].get("distributor", "")] == \
        ["Asteroid City", "The Phoenician Scheme"]
    assert comp["article"].get("distributor") == "Netflix", \
        comp["article"].get("distributor")

    # ---- the shorts decision, as arithmetic rather than an opinion ----------
    assert len(shorts) == 10, len(shorts)
    weightable = [s for s in shorts if s["runtime"]]
    assert len(weightable) == 7, [s["t"] for s in weightable]
    assert {s["t"] for s in shorts if not s["runtime"]} == \
        {"Do You Like to Read?", "Asteroid City: Location Featurette",
         "Castello Cavalcanti"}, \
        [s["t"] for s in shorts if not s["runtime"]]
    assert all(s["runtime_src"] == "P2047" for s in weightable)
    # four of the seven are the compilation this list already carries
    already = [s for s in weightable if s["t"] in dahl]
    assert len(already) == 4 and \
        sum(s["runtime"] for s in already) == comp["runtime"] == 88, \
        [(s["t"], s["runtime"]) for s in already]
    leftover = [s for s in weightable if s["t"] not in dahl]
    assert {s["t"] for s in leftover} == \
        {"Bottle Rocket", "Hotel Chevalier", "Cousin Ben Troop Screening"}, \
        [s["t"] for s in leftover]
    # the P57 sweep found exactly one thing on neither table: an H&M
    # commercial, which the article files under Commercials
    assert [e["label"] for e in data["sweep_extras"]] == \
        ["Come Together: A Fashion Picture in Motion"], data["sweep_extras"]

    # ---- what the "directing only" note names, read from the article --------
    assert data["producer_only"] == ["The Squid and the Whale (2005)"], \
        data["producer_only"]
    assert data["exec_producer_only"] == \
        ["She's Funny That Way (2014)", "Escapes (2017)", "Uncropped (2023)"], \
        data["exec_producer_only"]
    ads = [a["company"] for a in data["commercials"]]
    assert ads == ["American Express", "Softbank", "Stella Artois",
                   "Sony Xperia", "Prada", "H&M", "Montblanc", "Montblanc"], ads
    assert len(data["music_videos"]) == 1, data["music_videos"]

    # ---- sections -----------------------------------------------------------
    sections = []
    for key, title, lo, hi, intro in ERAS:
        got = [f for f in films if lo <= f["year"] <= hi]
        assert got, key
        items = []
        for f in got:
            it = {"id": "wa-%d-%s" % (f["year"], slug(f["t"])),
                  "t": f["t"], "n": str(f["year"]),
                  "w": round(f["runtime"] / 60.0, 2)}
            if f["t"] in NOTES:
                it["note"] = NOTES[f["t"]]
            items.append(it)
        sec = {"id": key, "title": title,
               "sub": "%d–%d · %d films · %d hours"
                      % (got[0]["year"], got[-1]["year"], len(got),
                         round(sum(f["runtime"] for f in got) / 60.0)),
               "intro": intro, "items": items}
        if key == "wilson":
            sec["open"] = True
        sections.append(sec)

    placed = sum(len(s["items"]) for s in sections)
    assert placed == len(films), (placed, len(films))
    for s in sections:
        assert all(a["n"] < b["n"] for a, b in zip(s["items"], s["items"][1:])), \
            "%s is out of year order" % s["title"]
    noted = {x["t"] for s in sections for x in s["items"] if x.get("note")}
    assert noted == set(NOTES), (sorted(noted), sorted(NOTES))
    # nothing unweighted anywhere: an item with no `w` in a weighted list is
    # silently worth one hour, and this list is weighted
    assert all(isinstance(x.get("w"), float) and x["w"] > 0
               for s in sections for x in s["items"]), \
        [x["id"] for s in sections for x in s["items"] if not x.get("w")]

    hours = sum(x["w"] for s in sections for x in s["items"])
    mins = sum(f["runtime"] for f in films)
    assert abs(hours - mins / 60.0) < 0.1, (hours, mins / 60.0)

    p = {
        "slug": SLUG,
        "title": "Wes Anderson",
        "subtitle": "the directed features",
        "kind": "films",
        "popularity": 68,
        # Not a story, so not a sequence: the order these came out in
        # is a fact about the maker, not an instruction to the viewer
        # (Nathan, CLU-372). Prerequisites, where any exist, live in
        # tools/data/sequences.json and are enforced separately.
        "random": True,
        "year": "1996–2025",
        "blurb": "Thirteen features in release order, Bottle Rocket to The "
                 "Phoenician Scheme — about %d hours." % round(hours),
        "unit": {"one": "film", "many": "films"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        # measured against every accent in properties/index.json — see
        # scratch/wesanderson/accent.py. The famous picks are all spoken for:
        # his khaki-yellow lands 1.9 from Pixar's, the deep Budapest pink 3.6
        # from Gossip Girl's, the Darjeeling mustard 6.5 from Castlevania's.
        # This is the pink family's free corner, 17.3 CIE76 from its nearest
        # neighbour (Kurosawa's dark) against 18.0 for the freest pair on the
        # whole wheel — the sun-bleached register of his palette, not the
        # candy one.
        "accent": "#9F6066",
        "accentDark": "#C69FA3",
        "tiers": False,
        "notes": [
            ["Thirteen features, and one of them is a compilation.",
             "The Wonderful Story of Henry Sugar and Three More is the four "
             "Roald Dahl shorts he made for Netflix in 2023, put out together "
             "as one film in 2024. The filmography lists it among the "
             "features, so it is here among the features."],
            ["No shorts section, and here is the arithmetic.",
             "Three of the ten shorts in the filmography's own table cannot "
             "be weighted from the one runtime source — Do You Like to Read? "
             "and Asteroid City: Location Featurette have no Wikidata item, "
             "and Castello Cavalcanti's carries no runtime — and an "
             "unweighted row in a weighted list is silently counted as an "
             "hour. Four of the seven that can be weighted are the Dahl "
             "quartet, already here as the 2024 feature, so listing them "
             "again would count the same 88 minutes twice. That leaves Hotel "
             "Chevalier, the 1993 Bottle Rocket short and Cousin Ben Troop "
             "Screening: three of ten, which is a subset rather than the "
             "shorts."],
            ["Directing only.",
             "The Squid and the Whale, which he produced, and She's Funny "
             "That Way, Escapes and Uncropped, which he executive produced, "
             "are other people's films. So are the commercials — American "
             "Express, Softbank, Stella Artois, Sony Xperia, Prada, H&M and "
             "two for Montblanc — and the one music video."],
            ["Bar widths are runtimes.",
             "From Wikidata's P2047 for all thirteen, in hours, each gated on "
             "a release year within a year of the filmography's. The 2024 "
             "compilation has no runtime of its own and takes the sum of the "
             "four parts its own Wikidata item names. The Phoenician "
             "Scheme's item carries a deprecated 120 beside a live 105; "
             "deprecated is the source saying the value is wrong, so 105 is "
             "what ships."],
            "Filmography from Wikipedia's Wes Anderson filmography, read from "
            "the table itself; runtimes from Wikidata.",
        ],
        "sections": sections,
    }

    out = prop.write(p)
    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == 13, len(ids)
    print("wrote %s — %d films, %d minutes, %.2f hours"
          % (out.name, len(ids), mins, hours))
    for s in sections:
        print("   %-38s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
