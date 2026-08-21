#!/usr/bin/env python3
"""Generate properties/twin-peaks.json.

    python3 tools/make_twinpeaks.py

Everything Twin Peaks, in the order you experience it: both seasons, Fire Walk
with Me, The Return, and the four books, woven in at the point they are read
rather than parked in their own section — the same rule the comic lists follow
for cross-title chapters.

Episode counts and directors from Wikipedia's List of Twin Peaks episodes and
the season 3 article: 8 + 22 episodes and 18 parts, with David Lynch directing
the pilot, episodes 2, 8, 9, 14 and 29, and all of The Return. The original
run aired without on-screen titles, so rows are numbered the way the show is
actually referred to — Pilot, then Episode 1 to 29, then Part 1 to 18.

Books are marked optional. Nothing here is weighted: an episode, a film and a
novel are not the same size, and pretending to know their hours would be worse
than counting each as one.
"""
import json
import pathlib

SLUG = "twin-peaks"

# overall episode number (pilot = 1) -> directed by David Lynch
LYNCH = {1, 3, 9, 10, 15, 30}


def ep(overall):
    """Row for one original-run episode, named the way the show is cited."""
    label = "Pilot" if overall == 1 else "Episode %d" % (overall - 1)
    x = {"id": "tp-e%d" % overall, "t": "Twin Peaks", "n": label}
    if overall in LYNCH:
        x["note"] = "Directed by David Lynch"
    if overall == 1:
        x["note"] = "Directed by David Lynch · feature length"
    if overall == 30:
        x["note"] = "Directed by David Lynch · the 1991 finale"
    return x


def book(key, title, year, note):
    return {"id": "tp-book-" + key, "t": title, "n": str(year),
            "note": "Book · " + note, "opt": 1}


SECTIONS = [
    {
        "id": "s1", "title": "Season 1", "sub": "1990 · the pilot and seven episodes",
        "open": True,
        "items": [ep(n) for n in range(1, 9)],
    },
    {
        "id": "s2", "title": "Season 2",
        "sub": "1990–91 · 22 episodes · with the two companion books",
        "items": (
            [book("secret-diary", "The Secret Diary of Laura Palmer", 1990,
                  "published between the seasons, by Jennifer Lynch")]
            + [ep(n) for n in range(9, 31)]
            + [book("autobiography",
                    "The Autobiography of F.B.I. Special Agent Dale Cooper", 1991,
                    "published as the season aired, by Scott Frost")]
        ),
    },
    {
        "id": "fwwm", "title": "Fire Walk with Me", "sub": "1992 · the film",
        "items": [
            {"id": "tp-fwwm", "t": "Twin Peaks: Fire Walk with Me", "n": "1992",
             "note": "Directed by David Lynch"},
            {"id": "tp-missing-pieces", "t": "Twin Peaks: The Missing Pieces",
             "n": "2014", "opt": 1,
             "note": "Ninety minutes of the film's deleted scenes, assembled by Lynch"},
        ],
    },
    {
        "id": "return", "title": "The Return",
        "sub": "2017 · 18 parts · a book on either side",
        "items": (
            [book("secret-history", "The Secret History of Twin Peaks", 2016,
                  "by Mark Frost — read before The Return")]
            + [{"id": "tp-p%d" % k, "t": "Twin Peaks: The Return", "n": "Part %d" % k,
                **({"note": "Directed by David Lynch"} if k == 1 else {})}
               for k in range(1, 19)]
            + [book("final-dossier", "Twin Peaks: The Final Dossier", 2017,
                    "by Mark Frost — read after")]
        ),
    },
]


def main():
    ids = [x["id"] for s in SECTIONS for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert len(ids) == 8 + 24 + 2 + 20, len(ids)
    eps = [x for s in SECTIONS for x in s["items"] if x["id"].startswith("tp-e")]
    assert len(eps) == 30, len(eps)
    assert sum(1 for s in SECTIONS for x in s["items"]
               if "Lynch" in (x.get("note") or "")) >= 8

    prop = {
        "slug": SLUG,
        "title": "Twin Peaks",
        "subtitle": "both seasons, the film, The Return, and the books",
        "kind": "tv, film & books",
        "order": 25,
        "year": "1990–2017",
        "blurb": "The whole thing: 30 episodes, Fire Walk with Me, the 18 parts "
                 "of The Return, and the four books woven in where you read them.",
        "unit": {"one": "entry", "many": "entries"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "accent": "#7A1E2E",
        "accentDark": "#E86A7E",
        "tiers": False,
        "notes": [
            ["The books sit where you read them.", "The Secret Diary of Laura "
             "Palmer came out between the seasons and opens Season 2 here; "
             "Cooper's autobiography closes it. The Secret History of Twin Peaks "
             "is read before The Return and The Final Dossier after, so they "
             "bracket it. All four are marked optional — the show stands "
             "without them."],
            ["Nothing is weighted.", "An episode, a film and a novel are not "
             "the same size, and pretending to know their hours would be worse "
             "than counting each as one."],
            ["Working through David Lynch instead?", "His filmography is its "
             "own list, and all of this is one row there — one tick for the "
             "whole town."],
            "Episode counts and directors from Wikipedia. The original run "
            "aired without on-screen titles, so rows are numbered the way the "
            "show is cited: Pilot, Episode 1–29, Part 1–18.",
        ],
        "sections": SECTIONS,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")
    print("wrote %s.json — %d entries" % (SLUG, len(ids)))
    for s in SECTIONS:
        print("   %-18s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
