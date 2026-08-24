#!/usr/bin/env python3
"""Generate properties/mst3k.json — every experiment, KTMA to the Gizmoplex.

    python3 tools/make_mst3k.py

One row per experiment, titled by the film riffed, numbered by episode code
(512 = season 5, episode 12; KTMA episodes are K01-K21): the KTMA-TV season
(optional — it aired only in Minneapolis before the national run, and its
unaired pilot K00 rides along), seasons 1-7 on The Comedy Channel / Comedy
Central, the 1996 theatrical movie in its place, seasons 8-10 on the Sci-Fi
Channel, and the revival seasons — 11-12 on Netflix, 13 on the Gizmoplex.
232 rows.

Season 14 (MST3K: The RiffTrax Experiments) starts airing September 2026 and
is deliberately absent until it has aired.

Everything is machine-read from "List of Mystery Science Theater 3000
episodes" by scratch/agent-tv1/extract_mst3k.py, which asserts each season's
row count against the article's own series overview; the committed result is
tools/data/mst3k-episodes.json. K03's note follows the article: long lost,
it resurfaced in March 2026.
"""
import json
import pathlib

SLUG = "mst3k"

ERA = {1: "the national run begins, on The Comedy Channel",
       8: "the Sci-Fi Channel years begin",
       11: "the Netflix revival begins",
       13: "the Gizmoplex season"}


def main():
    data = json.loads((pathlib.Path(__file__).resolve().parent / "data"
                       / "mst3k-episodes.json").read_text(encoding="utf-8"))

    sections = []
    for s in data["sections"]:
        if s["kind"] == "movie":
            r = s["rows"][0]
            sections.append({
                "id": "movie", "title": "The Movie",
                "sub": "1996 · the theatrical feature, between seasons 7 and 8",
                "items": [{"id": "mst-movie", "t": r["t"], "n": "1996",
                           "note": "%d film · riffed in theatres" % r["film_year"]}],
            })
            continue
        items = []
        for r in s["rows"]:
            row = {"id": "mst-%s" % r["code"].lower(), "t": r["t"],
                   "n": r["code"],
                   "note": "%d film" % r["film_year"]}
            if r["note_unaired"]:
                row["note"] += " · the unaired pilot"
            if r["code"] == "K03":
                row["note"] += " · long lost, resurfaced in 2026"
            if s["kind"] == "ktma":
                row["opt"] = True
            items.append(row)
        if s["kind"] == "ktma":
            sec = {"id": "k", "title": "KTMA (Season 0)",
                   "sub": "%s · 21 episodes + the unaired pilot · optional"
                          % s["years"],
                   "intro": "The year on Minneapolis's KTMA-TV, before the "
                            "national run. One episode was lost for decades. "
                            "Start at season 1 unless you want all of it.",
                   "items": items}
        else:
            n = s["season"]
            sub = "%s · %d episodes" % (s["years"], len(items))
            if n in ERA:
                sub += " · " + ERA[n]
            sec = {"id": "s%d" % n, "title": "Season %d" % n,
                   "sub": sub, "items": items}
            if n == 1:
                sec["open"] = True
        sections.append(sec)

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert len(ids) == 232, len(ids)
    assert sum(1 for s in sections for x in s["items"] if x.get("opt")) == 22
    assert [s["id"] for s in sections] == (
        ["k"] + ["s%d" % i for i in range(1, 8)] + ["movie"]
        + ["s%d" % i for i in range(8, 14)])
    assert [e["why"] for e in data["excluded"]] == ["unaired"] * 4

    prop = {
        "slug": SLUG,
        "title": "Mystery Science Theater 3000",
        "subtitle": "every experiment, KTMA to the Gizmoplex",
        "kind": "tv",
        "popularity": 46,
        "year": "1988–2022",
        "blurb": "All 232 experiments in air order — the KTMA year, the "
                 "cable runs, the movie, and the revivals, each row the film "
                 "it riffs.",
        "unit": {"one": "episode", "many": "episodes"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "accent": "#7A6200",
        "accentDark": "#F2C230",
        "tiers": False,
        "notes": [
            ["One row per experiment.", "The number is the episode code — 512 "
             "is season 5, episode 12; KTMA episodes are K01–K21 — and the "
             "title is the film riffed. Each row's note carries that film's "
             "release year, as the episode list files it."],
            ["KTMA is optional.", "The 1988–89 season aired only on "
             "Minneapolis's KTMA-TV, before the national run; one of its "
             "episodes, long lost, resurfaced only in 2026. Its 21 episodes "
             "and the unaired pilot K00 are marked optional."],
            ["Season 14 is not here yet.", "MST3K: The RiffTrax Experiments "
             "begins airing in September 2026; its episodes belong here once "
             "they have aired."],
            "Machine-read from Wikipedia's List of Mystery Science Theater "
            "3000 episodes; every season's row count is asserted against the "
            "article's own series overview before this builds.",
        ],
        "sections": sections,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json — %d rows" % (SLUG, len(ids)))
    for s in sections:
        print("   %-18s %3d  %s" % (s["title"], len(s["items"]), s.get("sub", "")[:52]))


if __name__ == "__main__":
    main()
