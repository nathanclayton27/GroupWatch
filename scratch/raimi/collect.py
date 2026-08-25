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

Film runtimes come from Wikidata P2047 with a P577 year gate, read at
statement rank — Doctor Strange in the Multiverse of Madness carries a
*preferred* 126 beside a normal 127, and gwlib's rank-blind reader takes the
longest, which is the number Wikidata itself demotes.

Episode runtimes barely exist. All thirty episodes have Wikidata items and the
sweep here re-checks every one of them for P2047: none carries it, and the
series infobox states only a range. The single exception is the pilot, which
has its own article — "El Jefe (Ash vs Evil Dead)" — whose episode infobox
gives `length = 41 minutes`, corroborated by the series infobox's own
"41 minutes (pilot)" line. Both are read and required to agree. Nothing else
about the show's running time is collected, and none of it is invented
downstream.

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
MINUTE = "Q7727"                       # the only unit P2047 is read in here
PILOT_PAGE = "El Jefe (Ash vs Evil Dead)"

# The Film table's columns, in table order, after the Year cell.
FILM_COLS = ["title", "director", "writer", "producer", "editor", "notes"]


def p2047(claims, lo=15, hi=250):
    """The item's runtime in minutes, honouring statement rank.

    gwlib.wikidata.runtime takes the longest in-range P2047 and ignores rank,
    which is right for the festival-cut case it was written for and wrong
    here: Doctor Strange in the Multiverse of Madness carries a *preferred*
    126 beside a normal 127, and preferred is Wikidata's way of saying "this
    is the value to use". Taking the longest quietly overrode the source's own
    ranking. So: deprecated statements are dropped, preferred rank wins
    outright if present, and only then does the longest-in-range rule apply.
    The unit is checked too — an item quoting seconds would otherwise sail
    through as minutes.

    Returns (minutes or None, [every value seen with its rank]).
    """
    seen, best = [], {}
    for st in (claims or {}).get("P2047", []):
        v = st.get("mainsnak", {}).get("datavalue", {}).get("value", {})
        try:
            amt = float(str(v["amount"]).lstrip("+"))
        except (KeyError, TypeError, ValueError):
            continue
        unit = str(v.get("unit", "")).rsplit("/", 1)[-1]
        rank = st.get("rank", "normal")
        seen.append({"amount": amt, "unit": unit, "rank": rank})
        if rank == "deprecated" or unit != MINUTE or not (lo <= amt <= hi):
            continue
        best.setdefault(rank, []).append(amt)
    vals = best.get("preferred") or best.get("normal") or []
    return (int(round(max(vals))) if vals else None), seen


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

            def raw(name, block=block):
                fm = re.search(r"\|\s*%s\s*=\s*(.*?)(?=\n\s*\||\Z)" % name,
                               block, re.S)
                return fm.group(1) if fm else ""

            def field(name, block=block):
                return wiki.clean(raw(name, block))

            # the Title cell's wikilink target, so the episode's own Wikidata
            # item can be looked up and re-checked for a runtime
            page, _ = wikilink(raw("Title"))
            out.append({"season": season, "overall": overall, "num": num,
                        "t": title, "year": year, "page": page or title,
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
        f["p2047_seen"] = []
        if c and wikidata.year_gate(c, f["year"]):
            f["runtime"], f["p2047_seen"] = p2047(c)
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

    # Every episode's own Wikidata item, re-checked for P2047 rather than
    # taken on trust from an earlier probe. The count that comes out of this
    # is what licenses the list to weigh 29 rows at zero.
    epqids = wikidata.qids_for([e["page"] for e in eps])
    epclaims = wikidata.claims_for(epqids.values())
    for e in eps:
        q = epqids.get(e["page"])
        e["qid"] = q
        e["runtime"], e["p2047_seen"] = p2047(epclaims.get(q) if q else None)
    wd_runtimes = sum(1 for e in eps if e["runtime"])
    wd_items = sum(1 for e in eps if e["qid"])

    # The pilot is the one episode with a published runtime, and it has its
    # own article to publish it: {{Infobox television episode}}'s `length`.
    pilot = [e for e in eps if e["page"] == PILOT_PAGE]
    assert len(pilot) == 1, [e["page"] for e in eps[:3]]
    ptext = wiki.wikitext(PILOT_PAGE, cache_dir=CACHE)
    pfb = wiki.infobox(ptext) if ptext else None
    pm = re.search(r"(\d+)\s*minutes", wiki.clean(pfb("length"))) if pfb else None
    assert pm, "no length in the El Jefe infobox"
    pilot[0]["runtime"] = int(pm.group(1))
    pilot[0]["runtime_src"] = "%s infobox length" % PILOT_PAGE

    overview = series_overview(avoid)
    fb = wiki.infobox(avoid, kind="television")
    listy = lambda v: [x.strip() for x in wiki.clean(v).split(",") if x.strip()]
    # the series infobox states the pilot's length too; both sources are read
    # and required to agree, so one of them going stale fails the collection
    sm = re.search(r"(\d+)\s*minutes\s*\(pilot\)", wiki.clean(fb("runtime")))
    assert sm, wiki.clean(fb("runtime"))
    assert int(sm.group(1)) == pilot[0]["runtime"], \
        "series infobox says %s for the pilot, the episode article says %s" \
        % (sm.group(1), pilot[0]["runtime"])
    series = {
        "runtime_field": wiki.clean(fb("runtime")),
        "pilot_runtime": pilot[0]["runtime"],
        "pilot_runtime_src": pilot[0]["runtime_src"],
        "episodes_with_wikidata_item": wd_items,
        "episodes_with_wikidata_runtime": wd_runtimes,
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
        junk = [s for s in f["p2047_seen"]
                if s["rank"] != "normal" or s["unit"] != MINUTE
                or s["amount"] != f["runtime"]]
        print("   %s  %-46s %s min  (%s)%s"
              % (f["year"], f["t"], f["runtime"], f["runtime_src"],
                 "   also saw %s" % [(s["amount"], s["rank"]) for s in junk]
                 if junk else ""))
    print("runtime gaps after Wikidata: %s" % (missing or "none"))
    print("films total: %d min" % sum(f["runtime"] for f in films))
    print("episodes: %d  (overview declares %s, infobox %s)"
          % (len(eps), overview, series["declared_episodes"]))
    print("episodes with a Wikidata item: %d; with P2047 on it: %d"
          % (wd_items, wd_runtimes))
    print("series runtime field: %r" % series["runtime_field"])
    print("pilot: %s — %d min (%s)"
          % (pilot[0]["t"], pilot[0]["runtime"], pilot[0]["runtime_src"]))
    byraimi = [e for e in eps if "Sam Raimi" in e["director"]]
    print("episodes directed by Raimi: %d — %s"
          % (len(byraimi), [(e["season"], e["num"], e["t"]) for e in byraimi]))
    print("wrote %s" % out)


if __name__ == "__main__":
    main()
