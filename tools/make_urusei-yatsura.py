#!/usr/bin/env python3
"""Generate properties/urusei-yatsura.json.

    python tools/make_urusei-yatsura.py

Four eras: the 1981–86 series (194 numbered episodes across the four
season tables Wikipedia uses), the six theatrical films, the ten OVAs, and
the 2022 remake's two seasons. Everything comes from
tools/data/urusei-yatsura.json, built by scratch/agent-anime/harvest_uy.py
from the Wikipedia episode lists and the film-series article; a film's own
article beats the franchise page on runtime (Beautiful Dreamer: 98 min,
not 96).

Films and episodes share the page, so everything is weighted — episodes
and OVAs at 0.4h, films at runtime/60. Beautiful Dreamer's row notes its
Time Loops cross-listing; it is on that page too. The three specials the
1981 tables carry outside the numbering are not rows, and the notes say so.
"""
import json
import pathlib

SLUG = "urusei-yatsura"

DATA = pathlib.Path(__file__).resolve().parent / "data" / (SLUG + ".json")
OUT = pathlib.Path(__file__).resolve().parent.parent / "properties" / (SLUG + ".json")

EP_W = 0.4
WIKI = "https://en.wikipedia.org/wiki/"

FILM_NOTES = {1984: "Also on the Time Loops list"}


def main():
    d = json.loads(DATA.read_text(encoding="utf-8"))

    sections = []
    for s in d["series"]:
        sec = {
            "id": "s%d" % s["season"],
            "title": "Season %d" % s["season"],
            "sub": "%s · %d episodes" % (s["years"], len(s["eps"])),
            "links": [{"label": "The episode list",
                       "url": WIKI + "List_of_Urusei_Yatsura_episodes"}],
            "items": [{"id": "uy-e%d" % e["n"], "t": e["t"],
                       "n": str(e["n"]), "w": EP_W} for e in s["eps"]],
        }
        if s["season"] == 1:
            sec["open"] = True
            sec["intro"] = ("Rumiko Takahashi's alien-girl farce, adapted "
                            "while the manga ran. Most early episodes aired "
                            "as two shorter segments — those rows join both "
                            "titles.")
        sections.append(sec)

    film_items = []
    for f in d["films"]:
        note = "%d min" % f["runtime"]
        if f["year"] in FILM_NOTES:
            note = FILM_NOTES[f["year"]] + " · " + note
        film_items.append({"id": "uy-film-%d" % f["year"], "t": f["t"],
                           "n": str(f["year"]),
                           "w": round(f["runtime"] / 60.0, 2), "note": note})
    sections.append({
        "id": "films",
        "title": "The films",
        "sub": "1983–91 · six theatrical films",
        "intro": "Four made during the TV run, two after it. Beautiful "
                 "Dreamer is Mamoru Oshii's — and sits on the Time Loops "
                 "list as well.",
        "links": [{"label": "The film series",
                   "url": WIKI + "Urusei_Yatsura_(film_series)"}],
        "items": film_items,
    })

    sections.append({
        "id": "ovas",
        "title": "The OVAs",
        "sub": "1987–2008 · ten releases",
        "intro": "Released 1987–91, plus one 2008 special made for the "
                 "It's a Rumic World exhibition. All ran in cinemas before "
                 "video.",
        "items": [{"id": "uy-ova-%d" % o["n"], "t": o["t"], "n": str(o["n"]),
                   "w": EP_W, "note": str(o["year"])} for o in d["ovas"]],
    })

    for r in d["remake"]:
        items = []
        for e in r["eps"]:
            slug_n = e["n"].replace("–", "-").lower()
            items.append({"id": "uy22-%s" % slug_n, "t": e["t"],
                          "n": e["n"], "w": EP_W})
        sec = {
            "id": "r%d" % r["season"],
            "title": "The remake, season %d" % r["season"],
            "sub": "%s · 23 broadcasts" % r["years"],
            "links": [{"label": "The 2022 series",
                       "url": WIKI + "Urusei_Yatsura_(2022_TV_series)"}],
            "items": items,
        }
        if r["season"] == 1:
            sec["intro"] = ("The 2022 remake by David Production, adapting "
                            "selected chapters afresh.")
        else:
            sec["intro"] = ("The numbering keeps the tables' own quirk: two "
                            "broadcasts each span parts of two episodes, so "
                            "their rows carry both numbers.")
        sections.append(sec)

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert len(ids) == 194 + 6 + 10 + 46, len(ids)
    hours = sum(x["w"] for s in sections for x in s["items"])

    prop = {
        "slug": SLUG,
        "title": "Urusei Yatsura",
        "subtitle": "the 1981 series, the films, the OVAs, the remake",
        "kind": "anime",
        "order": 86,
        "year": "1981–2024",
        "blurb": "All 194 episodes of the original run, six films, ten "
                 "OVAs and the 2022 remake — about %d hours of Lum."
                 % round(hours),
        "unit": {"one": "entry", "many": "entries"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": "#4C7A1D",
        "accentDark": "#FFD447",
        "tiers": False,
        "notes": [
            ["Eras in order.", "The 1981–86 series (the four season tables "
             "Wikipedia uses are kept), the six theatrical films, the OVAs "
             "as one block, then the 2022 remake's two seasons."],
            ["Weights.", "Episodes and OVAs weigh 0.4 hours; films weigh "
             "their runtimes. Beautiful Dreamer's runtime comes from its "
             "own article (98 min), which beats the franchise page's 96."],
            ["What is out.", "The three specials the 1981 tables carry "
             "outside the episode numbering — All-Star Bash, Ryoko's "
             "September Tea Party and Memorial Album, the latter two "
             "mixing new footage with clips — and the Lum the Forever "
             "making-of featurette."],
            "Episode tables, film years and runtimes machine-read from the "
            "Wikipedia episode lists, the film-series article and the "
            "films' own articles; season counts and the 1–194 numbering "
            "asserted before this builds.",
        ],
        "sections": sections,
    }

    with OUT.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json — %d rows, %.2f hours" % (SLUG, len(ids), hours))
    for s in sections:
        print("   %-24s %3d  %s" % (s["title"], len(s["items"]),
                                    s.get("sub", "")[:40]))


if __name__ == "__main__":
    main()
