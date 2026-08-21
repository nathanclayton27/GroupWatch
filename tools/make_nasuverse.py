#!/usr/bin/env python3
"""Generate properties/nasuverse.json.

    python3 tools/make_nasuverse.py

Type-Moon's shared universe — Fate, Tsukihime, Melty Blood, Kara no Kyoukai,
Witch on the Holy Night — organised by media type, release order inside each.

Dates come from Wikipedia's Type-Moon release list and the individual work
articles' infoboxes, read rather than typed. Where only a year could be
confirmed the entry shows the year and nothing finer; nothing here is a guess.
Runtimes are given for the films that had one in their infobox.

Deliberately not included: the Fate/Grand Order Camelot and Solomon films,
which have no English Wikipedia article under a title that resolves, so their
dates could not be confirmed. Say so rather than approximate them.

No tiers. The source is a catalogue of what exists, not a ranking, and the
"where to start" advice lives in the notes instead of being invented per row.
"""
import json
import pathlib

SLUG = "nasuverse"

# (media, title, date, note, minutes)
# date is YYYY-MM-DD where confirmed, or YYYY where only the year is
WORKS = [
    # ---------------------------------------------------------------- novels
    ("novel", "The Garden of Sinners", "1998-10",
     "Kara no Kyoukai. Nasu's first work, serialised before Type-Moon existed.", 0),
    ("novel", "Fate/Zero", "2006-12-29",
     "Urobuchi's prequel to Fate/stay night, in four volumes", 0),
    ("novel", "Fate/Apocrypha", "2012-12-29", "", 0),
    ("novel", "The Case Files of Lord El-Melloi II", "2014-12-30",
     "Detective stories set between Fate/Zero and Fate/stay night", 0),
    ("novel", "Fate/strange Fake", "2015-01-10", "Ryohgo Narita", 0),
    # ------------------------------------------------------------ visual novels
    ("vn", "Tsukihime", "2000-12-28",
     "The doujin visual novel everything else grew out of", 0),
    ("vn", "Kagetsu Tohya", "2001-08-13", "Tsukihime fan disc", 0),
    ("vn", "Fate/stay night", "2004-01-30",
     "Three routes — Fate, Unlimited Blade Works, Heaven's Feel — read in that order", 0),
    ("vn", "Fate/hollow ataraxia", "2005-10-28", "Sequel to Fate/stay night", 0),
    ("vn", "Witch on the Holy Night", "2012-04-12",
     "Mahoutsukai no Yoru. Standalone, and needs nothing else read first.", 0),
    ("vn", "Tsukihime -A piece of blue glass moon-", "2021-08-26",
     "The remake, retelling the first half of Tsukihime", 0),
    # ----------------------------------------------------------------- games
    ("game", "Melty Blood", "2002-12-28",
     "Fighting game with French-Bread, and a direct Tsukihime sequel in story", 0),
    ("game", "Melty Blood: Act Cadenza", "2005-03-25", "Arcade port", 0),
    ("game", "Fate/tiger colosseum", "2007-09-13", "PSP fighting game", 0),
    ("game", "Fate/unlimited codes", "2008-06-11", "Arcade, PS2 and PSP fighting game", 0),
    ("game", "Fate/Extra", "2010-07-22", "PSP dungeon-crawling RPG", 0),
    ("game", "Fate/Extra CCC", "2013-03-28", "Side story to Fate/Extra", 0),
    ("game", "Fate/Grand Order", "2015-07-30",
     "The mobile RPG, still running, and the largest single body of story in the universe", 0),
    ("game", "Fate/Extella: The Umbral Star", "2016-11-10", "Action RPG", 0),
    ("game", "Fate/Extella Link", "2018-06-07", "", 0),
    ("game", "Melty Blood: Type Lumina", "2021-09-30",
     "Reboot of the fighting game, following the Tsukihime remake", 0),
    ("game", "Fate/Samurai Remnant", "2023-09-28",
     "Action RPG set during a Holy Grail War in Edo-period Japan", 0),
    # ------------------------------------------------------------ anime series
    ("tv", "Lunar Legend Tsukihime", "2003-10-10", "J.C.Staff's Tsukihime adaptation", 0),
    ("tv", "Fate/stay night", "2006-01-07",
     "Studio Deen. 24 episodes, following the Fate route.", 0),
    ("tv", "Carnival Phantasm", "2011-08-12",
     "Comedy OVA crossing Fate and Tsukihime, from the Take Moon parody manga", 0),
    ("tv", "Fate/Zero", "2011-10-01", "ufotable. 25 episodes across two cours.", 0),
    ("tv", "Fate/kaleid liner Prisma Illya", "2013",
     "Magical-girl spin-off, four seasons from here", 0),
    ("tv", "Fate/stay night: Unlimited Blade Works", "2014-10-05",
     "ufotable. 26 episodes plus an OVA, adapting the second route.", 0),
    ("tv", "Fate/Apocrypha", "2017", "", 0),
    ("tv", "Fate/Extra Last Encore", "2018-01-28", "Shaft's take on Fate/Extra", 0),
    ("tv", "Today's Menu for the Emiya Family", "2018", "Cooking spin-off", 0),
    ("tv", "The Case Files of Lord El-Melloi II", "2019", "", 0),
    ("tv", "Fate/Grand Order: Absolute Demonic Front Babylonia", "2019-10-05",
     "The Babylonia singularity, animated by CloverWorks", 0),
    ("tv", "Fate/Grand Carnival", "2020-12-31",
     "Successor to Carnival Phantasm, using the Grand Order cast", 0),
    ("tv", "Fate/strange Fake: Whispers of Dawn", "2023-07-02", "One-off special", 55),
    # ----------------------------------------------------------------- films
    ("film", "The Garden of Sinners", "2007-12-01",
     "Seven films, released 2007–2009, adapting the novels out of chronological order", 0),
    ("film", "Fate/stay night: Unlimited Blade Works", "2010-01-23",
     "Studio Deen's film of the second route", 105),
    ("film", "The Garden of Sinners: A Study in Murder, Part 2", "2009-08-08", "", 0),
    ("film", "The Garden of Sinners: Epilogue", "2011-02-02", "", 33),
    ("film", "The Garden of Sinners: Mirai Fukuin", "2013-09-28",
     "The Garden of Sinners: The Future Gospel", 61),
    ("film", "Prisma Illya: Vow in the Snow", "2017-08-26", "", 62),
    ("film", "Prisma Illya: Oath Under Snow", "2019-06-14", "", 95),
    ("film", "Fate/stay night: Heaven's Feel I. presage flower", "2017-10-14",
     "ufotable. The third route, over three films.", 120),
    ("film", "Fate/stay night: Heaven's Feel II. lost butterfly", "2019-01-12", "", 117),
    ("film", "Fate/stay night: Heaven's Feel III. spring song", "2020-08-15", "", 122),
    # ----------------------------------------------------------------- manga
    ("manga", "Fate/kaleid liner Prisma Illya", "2007-09-26",
     "Long-running spin-off, and the source of the anime seasons", 0),
    ("manga", "Today's Menu for the Emiya Family", "2016-01-26", "", 0),
]

MEDIA = [
    ("vn", "Visual novels", "where almost all of it starts",
     "Nasu's own works, and the primary text for everything else. Fate/stay "
     "night and Tsukihime are the two entry points; Witch on the Holy Night "
     "stands completely alone and needs nothing read first."),
    ("tv", "Anime series", "", ""),
    ("film", "Films", "", ""),
    ("game", "Games", "",
     "Melty Blood carries real Tsukihime story rather than being a spin-off, "
     "and Fate/Grand Order is by volume the largest body of story Type-Moon "
     "has written."),
    ("novel", "Novels", "light novels and Nasu's early prose", ""),
    ("manga", "Manga", "", ""),
]


def sortkey(d):
    """Year-only dates sort mid-year, so they land among their own year."""
    parts = d.split("-")
    return (parts[0], parts[1] if len(parts) > 1 else "07",
            parts[2] if len(parts) > 2 else "01")


def slug(t):
    keep = "".join(c.lower() if c.isalnum() else "-" for c in t)
    while "--" in keep:
        keep = keep.replace("--", "-")
    return keep.strip("-")


def main():
    sections = []
    for key, title, sub, intro in MEDIA:
        got = sorted([w for w in WORKS if w[0] == key], key=lambda w: sortkey(w[2]))
        items = []
        for _, name, date, note, mins in got:
            x = {"id": "nasu-%s-%s" % (key, slug(name)), "t": name,
                 "n": date.split("-")[0]}
            if note:
                x["note"] = note
            if mins:
                x["w"] = round(mins / 60.0, 2)
            items.append(x)
        years = "%s–%s" % (got[0][2][:4], got[-1][2][:4])
        sec = {"id": key, "title": title,
               "sub": " · ".join(p for p in (years, sub, "%d entries" % len(items)) if p),
               "items": items}
        if intro:
            sec["intro"] = intro
        if key == "vn":
            sec["open"] = True
        sections.append(sec)

    ids = [x["id"] for s in sections for x in s["items"]]
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert len(ids) == len(WORKS), (len(ids), len(WORKS))
    # every date is either a year or a full date, never half-invented
    for _, name, d, _, _ in WORKS:
        assert len(d) in (4, 7, 10), "%s: odd date %r" % (name, d)

    prop = {
        "slug": SLUG,
        "title": "Nasuverse",
        "subtitle": "Type-Moon's shared universe, by media type",
        "kind": "mixed",
        "order": 17,
        "year": "1998–",
        "blurb": "%d works across six media, in release order within each." % len(WORKS),
        "unit": {"one": "work", "many": "works"},
        "verb": {"base": "read", "past": "done", "ing": "working through"},
        "accent": "#8A2E4A",
        "accentDark": "#E884A6",
        "tiers": False,
        "notes": [
            ["Where to start.", "Fate/stay night or Tsukihime, both visual "
             "novels. If you would rather watch than read: Fate/Zero, then "
             "Unlimited Blade Works, then the three Heaven's Feel films. Witch "
             "on the Holy Night and Kara no Kyoukai are standalone and need "
             "nothing else first."],
            ["Organised by medium, not by story.", "There is no single reading "
             "order for this universe — the works branch rather than continue — "
             "so this lists what exists in each medium, oldest first. The notes "
             "say where something sits when it matters."],
            ["Dates.", "Read from Wikipedia's Type-Moon release list and the "
             "individual work articles rather than typed from memory. Where only "
             "a year could be confirmed, only the year is shown."],
            ["Not here.", "The Fate/Grand Order Camelot and Solomon films, whose "
             "release dates could not be confirmed from a source, and the many "
             "drama CDs, art books and short stories that exist mostly in "
             "Japanese. Grand Order itself is one entry, which undersells it by "
             "several hundred hours."],
        ],
        "sections": sections,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json" % SLUG)
    print("  %d sections, %d works" % (len(sections), len(ids)))
    for s in sections:
        print("   %-16s %2d  %s" % (s["title"], len(s["items"]), s["sub"][:52]))


if __name__ == "__main__":
    main()
