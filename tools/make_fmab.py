#!/usr/bin/env python3
"""Generate properties/fma-brotherhood.json from the HD DVD Anime Club schedule.

One-off. Kept so the arc boundaries and dates can be corrected in one place and
regenerated, rather than hand-edited across 64 items.

    python3 tools/make_fmab.py
"""
import json
import pathlib

# (section id, title, first episode, last episode, window start, window end)
ARCS = [
    ("ch1-2", "Chapters 1–2: Hunt for the Stone & Shadow of the Homunculi",
     1, 20, "2026-07-15", "2026-07-28"),
    ("ch3", "Chapter 3: Sins of the Father",
     21, 30, "2026-07-29", "2026-08-04"),
    ("ch4", "Chapter 4: The Wall of Briggs",
     31, 43, "2026-08-05", "2026-08-11"),
    ("ch5", "Chapter 5: The Uprising",
     44, 53, "2026-08-12", "2026-08-18"),
    ("ch6", "Chapter 6: The Promised Day",
     54, 64, "2026-08-19", "2026-08-25"),
]

MONTH = {"07": "July", "08": "August"}

# English episode titles, 1-64. Cross-checked between the Wikipedia episode
# list (1-58) and epguides (55-64); the overlap agrees.
TITLES = [
    "Fullmetal Alchemist", "The First Day", "City of Heresy",
    "An Alchemist's Anguish", "Rain of Sorrows", "Road of Hope",
    "Hidden Truths", "The Fifth Laboratory", "Created Feelings",
    "Separate Destinations", "Miracle at Rush Valley", "One is All, All is One",
    "Beasts of Dublith", "Those Who Lurk Underground", "Envoy from the East",
    "Footsteps of a Comrade-in-Arms", "Cold Flame",
    "The Arrogant Palm of a Small Human", "Death of the Undying",
    "Father Before the Grave", "Advance of the Fool", "Backs in the Distance",
    "Girl on the Battlefield", "Inside the Belly", "Doorway of Darkness",
    "Reunion", "Interlude Party", "Father", "Struggle of the Fool",
    "The Ishvalan War of Extermination", "The 520 Cens Promise",
    "The Führer's Son", "The Northern Wall of Briggs", "Ice Queen",
    "The Shape of This Country", "Family Portrait", "The First Homunculus",
    "Conflict at Baschool", "Daydream", "Homunculus (The Dwarf in the Flask)",
    "The Abyss", "Signs of a Counteroffensive", "Bite of the Ant",
    "Revving at Full Throttle", "The Promised Day", "Looming Shadows",
    "Emissary of Darkness", "The Oath in the Tunnel", "Filial Affection",
    "Upheaval in Central", "The Immortal Legion", "Combined Strength",
    "Flame of Vengeance", "Beyond the Inferno", "The Adults' Way of Life",
    "The Return of the Führer", "Eternal Leave", "Sacrifices", "Lost Light",
    "Eye of Heaven, Gateway of Earth", "He Who Would Swallow God",
    "A Fierce Counterattack", "The Other Side of the Gateway", "Journey's End",
]
assert len(TITLES) == 64, "expected 64 titles, have %d" % len(TITLES)


def pretty(d):
    y, m, day = d.split("-")
    return "%s %d" % (MONTH[m], int(day))


def main():
    sections = []
    windows = []

    for sid, title, first, last, start, end in ARCS:
        sections.append({
            "id": sid,
            "title": title,
            "sub": "episodes %d–%d · %s – %s" % (first, last, pretty(start), pretty(end)),
            "window": {"start": start, "end": end},
            "items": [
                {"id": "fmab-%d" % n, "t": TITLES[n - 1], "n": str(n)}
                for n in range(first, last + 1)
            ],
        })
        windows.append({
            "start": start,
            "end": end,
            "through": last,          # cumulative episodes due by end of window
            "label": title,
        })

    total = sum(len(s["items"]) for s in sections)
    assert total == 64, "expected 64 episodes, built %d" % total
    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate item ids"

    prop = {
        "slug": "fma-brotherhood",
        "title": "Fullmetal Alchemist: Brotherhood",
        "kind": "anime",
        "year": "2009–2010",
        "blurb": "HD DVD Anime Club, Round 4. 64 episodes across six arcs, on a "
                 "fixed club schedule from 15 July to 25 August 2026.",
        "unit": {"one": "episode", "many": "episodes"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        # shows read better as "12  One is All, All is One" than the other way
        "itemOrder": "number-first",
        "accent": "#B0472E",
        "tiers": False,
        "rules": [
            "Pace yourself — don't watch a whole arc in one day. The windows are "
            "for flexibility, not permission to binge.",
            "Remember to discuss.",
            "Finish an arc before its window is up and the remaining days are yours "
            "off until the next arc begins.",
            "Don't transmute your mom.",
        ],
        "schedule": {"kind": "windows", "windows": windows},
        "sections": sections,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / "fma-brotherhood.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    # newline="\n" to match .gitattributes; otherwise every rebuild on Windows
    # rewrites all 800 lines as CRLF and the diff is useless
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s" % out.name)
    print("  %d episodes, %d arcs" % (total, len(sections)))
    for w in windows:
        print("  through E%-2d by %s  %s" % (w["through"], w["end"], w["label"]))


if __name__ == "__main__":
    main()
