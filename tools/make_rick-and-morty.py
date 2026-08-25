#!/usr/bin/env python3
"""Generate properties/rick-and-morty.json — every episode, one row each.

    python3 tools/make_rick-and-morty.py

Nine seasons on Adult Swim, 2013 to 2026, in the order they went out. 91 rows.

WHAT IS IN. Episodes, and only episodes: the numbered run Wikipedia's
{{Series overview}} counts, 11 in season 1 and 10 in each of the eight after
it. Nothing is merged, split or re-ordered.

WHAT IS OUT, AND WHY. Adult Swim has released a lot of Rick and Morty that is
not a Rick and Morty episode, and the list article's "Other media" section is
where it lives:

  * five anime short films (Samurai & Shogun, Rick and Morty vs. Genocider,
    Summer Meets God (Rick Meets Evil), The Great Yokai Battle of Akihabara
    and Samurai and Shogun Part 2), six to eight minutes each;
  * The Non-Canonical Adventures, Lee Hardcastle's claymation webisodes;
  * the other webisodes, the Vindicators 2 shorts and an animatic scene.

Those are what the 39 {{Episode list}} blocks in the list article actually
are — the nine seasons themselves are transcluded from their own articles, so
a generator that parsed the list page alone would ship the shorts and none of
the show. None of them carry an episode number in the series' own run, none
are counted by the series overview or the infobox's num_episodes, and none are
here. A row on this list is an episode of the television series.

ORDER. Broadcast, which for this show is the only order there is: the seasons
aired as numbered blocks, in sequence, and Wikipedia's in-season and overall
numbering agree with the airdates end to end. There is no Futurama-style
production/broadcast split to choose between. Season 3 premiered unannounced
on April 1, 2017 and then paused until July 30; that is a gap in the calendar,
not a gap in the order, so the rows sit where the numbering puts them.

WEIGHTS. None, deliberately, and this is not an oversight to be fixed later.
Wikipedia documents one running time for the series (22 minutes, from the
television infobox) and none per episode, so there is no verifiable per-row
number to weight with. Half-weighting is worse than not weighting: the reader
resolves `WEIGHT = x.w >= 0 ? x.w : 1`, so a row with no `w` on an otherwise
weighted list silently counts as a full hour. Either every row carries a real
runtime or no row does. No row does, and main() asserts that before writing.

THE BLURB CARRIES NO COUNT. The card prints the generated total three lines
above it; a hard-coded number in the blurb only survives until the next season
airs, and five other lists already contradict themselves that way.

Everything is machine-read from the cached Wikipedia wikitext in
scratch/rick-and-morty/ — "List of Rick and Morty episodes", the nine season
articles and the series article. Nothing is typed in from memory. Before
anything is written: each season's parsed row count is asserted against that
season's episodesN in the list article's own {{Series overview}}; each
season's in-season numbering is asserted to run 1..N; the overall numbering is
asserted contiguous 1..91; the series infobox's own num_episodes and
num_seasons are asserted to agree; and the last airdate parsed is asserted to
match the list article's {{Aired episodes}} stamp, which is what says season 9
finished rather than being mid-run.
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop, wiki  # noqa: E402

SLUG = "rick-and-morty"
CACHE = prop.ROOT / "scratch" / SLUG
LIST_PAGE = "List of Rick and Morty episodes"
SERIES_PAGE = "Rick and Morty"
SEASONS = list(range(1, 10))

TOTAL = 91  # asserted three ways below, never assumed

# The one season that needs a sentence. Everything else is a season of the
# show and says so by existing.
INTRO = {
    7: "The first season without co-creator Justin Roiland, who was removed "
       "from the show in January 2023. Ian Cardoni and Harry Belden take over "
       "the title roles from here.",
}


def text(page):
    t = wiki.wikitext(page, cache_dir=CACHE)
    assert t, "no wikitext for %r" % page
    return t


def airdate(block):
    """The first {{Start date}} in an episode block, as (y, m, d)."""
    m = re.search(r"\{\{Start date\|\s*(\d{4})\s*\|\s*(\d{1,2})\s*\|"
                  r"\s*(\d{1,2})", block)
    assert m, "no airdate in %r" % block[:80]
    return tuple(int(g) for g in m.groups())


def year_span(years):
    a, b = min(years), max(years)
    if a == b:
        return str(a)
    return "%d–%02d" % (a, b % 100) if a // 100 == b // 100 else "%d–%d" % (a, b)


def series_overview(list_text):
    """{season number: episode count} from the list article's own table."""
    seg = re.search(r"\{\{Series overview(.*?)\n\}\}", list_text, re.S)
    assert seg, "no series overview"
    counts = {int(m.group(1)): int(m.group(2)) for m in
              re.finditer(r"\|\s*episodes(\d+)\s*=\s*(\d+)", seg.group(1))}
    assert counts, "series overview carries no episode counts"
    assert sorted(counts) == SEASONS, \
        "series overview lists seasons %s, expected %s" % (sorted(counts),
                                                           SEASONS)
    return counts


def aired_stamp(list_text):
    """The list article's own {{Aired episodes}} date and airing season."""
    m = re.search(r"\{\{Aired episodes\|(\d{4})\|(\d{1,2})\|(\d{1,2})"
                  r"([^}]*)\}\}", list_text)
    assert m, "no {{Aired episodes}} stamp on the list article"
    airing = re.search(r"airing\s*=\s*(\d+)", m.group(4))
    assert airing, "aired stamp names no airing season"
    return tuple(int(g) for g in m.groups()[:3]), int(airing.group(1))


def read_episodes():
    """{season: [(overall, in_season, title, (y, m, d))]}.

    Every season has its own article; the list page only transcludes them.
    A season parsed from the list page instead would pick up the webisode
    tables, so this never reads episodes from there."""
    out = {}
    for n in SEASONS:
        raw = wiki.episodes(text("Rick and Morty season %d" % n))
        assert raw, "season %d parsed empty" % n
        rows = [(o, s, t, airdate(b)) for o, s, t, _, b in raw]
        for o, s, t, _ in rows:
            assert o and s and t, "season %d row incomplete: %r" % (n, (o, s, t))
        assert [s for _, s, _, _ in rows] == list(range(1, len(rows) + 1)), \
            "season %d numbering is not 1..%d" % (n, len(rows))
        dates = [d for _, _, _, d in rows]
        assert dates == sorted(dates), \
            "season %d airdates are not in broadcast order" % n
        out[n] = rows
    return out


def main():
    list_text = text(LIST_PAGE)
    overview = series_overview(list_text)
    episodes = read_episodes()

    # 1. the source article's own table is the check on every count parsed
    for n in SEASONS:
        assert len(episodes[n]) == overview[n], \
            "season %d: parsed %d rows, overview says %d" \
            % (n, len(episodes[n]), overview[n])

    # 2. the list article must still be transcluding the season articles; if
    # it ever inlines them, read_episodes' one-article-per-season assumption
    # needs revisiting rather than silently half-working
    for n in SEASONS:
        assert re.search(r"\{\{main\|Rick and Morty season %d\}\}" % n,
                         list_text), \
            "list article no longer points at the season %d article" % n

    # 3. overall numbering must run 1..91 unbroken or a season is missing
    numbered = sorted(o for n in SEASONS for o, _, _, _ in episodes[n])
    assert numbered == list(range(1, TOTAL + 1)), \
        "overall episode numbering is not contiguous 1..%d" % TOTAL

    # 4. the series infobox counts the run independently of the list article
    ib = wiki.infobox(text(SERIES_PAGE), kind="television")
    assert ib, "no television infobox on the series article"
    assert ib("num_episodes").strip() == str(TOTAL), \
        "series infobox says %r episodes, parsed %d" % (ib("num_episodes"),
                                                        TOTAL)
    assert ib("num_seasons").strip() == str(len(SEASONS)), \
        "series infobox says %r seasons, parsed %d" % (ib("num_seasons"),
                                                       len(SEASONS))
    # the one running time the encyclopedia documents — the reason for no `w`
    assert re.fullmatch(r"\d+ minutes", ib("runtime").strip()), \
        "series runtime is no longer a single value: %r" % ib("runtime")

    # 5. nothing is mid-run: the article's own stamp must name the last season
    # and the last airdate parsed
    stamp_date, airing = aired_stamp(list_text)
    assert airing == SEASONS[-1], \
        "aired stamp is tracking season %d, not %d" % (airing, SEASONS[-1])
    last = episodes[SEASONS[-1]][-1][3]
    assert last == stamp_date, \
        "last episode aired %s, stamp says %s" % (last, stamp_date)

    sections = []
    for n in SEASONS:
        rows = episodes[n]
        sec = {
            "id": "s%d" % n,
            "title": "Season %d" % n,
            "sub": prop.join_bits(year_span([d[0] for _, _, _, d in rows]),
                                  "%d episodes" % len(rows)),
            "items": [{"id": "rm-s%de%d" % (n, s), "t": t, "n": str(s)}
                      for _, s, t, _ in rows],
        }
        if n in INTRO:
            sec["intro"] = INTRO[n]
        sections.append(sec)

    sections[0]["open"] = True

    assert [s["id"] for s in sections] == ["s%d" % n for n in SEASONS]
    total = sum(len(s["items"]) for s in sections)
    assert total == TOTAL, total
    assert sum(1 for s in sections for x in s["items"] if "w" in x) == 0, \
        "a weight crept in — this list is unweighted end to end"

    p = {
        "slug": SLUG,
        "title": "Rick and Morty",
        "subtitle": "every episode, in broadcast order",
        "kind": "tv",
        "popularity": 72,
        "year": "2013–",
        "blurb": "Adult Swim's multiverse sitcom, one row per episode, every "
                 "season in the order it aired.",
        "unit": {"one": "episode", "many": "episodes"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": "#3E7B23",
        "accentDark": "#97CE4C",
        "tiers": False,
        "notes": [
            ["Episodes only.", "Adult Swim has released a lot of Rick and "
             "Morty that is not an episode of Rick and Morty — five anime "
             "short films, Lee Hardcastle's claymation Non-Canonical "
             "Adventures, the Vindicators 2 webisodes and an animatic scene. "
             "None of them carry a number in the series' own run and none of "
             "them are here. Every row is an episode of the show."],
            ["Broadcast order, which is the only order there is.", "The "
             "seasons aired as numbered blocks in sequence, and the source "
             "article's in-season and overall numbering agree with the "
             "airdates end to end. Season 3 premiered unannounced on April "
             "Fools' Day 2017 and then paused until July; that is a gap in "
             "the calendar, not in the order."],
            ["Nothing is weighted.", "Wikipedia documents one running time "
             "for the series — 22 minutes — and none per episode, so there is "
             "no verifiable per-row number to weight with and every row counts "
             "one. A half-weighted list is worse than an unweighted one: a row "
             "with no weight would silently count as a full hour."],
            ["The show is not finished.", "Season 9 ended on July 26, 2026. "
             "Adult Swim's long-term deal runs the series through a tenth "
             "season, and its episodes join the list as they air."],
            "Titles and airdates machine-read from Wikipedia's nine Rick and "
            "Morty season articles; every season's count is asserted against "
            "the list article's own series overview, the overall numbering "
            "asserted contiguous, and the total cross-checked against the "
            "series infobox and the article's aired-episodes stamp before "
            "this builds.",
        ],
        "sections": sections,
    }

    out = prop.write(p)
    print("wrote %s — %d episodes in %d sections"
          % (out.name, total, len(sections)))
    for s in sections:
        print("   %-12s %3d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
