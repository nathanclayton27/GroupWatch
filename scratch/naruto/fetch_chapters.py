#!/usr/bin/env python3
"""Cache the manga chapters each episode adapts, from Narutopedia.

    python scratch/naruto/fetch_chapters.py

Narutopedia's episode infoboxes carry `|chapters=` (the manga chapters an
episode adapts) and `|arc=`. An episode that adapts no chapters is
anime-original; that is the independent, chapter-anchored check the filler
list gets measured against. Writes scratch/naruto/chapters.json and stops if
the cache is already there.
"""
import json
import pathlib
import re
import time
import urllib.parse
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "chapters.json"
API = "https://naruto.fandom.com/api.php?"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

CONCEPTS = {"naruto": "Concept:Episodes of Naruto Original",
            "shippuden": "Concept:Episodes of Naruto Shippuden"}
EXPECTED = {"naruto": 220, "shippuden": 500}


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


def titles_for(concept):
    """{episode number: page title} for a Narutopedia episode concept."""
    out, offset = {}, 0
    while True:
        d = api({"action": "ask", "format": "json",
                 "query": "[[%s]]|?Episode number|limit=200|offset=%d"
                          % (concept, offset)})
        results = d.get("query", {}).get("results") or {}
        if not results:
            break
        for title, row in results.items():
            nums = row["printouts"].get("Episode number") or []
            if nums:
                out[int(nums[0])] = row["fulltext"]
        nxt = d.get("query-continue-offset")
        if not nxt or nxt <= offset:
            break
        offset = nxt
        time.sleep(0.4)
    return out


def wikitexts(titles):
    """{page title: wikitext} for up to any number of pages, 50 per request."""
    out = {}
    titles = list(titles)
    for i in range(0, len(titles), 50):
        batch = titles[i:i + 50]
        d = api({"action": "query", "format": "json", "formatversion": "2",
                 "prop": "revisions", "rvprop": "content", "rvslots": "main",
                 "titles": "|".join(batch)})
        norm = {n["from"]: n["to"]
                for n in d.get("query", {}).get("normalized", [])}
        for page in d.get("query", {}).get("pages", []):
            revs = page.get("revisions") or []
            if revs:
                out[page["title"]] = revs[0]["slots"]["main"]["content"]
        for t in batch:
            assert norm.get(t, t) in out, "no wikitext for %r" % t
        time.sleep(0.4)
    return out


CHAPTERS = re.compile(r"^\s*\|\s*chapters\s*=\s*(.*?)\s*$", re.M | re.I)
ARC = re.compile(r"^\s*\|\s*arc\s*=\s*(.*?)\s*$", re.M | re.I)


def main():
    if OUT.exists():
        print("%s already cached" % OUT)
        return
    data = {}
    for series, concept in CONCEPTS.items():
        titles = titles_for(concept)
        want = EXPECTED[series]
        missing = [n for n in range(1, want + 1) if n not in titles]
        assert not missing, "%s: no page for episodes %s" % (series, missing[:8])
        pages = wikitexts(sorted(set(titles[n] for n in range(1, want + 1))))
        rows = {}
        for n in range(1, want + 1):
            text = pages[titles[n]]
            ch = CHAPTERS.search(text)
            arc = ARC.search(text)
            rows[n] = {"title": titles[n],
                       "chapters": (ch.group(1) if ch else ""),
                       "arc": (arc.group(1) if arc else "")}
        data[series] = rows
        print("%-10s %d episodes, %d with chapters"
              % (series, len(rows),
                 sum(1 for r in rows.values() if r["chapters"])))
    with OUT.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=1, ensure_ascii=False, sort_keys=True)
        f.write("\n")
    print("wrote %s" % OUT)


if __name__ == "__main__":
    main()
