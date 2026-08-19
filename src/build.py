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
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "src" / "template.html"
PROPS = ROOT / "properties"
OUTPUT = ROOT / "index.html"
MANIFEST = PROPS / "index.json"

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

    for field in ("title", "unit", "sections"):
        if not prop.get(field):
            fail("%s has no %s" % (path.name, field))
    if not prop["unit"].get("one") or not prop["unit"].get("many"):
        fail("%s: unit needs both 'one' and 'many'" % path.name)

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

    files = sorted(p for p in PROPS.glob("*.json") if p.name != "index.json")
    if not files:
        fail("properties/ has no property files")

    props = [load_property(p) for p in files]

    slugs = [p["slug"] for p in props]
    if len(slugs) != len(set(slugs)):
        fail("two properties share a slug")

    # Menu and splash order. There is no "default property" — a first-time
    # visitor gets the splash picker — so this is presentation only.
    props.sort(key=lambda p: (p.get("order", 100), p["title"]))

    manifest = [
        {
            "slug": p["slug"],
            "title": p["title"],
            "subtitle": p.get("subtitle", ""),
            "kind": p.get("kind", ""),
            "year": p.get("year", ""),
            "blurb": p.get("blurb", ""),
            "accent": p.get("accent", ""),
            "unit": p["unit"],
            "total": p["_total"],
            "scheduled": bool(p.get("schedule")),
        }
        for p in props
    ]

    with MANIFEST.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

    html = TEMPLATE.read_text(encoding="utf-8")
    if "__MANIFEST__" not in html:
        fail("template.html is missing the __MANIFEST__ placeholder")
    # the manifest is small and needed before first paint, so it is inlined;
    # the property bodies are not
    html = html.replace("__MANIFEST__", json.dumps(manifest, indent=2, ensure_ascii=False))
    if "__MANIFEST__" in html:
        fail("__MANIFEST__ was not replaced")

    with OUTPUT.open("w", encoding="utf-8", newline="\n") as f:
        f.write(html)

    print("wrote index.html and properties/index.json")
    for p in props:
        print("  %-22s %4d %-9s %s"
              % (p["slug"], p["_total"], p["unit"]["many"],
                 "scheduled" if p.get("schedule") else ""))


if __name__ == "__main__":
    main()
