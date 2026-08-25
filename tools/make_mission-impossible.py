#!/usr/bin/env python3
"""Generate properties/mission-impossible.json.

    PYTHONIOENCODING=utf-8 python tools/make_mission-impossible.py

Every released Mission: Impossible film, in release order — the eight rows of
the Films table in Wikipedia's "Mission: Impossible (film series)". The table
is the roster and the roster is the whole list: nothing is excluded, so the
guard against a stale list is the row count itself. A ninth film appearing on
that table breaks this build, which is the point.

WHY THIS LIST EXISTS WHEN tom-cruise ALREADY HAS THESE FILMS

All eight are already rows on properties/tom-cruise.json, deliberately. That
list is held together by an actor; this one is held together by a story, and
someone working through the Missions in order does not want Jerry Maguire
next. Two doors into the same eight films.

Which makes one thing load-bearing rather than nice: the rows have to PAIR.
build.py groups film rows across lists on normalised-title | year | medium,
so a tick on either list must propagate to the other. Two ways that breaks,
and both are asserted below rather than assumed:

  * the year. Both lists take 1996/2000/2006/2011/2015/2018/2023/2025 from
    their own sources and they agree; the generator recomputes tom-cruise's
    keys off disk and refuses to build if a single one fails to match.
  * the title. The seventh film was retroactively retitled "Mission:
    Impossible – Dead Reckoning" for streaming, and Wikipedia's series
    article carries an explicit talk-page consensus to keep "Part One"
    anyway. tom-cruise says "Part One", so this list says "Part One" — a
    silent retitle here would split the group exactly the way Casablanca's
    did between Criterion and Best Picture (CLU-191). The consensus comment
    is asserted to still be in the source.

Row ids carry their own mi- prefix and are checked disjoint from
tom-cruise's tc- ids: separate files sharing an id scheme would be a real bug
even though the tick pairing is by title and year.

RUNTIMES

Every bar is the film's own Wikipedia infobox runtime, in hours — not
Wikidata, not an estimate. WEIGHT = x.w >= 0 ? x.w : 1, so one unweighted row
would silently count as an hour; the collector returns None rather than a
guess when an infobox gives a range, and this generator refuses to build on a
None. The series article's own infobox states the range as 110-170 minutes,
which is checked against the eight numbers actually collected.

Data:   scratch/mission-impossible/collect.py -> mi_data.json
Accent: scratch/mission-impossible/accent.py
"""
import datetime
import json
import pathlib
import re
import sys
import unicodedata

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop
from gwlib.prop import join_bits, slug

SLUG = "mission-impossible"
ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "scratch" / SLUG / "mi_data.json"

# A burnt fuse cord and the spark on it: one hue (h=23) at two lightnesses,
# both inside the bands the shipped accents actually occupy. Measured in
# CIELAB against every accent in properties/index.json — 148 lists, 296
# accents — by scratch/mission-impossible/accent.py, and asserted unshipped
# against properties/*.json below.
ACCENT, ACCENT_DARK = "#813403", "#E76E23"

# Two sections, and the break is the one the series itself makes. The first
# three films have three different directors and are made by Cruise/Wagner,
# which the series infobox marks as films 1-3; from Ghost Protocol on the
# companies are Skydance and TC Productions (4-8), McQuarrie directs four in
# a row, and every film runs longer than everything before it. Both halves of
# that are asserted, so the heading cannot outlive the facts under it.
ERAS = [
    ("early", "Three films, three directors", 1996, 2006),
    ("modern", "From Ghost Protocol on", 2011, 2025),
]

# Small counts read as words in this house's copy; a value outside the table
# raises rather than printing a digit mid-sentence.
WORD = {2: "two", 3: "three", 4: "four", 5: "five", 8: "eight"}


def normt(t):
    """build.py's sync-key normalizer, copied so this generator computes the
    same groups the build will."""
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    t = re.sub(r"[^a-z0-9]+", " ", t).strip()
    return re.sub(r"^(the|a|an) ", "", t)


def year_of(x, n):
    """build.py's year-for-sync rule: the row number when it is a plain year,
    else an explicit y, else the single year named in the note."""
    if re.fullmatch(r"(18|19|20)\d{2}", n):
        return n
    explicit = str(x.get("y", ""))
    if re.fullmatch(r"(18|19|20)\d{2}", explicit):
        return explicit
    found = set(re.findall(r"\b((?:18|19|20)\d{2})\b", x.get("note") or ""))
    return found.pop() if len(found) == 1 else None


def film_rows(p):
    """(sync key, id, title) for every syncable row of a shipped property."""
    if p.get("secret") or "film" not in (p.get("kind") or ""):
        return []
    out = []
    for s in p.get("sections", []):
        for x in s.get("items", []):
            y = year_of(x, str(x.get("n", "")))
            if y:
                out.append((normt(x["t"]) + "|" + y + "|f", x["id"], x["t"]))
    return out


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    films = data["films"]
    by = {f["t"]: f for f in films}

    # ---- the roster, checked against the source rather than remembered ----
    assert data["source"] == "Mission: Impossible (film series)", data["source"]
    # Nothing is excluded, so the count IS the guard: a ninth row on the
    # source's own Films table fails this build the day it appears, which is
    # what the "assert the excluded ones are still unreleased" rule buys on a
    # list that excludes nothing.
    assert data["table_rows"] == 8, data["table_rows"]
    assert len(films) == 8, [f["t"] for f in films]
    assert "the eighth film, The Final Reckoning" in data["lead"], data["lead"]
    assert films[0]["t"] == "Mission: Impossible" and films[0]["year"] == 1996
    assert films[-1]["t"] == "Mission: Impossible – The Final Reckoning" and \
        films[-1]["year"] == 2025, films[-1]
    assert all(f["t"].startswith("Mission: Impossible") for f in films), \
        [f["t"] for f in films]
    # Each row's title is the film article's own bold lead title AND the
    # series table's link label; where a source disagrees with itself the
    # build stops instead of picking one.
    assert all(f["t"] == f["table_title"] for f in films), \
        [(f["t"], f["table_title"]) for f in films if f["t"] != f["table_title"]]
    assert all(str(f["year"]) in f["short_description"] for f in films), \
        [(f["t"], f["short_description"]) for f in films]

    # ---- released, every one of them --------------------------------------
    today = datetime.date.today().isoformat()
    for f in films:
        assert f["table_release"] <= today, \
            "%s is dated %s and has not opened yet" % (f["t"], f["table_release"])
        assert f["release_dates"] and min(f["release_dates"]) <= today, \
            "%s has no released date in the past" % f["t"]
    rel = [f["table_release"] for f in films]
    assert rel == sorted(rel), "release dates are not non-decreasing: %s" % rel
    assert len({f["year"] for f in films}) == len(films), \
        "two films share a year; the release order needs a tiebreak"
    # No ninth film is titled or dated anywhere in the source's Future
    # section; the prose that says so is checked so the note cannot go stale.
    assert "would be his final film in the series" in data["future_section"], \
        data["future_section"][-600:]

    # ---- runtimes: parsed, never defaulted --------------------------------
    assert all(isinstance(f["runtime"], int) and f["runtime"] > 0
               for f in films), \
        "unparsed runtime: %s" % [f["t"] for f in films if not f["runtime"]]
    assert all(re.fullmatch(r"%d minutes" % f["runtime"], f["runtime_raw"])
               for f in films), \
        [(f["t"], f["runtime_raw"]) for f in films
         if not re.fullmatch(r"%d minutes" % f["runtime"], f["runtime_raw"])]
    mins = sum(f["runtime"] for f in films)
    assert mins == 1104, mins                     # 18 hours 24 minutes exactly
    hours = mins / 60.0
    # the series article's own infobox states the range; it must be these
    # same eight numbers, or one of the two sources has moved
    lo, hi = min(f["runtime"] for f in films), max(f["runtime"] for f in films)
    assert data["series_infobox"]["runtime"] == "%d–%d minutes" % (lo, hi), \
        data["series_infobox"]["runtime"]
    assert by["Mission: Impossible"]["runtime"] == lo == 110, lo
    assert films[-1]["runtime"] == hi == 170, hi

    # ---- the claims the sections and notes make ---------------------------
    early = [f for f in films if f["year"] <= 2006]
    modern = [f for f in films if f["year"] >= 2011]
    assert len(early) == 3 and len(modern) == 5, (len(early), len(modern))
    assert [f["director"] for f in early] == \
        ["Brian De Palma", "John Woo", "J. J. Abrams"], \
        [f["director"] for f in early]
    assert len({f["director"] for f in early}) == 3, "the first three repeat"
    assert [f["director"] for f in modern] == \
        ["Brad Bird"] + ["Christopher McQuarrie"] * 4, \
        [f["director"] for f in modern]
    # every film from Ghost Protocol on is longer than every film before it
    assert min(f["runtime"] for f in modern) > max(f["runtime"] for f in early), \
        (min(f["runtime"] for f in modern), max(f["runtime"] for f in early))
    # the production companies the section break is named after
    studio = data["series_infobox"]["studio"]
    assert "Cruise/Wagner Productions]] (1–3)" in studio, studio
    assert "Skydance]] (4–8)" in studio and "TC Productions]] (4–8)" in studio, \
        studio
    assert all(f["distributor"] == "Paramount Pictures" for f in films), \
        [(f["t"], f["distributor"]) for f in films]
    assert "Fallout, was released on July 27, 2018, and is currently the " \
        "series' highest-grossing entry" in data["lead"], data["lead"]
    assert "based on the 1966 television series created by Bruce Geller" in \
        data["lead"], data["lead"]
    # the retitle, and the consensus this list follows instead
    assert data["part_one_consensus"], \
        "the source dropped its keep-Part-One consensus — recheck the title"
    assert data["retitle_footnote"] == \
        "Retroactively retitled Mission: Impossible – Dead Reckoning upon " \
        "release on streaming platforms.", data["retitle_footnote"]

    # ---- the pairing with tom-cruise, computed rather than hoped for ------
    # These eight films are rows on that list too. If a single title or year
    # disagreed the sync group would not form and a tick on one list would
    # leave the other untouched, so the check is a build gate, not a report —
    # and it runs here, before any row is built, so a drifting title fails
    # with that sentence rather than somewhere downstream.
    mine = {normt(f["t"]) + "|" + str(f["year"]) + "|f": f["t"] for f in films}
    assert len(mine) == 8, sorted(mine)
    shared, elsewhere = {}, {}
    for path in sorted((ROOT / "properties").glob("*.json")):
        if path.stem in ("index", "search", SLUG):
            continue
        q = json.loads(path.read_text(encoding="utf-8"))
        for k, rid, t in film_rows(q):
            if k in mine:
                shared.setdefault(k, []).append((path.stem, rid, t))
                elsewhere.setdefault(path.stem, []).append(t)
    assert set(shared) == set(mine), \
        "no other list carries: %s" % sorted(set(mine) - set(shared))
    assert len(elsewhere.get("tom-cruise", [])) == 8, \
        "tom-cruise does not carry all eight: %s" % elsewhere.get("tom-cruise")
    # The first note names the Tom Cruise list and only that list. A third
    # list picking up one of these films is not a bug, but the note would be
    # wrong, so the build stops and the note gets rewritten with it.
    assert set(elsewhere) == {"tom-cruise"}, \
        "another list now carries these films — rewrite the overlap note: %s" \
        % {k: v for k, v in elsewhere.items() if k != "tom-cruise"}
    for k, hits in shared.items():
        for _, _, t in hits:
            assert t == mine[k], \
                "title drift on %s: %r against %r" % (k, t, mine[k])

    # ---- rows -------------------------------------------------------------
    NOTE = {
        f["t"]: join_bits("Directed by %s" % f["director"]) for f in films
    }
    NOTE[films[0]["t"]] = join_bits(NOTE[films[0]["t"]],
                                    "The shortest of the %s" % WORD[len(films)])
    NOTE["Mission: Impossible – Fallout"] = join_bits(
        NOTE["Mission: Impossible – Fallout"],
        "The series' highest-grossing film")
    NOTE["Mission: Impossible – Dead Reckoning Part One"] = join_bits(
        NOTE["Mission: Impossible – Dead Reckoning Part One"],
        "Retitled Mission: Impossible – Dead Reckoning for streaming")
    NOTE[films[-1]["t"]] = join_bits(NOTE[films[-1]["t"]],
                                     "The longest of the %s" % WORD[len(films)])

    INTRO = {
        "early": "Three films across ten years and three different directors, "
                 "one each: Brian De Palma, John Woo and J. J. Abrams. The "
                 "series infobox names Cruise/Wagner Productions as the "
                 "company on films 1 to 3, and these are those three. None of "
                 "them runs past %d minutes."
                 % max(f["runtime"] for f in early),
        "modern": "Brad Bird's Ghost Protocol, then four in a row from "
                  "Christopher McQuarrie. Skydance and TC Productions come in "
                  "for films 4 to 8, the seventh went out as Part One, and "
                  "every film in this half runs longer than every film in the "
                  "one above it — %d minutes at the shortest here against %d "
                  "at the longest there, climbing to %d for the last."
                  % (min(f["runtime"] for f in modern),
                     max(f["runtime"] for f in early), hi),
    }

    sections, placed = [], []
    for key, title, lo_y, hi_y in ERAS:
        got = [f for f in films if lo_y <= f["year"] <= hi_y]
        assert got, key
        placed += got
        items = [{"id": "mi-%d-%s" % (f["year"], slug(f["t"])),
                  "t": f["t"], "n": str(f["year"]),
                  "w": round(f["runtime"] / 60.0, 2),
                  "note": NOTE[f["t"]]} for f in got]
        sections.append({
            "id": key, "title": title,
            "sub": "%d–%d · %d films · %d hours"
                   % (got[0]["year"], got[-1]["year"], len(got),
                      round(sum(f["runtime"] for f in got) / 60.0)),
            "intro": INTRO[key],
            "items": items,
        })
    sections[0]["open"] = True

    # ---- the arithmetic ---------------------------------------------------
    assert placed == films, "a film was dropped or placed twice"
    rows = [x for s in sections for x in s["items"]]
    assert len(rows) == len(films) == 8, len(rows)
    for s in sections:
        assert all(a["n"] <= b["n"]
                   for a, b in zip(s["items"], s["items"][1:])), \
            "%s is out of year order" % s["title"]
    # a row with no `w` is silently worth one hour, and a row at zero would
    # mix weighted and unweighted rows — neither is allowed on this list
    assert all(isinstance(x["w"], float) and x["w"] > 0 for x in rows), \
        [x["id"] for x in rows if not x.get("w")]
    barsum = round(sum(x["w"] for x in rows), 2)
    assert abs(barsum - hours) < 0.05, (barsum, hours)
    printed = sum(round(sum(f["runtime"] for f in films
                            if a <= f["year"] <= b) / 60.0)
                  for _, _, a, b in ERAS)
    assert printed == round(hours), \
        "section headings add to %d hours, the real total rounds to %d" \
        % (printed, round(hours))

    # separate files, separate id schemes: a shared id would be a real bug
    tc_ids = {rid for _, rid, _ in
              film_rows(json.loads((ROOT / "properties" / "tom-cruise.json")
                                   .read_text(encoding="utf-8")))}
    ours = {x["id"] for x in rows}
    assert not (ours & tc_ids), sorted(ours & tc_ids)
    assert all(i.startswith("mi-") for i in ours), sorted(ours)

    # ---- the accent pair, checked unshipped -------------------------------
    # scratch/mission-impossible/accent.py measures the distances; this is the
    # cheap half of it, and it is here so a hex reused by a list shipped after
    # this one fails the next rebuild rather than going unnoticed.
    taken = {}
    for path in sorted((ROOT / "properties").glob("*.json")):
        if path.stem in ("index", "search", SLUG):
            continue
        q = json.loads(path.read_text(encoding="utf-8"))
        for field in ("accent", "accentDark"):
            if q.get(field):
                taken.setdefault(q[field].upper(), []).append(path.stem)
    for hexes in (ACCENT, ACCENT_DARK):
        assert hexes.upper() not in taken, \
            "%s is already %s's accent" % (hexes, taken[hexes.upper()])

    p = {
        "slug": SLUG,
        "title": "Mission: Impossible",
        "subtitle": "the released films, in release order",
        "kind": "films",
        # A franchise anyone can name, still the biggest thing its star does,
        # and eight films deep — but one series rather than a whole studio or
        # a canon, so it sits below the Tom Cruise list it overlaps and well
        # below the Marvel and Star Wars tier. See POPULARITY.md.
        "popularity": 70,
        "year": "1996–2025",
        "blurb": "Ethan Hunt in the order it happened, %d to %d — %d hours "
                 "and %d minutes, from a %d-minute first outing to a "
                 "%d-minute last one."
                 % (films[0]["year"], films[-1]["year"], mins // 60, mins % 60,
                    lo, hi),
        "unit": {"one": "film", "many": "films"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        # The obvious accents are all spoken for: the bright fuse orange
        # lands 7.7 from Bleach's, the title-card red 1.6 from Mario's, the
        # terminal green 13.4 from Naruto's, the Paramount blue 5.1 from
        # Fallout's. This pair's worst case is 14.6 (Ace Attorney's #F4764B
        # for the dark half; Robin Williams' #8A4A2E at 16.6 for the light)
        # against 17.5 for the freest pair anywhere on the wheel. It is also
        # 72 and 97 away from tom-cruise's teal, which matters most: these
        # eight films sit on that list too and the two pages must not read
        # as the same list.
        "accent": ACCENT,
        "accentDark": ACCENT_DARK,
        "tiers": False,
        "notes": [
            ["These films are on the Tom Cruise list too, on purpose.",
             "Every row here is a row there, and ticking one ticks the other: "
             "film rows pair across lists by title and year, so this is one "
             "set of ticks seen through two doors. The difference is what "
             "holds each list together. That one is an actor's filmography — "
             "Ethan Hunt sits between Jerry Maguire and Eyes Wide Shut on it. "
             "This one is a single story in the order it was told, which is "
             "what you want when you are watching the Missions and nothing "
             "else. Nothing is duplicated and no hours are counted twice, "
             "because each list totals only its own rows."],
            ["Two sections, and the split is at Ghost Protocol.",
             "The series changes character at the fourth film and the sources "
             "say so twice over. The first three have three different "
             "directors and are made by Cruise/Wagner Productions, which the "
             "series infobox marks as films 1 to 3; from Ghost Protocol on "
             "the companies are Skydance and TC Productions for films 4 to 8, "
             "and Christopher McQuarrie directs four in a row. The runtimes "
             "make the same cut on their own: every film from the fourth "
             "onward is longer than every film before it."],
            ["Bar widths are runtimes.",
             "Each film's own Wikipedia infobox, in hours — all %s of them, "
             "nothing estimated, and the generator refuses to build if a "
             "single one fails to parse. %d hours and %d minutes end to end. "
             "The series article's own infobox gives the range as %d–%d "
             "minutes, and those are the first film and the last."
             % (WORD[len(films)], mins // 60, mins % 60, lo, hi)],
            ["The seventh film keeps \"Part One\".",
             "Paramount dropped it for the streaming release — the film is "
             "Mission: Impossible – Dead Reckoning there — but Wikipedia's "
             "series article keeps Dead Reckoning Part One under a talk-page "
             "consensus, and so does the Tom Cruise list here. The two lists "
             "have to spell a title identically for their rows to pair, so "
             "this one follows rather than picks its own. A retitle on one "
             "side and not the other is how a film ends up ticked on one "
             "list and blank on the other."],
            ["Everything released, and nothing that is not.",
             "The Films table on the series article has %s rows and all %s "
             "have come out, so this list is the table. McQuarrie has said "
             "the series will continue, but no further film is titled or "
             "dated, and Cruise said at The Final Reckoning's premiere that "
             "it was his last as Ethan Hunt. The build fails the day a ninth "
             "row appears above."
             % (WORD[len(films)], WORD[len(films)])],
            "Film set, release order and release dates from Wikipedia's "
            "Mission: Impossible (film series) article, read from its Films "
            "table rather than its prose; every runtime from that film's own "
            "Wikipedia infobox.",
        ],
        "sections": sections,
    }

    out = prop.write(p)
    print("wrote %s — %d films, %d min = %.2f hours (prints as %d)"
          % (out.name, len(rows), mins, hours, round(hours)))
    print("   bar widths sum to %.2f hours; section headings print %d"
          % (barsum, printed))
    for s in sections:
        print("   %-28s %d  %s" % (s["title"], len(s["items"]), s["sub"]))
    print("   sync groups shared with tom-cruise:")
    for k in sorted(shared, key=lambda k: mine[k]):
        print("      %-48s %s" % (k, " + ".join(
            "%s/%s" % (sl, rid) for sl, rid, _ in shared[k])))


if __name__ == "__main__":
    main()
