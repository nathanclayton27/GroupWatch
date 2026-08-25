#!/usr/bin/env python3
"""Probe: what does Wikidata carry for the thirteen Nolan-directed features?

    PYTHONIOENCODING=utf-8 python scratch/nolan/probe_wd.py

Prints, per film, the QID the enwiki pageprops API resolves the article to, the
P2047 runtimes on the item, the P577 publication years, and whether the year
gate passes. Run before writing the collector so the answer to "is every
runtime actually there?" is a printout rather than a hope — the Sam Raimi
build's probe_wd.py did the same job for episode runtimes and found none.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from gwlib import wikidata  # noqa: E402

PAGES = [
    ("Following", 1998),
    ("Memento (film)", 2000),
    ("Insomnia (2002 film)", 2002),
    ("Batman Begins", 2005),
    ("The Prestige", 2006),
    ("The Dark Knight", 2008),
    ("Inception", 2010),
    ("The Dark Knight Rises", 2012),
    ("Interstellar (film)", 2014),
    ("Dunkirk (2017 film)", 2017),
    ("Tenet", 2020),
    ("Oppenheimer (film)", 2023),
    ("The Odyssey (2026 film)", 2026),
]


def main():
    qids = wikidata.qids_for([p for p, _ in PAGES])
    claims = wikidata.claims_for(qids.values())
    for page, year in PAGES:
        q = qids.get(page)
        c = claims.get(q) if q else None
        raw = []
        for st in (c or {}).get("P2047", []):
            try:
                raw.append(st["mainsnak"]["datavalue"]["value"]["amount"])
            except (KeyError, TypeError):
                raw.append("?")
        print("%-26s %s  %-9s  P2047 %-28s P577 %-14s gate=%s"
              % (page, year, q, ",".join(raw) or "-",
                 sorted(set(wikidata.pub_years(c))) if c else [],
                 wikidata.year_gate(c, year) if c else "no item"))
        print("   picked runtime: %s" % (wikidata.runtime(c) if c else None))


if __name__ == "__main__":
    main()
