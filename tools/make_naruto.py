#!/usr/bin/env python3
"""Generate properties/naruto.json.

    python tools/make_naruto.py

One list of 720: *Naruto* (220 episodes, 2002–07) and *Naruto: Shippuden*
(500, 2007–17) in broadcast order, sectioned by series then story arc.
*Boruto: Naruto Next Generations* is a different series and is not folded in.

The thing this list exists to show is the filler. Every row is classified
from two independent sources that have to agree:

  * animefillerlist.com's published per-episode classification, and
  * the manga chapters Narutopedia records the episode as adapting.

An episode both call anime-original is marked and flagged optional. An
episode they disagree about is left UNMARKED on purpose — a wrong filler
label sends someone skipping real story, and an unmarked filler episode
only costs them twenty minutes. Nothing is guessed either way.

Both are cached, by scratch/naruto/parse.py and scratch/naruto/fetch_chapters.py,
so this generator is offline and byte-reproducible. The counts come from the
enumerated episode tables on the Wikipedia season articles, never an infobox
summary; parse.py asserts the two agree per season, and TOTAL below asserts
the whole thing, so a future desync fails the build loudly instead of
shipping a short list.

No runtimes. Nobody publishes a verified length for 720 individual episodes,
so this ships unweighted rather than repeating an invented 23 minutes 720
times into everyone's finish date.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from gwlib import prop as gwprop            # noqa: E402

DATA = ROOT / "scratch" / "naruto" / "naruto.json"
CHAPTERS = ROOT / "scratch" / "naruto" / "chapters.json"

SLUG = "naruto"
TOTAL = 720
EXPECTED = {"naruto": 220, "shippuden": 500}

SERIES = {
    "naruto": {
        "name": "Naruto",
        "idp": "nar",
        "list": "https://en.wikipedia.org/wiki/List_of_Naruto_episodes",
    },
    "shippuden": {
        "name": "Naruto: Shippuden",
        "idp": "shp",
        "list": "https://en.wikipedia.org/wiki/List_of_Naruto:_Shippuden_episodes",
    },
}

# Wikipedia's episode tables mark a handful of runs that are not story arcs at
# all — recaps, a clip special, unnamed one-off side stories. They are folded
# into the arc they follow rather than becoming sections nobody can navigate
# by. Listed exactly so a renamed or new one fails the build instead of
# silently vanishing into its neighbour.
INTERSTITIAL = {
    "Standalone side story",
    "Standalone side stories",
    "Recap: Two Fates",
    "Battles recap special",
    "Extra edition",
}

# Named side arcs of two episodes that interrupt a longer arc and then hand it
# back. A strip cannot show a gap, so they are folded into the arc around them
# and named in that section's intro. Same deal: the exact set, asserted.
FOLDED_INSIDE = {
    "Kakashi Chronicles: Boys' Life on the Battlefield",
    "Tales of a Gutsy Ninja ~Jiraiya Ninja Scroll",
    "Big Adventure! The Quest for the Fourth Hokage's Legacy",
}

# animefillerlist classes, as parse.py normalises them
CANONISH = ("canon", "mixed", "anime-canon")


def dash(first, last):
    return str(first) if first == last else "%d–%d" % (first, last)


def spans(numbers):
    """[3, 4, 5, 9] -> '3–5, 9'."""
    out, run = [], []
    for n in sorted(numbers):
        if run and n == run[-1] + 1:
            run.append(n)
        else:
            if run:
                out.append(run)
            run = [n]
    if run:
        out.append(run)
    return ", ".join(dash(r[0], r[-1]) for r in out)


def arc_runs(series_data):
    """Wikipedia's part markers, merged into one contiguous run per arc."""
    runs = []
    for season in series_data["seasons"]:
        for a in season["arcs"]:
            if runs and runs[-1]["arc"] == a["arc"] and runs[-1]["last"] == a["first"] - 1:
                runs[-1]["last"] = a["last"]
            else:
                runs.append({"arc": a["arc"], "first": a["first"],
                             "last": a["last"], "folded": []})
    return runs


def fold(runs, series):
    """Absorb the interstitials, then the short interrupting side arcs, then
    re-join any arc whose halves have become contiguous again."""
    seen_interstitial, seen_folded = set(), set()

    out = []
    for r in runs:
        if r["arc"] in INTERSTITIAL:
            assert out, "%s: %r opens the series" % (series, r["arc"])
            seen_interstitial.add(r["arc"])
            out[-1]["folded"].append(r)
            out[-1]["last"] = r["last"]
        else:
            out.append(r)

    joined, i = [], 0
    while i < len(out):
        r = out[i]
        interrupts = (joined and i + 1 < len(out)
                      and joined[-1]["arc"] == out[i + 1]["arc"]
                      and r["last"] - r["first"] + 1 <= 2
                      and joined[-1]["last"] == r["first"] - 1
                      and out[i + 1]["first"] == r["last"] + 1)
        if interrupts:
            seen_folded.add(r["arc"])
            joined[-1]["folded"].append(r)
            joined[-1]["folded"].extend(out[i + 1]["folded"])
            joined[-1]["last"] = out[i + 1]["last"]
            i += 2
            continue
        if joined and joined[-1]["arc"] == r["arc"] and joined[-1]["last"] == r["first"] - 1:
            joined[-1]["folded"].extend(r["folded"])
            joined[-1]["last"] = r["last"]
            i += 1
            continue
        joined.append(r)
        i += 1

    for r in joined:
        r["folded"].sort(key=lambda f: f["first"])
    return joined, seen_interstitial, seen_folded


def classify(afl, chapters):
    """canon / filler / unconfirmed, from the two sources together."""
    if afl != "filler":
        return "canon"
    return "unconfirmed" if chapters.strip() else "filler"


def main():
    raw = json.loads(DATA.read_text(encoding="utf-8"))
    chap = json.loads(CHAPTERS.read_text(encoding="utf-8"))

    state, sections = {}, []
    interstitial_seen, folded_seen = set(), set()
    counts = {"filler": 0, "unconfirmed": 0, "canon": 0}
    unconfirmed_by_series = {}

    for key in ("naruto", "shippuden"):
        meta, data = SERIES[key], raw[key]
        want = EXPECTED[key]
        assert data["total"] == want, \
            "%s: the episode tables come to %d, expected %d" % (
                key, data["total"], want)

        afl = {int(n): v for n, v in data["filler"].items()}
        ch = {int(n): v["chapters"] for n, v in chap[key].items()}
        assert sorted(afl) == sorted(ch) == list(range(1, want + 1)), \
            "%s: the two sources do not cover the same episodes" % key

        state[key] = {e: classify(afl[e], ch[e]) for e in range(1, want + 1)}
        for e in range(1, want + 1):
            counts[state[key][e]] += 1
        unconfirmed_by_series[key] = [e for e in range(1, want + 1)
                                      if state[key][e] == "unconfirmed"]

        runs, si, sf = fold(arc_runs(data), key)
        interstitial_seen |= si
        folded_seen |= sf

        assert runs[0]["first"] == 1 and runs[-1]["last"] == want, \
            "%s: arcs run %d-%d, expected 1-%d" % (
                key, runs[0]["first"], runs[-1]["last"], want)
        for a, b in zip(runs, runs[1:]):
            assert b["first"] == a["last"] + 1, \
                "%s: gap between arcs at episode %d" % (key, b["first"])
        titles = [r["arc"] for r in runs]
        assert len(titles) == len(set(titles)), \
            "%s: two sections would share a title: %s" % (
                key, sorted(t for t in titles if titles.count(t) > 1)[:2])

        for r in runs:
            sections.append(build_section(key, meta, r, state[key]))

    assert interstitial_seen == INTERSTITIAL, \
        "the interstitial runs on Wikipedia changed: %s" % sorted(
            INTERSTITIAL ^ interstitial_seen)
    assert folded_seen == FOLDED_INSIDE, \
        "the folded side arcs on Wikipedia changed: %s" % sorted(
            FOLDED_INSIDE ^ folded_seen)

    rows = sum(len(s["items"]) for s in sections)
    assert rows == TOTAL, \
        "built %d rows, expected %d — the source tables moved" % (rows, TOTAL)
    assert sum(counts.values()) == TOTAL, counts
    assert not unconfirmed_by_series["naruto"], \
        "the two sources used to agree on every Naruto episode; now they do " \
        "not: %s" % unconfirmed_by_series["naruto"]

    unconfirmed = counts["unconfirmed"]
    filler = counts["filler"]

    prop = {
        "slug": SLUG,
        "title": "Naruto",
        "subtitle": "The original series and Shippuden",
        "kind": "anime",
        "popularity": 90,
        "year": "2002–2017",
        "blurb": "%d episodes, both series in broadcast order, with the "
                 "filler marked." % TOTAL,
        "unit": {"one": "episode", "many": "episodes"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "accent": "#155EEF",
        "accentDark": "#7FA8FF",
        "tiers": False,
        "notes": [
            ["Filler.",
             "%d of %d episodes are marked anime-original and flagged "
             "optional: “Filler arc” for a run of three or more, "
             "“Anime-original” for a one-off or a pair. A row has to "
             "be called filler by animefillerlist.com's published list AND "
             "adapt no manga chapter in Narutopedia's episode data before it "
             "gets marked. An unmarked row adapts the manga."
             % (filler, TOTAL)],
            ["Unmarked on purpose.",
             "%d Shippuden episodes are left unmarked because the two sources "
             "disagree about them — the filler list calls them filler, "
             "the chapter mapping ties them to a manga chapter: %s. A wrong "
             "filler label costs you real story; leaving one unmarked costs "
             "you an episode. Nothing here is guessed."
             % (unconfirmed, spans(unconfirmed_by_series["shippuden"]))],
            ["No runtimes.",
             "There is no verified per-episode length for 720 episodes, so "
             "every row weighs the same and the pace counts episodes rather "
             "than minutes. A blanket 23 minutes would read as measured and "
             "would be invented."],
            ["Arcs.",
             "Sections are the story arcs Wikipedia's own episode tables mark. "
             "Recaps, clip specials and unnamed side stories are folded into "
             "the arc they follow, and a two-episode side arc that interrupts "
             "a longer one is folded into it and named in that section's "
             "intro — a strip cannot show a gap. Rows are numbers, not "
             "titles: Naruto's episode titles routinely name the outcome of "
             "the episode."],
            ["Boruto.",
             "Boruto: Naruto Next Generations is a separate series with its "
             "own episode list and is not folded in here."],
            "Both series are finished: 220 episodes of Naruto and 500 of "
            "Shippuden, %d in all." % TOTAL,
        ],
        "sections": sections,
    }

    out = gwprop.write(prop)
    print("wrote %s" % out.name)
    print("  %d sections, %d rows (%d + %d)"
          % (len(sections), rows, EXPECTED["naruto"], EXPECTED["shippuden"]))
    print("  %d filler, %d unconfirmed, %d adapt the manga"
          % (filler, unconfirmed, counts["canon"]))
    for s in sections:
        marked = sum(1 for x in s["items"] if x.get("opt"))
        print("   %-56s %3d  %s" % (s["sub"], len(s["items"]),
                                    "%d filler" % marked if marked else ""))


def build_section(key, meta, run, state):
    first, last = run["first"], run["last"]
    n = last - first + 1
    episodes = list(range(first, last + 1))
    filler = [e for e in episodes if state[e] == "filler"]
    unconfirmed = [e for e in episodes if state[e] == "unconfirmed"]

    # "filler arc" for a run of three or more consecutive anime-original
    # episodes, or for any row in a section that is anime-original end to end;
    # "anime-original" for a one-off or a pair sitting inside a canon arc
    whole_arc = bool(filler) and len(filler) == n
    note = {}
    run_len, i = {}, 0
    while i < len(episodes):
        if state[episodes[i]] != "filler":
            i += 1
            continue
        j = i
        while j < len(episodes) and state[episodes[j]] == "filler":
            j += 1
        for e in episodes[i:j]:
            run_len[e] = j - i
        i = j
    for e in filler:
        note[e] = ("Filler arc" if whole_arc or run_len[e] >= 3
                   else "Anime-original")

    items = []
    for e in episodes:
        row = {"id": "%s-%d" % (meta["idp"], e), "t": "Episode", "n": str(e)}
        if e in note:
            row["note"] = note[e]
            row["opt"] = 1
        items.append(row)

    sub = "%s · episode%s %s" % (meta["name"], "" if n == 1 else "s",
                                      dash(first, last))
    if filler and len(filler) == n:
        sub += " · filler arc"
    elif filler:
        sub += " · %d of %d filler" % (len(filler), n)

    intro = []
    if run["folded"]:
        intro.append("Folded in: %s." % ", ".join(
            "%s (%s)" % (f["arc"], dash(f["first"], f["last"]))
            for f in run["folded"]))
    if unconfirmed:
        intro.append("Unmarked here: %s — the filler list and the "
                     "chapter mapping disagree." % spans(unconfirmed))

    section = {
        "id": "%s-%s" % (meta["idp"], gwprop.slug(run["arc"])),
        "title": run["arc"],
        "sub": sub,
        "links": [{"label": "Episode list", "url": meta["list"]}],
        "items": items,
    }
    if intro:
        section["intro"] = " ".join(intro)
    return section


if __name__ == "__main__":
    main()
