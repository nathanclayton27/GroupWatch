#!/usr/bin/env python3
"""Per-hue-family view of what accent room is left.

    PYTHONIOENCODING=utf-8 python scratch/raimi/accent2.py

accent.py answers "what is furthest from everything shipped"; this answers
"how much room is left in each hue family", which is the question you actually
need when the winner also has to suit the list. Same CIELAB maths, same house
bands read off properties/index.json.
"""
import sys
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from accent import (srgb_to_lab, de, chroma, hexof, hue, band, ROOT)  # noqa: E402
import json  # noqa: E402

FAMILIES = [("red", 350, 15), ("orange", 15, 45), ("gold", 45, 70),
            ("lime", 70, 100), ("green", 100, 150), ("teal", 150, 195),
            ("blue", 195, 250), ("indigo", 250, 280), ("violet", 280, 310),
            ("magenta", 310, 350)]


def infamily(h, lo, hi):
    return (lo <= h < hi) if lo < hi else (h >= lo or h < hi)


def main():
    manifest = json.loads((ROOT / "properties" / "index.json")
                          .read_text(encoding="utf-8"))
    light = [m["accent"] for m in manifest if m.get("accent")]
    dark = [m["accentDark"] for m in manifest if m.get("accentDark")]
    slug_of = {}
    for m in manifest:
        slug_of.setdefault(m["accent"], m["slug"])
        slug_of.setdefault(m["accentDark"], m["slug"])
    Ls = [srgb_to_lab(c) for c in light]
    Ds = [srgb_to_lab(c) for c in dark]
    lband, dband = band(light), band(dark)

    grid = sorted({hexof(h, s, l) for h in range(0, 360, 1)
                   for s in (0.2, 0.3, 0.4, 0.5, 0.6, 0.7)
                   for l in (0.16, 0.20, 0.24, 0.28, 0.32, 0.36, 0.40,
                             0.52, 0.58, 0.64, 0.70, 0.76)})

    def score(against, box):
        lo_l, hi_l, lo_c, hi_c = box
        out = []
        for hx in grid:
            lab = srgb_to_lab(hx)
            if lo_l <= lab[0] <= hi_l and lo_c <= chroma(lab) <= hi_c:
                out.append((min(de(lab, o) for o in against), hx))
        return out

    sl, sd = score(Ls, lband), score(Ds, dband)
    print("%-9s  %-26s  %s" % ("family", "best light accent", "best dark accent"))
    for name, lo, hi in FAMILIES:
        bl = max((x for x in sl if infamily(hue(x[1]), lo, hi)), default=None)
        bd = max((x for x in sd if infamily(hue(x[1]), lo, hi)), default=None)
        print("%-9s  %s minDE %5.1f          %s minDE %5.1f"
              % (name, bl[1], bl[0], bd[1], bd[0]))

    # how crowded each family already is
    print("\nshipped accents per family (light values):")
    for name, lo, hi in FAMILIES:
        n = [slug_of[c] for c in light if infamily(hue(c), lo, hi)]
        print("  %-9s %2d  %s" % (name, len(n), ", ".join(sorted(n)[:6])))


if __name__ == "__main__":
    main()
