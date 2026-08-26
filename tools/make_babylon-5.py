#!/usr/bin/env python3
"""Generate properties/babylon-5.json — 110 episodes and all eight films.

    python3 tools/make_babylon-5.py

Broadcast order, one row per episode, with every film at the point it went
out. The films are the whole shape of this list, and they are not one kind of
thing: *The Gathering* is the feature-length pilot and sits above season one,
where the source files it; *In the Beginning* went out between the season four
finale and the season five premiere; *Thirdspace* and *The River of Souls*
aired inside season five's own run and sit inside its list rather than in
sections of their own; *A Call to Arms*, *The Legend of the Rangers*, *The
Lost Tales* and *The Road Home* follow the finale, years apart.

Nothing here is placed by hand. Every film is filed by comparing its airdate
against each season's first and last, and the one slot the source states in
words — *Thirdspace* between "Movements of Fire and Shadow" and "The Fall of
Centauri Prime" — is asserted against the answer the dates give.

Nothing is weighted, all or nothing. The eight films publish runtimes and
their rows carry them as text; the episodes publish none — the source's
episode tables have no runtime column, only 14 of the 110 episodes have an
article of their own, and not one of those carries a runtime on Wikidata. A
weighted list counts an unweighted row as one hour, so weighting the films
alone would invent an hour 110 times over.

Titles, numbering, airdates, season names, film runtimes and the two
documented running-order corrections are machine-read from Wikipedia by
scratch/agent-b5/build_data.py; the committed result is
tools/data/babylon5.json.

*Crusade* is not here — see the notes on the page for why.
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop  # noqa: E402

SLUG = "babylon-5"
DATA = pathlib.Path(__file__).resolve().parent / "data" / "babylon5.json"

MONTHS = ["", "January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]

# Per film: the heading it gets when it stands alone, the sub under that
# heading, what kind of thing it is, and anything else worth one clause. The
# runtimes and dates are never typed here — they come from the data file.
FILMS = {
    "gathering": ("Pilot film", "the feature-length pilot",
                  "The feature-length pilot",
                  "A 1998 special edition re-cut is the version the DVD "
                  "sets carry"),
    "beginning": ("In the Beginning", "a television film, before season five",
                  "Television film", "A prequel"),
    "thirdspace": (None, None, "Television film", ""),
    "river": (None, None, "Television film", ""),
    "calltoarms": ("A Call to Arms", "a television film, after the finale",
                   "Television film",
                   "Sets up the spin-off series Crusade"),
    "rangers": ("The Legend of the Rangers",
                "a television film, three years after the finale",
                "Television film",
                "A pilot for a series that was never picked up"),
    "losttales": ("The Lost Tales", "direct to DVD, two stories",
                  "Direct to DVD", "Never aired on television"),
    "roadhome": ("The Road Home", "an animated film, direct to video",
                 "Animated, direct to video", ""),
}


def datestr(d):
    return "%s %d, %d" % (MONTHS[d[1]], d[2], d[0])


def span(a, b):
    return str(a[0]) if a[0] == b[0] else "%d–%02d" % (a[0], b[0] % 100)


def main():
    d = json.loads(DATA.read_text(encoding="utf-8"))
    seasons, names = d["seasons"], d["season_names"]
    nums = sorted(seasons, key=int)

    # ---- where each film goes: inside a season's broadcast run, or between
    # two of them. Dates decide; nothing is placed by hand.
    first = {n: seasons[n][0]["d"] for n in nums}
    last = {n: seasons[n][-1]["d"] for n in nums}
    inside, alone = {}, []
    for f in d["films"]:
        home = next((n for n in nums if first[n] < f["d"] < last[n]), None)
        (inside.setdefault(home, []).append(f) if home else alone.append(f))
    assert sorted(inside) == ["5"], sorted(inside)
    assert len(alone) == 6, len(alone)

    def film_row(f, n):
        _t, _s, kind, extra = FILMS[f["key"]]
        if n == "film":                       # a row inside a season's list
            slot = "Aired %s, between episodes %d and %d" % (
                datestr(f["d"]), f["before"], f["before"] + 1)
        else:
            slot = "%s %s" % ("Released" if "video" in kind or "DVD" in kind
                              else "Aired", datestr(f["d"]))
        note = prop.join_bits(kind, "%d minutes" % f["runtime"], slot, extra)
        return {"id": "b5-film-%s" % f["key"], "t": f["short"], "n": n,
                "note": note}

    # ---- the two running-order corrections the source records
    swap_note = {}
    for early, late in d["intended_order"]:
        pos = {e["t"]: e["e"] for e in seasons["2"]}
        assert pos[early] > pos[late], \
            "%r already airs before %r" % (early, late)
        swap_note[late] = "The creator has said %s was meant to air first" % early
        swap_note[early] = "Meant to air before %s" % late

    # ---- sections, in broadcast order
    blocks = []
    for n in nums:
        items, films_here = [], sorted(inside.get(n, []), key=lambda f: f["d"])
        for e in seasons[n]:
            while films_here and films_here[0]["d"] < e["d"]:
                f = films_here.pop(0)
                f["before"] = next(x["_e"] for x in reversed(items) if "_e" in x)
                items.append(film_row(f, "film"))
            row = {"id": "b5-s%se%d" % (n, e["e"]), "t": e["t"], "n": str(e["e"])}
            if e["t"] in swap_note:
                row["note"] = swap_note[e["t"]]
            row["_e"] = e["e"]
            items.append(row)
        assert not films_here, "a film outran its season"
        sub = prop.join_bits(names[n], span(first[n], last[n]),
                             "%d episodes" % len(seasons[n])
                             + (", with two television films where they aired"
                                if inside.get(n) else ""))
        blocks.append((first[n], {"id": "s%s" % n, "title": "Season %s" % n,
                                  "sub": sub, "items": items}))
    for f in alone:
        title, subbit, _k, _x = FILMS[f["key"]]
        blocks.append((f["d"], {
            "id": "film-%s" % f["key"], "title": title,
            "sub": prop.join_bits(str(f["d"][0]), subbit),
            "items": [film_row(f, str(f["d"][0]))]}))
    blocks.sort(key=lambda b: b[0])
    sections = [s for _d, s in blocks]
    sections[0]["open"] = True

    # ---- the slot the source names in words, checked against the dates
    s5 = sections[[s["id"] for s in sections].index("s5")]["items"]
    i = [x["id"] for x in s5].index("b5-film-thirdspace")
    assert [s5[i - 1]["t"], s5[i + 1]["t"]] == d["thirdspace_between"], \
        "Thirdspace landed between %r and %r" % (s5[i - 1]["t"], s5[i + 1]["t"])

    for s in sections:
        for x in s["items"]:
            x.pop("_e", None)

    # ---- counts, and the sync trap. This list's kind contains "film", so
    # build.py reads a year out of any row's note when the number column is
    # not one — an episode note naming a single year would quietly pair that
    # episode with a same-titled film on another list.
    ids = [x["id"] for s in sections for x in s["items"]]
    eps = [i for i in ids if not i.startswith("b5-film-")]
    assert len(eps) == 110, len(eps)
    assert len(ids) == 118, len(ids)
    assert len(set(ids)) == len(ids), "duplicate ids"
    for s in sections:
        for x in s["items"]:
            if not x["id"].startswith("b5-film-"):
                assert not re.search(r"(18|19|20)\d{2}", x.get("note") or ""), \
                    "year in an episode note would fake a film sync: %s" % x["id"]

    prop.write({
        "slug": SLUG,
        "title": "Babylon 5",
        "subtitle": "every episode, with the films where they aired",
        "kind": "tv & films",
        "popularity": 60,
        "year": "1993–2023",
        "blurb": "All 110 episodes and all eight films in broadcast order — "
                 "five seasons on one station, written as one long story.",
        "unit": {"one": "entry", "many": "entries"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": "#39417F",
        "accentDark": "#8E97E8",
        "tiers": False,
        "notes": [
            ["Broadcast order, films included.", "The pilot film, then five "
             "seasons of 22, with each later film at the point it went out: "
             "In the Beginning between the season four finale and the season "
             "five premiere, Thirdspace and The River of Souls inside season "
             "five's own run, the rest after the finale. The two that aired "
             "mid-season sit in season five's list rather than in sections of "
             "their own, because that is where they landed."],
            ["The season names are episode titles.", "Wikipedia names each "
             "season after an episode inside it — Signs and Portents, The "
             "Coming of Shadows, and so on — and the subheads here carry "
             "those names, so a season and one of its rows can share a title."],
            ["Season two aired two pairs the wrong way round.", "The source "
             "records the creator saying A Race Through Dark Places was meant "
             "to precede Soul Mates, and Knives to precede In the Shadow of "
             "Z'ha'dum. This list keeps broadcast order and those four rows "
             "say so, so you can swap them yourself if you want to."],
            ["Crusade is not here.", "The thirteen-episode spin-off has its "
             "own cast, its own run and its own list on Wikipedia, which is "
             "where the source keeps it. It also has four competing running "
             "orders on record, so no list can carry it without picking one. "
             "Two rows here touch it anyway: A Call to Arms sets it up, and "
             "The Legend of the Rangers aired three years after it ended."],
            ["What the last three rows are.", "The Legend of the Rangers "
             "aired on Sci Fi as a pilot for a series that was never picked "
             "up, The Lost Tales went straight to DVD and never aired at all, "
             "and The Road Home is animated and direct to video. All three "
             "sit in the source's own films table, so all three are here, at "
             "the end, in date order."],
            ["Nothing is weighted.", "The eight films' runtimes are known and "
             "every film row carries its own. The episodes' are not: the "
             "source's episode tables have no runtime column, only 14 of the "
             "110 episodes have an article of their own, and not one of those "
             "carries a runtime. A weighted list counts a row with no weight "
             "as one hour, so weighting the films alone would push a guessed "
             "hour into all 110 episodes. An episode and a film each count "
             "one."],
            "Titles, numbering, airdates, season names, film runtimes and the "
            "two documented running-order corrections machine-read from "
            "Wikipedia's List of Babylon 5 episodes and each film's own "
            "article; the page's series overview counts, the unbroken 1–110 "
            "numbering and Thirdspace's stated slot are asserted before this "
            "builds.",
        ],
        "sections": sections,
    })

    print("wrote %s.json — %d rows (%d episodes + 8 films)"
          % (SLUG, len(ids), len(eps)))
    for s in sections:
        print("   %-26s %3d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
