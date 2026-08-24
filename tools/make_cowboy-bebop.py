#!/usr/bin/env python3
"""Generate properties/cowboy-bebop.json.

    python tools/make_cowboy-bebop.py

The 26 sessions in broadcast order, then Knockin' on Heaven's Door (2001) as
its own one-row section. Session numbers and titles are machine-read from
Wikipedia's "List of Cowboy Bebop episodes" by scratch/agent-anime/
harvest_bebop.py, which asserts the numbering runs 1-26 with no gaps; the
film's year and runtime come from its own article's infobox. The committed
result is tools/data/cowboy-bebop.json.

Because the page mixes a film with episodes, everything is weighted so the
strip stays honest: sessions at 0.4h, the film at runtime/60. The "Mish-Mash
Blues" recap special and the 2021 Netflix live action are out; the notes say
so.
"""
import json
import pathlib

SLUG = "cowboy-bebop"

DATA = pathlib.Path(__file__).resolve().parent / "data" / (SLUG + ".json")
OUT = pathlib.Path(__file__).resolve().parent.parent / "properties" / (SLUG + ".json")

EP_W = 0.4


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    sessions, film = data["sessions"], data["film"]

    assert [s["n"] for s in sessions] == list(range(1, 27))
    assert data["skipped_special"] == "Mish-Mash Blues"

    film_w = round(film["runtime"] / 60.0, 2)
    series_h = len(sessions) * EP_W

    sections = [
        {
            "id": "sessions",
            "title": "The series",
            "sub": "1998–99 · 26 sessions · about %d hours" % round(series_h),
            "intro": "Every session, in order. The show files its episodes "
                     "as sessions, so that is what the counter calls them.",
            "links": [{"label": "The episode list",
                       "url": "https://en.wikipedia.org/wiki/"
                              "List_of_Cowboy_Bebop_episodes"}],
            "open": True,
            "items": [{"id": "bebop-%d" % s["n"], "t": s["t"],
                       "n": str(s["n"]), "w": EP_W} for s in sessions],
        },
        {
            "id": "film",
            "title": "Knockin' on Heaven's Door",
            "sub": "2001 · the film, set between sessions 22 and 23",
            "links": [{"label": "The film",
                       "url": "https://en.wikipedia.org/wiki/"
                              "Cowboy_Bebop:_The_Movie"}],
            "items": [{"id": "bebop-film-2001",
                       "t": "%s (%s)" % (film["t"], film["aka"]),
                       "n": str(film["year"]), "w": film_w,
                       "note": "%d min" % film["runtime"]}],
        },
    ]

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert len(ids) == 27, len(ids)
    hours = sum(x["w"] for s in sections for x in s["items"])

    prop = {
        "slug": SLUG,
        "title": "Cowboy Bebop",
        "subtitle": "the 26 sessions and the film",
        "kind": "anime",
        "popularity": 73,
        "year": "1998–2001",
        "blurb": "All 26 sessions and Knockin' on Heaven's Door — about %d "
                 "hours of bounty hunting, in order." % round(hours),
        "unit": {"one": "session", "many": "sessions"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": "#2B3A67",
        "accentDark": "#FF5C5C",
        "tiers": False,
        "notes": [
            ["The film sits where it aired.", "Knockin' on Heaven's Door is "
             "set between sessions 22 and 23, but it reached cinemas in 2001, "
             "after the series — it closes the list rather than interrupting "
             "it."],
            ["Weights.", "Sessions weigh 0.4 hours each and the film weighs "
             "its %d-minute runtime, so the strip stays honest about how "
             "long each mark takes." % film["runtime"]],
            ["What is out.", "The \"Mish-Mash Blues\" recap special — a "
             "clip-show summary that aired mid-run and adds nothing new — "
             "and the 2021 Netflix live-action series, which is a different "
             "production."],
            "Session numbers and titles machine-read from Wikipedia's List "
            "of Cowboy Bebop episodes; the film's year and runtime from its "
            "own article.",
        ],
        "sections": sections,
    }

    with OUT.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json — %d rows, %.2f hours" % (SLUG, len(ids), hours))
    for s in sections:
        print("   %-28s %2d  %s" % (s["title"], len(s["items"]),
                                    s.get("sub", "")[:44]))


if __name__ == "__main__":
    main()
