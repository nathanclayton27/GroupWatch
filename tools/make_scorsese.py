#!/usr/bin/env python3
"""Generate properties/scorsese.json.

    python3 tools/make_scorsese.py

Martin Scorsese's 26 directed features in release order, in five eras, plus
his 13 feature documentaries as an optional section. From Wikipedia's "Martin
Scorsese filmography" (director-credit rows only) with runtimes from Wikidata,
via tools/data/scorsese.json.

Left out, with reasons: Obsessions (writer only), What Happens at Night
(unreleased), Street Scenes (directing credit marked uncredited), Feel Like
Going Home (an episode of the documentary series The Blues), Beatles '64
(producer only), and two television one-offs with no article or runtime
anywhere (New York City... Melting Point, Lady by the Sea). Personality
Crisis: One Night Only stays: the table credits him, a Wikidata film item
exists, but no runtime is on record, so it weighs nothing and says so.
"""
import json
import pathlib

SLUG = "scorsese"

ERAS = [
    ("early", "New York pictures", 1967, 1976,
     "A first feature grown out of his NYU student work, an exploitation "
     "picture for Roger Corman, and then Mean Streets — the film where the "
     "voice arrives. Taxi Driver is where everyone else noticed."),
    ("bruised", "The bruising years", 1977, 1985,
     "A big-studio musical that failed, Raging Bull made out of the "
     "wreckage, and two comedies about humiliation — one on a talk-show "
     "set, one over a single long night in SoHo."),
    ("imperial", "The imperial stretch", 1986, 1999,
     "Eight films: a pool-hall sequel, the most protested picture of the "
     "decade, Goodfellas and Casino, a remade thriller, a costume drama, a "
     "Dalai Lama film, and a dying paramedic."),
    ("dicaprio", "The DiCaprio decade", 2002, 2013,
     "Five films with Leonardo DiCaprio, plus Hugo — and the Oscar finally "
     "arrived with The Departed."),
    ("late", "The late epics", 2016, 2023,
     "Three films about faith, regret and complicity, none of them under "
     "two and a half hours."),
]

# Table notes worth carrying: the co-director credits. Everything else stays
# quiet.
KEEP_NOTE = "Co-directed with"


def slug(t):
    keep = "".join(c.lower() if c.isalnum() else "-" for c in t)
    while "--" in keep:
        keep = keep.replace("--", "-")
    return keep.strip("-")


def hrs(m):
    return round((m or 0) / 60.0, 2)


def item(f):
    bits = []
    note = (f.get("tablenote") or "")
    if KEEP_NOTE in note:
        start = note.index(KEEP_NOTE)
        end = note.find(";", start)
        bits.append(note[start:end if end > -1 else len(note)].rstrip("."))
    if not f.get("runtime"):
        bits.append("No runtime on record — weighs nothing")
    it = {"id": "ms-%d-%s" % (f["year"], slug(f["t"])),
          "t": f["t"], "n": str(f["year"]), "w": hrs(f.get("runtime"))}
    if f["kind"] == "doc":
        it["opt"] = 1
    if bits:
        it["note"] = " · ".join(bits)
    return it


def main():
    data = pathlib.Path(__file__).resolve().parent / "data"
    films = json.loads((data / "scorsese.json").read_text(encoding="utf-8"))
    feats = [f for f in films if f["kind"] == "feature"]
    docs = [f for f in films if f["kind"] == "doc"]
    assert len(feats) == 26, len(feats)
    assert len(docs) == 13, len(docs)
    feats.sort(key=lambda f: (f["year"], f["t"]))
    docs.sort(key=lambda f: (f["year"], f["t"]))
    assert all(f["runtime"] for f in feats), \
        [f["t"] for f in feats if not f["runtime"]]

    sections = []
    for key, title, lo, hi, intro in ERAS:
        got = [f for f in feats if lo <= f["year"] <= hi]
        assert got, title
        items = [item(f) for f in got]
        sec = {"id": key, "title": title,
               "sub": "%d–%d · %d films · %d hours"
                      % (got[0]["year"], got[-1]["year"], len(got),
                         round(sum(f["runtime"] for f in got) / 60.0)),
               "intro": intro, "items": items}
        if key == "early":
            sec["open"] = True
        sections.append(sec)
    used = sum(len(s["items"]) for s in sections)
    assert used == len(feats), (used, len(feats))

    dh = sum(f.get("runtime") or 0 for f in docs) / 60.0
    sections.append({
        "id": "docs", "title": "The documentaries",
        "sub": "1974–2022 · %d films · %d hours · optional" % (len(docs), round(dh)),
        "intro": "The feature documentaries — concert films, Dylan and "
                 "Harrison portraits, and two long essays on film history. "
                 "All optional rows; watch what pulls you.",
        "items": [item(f) for f in docs],
    })

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert len(ids) == len(films) == 39, (len(ids), len(films))
    for s in sections:
        assert all(a["n"] <= b["n"] for a, b in zip(s["items"], s["items"][1:])), \
            "%s is out of year order" % s["title"]

    hours = sum(x["w"] for s in sections for x in s["items"])

    prop = {
        "slug": SLUG,
        "title": "Martin Scorsese",
        "subtitle": "the directed features, plus the documentaries",
        "kind": "films",
        "order": 56,
        "year": "1967–2023",
        "blurb": "26 features from Who's That Knocking at My Door to Killers "
                 "of the Flower Moon, with the 13 feature documentaries as "
                 "optional rows — about %d hours." % round(hours),
        "unit": {"one": "film", "many": "films"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "accent": "#5E1F38",
        "accentDark": "#D67F92",
        "tiers": False,
        "notes": [
            ["The documentaries are optional.", "Thirteen features he "
             "directed for their own sake — The Last Waltz, No Direction "
             "Home, Shine a Light and the rest. They count toward nothing "
             "unless you tick them."],
            ["What isn't here.", "Obsessions (writer only), the shorts and "
             "television episodes, two television one-offs with no runtime "
             "on record anywhere, and Street Scenes, where his directing "
             "credit is itself uncredited."],
            ["Bar widths are runtimes.", "From Wikidata, in hours. "
             "Personality Crisis: One Night Only has no runtime on record "
             "and weighs nothing rather than a guess."],
            "Filmography from Wikipedia's Martin Scorsese filmography; "
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
