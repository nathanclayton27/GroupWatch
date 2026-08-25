#!/usr/bin/env python3
"""Generate properties/chainsaw-man.json — the twelve episodes and the film.

    python3 tools/make_chainsaw-man.py

MAPPA's television season, October 12 to December 28, 2022, followed by the
feature that continues straight on from it. 13 rows.

THE FILM IS A ROW BECAUSE IT HAS OPENED, AND THAT IS TESTED, NOT ASSUMED.
`Chainsaw Man – The Movie: Reze Arc` is dated by its own article's infobox
{{Film date}}, which main() reads and compares against TODAY below. It carries
exactly one {{Film date}} — September 19, 2025 — and main() asserts both that
there is only one (a second would mean another installment has a date and this
list is short) and that it is in the past. A film dated after TODAY fails the
build with a message saying so rather than shipping as a row nobody can watch;
this is the same gate that keeps unreleased games off the Gears of War list.
Wikidata agrees independently: Q123906765 carries P577 in 2025 and P2047 of
100 minutes.

THE ANNOUNCED SEQUEL IS NOT A ROW. `Chainsaw Man – Assassins Arc` was
announced at Jump Festa in December 2025 and the film's director is returning,
but the source gives it no release date and does not even say what form it
takes — main() asserts that its section still carries no date of any kind. It
is named in the notes so its absence is a statement, and it joins this list
when it has a date.

WEIGHTS. None, and the film is the reason it is worth explaining. Its runtime
is documented twice over — 100 minutes on its own article and on Wikidata —
but no episode's is. What the source gives for the television run is a single
series-level figure in the series infobox, "23 minutes" with "25 minutes" for
episodes 1 and 10, uncited; no episode has an article of its own, and the one
episode that has a Wikidata item at all carries no P2047. Spreading a
series-level number across ten individual episodes would invent precision the
source refuses to give, so those ten rows have no sourceable runtime.

It is all rows or none. Weighting the film alone would be strictly worse than
weighting nothing, because a row with no `w` on a weighted list resolves to a
full hour: twelve roughly-half-hour episodes would read as twelve hours beside
a 1.67-hour film. So nothing is weighted, main() asserts nothing is, and the
film's 100 minutes lives in its row note as text where it informs without
entering the arithmetic. main() also asserts that no episode block has gained
a Runtime and that the series infobox's runtime field still parses to exactly
that one blanket figure plus its two named exceptions — if either changes, the
decision is worth re-making.

Everything is machine-read from the cached Wikipedia wikitext in
scratch/agent-mob/chainsaw-man/ — the episode list, the series article, the
film article and the franchise article. Nothing is typed in from memory.
Before anything is written: the episode count is asserted three ways (parsed
rows, the series infobox's num_episodes, and the list article's own sentence
about how much manga it adapts); the numbering is asserted contiguous 1..12;
airdates are asserted in broadcast order and matched against the series
infobox's first_aired and last_aired and against the franchise article's
prose; the film's release date is matched against the series article's prose
as well as its own infobox; and the accent pair is asserted unused by every
other property on disk.
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop, wiki  # noqa: E402

SLUG = "chainsaw-man"
CACHE = prop.ROOT / "scratch" / "agent-mob" / SLUG
LIST_PAGE = "List of Chainsaw Man episodes"
SERIES_PAGE = "Chainsaw Man (TV series)"
FILM_PAGE = "Chainsaw Man – The Movie: Reze Arc"
FRANCHISE_PAGE = "Chainsaw Man"

EPISODES = 12   # asserted three ways before anything is written
LISTED = EPISODES + 1

# Hard-coded rather than read from the clock so re-running this produces the
# same file. Any film whose release date is after this has not opened and is
# not a row.
TODAY = (2026, 8, 25)

ACCENT = "#A71930"       # the crimson the episode list uses for its own tables
ACCENT_DARK = "#F04E5E"  # ...raised for dark mode

MONTHS = {m: i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"], 1)}


def text(page):
    t = wiki.wikitext(page, cache_dir=CACHE)
    assert t, "no wikitext for %r" % page
    return t


def strip_refs(t):
    t = re.sub(r"<ref[^>]*/>", "", t)
    return re.sub(r"<ref.*?</ref>", "", t, flags=re.S)


def flat(t):
    """Refs gone and whitespace collapsed — prose matched as one line."""
    return re.sub(r"\s+", " ", strip_refs(t))


def date_in(field, kind="Start"):
    m = re.search(r"\{\{%s date\s*\|\s*(\d{4})\s*\|\s*(\d{1,2})\s*\|"
                  r"\s*(\d{1,2})" % kind, field or "", re.I)
    assert m, "no %s date in %r" % (kind.lower(), (field or "")[:80])
    return tuple(int(g) for g in m.groups())


def parse_date(s):
    m = re.match(r"\s*(\w+)\s+(\d{1,2}),\s*(\d{4})\s*$", s or "")
    assert m and m.group(1) in MONTHS, "unparsed date %r" % s
    return (int(m.group(3)), MONTHS[m.group(1)], int(m.group(2)))


def fmt_date(d):
    names = {v: k for k, v in MONTHS.items()}
    return "%s %d, %d" % (names[d[1]], d[2], d[0])


def read_episodes(list_text):
    """[(number, title, (y,m,d))], with the weights check on every block."""
    raw = wiki.episodes(list_text)
    assert raw, "the episode list parsed empty"
    rows = []
    for n, _n2, title, _year, block in raw:
        assert not re.search(r"\|\s*Runtime\s*=", block, re.I), \
            "episode %s has a per-episode runtime now — revisit weights" % n
        assert n and title, "episode row incomplete: %r" % ((n, title),)
        rows.append((n, title, date_in(block)))
    assert [n for n, _, _ in rows] == list(range(1, len(rows) + 1)), \
        "episode numbering is not contiguous 1..%d" % len(rows)
    dates = [d for _, _, d in rows]
    assert dates == sorted(dates), "airdates are not in broadcast order"
    return rows


def adapted_chapters(list_text):
    """How much manga the season covers, in the list article's own words."""
    m = re.search(r"It adapts the first (\d+) chapters of the manga in "
                  r"(\d+) episodes\.", flat(list_text))
    assert m, "the list article no longer says how many chapters the season " \
              "adapts — the section intro states it and must be re-read"
    chapters, eps = int(m.group(1)), int(m.group(2))
    assert eps == EPISODES, \
        "the list article says %d episodes, this generator carries %d" \
        % (eps, EPISODES)
    return chapters


def series_runtime(ib):
    """The series-level runtime figure, read so the weights note can quote it.

    This is the whole reason the list is unweighted: one blanket number for
    the run, with two episodes named as exceptions and nothing said about the
    other ten. If the field ever becomes per-episode, this trips."""
    rt = ib("runtime").strip()
    m = re.match(r"^\{\{UBL\|(\d+) minutes\|(\d+) minutes \(#([\d, ]+)\)\}\}$",
                 rt)
    assert m, "the series runtime field is %r, no longer one blanket figure " \
              "with named exceptions — revisit weights" % rt[:90]
    base, longer = int(m.group(1)), int(m.group(2))
    named = [int(x) for x in re.findall(r"\d+", m.group(3))]
    assert 0 < len(named) < EPISODES, \
        "the runtime field now names %d of %d episodes — if it names them " \
        "all, every row has a sourceable runtime and weights are back on" \
        % (len(named), EPISODES)
    return base, longer, named


def read_film():
    """(title, release date, runtime minutes) — and the release gate."""
    t = text(FILM_PAGE)
    ib = wiki.infobox(t, kind="film")
    assert ib, "no film infobox on %s" % FILM_PAGE

    m = re.search(r"\{\{Nihongo\|'''''(.*?)'''''", t)
    assert m, "%s states no bolded official title in its lead" % FILM_PAGE
    title = wiki.clean(m.group(1))
    assert title == FILM_PAGE, \
        "the film's lead titles it %r, the article is %r" % (title, FILM_PAGE)

    dates = re.findall(r"\{\{Film date\|([^}]*)\}\}", ib("released"))
    assert len(dates) == 1, \
        "%s carries %d {{Film date}} entries — a second one would mean " \
        "another installment has a release date and this list is short" \
        % (FILM_PAGE, len(dates))
    released = tuple(int(b) for b in dates[0].split("|")[:3])
    assert released <= TODAY, \
        "%s is dated %s, which has not happened yet — an unreleased film is " \
        "not a row; name it in the notes instead" % (FILM_PAGE, released)

    rt = re.search(r"(\d+)\s*minutes", ib("runtime"))
    assert rt, "no runtime for %s" % FILM_PAGE
    mins = int(rt.group(1))
    assert 60 <= mins <= 200, "%s runtime %d looks wrong" % (title, mins)

    # what the film is, in the source's words — the section intro says it
    seq = re.search(r"the film is a direct sequel to the first season of the "
                    r"\[\[Chainsaw Man \(TV series\)\|anime television "
                    r"series\]\] and adapts events covered by the original "
                    r"manga's (\w+) and (\w+) volumes", flat(t))
    assert seq, "the film's lead no longer calls itself a direct sequel to " \
                "the season — its placement after the finale rests on that"
    return title, released, mins, (seq.group(1), seq.group(2))


def series_facts():
    """The series article: the infobox, the film's date in prose, the sequel."""
    t = text(SERIES_PAGE)
    ib = wiki.infobox(t, kind="television")
    assert ib, "no television infobox on %s" % SERIES_PAGE
    assert ib("num_episodes").strip() == str(EPISODES), \
        "the series infobox says %r episodes, this generator carries %d" \
        % (ib("num_episodes"), EPISODES)
    assert ib("num_seasons").strip() == "1", \
        "the series infobox says %r seasons — a second season would change " \
        "the shape of this list" % ib("num_seasons")
    network = wiki.clean(ib("network"))
    assert network == "TV Tokyo", "the series aired on %r" % network[:60]

    film_date = re.search(r"It was distributed by \[\[Toho\]\] and premiered "
                          r"in Japan on (\w+ \d{1,2}, \d{4})\.", flat(t))
    assert film_date, "the series article no longer dates the film"

    seq = re.search(r"===\s*Sequel\s*===(.*?)(?=\n==[^=])", t, re.S)
    assert seq, "no Sequel section on the series article"
    body = flat(seq.group(1))
    assert "Assassins Arc" in body, \
        "the Sequel section no longer names Assassins Arc"
    assert not re.search(r"(?:premier|releas|air)\w*\s+(?:in Japan\s+)?on "
                        r"\w+ \d{1,2}, \d{4}", body) \
        and "{{Film date" not in seq.group(1) \
        and "{{Start date" not in seq.group(1), \
        "the announced sequel now has a release date — it may belong on " \
        "this list: %r" % body[:200]
    return ib, parse_date(film_date.group(1)), body


def franchise_facts():
    """The franchise article's independent dates for the season and the film."""
    t = flat(text(FRANCHISE_PAGE))
    a = re.search(r"A (\d+)-episode \[\[anime\]\] television series "
                  r"adaptation, produced by \[\[MAPPA\]\], was broadcast on "
                  r"\[\[TV Tokyo\]\] and its affiliates from (\w+ \d{1,2}) to "
                  r"(\w+ \d{1,2}, \d{4})\.", t)
    assert a, "the franchise article no longer states the season's length"
    year = a.group(3).split(", ")[1]
    b = re.search(r"An anime film, titled .{0,200}?Reze-hen\}\}, premiered in "
                  r"Japan on (\w+ \d{1,2}, \d{4})\.", t)
    assert b, "the franchise article no longer dates the film"
    return (int(a.group(1)),
            parse_date("%s, %s" % (a.group(2), year)),
            parse_date(a.group(3)),
            parse_date(b.group(1)))


def check_accent():
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
    rows = read_episodes(list_text)
    chapters = adapted_chapters(list_text)
    ib, film_date_prose, sequel_body = series_facts()
    fr_eps, fr_first, fr_last, fr_film = franchise_facts()
    film_title, film_date, film_mins, film_volumes = read_film()
    base_min, long_min, long_eps = series_runtime(ib)
    check_accent()

    # 1. the season's length and dates, three independent readings
    assert len(rows) == EPISODES, \
        "parsed %d episodes, expected %d" % (len(rows), EPISODES)
    assert fr_eps == EPISODES, \
        "the franchise article says %d episodes, parsed %d" % (fr_eps, len(rows))
    assert date_in(ib("first_aired")) == rows[0][2] == fr_first, \
        "the season's first airdate disagrees across the sources: %s / %s / %s" \
        % (ib("first_aired"), rows[0][2], fr_first)
    assert date_in(ib("last_aired"), "End") == rows[-1][2] == fr_last, \
        "the season's last airdate disagrees across the sources: %s / %s / %s" \
        % (ib("last_aired"), rows[-1][2], fr_last)

    # 2. the film's date, three independent readings, and it is in the past
    assert film_date == film_date_prose == fr_film, \
        "the film's release date disagrees across the sources: %s / %s / %s" \
        % (film_date, film_date_prose, fr_film)
    assert film_date > rows[-1][2], \
        "the film predates the season finale — its placement is wrong"

    # 3. the two runtimes the source names are exceptions, not the rule
    assert set(long_eps) <= {n for n, _, _ in rows}, \
        "the runtime field names episodes %s, which are not in the season" \
        % long_eps

    sections = [{
        "id": "s1",
        "title": "Season 1",
        "sub": prop.join_bits(str(rows[0][2][0]), "%d episodes" % len(rows),
                              wiki.clean(ib("network"))),
        "intro": "MAPPA's television season, and the whole of it so far — "
                 "twelve episodes covering the manga's first %d chapters. "
                 "Every episode closes on a different ending theme, so the "
                 "credits are worth staying for." % chapters,
        "open": True,
        "items": [{"id": "csm-e%d" % n, "t": t, "n": str(n)}
                  for n, t, _d in rows],
    }, {
        "id": "film",
        "title": "Reze Arc",
        "sub": prop.join_bits(str(film_date[0]), "the film",
                              "%d minutes" % film_mins),
        "intro": "A direct sequel to the season, in cinemas from %s. It "
                 "adapts the manga's %s and %s volumes, so it carries on "
                 "from the finale — watch it after episode %d."
                 % (fmt_date(film_date), film_volumes[0], film_volumes[1],
                    len(rows)),
        "items": [{
            "id": "csm-film-reze-arc",
            "t": film_title,
            "n": str(film_date[0]),
            "note": prop.join_bits("%d feature film" % film_date[0],
                                   "%d minutes" % film_mins,
                                   "a direct sequel to the season",
                                   "released %s" % fmt_date(film_date)),
        }],
    }]

    total = sum(len(s["items"]) for s in sections)
    assert total == LISTED, "%d rows, expected %d" % (total, LISTED)
    assert sum(1 for s in sections for x in s["items"] if "w" in x) == 0, \
        "a weight crept in — this list is unweighted end to end, film included"

    p = {
        "slug": SLUG,
        "title": "Chainsaw Man",
        "subtitle": "the twelve episodes, and the film that follows them",
        "kind": "tv & film",
        "popularity": 72,
        "year": "%d–" % rows[0][2][0],
        "blurb": "MAPPA's 2022 season in full, then the feature that carries "
                 "straight on from the finale — thirteen entries in the "
                 "order they were made.",
        "unit": {"one": "entry", "many": "entries"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": ACCENT,
        "accentDark": ACCENT_DARK,
        "tiers": False,
        "notes": [
            ["The film is here because it has opened.",
             "Reze Arc premiered in Japan on %s. That date is read off the "
             "film's own article rather than taken on trust, and anything "
             "dated after today fails this list's build instead of appearing "
             "as a row nobody can watch yet. It is a direct sequel to the "
             "season and sits after the finale, which is where the source "
             "puts it." % fmt_date(film_date)],
            ["A second animated work is announced and undated.",
             "Chainsaw Man – Assassins Arc was announced at Jump Festa in "
             "December 2025, with the film's director returning. The source "
             "gives it no release date and does not say what form it takes — "
             "series or film — so there is nothing to list. It joins this "
             "list when it has a date."],
            ["Nothing is weighted, and that includes the film.",
             "The film's runtime is documented twice over — %d minutes on its "
             "own article and on Wikidata — but no episode's is. The series "
             "infobox gives one blanket figure for the whole run, \"%d "
             "minutes\", with \"%d minutes\" for episodes %s, and says "
             "nothing about the other ten; no episode has an article of its "
             "own, and "
             "the one episode with a Wikidata item carries no runtime there "
             "either. Spreading a series-level number across ten individual "
             "episodes would invent precision the source refuses to give. It "
             "is all rows or none, so it is none: weighting the film alone "
             "would be worse than weighting nothing, because a row with no "
             "weight silently counts as a full hour and twelve half-hour "
             "episodes would read as twelve. The film's %d minutes is in its "
             "row note instead, where it informs without entering the "
             "arithmetic."
             % (film_mins, base_min, long_min,
                " and ".join(str(n) for n in long_eps), film_mins)],
            ["Watch order is release order, and there is no branch in it.",
             "Twelve episodes, then the film. Nothing here is optional and "
             "nothing is out of sequence."],
            "Titles and airdates machine-read from Wikipedia's List of "
            "Chainsaw Man episodes; the season's length and dates are "
            "asserted against the series article's infobox and the franchise "
            "article's prose, the numbering asserted contiguous 1–%d, and "
            "the film's release date read from its own infobox and matched "
            "against two other articles before this builds." % EPISODES,
        ],
        "sections": sections,
    }

    out = prop.write(p)
    print("wrote %s — %d rows in %d sections (%d episodes + 1 film)"
          % (out.name, total, len(sections), EPISODES))
    for s in sections:
        print("   %-12s %3d  %s" % (s["title"], len(s["items"]), s["sub"]))
    print("   film: %s, %s, %d minutes (unweighted)"
          % (film_title, fmt_date(film_date), film_mins))


if __name__ == "__main__":
    main()
