#!/usr/bin/env python3
"""Generate properties/ace-attorney.json.

    python3 tools/make_ace-attorney.py

Every Ace Attorney worth objecting to: the six mainline games, the
Investigations duology, and the Great Ace Attorney duology — grouped by
the four collections Capcom actually sells them in, release order within
each.

Which games exist and their release years come from Wikipedia's Ace
Attorney article and its game timeline
(scratch/agent-games1/wiki/ace-attorney.wiki); years shown are the
original Japanese releases, since several games reached the west only
years later inside a collection. Hours are HowLongToBeat main-story
figures — story only, the house standard, and in this series the story is
the whole game — read from tools/data/ace-attorney.json, collected by
scratch/agent-games1/fetch_hltb.py and verified by name (this generator
refuses a record whose name is not what it expects, and cross-checks
HLTB's release year against Wikipedia's — HLTB dates every entry to the
Japanese original, including Prosecutor's Gambit at 2011).

The collections' names are stated as fact: Phoenix Wright: Ace Attorney
Trilogy, Apollo Justice: Ace Attorney Trilogy, Ace Attorney
Investigations Collection — which gave Investigations 2 its official
English name, Prosecutor's Gambit — and The Great Ace Attorney
Chronicles. The Professor Layton crossover is not a row.
"""
import json
import pathlib

SLUG = "ace-attorney"

# key in the data file, display title, Wikipedia (JP) year, note
WRIGHT = [
    ("aa1", "Phoenix Wright: Ace Attorney", 2001,
     "GBA in Japan, DS in the west — the turnabouts start here"),
    ("aa2", "Phoenix Wright: Ace Attorney – Justice for All", 2002,
     "The rough middle child, redeemed by its final case"),
    ("aa3", "Phoenix Wright: Ace Attorney – Trials and Tribulations", 2004,
     "The trilogy's payoff — every thread lands"),
]

APOLLO = [
    ("apollo", "Apollo Justice: Ace Attorney", 2007,
     "New lead, new courtroom, and a very different Phoenix"),
    ("dual-destinies", "Phoenix Wright: Ace Attorney – Dual Destinies", 2013,
     "The 3DS return; Athena joins the office"),
    ("spirit", "Phoenix Wright: Ace Attorney – Spirit of Justice", 2016,
     "Split between Khura'in and home — séance trials included"),
]

INVESTIGATIONS = [
    ("aai", "Ace Attorney Investigations: Miles Edgeworth", 2009,
     "Edgeworth investigates the scenes himself — logic, not "
     "cross-examination"),
    ("aai2", "Ace Attorney Investigations 2: Prosecutor's Gambit", 2011,
     "Japan-only for thirteen years and widely called the series' best "
     "writing; the 2024 Collection finally brought it west"),
]

GREAT = [
    ("gaa1", "The Great Ace Attorney: Adventures", 2015,
     "Meiji-era Japan and Victorian London; Ryunosuke, ancestor of "
     "Phoenix"),
    ("gaa2", "The Great Ace Attorney 2: Resolve", 2017,
     "The direct conclusion — the duology is one long story"),
]

SECTIONS = [
    ("wright", "The Phoenix Wright trilogy",
     "The original three, sold together as Phoenix Wright: Ace Attorney "
     "Trilogy.", WRIGHT),
    ("apollo", "The Apollo Justice trilogy",
     "Games four to six, collected in 2024 as Apollo Justice: Ace "
     "Attorney Trilogy.", APOLLO),
    ("investigations", "The Investigations duology",
     "Edgeworth's spin-off pair, collected in 2024 as Ace Attorney "
     "Investigations Collection.", INVESTIGATIONS),
    ("great", "The Great Ace Attorney",
     "The period duology, west since 2021 as The Great Ace Attorney "
     "Chronicles.", GREAT),
]


def norm(s):
    s = (s or "").replace("’", "'").replace("–", "-")
    return " ".join(s.casefold().split())


def main():
    data = json.loads((pathlib.Path(__file__).resolve().parent / "data"
                       / "ace-attorney.json").read_text(encoding="utf-8"))

    sections = []
    for sec_id, sec_title, intro, roster in SECTIONS:
        years = [y for _, _, y, _ in roster]
        assert years == sorted(years), "%s roster out of release order" % sec_id
        items = []
        for key, title, year, note in roster:
            rec = data.get(key)
            assert rec, "no HLTB record for %s" % key
            assert norm(rec["name"]) == norm(title), \
                "record mismatch for %s: %r" % (key, rec["name"])
            assert abs(int(rec["year"]) - year) <= 1, \
                "year mismatch for %s: wiki %d, hltb %s" % (key, year, rec["year"])
            x = {"id": "aa-%s" % key, "t": title, "n": str(year),
                 "w": rec["main_h"]}
            if note:
                x["note"] = note
            items.append(x)
        hours = sum(x["w"] for x in items)
        sections.append({
            "id": sec_id, "title": sec_title,
            "sub": "%d–%d · %d games · %d hours story"
                   % (years[0], years[-1], len(items), round(hours)),
            "intro": intro,
            "items": items,
        })
    sections[0]["open"] = True

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert len(ids) == sum(len(r) for _, _, _, r in SECTIONS) == 10, (len(ids),)

    hours = sum(x["w"] for s in sections for x in s["items"])

    prop = {
        "slug": SLUG,
        "title": "Ace Attorney",
        "subtitle": "mainline, Investigations, and the Great duology",
        "kind": "games",
        "order": 95,
        "year": "2001–",
        "blurb": "%d games of courtroom drama — about %d hours of story, "
                 "which is the appeal." % (len(ids), round(hours)),
        "unit": {"one": "game", "many": "games"},
        "verb": {"base": "play", "past": "played", "ing": "playing"},
        "itemOrder": "number-first",
        "accent": "#263C6B",
        "accentDark": "#F4764B",
        "tiers": False,
        "notes": [
            ["Long is the point.", "These are visual novels in a "
             "courtroom; thirty-hour games are normal here and the hours "
             "are all story. The count is honest — pace accordingly."],
            ["Four boxes, one order.", "The sections mirror the "
             "collections Capcom sells: the Phoenix Wright trilogy, the "
             "Apollo Justice trilogy, the Investigations Collection and "
             "the Great Ace Attorney Chronicles. Years shown are the "
             "original Japanese releases. Start with the first trilogy; "
             "the Great duology stands alone if you want a second door."],
            ["Prosecutor's Gambit, factually.", "Investigations 2 shipped "
             "in Japan in 2011 and reached the west only in the 2024 "
             "Investigations Collection, retitled Prosecutor's Gambit — "
             "that official English name is the one on the row."],
            ["Not a row.", "Professor Layton vs. Phoenix Wright is a "
             "crossover with its own fandom and no bearing on the "
             "series' story."],
            "Game list and years from Wikipedia's Ace Attorney article; "
            "hours from HowLongToBeat main-story figures, verified by "
            "name.",
        ],
        "sections": sections,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json" % SLUG)
    print("  %d sections, %d games, %d hours story"
          % (len(sections), len(ids), round(hours)))
    for s in sections:
        print("   %-28s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
