#!/usr/bin/env python3
"""Generate properties/fullmetal-alchemist.json — the 2003 anime and its film.

    python3 tools/make_fullmetal-alchemist.py

This is the FIRST of the manga's two anime adaptations. `fma-brotherhood`
already ships and is the second one. They share a beginning and then do not:
Wikipedia's article on this series says the manga was still running during
production, that Arakawa asked for an ending of its own, and that this "led
to the anime deviating into an entirely original story direction around the
first dozen episodes". The Brotherhood article puts the same fact from the
other side — Brotherhood "was conceived to create a faithful adaptation that
directly follows the entire story from the original manga, as the first anime
adaptation strayed away from it".

Naming WHERE that happens is a fact about the adaptation and a reader
choosing between the two needs it. Naming WHAT changes is a spoiler. This
file does the first only, and nothing on the page — no row note, no section
sub — does the second.

Scope, all decided from the sources and not from memory:

  IN   the 51 episodes (2003-10-04 .. 2004-10-02) and Conqueror of Shamballa
       (2005), which the film's own article calls "a direct sequel and
       conclusion to the original Fullmetal Alchemist television series".

  OUT  The Sacred Star of Milos (2011). Its article's Development section
       says the producers wanted "a Fullmetal Alchemist movie set during the
       second anime's storyline" — that is Brotherhood's continuity, not this
       one's, and Brotherhood's infobox lists it as the related film.
  OUT  the recap special Reflections and the four Premium Collection OVAs.
       The episode list files them in a separate "Recap and OVAs" table
       outside the 1-51 numbering, and says of the OVAs that "the majority
       of these OVAs are side stories and do not expand on the plot".
  OUT  the live-action films (2017, and its two 2022 sequels) — a different
       medium adapting the manga directly, "covering the first four volumes
       of the original storyline".
  OUT  the manga.

Sections are the four opening-theme runs the episode list's lead documents
(1-13, 14-25, 26-41, 42-51), machine-read into the meta file. The series has
no arc names of its own and Wikipedia files it as a single season, so these
runs are the only structure the source itself draws across the 51 episodes.
The first of them happens to end where the divergence is dated, which is why
the note about it sits on the second section rather than anywhere else.

NOTHING IS WEIGHTED, and that is a finding rather than an omission — see the
runtime hunt recorded in the notes and in the WEIGHTS comment below.

Data: tools/data/fullmetal-alchemist_episodes.json (51 episodes, machine-read
from the {{Episode list}} blocks of "List of Fullmetal Alchemist episodes"),
and tools/data/fullmetal-alchemist_meta.json (the film's facts from its own
infobox, cross-checked against Wikidata P2047; the four opening-theme runs
from the episode list's lead). Both written by scratch/agent-fma03/.
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop  # noqa: E402

SLUG = "fullmetal-alchemist"
DATA = pathlib.Path(__file__).resolve().parent / "data"

# WEIGHTS — deliberately none, per CLU-131's all-or-nothing rule. The hunt for
# a per-episode runtime, source by source, all four of them empty:
#
#   1. the episode table's own RunTime fields ....... 0 in the whole article
#   2. each episode's own Wikipedia article ......... none exists. Probing all
#      51 titles bare and disambiguated (102 pages) returned not one
#      {{Infobox television episode}}; 40 of the titles are redirects into
#      the episode list itself and the rest are unrelated articles.
#   3. per-episode Wikidata P2047 ................... the series item Q711257
#      enumerates no episodes (no P527) and carries no P2047 of its own; a
#      Wikidata search across all 51 titles found an item for exactly one
#      episode (Q135840839, episode 1, P2047 = 24 min). One of 51.
#   4. season articles .............................. none. The series infobox
#      says num_seasons = 1 and Wikipedia has no per-season article to hold a
#      runtime column.
#
# The series infobox does carry a nominal "23 minutes", but that is one figure
# for the series, not 51 sourced episodes, so it is not used as a weight.
#
# The film's 105 minutes IS sourced twice over (its infobox and Wikidata
# P2047 = 105, P577 = 2005). Shipping it as the one weighted row beside 51
# unweighted ones is exactly the failure the rule stops: an unweighted row
# counts as one hour, so the strip would claim the series ran 51 hours. Every
# row therefore counts one, and the film's runtime lives in its row note.
WEIGHTED = False

# SYNC — build.py makes every row of a "film"-bearing kind a sync candidate,
# and a row with no year in `n` still gets one from a note that names exactly
# one year. Two different continuities sharing a tick is the failure mode
# here, so no episode note may contain a year; asserted below.
YEAR = re.compile(r"\b(?:18|19|20)\d{2}\b")

MONTH = ["", "January", "February", "March", "April", "May", "June", "July",
         "August", "September", "October", "November", "December"]


def span(rows):
    """`October-December 2003` / `July 2004-October 2004`, from air dates."""
    a, b = rows[0]["d"], rows[-1]["d"]
    (ay, am), (by, bm) = (a[:4], int(a[5:7])), (b[:4], int(b[5:7]))
    if ay == by:
        return "%s–%s %s" % (MONTH[am], MONTH[bm], ay)
    return "%s %s–%s %s" % (MONTH[am], ay, MONTH[bm], by)


def main():
    eps = json.loads((DATA / ("%s_episodes.json" % SLUG)).read_text("utf-8"))
    meta = json.loads((DATA / ("%s_meta.json" % SLUG)).read_text("utf-8"))
    film = meta["film"]

    assert [r["e"] for r in eps] == list(range(1, 52)), "numbering not 1-51"
    assert film["year"] == 2005 and film["runtime_min"] == 105, film

    # row notes: what an entry IS, never what happens in it
    NOTES = {
        1: "Series premiere",
        42: "Aired the same day as episode 41",
        51: "Series finale — the film picks up from here",
    }

    by_num = {r["e"]: r for r in eps}
    sections = []
    for i, b in enumerate(meta["blocks"], 1):
        rows = [by_num[n] for n in range(b["first"], b["last"] + 1)]
        sections.append({
            "id": "part%d" % i,
            "title": "Episodes %d–%d" % (b["first"], b["last"]),
            "sub": "%s · %d episodes" % (span(rows), len(rows)),
            "items": [{"id": "fma03-%d" % r["e"], "t": r["t"],
                       "n": str(r["e"]),
                       **({"note": NOTES[r["e"]]} if r["e"] in NOTES else {})}
                      for r in rows],
        })
    sections[0]["open"] = True

    # The one thing this list exists to say, and the only place it says it.
    sections[1]["intro"] = (
        "Around here the adaptation leaves the manga behind. Wikipedia dates "
        "this series' move into an original story direction to around the "
        "first dozen episodes; from roughly this point on, it and Brotherhood "
        "are not telling the same story. What changes is not on this page.")

    sections.append({
        "id": "film",
        "title": "Conqueror of Shamballa",
        "sub": "2005 · the sequel film, and the end of this continuity",
        "items": [{"id": "fma03-film-2005", "t": film["title"],
                   "n": str(film["year"]),
                   "note": "%d min · a direct sequel to the series"
                           % film["runtime_min"]}],
    })

    for s in sections[:-1]:
        for x in s["items"]:
            assert not YEAR.search(x.get("note") or ""), \
                "a year in an episode note would give %s a sync key" % x["id"]
    assert not WEIGHTED and not any("w" in x for s in sections
                                    for x in s["items"]), "unweighted list"

    prop_ = {
        "slug": SLUG,
        "title": "Fullmetal Alchemist (2003)",
        "subtitle": "the first anime adaptation, and the film that ends it",
        "kind": "anime & film",
        "popularity": 73,
        "year": "2003–2005",
        "blurb": "The manga's first anime adaptation — 51 episodes and "
                 "the sequel film that closes them.",
        "unit": {"one": "entry", "many": "entries"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": "#8A4500",
        "accentDark": "#D9903F",
        "tiers": False,
        "notes": [
            ["Two anime, one manga.", "This is the 2003 series, the first "
             "adaptation of Hiromu Arakawa's manga. Fullmetal Alchemist: "
             "Brotherhood (2009) is the second and has its own page at "
             "?p=fma-brotherhood. Wikipedia calls Brotherhood an independent "
             "second adaptation that directly follows the events of the manga "
             "and ignores the original anime's continuity. Which of the two "
             "to watch is not a question this list answers."],
            ["Where they part.", "The manga was still being published while "
             "this series was in production and Arakawa asked for an ending "
             "of its own, which Wikipedia says led to the anime deviating "
             "into an entirely original story direction around the first "
             "dozen episodes. That is the where. The what is a spoiler, so "
             "no note on this page names it."],
            ["The film belongs to this continuity.", "Conqueror of Shamballa "
             "is a direct sequel to this series and the conclusion of its "
             "story, which is why it is here. The Sacred Star of Milos (2011) "
             "is not: its own article records it as a film set during the "
             "second anime's storyline, which is Brotherhood's."],
            ["What else is out.", "The recap special Reflections and the four "
             "Premium Collection OVAs, which the episode list files outside "
             "the 1–51 numbering and describes as side stories that do "
             "not expand on the plot. The live-action films (2017, and two "
             "sequels in 2022) adapt the manga directly in another medium. "
             "The manga itself is not tracked here."],
            ["Nothing is weighted.", "No per-episode runtime for this series "
             "is published anywhere machine-readable. The episode table "
             "carries no RunTime fields; no episode has an article of its own "
             "(40 of the 51 titles are redirects into the episode list); "
             "Wikipedia files the series as one season, so there are no "
             "season articles; and Wikidata has an item for one episode out "
             "of 51. The film's 105 minutes is sourced and confirmed, but a "
             "single weighted row beside 51 unweighted ones would have the "
             "strip claim an episode takes an hour — so every row counts "
             "one, and the film's runtime sits in its note instead."],
            ["Sections are the broadcast runs.", "The series has no arc names "
             "of its own, so the four sections are the opening-theme runs the "
             "episode list documents — 1–13, 14–25, "
             "26–41 and 42–51. Episodes 41 and 42 share an air "
             "date; that is what the source records."],
            "Episode titles and air dates machine-read from Wikipedia's List "
            "of Fullmetal Alchemist episodes; the film's date and runtime "
            "from its own article and Wikidata; the 1–51 numbering "
            "asserted complete before this builds.",
        ],
        "sections": sections,
    }

    out = prop.write(prop_)
    total = sum(len(s["items"]) for s in sections)
    print("wrote %s — %d rows (%d episodes + 1 film), unweighted"
          % (out.name, total, total - 1))
    for s in sections:
        print("   %-16s %3d  %s" % (s["title"][:16], len(s["items"]),
                                    s.get("sub", "")))


if __name__ == "__main__":
    main()
