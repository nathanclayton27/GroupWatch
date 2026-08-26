#!/usr/bin/env python3
"""Generate properties/fullmetal-alchemist-manga.json.

    python tools/make_fullmetal-alchemist-manga.py

Hiromu Arakawa's manga — the thing both Fullmetal Alchemist anime adapt —
complete at 108 chapters in 27 collected volumes. One section per volume,
one row per chapter, unweighted: a chapter is a chapter.

Everything numeric comes from tools/data/fullmetal-alchemist-manga.json,
which scratch/agent-fmamanga/harvest.py builds from Wikipedia's "List of
Fullmetal Alchemist chapters" and asserts against the article's own lead
(108 chapters, 27 volumes) and against the volume chapter lists tiling
1..108 with no gap or overlap.

No arc names. Neither the chapter list nor the main article names a single
arc for this series, and the volumes carry no titles either, so the section
subs give the chapter range and the two release years and invent nothing.

The eight unnumbered extras the source files inside volumes — seven gaiden
side stories and one game-tie-in "Special Episode" prologue — are named in
the notes and are not rows. They sit outside the 108-chapter serialization
the counts are asserted against, and rowing them would make the catalogue
report 116 chapters for a 108-chapter series.
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from gwlib import prop as gwprop  # noqa: E402

SLUG = "fullmetal-alchemist-manga"
DATA = HERE / "data" / (SLUG + ".json")

# The totals the group signed up for; the build fails rather than drift when
# an upstream edit moves them.
EXPECTED = {"chapters": 108, "volumes": 27, "serialized": [2001, 2010]}

CHAPTER_LIST = ("https://en.wikipedia.org/wiki/"
                "List_of_Fullmetal_Alchemist_chapters")
LINKS = [{"label": "The chapter list", "url": CHAPTER_LIST}]

# Unnumbered entries the source places inside a volume's chapter list. Named
# in the notes, excluded from the rows — see the module docstring. Checked
# below against what the harvest actually found, so a new one upstream fails
# the build instead of vanishing quietly.
EXCLUDED = [
    (3,  "Gaiden", "The Military Festival"),
    (4,  "Gaiden", "Dog of the Military?"),
    (7,  "Gaiden", "The Second Lieutenant Goes to Battle!"),
    (8,  "Gaiden", "Fullmetal Alchemist and the Broken Angel"),
    (14, "Gaiden", "Short Story"),
    (23, "Special Episode", "Fullmetal Alchemist, Wii: Prince of Dawn, Prologue"),
    (24, "Gaiden", "Daughter of the Dusk—Prologue"),
    (27, "Gaiden", "Another Journey's End"),
]


def main():
    d = json.loads(DATA.read_text(encoding="utf-8"))
    vols = d["vols"]
    serial = d["serialized"]

    assert d["chapters"] == EXPECTED["chapters"], d["chapters"]
    assert d["volumes"] == EXPECTED["volumes"], d["volumes"]
    assert serial == EXPECTED["serialized"], serial
    assert len(vols) == EXPECTED["volumes"], len(vols)
    assert [v["n"] for v in vols] == list(range(1, EXPECTED["volumes"] + 1))

    # volumes must tile the chapters with no gap or overlap
    assert vols[0]["first"] == 1, vols[0]["first"]
    assert vols[-1]["last"] == EXPECTED["chapters"], vols[-1]["last"]
    for a, b in zip(vols, vols[1:]):
        assert b["first"] == a["last"] + 1, \
            "gap or overlap after chapter %d" % a["last"]
    for v in vols:
        assert v["jp"] and v["en"], "volume %d has no release year" % v["n"]

    found = [(e["vol"], e["label"], e["title"]) for e in d["extras"]]
    assert found == EXCLUDED, \
        "the source's unnumbered extras changed: %s" % (found,)

    sections = []
    for v in vols:
        sections.append({
            "id": "v-%d" % v["n"],
            "title": "Volume %d" % v["n"],
            "sub": "chapters %d–%d · %d · Viz %d"
                   % (v["first"], v["last"], v["jp"], v["en"]),
            "links": LINKS,
            "items": [
                {"id": "fmam-%d" % c, "t": "Chapter", "n": str(c)}
                for c in range(v["first"], v["last"] + 1)
            ],
        })

    items = [x for s in sections for x in s["items"]]
    ids = [x["id"] for x in items]
    assert len(ids) == len(set(ids)), "duplicate item ids"
    assert len(items) == EXPECTED["chapters"], len(items)
    assert len(sections) == EXPECTED["volumes"], len(sections)
    assert [x["n"] for x in items] == [str(c) for c in
                                       range(1, EXPECTED["chapters"] + 1)]

    # Unweighted, like every manga list here: chapter counts live in the
    # section subs and no row claims hours.
    assert not any("w" in x for x in items), "a row carries a weight"
    # build.py falls back to reading a single year out of a note when `n` is
    # not a year. These rows carry no notes at all; assert it rather than
    # trusting it.
    assert not any(x.get("note") for x in items), "a row carries a note"
    assert not any(re.search(r"\b(18|19|20)\d{2}\b", x.get("note") or "")
                   for x in items), "a row note leaks a bare year"

    firstv, lastv = vols[0], vols[-1]
    prop = {
        "slug": SLUG,
        "title": "Fullmetal Alchemist (manga)",
        "subtitle": "Hiromu Arakawa",
        "kind": "manga",
        "popularity": 72,
        "year": "%d–%d" % (serial[0], serial[1]),
        "blurb": "All %d chapters across %d volumes — the complete manga "
                 "both Fullmetal Alchemist anime adapt."
                 % (EXPECTED["chapters"], EXPECTED["volumes"]),
        "unit": {"one": "chapter", "many": "chapters"},
        "verb": {"base": "read", "past": "read", "ing": "reading"},
        "accent": "#3F5C6B",
        "accentDark": "#7FB3C8",
        "tiers": False,
        "notes": [
            ["The source.", "This is the manga both Fullmetal Alchemist anime "
             "adapt — the 2003 television series and Brotherhood are each an "
             "adaptation of it, and this is what they work from. Hiromu "
             "Arakawa serialized it in Monthly Shōnen Gangan from %d "
             "to %d." % (serial[0], serial[1])],
            ["Complete.", "It ended in %d at chapter %d, collected in %d "
             "volumes. Nothing here is waiting on a new release."
             % (serial[1], EXPECTED["chapters"], EXPECTED["volumes"])],
            ["Volumes.", "Sections are the collected tankōbon, each with "
             "its chapter range, its Japanese release year and the year Viz "
             "published it in English. Boundaries are parsed from Wikipedia's "
             "chapter list and checked to tile chapters 1–%d with no gap "
             "or overlap." % EXPECTED["chapters"]],
            ["No arcs named.", "Neither the chapter list nor the main article "
             "names an arc for this series, and the volumes carry no titles, "
             "so the subs give chapter ranges and years and nothing invented."],
            ["Side stories.", "Eight extras sit in the source's volume lists "
             "with no chapter number and are not rows here: gaiden in volumes "
             "3, 4, 7, 8, 14, 24 and 27, and a \"Special Episode\" "
             "prologue for a Wii game in volume 23. They fall outside the "
             "%d-chapter serialization the counts are checked against."
             % EXPECTED["chapters"]],
            "Chapters, volumes and release years machine-read from "
            "Wikipedia's List of Fullmetal Alchemist chapters, with the "
            "totals asserted against the article's own lead.",
        ],
        "sections": sections,
    }

    # manga is not a syncable kind — cross-list tick sync in src/build.py
    # gates on `"film" in kind or "game" in kind`, so nothing here can pair
    # with either anime list. Asserted rather than assumed.
    assert "film" not in prop["kind"] and "game" not in prop["kind"], \
        "kind %r would enter cross-list sync" % prop["kind"]

    out = gwprop.write(prop)

    print("wrote %s" % out.name)
    print("  %d volumes, %d sections, %d chapters, %d rows weighted"
          % (EXPECTED["volumes"], len(sections), len(items),
             sum(1 for x in items if "w" in x)))
    print("  span: %s, %d–%d (Viz %d–%d)"
          % (prop["year"], firstv["jp"], lastv["jp"],
             firstv["en"], lastv["en"]))
    print("  longest section: %d chapters"
          % max(len(s["items"]) for s in sections))
    print("  excluded (unnumbered in the source): %d" % len(EXCLUDED))
    for s in sections:
        print("   %-11s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
