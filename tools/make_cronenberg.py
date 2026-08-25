#!/usr/bin/env python3
"""Generate properties/cronenberg.json.

    PYTHONIOENCODING=utf-8 python tools/make_cronenberg.py

David Cronenberg's directed features, in release order, in the four eras
Wikipedia's own article divides his career into. Everything on the card —
titles, years, runtimes — is machine-read from wikitext cached in
scratch/cronenberg/: the "David Cronenberg filmography" article for the roster,
the "David Cronenberg" article for the era boundaries, and each film's own
article for its release date and its runtime. Nothing is typed in from memory,
and every number is asserted against the source that produced it before
anything is written.

THE FILMOGRAPHY, NOT A BODY-HORROR CANON
----------------------------------------
The commission offered two lists: this one, or a broad body-horror canon with
Cronenberg at its centre. This one, because a body-horror canon would be mostly
Cronenberg — the filmography article calls him "a principal originator of the
genre" in its first sentence — and a canon assembled before the filmography
exists would be a Cronenberg list with other people's films scattered through
it and no way to tick off his own run. Built in this order, the canon is a
better list later: it can lean on this page for the spine and spend its rows on
everyone else.

THE ROSTER RULE: THE FILM TABLE, DIRECTOR = YES
-----------------------------------------------
Every row of the filmography's ===Film=== table, all of which are marked
{{yes}} under Director. That is 23 films, from *Stereo* (1969) to *The Shrouds*
(2024), and it includes the two silent art-house features he made before
*Shivers* because the article files them with the features rather than with the
shorts.

TELEVISION IS OUT, AND THIS FILE SAYS SO OUT LOUD
-------------------------------------------------
He directed television, and none of it is here. The filmography's ==Television==
section holds two tables: nine CBC documentary *shorts* from 1971–72, which the
table's own Notes column marks "Documentary short", and episodes of five series
that belong to other people — *Program X*, *Peep Show*, *Teleplay*, *Friday the
13th: The Series* and *Scales of Justice*. This is a filmography of his
features, and an episode of somebody else's anthology is not one. The same
question came up on the Matt Johnson list, where a Director=Yes rule reached a
stand-up special he had only pointed cameras at, and it was answered the same
way. main() asserts both tables are still where this reasoning found them, so
the exclusion cannot outlive its reason: if Wikipedia ever moves a directed
*feature* into them, the build fails instead of quietly shipping short.

Out on the same grounds: the seven short films (===Short films===), the seven
commercials, and every acting role — he is in a lot of other directors' films
and in three of his own, and none of that is directing.

THE ERAS ARE THE ARTICLE'S, NOT THIS FILE'S
-------------------------------------------
The four sections come from the four ===Career=== headings on the "David
Cronenberg" article — "1969–1979: Film debut and early work", "1981–1988:
Breakthrough and acclaim", "1991–2002: Career fluctuations" and "2005–present:
Resurgence". main() reads those headings out of the wikitext, parses the year
ranges out of them, and builds the sections from the parsed ranges; the
headings are asserted present first, so a rewrite upstream breaks the build
rather than leaving four hand-chosen boundaries pretending to be sourced. Every
film must land in exactly one era, and that is asserted too.

WEIGHTS: ALL OF THEM, FROM EACH FILM'S OWN INFOBOX
--------------------------------------------------
The page resolves `WEIGHT = x.w >= 0 ? x.w : 1`, so one unweighted row on a
weighted list silently books itself as one hour and the total comes out
confidently wrong. So every row carries `w`, in hours, from the `runtime` field
of that film's own {{Infobox film}} — never from the filmography table, which
publishes no runtimes, and never estimated. minutes() refuses a field that does
not yield a single whole-minute figure, and main() asserts that the number of
weights equals the number of rows before it writes anything.

RELEASED FILMS ONLY
-------------------
Release dates come from each film's own infobox `released` field, are asserted
to agree with the filmography table's Year column, and are asserted to be on or
before the day this runs. He has no announced next feature on either article;
main() asserts the Film table's last row is the one this list ends on, so a
newly added row cannot go missing.

THE BLURB CARRIES NO FILM COUNT (CLU-190). The hours in it are computed from
the weights that ship, so it cannot drift from the card.
"""
import datetime
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop, wiki  # noqa: E402

SLUG = "cronenberg"
CACHE = prop.ROOT / "scratch" / SLUG
FILMOG = "David Cronenberg filmography"
BIO = "David Cronenberg"

# The four career headings the biography divides itself with. The sections take
# their boundaries from the years inside these strings, parsed, not chosen.
ERA_HEADINGS = [
    "1969–1979: Film debut and early work",
    "1981–1988: Breakthrough and acclaim",
    "1991–2002: Career fluctuations",
    "2005–present: Resurgence",
]

# Section titles and intros, one per heading above, in the same order. The
# boundaries are the article's; only the words are ours.
ERA_COPY = [
    ("early", "The early Canadian films",
     "Two art-house features shot around Toronto without synchronised sound, "
     "then a partnership with Ivan Reitman and a decade of Canadian "
     "government financing. The body-horror pictures that made his name are "
     "here, and so is the drag-racing film he made in the middle of them "
     "because he liked cars."),
    ("breakthrough", "Breakthrough and acclaim",
     "Five films in eight years, the run that took him from cult director to "
     "one studios would hand a remake to. Howard Shore scored all but one of "
     "them, and from the last of them on, Peter Suschitzky has shot every "
     "film he has made."),
    ("fluctuations", "Naked Lunch to Spider",
     "The stretch of adaptations nobody thought could be adapted — Burroughs, "
     "Hwang's play, Ballard — with an original of his own in the middle of "
     "it. Two of the five were shot outside Ontario, which for him is "
     "unusual."),
    ("resurgence", "The resurgence",
     "Bigger budgets, mostly other people's scripts, and four films with "
     "Viggo Mortensen. Twenty years wide, with an eight-year gap in the "
     "middle of it during which he published a novel and was reported to be "
     "considering retirement, and two late films back in Cannes "
     "competition."),
]

# Per-film row notes: production context only, nothing about what happens in
# the film — several of these are famous for one image, and none of that is
# here. Every one is grounded in the cached articles. Keyed by (year, title),
# because he made two films called Crimes of the Future and a title-keyed dict
# silently gave both of them the same note.
NOTES = {
    (1969, "Stereo"):
        "Shot in black and white without synchronised sound, on the "
        "University of Toronto's Scarborough campus — he directed, wrote, "
        "shot, cut and produced it",
    (1970, "Crimes of the Future"):
        "The second art-house feature, in colour and again a one-man crew; it "
        "shares a title with the 2022 film and nothing else",
    (1975, "Shivers"):
        "His first commercial feature, part-financed by the taxpayer-funded "
        "CFDC — which is how it ended up debated in Parliament",
    (1977, "Rabid"):
        "Marilyn Chambers took the lead after Sissy Spacek, his first choice, "
        "did not; the film that won him international distributors",
    (1979, "Fast Company"):
        "A drag-racing picture made between Rabid and The Brood, out of his "
        "own interest in cars and bike gangs",
    (1979, "The Brood"):
        "The first of his films scored by Howard Shore, who has scored every "
        "one since bar The Dead Zone",
    (1981, "Scanners"):
        "He started shooting without a finished script, writing that day's "
        "scenes in the mornings; he calls it his hardest film to make",
    (1983, "Videodrome"):
        "Universal put up half the budget and distributed it, on the strength "
        "of a one-page description",
    (1983, "The Dead Zone"):
        "From Stephen King's 1979 novel, and the one film since 1979 Howard "
        "Shore did not score — Michael Kamen did",
    (1986, "The Fly"):
        "A remake of Kurt Neumann's 1958 film and his biggest hit at $60 "
        "million; he directed Shore's opera of it in 2008",
    (1988, "Dead Ringers"):
        "The start of the run with cinematographer Peter Suschitzky, who has "
        "shot every film he has made since",
    (1991, "Naked Lunch"):
        "Partly from William S. Burroughs' 1959 novel, long called "
        "unfilmable, and partly from Burroughs' own life",
    (1993, "M. Butterfly"):
        "David Henry Hwang adapted his own 1988 play, and most of it was shot "
        "in China — for Cronenberg, unusually far from Ontario",
    (1996, "Crash"):
        "From J. G. Ballard's 1973 novel; the Cannes jury made a Special Jury "
        "Prize for it, for originality and daring",
    (1999, "eXistenZ"):
        "The one original screenplay in this stretch — the four films around "
        "it are all adaptations",
    (2002, "Spider"):
        "From Patrick McGrath's novel, shot in England on a small budget with "
        "part of his own fee deferred",
    (2005, "A History of Violence"):
        "One of his largest budgets, and the first of four films with Viggo "
        "Mortensen",
    (2007, "Eastern Promises"):
        "Filmed mostly in England, and his second with Mortensen",
    (2011, "A Dangerous Method"):
        "From Christopher Hampton's play The Talking Cure, shot in Germany "
        "and Austria",
    (2012, "Cosmopolis"):
        "From Don DeLillo's 2003 novel, and in competition at Cannes",
    (2014, "Maps to the Stars"):
        "The first film he shot in the United States, after four decades of "
        "working at home",
    (2022, "Crimes of the Future"):
        "Shot in Greece after an eight-year gap, and unrelated to the 1970 "
        "film of the same name",
    (2024, "The Shrouds"):
        "Premiered in Cannes competition and reached cinemas that September",
}

# The films this list ends on and begins with, pinned by name. If the Film
# table grows a row past The Shrouds, the assertion below fails rather than the
# new film going quietly missing.
FIRST, LAST = "Stereo", "The Shrouds"

# Italicised wikilinks in the biography's lead that are not films. The lead
# cross-check refuses anything else it does not ship.
LEAD_NOT_FILMS = {"The Village Voice": "a newspaper, not a film"}

_CELL = re.compile(r"^[|!]\s*(?:([^|\[{]*=[^|\[{]*)\|)?\s*(.*)$", re.S)


def table_after(text, heading):
    """The first wikitable following a `==heading==` line."""
    m = re.search(r"^=+\s*%s\s*=+\s*$" % re.escape(heading), text, re.M)
    assert m, "no %r section on the article" % heading
    a = text.index("\n{|", m.end())
    return text[a:text.index("\n|}", a)]


def table_rows(seg, ncols):
    """Cells per row, with rowspan carried down.

    The Film table's Year cell is a `!scope="row"` header, and it rowspans over
    the two-film years (1979 and 1983). Picking cells positionally without
    carrying the span hands The Brood and The Dead Zone the wrong year or none
    at all, which is the bug this parser exists to avoid.
    """
    out, pending = [], {}
    for chunk in seg.split("\n|-"):
        cells = [l.strip() for l in chunk.split("\n")
                 if l.strip()[:1] in ("|", "!")]
        # the two column-definition rows: a leading `!` cell that is not a row
        # header. Skipped before parsing so their rowspans never enter pending.
        if not cells or (cells[0].startswith("!")
                         and 'scope="row"' not in cells[0]):
            continue
        raw = iter(cells)
        cols = []
        for c in range(ncols):
            if c in pending:
                cols.append(pending[c][1])
                pending[c][0] -= 1
                if pending[c][0] == 0:
                    del pending[c]
                continue
            m = _CELL.match(next(raw, "|"))
            attrs, content = m.group(1) or "", m.group(2)
            cols.append(content)
            sp = re.search(r'rowspan="?(\d+)', attrs)
            if sp and int(sp.group(1)) > 1:
                pending[c] = [int(sp.group(1)) - 1, content]
        out.append(cols)
    return out


def yes(cell):
    """True only for a bare {{yes}}."""
    return bool(re.fullmatch(r"\{\{\s*[Yy]es\s*\}\}", cell.strip()))


def link(cell):
    """The wikilink target inside an italicised title cell."""
    m = re.search(r"\[\[([^\]|]+)", cell)
    return m.group(1).strip() if m else None


def key(target):
    """A page title normalised for comparison: disambiguator dropped, folded."""
    return prop.normt(re.sub(r"\s*\([^)]*\)\s*$", "", target or ""))


def minutes(field, what):
    """A single whole-minute runtime out of an infobox `runtime` field.

    A range, a blank, or two figures fails: this list weights every row, and an
    estimate wearing a citation is worse than a build that stops.
    """
    v = wiki.clean(field or "")
    m = re.match(r"^(\d{1,3})\s*minutes?\b", v.strip())
    assert m, "%s does not publish a single runtime: %r" % (what, v)
    n = int(m.group(1))
    assert 50 <= n <= 240, "%s: implausible runtime %d" % (what, n)
    return n


def released(field, what):
    """(year, earliest date or None) from an infobox `released` field.

    A {{Film date}} usually carries year|month|day|festival-or-country, often
    several times over; the earliest of those is the release this list means.
    *Crimes of the Future* (1970) publishes `{{Film date|1970}}` — a year and
    nothing else — so the year is returned on its own rather than a day being
    invented for it, and main() checks such a film against the calendar year.
    """
    dates, years = [], []
    for m in re.finditer(r"\{\{\s*[Ff]ilm date\s*\|(.*?)\}\}", field or "", re.S):
        body = m.group(1)
        for d in re.finditer(r"(?<!\d)((?:19|20)\d{2})\s*\|\s*(\d{1,2})"
                             r"\s*\|\s*(\d{1,2})(?!\d)", body):
            try:
                dates.append(datetime.date(*(int(g) for g in d.groups())))
            except ValueError:
                pass
        years += [int(y) for y in re.findall(r"(?<!\d)((?:19|20)\d{2})(?!\d)",
                                             body)]
    assert years, \
        "%s: no release date on the infobox: %r" % (what, (field or "")[:120])
    return (min(d.year for d in dates) if dates else min(years),
            min(dates) if dates else None)


def main():
    today = datetime.date.today()
    art = wiki.wikitext(FILMOG, cache_dir=CACHE)
    bio = wiki.wikitext(BIO, cache_dir=CACHE)
    assert art and bio, "no cached wikitext"

    # ---- the eras are the biography's own headings ------------------------
    eras = []
    for h in ERA_HEADINGS:
        assert re.search(r"^=+\s*%s\s*=+\s*$" % re.escape(h), bio, re.M), \
            ("the career heading %r is gone from %s — the sections take their "
             "boundaries from it and must be re-derived" % (h, BIO))
        m = re.match(r"(\d{4})–(\d{4}|present)", h)
        assert m, h
        eras.append((int(m.group(1)),
                     today.year if m.group(2) == "present" else int(m.group(2))))
    assert len(eras) == len(ERA_COPY) == 4, eras
    assert [e[0] for e in eras] == sorted(e[0] for e in eras), eras

    # ---- the roster: the Film table, Director = Yes -----------------------
    rows = table_rows(table_after(art, "Film"), 9)
    films = []
    for year, title, d, w, p, ed, ph, note, _ref in rows:
        assert yes(d), "%r is not marked directed" % wiki.clean(title)
        films.append({"t": wiki.clean(title), "page": link(title),
                      "year": int(wiki.clean(year)),
                      "wrote": yes(w), "note": wiki.clean(note)})
    assert len(films) == 23, [f["t"] for f in films]
    assert [f["year"] for f in films] == sorted(f["year"] for f in films), \
        "the filmography table is out of release order"
    assert films[0]["t"] == FIRST and films[-1]["t"] == LAST, \
        ("the Film table now runs %s to %s — a film has been added or removed "
         "and this list must be re-checked" % (films[0]["t"], films[-1]["t"]))
    assert all(f["page"] for f in films), \
        [f["t"] for f in films if not f["page"]]

    # ---- each film's own article: title, release date, runtime ------------
    for f in films:
        page = wiki.wikitext(f["page"], cache_dir=CACHE)
        assert page, "no cached article for %s" % f["page"]
        ib = wiki.infobox(page, kind="film")
        assert ib, "no film infobox on %s" % f["page"]
        # The film's own infobox name, not the filmography's link text: the
        # table links [[Existenz]] and the film is called eXistenZ.
        name = wiki.clean(ib("name")) or f["t"]
        assert prop.normt(name) == prop.normt(f["t"]), \
            "%s calls itself %r" % (f["t"], name)
        f["t"] = name
        f["runtime"] = minutes(ib("runtime"), f["t"])
        ryear, rdate = released(ib("released"), f["t"])
        f["released"] = rdate or ryear
        assert ryear == f["year"], \
            "%s: the filmography says %d, its own article's first release is %s" \
            % (f["t"], f["year"], ryear)
        if rdate:
            assert rdate <= today, \
                "%s is dated %s and has not come out" % (f["t"], rdate)
        else:
            # no day published: a film can only be assumed out if its whole
            # release year is behind us
            assert ryear < today.year, \
                "%s publishes only the year %d and it is not over" \
                % (f["t"], ryear)
    # every row weighted, from a real infobox figure — the all-or-nothing rule
    assert all(isinstance(f["runtime"], int) for f in films), \
        [f["t"] for f in films if not isinstance(f["runtime"], int)]
    # the table's order is the release order, checked to the day where the day
    # is published: 1979 and 1983 each hold two films and the table's order for
    # them has to be the real one
    order = [f["released"] if isinstance(f["released"], datetime.date)
             else datetime.date(f["released"], 1, 1) for f in films]
    assert order == sorted(order), \
        "the Film table's order is not release order: %s" % order
    # one note per film, keyed the way two Crimes of the Future demand
    assert set(NOTES) == {(f["year"], f["t"]) for f in films}, \
        sorted(set(NOTES) ^ {(f["year"], f["t"]) for f in films})
    # two claims the section intros make, checked against the columns that
    # could falsify them: the eighties run ends in a studio remake, and the
    # late films are mostly other people's screenplays
    fly = next(f for f in films if f["t"] == "The Fly")
    assert fly["note"].startswith("Remake of"), fly["note"]
    late = [f for f in films if f["year"] >= eras[-1][0]]
    assert sum(not f["wrote"] for f in late) > len(late) / 2.0, \
        [f["t"] for f in late if f["wrote"]]

    # ---- the lead cross-check: nothing either lead names may go missing ----
    shipped = {key(f["page"]) for f in films} | {key(f["t"]) for f in films}
    for src, text in ((FILMOG, art), (BIO, bio)):
        lead = text[:text.index("\n==")]
        named = set(re.findall(r"''\[\[([^\]|]+)", lead))
        loose = {n for n in named
                 if key(n) not in shipped and n not in LEAD_NOT_FILMS}
        assert not loose, \
            ("the lead of %s names %s and this list neither ships nor "
             "excludes it" % (src, sorted(loose)))

    # ---- television: named, checked, and deliberately not shipped ---------
    tvfilms = table_rows(table_after(art, "TV films"), 9)
    tvseries = table_rows(table_after(art, "TV series"), 6)
    assert len(tvfilms) == 9, len(tvfilms)
    assert all("Documentary short" in wiki.clean(r[7]) for r in tvfilms), \
        ("a row in the TV films table is no longer a documentary short — if a "
         "directed feature has appeared there, this list must reconsider")
    assert all(int(wiki.clean(r[0])) in (1971, 1972) for r in tvfilms), \
        [wiki.clean(r[0]) for r in tvfilms]
    series = [wiki.clean(r[1]) for r in tvseries]
    assert series == ["Program X", "Peep Show", "Teleplay",
                      "Friday the 13th: The Series", "Scales of Justice"], series
    assert all(yes(r[2]) for r in tvseries), series
    # every one of them is episodes of somebody else's programme, which is the
    # ground the ruling stands on
    assert all(re.search(r'"[^"]+"', wiki.clean(r[4])) for r in tvseries), \
        [wiki.clean(r[4]) for r in tvseries]
    shorts = table_rows(table_after(art, "Short films"), 7)
    assert len(shorts) == 7, len(shorts)

    # ---- sections ---------------------------------------------------------
    sections, seen = [], set()
    for (lo, hi), (sid, title, intro) in zip(eras, ERA_COPY):
        got = [f for f in films if lo <= f["year"] <= hi]
        assert got, title
        seen.update(id(f) for f in got)
        mins = sum(f["runtime"] for f in got)
        items = []
        for f in got:
            it = {"id": "dc-%d-%s" % (f["year"], prop.slug(f["t"])),
                  "t": f["t"], "n": str(f["year"]),
                  "w": round(f["runtime"] / 60.0, 2),
                  "note": NOTES[(f["year"], f["t"])]}
            items.append(it)
        sections.append({
            "id": sid, "title": title,
            "sub": "%d–%d · %d films · %d hours"
                   % (got[0]["year"], got[-1]["year"], len(got),
                      round(mins / 60.0)),
            "intro": intro,
            "items": items,
        })
    sections[0]["open"] = True
    # exactly one era each, no film in two and none in none
    assert len(seen) == len(films), \
        [f["t"] for f in films if id(f) not in seen]

    items = [x for s in sections for x in s["items"]]
    assert len(items) == len(films) == 23, len(items)
    assert len({x["id"] for x in items}) == len(items), "duplicate ids"
    assert all("w" in x and x["w"] > 0 for x in items), \
        [x["id"] for x in items if not x.get("w")]
    ys = [x["n"] for x in items]
    assert ys == sorted(ys), "the card is out of release order"
    hours = sum(x["w"] for x in items)
    shortest = min(films, key=lambda f: f["runtime"])
    longest = max(films, key=lambda f: f["runtime"])

    # ---- the accent pair is nobody else's ---------------------------------
    accent, accent_dark = "#7B2D3A", "#E8929B"
    for f in sorted((prop.ROOT / "properties").glob("*.json")):
        if f.stem in (SLUG, "index", "search"):
            continue
        try:
            other = json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            continue
        if not isinstance(other, dict):
            continue
        assert (other.get("accent") or "").lower() != accent.lower(), \
            "%s already uses accent %s" % (f.name, accent)
        assert (other.get("accentDark") or "").lower() != accent_dark.lower(), \
            "%s already uses accentDark %s" % (f.name, accent_dark)

    p = {
        "slug": SLUG,
        "title": "David Cronenberg",
        "subtitle": "the directed features, in release order",
        "kind": "films",
        "popularity": 56,
        "year": "%d–%d" % (films[0]["year"], films[-1]["year"]),
        "blurb": "Every feature he directed, Stereo to The Shrouds — %d years "
                 "of flesh, machines and Canadian film money, about %d hours."
                 % (films[-1]["year"] - films[0]["year"], round(hours)),
        "unit": {"one": "film", "many": "films"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        # Light: the arterial red of an operating theatre. Dark: the washed
        # pink of skin under a surgical lamp. Checked above against every
        # accent already shipping in properties/.
        "accent": accent,
        "accentDark": accent_dark,
        "tiers": False,
        "notes": [
            ["The filmography, not a body-horror canon.",
             "This list was proposed two ways: his films, or a canon of the "
             "genre he is credited with originating. It is his films, because "
             "a body-horror canon would be mostly him anyway — better to have "
             "the filmography first and let the canon spend its rows on "
             "everyone else, with this page carrying the spine."],
            ["Features only. The television is not here.",
             "He directed for television and none of it is on this list. What "
             "that leaves out is nine documentary shorts he made for the CBC "
             "in 1971 and 1972, and single episodes or pairs of episodes of "
             "five series that belong to other people — Program X, Peep Show, "
             "Teleplay, Friday the 13th: The Series and Scales of Justice. An "
             "episode of somebody else's anthology is not a film of his. The "
             "seven short films are out on the same grounds, as are the "
             "commercials, and so is his long second career acting in other "
             "directors' pictures."],
            ["The four sections are Wikipedia's, not ours.",
             "His biography splits its Career section four ways — film debut "
             "and early work, breakthrough and acclaim, career fluctuations, "
             "resurgence — and this list takes those year ranges as its era "
             "boundaries rather than inventing its own. The generator reads "
             "the headings and fails if they change, so the divisions on this "
             "page cannot quietly stop matching the article they came from."],
            ["Bar widths are runtimes.",
             "Every row is weighted, in hours, from the runtime published in "
             "that film's own Wikipedia infobox — never from an average and "
             "never estimated. The shortest is %s (%d) at %d minutes and the "
             "longest %s (%d) at %d."
             % (shortest["t"], shortest["year"], shortest["runtime"],
                longest["t"], longest["year"], longest["runtime"])],
            "Roster from Wikipedia's David Cronenberg filmography, read from "
            "the Film table itself; era boundaries from the career headings on "
            "the David Cronenberg article; runtimes and release dates from each "
            "film's own article.",
        ],
        "sections": sections,
    }

    out = prop.write(p)
    print("wrote %s — %d rows, %.1f hours" % (out.name, len(items), hours))
    for s in sections:
        print("   %-28s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))
    for f in films:
        print("   %-24s %s  %3d min  (%s)"
              % (f["t"], f["year"], f["runtime"], f["released"]))


if __name__ == "__main__":
    main()
