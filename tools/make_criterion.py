#!/usr/bin/env python3
"""Generate properties/criterion.json — the Criterion Collection by spine number.

    python3 tools/make_criterion.py

Every spine-numbered Criterion release, 1 to 1337, in order, with the formats
Criterion has put each one out on.

Sources, machine-read rather than typed:
  - criterion.com/shop/browse/list, which renders the whole catalogue server
    side in one table, plus each film's own page for its editions and runtime.
    This is where DVD, Blu-ray and 4K come from — an edition is recorded
    whether it is sold on its own or only inside a box set.
  - Wikipedia's List of films in the Criterion Collection, the only source for
    LaserDisc: Criterion stopped selling them in 1998 and no longer lists them.

Criterion restarted its numbering at 1 when it moved from LaserDisc to DVD, so
a LaserDisc-only release can share a number with a completely unrelated DVD.
Rather than interleave two numbering systems, the LaserDisc-only releases sit
in their own section, keyed by their own spine numbers, and are scoped out of
the finish date — they have been out of print since the nineties.

There are no tiers on the rows. Criterion does not rank its own collection and
neither does this; the only thing tier does here is carry that pace scope, via
the LaserDisc section, since computePace() reads a section's tier rather than
an item's.

Spine 88 is the only number covering two films, Ivan the Terrible Parts I and
II, and is the one place the list shows two entries under one number.
"""
import json
import pathlib

SLUG = "criterion"

BAND = 100  # one section per hundred spines


def slug(t):
    keep = "".join(c.lower() if c.isalnum() else "-" for c in t)
    while "--" in keep:
        keep = keep.replace("--", "-")
    return keep.strip("-")


def note_for(r):
    # the country field arrives with a trailing space from the source, which
    # doubled up around the separators on every note — strip each bit
    bits = [b.strip() for b in (r.get("director"), r.get("country"),
                                str(r["year"]) if r.get("year") else None)
            if b and str(b).strip()]
    # An empty list means the read failed, not that Criterion never pressed it.
    # Say so rather than leave a gap that looks like a finished answer.
    bits.append(", ".join(r["formats"]) if r["formats"] else "formats unconfirmed")
    if r.get("ld_spine"):
        bits.append("LaserDisc as #%d" % r["ld_spine"])
    return " · ".join(bits)


def band_title(lo, hi):
    return "#%d–%d" % (lo, hi)


def main():
    data = pathlib.Path(__file__).resolve().parent / "data" / "criterion.json"
    d = json.loads(data.read_text(encoding="utf-8"))
    spined, laser = d["spined"], d["laserdisc"]

    assert spined, "no spine-numbered releases"
    assert all(r["spine"] for r in spined), "a release with no spine number"
    spined.sort(key=lambda r: (r["spine"], r["t"]))
    top = spined[-1]["spine"]

    sections = []
    for lo in range(1, top + 1, BAND):
        hi = min(lo + BAND - 1, top)
        got = [r for r in spined if lo <= r["spine"] <= hi]
        if not got:
            continue
        mins = sum(r["runtime"] or 0 for r in got)
        items = [{
            "id": "crit-%d-%s" % (r["spine"], slug(r["t"])),
            "t": r["t"], "n": "#%d" % r["spine"],
            "w": round((r["runtime"] or 0) / 60.0, 2),
            **({"tags": r["formats"]} if r["formats"] else {}),
            **({"note": note_for(r)} if note_for(r) else {}),
        } for r in got]
        sec = {"id": "s%d" % lo, "title": band_title(lo, hi),
               "sub": "%d film%s · %d hours" % (len(got), "" if len(got) == 1 else "s",
                                                round(mins / 60.0)),
               "items": items}
        if lo == 1:
            sec["open"] = True
        sections.append(sec)

    laser.sort(key=lambda r: (r["spine"], r["t"]))
    sections.append({
        "id": "laserdisc", "tier": 2, "title": "LaserDisc only",
        "sub": "%d releases · a separate numbering, out of print since the "
               "nineties" % len(laser),
        "intro": "Criterion's LaserDisc line ran from 1984 to 1998 and had its "
                 "own spine numbers, which were reset when the DVD line began. "
                 "These are the releases that never made the jump, so their "
                 "numbers overlap unrelated films above. Nothing here is "
                 "purchasable; a finish date skips them unless you tick the box "
                 "under the bar.",
        "items": [{
            "id": "crit-ld-%d-%s" % (r["spine"], slug(r["t"])),
            "t": r["t"], "n": "LD #%d" % r["spine"], "w": 0, "tags": ["LaserDisc"],
            **({"note": note_for(r)} if note_for(r) else {}),
        } for r in laser],
    })

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), \
        "duplicate ids: %s" % sorted({i for i in ids if ids.count(i) > 1})[:6]
    assert len(ids) == len(spined) + len(laser), (len(ids), len(spined), len(laser))
    for s in sections[:-1]:
        nums = [int(x["n"][1:]) for x in s["items"]]
        assert nums == sorted(nums), "%s is out of spine order" % s["title"]

    hours = sum(r["runtime"] or 0 for r in spined) / 60.0
    by_fmt = {}
    for r in spined:
        for f in r["formats"]:
            by_fmt[f] = by_fmt.get(f, 0) + 1
    for r in laser:
        by_fmt["LaserDisc"] = by_fmt.get("LaserDisc", 0) + 1
    noruntime = sum(1 for r in spined if not r["runtime"])

    prop = {
        "slug": SLUG,
        "title": "The Criterion Collection",
        "subtitle": "every spine number, in order",
        "kind": "films",
        "order": 20,
        "year": "1984–",
        "blurb": "Spines #1 to #%d — %d releases, about %d hours, each with the "
                 "formats Criterion put it out on." % (top, len(spined), round(hours)),
        "unit": {"one": "film", "many": "films"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": "#8A6D2F",
        "accentDark": "#D6B36A",
        "tiers": False,
        "random": True,
        "filter": {
            "key": "format", "label": "Format",
            "values": ["4K", "Blu-ray", "DVD", "LaserDisc"]
        },
        "paceTiers": [1],
        "paceLabel": "the LaserDisc-only releases",
        "notes": [
            ["Sorted by spine number, because that is the collection.",
             "Criterion numbers every release, and the number is how the "
             "collection is referred to. The numbering restarted at 1 when the "
             "line moved from LaserDisc to DVD in 1998, so these are the "
             "DVD-era numbers — #1 is Grand Illusion, #%d is %s."
             % (top, spined[-1]["t"])],
            ["Formats are what Criterion lists now, plus LaserDisc.",
             "DVD, Blu-ray and 4K are read off each film's own Criterion page, "
             "and count an edition whether it is sold on its own or only inside "
             "a box set. The catch is that Criterion delists an edition once it "
             "goes out of print: #1 Grand Illusion had a Blu-ray in 2012 and its "
             "page no longer mentions it, so it shows here as LaserDisc and DVD. "
             "Read these as what you can still get hold of rather than as a "
             "complete pressing history. LaserDisc is the exception — it comes "
             "from Wikipedia, which is the only place that history survives. "
             "Counts across the collection: %s."
             % ", ".join("%s %d" % (k, v) for k, v in
                         sorted(by_fmt.items(), key=lambda kv: -kv[1]))],
            ["LaserDisc-only releases are their own section.",
             "%d films Criterion put out on LaserDisc and never reissued. They "
             "carry the old numbering, which collides with the DVD numbering "
             "above, so mixing them into one sequence would produce two #2s and "
             "two #4s. They sit outside a finish date unless you tick the box "
             "under the bar."
             % len(laser)],
            ["Spine #88 is two films.", "Ivan the Terrible, Part I and Part II "
             "share one number. Every other spine in the list is one entry."],
            ["Bar widths are runtimes.", "Read from each film's own Criterion "
             "page. %s" % ("Every one of them has a real runtime." if not noruntime
                           else "%d of the %d have no runtime listed and weigh "
                                "nothing, so they cannot drag a group's pace."
                                % (noruntime, len(spined)))],
            "Catalogue, editions and runtimes from criterion.com; LaserDisc "
            "history from Wikipedia's List of films in the Criterion Collection.",
        ],
        "sections": sections,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json" % SLUG)
    print("  %d sections, %d entries (%d spined + %d LaserDisc), %d hours"
          % (len(sections), len(ids), len(spined), len(laser), round(hours)))
    print("  formats: %s" % ", ".join("%s %d" % kv for kv in sorted(by_fmt.items())))
    for s in sections:
        print("   %-16s %4d  %s" % (s["title"], len(s["items"]), s["sub"][:46]))


if __name__ == "__main__":
    main()
