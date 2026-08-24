#!/usr/bin/env python3
"""Generate properties/kingdom-hearts.json.

    python3 tools/make_kingdomhearts.py

Kingdom Hearts is scattered across a dozen platforms, two of which no longer
sell the game, and the recommended path is release order rather than
chronological order. The order and the priority tiers come from a rundown
written by a friend of the group who has played all of it; that rundown is the
authority here and is followed as given.

Tiers map onto the priority list in that rundown: 1 is "max priority, all
contain crucial story elements", 2 is "medium priority" — worth doing, but the
important scenes can be watched instead — and 3 is the low-priority and
supplemental material.

Platform, version and availability details cross-checked against the Kingdom
Hearts Wiki and Square Enix's own announcements:
  - HD 1.5 + 2.5 ReMIX contains KH Final Mix, Re:Chain of Memories and
    KH II Final Mix and Birth by Sleep Final Mix as playable games, with
    358/2 Days and Re:coded remade as cutscene films.
  - HD 2.8 Final Chapter Prologue contains Dream Drop Distance HD and
    0.2 A Fragmentary Passage, plus Back Cover as a film.
  - Those three collections plus KH III + Re:Mind ship together as
    Kingdom Hearts Collection [I~III], 8 October 2026 on Switch 2, PS5 and
    Xbox Series.  https://www.square-enix.com/kingdomhearts/collection/en-us/
  - Union X Dark Road was delisted from the app stores in August 2024 and
    Missing-Link was cancelled in 2025, so both are watch-a-recap only.
  - Kingdom Hearts IV was dated to late 2027 at D23 2026, for PS5, Xbox
    Series, Switch 2 and PC.  https://press.na.square-enix.com/KINGDOM-HEARTS-IV-RELEASING-IN-LATE-2027

Deliberately no schedule. These are 30-to-40-hour games; a weekly window would
be fiction. Groups get a finish-by date and a linear pace line.
"""
import json
import pathlib

SLUG = "kingdom-hearts"

# Tiers a finish date paces you through — the story spine and the two entries
# you can watch instead of play. Tier 3 is optional and stays out of it.
PACE_TIERS = [1, 2]

# Query strings stripped from the links in the source rundown: the YouTube
# ones carried autoplay-radio parameters and the Drive folder carried a /u/0/
# account index that only resolves for whoever copied it.
ORCH_TOUR = "https://www.youtube.com/watch?v=a8S8ZZPWDDo"
ORCH_TRES = "https://www.youtube.com/watch?v=vHPQkXX50_k"
MISSING_LINK = "https://www.youtube.com/watch?v=3xM9jefq34Y"
VERSUS_TRAILERS = "https://www.youtube.com/watch?v=w0SSeBcWpJc"
VERSUS_DOC = "https://www.youtube.com/watch?v=NQ78JQ_ntYY"
PILOT = "https://www.youtube.com/watch?v=n_23o8Dj524"
PRESS_KIT = "https://drive.google.com/drive/folders/1bnj7MJKgFO1ylxi6w1aq6_neSBMJtcXJ"
FIRST_BREATH = "https://www.kh13.com/news/transcribtion-of-the-kingdom-hearts-orchestra-world-tour-guide/"
OSAKA = ("https://www.kh13.com/news/exclusive-canon-back-story-for-kingdom-hearts-iii"
         "-shown-at-kingdom-hearts-orchestra-world-tour-in-japan")


# Hours per entry, used to size the bars and drive the pace line. The point is
# proportion, not precision: a group with a finish date needs the strip to know
# that Kingdom Hearts II is not the same size as a four-minute trailer.
#
# These are the hours for the *recommended* path, which is the whole trick.
# Re:coded is the three-hour cutscene film, because that is what the rundown
# says to do with it, not the sixteen-hour DS game. The two delisted mobile
# games are recap-watching time. 358/2 Days is the full DS game, because there
# the rundown explicitly says to play the original rather than watch the film.
#
# Games are HowLongToBeat "main story" figures, taken from two aggregations
# that cite them and agree closely; where they differ the midpoint is used.
#   https://gamerant.com/how-long-to-beat-every-kingdom-hearts-game/
#   https://www.thegamer.com/kingdom-hearts-longest-shortest-games/
# Values marked EXACT were read from the source's own metadata rather than
# estimated. Everything else is an estimate and the property says so.
HOURS = {
    # tier 1 — the spine
    "kh1":          28,     # HLTB main: 29 / 28.5
    "com":          20,     # HLTB main: 18 / 18.5, 23 for the Re: remake
    "kh2":          30,     # HLTB main: 32 / 32, 29 for Final Mix
    "days":         26,     # HLTB main: 27 / 26.5 — the DS game, as recommended
    "bbs":          28,     # HLTB main: 28 / 29, 26 for Final Mix
    "ddd":          23,     # HLTB main: 23 / 23
    "ux1":           2,     # recap; Back Cover covers this material in 80 min
    "fragmentary":   3,     # HLTB main: 3 / 2.5
    "kh3":          29,     # HLTB main: 29 / 29
    "remind":        4,     # HLTB main: 4
    "ux2":           3,     # recap, estimated — no film exists for the second half
    "darkroad":      2,     # recap, estimated
    "kh4":           0,     # unreleased: weightless until it exists, so it can
                            # not drag a group's pace line for a year
    # tier 2 — watchable instead
    "recoded":       3,     # EXACT: the HD cutscene film runs 2h58m
    "mom":          10,     # HLTB main: 10 / 9.5
    # tier 3 — supplemental
    "firstbreath":   0.5,   # transcription, estimated read time
    "osaka":         0.25,  # short article, estimated read time
    "orch-tour":     1.2,   # EXACT: 4340s
    "orch-tres":     1.85,  # EXACT: 6658s
    "tweewy":       25,     # HLTB main for the DS original
    "missinglink":   0.08,  # EXACT: 279s
    "vr":            0.75,  # short PSVR piece, estimated
    "manga":        10,     # 16 volumes (4 + 2 + 10), estimated at ~35 min each
    "days-manga":    3,     # 5 volumes
    "novels":       13,     # the first three games' novels, estimated
    "ultimania":     2,     # coffee table book, estimated browse
    "charfiles":     1.5,   # coffee table book, estimated browse
    "versus":        0.5,   # EXACT: 1839s
    "versus-doc":    0.42,  # EXACT: 1503s
    "presskit":      0.5,   # estimated browse
    "pilot":         0.19,  # EXACT: 679s
}


def it(key, title, fmt, note="", url="", star=0):
    assert key in HOURS, "no weight for %r" % key
    x = {"id": "kh-" + key, "t": title, "n": fmt, "w": HOURS[key]}
    if note:
        x["note"] = note
    if url:
        x["url"] = url
    if star:
        x["star"] = star
    return x


SECTIONS = [
    {
        "id": "ps2", "tier": 1, "title": "The PS2 trilogy",
        "sub": "three games, in this order, no exceptions",
        "items": [
            it("kh1", "Kingdom Hearts", "PS2",
               "It starts with a boy looking for his friends. Play the Final Mix version."),
            it("com", "Chain of Memories", "GBA · PS2",
               "Straight on from the first game, with card-based combat. "
               "Re:Chain of Memories is the version to play."),
            it("kh2", "Kingdom Hearts II", "PS2",
               "Back to action RPG combat, and most people's favourite in the series. "
               "Final Mix.", star=2),
        ],
    },
    {
        "id": "handheld", "tier": 1, "title": "The handhelds",
        "sub": "a side story and a prequel · both load-bearing",
        "items": [
            it("days", "358/2 Days", "DS",
               "Set between the last two. Play the DS original — the version in the "
               "collections is cutscenes only."),
            it("bbs", "Birth by Sleep", "PSP",
               "Prequel to the first game: three keyblade wielders the whole saga "
               "turns on. Final Mix."),
        ],
    },
    {
        "id": "recoded", "tier": 2, "title": "Re:coded",
        "sub": "the one you can watch instead of play",
        "items": [
            it("recoded", "Re:coded", "DS",
               "Watch the cutscene film in the collections. Only the ending matters."),
        ],
    },
    {
        "id": "ddd", "tier": 1, "title": "Dream Drop Distance",
        "sub": "the setup for everything III pays off",
        "items": [
            it("ddd", "Dream Drop Distance", "3DS",
               "Sequel to KH2, and most of the groundwork for KH3. You play as both "
               "Sora and Riku."),
        ],
    },
    {
        "id": "concert", "tier": 3, "title": "Story in the concert programmes",
        "sub": "two short reads · yes, really",
        "items": [
            it("firstbreath", "Secret Story: First Breath", "WEB",
               "Read it after Dream Drop Distance, before 0.2.", FIRST_BREATH),
            it("osaka", "Osaka orchestra backstory", "WEB",
               "Read it before Kingdom Hearts III.", OSAKA),
        ],
    },
    {
        "id": "bridge", "tier": 1, "title": "Before the finale",
        "sub": "a century of backstory, then a three-hour prologue",
        "items": [
            it("ux1", "Union Cross, part 1", "MOBILE",
               "Delisted — watch a recap. Back Cover, in the 2.8 collection, covers "
               "the first half."),
            it("fragmentary", "0.2 Birth by Sleep – A Fragmentary Passage", "PS4",
               "About three hours. Set after Birth by Sleep, just before the end of KH1."),
        ],
    },
    {
        "id": "kh3", "tier": 1, "title": "Kingdom Hearts III",
        "sub": "the payoff, plus the DLC that finishes it",
        "items": [
            it("kh3", "Kingdom Hearts III", "PS4",
               "Every prior game, tied together. This series' Endgame.", star=2),
            it("remind", "Re:Mind", "DLC", "Not optional despite being paid DLC."),
        ],
    },
    {
        "id": "after", "tier": 1, "title": "After III",
        "sub": "where Kingdom Hearts IV is being set up",
        "items": [
            it("ux2", "Union Cross, part 2", "MOBILE",
               "Pick the recap back up at the Dandelions arc. Set a century before KH1."),
            it("darkroad", "Dark Road", "MOBILE",
               "Delisted — watch a recap. Xehanort's backstory, and it will matter in KH4."),
        ],
    },
    {
        "id": "mom", "tier": 2, "title": "Melody of Memory",
        "sub": "a rhythm game with one scene that counts",
        "items": [
            it("mom", "Melody of Memory", "PS4",
               "The ending leads into KH4 and you can just watch that part. "
               "The game does own, though."),
        ],
    },
    {
        "id": "kh4", "tier": 1, "title": "Kingdom Hearts IV",
        "sub": "late 2027 · nothing to check off yet",
        "items": [
            it("kh4", "Kingdom Hearts IV", "TBA",
               "Late 2027 on PS5, Xbox Series, Switch 2 and PC."),
        ],
    },
    {
        "id": "supp", "tier": 3, "title": "Supplemental",
        "sub": "none of it required",
        "items": [
            it("orch-tour", "Kingdom Hearts Orchestra – World Tour", "CONCERT",
               "2017–2019.", ORCH_TOUR),
            it("orch-tres", "Kingdom Hearts Orchestra – World of Tres", "CONCERT",
               "2019.", ORCH_TRES),
            it("tweewy", "The World Ends With You", "DS",
               "Its cast turns up in Dream Drop Distance. There is an anime adaptation "
               "if you would rather watch it."),
            it("missinglink", "Missing-Link", "VIDEO",
               "Cancelled before release; the events are likely folded into KH4. "
               "Opening video.", MISSING_LINK),
            it("vr", "Kingdom Hearts VR Experience", "PSVR", "No new story."),
            it("manga", "Kingdom Hearts, Chain of Memories and KH II manga", "MANGA",
               "Not canon, and not very good."),
            it("days-manga", "358/2 Days manga", "MANGA",
               "Not canon, but very good — fans treat it as head canon."),
            it("novels", "Kingdom Hearts light novels", "NOVELS",
               "Adapt the first three games. No idea if they're any good."),
            it("ultimania", "The Story Before Kingdom Hearts III", "BOOK",
               "Ultimania coffee table book."),
            it("charfiles", "Kingdom Hearts Character Files", "BOOK",
               "Coffee table book."),
            it("versus", "Final Fantasy Versus XIII trailers", "VIDEO",
               "2006–2015.", VERSUS_TRAILERS),
            it("versus-doc", "The Undying Legacy of Final Fantasy Versus XIII", "VIDEO",
               "", VERSUS_DOC),
            it("presskit", "Kingdom Hearts 1 press kit", "FILES",
               "Original designs and art.", PRESS_KIT),
            it("pilot", "Cancelled TV series pilot animatic", "VIDEO", "", PILOT),
        ],
    },
]


def main():
    ids = [x["id"] for s in SECTIONS for x in s["items"]]
    total = len(ids)
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate item ids")

    tiers = {1: 0, 2: 0, 3: 0}
    for s in SECTIONS:
        tiers[s["tier"]] += len(s["items"])

    # the rundown's max-priority list, one for one
    assert tiers[1] == 13, tiers[1]
    assert tiers[2] == 2, tiers[2]
    assert total == 31, total

    # a weight declared but never attached to an item is a silent typo
    used = {x["id"][3:] for s in SECTIONS for x in s["items"]}
    assert used == set(HOURS), (used ^ set(HOURS))
    hours = sum(x["w"] for s in SECTIONS for x in s["items"])
    spine = sum(x["w"] for s in SECTIONS if s["tier"] == 1 for x in s["items"])
    paced = sum(x["w"] for s in SECTIONS if s["tier"] in PACE_TIERS
                for x in s["items"])

    prop = {
        "slug": SLUG,
        "title": "Kingdom Hearts",
        "subtitle": "every game, in release order",
        "kind": "games",
        "popularity": 68,
        "year": "2002–2027",
        "blurb": "%d entries in release order, about %d hours if you do the lot. "
                 "Tiered by what the story actually needs." % (total, round(hours)),
        "unit": {"one": "entry", "many": "entries"},
        "verb": {"base": "play", "past": "played", "ing": "playing"},
        "itemOrder": "number-first",
        # The finish date paces you through tiers 1 and 2 only. Nobody should be
        # told they are late because they have not read the coffee table books.
        # A checkbox on the page puts tier 3 back for anyone who wants it.
        "paceTiers": PACE_TIERS,
        "paceLabel": "supplemental",
        "accent": "#3B4CA8",
        "accentDark": "#8A98E8",
        "tiers": True,
        "notes": [
            ["Release order, not chronological.", "The series jumps around in time "
             "constantly and every prequel is written assuming you have played what "
             "came before it. Play them in the order they came out."],
            ["Tiers.", "1 is the story spine — play those in the order listed. 2 is "
             "worth doing, but you can watch the scenes that matter instead. 3 is "
             "concert programmes, manga, books and videos, none of it required."],
            ["Where to play it.", "Everything from Kingdom Hearts through Re:Mind is "
             "in three collections — HD 1.5 + 2.5 ReMIX, HD 2.8 Final Chapter "
             "Prologue, and Kingdom Hearts III + Re:Mind — on PS4, PS5, Xbox One and "
             "Series, PC and Switch 2. Play the Final Mix versions in those "
             "collections. 358/2 Days and Re:coded are cutscene films there rather "
             "than playable games, which is fine for Re:coded and a real loss for "
             "358/2 Days."],
            ["The mobile games.", "Union Cross — officially Union χ [Cross] — and Dark "
             "Road were pulled from the app "
             "stores and cannot be played any more, so watch a cutscene compilation "
             "or a detailed recap. Back Cover, in the 2.8 collection, covers the "
             "first half of Union Cross; the second half is on YouTube only."],
            ["Why the bars are different sizes.", "Each mark is as wide as the "
             "thing takes, so a forty-hour game is not one tick next to a "
             "four-minute trailer. A finish-by date paces you through the hours "
             "rather than the entries, which is the only way the line means "
             "anything here. The spine alone is about %d hours; everything on "
             "this page is about %d." % (round(spine), round(hours))],
            ["Supplemental does not count toward a finish date.", "The timeline "
             "covers tiers 1 and 2 — about %d hours. The supplemental tier is "
             "optional, so it never makes anyone late, and ticking any of it is "
             "pure credit. If you would rather be paced through the whole %d "
             "hours, there is a checkbox under the bar." % (round(paced), round(hours))],
            ["The hours.", "Games use HowLongToBeat's main-story figures. Where "
             "the rundown says to watch something instead of playing it, the "
             "number is how long that takes — Re:coded is its three-hour "
             "cutscene film, not the sixteen-hour DS game. Video lengths are "
             "exact; books, manga and recaps are estimates. Kingdom Hearts IV "
             "weighs nothing until it exists."],
            "Order and priorities from a rundown written by a friend of the group who "
            "has played all of it. Platform, version and availability details "
            "cross-checked against the Kingdom Hearts Wiki and Square Enix's "
            "announcements.",
        ],
        "sections": SECTIONS,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json" % SLUG)
    print("  %d sections, %d entries, %.1f hours" % (len(SECTIONS), total, hours))
    print("  tier 1 spine: %.1f hours" % spine)
    print("  tier 1: %d   tier 2: %d   tier 3: %d" % (tiers[1], tiers[2], tiers[3]))
    for s in SECTIONS:
        print("   T%d  %-34s %2d  %6.1fh"
              % (s["tier"], s["title"][:34], len(s["items"]),
                 sum(x["w"] for x in s["items"])))


if __name__ == "__main__":
    main()
