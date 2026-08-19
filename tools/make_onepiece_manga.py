#!/usr/bin/env python3
"""Generate properties/one-piece-manga.json.

    python3 tools/make_onepiece_manga.py

Chapters rather than episodes, so this is the one to track if you are reading
ahead of the anime — or instead of it.

Arc chapter boundaries come from the One Pace timeline data, which lists the
manga chapters each arc covers and is the same source the One Pace property
here is built from. Made contiguous: One Pace has a few cover-story segments
that interleave with the main chapters, and every chapter belongs to exactly one
arc in a tracker.

Egghead ending at 1125 and Elbaf opening at 1126 are corroborated separately —
Egghead is widely reported as 68 chapters, and 1058-1125 is 68.

LAST is the newest released chapter. Bump it and rerun.
"""
import json
import pathlib

SLUG = "one-piece-manga"
LAST = 1190          # released 9 August 2026

# saga, arc, first chapter — each arc runs to the chapter before the next starts
ARCS = [
    ("East Blue",       "Romance Dawn",           1),
    ("East Blue",       "Orange Town",            8),
    ("East Blue",       "Syrup Village",         23),
    ("East Blue",       "Baratie",               42),
    ("East Blue",       "Arlong Park",           69),
    ("East Blue",       "Loguetown",             96),

    ("Alabasta",        "Reverse Mountain",     101),
    ("Alabasta",        "Whisky Peak",          106),
    ("Alabasta",        "Little Garden",        115),
    ("Alabasta",        "Drum Island",          130),
    ("Alabasta",        "Alabasta",             155),

    ("Sky Island",      "Jaya",                 218),
    ("Sky Island",      "Skypiea",              237),

    ("Water 7",         "Long Ring Long Land",  304),
    ("Water 7",         "Water Seven",          322),
    ("Water 7",         "Enies Lobby",          375),
    ("Water 7",         "Post-Enies Lobby",     431),

    ("Thriller Bark",   "Thriller Bark",        442),

    ("Summit War",      "Sabaody Archipelago",  490),
    ("Summit War",      "Amazon Lily",          514),
    ("Summit War",      "Impel Down",           525),
    ("Summit War",      "Marineford",           549),
    ("Summit War",      "Post-War",             581),

    ("Fish-Man Island", "Return to Sabaody",    598),
    ("Fish-Man Island", "Fish-Man Island",      603),

    ("Dressrosa",       "Punk Hazard",          654),
    ("Dressrosa",       "Dressrosa",            700),

    ("Whole Cake",      "Zou",                  801),
    ("Whole Cake",      "Whole Cake Island",    823),
    ("Whole Cake",      "Reverie",              903),

    ("Wano Country",    "Wano",                 909),

    ("Final",           "Egghead",             1058),
    ("Final",           "Elbaf",               1126),
]

MOVING = {"Elbaf"}


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
    for i, (saga, arc, first) in enumerate(ARCS):
        last = ARCS[i + 1][2] - 1 if i + 1 < len(ARCS) else LAST
        n = last - first + 1
        if n < 1:
            raise SystemExit("arc %r has no chapters" % arc)
        sections.append({
            "id": "c-" + slugify(arc),
            "title": arc,
            "sub": "%s · chapter%s %d–%d%s"
                   % (saga, "" if n == 1 else "s", first, last,
                      " · still running" if arc in MOVING else ""),
            "items": [
                {"id": "opm-%d" % c, "t": "Chapter", "n": str(c)}
                for c in range(first, last + 1)
            ],
        })

    ids = [x["id"] for s in sections for x in s["items"]]
    total = len(ids)
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate item ids")
    if total != LAST:
        raise SystemExit("expected %d chapters, built %d" % (LAST, total))

    by = {s["title"]: len(s["items"]) for s in sections}
    if by["Egghead"] != 68:
        raise SystemExit("Egghead is %d chapters, expected 68" % by["Egghead"])

    prop = {
        "slug": SLUG,
        "title": "One Piece (manga)",
        "subtitle": "Eiichiro Oda",
        "kind": "manga",
        "order": 7,
        "year": "1997–",
        "blurb": "%d chapters, %d arcs, still running." % (total, len(sections)),
        "unit": {"one": "chapter", "many": "chapters"},
        "verb": {"base": "read", "past": "read", "ing": "reading"},
        "tiers": False,
        "accent": "#A8721F",
        "accentDark": "#E0AE55",
        "notes": [
            ["Ahead of the anime.", "The manga is well past where the anime is. "
                                    "Chapter %d here is roughly a hundred chapters "
                                    "beyond what has been animated." % LAST],
            ["Arc boundaries.", "From the One Pace timeline data, which lists the "
                                "manga chapters each arc covers — the same source the "
                                "One Pace tracker here uses. Made contiguous so every "
                                "chapter belongs to exactly one arc."],
            "Still running. This goes up to chapter %d; rerun the generator to "
            "extend it." % LAST,
        ],
        "sections": sections,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json" % SLUG)
    print("  %d arcs, %d chapters" % (len(sections), total))
    print("  longest: %s (%d)" % max(((s["title"], len(s["items"])) for s in sections),
                                     key=lambda x: x[1])[::1])


if __name__ == "__main__":
    main()
