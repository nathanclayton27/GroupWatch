#!/usr/bin/env python3
"""Generate properties/kubrick.json.

    python3 tools/make_kubrick.py

The thirteen features Stanley Kubrick directed, in release order, weighted by
runtime — plus A.I. Artificial Intelligence as a coda. A.I. is Steven
Spielberg's film, built from Kubrick's long development of the project; it
closes this list by request and also appears on the Spielberg list.

The three early documentary shorts ride along as optional rows. The
filmography table lists a fourth, World Assembly of Youth, with its director
credit marked uncertain ({{yes}}?) and no runtime anywhere; it is left out.

Titles come from Wikipedia's "Stanley Kubrick filmography"; runtimes (P2047)
and release dates (P577) come from Wikidata, via tools/data/kubrick.json.
"""
import json
import pathlib

SLUG = "kubrick"

ERAS = [
    ("newyork", "New York", 1951, 1956,
     "A Look magazine photographer teaching himself to make films: three "
     "documentary shorts, two features financed with money raised from family "
     "and friends, and a first studio picture with producer James B. Harris. "
     "The shorts are optional rows."),
    ("hollywood", "Hollywood", 1957, 1964,
     "Four studio pictures: two produced with Harris, one he was hired onto, "
     "and one made after the partnership ended. Lolita onward was shot in "
     "England, and England is where he stayed."),
    ("england", "England", 1965, 1999,
     "Six films in thirty-one years, made from outside London with the "
     "control he had been working toward, the gaps between them widening "
     "from three years to twelve."),
]

# Row titles the table gives in full
TITLE = {
    "Dr. Strangelove or: How I Learned to Stop Worrying and Love the Bomb":
        "Dr. Strangelove",
}

NOTE = {
    "Fear and Desire":
        "His first feature — disowned by Kubrick, who tried to keep it out "
        "of circulation",
    "Spartacus":
        "A hired job, and the only feature he made without final control",
    "Dr. Strangelove":
        "In full: Dr. Strangelove or: How I Learned to Stop Worrying and "
        "Love the Bomb",
    "Eyes Wide Shut": "Released posthumously",
    "A.I. Artificial Intelligence":
        "Steven Spielberg's film, developed by Kubrick for years and handed "
        "on — here by request; it is on the Spielberg list too",
}


def slug(t):
    keep = "".join(c.lower() if c.isalnum() else "-" for c in t)
    while "--" in keep:
        keep = keep.replace("--", "-")
    return keep.strip("-")


def hrs(m):
    return round(m / 60.0, 2)


def main():
    data = pathlib.Path(__file__).resolve().parent / "data"
    films = json.loads((data / "kubrick.json").read_text(encoding="utf-8"))

    # the table order breaks ties between coarse same-day dates
    films = [(f["released"], i, f) for i, f in enumerate(films)
             if not f.get("director_uncertain")]
    films = [f for _, _, f in sorted(films)]

    features = [f for f in films if f["kind"] == "feature"]
    shorts = [f for f in films if f["kind"] == "short"]
    ai = [f for f in films if f["kind"] == "ai"]
    assert len(features) == 13, [f["title"] for f in features]
    assert len(shorts) == 3, [f["title"] for f in shorts]
    assert len(ai) == 1 and films[-1] is ai[0], "A.I. must close the list"
    assert all(f["runtime"] for f in films), \
        [f["title"] for f in films if not f["runtime"]]

    def item(f):
        t = TITLE.get(f["title"], f["title"])
        it = {"id": "kub-%d-%s" % (f["year"], slug(t)),
              "t": t, "n": str(f["year"]), "w": hrs(f["runtime"])}
        if f["kind"] == "short":
            it["opt"] = 1
            it["note"] = "Documentary short"
        elif t in NOTE:
            it["note"] = NOTE[t]
        return it

    sections = []
    for key, title, lo, hi, intro in ERAS:
        got = [f for f in films if f["kind"] != "ai" and lo <= f["year"] <= hi]
        assert got, title
        nf = sum(1 for f in got if f["kind"] == "feature")
        ns = len(got) - nf
        sub = "%d–%d · %d features" % (got[0]["year"], got[-1]["year"], nf)
        if ns:
            sub += " + %d shorts" % ns
        sub += " · %d hours" % round(sum(f["runtime"] for f in got) / 60.0)
        sec = {"id": key, "title": title, "sub": sub, "intro": intro,
               "items": [item(f) for f in got]}
        if key == "newyork":
            sec["open"] = True
        sections.append(sec)

    a = ai[0]
    sections.append({
        "id": "coda", "title": "Coda", "sub": "2001 · one film, not his",
        "intro": "Kubrick spent years developing A.I. and handed the project "
                 "to Steven Spielberg, who wrote and directed it after "
                 "Kubrick's death. It closes this list by request.",
        "items": [item(a)],
    })

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert len(ids) == len(films) == 17, (len(ids), len(films))
    for s in sections:
        assert all(a["n"] <= b["n"] for a, b in zip(s["items"], s["items"][1:])), \
            "%s is out of year order" % s["title"]

    mins = sum(f["runtime"] for f in films)
    fmins = sum(f["runtime"] for f in features)

    prop = {
        "slug": SLUG,
        "title": "Stanley Kubrick",
        "subtitle": "the thirteen features, plus A.I.",
        "kind": "films",
        "order": 31,
        "year": "1953–2001",
        "blurb": "The thirteen features in release order, the early shorts as "
                 "optional rows, and Spielberg's A.I. as a coda — about %d "
                 "hours." % round(mins / 60.0),
        "unit": {"one": "film", "many": "films"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "accent": "#202830",
        "accentDark": "#B8C4CE",
        "tiers": False,
        "notes": [
            ["A.I. is Spielberg's film.", "Kubrick developed it for years and "
             "handed the project to Steven Spielberg, who wrote and directed "
             "it after Kubrick's death in 1999. It closes this list by "
             "request, and it appears on the Spielberg list as well."],
            ["Fear and Desire is here even though Kubrick disowned it.", "He "
             "thought it amateurish and tried to keep it from being shown. It "
             "is still his first feature, so the list keeps it."],
            ["Bar widths are runtimes.", "From Wikidata, in hours — the "
             "thirteen features alone are about %d of the %d. The generator "
             "refuses to build without a runtime for every row."
             % (round(fmins / 60.0), round(mins / 60.0))],
            "Filmography from Wikipedia's Stanley Kubrick filmography; "
            "runtimes and release dates from Wikidata.",
        ],
        "sections": sections,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json" % SLUG)
    print("  %d rows (%d features, %d optional shorts, A.I.), %.1f hours"
          % (len(films), len(features), len(shorts), mins / 60.0))
    for s in sections:
        print("   %-12s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
