#!/usr/bin/env python3
"""Harvest the Attack on Titan episode tables into scratch/aot/attack-on-titan.json.

    python scratch/aot/harvest.py

Wikipedia's "List of Attack on Titan episodes" is a stub that transcludes four
season articles, so the enumerated rows live on those four pages. Each page is
cached as .wiki next to this script; delete a cache file to refetch.

The trap this script exists to defuse: season 4's article prints parts 3 and 4
TWICE — once as the two television specials they first aired as ("Special
Version", EpisodeNumber "SP 1"/"SP 2") and once as the seven numbered episodes
they were later redistributed as ("Episode Version", 88-94). Count the special
rows and you get the 89 that every summary of this show repeats; count the
enumerated episodes and you get 94. This keeps the episode rows and records the
special rows separately, so make_attack_on_titan.py can assert both numbers.

Also separated out, because they are not episodes of the run: season 1's
"Since That Day" recap special (13.5), and the three OADs the list page
enumerates in its own table.
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "tools"))

from gwlib import wiki  # noqa: E402

LIST_PAGE = "List of Attack on Titan episodes"
SEASON_PAGES = ["Attack on Titan season %d" % n for n in (1, 2, 3, 4)]

# {{Episode table/part|part=2|subtitle=Episode Version|c=#111}}
PART = re.compile(r"\{\{Episode table/part\s*\|\s*part\s*=\s*(\d+)"
                  r"((?:\s*\|[^|}\n]*)*)\}\}")
HEADING = re.compile(r"^=+\s*(.*?)\s*=+\s*$", re.M)


def field(block, name):
    m = re.search(r"\|\s*%s\s*=\s*(.*?)(?=\n\s*\||\Z)" % name, block, re.S)
    return m.group(1).strip() if m else ""


def contexts(text):
    """(position, heading, part, subtitle) markers in page order."""
    out = [(0, None, None, None)]
    for m in HEADING.finditer(text):
        out.append((m.start(), m.group(1).strip("' "), None, None))
    for m in PART.finditer(text):
        sub = re.search(r"\|\s*subtitle\s*=\s*([^|}\n]*)", m.group(2) or "")
        out.append((m.start(), None, int(m.group(1)),
                    sub.group(1).strip() if sub else None))
    out.sort(key=lambda x: x[0])
    # carry the last heading forward across part markers
    heading, rolled = None, []
    for pos, h, part, sub in out:
        if h is not None:
            heading = h
        rolled.append((pos, heading, part, sub))
    return rolled


def rows(page):
    """Every {{Episode list}} row on a page, with its table context."""
    text = (HERE / (re.sub(r"[^A-Za-z0-9]+", "-", page) + ".wiki"))
    text = text.read_text(encoding="utf-8") if text.exists() else None
    if text is None:
        text = wiki.wikitext(page, cache_dir=str(HERE))
    marks = contexts(text)
    out = []
    for m in re.finditer(r"\{\{(?:#invoke:)?Episode list"
                         r"(?:\s*\|\s*sublist\s*\|[^|\n]*|/sublist[^|}\n]*)?"
                         r"\s*(\|.*?)\n\s*\}\}", text, flags=re.S | re.I):
        block = "\n" + m.group(1)
        ctx = [c for c in marks if c[0] <= m.start()][-1]
        air = field(block, "OriginalAirDate")
        d = re.search(r"\{\{Start date\|(\d{4})\|(\d{1,2})\|(\d{1,2})", air)
        out.append({
            "overall": field(block, "EpisodeNumber"),
            "in_season": field(block, "EpisodeNumber2"),
            "t": wiki.clean(field(block, "Title")).strip('"'),
            "air": "%s-%02d-%02d" % (d.group(1), int(d.group(2)),
                                     int(d.group(3))) if d else None,
            "heading": ctx[1],
            "part": ctx[2],
            "table": ctx[3],
        })
    return out


def main():
    wiki.wikitext(LIST_PAGE, cache_dir=str(HERE))  # the source of record
    seasons, specials, recaps = [], [], []

    for n, page in enumerate(SEASON_PAGES, 1):
        eps, parts = [], {}
        for r in rows(page):
            if r["heading"] and "recap" in r["heading"].lower():
                recaps.append(dict(r, season=n))
                continue
            if not re.match(r"^\d+$", r["overall"]):
                # "SP 1"/"SP 2": the television-special printing of episodes
                # that also appear, numbered, in the Episode Version table
                specials.append(dict(r, season=n))
                continue
            if r["table"] and "special" in r["table"].lower():
                specials.append(dict(r, season=n))
                continue
            part = r["part"] or 1
            parts.setdefault(part, []).append(len(eps))
            eps.append({"overall": int(r["overall"]),
                        "in_season": int(r["in_season"]),
                        "t": r["t"], "air": r["air"], "part": part})
        seasons.append({"season": n, "page": page, "episodes": eps,
                        "parts": sorted(parts)})

    # The three OADs the list page enumerates in its own table. Its prose
    # counts eight in total; the other five are the No Regrets and Lost Girls
    # sets, which live on their own articles and are not enumerated here.
    oads = [dict(r) for r in rows(LIST_PAGE)]
    for i, r in enumerate(oads, 1):
        r["n"] = i

    data = {
        "source": "https://en.wikipedia.org/wiki/" + LIST_PAGE.replace(" ", "_"),
        "seasons": seasons,
        "oads": oads,
        "specials": specials,
        "recaps": recaps,
    }
    out = HERE / "attack-on-titan.json"
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    total = sum(len(s["episodes"]) for s in data["seasons"])
    print("wrote %s" % out.name)
    for s in data["seasons"]:
        eps = s["episodes"]
        print("  season %d: %2d episodes (%d-%d), parts %s"
              % (s["season"], len(eps), eps[0]["overall"], eps[-1]["overall"],
                 s["parts"]))
    print("  %d episodes; %d special printings, %d recaps, %d OADs"
          % (total, len(data["specials"]), len(data["recaps"]),
             len(data["oads"])))


if __name__ == "__main__":
    main()
