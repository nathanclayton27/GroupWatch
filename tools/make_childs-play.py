#!/usr/bin/env python3
"""Generate properties/childs-play.json.

    PYTHONIOENCODING=utf-8 python tools/make_childs-play.py

Every Child's Play film, and the Chucky television series, in a shape that
shows which things follow which.

WHY THE SERIES IS ON THIS LIST
------------------------------
Because the source says it continues the films. The Child's Play franchise
article's Television section states it outright:

    "The show aired on Syfy and USA Network and shares continuity with the
     original film series, and is a continuation of that story."

and the series' own article names the film it follows: "It serves as a sequel
to the film Cult of Chucky, the seventh installment of the series." A show
that is a continuation of a film line is not a separate property; it is the
rest of the line. check_source() asserts both sentences are still there.

THE FORK, RE-ASSERTED
---------------------
The franchise article's own Films table splits its nine rows into exactly two
labelled blocks, "Original series" and "Reboot", printed in that order, which
never intersect and never overlap in time. That is a fork, not a tangle: no
timeline to rule on, just two lines that start from the same 1988 film and
never touch again. Nothing here is inherited from the combined list this one
replaces — check_source() re-reads the table and asserts the blocks, their
order, their membership and their non-overlap before a row is written.

THE SHAPE
---------
Five sections, and the order is the argument:

    Original series   7 films, 1988-2017      the first line
    Chucky season 1   8 episodes, 2021        |
    Chucky season 2   8 episodes, 2022        | the same line, continued
    Chucky season 3   8 episodes, 2023-24     |
    Reboot            1 film, 2019            the other line, on its own

The television series sits directly under the films it continues rather than
being dumped at the end, and the Reboot sits last, alone, because it connects
to nothing else here. Last is also where the source's own table puts it: the
whole Original series block is printed first, the Reboot block after it, so
the section order mirrors the article's rather than re-sorting by year. A
reader can see which things follow which without being told what happens in
any of them.

WEIGHTS: NONE, AND HERE IS THE RECEIPT
--------------------------------------
The eight films' runtimes are known and machine-read (713 minutes between
them). The 24 episodes' are not, and weights in this repo are all-or-nothing
(a row with no `w` on a weighted list silently counts as one hour, CLU-131),
so `w` comes off every row including the films.

That is a finding, not a shrug. All four places a per-episode length could
live were checked, and `runtime_hunt` in the data file records what each one
returned:

  1. each episode's OWN article - none of the 24 has one. 96 candidate titles
     were probed ("Death by Misadventure", "<title> (Chucky)", "<title>
     (Chucky episode)", "<title> (Chucky season N)"); the 29 that exist are
     either redirects into the season or series article, or the unrelated
     film the episode title homages (Halloween II, Panic Room, Jennifer's
     Body, Final Destination, Dressed to Kill, Death Becomes Her, Let the
     Right One In, There Will Be Blood, Murder at 1600). Not one is a
     television-episode article.
  2. per-episode Wikidata P2047 - Wikidata holds no episode items for this
     series at all. The series item's `has part(s)` reaches only the three
     season items; those carry neither `has part(s)` nor P2047; and of the 17
     items linking to the series or a season, zero are instances of
     "television series episode".
  3. the three season articles - no runtime in any season infobox and no
     minutes figure anywhere in their prose.
  4. the episode tables' own RunTime fields - the {{Episode table}} in each
     season declares no runtime column, and not one of the 24 {{Episode list}}
     blocks carries a RunTime field.

The only figure that exists is the series-level range on the infobox,
"41-54 minutes", and a range applied per episode is an invented number, not a
sourced one. check_source() asserts all four sources are still empty, so a
future run that FINDS a runtime fails this build rather than shipping a stale
claim about having looked.

Data: scratch/agent-chucky/collect.py -> tools/data/childs-play.json, built
from wikitext already cached by the sibling slashers and agent-scream builds;
only the three season articles were fetched, batched into one request. The
runtime hunt is scratch/agent-chucky/hunt_runtimes.py and
hunt_wikidata_deep.py.
"""
import json
import pathlib
import re
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop
from gwlib.prop import slug, normt, join_bits

SLUG = "childs-play"
ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "tools" / "data" / "childs-play.json"

ACCENT, ACCENT_DARK = "#24417A", "#F0788A"

WIKI = "https://en.wikipedia.org/wiki/"

# The list this one replaces. It carries the same eight films, so every film
# row here pairs with one there — which would make the cross-list note read
# "these also sit on Scream & Child's Play" right up until the lead retires
# that list in the same change that ships this one. Excluding it keeps the
# note true of the catalogue this list ships into rather than the one it
# leaves behind. The scan is re-run on every build, so a genuinely new
# neighbour appears in the note by itself.
RETIRED = {"scream-childs-play"}

# Row notes for the films. Terse and spoiler-free: each says what a film IS or
# where it sits in the line, never what happens in it. The block label is NOT
# here — the sections ARE the blocks, and check_source() asserts each film
# landed in the section its table row is printed under.
FILM_NOTES = {
    ("Child's Play", 1988): "The first film.",
    ("Bride of Chucky", 1998):
        "Seven years on, and the first entry not titled Child's Play.",
    ("Seed of Chucky", 2004):
        "Series creator Don Mancini's first film as director; he directs the "
        "rest of this section.",
    ("Curse of Chucky", 2013):
        "Nine years later, and released to video on demand rather than "
        "cinemas.",
    ("Cult of Chucky", 2017):
        "Direct-to-video, as with the film before it, and the last of this "
        "line on film — the television series picks the story up from here.",
    ("Child's Play", 2019):
        "A remake of the 1988 film, and the only entry not written by Don "
        "Mancini or featuring Brad Dourif as Chucky.",
}


MONTHS = ("January February March April May June July August September "
          "October November December").split()
WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
         7: "seven", 8: "eight"}


def episode_note(season, e, halves):
    """A row note for an episode, or "".

    Three structural facts and nothing else: where the continuation starts,
    where the last season breaks in half, and where the show stops. No note
    says what HAPPENS in an episode.

    None of them carries a bare year, and that is load-bearing rather than
    stylistic: build.py falls back to a single year found in a note when a row
    is not numbered by year, so a year here would give an episode called
    "Panic Room" or "Final Destination" a cross-list sync key and let it tick
    the film it borrows its title from. main() asserts no episode row ever
    resolves to a year.
    """
    n = e["in_season"]
    if season == 1 and n == 1:
        return "The series starts here, a sequel to Cult of Chucky."
    if halves and n == halves[0]["episodes"] + 1:
        return ("The season's second half; the first %s aired the previous %s."
                % (WORDS[halves[0]["episodes"]],
                   MONTHS[halves[0]["start"][1] - 1]))
    if season == 3 and n == 8:
        return "Series finale; the show was cancelled after three seasons."
    return ""


def load_json(path, tries=4):
    """Read a JSON file that another builder may be mid-write on."""
    for n in range(tries):
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            if n == tries - 1:
                raise
            time.sleep(0.4)


def released(films):
    return [f for f in films if f["released"]]


def check_source(d):
    """Everything this list asserts about its own sources, before it builds."""
    films = released(d["films"])
    assert len(films) == 8, len(films)

    # --- the fork: two labelled blocks, in the table's own order -----------
    assert d["groups"] == ["Original series", "Reboot"], d["groups"]
    assert not d["chronology"], d["chronology"]      # no timeline to rule on
    blocks = {}
    for f in films:
        assert f["group"], "film row outside every block: %s" % f["label"]
        blocks.setdefault(f["group"], []).append(f["date"][0])
    assert sorted(blocks) == ["Original series", "Reboot"], sorted(blocks)
    assert len(blocks["Original series"]) == 7, len(blocks["Original series"])
    assert len(blocks["Reboot"]) == 1, len(blocks["Reboot"])
    # a clean fork, not a tangle: the blocks never interleave in time
    assert max(blocks["Original series"]) < min(blocks["Reboot"]), blocks
    # ...and the article prints them in the order this list's sections use
    first = {}
    for i, f in enumerate(d["films"]):
        first.setdefault(f["group"], i)
    assert first["Original series"] < first["Reboot"], first

    # --- everything the table names but this list leaves out is unreleased --
    for f in d["films"]:
        assert f["released"] or not f["date"], f["label"]
        assert f["released"] or re.search(r"untitled|\bTBA\b", f["label"],
                                          re.I), f["label"]
        assert f["released"] or "TBA" in f["date_cell"], f["label"]

    # --- every film row is machine-read, and its year checks out -----------
    for f in films:
        assert f["runtime"], "no runtime parsed: %s" % f["label"]
        assert 60 <= f["runtime"] <= 200, (f["label"], f["runtime"])
        assert re.fullmatch(r"\d+ minutes", f["runtime_field"]), \
            (f["label"], f["runtime_field"])
        # the table's release year is one the film's own infobox states — the
        # guard against the reused title (Child's Play 1988 / 2019) pulling
        # the wrong article's runtime
        assert f["date"][0] in f["infobox_years"], \
            (f["label"], f["date"], f["infobox_years"])
    got = [f["date"] for f in films]
    assert got == sorted(got), "the Films table is not in release order"
    reused = [f["label"] for f in films if f["label"] == "Child's Play"]
    assert len(reused) == 2, reused          # the title really is reused

    # --- the facts the film notes state, read from the articles ------------
    for needle, sentence in d["franchise_claims"].items():
        assert sentence, "the franchise article no longer says %r" % needle

    def film(label, year):
        return next(f for f in films
                    if f["label"] == label and f["date"][0] == year)

    orig = [f for f in films if f["group"] == "Original series"]
    named = [f["label"].startswith("Child's Play") for f in orig]
    assert named == [True, True, True, False, False, False, False], named
    assert film("Bride of Chucky", 1998)["date"][0] \
        - film("Child's Play 3", 1991)["date"][0] == 7
    directed = [f["label"] for f in orig if f["director"] == "Don Mancini"]
    assert directed == ["Seed of Chucky", "Curse of Chucky",
                        "Cult of Chucky"], directed
    assert film("Curse of Chucky", 2013)["date"][0] \
        - film("Seed of Chucky", 2004)["date"][0] == 9
    assert film("Curse of Chucky", 2013)["claim"], "no VOD sentence"
    assert film("Cult of Chucky", 2017)["claim"], "no direct-to-video sentence"
    assert film("Child's Play", 2019)["group"] == "Reboot"
    assert film("Cult of Chucky", 2017)["group"] == "Original series"

    # --- the series, and the source's own words on why it belongs here -----
    tv = d["tv"]
    assert tv["seasons"] == 3 and tv["episodes"] == 24, tv
    assert tv["years"] == [2021, 2024], tv["years"]
    assert tv["creator"] == "Don Mancini", tv["creator"]
    cont = d["franchise_claims"]["shares continuity with the original film series"]
    assert "continuation of that story" in cont, cont
    assert "sequel to the film Cult of Chucky" in \
        tv["claims"]["It serves as a sequel to the film"], tv["claims"]
    assert "canceled after three seasons" in \
        tv["claims"]["was canceled after three seasons"], tv["claims"]
    # the series follows the LAST film of the block it continues, not the
    # reboot — the whole reason it is filed under the original line
    assert film("Cult of Chucky", 2017)["date"][0] == max(
        blocks["Original series"])

    # --- the episodes ------------------------------------------------------
    eps = d["episodes"]
    assert len(eps) == 24, len(eps)
    assert [e["overall"] for e in eps] == list(range(1, 25)), \
        [e["overall"] for e in eps]
    for n in (1, 2, 3):
        s = [e for e in eps if e["season"] == n]
        assert len(s) == 8, (n, len(s))
        assert [e["in_season"] for e in s] == list(range(1, 9)), n
        assert all(e["title"] and e["date"] for e in s), n
    dates = [e["date"] for e in eps]
    assert dates == sorted(dates), "episodes are not in broadcast order"
    # the airdates agree with the article's own Series overview windows
    ov = d["overview"]
    for n in (1, 2, 3):
        s = [e for e in eps if e["season"] == n]
        o = ov[str(n)]
        assert o["total"] == 8, (n, o["total"])
        if o["parts"]:
            assert [p["episodes"] for p in o["parts"]] == [4, 4], o["parts"]
            assert s[0]["date"] == o["parts"][0]["start"], (n, s[0]["date"])
            assert s[3]["date"] == o["parts"][0]["end"], (n, s[3]["date"])
            assert s[4]["date"] == o["parts"][1]["start"], (n, s[4]["date"])
            assert s[-1]["date"] == o["parts"][1]["end"], (n, s[-1]["date"])
        else:
            assert s[0]["date"] == o["start"] and s[-1]["date"] == o["end"], n
    assert [bool(ov[str(n)]["parts"]) for n in (1, 2, 3)] == \
        [False, False, True], "which season aired in halves has changed"

    # --- the runtime hunt: all four sources, still empty --------------------
    h = d["runtime_hunt"]
    s1 = h["source1_episode_articles"]
    assert s1["actual_episode_articles"] == 0, s1
    assert s1["candidates_probed"] >= 96, s1
    s2 = h["source2_wikidata"]
    assert s2["episode_items_found"] == 0, s2
    assert s2["episode_items_with_P2047"] == 0, s2
    assert all(not s["P2047"] and not s["has_parts_P527"]
               for s in s2["season_items"]), s2["season_items"]
    assert len(s2["season_items"]) == 3, s2["season_items"]
    assert all(not v for v in h["source3_season_articles"].values()), \
        h["source3_season_articles"]
    s4 = h["source4_runtime_fields"]
    assert s4["blocks with a RunTime field"] == 0, s4
    assert all(s4["season %d article" % n] == 0 for n in (1, 2, 3)), s4
    assert not any(e["has_runtime_field"] for e in eps), "an episode grew one"
    assert not any(e["title_is_wikilinked"] for e in eps), \
        "an episode title is now linked — it may have its own article"
    # the one figure that does exist, and cannot be used: a range, not a length
    assert re.fullmatch(r"\d+[–-]\d+ minutes", h["series_level_range"]), \
        h["series_level_range"]
    assert h["series_level_range"] == tv["runtime_field"], h["series_level_range"]

    return films, eps


def accent_is_free():
    """No other property may share this list's accent pair (qa_lint rule)."""
    for f in sorted((ROOT / "properties").glob("*.json")):
        if f.name in ("index.json", "search.json", "%s.json" % SLUG):
            continue
        p = load_json(f)
        assert (p.get("accent"), p.get("accentDark")) != (ACCENT, ACCENT_DARK), \
            "accent pair already used by %s" % f.stem


def year_of(item):
    """build.py's sync year for a row, reproduced exactly.

    A row syncs on normalized title + year + medium. `n` is a year on the film
    rows and an episode number on the rest, and build.py falls back to a
    SINGLE year found in the note — which is how an episode called "Panic
    Room" or "Final Destination" could quietly tick a film of the same name.
    The generator asserts no episode row ever produces a year, so that whole
    class of collision cannot happen here.
    """
    n = str(item.get("n", ""))
    if re.fullmatch(r"(18|19|20)\d{2}", n):
        return n
    explicit = str(item.get("y", ""))
    if re.fullmatch(r"(18|19|20)\d{2}", explicit):
        return explicit
    found = set(re.findall(r"\b((?:18|19|20)\d{2})\b", item.get("note") or ""))
    return found.pop() if len(found) == 1 else None


def sync_partners(rows, skip=RETIRED):
    """Rows on other lists that would tick together with rows on this one.

    Reproduces build.py's group key exactly — normalized title + year +
    medium, films and games only, secret lists skipped — so the overlap the
    notes describe is the overlap the shipped page will actually have.
    `skip` is the retirement exclusion; pass an empty set to see the catalogue
    as it stands today rather than as it will stand after the retirement.
    Returns {our id: [(slug, id, title)]}.
    """
    want = {}
    for x in rows:
        y = year_of(x)
        if y:
            want["%s|%s|f" % (normt(x["t"]), y)] = x["id"]
    out = {}
    for f in sorted((ROOT / "properties").glob("*.json")):
        if f.name in ("index.json", "search.json", "%s.json" % SLUG):
            continue
        p = load_json(f)
        if p.get("secret") or p["slug"] in skip:
            continue
        kind = p.get("kind") or ""
        if not ("film" in kind or "game" in kind):
            continue
        medium = "g" if "game" in kind else "f"
        for s in p.get("sections", []):
            for x in s.get("items", []):
                y = year_of(x)
                key = "%s|%s|%s" % (normt(x.get("t", "")), y, medium)
                if y and key in want:
                    out.setdefault(want[key], []).append(
                        (p["slug"], x["id"], p["title"]))
    return out


def sync_note(partners, films):
    """The footer note about cross-list ticking, written from the facts."""
    if not partners:
        return ["Nothing here ticks anywhere else.",
                "Ticks sync across clubd wherever two lists carry the same "
                "film and year, and the two Child's Plays — 1988 and 2019 — "
                "are separate rows that would pair separately. As it stands "
                "none of these %d films sits on another list, and the "
                "episodes cannot pair at all, so every row here is ticked "
                "here only. The generator re-checks the whole catalogue each "
                "time it runs, so this note cannot quietly go stale."
                % len(films)]
    bits = []
    for rid in sorted(partners):
        titles = sorted({t for _, _, t in partners[rid]})
        others = (" and ".join(titles) if len(titles) < 3
                  else ", ".join(titles[:-1]) + " and " + titles[-1])
        row = next(x for x in films if x["id"] == rid)
        bits.append("%s (%s) also sits on %s" % (row["t"], row["n"], others))
    return ["Some rows tick on other lists too.",
            "Ticking a film in one place ticks it everywhere it appears: "
            + "; ".join(bits) + ". The episodes pair with nothing — sync is "
            "for films, and a television row has no year to pair on."]


def main():
    d = load_json(DATA)
    films, eps = check_source(d)
    accent_is_free()
    tv, hunt = d["tv"], d["runtime_hunt"]

    def film_row(f):
        year = f["date"][0]
        it = {"id": "cp-%d-%s" % (year, slug(f["label"])),
              "t": f["label"], "n": str(year)}
        note = join_bits(FILM_NOTES.get((f["label"], year)))
        if note:
            it["note"] = note
        return it

    def block_section(sid, group, title, intro, link):
        got = [f for f in films if f["group"] == group]
        items = [film_row(f) for f in got]
        years = [f["date"][0] for f in got]
        sub = ("%d · 1 film" % years[0] if len(got) == 1
               else "%d–%d · %d films" % (years[0], years[-1], len(got)))
        return {"id": sid, "title": title, "sub": sub, "intro": intro,
                "links": [link], "items": items}

    # ---- the first line: the films ---------------------------------------
    original = block_section(
        "original", "Original series", "Original series",
        "The block the franchise article's own filmography prints first, and "
        "seven of its eight released rows. All seven are written or "
        "co-written by series creator Don Mancini, and the line does not end "
        "with them: the television series in the next three sections "
        "continues this story, and the article says so in as many words. "
        "U.S. release order.",
        {"label": "The filmography", "url": WIKI + "Child%27s_Play_(franchise)"})

    # ---- the same line, continued: the series ----------------------------
    # Every date phrase below is derived from the collected airdates, not
    # typed: the gap to Cult of Chucky, the season spans, and the months the
    # last season split across. Prose that repeats a fact the data already
    # holds is prose that drifts away from it.
    gap = eps[0]["date"][0] - next(
        f for f in films if f["label"] == "Cult of Chucky")["date"][0]
    assert gap == 4, gap
    season_sections = []
    for n in (1, 2, 3):
        got = [e for e in eps if e["season"] == n]
        first, last = got[0]["date"], got[-1]["date"]
        span = (str(first[0]) if first[0] == last[0]
                else "%d–%02d" % (first[0], last[0] % 100))
        halves = d["overview"][str(n)]["parts"]
        items = []
        for e in got:
            it = {"id": "cp-s%de%d" % (n, e["in_season"]), "t": e["title"],
                  "n": str(e["in_season"])}
            note = join_bits(episode_note(n, e, halves))
            if note:
                it["note"] = note
            items.append(it)
        intro = ""
        if n == 1:
            intro = ("%s years after Cult of Chucky, and a continuation of it "
                     "rather than a fresh start: the franchise article says "
                     "the show shares continuity with the original film "
                     "series and is a continuation of that story, and the "
                     "series' own article calls it a sequel to that seventh "
                     "film. Same creator, and the same voice in the doll."
                     % WORDS[gap].capitalize())
        elif halves:
            intro = ("The last season, and the only one broadcast in halves — "
                     "%s episodes in %s, %s more the following %s. The show "
                     "was cancelled after it."
                     % (WORDS[halves[0]["episodes"]],
                        MONTHS[halves[0]["start"][1] - 1],
                        WORDS[halves[1]["episodes"]],
                        MONTHS[halves[1]["start"][1] - 1]))
        sec = {"id": "s%d" % n, "title": "Chucky season %d" % n,
               "sub": "%s · %d episodes%s" % (span, len(items),
                                              " in two halves" if halves else ""),
               **({"intro": intro} if intro else {}),
               "links": [{"label": "The season",
                          "url": WIKI + "Chucky_season_%d" % n}],
               "items": items}
        season_sections.append(sec)

    # ---- the other line: the reboot, alone -------------------------------
    reboot = block_section(
        "reboot", "Reboot", "Reboot",
        "The other block the same table prints, and the only film in it. It "
        "remakes the 1988 film rather than following anything, connects to "
        "nothing else on this list, and is the one entry made without the "
        "series creator. It sits last because that is where the article's own "
        "table puts it — after the whole original block — and because putting "
        "it in the middle by year would imply it leads somewhere. It does "
        "not.",
        {"label": "The film", "url": WIKI + "Child%27s_Play_(2019_film)"})

    sections = [original] + season_sections + [reboot]
    original["open"] = True

    # ---- the checks the shipped file has to pass -------------------------
    rows = [x for s in sections for x in s["items"]]
    film_rows = original["items"] + reboot["items"]
    ep_rows = [x for s in season_sections for x in s["items"]]
    assert len(rows) == 32, len(rows)
    assert len(film_rows) == 8 and len(ep_rows) == 24, \
        (len(film_rows), len(ep_rows))
    ids = [x["id"] for x in rows]
    assert len(ids) == len(set(ids)), \
        sorted({i for i in ids if ids.count(i) > 1})
    # the reused title is two distinct rows, and their ids differ by year
    reused = [x["id"] for x in film_rows if x["t"] == "Child's Play"]
    assert reused == ["cp-1988-child-s-play", "cp-2019-child-s-play"], reused

    # every film landed in the section its table row is printed under
    by_id = {film_row(f)["id"]: f for f in films}
    for x in original["items"]:
        assert by_id[x["id"]]["group"] == "Original series", x["id"]
    for x in reboot["items"]:
        assert by_id[x["id"]]["group"] == "Reboot", x["id"]

    # release / broadcast order inside every section
    for s in [original, reboot]:
        years = [int(x["n"]) for x in s["items"]]
        assert years == sorted(years), "%s is out of release order" % s["title"]
    for s in season_sections:
        nums = [int(x["n"]) for x in s["items"]]
        assert nums == list(range(1, 9)), s["id"]

    # all-or-nothing weighting: not one row carries `w`, because 24 of them
    # cannot (see the docstring). A half-weighted list silently counts an
    # unweighted row as one hour.
    assert not any("w" in x for x in rows), \
        [x["id"] for x in rows if "w" in x]

    # no episode row can ever acquire a sync year — see year_of()
    assert not any(year_of(x) for x in ep_rows), \
        [x["id"] for x in ep_rows if year_of(x)]
    assert all(year_of(x) == x["n"] for x in film_rows), film_rows

    partners = sync_partners(rows)
    # The same scan WITHOUT the retirement exclusion, printed rather than
    # written. While the combined list is still on disk its eight rows really
    # do pair with these, and the footer note says otherwise — the warning is
    # how the lead sees that the note is written for the catalogue AFTER the
    # retirement, and that shipping this list without removing that one leaves
    # the note briefly wrong.
    unretired = sync_partners(rows, skip=frozenset())
    mins = sum(f["runtime"] for f in films)
    assert mins == 713, mins

    p = {
        "slug": SLUG,
        "title": "Child's Play",
        "subtitle": "eight films in two lines, and the series that continues "
                    "the first",
        "kind": "films & tv",
        "popularity": 62,
        "year": "1988–2024",
        "blurb": "Chucky in full — seven films and the 24-episode series that "
                 "continues them, plus the 2019 reboot that starts the story "
                 "over. %d entries." % len(rows),
        "unit": {"one": "entry", "many": "entries"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": ACCENT,
        "accentDark": ACCENT_DARK,
        "tiers": False,
        "notes": [
            ["Two lines, and the article draws them.",
             "The franchise's own filmography splits its rows into exactly "
             "two labelled blocks — Original series and Reboot — that never "
             "intersect and never overlap in time. So there is no timeline to "
             "rule on here, only a fork: seven films from 1988 to 2017 in one "
             "line, and a 2019 remake that starts over in the other. The "
             "sections are those blocks, in the order the article prints "
             "them, and both facts are re-read from the table every time this "
             "list is generated."],
            ["The television series continues the first line, so it sits in "
             "it.",
             "The franchise article's own words: the show \"shares continuity "
             "with the original film series, and is a continuation of that "
             "story\". The series' article names the film it follows — a "
             "sequel to Cult of Chucky, the seventh installment — so the "
             "three seasons sit directly under the films they continue "
             "rather than at the end of the page, and the Reboot sits last, "
             "alone, connected to nothing. %d episodes across %d seasons, "
             "%d to %d, cancelled after the third."
             % (tv["episodes"], tv["seasons"], tv["years"][0],
                tv["years"][-1])],
            ["Nothing is weighted, and this is what was checked.",
             "Bars here count entries, not hours. The eight films' runtimes "
             "are known — %d minutes between them, from each film's own "
             "infobox — but not one of the 24 episodes has a length anywhere "
             "in the sources this repo reads, and weights are all-or-nothing: "
             "a row with no weight on a weighted list would silently count as "
             "an hour, so the films give theirs up too. Four places were "
             "searched. Each episode's own article: none of the 24 has one — "
             "%d candidate titles were probed and the %d that exist are "
             "either redirects into a season page or the unrelated film the "
             "episode title borrows. Wikidata: no episode items exist for "
             "this series at all, the three season items carry no runtime, "
             "and none of the %d items linking to them is an episode. The "
             "season articles: no runtime in any infobox, no minutes in any "
             "prose. The episode tables: no runtime column and no RunTime "
             "field in any of the 24 rows. All that exists is one range for "
             "the whole show, %s, and a range spread across 24 episodes is a "
             "number nobody measured. The build re-checks all four and fails "
             "if any of them starts answering, so this list gets weighted the "
             "day the sources can support it."
             % (mins, hunt["source1_episode_articles"]["candidates_probed"],
                hunt["source1_episode_articles"]["titles_that_exist"],
                hunt["source2_wikidata"]["items_linking_to_series_or_seasons"],
                hunt["series_level_range"])],
            ["Not included.",
             "An untitled Chucky film sits in the Original series block with "
             "no release date and no runtime, so it is not a row yet; every "
             "film the table dates is here. The novels, comics, video games "
             "and theme-park attractions the franchise article lists are out "
             "of scope, and so is the 2019 film's own unmade sequel."],
            sync_note(partners, film_rows),
            "Titles, U.S. release dates and the Original series / Reboot "
            "blocks from the Films table of Wikipedia's Child's Play "
            "franchise article; runtimes and directors from each film's own "
            "article infobox; the continuity statement from that article's "
            "Television section; episode numbers, titles and airdates from "
            "the three Chucky season articles, checked against the series "
            "article's own Series overview.",
        ],
        "sections": sections,
    }

    out = prop.write(p)
    print("wrote %s — %d rows (%d films + %d episodes), unweighted"
          % (out.name, len(rows), len(film_rows), len(ep_rows)))
    for s in sections:
        # the section's own sub already carries the span, machine-built from
        # the data — read it back rather than recomputing it a second way
        span = s["sub"].split(" · ")[0]
        print("   %-18s %2d %-6s %-9s no weights  |  %s"
              % (s["title"], len(s["items"]),
                 "row" if len(s["items"]) == 1 else "rows", span, s["sub"]))
    print("   films run %d minutes (%.2f h) by their own infoboxes, carried "
          "as prose not weights" % (mins, mins / 60.0))
    print("   sync groups formed: %s"
          % (", ".join("%s -> %s" % (k, [b for _, b, _ in v])
                       for k, v in sorted(partners.items())) or "none"))
    extra = {k: v for k, v in unretired.items() if k not in partners}
    if extra:
        print("   NOTE: %d row(s) still pair with %s, which this list "
              "replaces — the footer note assumes it is retired in the same "
              "change. %s"
              % (len(extra), ", ".join(sorted(RETIRED)),
                 ", ".join("%s -> %s" % (k, [b for _, b, _ in v])
                           for k, v in sorted(extra.items()))))


if __name__ == "__main__":
    main()
