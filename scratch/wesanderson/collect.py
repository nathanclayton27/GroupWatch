#!/usr/bin/env python3
"""Collect the Wes Anderson list's source data.

    PYTHONIOENCODING=utf-8 python scratch/wesanderson/collect.py

One Wikipedia article is the authority — "Wes Anderson filmography" — cached
as raw wikitext under scratch/wesanderson/cache/ so a re-run is offline and
reviewable.

  * "As a director > Feature films" is the list. Thirteen rows, every one of
    them a bare {{yes}} in the Director column. The Producer only and
    Executive producer only bullet lists beside it are ignored; so are the
    Commercials, Music Videos and As an actor tables.
  * "As a director > Short films" is collected too, ten rows, even though the
    shipped list has no shorts section. Collecting them is what turns the
    shorts decision into a checked fact rather than a claim: the generator
    asserts how many of the ten can be weighted from the one runtime source,
    and the answer (7 of 10) is why they are not shipped.

Runtimes come from Wikidata P2047 and from nothing else, gated on a P577
within a year of the table's year so a same-titled item cannot slip a wrong
number in. Twelve of the thirteen features carry P2047 directly.

The thirteenth, The Wonderful Story of Henry Sugar and Three More (2024), is
a compilation: its Wikidata item has no P2047 of its own but does carry P527
"has part", naming exactly the four 2023 Roald Dahl shorts, each of which
carries P2047. So its runtime is the sum of its own declared parts' P2047 —
still one source, still read rather than typed, and recorded here under a
separate runtime_src so the generator can assert that exactly one row took
that route. (Independent corroboration, not shipped: the film's own article
infobox says 88 minutes, which is 37 + 17 + 17 + 17.)

Wikidata's query service was rate-limiting to one request a minute when this
was written, so the "everything he directed" sweep goes through wikidata.org's
CirrusSearch — haswbstatement:P57=Q223687 — instead of SPARQL. Same answer.

Writes scratch/wesanderson/wes_anderson_data.json.
"""
import json
import pathlib
import re
import sys
import urllib.parse

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from gwlib import wiki, wikidata

CACHE = HERE / "cache"
WD_API = "https://www.wikidata.org/w/api.php"
HIM = "Q223687"                       # Wes Anderson on Wikidata

FEATURE_COLS = ["year", "title", "director", "writer", "producer"]
SHORT_COLS = ["year", "title", "director", "writer", "producer", "notes"]
AD_COLS = ["year", "title", "director", "writer", "company", "notes"]
MV_COLS = ["year", "title", "director", "artist", "notes"]

MINUTE = "Q7727"                      # the only unit P2047 is read in here


def p2047(claims, lo=15, hi=250):
    """The item's runtime in minutes, honouring statement rank.

    gwlib.wikidata.runtime takes the longest in-range P2047 and ignores rank,
    which is right for the festival-cut case it was written for and wrong
    here: The Phoenician Scheme's item carries a *deprecated* 120 beside a
    normal-rank 105, and deprecated is Wikidata's way of saying "this value is
    wrong". Taking the longest would have shipped the number the source itself
    flags as bad. So: deprecated statements are dropped, preferred rank wins
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


def section(text, head, nexthead):
    """The wikitext between two headings."""
    i = text.index(head)
    return text[i:text.index(nexthead, i)]


def first_table(seg):
    """The first wikitable in a chunk, without its {| ... |} fence."""
    seg = seg[seg.index("{|"):]
    return seg[:seg.index("\n|}")]


def cells(chunk):
    """A row's raw cells. These tables mix one-cell-per-line with inline `||`
    separators inside the same table (the Short films table does both in one
    row), so both have to be honoured. Splitting on `||` is safe: wikilinks
    and templates use a single pipe."""
    out = []
    for line in chunk.split("\n"):
        line = line.strip()
        if not line.startswith("|") or line.startswith("|}") or line.startswith("|-"):
            continue
        out += [c.strip() for c in line[1:].split("||")]
    return out


def rows(seg, cols):
    """Table rows as dicts, with rowspan cells carried down to the rows they
    cover. Positional cell-picking without the carry silently shifts every
    column after a rowspan — the Short films table has two of them."""
    out, pending = [], {}
    for chunk in seg.split("\n|-")[1:]:
        raw = iter(cells(chunk))
        row, ok = [], True
        for c in range(len(cols)):
            if c in pending:
                row.append(pending[c][1])
                pending[c][0] -= 1
                if pending[c][0] == 0:
                    del pending[c]
                continue
            v = next(raw, None)
            if v is None:
                row.append("")
                continue
            m = re.match(r'^rowspan\s*=\s*"?(\d+)"?\s*\|(.*)$', v, re.S)
            if m:
                span, v = int(m.group(1)), m.group(2).strip()
                if span > 1:
                    pending[c] = [span - 1, v]
            row.append(v)
        if not any(row):
            continue
        d = dict(zip(cols, row))
        if not re.fullmatch(r"(19|20)\d{2}", d["year"].strip()):
            ok = False
        if ok:
            d["year"] = int(d["year"])
            out.append(d)
    return out


def wikilink(cell):
    """([[Target|Label]] -> Target, Label); a bare [[X]] gives (X, X); a plain
    ''Title'' gives (None, Title)."""
    m = re.search(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]", cell)
    if m:
        return m.group(1), wiki.clean(m.group(2) or m.group(1))
    return None, wiki.clean(cell)


def directed_items():
    """Every Wikidata item claiming P57 = Wes Anderson, with label, publication
    years and P2047. CirrusSearch rather than SPARQL — see the module docstring.
    This is what proves a short has no runtime rather than merely no article:
    six of the ten shorts have no en-wiki page for pageprops to resolve."""
    qids, offset = [], 0
    while True:
        q = urllib.parse.urlencode({
            "action": "query", "list": "search", "format": "json",
            "formatversion": "2", "srlimit": "50", "sroffset": str(offset),
            "srsearch": "haswbstatement:P57=%s" % HIM})
        d = wiki.get_json(WD_API + "?" + q)
        qids += [x["title"] for x in d["query"]["search"]]
        offset = d.get("continue", {}).get("sroffset")
        if not offset:
            break
    out = {}
    for i in range(0, len(qids), 40):
        q = urllib.parse.urlencode({
            "action": "wbgetentities", "format": "json", "formatversion": "2",
            "ids": "|".join(qids[i:i + 40]), "props": "claims|labels",
            "languages": "en"})
        for qid, ent in wiki.get_json(WD_API + "?" + q)["entities"].items():
            c = ent.get("claims", {})
            # a wide band here: this sweep covers two-minute promos as well as
            # features, and its only job is to say whether a runtime exists
            rt, seen = p2047(c, lo=1, hi=400)
            out[qid] = {
                "label": (ent.get("labels", {}).get("en") or {}).get("value", ""),
                "years": sorted(set(wikidata.pub_years(c))),
                "runtime": rt,
                "p2047_seen": seen,
                "parts": [s["mainsnak"].get("datavalue", {}).get("value", {}).get("id")
                          for s in c.get("P527", [])],
            }
    return out


def article_facts(page):
    """The handful of article facts the section intros and row notes lean on,
    read from the film's own page. Never a runtime source — those all come
    from P2047 — but the writing credits, the distributors and the "is this
    one of the stop-motion ones" question are things the copy asserts, and an
    intro asserting something nobody checked is a guess.

    `lead` is the article's opening prose with the infobox cut off, kept so
    the generator can require the word "stop-motion" to be there before a row
    calls a film stop-motion."""
    t = wiki.wikitext(page, cache_dir=CACHE)
    fb = wiki.infobox(t) if t else None
    if not fb:
        return {}
    out = {}
    for f in ("screenplay", "writer", "story", "based_on", "distributor",
              "country", "studio", "runtime", "released"):
        v = wiki.clean(fb(f))
        if v:
            out[f] = v
    out["lead"] = wiki.clean(lead_of(t)[:1600])[:900]
    return out


def lead_of(text):
    """The article's prose, with the infobox counted past brace by brace.

    Anchoring on ^''' looked fine on twelve of the thirteen and silently
    returned nothing for the thirteenth: Isle of Dogs opens inside
    {{Nihongo|'''''Isle of Dogs'''''|犬ヶ島|…}}, so the bold title is not at the
    start of a line. An empty lead would have quietly failed the stop-motion
    check for the one film the check exists for."""
    i = text.find("{{Infobox film")
    if i < 0:
        return text
    depth, j = 0, i
    while j < len(text) - 1:
        if text[j:j + 2] == "{{":
            depth, j = depth + 1, j + 2
        elif text[j:j + 2] == "}}":
            depth, j = depth - 1, j + 2
            if depth == 0:
                return text[j:]
        else:
            j += 1
    return text[i:]


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    art = wiki.wikitext("Wes Anderson filmography", cache_dir=CACHE)

    feat_chunk = section(art, "=== Feature films ===", "=== Short films ===")
    feat_rows = rows(first_table(feat_chunk), FEATURE_COLS)
    short_rows = rows(first_table(section(art, "=== Short films ===",
                                          "=== Commercials ===")), SHORT_COLS)
    # The other-people's-films work, so the shipped "directing only" note can
    # name it from the article instead of from anyone's memory: the two bullet
    # lists under the Feature films table, the Commercials table and the one
    # Music Videos table.
    other = {}
    for head in ("Producer only", "Executive producer only"):
        seg = feat_chunk[feat_chunk.index("'''%s'''" % head) + len(head) + 6:]
        bullets = []
        for line in seg.split("\n"):
            if line.startswith("*"):
                bullets.append(wiki.clean(line[1:]))
            elif bullets:
                break                  # the list ended at the first non-bullet
        other[head] = bullets
    ads = rows(first_table(section(art, "=== Commercials ===",
                                   "=== Music Videos ===")), AD_COLS)
    mvs = rows(first_table(section(art, "=== Music Videos ===",
                                   "== As an actor ==")), MV_COLS)

    directed = [r for r in feat_rows if r["director"].strip() == "{{yes}}"]
    assert len(directed) == len(feat_rows), \
        "a Feature films row is not a bare {{yes}} director credit"

    features = []
    for r in directed:
        page, label = wikilink(r["title"])
        features.append({
            "t": label,
            "page": page or label,
            "year": r["year"],
            "wrote": r["writer"].strip().lower() == "{{yes}}",
            "produced": r["producer"].strip().lower() == "{{yes}}",
            "producer_cell": wiki.clean(r["producer"]),
            "runtime": None,
            "runtime_src": None,
        })
    features.sort(key=lambda f: (f["year"], f["t"]))

    shorts = []
    for r in short_rows:
        page, label = wikilink(r["title"])
        shorts.append({"t": label, "page": page, "year": r["year"],
                       "tablenote": wiki.clean(r["notes"])})
    shorts.sort(key=lambda s: (s["year"], s["t"]))

    # ---- Wikidata ---------------------------------------------------------
    sweep = directed_items()
    qids = wikidata.qids_for([f["page"] for f in features])
    claims = wikidata.claims_for(qids.values())

    for f in features:
        q = qids.get(f["page"])
        f["qid"] = q
        c = claims.get(q) if q else None
        f["pubyears"] = sorted(set(wikidata.pub_years(c))) if c else []
        rt, seen = p2047(c) if c else (None, [])
        f["p2047_seen"] = seen
        f["year_gate"] = bool(c) and wikidata.year_gate(c, f["year"])
        if f["year_gate"] and rt:
            f["runtime"], f["runtime_src"] = rt, "P2047"
        if f["runtime"]:
            continue
        # No P2047 of its own. If the item declares its own parts (P527) and
        # every one of them carries P2047, the sum of those is this film's
        # runtime — same property, same database, composed by the item's own
        # statement about what it is made of. Nothing else is attempted: a
        # film whose runtime cannot be reached this way ships unweighted, and
        # the generator decides what that costs the whole list.
        parts = [p for p in ((sweep.get(q) or {}).get("parts") or []) if p]
        got = [sweep.get(p) for p in parts]
        f["parts"] = [{"qid": p, "label": (sweep.get(p) or {}).get("label"),
                       "runtime": (sweep.get(p) or {}).get("runtime"),
                       "years": (sweep.get(p) or {}).get("years")}
                      for p in parts]
        def part_ok(g, year=f["year"]):
            # a part must exist, carry P2047, and have released within a year
            # of the compilation (an absent P577 is not a contradiction)
            return bool(g and g["runtime"] and
                        (not g["years"] or
                         min(abs(y - year) for y in g["years"]) <= 1))

        if parts and all(part_ok(g) for g in got):
            f["runtime"] = sum(g["runtime"] for g in got)
            f["runtime_src"] = "P2047-sum-of-P527-parts"

    for f in features:
        c = claims.get(f["qid"]) if f["qid"] else None
        f["p31"] = [s["mainsnak"].get("datavalue", {}).get("value", {}).get("id")
                    for s in (c or {}).get("P31", [])]
        f["article"] = article_facts(f["page"])

    # Shorts: match each table row to the sweep by title and year, so "this
    # short has no runtime" is a fact about Wikidata rather than about whether
    # anybody wrote an en-wiki article for it.
    from gwlib.prop import normt
    by_title = {}
    for qid, e in sweep.items():
        by_title.setdefault(normt(e["label"]), []).append((qid, e))
    for s in shorts:
        cand = by_title.get(normt(s["t"]), [])
        # the label may carry a suffix ("Cousin Ben Troop Screening with
        # Jason Schwartzman"), so fall back to a prefix match
        if not cand:
            cand = [(q, e) for q, e in sweep.items()
                    if normt(e["label"]).startswith(normt(s["t"]))]
        cand = [(q, e) for q, e in cand
                if not e["years"] or min(abs(y - s["year"]) for y in e["years"]) <= 1]
        # the 1993 short and the 1996 feature share a title; the year gate
        # separates them
        s["qid"] = cand[0][0] if len(cand) == 1 else None
        s["wd_label"] = cand[0][1]["label"] if len(cand) == 1 else None
        s["runtime"] = cand[0][1]["runtime"] if len(cand) == 1 else None
        s["runtime_src"] = "P2047" if s["runtime"] else None

    extras = {q: e for q, e in sweep.items()
              if q not in {f["qid"] for f in features}
              and q not in {s["qid"] for s in shorts}}

    data = {"features": features, "shorts": shorts,
            "producer_only": other["Producer only"],
            "exec_producer_only": other["Executive producer only"],
            "commercials": [{"year": a["year"], "t": wiki.clean(a["title"]),
                             "company": wiki.clean(a["company"])} for a in ads],
            "music_videos": [{"year": v["year"], "t": wiki.clean(v["title"])}
                             for v in mvs],
            "sweep_size": len(sweep),
            "sweep_extras": [{"qid": q, "label": e["label"], "years": e["years"],
                              "runtime": e["runtime"]}
                             for q, e in sorted(extras.items(),
                                                key=lambda kv: kv[1]["label"])]}
    out = HERE / "wes_anderson_data.json"
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(data, indent=1, ensure_ascii=False) + "\n")

    print("features: %d" % len(features))
    for f in features:
        junk = [s for s in f["p2047_seen"]
                if s["rank"] == "deprecated" or s["unit"] != MINUTE]
        print("   %s  %-52s %4s min  (%s)%s"
              % (f["year"], f["t"], f["runtime"], f["runtime_src"],
                 "   dropped %s" % [(s["amount"], s["rank"]) for s in junk]
                 if junk else ""))
    print("shorts in the Short films table: %d" % len(shorts))
    for s in shorts:
        print("   %s  %-40s %-11s %4s min  %s"
              % (s["year"], s["t"], s["qid"] or "NO ITEM",
                 s["runtime"] if s["runtime"] else "-", s["tablenote"][:40]))
    print("shorts weightable from P2047: %d of %d"
          % (sum(1 for s in shorts if s["runtime"]), len(shorts)))
    print("P57 sweep: %d items; not on either table: %s"
          % (len(sweep), [e["label"] for e in data["sweep_extras"]]))
    print("producer only: %s" % data["producer_only"])
    print("executive producer only: %s" % data["exec_producer_only"])
    print("commercials: %d — %s"
          % (len(data["commercials"]),
             ", ".join("%s (%s)" % (a["company"], a["year"])
                       for a in data["commercials"])))
    print("music videos: %d — %s"
          % (len(data["music_videos"]),
             ", ".join(v["t"] for v in data["music_videos"])))
    print("wrote %s" % out)


if __name__ == "__main__":
    main()
