#!/usr/bin/env python3
"""Collect the James Bond video game roster into scratch/bondgames/games.json.

    python3 scratch/bondgames/collect.py

Why this shape. Wikipedia's "List of James Bond video games" is a redirect to
"James Bond in video games", and that article carries NO wikitable at all —
it is prose plus era headings. The machine-readable enumeration of the games
lives in the navbox the article transcludes, {{James Bond video games}},
whose groups are the publisher eras. So:

  * the ROSTER comes from the navbox's own bullet lists (parsed here, not
    typed) — group name, display title, and the article each bullet links to;
  * the ERA BOUNDARIES come from the article's own === headings ===, parsed
    here too, so a re-cut of the article's eras shows up as an assert;
  * each game's YEAR comes from its own article's {{Infobox video game}}
    release field, not from anyone's memory;
  * each game's STORY HOURS come from HowLongToBeat behind gwlib.hltb's
    verify-by-name gate. Anything that does not verify records why and ships
    unweighted.

Everything fetched is cached next to this file so the run is reproducible.

The howlongtobeatpy package is dead — its hard-coded search endpoint 404s
against the current site and it returns None for every query instead of
raising. The live protocol this script found (GET /api/search/site/init for
a token, then POST /api/search/site with that token in BOTH the headers and
the payload — the site's own bundle sets payload[hpKey] = hpVal and the
request 404s without it) now lives in tools/gwlib/hltb.py, reconciled with
the Mega Man collector's punctuation-splitting of search terms, and this
uses it. The verify-by-name gate is still what decides: gwlib.hltb.
story_hours, which returns nothing rather than a guess, and RAISES rather
than returning nothing when the endpoint itself is broken.
"""
import json
import pathlib
import re
import sys
import time

import requests

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from gwlib import wiki  # noqa: E402
from gwlib import hltb  # noqa: E402

HLTB = "https://howlongtobeat.com"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")

Row = hltb.Result           # the attribute shape story_hours reads
_HLTB_SESSION = []          # one live session for the whole run


def hltb_search(name, session=None, cache=True):
    """Raw HowLongToBeat search rows for `name`, disk-cached one file per
    query so the misses stay reviewable next to the wikitext."""
    f = HERE / "hltb" / (re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-") + ".json")
    if cache and f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    if not _HLTB_SESSION:
        _HLTB_SESSION.append(hltb.Session())
    rows = _HLTB_SESSION[0].rows(name)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n",
                 encoding="utf-8", newline="\n")
    return rows

ARTICLE = "List of James Bond video games"
NAVBOX = "Template:James Bond video games"

# Navbox groups that hold licensed games from GoldenEye 007 onward. The
# pre-1995 8-bit run (group "Domark"), the odds and ends of "Other", and the
# fan projects in "Unofficial" are a different page's problem — except for
# 007 First Light, which sits in "Other" only because the navbox has no IO
# Interactive group yet.
KEEP_GROUPS = ["Nintendo", "Electronic Arts", "Activision"]
KEEP_EXTRA = {"007 First Light"}

# HowLongToBeat is queried under the exact name its own entry carries, keyed
# by Wikipedia page so the three separately-articled The World Is Not Enough
# games and the two Everything or Nothing games stay distinguishable. A None
# means HLTB has no entry that identifies THAT game — the row ships
# unweighted with the reason below, because the alternative is putting a
# figure that belongs to a different game into everyone's pace.
HLTB_NAME = {
    "GoldenEye 007": "GoldenEye 007",
    "James Bond 007 (1998 video game)": "James Bond 007",
    "Tomorrow Never Dies (video game)": "Tomorrow Never Dies",
    "007 Racing": "007 Racing",
    "The World Is Not Enough (Nintendo 64 video game)": None,
    "The World Is Not Enough (PlayStation video game)": None,
    "The World Is Not Enough (Game Boy Color video game)": None,
    "James Bond 007: Agent Under Fire": "James Bond 007: Agent Under Fire",
    "James Bond 007: Nightfire": "James Bond 007: Nightfire",
    "James Bond 007: Everything or Nothing":
        "James Bond 007: Everything or Nothing",
    "James Bond 007: Everything or Nothing (Game Boy Advance video game)":
        None,
    "GoldenEye: Rogue Agent": "GoldenEye: Rogue Agent",
    "From Russia with Love (video game)": "From Russia with Love",
    "007: Quantum of Solace": "Quantum of Solace",
    "James Bond 007: Blood Stone": "James Bond 007: Blood Stone",
    "GoldenEye 007 (2010 video game)": "GoldenEye 007",
    "007 Legends": "007 Legends",
    "007 First Light": "007 First Light",
}

# Why a None above is a None. Checked against the HLTB game pages themselves,
# whose platform lists are cached in hltb/ alongside the search results.
NO_HLTB = {
    "The World Is Not Enough (Nintendo 64 video game)":
        "HowLongToBeat files all three World Is Not Enough games as one entry",
    "The World Is Not Enough (PlayStation video game)":
        "HowLongToBeat files all three World Is Not Enough games as one entry",
    "The World Is Not Enough (Game Boy Color video game)":
        "HowLongToBeat files all three World Is Not Enough games as one entry",
    "James Bond 007: Everything or Nothing (Game Boy Advance video game)":
        "HowLongToBeat's only Everything or Nothing entry is the 2004 console "
        "game",
}


def hltb_platforms(game_id, session=None):
    """The platform list off an HLTB game page — the evidence that an entry
    covers more than one of Wikipedia's separately-articled games."""
    f = HERE / "hltb" / ("game-%s.json" % game_id)
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    s = session or requests.Session()
    r = s.get("%s/game/%s" % (HLTB, game_id), timeout=45,
              headers={"User-Agent": UA, "Referer": HLTB + "/"})
    r.raise_for_status()
    name = re.search(r'"game_name":"(.*?)"', r.text)
    plat = re.search(r'"profile_platform":"(.*?)"', r.text)
    out = {"game_id": game_id,
           "game_name": name.group(1) if name else None,
           "platforms": plat.group(1).split(", ") if plat else []}
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8",
                 newline="\n")
    time.sleep(1.5)
    return out


def navbox_roster(text):
    """[(group, display, page, qualifier)] from the navbox's bullet lists."""
    groups = dict(re.findall(r"^\s*\|\s*group(\d+)\s*=\s*(.+?)\s*$",
                             text, re.M))
    out = []
    for m in re.finditer(r"^\s*\|\s*list(\d+)\s*=\s*\n((?:\s*\*.*\n)+)",
                         text, re.M):
        group = groups.get(m.group(1))
        if not group:
            continue
        for line in m.group(2).strip().splitlines():
            line = line.strip().lstrip("*").strip()
            link = re.search(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]", line)
            if not link:
                continue
            page = link.group(1).strip()
            display = (link.group(2) or page).strip().strip("' ")
            # trailing "(N64)" / "(1998)" outside the link is the navbox's own
            # disambiguator for same-named entries
            tail = line[link.end():]
            qual = re.search(r"\(([^)]+)\)", tail)
            out.append((group, display, page, qual.group(1) if qual else ""))
    return out


def era_headings(text):
    """[(name, lo, hi)] from the article's own === Foo era (1999-2005) ==="""
    out = []
    for m in re.finditer(r"^===\s*(.+?)\s*\((\d{4})\s*[–-]\s*"
                         r"(\d{4}|present)\s*\)\s*===\s*$", text, re.M):
        hi = 9999 if m.group(3) == "present" else int(m.group(3))
        out.append((m.group(1), int(m.group(2)), hi))
    return out


RELEASE_YEAR = re.compile(r"(?:^|[^\d])((?:19|20)\d{2})(?![\d])")


def lead(value):
    """The first name in an infobox list — "Eurocom, Gearbox (PC)" -> Eurocom.

    Parentheses come off BEFORE the split: Quantum of Solace's developer field
    reads "Treyarch (PC, PS3, Wii, X360), Eurocom (PS2), …", and splitting
    first left the string as "Treyarch (PC".
    """
    v = re.sub(r"\s*\([^)]*\)\s*", " ", value)
    return re.split(r"\s*(?:,|&|\||/| and )\s*", v.strip(), 1)[0].strip(" ,;")


def game_facts(page):
    """Release year, lead developer, genre and platforms off the article's
    own {{Infobox video game}} — nobody's memory."""
    text = wiki.wikitext(page, cache_dir=str(HERE))
    assert text, "no wikitext for %r" % page
    field = wiki.infobox(text, kind=r"video game")
    assert field, "no {{Infobox video game}} on %r" % page
    raw = field("released") or field("release")
    assert raw, "no release field on %r" % page
    years = [int(y) for y in RELEASE_YEAR.findall(raw)]
    assert years, "no year in release field of %r: %r" % (page, raw[:120])
    plats = wiki.clean(field("platforms") or field("platform") or "")
    return {
        "year": min(years),
        "release_raw": re.sub(r"\s+", " ", raw)[:200],
        "developer": lead(wiki.clean(field("developer"))),
        "genre": wiki.clean(field("genre")),
        "platforms": [p for p in re.split(r"\s*[,|]\s*", plats) if p],
    }


def main():
    art = wiki.wikitext(ARTICLE, cache_dir=str(HERE))
    nav = wiki.wikitext(NAVBOX, cache_dir=str(HERE))
    assert art and nav

    eras = era_headings(art)
    roster = navbox_roster(nav)

    # The article's own {{Infobox video game series}}, kept so the generator
    # can fail loudly if the summary and the enumeration ever disagree —
    # the infobox already contradicts the article once (it dates the first
    # game to 1982 while the article's first era heading starts at 1983).
    ib = wiki.infobox(art, kind=r"video game series")
    assert ib, "no series infobox on the article"
    series = {
        "publishers": [p for p in re.split(r"\s*,\s*",
                       wiki.clean(ib("publisher"))) if p],
        "first_release_version": wiki.clean(ib("first release version")),
        "first_release_date": wiki.clean(ib("first release date")),
        "latest_release_version": wiki.clean(ib("latest release version")),
        "latest_release_date": wiki.clean(ib("latest release date")),
    }

    games = []
    for group, display, page, qual in roster:
        if group not in KEEP_GROUPS and display not in KEEP_EXTRA:
            continue
        row = {"group": group, "t": display, "page": page, "qual": qual}
        row.update(game_facts(page))
        games.append(row)

    games.sort(key=lambda g: (g["year"], g["t"], g["qual"]))

    session = requests.Session()
    for g in games:
        assert g["page"] in HLTB_NAME, "no HLTB name mapped for %r" % g["page"]
        name = HLTB_NAME[g["page"]]
        if name is None:
            g["hltb_query"] = None
            g["hltb_hours"] = None
            g["hltb_why"] = NO_HLTB[g["page"]]
            g["hltb_id"] = g["hltb_name"] = g["hltb_year"] = None
            print("%-38s %s  UNWEIGHTED: %s"
                  % (g["t"], g["year"], g["hltb_why"]))
            continue
        try:
            rows = hltb_search(name, session)
        except Exception as e:                     # network, not data
            rows, err = [], "lookup failed: %s" % e
        else:
            err = None
        # Two Bond games share a name ("GoldenEye 007", 1997 and 2010). The
        # gate used to return on its FIRST name match and reject the 2010
        # game as a year mismatch against the 1997 one, so this had to
        # pre-sort by year distance; that workaround is now inside
        # gwlib.hltb.story_hours, which considers name matches
        # nearest-year-first and still checks the year on the one it picks.
        hours, rec, why = hltb.story_hours(name, year=g["year"],
                                           results=[Row(d) for d in rows])
        g["hltb_query"] = name
        g["hltb_hours"] = hours
        g["hltb_why"] = err or why
        g["hltb_id"] = getattr(rec, "game_id", None) if rec else None
        g["hltb_name"] = getattr(rec, "game_name", None) if rec else None
        g["hltb_year"] = getattr(rec, "release_world", None) if rec else None
        print("%-38s %s  %s" % (name, g["year"],
                                hours if hours else "UNWEIGHTED: " + g["hltb_why"]))

    # The two HLTB entries that swallow more than one game, kept as evidence
    # for the unweighted rows above: their own platform lists span the
    # platforms Wikipedia splits into separate articles.
    conflated = [hltb_platforms(i, session) for i in (10278, 4808)]
    for c in conflated:
        print("conflated: %s covers %s"
              % (c["game_name"], ", ".join(c["platforms"])))

    out = {"article": ARTICLE, "navbox": NAVBOX,
           "eras": [{"name": n, "lo": lo, "hi": hi} for n, lo, hi in eras],
           "series_infobox": series,
           "conflated_hltb_entries": conflated,
           "games": games}
    # newline="\n" or a Windows re-run rewrites every line with CRLF and the
    # collector stops being byte-identical on a second pass
    (HERE / "games.json").write_text(
        json.dumps(out, indent=1, ensure_ascii=False) + "\n",
        encoding="utf-8", newline="\n")
    print("\n%d games, %d weighted" % (len(games),
          sum(1 for g in games if g["hltb_hours"])))


if __name__ == "__main__":
    main()
