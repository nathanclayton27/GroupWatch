#!/usr/bin/env python3
"""Generate properties/mass-effect.json.

    python tools/make_mass-effect.py

The Shepard trilogy in release order with its major story DLC as optional
rows, then Andromeda, last and standalone. The Legendary Edition — the
usual way in now — is a note, not a row: it is the same three games with
the DLC folded in.

The game list and DLC names were machine-read from Wikipedia (the Mass
Effect franchise article plus the ME2/ME3 articles —
scratch/agent-games2/verify_wiki.py). Hours are HowLongToBeat main-story
figures — story only, the house standard — read from
tools/data/mass-effect.json, collected by
scratch/agent-games2/fetch_hltb.py and verified by name and year there;
this generator refuses a record whose name is not what it expects. Only
DLC that HLTB carries as its own entry with real hours got a row.

Tiers:
  1  the trilogy
  2  the story DLC, each with its own hours
  3  Andromeda
"""
import json
import pathlib

SLUG = "mass-effect"

# id, data key, expected HLTB name, display year, section, tier, note, opt
ROSTER = [
    ("me-1", "me1", "Mass Effect", 2007, "me1", 1,
     "Legendary Edition (2021) remasters all three with the DLC folded in "
     "— the usual way in now, and any edition ticks these rows", 0),
    ("me-1-sky", "me1-bdts", "Mass Effect: Bring Down the Sky", 2008,
     "me1", 2, "The first game's one story DLC — an asteroid, a "
     "deadline", 1),
    ("me-2", "me2", "Mass Effect 2", 2010, "me2", 1, "", 0),
    ("me-2-overlord", "me2-overlord", "Mass Effect 2: Overlord", 2010,
     "me2", 2, "The rogue-VI station", 1),
    ("me-2-broker", "me2-shadow-broker",
     "Mass Effect 2: Lair of the Shadow Broker", 2010, "me2", 2,
     "Liara's chase — the essential one", 1),
    ("me-2-arrival", "me2-arrival", "Mass Effect 2: Arrival", 2011, "me2",
     2, "The bridge into 3 — save it for last before moving on", 1),
    ("me-3", "me3", "Mass Effect 3", 2012, "me3", 1,
     "Every modern edition includes the Extended Cut ending", 0),
    ("me-3-leviathan", "me3-leviathan", "Mass Effect 3: Leviathan", 2012,
     "me3", 2, "Where the Reapers come from", 1),
    ("me-3-omega", "me3-omega", "Mass Effect 3: Omega", 2012, "me3", 2,
     "Aria takes Omega back", 1),
    ("me-3-citadel", "me3-citadel", "Mass Effect 3: Citadel", 2013, "me3",
     2, "The send-off — best saved for just before the finale", 1),
    ("me-andromeda", "andromeda", "Mass Effect: Andromeda", 2017,
     "andromeda", 3,
     "A new galaxy and a new cast — the trilogy's story is complete "
     "without it", 1),
]

SECTIONS = [
    ("me1", "Mass Effect",
     "Where the save file starts — one game, one story DLC."),
    ("me2", "Mass Effect 2",
     "The heist-crew middle chapter, and the DLC era at its best."),
    ("me3", "Mass Effect 3",
     "The finish, with three optional detours worth the time."),
    ("andromeda", "Andromeda", ""),
]


def norm(s):
    s = (s or "").replace("’", "'").replace("–", "-").replace("—", "-")
    s = " ".join(s.casefold().split())
    return s[:-4] if s.endswith(" dlc") else s


def main():
    data = json.loads((pathlib.Path(__file__).resolve().parent / "data"
                       / "mass-effect.json").read_text(encoding="utf-8"))

    rows = {}
    used = set()
    for iid, key, expect, year, sec, tier, note, opt in ROSTER:
        rec = data.get(key)
        assert rec, "no HLTB record for %s" % key
        assert norm(rec["name"]) == norm(expect), \
            "record mismatch for %s: %r" % (key, rec["name"])
        assert abs(int(rec["year"]) - year) <= 1, \
            "year mismatch for %s: wiki %d, hltb %s" % (key, year, rec["year"])
        used.add(key)
        w = rec["main_h"] if rec["main_h"] else 0
        assert w > 0, "every Mass Effect row needs hours (%s)" % key
        x = {"id": iid, "t": expect, "n": str(year), "w": w, "tier": tier,
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
        span = ("%d" % got[0]["year"] if got[0]["year"] == got[-1]["year"]
                else "%d–%d" % (got[0]["year"], got[-1]["year"]))
        sec = {"id": key, "title": title,
               "sub": "%s · %d %s · %d hours story"
                      % (span, len(got),
                         "entry" if len(got) == 1 else "entries",
                         round(hours)),
               "items": [{k: v for k, v in e.items()
                          if k in ("id", "t", "n", "w", "tier", "opt", "note")}
                         for e in got]}
        if intro:
            sec["intro"] = intro
        if key == "me1":
            sec["open"] = True
        sections.append(sec)

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert len(ids) == len(ROSTER) == 11, (len(ids),)
    tiers = {t: [x for s in sections for x in s["items"] if x["tier"] == t]
             for t in (1, 2, 3)}
    assert len(tiers[1]) == 3, "trilogy should be 3, got %d" % len(tiers[1])
    assert len(tiers[2]) == 7, "story DLC should be 7, got %d" % len(tiers[2])
    assert len(tiers[3]) == 1, "tier 3 should be 1, got %d" % len(tiers[3])

    hours = sum(x["w"] for s in sections for x in s["items"])
    spine = sum(x["w"] for x in tiers[1])

    prop = {
        "slug": SLUG,
        "title": "Mass Effect",
        "subtitle": "the Shepard trilogy and its DLC, then Andromeda",
        "kind": "games",
        "order": 101,
        "year": "2007–",
        "blurb": "The trilogy, 7 story DLC and Andromeda — about %d hours "
                 "of story, %d of it the trilogy itself." % (round(hours),
                                                             round(spine)),
        "unit": {"one": "game", "many": "games"},
        "verb": {"base": "play", "past": "played", "ing": "playing"},
        "itemOrder": "number-first",
        "accent": "#B3282E",
        "accentDark": "#F2A03D",
        "tiers": True,
        "itemTiers": True,
        "paceTiers": [1],
        "paceLabel": "the DLC and Andromeda",
        "notes": [
            ["One save, three games.", "The trilogy is a single story that "
             "reads your choices forward — play it in order, carry the "
             "save. Legendary Edition (2021) is all three remastered with "
             "the DLC already inside, and it is the way in; whichever "
             "edition you play, tick the same rows."],
            ["The DLC rows are chapters.", "Only the major story add-ons "
             "HowLongToBeat tracks separately got rows; inside Legendary "
             "they are simply missions you pass on the way. The short "
             "companion packs — Kasumi, Zaeed, From Ashes — are not split "
             "out. And it is Bring Down the Sky, not Bringing — the "
             "asteroid is the thing being brought."],
            ["Order within the DLC.", "Arrival is the bridge into 3, so it "
             "goes last in 2; Citadel is the series' goodbye and lands "
             "hardest just before 3's finale. The rows sit in release "
             "order regardless."],
            ["Andromeda, last.", "A different galaxy, a different crew, no "
             "Shepard — the trilogy is complete without it, and it is "
             "marked optional for that reason, not because it is short."],
            ["Hours are story only.", "HowLongToBeat main-story figures — "
             "no side quests, no scanning planets. A completionist trilogy "
             "run is roughly double."],
            "Game and DLC list from Wikipedia's Mass Effect articles; "
            "hours from HowLongToBeat main-story figures, matched by name "
            "and year.",
        ],
        "sections": sections,
    }

    out = (pathlib.Path(__file__).resolve().parent.parent / "properties"
           / ("%s.json" % SLUG))
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json" % SLUG)
    print("  %d sections, %d rows, %d hours (%d the trilogy)"
          % (len(sections), len(ids), round(hours), round(spine)))
    for s in sections:
        print("   %-16s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
