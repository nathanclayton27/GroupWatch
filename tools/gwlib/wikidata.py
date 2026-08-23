"""Wikidata batch lookups with the year gates that keep wrong items out.

The year gate exists because a title search once matched the 2018 slasher
Night Shift to Stephen King's 1978 story collection; P577 within a year of
the claimed release is the price of believing a runtime.
"""
import time
import urllib.parse

from . import wiki

WD = "https://www.wikidata.org/w/api.php"


def qids_for(pages, sleep=2.5):
    """{page title -> QID} via the enwiki pageprops API, redirects resolved,
    batched 40 per request."""
    out = {}
    pages = [p for p in pages if p]
    for i in range(0, len(pages), 40):
        q = urllib.parse.urlencode({
            "action": "query", "format": "json", "formatversion": "2",
            "prop": "pageprops", "ppprop": "wikibase_item", "redirects": "1",
            "titles": "|".join(pages[i:i + 40])})
        d = wiki.get_json(wiki.API + "?" + q)
        time.sleep(sleep)
        norm = {}
        for k in ("normalized", "redirects"):
            for m in d.get("query", {}).get(k, []):
                norm[m["from"]] = m["to"]
        by = {p["title"]: p.get("pageprops", {}).get("wikibase_item")
              for p in d["query"]["pages"]}
        for c in pages[i:i + 40]:
            x = c
            while x in norm:
                x = norm[x]
            if by.get(x):
                out[c] = by[x]
    return out


def claims_for(qids, sleep=2.5):
    """{QID -> claims dict}, batched 40 per request."""
    out = {}
    ids = sorted(set(q for q in qids if q))
    for i in range(0, len(ids), 40):
        q = urllib.parse.urlencode({
            "action": "wbgetentities", "format": "json", "formatversion": "2",
            "ids": "|".join(ids[i:i + 40]), "props": "claims"})
        for k, v in wiki.get_json(WD + "?" + q)["entities"].items():
            out[k] = v.get("claims", {})
        time.sleep(sleep)
    return out


def runtime(claims, lo=15, hi=250):
    """Best P2047 in minutes within [lo, hi], else None. Takes the longest
    value in range — festival cuts and TV edits report short."""
    best = None
    for st in (claims or {}).get("P2047", []):
        try:
            v = float(st["mainsnak"]["datavalue"]["value"]["amount"].lstrip("+"))
        except (KeyError, TypeError, ValueError):
            continue
        if lo <= v <= hi and (best is None or v > best):
            best = v
    return int(round(best)) if best else None


def pub_years(claims):
    """Every P577 publication year on the item."""
    out = []
    for st in (claims or {}).get("P577", []):
        try:
            out.append(int(st["mainsnak"]["datavalue"]["value"]["time"][1:5]))
        except (KeyError, TypeError, ValueError):
            pass
    return out


def year_gate(claims, year, slack=1):
    """True when the item's publication dates are compatible with `year`.
    An item with no P577 passes (absence is not contradiction)."""
    ys = pub_years(claims)
    return not ys or min(abs(y - year) for y in ys) <= slack
