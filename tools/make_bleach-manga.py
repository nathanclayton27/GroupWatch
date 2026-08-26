#!/usr/bin/env python3
"""Generate properties/bleach-manga.json.

    python tools/make_bleach-manga.py

Tite Kubo's Bleach, complete: 698 chapters in 74 collected volumes, in
publication order, one section per volume — the same shape as the Dragon Ball
and One Piece manga lists here.

Sections carry the arc, because for once the source states it. Wikipedia's
three Bleach chapter lists each open by naming the arcs they cover and the
volumes each one runs through — "The first arc, going through volumes 1–8",
"The volumes that include the arc are 22 to 48" — so the five arcs below are
transcribed from those sentences and scratch/agent-bleachmanga/parse.py
asserts each sentence is still in the article before this builds. That is
unlike Naruto, whose arc names are fan-wiki taxonomy and are therefore absent
from its list here.

Two things about Bleach's numbering, both from the source rather than from
tidying:

  Twelve chapters are numbered -108 to -97. Wikipedia counts them among the
  698 ("686 listed chapters and 12 chapters which were listed as -108 to
  -97"), so they are ordinary rows, sitting in volumes 36 and 37 where the
  volumes put them.

  Nine further entries appear in the volume tables and NOT in that count:
  two chapters numbered 0, one each numbered 0.8, 88.5, 520.5, -12.5, -16
  and -17, and one entry with no number at all. They ship as optional rows
  carrying their titles, in the volume that collected them — never silently
  dropped, never counted as part of the run.

The one thing here that is not in a volume is the 20th-anniversary one-shot,
which the Bleach (manga) article files as a one-shot rather than as part of
the 698; it is the last section, optional.

Unweighted: a chapter is a chapter, and nothing here claims to know how long
one takes to read.

Data: scratch/agent-bleachmanga/fetch.py -> parse.py -> tools/data/bleach-manga.json
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from gwlib import prop  # noqa: E402

SLUG = "bleach-manga"
KIND = "manga"

DATA = pathlib.Path(__file__).resolve().parent / "data" / (SLUG + ".json")

# What the group signed up for; the build fails rather than drift.
EXPECTED = {"volumes": 74, "chapters": 698, "numbered": 686, "side": 12,
            "extras": 9, "side_first": -108, "side_last": -97}

WIKI = "https://en.wikipedia.org/wiki/"
# volumes lo, hi -> the chapter list that carries them, and the chapters that
# article's own title claims. Both halves are checked against the parsed data.
CHAPTER_LISTS = [
    (1, 21, 1, 187, WIKI + "List_of_Bleach_chapters_(1%E2%80%93187)"),
    (22, 48, 188, 423, WIKI + "List_of_Bleach_chapters_(188%E2%80%93423)"),
    (49, 74, 424, 686, WIKI + "List_of_Bleach_chapters_(424%E2%80%93686)"),
]
# Viz publishes it in English and its reader is the one place every chapter is
# legitimately available; there is no stable per-volume URL to point at, so
# every section carries the same series link.
VIZ = "https://www.viz.com/shonenjump/chapters/bleach"
ARTICLE = WIKI + "Bleach_(manga)"

# A hyphen-minus next to an en dash reads as a range separator, so the twelve
# backwards-numbered chapters wear a real minus sign: "−108 to −100", not
# "-108–-100".
MINUS = "−"

# The 20th-anniversary chapter, from the Bleach (manga) article: "A 73-page
# chapter, titled 'New Breathes From Hell' … was published in Weekly Shōnen
# Jump, to commemorate the 20th anniversary of the manga's debut in the
# magazine, on August 10, 2021 … The chapter was digitally released as a
# collected volume". It is in none of the 74 volumes and in none of the three
# chapter lists, so it is the one row here that no volume holds.
ONESHOT = "New Breathes From Hell"


def disp(n):
    """A chapter number as it should read on the page."""
    if n is None:
        return ""
    s = ("%g" % n) if isinstance(n, float) else str(n)
    return s.replace("-", MINUS)


def frag(n):
    """A chapter number as an id fragment: -12.5 -> m12-5, 88.5 -> 88-5."""
    if n is None:
        return ""
    s = ("%g" % n) if isinstance(n, float) else str(n)
    return s.replace("-", "m").replace(".", "-")


def ranges(nums):
    """Contiguous runs of integers, rendered as a chapter range."""
    runs = []
    for n in nums:
        if runs and isinstance(n, int) and n == runs[-1][1] + 1:
            runs[-1][1] = n
        else:
            runs.append([n, n])
    out = []
    for a, b in runs:
        if a == b:
            out.append(disp(a))
        elif a < 0:
            out.append("%s to %s" % (disp(a), disp(b)))
        else:
            out.append("%s–%s" % (disp(a), disp(b)))
    return ", ".join(out)


def counted(c):
    """Is this entry one of the 698 the source counts?"""
    n = c["n"]
    return isinstance(n, int) and (
        n > 0 or EXPECTED["side_first"] <= n <= EXPECTED["side_last"])


def links_for(vol):
    for lo, hi, _, _, url in CHAPTER_LISTS:
        if lo <= vol <= hi:
            return [{"label": "The chapter list", "url": url},
                    {"label": "Read on Viz", "url": VIZ}]
    raise SystemExit("volume %r belongs to no chapter list" % vol)


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    vols = data["vols"]

    assert data["volumes"] == EXPECTED["volumes"], data["volumes"]
    assert data["chapters"] == EXPECTED["chapters"], data["chapters"]
    assert data["numbered"] == EXPECTED["numbered"], data["numbered"]
    assert data["side_story"] == EXPECTED["side"], data["side_story"]
    assert data["extras"] == EXPECTED["extras"], data["extras"]
    assert [v["vol"] for v in vols] == list(range(1, EXPECTED["volumes"] + 1))

    # the volumes must tile the serialized run with no gap or overlap, and the
    # backwards-numbered side story must be whole and in order
    main_run = [c["n"] for v in vols for c in v["chapters"]
                if isinstance(c["n"], int) and c["n"] > 0]
    side_run = [c["n"] for v in vols for c in v["chapters"]
                if isinstance(c["n"], int)
                and EXPECTED["side_first"] <= c["n"] <= EXPECTED["side_last"]]
    assert main_run == list(range(1, EXPECTED["numbered"] + 1)), \
        "chapter run breaks at index %s" % next(
            (i for i, n in enumerate(main_run) if n != i + 1), "?")
    assert side_run == list(range(EXPECTED["side_first"],
                                  EXPECTED["side_last"] + 1)), side_run

    # each chapter list's title claims a chapter range; the volumes it covers
    # must actually hold exactly that range
    for lo, hi, first, last, _ in CHAPTER_LISTS:
        held = [c["n"] for v in vols if lo <= v["vol"] <= hi
                for c in v["chapters"] if isinstance(c["n"], int) and c["n"] > 0]
        assert held[0] == first and held[-1] == last, \
            "volumes %d–%d hold %d–%d, article says %d–%d" \
            % (lo, hi, held[0], held[-1], first, last)

    # arcs, stated by the articles and tiled by the parse; here they only have
    # to cover every volume exactly once
    arcs = data["arcs"]
    assert arcs[0]["first_vol"] == 1
    assert arcs[-1]["last_vol"] == EXPECTED["volumes"]
    for a, b in zip(arcs, arcs[1:]):
        assert b["first_vol"] == a["last_vol"] + 1, "arc gap after %r" % a["name"]

    def arc_of(vol):
        for a in arcs:
            if a["first_vol"] <= vol <= a["last_vol"]:
                return a
        raise SystemExit("volume %d belongs to no arc" % vol)

    def chapters_in(lo, hi):
        held = [c["n"] for v in vols if lo <= v["vol"] <= hi
                for c in v["chapters"] if isinstance(c["n"], int) and c["n"] > 0]
        return held[0], held[-1]

    sections = []
    for v in vols:
        arc = arc_of(v["vol"])
        items = []
        for c in v["chapters"]:
            if counted(c):
                items.append({"id": "blm-%s" % frag(c["n"]),
                              "t": "Chapter", "n": disp(c["n"])})
                continue
            # an entry outside the count: optional, and carrying the title it
            # needs to be findable at all — the unnumbered one has nothing else
            bits = [b for b in (frag(c["n"]), prop.slug(c["t"])) if b]
            items.append({"id": "blm-x%s" % "-".join(bits),
                          "t": "Chapter" if c["n"] is not None else "Special",
                          "n": disp(c["n"]),
                          "note": c["t"],
                          "opt": True})
        s = {
            "id": "v-%d" % v["vol"],
            "title": "Volume %d" % v["vol"],
            "sub": "chapters %s · %s · %s"
                   % (ranges([c["n"] for c in v["chapters"] if counted(c)]),
                      v["title"], arc["name"]),
            "links": links_for(v["vol"]),
            "items": items,
        }
        if v["vol"] == arc["first_vol"]:
            first, last = chapters_in(arc["first_vol"], arc["last_vol"])
            s["intro"] = ("%s arc — volumes %d–%d, chapters %d–%d."
                          % (arc["name"], arc["first_vol"], arc["last_vol"],
                             first, last))
        sections.append(s)

    # the one volume that opens the backwards-numbered side story explains it
    holder = next(s for s in sections
                  if any(x["n"] == disp(EXPECTED["side_first"])
                         for x in s["items"]))
    holder["intro"] = (
        "The twelve chapters numbered %s to %s are a side story, set before "
        "the main plot. Wikipedia counts them among the 698, so they are rows "
        "like any other; they run through this volume and into the next, "
        "between chapters 315 and 316, which is where the volumes put them."
        % (disp(EXPECTED["side_first"]), disp(EXPECTED["side_last"])))

    sections.append({
        "id": "after",
        "title": "After the run",
        "sub": "one chapter · %s · in no volume" % ONESHOT,
        "intro": "A 73-page chapter published in Weekly Shōnen Jump for "
                 "the manga's 20th anniversary, five years after the last "
                 "volume, and later released on its own. The article files it "
                 "as a one-shot rather than as one of the 698, so it is "
                 "optional here. Burn the Witch, Kubo's other series set in "
                 "the same world, is a separate series and is not on this "
                 "list.",
        "links": [{"label": "The article", "url": ARTICLE}],
        "items": [{"id": "blm-oneshot-%s" % prop.slug(ONESHOT),
                   "t": ONESHOT, "n": "",
                   "note": "20th-anniversary one-shot", "opt": True}],
    })
    sections[0]["open"] = True

    total = sum(len(s["items"]) for s in sections)
    optional = sum(1 for s in sections for x in s["items"] if x.get("opt"))
    assert total == EXPECTED["chapters"] + EXPECTED["extras"] + 1, total
    assert optional == EXPECTED["extras"] + 1, optional
    # Unweighted, like every manga list here: chapter counts live in the
    # section subs and no row claims an hour figure.
    assert not any("w" in x for s in sections for x in s["items"]), \
        "a row carries a weight"
    # kind "manga" is not one of build.py's syncable kinds (`syncable =
    # "film" in kind or "game" in kind`), so no row here can pair with a row
    # on another list — and the year fallback that feeds that pairing reads
    # item notes, so no note may carry a bare year either.
    assert "film" not in KIND and "game" not in KIND, KIND
    import re
    for s in sections:
        for x in s["items"]:
            assert not re.search(r"\b(?:18|19|20)\d{2}\b", x.get("note") or ""), \
                "a year leaked into %s's note: %r" % (x["id"], x.get("note"))

    p = {
        "slug": SLUG,
        "title": "Bleach (manga)",
        "subtitle": "Tite Kubo",
        "kind": KIND,
        # Under the Bleach anime (85), which is how most people met this
        # story, and a band under the manga lists of the series that outsold
        # it — One Piece 80, Naruto and Dragon Ball 78. See POPULARITY.md,
        # signals 2 and 3.
        "popularity": 74,
        "year": "2001–2016",
        "blurb": "All %d chapters across %d volumes, in publication order, "
                 "plus %d optional extras — finished."
                 % (EXPECTED["chapters"], EXPECTED["volumes"],
                    EXPECTED["extras"] + 1),
        "unit": {"one": "chapter", "many": "chapters"},
        "verb": {"base": "read", "past": "read", "ing": "reading"},
        # Ink blue: the manga's own black-and-white against the orange the
        # Bleach anime list here wears, so the two never read as one page.
        "accent": "#1F3557",
        "accentDark": "#89B9F0",
        "tiers": False,
        "notes": [
            ["Volumes, and the arcs on them.", "Sections are the %d collected "
             "tankōbon; each one names its own title and the arc it "
             "belongs to. Unusually, the arcs come from the source: each of "
             "Wikipedia's three Bleach chapter lists opens by naming the arcs "
             "it covers and the volumes each runs through, and the generator "
             "checks those sentences are still there before it builds."
             % EXPECTED["volumes"]],
            ["Chapters that count backwards.", "Twelve chapters are numbered "
             "%s to %s — a side story set before the main plot, collected "
             "in volumes 36 and 37 between chapters 315 and 316. The source "
             "counts them among the %d, so they are rows like any other."
             % (disp(EXPECTED["side_first"]), disp(EXPECTED["side_last"]),
                EXPECTED["chapters"])],
            ["Nine extras, marked optional.", "Nine more entries sit in the "
             "volume tables and outside that count: two chapters numbered 0, "
             "one each numbered 0.8, 88.5, 520.5, %s12.5, %s16 and %s17, and "
             "one with no number at all. Each sits in the volume that "
             "collected it, marked optional and carrying its title — "
             "which is the only way to tell two chapter 0s apart."
             % (MINUS, MINUS, MINUS)],
            ["Numbers, not titles.", "Every other row is a chapter number and "
             "nothing else, the same choice the Bleach episode list here "
             "makes. Only the optional rows carry a title, because a number "
             "alone cannot tell two chapter 0s apart."],
            ["Finished.", "August 2001 to August 2016. One chapter came after "
             "— the 20th-anniversary one-shot in the last section — "
             "and it is in none of the volumes."],
            "Volumes, chapter numbers and arc boundaries machine-read from "
            "Wikipedia's List of Bleach volumes and its three chapter lists; "
            "the one-shot from the Bleach (manga) article. Every count here is "
            "asserted against the totals those articles state for themselves.",
        ],
        "sections": sections,
    }

    out = prop.write(p)

    print("wrote %s" % out.name)
    print("  %d volumes + 1 section after them, %d rows (%d counted chapters, "
          "%d optional)" % (EXPECTED["volumes"], total,
                            EXPECTED["chapters"], optional))
    print("  shortest volume: %d rows, longest: %d"
          % (min(len(s["items"]) for s in sections[:-1]),
             max(len(s["items"]) for s in sections[:-1])))
    for a in arcs:
        first, last = chapters_in(a["first_vol"], a["last_vol"])
        print("  %-24s volumes %2d–%2d  chapters %3d–%3d"
              % (a["name"], a["first_vol"], a["last_vol"], first, last))


if __name__ == "__main__":
    main()
