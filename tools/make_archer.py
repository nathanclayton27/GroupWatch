#!/usr/bin/env python3
"""Generate properties/archer.json — every episode, one row each.

    python3 tools/make_archer.py

Fourteen seasons of Adam Reed's animated spy comedy, FX then FXX, in the order
they went out. 145 rows.

WHAT IS IN. Episodes, and only episodes: the numbered run Wikipedia's
{{Series overview}} counts, season by season — 10, 13, 13, 13, 13, 13, 10, 8,
8, 9, 8, 8, 8 and 11. Nothing is merged, split or re-ordered.

THE SERIES IS FINISHED, AND THE SOURCE SAYS SO FOUR WAYS. The one thing worth
being careful about here is season 14: the {{Series overview}} gives it no
`end14`, because the season is split into a broadcast run (`episodes14A` = 8,
ending October 11, 2023) and a three-part finale (`episodes14B` = 3,
`released14B` December 17, 2023), and the template carries the second half's
date under `released` rather than `end`. The list article also carries no
{{Aired episodes}} stamp, which on a mid-run show is what says "still going".
None of that is evidence of an unfinished season, and four independent
statements in the cached wikitext close it — all four asserted in main():

  * the series infobox's `last_aired` for the FXX run is a closed
    {{End date|2023|12|17}}, and the season 14 article's own infobox carries
    the same closed `last_aired`;
  * the series infobox counts num_episodes = 145 and num_seasons = 14, which
    is exactly what this parses;
  * the list article's lead says, in the past tense, "During the course of the
    series, 145 episodes of Archer aired over fourteen seasons, between
    September 17, 2009 and December 17, 2023" — count and both dates are
    machine-read from that sentence and asserted against the parsed rows; and
  * the same lead calls season 14 "the fourteenth and final season" and names
    the three-part finale, whose title is asserted against the season 14
    article's own episode block.

So nothing is excluded for want of an airdate. Every one of the 145 rows has a
date parsed from a {{Start date}} in the source.

THE THREE-PART FINALE IS THREE ROWS. Archer: Into the Cold aired as a single
block on December 17, 2023 and is numbered 143, 144 and 145 — one
{{Episode list}} with NumParts = 3, one RTitle, no titles for the individual
parts. This list follows the numbering: three rows, each carrying the finale's
one real title and a note saying which part it is and that all three aired
together. Inventing three part-titles the source does not give would be worse,
and collapsing it to one row would put season 14 at 9 against the overview's
11 and break the overall numbering at 143. The source itself frames the block
as three episodes under an {{Episode table/part}} headed "Series finale", and
that heading is asserted too.

SEASON SUBTITLES ARE SOURCED, NOT REMEMBERED. Four seasons have titles of
their own — Archer Vice, Archer Dreamland, Archer Danger Island and Archer
1999. Each is read from `season_name` in that season article's
{{Infobox television season}}, and cross-checked against the subtitle in the
list article's own section heading; the two do not always word it identically
(the list article heads season 9 "Danger Island" and season 10 "Archer 1999",
while the overview's link text says "Archer Danger Island" and "Archer: 1999"),
so the check is containment rather than equality and the season article's
`season_name` wins. Seasons with no `season_name` are asserted to have no
subtitle in the heading either, so a name can never quietly go missing.

ORDER. Broadcast, which for this show is the only order there is: the seasons
aired as numbered blocks in sequence, and the source's in-season and overall
numbering agree with the airdates end to end. Two-episode premieres (seasons
11, 12 and 14) put two rows on one date; that is a same-day pair, not a gap,
so the airdate check is non-decreasing rather than strictly increasing.

WEIGHTS. None, deliberately, and this is not an oversight to be fixed later.
Wikipedia documents a single series-level running time — "18–24 minutes", a
range, in the television infobox — and nothing per episode: not one of the 144
{{Episode list}} blocks carries a runtime field, which main() checks rather
than assumes. So there is no verifiable per-row number to weight with.
Half-weighting is worse than not weighting: the reader resolves
`WEIGHT = x.w >= 0 ? x.w : 1`, so a row with no `w` on an otherwise weighted
list silently counts as a full hour. Either every row carries a real runtime or
no row does. No row does, and main() asserts that before writing.

THE BLURB CARRIES NO COUNT. The card prints the generated total three lines
above it; a hard-coded number in the blurb only survives until someone revives
the show, and five other lists already contradict themselves that way.

Everything is machine-read from the cached Wikipedia wikitext in
scratch/archer/ — "List of Archer episodes", the fourteen season articles and
the series article. Nothing is typed in from memory. Before anything is
written: each season's parsed row count is asserted against BOTH that season's
episodesN in the list article's {{Series overview}} and num_episodes in the
season article's own infobox; each season's in-season numbering is asserted to
run 1..N; each season's first and last parsed airdates are asserted against
the season infobox's first_aired and last_aired; each section's year span is
asserted against the year span in the list article's section heading; the
overall numbering is asserted contiguous 1..145; and the accent pair is
asserted unused by every other property on disk.
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop, wiki  # noqa: E402

SLUG = "archer"
CACHE = prop.ROOT / "scratch" / SLUG
LIST_PAGE = "List of Archer episodes"
SERIES_PAGE = "Archer (2009 TV series)"
SEASONS = list(range(1, 15))

TOTAL = 145  # asserted four ways below, never assumed

ACCENT = "#0F4C5C"       # mid-century spy: the deep teal of the ISIS office
ACCENT_DARK = "#FF6F59"  # ...against the coral of the title cards

MONTHS = {m: i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"], 1)}
NUMBER_WORDS = {"fourteen": 14}

# Only where a season does something structurally different enough that a
# reader picking a starting point needs to know. Kept free of plot turns.
INTRO = {
    5: "The first season with a title of its own, and a single story rather "
       "than a case a week: the agency is gone by the end of the premiere and "
       "the cast spends thirteen episodes somewhere else entirely.",
    8: "The show moves from FX to FXX, and into the first of three seasons "
       "that leave the spy agency behind — each with its own title, setting "
       "and genre, and each a self-contained story.",
    11: "Back to the spy-agency format the first seven seasons ran on.",
    14: "The final season. Its last three episodes are the finale, Archer: "
        "Into the Cold, which aired as one block on December 17, 2023.",
}


def text(page):
    t = wiki.wikitext(page, cache_dir=CACHE)
    assert t, "no wikitext for %r" % page
    return t


def date_in(field, kind="Start"):
    """The first {{Start date}} / {{End date}} in a chunk, as (y, m, d).

    The leading-space form — `{{Start date |2014|4|7}}` — is live in season 5
    and season 11, so the pipe cannot be anchored to the template name."""
    m = re.search(r"\{\{%s date\s*\|\s*(\d{4})\s*\|\s*(\d{1,2})\s*\|"
                  r"\s*(\d{1,2})" % kind, field or "", re.I)
    assert m, "no %s date in %r" % (kind.lower(), (field or "")[:80])
    return tuple(int(g) for g in m.groups())


def prose_date(s):
    """"December 17, 2023" -> (2023, 12, 17)."""
    m = re.fullmatch(r"([A-Z][a-z]+) (\d{1,2}), (\d{4})", s.strip())
    assert m and m.group(1) in MONTHS, "unparseable date %r" % s
    return (int(m.group(3)), MONTHS[m.group(1)], int(m.group(2)))


def fmt_date(d):
    names = {v: k for k, v in MONTHS.items()}
    return "%s %d, %d" % (names[d[1]], d[2], d[0])


def year_span(years):
    a, b = min(years), max(years)
    if a == b:
        return str(a)
    return "%d–%02d" % (a, b % 100) if a // 100 == b // 100 else "%d–%d" % (a, b)


def series_overview(list_text):
    """{season number: episode count} from the list article's own table.

    `episodes14A` and `episodes14B` split season 14's eleven into the eight
    broadcast in the autumn and the three-part finale in December; the pattern
    requires the season number to be followed straight by `=`, so only the
    whole-season `episodes14 = 11` is read and the halves cannot double-count.
    """
    seg = re.search(r"\{\{Series overview(.*?)\n\}\}", list_text, re.S)
    assert seg, "no series overview"
    counts = {int(m.group(1)): int(m.group(2)) for m in
              re.finditer(r"\|\s*episodes(\d+)\s*=\s*(\d+)", seg.group(1))}
    assert counts, "series overview carries no episode counts"
    assert sorted(counts) == SEASONS, \
        "series overview lists seasons %s, expected %s" % (sorted(counts),
                                                           SEASONS)
    # the split that explains the missing end14 — if it ever collapses back
    # into a single block, the finale reasoning below needs re-reading
    parts = {m.group(1): int(m.group(2)) for m in
             re.finditer(r"\|\s*episodes14([AB])\s*=\s*(\d+)", seg.group(1))}
    assert parts == {"A": 8, "B": 3}, \
        "season 14 is no longer split 8 + 3: %r" % parts
    assert parts["A"] + parts["B"] == counts[14], \
        "season 14's halves do not sum to %d" % counts[14]
    assert re.search(r"\|\s*released14B\s*=\s*\{\{Start date\|2023\|12\|17",
                     seg.group(1)), \
        "the finale's release date is no longer stamped on the overview"
    return counts


def headings(list_text):
    """{season: (subtitle or '', year span)} from the article's own headings."""
    out = {}
    for m in re.finditer(r"^===\s*Season (\d+)(?::\s*(.*?))?\s*"
                         r"\((\d{4}(?:–\d{2,4})?)\)\s*===\s*$",
                         list_text, re.M):
        out[int(m.group(1))] = (wiki.clean(m.group(2) or ""), m.group(3))
    assert sorted(out) == SEASONS, \
        "list article headings cover %s, expected %s" % (sorted(out), SEASONS)
    return out


def lead_facts(list_text):
    """The three claims the article's own lead makes about the finished run.

    Returns (total, seasons, first airdate, last airdate, finale title,
    season 14 premiere)."""
    m = re.search(r"During the course of the series, (\d+) episodes of "
                  r"''Archer'' aired over ([a-z]+) seasons, between "
                  r"([A-Z][a-z]+ \d{1,2}, \d{4}) and "
                  r"([A-Z][a-z]+ \d{1,2}, \d{4})", list_text)
    assert m, "the lead no longer states the finished run in the past tense"
    seasons = NUMBER_WORDS.get(m.group(2))
    assert seasons, "unrecognised season count word %r" % m.group(2)

    f = re.search(r"fourteenth and final season premiered on "
                  r"([A-Z][a-z]+ \d{1,2}, \d{4})"
                  r".{0,400}?three-part series finale titled "
                  r"''\[\[([^\]|]+)\]\]'', which aired on "
                  r"([A-Z][a-z]+ \d{1,2}, \d{4})", list_text, re.S)
    assert f, "the lead no longer calls season 14 final and names the finale"
    assert prose_date(f.group(3)) == prose_date(m.group(4)), \
        "the lead's finale date and last-aired date disagree"

    # a mid-run show carries this stamp; a finished one does not
    assert "{{Aired episodes" not in list_text, \
        "the list article has an aired-episodes stamp again — Archer may be " \
        "running once more, and season 14 can no longer be treated as closed"

    return (int(m.group(1)), seasons, prose_date(m.group(3)),
            prose_date(m.group(4)), wiki.clean(f.group(2)),
            prose_date(f.group(1)))


def season_rows(season_text, n):
    """[(overall, in_season, title, (y,m,d), note)] for one season article.

    A block with NumParts covers several numbered episodes under one title —
    season 14's three-part finale is the only one in the series. It expands
    into one row per part, all carrying the block's single RTitle, because the
    source gives the parts no titles of their own."""
    rows = []
    for _, _, _, _, block in wiki.episodes(season_text):
        assert not re.search(r"\|\s*Runtime\s*=", block, re.I), \
            "season %d has a per-episode runtime now — revisit weights" % n

        def field(name):
            fm = re.search(r"\|\s*%s\s*=\s*(.*?)(?=\n\s*\||\Z)" % name,
                           block, re.S)
            return fm.group(1).strip() if fm else ""

        aired = date_in(field("OriginalAirDate"))
        parts = field("NumParts")
        if not parts:
            title = wiki.clean(field("Title")).strip('"')
            assert title, "season %d: an episode block has no title" % n
            rows.append((int(field("EpisodeNumber")),
                         int(field("EpisodeNumber2")), title, aired, None))
            continue

        count = int(parts)
        title = wiki.clean(field("RTitle")).strip('"')
        assert title, "season %d: a multi-part block has no title" % n
        for p in range(1, count + 1):
            rows.append((int(field("EpisodeNumber_%d" % p)),
                         int(field("EpisodeNumber2_%d" % p)), title, aired,
                         prop.join_bits(
                             "Part %d of the %s-part series finale" %
                             (p, {2: "two", 3: "three"}[count]),
                             "all %s parts aired together on %s"
                             % ({2: "two", 3: "three"}[count],
                                fmt_date(aired)))))
    return rows


def read_seasons():
    """{season: (rows, {meta})}, one article per season.

    The list page only transcludes the season articles, so nothing is ever
    parsed from there — a season inlined into the list page would silently
    pick up whatever else the page holds."""
    out = {}
    for n in SEASONS:
        t = text("Archer (season %d)" % n)
        rows = season_rows(t, n)
        assert rows, "season %d parsed empty" % n
        assert [s for _, s, _, _, _ in rows] == list(range(1, len(rows) + 1)), \
            "season %d numbering is not 1..%d" % (n, len(rows))
        dates = [d for _, _, _, d, _ in rows]
        assert dates == sorted(dates), \
            "season %d airdates are not in broadcast order" % n

        ib = wiki.infobox(t, kind="television season")
        assert ib, "no season infobox on the season %d article" % n
        network = wiki.clean(ib("network"))
        assert network in ("FX", "FXX"), \
            "season %d aired on %r, which is neither FX nor FXX" % (n, network)
        meta = {
            "name": wiki.clean(ib("season_name")),
            "episodes": int(ib("num_episodes")),
            "first": date_in(ib("first_aired")),
            "last": date_in(ib("last_aired"), "End"),
            "network": network,
        }
        assert meta["first"] == dates[0], \
            "season %d: infobox opens %s, first episode aired %s" \
            % (n, meta["first"], dates[0])
        assert meta["last"] == dates[-1], \
            "season %d: infobox closes %s, last episode aired %s" \
            % (n, meta["last"], dates[-1])
        out[n] = (rows, meta)
    return out


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
            assert hexv not in pair, \
                "%s already uses %s" % (f.stem, hexv)


def main():
    list_text = text(LIST_PAGE)
    overview = series_overview(list_text)
    heads = headings(list_text)
    lead_total, lead_seasons, lead_first, lead_last, finale, s14_start = \
        lead_facts(list_text)
    seasons = read_seasons()
    check_accent()

    # 1. two independent counts per season: the list article's overview table
    # and the season article's own infobox
    for n in SEASONS:
        rows, meta = seasons[n]
        assert len(rows) == overview[n], \
            "season %d: parsed %d rows, overview says %d" \
            % (n, len(rows), overview[n])
        assert meta["episodes"] == overview[n], \
            "season %d: infobox says %d episodes, overview says %d" \
            % (n, meta["episodes"], overview[n])

    # 2. the list article must still be transcluding the season articles; if it
    # ever inlines them, read_seasons' one-article-per-season assumption needs
    # revisiting rather than silently half-working
    for n in SEASONS:
        assert re.search(r"\{\{:Archer \(season %d\)\}\}" % n, list_text), \
            "list article no longer transcludes the season %d article" % n

    # 3. overall numbering must run 1..145 unbroken or a season is missing
    numbered = sorted(o for n in SEASONS for o, _, _, _, _ in seasons[n][0])
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
    # the one running time the encyclopedia documents — a range for the whole
    # series, nothing per episode. This is the reason for no `w`.
    assert re.fullmatch(r"\d+(–\d+)? minutes", ib("runtime").strip()), \
        "series runtime is no longer a single series-level value: %r" \
        % ib("runtime")

    # 5. the show is over. The infobox's second network block closes with an
    # {{End date}}, and it is the last date parsed.
    last_parsed = seasons[SEASONS[-1]][0][-1][3]
    ends = re.findall(r"\{\{End date\s*\|\s*(\d{4})\s*\|\s*(\d{1,2})\s*\|"
                      r"\s*(\d{1,2})", ib("last_aired"), re.I)
    assert ends, "the series infobox no longer carries a closed last-aired date"
    assert tuple(int(g) for g in ends[-1]) == last_parsed, \
        "series infobox closes %s, last episode parsed aired %s" \
        % (ends[-1], last_parsed)

    # 6. and the article's own lead says the same thing in prose
    assert lead_total == TOTAL, \
        "the lead counts %d episodes, parsed %d" % (lead_total, TOTAL)
    assert lead_seasons == len(SEASONS), \
        "the lead counts %d seasons, parsed %d" % (lead_seasons, len(SEASONS))
    assert lead_first == seasons[1][0][0][3], \
        "the lead opens %s, first episode parsed aired %s" \
        % (lead_first, seasons[1][0][0][3])
    assert lead_last == last_parsed, \
        "the lead closes %s, last episode parsed aired %s" \
        % (lead_last, last_parsed)
    assert s14_start == seasons[14][0][0][3], \
        "the lead premieres season 14 on %s, first episode aired %s" \
        % (s14_start, seasons[14][0][0][3])

    # 7. the finale: three rows, one title, and the source calling it that
    finale_rows = [r for r in seasons[14][0] if r[4]]
    assert len(finale_rows) == 3, \
        "expected a three-part finale, found %d part rows" % len(finale_rows)
    assert {r[2] for r in finale_rows} == {finale}, \
        "the season 14 article and the lead disagree on the finale's title: " \
        "%r vs %r" % ({r[2] for r in finale_rows}, finale)
    assert [r[0] for r in finale_rows] == [143, 144, 145], \
        "the finale is not episodes 143-145: %s" % [r[0] for r in finale_rows]
    assert re.search(r"\{\{Episode table/part\|[^}]*subtitle\s*=\s*"
                     r"Series finale\s*\}\}",
                     text("Archer (season 14)")), \
        "the season 14 article no longer heads the last block Series finale"

    # 8. season subtitles, from the season articles, cross-checked against the
    # list article's headings
    for n in SEASONS:
        name = seasons[n][1]["name"]
        head_sub, head_years = heads[n]
        if name:
            assert head_sub, \
                "season %d is titled %r but its heading carries no subtitle" \
                % (n, name)
            assert (head_sub.lower() in name.lower()
                    or name.lower() in head_sub.lower()), \
                "season %d: infobox says %r, heading says %r" \
                % (n, name, head_sub)
        else:
            assert not head_sub, \
                "season %d heading carries subtitle %r but the season " \
                "article names no season" % (n, head_sub)

    sections = []
    for n in SEASONS:
        rows, meta = seasons[n]
        span = year_span([d[0] for _, _, _, d, _ in rows])
        assert span == heads[n][1], \
            "season %d spans %s, the heading says %s" % (n, span, heads[n][1])
        title = "Season %d" % n
        if meta["name"]:
            title = "Season %d: %s" % (n, meta["name"])
        items = []
        for _, s, t, _, note in rows:
            item = {"id": "arch-s%de%d" % (n, s), "t": t, "n": str(s)}
            if note:
                item["note"] = note
            items.append(item)
        sec = {
            "id": "s%d" % n,
            "title": title,
            "sub": prop.join_bits(span, "%d episodes" % len(rows),
                                  meta["network"]),
            "items": items,
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
        "title": "Archer",
        "subtitle": "every episode, in broadcast order",
        "kind": "tv",
        "popularity": 64,
        "year": "2009–2023",
        "blurb": "Adam Reed's animated espionage comedy, FX then FXX — one row "
                 "per episode, every season in the order it aired, ending with "
                 "the three-part finale.",
        "unit": {"one": "episode", "many": "episodes"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": ACCENT,
        "accentDark": ACCENT_DARK,
        "tiers": False,
        "notes": [
            ["Episodes only, and all of them.", "Every row is a numbered "
             "episode of the television series, counted the way the source "
             "article's season overview counts them. Nothing is excluded for "
             "want of an airdate: all 145 rows carry a date read from the "
             "source."],
            ["The three-part finale is three rows.", "Archer: Into the Cold "
             "aired as one block on December 17, 2023 and is numbered 143, "
             "144 and 145. The source gives the three parts one shared title "
             "and no titles of their own, so each row carries that title and a "
             "note saying which part it is and that all three aired together. "
             "Collapsing them into one row would leave season 14 two short of "
             "the count its own article gives."],
            ["Broadcast order, which is the only order there is.", "The "
             "seasons aired as numbered blocks in sequence, and the source "
             "article's in-season and overall numbering agree with the "
             "airdates end to end. Seasons 11, 12 and 14 opened with two "
             "episodes on one night, so a few rows share a date; that is a "
             "double premiere, not a gap."],
            ["Four seasons have titles of their own.", "Archer Vice, Archer "
             "Dreamland, Archer Danger Island and Archer 1999 are named in "
             "the section headings the way the source names them, because a "
             "season that swaps setting and genre is worth knowing about "
             "before you start it."],
            ["Nothing is weighted.", "Wikipedia documents one running time for "
             "the series — a range, 18 to 24 minutes — and none per episode, "
             "so there is no verifiable per-row number to weight with and "
             "every row counts one. A half-weighted list is worse than an "
             "unweighted one: a row with no weight would silently count as a "
             "full hour."],
            ["The show is finished.", "145 episodes over fourteen seasons, "
             "September 17, 2009 to December 17, 2023. The series infobox "
             "carries a closed last-aired date, the season 14 article carries "
             "the same one, and the list article's lead states the whole run "
             "in the past tense — so season 14 is complete rather than "
             "mid-flight, despite the series overview leaving its end date "
             "blank."],
            "Titles and airdates machine-read from Wikipedia's fourteen Archer "
            "season articles; every season's count is asserted against both "
            "the list article's series overview and the season article's own "
            "infobox, every season's first and last airdates against that "
            "infobox, the overall numbering asserted contiguous, and the total "
            "cross-checked against the series infobox and the article's lead "
            "before this builds.",
        ],
        "sections": sections,
    }

    out = prop.write(p)
    print("wrote %s — %d episodes in %d sections"
          % (out.name, total, len(sections)))
    for s in sections:
        print("   %-28s %3d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
