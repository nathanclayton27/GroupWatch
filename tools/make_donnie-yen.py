#!/usr/bin/env python3
"""Generate properties/donnie-yen.json.

    PYTHONIOENCODING=utf-8 python tools/make_donnie-yen.py

Donnie Yen's films, year by year, one row per film. Everything here is
machine-read from tools/data/donnie-yen.json, collected by
scratch/agent-donnie/collect.py from Wikipedia's "Donnie Yen filmography",
the "Donnie Yen" article, each film's own article, and Wikidata. Nothing is
typed in from memory, and every claim the copy makes is asserted against the
data that produced it before anything is written.

THE CREDIT RULE: THE FILM TABLE, AND EVERY ROW SAYS WHAT THE CREDIT WAS
-----------------------------------------------------------------------
A film is a row when the source's own ==Film== table lists him in it — and
the row's note says what he was on it. That matters more here than on an
ordinary actor list, because Yen is an action director, a director and a
producer as well as a star, and the filmography records all four kinds of
credit in one table. Seven of the 78 rows are his as crew rather than as
cast: the source's Role column says {{n/a}} and its Notes column names the
job. Those rows are kept and labelled, the way the-wachowskis and eastwood
carry the role on each row, rather than being silently admitted or silently
dropped.

The table lists 80 films. 78 are rows. The two it drops are dropped on the
source's own flags, never on this file's opinion:

  * **Gong Shou Dao (2017)** — the Notes column says "Short film", the film's
    own article opens "a 2017 Chinese kung fu short film", its infobox says
    20 minutes, and the Donnie Yen article calls it "The full GSD 20 minutes
    short film". Same flag, same treatment as the seven shorts the Kevin
    Bacon list drops.
  * **Caine** — the year column says "TBA" and the Notes column says
    "Filming". Its article's infobox has an empty `released` field and an
    empty `runtime` field, it has no ==Release== section, and no sentence
    anywhere in it names a release date or year: the latest thing it can say
    is that principal photography began in Budapest on 25 April 2026. Under
    the house rule for announced work — a source-given release date makes it
    a row, a year alone is enough, and undated work stays off entirely — it
    is undated, so it stays off. It is the film Yen is directing and starring
    in for the John Wick franchise, and it should be added the day the source
    dates it.

Nothing else is filtered. Cameos stay (the source flags three), rows where
he is only the action director stay, and the Ip Man spin-off he produced but
does not appear in stays — with a note saying exactly that.

THE IP MAN ROWS COME FROM THE TABLE, NOT FROM THE SERIES ARTICLE
----------------------------------------------------------------
Five rows touch the series and they are not interchangeable. Ip Man (2008),
Ip Man 2 (2010), Ip Man 3 (2015) and Ip Man 4: The Finale (2019) are his,
and the note on each says which entry it is. Master Z: Ip Man Legacy (2018)
is the spin-off: the source's Role column is {{n/a}}, its Notes column says
"Producer", the film's own article opens "produced by Raymond Wong, Donnie
Yen, and Dave Bautista", his name is not in its cast list, and the Donnie
Yen lead says he "served as a co-producer of the spin-off". So it is a row
whose note says he is not in it. Taking the roster from the series article
instead would have swept in The Legend Is Born, The Final Fight and Ip Man:
Kung Fu Master, none of which he is in and none of which the table lists.

TELEVISION AND GAMES ARE OUT, AND THE SOURCE IS WHY
---------------------------------------------------
The filmography keeps television in its own ==Television== section — eight
rows, the TVB and ATV series he started on, including the Fist of Fury
series — and its two video game credits in a third. That separation is the
line this list takes, exactly as the Kevin Bacon and Clint Eastwood lists
take it.

THE SECTIONS ARE THE ARTICLE'S OWN FOUR CAREER HEADINGS
--------------------------------------------------------
Not four invented eras: the four ===…=== subheadings of the ==Career==
section on the "Donnie Yen" article, with their titles as written —
"Beginnings to the 1990s", "2000s: Breakthrough success", "2010s", "2020s".
They happen to divide the filmography exactly where a reader would want it
divided: the Hong Kong apprenticeship and the years he became an action
director, the Hollywood-choreography-and-breakthrough decade that ends with
Ip Man, the Ip Man decade that ends with Rogue One, and the international
run. SECTION_IDS is asserted against the wikitext, so a rewrite upstream
breaks the build instead of shipping a stale scheme.

Within a year the order is the source's own table order, not a release-date
sort. Six of these films have no Wikipedia article at all, so six rows have
no release date to sort on, and inventing a position for them would be a
guess dressed as data.

NO BARS ON THIS LIST, AND THE REASON IS SIX MISSING ARTICLES
-------------------------------------------------------------
Six titles in the source's table carry no wikilink — Holy Virgin vs. the
Evil Dead (1991), Asian Cop: High Voltage (1995), City of Darkness (1999),
Together (2013), Iceman: The Time Traveller (2018) and Come Back Home
(2022) — and a search finds no article under any other name for any of
them. No article means no infobox, no Wikidata item, no P2047: there is no
runtime to be had at any price. All's Well, Ends Well 2009's article exists
but leaves its runtime field empty.

CLU-131 is all-or-nothing: a row with NO `w` on a weighted list silently
counts as one hour. So this list ships **unweighted** — every row carries no
`w`, TOTALW === TOTAL, and every figure reduces to the film count. There is
deliberately no WEIGHTED switch to flip: 71 of the 78 rows could be weighed
from their own infoboxes today, and doing it would quietly price the other
seven at an hour each, which is the exact bug CLU-131 names. Weighting this
list means finding a runtime for all seven first, and main() asserts which
seven they are so a future attempt starts from the real gap.

That decision also disposes of the `w: 0` trap. On an unweighted list a
single `w: 0` row would flip `WEIGHTED = DATA.some(x => typeof x.w ===
'number')` on and price every other row at one hour, so no row here carries
one — which is fine, because the only announced film is undated and is not a
row at all.

TITLES: THE SOURCE'S TITLE, THE SOURCE'S ALTERNATES
----------------------------------------------------
Hong Kong films routinely carry several English names and this filmography
records them: the row title is the title the table's own link text uses, and
every "a.k.a." the Notes column gives is in the row note. In the Line of
Duty 4: Witness alone carries three.

CROSS-LIST SYNC
---------------
`q` is the film's Wikidata id, resolved from the wikilink the table's own
title cell gives — never from a title lookup — and gated on the item's P31
saying "film" and on its publication years agreeing with the table's year.
72 of the 78 rows carry one; the six with no article carry none, because a
row that cannot be resolved confidently ships with no id rather than a wrong
one.

Data:   scratch/agent-donnie/collect.py -> tools/data/donnie-yen.json
Checks: scratch/agent-donnie/inspect.py, scratch/agent-donnie/sync.py
Accent: scratch/agent-donnie/accent.py, scratch/agent-donnie/scan.py
"""
import json
import pathlib
import re
import sys
import unicodedata

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop                                       # noqa: E402
from gwlib.prop import join_bits, slug                       # noqa: E402

SLUG = "donnie-yen"
ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "tools" / "data" / "donnie-yen.json"

WORDS = ("no", "one", "two", "three", "four", "five", "six", "seven", "eight",
         "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
         "sixteen", "seventeen", "eighteen", "nineteen", "twenty",
         "twenty-one", "twenty-two", "twenty-three", "twenty-four",
         "twenty-five", "twenty-six", "twenty-seven", "twenty-eight",
         "twenty-nine", "thirty")

# The source's Notes column, minus its a.k.a. lines, turned into row prose.
# Every distinct flag in the whole table must appear here or main() fails, so
# a rewrite upstream breaks the build instead of shipping wikitext or silence.
# A None value belongs to a row this list does not ship.
CREDIT = {
    # he is in it, and did a job on it as well
    "Also action director": "He was the action director too",
    "Also action choreographer": "He was the action choreographer too",
    "Also martial arts choreographer": "He was the martial arts choreographer too",
    "Also action director and executive producer":
        "He was the action director and an executive producer too",
    "Also action director and producer":
        "He was the action director and a producer too",
    "Also director and action director":
        "He directed it and was the action director",
    "Also director and co-producer": "He directed and co-produced it",
    "Also director, producer and action director":
        "He directed and produced it, and was the action director",
    "Also director, producer, action director and co-writer":
        "He directed, produced and co-wrote it, and was the action director",
    "Also producer": "He produced it too",
    "Cameo": "A cameo",
    # the source gives him no role at all: the credit IS the reason for the row
    "Stuntman": "A stuntman credit; the source gives him no role",
    "Action director": "Action director; the source gives him no role",
    "Action choreographer":
        "Action choreographer; the source gives him no role",
    "Co-director and action director":
        "He co-directed it and was the action director; the source gives him "
        "no role",
    "Producer": "Producer; the source gives him no role",
    # rows this list does not ship
    "Short film": None,
    "Filming": None,
    "Also director": None,
}

# The four ===…=== headings of the article's ==Career== section, in order,
# with the year span each governs and the section id it becomes.
SECTIONS = [
    ("Beginnings to the 1990s", 0, 1999, "early"),
    ("2000s: Breakthrough success", 2000, 2009, "d2000"),
    ("2010s", 2010, 2019, "d2010"),
    ("2020s", 2020, 9999, "d2020"),
]

IPMAN = {"Ip Man": "The first of the four Ip Man films",
         "Ip Man 2": "The second Ip Man film",
         "Ip Man 3": "The third Ip Man film",
         "Ip Man 4: The Finale": "The fourth and last Ip Man film"}


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
    cannot go stale — sibling agents ship lists daily."""
    out = {}
    for f in sorted((ROOT / "properties").glob("*.json")):
        if f.stem in ("index", "search", SLUG):
            continue
        p = json.loads(f.read_text(encoding="utf-8"))
        kind = p.get("kind") or ""
        if p.get("secret") or not ("film" in kind or "game" in kind):
            continue
        prop_medium = "g" if "game" in kind else "f"
        for s in p.get("sections", []):
            for x in s.get("items", []):
                medium = x.get("m") or prop_medium
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
    games = data["game_rows"]
    lab = data["p31_labels"]

    assert len(table) == 80, len(table)
    assert len(tv) == 8, len(tv)
    assert len(games) == 2, len(games)

    def p31(f):
        return {lab.get(p, p) for p in f.get("p31") or []}

    # ---- the roster rule, and the two rows it drops ----------------------
    shorts = [f for f in table if "Short film" in f["flags"]]
    assert [f["t"] for f in shorts] == ["Gong Shou Dao"], shorts
    gsd = shorts[0]
    assert gsd["runtime_mins"] == [20], gsd["runtime_mins"]
    assert "short film" in gsd["first_sentences"].lower(), gsd["first_sentences"]
    assert "The full GSD 20 minutes short film" in data["career_text"], \
        "the career section no longer calls Gong Shou Dao a 20-minute short"

    undated = [f for f in table if not f["year"]]
    assert [f["t"] for f in undated] == ["Caine"], undated
    caine = undated[0]
    assert caine["year_cell"] == "TBA", caine["year_cell"]
    assert "Filming" in caine["flags"], caine["flags"]
    # the article's own silence is what keeps it off: no released field, no
    # runtime, and not one year of release anywhere in its prose
    assert caine["has_infobox"] and not caine["released_raw"] \
        and not caine["release_dates"] and not caine["runtime_mins"], caine
    assert "Release" not in caine["heads"], caine["heads"]
    assert caine["release_claim"] == [], caine["release_claim"]
    assert any("Budapest" in s for s in caine["photography"]), \
        caine["photography"]

    dropped = {f["t"] for f in shorts + undated}
    assert len(dropped) == 2, sorted(dropped)
    films = [f for f in table if f["t"] not in dropped]
    assert len(films) == 78, len(films)
    for a, b in zip(films, films[1:]):
        assert a["year"] <= b["year"], (a["t"], b["t"])
    assert (films[0]["t"], films[0]["year"]) == ("Shaolin Drunkard", 1983)
    assert (films[-1]["t"], films[-1]["year"]) == ("The Prosecutor", 2024)

    # ---- every credit the source states is accounted for ------------------
    all_flags = {p for f in table for p in f["flags"]}
    assert all_flags == set(CREDIT), sorted(all_flags ^ set(CREDIT))
    for f in films:
        for p in f["flags"]:
            assert CREDIT[p], (f["t"], p)
        assert f["role"] or f["flags"], f["t"]      # every row can say something

    # the seven rows that are his as crew, not as cast
    crew = [f for f in films if not f["role"]]
    assert [f["t"] for f in crew] == [
        "Shaolin Drunkard", "Moonlight Express", "The Princess Blade",
        "The Twins Effect", "Protégé de la Rose Noire", "Stormbreaker",
        "Master Z: Ip Man Legacy"], [f["t"] for f in crew]
    action = [f for f in films
              if any(re.search(r"action director|choreograph", p, re.I)
                     for p in f["flags"])]
    assert len(action) == 27, len(action)
    # "director" NOT preceded by "action" — otherwise Flash Point and Dragon
    # Tiger Gate, where he is the action director and a producer, read as
    # films he directed, which he did not
    directed = [f for f in films
                if any(re.search(r"(?<!action )(?<!Action )\bdirector\b", p)
                       for p in f["flags"])]
    assert [f["t"] for f in directed] == [
        "Legend of the Wolf", "Ballistic Kiss", "Shanghai Affairs",
        "The Twins Effect", "Protégé de la Rose Noire", "Sakra",
        "The Prosecutor"], [f["t"] for f in directed]

    # ---- the Ip Man rows --------------------------------------------------
    ip = [f for f in films if f["t"] in IPMAN]
    assert [f["t"] for f in ip] == ["Ip Man", "Ip Man 2", "Ip Man 3",
                                    "Ip Man 4: The Finale"], ip
    assert [f["year"] for f in ip] == [2008, 2010, 2015, 2019], ip
    mz = next(f for f in films if f["t"] == "Master Z: Ip Man Legacy")
    assert not mz["role"] and mz["flags"] == ["Producer"], mz
    assert "produced by Raymond Wong, Donnie Yen, and Dave Bautista" \
        in mz["first_sentences"], mz["first_sentences"]
    assert "co-producer of the spin-off Master Z: Ip Man Legacy" \
        in data["bio_lead_text"], "the lead no longer calls Master Z a spin-off"
    # and the reverse: the table names no other Ip Man film. The Legend Is
    # Born, Ip Man: The Final Fight and Ip Man: Kung Fu Master all exist and
    # he is in none of them, which is exactly what taking the roster from the
    # table rather than from the series article buys.
    ipish = sorted(f["t"] for f in table if "Ip Man" in f["t"])
    assert ipish == ["Ip Man", "Ip Man 2", "Ip Man 3", "Ip Man 4: The Finale",
                     "Master Z: Ip Man Legacy"], ipish

    # ---- runtimes: why the list is unweighted ------------------------------
    no_rt = [f for f in films if not (f.get("runtime_mins") or [])]
    assert [f["t"] for f in no_rt] == [
        "Holy Virgin vs. the Evil Dead", "Asian Cop: High Voltage",
        "City of Darkness", "All's Well, Ends Well 2009", "Together",
        "Iceman: The Time Traveller", "Come Back Home"], [f["t"] for f in no_rt]
    unlinked = [f for f in films if not f["target"]]
    assert len(unlinked) == 6, [f["t"] for f in unlinked]
    assert all(not f.get("has_infobox") and not f["qid"] and not f["p2047_seen"]
               for f in unlinked), [f["t"] for f in unlinked]
    awew = next(f for f in films if f["t"] == "All's Well, Ends Well 2009")
    assert awew["has_infobox"] and not awew["runtime_raw"], awew.get("runtime_raw")
    mins = sum((f.get("runtime_mins") or [0])[0] for f in films)
    weighable = len(films) - len(no_rt)
    assert weighable == 71, weighable

    # the two rows the source's own infobox gives two lengths for
    hero = next(f for f in films if f["t"] == "Hero")
    assert hero["runtime_mins"] == [99, 110], hero["runtime_mins"]
    assert "Director's Cut" in hero["runtime_raw"], hero["runtime_raw"]
    ice = next(f for f in films if f["t"] == "Iceman")
    assert ice["runtime_mins"] == [104, 91], ice["runtime_mins"]
    assert "Hong Kong" in ice["runtime_raw"] and "China" in ice["runtime_raw"], \
        ice["runtime_raw"]
    multi = [f["t"] for f in films if len(f.get("runtime_mins") or []) > 1]
    assert multi == ["Hero", "Iceman"], multi

    # ---- the facts the notes are built from, read out of the article ------
    career = data["career_text"]
    bio = data["bio_lead_text"]

    def career_says(phrase):
        assert phrase in career, \
            "the Career section no longer says: %s" % phrase
        return phrase

    def bio_says(phrase):
        assert phrase in bio, "the Donnie Yen lead no longer says: %s" % phrase
        return phrase

    career_says("Yen's first step into the film industry was when he landed "
                "his first starring role in the 1984 film Drunken Tai Chi")
    career_says("Yen made his breakthrough role as General Nap-lan in Once "
                "Upon a Time in China II (1992), which included a fight scene "
                "between his character and Wong Fei-hung (portrayed by Jet Li)")
    career_says("In 1997, Yen started the production company Bullet Films, "
                "and made his directorial debut in Legend of the Wolf (1997)")
    career_says("Yen went back to the United States, where he was invited to "
                "choreograph fight scenes in Hollywood films, such as "
                "Highlander: Endgame (2000) and Blade II (2002)")
    career_says("His choreography and skills impressed the directors, and "
                "they invited him for cameo appearances in both films")
    career_says("Li personally invited Yen back from Hollywood to star in the "
                "film, marking the second time the two actors appeared "
                "onscreen together since Once Upon a Time in China II")
    career_says("In 2008, Yen starred in Ip Man, a semi-biographical account "
                "of Ip Man, the Wing Chun master of Bruce Lee")
    bio_says("Yen made his American debut in Highlander: Endgame (2000)")
    bio_says("He is best known for portraying Wing Chun grandmaster Ip Man in "
              "the Ip Man film series")
    # the lead names General Nap-lan where the table's Role column says
    # Commander Lan. The table is the roster's source, so the row uses the
    # table; the note repeats the lead's claim about the film, not the name.
    ouatic = next(f for f in films if f["t"] == "Once Upon a Time in China II")
    assert ouatic["role"] == "Commander Lan", ouatic["role"]

    # every italicised film wikilink in the article's lead is a shipped row,
    # matched on Wikidata id so a redirect cannot make one look missing. The
    # two that are not are a series article and a television series.
    shipped_q = {f["qid"] for f in films if f["qid"]}
    assert len(shipped_q) == 72, len(shipped_q)
    stray = sorted({l["shown"] for l in data["bio_lead_links"]
                    if l["qid"] not in shipped_q})
    assert stray == ["Fist of Fury", "Ip Man"], stray
    strayq = {l["target"] for l in data["bio_lead_links"]
              if l["qid"] not in shipped_q}
    assert strayq == {"Ip Man (film series)", "Fist of Fury (TV series)"}, strayq
    assert any(r["cols"][1] == "Fist of Fury" for r in tv), \
        "Fist of Fury is no longer the television row"

    # ---- sections: the article's own headings -----------------------------
    assert data["career_heads"] == [t for t, _, _, _ in SECTIONS], \
        data["career_heads"]
    counts = {t: [f for f in films if lo <= f["year"] <= hi]
              for t, lo, hi, _ in SECTIONS}
    assert [len(counts[t]) for t, _, _, _ in SECTIONS] == [26, 20, 23, 9], \
        {t: len(v) for t, v in counts.items()}
    assert sum(len(v) for v in counts.values()) == 78

    # ---- row notes ---------------------------------------------------------
    def note_for(f):
        bits = []
        if f["role"]:
            bits.append("As %s" % f["role"])
        for p in f["flags"]:
            bits.append(CREDIT[p])
        if f["aka"]:
            bits.append("Also known as %s" % and_list(f["aka"]))
        if f["t"] in IPMAN:
            bits.append(IPMAN[f["t"]])
        if f["t"] == "Master Z: Ip Man Legacy":
            bits.append("The Ip Man spin-off; he co-produced it and is not in "
                        "the cast")
        if f["t"] == "Shaolin Drunkard":
            bits.append("The earliest credit the filmography lists")
        if f["t"] == "Drunken Tai Chi":
            bits.append("His first starring role")
        if f["t"] == "Once Upon a Time in China II":
            bits.append("His breakthrough, and his first film opposite Jet Li")
        if f["t"] == "Legend of the Wolf":
            bits.append("His directing debut")
        if f["t"] in ("Highlander: Endgame", "Blade II"):
            bits.append("Hollywood hired him to choreograph the fights and "
                        "then put him on screen")
        if f["t"] == "Highlander: Endgame":
            bits.append("His American debut")
        if f["t"] == "Hero":
            bits.append("His second film opposite Jet Li, ten years after the "
                        "first")
        if f["t"] == "Ip Man":
            bits.append("Ip Man taught Bruce Lee")
        if f["t"] == "Hero":
            bits.append("One row for the film: the infobox gives %d minutes "
                        "theatrical and %d for the Director's Cut"
                        % tuple(hero["runtime_mins"]))
        if f["t"] == "Iceman":
            bits.append("One row for the film: the infobox gives %d minutes "
                        "in Hong Kong and %d in China"
                        % tuple(ice["runtime_mins"]))
        if f["t"] == "Iceman: The Time Traveller":
            bits.append("The second half of Iceman, released four years later")
        return join_bits(*bits)

    # ---- section intros ----------------------------------------------------
    def intro_for(title):
        got = counts[title]
        n = len(got)
        crew_here = len([f for f in got if not f["role"]])
        act_here = len([f for f in got if f in action])
        dir_here = [f for f in got if f in directed]
        span = got[-1]["year"] - got[0]["year"] + 1
        if title == SECTIONS[0][0]:
            return ("%s films in %s years, and the first is a stuntman "
                    "credit. The article's own first career heading covers "
                    "the apprenticeship and the years he became an action "
                    "director — he is credited with the action on %s of these "
                    "— and the %s films he directed himself, all between %d "
                    "and %d."
                    % (word(n).capitalize(), word(span), word(act_here),
                       word(len(dir_here)), dir_here[0]["year"],
                       dir_here[-1]["year"]))
        if title == SECTIONS[1][0]:
            return ("The decade the article calls his breakthrough. It opens "
                    "with Hollywood hiring him to choreograph rather than to "
                    "act — %s of these %d rows are crew credits with no role "
                    "at all — and it ends in 2008 with Ip Man."
                    % (word(crew_here), n))
        if title == SECTIONS[2][0]:
            return ("%s films, three of them Ip Man sequels and one of them "
                    "the spin-off he produced but is not in. Rogue One in 2016 "
                    "is where the list stops being a Hong Kong filmography."
                    % word(n).capitalize())
        return ("%s films so far. Mulan, John Wick: Chapter 4 and two more he "
                "directed himself — the international run and the Hong Kong "
                "one at the same time." % word(n).capitalize())

    # ---- build --------------------------------------------------------------
    sections = []
    for title, lo, hi, sid in SECTIONS:
        got = counts[title]
        items = []
        for f in got:
            it = {"id": "dy-%d-%s" % (f["year"], slug(f["t"])),
                  "t": f["t"], "n": str(f["year"])}
            note = note_for(f)
            if note:
                it["note"] = note
            # the Wikidata id, from the table's own wikilink, gated on the
            # item being a film and on its dates agreeing with the row's year
            if (f["qid"] and f["year_gate"] and p31(f) == {"film"}):
                it["q"] = f["qid"]
            items.append(it)
        sub = "%d–%d · %d films" % (got[0]["year"], got[-1]["year"], len(got))
        sections.append({"id": sid, "title": title, "sub": sub,
                         "intro": intro_for(title), "items": items})
    sections[0]["open"] = True

    rows = [x for s in sections for x in s["items"]]
    assert len(rows) == 78, len(rows)
    assert len({x["id"] for x in rows}) == 78
    assert all(x.get("note") for x in rows), \
        [x["id"] for x in rows if not x.get("note")]
    assert not any("w" in x for x in rows), "this list is unweighted (CLU-131)"
    assert sum(1 for x in rows if "q" in x) == 72, \
        sum(1 for x in rows if "q" in x)
    for s in sections:
        assert all(a["n"] <= b["n"] for a, b in zip(s["items"], s["items"][1:]))

    # ---- the films this list shares with other lists here ------------------
    keys = {normt(f["t"]) + "|" + str(f["year"]) + "|f": f["t"] for f in films}
    qids = {f["qid"] + "|f": f["t"] for f in films if f["qid"]}
    shared = overlaps(keys, qids)
    # What was true when this was written. A NEW list arriving with one of
    # these films must not break the build — sibling agents ship lists daily
    # and the prose below is computed from `shared` — but these two must
    # never STOP pairing: a group going missing means a title or a year
    # drifted (CLU-191/CLU-247).
    for k, v in {"MCU Anthology": ["Blade II"],
                 "Star Wars": ["Rogue One"]}.items():
        assert shared.get(k) == v, (k, shared.get(k))
    paired = sorted({t for v in shared.values() for t in v},
                    key=[f["t"] for f in films].index)
    sharing = ("%s. Ticking one ticks the other: rows pair across lists by "
               "title and year, and by the film's Wikidata id where a list "
               "carries one, so a film watched here is watched there. Nothing "
               "is duplicated, because every list counts only its own rows."
               % "; ".join("%s on %s" % (and_list(v), k)
                           for k, v in sorted(shared.items())))

    p = {
        "slug": SLUG,
        "title": "Donnie Yen",
        "subtitle": "the films, year by year",
        "kind": "films",
        # Ip Man is a genuinely global franchise and Rogue One, XXX, Mulan and
        # John Wick: Chapter 4 put him in front of an audience that could not
        # name a Hong Kong director — but the NAME travels less far than the
        # films do, which is the thing this number measures. That puts him
        # under Kevin Bacon at 72 and Nicolas Cage at 65, level with David
        # Lynch and Ghost in the Shell at 64, and above Akira Kurosawa at 62
        # and Korean Cinema at 56. The band is what matters; 64 against 65 is
        # noise and POPULARITY.md says so.
        "popularity": 64,
        "year": "1983–2024",
        "blurb": "%s films across five decades — the Hong Kong action years, "
                 "four Ip Man films, and the run out through Rogue One and "
                 "John Wick. He directed %s of them and is credited with the "
                 "action on %s."
                 % (word(len(films)).capitalize(), word(len(directed)),
                    word(len(action))),
        "unit": {"one": "film", "many": "films"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        # Measured in CIELAB against every accent in properties/index.json;
        # see scratch/agent-donnie/accent.py and scan.py. Everything obvious
        # is taken and taken closely — an Ip Man lacquer red lands 0.0 from
        # D&D Novels' accent, a kung-fu gold 7.7 from Mad Men's, a changshan
        # slate 6.9 from Monster's. This pair is sea jade, the freest thing
        # in a family that suits a Chinese martial-arts filmography, at 14.5
        # worst-case CIE76 against 14.7 for the freest pair anywhere on the
        # wheel (a periwinkle with nothing to do with him). Nearest
        # neighbours: Ghibli's #3F7A55 at 14.5 for the light and Attack on
        # Titan's #63AD75 at 16.4 for the dark.
        "accent": "#0B8E6F",
        "accentDark": "#0AB286",
        "tiers": False,
        "notes": [
            ["Every row says what the credit was.",
             "Yen is an action director, a director and a producer as well as "
             "a star, and the filmography records all four in one table — so "
             "each row here names his credit rather than leaving you to "
             "assume he is in it. He is credited with the action on %s of "
             "these %d films, he directed %s of them, and on %s the source "
             "gives him no role at all: Shaolin Drunkard is a stuntman "
             "credit, Moonlight "
             "Express, The Princess Blade and Stormbreaker are action "
             "direction, The Twins Effect and Protégé de la Rose Noire he "
             "co-directed, and Master Z: Ip Man Legacy he produced."
             % (word(len(action)), len(films), word(len(directed)),
                word(len(crew)))],
            ["The four Ip Man films, and the spin-off he is not in.",
             "Ip Man (2008), Ip Man 2, Ip Man 3 and Ip Man 4: The Finale are "
             "his, and each row says which entry it is. Master Z: Ip Man "
             "Legacy (2018) is here too, because the filmography lists it — "
             "but he co-produced it and is not in the cast, and its row says "
             "so. The other spin-offs are not his and are not here; taking "
             "the roster from the filmography table rather than from the "
             "series article is what keeps them out."],
            ["%d of the %d films the filmography lists."
             % (len(films), len(table)),
             "Two are dropped, both on the source's own flag. Gong Shou Dao "
             "(2017) is marked Short film in the notes column; its own "
             "article opens \"a 2017 Chinese kung fu short film\" and its "
             "infobox says twenty minutes. And Caine, the John Wick film he "
             "is directing and starring in, has TBA where its year should be "
             "and Filming in the notes; its article has an empty release "
             "field, no release section, and no year of release anywhere in "
             "it. Announced work joins a list here the moment a source dates "
             "it — a year is enough — and until then it stays off. Television "
             "and video games are out too, and the source drew that line as "
             "well: it keeps its %s television credits and its two game "
             "credits in sections of their own."
             % word(len(tv))],
            ["The sections are the article's own.",
             "Not four invented eras: the four career subheadings on the "
             "Donnie Yen article, with their titles as written. They divide "
             "the work about where you would want it divided — the Hong Kong "
             "apprenticeship and the years he became an action director, the "
             "decade Hollywood hired him to choreograph and that ends with Ip "
             "Man, the Ip Man decade, and the international run. Within a "
             "year the "
             "order is the table's own, not a release-date sort, because six "
             "of these films have no article to date."],
            ["No bar widths on this list, and that is deliberate.",
             "Six titles in the source's table carry no wikilink and no "
             "article exists under any other name for them — %s — so there is "
             "no infobox, no Wikidata item and no runtime to be had at any "
             "price. All's Well, Ends Well 2009 has an article that leaves "
             "its runtime field empty. Weighting is all-or-nothing here: a "
             "row with no weight on a weighted list silently counts as one "
             "hour, which would have priced seven films at an hour each and "
             "made every other number wrong. So no row carries a weight, and "
             "the counters are film counts. The other %d rows do have a "
             "runtime in their own infobox if this is ever revisited."
             % (and_list([f["t"] for f in unlinked]), weighable)],
            ["Alternate titles are the source's, not ours.",
             "Hong Kong films routinely go out under several English names "
             "and this filmography records them, so the row title is the one "
             "the table's own link uses and every a.k.a. it gives is in the "
             "note. In the Line of Duty 4: Witness carries three; Satan "
             "Returns, Heroes Among Heroes and The Founding of a Republic "
             "carry two each."],
            ["%s of these films are on another list here."
             % word(len(paired)).capitalize(), sharing],
            "Roster, roles, credits and alternate titles from Wikipedia's "
            "Donnie Yen filmography, read from the film table itself; the "
            "sections and the facts on the rows from the Donnie Yen article; "
            "the runtimes and release details behind the weighting decision "
            "from each film's own article; the cross-list ids from Wikidata.",
        ],
        "sections": sections,
    }

    out = prop.write(p)
    print("wrote %s — %d films, unweighted (%d of %d have a sourceable "
          "runtime, %d minutes)" % (out.name, len(rows), weighable, len(films),
                                    mins))
    for s in sections:
        got = counts[s["title"]]
        m = sum((f.get("runtime_mins") or [0])[0] for f in got)
        print("   %-6s %-30s %2d  %s  ~%d hours"
              % (s["id"], s["title"], len(s["items"]), s["sub"], round(m / 60)))
    print("   ids: %d/%d   shared: %s"
          % (sum(1 for x in rows if "q" in x), len(rows),
             "; ".join("%s: %s" % (k, ", ".join(v))
                       for k, v in sorted(shared.items()))))


if __name__ == "__main__":
    main()
