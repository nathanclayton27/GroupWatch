#!/usr/bin/env python3
"""Generate properties/buffy-angel.json — Buffy and Angel woven in air order.

    python3 tools/make_buffy-angel.py

All 144 Buffy the Vampire Slayer episodes and all 110 Angel episodes as one
254-row broadcast-order list — the comics-weave treatment applied to TV.
Sections follow the broadcast year-pairs: Buffy seasons 1-3 alone, then four
overlap years (Buffy S4 + Angel S1 through Buffy S7 + Angel S4) interleaved
strictly by the tables' original air dates, then Angel season 5 alone. Where
both shows aired the same night the Buffy episode is listed first — The WB
ran them back-to-back with Buffy in the earlier slot.

Episode titles and air dates are machine-read from the twelve Wikipedia
season articles by scratch/agent-tv2/fetch_buffy_angel.py, which asserts each
season's numbering against the article's own infobox count and both series
totals (144, 110); the committed result is tools/data/buffy-angel.json. This
script re-asserts all of it, plus the air dates behind every note it writes.

Buffy season 3 is listed in the table's episode order: two late-season
episodes were postponed on broadcast ("Earshot" to September 1999,
"Graduation Day, Part Two" to July 1999) and their rows say so.

Nothing is weighted: an episode counts as one.
"""
import json
import pathlib
import re

SLUG = "buffy-angel"
BUFFY_EXPECT = {1: 12, 2: 22, 3: 22, 4: 22, 5: 22, 6: 22, 7: 22}
ANGEL_EXPECT = {1: 22, 2: 22, 3: 22, 4: 22, 5: 22}
TOTAL = 254
# the woven years: (buffy season, angel season)
PAIRS = [(4, 1), (5, 2), (6, 3), (7, 4)]

# one-line factual notes for the direct same-night crossovers, keyed
# (show, season, episode); air-date equality is asserted below
CROSSOVER_NOTES = {
    ("buffy", 4, 8): 'Continues directly into Angel\'s "I Will Remember '
                     'You", aired the same night',
    ("angel", 1, 8): 'Picks up directly from Buffy\'s "Pangs", aired the '
                     'same night',
    ("buffy", 5, 7): 'Companion half of a two-show flashback story — '
                     'Angel\'s "Darla" aired the same night',
    ("angel", 2, 7): 'Companion half of a two-show flashback story — '
                     'Buffy\'s "Fool for Love" aired the same night',
}
POSTPONED = {
    ("buffy", 3, 18): ("Earshot", "1999-09-21",
                       "Broadcast postponed to September 1999; listed in "
                       "its season position, as the table files it"),
    ("buffy", 3, 22): ("Graduation Day (Part 2)", "1999-07-13",
                       "Broadcast postponed to July 1999"),
}


def year_span(rows):
    ys = sorted({int(r["air"][:4]) for r in rows if r.get("air")})
    assert ys, "no airdates"
    if ys[0] == ys[-1]:
        return str(ys[0])
    a, b = ys[0], ys[-1]
    return "%d–%02d" % (a, b % 100) if a // 100 == b // 100 else "%d–%d" % (a, b)


def main():
    data = json.loads((pathlib.Path(__file__).resolve().parent / "data"
                       / "buffy-angel.json").read_text(encoding="utf-8"))
    buffy, angel = data["buffy"], data["angel"]

    for src, expect in (("buffy", BUFFY_EXPECT), ("angel", ANGEL_EXPECT)):
        for n, want in expect.items():
            rows = data[src][str(n)]
            assert [r["e"] for r in rows] == list(range(1, want + 1)), \
                "%s season %d numbering incomplete" % (src, n)
            assert all(r["air"] for r in rows), (src, n)
    assert sum(len(v) for v in buffy.values()) == 144
    assert sum(len(v) for v in angel.values()) == 110

    # the air dates every note stands on
    for (show, s, e), (title, air, _) in POSTPONED.items():
        r = data[show][str(s)][e - 1]
        assert (r["t"], r["air"]) == (title, air), r
    pangs = buffy["4"][7]
    remember = angel["1"][7]
    assert pangs["t"] == "Pangs" and remember["t"] == "I Will Remember You"
    assert pangs["air"] == remember["air"] == "1999-11-23"
    fool = buffy["5"][6]
    darla = angel["2"][6]
    assert fool["t"] == "Fool for Love" and darla["t"] == "Darla"
    assert fool["air"] == darla["air"] == "2000-11-14"

    prefix = {"buffy": ("Buffy", "bf"), "angel": ("Angel", "an")}

    def item(show, season, r):
        label, pid = prefix[show]
        row = {"id": "%s-s%d-%d" % (pid, season, r["e"]),
               "t": "%s — %s" % (label, r["t"]),
               "n": "%dx%02d" % (season, r["e"])}
        note = CROSSOVER_NOTES.get((show, season, r["e"]))
        if (show, season, r["e"]) in POSTPONED:
            note = POSTPONED[(show, season, r["e"])][2]
        if note:
            row["note"] = note
        return row

    def solo_section(show, season, sec_id, title):
        rows = data[show][str(season)]
        return {"id": sec_id, "title": title,
                "sub": "%s · %d episodes" % (year_span(rows), len(rows)),
                "items": [item(show, season, r) for r in rows]}

    def woven_section(bs, as_):
        brows = [("buffy", bs, r) for r in buffy[str(bs)]]
        arows = [("angel", as_, r) for r in angel[str(as_)]]
        # strict air-date interleave; on a shared night Buffy airs first
        merged = sorted(brows + arows,
                        key=lambda x: (x[2]["air"], x[0] != "buffy", x[2]["e"]))
        # the weave must preserve each show's own episode order
        for src in ("buffy", "angel"):
            eps = [x[2]["e"] for x in merged if x[0] == src]
            assert eps == sorted(eps), (bs, as_, src)
        rows = [x[2] for x in merged]
        return {"id": "w%d" % bs,
                "title": "Buffy S%d + Angel S%d" % (bs, as_),
                "sub": "%s · %d episodes, woven by air date"
                       % (year_span(rows), len(merged)),
                "items": [item(*x) for x in merged]}

    sections = [solo_section("buffy", n, "b%d" % n, "Buffy Season %d" % n)
                for n in (1, 2, 3)]
    sections[0]["open"] = True
    for bs, as_ in PAIRS:
        sections.append(woven_section(bs, as_))
    sections[3]["intro"] = ("Angel begins. From here to May 2003 the two "
                            "shows ran side by side and the rows follow the "
                            "original air dates, whichever show is next.")
    sections.append(solo_section("angel", 5, "a5", "Angel Season 5"))

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert all(re.fullmatch(r"[a-z0-9-]+", i) for i in ids)
    assert len(ids) == TOTAL, len(ids)

    prop = {
        "slug": SLUG,
        "title": "Buffy & Angel",
        "subtitle": "two shows woven into one broadcast order",
        "kind": "tv",
        "popularity": 68,
        "year": "1997–2004",
        "blurb": "All 144 Buffy and 110 Angel episodes in one air-order "
                 "list — four overlap years interleaved night by night.",
        "unit": {"one": "episode", "many": "episodes"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": "#6E4530",
        "accentDark": "#FF7EB6",
        "tiers": False,
        "notes": [
            ["One list, two shows.", "From October 1999 to May 2003 the "
             "shows ran side by side; those years are interleaved strictly "
             "by original air date, read from the season tables."],
            ["Same night, Buffy first.", "Where both shows aired on the "
             "same date, the Buffy episode is listed first — The WB ran "
             "them back-to-back with Buffy in the earlier slot."],
            ["Crossovers are noted, not moved.", "The two stories that "
             "continue directly into the other show the same night carry a "
             "one-line note on each half."],
            "Episode titles and air dates machine-read from the twelve "
            "Wikipedia season articles (Buffy the Vampire Slayer seasons "
            "1–7, Angel seasons 1–5); both series totals (144, 110) and "
            "every season's numbering are asserted before this builds.",
        ],
        "sections": sections,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json — %d rows in %d sections" % (SLUG, len(ids),
                                                      len(sections)))
    for s in sections:
        b = sum(1 for x in s["items"] if x["id"].startswith("bf-"))
        a = sum(1 for x in s["items"] if x["id"].startswith("an-"))
        print("   %-24s %3d  (%d buffy, %d angel)  %s"
              % (s["title"], len(s["items"]), b, a, s.get("sub", "")))


if __name__ == "__main__":
    main()
