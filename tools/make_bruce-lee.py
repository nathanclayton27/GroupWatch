#!/usr/bin/env python3
"""Generate properties/bruce-lee.json.

    PYTHONIOENCODING=utf-8 python tools/make_bruce-lee.py

Bruce Lee's films in release order, one row per film. Everything here is
machine-read from tools/data/bruce-lee.json, collected by
scratch/agent-bruce/collect.py from Wikipedia's "Bruce Lee filmography", the
"Bruce Lee" article, each linked film's own article, and Wikidata. Nothing is
typed in from memory, and every claim the copy makes is asserted against the
data that produced it before anything is written.

THE CREDIT RULE
---------------
**A film is a row when the filmography's own feature-film tables list him in
it, and the row says what the credit was.** Not "films he starred in" — the
source credits him on four films it does not give him a part in, and those
are rows whose notes say he is behind the camera and does not appear.

THE CHILD FILMS ARE IN, IN THEIR OWN SECTION, AND THE SOURCE IS WHY
--------------------------------------------------------------------
This is the decision that makes this list different from every other actor
list here, and it was settled from the source rather than from taste.

Bruce Lee's adult filmography is five leading roles. Before any of them he
had a whole career as a child actor in Hong Kong, credited under the screen
name Lee Siu-lung, and the source puts that career in the SAME table as the
adult work: one ===Feature films=== table running 1941 to 1973, with the
child films at the top, unflagged and undifferentiated. There is no
source-side line between them to inherit — so dropping them would be this
file's opinion overriding the source's table, which is the one thing the
pipeline does not do.

Three further facts from the source settle it the same way:

  * The "Bruce Lee" article's own lead names both careers: "Known for the
    five feature-length martial arts films that he starred in as an adult"
    AND "Lee was introduced to the Hong Kong film industry as a child actor
    by his father, Lee Hoi-chuen."
  * That article's first career heading, ===1940–1958: Early roles, schooling
    and martial arts initiation===, counts them: "By the time he was 18, he
    had appeared in 20 films."
  * Six of the twenty-four have their own Wikipedia articles, three of them
    naming him as the star in the first sentence. These are documented films,
    not a list of titles.

So: one list, four sections, and the child work is the first of them, named
"The child actor" so nobody has to guess why twenty-four films nobody
associates with Bruce Lee are sitting above The Big Boss. The page says this
in its own notes as well; a Bruce Lee list that silently contained them would
be as wrong as one that silently dropped them.

THE SECTIONS, AND WHERE THEIR EDGES COME FROM
----------------------------------------------
The fourth section is the source's own: ===Released posthumously=== is a
separate table in the filmography and it keeps its rows and its name. The
first three split the ===Feature films=== table at two hinges the source's
own Notes column supplies, in its own words:

  * The Orphan (1960) — "In his last Hong Kong widely released film until
    1971"
  * The Big Boss (1971) — "In his first Hong Kong widely released film since
    1960"

The eleven-year gap those two notes bracket is exactly the American stretch,
and it lines up with the "Bruce Lee" article's own era headings — 1966–1970:
American roles, then 1971–1973: Hong Kong films, stardom.

THREE ROWS ARE DROPPED, EACH ON THE SOURCE'S OWN EVIDENCE
----------------------------------------------------------
The two tables list 38 rows. 35 ship. The three that do not:

  * **The Game of Death (1972)** — the unfinished production, not a second
    film. Five things say so and they all say the same thing: both this row
    and the 1978 row link to the SAME article, so both resolve to the same
    Wikidata item (Q854576); that item's publication years are 1978 and 1979,
    so the year gate FAILS on 1972 and passes on 1978; the source's own note
    says "Unfinished because of Bruce Lee's death" and points the reader at
    the posthumous table; the article's infobox for it reads "40 minutes
    (incomplete)" and its first sentence calls it "an incomplete Hong Kong
    martial arts film"; and the "Bruce Lee" lead dates the film 1978. One
    film, one row, and the row is 1978.
  * **The Green Hornet (1974)** and **The Fury of the Dragon (1976)** — the
    source's Notes column says of each, in the same words, "A compilation of
    episodes from the TV series edited together and released as a feature
    film". Television is out (below), and these are that television, re-cut
    and sold as features: there is no footage in either that was shot for a
    film. THIS IS THE ONE PLACE THIS FILE OVERRIDES THE SOURCE'S TABLE
    PLACEMENT, and it does it on the source's own description of what is
    inside them. Neither is linked, neither has an article, and neither
    carries a runtime, so nothing measurable is lost either.

TELEVISION IS OUT, AND SO ARE FOUR OTHER SECTIONS
--------------------------------------------------
The filmography keeps television in its own ==Television appearances==
table — 20 rows, including The Green Hornet (1966–67) itself, the three
Batman crossover episodes, the four Longstreet episodes, Ironside, Blondie
and Here Come the Brides. That separation is the line this list takes,
exactly as the Kevin Bacon and Clint Eastwood lists here take it. The same
goes for the ==Documentaries== table (53), ==Video games== (27), ==Music
video appearances== (2) and the ==Brucexploitation films== list (85 titles
made to cash in on him, in none of which he appears).

IDS COME FROM THE SOURCE'S OWN WIKILINKS, NEVER FROM A TITLE
-------------------------------------------------------------
17 of the 35 rows carry `q`, the film's Wikidata id, resolved from the
wikilink the filmography's own title cell gives and gated on the item's P31
naming a film and its publication years agreeing with the row's year. The
other 18 the source leaves unlinked, and they ship with NO id rather than a
guessed one. scratch/agent-bruce/titlecheck.py measured what the alternative
would have cost: a title lookup on those rows returns a real Wikidata item
for five of them, and every one is a different thing — The Birth of Mankind
is a 16th-century German obstetrics manual, Infancy is the concept of being
a baby, The Guiding Light is the American soap opera, Love is the emotion,
and The Green Hornet is the 1936 radio superhero.

NOT WEIGHTED, AND THAT IS THE POINT OF CLU-131
-----------------------------------------------
18 of the 35 rows have no article behind them at all, so no runtime can be
sourced for them from anywhere this pipeline reaches. Under CLU-131 the
choice is all rows carry a weight or none do, and shipping eighteen rows at
`w: 0` would draw a strip where more than half the films are hairlines —
asserting, in the only language the strip has, that eighteen feature films
take no time to watch. So the list is unweighted: every row counts as one
film. The seventeen runtimes are not thrown away; they are read from each
film's own infobox, printed on the rows, summed in the section headers where
a section is complete, and totalled in the notes.

Where a runtime exists it is the film's own infobox figure, never Wikidata's
P2047, which disagrees by five minutes or more on five of the seventeen —
The Big Boss at 110 against an infobox 100, Fist of Fury 115 against 107,
Enter the Dragon 98 against 102, Game of Death II 87 against 96.

ALTERNATE CUTS: ONE ROW, THE HOME-MARKET LENGTH, THE REST IN THE NOTE
----------------------------------------------------------------------
One film's infobox names more than one length: Game of Death, with four —
103 international, 94 Hong Kong, 125 at the Hong Kong premiere, 100 in
America. Per HOW-IT-WORKS it gets one row, and the figure printed is the
94-minute Hong Kong cut, because it is a Hong Kong film that opened in Hong
Kong on the date the source gives and every other Hong Kong film here is
measured by its home-market length. All four are named on the row.

TITLES: THE SOURCE'S, WITH EVERY ALTERNATE IT GIVES
----------------------------------------------------
Ten rows carry an "Alternate title:" in the source's Notes column and every
one of them is on the row as "also X", read out of the italics in the
wikitext rather than out of the cleaned prose (Father's Fault would have
been cut at its apostrophe otherwise). Two of those alternates are a trap
the source documents in a footnote of its own: the American titles of The
Big Boss and Fist of Fury were swapped by accident, so Fists of Fury is The
Big Boss and The Chinese Connection is Fist of Fury, which is the reverse of
what the names suggest. Both rows say so.

CROSS-LIST SYNC
---------------
Enter the Dragon pairs with Cult Classics on both of build.py's lanes at
once — normalized title plus year, and the Wikidata id Q331617.

Data:   scratch/agent-bruce/collect.py -> tools/data/bruce-lee.json
Checks: scratch/agent-bruce/sync.py, scratch/agent-bruce/titlecheck.py
Accent: scratch/agent-bruce/accent.py
"""
import json
import pathlib
import re
import sys
import unicodedata

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop                                       # noqa: E402
from gwlib.prop import join_bits, slug                       # noqa: E402

SLUG = "bruce-lee"
ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "tools" / "data" / "bruce-lee.json"

WORDS = ("no", "one", "two", "three", "four", "five", "six", "seven", "eight",
         "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
         "sixteen", "seventeen", "eighteen", "nineteen", "twenty")

# The rows the roster rule drops, each keyed to the source evidence that
# drops it. main() asserts every one of these is present and dropped for the
# stated reason, so an upstream edit breaks the build rather than shipping a
# stale exclusion note.
DROP = {
    "The Game of Death": 1972,       # the unfinished production; = the 1978 row
    "The Green Hornet": 1974,        # "A compilation of episodes from the TV series"
    "The Fury of the Dragon": 1976,  # same words, same table, same reason
}

# Every distinct note line the source puts on a SHIPPED row, turned into row
# prose. Split out of the wikitext on the source's own <br> boundaries. None
# means the line is consumed elsewhere (an alternate title, or a composite
# note below). main() asserts this covers the shipped rows exactly.
LINE = {
    # composed by hand below, with the film's own article's detail folded in
    "As an infant": None,
    "Alternate title: My Son, Ah Chung. Available on region 1 "
    "English-subtitled DVD from Cinema Epoch.": None,
    "Alternate title: Father's Fault": None,
    "Available on region 1 English-subtitled DVD from Cinema Epoch / "
    "Alternate title: A Son Is Born": None,
    "Alternate title: A Mother Remembers": None,
    "Available on region 1 English-subtitled DVD from Cinema Epoch": None,
    "Alternate title: The More the Merrier": None,
    "Based on the play Lei Yu by Cao Yu": "From Cao Yu's play Lei Yu",
    "In his last Hong Kong widely released film until 1971":
        "His last widely released Hong Kong film until 1971",
    "Action director":
        "Behind the camera only — he is the action director and does not "
        "appear",
    "Also action director": "He directed the action too",
    "Lee, personal friend of producer Stirling Silliphant, is credited as "
    "the film's fight choreographer.":
        "Behind the camera only — he choreographed one fight as a favour to "
        "the producer, and does not appear",
    "Alternate title: Fists of Fury": None,
    "In his first Hong Kong widely released film since 1960":
        "His first widely released Hong Kong film since 1960",
    "Alternate title: The Chinese Connection": None,
    "Also producer, director, action director and screenwriter":
        "He produced, directed, wrote and choreographed it",
    "The film was released in the U.S. after Enter the Dragon; hence the "
    "alternate title: Return of the Dragon": None,
    "Action Director and fight choreographer":
        "Behind the camera only — he directed and choreographed the fights "
        "and does not appear",
    "Also action director and writer":
        "He directed the action and wrote on it too",
    "Also action director and writer ": None,
    "Released six days after Lee's death": "Out six days after his death",
    "There are two versions of this film, each one with a different plot "
    "(the original from an incomplete 1972 film and the 1978 build doing a "
    '"footage mashup")': None,
    "Lee was shown in incomplete original footage from 1972, plus stock "
    "footage from Enter the Dragon and other films": None,
    "The original was finally released as a short film in the year 2000.":
        None,
    "Co-writer": None,
    "Alternate title: The Silent Flute": None,
    "Film co-written by Bruce Lee, who was seeking to illustrate the "
    "differences between Eastern and Western philosophies": None,
    "Alternate title: Tower of Death": None,
    "Unrelated to the first Game of Death, it was marketed as a sequel in "
    "the U.S.": "Unrelated to Game of Death; America sold it as a sequel",
    "Lee appears in stock footage from Enter the Dragon and other films":
        None,
}

# Two Role cells name a part AND which half of it he plays; "As Son as
# teenager" is not English. Everything else in the column is a plain name.
ROLE_PROSE = {
    "Son as teenager": "Plays the son as a teenager",
    "Frank Wong (child)": "Plays Frank Wong as a child",
    "Billy Lo / Lee Chen-chiang":
        "Billed as Billy Lo and Lee Chen-chiang, but he is only in stock "
        "footage from Enter the Dragon and other films — nothing of him was "
        "shot for it",
}

SECTIONS = [
    ("child", "The child actor", 1941, 1960, "feature"),
    ("america", "America", 1968, 1970, "feature"),
    ("stardom", "Hong Kong, and stardom", 1971, 1973, "feature"),
    ("posthumous", "Released posthumously", 1973, 1981, "posthumous"),
]

# The Game of Death cut the printed runtime measures, and why. See the
# docstring: home market, on the release date the source gives.
GOD_CUT = "HK cut"


def word(n):
    return WORDS[n] if n < len(WORDS) else str(n)


def and_list(names):
    names = list(names)
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + " and " + names[-1]


def note_lines(raw):
    """The source's own note lines: it writes them <br>-separated."""
    out = []
    for piece in re.split(r"<br\s*/?>", raw or ""):
        piece = re.sub(r"<!--.*?-->", "", piece, flags=re.S)
        piece = _clean(piece)
        if piece:
            out.append(piece)
    return out


def _clean(t):
    from gwlib import wiki
    return wiki.clean(t)


ALT = re.compile(r"(?i)alternate title:\s*''(.+?)''")


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
    rows = data["rows"]
    lab = data["p31_labels"]

    assert len(data["feat_rows"]) == 32, len(data["feat_rows"])
    assert len(data["post_rows"]) == 6, len(data["post_rows"])
    assert len(rows) == 38, len(rows)
    n_tv = len(data["tv_rows"])
    n_doc = len(data["doc_rows"])
    n_game = len(data["game_rows"])
    n_mv = len(data["mv_rows"])
    n_brux = len(data["brux"])
    assert (n_tv, n_doc, n_game, n_mv, n_brux) == (20, 53, 27, 2, 85), \
        (n_tv, n_doc, n_game, n_mv, n_brux)

    def p31(r):
        return {lab.get(p, p) for p in r.get("p31") or []}

    by = {(r["t"], r["year"]): r for r in rows}
    assert len(by) == len(rows), "two rows share a title and a year"

    # ---- the three exclusions, each against the evidence that drops it ----
    for t, y in DROP.items():
        assert (t, y) in by, (t, y)

    god72, god78 = by[("The Game of Death", 1972)], by[("Game of Death", 1978)]
    # one article, one Wikidata item, and the item is dated 1978
    assert god72["target"] == god78["target"] == "Game of Death", \
        (god72["target"], god78["target"])
    assert god72["qid"] == god78["qid"] == "Q854576", god72["qid"]
    assert god72["pubyears"] == god78["pubyears"] == [1978, 1979], \
        god72["pubyears"]
    assert god72["year_gate"] is False and god78["year_gate"] is True
    assert "Unfinished because of Bruce Lee's death" in god72["note_src"], \
        god72["note_src"]
    assert god72["runtime_cuts"] == [[40, "incomplete"]], god72["runtime_cuts"]
    assert god72["first_sentences"].startswith(
        "'The Game of Death' is an incomplete Hong Kong martial arts film"), \
        god72["first_sentences"][:90]
    assert "The Game of Death (1978)" in data["bio_lead"], \
        "the Bruce Lee lead no longer dates The Game of Death to 1978"
    # and the two rows read the two DIFFERENT infoboxes on that one article
    assert god72["infobox_picked"] == "The Game of Death"
    assert god78["infobox_picked"] == "Game of Death"
    assert god72["infobox_names"] == ["The Game of Death", "Game of Death"]

    compilation = ("A compilation of episodes from the TV series edited "
                   "together and released as a feature film")
    for t, y in (("The Green Hornet", 1974), ("The Fury of the Dragon", 1976)):
        r = by[(t, y)]
        assert compilation in r["note_src"], r["note_src"]
        assert r["src"] == "posthumous" and not r["target"], r["target"]
        assert not r.get("has_infobox"), r.get("infobox_names")
    # and the series those two are cut from is in the television table
    assert any(r["cols"][1] == "The Green Hornet" for r in data["tv_rows"]), \
        "The Green Hornet is no longer a television row"

    films = [r for r in rows if DROP.get(r["t"]) != r["year"]]
    assert len(films) == 35, len(films)
    assert sum(1 for r in films if r["src"] == "posthumous") == 4

    # ---- release order ---------------------------------------------------
    for i, r in enumerate(films):
        r["pos"] = i
    for a, b in zip(films, films[1:]):
        assert a["year"] <= b["year"], (a["t"], b["t"])
    assert (films[0]["t"], films[0]["year"]) == ("Golden Gate Girl", 1941)
    assert (films[-1]["t"], films[-1]["year"]) == ("Game of Death II", 1981)

    # ---- runtimes: each film's own infobox, and only where it has one -----
    for r in films:
        cuts = r.get("runtime_cuts") or []
        if r["t"] == "Game of Death":
            assert len(cuts) == 4, cuts
            r["mins"] = next(m for m, l in cuts if l == GOD_CUT)
        else:
            assert len(cuts) <= 1, (r["t"], cuts)
            r["mins"] = cuts[0][0] if cuts else None
    timed = [r for r in films if r["mins"]]
    untimed = [r for r in films if not r["mins"]]
    assert len(timed) == 17, len(timed)
    assert len(untimed) == 18, len(untimed)
    # every untimed row is untimed for one reason: the source links no article
    assert all(not r["target"] for r in untimed), \
        [r["t"] for r in untimed if r["target"]]
    assert all(r["target"] and r.get("has_infobox") for r in timed)
    for r in timed:
        assert 60 <= r["mins"] <= 140, (r["t"], r["mins"])

    # only one film's infobox names more than one length
    multi = [r["t"] for r in films if len(r.get("runtime_cuts") or []) > 1]
    assert multi == ["Game of Death"], multi
    god_cuts = god78["runtime_cuts"]
    assert god_cuts == [[103, "Int'l cut"], [94, "HK cut"], [125, "HK premiere"],
                        [100, "US cut"]], god_cuts
    assert god78["release_dates"][0] == "1978-03-23", god78["release_dates"]
    assert god78["country"] == "Hong Kong", god78["country"]

    # why the infobox and not Wikidata: five disagreements of three minutes+
    wd_off = [(r["t"], r["mins"], r["wd_runtime"]) for r in timed
              if r["wd_runtime"] and abs(r["mins"] - r["wd_runtime"]) >= 3]
    assert len(wd_off) == 5, wd_off
    assert [t for t, _, _ in wd_off] == [
        "The Big Boss", "Fist of Fury", "Fist of Unicorn", "Enter the Dragon",
        "Game of Death II"], wd_off
    for t, ib, wd in (("The Big Boss", 100, 110), ("Fist of Fury", 107, 115),
                      ("Enter the Dragon", 102, 98),
                      ("Game of Death II", 96, 87)):
        r = next(x for x in films if x["t"] == t)
        assert (r["mins"], r["wd_runtime"]) == (ib, wd), (t, r["mins"],
                                                          r["wd_runtime"])
    # Wikidata cannot weigh four of the seventeen at all
    wd_gaps = sorted(r["t"] for r in timed if not r["wd_runtime"])
    assert wd_gaps == ["An Orphan's Tragedy", "Golden Gate Girl", "The Kid",
                       "The Orphan"], wd_gaps

    # ---- ids: the source's own wikilinks, P31- and year-gated -------------
    for r in films:
        r["q"] = (r["qid"] if r["qid"] and r["year_gate"]
                  and any("film" in c for c in p31(r)) else None)
    with_q = [r for r in films if r["q"]]
    assert len(with_q) == 17, len(with_q)
    assert {r["t"] for r in with_q} == {r["t"] for r in timed}, \
        "the rows with an id and the rows with a runtime should be the same 17"
    assert len({r["q"] for r in with_q}) == 17, "duplicate Wikidata id"

    # what a title lookup would have cost, measured rather than asserted from
    # memory (scratch/agent-bruce/titlecheck.py wrote this)
    tc = json.loads((ROOT / "scratch" / "agent-bruce" / "titlecheck.json")
                    .read_text(encoding="utf-8"))
    wrong = {k: v for k, v in tc.items() if v["qid"]}
    assert set(wrong) == {"The Birth of Mankind", "Infancy",
                          "The Guiding Light", "Love", "The Green Hornet"}, \
        sorted(wrong)
    for k, q in (("The Birth of Mankind", "Q88622"), ("Infancy", "Q998"),
                 ("The Guiding Light", "Q1145764"), ("Love", "Q316"),
                 ("The Green Hornet", "Q1510225")):
        assert wrong[k]["qid"] == q, (k, wrong[k]["qid"])
    wrong_shipped = sorted(k for k in wrong if k not in DROP)

    # ---- the facts the notes are built from, read out of the articles -----
    bio = data["bio_lead"]
    early = data["career_early"]
    post = data["career_post"]

    def says(text, phrase, where):
        assert phrase in text, "%s no longer says: %s" % (where, phrase)
        return phrase

    says(bio, "Known for the five feature-length martial arts films that he "
              "starred in as an adult", "the Bruce Lee lead")
    says(bio, "Lee was introduced to the Hong Kong film industry as a child "
              "actor by his father, Lee Hoi-chuen", "the Bruce Lee lead")
    says(bio, "Lee is regarded as the first global Chinese film star",
         "the Bruce Lee lead")
    # the swapped pair are the FIRST TWO leading roles, in this order
    assert [r["t"] for r in films if r["t"] in ("The Big Boss", "Fist of Fury")] \
        == ["The Big Boss", "Fist of Fury"]
    says(early, "By the time he was 18, he had appeared in 20 films",
         "the early-roles section")
    says(early, "As a nine-year-old, he co-starred with his father in The Kid "
                "in 1950", "the early-roles section")
    says(early, 'He took his Chinese stage name as 李小龍, lit. "Lee the '
                'Little Dragon"', "the early-roles section")
    says(post, "The cobbled-together film contained only fifteen minutes of "
               "actual footage of Lee", "the posthumous-work section")
    says(post, "Robert Clouse finished the film using a Lee look-alike",
         "the posthumous-work section")
    assert data["career_heads"][0].startswith("1940–1958"), data["career_heads"]
    assert any(h.startswith("1966–1970") for h in data["career_heads"])
    assert any(h.startswith("1971–1973") for h in data["career_heads"])

    # the five leading roles the lead names, matched to rows
    five = ["The Big Boss", "Fist of Fury", "The Way of the Dragon",
            "Enter the Dragon", "Game of Death"]
    for t in five:
        assert any(r["t"] == t for r in films), t
    assert all(t in bio for t in ("The Big Boss (1971)", "Fist of Fury (1972)",
                                  "The Way of the Dragon (1972)",
                                  "Enter the Dragon (1973)")), bio[:0]
    five_mins = sum(next(r for r in films if r["t"] == t)["mins"] for t in five)

    # the source's own footnote about the swapped American titles
    efn = data["efn_titles"]
    says(efn, "the titles were accidentally reversed", "the titles footnote")
    says(efn, "The Big Boss was released as Fists of Fury and Fist of Fury "
              "became The Chinese Connection", "the titles footnote")

    # a handful of per-film article facts the rows quote
    ggg = by[("Golden Gate Girl", 1941)]
    says(ggg["first_sentences"], "the film debut of Bruce Lee, an infant at "
                                 "the time", "the Golden Gate Girl article")
    kid = by[("The Kid", 1950)]
    says(kid["first_sentences"], "the then 9-year-old Bruce Lee in his first "
                                 "leading role", "the Kid article")
    wc = by[("The Wrecking Crew", 1968)]
    says(wc["cut_sentences"][0] if wc["cut_sentences"] else "", "", "n/a")
    coi = by[("Circle of Iron", 1978)]
    says(coi["first_sentences"], "co-written by Bruce Lee, who intended to "
                                 "star in the film himself", "the Circle of Iron article")

    # ---- alternate titles, out of the italics in the wikitext -------------
    for r in films:
        r["alts"] = [m.group(1) for m in ALT.finditer(r["note_raw"] or "")]
    alts = {r["t"]: r["alts"] for r in films if r["alts"]}
    assert alts == {
        "The Kid": ["My Son, Ah Chung"],
        "Blame it on Father": ["Father's Fault"],
        "The Guiding Light": ["A Son Is Born"],
        "A Mother's Tears": ["A Mother Remembers"],
        "We Owe It to Our Children": ["The More the Merrier"],
        "The Big Boss": ["Fists of Fury"],
        "Fist of Fury": ["The Chinese Connection"],
        "The Way of the Dragon": ["Return of the Dragon"],
        "Circle of Iron": ["The Silent Flute"],
        "Game of Death II": ["Tower of Death"]}, alts

    # ---- every source note line on a shipped row is accounted for ---------
    for r in films:
        r["lines"] = note_lines(r["note_raw"])
    seen = {l for r in films for l in r["lines"]}
    unknown = sorted(l for l in seen if l not in LINE)
    assert not unknown, "unmapped source note lines: %s" % unknown
    roles = {r["role"] for r in films if r["role"]}
    assert set(ROLE_PROSE) <= roles, sorted(set(ROLE_PROSE) - roles)

    dvd = "Available on region 1 English-subtitled DVD from Cinema Epoch"
    behind = [r["t"] for r in films
              if any("Behind the camera only" in (LINE.get(l) or "")
                     for l in r["lines"])]
    assert behind == ["The Wrecking Crew", "A Walk in the Spring Rain",
                      "Fist of Unicorn"], behind
    # Circle of Iron is the fourth: its Co-writer line is composed by hand
    behind = behind + ["Circle of Iron"]

    # ---- row notes ---------------------------------------------------------
    def note_for(r):
        bits = []
        role = r["role"]
        if role and "director" not in role.lower():
            bits.append(ROLE_PROSE.get(role, "As %s" % role))
        for l in r["lines"]:
            got = LINE.get(l)
            if got:
                bits.append(got)
        if r["t"] == "Golden Gate Girl":
            bits.append("His first film — he is three months old in it, and "
                        "the part is a baby girl")
        if r["t"] == "The Kid":
            bits.append("His first leading role, at nine")
        if r["t"] == "The Thunderstorm":
            bits.append("Dubbed into Mandarin and re-released in the 1970s "
                        "once he was famous")
        if r["t"] == "The Wrecking Crew":
            bits.append("His first Hollywood credit")
        if r["t"] == "The Big Boss":
            bits.append("also Fists of Fury — America swapped this film's "
                        "title with the next one's by mistake")
        if r["t"] == "Fist of Fury":
            bits.append("also The Chinese Connection — the title meant for "
                        "The Big Boss")
        if r["t"] == "The Way of the Dragon":
            bits.append("also Return of the Dragon, because America saw it "
                        "after Enter the Dragon")
        if r["t"] == "Game of Death":
            bits.append("Finished five years after his death with a "
                        "look-alike, a stunt double and archive footage from "
                        "his other films; the source counts fifteen minutes "
                        "of real Lee in it")
            where = {"Int'l cut": "minutes internationally", "HK cut":
                     "in Hong Kong", "HK premiere": "at the Hong Kong "
                     "premiere", "US cut": "in America"}
            bits.append("Four lengths exist — %s; the figure here is the "
                        "Hong Kong one, the cut that opened in March 1978"
                        % and_list(["%d %s" % (m, where[l])
                                    for m, l in god_cuts]))
        if r["t"] == "Circle of Iron":
            bits.append("Behind the camera only — he co-wrote it and does not "
                        "appear; he meant to star and left the project")
            bits.append("also The Silent Flute")
        # every remaining alternate title the source gives, plainly
        done = {"Fists of Fury", "The Chinese Connection", "Return of the Dragon",
                "The Silent Flute"}
        for a in r["alts"]:
            if a not in done:
                bits.append("also %s" % a)
        if any(dvd in l for l in r["lines"]):
            bits.append("The source names an English-subtitled region 1 DVD")
        if r["mins"]:
            bits.append("%d min" % r["mins"])
        else:
            bits.append("The source links no article for it, so no runtime")
        return join_bits(*bits)

    # ---- sections ----------------------------------------------------------
    buckets = {}
    for sid, title, lo, hi, src in SECTIONS:
        buckets[sid] = [r for r in films
                        if lo <= r["year"] <= hi and r["src"] == src]
    assert [len(buckets[s[0]]) for s in SECTIONS] == [24, 3, 4, 4], \
        {s[0]: len(buckets[s[0]]) for s in SECTIONS}
    assert sum(len(v) for v in buckets.values()) == 35
    assert {r["t"] for r in buckets["child"]} >= {"Golden Gate Girl", "The Kid",
                                                  "The Orphan"}
    assert [r["t"] for r in buckets["stardom"]] == [
        "The Big Boss", "Fist of Fury", "The Way of the Dragon",
        "Fist of Unicorn"], [r["t"] for r in buckets["stardom"]]
    assert [r["t"] for r in buckets["posthumous"]] == [
        "Enter the Dragon", "Game of Death", "Circle of Iron",
        "Game of Death II"], [r["t"] for r in buckets["posthumous"]]
    # the child section is the one with the runtime holes; the rest are whole
    for sid in ("america", "stardom", "posthumous"):
        assert all(r["mins"] for r in buckets[sid]), sid
    child_timed = [r for r in buckets["child"] if r["mins"]]
    assert len(child_timed) == 6, len(child_timed)

    def hours(rs):
        return sum(r["mins"] or 0 for r in rs) / 60.0

    def sub_for(sid, got):
        span = ("%d" % got[0]["year"] if got[0]["year"] == got[-1]["year"]
                else "%d–%d" % (got[0]["year"], got[-1]["year"]))
        n = len(got)
        if sid == "child":
            return ("%s · %d films · %d of them have a runtime, worth %d hours"
                    % (span, n, len(child_timed), round(hours(got))))
        return ("%s · %d film%s · %d hours"
                % (span, n, "" if n == 1 else "s", round(hours(got))))

    def intro_for(sid, got):
        n = len(got)
        if sid == "child":
            return ("His father was a Cantonese opera star and put him in "
                    "front of a camera at three months old, and by his own "
                    "article's count he had appeared in 20 films by the age "
                    "of 18. The source lists %s of them and does not separate "
                    "them from the rest — one table runs 1941 to 1973 — so "
                    "they are here, in their own section, credited as Lee "
                    "Siu-lung. Six have their own article; the other %s the "
                    "source names and links nothing for."
                    % (word(n), word(n - len(child_timed))))
        if sid == "america":
            return ("The eleven-year gap the source's own notes bracket: his "
                    "last widely released Hong Kong film was in 1960 and his "
                    "next was in 1971. What sits in between on a film list is "
                    "three American pictures, and he acts in exactly one of "
                    "them. The rest of that decade is television, which is "
                    "not on this list.")
        if sid == "stardom":
            return ("He goes home, and inside two years he is what his own "
                    "article calls the first global Chinese film star. Three "
                    "leading roles — the first two of them the pair whose "
                    "American titles got swapped — plus one more film he "
                    "choreographed and does not appear in. The Way of the "
                    "Dragon he also produced, directed and wrote.")
        return ("The source's own second table, and its own heading. Enter "
                "the Dragon opened six days after he died; the rest came "
                "later and get progressively less of him, down to a last row "
                "that is stock footage from the films above it.")

    sections = []
    for sid, title, lo, hi, src in SECTIONS:
        got = buckets[sid]
        items = []
        for r in got:
            it = {"id": "bl-%d-%s" % (r["year"], slug(r["t"])),
                  "t": r["t"], "n": str(r["year"]), "note": note_for(r)}
            if r["q"]:
                it["q"] = r["q"]
            items.append(it)
        sections.append({"id": sid, "title": title, "sub": sub_for(sid, got),
                         "intro": intro_for(sid, got), "items": items})
    sections[0]["open"] = True

    out_rows = [x for s in sections for x in s["items"]]
    assert len(out_rows) == 35, len(out_rows)
    assert len({x["id"] for x in out_rows}) == 35
    assert all(x.get("note") for x in out_rows)
    assert not any("w" in x for x in out_rows), "this list is not weighted"
    assert sum(1 for x in out_rows if "q" in x) == 17
    for x in out_rows:
        assert "<!--" not in x["note"] and "-->" not in x["note"], x["id"]
    for s in sections:
        assert all(a["n"] <= b["n"] for a, b in zip(s["items"], s["items"][1:]))

    total_mins = sum(r["mins"] or 0 for r in films)
    adult_mins = sum(r["mins"] for r in films if r["year"] >= 1968)
    assert total_mins == 1751, total_mins
    assert five_mins == 503, five_mins

    # ---- the films this list shares with other lists here ------------------
    keys = {normt(r["t"]) + "|" + str(r["year"]) + "|f": r["t"] for r in films}
    qids = {r["q"] + "|f": r["t"] for r in films if r["q"]}
    shared = overlaps(keys, qids)
    # What was true when this was written. A NEW list arriving with one of
    # these films must not break the build — sibling agents ship lists daily
    # and the prose below is computed from `shared` — but Enter the Dragon
    # must never stop pairing with Cult Classics: it matches on BOTH lanes,
    # so losing it means a title or a year drifted (CLU-191/CLU-247).
    assert shared.get("Cult Classics") == ["Enter the Dragon"], \
        shared.get("Cult Classics")
    paired = sorted({t for v in shared.values() for t in v},
                    key=[r["t"] for r in films].index)
    sharing = ("%s. Ticking one ticks the other: rows pair across lists by "
               "title and year, and by the film's Wikidata id where a list "
               "carries one, so a film watched here is watched there. Nothing "
               "is duplicated, because every list counts only its own rows."
               % "; ".join("%s on %s" % (and_list(v), k)
                           for k, v in sorted(shared.items())))
    sharing_head = ("%s of these films %s on another list here."
                    % (word(len(paired)).capitalize(),
                       "is" if len(paired) == 1 else "are"))

    p = {
        "slug": SLUG,
        "title": "Bruce Lee",
        "subtitle": "everything he was credited on, child roles and all",
        "kind": "films",
        # A global household name — the sort POPULARITY.md's 80–89 band
        # describes, recognised far outside anyone who has watched a martial
        # arts film. What holds it to the bottom of that band rather than up
        # with Dragon Ball at 89 is signals 4 and 5: the list is 35 rows, and
        # two thirds of them are 1950s Cantonese pictures a general audience
        # has never seen, on a career that closed in 1973. So it sits level
        # with Godzilla and Nolan at 80, a nudge above Clint Eastwood and Tom
        # Cruise at 79 on the strength of the name alone, and well under
        # Spielberg at 84.
        "popularity": 80,
        "year": "1941–1981",
        "blurb": "Thirty-five films, and only five of them the ones you are "
                 "thinking of. The other thirty include a whole childhood "
                 "career in Hong Kong cinema and four films he never appears "
                 "in.",
        "unit": {"one": "film", "many": "films"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        # Measured in CIELAB against every accent in properties/index.json;
        # see scratch/agent-bruce/accent.py. The obvious colour is the Game
        # of Death tracksuit yellow and gold turns out to be the most crowded
        # family in the catalogue — a bright #D8B12A lands 6.1 from Seinfeld
        # and 6.8 from Batman. This pair is the same hue taken deep and
        # tarnished, at 14.3 worst-case CIE76 against 14.7 for the freest
        # pair anywhere on the wheel. Nearest neighbours: Coen Brothers'
        # #6E5533 and M*A*S*H's #4B5320 for the light, One Location Films'
        # #D9A94E and Bond's #C9B458 for the dark.
        "accent": "#50400B",
        "accentDark": "#A68930",
        "tiers": False,
        "notes": [
            ["A film is a row when the source's own film tables credit him "
             "on it.",
             "Not the films he stars in — that would be a list of five. The "
             "filmography's two feature-film tables list %d rows and %d of "
             "them are here, each with what the credit actually was written "
             "on the row. On four of them he never appears at all: he is the "
             "action director on The Wrecking Crew and Fist of Unicorn, he "
             "choreographed a single fight in A Walk in the Spring Rain as a "
             "favour to the producer, and he co-wrote Circle of Iron years "
             "before it was made."
             % (len(rows), len(films))],
            ["The child films are here on purpose, and the source is why.",
             "Bruce Lee's adult filmography is %s completed leading roles. "
             "Before them he had a career as a child actor in Hong Kong, "
             "credited as Lee Siu-lung, and the source does not separate the "
             "two: ONE table runs from 1941 to 1973 with the child work at "
             "the top of it, unflagged. His own article's lead names both — "
             "the five adult films and the child actor his father introduced "
             "to the industry — and its first career section counts them: by "
             "18 he had appeared in 20 films. So they stay, in a section that "
             "says what they are, rather than being dropped on this list's "
             "opinion or smuggled in without a word. If you only want the "
             "films people mean by a Bruce Lee film, they are the last two "
             "sections."
             % word(len(five))],
            ["%s of the %d rows the source lists are not here."
             % (word(len(DROP)).capitalize(), len(rows)),
             "The Game of Death (1972) is the unfinished production, not a "
             "second film: it and the 1978 row link to the same article and "
             "resolve to the same Wikidata item, that item is dated 1978, the "
             "source's note says it was left unfinished, its infobox reads 40 "
             "minutes (incomplete), and the Bruce Lee article dates the film "
             "1978. One film, one row, and the row is 1978. The Green Hornet "
             "(1974) and The Fury of the Dragon (1976) are, in the source's "
             "own words on both rows, a compilation of episodes from the TV "
             "series edited together and released as a feature film — there "
             "is no footage in either that was shot for a film, and "
             "television is not on this list. That last one is the only place "
             "this list moves a row the source put in a film table, and it "
             "does it on the source's own description of what is inside them."],
            ["Television is out, and four other sections with it.",
             "The filmography keeps television in its own table, so that is "
             "where it stays: %s credits including The Green Hornet itself, "
             "the three Batman episodes he crossed over into as Kato, the "
             "four episodes of Longstreet, Ironside, Blondie and Here Come "
             "the Brides. This is the same rule the Kevin Bacon and Clint "
             "Eastwood lists here follow. Out for the same reason: %d "
             "documentaries, %d video games, %d music videos, and the %d "
             "Brucexploitation films the source lists — films made to cash in "
             "on him, in none of which he appears."
             % (word(n_tv), n_doc, n_game, n_mv, n_brux)],
            ["No bar widths on this list, and that is a deliberate choice.",
             "%d of the %d rows have no article behind them at all, so no "
             "running time can be sourced for them. A weighted list has to "
             "weigh every row or none — a row without one silently counts as "
             "an hour — and giving eighteen of thirty-five a zero would draw "
             "a strip in which more than half the films look like they take "
             "no time to watch. So every row counts as one film, and the "
             "seventeen runtimes are printed on the rows instead: %d hours "
             "across the whole list, %d of them in the %d films from 1968 on, "
             "and %.1f hours for the five leading roles. Each figure is that "
             "film's own infobox, never Wikidata, which has no runtime for "
             "four of the seventeen and disagrees by three minutes or more on "
             "five of them — The Big Boss at 110 minutes against an infobox "
             "100, Fist of Fury at 115 against 107, Enter the Dragon at 98 "
             "against a 102 the infobox cites to the BBFC."
             % (len(untimed), len(films), round(total_mins / 60.0),
                round(adult_mins / 60.0),
                sum(1 for r in films if r["year"] >= 1968), five_mins / 60.0)],
            ["The titles are the source's, and every alternate it gives is on "
             "the row.",
             "These films carry more English names than any others in the "
             "catalogue, and two of them carry each other's. The source's own "
             "footnote explains it: America meant to release The Big Boss as "
             "The Chinese Connection and Fist of Fury as Fists of Fury, and "
             "the titles were accidentally reversed — so Fists of Fury is The "
             "Big Boss and The Chinese Connection is Fist of Fury, the "
             "opposite of what the names suggest. Both rows say so. The other "
             "eight alternates are on their rows too, down to The Silent "
             "Flute, Tower of Death and Return of the Dragon."],
            ["Half these rows carry no cross-list id, on purpose.",
             "%d of the %d do: the film's Wikidata id, taken from the "
             "wikilink the source's own title cell gives and checked against "
             "the item being a film and its dates matching the row's year. "
             "The other %d the source links nothing for, and they ship with "
             "no id rather than a guessed one. That is not caution for its "
             "own sake — looking those titles up by name returns a real "
             "Wikidata item for %s of them and every one is something else "
             "entirely: %s is a 16th-century German obstetrics manual, "
             "Infancy is the concept of being a baby, The Guiding Light is "
             "the American soap opera, and Love is the emotion."
             % (len(with_q), len(films), len(untimed),
                word(len(wrong)), "The Birth of Mankind")],
            [sharing_head, sharing],
            "Roster, credits, alternate titles and every scope decision from "
            "Wikipedia's Bruce Lee filmography, read from the feature-film, "
            "television, documentary, video-game and Brucexploitation "
            "sections themselves; the career framing and the facts about "
            "Game of Death from the Bruce Lee article; runtimes, release "
            "dates and the four cut lengths from each film's own article; "
            "the cross-list ids from Wikidata.",
        ],
        "sections": sections,
    }

    out = prop.write(p)
    print("wrote %s — %d films, %d timed, %d minutes (%.2f hours), unweighted"
          % (out.name, len(out_rows), len(timed), total_mins,
             total_mins / 60.0))
    for s in sections:
        print("   %-11s %-24s %2d  %s"
              % (s["id"], s["title"], len(s["items"]), s["sub"]))
    print("   ids: %d/%d · dropped: %s"
          % (len(with_q), len(films),
             ", ".join("%s (%d)" % kv for kv in DROP.items())))
    print("   title-lookup traps avoided: %s" % ", ".join(wrong_shipped))
    print("   shared: %s"
          % ("; ".join("%s: %s" % (k, ", ".join(v))
                       for k, v in sorted(shared.items())) or "none"))


if __name__ == "__main__":
    main()
