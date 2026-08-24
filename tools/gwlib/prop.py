"""Property ids, note assembly, validation, and the emitter.

The asserts here are the ones every shipped generator grew independently;
validate() also carries the house rules the sweep linter enforces after the
fact, so a generator fails at build time instead of at QA time.
"""
import json
import pathlib
import re
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent


def slug(t):
    """ASCII-fold a title into an id fragment (NFKD, lowercase, dashes)."""
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    keep = "".join(c.lower() if c.isalnum() else "-" for c in t)
    while "--" in keep:
        keep = keep.replace("--", "-")
    return keep.strip("-")


def normt(t):
    """Normalize a title for matching (fold, lowercase, drop articles)."""
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    t = re.sub(r"[^a-z0-9]+", " ", t).strip()
    return re.sub(r"^(the|a|an) ", "", t)


def join_bits(*bits):
    """Assemble a row note from optional pieces: stripped, empties dropped —
    a trailing-space country field once double-spaced 1,418 notes."""
    out = [str(b).strip() for b in bits if b and str(b).strip()]
    return " · ".join(out)


WIKI_JUNK = re.compile(r"\[\[|\]\]|\{\{|\}\}|<ref|</ref|''|&nbsp;|<br|\|\||"
                       r"File:|thumb\||rowspan=|colspan=|scope=|align=|style=")
DANGEROUS_ID = re.compile(r"[\s\"'<>&\\]")


def validate(prop):
    """The build.py rules plus the house rules, raised as AssertionError."""
    assert prop.get("slug"), "no slug"
    u = prop.get("unit") or {}
    assert u.get("one") and u.get("many"), "unit incomplete"
    assert prop.get("accent") and prop.get("accentDark"), \
        "accent pair required (ultimate-marvel shipped grey without one)"
    # Catalogue position. Caught here so a generator author finds out while
    # writing the generator, not when the build refuses it. No default: see
    # POPULARITY.md for the bands and the signals behind them.
    assert "order" not in prop, \
        "`order` was replaced by `popularity` — see POPULARITY.md"
    pop = prop.get("popularity")
    assert isinstance(pop, int) and not isinstance(pop, bool) and 0 <= pop <= 100, \
        "popularity must be a whole number from 0 to 100 (POPULARITY.md), got %r" % pop
    ids, comicish = [], u.get("one") in ("issue", "chapter")
    for s in prop.get("sections", []):
        assert s.get("items"), "empty section %r" % s.get("id")
        assert re.match(r"^[A-Za-z][A-Za-z0-9_-]*$", s.get("id", "")), \
            "bad section id %r" % s.get("id")
        for field in ("title", "sub", "intro"):
            v = s.get(field) or ""
            assert not WIKI_JUNK.search(v), \
                "wikitext junk in section %s.%s: %r" % (s.get("id"), field, v[:60])
        for x in s["items"]:
            ids.append(x.get("id"))
            assert x.get("id") and not DANGEROUS_ID.search(x["id"]), \
                "dangerous item id %r" % x.get("id")
            assert x.get("t"), "item with no title: %r" % x.get("id")
            if comicish:
                assert not x.get("url"), \
                    "comic row %s carries a url — links live on headers" % x["id"]
            for field in ("t", "n", "note"):
                v = x.get(field)
                if isinstance(v, str):
                    assert not WIKI_JUNK.search(v), \
                        "wikitext junk in %s.%s: %r" % (x["id"], field, v[:70])
                    assert "  " not in v and not re.search(r"·\s*$|^\s*·", v), \
                        "note hygiene in %s.%s: %r" % (x["id"], field, v[:60])
    assert len(ids) == len(set(ids)), \
        "duplicate ids: %s" % [i for i in ids if ids.count(i) > 1][:4]
    flt = prop.get("filter")
    if flt:
        vals = set(flt.get("values") or [])
        tags = {t for s in prop["sections"] for x in s["items"]
                for t in x.get("tags") or []}
        assert vals == tags, "filter/tag mismatch: %s" % sorted(vals ^ tags)
    return ids


def write(prop, legacy_ids=()):
    """Validate and write properties/<slug>.json; legacy_ids must all still
    exist (renaming an id silently destroys everyone's ticks)."""
    ids = set(validate(prop))
    for lid in legacy_ids:
        assert lid in ids, "legacy id lost: %s" % lid
    out = ROOT / "properties" / ("%s.json" % prop["slug"])
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(prop, indent=2, ensure_ascii=False) + "\n")
    return out
