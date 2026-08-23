#!/usr/bin/env python3
"""Generate properties/doctor-who.json — the whole programme, 1963-2025.

    python3 tools/make_doctor-who.py

One row per watchable unit: the classic era (1963-1989) gets one row per
SERIAL — 155 stories in 26 season sections, each row noting its episode
count, 695 episodes in all — then the 1996 TV movie, then the revival
(2005-2025) one row per episode, sectioned the way the episode list article
sections itself: 15 series plus four standalone specials blocks, 196 episodes.
355 rows in all.

Rows carry the story number from Wikipedia's episode lists (which follow the
official episode guide): classic serials 1-155, the movie 156, revival
episodes 157-319 with two-part stories split a/b as the list splits them.
Season 23 is the one exception to one-row-per-story: The Trial of a Time Lord
is a single 14-episode story its season article files as four titled
segments, 143a-143d, and the four rows follow it.

The ten serials the BBC archive holds nothing of are marked optional, with a
"missing from the archive" note. Shada — abandoned mid-production, never
broadcast, story number "108.5" in the source — is excluded.

Everything is machine-read by scratch/agent-tv1/extract_dw.py from the 26
classic season articles, the 19 revival series/specials articles, and the
missing-episodes register, asserted against the lists' own Series overview
counts and {{DW episode count}} (892 episodes / 319 stories); the committed
result is tools/data/doctor-who-episodes.json.
"""
import json
import pathlib

SLUG = "doctor-who"


def short_years(y):
    """1963–1964 -> 1963–64; 1999–2000 stays; 1970 stays."""
    a, dash, b = y.partition("–")
    if b and a[:2] == b[:2]:
        b = b[2:]
    return a + (dash + b if b else "")


def main():
    data = json.loads((pathlib.Path(__file__).resolve().parent / "data"
                       / "doctor-who-episodes.json").read_text(encoding="utf-8"))
    missing = set(data["wholly_missing"])

    sections = []

    # ---- classic era: one section per season, one row per serial ----------
    for c in data["classic"]:
        n = c["season"]
        items = []
        for i, s in enumerate(c["serials"], 1):
            eps = "%d episode%s" % (s["parts"], "" if s["parts"] == 1 else "s")
            row = {"id": "dw-s%d-%d" % (n, i), "t": s["title"],
                   "n": "%d%s" % (s["story"], s["suffix"])}
            if s["story"] in missing:
                row["opt"] = True
                row["note"] = (eps + " · " +
                               ("missing from the archive" if s["parts"] == 1
                                else "all missing from the archive"))
            elif s["story"] == 129:
                row["note"] = eps + " · 20th-anniversary special"
            else:
                row["note"] = eps
            items.append(row)
        sec = {"id": "s%d" % n, "title": "Season %d" % n,
               "sub": "%s · %d serials · %d episodes"
                      % (short_years(c["years"]), len(c["serials"]), c["episodes"]),
               "items": items}
        if n == 1:
            sec["open"] = True
        if n == 23:
            sec["sub"] = ("%s · one 14-episode story in four segments"
                          % short_years(c["years"]))
        sections.append(sec)

    # ---- the TV movie ------------------------------------------------------
    f = data["film"]
    sections.append({
        "id": "tvm", "title": "The TV Movie",
        "sub": "1996 · one television film, between the eras",
        "items": [{"id": "dw-tvm", "t": f["title"], "n": str(f["story"]),
                   "note": "Television film"}],
    })

    # ---- revival: the list article's own sections, in its order -----------
    spno = 0
    for r in data["revival"]:
        if r["heading"].startswith("Series"):
            snum = int(r["heading"].split()[1])
            secid, title = "n%d" % snum, r["heading"]
            prefix = "dw-n%d" % snum
        else:
            spno += 1
            yr = short_years(r["years"])
            a, _, b = r["years"].partition("–")
            secid = "sp" + (a[2:] + b[2:] if b else a)   # sp0810, sp2013
            title = "Specials (%s)" % yr
            prefix = "dw-" + secid
        items = []
        for i, e in enumerate(r["episodes"], 1):
            row = {"id": "%s-%d" % (prefix, i), "t": e["title"], "n": e["story"]}
            if "special" in e:
                row["note"] = e["special"] + " special"
            items.append(row)
        k = r["specials_in_table"]
        if r["regular"]:
            sub = "%s · %d episodes" % (short_years(r["years"]), r["regular"])
            if k:
                sub += " + %d special%s" % (k, "" if k == 1 else "s")
        else:
            sub = "%d specials" % k
        if r["heading"] == "Series 13":
            sub += " · one six-chapter story, Flux"
        if r["heading"] == "Series 14":
            sub += " · aired as Season 1"
        if r["heading"] == "Series 15":
            sub += " · aired as Season 2"
        sections.append({"id": secid, "title": title, "sub": sub, "items": items})

    # ---- asserts -----------------------------------------------------------
    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert len(ids) == 355, len(ids)
    import re
    classic_rows = [x for s in sections if re.fullmatch(r"s\d+", s["id"])
                    for x in s["items"]]
    assert len(classic_rows) == 158, len(classic_rows)
    assert sum(1 for x in classic_rows if x.get("opt")) == 10
    revival_rows = [x for s in sections
                    if s["id"].startswith(("n", "sp")) for x in s["items"]]
    assert len(revival_rows) == 196, len(revival_rows)
    assert sum(c["episodes"] for c in data["classic"]) == 695
    assert len(sections) == 26 + 1 + 19, len(sections)
    secids = [s["id"] for s in sections]
    assert len(secids) == len(set(secids))
    assert [e["title"] for e in data["excluded"]] == ["Shada"]

    prop = {
        "slug": SLUG,
        "title": "Doctor Who",
        "subtitle": "every televised story, 1963–2025",
        "kind": "tv",
        "order": 73,
        "year": "1963–2025",
        "blurb": "All of it, in broadcast order — 26 seasons of classic "
                 "serials, the TV movie, and 15 revival series: 355 entries "
                 "covering 892 episodes.",
        "unit": {"one": "entry", "many": "entries"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "accent": "#003B6F",
        "accentDark": "#6FA8DC",
        "tiers": False,
        "notes": [
            ["Serials are the unit for the classic era.", "One row per serial "
             "for 1963–1989 — 155 stories holding 695 episodes, each "
             "row's note carrying its episode count. The revival is one row "
             "per episode, 196 of them."],
            ["Ten serials are wholly missing.", "The BBC archive is missing 95 "
             "classic-era episodes, and for ten serials nothing survives on "
             "film — those rows are marked optional. Full audio survives "
             "for all of them."],
            ["Season 23 is one story.", "The Trial of a Time Lord is a single "
             "14-episode story; its four titled segments are listed the way "
             "its season article files them, as 143a–143d."],
            ["Shada is not here.", "Abandoned mid-production in 1979 and never "
             "broadcast, it is skipped by the official story numbering and by "
             "this list."],
            ["The numbers are story numbers.", "Each row carries the story "
             "number from Wikipedia's episode lists, which follow the official "
             "episode guide; revival two-part stories are one row per episode, "
             "numbered like 172a and 172b."],
            "Machine-read from Wikipedia's 26 classic season articles, the 19 "
            "revival series and specials articles, and the missing-episodes "
            "register; every season's serial and episode counts are asserted "
            "against the episode lists' own totals — 892 episodes, 319 "
            "stories — before this builds.",
        ],
        "sections": sections,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    with out.open("w", encoding="utf-8", newline="\n") as f_:
        f_.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json — %d rows (%d classic serials + movie + %d revival)"
          % (SLUG, len(ids), len(classic_rows), len(revival_rows)))
    for s in sections:
        print("   %-22s %3d  %s" % (s["title"], len(s["items"]), s.get("sub", "")[:44]))


if __name__ == "__main__":
    main()
