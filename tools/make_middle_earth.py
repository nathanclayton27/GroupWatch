#!/usr/bin/env python3
"""Generate properties/middle-earth.json.

    python tools/make_middle_earth.py

Two sections. Books: The Hobbit, The Lord of the Rings as three volume
rows, The Silmarillion, then the four posthumous narrative volumes as
optional rows — years and Christopher Tolkien credits from the Middle-earth
section of Wikipedia's J. R. R. Tolkien bibliography. Films: Peter
Jackson's six, weighted by theatrical runtime, each row noting its extended
edition factually — both figures from the film-series articles' own length
tables, theatrical cuts cross-checked against Wikidata P2047.

Book rows are unweighted (pages aren't hours). The Rings of Power is not a
row; the notes say so. Data: tools/data/middle-earth.json, built and
asserted by scratch/agent-books/parse_middle_earth.py.
"""
import json
import pathlib

SLUG = "middle-earth"

OPT_BOOKS = {"Unfinished Tales", "The Children of Húrin",
             "Beren and Lúthien", "The Fall of Gondolin"}
LOTR_VOLS = {"The Fellowship of the Ring": 1, "The Two Towers": 2,
             "The Return of the King": 3}


def slugify(t):
    t = t.replace("'", "")
    keep = "".join(c.lower() if c.isalnum() else "-" for c in t)
    keep = keep.encode("ascii", "ignore").decode("ascii")
    while "--" in keep:
        keep = keep.replace("--", "-")
    return keep.strip("-")


def main():
    here = pathlib.Path(__file__).resolve().parent
    d = json.loads((here / "data" / "middle-earth.json")
                   .read_text(encoding="utf-8"))
    books, films = d["books"], d["films"]
    assert len(books) == 9 and len(films) == 6

    book_items = []
    for b in books:
        it = {"id": "me-%d-%s" % (b["year"], slugify(b["title"])),
              "t": b["title"], "n": str(b["year"])}
        bits = []
        if b["title"] in LOTR_VOLS:
            bits.append("The Lord of the Rings, volume %d"
                        % LOTR_VOLS[b["title"]])
        if b["christopher"]:
            bits.append("edited by Christopher Tolkien")
        if b["title"] in OPT_BOOKS:
            it["opt"] = 1
        if bits:
            it["note"] = " · ".join(bits)
        book_items.append(it)

    film_items = []
    for f in films:
        film_items.append({
            "id": "me-f-%d-%s" % (f["year"], slugify(f["title"])),
            "t": f["title"], "n": str(f["year"]),
            "w": round(f["theatrical"] / 60.0, 2),
            "note": "%d min · extended edition %d min"
                    % (f["theatrical"], f["extended"])})

    hours = sum(x["w"] for x in film_items)
    sections = [
        {"id": "books", "title": "The books",
         "sub": "1937–2018 · Tolkien on the page", "open": True,
         "intro": "The Hobbit, then The Lord of the Rings volume by "
                  "volume, then The Silmarillion. The four later volumes "
                  "Christopher Tolkien assembled from his father's papers "
                  "are optional rows — deep water, entered knowingly.",
         "items": book_items},
        {"id": "films", "title": "Jackson's six",
         "sub": "2001–2014 · about %.0f hours theatrical" % hours,
         "intro": "Weighted by theatrical runtime; every row notes its "
                  "extended edition. Watch either cut — the tick doesn't "
                  "ask which.",
         "items": film_items},
    ]

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == 15 and len(set(ids)) == 15
    assert all(i == slugify(i) and i.isascii() for i in ids)
    opts = [x["t"] for x in book_items if x.get("opt")]
    assert set(opts) == OPT_BOOKS, opts
    assert not any("w" in x for x in book_items)
    assert 17.0 < hours < 17.4, hours  # 557 + 474 = 1031 min

    prop = {
        "slug": SLUG,
        "title": "Middle-earth",
        "subtitle": "Tolkien's books and Jackson's films",
        "kind": "books & films",
        "order": 109,
        "year": "1937–2014",
        "blurb": "The Hobbit to The Silmarillion with the posthumous "
                 "volumes optional, and Peter Jackson's six films weighted "
                 "by runtime — the page and the screen, one list.",
        "unit": {"one": "entry", "many": "entries"},
        "verb": {"base": "read", "past": "done", "ing": "working through"},
        "accent": "#4A6B2A",
        "accentDark": "#E3C060",
        "tiers": False,
        "notes": [
            ["The Lord of the Rings is three rows.",
             "One per volume, 1954–55, so a winter spent inside The Two "
             "Towers still moves the bar. The Hobbit and The Silmarillion "
             "are one row each."],
            ["The posthumous four are optional.",
             "Unfinished Tales, The Children of Húrin, Beren and Lúthien "
             "and The Fall of Gondolin — all edited by Christopher Tolkien "
             "from his father's papers, all opt rows. The History of "
             "Middle-earth series is scholarship beyond even that, and is "
             "not here."],
            ["Films are weighted, books are not.",
             "Film rows use theatrical runtimes from Wikipedia's own "
             "length tables — about 9 hours for The Lord of the Rings "
             "plus 8 for The Hobbit — and each row notes its extended "
             "edition. Book rows count one each; pages aren't hours."],
            ["No Rings of Power.",
             "This list is Tolkien's page and Jackson's screen. The "
             "Amazon series is neither, and is left out on purpose."],
            "Books and years from Wikipedia's J. R. R. Tolkien "
            "bibliography; film lengths from The Lord of the Rings and "
            "The Hobbit film-series articles, cross-checked against "
            "Wikidata.",
        ],
        "sections": sections,
    }

    out = here.parent / "properties" / ("%s.json" % SLUG)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json — %d rows (%d books, %d films, %.1fh theatrical)"
          % (SLUG, len(ids), len(book_items), len(film_items), hours))
    for s in sections:
        print("   %-14s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
