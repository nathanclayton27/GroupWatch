#!/usr/bin/env python3
"""Generate properties/farscape.json — four seasons and the miniseries.

    python3 tools/make_farscape.py

90 rows: 88 episodes across four seasons, 1999–2003, then both parts of
Farscape: The Peacekeeper Wars, 2004.

THE MINISERIES IS PART OF THE LIST, not an appendix to it. Sci-Fi withdrew
funding for a fifth season in September 2002 with eleven of season four's
episodes still unaired, and season four ends mid-story; the miniseries was
made to finish it. Somebody who watches the four seasons and stops has not
finished the show, so The Peacekeeper Wars is a full section with the same
weight as a season, its own copy saying why it is required, and the year
range on the property runs to 2004 rather than 2003.

TWO PARTS, NOT A FILM. Wikipedia files it as a television miniseries — an
{{Infobox television}} with num_episodes = 2, an {{Episode table}} of two
{{Episode list}} rows numbered 89 and 90 in the series' own overall run, and
a {{Series overview}} block counting `episodes4S = 2`. Two rows, therefore,
not one film row. That also settles the property's kind as "tv": nothing
here is a film-kind row, so this list contributes no cross-list sync groups
(build.py gates sync on `"film" in kind or "game" in kind`) and the years
inside the two miniseries notes cannot pair with anything.

NOTHING IS WEIGHTED. The episode tables publish no runtimes — the source
gives one blanket "44 to 50 minutes" for the whole run, which is a
series-level figure and never a per-episode one — while the miniseries
publishes 182 minutes. Weighting the two rows that have a figure and leaving
the other 88 bare would silently count each bare row as one hour (CLU-131),
so no row carries a weight and every entry counts as one. All or nothing.

ORDER: the source's own. The episode list follows the order the official
Farscape site published — production order — rather than Sci-Fi's airing
order, and the difference is confined to season one; this script asserts
that seasons two to four are in airdate order and that season one is not.

Titles, numbering, part markers and airdates are machine-read from
Wikipedia's "List of Farscape episodes" by scratch/agent-farscape/parse.py,
which asserts the page's own {{Series overview}} counts (22/22/22/22 and a
two-part miniseries) and an unbroken 1–90 overall numbering. The committed
result is tools/data/farscape_episodes.json. This script re-asserts every
count and every claim its copy makes before it writes.
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop  # noqa: E402

SLUG = "farscape"
DATA = pathlib.Path(__file__).resolve().parent / "data" / "farscape_episodes.json"

SEASONS = ("s1", "s2", "s3", "s4")
PER_SEASON = 22
ROWS = 90

MONTHS = ("January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December")
COUNT = {2: "two", 3: "three"}

# The source marks multi-part stories two ways and the difference decides
# whether a row needs a note. A named arc puts the marker inside the title —
# `Look at the Princess (Part 1): A Kiss Is But a Kiss` — so the row already
# says it and a note would only repeat the title. The rest are marked in
# |RTitle, outside the title, and would be lost silently without one.
INTITLE = re.compile(r"^(.+?) \(Part (\d)\)(?::.*)?$")

# Season four's sub says it too, because a collapsed section shows the sub
# and not the intro, and this is the one fact the list exists to carry.
SEASON_SUB_TAIL = {"s4": "not the end of the story"}

SEASON_INTRO = {
    "s1": "In the order the official Farscape site published — production "
          "order — which is not the order Sci-Fi aired several of these.",
    "s4": "Sci-Fi withdrew funding for a fifth season in September 2002, with "
          "eleven of these episodes still unaired. This season does not end "
          "the story.",
}


def longdate(iso):
    """2004-10-17 -> 17 October 2004."""
    y, m, d = iso.split("-")
    return "%d %s %s" % (int(d), MONTHS[int(m) - 1], y)


def part_runs(flat):
    """Group the source's own part markers into runs of consecutive rows.

    The source marks parts in |RTitle — `"Nerve" (Part 1)` — and four of the
    five runs it marks are two-parters, three of which straddle a season
    break. A run is rows whose overall numbers are consecutive and whose part
    numbers count 1, 2, … from one; anything else means the markers moved
    upstream and should fail here rather than produce a note that lies.
    """
    runs, cur = [], []
    for row in flat:
        p = row.get("part")
        if p == 1:
            if cur:
                runs.append(cur)
            cur = [row]
        elif p:
            assert cur and p == cur[-1]["part"] + 1 \
                and row["o"] == cur[-1]["o"] + 1, \
                "part marker run broken at overall %d" % row["o"]
            cur.append(row)
        elif cur:
            runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    assert [len(r) for r in runs] == [2, 2, 2, 2, 3], [len(r) for r in runs]
    return runs


def intitle_arcs(flat):
    """Named arcs whose part marker lives inside the title, checked whole.

    A `(Part 2)` shipping without its `(Part 1)`, or with the two rows not
    adjacent, means the list has a hole; the titles are the only thing
    telling a reader these belong together, so they have to be complete.
    """
    arcs = {}
    for r in flat:
        m = INTITLE.match(r["t"])
        if m:
            arcs.setdefault(m.group(1), []).append((int(m.group(2)), r["o"]))
    for stem, got in arcs.items():
        parts = [p for p, _o in got]
        overalls = [o for _p, o in got]
        assert parts == list(range(1, len(parts) + 1)), (stem, parts)
        assert overalls == list(range(overalls[0], overalls[0] + len(got))), \
            (stem, overalls)
    return arcs


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))

    # ---- counts, before anything is built from them
    for k in SEASONS:
        eps = data[k]["eps"]
        assert len(eps) == PER_SEASON, (k, len(eps))
        assert [r["e"] for r in eps] == list(range(1, PER_SEASON + 1)), k
    mini = data["pkw"]["eps"]
    assert len(mini) == 2, len(mini)
    assert [r["o"] for r in mini] == [89, 90], mini

    flat = [r for k in SEASONS + ("pkw",) for r in data[k]["eps"]]
    assert [r["o"] for r in flat] == list(range(1, ROWS + 1)), "numbering gap"

    season_of = {r["o"]: int(k[1]) for k in SEASONS for r in data[k]["eps"]}

    # ---- every claim the copy makes, checked rather than trusted
    # season one is in production order; the rest are in airdate order
    def inversions(k):
        a = [r["air"] for r in data[k]["eps"]]
        return sum(1 for x, y in zip(a, a[1:]) if y < x)

    assert inversions("s1") > 0, "season one is now in airdate order"
    assert all(inversions(k) == 0 for k in ("s2", "s3", "s4")), \
        "a later season fell out of airdate order"
    # eleven of season four still unaired when the cancellation landed
    unaired = sum(1 for r in data["s4"]["eps"] if r["air"] > "2002-09-30")
    assert unaired == 11, unaired
    # the two nights of the miniseries, four months short of two years later
    assert [r["air"] for r in mini] == ["2004-10-17", "2004-10-18"], mini

    # ---- the two ways the source marks a multi-part story
    arcs = intitle_arcs(flat)
    runs = part_runs(flat)
    pairs, trios = sum(len(r) == 2 for r in runs), sum(len(r) == 3 for r in runs)
    assert (pairs, trios) == (4, 1), (pairs, trios)
    # the numbers the footer note quotes, so the prose cannot drift from them
    assert len(arcs) == 7 and sum(len(v) for v in arcs.values()) == 17, \
        (len(arcs), sum(len(v) for v in arcs.values()))

    # ---- notes the source's part markers earn
    notes = {}
    for run in runs:
        n = COUNT[len(run)]
        crosses = len({season_of[r["o"]] for r in run}) > 1
        for r in run:
            bits = []
            if crosses and r["e"] == PER_SEASON:
                bits.append("Season finale")
            elif crosses and r["e"] == 1:
                bits.append("Season premiere")
            tail = "Part %d of %s" % (r["part"], n)
            if crosses:
                tail += (", concluded in season %d" % (season_of[r["o"]] + 1)
                         if r["part"] == 1 else
                         ", begun in season %d" % (season_of[r["o"]] - 1))
            notes[r["o"]] = prop.join_bits(*bits, tail)

    # The last episode of the run carries no part marker of its own, and that
    # is exactly the point: what follows it is the miniseries, not a part two.
    last = data["s4"]["eps"][-1]
    assert not last.get("part"), last
    notes[last["o"]] = prop.join_bits(
        "Season finale", "the story continues in The Peacekeeper Wars")

    for r in flat:
        if r.get("alt"):
            notes[r["o"]] = prop.join_bits(notes.get(r["o"]),
                                           "Also known as %s" % r["alt"])
    for i, r in enumerate(mini):
        notes[r["o"]] = prop.join_bits(
            "%s night" % ("First", "Second")[i], longdate(r["air"]))
    assert len(notes) == 15, len(notes)     # 11 parts + s4 finale + alt + 2 nights

    # ---- sections
    sections = []
    for k in SEASONS:
        block = data[k]["eps"]
        sec = {
            "id": k,
            "title": "Season %s" % k[1],
            "sub": prop.join_bits(data[k]["span"],
                                  "%d episodes" % PER_SEASON,
                                  SEASON_SUB_TAIL.get(k)),
            "items": [{"id": "fs-%se%d" % (k, r["e"]), "t": r["t"],
                       "n": str(r["e"])}
                      | ({"note": notes[r["o"]]} if r["o"] in notes else {})
                      for r in block],
        }
        if k in SEASON_INTRO:
            sec["intro"] = SEASON_INTRO[k]
        if k == "s1":
            sec["open"] = True
        sections.append(sec)

    sections.append({
        "id": "pkw",
        "title": "The Peacekeeper Wars",
        "sub": "2004 · two nights · the ending",
        "intro": "Not optional. The miniseries was made after the "
                 "cancellation to finish what season four leaves open, and "
                 "the same source that numbers the seasons numbers its two "
                 "parts 89 and 90 of the run. Four seasons and stop is an "
                 "unfinished watch.",
        "items": [{"id": "fs-pkw-%d" % (i + 1), "t": r["t"], "n": str(i + 1),
                   "note": notes[r["o"]]}
                  for i, r in enumerate(mini)],
    })

    p = {
        "slug": SLUG,
        "title": "Farscape",
        "subtitle": "four seasons and the miniseries that finishes them",
        "kind": "tv",
        "popularity": 56,
        "year": "1999–2004",
        "blurb": "All 88 episodes across four seasons, then both nights of "
                 "The Peacekeeper Wars — because season four does not end "
                 "the story.",
        "unit": {"one": "entry", "many": "entries"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": "#2B3A8F",
        "accentDark": "#8B9BF0",
        "tiers": False,
        "notes": [
            ["The Peacekeeper Wars is not optional.", "Sci-Fi withdrew "
             "funding for a fifth season in September 2002, with eleven "
             "episodes of season four still unaired, and season four ends "
             "mid-story. The two-night miniseries that followed in 2004 was "
             "made to finish it, and the episode list numbers its parts 89 "
             "and 90 of the same run. It gets a section rather than a "
             "footnote for that reason: stopping at 88 is stopping early."],
            ["The source marks its own parts.", "Seven named arcs carry the "
             "marker inside the title — Look at the Princess (Part 1), "
             "We're So Screwed (Part 3) — and seventeen rows are theirs. Four "
             "more pairs and one trio are marked outside the title, and those "
             "became row notes so nothing was lost. Three of the four seasons "
             "end on a part one that the next season's premiere concludes; "
             "season four ends on no such marker, and the miniseries is what "
             "follows it."],
            ["Season one is in production order.", "The list follows the "
             "order the official Farscape site published rather than the "
             "order Sci-Fi aired them, and several early season one episodes "
             "differ between the two. Sci-Fi's scheduling was erratic "
             "throughout — season one's last four went out nearly four "
             "months after the one before them — and the other three seasons "
             "are in airdate order either way."],
            ["Nothing is weighted.", "No per-episode runtimes are published: "
             "the source gives one blanket 44-to-50 minutes for the whole "
             "run, which is a figure for the series and not for any episode "
             "in it. The miniseries does publish 182 minutes, and weighting "
             "those two rows while the other 88 stayed bare would quietly "
             "count each of them as exactly one hour. So no row carries a "
             "weight and every entry counts as one."],
            "Titles, numbering, part markers and airdates machine-read from "
            "Wikipedia's List of Farscape episodes and Farscape: The "
            "Peacekeeper Wars; the page's own series overview counts and an "
            "unbroken 1–90 numbering are asserted before this builds.",
        ],
        "sections": sections,
    }

    ids = prop.validate(p)
    assert len(ids) == ROWS, len(ids)
    assert sum(len(s["items"]) for s in sections[:4]) == 88
    out = prop.write(p)

    print("wrote %s — %d rows (88 episodes + 2 miniseries parts), unweighted"
          % (out.name, len(ids)))
    for s in sections:
        print("   %-22s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
