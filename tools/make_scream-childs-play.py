#!/usr/bin/env python3
"""Generate properties/scream-childs-play.json.

    PYTHONIOENCODING=utf-8 python tools/make_scream-childs-play.py

The two slasher franchises `slashers` deliberately left out, in one list.
Every row is a released theatrical or home-video feature taken from its
franchise's own Films table on Wikipedia, weighted by the runtime that film's
own article infobox states.

WHY THIS LIST EXISTS
--------------------
`tools/make_slashers.py` covers Halloween, Friday the 13th and A Nightmare on
Elm Street — three franchises whose timelines contradict each other, so that
list exists to rule on ordering. Its notes name Scream and Child's Play as the
two long slasher franchises it excluded, and gives a reason for each. This
list closes that gap, and RE-ASSERTS both reasons against the same articles
rather than inheriting them on trust:

  * Scream — seven released films, 1996 to 2026, one unbroken timeline. No
    story-chronology box on the article, no continuity blocks in the Films
    table, no remake, no reboot. The tangle `slashers` exists to untangle
    never arises here, which is exactly why these films sit on this list
    instead of that one. check_source() asserts the box and the blocks are
    still absent.
  * Child's Play — eight released films, and the article's own Films table
    splits them into exactly two labelled blocks, "Original series" and
    "Reboot", which never intersect. A clean fork rather than a tangle.
    check_source() asserts groups == ["Original series", "Reboot"] still
    holds, and every Child's Play row carries the block the table puts it in.

SHAPE
-----
One list, two sections, ordered by the year each franchise began — Child's
Play 1988, then Scream 1996 — with U.S. release order inside each section.
That is the same shape as `slashers`, so the sibling lists read alike. The
Child's Play blocks are LABELLED per row from the article's own grouping and
never imposed as sequence: the label says which of two lines a film belongs
to, not where it falls in one.

THE TELEVISION SERIES ARE OUT, MECHANICALLY
-------------------------------------------
The original Chucky line continues in the Chucky television series, and
Scream had an anthology series of its own; neither is a row. The reason is
weighting, not taste: weights in this repo are all-or-nothing (a row with no
`w` on a weighted list silently counts as one hour, CLU-131), and a series
article publishes ONE runtime range for the whole show rather than a length
per episode — the collector reads those range strings so the note can quote
them. Folding either series in would strip real, sourced hours off fifteen
films to gain rows for one show. Both are named in the notes with that reason,
so they do not look forgotten.

WEIGHTS
-------
Every row carries `w`, hours from the runtime in that film's own Wikipedia
infobox. The build asserts all fifteen runtimes were parsed rather than
defaulted, that each is a single unambiguous "N minutes", and — the trap
`slashers` hit three times — that the franchise table's release year is one
the film's own infobox states, because both franchises reuse a title across
decades (Child's Play 1988/2019, Scream 1996/2022).

Data: scratch/agent-scream/collect.py -> scream_childsplay_data.json, which
reuses the wikitext cache scratch/slashers/ already warmed.
"""
import datetime
import json
import pathlib
import re
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop
from gwlib.prop import slug, normt, join_bits

SLUG = "scream-childs-play"
ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "scratch" / "agent-scream" / "scream_childsplay_data.json"

ACCENT, ACCENT_DARK = "#7B1250", "#FF9AD5"

WIKI = "https://en.wikipedia.org/wiki/"

# Row notes. Terse, factual, spoiler-free — each says what a film IS or where
# it sits, never what happens in it. Keyed by (franchise, label, year). The
# Child's Play block label is NOT here: it is prepended per row from the
# table's own grouping, so it can never drift from the source.
NOTES = {
    ("chucky", "Child's Play", 1988):
        "The first film.",
    ("chucky", "Bride of Chucky", 1998):
        "Seven years on, and the first entry not titled Child's Play.",
    ("chucky", "Seed of Chucky", 2004):
        "Series creator Don Mancini's first film as director; he directs the "
        "rest of this block.",
    ("chucky", "Curse of Chucky", 2013):
        "Nine years later, and released to video on demand rather than "
        "cinemas.",
    ("chucky", "Cult of Chucky", 2017):
        "Direct-to-video, as with the film before it.",
    ("chucky", "Child's Play", 2019):
        "A remake of the 1988 film, and the only entry not written by Don "
        "Mancini or featuring Brad Dourif as Chucky.",
    ("scream", "Scream", 1996):
        "Wes Craven's original, with a cast who know the conventions of the "
        "horror film and use them — the self-reference the series runs on.",
    ("scream", "Scream 2", 1997):
        "Released less than a year after the first, and turns the same "
        "self-reference on the horror sequel.",
    ("scream", "Scream 3", 2000):
        "Written as the concluding chapter; the series resumed eleven years "
        "later.",
    ("scream", "Scream 4", 2011):
        "Eleven years on, and the last of the four Wes Craven directed.",
    ("scream", "Scream", 2022):
        "Shares its title with the 1996 film; the article indexes it as the "
        "fifth. The first not directed by Wes Craven.",
    ("scream", "Scream VI", 2023):
        "The one entry numbered in Roman numerals, from the directors of the "
        "2022 film.",
    ("scream", "Scream 7", 2026):
        "Directed by series creator Kevin Williamson, who wrote the first two "
        "films and the fourth.",
}


def load_json(path, tries=4):
    """Read a JSON file that another builder may be mid-write on."""
    for n in range(tries):
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            if n == tries - 1:
                raise
            time.sleep(0.4)


def released(films):
    """The rows of a Films table that name a film somebody has released."""
    return [f for f in films if f["released"]]


def check_source(d):
    """Everything the list asserts about its own sources, before it builds."""
    counts = {k: len(released(d[k]["films"])) for k in ("chucky", "scream")}
    assert counts == {"chucky": 8, "scream": 7}, counts

    # --- the two reasons slashers gave for leaving these franchises out, ----
    # re-checked here rather than inherited on trust
    assert not d["scream"]["chronology"], d["scream"]["chronology"]
    assert d["scream"]["groups"] == [], d["scream"]["groups"]
    assert all(f["group"] is None for f in d["scream"]["films"]), \
        "the Scream table grew a block header"
    assert not d["chucky"]["chronology"], d["chucky"]["chronology"]
    assert d["chucky"]["groups"] == ["Original series", "Reboot"], \
        d["chucky"]["groups"]
    blocks = {}
    for f in released(d["chucky"]["films"]):
        assert f["group"], "Child's Play row outside every block: %s" % f["label"]
        blocks.setdefault(f["group"], []).append(f["date"][0])
    assert sorted(blocks) == ["Original series", "Reboot"], sorted(blocks)
    assert len(blocks["Original series"]) == 7 and len(blocks["Reboot"]) == 1, \
        {k: len(v) for k, v in blocks.items()}
    # a clean fork, not a tangle: the two blocks do not interleave in time
    assert max(blocks["Original series"]) < min(blocks["Reboot"]), blocks

    # --- everything a table names but this list leaves out is unreleased ----
    for k in ("chucky", "scream"):
        for f in d[k]["films"]:
            assert f["released"] or not f["date"], (k, f["label"])
            assert f["released"] or re.search(r"untitled|\bTBA\b", f["label"],
                                              re.I), (k, f["label"])
            assert f["released"] or "TBA" in f["date_cell"], (k, f["label"])

    # --- every row is machine-read, and its year checks out ----------------
    for k in ("chucky", "scream"):
        for f in released(d[k]["films"]):
            assert f["runtime"], "no runtime parsed: %s" % f["label"]
            assert 60 <= f["runtime"] <= 200, (f["label"], f["runtime"])
            # one clean "N minutes", not a list of cuts to choose between
            assert re.fullmatch(r"\d+ minutes", f["runtime_field"]), \
                (f["label"], f["runtime_field"])
            # the franchise table's release year is one the film's own
            # infobox states — the guard against a reused title (Child's Play
            # 1988/2019, Scream 1996/2022) pulling the wrong runtime
            assert f["date"][0] in f["infobox_years"], \
                (f["label"], f["date"], f["infobox_years"])
        got = [f["date"] for f in released(d[k]["films"])]
        assert got == sorted(got), "%s table is not in release order" % k

    # --- the facts the row notes state, read from the articles -------------
    for k in ("chucky", "scream"):
        for needle, sentence in d[k]["claims"].items():
            assert sentence, "the article no longer says %r" % needle

    def film(k, label, year):
        return next(f for f in released(d[k]["films"])
                    if f["label"] == label and f["date"][0] == year)

    def days(a, b):
        return (datetime.date(*b["date"]) - datetime.date(*a["date"])).days

    # Child's Play: Bride is seven years on and the first title to drop the
    # franchise name; Mancini directs from Seed onwards and not before; Curse
    # is nine years after Seed
    cp3, bride = film("chucky", "Child's Play 3", 1991), \
        film("chucky", "Bride of Chucky", 1998)
    assert bride["date"][0] - cp3["date"][0] == 7, (cp3["date"], bride["date"])
    orig = [f for f in released(d["chucky"]["films"])
            if f["group"] == "Original series"]
    named = [f["label"].startswith("Child's Play") for f in orig]
    assert named == [True, True, True, False, False, False, False], named
    directed = [f["label"] for f in orig if f["director"] == "Don Mancini"]
    assert directed == ["Seed of Chucky", "Curse of Chucky", "Cult of Chucky"], \
        directed
    assert film("chucky", "Curse of Chucky", 2013)["date"][0] \
        - film("chucky", "Seed of Chucky", 2004)["date"][0] == 9
    assert film("chucky", "Curse of Chucky", 2013)["claim"], "no VOD sentence"
    assert film("chucky", "Cult of Chucky", 2017)["claim"], "no direct-to-video"
    assert film("chucky", "Child's Play", 2019)["group"] == "Reboot"

    # Scream: 2 lands inside a year of 1; Craven directs exactly the first
    # four; 4 is eleven years after 3; the article anchors the 2022 film as
    # the fifth; VI is the only Roman numeral; Williamson directs the seventh
    assert 0 < days(film("scream", "Scream", 1996),
                    film("scream", "Scream 2", 1997)) < 365
    craven = [f["label"] for f in released(d["scream"]["films"])
              if f["director"] == "Wes Craven"]
    assert craven == ["Scream", "Scream 2", "Scream 3", "Scream 4"], craven
    assert film("scream", "Scream 4", 2011)["date"][0] \
        - film("scream", "Scream 3", 2000)["date"][0] == 11
    fifth = [h for h in d["scream"]["film_headings"] if 'id="Scream 5"' in h]
    assert len(fifth) == 1 and "2022" in fifth[0], d["scream"]["film_headings"]
    romans = [f["label"] for f in released(d["scream"]["films"])
              if re.search(r"\b[IVX]+$", f["label"])]
    assert romans == ["Scream VI"], romans
    assert film("scream", "Scream", 2022)["director"] \
        == film("scream", "Scream VI", 2023)["director"], "directors diverged"
    assert film("scream", "Scream 7", 2026)["director"] == "Kevin Williamson"

    # --- the television series, and why they cannot be rows ----------------
    for k, v in d["tv"].items():
        assert v["seasons"] == 3, (k, v["seasons"])
        assert v["episodes"] and v["episodes"] > 20, (k, v["episodes"])
        # a RANGE for the whole show, not a length per episode — the reason
        # these cannot be weighted without inventing hours
        assert re.fullmatch(r"\d+[–-]\d+ minutes", v["runtime_field"]), \
            (k, v["runtime_field"])
    assert d["tv"]["chucky"]["years"] == [2021, 2024], d["tv"]["chucky"]["years"]
    assert d["tv"]["scream"]["years"][0] == 2015 \
        and d["tv"]["scream"]["years"][-1] == 2019, d["tv"]["scream"]["years"]
    return counts


def accent_is_free():
    """No other property may share this list's accent pair (qa_lint rule)."""
    for f in sorted((ROOT / "properties").glob("*.json")):
        if f.name in ("index.json", "search.json", "%s.json" % SLUG):
            continue
        p = load_json(f)
        assert (p.get("accent"), p.get("accentDark")) != (ACCENT, ACCENT_DARK), \
            "accent pair already used by %s" % f.stem


def sync_partners(rows):
    """Rows on other lists that would tick together with rows on this one.

    build.py groups syncable rows on normalized title + year + medium, with a
    fallback to an explicit `y` or to a single year found in the note, and it
    skips the secret property outright. This reproduces that key exactly
    rather than guessing at it, so the overlap the notes describe is the
    overlap the shipped page will actually have. Returns {our id: [(slug, id,
    title)]}, and the notes are written from whatever it finds — including
    nothing, which is the answer today.
    """
    want = {"%s|%s|f" % (normt(x["t"]), x["n"]): x["id"] for x in rows}
    out = {}
    for f in sorted((ROOT / "properties").glob("*.json")):
        if f.name in ("index.json", "search.json", "%s.json" % SLUG):
            continue
        p = load_json(f)
        if p.get("secret"):
            continue
        kind = p.get("kind") or ""
        if not ("film" in kind or "game" in kind):
            continue
        medium = "g" if "game" in kind else "f"
        for s in p.get("sections", []):
            for x in s.get("items", []):
                n = str(x.get("n", ""))
                if re.fullmatch(r"(18|19|20)\d{2}", n):
                    year = n
                elif re.fullmatch(r"(18|19|20)\d{2}", str(x.get("y", ""))):
                    year = str(x["y"])
                else:
                    found = set(re.findall(r"\b((?:18|19|20)\d{2})\b",
                                           x.get("note") or ""))
                    year = found.pop() if len(found) == 1 else None
                key = "%s|%s|%s" % (normt(x.get("t", "")), year, medium)
                if year and key in want:
                    out.setdefault(want[key], []).append(
                        (p["slug"], x["id"], p["title"]))
    return out


def sync_note(partners, rows):
    """The footer note about cross-list ticking, written from the facts."""
    if not partners:
        return ["Nothing here ticks anywhere else.",
                "Ticks sync across clubd wherever two lists carry the same "
                "film and year — but none of these %d films sits on another "
                "list today, so every row here is ticked here only. The "
                "generator re-checks the whole catalogue each time it runs, "
                "so this note cannot quietly go stale." % len(rows)]
    ours = {x["id"]: x for x in rows}
    bits = []
    for rid in sorted(partners):
        titles = sorted({t for _, _, t in partners[rid]})
        others = (" and ".join(titles) if len(titles) < 3
                  else ", ".join(titles[:-1]) + " and " + titles[-1])
        bits.append("%s (%s) also sits on %s"
                    % (ours[rid]["t"], ours[rid]["n"], others))
    return ["Some rows tick on other lists too.",
            "Ticking a film in one place ticks it everywhere it appears: "
            + "; ".join(bits) + ". Nothing else on this list overlaps the "
            "catalogue."]


def main():
    d = load_json(DATA)
    counts = check_source(d)
    accent_is_free()

    def row(key, f):
        year = f["date"][0]
        it = {"id": "scp-%d-%s" % (year, slug(f["label"])),
              "t": f["label"], "n": str(year),
              "w": round(f["runtime"] / 60.0, 2)}
        # the Child's Play block label leads its row's note, straight from the
        # table's own grouping; Scream rows have no block and carry none
        note = join_bits(f["group"], NOTES.get((key, f["label"], year)))
        if note:
            it["note"] = note
        return it

    def section(key, sid, title, intro, page):
        got = released(d[key]["films"])
        items = [row(key, f) for f in got]
        mins = sum(f["runtime"] for f in got)
        sub = "%d–%d · %d films · %d hours" % (
            got[0]["date"][0], got[-1]["date"][0], len(got), round(mins / 60.0))
        return {"id": sid, "title": title, "sub": sub, "intro": intro,
                "links": [{"label": "The filmography", "url": WIKI + page}],
                "items": items}, mins

    childs_play, c_min = section(
        "chucky", "childs-play", "Child's Play",
        "Eight films, and the article's own filmography divides them into "
        "exactly two labelled blocks — Original series and Reboot — "
        "that never intersect. Seven run from 1988 to 2017, all written or "
        "co-written by series creator Don Mancini; the 2019 film is a remake "
        "that starts over with new hands. Each row carries the block the table "
        "puts it in rather than being folded into one sequence, and the section "
        "runs in U.S. release order.",
        "Child%27s_Play_(franchise)")

    scream, s_min = section(
        "scream", "scream", "Scream",
        "Seven films and one unbroken line. The franchise's own article "
        "carries no story chronology, and its filmography carries no "
        "continuity blocks, because there is nothing to divide: no remake, no "
        "reboot, no competing sequel — so release order is story order here. "
        "What the series has instead is a method, stated from the first film "
        "on: characters who know the conventions of the horror film and use "
        "them.",
        "Scream_(franchise)")

    sections = [childs_play, scream]
    childs_play["open"] = True

    # ---- the checks the shipped file has to pass -------------------------
    rows = [x for s in sections for x in s["items"]]
    assert len(rows) == 15, len(rows)
    assert len(rows) == counts["chucky"] + counts["scream"], len(rows)
    ids = [x["id"] for x in rows]
    assert len(ids) == len(set(ids)), \
        sorted({i for i in ids if ids.count(i) > 1})
    for s in sections:
        years = [int(x["n"]) for x in s["items"]]
        assert years == sorted(years), "%s is out of release order" % s["title"]
    # all-or-nothing weighting: one bare row would silently cost an hour
    assert all(isinstance(x.get("w"), float) and x["w"] > 0 for x in rows), \
        [x["id"] for x in rows if not x.get("w")]
    # sections are ordered by the year each franchise began
    starts = [int(s["items"][0]["n"]) for s in sections]
    assert starts == [1988, 1996] == sorted(starts), starts
    # every Child's Play row is labelled with its block; no Scream row is
    for x in childs_play["items"]:
        assert x["note"].startswith(("Original series", "Reboot")), x
    for x in scream["items"]:
        assert not x["note"].startswith(("Original series", "Reboot")), x

    mins = c_min + s_min
    hours = round(sum(x["w"] for x in rows), 2)
    assert abs(hours - mins / 60.0) < 0.2, (hours, mins / 60.0)

    partners = sync_partners(rows)
    tv = d["tv"]

    p = {
        "slug": SLUG,
        "title": "Scream & Child's Play",
        "subtitle": "the two franchises Slashers left out, in release order",
        "kind": "films",
        "popularity": 59,
        "year": "1988–2026",
        "blurb": "Chucky and Ghostface — %d films, one clean fork and one "
                 "unbroken line, in the order they came out. About %d hours."
                 % (len(rows), round(hours)),
        "unit": {"one": "film", "many": "films"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "accent": ACCENT,
        "accentDark": ACCENT_DARK,
        "tiers": False,
        "notes": [
            ["Release order, and here it costs nothing.",
             "Neither franchise makes you pick a timeline. Scream's article "
             "carries no story chronology and its filmography no continuity "
             "blocks: seven films, one line, no remake and no reboot, so "
             "release order is story order. Child's Play's filmography does "
             "divide, but cleanly — into exactly two labelled blocks, "
             "Original series and Reboot, that never intersect and never "
             "overlap in time — so each of those rows carries the block "
             "the table puts it in instead of being folded into one sequence. "
             "Sections run by the year each franchise began: Child's Play "
             "1988, then Scream 1996."],
            ["The companion to Slashers.",
             "That list covers Halloween, Friday the 13th and A Nightmare on "
             "Elm Street, and names these two franchises as the ones it left "
             "out: Scream because it has no tangle to untangle, Child's Play "
             "because it forks rather than tangles. Both reasons are checked "
             "against the same articles every time this list is generated, "
             "and these %d films live here instead." % len(rows)],
            ["Bar widths are runtimes.",
             "Every row carries the runtime stated in that film's own "
             "Wikipedia infobox, checked against the U.S. release year the "
             "franchise table gives — %d hours in all. Both franchises "
             "reuse a title across decades, so the year is what tells Child's "
             "Play 1988 from 2019 and Scream 1996 from 2022. A row whose "
             "runtime could not be read would fail the build rather than ship "
             "as a guess, and there is no half-weighted state: every row "
             "carries a runtime or none does." % round(hours)],
            ["Neither television series is here.",
             "Chucky ran for %d seasons and %d episodes between %d and %d, "
             "and continues the original film line; the Scream series ran for "
             "%d seasons and %d episodes between %d and %d, as an anthology "
             "the franchise article states is not canon to the films. Both are "
             "left out for a mechanical reason rather than a critical one: "
             "weights here "
             "are hours, and a series article publishes a single runtime range "
             "for the whole show — %s for Chucky, %s for Scream — "
             "rather than a length per episode. Folding either in would trade "
             "measured hours on %d films for guessed ones on one show. Named "
             "here so they do not look forgotten."
             % (tv["chucky"]["seasons"], tv["chucky"]["episodes"],
                tv["chucky"]["years"][0], tv["chucky"]["years"][-1],
                tv["scream"]["seasons"], tv["scream"]["episodes"],
                tv["scream"]["years"][0], tv["scream"]["years"][-1],
                tv["chucky"]["runtime_field"], tv["scream"]["runtime_field"],
                len(rows))],
            ["Not included.",
             "An untitled eighth Scream film and an untitled Chucky film sit "
             "in the two tables with no release date and no runtime, so "
             "neither is a row yet; every film the tables date is here. The "
             "short films, documentaries, novels, comics, video games and "
             "theme-park attractions the franchise articles list are out of "
             "scope."],
            sync_note(partners, rows),
            "Titles, U.S. release dates and the Original series / Reboot "
            "blocks from the Films tables of Wikipedia's Child's Play and "
            "Scream franchise articles; runtimes and directors from each "
            "film's own article infobox; season counts, episode counts and "
            "runtime ranges from the two television series' own articles.",
        ],
        "sections": sections,
    }

    out = prop.write(p)
    print("wrote %s — %d rows, %.2f hours (%d minutes)"
          % (out.name, len(rows), hours, mins))
    for s in sections:
        years = [int(x["n"]) for x in s["items"]]
        print("   %-14s %2d rows  %d–%d  %5.2f h  |  %s"
              % (s["title"], len(s["items"]), years[0], years[-1],
                 sum(x["w"] for x in s["items"]), s["sub"]))
    print("   sync groups formed: %s"
          % (", ".join("%s -> %s" % (k, [b for _, b, _ in v])
                       for k, v in sorted(partners.items())) or "none"))


if __name__ == "__main__":
    main()
