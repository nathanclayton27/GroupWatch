#!/usr/bin/env python3
"""Generate properties/dnd-novels.json — the two D&D novel lines.

    python tools/make_dnd-novels.py

Wikipedia's List of Dungeons & Dragons fiction holds 1,208 works across a
dozen campaign settings. "All of them" is not a reading list, and picking
favourites is not something this catalogue does, so this page runs on a gate
instead of a roster:

  A line is here only if ONE AUTHORSHIP WROTE IT FROM FIRST BOOK TO LAST,
  WIKIPEDIA DOCUMENTS THE WHOLE SEQUENCE IN AN ARTICLE OF ITS OWN, and
  WIKIPEDIA'S OWN HISTORY OF D&D FICTION NAMES THAT AUTHORSHIP AS A REASON
  THE NOVEL LINE SUCCEEDED.

Exactly two clear it: Margaret Weis and Tracy Hickman's Dragonlance, and
R. A. Salvatore's Legend of Drizzt. The third clause is what keeps the gate
from being taste — it is a sentence in the "Dungeons & Dragons novels"
article ("Among these are R. A. Salvatore and the writing partnership of
Margaret Weis and Tracy Hickman"), and parse_dnd.py captures it verbatim so
this generator can assert the source still says it. If Wikipedia ever names
a third, the gate admits a third; nobody here gets to.

Every fact is machine-read. scratch/agent-dnd/parse_dnd.py reads six cached
articles into tools/data/dnd-novels.json:

  Dungeons & Dragons novels      the gate sentences, and the eleven settings
                                 that have novels at all
  Dragonlance Chronicles         the infobox book list, asserted against its
  Dragonlance Legends            own number_of_books
  The Legend of Drizzt           the numbered 1-39 order and its sub-series
  R. A. Salvatore bibliography   a second opinion on every Drizzt year
  List of Dragonlance novels     every Weis-and-Hickman Krynn novel
  List of D&D fiction            the master table, whose Type column is what
                                 decides that a title is a novel

THE DRIZZT SECTION IS NOT IN PUBLICATION ORDER, on purpose. The Legend of
Drizzt article publishes its own numbered sequence and says outright that it
runs by Drizzt's life rather than by publication; the house rule is that a
documented reading order beats publication order, so the rows follow the
source and the section says so. An assertion refuses to write the file if
the two orders ever come out the same, which would mean the numbering had
been misread.

NO WEIGHTS. Not one row carries `w`. The reader-side rule is
`WEIGHT = x.w >= 0 ? x.w : 1`, so a single weighted row would silently
redefine every unweighted row as one hour. Page counts differ by edition and
a page is not an hour, so this page counts books and says so.
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop  # noqa: E402

SLUG = "dnd-novels"
DATA = prop.ROOT / "tools" / "data" / "dnd-novels.json"

ACCENT, ACCENT_DARK = "#8C2F2A", "#E0A94F"

WIKI = "https://en.wikipedia.org/wiki/"

# The gate's third clause, verbatim. parse_dnd.py lifts these out of the
# "Dungeons & Dragons novels" article and fails if they have changed; this
# generator refuses to build if the captured text has drifted from what the
# page below claims the source says.
GATE_AUTHORS = (
    "some fantasy fiction authors that were introduced through the TSR "
    "novels became popular authors. Among these are [[R. A. Salvatore]] and "
    "the writing partnership of [[Margaret Weis]] and Tracy Hickman.")
GATE_CHRONICLES = ("The first three books became the highly successful "
                   "''Dragonlance Chronicles Trilogy''.")

# Every series the Dragonlance list files a post-Legends Weis-and-Hickman
# novel under, mapped to the label a row note uses. A series name that is
# not listed raises rather than reaching a reader unreviewed, and main()
# asserts every key matched something — a silent no-op here has caused real
# outages in this repo.
WH_SERIES = {
    "The Chronicles: The Second Generation": "The Second Generation",
    "The War of Souls": "The War of Souls",
    "The Chronicles: The Lost Chronicles Trilogy": "The Lost Chronicles",
    "Destinies": "Destinies",
    "War Wizard": "",          # its own name; the row is the series
}

# Lines named in the notes as left out. Each must exist in the source data,
# so the notes cannot quietly name something Wikipedia does not carry.
REJECTED_DL = ["Preludes", "Heroes", "Meetings Sextet", "Elven Nations",
               "Dwarven Nations", "Villains", "Lost Histories",
               "The Warriors", "The Raistlin Chronicles", "Dark Disciple",
               "Kang's Regiment"]
REJECTED_FR = ["The Harpers", "The Avatar Series", "War of the Spider Queen",
               "The Sundering", "Sembia: Gateway to the Realms",
               "The Cleric Quintet", "Stone of Tymora",
               "The Elminster Series", "Shandril's Saga",
               "The Erevis Cale Trilogy", "Brimstone Angels"]
REJECTED_SETTINGS = ["Greyhawk", "Ravenloft", "Dark Sun", "Eberron",
                     "Mystara", "Planescape", "Spelljammer", "Birthright",
                     "Kara-Tur"]


def load():
    d = json.loads(DATA.read_text(encoding="utf-8"))
    assert d["gate"]["authors"] == GATE_AUTHORS, \
        "the gate sentence has drifted:\n%s" % d["gate"]["authors"]
    assert d["gate"]["chronicles"] == GATE_CHRONICLES, d["gate"]["chronicles"]
    assert d["chronicles"]["claim"].startswith(
        "This series is the first set of Dragonlance novels"), \
        d["chronicles"]["claim"]
    assert d["legends"]["claim"].startswith(
        "This series is the sequel to the"), d["legends"]["claim"]
    return d


def row(title, year, note="", opt=0):
    it = {"id": "dnd-%d-%s" % (year, prop.slug(title)), "t": title,
          "n": str(year)}
    if note:
        it["note"] = note
    if opt:
        it["opt"] = 1
    return it


def unique_accent(pair):
    """No other property may already own this accent pair — a shared pair
    makes two lists look like one, and qa_lint rejects duplicates."""
    for f in sorted((prop.ROOT / "properties").glob("*.json")):
        if f.stem in (SLUG, "index", "search"):
            continue
        try:
            p = json.loads(f.read_text(encoding="utf-8"))
        except Exception:                                   # noqa: BLE001
            continue
        if isinstance(p, dict):
            assert (p.get("accent"), p.get("accentDark")) != pair, \
                "accent pair %s already belongs to %s" % (pair, f.stem)


def span(items):
    ys = [int(x["n"]) for x in items]
    return min(ys), max(ys)


def main():
    d = load()

    # ---------------------------------------------------------- the spine
    chron_rows = d["chronicles"]["rows"]
    leg_rows = d["legends"]["rows"]
    assert len(chron_rows) == d["chronicles"]["n"] == 3, chron_rows
    assert len(leg_rows) == d["legends"]["n"] == 3, leg_rows
    assert [r["t"] for r in chron_rows] == d["chronicles"]["books"]
    assert [r["t"] for r in leg_rows] == d["legends"]["books"]

    c_items = [row(r["t"], r["y"],
                   "The first Dragonlance novel" if i == 0 else "")
               for i, r in enumerate(chron_rows)]
    l_items = [row(r["t"], r["y"],
                   "The first of the sequel trilogy" if i == 0 else "")
               for i, r in enumerate(leg_rows)]

    # ---------------------------------------------------------- Drizzt
    drizzt = d["drizzt"]
    assert len(drizzt) == 39, len(drizzt)
    assert [x["n"] for x in drizzt] == list(range(1, 40))
    for x in drizzt:
        assert x["bib_y"] == x["y"], x          # two sources agreed at parse

    # the source's order really is not the publication order — if it ever
    # comes out the same, the numbering has been misread
    by_year = sorted(drizzt, key=lambda x: (x["y"], x["n"]))
    assert [x["t"] for x in by_year] != [x["t"] for x in drizzt], \
        "the numbered order and publication order came out identical"

    subs = {}
    for x in drizzt:
        subs.setdefault(x["sub"], []).append(x)
    assert len(subs) == 13, sorted(subs)

    facts = d["fr_facts"]
    assert facts["sundering_books"][0] == "The Companions", facts
    n_sundering = len(facts["sundering_authors"])

    SPELLED = {5: "five", 6: "six", 7: "seven"}
    EXTRA = {
        "The Crystal Shard": "The second Forgotten Realms novel published, "
                             "and the first of them by Salvatore",
        "The Legacy": "The first Forgotten Realms novel in hardcover",
        "The Companions": "Salvatore's volume of a %s-book crossover, one "
                          "book each by %s authors"
                          % (SPELLED[len(facts["sundering_books"])],
                             SPELLED[n_sundering]),
    }
    used_extra = set()
    d_items = []
    for x in drizzt:
        group = subs[x["sub"]]
        pos = group.index(x) + 1
        bits = [x["sub"] if len(group) == 1
                else "%s, %d of %d" % (x["sub"], pos, len(group))]
        if x["t"] in EXTRA:
            bits.append(EXTRA[x["t"]])
            used_extra.add(x["t"])
        d_items.append(row(x["t"], x["y"], prop.join_bits(*bits)))
    assert used_extra == set(EXTRA), sorted(set(EXTRA) - used_extra)

    # ------------------------------------------------- the continuations
    wh, seen_series = d["weis_hickman_after"], set()
    a_items = []
    for r in wh:
        assert r["series"] in WH_SERIES, \
            "unreviewed Dragonlance series on %r: %r" % (r["t"], r["series"])
        seen_series.add(r["series"])
        a_items.append((r["y"], row(r["t"], r["y"],
                                    prop.join_bits("Dragonlance",
                                                   WH_SERIES[r["series"]]),
                                    opt=1)))
    assert seen_series == set(WH_SERIES), \
        "series never matched: %s" % sorted(set(WH_SERIES) - seen_series)

    sal_after = d["salvatore_after"]
    assert len(sal_after) == 1, [r["t"] for r in sal_after]
    for r in sal_after:
        a_items.append((r["y"], row(
            r["t"], r["y"],
            "Forgotten Realms · filed with the Drizzt books, outside the "
            "numbered sequence", opt=1)))
    a_items = [it for _y, it in sorted(a_items, key=lambda p: (p[0], p[1]["t"]))]

    # ------------------------------------------------------- the sections
    cs, ce = span(c_items)
    ls, le = span(l_items)
    ds, de = span(d_items)
    as_, ae = span(a_items)

    sections = [
        {"id": "chronicles", "title": "Dragonlance Chronicles",
         "sub": "%d novels · %d–%d · Weis and Hickman" % (len(c_items), cs, ce),
         "open": True,
         "intro": "Where D&D fiction starts. Three novels written to carry a "
                  "campaign setting, which turned into the thing the setting "
                  "is remembered for. Publication order, which is also the "
                  "order they were written in.",
         "links": [{"label": "Dragonlance Chronicles",
                    "url": WIKI + "Dragonlance_Chronicles"}],
         "items": c_items},
        {"id": "legends", "title": "Dragonlance Legends",
         "sub": "%d novels · %d · the sequel trilogy" % (len(l_items), ls),
         "intro": "The same two authors, straight on from Chronicles, all "
                  "three published inside a single year. Read Chronicles "
                  "first — Legends is built for someone who has.",
         "links": [{"label": "Dragonlance Legends",
                    "url": WIKI + "Dragonlance_Legends"}],
         "items": l_items},
        {"id": "drizzt", "title": "The Legend of Drizzt",
         "sub": "%d novels · %d–%d · the numbered order, not publication order"
                % (len(d_items), ds, de),
         "intro": "Thirty-nine novels by one author, in the order Wikipedia's "
                  "own article numbers them — which is not the order they came "
                  "out in. The three opening books were written after the "
                  "three that follow them here, and the source puts them "
                  "first anyway. Each row names the trilogy or set it belongs "
                  "to.",
         "links": [{"label": "The Legend of Drizzt",
                    "url": WIKI + "The_Legend_of_Drizzt"}],
         "items": d_items},
        {"id": "after", "title": "What the same hands wrote next",
         "sub": "%d novels · %d–%d · optional" % (len(a_items), as_, ae),
         "intro": "The two lines above are finished stories. These are the "
                  "books the same authors went back and wrote afterwards, in "
                  "publication order. Optional rows: tick them or ignore "
                  "them, nothing above depends on them.",
         "links": [{"label": "Dragonlance novels",
                    "url": WIKI + "List_of_Dragonlance_novels"},
                   {"label": "Salvatore bibliography",
                    "url": WIKI + "R._A._Salvatore_bibliography"}],
         "items": a_items},
    ]

    # ------------------------------------------------------ house checks
    all_items = [x for s in sections for x in s["items"]]
    assert len(all_items) == 3 + 3 + 39 + 12 == 57, len(all_items)
    assert sum(1 for x in all_items if x.get("opt")) == 12
    assert not any("w" in x for x in all_items), "a weight got in"
    assert not any("url" in x for x in all_items), "links live on headers"
    for s in ("chronicles", "legends", "after"):
        items = next(x for x in sections if x["id"] == s)["items"]
        ys = [int(x["n"]) for x in items]
        assert ys == sorted(ys), (s, ys)
    spine = [x for x in all_items if not x.get("opt")]

    # every line and setting the notes name must exist in the source data
    for name in REJECTED_DL:
        assert name in d["dragonlance_series"], name
    for name in REJECTED_FR:
        assert any(name.lower() == s.lower() or name.lower() in s.lower()
                   for s in d["master_series"] + d["salvatore_series"]), name
    for name in REJECTED_SETTINGS:
        assert name in d["master_settings"], name
    assert set(d["gate"]["settings_with_novels"]) >= set(REJECTED_SETTINGS)
    # two figures the notes state in words, held to the source
    assert len(d["gate"]["settings_with_novels"]) == 11, \
        d["gate"]["settings_with_novels"]
    assert 1200 < d["master_rows"] < 1300, d["master_rows"]

    unique_accent((ACCENT, ACCENT_DARK))

    blurb = ("The two Dungeons & Dragons novel lines one authorship wrote "
             "start to finish — Weis and Hickman's Dragonlance, and "
             "Salvatore's Drizzt. Everything else in a very large shelf is "
             "deliberately left off, and the notes say what.")
    assert not re.search(r"\d", blurb), "no counts in the blurb (CLU-190)"

    p = {
        "slug": SLUG,
        "title": "Dungeons & Dragons novels",
        "subtitle": "Dragonlance and the Legend of Drizzt",
        "kind": "books",
        "popularity": 54,
        "year": "%d–%d" % span(spine),
        "blurb": blurb,
        "unit": {"one": "book", "many": "books"},
        "verb": {"base": "read", "past": "read", "ing": "reading"},
        "accent": ACCENT,
        "accentDark": ACCENT_DARK,
        "tiers": False,
        "notes": [
            ["Two lines, and a gate rather than a roster.",
             "Wikipedia's list of D&D fiction runs to more than twelve "
             "hundred entries across eleven settings. All of it at once is "
             "not a reading list, and choosing favourites is not something this "
             "catalogue does — so a line is here only if one authorship "
             "wrote it from first book to last, Wikipedia documents the "
             "whole sequence in an article of its own, and Wikipedia's own "
             "history of D&D fiction names that authorship as a reason the "
             "novel line succeeded. Exactly two clear it: Margaret Weis and "
             "Tracy Hickman on Dragonlance, and R. A. Salvatore on Drizzt. "
             "That last test is a sentence in a source, not an opinion held "
             "here; if it ever names a third partnership, a third line "
             "appears."],
            ["Where to start.",
             "Either section. Chronicles and Drizzt were written for people "
             "who had read neither, and they share nothing but a publisher — "
             "different world, different author, no crossover. Chronicles is "
             "three books and finishes; Drizzt is a long haul."],
            ["The Drizzt rows are not in publication order.",
             "The Legend of Drizzt article publishes its own numbered "
             "sequence and says plainly that it runs by Drizzt's life rather "
             "than by publication date. A documented reading order beats "
             "publication order here, so the rows follow the source: the "
             "three books numbered first came out after the three numbered "
             "next, and the years on the rows show it. Every other section "
             "on this page is publication order."],
            ["The optional section is the same authors, later.",
             "Weis and Hickman returned to Krynn repeatedly — The Second "
             "Generation, The War of Souls, The Lost Chronicles, Destinies — "
             "and Salvatore published a Realms novel in 2025 that his "
             "bibliography files with the Drizzt books but outside the "
             "numbered run. They are marked optional because the two lines "
             "above are complete without them."],
            ["What is not here, and why.",
             "Every other setting: Greyhawk, Ravenloft, Dark Sun, Eberron, "
             "Mystara, Planescape, Spelljammer, Birthright and Kara-Tur all "
             "have novels and none has a line clearing the gate. So does "
             "most of the Forgotten Realms — The Harpers, Sembia, the Avatar "
             "books, War of the Spider Queen and The Sundering are all "
             "shared-world lines with a different author on each volume, "
             "which is the first test failing. Salvatore wrote one of The "
             "Sundering's six books and it is here, because the Drizzt "
             "sequence claims it; the other five are not. So are most of "
             "Dragonlance's "
             "own runs: Preludes, Heroes, the Meetings Sextet, Elven "
             "Nations, Dwarven Nations, Villains, Lost Histories and The "
             "Warriors. Single-author lines miss later in the gate rather "
             "than at that first test — Salvatore's own Cleric Quintet and Stone of "
             "Tymora, Ed Greenwood's Elminster books and Shandril's Saga, "
             "Paul S. Kemp's Erevis Cale trilogy, Erin M. Evans' Brimstone "
             "Angels, Troy Denning's Prism Pentad on Dark Sun, Gary Gygax's "
             "Gord the Rogue on Greyhawk. And Krynn books Margaret Weis "
             "wrote without Tracy Hickman — The Raistlin Chronicles, Dark "
             "Disciple, the Kang's Regiment books with Don Perrin — are out "
             "because the gate names the partnership, not either half of "
             "it. None of this is a verdict on any of them."],
            ["Novels only.",
             "The master list's own Type column decides what counts, which "
             "keeps out the short stories, the novellas, the anthologies "
             "(including The Second Generation, which is a collection), the "
             "Endless Quest and Adventure gamebooks, the middle-grade and "
             "young-adult books, the graphic novels, the film tie-ins, and "
             "the omnibus, annotated and special editions that repackage "
             "books already on this page."],
            ["Hours are not tracked.",
             "Every book counts as one and nothing here is weighted. Page "
             "counts differ by edition, a page is not an hour, and one "
             "weighted row would quietly turn every other row into an hour "
             "— so there are none at all."],
            ["No row gives anything away.",
             "The notes are publication facts only: which trilogy a book "
             "belongs to, where it sits in one, which was an author's first. "
             "Nothing about what happens in any of them."],
            "Titles, years, series membership and the Drizzt reading order "
            "machine-read from Wikipedia's Dungeons & Dragons novels, "
            "Dragonlance Chronicles, Dragonlance Legends, The Legend of "
            "Drizzt, R. A. Salvatore bibliography, List of Dragonlance "
            "novels and List of Dungeons & Dragons fiction articles.",
        ],
        "sections": sections,
    }

    out = prop.write(p)
    print("wrote %s — %d rows (%d optional)"
          % (out.name, len(all_items),
             sum(1 for x in all_items if x.get("opt"))))
    for s in sections:
        ys = [int(x["n"]) for x in s["items"]]
        print("   %-32s %2d rows  %d–%d"
              % (s["title"], len(s["items"]), min(ys), max(ys)))
    print("   gate asserted against the source · unweighted · %d spine rows"
          % len(spine))


if __name__ == "__main__":
    main()
