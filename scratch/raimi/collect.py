#!/usr/bin/env python3
"""Collect the Sam Raimi list's source data.

    PYTHONIOENCODING=utf-8 python scratch/raimi/collect.py

Two Wikipedia articles, both cached as raw wikitext under scratch/raimi/cache/
so a re-run is offline and reviewable:

  * "Sam Raimi" — the Filmography section's Film table is the authority on
    what he directed. Only rows whose Director cell is a bare {{yes}} count;
    {{partial|2nd unit}} (The Hudsucker Proxy) is not a directing credit, and
    the Producer only / Executive producer only / Acting roles tables beside
    it are ignored entirely. The Short film table is ignored too.
  * "Ash vs Evil Dead" — thirty {{Episode list}} entries across three season
    headings, each carrying its own DirectedBy field. The per-episode director
    is read, never assumed: Raimi directed the pilot and nothing else.

Runtimes come from Wikidata P2047 with a P577 year gate, for the films only.
The episodes have Wikidata items (all thirty) but not one of them carries a
runtime, and the series article states only a range — so no episode runtime is
collected, and none is invented downstream.

Writes scratch/raimi/raimi_data.json.
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from gwlib import wiki, wikidata

CACHE = HERE / "cache"

# The Film table's columns, in table order, after the Year cell.
FILM_COLS = ["title", "director", "writer", "producer", "editor", "notes"]


def film_table(text):
    """Rows of the Filmography > Film wikitable, rowspan years carried down."""
    start = text.index("==Filmography==")
    seg = text[start:text.index("===Short film===", start)]
    seg = seg[seg.index("{|"):]
    seg = seg[:seg.index("\n|}")]          # first table only: the Film table
    rows, year = [], None
    for chunk in seg.split("\n|-")[1:]:
        cells = []
        for line in chunk.split("\n"):
            line = line.strip()
            if line.startswith("|") and not line.startswith("|}"):
                cells.append(line[1:].strip())
        if not cells:
            continue
        # A rowspan on the Year cell means the following rows omit it.
        if re.match(r'^rowspan="?\d+"?\s*\|', cells[0]):
            year = cells[0].split("|", 1)[1].strip()
            cells = cells[1:]
        elif re.fullmatch(r"(19|20)\d{2}", cells[0]):
            year = cells[0]
            cells = cells[1:]
        if len(cells) < 5:
            continue
        row = dict(zip(FILM_COLS, cells + [""] * 6))
        row["year"] = int(year)
        rows.append(row)
    return rows


def wikilink(cell):
    """([[Target|Label]] -> Target, Label); a bare [[X]] gives (X, X)."""
    m = re.search(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]", cell)
    if m:
        return m.group(1), (m.group(2) or m.group(1))
    return None, wiki.clean(cell)


def series_overview(text):
    """{season -> declared episode count} from the {{Series overview}} box —
    kept so the generator can fail loudly if it ever disagrees with the
    enumerated episode tables."""
    m = re.search(r"\{\{Series overview(.*?)\n\}\}", text, re.S)
    assert m, "no Series overview box"
    return {int(k): int(v)
            for k, v in re.findall(r"\|\s*episodes(\d+)\s*=\s*(\d+)", m.group(1))}


def episodes_by_season(text):
    """[{season, overall, num, title, director, writers, year}] for all rows,
    seasons taken from the ===Season N=== headings the tables sit under."""
    heads = [(int(m.group(1)), m.start())
             for m in re.finditer(r"^===Season (\d+) \(", text, re.M)]
    assert heads, "no season headings"
    bounds = [(n, s, heads[i + 1][1] if i + 1 < len(heads) else len(text))
              for i, (n, s) in enumerate(heads)]
    out = []
    for season, lo, hi in bounds:
        for overall, num, title, year, block in wiki.episodes(text[lo:hi]):

            def field(name, block=block):
                fm = re.search(r"\|\s*%s\s*=\s*(.*?)(?=\n\s*\||\Z)" % name,
                               block, re.S)
                return wiki.clean(fm.group(1)) if fm else ""

            out.append({"season": season, "overall": overall, "num": num,
                        "t": title, "year": year,
                        "director": field("DirectedBy"),
                        "writers": field("WrittenBy")})
    return out


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    raimi = wiki.wikitext("Sam Raimi", cache_dir=CACHE)
    avoid = wiki.wikitext("Ash vs Evil Dead", cache_dir=CACHE)

    rows = film_table(raimi)
    assert len(rows) >= 20, len(rows)
    directed = [r for r in rows if r["director"].strip() == "{{yes}}"]
    assert directed, "no directing credits parsed"

    films = []
    for r in directed:
        page, label = wikilink(r["title"])
        films.append({
            "t": label,
            "page": page or label,
            "year": r["year"],
            "tablenote": wiki.clean(r["notes"]),
            "wrote": r["writer"].strip() == "{{yes}}",
            "runtime": None,
        })
    films.sort(key=lambda f: (f["year"], f["t"]))

    # Runtimes: Wikidata P2047, gated on a P577 within a year of the table's
    # year so a same-titled item can't slip a wrong runtime in.
    qids = wikidata.qids_for([f["page"] for f in films])
    claims = wikidata.claims_for(qids.values())
    for f in films:
        q = qids.get(f["page"])
        c = claims.get(q) if q else None
        if c and wikidata.year_gate(c, f["year"]):
            f["runtime"] = wikidata.runtime(c)
        f["qid"] = q
        # P577 publication years, kept so the generator can refuse to ship a
        # film the table lists but nothing has actually released.
        f["pubyears"] = sorted(set(wikidata.pub_years(c))) if c else []
    missing = [f["t"] for f in films if not f["runtime"]]

    # Fallback for anything Wikidata does not carry: the film article's own
    # infobox runtime field. Still read, never typed.
    for f in films:
        if f["runtime"]:
            continue
        t = wiki.wikitext(f["page"], cache_dir=CACHE)
        fb = wiki.infobox(t) if t else None
        m = re.search(r"(\d+)\s*minutes", wiki.clean(fb("runtime"))) if fb else None
        if m:
            f["runtime"] = int(m.group(1))
            f["runtime_src"] = "infobox"
        else:
            f["runtime_src"] = None
    for f in films:
        f.setdefault("runtime_src", "wikidata")

    eps = episodes_by_season(avoid)
    overview = series_overview(avoid)
    fb = wiki.infobox(avoid, kind="television")
    listy = lambda v: [x.strip() for x in wiki.clean(v).split(",") if x.strip()]
    series = {
        "runtime_field": wiki.clean(fb("runtime")),
        "declared_episodes": int(re.search(r"\d+", wiki.clean(fb("num_episodes"))).group(0)),
        "declared_seasons": int(wiki.clean(fb("num_seasons"))),
        "developer": listy(fb("developer")),
        "executive_producer": listy(fb("executive_producer")),
        "channel": wiki.clean(fb("channel")),
        "overview": overview,
    }

    data = {"films": films, "episodes": eps, "series": series}
    out = HERE / "raimi_data.json"
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(data, indent=1, ensure_ascii=False) + "\n")

    print("films directed: %d" % len(films))
    for f in films:
        print("   %s  %-46s %s min  (%s)"
              % (f["year"], f["t"], f["runtime"], f["runtime_src"]))
    print("runtime gaps after Wikidata: %s" % (missing or "none"))
    print("episodes: %d  (overview declares %s, infobox %s)"
          % (len(eps), overview, series["declared_episodes"]))
    print("series runtime field: %r" % series["runtime_field"])
    byraimi = [e for e in eps if "Sam Raimi" in e["director"]]
    print("episodes directed by Raimi: %d — %s"
          % (len(byraimi), [(e["season"], e["num"], e["t"]) for e in byraimi]))
    print("wrote %s" % out)


if __name__ == "__main__":
    main()
