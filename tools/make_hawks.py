#!/usr/bin/env python3
"""Generate properties/hawks.json.

    PYTHONIOENCODING=utf-8 python tools/make_hawks.py

Howard Hawks' directed features in release order, in the three eras his own
Wikipedia biography divides his career into. Everything on the card — titles,
years, genres, runtimes, alternate-version lengths — is machine-read from
wikitext cached in scratch/agent-hawks/ by scratch/agent-hawks/fetch.py: the
"Howard Hawks filmography" article for the roster, the "Howard Hawks" article
for the era boundaries, and each film's own article for the rest. Nothing is
typed in from memory, and every claim the copy makes is asserted against the
source that produced it before anything is written.

THE ROSTER RULE: THE FILMS DIRECTED TABLE, MINUS WHAT CANNOT BE WATCHED
----------------------------------------------------------------------
The filmography's ==Films directed== table has 41 rows and its own lead says
he "made 40 films between 1926 and 1970". Both numbers are right, because one
row is not a film: "Ransom of Red Chief" is a segment of the five-director
anthology *O. Henry's Full House*, and it is the only row on the table whose
title is not set as a film title. Its article is the anthology's, and the only
running time anybody publishes for it is the anthology's 117 minutes. It is
not a feature of his, so it is not a row here.

Three more rows come off, under one rule read off one column. The table's own
Notes column marks exactly three films by survival — two "Lost film" and one
"Partially lost" — and marks nothing else that way:

  * *The Road to Glory* (1926), his first film, is lost.
  * *The Air Circus* (1928), the part-talkie, is lost. The biography names
    these two together: "one of two Hawks films that are lost".
  * *Cradle Snatchers* (1927) survives only as an incomplete print, "missing
    part of reel 3 and all of reel 4", at the Library of Congress.

This is a list of things to watch and tick, and none of those three can be
watched through. They are named in the notes rather than shipped as rows,
because a row nobody can complete is worse than an absence somebody can read
about. That leaves 37 films, 1926 to 1970.

CO-DIRECTED IN, WALKED-AWAY-FROM OUT — WHAT THE TABLE SAYS, NOT THE STORIES
---------------------------------------------------------------------------
Hawks attracts attribution arguments, and every one of them is settled here
the same way: by what the filmography's tables say, not by what anyone claims.

  * The four films the Notes column marks co-directed — *Scarface* and *Today
    We Live* with Richard Rosson, *Come and Get It* with William Wyler, and
    the lost *Air Circus* with Lewis Seiler — are rows. He is credited as a
    director of them; a shared credit is still a credit.
  * *The Thing from Another World* (1951) is not a row. John Carpenter is
    quoted in the filmography's own footnote saying it was "verifiably
    directed by Howard Hawks", and the article carries a whole section on the
    dispute — but the table files it under ==Films produced only==, crediting
    Christian Nyby, and that is the source's answer.
  * The four ==Unfinished projects== are not rows either: he resigned from
    *The Prizefighter and the Lady*, *Viva Villa!* and *The Outlaw* and was
    replaced each time, and *La foule hurle* is somebody else's
    French-language version of *The Crowd Roars*. *The Outlaw*'s own article
    is explicit that "none of the footage shot by Howard Hawks during the
    first two weeks of production ... remains in the finished film".
  * *Red River*'s Notes cell names Arthur Rosson as second-unit director.
    That is not co-direction and changes nothing.

THE ERAS ARE THE ARTICLE'S, NOT THIS FILE'S
-------------------------------------------
The biography splits its ==Career== section four ways — "Entering films
(1916–1925)", "Silent films (1925–1929)", "Early sound films (1930–1934)" and
"Later sound films (1935–1970)". main() reads all four headings out of the
wikitext, parses the year ranges out of them, asserts the first holds no
directed feature, and builds three sections from the rest. The headings are
asserted present first, so a rewrite upstream breaks the build rather than
leaving three hand-chosen boundaries pretending to be sourced.

The last section is much the largest — 25 of the 37 rows — because that is
where the article puts the line, and inventing a tidier one would be
inventing. The intros carry the genres instead, which is the point of this
particular filmography: the same man made *Scarface*, *Bringing Up Baby*,
*The Big Sleep*, *Red River* and *Rio Bravo*, and sorting his work by genre
would hide exactly that.

WEIGHTS: EVERY ROW, FROM THAT FILM'S OWN INFOBOX
------------------------------------------------
The page resolves `WEIGHT = x.w >= 0 ? x.w : 1`, so one unweighted row on a
weighted list silently books itself as an hour. Every row therefore carries
`w`, in hours, from the `runtime` field of that film's own {{Infobox film}} —
one source for all 37, never blended with anything else.

Wikidata's P2047 was the alternative and was rejected on quality after being
checked for all 41 rows (scratch/agent-hawks/probe2.py holds every value it
carries). It covers everything, including *Cradle Snatchers*, but several of
its figures are PAL-speedup running times taken off European discs — 136
minutes for the 141-minute *Rio Bravo*, 121 for the 126-minute *El Dorado*,
96 for the 100-minute *To Have and Have Not*, 88 for the 91-minute *Gentlemen
Prefer Blondes*, each of them the theatrical figure times 24/25. Shipping
those would be shipping numbers that are wrong by construction.

The one row the infoboxes cannot weigh is *Cradle Snatchers*, whose article
publishes "7 reels; 6,281 feet" and no running time in minutes — and it is
already off the list for surviving incomplete. That is a coincidence worth
saying out loud rather than hiding: the exclusion is a watchability ruling,
and it happens also to remove the only row this source could not weigh.

ALTERNATE CUTS: ONE ROW PER FILM
--------------------------------
Five of these films exist in more than one version according to the sources,
and none of them gets a second row — HOW-IT-WORKS.md's rule, because a second
row would either double the film's hours or have to carry no weight, and it
would pair with nothing on any other list. The cut lives in the row note, and
the note says which version the bar is measuring. The default is the
theatrical release, and four of the five take it:

  * *The Big Sleep* — the bar is the 114-minute 1946 release. A 116-minute
    1945 cut was sent to servicemen overseas before Warner Bros reshot the
    film; it was released publicly in 1997 and both are on the DVD.
  * *Red River* — the bar is the 127-minute theatrical cut, the one Howard
    Hughes prepared, which swapped the 133-minute pre-release version's
    book-page transitions for Walter Brennan's narration. Criterion's 2014
    release carries both. (The article contradicts itself about which of the
    two went missing and was recovered, so the note says only what both of
    its passages agree on.)
  * *Scarface* — the bar is the 93-minute version; the censors forced a second
    ending and that version runs 95.
  * *Land of the Pharaohs* — the bar is the 106-minute American version;
    Britain got 103.
  * *The Big Sky* — the bar is the 122-minute general release, the only figure
    its infobox gives. It first went out at 140 minutes and was cut.

THE BLURB CARRIES NO FILM COUNT (CLU-190). The hours in it are computed from
the weights that ship, so it cannot drift from the card.

Data:   scratch/agent-hawks/ (wikitext cache, probe*.py)
Accent: scratch/agent-hawks/accent.py
"""
import datetime
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop, wiki  # noqa: E402
from gwlib.prop import join_bits  # noqa: E402

SLUG = "hawks"
CACHE = prop.ROOT / "scratch" / "agent-hawks"
FILMOG = "Howard Hawks filmography"
BIO = "Howard Hawks"

# The four ===Career=== headings on the biography. The sections take their
# boundaries from the years inside these strings, parsed, not chosen; the
# first is asserted to hold no directed feature and produces no section.
ERA_HEADINGS = [
    "Entering films (1916–1925)",
    "Silent films (1925–1929)",
    "Early sound films (1930–1934)",
    "Later sound films (1935–1970)",
]

# Section titles and intros for the three heading ranges that hold films, in
# order. The boundaries are the article's; only the words are ours, and every
# number in them is computed in main() and asserted before it is printed.
ERA_COPY = [
    ("silent", "The Fox silents",
     "Fox hired him in 1925 on the promise of letting him direct, and he made "
     "eight films there in three years — comedies mostly, one of them from a "
     "story of his own, and one shot in the manner of the German pictures he "
     "had been watching. Three of the eight are not on this card: two are "
     "lost and one survives only as an incomplete print. His contract ended "
     "in May 1929 and he never signed a long-term one with a major studio "
     "again."),
    ("earlysound", "Proving it again in sound",
     "Fourteen years in the business and the talkies made him start over — "
     "studios were hiring stage directors and he had left Fox on bad terms. "
     "Seven films in five years, every one of them pre-Code: the gangster "
     "picture that had to grow a second ending for the censors, two about men "
     "who fly or drive fast, and at the end of it the first of the seven "
     "screwball comedies on this list."),
    ("latersound", "Thirty-five years, no two alike",
     "The long stretch, and the reason this is worth having as one list: "
     "screwball comedies, a war biography that got him his only Best Director "
     "nomination, film noir, a Marilyn Monroe musical, an Egyptian epic, and "
     "the Westerns he kept returning to — including one idea he made three "
     "times in eleven years. He produced most of them himself and worked with "
     "John Wayne five times."),
]

# Genre, read out of each film's own lead sentence. The value here is the
# display string; main() asserts every word of it appears in that film's lead
# paragraph, so a rewrite upstream fails the build instead of leaving the card
# describing a film Wikipedia no longer describes that way.
GENRE = {
    (1926, "Fig Leaves"): "Silent comedy",
    (1927, "Paid to Love"): "Silent comedy",
    (1928, "A Girl in Every Port"): "Silent comedy",
    (1928, "Fazil"): "Synchronized-sound drama",
    (1929, "Trent's Last Case"): "Synchronized-sound Pre-Code detective film",
    (1930, "The Dawn Patrol"): "Pre-Code World War I film",
    (1931, "The Criminal Code"): "Pre-Code romantic crime drama",
    (1932, "Scarface"): "Pre-Code gangster film",
    (1932, "The Crowd Roars"): "Pre-Code drama",
    (1932, "Tiger Shark"): "Pre-Code romantic melodrama",
    (1933, "Today We Live"): "Pre-Code romance drama",
    (1934, "Twentieth Century"): "Pre-Code screwball comedy",
    (1935, "Barbary Coast"): "Historical Western",
    (1936, "Ceiling Zero"): "Adventure drama",
    (1936, "The Road to Glory"): "War drama",
    (1936, "Come and Get It"): "Lumberjack drama",
    (1938, "Bringing Up Baby"): "Screwball comedy",
    (1939, "Only Angels Have Wings"): "Adventure romantic drama",
    (1940, "His Girl Friday"): "Screwball comedy",
    (1941, "Sergeant York"): "Biographical film",
    (1941, "Ball of Fire"): "Screwball comedy",
    (1943, "Air Force"): "World War II aviation film",
    (1944, "To Have and Have Not"): "Romantic war adventure",
    (1946, "The Big Sleep"): "Film noir",
    (1948, "Red River"): "Western",
    (1948, "A Song Is Born"): "Musical romantic comedy",
    (1949, "I Was a Male War Bride"): "Screwball comedy",
    (1952, "The Big Sky"): "Western",
    (1952, "Monkey Business"): "Screwball comedy",
    (1953, "Gentlemen Prefer Blondes"): "Musical comedy",
    (1955, "Land of the Pharaohs"): "Epic historical drama",
    (1959, "Rio Bravo"): "Western",
    (1962, "Hatari!"): "Adventure romantic comedy",
    (1964, "Man's Favorite Sport?"): "Screwball comedy",
    (1965, "Red Line 7000"): "Action sports film",
    (1966, "El Dorado"): "Western",
    (1970, "Rio Lobo"): "Western",
}

# The rest of each row note: what the film is, never what happens in it. Every
# one is grounded in a cached article — an infobox based_on / story / writer
# field, the filmography table's own Notes column, or a sentence of the
# biography. Rows with nothing worth saying carry the genre alone.
FACTS = {
    (1926, "Fig Leaves"):
        "His first comedy, and until 1935 his only one; the fashion-show "
        "sequence was shot in two-strip Technicolor",
    (1927, "Paid to Love"):
        "The experimental one — tracking shots and expressionist lighting out "
        "of German cinema, which he said afterwards was not his sort of thing",
    (1928, "A Girl in Every Port"):
        "From his own story, and the first of his films about two men whose "
        "friendship outranks everything else",
    (1928, "Fazil"):
        "From Pierre Frondaie's play L'Insoumise; it ran over schedule and "
        "began the rift with Fox that ended his contract",
    (1929, "Trent's Last Case"):
        "From E. C. Bentley's 1913 detective novel. He meant it to be his "
        "first talkie and Fox made him deliver a silent with a score",
    (1930, "The Dawn Patrol"):
        "His first all-sound film, from John Monk Saunders' story The Flight "
        "Commander",
    (1931, "The Criminal Code"):
        "From Martin Flavin's 1929 play",
    (1932, "Scarface"):
        "From Armitage Trail's novel, co-directed with Richard Rosson",
    (1932, "The Crowd Roars"):
        "From his own story. Warner Bros made a French-language version "
        "alongside it, La foule hurle, out of his footage and somebody "
        "else's direction",
    (1932, "Tiger Shark"):
        "From a Houston Branch story, and the third of the three films he "
        "released in 1932",
    (1933, "Today We Live"):
        "Co-directed with Richard Rosson, from William Faulkner's story Turn "
        "About — Faulkner wrote the dialogue too",
    (1934, "Twentieth Century"):
        "From Charles Bruce Millholland's play Napoleon of Broadway, adapted "
        "by Ben Hecht and Charles MacArthur",
    (1935, "Barbary Coast"):
        "Written by Hecht and MacArthur again, this time for Samuel Goldwyn",
    (1936, "Ceiling Zero"):
        "From Frank Wead's play, and the second of his two films with James "
        "Cagney",
    (1936, "The Road to Glory"):
        "Trench warfare in France, and the second film of his to carry this "
        "title — the 1926 one is lost",
    (1936, "Come and Get It"):
        "From Edna Ferber's 1935 novel, co-directed with William Wyler",
    (1938, "Bringing Up Baby"):
        "From a Hagar Wilde short story in Collier's",
    (1939, "Only Angels Have Wings"):
        "From his own story",
    (1940, "His Girl Friday"):
        "From The Front Page, the Hecht and MacArthur play, with the star "
        "reporter rewritten as a woman",
    (1941, "Sergeant York"):
        "From Alvin York's own diary. His only Best Director nomination; the "
        "only Oscar he ever took home was the honorary one in 1974",
    (1941, "Ball of Fire"):
        "From a Billy Wilder and Thomas Monroe story called From A to Z",
    (1944, "To Have and Have Not"):
        "Loosely from Hemingway's 1937 novel, with William Faulkner on the "
        "screenplay",
    (1946, "The Big Sleep"):
        "From Raymond Chandler's 1939 novel",
    (1948, "Red River"):
        "From Borden Chase's Saturday Evening Post serial The Chisholm Trail",
    (1948, "A Song Is Born"):
        "A musical remake of his own Ball of Fire, seven years on, and the "
        "first film of his in Technicolor",
    (1949, "I Was a Male War Bride"):
        "From a newspaper account by Henri Rochard of his own marriage",
    (1952, "The Big Sky"):
        "From A. B. Guthrie Jr.'s novel",
    (1952, "Monkey Business"):
        "The last of his five films with Cary Grant",
    (1953, "Gentlemen Prefer Blondes"):
        "From the 1949 stage musical, itself from Anita Loos' 1925 novel",
    (1955, "Land of the Pharaohs"):
        "In CinemaScope and WarnerColor, co-written by William Faulkner",
    (1959, "Rio Bravo"):
        "From a B. H. McCampbell story, and the first of the three films the "
        "filmography calls the same idea",
    (1962, "Hatari!"):
        "Shot on location in northern Tanganyika, now Tanzania",
    (1964, "Man's Favorite Sport?"):
        "From a Pat Frank story in Cosmopolitan",
    (1965, "Red Line 7000"):
        "He wrote the story himself as well as producing it",
    (1966, "El Dorado"):
        "From Harry Brown's 1960 novel The Stars in Their Courses, and the "
        "filmography's own notes call it the same idea as Rio Bravo",
    (1970, "Rio Lobo"):
        "His last film, and the third worked from the Rio Bravo idea",
}

# The films whose infobox publishes more than one running time. The value is
# (label to measure, note). main() asserts the label is one the field actually
# carries and that the number it picks is one of the field's own figures — the
# override lives here, in one visible place, and never invents a number.
CUT_PICKS = {
    (1932, "Scarface"): (
        "",
        "The bar is the {picked}-minute version; the censors forced a second "
        "ending, and that one runs {other}"),
    (1946, "The Big Sleep"): (
        "released cut",
        "The bar is the {picked}-minute 1946 release; the {other}-minute 1945 "
        "cut, sent to servicemen overseas before the studio reshot the film, "
        "came out publicly in 1997"),
    (1948, "Red River"): (
        "Theatrical",
        "The bar is the {picked}-minute theatrical cut, which replaced the "
        "{other}-minute pre-release version's book-page transitions with "
        "spoken narration; Criterion's 2014 release carries both"),
    (1955, "Land of the Pharaohs"): (
        "U.S.",
        "The bar is the {picked}-minute American version; Britain got "
        "{other}"),
}

# The one film whose second version is in its article's prose rather than in
# its infobox. The sentence is asserted present before the note is written.
BIGSKY = (1952, "The Big Sky")
BIGSKY_CLAIM = "reduced from 140 minutes to 122 minutes for the film's general release"

# Every sentence a cut note leans on, checked against the article that
# produced it. A version note is the easiest thing on a card to get subtly
# wrong, so none of these is trusted to memory.
CUT_CLAIMS = {
    (1932, "Scarface"): [
        "censors required the ending to be modified",
        "The alternate ending (Version B)"],
    (1946, "The Big Sleep"): [
        "A cut was released to servicemen overseas in 1945",
        "reshoots of ''The Big Sleep'' were done in early 1946",
        "In 1997, the original 1945 cut was restored and released",
        "==1997 release of the 1945 original cut=="],
    # the Red River article contradicts itself on which cut went missing —
    # one paragraph has the pre-release version rediscovered as a Cinémathèque
    # print, the next has the theatrical cut lost and reassembled by Janus for
    # the same 2014 Criterion release. The note therefore says only what both
    # passages agree on: which version carries what, and that Criterion's
    # release carries both.
    (1948, "Red River"): [
        "the pre-release version was 133 minutes and included book-style transitions",
        "released by [[the Criterion Collection]]",
        "Hughes prepared a new 127-minute cut, which replaced the book inserts "
        "with spoken [[narration]] by Walter Brennan",
        "The original theatrical cut was reassembled by [[Janus Films]]",
        "Criterion Collection Blu-ray/DVD release on May 27, 2014"],
    (1955, "Land of the Pharaohs"): [
        "106 minutes (U.S.)", "103 minutes (UK)"],
}

# What the roster rule drops, and why. Asserted row by row in main() against
# the column that says so — nothing here is taken on trust.
SEGMENT = '"Ransom of Red Chief"'
LOST_NOTE, PARTIAL_NOTE = "Lost film", "Partially lost"

# Rows on other film lists that share a title with one of these and are NOT
# the same work — checked by hand, one entry per (slug, title, n). Anything
# not listed here that fails to pair stops the build.
NEAR_OK = set()

_CELL = re.compile(r"^[|!]\s*(?:([^|\[{]*=[^|\[{]*)\|)?\s*(.*)$", re.S)


def table_after(text, heading):
    """The first wikitable following a `==heading==` line."""
    m = re.search(r"^=+\s*%s\s*=+\s*$" % re.escape(heading), text, re.M)
    assert m, "no %r section on the article" % heading
    a = text.index("\n{|", m.end())
    return text[a:text.index("\n|}", a)]


def table_rows(seg, ncols):
    """(group, cells) per row, with rowspan carried down.

    The Films directed table's Year column rowspans over every year holding
    more than one film, and the Notes and Other roles columns rowspan too — a
    six-row Technicolor cell runs from Gentlemen Prefer Blondes to Red Line
    7000, and a four-row Producer cell from Bringing Up Baby to Sergeant York.
    Picking cells positionally without carrying those spans hands most of the
    fifties the wrong year, which is the bug this parser exists to avoid.

    `group` is the last full-width banner row seen — the table separates
    "Silent films" from "Sound films" with a colspan cell rather than a
    heading, so the banner is data and is returned rather than dropped. Banner
    rows never touch the rowspan state.
    """
    out, pending, group = [], {}, None
    for chunk in seg.split("\n|-"):
        cells = [l.strip() for l in chunk.split("\n")
                 if l.strip()[:1] in ("|", "!")]
        if not cells:
            continue
        if cells[0].startswith("!"):          # the column-definition row
            continue
        if re.search(r'colspan="?%d' % ncols, cells[0]):
            group = _CELL.match(cells[0]).group(2).replace("'''", "").strip()
            continue
        raw = iter(cells)
        cols = []
        for c in range(ncols):
            if c in pending:
                cols.append(pending[c][1])
                pending[c][0] -= 1
                if pending[c][0] == 0:
                    del pending[c]
                continue
            m = _CELL.match(next(raw, "|"))
            attrs, content = m.group(1) or "", m.group(2)
            cols.append(content)
            sp = re.search(r'rowspan="?(\d+)', attrs)
            if sp and int(sp.group(1)) > 1:
                pending[c] = [int(sp.group(1)) - 1, content]
        out.append((group, cols))
    return out


def link(cell):
    """The wikilink target inside a title cell."""
    m = re.search(r"\[\[([^\]|]+)", cell)
    return m.group(1).strip() if m else None


def article(page):
    """The cached wikitext for a linked page, refs stripped."""
    txt = wiki.wikitext(page, cache_dir=CACHE)
    assert txt, "no cached article for %r — run scratch/agent-hawks/fetch.py" % page
    return txt


def lead(text):
    """The article's bold lead paragraph, cleaned to display text."""
    m = re.search(r"^'''.{0,2500}", text, re.M | re.S)
    assert m, "no bold lead paragraph"
    return wiki.clean(m.group(0))


def figures(field, what):
    """Every (minutes, label) the infobox runtime field publishes.

    A field with no whole-minute figure fails: this list weights every row,
    and an estimate wearing a citation is worse than a build that stops.
    """
    v = wiki.clean(field or "")
    out = []
    for m in re.finditer(r"(?<!\d)(\d{2,3})\s*min(?:ute)?s?\.?"
                         r"\s*,?\s*(?:\(([^)]*)\))?", v):
        n = int(m.group(1))
        assert 50 <= n <= 240, "%s: implausible runtime %d in %r" % (what, n, v)
        out.append((n, (m.group(2) or "").strip()))
    assert out, "%s publishes no runtime in minutes: %r" % (what, v)
    return out


def released(field, what):
    """(year, earliest full date or None) from an infobox `released` field."""
    dates, years = [], []
    for m in re.finditer(r"\{\{\s*[Ff]ilm date\s*\|(.*?)\}\}", field or "", re.S):
        body = m.group(1)
        for d in re.finditer(r"(?<!\d)((?:18|19|20)\d{2})\s*\|\s*(\d{1,2})"
                             r"\s*\|\s*(\d{1,2})(?!\d)", body):
            try:
                dates.append(datetime.date(*(int(g) for g in d.groups())))
            except ValueError:
                pass
        years += [int(y) for y in re.findall(r"(?<!\d)((?:19|20)\d{2})(?!\d)",
                                             body)]
    assert years, "%s: no release date on the infobox" % what
    return (min(d.year for d in dates) if dates else min(years),
            min(dates) if dates else None)


def normt(t):
    return prop.normt(t)


def year_of(x, n):
    """build.py's year-for-sync rule, copied so this generator computes the
    same groups the build will."""
    if re.fullmatch(r"(18|19|20)\d{2}", n):
        return n
    explicit = str(x.get("y", ""))
    if re.fullmatch(r"(18|19|20)\d{2}", explicit):
        return explicit
    found = set(re.findall(r"\b((?:18|19|20)\d{2})\b", x.get("note") or ""))
    return found.pop() if len(found) == 1 else None


def overlaps(keys, mine):
    """({sync key -> [list titles]}, [near misses]) over the shipped films.

    The second half is the live bug class (CLU-191, CLU-247): a row on another
    list carrying one of these titles that will NOT pair, because its sync
    year comes out different or comes out empty. A ceremony-dated award list
    misses by exactly one year and looks fine until you tick something.
    """
    out, near = {}, []
    for f in sorted((prop.ROOT / "properties").glob("*.json")):
        if f.stem in ("index", "search", SLUG):
            continue
        p = json.loads(f.read_text(encoding="utf-8"))
        if not isinstance(p, dict) or p.get("secret"):
            continue
        if "film" not in (p.get("kind") or ""):
            continue
        for s in p.get("sections", []):
            for x in s.get("items", []):
                nt = normt(x["t"])
                y = year_of(x, str(x.get("n", "")))
                k = nt + "|" + (y or "")
                if k in keys:
                    if p["title"] not in out.get(k, []):
                        out.setdefault(k, []).append(p["title"])
                elif nt in mine:
                    near.append((p["title"], p["slug"], x["t"],
                                 str(x.get("n", "")), y, mine[nt]))
    return out, near


def and_list(names):
    names = list(names)
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + " and " + names[-1]


WORDS = ("no", "one", "two", "three", "four", "five", "six", "seven", "eight",
         "nine", "ten", "eleven", "twelve")


def word(n):
    """Small counts read as words in prose; anything bigger stays a numeral."""
    return WORDS[n] if n < len(WORDS) else str(n)


def main():
    today = datetime.date.today()
    art = article(FILMOG)
    bio = article(BIO)

    # ---- the eras are the biography's own headings ------------------------
    eras = []
    for h in ERA_HEADINGS:
        assert re.search(r"^=+\s*%s\s*=+\s*$" % re.escape(h), bio, re.M), \
            ("the career heading %r is gone from %s — the sections take their "
             "boundaries from it and must be re-derived" % (h, BIO))
        m = re.search(r"\((\d{4})[–-](\d{4}|present)\)", h)
        assert m, h
        eras.append((int(m.group(1)),
                     today.year if m.group(2) == "present" else int(m.group(2))))
    assert len(eras) == 4 and len(ERA_COPY) == 3, (eras, len(ERA_COPY))
    assert [e[0] for e in eras] == sorted(e[0] for e in eras), eras

    # ---- the table ---------------------------------------------------------
    rows = table_rows(table_after(art, "Films directed"), 4)
    assert len(rows) == 41, len(rows)
    assert sorted({g for g, _ in rows}) == ["Silent films", "Sound films"], \
        sorted({g for g, _ in rows})

    table = []
    for group, (year, title, note, roles) in rows:
        table.append({
            "group": group, "year": int(wiki.clean(year)),
            "t": wiki.clean(title), "page": (link(title) or "").split("#")[0],
            "tablenote": wiki.clean(note), "roles": wiki.clean(roles),
            "italic": title.strip().startswith("''"),
        })
    assert all(f["page"] for f in table), [f["t"] for f in table if not f["page"]]

    # the lead's own arithmetic: 41 rows, 40 films, and the row it does not
    # count is the one that is not set as a film title
    filmog_lead = wiki.clean(art[:art.index("\n==")])
    m = re.search(r"made (\d+) films between (\d{4}) and (\d{4})", filmog_lead)
    assert m, filmog_lead[:200]
    claimed, lo_year, hi_year = (int(m.group(1)), int(m.group(2)),
                                 int(m.group(3)))
    segment = [f for f in table if not f["italic"]]
    assert [f["t"] for f in segment] == [SEGMENT], [f["t"] for f in segment]
    assert len(table) - len(segment) == claimed == 40, (len(table), claimed)
    # and its article is the anthology's, which is what makes it a segment
    seg = segment[0]
    seg_ib = wiki.infobox(article(seg["page"]), kind="film")
    assert seg_ib and wiki.clean(seg_ib("name")) == "O. Henry's Full House", \
        wiki.clean(seg_ib("name")) if seg_ib else None
    assert len(wiki.clean(seg_ib("director")).split(",")) == 5, \
        wiki.clean(seg_ib("director"))

    # the survival rule, read off the Notes column and nowhere else
    lost = [f for f in table if LOST_NOTE in f["tablenote"]]
    partial = [f for f in table if PARTIAL_NOTE in f["tablenote"]]
    assert [f["t"] for f in lost] == ["The Road to Glory", "The Air Circus"], \
        [f["t"] for f in lost]
    assert [f["t"] for f in partial] == ["The Cradle Snatchers"], \
        [f["t"] for f in partial]
    assert "one of two Hawks films that are lost" in wiki.clean(bio), \
        "the biography no longer says two films are lost"
    partial_page = article(partial[0]["page"])
    assert "missing part of reel 3 and all of reel 4" in wiki.clean(partial_page), \
        "Cradle Snatchers' preservation note has changed — recheck the exclusion"
    # and it is the one row no source weighs in minutes, which is why the
    # infobox source can weigh every row that ships
    pt_ib = wiki.infobox(partial_page, kind="film")
    assert "reels" in wiki.clean(pt_ib("runtime")) and \
        not re.search(r"\d+\s*min", wiki.clean(pt_ib("runtime"))), \
        wiki.clean(pt_ib("runtime"))
    assert wiki.clean(pt_ib("name")) == "Cradle Snatchers", \
        wiki.clean(pt_ib("name"))

    dropped = {id(f) for f in lost + partial + segment}
    assert len(dropped) == 4, len(dropped)
    films = [f for f in table if id(f) not in dropped]
    assert len(films) == 37, len(films)
    assert films[0]["year"] == lo_year and films[-1]["year"] == hi_year, \
        (films[0], films[-1])

    # co-direction stays; the source's own words for each of the four
    codirected = [f for f in table if "Co-directed" in f["tablenote"]]
    assert [f["t"] for f in codirected] == \
        ["The Air Circus", "Scarface", "Today We Live", "Come and Get It"], \
        [f["t"] for f in codirected]
    assert sum(1 for f in codirected if id(f) not in dropped) == 3, codirected
    # ... and the two tables that are deliberately not the roster
    produced = table_rows(table_after(art, "Films produced only"), 6)
    assert [wiki.clean(c[1]) for _g, c in produced] == \
        ["Corvette K-225", "The Thing from Another World"], produced
    assert all("directed by" in wiki.clean(c[5]) for _g, c in produced), \
        [wiki.clean(c[5]) for _g, c in produced]
    unfinished = table_rows(table_after(art, "Unfinished projects"), 3)
    assert [wiki.clean(c[1]) for _g, c in unfinished] == \
        ["La foule hurle", "The Prizefighter and the Lady", "Viva Villa!",
         "The Outlaw"], unfinished
    assert sum(1 for _g, c in unfinished
               if "resigned" in wiki.clean(c[2])) == 3, unfinished
    # the claim lives inside an {{efn}} on the director field, which clean()
    # removes whole, so this reads the raw wikitext
    outlaw = re.sub(r"\s+", " ", article("The Outlaw"))
    assert "none of the footage shot by [[Howard Hawks]]" in outlaw or \
        "none of the footage shot by Howard Hawks" in outlaw, \
        "The Outlaw no longer says Hawks' footage is gone — recheck"

    # ---- each film's own article ------------------------------------------
    for f in films:
        page = article(f["page"])
        ib = wiki.infobox(page, kind="film")
        assert ib, "no film infobox on %s" % f["page"]
        name = wiki.clean(ib("name")) or f["t"]
        assert normt(name) == normt(f["t"]), \
            "%s calls itself %r" % (f["t"], name)
        f["t"] = name
        f["lead"] = lead(page)
        f["figures"] = figures(ib("runtime"), f["t"])
        f["starring"] = wiki.clean(ib("starring"))
        f["story"] = wiki.clean(ib("story"))
        f["raw"] = re.sub(r"\s+", " ", page)
        f["body"] = wiki.clean(re.sub(r"<ref.*?</ref>", "", page, flags=re.S))
        ryear, rdate = released(ib("released"), f["t"])
        f["released"] = rdate or ryear
        assert ryear == f["year"], \
            "%s: the filmography says %d, its own article's first release is %d" \
            % (f["t"], f["year"], ryear)
        assert (rdate or datetime.date(ryear, 12, 31)) <= today, \
            "%s is dated %s and has not come out" % (f["t"], f["released"])

    # release order, checked to the day where the day is published
    order = [f["released"] if isinstance(f["released"], datetime.date)
             else datetime.date(f["released"], 1, 1) for f in films]
    assert order == sorted(order), \
        "the Films directed table's order is not release order"

    # ---- runtimes: one figure, or a pick made here and asserted -----------
    for f in films:
        key = (f["year"], f["t"])
        figs = f["figures"]
        if len(figs) == 1:
            f["runtime"], f["cutnote"] = figs[0][0], None
            continue
        assert key in CUT_PICKS, \
            "%s publishes %d runtimes and no pick is recorded: %s" \
            % (f["t"], len(figs), figs)
        label, template = CUT_PICKS[key]
        want = [n for n, lab in figs if lab == label]
        assert len(want) == 1, \
            "%s: %r matches %d of %s" % (f["t"], label, len(want), figs)
        other = [n for n, lab in figs if lab != label]
        assert len(other) == 1, (f["t"], figs)
        f["runtime"] = want[0]
        f["cutnote"] = template.format(picked=want[0], other=other[0])
    assert set(CUT_PICKS) == {(f["year"], f["t"]) for f in films
                              if len(f["figures"]) > 1}, \
        sorted(set(CUT_PICKS) ^ {(f["year"], f["t"]) for f in films
                                 if len(f["figures"]) > 1})

    # the fifth noted version, which lives in prose rather than in an infobox
    sky = next(f for f in films if (f["year"], f["t"]) == BIGSKY)
    assert BIGSKY_CLAIM in sky["body"], \
        "The Big Sky no longer states the 140-minute original — recheck"
    assert sky["runtime"] == 122 and len(sky["figures"]) == 1, sky["figures"]
    sky["cutnote"] = ("The bar is the 122-minute general release; it first "
                      "went out at 140 minutes and was cut")
    cut_rows = [f for f in films if f["cutnote"]]
    assert [f["t"] for f in cut_rows] == \
        ["Scarface", "The Big Sleep", "Red River", "The Big Sky",
         "Land of the Pharaohs"], [f["t"] for f in cut_rows]
    # every sentence the version notes stand on, re-read from the article
    assert set(CUT_CLAIMS) <= {(f["year"], f["t"]) for f in cut_rows}, \
        sorted(CUT_CLAIMS)
    for f in cut_rows:
        for claim in CUT_CLAIMS.get((f["year"], f["t"]), []):
            assert re.sub(r"\s+", " ", claim) in f["raw"], \
                "%s no longer says %r — the version note is stale" \
                % (f["t"], claim)

    # ---- what the copy claims, checked against the source -----------------
    roster_keys = {(f["year"], f["t"]) for f in films}
    # a genre for every row, and no fact attached to a row that is not here.
    # Air Force is the one row whose note is its genre alone — nothing in its
    # article says anything about the film that is not about its plot.
    assert set(GENRE) == roster_keys, sorted(set(GENRE) ^ roster_keys)
    assert roster_keys - set(FACTS) == {(1943, "Air Force")}, \
        sorted(roster_keys - set(FACTS))
    for f in films:
        words = re.findall(r"[a-z0-9]+",
                           GENRE[(f["year"], f["t"])].lower().replace("-", " "))
        have = set(re.findall(r"[a-z0-9]+", f["lead"].lower().replace("-", " ")))
        missing = [w for w in words if w not in have]
        assert not missing, \
            "%s's lead no longer says %s (missing %s)" \
            % (f["t"], GENRE[(f["year"], f["t"])], missing)

    by_era = []
    for (lo, hi) in eras:
        by_era.append([f for f in films if lo <= f["year"] <= hi])
    assert not by_era[0], \
        "a directed feature now falls in %r" % ERA_HEADINGS[0]
    assert sum(len(g) for g in by_era) == len(films), \
        "a film falls outside every era, or inside two"
    silent, early, later = by_era[1], by_era[2], by_era[3]
    assert (len(silent), len(early), len(later)) == (5, 7, 25), \
        (len(silent), len(early), len(later))
    # the one row whose filmography group and era-by-year disagree is the lost
    # part-talkie, and it is not shipped
    crossers = [f for f in table
                if (f["group"] == "Sound films") != (f["year"] > eras[1][1])]
    assert [f["t"] for f in crossers] == ["The Air Circus"], \
        [f["t"] for f in crossers]

    # intro claims
    assert "directed his first eight films" in wiki.clean(bio), \
        "the biography no longer counts eight Fox films"
    assert "never again signed a long-term contract with a major studio" in \
        wiki.clean(bio), "the biography no longer says he left Fox for good"
    assert "After working in the industry for 14 years" in wiki.clean(bio), \
        "the biography no longer says he had to prove himself again"
    precode = [f for f in early if "pre-code" in f["lead"].lower()]
    assert len(precode) == len(early) == 7, [f["t"] for f in early]
    wayne = [f for f in films if "John Wayne" in f["starring"]]
    assert len(wayne) == 5, [f["t"] for f in wayne]
    grant = [f for f in films if "Cary Grant" in f["starring"]]
    assert len(grant) == 5 and grant[-1]["t"] == "Monkey Business", \
        [f["t"] for f in grant]
    riobravo = [f for f in table if "Similar idea to" in f["tablenote"]]
    assert [f["t"] for f in riobravo] == ["El Dorado", "Rio Lobo"], \
        [f["t"] for f in riobravo]
    assert riobravo[-1]["year"] - 1959 == 11, riobravo[-1]["year"]
    assert "nominated for Academy Award for Best Director in 1942 for " \
        "Sergeant York" in wiki.clean(bio), "the Oscar claim has moved"
    westerns = [f for f in films
                if "western" in GENRE[(f["year"], f["t"])].lower()]
    assert len(westerns) == 6, [f["t"] for f in westerns]
    screwball = [f for f in films
                 if "screwball" in GENRE[(f["year"], f["t"])].lower()]
    assert len(screwball) == 7, [f["t"] for f in screwball]
    assert screwball[0]["t"] == "Twentieth Century" and \
        screwball[0] is early[-1], \
        "the first screwball is no longer the last of the early sound films"
    own = [f for f in films if "Howard Hawks" in f["story"]]
    assert [f["t"] for f in own if f in silent] == ["A Girl in Every Port"], \
        [f["t"] for f in own if f in silent]
    assert "The Crowd Roars" in [f["t"] for f in own], [f["t"] for f in own]
    cagney = [f for f in films if "James Cagney" in f["starring"]]
    assert [f["t"] for f in cagney] == ["The Crowd Roars", "Ceiling Zero"], \
        [f["t"] for f in cagney]
    assert [f["t"] for f in films if f["year"] == 1932] == \
        ["Scarface", "The Crowd Roars", "Tiger Shark"], \
        [f["t"] for f in films if f["year"] == 1932]
    tiger = next(f for f in films if f["t"] == "Tiger Shark")
    assert tiger["story"] == "Houston Branch", tiger["story"]
    pharaohs = next(f for f in films if f["t"] == "Land of the Pharaohs")
    assert "CinemaScope and WarnerColor" in pharaohs["lead"], pharaohs["lead"][:200]
    assert "three credited screenwriters" in pharaohs["body"] and \
        "William Faulkner" in pharaohs["body"], "the Faulkner credit has moved"

    # ---- sections ----------------------------------------------------------
    sections = []
    for got, (sid, title, intro) in zip(by_era[1:], ERA_COPY):
        mins = sum(f["runtime"] for f in got)
        items = []
        for f in got:
            note = join_bits(GENRE[(f["year"], f["t"])],
                             FACTS.get((f["year"], f["t"])), f["cutnote"])
            items.append({"id": "hh-%d-%s" % (f["year"], prop.slug(f["t"])),
                          "t": f["t"], "n": str(f["year"]),
                          "w": round(f["runtime"] / 60.0, 2),
                          "note": note})
        sections.append({
            "id": sid, "title": title,
            "sub": "%d–%d · %d films · %d hours"
                   % (got[0]["year"], got[-1]["year"], len(got),
                      round(mins / 60.0)),
            "intro": intro, "items": items})
    sections[0]["open"] = True

    items = [x for s in sections for x in s["items"]]
    assert len(items) == len(films) == 37, len(items)
    assert len({x["id"] for x in items}) == len(items), "duplicate ids"
    assert all(isinstance(x["w"], float) and x["w"] > 0 for x in items), \
        [x["id"] for x in items if not x.get("w")]
    ys = [x["n"] for x in items]
    assert ys == sorted(ys), "the card is out of release order"
    mins = sum(f["runtime"] for f in films)
    hours = round(sum(x["w"] for x in items), 2)
    assert abs(hours - mins / 60.0) < 0.2, (hours, mins / 60.0)
    shortest = min(films, key=lambda f: f["runtime"])
    longest = max(films, key=lambda f: f["runtime"])

    # ---- the films this list shares with other lists here -----------------
    keys = {normt(f["t"]) + "|" + str(f["year"]): f["t"] for f in films}
    mine = {normt(f["t"]): f["t"] for f in films}
    shared, near = overlaps(keys, mine)
    # a title of ours on another film list that does not pair. NEAR_OK holds
    # the ones checked by hand and found to be different films; anything else
    # is a sync bug and stops the build rather than shipping a broken group.
    unexplained = [n for n in near if (n[1], n[2], n[3]) not in NEAR_OK]
    assert not unexplained, \
        "these rows share a title with this list and will not pair: %s" \
        % unexplained
    by_list = {}
    for k, titles in shared.items():
        for t in titles:
            by_list.setdefault(t, []).append(keys[k])
    # the three groups verified by hand against each list's own rows. Other
    # lists may join later — the count and the prose are computed, not typed —
    # but these must never silently stop pairing.
    assert set(by_list["The Criterion Collection"]) == \
        {"Scarface", "Bringing Up Baby", "Only Angels Have Wings",
         "His Girl Friday", "Red River"}, by_list.get("The Criterion Collection")
    assert by_list["Best Picture"] == ["Sergeant York"], by_list["Best Picture"]
    assert set(by_list["John Wayne"]) == \
        {"Red River", "Rio Bravo", "Hatari!", "El Dorado", "Rio Lobo"}, \
        by_list.get("John Wayne")
    order_of = [f["t"] for f in films]
    phrases = ["%s on %s" % (and_list(sorted(by_list[t], key=order_of.index)), t)
               for t in sorted(by_list, key=lambda t: (-len(by_list[t]), t))]
    # the clause naming the most-shared film only appears when there is one
    # to name — the catalogue grows and this must not need editing when it does
    busiest = max(shared, key=lambda k: (len(shared[k]), k))
    triple = ("" if len(shared[busiest]) < 2 else
              " — %s sits on %s lists at once"
              % (keys[busiest], word(len(shared[busiest]) + 1)))
    sharing = ("%s. Ticking one ticks the other: film rows are paired across "
               "lists by title and year, so a film watched here is watched "
               "there%s. Criterion numbers its rows by spine rather than by "
               "year, so its five pair through the year written in the "
               "spine's note instead. Nothing is duplicated and no hours are "
               "counted twice, because every list totals only its own rows."
               % ("; ".join(phrases), triple))

    # ---- the accent pair is nobody else's ---------------------------------
    accent, accent_dark = "#5F6142", "#A69A5E"
    for f in sorted((prop.ROOT / "properties").glob("*.json")):
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

    p = {
        "slug": SLUG,
        "title": "Howard Hawks",
        "subtitle": "the directed features, in release order",
        "kind": "films",
        # Nobody has to be told what Scarface, His Girl Friday, The Big Sleep,
        # Gentlemen Prefer Blondes or Rio Bravo are; plenty of people have
        # never heard the name that connects them. So: above Cronenberg (56)
        # and Universal Monsters (56), below Kurosawa (62) and Carpenter (61),
        # whose names travel further than his does. See POPULARITY.md.
        "popularity": 60,
        "year": "%d–%d" % (films[0]["year"], films[-1]["year"]),
        "blurb": "Every feature he directed, Fig Leaves to Rio Lobo — "
                 "gangsters, screwball, noir and Westerns from one man across "
                 "%d years, about %d hours."
                 % (films[-1]["year"] - films[0]["year"], round(hours)),
        "unit": {"one": "film", "many": "films"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        # Light: the olive drab of a flight jacket — he flew before he
        # directed and kept making pictures about aeroplanes. Dark: the same
        # tone gone khaki-gold, which is what the late Westerns are shot on.
        # Measured in CIELAB against every accent in properties/index.json;
        # see scratch/agent-hawks/accent.py. Every obvious pick is taken — the
        # Rio Bravo desert tan lands 8.8 from Criterion's, the aviation sky
        # 3.0 from The Office's, the newsprint grey IS Hitchcock's, and the
        # cockpit green 2.3 from One Pace's. This pair is 13.7 worst-case from
        # its nearest neighbour, MASH's #4B5320. The dark half was re-picked
        # once mid-build: the first choice sat 6.4 from the Clint Eastwood
        # list's dark accent, which shipped while this file was being written.
        "accent": accent,
        "accentDark": accent_dark,
        "tiers": False,
        "notes": [
            ["The features he directed — 37 of the 41 rows on the table.",
             "The roster is Wikipedia's Films directed table, read from the "
             "table itself. Four rows are not on this card. Ransom of Red "
             "Chief is a segment of the five-director anthology O. Henry's "
             "Full House rather than a film of his — the only row on that "
             "table not set as a film title, which is why the article's own "
             "lead counts 40 films across 41 rows. The other three are here "
             "in words instead of rows, below."],
            ["Three films are missing because nobody can watch them.",
             "The table's Notes column marks exactly three films by survival, "
             "and all three come off. The Road to Glory (1926), his first "
             "film, and The Air Circus (1928), the part-talkie he refused to "
             "shoot dialogue for, are lost — the biography names them "
             "together as his two lost films. Cradle Snatchers (1927) "
             "survives only as an incomplete print at the Library of "
             "Congress, missing part of reel 3 and all of reel 4. A row is "
             "something to watch and tick, and none of those three can be "
             "finished. They are named here so their absence is a decision "
             "rather than a gap."],
            ["Co-directed films are here. The ones he walked away from are "
             "not.",
             "He attracts attribution arguments, and every one of them is "
             "settled the same way: by what the filmography's tables say. "
             "Scarface and Today We Live are marked co-directed with Richard "
             "Rosson and Come and Get It with William Wyler, so all three are "
             "rows — a shared credit is still a credit. The Thing from "
             "Another World is not, even though the filmography's own "
             "footnote quotes John Carpenter calling it verifiably "
             "directed by Howard Hawks: the table files it under films "
             "produced only, crediting Christian Nyby. Nor are the four "
             "unfinished projects — he resigned from The Prizefighter and the "
             "Lady, Viva Villa! and The Outlaw and was replaced each time, "
             "and The Outlaw's own article says none of his footage survives "
             "in the finished film. Red River's second-unit director is not "
             "co-direction and changes nothing."],
            ["One row per film, cuts and all.",
             "Five of these exist in more than one version according to the "
             "sources — Scarface, The Big Sleep, Red River, The Big Sky and "
             "Land of the Pharaohs — and none gets a second row. A row is "
             "something to watch and tick, and the 1945 Big Sleep is not a "
             "second film to get through: a second row would either double "
             "that film's hours or have to carry no weight, and this list has "
             "no unweighted rows in it. So the version is named on the row "
             "instead, and the note says which one the bar is measuring. Four "
             "of the five measure the theatrical release; The Big Sky "
             "measures the general release, the only figure its article "
             "gives, and names the longer first cut."],
            ["Bar widths are runtimes, from one source.",
             "All 37 come from the runtime published in that film's own "
             "Wikipedia infobox, in hours — never estimated, never blended "
             "with a second source. Wikidata was the alternative and was "
             "checked for every row before being turned down: several of its "
             "figures are PAL running times taken off European discs, which "
             "would have shipped 136 minutes for the 141-minute Rio Bravo and "
             "121 for the 126-minute El Dorado. The shortest here is %s (%d) "
             "at %d minutes and the longest %s (%d) at %d."
             % (shortest["t"], shortest["year"], shortest["runtime"],
                longest["t"], longest["year"], longest["runtime"])],
            ["The three sections are Wikipedia's, not ours.",
             "His biography splits its Career section four ways — entering "
             "films, silent films, early sound films, later sound films — and "
             "this list takes those year ranges as its era boundaries rather "
             "than inventing its own. The first holds no film he directed, so "
             "there are three sections and not four, and the last one is "
             "enormous because that is where the article puts the line. The "
             "generator reads the headings and fails if they change. Sorting "
             "him by genre instead would have hidden the only thing this "
             "filmography is really about, which is that one man made all of "
             "these."],
            ["%d of these films are on other lists here." % len(shared),
             sharing],
            "Roster from Wikipedia's Howard Hawks filmography, read from the "
            "Films directed table itself; era boundaries from the career "
            "headings on the Howard Hawks article; genres, runtimes, release "
            "dates and alternate-version lengths from each film's own "
            "article.",
        ],
        "sections": sections,
    }

    out = prop.write(p)
    print("wrote %s — %d films, %d minutes, %.2f hours"
          % (out.name, len(items), mins, hours))
    for s in sections:
        print("   %-28s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))
    print("   not shipped: %s"
          % "; ".join("%s (%d) %s" % (f["t"], f["year"], f["tablenote"] or
                                      "segment of O. Henry's Full House")
                      for f in lost + partial + segment))
    print("   shared with other lists: %d films — %s"
          % (len(shared),
             "; ".join("%s: %s" % (t, ", ".join(by_list[t])) for t in by_list)))


if __name__ == "__main__":
    main()
