#!/usr/bin/env python3
"""Generate properties/disney.json.

    python3 tools/make_disney.py

Every Disney film in release order — theatrical, television and direct-to-video
— with the acquired properties left out: no Star Wars, no Marvel, no Pixar, no
20th Century, no Muppets. Walt Disney Pictures, Disney Channel and Disneytoon
are the studio's own output, and that is what "a Disney movie" means here.

Sources, machine-read by scratch/disney/parse.py:
  - List of Walt Disney Pictures films          theatrical
  - List of Disney Channel original films       television
  - List of Disneytoon Studios productions      direct-to-video
with runtimes from Wikidata (P2047). Where the same film appears on two lists,
Disneytoon's word wins on how it was released — the Walt Disney Pictures list
files Bambi II as theatrical because it had a cinema release outside North
America, and the studio that made it is the better authority.

Tiers are release channels, not rankings:
  1 theatrical   2 television   3 direct-to-video
A finish date paces you through the theatrical line; the checkbox adds the
rest. The channels are also filter chips, so "no TV movies" is one click.
"""
import json
import pathlib

SLUG = "disney"

KIND = {
    "theatrical": (1, "Theatrical", []),
    "television": (2, "Television", ["TV movie"]),
    "direct-to-video": (3, "Direct-to-video", ["Direct-to-video"]),
}

ERAS = [
    ("walt", "Walt's era", 0, 1966,
     "Snow White to The Jungle Book — the films made while Walt Disney was "
     "alive, which is the canon the studio still measures itself against."),
    ("after", "After Walt", 1967, 1988,
     "The studio wobbles for twenty years: live-action comedies, the scruffy "
     "seventies animation, and the beginnings of the Disney Channel."),
    ("renaissance", "The Renaissance", 1989, 1999,
     "The Little Mermaid through Tarzan, and alongside it the first wave of "
     "direct-to-video sequels and Disney Channel movies."),
    ("aughts", "The two thousands", 2000, 2009,
     "The sequel factory at full tilt, the DCOM golden age, and the slow slide "
     "of hand-drawn animation."),
    ("revival", "The Revival", 2010, 2019,
     "Tangled, Frozen, Moana — and the live-action remakes begin."),
    ("plus", "The Disney+ era", 2020, 9999,
     "Streaming first, cinemas second, and the remakes keep coming."),
]


def slug(t):
    keep = "".join(c.lower() if c.isalnum() else "-" for c in t)
    while "--" in keep:
        keep = keep.replace("--", "-")
    return keep.strip("-")


def era_of(year):
    for key, _, lo, hi, _ in ERAS:
        if lo <= year <= hi:
            return key
    return "plus"


def main():
    data = pathlib.Path(__file__).resolve().parent / "data" / "disney.json"
    films = json.loads(data.read_text(encoding="utf-8"))
    films.sort(key=lambda f: (f["date"], f["t"]))

    sections = []
    for key, title, lo, hi, intro in ERAS:
        got = [f for f in films if lo <= int(f["date"][:4]) <= hi]
        if not got:
            continue
        items = []
        for f in got:
            tier, label, tags = KIND[f["kind"]]
            bits = list(tags)
            if not f.get("runtime") and int(f["date"][:4]) > 2025:
                bits.append("Not out yet")
            items.append({
                "id": "dis-%s-%s" % (f["date"][:4], slug(f["t"])),
                "t": f["t"], "n": f["date"][:4],
                "w": round((f.get("runtime") or 0) / 60.0, 2),
                "tier": tier,
                "tags": [label],
                **({"note": " · ".join(bits)} if bits else {}),
            })
        counts = {}
        for f in got:
            counts[f["kind"]] = counts.get(f["kind"], 0) + 1
        parts = ["%d theatrical" % counts.get("theatrical", 0),
                 "%d TV" % counts["television"] if counts.get("television") else "",
                 "%d direct-to-video" % counts["direct-to-video"]
                 if counts.get("direct-to-video") else ""]
        sec = {"id": key, "title": title,
               "sub": "%d–%d · %s · %d hours"
                      % (int(got[0]["date"][:4]), int(got[-1]["date"][:4]),
                         ", ".join(p for p in parts if p),
                         round(sum(f.get("runtime") or 0 for f in got) / 60.0)),
               "intro": intro, "items": items}
        if key == "walt":
            sec["open"] = True
        assert all(a["n"] <= b["n"] for a, b in zip(sec["items"], sec["items"][1:])), \
            "%s out of order" % title
        sections.append(sec)

    ids = [x["id"] for s in sections for x in s["items"]]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    assert not dupes, "duplicate ids: %s" % dupes[:6]
    assert len(ids) == len(films), (len(ids), len(films))

    n = {}
    for f in films:
        n[f["kind"]] = n.get(f["kind"], 0) + 1
    hours = sum(f.get("runtime") or 0 for f in films) / 60.0
    nort = sum(1 for f in films if not f.get("runtime"))

    prop = {
        "slug": SLUG,
        "title": "Disney",
        "subtitle": "the studio's own films, in release order",
        "kind": "films",
        "order": 23,
        "year": "1937–",
        "blurb": "%d films from Snow White on — %d theatrical, %d television, "
                 "%d direct-to-video — about %d hours."
                 % (len(films), n["theatrical"], n["television"],
                    n["direct-to-video"], round(hours)),
        "unit": {"one": "film", "many": "films"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": "#1F4FA8",
        "accentDark": "#6F9BE8",
        "tiers": True,
        "random": True,
        "itemTiers": True,
        "paceTiers": [1],
        "paceLabel": "the TV movies and direct-to-video sequels",
        "filter": {
            "key": "channel", "label": "Show", "mode": "exclude",
            "values": ["Theatrical", "Television", "Direct-to-video"],
        },
        "notes": [
            ["Tiers are release channels, not rankings.", "1 is theatrical, 2 is "
             "television, 3 is direct-to-video. A finish date paces you through "
             "the theatrical line — %d films — and the checkbox under the bar "
             "adds the other two. The chips at the top hide a channel entirely."
             % n["theatrical"]],
            ["No acquired properties.", "No Star Wars, no Marvel, no Pixar, no "
             "20th Century, no Muppets. Those are their own lists or their own "
             "studios; this is what Disney itself made — Walt Disney Pictures, "
             "Disney Channel and Disneytoon."],
            ["Where a film sits on two lists, the studio that made it wins.",
             "Several direct-to-video sequels had cinema releases outside North "
             "America and appear on the theatrical list because of it. Bambi II "
             "and Tarzan II are direct-to-video here because Disneytoon says so, "
             "and it made them."],
            ["Bar widths are runtimes.", "From Wikidata, for %d of the %d. The "
             "%d without one — mostly sixties and seventies live-action — weigh "
             "nothing rather than a guess." % (len(films) - nort, len(films), nort)],
            "Film lists from Wikipedia: Walt Disney Pictures films, Disney "
            "Channel original films, and Disneytoon Studios productions.",
        ],
        "sections": sections,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json" % SLUG)
    print("  %d sections, %d films, %d hours" % (len(sections), len(ids), round(hours)))
    for s in sections:
        print("   %-20s %4d  %s" % (s["title"], len(s["items"]), s["sub"][:56]))


if __name__ == "__main__":
    main()
