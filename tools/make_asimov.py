#!/usr/bin/env python3
"""Generate properties/asimov.json — Asimov's merged future history.

    python tools/make_asimov.py

Robot + Empire + Foundation, the three series Asimov himself welded into one
future history, as one spine. The list exists to make a ruling on a real
argument — publication order or the internal chronology Asimov stitched
together afterwards — and it rules for publication order, because the later
books were written to recontextualise the earlier ones. The chronological
sequence is offered in a note, not as a second list.

Section order is deliberately NOT the chronological one. The chronology runs
Robot -> Empire -> Foundation, so sectioning that way would quietly ship the
order this page argues against. Sections here run Foundation -> Robot ->
Empire, and inside each section rows are strictly by year of publication —
which is where the two orders actually differ: the chronology puts the
Foundation prequels first and reshuffles the Empire trio.

Nothing is typed from memory. Every title, year and series membership is read
out of wikitext cached under scratch/asimov/:

  Foundation universe          the narrative-chronological list of the whole
                               merged history, and what it excludes
  Foundation (novel series)    the infobox book list — Asimov's seven, and
                               the three by other authors it also files here
  Robot series                 the novels, their Baley/Olivaw numbering, and
                               the lead's own count
  Galactic Empire series       the three Empire novels and their years

NO WEIGHTS. Not one row carries `w`, on purpose: the reader-side weight rule
is `WEIGHT = x.w >= 0 ? x.w : 1`, so a single weighted row would silently
redefine every unweighted row as one hour. Page counts differ by edition and a
page is not an hour, so this page tracks books and says so in the notes.
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop, wiki  # noqa: E402

SLUG = "asimov"
ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "scratch" / "asimov"

PAGES = {
    "universe": "Foundation universe",
    "foundation": "Foundation (novel series)",
    "robot": "Robot series",
    "empire": "Galactic Empire series",
}

WORDNUM = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
           "eight": 8, "nine": 9, "ten": 10}
ORDINAL = {"first": 1, "second": 2, "third": 3, "fourth": 4}

# `''[[Page|Label]]'' (1954)` — italic wikilink plus year. Short stories in
# these lists are quoted rather than italicised, so this never picks one up.
BOOK = re.compile(r"''\[\[([^\]|]+)(?:\|([^\]]+))?\]\]''\s*\((\d{4})\)")

ACCENT, ACCENT_DARK = "#3D4C86", "#E3B84C"


def page(key):
    text = wiki.wikitext(PAGES[key], cache_dir=CACHE)
    assert text, "could not read %s" % PAGES[key]
    return text


def linked(m):
    """Display title of a BOOK match: the pipe label if there is one."""
    return (m.group(2) or m.group(1)).strip()


# ---------------------------------------------------------------- sources

def chronological(universe):
    """(title, year) for every NOVEL in the Foundation universe article's
    narrative-chronological list, in that article's order."""
    seg = universe.split("The following works are listed in chronological "
                         "order by narrative:")[1].split("==== Timeline ====")[0]
    out = []
    for line in seg.strip().split("\n"):
        if not line.startswith("#"):
            continue
        body = line.lstrip("#").strip()
        m = BOOK.match(body)
        if m:
            out.append((linked(m), int(m.group(3))))
    assert len(out) >= 15, out
    return out


def foundation_books(text):
    """The infobox's own book list, split into Asimov's and other authors'."""
    m = re.search(r"\|\s*books\s*=\s*\{\{Plainlist\|(.*?)\n\}\}", text, re.S)
    assert m, "Foundation infobox book list not found"
    groups, current = {}, None
    for line in m.group(1).strip().split("\n"):
        line = line.strip()
        head = re.match(r"^\*\s*'''(?:\[\[)?([^'\]]+?)(?:\]\])?'''\s*:", line)
        if head:
            current = head.group(1).strip()
            groups[current] = []
            continue
        b = BOOK.search(line)
        if b and current:
            by = re.search(r"by \[\[([^\]|]+)(?:\|[^\]]+)?\]\]", line)
            groups[current].append((linked(b), int(b.group(3)),
                                    by.group(1).strip() if by else None))
    assert set(groups) == {"Isaac Asimov", "Other authors"}, sorted(groups)
    return groups["Isaac Asimov"], groups["Other authors"]


def foundation_shape(text):
    """Which of Asimov's seven the lead calls trilogy / sequel / prequel."""
    lead = text.split("==Publication history==")[0]
    tri = re.search(r"in (\w+) novels in 1951[^.]*?:(.*?)\. It won", lead, re.S)
    later = re.search(r"with (\w+) sequels?,(.*?), and (\w+) prequels?,(.*?)\.",
                      lead, re.S)
    assert tri and later, "Foundation lead sentence did not parse"
    shape = {}
    for label, blob, want in (
            ("The original trilogy", tri.group(2), WORDNUM[tri.group(1)]),
            ("Sequel", later.group(2), WORDNUM[later.group(1)]),
            ("Prequel", later.group(4), WORDNUM[later.group(3)])):
        hits = [linked(m) for m in BOOK.finditer(blob)]
        assert len(hits) == want, (label, hits, want)
        for t in hits:
            shape[t] = label
    return shape


def robot_books(text, universe):
    """I, Robot plus the four Baley/Olivaw novels plus The Positronic Man,
    each with the label the article gives it. The Silverberg credit comes
    from the Foundation universe article, which is where it is spelled out."""
    lead = text.split("==Novels and stories==")[0]
    nm = re.search(r"and (\w+) \[\[novel series\|novels\]\]", lead)
    assert nm, "Robot lead novel count not found"
    stated = WORDNUM[nm.group(1)]

    seg = text.split("chronological order by narrative ===")[1] \
              .split("=== Overview of short stories ===")[0]
    baley = []
    for line in seg.strip().split("\n"):
        if not line.startswith("#"):
            continue
        body = line.lstrip("#").strip()
        m = BOOK.match(body)
        if not m:
            continue
        ord_m = re.search(r"-\s*(first|second|third|fourth) Robot series/"
                          r"R\. Daneel Olivaw novel", body)
        if ord_m:
            baley.append((linked(m), int(m.group(3)),
                          ORDINAL[ord_m.group(1)]))
    assert [b[2] for b in baley] == [1, 2, 3, 4], baley

    ov = text.split("=== Overview of the Robot Novels ===")[1]
    fm = re.match(r"\s*The first book is ''\[\[([^\]|]+)\]\]'' \((\d{4})\), "
                  r"a collection of (\w+) previously published short stories",
                  ov)
    assert fm, "Robot novels overview did not parse"
    first = (fm.group(1).strip(), int(fm.group(2)), WORDNUM[fm.group(3)])

    pm = re.search(r"''\[\[The Positronic Man\]\]'' \((\d{4})\) - short story "
                   r"and related subsequent novel", text)
    sv = re.search(r"''\[\[The Positronic Man\]\]'' \(\d{4}\)[^\n]*?written "
                   r"by \[\[([^\]|]+)\]\][^\n]*?based on Asimov's (\d{4}) "
                   r"\[\[Short story\|novelette\]\]", universe)
    return stated, first, baley, pm, sv


def empire_books(text):
    """The three Empire novels, and the lead's own count of them."""
    lead = text.split("==Works in the series==")[0]
    cm = re.search(r"sequence\]\] of (\w+) of \[\[Isaac Asimov\]\]'s "
                   r"earliest \[\[novel\]\]s", lead)
    assert cm, "Empire lead novel count not found"
    seg = text.split("==Works in the series==")[1] \
              .split("==Publication history==")[0]
    out = []
    for line in seg.strip().split("\n"):
        if not line.startswith("#"):
            continue
        body = line.lstrip("#").strip()
        m = BOOK.match(body)
        if m and re.search(r"\),\s*(?:his first )?novel\b", body):
            out.append((linked(m), int(m.group(3)),
                        "his first novel" in body))
    return WORDNUM[cm.group(1)], out


# ---------------------------------------------------------------- assembly

def row(title, year, note="", opt=0):
    it = {"id": "asi-%d-%s" % (year, prop.slug(title)), "t": title,
          "n": str(year)}
    if note:
        it["note"] = note
    if opt:
        it["opt"] = 1
    return it


def accent_is_free():
    """No other property may already own this accent pair (qa_lint rejects
    duplicates, and a shared pair makes two lists look like one)."""
    for f in sorted((ROOT / "properties").glob("*.json")):
        if f.stem in (SLUG, "index", "search"):
            continue
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(d, dict):
            continue
        assert (d.get("accent"), d.get("accentDark")) != (ACCENT, ACCENT_DARK), \
            "accent pair already used by %s" % f.stem
    return True


def main():
    universe = page("universe")
    chron = chronological(universe)
    chron_year = dict(chron)

    asimov_f, others_f = foundation_books(page("foundation"))
    shape = foundation_shape(page("foundation"))
    r_stated, r_first, r_baley, r_pm, r_sv = robot_books(page("robot"), universe)
    e_stated, empire = empire_books(page("empire"))

    # --- counts against each source's own stated totals
    assert len(asimov_f) == 7, asimov_f            # 3 trilogy + 2 + 2, below
    assert len(shape) == 7, sorted(shape)
    assert {t for t, _, _ in asimov_f} == set(shape), "Foundation lead/infobox"
    assert len(others_f) == 3 and all(a for _, _, a in others_f), others_f
    assert e_stated == len(empire) == 3, (e_stated, empire)
    assert r_pm and r_sv, "The Positronic Man rows did not parse"
    robot_rows = 1 + len(r_baley) + 1                  # I, Robot + Baley + PM
    assert robot_rows == r_stated == 6, (robot_rows, r_stated)

    # --- every year must agree with the Foundation universe article
    for t, y in ([(r_first[0], r_first[1])]
                 + [(t, y) for t, y, _ in r_baley]
                 + [(t, y) for t, y, _ in empire]
                 + [(t, y, ) for t, y, _ in asimov_f]
                 + [("The Positronic Man", int(r_pm.group(1)))]):
        assert chron_year.get(t) == y, "year disagreement: %s %s vs %s" % (
            t, y, chron_year.get(t))

    # --- rows, publication order inside every section
    f_items = [row(t, y, shape[t] + (
        " · written last, and it belongs last" if shape[t] == "Prequel"
        else ""))
        for t, y, _ in sorted(asimov_f, key=lambda x: x[1])]

    spelled = {v: k for k, v in WORDNUM.items()}
    r_items = [row(r_first[0], r_first[1],
                   "Fixup novel — %s early robot stories woven together"
                   % spelled[r_first[2]])] + [
        row(t, y, "Baley and Olivaw, novel %d" % n)
        for t, y, n in sorted(r_baley, key=lambda x: x[1])]

    e_items = [row(t, y, "Asimov's first published novel" if first else "")
               for t, y, first in sorted(empire, key=lambda x: x[1])]

    c_items = [row("The Positronic Man", int(r_pm.group(1)),
                   "With %s · expands Asimov's %s novelette"
                   % (r_sv.group(1), r_sv.group(2)), opt=1)] + [
        row(t, y, a, opt=1) for t, y, a in sorted(others_f, key=lambda x: x[1])]

    spine = {x["t"] for x in f_items + r_items + e_items}
    assert len(spine) == 15, sorted(spine)

    # the chronological alternative, read off the article rather than recalled
    chron_spine = [t for t, _ in chron if t in spine]
    assert len(chron_spine) == 15, chron_spine
    assert chron_spine[0] == r_first[0] and chron_spine[-1] == "Foundation and Earth"
    assert chron_spine != [x["t"] for x in f_items + r_items + e_items], \
        "the two orders came out identical — something is wrong"
    chron_text = " → ".join(chron_spine)

    sections = [
        {"id": "foundation", "title": "Foundation",
         "sub": "1951–1993 · seven novels · publication order",
         "open": True,
         "intro": "The trilogy, then the two sequels Asimov wrote thirty "
                  "years later, then the two prequels he finished with. "
                  "Every one of them was written for a reader who had "
                  "already read the ones before it.",
         "items": f_items},
        {"id": "robot", "title": "The Robot novels",
         "sub": "1950–1985 · five books · publication order",
         "intro": "A fixup of the early robot stories, then four detective "
                  "novels starring Elijah Baley and R. Daneel Olivaw — "
                  "the last two written decades after the first two, once "
                  "Asimov had decided all of this was one history.",
         "items": r_items},
        {"id": "empire", "title": "The Empire novels",
         "sub": "1950–1952 · three books · publication order",
         "intro": "Asimov's earliest novels, and the thinnest connection of "
                  "the three series: each is a complete story on its own, "
                  "tied to the rest by setting rather than by plot. They sit "
                  "last here because they are the least load-bearing, not "
                  "because they come last.",
         "items": e_items},
        {"id": "continuations", "title": "Not Asimov alone",
         "sub": "1992–1999 · four books · optional",
         "intro": "Books the source files with these series but Asimov did "
                  "not write by himself. Optional rows: tick them or ignore "
                  "them, nothing here depends on them.",
         "items": c_items},
    ]

    for s in sections:
        ys = [int(x["n"]) for x in s["items"]]
        assert ys == sorted(ys), (s["id"], ys)          # non-decreasing years
    all_items = [x for s in sections for x in s["items"]]
    assert len(all_items) == 19, len(all_items)
    assert not any("w" in x for x in all_items), "a weight got in"
    assert sum(1 for x in all_items if x.get("opt")) == 4
    accent_is_free()

    blurb = ("Isaac Asimov's Foundation, Robot and Empire novels as one "
             "future history, in the order he published them — which is "
             "the order that keeps the later books' surprises intact.")
    assert not re.search(r"\d", blurb), "no counts in the blurb (CLU-190)"

    p = {
        "slug": SLUG,
        "title": "The Foundation universe",
        "subtitle": "Isaac Asimov — Foundation, Robot and Empire",
        "kind": "books",
        "popularity": 52,
        "year": "1950–1999",
        "blurb": blurb,
        "unit": {"one": "book", "many": "books"},
        "verb": {"base": "read", "past": "read", "ing": "reading"},
        "accent": ACCENT,
        "accentDark": ACCENT_DARK,
        "tiers": False,
        "notes": [
            ["Publication order, not chronology.",
             "Asimov wrote these as three separate series across forty years "
             "and only merged them into a single future history late on. The "
             "later books exist to recast the earlier ones, so the internal "
             "chronology hands you answers before you have met the "
             "questions — most obviously the two Foundation prequels, "
             "which were written last and explain things the original "
             "trilogy is still busy setting up. Read them as they arrived."],
            ["The chronological order, if you want it anyway.",
             "For the books on this page it runs: " + chron_text + ". That "
             "is a good second pass and a poor first one. It is offered "
             "here as a note rather than a second list — there is one "
             "list on this page, and the boxes do not mind what order you "
             "tick them in."],
            ["The sections are the three series; the order is publication.",
             "Rows run by year of publication inside every section, which is "
             "where the two orders actually part company: the chronology "
             "moves the Foundation prequels to the front and reshuffles the "
             "Empire trio. The sections themselves are led by Foundation "
             "because it is the reason most people are here, and deliberately "
             "not by the chronology, which would run Robot, Empire, "
             "Foundation."],
            ["Four optional rows Asimov did not write alone.",
             "Wikipedia's Foundation series infobox files Foundation's Fear, "
             "Foundation and Chaos and Foundation's Triumph — by "
             "Gregory Benford, Greg Bear and David Brin — among the "
             "series' books, and the Robot series article files The "
             "Positronic Man, which Robert Silverberg expanded from an "
             "Asimov novelette. They are here because the source puts them "
             "here, marked optional because they are not his. Skip all four "
             "and you have missed nothing the rest of the page needs."],
            ["Novels only.",
             "The robot short stories and the collections that hold them are "
             "out — I, Robot is here because it is a novel-length fixup "
             "and the series' first book, not as a stand-in for the "
             "collections. So is the Empire short story Blind Alley, and so "
             "are Nemesis and The End of Eternity, which the source treats "
             "as adjacent rather than part of the series. The Robot City, "
             "Robots and Aliens and Robots in Time novels, Roger MacBride "
             "Allen's Caliban trilogy, the Tiedemann robot mysteries and the "
             "Reichert I, Robot prequels are all outside what the articles "
             "count as these series."],
            ["Hours are not tracked.",
             "Every book counts as one and nothing on this page is weighted. "
             "Page counts differ by edition, a page is not an hour, and one "
             "weighted row would quietly turn every other row into an hour "
             "— so there are none at all."],
            "Titles, years, series membership and the chronological ordering "
            "read from Wikipedia's Foundation universe, Foundation (novel "
            "series), Robot series and Galactic Empire series articles.",
        ],
        "sections": sections,
    }

    out = prop.write(p)
    print("wrote %s — %d rows (%d optional)"
          % (out.name, len(all_items),
             sum(1 for x in all_items if x.get("opt"))))
    for s in sections:
        print("   %-18s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))
    print("   chronological alternative: %s … %s"
          % (chron_spine[0], chron_spine[-1]))


if __name__ == "__main__":
    main()
