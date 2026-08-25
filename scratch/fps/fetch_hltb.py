#!/usr/bin/env python3
"""Collect HowLongToBeat main-story hours for the FPS canon.

    python scratch/fps/fetch_hltb.py

Every figure goes through tools/gwlib/hltb.py's verify-by-name gate: a result
only counts when its name normalizes to the title asked for and its release
year sits within two years of the one asked for. Anything the gate refuses is
written down with the reason instead of a number — tools/make_fps_canon.py
ships those rows unweighted and says why on the row.

Raw rows land in scratch/fps/hltb_raw.json (the Session cache), the verified
per-key result in scratch/fps/hltb.json. Re-running costs nothing; delete the
raw cache to re-fetch.

Two titles need help and get it here rather than in the generator:

  * "Doom" is two games in this canon, 1993 and 2016, and HowLongToBeat calls
    both of them "Doom". The gate's nearest-year sort separates them, which is
    the same fix the two GoldenEye 007 records needed.
  * "F.E.A.R." cannot be searched for under its own name. Search terms are
    matched one at a time, so the punctuation split turns it into F, E, A, R
    — four single letters — and the site answers with Grand Theft Auto V.
    The row therefore searches for "FEAR" and still VERIFIES against
    "F.E.A.R.": the gate is untouched, only the query changes. Rows with a
    separate search string carry it as the fourth field below.

Multiplayer-only entries (Counter-Strike, Team Fortress 2) verify by name and
come back with a figure that is not a story length — nothing in them ends.
Judging that is the generator's job, not this script's; it records what the
site said and tools/make_fps_canon.py decides what is a story.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from gwlib import hltb  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent

# key, name to VERIFY against, release year, (optional) string to SEARCH with
QUERIES = [
    ("wolf3d", "Wolfenstein 3D", 1992),
    ("doom", "Doom", 1993),
    ("duke3d", "Duke Nukem 3D", 1996),
    ("quake", "Quake", 1996),
    ("goldeneye", "GoldenEye 007", 1997),
    ("halflife", "Half-Life", 1998),
    ("quake3", "Quake III Arena", 1999),
    ("ut", "Unreal Tournament", 1999),
    ("cs", "Counter-Strike", 2000),
    ("perfectdark", "Perfect Dark", 2000),
    ("halo", "Halo: Combat Evolved", 2001),
    ("bf1942", "Battlefield 1942", 2002),
    ("cod", "Call of Duty", 2003),
    ("halflife2", "Half-Life 2", 2004),
    ("halo2", "Halo 2", 2004),
    ("fear", "F.E.A.R.", 2005, "FEAR"),
    ("bioshock", "BioShock", 2007),
    ("cod4", "Call of Duty 4: Modern Warfare", 2007),
    ("tf2", "Team Fortress 2", 2007),
    ("l4d", "Left 4 Dead", 2008),
    ("metro2033", "Metro 2033", 2010),
    ("borderlands2", "Borderlands 2", 2012),
    ("wolftno", "Wolfenstein: The New Order", 2014),
    ("doom2016", "Doom", 2016),
    ("titanfall2", "Titanfall 2", 2016),
    ("alyx", "Half-Life: Alyx", 2020),
    ("doometernal", "Doom Eternal", 2020),
]


def main():
    session = hltb.Session(cache_dir=str(HERE))
    out = {}
    for row in QUERIES:
        key, query, year = row[0], row[1], row[2]
        search = row[3] if len(row) > 3 else query
        rows = session.search(search)
        hours, rec, why = hltb.story_hours(query, year, results=rows)
        out[key] = {
            "query": query, "search": search, "want_year": year,
            "name": getattr(rec, "game_name", None),
            "year": getattr(rec, "release_world", None),
            "main_h": hours, "why": why,
            "candidates": sorted({(r.game_name, r.release_world)
                                  for r in rows})[:6],
        }
        print("%-14s %-32s %-8s %s"
              % (key, out[key]["name"] or "-", hours, why[:60]))

    (HERE / "hltb.json").write_text(
        json.dumps(out, indent=1, ensure_ascii=False) + "\n",
        encoding="utf-8", newline="\n")
    got = sum(1 for v in out.values() if v["main_h"])
    print("\n%d/%d verified, %d live calls"
          % (got, len(QUERIES), session.calls))


if __name__ == "__main__":
    main()
