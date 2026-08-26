#!/usr/bin/env python3
"""Generate properties/martial-arts.json.

    python tools/make_martial-arts.py

"A classic" is a verdict, and this catalogue does not ship verdicts. The
request this list answers came with its own warning — kung fu and martial
arts, "maybe just the classics, deep, terrible depths there" — and the depths
are real: this is a genre that made thousands of interchangeable films and a
few dozen that matter. So this file never decides which is which. It records
how many of nine sources singled a film out, prints the count on every row,
and lets a reader argue with the count rather than with us.

The gate
--------
**A film is here only if it is a martial arts film made in Hong Kong, Taiwan
or mainland China, and one of the six surveys named it, or the three award
juries did more than nominate it once.** Nothing else qualifies a row, and
nothing that cleared the gate was dropped for taste.

The nine sources are two different kinds of thing, and the gate treats them
differently on purpose.

**Six surveys**, each of which looked back over a whole history and picked out
what mattered:

  * **The Best 100 Chinese Motion Pictures** — the Hong Kong Film Awards
    Association's 2005 canon of a century of Chinese cinema, voted by a panel
    of 101 filmmakers, critics and scholars and printed in rank order. It is
    the closest thing this cinema has to a native canon.
  * **Five written histories** — Wikipedia's *Hong Kong action cinema*,
    *Kung fu film*, *Wuxia*, *Cinema of Hong Kong* and *Shaw Brothers
    Studio*. A film counts where the article names it in its body text, which
    is how those articles write a landmark.

**Three juries**, each of which picks about five films out of one year:

  * the Hong Kong Film Award for **Best Film** (1982–), and the **Best Action
    Choreography** awards of both the Hong Kong Film Awards (1983–) and
    Taiwan's Golden Horse (1992–), winners and nominees alike. Action
    choreography is the only award category in world cinema given for the
    craft that defines this genre.

One survey is enough because a survey is already the long view. One jury
nomination is not, because a jury names five films every year whatever the
year was like — that is korean-cinema's lesson and it holds here. Two
nominations, or one outright win, is where an award record stops being one
jury's pick of one year. **The win clause is there for consistency rather
than for scale**: it adds seven rows, and without it this list would admit a
film two juries merely nominated while refusing one that actually won the
prize for the very craft the list is about.

Why the histories are sources at all
-------------------------------------
Because without them the list has no 1960s and no 1970s. **Every award that
honours this genre postdates the genre's founding decade.** The Hong Kong
Film Awards began in 1982, the choreography award in 1983, the Golden Horse
equivalent in 1992; the 2005 canon reaches back but is a canon of Chinese
cinema rather than of martial arts, and only nineteen of its hundred are
martial arts films at all. Gate on the canon and the juries alone and Enter
the Dragon, The 36th Chamber of Shaolin, Come Drink with Me, Five Deadly
Venoms and King Boxer are all absent — an unusable answer to a question about
kung fu classics. The histories are tertiary sources, which is said on the
page rather than hidden, and they are the only per-film record that reaches
1966.

They cost something too, and it is stated on the page: a written history
mentions a film for all sorts of reasons, so *Naked Killer*, *Kung Fu VS
Acrobatic* and *Shanghai Noon* ride in on one mention apiece.

Scope: Chinese-language cinema, and why not the whole world
-----------------------------------------------------------
"Kung fu / martial arts" could have meant the genre worldwide — chanbara,
Ong-Bak, The Raid, Hollywood. It does not here, and the reason is the sources
rather than taste. Every per-entry record that reaches this genre is Chinese:
the only native canon, the only awards for its own craft, the histories that
reach back before those awards. There is no Thai or Indonesian equivalent at
all, so a list claiming the whole genre would have had a hole exactly where
its modern non-Chinese half lives, while Japan would have arrived through
Criterion and a completely different kind of source. The samurai film is a
neighbouring tradition with its own canon and its own list in this catalogue;
the two pair rather than duplicate, and the ids are what make that work.

What the scope costs, plainly: no Seven Samurai, no Yojimbo, no Zatoichi, no
Lone Wolf and Cub, no Ong-Bak, no The Raid, no Kill Bill, no Karate Kid.

The one asymmetry in the panel, and the check that settled it
---------------------------------------------------------------
Hong Kong's Best Film award is a jury here and Taiwan's Best Narrative
Feature is not, which looks arbitrary until you count. That record carries 168
linked films across sixty years and eight of them are martial arts films, and
seven of those eight are already on this list through something else. Adding
it would change exactly one row: **The Assassin** (2015), Hou Hsiao-hsien's
wuxia film, which is nominated for the Golden Horse's choreography prize and
loses it. Adding a source that moves one film is tuning the gate to a result,
so it was not added — and The Assassin is named on the page as the casualty
instead, which is the honest version of the same information.

Wikipedia's own "Martial arts film" was on the panel and was taken off for the
same reason: it is the genre's worldwide umbrella article, everything Chinese
it names the five other histories name too, and its unique contributions are
American. That is a rule about a source's scope, not about the films — but it
costs One Armed Boxer (1972), which nothing else names.

Genre and region are the film's own article, not ours
------------------------------------------------------
A row's genre comes from the categories on its own Wikipedia article — the
martial arts, kung fu, wuxia and swordplay categories — with Wikidata's genre
claim as a fallback. That is what keeps Infernal Affairs, The Killer, A Better
Tomorrow and The Mission off a martial arts list without anybody here ruling
on it, all four of which four or more of these sources name.

Region is the same idea and had to be tightened twice. A category naming a
LANGUAGE is not a production country — "Chinese-language American films" sits
on both Kill Bill and Rush Hour — so only a `<year> Hong Kong/Chinese/
Taiwanese films` category counts, or Wikidata's own country of origin. Both
are needed: Wikidata records Enter the Dragon as American and nothing else,
which is wrong about the first US–Hong Kong co-production ever made and would
have cut the most famous film in the genre.

Four kinds of row cannot exist here, each for a stated reason:
  * **A lost film is not watchable.** The Burning of the Red Lotus Monastery
    (1928) is the founding wuxia hit and every print of it and its eighteen
    sequels is gone.
  * **A serial is not one film.** The Swordswoman of Huangjiang (1930) ran to
    thirteen parts; cult-classics refused Fantômas on the same rule.
  * **Neither is a two-parter.** The canon's no. 19, A Chinese Odyssey, is two
    films shot back to back and released months apart, and its infobox prints
    a running time for each; one row could only be half of it.
  * **A film with no running time anywhere cannot be weighted**, and this list
    is weighted, so a guessed number is worse than an absence. Two rows take
    the figure from Wikidata because their own infobox leaves the field empty,
    which is stated on the page — dropping a canon selection over a blank
    template field would have been the worse answer.

Wikidata ids
------------
Every row carries `q`, which build.py groups on ahead of title and year, and
every id was resolved from the wikilink the source itself printed — never from
a title. That matters more here than anywhere else in the catalogue, because
these films have three and four English names apiece: Drunken Master II is The
Legend of Drunken Master, Dragon Inn is Dragon Gate Inn, King Boxer is Five
Fingers of Death, and the romanisations move under them as well. Every
alternate name a source gave rides in the row note as "also …". Each id is
then checked against its item's P31 and P577: an item that is not a film, or
whose publication dates miss the row's year by more than a year, loses its id
rather than risk ticking a film nobody watched.

Two source defects worth naming, both found and both handled:
  * **A film named in italics but never linked cannot carry an id.** Hong Kong
    action cinema credits "Chinese Boxer (1970)" with launching the kung fu
    boom and does not link it, and Lau Kar-leung's The Spiritual Boxer is
    unlinked in the same paragraph. Both are absent rather than resolved by
    title, because looking a title up is exactly how the Korean build got a
    1960 film for a 1956 row.
  * **A winner with no article is invisible to a parse of links.** Downtown
    Torpedoes won the 1998 Hong Kong choreography award and Nezha the 2021
    Golden Horse one; neither has an English article, so neither year yields a
    winner. The generator asserts that this happens exactly twice.

Weights
-------
Every row is weighted and no figure was invented. Running times come from each
film's own English Wikipedia infobox rather than from Wikidata's P2047, per
HOW-IT-WORKS — and this is the genre where that matters most, because the same
film exists as a Hong Kong release, a Mandarin export version and a shorter
dubbed American cut. One row per film, the first figure the infobox prints is
what the bar measures, and any other cut is named in the note.

Data: scratch/agent-ma/{fetch,parse,collect,gate,runtimes,bake}.py
      -> tools/data/martial-arts.json
"""
import collections
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop as P  # noqa: E402

SLUG = "martial-arts"
DATA = pathlib.Path(__file__).resolve().parent / "data" / ("%s.json" % SLUG)

# The gate. A survey is the long view and counts on its own; a jury picks five
# films out of one year, so one nomination is not a verdict — but one win is.
MIN_JURIES = 2

# The nine, in the order the notes name them.
SURVEYS = [
    ("hkfa100", "the Best 100 Chinese Motion Pictures"),
    ("hkaction", "Hong Kong action cinema"),
    ("kungfu", "Kung fu film"),
    ("wuxia", "Wuxia"),
    ("hkcinema", "Cinema of Hong Kong"),
    ("shaw", "Shaw Brothers Studio"),
]
JURIES = [
    ("hkfa_bestfilm", "the Hong Kong Film Award for Best Film"),
    ("hkfa_choreo", "the Hong Kong Film Award for Best Action Choreography"),
    ("gh_choreo", "the Golden Horse Award for Best Action Choreography"),
]
PANEL_KEYS = [k for k, _n in SURVEYS] + [k for k, _n in JURIES]

ACCENT, ACCENT_DARK = "#96341C", "#E8825E"

# Genre, from the film's own article. Categories first because they are
# per-article and maintained by whoever wrote the article; Wikidata's genre
# claim is the fallback.
GENRE_CAT = re.compile(r"martial arts|kung fu|wuxia|swordplay", re.I)
GENRE_Q = re.compile(r"martial arts|wuxia|kung fu", re.I)
# A production country, never a language: "Chinese-language American films"
# sits on Kill Bill and on Rush Hour and says nothing about where either was
# made. Wikidata's country is the other half, because these two disagree in
# both directions — see the docstring.
REGION_CAT = re.compile(r"^(19|20)\d{2} (Hong Kong|Chinese|Taiwanese) films$")
REGION_Q = {"Hong Kong", "British Hong Kong", "China", "Taiwan",
            "People's Republic of China", "Republic of China"}
LOST_CAT = re.compile(r"\blost (film|silent)", re.I)
SERIAL_CAT = re.compile(r"^Film serials", re.I)

# Where a row's region label comes from, most specific first.
REGION_OF = [("Hong Kong", re.compile(r"\bHong Kong\b")),
             ("Taiwan", re.compile(r"\bTaiwan(ese)?\b")),
             ("China", re.compile(r"\bChin(a|ese)\b"))]

# The eras. Every label is a heading or subheading of Wikipedia's "Hong Kong
# action cinema"; the cut years are ours, because "late 1960s" is not a
# boundary a program can use, and each one is set at a film that article
# itself calls the turn. ANCHORS holds those sentences and the build fails if
# the article stops saying them.
ERAS = [
    ("early", "Before the new school", None, 1964),
    ("newschool", "“New School” wuxia", 1965, 1969),
    ("kungfuwave", "The kung fu wave", 1970, 1979),
    ("reinvent", "Reinventing action", 1980, 1989),
    ("wirework", "The wire-work wave", 1990, 1996),
    ("recent", "After the handover", 1997, None),
]

ANCHORS = [
    "inaugurated a new generation of wuxia films, starting with Xu "
    "Zenghong's ''Temple of the Red Lotus'' (1965)",
    "''Chinese Boxer'' (1970), starring and directed by Jimmy Wang Yu, is "
    "widely credited with launching the kung fu boom",
    "In the 1980s, he and many colleagues would forge a slicker, more "
    "spectacular Hong Kong pop cinema",
    "As the triad films petered out in the early 1990s, period martial arts "
    "returned as the favored action genre",
    "The Hong Kong film industry has been in a severe",
]

INTROS = {
    "early": "Before any of it. The wuxia film is a Shanghai invention of the "
             "1920s, adapted from the martial-chivalry serials the newspapers "
             "were printing, and almost none of it survives — the genre's "
             "founding hit and its eighteen sequels are lost prints. What is "
             "here is what can still be watched.",
    "newschool": "Shaw Brothers restarts the swordplay film in colour and in "
                 "Mandarin, and the action picture moves to the centre of an "
                 "industry that had been built on romances and musicals. "
                 "Chang Cheh and King Hu are the two directors this section "
                 "is really about, and most of what follows is downstream of "
                 "these few years.",
    "kungfuwave": "Swords give way to fists. The kung fu film takes over the "
                  "decade, Bruce Lee turns it into a worldwide business in "
                  "four films, and the same studios turn out the hundreds of "
                  "cheap imitations that gave the genre its reputation. The "
                  "biggest section here, and the one the gate works hardest "
                  "on.",
    "reinvent": "Jackie Chan takes the fight out of the training hall and "
                "into traffic, Tsui Hark and Cinema City bring effects and "
                "budgets, and John Woo replaces the fists with guns "
                "altogether. Fewer martial arts films get made and the ones "
                "that do are bigger.",
    "wirework": "Period martial arts return on wires and on much larger "
                "budgets, adapted from the more fantastical wuxia novels. "
                "This is the Hong Kong the rest of the world was about to "
                "start copying, and the last stretch before the industry's "
                "slump.",
    "recent": "The industry falls into a slump it has never really left, and "
              "the genre survives by going bigger and by co-producing with "
              "the mainland. The written histories stop around 2004, so this "
              "section leans on the award records more than any other — read "
              "the counts here as thinner evidence than the ones above.",
}

# Asserted rather than hoped for: films any credible answer to "the classics
# of kung fu cinema" has to contain. If an edit breaks one of these the gate
# is wrong and the build should stop rather than be patched around.
CANARIES = [
    ("Enter the Dragon", 1973),
    ("The 36th Chamber of Shaolin", 1978),
    ("Come Drink with Me", 1966),
    ("One-Armed Swordsman", 1967),
    ("A Touch of Zen", 1971),
    ("Drunken Master", 1978),
    ("Five Deadly Venoms", 1978),
    ("The Big Boss", 1971),
    ("Once Upon a Time in China", 1991),
    ("Crouching Tiger, Hidden Dragon", 2000),
]

# Named on the page as excluded, and checked against the data so the claim
# cannot go stale. Each is a martial arts film in the region that the gate
# refuses, with the reason it refuses it.
REFUSED = {
    "Iron Monkey": "one nomination, no win",
    "Shaolin Temple": "one nomination, no win",
    "Duel to the Death": "one nomination, no win",
    "Armour of God": "one nomination, no win",
    "Dragons Forever": "one nomination, no win",
    "Eastern Condors": "one nomination, no win",
    "The Assassin": "one nomination, no win — see the docstring",
}

# The films the sources name in italics without linking them. They cannot
# carry an id and are not resolved by title; named on the page instead.
UNLINKED = ["Chinese Boxer", "The Spiritual Boxer"]

# Named on the page as the cost of counting a written history's mention:
# each is a martial arts film in the region that one history names in passing
# and nothing else touches. Checked against the data, like REFUSED.
ADMITTED_ON_ONE = ["Naked Killer", "Kung Fu VS Acrobatic",
                   "Shanghai Noon"]

# The four the notes say a canon-plus-juries gate would lose. Each has to be
# on this list AND have no jury behind it, or the claim is wrong.
NO_JURY = ["Enter the Dragon", "The 36th Chamber of Shaolin",
           "Come Drink with Me", "Five Deadly Venoms"]

# Sync partners that must still form a group. Ticking Enter the Dragon here
# has to tick it on Bruce Lee's list and on Cult Classics, and a rename or a
# lost id would otherwise break that in silence.
MUST_PAIR = ["criterion", "cult-classics", "best-picture", "bruce-lee",
             "jackie-chan", "jet-li", "donnie-yen"]


def is_film(kinds):
    return any("film" in k.lower() for k in kinds or ())


def bare(title):
    """An article title without its disambiguator."""
    return re.sub(r"\s*\([^()]*\)$", "", title or "").strip()


def straight(t):
    return (t or "").replace("’", "'").replace("‘", "'")


def person(name):
    """A director's name as display text, or nothing.

    Infoboxes on this genre's pages carry citations inside the director field
    and the field capture can stop inside one, so anything that still looks
    like wikitext after cleaning is dropped rather than printed at a reader.
    """
    name = re.split(r"<ref|\{\{", straight(name or ""))[0]
    # <small> survives gwlib's cleaner, and Game of Death's director field is
    # three names with two <small> credits threaded through them.
    name = re.sub(r"<[^>]*>", " ", name)
    # gwlib's cleaner unwraps {{ubl|A|B|C}} to "A|B|C"; a pipe is a list
    # separator there, not punctuation, and four directors of Swordsman
    # shipped as "King Hu|Ching Siu-tung|Tsui Hark|Raymond Lee".
    name = re.sub(r"\s*\|\s*", ", ", name)
    # a parenthetical is a credit, not part of a name: Five Deadly Venoms
    # lists "Leung Ting (Action Director)" and Crime Story two "(action)"
    # co-directors. The name is what ships.
    name = re.sub(r"\s*\([^()]*\)", "", name)
    parts, seen = [], set()
    for p in re.split(r"\s*,\s*", re.sub(r"\s+", " ", name)):
        p = p.strip(" ,;.")
        if p and p.lower() not in seen and not P.WIKI_JUNK.search(p):
            seen.add(p.lower())
            parts.append(p)
    return ", ".join(parts[:4])


def era_of(year):
    for key, _t, lo, hi in ERAS:
        if (lo is None or year >= lo) and (hi is None or year <= hi):
            return key
    raise AssertionError("no era holds %r" % year)


def year_of(x, n):
    """build.py's rule for a film row's sync year."""
    if re.fullmatch(r"(18|19|20)\d{2}", n):
        return n
    ex = str(x.get("y", ""))
    if re.fullmatch(r"(18|19|20)\d{2}", ex):
        return ex
    found = set(re.findall(r"\b((?:18|19|20)\d{2})\b", x.get("note") or ""))
    return found.pop() if len(found) == 1 else None


def catalogue():
    """Every syncable film row already in the catalogue, as build.py sees it:
    (slug, id, normalized title, year or None, q or None, raw title)."""
    out = []
    for f in sorted((P.ROOT / "properties").glob("*.json")):
        if f.name in ("index.json", "search.json", "%s.json" % SLUG):
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        if d.get("secret") or "film" not in (d.get("kind") or ""):
            continue
        for s in d.get("sections", []):
            for x in s.get("items", []):
                y = year_of(x, str(x.get("n", "")))
                q = x.get("q")
                out.append((d["slug"], x["id"], P.normt(x["t"]),
                            int(y) if y else None,
                            q if isinstance(q, str) else None, x["t"]))
    return out


def works(d):
    """One record per film, keyed on the id its own source's wikilink gave.

    Two sources linking two different articles that resolve to one item merge
    here and nowhere else — which is the whole reason ids are resolved from
    links rather than from titles. "One-Armed Swordsman" and "The One-Armed
    Swordsman" are two pages and one film, and a title match would have made
    them two rows and then failed to pair either with anything.
    """
    rows, qids, cats, facts = d["rows"], d["qids"], d["cats"], d["facts"]
    films = {}
    for src, rs in rows.items():
        for r in rs:
            page = r.get("page")
            if not page:
                continue
            q = qids.get(page)
            key = q or "p:" + page
            f = films.setdefault(key, {
                "key": key, "q": q, "pages": [], "titles": [], "src": {},
                "wins": set(), "rank": None, "canon_year": None,
                "canon_region": None, "director": None})
            if page not in f["pages"]:
                f["pages"].append(page)
            t = straight(r.get("t"))
            if t and t not in f["titles"]:
                f["titles"].append(t)
            f["src"].setdefault(r["src"], r.get("award_year") or r.get("year"))
            if r.get("win"):
                f["wins"].add(r["src"])
            if src == "hkfa100":
                f["rank"] = r["rank"]
                f["canon_year"] = r["year"]
                f["canon_region"] = r["region"]
                f["director"] = r["director"]
    for f in films.values():
        cs = []
        for p in f["pages"]:
            cs += cats.get(p, [])
        fa = facts.get(f["q"]) or {}
        f["cats"] = cs
        f["kinds"] = fa.get("p31") or []
        f["genres"] = fa.get("genre") or []
        f["countries"] = fa.get("country") or []
        f["pub_years"] = fa.get("pub_years") or []
        f["p2047"] = fa.get("p2047")
        f["zh"] = fa.get("zh")
        f["is_film"] = is_film(f["kinds"])
        f["martial"] = any(GENRE_CAT.search(c) for c in cs) or \
            any(GENRE_Q.search(g) for g in f["genres"])
        f["region"] = any(REGION_CAT.match(c) for c in cs) or \
            any(c in REGION_Q for c in f["countries"])
        f["lost"] = any(LOST_CAT.search(c) for c in cs)
        f["serial"] = any(SERIAL_CAT.match(c) for c in cs)
        f["year"] = f["canon_year"] or (min(f["pub_years"])
                                        if f["pub_years"] else None)
        f["nsurvey"] = len([k for k in f["src"] if k in dict(SURVEYS)])
        f["njury"] = len([k for k in f["src"] if k in dict(JURIES)])
        f["nwin"] = len(f["wins"])
        f["n"] = f["nsurvey"] + f["njury"]
    return films


def gate(d):
    """(every work, the genre+region pool, the rows that clear the gate)."""
    films = works(d)
    pool = [f for f in films.values()
            if f["is_film"] and f["martial"] and f["region"] and f["year"]
            and not f["lost"] and not f["serial"]]
    keep = [f for f in pool if f["nsurvey"] >= 1
            or f["njury"] >= MIN_JURIES or f["nwin"]]
    return films, pool, keep


def region_label(f):
    """Every place that made the film, in the canon's own order where it has
    one.

    Two mistakes were made here first. Reading the whole category list let a
    LANGUAGE category ("Chinese-language films") label a Hong Kong picture as
    Chinese, so only the year-of-country categories are read now; and taking
    the first match in a fixed order printed "Hong Kong" on A Touch of Zen,
    which the canon's own Region column calls Taiwan. Co-productions get all
    of their places, because that is what they are.
    """
    cr = f["canon_region"] or ""
    hits = [(m.start(), label) for label, rx in REGION_OF
            for m in [rx.search(cr)] if m]
    out = [label for _p, label in sorted(hits)]
    hay = " ; ".join(list(f["countries"])
                     + [c for c in f["cats"] if REGION_CAT.match(c)])
    for label, rx in REGION_OF:
        if label not in out and rx.search(hay):
            out.append(label)
    return "/".join(out) or None


def main():
    d = json.loads(DATA.read_text(encoding="utf-8"))
    rows = d["rows"]

    # ---- the sources are the shape this file describes ---------------------
    canon = rows["hkfa100"]
    assert len(canon) == 103, \
        "the 2005 canon prints %d rows, not the 103 it says" % len(canon)
    assert sorted(r["rank"] for r in canon) == list(range(1, 104))
    assert max(r["year"] for r in canon) == 2002, \
        "the canon's newest selection is no longer 2002"
    for key in PANEL_KEYS:
        assert rows.get(key), "no rows for source %s" % key

    # A jury year with no linked winner means the winning film has no English
    # article — Downtown Torpedoes in 1998, Nezha in 2021. Asserted so a
    # parser regression that quietly lost a whole year's winners is caught.
    blank = []
    for key, _n in JURIES:
        yrs = collections.defaultdict(int)
        for r in rows[key]:
            if r["win"]:
                yrs[r["award_year"]] += 1
        blank += [(key, y) for y in {r["award_year"] for r in rows[key]}
                  if yrs[y] != 1]
    assert sorted(blank) == [("gh_choreo", 2021), ("hkfa_choreo", 1998)], \
        "jury years with no single linked winner moved: %s" % sorted(blank)

    films, pool, gated = gate(d)

    # ---- ids: the source's own link, and only where it holds up ------------
    refused_id = []
    for f in gated:
        ys = f["pub_years"]
        if f["q"] and ys and min(abs(y - f["year"]) for y in ys) > 1:
            refused_id.append((f["titles"][0], f["year"], sorted(ys)))
            f["q"] = None
    qs = [f["q"] for f in gated if f["q"]]
    assert len(qs) == len(set(qs)), \
        "two rows share an id: %s" % [q for q in qs if qs.count(q) > 1][:3]

    # ---- weights are all-or-nothing (CLU-131) ------------------------------
    # A film whose own article prints no running time is not a row. It cannot
    # be weighted from anything but a guess, and one unweighted row on a
    # weighted list silently counts as an hour.
    runtime, unweighable, from_wikidata, multipart = d["runtime"], [], [], []
    for f in list(gated):
        vals = (runtime.get(f["key"]) or {}).get("vals") or []
        if not vals and f["p2047"]:
            # Two infoboxes leave the runtime field empty — Lady Whirlwind
            # and Raining in the Mountain, a canon selection. The
            # infobox is the preferred source, not the only allowed one, and
            # dropping a film the 2005 canon picked because a template field
            # is blank would be a worse answer than citing Wikidata for it.
            vals = [[f["p2047"], "", ""]]
            from_wikidata.append(f["titles"][0])
        if not vals:
            unweighable.append((f["titles"][0], f["year"]))
            gated.remove(f)
            continue
        # "Part 1: 87 minutes / Part 2: 95 minutes" is two films sharing one
        # entry, not one film with two cuts. A Chinese Odyssey is the canon's
        # no. 19 and is refused for the same reason cult-classics refuses the
        # Lord of the Rings row: it cannot be one row with one weight, and it
        # could never pair with anything either.
        if any(re.search(r"\bpart\b", (v[2] if len(v) > 2 else ""), re.I)
               for v in vals):
            multipart.append((f["titles"][0], f["year"]))
            gated.remove(f)
            continue
        f["runtime"], f["rt_label"] = vals[0][0], vals[0][1]
        f["rt_alts"] = [(v[0], v[1]) for v in vals[1:]]
        f["page"] = (runtime.get(f["key"]) or {}).get("page")
        # the film's own infobox first, the canon's director column second:
        # the canon types some names in its own casing (Yuen Woo-Ping,
        # Lau Kar-Leung) and two spellings across one list is the kind of
        # thing a reader notices and nobody can explain
        f["director"] = person((runtime.get(f["key"]) or {}).get("director")) \
            or person(f["director"])
        assert 40 <= f["runtime"] <= 250, \
            "%s runtime %r is not credible" % (f["titles"][0], f["runtime"])

    # ---- titles: the article's name, with every alias the sources gave -----
    # The article title is the tie-break because these sources disagree
    # constantly: the same film arrives as Dragon Inn from one record and
    # Dragon Gate Inn from another. Whichever loses rides in the note, so a
    # reader can find the disc they actually own.
    for f in gated:
        art = bare(f.get("page") or "")
        f["t"] = next((c for c in f["titles"] if P.normt(c) == P.normt(art)),
                      art or f["titles"][0])
        akas, seen = [], {P.normt(f["t"])}
        for a in f["titles"]:
            if P.normt(a) not in seen:
                seen.add(P.normt(a))
                akas.append(a)
        f["akas"] = akas

    # ---- rows --------------------------------------------------------------
    gated.sort(key=lambda f: (f["year"], P.normt(f["t"])))
    entries, used = [], set()
    for f in gated:
        cut = None
        if f["rt_alts"]:
            n, label = f["rt_alts"][0]
            cut = "also %d min%s" % (n, " %s" % label if label else "")
        survey_bit = ("%d of %d surveys" % (f["nsurvey"], len(SURVEYS))
                      if f["nsurvey"] else None)
        jury_bit = None
        if f["njury"]:
            jury_bit = "%d of %d juries" % (f["njury"], len(JURIES))
            if f["nwin"]:
                jury_bit += ", %d won" % f["nwin"]
        base = "ma-%d-%s" % (f["year"], P.slug(f["t"]))
        iid, k = base, 2
        while iid in used:
            iid, k = "%s-%d" % (base, k), k + 1
        used.add(iid)
        x = {"id": iid, "t": f["t"], "n": str(f["year"]),
             "w": round(f["runtime"] / 60.0, 2),
             "note": P.join_bits(
                 survey_bit, jury_bit,
                 ("Best 100 no. %d" % f["rank"]) if f["rank"] else None,
                 f["director"] or None,
                 region_label(f),
                 "%d min" % f["runtime"],
                 cut,
                 "also %s" % ", ".join(f["akas"][:2]) if f["akas"] else None)}
        if f["q"]:
            x["q"] = f["q"]
        if f["rank"]:
            x["star"] = True
        entries.append(dict(x, era=era_of(f["year"]), year=f["year"],
                            runtime=f["runtime"], surveys=f["nsurvey"],
                            juries=f["njury"], wins=f["nwin"],
                            canon=bool(f["rank"]), akas=len(f["akas"]),
                            cuts=len(f["rt_alts"])))

    years = [e["year"] for e in entries]
    assert years == sorted(years), "the roster is out of release order"
    for e in entries:
        assert re.fullmatch(r"(19|20)\d{2}", e["n"]), e["id"]
    total_min = sum(e["runtime"] for e in entries)

    # ---- the sanity checks, on their own merits ----------------------------
    for name, year in CANARIES:
        hit = [e for e in entries
               if P.normt(e["t"]) == P.normt(name) and e["year"] == year]
        assert len(hit) == 1, \
            "%s (%d) is not on this list — the gate is wrong" % (name, year)
    for name in REFUSED:
        assert not [e for e in entries if P.normt(e["t"]) == P.normt(name)], \
            "the notes say %s is excluded and it is not" % name
        assert [f for f in pool if any(P.normt(t) == P.normt(name)
                                       for t in f["titles"])], \
            "the notes name %s as a casualty and it is not even a " \
            "candidate" % name
    for name in ADMITTED_ON_ONE:
        hit = [e for e in entries if P.normt(e["t"]) == P.normt(name)]
        assert len(hit) == 1 and hit[0]["surveys"] == 1 \
            and not hit[0]["juries"], \
            "the notes say %s is here on one mention alone: %s" % (name, hit)
    for name in NO_JURY:
        hit = [e for e in entries if P.normt(e["t"]) == P.normt(name)]
        assert len(hit) == 1 and not hit[0]["juries"] and not hit[0]["canon"], \
            "the notes say a canon-and-juries gate would lose %s" % name
    hist = (P.ROOT / "scratch" / "agent-ma" / "Hong-Kong-action-cinema.wiki")
    if hist.exists():
        src = hist.read_text(encoding="utf-8")
        for claim in ANCHORS:
            assert claim in src, "an era boundary outran its source: %r" % claim
        for t in UNLINKED:
            assert "''%s''" % t in src and "[[%s]]" % t not in src, \
                "%s is linked now — it can carry an id" % t

    # ---- sections ----------------------------------------------------------
    sections = []
    for key, title, lo, hi in ERAS:
        got = [e for e in entries if e["era"] == key]
        assert got, "empty era %s" % key
        assert all((lo is None or e["year"] >= lo)
                   and (hi is None or e["year"] <= hi) for e in got), key
        sections.append({
            "id": key, "title": title,
            "sub": " · ".join([
                ("%d" % got[0]["year"] if got[0]["year"] == got[-1]["year"]
                 else "%d–%d" % (got[0]["year"], got[-1]["year"])),
                "%d film%s" % (len(got), "" if len(got) == 1 else "s"),
                "%d hours" % round(sum(e["runtime"] for e in got) / 60.0)]),
            "intro": INTROS[key],
            "items": [{k: v for k, v in e.items()
                       if k in ("id", "t", "n", "w", "note", "q", "star")}
                      for e in got]})
    sections[2]["open"] = True
    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)) == len(entries)

    # ---- the accent pair is ours alone -------------------------------------
    for f in sorted((P.ROOT / "properties").glob("*.json")):
        if f.name in ("index.json", "search.json", "%s.json" % SLUG):
            continue
        o = json.loads(f.read_text(encoding="utf-8"))
        assert o.get("accent") != ACCENT, \
            "%s already uses accent %s" % (o.get("slug"), ACCENT)
        assert o.get("accentDark") != ACCENT_DARK, \
            "%s already uses accentDark %s" % (o.get("slug"), ACCENT_DARK)

    # ---- the overlaps have to actually group -------------------------------
    # A row carrying both an id and a plain year offers build.py two keys and
    # build.py merges them into ONE group, so groups are counted per row of
    # ours, which is what merging does.
    mine_year = {(P.normt(e["t"]), e["year"]): e["id"] for e in entries}
    mine_keys = {k for k, _y in mine_year}
    mine_q = {e["q"]: e["id"] for e in entries if e.get("q")}
    groups, missed = collections.defaultdict(set), []
    for slug, _iid, key, year, q, raw in catalogue():
        if q and q in mine_q:
            groups[mine_q[q]].add(slug)
        elif (key, year) in mine_year:
            groups[mine_year[(key, year)]].add(slug)
        elif key in mine_keys and year:
            missed.append((raw, slug, year,
                           tuple(sorted(y for k, y in mine_year if k == key))))
    lists_met = {s for v in groups.values() for s in v}
    for slug in MUST_PAIR:
        assert any(slug in v for v in groups.values()), \
            "no sync group forms with %s" % slug
    by_id = {e["id"]: e["t"] for e in entries}
    top_share = max(groups.items(), key=lambda kv: len(kv[1]))

    # ---- figures the notes quote, computed rather than typed ---------------
    oldest, newest = entries[0], entries[-1]
    top = max(entries, key=lambda e: (e["surveys"] + e["juries"]))
    canon_rows = [e for e in entries if e["canon"]]
    jury_only = [e for e in entries if not e["surveys"]]
    survey_only = [e for e in entries if not e["juries"]]
    by_win = [e for e in entries if not e["surveys"] and e["juries"] < 2]
    shortest = min(entries, key=lambda e: e["runtime"])
    longest = max(entries, key=lambda e: e["runtime"])
    biggest = max(sections, key=lambda s: len(s["items"]))
    with_id = sum(1 for e in entries if e.get("q"))
    with_alt = sum(1 for e in entries if e["akas"])
    with_cut = sum(1 for e in entries if e["cuts"])
    canon_pool = [f for f in pool if f["rank"]]
    # refused BY THE GATE, which is not the same set as "not a row": one more
    # film cleared the gate and then had no running time anywhere.
    refused_gate = [f for f in pool if not (f["nsurvey"] >= 1
                                            or f["njury"] >= MIN_JURIES
                                            or f["nwin"])]
    assert (len(refused_gate) + len(entries) + len(unweighable)
            + len(multipart) == len(pool))
    assert [t for t, _y in multipart] == ["A Chinese Odyssey"], \
        "the notes name the multi-part entries: %s" % multipart

    prop = {
        "slug": SLUG,
        "title": "Martial Arts",
        "subtitle": "the classics of Chinese kung fu and wuxia cinema",
        "kind": "films",
        # A genre survey that needs a sentence of explanation to a general
        # audience — the 40-59 band in POPULARITY.md. "Kung fu movie" travels
        # further as a phrase than "cult classic" does, and Enter the Dragon
        # and Crouching Tiger are household titles, but the LIST is a
        # Chinese-cinema survey rather than a flagship, so it sits with Cult
        # Classics (55) and Korean Cinema (56) and below Criterion (63) and
        # Kurosawa (62), a named auteur whose name travels on its own.
        "popularity": 54,
        "year": "%d–%d" % (oldest["year"], newest["year"]),
        "blurb": "%d Chinese martial arts films the genre's own canon, "
                 "histories and award juries picked out, %d to %d — about %d "
                 "hours. No order; let the picker choose."
                 % (len(entries), oldest["year"], newest["year"],
                    round(total_min / 60.0)),
        "unit": {"one": "film", "many": "films"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "accent": ACCENT,
        "accentDark": ACCENT_DARK,
        "tiers": False,
        "random": True,
        "notes": [
            ["“A classic” is a verdict, so this list does not pass one.",
             "The request behind it said “maybe just the classics, deep, "
             "terrible depths there”, and the depths are the point: this "
             "genre made thousands of interchangeable films. So a film is "
             "here only if somebody else singled it out. Six surveys look "
             "back over a whole history — the Hong Kong Film Awards "
             "Association's 2005 Best 100 Chinese Motion Pictures, a native "
             "canon voted by 101 filmmakers, critics and scholars, and "
             "Wikipedia's histories of Hong Kong action cinema, the kung fu "
             "film, wuxia, Hong Kong cinema and the Shaw Brothers studio. "
             "Three juries pick about five films out of one year: the Hong "
             "Kong Film Award for Best Film and the Best Action Choreography "
             "awards of the Hong Kong Film Awards and Taiwan's Golden Horse. "
             "The counts ride on every row."],
            ["One survey, or two juries, or one win.",
             "A survey is already the long view, so one is enough. A jury "
             "names five films every year whatever the year was like, so one "
             "nomination is not a verdict about a genre — two are, and so is "
             "an outright win. %d of these rows are here on the surveys "
             "alone, %d on the juries alone, and %d on both. The win clause "
             "adds %d rows and exists for consistency rather than for scale: "
             "without it this list would carry films two juries merely "
             "nominated while refusing ones that actually won the prize for "
             "the very craft it is about. %s leads with %d of the nine."
             % (len(survey_only), len(jury_only),
                len(entries) - len(survey_only) - len(jury_only), len(by_win),
                top["t"], top["surveys"] + top["juries"])],
            ["The histories are on the panel because the awards are too "
             "young.",
             "Every award that honours this genre postdates its founding "
             "decade — the Hong Kong Film Awards start in 1982, the "
             "choreography award in 1983, the Golden Horse one in 1992 — and "
             "the 2005 canon reaches back but is a canon of Chinese cinema, "
             "not of martial arts: only %d of its hundred are martial arts "
             "films at all, %d of them can be a row here, and every one of "
             "those is starred. Gate on "
             "the canon and "
             "the juries alone and Enter the Dragon, The 36th Chamber of "
             "Shaolin, Come Drink with Me and Five Deadly Venoms are all "
             "missing. That is why written histories count. They are "
             "tertiary sources and they cost something: a history mentions a "
             "film for all sorts of reasons, so Naked Killer, Kung Fu VS "
             "Acrobatic and Shanghai Noon ride in on one mention apiece."
             % (len(canon_pool), len(canon_rows))],
            ["Chinese-language cinema only, and that is a decision about "
             "sources.",
             "“Kung fu / martial arts” could have meant the genre worldwide. "
             "It does not here. Every per-entry record that reaches this "
             "genre is Chinese — the only native canon, the only awards for "
             "its own craft, the only histories that reach back past 1982 — "
             "and there is no Thai or Indonesian equivalent at all, so a "
             "worldwide list would have had a hole exactly where its modern "
             "non-Chinese half lives. The samurai film is a neighbouring "
             "tradition with its own canon and its own list here. What that "
             "costs, plainly: no Seven Samurai, no Zatoichi, no Ong-Bak, no "
             "The Raid, no Kill Bill."],
            ["What else the gate throws out.",
             "%d martial arts films from these three places were named at "
             "most once and stop there, and every one of them is refused: "
             "The Assassin, "
             "Iron Monkey, Shaolin Temple, Duel to the Death, Armour of God, "
             "Dragons Forever and Eastern Condors are the ones worth arguing "
             "about, all seven nominated for action choreography and none of "
             "them a winner. The Assassin is the closest call on the list — "
             "adding Taiwan's Best Feature record to the panel would let it "
             "in and would change nothing else at all, which is what tuning a "
             "gate to one result looks like, so it was left out and named "
             "here instead. Two more are refused by the sources rather than "
             "by the "
             "gate: the histories name Chinese Boxer and The Spiritual Boxer "
             "in italics without linking them, and a film with no link "
             "cannot carry an id, so neither is here rather than being "
             "looked up by title and risking the wrong film. Genre and "
             "region are the film's own article, which is what keeps "
             "Infernal Affairs, The Killer, A Better Tomorrow and The "
             "Mission off a martial arts list without anybody here ruling on "
             "it." % len(refused_gate)],
            ["Bar widths are runtimes, and none was invented.",
             "All %d rows are weighted, %d hours in total, and every figure "
             "is a running time from the film's own Wikipedia article "
             "rather than from Wikidata — except on %d rows whose infobox "
             "leaves the field empty, one of them a canon selection, where "
             "Wikidata's figure is cited instead of dropping the film. That "
             "matters more here than "
             "anywhere else in this catalogue: the same film exists as a "
             "Hong Kong release, a Mandarin export version and a shorter "
             "dubbed American cut, and %d rows carry a second length in the "
             "note for exactly that reason. One row per film, the first cut "
             "the infobox names is what the bar measures. The range runs "
             "from %s at %d minutes to %s at %d. A film with no running time "
             "in either place is not a row at all."
             % (len(entries), round(total_min / 60.0), len(from_wikidata),
                with_cut, shortest["t"], shortest["runtime"], longest["t"],
                longest["runtime"])],
            ["Every row carries an id, and the titles are a mess.",
             "These films have three and four English names apiece — Drunken "
             "Master II is The Legend of Drunken Master, Dragon Inn is "
             "Dragon Gate Inn, King Boxer is Five Fingers of Death — and the "
             "romanisations move under them as well, so title matching would "
             "have been hopeless. All %d rows carry a Wikidata id resolved "
             "from the wikilink the source printed itself, never from a "
             "title, and %d rows name an alternate title in the note. %d of "
             "these films are already somewhere else in the catalogue, "
             "across %s, and ticking one ticks the other."
             % (with_id, with_alt, len(groups), ", ".join(sorted(lists_met)))],
            ["The eras are Wikipedia's “Hong Kong action cinema”, not ours.",
             "Its section headings are the six here — the early Shanghai "
             "wuxia film, the “New School” wuxia of the late 1960s, the kung "
             "fu wave of the 1970s, the reinvention of the 1980s, the "
             "wire-work wave and what came after the industry's slump. The "
             "cut years are ours, because “late 1960s” is not a boundary a "
             "program can use, and each is set at a film that article itself "
             "calls the turn. Four kinds of film cannot be a row: a lost one, "
             "because the founding wuxia hit and its eighteen sequels are "
             "gone; a serial, because it is not one film with one length; a "
             "two-parter, which is why the canon's A Chinese Odyssey is not "
             "here; and one with no running time anywhere, which is why the "
             "oldest thing that survives the gate is from 1960."],
            "Selection from the Hong Kong Film Awards Association's “Best 100 "
            "Chinese Motion Pictures” (2005), the Hong Kong Film Award "
            "records for Best Film and Best Action Choreography, the Golden "
            "Horse Award for Best Action Choreography, and Wikipedia's “Hong "
            "Kong action cinema”, “Kung fu film”, “Wuxia”, “Cinema of Hong "
            "Kong” and “Shaw Brothers Studio”; genre, production country and "
            "running times from each film's own Wikipedia article; ids from "
            "the sources' own wikilinks via Wikidata.",
        ],
        "sections": sections,
    }

    P.write(prop)

    print("wrote %s.json" % SLUG)
    print("  %d works read, %d in the genre+region pool, %d rows"
          % (len(films), len(pool), len(entries)))
    print("  %d min (%.1f hours) — every row weighted"
          % (total_min, total_min / 60.0))
    for s in sections:
        print("   %-24s %3d  %s" % (s["title"], len(s["items"]), s["sub"]))
    print("  gate: %d on surveys alone, %d on juries alone, %d on both; "
          "%d of those on a win" % (len(survey_only), len(jury_only),
                                    len(entries) - len(survey_only)
                                    - len(jury_only), len(by_win)))
    print("  ids: %d of %d rows; %d rows name an alternate title"
          % (with_id, len(entries), with_alt))
    for t, y, ys in refused_id:
        print("    id refused %-34s row %s vs item %s" % (t, y, ys))
    print("  dropped for having no running time anywhere (%d): %s"
          % (len(unweighable), unweighable))
    print("  dropped for being more than one film (%d): %s"
          % (len(multipart), multipart))
    print("  runtime taken from Wikidata where the infobox was empty (%d): %s"
          % (len(from_wikidata), from_wikidata))
    print("  %d sync groups across %d other lists" % (len(groups),
                                                      len(lists_met)))
    for s, n in collections.Counter(
            s for v in groups.values() for s in v).most_common(15):
        print("   %-24s %3d" % (s, n))
    print("  most-shared row: %s on %d other lists"
          % (by_id[top_share[0]], len(top_share[1])))
    print("  near misses — same title, a different year (%d):" % len(missed))
    for raw, slug, year, ours in sorted(set(missed)):
        print("   %-36s %-18s theirs=%s ours=%s" % (raw, slug, year, ours))
    print("  in the genre and region but refused by the gate (%d):"
          % len(refused_gate))
    for f in sorted(refused_gate, key=lambda f: (f["year"], f["titles"][0])):
        print("   %s %-42s %s" % (f["year"], f["titles"][0][:41],
                                  ",".join(sorted(f["src"]))))
    print("  biggest section: %s" % biggest["title"])


if __name__ == "__main__":
    main()
