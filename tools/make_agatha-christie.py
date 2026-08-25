#!/usr/bin/env python3
"""Generate properties/agatha-christie.json — Poirot, Marple, standalones.

    python tools/make_agatha-christie.py

Every novel Agatha Christie published, in publication order, split into the
two runs a reader actually works through — Hercule Poirot and Miss Marple —
plus a third section holding everything else: the standalones and the
shorter runs for Tommy and Tuppence, Superintendent Battle and Colonel Race.

Nothing here is typed from memory. Three Wikipedia articles are read as
wikitext, cached under scratch/agatha-christie/:

  * "Agatha Christie bibliography" — the novels table is the spine. Its
    ``Series`` column decides which section a novel lands in, its UK-title
    header cell and UK-publication-year column supply title and year, its
    US-title column supplies most of the alternative titles, and its Notes
    column supplies the rest. The table's 74 rows are asserted against the
    article's own infobox count of 74 novels.
  * "Hercule Poirot in literature" — its numbered publication-order list is
    the merge order for the Poirot section, and the five entries it marks
    ``ss`` are the Poirot short-story collections. Its novel entries are
    asserted, title for title and in order, against the bibliography table's
    Poirot rows.
  * "Miss Marple" — its numbered series list gives the twelve Marple novels
    (asserted against the bibliography table, titles and years both) and its
    collections list gives the six Marple collections.

Both runs are checked against the character articles' own stated totals:
"appearing in 33 novels" and "wrote 12 novels". A Wikipedia edit that adds
or drops a book therefore breaks this build instead of silently reshaping
the list.

Two deliberate rulings, both explained in the property's notes:

  * The short-story collections are ``opt``. A collection is a different
    sitting from a novel, and someone working through Poirot wants the
    novels' arc — so the collections sit in the runs, in publication order,
    marked optional rather than mixed in silently. So do the six Mary
    Westmacott romances, The Floating Admiral (written with the Detection
    Club) and Hercule Poirot and the Greenshore Folly, the 1954 novella the
    bibliography's table carries but the "33 novels" figure does not.
  * Nothing is weighted. Wikipedia does not publish page counts
    consistently, and a page count is not an hour — so no row carries ``w``
    and none is estimated. This is all-or-nothing on purpose: the front end
    reads an unweighted row as one hour (WEIGHT = x.w >= 0 ? x.w : 1), so a
    partly weighted list would quietly invent times for the rest. A final
    assertion refuses to write a file where any row carries a weight.

Row notes are publication history only — alternative titles, pen names,
when a book was written against when it came out. Christie's whole value is
the reveal, so no note may hint at a solution, a victim or a twist, and the
only material a note can be built from here is the structured title and
notes columns reviewed below.
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop, wiki

SLUG = "agatha-christie"
CACHE = prop.ROOT / "scratch" / SLUG

BIB = "Agatha Christie bibliography"
POIROT = "Hercule Poirot in literature"
POIROT_CHAR = "Hercule Poirot"
MARPLE = "Miss Marple"

SER_POIROT = "Hercule Poirot"
SER_MARPLE = "Miss Marple"

# The bibliography novels table carries one Poirot row the "33 novels"
# figure does not: a 1954 novella first published on its own in 2014. It
# stays, at the end of the run, marked optional.
NOVELLA = "Hercule Poirot and the Greenshore Folly"

# Every distinct value the novels table's Notes column holds, mapped to
# (alternative titles, note fragment). Anything not listed raises rather
# than reaching a reader unreviewed, and main() asserts every key matched
# something — a silent no-op here has caused real outages in this repo.
NOTES_COL = {
    "As Mary Westmacott":
        ([], "As Mary Westmacott — a romance, not a mystery"),
    "With members of The Detection Club.":
        ([], "Written with members of The Detection Club"),
    "Later US editions also published under the title A Holiday for Murder":
        (["A Holiday for Murder"], ""),
    "Also published in the U.S. as Ten Little Indians":
        (["Ten Little Indians"], ""),
    "Published in paperback in the US under the title An Overdose of Death":
        (["An Overdose of Death"], ""),
    "Also published as A Haunting in Venice, as a tie-in with the movie of "
    "the same name":
        (["A Haunting in Venice"], "the later film tie-in title"),
    "Poirot's last case, written in the 1940s.":
        ([], "Written in the 1940s, held back and published last"),
    "Miss Marple's last case, written in the 1940s.":
        ([], "Written in the 1940s, held back and published last"),
    "Written in 1954 to raise money for a church. Later reworked into Dead "
    "Man's Folly (see above).":
        ([], "A novella written in 1954 to raise money for a church, "
             "published on its own in 2014"),
}

# Rows the Notes column marks as something other than a Christie mystery
# novel. They stay — the bibliography's table counts them — but optional.
OPT_NOTE = {"As Mary Westmacott", "With members of The Detection Club."}

DASH = "–"
PROBE = '! scope="row"'


def text(page):
    """Cached wikitext, or a loud failure — never a silent empty page."""
    t = wiki.wikitext(page, cache_dir=str(CACHE))
    assert t and len(t) > 5000, "no wikitext for %r" % page
    return t


def cell(line):
    """The content of a `! scope="row"| ...` header cell, cleaned."""
    return wiki.clean(line.split("|", 1)[1] if "|" in line else line)


def year_of(v):
    v = wiki.clean(v)
    m = re.search(r"(18|19|20)\d{2}", v)
    return int(m.group(0)) if m else None


def read_novels():
    """The bibliography's novels table: title, UK year, US year, series."""
    t = text(BIB)
    box = re.search(r"\|\s*Novel\s*=\s*(\d+)", t)
    assert box, "no Novel count in the bibliography infobox"
    seg = t[t.index("==Novels=="):t.index("==Short fiction collections==")]
    rows = wiki.table_rows(seg, 7, header_probe=PROBE)
    out = []
    for line, cols in rows:
        out.append({
            "t": cell(line),
            "y": year_of(cols[0]),
            "us_y": year_of(cols[2]),
            "us_t": wiki.clean(cols[3]),
            "series": wiki.clean(cols[5]),
            "note": wiki.clean(cols[6]),
        })
    for nv in out:
        assert nv["t"] and nv["y"], nv
    return out, int(box.group(1))


ALSO = re.compile(r"also published as ''([^']+)''(?:\s*and as ''([^']+)'')?", re.I)
US_ALSO = re.compile(r"also published in the United States as ''([^']+)''", re.I)
# the linked, italicised title that OPENS a list bullet. Anchored, because
# several bullets link further titles further along the line and an
# unanchored match once claimed the wrong one.
LINKED = re.compile(r"^[#*]\s*''\[\[(?:[^\]|]*\|)?([^\]]+)\]\]''")


def read_poirot_list():
    """The Poirot article's numbered publication-order list.

    Each entry becomes (title, year, kind, alts) with kind in
    novel/ss/play — the merge order for the Poirot section.
    """
    t = text(POIROT)
    seg = t.split("== Hercule Poirot series in publication order ==")[1]
    seg = re.split(r"\n=+[^=\n]", seg)[0]
    out = []
    for line in seg.splitlines():
        if not line.startswith("# "):
            continue
        m = LINKED.search(line)
        assert m, "unlinked entry in the Poirot list: %r" % line[:70]
        title = m.group(1)
        rest = line[m.end():]
        par = re.match(r"\s*\(([^()]*)\)", rest)
        assert par, "no year bracket on %r" % title
        inner = par.group(1)
        years = re.findall(r"(?:18|19|20)\d{2}", inner)
        assert years, "no year for %r" % title
        kind = ("ss" if re.search(r"\bss\b", inner)
                else "play" if "play" in inner else "novel")
        alts = []
        for a in ALSO.finditer(rest):
            alts += [x for x in a.groups() if x]
        out.append((title, int(years[-1]), kind, alts))
    return out


def read_marple_lists():
    """The Miss Marple article's novels list and its collections list."""
    t = text(MARPLE)
    seg = t.split("===Miss Marple series===")[1]
    novels_seg, rest = seg.split("===Miss Marple short story collections===")
    coll_seg = rest.split("===Continuations by other authors===")[0]

    novels = []
    for line in novels_seg.splitlines():
        if not line.startswith("# "):
            continue
        m = LINKED.search(line)
        assert m, "unlinked Marple novel: %r" % line[:70]
        y = re.search(r"\((\d{4}), Novel\)", line)
        assert y, "Marple list entry is not marked Novel: %r" % line[:70]
        alts = [a.group(1) for a in US_ALSO.finditer(line)]
        novels.append((m.group(1), int(y.group(1)), alts))

    colls, skipped = [], []
    for line in coll_seg.splitlines():
        if not line.startswith("*"):
            continue
        m = LINKED.search(line)
        if not m:
            # the one unlinked bullet is the 1985 omnibus, which reprints
            # collections already rowed above it. Recorded, then dropped.
            skipped.append(line)
            continue
        pub = re.search(r"published (\d{4})", line)
        y = int(pub.group(1)) if pub else year_of(line)
        assert y, "no year on Marple collection %r" % line[:70]
        colls.append((m.group(1), y))
    assert len(skipped) == 1 and "Complete Short Stories" in skipped[0], skipped
    return novels, colls


def stated(page, pattern):
    """A count the article states about itself, as an int."""
    m = re.search(pattern, text(page))
    assert m, "article %r no longer states its own total (%r)" % (page, pattern)
    return int(m.group(1))


def unique_accent(pair):
    """No other property may already own this accent pair."""
    for f in sorted((prop.ROOT / "properties").glob("*.json")):
        if f.stem in (SLUG, "index", "search"):
            continue
        p = json.loads(f.read_text(encoding="utf-8"))
        assert (p.get("accent"), p.get("accentDark")) != pair, \
            "accent pair %s already belongs to %s" % (pair, f.stem)


def join_alts(alts):
    """'Also published as A, B and C' — deduped, source order kept."""
    seen, out = set(), []
    for a in alts:
        k = prop.normt(a)
        if k and k not in seen:
            seen.add(k)
            out.append(a.strip())
    if not out:
        return ""
    if len(out) == 1:
        body = out[0]
    else:
        body = "%s and %s" % (", ".join(out[:-1]), out[-1])
    return "Also published as " + body


def main():
    novels, infobox_novels = read_novels()
    assert len(novels) == infobox_novels == 74, \
        "novels table holds %d rows, infobox says %d" % (len(novels), infobox_novels)

    poirot_list = read_poirot_list()
    marple_novels, marple_colls = read_marple_lists()

    say_poirot = stated(POIROT_CHAR, r"appearing in (\d+) novels")
    say_marple = stated(MARPLE, r"Christie wrote (\d+) novels")

    by_norm = {}
    for nv in novels:
        by_norm.setdefault(prop.normt(nv["t"]), nv)
    assert len(by_norm) == len(novels), "two novels normalise to one title"

    # ---- the two runs, cross-checked against their own articles ----------
    tbl_poirot = [nv for nv in novels if nv["series"] == SER_POIROT]
    tbl_marple = [nv for nv in novels if nv["series"] == SER_MARPLE]
    spine_poirot = [nv for nv in tbl_poirot if nv["t"] != NOVELLA]
    assert len(tbl_poirot) - len(spine_poirot) == 1, \
        "the Greenshore Folly row is no longer in the novels table"

    list_novels = [e for e in poirot_list if e[2] == "novel"]
    list_ss = [e for e in poirot_list if e[2] == "ss"]
    list_play = [e for e in poirot_list if e[2] == "play"]
    assert len(list_play) == 1, "the Poirot list's play count changed"
    assert len(list_ss) == 5, "the Poirot list now marks %d collections" % len(list_ss)
    assert len(list_novels) == len(spine_poirot) == say_poirot == 33, \
        ("Poirot: list %d, table %d, article says %d"
         % (len(list_novels), len(spine_poirot), say_poirot))
    assert ([prop.normt(e[0]) for e in list_novels]
            == [prop.normt(nv["t"]) for nv in spine_poirot]), \
        "the Poirot list and the bibliography table disagree on the run"

    assert len(marple_novels) == len(tbl_marple) == say_marple == 12, \
        ("Marple: list %d, table %d, article says %d"
         % (len(marple_novels), len(tbl_marple), say_marple))
    assert ([(prop.normt(t), y) for t, y, _ in marple_novels]
            == [(prop.normt(nv["t"]), nv["y"]) for nv in tbl_marple]), \
        "the Miss Marple list and the bibliography table disagree on the run"
    assert len(marple_colls) == 6, \
        "the Marple article now lists %d collections" % len(marple_colls)

    # Years are UK first publication, which is how the table is ordered.
    # Four books reached America a year earlier and the notes say "four", so
    # a Wikipedia edit has to break this rather than quietly falsify the
    # sentence. The year gap is never more than one, so UK-year ordering and
    # first-publication ordering never actually disagree by more than a tie.
    us_first = sorted(nv["t"] for nv in novels
                      if nv["us_y"] and nv["us_y"] < nv["y"])
    assert len(us_first) == 4, us_first
    assert "The Mysterious Affair at Styles" in us_first, us_first
    assert all(nv["y"] - nv["us_y"] <= 1 for nv in novels
               if nv["us_y"] and nv["us_y"] < nv["y"]), us_first

    # ---- row assembly ---------------------------------------------------
    used_notes, extra_alts = set(), {}
    for title, _y, _k, alts in poirot_list:
        if alts:
            extra_alts.setdefault(prop.normt(title), []).extend(alts)
    for title, _y, alts in marple_novels:
        if alts:
            extra_alts.setdefault(prop.normt(title), []).extend(alts)

    def novel_row(nv, opt=False):
        alts, frag = [], ""
        if nv["us_t"] and nv["us_t"] != DASH \
                and prop.normt(nv["us_t"]) != prop.normt(nv["t"]):
            alts.append(nv["us_t"])
        if nv["note"] and nv["note"] != DASH:
            key = nv["note"]
            assert key in NOTES_COL, \
                "unreviewed table note on %r: %r" % (nv["t"], key)
            used_notes.add(key)
            more, frag = NOTES_COL[key]
            alts += more
            if key in OPT_NOTE:
                opt = True
        alts += extra_alts.get(prop.normt(nv["t"]), [])
        row = {"id": "ac-%d-%s" % (nv["y"], prop.slug(nv["t"])),
               "t": nv["t"], "n": str(nv["y"])}
        if opt:
            row["opt"] = 1
        note = prop.join_bits(join_alts(alts), frag)
        if note:
            row["note"] = note
        return row

    def coll_row(title, year, alts=()):
        row = {"id": "ac-%d-%s" % (year, prop.slug(title)),
               "t": title, "n": str(year), "opt": 1,
               "note": prop.join_bits("Short stories", join_alts(list(alts)))}
        return row

    # Poirot: the article's own publication-order list, the play dropped,
    # the novella appended at the end where its 2014 publication puts it.
    poirot_items = []
    for title, _ly, kind, alts in poirot_list:
        if kind == "play":
            continue
        if kind == "ss":
            poirot_items.append(coll_row(title, _ly, alts))
        else:
            poirot_items.append(novel_row(by_norm[prop.normt(title)]))
    poirot_items.append(novel_row(by_norm[prop.normt(NOVELLA)], opt=True))

    # Marple: the twelve novels and the six collections, merged by year with
    # the novel first when a year holds both.
    merged = ([(y, 0, novel_row(by_norm[prop.normt(t)])) for t, y, _ in marple_novels]
              + [(y, 1, coll_row(t, y)) for t, y in marple_colls])
    marple_items = [r for _y, _k, r in sorted(merged, key=lambda x: (x[0], x[1]))]

    # Everything else, in the table's own order.
    rest = [nv for nv in novels
            if nv["series"] not in (SER_POIROT, SER_MARPLE)]
    rest_items = [novel_row(nv) for nv in rest]

    assert used_notes == set(NOTES_COL), \
        "table note never matched: %s" % sorted(set(NOTES_COL) - used_notes)

    sections = [
        {"id": "poirot", "title": "Hercule Poirot",
         "sub": "%d novels · %d–%d · plus the collections, optional"
                % (len(spine_poirot), spine_poirot[0]["y"], spine_poirot[-1]["y"]),
         "intro": "Publication order, The Mysterious Affair at Styles to "
                  "Curtain. The five short-story collections sit where they "
                  "were published, marked optional.",
         "open": True,
         "links": [{"label": "The Poirot books",
                    "url": "https://en.wikipedia.org/wiki/"
                           "Hercule_Poirot_in_literature"}],
         "items": poirot_items},
        {"id": "marple", "title": "Miss Marple",
         "sub": "%d novels · %d–%d · plus the collections, optional"
                % (len(tbl_marple), tbl_marple[0]["y"], tbl_marple[-1]["y"]),
         "intro": "Publication order, The Murder at the Vicarage to Sleeping "
                  "Murder, with the collections optional alongside.",
         "links": [{"label": "Miss Marple",
                    "url": "https://en.wikipedia.org/wiki/Miss_Marple"}],
         "items": marple_items},
        {"id": "standalones", "title": "The standalones",
         "sub": "%d novels · %d–%d" % (len(rest), rest[0]["y"], rest[-1]["y"]),
         "intro": "Everything outside the two runs: the one-offs — And Then "
                  "There Were None, Crooked House, Endless Night — and the "
                  "shorter runs for Tommy and Tuppence, Superintendent "
                  "Battle and Colonel Race. The Mary Westmacott romances are "
                  "here too, optional.",
         "links": [{"label": "The bibliography",
                    "url": "https://en.wikipedia.org/wiki/"
                           "Agatha_Christie_bibliography"}],
         "items": rest_items},
    ]

    # ---- the shape of the finished list ---------------------------------
    all_items = [x for s in sections for x in s["items"]]
    novel_rows = [x for x in all_items
                  if prop.normt(x["t"]) in by_norm]
    assert len(novel_rows) == 74, \
        "%d novel rows built from a 74-row table" % len(novel_rows)
    assert len(all_items) == 74 + 5 + 6, len(all_items)
    for s in sections:
        years = [int(x["n"]) for x in s["items"]]
        assert years == sorted(years), \
            "%s is not in publication order at %r" % (s["id"], s["title"])
    # weights are all-or-nothing and here they are none: the front end reads
    # a missing w as one hour, so a single stray weight would misvalue the rest
    assert not any("w" in x for x in all_items), "a row carries a weight"
    assert sum(1 for x in poirot_items if not x.get("opt")) == 33
    assert sum(1 for x in marple_items if not x.get("opt")) == 12
    opt_rest = [x for x in rest_items if x.get("opt")]
    assert len(opt_rest) == 7, len(opt_rest)   # six Westmacotts + the round-robin
    span = [int(x["n"]) for x in all_items if not x.get("opt")]

    accent = ("#1F5138", "#D9B65E")
    unique_accent(accent)

    p = {
        "slug": SLUG,
        "title": "Agatha Christie",
        "subtitle": "Poirot, Marple and the standalones",
        "kind": "books",
        "popularity": 58,
        "year": "%d–%d" % (min(span), max(span)),
        "blurb": "Every Christie novel in publication order — the Poirot "
                 "run, the Marple run, and the standalones. The short-story "
                 "collections ride alongside marked optional, and no row note "
                 "gives anything away.",
        "unit": {"one": "book", "many": "books"},
        "verb": {"base": "read", "past": "read", "ing": "reading"},
        "accent": accent[0],
        "accentDark": accent[1],
        "tiers": False,
        "notes": [
            ["Two runs, then everything else.",
             "Poirot and Marple each get their own section in publication "
             "order. The third holds every other novel Christie wrote: the "
             "standalones, and the shorter runs for Tommy and Tuppence, "
             "Superintendent Battle and Colonel Race."],
            ["The short-story collections are optional.",
             "A collection is a genuinely different sitting from a novel — "
             "a dozen small puzzles instead of one long one — and someone "
             "working through Poirot wants the novels' arc. So the "
             "collections sit in the runs where they were published, marked "
             "optional, rather than mixed into the count. Several of them "
             "hold both detectives; those are rowed once, in the run whose "
             "article claims them."],
            ["Published order, not written order.",
             "Christie wrote Curtain and Sleeping Murder in the 1940s and "
             "locked them away; they came out last, in 1975 and 1976, and "
             "that is where they sit. Publication order is the spine "
             "throughout, because it is the order the books were built to be "
             "met in. Years are UK first publication, the way the "
             "bibliography orders its table; four books reached America a "
             "year earlier, The Mysterious Affair at Styles among them."],
            ["A few other rows are optional too.",
             "The six romances Christie published as Mary Westmacott are in "
             "the bibliography's novels table, so they are here, marked "
             "optional — they are not mysteries. So is The Floating "
             "Admiral, written with the Detection Club. And Hercule Poirot "
             "and the Greenshore Folly, a 1954 novella first published on "
             "its own in 2014, closes the Poirot run: the table carries it, "
             "the count of 33 does not."],
            ["Nothing is weighted, and hours are not tracked.",
             "Every book counts as one and the counter counts books, not "
             "time. Wikipedia does not publish page counts consistently, and "
             "a page count is not an hour anyway — so no row here carries "
             "a reading time and none has been estimated."],
            ["No row gives anything away.",
             "The notes are publication history only: alternative titles, "
             "pen names, when a book was written against when it came out. "
             "Nothing about who, how or why."],
            "Titles, years, series and alternative titles machine-read from "
            "Wikipedia's Agatha Christie bibliography — the novels table, "
            "checked against the article's own count of 74 — with the two "
            "runs verified title by title against the Hercule Poirot and "
            "Miss Marple articles and their own counts of 33 and 12 novels.",
        ],
        "sections": sections,
    }

    out = prop.write(p)
    print("wrote %s — %d rows" % (out.name, len(all_items)))
    for s in sections:
        opt = sum(1 for x in s["items"] if x.get("opt"))
        print("   %-16s %2d rows (%d optional)  %s"
              % (s["title"], len(s["items"]), opt, s["sub"]))
    print("   asserted: 74 novels (infobox), Poirot 33, Marple 12 · unweighted")


if __name__ == "__main__":
    main()
