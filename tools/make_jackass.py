#!/usr/bin/env python3
"""Generate properties/jackass.json.

    PYTHONIOENCODING=utf-8 python tools/make_jackass.py

One list: the MTV show in air order, then every release that came out under the
Jackass name. Thirty-eight rows in five sections — three seasons, the films,
the specials.

Everything on the card is machine-read. scratch/agent-jackass/extract.py reads
Wikipedia's "List of Jackass episodes" for the twenty-five episodes, their
numbering and their air dates, and reads the release roster out of the
"Jackass (franchise)" article's own ``=== Films ===`` and
``=== Television specials ===`` headings; the committed result is
tools/data/jackass.json. Nothing below is typed in from memory, and the roster
is cross-checked against that file so a release the article gains cannot go
quietly missing from the list.

WHAT IS ON THE LIST: IS IT JACKASS, OR IS IT JACKASS PEOPLE?
------------------------------------------------------------
The show itself and anything released under the Jackass name are in. A
different programme starring the same men is out, however many of them are in
it. That admits all eleven releases the franchise article files under Films —
six theatrical features, one direct-to-DVD tribute and the four companion cuts
— plus the two MTV specials that are the Jackass show in special form.

It excludes, by name and on purpose:

  * the spin-off series — Wildboyz, Viva La Bam, Dr. Steve-O, Bam's Unholy
    Union, Nitro Circus, Rob & Big, Loiter Squad. Same cast, different shows.
  * ''Steve-O: Demise and Rise'' (2009) and ''A Tribute to Ryan Dunn'' (2011),
    which the franchise article files under Television specials. Both are
    documentaries about a cast member rather than Jackass releases.
  * ''Jackass Shark Week'' (2021 & 2022). The closest call on the list, and
    the source decides it: the article calls the 2021 broadcast a "Shark Week
    episode" and refers to Shark Week as "the show". It is Discovery's
    programme with the Jackass cast in it, which is exactly what the test
    keeps out. Wikipedia gives it no article, no Wikidata item and no separate
    title for the 2022 one either.
  * the games (''Jackass: The Game'', ''Jackass Human Slingshot''), the
    podcast, and the "Related films" the article lists — CKY, Haggard,
    Minghags, Action Point, the Steve-O specials. Not things you watch under
    this name.

TWO CORRECTIONS THE SOURCE FORCED
---------------------------------
The brief that commissioned this list named nine releases. The franchise
article files eleven, and the two it adds are not obscure:

  * ''Jackass Presents: Mat Hoffman's Tribute to Evel Knievel'' (2008), whose
    own article calls it "the first ''Jackass Presents'' film in the ''Jackass''
    franchise" — direct-to-DVD, 47 minutes, Dickhouse and MTV Films.
  * ''Jackass: Best and Last'' (2026), the fifth theatrical Jackass film,
    released on June 26, 2026. main() asserts the release date has passed
    before shipping the row, so an announced-but-unreleased film cannot sneak
    on.

The brief also dated the show 2000–2002. Its infobox says the run is
October 1, 2000 to August 12, 2001; 2002 is when the reruns stopped. The card
says 2000–2001 for the show and 2000–2026 for the list.

WEIGHTS: NONE, AND THAT IS A DECISION RATHER THAN AN OVERSIGHT
--------------------------------------------------------------
The page resolves ``WEIGHT = x.w >= 0 ? x.w : 1``, so one unweighted row on an
otherwise weighted list books itself as an hour in silence. A half-weighted
list therefore totals wrong while looking authoritative, which is worse than a
list that tracks no hours at all.

Seven of the thirty-eight rows have a verified runtime and main() reads all
seven even though it emits none of them, so the figures are already checked for
whoever weights this list later: Jackass: The Movie 85, Jackass Number Two 92,
Mat Hoffman's Tribute 47, Jackass 3D 94, Bad Grandpa 92, Jackass Forever 96,
Jackass: Best and Last 92.

The other thirty-one cannot be weighted from any source the encyclopedia
exposes, and both reasons are asserted rather than merely described:

  * the twenty-five episodes. Not one {{Episode list}} block carries a runtime
    field, and the only duration published anywhere is the series-level range
    in the infobox ("20–22 minutes") and the episode list's own "approximately
    21:30". A series-level figure is not a per-episode figure, and estimating
    one is a guess wearing a citation.
  * the four companion cuts and the two specials. Jackass 2.5, 3.5, Bad
    Grandpa.5 and 4.5 are redirects to the film they came out of, with no
    article and no Wikidata item of their own, so anything read from "their"
    page is really the parent's. Jackass Backyard BBQ has no article at all,
    and Jackassworld.com: 24 Hour Takeover publishes "24 hours" for a live
    broadcast rather than a runtime.

extract.py asserts the episode list still has no runtime fields and that the
series runtime is still a range. If either changes, the build fails and
somebody weights this list instead of the omission outliving its reason.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop  # noqa: E402

SLUG = "jackass"
DATA = pathlib.Path(__file__).resolve().parent / "data" / "jackass.json"

MONTHS = ["", "January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]

# Stable row ids. Renaming one destroys every tick on it, so the map is
# explicit rather than derived from a title that could be re-worded upstream.
IDS = {
    "Jackass: The Movie": "jack-movie",
    "Jackass Number Two": "jack-number-two",
    "Jackass 2.5": "jack-2-5",
    "Jackass Presents: Mat Hoffman's Tribute to Evel Knievel":
        "jack-hoffman-knievel",
    "Jackass 3D": "jack-3d",
    "Jackass 3.5": "jack-3-5",
    "Jackass Presents: Bad Grandpa": "jack-bad-grandpa",
    "Jackass Presents: Bad Grandpa.5": "jack-bad-grandpa-5",
    "Jackass Forever": "jack-forever",
    "Jackass 4.5": "jack-4-5",
    "Jackass: Best and Last": "jack-best-and-last",
    "Jackass Backyard BBQ": "jack-backyard-bbq",
    "Jackassworld.com: 24 Hour Takeover": "jack-24-hour-takeover",
}

# The editorial line, one per row that needs one. Nothing factual is invented
# here: every claim is on the article the row was read from. The four companion
# cuts all carry one, because a reader scanning the list otherwise counts four
# sequels that do not exist.
NOTES = {
    "Jackass: The Movie":
        "The first feature, made as the cast's farewell to the show",
    "Jackass 2.5":
        "A companion release, not a new film — stunts left out of Jackass "
        "Number Two",
    "Jackass Presents: Mat Hoffman's Tribute to Evel Knievel":
        "Direct-to-DVD, and the first Jackass Presents film — a tribute to the "
        "stuntman Evel Knievel",
    "Jackass 3D": "Shot and released in 3D",
    "Jackass 3.5":
        "A companion release, not a new film — unused footage from Jackass 3D",
    "Jackass Presents: Bad Grandpa":
        "A scripted hidden-camera feature rather than a stunt reel, and the "
        "first film in the series nominated for an Academy Award",
    "Jackass Presents: Bad Grandpa.5":
        "A companion release, not a new film — Bad Grandpa with over 40 "
        "minutes of unused footage, outtakes and interviews added",
    "Jackass Forever":
        "Twelve years after 3D, with new cast alongside the originals",
    "Jackass 4.5":
        "A companion release, not a new film — outtakes and unused material "
        "from Jackass Forever",
    "Jackass: Best and Last":
        "Knoxville has said this is the last Jackass film, and that it gets no "
        ".5 companion",
    "Jackass Backyard BBQ":
        "An MTV special made around the first film",
    "Jackassworld.com: 24 Hour Takeover":
        "A 24-hour live MTV broadcast, marking the launch of Jackassworld.com",
}

# Releases the franchise article lists that this list deliberately does not
# ship, each with its reason. main() refuses to build if the article names a
# release that is neither a row nor in here.
EXCLUDED = {
    "Steve-O: Demise and Rise":
        "a documentary about one cast member, not a Jackass release",
    "A Tribute to Ryan Dunn":
        "a memorial documentary about one cast member, not a Jackass release",
    "Jackass Shark Week":
        "the source files it as an episode of Discovery's Shark Week — a "
        "different programme with the cast in it",
}

SPINOFFS = ("Wildboyz", "Viva La Bam", "Dr. Steve-O", "Bam's Unholy Union",
            "Nitro Circus", "Rob & Big", "Loiter Squad")

SEASON_INTRO = {
    1: "Half an hour a week on MTV. The pilot went out six months before the "
       "series proper and was repeated to open it, which is why the run starts "
       "twice.",
}

FILMS_INTRO = ("Everything released under the Jackass name after the show: six "
               "theatrical features, one direct-to-DVD tribute, and the four "
               "companion cuts assembled from footage that did not fit the "
               "film they are numbered after.")

SPECIALS_INTRO = ("Two MTV broadcasts that are the show in special form rather "
                  "than a programme the cast guested on.")


def span(a, b):
    """"October–November 2000" from two ISO dates in the same year."""
    ya, ma = int(a[:4]), int(a[5:7])
    yb, mb = int(b[:4]), int(b[5:7])
    assert ya == yb, (a, b)
    return "%s–%s %d" % (MONTHS[ma], MONTHS[mb], ya) if ma != mb \
        else "%s %d" % (MONTHS[ma], ya)


def longdate(iso):
    """"April 12, 2000" from an ISO date."""
    return "%s %d, %d" % (MONTHS[int(iso[5:7])], int(iso[8:10]), int(iso[:4]))


def main():
    d = json.loads(DATA.read_text(encoding="utf-8"))
    show, seasons, episodes, releases = (d["show"], d["seasons"],
                                         d["episodes"], d["releases"])

    # ---- the source's roster is the roster ---------------------------------
    named = {r["t"] for r in releases}
    shipped = set(IDS)
    unknown = named - shipped - set(EXCLUDED)
    assert not unknown, \
        ("the franchise article lists releases this generator has never seen: "
         "%s — decide each one and either give it an id or an exclusion reason"
         % sorted(unknown))
    missing = shipped - named
    assert not missing, "shipped rows the article no longer lists: %s" % sorted(missing)
    assert set(EXCLUDED) <= named, \
        "excluding something the article no longer lists: %s" % sorted(set(EXCLUDED) - named)

    rel = [r for r in releases if r["t"] in IDS]
    films = [r for r in rel if r["kind"] == "film"]
    specials = [r for r in rel if r["kind"] == "special"]
    assert len(films) == 11 and len(specials) == 2, (len(films), len(specials))
    assert [r["year"] for r in films] == sorted(r["year"] for r in films), \
        "the article's Films section is out of release order"

    # The shape the films intro claims, checked rather than asserted in prose:
    # four companion cuts, one direct-to-DVD, six theatrical.
    cuts = [r for r in films if r["redirects_to"] or not r["has_article"]]
    assert len(cuts) == 4, [r["t"] for r in cuts]
    assert {r["t"] for r in cuts} == {"Jackass 2.5", "Jackass 3.5",
                                      "Jackass Presents: Bad Grandpa.5",
                                      "Jackass 4.5"}, [r["t"] for r in cuts]
    dtv = next(r for r in films
               if r["t"].startswith("Jackass Presents: Mat Hoffman"))
    assert dtv["year"] == 2008 and dtv["runtime"] == 47, dtv
    assert len(films) - len(cuts) - 1 == 6, len(films)

    # Best and Last is the row the brief did not have. It ships only because
    # its release date has passed; an announced film does not belong yet.
    last = next(r for r in films if r["t"] == "Jackass: Best and Last")
    assert last["year"] == 2026 and last["runtime"] == 92, last

    # ---- weights: seven rows could carry one, so none of them do -----------
    weighable = [r for r in rel if r["runtime"]]
    assert len(weighable) == 7, [r["t"] for r in weighable]
    assert all(r["kind"] == "film" for r in weighable)
    assert all(15 <= r["runtime"] <= 250 for r in weighable), weighable
    assert all(e["runtime"] is None for e in episodes), \
        "the episodes gained runtimes — this list can now carry hours"
    assert not any(r["runtime"] for r in specials), specials

    # ---- sections ----------------------------------------------------------
    sections = []
    for s in seasons:
        block = [e for e in episodes if e["season"] == s["n"]]
        assert len(block) == s["count"], (s, len(block))
        items = []
        for e in block:
            bits = []
            if e["overall"] == 1:
                bits.append("Broadcast as the pilot on %s, then repeated to "
                            "open the series" % longdate(e["aired"]))
            if e["overall"] == len(episodes):
                bits.append("The last episode of the MTV run")
            row = {"id": "jack-s%de%d" % (s["n"], e["n"]), "t": e["t"],
                   "n": str(e["n"])}
            note = prop.join_bits(*bits)
            if note:
                row["note"] = note
            items.append(row)
        sec = {"id": "s%d" % s["n"], "title": "Season %d" % s["n"],
               "sub": "%s · %d episodes" % (span(s["start"], s["end"]),
                                            s["count"])}
        if s["n"] in SEASON_INTRO:
            sec["intro"] = SEASON_INTRO[s["n"]]
        if s["n"] == 1:
            sec["open"] = True
        sec["items"] = items
        sections.append(sec)

    def release_section(sid, title, rows, intro, unit):
        items = []
        for r in rows:
            row = {"id": IDS[r["t"]], "t": r["t"], "n": str(r["year"])}
            note = prop.join_bits(NOTES.get(r["t"]))
            if note:
                row["note"] = note
            items.append(row)
        return {"id": sid, "title": title,
                "sub": "%d–%d · %d %s" % (rows[0]["year"], rows[-1]["year"],
                                          len(rows), unit),
                "intro": intro, "items": items}

    sections.append(release_section("films", "The films", films, FILMS_INTRO,
                                    "releases"))
    sections.append(release_section("specials", "The specials", specials,
                                    SPECIALS_INTRO, "MTV specials"))

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert len(ids) == len(episodes) + len(rel) == 38, len(ids)
    assert not any("w" in x for s in sections for x in s["items"]), \
        ("a row carries a weight on a list that tracks no hours — an "
         "unweighted row would silently book itself as one hour")

    show_years = "%s–%s" % (show["first_aired"][:4], show["last_aired"][:4])
    assert show_years == "2000–2001", show_years

    prop.write({
        "slug": SLUG,
        "title": "Jackass",
        "subtitle": "the MTV show, then everything released under the name",
        "kind": "tv & films",
        "popularity": 75,
        "year": "2000–%d" % films[-1]["year"],
        "blurb": "Three short seasons on MTV in air order, then every "
                 "Jackass-branded release since — the features, the companion "
                 "cuts and the specials.",
        "unit": {"one": "entry", "many": "entries"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        "accent": "#A85C00",
        "accentDark": "#F5A83C",
        "tiers": False,
        "notes": [
            ["Hours are not tracked on this list.",
             "Wikipedia publishes no runtime for any individual episode — only "
             "an approximate series-level range — and the four .5 releases "
             "redirect to the film they came out of, so they have no runtime "
             "of their own to read either. Seven of the eleven films do have a "
             "verified one, but weighting here is all-or-nothing: a row "
             "without a weight on an otherwise weighted list silently counts "
             "as an hour, so a half-weighted list totals wrong while looking "
             "authoritative. Completeness won and the weights came off."],
            ["The .5 releases are companion cuts, not sequels.",
             "Jackass 2.5, Jackass 3.5, Bad Grandpa.5 and Jackass 4.5 are "
             "assembled from footage left out of the film each is numbered "
             "after. They are here because they are Jackass releases, not "
             "because there are more films than you thought — and every one of "
             "them says so on its row."],
            ["The spin-offs are deliberately absent.",
             "%s share a cast with Jackass, not a show, and none of them is on "
             "this list. The test applied throughout is whether a thing is "
             "Jackass or Jackass people, which is also why Jackass Shark Week "
             "is off it — the source files those broadcasts as episodes of "
             "Discovery's Shark Week — along with Steve-O: Demise and Rise and "
             "A Tribute to Ryan Dunn, documentaries about a cast member rather "
             "than Jackass releases."
             % (", ".join(SPINOFFS[:-1]) + " and " + SPINOFFS[-1])],
            ["The show ran for one year, not three.",
             "Three seasons and twenty-five episodes between October 2000 and "
             "August 2001; the reruns that ran into 2002 are why the dates get "
             "quoted differently elsewhere."],
            "Episodes, air dates and the release roster machine-read from "
            "Wikipedia's List of Jackass episodes and Jackass (franchise); "
            "runtimes probed against each release's own article and Wikidata.",
        ],
        "sections": sections,
    })

    print("wrote %s.json — %d rows, unweighted (%d of %d could be weighted)"
          % (SLUG, len(ids), len(weighable), len(ids)))
    for s in sections:
        print("   %-12s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))
    print("   runtimes on record: %s"
          % ", ".join("%s %d" % (r["t"], r["runtime"]) for r in weighable))
    print("   excluded: %s" % "; ".join("%s (%s)" % (k, v)
                                        for k, v in sorted(EXCLUDED.items())))


if __name__ == "__main__":
    main()
