#!/usr/bin/env python3
"""Generate properties/ghost-in-the-shell.json.

    python tools/make_ghost-in-the-shell.py

Everything animated, sectioned by continuity: Mamoru Oshii's two films; the
Stand Alone Complex television continuity (season 1, 2nd GIG, the Solid
State Society TV film, and — much later — SAC_2045 with its Sustainable War
compilation film between the seasons); and the Arise continuity (five
feature-length OVA "borders" closed by the 2015 New Movie).

Everything numeric comes from tools/data/ghost-in-the-shell.json, built by
scratch/agent-anime/harvest_gits.py from the Wikipedia episode lists and
film articles (infobox runtimes beat Wikidata). Because films and episodes
share the page, everything is weighted: episodes at 0.4h, films at
runtime/60, the borders at the Arise infobox's 50 minutes each. Sustainable
War has no runtime in any machine-readable source and weighs nothing rather
than a guess. Live action is out; the notes say so.
"""
import json
import pathlib

SLUG = "ghost-in-the-shell"

DATA = pathlib.Path(__file__).resolve().parent / "data" / (SLUG + ".json")
OUT = pathlib.Path(__file__).resolve().parent.parent / "properties" / (SLUG + ".json")

EP_W = 0.4

WIKI = "https://en.wikipedia.org/wiki/"


def ep_rows(eps, prefix):
    return [{"id": "%s%d" % (prefix, e["n"]), "t": e["t"], "n": str(e["n"]),
             "w": EP_W} for e in eps]


def film_row(f, id_, note_extra=""):
    w = round(f["runtime"] / 60.0, 2) if f.get("runtime") else 0
    note = ("%d min" % f["runtime"]) if f.get("runtime") else \
        "No runtime on record — weighs nothing"
    if note_extra:
        note = note_extra + " · " + note
    return {"id": id_, "t": f["t"], "n": str(f["year"]), "w": w, "note": note}


def main():
    d = json.loads(DATA.read_text(encoding="utf-8"))
    films = d["films"]

    sections = [
        {
            "id": "oshii",
            "title": "The Oshii films",
            "sub": "1995 & 2004 · the film continuity",
            "intro": "Mamoru Oshii's continuity: the 1995 film and its "
                     "sequel Innocence. Separate from every series below.",
            "links": [{"label": "The 1995 film",
                       "url": WIKI + "Ghost_in_the_Shell_(1995_film)"}],
            "open": True,
            "items": [film_row(films["f1995"], "gits-film-1995"),
                      film_row(films["f2004"], "gits-film-2004")],
        },
        {
            "id": "sac1",
            "title": "Stand Alone Complex",
            "sub": "2002–03 · 26 episodes",
            "intro": "A second continuity, restarted for television: "
                     "Section 9 from scratch, unconnected to the films.",
            "links": [{"label": "The episode list",
                       "url": WIKI + "List_of_Ghost_in_the_Shell:_"
                              "Stand_Alone_Complex_episodes"}],
            "items": ep_rows(d["sac1"], "gits-s1e"),
        },
        {
            "id": "sac2",
            "title": "S.A.C. 2nd GIG",
            "sub": "2004–05 · 26 episodes",
            "intro": "Season two of the Stand Alone Complex continuity.",
            "items": ep_rows(d["sac2"], "gits-s2e"),
        },
        {
            "id": "sss",
            "title": "Solid State Society",
            "sub": "2006 · the Stand Alone Complex TV film",
            "items": [film_row(films["f2006"], "gits-film-2006",
                               "TV film, two years after 2nd GIG")],
        },
        {
            "id": "arise",
            "title": "Arise",
            "sub": "2013–15 · five borders",
            "intro": "A third continuity: a younger Section 9, told in five "
                     "feature-length OVAs called borders, released to "
                     "cinemas first.",
            "links": [{"label": "Arise",
                       "url": WIKI + "Ghost_in_the_Shell:_Arise"}],
            "items": [{"id": "gits-arise-b%d" % b["n"],
                       "t": "Border %d: %s" % (b["n"], b["t"]),
                       "n": str(b["n"]),
                       "w": round(d["arise_min"] / 60.0, 2),
                       "note": "%d min" % d["arise_min"]}
                      for b in d["arise"]],
        },
        {
            "id": "newmovie",
            "title": "The New Movie",
            "sub": "2015 · the film that closes Arise",
            "items": [film_row(films["f2015"], "gits-film-2015",
                               "Follows the Arise borders")],
        },
        {
            "id": "s2045a",
            "title": "SAC_2045 season 1",
            "sub": "2020 · 12 episodes",
            "intro": "Back to the Stand Alone Complex continuity, set in "
                     "2045 — eleven years after Solid State Society. 3DCG, "
                     "on Netflix.",
            "links": [{"label": "The episode list",
                       "url": WIKI + "List_of_Ghost_in_the_Shell:_"
                              "SAC_2045_episodes"}],
            "items": ep_rows(d["s2045a"], "gits-2045-s1e"),
        },
        {
            "id": "suswar",
            "title": "Sustainable War",
            "sub": "2021 · the season-one compilation film",
            "items": [film_row(d["suswar"], "gits-film-2021",
                               "Recompiles season 1")],
        },
        {
            "id": "s2045b",
            "title": "SAC_2045 season 2",
            "sub": "2022 · 12 episodes",
            "items": ep_rows(d["s2045b"], "gits-2045-s2e"),
        },
    ]

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert len(ids) == 86, len(ids)
    hours = sum(x["w"] for s in sections for x in s["items"])

    prop = {
        "slug": SLUG,
        "title": "Ghost in the Shell",
        "subtitle": "everything animated, by continuity",
        "kind": "anime",
        "popularity": 64,
        "year": "1995–2022",
        "blurb": "Three animated continuities — the Oshii films, Stand "
                 "Alone Complex through SAC_2045, and Arise — %d entries, "
                 "about %d hours." % (len(ids), round(hours)),
        "unit": {"one": "entry", "many": "entries"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": "#186A66",
        "accentDark": "#F5933E",
        "tiers": False,
        "notes": [
            ["Sections are continuities.", "Three separate animated tellings "
             "share these characters: Oshii's two films; the Stand Alone "
             "Complex television line (seasons 1 and 2, Solid State Society, "
             "and — set eleven years later — SAC_2045); and Arise, whose "
             "five borders the 2015 New Movie concludes. Watch a continuity "
             "together; nothing carries between them."],
            ["Weights.", "Episodes weigh 0.4 hours, films their runtimes, "
             "and the Arise borders the 50 minutes each their article "
             "gives. Sustainable War has no runtime on record anywhere "
             "machine-readable and weighs nothing rather than a guess."],
            ["Animation only.", "The 2017 live-action remake is out. So are "
             "the recuts and rebroadcasts — Arise: Alternative Architecture "
             "(the borders re-aired for TV) and The Last Human (the "
             "season-two compilation film). Sustainable War, the season-one "
             "compilation, keeps its row so the Netflix run is complete; "
             "its row says what it is."],
            ["The Tachikomatic Days shorts are not rows.",
             "Comedy omake attached to the Stand Alone Complex broadcasts; "
             "they are on the episode-list page and nothing here depends on "
             "them."],
            "Episode lists, film years and runtimes machine-read from the "
            "Wikipedia articles; every season's numbering asserted complete "
            "before this builds.",
        ],
        "sections": sections,
    }

    with OUT.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json — %d rows, %.2f hours" % (SLUG, len(ids), hours))
    for s in sections:
        print("   %-22s %2d  %s" % (s["title"], len(s["items"]),
                                    s.get("sub", "")[:40]))


if __name__ == "__main__":
    main()
