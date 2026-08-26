#!/usr/bin/env python3
"""Generate properties/tremors.json.

    PYTHONIOENCODING=utf-8 python tools/make_tremors.py

Every released Tremors film in U.S. release order, plus the 2003 television
series as its own section. Twenty rows, all weighted, nothing typed from
memory: scratch/agent-tremors/collect.py machine-reads the three source
articles into tools/data/tremors.json and this asserts every claim the page
makes before it writes.

WHY RELEASE ORDER, AND WHERE THE PREQUEL SITS
---------------------------------------------
The fourth film released, *Tremors 4: The Legend Begins*, is set in 1889 —
before every other film here, and before the town in them has its present
name. Its own article's categories say both things: "Direct-to-video prequel
films" and "Films set in 1889", and this generator reads that rather than
being told it.

It still sits fourth. Wikipedia's franchise article presents exactly one
order for these films — its Films table, in U.S. release order — and offers
no story chronology at all. A list that moved the prequel to the front would
be inventing an order its source does not carry, so the row says what the
film is and the order says when it came out. Same call steins-gate made
about its alternate episode.

THE DIRECT-TO-VIDEO RUN, MARKED PER ROW
---------------------------------------
One of the seven played in cinemas. The other six went straight to video,
and someone choosing what to watch tonight wants that on the row rather than
in a paragraph. The channel comes from each film's OWN article categories —
"1996 direct-to-video films", "Universal Pictures direct-to-video films" and
the rest — not from the franchise article's prose and not from assumption;
the theatrical one is cross-checked against the box-office gross its infobox
states and the "Theatrical release poster" its image caption names.

It is carried as a row note rather than as disney's release-channel tiers.
Tiers render as a bare "T2" badge with no legend and a Tier 1/2/3 panel in
the stats; on a 600-row studio catalogue the filter chips pay for that, on
twenty rows the words "Direct-to-video" are shorter to read and need
explaining to nobody.

THE 2003 SERIES IS IN, AND KEEPS THE LIST WEIGHTED
--------------------------------------------------
Its own section, because the source treats it as its own thing: a separate
Television heading, a separate table, a separate article. The risk was
CLU-131 — a row with no `w` on a weighted list silently counts as one hour,
so thirteen unweighted episodes would have quietly stolen two hours from the
films and the honest response would have been to drop every weight on the
list. It does not arise: the series article's episode table carries a
Runtime column, per episode, so all thirteen are weighted from the source
and the films keep their hours. The trade never had to be made, and this
paragraph is here so the next person can see it was checked.

Sci-Fi aired the series out of order and the article's table records both
orders. The rows follow the broadcast order the table itself is listed in —
release order again — and each row states where it was made in the run,
which is the fact, offered rather than imposed.

WEIGHTS
-------
All twenty rows carry `w`, all-or-nothing: films from the runtime in each
film's own Wikipedia infobox (one clean "N minutes" apiece, asserted, each
cited in the article to the BBFC), episodes from the series article's own
Runtime column. Wikidata's P2047 is deliberately NOT the source for the
films — it reports the longest runtime it holds, which for four of the six
sequels is an unrated cut five minutes longer than the release the article
documents, and mixing the two would make the bar widths mean two things.

Data: scratch/agent-tremors/fetch.py (batched wikitext) ->
scratch/agent-tremors/collect.py -> tools/data/tremors.json
"""
import json
import pathlib
import re
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop  # noqa: E402
from gwlib.prop import join_bits, normt, slug  # noqa: E402

SLUG = "tremors"
ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "tools" / "data" / "tremors.json"

ACCENT, ACCENT_DARK = "#8A4B12", "#E0A257"

WIKI = "https://en.wikipedia.org/wiki/"

# What each film IS, keyed by the label its franchise table prints. Terse,
# spoiler-free: a position in the run, a release channel, a fact about how it
# was made. The channel word is prepended from the data, not written here.
NOTES = {
    "Tremors":
        "The original, and the only one with Kevin Bacon in it.",
    "Tremors 2: Aftershocks":
        "The first sequel, six years on.",
    "Tremors 3: Back to Perfection":
        "Returns to the town of the first film. The 2003 series picks up "
        "from here.",
    "Tremors 4: The Legend Begins":
        "A prequel: fourth out, but set in 1889, in the town before it was "
        "renamed.",
    "Tremors 5: Bloodlines":
        "Eleven years later, and the first made without the writers who "
        "created the series.",
    "Tremors: A Cold Day in Hell":
        "The sixth film, and the first with no number in its title.",
    "Tremors: Shrieker Island":
        "The seventh, and the last so far.",
}

CHANNEL = {"theatrical": "In cinemas", "direct-to-video": "Direct-to-video"}

ORDINAL = {1: "1st", 2: "2nd", 3: "3rd"}


def load_json(path, tries=4):
    """Read a JSON file that another builder may be mid-write on."""
    for n in range(tries):
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            if n == tries - 1:
                raise
            time.sleep(0.4)


def check_source(d):
    """Everything this list asserts about its sources, before it builds."""
    films, ep = d["films"], d["series"]["episodes"]

    # --- the shape the page claims: seven films, 1990 to 2020 -------------
    assert len(films) == 7, len(films)
    dates = [f["date"] for f in films]
    assert dates == sorted(dates), "the Films table is not in release order"
    assert dates[0][:4] == "1990" and dates[-1][:4] == "2020", dates
    # the franchise infobox's own span agrees with the table's ends
    assert re.fullmatch(r"1990.2020", d["franchise_years"]), \
        d["franchise_years"]

    # --- every runtime is one clean figure from the film's own article ----
    for f in films:
        assert re.fullmatch(r"\d+ minutes", f["runtime_field"]), \
            (f["t"], f["runtime_field"])
        assert 60 <= f["runtime"] <= 200, (f["t"], f["runtime"])
        # the franchise table's year is one the film's own infobox states —
        # the guard against a searched-for page supplying a stranger's runtime
        assert int(f["date"][:4]) in f["infobox_years"], \
            (f["t"], f["date"], f["infobox_years"])
        assert re.fullmatch(r"Q[1-9]\d*", f["q"]), (f["t"], f["q"])

    # --- release channels, read from each film's own categories -----------
    theatrical = [f for f in films if f["channel"] == "theatrical"]
    dtv = [f for f in films if f["channel"] == "direct-to-video"]
    assert len(theatrical) == 1 and len(dtv) == 6, \
        [(f["t"], f["channel"]) for f in films]
    one = theatrical[0]
    assert one["date"][:4] == "1990" and not one["dtv_categories"], one["t"]
    # a cinema release leaves two other marks on the article, and both are
    # here — a box-office gross, and a poster the caption calls theatrical
    assert "$" in one["gross"], one["gross"]
    assert "theatrical" in one["caption"].lower(), one["caption"]
    for f in dtv:
        assert f["dtv_categories"], f["t"]
        assert not f["gross"], (f["t"], f["gross"])

    # --- the gaps two row notes name, from the dates rather than memory ---
    yrs = [int(f["date"][:4]) for f in films]
    assert yrs[1] - yrs[0] == 6, yrs                      # "six years on"
    assert yrs[4] - yrs[3] == 11, yrs                     # "eleven years later"
    assert "without participation of Stampede Entertainment" in films[4]["lead"], \
        films[4]["lead"][:400]
    assert "writing team that created the series" in films[4]["lead"], \
        films[4]["lead"][:400]

    # --- the numbering claim a row note makes, checked not remembered ----
    numbered = [f["t"] for f in films if re.search(r"\d", f["t"])]
    assert numbered == ["Tremors 2: Aftershocks",
                        "Tremors 3: Back to Perfection",
                        "Tremors 4: The Legend Begins",
                        "Tremors 5: Bloodlines"], numbered
    assert not re.search(r"\d", films[5]["t"]), films[5]["t"]

    # --- the prequel: fourth out, nineteenth century, said by the source --
    pre = [f for f in films if f["prequel"]]
    assert len(pre) == 1, [f["t"] for f in pre]
    p = pre[0]
    assert films.index(p) == 3, films.index(p)
    assert p["setting_years"] == [1889], p["setting_years"]
    assert 1800 <= p["setting_years"][0] < 1900, p["setting_years"]
    # the two things its row note says beyond the year, in the article's lead
    assert "prequel to the earlier films" in p["lead"], p["lead"][:200]
    assert "renamed" in p["lead"], p["lead"][:400]
    # and no other film's article claims a period setting at all
    assert not [f for f in films if f is not p and f["setting_years"]], \
        [(f["t"], f["setting_years"]) for f in films if f["setting_years"]]

    # --- the television series --------------------------------------------
    s = d["series"]
    assert s["num_seasons"] == 1 and s["num_episodes"] == 13, s["num_episodes"]
    assert len(ep) == s["num_episodes"], (len(ep), s["num_episodes"])
    assert [e["n"] for e in ep] == list(range(1, 14)), [e["n"] for e in ep]
    assert sorted(e["produced"] for e in ep) == list(range(1, 14)), \
        "the production-order column is not a permutation of 1-13"
    assert {e["year"] for e in ep} == {2003}, {e["year"] for e in ep}
    # the reason the series can join a WEIGHTED list at all
    assert all(30 <= e["runtime"] <= 70 for e in ep), \
        [(e["t"], e["runtime"]) for e in ep]
    assert d["television"] == [["1", "13", "March 28, 2003", "August 8, 2003",
                               "Nancy Roberts", "Syfy"]], d["television"]
    assert d["series_sequel_to"] == "Tremors 3: Back to Perfection", \
        d["series_sequel_to"]

    # --- who is in what, from the franchise article's own cast grid -------
    cast = d["cast"]
    assert cast["years"] == ["1990", "1996", "2001", "2004", "2015", "2018",
                             "2020", "2003"], cast["years"]
    assert [f["date"][:4] for f in films] == cast["years"][:7], cast["years"]
    # the two dropped rows are the table's own header rows, nothing else
    assert len(cast["dropped"]) == 2, cast["dropped"]
    assert not [r for r in cast["dropped"]
                if re.search(r"Bacon|Michael Gross", r)], cast["dropped"]
    bacon = d["appearances"]["Kevin Bacon"]
    assert bacon == [0], bacon                       # the 1990 film, and only
    rows = [r for r in cast["rows"] if "Kevin Bacon" in " ".join(r["cells"])]
    assert len(rows) == 1, [r["character"] for r in rows]
    assert d["appearances"]["Michael Gross"] == list(range(8)), \
        d["appearances"]["Michael Gross"]
    return films, ep


def accent_is_free():
    """No other property may share this list's accent pair (qa_lint rule)."""
    for f in sorted((ROOT / "properties").glob("*.json")):
        if f.name in ("index.json", "search.json", "%s.json" % SLUG):
            continue
        p = load_json(f)
        assert (p.get("accent"), p.get("accentDark")) != (ACCENT, ACCENT_DARK), \
            "accent pair already used by %s" % f.stem


def sync_partners(rows):
    """Rows on other lists that will tick together with rows on this one.

    build.py groups film rows across lists on normalized title + year (with a
    fallback to a single year named in the note, which is how spine-numbered
    lists join in), so this reproduces that key rather than guessing at it.

    The point of interest is the 1990 film, which is the only Tremors any
    other list is likely to carry — but every overlap is found, not just the
    expected one, because a thirteen-episode section brings thirteen more
    titles into a catalogue that is still growing. Episode rows are numbered
    1-13 and their notes name no year, so build.py derives no sync key for
    them at all; this asserts that, rather than trusting it.
    """
    want = {}
    for x in rows:
        if re.fullmatch(r"(18|19|20)\d{2}", str(x["n"])):
            want["%s|%s" % (normt(x["t"]), x["n"])] = x["id"]
        else:
            years = set(re.findall(r"\b((?:18|19|20)\d{2})\b",
                                   x.get("note") or ""))
            assert len(years) != 1, \
                "row %s would sync on a year in its note: %r" % (x["id"],
                                                                 x.get("note"))
    out = {}
    for f in sorted((ROOT / "properties").glob("*.json")):
        if f.name in ("index.json", "search.json", "%s.json" % SLUG):
            continue
        p = load_json(f)
        kind = p.get("kind") or ""
        # films sync with films, games with games, never across (build.py
        # rides the medium in the key so Goldeneye cannot tick Goldeneye)
        if "film" not in kind or "game" in kind or p.get("secret"):
            continue
        for s in p.get("sections", []):
            for x in s.get("items", []):
                n = str(x.get("n", ""))
                if re.fullmatch(r"(18|19|20)\d{2}", n):
                    year = n
                else:
                    found = set(re.findall(r"\b((?:18|19|20)\d{2})\b",
                                           x.get("note") or ""))
                    year = found.pop() if len(found) == 1 else None
                key = "%s|%s" % (normt(x.get("t", "")), year)
                if year and key in want:
                    out.setdefault(want[key], []).append(
                        (p["slug"], x["id"], p["title"]))
    assert set(out) <= {"tr-1990-tremors"}, \
        "an unexpected row pairs across the catalogue: %s" % sorted(out)
    return sorted(out.get("tr-1990-tremors", []))


def main():
    d = load_json(DATA)
    films, eps = check_source(d)
    accent_is_free()

    film_rows = []
    for f in films:
        year = f["date"][:4]
        film_rows.append({
            "id": "tr-%s-%s" % (year, slug(f["t"])),
            "t": f["t"], "n": year,
            "w": round(f["runtime"] / 60.0, 2),
            "q": f["q"],
            "note": join_bits(CHANNEL[f["channel"]], NOTES[f["t"]]),
        })

    ep_rows = []
    for e in eps:
        made = ORDINAL.get(e["produced"], "%dth" % e["produced"])
        ep_rows.append({
            "id": "tr-tv-%s" % slug(e["t"]),
            "t": e["t"], "n": str(e["n"]),
            "w": round(e["runtime"] / 60.0, 2),
            **({"note": "Produced %s." % made}
               if e["produced"] != e["n"] else {}),
        })

    fmin = sum(f["runtime"] for f in films)
    emin = sum(e["runtime"] for e in eps)
    dtv = sum(1 for f in films if f["channel"] == "direct-to-video")

    sections = [
        {
            "id": "films", "title": "The films",
            "sub": "1990–2020 · 7 films · %d hours · 1 in cinemas, %d "
                   "direct-to-video" % (round(fmin / 60.0), dtv),
            "intro": "Seven films in the order they came out, which is the "
                     "only order the franchise's own filmography presents. "
                     "The first played in cinemas and the six after it went "
                     "straight to video; every row says which. The fourth is "
                     "a prequel and stays fourth — it is where the series "
                     "put it, and the row says where the story sits.",
            "links": [{"label": "The franchise",
                       "url": WIKI + "Tremors_(franchise)"}],
            "open": True,
            "items": film_rows,
        },
        {
            "id": "series", "title": "The 2003 series",
            "sub": "2003 · 13 episodes · %d hours" % round(emin / 60.0),
            "intro": "One season on the Sci-Fi Channel, thirteen episodes, "
                     "cancelled after them. It follows on from the third "
                     "film. The channel aired it out of order, so the rows "
                     "run in the broadcast order the episode list is given "
                     "in and each one notes where it was made in the run — "
                     "the other order is there if you want it, but the list "
                     "does not pick it for you.",
            "links": [{"label": "The series",
                       "url": WIKI + "Tremors_(TV_series)"}],
            "items": ep_rows,
        },
    ]

    # ---- the checks the shipped file has to pass -------------------------
    rows = [x for s in sections for x in s["items"]]
    assert len(rows) == 20, len(rows)
    ids = [x["id"] for x in rows]
    assert len(ids) == len(set(ids)), \
        sorted({i for i in ids if ids.count(i) > 1})
    # all-or-nothing weighting: one bare row would silently cost an hour
    assert all(isinstance(x.get("w"), float) and x["w"] > 0 for x in rows), \
        [x["id"] for x in rows if not x.get("w")]
    hours = round(sum(x["w"] for x in rows), 2)
    assert abs(hours - (fmin + emin) / 60.0) < 0.2, (hours, fmin + emin)
    years = [int(x["n"]) for x in film_rows]
    assert years == sorted(years), years
    nums = [int(x["n"]) for x in ep_rows]
    assert nums == list(range(1, 14)), nums
    # the prequel is a row in the fourth position, not a section of its own
    assert film_rows[3]["t"] == "Tremors 4: The Legend Begins", film_rows[3]
    assert "1889" in film_rows[3]["note"], film_rows[3]["note"]

    partners = sync_partners(rows)
    titles = [t for _, _, t in partners]
    others = (" and ".join(titles) if len(titles) < 3
              else ", ".join(titles[:-1]) + " and " + titles[-1])

    # The joke, and the sync that makes it work — one note, so a reader meets
    # the fact and the consequence together. The second sentence appears only
    # when the catalogue actually carries a list that pairs with the 1990
    # film, because it is a claim about what ticking a box does.
    bacon_note = [
        "Kevin Bacon is in the first one and nothing else.",
        "One film out of the seven, and none of the thirteen episodes — the "
        "franchise article's cast table gives him a single column. He was "
        "going to come back for a Syfy series in 2017 and the network passed "
        "on the pilot."]
    if partners:
        bacon_note[1] += (
            " Tremors (1990) also sits on %s, and ticking it in any one of "
            "those places ticks it in all of them." % others)

    notes = [
        ["Release order, and the prequel stays where it is.",
         "Tremors 4: The Legend Begins came out fourth and is set in 1889, "
         "before everything else here. Wikipedia's franchise article presents "
         "one order for these films — its own filmography, by U.S. release "
         "date — and no story chronology at all, so moving the prequel to the "
         "front would be inventing an order the source does not carry. It "
         "stays fourth, and its row says what it is."],
        ["One of the seven played in cinemas.",
         "The 1990 film. The six after it went straight to video, which each "
         "film's own article states, and every row is marked so you can tell "
         "without looking it up. The cinema release is the one with a "
         "box-office figure attached; the rest have none."],
        ["The series is here, with its episodes.",
         "Thirteen of them on the Sci-Fi Channel between March and August "
         "2003, following on from the third film. It gets its own section "
         "because the franchise article gives it its own heading and its own "
         "table. Sci-Fi ran the episodes out of the order they were made in, "
         "and the rows follow the broadcast order the episode list is "
         "written in, each one saying where it was made — the other order is "
         "stated, never imposed."],
        ["Bar widths are runtimes.",
         "All %d rows carry one — %d hours in all. The films take the runtime "
         "in each film's own Wikipedia infobox; the episodes take the runtime "
         "column of the series article's episode list. That column is the "
         "reason the series could join a weighted list at all: an episode "
         "with no runtime would have counted as an hour and quietly stolen "
         "time from the films, so a row whose runtime could not be read "
         "fails the build rather than shipping as a guess."
         % (len(rows), round(hours))],
        bacon_note,
        ["Michael Gross is in all of it.",
         "All seven films and all thirteen episodes — as Burt Gummer in every "
         "one except the prequel, where he plays the ancestor. Nobody else in "
         "the cast table comes close."],
        ["Not included.",
         "The Syfy pilot shot in 2017 with Kevin Bacon: the network passed on "
         "it in 2018 and it never aired, so there is nothing to watch. Nor "
         "the series cancelled during the second film's production, nor the "
         "video games, nor the eighth film the creators were reported to be "
         "discussing in 2025 — it has no title and no date, and an undated "
         "announcement is not a row."],
        "Film order and U.S. release dates from the Films table of "
        "Wikipedia's Tremors (franchise) article, with each film's runtime, "
        "release channel and period setting from that film's own article; "
        "episode titles, order and runtimes from the episode list in "
        "Wikipedia's Tremors (TV series) article; the cast facts from the "
        "franchise article's own principal-cast table.",
    ]

    p = {
        "slug": SLUG,
        "title": "Tremors",
        "subtitle": "seven films and a television series, in release order",
        "kind": "films & tv",
        "popularity": 52,
        "year": d["franchise_years"],
        "blurb": "One cinema release in 1990, six direct-to-video sequels "
                 "after it, and a thirteen-episode series in between. "
                 "About %d hours." % round(hours),
        "unit": {"one": "entry", "many": "entries"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": ACCENT,
        "accentDark": ACCENT_DARK,
        "tiers": False,
        "notes": notes,
        "sections": sections,
    }

    out = prop.write(p)
    print("wrote %s — %d rows, %.2f hours (%d minutes)"
          % (out.name, len(rows), hours, fmin + emin))
    for s in sections:
        print("   %-16s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))
    print("   channels: 1 theatrical, %d direct-to-video" % dtv)
    print("   prequel at position %d of 7, set in %d"
          % (films.index(next(f for f in films if f["prequel"])) + 1,
             next(f for f in films if f["prequel"])["setting_years"][0]))
    print("   sync key: %s|1990|f -> %s"
          % (normt("Tremors"), ", ".join("%s/%s" % (s, i)
                                         for s, i, _ in partners) or "NOBODY"))


if __name__ == "__main__":
    main()
