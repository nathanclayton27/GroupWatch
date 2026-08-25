"""Probe: what does Wikidata carry for everything Wes Anderson directed?

    PYTHONIOENCODING=utf-8 python scratch/wesanderson/probe_wd.py

Two questions the shorts decision hangs on:

  1. Do the ten shorts in the filmography's Short films table have Wikidata
     items at all, and do those items carry P2047 runtimes? Six of the ten
     have no en-wiki article (The Swan, The Rat Catcher, Poison, Do You Like
     to Read?, Cousin Ben Troop Screening, Asteroid City: Location Featurette)
     and the 1993 Bottle Rocket short redirects to the 1996 feature, so the
     pageprops route alone cannot answer this.
  2. Does that set agree with the article's Feature films table?

The query service (query.wikidata.org) was 429ing hard when this was written
("aggressively rate-limiting to 1 req / min ... active wdqs outage"), so the
sweep goes through wikidata.org's CirrusSearch instead: haswbstatement:P57=Q…
enumerates every item claiming him as director, and wbgetentities reads the
claims. Same answer, no SPARQL.

Its P2047 column is deliberately rank-blind — it uses gwlib's runtime() as-is —
and that is how the third finding turned up: The Phoenician Scheme prints 120
here and ships 105, because its item carries a *deprecated* 120 beside a live
105. The collector reads rank; this probe does not, and the gap between the two
numbers is the evidence.

Prints; writes nothing. The collector is scratch/wesanderson/collect.py.
"""
import pathlib
import sys
import urllib.parse

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from gwlib import wiki, wikidata

WD_API = "https://www.wikidata.org/w/api.php"
HIM = "Q223687"


def directed_items():
    """Every Wikidata item with P57 = Wes Anderson, via CirrusSearch."""
    out, offset = [], 0
    while True:
        q = urllib.parse.urlencode({
            "action": "query", "list": "search", "format": "json",
            "formatversion": "2", "srlimit": "50", "sroffset": str(offset),
            "srsearch": "haswbstatement:P57=%s" % HIM})
        d = wiki.get_json(WD_API + "?" + q)
        out += [x["title"] for x in d["query"]["search"]]
        cont = d.get("continue", {}).get("sroffset")
        if not cont:
            return out
        offset = cont


def main():
    qids = wikidata.qids_for(["Wes Anderson"])
    print("Wes Anderson qid: %s (probe assumes %s)" % (qids, HIM))
    assert qids["Wes Anderson"] == HIM, qids

    items = directed_items()
    print("items claiming P57=Wes Anderson: %d" % len(items))

    # labels + claims in one pass
    rows = []
    for i in range(0, len(items), 40):
        q = urllib.parse.urlencode({
            "action": "wbgetentities", "format": "json", "formatversion": "2",
            "ids": "|".join(items[i:i + 40]), "props": "claims|labels",
            "languages": "en"})
        d = wiki.get_json(WD_API + "?" + q)
        for qid, ent in d["entities"].items():
            c = ent.get("claims", {})
            rows.append({
                "qid": qid,
                "label": (ent.get("labels", {}).get("en") or {}).get("value", ""),
                "years": sorted(set(wikidata.pub_years(c))),
                "runtime_any": wikidata.runtime(c, lo=1, hi=400),
                "runtime_gated": wikidata.runtime(c),
                "instance": [s["mainsnak"].get("datavalue", {})
                             .get("value", {}).get("id")
                             for s in c.get("P31", [])],
            })

    rows.sort(key=lambda r: (r["years"] or [9999], r["label"]))
    print("%-10s %-50s %-6s %-8s %s" % ("QID", "label", "year", "P2047", "P31"))
    for r in rows:
        print("  %-10s %-50s %-6s %-8s %s"
              % (r["qid"], r["label"][:50],
                 ",".join(str(y) for y in r["years"]) or "-",
                 r["runtime_any"] if r["runtime_any"] else "NONE",
                 ",".join(x for x in r["instance"] if x)[:40]))
    print("\ndistinct items: %d;  carrying any P2047: %d"
          % (len(rows), sum(1 for r in rows if r["runtime_any"])))


if __name__ == "__main__":
    main()
