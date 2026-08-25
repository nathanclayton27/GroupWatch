#!/usr/bin/env python3
"""Generate properties/raimi.json.

    PYTHONIOENCODING=utf-8 python tools/make_raimi.py

Every feature Sam Raimi has directed, in release order — the seventeen rows
whose Director cell is a bare {{yes}} in the Filmography > Film table on
Wikipedia's Sam Raimi article — plus all thirty episodes of Ash vs Evil Dead,
which the list's owner asked for by name.

The show is the honest problem here. Raimi developed Ash vs Evil Dead with
Ivan Raimi and Tom Spezialy, executive produced all three seasons, and
directed exactly one of the thirty episodes: the pilot, "El Jefe", which he
also co-wrote. So the section's title, its sub and its intro all say so, and
every episode row names the director who actually made it — read out of the
article's own DirectedBy fields, never assumed. A list called "Sam Raimi" that
showed thirty episodes with no attribution would be telling a lie by layout.

What stays out, and can be argued back in cheaply:
  * the films he produced or executive produced for other directors — the 2013
    Evil Dead, Evil Dead Rise, Don't Breathe, both Grudges, Crawl, 65 — because
    this is a directing list plus the one show that was asked for;
  * his television directing outside Ash vs Evil Dead: two episodes of Rake
    (2014) and three of 50 States of Fright (2020);
  * the films he only wrote (Easy Wheels, The Nutt House), the second-unit
    directing on The Hudsucker Proxy, the acting, and the shorts — Within the
    Woods and The Black Ghiandola included.

What carries hours, and what does not. The seventeen films are weighted from
Wikidata P2047, read at statement rank — the collector honours preferred and
drops deprecated, because gwlib's rank-blind reader takes the longest value
and Doctor Strange in the Multiverse of Madness carries a *preferred* 126
beside a normal 127. The pilot is weighted too, at the 41 minutes its own
article's infobox states and the series infobox repeats.

The other twenty-nine episodes carry `w: 0` and `opt: 1`. Zero is deliberate
and load-bearing: a row with no `w` at all in a weighted list is silently
worth one hour downstream, so leaving them bare would inject twenty-nine
invented hours into real finish-date maths. `opt: 1` is only the OPTIONAL
chip — it does not exclude a row from the total, so it is never used alone
here. The twenty-nine still tick and still draw their marks; they simply add
nothing to the clock, because no per-episode runtime for them is published:
the series infobox gives a range, and the collector re-checks all thirty
Wikidata episode items and finds P2047 on none of them.

Data: scratch/raimi/collect.py -> scratch/raimi/raimi_data.json
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop
from gwlib.prop import slug

SLUG = "raimi"
DATA = pathlib.Path(__file__).resolve().parent.parent / "scratch" / "raimi" / "raimi_data.json"

# Film sections, chronological. Ash vs Evil Dead sits between them at 2015,
# where it belongs in the run of the career — the x-files rule, which puts the
# films between the seasons they were made between rather than in an appendix.
ERAS = [
    ("evildead", "The Evil Dead years", 1978, 1992,
     "A Super 8 feature made while he was a student at Michigan State, the "
     "three Evil Dead films, a comedy he wrote with the Coen brothers, and a "
     "superhero picture of his own. He has a writing credit on all six."),
    ("nineties", "Out of the woods", 1995, 2000,
     "A revisionist Western, a neo-noir, a baseball picture and a Southern "
     "Gothic thriller. He directed all four and wrote none of them."),
    ("spiderman", "Spider-Man", 2002, 2007,
     "Three films in five years. He takes a screenplay credit on the third "
     "and on neither of the first two."),
    ("late", "After the trilogy", 2009, 2013,
     "A horror picture with his name on the screenplay, and then a Disney "
     "tentpole without it."),
    (None, None, None, None, None),        # Ash vs Evil Dead is spliced here
    ("recent", "The return", 2022, 2026,
     "Nine years after Oz, a Marvel film — and a survival picture four years "
     "after that."),
]


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    films, eps, series = data["films"], data["episodes"], data["series"]

    # ---- films -----------------------------------------------------------
    assert len(films) == 17, len(films)
    assert films[0]["t"] == "It's Murder!" and films[-1]["t"] == "Send Help", \
        (films[0]["t"], films[-1]["t"])
    assert all(f["year"] <= g["year"] for f, g in zip(films, films[1:])), \
        "films are not in release order"
    # every runtime from one source, so no row is quietly a different kind of
    # number from its neighbours (Wikidata says 70 for It's Murder!, the
    # article's own infobox says 71 — pick one source and keep to it)
    assert all(f["runtime"] and f["runtime_src"] == "wikidata" for f in films), \
        [f["t"] for f in films if f["runtime_src"] != "wikidata"]
    # a film the table lists but nothing has released has no P577; Send Help
    # is on this list because Wikidata says it came out, not because the table
    # printed a year
    assert all(f["pubyears"] for f in films), \
        [f["t"] for f in films if not f["pubyears"]]

    amateur = [f for f in films if "Amateur film" in f["tablenote"]]
    assert [f["t"] for f in amateur] == ["It's Murder!"], amateur

    # the claims the era intros make, checked rather than trusted
    early = [f for f in films if f["year"] <= 1992]
    assert len(early) == 6 and all(f["wrote"] for f in early), early
    assert [f["wrote"] for f in films if 1995 <= f["year"] <= 2000] == \
        [False, False, False, False]
    assert [f["wrote"] for f in films if 2002 <= f["year"] <= 2007] == \
        [False, False, True]
    assert [f["wrote"] for f in films if 2009 <= f["year"] <= 2013] == \
        [True, False]
    gap = [f["year"] for f in films if f["year"] > 2013][0] - 2013
    assert gap == 9, gap
    assert films[-1]["year"] - films[-2]["year"] == 4, films[-1]["year"]

    # ---- episodes --------------------------------------------------------
    seasons = sorted({e["season"] for e in eps})
    assert seasons == [1, 2, 3], seasons
    # The infobox count, the {{Series overview}} box and the enumerated
    # {{Episode list}} rows all say thirty. If they ever disagree the
    # enumerated rows are the truth and this assert is what turns the
    # disagreement into a failed build instead of a quietly wrong list.
    assert len(eps) == 30, len(eps)
    assert series["declared_episodes"] == len(eps), \
        "infobox says %s, the episode tables enumerate %d — the tables win" \
        % (series["declared_episodes"], len(eps))
    assert sum(series["overview"].values()) == len(eps), \
        "Series overview says %s, the episode tables enumerate %d — the " \
        "tables win" % (series["overview"], len(eps))
    for n in seasons:
        got = [e["num"] for e in eps if e["season"] == n]
        assert got == list(range(1, 11)), (n, got)
        assert series["overview"][str(n)] == len(got), \
            "season %d: overview %s vs %d enumerated — the table wins" \
            % (n, series["overview"][str(n)], len(got))
    assert [e["overall"] for e in eps] == list(range(1, 31))

    # the attribution the section header makes, checked against the data
    assert "Sam Raimi" in series["developer"], series["developer"]
    assert "Sam Raimi" in series["executive_producer"], series["executive_producer"]
    his = [e for e in eps if e["director"] == "Sam Raimi"]
    assert len(his) == 1 and (his[0]["season"], his[0]["num"]) == (1, 1), his
    assert his[0]["t"] == "El Jefe", his[0]["t"]
    assert "Sam Raimi" in his[0]["writers"], his[0]["writers"]
    assert all(e["director"] for e in eps), \
        [e["t"] for e in eps if not e["director"]]
    assert not any("Sam Raimi" in e["director"] for e in eps if e is not his[0]), \
        "a second Raimi-directed episode appeared"
    # The pilot is the only episode with a published runtime. The series
    # infobox states a range for the rest and the collector, having looked up
    # all thirty episode items, found P2047 on none of them — which is what
    # licenses the other twenty-nine to weigh zero. If either ever changes,
    # this fails and the decision gets revisited.
    assert "–" in series["runtime_field"], series["runtime_field"]
    assert series["episodes_with_wikidata_item"] == len(eps), series
    assert series["episodes_with_wikidata_runtime"] == 0, \
        "an episode grew a Wikidata runtime — reweigh instead of zeroing"
    pilot_min = series["pilot_runtime"]
    assert his[0]["runtime"] == pilot_min and 15 <= pilot_min <= 90, series
    assert all(e["runtime"] is None for e in eps if e is not his[0]), \
        [e["t"] for e in eps if e is not his[0] and e["runtime"]]

    # ---- sections --------------------------------------------------------
    def film_section(key, title, lo, hi, intro):
        got = [f for f in films if lo <= f["year"] <= hi]
        assert got, key
        items = []
        for f in got:
            it = {"id": "sr-%d-%s" % (f["year"], slug(f["t"])),
                  "t": f["t"], "n": str(f["year"]),
                  "w": round(f["runtime"] / 60.0, 2)}
            # Writing credits live in the era intros, which can say "all six"
            # or "none of them" without repeating one note down every row —
            # and without a per-row note having to guess sole against shared
            # authorship, which the source's tick-box column does not record.
            if f in amateur:
                it["opt"] = 1
                it["note"] = ("Amateur Super 8 feature, made while he was a "
                              "student")
            items.append(it)
        n = len(got) - sum(1 for f in got if f in amateur)
        sub = "%d–%d · %d film%s" % (got[0]["year"], got[-1]["year"], n,
                                     "s" if n > 1 else "")
        if len(got) > n:
            sub += " + 1 optional"
        sub += " · about %d hours" % round(sum(f["runtime"] for f in got) / 60.0)
        return {"id": key, "title": title, "sub": sub, "intro": intro,
                "items": items}

    def ash_section():
        items = []
        for e in eps:
            it = {"id": "sr-aved-s%de%02d" % (e["season"], e["num"]),
                  "t": e["t"],
                  "n": "S%dE%d" % (e["season"], e["num"])}
            if e is his[0]:
                # the one episode with a runtime anyone published
                it["w"] = round(pilot_min / 60.0, 2)
                it["note"] = "Directed by Sam Raimi, who also co-wrote it"
            else:
                # w:0 is what keeps these out of the hours — `opt` is only the
                # chip and would leave each of them silently worth an hour
                it["w"] = 0
                it["opt"] = 1
                it["note"] = "Directed by %s" % e["director"]
            items.append(it)
        return {
            "id": "ashvsevildead",
            "title": "Ash vs Evil Dead — he directed the pilot",
            "sub": "2015–2018 · 30 episodes on %s, 29 of them optional · "
                   "developed and executive produced by Raimi, who directed "
                   "1 of the 30 · %d minutes"
                   % (series["channel"], pilot_min),
            "intro": "The one television series on this list, and it is here "
                     "because it was asked for. Raimi developed Ash vs Evil "
                     "Dead with Ivan Raimi and Tom Spezialy, executive "
                     "produced all three seasons, and directed exactly one "
                     "episode — the pilot, El Jefe, which he also co-wrote. "
                     "The other 29 were directed by other people, and every "
                     "row names the director who made it, so nothing here "
                     "reads as his that was not. The pilot carries its %d "
                     "minutes; the other 29 are marked optional and carry no "
                     "hours, because no runtime for them is published "
                     "anywhere. They tick all the same." % pilot_min,
            "items": items,
        }

    sections = []
    for key, title, lo, hi, intro in ERAS:
        if key is None:
            sections.append(ash_section())
            continue
        sec = film_section(key, title, lo, hi, intro)
        if key == "evildead":
            sec["open"] = True
        sections.append(sec)

    placed = sum(len(s["items"]) for s in sections if s["id"] != "ashvsevildead")
    assert placed == len(films), (placed, len(films))
    for s in sections:
        if s["id"] == "ashvsevildead":
            continue
        assert all(a["n"] <= b["n"] for a, b in zip(s["items"], s["items"][1:])), \
            "%s is out of year order" % s["title"]
    # the show sits where it happened, not in an appendix
    order = [s["id"] for s in sections]
    assert order.index("late") < order.index("ashvsevildead") < order.index("recent")

    mins = sum(f["runtime"] for f in films)

    # ---- the weighting, checked against what the page will actually total --
    rows = [x for s in sections for x in s["items"]]
    assert all("w" in x for x in rows), \
        [x["id"] for x in rows if "w" not in x]     # a bare row is worth 1h
    paid = [x for x in rows if x["w"] > 0]
    free = [x for x in rows if x["w"] == 0]
    assert len(paid) == len(films) + 1 == 18, len(paid)
    assert len(free) == len(eps) - 1 == 29, len(free)
    # the chip never travels without the zero, or those 29 cost an hour each
    assert all(x.get("opt") == 1 for x in free), \
        [x["id"] for x in free if x.get("opt") != 1]
    hours = round(sum(x["w"] for x in rows), 2)
    want = round(sum(round(f["runtime"] / 60.0, 2) for f in films)
                 + round(pilot_min / 60.0, 2), 2)
    assert hours == want, (hours, want)
    # and the same number the honest way: the films plus the one episode
    assert abs(hours - (mins + pilot_min) / 60.0) < 0.2, \
        (hours, (mins + pilot_min) / 60.0)

    p = {
        "slug": SLUG,
        "title": "Sam Raimi",
        "subtitle": "the directed features, plus Ash vs Evil Dead",
        "kind": "films & tv",
        "popularity": 58,
        "year": "1978–2026",
        "blurb": "Seventeen directed features, from a Super 8 student film to "
                 "Send Help — about %d hours of them — plus all 30 episodes "
                 "of Ash vs Evil Dead, the series he developed and directed "
                 "one episode of." % round(mins / 60.0),
        "unit": {"one": "entry", "many": "entries"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "accent": "#460971",
        "accentDark": "#1DED99",
        "tiers": False,
        "notes": [
            ["29 of the 30 episodes are not his.", "Ash vs Evil Dead is on a "
             "list called Sam Raimi because it was asked for by name, so it "
             "says what it is: he developed the series with Ivan Raimi and "
             "Tom Spezialy, executive produced all three seasons, and "
             "directed the pilot. Every other row names the director who "
             "actually made it."],
            ["Directing only, with that one exception.", "The films he "
             "produced or executive produced for other directors are not "
             "here — the 2013 Evil Dead, Evil Dead Rise, Don't Breathe, both "
             "Grudges, Crawl, 65. Neither are the films he only wrote, the "
             "second-unit work on The Hudsucker Proxy, the acting, the "
             "shorts, or the television he directed outside this show: two "
             "episodes of Rake and three of 50 States of Fright."],
            ["It's Murder! is an optional row.", "The Super 8 feature he made "
             "as a student at Michigan State. The filmography's own table "
             "lists it with the features and marks it an amateur film, so it "
             "rides along, marked the same way. It still carries its %d "
             "minutes: optional is a label on a row, not a hole in the "
             "total — the 29 episodes carry none for a different reason, "
             "which is that nobody publishes one."
             % amateur[0]["runtime"]],
            ["The films and the pilot carry the hours.", "All 17 films have "
             "verified runtimes, and so does the one episode he directed — "
             "El Jefe, %d minutes — which is where the %d hours on this list "
             "come from. The other 29 episodes are marked optional and carry "
             "no hours at all, because no per-episode runtime for them is "
             "published anywhere: the series article gives only a range and "
             "not one of the 30 Wikidata episode items carries a runtime. "
             "They tick like everything else; they just do not move a finish "
             "date." % (pilot_min, round(hours))],
            "Filmography and episode directors from Wikipedia's Sam Raimi and "
            "Ash vs Evil Dead articles, read from the tables themselves; film "
            "runtimes from Wikidata, gated on a matching release year and "
            "read at statement rank; the pilot's from the infobox of its own "
            "article.",
        ],
        "sections": sections,
    }

    out = prop.write(p)
    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == 47, len(ids)
    print("wrote %s — %d rows (%d films + %d episodes); %.2f hours = "
          "%d films (%d min) + the pilot (%d min); %d weighted, %d at zero"
          % (out.name, len(ids), len(films), len(eps), hours, len(films),
             mins, pilot_min, len(paid), len(free)))
    for s in sections:
        print("   %-42s %2d  %s" % (s["title"][:42], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
