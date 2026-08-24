#!/usr/bin/env python3
"""Find HowLongToBeat's current search endpoint and token scheme.

howlongtobeatpy's bundled extractor points at /api/search, which 404s today —
the site rotates the path and splices an auth token into it. This downloads
the Next.js chunks the home page loads and prints every /api/ string and
every fetch/token-looking constant, so the collector can be pointed at the
endpoint that actually exists.

    python3 scratch/megaman/hltb_probe.py
"""
import pathlib
import re
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
JS = HERE / "hltbjs"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA,
                                               "Referer": "https://howlongtobeat.com/"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def main():
    JS.mkdir(exist_ok=True)
    home = HERE / "hltb_home.html"
    if not home.exists():
        home.write_text(get("https://howlongtobeat.com/"), encoding="utf-8",
                        newline="\n")
    s = home.read_text(encoding="utf-8")
    paths = sorted(set(re.findall(r"/_next/static/[^\"']+\.js", s)))
    for p in paths:
        out = JS / p.rsplit("/", 1)[-1]
        if not out.exists():
            out.write_text(get("https://howlongtobeat.com" + p),
                           encoding="utf-8", newline="\n")
    for p in sorted(JS.glob("*.js")):
        body = p.read_text(encoding="utf-8", errors="replace")
        hits = set(re.findall(r'"/api/[^"]*"', body))
        hits |= set(re.findall(r"'/api/[^']*'", body))
        if not hits:
            continue
        print("== %s (%d bytes)" % (p.name, len(body)))
        for h in sorted(hits):
            print("   ", h)
        for m in re.finditer(r"/api/", body):
            print("    ctx:", repr(body[max(0, m.start() - 220):m.start() + 160]))


if __name__ == "__main__":
    main()
