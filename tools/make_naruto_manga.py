#!/usr/bin/env python3
"""Generate properties/naruto-manga.json.

    python tools/make_naruto_manga.py

Masashi Kishimoto's Naruto, complete: 700 chapters in 72 collected volumes,
in publication order, one section per volume.

Volumes rather than arcs, because volumes are what the source enumerates.
Wikipedia's three Naruto chapter lists — Part I, and the two halves of Part
II — are built entirely out of {{Graphic novel list}} templates, one per
tankobon, each stating its own first chapter number. There is no arc table
anywhere in them. Naruto's arc names ("Chunin Exams", "Pain's Assault") are
fan-wiki taxonomy, not Wikipedia's, so sectioning by arc would mean importing
boundaries from a source that does not enumerate them, or drawing them by
hand. Volumes are stated, they tile the run exactly, and at seven to thirteen
chapters each they are the right size for a strip.

The counts reconcile against the tables, never against prose. The Part I
article's lead says the series continues "to more than seven hundred chapters
in all"; the enumerated tables give exactly 700, and the tables win. The
infobox on Naruto agrees with them at 72 volumes, and List of Naruto volumes
splits those 27 + 45 between the two Parts, which is what the tables do.
EXPECTED below asserts all of it, so a future edit that desyncs the article
from its own tables fails this build instead of quietly shipping.

Rows carry the English chapter title and nothing else. Every {{Graphic novel
list}} template also has a Summary field; scratch/naruto-manga/harvest.py
reads past it deliberately. A Naruto chapter summary is a spoiler, and this is
the easiest list on the site to ruin for someone.

Unweighted: a chapter is a chapter. Nothing here claims to know how long one
takes to read.

Data: scratch/naruto-manga/harvest.py -> scratch/naruto-manga/naruto-manga.json
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from gwlib import prop  # noqa: E402

SLUG = "naruto-manga"

DATA = (pathlib.Path(__file__).resolve().parent.parent
        / "scratch" / "naruto-manga" / "naruto-manga.json")

# What the group signed up for. The build fails rather than drift.
EXPECTED = {"chapters": 700, "volumes": 72,
            "part1_volumes": 27, "part2_volumes": 45,
            "part1_last_chapter": 244}

WIKI = "https://en.wikipedia.org/wiki/"
# The three articles that carry the chapter tables, by the volume they cover.
CHAPTER_LISTS = [
    (1, 27, WIKI + "List_of_Naruto_chapters_(Part_I)"),
    (28, 48, WIKI + "List_of_Naruto_chapters_(Part_II,_volumes_28%E2%80%9348)"),
    (49, 72, WIKI + "List_of_Naruto_chapters_(Part_II,_volumes_49%E2%80%9372)"),
]
# Viz publishes it in English and its reader is the one place every chapter is
# legitimately available; there is no stable per-volume URL to point at, so
# every section carries the same series link.
VIZ = "https://www.viz.com/shonenjump/chapters/naruto"


def list_url(vol):
    for lo, hi, url in CHAPTER_LISTS:
        if lo <= vol <= hi:
            return url
    raise SystemExit("volume %r belongs to no chapter list" % vol)


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    vols = data["vols"]

    assert data["chapters"] == EXPECTED["chapters"], data["chapters"]
    assert data["volumes"] == EXPECTED["volumes"], data["volumes"]
    assert len(vols) == EXPECTED["volumes"], len(vols)
    assert [v["n"] for v in vols] == list(range(1, EXPECTED["volumes"] + 1))

    # volumes must tile chapters 1..700 with no gap and no overlap
    run = [c["n"] for v in vols for c in v["chapters"]]
    assert run == list(range(1, EXPECTED["chapters"] + 1)), \
        "chapter run breaks at index %s" % next(
            (i for i, n in enumerate(run) if n != i + 1), "?")

    # the Part I / Part II split the articles state for themselves
    part1 = [v for v in vols if v["n"] <= EXPECTED["part1_volumes"]]
    part2 = [v for v in vols if v["n"] > EXPECTED["part1_volumes"]]
    assert len(part1) == EXPECTED["part1_volumes"], len(part1)
    assert len(part2) == EXPECTED["part2_volumes"], len(part2)
    assert part1[-1]["chapters"][-1]["n"] == EXPECTED["part1_last_chapter"]
    assert part2[0]["chapters"][0]["n"] == EXPECTED["part1_last_chapter"] + 1

    sections = []
    for v in vols:
        first = v["chapters"][0]["n"]
        last = v["chapters"][-1]["n"]
        sections.append({
            "id": "v-%d" % v["n"],
            "title": "Volume %d" % v["n"],
            "sub": "chapters %d–%d · %s" % (first, last, v["title"]),
            "links": [
                {"label": "The chapter list", "url": list_url(v["n"])},
                {"label": "Read on Viz", "url": VIZ},
            ],
            "items": [{"id": "nrm-%d" % c["n"], "t": c["t"], "n": str(c["n"])}
                      for c in v["chapters"]],
        })

    # the only two structural signposts in 72 volumes
    by_id = {s["id"]: s for s in sections}
    by_id["v-1"]["intro"] = ("Part I — volumes 1–27, chapters 1–%d."
                             % EXPECTED["part1_last_chapter"])
    by_id["v-28"]["intro"] = ("Part II — volumes 28–72, chapters %d–%d."
                              % (EXPECTED["part1_last_chapter"] + 1,
                                 EXPECTED["chapters"]))
    sections[0]["open"] = True

    p = {
        "slug": SLUG,
        "title": "Naruto (manga)",
        "subtitle": "Masashi Kishimoto",
        "kind": "manga",
        # Below the Naruto anime, which is how most people met this story, and
        # level with Dragon Ball's manga (78) — the same shape of list, the
        # same order of sales, one band under One Piece's manga (80). See
        # POPULARITY.md, signals 2 and 3.
        "popularity": 78,
        "year": "1999–2014",
        "blurb": "All %d chapters across %d volumes, in publication order — "
                 "finished." % (EXPECTED["chapters"], EXPECTED["volumes"]),
        "unit": {"one": "chapter", "many": "chapters"},
        "verb": {"base": "read", "past": "read", "ing": "reading"},
        "itemOrder": "number-first",
        # Deep leaf green: the corner of the palette nothing else occupies —
        # every other green here is lighter and greyer — and a long way from
        # the orange the Naruto anime list wears, so the two never read as one
        # page. Nearest shipped accent is Breaking Bad's #2E5F2E.
        "accent": "#00560E",
        "accentDark": "#5FE06B",
        "tiers": False,
        "notes": [
            ["Volumes, not arcs.", "Sections are the %d collected tankōbon. "
             "Wikipedia's Naruto chapter lists enumerate volumes and nothing "
             "else — the arc names people use come from fan wikis — so the "
             "volume is the only boundary this list can take from a source "
             "rather than invent. Each volume's first chapter is stated by "
             "the table it comes from, and the generator checks the %d "
             "volumes tile chapters 1–%d with no gap or overlap."
             % (EXPECTED["volumes"], EXPECTED["volumes"],
                EXPECTED["chapters"])],
            ["Two parts.", "Part I runs to chapter %d and closes volume 27; "
             "Part II picks up at %d and runs to the end. The six chapters "
             "that finish volume 27 are a gaiden — set before the main story, "
             "numbered straight through with everything else, which is why "
             "the count never breaks."
             % (EXPECTED["part1_last_chapter"],
                EXPECTED["part1_last_chapter"] + 1)],
            ["Titles only.", "Every row is the chapter's English title and "
             "nothing more. The source has a summary for each volume and this "
             "list deliberately does not carry it: of everything here, Naruto "
             "is the easiest to spoil."],
            "Finished — September 1999 to November 2014, %d chapters, no more "
             "coming. Nothing to rerun for." % EXPECTED["chapters"],
        ],
        "sections": sections,
    }

    out = prop.write(p)

    total = sum(len(s["items"]) for s in sections)
    print("wrote %s" % out.name)
    print("  %d volumes, %d chapters" % (len(sections), total))
    print("  shortest section: %d chapters, longest: %d"
          % (min(len(s["items"]) for s in sections),
             max(len(s["items"]) for s in sections)))


if __name__ == "__main__":
    main()
