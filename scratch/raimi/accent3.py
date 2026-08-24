#!/usr/bin/env python3
"""Shortlist accents that clear a distance threshold and still have colour.

    PYTHONIOENCODING=utf-8 python scratch/raimi/accent3.py

Pure max-min (accent.py) drives toward muted mid-chroma greys, because that is
where nobody has shipped — colours nobody wants are always the furthest away.
This instead takes every in-band candidate clearing a floor of CIE76 distance
to the whole shipped set AND carrying real chroma, then ranks by chroma so the
choice is made among accents that look like accents.
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from accent import srgb_to_lab, de, chroma, hexof, hue, band, ROOT  # noqa: E402

LIGHT_FLOOR, LIGHT_CHROMA = 17.0, 30.0
DARK_FLOOR, DARK_CHROMA = 16.0, 45.0


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
                   for s in (0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85)
                   for l in (0.16, 0.20, 0.24, 0.28, 0.32, 0.36, 0.40, 0.44,
                             0.52, 0.58, 0.62, 0.66, 0.70, 0.74)})

    def shortlist(against, box, floor, minc):
        lo_l, hi_l, lo_c, hi_c = box
        out = []
        for hx in grid:
            lab = srgb_to_lab(hx)
            if not (lo_l <= lab[0] <= hi_l and minc <= chroma(lab) <= hi_c):
                continue
            d = min(de(lab, o) for o in against)
            if d >= floor:
                out.append((chroma(lab), d, hx, lab))
        out.sort(reverse=True)
        return out

    for label, against, box, floor, minc in (
            ("LIGHT", Ls, lband, LIGHT_FLOOR, LIGHT_CHROMA),
            ("DARK", Ds, dband, DARK_FLOOR, DARK_CHROMA)):
        sl = shortlist(against, box, floor, minc)
        print("\n%s accents clearing minDE %.0f with chroma >= %.0f: %d candidates"
              % (label, floor, minc, len(sl)))
        seen = {}
        for c, d, hx, lab in sl:
            k = int(hue(hx)) // 10
            if k in seen:
                continue
            seen[k] = 1
            print("   %s  C=%5.1f  minDE %5.1f  L*=%5.1f  h=%3.0f"
                  % (hx, c, d, lab[0], hue(hx)))

    for hx in sys.argv[1:]:
        lab = srgb_to_lab(hx)
        for label, names in (("light", light), ("dark", dark)):
            near = sorted((de(lab, srgb_to_lab(c)), c, slug_of[c]) for c in names)[:5]
            print("\n%s vs %s accents:  L*=%.1f C=%.1f h=%.0f"
                  % (hx, label, lab[0], chroma(lab), hue(hx)))
            for d, c, slug in near:
                print("   %5.1f  %s  %s" % (d, c, slug))


if __name__ == "__main__":
    main()
