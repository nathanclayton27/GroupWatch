#!/usr/bin/env python3
"""Generate properties/columbo.json — every Columbo, pilots to Nightlife.

    python3 tools/make_columbo.py

All 69 feature-length episodes in broadcast order, grouped as Wikipedia's
"List of Columbo episodes" groups them (the UK DVD arrangement): the two
pilots, seasons 1-7 on NBC, the two ABC Mystery Movie seasons, and the final
fourteen sporadic specials (1990-2003) filed as season 10.

Weights are real runtimes: every row of every season table carries a Runtime
column ("NN min"), machine-read by scratch/columbo/parse.py from the list
article and the ten season articles it transcludes, into
tools/data/columbo.json. No row uses a slot-length convention.

Each row names its murderer's actor because the source tables do — their
"Murderer played by" column leads every season table. Columbo is an inverted
mystery; the killer is shown before the detective appears, so the guest star
is the hook, not a spoiler.

IDs are columbo-<overall broadcast number> (1-69, pilots included) — the
numbering the source uses, continuous across eras, asserted continuous here.
The total is asserted against the list article's own {{Series overview}}
counts, which parse.py stores alongside the rows.
"""
import json
import pathlib

SLUG = "columbo"


def years(info):
    y1, y2 = int(info["start"][:4]), int(info["end"][:4])
    if y1 == y2:
        return "%d" % y1
    if y1 // 100 == y2 // 100:
        return "%d–%02d" % (y1, y2 % 100)
    return "%d–%d" % (y1, y2)


def note_for(x, with_year=False):
    m = x["murderer"]
    if m.startswith("(") and m.endswith(")"):
        note = m[1:-1].strip()          # "No Time to Die" has no murderer
    else:
        note = "Murderer: " + m
    if with_year:
        note = "%s · %s" % (x["air"][:4], note)
    return note


def main():
    data = json.loads((pathlib.Path(__file__).resolve().parent / "data"
                       / "columbo.json").read_text(encoding="utf-8"))
    overview, pilots, seasons = data["overview"], data["pilots"], data["seasons"]

    def item(x, n, with_year=False):
        return {"id": "columbo-%d" % x["n"], "t": x["t"], "n": n,
                "note": note_for(x, with_year), "w": round(x["min"] / 60.0, 2)}

    sections = [{
        "id": "pilots", "title": "The pilots",
        "sub": "1968 & 1971 · 2 episodes",
        "intro": "Prescription: Murder began as a stage play; Peter Falk "
                 "played Columbo twice, three years apart, before NBC "
                 "ordered a series.",
        "open": True,
        "items": [item(x, x["air"][:4]) for x in pilots],
    }]

    INTRO = {
        1: "The series proper: feature-length films in rotation as one "
           "element of The NBC Mystery Movie, 1971 to 1978.",
        8: "Eleven years after NBC dropped it, ABC brought Falk back as "
           "part of The ABC Mystery Movie.",
        10: "The last fourteen aired sporadically across thirteen years. "
            "DVD releases file them as a tenth season, and the source "
            "list follows suit.",
    }

    for s in range(1, 11):
        eps = seasons[str(s)]
        sec = {
            "id": "s%d" % s,
            "title": "Season 10 and specials" if s == 10 else "Season %d" % s,
            "sub": "%s · %d episodes" % (years(overview[str(s)]), len(eps)),
            "items": [item(x, str(x["e"]), with_year=(s == 10)) for x in eps],
        }
        if s in INTRO:
            sec["intro"] = INTRO[s]
        sections.append(sec)

    items = [x for sec in sections for x in sec["items"]]
    ids = [x["id"] for x in items]
    assert len(ids) == len(set(ids)), "duplicate ids"

    # the list article's own count, from its {{Series overview}}
    claimed = sum(v["episodes"] for v in overview.values())
    assert len(items) == claimed, (len(items), claimed)
    assert ids == ["columbo-%d" % i for i in range(1, claimed + 1)], \
        "overall numbering not continuous"
    assert all(x["w"] > 0 for x in items)
    hours = sum(x["w"] for x in items)

    prop = {
        "slug": SLUG,
        "title": "Columbo",
        "subtitle": "every case in broadcast order, pilots included",
        "kind": "tv movies",
        "popularity": 59,
        "year": "1968–2003",
        "blurb": "All %d feature-length cases in broadcast order — two "
                 "pilots, the NBC seventies, and the ABC revival films."
                 % claimed,
        "unit": {"one": "episode", "many": "episodes"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": "#8A7B5C",
        "accentDark": "#D9C9A3",
        "tiers": False,
        "notes": [
            ["The killer is not a spoiler.", "Columbo is an inverted "
             "mystery — every episode opens on the murder and the murderer, "
             "and the fun is watching the trap close. The source tables lead "
             "with the guest star for the same reason, so each row names its "
             "murderer."],
            ["Weights are real runtimes.", "Every row carries the runtime "
             "from Wikipedia's episode tables, read as hours — a 70-minute "
             "Mystery Movie entry and a 94-minute pilot earn their width. "
             "No row falls back on a slot-length convention."],
            ["Grouped as the source groups it.", "Wikipedia arranges the "
             "list as the UK DVD release does: the two pilots, seasons 1–7 "
             "on NBC, the two ABC Mystery Movie seasons, and the final "
             "fourteen specials of 1990–2003 filed as season 10."],
            "Titles, airdates, runtimes and murderers machine-read from "
            "Wikipedia's List of Columbo episodes and the ten season "
            "articles it transcludes; the %d-episode total is asserted "
            "against the list's own series overview." % claimed,
        ],
        "sections": sections,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json — %d episodes, %.2f h of runtime"
          % (SLUG, len(items), hours))
    for sec in sections:
        print("   %-24s %3d  %s"
              % (sec["title"], len(sec["items"]), sec.get("sub", "")))


if __name__ == "__main__":
    main()
