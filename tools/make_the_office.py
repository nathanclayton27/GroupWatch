#!/usr/bin/env python3
"""Generate properties/the-office.json — the American series, 2005-2013.

    python3 tools/make_the_office.py

One row per entry in the nine season articles' episode tables: 186 rows
covering all 201 numbered episodes. Fifteen entries are numbered as two
episodes each by the episode lists and sit here as one row spanning both
numbers, exactly as the season articles file them; all fifteen aired in one
sitting, so there is never a "part two" to look for on another night.

THE COUNT. 201 is the figure the list page's lede states and the figure this
list ships, because it is the numbering the enumerated episode tables use:
the Series overview counts 6, 22, 25, 19, 28, 26, 26, 24 and 25. Those tables
have only 186 entries. The 15-entry gap is the hour-long broadcasts that the
production numbering splits in two, and the split is not applied evenly —
"Moving On" and "Livin' the Dream" aired hour-long and are numbered as one
episode each, while "Niagara" and "The Delivery" aired hour-long and are
numbered as two. Counting each table entry once instead of following the
tables' own numbers gives 186, which is what a streaming catalogue shows. Both
figures are defensible; this list takes 201 and marks the shape of every row
that is not a plain half-hour, so the numbering never has to be guessed at.

Deliberately excluded: the nine webisode series that ran on NBC.com between
seasons (36 shorts, outside the 201), and the British series, which is a
different show with its own episode list. Not marked: the season-eight DVD's
"producer's cuts" of "Angry Andy" and "Fundraiser", and Peacock's extended
"Superfan Episodes" — both are alternate cuts of rows already here rather than
entries of their own, and marking one family of home-video recuts but not the
other would be arbitrary.

Nothing is weighted. The season articles publish runtime only as a per-category
approximation attached to a footnote symbol ("around 28 minutes", "around 42
minutes"), never per row, so there is no verified per-episode runtime to weight
by, and a blanket 22 minutes would be actively wrong on the 25 rows that aired
long rather than merely unverified. Every row counts one.

Episode titles, numbering and airdates are machine-read here from the nine
"The Office (American TV series) season N" articles, cached under
scratch/theoffice/; the per-season totals are asserted against the list page's
own Series overview and its stated 201 before anything is written.
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop, wiki

SLUG = "the-office"
CACHE = prop.ROOT / "scratch" / "theoffice"
LIST_PAGE = "List of The Office (American TV series) episodes"
SEASON_PAGE = "The Office (American TV series) season %d"

SEASONS = 9
TOTAL = 201            # the tables' own numbering, and the list page's lede
ROWS = 186             # one row per table entry
DOUBLES = TOTAL - ROWS  # 15 entries numbered as two episodes
SUPERSIZED = 8         # 40-minute slots, every one numbered as a single episode
HOUR_LONG = 16         # 14 of them numbered as two, 2 numbered as one
EXTENDED_75 = 1        # "Finale", numbered as two

# The footnote legends the season articles carry under their tables, keyed by
# the phrase that identifies them. The symbols are reused across seasons for
# different meanings (season 3's "a" is super-sized, season 9's "c" is the
# 75-minute finale), so the legend is read per season rather than assumed.
LEGEND = {"super-sized": "supersized", "hour-long": "hour",
          "75-minute": "ext75"}
SHAPE_NOTE = {"supersized": "Aired super-sized, in a 40-minute slot",
              "hour": "Aired hour-long",
              "ext75": "Aired in a 75-minute slot"}


def page(name):
    """Cached wikitext, fetched on first run."""
    text = wiki.wikitext(name, cache_dir=str(CACHE))
    assert text, "could not read %s" % name
    return text


def blocks(text):
    """Every {{Episode list}} / {{Episode list/sublist}} template, whole.

    Brace-matched rather than regex-bounded: the multi-part rows nest
    {{Start date}} and citation templates inside themselves, and a lazy
    close would cut the block off at the first inner }}.
    """
    out = []
    for m in re.finditer(r"\{\{(?:#invoke:)?Episode list", text, re.I):
        depth, j = 0, m.start()
        while j < len(text):
            if text.startswith("{{", j):
                depth += 1
                j += 2
            elif text.startswith("}}", j):
                depth -= 1
                j += 2
                if depth == 0:
                    break
            else:
                j += 1
        assert depth == 0, "unclosed episode block in wikitext"
        out.append(text[m.start():j])
    return out


def field(block, name):
    """One template field, up to the next field or the template close."""
    m = re.search(r"\|\s*%s\s*=\s*(.*?)(?=\n\s*\||\Z)" % name, block, re.S)
    return m.group(1).strip() if m else ""


def legend_of(text):
    """{{note|a|sym}} denotes ... -> {"a": "supersized"} for one season."""
    out = {}
    for m in re.finditer(r"\{\{note\|([A-Za-z]+)\|[^}]*\}\}\s*([^\n]*)", text):
        key, body = m.group(1), m.group(2)
        if "denotes" not in body:
            continue          # season 1's notes are casting trivia, not shapes
        hit = [v for k, v in LEGEND.items() if k in body]
        assert len(hit) == 1, "unreadable legend %r: %r" % (key, body[:80])
        out[key] = hit[0]
    return out


def season_rows(n):
    """(e, e2, title, year, shape) per table entry, in table order."""
    text = page(SEASON_PAGE % n)
    legend = legend_of(text)
    rows = []
    for b in blocks(text):
        parts = field(b, "NumParts")
        if parts:
            assert parts.strip() == "2", "unexpected NumParts %r in season %d" % (parts, n)
            e = int(field(b, "EpisodeNumber2_1"))
            e2 = int(field(b, "EpisodeNumber2_2"))
            overall = int(field(b, "EpisodeNumber_1"))
        else:
            e = e2 = int(field(b, "EpisodeNumber2"))
            overall = int(field(b, "EpisodeNumber"))
        title = wiki.clean(field(b, "Title")).strip('"')
        assert title, "empty title in season %d, episode %d" % (n, e)
        air = field(b, "OriginalAirDate")
        assert not re.search(r"OriginalAirDate_\d", b), \
            "season %d, %s: parts aired on separate dates" % (n, title)
        ym = re.search(r"\{\{Start date\|(\d{4})\|", air)
        assert ym, "no airdate for season %d, %s" % (n, title)
        ref = re.search(r"\{\{ref\|([A-Za-z]+)\|", field(b, "RTitle"))
        shape = None
        if ref:
            assert ref.group(1) in legend, \
                "season %d, %s: footnote %r has no legend" % (n, title, ref.group(1))
            shape = legend[ref.group(1)]
        rows.append({"e": e, "e2": e2, "overall": overall, "t": title,
                     "y": int(ym.group(1)), "shape": shape})
    return rows


def year_span(rows):
    ys = sorted({r["y"] for r in rows})
    if ys[0] == ys[-1]:
        return str(ys[0])
    return "%d–%02d" % (ys[0], ys[-1] % 100)


def main():
    # The list page is the arbiter of the totals: its Series overview holds a
    # per-season count and its lede holds the series total, and both are
    # checked against what the tables actually enumerate.
    listing = page(LIST_PAGE)
    stated = {n: int(re.search(r"\|\s*episodes%d\s*=\s*(\d+)" % n,
                               listing).group(1))
              for n in range(1, SEASONS + 1)}
    lede = int(re.search(r"A total of (\d+) episodes", listing).group(1))
    assert lede == TOTAL, lede
    assert sum(stated.values()) == TOTAL, sum(stated.values())

    sections, shapes, doubles = [], [], []
    overall = 0
    for n in range(1, SEASONS + 1):
        rows = season_rows(n)
        items = []
        for i, r in enumerate(rows):
            # numbering must be contiguous within the season and across the run
            assert r["e"] == (rows[i - 1]["e2"] + 1 if i else 1), \
                "season %d numbering breaks at %r" % (n, r["t"])
            assert r["overall"] == overall + 1, \
                "run numbering breaks at %r" % r["t"]
            overall = r["overall"] + (r["e2"] - r["e"])

            span = str(r["e"]) if r["e"] == r["e2"] else "%d–%d" % (r["e"], r["e2"])
            item = {"id": "office-s%de%d" % (n, r["e"]), "t": r["t"],
                    "n": "S%dE%s" % (n, span)}
            bits = []
            if n == 1 and i == 0:
                bits.append("Series premiere")
            if n == SEASONS and i == len(rows) - 1:
                bits.append("Series finale")
            if r["t"] == "Stress Relief":
                bits.append("The post-Super Bowl XLIII episode")
            if r["shape"]:
                shapes.append((n, r["t"], r["shape"]))
                bits.append(SHAPE_NOTE[r["shape"]])
            if r["e"] != r["e2"]:
                doubles.append((n, r["t"]))
                assert r["shape"], \
                    "season %d, %s: numbered as two with no shape footnote" % (n, r["t"])
                bits.append("Numbered as two episodes")
            elif r["shape"]:
                bits.append("Numbered as one episode")
            note = prop.join_bits(*bits)
            if note:
                item["note"] = note
            items.append(item)

        count = sum(r["e2"] - r["e"] + 1 for r in rows)
        assert count == stated[n], (n, count, stated[n])
        sec = {"id": "s%d" % n, "title": "Season %d" % n,
               "sub": "%s · %d episodes" % (year_span(rows), count),
               "items": items}
        if n == 1:
            sec["open"] = True
        sections.append(sec)

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == ROWS, len(ids)
    assert overall == TOTAL, overall
    assert len(doubles) == DOUBLES, len(doubles)
    tally = {k: [t for _, t, s in shapes if s == k] for k in SHAPE_NOTE}
    assert len(tally["supersized"]) == SUPERSIZED, tally["supersized"]
    assert len(tally["hour"]) == HOUR_LONG, tally["hour"]
    assert len(tally["ext75"]) == EXTENDED_75, tally["ext75"]
    assert sections[0]["items"][0]["t"] == "Pilot"
    finale = sections[-1]["items"][-1]
    assert finale["t"] == "Finale" and finale["n"] == "S9E24–25", finale
    assert not any("w" in x for s in sections for x in s["items"]), \
        "a weighted row in an unweighted list would count as one hour"

    p = {
        "slug": SLUG,
        "title": "The Office",
        "subtitle": "the American series — nine seasons, 2005–2013",
        "kind": "tv",
        # Nine seasons on network television, and the comfort rewatch a
        # general audience names without being prompted; a notch above
        # Seinfeld (82) and Breaking Bad (84) on present-day reach, well
        # below The Simpsons (93), the one sitcom here that is a household
        # name outside its own audience. See POPULARITY.md.
        "popularity": 85,
        "year": "2005–2013",
        "blurb": "All 201 episodes in broadcast order — nine seasons at the "
                 "Scranton branch of Dunder Mifflin, from Pilot to Finale.",
        "unit": {"one": "episode", "many": "episodes"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "accent": "#2E6F8E",
        "accentDark": "#E8B27A",
        "tiers": False,
        "notes": [
            ["186 rows, 201 episodes.", "Fifteen entries are numbered as two "
             "episodes each by the episode lists and sit here as one row "
             "spanning both numbers, exactly as the season articles file "
             "them. All fifteen aired in one sitting, so no row has a second "
             "half on another night. Counting each entry once instead — the "
             "way a streaming catalogue does — gives 186."],
            ["Hour-long and double-numbered are not the same thing.",
             "Two hour-long broadcasts are numbered as one episode each, "
             "fourteen others as two, and eight super-sized 40-minute "
             "broadcasts as one. Every row that did not air as a plain "
             "half-hour says what shape it aired in and how it is numbered, "
             "so the count never has to be guessed at."],
            ["The webisodes are not listed.", "Nine short webisode series ran "
             "on NBC.com between seasons. They sit outside the run's 201 "
             "numbered episodes and are not rows here."],
            ["Broadcast versions only.", "The season-eight DVD's producer's "
             "cuts of two episodes and Peacock's extended Superfan Episodes "
             "are alternate cuts of rows already listed, not entries of their "
             "own, and are not marked."],
            ["Nothing is weighted.", "The source articles publish runtime "
             "only as a per-category approximation on a footnote, never per "
             "episode, so there is no verified per-row runtime to weight by — "
             "and with genuine hour-long entries in the list, a flat 22 "
             "minutes on every row would be wrong rather than merely "
             "unverified. Every row counts one."],
            "Episode titles, numbering and airdates machine-read from the "
            "nine Wikipedia season articles; every season's numbering is "
            "asserted contiguous and equal to the episode list's own Series "
            "overview counts, and the run total against its stated 201, "
            "before this builds.",
        ],
        "sections": sections,
    }

    out = prop.write(p)
    print("wrote %s — %d rows covering %d episodes" % (out.name, len(ids), overall))
    for s in sections:
        print("   %-10s %3d rows  %s" % (s["title"], len(s["items"]), s["sub"]))
    print("   numbered as two (%d): %s"
          % (len(doubles), ", ".join(t for _, t in doubles)))
    for k in ("supersized", "hour", "ext75"):
        print("   %-10s (%d): %s" % (k, len(tally[k]), ", ".join(tally[k])))


if __name__ == "__main__":
    main()
