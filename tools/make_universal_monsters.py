#!/usr/bin/env python3
"""Generate properties/universal-monsters.json — the classic cycle, 1923-1956.

    python tools/make_universal_monsters.py

All 34 films of the classic era per the filmography table in Wikipedia's
Universal Monsters article, grouped by monster family — the silents, the four
great houses of the '30s and '40s, the wolves, the monster-rally crossovers,
the Abbott & Costello meetings, and the Creature. Weighted by runtime.

The table's one pre-cycle row, the 1913 Dr. Jekyll and Mr. Hyde short, is
excluded — this property covers the 1923-1956 cycle.

Data: tools/data/universal-monsters.json via scratch/agent-canons/collect_um.py.
"""
import json
import pathlib

SLUG = "universal-monsters"
ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = pathlib.Path(__file__).resolve().parent / "data" / ("%s.json" % SLUG)
OUT = ROOT / "properties" / ("%s.json" % SLUG)

FAMILIES = [
    ("silents", "Hunchback & Phantom", "the silents, and the Technicolor "
     "Phantom remake",
     ["The Hunchback of Notre Dame", "The Phantom of the Opera",
      "Phantom of the Opera"]),
    ("dracula", "Dracula", "including the Spanish-language production shot "
     "on the same sets",
     ["Dracula", "Drácula", "Dracula's Daughter", "Son of Dracula"]),
    ("frankenstein", "Frankenstein", "",
     ["Frankenstein", "Bride of Frankenstein", "Son of Frankenstein",
      "The Ghost of Frankenstein"]),
    ("mummy", "The Mummy", "",
     ["The Mummy", "The Mummy's Hand", "The Mummy's Tomb",
      "The Mummy's Ghost", "The Mummy's Curse"]),
    ("invisible", "The Invisible Man", "",
     ["The Invisible Man", "The Invisible Man Returns", "The Invisible Woman",
      "Invisible Agent", "The Invisible Man's Revenge"]),
    ("wolves", "The wolves", "Werewolf of London predates Talbot by six years",
     ["Werewolf of London", "The Wolf Man", "She-Wolf of London"]),
    ("house", "The monster rallies", "the crossovers and house films",
     ["Frankenstein Meets the Wolf Man", "House of Frankenstein",
      "House of Dracula"]),
    ("abbott", "Abbott & Costello meet…", "the cycle winds down laughing",
     ["Abbott and Costello Meet Frankenstein",
      "Abbott and Costello Meet the Invisible Man",
      "Abbott and Costello Meet Dr. Jekyll and Mr. Hyde",
      "Abbott and Costello Meet the Mummy"]),
    ("creature", "The Creature", "the Gill-man trilogy closes the era",
     ["Creature from the Black Lagoon", "Revenge of the Creature",
      "The Creature Walks Among Us"]),
]


def slug(t):
    import unicodedata
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    keep = "".join(c.lower() if c.isalnum() else "-" for c in t)
    while "--" in keep:
        keep = keep.replace("--", "-")
    return keep.strip("-")


def main():
    d = json.loads(DATA.read_text(encoding="utf-8"))
    films = d["films"]
    assert len(films) == 34, len(films)
    assert d["excluded"] and d["excluded"][0]["year"] == 1913

    by_title = {}
    for f in films:
        by_title.setdefault(f["t"], []).append(f)

    used = set()
    sections = []
    for key, title, sub_extra, names in FAMILIES:
        got = []
        for name in names:
            pool = [f for f in by_title.get(name, []) if id(f) not in used]
            assert pool, "no unused film titled %r" % name
            f = min(pool, key=lambda x: x["year"])
            used.add(id(f))
            got.append(f)
        got.sort(key=lambda f: f["date"])
        items = []
        for f in got:
            note = ""
            sl = slug(f["t"])
            if f["t"] == "Drácula":
                note = "The Spanish-language version, shot nights on the " \
                       "same sets"
                sl = "dracula-spanish"  # slug() strips the accent; the 1931
                # English-language film already owns um-1931-dracula
            items.append({
                "id": "um-%d-%s" % (f["year"], sl),
                "t": f["t"], "n": str(f["year"]),
                "w": round((f["runtime"] or 0) / 60.0, 2),
                **({"note": note} if note else {}),
            })
        hours = sum(x["w"] for x in items)
        sub = "%d–%d · %d film%s · %d hours" % (
            got[0]["year"], got[-1]["year"], len(got),
            "" if len(got) == 1 else "s", round(hours))
        sec = {"id": key, "title": title,
               "sub": sub + (" · " + sub_extra if sub_extra else ""),
               "items": items}
        if key == "silents":
            sec["open"] = True
        sections.append(sec)

    assert len(used) == len(films), \
        "unmapped: %s" % [f["t"] for f in films if id(f) not in used]
    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), \
        "duplicate ids: %s" % sorted({i for i in ids if ids.count(i) > 1})[:6]
    norun = [f["t"] for f in films if not f["runtime"]]
    hours = sum(x["w"] for s in sections for x in s["items"])

    prop = {
        "slug": SLUG,
        "title": "Universal Monsters",
        "subtitle": "the classic cycle, by monster",
        "kind": "films",
        "popularity": 56,
        "year": "1923–1956",
        "blurb": "All 34 films of the classic cycle, grouped by monster — "
                 "about %d hours from the Hunchback to the last Creature."
                 % round(hours),
        "unit": {"one": "film", "many": "films"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "accent": "#4A6357",
        "accentDark": "#8FB09E",
        "tiers": False,
        "random": True,
        "notes": [
            ["Grouped by monster, not by date.",
             "Each family runs in release order inside its section, so you "
             "can take one lineage at a time; the crossovers and the Abbott "
             "& Costello films sit apart, where the timelines tangle."],
            ["Bar widths are runtimes." if not norun else
             "Bar widths are runtimes.",
             "From Wikidata (duration, P2047)." if not norun else
             "From Wikidata (duration, P2047); %s have none on record and "
             "weigh nothing." % ", ".join(norun)],
            ["One row older than the cycle is left out.",
             "Wikipedia's classic-era table opens with a 1913 Dr. Jekyll and "
             "Mr. Hyde short from the studio's earliest days; it predates "
             "the 1923–1956 cycle this list covers."],
            "Filmography from Wikipedia's Universal Monsters article; "
            "runtimes from Wikidata.",
        ],
        "sections": sections,
    }

    with OUT.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")
    print("wrote %s.json — %d films, %d hours" % (SLUG, len(ids), round(hours)))
    for s in sections:
        print("   %-26s %2d  %s" % (s["title"], len(s["items"]), s["sub"][:46]))


if __name__ == "__main__":
    main()
