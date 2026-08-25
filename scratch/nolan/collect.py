#!/usr/bin/env python3
"""Collect the Christopher Nolan list's source data.

    PYTHONIOENCODING=utf-8 python scratch/nolan/collect.py

One Wikipedia article is the authority — "Christopher Nolan filmography", a
featured list — cached as raw wikitext under scratch/nolan/cache/ so a re-run
is offline and reviewable. Nothing is read out of the article's prose summary;
the enumerated tables are what count.

  * "== Feature film ==" is a five-column table (Year, Title, Director, Writer,
    Producer). A row counts as his only when the Director cell is a bare
    {{yes}}. That drops exactly one row — Man of Steel (2013), where he is
    producer and story writer and Zack Snyder directed — leaving thirteen.
  * The "Executive producer" table under it and the "== Short films ==" table
    below are read too, but only so the generator can state how many rows it is
    deliberately leaving out and fail if either table grows. The short-film
    table is a separate table under a separate heading: the source does not
    treat any short as a feature.
  * "== Documentary appearances ==" is read for the same reason. Those are
    on-camera appearances in other people's films, not credits of his.

Runtimes come from Wikidata P2047, gated on a P577 within a year of the table's
year, for every film — the pattern the Sam Raimi build proved. Each film's own
Wikipedia infobox runtime is collected alongside, but ONLY as a cross-check
that the generator prints: mixing the two sources row by row is what makes a
total-hours figure meaningless, so the generator asserts every shipped runtime
came from Wikidata. Two of the thirteen disagree between the sources by a
minute, which is exactly why the rule exists.

Each film's infobox `based_on` is collected so the adaptation notes on the list
are read out of the source rather than typed from memory, and `studio` /
`distributor` so the era intros can name a studio without guessing.

Writes scratch/nolan/nolan_data.json.
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from gwlib import wiki, wikidata  # noqa: E402

PAGE = "Christopher Nolan filmography"
CACHE = HERE / "cache"

# The Feature film table's columns, in table order, after the Year header cell.
# The Ref column carries rowspans and is never read, so it is not listed.
FILM_COLS = ["title", "director", "writer", "producer"]


def strip_refs(t):
    """Footnote markup removed whole, before any line-based cell splitting —
    a multi-line <ref> block contains lines starting with '|' and would
    otherwise be counted as table cells."""
    t = re.sub(r"<ref[^>]*/>", "", t)
    return re.sub(r"<ref.*?</ref>", "", t, flags=re.S)


def section(text, start, end):
    """The wikitext between two markers, end exclusive."""
    i = text.index(start)
    return text[i:text.index(end, i)]


def first_table(seg):
    """The first wikitable in a segment, braces excluded."""
    seg = seg[seg.index("{|"):]
    return seg[:seg.index("\n|}")]


def rows(seg, cols):
    """[(year, {col: cell}, efn)] for a plainrowheaders table whose row header
    is the year. Cells are taken positionally from the front of the row, so a
    trailing rowspan'd Ref column that later rows omit cannot shift anything."""
    out = []
    for chunk in strip_refs(seg).split("\n|-")[1:]:
        lines = [l.strip() for l in chunk.split("\n") if l.strip()]
        head = next((l for l in lines if l.startswith("!scope=row")), None)
        if not head:
            continue
        year = int(re.search(r"(19|20)\d{2}", head).group(0))
        cells = [l[1:].strip() for l in lines
                 if l.startswith("|") and not l.startswith("|}")]
        if len(cells) < len(cols):
            continue
        row = dict(zip(cols, cells))
        efn = re.search(r"\{\{efn\|([^{}]*)\}\}", row.get("title", ""))
        out.append((year, row, efn.group(1).strip() if efn else ""))
    return out


def wikilink(cell):
    """([[Target|Label]] -> Target, Label); a bare [[X]] gives (X, X)."""
    m = re.search(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]", cell)
    if m:
        return m.group(1), (m.group(2) or m.group(1))
    return None, wiki.clean(cell)


def yes(cell):
    return cell.strip() == "{{yes}}"


def based_on(text):
    """{{Based on|Work|Author…}} -> {"work": …, "by": [...]}.

    wiki.clean() keeps only a template's last argument, which turns
    "American Prometheus by Kai Bird and Martin J. Sherwin" into
    "Martin J. Sherwin" — so the source work of every adaptation on this list
    would be lost. The template's arguments are split here instead."""
    text = re.sub(r"<!--.*?-->", "", text or "", flags=re.S)
    m = re.search(r"\{\{Based on\s*\|(.*?)\}\}\s*$", text.strip(), re.S | re.I)
    if not m:
        # The Odyssey's infobox states its source in plain wikitext rather than
        # through the template.
        w = wiki.clean(text).strip('"')
        return {"work": w, "by": []}
    # Split on top-level pipes only: a [[Target|Label]] argument contains a
    # pipe of its own, and splitting naively cuts every linked work in half.
    body = re.sub(r"\[\[([^\]]*?)\|", lambda mm: "[[" + mm.group(1) + "\x00",
                  m.group(1))
    args = [wiki.clean(a.replace("\x00", "|")).strip('"')
            for a in body.split("|")]
    return {"work": args[0], "by": [a for a in args[1:] if a]}


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    text = wiki.wikitext(PAGE, cache_dir=CACHE)
    assert text, PAGE

    feat = first_table(section(text, "== Feature film ==", "{{notelist}}"))
    shorts_seg = first_table(section(text, "== Short films ==",
                                     "== Documentary appearances =="))
    doc_seg = first_table(section(text, "== Documentary appearances ==",
                                  "== Notes =="))
    ep_seg = first_table(section(text, "'''Executive producer'''",
                                 "== Short films =="))

    feat_rows = rows(feat, FILM_COLS)
    # Short films: Year, Title, Director, Producer, Writer, Cinematographer,
    # Editor, Notes — the Director cell is still column 2.
    short_rows = rows(shorts_seg, ["title", "director", "producer", "writer",
                                   "cinematographer", "editor", "notes"])
    ep_rows = rows(ep_seg, ["title", "notes"])
    doc_rows = rows(doc_seg, ["title"])

    directed = [(y, r, e) for y, r, e in feat_rows if yes(r["director"])]
    not_directed = [(y, wiki.clean(r["title"]), wiki.clean(r["director"]))
                    for y, r, e in feat_rows if not yes(r["director"])]

    films = []
    for year, r, efn in directed:
        page, label = wikilink(r["title"])
        films.append({
            "t": label,
            "page": page or label,
            "year": year,
            "wrote": yes(r["writer"]),
            "produced": yes(r["producer"]),
            "tableefn": wiki.clean(efn),
            "runtime": None,
            "runtime_src": None,
        })
    films.sort(key=lambda f: (f["year"], f["t"]))

    # ---- runtimes: Wikidata P2047, P577 year-gated -----------------------
    qids = wikidata.qids_for([f["page"] for f in films])
    claims = wikidata.claims_for(qids.values())
    for f in films:
        q = qids.get(f["page"])
        c = claims.get(q) if q else None
        f["qid"] = q
        f["pubyears"] = sorted(set(wikidata.pub_years(c))) if c else []
        if c and wikidata.year_gate(c, f["year"]):
            rt = wikidata.runtime(c)
            if rt:
                f["runtime"], f["runtime_src"] = rt, "wikidata"

    # ---- each film's own article: cross-check runtime, and the facts the
    #      list's notes and era intros are allowed to state ----------------
    for f in films:
        t = wiki.wikitext(f["page"], cache_dir=CACHE)
        fb = wiki.infobox(t) if t else None
        f["infobox_runtime"] = None
        f["based_on"] = {"work": "", "by": []}
        f["studio"] = ""
        f["distributor"] = ""
        if not fb:
            continue
        m = re.search(r"(\d+)\s*minutes", wiki.clean(fb("runtime")))
        if m:
            f["infobox_runtime"] = int(m.group(1))
        f["based_on"] = based_on(fb("based_on"))
        f["studio"] = wiki.clean(fb("studio"))
        f["distributor"] = wiki.clean(fb("distributor"))
        # Only the plain, unfootnoted budgets survive; several of the later
        # films' fields are ranges with an explanatory note attached, and a
        # range is not a fact the list is going to print.
        b = wiki.clean(fb("budget"))
        f["budget"] = b if re.fullmatch(r"\$[\d,.]+( million| billion)?", b) else ""
        # {{Film date|YYYY|M|D|where|…}} -> ISO dates. A list that ships a film
        # nobody can watch yet is the failure the David Fincher build avoided
        # by dropping an unreleased title; this is the field that lets the
        # generator check rather than assume.
        fd = re.search(r"\{\{Film date\|(.*?)\}\}", fb("released"), re.S | re.I)
        f["release_dates"] = []
        if fd:
            for y, mo, d in re.findall(r"(\d{4})\|(\d{1,2})\|(\d{1,2})",
                                       fd.group(1)):
                f["release_dates"].append("%s-%02d-%02d"
                                          % (y, int(mo), int(d)))

    # The lead's group=note footnote about a mid-90s feature that was made and
    # scrapped. Read, not typed — the list says why it starts at Following.
    fn = re.search(r"\{\{refn\|group=note\|(.*?)<ref name=\"Mahoney\"", text,
                   re.S)
    scrapped = wiki.clean(fn.group(1)) if fn else ""

    data = {
        "source": PAGE,
        "films": films,
        "feature_table_rows": len(feat_rows),
        "not_directed": not_directed,
        "shorts": [{"year": y, "t": wikilink(r["title"])[1],
                    "directed": yes(r["director"]),
                    "notes": wiki.clean(r["notes"])}
                   for y, r, e in short_rows],
        "exec_producer": [{"year": y, "t": wikilink(r["title"])[1],
                           "notes": wiki.clean(r["notes"])}
                          for y, r, e in ep_rows],
        "documentary_appearances": [{"year": y, "t": wikilink(r["title"])[1]}
                                    for y, r, e in doc_rows],
        "scrapped_feature_note": scrapped,
    }
    out = HERE / "nolan_data.json"
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(data, indent=1, ensure_ascii=False) + "\n")

    print("feature table rows: %d   directed: %d   not directed: %s"
          % (len(feat_rows), len(films), not_directed))
    total = 0
    for f in films:
        total += f["runtime"] or 0
        flag = ""
        if f["infobox_runtime"] and f["infobox_runtime"] != f["runtime"]:
            flag = "   <- infobox says %d" % f["infobox_runtime"]
        print("   %d  %-24s %-11s %3s min (%s)%s"
              % (f["year"], f["t"], f["qid"], f["runtime"], f["runtime_src"],
                 flag))
        print("        based_on=%r budget=%r dist=%r"
              % (f["based_on"], f["budget"], f["distributor"]))
    print("total: %d min = %.2f hours" % (total, total / 60.0))
    print("shorts (%d, directed %d): %s"
          % (len(data["shorts"]), sum(1 for s in data["shorts"] if s["directed"]),
             [(s["year"], s["t"]) for s in data["shorts"]]))
    print("exec producer (%d): %s"
          % (len(data["exec_producer"]),
             [(s["year"], s["t"]) for s in data["exec_producer"]]))
    print("documentary appearances: %d" % len(data["documentary_appearances"]))
    print("scrapped-feature footnote: %r" % scrapped)
    print("wrote %s" % out)


if __name__ == "__main__":
    main()
