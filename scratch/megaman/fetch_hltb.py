#!/usr/bin/env python3
"""Collect HowLongToBeat main-story hours for the 94 compendium entries.

Every query goes through tools/gwlib/hltb.py's verify-by-name gate: a record
only counts when its name normalizes to what was asked for AND its release
year sits inside the window Backloggd gives. Anything that fails ships
UNWEIGHTED with the reason written down — a Mega Man list is full of
feature-phone toys and Japan-only oddities that HowLongToBeat has never
heard of, and inventing a number for one of them would go straight into a
reader's pace.

The howlongtobeatpy package is dead — its bundled endpoint extractor points
at /api/search, which 404s, and it returns None rather than raising. The
live protocol (a per-session token from /api/search/site/init, handed back
on /api/search/site as headers PLUS a rotating key/value pair spliced into
the body) was found by scratch/megaman/hltb_probe.py reading the site's own
Next.js chunks, and now lives in tools/gwlib/hltb.py, which this uses. The
punctuation-splitting of search terms lives there too: "Mega Man: Maverick
Hunter X" split on whitespace asks for a term "Man:" and finds nothing,
which cost seven rows their weight before it was found.

Raw search results are cached in scratch/megaman/hltb_raw.json so a re-run
costs nothing and the misses stay reviewable; the verdicts are written to
tools/data/megaman.json, which is what the generator reads. The roster it
runs over is tools/data/megaman-compendium.json.

    python3 scratch/megaman/fetch_hltb.py
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
from gwlib import hltb as H  # noqa: E402

ROSTER = ROOT / "tools" / "data" / "megaman-compendium.json"
OUT = ROOT / "tools" / "data" / "megaman.json"

# Extra names to try when the Backloggd title is not what HowLongToBeat files
# the game under. Each alias must be a genuine alternate title of the SAME
# game — the gate still refuses any record whose name does not match, so a
# wrong alias produces an unweighted row, never a wrong number.
ALIASES = {
    "78132": ["Mega Man (PC)"],                       # the 1990 DOS game
    "1738": ["Mega Man (Game Gear)"],                 # the 1995 Game Gear game
    # HowLongToBeat disambiguates the Game Boy numbering from the NES one
    "1734": ["Mega Man II (Game Boy)"],
    "1735": ["Mega Man III (Game Boy)"],
    "1736": ["Mega Man IV (Game Boy)"],
    "1737": ["Mega Man V (Game Boy)"],
    # Dr. Right and Dr. Light are the same character; HLTB transliterates the
    # 1993 Famicom board game the other way round
    "1729": ["Wily and Light no Rock Board: That's Paradise"],
    "88384": ["Mega Man 3: The Robots are Revolting",
              "Mega Man 3 (PC)"],
    "1727": ["Mega Man: The Wily Wars", "Rockman Mega World"],
    "1758": ["Mega Man Battle Network 3: Blue",
             "Mega Man Battle Network 3 Blue Version",
             "Mega Man Battle Network 3: Blue Version"],
    "1757": ["Mega Man Battle Network 3: White",
             "Mega Man Battle Network 3 White Version",
             "Mega Man Battle Network 3: White Version"],
    "1761": ["Mega Man Battle Network 5: Team Protoman",
             "Mega Man Battle Network 5: Team ProtoMan"],
    "1762": ["Mega Man Battle Network 5: Team Colonel"],
    "1783": ["Mega Man Star Force: Dragon", "Mega Man Star Force Dragon"],
    "1782": ["Mega Man Star Force: Leo", "Mega Man Star Force Leo"],
    "1781": ["Mega Man Star Force: Pegasus", "Mega Man Star Force Pegasus"],
    "1786": ["Mega Man Star Force 3: Black Ace"],
    "1787": ["Mega Man Star Force 3: Red Joker"],
    "1774": ["Mega Man Battle Network: Operate Shooting Star",
             "Rockman EXE: Operate Shooting Star",
             "Rockman.EXE Operate Shooting Star"],
    "1739": ["Rockman & Forte: Mirai Kara no Chousensha",
             "Mega Man & Bass: Challenger from the Future"],
    "252996": ["Mega Man X DiVE Offline", "Mega Man X DiVE"],
    "1753": ["The Misadventures of Tron Bonne"],
    "1731": ["Mega Man Battle & Chase"],
    "1724": ["Mega Man: The Power Battle", "Mega Man: The Power Battles"],
    "1725": ["Mega Man 2: The Power Fighters"],
    "45184": ["Street Fighter X Mega Man"],
    "1732": ["Super Adventure Rockman"],
    "1766": ["Mega Man Network Transmission"],
    "1751": ["Mega Man X: Command Mission"],
    "24275": ["Mega Man: Maverick Hunter X"],
    "12937": ["Mega Man: Powered Up", "Mega Man Powered Up"],
}


def save(obj, path):
    path.write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n",
                    encoding="utf-8", newline="\n")


def main():
    games = json.loads(ROSTER.read_text(encoding="utf-8"))["games"]
    # gwlib.hltb.Session does the token dance, the punctuation split, the
    # retries with a token refresh, and the on-disk cache. It RAISES when the
    # endpoint is broken rather than returning nothing, which is the whole
    # point: a dead lookup must not look like "no such game".
    sess = H.Session(cache_dir=str(HERE), pause=1.6)
    out = {}
    for g in games:
        tries = [g["t"]] + [a for a in ALIASES.get(g["gid"], []) if a != g["t"]]
        hours, why, hit = None, None, None
        for q in tries:
            results = sess.search(q)
            hours, rec, reason = H.story_hours(q, g["year"], 2, results)
            if hours:
                hit, why = q, reason
                break
            if why is None:
                why = reason
        if hours:
            out[g["gid"]] = {"t": g["t"], "query": hit, "main_h": hours,
                             "year": g["year"]}
            print("  %-52s %6.2f h  (%s)" % (g["t"][:52], hours, hit))
        else:
            out[g["gid"]] = {"t": g["t"], "main_h": None, "why": why,
                             "year": g["year"]}
            print("  %-52s   ----   %s" % (g["t"][:52], str(why)[:78]))
    assert len(out) == len(games), "lost an entry"
    save(out, OUT)
    weighted = sum(1 for v in out.values() if v["main_h"])
    print("\n%d/%d weighted, %d unweighted (%d live searches this run)"
          % (weighted, len(out), len(out) - weighted, sess.calls))
    print("wrote %s" % OUT)


if __name__ == "__main__":
    main()
