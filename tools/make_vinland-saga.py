#!/usr/bin/env python3
"""Generate properties/vinland-saga.json — both seasons, every episode.

    PYTHONIOENCODING=utf-8 python tools/make_vinland-saga.py

Makoto Yukimura's manga, adapted twice over by two different studios. 48
rows: 24 episodes made by Wit Studio and broadcast July to December 2019,
and 24 made by MAPPA and broadcast January to June 2023.

THE TWO SEASONS ARE DOCUMENTED SEPARATELY, SO THEY ARE READ SEPARATELY.
"List of Vinland Saga episodes" holds no episode table of its own — it
transcludes "Vinland Saga season 1" and "Vinland Saga season 2", each of
which carries its own {{Infobox television season}}. Nothing is parsed from
the list page, because a season inlined there would silently pick up
whatever else that page holds. 24 + 24 is the answer, but it is not an
assumption: each season's parsed row count is asserted against BOTH its own
article's `num_episodes` and the list article's {{Series overview}}, and the
total against the series article's `episodes = 48`.

THE STUDIO CHANGED, AND THE SOURCE SAYS SO TWICE. The series article's
infobox gives `studio = Wit Studio (S1), MAPPA (S2)`, and its prose says
"The first season of the series was produced by Wit Studio and aired in
2019; the second season was produced by MAPPA and aired in 2023." Both are
read and asserted, and the studio is named in each section's subtitle. The
director did not change — Shūhei Yabuta is the infobox's only director, and
that is asserted too, because "different studio" is easy to over-read.

THE SEASON 2 ARTICLE'S "SHORTS" TABLE IS NOT EPISODES. Two shorts sit in a
separate table under their own heading, numbered 30.5 / 6.5 and 42.5 / 18.5.
They are outside the season's 24 and are not listed — and they are a real
hazard, not a hypothetical one: {{Episode list}} numbers parse as integers,
so 30.5 and 42.5 come back as 30 and 42 and collide head-on with genuine
episodes. This generator therefore cuts the article at the shorts heading
before parsing and asserts the heading is still where it cuts.

TWO SETS OF ENGLISH TITLES IN SEASON 2. Eleven of its episodes carry two
official English titles in one field, written `A" / "B`. The article's own
footnotes name them: the first set "are taken from Netflix and the official
anime website", the second "from Crunchyroll. For episodes where there are
none, the first set is used." So the first set is the source's own default
and is what the row carries; the Crunchyroll title goes in the row note
rather than being thrown away. Both footnotes are asserted present, because
the whole rule rests on them.

WEIGHTS: NONE. Wikipedia documents no running time for this series
anywhere — not on the series article's infobox, not on either season
article's infobox, and not on one of the 48 episode entries, all of which
main() asserts rather than assumes. Wikidata has no P2047 on the series
item, either season item, or the episode list. There is no per-episode
number to be had, and there is not even a series-level average to be
tempted by. It is all rows or none regardless, because a row with no `w` on
a weighted list silently counts as one hour; it is none, and main() asserts
none.

Everything is machine-read from the cached Wikipedia wikitext — the two
season articles, the episode list article and the series article. Nothing is
typed from memory. Before anything is written: airdates are asserted
non-decreasing and matched against each season infobox's first_aired and
last_aired and against the list article's series overview; in-season
numbering is asserted to run 1..24 for each season and the overall numbering
to run 1..48 unbroken; and the accent pair is asserted unused by every other
property on disk.
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop, wiki  # noqa: E402

SLUG = "vinland-saga"

# The wikitext cache. Nothing here is required — gwlib re-fetches and
# repopulates whichever of these exists — but a warmed cache keeps this
# generator offline and keeps it off Wikipedia's rate limiter.
CACHE = next((d for d in (prop.ROOT / "scratch" / SLUG,
                          prop.ROOT / "scratch" / "agent-frieren")
              if d.exists()), prop.ROOT / "scratch" / SLUG)

LIST_PAGE = "List of Vinland Saga episodes"
SERIES_PAGE = "Vinland Saga (TV series)"
SEASON_PAGE = "Vinland Saga season %d"

SEASONS = [1, 2]
TOTAL_EPISODES = 48
PER_SEASON = 24              # asserted, never assumed — see the docstring

# Where season 2's article stops being about episodes. Cutting here is what
# keeps the two fractional-numbered shorts out of the 24.
SHORTS_HEADING = "== Shorts =="

# The two official English title sets, and the separator the source writes
# between them inside one Title field.
TITLE_SEP = '" / "'

# Hard-coded rather than read from the clock so re-running produces the same
# file. Anything dated after this has not aired.
TODAY = (2026, 8, 25)

ACCENT = "#1F4E6B"       # cold North Sea blue
ACCENT_DARK = "#93B7BE"  # ...gone pale, for dark mode

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


NUMWORD = ["zero", "one", "two", "three", "four", "five", "six", "seven",
           "eight", "nine", "ten", "eleven", "twelve"]


def word(n):
    """Small counts read as words in prose; anything larger stays a numeral."""
    return NUMWORD[n] if 0 <= n < len(NUMWORD) else str(n)


def text(page):
    t = wiki.wikitext(page, cache_dir=CACHE)
    assert t, "no wikitext for %r" % page
    return t


def strip_refs(t):
    """Prose with the footnotes gone, for the sentences main() reads as fact."""
    t = re.sub(r"<ref[^>]*/>", "", t)
    return re.sub(r"<ref.*?</ref>", "", t, flags=re.S)


def date_in(field, kind="Start"):
    """The first {{Start date}} / {{End date}} in a chunk, as (y, m, d)."""
    m = re.search(r"\{\{%s date\s*\|\s*(\d{4})\s*\|\s*(\d{1,2})\s*\|"
                  r"\s*(\d{1,2})" % kind, field or "", re.I)
    assert m, "no %s date in %r" % (kind.lower(), (field or "")[:80])
    return tuple(int(g) for g in m.groups())


def fmt_date(d):
    return "%d %s %d" % (d[2], MONTHS[d[1] - 1], d[0])


def series_overview(list_text):
    """{season: (episodes, start, end)} from the list article's overview."""
    seg = re.search(r"\{\{Series overview(.*?)\n\}\}", list_text, re.S)
    assert seg, "no series overview on the list article"
    body = seg.group(1)
    out = {}
    for n in SEASONS:
        m = re.search(r"\|\s*episodes%d\s*=\s*(\d+)" % n, body)
        s = re.search(r"\|\s*start%d\s*=\s*([^\n]*)" % n, body)
        e = re.search(r"\|\s*end%d\s*=\s*([^\n]*)" % n, body)
        assert m and s and e, "the overview no longer documents season %d" % n
        out[n] = (int(m.group(1)), date_in(s.group(1)),
                  date_in(e.group(1), "End"))
    assert not re.search(r"\|\s*episodes%d\s*=" % (len(SEASONS) + 1), body), \
        "the overview now carries a season %d — it is airing and this list " \
        "is short" % (len(SEASONS) + 1)
    assert sum(v[0] for v in out.values()) == TOTAL_EPISODES, \
        "the overview counts %d episodes, expected %d" \
        % (sum(v[0] for v in out.values()), TOTAL_EPISODES)
    # the list page must still be transcluding rather than holding episodes
    for n in SEASONS:
        assert re.search(r"\{\{:Vinland Saga season %d\}\}" % n, list_text), \
            "the list article no longer transcludes the season %d article — " \
            "check where its episodes now live" % n
    return out


def split_titles(raw, label):
    """(title carried, alternate title or "") for one Title field.

    Season 2 writes two official English titles into one field as `A" / "B`;
    the first set is the source's own default (see the docstring), so it is
    the one the row carries."""
    parts = raw.split(TITLE_SEP)
    assert len(parts) <= 2, "%s has %d title sets: %r" % (label, len(parts), raw)
    for p in parts:
        assert p and '"' not in p, "%s title did not split cleanly: %r" % (label, raw)
    return parts[0], (parts[1] if len(parts) == 2 else "")


def english_only_note(block):
    """The source's footnote for the one episode titled in English only."""
    if not re.search(r"\{\{efn\|name=eto", block):
        return ""
    return "titled in English only in the original Japanese release"


def rows_from(season_text, n):
    """[(overall, in_season, title, alt title, (y,m,d), note)] for a season."""
    label = "season %d" % n
    seg = season_text
    if SHORTS_HEADING in seg:
        seg = seg[:seg.index(SHORTS_HEADING)]
    raw = wiki.episodes(seg)
    assert raw, "%s parsed empty" % label
    rows = []
    for o, s, t, _, block in raw:
        assert not re.search(r"\|\s*Runtime\s*=", block, re.I), \
            "%s now carries a per-episode runtime — revisit weights, because " \
            "the only reason this list is unweighted is that it did not" % label
        assert o and s and t, "%s row incomplete: %r" % (label, (o, s, t))
        title, alt = split_titles(t, "%s episode %s" % (label, s))
        rows.append((o, s, title, alt, date_in(block),
                     english_only_note(block)))
    dates = [d for _, _, _, _, d, _ in rows]
    assert dates == sorted(dates), "%s airdates are not in broadcast order" % label
    for _, s, t, _, d, _ in rows:
        assert d <= TODAY, \
            "%s episode %d (%r) is dated %s, which has not happened yet" \
            % (label, s, t, fmt_date(d))
    return rows


def season_meta(season_text, n):
    """{episodes, first, last, network} from the season article's own infobox."""
    ib = wiki.infobox(season_text, kind="television season")
    assert ib, "no season infobox on the season %d article" % n
    assert not ib("runtime").strip(), \
        "season %d now documents a runtime — revisit weights" % n
    network = wiki.clean(ib("network")).split(",")[0].strip()
    assert network, "season %d names no network" % n
    return {"episodes": int(ib("num_episodes")),
            "first": date_in(ib("first_aired")),
            "last": date_in(ib("last_aired"), "End"),
            "network": network}


def series_facts():
    """Studios by season, the director, and the run, from the series article.

    The studio change is the one fact this list is built to show, so it is
    read from the infobox AND confirmed against the article's own prose."""
    t = text(SERIES_PAGE)
    ib = wiki.infobox(t, kind=r"animanga/Video")
    assert ib, "no animanga video infobox on the series article"
    assert ib("type").strip() == "tv series", \
        "the series infobox is no longer describing a tv series"
    assert not ib("runtime").strip(), \
        "the series now documents a running time — revisit weights, because " \
        "the only reason this list is unweighted is that it did not"
    assert ib("episodes").strip() == str(TOTAL_EPISODES), \
        "the series infobox says %r episodes, this list carries %d" \
        % (ib("episodes"), TOTAL_EPISODES)

    pairs = re.findall(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\] \(\{\{Abbr\|S(\d)\|",
                       ib("studio"))
    studios = {int(s): name for name, s in pairs}
    assert sorted(studios) == SEASONS, \
        "the infobox attributes studios to seasons %s, expected %s" \
        % (sorted(studios), SEASONS)
    assert len(set(studios.values())) == len(SEASONS), \
        "both seasons are now credited to the same studio: %r" % studios

    prose = re.sub(r"\s+", " ", strip_refs(t))
    m = re.search(r"The first season of the series was produced by "
                  r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\] and aired in (\d{4}); the "
                  r"second season was produced by \[\[([^\]|]+)(?:\|[^\]]+)?"
                  r"\]\] and aired in (\d{4})\.", prose)
    assert m, "the series article no longer states the studio change in " \
              "prose — the whole shape of this list rests on it"
    assert (m.group(1), m.group(3)) == (studios[1], studios[2]), \
        "the prose credits %r and %r, the infobox credits %r" \
        % (m.group(1), m.group(3), studios)

    director = wiki.clean(ib("director"))
    assert director and "," not in director, \
        "the series now credits more than one director (%r) — the section " \
        "intros say the director did not change" % director
    return studios, director, (int(m.group(2)), int(m.group(4)))


def premiere_size(list_text):
    """How many episodes shared the opening broadcast, from the source."""
    prose = re.sub(r"\s+", " ", strip_refs(list_text))
    m = re.search(r"The anime aired from (\w+ \d+, \d{4}), with the first "
                  r"(\w+) episodes, and finished on (\w+ \d+, \d{4})\.", prose)
    assert m, "the list article no longer describes the three-episode opening"
    words = {"two": 2, "three": 3, "four": 4}
    assert m.group(2) in words, "the opening is %r episodes" % m.group(2)
    return words[m.group(2)]


def check_title_footnotes(season2_text):
    """The two footnotes that decide which English title a row carries."""
    a = re.search(r"\{\{efn\|name=NFLXTitle\|The first set of English "
                  r"translated titles are taken from \[\[Netflix\]\] and the "
                  r"official anime website\.\}\}", season2_text)
    assert a, "the Netflix/official-site title footnote is gone — this list " \
              "carries the first title set because of it"
    b = re.search(r"\{\{efn\|name=CRTitle\|The second set of English "
                  r"translated titles are taken from \[\[Crunchyroll\]\]\. "
                  r"For episodes where there are none, the first set is "
                  r"used\.\}\}", season2_text)
    assert b, "the Crunchyroll title footnote is gone"


def check_shorts_excluded(season2_text):
    """The shorts must still be shorts, and still be outside the season."""
    assert SHORTS_HEADING in season2_text, \
        "season 2's shorts heading moved — this generator cuts the article " \
        "there, and {{Episode list}} numbers parse as integers, so 30.5 and " \
        "42.5 would come back as 30 and 42 and collide with real episodes"
    seg = season2_text[season2_text.index(SHORTS_HEADING):]
    nums = re.findall(r"\|\s*EpisodeNumber\s*=\s*([\d.]+)", seg)
    assert nums and all("." in n for n in nums), \
        "the shorts are no longer all fractionally numbered (%r) — one of " \
        "them may now be a full episode of the season" % nums
    return len(nums)


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


def main():
    list_text = text(LIST_PAGE)
    season_text = {n: text(SEASON_PAGE % n) for n in SEASONS}

    overview = series_overview(list_text)
    studios, director, prose_years = series_facts()
    opening = premiere_size(list_text)
    check_title_footnotes(season_text[2])
    n_shorts = check_shorts_excluded(season_text[2])
    check_accent()

    seasons = {n: rows_from(season_text[n], n) for n in SEASONS}
    meta = {n: season_meta(season_text[n], n) for n in SEASONS}

    # 1. three independent counts per season: this parse, the season
    # article's own infobox, and the list article's overview
    for n in SEASONS:
        rows = seasons[n]
        assert len(rows) == PER_SEASON, \
            "season %d parsed %d rows, expected %d" % (n, len(rows), PER_SEASON)
        assert meta[n]["episodes"] == len(rows), \
            "season %d: the infobox says %d episodes, %d parsed" \
            % (n, meta[n]["episodes"], len(rows))
        assert overview[n][0] == len(rows), \
            "season %d: the overview says %d episodes, %d parsed" \
            % (n, overview[n][0], len(rows))
        assert [s for _, s, _, _, _, _ in rows] == list(range(1, len(rows) + 1)), \
            "season %d numbering is not 1..%d" % (n, len(rows))
        assert meta[n]["first"] == rows[0][4] == overview[n][1], \
            "season %d opens %s / %s / %s in three places" \
            % (n, meta[n]["first"], rows[0][4], overview[n][1])
        assert meta[n]["last"] == rows[-1][4] == overview[n][2], \
            "season %d closes %s / %s / %s in three places" \
            % (n, meta[n]["last"], rows[-1][4], overview[n][2])
        assert rows[0][4][0] == prose_years[n - 1], \
            "season %d aired in %d, the prose says %d" \
            % (n, rows[0][4][0], prose_years[n - 1])

    # 2. overall numbering contiguous, or a season is missing
    numbered = sorted(o for n in SEASONS for o, _, _, _, _, _ in seasons[n])
    assert numbered == list(range(1, TOTAL_EPISODES + 1)), \
        "overall episode numbering is not contiguous 1..%d" % TOTAL_EPISODES

    # 3. the opening broadcast really did carry more than one episode
    first_dates = {d for _, s, _, _, d, _ in seasons[1] if s <= opening}
    assert len(first_dates) == 1, \
        "the first %d episodes carry %d airdates, so they were not one " \
        "broadcast" % (opening, len(first_dates))
    assert seasons[1][opening][4] != seasons[1][0][4], \
        "episode %d shares the opening airdate — more than %d episodes went " \
        "out together" % (opening + 1, opening)

    alts = sum(1 for n in SEASONS for r in seasons[n] if r[3])
    assert alts and all(not r[3] for r in seasons[1]), \
        "the alternate English titles are no longer confined to season 2"

    sections = []
    for n in SEASONS:
        rows = seasons[n]
        items = []
        for _, s, t, alt, d, extra in rows:
            bits = []
            if n == 1 and s == 1:
                bits.append("series premiere")
                bits.append("episodes 1–%d aired back to back" % opening)
            elif n == 1 and s <= opening:
                bits.append("part of the opening broadcast")
            if s == len(rows):
                bits.append("season finale")
            if extra:
                bits.append(extra)
            if alt:
                bits.append("Crunchyroll titles it \"%s\"" % alt)
            row = {"id": "vinland-s%de%d" % (n, s), "t": t, "n": str(s)}
            note = prop.join_bits(*bits)
            if note:
                row["note"] = note
            items.append(row)
        sections.append({
            "id": "s%d" % n,
            "title": "Season %d" % n,
            "sub": prop.join_bits(str(rows[0][4][0]),
                                  "%d episodes" % len(rows),
                                  studios[n], meta[n]["network"]),
            "items": items,
        })

    sections[0]["intro"] = (
        "%s's twenty-four, %s to %s. The first %s went out back to back "
        "on the opening night."
        % (studios[1], fmt_date(seasons[1][0][4]),
           fmt_date(seasons[1][-1][4]), word(opening)))
    sections[0]["open"] = True
    sections[1]["intro"] = (
        "A different studio: %s made the second season, %s to %s. %s directs "
        "both, and the count is the same twenty-four."
        % (studios[2], fmt_date(seasons[2][0][4]),
           fmt_date(seasons[2][-1][4]), director))

    total = sum(len(s["items"]) for s in sections)
    assert total == TOTAL_EPISODES, "%d rows, expected %d" % (total, TOTAL_EPISODES)
    assert sum(1 for s in sections for x in s["items"] if "w" in x) == 0, \
        "a weight crept in — this list is unweighted end to end"

    p = {
        "slug": SLUG,
        "title": "Vinland Saga",
        "subtitle": "both seasons, two studios",
        "kind": "anime",
        "popularity": 60,
        "year": "2019–2023",
        "blurb": "Thorfinn's two seasons in broadcast order — 24 episodes "
                 "from Wit Studio, then 24 from MAPPA.",
        "unit": {"one": "episode", "many": "episodes"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": ACCENT,
        "accentDark": ACCENT_DARK,
        "tiers": False,
        "notes": [
            ["Two seasons, two studios.",
             "%s made the %d season and %s made the %d one — the source says "
             "so in its infobox and again in its prose, and each section here "
             "names which. What did not change is the director: %s took both."
             % (studios[1], prose_years[0], studios[2], prose_years[1],
                director)],
            ["Twenty-four each, taken from the source rather than assumed.",
             "The two seasons are documented on separate articles, so the "
             "counts are read separately and cross-checked three ways before "
             "this builds: each season's parsed rows against that season's "
             "own infobox, against the episode list article's series "
             "overview, and the total against the series article's own figure "
             "of %d. The first and last airdates are checked the same three "
             "ways." % TOTAL_EPISODES],
            ["The opening night was %s episodes." % word(opening),
             "The first season began on %s with episodes 1 to %d in one "
             "sitting. They are %s rows here because the source lists %s "
             "episodes, and each of them says so."
             % (fmt_date(seasons[1][0][4]), opening, word(opening),
                word(opening))],
            ["Two sets of English titles in the second season.",
             "%s of its episodes carry two official English titles. The "
             "source's own footnotes say the first set comes from Netflix and "
             "the official Japanese site and the second from Crunchyroll, and "
             "that where Crunchyroll has none the first set is used — so the "
             "first set is the default and it is what each row carries. The "
             "Crunchyroll title sits in the row note rather than being "
             "dropped." % word(alts).capitalize()],
            ["The second season's %s shorts are not listed." % word(n_shorts),
             "Its article files them in a table of their own, numbered 30.5 "
             "and 42.5 rather than given episode numbers. They are outside "
             "the 24 the source counts, so they are outside this list."],
            ["Nothing is weighted, and hours are not tracked on this list.",
             "Wikipedia documents no running time for this series at all: not "
             "on the series article, not on either season article, and not on "
             "one of the 48 episode entries — every one of those absences is "
             "asserted before this builds. Wikidata holds no duration for the "
             "series, either season, or the episode list either. There is no "
             "per-episode figure to use and no series-level average to be "
             "tempted by, and a part-weighted list would be worse than an "
             "unweighted one, because a row with no weight silently counts as "
             "a full hour. So every row counts one."],
            "Titles and airdates machine-read from Wikipedia's \"Vinland Saga "
            "season 1\" and \"Vinland Saga season 2\" articles, with counts "
            "and dates cross-checked against \"List of Vinland Saga "
            "episodes\" and \"Vinland Saga (TV series)\" before this builds.",
        ],
        "sections": sections,
    }

    out = prop.write(p)
    print("wrote %s — %d rows in %d sections" % (out.name, total, len(sections)))
    for n, s in zip(SEASONS, sections):
        rows = seasons[n]
        print("   %-10s %3d  %-42s %s – %s"
              % (s["title"], len(s["items"]), s["sub"],
                 fmt_date(rows[0][4]), fmt_date(rows[-1][4])))
    print("   unweighted: no runtime published anywhere for any of %d rows"
          % total)
    print("   %d rows carry a second official English title; %d shorts excluded"
          % (alts, n_shorts))


if __name__ == "__main__":
    main()
