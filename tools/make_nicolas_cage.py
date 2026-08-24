#!/usr/bin/env python3
"""Generate properties/nicolas-cage.json.

    python3 tools/make_nicolas_cage.py

Nicolas Cage's film roles in release order, one row per film, from
Wikipedia's Nicolas Cage filmography film table, runtimes from Wikidata with
the film articles' own infoboxes filling the gaps. Same shape as the Robin
Williams list: era sections, the table's factual notes riding along, weights
in hours.

Out, with reasons: the five producer-only rows (Bel Air, Shadow of the
Vampire, The Life of David Gale, A Thousand Words, Can't Stand Losing You —
no acting role), everything the article marks pending or TBA (Madden, Lords
of War, Beyond the Spider-Verse and three more), and the television and
video-game work.
"""
import json
import pathlib

SLUG = "nicolas-cage"

ERAS = [
    ("coppola", "Nicolas Coppola", 1982, 1989,
     "Billed as Nicolas Coppola in Fast Times, then renamed to escape the "
     "uncle — the decade runs from bit parts through Birdy, Raising "
     "Arizona and Moonstruck to eating a cockroach in Vampire's Kiss."),
    ("leading", "Leading man", 1990, 1996,
     "Wild at Heart to The Rock: the Elvis fixation, the screwball years, "
     "and Leaving Las Vegas — the shoestring drama that won him the "
     "Oscar."),
    ("action", "The action star", 1997, 2004,
     "Con Air, Face/Off, the Bruckheimer money years — with 8MM, Bringing "
     "Out the Dead and Adaptation folded between explosions, and National "
     "Treasure to close."),
    ("excess", "Ghost riders", 2005, 2012,
     "Lord of War through the second Ghost Rider: the era of the burning "
     "skull, the bees, the bad lieutenant, and Kick-Ass — committed to "
     "all of it equally."),
    ("vod", "The video-on-demand years", 2013, 2018,
     "The tax-debt stretch: a dozen thrillers that went straight to "
     "video, with Joe, The Trust and finally Mandy scattered through them "
     "like signal in the noise."),
    ("renaissance", "The renaissance", 2019, 2025,
     "Color Out of Space, Pig, playing himself in The Unbearable Weight "
     "of Massive Talent, Dream Scenario, Longlegs — the comeback that "
     "turned out to be the whole point."),
]

# The table's display text says "Colour"; the film's own article - which
# the same cell links to - is titled Color Out of Space. The article wins.
TITLE = {"Colour Out of Space": "Color Out of Space"}

# Which table notes ride along - factual flags only, same test as the
# Robin Williams list plus this filmography's own recurring markers.
KEYS = ("credited as", "voice", "cameo", "uncredited", "documentary",
        "short film", "television", "direct-to-video", "video on demand",
        "also director")


def slug(t):
    keep = "".join(c.lower() if c.isalnum() else "-" for c in t)
    while "--" in keep:
        keep = keep.replace("--", "-")
    return keep.strip("-")


def main():
    data = pathlib.Path(__file__).resolve().parent / "data"
    films = json.loads((data / "nicolas-cage.json").read_text(encoding="utf-8"))
    assert len(films) == 113, len(films)
    for f in films:
        f["t"] = TITLE.get(f["t"], f["t"])
    films.sort(key=lambda f: (f["year"], f["t"]))
    assert all(f.get("runtime") for f in films), \
        [f["t"] for f in films if not f.get("runtime")]

    sections = []
    for key, title, lo, hi, intro in ERAS:
        got = [f for f in films if lo <= f["year"] <= hi]
        assert got, title
        items = []
        for f in got:
            bits = []
            note = (f.get("tablenote") or "").strip()
            if note and any(k in note.lower() for k in KEYS):
                bits.append(note.rstrip("."))
            it = {"id": "nc-%d-%s" % (f["year"], slug(f["t"])),
                  "t": f["t"], "n": str(f["year"]),
                  "w": round(f["runtime"] / 60.0, 2)}
            if bits:
                it["note"] = " · ".join(bits)
            items.append(it)
        sec = {"id": key, "title": title,
               "sub": "%d–%d · %d films · %d hours"
                      % (got[0]["year"], got[-1]["year"], len(got),
                         round(sum(f["runtime"] for f in got) / 60.0)),
               "intro": intro, "items": items}
        if key == "coppola":
            sec["open"] = True
        sections.append(sec)

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert len(ids) == len(films) == 113, (len(ids), len(films))
    for s in sections:
        assert all(a["n"] <= b["n"] for a, b in zip(s["items"], s["items"][1:])), \
            "%s is out of year order" % s["title"]

    hours = sum(x["w"] for s in sections for x in s["items"])

    prop = {
        "slug": SLUG,
        "title": "Nicolas Cage",
        "subtitle": "the film roles, in release order",
        "kind": "films",
        "popularity": 65,
        "year": "1982–2025",
        "blurb": "%d films across five decades — about %d hours, from "
                 "Nicolas Coppola's bit parts to the renaissance."
                 % (len(films), round(hours)),
        "unit": {"one": "film", "many": "films"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "accent": "#B8860B",
        "accentDark": "#F2B845",
        "tiers": False,
        "notes": [
            ["Acting roles only.", "The five films he only produced, "
             "everything still marked pending or TBA, and the television "
             "and video-game work are not here. The table's own factual "
             "notes — a name change, a voice role, a video-on-demand "
             "release — ride along where they help."],
            ["Bar widths are runtimes.", "From Wikidata for 104 of the "
             "113; the film articles' own infoboxes fill the other "
             "nine."],
            "Filmography from Wikipedia's Nicolas Cage filmography; "
            "runtimes from Wikidata and the film articles' infoboxes.",
        ],
        "sections": sections,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")
    print("wrote %s.json — %d films, %.1f hours" % (SLUG, len(ids), hours))
    for s in sections:
        print("   %-28s %3d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
