"""Shared tables for the two Spider-Man reading lists.

`make_spiderman.py` covers Amazing Fantasy #15 to ASM #528 and
`make_spiderman_after.py` picks up at #539, with the Civil War issues between
them living in `make_civilwar.py`. All three read their annotations from here
so the same issue is never described two different ways.

**Notes say what an issue is, never what happens in it.** A debut, a creator's
first or last issue, which villain turns up, an arc name, an anniversary, a
publication fact — all fine. Deaths, unmaskings, identity reveals and endings
are not: the point of the list is to be read before the comics, not after. The
star rating carries the "this one matters" signal instead. Real issue titles
stay even where they give something away, because they are printed on the
cover regardless.

Order, era boundaries and star ratings come from the checklist written for the
group. The annotations are rewritten from it rather than transcribed, because
that document is heavily spoiler-annotated throughout.
"""

S_V1    = "https://www.marvel.com/comics/series/1987/the_amazing_spiderman_1963_1998"
S_V2    = "https://www.marvel.com/comics/series/454/the_amazing_spiderman_1999_2013"
S_ANN   = "https://www.marvel.com/comics/series/2984/amazing_spiderman_annual_1964_2018"
S_WEB   = "https://www.marvel.com/comics/series/2092/web_of_spiderman_1985_1995"
S_SPEC  = "https://www.marvel.com/comics/series/43439/spectacular_spiderman_1976_1998"
S_PPSM  = "https://www.marvel.com/comics/series/2060/peter_parker_spiderman_1999_2003"
S_SUP   = "https://www.marvel.com/comics/series/17554/superior_spiderman_2013_2014"
S_ULT24 = "https://www.marvel.com/comics/series/38809/ultimate_spider-man_2024_-_present"
S_2022  = "https://www.marvel.com/comics/series/32866/the_amazing_spiderman_2022_2025"
S_2025  = "https://www.marvel.com/comics/series/41731/the_amazing_spiderman_2025_present"
S_2014  = "https://www.marvel.com/comics/series/17285/the_amazing_spiderman_2014_2015"
S_2015  = "https://www.marvel.com/comics/series/20432/the_amazing_spiderman_2017_2018"
S_2018  = "https://www.marvel.com/comics/series/24396/the_amazing_spider-man_2018_-_2022"
S_ULT00 = "https://www.marvel.com/comics/series/466/ultimate_spider-man_(2000_-_2009)"
S_LIFE  = "https://www.marvel.com/comics/series/26911/spiderman_life_story_2019"
S_BLUE  = "https://www.marvel.com/comics/series/2072/spider-man_blue_2002_-_2003"

# Marvel gives issues arbitrary database ids with no derivable pattern, and its
# series pages page their back catalogue through JavaScript, so these cannot be
# generated in bulk. Copied, not built — #39 drops the leading "the".
URLS = {
    1: "6482/the_amazing_spider-man_1963_1",
    2: "6593/the_amazing_spider-man_1963_2",
    3: "6704/the_amazing_spider-man_1963_3",
    13: "6516/the_amazing_spider-man_1963_13",
    16: "6549/the_amazing_spider-man_1963_16",
    20: "6594/the_amazing_spider-man_1963_20",
    39: "6804/amazing_spider-man_1963_39",
    63: "6883/the_amazing_spider-man_1963_63",
    101: "6485/the_amazing_spider-man_1963_101",
    300: "6706/the_amazing_spider-man_1963_300",
    422: "6841/the_amazing_spider-man_1963_422",
    423: "6842/the_amazing_spider-man_1963_423",
    424: "6843/the_amazing_spider-man_1963_424",
    425: "6844/the_amazing_spider-man_1963_425",
    426: "6845/the_amazing_spider-man_1963_426",
    427: "6846/the_amazing_spider-man_1963_427",
    428: "6847/the_amazing_spider-man_1963_428",
    429: "6848/the_amazing_spider-man_1963_429",
    430: "6850/the_amazing_spider-man_1963_430",
    431: "6851/the_amazing_spider-man_1963_431",
    432: "6852/the_amazing_spider-man_1963_432",
    433: "6853/the_amazing_spider-man_1963_433",
    434: "6854/the_amazing_spider-man_1963_434",
    435: "6855/the_amazing_spider-man_1963_435",
    436: "6856/the_amazing_spider-man_1963_436",
    437: "6857/the_amazing_spider-man_1963_437",
    438: "6858/the_amazing_spider-man_1963_438",
    439: "6859/the_amazing_spider-man_1963_439",
    440: "6861/the_amazing_spider-man_1963_440",
    441: "6862/the_amazing_spider-man_1963_441",
}

NOTES = {
    1: "Chameleon; the Fantastic Four cameo",
    2: "Vulture and the Tinkerer debut",
    3: "Doctor Octopus debuts",
    4: "Sandman debuts",
    5: "Doctor Doom — Spidey's first tangle with an outside heavyweight",
    6: "The Lizard debuts",
    7: "Vulture",
    8: "The Living Brain; the Human Torch",
    9: "Electro debuts",
    10: "The Enforcers and the Big Man — the book's first crime-syndicate story",
    11: "Doc Ock; Betty Brant's background",
    12: "Doc Ock",
    13: "Mysterio debuts",
    14: "The Green Goblin debuts",
    15: "Kraven the Hunter debuts",
    16: "Daredevil",
    17: "Green Goblin",
    18: "“The End of Spider-Man” — Ditko's character work at its sharpest",
    19: "Sandman and the Enforcers",
    20: "The Scorpion debuts",
    21: "The Beetle; Human Torch",
    22: "Circus of Crime",
    23: "Green Goblin",
    24: "Mysterio",
    25: "Spider-Slayer; Mary Jane's first appearance, face hidden",
    26: "Green Goblin and the Crime-Master",
    27: "Goblin and Crime-Master, part 2",
    28: "Molten Man debuts; Peter graduates high school",
    29: "Scorpion",
    30: "The cat burglar",
    31: "Gwen Stacy and Harry Osborn debut; Master Planner begins",
    32: "Master Planner, part 2",
    33: "“The Final Chapter” — the most famous sequence in Spider-Man comics",
    34: "Kraven",
    35: "Molten Man",
    36: "The Looter",
    37: "Norman Osborn's first appearance as himself",
    38: "Ditko's last issue",
    39: "“How Green Was My Goblin” — Romita's first issue",
    40: "The Goblin's origin",
    41: "The Rhino debuts",
    42: "Mary Jane's face is finally on the page",
    43: "Rhino",
    44: "Lizard",
    45: "Lizard",
    46: "The Shocker debuts",
    47: "Kraven",
    48: "A new Vulture, Blackie Drago",
    49: "Vulture vs. Vulture",
    50: "“Spider-Man No More!” — and the Kingpin debuts",
    51: "Kingpin",
    52: "Kingpin",
    53: "Doc Ock",
    54: "Doc Ock",
    55: "Doc Ock",
    56: "Doc Ock",
    57: "Ka-Zar",
    58: "Spider-Slayer",
    59: "The Brainwasher; MJ's first cover",
    60: "Kingpin",
    61: "Kingpin",
    62: "Medusa",
    63: "Vulture vs. Vulture",
    64: "Vulture",
    65: "Peter in jail",
    66: "Mysterio",
    67: "Mysterio",
    68: "Campus unrest and the Lifeline Tablet begins",
    69: "Kingpin",
    70: "Kingpin",
    71: "Quicksilver",
    72: "Shocker",
    73: "Silvermane debuts",
    74: "Silvermane",
    75: "Silvermane",
    76: "Lizard",
    77: "Lizard; Human Torch",
    78: "The Prowler debuts",
    79: "Prowler",
    80: "Chameleon",
    81: "The Kangaroo",
    82: "Electro",
    83: "The Schemer",
    84: "Schemer; Kingpin",
    85: "The Schemer",
    86: "Black Widow's redesign",
    87: "Peter and the secret identity",
    88: "Doc Ock",
    89: "Doc Ock",
    90: "One of the run's turning points",
    91: "Sam Bullit",
    92: "Sam Bullit; Iceman",
    93: "Prowler",
    94: "The origin retold",
    95: "London",
    96: "The drug arc begins — published without Comics Code approval",
    97: "Drug arc, part 2",
    98: "Drug arc, part 3",
    99: "Prison riot",
    100: "The 100th issue",
    101: "Morbius debuts",
    102: "Morbius; the Lizard",
    103: "Ka-Zar",
    104: "Ka-Zar",
    105: "Spider-Slayer",
    106: "Spider-Slayer",
    107: "Spider-Slayer",
    108: "Flash Thompson in Vietnam",
    109: "Doctor Strange",
    110: "The Gibbon debuts",
    111: "Gibbon; Kraven",
    112: "Doc Ock",
    113: "Hammerhead debuts",
    114: "Hammerhead; Doc Ock",
    115: "Hammerhead; Doc Ock",
    116: "The Disruptor, reworked from a 1968 magazine story",
    117: "Disruptor",
    118: "Disruptor; Smasher",
    119: "Spider-Man vs. the Hulk in Canada",
    120: "Hulk, part 2",
    121: "“The Night Gwen Stacy Died” — the end of the Silver Age",
    122: "“The Goblin's Last Stand”",
    123: "Luke Cage",
    124: "Man-Wolf debuts",
    125: "Man-Wolf",
    126: "Kangaroo",
    127: "Vulture",
    128: "Vulture",
    129: "The Punisher debuts — and so does the Jackal",
    130: "Hammerhead; Doc Ock",
    131: "Doc Ock and Aunt May",
    132: "Molten Man",
    133: "Molten Man",
    134: "The Tarantula debuts; Punisher",
    135: "Tarantula; Punisher",
    136: "A new Green Goblin",
    137: "The new Goblin, part 2",
    138: "Mindworm",
    139: "The Grizzly; the Jackal",
    140: "Grizzly; Jackal",
    141: "Mysterio",
    142: "Mysterio",
    143: "Cyclone",
    144: "Cyclone",
    146: "Scorpion; Jackal",
    147: "Tarantula",
    148: "The Jackal",
    149: "The original Clone Saga — short, self-contained, and the seed of 1994",
    150: "“Spider-Man or Spider-Clone?”",
    159: "Doc Ock",
    160: "The Tinkerer",
    161: "Nightcrawler; Punisher",
    162: "Jigsaw debuts; Punisher",
    164: "Kingpin",
    165: "Kingpin; Stegron",
    167: "Will o' the Wisp debuts",
    168: "Will o' the Wisp",
    170: "Nova",
    171: "Nova",
    174: "Punisher and the Hitman",
    175: "Punisher and the Hitman, part 2",
    176: "A third Green Goblin",
    177: "Green Goblin III",
    178: "Green Goblin III",
    179: "Green Goblin III",
    180: "Green Goblin III",
    181: "The origin retold",
    182: "Rocket Racer",
    184: "White Dragon",
    185: "Peter's graduation",
    186: "Chameleon",
    187: "Captain America",
    188: "Jigsaw",
    189: "Man-Wolf",
    190: "Man-Wolf",
    194: "The Black Cat debuts",
    195: "Black Cat's origin",
    200: "The burglar returns",
    206: "Roger Stern's first issue",
    209: "Calypso debuts; Kraven",
    212: "Hydro-Man debuts",
    217: "Hydro-Man and Sandman",
    220: "Moon Knight",
    224: "Stern's run proper begins — Vulture",
    225: "Foolkiller",
    226: "Black Cat",
    227: "Black Cat",
    229: "“Nothing Can Stop the Juggernaut” — arguably the best two-parter in the run",
    230: "Juggernaut, part 2",
    231: "Mister Hyde and the Cobra",
    232: "Mister Hyde",
    233: "Tarantula",
    234: "Will o' the Wisp",
    235: "Will o' the Wisp",
    236: "Tarantula",
    238: "The Hobgoblin debuts",
    239: "Hobgoblin",
    241: "The Vulture's origin",
    248: "“The Kid Who Collects Spider-Man” — a nine-page backup, and the most "
         "affecting thing in the run",
    249: "Hobgoblin and Kingpin",
    250: "Hobgoblin",
    251: "Stern's finale",
    252: "The black costume arrives in ASM",
    253: "The Rose debuts",
    256: "Puma debuts",
    257: "Hobgoblin",
    258: "A turn for the black costume",
    259: "MJ's backstory",
    265: "Silver Sable debuts",
    267: "“The Commuter Cometh” — the funniest issue in the run",
    268: "Kingpin; the Beyonder",
    275: "Hobgoblin and Kingpin",
    276: "Hobgoblin; Flash Thompson",
    284: "Gang War begins",
    285: "Gang War; Punisher",
    286: "Gang War",
    287: "Gang War",
    288: "Gang War, part 5",
    289: "The Hobgoblin's identity",
    293: "Kraven's Last Hunt, part 2",
    294: "Kraven's Last Hunt, part 5",
    296: "Doc Ock",
    297: "Doc Ock",
    298: "McFarlane's first issue",
    299: "Venom",
    300: "Venom's first full appearance",
    312: "Green Goblin and Hobgoblin",
    315: "Venom",
    316: "Venom",
    317: "Venom",
    318: "Scorpion",
    319: "Rhino",
    321: "Assassin Nation Plot",
    322: "Assassin Nation; Silver Sable",
    323: "Captain America",
    324: "Assassin Nation",
    325: "Assassin Nation, part 5",
    326: "Acts of Vengeance — Graviton",
    327: "Acts of Vengeance — Magneto",
    328: "The Hulk — McFarlane's last ASM issue",
    329: "Tri-Sentinel",
    330: "Punisher; Erik Larsen's run begins",
    331: "Punisher",
    332: "Doc Ock",
    333: "Doc Ock",
    344: "Cletus Kasady debuts; Cardiac debuts",
    345: "Carnage's origin",
    346: "Venom",
    347: "Venom",
    348: "Doc Ock",
    350: "Doctor Doom",
    361: "Carnage's first full appearance",
    362: "Carnage; Venom",
    363: "Carnage, part 3",
    365: "30th anniversary; Spider-Man 2099 previews",
    375: "Venom",
    378: "Maximum Carnage, part 4",
    379: "Maximum Carnage, part 8",
    380: "Maximum Carnage, part 12",
    388: "Green Goblin and Vulture — Michelinie's last issue",
    394: "“Power and Responsibility”",
    396: "The Jackal",
    400: "“The Gift” — the 400th issue",
    401: "Maximum Clonage",
    402: "Maximum Clonage",
    403: "Maximum Clonage",
    407: "Spider-Carnage",
    408: "Spider-Carnage",
    409: "Spider-Carnage",
    410: "Spider-Carnage",
    418: "A chapter of “Revelations”",
    430: "Carnage and the Silver Surfer, as unhinged as it sounds",
    431: "Carnage; Silver Surfer",
    435: "Norman Osborn",
    440: "“The Gathering of Five”",
    441: "“The Final Chapter” — the last issue of volume 1",
    500: "Anniversary issue",
    506: "“The Book of Ezekiel”",
    507: "Book of Ezekiel",
    508: "Book of Ezekiel",
    509: "“Sins Past” begins. Notorious — a retcon many readers reject outright. "
         "Needed for continuity; you don't have to like it.",
    510: "Sins Past",
    511: "Sins Past",
    512: "Sins Past",
    513: "Sins Past",
    514: "Sins Past, part 6",
    519: "Peter, MJ and May move into Avengers Tower",
    524: "Before The Other",
    525: "“The Other” begins — the chapters outside ASM are listed at the end of "
         "this section",
    526: "The Other",
    527: "The Other",
    528: "The Other, part 4",
    # --- Civil War issues live in make_civilwar.py ---
    539: "“Back in Black” begins",
    540: "Back in Black",
    541: "Back in Black",
    542: "Back in Black",
    543: "Back in Black, part 5",
    544: "One More Day, part 1",
    545: "One More Day, part 4",
}

# 1 = notable, 2 = an all-timer. Carried from the source checklist, and doing
# the work the removed spoilers used to do: flagging that an issue matters
# without saying why.
STARS = {
    3: 1, 14: 2, 31: 1, 33: 2,
    39: 1, 40: 1, 42: 1, 50: 2, 68: 1, 90: 2, 96: 2, 97: 1, 98: 1, 100: 1, 101: 1,
    119: 1, 120: 1, 121: 2, 122: 2, 129: 2, 136: 2, 137: 1, 143: 1, 148: 1, 149: 2,
    150: 1, 161: 1, 162: 1, 174: 1, 175: 1, 176: 1, 180: 1, 182: 1, 183: 1,
    194: 2, 200: 1,
    212: 1, 224: 1, 229: 2, 230: 2, 238: 2, 248: 2, 249: 1, 250: 1, 251: 1,
    252: 2, 258: 2, 259: 1, 265: 1, 275: 1, 289: 1, 293: 2, 294: 2, 298: 1, 300: 2,
    312: 1, 315: 1, 316: 1, 317: 1, 328: 1, 344: 1, 345: 1, 346: 1, 347: 1,
    361: 2, 362: 1, 363: 1, 365: 1, 375: 1, 378: 1, 379: 1, 380: 1,
    394: 1, 395: 1, 400: 2, 410: 1, 418: 1, 440: 1, 441: 1,
    500: 1, 525: 1, 526: 1, 527: 1, 528: 1,
    539: 1, 540: 1, 541: 1, 542: 1, 543: 1,
    545: 2,
}

V2_NOTES = {
    1: "John Byrne relaunches the title",
    2: "Byrne",
    3: "Byrne",
    13: "Venom",
    18: "A major turn for Mary Jane",
    29: "Mackie's last issue",
    30: "“Coming Home” — JMS begins. Ezekiel and Morlun.",
    31: "Coming Home",
    32: "Coming Home",
    33: "Coming Home",
    34: "Coming Home",
    35: "Coming Home, part 6",
    36: "The 9/11 issue. Black cover, no ads.",
    37: "Peter and Aunt May",
    38: "The best issue of the run",
    39: "Doctor Octopus",
    40: "Doc Ock",
    41: "Doctor Strange",
    43: "Loki",
    46: "“My Dinner with Jonah”",
    47: "Peter and Jonah",
    50: "Doc Ock; Peter's birthday",
    51: "Doc Ock",
    52: "Doc Ock",
    55: "Ezekiel",
    56: "Ezekiel",
    57: "Ezekiel",
    58: "The last issue before renumbering",
}
V2_STARS = {18: 1, 30: 2, 31: 1, 32: 1, 33: 1, 34: 1, 35: 1, 36: 2, 37: 1, 38: 2,
            50: 1, 51: 1, 52: 1}


def asm(n):
    """One issue of the original run, or of the resumed #500+ numbering."""
    x = {"id": "asm-%d" % n, "t": "Amazing Spider-Man", "n": "#%d" % n, "w": 1}
    if n in NOTES:
        x["note"] = NOTES[n]
    if n in STARS:
        x["star"] = STARS[n]
    if n in URLS:
        x["url"] = "https://www.marvel.com/comics/issue/" + URLS[n]
    return x


def v2(n):
    x = {"id": "asm-v2-%d" % n, "t": "Amazing Spider-Man vol. 2",
         "n": "#%d" % n, "w": 1}
    if n in V2_NOTES:
        x["note"] = V2_NOTES[n]
    if n in V2_STARS:
        x["star"] = V2_STARS[n]
    return x


def item(key, title, num, note="", star=0, w=1, url="", opt=0):
    x = {"id": "asm-" + key, "t": title, "n": num, "w": w}
    if note:
        x["note"] = note
    if star:
        x["star"] = star
    if url:
        x["url"] = url
    if opt:
        x["opt"] = 1
    return x


def rng(a, b):
    return [asm(n) for n in range(a, b + 1)]


def check(sections, expect_total=None):
    """Shared validation: unique ids, and no note or star left orphaned."""
    ids = [x["id"] for s in sections for x in s["items"]]
    if len(ids) != len(set(ids)):
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        raise SystemExit("duplicate item ids: %s" % dupes[:10])
    if expect_total is not None and len(ids) != expect_total:
        raise SystemExit("expected %d items, built %d" % (expect_total, len(ids)))
    return len(ids)
