#!/usr/bin/env python3
"""Generate properties/avatar.json.

    python tools/make_avatar.py

*Avatar: The Last Airbender* (61 chapters, three books) and *The Legend of
Korra* (52 chapters, four books) as one list of 113, in air order, one section
per book. Korra is a sequel rather than a spin-off — same world, same creators,
the next Avatar — so it belongs on the same page rather than on one of its own.

The live-action retellings, the 2010 film and the 2024 Netflix series, are not
here. They are separate works with their own reception and neither is an
episode of either show; the list's own notes say so, so the omission reads as a
decision rather than an oversight.

Everything numeric is enumerated from Wikipedia's episode tables — the seven
season articles the two "List of ... episodes" pages transclude — never from an
infobox count. The infobox totals and the series-overview per-book counts are
read as well and asserted against the enumerated rows, so an edit that
desynchronises a table from its own summary fails this generator loudly instead
of shipping a list that is quietly one episode short.

Two parsing details earned their code here:

  * Blocks are brace-balanced, not regex-terminated. "The Tales of Ba Sing Se"
    carries a multi-line {{efn}} whose closing braces sit on their own line; a
    non-greedy `.*?\\n}}` ends the block there and the episode silently loses
    its air date.
  * Fields are split at top-level pipes only, so a `|` inside a wikilink, a
    citation or a footnote cannot invent a field.

Nothing is weighted: see the note of the same name in the list.
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop, wiki                                    # noqa: E402

SLUG = "avatar"
ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "scratch" / "avatar"
WIKI = "https://en.wikipedia.org/wiki/"

# The totals this list signed up for. Enumerated rows must equal them, and so
# must the infobox and the series-overview figures on the source pages.
SERIES = [
    {
        "key": "atla",
        "title": "Avatar: The Last Airbender",
        "short": "The Last Airbender",
        "idp": "atla",
        "article": "Avatar: The Last Airbender",
        "list": "List of Avatar: The Last Airbender episodes",
        "seasons": ["Avatar: The Last Airbender season %d" % n for n in (1, 2, 3)],
        "total": 61,
        "books": [20, 20, 21],
    },
    {
        "key": "korra",
        "title": "The Legend of Korra",
        "short": "The Legend of Korra",
        "idp": "korra",
        "article": "The Legend of Korra",
        "list": "List of The Legend of Korra episodes",
        "seasons": ["The Legend of Korra season %d" % n for n in (1, 2, 3, 4)],
        "total": 52,
        "books": [12, 14, 13, 13],
    },
]

# Table entries that cover more than one numbered chapter, keyed by the overall
# numbers they span. Asserted against what the tables actually say, so the note
# naming them cannot drift away from the data.
MULTIPART = {
    "atla": [((7, 8), "Winter Solstice"),
             ((19, 20), "The Siege of the North"),
             ((50, 51), "The Day of Black Sun"),
             ((54, 55), "The Boiling Rock"),
             ((58, 59, 60, 61), "Sozin's Comet")],
    "korra": [((15, 16), "Civil Wars"),
              ((19, 20), "Beginnings")],
}

ORDINALS = ["One", "Two", "Three", "Four", "Five", "Six", "Seven"]
MONTHS = ["", "January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


# --------------------------------------------------------------- wikitext ---

def page(name):
    """Cached wikitext, comments stripped so they cannot unbalance braces."""
    text = wiki.wikitext(name, cache_dir=str(CACHE))
    assert text, "no wikitext for %s" % name
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def balanced_blocks(text, opener):
    """Every {{opener...}} in `text`, closed by brace counting.

    A non-greedy regex stops at the first `}}` on its own line, which is inside
    a multi-line footnote for at least one episode in this franchise.
    """
    out = []
    for m in re.finditer(r"\{\{(?:#invoke:)?%s" % opener, text, re.I):
        i, depth = m.start(), 0
        while i < len(text):
            if text.startswith("{{", i):
                depth += 1
                i += 2
            elif text.startswith("}}", i):
                depth -= 1
                i += 2
                if depth == 0:
                    break
            else:
                i += 1
        assert depth == 0, "unbalanced template at %d" % m.start()
        out.append(text[m.start():i])
    return out


def fields(block):
    """Named arguments of a template, split at top-level pipes only."""
    body, parts, buf, depth, i = block[2:-2], [], [], 0, 0
    while i < len(body):
        two = body[i:i + 2]
        if two in ("{{", "[["):
            depth += 1
            buf.append(two)
            i += 2
        elif two in ("}}", "]]"):
            depth -= 1
            buf.append(two)
            i += 2
        elif body[i] == "|" and depth == 0:
            parts.append("".join(buf))
            buf = []
            i += 1
        else:
            buf.append(body[i])
            i += 1
    parts.append("".join(buf))
    out = {}
    for p in parts[1:]:
        if "=" in p:
            k, v = p.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def title_of(raw):
    """A display title. <br /> is a line break inside a title, not a list
    separator, so it becomes a space before gwlib's cleaner turns it into a
    comma and leaves 'The Day of Black Sun,, Part 1'."""
    t = wiki.clean(re.sub(r"<br\s*/?>", " ", raw)).strip().strip('"')
    return re.sub(r"\s+", " ", t)


def date_of(raw):
    m = re.search(r"Start date\|(\d+)\|(\d+)\|(\d+)", raw)
    assert m, "no air date in %r" % raw[:80]
    return tuple(int(x) for x in m.groups())


def episodes_of(text):
    """(overall, in-book, title, air date) per numbered chapter, table order."""
    rows = []
    for block in balanced_blocks(text, "Episode list"):
        f = fields(block)
        parts = int(f.get("NumParts", 1))
        for i in range(1, parts + 1):
            sfx = "_%d" % i if parts > 1 else ""
            title = f.get("Title" + sfx)
            if not title:
                # one title over several chapters: The Boiling Rock, Civil Wars
                title = "%s, Part %d" % (title_of(f["Title"]), i)
            else:
                title = title_of(title)
            rows.append((int(f["EpisodeNumber" + sfx]),
                         int(f["EpisodeNumber2" + sfx]),
                         title,
                         date_of(f.get("OriginalAirDate" + sfx)
                                 or f["OriginalAirDate"]),
                         parts))
    return rows


def books_of(list_page_text):
    """(ordinal word, book name, displayed year span) per book heading."""
    out = re.findall(r"^===\s*Book ([A-Za-z]+):\s*''(.+?)''\s*\((.+?)\)\s*===\s*$",
                     list_page_text, re.M)
    assert out, "no book headings"
    return [(a, b.strip(), c.strip()) for a, b, c in out]


def overview_counts(list_page_text):
    """The per-book episode counts the list page's own summary box claims."""
    m = re.search(r"\{\{Series overview(.*?)\n\}\}", list_page_text, re.S)
    assert m, "no series overview"
    got = re.findall(r"\|\s*episodes(\d+)\s*=\s*(\d+)", m.group(1))
    return [int(n) for _, n in sorted(got, key=lambda kv: int(kv[0]))]


def infobox_total(article_text):
    f = wiki.infobox(article_text, kind=r"television")
    assert f, "no television infobox"
    return int(re.search(r"\d+", f("num_episodes")).group(0))


# ----------------------------------------------------------------- sections --

def collect(s):
    """Every chapter of one series, checked against every count the source
    publishes about itself."""
    rows = []
    for season in s["seasons"]:
        rows += episodes_of(page(season))

    nums = [r[0] for r in rows]
    assert nums == list(range(1, s["total"] + 1)), \
        "%s: episode numbers are %r, not 1..%d" % (s["key"], nums[:5], s["total"])
    assert len(rows) == s["total"], "%s: %d rows, expected %d" % (
        s["key"], len(rows), s["total"])

    # the tables are the authority; the infobox and the overview only get to
    # agree with them
    box = infobox_total(page(s["article"]))
    assert box == s["total"], \
        "%s: infobox says %d episodes, the tables enumerate %d" % (
            s["key"], box, s["total"])
    listing = page(s["list"])
    overview = overview_counts(listing)
    assert overview == s["books"], \
        "%s: series overview says %r, this list expects %r" % (
            s["key"], overview, s["books"])
    assert sum(overview) == s["total"], "%s: overview sums to %d" % (
        s["key"], sum(overview))

    books = books_of(listing)
    assert len(books) == len(s["books"]), \
        "%s: %d book headings, %d book counts" % (
            s["key"], len(books), len(s["books"]))
    assert [b[0] for b in books] == ORDINALS[:len(books)], \
        "%s: unexpected book ordinals %r" % (s["key"], [b[0] for b in books])

    # air order, which is also the order the tables are written in
    dates = [r[3] for r in rows]
    assert dates == sorted(dates), "%s: rows are not in air order" % s["key"]

    # multi-part entries, named in the notes, verified here
    groups, i = [], 0
    while i < len(rows):
        n = rows[i][4]
        if n > 1:
            groups.append(tuple(r[0] for r in rows[i:i + n]))
        i += n
    assert groups == [g for g, _ in MULTIPART[s["key"]]], \
        "%s: multi-part entries are %r" % (s["key"], groups)

    return rows, books


def sections_for(s, rows, books):
    out, first = [], 1
    for i, ((word, name, years), count) in enumerate(zip(books, s["books"]), 1):
        last = first + count - 1
        chunk = rows[first - 1:last]
        assert [r[1] for r in chunk] == list(range(1, count + 1)), \
            "%s book %d: in-book numbering is not 1..%d" % (s["key"], i, count)
        sec = {
            "id": "%s-b%d" % (s["idp"], i),
            "title": "%s · Book %s: %s" % (s["short"], word, name),
            "sub": "%s · %d episodes · %d–%d of %d" % (
                years, count, first, last, s["total"]),
            "links": [{"label": "Episode list",
                       "url": WIKI + s["seasons"][i - 1].replace(" ", "_")}],
            "items": [{"id": "%s-%d" % (s["idp"], r[0]),
                       "t": r[2],
                       "n": str(r[1])} for r in chunk],
        }
        if s["key"] == "atla" and i == 1:
            sec["open"] = True
        out.append(sec)
        first = last + 1
    assert first - 1 == s["total"]
    return out


def series_list(names):
    return ", ".join(names[:-1]) + " and " + names[-1]


def main():
    sections, spans, multi = [], [], []
    for s in SERIES:
        rows, books = collect(s)
        sections += sections_for(s, rows, books)
        spans.append((rows[0][3], rows[-1][3]))
        multi += [name for _, name in MULTIPART[s["key"]]]

    total = sum(s["total"] for s in SERIES)
    assert total == 113, total
    assert len(sections) == 7, len(sections)
    counted = sum(len(sec["items"]) for sec in sections)
    assert counted == total, (counted, total)

    first_year, last_year = spans[0][0][0], spans[-1][1][0]
    parts = sum(len(g) for s in SERIES for g, _ in MULTIPART[s["key"]])

    p = {
        "slug": SLUG,
        "title": "Avatar: The Last Airbender",
        "subtitle": "with The Legend of Korra",
        "kind": "animated series",
        # Nickelodeon's flagship, a theatrical film, a live-action remake and a
        # streaming revival keep the name in general circulation: it sits under
        # X-Men (86) and over Breaking Bad (84), with the catalogue's other
        # acclaimed-animation flagship, Brotherhood (83), a notch below.
        "popularity": 85,
        "year": "%d–%d" % (first_year, last_year),
        "blurb": "All %d episodes of both series in air order — %d chapters of "
                 "The Last Airbender, then Korra's %d."
                 % (total, SERIES[0]["total"], SERIES[1]["total"]),
        "unit": {"one": "episode", "many": "episodes"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        # a deep spirit-blue with a luminous arrow-cyan: the elements' own
        # colours are all spoken for in this catalogue, and this pair sits
        # further from its nearest neighbour (Cosmere) than the median list
        "accent": "#2B3F73",
        "accentDark": "#5FD3D9",
        "tiers": False,
        "notes": [
            ["One list, two series.",
             "The Legend of Korra is a sequel, not a spin-off: the same world, "
             "the same creators, the next Avatar. The Last Airbender's three "
             "books run first and Korra's four follow, which is air order and "
             "story order at once."],
            ["Books, not seasons.",
             "The franchise calls a season a Book and an episode a chapter, and "
             "both Wikipedia lists follow it. One section per book; the number "
             "on a row is its place within that book, and every section header "
             "carries the series-wide range so the %d and the %d stay countable."
             % (SERIES[0]["total"], SERIES[1]["total"])],
            ["The live-action versions are not here.",
             "The 2010 film and the 2024 Netflix series retell this story as "
             "separate works with their own reception, and neither is an "
             "episode of either show. Left out deliberately, not forgotten."],
            ["Multi-part chapters get a row each.",
             "%s table entries across the two series cover more than one "
             "numbered chapter — %s — %d chapters between them. Each part is "
             "numbered separately at the source, so each part is its own row "
             "here." % (ORDINALS[len(multi) - 1], series_list(multi), parts)],
            ["Nothing is weighted.",
             "The episode tables carry no per-episode runtime and each series "
             "infobox gives one blanket figure for every chapter, which is "
             "plainly wrong for a four-part finale that also aired as a "
             "two-hour television film. Repeating a number the source does not "
             "have per row would be inventing data, so nothing is weighted at "
             "all and all %d rows count the same." % total],
            "Titles, numbering and air dates are read from the seven Wikipedia "
            "season articles the two episode lists transclude. Both series "
            "totals and every book's count are checked against those lists' "
            "series-overview boxes and the series infoboxes; the generator "
            "fails rather than ship a list that disagrees with its sources.",
        ],
        "sections": sections,
    }

    out = prop.write(p)
    print("wrote %s" % out.name)
    print("  %d sections, %d episodes (%d + %d)"
          % (len(sections), counted, SERIES[0]["total"], SERIES[1]["total"]))
    for sec in sections:
        print("   %-40s %-34s %3d" % (sec["title"], sec["sub"], len(sec["items"])))


if __name__ == "__main__":
    main()
