#!/usr/bin/env python3
"""Build scratch/naruto/naruto.json from the cached Wikipedia season articles
and the cached animefillerlist.com classification tables.

    python scratch/naruto/parse.py            # uses the cache, no network
    python scratch/naruto/parse.py --fetch    # refresh the cache first

The enumerated episode tables are the source of truth for the count, never the
infoboxes: this asserts both agree per season and fails loudly if they ever
diverge.  Wikipedia's `{{Episode table/part|subtitle=...}}` markers give the
arc each episode belongs to; animefillerlist gives the canon/filler class.
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
WIKI = HERE / "wiki"
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "tools"))

SEASONS = ([("naruto", n, "Naruto season %d" % n) for n in range(1, 6)]
           + [("shippuden", n, "Naruto: Shippuden season %d" % n)
              for n in range(1, 23)])

# the totals the two list articles' own tables come to; the infoboxes agree
EXPECTED = {"naruto": 220, "shippuden": 500}

AFL = {"naruto": "naruto", "shippuden": "naruto-shippuden"}


def cache_name(page):
    return re.sub(r"[^A-Za-z0-9]+", "-", page) + ".wiki"


def fetch():
    from gwlib import wiki
    for page in ["List of Naruto episodes", "List of Naruto: Shippuden episodes"]:
        wiki.wikitext(page, cache_dir=str(WIKI), sleep=0.6)
    for _, _, page in SEASONS:
        wiki.wikitext(page, cache_dir=str(WIKI), sleep=0.6)
    import urllib.request
    ua = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
    for slug in AFL.values():
        out = HERE / ("afl-%s.html" % slug)
        if out.exists():
            continue
        req = urllib.request.Request(
            "https://www.animefillerlist.com/shows/" + slug,
            headers={"User-Agent": ua, "Accept": "text/html"})
        with urllib.request.urlopen(req, timeout=60) as r:
            out.write_bytes(r.read())


# --- Wikipedia: the enumerated tables -------------------------------------

PART = re.compile(r"\{\{Episode table/part\s*\|\s*subtitle\s*=\s*([^|}]+)")
# Part I's season pages use {{Episode list/sublist|<page>}}, Shippuden's use
# {{#invoke:Episode list|sublist}} with the page as a positional `1 =`. Match
# the template opening, then read the EpisodeNumber that follows it.
EPSTART = re.compile(r"\{\{(?:#invoke:)?Episode list\s*[|/]")
EPNUM = re.compile(r"\|\s*EpisodeNumber\s*=\s*(\d+)")
INFOBOX_N = re.compile(r"\|\s*num_episodes\s*=\s*(\d+)")


def season_rows(page):
    """[(arc_subtitle, episode_number)] in table order, plus the infobox count."""
    text = (WIKI / cache_name(page)).read_text(encoding="utf-8")
    box = INFOBOX_N.search(text)
    assert box, "no num_episodes in %s" % page
    body = text[text.index("== Episodes =="):]

    events = [(m.start(), "part", re.sub(r"\s+", " ", m.group(1)).strip())
              for m in PART.finditer(body)]
    for m in EPSTART.finditer(body):
        n = EPNUM.search(body, m.end(), m.end() + 400)
        assert n, "%s: Episode list template with no EpisodeNumber at %d" % (
            page, m.start())
        events.append((m.start(), "ep", int(n.group(1))))
    events.sort()

    rows, arc = [], None
    for _, kind, value in events:
        if kind == "part":
            arc = value
        else:
            assert arc, "%s: episode %s before any part header" % (page, value)
            rows.append((arc, value))
    assert rows, "no episodes parsed from %s" % page
    return rows, int(box.group(1))


# --- animefillerlist: the published filler classification ------------------

AFL_ROW = re.compile(r'<tr class="[^"]*" id="eps-(\d+)">.*?'
                     r'<td class="Type"><span>([^<]+)</span>', re.S)

CLASS = {"Manga Canon": "canon", "Filler": "filler",
         "Mixed Canon/Filler": "mixed", "Anime Canon": "anime-canon"}


def filler_map(series):
    html = (HERE / ("afl-%s.html" % AFL[series])).read_text(
        encoding="utf-8", errors="replace")
    out = {}
    for num, kind in AFL_ROW.findall(html):
        assert kind in CLASS, "unknown animefillerlist type %r" % kind
        out[int(num)] = CLASS[kind]
    want = EXPECTED[series]
    assert sorted(out) == list(range(1, want + 1)), \
        "%s: animefillerlist covers %d rows, expected 1..%d" % (
            series, len(out), want)
    return out


def main():
    if "--fetch" in sys.argv:
        fetch()

    data = {}
    for series in ("naruto", "shippuden"):
        seasons, seen = [], 0
        for s, n, page in SEASONS:
            if s != series:
                continue
            rows, box_n = season_rows(page)
            nums = [e for _, e in rows]
            assert nums == list(range(nums[0], nums[-1] + 1)), \
                "%s: episode numbers are not contiguous" % page
            assert nums[0] == seen + 1, \
                "%s: starts at %d, previous season ended at %d" % (
                    page, nums[0], seen)
            assert len(nums) == box_n, \
                "%s: table has %d episodes, infobox says %d (the table wins, " \
                "but a mismatch means the article changed)" % (
                    page, len(nums), box_n)
            seen = nums[-1]
            # collapse the table's part markers into contiguous arc runs
            arcs, prev = [], None
            for arc, e in rows:
                if prev is not None and prev["arc"] == arc and prev["last"] == e - 1:
                    prev["last"] = e
                else:
                    prev = {"arc": arc, "first": e, "last": e}
                    arcs.append(prev)
            seasons.append({"season": n, "page": page,
                            "first": nums[0], "last": nums[-1],
                            "episodes": len(nums), "arcs": arcs})
        assert seen == EXPECTED[series], \
            "%s: tables come to %d episodes, expected %d" % (
                series, seen, EXPECTED[series])
        data[series] = {"total": seen, "seasons": seasons,
                        "filler": filler_map(series)}

    out = HERE / "naruto.json"
    with out.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=1, ensure_ascii=False, sort_keys=True)
        f.write("\n")
    print("wrote %s" % out)
    for series in ("naruto", "shippuden"):
        d = data[series]
        runs = sum(len(s["arcs"]) for s in d["seasons"])
        print("  %-10s %3d episodes, %2d seasons, %d arc runs"
              % (series, d["total"], len(d["seasons"]), runs))


if __name__ == "__main__":
    main()
