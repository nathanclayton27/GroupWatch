#!/usr/bin/env python3
"""Generate properties/attack-on-titan.json.

    python tools/make_attack_on_titan.py

Every numbered episode of the anime in broadcast order, one row each, from
season 1 through the Final Season's fourth part.

The count is **94**, not the 89 that most summaries of this show repeat, and
the difference is the whole reason this generator asserts as hard as it does.
The Final Season's parts 3 and 4 first aired as two feature-length television
specials; they were later redistributed as the seven numbered episodes 88-94.
Wikipedia's season 4 article prints both printings, one under "Special
Version" and one under "Episode Version". Count the special rows and you get
87 + 2 = 89; count the enumerated episodes and you get 94. This list uses the
numbered episodes, so every row is one sitting, and RECONCILE below fails the
build if that arithmetic ever stops holding.

Sections follow the source's own tables: one per season, subdivided wherever
the season article carries an {{Episode table/part}} marker. Seasons 1 and 2
have none. Season 3 has two parts (2018, 2019); the Final Season has four
(2020-21, 2022, 2023, 2023), which aired years apart and are how everyone
refers to them.

Unweighted, deliberately. Wikipedia's episode tables carry no per-episode
runtimes and neither do the season infoboxes, so there is nothing to weigh
with; stamping the same guessed figure on 94 rows would be an invented number
wearing a decimal point. Every row counts as one episode instead, and no row
carries `w` — a single weighted row here would make the other 93 silently
count as an hour apiece.

Out: the compilation films, which re-cut episodes already on this list, and
season 1's "Since That Day" recap special (13.5) — both would count a watch
this list already counts. Neither is enumerated on the episode list, so
neither is counted here either. Optional tail: the three OADs the list page
does enumerate, in its own table.

Data: scratch/aot/harvest.py -> scratch/aot/attack-on-titan.json, parsed from
the cached wikitext of the list page and the four season articles beside it.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from gwlib import prop as P  # noqa: E402

SLUG = "attack-on-titan"
DATA = ROOT / "scratch" / "aot" / (SLUG + ".json")

WIKI = "https://en.wikipedia.org/wiki/"
LIST_URL = WIKI + "List_of_Attack_on_Titan_episodes"

# The totals this list signed up for, from the Series overview table on the
# list page: episodes1=25, episodes2=12, episodes3=22 (12+10),
# episodes4=35 (16+12+3+4). A desync fails the build rather than shipping.
EXPECTED = {
    (1, 1): 25,
    (2, 1): 12,
    (3, 1): 12, (3, 2): 10,
    (4, 1): 16, (4, 2): 12, (4, 3): 3, (4, 4): 4,
}
TOTAL = 94
OADS = 3

# The arithmetic behind the wrong number everyone quotes. Parts 3 and 4 are
# SPECIALS=2 television specials and REDISTRIBUTED=7 numbered episodes; both
# printings are the same footage, and 94 - 7 + 2 is the familiar 89.
SPECIALS = 2
REDISTRIBUTED = 7
RECONCILE = 89

# id prefix; never change it, these are the saved ticks
IDP = "aot"

# small counts read better spelled out in a note than as digits
WORDS = {2: "two", 3: "three", 4: "four", 7: "seven"}

# (season, part) -> section id, section title, year label, and the intro that
# explains a part that is not simply "these aired weekly"
PARTS = {
    (1, 1): ("s1", "Season 1", "2013", None),
    (2, 1): ("s2", "Season 2", "2017", None),
    (3, 1): ("s3-p1", "Season 3 Part 1", "2018", None),
    (3, 2): ("s3-p2", "Season 3 Part 2", "2019", None),
    (4, 1): ("s4-p1", "The Final Season Part 1", "2020–21", None),
    (4, 2): ("s4-p2", "The Final Season Part 2", "2022", None),
    (4, 3): ("s4-p3", "The Final Season Part 3", "2023",
             "First aired as a feature-length television special, "
             "The Final Chapters (Part 1), in March 2023; later "
             "redistributed as these three numbered episodes. Three rows "
             "rather than one, because three is what the episode tables "
             "enumerate."),
    (4, 4): ("s4-p4", "The Final Season Part 4", "2023",
             "The same again: one television special, The Final Chapters "
             "(Part 2), redistributed as these four numbered episodes."),
}

SEASON_URL = {n: WIKI + "Attack_on_Titan_season_%d" % n for n in (1, 2, 3, 4)}


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    seasons = {s["season"]: s for s in data["seasons"]}

    # --- the source's own arithmetic, before anything is built ------------
    episodes = [e for s in data["seasons"] for e in s["episodes"]]
    assert [e["overall"] for e in episodes] == list(range(1, TOTAL + 1)), \
        "overall episode numbers are not a contiguous 1-%d run" % TOTAL
    for n, s in seasons.items():
        want = sum(v for (sn, _), v in EXPECTED.items() if sn == n)
        assert len(s["episodes"]) == want, \
            "season %d: harvested %d episodes, expected %d" \
            % (n, len(s["episodes"]), want)
        assert [e["in_season"] for e in s["episodes"]] == \
            list(range(1, want + 1)), "season %d: in-season numbering broken" % n
    for key, want in EXPECTED.items():
        got = [e for e in seasons[key[0]]["episodes"] if e["part"] == key[1]]
        assert len(got) == want, \
            "season %d part %d: harvested %d, expected %d" \
            % (key[0], key[1], len(got), want)
    assert len(episodes) == TOTAL, (len(episodes), TOTAL)

    # The 89 trap, asserted in both directions: the two special printings are
    # present in the source and are NOT counted as rows, and dropping the
    # seven redistributed episodes for them reproduces the familiar number.
    assert len(data["specials"]) == SPECIALS, data["specials"]
    assert sum(EXPECTED[(4, p)] for p in (3, 4)) == REDISTRIBUTED
    assert TOTAL - REDISTRIBUTED + SPECIALS == RECONCILE, \
        "the 94/89 reconciliation no longer holds — re-read the source"
    assert len(data["recaps"]) == 1, data["recaps"]
    assert len(data["oads"]) == OADS, data["oads"]

    # --- sections ---------------------------------------------------------
    sections = []
    for key in sorted(EXPECTED):
        season, part = key
        sid, title, years, intro = PARTS[key]
        rows = [e for e in seasons[season]["episodes"] if e["part"] == part]
        sec = {
            "id": sid,
            "title": title,
            "sub": "%s · episodes %d–%d" % (years, rows[0]["overall"],
                                            rows[-1]["overall"]),
            "links": [{"label": "Episode list", "url": SEASON_URL[season]}],
            "items": [{"id": "%s-%d" % (IDP, e["overall"]), "t": e["t"],
                       "n": str(e["overall"])} for e in rows],
        }
        if intro:
            sec["intro"] = intro
        if sid == "s1":
            sec["open"] = True
        sections.append(sec)

    sections.append({
        "id": "oads",
        "title": "OADs",
        "sub": "2013–14 · three bonus episodes · optional",
        "intro": "Bundled with limited editions of the manga. Optional: they "
                 "sit outside the broadcast run and nothing in the numbered "
                 "episodes depends on them.",
        "links": [{"label": "Episode list", "url": LIST_URL}],
        "items": [{"id": "%s-oad-%d" % (IDP, o["n"]), "t": o["t"],
                   "n": "OAD %d" % o["n"], "opt": 1} for o in data["oads"]],
    })

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == TOTAL + OADS, (len(ids), TOTAL + OADS)
    assert len(sections) == len(EXPECTED) + 1, len(sections)
    # Unweighted, all of it. One weighted row would turn the other 96 into an
    # hour apiece without saying so.
    assert not any("w" in x for s in sections for x in s["items"]), \
        "a weight crept in — this list is unweighted on purpose"

    p = {
        "slug": SLUG,
        "title": "Attack on Titan",
        "subtitle": "the complete broadcast run",
        "kind": "anime",
        "popularity": 84,
        "year": "2013–2023",
        "blurb": "All %d episodes in broadcast order, season 1 through the "
                 "Final Season's fourth part." % TOTAL,
        "unit": {"one": "episode", "many": "episodes"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": "#2B5032",
        "accentDark": "#63AD75",
        "tiers": False,
        "notes": [
            ["%d episodes, not %d." % (TOTAL, RECONCILE),
             "The Final Season's parts 3 and 4 first aired as two "
             "feature-length television specials, and most summaries count "
             "those as two entries — %d weekly episodes plus %d specials. "
             "They were later redistributed as the %s numbered episodes "
             "%d–%d, which is what the episode tables enumerate and what "
             "this list uses, so every row is one sitting."
             % (TOTAL - REDISTRIBUTED, SPECIALS, WORDS[REDISTRIBUTED],
                TOTAL - REDISTRIBUTED + 1, TOTAL)],
            ["Sections follow the source's own tables.",
             "One per season, split wherever the season article splits "
             "itself: season 3 into two parts, the Final Season into four. "
             "Those parts aired years apart and are how the show is talked "
             "about."],
            ["No weights.",
             "Neither the episode tables nor the season infoboxes carry "
             "per-episode runtimes, so there is nothing here to weigh with. "
             "Putting one guessed figure on %d rows would be an invented "
             "number wearing a decimal point; every row counts as one "
             "episode instead." % TOTAL],
            ["The films are out.",
             "The compilation films re-cut episodes that are already on this "
             "list, so ticking them would count the same watch twice. Season "
             "1's \"Since That Day\" recap special is out for the same "
             "reason."],
            ["The OADs are optional.",
             "Three bonus episodes bundled with manga volumes, enumerated in "
             "the episode list's own table and marked optional here. That "
             "page's prose counts eight OADs in all — the other five belong "
             "to the No Regrets and Lost Girls sets, which have their own "
             "articles and are not enumerated on it."],
            "Episode numbers, titles and part boundaries machine-read from "
            "Wikipedia's four season articles and checked against the series "
            "overview on List of Attack on Titan episodes.",
        ],
        "sections": sections,
    }

    out = P.write(p)
    print("wrote %s — %d rows (%d episodes + %d optional OADs)"
          % (out.name, len(ids), TOTAL, OADS))
    print("  reconciles: %d episodes − %d redistributed + %d specials = %d"
          % (TOTAL, REDISTRIBUTED, SPECIALS, RECONCILE))
    for s in sections:
        print("   %-26s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
