#!/usr/bin/env python3
"""Generate properties/death-note.json — Death Note (2006-07), the anime.

    python tools/make_death-note.py

37 episodes in broadcast order, machine-read from the wikitext of Wikipedia's
"List of Death Note episodes", cached at scratch/deathnote/. Re-running against
the cache is byte-identical; delete the cache to refetch.

SECTIONS are the source's own. That page files the run under two headings,
=== Part I === and === Part II ===, each with an HTML comment reading
"Official narrative-wise, not release-wise" — a division the production makes,
not one this generator invented. It falls at 26/11 and the parser asserts that,
so if the page ever re-cuts it the build fails instead of shipping a stale
split. Nothing else about the split is described: the headers carry episode
ranges and air dates and no more.

SPOILERS. The show is built on its turns, so no row carries a note and no
section carries an intro. Titles ship exactly as the source has them, including
the loaded ones — a title is what an episode IS, and every list in this
catalogue prints titles. What is refused is any sentence about what happens,
which is why the {{Episode list}} ShortSummary fields are parsed past and
dropped. The same care applies to the exclusions note: the two Relight specials
are named by series and year rather than by their subtitles, one of which gives
away a turn on its own.

UNWEIGHTED, deliberately. The episode list carries no runtime column, so there
is no per-episode figure to verify; every row is one television episode of the
same nominal length, and the list is homogeneous, so nothing is weighted and
the strip counts episodes. Weighting some rows and not others is the failure
this avoids — an unweighted row inside a weighted list silently counts as one
hour.

OUT OF SCOPE, and said in the notes so it reads as a decision: the two Relight
television specials, the Japanese live-action films, the 2015 drama, and the
2017 Netflix film.
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop, wiki  # noqa: E402

SLUG = "death-note"
PAGE = "List of Death Note episodes"
CACHE = pathlib.Path(__file__).resolve().parent.parent / "scratch" / "deathnote"

# The page's own headings, and the count each must hold. Asserted rather than
# trusted: the split is the only editorial claim this list makes, so a re-cut
# upstream should break the build, not quietly reshape the sections.
PARTS = [
    ("part1", "=== Part I ===",  "Part I",  26, "4 October 2006 – 11 April 2007"),
    ("part2", "=== Part II ===", "Part II", 11, "18 April 2007 – 27 June 2007"),
]

TOTAL = 37
# The Relight specials live under their own heading, after the episode tables.
# The slice stops here; the assert below proves they never entered the list.
END = "== ''Relight'' TV films =="
RELIGHT = re.compile(r"Relight", re.I)


def part_segments(text):
    """The Episodes section, sliced at the page's own Part headings."""
    bounds = []
    for _, heading, _, _, _ in PARTS:
        i = text.find(heading)
        assert i >= 0, "the page no longer carries the heading %r" % heading
        bounds.append(i)
    end = text.find(END)
    assert end > bounds[-1], "the Relight heading has moved above the episodes"
    assert bounds == sorted(bounds), "the Part headings are out of order"
    return [text[a:b] for a, b in zip(bounds, bounds[1:] + [end])]


def main():
    text = wiki.wikitext(PAGE, cache_dir=CACHE)
    assert text, "could not read %r" % PAGE

    sections, seen = [], 0
    for (sid, _, title, count, aired), seg in zip(PARTS, part_segments(text)):
        eps = wiki.episodes(seg)
        assert len(eps) == count, \
            "%s now holds %d episodes, not %d — the source has re-cut the " \
            "split and the sections need revisiting" % (title, len(eps), count)
        nums = [n for n, _, _, _, _ in eps]
        assert nums == list(range(seen + 1, seen + count + 1)), \
            "%s numbers %r are not the contiguous run %d-%d" \
            % (title, nums, seen + 1, seen + count)
        for _, _, t, _, _ in eps:
            assert t, "an episode in %s has no title" % title
            assert not RELIGHT.search(t), "a Relight special leaked into %s" % title

        sections.append({
            "id": sid,
            "title": title,
            "sub": "episodes %d–%d · %s" % (seen + 1, seen + count, aired),
            "links": [{"label": "The episode list",
                       "url": "https://en.wikipedia.org/wiki/"
                              "List_of_Death_Note_episodes"}],
            "open": sid == "part1",
            # No note field anywhere: see the spoiler paragraph above.
            "items": [{"id": "dn-%d" % n, "t": t, "n": str(n)}
                      for n, _, t, _, _ in eps],
        })
        seen += count

    assert seen == TOTAL, "built %d episodes, expected %d" % (seen, TOTAL)

    p = {
        "slug": SLUG,
        "title": "Death Note",
        "subtitle": "the anime",
        "kind": "anime",
        # 80-89: a mainstream audience recognises the title on sight. Level
        # with Fullmetal Alchemist: Brotherhood at 83 — the same tier of
        # recognition, and POPULARITY.md says a tie is legal and expected
        # rather than a thing to break with false precision. Below Dragon Ball
        # at 89, above Evangelion at 75 and Cowboy Bebop at 73.
        "popularity": 83,
        "year": "2006–2007",
        "blurb": "All 37 episodes in broadcast order. The anime only.",
        "unit": {"one": "episode", "many": "episodes"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        # A deep blood red against a scarlet that lifts in the dark theme. The
        # two obvious readings of this show are both taken: near-black is A24's
        # accent exactly (#111111) with Junji Ito 4.7 away, and a mid blood red
        # lands 1.8 from Everything Dies: Secret Wars and 2.4 from Lego Games.
        # This pair sits 15.8 (CIELAB) from its nearest light-mode neighbour,
        # The Sopranos #6B1F1F, and 14.2 from its nearest dark-mode neighbour,
        # Berserk #E03A3A.
        "accent": "#6C0000",
        "accentDark": "#FF2E3C",
        "tiers": False,
        "notes": [
            ["Two parts, because the source has two parts.",
             "Wikipedia's episode list files the run under Part I and Part II "
             "— a narrative division rather than a broadcast one; the show "
             "aired as a single continuous run. The sections here are that "
             "split and nothing else. The headers carry episode ranges and "
             "air dates, and no description."],
            ["No episode notes, on purpose.",
             "This show is its turns, and a one-line summary gives several of "
             "them away. Nothing here describes what happens in an episode. "
             "The titles are the official titles, printed as the source has "
             "them — a title is what an episode is called, not what it does."],
            ["Unweighted.",
             "The episode list carries no runtimes, so there is no per-episode "
             "figure anyone could check. Every row is one television episode "
             "of the same nominal length, so the strip counts episodes and "
             "nothing carries a weight."],
            ["What is out.",
             "The two Relight television specials, from 2007 and 2008, which "
             "recut the series into digest form rather than adding to it. "
             "Also out: the Japanese live-action films, the 2015 television "
             "drama, and the 2017 Netflix film. This list is the anime."],
            "Episode numbers and titles machine-read from Wikipedia's List of "
            "Death Note episodes; the Part I / Part II split is that page's "
            "own.",
        ],
        "sections": sections,
    }

    out = prop.write(p)
    print("wrote %s — %d episodes" % (out.name, seen))
    for s in sections:
        print("   %-8s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
