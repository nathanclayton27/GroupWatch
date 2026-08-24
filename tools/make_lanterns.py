#!/usr/bin/env python3
"""Generate properties/lanterns.json — Lanterns (2026).

    python3 tools/make_lanterns.py

The DC Green Lantern series: Hal Jordan and John Stewart investigating a murder
in the American heartland. Eight episodes, weekly on Sundays from 16 August to
4 October 2026.

It is airing right now, which makes it the one property here with a schedule
that matters week to week — one window per episode, so the pace line tells you
whether you are current rather than whether you are on track for a distant date.

Only the first two titles have been announced. The rest are numbered and will
get their titles as they air; bump them here and rerun.
"""
import json
import pathlib
from datetime import date, timedelta

SLUG = "lanterns"

FIRST_AIR = date(2026, 8, 16)      # Sunday
EPISODES = [
    "Pilot",
    "Trust Fall",
    None, None, None, None, None, None,
]


def iso(d):
    return d.isoformat()


def main():
    items, windows = [], []
    for i, title in enumerate(EPISODES):
        n = i + 1
        airs = FIRST_AIR + timedelta(weeks=i)
        items.append({
            "id": "lanterns-%d" % n,
            "t": title or "Episode %d" % n,
            "n": str(n),
            # %-d is not portable, so the day is formatted by hand
            "note": "airs %d %s" % (airs.day, airs.strftime("%B")),
        })
        # a week to watch each one, so "behind" means behind the broadcast
        windows.append({
            "start": iso(airs),
            "end": iso(airs + timedelta(days=6)),
            "through": n,
            "label": "Episode %d" % n,
        })

    sections = [{
        "id": "s1",
        "title": "Season 1",
        "sub": "8 episodes · weekly from %d %s" % (FIRST_AIR.day,
                                                   FIRST_AIR.strftime("%B %Y")),
        "items": items,
    }]

    ids = [x["id"] for s in sections for x in s["items"]]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate item ids")
    if len(ids) != 8:
        raise SystemExit("expected 8 episodes, built %d" % len(ids))
    thr = [w["through"] for w in windows]
    if thr != sorted(thr):
        raise SystemExit("window targets are not monotonic")

    prop = {
        "slug": SLUG,
        "title": "Lanterns",
        "subtitle": "Hal Jordan and John Stewart",
        "kind": "tv",
        "popularity": 29,
        "year": "2026",
        "blurb": "8 episodes, weekly, still airing.",
        "unit": {"one": "episode", "many": "episodes"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": "#2E7A45",
        "accentDark": "#5FC47E",
        "tiers": False,
        "schedule": {"kind": "windows", "windows": windows},
        "notes": [
            ["Airing now.", "One window per episode, so the pace line tells you "
                            "whether you are caught up with the broadcast rather than "
                            "on track for some distant finish. The last episode lands "
                            "on 4 October 2026."],
            ["Titles.", "Only the first two have been announced. The rest are "
                        "numbered until HBO says otherwise."],
        ],
        "sections": sections,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json" % SLUG)
    for it, w in zip(items, windows):
        print("   %-2s %-14s %s .. %s" % (it["n"], it["t"], w["start"], w["end"]))


if __name__ == "__main__":
    main()
