#!/usr/bin/env python3
"""Look at the raw P2047 statements on the films with famous alternate cuts.

    PYTHONIOENCODING=utf-8 python scratch/ridley/probe_wd.py

Not part of the build. This is the reconnaissance that decided how the
collector reads a runtime: which of these items carry more than one P2047,
what rank each value sits at, and what qualifiers (if any) say which cut a
value belongs to.
"""
import json
import pathlib
import sys
import urllib.parse

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from gwlib import wiki, wikidata

WD_API = "https://www.wikidata.org/w/api.php"

PAGES = ["Blade Runner", "Kingdom of Heaven (film)", "Legend (1985 film)",
         "Alien (film)", "Gladiator (2000 film)", "Napoleon (2023 film)",
         "The Counselor", "American Gangster (film)", "Robin Hood (2010 film)",
         "The Dog Stars (film)", "Black Hawk Down (film)"]


def labels(qids):
    out = {}
    ids = sorted({q for q in qids if q})
    for i in range(0, len(ids), 40):
        q = urllib.parse.urlencode({
            "action": "wbgetentities", "format": "json", "formatversion": "2",
            "ids": "|".join(ids[i:i + 40]), "props": "labels",
            "languages": "en"})
        for qid, ent in wiki.get_json(WD_API + "?" + q)["entities"].items():
            out[qid] = (ent.get("labels", {}).get("en") or {}).get("value", "")
    return out


def main():
    qids = wikidata.qids_for(PAGES)
    claims = wikidata.claims_for(qids.values())
    wanted = set()
    for page in PAGES:
        for st in (claims.get(qids.get(page)) or {}).get("P2047", []):
            for pid, qs in (st.get("qualifiers") or {}).items():
                wanted.add(pid)
                for qsnak in qs:
                    v = qsnak.get("datavalue", {}).get("value", {})
                    if isinstance(v, dict) and v.get("id"):
                        wanted.add(v["id"])
    lab = labels(wanted)

    for page in PAGES:
        q = qids.get(page)
        c = claims.get(q) or {}
        print("\n%s  %s   pub years %s"
              % (page, q, sorted(set(wikidata.pub_years(c)))))
        for st in c.get("P2047", []):
            v = st["mainsnak"].get("datavalue", {}).get("value", {})
            bits = []
            for pid, qs in (st.get("qualifiers") or {}).items():
                vals = []
                for qsnak in qs:
                    dv = qsnak.get("datavalue", {}).get("value", {})
                    if isinstance(dv, dict) and dv.get("id"):
                        vals.append("%s (%s)" % (lab.get(dv["id"], ""), dv["id"]))
                    else:
                        vals.append(json.dumps(dv, ensure_ascii=False)[:60])
                bits.append("%s=%s [%s]" % (lab.get(pid, pid), ",".join(vals), pid))
            print("    %8s  unit %-8s rank %-11s  %s"
                  % (v.get("amount"), str(v.get("unit")).rsplit("/", 1)[-1],
                     st.get("rank"), "; ".join(bits)))


if __name__ == "__main__":
    main()
