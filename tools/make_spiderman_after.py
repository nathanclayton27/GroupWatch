#!/usr/bin/env python3
"""Generate properties/spider-man-after-civil-war.json.

    python3 tools/make_spiderman_after.py

Picks up at ASM #539, where the Civil War list leaves off, and runs to now.

Two different kinds of thing live here and the tiers say which is which. Back
in Black and One More Day finish the story the pre-Civil War list was telling,
so they are tier 1 and every issue is listed. Everything after that is
explicitly a set of recommendations rather than a list to complete, so its
entries are whole arcs and runs — Superior Spider-Man at tier 2 because it is
the one thing every guide singles out, the rest at tier 3 and outside the
finish date.

Part Two entries weigh one each on purpose. They are single decisions, not a
queue being paced through, and at true length Ultimate Spider-Man's 160 issues
would crush every neighbouring mark to the minimum width.

Notes say what an entry is, never what happens in it.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from spiderman_data import S_V2, S_SUP, S_ULT24, S_2022, S_2025, asm, item, rng

SLUG = "spider-man-after-civil-war"

SECTIONS = [
    {
        "id": "backinblack", "tier": 1, "title": "Back in Black",
        "sub": "#539–543 · 2007 · straight out of Civil War",
        "open": True,
        "links": [{"label": "The series", "url": S_V2}],
        "intro": "Reads directly on from the last Civil War issue. If you have "
                 "not read that list, start there — this arc is a reaction to it "
                 "from the first page.",
        "items": rng(539, 543),
    },
    {
        "id": "omd", "tier": 1, "title": "One More Day",
        "sub": "2007 · four issues, in exactly this order",
        "intro": "The most argued-about editorial decision in the character's "
                 "history, and the line the classic run ends on. Best read in one "
                 "sitting — and plenty of readers stop here on purpose.",
        "items": [
            asm(544),
            item("omd-2", "Friendly Neighborhood Spider-Man", "#24",
                 "One More Day, part 2"),
            item("omd-3", "Sensational Spider-Man", "#41", "One More Day, part 3"),
            asm(545),
        ],
    },
    {
        "id": "bnd", "tier": 3, "title": "Brand New Day",
        "sub": "#546–647 · 2008–10 · selected arcs",
        "links": [{"label": "The series", "url": S_V2}],
        "intro": "From here on this is a set of recommendations, not a list to "
                 "finish. Three issues a month, rotating writers. Peter is single, "
                 "broke and back in Queens. Better than its reputation; the arcs "
                 "are often sharp even if the premise is the thing people object to.",
        "items": [
            item("bnd-546", "The new status quo", "#546–548", "Slott and McNiven"),
            item("bnd-568", "“New Ways to Die”", "#568–573",
                 "Slott and John Romita Jr. The best Brand New Day arc.", 1),
            item("bnd-595", "“American Son”", "#595–599"),
            item("bnd-600", "Anniversary issue", "#600"),
            item("bnd-612", "“The Gauntlet”", "#612–623",
                 "A systematic reintroduction of the rogues gallery"),
            item("bnd-630", "“Shed”", "#630–633",
                 "Zeb Wells and Chris Bachalo on the Lizard. Genuinely disturbing, "
                 "genuinely great.", 1),
            item("bnd-634", "“Grim Hunt”", "#634–637",
                 "The sequel to Kraven's Last Hunt, 23 years later", 1),
            item("bnd-642", "“Origin of the Species”", "#642–647"),
        ],
    },
    {
        "id": "bigtime", "tier": 3, "title": "Dan Slott solo: Big Time",
        "sub": "#648–700 · 2010–13 · selected arcs",
        "intro": "Peter takes a job at Horizon Labs. Brighter, gadget-heavy, "
                 "more optimistic.",
        "items": [
            item("bt-666", "“Spider-Island”", "#666–673",
                 "All of Manhattan gets spider-powers. Big, fun, well-built.", 1),
            item("bt-682", "“Ends of the Earth”", "#682–687", "Doc Ock"),
            item("bt-698", "“Dying Wish”", "#698–700",
                 "The end of Slott's first era, and the run that leads into "
                 "Superior", 2),
        ],
    },
    {
        "id": "superior", "tier": 2, "title": "Superior Spider-Man",
        "sub": "#1–33 · 2013–14 · if you read one thing after One More Day",
        "links": [{"label": "The series", "url": S_SUP}],
        "intro": "The most contentious relaunch in the character's history — "
                 "greeted with fury on announcement, and now widely considered "
                 "the best Spider-Man run of the century. Thirty-three issues, "
                 "finished, and it goes somewhere the main title never could.",
        "items": [item("superior", "Superior Spider-Man", "#1–33", "", 2, url=S_SUP)],
    },
    {
        "id": "modern", "tier": 3, "title": "The modern volumes",
        "sub": "2014 to now · Marvel Unlimited finds each by exact title and year",
        "items": [
            item("m-2014", "Amazing Spider-Man (2014)", "#1–18",
                 "Contains “Spider-Verse” (#9–15), the crossover the animated "
                 "films drew from.", 1),
            item("m-2015", "Amazing Spider-Man (2015–17)", "#1–32, #789–801",
                 "Parker Industries; Peter as globe-trotting CEO. Divisive, but "
                 "Slott's finale in #801 is genuinely lovely."),
            item("m-2018", "Amazing Spider-Man (2018–22)", "#1–74",
                 "Nick Spencer, and the best-regarded modern run on the main "
                 "title. Highlights: “Hunted” (#16–23) and “Last Remains” (#50–55).",
                 1),
            item("m-2022", "Amazing Spider-Man (2022–25)", "#1–70",
                 "Zeb Wells. The run that broke a lot of people's patience.",
                 url=S_2022),
            item("m-2025", "Amazing Spider-Man (2025– )", "#1–34",
                 "Joe Kelly and Pepe Larraz, twice monthly and well received, "
                 "building to ASM #1000 in September 2026. Marvel Unlimited adds "
                 "issues about three months after print.", url=S_2025),
        ],
    },
    {
        "id": "outside", "tier": 3, "title": "Outside continuity",
        "sub": "where a lot of the best modern Spider-Man actually lives",
        "items": [
            item("lifestory", "Spider-Man: Life Story", "#1–6",
                 "Zdarsky and Bagley. One issue per decade, Peter ageing in real "
                 "time from 1962. Self-contained, and arguably the finest "
                 "Spider-Man comic of the last twenty years.", 2),
            item("ult2024", "Ultimate Spider-Man (2024–26)", "#1–24",
                 "Hickman and Checchetto. A complete, finished run — Peter becomes "
                 "Spider-Man in his mid-thirties, already married with two kids.",
                 1, url=S_ULT24),
            item("ult2000", "Ultimate Spider-Man (2000–11)", "#1–160",
                 "Bendis and Bagley. Separate continuity, retells the origin, runs "
                 "eleven years. One of the great long runs in Marvel history.", 1),
            item("blue", "Spider-Man: Blue", "#1–6",
                 "Loeb and Sale. A good decompression read after the classic run."),
        ],
    },
]


def main():
    ids = [x["id"] for s in SECTIONS for x in s["items"]]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate item ids")
    total = len(ids)
    issues = sum(x["w"] for s in SECTIONS for x in s["items"])

    tiers = {1: 0, 2: 0, 3: 0}
    for s in SECTIONS:
        tiers[s["tier"]] += len(s["items"])
    assert tiers[1] == 9, tiers[1]        # #539-545 plus the two OMD chapters
    assert tiers[2] == 1, tiers[2]

    # nothing here may overlap the Civil War list, which ends at ASM #538
    nums = [int(x["id"][4:]) for s in SECTIONS for x in s["items"]
            if x["id"].startswith("asm-") and x["id"][4:].isdigit()]
    assert min(nums) == 539 and max(nums) == 545, (min(nums), max(nums))

    prop = {
        "slug": SLUG,
        "title": "Spider-Man After Civil War",
        "subtitle": "Back in Black to now",
        "kind": "comics",
        "order": 13,
        "year": "2007–",
        "blurb": "The end of the classic run, then eighteen years of "
                 "recommendations rather than a list to finish.",
        "unit": {"one": "entry", "many": "entries"},
        "weightUnit": {"one": "issue", "many": "issues"},
        "verb": {"base": "read", "past": "read", "ing": "reading"},
        "accent": "#7A3B5E",
        "accentDark": "#D98BB4",
        "tiers": True,
        "paceTiers": [1, 2],
        "paceLabel": "the modern recommendations",
        "notes": [
            ["Start with the Civil War list.", "Back in Black reads directly on "
             "from the last issue of Civil War. Before that, the whole run from "
             "1962 is in Amazing Spider-Man."],
            ["Tiers.", "1 is Back in Black and One More Day, every issue, "
             "finishing the story the earlier lists were telling. 2 is Superior "
             "Spider-Man, the one run every guide singles out. 3 is the rest — "
             "recommendations, not a list to complete, and outside the finish date."],
            ["No spoilers.", "The notes say what an entry is, never what happens "
             "in it. The eighteen years covered here are the most contested "
             "period in the character's history and the arguments are easy to "
             "find; none of them are here."],
            ["Part Two entries count as one each.", "They are single decisions — "
             "whether you read that run — rather than a queue to be paced "
             "through, so Ultimate Spider-Man's 160 issues don't swallow the bar. "
             "The real lengths are in the issue numbers beside each one."],
            "Selections from the checklist written for the group; the annotations "
            "are rewritten from it rather than copied, because that document "
            "spoils freely.",
        ],
        "sections": SECTIONS,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json" % SLUG)
    print("  %d sections, %d entries, %d issues" % (len(SECTIONS), total, issues))
    for s in SECTIONS:
        print("   T%d  %-34s %2d entries" % (s["tier"], s["title"][:34], len(s["items"])))


if __name__ == "__main__":
    main()
