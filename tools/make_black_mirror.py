#!/usr/bin/env python3
"""Generate properties/black-mirror.json — every Black Mirror, plus Bandersnatch.

    python tools/make_black_mirror.py

34 rows in broadcast order: the 33 numbered episodes across series 1-7, the
2014 special "White Christmas", and the 2018 interactive film *Bandersnatch*.
Sections are Wikipedia's own headings on "List of Black Mirror episodes" —
seven series plus the two one-offs, in the order the page lists them, which is
the order they were broadcast. Everything is machine-read from wikitext cached
under scratch/blackmirror/; re-running against the cache is byte-identical,
and deleting the cache refetches.

OWN PARSER, on purpose. gwlib.wiki.episodes() drops rows on this page (CLU-167)
in two ways that both matter here: it reads only |Title, so *Bandersnatch* —
which the page files under |RTitle, having no episode number — comes back with
an empty title and would have shipped as a blank row; and gwlib.clean() turns
the {{hsp}} hair space inside "USS ''Callister''{{hsp}}: Into Infinity" into
the literal text "hsp", so series 7's finale would have shipped as "USS
Callisterhsp: Into Infinity". The brace-counting reader below (blocks/fields)
takes each {{Episode list}} whole, splits its fields at depth zero only, and
reads RTitle when Title is absent. Nothing it produces is trusted on sight:
every section's row count, the contiguity of the overall numbering, and the
presence of a title, an air date and a weight on every row are all asserted
before anything is written.

COUNTS ARE ASSERTED AGAINST THE ENUMERATED ROWS. EXPECT below is the number of
{{Episode list}} blocks each heading must hold, and the overall numbering must
be the contiguous run 1-33 across the numbered rows. The {{Series overview}}
template at the top of the page is read too, but only as a secondary
cross-check that shouts if the summary and the tables disagree; the enumerated
rows are what the list is built from.

WEIGHTED, and every single row carries one. Black Mirror is the rare
television list where a runtime is published per episode: each episode has its
own Wikipedia article whose {{Infobox television episode}} gives |length, and
they run from 41 minutes ("Metalhead") to 90 ("USS Callister: Into Infinity")
— more than a factor of two, so counting episodes would have been a poor guide
to an evening. *Bandersnatch* is the one row with no fixed length: its article
gives "Variable", with a cited Default of 90 minutes and 312 minutes of footage
in total. It is weighted at that published 90-minute default path, and the
Bandersnatch section says so in as many words. Weighting 33 rows and leaving
that one bare was the alternative and is the worse bug: an unweighted row in a
weighted list silently counts as one hour (CLU-131), which would have been
wrong by half an hour with no way for a reader to tell. The assert below fails
the build if any row is missing a weight.

SPOILERS. Titles only. No row carries a note and no section intro describes an
episode, because this show is built on its turns and a one-line summary gives
several of them away — several titles are already as far as a list should go.
The {{Episode list}} ShortSummary fields are parsed past and dropped. The two
section intros that do exist describe format and availability, not plot.

ANTHOLOGY. Nothing connects the episodes and the list says so: random:true
puts the "Pick one for me" button on the page and the first note tells a
reader arriving at thirty-four unconnected stories that starting anywhere is
fine. The one exception — one episode that is a sequel to another — is named
in the notes without saying anything about either.
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop, wiki  # noqa: E402

SLUG = "black-mirror"
PAGE = "List of Black Mirror episodes"
CACHE = pathlib.Path(__file__).resolve().parent.parent / "scratch" / "blackmirror"
LIST_URL = "https://en.wikipedia.org/wiki/List_of_Black_Mirror_episodes"

# (section id, the page's own heading, section title, rows it must hold).
# The order is the page's order, which is broadcast order.
EXPECT = [
    ("s1",           "Series 1 (2011)",          "Series 1",          3),
    ("s2",           "Series 2 (2013)",          "Series 2",          3),
    ("special",      "Special (2014)",           "Special",           1),
    ("s3",           "Series 3 (2016)",          "Series 3",          6),
    ("s4",           "Series 4 (2017)",          "Series 4",          6),
    ("bandersnatch", "Interactive film (2018)",  "Interactive film",  1),
    ("s5",           "Series 5 (2019)",          "Series 5",          3),
    ("s6",           "Series 6 (2023)",          "Series 6",          5),
    ("s7",           "Series 7 (2025)",          "Series 7",          6),
]
TOTAL = 34          # rows, Bandersnatch included
NUMBERED = 33       # rows the page gives an EpisodeNumber

# The {{Series overview}} keys that correspond to the headings above, for the
# secondary cross-check. The two one-offs carry no episode count there.
OVERVIEW = {"s1": "1", "s2": "2", "s3": "3", "s4": "4",
            "s5": "5", "s6": "6", "s7": "7"}

MONTHS = ("January February March April May June July August September "
          "October November December").split()


def blocks(seg, name="Episode list"):
    """Every {{Episode list ...}} in seg, taken whole by counting braces.

    The shared reader closes a block at the first line-initial }} and so
    truncates at a nested multi-line template. This walks the braces instead,
    so a block ends where it actually ends.
    """
    out = []
    for m in re.finditer(r"\{\{\s*%s\s*(?=[|}])" % name, seg, re.I):
        i, depth = m.start(), 0
        while i < len(seg):
            if seg.startswith("{{", i):
                depth += 1
                i += 2
            elif seg.startswith("}}", i):
                depth -= 1
                i += 2
                if depth == 0:
                    break
            else:
                i += 1
        assert depth == 0, "unbalanced braces in an %s block" % name
        out.append(seg[m.end():i - 2])
    return out


def fields(block):
    """A block's |name = value pairs, split on pipes at nesting depth zero.

    Splitting on every pipe is what makes a wikilink or a template argument
    look like a new field; only depth-zero pipes separate fields.
    """
    depth, buf, parts, i = 0, [], [], 0
    while i < len(block):
        if block.startswith("{{", i) or block.startswith("[[", i):
            depth += 1
            buf.append(block[i:i + 2])
            i += 2
        elif block.startswith("}}", i) or block.startswith("]]", i):
            depth -= 1
            buf.append(block[i:i + 2])
            i += 2
        elif block[i] == "|" and depth == 0:
            parts.append("".join(buf))
            buf = []
            i += 1
        else:
            buf.append(block[i])
            i += 1
    parts.append("".join(buf))
    out = {}
    for p in parts:
        if "=" in p:
            k, v = p.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def title_of(f):
    """Display title and the article it links to.

    |RTitle is where the page puts a title that is a film rather than an
    episode; reading only |Title is what blanks Bandersnatch. {{hsp}} is a
    hair space and has to go before cleaning, or it cleans to the word "hsp".
    """
    raw = f.get("Title") or f.get("RTitle") or ""
    assert raw, "an episode row has neither Title nor RTitle"
    link = re.search(r"\[\[([^\]|]+)", raw)
    assert link, "no article link in %r" % raw[:60]
    text = wiki.clean(re.sub(r"\{\{\s*hsp\s*\}\}", "", raw)).strip('"')
    assert text, "empty title from %r" % raw[:60]
    return text, link.group(1).strip()


def airdate(f):
    """(year, "4 December 2011") from {{Start date|Y|M|D}}."""
    m = re.search(r"\{\{\s*Start date\s*\|\s*(\d{4})\s*\|\s*(\d{1,2})\s*\|\s*(\d{1,2})",
                  f.get("OriginalAirDate", ""), re.I)
    assert m, "no {{Start date}} in %r" % f.get("OriginalAirDate", "")[:60]
    y, mo, d = (int(x) for x in m.groups())
    return y, "%d %s %d" % (d, MONTHS[mo - 1], y)


def minutes(text):
    """The published runtime of one episode, from its own article's infobox."""
    ib = wiki.infobox(text, kind=r"television episode")
    assert ib, "no {{Infobox television episode}}"
    m = re.search(r"(\d+)\s*minutes", ib("length"))
    assert m, "no runtime in |length = %r" % ib("length")[:60]
    return int(m.group(1))


def bandersnatch_minutes(text):
    """Bandersnatch's default path. Its |runtime is a Plainlist reading
    Variable / Default / Total, so the number taken is the labelled Default
    and the section intro says that is what it is."""
    ib = wiki.infobox(text, kind=r"film")
    assert ib, "no {{Infobox film}} on the Bandersnatch article"
    rt = ib("runtime")
    assert re.search(r"''Variable''", rt), \
        "Bandersnatch's runtime is no longer given as Variable — recheck the note"
    m = re.search(r"Default'''\s*:?\s*(\d+)\s*minutes", rt)
    assert m, "no labelled Default runtime in %r" % rt[:90]
    total = re.search(r"Total'''\s*:?\s*(\d+)\s*minutes", rt)
    assert total, "no labelled Total runtime in %r" % rt[:90]
    return int(m.group(1)), int(total.group(1))


def segments(text):
    """The page sliced at its own === headings ===, keyed by heading."""
    heads = [(m.start(), m.group(1).strip())
             for m in re.finditer(r"^===\s*(.*?)\s*===\s*$", text, re.M)]
    end = text.find("==Home media==")
    assert end > 0, "the Home media heading has moved or gone"
    bounds = [h[0] for h in heads if h[0] < end] + [end]
    out = {}
    for (start, name), stop in zip(heads, bounds[1:]):
        if start < end:
            out[name] = text[start:stop]
    return out


def overview_counts(text):
    """episodesN from the page's {{Series overview}} — a cross-check only."""
    m = re.search(r"\{\{Series overview(.*?)\n\}\}", text, re.S)
    assert m, "no {{Series overview}} on the page"
    return {k: int(v) for k, v in re.findall(r"\|\s*episodes(\d+)\s*=\s*(\d+)",
                                             m.group(1))}


def hm(mins):
    return "%dh %dm" % (mins // 60, mins % 60) if mins >= 60 else "%dm" % mins


def anchor(heading):
    return "%s#%s" % (LIST_URL, heading.replace(" ", "_"))


def main():
    text = wiki.wikitext(PAGE, cache_dir=CACHE)
    assert text, "could not read %r" % PAGE
    segs = segments(text)
    over = overview_counts(text)

    # runtimes[id] = the published minutes, kept exact so the notes quote the
    # source figures rather than reconstructing them from rounded hours
    sections, seen, bander, runtimes = [], 0, None, {}
    for sid, heading, title, count in EXPECT:
        assert heading in segs, "the page no longer has the heading %r" % heading
        rows = blocks(segs[heading])
        # The enumerated rows are the authority: this is the count assertion.
        assert len(rows) == count, \
            "%s now holds %d episode rows, not %d — the source has been " \
            "re-cut and the sections need revisiting" % (heading, len(rows), count)
        # Secondary: the page's own summary must agree with its own tables.
        if sid in OVERVIEW:
            assert over.get(OVERVIEW[sid]) == count, \
                "{{Series overview}} says %r for %s but the tables enumerate %d" \
                % (over.get(OVERVIEW[sid]), heading, count)

        items, years, mins, last = [], set(), 0, ""
        for block in rows:
            f = fields(block)
            t, page = title_of(f)
            year, when = airdate(f)
            years.add(year)
            n = f.get("EpisodeNumber", "").strip()
            art = wiki.wikitext(page, cache_dir=CACHE)
            assert art, "could not read the article %r" % page

            if n:
                num = int(re.search(r"\d+", n).group(0))
                seen += 1
                assert num == seen, \
                    "episode numbering broke at %r: the page says %d, the run " \
                    "so far is %d" % (t, num, seen)
                w = minutes(art)
                items.append({"id": "bm-%d" % num, "t": t, "n": str(num),
                              "w": round(w / 60.0, 2)})
            else:
                # Bandersnatch: no episode number on the page, so none here.
                bander = bandersnatch_minutes(art)
                w = bander[0]
                items.append({"id": "bm-bandersnatch", "t": t, "n": "film",
                              "w": round(w / 60.0, 2)})
            runtimes[items[-1]["id"]] = w
            mins += w
            last = when

        # A multi-episode series is dated by year; a one-off is dated exactly,
        # because the date is the interesting thing about a special.
        if count > 1:
            span = "%d" % min(years) if len(years) == 1 else \
                   "%d–%d" % (min(years), max(years))
            sub = "%s · %d episodes · %s" % (span, count, hm(mins))
        else:
            sub = "%s · one %s · %s" % (
                last, "film" if sid == "bandersnatch" else "episode", hm(mins))
        sections.append({
            "id": sid, "title": title, "sub": sub,
            "links": [{"label": "Episode list", "url": anchor(heading)}],
            # No note on any row, and no intro that describes an episode.
            "items": items,
        })

    assert seen == NUMBERED, "built %d numbered episodes, expected %d" % (seen, NUMBERED)
    rows = [x for s in sections for x in s["items"]]
    assert len(rows) == TOTAL, "built %d rows, expected %d" % (len(rows), TOTAL)
    # The rule this list would most easily break: a bare row inside a weighted
    # list counts as one hour and nothing says so on the page.
    assert all(isinstance(x.get("w"), float) and x["w"] > 0 for x in rows), \
        "a row has no weight — an unweighted row in a weighted list silently " \
        "counts as one hour"

    total_min = sum(runtimes.values())
    # The range quoted in the notes is the range of the fixed-length rows;
    # Bandersnatch has no fixed length and its own note carries its figures.
    fixed = [m for i, m in runtimes.items() if i != "bm-bandersnatch"]
    shortest, longest = min(fixed), max(fixed)

    sections[0]["open"] = True
    assert bander, "Bandersnatch never parsed — the interactive film section moved"
    default_min, total_footage = bander
    assert sections[5]["id"] == "bandersnatch", "the intro is on the wrong section"
    sections[5]["intro"] = (
        "An interactive film rather than an episode, and the only row here "
        "with no fixed length: its own article gives the runtime as variable, "
        "with a default path of %d minutes and %d minutes of footage in "
        "total. It is weighted at the %d-minute default. Netflix withdrew it "
        "in May 2025 and has not reissued it in a linear form, so it may not "
        "be watchable where the rest of the list is."
        % (default_min, total_footage, default_min))

    p = {
        "slug": SLUG,
        "title": "Black Mirror",
        "subtitle": "every episode, plus Bandersnatch",
        "kind": "tv",
        # 80-89: a mainstream audience recognises the title on sight, and
        # "a Black Mirror episode" has become an ordinary English phrase for
        # people who have never watched one. Bottom of that band: it sits
        # below the long-running prestige runs a general audience has spent
        # more years with (The Sopranos 81, Seinfeld 82, Breaking Bad 84,
        # The Office 85) and above Doctor Who 77, The X-Files 73 and its own
        # stated ancestor The Twilight Zone 72. Thirty-four rows is a small
        # list, which is a mild nudge down inside the band, not out of it.
        "popularity": 80,
        "year": "2011–2025",
        "blurb": "All 33 episodes and Bandersnatch, in broadcast order and "
                 "weighted by runtime. Nothing connects them — start anywhere.",
        "unit": {"one": "episode", "many": "episodes"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        # The switched-off screen the show is named after: black with blue in
        # it, lifting to a cold screen glow in the dark theme. Deliberately
        # not the obvious near-black — #111111 is A24's accent exactly, with
        # Junji Ito 4.7 from it, and this pair would have landed on top of
        # both. Measured in CIELAB against every accent in the catalogue,
        # #101560 sits 16.3 from its nearest light-mode neighbour, Final
        # Fantasy #2E3A8A (then Futurama 17.0, Star Trek 17.5), and #C6B4FE
        # sits 13.3 from its nearest dark-mode neighbour, The Twilight Zone
        # #B4ABDE (then David Lynch 13.6, James Bond Games 14.0).
        "accent": "#101560",
        "accentDark": "#C6B4FE",
        "tiers": False,
        "random": True,
        "notes": [
            ["Start anywhere.",
             "This is an anthology: no character, no world and no arc carries "
             "from one episode to the next, so the order is a filing system "
             "rather than a route. The Pick one for me button is a perfectly "
             "good front door, and a series you fancy is as valid a starting "
             "point as the first. The single exception is series 7's finale, "
             "which is "
             "a sequel to a series 4 episode and shares its name — the only "
             "pair in %d rows that asks to be watched in order." % TOTAL],
            ["Weighted by runtime, every row.",
             "Unusually for television, Black Mirror publishes a length per "
             "episode, and they run from %d minutes to %d — the strip and the "
             "finish date are built on those figures rather than on an "
             "episode count. %d rows, %s in total. Each figure is the runtime "
             "given by that episode's own Wikipedia article." %
             (shortest, longest, TOTAL, hm(total_min))],
            ["Bandersnatch, and how it is counted.",
             "The 2018 interactive film sits where it was released, between "
             "series 4 and series 5, in a section of its own because it is "
             "not an episode and the source does not number it. It has no "
             "fixed runtime; it is weighted at its published 90-minute "
             "default path, with 312 minutes of footage in total, and a "
             "single viewing is what that number describes. Netflix withdrew "
             "it in May 2025 and has not reissued it in a linear form."],
            ["No episode notes, on purpose.",
             "The show is its turns, and a one-line summary hands several of "
             "them over. Nothing here describes what happens in an episode. "
             "The titles are the official titles, printed as the source has "
             "them, including the loaded ones — a title is what an episode is "
             "called, not what it does."],
            "Titles, air dates and numbering machine-read from Wikipedia's "
            "List of Black Mirror episodes; runtimes from each episode's own "
            "article. Every section's row count is asserted against the "
            "enumerated tables before this builds.",
        ],
        "sections": sections,
    }

    out = prop.write(p)
    print("wrote %s — %d rows, %s" % (out.name, len(rows), hm(total_min)))
    for s in sections:
        print("   %-16s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
