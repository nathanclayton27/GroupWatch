#!/usr/bin/env python3
"""Generate properties/cates-venom.json — Donny Cates' Venom run.

    python3 tools/make_venom.py

Tiers: 1 is the spine Cates wrote, 2 is supplemental material worth the time,
3 is genuinely optional. The section intros are deliberately spoiler-light —
they exist so you can skip thirty years of prior comics, not so you can skip
this one.

Order compiled from How To Love Comics, Comic Book Treasury, Comic Book Herald
and comicbookreadingorders.com. Where those disagree on interleaving, the
event issues are cut into the main run at chapter boundaries, which is how the
omnibus reads.
"""
import json
import pathlib

SLUG = "cates-venom"


def it(title, num, note="", star=0, opt=0, key=None):
    slug = key or (
        title.lower()
        .replace("'", "").replace(".", "").replace(":", "")
        .replace("/", "-").replace(" ", "-")
        + "-" + str(num).lstrip("#")
    )
    x = {"id": "venom-" + slug, "t": title, "n": "#" + str(num).lstrip("#")}
    if note:
        x["note"] = note
    if star:
        x["star"] = star
    if opt:
        x["opt"] = opt
    return x


def vn(n, note="", star=0):
    return it("Venom", n, note, star)


def rng(title, a, b, note_first=""):
    out = []
    for n in range(a, b + 1):
        out.append(it(title, n, note_first if n == a else ""))
    return out


SECTIONS = [
    {
        "id": "rex", "tier": 1, "title": "Rex",
        "sub": "Venom #1–6 · the run's opening statement",
        "intro":
            "Eddie Brock is a disgraced journalist. The symbiote is an alien that "
            "bonded to Spider-Man in the eighties, was rejected, and found Eddie "
            "instead — they shared a grudge, and that grudge became Venom. In the "
            "thirty years since, the character has been a villain, an antihero and "
            "a self-declared lethal protector, and Eddie has been separated from "
            "and rebonded to the symbiote more times than is worth counting.\n\n"
            "You need none of it. Cates reintroduces Eddie in the first few pages "
            "and treats the symbiote's history as something nobody has told the "
            "truth about — including the symbiote. Starting cold is close to the "
            "intended experience.",
        "items":
            [vn(1, "the pitch, in one issue", 2), vn(2), vn(3)]
            + [it("Web of Venom: Ve'Nam", 1,
                  "Vietnam, 1968 — the flashback the arc keeps gesturing at", 1,
                  key="wov-venam")]
            + [vn(4), vn(5), vn(6, "", 1)],
    },
    {
        "id": "abyss", "tier": 1, "title": "The Abyss",
        "sub": "Venom #7–12 · the fallout, and what Eddie is carrying",
        "items": rng("Venom", 7, 12)
                 + [it("Venom Annual", 1, "anthology; the Cates story is the reason",
                       0, 1, key="annual-1")],
    },
    {
        "id": "wotr", "tier": 3, "title": "War of the Realms",
        "sub": "Venom #13–15 · a detour, and not Cates'",
        "intro":
            "War of the Realms was a line-wide 2019 event: Malekith the Accursed "
            "invades Earth with the armies of the ten realms and every hero fights "
            "a war on a different front. These three issues are Venom's corner of "
            "it, written by Cullen Bunn rather than Cates.\n\n"
            "Nothing in the main run depends on them. They are here for "
            "completeness — skip to the next section without consequence.",
        "items": [it("Venom", n, "", 0, 1) for n in range(13, 16)],
    },
    {
        "id": "road-ac", "tier": 2, "title": "Road to Absolute Carnage",
        "sub": "the setup · read before the event",
        "intro":
            "Cletus Kasady is a serial killer who bonded with the symbiote's "
            "offspring and became Carnage — stronger than Venom, without any of "
            "the parts of Eddie that pull him back. His 1993 rampage through New "
            "York is the story people mean when they call him Marvel's worst. He "
            "has died more than once, and he is dead when this run opens.\n\n"
            "That is the whole briefing. What matters going in is that he is a "
            "murderer with a symbiote, and that every symbiote leaves a trace in "
            "a host it has bonded with — which is about to be a problem for "
            "everyone who has ever worn one.",
        "items": [
            it("Web of Venom: Carnage Born", 1, "the one to not skip", 1, key="wov-carnage-born"),
            it("Free Comic Book Day: Spider-Man/Venom", 1, "2019 · short prelude", 0, 1,
               key="fcbd-2019"),
            vn(16, "the hinge into the event"),
        ],
    },
    {
        "id": "absolute-carnage", "tier": 1, "title": "Absolute Carnage",
        "sub": "the event, cut into the run · Cates wrote both halves",
        "intro":
            "The main series and the Venom tie-in were written by the same person "
            "at the same time, and they interleave chapter for chapter. Read them "
            "cut together as below rather than one after the other.",
        "items": [
            it("Absolute Carnage", 1, "", 2, key="ac-1"),
            vn(17),
            it("Absolute Carnage", 2, "", 0, key="ac-2"),
            vn(18),
            it("Web of Venom: Funeral Pyre", 1, "", 0, key="wov-funeral-pyre"),
            it("Absolute Carnage", 3, "", 0, key="ac-3"),
            vn(19),
            it("Absolute Carnage", 4, "", 0, key="ac-4"),
            vn(20),
            it("Absolute Carnage", 5, "", 1, key="ac-5"),
        ],
    },
    {
        "id": "ac-tie-ins", "tier": 3, "title": "Absolute Carnage tie-ins",
        "sub": "the ones worth it, of about a dozen",
        "intro":
            "Cates' own advice was that the main series plus the Venom tie-in is "
            "enough. These four are the ones that earn their place anyway. The "
            "other tie-ins — Deadpool, Avengers, Captain Marvel, Weapon Plus, "
            "Symbiote Spider-Man, Separation Anxiety, Symbiote of Vengeance — are "
            "fine and entirely skippable.",
        "items":
            [it("Absolute Carnage: Scream", n, "the best of them" if n == 1 else "", 1 if n == 1 else 0, 1, key="ac-scream-%d" % n) for n in (1, 2, 3)]
            + [it("Absolute Carnage: Miles Morales", n, "", 0, 1, key="ac-miles-%d" % n) for n in (1, 2, 3)]
            + [it("Absolute Carnage: Lethal Protectors", n, "", 0, 1, key="ac-lethal-%d" % n) for n in (1, 2, 3)]
            + [it("Absolute Carnage: Immortal Hulk", 1, "", 0, 1, key="ac-hulk-1")],
    },
    {
        "id": "aftermath", "tier": 2, "title": "After the carnage",
        "sub": "two one-shots that carry weight later",
        "items": [
            it("Web of Venom: Cult of Carnage", 1, "", 0, key="wov-cult"),
            it("Web of Venom: The Good Son", 1, "Dylan; matters more than it looks", 1,
               key="wov-good-son"),
        ],
    },
    {
        "id": "island", "tier": 1, "title": "Venom Island",
        "sub": "Venom #21–25 · Eddie alone, at his worst",
        "items": rng("Venom", 21, 25),
    },
    {
        "id": "beyond", "tier": 1, "title": "Venom Beyond",
        "sub": "Venom #26–30",
        "items": rng("Venom", 26, 30),
    },
    {
        "id": "road-kib", "tier": 2, "title": "Road to King in Black",
        "sub": "the last breath before the sky goes dark",
        "intro":
            "One piece of outside context: Empyre was a 2020 event in which the "
            "Kree and the Skrulls united under one emperor and turned on Earth. "
            "Venom's connection is glancing — a single one-shot tidying an "
            "aftermath thread. Knowing it happened is enough; you do not need to "
            "have read it.",
        "items": [
            it("Web of Venom: Wraith", 1, "", 1, key="wov-wraith"),
            it("Web of Venom: Empyre's End", 1, "", 0, key="wov-empyres-end"),
            it("Free Comic Book Day: Spider-Man/Venom", 1, "2020 · short prelude", 0, 1,
               key="fcbd-2020"),
        ],
    },
    {
        "id": "king-in-black", "tier": 1, "title": "King in Black",
        "sub": "the payoff · main series cut with Venom #31–34",
        "items": [
            it("King in Black", 1, "", 2, key="kib-1"),
            vn(31),
            it("King in Black", 2, "", 0, key="kib-2"),
            vn(32),
            it("King in Black", 3, "", 0, key="kib-3"),
            vn(33),
            it("King in Black", 4, "", 0, key="kib-4"),
            vn(34),
            it("King in Black", 5, "", 1, key="kib-5"),
        ],
    },
    {
        "id": "kib-tie-ins", "tier": 3, "title": "King in Black tie-ins",
        "sub": "three of many",
        "items":
            [it("King in Black: Namor", n, "the strongest tie-in" if n == 1 else "", 1 if n == 1 else 0, 1, key="kib-namor-%d" % n) for n in range(1, 6)]
            + [it("King in Black: Planet of the Symbiotes", n, "", 0, 1, key="kib-planet-%d" % n) for n in (1, 2, 3)]
            + [it("King in Black: Gwenom vs. Carnage", n, "", 0, 1, key="kib-gwenom-%d" % n) for n in (1, 2, 3)],
    },
    {
        "id": "finale", "tier": 1, "title": "The 200th issue",
        "sub": "Venom #35 · the end of the run",
        "items": [vn(35, "legacy #200 — Cates and Stegman sign off", 2)],
    },
    {
        "id": "orbit", "tier": 3, "title": "Elsewhere in the same cosmology",
        "sub": "Cates was writing this alongside Venom",
        "intro":
            "Silver Surfer Black ran during this period, by the same writer, and "
            "reaches the same mythology from the far end — the Surfer thrown back "
            "toward the beginning of everything. It answers a question the Venom "
            "run spends years circling.\n\n"
            "Read it after King in Black if you would rather the main run explain "
            "itself in its own time. It is a better comic than it needs to be.",
        "items": [it("Silver Surfer Black", n, "" if n > 1 else "gorgeous", 1 if n == 1 else 0, 1,
                     key="ssb-%d" % n) for n in range(1, 6)],
    },
]


def main():
    seen = set()
    for s in SECTIONS:
        for x in s["items"]:
            if x["id"] in seen:
                raise SystemExit("duplicate id %s" % x["id"])
            seen.add(x["id"])

    total = len(seen)
    tiers = {1: 0, 2: 0, 3: 0}
    for s in SECTIONS:
        tiers[s["tier"]] += len(s["items"])

    prop = {
        "slug": SLUG,
        "title": "Venom",
        "subtitle": "Donny Cates & Ryan Stegman",
        "kind": "comics",
        "year": "2018–2021",
        "order": 3,
        "blurb": "The whole Cates run, with the supplements worth reading and "
                 "enough backstory to start cold.",
        "unit": {"one": "issue", "many": "issues"},
        "verb": {"base": "read", "past": "read", "ing": "reading"},
        "accent": "#7A4FB5",
        "tiers": True,
        "notes": [
            ["Tiers.", "1 is the spine Cates wrote and the run does not work "
                       "without it. 2 is supplemental material worth the time. 3 is "
                       "genuinely optional — event tie-ins and a detour written by "
                       "someone else. Tier 1 alone is a complete read."],
            ["The intros.", "Sections that need prior context have a short explainer "
                            "at the top. They are written to save you thirty years of "
                            "reading, and kept as spoiler-light as that allows."],
            "Order compiled from How To Love Comics, Comic Book Treasury, Comic Book "
            "Herald and comicbookreadingorders.com. Where sources disagree on how the "
            "events interleave, the tie-in issues are cut into the main run at chapter "
            "boundaries, which is how the omnibus reads.",
            "No Marvel links on this one yet — the series ids would have to be looked "
            "up per title, and a wrong link is worse than none.",
        ],
        "sections": SECTIONS,
    }

    out = pathlib.Path(__file__).resolve().parent.parent / "properties" / ("%s.json" % SLUG)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")

    print("wrote %s.json" % SLUG)
    print("  %d sections, %d issues" % (len(SECTIONS), total))
    print("  tier 1: %d   tier 2: %d   tier 3: %d" % (tiers[1], tiers[2], tiers[3]))
    for s in SECTIONS:
        print("   T%d  %-28s %3d%s"
              % (s["tier"], s["title"][:28], len(s["items"]),
                 "  (intro)" if s.get("intro") else ""))


if __name__ == "__main__":
    main()
