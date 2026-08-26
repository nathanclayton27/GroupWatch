#!/usr/bin/env python3
"""Generate properties/jet-li.json.

    PYTHONIOENCODING=utf-8 python tools/make_jet-li.py

Jet Li's films in the order his filmography lists them, one row per film.
Everything here is machine-read from tools/data/jet-li.json, collected by
scratch/agent-jet/collect.py from Wikipedia's "Jet Li filmography", the
"Jet Li" article, each film's own article, and Wikidata. Nothing is typed in
from memory, and every claim the copy makes is asserted against the data that
produced it before anything is written.

THE ROSTER: THE FILM TABLE, ALL OF IT
-------------------------------------
A film is a row when the ==Film== table of "Jet Li filmography" lists him in
it, and the row says what the credit was — the character, and any producing
or directing credit the table's own Notes column records. That table has 48
rows and all 48 ship. Unlike the Kevin Bacon list, which dropped ten of 82 on
the source's own flags, this table flags nothing: no row says "short film",
none says his footage was cut, and none is duplicated in another table.

What is NOT here is what the source itself files elsewhere, in its own
separate sections of the same article:

  * **Six documentaries** — This is Kung Fu (1983), Dragons of the Orient and
    Abbot Hai Teng (1988), Lucky Way (1992), Shaolin Kung Fu (1994) and
    Li-Thal Weapon (1999). The table's own Notes column calls the first three
    a "Biographic role".
  * **One music video**, Aaliyah's "Try Again" (2000).
  * **One video game**, Jet Li: Rise to Honor (2004), where the source's own
    column heading is "Voice role".

And one thing the source contradicts itself about: the "Jet Li" article's
prose says "To promote tai chi, in 2012, Li starred in a film titled Tai Chi
and co-produced the movie with Chen Kuo-Fu." No film of that description is
in the Film table, in 2012 or any other year, so under the credit rule it is
not a row. The same prose records a role he did NOT take — he was announced
for XXX: Return of Xander Cage and replaced by Donnie Yen — which is likewise
not a credit and not a row.

Gong Shou Dao (2017) is a row and its own article calls it a short film. The
table does not flag it, and this file does not overrule the table; the row
says it runs twenty minutes so nobody is surprised by the bar.

ONCE UPON A TIME IN CHINA: FOUR OF SIX, AND THE SOURCE SAYS WHICH
-----------------------------------------------------------------
The series runs to six films and he is not in two of them. The filmography's
Film table lists Once Upon a Time in China (1991), II (1992), III (1993) and
Once Upon a Time in China and America (1997) — and does not list IV or V. The
series article agrees in its own infobox, which reads "Jet Li (I-III, VI)"
and "Vincent Zhao (IV-V)", and in its prose: Wong Fei-hung is "portrayed by
Jet Li in the first through third and sixth films and Vincent Zhao in the
fourth and fifth films". Each of the two absent films says the same on its own
page — IV's opens "It is the first not to star Jet Li as Wong Fei-hung, with
the main role instead played by Vincent Zhao", and V's has Zhao "reprising his
role ... after taking over the character from Jet Li in Once Upon a Time in
China IV". All four statements are asserted below.

One trap, and this file does not walk into it: the filmography's Notes column
says Once Upon a Time in China and America is "A.k.a. Once Upon a Time in
China IV". A different film released in 1993 carries exactly that title, and
he is not in it. So that row does NOT print the alternate as a plain "also
known as"; it names the confusion and resolves it.

FIST OF LEGEND IS NOT FIST OF FURY
----------------------------------
Fist of Legend (1994) is a remake of Bruce Lee's Fist of Fury (1972) — both
articles say so — and they are different films that must never pair across
lists. Different titles once normalised (fist of legend / fist of fury),
different years, different Wikidata items (Q1001759 / Q253565). main() asserts
all three, and asserts that no shipped row anywhere in properties/ carries
Fist of Fury's id or its title-and-year key alongside this one.

THE SECTIONS ARE THE ARTICLE'S CAREER HEADINGS, SPLIT ONCE AND EXTENDED ONCE
----------------------------------------------------------------------------
The "Jet Li" article's ==Acting career== section has exactly two subheadings,
Asia and International career. Those are the spine:

  * **Asia** is split in two at a line the article itself draws — his career
    began "in mainland China and then continuing into Hong Kong", and the lead
    dates the first part: he "made his acting debut with the Hong Kong film
    Shaolin Temple (1982) ... followed by two sequels in 1984 and 1986", which
    the career section groups as "The Shaolin Temple series (1, 2 and 3)".
    The films corroborate the split without being asked to: those three name
    China alongside Hong Kong in their own infoboxes, and every one of the 21
    films that follow names Hong Kong alone.
  * **International career** starts exactly where the article starts it: "In
    1998, he made his international film debut in Lethal Weapon 4."
  * The fourth heading is this list's, and it is the only one that is not
    sourced. The article's account stops with the two 2008 films and resumes
    at The Expendables — "After a one-year hiatus from filmmaking, Li returned
    to acting in 2010" — so the last section begins at the first row past that
    account.

WEIGHTS: ONE SOURCE, EACH FILM'S OWN INFOBOX
--------------------------------------------
Every bar is the running time stated in that film's own Wikipedia infobox, in
hours. All 48 have one. Wikidata's P2047 was the alternative and loses badly
on a filmography this heavily re-cut for export: it disagrees with the film's
own article by six minutes or more on six films — Black Mask at 83 against an
infobox 99, The Sorcerer and the White Snake at 120 against 102, Kung Fu Cult
Master at 107 against 95 — and has no figure at all for two of them.

ALTERNATE CUTS: ONE ROW EACH, THE HOME CUT, THE OTHER VERSION IN THE NOTE
-------------------------------------------------------------------------
Six films have a documented second version, which is what a career spent
being re-cut for Western release looks like. Four state it in the infobox
itself — Born to Defence (92 Hong Kong / 91 US), Swordsman II (107 Hong Kong /
99 US / 112 Taiwan), Dr. Wai (90 Hong Kong / 87 international) and Hero (99
theatrical / 110 director's cut) — and two state it in prose, Fearless (a
140-minute director's cut on DVD) and The Expendables (an extended cut with
"roughly 11 minutes of additional footage"). Each gets one row, per
HOW-IT-WORKS. The figure measured is the first the infobox states, which in
all four multi-figure cases is the film's own home market: the Hong Kong cut
of a Hong Kong film, the theatrical cut of Hero. The other versions are named
on the row.

CROSS-LIST SYNC
---------------
`q` is the film's Wikidata id, resolved from the wikilink the filmography
table's own title cell gives — never from a title lookup, which is how a
sibling list got a 1960 film onto a 1956 row this week. All 48 resolve and all
48 are P31 films. Three of them fail a publication-year gate against the
table's year (Born to Defence, The Master, Tai Chi Master) and keep their id
anyway: in each case the film's OWN article states the table's year, and
Wikidata's P577 is the outlier — which is exactly the disagreement `q` exists
to paper over (CLU-191).

Data:   scratch/agent-jet/collect.py -> tools/data/jet-li.json
Accent: scratch/agent-jet/accent.py, scratch/agent-jet/probe2.py
Sync:   scratch/agent-jet/sync.py
"""
import json
import pathlib
import re
import sys
import unicodedata

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop                                       # noqa: E402
from gwlib.prop import join_bits, slug                       # noqa: E402

SLUG = "jet-li"
ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "tools" / "data" / "jet-li.json"

# Flip to False to strip every bar. Every row has an infobox runtime, so this
# list has no unweighted rows and no zero-weight rows (CLU-131).
WEIGHTED = True

WORDS = ("no", "one", "two", "three", "four", "five", "six", "seven", "eight",
         "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
         "sixteen", "seventeen", "eighteen", "nineteen", "twenty",
         "twenty-one")

# Every non-"a.k.a." clause the source's Notes column puts on a row, turned
# into row prose. A clause that is not in here fails the build, so a rewrite
# upstream breaks it instead of shipping wikitext or silence.
SRC_NOTE = {
    "Directorial debut": "His directorial debut",
    "Also producer": "He produced it too",
    "Also associate producer": "He was an associate producer too",
    "Also producer and presenter": "He produced and presented it too",
    "filmed in 1989, but released in 1992":
        "Shot in 1989 and held back three years",
    "Released in 1999 in the U.S.": "The US release came three years later",
    "Released in 2004 in the U.S.": "The US release came two years later",
}

# The one alternate title this file refuses to print as a plain alternate,
# and why. See the docstring.
OUATIC_TRAP = "A.k.a. Once Upon a Time in China IV"

SECTION_TITLES = ["Shaolin Temple", "Hong Kong", "International career",
                  "The later career"]
SECTION_IDS = ["shaolin", "hk", "intl", "later"]


def word(n):
    return WORDS[n] if n < len(WORDS) else str(n)


def and_list(names):
    names = list(names)
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + " and " + names[-1]


def tidy(s):
    """Role strings arrive as `A/B/C`; space the slashes and collapse runs."""
    return re.sub(r"\s+", " ", s.replace("/", " / ")).strip()


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


def syncable_rows():
    """Every row on every other syncable list on disk, with its sync keys."""
    for f in sorted((ROOT / "properties").glob("*.json")):
        if f.stem in ("index", "search", SLUG):
            continue
        p = json.loads(f.read_text(encoding="utf-8"))
        if not isinstance(p, dict):
            continue
        kind = p.get("kind") or ""
        if p.get("secret") or not ("film" in kind or "game" in kind):
            continue
        prop_medium = "g" if "game" in kind else "f"
        for s in p.get("sections", []):
            for x in s.get("items", []):
                medium = x.get("m") or prop_medium
                keys = []
                y = year_of(x, str(x.get("n", "")))
                if y:
                    keys.append(normt(x["t"]) + "|" + y + "|" + medium)
                q = x.get("q")
                if isinstance(q, str) and re.fullmatch(r"Q[1-9]\d*", q):
                    keys.append(q + "|" + medium)
                yield p, x, keys


def overlaps(keys, qids):
    """{list title -> [film titles]} for every other syncable list on disk,
    matched on build.py's two lanes. Read off the catalogue so the note naming
    the shared films cannot go stale."""
    out = {}
    for p, x, ks in syncable_rows():
        hit = None
        for k in ks:
            hit = keys.get(k) or qids.get(k) or hit
        if hit and hit not in out.setdefault(p["title"], []):
            out[p["title"]].append(hit)
    return {k: v for k, v in out.items() if v}


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    films = data["films"]
    lab = data["p31_labels"]

    assert len(films) == 48, len(films)
    assert len(data["doc_rows"]) == 6, len(data["doc_rows"])
    assert len(data["mv_rows"]) == 1, len(data["mv_rows"])
    assert len(data["game_rows"]) == 1, len(data["game_rows"])

    def p31(f):
        return {lab.get(p, p) for p in f.get("p31") or []}

    # ---- the roster rule: the table flags nothing, so nothing is dropped ---
    for f in films:
        assert not re.search(r"short film|cut from|scene deleted|television",
                             f["note_src"], re.I), (f["t"], f["note_src"])
        assert f["target"] and f["qid"] and f["has_infobox"], f["t"]
        assert "film" in p31(f), (f["t"], p31(f))
    # and nothing in the film table is repeated in the source's other tables
    other = ({r["cols"][1] for r in data["doc_rows"]}
             | {r["cols"][1] for r in data["mv_rows"]}
             | {r["cols"][1] for r in data["game_rows"]})
    assert not ({f["t"] for f in films} & other), \
        sorted({f["t"] for f in films} & other)
    docs = [r["cols"][1] for r in data["doc_rows"]]
    assert docs[0].startswith("This is Kung Fu"), docs
    assert any("Biographic role" in r["cols"][2] for r in data["doc_rows"]), docs
    game = data["game_rows"][0]
    assert game["cols"][1] == "Jet Li: Rise to Honor", game["cols"]
    mv = data["mv_rows"][0]
    assert mv["cols"][1] == '"Try Again"' and mv["cols"][2].startswith("Aaliyah"), \
        mv["cols"]

    # the two things the article's prose records that the table does not
    career = data["career_text"]

    def career_says(phrase):
        assert phrase in career, \
            "the Acting career section no longer says: %s" % phrase
        return phrase

    career_says("To promote tai chi, in 2012, Li starred in a film titled Tai "
                "Chi and co-produced the movie with Chen Kuo-Fu")
    career_says("Li was initially stated to be appearing with Vin Diesel in "
                "XXX: Return of Xander Cage, but according to a Facebook post "
                "by Diesel, Li was replaced by Donnie Yen")
    # no row is that film, under that title, in that year or any other
    assert not any(normt(f["t"]) == "tai chi" for f in films), \
        [f["t"] for f in films if "Tai Chi" in f["t"]]
    assert [f["t"] for f in films if f["year"] == 2012] == ["The Expendables 2"]
    assert not any("Xander" in f["t"] for f in films)

    # ---- order: the source's own, which is release order wherever checkable
    for a, b in zip(films, films[1:]):
        assert a["year"] <= b["year"], (a["t"], b["t"])
    for a, b in zip(films, films[1:]):
        if a["year"] == b["year"] and a.get("release_dates") and \
                b.get("release_dates"):
            assert a["release_dates"][0] <= b["release_dates"][0], \
                (a["t"], b["t"], a["release_dates"], b["release_dates"])
    assert films[0]["t"] == "Shaolin Temple" and films[0]["year"] == 1982
    assert films[-1]["t"] == "Blades of the Guardians" and films[-1]["year"] == 2026
    assert films[-1]["release_dates"] == ["2026-02-17"], films[-1]["release_dates"]

    # ---- weights: each film's own infobox, first figure stated -------------
    # The four infoboxes that state several lengths label them, and the label
    # on the FIRST is asserted here: a source that reorders them breaks the
    # build rather than silently re-measuring the list.
    CUTS = {
        "Born to Defence": ("HK", [(91, "the US cut runs 91 minutes")]),
        "Swordsman II": ("Hong Kong",
                         [(99, "a US cut runs 99"),
                          (112, "a Mandarin-dubbed Taiwanese version runs 112")]),
        'Dr. Wai in "The Scripture with No Words"':
            ("Hong Kong", [(87, "the international cut runs 87")]),
        "Hero": ("theatrical", [(110, "a director's cut runs 110")]),
    }
    for f in films:
        mins = f["runtime_mins"]
        assert mins, (f["t"], f.get("runtime_raw"))
        f["mins"] = mins[0]
        assert 15 <= f["mins"] <= 200, (f["t"], f["mins"])
        if len(mins) > 1:
            assert f["t"] in CUTS, (f["t"], f["runtime_raw"])
            label, others = CUTS[f["t"]]
            head = f["runtime_raw"].split(str(mins[1]))[0]
            assert label in head, (f["t"], head, label)
            assert [o[0] for o in others] == mins[1:], (f["t"], mins)
    assert sorted(CUTS) == sorted(f["t"] for f in films
                                  if len(f["runtime_mins"]) > 1)

    # the two second cuts the infoboxes do not carry, read out of the prose
    fearless = next(f for f in films if f["t"] == "Fearless")
    dc = next(s for s in fearless["cut_sentences"] if "director's cut" in s)
    fearless_dc = int(re.search(r"(\d{3})-minute director's cut", dc).group(1))
    assert (fearless["mins"], fearless_dc) == (105, 140), \
        (fearless["mins"], fearless_dc)
    exp = next(f for f in films if f["t"] == "The Expendables")
    ext = next(s for s in exp["cut_sentences"] if "Extended Cut" in s)
    exp_extra = int(re.search(r"roughly (\d+) minutes of additional footage",
                              ext).group(1))
    assert (exp["mins"], exp_extra) == (103, 11), (exp["mins"], exp_extra)
    # nothing else on the page has a second cut
    PAT = re.compile(r"director'?s cut|extended (version|cut)|unrated|"
                     r"export version|uncut|re-?cut", re.I)
    cutfilms = sorted({f["t"] for f in films
                       if len(f["runtime_mins"]) > 1
                       or any(PAT.search(s) for s in f["cut_sentences"] or [])})
    assert cutfilms == sorted(list(CUTS) + ["Fearless", "The Expendables"]), \
        cutfilms

    # why Wikidata is not the source
    wd_gaps = sorted(f["t"] for f in films if not f["wd_runtime"])
    assert wd_gaps == ["Blades of the Guardians", "Fong Sai-yuk II"], wd_gaps
    wd_off = [(f["t"], f["mins"], f["wd_runtime"]) for f in films
              if f["wd_runtime"] and abs(f["mins"] - f["wd_runtime"]) >= 6]
    assert len(wd_off) == 6, wd_off
    for t, a, b in (("Black Mask", 99, 83),
                    ("The Sorcerer and the White Snake", 102, 120),
                    ("Kung Fu Cult Master", 95, 107)):
        g = next(f for f in films if f["t"] == t)
        assert (g["mins"], g["wd_runtime"]) == (a, b), (t, g["mins"], g["wd_runtime"])

    # ---- the Once Upon a Time in China question ---------------------------
    series = data["corroboration"]["Once Upon a Time in China (film series)"]
    assert "Jet Li (I-III, VI)" in series["starring"], series["starring"]
    assert "Vincent Zhao (IV-V)" in series["starring"], series["starring"]
    assert ("portrayed by Jet Li in the first through third and sixth films "
            "and Vincent Zhao in the fourth and fifth films"
            in series["first_sentences"]), series["first_sentences"]
    four = data["corroboration"]["Once Upon a Time in China IV"]
    assert ("It is the first not to star Jet Li as Wong Fei-hung, with the "
            "main role instead played by Vincent Zhao" in four["first_sentences"])
    five = data["corroboration"]["Once Upon a Time in China V"]
    assert ("taking over the character from Jet Li in Once Upon a Time in "
            "China IV" in five["first_sentences"]), five["first_sentences"]
    ouatic = [f["t"] for f in films if f["t"].startswith("Once Upon a Time")]
    assert ouatic == ["Once Upon a Time in China",
                      "Once Upon a Time in China II",
                      "Once Upon a Time in China III",
                      "Once Upon a Time in China and America"], ouatic
    # the roster does not, and must not, contain IV or V
    assert not any(f["qid"] in (data["extra_qids"]["Once Upon a Time in China IV"],
                                data["extra_qids"]["Once Upon a Time in China V"])
                   for f in films)
    america = next(f for f in films if f["t"].endswith("and America"))
    assert OUATIC_TRAP in america["note_src"], america["note_src"]
    ORDINAL = {"Once Upon a Time in China": "first",
               "Once Upon a Time in China II": "second",
               "Once Upon a Time in China III": "third",
               "Once Upon a Time in China and America": "sixth"}

    # ---- Fist of Legend is not Fist of Fury -------------------------------
    fol = next(f for f in films if f["t"] == "Fist of Legend")
    fury_q = data["extra_qids"]["Fist of Fury"]
    assert (fol["qid"], fury_q) == ("Q1001759", "Q253565"), (fol["qid"], fury_q)
    assert fol["qid"] != fury_q and normt(fol["t"]) != normt("Fist of Fury")
    assert fol["year"] == 1994, fol["year"]
    assert ("It is a remake of the 1972 martial arts film Fist of Fury "
            "starring Bruce Lee" in fol["first_sentences"]), \
        fol["first_sentences"]
    assert ("Fist of Legend (Chinese title: Jing Wu Ying Xiong), a remake of "
            "Bruce Lee's Fist of Fury (1972)" in career), "career prose moved"
    fol_keys = {normt(fol["t"]) + "|1994|f", fol["qid"] + "|f"}
    fury_keys = {normt("Fist of Fury") + "|1972|f", fury_q + "|f"}
    assert not (fol_keys & fury_keys), fol_keys & fury_keys
    # and no shipped row anywhere collides with either
    for p, x, ks in syncable_rows():
        assert not (set(ks) & fury_keys & fol_keys), (p["slug"], x["id"])
        if set(ks) & fury_keys:
            assert not (set(ks) & fol_keys), (p["slug"], x["id"], ks)

    # ---- sections ----------------------------------------------------------
    heads = data["career_heads"]
    assert heads == ["Asia", "International career"], heads
    career_says("beginning in mainland China and then continuing into Hong Kong")
    career_says("The Shaolin Temple series (1, 2 and 3)")
    career_says("In 1998, he made his international film debut in Lethal "
                "Weapon 4 which also marked the first time he had ever played "
                "a villain in a film")
    career_says("After a one-year hiatus from filmmaking, Li returned to "
                "acting in 2010, portraying a mercenary in the film The "
                "Expendables")
    bio = data["bio_lead_text"]
    for phrase in ("he made his acting debut with the Hong Kong film Shaolin "
                   "Temple (1982), a runaway success followed by two sequels "
                   "in 1984 and 1986",
                   "Li made his Hollywood debut as a villain in Lethal Weapon "
                   "4 (1998)",
                   "Li established himself as a leading action star with the "
                   "Once Upon a Time in China series (1991–1993)"):
        assert phrase in bio, "the Jet Li lead no longer says: %s" % phrase

    i_lw4 = next(i for i, f in enumerate(films) if f["t"] == "Lethal Weapon 4")
    i_late = next(i for i, f in enumerate(films) if f["year"] >= 2009)
    groups = [films[:3], films[3:i_lw4], films[i_lw4:i_late], films[i_late:]]
    assert [len(g) for g in groups] == [3, 21, 12, 12], [len(g) for g in groups]
    assert [g[0]["t"] for g in groups] == [
        "Shaolin Temple", "Born to Defence", "Lethal Weapon 4",
        "The Founding of a Republic"], [g[0]["t"] for g in groups]
    assert groups[1][-1]["t"] == "Hitman", groups[1][-1]["t"]
    assert groups[2][-1]["t"] == "The Mummy: Tomb of the Dragon Emperor"

    # the country field draws the same line the article's prose does
    def country(f):
        return re.sub(r"\s+", " ", (f.get("country") or "")
                      .replace("|", ", ").replace("*", "")).strip(" ,")
    for f in groups[0]:
        assert "China" in country(f) and "Hong Kong" in country(f), \
            (f["t"], country(f))
    hk_only = [f["t"] for f in films if country(f) == "Hong Kong"]
    assert hk_only == [f["t"] for f in groups[1]], hk_only
    # and China does not reappear in a country field until Hero
    china_again = [f["t"] for f in films[3:] if "China" in country(f)]
    assert china_again[0] == "Hero", china_again[:3]

    asia_back = [f["t"] for f in groups[2] if "United States" not in country(f)
                 and ("China" in country(f) or "Hong Kong" in country(f))]
    assert asia_back == ["Hero", "Fearless", "The Warlords"], asia_back
    us_late = [f["t"] for f in groups[3] if country(f) == "United States"]
    assert us_late == ["The Expendables", "The Expendables 2",
                       "The Expendables 3", "Mulan"], us_late

    # ---- row notes ---------------------------------------------------------
    def clauses(f):
        return [c.strip() for c in f["note_src"].split(";") if c.strip()]

    seen_clauses = set()

    def note_for(f):
        bits = ["As %s" % tidy(f["role"])] if f["role"] else []
        akas = []
        for c in clauses(f):
            seen_clauses.add(c)
            if c.lower().startswith("a.k.a."):
                if c == OUATIC_TRAP:
                    continue                      # handled below, deliberately
                akas.append(c[len("a.k.a."):].strip())
            else:
                bits.append(SRC_NOTE[c])
        if akas:
            bits.append("Also known as %s" % and_list(akas))
        t = f["t"]
        if t in ORDINAL:
            if t == "Once Upon a Time in China and America":
                bits.append(
                    "The sixth and last of the series, and his return to it "
                    "after two films he is not in")
                bits.append(
                    "The source's notes column calls it Once Upon a Time in "
                    "China IV; a separate 1993 film carries that title and "
                    "Vincent Zhao plays the part in it")
            else:
                bits.append("The %s of the series' six films" % ORDINAL[t])
                if t.endswith("III"):
                    bits.append("The last before the role was recast")
        if t == "Shaolin Temple":
            bits.append("His film debut")
        if t == "Kids From Shaolin":
            bits.append("The first of its two sequels")
        if t == "Martial Arts of Shaolin":
            bits.append("The second sequel, and the last of the three")
        if t == "Last Hero in China":
            bits.append("Wong Fei-hung again, outside the series")
        if t == "Fist of Legend":
            bits.append("A remake of Bruce Lee's Fist of Fury from 1972 — a "
                        "different film, and a separate row on any list here "
                        "that carries it")
        if t == "Lethal Weapon 4":
            bits.append("His Hollywood debut, and the first villain he played")
        if t == "Fearless":
            bits.append("The bar is the %d-minute theatrical version; a "
                        "director's cut runs %d"
                        % (fearless["mins"], fearless_dc))
        if t == "The Expendables":
            bits.append("The bar is the %d-minute theatrical version; an "
                        "extended cut adds about %s minutes"
                        % (exp["mins"], word(exp_extra)))
        if t == "The Forbidden Kingdom":
            bits.append("The first time he and Jackie Chan appeared on screen "
                        "together")
        if t == "Gong Shou Dao":
            bits.append("Twenty minutes long; its own article calls it a "
                        "short film, though the source's table does not")
        if t == "Blades of the Guardians":
            bits.append("Released in February 2026, the newest film here")
        if t in CUTS:
            label, others = CUTS[t]
            where = ("theatrical version" if label == "theatrical"
                     else "Hong Kong cut")
            bits.append("The bar is the %d-minute %s; %s"
                        % (f["mins"], where, and_list([o[1] for o in others])))
        return join_bits(*bits)

    # ---- section intros ----------------------------------------------------
    # the recurring parts, counted rather than remembered
    roles = {}
    for f in groups[1]:
        roles[f["role"]] = roles.get(f["role"], 0) + 1
    assert roles["Wong Fei-hung"] == 5, roles
    assert roles["Fong Sai-yuk"] == 2, roles
    assert roles["Chen Zhen"] == 1, roles

    def hours(g):
        return sum(f["mins"] for f in g) / 60.0

    def intro_for(i):
        g = groups[i]
        if i == 0:
            return ("Three films shot in mainland China, and the source keeps "
                    "them together — the career section calls them the Shaolin "
                    "Temple series and credits them with the rebirth of the "
                    "real temple, and the lead dates the run: a debut in 1982 "
                    "and two sequels, in 1984 and 1986. All three name China "
                    "alongside Hong Kong in their own infoboxes. Nothing else "
                    "on this page does until 2002.")
        if i == 1:
            return ("Eleven years the career is built on, and it is Hong Kong "
                    "and nothing else: every one of these %s films names Hong "
                    "Kong alone as its country, and no film outside this "
                    "section does. He plays Wong Fei-hung %s times here, Fong "
                    "Sai-yuk %s, and Chen Zhen once."
                    % (word(len(g)), word(roles["Wong Fei-hung"]),
                       "twice" if roles["Fong Sai-yuk"] == 2
                       else "%s times" % word(roles["Fong Sai-yuk"])))
        if i == 2:
            return ("The article's own second career heading, starting where "
                    "the article starts it: his international debut in Lethal "
                    "Weapon 4, which was also the first villain he played. "
                    "%s films, about %d hours, and three of them made back in "
                    "Asia between the Hollywood ones."
                    % (word(len(g)).capitalize(), round(hours(g))))
        return ("The only heading here the article does not supply. Its "
                "account stops with the two 2008 films and picks up again at "
                "The Expendables, calling 2009 a one-year hiatus — so this "
                "section starts at the first row past that account. %s films: "
                "three Expendables, a Disney remake, and eight made in China "
                "or Hong Kong." % word(len(groups[3])).capitalize())

    # ---- build --------------------------------------------------------------
    sections = []
    for i, g in enumerate(groups):
        items = []
        for f in g:
            it = {"id": "jl-%d-%s" % (f["year"], slug(f["t"])),
                  "t": f["t"], "n": str(f["year"])}
            if WEIGHTED:
                it["w"] = round(f["mins"] / 60.0, 2)
            note = note_for(f)
            if note:
                it["note"] = note
            # the Wikidata id, from the table's own wikilink, gated on the
            # item being a film. NOT gated on the year: see the docstring.
            it["q"] = f["qid"]
            items.append(it)
        mins = sum(f["mins"] for f in g)
        span = ("%d" % g[0]["year"] if g[0]["year"] == g[-1]["year"]
                else "%d–%d" % (g[0]["year"], g[-1]["year"]))
        sections.append({
            "id": SECTION_IDS[i], "title": SECTION_TITLES[i],
            "sub": "%s · %d film%s · %d hours"
                   % (span, len(g), "" if len(g) == 1 else "s",
                      round(mins / 60.0)),
            "intro": intro_for(i), "items": items})
    sections[0]["open"] = True

    # every clause the source wrote on a shipped row was accounted for
    assert seen_clauses == {c for f in films for c in clauses(f)}, \
        sorted(seen_clauses ^ {c for f in films for c in clauses(f)})
    assert set(SRC_NOTE) == {c for c in seen_clauses
                             if not c.lower().startswith("a.k.a.")}, \
        sorted(set(SRC_NOTE) ^ {c for c in seen_clauses
                                if not c.lower().startswith("a.k.a.")})

    rows = [x for s in sections for x in s["items"]]
    assert len(rows) == 48, len(rows)
    assert len({x["id"] for x in rows}) == 48
    assert all(x.get("note") for x in rows), \
        [x["id"] for x in rows if not x.get("note")]
    assert sum(1 for x in rows if "q" in x) == 48
    assert len({x["q"] for x in rows}) == 48
    # every row numbers by a plain year, so build.py's sync never falls back
    # to reading a year out of a note — several notes name one
    assert all(re.fullmatch(r"(18|19|20)\d{2}", x["n"]) for x in rows)
    if WEIGHTED:
        assert all(isinstance(x["w"], float) and x["w"] > 0 for x in rows)
    for s in sections:
        assert all(a["n"] <= b["n"] for a, b in zip(s["items"], s["items"][1:]))
    mins = sum(f["mins"] for f in films)
    total = round(sum(x["w"] for x in rows), 2) if WEIGHTED else 0
    if WEIGHTED:
        assert abs(total - mins / 60.0) < 0.3, (total, mins / 60.0)

    # ---- the films this list shares with other lists here ------------------
    keys = {normt(f["t"]) + "|" + str(f["year"]) + "|f": f["t"] for f in films}
    qids = {f["qid"] + "|f": f["t"] for f in films}
    shared = overlaps(keys, qids)
    paired = sorted({t for v in shared.values() for t in v},
                    key=[f["t"] for f in films].index)
    if shared:
        sharing = ["%s of these films %s already on another list here."
                   % (word(len(paired)).capitalize(),
                      "is" if len(paired) == 1 else "are"),
                   "%s. Ticking one ticks the other: rows pair across lists by "
                   "title and year, and by the film's Wikidata id where a list "
                   "carries one, so a film watched here is watched there. "
                   "Nothing is duplicated and no hours are counted twice, "
                   "because every list totals only its own rows."
                   % "; ".join("%s on %s" % (and_list(v), k)
                               for k, v in sorted(shared.items()))]
    else:
        sharing = ["None of these films is on another list here yet.",
                   "Every row carries the film's Wikidata id as well as its "
                   "title and year, which is what pairs a row across lists, so "
                   "the moment another list here carries The Forbidden "
                   "Kingdom, Hero or an Expendables film, ticking it there "
                   "ticks it here and the other way round. Nothing is "
                   "duplicated and no hours are counted twice, because every "
                   "list totals only its own rows."]

    p = {
        "slug": SLUG,
        "title": "Jet Li",
        "subtitle": "the films, in the order they came out",
        "kind": "films",
        # The wushu champion who became Wong Fei-hung and then a Hollywood
        # villain: Lethal Weapon 4, Romeo Must Die, three Expendables and a
        # Disney Mulan carry the name a long way outside kung fu cinema, and
        # Hero was the highest-grossing Chinese film of its day. But he is not
        # the household word Jackie Chan or Bruce Lee is in the West, so this
        # sits at the floor of the 70s band — under Kevin Bacon at 72 and
        # Robin Williams at 71, level with Mission: Impossible at 70, above
        # Nicolas Cage at 65. The gap to 71 is noise and POPULARITY.md says so.
        "popularity": 70,
        "year": "1982–2026",
        "blurb": "Forty-eight films across five decades — about %d hours. "
                 "The wushu champion who became Wong Fei-hung, then "
                 "Hollywood's villain." % round(total),
        "unit": {"one": "film", "many": "films"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        # Measured in CIELAB against every accent in properties/ — see
        # scratch/agent-jet/accent.py and probe2.py. Everything obvious is
        # taken and taken closely: the Once Upon a Time in China lacquer red
        # lands 2.1 from Gurren Lagann's, Hero's blue chapter 1.0 from Vinland
        # Saga's, Hero's green 3.1 from Zelda's, the wushu ochre 4.5 from
        # Mission: Impossible's. This pair is the saffron of a Shaolin robe —
        # the three films that open the list — at 16.0 worst-case CIE76, which
        # beats the freest pair the coarse scan found anywhere on the wheel.
        # Nearest neighbours: Coen Brothers' #6E5533 at 16.4 for the light and
        # James Bond's #C9B458 at 16.0 for the dark.
        "accent": "#4B3A02",
        "accentDark": "#A48932",
        "tiers": False,
        "notes": [
            ["Films only, and the source drew that line.",
             "The filmography keeps everything else in its own sections of the "
             "same article, so that is where they stay: %s documentaries, the "
             "first three of them filed under a Biographic role; the Aaliyah "
             "video for Try Again; and one video game, Jet Li: Rise to Honor, "
             "under a column headed Voice role. This is the rule the Kevin "
             "Bacon and Clint Eastwood lists here follow."
             % word(len(data["doc_rows"]))],
            ["All %d films the filmography lists, and nothing else."
             % len(films),
             "A film is a row when the source's own Film table lists him in "
             "it, and the row says what the credit was — the character, "
             "plus any producing or directing credit the table's notes "
             "record. Nothing is dropped, because unlike other filmographies "
             "here the table flags nothing: no row is marked a short film, "
             "none says his footage was cut, and none is repeated in another "
             "table. Two things the article's prose mentions are still not "
             "rows, because the table does not list them: a 2012 film called "
             "Tai Chi that he starred in and co-produced, which appears "
             "nowhere in the table under any year, and XXX: Return of Xander "
             "Cage, which he was announced for and Donnie Yen replaced him "
             "on. Gong Shou Dao (2017) is a row and its own article calls it "
             "a short film; the table does not, so it stays, and the row says "
             "it runs twenty minutes."],
            ["Once Upon a Time in China: four of the six.",
             "He is not in two of them, and this is the kind of gap a list "
             "gets quietly wrong. The Film table lists the 1991 original, II, "
             "III and Once Upon a Time in China and America, and does not "
             "list IV or V. The series article says the same in its own "
             "infobox — Jet Li (I-III, VI), Vincent Zhao (IV-V) — "
             "and so does each absent film: IV's article opens by saying it "
             "is the first not to star him, and V's has Zhao reprising the "
             "part he took over. One trap survives in the source and this "
             "list does not repeat it: the table's notes call the 1997 film "
             "an alias of Once Upon a Time in China IV, but a separate 1993 "
             "film carries that title and he is not in it, so that row names "
             "the confusion instead of printing the alias."],
            ["Fist of Legend is not Fist of Fury.",
             "The 1994 film is a remake of Bruce Lee's 1972 one — both "
             "articles say so, and this list's own source says so — and "
             "they are two different films twenty-two years apart. They pair "
             "with nothing of each other's: different titles, different "
             "years, and different Wikidata items, all three checked when "
             "this file is built. A list here that carries Fist of Fury gets "
             "its own row for it, and ticking one has no effect on the other."],
            ["The sections are the article's career headings, split once and "
             "extended once.",
             "The Acting career section has exactly two subheadings, Asia and "
             "International career. Asia is split in two on a line the "
             "article itself draws — the career began in mainland China "
             "and continued into Hong Kong — and the films agree without "
             "being asked: the three Shaolin Temple films name China "
             "alongside Hong Kong in their own infoboxes, and the %s that "
             "follow name Hong Kong alone. International career starts "
             "exactly where the article starts it, at Lethal Weapon 4 in "
             "1998. The fourth heading is this list's own: the article's "
             "account stops with the two 2008 films and resumes at The "
             "Expendables, calling 2009 a one-year hiatus."
             % word(len(groups[1]))],
            ["Bar widths are runtimes, from each film's own infobox.",
             "One source for all %d, so there is nothing to adjudicate, and "
             "no row weighs nothing. Wikidata's runtime property was the "
             "alternative and lost badly on a filmography this heavily re-cut "
             "for export: it disagrees with the film's own article by six "
             "minutes or more on %s films — Black Mask at 83 minutes "
             "against an infobox 99, The Sorcerer and the White Snake at 120 "
             "against 102, Kung Fu Cult Master at 107 against 95 — and "
             "carries no figure at all for two others."
             % (len(films), word(len(wd_off)))],
            ["%s films have a second version. Each still gets one row."
             % word(len(cutfilms)).capitalize(),
             "Which is what a career spent being re-cut for Western release "
             "looks like. Four state it in the infobox itself: Born to "
             "Defence at 92 minutes in Hong Kong and 91 in the US, Swordsman "
             "II at 107 in Hong Kong, 99 in the US and 112 in a "
             "Mandarin-dubbed Taiwanese version, Dr. Wai at 90 against an "
             "87-minute international cut, and Hero at 99 theatrical against "
             "a 110-minute director's cut. Two more say it in prose: "
             "Fearless, whose director's cut runs %d minutes, and The "
             "Expendables, whose extended cut adds roughly %d. Every bar "
             "measures the first figure the infobox states, which is the "
             "film's own home market in all four — the Hong Kong cut of "
             "a Hong Kong film, the theatrical cut of Hero — and every "
             "row names the other version. A second row would either double "
             "the film's hours, which you do not watch twice, or carry no "
             "weight in a list where everything else has some."
             % (fearless_dc, exp_extra)],
            sharing,
            "Roster, roles, alternate titles and the scope decisions from "
            "Wikipedia's Jet Li filmography, read from the film, documentary, "
            "music video and video game tables themselves; the sections and "
            "the career facts from the Jet Li article; runtimes, release "
            "dates, countries and the alternate-cut lengths from each film's "
            "own article; the Once Upon a Time in China casting from the "
            "series article and from the two films he is not in; the "
            "cross-list ids from Wikidata.",
        ],
        "sections": sections,
    }

    out = prop.write(p)
    print("wrote %s — %d films, %d minutes, %.2f hours"
          % (out.name, len(rows), mins, total))
    for s in sections:
        g = s["items"]
        print("   %-8s %-22s %2d  %-28s %6.1f h"
              % (s["id"], s["title"], len(g), s["sub"],
                 sum(x["w"] for x in g) if WEIGHTED else 0))
    print("   shared: %s"
          % ("; ".join("%s: %s" % (k, ", ".join(v))
                       for k, v in sorted(shared.items())) or "nothing yet"))


if __name__ == "__main__":
    main()
