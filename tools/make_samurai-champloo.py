#!/usr/bin/env python3
"""Generate properties/samurai-champloo.json — all 26 episodes, both runs.

    python tools/make_samurai-champloo.py

Manglobe's debut production, directed by Shinichirō Watanabe: twenty-six
episodes, May 20 2004 to March 19 2005, finished. One row per episode, in
broadcast order, in two sections.

TWO SECTIONS BECAUSE THE BROADCAST HAS TWO HALVES, AND THAT IS THE ONLY
STRUCTURE THE SOURCE DOCUMENTS. Wikipedia's episode list is one flat table of
26 with no arc headings, no {{Series overview}} and no part markers — nothing
to cut it on. What the series article's Broadcast section does document, in
words this generator asserts before it builds, is that Fuji TV "ran for
seventeen episodes on the network until September 23, 2004, when they decided
to cancel its broadcast", and that the series "resumed airing… referred to as
a second season", with "the remaining 18th–26th episodes" airing from January
22 to March 19, 2005. So the sections are those two runs and nothing else. No
arcs are invented: the only multi-episode stories on this list are the ones
that name themselves in their own titles — Hellhounds for Hire, Misguided
Miscreants, Lullabies of the Lost, Elegy of Entrapment and the three-part
Evanescent Encounter — and none of them gets a section of its own.

THE TWO ARTICLES DISAGREE ABOUT WHEN THE FIRST RUN ENDED, AND THE TABLE
SETTLES IT. The episode-list article's lead says the broadcast was "cancelled
on September 9"; that is the date its own table gives episode 15. The series
article — a Good Article — says September 23, which is the date the table
gives episode 17, the seventeenth and last of the first run. This list follows
the series article and the table's own dates. Both statements are asserted
still to be present by scratch/agent-champloo/harvest.py, so if either is
corrected upstream this stops building rather than shipping a stale note. The
two articles also name different channels for the second run (Fuji Network
System against BS Fuji), so this list names neither.

NOTHING IS WEIGHTED, AND THE HUNT IS ON THE RECORD. Four places a per-episode
running time could live were checked and all four are empty:

  * the episode table declares no RunTime column, and not one of its 26
    {{Episode list}} blocks carries a RunTime field;
  * there is no season article to hold one — "Samurai Champloo season 1",
    "season 2" and both parenthesised forms are all redlinks;
  * no episode has its own article: all 26 titles were requested bare and
    disambiguated, 52 candidates, and the only one that resolves as this show
    is a redirect straight back to the episode list; and
  * of the 26 Wikidata items the series item lists as its parts, not one
    carries P2047.

The single running time anywhere is 23 minutes on the series' own Wikidata
item, and its only reference is P143 — imported from German Wikipedia, with no
citation behind it. That is one series-level number of unknown provenance, not
26 sourced ones, so it weights nothing here. Weighting is all or nothing
(CLU-131): a row with no `w` silently counts as one hour, so weighting a few
rows would make the rest read as full hours apiece. Every row counts one, and
main() asserts no weight ever creeps in.

Everything is machine-read. scratch/agent-champloo/harvest.py parses the
cached wikitext of the two articles, asserts the numbering runs 1..26
unbroken, the airdates are in broadcast order, the infobox independently
counts 26 episodes and opens and closes on the first and last episode parsed,
the seventeenth episode aired on the day the Broadcast section ends the first
run, the eighteenth on the day it opens the second, and the whole runtime hunt
came up empty; the committed result is tools/data/samurai-champloo.json. This
generator re-asserts what that file claims and touches no network, so running
it twice produces the same bytes.
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop  # noqa: E402

SLUG = "samurai-champloo"
DATA = pathlib.Path(__file__).resolve().parent / "data" / (SLUG + ".json")

TOTAL = 26
RUN1 = 17          # episodes Fuji TV aired before cancelling the broadcast

# The pair, and each half of it, is asserted unused by every other list.
ACCENT = "#264B7A"       # the indigo of an Edo dyer's cloth
ACCENT_DARK = "#EFC050"  # ...against the sunflower the three are walking to

# Where the picker puts it. Below Cowboy Bebop (73), which is the better-known
# work by the same director — signal 2 in POPULARITY.md, and checkable from
# the catalogue rather than a matter of taste. Above Ghost in the Shell (64)
# and beside Frieren (67) and Wes Anderson (68): a name anyone who watches
# anime knows, carried some way outside it by an Adult Swim run and by a
# soundtrack people know without knowing where it came from.
POPULARITY = 68


def check_accent():
    """The pair, and each half of it, must be unused by every other list."""
    for f in sorted((prop.ROOT / "properties").glob("*.json")):
        if f.stem in (SLUG, "index", "search"):
            continue
        other = json.loads(f.read_text(encoding="utf-8"))
        pair = (other.get("accent"), other.get("accentDark"))
        assert pair != (ACCENT, ACCENT_DARK), \
            "accent pair already belongs to %s" % f.stem
        for hexv in (ACCENT, ACCENT_DARK):
            assert hexv not in pair, "%s already uses %s" % (f.stem, hexv)


def check_source(d):
    """Re-assert what the harvest claims, so a hand-edited data file fails."""
    eps = d["episodes"]
    assert d["total"] == TOTAL and len(eps) == TOTAL, \
        "%d episodes in the data file, expected %d" % (len(eps), TOTAL)
    assert [e["n"] for e in eps] == list(range(1, TOTAL + 1)), \
        "episode numbering is not contiguous 1..%d" % TOTAL
    airs = [e["air"] for e in eps]
    assert airs == sorted(airs), "airdates are not in broadcast order"
    assert len({e["t"] for e in eps}) == TOTAL, "two episodes share a title"

    ib, bc = d["infobox"], d["broadcast"]
    assert ib["episodes"] == TOTAL, ib["episodes"]
    assert ib["director"] == "Shinichirō Watanabe", ib["director"]
    assert bc["run1_episodes"] == RUN1, bc["run1_episodes"]
    assert eps[0]["air"] == bc["run1_first"], "the first run opens elsewhere"
    assert eps[RUN1 - 1]["air"] == bc["run1_last"], \
        "episode %d did not air on the day the first run ends" % RUN1
    assert eps[RUN1]["air"] == bc["run2_first"], \
        "episode %d did not air on the day the second run opens" % (RUN1 + 1)
    assert eps[-1]["air"] == bc["run2_last"], "the second run closes elsewhere"

    # the runtime hunt, re-checked rather than trusted
    h = d["runtime_hunt"]
    assert h["episode_table"]["blocks_with_runtime"] == 0, \
        "the episode table carries runtimes now — this list can be weighted"
    assert not h["episode_table"]["runtime_column_declared"]
    assert not h["season_articles"]["existing"], \
        "a season article exists now: %s" % h["season_articles"]["existing"]
    assert not h["episode_articles"]["own_article"], \
        "an episode has its own article now: %s" \
        % h["episode_articles"]["own_article"]
    assert h["episode_articles"]["candidates"] == 2 * TOTAL, \
        "the episode-article hunt checked %d candidates, expected %d" \
        % (h["episode_articles"]["candidates"], 2 * TOTAL)
    w = h["wikidata"]
    assert w["episode_items"] == TOTAL and not w["episode_items_with_runtime"], \
        "Wikidata has per-episode runtimes now — weight this list"
    assert w["series_runtime_minutes"] == 23, w["series_runtime_minutes"]
    assert w["series_runtime_reference_properties"] == [["P143"]], \
        "the series duration is referenced properly now — revisit weights"
    return eps


def rows(eps, lo, hi):
    """One row per episode, numbered as the source numbers it.

    Notes say what an episode is, never what happens in it: the premiere, the
    finale, and nothing else — the multi-part stories already say so in their
    own titles, so a note repeating that would be noise."""
    out = []
    for e in eps[lo - 1:hi]:
        row = {"id": "champloo-%d" % e["n"], "t": e["t"], "n": str(e["n"])}
        if e["n"] == 1:
            row["note"] = "The premiere"
        elif e["n"] == TOTAL:
            row["note"] = "The finale, and the last of three parts"
        out.append(row)
    return out


def main():
    d = json.loads(DATA.read_text(encoding="utf-8"))
    eps = check_source(d)
    check_accent()
    bc = d["broadcast"]

    sections = [
        {
            "id": "s1",
            "title": "Season 1",
            "sub": "2004 · %d episodes · %s" % (RUN1, bc["run1_network"]),
            "intro": "The first seventeen, weekly from May to September 2004. "
                     "The network cancelled the broadcast here, seventeen "
                     "episodes into a twenty-six episode series.",
            "links": [{"label": "The episode list",
                       "url": "https://en.wikipedia.org/wiki/"
                              "List_of_Samurai_Champloo_episodes"}],
            "open": True,
            "items": rows(eps, 1, RUN1),
        },
        {
            "id": "s2",
            "title": "Season 2",
            "sub": "2005 · %d episodes" % (TOTAL - RUN1),
            "intro": "The remaining nine, four months later, in a midnight "
                     "slot. The source calls them a second season; they are "
                     "episodes 18 to 26 of one twenty-six episode "
                     "production, and they keep those numbers here. The last "
                     "three are a single story, which the source says was "
                     "not planned in advance.",
            "links": [{"label": "The series",
                       "url": "https://en.wikipedia.org/wiki/Samurai_Champloo"}],
            "items": rows(eps, RUN1 + 1, TOTAL),
        },
    ]

    items = [x for s in sections for x in s["items"]]
    assert len(items) == TOTAL, "%d rows, expected %d" % (len(items), TOTAL)
    assert [x["n"] for x in items] == [str(i) for i in range(1, TOTAL + 1)], \
        "the two sections do not reassemble into 1..%d" % TOTAL
    assert not any("w" in x for x in items), \
        "a weight crept in — this list is unweighted end to end"
    # cross-list tick sync pairs rows by title and year, and reads a year out
    # of a note when `n` is not one. Nothing here can leak into that: the
    # kind is not syncable, no `n` is a year, and no note holds one.
    kind = "anime"
    assert "film" not in kind and "game" not in kind, \
        "src/build.py only syncs film- and game-kind lists; %r would" % kind
    for x in items:
        assert not re.fullmatch(r"(18|19|20)\d{2}", x["n"]), \
            "row %s is numbered like a year" % x["id"]
        assert not re.search(r"\b(18|19|20)\d{2}\b", x.get("note") or ""), \
            "row %s has a year in its note — build.py would read it as a " \
            "release year and pair the row with a same-titled film" % x["id"]
        assert "y" not in x, "row %s carries an explicit sync year" % x["id"]

    p = {
        "slug": SLUG,
        "title": "Samurai Champloo",
        "subtitle": "all 26 episodes, in broadcast order",
        "kind": kind,
        "popularity": POPULARITY,
        "year": "2004–05",
        "blurb": "Every episode of Shinichirō Watanabe's Edo-period road "
                 "story, in broadcast order across the two runs it aired in.",
        "unit": {"one": "episode", "many": "episodes"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": ACCENT,
        "accentDark": ACCENT_DARK,
        "tiers": False,
        "notes": [
            ["Two seasons, one twenty-six episode series.",
             "Fuji TV aired seventeen episodes from May 20 to September 23, "
             "2004 and then cancelled the broadcast. The remaining nine aired "
             "from January 22 to March 19, 2005, and the source refers to "
             "them as a second season. The split is a broadcast fact rather "
             "than a break in the story, and the sections here follow it "
             "because it is the only division the source documents."],
            ["The source disagrees with itself about one date.",
             "The episode-list article's lead dates the cancellation to "
             "September 9, 2004 — which is the day its own table gives "
             "episode 15. The series article says September 23, the day the "
             "table gives episode 17, the last of the first run. This list "
             "follows the series article and the table. The two also name "
             "different channels for the second run, so this list names "
             "neither."],
            ["No arcs, because the source names none.",
             "The episode list is one flat table of 26 with no arc headings "
             "and no part markers, so nothing here is grouped by story. The "
             "multi-part episodes announce themselves in their own titles — "
             "Hellhounds for Hire, Misguided Miscreants, Lullabies of the "
             "Lost, Elegy of Entrapment, and Evanescent Encounter, which "
             "runs three."],
            ["Nothing is weighted, and here is everywhere that was checked.",
             "The episode table declares no runtime column and not one of its "
             "26 entries carries a running time. There is no season article "
             "to hold one. No episode has an article of its own — all 26 "
             "titles were looked up bare and disambiguated, and the only one "
             "that resolves as this show is a redirect back to the episode "
             "list. And of the 26 Wikidata items the series lists as its "
             "parts, not one records a duration. The single running time "
             "anywhere is 23 minutes on the series' own Wikidata item, whose "
             "only reference is an import from another Wikipedia rather than "
             "a citation. Weighting is all or nothing: a row with no weight "
             "silently counts as a full hour, so weighting a handful would "
             "make the other rows read as hours apiece. Every row counts one, "
             "and this list does not track hours."],
            ["Watanabe made this after Cowboy Bebop, which is also here.",
             "The source dates the concept to 1999, when he was known for "
             "Cowboy Bebop, and says work was delayed by Cowboy Bebop: The "
             "Movie and his segments of The Animatrix. That is the whole of "
             "the connection as far as this list is concerned — two lists by "
             "the same director, in whichever order you like."],
            ["What is out.",
             "The 2004 manga, whose author wrote an original story rather "
             "than a retelling; the Roman Album art book; the PlayStation 2 "
             "game Samurai Champloo: Sidetracked, which its publisher "
             "describes as a separate storyline; a mobile card game; and the "
             "live-action adaptation announced in March 2026, which has no "
             "episodes. This list is the animated television series."],
            "Titles and airdates machine-read from Wikipedia's List of "
            "Samurai Champloo episodes; the broadcast split, the "
            "cancellation and the production facts from the Samurai Champloo "
            "article. The numbering is asserted contiguous 1–26, the "
            "airdates asserted in broadcast order, the total cross-checked "
            "against the series infobox, and both ends of each run matched "
            "to the episode that aired that day before this builds.",
        ],
        "sections": sections,
    }

    out = prop.write(p)
    print("wrote %s — %d rows in %d sections, unweighted"
          % (out.name, len(items), len(sections)))
    for s in sections:
        first, last = s["items"][0], s["items"][-1]
        print("   %-10s %2d  %-26s episodes %s–%s"
              % (s["title"], len(s["items"]), s["sub"], first["n"], last["n"]))
    print("   span %s to %s · %s"
          % (eps[0]["air"], eps[-1]["air"],
             "no hours tracked (unweighted by design)"))


if __name__ == "__main__":
    main()
