#!/usr/bin/env python3
"""Cache the manga chapters each Bleach episode adapts, from the Bleach wiki.

    python scratch/bleach/fetch_chapters.py

bleach.fandom.com's episode infobox carries `|chapters=` (the manga chapters
the episode adapts) and `|arc=`. An episode that adapts no chapter is
anime-original, and that is the independent, chapter-anchored check the
published filler list gets measured against.

There is no Semantic MediaWiki here the way Narutopedia has one, so the
episodes are enumerated from Category:Episodes and keyed by the
`|episodenumber=` in each page's own infobox. Writes scratch/bleach/
chapters.json and stops if the cache is already there.
"""
import json
import pathlib
import re
import time
import urllib.parse
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "chapters.json"
API = "https://bleach.fandom.com/api.php?"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")


def api(params):
    for attempt in range(5):
        try:
            req = urllib.request.Request(API + urllib.parse.urlencode(params),
                                         headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception:
            if attempt == 4:
                raise
            time.sleep(5 * (attempt + 1))


def category(name):
    """Every article title in a category, following continuations."""
    out, cont = [], {}
    while True:
        d = api(dict({"action": "query", "format": "json",
                      "formatversion": "2", "list": "categorymembers",
                      "cmtitle": name, "cmlimit": "500", "cmnamespace": "0"},
                     **cont))
        out += [p["title"] for p in d["query"]["categorymembers"]]
        cont = d.get("continue")
        if not cont:
            return out
        time.sleep(0.3)


def wikitexts(titles):
    """{page title: wikitext}, 50 pages a request."""
    out = {}
    titles = list(titles)
    for i in range(0, len(titles), 50):
        batch = titles[i:i + 50]
        d = api({"action": "query", "format": "json", "formatversion": "2",
                 "prop": "revisions", "rvprop": "content", "rvslots": "main",
                 "titles": "|".join(batch)})
        for page in d.get("query", {}).get("pages", []):
            revs = page.get("revisions") or []
            if revs:
                out[page["title"]] = revs[0]["slots"]["main"]["content"]
        time.sleep(0.3)
    return out


# `[ \t]` and not `\s`: with `\s*` around the value an EMPTY field ate its own
# newline and captured the NEXT line, so `|chapters =` (blank, meaning
# anime-original) read back as the arc name and the episode looked adapted.
FIELD = r"^[ \t]*\|[ \t]*%s[ \t]*=[ \t]*(.*?)[ \t]*$"
NUM = re.compile(FIELD % "episodenumber", re.M | re.I)
CHAPTERS = re.compile(FIELD % "chapters", re.M | re.I)
ARC = re.compile(FIELD % "arc", re.M | re.I)


def main():
    if OUT.exists():
        print("%s already cached" % OUT)
        return
    titles = category("Category:Episodes")
    print("%d pages in Category:Episodes" % len(titles))
    pages = wikitexts(titles)
    print("%d wikitexts" % len(pages))

    rows, skipped = {}, []
    for title, text in sorted(pages.items()):
        m = NUM.search(text)
        if not m or not re.fullmatch(r"\d+", m.group(1).strip()):
            skipped.append(title)
            continue
        n = int(m.group(1))
        ch = CHAPTERS.search(text)
        arc = ARC.search(text)
        row = {"title": title,
               "chapters": (ch.group(1).strip() if ch else ""),
               "arc": (arc.group(1).strip() if arc else "")}
        assert n not in rows, \
            "episode %d claimed by both %r and %r" % (n, rows[n]["title"], title)
        rows[n] = row

    nums = sorted(rows)
    print("%d numbered episodes, %d–%d" % (len(rows), nums[0], nums[-1]))
    print("%d pages skipped (no numeric episodenumber)" % len(skipped))
    print("%d with chapters" % sum(1 for r in rows.values() if r["chapters"]))
    gaps = [n for n in range(nums[0], nums[-1] + 1) if n not in rows]
    if gaps:
        print("gaps: %s" % gaps[:20])

    with OUT.open("w", encoding="utf-8", newline="\n") as f:
        json.dump({str(k): v for k, v in rows.items()}, f, indent=1,
                  ensure_ascii=False, sort_keys=True)
        f.write("\n")
    print("wrote %s" % OUT)


if __name__ == "__main__":
    main()
