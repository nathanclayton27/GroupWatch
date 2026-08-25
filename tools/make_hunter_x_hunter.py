#!/usr/bin/env python3
"""Generate properties/hunter-x-hunter.json — the 2011 series, arc by arc.

    PYTHONIOENCODING=utf-8 python tools/make_hunter_x_hunter.py

148 episodes in broadcast order, one section per arc. The arcs are not an
invention of this file: Wikipedia's "List of Hunter × Hunter (2011 TV series)
episodes" splits its episode tables under six `=== … arc ===` headings and
repeats the same six in a {{Series overview}} table, so the divisions are read
off the source and then checked against the source's own counts. Most shonen
episode lists offer nothing of the kind; this one does, so nothing here is
guessed.

THE 1999 SERIES AND THE OVAs ARE DELIBERATELY NOT HERE. They are a different
adaptation by a different studio that stops at a different point in the story,
and Wikipedia keeps them on their own pages. Folding them in would put two
incompatible completion states on one page — a member who finished this list
would be shown as part-way through a list they have finished — so this page is
the 2011 series and says so in its notes.

READING THE SOURCE. gwlib.wiki.episodes() is not used to build the rows, for
two reasons. The small one is CLU-167: that parser closes an {{Episode list}}
block at the first line-initial `}}`, truncates at a nested multi-line
template, and reads only the first number of a paired EpisodeNumber, all of
which drop rows silently. (This particular page uses none of those shapes —
checked — and gwlib does return all 148, but a reader that cannot be wrong is
better than one that happens not to be.) The deciding reason is that the arc
split needs each block's OFFSET in the page to attach it to the heading above
it, and gwlib returns no offsets. So this file carries its own brace-counting
reader, the way tools/make_star_trek.py's collector does: count `{{`/`}}` to
the matching close, then split the body on depth-zero pipes.

Nothing is weighted. See the WEIGHTING note in main().
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop, wiki

SLUG = "hunter-x-hunter"
PAGE = "List of Hunter × Hunter (2011 TV series) episodes"
CACHE = prop.ROOT / "scratch" / "hxh"

TOTAL = 148

# The six arcs, in broadcast order, with the count each must come to. Written
# here as well as read from the page so that a Wikipedia edit — a re-split arc,
# a row added or lost — fails this build loudly instead of quietly reshaping
# somebody's list. All three numbers have to agree: this table, the page's
# {{Series overview}}, and the rows actually enumerated under each heading.
ARCS = [
    ("hunter-exam",    "Hunter Exam",    26),
    ("heavens-arena",  "Heavens Arena",  12),
    ("phantom-troupe", "Phantom Troupe", 20),
    ("greed-island",   "Greed Island",   17),
    ("chimera-ant",    "Chimera Ant",    61),
    ("election",       "Election",       12),
]

# Section intros. Facts about what a section IS — its size, or the other name
# the source records for it — never what happens inside it.
INTROS = {
    "phantom-troupe": "The source also files this one as the Yorknew City "
                      "arc; the two names mean the same twenty episodes.",
    "chimera-ant": "Sixty-one episodes, more than the first three arcs put "
                   "together and the longest single run in the series.",
    "election": "The source also files this one as the 13th Hunter Chairman "
                "Election arc. Twelve episodes, and the end of the "
                "television series.",
}


def blocks(text, name="Episode list"):
    """(offset, block) for every {{name …}} template, matched by brace depth.

    Walks the text counting `{{` and `}}` rather than looking for a line that
    begins `}}`, so a nested template — cite, efn, start date — cannot end the
    block early.
    """
    out = []
    for m in re.finditer(r"\{\{\s*%s\s*(?=\||\n)" % re.escape(name), text):
        i, depth, j = m.start(), 0, m.start()
        while j < len(text):
            if text.startswith("{{", j):
                depth += 1
                j += 2
            elif text.startswith("}}", j):
                depth -= 1
                j += 2
                if depth == 0:
                    break
            else:
                j += 1
        assert depth == 0, "unclosed template at offset %d" % i
        out.append((i, text[i:j]))
    return out


def fields(block):
    """A template block's `|name = value` pairs, split on depth-zero pipes.

    Pipes inside `[[a|b]]` and `{{t|x|y}}` belong to those, not to the block,
    so the split tracks link and template depth as well.
    """
    body, depth, parts, cur, i = block[2:-2], 0, [], [], 0
    while i < len(body):
        two = body[i:i + 2]
        if two in ("{{", "[["):
            depth += 1
            cur.append(two)
            i += 2
        elif two in ("}}", "]]"):
            depth -= 1
            cur.append(two)
            i += 2
        elif body[i] == "|" and depth == 0:
            parts.append("".join(cur))
            cur = []
            i += 1
        else:
            cur.append(body[i])
            i += 1
    parts.append("".join(cur))
    out = {}
    for p in parts[1:]:                      # parts[0] is the template name
        if "=" in p:
            k, v = p.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def overview_counts(text):
    """The arc names and episode counts from the page's {{Series overview}}.

    A second statement of the same facts, made by the same page in a different
    table, used only to cross-check the enumerated rows — never as the source
    of the rows themselves.
    """
    seg = text[text.index("== Series overview =="):text.index("== Episodes ==")]
    out = []
    for n in range(1, 40):
        name = re.search(r"\|\s*linkT%d\s*=\s*(.*)" % n, seg)
        eps = re.search(r"\|\s*episodes%d\s*=\s*(\d+)" % n, seg)
        if not name or not eps:
            break
        out.append((name.group(1).strip(), int(eps.group(1))))
    return out


def read_episodes(text):
    """[(arc_heading, overall_no, no_in_arc, title)] for every enumerated row."""
    heads = [(m.start(), m.group(1).strip())
             for m in re.finditer(r"^===\s*(.*?)\s*===$", text, re.M)]
    assert heads, "no arc headings on the page"
    rows = []
    for pos, block in blocks(text):
        before = [h for hp, h in heads if hp < pos]
        assert before, "an episode block sits above the first arc heading"
        f = fields(block)
        title = wiki.clean(f.get("Title", "")).strip('"')
        assert title, "row with no title near offset %d" % pos
        rows.append((before[-1], int(f["EpisodeNumber"]),
                     int(f["EpisodeNumber2"]), title))
    return rows


def main():
    text = wiki.wikitext(PAGE, cache_dir=CACHE)
    assert text, "could not read %s" % PAGE

    rows = read_episodes(text)
    assert len(rows) == TOTAL, \
        "expected %d enumerated rows, read %d" % (TOTAL, len(rows))
    assert [r[1] for r in rows] == list(range(1, TOTAL + 1)), \
        "broadcast numbering is not a clean 1..%d run" % TOTAL

    # The page's own arc table has to agree with the rows and with ARCS above.
    overview = overview_counts(text)
    assert overview == [(name, n) for _, name, n in ARCS], \
        "the page's arc table has changed: %r" % (overview,)
    assert sum(n for _, _, n in ARCS) == TOTAL, "ARCS does not sum to %d" % TOTAL

    grouped, order = {}, []
    for head, overall, in_arc, title in rows:
        if head not in grouped:
            grouped[head] = []
            order.append(head)
        grouped[head].append((overall, in_arc, title))
    assert len(order) == len(ARCS), \
        "expected %d arc headings, found %d" % (len(ARCS), len(order))

    sections = []
    for (sid, name, count), head in zip(ARCS, order):
        eps = grouped[head]
        assert head.startswith(name + " arc"), \
            "heading %r is not the %s arc" % (head, name)
        assert len(eps) == count, \
            "%s: page enumerates %d rows, expected %d" % (name, len(eps), count)
        assert [e[1] for e in eps] == list(range(1, count + 1)), \
            "%s: the arc's own numbering is not 1..%d" % (name, count)
        years = re.search(r"\((\d{4}(?:–\d{2,4})?)\)", head)
        assert years, "no year range in heading %r" % head
        sec = {
            "id": sid,
            "title": "%s arc" % name,
            "sub": "episodes %d–%d · %d episodes · %s"
                   % (eps[0][0], eps[-1][0], count, years.group(1)),
            "items": [{"id": "hxh-%d" % overall, "t": title, "n": str(overall)}
                      for overall, _, title in eps],
        }
        if sid in INTROS:
            sec["intro"] = INTROS[sid]
        sections.append(sec)
    sections[0]["open"] = True

    # WEIGHTING. Unweighted, and that is a decision rather than an omission.
    # The source's episode tables carry titles, directors, writers and air
    # dates and no runtimes at all, so a weight here would be a nominal figure
    # invented on this side of the wire. Half-weighting is worse than none:
    # the strip reads a row with no weight as one hour, so a list where some
    # rows carry real minutes and the rest do not is silently wrong about its
    # own length (CLU-131). 148 equal marks instead.
    assert not any("w" in x for s in sections for x in s["items"]), \
        "a weight leaked into an unweighted list"

    p = {
        "slug": SLUG,
        "title": "Hunter × Hunter",
        "subtitle": "the 2011 series",
        "kind": "anime",
        # Band 70-79 in POPULARITY.md: the canonical "anyone into this has
        # heard of it". A Weekly Shonen Jump flagship whose anime is a fixture
        # of every best-of-the-medium list and which ran on Toonami in the US,
        # but a title a general audience would still have to be told about —
        # so below Naruto 90, Dragon Ball 89, Attack on Titan 84 and
        # Fullmetal Alchemist: Brotherhood 83, which a non-viewer can name,
        # and beside JoJo 71 and Cowboy Bebop 73.
        "popularity": 72,
        "year": "2011–2014",
        "blurb": "All 148 episodes of the 2011 series in broadcast order, "
                 "split into the six arcs it was broadcast as.",
        "unit": {"one": "episode", "many": "episodes"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        # A yellow-green measured in CIELAB against every accent and
        # accentDark in properties/index.json — see scratch/hxh/pick_accent.py.
        # Nearest neighbours: #4E8F00 sits 16.2 from fps-canon's #10851E and
        # 17.6 from Urusei Yatsura's #4C7A1D; #8CE83C sits 17.1 from President
        # Curtis's #A8D93F. The catalogue's other greens are muted or olive,
        # and the one saturated green corner is fps-canon's, so this pair
        # takes the yellow side of the hue that nothing else occupies.
        "accent": "#4E8F00",
        "accentDark": "#8CE83C",
        "tiers": False,
        "notes": [
            ["The 2011 series, and only the 2011 series.",
             "148 episodes made by Madhouse, broadcast from October 2011 to "
             "September 2014. The 1999 series and the OVAs that continued it "
             "are a separate adaptation, by a different studio, that stops at "
             "a different point in the story — Wikipedia keeps them on their "
             "own pages and so does this list. Putting both on one page would "
             "mean two incompatible ideas of what finishing it looks like, "
             "and a group that watched every episode here would still be "
             "shown as part-way through."],
            ["The sections are the broadcast arcs.",
             "Six of them, and they are the source's own divisions rather "
             "than anything drawn here: Hunter Exam 26 episodes, Heavens "
             "Arena 12, Phantom Troupe 20, Greed Island 17, Chimera Ant 61 "
             "and Election 12. An arc boundary is the natural place to stop "
             "for the night."],
            ["The numbers are the broadcast numbers.",
             "Every row is numbered 1–148 across the whole run. The "
             "source also numbers each arc from 1, which is why the same "
             "episode can be called both 137 and Election 1 elsewhere; each "
             "section heading gives the range it covers and how long it is."],
            ["Nothing is weighted.",
             "148 equal marks. The episode tables carry no runtimes, so any "
             "weight here would be a number invented rather than read, and a "
             "list where only some rows are weighted counts the rest as an "
             "hour each and lies about its own length."],
            "Episode titles, arc divisions and arc counts machine-read from "
            "Wikipedia's list of the 2011 series' episodes; every arc's count "
            "is checked against that page's own arc table, and the run is "
            "checked for a clean 1–148, before this file is written.",
        ],
        "sections": sections,
    }

    out = prop.write(p)
    total = sum(len(s["items"]) for s in sections)
    assert total == TOTAL, "wrote %d episodes, expected %d" % (total, TOTAL)
    print("wrote %s — %d episodes in %d arcs" % (out.name, total, len(sections)))
    for s in sections:
        print("   %-18s %3d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
