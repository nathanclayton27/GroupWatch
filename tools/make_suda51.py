#!/usr/bin/env python3
"""Generate properties/suda51.json.

    PYTHONIOENCODING=utf-8 python tools/make_suda51.py

Every game Goichi Suda is credited on, 1993 to 2026, in release order, with
the credit on the row.

THE CREDIT RULE, AND WHY IT IS THIS ONE

Wikipedia's "Goichi Suda" article carries a Works table with three columns:
Year, Title, Role. That Role column is the whole argument, so the rule is
read straight off it:

    A game is a row here when the Role column names Suda on it — director
    of any kind, writer, designer, producer, or the original idea — and the
    row says which.

Both neighbouring rules are worse, and the table is what shows it.

  * "Everything Grasshopper Manufacture made" is a studio list, not his. The
    studio's own article lists 28 developed titles, two of which — Shining
    Soul (2002) and Shining Soul II (2003), work-for-hire action RPGs for
    Sega — the Suda works table does not mention at all. It also misses the
    five games he made at Human Entertainment before Grasshopper existed,
    which are the first five rows here.
  * "Only what he directed" is 15 of these 33. It drops Lollipop Chainsaw,
    Shadows of the Damned, Killer Is Dead, Let It Die, Michigan, Contact and
    Sine Mora — most of the second half of his career, and several of the
    games people would come to this list looking for. After No More Heroes
    (2007) he stopped directing Grasshopper games for twelve years and the
    Role column changes to executive director, creative director, executive
    producer and producer; a directing-only rule would leave that entire
    decade as a hole.

The rule is stated on the page in plain words, every row carries its credit,
and everything the rule excludes is named below and in the property's notes.

WHAT FALLS OUT, AND WHY (five of the table's 38 rows)

  * Sdatcher (2011) — a radio drama written for Hideo Kojima. Not a game.
  * Tokio of the Moon's Shadow (2015) — episode 16 of the Japan Animator
    Expo, an animated short. Not a game.
  * Kurayami Dance (2015) — a two-volume manga, per the Shadows of the
    Damned article. Not a game.
  * Fire Pro Wrestling World (2020) — the Role column scopes this credit
    itself: "The Vanishing scenario writer". The game is a 2017 wrestling
    sim developed by ZEX Corporation and published by Spike Chunsoft; his
    credit is a downloadable story pack inside it, not the game.
  * Sine Mora EX (2017) — the same game as Sine Mora (2012), which is
    already a row. Wikipedia covers both under one article, which calls EX
    "an extended version of Sine Mora". One row per game; the note says so.

That last one is a house rule, not a one-off: a row is a thing to play and
tick, so a game gets ONE row at the year it first came out, and re-releases
live in its note. The Silver Case's 2016 HD remaster, The 25th Ward's 2018
remake and Flower, Sun, and Rain's expanded DS port are all handled the same
way. Rows also pair across lists by title and year, so a second row for a
re-release would split the ticks as well as the hours.

NO WEIGHTS, AND THE COUNT THAT DID RESOLVE

HowLongToBeat main-story figures were asked for all 33 through gwlib's
verify-by-name gate. 27 came back. The six that did not are recorded in
tools/data/suda51.json with the reason each failed, and this file asserts
that the failures are still exactly those six. Under the all-or-nothing rule
a list is weighted only when every row is, so no row carries `w`.

Data:   scratch/agent-suda/collect.py -> tools/data/suda51_works.json
        scratch/agent-suda/hltb.py    -> tools/data/suda51.json
Accent: scratch/agent-suda/accent.py
"""
import json
import pathlib
import re
import sys
import unicodedata

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop
from gwlib.prop import join_bits

SLUG = "suda51"
ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "tools" / "data"

# ---------------------------------------------------------------------------
# the roster: one entry per shipped row, keyed to the Works table by the
# exact (year, title) pair the table gives, so a table edit fails the build
# rather than quietly changing the list.
# key, works-table title, works-table year, section, what the game IS
# ---------------------------------------------------------------------------
ROSTER = [
    ("sfpw3", "Super Fire Pro Wrestling 3 Final Bout", 1993, "human",
     "Super Famicom wrestling, Japan-only, and his first job in games"),
    ("sfpwsp", "Super Fire Pro Wrestling Special", 1994, "human",
     "Super Famicom again, Japan-only; its scenario is what first made his "
     "name"),
    ("tssearch", "Twilight Syndrome: Search", 1996, "human",
     "PlayStation horror adventure, Japan-only. Planned as one game with "
     "Investigation and split in two during development."),
    ("tsinvest", "Twilight Syndrome: Investigation", 1996, "human",
     "The other half of that split, four months later. Japan-only."),
    ("moonlight", "Moonlight Syndrome", 1997, "human",
     "A sequel to the Twilight Syndrome pair, Japan-only, and the last game "
     "he made for Human Entertainment"),
    ("silvercase", "The Silver Case", 1999, "debut",
     "Grasshopper Manufacture's debut, on PlayStation. Japan-only until the "
     "2016 HD remaster."),
    ("fsr", "Flower, Sun, and Rain", 2001, "debut",
     "PlayStation 2, Japan-only; the expanded Nintendo DS port took it West"),
    ("michigan", "Michigan: Report from Hell", 2004, "debut",
     "Akira Ueda directed. Released in Japan and Europe, never in North "
     "America."),
    ("killer7", "Killer7", 2005, "west",
     "One of the Capcom Five, and the first of his games released outside "
     "Japan"),
    ("ward25", "The 25th Ward: The Silver Case", 2005, "west",
     "A mobile sequel to The Silver Case, Japan-only; fully remade in HD in "
     "2018"),
    ("champloo", "Samurai Champloo: Sidetracked", 2006, "west",
     "A licensed tie-in to the anime — Japan and North America only"),
    ("contact", "Contact", 2006, "west",
     "Nintendo DS role-playing; Akira Ueda directed"),
    ("bloodplus", "Blood+: One Night Kiss", 2006, "west",
     "Another anime tie-in, PlayStation 2, Japan-only"),
    ("nmh", "No More Heroes", 2007, "west",
     "Wii, and the series he created"),
    ("fatalframe4", "Fatal Frame: Mask of the Lunar Eclipse", 2008, "west",
     "The fourth Fatal Frame, built by Tecmo, Grasshopper and Nintendo SPD "
     "together; his own article calls his part a co-direction. Wii, "
     "Japan-only until the 2023 remaster."),
    ("nmh2", "No More Heroes 2: Desperate Struggle", 2010, "supervising",
     "The direct sequel; Nobutaka Ichiki directed"),
    ("frog", "Frog Minutes", 2011, "supervising",
     "A small iOS game Grasshopper published itself"),
    ("shadows", "Shadows of the Damned", 2011, "supervising",
     "Grown out of the cancelled Kurayami, with Shinji Mikami producing"),
    ("evasound", "Rebuild of Evangelion: Sound Impact", 2011, "supervising",
     "A PlayStation Portable rhythm game — one of the licensed anime tie-ins "
     "that paid the studio's bills"),
    ("sinemora", "Sine Mora", 2012, "supervising",
     "A shoot 'em up co-developed with Digital Reality. Its expanded EX "
     "version followed in 2017."),
    ("diabolical", "Diabolical Pitch", 2012, "supervising",
     "Baseball, built for the Xbox 360 Kinect"),
    ("libmaiden", "Liberation Maiden", 2012, "supervising",
     "Made for the Guild01 compilation, later sold on its own"),
    ("lollipop", "Lollipop Chainsaw", 2012, "supervising",
     "Co-written with James Gunn; Tomo Ikeda directed"),
    ("worldranker", "No More Heroes: World Ranker", 2012, "supervising",
     "A Japan-only mobile spin-off, since removed from its servers"),
    ("bksword", "Black Knight Sword", 2012, "supervising",
     "A downloadable side-scroller built on an early draft of Kurayami"),
    ("killerdead", "Killer Is Dead", 2013, "gungho",
     "Hideyuki Shin directed"),
    ("libmaidensin", "Liberation Maiden SIN", 2013, "gungho",
     "A visual novel sequel to Liberation Maiden, built by 5pb. for "
     "PlayStation 3"),
    ("ranko", "Ranko Tsukigime's Longest Day", 2014, "gungho",
     "The game half of Short Peace, which four anime shorts share; Suda "
     "handed it to Yohei Kataoka"),
    ("letitdie", "Let It Die", 2016, "gungho",
     "The studio's first title released under GungHo, which bought it in "
     "2013"),
    ("travis", "Travis Strikes Again: No More Heroes", 2019, "return",
     "A spin-off, and his first game as director since No More Heroes"),
    ("nmh3", "No More Heroes III", 2021, "return",
     "The third mainline entry, and the one meant to close the series"),
    ("hotelbcn", "Hotel Barcelona", 2025, "return",
     "A collaboration with Hidetaka Suehiro, of Deadly Premonition"),
    ("romeo", "Romeo is a Dead Man", 2026, "return",
     "Grasshopper developed and published this one itself; Ren Yamazaki "
     "directed"),
]

# the works-table title is not always the name to ship
DISPLAY = {"romeo": "Romeo Is a Dead Man"}

# the five Works-table rows that are not rows here, and why
EXCLUDED = {
    "Sdatcher (Radio Drama)":
        "a radio drama written for Hideo Kojima, not a game",
    "Tokio of the Moon's Shadow":
        "an animated short — episode 16 of the Japan Animator Expo",
    "Kurayami Dance":
        "a two-volume manga, per the Shadows of the Damned article",
    "Fire Pro Wrestling World":
        "the Role column scopes this credit to one downloadable story "
        "scenario inside another studio's game",
    "Sine Mora EX":
        "the same game as Sine Mora, which is already a row",
}

SECTIONS = [
    ("human", "Human Entertainment", 1993, 1997),
    ("debut", "Grasshopper, and Japan only", 1999, 2004),
    ("west", "Killer7, and the run he directed", 2005, 2008),
    ("supervising", "The supervising years", 2010, 2012),
    ("gungho", "Under GungHo", 2013, 2016),
    ("return", "Back in the chair", 2019, 9999),
]

# lead-vs-table cross-check. Every italicised wikilink in the Suda article's
# lead has to be a shipped row or a series whose Suda entries are all rows —
# the check the other filmography lists run, so nothing famous can go missing
# without the build noticing.
LEAD_SERIES = {
    "No More Heroes (series)": ["nmh", "nmh2", "worldranker", "travis", "nmh3"],
    "Fire Pro Wrestling": ["sfpw3", "sfpwsp"],
    "Twilight Syndrome": ["tssearch", "tsinvest", "moonlight"],
}
LEAD_ROWS = {"The Silver Case": "silvercase", "Killer7": "killer7",
             "Lollipop Chainsaw": "lollipop",
             "No More Heroes (video game)": "nmh"}

# the six HowLongToBeat misses, asserted so a future fill-in reopens weighting
HLTB_MISSING = {"sfpw3", "moonlight", "ward25", "frog", "worldranker",
                "libmaidensin"}


def role_phrase(role):
    """The Role column read back as prose: last comma becomes "and"."""
    bits = [b.strip() for b in role.split(",") if b.strip()]
    if len(bits) == 1:
        return bits[0]
    return ", ".join(bits[:-1]) + " and " + bits[-1]


def directed(role):
    """True when the Role column gives him a plain director credit.

    "Executive director" and "creative director" deliberately do not count:
    the whole point of the note about a directing-only rule being too narrow
    is that those are different credits, and the table distinguishes them.
    """
    return any(b.strip().lower() == "director" for b in role.split(","))


# --------------------------------------------------------------------------
# the cross-list overlap, computed rather than remembered
# --------------------------------------------------------------------------
def normt(t):
    """build.py's sync-key normalizer, so this generator computes the same
    groups the build will."""
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    t = re.sub(r"[^a-z0-9]+", " ", t).strip()
    return re.sub(r"^(the|a|an) ", "", t)


def year_of(x, n):
    if re.fullmatch(r"(18|19|20)\d{2}", n):
        return n
    explicit = str(x.get("y", ""))
    if re.fullmatch(r"(18|19|20)\d{2}", explicit):
        return explicit
    found = set(re.findall(r"\b((?:18|19|20)\d{2})\b", x.get("note") or ""))
    return found.pop() if len(found) == 1 else None


def overlaps(keys):
    """{sync key -> [list titles]} for game rows already in the catalogue.

    Games pair with games and never with films — build.py puts the medium in
    the group key — so a same-titled film cannot collide. Computed off the
    catalogue on disk so the note cannot go stale.
    """
    out = {}
    for f in sorted((ROOT / "properties").glob("*.json")):
        if f.stem in ("index", "search", SLUG):
            continue
        p = json.loads(f.read_text(encoding="utf-8"))
        if p.get("secret") or "game" not in (p.get("kind") or ""):
            continue
        for s in p.get("sections", []):
            for x in s.get("items", []):
                y = year_of(x, str(x.get("n", "")))
                if not y:
                    continue
                k = normt(x["t"]) + "|" + y
                if k in keys and p["title"] not in out.get(k, []):
                    out.setdefault(k, []).append(p["title"])
    return out


WORDS = ("no", "one", "two", "three", "four", "five", "six", "seven", "eight",
         "nine", "ten", "eleven", "twelve")


def word(n):
    return WORDS[n] if n < len(WORDS) else str(n)


def main():
    works = json.loads((DATA / "suda51_works.json").read_text(encoding="utf-8"))
    hours = json.loads((DATA / "suda51.json").read_text(encoding="utf-8"))
    table, facts = works["works"], works["facts"]
    claims, studio = works["claims"], works["grasshopper"]

    # ---- the source table, and that the roster is exactly it minus five ----
    assert len(table) == 38, len(table)
    assert table[0]["t"] == "Super Fire Pro Wrestling 3 Final Bout" and \
        table[0]["year"] == 1993, table[0]
    assert table[-1]["t"] == "Romeo is a Dead Man" and \
        table[-1]["year"] == 2026, table[-1]
    by_title = {r["t"]: r for r in table}
    assert len(by_title) == 38, "the Works table has a duplicate title"

    for name in EXCLUDED:
        assert name in by_title, "exclusion %r is no longer in the table" % name
    kept = {t for t, _y, _s, _d in [(k[1], k[2], k[3], k[4]) for k in ROSTER]}
    assert kept | set(EXCLUDED) == set(by_title), \
        "roster + exclusions != the table: %s" \
        % sorted((kept | set(EXCLUDED)) ^ set(by_title))
    assert len(ROSTER) == 33, len(ROSTER)

    games = []
    for key, title, year, sect, desc in ROSTER:
        row = by_title[title]
        assert row["year"] == year, \
            "%s: table says %d, roster says %d" % (title, row["year"], year)
        assert facts.get(key), "no collected facts for %s" % key
        games.append({"key": key, "t": DISPLAY.get(key, title), "year": year,
                      "sect": sect, "desc": desc, "role": row["role"],
                      "article": row["article"], "f": facts[key]})

    years = [g["year"] for g in games]
    assert years == sorted(years), "roster is out of release order"

    # ---- the credit rule, checked against the column it is read from ------
    dirs = [g for g in games if directed(g["role"])]
    assert len(dirs) == 15, [g["t"] for g in dirs]
    # the games a directing-only rule would drop, named in the notes
    dropped = ["Michigan: Report from Hell", "Contact", "Shadows of the Damned",
               "Sine Mora", "Lollipop Chainsaw", "Killer Is Dead", "Let It Die"]
    assert all(d in {g["t"] for g in games} and
               d not in {g["t"] for g in dirs} for d in dropped), dropped
    # every kept row's Role column actually names a credit
    assert all(g["role"] for g in games), \
        [g["t"] for g in games if not g["role"]]
    # ... and the last plain director credit before the twelve-year gap
    gap = [g for g in dirs if g["year"] <= 2008]
    assert gap[-1]["t"] == "Fatal Frame: Mask of the Lunar Eclipse", gap[-1]
    assert [g["t"] for g in dirs if g["year"] > 2008] == \
        ["Travis Strikes Again: No More Heroes", "No More Heroes III"], \
        [g["t"] for g in dirs if g["year"] > 2008]
    assert "having not directed a game since the original No More Heroes in " \
        "2007" in claims["not_directed_since"]["text"], claims

    # ---- the studio list this is NOT ---------------------------------------
    made = set(studio["developed"])
    assert len(studio["developed"]) == 28, len(studio["developed"])
    uncredited = sorted(made - {g["t"] for g in games} -
                        {"Sine Mora EX", "Romeo Is a Dead Man"})
    assert uncredited == ["Shining Soul", "Shining Soul II"], uncredited
    # and the five Human Entertainment games that a studio list would miss
    human = [g for g in games if g["sect"] == "human"]
    assert len(human) == 5 and not (set(t for t in
                                        (g["t"] for g in human)) & made), human
    assert "founded on March 30, 1998" in claims["founded"]["text"], claims

    # ---- the lead-vs-table cross-check -------------------------------------
    keyed = {g["key"]: g for g in games}
    titled = {g["t"] for g in games}
    lead = [tuple(x) for x in works["lead"]]
    assert len(lead) == 7, lead
    for target, label in lead:
        if target in LEAD_SERIES:
            missing = [k for k in LEAD_SERIES[target] if k not in keyed]
            assert not missing, "lead names %s; missing rows %s" % (target,
                                                                    missing)
        elif target in LEAD_ROWS:
            assert LEAD_ROWS[target] in keyed, target
        else:
            raise AssertionError(
                "the lead names %r (%s) and nothing on this list accounts for "
                "it" % (target, label))
    # the infobox's three known-for titles land the same way
    for t in ("The Silver Case", "Killer7", "No More Heroes"):
        assert t in titled, t

    # ---- the exclusions, each still true of its source ----------------------
    assert "radio drama" in claims["sdatcher"]["text"], claims["sdatcher"]
    assert "Tokio of the Moon's Shadow" in claims["tokio_short"]["text"]
    assert "manga" in claims["kurayami_manga"]["text"]
    assert "Fighting Road: Champion Road Beyond" in \
        claims["firepro_dlc"]["text"], claims["firepro_dlc"]
    assert by_title["Fire Pro Wrestling World"]["role"] == \
        "The Vanishing scenario writer", \
        by_title["Fire Pro Wrestling World"]["role"]
    assert "an extended version of Sine Mora" in claims["sinemora_ex"]["text"]
    # Sine Mora and Sine Mora EX resolve to the same Wikipedia article, which
    # is the strongest form of "these are one game"
    assert facts["sinemora"]["article"] == "Sine Mora", facts["sinemora"]
    assert len(EXCLUDED) == 5, EXCLUDED

    # ---- regions, which several row notes lean on --------------------------
    jp_only = {g["key"] for g in games if g["f"]["regions"] == ["JP"]}
    assert jp_only == {"sfpw3", "sfpwsp", "moonlight", "bloodplus"}, \
        sorted(jp_only)
    # the two Twilight games carry no region codes; the series article says it
    assert "released exclusively in Japan" in \
        claims["twilight_jp_only"]["text"], claims["twilight_jp_only"]
    assert "in Japan only" in facts["worldranker"]["release_raw"], \
        facts["worldranker"]
    assert "removed from servers" in facts["worldranker"]["release_raw"]
    assert facts["michigan"]["regions"] == ["EU", "JP"], facts["michigan"]
    assert facts["champloo"]["regions"] == ["JP", "NA"], facts["champloo"]
    assert "outside Japan" in claims["killer7_first_west"]["text"]
    # Fatal Frame IV and the two Silver Case games left Japan only later
    assert facts["fatalframe4"]["regions"] == ["JP", "WW"], facts["fatalframe4"]
    assert "Remastered with improved assets" in \
        claims["fatalframe_remaster"]["text"]
    assert claims["silvercase_remaster"]["text"] == "HD remaster."
    assert claims["ward25_remake"]["text"] == "Full remake in HD."
    assert claims["fsr_ds_port"]["text"].startswith("Expanded port")

    # ---- the people the notes name, read out of the infoboxes --------------
    named = {"michigan": "Akira Ueda", "contact": "Akira Ueda",
             "nmh2": "Nobutaka Ichiki", "killerdead": "Hideyuki Shin",
             "romeo": "Ren Yamazaki"}
    for key, who in named.items():
        assert who in facts[key]["director"], (key, facts[key]["director"])
    assert "Tomo Ikeda" in facts["lollipop"]["director"], facts["lollipop"]
    assert "James Gunn" in facts["lollipop"]["writer"], facts["lollipop"]
    assert "5pb." in facts["libmaidensin"]["release_raw"], facts["libmaidensin"]
    assert "Kinect" in claims["kinect"]["text"]
    assert "Digital Reality" in claims["sinemora_dev"]["text"]
    assert "Guild01" in claims["libmaiden_guild"]["text"]
    assert "Yohei Kataoka" in claims["ranko_kataoka"]["text"]
    assert "four short anime films" in claims["shortpeace_four"]["text"], \
        claims["shortpeace_four"]
    assert "Shinji Mikami" in facts["shadows"]["producer"], facts["shadows"]
    assert "early draft of Kurayami" in claims["bksword_kurayami"]["text"]
    assert "first incarnation of Shadows of the Damned" in \
        claims["shadows_kurayami"]["text"], claims["shadows_kurayami"]
    assert "Deadly Premonition" in claims["suehiro_known"]["text"]
    assert "Hotel Barcelona" in claims["suehiro_collab"]["text"]
    assert "was released for PlayStation 5, Windows, and Xbox Series X/S in " \
        "September 2025" in facts["hotelbcn"]["release_raw"], facts["hotelbcn"]
    assert "Grasshopper Manufacture" in claims["romeo_selfpub"]["text"]
    assert "Capcom Five" in claims["capcom_five"]["text"]
    assert "iOS" in facts["frog"]["release_raw"], facts["frog"]
    assert "first title released under GungHo" in \
        claims["gungho_first"]["text"], claims["gungho_first"]
    assert "30 January 2013" in claims["gungho"]["text"]

    # ---- weights: all or nothing -------------------------------------------
    assert set(hours) == {g["key"] for g in games}, \
        sorted(set(hours) ^ {g["key"] for g in games})
    missed = {k for k, v in hours.items() if v["main_h"] is None}
    assert missed == HLTB_MISSING, sorted(missed)
    resolved = len(hours) - len(missed)
    assert resolved == 27, resolved
    # exactly why each miss missed, so a data fix reopens the question
    nofigure = sorted(k for k in missed
                      if hours[k]["why"] == "verified by name but no "
                                            "main-story figure")
    assert nofigure == ["frog", "libmaidensin", "moonlight", "sfpw3"], nofigure
    assert hours["worldranker"]["why"].startswith("no result named"), \
        hours["worldranker"]
    assert hours["ward25"]["why"] == \
        "year mismatch: HLTB says 2018, wanted 2005", hours["ward25"]

    # ---- what the section intros claim -------------------------------------
    bysect = {}
    for g in games:
        bysect.setdefault(g["sect"], []).append(g)
    assert [len(bysect[k]) for k, _t, _l, _h in SECTIONS] == \
        [5, 3, 7, 10, 4, 4], [len(bysect[k]) for k, _t, _l, _h in SECTIONS]
    # human: he directed every one of the five, and the studio came after
    assert all(directed(g["role"]) for g in bysect["human"]), bysect["human"]
    assert [g["f"]["platforms"] for g in bysect["human"][:2]] == \
        ["Super Famicom", "Super Famicom"], bysect["human"][:2]
    assert "Suda entered the position partway through development" in \
        claims["twilight_suda"]["text"], claims["twilight_suda"]
    assert "last game worked on by Suda for Human Entertainment" in \
        claims["moonlight_last"]["text"]
    # debut: the two Grasshopper originals shipped in Japan alone on their
    # own consoles, and Michigan has no North American release at all
    assert "'''PlayStation'''{{vgrelease|JP|October 7, 1999}}" in \
        facts["silvercase"]["release_raw"], facts["silvercase"]
    assert "'''PlayStation 2'''{{vgrelease|JP|May 2, 2001}}" in \
        facts["fsr"]["release_raw"], facts["fsr"]
    assert "NA" not in facts["michigan"]["regions"], facts["michigan"]
    # west: six of the seven carry a plain director credit, two are anime
    # tie-ins the studio did not own and one is another studio's horror series
    assert len([g for g in bysect["west"] if directed(g["role"])]) == 6, \
        [g["t"] for g in bysect["west"] if directed(g["role"])]
    tieins = claims["anime_tieins"]["text"]
    assert "Samurai Champloo: Sidetracked" in tieins and \
        "Blood+: One Night Kiss" in tieins, tieins
    assert "collaboration between Tecmo Koei, Grasshopper Manufacture and " \
        "Nintendo SPD" in claims["fatalframe_collab"]["text"], claims
    # the one place two Wikipedia articles pull against each other: the works
    # table gives him Director on Fatal Frame (2008) while Grasshopper's
    # article says he had not directed since 2007. Both are quoted rather than
    # reconciled — the Suda article itself calls that credit a co-direction.
    assert "designer, co-director and co-writer on Fatal Frame: Mask of the " \
        "Lunar Eclipse, the fourth entry" in \
        claims["fatalframe_codirector"]["text"], claims["fatalframe_codirector"]
    # supervising: not one plain director credit in the whole run
    assert not any(directed(g["role"]) for g in bysect["supervising"]), \
        [g["t"] for g in bysect["supervising"] if directed(g["role"])]
    assert {g["role"] for g in bysect["supervising"]} == {
        "Executive director", "Executive producer",
        "Executive director, writer", "Creative producer", "Creative director",
        "Producer", "Executive producer, writer"}, \
        sorted({g["role"] for g in bysect["supervising"]})
    # return: the 2018 split, and what came out of it
    assert "absorption-type split" in claims["split_2018"]["text"]
    assert "Travis Strikes Again" in claims["after_split"]["text"]

    # ---- rows ---------------------------------------------------------------
    intros = {
        "human":
            "Five games before Grasshopper Manufacture existed, every one of "
            "them released only in Japan and every one of them directed by "
            "him: two Super Famicom wrestling games, the Twilight Syndrome "
            "pair he joined partway through development, and Moonlight "
            "Syndrome, the last thing he made for Human before founding his "
            "own studio on 30 March 1998.",
        "debut":
            "The studio's first three. He directed and wrote its debut, The "
            "Silver Case, and Flower, Sun, and Rain after it; on Michigan he "
            "handed the chair to Akira Ueda and took an original-plan and "
            "producer credit instead. The first two shipped on their own "
            "consoles in Japan alone, and Michigan reached Europe a year "
            "later and North America never.",
        "west":
            "Killer7 is the first of his games released outside Japan and the "
            "one that made his name in the West. Seven games in four years "
            "follow it — two of them tie-ins to anime the studio did not own, "
            "one an entry in another studio's horror series — and the Role "
            "column gives him a plain director credit on six. Then it stops. "
            "Fatal Frame is the last of them and his own article calls that "
            "one a co-direction; the column does not read director again "
            "until 2019, and Grasshopper's article dates the gap from No More "
            "Heroes in 2007.",
        "supervising":
            "Ten games in three years and not one plain director credit among "
            "them. Wikipedia's own line is that after No More Heroes he took "
            "a supervisory role on the majority of Grasshopper's projects, "
            "and the column bears it out — executive director, creative "
            "director, executive producer, producer, creative producer, "
            "never director.",
        "gungho":
            "GungHo Online Entertainment bought Grasshopper Manufacture on 30 "
            "January 2013, and Wikipedia names Let It Die as the studio's "
            "first title released under it. Four games, and the two in the "
            "middle are largely other people's — a visual novel 5pb. built, "
            "and the game half of a project four anime shorts share.",
        "return":
            "The studio split from GungHo in 2018 and Travis Strikes Again "
            "followed — by Grasshopper's own account his first game as "
            "director since No More Heroes in 2007. No More Heroes III was "
            "meant to close that series. Then a collaboration with Deadly "
            "Premonition's Hidetaka Suehiro, and a self-published one.",
    }

    sections = []
    for key, title, lo, hi in SECTIONS:
        got = [g for g in games if g["sect"] == key]
        assert got, key
        assert all(lo <= g["year"] <= hi for g in got), \
            "%s holds a row outside %d-%d" % (key, lo, hi)
        items = []
        for g in got:
            items.append({"id": "suda-%d-%s" % (g["year"], prop.slug(g["t"])),
                          "t": g["t"], "n": str(g["year"]),
                          "note": join_bits(role_phrase(g["role"]), g["desc"])})
        sections.append({
            "id": key, "title": title,
            "sub": "%d–%d · %d games" % (got[0]["year"], got[-1]["year"],
                                         len(got)),
            "intro": intros[key], "items": items})
    sections[0]["open"] = True

    placed = sum(len(s["items"]) for s in sections)
    assert placed == len(games), (placed, len(games))
    for s in sections:
        assert all(a["n"] <= b["n"]
                   for a, b in zip(s["items"], s["items"][1:])), \
            "%s is out of year order" % s["title"]
    rows = [x for s in sections for x in s["items"]]
    assert all(x.get("note") for x in rows), \
        "every row carries its credit: %s" % [x["id"] for x in rows
                                              if not x.get("note")]
    assert not any("w" in x for x in rows), "this list ships unweighted"

    # ---- what this list shares with other lists here ------------------------
    keys = {normt(g["t"]) + "|" + str(g["year"]): g["t"] for g in games}
    assert len(keys) == len(games), "two rows share a sync key"
    shared = overlaps(keys)
    assert not shared, \
        "a game here now sits on another list — say so in the notes: %s" \
        % {keys[k]: v for k, v in shared.items()}

    p = {
        "slug": SLUG,
        "title": "Suda51",
        "subtitle": "the games of Goichi Suda, with the credit on each row",
        "kind": "games",
        # A cult auteur: No More Heroes and Lollipop Chainsaw carry real
        # recognition inside games, "Suda51" is a name people say, and none of
        # it travels far outside the medium — enthusiast territory, a little
        # above the Bond games subset and a little under Ace Attorney. See
        # POPULARITY.md.
        "popularity": 46,
        "year": "1993–2026",
        "blurb": "%d games with Goichi Suda's name on them, Super Famicom "
                 "wrestling to Romeo Is a Dead Man — every one his own credit "
                 "list gives him, and every row says what the credit was."
                 % len(games),
        "unit": {"one": "game", "many": "games"},
        "verb": {"base": "play", "past": "played", "ing": "playing"},
        "itemOrder": "number-first",
        # measured in CIELAB against every accent in properties/index.json;
        # see scratch/agent-suda/accent.py. The obvious picks are all taken:
        # the Killer7 blood red lands 7.5 from Super Mario's, the No More
        # Heroes hot pink 10.6 from Grand Theft Auto's, Lollipop Chainsaw's
        # bubblegum 6.9 from Buffy's, and Grasshopper's warning yellow IS
        # Deadwood's, exactly. This neon violet-magenta is the free corner of
        # his own palette at 15.7 worst-case against 17.5 for the freest pair
        # anywhere on the wheel.
        "accent": "#8A2C96",
        "accentDark": "#E479EC",
        "tiers": False,
        "notes": [
            ["A credit, not a studio.",
             "Wikipedia's Goichi Suda article carries a Works table with a "
             "Role column, and that column is the rule: a game is a row here "
             "when the column names him — director of any kind, writer, "
             "designer, producer, or the original idea — and the row says "
             "which. "
             "Both of the obvious alternatives are worse. Everything "
             "Grasshopper Manufacture made is a studio list, not his: it "
             "includes %s and %s, two Sega action RPGs his credit list does "
             "not mention at all, and misses the %s games he made at Human "
             "Entertainment before the studio existed. Only what he directed "
             "is %d of these %d — it would drop Michigan, Contact, Shadows of "
             "the Damned, Sine Mora, Lollipop Chainsaw, Killer Is Dead and "
             "Let It Die, and cut a hole through the middle of the career. "
             "The column's last plain director credit before that gap is "
             "Fatal Frame: Mask of the Lunar Eclipse in 2008, which the same "
             "article describes as a co-direction, and its next is Travis "
             "Strikes Again in 2019; Grasshopper Manufacture's own article "
             "dates the gap from No More Heroes in 2007. Everything in "
             "between reads executive director, creative director or "
             "producer."
             % (uncredited[0], uncredited[1], word(len(human)), len(dirs),
                len(games))],
            ["What the rule leaves out.",
             "Five rows of that same table are not rows here. Three are not "
             "games: Sdatcher, a radio drama he wrote for Hideo Kojima; Tokio "
             "of the Moon's Shadow, an animated short for the Japan Animator "
             "Expo; and Kurayami Dance, a two-volume manga. Fire Pro "
             "Wrestling World is out because the column scopes that credit "
             "itself — \"The Vanishing scenario writer\" — to one "
             "downloadable story pack inside a wrestling game another studio "
             "built. And Sine Mora EX is out because it is the same game as "
             "Sine Mora, which is already here."],
            ["One row per game.",
             "A game gets one row, at the year it first came out, and its "
             "re-releases live in the note. The Silver Case is a 1999 "
             "PlayStation row whose 2016 HD remaster is named on it; The 25th "
             "Ward is a 2005 mobile row that was remade in HD in 2018; Flower, "
             "Sun, and Rain's expanded DS port and Sine Mora's EX version ride "
             "in their notes the same way. A second row would double a game "
             "you only play once, and rows pair across lists by title and "
             "year, so splitting a game in two would split the ticks with it."],
            ["No hours on these rows, and the %d that did resolve." % resolved,
             "HowLongToBeat main-story figures were checked for all %d by name "
             "and release year. %d came back. The %s that did not are Super "
             "Fire Pro Wrestling 3 Final Bout, Moonlight Syndrome, Frog "
             "Minutes and Liberation Maiden SIN, which HowLongToBeat lists "
             "without a single main-story submission between them; No More "
             "Heroes: World Ranker, which it has never heard of; and The 25th "
             "Ward, which it knows only as the 2018 remake. A part-weighted "
             "list draws its unweighted rows as slivers and reads as though "
             "those games were short, so this one carries no weights at all "
             "rather than most of them."
             % (len(games), resolved, word(len(missed)))],
            ["Nothing here is on another list yet.",
             "None of these %d games appears anywhere else in the catalogue, "
             "so no row on this list ticks a row on another one. Game rows "
             "pair by title and year and never pair with films, so the day a "
             "horror or action list picks up Killer7 or No More Heroes, the "
             "tick will carry across on its own." % len(games)],
            "Roster, years and credits from the Works table in Wikipedia's "
            "Goichi Suda article; the studio catalogue and the acquisition "
            "dates from Grasshopper Manufacture; release dates and regions "
            "from each game's own article; hours checked against "
            "HowLongToBeat and reported above rather than shipped.",
        ],
        "sections": sections,
    }

    out = prop.write(p)
    print("wrote %s — %d games, %d–%d, unweighted (%d/%d resolved on HLTB)"
          % (out.name, len(rows), games[0]["year"], games[-1]["year"],
             resolved, len(games)))
    for s in sections:
        print("   %-34s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))
    print("   plain director credits: %d of %d; excluded from the table: %d"
          % (len(dirs), len(games), len(EXCLUDED)))
    print("   sync groups formed with other lists: %d" % len(shared))


if __name__ == "__main__":
    main()
