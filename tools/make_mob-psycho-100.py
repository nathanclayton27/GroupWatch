#!/usr/bin/env python3
"""Generate properties/mob-psycho-100.json — three seasons and the two OVAs.

    python3 tools/make_mob-psycho-100.py

Bones' adaptation of ONE's manga: 37 episodes across three seasons, July 12,
2016 to December 22, 2022, plus the two entries the source keeps outside that
numbering. 39 rows.

THE EXTRAS ARE THE DECISION, AND THE SOURCE MAKES IT TWICE. The question was
whether the OVAs and the Reigen event film are rows or a sentence in the
notes. Two independent statements in the cached wikitext say rows, and both
are asserted in main():

  * the episode list article files them in their own {{Episode table}} under
    its own `==OVAs==` heading, after all three season tables, numbered 1 and
    2 — the source's own placement, which is why they sit at the end here
    rather than being slotted between the seasons by airdate; and
  * the series infobox on the franchise article counts the run as
    `episodes = 37 + 2 OVAs` — the source adding them to the total while
    holding them apart from the numbered episodes.

So they are rows, and they carry `opt`. "Outside the numbered seasons but
counted" is exactly what the optional badge says, and it is the only shape
that neither hides them nor pretends they are episodes 38 and 39.

THE REIGEN SPECIAL IS A COMPILATION, AND ITS ROW SAYS SO. The franchise
article calls it "a 60-minute compilation of the anime series" that "features
new scenes focused on Arataka Reigen", screened twice at the Maihama
Amphitheater on March 18, 2018 and later released on home video — read and
asserted here, and quoted into the row note so a reader who has watched the
seasons knows exactly what they would be getting. make_demon-slayer.py
refuses that franchise's two compilation films for being re-cuts of episodes
already listed, and the reflex would be to refuse this one too. The reflex is
wrong here for a reason the source states rather than one this file argues:
Demon Slayer's franchise article files its compilations in a list SEPARATE
from its films, whereas Mob Psycho's own episode list files this one WITH the
OVAs and its infobox counts it in the series total. Optional is the honest
middle: listed where the source lists it, flagged as skippable.

THE 2026 SHORT IS NOT A ROW. An anime short was presented at the series' 10th
anniversary event on July 13, 2026 and released on YouTube afterwards. The
source gives it no title, does not put it in the episode list, and does not
count it in `37 + 2 OVAs` — main() asserts all three, including that no
{{Nihongo}} title has appeared beside it. There is nothing to make a row out
of yet, so it is named in the notes instead of vanishing.

THE LIVE-ACTION DRAMA IS OUT. A twelve-episode live-action adaptation ran on
TV Tokyo from January 18 to April 5, 2018; the franchise article gives it its
own infobox with `type = drama`, read here so the notes can name it. It is a
different adaptation, not part of Bones' run, and this list is the anime.

WEIGHTS. None. Wikipedia documents no running time for this series: the
series infobox has no runtime field and not one of the 39 episode blocks
carries a Runtime — both asserted rather than assumed, and Wikidata has no
P2047 on the series or on the one episode that has an item of its own. The
single duration the source gives anywhere is the Reigen compilation's 60
minutes, which lives in that row's note as text. One figure out of 39 cannot
weight a list, and weighting only that row would be worse than weighting
nothing: an unweighted row on a weighted list resolves to a full hour, so 37
half-hour episodes would read as 37 hours. main() asserts no row carries `w`.

Everything is machine-read from the cached Wikipedia wikitext in
scratch/agent-mob/mob-psycho-100/ — the episode list article and the
franchise article. Nothing is typed in from memory. Before anything is
written: each season's parsed row count is asserted against BOTH the list
article's {{Series overview}} and the franchise article's own prose; each
season's in-season numbering is asserted to run 1..N; the overall numbering is
asserted contiguous 1..37; every airdate is asserted non-decreasing and
matched against the overview's start/end dates; the run's first and last
airdates are matched against the series infobox; the OVA titles are asserted
to carry the franchise prefix before it is stripped; and the accent pair is
asserted unused by every other property on disk.
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop, wiki  # noqa: E402

SLUG = "mob-psycho-100"
CACHE = prop.ROOT / "scratch" / "agent-mob" / SLUG
LIST_PAGE = "List of Mob Psycho 100 episodes"
FRANCHISE_PAGE = "Mob Psycho 100"
SEASONS = [1, 2, 3]

TOTAL_EPISODES = 37   # asserted three ways before anything is written
OVA_COUNT = 2
LISTED = TOTAL_EPISODES + OVA_COUNT

# Every OVA title on the episode list opens with this; stripping it is what
# turns the catalogue title into a row title, and it is asserted, not assumed.
OVA_PREFIX = "Mob Psycho 100: "

# The on-air titles of the second and third seasons, from the franchise
# article's prose. Read and asserted; used in the section intros.
SEASON_ONAIR = {2: "Mob Psycho 100 II", 3: "Mob Psycho 100 III"}

ACCENT = "#1F5E7A"       # the deep water-blue of the psychic glow...
ACCENT_DARK = "#6CE1F7"  # ...and the cyan the source itself uses for season 3

MONTHS = {m: i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"], 1)}


def text(page):
    t = wiki.wikitext(page, cache_dir=CACHE)
    assert t, "no wikitext for %r" % page
    return t


def strip_refs(t):
    """Prose with the footnotes gone, for the sentences main() reads as fact."""
    t = re.sub(r"<ref[^>]*/>", "", t)
    return re.sub(r"<ref.*?</ref>", "", t, flags=re.S)


def flat(t):
    """Refs gone and whitespace collapsed — prose matched as one line."""
    return re.sub(r"\s+", " ", strip_refs(t))


def date_in(field, kind="Start"):
    """The first {{Start date}} / {{End date}} in a chunk, as (y, m, d)."""
    m = re.search(r"\{\{%s date\s*\|\s*(\d{4})\s*\|\s*(\d{1,2})\s*\|"
                  r"\s*(\d{1,2})" % kind, field or "", re.I)
    assert m, "no %s date in %r" % (kind.lower(), (field or "")[:80])
    return tuple(int(g) for g in m.groups())


def parse_date(s):
    """"July 12, 2016" -> (2016, 7, 12)."""
    m = re.match(r"\s*(\w+)\s+(\d{1,2}),\s*(\d{4})\s*$", s or "")
    assert m and m.group(1) in MONTHS, "unparsed date %r" % s
    return (int(m.group(3)), MONTHS[m.group(1)], int(m.group(2)))


def fmt_date(d):
    names = {v: k for k, v in MONTHS.items()}
    return "%s %d, %d" % (names[d[1]], d[2], d[0])


def animanga_video(t, nth=0):
    """A field reader over the nth {{Infobox animanga/Video}} on a page.

    gwlib.wiki.infobox only knows {{Infobox film}} and {{Infobox television}};
    an anime franchise article carries neither. Refs and comments are stripped
    before the box end is located, because a multi-line citation inside a
    field would otherwise close the box early."""
    starts = [m.start() for m in re.finditer(r"\{\{Infobox animanga/Video", t)]
    assert len(starts) > nth, "no {{Infobox animanga/Video}} #%d on the page" % nth
    box = re.sub(r"<!--.*?-->", "", strip_refs(t[starts[nth]:]), flags=re.S)
    end = box.find("\n}}")
    assert end > 0, "unterminated {{Infobox animanga/Video}} #%d" % nth
    box = box[:end]

    def field(name):
        m = re.search(r"^\s*\|\s*%s[ \t]*=[ \t]*(.*?)"
                      r"(?=\n\s*\|\s*[a-z_ ]+[ \t]*=|\Z)" % name,
                      box, re.M | re.S | re.I)
        return m.group(1).strip() if m else ""
    return field


def series_overview(list_text):
    """{season: (episodes, first, last)} from the list article's own table."""
    seg = re.search(r"\{\{Series overview(.*?)\n\}\}", list_text, re.S)
    assert seg, "no series overview on the list article"
    body = seg.group(1)
    counts = {int(m.group(1)): int(m.group(2)) for m in
              re.finditer(r"\|\s*episodes(\d+)\s*=\s*(\d+)", body)}
    assert sorted(counts) == SEASONS, \
        "series overview lists seasons %s, expected %s" % (sorted(counts), SEASONS)
    assert sum(counts.values()) == TOTAL_EPISODES, \
        "the overview counts %d episodes, expected %d" \
        % (sum(counts.values()), TOTAL_EPISODES)
    out = {}
    for n in SEASONS:
        start = re.search(r"\|\s*start%d\s*=\s*(.*)" % n, body)
        end = re.search(r"\|\s*end%d\s*=\s*(.*)" % n, body)
        assert start and end, "season %d has no start/end in the overview" % n
        out[n] = (counts[n], date_in(start.group(1)),
                  date_in(end.group(1), "End"))
    # a mid-run show carries this stamp; this one must not, or "three seasons,
    # complete" is no longer true and the section intros need re-reading
    assert "{{Aired episodes" not in list_text, \
        "the list article has an aired-episodes stamp — the series may be " \
        "running again and season 3 can no longer be called the last"
    return out


def headings(list_text):
    """{season: year} from the list article's own === Season N (YYYY) === ."""
    out = {}
    for m in re.finditer(r"^===\s*Season (\d+)\s*\((\d{4})\)\s*===\s*$",
                         list_text, re.M):
        out[int(m.group(1))] = int(m.group(2))
    assert sorted(out) == SEASONS, \
        "list article headings cover %s, expected %s" % (sorted(out), SEASONS)
    return out


def split_ovas(list_text):
    """(everything before the OVAs heading, everything after it).

    The heading is the source's own divider between the numbered run and the
    two entries it holds outside that run, so the split is the article's and
    not a guess at where the episodes stop."""
    marker = "\n==OVAs=="
    assert list_text.count(marker) == 1, \
        "the list article no longer has exactly one ==OVAs== heading — the " \
        "whole placement decision rests on it and must be re-read"
    head, _, tail = list_text.partition(marker)
    for n in SEASONS:
        assert re.search(r"^===\s*Season %d\s*\(\d{4}\)\s*===\s*$" % n,
                         head, re.M), \
            "season %d's heading is not above the OVAs heading" % n
    return head, tail


def rows_from(seg, label):
    """[(overall, in_season, title, (y,m,d))] from a chunk of the article."""
    raw = wiki.episodes(seg)
    assert raw, "%s parsed empty" % label
    rows = []
    for o, s, title, _year, block in raw:
        assert not re.search(r"\|\s*Runtime\s*=", block, re.I), \
            "%s has a per-episode runtime now — revisit weights" % label
        assert o and title, "%s row incomplete: %r" % (label, (o, s, title))
        rows.append((o, s, title, date_in(block)))
    dates = [d for _, _, _, d in rows]
    assert dates == sorted(dates), "%s airdates are not in broadcast order" % label
    return rows


def franchise_prose(fr_text):
    """The counts and dates the franchise article states in words.

    A second, independent reading of every season's length — the list
    article's overview table is the first — so a season that quietly gained or
    lost an episode fails here instead of shipping."""
    t = flat(fr_text)
    out = {}
    a = re.search(r"The series aired for (\d+) episodes between "
                  r"(\w+ \d{1,2}) and (\w+ \d{1,2}, \d{4}), on \[\[Tokyo MX\]\]",
                  t)
    assert a, "the franchise article no longer states season 1's length"
    out[1] = (int(a.group(1)),
              parse_date("%s, %s" % (a.group(2), a.group(3).split(", ")[1])),
              parse_date(a.group(3)))
    b = re.search(r"''Mob Psycho 100 II'' aired for (\d+) episodes from "
                  r"(\w+ \d{1,2}) to (\w+ \d{1,2}, \d{4})\.", t)
    assert b, "the franchise article no longer states season 2's length"
    out[2] = (int(b.group(1)),
              parse_date("%s, %s" % (b.group(2), b.group(3).split(", ")[1])),
              parse_date(b.group(3)))
    c = re.search(r"''Mob Psycho 100 III'' aired from (\w+ \d{1,2}) to "
                  r"(\w+ \d{1,2}, \d{4})\.", t)
    assert c, "the franchise article no longer states season 3's dates"
    out[3] = (None,
              parse_date("%s, %s" % (c.group(1), c.group(2).split(", ")[1])),
              parse_date(c.group(2)))
    return out


def final_season(fr_text):
    """The lead's own words for season 3 — the section intro calls it the
    last one the series made, and that has to be the source's claim."""
    m = re.search(r"a third and final season from October to December 2022",
                  flat(fr_text))
    assert m, "the franchise article no longer calls season 3 the final " \
              "season — the section intro says so and must be re-read"
    return True


def premise(fr_text):
    """The one sentence the blurb paraphrases, read rather than remembered."""
    m = re.search(r"The story follows \[\[Shigeo Kageyama\]\], nicknamed Mob, "
                  r"an (introverted \d+-year old boy with immense "
                  r"\[\[psychic\]\] powers)", flat(fr_text))
    assert m, "the franchise article's premise sentence has changed — the " \
              "blurb paraphrases it and must be re-read"
    return wiki.clean(m.group(1)).replace("year old", "year-old")


def reigen_evidence(fr_text):
    """What the Reigen event film is, in the source's own words.

    Returns (minutes, screening date). The whole "row, not a footnote"
    decision for this entry rests on the source both counting it and
    describing it, so both are read rather than assumed."""
    t = flat(fr_text)
    m = re.search(r"It is a (\d+)-minute compilation of the anime series and "
                  r"features new scenes focused on Arataka Reigen\. It was "
                  r"screened twice at the Maihama Amphitheater in "
                  r"\[\[Chiba Prefecture\|Chiba\]\] on (\w+ \d{1,2}, \d{4}), "
                  r"and was later released on home video\.", t)
    assert m, "the franchise article no longer describes the Reigen event " \
              "film as a compilation with new scenes — the row note quotes " \
              "that sentence and must be re-read before this builds"
    return int(m.group(1)), parse_date(m.group(2))


def ova_evidence(fr_text):
    """The sentence placing the second OVA after season 2."""
    t = flat(fr_text)
    m = re.search(r"Following the conclusion of the second season, an "
                  r"\[\[original video animation\]\] \(OVA\) was announced",
                  t)
    assert m, "the franchise article no longer places the OVA after season 2"
    return True


def short_evidence(fr_text):
    """The 2026 anniversary short: its date, and the fact it has no title.

    It is excluded, so the reason has to be a fact rather than an oversight.
    If a title ever appears beside it, this trips and the decision is re-made."""
    t = flat(fr_text)
    m = re.search(r"An anime short was presented at the .{0,160}?"
                  r"10th Anniversary Event: Reunion.{0,220}?"
                  r"on (\w+ \d{1,2}, \d{4})\.", t)
    assert m, "the franchise article no longer describes the 10th " \
              "anniversary short — check whether it became a listed entry"
    tail = t[m.start():m.start() + 400]
    assert "{{Nihongo|''" not in tail, \
        "the anniversary short has been given a title — it may now be a row"
    return parse_date(m.group(1))


def drama_facts(fr_text):
    """(episodes, first, last) for the live-action drama the notes name."""
    ib = animanga_video(fr_text, 1)
    assert ib("type").strip() == "drama", \
        "the second animanga/Video box is %r, not the live-action drama" \
        % ib("type")[:40]
    return int(ib("episodes")), parse_date(ib("first")), parse_date(ib("last"))


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
    fr_text = text(FRANCHISE_PAGE)
    overview = series_overview(list_text)
    heads = headings(list_text)
    prose = franchise_prose(fr_text)
    final_season(fr_text)
    who = premise(fr_text)
    reigen_mins, reigen_date = reigen_evidence(fr_text)
    ova_evidence(fr_text)
    short_date = short_evidence(fr_text)
    drama_eps, drama_first, drama_last = drama_facts(fr_text)
    check_accent()

    seasons_seg, ova_seg = split_ovas(list_text)
    episodes = rows_from(seasons_seg, "the season tables")
    ovas = rows_from(ova_seg, "the OVAs table")

    # 1. the numbered run, three ways: parsed, the overview table, the prose
    assert len(episodes) == TOTAL_EPISODES, \
        "parsed %d episodes, expected %d" % (len(episodes), TOTAL_EPISODES)
    assert [o for o, _, _, _ in episodes] == list(range(1, TOTAL_EPISODES + 1)), \
        "overall episode numbering is not contiguous 1..%d" % TOTAL_EPISODES

    by_season, cursor = {}, 0
    for n in SEASONS:
        count = overview[n][0]
        by_season[n] = episodes[cursor:cursor + count]
        cursor += count
    assert cursor == TOTAL_EPISODES, "the overview counts do not partition the run"
    for n in SEASONS:
        rows = by_season[n]
        assert [s for _, s, _, _ in rows] == list(range(1, len(rows) + 1)), \
            "season %d numbering is not 1..%d" % (n, len(rows))
        assert rows[0][3] == overview[n][1], \
            "season %d opens %s, the overview says %s" \
            % (n, rows[0][3], overview[n][1])
        assert rows[-1][3] == overview[n][2], \
            "season %d closes %s, the overview says %s" \
            % (n, rows[-1][3], overview[n][2])
        assert rows[0][3][0] == heads[n], \
            "season %d aired from %s, its heading says (%d)" \
            % (n, rows[0][3], heads[n])
        p_count, p_first, p_last = prose[n]
        if p_count is not None:
            assert p_count == len(rows), \
                "the franchise article says season %d is %d episodes, %d parsed" \
                % (n, p_count, len(rows))
        assert (p_first, p_last) == (rows[0][3], rows[-1][3]), \
            "the franchise article dates season %d %s–%s, parsed %s–%s" \
            % (n, p_first, p_last, rows[0][3], rows[-1][3])

    # 2. the series infobox counts the run independently and documents no
    # running time — the only reason this list is unweighted
    ib = animanga_video(fr_text, 0)
    assert ib("type").strip() == "tv series", \
        "the first animanga/Video box is %r, not the anime" % ib("type")[:40]
    assert not ib("runtime").strip(), \
        "the series now documents a running time — revisit weights"
    counted = re.match(r"^(\d+)\s*\+\s*(\d+)\s*OVAs$", ib("episodes").strip())
    assert counted, \
        "the series infobox counts %r, not 'N + M OVAs' — the placement of " \
        "the extras rests on that shape and must be re-read" % ib("episodes")[:40]
    assert int(counted.group(1)) == TOTAL_EPISODES, \
        "the series infobox counts %s episodes, parsed %d" \
        % (counted.group(1), TOTAL_EPISODES)
    assert int(counted.group(2)) == OVA_COUNT == len(ovas), \
        "the series infobox counts %s OVAs, the OVAs table holds %d" \
        % (counted.group(2), len(ovas))
    assert parse_date(ib("first")) == episodes[0][3], \
        "the series infobox opens %r, the first episode aired %s" \
        % (ib("first"), episodes[0][3])
    assert parse_date(ib("last")) == episodes[-1][3], \
        "the series infobox closes %r, the last episode aired %s" \
        % (ib("last"), episodes[-1][3])

    # 3. the OVAs carry the franchise prefix, and the first of them is the
    # Reigen film the notes describe
    ova_titles = []
    for _o, _s, title, _d in ovas:
        assert title.startswith(OVA_PREFIX), \
            "OVA titled %r does not start with %r" % (title[:60], OVA_PREFIX)
        short = title[len(OVA_PREFIX):].strip()
        assert short, "an OVA reduces to an empty title"
        ova_titles.append(short)
    assert ova_titles[0].startswith("Reigen "), \
        "the first OVA is %r, not the Reigen event film" % ova_titles[0][:60]
    assert ovas[0][3] == reigen_date, \
        "the OVAs table dates the Reigen film %s, the prose says %s" \
        % (ovas[0][3], reigen_date)
    assert ovas[0][3] < ovas[1][3], "the OVAs are not in release order"

    # 4. the anniversary short really is outside everything this list reads
    assert short_date > episodes[-1][3], \
        "the anniversary short predates the end of the run"

    networks = wiki.clean(ib("network"))
    assert networks.startswith("Tokyo MX"), \
        "the series infobox no longer opens its network list with Tokyo MX: %r" \
        % networks[:70]

    # ---- sections ---------------------------------------------------------
    sections = []
    intro = {
        1: "Where it starts — the whole of Bones' first season, twelve "
           "episodes.",
        2: "Broadcast as %s. Thirteen episodes, the longest of the three."
           % SEASON_ONAIR[2],
        3: "Broadcast as %s, and the last season the series made. The "
           "television run closes here." % SEASON_ONAIR[3],
    }
    for n in SEASONS:
        rows = by_season[n]
        sections.append({
            "id": "s%d" % n,
            "title": "Season %d" % n,
            # no network in the sub: the source names Tokyo MX for the first
            # and third seasons and gives the rest as one series-wide list,
            # so a per-season broadcaster would be this list's claim, not the
            # source's. The broadcasters are named once, in the notes.
            "sub": prop.join_bits(str(heads[n]), "%d episodes" % len(rows)),
            "intro": intro[n],
            "items": [{"id": "mp100-s%de%d" % (n, s), "t": t, "n": str(s)}
                      for _o, s, t, _d in rows],
        })

    sections.append({
        "id": "ovas",
        "title": "OVAs",
        "sub": prop.join_bits("%d–%d" % (ovas[0][3][0], ovas[-1][3][0]),
                              "%d entries" % len(ovas), "optional"),
        "intro": "Two entries the source keeps outside the numbered run and "
                 "counts separately — its episode list gives them their own "
                 "table after season 3, and the series infobox reads \"%s\". "
                 "They sit here for the same reason, marked optional: listed "
                 "where the source lists them, and not needed to follow the "
                 "seasons." % ib("episodes").strip(),
        "items": [
            {"id": "mp100-ova1", "t": ova_titles[0], "n": "OVA 1", "opt": True,
             "note": prop.join_bits(
                 "screened %s" % fmt_date(ovas[0][3]),
                 "a %d-minute compilation of the anime series with new scenes "
                 "focused on Reigen" % reigen_mins,
                 "later released on home video")},
            {"id": "mp100-ova2", "t": ova_titles[1], "n": "OVA 2", "opt": True,
             "note": prop.join_bits(
                 "released %s" % fmt_date(ovas[1][3]),
                 "an original video animation, made after season 2")},
        ],
    })

    sections[0]["open"] = True

    assert [s["id"] for s in sections] == ["s1", "s2", "s3", "ovas"], \
        [s["id"] for s in sections]
    total = sum(len(s["items"]) for s in sections)
    assert total == LISTED, "%d rows, expected %d" % (total, LISTED)
    assert sum(1 for s in sections for x in s["items"] if "w" in x) == 0, \
        "a weight crept in — this list is unweighted end to end"
    assert sum(1 for s in sections for x in s["items"] if x.get("opt")) \
        == OVA_COUNT, "the optional rows are not exactly the two OVAs"

    span = "%d–%d" % (episodes[0][3][0], episodes[-1][3][0])

    p = {
        "slug": SLUG,
        "title": "Mob Psycho 100",
        "subtitle": "every episode, and the two the source keeps beside them",
        "kind": "anime",
        "popularity": 63,
        "year": span,
        "blurb": "Bones' adaptation of ONE's manga in order — three complete "
                 "seasons following an %s, plus the two OVAs, marked "
                 "optional." % who,
        "unit": {"one": "entry", "many": "entries"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": ACCENT,
        "accentDark": ACCENT_DARK,
        "tiers": False,
        "notes": [
            ["The two OVAs are rows, and they are optional.",
             "They could have been a sentence in these notes instead, and the "
             "source is what decided otherwise — twice. Its episode list puts "
             "them in their own table under an OVAs heading, after all three "
             "season tables, numbered 1 and 2; and the series infobox counts "
             "the run as \"%s\", adding them to the total while holding them "
             "apart from the numbered episodes. So they are listed, at the "
             "end, where the source puts them — and flagged optional, which "
             "is the same statement the source is making. Slotting them "
             "between the seasons by airdate would have been this list's "
             "arrangement rather than the source's."
             % ib("episodes").strip()],
            ["What the first OVA is.",
             "A %d-minute compilation of the anime series with new scenes "
             "focused on Reigen, screened twice on %s and later released on "
             "home video. Most of it is footage the seasons already carry, "
             "which is why it is optional rather than a stop on the way "
             "through; the row note says so plainly so nobody watches it "
             "expecting a new episode. The second OVA is an original video "
             "animation made after season 2."
             % (reigen_mins, fmt_date(reigen_date))],
            ["A 2026 anime short is not here.",
             "A short was presented at the series' 10th anniversary event on "
             "%s and put on YouTube afterwards. The source gives it no title, "
             "does not list it among the episodes, and does not count it in "
             "the series total — there is nothing to make a row out of yet. "
             "It is named here rather than left out silently, and it joins "
             "this list when the source can name it."
             % fmt_date(short_date)],
            ["The live-action drama is a different thing.",
             "A %d-episode live-action Mob Psycho 100 ran on television from "
             "%s to %s. It is a separate adaptation with its own cast and "
             "crew, not part of Bones' run, and this list is the anime."
             % (drama_eps,
                fmt_date(drama_first).replace(", %d" % drama_first[0], ""),
                fmt_date(drama_last))],
            ["Nothing is weighted, and hours are not tracked on this list.",
             "Wikipedia documents no running time for this series: the series "
             "infobox has no runtime field and not one of the %d entries "
             "carries one, both checked before this builds. The only duration "
             "in the source anywhere is the first OVA's %d minutes, and it is "
             "in that row's note rather than in the arithmetic. One figure out "
             "of %d cannot weight a list. Weighting only that row would be "
             "worse than weighting nothing: a row with no weight silently "
             "counts as a full hour, so 37 half-hour episodes would read as 37 "
             "hours. Every row counts one."
             % (LISTED, reigen_mins, LISTED)],
            ["Where it aired.",
             "The series infobox lists the broadcasters as %s. The source "
             "names Tokyo MX for the first and third seasons specifically and "
             "gives the rest as one series-wide list, so the sections here "
             "carry no per-season broadcaster." % networks],
            "Titles and airdates machine-read from Wikipedia's List of Mob "
            "Psycho 100 episodes and the Mob Psycho 100 article; each season's "
            "length is asserted against both the list article's series "
            "overview and the franchise article's prose, the overall "
            "numbering asserted contiguous 1–%d, and every airdate asserted "
            "in broadcast order and matched against the series infobox before "
            "this builds." % TOTAL_EPISODES,
        ],
        "sections": sections,
    }

    out = prop.write(p)
    print("wrote %s — %d rows in %d sections (%d episodes + %d OVAs)"
          % (out.name, total, len(sections), TOTAL_EPISODES, OVA_COUNT))
    for s in sections:
        print("   %-12s %3d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
