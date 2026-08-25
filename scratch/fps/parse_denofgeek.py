#!/usr/bin/env python3
"""Parse Den of Geek's ranked "30 Best First-Person Shooter Games Ever Made".

    python scratch/fps/parse_denofgeek.py

The article numbers its picks in <h2>/<h3> headings, 30 down to 1, so the rank
comes out of the page rather than out of anyone's memory. Reads the cached
scratch/fps/denofgeek-30-best-fps.html (fetched with a browser User-Agent;
WebFetch 403s on this host) and writes scratch/fps/denofgeek30.json as
{title: rank}.

This is the second published canon tools/make_fps_canon.py checks itself
against. It is not independent of the other one — Wikipedia's aggregator
counts this same article as one of its twenty sources — which is exactly why
it is read directly here instead of trusted second-hand.
"""
import html
import json
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
PAGE = HERE / "denofgeek-30-best-fps.html"

RANKED = re.compile(r"^(\d{1,2})\.\s+(.*\S)\s*$")


def main():
    text = PAGE.read_text(encoding="utf-8", errors="replace").replace("\r\n",
                                                                      "\n")
    out = {}
    for raw in re.findall(r"<h[23][^>]*>(.*?)</h[23]>", text, re.S):
        line = html.unescape(re.sub(r"<[^>]+>", "", raw)).strip()
        m = RANKED.match(line)
        if not m:
            continue
        rank, title = int(m.group(1)), m.group(2)
        if not 1 <= rank <= 30 or rank in out.values():
            continue
        out[title] = rank

    assert len(out) == 30, "expected 30 ranked picks, parsed %d" % len(out)
    assert sorted(out.values()) == list(range(1, 31)), \
        "ranks are not 1..30: %s" % sorted(out.values())

    (HERE / "denofgeek30.json").write_text(
        json.dumps(out, indent=1, ensure_ascii=False) + "\n",
        encoding="utf-8", newline="\n")
    for title, rank in sorted(out.items(), key=lambda kv: kv[1]):
        print("%2d  %s" % (rank, title))


if __name__ == "__main__":
    main()
