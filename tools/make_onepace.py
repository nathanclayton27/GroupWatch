#!/usr/bin/env python3
"""Generate properties/one-pace.json — the One Pace recut.

    python3 tools/make_onepace.py

One Pace is a fan project that re-edits the One Piece anime down to the manga's
pacing: filler cut, padding removed. Arc names, order, the manga chapters each covers and the anime episodes each
replaces come from the official watch page at https://onepace.net/en/watch —
read out of the timeline data the page itself ships, so this is what One Pace
says rather than someone's summary of it.

The one thing that page does not publish is a per-arc episode COUNT. Those come
from a community mirror, positionally matched against the official arc order,
which agrees exactly at 36 arcs. Where a second source quoted a number it
matched: Enies Lobby 25, Marineford 17, Dressrosa 48, Whole Cake 39.

Each arc numbers its episodes from 1, as the releases do, so there is no
continuous episode number to track.

Two "special" segments are left out — the One Piece Fan Letter tie-in and an
April Fools release — since neither is part of the run. Egghead is still being
released and its count will grow.
"""
import json
import pathlib

SLUG = "one-pace"


ARCS = [
    ('Romance Dawn', '1-7', '1-3, 19, 312, Episode of East Blue', 4),
    ('Orange Town', '8-21', '4-8', 3),
    ('Syrup Village', '23-41', '9-18', 6),
    ('Gaimon', '42,22', '18', 1),
    ('Baratie', '42-68', '19-30', 9),
    ('Arlong Park', '69-95', '31-44', 10),
    ("The Adventures of Buggy's Crew", '35-75 cover stories', '46-47', 1),
    ('Loguetown', '96-100', '45, 48-49, 51-53', 3),
    ('Reverse Mountain', '101-105', '54-55, 61-63', 2),
    ('Whisky Peak', '106-114', '64-67', 2),
    ('The Trials of Koby-Meppo', '83-119 cover stories', '68-69', 1),
    ('Little Garden', '115-129', '70-77', 5),
    ('Drum Island', '130-154', '78-91', 8),
    ('Alabasta', '155-217', '92-130', 21),
    ('Jaya', '218-236', '144-152', 8),
    ('Skypiea', '237-303', '153-195, 203, 207, 225', 16),
    ('Long Ring Long Land', '304-321', '207-228', 6),
    ('Water Seven', '322-374', '229-263', 20),
    ('Enies Lobby', '375-430', '264-312', 25),
    ('Post-Enies Lobby', '431-441', '313-325', 5),
    ('Thriller Bark', '442-489', '337-381', 22),
    ('Sabaody Archipelago', '490-513', '385-405', 11),
    ('Amazon Lily', '514-524', '408-421', 5),
    ('Impel Down', '525-548', '422-452', 10),
    ('If You Could Go Anywhere... The Adventures of the Straw Hats', '543-560 cover stories', '453-456', 1),
    ('Marineford', '549-580', '457-489', 17),
    ('Post-War', '581-597', '490-516', 8),
    ('Return to Sabaody', '598-602', '517-522', 3),
    ('Fishman Island', '603-653', '523-574', 24),
    ('Punk Hazard', '654-699', '579-625', 22),
    ('Dressrosa', '700-800', '629-746', 48),
    ('Zou', '801-822', '746-747, 751-776', 10),
    ('Whole Cake Island', '823-902', '777-877', 39),
    ('Reverie', '903-908', '878-889', 3),
    ('Wano', '909-1057', '890-894, 897-1028, 1031-1083, 1085', 43),
    ('Egghead', '1058-1125', '1086-', 13),
]

MOVING = {"Egghead"}

# Three arcs took their official names after ids had already shipped. Item ids
# are what progress is stored against, so those keep the slug they were first
# published with — the title on screen changes, the key underneath does not.
ID_ALIAS = {
    "Whisky Peak": "whiskey-peak",
    "Alabasta": "arabasta",
    "If You Could Go Anywhere... The Adventures of the Straw Hats":
        "the-adventures-of-the-straw-hat-pirates",
}


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
    for arc, chapters, anime, n in ARCS:
        sid = ID_ALIAS.get(arc, slugify(arc))
        bits = []
        if chapters: bits.append("chapters " + chapters)
        if anime:    bits.append("anime " + anime)
        bits.append("%d episode%s" % (n, "" if n == 1 else "s"))
        if arc in MOVING: bits.append("still releasing")
        sections.append({
            "id": "a-" + sid,
            "title": arc,
            "sub": " · ".join(bits),
            "items": [
                {"id": "onepace-%s-%d" % (sid, i), "t": "Episode", "n": str(i)}
                for i in range(1, n + 1)
            ],
        })

    ids = [x["id"] for s in sections for x in s["items"]]
    total = len(ids)
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate item ids")
    if len(sections) != 36:
        raise SystemExit("expected 36 arcs, built %d" % len(sections))

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
            ["Source.", "Arc order, names, the manga chapters each covers and the "
                        "anime episodes each replaces are read from the official "
                        "watch page at onepace.net. Egghead is still being released "
                        "and its count will grow."],
        ],
        "sections": sections,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json" % SLUG)
    print("  %d arcs, %d episodes" % (len(sections), total))
    for s in sections[:3]:
        print("   %-20s %s" % (s["title"][:20], s["sub"]))


if __name__ == "__main__":
    main()
