#!/usr/bin/env python3
"""Generate properties/rurouni-kenshin.json — the 1996 anime, whole.

    python3 tools/make_rurouni-kenshin.py

All 95 television episodes in broadcast order, the 1997 feature film at the
point in the story the source puts it, and both OVA series that add something
the television run does not already contain. 101 rows.

Everything is machine-read from English Wikipedia by
scratch/agent-kenshin/build_data.py; the committed result is
tools/data/kenshin.json, and this file asserts its way through that data
rather than trusting it. Nothing here is typed from memory.

THE 2023 SERIES IS NOT ON THIS LIST, AND IT IS NOT A SECTION OF IT. Its own
article says what it is: "It is the second anime television series adaptation
after the 1996-98 series", and, in production, "The series is a re-adaptation
of the original manga." Different studio (Liden Films), different director,
different cast, its own episode list, and narrative revisions of its own. That
is the fullmetal-alchemist / fma-brotherhood shape exactly — two lists that
point at each other — not the shape of a remake that merely re-tells the same
story inside one list. It is also unfinished: its infobox carries no end date,
47 episodes have aired across two seasons, and Aniplex announced a third
season on March 22, 2025. So it needs its OWN list, and this generator does
not build it. main() asserts all four of those facts, so the day the 2023 run
closes, this file fails and says so.

THE ANIME-ORIGINAL EPISODES ARE MARKED WHERE THE SOURCE MARKS THEM, AND
NOWHERE ELSE. The season 3 article's lead covers episodes 63-95 and says
flatly: "Unlike previous episodes, these were not adapted from the manga." So
every one of those 33 rows carries `Anime-original` — a fact worth having in
front of you while you decide what to watch, and one the source states about
each of them.

Season 2 is the trap. The series article quotes Watsuki saying "The anime's
second season included original stories not found in the manga" — and names
no episode. Fan lists will tell you which ones. Fan consensus is not a source,
so not one row outside season 3 says a word about it, and
no_episode_level_marking() in the data builder asserts the remark still names
no episodes; the day it does, those rows can carry it too.

WHERE THE FILM GOES. The film article states its own place in the story: "The
movie takes place somewhere after the Kyoto arc." The Kyoto arc is season 2 —
three articles call it that — so the film sits in a one-row section between
season 2 and season 3. Its December 20, 1997 release actually fell nine
episodes into season 3's broadcast, between episodes 71 and 72; that is filed
in the section sub so a reader who prefers release order can see it and move.
Story placement wins because that is where you watch it, which is the same
reason the X-Files films sit where they do. The franchise article also calls it
"An anime film with an original story", so it adapts nothing that is already a
row here and double-counts nothing.

TWO OF THE THREE OVA SERIES ARE HERE; THE THIRD IS NOT. The series article
describes all three in one sentence, and that sentence makes the call:

    three series of original video animations (OVAs) were also produced; the
    first adapts stories from the manga that were not featured in the
    television series; the second is both a retelling and a sequel to the
    television series; and the third was a reimagining of the second story arc
    of the series.

  * Trust & Betrayal adapts manga the television series never touched, so it
    is four rows that duplicate nothing.
  * Reflection is a sequel — the franchise article says so outright — so it is
    a row that duplicates nothing either.
  * New Kyoto Arc "remade the series' Kyoto arc", which is episodes 28-62,
    already 35 rows on this list. Carrying it would put the same story on the
    page twice. It is excluded and named in the notes so its absence is a
    statement rather than an oversight.

They sit after the television run, in release order, because that is where and
how the source's own episode list files them: an OVAs section under the three
seasons, Trust & Betrayal (1999) then Reflection (2001-02). It is a prequel
placed second, which looks odd until you notice that watching a prequel first
is a choice about spoilers this list has no business making for you.

Reflection is ONE row, not two. The source's table files it as a single
{{Episode list}} entry with NumParts = 2, one title, two release dates — the
same shape as the X-Files season nine finale, and treated the same way: one
row spanning 1-2.

NOTHING IS WEIGHTED, AND THE HUNT IS THE REASON. CLU-131 is all or nothing,
and 95 of the 101 rows have no verifiable running time anywhere. Every place
one could live was checked, and the result is committed under `runtime_hunt`
in the data file:

  1. the RunTime field of all 102 {{Episode list}} blocks (95 TV + 7 OVA):
     zero of 102 carry one.
  2. the `runtime` field of the three season infoboxes: all three empty.
  3. the series' own Infobox animanga/Video: no `runtime` field at all.
  4. per-episode articles: none exist. Not one of the 95 titles is a wikilink,
     so there is no episode article to read a runtime out of — and therefore
     no per-episode Wikidata item either.
  5. Wikidata P2047: null on the series item (Q11281548), null on all three
     season items (Q6596024/5/6), null on all three OVA items (Q960246,
     Q285971, Q104842469).
  6. Wikidata P179: zero items anywhere declare themselves part of the series,
     confirming (4) from the other side.

The only verified runtime in the whole corpus is the film's — 90 minutes, on
the article and on Wikidata (Q3814643, P577 1997, year-gated). The OVA
articles give lengths in prose (29 minutes, 45 minutes each). Weighting those
six rows and leaving 95 episodes bare is precisely the failure the rule stops:
`WEIGHT = x.w >= 0 ? x.w : 1` bills every unweighted row at one hour, so a
half-hour television run would read as 95 hours. Every row weighs one. The
film and OVA rows carry their lengths as text in the note, where they inform
without doing arithmetic.

THE "SEASONS" ARE AN AMERICAN INVENTION AND THE SOURCE SAYS SO. The list
article's own hatnote: the seasons "correspond to Media Blaster's release of
the series in North America. In Japan, Rurouni Kenshin was aired year-round
continuously... and not split into standard seasonal cycles." The divisions
are kept because the numbering everyone uses rests on them, and the caveat is
in the notes. Only one of the three carries an arc name, because only one is
given one by the source: three separate articles call season 2 the Kyoto arc.
Seasons 1 and 3 are named nowhere, so they stay numbered.

The five live-action films are a different medium and are not here.
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop  # noqa: E402

SLUG = "rurouni-kenshin"
DATA = pathlib.Path(__file__).resolve().parent / "data" / "kenshin.json"

TOTAL_EPISODES = 95
ROWS = 101          # 95 episodes + 1 film + 4 Trust & Betrayal + 1 Reflection

ACCENT = "#8C2A46"       # the deep red-magenta of Kenshin's gi
ACCENT_DARK = "#F27E93"  # ...at the brightness dark mode needs

MONTHS = ["", "January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]

# The seasons the source splits the run into, with what this list knows about
# each beyond its episodes. `arc` is filled only where the source names one.
SEASONS = {
    # %s is the manga volumes the season adapts, read from its own article
    1: {"arc": None,
        "intro": "The opening 27 episodes, adapting %s of the manga. The "
                 "place to start, and where Toonami started."},
    2: {"arc": "the Kyoto arc",
        "intro": "The long middle stretch, adapting %s, and the one run of "
                 "this series the source gives a name. Toonami stopped at the "
                 "end of it."},
    # season 3 adapts no manga at all, so its intro takes no volumes
    3: {"arc": None,
        "intro": "Every episode here is anime-original. The season 3 article "
                 "says so of the whole block: \"Unlike previous episodes, "
                 "these were not adapted from the manga.\" The manga was "
                 "still being written, so the anime went its own way to the "
                 "end."},
}


def datestr(d):
    return "%s %d, %d" % (MONTHS[d[1]], d[2], d[0])


def span(years):
    a, b = min(years), max(years)
    if a == b:
        return str(a)
    return "%d–%02d" % (a, b % 100) if a // 100 == b // 100 else "%d–%d" % (a, b)


def load():
    d = json.loads(DATA.read_text(encoding="utf-8"))
    assert d["total_episodes"] == TOTAL_EPISODES, d["total_episodes"]
    return d


def check_runtime_hunt(hunt):
    """The six places a per-episode running time could have been, all empty.

    This is not decoration. A weighted OVA beside 95 unweighted episodes would
    silently bill each episode at one hour, so the list stays unweighted only
    for as long as every one of these stays empty — and fails loudly the day
    one of them fills in."""
    assert hunt["1_episode_RunTime_fields"] == "0 of 102 blocks", \
        "an episode block now carries a RunTime: %r" \
        % hunt["1_episode_RunTime_fields"]
    assert not any(v.strip() for v in hunt["2_season_infobox_runtime"].values()), \
        "a season infobox now documents a runtime: %r" \
        % hunt["2_season_infobox_runtime"]
    assert hunt["3_series_infobox_runtime"] == "(no field)", \
        "the series infobox now has a runtime: %r" \
        % hunt["3_series_infobox_runtime"]
    assert hunt["4_episodes_with_own_article"] == [], \
        "an episode has an article of its own now — check it for a runtime: " \
        "%r" % hunt["4_episodes_with_own_article"]
    wd = hunt["5_wikidata_P2047"]
    weighted = {p: v["runtime"] for p, v in wd.items() if v["runtime"]}
    assert set(weighted) == {"Rurouni Kenshin: The Motion Picture"}, \
        "Wikidata now carries runtimes for %r — if the series or the seasons " \
        "have one, this list can be weighted and must be" % sorted(weighted)
    assert hunt["6_wikidata_parts_of_series"]["n"] == 0, \
        "%d Wikidata items now declare themselves part of the series — they " \
        "may carry per-episode runtimes" % hunt["6_wikidata_parts_of_series"]["n"]


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


def episode_rows(d, n):
    """One season's rows, with the notes the source supports and no others."""
    rows = []
    for r in d["seasons"][str(n)]["rows"]:
        bits = []
        if n == 3:
            # the source marks this block, and only this block
            bits.append("Anime-original")
        if r["o"] == 1:
            bits.append("Series premiere")
        if r["o"] == 62:
            bits.append("The last episode Toonami aired")
        if r["o"] == 67:
            bits.append("The first episode animated by Studio Deen")
        if r["video_only"]:
            bits.append("Never broadcast — a home-video bonus")
        row = {"id": "rk-%d" % r["o"], "t": r["t"], "n": str(r["o"])}
        note = prop.join_bits(*bits)
        if note:
            row["note"] = note
        rows.append(row)
    return rows


def main():
    d = load()
    check_runtime_hunt(d["runtime_hunt"])
    check_accent()
    prose = d["prose"]

    # --- the decisions, re-asserted against the data before anything builds -
    # 1. the 2023 series is a separate adaptation and stays off this list
    sa = prose["second_adaptation"]
    assert "second anime television series adaptation" in sa["second_adaptation"]
    assert "re-adaptation of the original manga" in sa["re_adaptation"]
    assert sa["studio"] == "Liden Films" and sa["episodes"] == 47, sa
    # 2. only season 3 is marked, and season 2's remark still names no episode
    assert prose["season3_original"] == \
        "Unlike previous episodes, these were not adapted from the manga."
    assert "original stories not found in the manga" in \
        prose["season2_originality_unnamed"]
    # 3. the OVA call rests on one sentence; it must still say all three things
    combined = prose["ova_relationships"]["combined"]
    for phrase in ("the first adapts stories from the manga that were not "
                   "featured in the television series",
                   "the second is both a retelling and a sequel to the "
                   "television series",
                   "the third was a reimagining of the second story arc of "
                   "the series"):
        assert phrase in combined, "the OVA sentence lost %r" % phrase
    assert "remade the series' Kyoto arc" in prose["ova_relationships"]["newkyoto"]
    # and season 2 is what "the Kyoto arc" means, in more than one article
    assert len(prose["kyoto_arc"]) >= 2, prose["kyoto_arc"]

    film = d["film"]
    assert film["released"] == [1997, 12, 20], film["released"]
    assert film["runtime"] == 90, film["runtime"]
    assert film["placement"] == \
        "The movie takes place somewhere after the Kyoto arc."

    # where the film's release date actually fell, computed rather than typed
    s3 = d["seasons"]["3"]["rows"]
    before = [r for r in s3 if r["d"] < film["released"]]
    after = [r for r in s3 if r["d"] > film["released"]]
    assert before and after, "the film no longer opened during season 3"
    assert (before[-1]["o"], after[0]["o"]) == (71, 72), \
        "the film opened between episodes %d and %d" \
        % (before[-1]["o"], after[0]["o"])

    sections = []

    # --- seasons 1 and 2 ----------------------------------------------------
    for n in (1, 2):
        rows = episode_rows(d, n)
        meta = d["seasons"][str(n)]["meta"]
        title = "Season %d" % n
        if SEASONS[n]["arc"]:
            title += ": %s" % SEASONS[n]["arc"]
        sections.append({
            "id": "s%d" % n, "title": title,
            "sub": prop.join_bits(span([r["d"][0] for r in
                                        d["seasons"][str(n)]["rows"]]),
                                  "%d episodes" % len(rows),
                                  "numbered %d–%d" % (int(rows[0]["n"]),
                                                      int(rows[-1]["n"])),
                                  meta["network"]),
            "intro": SEASONS[n]["intro"] % prose["manga_volumes"][str(n)],
            "items": rows,
        })

    # --- the film, after the arc the source says it follows -----------------
    sections.append({
        "id": "film", "title": "The Motion Picture",
        "sub": prop.join_bits(str(film["released"][0]), "one film",
                              "%d minutes" % film["runtime"]),
        "intro": "The one theatrical feature the 1996 series produced, and an "
                 "original story rather than an adaptation of anything else "
                 "on this list. It sits here because its own article says "
                 "\"The movie takes place somewhere after the Kyoto arc\", "
                 "which is the season above. It opened on %s, nine episodes "
                 "into season 3's broadcast — between episodes %d and %d — so "
                 "release order would put it lower down."
                 % (datestr(film["released"]), before[-1]["o"], after[0]["o"]),
        "items": [{
            "id": "rk-film-1997", "t": film["title"],
            "n": str(film["released"][0]),
            "q": film["qid"],
            "note": prop.join_bits("Feature film",
                                   "%d minutes" % film["runtime"],
                                   "also released as %s" % film["alt"]),
        }],
    })

    # --- season 3 -----------------------------------------------------------
    rows = episode_rows(d, 3)
    meta = d["seasons"]["3"]["meta"]
    sections.append({
        "id": "s3", "title": "Season 3",
        "sub": prop.join_bits(span([r["d"][0] for r in s3]),
                              "%d episodes" % len(rows),
                              "numbered %d–%d" % (int(rows[0]["n"]),
                                                  int(rows[-1]["n"])),
                              "all anime-original"),
        "intro": SEASONS[3]["intro"],
        "items": rows,
    })

    # --- the OVAs, in the order the source's own list puts them -------------
    trust = d["ova_episodes"]["trust"]
    tv = d["ovas"]["trust"]
    sections.append({
        "id": "trust", "title": "Trust & Betrayal",
        "sub": prop.join_bits(span([r["dates"][0][0] for r in trust]),
                              "%d episodes" % len(trust),
                              tv["runtime_prose"] + " each", tv["studio"]),
        "intro": "A prequel, and the one part of the manga the television run "
                 "never adapted — the series article says this OVA \"adapts "
                 "stories from the manga that were not featured in the "
                 "television series\". The four parts came out between %s and "
                 "%s, after the series had ended, and they are filed here "
                 "rather than at the top because whether to watch a prequel "
                 "first is your call, not this list's."
                 % (datestr(trust[0]["dates"][0]),
                    datestr(trust[-1]["dates"][0])),
        # Release dates live in the intro, not the row notes. A year inside a
        # row note is a cross-list sync key on a list whose kind contains
        # "film" (see the gate at the foot of main), and these rows are OVA
        # episodes that must never pair with anybody's film.
        "items": [{"id": "rk-tb-%d" % r["n"], "t": r["t"], "n": str(r["n"]),
                   "note": prop.join_bits("OVA", tv["runtime_prose"])}
                  for r in trust],
    })

    ref = d["ova_episodes"]["reflection"][0]
    rv = d["ovas"]["reflection"]
    assert len(ref["dates"]) == 2, ref
    sections.append({
        "id": "reflection", "title": "Reflection",
        "sub": prop.join_bits(span([y for y, _m, _d in ref["dates"]]),
                              "two episodes, one entry",
                              rv["runtime_prose"], rv["studio"]),
        "intro": "A sequel to the television series, released two years after "
                 "the OVA above — %s and %s. The source files both parts as a "
                 "single entry with one title, so it is one row spanning 1–2."
                 % (datestr(ref["dates"][0]), datestr(ref["dates"][1])),
        "items": [{
            "id": "rk-ref-1", "t": ref["t"], "n": "1–2",
            "note": prop.join_bits(
                "OVA", "two parts, filed as one entry by the source",
                rv["runtime_prose"]),
        }],
    })

    sections[0]["open"] = True

    # --- the counts, and the two rules a slip here would break --------------
    assert [s["id"] for s in sections] == \
        ["s1", "s2", "film", "s3", "trust", "reflection"], \
        [s["id"] for s in sections]
    total = sum(len(s["items"]) for s in sections)
    assert total == ROWS, "%d rows, expected %d" % (total, ROWS)
    eps = sum(len(s["items"]) for s in sections if s["id"].startswith("s"))
    assert eps == TOTAL_EPISODES, "%d episode rows, expected %d" \
        % (eps, TOTAL_EPISODES)
    assert sum(1 for s in sections for x in s["items"] if "w" in x) == 0, \
        "a weight crept in — this list is unweighted end to end"
    assert sum(1 for x in sections[3]["items"]
               if x.get("note", "").startswith("Anime-original")) == 33, \
        "season 3 lost its anime-original notes"
    assert not any("Anime-original" in (x.get("note") or "")
                   for s in sections if s["id"] != "s3" for x in s["items"]), \
        "a row outside season 3 claims to be anime-original — the source " \
        "marks no such episode"

    # Cross-list tick sync pairs film-kind rows on title+year, falling back to
    # a single year found in the note (src/build.py `_year_of`). This list's
    # kind contains "film", so EVERY row is scanned — and a stray year in an
    # episode note would mint a key that ticks somebody else's film. Exactly
    # one row here may carry a year, and it is the film.
    for s in sections:
        for x in s["items"]:
            if x["id"] == "rk-film-1997":
                continue
            assert not re.fullmatch(r"(18|19|20)\d{2}", x["n"]), \
                "%s numbers itself with a year" % x["id"]
            assert not re.search(r"\b(18|19|20)\d{2}\b", x.get("note") or ""), \
                "%s leaks a year into its note — cross-list sync would " \
                "read it as a film release year: %r" % (x["id"], x["note"])

    p = {
        "slug": SLUG,
        "title": "Rurouni Kenshin",
        "subtitle": "the 1996 anime, the film, and the OVAs",
        "kind": "anime & film",
        "popularity": 70,
        "year": "1996–2002",
        "blurb": "All 95 episodes of the Meiji-era wanderer in broadcast "
                 "order, the original-story film where the source puts it, "
                 "and the two OVAs that add something the series does not.",
        "unit": {"one": "entry", "many": "entries"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": ACCENT,
        "accentDark": ACCENT_DARK,
        "tiers": False,
        "notes": [
            ["The 2023 series is a different adaptation and gets its own "
             "list.",
             "It is not a section of this one and not a remake folded into "
             "it. Its own article calls it \"the second anime television "
             "series adaptation after the 1996–98 series\" and \"a "
             "re-adaptation of the original manga\" — new studio, new "
             "director, new cast, its own episode list, its own revisions to "
             "the story. That is two lists pointing at each other, the way "
             "Fullmetal Alchemist and Brotherhood are two lists. It is also "
             "still running: 47 episodes across two seasons, no end date, and "
             "a third season announced in March 2025."],
            ["Season 3 is anime-original, and the source says which episodes.",
             "The article covering episodes 63–95 puts it plainly: \"Unlike "
             "previous episodes, these were not adapted from the manga.\" The "
             "manga's own final arc was still being written, so the anime "
             "wrote its own ending. Every row in that section says so."],
            ["Nothing else is marked, on purpose.",
             "Watsuki is quoted saying the second season \"included original "
             "stories not found in the manga\", and no source here names "
             "which. Fan lists will tell you. They are not a source, so no "
             "row outside season 3 claims to be anime-original. If Wikipedia "
             "ever marks them, this list will."],
            ["The film sits after the Kyoto arc because that is where the "
             "source puts it.",
             "Its article says \"The movie takes place somewhere after the "
             "Kyoto arc\", and three articles call season 2 the Kyoto arc. "
             "The film actually opened on December 20, 1997, nine episodes "
             "into season 3's broadcast — between episodes 71 and 72 — so "
             "release order would place it lower; story order is what you "
             "watch by. It is an original story, so it adapts nothing else on "
             "this page."],
            ["Two of the three OVA series are here.",
             "One sentence in the series article decides it: the first OVA "
             "\"adapts stories from the manga that were not featured in the "
             "television series\", the second \"is both a retelling and a "
             "sequel\", and the third \"was a reimagining of the second story "
             "arc of the series\". So Trust & Betrayal and Reflection are "
             "here, and New Kyoto Arc (2011–12) is not: it \"remade the "
             "series' Kyoto arc\", which is already 35 rows above. Listing it "
             "would put the same story on this page twice."],
            ["Reflection is one row for two episodes.",
             "Not an editorial choice — the source's own table files it as a "
             "single entry with one title and two release dates, so it is one "
             "row spanning 1–2. That is 101 rows covering 102 entries."],
            ["The \"seasons\" are an American invention.",
             "The source flags this itself: the seasons \"correspond to Media "
             "Blaster's release of the series in North America. In Japan, "
             "Rurouni Kenshin was aired year-round continuously… and not "
             "split into standard seasonal cycles.\" They are kept because "
             "the episode numbering everybody uses rests on them. Only season "
             "2 carries an arc name, because it is the only stretch the "
             "source names."],
            ["Episodes are numbered the way the source states its facts.",
             "Each television row carries its number across the whole run, "
             "which is why season 3 starts at 63 rather than at 1. Every fact "
             "worth knowing about this series is stated that way — Toonami "
             "stopped at 62, Studio Deen took over at 67, the anime-original "
             "block is 63 to 95 — and a row you cannot line up with those is "
             "a row that has lost the point."],
            ["Toonami stopped two thirds of the way through.",
             "Cartoon Network began the series on March 17, 2003 and ended at "
             "episode 62. Episodes 63–95 never aired in the US and came out "
             "on DVD instead — and episode 95 never aired in Japan either, as "
             "a home-video bonus. All of it is here."],
            ["Nothing is weighted, and that took some looking.",
             "Wikipedia documents no running time for this series anywhere: "
             "not one of the 102 episode blocks has a RunTime field, none of "
             "the three season infoboxes has a runtime, the series infobox "
             "has no such field at all, not one of the 95 episodes has an "
             "article of its own to read one from, and Wikidata's series, "
             "season and OVA items all return nothing for running time. The "
             "one verified figure in the whole corpus is the film's 90 "
             "minutes. Weighting six rows and leaving 95 bare would be worse "
             "than weighting none, because an unweighted row silently counts "
             "as a full hour — a half-hour series would read as 95 hours. So "
             "every row counts one, and the film and OVA rows give their "
             "lengths in the note instead."],
            ["The live-action films are a different medium.",
             "Five of them exist, from 2012 to 2021. This list is the anime."],
            "Titles, numbering and airdates machine-read from Wikipedia's "
            "three Rurouni Kenshin season articles and its episode list; the "
            "film, OVA and remake facts from the 1996 series, franchise, "
            "film and OVA articles; runtimes checked against Wikidata. Every "
            "season's count is asserted against both the list article's "
            "series overview and the season article's own infobox, the "
            "overall numbering asserted contiguous 1–95, and every sentence "
            "quoted above asserted still present before this builds.",
        ],
        "sections": sections,
    }

    out = prop.write(p)
    print("wrote %s — %d rows in %d sections (%d episodes, 1 film, 5 OVA rows)"
          % (out.name, total, len(sections), eps))
    for s in sections:
        print("   %-26s %3d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
