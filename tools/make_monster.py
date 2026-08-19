#!/usr/bin/env python3
"""Generate properties/monster.json — Monster (2004).

    python3 tools/make_monster.py

74 episodes, one continuous run with no official season split. Titles from the
Wikipedia episode list. Sections are the three broadcast cours, which is the only
division the show actually has — it is one story and nothing here is skippable.
"""
import json
import pathlib

SLUG = "monster"

TITLES = [
    "Herr Dr. Tenma", "Downfall", "Murder Case", "Night of the Execution",
    "The Girl From Heidelberg", "Disappearance Report", "Mansion of Tragedy",
    "The Fugitive", "The Girl and the Seasoned Soldier", "A Past Erased",
    "511 Kinderheim", "A Little Experiment", "Petra and Schumann",
    "The Abandoned Man, The Abandoned Woman", "Be My Baby", "Wolf's Confession",
    "Reunion", "The Fifth Spoonful of Sugar", "The Monster's Abyss",
    "Journey to Freiham", "A Wonderful Holiday", "Lunge's Trap",
    "Eva's Confession", "The Men's Dining Table", "The Thursday Boy",
    "The Secret Woods", "Pieces of Evidence", "Just One Case", "Execution",
    "A Certain Decision", "Under Broad Daylight", "Sanctuary",
    "Scene of a Child", "At the End of the Darkness", "A Hero With No Name",
    "A Monster of Chaos", "A Monster Without a Name", "The Demon in Our Eyes",
    "The Hell in His Eyes", "Grimmer", "The Ghost of 511",
    "The Adventures of the Magnificent Steiner", "Detective Suk",
    "The Two Darkness", "The Afterimage of a Monster", "The Point of Contact",
    "The Door to a Nightmare", "The Most Frightening Thing",
    "The Cruelest Thing", "The Rose Mansion", "A Monster's Love Letter",
    "Lawyer", "Determination", "Escape", "Room Number 402",
    "The Unending Journey", "That Night", "Unwanted Job",
    "The Man Who Saw the Devil", "The Man Who Knew Too Much",
    "The Door of Memory", "A Fun Dining Table", "An Unrelated Murder",
    "The Baby's Depression", "Johan's Footprints", "Welcome Back", "I'm Home",
    "Ruhenheim", "A Peaceful Home", "The Town of Slaughter",
    "The Magnificent Steiner's Rage", "Man Without a Name",
    "The Landscape of the End", "The Real Monster",
]
assert len(TITLES) == 74, "expected 74 titles, have %d" % len(TITLES)

# (section id, title, first, last) — the broadcast cours
PARTS = [
    ("p1", "Part 1", 1, 25),
    ("p2", "Part 2", 26, 50),
    ("p3", "Part 3", 51, 74),
]


def main():
    sections = []
    for pid, title, first, last in PARTS:
        sections.append({
            "id": pid,
            "title": title,
            "sub": "episodes %d–%d" % (first, last),
            "items": [
                {"id": "monster-%d" % n, "t": TITLES[n - 1], "n": str(n)}
                for n in range(first, last + 1)
            ],
        })

    ids = [x["id"] for s in sections for x in s["items"]]
    total = len(ids)
    assert len(ids) == len(set(ids)), "duplicate item ids"
    assert total == 74, "expected 74 episodes, built %d" % total

    prop = {
        "slug": SLUG,
        "title": "Monster",
        "subtitle": "Naoki Urasawa",
        "kind": "anime",
        "order": 6,
        "year": "2004–2005",
        "blurb": "74 episodes, no filler, watch it in order.",
        "unit": {"one": "episode", "many": "episodes"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": "#6B6F7A",
        "accentDark": "#A8ADB8",
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
    print("  %d parts, %d episodes" % (len(sections), total))
    for s in sections:
        print("   %-8s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
