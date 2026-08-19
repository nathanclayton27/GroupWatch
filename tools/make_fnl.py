#!/usr/bin/env python3
"""Generate properties/friday-night-lights.json.

    python3 tools/make_fnl.py

Episode titles from the Wikipedia episode list. No schedule — a group sets its
own finish date — and no tiers or section prose: it is one show watched straight
through, and the season sub-lines carry everything worth saying.
"""
import json
import pathlib

SLUG = "friday-night-lights"

SEASONS = [
    (1, 2006, [
        "Pilot", "Eyes Wide Open", "Wind Sprints", "Who's Your Daddy",
        "Git'er Done", "El Accidente", "Homecoming", "Crossing the Line",
        "Full Hearts", "It's Different for Girls", "Nevermind",
        "What to Do While You're Waiting", "Little Girl I Wanna Marry You",
        "Upping the Ante", "Blinders", "Black Eyes and Broken Hearts",
        "I Think We Should Have Sex", "Extended Families",
        "Ch-Ch-Ch-Ch-Changes", "Mud Bowl", "Best Laid Plans", "State",
    ]),
    (2, 2007, [
        "Last Days of Summer", "Bad Ideas", "Are You Ready for Friday Night?",
        "Backfire", "Let's Get It On", "How Did I Get Here", "Pantherama!",
        "Seeing Other People", "The Confession", "There Goes the Neighborhood",
        "Jumping the Gun", "Who Do You Think You Are?", "Humble Pie",
        "Leave No One Behind", "May the Best Man Win",
    ]),
    (3, 2008, [
        "I Knew You When", "Tami Knows Best", "How the Other Half Lives",
        "Hello, Goodbye", "Every Rose Has Its Thorn",
        "It Ain't Easy Being J.D. McCoy", "Keeping Up Appearances",
        "New York, New York", "Game of the Week", "The Giving Tree",
        "A Hard Rain's Gonna Fall", "Underdogs", "Tomorrow Blues",
    ]),
    (4, 2009, [
        "East of Dillon", "After the Fall", "In the Skin of a Lion",
        "A Sort of Homecoming", "The Son", "Stay", "In the Bag", "Toilet Bowl",
        "The Lights in Carroll Park", "I Can't", "Injury List", "Laboring",
        "Thanksgiving",
    ]),
    (5, 2010, [
        "Expectations", "On the Outside Looking In",
        "The Right Hand of the Father", "Keep Looking", "Kingdom", "Swerve",
        "Perfect Record", "Fracture", "Gut Check", "Don't Go", "The March",
        "Texas Whatever", "Always",
    ]),
]


def main():
    sections = []
    for num, year, titles in SEASONS:
        sections.append({
            "id": "s%d" % num,
            "title": "Season %d" % num,
            "sub": "%d episode%s · %d" % (len(titles),
                                          "" if len(titles) == 1 else "s", year),
            "items": [
                {"id": "fnl-s%de%d" % (num, i + 1), "t": t, "n": str(i + 1)}
                for i, t in enumerate(titles)
            ],
        })

    ids = [x["id"] for s in sections for x in s["items"]]
    total = len(ids)
    assert len(ids) == len(set(ids)), "duplicate item ids"
    assert total == 76, "expected 76 episodes, built %d" % total

    prop = {
        "slug": SLUG,
        "title": "Friday Night Lights",
        "subtitle": "Dillon, Texas",
        "kind": "tv",
        "order": 4,
        "year": "2006–2011",
        "blurb": "76 episodes, 5 seasons, the book and movie are optional.",
        "unit": {"one": "episode", "many": "episodes"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": "#2E5C8A",
        "accentDark": "#6FAEDC",
        "tiers": False,
        "notes": [
            "Episode titles from the Wikipedia episode list.",
        ],
        "sections": sections,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json" % SLUG)
    print("  %d seasons, %d episodes" % (len(sections), total))
    for s in sections:
        print("   %-10s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
