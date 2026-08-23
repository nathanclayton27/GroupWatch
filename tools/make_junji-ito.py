#!/usr/bin/env python3
"""Generate properties/junji-ito.json.

    python tools/make_junji-ito.py

A reading list of the major works — one row per book as published in
English, n = year. Rows come from tools/data/junji-ito.json, built by
scratch/agent-anime/harvest_ito.py: every English title is asserted present
in the Works section of Wikipedia's Junji Ito article (the bibliography),
and every year is machine-read — from the work's own article's infobox
where one exists, otherwise from the Japanese Wikipedia works table via the
exact Japanese title the bibliography gives. The bibliography article
itself carries no years, so a year here is the work's first Japanese
appearance: a serial's first chapter, a one-shot's magazine issue, a
curated book's Japanese release.

Unweighted: a book is a book.
"""
import json
import pathlib

SLUG = "junji-ito"

DATA = pathlib.Path(__file__).resolve().parent / "data" / (SLUG + ".json")
OUT = pathlib.Path(__file__).resolve().parent.parent / "properties" / (SLUG + ".json")

BIB = [{"label": "The bibliography",
        "url": "https://en.wikipedia.org/wiki/Junji_Ito#Works"}]

SECTIONS = [
    ("long", "The long works",
     "One story per book: the serialized works and the two literary "
     "adaptations (Frankenstein, No Longer Human)."),
    ("coll", "The collections",
     "The short stories as the current English books collect them. Where "
     "a book is named for one story, the year is that story's first run."),
    ("odd", "The oddities",
     "The autobiographical cat comic and the art book."),
]


def slug(t):
    keep = "".join(c.lower() if c.isalnum() else "-" for c in t)
    while "--" in keep:
        keep = keep.replace("--", "-")
    return keep.strip("-")


def main():
    rows = json.loads(DATA.read_text(encoding="utf-8"))

    sections = []
    for key, title, intro in SECTIONS:
        got = sorted((r for r in rows if r["section"] == key),
                     key=lambda r: (r["year"], r["t"]))
        assert got, key
        items = [{"id": "ito-%d-%s" % (r["year"], slug(r["t"])),
                  "t": r["t"], "n": str(r["year"]), "note": r["note"]}
                 for r in got]
        sec = {"id": key, "title": title,
               "sub": "%d–%d · %d books"
                      % (got[0]["year"], got[-1]["year"], len(got)),
               "intro": intro, "links": BIB, "items": items}
        sections.append(sec)
    sections[0]["open"] = True

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert len(ids) == len(rows) == 22, len(ids)

    prop = {
        "slug": SLUG,
        "title": "Junji Ito",
        "subtitle": "a reading list of the major works",
        "kind": "manga",
        "order": 88,
        "year": "1987–2020",
        "blurb": "Tomie to The Liminal Zone — %d books: the long works, "
                 "the story collections, and two oddities." % len(ids),
        "unit": {"one": "book", "many": "books"},
        "verb": {"base": "read", "past": "read", "ing": "reading"},
        "accent": "#1B1B1B",
        "accentDark": "#E9E4D8",
        "tiers": False,
        "notes": [
            ["One row per book as published in English.", "The Viz "
             "hardcovers and their peers. The same stories exist in older "
             "out-of-print editions — Museum of Terror, the Horror Comic "
             "Collection, Flesh-Colored Horror — and those are not "
             "separate rows."],
            ["Years are first Japanese appearance.", "The bibliography "
             "article carries no dates, so each year is machine-read from "
             "the work's own article or the Japanese Wikipedia works "
             "table: a serial's first chapter, a title story's magazine "
             "issue, a curated book's Japanese release. The English books "
             "themselves are mostly recent."],
            ["Left off.", "Reprint lines and superseded editions, sequel "
             "volumes (The Liminal Zone Vol. 2), the specials and "
             "uncollected one-shots, and two deep cuts the list does not "
             "chase: Rasputin the Patriot and A Diary of Embellished "
             "Patches."],
            "Titles verified against the Works section of Wikipedia's "
            "Junji Ito article; a row whose year could not be verified "
            "would fail the build rather than ship a guess.",
        ],
        "sections": sections,
    }

    with OUT.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json — %d books" % (SLUG, len(ids)))
    for s in sections:
        print("   %-16s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
