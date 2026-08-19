#!/usr/bin/env python3
"""Build index.html from template.html + reading_order.py.

    python3 src/build.py

Writes index.html at the repo root. Safe to run repeatedly.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from reading_order import build_sections  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "src" / "template.html"
OUTPUT = ROOT / "index.html"


def main():
    sections = build_sections()

    tiers = {1: 0, 2: 0, 3: 0}
    for s in sections:
        tiers[s["tier"]] += len(s["items"])
    total = sum(tiers.values())

    html = TEMPLATE.read_text(encoding="utf-8")
    if "__DATA__" not in html:
        raise SystemExit("template.html is missing the __DATA__ placeholder")

    # indent=2 keeps index.html diffable in git — without it the whole reading
    # order lands on one line and every rebuild looks like a total rewrite.
    data = json.dumps(sections, indent=2, ensure_ascii=False)

    html = html.replace("__DATA__", data)
    html = html.replace("__TOTAL__", str(total))
    for t in (1, 2, 3):
        html = html.replace("__T%d__" % t, str(tiers[t]))

    for leftover in ("__DATA__", "__TOTAL__", "__T1__", "__T2__", "__T3__"):
        if leftover in html:
            raise SystemExit("placeholder %s was not replaced" % leftover)

    # newline="\n" so a rebuild on Windows doesn't rewrite every line as CRLF
    # and turn the diff into a whole-file change.
    with OUTPUT.open("w", encoding="utf-8", newline="\n") as f:
        f.write(html)

    print("wrote %s" % OUTPUT.relative_to(ROOT))
    print("  %d sections, %d issues" % (len(sections), total))
    print("  tier 1: %d   tier 2: %d   tier 3: %d" % (tiers[1], tiers[2], tiers[3]))
    linked = sum(1 for s in sections if s.get("series"))
    issue_links = sum(1 for s in sections for x in s["items"] if x["url"])
    print("  %d/%d sections have series links, %d direct issue links"
          % (linked, len(sections), issue_links))


if __name__ == "__main__":
    main()
