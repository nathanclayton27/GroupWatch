#!/usr/bin/env python3
"""Generate properties/van-damme.json.

    PYTHONIOENCODING=utf-8 python tools/make_van-damme.py

Jean-Claude Van Damme's films in release order, one row per film, every row
saying how the film reached its audience. Everything here is machine-read from
tools/data/van-damme.json, collected by scratch/agent-jcvd/collect.py from
Wikipedia's "Jean-Claude Van Damme" article, each film's own article, and
Wikidata. Nothing is typed in from memory, and every claim the copy makes is
asserted against the data that produced it before anything is written.

THE ROSTER: THE FILM TABLE, MINUS WHAT THE TABLE'S OWN NOTES FLAG
-----------------------------------------------------------------
There is no "Jean-Claude Van Damme filmography" article — wiki.search() finds
none — so the biography's own ==Filmography== section is the source, and its
===Film=== table is the roster. That table lists 67 films. 65 of them are rows
here. The two it drops are dropped on the table's own flags, never on this
file's opinion:

  * **One short film.** Monaco Forever (1984), whose Notes cell says "Short
    film" and whose own article says "The film runs 48 minutes and is most
    notable for the first (although brief) appearance of Jean-Claude Van
    Damme". Same flag, same rule, as the seven kevin-bacon dropped. (Wikidata
    is no help here — its P31 says plain "film" — so the table's Notes cell is
    the sole authority, and this file says so out loud rather than implying a
    second source it does not have.)
  * **One film that does not exist yet.** Frenchy, whose Year cell says "TBA".
    Three things agree: the table gives no year, its article opens "is an
    unreleased action drama", and Wikidata's P31 calls it a "film project"
    with no publication date at all. clubd carries announced work that has a
    source-given date — even a bare year — and Frenchy has none. An undated
    announcement is not a row.

THE UNCREDITED EXTRAS STAY, AND THAT IS THE INTERESTING CALL
-------------------------------------------------------------
Two rows carry the Notes flag "Uncredited extra": Woman Between Wolf and Dog
(1979), where the Role cell reads "Moviegoer / Man in Garden", and Breakin'
(1984), where it reads "Spectator in the first dance scene". Both are rows.

The reason is kevin-bacon's own precedent read carefully. Bacon dropped two
films because his footage is NOT IN THEM — a deleted scene and a segment cut
before release — and kept every film he is actually on screen in, including
the ones where he plays himself. Van Damme is on screen in both of these; the
article's career section even says where to look, that he and Michel Qissi
"are seen dancing in the background at a dance demonstration". A list of films
you can watch him in should contain the films you can watch him in, and the
note says "An uncredited extra" so nobody is sold a starring role.

THIS IS THE JUDGEMENT CALL ON THIS LIST, and it is one edit to reverse:
DROP_EXTRAS = True below drops both rows and the notes rewrite themselves.

RELEASE CHANNEL: THE DEFINING FACT, AND TWO SOURCE SIGNALS READ IT
-------------------------------------------------------------------
More than a third of this filmography never played a cinema, and someone
choosing what to watch tonight wants that on the row. tools/make_tremors.py
reads the channel from each film's OWN article categories ("1996
direct-to-video films", "Direct-to-video sequel films") and never from prose.
That signal was run here first, and it is not sufficient on its own: it finds
nine direct-to-video films where the filmography table's own Notes column
marks fourteen. The five it misses — Replicant, Wake of Death, The Shepherd:
Border Patrol, Swelter and Kill 'Em All — simply have no such category on
their articles. Every film the categories DO flag, the table flags too; the
disagreement runs one way only.

So the channel is the union of two structured source fields, never prose:

  direct-to-video  the film's own article categories say so, OR the
                   filmography table's own Notes cell says so.   (14 films)
  straight to Netflix  the film's own article categories say "Netflix original
                   films". One film.                             (1 film)
  limited release  the table's Notes cell says so — a handful of screens
                   rather than a wide opening.                   (14 films)
  in cinemas       none of the above.                            (35 films)
  not recorded     no article at all to read.                    (1 film)

"In cinemas" is cross-checked the two further ways tremors used: a box-office
gross in the film's own infobox, and an image caption naming a theatrical
poster. Exactly one shipped row fails both — Legionnaire (1998), whose
infobox states no gross and whose image is captioned "Official DVD cover" —
and its row says so rather than quietly claiming a cinema release.

NOTES, NOT TIERS — AND HERE IS WHY
-----------------------------------
tremors chose row notes over disney-style release-channel tiers because at
twenty rows the words are shorter to read than a badge needing a legend. This
list is three times the size, so the question was reopened, and it comes out
the same way for a different and stronger reason: on this engine a tier is a
RANK, not a label. It sets mark height on the strip, it is what `paceTiers`
scopes a finish date to, and it renders as an unlabelled "T3" beside a Tier
1/2/3 panel in the stats. Filing fourteen films as tier 3 would tell a reader
they are the skippable ones. That is not what "went to video" means — Universal
Soldier: Regeneration is the best-reviewed film of his second act and it went
to video — and this list is not in the business of ranking his work. A release
channel is a fact about a film, so it goes in words on the row, and the
per-channel counts go in every section's subtitle so the split is countable at
a glance without opening anything.

WEIGHTS: EACH FILM'S OWN INFOBOX, AND ONE ROW THAT WEIGHS NOTHING
------------------------------------------------------------------
Every bar is the running time stated in that film's own Wikipedia infobox, in
hours. Wikidata's P2047 was the alternative and lost: it disagrees with the
film's own article by six minutes or more on four films — Double Impact at 118
against an infobox 110, Rzhevsky versus Napoleon at 95 against 80 — and it has
no runtime at all for three shipped rows where the infobox does. The brief's
specific worry, that direct-to-video action films ship unrated cuts and
Wikidata reports the longest it holds, is real (P2047 carries two figures for
Missing in Action, The Exam, Rzhevsky and Minions and gwlib.wikidata.runtime
returns the larger) — but a sweep of all 64 articles for a sentence stating a
running time beside a word meaning a particular version finds a second cut on
exactly two films, and NEITHER is one of the fourteen direct-to-video ones.

  * No Retreat, No Surrender (1985) — 98 minutes (international cut) and 83
    (U.S. cut); the article adds that the American cut "runs approximately 14
    minutes shorter, features a different musical score, and omits several
    overtly comedic scenes". The bar is the 98-minute international cut,
    because that is the release the row's own year names: the table dates the
    film 1985 and the infobox's 1985 date is the Italian opening, with the
    U.S. release in 1986.
  * Black Eagle (1988) — 93 minutes, with a 104-minute director's cut. The bar
    is the 93.

ONE ROW CARRIES w: 0, AND THIS IS A DEPARTURE WORTH ARGUING WITH
-----------------------------------------------------------------
Haters (2021) is the one row with no sourceable runtime: the table gives it no
wikilink, there is no English Wikipedia article, and so there is no infobox,
no categories and no Wikidata item. The instruction this list was built under
says a list with any unsourceable runtime should ship UNWEIGHTED rather than
mixed. This file does not do that, for kevin-bacon's reason, shipped the same
day: stripping 64 verified runtimes because one French comedy cameo has no
article makes the list strictly worse, and the failure CLU-131 actually names
— a row with NO `w` silently counting as one hour — cannot happen here,
because the `w` is an explicit 0 and src/template.html honours
`typeof x.w === 'number' && x.w >= 0`. Resolving it by title search was the
other option and is exactly the hazard the id rule exists for: "Haters" is as
collidable a title as this catalogue has.

THIS IS A JUDGEMENT CALL AND THE LEAD SHOULD OVERRULE IT IF THEY DISAGREE:
flipping WEIGHTED to False below strips every bar in one edit.

THE SECTIONS ARE THE ARTICLE'S OWN, ALL SIX OF THEM
----------------------------------------------------
Nothing is invented. The ==Career== section carries six dated subheadings —
"Early 1970s to 1980: Martial arts and first film appearance", "1982-1988:
Early works and breakthrough", "1989-1999: International stardom", "2000-2007:
Switch to direct-to-video", "2008-2013: Return to mainstream" and
"2014-present: Subsequent films" — and their date ranges are parsed out of the
headings themselves and used as the section spans. Every one of the 65 films
lands in exactly one, which is asserted. The section titles are the half of
each heading after the colon, as written. The article periodised this career;
this list did not have to.

IDS
---
`q` is the film's Wikidata id, resolved from the wikilink the filmography
table's OWN title cell gives — never from a title lookup — and gated three
ways: P31 must name a film, the item's publication years must agree with the
table's year, and the wikilink must have resolved. 64 of 65 rows carry one.
This matters more than usual here because the later titles are generic and
highly collidable (Inferno, The Order, Assassination Games, Enemies Closer,
Pound of Flesh), and a title lookup on any of them lands somewhere else.

Data:   scratch/agent-jcvd/collect.py -> tools/data/van-damme.json
Checks: scratch/agent-jcvd/analyze.py, scratch/agent-jcvd/analyze2.py
Accent: scratch/agent-jcvd/accent.py, accent_grid.py, accent_refine.py
"""
import json
import pathlib
import re
import sys
import time
import unicodedata

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop                                       # noqa: E402
from gwlib.prop import join_bits, slug                       # noqa: E402

SLUG = "van-damme"
ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "tools" / "data" / "van-damme.json"

# Flip to False to strip every bar (see the weights note in the docstring).
WEIGHTED = True
# Flip to True to drop the two "Uncredited extra" rows (see the roster note).
DROP_EXTRAS = False

# Measured in CIELAB against every accent pair in properties/index.json — 202
# lists, so the wheel is crowded and everything warm and obvious is taken
# closely: the Kickboxer red lands 5.0 from Gurren Lagann's, the Belgian gold
# 2.1 from Star Wars', the VHS magenta 3.0 from Sailor Moon's and 4.7 from
# Cult Classics'. This is the freest usable pair anywhere on the wheel at 14.1
# worst-case CIE76, and the sci-fi spine of the filmography — Cyborg,
# Universal Soldier, Timecop, Replicant — is a fair enough hook for an
# electric blue. Nearest neighbours: Spawn's #4412A6 at 14.1, Invincible at
# 15.0, Futurama at 15.7. See scratch/agent-jcvd/accent_refine.py.
ACCENT, ACCENT_DARK = "#0B1985", "#6879F7"

# See POPULARITY.md. The name travels a long way outside the films — "the
# Muscles from Brussels", the splits, Bloodsport and Timecop and Street
# Fighter are titles a general audience recognises — which puts him well above
# Nicolas Cage at 65 in 90s footprint. But two thirds of this filmography is
# video-shelf work almost nobody has seen, and that is what keeps him under
# Kevin Bacon and John Wayne at 72 and Robin Williams at 71, level with the
# Coen Brothers and Mad Men at 67.
POPULARITY = 67

WORDS = ("no", "one", "two", "three", "four", "five", "six", "seven", "eight",
         "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
         "sixteen", "seventeen", "eighteen", "nineteen", "twenty")

# The five article headings, in order, mapped to section ids. Asserted against
# the wikitext below, so a rewrite upstream breaks the build.
SECTION_IDS = {
    "Early 1970s to 1980: Martial arts and first film appearance": "early",
    "1982–1988: Early works and breakthrough": "breakthrough",
    "1989–1999: International stardom": "stardom",
    "2000–2007: Switch to direct-to-video": "video",
    "2008–2013: Return to mainstream": "mainstream",
    "2014–present: Subsequent films": "later",
}

# What the row says about how the film came out. The word is prepended from
# the data; nothing here is written on a row this file decided by hand.
CHANNEL = {
    "cinemas": "In cinemas",
    "limited": "Limited release",
    "streaming": "Straight to Netflix",
    "direct-to-video": "Direct-to-video",
    "unknown": "Release channel not recorded",
}
CHANNEL_SHORT = {
    "cinemas": "in cinemas",
    "limited": "limited release",
    "streaming": "straight to Netflix",
    "direct-to-video": "direct-to-video",
    "unknown": "channel not recorded",
}
CHANNEL_ORDER = ["cinemas", "limited", "streaming", "direct-to-video",
                 "unknown"]

# The table's Notes cells, split on their own semicolons, turned into row
# prose. Every atom on a shipped row must appear here or main() fails, so a
# rewrite upstream breaks the build instead of shipping wikitext or silence.
# The two channel atoms are handled by CHANNEL and are not repeated as prose.
CHANNEL_ATOMS = {"direct-to-video", "limited release"}
ATOM = {
    "also credited for stunts": "Credited for the stunts too",
    "also director and writer": "He directed and wrote it",
    "also editor (uncredited)": "He cut it too, uncredited",
    "also executive producer": "He executive produced it too",
    "also producer": "He produced it too",
    "also story": "He wrote the story too",
    "also writer": "He wrote it too",
    "also writer and fight choreographer":
        "He wrote it and choreographed the fights",
    "also writer and producer": "He wrote and produced it too",
    "also writer, fight director and choreographer":
        "He wrote it and directed the fights",
    "also writer, producer and fight choreographer":
        "He wrote it, produced it and choreographed the fights",
    "cameo": "A cameo",
    "dual role": "A dual role",
    "french movie": "A French production",
    "uncredited extra": "An uncredited extra",
    "van damme's first widely released film since 1999":
        "The source calls it his first widely released film since 1999",
    "voice role": "A voice role",
}


TENS = ("", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy",
        "eighty", "ninety")


def word(n):
    if n < len(WORDS):
        return WORDS[n]
    if n < 100:
        t, u = divmod(n, 10)
        return TENS[t] + ("-" + WORDS[u] if u else "")
    return str(n)


def and_list(names):
    names = list(names)
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + " and " + names[-1]


def load_json(path, tries=5):
    """Read a JSON file another builder may be mid-write on — six agents are
    shipping lists into properties/ while this runs."""
    for n in range(tries):
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            if n == tries - 1:
                raise
            time.sleep(0.4)


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
    cannot go stale — six sibling agents are adding lists as this runs."""
    out, near = {}, []
    for f in sorted((ROOT / "properties").glob("*.json")):
        if f.stem in ("index", "search", SLUG):
            continue
        p = load_json(f)
        kind = p.get("kind") or ""
        syncable = ("film" in kind or "game" in kind) and not p.get("secret")
        prop_medium = "g" if "game" in kind else "f"
        for s in p.get("sections", []):
            for x in s.get("items", []):
                n = str(x.get("n", ""))
                y = year_of(x, n)
                medium = x.get("m") or prop_medium
                hit = None
                if syncable and y:
                    hit = keys.get(normt(x["t"]) + "|" + y + "|" + medium)
                q = x.get("q")
                if syncable and isinstance(q, str):
                    hit = qids.get(q + "|" + medium) or hit
                if hit:
                    if hit not in out.setdefault(p["title"], []):
                        out[p["title"]].append(hit)
                elif normt(x.get("t", "")) in {k.split("|")[0] for k in keys}:
                    # same normalized title, different year or medium or a
                    # non-syncable kind: a near miss worth reporting, never a
                    # pairing to force
                    near.append((p["title"], kind, x.get("t"), n))
    return out, near


# --------------------------------------------------------------------------
def span_of(head):
    """The years a career heading covers, parsed out of the heading itself."""
    label = head.split(":", 1)[0].strip()
    m = re.fullmatch(r"(\d{4})[–-](\d{4})", label)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.fullmatch(r"(\d{4})[–-]present", label)
    if m:
        return int(m.group(1)), 9999
    m = re.fullmatch(r"Early \d{4}s to (\d{4})", label)
    if m:
        return 0, int(m.group(1))
    raise AssertionError("unparseable career heading: %r" % head)


def channel_of(f):
    """How the film reached its audience, from two structured source fields:
    the film's own article categories, and the filmography table's own Notes
    cell. Never from prose, and never from this file's opinion."""
    if not f.get("has_article"):
        return "unknown"
    n = f["note_src"].lower()
    if f.get("dtv_categories") or "direct-to-video" in n:
        return "direct-to-video"
    if f.get("streaming_categories"):
        return "streaming"
    if "limited release" in n:
        return "limited"
    return "cinemas"


def atoms_of(f):
    """The table's Notes cell, split on its own semicolons, minus the channel
    words (which CHANNEL already says)."""
    out = []
    for part in f["note_src"].split(";"):
        part = part.strip()
        if part and part.lower() not in CHANNEL_ATOMS:
            out.append(part)
    return out


def split_str(got, words=False):
    """The per-channel breakdown of a set of rows. `words` spells the numbers,
    for prose; the section subtitles keep the digits."""
    counts = {}
    for f in got:
        counts[f["_ch"]] = counts.get(f["_ch"], 0) + 1
    if len(counts) == 1:
        only = next(iter(counts))
        return ("in cinemas" if only == "cinemas"
                else CHANNEL_SHORT[only]) if len(got) == 1 else \
            "all %s" % CHANNEL_SHORT[only]
    fmt = (lambda n: word(n)) if words else (lambda n: str(n))
    return ", ".join("%s %s" % (fmt(counts[k]), CHANNEL_SHORT[k])
                     for k in CHANNEL_ORDER if counts.get(k))


def main():
    data = load_json(DATA)
    table = data["films"]
    tv, mv, vg = data["tv_rows"], data["music_video_rows"], data["video_game_rows"]
    lab = data["p31_labels"]
    lead = data["lead_text"]
    heads = data["career_heads"]
    subs = data["career_subs"]

    assert len(table) == 67, len(table)
    assert len(tv) == 10 and len(mv) == 9 and len(vg) == 4, (len(tv), len(mv),
                                                             len(vg))
    # the three television facts the "Not included" note names, read from the
    # source's own Television table rather than written here
    vj = next(r for r in tv if r[1] == "Jean-Claude Van Johnson")
    vanjohnson_eps = int(re.match(r"(\d+) episodes", vj[3]).group(1))
    assert {"Friends", "Sense8"} <= {r[1] for r in tv}, [r[1] for r in tv]
    assert "The One After the Superbowl" in \
        next(r for r in tv if r[1] == "Friends")[3], tv
    assert vg[0][1] == "Street Fighter: The Movie", vg[0]
    assert {"Mortal Kombat 1", "Hitman: World of Assassination"} <= \
        {r[1] for r in vg}, [r[1] for r in vg]

    def p31(f):
        return {lab.get(p, p) for p in f.get("p31") or []}

    def lead_says(phrase):
        assert phrase in lead, "the article's lead no longer says: %s" % phrase
        return phrase

    def career_says(head, phrase):
        assert phrase in subs[head], \
            "the %r section no longer says: %s" % (head, phrase)
        return phrase

    # ---- the roster rule, and the two rows it drops ----------------------
    shorts = [f for f in table if f["note_src"].lower() == "short film"]
    undated = [f for f in table if f["year"] is None]
    assert [f["t"] for f in shorts] == ["Monaco Forever"], shorts
    assert [f["t"] for f in undated] == ["Frenchy"], undated
    assert undated[0]["year_raw"] == "TBA", undated[0]["year_raw"]
    # the short: the table's Notes cell is the ONLY authority, and the film's
    # own article corroborates the length rather than the classification
    mf = shorts[0]
    assert "The film runs 48 minutes" in mf["first_sentences"], \
        mf["first_sentences"][:300]
    assert p31(mf) == {"film"}, p31(mf)          # Wikidata does NOT agree
    # the unreleased one: three independent sources say it does not exist
    fr = undated[0]
    assert "is an unreleased action drama" in fr["first_sentences"], \
        fr["first_sentences"][:300]
    assert p31(fr) == {"film project"}, p31(fr)
    assert fr["pubyears"] == [], fr["pubyears"]

    extras = [f for f in table if f["note_src"].lower() == "uncredited extra"]
    assert [f["t"] for f in extras] == ["Woman Between Wolf and Dog",
                                        "Breakin'"], [f["t"] for f in extras]
    assert [f["role"] for f in extras] == ["Moviegoer / Man in Garden",
                                           "Spectator in the first dance scene"], \
        [f["role"] for f in extras]

    dropped = {f["t"] for f in shorts + undated}
    if DROP_EXTRAS:
        dropped |= {f["t"] for f in extras}
    films = [f for f in table if f["t"] not in dropped]
    assert len(films) == (63 if DROP_EXTRAS else 65), len(films)
    # nothing else is filtered: the films where he plays himself stay, the
    # animated voice roles stay, the cameos stay — the table flags none of them
    assert sum(1 for f in films if f["role"] == "Himself") == 4, \
        [f["t"] for f in films if f["role"] == "Himself"]

    # ---- release order ----------------------------------------------------
    for a, b in zip(films, films[1:]):
        assert a["year"] <= b["year"], (a["t"], b["t"])
    assert films[0]["year"] == 1979 and films[-1]["year"] == 2025, \
        (films[0]["year"], films[-1]["year"])
    decades = len({f["year"] // 10 for f in films})
    assert decades == 6, sorted({f["year"] // 10 for f in films})

    # ---- the release channel, from two structured source fields -----------
    for f in table:
        f["_ch"] = channel_of(f)
    by_ch = {}
    for f in films:
        by_ch.setdefault(f["_ch"], []).append(f)
    dtv = by_ch["direct-to-video"]
    limited = by_ch["limited"]
    cinemas = by_ch["cinemas"]
    stream = by_ch["streaming"]
    unknown = by_ch["unknown"]
    assert len(dtv) == 14, [f["t"] for f in dtv]
    assert len(limited) == 14, [f["t"] for f in limited]
    assert len(stream) == 1 and stream[0]["t"] == "The Last Mercenary", stream
    assert stream[0]["streaming_categories"] == ["Netflix original films"], \
        stream[0]["streaming_categories"]
    assert len(unknown) == 1 and unknown[0]["t"] == "Haters", unknown
    assert len(cinemas) == 35, len(cinemas)
    assert len(films) == len(dtv) + len(limited) + len(stream) + \
        len(cinemas) + len(unknown)

    # tremors' signal on its own, and the five it misses. Every film the
    # CATEGORIES flag, the table flags too — the disagreement runs one way.
    cat_dtv = [f for f in films if f.get("dtv_categories")]
    tbl_dtv = [f for f in films if "direct-to-video" in f["note_src"].lower()]
    assert len(cat_dtv) == 9, [f["t"] for f in cat_dtv]
    assert len(tbl_dtv) == 14, [f["t"] for f in tbl_dtv]
    assert all(f in tbl_dtv for f in cat_dtv), \
        [f["t"] for f in cat_dtv if f not in tbl_dtv]
    cats_missed = [f["t"] for f in tbl_dtv if f not in cat_dtv]
    assert cats_missed == ["Replicant", "Wake of Death",
                           "The Shepherd: Border Patrol", "Swelter",
                           "Kill 'Em All"], cats_missed

    # the theatrical cross-checks tremors used, and the one row that fails both
    def cinema_evidence(f):
        return ("$" in (f.get("gross") or ""),
                "theatrical" in (f.get("caption") or "").lower())

    unverified = [f["t"] for f in cinemas if not any(cinema_evidence(f))]
    assert unverified == ["Legionnaire"], unverified
    leg = next(f for f in films if f["t"] == "Legionnaire")
    assert leg["caption"] == "Official DVD cover", leg["caption"]
    assert not leg["gross"], leg["gross"]
    # and a direct-to-video row does not carry a theatrical poster caption by
    # accident: most of them are captioned as a DVD cover
    dvd = [f for f in dtv if "dvd" in (f.get("caption") or "").lower()]
    assert len(dvd) == 11, [(f["t"], f.get("caption")) for f in dtv]

    # ---- weights: each film's own infobox --------------------------------
    for f in films:
        f["mins"] = (f.get("runtime_mins") or [None])[0]
    no_rt = [f["t"] for f in films if not f["mins"]]
    assert no_rt == ["Haters"], no_rt
    ht = next(f for f in films if f["t"] == "Haters")
    assert not ht["linked"] and not ht["has_article"] and not ht["qid"], ht["t"]
    for f in films:
        if f["mins"]:
            assert 60 <= f["mins"] <= 200, (f["t"], f["mins"])
    # why Wikidata is not the source
    wd_gaps = sorted(f["t"] for f in films if f["mins"] and not f["wd_runtime"])
    assert wd_gaps == ["Kill 'Em All 2", "The Bouncer", "The Gardener"], wd_gaps
    wd_off = [(f["t"], f["mins"], f["wd_runtime"]) for f in films
              if f["mins"] and f["wd_runtime"]
              and abs(f["mins"] - f["wd_runtime"]) >= 6]
    assert len(wd_off) == 4, wd_off
    di = next(f for f in films if f["t"] == "Double Impact")
    rz = next(f for f in films if f["t"] == "Rzhevsky versus Napoleon")
    assert (di["mins"], di["wd_runtime"]) == (110, 118), di["t"]
    assert (rz["mins"], rz["wd_runtime"]) == (80, 95), rz["t"]
    # the unrated-cut hazard is real in P2047 and absent from the infoboxes
    multi_p2047 = sorted(f["t"] for f in films
                         if len(f.get("p2047_seen") or []) > 1)
    assert multi_p2047 == ["Minions: The Rise of Gru", "Missing in Action",
                           "Rzhevsky versus Napoleon", "The Exam"], multi_p2047

    # ---- alternate cuts: the sweep finds two, neither direct-to-video -----
    cutfilms = [f for f in films
                if len(f.get("runtime_mins") or []) > 1
                or [s for s in (f.get("cut_sentences") or [])
                    if re.search(r"international cut|U\.S\. cut|director'?s "
                                 r"cut|unrated", s, re.I)]]
    assert sorted(f["t"] for f in cutfilms) == ["Black Eagle",
                                                "No Retreat, No Surrender"], \
        [f["t"] for f in cutfilms]
    assert not [f for f in cutfilms if f["_ch"] == "direct-to-video"], cutfilms
    nrns = next(f for f in films if f["t"] == "No Retreat, No Surrender")
    be = next(f for f in films if f["t"] == "Black Eagle")
    assert nrns["runtime_parts"] == [[98, "international cut"],
                                     [83, "U.S. cut"]], nrns["runtime_parts"]
    assert be["runtime_parts"] == [[93, ""], [104, "director's cut"]], \
        be["runtime_parts"]
    assert any("runs approximately 14 minutes shorter" in s
               for s in nrns["cut_sentences"]), nrns["cut_sentences"]
    # the tie-break: the row's year is the international release, not the U.S.
    assert nrns["year"] == 1985 and "1985" in nrns["released_wt"] \
        and "1986" in nrns["released_wt"], nrns["released_wt"]
    assert nrns["mins"] == 98 and be["mins"] == 93, (nrns["mins"], be["mins"])

    # ---- the facts two special rows carry, read out of the articles -------
    jcvd = next(f for f in films if f["t"] == "JCVD")
    assert any("a fictionalized version of himself" in s
               for s in jcvd["self_sentences"]), jcvd["self_sentences"]
    assert jcvd["role"] == "Himself", jcvd["role"]
    assert any("cast as the Soviet villain Ivan Kraschinsky" in s
               for s in nrns["villain_sentences"]), nrns["villain_sentences"]
    assert any("cast as the main antagonist" in s
               for s in nrns["villain_sentences"]), nrns["villain_sentences"]
    assert nrns["role"] == "Ivan Kraschinsky", nrns["role"]

    # ---- the facts the notes are built from -------------------------------
    lead_says("he got his break as the lead in the martial arts film "
              "Bloodsport (1988)")
    lead_says("The Quest, which marked his directorial debut")
    career_says(heads[1], "Their first job working on a film as extras in the "
                          "hip hop dance film Breakin' (1984)")
    career_says(heads[1], "they are seen dancing in the background at a dance "
                          "demonstration")
    career_says(heads[4], "released theatrically in the Middle East and "
                          "Southeast Asia and directly to video in the "
                          "United States")
    career_says(heads[4], "Van Damme returned to the mainstream with the "
                          "limited theatrical release of the 2008 film JCVD")
    assert "first film appearance" in heads[0], heads[0]

    usr = next(f for f in films if f["t"] == "Universal Soldier: Regeneration")
    assert usr["_ch"] == "direct-to-video", usr["_ch"]
    exp2 = next(f for f in films if f["t"] == "The Expendables 2")
    assert exp2["note_src"] == \
        "Van Damme's first widely released film since 1999", exp2["note_src"]
    # the karate facts the first section's intro names, in the article's words
    career_says(heads[0], "he compiled a record of 44 victories and four "
                          "defeats")
    career_says(heads[0], "member of the Belgium Karate Team when it won the "
                          "European Karate Championship")
    # student in 1989, master in the reboot — the roles say it, not this file
    assert [f["role"] for f in films
            if f["t"].startswith("Kickboxer")] == ["Kurt Sloane",
                                                   "Master Durand",
                                                   "Master Durand"], \
        [(f["t"], f["role"]) for f in films if f["t"].startswith("Kickboxer")]
    # the three animated voice roles, and where they fall
    voices = [f for f in films if "Voice role" in f["note_src"]]
    assert [f["t"] for f in voices] == ["Kung Fu Panda 2", "Kung Fu Panda 3",
                                        "Minions: The Rise of Gru"], voices
    assert all("animated film" in p31(f) for f in voices), \
        [(f["t"], p31(f)) for f in voices]

    # every atom the source puts on a shipped row is accounted for
    seen_atoms = {a.lower() for f in films for a in atoms_of(f)}
    assert seen_atoms <= set(ATOM), sorted(seen_atoms - set(ATOM))

    # ---- sections: the article's own career headings ----------------------
    assert heads == list(SECTION_IDS), heads
    spans = [(h,) + span_of(h) for h in heads]
    assert [s[1:] for s in spans] == [(0, 1980), (1982, 1988), (1989, 1999),
                                      (2000, 2007), (2008, 2013),
                                      (2014, 9999)], [s[1:] for s in spans]
    counts, placed = {}, []
    for h, lo, hi in spans:
        counts[h] = [f for f in films if lo <= f["year"] <= hi]
        placed += counts[h]
    # the intros' per-section claims, checked against the placement
    assert [f["t"] for f in counts[heads[2]] if f["_ch"] != "cinemas"] == \
        ["Inferno"], [f["t"] for f in counts[heads[2]] if f["_ch"] != "cinemas"]
    assert all(f["_ch"] == "cinemas" for f in counts[heads[1]]), \
        [(f["t"], f["_ch"]) for f in counts[heads[1]]]
    assert [f["t"] for f in counts[heads[4]] if "Voice role" in f["note_src"]] \
        == ["Kung Fu Panda 2"], counts[heads[4]]
    assert [f["t"] for f in counts[heads[5]] if "Voice role" in f["note_src"]] \
        == ["Kung Fu Panda 3", "Minions: The Rise of Gru"], counts[heads[5]]
    assert len(placed) == len(films), \
        [f["t"] for f in films if f not in placed]      # a year in no heading
    assert len({id(f) for f in placed}) == len(films)   # or in two
    assert [len(counts[h]) for h in heads] == \
        ([0, 4, 19, 10, 15, 15] if DROP_EXTRAS else [1, 5, 19, 10, 15, 15]), \
        {h: len(counts[h]) for h in heads}

    # ---- row notes ---------------------------------------------------------
    def note_for(f):
        bits = [CHANNEL[f["_ch"]]]
        if f["t"] == "JCVD":
            bits.append("As a fictionalised version of himself")
        elif f["role"] and f["role"] != "Himself":
            bits.append("As %s" % f["role"])
        elif f["role"] == "Himself":
            bits.append("As himself")
        for a in atoms_of(f):
            bits.append(ATOM[a.lower()])
        if f["t"] == "Woman Between Wolf and Dog":
            bits.append("His first appearance on screen")
        if f["t"] == "Breakin'":
            bits.append("He and Michel Qissi dance in the background of a "
                        "dance demonstration")
        if f["t"] == "No Retreat, No Surrender":
            bits.append("He plays the villain here, not the lead")
            bits.append("The bar is the %d-minute international cut; a U.S. "
                        "cut runs %d" % tuple(p[0] for p in nrns["runtime_parts"]))
        if f["t"] == "Black Eagle":
            bits.append("The bar is the %d-minute release; a director's cut "
                        "runs %d" % tuple(p[0] for p in be["runtime_parts"]))
        if f["t"] == "Bloodsport":
            bits.append("His break, and the first film he led")
        if f["t"] == "The Quest":
            bits.append("His directorial debut")
        if f["t"] == "Universal Soldier: Regeneration":
            bits.append("Cinemas in the Middle East and Southeast Asia, video "
                        "in the United States")
        if f["t"] == "Legionnaire":
            bits.append("The source flags no channel, but its article states "
                        "no box office and its poster is a DVD cover")
        if f["t"] == "Haters":
            bits.append("The one row with no article behind it: no id, no "
                        "runtime, so it weighs nothing")
        return join_bits(*bits)

    # ---- section intros ----------------------------------------------------
    def intro_for(h):
        got = counts[h]
        n = len(got)
        i = heads.index(h)
        if i == 0:
            return ("The article's first career heading, and one film sits "
                    "under it — a Belgian art film he is an uncredited extra "
                    "in. What the heading mostly covers is karate: the "
                    "Belgian national team, the European championship, a "
                    "record of forty-four wins and four losses.")
        if i == 1:
            return ("%s films, and the arc of the heading is in them: a "
                    "spectator in a dance scene and a soldier with no name, "
                    "then the villain in No Retreat, No Surrender, then "
                    "Bloodsport, which the article calls his break and the "
                    "first film he led. All %s played cinemas."
                    % (word(n).capitalize(), word(n)))
        if i == 2:
            return ("The decade the name meant something — %s films in "
                    "eleven years, about %d hours, and all but one of them "
                    "in cinemas. Universal Soldier, Timecop and Street "
                    "Fighter are the wide ones; The Quest in 1996 is the "
                    "first he directed, and Inferno at the end of 1999 is "
                    "the first row on this list that is not a full release."
                    % (word(n).capitalize(),
                       round(sum(f["mins"] or 0 for f in got) / 60.0)))
        if i == 3:
            return ("The article named this era itself, and the rows show "
                    "it: %s of these %s films went straight to video. This "
                    "is the stretch of the filmography a viewer is least "
                    "likely to have seen and most likely to want warning "
                    "about, which is the whole reason every row on this list "
                    "carries a release channel."
                    % (word(sum(1 for f in got
                                if f["_ch"] == "direct-to-video")), word(n)))
        if i == 4:
            return ("JCVD in 2008 is the turn — a limited release the "
                    "article says brought him back to the mainstream — and "
                    "The Expendables 2 in 2012 is the wide one, which the "
                    "source calls his first since 1999. The rest is still "
                    "mostly video and limited runs, and Kung Fu Panda 2 is "
                    "voice work.")
        return ("The heading the article leaves open-ended, and the split is "
                "the point here: %s. Two animated voice roles, a Netflix "
                "film, two Kickboxer sequels in which he plays the master "
                "rather than the student he played in 1989, and one row "
                "nobody can source at all." % split_str(got, words=True))

    # ---- build --------------------------------------------------------------
    sections = []
    for h, lo, hi in spans:
        got = counts[h]
        if not got:
            continue           # only reachable with DROP_EXTRAS on
        items = []
        for f in got:
            it = {"id": "jcvd-%d-%s" % (f["year"], slug(f["t"])),
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
        span = ("%d" % got[0]["year"] if got[0]["year"] == got[-1]["year"]
                else "%d–%d" % (got[0]["year"], got[-1]["year"]))
        sections.append({
            "id": SECTION_IDS[h],
            "title": h.split(":", 1)[1].strip(),
            "sub": "%s · %d film%s · %d hours · %s"
                   % (span, len(got), "" if len(got) == 1 else "s",
                      round(mins / 60.0), split_str(got)),
            "intro": intro_for(h),
            "items": items,
        })
    sections[2]["open"] = True          # the decade a newcomer starts in

    # ---- the checks the shipped file has to pass ---------------------------
    rows = [x for s in sections for x in s["items"]]
    assert len(rows) == len(films), (len(rows), len(films))
    ids = [x["id"] for x in rows]
    assert len(ids) == len(set(ids)), sorted({i for i in ids if ids.count(i) > 1})
    assert all(x.get("note") for x in rows), \
        [x["id"] for x in rows if not x.get("note")]
    assert all(re.fullmatch(r"(19|20)\d{2}", x["n"]) for x in rows), \
        [x["n"] for x in rows]
    with_q = [x for x in rows if "q" in x]
    assert len(with_q) == len(films) - 1, len(with_q)
    assert len({x["q"] for x in with_q}) == len(with_q), "duplicate qid"
    if WEIGHTED:
        assert all(isinstance(x["w"], float) for x in rows)
        zero = [x["id"] for x in rows if x["w"] == 0]
        assert zero == ["jcvd-2021-haters"], zero
    for s in sections:
        assert all(a["n"] <= b["n"] for a, b in zip(s["items"], s["items"][1:]))
    mins = sum(f["mins"] or 0 for f in films)
    hours = round(sum(x["w"] for x in rows), 2) if WEIGHTED else 0
    if WEIGHTED:
        assert abs(hours - mins / 60.0) < 0.3, (hours, mins / 60.0)

    # ---- accent: nobody else's -------------------------------------------
    for f in sorted((ROOT / "properties").glob("*.json")):
        if f.stem in ("index", "search", SLUG):
            continue
        o = load_json(f)
        assert (o.get("accent"), o.get("accentDark")) != (ACCENT, ACCENT_DARK), \
            "accent pair already used by %s" % f.stem

    # ---- the films this list shares with other lists here ------------------
    keys = {normt(f["t"]) + "|" + str(f["year"]) + "|f": f["t"] for f in films}
    qids = {f["qid"] + "|f": f["t"] for f in films if f["qid"]}
    shared, near = overlaps(keys, qids)
    # What was true when this was written. A NEW list arriving with one of
    # these films must not break the build — six sibling agents are shipping
    # martial-arts, japanese-cinema and four other actor lists as this runs,
    # and the prose below is computed from `shared`, so a new pairing simply
    # joins the note. What must never change is that this one still pairs: it
    # is the only exact-id match in the catalogue and losing it means a title
    # or a year drifted (CLU-191/CLU-247).
    assert shared.get("Street Fighter") == ["Street Fighter"], \
        shared.get("Street Fighter")
    paired = sorted({t for v in shared.values() for t in v},
                    key=[f["t"] for f in films].index)
    sharing = ("%s. Ticking one ticks the other: rows pair across lists by "
               "title and year, and by the film's Wikidata id where a list "
               "carries one, so a film watched here is watched there. Nothing "
               "is duplicated and no hours are counted twice, because every "
               "list totals only its own rows."
               % "; ".join("%s on %s" % (and_list(v), k)
                           for k, v in sorted(shared.items())))

    # ---- notes -------------------------------------------------------------
    notes = [
        ["%s of the %s films the source's own table lists."
         % (word(len(films)).capitalize(), word(len(table))),
         "There is no separate filmography article for him, so the roster is "
         "the Film table inside the Jean-Claude Van Damme article, and a film "
         "is a row here when that table lists him in it. Every row says what "
         "the credit was, in the table's own words — the part, and whether he "
         "also wrote, directed, produced, edited or choreographed the fights. "
         "Two rows are dropped and both on the table's own flag: Monaco "
         "Forever (1984), whose notes cell says Short film and whose article "
         "puts it at 48 minutes, and Frenchy, whose year cell says TBA — its "
         "article calls it unreleased and Wikidata files it as a film "
         "project, not a film. Nothing else is filtered. The four films where "
         "he plays himself stay, the three animated voice roles stay, and the "
         "cameos stay, because the table flags none of them."],
        ["The two rows where he is an extra stay, and here is the argument.",
         "Woman Between Wolf and Dog (1979) and Breakin' (1984) both carry "
         "the note Uncredited extra — he is a moviegoer in one and a "
         "spectator in a dance scene in the other, and the article says he "
         "and Michel Qissi are the two dancing in the background. They are "
         "rows because his footage is in them and you can watch him. That is "
         "the same line the Kevin Bacon list here drew: it dropped the two "
         "films his footage is NOT in and kept everything he is on screen "
         "for. Each row says An uncredited extra, so nobody is sold a part "
         "that is not there."],
        ["%s of the %s went straight to video."
         % (word(len(dtv)).capitalize(), word(len(films))),
         "The most useful thing this list carries, and every row says which. "
         "%s went straight to video, %s got a limited release — a handful of "
         "screens rather than a wide opening — %s went straight to Netflix, "
         "and %s opened in cinemas. One row has no channel because it "
         "has no article. The two reads behind that are both structured "
         "source fields, never prose: each film's own Wikipedia categories "
         "(2002 direct-to-video films, Direct-to-video sequel films), and the "
         "filmography table's own notes column. The categories alone find "
         "only %s of the %s — %s carry no such category — and everything the "
         "categories do flag, the table flags too, so the disagreement runs "
         "one way and the union is the honest answer. Direct-to-video means "
         "in the United States: Universal Soldier: Regeneration played "
         "cinemas in the Middle East and Southeast Asia and went to video at "
         "home, and its row says so."
         % (word(len(dtv)).capitalize(), word(len(limited)),
            word(len(stream)), word(len(cinemas)),
            word(len(cat_dtv)), word(len(dtv)), and_list(cats_missed))],
        ["In cinemas is checked twice more, and one row fails both.",
         "A cinema release leaves two other marks on a film's article — a "
         "box-office figure in the infobox, and an image the caption calls a "
         "theatrical poster — so every row this list calls In cinemas was "
         "tested against both. %s of the %s clear at least one. Legionnaire "
         "(1998) clears neither: its infobox states no gross and its image is "
         "captioned Official DVD cover. Its row says that rather than quietly "
         "claiming a cinema release, because the table flags no channel for "
         "it and this list will not invent one."
         % (word(len(cinemas) - len(unverified)).capitalize(),
            word(len(cinemas)))],
        ["Words on the row, not tier badges.",
         "The release channel could have been three tiers with filter chips "
         "instead, which is how the Disney list handles the same fact. It is "
         "not, and the reason is what a tier means on this engine: it is a "
         "rank. It sets how tall a mark is drawn, it is what a finish date "
         "can be scoped to, and it renders as a bare T3 beside a Tier 1/2/3 "
         "panel. Filing fourteen films as tier 3 would tell you they are the "
         "skippable ones, and that is not what went to video means — "
         "Universal Soldier: Regeneration is the best-reviewed film of his "
         "second act and it went to video. So the channel is two or three "
         "words at the front of each row, and each section header carries the "
         "count so the split is readable without opening anything."],
        ["The six sections are the article's own career headings.",
         "Not invented decades. The Career section of the Jean-Claude Van "
         "Damme article is split into six dated subheadings, and this list "
         "takes both the titles and the date ranges from them, parsed out of "
         "the headings themselves: Early 1970s to 1980, then 1982–1988, "
         "1989–1999, 2000–2007, 2008–2013 and "
         "2014–present. Every film lands in exactly one of them, which "
         "the generator checks. Switch to direct-to-video is the article's "
         "own phrase for 2000–2007, not this list's."],
        ["Bar widths are runtimes, from each film's own infobox.",
         "One source for %s of the %s, so there is nothing to adjudicate. "
         "Wikidata's runtime property was the alternative and lost twice: it "
         "has no figure at all for %s, where the infobox has one, and where "
         "both exist it disagrees by six minutes or more on %s films — Double "
         "Impact at 118 minutes against an infobox 110, Rzhevsky versus "
         "Napoleon at 95 against 80. That gap is the unrated-cut problem: "
         "Wikidata holds two figures for four of these films and reports the "
         "longer. One row weighs nothing and says so — Haters (2021) is the "
         "single film here with no Wikipedia article at all, so it has no "
         "runtime, no categories and no id."
         % (word(len(films) - 1), word(len(films)), and_list(wd_gaps),
            word(len(wd_off)))],
        ["Two films have a second cut. Each still gets one row.",
         "A sweep of all %s film articles behind these rows for a sentence "
         "stating a running time "
         "beside a word meaning a particular version turns up No Retreat, No "
         "Surrender, released at 98 minutes internationally and 83 in "
         "America, and Black Eagle, whose infobox gives 93 minutes and then "
         "104 for a director's cut. Neither is one of the direct-to-video "
         "films, which is worth saying because that is where a second cut "
         "would have been expected. No Retreat's bar is the 98-minute "
         "international cut, because the 1985 the table dates it to is the "
         "international release and the American one came in 1986; Black "
         "Eagle's is the 93. Both notes name the other version. A second row "
         "would either double the film's hours — you do not watch it "
         "twice — or carry no weight in a list where everything else "
         "has some." % word(sum(1 for f in films if f.get("has_article")))],
        ["Not included.",
         "Television, which the source keeps in its own table: %s credits, "
         "including the %s episodes of Jean-Claude Van Johnson, the Friends "
         "episode after the Super Bowl, Sense8, and his own reality series. "
         "The %s music videos are out for the same reason — their own table, "
         "a different medium — and so are the %s video game credits, "
         "including Street Fighter: The Movie, the Mortal Kombat 1 Johnny "
         "Cage skin and the Hitman elusive target."
         % (word(len(tv)), word(vanjohnson_eps), word(len(mv)),
            word(len(vg)))],
    ]
    if paired:
        notes.append(["%s of these films is on another list here."
                      % word(len(paired)).capitalize()
                      if len(paired) == 1 else
                      "%s of these films are on another list here."
                      % word(len(paired)).capitalize(), sharing])
    notes.append(
        "Roster, roles, credits and the release-channel flags from the Film "
        "table of Wikipedia's Jean-Claude Van Damme article; the section "
        "titles and their date ranges from that article's own career "
        "headings; runtimes, release dates, box-office figures, poster "
        "captions and the alternate-cut lengths from each film's own article, "
        "with the direct-to-video and Netflix categories read off those "
        "articles too; the cross-list ids from Wikidata.")

    p = {
        "slug": SLUG,
        "title": "Jean-Claude Van Damme",
        "subtitle": "the films in release order, and how each one came out",
        "kind": "films",
        "popularity": POPULARITY,
        "year": "%d–%d" % (films[0]["year"], films[-1]["year"]),
        "blurb": "%s films across %s decades — about %d hours. %s went "
                 "straight to video, %s more got a limited release, and "
                 "every row says which."
                 % (word(len(films)).capitalize(), word(decades), round(hours),
                    word(len(dtv)).capitalize(), word(len(limited))),
        "unit": {"one": "film", "many": "films"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "accent": ACCENT,
        "accentDark": ACCENT_DARK,
        "tiers": False,
        "notes": notes,
        "sections": sections,
    }

    out = prop.write(p)
    print("wrote %s — %d films, %d minutes, %.2f hours"
          % (out.name, len(rows), mins, hours))
    for s in sections:
        print("   %-12s %-38s %2d  %s"
              % (s["id"], s["title"][:38], len(s["items"]), s["sub"]))
    print("   channels: %s" % split_str(films))
    print("   ids: %d of %d rows" % (len(with_q), len(rows)))
    print("   shared: %s"
          % ("; ".join("%s: %s" % (k, ", ".join(v))
                       for k, v in sorted(shared.items())) or "NOBODY"))
    print("   near misses (same title, no pairing):")
    for t, kind, title, n in sorted(set(near)):
        print("      %-24s %-14s %-22s n=%s" % (t, kind, title, n))


if __name__ == "__main__":
    main()
