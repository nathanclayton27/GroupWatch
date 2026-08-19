#!/usr/bin/env python3
"""Generate properties/evangelion.json.

    python3 tools/make_evangelion.py

Evangelion's problem is not what to watch but in what order, and which of the
several endings count. Tiers do the work: 1 is the spine, 2 is worth the time,
3 is a recap you can skip outright.

Episode titles from the Wikipedia episode list. Watch order compiled from the
several 2026 guides that agree on the shape — series, then End of Evangelion,
then Rebuild in order — and on Death & Rebirth being skippable.

Deliberately not included: EVANGELION 3.0 (-120 min.) is a prequel manga rather
than a film, and the (-46h) disc extra is a bonus video, so neither is part of a
watch order.
"""
import json
import pathlib

SLUG = "evangelion"

NGE = [
    "Angel Attack", "The Beast", "A Transfer", "Hedgehog's Dilemma", "Rei I",
    "Rei II", "A Human Work", "Asuka Strikes!",
    "Both of You, Dance Like You Want to Win!", "Magmadiver",
    "The Day Tokyo-3 Stood Still",
    "She said, “Don't make others suffer for your personal hatred.”",
    "Lilliputian Hitcher", "Weaving a Story",
    "Those women longed for the touch of others' lips, and thus invited their kisses.",
    "Splitting of the Breast", "Fourth Children", "Ambivalence", "Introjection",
    "Weaving a Story 2: oral stage", "He was aware that he was still a child",
    "Don't Be", "Rei III",
    "The Beginning and the End, or “Knockin' on Heaven's Door”",
    "Do you love me?", "Take care of yourself.",
]
assert len(NGE) == 26, len(NGE)


def ep(n, note=""):
    x = {"id": "eva-tv-%d" % n, "t": NGE[n - 1], "n": str(n)}
    if note:
        x["note"] = note
    return x


def film(key, title, year, note="", star=0):
    x = {"id": "eva-" + key, "t": title, "n": year}
    if note:
        x["note"] = note
    if star:
        x["star"] = star
    return x


SECTIONS = [
    {
        "id": "tv", "tier": 1, "title": "Neon Genesis Evangelion",
        "sub": "1995 · episodes 1–24",
        "intro":
            "Start here, and start cold. A teenager is called to a city under "
            "attack and told to pilot something nobody will explain to him. The "
            "series spends twenty-four episodes on the consequences.\n\n"
            "It gets stranger and more interior as it goes, and that is the point "
            "rather than a production accident. Episodes 25 and 26 are held back "
            "into their own section below because there is a decision to make "
            "about them.",
        "items": [ep(n) for n in range(1, 25)],
    },
    {
        "id": "dc", "tier": 2, "title": "Director's Cut, episodes 21–24",
        "sub": "1997 · extended versions of four episodes you have just watched",
        "intro":
            "These four were later reissued with substantial new footage — around "
            "six minutes added to 21, five to 22, two to 23, three to 24. Most "
            "modern releases, including the Netflix run, give you these by "
            "default, in which case you have already seen them and can tick this "
            "section off.\n\n"
            "Worth seeking out if your copy is the broadcast version. Not worth "
            "rewatching the whole run for.",
        "items": [
            {"id": "eva-dc-%d" % n, "t": NGE[n - 1] + " (Director's Cut)",
             "n": str(n), "opt": 1} for n in range(21, 25)
        ],
    },
    {
        "id": "tvend", "tier": 2, "title": "The television ending",
        "sub": "1996 · episodes 25–26",
        "intro":
            "The original ending, made with the budget and the schedule gone. It "
            "abandons the plot almost entirely for something interior and abstract, "
            "and it divided everyone at the time.\n\n"
            "The End of Evangelion covers the same ground very differently. You do "
            "not need both, and plenty of people watch only the film — but these "
            "two are what the film is answering, and it lands harder if you have "
            "seen them.",
        "items": [ep(25), ep(26)],
    },
    {
        "id": "eoe", "tier": 1, "title": "The End of Evangelion",
        "sub": "1997 · the ending most people mean",
        "intro":
            "A theatrical retelling of the same final events, made after the fact "
            "and with the resources the series never had. Treat it as the "
            "conclusion.\n\n"
            "Watch it after episode 24 at the earliest. Watching it before the "
            "series is finished spoils everything and makes very little sense.",
        "items": [film("eoe", "The End of Evangelion", "1997", "", 2)],
    },
    {
        "id": "dr", "tier": 3, "title": "Death & Rebirth",
        "sub": "1997 · recap · skippable",
        "intro":
            "Two halves: Death is a compilation of the series, Rebirth is the first "
            "twenty-odd minutes of The End of Evangelion. If you have watched the "
            "series and the film, you have seen all of it already.\n\n"
            "Here for completeness. Every guide says skip it and they are right.",
        "items": [film("dr", "Death & Rebirth", "1997", "recap of the series, then "
                       "the opening of End of Evangelion", 0)],
    },
    {
        "id": "rebuild", "tier": 1, "title": "Rebuild of Evangelion",
        "sub": "2007–2021 · four films",
        "intro":
            "A retelling that starts close to the series and diverges further with "
            "each film, ending somewhere the original never went. It is its own "
            "continuity and its own ending.\n\n"
            "Watch it after the original, not instead of it — the first film "
            "assumes very little, but the later ones are in conversation with "
            "material you would not otherwise have seen. The final film is the "
            "conclusion; there is nothing after it.",
        "items": [
            film("r1", "Evangelion: 1.0 You Are (Not) Alone", "2007"),
            film("r2", "Evangelion: 2.0 You Can (Not) Advance", "2009"),
            film("r3", "Evangelion: 3.0 You Can (Not) Redo", "2012"),
            film("r4", "Evangelion: 3.0+1.0 Thrice Upon a Time", "2021",
                 "released as 3.0+1.01; the revision is the one to watch", 2),
        ],
    },
]


def main():
    ids = [x["id"] for s in SECTIONS for x in s["items"]]
    total = len(ids)
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate item ids")

    tiers = {1: 0, 2: 0, 3: 0}
    for s in SECTIONS:
        tiers[s["tier"]] += len(s["items"])

    prop = {
        "slug": SLUG,
        "title": "Evangelion",
        "subtitle": "series, endings and Rebuild",
        "kind": "anime",
        "order": 9,
        "year": "1995–2021",
        "blurb": "%d pieces in the order they work best, with the recap marked "
                 "skippable." % total,
        "unit": {"one": "part", "many": "parts"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": "#6B3FA0",
        "accentDark": "#A98AE0",
        "tiers": True,
        "notes": [
            ["Tiers.", "1 is the spine — the series, The End of Evangelion, and the "
                       "four Rebuild films. 2 is worth the time: the television "
                       "ending and the extended episodes. 3 is Death & Rebirth, "
                       "which is a recap and genuinely skippable."],
            ["The short version.", "Episodes 1–24, then 25–26, then The End of "
                                   "Evangelion, then Rebuild 1.0 through 3.0+1.0. "
                                   "Skip Death & Rebirth."],
            ["Not included.", "EVANGELION 3.0 (-120 min.) is a prequel manga rather "
                              "than a film, and (-46h) is a disc extra. Neither "
                              "belongs in a watch order."],
            "Episode titles from the Wikipedia episode list; order compiled from "
            "the current watch guides, which agree on the shape and on Death & "
            "Rebirth being optional.",
        ],
        "sections": SECTIONS,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json" % SLUG)
    print("  %d sections, %d parts" % (len(SECTIONS), total))
    print("  tier 1: %d   tier 2: %d   tier 3: %d" % (tiers[1], tiers[2], tiers[3]))
    for s in SECTIONS:
        print("   T%d  %-32s %2d%s" % (s["tier"], s["title"][:32], len(s["items"]),
                                       "  (intro)" if s.get("intro") else ""))


if __name__ == "__main__":
    main()
