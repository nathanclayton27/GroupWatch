#!/usr/bin/env python3
"""Generate properties/flcl.json — all five FLCL series, 24 episodes, one list.

    python3 tools/make_flcl.py

Kazuya Tsurumaki's six-episode OVA and the four runs that followed it, in
release order: FLCL (2000–2001), FLCL Progressive (2018), FLCL Alternative
(2018), FLCL: Grunge (2023) and FLCL: Shoegaze (2023). The sections are the
five series; the rows are the 24 episodes the source counts between them.

THE COUNTS ARE NOT SIX EACH, AND THAT IS THE FIRST THING TO CHECK. The
original, Progressive and Alternative are six apiece; Grunge and Shoegaze are
three apiece. 6 + 6 + 6 + 3 + 3 = 24, and main() asserts every one of those
five numbers three independent ways before anything is written: the
`episodes<N>` fields in the list article's {{Series overview}}, the
`num_episodes` field in each season article's own {{Infobox television
season}}, and the `episodes` field in the matching {{Infobox animanga/Video}}
block on the FLCL article. The parsed row count has to agree with all three.

THE FOUR LATER SERIES ARE A DIFFERENT PRODUCTION FROM THE ORIGINAL, AND THE
SOURCE SAYS SO — so it rides in the section subs, the way vinland-saga's two
studios do and the-big-o's second-season funding does. Every sentence below is
asserted in main() before this builds:

  * the FLCL article: "The original ''FLCL'' series was released as an
    [[original video animation]] (OVA) series" — six episodes to video in
    Japan, April 2000 to March 2001, from a committee the article names as
    Gainax and Production I.G;
  * the same article's Sequel seasons section: "On August 31, 2015, [[Anime
    News Network]] reported that Production I.G may have been planning a
    continuation or remake of the OVA series after announcing their
    acquisition of the rights to ''FLCL'' from production studio Gainax." The
    rights left the studio that made the original;
  * and then: "On March 24, 2016, via [[Toonami]]'s official Facebook and
    Tumblr pages, it was announced that [[Cartoon Network]]'s [[Adult Swim]]
    will produce 12 new episodes of ''FLCL'' in cooperation with Production
    I.G.";
  * the Progressive and Alternative articles, both: "is produced by
    [[Production I.G]], [[Toho]], and [[Adult Swim]]'s production arm
    [[Williams Street]]", broadcast on Adult Swim's Toonami block;
  * the Grunge article: "is produced by [[Production I.G]] and [[Adult
    Swim]]'s production arm [[Williams Street]]. ''Grunge'' was animated by
    MontBlanc Pictures"; and the Shoegaze article, the same with NUT.

Different studios, a different decade, a different broadcaster. THAT IS ALL IT
IS. Nothing in this list rates the later series against the original, and the
copy must never start: the same section of the same article also records that
Tsurumaki supervised the 2018 pair and that the original character designer
came back for them, which is asserted here too so the framing stays even. A
reader can decide for themselves whether to go past the original.

NUMBERING IS THE SOURCE'S, AND THE SOURCE GIVES TWO. Every episode block
carries an EpisodeNumber (1 to 24 straight through the five series) and an
EpisodeNumber2 (1..6, 1..6, 1..6, 1..3, 1..3). The rows use the second,
because each section IS one of the five series and "Alternative, episode 3"
is how anyone refers to it; the overall numbering is asserted contiguous
1..24 anyway, so a missing episode still fails the build.

WEIGHTS: NONE, AND THE HUNT IS THE FINDING — 0 of 24 rows resolved. Four
places a per-episode running time could live were checked; scratch/agent-flcl/
holds the probes, and main() re-asserts the offline half of it every build:

  1. Each episode's own Wikipedia article. There are none. All 24 titles were
     probed bare, as "<title> (FLCL)" and as "<title> (FLCL episode)" — 72
     candidates, of which 12 answer with a page: three are redirects into the
     FLCL season 1 article (Brittle Bullet, FLCLimax, Marquis de Carabas
     (FLCL)), one is the FLCL article itself (Fooly Cooly), three are
     disambiguation pages (Fire Starter, Full Swing, Marquis de Carabas), and
     five are unrelated subjects that happen to share a title — a the Pillows
     compilation album, a K-pop group, a mall in Christchurch, a Taylor Swift
     single and a Japanese given name. A separate probe of the common
     misspelling "Firestarter" turns up the same two shapes again, a
     disambiguation page and a redirect into the season 1 article. Not one
     Title field in any of the five episode tables is a wikilink either, which
     main() asserts — a wikilinked title is what an episode article would look
     like from here.
  2. Per-episode Wikidata P2047. There are no per-episode Wikidata items at
     all. The series is Q92572; its five P527 has-parts are the five season
     items (Q111954103, Q111953383, Q111953468, Q122422436, Q122790739) and
     nothing else. A haswbstatement search for items declaring P179, P361 or
     P4908 against the series or against any season returns only those same
     five. Not one of the six items carries P2047, and label searches for the
     distinctive titles (FLCLimax, LooPQR, Freebie Honey, Furu-Bari,
     Gene-Bato, Grown-Up Wannabe) return no items.
  3. The season and series articles. All five season articles use {{Infobox
     television season}}, and not one of them has a runtime parameter. The
     FLCL article's six {{Infobox animanga/Video}} blocks carry exactly two
     runtimes between them: "23–31 minutes" on the original OVA, which is a
     RANGE across its six episodes and says nothing about which episode is
     which, and "135 minutes / 136 minutes" on the two compilation films,
     which are not rows here. The four later series carry no runtime at all.
  4. The episode tables' own RunTime fields. Not one of the 24 {{Episode
     list}} blocks has one.

So the only duration in the source that touches an episode is a range covering
a quarter of the list. It is all 24 rows or none (CLU-131), because a row with
no `w` on a weighted list silently counts as one full hour — 24 half-hours
would read as 24 hours. It is none, main() asserts none, and the notes name
every source that was checked and came up empty.

EXCLUDED, WITH REASONS. The two compilation films: Toho gave Progressive and
Alternative theatrical screenings in Japan in September 2018, and the list
article files them separately from the episodes under a heading that says
"In September 2018, [[Toho]] theatrically released the ''FLCL Progressive''
and ''FLCL Alternative'' sequel seasons as compilation films. They are
exclusive to Japan." — asserted here. They are re-cuts of episodes that are
already rows, so listing them would count the same twelve episodes twice; the
demon-slayer list refuses its two compilation films for the identical reason.
Everything else in the franchise is another medium: Hajime Ueda's two-volume
manga, Yōji Enokido's three-volume novel series, and the Pillows soundtracks.
The 2003 Adult Swim broadcast of the original is those same six episodes with
an English dub, not more of them.

CROSS-LIST SYNC: THERE IS NONE, AND IT IS CONFIRMED RATHER THAN ASSUMED.
build.py's gate is `syncable = "film" in kind or "game" in kind`; this list's
kind is "anime", so no row ever reaches the pairing code. main() restates that
gate literally so a future kind change trips it, and also asserts no row
carries an explicit `y`, no `n` is a bare year, and no note contains one —
build.py reads a single year out of a note when `n` is not a year, and an
episode called "Shake It Off" or "Full Swing" pairing with a same-titled film
is exactly the accident that would cause. Airdates therefore stay out of the
row notes entirely and live in the section intros.

ONE EPISODE IS DATED TWICE, DELIBERATELY. FLCL Alternative's first episode
went out unannounced at midnight ET on April 1, 2018 in Japanese with English
subtitles, as part of Adult Swim's April Fools' stunt, more than five months
before the season's proper first run on September 8. The episode table carries
both dates and the season infobox carries a footnote saying the September date
"reflects the proper first run broadcast of the series". This list follows the
infobox for the season's span and names the stunt in the row note, and main()
asserts both dates and the footnote are still there.

Everything is machine-read from the cached Wikipedia wikitext in
scratch/agent-flcl/core. Nothing is typed in from memory.
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop, wiki  # noqa: E402

SLUG = "flcl"

# The wikitext cache. Nothing here is required — gwlib re-fetches and
# repopulates whichever of these exists — but a warmed cache keeps this
# generator offline and off Wikipedia's rate limiter.
CACHE = next((d for d in (prop.ROOT / "scratch" / "agent-flcl" / "core",
                          prop.ROOT / "scratch" / SLUG)
              if d.exists()), prop.ROOT / "scratch" / "agent-flcl" / "core")

LIST_PAGE = "List of FLCL episodes"
SERIES_PAGE = "FLCL"

# The five series in release order: (season number, article, row title, id
# stem, the {{Infobox animanga/Video}} title on the FLCL article). Season 1's
# infobox block is the OVA one and carries no `title` field, hence the None.
SERIES = [
    (1, "FLCL (season 1)", "FLCL", "s1", None),
    (2, "FLCL Progressive", "FLCL Progressive", "s2", "FLCL Progressive"),
    (3, "FLCL Alternative", "FLCL Alternative", "s3", "FLCL Alternative"),
    (4, "FLCL: Grunge", "FLCL: Grunge", "s4", "FLCL: Grunge"),
    (5, "FLCL: Shoegaze", "FLCL: Shoegaze", "s5", "FLCL: Shoegaze"),
]
SEASONS = [n for n, _p, _t, _i, _b in SERIES]

# Asserted three ways each, never assumed — see the docstring.
PER_SEASON = {1: 6, 2: 6, 3: 6, 4: 3, 5: 3}
TOTAL_EPISODES = 24

# The one running time in the whole source that touches an episode, and the
# reason it cannot weight anything: it is a range across season 1's six.
OVA_RUNTIME = "23–31 minutes"

# FLCL Alternative's first episode aired twice. The table's {{Start date}} is
# the April Fools' stunt; the season's proper first run is the infobox's.
ALT_APRIL_FOOLS = (2018, 4, 1)

ACCENT = "#B30427"       # the red the source itself assigns the original
ACCENT_DARK = "#F2718C"  # ...against Haruko's pink, for dark mode

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]

# Rows that get a note. Nothing here says what happens in an episode — only
# what the episode IS, which is the copy rule. Keyed (season, in-season
# number). Progressive's and Alternative's per-episode animation studios are
# read from the source and appended in main().
ROW_NOTES = {
    (1, 1): "series premiere",
    (1, 6): "the original's last episode",
}


def text(page):
    t = wiki.wikitext(page, cache_dir=CACHE)
    assert t, "no wikitext for %r" % page
    return t


def strip_refs(t):
    """Prose with the footnotes gone, for the sentences main() reads as fact."""
    t = re.sub(r"<ref[^>]*/>", "", t)
    return re.sub(r"<ref.*?</ref>", "", t, flags=re.S)


def flat(t):
    """Footnote-free prose on one line, for sentence matching."""
    return re.sub(r"\s+", " ", strip_refs(t))


def date_in(field, kind="Start"):
    """The first {{Start date}} / {{End date}} in a chunk, as (y, m, d)."""
    m = re.search(r"\{\{%s date\s*\|\s*(\d{4})\s*\|\s*(\d{1,2})\s*\|"
                  r"\s*(\d{1,2})" % kind, field or "", re.I)
    assert m, "no %s date in %r" % (kind.lower(), (field or "")[:80])
    return tuple(int(g) for g in m.groups())


def plain_date(s):
    """`August 5, 2003` -> (2003, 8, 5)."""
    m = re.search(r"(%s)\s+(\d{1,2}),\s*(\d{4})" % "|".join(MONTHS), s or "")
    assert m, "no plain date in %r" % (s or "")[:60]
    return (int(m.group(3)), MONTHS.index(m.group(1)) + 1, int(m.group(2)))


def fmt_date(d):
    return "%s %d, %d" % (MONTHS[d[1] - 1], d[2], d[0])


def year_span(years):
    a, b = min(years), max(years)
    return str(a) if a == b else "%d–%d" % (a, b)


def balanced(text_, opening):
    """Every template body starting with `opening`, brace-balanced.

    A lazy match to the next `\\n}}` is not good enough for these infoboxes:
    they nest {{ubl}} and {{English anime network}}, whose closing braces sit
    on their own lines, so a lazy match stops inside the box and every field
    after it reads as empty. Counting braces is the only way to get the whole
    block. Lifted from make_the-big-o.py, which learned it the hard way."""
    out = []
    for m in re.finditer(re.escape(opening), text_):
        i, depth = m.start(), 0
        while i < len(text_):
            if text_.startswith("{{", i):
                depth += 1
                i += 2
            elif text_.startswith("}}", i):
                depth -= 1
                i += 2
                if depth == 0:
                    break
            else:
                i += 1
        assert depth == 0, "unbalanced %s block" % opening
        out.append(text_[m.start() + len(opening):i - 2])
    return out


def boxfield(body, name):
    """One field out of a brace-balanced infobox body.

    The whitespace after the `=` is `[ \\t]*`, not `\\s*`, for the reason
    gwlib.wiki.infobox uses the same: a greedy `\\s*` eats the newline of an
    EMPTY field, the lookahead then cannot fire on it, and the field reads as
    whatever is on the next line. An empty runtime that reported the episode
    count would be exactly the wrong thing to get wrong here."""
    m = re.search(r"^[ \t]*\|[ \t]*%s[ \t]*=[ \t]*(.*?)"
                  r"(?=\n\s*\|\s*[a-z_0-9]+\s*=|\Z)"
                  % name, body, re.M | re.S | re.I)
    return m.group(1).strip() if m else ""


def series_overview(list_text):
    """{season: (episodes, start, end, title)} from the list article's table.

    The overview is the first of the three counts every season is checked
    against, and it is also where the five series' official titles and
    broadcast windows come from."""
    seg = re.search(r"\{\{Series overview(.*?)\n\}\}", list_text, re.S)
    assert seg, "no series overview on the list article"
    body = seg.group(1)
    counts = {int(m.group(1)): int(m.group(2)) for m in
              re.finditer(r"\|\s*episodes(\d+)\s*=\s*(\d+)", body)}
    assert counts == PER_SEASON, \
        "the series overview counts %s, this list expects %s — a season has " \
        "grown, shrunk or appeared" % (counts, PER_SEASON)
    assert sum(counts.values()) == TOTAL_EPISODES, \
        "the overview totals %d episodes, expected %d" \
        % (sum(counts.values()), TOTAL_EPISODES)
    # a mid-run show carries this stamp; this one does not, which is why the
    # counts above can be treated as final
    assert "{{Aired episodes" not in list_text, \
        "the list article has an aired-episodes stamp — a season may be " \
        "running and its count is not final"
    out = {}
    for n in SEASONS:
        start = date_in(re.search(r"\|\s*start%d\s*=\s*(.*)" % n,
                                  body).group(1))
        end = date_in(re.search(r"\|\s*end%d\s*=\s*(.*)" % n, body).group(1),
                      "End")
        title = wiki.clean(re.search(r"\|\s*infoA%d\s*=\s*(.*)" % n,
                                     body).group(1))
        assert start <= end, "season %d ends before it starts" % n
        out[n] = (counts[n], start, end, title)
    return out


def headings(list_text):
    """{season: (heading title, year span)} from the article's own headings.

    The year spans in these headings are what the section subs print, so a
    season quietly gaining a year fails the build rather than shipping a sub
    that disagrees with the source."""
    out = {}
    for m in re.finditer(r"^===\s*Season (\d+)(?::\s*(.*?))?\s*"
                         r"\((\d{4}(?:–\d{4})?)\)\s*===\s*$", list_text, re.M):
        out[int(m.group(1))] = (wiki.clean(m.group(2) or ""), m.group(3))
    assert sorted(out) == SEASONS, \
        "the list article's season headings cover %s, expected %s" \
        % (sorted(out), SEASONS)
    return out


def transclusions(list_text):
    """The list article must transclude the five season articles rather than
    inline them — everything parsed here comes from the season articles, and a
    season inlined into the list page would silently pick up whatever else
    that page holds (its two compilation-film rows, for a start)."""
    for _n, page, _t, _i, _b in SERIES:
        assert "{{:%s}}" % page in list_text, \
            "the list article no longer transcludes %r" % page
    inline = wiki.episodes(list_text)
    assert len(inline) == 2, \
        "the list article parses %d episode blocks of its own, expected the " \
        "2 compilation films" % len(inline)
    return [t for _o, _s, t, _y, _b in inline]


def compilation_films(list_text):
    """The two films this list refuses, and the sentence that refuses them."""
    m = re.search(r"In September 2018, Toho theatrically released the FLCL "
                  r"Progressive and FLCL Alternative sequel seasons as "
                  r"compilation films\. They are exclusive to Japan\.",
                  flat(wiki.clean(list_text)))
    assert m, "the list article no longer files the two theatrical releases " \
              "as compilations of the seasons — if they now hold original " \
              "footage they belong on this list"
    return True


def rows_from(season_text, n, label):
    """[(overall, in_season, title, (y,m,d), block)] for one series."""
    raw = wiki.episodes(season_text)
    assert raw, "%s parsed empty" % label
    rows = []
    for o, s, title, _y, block in raw:
        assert o and s and title, \
            "%s row incomplete: %r" % (label, (o, s, title))
        assert not re.search(r"\|\s*RunTime\s*=\s*\S", block, re.I), \
            "%s episode %d now documents a running time — revisit weights, " \
            "because the only reason this list is unweighted is that no " \
            "episode had one" % (label, s)
        rawtitle = re.search(r"\|\s*Title\s*=\s*(.*)", block)
        assert rawtitle and "[[" not in rawtitle.group(1), \
            "%s episode %d's title is now a wikilink — an episode article " \
            "exists and may document a running time" % (label, s)
        rows.append((o, s, title, date_in(block), block))
    assert [s for _o, s, _t, _d, _b in rows] == list(range(1, len(rows) + 1)), \
        "%s in-season numbering is not 1..%d" % (label, len(rows))
    dates = [d for _o, _s, _t, d, _b in rows]
    assert dates == sorted(dates), "%s airdates are not in order" % label
    assert len(rows) == PER_SEASON[n], \
        "%s parsed %d episodes, expected %d" % (label, len(rows), PER_SEASON[n])
    return rows


def read_series():
    """{season: (rows, infobox reader)}, one article per series."""
    out = {}
    for n, page, _t, _i, _b in SERIES:
        t = text(page)
        rows = rows_from(t, n, page)
        ib = wiki.infobox(t, kind="television season")
        assert ib, "no season infobox on %r" % page
        assert not ib("runtime").strip(), \
            "%r now documents a runtime — revisit weights" % page
        assert ib("num_episodes").strip() == str(PER_SEASON[n]), \
            "%r's infobox says %r episodes, expected %d" \
            % (page, ib("num_episodes"), PER_SEASON[n])
        network = wiki.clean(ib("network")).split("(")[0].strip()
        assert network == "Adult Swim", \
            "%r's network is now %r" % (page, network)
        out[n] = (rows, ib)
    return out


def season_chain(seasons):
    """The five season infoboxes must link into one chain, and the chain must
    end at Shoegaze.

    This is how the list knows it is complete without anyone asserting a
    negative: every article but the last names a next_season, every article
    but the first names a prev_season, and each link points at the article
    this generator reads next. A sixth series appearing gives Shoegaze a
    next_season and fails the build here."""
    pages = [p for _n, p, _t, _i, _b in SERIES]
    for i, (n, page, _t, _i2, _b) in enumerate(SERIES):
        ib = seasons[n][1]
        nxt, prev = ib("next_season"), ib("prev_season")
        if i + 1 < len(SERIES):
            assert pages[i + 1] in nxt, \
                "%r's next_season is %r, expected a link to %r" \
                % (page, nxt, pages[i + 1])
        else:
            assert not nxt.strip(), \
                "%r now names a next season (%r) — a sixth FLCL series " \
                "exists and this list is short" % (page, nxt)
        if i:
            assert pages[i - 1] in prev, \
                "%r's prev_season is %r, expected a link to %r" \
                % (page, prev, pages[i - 1])
        else:
            assert not prev.strip(), "%r now names a previous season" % page


def video_boxes(series_text):
    """The FLCL article's {{Infobox animanga/Video}} blocks, by title.

    Six of them: the OVA, Progressive, Alternative, the two-film series, and
    Grunge and Shoegaze. A seventh would mean another installment exists and
    this list is short, so the count is asserted rather than assumed."""
    blocks = balanced(series_text, "{{Infobox animanga/Video")
    assert len(blocks) == len(SERIES) + 1, \
        "the FLCL article carries %d animanga/Video infoboxes, expected %d " \
        "(five series plus the compilation-film pair) — a new one means " \
        "another installment exists" % (len(blocks), len(SERIES) + 1)
    by = {}
    for b in blocks:
        by[wiki.clean(boxfield(b, "title")) or None] = b
    for _n, _p, _t, _i, boxtitle in SERIES:
        assert boxtitle in by, \
            "the FLCL article has no infobox titled %r" % boxtitle
    return by


def other_media(series_text):
    """The manga and the novels, read rather than remembered.

    The exclusions note names both by length and by author, so both come from
    the FLCL article's two {{Infobox animanga/Print}} blocks."""
    blocks = balanced(series_text, "{{Infobox animanga/Print")
    assert len(blocks) == 2, \
        "the FLCL article carries %d print infoboxes, expected the manga and " \
        "the novel series" % len(blocks)
    got = [(boxfield(b, "type"),
            wiki.clean(boxfield(b, "illustrator") or boxfield(b, "author")),
            boxfield(b, "volumes")) for b in blocks]
    assert got[0][0] == "manga" and got[0][1].startswith("Hajime Ueda") \
        and got[0][2] == "2", "the manga is now %r" % (got[0],)
    assert got[1][0] == "novel series" and got[1][2] == "3", \
        "the novel series is now %r" % (got[1],)
    return got


def runtime_hunt(series_text, boxes, seasons):
    """Sources 3 and 4 of the weights hunt, re-run from the cached wikitext.

    Sources 1 (per-episode articles) and 2 (per-episode Wikidata items) are
    network probes and live in scratch/agent-flcl/; the wikilink assert in
    rows_from covers the offline half of source 1, and rows_from covers 4."""
    runtimes = {k: boxfield(b, "runtime").strip()
                for k, b in boxes.items() if boxfield(b, "runtime").strip()}
    # exactly two boxes carry a runtime: the OVA (keyed None, it has no title)
    # and the film-series pair
    assert len(runtimes) == 2, \
        "%d animanga/Video infoboxes now carry a runtime, expected 2 (the " \
        "OVA's range and the two compilation films'): %s" \
        % (len(runtimes), sorted(str(k) for k in runtimes))
    assert None in runtimes, "the OVA infobox no longer carries a runtime"
    assert runtimes[None] == OVA_RUNTIME, \
        "the OVA's runtime is now %r, not the %r range this list reports as " \
        "the only episode duration in the source" % (runtimes[None], OVA_RUNTIME)
    for _n, _p, _t, _i, boxtitle in SERIES:
        if boxtitle is None:
            continue
        assert boxtitle not in runtimes, \
            "%s now documents a running time — revisit weights" % boxtitle
    # ...and no season article's episode table or infobox has one, which
    # read_series and rows_from asserted; restated here so the finding reads
    # in one place
    for n in SEASONS:
        assert not seasons[n][1]("runtime").strip(), "season %d runtime" % n
    return runtimes


def production_sentences(series_text, seasons_text, list_text):
    """The sentences the section subs and the notes rest on, read as data.

    Asserted so a rewrite upstream fails the build instead of leaving this
    list stating something the source no longer supports."""
    s = flat(series_text)

    ova = re.search(r"The original ''FLCL'' series was released as an "
                    r"\[\[original video animation\]\] \(OVA\) series", s)
    assert ova, "the FLCL article no longer calls the original an OVA — the " \
                "first section's sub says it was released direct to video"

    rights = re.search(r"On August 31, 2015, \[\[Anime News Network\]\] "
                       r"reported that Production I\.G may have been planning "
                       r"a continuation or remake of the OVA series after "
                       r"announcing their acquisition of the rights to "
                       r"''FLCL'' from production studio Gainax\.", s)
    assert rights, \
        "the FLCL article no longer records Production I.G acquiring the " \
        "rights from Gainax — the note about the later series being a " \
        "different production quotes it"

    order = re.search(r"On March 24, 2016, via \[\[Toonami\]\]'s official "
                      r"Facebook and Tumblr pages, it was announced that "
                      r"\[\[Cartoon Network\]\]'s \[\[Adult Swim\]\] will "
                      r"produce (\d+) new episodes of ''FLCL'' in cooperation "
                      r"with Production I\.G\.", s)
    assert order, "the FLCL article no longer records the 2016 order"
    assert int(order.group(1)) == PER_SEASON[2] + PER_SEASON[3], \
        "the 2016 order was for %s episodes, but Progressive and Alternative " \
        "hold %d" % (order.group(1), PER_SEASON[2] + PER_SEASON[3])

    # the other half of the framing: the original's people did not all leave
    kept = re.search(r"featured the return of original character designer "
                     r"Yoshiyuki Sadamato \(as his respective role\) and "
                     r"original series creator Kazuya Tsurumaki, who "
                     r"supervised the project", s)
    assert kept, \
        "the FLCL article no longer says Tsurumaki supervised Progressive — " \
        "the notes cite it so the production framing stays even"

    tsurumaki = re.search(r"is a Japanese \[\[anime\]\] series created and "
                          r"directed by \[\[Kazuya Tsurumaki\]\]", s)
    assert tsurumaki, "the FLCL article no longer credits Tsurumaki"

    made = {}
    for n in (2, 3):
        m = re.search(r"is produced by \[\[Production I\.G\]\], \[\[Toho\]\], "
                      r"and \[\[Adult Swim\]\]'s production arm "
                      r"\[\[Williams Street\]\]", flat(seasons_text[n]))
        assert m, "season %d's article no longer names Production I.G, Toho " \
                  "and Williams Street as its producers" % n
        made[n] = "Production I.G, Toho and Williams Street"

    for n, animator in ((4, r"MontBlanc Pictures"),
                        (5, r"\[\[NUT \(studio\)\|NUT\]\]")):
        m = re.search(r"is produced by \[\[Production I\.G\]\] and \[\[Adult "
                      r"Swim\]\]'s production arm \[\[Williams Street\]\]\. "
                      r"''(?:FLCL: )?\w+'' was animated by %s" % animator,
                      flat(seasons_text[n]))
        assert m, "season %d's article no longer names Production I.G, " \
                  "Williams Street and its animation studio" % n
        made[n] = ("%s for Production I.G and Williams Street"
                   % ("MontBlanc Pictures" if n == 4 else "NUT"))

    # the 2022 order, and the two placement facts the last two intros state
    order22 = re.search(r"Two additional seasons were ordered by Adult Swim "
                        r"in March 2022, which were announced on Toonami's "
                        r"25th anniversary, titled '''''FLCL: Grunge''''' and "
                        r"'''''FLCL: Shoegaze'''''\.", flat(list_text))
    assert order22, \
        "the episode-list article no longer records the March 2022 order of " \
        "Grunge and Shoegaze — both of the last two intros state it"
    prequel = re.search(r"''Grunge'' is a prequel to the original ''FLCL'' "
                        r"series from 2000\.", flat(seasons_text[4]))  # Grunge
    assert prequel, \
        "the Grunge article no longer calls itself a prequel to the original"
    after = re.search(r"''Shoegaze'' takes place 10 years after the events of "
                      r"''\[\[FLCL Alternative\]\]''", flat(seasons_text[5]))
    assert after, \
        "the Shoegaze article no longer places itself ten years after " \
        "Alternative"

    # season 1's studios come from the OVA infobox, not from prose
    return made


def april_fools(seasons, seasons_text):
    """FLCL Alternative's first episode is dated twice on purpose.

    Returns nothing; asserts that the table still carries both dates and that
    the season infobox still explains which one the season's span uses."""
    rows, ib = seasons[3]
    first = rows[0]
    assert first[3] == ALT_APRIL_FOOLS, \
        "Alternative's first episode is now dated %s in the table, not the " \
        "April Fools' airing %s" % (first[3], ALT_APRIL_FOOLS)
    assert re.search(r"<hr\s*/?>September 8, 2018 <small>\(English\)</small>",
                     first[4]), \
        "Alternative's first episode no longer carries its September " \
        "first-run date alongside the April Fools' one"
    note = re.search(r"The first episode of ''FLCL Alternative'' premiered "
                     r"unannounced in Japanese audio with English subtitles "
                     r"on April 1, 2018 at midnight ET as part of Adult "
                     r"Swim's .*?April Fools' stunt.*?\. The date reflects "
                     r"the proper first run broadcast of the series\.",
                     flat(seasons_text[3]))
    assert note, \
        "Alternative's infobox no longer footnotes the April Fools' airing — " \
        "the row note and the season's dates both depend on that footnote"
    assert date_in(ib("first_aired")) == (2018, 9, 8), \
        "Alternative's infobox first_aired is %r, not the September first " \
        "run" % ib("first_aired")


def english_dub_window(seasons):
    """Season 1's English broadcast, from the table's own AltDate column.

    The list article's prose says the Adult Swim run started August 4, 2003;
    the table's first AltDate is August 5. Rather than pick a winner between
    two defensible readings of a midnight slot, the intro says "six nights in
    August 2003" and this asserts exactly that much: every AltDate is in
    August 2003, in order."""
    rows, _ib = seasons[1]
    dates = [plain_date(re.search(r"\|\s*AltDate\s*=\s*(.*)",
                                  b).group(1)) for _o, _s, _t, _d, b in rows]
    assert dates == sorted(dates), "season 1's English airdates are out of order"
    assert all(d[0] == 2003 and d[1] == 8 for d in dates), \
        "season 1's English broadcast is no longer six nights in August " \
        "2003: %s" % [fmt_date(d) for d in dates]
    return dates


def check_not_syncable(p):
    """build.py's own gate, restated. An anime-kind list never reaches the
    pairing code; if that ever changes, this is where it fails loudly."""
    kind = p.get("kind") or ""
    assert "film" not in kind and "game" not in kind, \
        "kind %r is syncable — every row would try to pair by title+year" % kind
    for s in p["sections"]:
        for x in s["items"]:
            assert "y" not in x, "%s carries an explicit year" % x["id"]
            assert not re.fullmatch(r"(18|19|20)\d{2}", str(x.get("n", ""))), \
                "%s numbers itself with a bare year" % x["id"]
            leak = re.findall(r"\b(?:18|19|20)\d{2}\b", x.get("note") or "")
            assert not leak, \
                "%s leaks the year %s into its note — build.py reads a single " \
                "year out of a note when `n` is not one, which would pair " \
                "this episode with a same-titled film" % (x["id"], leak)


def check_accent():
    """The pair, and each half of it, must be unused by every other list."""
    for f in sorted((prop.ROOT / "properties").glob("*.json")):
        if f.stem in (SLUG, "index", "search"):
            continue
        other = json.loads(f.read_text(encoding="utf-8"))
        if not isinstance(other, dict):
            continue
        pair = (other.get("accent"), other.get("accentDark"))
        assert pair != (ACCENT, ACCENT_DARK), \
            "accent pair already belongs to %s" % f.stem
        for hexv in (ACCENT, ACCENT_DARK):
            assert hexv not in pair, "%s already uses %s" % (f.stem, hexv)


def main():
    list_text = text(LIST_PAGE)
    series_text = text(SERIES_PAGE)
    seasons_text = {n: text(page) for n, page, _t, _i, _b in SERIES}

    overview = series_overview(list_text)
    heads = headings(list_text)
    films = transclusions(list_text)
    compilation_films(list_text)
    seasons = read_series()
    season_chain(seasons)
    boxes = video_boxes(series_text)
    made = production_sentences(series_text, seasons_text, list_text)
    april_fools(seasons, seasons_text)
    dub = english_dub_window(seasons)
    runtimes = runtime_hunt(series_text, boxes, seasons)
    other_media(series_text)
    check_accent()

    assert films == ["FLCL Alternative: The Movie", "FLCL Progressive: The Movie"], \
        "the list article's compilation-film table now holds %r" % films

    # 1. the third count: the FLCL article's own infobox for each series
    for n, _page, _t, _i, boxtitle in SERIES:
        b = boxes[boxtitle]
        assert boxfield(b, "episodes").strip() == str(PER_SEASON[n]), \
            "the FLCL article's %s infobox says %r episodes, expected %d" \
            % (boxtitle or "OVA", boxfield(b, "episodes"), PER_SEASON[n])
        assert len(seasons[n][0]) == overview[n][0] == PER_SEASON[n], \
            "season %d: parsed %d, overview %d, expected %d" \
            % (n, len(seasons[n][0]), overview[n][0], PER_SEASON[n])

    # 2. overall numbering runs 1..24 unbroken across the five series
    numbered = [o for n in SEASONS for o, _s, _t, _d, _b in seasons[n][0]]
    assert numbered == list(range(1, TOTAL_EPISODES + 1)), \
        "overall episode numbering is not contiguous 1..%d: %s" \
        % (TOTAL_EPISODES, numbered)

    # 3. season 1's studios, from the OVA infobox rather than from prose
    # {{ubl|Gainax|Production I.G}} — clean() drops the template head and
    # leaves the members pipe-separated, so both separators are split on
    ova_studio = [x.strip() for x in
                  re.split(r"[|,]", wiki.clean(boxfield(boxes[None], "studio")))
                  if x.strip()]
    assert ova_studio == ["Gainax", "Production I.G"], \
        "the OVA infobox now credits %r" % ova_studio
    made[1] = " and ".join(ova_studio)

    # 4. the two 2018 seasons farmed their episodes out; the row notes say to
    # whom, and every one of those twelve blocks must carry the field
    animators = {}
    for n in (2, 3):
        for _o, s, _t, _d, block in seasons[n][0]:
            a = wiki.clean(re.search(r"\|\s*Aux1\s*=\s*(.*)", block).group(1))
            assert a, "season %d episode %d has no animation studio" % (n, s)
            animators[(n, s)] = a
    assert len(set(animators.values())) > 1, \
        "Progressive and Alternative no longer name more than one animation " \
        "studio between them — the row notes exist to show that they did"

    where = {1: "released direct to video in Japan"}
    for n in (2, 3, 4, 5):
        where[n] = "Adult Swim (Toonami)"

    studios = {n: sorted({animators[(m, s)] for (m, s) in animators if m == n})
               for n in (2, 3)}
    intros = {
        1: "Six episodes released straight to video in Japan, %s to %s, "
           "created and directed by Kazuya Tsurumaki for a production "
           "committee the source names as Gainax and Production I.G. Adult "
           "Swim ran the English dub over six nights in August 2003."
           % (fmt_date(overview[1][1]), fmt_date(overview[1][2])),
        2: "Eighteen years later, and made by different people: Anime News "
           "Network reported in 2015 that Production I.G had acquired the "
           "rights from Gainax, and in March 2016 Adult Swim announced twelve "
           "new episodes in cooperation with Production I.G. Tsurumaki "
           "supervised and the original character designer returned. It ran "
           "on Adult Swim's Toonami block, %s to %s, with the six episodes "
           "split between %d animation studios — each row names its own."
           % (fmt_date(overview[2][1]), fmt_date(overview[2][2]),
              len(studios[2])),
        3: "The other half of that 2016 order, two months after Progressive, "
           "%s to %s, with the same producers and the six episodes again "
           "split between %d studios. Its first episode had already gone out "
           "unannounced on April Fools' Day, in Japanese with English "
           "subtitles, at midnight on Toonami."
           % (fmt_date(overview[3][1]), fmt_date(overview[3][2]),
              len(studios[3])),
        4: "Adult Swim ordered two more seasons in March 2022, announced on "
           "Toonami's 25th anniversary. Grunge is three episodes rather than "
           "six, animated by MontBlanc Pictures with Hitoshi Takekiyo "
           "directing, %s to %s. The source calls it a prequel to the "
           "original."
           % (fmt_date(overview[4][1]), fmt_date(overview[4][2])),
        5: "The other half of the 2022 order, three episodes again, animated "
           "by NUT with Yutaka Uemura directing, %s to %s. The source places "
           "it ten years after Alternative, and it is the newest of the five "
           "— its article is the only one of the five that names no season "
           "after it."
           % (fmt_date(overview[5][1]), fmt_date(overview[5][2])),
    }

    sections = []
    for n, _page, title, sid, _b in SERIES:
        rows, _ib = seasons[n]
        span = year_span([d[0] for _o, _s, _t, d, _b2 in rows])
        head_span = heads[n][1]
        # Alternative's parsed dates open on the April Fools' airing, which is
        # the same year as its proper run; every other season matches outright
        assert span == head_span or (n == 3 and head_span == "2018"), \
            "season %d spans %s, the list article's heading says %s" \
            % (n, span, head_span)
        items = []
        for _o, s, t, _d, _b2 in rows:
            note = prop.join_bits(
                ROW_NOTES.get((n, s)),
                "animated by %s" % animators[(n, s)] if (n, s) in animators
                else None,
                "first aired unannounced on April Fools' Day, in Japanese "
                "with English subtitles" if (n, s) == (3, 1) else None)
            row = {"id": "flcl-%se%d" % (sid, s), "t": t, "n": str(s)}
            if note:
                row["note"] = note
            items.append(row)
        sections.append({
            "id": sid,
            "title": title,
            "sub": prop.join_bits(head_span, "%d episodes" % len(rows),
                                  made[n], where[n]),
            "intro": intros[n],
            "items": items,
        })
    sections[0]["open"] = True

    total = sum(len(s["items"]) for s in sections)
    assert total == TOTAL_EPISODES, "%d rows, expected %d" % (total, TOTAL_EPISODES)
    assert sum(1 for s in sections for x in s["items"] if "w" in x) == 0, \
        "a weight crept in — this list is unweighted end to end"

    p = {
        "slug": SLUG,
        "title": "FLCL",
        "subtitle": "all five series, in release order",
        "kind": "anime",
        "popularity": 62,
        "year": "2000–2023",
        "blurb": "Gainax's six-episode OVA and the four runs Production I.G "
                 "and Adult Swim made after it — 24 episodes, one list.",
        "unit": {"one": "episode", "many": "episodes"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": ACCENT,
        "accentDark": ACCENT_DARK,
        "tiers": False,
        "notes": [
            ["Five series, one list.",
             "The source files them as seasons 1 to 5 of one show and numbers "
             "the episodes 1 to 24 straight through, but each was made as its "
             "own production, so the sections here are the five series in "
             "release order and each row carries its number inside its own "
             "series. The overall numbering is still checked for gaps before "
             "this builds."],
            ["The four later series are a different production, and the "
             "source says so.",
             "The original is an original video animation: six episodes "
             "released straight to video in Japan between April 2000 and "
             "March 2001, created and directed by Kazuya Tsurumaki for a "
             "committee the article names as Gainax and Production I.G. The "
             "rest were made after the rights moved. Anime News Network "
             "reported in August 2015 that Production I.G had acquired the "
             "rights to FLCL from Gainax, and in March 2016 Adult Swim "
             "announced it would produce twelve new episodes in cooperation "
             "with Production I.G; those became Progressive and Alternative, "
             "co-produced with Toho and Adult Swim's production arm Williams "
             "Street and broadcast on Toonami in 2018. Adult Swim ordered two "
             "more in March 2022 — Grunge, animated by MontBlanc Pictures, "
             "and Shoegaze, animated by NUT — and both ran in 2023. Different "
             "studios, a different decade, a different broadcaster. It is not "
             "a clean break either: the same source records that Tsurumaki "
             "supervised the 2018 pair and that the original character "
             "designer came back for them. All of that is here as a fact "
             "about how the things were made. Whether to go past the original "
             "is your call, and this list takes no view."],
            ["Not six each.",
             "The original, Progressive and Alternative are six episodes "
             "apiece; Grunge and Shoegaze are three apiece. Twenty-four "
             "between them, and every one of those five counts is checked "
             "three ways before this builds — the series overview on the "
             "episode-list article, the num_episodes field in each season "
             "article's own infobox, and the episodes field in the matching "
             "infobox on the FLCL article — with the overall numbering "
             "asserted contiguous 1 to 24 on top."],
            ["Nothing is weighted, and hours are not tracked on this list.",
             "Not for want of looking: four sources were checked and all four "
             "came up empty. (1) Per-episode articles: none exist. All 24 "
             "titles were probed bare and in both disambiguated forms; the "
             "pages that answer are redirects into the season articles, "
             "disambiguation pages, or unrelated subjects that share a title "
             "— a Taylor Swift single, a K-pop group, a mall in New Zealand. "
             "No Title field in any of the five episode tables is a wikilink. "
             "(2) Per-episode Wikidata: no episode items exist at all. The "
             "series item's five has-parts are the five season items and "
             "nothing else, none of the six carries a runtime, and label "
             "searches for the distinctive titles return nothing. (3) The "
             "season and series articles: not one of the five season "
             "infoboxes has a runtime parameter, and the FLCL article gives "
             "only \"23–31 minutes\" for the original — a range across its "
             "six episodes, which cannot say which episode is which — and the "
             "two compilation films' lengths, which are not rows here. (4) "
             "The episode tables' own RunTime fields: not one of the 24 "
             "blocks has one. It has to be every row or none, because a row "
             "with no weight silently counts as a full hour; weighting "
             "nothing keeps 24 half-hours from reading as 24 hours."],
            ["The two compilation films are not here.",
             "Toho gave Progressive and Alternative theatrical screenings in "
             "Japan in September 2018, as FLCL Progressive: The Movie and "
             "FLCL Alternative: The Movie. The episode-list article files "
             "them away from the episodes and says they are exclusive to "
             "Japan; they are re-cuts of twelve episodes that are already "
             "rows, so listing them would count the same twelve twice. "
             "Everything else in the franchise is another medium — Hajime "
             "Ueda's two-volume manga, the three-volume novel series, the "
             "Pillows soundtracks — and the 2003 Adult Swim broadcast is the "
             "original six with an English dub rather than more of them."],
            ["One episode is dated twice, on purpose.",
             "Alternative's first episode went out unannounced at midnight on "
             "April Fools' Day, in Japanese with English subtitles, five "
             "months before the season's proper first run in September. The "
             "episode table carries both dates and the season's infobox "
             "footnotes which one counts. This list follows the infobox for "
             "the season's span and names the stunt in that row's note."],
            "Titles, numbering and airdates machine-read from Wikipedia's "
            "five FLCL season articles; counts, spans and the compilation "
            "films cross-checked against \"List of FLCL episodes\" and the "
            "\"FLCL\" article's own infoboxes; the runtime hunt run against "
            "Wikidata items Q92572, Q111954103, Q111953383, Q111953468, "
            "Q122422436 and Q122790739 and the English Wikipedia article "
            "index.",
        ],
        "sections": sections,
    }

    check_not_syncable(p)
    out = prop.write(p)

    print("wrote %s — %d rows in %d sections, unweighted (0 of %d rows "
          "resolved a runtime)" % (out.name, total, len(sections),
                                   TOTAL_EPISODES))
    print("   the only duration in the source: %r on the original OVA, a "
          "range across its six" % runtimes[None])
    print("   English dub of the original: %s to %s"
          % (fmt_date(dub[0]), fmt_date(dub[-1])))
    for n, _page, title, _sid, _b in SERIES:
        rows, _ib = seasons[n]
        s = next(x for x in sections if x["title"] == title)
        print("   %-18s %2d rows  #%d–%d overall  %s..%s  %s"
              % (title, len(rows), rows[0][0], rows[-1][0],
                 fmt_date(overview[n][1]), fmt_date(overview[n][2]), s["sub"]))


if __name__ == "__main__":
    main()
