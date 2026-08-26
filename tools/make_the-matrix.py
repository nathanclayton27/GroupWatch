#!/usr/bin/env python3
"""Generate properties/the-matrix.json.

    PYTHONIOENCODING=utf-8 python tools/make_the-matrix.py

Four films, The Animatrix, and the two games that survive the gate — seven
rows in one run, each sitting where the story puts it. Every fact below is
read out of tools/data/matrix.json, collected by scratch/agent-matrix/collect.py
from Wikipedia wikitext, Wikidata P2047 and HowLongToBeat. Nothing here is
typed from memory; the asserts re-check every claim the prose makes.

THE GAMES ARE A GATE, NOT A ROSTER
----------------------------------
Nathan asked for "the games that are worth playing too". Turned into a rule a
row can be tested against, that is: **playable today, and part of this story.**
Two halves, and each half does work.

  Enter the Matrix (2003)     in. Wikipedia: its story "is concurrent with"
                              Reloaded, it carries "over an hour of original
                              footage, written and directed by the Wachowskis
                              and starring the cast of the films", and the
                              franchise article says that footage was shot
                              during the filming of the two 2003 films.
  The Matrix: Path of Neo      in. "Players control the character Neo,
  (2005)                      participating in scenes from the films" —
                              the trilogy replayed from inside it.
  The Matrix Online (2005)     OUT on the first half. The franchise article
                              says it "continued the story beyond The Matrix
                              Revolutions" — it passes the second half
                              outright — and its own article says Sony Online
                              Entertainment "shut down operation of the game
                              on July 31, 2009". It cannot be played at any
                              price. HowLongToBeat knows the game and carries
                              no main-story figure for it either, so there is
                              not even a number to argue about.
  The Matrix Awakens (2021)    OUT on both halves: a "technology
                              demonstration" made to promote Resurrections,
                              and "delisted on July 9, 2022".

Placement is the other half of the ruling. A game row sits with the films, in
the story's order — Enter the Matrix between The Animatrix and Reloaded,
because the anthology's Osiris short "sets up the prologue" for it and its own
story runs alongside Reloaded. Filing the games in a section at the bottom
would remove the only reason to have them on this list rather than on a games
list of their own.

THE ANIMATRIX: ONE ROW, AND IT LEADS 2003
-----------------------------------------
Granularity is decided by the source, not by taste. Wikipedia files The
Animatrix as a single film — one {{Infobox film}}, one runtime, one release
date — and the franchise article lists it once. Its Plot section has nine
subsections and its Staff table eight rows naming seven directors, and neither
carries a runtime for any individual short. Nine rows would therefore be nine
rows that cannot be weighted, and on a weighted list a row with no `w` is
silently worth one hour (CLU-131). So: one row, weighted whole.

Placement mattered more, and the source places it. Wikipedia says "Kid's Story
takes place during the six-month gap between The Matrix and The Matrix
Reloaded", and that Final Flight of the Osiris ends by setting up Enter the
Matrix's prologue. Both put the anthology ahead of the May 2003 pair, so it
leads the 2003 section rather than trailing it at the complete DVD's June 3
date — and Osiris had already played in cinemas with Dreamcatcher that March,
before Reloaded. This is the babylon-5 rule applied to an anthology: file it
where the source puts it, do not append it.

THE TWO 2003 FILMS
------------------
Release order sequences them on its own, but two adjacent rows read as a
sequel and its sequel. The franchise article says what they are: Reloaded and
Revolutions "were filmed simultaneously during one shoot (under the project
codename 'The Burly Man'), and released in two parts in 2003". That sentence
is the section title and both row notes, so the pairing is legible on the page
rather than inferred from the dates.

WEIGHTS
-------
All-or-nothing. Every row carries a `w`:

  films  Wikidata P2047, in minutes, each gated on a P577 publication year
         within a year of the release date the film's own article gives. Four
         of the five agree with their article exactly; The Animatrix does not
         (97 against 102) and keeps to the one source, as the rest of the
         catalogue does.
  games  HowLongToBeat main-story hours through gwlib.hltb, behind the
         mandatory verify-by-name gate. Both verified on name and year.

Mixing film hours and game hours in one total is deliberate and already
happens elsewhere; the games are the larger share here, and the notes say so.

WHAT HAS NO ROW
---------------
A fifth film is in development with Drew Goddard writing and directing. The
source gives it no release date — not even a year — so under the announced-work
rule it stays off, rather than shipping as a `w: 0` row. The moment Wikipedia
carries a date, this file grows a zero-weight row and the assert below is what
will say so.

A NOTE FOR WHOEVER TOUCHES THE SYNC KEYS
----------------------------------------
build.py derives a row's sync medium from the PROPERTY's kind string —
`medium = "g" if "game" in kind else "f"` — so a list that is honestly both
mediums can only be one of them. This list's kind names games, which is true
and is what puts it under the games chip on the card wall, and the consequence
is that its FILM rows ride the game lane. Nothing is broken by that today:
no other list in the catalogue carries any Matrix film or any Matrix game, so
no cross-list group forms either way. It would matter the day a canon film
list picked up The Matrix, so `sync_report()` below raises then instead of
letting the pairing fail in silence. The fix at that point is one line in
build.py's MEDIA_FIX (the hatch nasuverse already uses) plus kind "films" —
not a rename of any id here.

Data:   scratch/agent-matrix/fetch.py -> scratch/agent-matrix/wiki/
        scratch/agent-matrix/collect.py -> tools/data/matrix.json
Accent: scratch/agent-matrix/accent.py
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

SLUG = "the-matrix"
ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "tools" / "data" / "matrix.json"

# key, medium, display title, year, section
ROSTER = [
    ("The Matrix", "film", 1999, "first"),
    ("The Animatrix", "film", 2003, "burlyman"),
    ("Enter the Matrix", "game", 2003, "burlyman"),
    ("The Matrix Reloaded", "film", 2003, "burlyman"),
    ("The Matrix Revolutions", "film", 2003, "burlyman"),
    ("The Matrix: Path of Neo", "game", 2005, "after"),
    ("The Matrix Resurrections", "film", 2021, "after"),
]

SECTIONS = ["first", "burlyman", "after"]


# --------------------------------------------------------------------------
# the cross-list overlap, computed rather than remembered
# --------------------------------------------------------------------------
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


def catalogue_rows():
    """[(slug, medium, normalized title, year, display title)] for every
    syncable row already shipped, read off disk so this cannot go stale."""
    out = []
    for f in sorted((ROOT / "properties").glob("*.json")):
        if f.stem in ("index", "search", SLUG):
            continue
        p = json.loads(f.read_text(encoding="utf-8"))
        if p.get("secret"):
            continue
        kind = p.get("kind") or ""
        if not ("film" in kind or "game" in kind):
            continue
        medium = "g" if "game" in kind else "f"
        for s in p.get("sections", []):
            for x in s.get("items", []):
                y = year_of(x, str(x.get("n", "")))
                if y:
                    out.append((p["slug"], medium, normt(x["t"]), y, x["t"]))
    return out


def sync_report(mine, medium):
    """Groups this list would join, and the one that must never appear.

    `mine` is [(normalized title, year, medium of the work)]. The list ships
    under one property medium (see the module docstring), so the groups that
    actually form are the ones matching THAT letter. A film sibling on a
    film-kind list is the case the medium choice would silently break, so it
    raises instead.
    """
    shipped = catalogue_rows()
    forms, would_have = {}, {}
    for title, year, own in mine:
        for oslug, omedium, otitle, oyear, odisp in shipped:
            if (otitle, oyear) != (title, year):
                continue
            key = "%s|%s|%s" % (title, year, omedium)
            (forms if omedium == medium else would_have).setdefault(
                key, []).append((oslug, odisp, own))
    assert not [k for k, v in would_have.items()
                if any(own == "film" for _s, _d, own in v)], (
        "a Matrix FILM now appears on a film-kind list (%s) while this list "
        "rides the '%s' medium, so the two would not pair. Move this list to "
        "kind 'films' and add {\"the-matrix\": [\"movies\", \"games\"]} to "
        "MEDIA_FIX in src/build.py — do not rename any id here."
        % (sorted(would_have), medium))
    return forms, would_have


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    films = {f["t"]: f for f in data["films"]}
    games = {g["t"]: g for g in data["games"]}
    claims = data["claims"]
    anim = data["animatrix"]

    def said(page, key, *musts):
        """A sentence the source gave us, re-checked for what we quote of it."""
        s = claims[page][key]
        for m in musts:
            assert m in s, "%s.%s no longer says %r: %r" % (page, key, m, s)
        return s

    # ---- the films: one source, one value each, every gate passed ----------
    assert len(films) == 5, sorted(films)
    for t, f in films.items():
        assert f["qid"] and f["year_gate"] and f["pubyears"], f
        assert f["runtime"], "unweighted film row: %s" % t
        vals = {s["amount"] for s in f["p2047_seen"]}
        assert len(vals) == 1, \
            "%s grew a second runtime %s — pick one and say why" % (t, vals)
        assert float(f["runtime"]) in vals, (t, f["runtime"], vals)
        assert all(s["unit"] == "Q7727" for s in f["p2047_seen"]), f
    # four of five match their own article exactly; The Animatrix is the one
    # that does not, and the notes name it rather than blending the sources
    drift = {t: (f["runtime"], f["stated_runtime"]) for t, f in films.items()
             if f["stated_runtime"] != f["runtime"]}
    assert set(drift) == {"The Animatrix"}, drift
    assert drift["The Animatrix"] == (97, 102), drift

    # ---- release dates, and the pair they make -----------------------------
    us = {t: f["release_dates"][-1] for t, f in films.items()}
    assert us["The Matrix Reloaded"] == "2003-05-15", us
    assert us["The Matrix Revolutions"] == "2003-11-05", us
    assert us["The Animatrix"] == "2003-06-03", us
    d = lambda s: datetime.date(*(int(x) for x in s.split("-")))
    gap = (d(us["The Matrix Revolutions"]) - d(us["The Matrix Reloaded"])).days
    assert 150 < gap < 183, gap          # under six months, not seven
    assert (d(us["The Matrix Resurrections"]).year
            - d(us["The Matrix Revolutions"]).year) == 18
    # the anthology's complete release falls between the two films; its stories
    # and its first public showing do not, which is why the row leads instead
    assert us["The Matrix Reloaded"] < us["The Animatrix"] \
        < us["The Matrix Revolutions"], us

    burly = said("The Matrix (franchise)", "burly_man",
                 "filmed simultaneously during one shoot",
                 "The Burly Man", "released in two parts in 2003")
    said("The Matrix Revolutions", "back_to_back", "shot back-to-back with")
    said("The Matrix Reloaded", "filming",
         "concurrently with the filming of the second sequel")
    said("The Matrix (franchise)", "trilogy_backed",
         "backed up the initial idea of making a trilogy")
    said("The Matrix", "registry", "National Film Registry", "In 2012")
    oscars = said("The Matrix", "oscars", "Best Visual Effects",
                  "Best Film Editing", "Best Sound",
                  "Best Sound Effects Editing")
    assert oscars.count(",") == 2 and " and " in oscars, oscars

    # ---- The Animatrix: what the source's own structure allows -------------
    assert len(anim["plot_segments"]) == 9, anim["plot_segments"]
    assert anim["plot_segments"][0] == "Final Flight of the Osiris", \
        anim["plot_segments"]
    directors = sorted({r["director"] for r in anim["staff_rows"]})
    assert len(anim["staff_rows"]) == 8 and len(directors) == 7, \
        (len(anim["staff_rows"]), directors)
    # the whole granularity argument: no per-short runtime exists to weigh
    # nine rows with, and an unweighted row on this list would be worth an
    # hour by default
    assert not anim["per_segment_runtimes"], \
        "the source grew per-short runtimes — nine rows are now possible"
    said("The Animatrix", "lead", "nine animated short films")
    said("The Matrix (franchise)", "animatrix_is",
         "collection of nine animated short films")
    said("The Matrix (franchise)", "animatrix_when",
         "to coincide with the release of The Matrix Reloaded")
    gap_claim = said("The Animatrix", "kids_gap",
                     "takes place during the six-month gap between "
                     "The Matrix and The Matrix Reloaded")
    said("The Animatrix", "osiris_sets_up",
         "sets up the prologue for the video game Enter the Matrix")
    said("The Animatrix", "osiris_theaters", "was shown in theaters with")
    said("The Animatrix", "dvd_release", "June 3, 2003")

    # ---- the gate, applied to each game ------------------------------------
    said("Enter the Matrix", "lead",
         "its story is concurrent with that of the film The Matrix Reloaded",
         "over an hour of original footage",
         "starring the cast of the films")
    said("The Matrix (franchise)", "enter_shot",
         "featured scenes that were shot during the filming of "
         "The Matrix Reloaded and The Matrix Revolutions")
    said("The Matrix (franchise)", "enter_when",
         "released in North America concurrently with The Matrix Reloaded")
    said("The Matrix: Path of Neo", "lead",
         "Players control the character Neo, participating in scenes from "
         "the films")
    said("The Matrix: Path of Neo", "gameplay",
         "guiding the character through the events of The Matrix trilogy")
    # the exclusions, each with the sentence that excludes it
    said("The Matrix Online", "discontinued", "is a discontinued")
    said("The Matrix Online", "shutdown",
         "shut down operation of the game on July 31, 2009")
    said("The Matrix (franchise)", "online_continued",
         "continued the story beyond The Matrix Revolutions")
    said("The Matrix Awakens", "tech_demo", "technology demonstration")
    said("The Matrix Awakens", "delisted", "delisted on July 9, 2022")
    said("The Matrix Revisited", "documentary",
         "documentary film about the production of the 1999 film")
    said("The Matrix Comics", "free_web", "originally presented for free on")
    fifth = said("The Matrix (franchise)", "fifth_film",
                 "A fifth film is currently in development", "Drew Goddard")
    # announced work may ship a w:0 row when the source dates it. This one is
    # undated, so it stays off — and stops staying off the day that changes.
    assert not re.search(r"\b(19|20)\d{2}\b", fifth.split("==")[0]), \
        "the fifth film now carries a date — it earns a w:0 row: %r" % fifth

    # ---- the two games, verified by name and year --------------------------
    for t in ("Enter the Matrix", "The Matrix: Path of Neo"):
        g = games[t]
        assert g["why"] == "ok" and g["main_h"], g
        assert g["hltb_name"] == t, g
        assert abs(int(g["hltb_year"]) - g["year"]) <= 1, g
    mxo = games["The Matrix Online"]
    assert mxo["hltb_name"] == "The Matrix Online" and not mxo["main_h"], mxo
    assert "no main-story figure" in mxo["why"], mxo

    # ---- rows ---------------------------------------------------------------
    NOTES = {
        "The Matrix": "Four Academy Awards, and in the National Film Registry "
                      "since 2012",
        "The Animatrix": "Nine animated shorts by seven directors, counted as "
                         "one film. It leads 2003 because its stories do — one "
                         "is set in the gap between the first two films, and "
                         "Final Flight of the Osiris sets up the next row's "
                         "prologue",
        "Enter the Matrix": "Shot with the cast during the same production as "
                            "the two 2003 films — over an hour of original "
                            "footage written and directed by the Wachowskis. "
                            "Its story runs concurrent with Reloaded",
        "The Matrix Reloaded": "First of two halves filmed simultaneously in "
                               "one shoot, codenamed The Burly Man, and "
                               "released in two parts in 2003",
        "The Matrix Revolutions": "The other half, out under six months later; "
                                  "the two were shot back-to-back",
        "The Matrix: Path of Neo": "A game that replays the trilogy's own "
                                   "scenes with Neo under your control; the "
                                   "Wachowskis wrote and co-directed it",
        "The Matrix Resurrections": "Eighteen years after Revolutions, and "
                                    "directed by Lana Wachowski alone",
    }

    rows, by_section = [], {k: [] for k in SECTIONS}
    for title, medium, year, sec in ROSTER:
        if medium == "film":
            w = round(films[title]["runtime"] / 60.0, 2)
        else:
            w = games[title]["main_h"]
        x = {"id": "mtx-%d-%s" % (year, slug(title)), "t": title,
             "n": str(year), "w": w}
        note = join_bits(NOTES[title])
        if note:
            x["note"] = note
        rows.append((x, medium, year))
        by_section[sec].append(x)

    assert len(rows) == 7, len(rows)
    # every row weighs something: a missing w is silently one hour, and a 0 is
    # reserved for announced work the source has dated (there is none here)
    assert all(isinstance(x["w"], float) and x["w"] > 0 for x, _m, _y in rows), \
        [x["id"] for x, _m, _y in rows if not x["w"]]
    ids = [x["id"] for x, _m, _y in rows]
    assert len(ids) == len(set(ids)), ids

    hours = round(sum(x["w"] for x, _m, _y in rows), 2)
    film_h = round(sum(x["w"] for x, m, _y in rows if m == "film"), 2)
    game_h = round(sum(x["w"] for x, m, _y in rows if m == "game"), 2)
    assert abs(film_h + game_h - hours) < 0.01, (film_h, game_h, hours)
    assert game_h > film_h, (game_h, film_h)   # the notes say so

    # ---- sections -----------------------------------------------------------
    INTROS = {
        "first": ("The first film", "1999",
                  "One film, and no trilogy yet — the franchise's own history "
                  "says its mainstream success is what backed the idea of "
                  "making one. Everything below came out of a single shoot "
                  "four years later."),
        "burlyman": ("2003: one shoot, four releases", "2003",
                     "Reloaded and Revolutions were filmed simultaneously "
                     "during one shoot, codenamed The Burly Man, and released "
                     "in two parts in 2003 — one story in halves, not a sequel "
                     "and its sequel. The same production shot the live-action "
                     "footage for Enter the Matrix, whose story runs alongside "
                     "the first half. The Animatrix leads rather than trails: "
                     "its shorts sit in the gap before Reloaded, and one of "
                     "them sets the game's prologue up."),
        "after": ("After the trilogy", "2005–2021",
                  "Sixteen years between these two: a game that replays the "
                  "trilogy from inside it, and the film that came back to it. "
                  "A fifth film is in development with Drew Goddard writing "
                  "and directing, and the source gives it no date, so it has "
                  "no row here yet."),
    }

    sections = []
    for key in SECTIONS:
        items = by_section[key]
        assert items, key
        title, span, intro = INTROS[key]
        h = sum(x["w"] for x in items)
        sections.append({
            "id": key, "title": title,
            "sub": "%s · %d %s · %d hours"
                   % (span, len(items),
                      "entry" if len(items) == 1 else "entries", round(h)),
            "intro": intro, "items": items})
    sections[0]["open"] = True

    years = [int(x["n"]) for s in sections for x in s["items"]]
    assert years == sorted(years), years

    # ---- what this list shares with the rest of the catalogue ---------------
    KIND = "films & games"
    medium = "g" if "game" in KIND else "f"
    mine = [(normt(x["t"]), x["n"], m) for x, m, _y in rows]
    forms, would_have = sync_report(mine, medium)

    p = {
        "slug": SLUG,
        "title": "The Matrix",
        "subtitle": "four films, nine shorts and the games worth playing",
        # films AND games, and build.py reads this string for both the medium
        # chips and the sync medium — see the docstring before changing it
        "kind": KIND,
        # Band 80-89: a mainstream audience recognises the title on sight, and
        # the first film's vocabulary is in ordinary speech. Four films rather
        # than a decades-long serial, so it sits under James Bond (88) and
        # Star Trek (92) and over Godzilla (80) and Christopher Nolan (80),
        # level with Breaking Bad and Spielberg. See POPULARITY.md.
        "popularity": 83,
        "year": "1999–2021",
        "blurb": "Four films, The Animatrix and the two games still worth "
                 "playing — seven entries, about %d hours, each sitting where "
                 "the story puts it." % round(hours),
        "unit": {"one": "entry", "many": "entries"},
        "verb": {"base": "watch and play", "past": "done",
                 "ing": "working through"},
        # measured in CIE76 against every accent in properties/index.json —
        # 188 lists, 376 accents, when this was picked; see
        # scratch/agent-matrix/accent.py. The phosphor green of the digital
        # rain itself is unusable at 26.8 from FPS Canon's dark accent, and
        # the screen-green cast of the films lands 6.0 from the Muppets and
        # 7.9 from Rick and Morty; the ships' cold blue is 2.4 from Vinland
        # Saga's and the sunglasses brass 1.4 from Star Wars Games'. This
        # deep-code / phosphor pair is the free spot inside the series' own
        # colour: worst-case 15.0, against 17.5 for the freest pair anywhere
        # on the wheel — which is a magenta with nothing to do with the films.
        # Nearest neighbours are Attack on Titan's #2B5032 and Breaking Bad's
        # #2E5F2E for the light, Naruto (manga)'s #5FE06B for the dark.
        "accent": "#0C3B0C",
        "accentDark": "#26AE38",
        "tiers": False,
        "notes": [
            ["Films and games on one list, on purpose.",
             "The gate for a game is: playable today, and part of this story. "
             "Two pass. Enter the Matrix was shot with the cast during the "
             "same production as the 2003 films and its story runs concurrent "
             "with Reloaded; Path of Neo replays the trilogy's own scenes with "
             "Neo under your control. Both sit where the story puts them, next "
             "to the films, rather than in a section at the bottom — that "
             "placement is the only reason to carry them here instead of on a "
             "games list. They are also the larger share of the time: about "
             "%d of the %d hours." % (round(game_h), round(hours))],
            ["What the gate leaves out.",
             "The Matrix Online is the one that hurts. It passes the second "
             "half outright — the franchise article says it continued the "
             "story beyond Revolutions — and fails the first: Sony Online "
             "Entertainment shut its servers down on 31 July 2009, so it "
             "cannot be played at any price, however anyone rates it. "
             "HowLongToBeat does not carry a main-story figure for it either. "
             "The Matrix Awakens (2021) fails both halves: a technology "
             "demonstration made to promote Resurrections, delisted on 9 July "
             "2022. The Matrix Revisited (2001) is a documentary about the "
             "making of the first film, not part of the story. The comics are "
             "out because this list is films and games — they went out free on "
             "the series' website between 1999 and 2003 and were collected in "
             "print later, and they are their own thing."],
            ["The Animatrix is one row, and it leads 2003.",
             "Wikipedia files it as a single film — one infobox, one runtime, "
             "one release date — and gives a runtime for none of the nine "
             "shorts individually. Nine rows would therefore be nine rows that "
             "cannot be weighted, and on a weighted list a row carrying no "
             "figure is silently worth an hour. Placement mattered more, and "
             "the source decides that too: Kid's Story is set in the six-month "
             "gap between the first two films, and Final Flight of the Osiris "
             "ends by setting up Enter the Matrix's prologue. So the anthology "
             "sits ahead of both rather than at the June date its complete DVD "
             "carries — and Osiris had already played in cinemas that March, "
             "before Reloaded."],
            ["Bar widths, and the one number that disagrees.",
             "Film hours are Wikidata runtimes, each gated on a release year "
             "within a year of the film's own article, and every film here "
             "carries exactly one value. Game hours are HowLongToBeat "
             "main-story figures, verified against the name and the year. Four "
             "of the five films' runtimes match their articles to the minute. "
             "The Animatrix does not — Wikidata says 97 minutes and the "
             "article says 102 — and the row keeps to the one source rather "
             "than becoming a blend of two, the same rule the rest of this "
             "catalogue follows."],
            ["A fifth film has no row yet.",
             "Wikipedia says one is in development with Drew Goddard writing "
             "and directing and Lana Wachowski executive producing. It names "
             "no release date, not even a year, so there is nothing to place. "
             "A row appears the day a date does."],
            "Films, shorts and games from Wikipedia — The Matrix (franchise) "
            "and each work's own article; runtimes from Wikidata, gated on a "
            "matching release year; game hours from HowLongToBeat, verified "
            "by name.",
        ],
        "sections": sections,
    }

    out = prop.write(p)
    print("wrote %s — %d entries, %.2f hours (%.2f film, %.2f game)"
          % (out.name, len(ids), hours, film_h, game_h))
    for s in sections:
        print("   %-28s %d  %s" % (s["title"], len(s["items"]), s["sub"]))
    print("   sync groups formed: %s"
          % (", ".join(sorted(forms)) if forms else "none — no other list "
             "carries a Matrix film or game"))
    if would_have:
        print("   same-title rows in the OTHER medium lane: %s"
              % sorted(would_have))
    print("   burly man: %s" % burly[:96])
    print("   animatrix: %s" % gap_claim[:96])


if __name__ == "__main__":
    main()
