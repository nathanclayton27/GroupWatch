#!/usr/bin/env python3
"""Generate properties/demon-slayer.json — the television run and the films.

    python3 tools/make_demon-slayer.py

Ufotable's adaptation of Koyoharu Gotouge's manga, in the order the story goes:
season 1, the Mugen Train film, the Entertainment District half of season 2,
seasons 3 and 4, then the first Infinity Castle film. 59 rows.

MUGEN TRAIN EXISTS TWICE, AND THIS IS THE WHOLE JOB. It is a 2020 theatrical
film and it is also the first seven episodes of season 2, which the list
article describes as "a television series recompilation of the 'Mugen Train'
arc as featured in the film". Carrying both would count the same two hours
twice.

make_futurama.py is the house precedent for exactly this shape — four films
re-cut into sixteen episodes, and that list carries the films and refuses the
re-cut, because the film is the form the work was released in. Applying that
by reflex here would be wrong, and the source says why. Two independent
statements in the cached wikitext, both asserted in main():

  * the film article's "Television series version" section: the TV part "is an
    extended and recompiled version of the film that ran for a total of seven
    episodes. The first episode of the part is an entirely new episode that
    focuses on what Kyojuro did immediately before the events of the film,
    while the remaining six episodes are recompiled cuts of the film"; and
  * the season 2 article's lead: the part "is a seven-episode recompilation of
    the 'Mugen Train' arc as featured in the 2020 anime film. It contains new
    music and an all new anime original episode which takes place immediately
    before the main story."

So season 2A is a re-cut plus one episode of animation that exists nowhere
else. Futurama's answer — film once, refuse the re-cut — is right for the six,
and wrong for the seventh. This list therefore carries:

  * the film, once, at 119 minutes; and
  * "Flame Hashira Kyojuro Rengoku", season 2's first episode, as its own row,
    placed BEFORE the film because the source says it happens before it.

and refuses the six recompiled episodes. The arithmetic: 57 of the series' 63
episodes are listed. Taking all seven episodes as well as the film would be 64
entries and two hours of double-counting; taking the film alone, the futurama
reading, would be 58 and would silently drop a whole episode of animation that
exists nowhere but television. 59 is the only count that loses nothing and
repeats nothing.

Numbering follows the source rather than the sections, which is why the
Entertainment District rows run 8 to 18 instead of restarting at 1 — the gap
where 2 to 7 would be is the film.

THE TWO COMPILATION FILMS ARE OUT, FOR THE SAME REASON IN REVERSE. "To the
Swordsmith Village" (2023) and "To the Hashira Training" (2024) are theatrical
compilations built out of episodes that are already rows here — the last one
or two episodes of a season plus an advance screening of the next season's
first episode — and their own articles say so in the words "acts as a
compilation film to the anime television series, incorporating…", which
main() asserts. Here the episodes are the original form and the film is the
re-cut, so the episodes stay and the compilations go. The franchise article
files them under "Anime compilations", separately from its "Anime films"
list, and main() asserts that both lists still hold exactly the two titles
this generator expects.

INFINITY CASTLE: ONE FILM HAS ACTUALLY OPENED. The arc was announced in June
2024 as a trilogy. Part 1: Akaza Returns opened in Japan on July 18, 2025 and
is the only installment in the cached source with a release date — its article
carries exactly one {{Film date}}, which main() asserts, and asserts is in the
past. Parts 2 and 3 have no dated release and are not listed; they are named
in the notes so their absence is a statement rather than an oversight.

THE TELEVISION SERIES IS FINISHED. Four seasons, 63 episodes, April 6 2019 to
June 30 2024. The series infobox closes its second network block with an
{{End date}} and carries an editor's note saying only films are confirmed to
follow, and no fifth season exists because the Infinity Castle arc went to
cinemas instead. main() asserts the closed date matches the last episode
parsed, so a list that looks abandoned mid-story is instead a list that says
where the story went.

WEIGHTS. None, and the reason is stronger here than on any list built so far:
Wikipedia documents NO running time for this series. The television infobox has
no runtime field, not one of the four season infoboxes has one, and not one of
the 63 episode blocks carries a Runtime — all four facts asserted in main()
rather than assumed. What the source does give is a length for four episodes,
in prose: seasons 3 and 4 each opened with a one-hour episode and closed with
one of 70 and 60 minutes respectively. Those four sentences are read and
asserted here too, because they are worth telling a reader — but four
durations out of 57 cannot weight a list.

The two film articles do give runtimes (119 and 155 minutes), and that is
precisely the trap: weighting the films while the episodes have no verifiable
number would leave every episode row resolving `WEIGHT = x.w >= 0 ? x.w : 1`
to one hour apiece, so 57 half-hour episodes would read as 57 hours. It is all
rows or none. It is none, main() asserts none, and the notes say plainly that
hours are not tracked on this list. The film rows carry their runtimes as text
in the row note instead, where they inform without arithmetic.

SEASON DIVISIONS ARE THE SOURCE'S, AND THE SOURCE FLAGS THEM. The list
article's own hatnote says the season divisions "correspond to general
audience consensus" and that "the season sorting has never been made clear by
any official sources", while the arc titles are official. So the sections are
named for the arcs, which are official, and main() asserts that hatnote is
still there — if the divisions ever become official, the caveat in the notes
should go.

Everything is machine-read from the cached Wikipedia wikitext in
scratch/demon-slayer/ — the list article, the four season articles, the series
article, the franchise article and the four film articles. Nothing is typed in
from memory. Before anything is written: each season's parsed row count is
asserted against BOTH that season's episodesN in the list article's
{{Series overview}} (reading episodes2A and episodes2B separately, since a
naive episodes2 read gives 18 and hides the split) and num_episodes in the
season article's own infobox; each season's in-season numbering is asserted to
run 1..N; airdates are asserted non-decreasing and matched against each season
infobox's first_aired and last_aired; each section's year span is asserted
against the year span in the list article's own section heading; the overall
numbering is asserted contiguous 1..63; the total is cross-checked against the
series infobox's num_episodes and num_seasons; and the accent pair is asserted
unused by every other property on disk.
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop, wiki  # noqa: E402

SLUG = "demon-slayer"
CACHE = prop.ROOT / "scratch" / SLUG
LIST_PAGE = "List of Demon Slayer: Kimetsu no Yaiba episodes"
SERIES_PAGE = "Demon Slayer: Kimetsu no Yaiba (TV series)"
FRANCHISE_PAGE = "Demon Slayer: Kimetsu no Yaiba"
SEASONS = [1, 2, 3, 4]

TOTAL_EPISODES = 63   # every episode the series made, asserted three ways
LISTED = 59           # rows on this list: 57 episodes + 2 films

# The films this list carries, in release order, with the article each is read
# from. The two compilation films are deliberately absent — see COMPILATIONS.
FILM_PAGES = ["Demon Slayer: Kimetsu no Yaiba – The Movie: Mugen Train",
              "Demon Slayer: Kimetsu no Yaiba – The Movie: Infinity Castle"]
COMPILATIONS = ["Demon Slayer: Kimetsu no Yaiba – To the Swordsmith Village",
                "Demon Slayer: Kimetsu no Yaiba – To the Hashira Training"]

# Every film article titles itself with this in front; stripping it is what
# turns the official title into a row title, and it is asserted, not assumed.
FILM_PREFIX = "Demon Slayer: Kimetsu no Yaiba – The Movie: "

# Hard-coded rather than read from the clock so re-running this produces the
# same file. Any film whose release date is after this is unreleased and out.
TODAY = (2026, 8, 25)

ACCENT = "#1A3A2A"       # the black-green check of Tanjiro's haori
ACCENT_DARK = "#F2789F"  # ...against the pink of Nezuko's kimono

MONTHS = {m: i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"], 1)}
NUMBER_WORDS = {"six": 6, "seven": 7}

INTRO = {
    1: "The whole first season, adapting the manga from its first volume into "
       "the opening chapters of the seventh. The place to start.",
}


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
    names = {v: k for k, v in MONTHS.items()}
    return "%s %d, %d" % (names[d[1]], d[2], d[0])


def year_span(years):
    a, b = min(years), max(years)
    if a == b:
        return str(a)
    return "%d–%02d" % (a, b % 100) if a // 100 == b // 100 else "%d–%d" % (a, b)


def series_overview(list_text):
    """{season: episode count} plus season 2's two halves, from the article.

    Season 2 is stored as `episodes2 = 18` with `episodes2A = 7` and
    `episodes2B = 11` beside it. The whole-season pattern requires the number
    to be followed straight by `=`, so the halves cannot double-count into it;
    they are read separately and asserted to sum."""
    seg = re.search(r"\{\{Series overview(.*?)\n\}\}", list_text, re.S)
    assert seg, "no series overview"
    body = seg.group(1)
    counts = {int(m.group(1)): int(m.group(2)) for m in
              re.finditer(r"\|\s*episodes(\d+)\s*=\s*(\d+)", body)}
    assert sorted(counts) == SEASONS, \
        "series overview lists seasons %s, expected %s" % (sorted(counts),
                                                           SEASONS)
    halves = {m.group(1): int(m.group(2)) for m in
              re.finditer(r"\|\s*episodes2([AB])\s*=\s*(\d+)", body)}
    assert sorted(halves) == ["A", "B"], \
        "season 2 is no longer split into 2A and 2B: %r" % halves
    assert halves["A"] + halves["B"] == counts[2], \
        "season 2's halves (%d + %d) do not sum to %d" \
        % (halves["A"], halves["B"], counts[2])
    assert sum(counts.values()) == TOTAL_EPISODES, \
        "the overview counts %d episodes, expected %d" \
        % (sum(counts.values()), TOTAL_EPISODES)
    # a mid-run show carries this stamp; this one does not, which is why
    # completeness below comes from the infoboxes instead
    assert "{{Aired episodes" not in list_text, \
        "the list article has an aired-episodes stamp — the series may be " \
        "running again and season 4 can no longer be treated as the last"
    # the one claim season 1's intro makes about the manga, read from the lead
    m = re.search(r"The first season contains (\d+) episodes, adapting from "
                  r"the first volume to the first chapters of the seventh\.",
                  strip_refs(list_text))
    assert m and int(m.group(1)) == counts[1], \
        "the lead no longer says season 1 is %d episodes covering volumes " \
        "one to seven — season 1's intro says so and must be re-read" \
        % counts[1]
    return counts, halves


def headings(list_text):
    """{season: (arc title(s), year span)} from the article's own headings."""
    out = {}
    for m in re.finditer(r"^===\s*Season (\d+):\s*(.*?)\s*"
                         r"\((\d{4}(?:–\d{2,4})?)\)\s*===\s*$",
                         list_text, re.M):
        out[int(m.group(1))] = (wiki.clean(m.group(2)), m.group(3))
    assert sorted(out) == SEASONS, \
        "list article headings cover %s, expected %s" % (sorted(out), SEASONS)
    return out


def extended_episodes(list_text):
    """{season: sentence} for the two seasons whose openers and finales the
    source gives a length for — the only per-episode durations it documents,
    and the reason the weights note can be specific about what is missing.

    The footnotes sit mid-sentence here, so the prose is read with the refs
    stripped and its whitespace collapsed before matching."""
    out = {}
    list_text = re.sub(r"\s+", " ", strip_refs(list_text))
    a = re.search(r"It premiered on April 9, 2023, with a (one-hour) special, "
                  r"and ended on June 18 of that same year with a "
                  r"(\d+-minute) special\.", list_text)
    assert a, "the list article no longer describes season 3's long episodes"
    out[3] = ("Opens with a %s episode and closes with a %s one — the only "
              "two lengths the source gives for this season."
              % (a.group(1), a.group(2)))
    b = re.search(r"It premiered on May 12, 2024, with a (one-hour) episode\. "
                  r"The season ended with a (\d+-minute) episode, which aired "
                  r"on June 30 of the same year\.", list_text)
    assert b, "the list article no longer describes season 4's long episodes"
    out[4] = ("The last television season: a %s premiere, a %s finale, and "
              "the handover to the films. The story continues in cinemas."
              % (b.group(1), b.group(2)))
    return out


def season_caveat(list_text):
    """The hatnote saying the season divisions are consensus, not official."""
    m = re.search(r"The season divisions that comprise the following list "
                  r"correspond to general audience consensus\. While the "
                  r"story arc titles are official, the season sorting has "
                  r"never been made clear by any official sources\.",
                  list_text)
    assert m, "the list article no longer flags its season divisions as " \
              "unofficial — the caveat in the notes needs re-reading"
    return True


def rows_from(season_text, n, label):
    """[(overall, in_season, title, (y,m,d))] from a chunk of a season page."""
    raw = wiki.episodes(season_text)
    assert raw, "%s parsed empty" % label
    rows = []
    for o, s, t, _, block in raw:
        assert not re.search(r"\|\s*Runtime\s*=", block, re.I), \
            "%s has a per-episode runtime now — revisit weights" % label
        assert o and s and t, "%s row incomplete: %r" % (label, (o, s, t))
        rows.append((o, s, t, date_in(block)))
    dates = [d for _, _, _, d in rows]
    assert dates == sorted(dates), \
        "%s airdates are not in broadcast order" % label
    return rows


def read_seasons():
    """{season: (rows, meta)}, one article per season.

    The list page only transcludes the season articles, so nothing is ever
    parsed from there — a season inlined into the list page would silently
    pick up whatever else that page holds."""
    out = {}
    for n in SEASONS:
        t = text("Demon Slayer: Kimetsu no Yaiba season %d" % n)
        rows = rows_from(t, n, "season %d" % n)
        assert [s for _, s, _, _ in rows] == list(range(1, len(rows) + 1)), \
            "season %d numbering is not 1..%d" % (n, len(rows))

        ib = wiki.infobox(t, kind="television season")
        assert ib, "no season infobox on the season %d article" % n
        assert not ib("runtime").strip(), \
            "season %d now documents a runtime — revisit weights" % n
        network = wiki.clean(ib("network")).split(",")[0].strip()
        assert network in ("Tokyo MX", "Fuji Television"), \
            "season %d aired on %r, which is neither of the two networks " \
            "this list knows" % (n, network)
        meta = {"episodes": int(ib("num_episodes")),
                "first": date_in(ib("first_aired")),
                "last": date_in(ib("last_aired"), "End"),
                "network": network}
        assert meta["first"] == rows[0][3], \
            "season %d: infobox opens %s, first episode aired %s" \
            % (n, meta["first"], rows[0][3])
        assert meta["last"] == rows[-1][3], \
            "season %d: infobox closes %s, last episode aired %s" \
            % (n, meta["last"], rows[-1][3])
        out[n] = (rows, meta)
    return out


def split_season_two():
    """Season 2's episodes cut at the article's own Entertainment District
    part marker: ([Mugen Train rows], [Entertainment District rows], arc names).

    The two {{Episode table/part}} markers are how the season article itself
    divides the eighteen, so the split is the source's and not a guess at
    where seven ends."""
    t = text("Demon Slayer: Kimetsu no Yaiba season 2")
    parts = re.findall(r"\{\{Episode table/part\|subtitle=''([^{}']+)", t)
    assert parts == ["Mugen Train Arc", "Entertainment District Arc"], \
        "season 2's part markers are %r, not the two arcs" % parts
    marker = "{{Episode table/part|subtitle=''Entertainment District Arc"
    halves = t.split(marker)
    assert len(halves) == 2, "the Entertainment District part marker moved"
    mta = rows_from(halves[0], 2, "season 2 Mugen Train Arc")
    eda = rows_from(halves[1], 2, "season 2 Entertainment District Arc")
    return mta, eda, parts


def mugen_train_evidence(film_text, season2_text):
    """The two sentences that decide what Mugen Train is, read as data.

    Returns (episodes in the TV part, episodes that are re-cut film). The
    difference between them is the original episode this list keeps."""
    a = re.search(r"is an extended and recompiled version of the film that "
                  r"ran for a total of (\w+) episodes\.\s*The first episode "
                  r"of the part is an entirely new episode.*?while the "
                  r"remaining (\w+) episodes are recompiled cuts of the film",
                  strip_refs(film_text), re.S)
    assert a, "the film article no longer separates the new episode from " \
              "the recompiled ones — the whole Mugen Train decision rests " \
              "on that sentence and must be re-read before this builds"
    total, recut = NUMBER_WORDS[a.group(1)], NUMBER_WORDS[a.group(2)]
    assert total - recut == 1, \
        "the film article now counts %d new episodes, not one" % (total - recut)

    b = re.search(r"is a (\w+)-episode recompilation of the \"Mugen Train\" "
                  r"arc as featured in the .{0,140}?2020 anime film.{0,40}?"
                  r"\. It contains new music and an all new anime original "
                  r"episode which takes place immediately before the main "
                  r"story", strip_refs(season2_text), re.S)
    assert b, "the season 2 article no longer calls its first part a " \
              "recompilation with one original episode"
    assert NUMBER_WORDS[b.group(1)] == total, \
        "the two articles disagree on the length of the TV recompilation"
    return total, recut


def read_film(page):
    """(display title, release date, runtime minutes) for one film article."""
    t = text(page)
    ib = wiki.infobox(t, kind="film")
    assert ib, "no film infobox on %s" % page

    name = wiki.clean(ib("name"))
    if not name:
        # Infinity Castle's infobox omits `name`; the article states the full
        # official title in a footnote instead, and that is what is used.
        m = re.search(r"Officially titled '''''(.*?)'''''", t)
        assert m, "%s gives no name and no official title" % page
        name = wiki.clean(m.group(1))
    assert name.startswith(FILM_PREFIX), \
        "%s is titled %r, which does not start with the film prefix" \
        % (page, name)
    title = name[len(FILM_PREFIX):].strip()
    assert title, "%s reduces to an empty title" % page

    dates = re.findall(r"\{\{Film date\|([^}]*)\}\}", ib("released"))
    assert len(dates) == 1, \
        "%s carries %d {{Film date}} entries — a second one would mean " \
        "another installment has a release date and this list is short" \
        % (page, len(dates))
    bits = dates[0].split("|")
    released = tuple(int(b) for b in bits[:3])
    assert released <= TODAY, \
        "%s is dated %s, which has not happened yet" % (page, released)

    rt = re.search(r"(\d+)\s*minutes", ib("runtime"))
    assert rt, "no runtime for %s" % page
    mins = int(rt.group(1))
    assert 90 <= mins <= 200, "%s runtime %d looks wrong" % (title, mins)
    return title, released, mins


def check_compilations():
    """The two films this list refuses must still describe themselves as
    compilations of episodes that are already rows here."""
    for page in COMPILATIONS:
        t = strip_refs(text(page))
        m = re.search(r"acts as a \[\[compilation film\]\] to the anime "
                      r"television series, incorporating", t)
        assert m, "%s no longer calls itself a compilation of the series — " \
                  "if it now holds original footage it belongs on the list" \
                  % page
        assert re.search(r"feature-length compilation", t), \
            "%s no longer calls itself a feature-length compilation" % page


def check_franchise_lists():
    """The franchise article files films and compilations separately; both
    lists must still hold exactly what this generator expects, so a newly
    released Infinity Castle installment cannot slip past unnoticed."""
    t = text(FRANCHISE_PAGE)

    def block(title):
        m = re.search(r"\{\{Infobox animanga/Other\s*\|\s*title\s*=\s*%s\s*"
                      r"\|\s*content\s*=(.*?)\n\}\}" % title, t, re.S)
        assert m, "no %r block on the franchise article" % title
        return re.findall(r"\*\s*''\[\[([^\]|]+)\]\]''", m.group(1))

    films = block("Anime films")
    assert films == FILM_PAGES, \
        "the franchise article lists films %s, this generator carries %s" \
        % (films, FILM_PAGES)
    comps = block("Anime compilations")
    assert comps == COMPILATIONS, \
        "the franchise article lists compilations %s, expected %s" \
        % (comps, COMPILATIONS)


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
    overview, halves = series_overview(list_text)
    heads = headings(list_text)
    long_eps = extended_episodes(list_text)
    season_caveat(list_text)
    seasons = read_seasons()
    mta, eda, arc_names = split_season_two()
    check_compilations()
    check_franchise_lists()
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

    # 2. and season 2 splits the way the overview's two halves say it does
    assert len(mta) == halves["A"], \
        "Mugen Train Arc parsed %d episodes, the overview says %d" \
        % (len(mta), halves["A"])
    assert len(eda) == halves["B"], \
        "Entertainment District Arc parsed %d episodes, the overview says %d" \
        % (len(eda), halves["B"])
    assert mta + eda == seasons[2][0], \
        "the two halves of season 2 do not reassemble into the season"

    # 3. the list article must still be transcluding the season articles
    for n in SEASONS:
        assert re.search(r"\{\{:Demon Slayer: Kimetsu no Yaiba season %d\}\}"
                         % n, list_text), \
            "list article no longer transcludes the season %d article" % n

    # 4. overall numbering must run 1..63 unbroken or a season is missing
    numbered = sorted(o for n in SEASONS for o, _, _, _ in seasons[n][0])
    assert numbered == list(range(1, TOTAL_EPISODES + 1)), \
        "overall episode numbering is not contiguous 1..%d" % TOTAL_EPISODES

    # 5. the series infobox counts the run independently of the list article,
    # documents no running time, and closes with a date
    ib = wiki.infobox(text(SERIES_PAGE), kind="television")
    assert ib, "no television infobox on the series article"
    assert ib("num_episodes").strip() == str(TOTAL_EPISODES), \
        "series infobox says %r episodes, parsed %d" \
        % (ib("num_episodes"), TOTAL_EPISODES)
    assert ib("num_seasons").strip() == str(len(SEASONS)), \
        "series infobox says %r seasons, parsed %d" \
        % (ib("num_seasons"), len(SEASONS))
    assert not ib("runtime").strip(), \
        "the series now documents a running time — revisit weights, because " \
        "the only reason this list is unweighted is that it did not"
    last_parsed = seasons[SEASONS[-1]][0][-1][3]
    assert date_in(ib("last_aired2"), "End") == last_parsed, \
        "series infobox closes %s, last episode parsed aired %s" \
        % (ib("last_aired2"), last_parsed)

    # 6. the Mugen Train decision, from the two articles that make it
    tv_part, recut = mugen_train_evidence(
        text(FILM_PAGES[0]), text("Demon Slayer: Kimetsu no Yaiba season 2"))
    assert tv_part == len(mta), \
        "the film article counts %d TV episodes, %d parsed" \
        % (tv_part, len(mta))
    original = [r for r in mta if r[1] == 1]
    assert len(original) == 1 and len(mta) - len(original) == recut, \
        "the one original episode and the %d re-cut ones do not account for " \
        "the whole part" % recut

    films = [read_film(p) for p in FILM_PAGES]
    assert [t for t, _, _ in films] == ["Mugen Train",
                                        "Infinity Castle – Part 1: Akaza Returns"], \
        "the film titles read from the source are %r" % [t for t, _, _ in films]
    assert films[0][1][0] == 2020 and films[1][1][0] == 2025, \
        "film release years are %r" % [d[0] for _, d, _ in films]
    # the trilogy is a trilogy, and only one of it has opened
    assert re.search(r"It is the first film of a trilogy announced in June "
                     r"2024", strip_refs(text(FILM_PAGES[1]))), \
        "the Infinity Castle article no longer calls itself the first of a " \
        "trilogy — check whether a second installment has opened"

    mt_title, mt_date, mt_mins = films[0]
    ic_title, ic_date, ic_mins = films[1]
    o_overall, o_num, o_title, o_date = original[0]
    assert o_overall == overview[1] + 1, \
        "the original Mugen Train episode is overall #%d, not the one " \
        "straight after season 1" % o_overall

    sections = []

    # --- Season 1 -----------------------------------------------------------
    s1_rows, s1_meta = seasons[1]
    s1_span = year_span([d[0] for _, _, _, d in s1_rows])
    assert s1_span == heads[1][1], \
        "season 1 spans %s, the heading says %s" % (s1_span, heads[1][1])
    sections.append({
        "id": "s1",
        "title": "Season 1: %s" % heads[1][0],
        "sub": prop.join_bits(s1_span, "%d episodes" % len(s1_rows),
                              s1_meta["network"]),
        "intro": INTRO[1],
        "items": [{"id": "ds-s1e%d" % s, "t": t, "n": str(s)}
                  for _, s, t, _ in s1_rows],
    })

    # --- Mugen Train: the film, and the episode the film does not contain ---
    sections.append({
        "id": "mugen-train",
        "title": arc_names[0],
        "sub": prop.join_bits(year_span([mt_date[0], o_date[0]]),
                              "one film and one original episode"),
        "intro": "The same story exists as a 2020 feature film and as the "
                 "first seven episodes of season 2, and the source is exact "
                 "about the difference: one of those episodes is new, and the "
                 "other six are the film re-cut. So the film is here once, "
                 "with the new episode ahead of it — it covers what Kyojuro "
                 "was doing just before the film starts. The six re-cut "
                 "episodes are not listed; watching the film is watching "
                 "them.",
        "items": [
            {"id": "ds-s2e%d" % o_num, "t": o_title, "n": str(o_num),
             "note": prop.join_bits(
                 "Season 2 episode %d" % o_num,
                 "an original episode, not part of the film",
                 "aired %s" % fmt_date(o_date))},
            {"id": "ds-film-%s" % prop.slug(mt_title), "t": mt_title,
             "n": str(mt_date[0]),
             "note": prop.join_bits(
                 "%d feature film" % mt_date[0],
                 "%d minutes" % mt_mins,
                 "re-cut as season 2 episodes %d–%d, which are not listed "
                 "separately" % (mta[1][1], mta[-1][1]))},
        ],
    })

    # --- Season 2's other half ---------------------------------------------
    s2_span = year_span([d[0] for _, _, _, d in mta + eda])
    assert s2_span == heads[2][1], \
        "season 2 spans %s, the heading says %s" % (s2_span, heads[2][1])
    assert heads[2][0] == "%s and %s" % tuple(arc_names), \
        "the season 2 heading names %r, the part markers name %r" \
        % (heads[2][0], arc_names)
    sections.append({
        "id": "s2",
        "title": "Season 2: %s" % arc_names[1],
        "sub": prop.join_bits(year_span([d[0] for _, _, _, d in eda]),
                              "%d episodes" % len(eda),
                              seasons[2][1]["network"]),
        "intro": "The second half of season 2, and the first stretch of the "
                 "series after Mugen Train that is only television. Numbered "
                 "8 to 18 because that is where the source puts it inside the "
                 "season; the gap before it is the film.",
        "items": [{"id": "ds-s2e%d" % s, "t": t, "n": str(s)}
                  for _, s, t, _ in eda],
    })

    # --- Seasons 3 and 4 ----------------------------------------------------
    for n in (3, 4):
        rows, meta = seasons[n]
        span = year_span([d[0] for _, _, _, d in rows])
        assert span == heads[n][1], \
            "season %d spans %s, the heading says %s" % (n, span, heads[n][1])
        sections.append({
            "id": "s%d" % n,
            "title": "Season %d: %s" % (n, heads[n][0]),
            "sub": prop.join_bits(span, "%d episodes" % len(rows),
                                  meta["network"]),
            "intro": long_eps[n],
            "items": [{"id": "ds-s%de%d" % (n, s), "t": t, "n": str(s)}
                      for _, s, t, _ in rows],
        })

    # --- Infinity Castle ----------------------------------------------------
    sections.append({
        "id": "infinity-castle",
        "title": "Infinity Castle",
        "sub": prop.join_bits(str(ic_date[0]), "one film",
                              "%d minutes" % ic_mins),
        "intro": "Where the story goes after season 4. The Infinity Castle "
                 "arc was adapted for cinemas as a trilogy rather than a "
                 "fifth season; one of the three has opened so far, and the "
                 "other two join this list when they do.",
        "items": [{
            "id": "ds-film-%s" % prop.slug(ic_title),
            "t": ic_title,
            "n": str(ic_date[0]),
            "note": prop.join_bits("%d feature film" % ic_date[0],
                                   "%d minutes" % ic_mins,
                                   "first of three",
                                   "released %s" % fmt_date(ic_date)),
        }],
    })

    sections[0]["open"] = True

    assert [s["id"] for s in sections] == \
        ["s1", "mugen-train", "s2", "s3", "s4", "infinity-castle"], \
        [s["id"] for s in sections]
    total = sum(len(s["items"]) for s in sections)
    assert total == LISTED, "%d rows, expected %d" % (total, LISTED)
    episodes_listed = total - len(FILM_PAGES)
    assert episodes_listed == TOTAL_EPISODES - recut, \
        "%d episodes listed, expected %d (%d made, %d re-cut into the film)" \
        % (episodes_listed, TOTAL_EPISODES - recut, TOTAL_EPISODES, recut)
    assert sum(1 for s in sections for x in s["items"] if "w" in x) == 0, \
        "a weight crept in — this list is unweighted end to end"

    p = {
        "slug": SLUG,
        "title": "Demon Slayer: Kimetsu no Yaiba",
        "subtitle": "every episode and the films, each story once",
        "kind": "tv & films",
        "popularity": 74,
        "year": "2019–",
        "blurb": "Ufotable's Taishō-era demon hunt, in story order — the four "
                 "television arcs and the theatrical films, with Mugen Train "
                 "counted once rather than twice.",
        "unit": {"one": "entry", "many": "entries"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": ACCENT,
        "accentDark": ACCENT_DARK,
        "tiers": False,
        "notes": [
            ["Mugen Train is here once — as the film, plus the one episode "
             "the film does not contain.",
             "The 2020 feature and the first seven episodes of season 2 are "
             "the same story, so listing both would count the same two hours "
             "twice. The source is precise about how they differ: the film's "
             "article says the television part is \"an extended and "
             "recompiled version of the film\", that its first episode is "
             "\"an entirely new episode\" showing what Kyojuro did just "
             "before the film begins, and that \"the remaining six episodes "
             "are recompiled cuts of the film\". So this list carries the "
             "film and that one original episode, and refuses the six re-cut "
             "ones. Fifty-seven of the series' 63 episodes are here; the six "
             "that are missing are the film."],
            ["The two compilation films are not here either.",
             "To the Swordsmith Village (2023) and To the Hashira Training "
             "(2024) are theatrical compilations of episodes that are already "
             "rows on this list — the closing episodes of one season plus an "
             "early screening of the next season's first. Their own articles "
             "call them compilations of the television series. Listing them "
             "would count those episodes a second time, so they are named "
             "here instead."],
            ["Episode numbers are the ones the source gives.",
             "Each row carries its number inside its own season, which is why "
             "the Entertainment District rows run 8 to 18 rather than "
             "restarting at 1. The gap where 2 to 7 would be is the Mugen "
             "Train film."],
            ["One Infinity Castle film has opened.",
             "The arc was announced in June 2024 as a trilogy for cinemas. "
             "Part 1: Akaza Returns opened in Japan on July 18, 2025 and is "
             "the only installment with a release date in the source. Parts 2 "
             "and 3 have no dated release and are not listed; they join when "
             "they open."],
            ["The television series is finished, but the story is not.",
             "Four seasons, 63 episodes, April 6, 2019 to June 30, 2024. "
             "There is no fifth season because the Infinity Castle arc went "
             "to cinemas instead — the series article closes its run with a "
             "final airdate and notes that only films are confirmed to "
             "follow. The list carries on into the films rather than stopping "
             "mid-story."],
            ["Nothing is weighted, and hours are not tracked on this list.",
             "Wikipedia documents no running time for this series: the "
             "television infobox has no runtime, none of the four season "
             "articles has one, and not one of the 63 episode blocks carries "
             "one. The only lengths in the source are for four episodes — the "
             "extended openers and finales of seasons 3 and 4, named in those "
             "sections — and the two films. Four durations out of 57 cannot "
             "weight a list, so every row counts one, films included. "
             "Weighting only the films would be worse than weighting nothing: "
             "a row with no weight silently counts as a full hour, so 57 "
             "half-hour episodes would read as 57 hours. The film rows give "
             "their runtimes in the row note instead."],
            ["The season divisions are consensus, not official.",
             "The source article says so itself: the arc titles are official, "
             "but no official source has ever set out where one season ends "
             "and the next begins. Mugen Train and Entertainment District are "
             "treated as halves of one second season because they aired "
             "back to back. The sections here are named for the arcs, which "
             "are not in doubt."],
            "Titles and airdates machine-read from Wikipedia's four Demon "
            "Slayer season articles and the film articles; every season's "
            "count is asserted against both the list article's series "
            "overview and the season article's own infobox, every season's "
            "first and last airdates against that infobox, the overall "
            "numbering asserted contiguous, and the total cross-checked "
            "against the series infobox before this builds.",
        ],
        "sections": sections,
    }

    out = prop.write(p)
    print("wrote %s — %d rows in %d sections (%d of %d episodes, %d films)"
          % (out.name, total, len(sections), episodes_listed, TOTAL_EPISODES,
             len(FILM_PAGES)))
    for s in sections:
        print("   %-42s %3d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
