#!/usr/bin/env python3
"""Generate properties/one-pace.json — the One Pace recut.

    python3 tools/make_onepace.py

One Pace is a fan project that re-edits the One Piece anime down to the manga's
pacing: filler cut, padding removed. Arc names and episode counts from the One
Pace release list, cross-checked against a second source where both quote a
number — Enies Lobby 25, Marineford 17, Dressrosa 48 and Whole Cake 39 agree.

Each arc numbers its own episodes from 1, which is how One Pace releases them,
so there is no continuous episode number to track.

Sources disagree on Wano and Egghead, which are the arcs still being released.
Those two counts will move; the rest are settled.
"""
import json
import pathlib

SLUG = "one-pace"

# arc, One Pace episode count
ARCS = [
    ("Romance Dawn", 4),
    ("Orange Town", 3),
    ("Syrup Village", 6),
    ("Gaimon", 1),
    ("Baratie", 9),
    ("Arlong Park", 10),
    ("The Adventures of Buggy's Crew", 1),
    ("Loguetown", 3),
    ("Reverse Mountain", 2),
    ("Whiskey Peak", 2),
    ("The Trials of Koby-Meppo", 1),
    ("Little Garden", 5),
    ("Drum Island", 8),
    ("Arabasta", 21),
    ("Jaya", 8),
    ("Skypiea", 16),
    ("Long Ring Long Land", 6),
    ("Water Seven", 20),
    ("Enies Lobby", 25),
    ("Post-Enies Lobby", 5),
    ("Thriller Bark", 22),
    ("Sabaody Archipelago", 11),
    ("Amazon Lily", 5),
    ("Impel Down", 10),
    ("The Adventures of the Straw Hat Pirates", 1),
    ("Marineford", 17),
    ("Post-War", 8),
    ("Return to Sabaody", 3),
    ("Fishman Island", 24),
    ("Punk Hazard", 22),
    ("Dressrosa", 48),
    ("Zou", 10),
    ("Whole Cake Island", 39),
    ("Reverie", 3),
    ("Wano", 43),
    ("Egghead", 13),
]

MOVING = {"Wano", "Egghead"}


def slugify(name):
    out = []
    for ch in name.lower():
        if ch.isalnum():
            out.append(ch)
        elif out and out[-1] != "-":
            out.append("-")
    return "".join(out).strip("-")


def main():
    sections = []
    for arc, n in ARCS:
        sid = slugify(arc)
        sections.append({
            "id": "a-" + sid,
            "title": arc,
            "sub": "%d episode%s%s" % (n, "" if n == 1 else "s",
                                       " · still releasing" if arc in MOVING else ""),
            "items": [
                {"id": "onepace-%s-%d" % (sid, i), "t": "Episode", "n": str(i)}
                for i in range(1, n + 1)
            ],
        })

    ids = [x["id"] for s in sections for x in s["items"]]
    total = len(ids)
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate item ids")
    if total != sum(n for _, n in ARCS):
        raise SystemExit("episode count mismatch")

    prop = {
        "slug": SLUG,
        "title": "One Pace",
        "subtitle": "One Piece at the manga's pacing",
        "kind": "anime",
        "order": 6,
        "year": "fan recut",
        "blurb": "%d episodes, %d arcs, no filler and no padding." % (total, len(ARCS)),
        "unit": {"one": "episode", "many": "episodes"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": "#2E7A6B",
        "accentDark": "#5FBFA8",
        "tiers": False,
        "notes": [
            ["What this is.", "A fan re-edit of the One Piece anime cut down to the "
                              "manga's pacing — filler removed, padding trimmed. The "
                              "same story as the One Piece tracker here, in roughly a "
                              "third of the runtime."],
            ["Numbering.", "One Pace numbers each arc from 1 rather than running a "
                           "continuous count, so the episode numbers here restart in "
                           "every section, exactly as the releases do."],
            ["Wano and Egghead are still being released.", "Their counts will grow, "
                                                           "and sources disagree on "
                                                           "them today. Everything "
                                                           "before them is settled."],
        ],
        "sections": sections,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json" % SLUG)
    print("  %d arcs, %d episodes" % (len(sections), total))
    print("  longest: %s" % max(ARCS, key=lambda a: a[1])[0])


if __name__ == "__main__":
    main()
