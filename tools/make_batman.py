#!/usr/bin/env python3
"""Generate properties/batman.json — a curated route through Batman comics.

    python tools/make_batman.py

Batman has no spine. Seventy years, three continuity reboots and two flagship
titles that ran in parallel the whole time; there is no run you can read from
#1 to the end and say you have read Batman. So this is the other kind of list
— the curated route, the way properties/civil-war.json and
properties/hickman-secret-wars.json are curated — and every row is a
collected story rather than an issue: Year One is one row, not four.

Where the cut came from
-----------------------
A curated list has no authority except its sources, so this one names them
and then obeys them. The gate below is re-applied from cached wikitext every
time this file runs, and the build fails if Wikipedia's answer stops matching
the shipped roster.

**A story earns a row when all three of these hold.**

  1. **It has its own Wikipedia article, and that article is about a comic.**
     Machine-checked on the article's infobox: `comic book title`,
     `comics story arc`, `graphic novel` or `comics team and title`. This is
     what makes characters, creators, films, publishers and companies fall
     out on their own — Bane, Jim Aparo, the 1989 film and DC Comics are all
     linked from the same paragraphs and none of them is a story.

  2. **Wikipedia's publication history of Batman names it.** The corpus is
     the four articles that narrate that history and nothing else:
     `Batman` (its Publication history section), `Publication history of
     Batman` (whole), `Batman (comic book)` and `Detective Comics` (their
     Publication history sections). A story qualifies by being wikilinked
     from that narrative. This is the same shape of gate
     tools/make_fps_canon.py uses — significance is something the sources
     assert, not something the author feels.

  3. **It is a finite Batman story rather than a container or a company-wide
     event.** Two mechanical halves:

       * not an ongoing title — the infobox does not declare `ongoing`, its
         `format` does not say "ongoing series", and it is not listed among
         the ongoing series in `List of Batman comics` unless its own
         infobox declares it a limited series. *Batman*, *Detective Comics*,
         *Shadow of the Bat*, *Legends of the Dark Knight*, *Batman and
         Robin* and *Batman Incorporated* are the books the stories were
         printed in, not stories;
       * and Batman's own book — `List of Batman comics`, Wikipedia's Batman
         bibliography, lists it in a title column, or its infobox says it ran
         in *Batman* or *Detective Comics*; and no more of the books it ran
         in sit outside that bibliography than inside it. That last clause is
         what separates a Bat-line crossover from a line-wide DC event:
         Knightfall names five books inside the Batman bibliography and three
         outside it, DC One Million names seven inside and twenty-seven of
         everyone else's. One is a Batman story; the other is an event Batman
         is in.

What the gate threw out, and it hurts
-------------------------------------
  * **Everything before 1986.** Not one pre-Crisis story survives clause 1.
    The publication history names the Golden and Silver Age material by
    character and by creator — Robin's debut, the Julius Schwartz "New Look",
    O'Neil and Adams — and the one story it names outright, "The Secret of
    the Waiting Graves", redirects to the bibliography rather than having an
    article. That is a fact about how Batman was published, not a hole in
    the sources: the self-contained collected story is a Modern Age unit,
    and the list starts where the unit does.
  * **Batman: The Black Mirror.** It has an article and it is the story most
    often named as the best of the last twenty years. Wikipedia's Batman
    publication history does not mention it once. Clause 2 is the clause
    doing the work here, and the honest thing is to leave it out and say so.
  * The same clause cuts **The Man Who Laughs**, **The Cult**, **Gothic**,
    **Mad Love**, **Gotham Central**, **White Knight**, **Year 100** and
    **Three Jokers** — all with their own articles, none named in the
    publication history.
  * **All Star Batman & Robin, the Boy Wonder** has its own heading in
    `Publication history of Batman` and still fails, because its infobox
    calls it an ongoing series and it never finished. Clause 3 does not make
    exceptions for famous.

Rows, weights and spoilers
--------------------------
A row is a collected story: the unit `List of Batman comics` collects and
Wikipedia gives an article. Grant Morrison's and Scott Snyder's runs are
therefore several rows apiece rather than one, and that is Wikipedia's
structuring rather than a choice made here — both runs are documented as a
sequence of separately-titled arcs with separate articles (Batman and Son,
R.I.P., Battle for the Cowl, The Return of Bruce Wayne; Night of the Owls,
Death of the Family, Zero Year, Endgame), not as one article per run.

**No row carries a weight and none ever should.** Comics have no runtimes,
and an issue count is not an hour — WEIGHT = x.w >= 0 ? x.w : 1 means one
weighted row would silently turn every other row into "one hour". Issue
counts go in the row notes instead, where they are information rather than
arithmetic.

Notes say what a story IS — who made it, which issues it is — and never what
happens in it. Several of these are famous for one event apiece and the
whole point of a reading list is to be read first.
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop as P  # noqa: E402
from gwlib import wiki as W  # noqa: E402

SLUG = "batman"
CACHE = P.ROOT / "scratch" / "batman"      # the four source articles
CAND = CACHE / "cand"                      # everything they link to
WP = "https://en.wikipedia.org/wiki/"

# (cached article, the section to read; None reads the whole article)
CORPUS = [
    ("Batman", "Publication history"),
    ("Publication history of Batman", None),
    ("Batman (comic book)", "Publication history"),
    ("Detective Comics", "Publication history"),
]

COMIC_BOX = ("comic book title", "comics story arc", "graphic novel",
             "comics team and title")

# The roster the gate produced when this file was written, keyed by the
# Wikipedia article each row is read from. `main` re-runs the gate and fails
# if the two ever disagree, so an edit upstream surfaces as a build error
# rather than as a silently different list.
#   article, id key, display title, section
ROSTER = [
    ("The Dark Knight Returns", "dkr", "The Dark Knight Returns", "crisis"),
    ("Batman: Year One", "year-one", "Year One", "crisis"),
    ("Batman: Year Two", "year-two", "Year Two", "crisis"),
    ("Batman: Son of the Demon", "son-of-demon", "Son of the Demon", "crisis"),
    ("Batman: The Killing Joke", "killing-joke", "The Killing Joke", "crisis"),
    ("A Death in the Family (comics)", "death-in-family",
     "A Death in the Family", "crisis"),
    ("Gotham by Gaslight", "gaslight", "Gotham by Gaslight", "crisis"),
    ("Arkham Asylum: A Serious House on Serious Earth", "arkham",
     "Arkham Asylum: A Serious House on Serious Earth", "crisis"),
    ("The Return of the Joker", "return-of-joker", "The Return of the Joker",
     "crisis"),

    ("Batman: Knightfall", "knightfall", "Knightfall", "gotham"),
    ("Batman: Contagion", "contagion", "Contagion", "gotham"),
    ("Batman: Legacy", "legacy", "Legacy", "gotham"),
    ("Batman: The Long Halloween", "long-halloween", "The Long Halloween",
     "gotham"),
    ("Batman: Cataclysm", "cataclysm", "Cataclysm", "gotham"),
    ("No Man's Land (comics)", "no-mans-land", "No Man's Land", "gotham"),
    ("Batman: Dark Victory", "dark-victory", "Dark Victory", "gotham"),

    ("Bruce Wayne: Fugitive", "fugitive", "Bruce Wayne: Fugitive", "hush"),
    ("Batman: Hush", "hush", "Hush", "hush"),
    ("Broken City (comics)", "broken-city", "Broken City", "hush"),
    ("Batman: War Games", "war-games", "War Games", "hush"),
    ("Batman: Under the Hood", "under-the-hood", "Under the Hood", "hush"),

    ("Batman: Face the Face", "face-the-face", "Face the Face", "morrison"),
    ("Batman and Son", "batman-and-son", "Batman and Son", "morrison"),
    ("Batman R.I.P.", "rip", "Batman R.I.P.", "morrison"),
    ("Batman: Battle for the Cowl", "battle-cowl", "Battle for the Cowl",
     "morrison"),
    ("Batman: Whatever Happened to the Caped Crusader?", "whatever-happened",
     "Whatever Happened to the Caped Crusader?", "morrison"),
    ("Batman: The Return of Bruce Wayne", "return-bruce-wayne",
     "The Return of Bruce Wayne", "morrison"),

    ("Batman: Night of the Owls", "night-owls", "Night of the Owls", "new52"),
    ("Death of the Family", "death-of-family", "Death of the Family", "new52"),
    ("Batman: Zero Year", "zero-year", "Zero Year", "new52"),
    ("Batman Eternal", "eternal", "Batman Eternal", "new52"),
    ("Batman: Endgame", "endgame", "Endgame", "new52"),
    ("The Dark Knight III: The Master Race (comic)", "dkiii",
     "The Dark Knight III: The Master Race", "new52"),

    ("Joker War", "joker-war", "The Joker War", "rebirth"),
    ("Fear State", "fear-state", "Fear State", "rebirth"),
]

# id, title, first year, last year, sub-tail, intro, source article for the link
SECTIONS = [
    ("crisis", "After Crisis", 1986, 1992,
     "where the modern character starts",
     "Crisis on Infinite Earths wiped the slate in 1985 and the next four "
     "years rebuilt Batman from the ground up — an origin, a future, a "
     "villain's origin and an asylum, mostly by writers who had never worked "
     "on the book before. Nothing here needs anything before it, which makes "
     "this the place to start.",
     "Publication history of Batman"),
    ("gotham", "The Gotham crossovers", 1993, 2000,
     "one long serial across every Bat-book",
     "For most of the nineties the line ran as a single serial: a story "
     "started in one title and finished in another, and the city itself took "
     "more damage each year. Knightfall through No Man's Land is that "
     "sequence in order. The two Loeb and Sale miniseries sit inside the "
     "decade by date and outside it by everything else — they are "
     "self-contained and they read fine alone.",
     "Publication history of Batman"),
    ("hush", "The 21st century opens", 2001, 2005,
     "the star-artist years",
     "The line stops crossing over and starts hiring: Jim Lee, Eduardo "
     "Risso, Brian Azzarello. Two of these are twelve-issue arcs in the main "
     "title with one artist each, which had not happened in a decade.",
     "Batman (comic book)"),
    ("morrison", "One Year Later, and Morrison", 2006, 2010,
     "Morrison's run, and the two that frame it",
     "Grant Morrison took the book in 2006 and did not let go until 2013. "
     "Wikipedia documents that run as a sequence of separately-titled arcs "
     "with separate articles rather than as one run, so it is several rows "
     "here rather than one. Face the Face is the relaunch that clears the "
     "board for it; the Gaiman two-parter is a standalone that runs "
     "alongside.",
     "Batman (comic book)"),
    ("new52", "The New 52", 2011, 2015,
     "Snyder and Capullo, and a second Miller sequel",
     "DC restarted its whole line in 2011 and put Scott Snyder and Greg "
     "Capullo on Batman #1. Their run is the last time the character had one "
     "definitive book, and it is broken into arcs here for the same reason "
     "Morrison's is. Batman Eternal is the weekly that ran beside it.",
     "Publication history of Batman"),
    ("rebirth", "Rebirth and after", 2016, 2099,
     "as far as the sources go",
     "The publication history thins out here — recent years are documented "
     "by creator rather than by story, and only two arcs since 2016 clear "
     "the gate. Read that as the sources not having settled yet rather than "
     "as a verdict on the comics.",
     "Batman (comic book)"),
]


# --------------------------------------------------------------- wikitext --
def text(page, cache=None):
    """Cached wikitext. scratch/batman/fetch.py primes the cache in bulk;
    anything missing is fetched here so the generator stays re-runnable."""
    t = W.wikitext(page, cache_dir=str(cache or CACHE))
    assert t, "no Wikipedia article: %r" % page
    return t


def strip_refs(t):
    # self-closing refs first: <ref name=x /> ... <ref>y</ref> would otherwise
    # let the non-greedy match swallow a whole section heading
    t = re.sub(r"<ref[^>]*/>", "", t)
    return re.sub(r"<ref(?![^>]*/>).*?</ref>", "", t, flags=re.S)


def split_sections(t):
    parts = re.split(r"^(=+)\s*(.*?)\s*\1\s*$", t, flags=re.M)
    out = [("(lead)", 0, parts[0])]
    for i in range(1, len(parts), 3):
        out.append((parts[i + 1], len(parts[i]), parts[i + 2]))
    return out


def corpus_text(page, head):
    t = strip_refs(text(page))
    if head is None:
        return t
    keep, lvl = [], None
    for name, depth, body in split_sections(t):
        if lvl is None:
            if head.lower() in name.lower():
                lvl = depth
                keep.append(body)
            continue
        if depth <= lvl:
            break
        keep.append(body)
    assert keep, "%s has no %r section any more" % (page, head)
    return "\n".join(keep)


def wikilinks(t):
    out = []
    for m in re.finditer(r"\[\[([^\]|#]+)(?:\|[^\]]*)?\]\]", t):
        tgt = m.group(1).strip()
        if not tgt.startswith(("File:", "Image:", "Category:", "wikt:")) \
                and tgt not in out:
            out.append(tgt)
    return out


def infobox(t):
    """(kind, fields) for the article's first infobox."""
    m = re.search(r"\{\{\s*Infobox\s+([A-Za-z ]+)", t)
    if not m:
        return None, {}
    box = re.sub(r"<!--.*?-->", "", t[m.start():m.start() + 4000], flags=re.S)
    fields = {}
    for fm in re.finditer(r"^\s*\|\s*([a-zA-Z0-9_ ]+?)\s*=[ \t]*(.*?)"
                          r"(?=\n\s*\|\s*[a-zA-Z0-9_ ]+\s*=|\|\s*[a-zA-Z0-9_-]+"
                          r"\s*=|\n\s*\}\})", box, re.M | re.S):
        fields[fm.group(1).strip()] = fm.group(2).strip()
    return m.group(1).strip().lower(), fields


def undab(t):
    """Drop a Wikipedia disambiguator so a redirect and its target match."""
    return re.sub(r"\s*\((?:comic|comics|comic book|DC Comics)\)$", "", t)


# ------------------------------------------------------------ the sources --
def bibliography():
    """(ongoing, anywhere) — wikilinks in the first (Title) cell of the rows
    of every table in List of Batman comics, and of its Ongoing series table
    alone. Notes cells are excluded on purpose: half the creators in comics
    are linked from a footnote in that article."""
    t = strip_refs(text("List of Batman comics"))
    ongoing, anywhere = set(), set()
    for name, _d, body in split_sections(t):
        is_ongoing = name.strip().strip("'") == "Ongoing series"
        for row in body.split("\n|-"):
            cells = [l for l in row.split("\n")
                     if l.startswith("|") and not l.startswith("|}")]
            if not cells:
                continue
            for tgt in wikilinks(cells[0]):
                anywhere.add(undab(tgt))
                if is_ongoing:
                    ongoing.add(undab(tgt))
    assert len(ongoing) > 30 and len(anywhere) > 120, \
        "the bibliography parse collapsed: %d ongoing, %d total" \
        % (len(ongoing), len(anywhere))
    return ongoing, anywhere


def collected_in():
    """title -> the 'Material collected' cell of its collected-editions row.
    The only place the issue range lives for a story whose article carries no
    `titles` field (Year One, Batman R.I.P.)."""
    t = strip_refs(text("List of Batman comics"))
    out = {}
    for _name, _d, body in split_sections(t):
        for row in body.split("\n|-"):
            cells, cur = [], None
            for line in row.split("\n"):
                if line.startswith("|}") or line.startswith("!"):
                    continue
                if line.startswith("|"):
                    if cur is not None:
                        cells.append(cur)
                    cur = line[1:]
                elif cur is not None:
                    cur += " " + line
            if cur is not None:
                cells.append(cur)
            if len(cells) < 2:
                continue
            for tgt in wikilinks(cells[0]):
                got = W.clean(cells[1])
                if got and undab(tgt) not in out:
                    out[undab(tgt)] = got
    return out


def gate():
    """{article the gate admits: every title that redirects to it here}.

    The alias set matters: the four source articles link the same story
    under different names (Batman article says "A Death in the Family
    (comics)", the publication history says "Batman: A Death in the
    Family"), and counting sources per name instead of per story would
    quietly halve every star."""
    cited = set()
    for page, head in CORPUS:
        cited |= set(wikilinks(corpus_text(page, head)))
    assert len(cited) > 250, "the corpus parse collapsed: %d links" % len(cited)

    bib_ongoing, bib_any = bibliography()
    keep, canonical = {}, {}
    for tgt in sorted(cited):
        t = W.wikitext(tgt, cache_dir=str(CAND))
        if not t:
            continue
        kind, fx = infobox(t)
        if kind not in COMIC_BOX:                       # clause 1
            continue
        lead = t[:400]
        if lead in canonical:                           # a redirect to a keeper
            if canonical[lead] in keep:
                keep[canonical[lead]].add(tgt)
            continue
        canonical[lead] = tgt

        fmt = (fx.get("format", "") + " " + fx.get("schedule", "")).lower()
        limited = fx.get("limited", "").strip().lower() in ("y", "yes")
        container = (fx.get("ongoing", "").strip().lower() in ("y", "yes")
                     or "ongoing series" in fmt
                     or (undab(tgt) in bib_ongoing and not limited))

        ran_in = wikilinks(re.sub(r"\s+", " ", fx.get("titles", "")))
        inside = [x for x in ran_in if undab(x) in bib_any]
        outside = [x for x in ran_in if undab(x) not in bib_any]
        bat = (undab(tgt) in bib_any
               or bool({"Batman (comic book)", "Detective Comics"} & set(ran_in)))
        if container or not bat or len(inside) < len(outside):   # clause 3
            continue
        keep[tgt] = {tgt}
    return keep


# ------------------------------------------------------------- row fields --
JUNK = re.compile(r"\d|collapsible|\blist\b|\bvol\b|issues?\b|:", re.I)


def names(v, cap=2):
    """A creator field down to at most `cap` names plus 'and others'.

    Infobox credit fields in comics articles are a swamp: per-issue
    breakdowns, {{collapsible list}}, bolded run labels, a parenthetical
    naming the title each writer covered. Anything that is not plainly a
    person's name is dropped rather than guessed at."""
    v = re.sub(r"\|.*$", "", W.clean(v or ""))
    v = re.sub(r"\([^)]*\)", "", v)
    v = re.sub(r"Issues?[\d\s,%s-]*:" % DASH, " ", v, flags=re.I)
    parts, seen = [], set()
    for p in re.split(r"[,*]|\band\b", v):
        p = p.strip(" .;:'\"")
        if not p or len(p) > 40 or JUNK.search(p) or p.lower() in seen:
            continue
        seen.add(p.lower())
        parts.append(p)
    if not parts:
        return ""
    if len(parts) > cap:
        return ", ".join(parts[:cap]) + " and others"
    if len(parts) == 2:
        return "%s and %s" % tuple(parts)
    return parts[0]


def credits(fx):
    """writers, then the artist — but never the same person twice, and never
    a second 'and others' on a crossover with a dozen of each."""
    who = names(fx.get("writers"))
    art = names(fx.get("artists") or fx.get("pencillers"), cap=1)
    if not who:
        return art
    if not art or art.endswith("and others") and who.endswith("and others"):
        return who
    if art.split(" and ")[0].lower() in who.lower():
        return who
    return "%s with %s" % (who, art)


DASH = "–"


def endash(t):
    t = re.sub(r"#(\d+)\s*-\s*#?(\d+)", r"#\1%s\2" % DASH, t)
    return re.sub(r"(\d)\s*-\s*(\d)", r"\1%s\2" % DASH, t)


def shortdesc(t):
    m = re.search(r"\{\{\s*[Ss]hort description\s*\|([^}|]*)", t)
    return (m.group(1) if m else "").lower()


def ran_in(kind, fx, raw_page, collected, article):
    """What the story physically is, in the fewest honest words: the issues
    of the book it ran in, or the shape of the object it was published as."""
    raw = re.sub(r"\s+", " ", fx.get("titles", ""))
    if raw:
        chunks = re.split(r"\*|<br\s*/?>|(?<=\d),(?=\s*(?:''|\[\[|[A-Z]))", raw)
        cleaned = [W.clean(c).strip(" ,;").replace("; ", ", ")
                   for c in chunks if c.strip()]
        # a book counts when the source gives issue numbers for it, which is
        # every entry bar the occasional unnumbered one-shot
        cleaned = [c for c in cleaned if re.search(r"[#\s]\d", c)]
        assert cleaned, "cannot read the issue list of %s: %r" % (article, raw[:70])
        spine = next((c for c in cleaned if re.match(r"Batman [#(\d]", c)), None) \
            or next((c for c in cleaned
                     if re.match(r"Detective Comics [#(\d]", c)), None) \
            or next((c for c in cleaned if c.startswith("Batman")), None) \
            or cleaned[0]
        if "#" not in spine:
            spine = re.sub(r"\s(\d)", r" #\1", spine, count=1)
        rest = len(cleaned) - 1
        if rest:
            return "%s, and %d other book%s" % (endash(spine), rest,
                                                "" if rest == 1 else "s")
        return endash(spine)
    if fx.get("1shot", "").strip().lower() in ("y", "yes"):
        return "a one-shot"
    if kind == "graphic novel":
        return "a graphic novel"
    n = re.sub(r"\D", "", fx.get("issues", ""))
    if n:
        limited = fx.get("limited", "").strip().lower() in ("y", "yes")
        return "a %s-issue %s" % (
            n, "miniseries" if limited and int(n) <= 12 else "series")
    sd = shortdesc(raw_page)
    for shape in ("graphic novel", "one-shot"):
        if shape in sd:
            return "a " + shape
    got = collected.get(undab(article))
    if got and "#" in got:
        return endash(got)
    return ""


def years(fx, article):
    a = fx.get("startyr", "").strip()
    if not a:
        m = re.search(r"(19|20)\d{2}", fx.get("date", ""))
        a = m.group(0) if m else ""
    assert re.match(r"^(19|20)\d{2}$", a or ""), \
        "no start year parsed for %s (%r)" % (article, fx.get("date", "")[:50])
    b = fx.get("endyr", "").strip()
    if not b:
        seen = re.findall(r"(?:19|20)\d{2}", fx.get("date", ""))
        b = seen[-1] if seen else a
    assert re.match(r"^(19|20)\d{2}$", b), \
        "no end year parsed for %s (%r)" % (article, fx.get("date", "")[:50])
    return int(a), int(b)


MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


def span(a, b):
    """1986 · 1999–2000 · 2013–14 — a two-digit tail unless it crosses a
    century, where it would read as going backwards."""
    if a == b:
        return str(a)
    return "%d%s%s" % (a, DASH, b if a // 100 != b // 100 else "%02d" % (b % 100))


def start_month(fx):
    m = fx.get("startmo", "").strip() or fx.get("date", "")
    for i, name in enumerate(MONTHS):
        if re.search(name, m):
            return i + 1
    return 0


# ------------------------------------------------------------------ main --
def main():
    admitted = gate()
    declared = {a for a, _k, _t, _s in ROSTER}
    assert set(admitted) == declared, (
        "the gate no longer agrees with the shipped roster.\n"
        "  gained: %s\n  lost:   %s"
        % (sorted(set(admitted) - declared), sorted(declared - set(admitted))))

    cited_by = {}
    for page, head in CORPUS:
        for tgt in wikilinks(corpus_text(page, head)):
            cited_by.setdefault(tgt, set()).add(page)

    collected = collected_in()
    rows = []
    for article, key, title, sec in ROSTER:
        raw_page = text(article, CAND)
        kind, fx = infobox(raw_page)
        assert kind in COMIC_BOX, (article, kind)
        a, b = years(fx, article)
        assert 1935 <= a <= b <= 2030, "impossible years for %s: %d-%d" % (
            article, a, b)
        where = ran_in(kind, fx, raw_page, collected, article)
        assert where, "nothing to say about what %s is" % article
        note = P.join_bits(credits(fx), where)
        assert note, article
        row = {"id": "bat-" + key, "t": title,
               "n": span(a, b),
               "note": note, "sec": sec, "y0": a, "y1": b,
               "m": start_month(fx),
               "srcs": len(set().union(*(cited_by.get(alias, set())
                                         for alias in admitted[article])))}
        # how many of the four articles that tell the history stop to name it
        if row["srcs"] >= 4:
            row["star"] = 2
        elif row["srcs"] == 3:
            row["star"] = 1
        rows.append(row)

    assert len({r["id"] for r in rows}) == len(rows), "duplicate ids"

    sections, placed = [], 0
    for sid, stitle, lo, hi, tail, intro, src in SECTIONS:
        got = sorted([r for r in rows if r["sec"] == sid],
                     key=lambda r: (r["y0"], r["m"], r["t"]))
        assert got, "empty section %s" % sid
        for r in got:
            assert lo <= r["y0"] <= hi, \
                "%s (%d) does not belong to %s (%d-%d)" % (r["t"], r["y0"],
                                                           sid, lo, hi)
        ys = [r["y0"] for r in got]
        assert ys == sorted(ys), "%s is out of publication order" % sid
        placed += len(got)
        sections.append({
            "id": sid, "title": stitle,
            "sub": "%s · %s" % (span(ys[0], max(r["y1"] for r in got)), tail),
            "intro": intro,
            "links": [{"label": src, "url": WP + src.replace(" ", "_")}],
            "items": [{k: v for k, v in r.items()
                       if k in ("id", "t", "n", "note", "star")} for r in got],
        })
    assert placed == len(rows), "%d rows, %d placed" % (len(rows), placed)
    sections[0]["open"] = True

    # All or none, and here it is none: an issue count is not an hour, and
    # WEIGHT = x.w >= 0 ? x.w : 1 would turn every unweighted row into one.
    assert not any("w" in x for s in sections for x in s["items"]), \
        "a weight got onto a row"

    accent, accent_dark = "#1B2436", "#D8B740"
    taken = {}
    for f in sorted((P.ROOT / "properties").glob("*.json")):
        if f.stem in (SLUG, "index", "search"):
            continue
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            continue
        taken[(d.get("accent"), d.get("accentDark"))] = f.stem
    assert (accent, accent_dark) not in taken, \
        "accent pair already used by %s" % taken.get((accent, accent_dark))

    starred = sum(1 for s in sections for x in s["items"] if x.get("star"))
    blurb = ("The stories Wikipedia's publication history of Batman stops to "
             "name, from The Dark Knight Returns to Fear State — collected "
             "stories rather than issues, sectioned by era.")
    assert not re.search(r"\d", blurb), "no counts in the blurb (CLU-190)"

    prop = {
        "slug": SLUG,
        "title": "Batman",
        "subtitle": "a reading order",
        "kind": "comics",
        # Batman is as famous as fiction gets and the comics are the least
        # famous part of him — most people know the films. That is the band
        # just under the flagship franchise lists rather than inside it.
        "popularity": 72,
        "year": "%d%s%d" % (min(r["y0"] for r in rows), DASH,
                            max(r["y1"] for r in rows)),
        "blurb": blurb,
        "unit": {"one": "story", "many": "stories"},
        "verb": {"base": "read", "past": "read", "ing": "reading"},
        "itemOrder": "number-first",
        "accent": accent,
        "accentDark": accent_dark,
        "tiers": False,
        "notes": [
            ["This is a route, not a run.",
             "There is no Batman run to read start to finish. Seventy years, "
             "three reboots and two flagship titles running in parallel the "
             "whole time — so this is the curated kind of list, and every "
             "row is a collected story rather than an issue. Year One is one "
             "row, not four."],
            ["What earns a row, and it is not taste.",
             "Three things have to be true at once. The story has its own "
             "Wikipedia article and that article is about a comic rather "
             "than a character, a creator or a film. Wikipedia's "
             "publication history of Batman names it — the four "
             "articles that tell that history are “Batman”, "
             "“Publication history of Batman”, “Batman "
             "(comic book)” and “Detective Comics”, and a "
             "story qualifies by being linked from their publication-history "
             "narrative. And it is a finite Batman story: not an ongoing "
             "title, which is the book stories were printed in rather than a "
             "story, and not a company-wide DC event that Batman merely "
             "appears in. The generator re-runs that test from cached "
             "wikitext every time and refuses to build if the answer has "
             "changed."],
            ["It starts in 1986, and that is the gate talking.",
             "Not one pre-Crisis story survives. The publication history "
             "names the Golden and Silver Age by character and by creator "
             "rather than by story, and the one story it does name outright "
             "has no article of its own. That is a fact about how Batman was "
             "published — the self-contained collected story is a "
             "Modern Age unit — rather than a hole in the list, and it "
             "seemed better to say so than to quietly hand-pick a Bronze Age "
             "section."],
            ["Some famous absences, named on purpose.",
             "The Black Mirror has its own article and is the story most "
             "often called the best of the last twenty years; Wikipedia's "
             "publication history never mentions it. The same clause cuts "
             "The Man Who Laughs, The Cult, Gothic, Mad Love, Gotham "
             "Central, White Knight and Three Jokers. All Star Batman & "
             "Robin has its own heading in the publication history and still "
             "fails, because it is an ongoing series that never finished. "
             "Following the sources when it is inconvenient is the whole "
             "point of naming them."],
            ["No hours, on any row.",
             "Comics have no runtimes and an issue count is not an hour, so "
             "nothing here is weighted — it is all or none, and one "
             "weighted row would quietly turn every other row into an hour. "
             "The issue counts are in the row notes instead, where they are "
             "information rather than arithmetic: what each story is, which "
             "issues of which books, and how many other books it ran "
             "through."],
            ["Starred rows, and spoilers.",
             "A star means three of the four source articles stop to name "
             "that story; two stars means all four do. Only %d rows clear "
             "that, and the star is a measure of how much the sources "
             "talk about a story rather than of how good it is. The notes "
             "say who made a story and which issues it is, never what "
             "happens in it — several of these are famous for a single "
             "event apiece, and a reading list is meant to be read first."
             % starred],
            "Contents and the gate from Wikipedia's “Publication "
            "history of Batman”, “Batman”, “Batman "
            "(comic book)” and “Detective Comics”; issue "
            "ranges, creators and dates machine-read from each story's own "
            "article and from “List of Batman comics”.",
        ],
        "sections": sections,
    }

    P.write(prop)
    print("wrote %s.json" % SLUG)
    print("  %d sections, %d stories, %d starred, 0 weighted"
          % (len(sections), len(rows), starred))
    for s in sections:
        print("   %-28s %2d  %s" % (s["title"][:28], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
