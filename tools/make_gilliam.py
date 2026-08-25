#!/usr/bin/env python3
"""Generate properties/gilliam.json.

    PYTHONIOENCODING=utf-8 python tools/make_gilliam.py

Every feature Terry Gilliam has directed, in release order — the rows of the
first table on Wikipedia's "Terry Gilliam filmography", every one of which is
a bare {{yes}} in the Director column. There are thirteen, and both the
filmography's lead and the biography's lead say thirteen independently.

THE CREDIT TEST, AND THE FOUR THINGS IT KEEPS OUT

Features he DIRECTED. That admits Monty Python and the Holy Grail, which he
co-directed with Terry Jones and which is a feature directorial debut for
both of them; the row says so. It excludes, in each case because the
filmography files the credit somewhere other than its feature table:

  * the Python films he wrote or animated but did not direct — Life of Brian,
    The Meaning of Life, And Now for Something Completely Different, the
    Hollywood Bowl concert film. Two of those carry an "also director of the
    animated segments" note, and animating a sequence is not directing a
    feature;
  * The Crimson Permanent Assurance, the piece he directed inside The Meaning
    of Life. The question was whether the source treats it as a standalone
    work, and it does — but as a SHORT: the filmography lists it in its Short
    film table, its own article opens "is a 1983 British swashbuckling comedy
    short film", it runs sixteen minutes, and the biography has him nominated
    for the BAFTA Award for Best Short Film for it. So it is excluded with
    the other four shorts, not admitted as a fourteenth feature, and the
    notes name it rather than leaving it to look forgotten;
  * the television, the commercials, and the acting;
  * Lost in La Mancha and He Dreams of Giants, which are documentaries ABOUT
    him — both directed by Keith Fulton and Louis Pepe, neither anywhere on
    his filmography. Named in the notes for the same reason.

THE LEAD CROSS-CHECK

The table is checked against prose written independently of it, because a
rowspan bug silently dropped a film from another list in this session and
this table rowspans its Year cell at 2005. The biography's lead italicises
fifteen works; eleven are rows here and the other four are the exclusions
above, each one filed by the source in a different table. The reverse
direction holds for eleven of thirteen — the lead's phrasing is "other
directing credits include", which does not claim to be exhaustive, and the
two features it leaves out are asserted by name below so that a change to
either side breaks the build instead of passing quietly.

BRAZIL, AND THE ALTERNATE-CUTS RULE

One film here exists at more than one length, and it is the most famous
recutting fight in cinema. Its infobox states three:

    142 minutes (final cut) · 132 minutes (American Universal cut) ·
    94 minutes ("Love Conquers All" cut)

HOW-IT-WORKS says one row per film and the bar measures the theatrical
release. The unusual thing about Brazil is that there were two theatrical
releases at two lengths, and the article says which came first:

    "Gilliam's original cut of the film was 142 minutes long and ends on a
    dark note. This version was released in Europe and internationally by
    20th Century Fox without issue. However, the film's US distribution was
    handled by Universal Pictures ... This prompted Universal to finally
    agree to release a modified 132-minute version supervised by Gilliam in
    1985."

So 142 IS the theatrical release — the first one, in February 1985, and the
one the rest of the world saw. Taking it is the DEFAULT rule, not the
Kingdom of Heaven override: nothing here prefers a home-video cut over a
cinema one, it picks between two cinema releases and takes the earlier and
wider. It independently satisfies the second exception too — it is the
version worth watching, it is the only one Criterion has ever released, and
the row says which to watch in plain words. The row note is the only place
any of this lives; there is no second row for a cut, because a row is a
thing to watch and tick, and ticking Brazil twice is not a thing anyone does.

RUNTIMES

Each film's own infobox, for all thirteen, and nothing else. Wikidata P2047
also covers all thirteen and would have weighted the list too, but it carries
142 and 140 for Brazil with no qualifier on either, so it cannot say which of
Brazil's releases a number belongs to. A source that cannot answer the only
hard question on the list is the wrong source for the list. Wikidata is
collected anyway as a cross-check and recorded on every row; the three places
the two disagree by more than a minute are named in the notes.

Data:   scratch/agent-gilliam/fetch.py -> collect.py -> tools/data/gilliam.json
Accent: scratch/agent-gilliam/accent.py
"""
import json
import pathlib
import re
import sys
import unicodedata

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop
from gwlib.prop import join_bits, slug

SLUG = "gilliam"
ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "tools" / "data" / "gilliam.json"

# The 142-minute figure the row measures, and the two other lengths the same
# infobox field states. Written as labels rather than numbers so the asserts
# below read them out of the data and nothing here is typed in.
BRAZIL_CUT = "final cut"

ERAS = [
    ("python", "Python, then on his own", 1975, 1977,
     "His first two, two years apart, both British and both of which he "
     "co-wrote. Monty Python and the Holy Grail is a feature directing debut "
     "for him and for Terry Jones, who directed it with him; Jabberwocky, "
     "from the Lewis Carroll poem, is the first he directed alone. Nothing "
     "else on this list is a Python film."),
    ("imagination", "The Trilogy of Imagination", 1981, 1988,
     "Gilliam's own name for these three, and all three articles carry the "
     "claim. Time Bandits' article gives the through-line: the same "
     "fantasist seen from three ages — a young boy, then a grown man, then "
     "an old one. It is also the stretch that contains the recutting fight, "
     "and the one row on this list whose length took a decision."),
    ("american", "The American films", 1991, 1998,
     "The only three rows whose country is the United States and nothing "
     "else. Two of them are the first films he directed without a writing "
     "credit of any kind, from screenplays by Richard LaGravenese and by "
     "David and Janet Peoples; the third he co-wrote. The first of the three "
     "is the only Oscar winner of his career."),
    ("coproductions", "The co-productions", 2005, 2018,
     "From here on nothing is American and nothing is made in one country. "
     "These five are the only rows assembled across two or more countries "
     "without the United States among them, and the number of partners "
     "climbs as the money gets harder: two, two, three, three, and finally "
     "five for a film he had been trying to make since 1989."),
]


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
    else an explicit y, else the single year named in the note.

    The note fallback is what makes these groups possible at all. Criterion
    numbers its rows by spine — Brazil is "#51" — so a title-and-number match
    could never fire, and every one of the seven pairs below is made through
    the year in Criterion's own note."""
    if re.fullmatch(r"(18|19|20)\d{2}", n):
        return n
    explicit = str(x.get("y", ""))
    if re.fullmatch(r"(18|19|20)\d{2}", explicit):
        return explicit
    found = set(re.findall(r"\b((?:18|19|20)\d{2})\b", x.get("note") or ""))
    return found.pop() if len(found) == 1 else None


def overlaps(keys):
    """{sync key -> [list titles]} for the other film lists already shipped.

    Computed off the catalogue on disk instead of typed, so the note naming
    the shared films cannot quietly go stale, and so a title that fails to
    match shows up here as a missing group rather than as a film that is
    ticked on one list and blank on another."""
    out = {}
    for f in sorted((ROOT / "properties").glob("*.json")):
        if f.stem in ("index", "search", SLUG):
            continue
        p = json.loads(f.read_text(encoding="utf-8"))
        if p.get("secret") or "film" not in (p.get("kind") or ""):
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


def and_list(names):
    names = list(names)
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + " and " + names[-1]


WORDS = ("no", "one", "two", "three", "four", "five", "six", "seven", "eight",
         "nine", "ten", "eleven", "twelve", "thirteen")


def word(n):
    """Small counts read as words in prose; anything bigger stays a numeral."""
    return WORDS[n] if n < len(WORDS) else str(n)


def countries(article):
    """The country field split into names. clean() leaves {{Plainlist}} items
    pipe-separated and {{ubl}} items comma-separated, so both count."""
    return [c.strip() for c in re.split(r"[|,]", article.get("country", ""))
            if c.strip()]


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    films = data["films"]
    shorts, credits = data["shorts"], data["other_credits"]
    docs = data["documentaries_about_him"]

    # ---- the table is the credit test -------------------------------------
    assert len(films) == 13, len(films)
    assert films[0]["t"] == "Monty Python and the Holy Grail" and \
        films[0]["year"] == 1975, films[0]
    assert films[-1]["t"] == "The Man Who Killed Don Quixote" and \
        films[-1]["year"] == 2018, films[-1]
    assert all(a["year"] <= b["year"] for a, b in zip(films, films[1:])), \
        "films are not in release order"
    # the one year with two releases, and the rowspan that carries its year
    # down to the second row. Get this wrong and a film silently vanishes.
    doubles = sorted(y for y in {f["year"] for f in films}
                     if sum(1 for f in films if f["year"] == y) > 1)
    assert doubles == [2005], doubles
    pair = [f for f in films if f["year"] == 2005]
    assert [f["t"] for f in pair] == ["The Brothers Grimm", "Tideland"], pair
    assert pair[0]["release_date"] < pair[1]["release_date"], \
        [f["release_date"] for f in pair]

    by_t = {f["t"]: f for f in films}
    # Holy Grail is the only co-direction, and the table says with whom
    codirected = [f for f in films if "Co-directed" in f["tablenote"]]
    assert [f["t"] for f in codirected] == ["Monty Python and the Holy Grail"], \
        [f["t"] for f in codirected]
    grail = codirected[0]
    assert grail["tablenote"] == "Co-directed with Terry Jones", \
        grail["tablenote"]
    assert "directorial debuts" in grail["article"]["lead"], \
        grail["article"]["lead"][:300]
    assert "solo directorial debut" in by_t["Jabberwocky"]["article"]["lead"], \
        by_t["Jabberwocky"]["article"]["lead"][:300]

    # ---- the lead cross-check ---------------------------------------------
    # both leads state the count, and they were written separately
    assert data["lead"]["spine_says_features"] == 13, data["lead"]
    assert data["lead"]["bio_says_features"] == "thirteen", data["lead"]
    assert data["lead"]["spine_says_shorts"] == "five", data["lead"]
    # the filmography's own lead names no films at all, which is why the
    # check runs against the biography's
    assert data["lead"]["spine_italic_links"] == [], \
        data["lead"]["spine_italic_links"]

    lead_pages = [p for p, _ in data["lead"]["bio_italic_links"]]
    assert len(lead_pages) == 15, lead_pages
    row_pages = {f["page"] for f in films}
    # every one of the four non-rows is filed by the SOURCE in another table
    elsewhere = ({s["page"] for s in shorts} | {c["page"] for c in credits} |
                 {"Monty Python's Flying Circus"})
    unaccounted = [p for p in lead_pages
                   if p not in row_pages and p not in elsewhere]
    assert not unaccounted, \
        "lead names a work that is neither a row nor a named exclusion: %s" \
        % unaccounted
    excluded_in_lead = [p for p in lead_pages if p not in row_pages]
    assert excluded_in_lead == [
        "Monty Python's Flying Circus", "Monty Python's Life of Brian",
        "Monty Python's The Meaning of Life",
        "The Crimson Permanent Assurance"], excluded_in_lead
    # and the reverse: the two features the lead's "include" leaves out
    not_in_lead = [f["t"] for f in films if f["page"] not in lead_pages]
    assert not_in_lead == ["Tideland", "The Zero Theorem"], not_in_lead

    # ---- what is not here, counted from the source ------------------------
    assert len(shorts) == 6 and sum(1 for s in shorts if s["directed"]) == 5, \
        [(s["t"], s["directed"]) for s in shorts]
    directed_shorts = [s for s in shorts if s["directed"]]
    cpa = next(s for s in directed_shorts
               if s["t"] == "The Crimson Permanent Assurance")
    # the source's own classification is the whole answer to whether it is a
    # row: the filmography files it as a short and its article says the same
    assert cpa["runtime"] == 16, cpa["runtime"]
    assert "short film directed by Terry Gilliam" in cpa["article"]["lead"], \
        cpa["article"]["lead"][:200]
    assert "prelude to the film Monty Python's The Meaning of Life" in \
        cpa["article"]["lead"], cpa["article"]["lead"][:400]
    assert "nominated for the BAFTA Award for Best Short Film" in \
        data["lead"]["bio_text"], data["lead"]["bio_text"][:900]
    # two of the five directed shorts have no runtime anywhere, so a shorts
    # section could not be fully weighted even if one were wanted
    unweighable = [s["t"] for s in directed_shorts if not s["runtime"]]
    assert unweighable == ["Miracle of Flight", "Story Time"], unweighable

    assert len(credits) == 5, [c["t"] for c in credits]
    animated = [c for c in credits if "animat" in c["tablenote"].lower()]
    assert [c["t"] for c in animated] == \
        ["And Now for Something Completely Different",
         "Monty Python's The Meaning of Life"], [c["t"] for c in animated]
    assert sum(1 for c in credits if c["wrote"]) == 4, credits
    assert [c["t"] for c in credits if c["produced"]] == \
        ["The Piano Tuner of Earthquakes"], credits

    assert len(docs) == 2, docs
    assert all(d["director"] == "Keith Fulton, Louis Pepe" for d in docs), \
        [(d["t"], d["director"]) for d in docs]
    assert all("documentary film" in d["lead"] for d in docs), \
        [d["lead"][:120] for d in docs]

    # ---- runtimes ---------------------------------------------------------
    # Weighting is all-or-nothing: a row with no `w` on a weighted list is
    # silently worth one hour (CLU-131), so either every row carries a
    # sourced runtime or none of them does.
    assert all(f["cuts"] for f in films), \
        [f["t"] for f in films if not f["cuts"]]
    assert all(f["qid"] and f["wd_year_gate"] for f in films), \
        [f["t"] for f in films if not (f["qid"] and f["wd_year_gate"])]

    # exactly one film states more than one length, and no article on the
    # list carries a version/cut/edition section heading
    multi = [f for f in films if len(f["cuts"]) > 1]
    assert [f["t"] for f in multi] == ["Brazil"], [f["t"] for f in multi]
    assert not [f["t"] for f in films if f["article"]["version_heads"]], \
        [(f["t"], f["article"]["version_heads"]) for f in films]

    # ---- Brazil: the one decision on this list ----------------------------
    br = by_t["Brazil"]
    labelled = {label: mins for mins, label in br["cuts"]}
    assert labelled == {"final cut": 142,
                        "American Universal cut": 132,
                        '"Love Conquers All" cut': 94}, labelled
    # the sentences the choice rests on, asserted so a rewrite of the article
    # breaks the build rather than leaving the row note claiming something
    # the source no longer says
    rel = data["brazil_release"]
    assert "Gilliam's original cut of the film was 142 minutes long" in rel, rel[:400]
    assert "released in Europe and internationally by 20th Century Fox" in rel, \
        rel[:600]
    assert "release a modified 132-minute version supervised by Gilliam in 1985" \
        in rel, rel[-600:]
    assert "142-minute cut of the film" in data["brazil_home_media"] and \
        "The Criterion Collection" in data["brazil_home_media"], \
        data["brazil_home_media"][:400]
    # THE OVERRIDE, in one visible place. HOW-IT-WORKS' default is the
    # theatrical release, and 142 is a theatrical release — the first, in
    # February 1985, and the one every territory outside America saw. The
    # 132 is the second theatrical release, cut for one country nine months
    # later. So this is the default applied to a film with two theatrical
    # releases, not the Kingdom of Heaven exception; it happens to satisfy
    # that exception as well, and the row recommends a version in plain
    # words either way.
    br["runtime"] = labelled[BRAZIL_CUT]
    assert br["runtime"] == 142 and br["release_date"] == "1985-02-20", br
    assert br["runtime"] == max(labelled.values()), labelled

    for f in films:
        if f["runtime"] is None:
            f["runtime"] = f["cuts"][0][0]
    assert all(isinstance(f["runtime"], int) and 15 <= f["runtime"] <= 250
               for f in films), [(f["t"], f["runtime"]) for f in films]
    # every shipped number is a figure the infobox itself states
    assert all(f["runtime"] in [m for m, _ in f["cuts"]] for f in films), \
        [(f["t"], f["runtime"], f["cuts"]) for f in films]

    # the three rows where the source we did not use disagrees by more than a
    # minute. Named in the notes, not blended in — one source, kept to.
    drift = [f for f in films if f["wd_runtime"] and
             abs(f["runtime"] - f["wd_runtime"]) > 1]
    assert [f["t"] for f in drift] == \
        ["Jabberwocky", "Time Bandits", "12 Monkeys"], [f["t"] for f in drift]
    assert by_t["Brazil"]["wd_p2047"] == [140, 142], by_t["Brazil"]["wd_p2047"]

    # ---- what the era intros claim ----------------------------------------
    first = [f for f in films if f["year"] <= 1977]
    assert len(first) == 2 and all(f["wrote"] for f in first), first
    assert all(countries(f["article"]) == ["United Kingdom"] for f in first), \
        [countries(f["article"]) for f in first]
    assert by_t["Jabberwocky"]["article"]["based_on"] == "Lewis Carroll", \
        by_t["Jabberwocky"]["article"].get("based_on")

    trio = [f for f in films if 1981 <= f["year"] <= 1988]
    assert [f["t"] for f in trio] == \
        ["Time Bandits", "Brazil", "The Adventures of Baron Munchausen"], trio
    # the Trilogy of Imagination is Gilliam's own phrase and all three
    # articles carry it; the through-line comes from Time Bandits'
    for f in trio:
        assert "Trilogy of Imagination" in data["trilogy_claims"][f["t"]], \
            f["t"]
    tb = data["trilogy_claims"]["Time Bandits"]
    assert "a young boy in this film" in tb and "an old man in" in tb, tb

    usa = [f for f in films if countries(f["article"]) == ["United States"]]
    assert [f["t"] for f in usa] == \
        ["The Fisher King", "12 Monkeys",
         "Fear and Loathing in Las Vegas"], [f["t"] for f in usa]
    assert [f["t"] for f in usa if not f["wrote"]] == \
        ["The Fisher King", "12 Monkeys"], [f["t"] for f in usa if not f["wrote"]]
    assert by_t["The Fisher King"]["article"]["writer"] == \
        "Richard LaGravenese", by_t["The Fisher King"]["article"]["writer"]
    assert by_t["12 Monkeys"]["article"]["screenplay"] == \
        "David Peoples, Janet Peoples", by_t["12 Monkeys"]["article"]["screenplay"]
    assert "only Oscar-winning film of Gilliam's career" in \
        by_t["The Fisher King"]["article"]["lead"], \
        by_t["The Fisher King"]["article"]["lead"][:400]
    # "the first he directed with no writing credit" — a bare {{no}} in the
    # Writer column, and the first such row in release order. Everything
    # before it is a bare {{yes}}.
    nowriting = [f["t"] for f in films if f["writer_cell"] == "{{no}}"]
    assert nowriting == ["The Fisher King", "12 Monkeys",
                         "The Zero Theorem"], nowriting
    assert all(f["writer_cell"] == "{{yes}}"
               for f in films if f["year"] < 1991), \
        [(f["t"], f["writer_cell"]) for f in films if f["year"] < 1991]
    assert "La Jetée" in by_t["12 Monkeys"]["article"]["lead"], \
        by_t["12 Monkeys"]["article"]["lead"][:300]

    late = [f for f in films if f["year"] >= 2005]
    assert len(late) == 5, [f["t"] for f in late]
    assert [len(countries(f["article"])) for f in late] == [2, 2, 3, 3, 5], \
        [(f["t"], countries(f["article"])) for f in late]
    # "the only rows made across two or more countries without America"
    multinat = [f for f in films if len(countries(f["article"])) > 1 and
                not any("United States" in c for c in countries(f["article"]))]
    assert [f["t"] for f in multinat] == [f["t"] for f in late], \
        [f["t"] for f in multinat]
    assert "29" in by_t["The Man Who Killed Don Quixote"]["article"]["lead"] and \
        "development hell" in \
        by_t["The Man Who Killed Don Quixote"]["article"]["lead"], \
        by_t["The Man Who Killed Don Quixote"]["article"]["lead"][:400]
    assert "started work on the film in 1989" in \
        by_t["The Man Who Killed Don Quixote"]["article"]["lead"], \
        by_t["The Man Who Killed Don Quixote"]["article"]["lead"][:500]

    # the two films he produced as well as directed, from the table's own
    # Producer column
    produced = [f["t"] for f in films if f["produced"]]
    assert produced == ["Time Bandits",
                        "The Imaginarium of Doctor Parnassus"], produced
    # the one row whose writing credit the table qualifies rather than
    # answering yes or no
    assert by_t["The Brothers Grimm"]["writer_cell"] == \
        "{{partial|Uncredited}}", by_t["The Brothers Grimm"]["writer_cell"]
    assert "refused to credit them" in \
        by_t["The Brothers Grimm"]["article"]["lead"], \
        by_t["The Brothers Grimm"]["article"]["lead"][:600]
    assert "Ledger's final performance" in \
        by_t["The Imaginarium of Doctor Parnassus"]["article"]["lead"], \
        by_t["The Imaginarium of Doctor Parnassus"]["article"]["lead"][:900]
    zt = by_t["The Zero Theorem"]["article"]["lead"]
    assert "conflicting statements" in zt and "Orwellian triptych" in zt, zt[:400]
    assert by_t["The Zero Theorem"]["article"]["writer"] == "Pat Rushin", \
        by_t["The Zero Theorem"]["article"]["writer"]

    # ---- row notes: every one of them read out of the data above ----------
    def note_for(f):
        bits = []
        t = f["t"]
        if t == "Monty Python and the Holy Grail":
            bits.append("Co-directed with Terry Jones — a feature directing "
                        "debut for both of them")
        elif t == "Jabberwocky":
            bits.append("The first he directed alone, from the Lewis Carroll "
                        "poem")
        elif t == "Time Bandits":
            bits.append("First of the Trilogy of Imagination, and one of two "
                        "here he produced as well as directed")
        elif t == "Brazil":
            bits.append("Watch the %d-minute final cut — the version released "
                        "across Europe, the only one Criterion has ever put "
                        "out, and the one the bar measures. Universal recut "
                        "it to %d minutes for America, and a %d-minute "
                        "television version exists"
                        % (labelled["final cut"],
                           labelled["American Universal cut"],
                           labelled['"Love Conquers All" cut']))
        elif t == "The Adventures of Baron Munchausen":
            bits.append("Last of the Trilogy of Imagination")
        elif t == "The Fisher King":
            bits.append("The first he directed with no writing credit, from a "
                        "script by Richard LaGravenese")
            bits.append("The only Oscar winner of his career")
        elif t == "12 Monkeys":
            bits.append("From Chris Marker's short film La Jetée")
        elif t == "Fear and Loathing in Las Vegas":
            bits.append("From the Hunter S. Thompson book")
        elif t == "The Brothers Grimm":
            bits.append("Ehren Kruger's script; the Writers Guild refused "
                        "Gilliam and Tony Grisoni a credit for their rewrite")
        elif t == "Tideland":
            bits.append("From the Mitch Cullin novel")
        elif t == "The Imaginarium of Doctor Parnassus":
            bits.append("Heath Ledger's last performance; he died during the "
                        "shoot and three actors finished the part")
            bits.append("The other film here he produced")
        elif t == "The Zero Theorem":
            bits.append("Pat Rushin's script. Gilliam has given conflicting "
                        "answers about whether it completes a dystopian "
                        "trilogy with Brazil and 12 Monkeys")
        elif t == "The Man Who Killed Don Quixote":
            bits.append("The one he spent 29 years trying to make — the "
                        "collapsed 2000 shoot became the documentary Lost in "
                        "La Mancha")
        return join_bits(*bits)

    # ---- sections ---------------------------------------------------------
    sections = []
    for key, title, lo, hi, intro in ERAS:
        got = [f for f in films if lo <= f["year"] <= hi]
        assert got, key
        items = []
        for f in got:
            it = {"id": "tg-%d-%s" % (f["year"], slug(f["t"])),
                  "t": f["t"], "n": str(f["year"]),
                  "w": round(f["runtime"] / 60.0, 2)}
            n = note_for(f)
            if n:
                it["note"] = n
            items.append(it)
        sections.append({
            "id": key, "title": title,
            "sub": "%d–%d · %d films · %d hours"
                   % (got[0]["year"], got[-1]["year"], len(got),
                      round(sum(f["runtime"] for f in got) / 60.0)),
            "intro": intro, "items": items})
    sections[0]["open"] = True

    placed = sum(len(s["items"]) for s in sections)
    assert placed == len(films), (placed, len(films))
    for s in sections:
        assert all(a["n"] <= b["n"] for a, b in zip(s["items"], s["items"][1:])), \
            "%s is out of year order" % s["title"]
    rows = [x for s in sections for x in s["items"]]
    # every row noted: on a thirteen-row list there is no row so plain that
    # it has nothing true to say about itself
    assert all(x.get("note") for x in rows), \
        [x["id"] for x in rows if not x.get("note")]
    # a row with no `w` in a weighted list is silently worth one hour, and a
    # row at zero would mix the two kinds — neither is allowed here
    assert all(isinstance(x.get("w"), float) and x["w"] > 0 for x in rows), \
        [x["id"] for x in rows if not x.get("w")]

    mins = sum(f["runtime"] for f in films)
    hours = round(sum(x["w"] for x in rows), 2)
    assert abs(hours - mins / 60.0) < 0.2, (hours, mins / 60.0)

    # ---- the films this list shares with other lists here ------------------
    keys = {normt(f["t"]) + "|" + str(f["year"]): f["t"] for f in films}
    shared = overlaps(keys)
    assert len(shared) == 7, sorted(shared)
    by_list = {}
    for k, titles in shared.items():
        for t in titles:
            by_list.setdefault(t, []).append(keys[k])
    assert sorted(by_list) == ["Robin Williams", "The Criterion Collection"], \
        sorted(by_list)
    assert len(by_list["The Criterion Collection"]) == 7, \
        by_list["The Criterion Collection"]
    assert sorted(by_list["Robin Williams"]) == \
        ["The Adventures of Baron Munchausen", "The Fisher King"], \
        by_list["Robin Williams"]
    unpaired = [t for k, t in keys.items() if k not in shared]
    assert unpaired == ["12 Monkeys", "The Brothers Grimm", "Tideland",
                        "The Imaginarium of Doctor Parnassus",
                        "The Zero Theorem",
                        "The Man Who Killed Don Quixote"], unpaired

    order = [f["t"] for f in films]
    phrases = ["%s on %s" % (and_list(sorted(by_list[t], key=order.index)), t)
               for t in sorted(by_list, key=lambda t: (-len(by_list[t]), t))]
    sharing = ("%s. Ticking one ticks the other: film rows pair across lists "
               "by title and year, so a film watched here is watched there. "
               "Criterion numbers its rows by spine rather than year — Brazil "
               "is #51 — so all seven of those pairs are made through the "
               "year in Criterion's own note. Nothing is duplicated and no "
               "hours are counted twice, because every list totals only its "
               "own rows." % "; ".join(phrases))

    p = {
        "slug": SLUG,
        "title": "Terry Gilliam",
        "subtitle": "the directed features, in release order",
        "kind": "films",
        # A Python, which carries the name further than most directors', and
        # two films almost anyone into film can name. But the list is the
        # DIRECTING, and as a directing name he travels less far than Fincher
        # (69) or the Coens (67) — level with David Lynch, a notch over
        # Villeneuve and Kurosawa. See POPULARITY.md.
        "popularity": 64,
        "year": "1975–2018",
        "blurb": "Thirteen features in release order, Holy Grail to Don "
                 "Quixote — about %d hours. Brazil gets one row, and the row "
                 "says which of its three cuts to watch." % round(hours),
        "unit": {"one": "film", "many": "films"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        # measured in CIELAB against every accent in properties/index.json
        # when this was picked — see scratch/agent-gilliam/accent.py. The
        # obvious picks are all spoken for: the Imaginarium's stage purple IS
        # Evangelion's accent to the byte, the Python cut-out red lands 1.8
        # from Secret Wars', Munchausen's moon blue 2.7 from Friday Night
        # Lights', and Time Bandits' storybook gold 6.6 from Criterion's —
        # the list this one shares seven films with. This is the other
        # Gilliam colour: the institutional olive of Brazil's ducting and
        # paperwork, which is also the flat mustard the Python cut-outs are
        # printed in, 14.4 from its nearest neighbour against 16.6 for the
        # freest pair anywhere on the wheel.
        "accent": "#7A7A29",
        "accentDark": "#A3AB3A",
        "tiers": False,
        "notes": [
            ["One row per film, cuts and all.",
             "Brazil is the only film here that exists at more than one "
             "length, and it exists at three: the %d-minute final cut, "
             "Universal's %d-minute American recut, and a %d-minute "
             "television version. It still gets one row. A row is something "
             "to watch and tick, and nobody watches Brazil twice — a second "
             "row would either double its hours or carry no weight at all, "
             "and this list has no unweighted rows in it. So the cut lives "
             "on the row, and the row says which version to watch."
             % (labelled["final cut"], labelled["American Universal cut"],
                labelled['"Love Conquers All" cut'])],
            ["Which Brazil the bar measures, and why.",
             "The %d-minute final cut. The house rule is that a bar measures "
             "the theatrical release, and the unusual thing about this film "
             "is that there were two: the article says Gilliam's original cut "
             "\"was released in Europe and internationally by 20th Century "
             "Fox without issue\" in February 1985, and that Universal "
             "later \"agree[d] to release a modified 132-minute version\" in "
             "America that December. So the long one is a theatrical release "
             "— the first, and the one the rest of the world saw — and "
             "taking it is the ordinary rule rather than an exception to it. "
             "It is also the only version Criterion has ever released, on "
             "LaserDisc in 1996 and on 4K in 2025, which is the plainer "
             "reason the row tells you to watch it."
             % labelled["final cut"]],
            ["Bar widths are runtimes, from each film's own article.",
             "The infobox runtime field, for all thirteen, and no other "
             "source. Wikidata's runtime property covers all thirteen too, "
             "but it carries both 140 and 142 for Brazil with nothing on "
             "either statement to say which release it means, and a source "
             "that cannot answer the only hard question on the list is the "
             "wrong source for the list. Where the two disagree by more than "
             "a minute — Jabberwocky, Time Bandits and 12 Monkeys — this "
             "list keeps to the one it chose rather than becoming a blend of "
             "two."],
            ["Directing only, and features only.",
             "The credit test is a bare yes in the filmography's Director "
             "column, which is why Monty Python and the Holy Grail is here "
             "and the rest of the Python films are not: he wrote Life of "
             "Brian, The Meaning of Life, And Now for Something Completely "
             "Different and the Hollywood Bowl concert film, and animated "
             "two of them, but animating a sequence is not directing a "
             "feature. The %s short films are out as a class, The Crimson "
             "Permanent Assurance included — the sixteen-minute piece inside "
             "The Meaning of Life is a standalone work, but a standalone "
             "short: the filmography files it in its short film table, its "
             "own article calls it one, and he was nominated for the BAFTA "
             "Award for Best Short Film for it. Two of the five shorts have "
             "no published runtime at all, so a shorts section could not "
             "have been weighted either. Nor the television, the "
             "commercials, or the acting."
             % word(len(directed_shorts))],
            ["Lost in La Mancha is not here, and neither is He Dreams of "
             "Giants.",
             "Both are documentaries about Gilliam rather than by him — "
             "Keith Fulton and Louis Pepe directed both, the first about the "
             "shoot that collapsed in 2000 and the second about the one that "
             "finally worked. Neither appears anywhere on his filmography. "
             "They are named here so they do not look forgotten."],
            ["%s of these films are on other lists here."
             % word(len(shared)).capitalize(), sharing],
            "Filmography from Wikipedia's Terry Gilliam filmography, read "
            "from the table itself and cross-checked against the works his "
            "biography's lead names; runtimes and cut lengths from each "
            "film's own article, with Wikidata's runtime property kept as a "
            "check; Brazil's release history from that film's article.",
        ],
        "sections": sections,
    }

    out = prop.write(p)
    ids = [x["id"] for x in rows]
    assert len(ids) == 13, len(ids)
    print("wrote %s — %d films, %d minutes, %.2f hours"
          % (out.name, len(ids), mins, hours))
    for s in sections:
        print("   %-28s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))
    print("   Brazil measures %d min (%s) of %s"
          % (br["runtime"], BRAZIL_CUT,
             sorted(labelled.values(), reverse=True)))
    print("   shared with other lists: %d films — %s"
          % (len(shared),
             "; ".join("%s: %s" % (t, ", ".join(by_list[t])) for t in by_list)))


if __name__ == "__main__":
    main()
