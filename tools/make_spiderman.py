#!/usr/bin/env python3
"""Generate properties/amazing-spider-man.json — the run up to Civil War.

    python3 tools/make_spiderman.py

Amazing Fantasy #15 through ASM #528, which is where the Road to Civil War
begins. Civil War itself is its own list (properties/civil-war.json) and
everything after it is a third (properties/spider-man-after-civil-war.json),
because one 600-issue list that swallowed a company-wide crossover in the
middle was doing three jobs badly.

Every issue in this range is listed and every issue is meant to be read. The
annotations flag what an entry *is*, never what happens in it — see the note at
the top of spiderman_data.py.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from spiderman_data import (S_V1, S_V2, S_ANN, S_AF, S_WEB, S_SPEC, S_PPSM,
                            asm, v2, item, rng, weave, check)

SLUG = "amazing-spider-man"

SECTIONS = [
    {
        "id": "prologue", "tier": 1, "title": "Prologue",
        "sub": "1962 · where it starts",
        # every section carries a series link now, so the fallback would open
        # whichever comes first; say outright that it should be this one
        "open": True,
        "links": [{"label": "Amazing Fantasy", "url": S_AF}],
        "items": [item("af15", "Amazing Fantasy", "#15", "Eleven pages.", 2)],
    },
    {
        "id": "ditko", "tier": 1, "title": "Lee & Ditko", "sub": "#1–38 · 1963–66",
        "links": [{"label": "The series", "url": S_V1},
                  {"label": "Annual", "url": S_ANN}],
        "intro": "Nearly every major villain in the mythology debuts inside "
                 "these 38 issues. Ditko's Peter is anxious, prickly and broke — "
                 "closer to the character's core than the friendlier version "
                 "that follows.",
        "items": rng(1, 38) + [
            item("ann-1", "Amazing Spider-Man Annual", "#1", "The Sinister Six", 1),
            item("ann-2", "Amazing Spider-Man Annual", "#2", "Doctor Strange"),
            item("ann-3", "Amazing Spider-Man Annual", "#3", "The Avengers"),
        ],
    },
    {
        "id": "romita", "tier": 1, "title": "Lee & Romita Sr.", "sub": "#39–102 · 1966–71",
        "intro": "The art turns glossy, Peter goes to college, and the soap "
                 "opera takes over the book.",
        "links": [{"label": "The series", "url": S_V1},
                  {"label": "Annual", "url": S_ANN}],
        "items": rng(39, 102) + [
            item("ann-5", "Amazing Spider-Man Annual", "#5", "Peter's parents", 1),
            item("ann-6", "Amazing Spider-Man Annual", "#6",
                 "Mostly reprints; skippable without loss", opt=1),
        ],
    },
    {
        "id": "conway", "tier": 1, "title": "Conway & Kane", "sub": "#103–149 · 1971–75",
        "intro": "The tonal hinge of the whole character. Read this stretch "
                 "straight through — it's the densest run of consequence in the "
                 "title's history.",
        "links": [{"label": "The series", "url": S_V1}],
        "items": rng(103, 149),
    },
    {
        "id": "seventies", "tier": 1, "title": "Wolfman, Wein & the Late Seventies",
        "sub": "#150–200 · 1975–80",
        "intro": "Quieter and more procedural. This is the stretch where the "
                 "unannotated issues outnumber the annotated ones by the widest "
                 "margin — that's the era, not an omission.",
        "links": [{"label": "The series", "url": S_V1}],
        "items": rng(150, 200),
    },
    {
        "id": "stern", "tier": 1, "title": "Stern, Mantlo & the Hobgoblin",
        "sub": "#201–251 · 1980–84",
        "intro": "Roger Stern's run, roughly #224 onward, is one of the two or "
                 "three best in the title's history: tight, character-driven, "
                 "brilliantly plotted.",
        "links": [{"label": "The series", "url": S_V1}],
        "items": rng(201, 251),
    },
    {
        "id": "black", "tier": 1, "title": "The Black Costume & Venom",
        "sub": "#252–300 · 1984–88 · with the cross-title chapters that matter",
        "links": [{"label": "The series", "url": S_V1},
                  {"label": "Spectacular", "url": S_SPEC},
                  {"label": "Web", "url": S_WEB},
                  {"label": "Annual", "url": S_ANN}],
        "items": weave(
            [item("secretwars", "Secret Wars", "#1–12",
                  "Optional, but it's where the suit is acquired", w=12, opt=1)]
            + rng(252, 300),
            ("asm-271", item("jeandewolff", "Spectacular Spider-Man", "#107–110",
                             "“The Death of Jean DeWolff” — not ASM, but one of "
                             "the finest Spider-Man stories of the decade", 2, w=4)),
            ("asm-292", item("ann-21", "Amazing Spider-Man Annual", "#21",
                             "Peter and MJ's wedding", 1)),
            ("asm-292", item("klh-1", "Web of Spider-Man", "#31",
                             "Kraven's Last Hunt, part 1", 2)),
            ("asm-293", item("klh-3", "Spectacular Spider-Man", "#131",
                             "Kraven's Last Hunt, part 3", 2)),
            ("asm-293", item("klh-4", "Web of Spider-Man", "#32",
                             "Kraven's Last Hunt, part 4", 2)),
            ("asm-294", item("klh-6", "Spectacular Spider-Man", "#132",
                             "Kraven's Last Hunt, part 6", 2)),
        ),
    },
    {
        "id": "mcfarlane", "tier": 1, "title": "McFarlane, Larsen & the Early Nineties",
        "sub": "#301–350 · 1988–91",
        "intro": "Art-driven. Thinner storytelling than Stern, but these are the "
                 "issues that fixed how a generation pictures the character.",
        "links": [{"label": "The series", "url": S_V1}],
        "items": rng(301, 350),
    },
    {
        "id": "carnage", "tier": 1, "title": "Carnage & Nineties Excess",
        "sub": "#351–393 · 1991–94 · plus the Maximum Carnage chapters",
        "links": [{"label": "The series", "url": S_V1}],
        "items": weave(
            rng(351, 393),
            ("asm-377", item("maxcarn-1", "Maximum Carnage, chapters 1–3", "◆",
                             "Spider-Man Unlimited #1 → Web #101 → Spectacular "
                             "#201, then ASM #378", 1, w=3)),
            ("asm-378", item("maxcarn-2", "Maximum Carnage, chapters 5–7", "◆",
                             "Spider-Man #35 → Web #102 → Spectacular #202, "
                             "then ASM #379", w=3)),
            ("asm-379", item("maxcarn-3", "Maximum Carnage, chapters 9–11", "◆",
                             "Spider-Man #36 → Web #103 → Spectacular #203, "
                             "then ASM #380", w=3)),
            ("asm-380", item("maxcarn-4", "Maximum Carnage, chapters 13–14", "◆",
                             "Spider-Man #37 → Spider-Man Unlimited #2", w=2)),
        ),
    },
    {
        "id": "clone", "tier": 1, "title": "The Clone Saga",
        "sub": "#394–418 · 1994–96 · the ASM path, not the complete 200 issues",
        "intro": "The Clone Saga ran two years across five monthly titles and is "
                 "genuinely enormous — roughly 200 issues read complete. It was "
                 "also being rewritten in real time by editorial, so it "
                 "contradicts itself.\n\n"
                 "These are the ASM issues plus the Revelations bookend, which is "
                 "the recommended path and follows the plot fine. The completist "
                 "alternative is the six Complete Clone Saga Epic volumes.",
        "links": [{"label": "The series", "url": S_V1},
                  {"label": "Peter Parker: Spider-Man", "url": S_PPSM}],
        "items": weave(
            rng(394, 418),
            ("asm-418", item("revelations", "“Revelations”, the other three "
                             "chapters", "◆", "Spectacular #240, Sensational #11 "
                             "and Peter Parker: Spider-Man #75 — read after "
                             "ASM #418", 1, w=3)),
        ),
    },
    {
        "id": "endvol1", "tier": 1, "title": "The End of Volume One",
        "sub": "#419–441 · 1996–98",
        "links": [{"label": "The series", "url": S_V1}],
        "items": weave(
            rng(419, 441),
            ("asm-441", item("finalchapter", "“The Final Chapter” continues", "◆",
                             "Spectacular #263 and Spider-Man #98 — read after "
                             "ASM #441", w=2)),
        ),
    },
    {
        "id": "mackie", "tier": 1, "title": "Volume Two: Mackie & Byrne",
        "sub": "vol. 2 #1–29 · 1999–2001",
        "links": [{"label": "The series", "url": S_V2}],
        "intro": "The soft reboot, and the weakest sustained stretch in the "
                 "title's history. If you're going to abridge anything, abridge here.",
        "items": [v2(n) for n in range(1, 30)],
    },
    {
        "id": "jms", "tier": 1, "title": "J. Michael Straczynski begins",
        "sub": "vol. 2 #30–58 · 2001–03",
        "intro": "The last great sustained run before the reset.",
        "links": [{"label": "The series", "url": S_V2}],
        "items": [v2(n) for n in range(30, 59)],
    },
    {
        "id": "renumbered", "tier": 1, "title": "Renumbered to #500",
        "sub": "#500–528 · 2003–06 · up to the edge of Civil War",
        "intro": "Volume 2 #58 was followed by #500, resuming the original count.\n\n"
                 "This list stops at #528. What comes next is the Road to Civil "
                 "War, and Spider-Man is close enough to the middle of that event "
                 "that it gets its own list.",
        "links": [{"label": "The series", "url": S_V2}],
        "items": weave(
            rng(500, 528),
            # The Other opens with Friendly Neighborhood #1, before ASM #525
            ("asm-524", item("theother", "“The Other”, the chapters outside ASM",
                             "◆", "Friendly Neighborhood Spider-Man #1–4 and "
                             "Marvel Knights Spider-Man #19–22, interleaved with "
                             "ASM #525–528", 1, w=8)),
        ),
    },
]


def main():
    total = check(SECTIONS, 548)
    issues = sum(x["w"] for s in SECTIONS for x in s["items"])

    v1 = [x["id"] for s in SECTIONS for x in s["items"]
          if x["id"].startswith("asm-") and x["id"][4:].isdigit()
          and int(x["id"][4:]) <= 441]
    assert len(v1) == 441, len(v1)
    assert len([x for s in SECTIONS for x in s["items"]
                if x["id"].startswith("asm-v2-")]) == 58

    prop = {
        "slug": SLUG,
        "title": "Amazing Spider-Man",
        "subtitle": "Amazing Fantasy #15 to Civil War",
        "kind": "comics",
        "popularity": 87,
        "year": "1962–2006",
        "blurb": "The complete run from the origin to the edge of Civil War — "
                 "%d issues, nothing filtered out." % issues,
        "unit": {"one": "entry", "many": "entries"},
        "weightUnit": {"one": "issue", "many": "issues"},
        "verb": {"base": "read", "past": "read", "ing": "reading"},
        "accent": "#B01E32",
        "accentDark": "#EC6B7B",
        "tiers": False,
        "notes": [
            ["This one is meant to be read whole.", "Every issue from Amazing "
             "Fantasy #15 to #528 is listed, in order, nothing filtered out. The "
             "notes are annotations, not selections: an issue with no note is a "
             "solid done-in-one with no lasting consequence, and reading those is "
             "a large part of what makes the runs feel like runs."],
            ["No spoilers.", "The notes say what an entry is — a debut, a "
             "creator's first issue, which villain turns up — and never what "
             "happens in it. Where an issue matters more than its note suggests, "
             "the stars say so instead."],
            ["Where it goes next.", "This list ends at #528. The Road to Civil "
             "War starts at #529, and both it and the event are in the Civil War "
             "list; Spider-Man picks back up in Spider-Man After Civil War."],
            ["◆ marks a chapter published outside ASM.", "From 1976 to 1998 "
             "Spider-Man ran across three or four concurrent monthlies. ASM tells "
             "a complete story alone, but stories occasionally begin or end "
             "elsewhere; everything cross-title that genuinely matters is here as "
             "its own entry, sized by how many issues it is, and placed at the "
             "point in the run where you read it rather than at the end of its "
             "section."],
            ["Links sit on the section headers.", "Every series this list draws "
             "from is linked from the header of each section that uses it, so a "
             "row never carries its own link. Marvel gives individual issues "
             "arbitrary database ids with no pattern, and series level is how "
             "you would navigate Marvel Unlimited anyway."],
            ["A shorter path, if you want one.", "The spine is roughly 200 "
             "issues: Ditko #1–38, Conway #101–149, Stern #224–252, the "
             "black-suit years #252–300, then jump to JMS at vol. 2 #30. You lose "
             "surprisingly little."],
            "Order, era boundaries and star ratings from the checklist written "
            "for the group; the annotations are rewritten from it rather than "
            "copied, because that document spoils freely.",
        ],
        "sections": SECTIONS,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json" % SLUG)
    print("  %d sections, %d entries, %d issues" % (len(SECTIONS), total, issues))
    for s in SECTIONS:
        print("   %-40s %4d entries %5d issues"
              % (s["title"][:40], len(s["items"]), sum(x["w"] for x in s["items"])))


if __name__ == "__main__":
    main()
