#!/usr/bin/env python3
"""Generate properties/amazing-spider-man.json.

    python3 tools/make_spiderman.py

Adapted from a reading checklist written for the group, which is the authority
for the order, the era boundaries, the per-issue annotations and the star
ratings. Nothing here is invented; where the checklist declines to pick, so
does this.

Its shape, kept intact:
  - Part One is a *complete* read — Amazing Fantasy #15 through One More Day,
    every issue, nothing filtered. Annotations flag what happens in an issue;
    an issue with no note is a done-in-one, not a skip. That is tier 1.
  - Part Two is explicitly selective, so its entries are whole arcs and runs
    rather than single issues. Superior Spider-Man is tier 2 — the checklist
    calls it "the one" — and the rest is tier 3.
  - Items marked in the source are carried over: star 1 for a notable issue,
    star 2 for an all-timer. Cross-title chapters that the run genuinely needs
    are separate items rather than footnotes, so they can be ticked.

Weights are issue counts, not hours, because a Part Two entry can be a whole
run: Ultimate Spider-Man is 160 issues against one issue of ASM. Without that
the strip and the pace line would treat them as equals. `weightUnit` makes the
readouts say "160 issues" rather than mislabelling them as hours.

Marvel assigns issues arbitrary database ids with no derivable pattern, and its
series pages page their back catalogue through JavaScript, so per-issue URLs
cannot be generated in bulk. The 30 direct links below are the ones the source
had confirmed; everything else links at series level, which is how you would
navigate Marvel Unlimited anyway.

Amazing Spider-Man (2025) issue count checked August 2026 — 34 published, with
#1000 due 16 September 2026.
"""
import json
import pathlib

SLUG = "amazing-spider-man"

S_V1     = "https://www.marvel.com/comics/series/1987/the_amazing_spiderman_1963_1998"
S_V2     = "https://www.marvel.com/comics/series/454/the_amazing_spiderman_1999_2013"
S_ANN    = "https://www.marvel.com/comics/series/2984/amazing_spiderman_annual_1964_2018"
S_WEB    = "https://www.marvel.com/comics/series/2092/web_of_spiderman_1985_1995"
S_SPEC   = "https://www.marvel.com/comics/series/43439/spectacular_spiderman_1976_1998"
S_PPSM   = "https://www.marvel.com/comics/series/2060/peter_parker_spiderman_1999_2003"
S_SUP    = "https://www.marvel.com/comics/series/17554/superior_spiderman_2013_2014"
S_ULT24  = "https://www.marvel.com/comics/series/38809/ultimate_spider-man_2024_-_present"
S_2022   = "https://www.marvel.com/comics/series/32866/the_amazing_spiderman_2022_2025"
S_2025   = "https://www.marvel.com/comics/series/41731/the_amazing_spiderman_2025_present"

# The per-issue links the source could confirm. Note the slug is not uniform —
# #39 drops the leading "the" — so these are copied rather than built.
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
assert len(URLS) == 30, len(URLS)

# Annotations from the source, by issue. A missing entry is a done-in-one with
# no lasting consequence, which the source is explicit is not the same as a skip.
NOTES = {
    1: "Chameleon; the Fantastic Four cameo",
    2: "Vulture and the Tinkerer debut",
    3: "Doctor Octopus debuts",
    4: "Sandman debuts",
    5: "Doctor Doom — Spidey's first tangle with an outside heavyweight",
    6: "The Lizard debuts",
    7: "Vulture returns",
    8: "The Living Brain; the Human Torch",
    9: "Electro debuts",
    10: "The Enforcers and the Big Man — the book's first crime-syndicate story",
    11: "Doc Ock; Betty Brant's background",
    12: "Doc Ock unmasks him — and nobody believes it",
    13: "Mysterio debuts",
    14: "The Green Goblin debuts",
    15: "Kraven the Hunter debuts",
    16: "Daredevil",
    17: "Green Goblin returns",
    18: "“The End of Spider-Man” — Peter quits. Ditko's character work at its sharpest.",
    19: "Sandman and the Enforcers",
    20: "The Scorpion debuts",
    21: "The Beetle; Human Torch",
    22: "Circus of Crime",
    23: "Green Goblin",
    24: "Mysterio — Peter thinks he's losing his mind",
    25: "Spider-Slayer; Mary Jane's first appearance, face hidden",
    26: "Green Goblin vs. the Crime-Master",
    27: "Goblin/Crime-Master concludes",
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
    39: "“How Green Was My Goblin” — the Goblin unmasks. Romita's first issue.",
    40: "The Goblin's origin",
    41: "The Rhino debuts",
    42: "Mary Jane's face is finally revealed",
    43: "Rhino; Osborn's amnesia",
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
    55: "Doc Ock — who is now boarding with Aunt May",
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
    75: "Silvermane's fate",
    76: "Lizard",
    77: "Lizard; Human Torch",
    78: "The Prowler debuts",
    79: "Prowler",
    80: "Chameleon",
    81: "The Kangaroo",
    82: "Electro",
    83: "The Schemer",
    84: "Schemer; Kingpin",
    85: "Schemer's identity",
    86: "Black Widow's redesign",
    87: "Peter reveals his identity — or does he",
    88: "Doc Ock",
    89: "Doc Ock",
    90: "Captain Stacy dies",
    91: "Sam Bullit",
    92: "Sam Bullit; Iceman",
    93: "Prowler",
    94: "The origin retold",
    95: "London",
    96: "The drug arc begins — published without Comics Code approval",
    97: "Drug arc, part 2",
    98: "Drug arc, part 3",
    99: "Prison riot",
    100: "Peter grows six arms",
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
    112: "Doc Ock — Aunt May goes missing",
    113: "Hammerhead debuts",
    114: "Hammerhead; Doc Ock",
    115: "Hammerhead; Doc Ock",
    116: "The Disruptor, reworked from a 1968 magazine story",
    117: "Disruptor",
    118: "Disruptor; Smasher",
    119: "Spider-Man vs. the Hulk in Canada",
    120: "Hulk, part 2",
    121: "“The Night Gwen Stacy Died” — the end of the Silver Age",
    122: "“The Goblin's Last Stand” — Norman Osborn dies",
    123: "Luke Cage",
    124: "Man-Wolf debuts",
    125: "Man-Wolf",
    126: "Kangaroo",
    127: "Vulture",
    128: "Vulture",
    129: "The Punisher debuts — and so does the Jackal",
    130: "Hammerhead; Doc Ock",
    131: "Doc Ock nearly marries Aunt May",
    132: "Molten Man",
    133: "Molten Man",
    134: "The Tarantula debuts; Punisher",
    135: "Tarantula; Punisher",
    136: "Harry Osborn becomes the Green Goblin",
    137: "Harry as the Goblin, part 2",
    138: "Mindworm",
    139: "The Grizzly; the Jackal",
    140: "Grizzly; Jackal",
    141: "Mysterio",
    142: "Mysterio",
    143: "Cyclone; Peter and MJ's first kiss",
    144: "Cyclone; “Gwen” reappears",
    145: "The Gwen mystery deepens",
    146: "Scorpion; Jackal",
    147: "Tarantula",
    148: "The Jackal unmasked",
    149: "The original Clone Saga — short, self-contained, and the seed of 1994",
    150: "“Spider-Man or Spider-Clone?” — the question is settled",
    151: "Peter disposes of the body",
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
    180: "The third Goblin unmasked",
    181: "The origin retold",
    182: "Rocket Racer; Peter proposes to MJ",
    183: "She turns him down",
    184: "White Dragon",
    185: "Peter's graduation goes wrong",
    186: "Chameleon",
    187: "Captain America",
    188: "Jigsaw",
    189: "Man-Wolf",
    190: "Man-Wolf",
    194: "The Black Cat debuts",
    195: "Black Cat's origin",
    200: "The burglar returns — Peter finally confronts Uncle Ben's killer",
    206: "Roger Stern's first issue",
    209: "Calypso debuts; Kraven",
    212: "Hydro-Man debuts",
    217: "Hydro-Man and Sandman merge",
    220: "Moon Knight",
    224: "Stern's run proper begins — Vulture",
    225: "Foolkiller",
    226: "Black Cat returns",
    227: "Black Cat",
    229: "“Nothing Can Stop the Juggernaut” — arguably the best two-parter in the run",
    230: "Juggernaut, part 2",
    231: "Mister Hyde and the Cobra",
    232: "Mister Hyde",
    233: "Tarantula",
    234: "Will o' the Wisp",
    235: "Will o' the Wisp",
    236: "Tarantula's end",
    238: "The Hobgoblin debuts",
    239: "Hobgoblin",
    241: "The Vulture's origin",
    248: "“The Kid Who Collects Spider-Man” — a nine-page backup, and the most affecting thing in the run",
    249: "Hobgoblin and Kingpin",
    250: "Hobgoblin",
    251: "Stern's finale",
    252: "The black costume arrives in ASM",
    253: "The Rose debuts",
    256: "Puma debuts",
    257: "Hobgoblin; MJ reveals she's known all along",
    258: "The costume is alive",
    259: "MJ's backstory; back to red-and-blue",
    265: "Silver Sable debuts",
    267: "“The Commuter Cometh” — the funniest issue in the run",
    268: "Kingpin; the Beyonder",
    275: "Hobgoblin/Kingpin; Peter retells his origin to MJ",
    276: "Hobgoblin; Flash Thompson framed",
    284: "Gang War begins",
    285: "Gang War; Punisher",
    286: "Gang War",
    287: "Gang War",
    288: "Gang War concludes",
    289: "The Hobgoblin's identity revealed; Macendale takes the name",
    293: "Kraven's Last Hunt, part 2",
    294: "Kraven's Last Hunt, part 5",
    296: "Doc Ock",
    297: "Doc Ock",
    298: "McFarlane's first issue; Eddie Brock cameo",
    299: "Venom — a glimpse",
    300: "Venom's first full appearance; back to red-and-blue",
    312: "Green Goblin vs. Hobgoblin",
    315: "Venom returns",
    316: "Venom",
    317: "Venom",
    318: "Scorpion",
    319: "Rhino",
    321: "Assassin Nation Plot",
    322: "Assassin Nation; Silver Sable",
    323: "Captain America",
    324: "Assassin Nation",
    325: "Assassin Nation concludes",
    326: "Acts of Vengeance — Graviton",
    327: "Acts of Vengeance — Magneto",
    328: "The Hulk — McFarlane's last ASM issue",
    329: "Tri-Sentinel",
    330: "Punisher; Erik Larsen's run begins",
    331: "Punisher",
    332: "Doc Ock",
    333: "Doc Ock",
    344: "Cletus Kasady debuts; Cardiac debuts",
    345: "The Carnage symbiote finds Kasady",
    346: "Venom",
    347: "Venom",
    348: "Doc Ock",
    350: "Doctor Doom",
    361: "Carnage's first full appearance",
    362: "Carnage; Venom",
    363: "Carnage concludes",
    365: "30th anniversary — Peter's “parents” return, and Spider-Man 2099 previews",
    375: "Venom; Peter confronts his “parents”",
    378: "Maximum Carnage, part 4",
    379: "Maximum Carnage, part 8",
    380: "Maximum Carnage, part 12",
    388: "Green Goblin and Vulture — Michelinie's last issue",
    394: "“Power and Responsibility” — Ben Reilly returns",
    395: "Ben Reilly",
    396: "The Jackal returns",
    399: "Aunt May's decline",
    400: "“The Gift” — the death of Aunt May. Later undone; still beautiful.",
    401: "Maximum Clonage",
    402: "Maximum Clonage",
    403: "Maximum Clonage",
    407: "Spider-Carnage",
    408: "Spider-Carnage",
    409: "Spider-Carnage",
    410: "Spider-Carnage",
    418: "A chapter of “Revelations” — the Clone Saga's real ending",
    430: "Carnage vs. the Silver Surfer, as unhinged as it sounds",
    431: "Carnage; Silver Surfer",
    435: "Norman Osborn tightens his grip",
    440: "“The Gathering of Five”",
    441: "“The Final Chapter” — the last issue of volume 1",
    500: "Anniversary issue — Peter's whole life, seen at once",
    506: "“The Book of Ezekiel”",
    507: "Book of Ezekiel",
    508: "Book of Ezekiel",
    509: "“Sins Past” begins. Notorious — a Gwen Stacy retcon many readers reject "
         "outright. Needed for continuity; you don't have to like it.",
    510: "Sins Past",
    511: "Sins Past",
    512: "Sins Past",
    513: "Sins Past",
    514: "Sins Past concludes",
    519: "Peter, MJ and May move into Avengers Tower",
    524: "Before The Other",
    525: "“The Other” begins — the interleaved order is listed at the end of this section",
    526: "The Other",
    527: "The Other",
    528: "The Other concludes",
    529: "The Iron Spider suit",
    530: "Civil War builds",
    531: "Civil War builds",
    532: "Civil War — Peter unmasks publicly",
    533: "The fallout",
    534: "Civil War",
    535: "Civil War",
    536: "Civil War — Peter turns on Stark",
    537: "Civil War",
    538: "Civil War ends badly",
    539: "“Back in Black” — Aunt May is shot",
    540: "Back in Black",
    541: "Back in Black",
    542: "Back in Black",
    543: "Back in Black concludes",
    544: "One More Day, part 1",
    545: "One More Day, part 4 — the marriage is traded to Mephisto",
}

# ★ = notable, ★★ = all-timer, carried straight from the source.
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
    500: 1, 525: 1, 526: 1, 527: 1, 528: 1, 529: 1, 532: 1, 533: 1, 538: 1,
    539: 1, 540: 1, 541: 1, 542: 1, 543: 1,
    545: 2,
}

V2_NOTES = {
    1: "John Byrne relaunches the title",
    2: "Byrne",
    3: "Byrne",
    13: "Venom",
    18: "Mary Jane's apparent death",
    29: "Mackie's last issue",
    30: "“Coming Home” — JMS begins. Ezekiel and Morlun.",
    31: "Coming Home",
    32: "Coming Home",
    33: "Coming Home",
    34: "Coming Home",
    35: "Coming Home concludes",
    36: "The 9/11 issue. Black cover, no ads.",
    37: "Aunt May finds the costume",
    38: "Aunt May and Peter talk. Superb.",
    39: "Doctor Octopus",
    40: "Doc Ock",
    41: "Doctor Strange",
    43: "Loki",
    46: "“My Dinner with Jonah”",
    47: "Peter and Jonah",
    50: "Doc Ock; Peter's birthday",
    51: "Doc Ock",
    52: "Doc Ock",
    55: "Ezekiel's endgame",
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


SECTIONS = [
    {
        "id": "prologue", "tier": 1, "title": "Prologue",
        "sub": "1962 · where it starts",
        # Without this a newcomer lands on Lee & Ditko, because the fallback
        # looks for the first section carrying series links and the Prologue
        # has none.
        "open": True,
        "items": [item("af15", "Amazing Fantasy", "#15",
                       "The origin. Eleven pages.", 2)],
    },
    {
        "id": "ditko", "tier": 1, "title": "Lee & Ditko",
        "sub": "#1–38 · 1963–66",
        "links": [{"label": "The series", "url": S_V1}],
        "intro": "Nearly every major villain in the mythology debuts inside "
                 "these 38 issues. Ditko's Peter is anxious, prickly and broke — "
                 "closer to the character's core than the friendlier version "
                 "that follows.",
        "items": rng(1, 38) + [
            item("ann-1", "Amazing Spider-Man Annual", "#1", "The Sinister Six", 1,
                 url=S_ANN),
            item("ann-2", "Amazing Spider-Man Annual", "#2", "Doctor Strange"),
            item("ann-3", "Amazing Spider-Man Annual", "#3", "The Avengers"),
        ],
    },
    {
        "id": "romita", "tier": 1, "title": "Lee & Romita Sr.",
        "sub": "#39–102 · 1966–71",
        "intro": "The art turns glossy, Peter goes to college, and the soap "
                 "opera takes over the book.",
        "items": rng(39, 102) + [
            item("ann-5", "Amazing Spider-Man Annual", "#5", "Peter's parents", 1,
                 url=S_ANN),
            item("ann-6", "Amazing Spider-Man Annual", "#6",
                 "Mostly reprints; skippable without loss", opt=1),
        ],
    },
    {
        "id": "conway", "tier": 1, "title": "Conway & Kane",
        "sub": "#103–149 · 1971–75",
        "intro": "The tonal hinge of the whole character. Read this stretch "
                 "straight through — it's the densest run of consequence in the "
                 "title's history.",
        "items": rng(103, 149),
    },
    {
        "id": "seventies", "tier": 1, "title": "Wolfman, Wein & the Late Seventies",
        "sub": "#150–200 · 1975–80",
        "intro": "Quieter and more procedural. This is the stretch where the "
                 "unannotated issues outnumber the annotated ones by the widest "
                 "margin — that's the era, not an omission.",
        "items": rng(150, 200),
    },
    {
        "id": "stern", "tier": 1, "title": "Stern, Mantlo & the Hobgoblin",
        "sub": "#201–251 · 1980–84",
        "intro": "Roger Stern's run, roughly #224 onward, is one of the two or "
                 "three best in the title's history: tight, character-driven, "
                 "brilliantly plotted.",
        "items": rng(201, 251),
    },
    {
        "id": "black", "tier": 1, "title": "The Black Costume & Venom",
        "sub": "#252–300 · 1984–88 · with the cross-title chapters that matter",
        "links": [{"label": "Spectacular", "url": S_SPEC},
                  {"label": "Web", "url": S_WEB}],
        "items": (
            [item("secretwars", "Secret Wars", "#1–12",
                  "Optional, but it's where the suit is acquired", w=12, opt=1)]
            + rng(252, 300)
            + [
                item("jeandewolff", "Spectacular Spider-Man", "#107–110",
                     "“The Death of Jean DeWolff” — not ASM, but one of the finest "
                     "Spider-Man stories of the decade", 2, w=4, url=S_SPEC),
                item("ann-21", "Amazing Spider-Man Annual", "#21",
                     "Peter and MJ's wedding", 1, url=S_ANN),
                item("klh-1", "Web of Spider-Man", "#31",
                     "Kraven's Last Hunt, part 1 — read before ASM #293", 2,
                     url=S_WEB),
                item("klh-3", "Spectacular Spider-Man", "#131",
                     "Kraven's Last Hunt, part 3 — between ASM #293 and #294", 2,
                     url=S_SPEC),
                item("klh-4", "Web of Spider-Man", "#32",
                     "Kraven's Last Hunt, part 4 — between ASM #293 and #294", 2,
                     url=S_WEB),
                item("klh-6", "Spectacular Spider-Man", "#132",
                     "Kraven's Last Hunt, part 6 — read after ASM #294", 2,
                     url=S_SPEC),
            ]
        ),
    },
    {
        "id": "mcfarlane", "tier": 1, "title": "McFarlane, Larsen & the Early Nineties",
        "sub": "#301–350 · 1988–91",
        "intro": "Art-driven. Thinner storytelling than Stern, but these are the "
                 "issues that fixed how a generation pictures the character.",
        "items": rng(301, 350),
    },
    {
        "id": "carnage", "tier": 1, "title": "Carnage & Nineties Excess",
        "sub": "#351–393 · 1991–94 · plus the Maximum Carnage chapters",
        "items": rng(351, 393) + [
            item("maxcarn-1", "Maximum Carnage, chapters 1–3", "◆",
                 "Spider-Man Unlimited #1 → Web #101 → Spectacular #201, then ASM #378",
                 1, w=3),
            item("maxcarn-2", "Maximum Carnage, chapters 5–7", "◆",
                 "Spider-Man #35 → Web #102 → Spectacular #202, then ASM #379",
                 w=3),
            item("maxcarn-3", "Maximum Carnage, chapters 9–11", "◆",
                 "Spider-Man #36 → Web #103 → Spectacular #203, then ASM #380",
                 w=3),
            item("maxcarn-4", "Maximum Carnage, chapters 13–14", "◆",
                 "Spider-Man #37 → Spider-Man Unlimited #2", w=2),
        ],
    },
    {
        "id": "clone", "tier": 1, "title": "The Clone Saga",
        "sub": "#394–418 · 1994–96 · the ASM path, not the complete 200 issues",
        "intro": "The Clone Saga ran two years across five monthly titles and is "
                 "genuinely enormous — roughly 200 issues read complete. It was "
                 "also being rewritten in real time by editorial, so it "
                 "contradicts itself.\n\n"
                 "These are the ASM issues plus the Revelations bookend, which "
                 "is the recommended path and follows the plot fine. The "
                 "completist alternative is the six Complete Clone Saga Epic "
                 "volumes.",
        "items": rng(394, 418) + [
            item("revelations", "“Revelations”, the other three chapters", "◆",
                 "Spectacular #240, Sensational #11 and Peter Parker: Spider-Man #75",
                 1, w=3, url=S_PPSM),
        ],
    },
    {
        "id": "endvol1", "tier": 1, "title": "The End of Volume One",
        "sub": "#419–441 · 1996–98",
        "items": rng(419, 441) + [
            item("finalchapter", "“The Final Chapter” continues", "◆",
                 "Spectacular #263 and Spider-Man #98", w=2),
        ],
    },
    {
        "id": "mackie", "tier": 1, "title": "Volume Two: Mackie & Byrne",
        "sub": "vol. 2 #1–29 · 1999–2001",
        "links": [{"label": "The series", "url": S_V2}],
        "intro": "The soft reboot, and the weakest sustained stretch in the "
                 "title's history — MJ is written out and the Osborn plots spin "
                 "in place. If you're going to abridge anything, abridge here.",
        "items": [v2(n) for n in range(1, 30)],
    },
    {
        "id": "jms", "tier": 1, "title": "J. Michael Straczynski begins",
        "sub": "vol. 2 #30–58 · 2001–03",
        "intro": "The last great sustained run before the reset.",
        "items": [v2(n) for n in range(30, 59)],
    },
    {
        "id": "renumbered", "tier": 1, "title": "Renumbered to #500",
        "sub": "#500–543 · 2003–07",
        "intro": "Volume 2 #58 was followed by #500, resuming the original count.",
        "items": rng(500, 543) + [
            item("theother", "“The Other”, the chapters outside ASM", "◆",
                 "Friendly Neighborhood Spider-Man #1–4 and Marvel Knights "
                 "Spider-Man #19–22, interleaved with ASM #525–528", 1, w=8),
            item("civilwar", "Civil War", "#1–2",
                 "The public unmasking happens in #2", w=2),
        ],
    },
    {
        "id": "omd", "tier": 1, "title": "One More Day",
        "sub": "2007 · four issues, in exactly this order",
        "intro": "Peter and MJ's marriage is traded to Mephisto in exchange for "
                 "Aunt May's life, and roughly twenty years of continuity are "
                 "quietly rewritten. This is where Part One ends, and where "
                 "plenty of readers stop on purpose.",
        "items": [
            asm(544),
            item("omd-2", "Friendly Neighborhood Spider-Man", "#24",
                 "One More Day, part 2"),
            item("omd-3", "Sensational Spider-Man", "#41", "One More Day, part 3"),
            asm(545),
        ],
    },
    # ---------------------------------------------------------------- part two
    {
        "id": "bnd", "tier": 3, "title": "Brand New Day",
        "sub": "#546–647 · 2008–10 · selected arcs",
        "links": [{"label": "The series", "url": S_V2}],
        "intro": "Part Two is selective — recommendations, not a complete read. "
                 "Three issues a month, rotating writers. Peter is single, broke "
                 "and back in Queens. Better than its reputation; the arcs are "
                 "often sharp even if the premise is the thing people object to.",
        "items": [
            item("bnd-546", "The new status quo", "#546–548",
                 "Slott and McNiven"),
            item("bnd-568", "“New Ways to Die”", "#568–573",
                 "Slott and John Romita Jr. Anti-Venom, Thunderbolts. The best "
                 "Brand New Day arc.", 1),
            item("bnd-595", "“American Son”", "#595–599", ""),
            item("bnd-600", "Anniversary issue", "#600", "Doc Ock, and a wedding"),
            item("bnd-612", "“The Gauntlet”", "#612–623",
                 "A systematic reintroduction of the rogues gallery"),
            item("bnd-630", "“Shed”", "#630–633",
                 "Zeb Wells and Chris Bachalo on the Lizard. Genuinely "
                 "disturbing, genuinely great.", 1),
            item("bnd-634", "“Grim Hunt”", "#634–637",
                 "The sequel to Kraven's Last Hunt, 23 years later", 1),
            item("bnd-642", "“Origin of the Species”", "#642–647", ""),
        ],
    },
    {
        "id": "bigtime", "tier": 3, "title": "Dan Slott solo: Big Time",
        "sub": "#648–700 · 2010–13 · selected arcs",
        "intro": "Peter takes a job at Horizon Labs. Brighter, gadget-heavy, "
                 "more optimistic.",
        "items": [
            item("bt-666", "“Spider-Island”", "#666–673",
                 "All of Manhattan gets spider-powers. Big, fun, well-built.", 1),
            item("bt-682", "“Ends of the Earth”", "#682–687",
                 "Doc Ock's endgame"),
            item("bt-698", "“Dying Wish”", "#698–700",
                 "Otto swaps minds with Peter, and Peter dies in Otto's body", 2),
        ],
    },
    {
        "id": "superior", "tier": 2, "title": "Superior Spider-Man",
        "sub": "#1–33 · 2013–14 · if you read one thing after One More Day",
        "links": [{"label": "The series", "url": S_SUP}],
        "intro": "Doctor Octopus, in Peter's body, sets out to be a better "
                 "Spider-Man than Peter ever was — and in measurable ways "
                 "succeeds. Greeted with fury on announcement, now widely "
                 "considered the best Spider-Man run of the century.",
        "items": [item("superior", "Superior Spider-Man", "#1–33", "", 2,
                       url=S_SUP)],
    },
    {
        "id": "modern", "tier": 3, "title": "The modern volumes",
        "sub": "2014 to now · Marvel Unlimited finds each by exact title and year",
        "items": [
            item("m-2014", "Amazing Spider-Man (2014)", "#1–18",
                 "Peter returns. Contains “Spider-Verse” (#9–15), the crossover "
                 "the animated films drew from.", 1),
            item("m-2015", "Amazing Spider-Man (2015–17)", "#1–32, #789–801",
                 "Parker Industries; Peter as globe-trotting CEO. Divisive, but "
                 "Slott's finale in #801 is genuinely lovely."),
            item("m-2018", "Amazing Spider-Man (2018–22)", "#1–74",
                 "Nick Spencer. The best-regarded post-One More Day run on the "
                 "main title, building across its full length toward an answer "
                 "to it. Highlights: “Hunted” (#16–23) and “Last Remains” (#50–55).",
                 1),
            item("m-2022", "Amazing Spider-Man (2022–25)", "#1–70",
                 "Zeb Wells. The run that broke a lot of people's patience — the "
                 "source wouldn't send you here.", url=S_2022),
            item("m-2025", "Amazing Spider-Man (2025– )", "#1–34",
                 "Joe Kelly and Pepe Larraz, twice monthly and well received, "
                 "building to ASM #1000 in September 2026. Marvel Unlimited adds "
                 "issues about three months after print.", url=S_2025),
        ],
    },
    {
        "id": "outside", "tier": 3, "title": "Outside continuity",
        "sub": "where a lot of the best modern Spider-Man actually lives",
        "items": [
            item("lifestory", "Spider-Man: Life Story", "#1–6",
                 "Zdarsky and Bagley. Six issues, one per decade, Peter ageing in "
                 "real time from 1962. Self-contained, and arguably the finest "
                 "Spider-Man comic of the last twenty years.", 2),
            item("ult2024", "Ultimate Spider-Man (2024–26)", "#1–24",
                 "Hickman and Checchetto. A complete, finished run. Peter becomes "
                 "Spider-Man in his mid-thirties, already married with two kids. "
                 "Openly the anti-One More Day.", 1, url=S_ULT24),
            item("ult2000", "Ultimate Spider-Man (2000–11)", "#1–160",
                 "Bendis and Bagley. Separate continuity, retells the origin, runs "
                 "eleven years. One of the great long runs in Marvel history.",
                 1),
            item("blue", "Spider-Man: Blue", "#1–6",
                 "Loeb and Sale. Peter looking back on Gwen — a good "
                 "decompression read after Part One."),
        ],
    },
]

PACE_TIERS = [1, 2]


def main():
    ids = [x["id"] for s in SECTIONS for x in s["items"]]
    if len(ids) != len(set(ids)):
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        raise SystemExit("duplicate item ids: %s" % dupes[:10])
    total = len(ids)

    tiers = {1: 0, 2: 0, 3: 0}
    for s in SECTIONS:
        tiers[s["tier"]] += len(s["items"])

    # the complete volume one, exactly as the source lists it
    v1 = [x for x in ids if x.startswith("asm-") and x[4:].isdigit()
          and int(x[4:]) <= 441]
    assert len(v1) == 441, len(v1)
    assert len([x for x in ids if x.startswith("asm-v2-")]) == 58
    resumed = [x for x in ids if x.startswith("asm-") and x[4:].isdigit()
               and 500 <= int(x[4:]) <= 545]
    assert len(resumed) == 46, len(resumed)

    issues = sum(x["w"] for s in SECTIONS for x in s["items"])
    paced = sum(x["w"] for s in SECTIONS if s["tier"] in PACE_TIERS
                for x in s["items"])
    partone = sum(x["w"] for s in SECTIONS if s["tier"] == 1 for x in s["items"])

    # every annotation and star must land on an item that exists
    used = {int(x["n"][1:]) for s in SECTIONS for x in s["items"]
            if x["t"] == "Amazing Spider-Man" and x["n"].startswith("#")
            and x["n"][1:].isdigit()}
    assert set(NOTES) <= used, sorted(set(NOTES) - used)
    assert set(STARS) <= used, sorted(set(STARS) - used)
    assert set(URLS) <= used, sorted(set(URLS) - used)

    prop = {
        "slug": SLUG,
        "title": "The Amazing Spider-Man",
        "subtitle": "Amazing Fantasy #15 to now",
        "kind": "comics",
        "order": 11,
        "year": "1962–",
        "blurb": "Part One is the complete run, every issue, %d of them. Part Two "
                 "is what's worth your time since." % partone,
        "unit": {"one": "entry", "many": "entries"},
        "weightUnit": {"one": "issue", "many": "issues"},
        "verb": {"base": "read", "past": "read", "ing": "reading"},
        "accent": "#B01E32",
        "accentDark": "#EC6B7B",
        "tiers": True,
        "paceTiers": PACE_TIERS,
        "paceLabel": "the optional modern runs",
        "notes": [
            ["Part One is meant to be read whole.", "Every issue from Amazing "
             "Fantasy #15 to One More Day is listed, in order, nothing filtered "
             "out. The notes are annotations, not selections: an issue with no "
             "note is a solid done-in-one with no lasting consequence, and "
             "reading those is a large part of what makes the runs feel like "
             "runs."],
            ["Tiers.", "1 is Part One, the complete read. 2 is Superior "
             "Spider-Man — the one thing to read after One More Day if you read "
             "only one. 3 is the rest of Part Two, which is explicitly a set of "
             "recommendations rather than a list to finish."],
            ["The finish date only covers Part One and Superior.", "Part One is "
             "%d issues; Superior Spider-Man is one more decision on top. "
             "Everything in the optional modern runs sits outside the timeline "
             "and never makes anyone late, and there is a checkbox under the bar "
             "if you want them counted." % partone],
            ["Bar widths.", "Most marks are a single issue, so most are the same "
             "width. The wide ones are entries that genuinely bundle several — "
             "Secret Wars #1–12, the Maximum Carnage legs, the chapters of The "
             "Other — and the pace line moves through issues rather than "
             "entries so those count for what they are."],
            ["Part Two entries count as one each.", "They are single decisions — "
             "whether you read that run — rather than a queue to be paced "
             "through, so Ultimate Spider-Man's 160 issues don't swallow the "
             "bar. The real lengths are in the issue numbers beside each one."],
            ["◆ marks a chapter published outside ASM.", "From 1976 to 1998 "
             "Spider-Man ran across three or four concurrent monthlies. ASM tells "
             "a complete story alone, but stories occasionally begin or end "
             "elsewhere; everything cross-title that genuinely matters is here as "
             "its own entry."],
            ["Links.", "Marvel gives issues arbitrary database ids with no "
             "pattern, and its series pages load their back catalogue through "
             "JavaScript that can't be paged from outside, so per-issue URLs "
             "can't be generated in bulk. The %d direct issue links are the ones "
             "that could be confirmed; everything else links at series level, "
             "which is how you'd navigate Marvel Unlimited anyway." % len(URLS)],
            ["A shorter path, if you want one.", "The spine is roughly 200 "
             "issues: Ditko #1–38, Conway #101–149, Stern #224–252, the "
             "black-suit years #252–300, then jump to JMS at vol. 2 #30 and read "
             "to #545. You lose surprisingly little."],
        ],
        "sections": SECTIONS,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json" % SLUG)
    print("  %d sections, %d entries, %d issues" % (len(SECTIONS), total, issues))
    print("  tier 1: %-4d tier 2: %-3d tier 3: %d   (entries)" % (tiers[1], tiers[2], tiers[3]))
    print("  part one: %d issues   on the clock: %d   optional: %d"
          % (partone, paced, issues - paced))
    print("  annotations: %d   stars: %d   direct links: %d"
          % (len(NOTES) + len(V2_NOTES), len(STARS) + len(V2_STARS), len(URLS)))
    for s in SECTIONS:
        print("   T%d  %-38s %4d entries %5d issues"
              % (s["tier"], s["title"][:38], len(s["items"]),
                 sum(x["w"] for x in s["items"])))


if __name__ == "__main__":
    main()
