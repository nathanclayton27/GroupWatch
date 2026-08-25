#!/usr/bin/env python3
"""Generate properties/nolan.json.

    PYTHONIOENCODING=utf-8 python tools/make_nolan.py

Every feature Christopher Nolan has directed, in release order — the thirteen
rows whose Director cell is a bare {{yes}} in the Feature film table on
Wikipedia's "Christopher Nolan filmography". The table has fourteen rows; the
fourteenth is Man of Steel (2013), whose Director cell says {{no}} — Nolan
produced it and wrote the story and Zack Snyder directed it — so it is not
here.

Two scope calls, both stated on the list itself so either can be overturned by
changing one line:

  * Produced or written but not directed: OUT. That drops Man of Steel and the
    five rows of the filmography's Executive producer table (Transcendence,
    Batman v Superman, both cuts of Justice League, and Sanatorium Under the
    Sign of the Hourglass, on which the credit is "Presented by").
  * Short films: OUT. The source keeps them in a separate table under its own
    "Short films" heading and treats none of them as a feature. Four are his:
    Tarantella (1989, co-directed), Larceny (1996), Doodlebug (1997) and Quay
    (2015). The fifth, The Doll's Breath (2019), he only executive produced.

The list starts at Following because the source starts there. Its lead carries
a footnote about a feature called Larry Mahoney that Nolan directed in the
mid-1990s and that was scrapped and never released; there is nothing to watch
and nothing to weigh, so it is a note and not a row.

Every runtime is Wikidata P2047, gated on a P577 within a year of the table's
year, and the generator refuses to build if any row's runtime came from
anywhere else. That rule is not decoration: three of these films' own
Wikipedia infoboxes disagree with Wikidata (The Prestige by five minutes), and
taking whichever number is handier per film would make the total-hours figure
on the front of the list a number from no source at all. The total is checked
against the exact minute sum, never against a sum of rounded hours.

Notes say what a thing is — where it was adapted from, where it sits in the
trilogy, what it cost, how long it runs. Nothing here describes what happens
in a film.

Data: scratch/nolan/collect.py -> scratch/nolan/nolan_data.json
"""
import datetime
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop
from gwlib.prop import join_bits, slug

SLUG = "nolan"
DATA = (pathlib.Path(__file__).resolve().parent.parent
        / "scratch" / "nolan" / "nolan_data.json")

# Four sections, and the divisions are the career's own. Each break is a fact
# about how the films were made rather than a decade boundary: (1) the three
# before a franchise, ending with the film that took him to Warner Bros.;
# (2) the Batman trilogy and the two films made between its instalments, which
# is also where he starts producing everything he directs; (3) three originals
# in a row at that same scale; (4) the move to Universal.
ERAS = [
    ("debut", "Before the franchise", 1998, 2002),
    ("batman", "The Batman years", 2005, 2012),
    ("originals", "Three originals in a row", 2014, 2020),
    ("universal", "Universal", 2023, 2026),
]


# Small numbers read as words in this house's copy. Spelled out rather than
# formatted so a value falling outside the table raises instead of printing a
# digit into the middle of a sentence.
WORD = {9: "nine", 13: "thirteen", 18: "eighteen"}


def hrs(m):
    return round(m / 60.0, 2)


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    films = data["films"]
    by = {f["t"]: f for f in films}

    # ---- what the source says, checked rather than remembered -------------
    assert data["source"] == "Christopher Nolan filmography", data["source"]
    assert data["feature_table_rows"] == 14, data["feature_table_rows"]
    assert len(films) == 13, [f["t"] for f in films]
    assert [(y, t) for y, t, _ in data["not_directed"]] == [(2013, "Man of Steel")], \
        data["not_directed"]
    assert films[0]["t"] == "Following" and films[0]["year"] == 1998
    assert films[-1]["t"] == "The Odyssey" and films[-1]["year"] == 2026
    assert all(f["year"] <= g["year"] for f, g in zip(films, films[1:])), \
        "films are not in release order"
    assert len({f["year"] for f in films}) == len(films), \
        "two features share a year; the release order needs a tiebreak"

    # Nothing ships that nobody can watch. Wikidata says each film published,
    # and each film's own article gives a release date already in the past —
    # the check the David Fincher list makes by hand, made from data here.
    today = datetime.date.today().isoformat()
    for f in films:
        assert f["pubyears"], "%s has no P577; is it actually out?" % f["t"]
        assert f["release_dates"], "%s has no release date" % f["t"]
        assert min(f["release_dates"]) <= today, \
            "%s is dated %s and has not opened yet" % (f["t"], min(f["release_dates"]))

    # ---- one runtime source, and only one ---------------------------------
    # A list whose bars come half from Wikidata and half from article infoboxes
    # has a total that belongs to neither source. Both halves of that are
    # asserted: every row has a runtime, and every row's runtime came from
    # Wikidata.
    assert all(f["runtime"] for f in films), \
        [f["t"] for f in films if not f["runtime"]]
    assert {f["runtime_src"] for f in films} == {"wikidata"}, \
        "mixed runtime sources: %s" % sorted({f["runtime_src"] for f in films})

    # The cross-check that makes the rule worth having: where the film's own
    # Wikipedia infobox gives a different number, and by how much. The note on
    # the list is written from this list, so it can never drift from it.
    disagree = [(f["t"], f["infobox_runtime"], f["runtime"]) for f in films
                if f["infobox_runtime"] and f["infobox_runtime"] != f["runtime"]]
    assert len(disagree) == 3, disagree
    assert dict((t, (a, b)) for t, a, b in disagree) == {
        "The Prestige": (130, 125),
        "The Dark Knight": (152, 153),
        "The Odyssey": (173, 172),
    }, disagree
    disagree_txt = ", ".join("%s %d against %d" % (t, a, b)
                             for t, a, b in disagree)

    mins = sum(f["runtime"] for f in films)
    assert mins == 1808, mins          # 30 hours 8 minutes, exactly
    hours = mins / 60.0

    # ---- the claims the intros and notes make, checked --------------------
    nowrite = [f["t"] for f in films if not f["wrote"]]
    assert nowrite == ["Insomnia"], nowrite
    assert [f["t"] for f in films if not f["produced"]] == \
        ["Memento", "Insomnia", "Batman Begins"], \
        [f["t"] for f in films if not f["produced"]]
    assert all(f["produced"] for f in films if f["year"] >= 2006), \
        "he no longer produces everything from The Prestige on"

    assert by["Following"]["budget"] == "$6,000", by["Following"]["budget"]
    assert "Warner Bros." not in by["Following"]["distributor"]
    assert "Warner Bros." not in by["Memento"]["distributor"]
    wb = [f["t"] for f in films if "Warner Bros." in f["distributor"]]
    assert wb == ["Insomnia", "Batman Begins", "The Prestige",
                  "The Dark Knight", "Inception", "The Dark Knight Rises",
                  "Interstellar", "Dunkirk", "Tenet"], wb
    assert "Buena Vista" in by["The Prestige"]["distributor"]
    assert by["Oppenheimer"]["distributor"] == "Universal Pictures"
    assert by["The Odyssey"]["distributor"] == "Universal Pictures"

    trilogy = [f["t"] for f in films
               if "comic books" in f["based_on"]["work"]]
    assert trilogy == ["Batman Begins", "The Dark Knight",
                       "The Dark Knight Rises"], trilogy
    # Insomnia's row calls it a remake of a 1997 Norwegian film; that comes
    # from its own infobox naming the earlier film and the pair who made it.
    assert by["Insomnia"]["based_on"] == {
        "work": "Insomnia",
        "by": ["Nikolaj Frobenius", "Erik Skjoldbjærg"]}, \
        by["Insomnia"]["based_on"]

    # Runtime superlatives the notes and intros lean on.
    order = sorted(films, key=lambda f: -f["runtime"])
    assert [f["t"] for f in order[:2]] == ["Oppenheimer", "The Odyssey"], \
        [f["t"] for f in order[:3]]
    assert order[-1]["t"] == "Following", order[-1]["t"]
    assert min(films[1:], key=lambda f: f["runtime"])["t"] == "Dunkirk"
    longest_by_2014 = max((f for f in films if f["year"] <= 2014),
                          key=lambda f: f["runtime"])
    assert longest_by_2014["t"] == "Interstellar", longest_by_2014["t"]
    over_two = [f["t"] for f in films if f["runtime"] > 120]
    assert len(over_two) == 9, over_two

    assert "scrapped and never released" in data["scrapped_feature_note"], \
        data["scrapped_feature_note"]
    assert [s["t"] for s in data["shorts"] if s["directed"]] == \
        ["Tarantella", "Larceny", "Doodlebug", "Quay"], data["shorts"]
    assert len(data["exec_producer"]) == 5, data["exec_producer"]

    # ---- rows --------------------------------------------------------------
    def adapted(f, kind):
        b = f["based_on"]
        assert b["work"], f["t"]
        who = " and ".join(b["by"])
        return join_bits("Adapted from %s%s" % (b["work"],
                                                ", a %s by %s" % (kind, who)
                                                if who else ""))

    NOTE = {
        "Following": join_bits(
            "Also his own cinematographer and editor",
            "Made for %s" % by["Following"]["budget"]),
        "Memento": adapted(by["Memento"], "short story"),
        "Insomnia": join_bits(
            "A remake of the 1997 Norwegian film of the same name",
            "The only one of the thirteen he did not write"),
        "Batman Begins": "The Dark Knight trilogy, 1 of 3",
        "The Prestige": adapted(by["The Prestige"], "novel"),
        "The Dark Knight": "The Dark Knight trilogy, 2 of 3",
        "The Dark Knight Rises": "The Dark Knight trilogy, 3 of 3",
        "Dunkirk": "His shortest feature since Following",
        "Oppenheimer": join_bits(adapted(by["Oppenheimer"], "biography"),
                                 "His longest feature"),
        "The Odyssey": adapted(by["The Odyssey"], ""),
    }
    assert by["Following"]["tableefn"] == "Also cinematographer and editor", \
        by["Following"]["tableefn"]
    assert "Christopher Priest" in NOTE["The Prestige"], NOTE["The Prestige"]
    assert "Jonathan Nolan" in NOTE["Memento"], NOTE["Memento"]
    assert "Kai Bird" in NOTE["Oppenheimer"], NOTE["Oppenheimer"]
    assert NOTE["The Odyssey"] == "Adapted from Homer's Odyssey", \
        NOTE["The Odyssey"]

    INTRO = {
        "debut": "Following was made for %s and runs %d minutes, the shortest "
                 "thing here by a distance. Memento came from a short story "
                 "his brother Jonathan wrote. Insomnia, a remake of a Norwegian "
                 "film, was his first for Warner Bros. — and the only one of "
                 "the thirteen he did not write."
                 % (by["Following"]["budget"], by["Following"]["runtime"]),
        "batman": "Five films in seven years: a Batman trilogy, with The "
                  "Prestige and Inception made between its instalments. From "
                  "The Prestige onward he produces everything he directs, and "
                  "Warner Bros. is on all five — though The Prestige went out "
                  "through Buena Vista in the United States.",
        "originals": "No franchise behind any of the three, and all three made "
                     "at the scale the Batman films had bought him. "
                     "Interstellar, at %d minutes, was the longest he had made "
                     "to that point; Dunkirk, at %d, is still the shortest "
                     "since his debut."
                     % (by["Interstellar"]["runtime"], by["Dunkirk"]["runtime"]),
        "universal": "Two films for Universal, after %s years in which Warner "
                     "Bros. was on the release of every film he directed. They "
                     "are also the two longest he has made: %d minutes and %d."
                     % (WORD[by["Tenet"]["year"] - by["Insomnia"]["year"]],
                        by["Oppenheimer"]["runtime"],
                        by["The Odyssey"]["runtime"]),
    }

    sections, placed = [], []
    for key, title, lo, hi in ERAS:
        got = [f for f in films if lo <= f["year"] <= hi]
        assert got, key
        placed += got
        smins = sum(f["runtime"] for f in got)
        items = []
        for f in got:
            it = {"id": "cn-%d-%s" % (f["year"], slug(f["t"])),
                  "t": f["t"], "n": str(f["year"]), "w": hrs(f["runtime"])}
            if f["t"] in NOTE:
                it["note"] = NOTE[f["t"]]
            items.append(it)
        sections.append({
            "id": key, "title": title,
            "sub": "%d–%d · %d films · %d hours"
                   % (got[0]["year"], got[-1]["year"], len(got),
                      round(smins / 60.0)),
            "intro": INTRO[key],
            "items": items,
        })
    sections[0]["open"] = True

    # ---- the arithmetic, checked ------------------------------------------
    assert placed == films, "a film was dropped or placed twice"
    assert sum(len(s["items"]) for s in sections) == 13
    for s in sections:
        assert all(a["n"] <= b["n"] for a, b in zip(s["items"], s["items"][1:])), \
            "%s is out of year order" % s["title"]
    # The section minutes must reconstitute the exact total, and the rounded
    # hours the section headings print must add to the rounded total. Rounding
    # thirteen numbers and adding them is how a list ends up advertising an
    # hour it does not have.
    sec_mins = [sum(f["runtime"] for f in films
                    if lo <= f["year"] <= hi) for _, _, lo, hi in ERAS]
    assert sum(sec_mins) == mins, (sec_mins, mins)
    printed = sum(round(m / 60.0) for m in sec_mins)
    assert printed == round(hours), \
        "section headings add to %d hours, the real total rounds to %d" \
        % (printed, round(hours))
    # And the bar widths, which are rounded to two decimals per row, must not
    # drift from the true total either.
    barsum = sum(x["w"] for s in sections for x in s["items"])
    assert abs(barsum - hours) < 0.05, (barsum, hours)

    p = {
        "slug": SLUG,
        "title": "Christopher Nolan",
        "subtitle": "the directed features",
        "kind": "films",
        "popularity": 80,
        "year": "1998–2026",
        "blurb": "Thirteen features in release order, from a $6,000 debut to "
                 "The Odyssey — %d hours and %d minutes of them, %s of the "
                 "%s running over two hours each."
                 % (mins // 60, mins % 60, WORD[len(over_two)],
                    WORD[len(films)]),
        "unit": {"one": "film", "many": "films"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "accent": "#0985C3",
        "accentDark": "#2E96B2",
        "tiers": False,
        "notes": [
            ["Thirteen, not fourteen.", "The filmography's Feature film table "
             "has fourteen rows. The fourteenth is Man of Steel (2013), and "
             "its Director cell says no: Nolan produced that film and wrote "
             "its story, and Zack Snyder directed it. Only a bare director "
             "credit puts a film on this list."],
            ["Directed features only.", "Out: the films he produced or "
             "executive produced for other directors — Man of Steel, "
             "Transcendence, Batman v Superman, both cuts of Justice League, "
             "and Sanatorium Under the Sign of the Hourglass. Also out: the "
             "four shorts he directed — Tarantella, Larceny, Doodlebug and "
             "Quay — which the source keeps in a separate table under its own "
             "heading and does not treat as features. Either set can be added "
             "if the list would rather have them."],
            ["Bar widths are runtimes.", "From Wikidata, in hours, for all "
             "thirteen — %d hours %d minutes in total. Every runtime comes "
             "from that one source and the generator refuses to build "
             "otherwise, because three of the films' own Wikipedia infoboxes "
             "give a different number (%s). Picking whichever is handier "
             "per film would produce a total belonging to no source at all."
             % (mins // 60, mins % 60, disagree_txt)],
            ["It starts at Following because the source does.", "A footnote "
             "on the filmography records a feature called Larry Mahoney that "
             "Nolan directed in the mid-1990s; it was scrapped and never "
             "released. There is nothing to watch and no runtime to weigh, so "
             "it is mentioned here rather than listed above."],
            "Filmography from Wikipedia's Christopher Nolan filmography, read "
            "from the enumerated tables and not from its prose; runtimes from "
            "Wikidata (P2047), gated on a matching release year.",
        ],
        "sections": sections,
    }

    out = prop.write(p)
    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == 13, len(ids)
    print("wrote %s — %d films, %d min = %.2f hours (prints as %d)"
          % (out.name, len(ids), mins, hours, round(hours)))
    print("   bar widths sum to %.2f hours; section headings print %d"
          % (barsum, printed))
    for s in sections:
        print("   %-26s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
