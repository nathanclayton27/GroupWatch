#!/usr/bin/env python3
"""Generate properties/invincible.json — Invincible (2021–), the animated series.

    python tools/make_invincible.py

33 episodes across four aired seasons, in broadcast order, machine-read from
the wikitext of the four Wikipedia season articles ("Invincible season 1" …
"Invincible season 4"), cached under scratch/invincible/. Re-running against
the cache is byte-identical; delete the cache to refetch.

TITLES ONLY. No row carries a note and no section carries an intro. This show
is built on its turns and a one-sentence summary hands them over, so the
per-episode summaries the source carries are refused rather than trimmed —
the same call the Death Note list made, and said out loud in its own notes so
a reader knows the blank column is a decision and not a gap.

That refusal is enforced by the reader below rather than left to discipline.
`fields()` keeps a whitelist — EpisodeNumber, EpisodeNumber2, Title,
OriginalAirDate — and drops everything else, so a ShortSummary is never even
returned to the code that builds rows; DROPPED asserts one was present in
every block, so a source that stops carrying summaries fails loudly instead
of quietly changing what this file is refusing. The last guard in main()
re-reads the emitted JSON and asserts no 40-character run of any dropped
summary survived into it.

A HAND-ROLLED READER, and why. gwlib.wiki.episodes() reads this source's rows
at the right count, but two of the titles carry a long inline HTML editor's
comment (`We Need to Talk<!--Do NOT change this…-->`) and gwlib.clean() does
not strip HTML comments — the shared parser hands back the comment glued to
the title. Rather than special-case that, the reader here counts braces to
find each {{Episode list}} template whole, splits its fields at brace depth
zero, and strips comments before cleaning. Brace counting also makes the
CLU-167 failure modes structurally impossible here: a line-initial `}}` or a
nested multi-line template inside a summary cannot truncate a block, because
nothing about the block's extent depends on where the lines break.

THE SPECIAL IS IN. Wikipedia's season 2 table opens with "Invincible: Atom
Eve", released July 2023, filed under the table's own "Special" part and
numbered 9 in the series' overall run. Rows here carry the source's overall
numbers, so leaving it out would put a hole at 9. It aired, it is in the
enumerated table, it is listed — 8 + 9 + 8 + 8 = 33.

COUNTS ARE ASSERTED AGAINST THE TABLES, never the {{Series overview}} box at
the top of the parent article. Per-season expectations live in SEASONS below
and a mismatch fails the build.

CUT-OFF FROZEN. AS_OF is a constant, not date.today(): every episode must
have aired on or before it. Nothing is mid-run right now — season 4 finished
on 22 April 2026 — but the constant is what keeps two runs of this file in
agreement if a season 5 table appears upstream before anyone revisits this.

UNWEIGHTED, deliberately. The {{Episode table}} headers declare overall,
season, title, director, writer and airdate columns and no runtime column, so
there is no per-episode figure anybody could check. Every row is one episode
of the same nominal length; nothing is weighted and the strip counts
episodes. Weighting some rows and not others is the failure this avoids.

OUT OF SCOPE: the Invincible comic (Image Comics, 2003–2018) is a separate
work in a separate medium and belongs on its own card, not folded in here.
"""
import json
import pathlib
import re
import sys
from datetime import date

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gwlib import prop, wiki  # noqa: E402

SLUG = "invincible"
CACHE = pathlib.Path(__file__).resolve().parent.parent / "scratch" / "invincible"

# Frozen build cut-off. Nothing dated after this may enter the list, and this
# is a constant on purpose: reading the clock would make the file differ by
# the day and re-runs would stop being byte-identical.
AS_OF = date(2026, 8, 24)

# season number, Wikipedia page, section title, episode count in that page's
# own table. The counts are asserted, not trusted — see the docstring.
SEASONS = [
    (1, "Invincible season 1", "Season 1", 8),
    (2, "Invincible season 2", "Season 2", 9),
    (3, "Invincible season 3", "Season 3", 8),
    (4, "Invincible season 4", "Season 4", 8),
]
TOTAL = 33

# the only fields that leave the reader. Everything else — ShortSummary above
# all, but also director, writer, line colour — is dropped at the source.
KEEP = ("EpisodeNumber", "EpisodeNumber2", "Title", "OriginalAirDate")
DROPPED = "ShortSummary"

MONTHS = ("January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December")


def templates(text, name):
    """Every {{name…}} template in `text`, whole, found by counting braces.

    Returns the full template text including its delimiters. Line breaks are
    irrelevant to the scan, which is the point: a line-initial `}}` inside a
    field, or a nested template spanning lines, cannot end a block early.
    """
    out, i, n = [], 0, len(text)
    open_at = "{{" + name
    while True:
        start = text.find(open_at, i)
        if start < 0:
            return out
        j, depth = start, 0
        while j < n:
            if text[j:j + 2] == "{{":
                depth += 1
                j += 2
            elif text[j:j + 2] == "}}":
                depth -= 1
                j += 2
                if depth == 0:
                    break
            else:
                j += 1
        assert depth == 0, "unclosed %s template at offset %d" % (name, start)
        out.append(text[start:j])
        i = j


def fields(block):
    """A template's named fields, split at brace/bracket depth zero.

    Only KEEP survives; DROPPED must have been present and is thrown away
    unread. Returns (kept, dropped_summary_text) — the summary comes back
    only so main() can prove it never reached the output, and nothing else
    in this file may look at it.
    """
    inner = block[2:-2]
    parts, buf, depth, link = [], [], 0, 0
    i, n = 0, len(inner)
    while i < n:
        two = inner[i:i + 2]
        if two == "{{":
            depth += 1
            buf.append(two)
            i += 2
        elif two == "}}":
            depth -= 1
            buf.append(two)
            i += 2
        elif two == "[[":
            link += 1
            buf.append(two)
            i += 2
        elif two == "]]":
            link -= 1
            buf.append(two)
            i += 2
        elif inner[i] == "|" and depth == 0 and link == 0:
            parts.append("".join(buf))
            buf = []
            i += 1
        else:
            buf.append(inner[i])
            i += 1
    parts.append("".join(buf))

    kept, summary = {}, None
    for part in parts[1:]:
        m = re.match(r"\s*([A-Za-z][A-Za-z0-9_]*)\s*=(.*)$", part, re.S)
        if not m:
            continue                      # positional arg: the sublist page
        key, value = m.group(1), m.group(2)
        if key in KEEP:
            kept[key] = value.strip()
        elif key == DROPPED:
            summary = value              # held only for the guard in main()
    assert summary is not None, \
        "a block carries no %s — the source has changed shape and this " \
        "generator's refusal no longer means what it says" % DROPPED
    return kept, summary


def title_of(raw):
    """A display title: HTML comments out first, then the shared cleaner.

    The comment strip is the reason this file does not use wiki.clean() on
    its own — two of these titles carry a multi-sentence editor's note inline
    and clean() would ship it.
    """
    t = re.sub(r"<!--.*?-->", "", raw, flags=re.S)
    return wiki.clean(t).strip('"')


def air_date(raw):
    """{{Start date|Y|M|D}} -> date. Anything else is a build failure."""
    m = re.search(r"\{\{\s*Start date\s*\|\s*(\d{4})\s*\|\s*(\d{1,2})\s*\|"
                  r"\s*(\d{1,2})", raw)
    assert m, "unreadable air date %r" % raw[:60]
    return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))


def num(raw):
    """An episode number, or None where the source prints a dash."""
    m = re.search(r"\d+", raw or "")
    return int(m.group(0)) if m else None


def span(first, last):
    """'25 March – 29 April 2021', or both years where they differ."""
    fmt = lambda d, y: "%d %s%s" % (d.day, MONTHS[d.month - 1],
                                    " %d" % d.year if y else "")
    if first == last:
        return fmt(first, True)
    return "%s – %s" % (fmt(first, first.year != last.year), fmt(last, True))


def read_season(page):
    """(number, in-season number, title, air date) per row of one season's
    enumerated episode table. The table is the page's <onlyinclude> region —
    exactly the part the parent article transcludes."""
    text = wiki.wikitext(page, cache_dir=CACHE)
    assert text, "could not read %r" % page
    assert text.count("<onlyinclude>") == 1 and text.count("</onlyinclude>") == 1, \
        "%s no longer has exactly one transcluded episode table" % page
    table = text[text.index("<onlyinclude>"):text.index("</onlyinclude>")]
    assert "{{Episode table" in table, "%s: no episode table found" % page

    rows, summaries = [], []
    for block in templates(table, "Episode list"):
        f, summary = fields(block)
        summaries.append(summary)
        t = title_of(f.get("Title", ""))
        assert t, "%s: an episode row has no title" % page
        assert "<!--" not in t and "-->" not in t, \
            "%s: an HTML comment survived into %r" % (page, t[:40])
        assert len(t) <= 80, \
            "%s: %r is too long to be a title — a summary may have leaked" \
            % (page, t[:60])
        rows.append((num(f.get("EpisodeNumber", "")),
                     num(f.get("EpisodeNumber2", "")),
                     t, air_date(f.get("OriginalAirDate", ""))))
    return rows, summaries


def main():
    sections, dropped, overall = [], [], 0
    for n, page, title, count in SEASONS:
        rows, summaries = read_season(page)
        dropped += summaries
        assert len(rows) == count, \
            "%s now enumerates %d episodes, not %d — the source has re-cut " \
            "the season and this generator needs revisiting" \
            % (title, len(rows), count)

        nums = [a for a, _, _, _ in rows]
        assert nums == list(range(overall + 1, overall + count + 1)), \
            "%s numbers %r are not the contiguous run %d–%d" \
            % (title, nums, overall + 1, overall + count)
        dates = [d for _, _, _, d in rows]
        assert dates == sorted(dates), "%s is not in broadcast order" % title
        assert dates[-1] <= AS_OF, \
            "%s carries an episode dated after the frozen cut-off %s — list " \
            "only what has aired, then move AS_OF" % (title, AS_OF)

        sections.append({
            "id": "s%d" % n,
            "title": title,
            "sub": "episodes %d–%d · %s" % (nums[0], nums[-1],
                                            span(dates[0], dates[-1])),
            "links": [{"label": "The season's episode table",
                       "url": "https://en.wikipedia.org/wiki/"
                              + page.replace(" ", "_")}],
            "open": n == 1,
            # No note on any row and no intro on any section: see the module
            # docstring and the first list note.
            "items": [{"id": "inv-%d" % a, "t": t, "n": str(a)}
                      for a, _, t, _ in rows],
        })
        overall += count

    assert overall == TOTAL, "built %d episodes, expected %d" % (overall, TOTAL)

    p = {
        "slug": SLUG,
        "title": "Invincible",
        "subtitle": "the animated series",
        "kind": "tv",
        # 70–79 is "anyone into this has heard of it, with real spill outside
        # the medium", and this sits at the floor of it: four seasons on Prime
        # Video, a comics adaptation whose lines travel well past its own
        # audience, but a five-year track record rather than a generational
        # one. Level with The Sandman and Metroid at 70 — POPULARITY.md says a
        # tie is legal and expected — under Lost and JoJo at 71 and The
        # X-Files at 73, over Buffy & Angel at 68 and DC Animation at 62.
        "popularity": 70,
        # open-ended: seasons 5 and 6 are ordered and unaired, so the run is
        # still producing. Only what has aired is listed.
        "year": "2021–",
        "blurb": "All %d episodes across four seasons, in broadcast order. "
                 "Titles only — the summaries are withheld on purpose." % TOTAL,
        "unit": {"one": "episode", "many": "episodes"},
        "verb": {"base": "watch", "past": "watched", "ing": "watching"},
        "itemOrder": "number-first",
        # The suit: a saturated royal blue against the show's own title
        # yellow, which is #FFF209 — the colour Wikipedia's series overview
        # uses for season 1, not a colour invented here. Blue-and-yellow is a
        # crowded corner of this catalogue and the obvious navies are gone:
        # a deep navy lands 8.4 (CIELAB) from Ultimate Marvel and 8.5 from
        # The Wire. This pair sits 17.8 from its nearest light-mode
        # neighbour, Naruto #155EEF, and 19.8 from its nearest dark-mode
        # neighbour, Cyberpunk: Edgerunners #D4E338.
        "accent": "#1238B4",
        "accentDark": "#FFF209",
        "tiers": False,
        "notes": [
            ["No episode summaries, on purpose.",
             "Every row here is a number and a title, and nothing else. That "
             "is a decision rather than a gap: this show is built on its "
             "turns, and a one-sentence summary hands them over. The source "
             "carries a summary for every episode; this list reads them and "
             "drops them before the file is written, and checks afterwards "
             "that none of that text reached the page. Titles ship exactly "
             "as the source has them — a title is what an episode is called, "
             "not what it does."],
            ["The 2023 special is in, at 9.",
             "Wikipedia's season 2 table opens with \"Invincible: Atom Eve\", "
             "released in July 2023 under the table's own Special heading and "
             "numbered ninth in the series' overall run. Rows here carry "
             "those overall numbers, so it is listed where the source puts "
             "it — 8 + 9 + 8 + 8 = 33."],
            ["Broadcast order, and only what has aired.",
             "Four seasons, from March 2021 to April 2026. A fifth and sixth "
             "season have been ordered and neither has aired, so neither is "
             "here; the build refuses any episode dated past its own frozen "
             "cut-off rather than guessing at a schedule."],
            ["Unweighted.",
             "The episode tables declare no runtime column, so there is no "
             "per-episode figure anyone could check. Every row is one episode "
             "of the same nominal length, so the strip counts episodes and "
             "nothing carries a weight."],
            ["The comic is not in here.",
             "Robert Kirkman, Cory Walker and Ryan Ottley's Image series ran "
             "144 issues from 2003 to 2018. It is a different work in a "
             "different medium and the show diverges from it; if it is ever "
             "worth reading through together it wants its own list, not a "
             "wing of this one."],
            "Episode numbers, titles and air dates machine-read from the "
            "four Wikipedia season articles; each season's count is checked "
            "against its own episode table, never against the series "
            "overview box.",
        ],
        "sections": sections,
    }

    # The refusal, proved rather than asserted by hand: nothing that was
    # dropped may appear in what was written. 40 characters is long enough
    # that a shared phrase between a title and a summary cannot trip it.
    out = prop.write(p)
    written = out.read_text(encoding="utf-8")
    leaks = 0
    for s in dropped:
        flat = re.sub(r"\s+", " ", re.sub(r"<!--.*?-->", "", s, flags=re.S)).strip()
        for i in range(0, max(0, len(flat) - 40), 7):
            if flat[i:i + 40] in written:
                leaks += 1
    assert leaks == 0, "%d summary fragment(s) reached the output" % leaks

    items = [x for s in sections for x in s["items"]]
    assert len(items) == TOTAL, len(items)
    assert not any("note" in x for x in items), "a row carries a note"
    assert not any("intro" in s for s in sections), "a section carries an intro"

    print("wrote %s — %d episodes, %d summaries read and dropped"
          % (out.name, len(items), len(dropped)))
    print("   no row carries a note; no section carries an intro")
    for s in sections:
        print("   %-10s %2d  %s" % (s["title"], len(s["items"]), s["sub"]))


if __name__ == "__main__":
    main()
