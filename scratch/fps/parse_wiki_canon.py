#!/usr/bin/env python3
"""Parse Wikipedia's "Video games listed among the best first-person shooters".

    python scratch/fps/parse_wiki_canon.py

That article is an aggregator: one row per game, and the last column carries a
footnote per published best-of-FPS list that named it. Counting the distinct
ref names in a row gives a "how many published canons agree" score, which is
what tools/make_fps_canon.py uses to defend its cut.

Writes scratch/fps/wiki_canon.json — {year, title, refs:[...], n} per game —
and prints the roll-up.
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
WIKI = HERE / "Video-games-listed-among-the-best-first-person-shooters.wiki"

REF = re.compile(r'<ref name=([A-Za-z0-9_]+)\s*/?>')
LINK = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")


def clean_title(cell):
    cell = cell.strip().strip("|")
    m = LINK.search(cell)
    if m:
        t = m.group(2) or m.group(1)
    else:
        t = cell
    return t.replace("''", "").strip()


def main():
    # the cache is written on Windows and read back after git has normalized
    # it to LF, so the newlines are settled here rather than trusted
    text = WIKI.read_text(encoding="utf-8").replace("\r\n", "\n")
    start = text.index('{|class="wikitable sortable sticky-header"')
    end = text.index("\n|}", start)
    table = text[start:end]

    games, year = [], None
    for row in table.split("\n|-"):
        ym = re.search(r'!scope="row"[^|]*\|\[\[(\d{4}) in video games', row)
        if ym:
            year = int(ym.group(1))
        lines = [l for l in row.split("\n") if l.startswith("|")]
        # drop the year header line's trailing content; the first data cell is
        # the game (after any rowspan year header, which starts with !)
        cells = [l for l in lines if not l.startswith("|+")]
        if not cells:
            continue
        title = clean_title(cells[0])
        if not title or title.startswith("class=") or "scope=" in title:
            continue
        refs = sorted(set(REF.findall(row)))
        if not refs:
            continue
        games.append({"year": year, "title": title, "refs": refs,
                      "n": len(refs)})

    allrefs = {}
    for g in games:
        for r in g["refs"]:
            allrefs[r] = allrefs.get(r, 0) + 1

    # A silent parse failure here would quietly change which games clear
    # tools/make_fps_canon.py's gate, so the shape is asserted rather than
    # eyeballed. If the article genuinely grows, move these and say so.
    assert len(games) >= 150, "only parsed %d games — the table moved" % len(games)
    assert len(allrefs) == 20, \
        "expected 20 source lists, found %d: %s" % (len(allrefs), sorted(allrefs))
    assert all(g["year"] for g in games), "a row lost its year"

    out = HERE / "wiki_canon.json"
    out.write_text(json.dumps(games, indent=1, ensure_ascii=False) + "\n",
                   encoding="utf-8", newline="\n")
    print("%d games, %d source lists" % (len(games), len(allrefs)))
    print("sources: %s" % ", ".join("%s(%d)" % kv
                                    for kv in sorted(allrefs.items(),
                                                     key=lambda kv: -kv[1])))
    for g in sorted(games, key=lambda g: (-g["n"], g["year"])):
        if g["n"] >= int(sys.argv[1]) if len(sys.argv) > 1 else g["n"] >= 3:
            print("  %2d  %s  %s" % (g["n"], g["year"], g["title"]))


if __name__ == "__main__":
    main()
