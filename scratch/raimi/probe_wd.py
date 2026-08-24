"""Probe: does Wikidata carry per-episode runtimes for Ash vs Evil Dead?"""
import json
import pathlib
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from gwlib import wikidata

UA = "GroupWatch/1.0 (reading-list builder)"

qid = wikidata.qids_for(["Ash vs Evil Dead"])
print("series qid:", qid)
series = qid["Ash vs Evil Dead"]

q = """
SELECT ?ep ?epLabel ?num ?dur WHERE {
  ?ep wdt:P179 wd:%s .
  OPTIONAL { ?ep wdt:P1545 ?num . }
  OPTIONAL { ?ep wdt:P2047 ?dur . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
LIMIT 300
""" % series
url = "https://query.wikidata.org/sparql?format=json&query=" + urllib.parse.quote(q)
req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/sparql-results+json"})
try:
    d = json.loads(urllib.request.urlopen(req, timeout=120).read().decode("utf-8"))
except Exception as e:
    print("SPARQL ERR", type(e).__name__, e)
    raise SystemExit(1)
rows = d["results"]["bindings"]
print("rows:", len(rows))
withdur = [r for r in rows if r.get("dur")]
print("with runtime:", len(withdur))
for r in rows[:40]:
    print(" ", r["ep"]["value"].rsplit("/", 1)[-1],
          r.get("epLabel", {}).get("value"),
          r.get("num", {}).get("value"),
          r.get("dur", {}).get("value"))
