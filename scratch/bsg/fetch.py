#!/usr/bin/env python3
"""Extract the Battlestar Galactica (2004) episode data into scratch/bsg/bsg.json.

    python3 scratch/bsg/fetch.py

Reads five Wikipedia pages, disk-cached beside this script as .wiki files so a
re-run is offline and byte-stable:

  List of Battlestar Galactica (2004 TV series) episodes   the miniseries rows,
                                                           Razor, The Plan, and
                                                           the Series overview
  Battlestar Galactica season 1..4                         the episode tables,
                                                           transcluded into the
                                                           list page above

Everything the generator needs is asserted here: the four season counts and the
miniseries count against the list page's own {{Series overview}}, the season
numbering contiguous from 1, the overall numbering contiguous from 1 across
season 1 -> Razor -> season 4, and both television films' dates.

Two rows are {{Episode list}} blocks with NumParts=2, i.e. one broadcast that
covers two numbered slots: Razor (54-55) and the Daybreak finale (75-76 /
season 4's 20-21). Both are kept as one row, because this list is in broadcast
order and that is what was broadcast.

The season 4 page repeats Razor as its first table row with an in-season number
of 0. That row is dropped here (asserted to be Razor) — Razor is taken from the
list page, where it has its own section between seasons 3 and 4.
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "tools"))
from gwlib import wiki  # noqa: E402

LIST_PAGE = "List of Battlestar Galactica (2004 TV series) episodes"
SEASON_PAGE = "Battlestar Galactica season %d"
EXPECT = {1: 13, 2: 20, 3: 20, 4: 21}
MINI = 2


def field(block, name):
    m = re.search(r"\|\s*%s\s*=\s*(.*?)(?=\n\s*\||\Z)" % name, block, re.S)
    return m.group(1).strip() if m else ""


def dates(block):
    """Every {{Start date}} in OriginalAirDate, in order, as ISO strings."""
    raw = field(block, "OriginalAirDate")
    out = []
    for m in re.finditer(r"\{\{Start date\|(\d{4})\|(\d{1,2})\|(\d{1,2})", raw):
        out.append("%04d-%02d-%02d" % tuple(int(x) for x in m.groups()))
    assert out, "no airdate in %r" % raw[:80]
    return out


def num(v):
    m = re.search(r"\d+", v or "")
    return int(m.group(0)) if m else None


def row(block):
    """One {{Episode list}} block -> {e, e2, titles, air, air2}.

    e/e2 are the in-season numbers the row spans (equal for a normal row);
    `overall` is the same span in series numbering; `titles` is one title per
    numbered slot. Titles come from Title, or Title_1/Title_2 on a NumParts
    row, or RTitle when the entry is a film with no plain title.
    """
    parts = num(field(block, "NumParts")) or 1
    if parts == 1:
        titles = [wiki.clean(field(block, "Title")).strip('"')]
        if not titles[0]:
            titles = [wiki.clean(field(block, "RTitle")).strip('"')]
        e = e2 = num(field(block, "EpisodeNumber2"))
        o = o2 = num(field(block, "EpisodeNumber"))
    else:
        assert parts == 2, parts
        titles = [wiki.clean(field(block, "Title_%d" % i)).strip('"')
                  for i in (1, 2)]
        if not any(titles):
            titles = [wiki.clean(field(block, "RTitle")).strip('"')]
        else:
            assert all(titles), titles
        e = num(field(block, "EpisodeNumber2_1"))
        e2 = num(field(block, "EpisodeNumber2_2"))
        o = num(field(block, "EpisodeNumber_1"))
        o2 = num(field(block, "EpisodeNumber_2"))
    d = dates(block)
    out = {"e": e, "e2": e2, "overall": [o, o2], "titles": titles,
           "air": d[0]}
    if len(d) > 1:
        out["air2"] = d[1]
    return out


def main():
    listing = wiki.wikitext(LIST_PAGE, cache_dir=HERE)
    assert listing, "list page unavailable"

    # ---- the page's own Series overview, used as the count to beat ----
    ov = re.search(r"\{\{Series overview(.*?)\n\}\}", listing, re.S).group(1)
    stated = {int(k): int(v) for k, v in
              re.findall(r"\|\s*episodes(\d)\s*=\s*(\d+)", ov)}
    assert stated == {0: MINI, **EXPECT}, stated

    heads = {m.group(1): m.start() for m in
             re.finditer(r"^===\s*(.*?)\s*===$", listing, re.M)}

    def section_between(a, b):
        return listing[heads[a]:heads[b]]

    # ---- miniseries: two untitled broadcast nights ----
    mini_seg = section_between("Miniseries (2003)", "Season 1 (2004–05)")
    mini = [row(b) for *_, b in wiki.episodes(mini_seg)]
    assert len(mini) == MINI, len(mini)
    assert [m["titles"] for m in mini] == [["Part/Night 1"], ["Part/Night 2"]], \
        [m["titles"] for m in mini]
    assert [m["air"] for m in mini] == ["2003-12-08", "2003-12-09"], mini

    # ---- Razor, its own section on the list page ----
    razor_seg = section_between("''Razor'' (2007)", "Season 4 (2008–09)")
    razor = [row(b) for *_, b in wiki.episodes(razor_seg)]
    assert len(razor) == 1 and razor[0]["titles"] == ["Razor"], razor
    assert razor[0]["overall"] == [54, 55], razor
    assert razor[0]["air"] == "2007-11-24", razor

    # ---- The Plan, the closing section ----
    plan_seg = listing[heads["''The Plan'' (2009)"]:]
    plan_seg = plan_seg[:plan_seg.index("\n==Webisodes")]
    plan = [row(b) for *_, b in wiki.episodes(plan_seg)]
    assert len(plan) == 1 and plan[0]["titles"] == ["The Plan"], plan
    assert plan[0]["air"] == "2009-10-27", plan       # Blu-ray/DVD
    assert plan[0]["air2"] == "2010-01-10", plan      # Sci-Fi Channel

    # ---- the four seasons, from the transcluded season articles ----
    seasons = {}
    for n in (1, 2, 3, 4):
        text = wiki.wikitext(SEASON_PAGE % n, cache_dir=HERE)
        assert text, "season %d page unavailable" % n
        rows = [row(b) for *_, b in wiki.episodes(text)]
        if n == 4:
            # the page opens with Razor as a season-4 "episode 0"
            lead = rows.pop(0)
            assert lead["titles"] == ["Razor"] and lead["e"] == 0, lead
        span = []
        for r in rows:
            span += list(range(r["e"], r["e2"] + 1))
        assert span == list(range(1, EXPECT[n] + 1)), (n, span)
        seasons[str(n)] = rows

    # ---- overall numbering: season 1 -> Razor -> season 4, no gaps ----
    overall = []
    for n in (1, 2, 3):
        for r in seasons[str(n)]:
            overall += list(range(r["overall"][0], r["overall"][1] + 1))
    overall += [54, 55]
    for r in seasons["4"]:
        overall += list(range(r["overall"][0], r["overall"][1] + 1))
    assert overall == list(range(1, 77)), overall[:5] + overall[-5:]

    data = {
        "source": {
            "list": LIST_PAGE,
            "seasons": [SEASON_PAGE % n for n in (1, 2, 3, 4)],
        },
        "stated": {str(k): v for k, v in stated.items()},
        "miniseries": mini,
        "seasons": seasons,
        "razor": razor[0],
        "plan": plan[0],
    }
    out = HERE / "bsg.json"
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print("wrote %s" % out)
    print("  miniseries %d · seasons %s · Razor + The Plan"
          % (len(mini), "/".join(str(len(seasons[str(n)])) for n in (1, 2, 3, 4))))


if __name__ == "__main__":
    main()
