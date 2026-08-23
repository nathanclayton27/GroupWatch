#!/usr/bin/env python3
"""Generate properties/persona.json.

    python tools/make_persona.py

Mainline Persona in release order: the PS1 original, the Persona 2 duology,
and the modern trilogy, with Persona 3 Reload as its own optional row
because HowLongToBeat splits it (it is a ground-up remake, not an edition).
Spin-offs — the fighting games, rhythm games, Q and Strikers — are cut, and
the cut is noted.

The game list, years and edition facts were machine-read from Wikipedia's
Persona (series) article (scratch/agent-games2/verify_wiki.py). Hours are
HowLongToBeat main-story figures — story only, the house standard — read
from tools/data/persona.json, collected by
scratch/agent-games2/fetch_hltb.py and verified by name and year there;
this generator refuses a record whose name is not what it expects.

Display years are first-release (Japanese) years — the order the series
came out in. Two rows tolerate a later HLTB year on purpose: Innocent Sin
only reached the west as the 2011 PSP release, and HLTB stamps some entries
with the western year.

Tiers:
  1  the modern trilogy — 3, 4, 5, what everyone means by "Persona"
  2  the PS1 classics — the original and the Persona 2 duology
  3  the Reload retelling — same story as Persona 3, tick one
"""
import json
import pathlib

SLUG = "persona"

# id, data key, expected HLTB names, display title, display year,
# acceptable HLTB years, section, tier, note, opt
ROSTER = [
    ("per-1", "p1", ["Revelations: Persona", "Shin Megami Tensei: Persona"],
     "Revelations: Persona", 1996, (1996, 2009), "ps1", 2,
     "The PS1 original. The 2009 PSP remake is the usual way to play it "
     "now — either edition ticks this row.", 0),
    ("per-2is", "p2is", ["Persona 2: Innocent Sin",
                         "Shin Megami Tensei: Persona 2 - Innocent Sin"],
     "Persona 2: Innocent Sin", 1999, (1999, 2011), "ps1", 2,
     "First half of the duology — Japan-only until the 2011 PSP release",
     0),
    ("per-2ep", "p2ep", ["Persona 2: Eternal Punishment",
                         "Shin Megami Tensei: Persona 2 - Eternal Punishment"],
     "Persona 2: Eternal Punishment", 2000, (2000, 2000), "ps1", 2,
     "The direct conclusion — the duology is one story in two games", 0),
    ("per-3", "p3", ["Persona 3", "Shin Megami Tensei: Persona 3"],
     "Persona 3", 2006, (2006, 2007), "calendar", 1,
     "The calendar reinvention. FES (2008) and Portable (2010) are its "
     "expanded editions — any of the three ticks this row; Reload, the "
     "2024 remake, has its own row below.", 0),
    ("per-4", "p4", ["Persona 4", "Shin Megami Tensei: Persona 4"],
     "Persona 4", 2008, (2008, 2008), "calendar", 1,
     "Golden (2012) is its expanded edition and the usual pick — either "
     "ticks this row", 0),
    ("per-5", "p5", ["Persona 5"], "Persona 5", 2016, (2016, 2017),
     "phantom", 1,
     "Royal (2019) is its expanded edition and the usual pick — either "
     "ticks this row", 0),
    ("per-3r", "p3r", ["Persona 3 Reload"], "Persona 3 Reload", 2024,
     (2024, 2024), "phantom", 3,
     "The ground-up remake of Persona 3 — same story, modern build. Play "
     "this or the original, not both.", 1),
]

SECTIONS = [
    ("ps1", "The PS1 years",
     "Before the social links — the original and the two-part sequel, "
     "darker and stranger than what followed."),
    ("calendar", "The calendar reinvention",
     "A school year, a dungeon, and a deadline — the structure the series "
     "is famous for arrives."),
    ("phantom", "Phantom Thieves and after",
     "The biggest one, and the remake that brought Persona 3 up to its "
     "standard."),
]


def norm(s):
    s = (s or "").replace("’", "'").replace("–", "-").replace("—", "-")
    return " ".join(s.casefold().split())


def main():
    data = json.loads((pathlib.Path(__file__).resolve().parent / "data"
                       / "persona.json").read_text(encoding="utf-8"))

    rows = {}
    used = set()
    for iid, key, expects, title, year, ok_years, sec, tier, note, opt in ROSTER:
        rec = data.get(key)
        assert rec, "no HLTB record for %s" % key
        assert norm(rec["name"]) in {norm(e) for e in expects}, \
            "record mismatch for %s: %r" % (key, rec["name"])
        assert ok_years[0] <= int(rec["year"]) <= ok_years[1], \
            "year mismatch for %s: hltb %s" % (key, rec["year"])
        used.add(key)
        w = rec["main_h"] if rec["main_h"] else 0
        assert w > 0, "persona rows all need hours (%s)" % key
        x = {"id": iid, "t": title, "n": str(year), "w": w, "tier": tier,
             "sec": sec, "year": year}
        if note:
            x["note"] = note
        if opt:
            x["opt"] = 1
        rows.setdefault(sec, []).append(x)
    assert used == set(data), "cache keys unused: %r" % (set(data) - used)

    sections = []
    for key, title, intro in SECTIONS:
        got = rows[key]
        assert got == sorted(got, key=lambda e: e["year"]), key
        hours = sum(e["w"] for e in got)
        sec = {"id": key, "title": title,
               "sub": "%d–%d · %d games · %d hours story"
                      % (got[0]["year"], got[-1]["year"], len(got),
                         round(hours)),
               "intro": intro,
               "items": [{k: v for k, v in e.items()
                          if k in ("id", "t", "n", "w", "tier", "opt", "note")}
                         for e in got]}
        if key == "ps1":
            sec["open"] = True
        sections.append(sec)

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert len(ids) == len(ROSTER) == 7, (len(ids),)
    tiers = {t: [x for s in sections for x in s["items"] if x["tier"] == t]
             for t in (1, 2, 3)}
    assert len(tiers[1]) == 3, "trilogy should be 3, got %d" % len(tiers[1])
    assert len(tiers[2]) == 3, "classics should be 3, got %d" % len(tiers[2])
    assert len(tiers[3]) == 1, "retellings should be 1, got %d" % len(tiers[3])

    hours = sum(x["w"] for s in sections for x in s["items"])
    trilogy = sum(x["w"] for x in tiers[1])

    prop = {
        "slug": SLUG,
        "title": "Persona",
        "subtitle": "the mainline RPGs in release order, spin-offs cut",
        "kind": "games",
        "order": 98,
        "year": "1996–",
        "blurb": "7 games and about %d hours of story — these are 60-to-"
                 "100-hour RPGs, and that total is not a typo. The modern "
                 "trilogy alone is %d." % (round(hours), round(trilogy)),
        "unit": {"one": "game", "many": "games"},
        "verb": {"base": "play", "past": "played", "ing": "playing"},
        "itemOrder": "number-first",
        "accent": "#2D3C93",
        "accentDark": "#EF4B5E",
        "tiers": True,
        "itemTiers": True,
        "paceTiers": [1, 2],
        "paceLabel": "the Reload retelling",
        "notes": [
            ["Mainline only.", "The numbered RPGs, nothing else. The "
             "fighting games (Arena, Ultimax), the rhythm games, Persona Q "
             "and the Strikers sequels are real games and real spin-offs — "
             "cut here because this list is the story spine, and every one "
             "of them assumes you have played it already."],
            ["Editions are notes, not rows.", "FES, Portable, Golden and "
             "Royal are expanded editions of games already listed — play "
             "whichever and tick the one row. Persona 3 Reload is the "
             "exception: a ground-up remake that HowLongToBeat tracks as "
             "its own game, so it gets its own optional row. It is the "
             "same story as Persona 3 — tick one, not both."],
            ["Budget honestly.", "Nothing here is under 25 hours and the "
             "modern trilogy averages north of 70 each, before the "
             "expanded editions add more. A finish date covers the "
             "mainline seven; the checkbox adds Reload."],
            ["Hours are story only.", "HowLongToBeat main-story figures — "
             "no side content, no max social links. Royal and Golden run "
             "longer than the base figures shown."],
            "Game list, years and edition facts from Wikipedia's Persona "
            "(series) article; hours from HowLongToBeat main-story "
            "figures, matched by name and year.",
        ],
        "sections": sections,
    }

    out = (pathlib.Path(__file__).resolve().parent.parent / "properties"
           / ("%s.json" % SLUG))
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json" % SLUG)
    print("  %d sections, %d games, %d hours (%d the modern trilogy)"
          % (len(sections), len(ids), round(hours), round(trilogy)))
    for s in sections:
        print("   %-28s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
