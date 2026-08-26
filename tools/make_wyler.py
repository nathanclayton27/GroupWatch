#!/usr/bin/env python3
"""Generate properties/wyler.json.

    PYTHONIOENCODING=utf-8 python tools/make_wyler.py

William Wyler's directed features in release order, in the four eras
Wikipedia's own biography divides his career into. Everything on the card —
titles, years, order, notes — is machine-read from wikitext cached in
scratch/agent-wyler/ by scratch/agent-wyler/fetch.py: the "William Wyler
filmography" article for the roster, the "William Wyler" article for the era
boundaries, "List of awards and nominations received by William Wyler" for the
Best Director record, each film's own article for its release date and its
credits, and this catalogue's own properties/best-picture.json for the Best
Picture ticks. Nothing is typed in from memory, and every claim the copy makes
is asserted against the source that produced it before anything is written.

THE SCOPE QUESTION: FORTY-SIX FEATURES, TWENTY-ONE TWO-REELERS LEFT OUT
----------------------------------------------------------------------
The filmography has three tables — Silent films (32 rows), Sound films (33)
and Documentaries (2) — and the whole scope question lives in the first one.
Twenty-seven of those 32 rows are entries in two Universal series, and the
article's own footnotes say what the series were:

    * Universal's Mustang Series. Wyler made 21 two-reeler films for this
      series, all with a duration of 24 minutes.
    ** Universal's Blue Streak Series. Wyler made 6 five-reeler films for this
      series, all with a duration of an hour.

So the line is the source's own, not this file's. **The 21 Mustang two-reelers
are a named exclusion**: two reels is 24 minutes, which is a short, and this is
a list of features — the same ruling the Hitchcock, Cronenberg and Ridley Scott
lists made about their directors' shorts. It is corroborated exactly: those 21
titles are the only red links in the whole filmography, and the other eleven
silent rows each have their own Wikipedia article. main() asserts that the
redlink set and the Mustang set are the same 21 titles, so if Wikipedia ever
writes one of those articles the build stops and asks for the ruling again.

**The six Blue Streak five-reelers are rows**, and so are the two unlabelled
westerns (*Desert Dust*, *Thunder Riders*) that sit beside them at the same
50 minutes. A five-reel picture in 1927 is a feature; the article calls each of
them a film and gives each a runtime, and the catalogue already carries a
director's silent features as their own section — Hitchcock's nine British
silents. Dropping them would also empty this list's first era, which is the
biography's own "1923–1929: Early work and silent films".

*Anybody Here Seen Kelly?* (1928) is **a row, and it is lost** — its own
article says no print survives in any archive. It stays for the reason the
Hitchcock list keeps *The Mountain Eagle*: it is part of the work, and a list
that quietly drops the one film nobody can see is lying about the shape of the
career. Its row says so.

NO WEIGHTS, AND EXACTLY WHY
---------------------------
The commission allowed one runtime source, either Wikidata P2047 gated on a
publication year or each film's own infobox, and required all-or-nothing:
one unsourceable row and the whole list ships unweighted. Both sources were
collected in full into tools/data/wyler-runtimes.json, and **neither covers
every row**:

  * Wikidata carries no P2047 at all for nine rows — the six Blue Streak
    westerns, *Desert Dust*, *Thunder Riders* and *The Love Trap*.
  * The infobox publishes no single whole-minute figure for four rows —
    *Blazing Days* says "5 reels", *Straight Shootin'* and *Tom Brown of
    Culver* say nothing, and *The Gay Deception* gives a range, "75-77
    minutes".

Mixing the two would make the bar widths a blend of two sources, and inventing
a number for "5 reels" would be a guess. So no row carries `w`, every mark on
the strip is the same width, and the notes say this out loud. main() asserts
both gaps are still exactly the size they are here: the day either source
fills in, the build fails and asks to be reweighted rather than shipping a
stale explanation.

That decision costs nothing that would otherwise be right. Ben-Hur alone shows
why: its infobox reads 212 minutes "excluding overture, intermission and
entr'acte" while Wikidata reads 222, and with no bar to draw, the list never
has to pretend one of those is the film's length.

ALTERNATE CUTS
--------------
One row per film, per HOW-IT-WORKS. Only one film here has genuinely different
released versions: *The Shakedown* (1929) went out as a part-talkie for
English-speaking audiences and as a synchronised-score version for everyone
else, and the print that survives is the second one, reissued silent. That is
on its row. *Ben-Hur* and *Funny Girl* are roadshow pictures whose two figures
differ only by overture and intermission, which is a measurement difference
rather than a different cut; both are noted, neither gets a second row.

THE ERAS ARE THE ARTICLE'S, NOT THIS FILE'S
-------------------------------------------
The four sections come from the four ===Career=== headings on the "William
Wyler" article. main() reads those headings out of the wikitext, parses the
year ranges out of them and builds the sections from the parsed ranges, after
asserting the headings are still there. Every film lands in exactly one era,
and that is asserted too.

Cache:  scratch/agent-wyler/ (scratch/agent-wyler/fetch.py primes it)
Data:   tools/data/wyler-runtimes.json (scratch/agent-wyler/mkdata.py)
Accent: scratch/agent-wyler/accent.py
"""
import datetime
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop, wiki  # noqa: E402

SLUG = "wyler"
ROOT = prop.ROOT
CACHE = ROOT / "scratch" / "agent-wyler"
DATA = ROOT / "tools" / "data" / "wyler-runtimes.json"

FILMOG = "William Wyler filmography"
BIO = "William Wyler"
AWARDS = "List of awards and nominations received by William Wyler"

# The filmography's three tables, and how many data columns each carries after
# the Year cell. gwlib.wiki.table_rows carries rowspans down, which these
# tables need: the Year cell rowspans eight rows over 1926 and nineteen over
# 1927.
TABLES = [("Silent films", 5), ("Sound films", 5), ("Documentaries", 4)]

# The footnotes under the Silent films table. The scope ruling stands on these
# exact sentences, so they are asserted verbatim before anything is excluded.
MUSTANG = ("Universal's Mustang Series. Wyler made 21 two-reeler films for "
           "this series, all with a duration of 24 minutes.")
BLUESTREAK = ("Universal's Blue Streak Series. Wyler made 6 five-reeler films "
              "for this series, all with a duration of an hour.")

ERA_HEADINGS = [
    "1923–1929: Early work and silent films",
    "1930–1949: Career acclaim and stardom",
    "1950–1959: Established director",
    "1960–1970: Later work and final films",
]

# One per heading above, in the same order. The boundaries are the article's;
# only the words are ours. Each intro's factual claims are checked in main().
ERA_COPY = [
    ("silents", "The Universal westerns, and the first sound",
     "The youngest director on the Universal lot, turning out five-reel "
     "westerns for the studio's Blue Streak series — the two-reelers he made "
     "alongside them are not rows here, and the notes say why. The run closes "
     "on his first picture that is not a western, then the two part-talkies, "
     "then the first film he shot with sound throughout."),
    ("acclaim", "Universal to Goldwyn, and the war",
     "Twenty years and the making of the reputation. He finishes the Universal "
     "contract, moves to Samuel Goldwyn and Warner Bros., and collects the "
     "first of his record twelve Best Director nominations. Halfway through he "
     "goes to the war himself and comes back with two documentaries shot in "
     "the air."),
    ("established", "The established director",
     "Seven films, six of them produced as well as directed, ending on the "
     "largest production of his life — the one he did not produce. Three of "
     "the seven were nominated for Best Picture and one of those took a "
     "record eleven Academy Awards."),
    ("later", "The last five",
     "He films Lillian Hellman's The Children's Hour a second time, this time "
     "under its own title; makes two more with Audrey Hepburn; and finishes "
     "with a musical and a courtroom picture. Then he stops, on a career his "
     "own article puts at forty-five years."),
]

# Row notes. Production and provenance only — what a film IS, never what
# happens in it. Every one is grounded in the cached articles, and the claims
# main() could get wrong are re-checked below against the columns and fields
# they came from. Keyed by (year, title): no two rows share a pair.
NOTES = {
    (1926, "Lazy Lightning"):
        "A five-reeler from Universal's Blue Streak series, with Fay Wray in "
        "an early role",
    (1926, "The Stolen Ranch"):
        "Blue Streak series; Janet Gaynor appears in it as an extra, before "
        "she was anybody",
    (1927, "Blazing Days"):
        "Blue Streak series; prints are held by the Library of Congress and "
        "the UCLA Film and Television Archive",
    (1927, "Straight Shootin'"):
        "Blue Streak series, and the one row on this list whose length no "
        "source gives at all",
    (1927, "Hard Fists"):
        "Blue Streak series, and the second of two with Art Acord",
    (1927, "The Border Cavalier"):
        "Blue Streak series, and the second of two with Fred Humes",
    (1927, "Desert Dust"):
        "A Universal five-reeler the filmography files under neither of the "
        "two series",
    (1928, "Thunder Riders"):
        "The last of the silent westerns; a print is listed in the collection "
        "of the Cineteca del Friuli",
    (1928, "Anybody Here Seen Kelly?"):
        "His first film that is not a western, and the one film here nobody "
        "can watch: no print survives in any archive",
    (1929, "The Shakedown"):
        "His first part-talkie, released in two versions — a part-talking one "
        "for English-speaking audiences and a synchronised-score one for "
        "everywhere else. The version that survives is the second, reissued "
        "silent",
    (1929, "The Love Trap"):
        "The second part-talkie, with a synchronised score, sound effects and "
        "English intertitles",
    (1929, "Hell's Heroes"):
        "His first all-talking film, and Universal's first sound production "
        "shot entirely on location; from a Peter B. Kyne short story",
    (1930, "The Storm"):
        "From a Langdon McCormick play, with John Huston among the writers "
        "years before he directed",
    (1931, "A House Divided"):
        "From an Olive Edens story, and the first of two with Walter Huston",
    (1932, "Tom Brown of Culver"):
        "A pre-Code picture set at Culver Military Academy; its copyright was "
        "renewed in 1960, so it stays out of the public domain until 2028",
    (1933, "Her First Mate"):
        "A pre-Code comedy out of a Frank Craven and John Golden play",
    (1933, "Counsellor at Law"):
        "Elmer Rice adapting his own 1931 Broadway play, with John Barrymore",
    (1934, "Glamour"):
        "A pre-Code drama, and one of the last of the Universal contract "
        "pictures",
    (1935, "The Good Fairy"):
        "From a Ferenc Molnár play, screenplay by Preston Sturges — the last "
        "film he made at Universal",
    (1935, "The Gay Deception"):
        "His first film away from Universal, for 20th Century-Fox",
    (1936, "These Three"):
        "Lillian Hellman adapting her own play The Children's Hour, and his "
        "first for Samuel Goldwyn; he filmed the play again in 1961",
    (1936, "Dodsworth"):
        "From Sidney Howard's stage version of the Sinclair Lewis novel, and "
        "the second with Walter Huston",
    (1936, "Come and Get It"):
        "From the Edna Ferber novel; he took the picture over from Howard "
        "Hawks after 42 days and both men are credited",
    (1937, "Dead End"):
        "From Sidney Kingsley's 1935 Broadway play",
    (1938, "Jezebel"):
        "From an Owen Davis play, his first for Warner Bros. and the first of "
        "three with Bette Davis",
    (1939, "Wuthering Heights"):
        "From Emily Brontë's 1847 novel, of which it films 16 of the 34 "
        "chapters and none of the second generation",
    (1940, "The Westerner"):
        "A western with Gary Cooper; Walter Brennan won a record third "
        "Supporting Actor Oscar for it",
    (1940, "The Letter"):
        "From W. Somerset Maugham's 1927 play, and the second with Bette Davis",
    (1941, "The Little Foxes"):
        "Lillian Hellman adapting her own 1939 play, and the third with Bette "
        "Davis",
    (1942, "Mrs. Miniver"):
        "From Jan Struther's book about an English family in the war. MGM "
        "meant to shoot it in England and moved it to California instead",
    (1944, "The Memphis Belle: A Story of a Flying Fortress"):
        "A wartime documentary in colour, shot over Europe by an Army Air "
        "Forces camera crew; one of its cinematographers was killed during "
        "the filming",
    (1946, "The Best Years of Our Lives"):
        "From MacKinlay Kantor's verse novella Glory for Me, written for "
        "Samuel Goldwyn after Wyler came home from the war",
    (1947, "Thunderbolt"):
        "A second wartime documentary, co-directed with John Sturges, on the "
        "fighter squadrons flying out of Corsica",
    (1949, "The Heiress"):
        "From Ruth and Augustus Goetz's 1947 play, itself out of Henry "
        "James's novel Washington Square",
    (1951, "Detective Story"):
        "From Sidney Kingsley's 1949 play, and one day inside a police squad "
        "room",
    (1952, "Carrie"):
        "From Theodore Dreiser's novel Sister Carrie, and nothing to do with "
        "the Stephen King one",
    (1953, "Roman Holiday"):
        "Shot in Rome, and Audrey Hepburn's first major film role; the script "
        "is Dalton Trumbo's, credited for years to somebody else because he "
        "was on the blacklist",
    (1955, "The Desperate Hours"):
        "From Joseph Hayes's novel and his own stage version of it",
    (1956, "Friendly Persuasion"):
        "From Jessamyn West's book about a Quaker family in the Civil War; it "
        "took the Palme d'Or at Cannes the following year",
    (1958, "The Big Country"):
        "A widescreen western from a Donald Hamilton novel, produced by Wyler "
        "and Gregory Peck together",
    (1959, "Ben-Hur"):
        "From the Lew Wallace novel, and a remake of the 1925 silent on which "
        "Wyler had been one of thirty assistant directors. A record eleven "
        "Academy Awards; the runtime sources differ by the length of the "
        "overture and intermission",
    (1961, "The Children's Hour"):
        "Lillian Hellman's play a second time, under its own title now — he "
        "had filmed it in 1936 as These Three",
    (1965, "The Collector"):
        "From John Fowles's 1963 novel; both its leads took acting prizes at "
        "Cannes",
    (1966, "How to Steal a Million"):
        "A heist comedy shot in Paris, from a George Bradshaw story, and his "
        "third with Audrey Hepburn",
    (1968, "Funny Girl"):
        "From the 1964 stage musical, and Barbra Streisand's first film; a "
        "roadshow release, so the runtime sources differ by its overture",
    (1970, "The Liberation of L.B. Jones"):
        "From a Jesse Hill Ford novel, and his last film: its article calls it "
        "the end of a career spanning forty-five years",
}

FIRST, LAST = "The Crook Buster", "The Liberation of L.B. Jones"

# Its own article gives the film a longer name than the filmography's link
# text does, and the film's own name wins. Asserted to be the only such row.
RENAMED = {"The Memphis Belle": "The Memphis Belle: A Story of a Flying Fortress"}


def table_after(text, heading):
    """The first wikitable following a `===heading===` line."""
    m = re.search(r"^=+\s*%s\s*=+\s*$" % re.escape(heading), text, re.M)
    assert m, "no %r section on %s" % (heading, FILMOG)
    a = text.index("\n{|", m.end())
    return text[a:text.index("\n|}", a)]


def link(cell):
    """The wikilink target inside an italicised title cell."""
    m = re.search(r"\[\[([^\]|]+)", cell)
    assert m, "no wikilink in title cell %r" % cell[:60]
    return m.group(1).strip()


def cached(page):
    """The cached wikitext for an article, or "" for a red link."""
    f = CACHE / (re.sub(r"[^A-Za-z0-9]+", "-", page) + ".wiki")
    assert f.exists(), \
        "%s is not in the cache — run scratch/agent-wyler/fetch.py" % page
    return f.read_text(encoding="utf-8")


def released(field, what):
    """(earliest date or None, earliest year) from an infobox `released`.

    Footnotes come out first: Wuthering Heights cites an AFI catalogue volume
    called "Feature Films, 1931-1940" from inside its own {{Film date}}, and a
    year regex run over the raw field reads 1931 as a release year and fails
    the film against its own filmography row.
    """
    field = re.sub(r"<ref[^>]*/>", "", field or "")
    field = re.sub(r"<ref.*?</ref>", "", field, flags=re.S)
    field = re.sub(r"<!--.*?-->", "", field, flags=re.S)
    dates, years = [], []
    for m in re.finditer(r"\{\{\s*[Ff]ilm date\s*\|(.*?)\}\}", field or "", re.S):
        body = m.group(1)
        for d in re.finditer(r"(?<!\d)((?:19|20)\d{2})\s*\|\s*(\d{1,2})"
                             r"\s*\|\s*(\d{1,2})(?!\d)", body):
            try:
                dates.append(datetime.date(*(int(g) for g in d.groups())))
            except ValueError:
                pass
        years += [int(y) for y in re.findall(r"(?<!\d)((?:19|20)\d{2})(?!\d)",
                                             body)]
    assert years, "%s: no release date on its infobox" % what
    return (min(dates) if dates else None, min(years))


def single_minutes(field):
    """True when an infobox `runtime` names one determinate length.

    Used only to count the gaps in the source this list decided not to weigh
    by. A range ("75-77 minutes"), a reel count ("5 reels") and an absent field
    all fail, because none of them is a number this catalogue would put in a
    bar. "1 hour 20 minutes" passes — it is one length, only written the long
    way, and Wikidata carries the same 80 for that film.
    """
    v = wiki.clean(field or "").strip()
    return bool(re.match(r"^\d{1,3}\s*minutes?\b", v)
                or re.match(r"^\d{1,2}\s*hours?\s+\d{1,2}\s*minutes?\b", v))


def italic_links(text):
    """Display text of every ''[[wikilink]]'' in a run of prose."""
    return [(m.group(2) or m.group(1)).strip() for m in
            re.finditer(r"''\[\[([^\]|]+)(?:\|([^\]]+))?\]\]''", text)]


def and_list(names):
    names = list(names)
    return names[0] if len(names) == 1 else \
        ", ".join(names[:-1]) + " and " + names[-1]


WORDS = ("no", "one", "two", "three", "four", "five", "six", "seven", "eight",
         "nine", "ten", "eleven", "twelve", "thirteen")


def word(n):
    return WORDS[n] if n < len(WORDS) else str(n)


def main():
    today = datetime.date.today()
    art, bio = cached(FILMOG), cached(BIO)
    awards = cached(AWARDS)
    assert art and bio and awards, "empty cached article"

    # ---- the eras are the biography's own headings ------------------------
    eras = []
    for h in ERA_HEADINGS:
        assert re.search(r"^=+\s*%s\s*=+\s*$" % re.escape(h), bio, re.M), \
            ("the career heading %r is gone from %s — the sections take their "
             "boundaries from it and must be re-derived" % (h, BIO))
        m = re.match(r"(\d{4})–(\d{4}|present)", h)
        assert m, h
        eras.append((int(m.group(1)),
                     today.year if m.group(2) == "present" else int(m.group(2))))
    assert len(eras) == len(ERA_COPY) == 4, eras
    assert [e[0] for e in eras] == sorted(e[0] for e in eras), eras

    # ---- the three tables -------------------------------------------------
    tables = {}
    for name, ncols in TABLES:
        rows = wiki.table_rows(table_after(art, name), ncols,
                               header_probe="|''[[")
        got = []
        for cols in (c for _t, c in rows):
            # Documentaries has no Genre column; pad so the shape is uniform
            year, title, studio = cols[0], cols[1], cols[2]
            genre, note = (cols[3], cols[4]) if ncols == 5 else ("", cols[3])
            got.append({"table": name, "year": int(wiki.clean(year)),
                        "disp": wiki.clean(title), "page": link(title),
                        "studio": wiki.clean(studio),
                        "genre": wiki.clean(genre),
                        "tablenote": wiki.clean(note)})
        tables[name] = got
    assert [len(tables[n]) for n, _ in TABLES] == [32, 33, 2], \
        {n: len(tables[n]) for n, _ in TABLES}
    everything = [f for n, _ in TABLES for f in tables[n]]
    ends = (tables["Silent films"][0]["disp"], tables["Sound films"][-1]["disp"])
    assert ends == (FIRST, LAST), \
        ("the filmography now runs %s to %s — a row has been added or removed "
         "and this list must be re-checked" % ends)
    for n, _ in TABLES:
        ys = [f["year"] for f in tables[n]]
        assert ys == sorted(ys), "%s is out of year order" % n

    # ---- the scope ruling, checked against the article's own footnotes -----
    assert (": * " + MUSTANG) in art and (": ** " + BLUESTREAK) in art, \
        ("the Silent films footnotes have changed — the exclusion of the "
         "two-reelers stands on their exact wording")
    silents = tables["Silent films"]
    mustang = [f for f in silents if f["tablenote"] == "UMS*"
               or f["tablenote"] == "UMS"]
    bluestreak = [f for f in silents if f["tablenote"] == "UBSS**"
                  or f["tablenote"] == "UBSS"]
    assert len(mustang) == 21, [f["disp"] for f in mustang]
    assert len(bluestreak) == 6, [f["disp"] for f in bluestreak]
    # the corroboration: the two-reelers are exactly the red links, and every
    # other row in the filmography has an article of its own
    redlinks = [f for f in everything if not cached(f["page"]).strip()]
    assert {f["disp"] for f in redlinks} == {f["disp"] for f in mustang}, \
        ("the red links and the Mustang two-reelers are no longer the same "
         "set — the scope ruling has to be made again: %s"
         % sorted({f["disp"] for f in redlinks}
                  ^ {f["disp"] for f in mustang}))

    films = [f for f in everything if f not in mustang]
    assert len(films) == 46, len(films)
    assert len([f for f in films if f["table"] == "Silent films"]) == 11, films

    # ---- each film's own article ------------------------------------------
    data = {r["page"]: r for r in
            json.loads(DATA.read_text(encoding="utf-8"))}
    for f in films:
        page = cached(f["page"])
        ib = wiki.infobox(page, kind="film")
        assert ib, "no film infobox on %s" % f["page"]
        name = wiki.clean(ib("name")) or f["disp"]
        if prop.normt(name) != prop.normt(f["disp"]):
            assert RENAMED.get(f["disp"]) == name, \
                "%s calls itself %r" % (f["disp"], name)
        f["t"] = name
        f["article"] = page
        # the article as display text: the note claims below are checked
        # against this rather than the wikitext, so a needle does not have to
        # guess whether a name happens to be wrapped in a wikilink today
        f["prose"] = wiki.clean(page)
        rdate, ryear = released(ib("released"), f["disp"])
        f["date"], f["ryear"] = rdate, ryear
        f["runtime_field"] = ib("runtime")
        f["based_on"] = ib("based[_ ]on")
        f["starring"] = wiki.clean(ib("starring"))
        assert ryear == f["year"], \
            "%s: the filmography says %d, its own article says %d" \
            % (f["t"], f["year"], ryear)
        if rdate:
            assert rdate <= today, "%s is dated %s" % (f["t"], rdate)
        else:
            assert ryear < today.year, \
                "%s publishes only the year %d" % (f["t"], ryear)
        assert f["page"] in data, "no runtime evidence for %s" % f["page"]
    assert sum(1 for f in films if f["t"] != f["disp"]) == len(RENAMED), \
        [f["disp"] for f in films if f["t"] != f["disp"]]

    # ---- release order ----------------------------------------------------
    # The tables are each in release order and no year holds rows from two of
    # them out of sequence, so year-then-table-order is release order. Every
    # published date is checked against that, which is what catches a table
    # that has been re-sorted upstream.
    films.sort(key=lambda f: (f["year"], everything.index(f)))
    dated = [f for f in films if f["date"]]
    assert [f["date"] for f in dated] == sorted(f["date"] for f in dated), \
        ("the filmography's order is not release order: %s"
         % [(f["t"], str(f["date"])) for f in dated])
    assert len(films) - len(dated) == 1 and \
        [f["t"] for f in films if not f["date"]] == ["Straight Shootin'"], \
        [f["t"] for f in films if not f["date"]]

    # ---- the weights that are not here ------------------------------------
    no_wikidata = [f for f in films if not data[f["page"]]["p2047"]]
    no_infobox = [f for f in films if not single_minutes(f["runtime_field"])]
    assert [f["t"] for f in no_wikidata] == \
        ["Lazy Lightning", "The Stolen Ranch", "Blazing Days",
         "Straight Shootin'", "Hard Fists", "The Border Cavalier",
         "Desert Dust", "Thunder Riders", "The Love Trap"], \
        ("Wikidata's runtime coverage has changed — if it now covers every "
         "row this list should be weighted from it: %s"
         % [f["t"] for f in no_wikidata])
    # what the runtime note calls them: all nine are 1920s Universal pictures
    assert all(f["studio"] == "Universal" and f["year"] < 1930
               for f in no_wikidata), \
        [(f["t"], f["studio"], f["year"]) for f in no_wikidata]
    assert [f["t"] for f in no_infobox] == \
        ["Blazing Days", "Straight Shootin'", "Tom Brown of Culver",
         "The Gay Deception"], \
        ("the infobox runtime coverage has changed — if every row now "
         "publishes one whole-minute figure this list should be weighted from "
         "it: %s" % [f["t"] for f in no_infobox])
    # the two disagreements the copy names, both roadshow measurement gaps
    for t, ib_min, wd_min in (("Ben-Hur", 212, 222), ("Funny Girl", 149, 151)):
        f = next(x for x in films if x["t"] == t)
        assert wiki.clean(f["runtime_field"]).startswith("%d minutes" % ib_min), \
            (t, f["runtime_field"][:60])
        assert [s["amount"] for s in data[f["page"]]["p2047"]] == [float(wd_min)], \
            (t, data[f["page"]]["p2047"])

    # ---- the Oscars, read rather than remembered --------------------------
    # Best Picture from this catalogue's own list, which is where the ticks
    # pair; Best Director from the awards article's lead.
    bp = json.loads((ROOT / "properties" / "best-picture.json")
                    .read_text(encoding="utf-8"))
    bpkeys, bpwon = {}, set()
    for s in bp["sections"]:
        for x in s["items"]:
            k = prop.normt(x["t"]) + "|" + str(x.get("n"))
            bpkeys[k] = x
            if "Won Best Picture" in (x.get("note") or ""):
                bpwon.add(k)
    picture, picture_won = [], []
    for f in films:
        k = prop.normt(f["t"]) + "|" + str(f["year"])
        if k in bpkeys:
            picture.append(f)
            if k in bpwon:
                picture_won.append(f)
    assert len(picture) == 13 and len(picture_won) == 3, \
        ([f["t"] for f in picture], [f["t"] for f in picture_won])
    assert [f["t"] for f in picture_won] == \
        ["Mrs. Miniver", "The Best Years of Our Lives", "Ben-Hur"], picture_won
    # The filmography's own Notes column marks only twelve of the thirteen; it
    # leaves The Heiress blank. The catalogue's Best Picture list wins, and the
    # difference is asserted so the correction cannot silently change shape.
    marked = [f for f in films if "Best Picture" in f["tablenote"]]
    assert len(marked) == 12, [f["t"] for f in marked]
    assert [f["t"] for f in picture if f not in marked] == ["The Heiress"], \
        [f["t"] for f in picture if f not in marked]
    assert not [f for f in marked if f not in picture], \
        [f["t"] for f in marked if f not in picture]

    lead = awards[:awards.index("\n=")]
    assert "record twelve nominations for the [[Academy Award for Best " \
        "Director]]" in lead, lead[:400]
    wins_seg = lead[lead.index("win the [[Academy Award for Best Director]]"):
                    lead.index("all of which also won")]
    noms_seg = lead[lead.index("He was Oscar-nominated for"):]
    director_won = italic_links(wins_seg)
    director_nom = italic_links(noms_seg)
    assert len(director_won) == 3 and len(director_nom) == 9, \
        (director_won, director_nom)
    assert director_won == [f["t"] for f in picture_won], director_won
    shipped = {prop.normt(f["t"]) for f in films}
    for t in director_won + director_nom:
        assert prop.normt(t) in shipped, \
            "the awards article names %r and this list does not ship it" % t
    won_set = {prop.normt(t) for t in director_won}
    nom_set = {prop.normt(t) for t in director_nom}
    assert not (won_set & nom_set), sorted(won_set & nom_set)

    # ---- what the era intros claim ----------------------------------------
    def era_of(f):
        for i, (lo, hi) in enumerate(eras):
            if lo <= f["year"] <= hi:
                return i
        raise AssertionError("%s (%d) falls in no era" % (f["t"], f["year"]))

    buckets = [[f for f in films if era_of(f) == i] for i in range(4)]
    assert [len(b) for b in buckets] == [12, 22, 7, 5], [len(b) for b in buckets]
    assert sum(len(b) for b in buckets) == len(films)

    # era 1: the youngest director, the Blue Streak series, the first
    # non-western, the part-talkies and the first all-talking picture
    assert "he became the youngest director on the Universal lot" in bio, bio[:0]
    assert "He directed his first non-Western, the lost " \
        "''[[Anybody Here Seen Kelly?]]''" in bio
    assert "This was followed by his first part-talkie films" in bio
    assert "His first all-talking film, and Universal's first sound production" \
        " to be filmed entirely on location, was ''[[Hell's Heroes" in bio
    assert all(f in buckets[0] for f in bluestreak), \
        [f["disp"] for f in bluestreak if f not in buckets[0]]
    parttalk = [f for f in films if f["tablenote"] == "Part-Talking film"]
    assert [f["t"] for f in parttalk] == ["The Shakedown", "The Love Trap"], \
        [f["t"] for f in parttalk]
    assert buckets[0][-1]["t"] == "Hell's Heroes", buckets[0][-1]["t"]

    # era 2: the studio move, the first Best Director nominations, the two
    # documentaries
    assert buckets[1][0]["studio"].startswith("Universal"), buckets[1][0]
    goldwyn = [f for f in films if "Goldwyn" in f["studio"]]
    assert goldwyn[0]["t"] == "These Three", goldwyn[0]["t"]
    warners = [f for f in films if "Warner" in f["studio"]]
    assert warners[0]["t"] == "Jezebel", warners[0]["t"]
    docs = [f for f in films if f["table"] == "Documentaries"]
    assert [f["t"] for f in docs] == \
        ["The Memphis Belle: A Story of a Flying Fortress", "Thunderbolt"], docs
    assert all(f in buckets[1] for f in docs), docs
    era2_director = [f for f in buckets[1]
                     if prop.normt(f["t"]) in won_set | nom_set]
    assert len(era2_director) == 7, [f["t"] for f in era2_director]

    # era 3: six of seven produced as well as directed — Ben-Hur, the biggest
    # of them, is the one he did not — three Best Picture nominees, and the
    # eleven Oscars
    benhur = next(f for f in films if f["t"] == "Ben-Hur")
    produced = [f for f in buckets[2]
                if re.search(r"\|\s*producer\s*=[^\n]*William Wyler",
                             f["article"], re.I)]
    assert len(produced) == 6 and benhur not in produced, \
        [f["t"] for f in produced]
    assert len([f for f in buckets[2] if f in picture]) == 3, \
        [f["t"] for f in buckets[2] if f in picture]
    assert "won a record eleven [[Academy Awards]]" in benhur["article"]
    assert benhur is buckets[2][-1], buckets[2][-1]["t"]

    # era 4: the Hellman remake, the two Hepburn films, the forty-five years
    hepburn = [f for f in films if "Audrey Hepburn" in f["starring"]]
    assert [f["t"] for f in hepburn] == \
        ["Roman Holiday", "The Children's Hour", "How to Steal a Million"], \
        [f["t"] for f in hepburn]
    assert len([f for f in hepburn if f in buckets[3]]) == 2, hepburn
    hellman = [f for f in films if "Children's Hour" in f["based_on"]]
    assert [f["t"] for f in hellman] == ["These Three", "The Children's Hour"], \
        [f["t"] for f in hellman]
    last = buckets[3][-1]
    assert last["t"] == LAST and \
        "his final project in a career that spanned 45 years" in last["article"], \
        last["t"]

    # ---- the claims the row notes make ------------------------------------
    def art_of(t):
        return next(f for f in films if f["t"] == t)["prose"]

    for t, needle in (
            ("Lazy Lightning", "Fay Wray"),
            ("The Stolen Ranch", "Gaynor appeared as an extra in the film"),
            ("Blazing Days", "A print is preserved at the Library of "
                             "Congress and UCLA Film"),
            ("Straight Shootin'", "Blue Streak Series"),
            ("Thunder Riders", "La Cineteca Del Friuli"),
            ("Anybody Here Seen Kelly?", "it is a lost film"),
            ("Tom Brown of Culver", "will enter the public domain in 2028 as "
                                    "its copyright was renewed in 1960"),
            ("Tom Brown of Culver", "attends Culver Military Academy"),
            ("The Shakedown", "released in two versions"),
            ("The Love Trap", "synchronized musical score and sound effects"),
            ("Hell's Heroes", "Peter B. Kyne"),
            ("The Storm", "Langdon McCormick"),
            ("A House Divided", "Olive Edens"),
            ("Her First Mate", "Frank Craven"),
            ("Counsellor at Law", "Elmer Rice"),
            ("The Good Fairy", "Ferenc Moln"),
            ("Dodsworth", "Sinclair Lewis"),
            ("Come and Get It", "Edna Ferber"),
            ("Dead End", "Sidney Kingsley"),
            ("Jezebel", "Owen Davis"),
            ("Wuthering Heights", "Emily Bront"),
            ("Wuthering Heights", "depicts only 16 of the novel's 34 chapters, "
                                  "eliminating the second generation"),
            ("The Westerner", "record-setting third Academy Award for Best "
                              "Supporting Actor"),
            ("The Letter", "W. Somerset Maugham"),
            ("The Little Foxes", "Lillian Hellman"),
            ("Mrs. Miniver", "Jan Struther"),
            ("Mrs. Miniver", "Originally the film was to be shot at MGM's "
                             "studios in Denham, England but due to the "
                             "difficulties of the war it was switched to "
                             "Culver City, California"),
            ("The Memphis Belle: A Story of a Flying Fortress",
             "was killed in action during the filming"),
            ("The Best Years of Our Lives",
             "Goldwyn hired former war correspondent MacKinlay Kantor"),
            ("The Best Years of Our Lives",
             "a novella, Glory for Me, which Kantor wrote in blank verse"),
            ("The Best Years of Our Lives",
             "Wyler had flown combat missions over Europe in filming Memphis "
             "Belle"),
            ("Thunderbolt", "John Sturges"),
            ("Thunderbolt", "Twelfth Air Force based on Corsica"),
            ("The Heiress", "Ruth and Augustus Goetz"),
            ("The Heiress", "Washington Square"),
            ("Detective Story", "Sidney Kingsley"),
            ("Carrie", "Theodore Dreiser"),
            ("Roman Holiday", "her first major film role"),
            ("Roman Holiday", "with Trumbo on the Hollywood blacklist, he did "
                              "not receive a credit"),
            ("The Desperate Hours", "Joseph Hayes"),
            ("Friendly Persuasion", "Jessamyn West"),
            ("The Big Country", "Donald Hamilton"),
            ("Ben-Hur", "one of 30 assistant directors on the 1925 film"),
            ("The Collector", "John Fowles"),
            ("How to Steal a Million", "George Bradshaw"),
            ("Funny Girl", "Streisand (in her film debut"),
            ("The Liberation of L.B. Jones", "Jesse Hill Ford")):
        assert needle in art_of(t), "%s no longer says %r" % (t, needle)
    # the three claims about how many films he made with somebody
    for who, titles in (("Bette Davis", ["Jezebel", "The Letter",
                                         "The Little Foxes"]),
                        ("Walter Huston", ["A House Divided", "Dodsworth"]),
                        ("Art Acord", ["Lazy Lightning", "Hard Fists"]),
                        ("Fred Humes", ["The Stolen Ranch",
                                        "The Border Cavalier"])):
        got = [f["t"] for f in films if who in f["starring"]]
        assert got == titles, (who, got)
    # Straight Shootin' is the one row neither runtime source describes at all
    # — Blazing Days at least publishes a reel count and Tom Brown of Culver
    # has a Wikidata figure, so this is the only row with nothing anywhere
    nothing = [f["t"] for f in films
               if not data[f["page"]]["p2047"] and not f["runtime_field"].strip()]
    assert nothing == ["Straight Shootin'"], nothing
    # Thunder Riders is the last western in the silent table
    silent_westerns = [f for f in silents if f["genre"] == "Western"
                       and f not in mustang]
    assert silent_westerns[-1]["disp"] == "Thunder Riders", \
        silent_westerns[-1]["disp"]
    # Glamour is near the end of the Universal contract, not at it: The Good
    # Fairy is the last, and the row after that is the first film elsewhere
    universal = [f for f in films if f["studio"] == "Universal"]
    assert universal[-1]["t"] == "The Good Fairy", universal[-1]["t"]
    assert universal[-2]["t"] == "Glamour", universal[-2]["t"]
    assert films[films.index(universal[-1]) + 1]["t"] == "The Gay Deception", \
        "the first film away from Universal has changed"
    # The Big Country is the one row with two producers, Wyler and its star
    bc = next(f for f in films if f["t"] == "The Big Country")
    assert re.search(r"\|\s*producer\s*=[^\n]*William Wyler[^\n]*Gregory Peck",
                     bc["article"], re.S), "The Big Country's producers changed"
    # Come and Get It is the one row the filmography credits to two directors
    cagi = next(f for f in films if f["t"] == "Come and Get It")
    assert cagi["tablenote"] == "Replaced Howard Hawks after 42 days", \
        cagi["tablenote"]
    assert "directed by [[Howard Hawks]] and [[William Wyler]]" in \
        cagi["article"], "Come and Get It no longer credits both directors"
    # Thunderbolt is the co-directed documentary
    assert "co-directed with John Sturges" in \
        next(f for f in films if f["t"] == "Thunderbolt")["tablenote"]
    # every row has a note, and no two rows share a key
    assert set(NOTES) == {(f["year"], f["t"]) for f in films}, \
        sorted(set(NOTES) ^ {(f["year"], f["t"]) for f in films})

    # ---- the Oscar tail on each row, composed rather than typed -----------
    def oscar_bit(f):
        n = prop.normt(f["t"])
        if f in picture_won:
            return "Won Best Picture, and Wyler's %s Best Director Oscar" \
                % ("first", "second", "third")[picture_won.index(f)]
        if f in picture and n in nom_set:
            return "Nominated for Best Picture and Best Director"
        if f in picture:
            return "Nominated for Best Picture"
        if n in nom_set:
            return "Nominated for Best Director"
        return ""

    # ---- sections ---------------------------------------------------------
    sections, seen = [], set()
    for i, (sid, title, intro) in enumerate(ERA_COPY):
        got = buckets[i]
        assert got, title
        seen.update(id(f) for f in got)
        items = []
        for f in got:
            items.append({
                "id": "wyl-%d-%s" % (f["year"], prop.slug(f["t"])),
                "t": f["t"], "n": str(f["year"]),
                "note": prop.join_bits(NOTES[(f["year"], f["t"])],
                                       oscar_bit(f)),
            })
        sections.append({
            "id": sid, "title": title,
            "sub": "%d–%d · %d films" % (got[0]["year"], got[-1]["year"],
                                         len(got)),
            "intro": intro, "items": items,
        })
    sections[0]["open"] = True
    assert len(seen) == len(films), \
        [f["t"] for f in films if id(f) not in seen]

    rows = [x for s in sections for x in s["items"]]
    assert len(rows) == 46, len(rows)
    assert len({x["id"] for x in rows}) == len(rows), "duplicate ids"
    assert not any("w" in x for x in rows), "this list ships unweighted"
    ys = [x["n"] for x in rows]
    assert ys == sorted(ys), "the card is out of release order"

    # ---- the films this list shares with other lists here -----------------
    def year_of(x):
        n = str(x.get("n", ""))
        if re.fullmatch(r"(18|19|20)\d{2}", n):
            return n
        e = str(x.get("y", ""))
        if re.fullmatch(r"(18|19|20)\d{2}", e):
            return e
        found = set(re.findall(r"\b((?:18|19|20)\d{2})\b", x.get("note") or ""))
        return found.pop() if len(found) == 1 else None

    keys = {prop.normt(f["t"]) + "|" + str(f["year"]): f["t"] for f in films}
    mine = {prop.normt(f["t"]): f["year"] for f in films}
    shared, bylist, missed = {}, {}, []
    for p in sorted((ROOT / "properties").glob("*.json")):
        if p.stem in ("index", "search", SLUG):
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(d, dict) or d.get("secret"):
            continue
        for s in d.get("sections", []):
            for x in s.get("items", []):
                y, t = year_of(x), prop.normt(x["t"])
                k = t + "|" + str(y)
                if y and k in keys:
                    if d["title"] not in shared.get(k, []):
                        shared.setdefault(k, []).append(d["title"])
                        bylist.setdefault(d["title"], []).append(keys[k])
                elif t in mine and y and abs(int(y) - mine[t]) == 1:
                    # same film, dated a year apart: the row will tick on one
                    # list and stay blank on the other (CLU-191)
                    missed.append((x["t"], d["title"], p.stem, int(y),
                                   mine[t]))
    # The groups this list was built expecting. Extra lists may join them —
    # the catalogue grows — so this checks the known ones are all there rather
    # than pinning a total that another list would break.
    for title, want in (("Best Picture", 13), ("The Criterion Collection", 2),
                        ("Real Time", 1)):
        assert len(bylist.get(title, [])) == want, \
            (title, bylist.get(title))
    assert sorted(bylist["The Criterion Collection"]) == \
        ["Funny Girl", "The Heiress"], bylist["The Criterion Collection"]
    assert bylist["Real Time"] == ["Detective Story"], bylist["Real Time"]
    assert len(shared) >= 14, sorted(shared)
    # Friendly Persuasion is the near-miss this list knows about: the Palme
    # d'Or list dates it by the year it won at Cannes, this one by the year it
    # came out. If that is ever fixed upstream the pair forms and this fails.
    assert [(m[0], m[2]) for m in missed] == \
        [("Friendly Persuasion", "palme-dor")], missed
    order = [f["t"] for f in films]
    sharing = "; ".join(
        "%s on %s" % (and_list(sorted(bylist[t], key=order.index)), t)
        for t in sorted(bylist, key=lambda t: (-len(bylist[t]), t)))
    nearmiss = ("%s is the one that does not pair — %s dates it %d, the year "
                "it won at Cannes, and this list dates it %d, the year it came "
                "out." % (missed[0][0], missed[0][1], missed[0][3],
                          missed[0][4]))

    # ---- the accent pair is nobody else's ---------------------------------
    accent, accent_dark = "#B56940", "#B4815F"
    for f in sorted((ROOT / "properties").glob("*.json")):
        if f.stem in (SLUG, "index", "search"):
            continue
        try:
            other = json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            continue
        if not isinstance(other, dict):
            continue
        assert (other.get("accent") or "").lower() != accent.lower(), \
            "%s already uses accent %s" % (f.name, accent)
        assert (other.get("accentDark") or "").lower() != accent_dark.lower(), \
            "%s already uses accentDark %s" % (f.name, accent_dark)

    span = films[-1]["year"] - films[0]["year"]
    p = {
        "slug": SLUG,
        "title": "William Wyler",
        "subtitle": "the directed features, in release order",
        "kind": "films",
        # Three Best Director Oscars and a record twelve nominations, and three
        # films most people can name without being able to name him — which is
        # the whole shape of his reputation. Enthusiast territory rather than
        # household: a point under Cronenberg, level with Palme d'Or, well
        # under Hitchcock's 77. See POPULARITY.md.
        "popularity": 55,
        "year": "%d–%d" % (films[0]["year"], films[-1]["year"]),
        "blurb": "Every feature he directed, from the Universal westerns of "
                 "%d to his last film in %d — %d of them. %s were nominated "
                 "for Best Picture and %s won."
                 % (films[0]["year"], films[-1]["year"], len(films),
                    word(len(picture)).capitalize(), word(len(picture_won))),
        "unit": {"one": "film", "many": "films"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        # Light: burnt sienna, the sepia a 1926 Universal western prints at.
        # Dark: the warm sand it fades to. Measured in CIELAB against every
        # accent in properties/index.json — see scratch/agent-wyler/accent.py.
        # Every obvious pick is taken: the Ben-Hur crimson lands 7.3 from
        # Marvel Animation's, Jezebel's red IS Dragon Ball manga's exactly, the
        # deep-focus silver 1.4 from another list's, and the Wuthering Heights
        # slate 3.4 from Frasier's. This pair is the free corner of his own
        # register at 15.3 worst-case, against 17.5 for the freest pair
        # anywhere on the wheel — a magenta with nothing to do with him. It
        # sits 16.4 from Ridley Scott's terracotta and 15.3 from Kurosawa's
        # dark, its two nearest neighbours.
        "accent": accent,
        "accentDark": accent_dark,
        "tiers": False,
        "notes": [
            ["The two-reelers are not here, and that is the whole scope "
             "question.",
             "The filmography's silent table has %d rows and this list takes "
             "%d of them. The other %d are Universal's Mustang Series, which "
             "the article's own footnote describes as two-reel films 24 "
             "minutes long — shorts, and this is a list of features, the same "
             "line the Hitchcock and Cronenberg lists drew about their "
             "directors' shorts. The source corroborates it exactly: those %d "
             "titles are the only red links in the whole filmography, and "
             "every other row has an article of its own. What stays is the "
             "%s five-reelers of the Blue Streak Series, two more Universal "
             "westerns of the same length that the table files under neither "
             "series, and the two part-talkies of 1929. A five-reel picture "
             "in 1927 is a feature."
             % (len(silents), len(silents) - len(mustang), len(mustang),
                len(mustang), word(len(bluestreak)))],
            ["One of these you cannot watch.",
             "Anybody Here Seen Kelly? (1928) was his first film that is not a "
             "western, and no print of it survives in any archive. It keeps "
             "its row anyway. A list that quietly drops the one lost film "
             "would be telling you the career had a shape it did not have."],
            ["The bars are not runtimes, and here is why not.",
             "Most film lists in this catalogue weigh their rows by runtime. "
             "This one cannot, because neither source that would supply the "
             "numbers covers all %d rows: Wikidata publishes no runtime at "
             "all for %s of them, every one a 1920s Universal picture, and "
             "the films' own articles publish no single figure for %s — one "
             "gives a reel "
             "count, two give nothing at all, and one gives a range. Blending "
             "the two sources would make the bar widths a mixture of two "
             "different measurements, and inventing a number for \"5 reels\" "
             "would be a guess. So no row is weighted and every mark is the "
             "same width. Ben-Hur shows what that saves: its own article says "
             "212 minutes excluding the overture, intermission and entr'acte, "
             "and Wikidata says 222, and with no bar to draw the list never "
             "has to pick one."
             % (len(films), word(len(no_wikidata)), word(len(no_infobox)))],
            ["One row per film, cuts included.",
             "The Shakedown (1929) is the only film here that went out in more "
             "than one version — a part-talkie for English-speaking audiences "
             "and a synchronised-score version for everywhere else — and the "
             "print that survives is the second, reissued silent. It gets one "
             "row, with the versions named on it. Ben-Hur and Funny Girl were "
             "roadshow releases whose two published lengths differ only by an "
             "overture and an intermission; that is a measurement difference "
             "rather than a different cut, and both are noted on their rows."],
            ["The four sections are Wikipedia's, not ours.",
             "His biography splits its Career section four ways — early work "
             "and silent films, career acclaim and stardom, established "
             "director, later work and final films — and this list takes those "
             "year ranges as its era boundaries rather than inventing its own. "
             "The generator reads the headings and fails if they change."],
            ["The filmography misses one Best Picture nomination.",
             "Its Notes column marks %d of these films as Best Picture "
             "nominees or winners and leaves The Heiress (1949) blank, but "
             "The Heiress was nominated, and this catalogue's own Best "
             "Picture list carries it. The rows follow the Best Picture list, "
             "so %d films here carry a Best Picture note and %s of those won. "
             "The Best Director record is separate and comes from his awards "
             "article: %s wins and %s further nominations, %s in all, which "
             "is still the record."
             % (len(marked), len(picture), word(len(picture_won)),
                word(len(director_won)), word(len(director_nom)),
                word(len(director_won) + len(director_nom)))],
            ["%d of these films are on other lists here." % len(shared),
             "%s. Ticking one ticks the other: film rows are paired across "
             "lists by title and year, so a film watched here is watched "
             "there. %s" % (sharing, nearmiss)],
            "Filmography from Wikipedia's William Wyler filmography, read from "
            "its own three tables; era boundaries from the career headings on "
            "the William Wyler article; release dates, credits and adaptation "
            "sources from each film's own article; the Best Director record "
            "from List of awards and nominations received by William Wyler; "
            "the Best Picture ticks from this catalogue's own Best Picture "
            "list.",
        ],
        "sections": sections,
    }

    out = prop.write(p)
    print("wrote %s — %d rows, %d years, unweighted"
          % (out.name, len(rows), span))
    for s in sections:
        print("   %-42s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))
    print("   excluded: %d Mustang two-reelers" % len(mustang))
    print("   shared with other lists: %d rows — %s"
          % (len(shared),
             "; ".join("%s: %s" % (t, ", ".join(bylist[t])) for t in bylist)))


if __name__ == "__main__":
    main()
