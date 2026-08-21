#!/usr/bin/env python3
"""Generate properties/star-wars.json.

    python3 tools/make_starwars.py

Every Star Wars film and television season, in the order they came out. The
games are their own property — see tools/make_starwars_games.py.

Sources, machine-read rather than typed:
  - the title sets come from the section headings of Wikipedia's "List of Star
    Wars films" and "List of Star Wars television series", which are prose
    articles rather than tables
  - film release dates and runtimes from Wikidata (P577, P2047)
  - season counts and episode totals from each show's own infobox, not from
    Wikidata: P1113 sometimes records a season's count against the series item,
    which gave The Bad Batch 18 episodes for a run of 47
  - the games from Wikipedia's "List of Star Wars video games"

Young Jedi Adventures is left out: it is a Disney Junior preschool show rather
than something an audience works through. Droids and Ewoks stay — Saturday
morning cartoons aimed at children are a different thing, and they were the
only Star Wars television that existed for twenty years.

Weights are runtimes throughout.
"""
import json
import pathlib

SLUG = "star-wars"

# minutes per episode by kind — the two are far enough apart that one number
# for both would misstate every animated season in the list
EP_MINUTES = {"animated": 22, "live": 42}

ERAS = [
    ("original", "The original trilogy", 0, 1986,
     "Three films, two Ewok adventures, a variety special nobody involved will "
     "discuss, and the two Saturday-morning cartoons that followed."),
    ("prequels", "The prequels", 1987, 2007,
     "Sixteen years later, and a different kind of film — political, digital, "
     "and building the war the cartoons would spend a decade fighting."),
    ("clonewars", "The Clone Wars era", 2008, 2014,
     "One film and one series that outgrew it. This is where the animation "
     "became the main event rather than a spin-off."),
    ("disney", "Disney: the sequels and the anthologies", 2015, 2018,
     "A trilogy and two standalone films, made to a schedule that turned out "
     "to be faster than the story could take."),
    ("plus", "The Disney+ era", 2019, 9999,
     "Television becomes the centre of gravity, and the films slow to a stop."),
]


# Tier 1 is the spine: the nine numbered films, the story everything else is
# arranged around. Tier 2 is the rest of the main line — the other theatrical
# films and the series that carry real plot. Tier 3 is everything you can enjoy
# without it changing what tier 1 means: the variety special, the Ewok films,
# the eighties cartoons, the anthologies, and the games.
SAGA = {
    "Star Wars", "The Empire Strikes Back", "Return of the Jedi",
    "The Phantom Menace", "Attack of the Clones", "Revenge of the Sith",
    "The Force Awakens", "The Last Jedi", "The Rise of Skywalker",
    # not numbered, but it runs straight into the opening of the first film
    # and Andor runs straight into it
    "Rogue One",
}
MAIN_SHOWS = {
    "The Clone Wars", "Rebels", "The Bad Batch", "The Mandalorian",
    "The Book of Boba Fett", "Obi-Wan Kenobi", "Ahsoka",
    "The Acolyte", "Skeleton Crew", "Resistance",
}
# The one series held to the same standard as the films.
SAGA_SHOWS = {"Andor"}

# Made for preschoolers rather than for an audience working through Star Wars.
# Droids and Ewoks are not in here: Saturday morning cartoons aimed at children
# are a different thing, and they were the only Star Wars television that
# existed for twenty years.
FOR_PRESCHOOL = {"Young Jedi Adventures"}


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


def spread(start_year, end_year, n, k):
    """Season k of n, placed between the years the show ran."""
    if n == 1 or end_year is None or end_year <= start_year:
        return start_year
    return start_year + round((k - 1) * (end_year - start_year) / (n - 1))


def main():
    data = pathlib.Path(__file__).resolve().parent / "data" / "starwars.json"
    d = json.loads(data.read_text(encoding="utf-8"))

    entries = []

    for f in d["films"]:
        year = int(f["released"][:4])
        bits = []
        if f["kind"] == "tv":
            bits.append("Made for television")
        if not f["runtime"]:
            bits.append("Not out yet")
        entries.append({
            "id": "sw-f-%d-%s" % (year, slug(f["t"])),
            "t": f["t"], "n": str(year),
            "w": round((f["runtime"] or 0) / 60.0, 2),
            "note": " · ".join(bits), "date": f["released"],
            "year": year, "kind": "film",
            "tier": 1 if f["t"] in SAGA else (3 if f["kind"] == "tv" else 2),
            "tags": ["Films"],
        })

    for s in d["shows"]:
        if s["t"] in FOR_PRESCHOOL:
            continue
        start = int(s["start"][:4])
        end = int(s["end"][:4]) if s["end"] else None
        n, eps = s["seasons"], s["episodes"]
        dates = s.get("season_dates") or {}
        per_eps = s.get("season_eps") or {}
        # an even split is the fallback, not the plan: where a season's own
        # episode count is known it is used, and only the remainder is shared out
        known = sum(per_eps.get(str(k), 0) for k in range(1, n + 1))
        rest = [k for k in range(1, n + 1) if str(k) not in per_eps]
        spare = max(0, eps - known) / len(rest) if rest else 0
        for k in range(1, n + 1):
            iso = dates.get(str(k))
            sy = int(iso[:4]) if iso else spread(start, end, n, k)
            mine = per_eps.get(str(k), spare)
            bits = []
            if k == 1:
                span = s["start"][:4] + ("–" + s["end"][:4] if s["end"] else "–")
                bits.append("%s · %d season%s, %d episodes"
                            % (span, n, "" if n == 1 else "s", eps))
                bits.append("Animated" if s["kind"] == "animated" else "Live action")
            if mine and n > 1:
                bits.append("%d episode%s" % (round(mine), "" if round(mine) == 1 else "s"))
            entries.append({
                "id": "sw-t-%d-%s-s%d" % (start, slug(s["t"]), k),
                "t": "%s season %d" % (s["t"], k) if n > 1 else s["t"],
                "n": str(sy),
                "w": round(mine * EP_MINUTES[s["kind"]] / 60.0, 2),
                "note": " · ".join(bits),
                # a season with a real premiere sorts on it; The Clone Wars film
                # came out in August 2008 and the series that October
                "date": iso or ("%d-06-15" % sy),
                "year": sy, "kind": "show", "sortkey": (s["t"], k),
                "tier": 1 if s["t"] in SAGA_SHOWS
                        else (2 if s["t"] in MAIN_SHOWS else 3),
                "tags": ["Television"],
            })

    entries.sort(key=lambda e: (e["date"], {"film": 0, "show": 1}[e["kind"]],
                                e.get("sortkey", (e["t"], 0))))

    sections = []
    for key, title, lo, hi, intro in ERAS:
        got = [e for e in entries if era_of(e["year"]) == key]
        if not got:
            continue
        nf = sum(1 for e in got if e["kind"] == "film")
        ns = sum(1 for e in got if e["kind"] == "show")
        parts = ["%d film%s" % (nf, "" if nf == 1 else "s") if nf else "",
                 "%d season%s" % (ns, "" if ns == 1 else "s") if ns else "",
                 ]
        sec = {"id": key, "title": title,
               "sub": "%d–%d · %s · %d hours"
                      % (got[0]["year"], got[-1]["year"],
                         ", ".join(p for p in parts if p),
                         round(sum(e["w"] for e in got))),
               "intro": intro,
               "items": [{k: v for k, v in e.items()
                          if k in ("id", "t", "n", "w", "tier", "tags")
                          or (k == "note" and v)}
                         for e in got]}
        if key == "original":
            sec["open"] = True
        assert all(a["n"] <= b["n"] for a, b in zip(sec["items"], sec["items"][1:])), \
            "%s is out of year order" % title
        sections.append(sec)

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), \
        "duplicate ids: %s" % sorted({i for i in ids if ids.count(i) > 1})[:5]
    assert len(ids) == len(entries), (len(ids), len(entries))

    hours = sum(e["w"] for e in entries)
    nf = sum(1 for e in entries if e["kind"] == "film")
    ns = sum(1 for e in entries if e["kind"] == "show")

    prop = {
        "slug": SLUG,
        "title": "Star Wars",
        "subtitle": "every film and television season, in release order",
        "kind": "films & shows",
        "order": 21,
        "year": "1977–",
        "blurb": "%d films and %d television seasons in the order they came out "
                 "— about %d hours." % (nf, ns, round(hours)),
        "unit": {"one": "entry", "many": "entries"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": "#8A6D1F",
        "accentDark": "#E8C450",
        "tiers": True,
        "itemTiers": True,
        "filter": {
            "key": "kind", "label": "Show", "mode": "exclude",
            "values": ["Films", "Television"]
        },
        "paceTiers": [1, 2],
        "paceLabel": "the specials and the anthologies",
        "notes": [
            ["Tiers are on each row, not each section.",
             "These sections are eras, and an era holds all three at once. "
             "1 is the spine — the nine numbered films, plus Rogue One and "
             "Andor, which run into the opening of the first film and into "
             "each other. 2 is the rest of the main line: the "
             "other theatrical films and the series carrying real plot. 3 is "
             "everything you can take or leave without changing what 1 means — "
             "the Holiday Special, the Ewok films, the eighties cartoons and "
             "the anthologies. A finish date covers 1 and 2; the checkbox "
             "under the bar adds the rest."],
            ["Release order, not chronological.", "This is the order it came out, "
             "which is the order it was written to be met in. Every in-universe "
             "ordering spoils the one reveal the films are built around."],
            ["Television is tracked season by season.", "A season's length is the "
             "series' episode count split evenly across its seasons, at %d minutes "
             "an episode for animation and %d for live action — one number for both "
             "would misstate every animated season here. Seasons are spread across "
             "the years the show ran rather than parked at its first, so The Clone "
             "Wars sits across the decade it actually occupied."
             % (EP_MINUTES["animated"], EP_MINUTES["live"])],
            ["Turning parts of it off.",
             "The chips at the top drop a whole category, so “just the films” "
             "is one click rather than a decision about every row. It hides "
             "rows and redraws the bar to match; it never unticks anything."],
            ["What is not here.", "The games, which are their own page — "
             "sixty-eight of them buried whatever they sat beside, and they are a "
             "parallel thing rather than a step in the same sequence. Star Wars "
             "Games is in the switcher, with its own Legends and canon filters. "
             "And Young Jedi Adventures, "
             "which is a Disney Junior preschool show rather than something anyone "
             "else is working through. Droids and Ewoks stay: they are Saturday "
             "morning cartoons for children, which is not the same thing, and they "
             "are the only Star Wars television there was for twenty years."],
            "Film runtimes and dates from Wikidata; season and episode counts from "
            "each show's own infobox; the games from Wikipedia's list of Star Wars "
            "video games.",
        ],
        "sections": sections,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json" % SLUG)
    print("  %d sections, %d entries (%d films, %d seasons), %d hours"
          % (len(sections), len(ids), nf, ns, round(hours)))
    for s in sections:
        print("   %-38s %3d  %s" % (s["title"][:38], len(s["items"]), s["sub"][:48]))


if __name__ == "__main__":
    main()
