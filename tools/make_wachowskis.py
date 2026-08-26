#!/usr/bin/env python3
"""Generate properties/wachowskis.json.

    PYTHONIOENCODING=utf-8 python tools/make_wachowskis.py

Every film Lana and Lilly Wachowski wrote or directed, in release order, with
the credit on the row. Everything here is machine-read from
tools/data/wachowskis.json, collected by scratch/agent-wachowski/collect.py
from Wikipedia's "The Wachowskis" article — its ==Works== tables, its lead,
and its four career subsections — plus each film's own article for the
runtime and the director, and Wikidata for a work id per row. Nothing is
typed in from memory, and every claim the copy makes is asserted against the
data that produced it before anything is written.

THE CREDIT RULE, AND WHY IT IS THIS ONE
---------------------------------------
The Works section's ==Films== table has three credit columns — Directors,
Writers, Producers — and the rule is read straight off two of them:

    A film is a row here when that table marks them Directors or Writers on
    it, and the row says which.

That is 11 of the table's 19 rows. Both neighbouring rules are worse, and the
table itself is what shows it:

  * **"Everything they directed"** is 8 films. It drops Assassins, which is
    the first credit on the whole filmography; V for Vendetta, which their
    own article's infobox lists among their notable works; and The Animatrix.
    A reader who came for the Wachowskis would find the three most obviously
    missing things missing.
  * **"Everything they wrote"** is those same 11, because the table marks
    them Writers on every single film it marks them Directors on — there is
    no film here they directed from someone else's script. So the two rules
    differ by exactly three films, and stating the rule as "wrote or
    directed" costs nothing and says the true thing.
  * **"Everything with their name on it"** would take all 19, and eight of
    those are producer credits on other people's films — a documentary about
    their own first film, Ninja Assassin, two shorts, and the run of
    executive-producer credits Lilly has taken since 2025. Producing is not
    authorship and this list does not track it.

The rule is stated on the page in plain words, every row carries its credit,
and everything the rule excludes is named below and in the property's notes.

WHERE IT IS ONE SISTER, THE ROW SAYS SO
---------------------------------------
The table flags this itself and the rows follow it: The Matrix Resurrections
is {{yes|Lana}} in all three columns, and its note says Lana made it without
Lilly. It is the only row on the list that is one of them rather than both —
Lilly's solo work is all television or producing, which this list does not
carry, and both facts are named in the notes rather than left as a hole.
Cloud Atlas gets the same treatment from the other direction: the table's own
Notes column says "Co-directed with Tom Tykwer", so the row does too.

WHAT FALLS OUT, AND WHY (eight of the table's 19 rows)
------------------------------------------------------
  * **The Invasion** (2007) — the Writers column is {{partial|Uncredited}}
    and the article says outright that the Wachowskis are not credited on the
    film. An uncredited rewrite is the source drawing the line, not this
    file: a writing credit has to mean something.
  * **The Matrix Revisited** (2001) — executive producer only, and the
    table's Notes column marks it "Documentary".
  * **Ninja Assassin** (2009) — producer only.
  * **Google Me Love** (2014) — executive producer only; the Notes column
    marks it a short film.
  * **Castration Movie Anthology ii** and **Dolls** (both 2025), **Again
    Again** (2026), **Trash Mountain** (no year) — executive producer, Lilly.
    Trash Mountain is also the one place the source contradicts itself: the
    prose says Lilly would direct it, the Works table says executive producer
    and gives the year as TBA. Either reading leaves it off — undated work
    gets no row, because there is nothing to place.

No announced film clears the credit rule, so no row here carries w: 0.

NO TELEVISION, AND SENSE8 IS WHAT THAT COSTS
--------------------------------------------
The source keeps television in its own table with its own columns, and that
is the line this list takes. It costs two things and names both: Sense8,
which they created with J. Michael Straczynski and which is as much theirs as
anything on the page, and the two episodes of Work in Progress that Lilly
wrote and directed. The other reason is the bar: every row here is weighted
in hours from one source, and the source publishes no per-episode runtime for
Sense8 at all — the series infobox gives "46-151 minutes" across 24 episodes
and nothing finer. Twenty-four unweighted rows would outnumber the films two
to one on a list of films and would take the hours figure with them. The
games, the comics and the music video are out for the first reason alone:
each is its own table.

WEIGHTS: ONE SOURCE, THE FILM'S OWN INFOBOX
-------------------------------------------
Every bar is the running time stated in that film's own Wikipedia infobox, in
hours. All 11 have exactly one such figure, so nothing is adjudicated and no
row goes unweighted. Wikidata's P2047 was the alternative and disagrees on
four of the 11 — Assassins, V for Vendetta, Speed Racer and The Animatrix —
which is the reason for picking one source and staying in it.

THE OVERLAP WITH properties/the-matrix.json
-------------------------------------------
Five rows here are also rows there: the four Matrix films and The Animatrix.
Titles and years match exactly, so they would pair — except that build.py
derives a row's sync medium from its LIST's kind string ("g" if "game" is in
it, else "f"), and the-matrix is kind "films & games". Its film rows are
therefore in the games lane and this list's are in the films lane, and the
two never meet. That is a property of the engine, not of this data, and it is
left alone here rather than worked around: making this list "films & games"
to chase the match would put ELEVEN film rows in a games lane to fix five.
Bound does pair, with The Criterion Collection, and the notes say so.

Data:   scratch/agent-wachowski/collect.py -> tools/data/wachowskis.json
Accent: scratch/agent-wachowski/accent.py, accent_search.py
"""
import json
import pathlib
import re
import sys
import unicodedata

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop                                       # noqa: E402
from gwlib.prop import join_bits, slug                       # noqa: E402

SLUG = "wachowskis"
ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "tools" / "data" / "wachowskis.json"

# The four ===Film and television careers=== subsections on the article, in
# order, with the id this list gives each. The titles and the year bands are
# NOT written here — main() reads the titles out of the collected headings and
# derives each band from the roster films that subsection's own prose links,
# so a rewrite upstream fails the build rather than leaving four hand-picked
# decades pretending to be sourced.
SECTION_IDS = ["early", "matrix", "later", "solo"]

WORDS = ("no", "one", "two", "three", "four", "five", "six", "seven", "eight",
         "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
         "sixteen", "seventeen", "eighteen", "nineteen", "twenty")


def word(n):
    return WORDS[n] if n < len(WORDS) else str(n)


def and_list(names):
    names = list(names)
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + " and " + names[-1]


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


def medium_of(kind):
    """build.py's medium letter. It comes off the LIST's kind string, not the
    row, which is why a film row on a "films & games" list lands in the games
    lane — see THE OVERLAP note above."""
    return "g" if "game" in (kind or "") else "f"


def overlaps(keys, my_medium):
    """{list title -> ([titles that pair], [titles that cannot])} for every
    other syncable list in the catalogue. Read off the catalogue on disk so
    the note naming the shared films cannot go stale."""
    same, cross = {}, {}
    for f in sorted((ROOT / "properties").glob("*.json")):
        if f.stem in ("index", "search", SLUG):
            continue
        p = json.loads(f.read_text(encoding="utf-8"))
        kind = p.get("kind") or ""
        if p.get("secret") or not ("film" in kind or "game" in kind):
            continue
        bucket = same if medium_of(kind) == my_medium else cross
        for s in p.get("sections", []):
            for x in s.get("items", []):
                y = year_of(x, str(x.get("n", "")))
                if not y:
                    continue
                k = normt(x["t"]) + "|" + y
                if k in keys and keys[k] not in bucket.get(p["title"], []):
                    bucket.setdefault(p["title"], []).append(keys[k])
    return same, cross


def main():
    d = json.loads(DATA.read_text(encoding="utf-8"))
    table, claims = d["films_table"], d["claims"]
    facts, qids = d["film_facts"], d["qids"]

    def says(key, phrase=None):
        """A prose claim, still present in the article that produced it."""
        c = claims[key]
        assert c, "claim %s was not collected" % key
        assert (phrase or c["probe"]) in c["text"], \
            "the article no longer says: %s" % (phrase or c["probe"])
        return c["probe"]

    # ---- the source tables ------------------------------------------------
    assert len(table) == 19, len(table)
    assert table[0]["t"] == "Assassins" and table[0]["year"] == 1995, table[0]
    assert table[-1]["t"] == "Trash Mountain" and \
        table[-1]["year_raw"] == "tba", table[-1]
    assert len({r["t"] for r in table}) == 19, "the Films table repeats a title"
    assert len(d["tv_table"]) == 2 and len(d["games_table"]) == 4 and \
        len(d["comics_table"]) == 7 and len(d["music_videos"]) == 1, \
        "the Works section no longer has the tables this list accounts for"

    # ---- the credit rule, applied to the columns it is read from ----------
    films = [r for r in table
             if r["directors"][0] == "yes" or r["writers"][0] == "yes"]
    dropped = [r for r in table if r not in films]
    assert len(films) == 11 and len(dropped) == 8, (len(films), len(dropped))

    # every film they directed, they also wrote — which is why "wrote or
    # directed" and "wrote" pick the same 11, and the note can say so
    assert all(r["writers"][0] == "yes" for r in films
               if r["directors"][0] == "yes"), \
        "a directed film is no longer marked Writers; the rule note is stale"
    directed = [r for r in films if r["directors"][0] == "yes"]
    written_only = [r for r in films if r["directors"][0] != "yes"]
    assert len(directed) == 8 and len(written_only) == 3, \
        (len(directed), len(written_only))
    assert [r["t"] for r in written_only] == \
        ["Assassins", "The Animatrix", "V for Vendetta"], written_only

    # the eight the rule drops, each with the source's own reason
    invasion = next(r for r in dropped if r["t"] == "The Invasion")
    assert invasion["writers"] == ["partial", "Uncredited"], invasion
    says("invasion_uncredited")
    prod_only = [r for r in dropped if r is not invasion]
    assert len(prod_only) == 7, prod_only
    assert all(r["producers"][0] in ("yes", "partial") and
               r["directors"][0] == "no" and r["writers"][0] == "no"
               for r in prod_only), prod_only
    lilly_prod = [r for r in prod_only if "Lilly" in r["producers"][1]]
    assert [r["t"] for r in lilly_prod] == [
        "Castration Movie Anthology ii. The Best of Both Worlds", "Dolls",
        "Again Again", "Trash Mountain"], lilly_prod
    # announced work: a dated row would weigh 0 and say so, but none of the
    # announced rows clears the credit rule, so the question does not arise
    undated = [r for r in table if r["year"] is None]
    assert [r["t"] for r in undated] == ["Trash Mountain"], undated
    says("trash_mountain_direct")          # the prose says she will direct it
    assert undated[0]["directors"][0] == "no", \
        "the table now agrees with the prose about Trash Mountain"
    assert not [r for r in films if r["year"] is None], \
        "a roster film has no year; announced rows need w: 0 and a note"

    # ---- solo versus both, flagged by the table itself ---------------------
    solo = [r for r in films if r["directors"][1] or r["writers"][1]]
    assert len(solo) == 1 and solo[0]["t"] == "The Matrix Resurrections", solo
    assert solo[0]["directors"][1] == solo[0]["writers"][1] == "Lana", solo[0]
    says("resurrections_solo")
    codir = [r for r in films if r["notes"].startswith("Co-directed with")]
    assert [r["t"] for r in codir] == ["Cloud Atlas"], codir
    tykwer = codir[0]["notes"][len("Co-directed with "):].strip()
    assert tykwer == "Tom Tykwer", tykwer
    assert tykwer in facts["Cloud Atlas (film)"]["director_raw"], \
        "the film's own infobox no longer names the co-director"

    # ---- release order, from each film's own infobox release date ----------
    for r in films:
        f = facts[r["target"]]
        assert f["release_dates"], r["t"]
        r["rel"] = f["release_dates"][0]
        assert r["rel"][:4] == str(r["year"]), (r["t"], r["rel"], r["year"])
    films.sort(key=lambda r: (r["year"], r["rel"]))
    assert [r["t"] for r in films if r["year"] == 2003] == \
        ["The Matrix Reloaded", "The Animatrix", "The Matrix Revolutions"], \
        "the 2003 rows are no longer in release order"

    # ---- weights: the film's own infobox, all 11 of them --------------------
    for r in films:
        f = facts[r["target"]]
        assert len(f["runtime_mins"]) == 1, (r["t"], f["runtime_raw"])
        r["mins"] = f["runtime_mins"][0]
        assert 90 <= r["mins"] <= 200, (r["t"], r["mins"])
    # the four where Wikidata disagrees, which is why one source was picked
    disagree = [r["t"] for r in films
                if qids[r["target"]]["p2047"] != r["mins"]]
    assert disagree == ["Assassins", "The Animatrix", "V for Vendetta",
                        "Speed Racer"], disagree

    # ---- work ids, resolved only from the Works table's own wikilinks ------
    for r in films:
        q = qids[r["target"]]
        assert q["q"] and q["gate"], (r["t"], q)
        assert re.fullmatch(r"Q[1-9]\d*", q["q"]), q
        r["q"] = q["q"]
    assert len({r["q"] for r in films}) == 11, "two rows share a work id"

    # ---- the lead cross-check: every italicised link in the lead is a
    # shipped row or a named exclusion, and nothing falls between ------------
    shipped = {r["target"] for r in films}
    tv_targets = {r["target"] for r in d["tv_table"]}
    stray = [t for t, _s in d["lead_links"]
             if t not in shipped and t not in tv_targets]
    assert not stray, "the lead names %s and nothing accounts for it" % stray
    assert len(d["lead_links"]) == 11, d["lead_links"]
    lead_tv = sorted({t for t, _s in d["lead_links"] if t in tv_targets})
    assert lead_tv == ["Sense8", "Work in Progress (TV series)"], lead_tv
    # and the infobox's notable works land the same way
    for t, _s in d["notable_works"]:
        assert t in shipped or t in tv_targets, t

    # ---- the sections: the article's own career headings --------------------
    subs = d["career_subs"]
    assert len(subs) == len(SECTION_IDS) == 4, subs
    assert [s["title"] for s in subs] == [
        "Early film projects", "The Matrix franchise", "Later collaborations",
        "Solo projects"], [s["title"] for s in subs]
    bands = []
    for s in subs:
        named = [r for r in films if r["target"] in s["links"]]
        assert named, "no roster film is linked under %s" % s["title"]
        bands.append((min(r["year"] for r in named),
                      max(r["year"] for r in named)))
    assert bands == [(1995, 1999), (2003, 2003), (2005, 2015), (2021, 2021)], \
        bands
    for (_a, hi), (lo, _b) in zip(bands, bands[1:]):
        assert hi < lo, "the article's career bands overlap: %s" % (bands,)
    got = {}
    for r in films:
        hits = [i for i, (lo, hi) in enumerate(bands) if lo <= r["year"] <= hi]
        assert len(hits) == 1, (r["t"], hits)
        got.setdefault(hits[0], []).append(r)
    assert [len(got[i]) for i in range(4)] == [3, 3, 4, 1], \
        {i: len(v) for i, v in got.items()}
    # The Animatrix is the one row no career subsection links by name; it
    # lands in the Matrix band on its year, which is where it belongs
    assert not any("The Animatrix" in s["links"] for s in subs)
    assert got[1][1]["t"] == "The Animatrix", got[1]

    # ---- The Animatrix: what "wrote it" actually covers ---------------------
    anim = next(r for r in films if r["t"] == "The Animatrix")
    segs = d["animatrix_segments"]
    assert len(segs) == 9, segs
    ac = d["film_claims"]["The Animatrix"]
    assert ac and ac["probe"] in ac["text"], ac
    wrote = re.search(r'Wrote: "([^"]+)"', anim["notes"]).group(1)
    story = re.findall(r'"([^"]+)"', anim["notes"].split("Story by:")[1])
    assert wrote == "Final Flight of the Osiris" and wrote in segs, wrote
    assert story == ["The Second Renaissance Part I & II", "Kid's Story"], story
    # "Part I & II" is two of the nine, so the story credit covers three
    assert {"The Second Renaissance, Part I", "The Second Renaissance, Part II",
            "Kid's Story"} <= set(segs), segs
    story_n = 3
    assert "Direct-to-video" in anim["notes"], anim["notes"]
    anim_dirs = len([x for x in
                     facts["The Animatrix"]["director_raw"].split(",")
                     if x.strip()])
    assert anim_dirs == 7, anim_dirs

    # ---- the other facts the row notes are built from -----------------------
    says("assassins_donner")
    assert facts["Assassins (1995 film)"]["director_raw"] == "Richard Donner"
    says("bound_debut")
    says("bound_noir")
    assert films[1]["t"] == "Bound", films[1]        # the first they directed
    assert directed[0]["t"] == "Bound", directed[0]
    says("registry")
    says("sequels_btb")
    says("vfv_mcteigue")
    vfv = d["film_claims"]["V for Vendetta (film)"]
    assert vfv and vfv["probe"] in vfv["text"], vfv
    assert facts["V for Vendetta (film)"]["director_raw"] == "James McTeigue"
    says("vfv_wrote")
    says("speed_racer_anime")
    says("speed_racer_manga")
    ca = d["film_claims"]["Cloud Atlas (film)"]
    assert ca and ca["probe"] in ca["text"], ca
    says("cloud_atlas_tykwer")
    says("cloud_atlas_proud")
    says("cloud_atlas_indep")
    says("jupiter_original")
    says("sense8_created")
    says("sense8_finale")
    says("lilly_break")
    says("wip_lilly")

    # ---- row notes ----------------------------------------------------------
    def role_of(r):
        if r["directors"][0] != "yes":
            who = facts[r["target"]]["director_raw"]
            if r["t"] == "The Animatrix":
                return ("Wrote %s and shared the story on %s more of its nine "
                        "shorts; directed none of it" % (wrote, word(story_n)))
            return "Wrote it, did not direct it — %s did" % who
        if r in solo:
            return "%s wrote and directed this one without Lilly" \
                   % r["directors"][1]
        if r in codir:
            return "Wrote and co-directed with %s" % tykwer
        return "Wrote and directed"

    EXTRA = {
        "Assassins": "The earliest credit on their filmography",
        "Bound": "A neo-noir thriller, and their debut as directors",
        "The Matrix": "In the National Film Registry since 2012",
        "The Matrix Reloaded": "First of two sequels shot back-to-back",
        "The Animatrix": "Direct-to-video, and made by %s other directors"
                         % word(anim_dirs),
        "The Matrix Revolutions": "The other half of that shoot, six months "
                                  "later",
        "V for Vendetta": "Adapted from the Alan Moore and David Lloyd comic, "
                          "and McTeigue's first film",
        "Speed Racer": "From the 1960s manga Mach GoGoGo — the first anime "
                       "they watched",
        "Cloud Atlas": "Adapted from David Mitchell's novel, and the one they "
                       "say they are proudest of",
        "Jupiter Ascending": "An original space opera, not an adaptation, and "
                             "the last film the two of them made together",
        "The Matrix Resurrections": "The first film made by only one of them",
    }
    assert set(EXTRA) == {r["t"] for r in films}, \
        set(EXTRA) ^ {r["t"] for r in films}

    # ---- sections ------------------------------------------------------------
    counts = {i: (len(got[i]), sum(1 for r in got[i]
                                   if r["directors"][0] == "yes"))
              for i in got}

    def intro_for(i):
        n, dirs = counts[i]
        if i == 0:
            return ("A script they sold and the two films they made "
                    "themselves. Assassins they wrote and handed over; Bound "
                    "is the first thing they directed; The Matrix is the one "
                    "that made the name. The heading is the article's own, "
                    "and so is the fact that the first Matrix film sits here "
                    "rather than in the section named after its franchise.")
        if i == 1:
            return ("One year, three releases, and the article gives them "
                    "their own heading. Two sequels shot back-to-back with "
                    "an animated anthology out between them — the anthology "
                    "is the row they wrote without directing, and its note "
                    "says how much of it is theirs.")
        if i == 2:
            return ("Ten years, %s films, and the last of them is the last "
                    "the two of them made together. %s they directed; V for "
                    "Vendetta they wrote and gave to James McTeigue."
                    % (word(n), word(dirs).capitalize()))
        return ("The article's heading for what came after Sense8, and one "
                "film on this list falls under it. Lilly's solo work in the "
                "same stretch is television and a run of producer credits, "
                "and this list carries neither.")

    sections = []
    for i, s in enumerate(subs):
        rows = got[i]
        items = []
        for r in rows:
            items.append({
                "id": "wach-%d-%s" % (r["year"], slug(r["t"])),
                "t": r["t"], "n": str(r["year"]), "q": r["q"],
                "w": round(r["mins"] / 60.0, 2),
                "note": join_bits(role_of(r), EXTRA[r["t"]]),
            })
        span = ("%d" % rows[0]["year"] if rows[0]["year"] == rows[-1]["year"]
                else "%d–%d" % (rows[0]["year"], rows[-1]["year"]))
        sections.append({
            "id": SECTION_IDS[i], "title": s["title"],
            "sub": "%s · %d film%s · about %d hours"
                   % (span, len(rows), "" if len(rows) == 1 else "s",
                      round(sum(r["mins"] for r in rows) / 60.0)),
            "intro": intro_for(i), "items": items})
    sections[0]["open"] = True

    rows = [x for s in sections for x in s["items"]]
    assert len(rows) == 11, len(rows)
    assert all(isinstance(x["w"], float) and x["w"] > 0 for x in rows), rows
    assert all(x.get("note") and x.get("q") for x in rows), rows
    for s in sections:
        assert all(a["n"] <= b["n"] for a, b in zip(s["items"],
                                                    s["items"][1:])), s["id"]
    mins = sum(r["mins"] for r in films)
    hours = round(sum(x["w"] for x in rows), 2)
    assert abs(hours - mins / 60.0) < 0.1, (hours, mins / 60.0)

    # ---- the films this list shares with other lists here --------------------
    keys = {normt(r["t"]) + "|" + str(r["year"]): r["t"] for r in films}
    order = [r["t"] for r in films]
    same, cross = overlaps(keys, medium_of("films"))
    assert list(same) == ["The Criterion Collection"], same
    assert same["The Criterion Collection"] == ["Bound"], same
    assert list(cross) == ["The Matrix"], cross
    assert sorted(cross["The Matrix"]) == sorted([
        "The Matrix", "The Animatrix", "The Matrix Reloaded",
        "The Matrix Revolutions", "The Matrix Resurrections"]), cross
    blocked = sorted(cross["The Matrix"], key=order.index)
    shared_n = len(same["The Criterion Collection"]) + len(blocked)

    p = {
        "slug": SLUG,
        "title": "The Wachowskis",
        "subtitle": "wrote it or directed it, one row per film",
        "kind": "films",
        # The Matrix is a household name; the sisters who made it are not, in
        # the way Nolan (80) or Tarantino (78) are. This is squarely the
        # 60–69 band — well known inside film, thinner outside it — and it
        # sits a shade under the auteurs whose surname is the draw (Fincher
        # 69, Coppola and Wes Anderson 68, Coen 67, PTA 66) and a shade over
        # Lynch and Gilliam at 64. Well under the-matrix at 83, which carries
        # the franchise line this list only crosses. See POPULARITY.md.
        "popularity": 65,
        "year": "1995–2021",
        "blurb": "Eleven films in release order — about %d hours. Eight they "
                 "directed and three they only wrote, and every row says "
                 "which." % round(hours),
        "unit": {"one": "film", "many": "films"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        # Measured in CIELAB against all 392 accents already in
        # properties/index.json; see scratch/agent-wachowski/accent_search.py.
        # The obvious colour is the Matrix rain green and it is exactly taken
        # — the-matrix carries #0C3B0C — so this walks the hue wheel instead
        # and takes the most separated region left, a saturated violet at
        # 11.7 worst-case (nearest: Time Loops' #C08FE0). It suits the run
        # from Speed Racer to Jupiter Ascending, which is the most saturated
        # stretch of film-making anyone here has.
        "accent": "#9542B9",
        "accentDark": "#E5A3FF",
        "tiers": False,
        "notes": [
            ["The rule is: they wrote it or they directed it.",
             "Their filmography's own Films table has three credit columns — "
             "Directors, Writers, Producers — and this list takes the first "
             "two. That is %s of its %s rows, and every row says which job it "
             "was: %s they wrote and directed, %s they wrote and someone else "
             "directed. The two rules pick the same films, as it happens, "
             "because there is no film here they directed from somebody "
             "else's script — so \"everything they wrote\" and \"everything "
             "they wrote or directed\" are the same %s films, and "
             "\"everything they directed\" would be %s, dropping Assassins, "
             "V for Vendetta and The Animatrix."
             % (word(len(films)), word(len(table)), word(len(directed)),
                word(len(written_only)), word(len(films)),
                word(len(directed)))],
            ["Where one sister made it and the other did not, the row says so.",
             "One film here is one of them rather than both: The Matrix "
             "Resurrections, which Lana wrote and directed without Lilly, and "
             "the table flags it that way itself. Cloud Atlas is the other "
             "direction — co-directed with "
             "Tom Tykwer, and the row says that too. Lilly's own solo work "
             "does not appear at all, because it is television and producing: "
             "two episodes of Work in Progress that she wrote and directed, "
             "and executive-producer credits on four recent films."],
            ["Producing is not authorship — %s rows the table has are not "
             "rows here." % word(len(dropped)),
             "%s of the %s are producer or executive-producer credits only: "
             "The Matrix Revisited, a documentary about their own first film; "
             "Ninja Assassin; the short Google Me Love; and four Lilly has "
             "executive produced lately — %s. The eighth is The "
             "Invasion, where the Writers column says \"Uncredited\" and the "
             "article says outright that they are not credited on the film. "
             "That is the source drawing the line, not this list. Trash "
             "Mountain is the one place the source argues with itself: the "
             "prose says Lilly will direct it and the table says executive "
             "producer with the year still to be announced. Undated work gets "
             "no row either way, because there is nothing to place."
             % (word(len(prod_only)).capitalize(), word(len(dropped)),
                and_list([r["t"].split(" Anthology")[0]
                          for r in lilly_prod]))],
            ["No television, and Sense8 is what that costs.",
             "The source keeps television in its own table with its own "
             "columns, and this list stops at the film table. That leaves out "
             "the series they created with J. Michael Straczynski and ran for "
             "%d episodes over two seasons, ending with a two-hour finale in "
             "2018 — Lilly stepped away after the first season, so the second "
             "is Lana's. The bar is the other reason: every row here is "
             "weighted in hours from one source, and the source publishes no "
             "per-episode runtime for Sense8, only \"%s\" across all %d. "
             "Twenty-four rows carrying no hours would outnumber the films "
             "two to one and take the total with them. The four games, the "
             "seven comics and the one music video are out for the first "
             "reason alone: each is its own table."
             % (d["sense8"]["episodes"], d["sense8"]["runtime_raw"],
                d["sense8"]["episodes"])],
            ["The four sections are the article's own.",
             "Not four invented decades: they are the four career headings on "
             "the Wachowskis article, in order, and each section holds the "
             "films whose years fall inside the span that heading's own prose "
             "covers. It is why the first Matrix film sits under Early film "
             "projects rather than under The Matrix franchise — the article "
             "puts it there."],
            ["Bar widths are runtimes, from each film's own infobox.",
             "One source for all %s, and every one of them states exactly one "
             "figure, so nothing is adjudicated and no row goes unweighted. "
             "Wikidata's runtime property was the alternative and disagrees "
             "on %s of the %s — %s — which is the whole argument for picking "
             "one source and staying inside it. The Animatrix is the one to "
             "know about: %d minutes here, %d on Wikidata, which is what The "
             "Matrix list on this site uses."
             % (word(len(films)), word(len(disagree)), word(len(films)),
                and_list(disagree), anim["mins"],
                qids["The Animatrix"]["p2047"])],
            ["%s of these films are on another list here."
             % word(shared_n).capitalize(),
             "Bound is on The Criterion Collection, and ticking it in one "
             "place ticks it in the other: film rows pair across lists by "
             "title and year. The %s Matrix entries — %s — are on The Matrix "
             "as well, and those do NOT pair, because that list carries games "
             "alongside its films and the catalogue reads a row's medium off "
             "the whole list rather than the row. Nothing is duplicated and "
             "no hours are counted twice either way: every list totals only "
             "its own rows."
             % (word(len(blocked)), and_list(blocked))],
            "Roster, credits and sections from Wikipedia's The Wachowskis "
            "article, read from the Works tables and the career headings "
            "themselves; runtimes, directors and release dates from each "
            "film's own article; work ids from Wikidata, resolved from the "
            "table's own links and gated on a matching release year.",
        ],
        "sections": sections,
    }

    out = prop.write(p)
    print("wrote %s — %d films, %d minutes, %.2f hours"
          % (out.name, len(rows), mins, hours))
    print("   %d wrote and directed, %d wrote only (%s)"
          % (len(directed), len(written_only),
             ", ".join(r["t"] for r in written_only)))
    print("   solo: %s · co-directed: %s"
          % (", ".join("%s (%s)" % (r["t"], r["directors"][1]) for r in solo),
             ", ".join(r["t"] for r in codir)))
    for s in sections:
        print("   %-24s %2d  %s" % (s["title"][:24], len(s["items"]), s["sub"]))
    print("   pairs: Criterion/Bound · blocked: %s" % ", ".join(blocked))


if __name__ == "__main__":
    main()
