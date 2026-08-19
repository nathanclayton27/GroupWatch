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

# The three broadcast cours, each split in half, so a section is about a week's
# watching rather than a month's.
PARTS = [
    ("p1a", "Part 1 · first half",   1, 13),
    ("p1b", "Part 1 · second half", 14, 25),
    ("p2a", "Part 2 · first half",  26, 38),
    ("p2b", "Part 2 · second half", 39, 50),
    ("p3a", "Part 3 · first half",  51, 62),
    ("p3b", "Part 3 · second half", 63, 74),
]

# One week per section, with no dates of its own — a group says when it starts.


def main():
    sections, windows = [], []
    for i, (pid, title, first, last) in enumerate(PARTS):
        sections.append({
            "id": pid,
            "title": title,
            "sub": "episodes %d–%d · week %d" % (first, last, i + 1),
            "items": [
                {"id": "monster-%d" % n, "t": TITLES[n - 1], "n": str(n)}
                for n in range(first, last + 1)
            ],
        })
        windows.append({
            "offset": i * 7,          # days from whenever the group starts
            "days": 7,
            "through": last,          # cumulative episodes due by the end of the week
            "label": title,
        })

    ids = [x["id"] for s in sections for x in s["items"]]
    total = len(ids)
    assert len(ids) == len(set(ids)), "duplicate item ids"
    assert total == 74, "expected 74 episodes, built %d" % total
    thr = [w["through"] for w in windows]
    assert thr == sorted(thr) and thr[-1] == 74, "window targets are wrong"

    prop = {
        "slug": SLUG,
        "title": "Monster",
        "subtitle": "Naoki Urasawa",
        "kind": "anime",
        "order": 6,
        "year": "2004–2005",
        "blurb": "74 episodes, no filler, watch it in order.",
        "schedule": {"kind": "windows", "windows": windows},
        "unit": {"one": "episode", "many": "episodes"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": "#6B6F7A",
        "accentDark": "#A8ADB8",
        "tiers": False,
        "notes": [
            ["The schedule.", "Six weeks, half a broadcast cour each. It has no "
                              "dates until a group sets a start; until then nobody "
                              "is behind."],
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
    for s, w in zip(sections, windows):
        print("   %-22s %2d  through E%-2d by day %d"
              % (s["title"], len(s["items"]), w["through"], w["offset"] + w["days"]))


if __name__ == "__main__":
    main()
