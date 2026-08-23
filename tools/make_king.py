#!/usr/bin/env python3
"""Generate properties/stephen-king.json.

    python3 tools/make_king.py

Every Stephen King novel in publication order, sectioned by decade —
including the seven published as Richard Bachman, which are marked. Story
collections, standalone novellas shelved elsewhere, nonfiction, children's
books and graphic novels are excluded; the list is exactly the Novels table
of Wikipedia's "Stephen King bibliography", via tools/data/king.json
(fetched and verified by scratch/king/fetch_wiki.py + parse_wiki.py).

The list is unweighted: page counts vary by edition and pretending to know
the hours would be worse, so each novel counts as one.

The Dark Tower books are the connected spine and carry "Dark Tower N of 8".
Row notes otherwise say only what the bibliography table says — pen names,
co-writers, declared sequels and twins. No connections from memory.

The generator asserts the total against the article's own infobox count and
refuses to build if any note transform below fails to match; a Wikipedia
edit therefore breaks the build loudly instead of drifting silently. (The
article's lead says "67 novels/novellas" while its infobox and table say 69
— the two extras being the Uncut Stand, kept as an optional row, and the
still-serializing The End Times.)
"""
import json
import pathlib

SLUG = "stephen-king"

# Single-fragment rewrites, applied verbatim. Keys must match the cleaned
# table fragments in king.json exactly; main() asserts every one was used.
TRANSFORM = {
    "First novel published under pseudonym Richard Bachman, now out of "
    "print at the author's request":
        "as Richard Bachman · out of print at the author's request",
    "Published under pseudonym Richard Bachman": "as Richard Bachman",
    "First novel in the Bill Hodges Trilogy": "Bill Hodges 1 of 3",
    "Second novel in the Bill Hodges Trilogy": "Bill Hodges 2 of 3",
    "Third novel in the Bill Hodges Trilogy": "Bill Hodges 3 of 3",
    "The eighth Dark Tower novel, but chronologically set between the "
    "fourth and fifth volumes": "set between books 4 and 5",
}

# Fragments allowed through untouched. Anything not listed anywhere raises,
# so a changed table cannot slip an unreviewed note into the page.
KEEP = {
    "Written with Peter Straub",
    "Written with Owen King",
    "Written with Richard Chizmar",
    "Sequel to The Shining",
    "Twin novel of The Regulators",
    "Illustrated by Bernie Wrightson",
    "First published as a limited edition in 1984, then for the mass "
    "market in 1987",
}

# Whole-note overrides for rows whose table fragments read poorly verbatim.
# Keyed by table title; main() asserts every key was found.
OVERRIDE = {
    "The Stand: The Complete and Uncut Edition":
        "The 1978 novel complete and uncut — its own row in the "
        "bibliography, optional here",
    "The Regulators":
        "as Richard Bachman · twin novel of Desperation",
    "Black House":
        "Written with Peter Straub · sequel to The Talisman",
    "Gwendy's Final Task":
        "Written with Richard Chizmar · the third Gwendy book",
    "The End Times":
        "Serialized, written with Benjamin Percy as Claudia Inez Bachman · "
        "collected edition due 2027",
    "Other Worlds Than These":
        "Written with Peter Straub · the third Talisman book",
}

OPTIONAL = {"The Stand: The Complete and Uncut Edition"}


def slug(t):
    """ASCII-fold a title into an id fragment."""
    t = t.replace("'", "").replace("’", "")
    keep = "".join(c.lower() if c.isalnum() else "-" for c in t)
    keep = keep.encode("ascii", "ignore").decode("ascii")
    while "--" in keep:
        keep = keep.replace("--", "-")
    return keep.strip("-")


def main():
    here = pathlib.Path(__file__).resolve().parent
    data = json.loads((here / "data" / "king.json").read_text(encoding="utf-8"))
    novels = data["novels"]

    used_t, used_o = set(), set()

    def item(nv):
        frags = []
        if nv["dark_tower"]:
            frags.append("Dark Tower %d of 8" % nv["dark_tower"])
        if nv["title"] in OVERRIDE:
            used_o.add(nv["title"])
            frags.append(OVERRIDE[nv["title"]])
        else:
            for f in nv["notes"]:
                if f in TRANSFORM:
                    used_t.add(f)
                    frags.append(TRANSFORM[f])
                elif f in KEEP:
                    frags.append(f)
                else:
                    raise SystemExit("unreviewed table note on %r: %r"
                                     % (nv["title"], f))
        it = {"id": "king-%d-%s" % (nv["year"], slug(nv["title"])),
              "t": nv["title"], "n": nv["n"]}
        if nv["title"] in OPTIONAL:
            it["opt"] = 1
        if frags:
            it["note"] = " · ".join(frags)
        return it

    assert used_o | set(OPTIONAL) <= {nv["title"] for nv in novels}
    nb = sum(1 for nv in novels if nv["bachman"])

    sections = []
    for decade in range(1970, 2030, 10):
        got = [nv for nv in novels if decade <= nv["year"] < decade + 10]
        assert got, decade
        sub = "%d–%d · %d novels" % (got[0]["year"],
                                     max(nv["year"] for nv in got), len(got))
        db = sum(1 for nv in got if nv["bachman"])
        if db:
            sub += " · %d as Bachman" % db
        sec = {"id": "d%02d" % (decade % 100), "title": "The %ds" % decade,
               "sub": sub, "items": [item(nv) for nv in got]}
        if decade == 1970:
            sec["open"] = True
        sections.append(sec)

    # every transform and override matched something — a silent no-op here
    # has caused real outages elsewhere in this repo
    assert used_t == set(TRANSFORM), set(TRANSFORM) - used_t
    assert used_o == set(OVERRIDE), set(OVERRIDE) - used_o

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert all(i == slug(i) and i.isascii() for i in ids), "non-folded id"

    # the total, against the article's own count
    assert len(ids) == len(novels) == data["infobox_novels"], \
        (len(ids), len(novels), data["infobox_novels"])
    assert nb == data["lead_bachman"] == 7, nb
    spine = [x for s in sections for x in s["items"]
             if x.get("note", "").startswith("Dark Tower ")]
    assert len(spine) == 8 and "Dark Tower 8 of 8" in spine[-1]["note"]

    first, last = novels[0], novels[-1]
    prop = {
        "slug": SLUG,
        "title": "Stephen King",
        "subtitle": "all %d novels, Bachman included" % len(novels),
        "kind": "books",
        "order": 54,
        "year": "%d–%d" % (first["year"], last["year"]),
        "blurb": "Every novel in publication order, %s to %s — %d of them, "
                 "the seven Richard Bachman books included, each counting "
                 "as one." % (first["title"], last["title"], len(novels)),
        "unit": {"one": "novel", "many": "novels"},
        "verb": {"base": "read", "past": "read", "ing": "reading"},
        "accent": "#4A1F1F",
        "accentDark": "#C97070",
        "tiers": False,
        "notes": [
            ["Novels only, as Wikipedia draws the line.",
             "This is the bibliography's novels table, whole — %d rows. "
             "Story collections, standalone novellas shelved elsewhere, "
             "nonfiction, children's books and graphic novels are out. A "
             "few short books the table counts as novels — Cycle of the "
             "Werewolf, Elevation, the Gwendy books — stay in because the "
             "table says so." % len(novels)],
            ["The Bachman books are here.",
             "Seven novels came out under the pen name Richard Bachman; "
             "they sit in publication order with everything else, marked "
             "“as Richard Bachman”."],
            ["The Dark Tower is the spine.",
             "Eight books, marked “Dark Tower N of 8”, read here "
             "in publication order. The eighth, The Wind Through the "
             "Keyhole, arrived last but sits between books 4 and 5 in the "
             "story."],
            ["The Stand appears twice.",
             "The bibliography lists the 1990 Complete & Uncut Edition as "
             "its own row, so it is one here too — marked optional, since "
             "it is the 1978 novel restored rather than a new one."],
            ["Nothing is weighted.",
             "An eleven-hundred-page novel and a slim one each count as "
             "one. Page counts differ by edition, and pretending to know "
             "the hours would be worse."],
            "Titles, years and notes from Wikipedia's Stephen King "
            "bibliography — the novels table, verified against the "
            "article's own count of %d." % data["infobox_novels"],
        ],
        "sections": sections,
    }

    out = here.parent / "properties" / ("%s.json" % SLUG)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json" % SLUG)
    print("  %d novels (%d as Bachman, 8 Dark Tower), %s"
          % (len(ids), nb, prop["year"]))
    for s in sections:
        print("   %-9s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
