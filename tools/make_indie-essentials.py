#!/usr/bin/env python3
"""Generate properties/indie-essentials.json.

    python tools/make_indie-essentials.py

A curated canon of 24 modern indie essentials, Braid to Balatro, in release
order. House-curated in the Time Loops tradition — the property note says
so and invites vetoes. No order matters, so random is on.

Every game was verified against its own Wikipedia article
(scratch/agent-games2/verify_wiki.py) and against HowLongToBeat by name and
year (scratch/agent-games2/fetch_hltb.py -> tools/data/indie-essentials.json).
Hours are HLTB main-story figures — story only, the house standard. The
three endless-shaped games (Stardew Valley, Slay the Spire, Balatro) are
marked optional and carry no story clock instead of a fake number: HLTB's
main-story figure is meaningless where nothing ends.
"""
import json
import pathlib

SLUG = "indie-essentials"

# endless-shaped: verified rows that ship with no story clock
NOCLOCK = {"stardew", "slay-the-spire", "balatro"}

# data key, expected HLTB names, display title, display year, section, note
ROSTER = [
    ("braid", ["Braid"], "Braid", 2008, "firstwave",
     "Where the wave starts — time-bending puzzles"),
    ("limbo", ["Limbo"], "Limbo", 2010, "firstwave",
     "Playdead's monochrome forest — one long evening"),
    ("super-meat-boy", ["Super Meat Boy"], "Super Meat Boy", 2010,
     "firstwave", "Pure execution — the hours shown are the light side"),
    ("journey", ["Journey"], "Journey", 2012, "firstwave",
     "Two hours, anonymous strangers, no words — best in one sitting"),
    ("fez", ["Fez"], "Fez", 2012, "firstwave",
     "The perspective trick, and a second layer for the obsessed"),
    ("papers-please", ["Papers, Please"], "Papers, Please", 2013, "boom",
     "Glory to Arstotzka"),
    ("shovel-knight", ["Shovel Knight", "Shovel Knight: Shovel of Hope"],
     "Shovel Knight", 2014, "boom",
     "The Shovel of Hope campaign is what this row counts"),
    ("ori", ["Ori and the Blind Forest"], "Ori and the Blind Forest", 2015,
     "boom", "The beautiful one that bites"),
    ("undertale", ["Undertale"], "Undertale", 2015, "boom",
     "Go in knowing nothing"),
    ("oxenfree", ["Oxenfree"], "Oxenfree", 2016, "boom",
     "Radio ghosts and very good teen talk"),
    ("firewatch", ["Firewatch"], "Firewatch", 2016, "boom",
     "A summer in a lookout tower"),
    ("stardew", ["Stardew Valley"], "Stardew Valley", 2016, "boom",
     "Ongoing by design — the farm has no credits, so no story clock "
     "here"),
    ("inside", ["Inside"], "Inside", 2016, "boom",
     "Playdead again — one sitting, no words, an ending people argue "
     "about"),
    ("hollow-knight", ["Hollow Knight"], "Hollow Knight", 2017, "peak",
     "The big one — a whole kingdom underground"),
    ("cuphead", ["Cuphead"], "Cuphead", 2017, "peak",
     "The 1930s-cartoon boss rush"),
    ("celeste", ["Celeste"], "Celeste", 2018, "peak",
     "Climbing a mountain and meaning it"),
    ("obra-dinn", ["Return of the Obra Dinn"], "Return of the Obra Dinn",
     2018, "peak", "Sixty fates, one ledger — pure deduction"),
    ("slay-the-spire", ["Slay the Spire"], "Slay the Spire", 2019, "peak",
     "Run-based and endless-shaped — no story clock"),
    ("outer-wilds", ["Outer Wilds"], "Outer Wilds", 2019, "peak",
     "A solar system on a 22-minute loop — spoil nothing, not even "
     "mechanics"),
    ("a-short-hike", ["A Short Hike"], "A Short Hike", 2019, "peak",
     "An afternoon, feathered and kind"),
    ("disco-elysium", ["Disco Elysium", "Disco Elysium: The Final Cut"],
     "Disco Elysium", 2019, "peak",
     "The RPG that is all talk, all of it good — The Final Cut is the "
     "edition to play"),
    ("hades", ["Hades"], "Hades", 2020, "now",
     "Run-based with real credits — the hours run to the story's end"),
    ("tunic", ["Tunic"], "Tunic", 2022, "now",
     "A small fox and an instruction manual you piece together"),
    ("balatro", ["Balatro"], "Balatro", 2024, "now",
     "One more run, forever — no story clock"),
]

SECTIONS = [
    ("firstwave", "The first wave", "2008–2012",
     "When 'indie game' became a canon — five that made the case."),
    ("boom", "The boom", "2013–2016",
     "The storefronts open up and every shape of game gets through."),
    ("peak", "The peak years", "2017–2019",
     "Three years that produced half of everyone's all-time lists."),
    ("now", "The 2020s", "2020–2024",
     "The wave keeps coming."),
]


def norm(s):
    s = (s or "").replace("’", "'").replace("–", "-").replace("—", "-")
    return " ".join(s.casefold().split())


def main():
    data = json.loads((pathlib.Path(__file__).resolve().parent / "data"
                       / "indie-essentials.json").read_text(encoding="utf-8"))

    rows = {}
    used = set()
    for key, expects, title, year, sec, note in ROSTER:
        rec = data.get(key)
        assert rec, "no HLTB record for %s" % key
        assert norm(rec["name"]) in {norm(e) for e in expects}, \
            "record mismatch for %s: %r" % (key, rec["name"])
        assert abs(int(rec["year"]) - year) <= 2, \
            "year mismatch for %s: wiki %d, hltb %s" % (key, year, rec["year"])
        used.add(key)
        if key in NOCLOCK:
            w = 0
        else:
            w = rec["main_h"]
            assert w and w > 0, "missing hours for %s" % key
        x = {"id": "ind-%s" % key, "t": title, "n": str(year), "w": w,
             "year": year, "note": note}
        if key in NOCLOCK:
            x["opt"] = 1
        rows.setdefault(sec, []).append(x)
    assert used == set(data), "cache keys unused: %r" % (set(data) - used)

    sections = []
    for key, title, span, intro in SECTIONS:
        got = rows[key]
        assert got == sorted(got, key=lambda e: e["year"]), key
        hours = sum(e["w"] for e in got)
        clocked = [e for e in got if e["w"]]
        sec = {"id": key, "title": title,
               "sub": "%s · %d games · %d hours story"
                      % (span, len(got), round(hours)),
               "intro": intro,
               "items": [{k: v for k, v in e.items()
                          if k in ("id", "t", "n", "w", "opt", "note")}
                         for e in got]}
        assert clocked, key
        if key == "firstwave":
            sec["open"] = True
        sections.append(sec)

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert len(ids) == len(ROSTER) == 24, (len(ids),)
    noclock = [x for s in sections for x in s["items"] if not x["w"]]
    assert len(noclock) == 3, "no-clock rows should be 3, got %d" % len(noclock)

    hours = sum(x["w"] for s in sections for x in s["items"])

    prop = {
        "slug": SLUG,
        "title": "Indie Essentials",
        "subtitle": "a house canon of the modern indies, Braid to Balatro",
        "kind": "games",
        "order": 103,
        "year": "2008–",
        "blurb": "24 essentials in any order — about %d hours of story "
                 "where a story clock exists, and three games that never "
                 "end." % round(hours),
        "unit": {"one": "game", "many": "games"},
        "verb": {"base": "play", "past": "played", "ing": "playing"},
        "itemOrder": "number-first",
        "accent": "#D94F45",
        "accentDark": "#4FC4AE",
        "tiers": False,
        "random": True,
        "notes": [
            ["The house's picks — veto freely.", "No list like this is "
             "neutral and this one does not pretend to be: 24 games, "
             "curated here, in release order because that is the story of "
             "the scene. If one is not for you, skip it loudly; if one is "
             "missing, that is what the group chat is for."],
            ["No order.", "Nothing leads to anything else — pick whatever "
             "tonight feels like. The sections are eras, not a "
             "sequence."],
            ["Three games have no clock.", "Stardew Valley, Slay the Spire "
             "and Balatro are built to never end, so they are marked "
             "optional and weigh nothing rather than wearing a made-up "
             "number. Tick them when you feel done — that is the only "
             "honest rule."],
            ["Hours are story only.", "HowLongToBeat main-story figures — "
             "credits, not completion. Hollow Knight and Disco Elysium in "
             "particular go far past their numbers."],
            "Every title verified against its own Wikipedia article; hours "
            "from HowLongToBeat main-story figures, matched by name and "
            "year.",
        ],
        "sections": sections,
    }

    out = (pathlib.Path(__file__).resolve().parent.parent / "properties"
           / ("%s.json" % SLUG))
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json" % SLUG)
    print("  %d sections, %d games, %d hours story (3 no-clock)"
          % (len(sections), len(ids), round(hours)))
    for s in sections:
        print("   %-18s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
