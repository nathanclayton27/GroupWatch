#!/usr/bin/env python3
"""Generate properties/civil-war.json.

    python3 tools/make_civilwar.py

The 2006 event in interleaved reading order, which is the part that is actually
hard to hold in your head: seven issues of the main series with forty-odd
tie-ins slotted between them.

Order taken from the How To Love Comics guide, which lists it issue by issue,
cross-checked against comicbookreadingorders.com for the prelude and the
Spider-Man run. Where the two disagree only on placing New Avengers: Illuminati
this follows comicbookreadingorders and puts it after ASM #531.

Which tie-ins are essential and which are skippable follows those same guides:
Civil War #1–7 carries the whole plot, Front Line and the Spider-Man issues are
the two tie-ins everyone agrees on, and the rest is there if you follow that
character. Anything the sources call skippable is marked optional rather than
dropped, so the order stays complete.

Notes say what an entry is, never what happens in it. That matters more here
than anywhere: this is an event with a widely-known ending, and the point of a
reading list is to be read first. One consequence — the Fallen Son series is
listed under its short name, because its subtitle gives away the ending.
"""
import json
import pathlib

SLUG = "civil-war"

S_ASM = "https://www.marvel.com/comics/series/454/the_amazing_spiderman_1999_2013"
S_CW  = "https://www.marvel.com/comics/series/1067/civil_war_2006_-_2007"
S_FL  = "https://www.marvel.com/comics/series/1109/civil_war_front_line_2006_2007"

# Every section of the event proper points at the two series that run its whole
# length. The tie-ins are two dozen different books and Marvel gives each an
# arbitrary id, so those are found by title and year in Marvel Unlimited — the
# notes say so.
EVENT_LINKS = [{"label": "Civil War", "url": S_CW},
               {"label": "Front Line", "url": S_FL}]


# Every series this list touches, by its slug on marvel.com. Resolved against
# tools/data/marvel_series_index.json — Marvel's whole A-Z series index, saved
# locally — so a wrong slug fails the build rather than shipping a dead link.
SERIES_SLUG = {
    "Civil War": "civil_war_2006_2007",
    "Civil War: Front Line": "civil_war_front_line_2006_2007",
    "Amazing Spider-Man": "the_amazing_spiderman_1999_2013",
    "New Warriors": "new_warriors_2005",
    "New Avengers: Illuminati": "new_avengers_illuminati_2006_2007",
    "Fantastic Four": "fantastic_four_1998_2012",
    "She-Hulk": "shehulk_2005_2009",
    "Wolverine": "wolverine_2003_2009",
    "Thunderbolts": "thunderbolts_2006_2012",
    "X-Factor": "xfactor_2005_2013",
    "New Avengers": "new_avengers_2004_2010",
    "Civil War: X-Men": "civil_war_xmen_2006",
    "Cable & Deadpool": "cable_and_deadpool_2004_2008",
    "Civil War: Young Avengers & Runaways": "civil_war_young_avengers_and_runaways_2006",
    "Black Panther": "black_panther_2005_2008",
    "Ms. Marvel": "ms_marvel_2006_2010",
    "Heroes for Hire": "heroes_for_hire_2006_2007",
    "Captain America": "captain_america_2004_2011",
    "Iron Man": "the_invincible_iron_man_2004_2008",
    "Punisher War Journal": "punisher_war_journal_2006_2008",
    "Civil War: War Crimes": "civil_war_war_crimes_1_2006",
    "Iron Man/Captain America: Casualties of War":
        "iron_mancaptain_america_casualties_of_war_2006",
    "Civil War: The Return": "civil_war_the_return_1_2007",
    "Blade": "blade_2006_2007",
    "Ghost Rider": "ghost_rider_2006_2009",
    "Moon Knight": "moon_knight_2006_2009",
    "Winter Soldier: Winter Kills": "winter_soldier_winter_kills_1_2006",
    "Civil War: The Initiative": "civil_war_the_initiative_1_2007",
    "Civil War: The Confession": "civil_war_the_confession_1_2007",
    "Civil War: Fallen Son": "fallen_son_the_death_of_captain_america_2007",
    "Civil War: Battle Damage Report": "civil_war_battle_damage_report_2007",
    "Mighty Avengers": "the_mighty_avengers_2007_2010",
    "Avengers: The Initiative": "avengers_the_initiative_2007_2010",
    "Iron Man: Director of S.H.I.E.L.D.": "iron_man_director_of_shield_2008",
    "Omega Flight": "omega_flight_2007",
    "The Order": "the_order_2007_2008",
    "Sub-Mariner": "submariner_2007",
}

_INDEX = json.loads(
    (pathlib.Path(__file__).resolve().parent / "data" / "marvel_series_index.json")
    .read_text(encoding="utf-8"))
SERIES_URL = {}
for _name, _slug in SERIES_SLUG.items():
    assert _slug in _INDEX, "%r: %s is not in the Marvel index" % (_name, _slug)
    SERIES_URL[_name] = "https://www.marvel.com/comics/series/%s/%s" % (_INDEX[_slug], _slug)

# A header carries the series in its own section, biggest first, capped so it
# stays a header rather than a directory. Twelve is the smallest cap under
# which every mapped series still appears somewhere: at ten, Blade and
# Winter Soldier: Winter Kills are never reachable from any header.
HEADER_LINKS = 12


def it(key, title, num, note="", star=0, w=1, opt=0, url=""):
    x = {"id": "cw-" + key, "t": title, "n": num, "w": w}
    if note:
        x["note"] = note
    if star:
        x["star"] = star
    if opt:
        x["opt"] = 1
    if url:
        x["url"] = url
    return x


def asm(n, note="", star=0):
    return it("asm-%d" % n, "Amazing Spider-Man", "#%d" % n, note, star)


def war(n, note="", star=2):
    return it("war-%d" % n, "Civil War", "#%d" % n, note, star)


def fl(n, note="", star=1):
    return it("fl-%d" % n, "Civil War: Front Line", "#%d" % n, note, star)


SECTIONS = [
    {
        "id": "road", "tier": 1, "title": "The Road to Civil War",
        "sub": "the six issues that set it up · 2006",
        "open": True,
        "intro": "Collected as Civil War: The Road to Civil War, minus the New "
                 "Warriors issues. Skipping the prelude and starting at Civil "
                 "War #1 works, but these are where the positions are staked out.",
        "items": [
            it("newwarriors", "New Warriors", "#1–6",
               "The reality-TV miniseries whose cast sets everything off. Not "
               "collected with the rest of the prelude.", w=6, opt=1),
            asm(529, "The Iron Spider suit", 1),
            asm(530, "Road to Civil War"),
            asm(531, "Road to Civil War"),
            it("illuminati", "New Avengers: Illuminati", "#1",
               "The one prelude issue everyone names as essential", 2),
            it("ff-536", "Fantastic Four", "#536", "Road to Civil War"),
            it("ff-537", "Fantastic Four", "#537", "Road to Civil War"),
        ],
    },
    {
        "id": "war12", "tier": 1, "title": "Civil War #1–2",
        "sub": "the opening, with what reads between",
        "intro": "Civil War #1–7 carries the entire plot on its own. Everything "
                 "between the numbered issues is a tie-in: read the ones whose "
                 "characters you follow, and treat the rest as optional. The "
                 "sources agree on two exceptions worth reading whoever you "
                 "are — Front Line and the Spider-Man issues.",
        "items": [
            war(1),
            it("shehulk-8", "She-Hulk", "#8", "", opt=1),
            it("wolv-42", "Wolverine", "#42", "", opt=1),
            asm(532, "", 1),
            fl(1, "Reporters covering the war from street level"),
            war(2),
            it("tbolts-103", "Thunderbolts", "#103", "", opt=1),
            fl(2),
            it("xfactor-8", "X-Factor", "#8", "", opt=1),
            it("na-21", "New Avengers", "#21"),
            it("wolv-43", "Wolverine", "#43", "", opt=1),
            asm(533, "", 1),
            it("ff-538", "Fantastic Four", "#538"),
            fl(3),
            it("tbolts-104", "Thunderbolts", "#104", "", opt=1),
            it("xmen-1", "Civil War: X-Men", "#1",
               "More to do with the aftermath of House of M than with this", opt=1),
        ],
    },
    {
        "id": "war34", "tier": 1, "title": "Civil War #3–4",
        "sub": "the middle, where the tie-ins are thickest",
        "items": [
            war(3),
            it("cd-30", "Cable & Deadpool", "#30", "", opt=1),
            it("yar-1", "Civil War: Young Avengers & Runaways", "#1", "", opt=1),
            fl(4),
            it("xfactor-9", "X-Factor", "#9", "", opt=1),
            it("na-22", "New Avengers", "#22"),
            it("bp-18", "Black Panther", "#18", "", opt=1),
            it("wolv-44", "Wolverine", "#44", "", opt=1),
            asm(534, "", 1),
            it("ff-539", "Fantastic Four", "#539"),
            fl(5),
            it("msm-6", "Ms. Marvel", "#6", "", opt=1),
            it("tbolts-105", "Thunderbolts", "#105", "", opt=1),
            it("xmen-2", "Civil War: X-Men", "#2", "", opt=1),
            it("hfh-1", "Heroes for Hire", "#1", "", opt=1),
            it("na-23", "New Avengers", "#23"),
            it("wolv-45", "Wolverine", "#45", "", opt=1),
            it("yar-2", "Civil War: Young Avengers & Runaways", "#2", "", opt=1),
            it("cd-31", "Cable & Deadpool", "#31", "", opt=1),
            it("msm-7", "Ms. Marvel", "#7", "", opt=1),
            it("xmen-3", "Civil War: X-Men", "#3", "", opt=1),
            war(4),
            it("wolv-46", "Wolverine", "#46", "", opt=1),
            it("hfh-2", "Heroes for Hire", "#2", "", opt=1),
            it("yar-3", "Civil War: Young Avengers & Runaways", "#3", "", opt=1),
            fl(6),
            it("cap-22", "Captain America", "#22",
               "One half of the argument, in his own book", 2),
            it("cd-32", "Cable & Deadpool", "#32", "", opt=1),
            asm(535, "", 1),
            it("ff-540", "Fantastic Four", "#540"),
            fl(7),
            it("xmen-4", "Civil War: X-Men", "#4", "", opt=1),
            it("msm-8", "Ms. Marvel", "#8", "", opt=1),
            it("wolv-47", "Wolverine", "#47", "", opt=1),
            it("hfh-3", "Heroes for Hire", "#3", "", opt=1),
            it("cap-23", "Captain America", "#23", "", 2),
            it("na-24", "New Avengers", "#24"),
        ],
    },
    {
        "id": "war5", "tier": 1, "title": "Civil War #5",
        "sub": "the turn",
        "items": [
            war(5),
            it("yar-4", "Civil War: Young Avengers & Runaways", "#4", "", opt=1),
            it("im-13", "Iron Man", "#13", "The other half of the argument", 2),
            it("na-25", "New Avengers", "#25"),
            it("pwj-1", "Punisher War Journal", "#1",
               "Expands a genuinely good role in the main series", 1),
            fl(8),
            asm(536, "", 1),
            it("bp-22", "Black Panther", "#22", "", opt=1),
            it("cap-24", "Captain America", "#24", "", 2),
            it("warcrimes", "Civil War: War Crimes", "#1", "", opt=1),
            it("im-14", "Iron Man", "#14", "", 2),
            it("ff-541", "Fantastic Four", "#541"),
            it("bp-23", "Black Panther", "#23", "", opt=1),
            it("pwj-2", "Punisher War Journal", "#2", "", 1),
        ],
    },
    {
        "id": "war67", "tier": 1, "title": "Civil War #6–7",
        "sub": "the end",
        "items": [
            war(6),
            it("casualties", "Iron Man/Captain America: Casualties of War", "#1",
               "The two of them, in a room. Often named the best single tie-in.", 2),
            fl(9),
            fl(10),
            asm(537, "", 1),
            it("ff-542", "Fantastic Four", "#542"),
            it("thereturn", "Civil War: The Return", "#1", "", opt=1),
            it("pwj-3", "Punisher War Journal", "#3", "", 1),
            it("bp-24", "Black Panther", "#24", "", opt=1),
            war(7),
            asm(538, "", 1),
            fl(11, "The last chapter, and the one people argue about"),
            it("bp-25", "Black Panther", "#25", "", opt=1),
            it("blade-5", "Blade", "#5", "", opt=1),
            it("ghostrider", "Ghost Rider", "#8–11", "", w=4, opt=1),
            it("moonknight", "Moon Knight", "#7–9", "", w=3, opt=1),
            it("winterkills", "Winter Soldier: Winter Kills", "#1",
               "A quiet one, and better than it needs to be", 1),
            it("wolv-48", "Wolverine", "#48", "", opt=1),
        ],
    },
    {
        "id": "after", "tier": 2, "title": "Straight after",
        "sub": "the four that close it out",
        "intro": "These are the epilogue, and they are where the event's "
                 "consequences get stated rather than implied. Read them before "
                 "moving on to anything that follows.",
        "items": [
            it("initiative", "Civil War: The Initiative", "#1",
               "Sets up the status quo the whole line ran on next", 1),
            it("confession", "Civil War: The Confession", "#1",
               "A two-hander, and the best-regarded thing to come out of the event",
               2),
            it("fallenson", "Civil War: Fallen Son", "#1–5",
               "Five one-shots, each by a different artist", w=5),
            it("bdr", "Civil War: Battle Damage Report", "#1",
               "A file-format summary of where everyone ended up", opt=1),
        ],
    },
    {
        "id": "follow", "tier": 3, "title": "What it turned into",
        "sub": "the runs that came directly out of it",
        "intro": "Not part of the event, and not a list to finish — this is "
                 "where to go if a particular thread interested you.",
        "items": [
            it("f-mighty", "Mighty Avengers", "#1–6", "Bendis, the licensed team",
               w=6),
            it("f-init", "Avengers: The Initiative", "#1–3", "The other side of it",
               w=3),
            it("f-cap", "Captain America", "#25–30",
               "Brubaker's run continues straight through", 1, w=6),
            it("f-iron", "Iron Man: Director of S.H.I.E.L.D.", "#15–18", "", w=4),
            it("f-ff", "Fantastic Four", "#543–550", "", w=8),
            it("f-omega", "Omega Flight", "#1–5", "", w=5),
            it("f-order", "The Order", "#1–4", "", w=4),
            it("f-subm", "Sub-Mariner", "#1–6", "", w=6),
            it("f-tbolts", "Thunderbolts", "#110–115",
               "Warren Ellis takes over, and it's the best of these", 1, w=6),
        ],
    },
]


def main():
    for sec in SECTIONS:
        weight, order = {}, []
        for x in sec["items"]:
            if x["t"] not in SERIES_URL:
                continue
            if x["t"] not in weight:
                order.append(x["t"])
            weight[x["t"]] = weight.get(x["t"], 0) + x["w"]
        keep = set(sorted(weight, key=lambda t: -weight[t])[:HEADER_LINKS])
        links = [{"label": t, "url": SERIES_URL[t]} for t in order if t in keep]
        if links:
            sec["links"] = links
        missing = {x["t"] for x in sec["items"]} - set(SERIES_URL)
        assert not missing, "no slug for %s" % sorted(missing)

    ids = [x["id"] for s in SECTIONS for x in s["items"]]
    if len(ids) != len(set(ids)):
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        raise SystemExit("duplicate item ids: %s" % dupes[:10])
    total = len(ids)
    issues = sum(x["w"] for s in SECTIONS for x in s["items"])

    # the spine must be complete and in order
    main_series = [x["n"] for s in SECTIONS for x in s["items"] if x["t"] == "Civil War"]
    assert main_series == ["#%d" % n for n in range(1, 8)], main_series
    front = [x["n"] for s in SECTIONS for x in s["items"]
             if x["t"] == "Civil War: Front Line"]
    assert front == ["#%d" % n for n in range(1, 12)], front
    spidey = [x["n"] for s in SECTIONS for x in s["items"]
              if x["t"] == "Amazing Spider-Man"]
    assert spidey == ["#%d" % n for n in range(529, 539)], spidey

    core = sum(x["w"] for s in SECTIONS if s["tier"] in (1, 2)
               for x in s["items"] if not x.get("opt"))
    optional = sum(x["w"] for s in SECTIONS for x in s["items"] if x.get("opt"))

    prop = {
        "slug": SLUG,
        "title": "Civil War",
        "subtitle": "the 2006 event, in reading order",
        "kind": "comics",
        "order": 12,
        "year": "2006–07",
        "blurb": "Seven issues of main series and forty-odd tie-ins, interleaved "
                 "in the order they're meant to be read.",
        "unit": {"one": "entry", "many": "entries"},
        "weightUnit": {"one": "issue", "many": "issues"},
        "verb": {"base": "read", "past": "read", "ing": "reading"},
        "accent": "#4A6B8A",
        "accentDark": "#8FB6D6",
        "tiers": True,
        "paceTiers": [1, 2],
        "paceLabel": "the follow-on runs",
        "notes": [
            ["Three ways to read it.", "Civil War #1–7 alone is a complete story, "
             "start to finish. Adding the Road to Civil War prelude gives you the "
             "positions before the argument starts. Everything else is a tie-in, "
             "and the honest advice from every guide is the same: read the ones "
             "whose characters you already follow."],
            ["What's marked optional.", "The %d issues tagged optional are the "
             "ones the guides call skippable. They're left in place rather than "
             "removed so the interleaved order stays intact — if you're reading a "
             "character's whole run, you'll want to know where their issues sit." % optional],
            ["The two everyone agrees on.", "Front Line runs the whole length of "
             "the event from a reporter's point of view, and the Spider-Man "
             "issues put a character at the centre of it rather than at the edge. "
             "Neither is optional in any guide."],
            ["No spoilers.", "The notes say what an entry is, never what happens "
             "in it — which takes some doing for an event this famous. Fallen Son "
             "is listed under its short name for the same reason; its subtitle "
             "gives away the ending."],
            ["Tiers.", "1 is the event itself in order. 2 is the four issues that "
             "close it out. 3 is the runs that came out of it, which aren't part "
             "of the event and stay out of the finish date."],
            "Order from the How To Love Comics guide, which lists it issue by "
            "issue, cross-checked against comicbookreadingorders.com for the "
            "prelude and the Spider-Man issues.",
        ],
        "sections": SECTIONS,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json" % SLUG)
    print("  %d sections, %d entries, %d issues" % (len(SECTIONS), total, issues))
    print("  core: %d issues   marked optional: %d" % (core, optional))
    for s in SECTIONS:
        o = sum(1 for x in s["items"] if x.get("opt"))
        print("   T%d  %-28s %3d entries %4d issues  (%d optional)"
              % (s["tier"], s["title"][:28], len(s["items"]),
                 sum(x["w"] for x in s["items"]), o))


if __name__ == "__main__":
    main()
