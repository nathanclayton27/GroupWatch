#!/usr/bin/env python3
"""Generate properties/bond-games.json.

    python3 tools/make_bond_games.py

The licensed James Bond video games from GoldenEye 007 onward, on their own
page. The 27 films are the `bond` list and are untouched by this; games and
films sit on separate pages here for the same reason star-wars-games does.

Where the data comes from. Wikipedia's "List of James Bond video games" is a
redirect to "James Bond in video games", and that article carries no
wikitable at all — it is prose under era headings. The enumeration lives in
the navbox it transcludes, {{James Bond video games}}, whose groups ARE the
publisher eras. So scratch/bondgames/collect.py reads three machine sources
and writes scratch/bondgames/games.json:

  * the navbox bullet lists          -> which games exist, and under whom
  * the article's === era headings === -> the year range of each era
  * each game's own {{Infobox video game}} -> release year, developer, genre

and then HowLongToBeat main-story figures through gwlib.hltb's
verify-by-name gate.

The sections are the article's own eras, and this generator asserts the two
enumerations still agree: every game's release year must land inside the era
belonging to its navbox publisher group. Wikipedia re-cutting an era, or
moving a game between publishers, fails the build rather than quietly
shipping a game filed under the wrong decade. The article's series infobox is
checked against the roster's last row for the same reason — that infobox
already contradicts the article once, dating the first Bond game to 1982
while the article's own first era heading starts at 1983.

Four of the eighteen ship UNWEIGHTED, and the reason is in games.json rather
than in anyone's head. HowLongToBeat files all three of Wikipedia's separate
World Is Not Enough games (Nintendo 64, PlayStation, Game Boy Color — three
studios, two genres) under one entry, and files the Game Boy Advance
Everything or Nothing under the 2004 console game's entry. A single figure
that covers several different games cannot be handed to any one of them, so
those rows carry no weight at all. A guessed number would go straight into
real pace calculations.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from gwlib import prop  # noqa: E402

SLUG = "bond-games"
DATA = pathlib.Path(__file__).resolve().parent.parent / "scratch" / \
    "bondgames" / "games.json"

# The navbox's own platform shorthand, spelled out. Rows whose title repeats
# inside the list get the qualifier appended so no two rows read the same;
# the rest drop it (the navbox uses "(1998)" purely to disambiguate a link).
PLATFORM = {
    "N64": "Nintendo 64",
    "PS": "PlayStation",
    "GBC": "Game Boy Color",
    "GBA": "Game Boy Advance",
}

# Section titles and intros, keyed by the era heading the article uses. Every
# era that ends up holding games must appear here, so a renamed heading is a
# build failure and not a blank section title.
ERA_COPY = {
    "Nintendo era": (
        "The Nintendo years",
        "Rare turns a film licence into a landmark on the Nintendo 64, and "
        "Nintendo follows it with a Game Boy game built by Saffire."),
    "Electronic Arts era": (
        "The Electronic Arts years",
        "Eleven games in seven years and the widest the catalogue ever got: "
        "film tie-ins, three separate World Is Not Enough games by three "
        "studios, a racer, and a spin-off."),
    "Activision era": (
        "The Activision years",
        "A film tie-in, an original thriller, a remake of the Nintendo 64 "
        "game, and an anniversary compilation. Activision let the licence go "
        "in 2013."),
    "IO Interactive era": (
        "IO Interactive",
        "Announced as Project 007 in 2020 and unveiled under its real name "
        "five years later — the Hitman studio's original Bond, and the first "
        "licensed Bond game since 2012."),
}

# One editorial line per row: what the game IS. The studio on the end of each
# is the lead developer read out of that game's own infobox, not typed here.
NOTE = {
    "GoldenEye 007":
        "The Nintendo 64 first-person shooter that made the licence matter",
    "James Bond 007 (1998 video game)":
        "Game Boy action-adventure with casino minigames built in",
    "Tomorrow Never Dies (video game)":
        "Third-person shooter with stealth, on PlayStation",
    "007 Racing":
        "The one that is a driving game, on PlayStation",
    "The World Is Not Enough (Nintendo 64 video game)":
        "First-person shooter — the Nintendo 64 version, built in GoldenEye's "
        "shadow",
    "The World Is Not Enough (PlayStation video game)":
        "First-person shooter with stealth — a different game from the "
        "Nintendo 64 version, sharing only the title",
    "The World Is Not Enough (Game Boy Color video game)":
        "Top-down action-adventure — the handheld take, different again",
    "James Bond 007: Agent Under Fire":
        "First-person shooter with rail and driving sections; an original "
        "story, no film behind it",
    "James Bond 007: Nightfire":
        "First-person shooter across three consoles, with a substantially "
        "different PC version",
    "James Bond 007: Everything or Nothing (Game Boy Advance video game)":
        "A separate handheld game sharing the console version's title",
    "James Bond 007: Everything or Nothing":
        "Third-person action-adventure with driving, and a cast recorded with "
        "the film actors' voices and likenesses",
    "GoldenEye: Rogue Agent":
        "A first-person shooter spin-off — you do not play Bond in it",
    "From Russia with Love (video game)":
        "Third-person shooter adapting the 1963 film, with Sean Connery "
        "recorded for it",
    "007: Quantum of Solace":
        "Film tie-in shot in first person with third-person cover",
    "James Bond 007: Blood Stone":
        "Third-person shooter with an original story, and the last game its "
        "studio finished",
    "GoldenEye 007 (2010 video game)":
        "The remake of the 1997 game, rebuilt for the Wii with a new script",
    "007 Legends":
        "First-person shooter assembled from six films at once, for the "
        "franchise's fiftieth",
    "007 First Light":
        "Action-adventure, and the first Bond game built as an original story "
        "since 2010",
}


def display(g):
    """Row title: the navbox's own display name, plus its platform qualifier
    where the qualifier is what tells two rows apart."""
    plat = PLATFORM.get(g["qual"])
    return "%s (%s)" % (g["t"], plat) if plat else g["t"]


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    games = data["games"]
    eras = data["eras"]
    series = data["series_infobox"]

    # --- the two enumerations must still agree -------------------------
    for g in games:
        hit = [e for e in eras if e["lo"] <= g["year"] <= e["hi"]]
        assert len(hit) == 1, \
            "%s (%d) lands in %d eras" % (g["t"], g["year"], len(hit))
        g["era"] = hit[0]["name"]
        if g["group"] in ("Nintendo", "Electronic Arts", "Activision"):
            assert g["era"] == g["group"] + " era", (
                "navbox files %s under %s but its %d release lands in the "
                "article's %s" % (g["t"], g["group"], g["year"], g["era"]))
        assert g["era"] not in ("Early era", "Hiatus"), (
            "%s (%d) fell into %s — the roster starts at GoldenEye 007 and "
            "the hiatus is meant to be empty"
            % (g["t"], g["year"], g["era"]))

    # The article's summary infobox against the article's own enumeration:
    # if a newer game is announced and only one of them is updated, stop.
    last = games[-1]
    assert series["latest_release_version"] == last["t"], (
        "infobox calls %r the latest game; the navbox roster ends at %r"
        % (series["latest_release_version"], last["t"]))
    assert series["latest_release_date"] == str(last["year"]), (
        "infobox dates the latest game %s; its own article says %d"
        % (series["latest_release_date"], last["year"]))
    for pub in ("Nintendo", "Electronic Arts", "Activision", "IO Interactive"):
        assert pub in series["publishers"], \
            "%s is a section here but no longer a listed publisher" % pub

    # --- rows ----------------------------------------------------------
    rows = []
    for g in games:
        assert g["page"] in NOTE, "no note written for %r" % g["page"]
        note = prop.join_bits(NOTE[g["page"]], g["developer"])
        row = {"id": "bondg-%d-%s" % (g["year"], prop.slug(display(g))),
               "t": display(g), "n": str(g["year"]), "note": note,
               "era": g["era"], "year": g["year"]}
        if g["hltb_hours"] is not None:
            assert 0 < g["hltb_hours"] < 300, \
                "absurd weight on %s: %r" % (g["t"], g["hltb_hours"])
            row["w"] = g["hltb_hours"]
        else:
            assert g["hltb_why"], "unweighted %s with no reason" % g["t"]
        rows.append(row)

    years = [r["year"] for r in rows]
    assert years == sorted(years), "roster is out of release order"

    unweighted = [r for r in rows if "w" not in r]
    assert len(unweighted) == 4, (
        "expected the four rows HowLongToBeat cannot tell apart, got %d: %s"
        % (len(unweighted), [r["t"] for r in unweighted]))

    # --- sections ------------------------------------------------------
    sections = []
    for era in eras:
        got = [r for r in rows if r["era"] == era["name"]]
        if not got:
            continue
        assert era["name"] in ERA_COPY, \
            "the article grew an era with games in it and no copy: %r" \
            % era["name"]
        title, intro = ERA_COPY[era["name"]]
        hours = sum(r.get("w", 0) for r in got)
        span = ("%d" % got[0]["year"] if got[0]["year"] == got[-1]["year"]
                else "%d–%d" % (got[0]["year"], got[-1]["year"]))
        nw = sum(1 for r in got if "w" not in r)
        sections.append({
            "id": prop.slug(era["name"]).replace("-era", ""),
            "title": title,
            "sub": prop.join_bits(
                span,
                "%d game%s" % (len(got), "" if len(got) == 1 else "s"),
                "%d hours story" % round(hours) if hours else "",
                "%d unweighted" % nw if nw else ""),
            "intro": intro,
            "items": [{k: v for k, v in r.items()
                       if k in ("id", "t", "n", "w", "note")} for r in got],
        })
    sections[0]["open"] = True

    assert len(sections) == 4, "expected four populated eras, got %d" \
        % len(sections)
    assert sum(len(s["items"]) for s in sections) == len(games), \
        "a game fell out of the sections"

    hours = sum(r.get("w", 0) for r in rows)
    weighted = len(rows) - len(unweighted)

    p = {
        "slug": SLUG,
        "title": "James Bond Games",
        "subtitle": "the licensed games, GoldenEye 007 onward",
        "kind": "games",
        "order": 116,
        "year": "%d–%d" % (rows[0]["year"], rows[-1]["year"]),
        "blurb": "%d games in release order, grouped by who held the licence "
                 "— Nintendo, EA, Activision, and now IO Interactive. About "
                 "%d hours of story across the %d with a verified figure."
                 % (len(rows), round(hours), weighted),
        "unit": {"one": "game", "many": "games"},
        "verb": {"base": "play", "past": "played", "ing": "playing"},
        "itemOrder": "number-first",
        "accent": "#7D5C8A",
        "accentDark": "#E6BEF4",
        "tiers": False,
        "notes": [
            ["The films are a separate list.", "The 25 Eon films and the two "
             "made outside Eon live on their own page. The games follow the "
             "licence rather than the film series: some adapt a film, most of "
             "the later ones do not, and the two lines only occasionally meet."],
            ["Where this starts, and what is not here.", "GoldenEye 007 in "
             "1997 is where the games start being a thing people finish. The "
             "1983–1994 run of 8-bit tie-ins that came before it is a "
             "different hobby and is not on this page, and neither are the "
             "mobile-only games, the fan remakes, the cancelled ones, or "
             "re-releases of something already listed — GoldenEye 007: "
             "Reloaded in 2011 is the 2010 game again."],
            ["Hours are story only.", "HowLongToBeat main-story figures, "
             "verified by name against the game they belong to. %d of the %d "
             "rows carry one; they add up to about %d hours."
             % (weighted, len(rows), round(hours))],
            ["Four rows carry no hours at all.", "HowLongToBeat files all "
             "three World Is Not Enough games as a single entry, and files "
             "the Game Boy Advance Everything or Nothing under the console "
             "game's. One figure covering several different games cannot "
             "honestly be given to any one of them, so those four rows count "
             "as one entry each and wear no number. The bar stays honest and "
             "a finish date paces you by count across them."],
            ["Three games called The World Is Not Enough.", "They are not "
             "ports of each other. Eurocom built the Nintendo 64 one, Black "
             "Ops built the PlayStation one, and 2n Productions built the "
             "Game Boy Color one as a top-down game — three studios, two "
             "genres, one title. Wikipedia gives each its own article and so "
             "does this list."],
            ["The gap between 2012 and 2026.", "Activision's licence was "
             "revoked in 2013 and nothing licensed shipped for the rest of "
             "the decade. The empty stretch is real, which is why there is no "
             "section for it."],
            "Roster from the navbox on Wikipedia's James Bond in video games "
            "(the article Wikipedia's list of James Bond video games "
            "redirects to, and which has no table of its own); years, "
            "developers and genres from each game's own article; hours from "
            "HowLongToBeat, verified by name.",
        ],
        "sections": sections,
    }

    out = prop.write(p)
    print("wrote %s" % out.name)
    print("  %d sections, %d games, %d weighted (%d hours), %d unweighted"
          % (len(sections), len(rows), weighted, round(hours),
             len(unweighted)))
    for s in sections:
        print("   %-26s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))
    for r in unweighted:
        print("   unweighted: %s (%s)" % (r["t"], r["n"]))


if __name__ == "__main__":
    main()
