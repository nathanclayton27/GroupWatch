"""Wikipedia fetching and wikitext parsing, the shipped-and-burned edition.

Every regex here earned its shape from a real incident:
- rowspan carry: Robin Williams' year column silently went stale (two bugs)
- leading pipe: episode blocks' first field (usually Title) was invisible
- {{#invoke:Episode list|sublist}}: American Dad's season pages use it
- footnote templates removed whole: Troll 2 shipped "Fragassoefn|name=…"
- multi-line infobox fields: Toxic Avenger's {{Plainlist}} of directors
- comments stripped before field parsing: Free Fire's runtime line
"""
import json
import pathlib
import re
import time
import urllib.error
import urllib.parse
import urllib.request

UA = "GroupWatch/1.0 (reading-list builder)"
API = "https://en.wikipedia.org/w/api.php"


def get_json(url, tries=6):
    """GET a JSON API url with 429 backoff and network retries."""
    for n in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code != 429 or n == tries - 1:
                raise
            time.sleep(12 * (n + 1))
        except (urllib.error.URLError, TimeoutError):
            if n == tries - 1:
                raise
            time.sleep(5)


def wikitext(page, cache_dir=None, sleep=2.5):
    """Fetch a page's wikitext (redirects followed), optionally disk-cached."""
    if cache_dir:
        f = pathlib.Path(cache_dir) / (re.sub(r"[^A-Za-z0-9]+", "-", page) + ".wiki")
        if f.exists():
            return f.read_text(encoding="utf-8")
    q = urllib.parse.urlencode({"action": "parse", "page": page,
                                "prop": "wikitext", "format": "json",
                                "formatversion": "2", "redirects": "1"})
    d = get_json(API + "?" + q)
    time.sleep(sleep)
    if "error" in d:
        return None
    t = d["parse"]["wikitext"]
    if cache_dir:
        pathlib.Path(cache_dir).mkdir(parents=True, exist_ok=True)
        f.write_text(t, encoding="utf-8")
    return t


def search(query, limit=6):
    """Article titles matching a query — the way to find a page's real name."""
    q = urllib.parse.urlencode({"action": "query", "list": "search",
                                "srsearch": query, "srlimit": str(limit),
                                "format": "json", "formatversion": "2"})
    return [x["title"] for x in get_json(API + "?" + q)["query"]["search"]]


def clean(t):
    """Wikitext -> display text. Footnotes vanish whole; wikilinks keep their
    label; inline templates keep their last argument; italics drop."""
    t = re.sub(r"<ref[^>]*/>", "", t or "")
    t = re.sub(r"<ref.*?</ref>", "", t, flags=re.S)
    for _ in range(3):
        t = re.sub(r"\{\{\s*(?:efn|refn|sfn|notetag)[^{}]*\}\}", "", t, flags=re.I)
    t = re.sub(r"<br\s*/?>", ", ", t)
    t = re.sub(r"\{\{(?:ubl|unbulleted list|plainlist)\s*\|", "", t, flags=re.I)
    t = re.sub(r"\s*\n\s*\*\s*", ", ", t)
    t = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", t)
    t = re.sub(r"\[\[([^\]]+)\]\]", r"\1", t)
    t = re.sub(r"\{\{[^{}|]*\|(?:[^{}|]*\|)*([^{}|]*)\}\}", r"\1", t)
    t = t.replace("{{", "").replace("}}", "").replace("''", "")
    return re.sub(r"\s+", " ", t).strip(" ,|")


# a table cell is `| content` or `| attrs | content`; the attrs test excludes
# link/template pipes so `[[A|B]]` and `{{sort|x|y}}` survive
_CELL = re.compile(r"^\|\s*(?:([^|\[{]*=[^|\[{]*)\|)?\s*(.*)$", re.S)


def table_rows(seg, ncols, header_probe="!scope=\"row\""):
    """Rows of a wikitable whose title cell is a `!scope="row"` header.

    Returns (title_line, cols) per row, with rowspan cells carried down to
    the rows they cover — the parsing that positional cell-picking got wrong
    three separate times. `ncols` counts the data columns to read, in table
    order, excluding the title header cell.
    """
    out, pending = [], {}
    for row in seg.split("\n|-"):
        lines = [l.strip() for l in row.strip().split("\n") if l.strip()]
        title_line = next((l for l in lines if l.startswith(header_probe)), None)
        if not title_line:
            continue
        raw = iter(l for l in lines
                   if l.startswith("|") and "text-align" not in l)
        cols = []
        for c in range(ncols):
            if c in pending:
                cols.append(pending[c][1])
                pending[c][0] -= 1
                if pending[c][0] == 0:
                    del pending[c]
                continue
            m = _CELL.match(next(raw, "|"))
            attrs, content = m.group(1) or "", m.group(2)
            cols.append(content)
            span = re.search(r"rowspan=\"?(\d+)", attrs)
            if span and int(span.group(1)) > 1:
                pending[c] = [int(span.group(1)) - 1, content]
        out.append((title_line, cols))
    return out


def episodes(text):
    """Episode-list entries: (num_overall, num_in_season, title, year, block).

    Handles {{Episode list}}, {{Episode list/sublist|Page}}, and
    {{#invoke:Episode list|sublist|Page}}; keeps the leading pipe inside the
    block so the first field is findable; empty titles stay empty (an empty
    title once containment-matched everything)."""
    out = []
    for m in re.finditer(r"\{\{(?:#invoke:)?Episode list"
                         r"(?:\s*\|\s*sublist\s*\|[^|\n]*|/sublist[^|}\n]*)?"
                         r"\s*(\|.*?)\n\s*\}\}", text, flags=re.S | re.I):
        block = "\n" + m.group(1)

        def field(name):
            fm = re.search(r"\|\s*%s\s*=\s*(.*?)(?=\n\s*\||\Z)" % name,
                           block, re.S)
            return fm.group(1).strip() if fm else ""

        title = clean(field("Title")).strip('"')
        n1, n2 = field("EpisodeNumber"), field("EpisodeNumber2")
        ad = field("OriginalAirDate")
        ym = re.search(r"(19|20)\d{2}", ad)
        num = lambda v: (int(re.search(r"\d+", v).group(0))
                         if re.search(r"\d+", v) else None)
        out.append((num(n1), num(n2), title,
                    int(ym.group(0)) if ym else None, block))
    return out


def infobox(text, kind=r"film|television"):
    """A field reader over the page's first infobox, comments pre-stripped,
    multi-line values captured whole (to the next field or the box close)."""
    im = re.search(r"\{\{Infobox (%s)" % kind, text, re.I)
    if not im:
        return None
    box = re.sub(r"<!--.*?-->", "", text[im.start():im.start() + 6000], flags=re.S)

    def field(name):
        m = re.search(r"^\s*\|\s*%s[ \t]*=[ \t]*(.*?)"
                      r"(?=\n\s*\|\s*[a-z_ ]+[ \t]*=|\n\}\})" % name,
                      box, re.M | re.S | re.I)
        return m.group(1).strip() if m else ""

    return field
