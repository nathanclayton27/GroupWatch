"""Cross-check the document's numbering against Wikipedia. Verification only —
Wikipedia is never the scope here; where the two disagree the document wins and
the disagreement gets reported."""
import json, pathlib, re, urllib.request, html

HERE = pathlib.Path(__file__).resolve().parent
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/126.0.0.0 Safari/537.36"}
API = ("https://en.wikipedia.org/w/api.php?action=query&prop=extracts"
       "&explaintext=1&format=json&redirects=1&titles=%s")

for page in ("Spawn (comics)", "Curse of the Spawn", "Spawn: The Dark Ages",
             "King Spawn", "Gunslinger Spawn", "The Scorched"):
    cache = HERE / ("wiki_%s.txt" % re.sub(r"\W+", "_", page).strip("_"))
    if not cache.exists():
        req = urllib.request.Request(API % urllib.parse.quote(page), headers=UA)
        data = json.loads(urllib.request.urlopen(req, timeout=60).read())
        pages = data["query"]["pages"]
        text = next(iter(pages.values())).get("extract", "")
        cache.write_text(text, encoding="utf-8")
    text = cache.read_text(encoding="utf-8")
    print("\n===== %s (%d chars)" % (page, len(text)))
    for m in re.finditer(r"[^.\n]*#\s?\d+[^.\n]*\.", text[:4000]):
        print("   ", m.group(0).strip()[:200])
    for m in re.finditer(r"[^.\n]*\b(issues?|ran|published|ongoing)\b[^.\n]*\.",
                         text[:2500]):
        print("   *", m.group(0).strip()[:200])
