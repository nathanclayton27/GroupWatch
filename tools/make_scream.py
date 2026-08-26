#!/usr/bin/env python3
"""Generate properties/scream.json.

    PYTHONIOENCODING=utf-8 python tools/make_scream.py

The seven released Scream films, 1996 to 2026, in U.S. release order, weighted
by the runtime each film's own Wikipedia infobox states.

WHY THIS LIST EXISTS
--------------------
`tools/make_slashers.py` covers Halloween, Friday the 13th and A Nightmare on
Elm Street — three franchises whose timelines contradict each other, so that
list exists to rule on ordering. Its notes name Scream as one of the two long
slasher franchises it left out, for the opposite reason: there is no tangle to
untangle. This list carries those films, and RE-ASSERTS that reason against
the article every time it runs rather than inheriting it on trust.
check_source() fails the build if the franchise article grows a story
chronology box, if the Films table grows a block header, or if release order
stops matching the numbering the films' own articles claim.

ONE UNBROKEN LINE
-----------------
Seven films, one section, no divisions. No remake, no reboot, no competing
continuity, no chronology box — so release order is story order and there is
nothing for a second section to separate. The one thing that could confuse a
reader is the title: the 2022 film is called Scream, exactly like the 1996
one. Both rows carry the year, and each note names the other film, so neither
can be mistaken for the other. Neither note calls the 2022 film a remake,
because its own article does not: it says "a sequel to Scream 4 (2011), the
fifth installment in the Scream film series".

WEIGHTS
-------
Every row carries `w`, hours from that film's own infobox runtime, and every
one of the seven is corroborated by a SECOND independent source — Wikidata
P2047, gated on P577 so a reused title cannot hand back the wrong film's
length. Six of the seven agree exactly. Scream VI is the one that does not:
Wikipedia states 122 minutes cited to the BBFC certificate, Wikidata's item
says 118. The bar uses the cited BBFC figure, the disagreement is asserted so
that a new or wider one fails the build instead of passing quietly, and it is
named in the notes.

Weighting is all-or-nothing here, as everywhere in this repo: a row with no
`w` on a weighted list silently counts as one hour (CLU-131), so either all
seven carry a runtime or the build fails.

THE TELEVISION SERIES IS OUT, AND THE REASON IS QUOTED
------------------------------------------------------
The Scream television series (2015-19, MTV then VH1, three seasons, 30
episodes) is not a row, for the reason its own franchise article gives: it is
an anthology that "is not canon to the films". That sentence is collected as
data and asserted, so the exclusion cannot outlive the source it rests on.

It could not have been weighted either, and — Nathan's instruction, "try
harder to find the runtimes" — that was established by exhausting all four
places a per-episode runtime could live, not by glancing at one infobox and
finding a range:

  1. the episodes' own articles   1 of 30 episodes has one. "Pilot" states 44
                                  minutes; the other 29 have no article.
  2. Wikidata P2047 per item      Wikidata holds an item for all 30 episodes.
                                  Not one carries P2047. (The SERIES item
                                  carries 45 — one figure for the whole show.)
  3. season articles              There are none. "Scream (season 1)",
                                  "Scream: Resurrection" and the "(TV series)
                                  season N" forms do not exist; "Scream
                                  (season 2)" redirects to the episode list
                                  and "Scream (season 3)" to the series page.
  4. the episode tables' RunTime  None of the 5 episode tables on List of
                                  Scream episodes declares a runtime column,
                                  and none of the 30 {{Episode list}} blocks
                                  carries a RunTime field.

All four are recorded in tools/data/scream.json with counts, asserted below,
and named in the notes. "Unweighted" is a finding with receipts, not a shrug.

Data: scratch/agent-scream2/collect.py -> tools/data/scream.json.
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

SLUG = "scream"
ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "tools" / "data" / "scream.json"

ACCENT, ACCENT_DARK = "#A31432", "#FF9DAF"

WIKI = "https://en.wikipedia.org/wiki/"

# The combined Scream & Child's Play list these films used to sit on. It is
# being retired in favour of this list and a separate Child's Play one, so it
# is skipped by both the accent check and the cross-list sync scan: pairing
# with a list that is about to stop existing would put a promise on the page
# that disappears at the next build. If the file is still present when this
# runs, the skip is announced rather than silent.
RETIRING = "scream-childs-play"

SERIES = "Scream (TV series)"
EPLIST = "List of Scream episodes"

# Row notes. Terse and spoiler-free: each says what a film IS or where it
# sits, never what happens in it and never who is in it at the end. Keyed by
# (title, year), because the title alone is ambiguous — which is the whole
# point of the two notes that name each other.
NOTES = {
    ("Scream", 1996):
        "Wes Craven's original, with a cast who know the conventions of the "
        "horror film and use them. The 2022 film reuses this title.",
    ("Scream 2", 1997):
        "Released less than a year after the first, and turns the same "
        "self-reference on the horror sequel.",
    ("Scream 3", 2000):
        "Written as the concluding chapter; the series resumed eleven years "
        "later.",
    ("Scream 4", 2011):
        "Eleven years on, and the last of the four Wes Craven directed.",
    ("Scream", 2022):
        "A sequel to Scream 4 that takes the 1996 title back — its article "
        "numbers it the fifth film. The first not directed by Wes Craven, "
        "who died in 2015.",
    ("Scream VI", 2023):
        "The sixth, and the one entry numbered in Roman numerals, from the "
        "directors of the 2022 film.",
    ("Scream 7", 2026):
        "Directed by series creator Kevin Williamson, who wrote the first two "
        "films and the fourth.",
}

# Wikipedia's infobox and Wikidata's P2047 are asked independently for every
# film. Where they disagree, the infobox figure is the one the bar uses — it
# carries a citation to a classification board on the article. Exactly one
# such disagreement is expected, and check_source() fails if a new one appears
# or if this one widens, so "the sources disagree" can never become invisible.
RUNTIME_SPLITS = {("Scream VI", 2023): (122, 118)}
SPLIT_TOLERANCE = 5

ORDINALS = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh"]


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
    """The rows of the Films table that name a film somebody has released."""
    return [f for f in films if f["released"]]


def check_source(d):
    """Everything this list asserts about its sources, before it builds."""
    fr = d["franchise"]
    got = released(fr["films"])
    assert len(fr["films"]) == 8 and len(got) == 7, \
        (len(fr["films"]), len(got))

    # --- the reason slashers gave for leaving Scream out, re-checked --------
    # no story chronology to rule on, and no continuity blocks in the table
    assert not fr["chronology"], fr["chronology"]
    assert fr["groups"] == [], fr["groups"]
    assert all(f["group"] is None for f in fr["films"]), \
        "the Films table grew a block header"

    # --- everything the table names but this list leaves out is unreleased --
    for f in fr["films"]:
        assert f["released"] or not f["date"], f["label"]
        assert f["released"] or re.search(r"untitled|\bTBA\b", f["label"], re.I), \
            f["label"]
        assert f["released"] or "TBA" in f["date_cell"], f["label"]

    # --- release order, and the numbering the films claim for themselves ----
    dates = [f["date"] for f in got]
    assert dates == sorted(dates), "the Films table is not in release order"
    ordinals = [f["self_ordinal"] for f in got]
    assert ordinals == [None] + ORDINALS[1:], ordinals
    # so: six of the seven articles number themselves, those numbers run
    # 2..7 in release order, and only the earliest claims no ordinal at all

    # --- every runtime, from two independent sources ------------------------
    for f in got:
        year = f["date"][0]
        assert f["runtime"], "no runtime parsed: %s" % f["label"]
        assert 60 <= f["runtime"] <= 200, (f["label"], f["runtime"])
        # one clean "N minutes", not a list of cuts to choose between
        assert re.fullmatch(r"\d+ minutes", f["runtime_field"]), \
            (f["label"], f["runtime_field"])
        assert len(f["runtime_values"]) == 1, (f["label"], f["runtime_values"])
        # the franchise table's year is one the film's own infobox states —
        # the guard that stops the reused Scream title (1996 / 2022) pulling
        # the wrong film's runtime
        assert year in f["infobox_years"], \
            (f["label"], f["date"], f["infobox_years"])
        wd = f["wikidata"]
        assert wd["qid"], "no Wikidata item: %s" % f["label"]
        assert wd["year_gate"], (f["label"], year, wd["p577_years"])
        assert wd["p2047"], "no P2047: %s" % f["label"]
        split = RUNTIME_SPLITS.get((f["label"], year))
        if split:
            assert (f["runtime"], wd["p2047"]) == split, \
                ("the known disagreement moved", f["label"], f["runtime"],
                 wd["p2047"], split)
            assert abs(split[0] - split[1]) <= SPLIT_TOLERANCE, split
        else:
            assert f["runtime"] == wd["p2047"], \
                ("undeclared source disagreement", f["label"], f["runtime"],
                 wd["p2047"])
    assert set(RUNTIME_SPLITS) <= {(f["label"], f["date"][0]) for f in got}, \
        "a declared disagreement names a film that is not on the list"

    # --- the facts the row notes state, read from the articles --------------
    for needle, sentence in fr["claims"].items():
        assert sentence, "the article no longer says %r" % needle

    def film(label, year):
        return next(f for f in got
                    if f["label"] == label and f["date"][0] == year)

    def days(a, b):
        return (datetime.date(*b["date"]) - datetime.date(*a["date"])).days

    # exactly one title is used twice, and it is Scream 1996 / 2022 — the
    # thing the two notes exist to disambiguate
    seen = {}
    for f in got:
        seen.setdefault(f["label"], []).append(f["date"][0])
    assert {k: v for k, v in seen.items() if len(v) > 1} == {"Scream": [1996, 2022]}, \
        {k: v for k, v in seen.items() if len(v) > 1}

    # 2 lands inside a year of 1; Craven directs exactly the first four; 4 is
    # eleven years after 3; the article anchors the 2022 film as the fifth;
    # VI is the only Roman numeral; VI shares the 2022 film's directors;
    # Williamson directs the seventh
    assert 0 < days(film("Scream", 1996), film("Scream 2", 1997)) < 365
    craven = [f["label"] for f in got if f["director"] == "Wes Craven"]
    assert craven == ["Scream", "Scream 2", "Scream 3", "Scream 4"], craven
    assert film("Scream 4", 2011)["date"][0] \
        - film("Scream 3", 2000)["date"][0] == 11
    fifth = [h for h in fr["film_headings"] if 'id="Scream 5"' in h]
    assert len(fifth) == 1 and "2022" in fifth[0], fr["film_headings"]
    romans = [f["label"] for f in got if re.search(r"\b[IVX]+$", f["label"])]
    assert romans == ["Scream VI"], romans
    assert film("Scream", 2022)["director"] == film("Scream VI", 2023)["director"]
    assert film("Scream 7", 2026)["director"] == "Kevin Williamson"

    # --- the television series: why it is out, and the runtime hunt ---------
    tv, hunt = d["tv"]["series"], d["tv"]["hunt"]
    assert tv["seasons"] == 3, tv["seasons"]
    assert tv["episodes"] == 30, tv["episodes"]
    assert tv["years"] == [2015, 2016, 2019], tv["years"]
    # the reason it is excluded, quoted rather than paraphrased
    canon = fr["claims"]["is not [[Canon (fiction)|canon]] to the films"]
    assert "is not canon to the films" in canon, canon
    assert "anthology" in canon.lower(), canon

    # all four runtime sources, each asked and each empty
    assert hunt["episodes_counted"] == 30, hunt["episodes_counted"]
    ea = hunt["episode_articles"]
    assert ea["with_article"] == 1 and ea["without_article"] == 29, ea
    assert ea["found"][0]["title"] == "Pilot", ea["found"]
    assert re.fullmatch(r"\d+ minutes", ea["found"][0]["length"] or ""), ea["found"]
    wd = hunt["wikidata"]
    assert wd["query_error"] is None, wd["query_error"]
    assert wd["items"] == 30, wd["items"]
    assert wd["with_p2047"] == 0, "an episode grew a runtime — re-check the hunt"
    assert wd["series_item"]["p2047"], wd["series_item"]
    assert wd["pilot_item"]["p2047"] is None, wd["pilot_item"]
    for name, dest in hunt["season_articles"].items():
        if name == EPLIST:
            continue
        assert dest in (None, EPLIST, SERIES), \
            "a real season article now exists: %s -> %s" % (name, dest)
    assert hunt["episode_tables"]["with_runtime_field"] == 0, \
        "an episode table grew a RunTime column — re-check the hunt"
    assert hunt["episode_tables"]["tables"] == 5, hunt["episode_tables"]["tables"]
    # and the one figure the series article does publish is a RANGE, which is
    # not a runtime for any particular episode
    assert re.fullmatch(r"\d+[–-]\d+ minutes", tv["runtime_field"]), \
        tv["runtime_field"]
    return got


def accent_is_free():
    """No other property may share this list's accent pair (qa_lint rule)."""
    for f in sorted((ROOT / "properties").glob("*.json")):
        if f.stem in ("index", "search", SLUG, RETIRING):
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
    overlap the shipped page will actually have. Returns ({our id: [(slug, id,
    title)]}, [rows the retiring list would have paired with]).
    """
    want = {"%s|%s|f" % (normt(x["t"]), x["n"]): x["id"] for x in rows}
    out, retiring = {}, []
    for f in sorted((ROOT / "properties").glob("*.json")):
        if f.stem in ("index", "search", SLUG):
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
                if not (year and key in want):
                    continue
                if f.stem == RETIRING:
                    retiring.append(x["id"])
                else:
                    out.setdefault(want[key], []).append(
                        (p["slug"], x["id"], p["title"]))
    return out, retiring


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
    got = check_source(d)
    accent_is_free()

    items, mins = [], 0
    for f in got:
        year = f["date"][0]
        mins += f["runtime"]
        it = {"id": "scr-%d-%s" % (year, slug(f["label"])),
              "t": f["label"], "n": str(year),
              "w": round(f["runtime"] / 60.0, 2)}
        note = join_bits(NOTES.get((f["label"], year)))
        if note:
            it["note"] = note
        items.append(it)

    hours = round(sum(x["w"] for x in items), 2)
    years = [int(x["n"]) for x in items]
    section = {
        "id": "films",
        "title": "The films",
        "sub": "%d–%d · %d films · %d hours" % (
            years[0], years[-1], len(items), round(mins / 60.0)),
        "intro":
            "Seven films and one unbroken line. The franchise's own article "
            "carries no story chronology, and its filmography carries no "
            "continuity blocks, because there is nothing to divide: no "
            "remake, no reboot, no competing timeline — so release order is "
            "story order, and six of the seven articles number themselves in "
            "exactly the order the films came out. What the series has "
            "instead of a tangle is a method, stated from the first film on: "
            "characters who know the conventions of the horror film and use "
            "them.",
        "links": [{"label": "The filmography",
                   "url": WIKI + "Scream_(franchise)"}],
        "items": items,
    }
    sections = [section]

    # ---- the checks the shipped file has to pass --------------------------
    assert len(items) == 7 == len(got), len(items)
    ids = [x["id"] for x in items]
    assert len(ids) == len(set(ids)), \
        sorted({i for i in ids if ids.count(i) > 1})
    assert years == sorted(years), "out of release order"
    assert years == [1996, 1997, 2000, 2011, 2022, 2023, 2026], years
    # the two same-title rows are distinct rows with distinct ids
    same = [x for x in items if x["t"] == "Scream"]
    assert len(same) == 2 and same[0]["id"] != same[1]["id"], same
    # each of the two notes names the OTHER one's year, so a reader landing on
    # either row is told which film it is not
    for x, other in zip(same, reversed(same)):
        assert other["n"] in x["note"], (x["id"], x["note"])
    # nothing calls the 2022 film a remake — its own article calls it a sequel
    assert not any("remake" in (x.get("note") or "") for x in items), \
        [x["id"] for x in items if "remake" in (x.get("note") or "")]
    # all-or-nothing weighting: one bare row would silently cost an hour
    assert all(isinstance(x.get("w"), float) and x["w"] > 0 for x in items), \
        [x["id"] for x in items if not x.get("w")]
    assert abs(hours - mins / 60.0) < 0.2, (hours, mins / 60.0)

    partners, retiring = sync_partners(items)
    tv, hunt = d["tv"]["series"], d["tv"]["hunt"]
    pilot = hunt["episode_articles"]["found"][0]

    p = {
        "slug": SLUG,
        "title": "Scream",
        "subtitle": "the whole run, 1996 to 2026, in release order",
        "kind": "films",
        "popularity": 68,
        "year": "1996–2026",
        "blurb": "Ghostface — %d films, one unbroken line, in the order they "
                 "came out. About %d hours." % (len(items), round(hours)),
        "unit": {"one": "film", "many": "films"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "accent": ACCENT,
        "accentDark": ACCENT_DARK,
        "tiers": False,
        "notes": [
            ["Release order, and here it costs nothing.",
             "Nothing on this list makes you pick a timeline. The franchise "
             "article carries no story chronology and its filmography carries "
             "no continuity blocks: %d films, one line, no remake and no "
             "reboot, so release order is story order. Six of the seven "
             "articles number themselves in the series — second through "
             "seventh — and those numbers run in the same order the films "
             "were released, which is why this list needs one section and no "
             "arguing." % len(items)],
            ["Two of them are called Scream.",
             "The 1996 film and the 2022 one share a title, so they are two "
             "rows with two ids, each dated and each note naming the other. "
             "The 2022 film is not described here as a remake, because its "
             "own article does not describe it as one: it calls it a sequel "
             "to Scream 4 and the fifth installment in the series, and the "
             "franchise article files it under a Scream 5 anchor."],
            ["Bar widths are runtimes.",
             "Every row carries the runtime stated in that film's own "
             "Wikipedia infobox, checked against the U.S. release year the "
             "franchise table gives — %d hours in all — and every one is "
             "confirmed against a second source, Wikidata's runtime property, "
             "identity-gated on publication date so the reused Scream title "
             "cannot fetch the wrong film. Six of the seven agree exactly. "
             "Scream VI is the one that does not: Wikipedia says 122 minutes "
             "citing the BBFC certificate, Wikidata says 118, and the bar "
             "uses the cited figure. A row whose runtime could not be read "
             "would fail the build rather than ship as a guess, and there is "
             "no half-weighted state: every row carries a runtime or none "
             "does." % round(hours)],
            ["The television series is not here, and here is what was checked.",
             "Scream ran for %d seasons and %d episodes — on MTV in %d and %d, "
             "then on VH1 in %d — and it is left out for the reason the "
             "franchise article "
             "itself gives: it is an anthology that “is not canon to the "
             "films”. It could not have been weighted either, and that was "
             "established rather than assumed. All four places a per-episode "
             "runtime could live are empty. One of the %d episodes has its "
             "own article, the pilot, which states %s; the other %d have no "
             "article at all. Wikidata holds an item for all %d and not one "
             "carries a runtime. There are no season articles: “Scream "
             "(season 1)” and “Scream: Resurrection” do not exist, “Scream "
             "(season 2)” redirects to the episode list and “Scream (season "
             "3)” back to the series page. And none of the %d episode tables "
             "on the episode list declares a runtime column, so none of the "
             "%d entries states a length. The series article publishes one "
             "range for the whole show, %s, and a range is not a runtime."
             % (tv["seasons"], tv["episodes"], tv["years"][0], tv["years"][1],
                tv["years"][2],
                hunt["episodes_counted"], pilot["length"],
                hunt["episode_articles"]["without_article"],
                hunt["wikidata"]["items"], hunt["episode_tables"]["tables"],
                hunt["episodes_counted"], tv["runtime_field"])],
            ["Not included.",
             "An untitled eighth film sits in the Films table with no release "
             "date and no runtime, so it is not a row yet; every film the "
             "table dates is here. The short films, video games, comics and "
             "the aftershow the franchise article lists are out of scope."],
            sync_note(partners, items),
            "Titles and U.S. release dates from the Films table of "
            "Wikipedia's Scream (franchise) article; runtimes, directors and "
            "each film's own place in the series from that film's article "
            "infobox and lead, cross-checked against Wikidata; the television "
            "series' shape, and every runtime source checked for it, from the "
            "series article, its episode list and Wikidata.",
        ],
        "sections": sections,
    }

    out = prop.write(p)
    print("wrote %s — %d rows, %.2f hours (%d minutes)"
          % (out.name, len(items), hours, mins))
    for s in sections:
        ys = [int(x["n"]) for x in s["items"]]
        print("   %-12s %2d rows  %d–%d  %5.2f h  |  %s"
              % (s["title"], len(s["items"]), ys[0], ys[-1],
                 sum(x["w"] for x in s["items"]), s["sub"]))
    print("   sync groups formed: %s"
          % (", ".join("%s -> %s" % (k, [b for _, b, _ in v])
                       for k, v in sorted(partners.items())) or "none"))
    if retiring:
        print("   note: %s is still in properties/ and was skipped as "
              "retiring — %d rows would otherwise pair with it"
              % (RETIRING, len(retiring)))


if __name__ == "__main__":
    main()
