#!/usr/bin/env python3
"""Generate properties/steins-gate.json — the anime: both series and the film.

    python3 tools/make_steins-gate.py

White Fox's adaptation of 5pb. and Nitroplus' visual novel, plus its film and
its 2018 sequel series. 51 rows.

THE SLUG HAS NO SEMICOLON. The list is titled "Steins;Gate"; the address is
`?p=steins-gate`. A semicolon is a reserved sub-delimiter in a URL, not a
letter, and the slug is also the `property_id` every tick is stored against —
so it stays ASCII and boring. The title carries the real punctuation.

THE ORDER IS THE DECISION, AND HERE THE SOURCE AND RELEASE ORDER AGREE.
Two of the three pieces could plausibly sit anywhere relative to the 2011
run, so where each goes is read from the source rather than assumed. Both
statements are asserted in main():

  * the film — "The film takes place in August 2011, one year after the
    events of the anime series", and the franchise article calls it "an
    original storyline taking place after the events of the series"; and
  * Steins;Gate 0 — "As a sequel to the Steins;Gate visual novel game, and
    the 2011 anime adaptation, this series takes place in an alternate future
    timeline that forks off from the original series' ending".

Both follow the 2011 run, and they were released in that order — series
(2011), film (2013), 0 (2018) — so nothing had to be re-sequenced and the
list is in release order and story order at once. It is worth saying plainly
because it did not have to come out that way, and a list that quietly picks
one of two orders without saying which is a list you cannot check.

EPISODE 23β IS THE ONE PLACE THIS LIST DEPARTS FROM THE SOURCE'S TABLE.
Wikipedia's episode table for the 2011 series holds the twenty-four
episodes, then a twenty-fifth released with the final Blu-ray volume, then —
last, in release order — "23β", an alternate version of episode 23 that aired
during a 2015 rebroadcast. The franchise article says what it is for:
"depicting an alternate ending which leads into the events of Steins;Gate 0",
asserted below. So it sits immediately before Steins;Gate 0 here rather than
trailing the original run, because that is what the source says it does.

It is a row of its own rather than a swap for episode 23. HOW-IT-WORKS'
alternate-cut rule — one row per work, the version named in the note — is
about a film that exists in two lengths; this is a different episode with a
different title, a different air date and a different consequence, and the
series infobox counts it separately: "Twenty-four episodes, plus an
alternative version of episode 23 titled '23β', plus one OVA", also asserted.

OUT: THE VISUAL NOVELS AND THE GAMES, DELIBERATELY. This is the anime. The
2009 Steins;Gate visual novel that the 2011 series adapts and the 2015
Steins;Gate 0 visual novel that the 2018 series adapts are both named in the
notes so their absence reads as a decision; both release dates are read from
the source rather than typed. The four 2014 IBM promotional shorts on the
episode-list article are refused for the same reason the games are: they are
not the television run, and main() asserts they are still parked in their own
section so they cannot drift into the main table unnoticed.

WEIGHTS: NONE, AND IT IS ALL-OR-NOTHING. Wikipedia documents no running time
for either series — no `runtime` on either television infobox, and no
`Runtime` field on any of the 49 episode blocks, all asserted. The film gives
90 minutes, and that is the trap: weighting one row out of fifty-one while
the episodes have no verifiable number would leave every episode resolving
`WEIGHT = x.w >= 0 ? x.w : 1` to a full hour, so 49 half-hour episodes would
read as 49 hours (CLU-131). So no row carries a `w`, the film included, and
its runtime rides in the row note as text.

Everything is machine-read from the cached Wikipedia wikitext in
scratch/agent-abyss/steins-gate/. Before anything is written: each series'
numbering is asserted contiguous and its extras identified from the raw
EpisodeNumber text rather than an int() of it; each series' first and last
air dates are asserted against its own television infobox; the film's date is
asserted to agree between its infobox and the franchise article's prose; and
the accent pair is asserted unused by every other property on disk.
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop, wiki  # noqa: E402

SLUG = "steins-gate"
CACHE = prop.ROOT / "scratch" / "agent-abyss" / SLUG

SG_PAGE = "Steins;Gate (TV series)"
SG_LIST = "List of Steins;Gate episodes"
SG0_PAGE = "Steins;Gate 0 (TV series)"
SG0_LIST = "List of Steins;Gate 0 episodes"
FILM_PAGE = "Steins;Gate: The Movie − Load Region of Déjà Vu"
FRANCHISE_PAGE = "Steins;Gate"

SG_EPISODES = 24     # the 2011 run, asserted against its own infobox
SG0_EPISODES = 23    # the 2018 run, likewise
LISTED = 51          # 24 + OVA + film + 23β + 23 + OVA

# The heading the four IBM promotional shorts live under. They are refused,
# and main() asserts they are still down there rather than in the main table.
ONA_HEADING = "===''Steins;Gate: Sōmei Eichi no Cognitive Computing''"

ACCENT = "#4A2C6F"       # the CRT purple of a lab with the blinds down
ACCENT_DARK = "#FF9F1C"  # ...and the amber of a nixie tube

MONTHS = {m: i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"], 1)}


def text(page):
    t = wiki.wikitext(page, cache_dir=CACHE)
    assert t, "no wikitext for %r (run scratch/agent-abyss/fetch.py)" % page
    return t


def strip_refs(t):
    """Prose with the footnotes gone, for the sentences main() reads as fact."""
    t = re.sub(r"<ref[^>]*/>", "", t)
    return re.sub(r"<ref.*?</ref>", "", t, flags=re.S)


def raw_field(block, name):
    """One {{Episode list}} field exactly as written.

    This is the load-bearing reader on this list. gwlib's episodes() takes
    EpisodeNumber through int(re.search(r"\\d+")), which folds "23β" into 23
    and "25 (OVA)" into 25 — the first of those would collide with episode
    23's id and silently destroy a tick, so every number here comes from the
    raw text and the extras are identified by what the source actually
    wrote."""
    m = re.search(r"\|\s*%s\s*=\s*(.*?)(?=\n\s*\||\Z)" % name, block, re.S)
    return m.group(1).strip() if m else ""


def date_in(chunk):
    """The first {{Start date}} in a chunk, as (y, m, d)."""
    m = re.search(r"\{\{Start date\s*\|\s*(\d{4})\s*\|\s*(\d{1,2})\s*\|"
                  r"\s*(\d{1,2})", chunk or "", re.I)
    assert m, "no start date in %r" % (chunk or "")[:80]
    return tuple(int(g) for g in m.groups())


def plain_date(s):
    """A "September 14, 2011" style date, as (y, m, d)."""
    m = re.search(r"(%s)\s+(\d{1,2}),\s*(\d{4})" % "|".join(MONTHS), s or "")
    assert m, "no plain date in %r" % (s or "")[:80]
    return (int(m.group(3)), MONTHS[m.group(1)], int(m.group(2)))


def fmt_date(d):
    names = {v: k for k, v in MONTHS.items()}
    return "%s %d, %d" % (names[d[1]], d[2], d[0])


def brace_block(t, start):
    """The balanced {{...}} beginning at `start`.

    A naive split on a line-leading `}}` is wrong on these pages: the
    animanga infoboxes nest {{English anime network}} blocks whose closing
    braces also sit at column zero, and a split-based reader silently
    truncates every field after them."""
    depth, i = 0, start
    while i < len(t):
        if t.startswith("{{", i):
            depth, i = depth + 1, i + 2
        elif t.startswith("}}", i):
            depth, i = depth - 1, i + 2
            if depth == 0:
                return t[start:i]
        else:
            i += 1
    raise AssertionError("unbalanced braces from offset %d" % start)


def infobox_fields(block):
    """{field: value} for one template, split only on top-level pipes.

    Two things have to be tracked or the split is silently wrong, and both
    occur in these infoboxes:

      * nested templates — `writer = {{ubl|A|'''Supervised by''':{{efn|…}}}}`
        ends in four closing braces, so the scanner must step over `{{` and
        `}}` two characters at a time rather than testing every character
        (testing every character counts `}}}}` as three closes and throws the
        depth off, which shipped a reader that lost every field after
        `writer`); and
      * wikilinks — `network = [[AT-X (company)|AT-X]], [[Tokyo MX]]` carries
        a pipe at template depth zero, so `[[`/`]]` count as depth too."""
    body = block[2:-2]
    fields, depth, buf, i, n = {}, 0, "", 0, len(body)

    def flush(chunk):
        if "=" in chunk:
            k, v = chunk.split("=", 1)
            fields[k.strip().lower()] = v.strip()

    while i < n:
        two = body[i:i + 2]
        if two in ("{{", "[["):
            depth, buf, i = depth + 1, buf + two, i + 2
        elif two in ("}}", "]]"):
            depth, buf, i = depth - 1, buf + two, i + 2
        elif body[i] == "|" and depth == 0:
            flush(buf)
            buf, i = "", i + 1
        else:
            buf, i = buf + body[i], i + 1
    flush(buf)
    return fields


def animanga_videos(t):
    """Every {{Infobox animanga/Video}} on a page, as [(type, {field: value})].

    gwlib.wiki.infobox() reads {{Infobox film}} / {{Infobox television}};
    these pages use the animanga family and stack several — the Steins;Gate
    article carries the television series and the ONA shorts in the same
    infobox column, and only one of them is this list's."""
    out = []
    for m in re.finditer(r"\{\{Infobox animanga/Video", t):
        fields = infobox_fields(brace_block(t, m.start()))
        out.append((fields.get("type", "").lower(), fields))
    return out


def only_video(t, want, page):
    """The one animanga video infobox of a given type on a page."""
    hits = [f for kind, f in animanga_videos(t) if kind == want]
    assert len(hits) == 1, \
        "%s carries %d %r infoboxes, expected one" % (page, len(hits), want)
    return hits[0]


def table_slice(t, page, start="==Episodes==", stop=None):
    """The article's main episode table, cut at its own headings."""
    i = t.find(start)
    assert i >= 0, "%s no longer has a %r heading" % (page, start)
    j = t.find(stop, i) if stop else -1
    if stop:
        assert j > i, "%s no longer has the %r heading after %r — the " \
                      "sections this generator slices on have moved" \
                      % (page, stop, start)
    return t[i:j] if j > i else t[i:]


def parsed(seg, page):
    """[(raw_number, title, (y,m,d))] for one episode table, numbers raw."""
    raw = wiki.episodes(seg)
    assert raw, "%s parsed empty" % page
    out = []
    for _o, _s, title, _y, block in raw:
        assert not raw_field(block, "Runtime"), \
            "%s documents a per-episode runtime now — revisit weights, " \
            "because the only reason this list is unweighted is that no " \
            "episode had one" % page
        num = raw_field(block, "EpisodeNumber")
        assert num and title, "%s row incomplete: %r" % (page, (num, title))
        out.append((num, title, date_in(raw_field(block, "OriginalAirDate"))))
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
            assert hexv not in pair, "%s already uses %s" % (f.stem, hexv)


def read_sg():
    """The 2011 run: (episodes 1..24, the OVA, episode 23β).

    All three come out of one table on the source; which is which is decided
    by the raw EpisodeNumber string, never by a parsed integer."""
    t = text(SG_LIST)
    rows = parsed(table_slice(t, SG_LIST, stop=ONA_HEADING), SG_LIST)

    numbered = [r for r in rows if re.fullmatch(r"\d+", r[0])]
    ova = [r for r in rows if r[0] == "%d (OVA)" % (SG_EPISODES + 1)]
    beta = [r for r in rows if r[0] == "23β"]
    assert len(numbered) + len(ova) + len(beta) == len(rows), \
        "the table holds entries this generator cannot classify: %r" \
        % [r[0] for r in rows
           if r not in numbered and r not in ova and r not in beta]
    assert [int(r[0]) for r in numbered] == list(range(1, SG_EPISODES + 1)), \
        "the 2011 run's numbering is not 1..%d: %r" \
        % (SG_EPISODES, [r[0] for r in numbered])
    assert len(ova) == 1, "expected one OVA row, got %d" % len(ova)
    assert len(beta) == 1, \
        "expected exactly one 23β row, got %d — that episode is why this " \
        "list has a section between the film and Steins;Gate 0" % len(beta)

    dates = [d for _, _, d in numbered]
    assert dates == sorted(dates), "the 2011 run's air dates are out of order"
    assert ova[0][2] > dates[-1] and beta[0][2] > ova[0][2], \
        "the OVA and 23β are no longer the last two entries by date"

    # the four IBM shorts must still be parked in their own section — the
    # notes name them as deliberately absent, and a note that names a thing
    # the source has since moved is worse than no note
    assert ONA_HEADING in t, \
        "the IBM promotional shorts' heading has gone — if those four have " \
        "moved into the main table they would be listed by accident"
    head = t[t.find(ONA_HEADING):]
    shorts = wiki.episodes(head)
    assert len(shorts) == 4, \
        "the promotional-shorts section holds %d entries, not four" \
        % len(shorts)
    year = re.match(r"[^\n]*\((\d{4}) ONA\)", head)
    assert year, "the shorts' heading no longer dates them"
    shorts_year = int(year.group(1))

    ib = only_video(text(SG_PAGE), "tv series", SG_PAGE)
    assert not ib.get("runtime"), \
        "the 2011 series now documents a running time — revisit weights"
    assert re.match(r"^%d\{\{efn\|" % SG_EPISODES, ib.get("episodes", "")), \
        "the series infobox says %r episodes, expected %d plus a footnote" \
        % (ib.get("episodes"), SG_EPISODES)
    note = re.search(r"\{\{efn\|([^{}]+)\}\}", ib["episodes"]).group(1)
    assert note.strip() == ('Twenty-four episodes, plus an alternative '
                            'version of episode 23 titled "23β", plus one '
                            'OVA.'), \
        "the infobox footnote that counts 23β separately now reads %r" % note
    assert plain_date(ib.get("first", "")) == dates[0], \
        "the infobox opens %r, episode 1 aired %s" % (ib.get("first"), dates[0])
    assert plain_date(ib.get("last", "")) == dates[-1], \
        "the infobox closes %r, episode %d aired %s" \
        % (ib.get("last"), SG_EPISODES, dates[-1])
    return numbered, ova[0], beta[0], shorts_year


def read_sg0():
    """Steins;Gate 0: (episodes 1..23, the bonus episode)."""
    t = text(SG0_LIST)
    rows = parsed(table_slice(t, SG0_LIST, stop="\n==Notes=="), SG0_LIST)

    numbered = [r for r in rows if re.fullmatch(r"\d+", r[0])]
    ova = [r for r in rows if r[0] == "OVA"]
    assert len(numbered) + len(ova) == len(rows), \
        "unclassifiable entries: %r" % [r[0] for r in rows
                                        if r not in numbered and r not in ova]
    assert [int(r[0]) for r in numbered] == list(range(1, SG0_EPISODES + 1)), \
        "Steins;Gate 0's numbering is not 1..%d: %r" \
        % (SG0_EPISODES, [r[0] for r in numbered])
    assert len(ova) == 1, "expected one bonus episode, got %d" % len(ova)
    dates = [d for _, _, d in numbered]
    assert dates == sorted(dates), "Steins;Gate 0's air dates are out of order"
    assert ova[0][2] > dates[-1], "the bonus episode predates the finale"

    ib = only_video(text(SG0_PAGE), "tv series", SG0_PAGE)
    assert not ib.get("runtime"), \
        "Steins;Gate 0 now documents a running time — revisit weights"
    assert ib.get("episodes", "").strip() == "%d + OVA" % SG0_EPISODES, \
        "the infobox says %r episodes, expected '%d + OVA'" \
        % (ib.get("episodes"), SG0_EPISODES)
    assert plain_date(ib.get("first", "")) == dates[0], \
        "the infobox opens %r, episode 1 aired %s" % (ib.get("first"), dates[0])
    assert plain_date(ib.get("last", "")) == dates[-1], \
        "the infobox closes %r, episode %d aired %s" \
        % (ib.get("last"), SG0_EPISODES, dates[-1])
    return numbered, ova[0]


def read_film(franchise_text):
    """(title, release date, minutes) plus the two placement statements."""
    t = text(FILM_PAGE)
    ib = only_video(t, "film", FILM_PAGE)

    lead = re.search(r"\{\{nihongo\|'''''([^'|]+)'''''", t, re.I)
    assert lead, "the film article's lead no longer states its title"
    title = lead.group(1).strip()
    assert "Load Region of D" in title, "the film is titled %r" % title

    released = plain_date(ib.get("released", ""))
    rt = re.search(r"(\d+) minutes", ib.get("runtime", ""))
    assert rt, "no runtime on the film's infobox"
    mins = int(rt.group(1))
    assert 60 <= mins <= 180, "film runtime %d looks wrong" % mins

    # where it sits: the film article's own words, and the franchise
    # article's, asserted separately so one being reworded is caught
    where = re.search(r"The film takes place in August (\d{4}), one year "
                      r"after \[\[Steins;Gate \(TV series\)\|the events of "
                      r"the anime series\]\]\.", strip_refs(t))
    assert where, "the film article no longer says when it is set relative " \
                  "to the series — that sentence is why it sits after the " \
                  "2011 run on this list"
    follows = re.search(r"It is a follow-up to the 2011 \[\[[Aa]nime\]\] "
                        r"television series", strip_refs(t))
    assert follows, "the film article no longer calls itself a follow-up to " \
                    "the television series"
    fr = re.search(r"The movie, featuring an original storyline taking place "
                   r"after the events of the series, was released in Japanese "
                   r"theaters on (\w+ \d{1,2}, \d{4})", strip_refs(franchise_text))
    assert fr, "the franchise article no longer places the film after the " \
               "series"
    assert plain_date(fr.group(1)) == released, \
        "the franchise article dates the film %r, its infobox says %s" \
        % (fr.group(1), released)
    return title, released, mins


def read_placement(franchise_text):
    """The two sentences that place Steins;Gate 0 and episode 23β."""
    fork = re.search(r"As a sequel to the ''\[\[Steins;Gate\]\]'' visual "
                     r"novel game, and the \[\[Steins;Gate \(TV series\)\|"
                     r"2011 anime adaptation\]\], this series takes place in "
                     r"an \[\[Alternate history\|alternate future\]\] "
                     r"timeline that forks off from the original series' "
                     r"ending\.", strip_refs(text(SG0_LIST)))
    assert fork, "the Steins;Gate 0 episode list no longer says where that " \
                 "series sits relative to the 2011 run — that sentence is " \
                 "the ordering decision on this list"
    sequel = re.search(r"It serves as a sequel to ''\[\[Steins;Gate\]\]'' and "
                       r"the \[\[Steins;Gate \(TV series\)\|2011 anime "
                       r"adaptation\]\]\.", strip_refs(text(SG0_PAGE)))
    assert sequel, "the Steins;Gate 0 article no longer calls itself a sequel"

    beta = re.search(r"an alternate version of episode 23 of the first season "
                     r"aired on (\w+ \d{1,2}, \d{4}), as part of a rebroadcast "
                     r"of the series, depicting an alternate ending which "
                     r"leads into the events of ''Steins;Gate 0''\.",
                     strip_refs(franchise_text))
    assert beta, "the franchise article no longer says what episode 23β is " \
                 "for — this list moves it out of release order on the " \
                 "strength of that sentence and must not do so silently"
    return plain_date(beta.group(1))


def read_excluded_games(franchise_text):
    """The two visual novels the anime adapts, dated from the source, so the
    exclusion note names them with real release dates rather than memory."""
    def first_release(t, page):
        m = re.search(r"\|\s*released\s*=\s*\{\{[Cc]ollapsible list\|title="
                      r"\{\{nobold\|([^}]+)\}\}", t)
        assert m, "%s gives no headline release date" % page
        return plain_date(m.group(1))

    sg = first_release(franchise_text, FRANCHISE_PAGE)
    sg0 = first_release(text("Steins;Gate 0"), "Steins;Gate 0")
    assert sg[0] == 2009 and sg0[0] == 2015, \
        "the visual novels are dated %s and %s" % (sg, sg0)
    return sg, sg0


def main():
    franchise_text = text(FRANCHISE_PAGE)
    check_accent()

    sg, sg_ova, beta, shorts_year = read_sg()
    sg0, sg0_ova = read_sg0()
    film_title, film_date, film_mins = read_film(franchise_text)
    beta_date = read_placement(franchise_text)
    vn_sg, vn_sg0 = read_excluded_games(franchise_text)

    assert beta[2] == beta_date, \
        "the episode table dates 23β %s, the franchise article says %s" \
        % (beta[2], beta_date)

    # the running order this list uses, asserted to be both story order (the
    # sentences read above) and release order (these dates)
    assert sg[-1][2] < film_date < beta[2] < sg0[0][2], \
        "the 2011 finale, the film, 23β and Steins;Gate 0 are no longer in " \
        "that order by date: %s, %s, %s, %s" \
        % (sg[-1][2], film_date, beta[2], sg0[0][2])

    sections = [{
        "id": "sg",
        "title": "Steins;Gate",
        "sub": prop.join_bits("2011–12", "%d episodes and an OVA"
                              % SG_EPISODES),
        "intro": "The 2011 run, and the whole of it. The twenty-fifth entry "
                 "was released with the final Blu-ray volume rather than "
                 "broadcast.",
        "open": True,
        "items": [{"id": "sg-e%s" % n, "t": t, "n": n} for n, t, _d in sg]
        + [{"id": "sg-ova", "t": sg_ova[1], "n": str(SG_EPISODES + 1),
            "note": "Original video animation, released with the final "
                    "Blu-ray volume"}],
    }, {
        "id": "film",
        "title": "Load Region of Déjà Vu",
        "sub": prop.join_bits(str(film_date[0]), "the film",
                              "%d minutes" % film_mins),
        "intro": "The film, and the source is exact about where it goes: it "
                 "is set one year after the events of the series.",
        "items": [{
            "id": "sg-film-%s" % prop.slug("Load Region of Deja Vu"),
            "t": film_title,
            "n": str(film_date[0]),
            "note": prop.join_bits("Feature film", "%d minutes" % film_mins,
                                   "released %s" % fmt_date(film_date)),
        }],
    }, {
        "id": "bridge",
        "title": "Episode 23β",
        "sub": prop.join_bits(str(beta[2][0]), "an alternate episode 23"),
        "intro": "An alternate version of episode 23, aired during a 2015 "
                 "rebroadcast. The source says it leads into Steins;Gate 0, "
                 "so it sits here rather than at the end of the 2011 run "
                 "where release order would put it.",
        "items": [{
            "id": "sg-23b", "t": beta[1], "n": beta[0],
            "note": prop.join_bits("Alternate version of episode 23",
                                   "the way in to Steins;Gate 0"),
        }],
    }, {
        "id": "sg0",
        "title": "Steins;Gate 0",
        "sub": prop.join_bits("2018", "%d episodes and an OVA" % SG0_EPISODES),
        "intro": "The 2018 sequel series, which the source places in a "
                 "timeline forking off the original run's ending.",
        "items": [{"id": "sg0-e%s" % n, "t": t, "n": n} for n, t, _d in sg0]
        + [{"id": "sg0-ova", "t": sg0_ova[1], "n": "OVA",
            "note": "Bonus episode, released after the finale"}],
    }]

    assert [s["id"] for s in sections] == ["sg", "film", "bridge", "sg0"], \
        [s["id"] for s in sections]
    total = sum(len(s["items"]) for s in sections)
    assert total == LISTED, "%d rows, expected %d" % (total, LISTED)
    assert sum(1 for s in sections for x in s["items"] if "w" in x) == 0, \
        "a weight crept in — this list is unweighted end to end"
    # a year in an episode note would make that row a cross-list sync
    # candidate keyed on title+year; only the film row may carry one
    for s in sections:
        for x in s["items"]:
            if x["id"].startswith("sg-film"):
                continue
            assert not re.search(r"\b(18|19|20)\d{2}\b", x.get("note") or ""), \
                "episode row %s names a year in its note" % x["id"]

    p = {
        "slug": SLUG,
        "title": "Steins;Gate",
        "subtitle": "the 2011 series, the film, and Steins;Gate 0",
        "kind": "anime & films",
        "popularity": 70,
        "year": "2011–2018",
        "blurb": "White Fox's time-travel run in full — both television "
                 "series, the film between them, and the alternate episode "
                 "that leads from one into the other.",
        "unit": {"one": "entry", "many": "entries"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": ACCENT,
        "accentDark": ACCENT_DARK,
        "tiers": False,
        "notes": [
            ["Release order and story order agree, and this list is in both.",
             "It did not have to be that way, so it is worth saying which "
             "order this is. The source places the film \"in August 2011, one "
             "year after the events of the anime series\", and places "
             "Steins;Gate 0 in \"an alternate future timeline that forks off "
             "from the original series' ending\". Both follow the 2011 run, "
             "and both came out in that order — series, film, 0 — so nothing "
             "had to be re-sequenced."],
            ["Episode 23β sits before Steins;Gate 0, not at the end of the "
             "2011 run.",
             "It is an alternate version of episode 23 that aired during a "
             "rebroadcast on %s, and the source says it depicts \"an "
             "alternate ending which leads into the events of Steins;Gate "
             "0\". That is the one place this list departs from the order of "
             "the source's own table, which lists it last by air date. It is "
             "a row of its own rather than a replacement for episode 23, "
             "because it is a different episode with a different title and "
             "its own air date — the series infobox counts it separately "
             "from the twenty-four." % fmt_date(beta[2])],
            ["Both OVAs are here.",
             "The 2011 run's twenty-fifth entry went out with the final "
             "Blu-ray volume rather than on television, and Steins;Gate 0 "
             "closes with a bonus episode released after its finale. The "
             "source's episode tables carry both, so this list does too."],
            ["The visual novels and the games are not here.",
             "This is the anime. The Steins;Gate visual novel the first "
             "series adapts (%s) and the Steins;Gate 0 visual novel the "
             "second one adapts (%s) are deliberately out of scope, as is the "
             "rest of the Science Adventure line — they are a different thing "
             "to sit down to, and mixing them in would make the count "
             "meaningless. The four IBM promotional shorts from %d are out "
             "for the same reason."
             % (fmt_date(vn_sg), fmt_date(vn_sg0), shorts_year)],
            ["Nothing is weighted, and hours are not tracked here.",
             "Wikipedia documents no running time for either series: neither "
             "television infobox has one and not one of the forty-nine "
             "episode blocks carries one. The film's %d minutes is the only "
             "length in the source, and one row out of fifty-one cannot "
             "weight a list — an unweighted row silently counts as a full "
             "hour, so forty-nine half-hour episodes would read as "
             "forty-nine hours. Every row counts one, the film included, and "
             "its runtime is in the row note instead." % film_mins],
            ["The address has no semicolon.",
             "The list is Steins;Gate; the page is at ?p=steins-gate. A "
             "semicolon is a separator in a URL rather than a letter, and "
             "the slug is also the key every tick is stored against."],
            "Episode titles, air dates, the film's date and its runtime "
            "machine-read from Wikipedia's two Steins;Gate episode lists, "
            "both series articles, the film article and the franchise "
            "article; each series' numbering is asserted contiguous and its "
            "first and last air dates asserted against its own infobox "
            "before this builds.",
        ],
        "sections": sections,
    }

    out = prop.write(p)
    print("wrote %s — %d rows in %d sections" % (out.name, total,
                                                 len(sections)))
    for s in sections:
        print("   %-24s %3d  %s" % (s["title"], len(s["items"]), s["sub"]))
    print("   order: source placement == release order (series, film, 23β, 0)")
    print("   weighted: no (no episode runtime in the source)")


if __name__ == "__main__":
    main()
