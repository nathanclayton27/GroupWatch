#!/usr/bin/env python3
"""Build index.html and the property manifest.

    python3 src/build.py

Property data is no longer inlined. The page boots, reads ?p=<slug>, and fetches
that property's JSON at runtime, so adding a show is dropping a file into
properties/ and rebuilding. This script's job is to validate those files and
write the manifest the property switcher reads.

Because the data is fetched, the page must be served over http — file:// blocks
fetch. Use `python3 -m http.server 8000`.
"""
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "src" / "template.html"
PROPS = ROOT / "properties"
OUTPUT = ROOT / "index.html"
MANIFEST = PROPS / "index.json"
BUILDFILE = ROOT / "build.json"

ID_OK = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")


def fail(msg):
    raise SystemExit("build failed: %s" % msg)


def load_property(path):
    try:
        prop = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as e:
        fail("%s is not valid JSON — %s" % (path.name, e))

    slug = prop.get("slug")
    if not slug:
        fail("%s has no slug" % path.name)
    if slug != path.stem:
        fail("%s declares slug %r — slug and filename must match" % (path.name, slug))
    if not ID_OK.match(slug):
        fail("%s: slug %r must be a valid html id" % (path.name, slug))

    for field in ("title", "unit"):
        if not prop.get(field):
            fail("%s has no %s" % (path.name, field))
    if not prop["unit"].get("one") or not prop["unit"].get("many"):
        fail("%s: unit needs both 'one' and 'many'" % path.name)

    # A generated property has no sections on disk: the page builds them from
    # the calendar when it loads, so the list grows by itself as days pass and
    # a static file would be stale the morning after it shipped. Everything
    # about it that can be checked ahead of time is checked here instead.
    # An encrypted property carries nothing to validate: its sections, its
    # generate block and its real title are all inside the ciphertext, and the
    # build has no key. Check the envelope and stop there.
    sec = prop.get("secret") or {}
    if sec.get("blob"):
        for field in ("salt", "iv", "iter"):
            if not sec.get(field):
                fail("%s: an encrypted property needs secret.%s" % (path.name, field))
        if prop.get("sections") or prop.get("generate"):
            fail("%s: an encrypted property must not also ship its contents"
                 % path.name)
        prop["_total"] = 0
        return prop

    gen = prop.get("generate")
    if gen:
        if prop.get("sections"):
            fail("%s: a generated property must not also carry sections" % path.name)
        if gen.get("kind") != "daily":
            fail("%s: generate.kind %r is not one this build knows"
                 % (path.name, gen.get("kind")))
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", gen.get("start", "")):
            fail("%s: generate.start must be a YYYY-MM-DD date" % path.name)
        if not isinstance(gen.get("slots"), int) or not 1 <= gen["slots"] <= 24:
            fail("%s: generate.slots must be a whole number from 1 to 24" % path.name)
        if not gen.get("idPrefix"):
            fail("%s: generate needs an idPrefix, since item ids are permanent"
                 % path.name)
        prop["_total"] = 0        # only today knows, and today is the reader's
        return prop

    if not prop.get("sections"):
        fail("%s has no sections" % path.name)

    seen = set()
    total = 0
    for s in prop["sections"]:
        if not s.get("id"):
            fail("%s: a section has no id" % path.name)
        if not ID_OK.match(s["id"]):
            fail("%s: section id %r must be a valid html id" % (path.name, s["id"]))
        if not s.get("items"):
            fail("%s: section %r has no items" % (path.name, s["id"]))
        for x in s["items"]:
            if not x.get("id"):
                fail("%s: an item in %r has no id" % (path.name, s["id"]))
            # duplicate ids make two checkboxes move together, silently
            if x["id"] in seen:
                fail("%s: duplicate item id %r" % (path.name, x["id"]))
            seen.add(x["id"])
            total += 1

    prop["_total"] = total
    return prop


def main():
    if not PROPS.is_dir():
        fail("no properties/ directory")

    files = sorted(p for p in PROPS.glob("*.json")
                   if p.name not in ("index.json", "search.json"))
    if not files:
        fail("properties/ has no property files")

    props = [load_property(p) for p in files]

    slugs = [p["slug"] for p in props]
    if len(slugs) != len(set(slugs)):
        fail("two properties share a slug")

    # Menu and splash order. There is no "default property" — a first-time
    # visitor gets the splash picker — so this is presentation only.
    props.sort(key=lambda p: (p.get("order", 100), p["title"]))

    # medium tags for the search chips and the card wall — derived from the
    # kind string plus the unit, so mixed-media pages (MCU: films & shows)
    # surface under every medium they contain
    def media_of(p):
        k = (p.get("kind") or "").lower()
        u = (p.get("unit") or {}).get("one", "")
        m = set()
        if "film" in k or "movie" in k:
            m.add("movies")
        if re.search(r"\btv\b|show|series|episode", k):
            m.add("tv")
        if "anime" in k:
            m.add("anime")
        if "manga" in k or u == "chapter":
            m.add("manga")
        if "comic" in k or u == "issue":
            m.add("comics")
        if "book" in k or u in ("book", "novel"):
            m.add("books")
        if "game" in k:
            m.add("games")
        return sorted(m or {"other"})

    MEDIA_FIX = {"nasuverse": ["anime", "games", "manga", "movies"],
                 "bottle-episodes": ["tv"]}

    manifest = [
        {
            "slug": p["slug"],
            "media": MEDIA_FIX.get(p["slug"], media_of(p)),
            "title": p["title"],
            "subtitle": p.get("subtitle", ""),
            "kind": p.get("kind", ""),
            "year": p.get("year", ""),
            "blurb": p.get("blurb", ""),
            "accent": p.get("accent", ""),
            "accentDark": p.get("accentDark", ""),
            "unit": p["unit"],
            "total": p["_total"],
            # home ranks schedule-active clubs first; the flag is all it needs
            **({"scheduled": True} if p.get("schedule") else {}),
            # grab-bag lists welcome a random pick; everything else is
            # ordered and only ever offers its next unticked item
            **({"random": True} if p.get("random") else {}),
            # the page needs these before first paint: one to know not to list
            # a locked property, the other to size a generated one
            # the switcher names a locked list by its cover title, not its own
            **({"secret": {"title": p["secret"].get("title", "Secret")}}
               if p.get("secret") else {}),
            **({"generate": p["generate"]} if p.get("generate") else {}),
        }
        for p in props
    ]

    with MANIFEST.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

    # ---- the row index: one file powering global search and cross-list ----
    # tick sync. rows: [slug, id, title, n] for every visible property.
    # sync groups: film-kind rows (n = a plain year) that share a normalized
    # title+year across DIFFERENT lists — Dr. Strangelove on Kubrick,
    # Criterion and Best Picture is one group. Exact matches only.
    import unicodedata as _ud

    def _normt(t):
        t = _ud.normalize("NFKD", t)
        t = "".join(c for c in t if not _ud.combining(c)).lower()
        t = re.sub(r"[^a-z0-9]+", " ", t).strip()
        return re.sub(r"^(the|a|an) ", "", t)

    rows, groups = [], {}
    for p in props:
        if p.get("secret"):
            continue
        filmish = "film" in (p.get("kind") or "")
        for s in p.get("sections", []):
            for x in s.get("items", []):
                n = str(x.get("n", ""))
                rows.append([p["slug"], x["id"], x["t"], n])
                if filmish and re.fullmatch(r"(18|19|20)\d{2}", n):
                    groups.setdefault(_normt(x["t"]) + "|" + n, []).append(
                        [p["slug"], x["id"]])
    sync = {k: v for k, v in groups.items()
            if len({s for s, _ in v}) > 1}
    with (PROPS / "search.json").open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({"rows": rows, "sync": sync},
                           separators=(",", ":"), ensure_ascii=False) + "\n")
    print("  search index: %d rows, %d sync groups spanning %d lists"
          % (len(rows), len(sync),
             len({s for v in sync.values() for s, _ in v})))

    html = TEMPLATE.read_text(encoding="utf-8")
    for ph in ("__MANIFEST__", "__BUILD__"):
        if ph not in html:
            fail("template.html is missing the %s placeholder" % ph)

    # the manifest is small and needed before first paint, so it is inlined;
    # the property bodies are not
    html = html.replace("__MANIFEST__", json.dumps(manifest, indent=2, ensure_ascii=False))

    # A content hash of everything that ends up in the page. GitHub Pages serves
    # index.html with a cache lifetime, so a browser can go on running an old
    # copy after a deploy. The page checks this against build.json and reloads
    # itself once if they differ, which is what saves anyone hard-refreshing.
    stamp = hashlib.sha1(html.encode("utf-8"))
    for f in files:
        stamp.update(f.read_bytes())
    build = stamp.hexdigest()[:12]

    html = html.replace("__BUILD__", build)
    for ph in ("__MANIFEST__", "__BUILD__"):
        if ph in html:
            fail("%s was not replaced" % ph)

    with OUTPUT.open("w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    with BUILDFILE.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({"build": build}) + "\n")

    print("wrote index.html, properties/index.json and build.json")
    print("  build %s" % build)
    for p in props:
        print("  %-22s %4d %-9s %s"
              % (p["slug"], p["_total"], p["unit"]["many"],
                 "scheduled" if p.get("schedule") else ""))


if __name__ == "__main__":
    main()
