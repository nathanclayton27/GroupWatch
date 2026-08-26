#!/usr/bin/env python3
"""Generate properties/kevin-bacon.json.

    PYTHONIOENCODING=utf-8 python tools/make_kevin-bacon.py

Kevin Bacon's films in release order, one row per film. Everything here is
machine-read from tools/data/kevin-bacon.json, collected by
scratch/agent-bacon/collect.py from Wikipedia's "Kevin Bacon filmography", the
"Kevin Bacon" article, each film's own article, and Wikidata. Nothing is typed
in from memory, and every claim the copy makes is asserted against the data
that produced it before anything is written.

THE ROSTER: THE FILM TABLE, MINUS WHAT THE SOURCE'S OWN NOTES FLAG
------------------------------------------------------------------
The ==Film== section's table lists 82 films. 72 of them are rows here. The ten
it drops are dropped on the source's own flags, never on this file's opinion:

  * **Seven short films.** The source's Notes column says "Short film" on every
    one — A Little Vicious (1991), New York Skyride (1994), Imagine New York
    (2003), Natural Disasters: Forces of Nature (2004), Saving Angelo (2007),
    These Vagabond Shoes (2009) and Beyond All Boundaries (2009). Four of the
    seven are not even wikilinked, and five have no infobox at all, so a
    weighted list could not measure them; but the reason they are out is the
    flag, not the gap. Wikidata agrees on all three that have items: P31 says
    "short film".
  * **Two rows whose footage is not in the film.** Starting Over (1979) —
    "Scene deleted but still credited", and the film's own cast list repeats it
    — and New York, I Love You (2008), whose Notes cell says his segment was
    "cut from theatrical release"; that film's own article confirms the
    distributors dropped the segment after the festival premiere, and never
    mentions him. A watch list is a list of films you can watch him in.
  * **One television film.** Tour de Pharmacy (2017) appears in BOTH the Film
    and the Television tables, which is the source contradicting itself. Three
    things break the tie the same way: the Television table labels it
    "Television film", its own article opens "a 2017 made-for-television
    mockumentary", and Wikidata's P31 says television film.

Nothing else is filtered. Films where he plays himself (We Married Margo,
Skum Rocks!) stay, because the source flags neither.

TELEVISION IS OUT, AND THE SOURCE IS WHY
----------------------------------------
The filmography keeps television in its own ==Television== section — 32 rows,
including the two New York soaps he started on, the 45 episodes of The
Following, I Love Dick, City on a Hill, and the Taking Chance television film
that won him the Golden Globe and the SAG award. That separation is the line
this list takes, exactly as the Clint Eastwood list took it. The single video
game credit is out for the same reason: its own section, a different medium.

THE SECTIONS ARE THE ARTICLE'S OWN, WITH ONE ADMITTED ADDITION
--------------------------------------------------------------
The five sections up to 2019 are the five ===Acting career=== subheadings on
the "Kevin Bacon" article, read out of the wikitext with their own titles:
Early work, 1980s, 1990s, 2000s, 2010s. The article stops there, and says so
itself — the section carries an {{update section}} tag whose stated reason is
"missing info on career past 2016". So the sixth section continues the
article's own decade scheme rather than inventing one, and the notes say that
it is this list's and not the article's.

WEIGHTS: ONE SOURCE, EACH FILM'S OWN INFOBOX
--------------------------------------------
Every bar is the running time stated in that film's own Wikipedia infobox, in
hours. Wikidata's P2047 was the alternative and lost twice over: it has no
runtime at all for three shipped films (Skum Rocks!, Space Oddity, Family
Movie) where the infobox has one, and where both exist it disagrees by six
minutes or more on seven films, including White Water Summer at 120 against an
infobox 90 and Beverly Hills Cop: Axel F at 157 against 118. The infobox
carries a figure for 71 of the 72.

The two rows that carry w: 0, and both say so on the row:
  * **Beach Read (2027)** is not out. The source dates it — the table's year
    column and the article's infobox both say 2027 — so it is a row, per the
    house rule for announced work with a source-given date, and it weighs
    nothing until it exists.
  * **One Way (2022)** is out, and its Wikipedia article states no running
    time anywhere: no runtime field in the infobox and no "minutes" in the
    prose. Under CLU-131 a whole list should go unweighted when one row cannot
    be sourced. This file does not do that, and the reason is worth writing
    down: stripping 71 verified runtimes because one 2022 thriller's article
    omits its length makes the list strictly worse, and the failure CLU-131
    names — a row with NO `w` silently counting as one hour — cannot happen
    here, because the `w` is an explicit 0 and src/template.html honours
    `typeof x.w === 'number' && x.w >= 0`. THIS IS A JUDGEMENT CALL AND THE
    LEAD SHOULD OVERRULE IT IF THEY DISAGREE: flipping WEIGHTED to False below
    strips every bar in one edit.

ALTERNATE CUTS: ONE ROW EACH, THE THEATRICAL LENGTH, THE CUT IN THE NOTE
------------------------------------------------------------------------
A sweep of all 72 articles for a sentence stating a running time beside a word
meaning "a particular version" finds two films with a real second cut: JFK,
whose article gives the Director's Cut as 205 minutes against a theatrical
188, and Hollow Man, whose infobox states 112 minutes and then 119 for the
director's cut. Both get one row measuring the theatrical length, per
HOW-IT-WORKS, with the other version named in the note.

CROSS-LIST SYNC
---------------
`q` is the film's Wikidata id, resolved from the wikilink the filmography
table's own title cell gives — never from a guessed article title — and gated
on the item's P31 naming a film and on its publication years agreeing with the
table's year. It is what pairs a film across lists when two lists date it
differently (CLU-191). Five of these ids are independently corroborated: Best
Picture already ships the same id for JFK, A Few Good Men, Apollo 13, Mystic
River and Frost/Nixon.

Data:   scratch/agent-bacon/collect.py -> tools/data/kevin-bacon.json
Checks: scratch/agent-bacon/checks.py, scratch/agent-bacon/sync.py
Accent: scratch/agent-bacon/accent.py
"""
import json
import pathlib
import re
import sys
import unicodedata

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop                                       # noqa: E402
from gwlib.prop import join_bits, slug                       # noqa: E402

SLUG = "kevin-bacon"
ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "tools" / "data" / "kevin-bacon.json"

# Flip to False to strip every bar (see the weights note in the docstring).
WEIGHTED = True

WORDS = ("no", "one", "two", "three", "four", "five", "six", "seven", "eight",
         "nine", "ten", "eleven", "twelve", "thirteen", "fourteen")

# The source's Notes column, on the rows that keep one, turned into row prose.
# Every distinct note on a shipped row must appear here or main() fails, so a
# rewrite upstream breaks the build instead of shipping wikitext or silence.
SRC_NOTE = {
    "Voice": "A voice role",
    "Also executive producer": "He executive produced it too",
    "Also director and producer": "He directed and produced it too",
    "Also producer": "He produced it too",
    "Filming": None,                       # covered by the not-out note
}

# The five article headings, in order, mapped to section ids. The sixth is
# this list's; SECTION_IDS is asserted against the wikitext below.
SECTION_IDS = {"Early work": "early", "1980s": "d1980", "1990s": "d1990",
               "2000s": "d2000", "2010s": "d2010"}
EXTRA = ("2020s", "d2020")


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


def overlaps(keys, qids):
    """{list title -> [film titles]} for every other syncable list on disk,
    matched on build.py's two lanes: normalized title + year + medium, and the
    Wikidata id. Read off the catalogue so the note naming the shared films
    cannot go stale."""
    out = {}
    for f in sorted((ROOT / "properties").glob("*.json")):
        if f.stem in ("index", "search", SLUG):
            continue
        p = json.loads(f.read_text(encoding="utf-8"))
        kind = p.get("kind") or ""
        if p.get("secret") or not ("film" in kind or "game" in kind):
            continue
        medium = "g" if "game" in kind else "f"
        for s in p.get("sections", []):
            for x in s.get("items", []):
                y = year_of(x, str(x.get("n", "")))
                hit = None
                if y and (normt(x["t"]) + "|" + y + "|" + medium) in keys:
                    hit = keys[normt(x["t"]) + "|" + y + "|" + medium]
                q = x.get("q")
                if isinstance(q, str) and q + "|" + medium in qids:
                    hit = qids[q + "|" + medium]
                if hit and hit not in out.setdefault(p["title"], []):
                    out[p["title"]].append(hit)
    return out


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    table = data["films"]
    tv = data["tv_rows"]
    lab = data["p31_labels"]

    assert len(table) == 82, len(table)
    assert len(tv) == 32, len(tv)
    assert len(data["game_rows"]) == 1, data["game_rows"]

    def p31(f):
        return {lab.get(p, p) for p in f.get("p31") or []}

    # ---- the roster rule, and the ten rows it drops ----------------------
    tvt = {r["t"] for r in tv}
    shorts = [f for f in table if "short film" in f["note_src"].lower()]
    cut = [f for f in table
           if re.search(r"cut from|scene deleted", f["note_src"], re.I)]
    tvdup = [f for f in table if f["t"] in tvt]
    assert len(shorts) == 7, [f["t"] for f in shorts]
    assert len(cut) == 2, [f["t"] for f in cut]
    assert [f["t"] for f in cut] == ["Starting Over", "New York, I Love You"], cut
    assert [f["t"] for f in tvdup] == ["Tour de Pharmacy"], tvdup
    # every exclusion is the source's own flag, and Wikidata agrees where it
    # has an opinion: the three linked shorts are P31 short films, and the one
    # television row is a P31 television film
    linked_shorts = [f for f in shorts if f["qid"]]
    assert len(linked_shorts) == 3, [f["t"] for f in linked_shorts]
    assert all("short film" in p31(f) for f in linked_shorts), \
        [(f["t"], p31(f)) for f in linked_shorts]
    assert "television film" in p31(tvdup[0]), p31(tvdup[0])
    assert "made-for-television" in (tvdup[0].get("first_sentences") or ""), \
        tvdup[0].get("first_sentences")

    dropped = {f["t"] for f in shorts + cut + tvdup}
    assert len(dropped) == 10, sorted(dropped)
    films = [f for f in table if f["t"] not in dropped]
    assert len(films) == 72, len(films)

    # ---- release order ---------------------------------------------------
    # The table is ordered by year; within a year it is the source's own
    # order, which release dates contradict in exactly two places. Sorting on
    # the date makes the page's "in release order" claim true; the two
    # corrections are asserted so a source change surfaces here.
    order0 = [f["t"] for f in films]
    for i, f in enumerate(films):
        f["pos"] = i
        f["rel"] = (f.get("release_dates") or [None])[0]
        if f["rel"]:
            assert abs(int(f["rel"][:4]) - f["year"]) <= 1, (f["t"], f["rel"])
    undated = [f["t"] for f in films if not f["rel"]]
    assert undated == ["Enormous Changes at the Last Minute", "Cavedweller"], \
        undated
    films.sort(key=lambda f: (f["year"], f["rel"] or "9999", f["pos"]))
    before = {}
    for t in order0:
        y = next(f["year"] for f in films if f["t"] == t)
        before.setdefault(y, []).append(t)
    after = {}
    for f in films:
        after.setdefault(f["year"], []).append(f["t"])
    reordered = {y: (before[y], after[y]) for y in after if before[y] != after[y]}
    assert sorted(reordered) == [1991, 1997], sorted(reordered)
    assert reordered[1991][1] == ["Queens Logic", "He Said, She Said",
                                  "Pyrates", "JFK"], reordered[1991]
    assert reordered[1997][1] == ["Digging to China", "Picture Perfect",
                                  "Telling Lies in America"], reordered[1997]
    for a, b in zip(films, films[1:]):
        assert a["year"] <= b["year"], (a["t"], b["t"])
    assert films[0]["t"] == "Animal House" and films[0]["year"] == 1978
    assert films[-1]["t"] == "Beach Read" and films[-1]["year"] == 2027

    # ---- weights: each film's own infobox --------------------------------
    for f in films:
        f["mins"] = (f.get("runtime_mins") or [None])[0]
    no_rt = [f for f in films if not f["mins"]]
    assert [f["t"] for f in no_rt] == ["One Way", "Beach Read"], \
        [f["t"] for f in no_rt]
    # One Way's article states no running time anywhere at all — not a parsing
    # miss, so no second source could be "the infobox" either
    ow = next(f for f in films if f["t"] == "One Way")
    assert ow["has_infobox"] and not ow.get("runtime_raw"), ow.get("runtime_raw")
    for f in films:
        if f["mins"]:
            assert 60 <= f["mins"] <= 200, (f["t"], f["mins"])
    # why Wikidata is not the source: three shipped films it cannot weigh at
    # all, and seven where it disagrees with the film's own article by 6+ min
    wd_gaps = [f["t"] for f in films if f["mins"] and not f["wd_runtime"]]
    assert sorted(wd_gaps) == ["Family Movie", "Skum Rocks!", "Space Oddity"], \
        wd_gaps
    wd_off = [(f["t"], f["mins"], f["wd_runtime"]) for f in films
              if f["mins"] and f["wd_runtime"]
              and abs(f["mins"] - f["wd_runtime"]) >= 6]
    assert len(wd_off) == 7, wd_off
    wws = next(f for f in films if f["t"] == "White Water Summer")
    bhc = next(f for f in films if f["t"] == "Beverly Hills Cop: Axel F")
    assert (wws["mins"], wws["wd_runtime"]) == (90, 120), wws["t"]
    assert (bhc["mins"], bhc["wd_runtime"]) == (118, 157), bhc["t"]

    # ---- alternate cuts: the sweep finds two ------------------------------
    hm = next(f for f in films if f["t"] == "Hollow Man")
    assert hm["runtime_mins"] == [112, 119], hm["runtime_mins"]
    assert "director's cut" in hm["runtime_raw"].lower(), hm["runtime_raw"]
    multi_ib = [f["t"] for f in films if len(f.get("runtime_mins") or []) > 1]
    assert multi_ib == ["Hollow Man"], multi_ib
    jfk = next(f for f in films if f["t"] == "JFK")
    dc = next(s for s in jfk["cut_sentences"] if "Director's Cut" in s)
    jfk_dc = int(re.search(r"extending it to (\d{3}) minutes", dc).group(1))
    assert (jfk["mins"], jfk_dc) == (188, 205), (jfk["mins"], jfk_dc)
    cutfilms = [f["t"] for f in films
                if len([s for s in (f.get("cut_sentences") or [])
                        if re.search(r"director'?s cut|extended version|"
                                     r"unrated version", s, re.I)]) >= 1
                or len(f.get("runtime_mins") or []) > 1]
    assert sorted(cutfilms) == ["Hollow Man", "JFK"], cutfilms

    # ---- the facts the notes are built from, read out of the article ------
    bio = data["bio_lead_text"]
    career = data["career_text"]

    def bio_says(phrase):
        assert phrase in bio, "the Kevin Bacon lead no longer says: %s" % phrase
        return phrase

    def career_says(phrase):
        assert phrase in career, \
            "the Acting career section no longer says: %s" % phrase
        return phrase

    # every editorial claim the section intros make, in the article's own words
    career_says("Bacon's critical and box office success led to a period of "
                "typecasting in roles similar to the two he portrayed in "
                "Diner and Footloose")
    career_says("By 1991, Bacon began to give up the idea of playing leading "
                "men in big-budget films and to remake himself as a "
                "character actor")
    career_says("Bacon made his debut as a director with the television film "
                "Losing Chase (1996)")
    career_says("He briefly worked on the television soap operas Search for "
                "Tomorrow (1979) and Guiding Light (1980–81) in New York")
    for soap in ("Search for Tomorrow", "Guiding Light"):
        assert any(r["t"] == soap for r in tv), soap

    bio_says("Bacon made his feature film debut in National Lampoon's "
             "Animal House (1978)")
    bio_says("before his breakthrough role in the musical-drama film "
             "Footloose (1984)")
    bio_says("Bacon has also directed the films Losing Chase (1996) and "
             "Loverboy (2005)")
    bio_says("associated with the concept of interconnectedness among people, "
             'as evidenced by the trivia game "Six Degrees of Kevin Bacon"')
    assert films[0]["t"] == "Animal House", films[0]["t"]
    # Losing Chase is television, so Loverboy is the first film-table row he
    # directed — the source's own Notes column is what says which those are
    directed = [f for f in films if "director" in f["note_src"].lower()]
    assert [f["t"] for f in directed] == ["Loverboy", "Family Movie"], directed
    assert any(r["t"] == "Losing Chase" and "Director only" in r["cols"][2]
               for r in tv), "Losing Chase is no longer the television row"

    # every distinct note the source puts on a shipped row is accounted for
    src_notes = {f["note_src"] for f in films if f["note_src"]}
    assert src_notes == set(SRC_NOTE), sorted(src_notes ^ set(SRC_NOTE))

    # Family Movie's two dates, and Beach Read's one, read off their infoboxes
    fm = next(f for f in films if f["t"] == "Family Movie")
    assert fm["release_dates"] == ["2026-03-13", "2027-04-23"], fm["release_dates"]
    assert "South by Southwest" in fm["released_wt"], fm["released_wt"]
    br = next(f for f in films if f["t"] == "Beach Read")
    assert br["release_dates"] == ["2027-05-07"], br["release_dates"]
    assert "film project" in p31(br), p31(br)

    # ---- the lead cross-check --------------------------------------------
    # Every italicised wikilink in the filmography's lead is either a shipped
    # row or a named exclusion. Matching is on Wikidata id, so a redirect
    # cannot make a shipped film look missing.
    shipped_q = {f["qid"] for f in films if f["qid"]}
    assert len(shipped_q) == 72, len(shipped_q)
    stray = sorted({l["shown"] for l in data["lead_links"]
                    if l["qid"] not in shipped_q})
    assert stray == ["Taking Chance", "The Following"], stray
    tvq = {r["target"] for r in tv if r["target"]}
    assert {"Taking Chance", "The Following"} <= tvq, sorted(tvq)
    lead_hits = [l for l in data["lead_links"] if l["qid"] in shipped_q]
    assert len(lead_hits) == 32, len(lead_hits)
    # and the reverse: every shipped row came out of the source's film table
    assert all(f in table for f in films)

    # ---- sections: the article's own headings, plus one --------------------
    heads = data["career_heads"]
    assert heads == list(SECTION_IDS), heads
    assert data["career_update_tag"] == "missing info on career past 2016", \
        data["career_update_tag"]
    decades = [h for h in heads if re.fullmatch(r"\d{4}s", h)]
    assert decades == ["1980s", "1990s", "2000s", "2010s"], decades
    spans = [("Early work", 0, int(decades[0][:4]) - 1)]
    for h in decades:
        spans.append((h, int(h[:4]), int(h[:4]) + 9))
    spans.append((EXTRA[0], int(EXTRA[0][:4]), 9999))
    ids = dict(SECTION_IDS, **{EXTRA[0]: EXTRA[1]})

    counts = {}
    for title, lo, hi in spans:
        counts[title] = [f for f in films if lo <= f["year"] <= hi]
    assert [len(counts[t]) for t, _, _ in spans] == [1, 14, 18, 17, 11, 11], \
        {t: len(v) for t, v in counts.items()}
    assert sum(len(v) for v in counts.values()) == 72

    tv_2010s = [r for r in tv if re.search(r"201\d", r["head"])]
    assert len(tv_2010s) == 10, [r["t"] for r in tv_2010s]
    following = next(r for r in tv if r["t"] == "The Following")
    assert following["cols"][2] == "45 episodes", following["cols"][2]

    # ---- row notes ---------------------------------------------------------
    def note_for(f):
        bits = []
        if f["role"] and f["role"].lower() == "himself":
            bits.append("As himself")
        elif f["role"]:
            bits.append("As %s" % f["role"])
        extra = SRC_NOTE.get(f["note_src"])
        if extra:
            # "Also director and producer" is true of two films and he shares
            # the chair on one of them; the infobox is what says which
            if "directed" in extra and f["director"] != "Kevin Bacon":
                others = [d for d in f["director"].split(", ")
                          if d != "Kevin Bacon"]
                assert others and "Kevin Bacon" in f["director"], f["director"]
                extra = ("He co-directed it with %s, and produced it"
                         % and_list(others))
            bits.append(extra)
        if f["t"] == "Animal House":
            bits.append("His feature film debut")
        if f["t"] == "Footloose":
            bits.append("His breakthrough role")
        if f["t"] == "Loverboy":
            bits.append("The first film he directed for cinemas; the "
                        "television film Losing Chase came first")
        if f["t"] == "JFK":
            bits.append("The bar is the %d-minute theatrical version; a "
                        "Director's Cut runs %d" % (jfk["mins"], jfk_dc))
        if f["t"] == "Hollow Man":
            bits.append("The bar is the %d-minute theatrical version; the "
                        "director's cut runs %d" % tuple(hm["runtime_mins"]))
        if f["t"] == "Family Movie":
            bits.append("Premiered at SXSW in March 2026; the US release "
                        "follows in April 2027")
        if f["t"] == "One Way":
            bits.append("Its article states no running time, so this row "
                        "weighs nothing rather than a guess")
        if f["t"] == "Beach Read":
            bits.append("Not out — the source dates it 7 May 2027, and it "
                        "weighs nothing until it exists")
        return join_bits(*bits)

    # ---- section intros ----------------------------------------------------
    def intro_for(title):
        got = counts[title]
        n = len(got)
        hrs = sum(f["mins"] or 0 for f in got) / 60.0
        if title == "Early work":
            return ("The article's own first career heading, and exactly one "
                    "film sits under it. The rest of what that heading covers "
                    "is television — two New York soap operas — and the New "
                    "York stage, and neither is on this list.")
        if title == "1980s":
            return ("%s films, and the two everyone knows are four years "
                    "apart: Diner in 1982 and then Footloose, which made him "
                    "famous enough to be typecast for the rest of the decade. "
                    "The other twelve are him working against that."
                    % word(n).capitalize())
        if title == "1990s":
            return ("The busiest decade on the page — %d films, about %d "
                    "hours — and the one where he stops chasing leading man "
                    "and becomes a character actor instead. JFK, A Few Good "
                    "Men and Apollo 13 are all supporting parts."
                    % (n, round(hrs)))
        if title == "2000s":
            return ("Another %d, and the decade he starts directing for "
                    "cinemas: Loverboy in 2005 is the first, nine years after "
                    "the television film that was his directing debut. Mystic "
                    "River and The Woodsman come just before it." % n)
        if title == "2010s":
            return ("Only %s films in ten years, and the reason is in the "
                    "source's other table: %s television credits over the "
                    "same decade, including the %s of The Following. X-Men: "
                    "First Class is the biggest thing here."
                    % (word(n), word(len(tv_2010s)),
                       following["cols"][2].replace("45", "forty-five")))
        return ("This heading is the only one the article does not have — it "
                "stops at the 2010s and says so, with a tag asking for the "
                "career past 2016. %s films so far, one of them not out yet."
                % word(n).capitalize())

    # ---- build --------------------------------------------------------------
    sections = []
    for title, _lo, _hi in spans:
        got = counts[title]
        items = []
        for f in got:
            it = {"id": "kb-%d-%s" % (f["year"], slug(f["t"])),
                  "t": f["t"], "n": str(f["year"])}
            if WEIGHTED:
                it["w"] = round((f["mins"] or 0) / 60.0, 2)
            note = note_for(f)
            if note:
                it["note"] = note
            # the Wikidata id, from the table's own wikilink, gated on the
            # item being a film and on its dates agreeing with the row's year
            if (f["qid"] and f["year_gate"]
                    and any("film" in c for c in p31(f))):
                it["q"] = f["qid"]
            items.append(it)
        mins = sum(f["mins"] or 0 for f in got)
        sub = ("%d · %d film%s · %d hours" if got[0]["year"] == got[-1]["year"]
               else "%d–%d · %d film%s · %d hours")
        args = ((got[0]["year"], len(got), "" if len(got) == 1 else "s",
                 round(mins / 60.0)) if got[0]["year"] == got[-1]["year"]
                else (got[0]["year"], got[-1]["year"], len(got),
                      "" if len(got) == 1 else "s", round(mins / 60.0)))
        sections.append({"id": ids[title], "title": title, "sub": sub % args,
                         "intro": intro_for(title), "items": items})
    sections[0]["open"] = True

    rows = [x for s in sections for x in s["items"]]
    assert len(rows) == 72, len(rows)
    assert len({x["id"] for x in rows}) == 72
    assert all(x.get("note") for x in rows), \
        [x["id"] for x in rows if not x.get("note")]
    assert sum(1 for x in rows if "q" in x) == 72
    if WEIGHTED:
        assert all(isinstance(x["w"], float) for x in rows)
        zero = [x["id"] for x in rows if x["w"] == 0]
        assert zero == ["kb-2022-one-way", "kb-2027-beach-read"], zero
    for s in sections:
        assert all(a["n"] <= b["n"] for a, b in zip(s["items"], s["items"][1:]))
    mins = sum(f["mins"] or 0 for f in films)
    hours = round(sum(x["w"] for x in rows), 2) if WEIGHTED else 0
    if WEIGHTED:
        assert abs(hours - mins / 60.0) < 0.3, (hours, mins / 60.0)

    # ---- the films this list shares with other lists here ------------------
    keys = {normt(f["t"]) + "|" + str(f["year"]) + "|f": f["t"] for f in films}
    qids = {f["qid"] + "|f": f["t"] for f in films if f["qid"]}
    shared = overlaps(keys, qids)
    # What was true when this was written. A NEW list arriving with one of
    # these films must not break the build — sibling agents ship lists daily
    # and the prose below is computed from `shared`, so a new pairing simply
    # joins the note. What must never change is that these nine still pair:
    # a group going missing means a title or a year drifted (CLU-191/CLU-247).
    for k, v in {
            "A24": ["MaXXXine"],
            "Best Picture": ["JFK", "A Few Good Men", "Apollo 13",
                             "Mystic River", "Frost/Nixon"],
            "Clint Eastwood": ["Mystic River"],
            "MCU Anthology": ["X-Men: First Class"],
            "Slashers": ["Friday the 13th"],
            "Tom Cruise": ["A Few Good Men"],
            "Tremors": ["Tremors"]}.items():
        assert shared.get(k) == v, (k, shared.get(k))
    paired = sorted({t for v in shared.values() for t in v},
                    key=[f["t"] for f in films].index)
    assert len(paired) >= 9, paired
    sharing = ("%s. Ticking one ticks the other: rows pair across lists by "
               "title and year, and by the film's Wikidata id where a list "
               "carries one, so a film watched here is watched there. Nothing "
               "is duplicated and no hours are counted twice, because every "
               "list totals only its own rows."
               % "; ".join("%s on %s" % (and_list(v), k)
                           for k, v in sorted(shared.items())))

    p = {
        "slug": SLUG,
        "title": "Kevin Bacon",
        "subtitle": "the films, in release order",
        "kind": "films",
        # The name travels further than the filmography does: "six degrees of
        # Kevin Bacon" is a phrase people use who could not name three of
        # these films, and Footloose is a household title. But he is a
        # character actor rather than a headline star, which keeps him under
        # Tom Cruise and Clint Eastwood at 79 and level with John Wayne at 72,
        # a notch above Robin Williams at 71 — and the difference between 71
        # and 72 is noise, which POPULARITY.md says out loud.
        "popularity": 72,
        "year": "1978–2027",
        "blurb": "Seventy-two films across six decades — about %d hours. The "
                 "actor the six-degrees game is named after, in the order the "
                 "films came out." % round(hours),
        "unit": {"one": "film", "many": "films"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        # Measured in CIELAB against every accent in properties/index.json;
        # see scratch/agent-bacon/accent.py. Everything obvious is taken and
        # taken closely — the Footloose warehouse red lands 0.9 from Dragon
        # Ball's, the denim indigo 1.8 from Samurai Champloo's, the Boston
        # slate 2.4 from Civil War's. This pair is the network teal the list's
        # own premise suggests, at 12.7 worst-case CIE76 against 15.0 for the
        # freest pair anywhere on the wheel (a magenta with nothing to do with
        # him). Nearest neighbours: The X-Files' #275E6B and Battlestar's
        # #24889E, both 12.7, and Hellboy's #66C2BC at 15.5 for the dark.
        "accent": "#507C86",
        "accentDark": "#229CA0",
        "tiers": False,
        "notes": [
            ["Films only, and the source drew that line.",
             "The filmography keeps television in its own section, so that is "
             "where it stays: %s credits including the two New York soaps he "
             "started on, the %s of The Following, I Love Dick, City on a "
             "Hill, and Taking Chance, the television film that won him the "
             "Golden Globe and the SAG award. The one video game credit is "
             "out for the same reason. This is the same rule the Clint "
             "Eastwood list here follows."
             % (word(len(tv)), following["cols"][2])],
            ["%d of the %d films the filmography lists."
             % (len(films), len(table)),
             "The ten it drops, every one on the source's own flag. %s short "
             "films, each marked Short film in the notes column — %s; four of "
             "them are not even linked to an article. Two rows whose footage "
             "is not in the film: Starting Over, where the source and the "
             "film's own cast list both say the scene was deleted though he "
             "kept the credit, and New York, I Love You, whose note says his "
             "segment was cut from the theatrical release — that film's "
             "article confirms the distributors dropped it after the festival "
             "premiere and never mentions him. And one television film, Tour "
             "de Pharmacy, which the source lists in both tables; the "
             "television one labels it, its own article opens with "
             "made-for-television, and Wikidata agrees. Films where he plays "
             "himself stay — the source flags none of those."
             % (word(len(shorts)).capitalize(),
                and_list([f["t"] for f in shorts]))],
            ["The sections are the article's own, except the last.",
             "Not six invented decades: five of them are the five career "
             "headings on the Kevin Bacon article, with their titles as "
             "written. The article stops at the 2010s and says so itself — "
             "the section carries a tag asking for the career past 2016 — so "
             "the 2020s heading is this list continuing the article's own "
             "scheme, and it is the only one that is not sourced."],
            ["Bar widths are runtimes, from each film's own infobox.",
             "One source for %d of the %d, so there is nothing to adjudicate. "
             "Wikidata's runtime property was the alternative and lost twice: "
             "it has no figure at all for %s, where the infobox does, and "
             "where both exist it disagrees by six minutes or more on %s "
             "films — White Water Summer at 120 minutes against an infobox "
             "90, Beverly Hills Cop: Axel F at 157 against 118. Two rows "
             "weigh nothing and say so on the row: Beach Read is not out, and "
             "One Way's article states no running time anywhere."
             % (len(films) - len(no_rt), len(films),
                and_list(sorted(wd_gaps)), word(len(wd_off)))],
            ["Two films have a second cut. Each still gets one row.",
             "A sweep of all %d articles for a sentence stating a running "
             "time beside a word meaning a particular version turns up JFK, "
             "whose Director's Cut runs %d minutes against a theatrical %d, "
             "and Hollow Man, whose infobox gives %d and then %d. Both bars "
             "measure the theatrical length and both notes name the other "
             "version. A second row would either double the film's hours — "
             "you do not watch it twice — or carry no weight in a list where "
             "everything else has some."
             % (len(films), jfk_dc, jfk["mins"], *hm["runtime_mins"])],
            ["%s of these films are on another list here."
             % word(len(paired)).capitalize(), sharing],
            "Roster, roles and the scope decisions from Wikipedia's Kevin "
            "Bacon filmography, read from the film and television tables "
            "themselves; the sections and the facts on the rows from the "
            "Kevin Bacon article; runtimes, release dates and the "
            "alternate-cut lengths from each film's own article; the "
            "cross-list ids from Wikidata.",
        ],
        "sections": sections,
    }

    out = prop.write(p)
    print("wrote %s — %d films, %d minutes, %.2f hours"
          % (out.name, len(rows), mins, hours))
    for s in sections:
        print("   %-12s %-12s %2d  %s"
              % (s["id"], s["title"], len(s["items"]), s["sub"]))
    print("   shared: %s"
          % "; ".join("%s: %s" % (k, ", ".join(v)) for k, v in sorted(shared.items())))


if __name__ == "__main__":
    main()
