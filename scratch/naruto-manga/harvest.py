#!/usr/bin/env python3
"""Harvest Naruto's 72 volumes and 700 chapter titles from Wikipedia.

    python scratch/naruto-manga/harvest.py

Three articles carry the enumerated tables — Part I (volumes 1-27) and the two
Part II halves (28-48, 49-72). Each volume is one {{Graphic novel list}}
template whose ChapterList field is a numbered list; the first entry of each
volume carries an explicit <li value="N">, so the chapter numbering is stated
by the table itself rather than inferred by counting.

Only the English chapter title is taken. The Summary field of every template is
deliberately ignored: a Naruto summary is a spoiler, and the property ships
titles only.

Writes scratch/naruto-manga/naruto-manga.json, which tools/make_naruto_manga.py
reads. Nothing here is typed by hand.
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from gwlib import wiki  # noqa: E402

PAGES = [
    ("List of Naruto chapters (Part I)", 1, 27),
    ("List of Naruto chapters (Part II, volumes 28–48)", 28, 48),
    ("List of Naruto chapters (Part II, volumes 49–72)", 49, 72),
]

OUT = HERE / "naruto-manga.json"


def blocks(text, name):
    """Every {{name ...}} template in `text`, brace-matched.

    A ChapterList is full of nested {{nihongo}} templates and the Summary field
    is full of {{cite}}, so a non-greedy regex to the first }} truncates the
    volume; the depth counter is the only thing that gets the whole block.
    """
    out = []
    for m in re.finditer(r"\{\{\s*%s\s*\n" % re.escape(name), text):
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
        out.append(text[m.start():i])
    return out


def field(block, name):
    """A top-level template field, captured to the next top-level field.

    Fields are matched only at brace depth 1 so that a `| title=` inside a
    nested {{cite web}} cannot end the field it sits in.
    """
    m = re.search(r"\n\|\s*%s\s*=" % re.escape(name), block)
    if not m:
        return ""
    i, depth, start = m.end(), 0, m.end()
    while i < len(block):
        if block.startswith("{{", i):
            depth += 1
            i += 2
        elif block.startswith("}}", i):
            if depth == 0:
                break
            depth -= 1
            i += 2
        elif depth == 0 and block[i] == "\n" and re.match(r"\n\|\s*[A-Za-z]", block[i:]):
            break
        else:
            i += 1
    return block[start:i].strip()


def chapter_titles(raw):
    """(number, English title) for each `#` line of a ChapterList field.

    Titles come from {{nihongo|"English"|kanji|romaji}} / {{nihongo-s|...}};
    the English form is always the first argument. Volume 2's chapter 11 is
    missing its closing quote in the source ("Going Ashore), so quotes are
    stripped rather than required.
    """
    out, n = [], None
    for line in raw.split("\n"):
        line = line.strip()
        if not line.startswith("#"):
            continue
        v = re.search(r'<li\s+value\s*=\s*"?(\d+)', line)
        if v:
            n = int(v.group(1))
        elif n is None:
            raise SystemExit("chapter line before any <li value=>: %r" % line[:60])
        else:
            n += 1
        m = re.search(r"\{\{\s*nihongo(?:-s)?\s*\|(.*)$", line)
        if not m:
            raise SystemExit("no nihongo template on chapter %s: %r" % (n, line[:80]))
        title = m.group(1).split("|")[0]
        title = wiki.clean(title).strip().strip('"').strip()
        title = title.replace("&nbsp;", " ")
        title = re.sub(r"\s+", " ", title)
        if not title:
            raise SystemExit("empty chapter title at %s" % n)
        out.append((n, title))
    return out


def main():
    volumes = []
    for page, lo, hi in PAGES:
        text = wiki.wikitext(page, cache_dir=str(HERE))
        assert text, page
        found = blocks(text, "Graphic novel list")
        assert len(found) == hi - lo + 1, \
            "%s: %d volume blocks, expected %d" % (page, len(found), hi - lo + 1)
        for b in found:
            num = int(field(b, "VolumeNumber"))
            chaps = chapter_titles(field(b, "ChapterList"))
            volumes.append({
                "n": num,
                "title": wiki.clean(field(b, "LicensedTitle")),
                "jp": wiki.clean(field(b, "TranslitTitle")),
                "jp_date": wiki.clean(field(b, "OriginalRelDate")),
                "en_date": wiki.clean(field(b, "LicensedRelDate")),
                "chapters": [{"n": n, "t": t} for n, t in chaps],
                "page": page,
            })

    volumes.sort(key=lambda v: v["n"])
    assert [v["n"] for v in volumes] == list(range(1, 73)), \
        [v["n"] for v in volumes]

    # the tables must tile the chapters 1..700 with no gap and no overlap
    run = [c["n"] for v in volumes for c in v["chapters"]]
    assert run == list(range(1, 701)), \
        "chapter run breaks at %s" % next(
            (i + 1 for i, n in enumerate(run) if n != i + 1), "?")

    for v in volumes:
        assert v["title"], "volume %d has no English title" % v["n"]
        assert v["jp_date"], "volume %d has no Japanese release date" % v["n"]

    data = {
        "source": "Wikipedia: %s" % "; ".join(p for p, _, _ in PAGES),
        "chapters": len(run),
        "volumes": len(volumes),
        "vols": volumes,
    }
    with OUT.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(data, indent=1, ensure_ascii=False, sort_keys=False) + "\n")
    print("wrote %s" % OUT.name)
    print("  %d volumes, %d chapters" % (len(volumes), len(run)))
    print("  shortest volume: %d chapters, longest: %d"
          % (min(len(v["chapters"]) for v in volumes),
             max(len(v["chapters"]) for v in volumes)))


if __name__ == "__main__":
    main()
