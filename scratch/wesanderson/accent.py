#!/usr/bin/env python3
"""Pick the Wes Anderson accent pair, and say what it was measured against.

    PYTHONIOENCODING=utf-8 python scratch/wesanderson/accent.py

His palette is the most recognisable thing about him and that is exactly the
problem: Mendl's pink, the Zissou blue, the Tenenbaum red, the Darjeeling
mustard are all colours a catalogue of 124 lists is likely to have spent
already. So this does two passes.

  1. Name the obvious picks and print, for each, the nearest shipped accent
     in CIE76. That is the check, written down: "the pink is taken" has to be
     a measurement, not a shrug.
  2. Scan the whole in-band grid for the pair whose worst-case distance to
     every shipped accent is largest, then re-scan restricted to each of his
     signature hue families, so the choice is between a colour that is his
     and a colour that is merely free.

Bands are measured off the shipped set (the L* and chroma the light accents
and the dark accents actually occupy) so the winner is a usable accent rather
than a neon sitting in an empty corner. Adapted from scratch/raimi/accent.py.
"""
import colorsys
import json
import math
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]

# The colours anyone would reach for first, with where they come from.
SIGNATURE = [
    ("#F1BFC8", "Mendl's box pink, The Grand Budapest Hotel"),
    ("#E8A0BF", "the deeper Budapest pink"),
    ("#D8455F", "Tenenbaum red / the Adidas tracksuit stripe"),
    ("#E0A32E", "Darjeeling mustard"),
    ("#F2C14E", "Moonrise Kingdom khaki-yellow"),
    ("#3E8FC1", "Zissou blue"),
    ("#7A9E7E", "Isle of Dogs sage"),
    ("#8C4A63", "the Budapest lobby plum"),
]
FAMILIES = [("pink", 320, 355), ("red", 350, 10), ("mustard", 35, 55),
            ("blue", 190, 215), ("green", 90, 150)]


def srgb_to_lab(hex6):
    r, g, b = (int(hex6[i:i + 2], 16) / 255.0 for i in (1, 3, 5))

    def lin(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = lin(r), lin(g), lin(b)
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 1.00000
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883

    def f(t):
        return t ** (1.0 / 3) if t > 216 / 24389 else (841 / 108) * t + 4 / 29

    fx, fy, fz = f(x), f(y), f(z)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def de(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def chroma(lab):
    return math.hypot(lab[1], lab[2])


def hexof(h, s, l):
    r, g, b = colorsys.hls_to_rgb(h / 360.0, l, s)
    return "#%02X%02X%02X" % tuple(int(round(c * 255)) for c in (r, g, b))


def hue(hx):
    r, g, b = (int(hx[i:i + 2], 16) / 255.0 for i in (1, 3, 5))
    return colorsys.rgb_to_hls(r, g, b)[0] * 360


def inband(h, lo, hi):
    return lo <= h <= hi if lo <= hi else (h >= lo or h <= hi)


def band(hexes, lo_pct=0.05, hi_pct=0.95):
    labs = [srgb_to_lab(c) for c in hexes]
    ls = sorted(l for l, _, _ in labs)
    cs = sorted(chroma(x) for x in labs)
    pick = lambda v, p: v[min(len(v) - 1, int(len(v) * p))]
    return (pick(ls, lo_pct), pick(ls, hi_pct),
            pick(cs, lo_pct), pick(cs, hi_pct))


def main():
    manifest = json.loads((ROOT / "properties" / "index.json")
                          .read_text(encoding="utf-8"))
    light = [m["accent"] for m in manifest if m.get("accent")]
    dark = [m["accentDark"] for m in manifest if m.get("accentDark")]
    slug_of = {}
    for m in manifest:
        slug_of.setdefault(m["accent"], m["slug"])
        slug_of.setdefault(m["accentDark"], m["slug"])
    print("measured against %d shipped lists — %d light accents, %d dark"
          % (len(manifest), len(light), len(dark)))
    Ls = [srgb_to_lab(c) for c in light]
    Ds = [srgb_to_lab(c) for c in dark]
    allc = light + dark

    print("\n--- 1. the obvious Wes Anderson picks, and what they collide with")
    for hx, why in SIGNATURE:
        lab = srgb_to_lab(hx)
        near = sorted((de(lab, srgb_to_lab(c)), c, slug_of[c]) for c in allc)[:3]
        print("  %s  h=%3.0f  %-44s" % (hx, hue(hx), why))
        for d, c, s in near:
            print("        %5.1f from %s (%s)" % (d, c, s))

    lband, dband = band(light), band(dark)
    print("\nlight accents occupy L* %.0f-%.0f, chroma %.0f-%.0f" % lband)
    print("dark  accents occupy L* %.0f-%.0f, chroma %.0f-%.0f" % dband)

    grid = [hexof(h, s, l) for h in range(0, 360)
            for s in (0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75)
            for l in (0.14, 0.18, 0.22, 0.26, 0.30, 0.34, 0.38, 0.42,
                      0.50, 0.58, 0.62, 0.66, 0.70, 0.74, 0.78)]
    grid = sorted(set(grid))

    def scored(against, box, hues=None):
        lo_l, hi_l, lo_c, hi_c = box
        out = []
        for hx in grid:
            lab = srgb_to_lab(hx)
            if not (lo_l <= lab[0] <= hi_l and lo_c <= chroma(lab) <= hi_c):
                continue
            if hues and not inband(hue(hx), *hues):
                continue
            out.append((min(de(lab, o) for o in against), hx))
        out.sort(reverse=True)
        return out

    def pairs(sl, sd, gap_max=14, take=600):
        got = []
        for dl, hl in sl[:take]:
            for dd, hd in sd[:take]:
                g = abs(hue(hl) - hue(hd))
                g = min(g, 360 - g)
                if g <= gap_max:
                    got.append((min(dl, dd), dl, dd, hl, hd))
        got.sort(reverse=True)
        return got

    print("\n--- 2. best in-band pair anywhere on the wheel")
    best = pairs(scored(Ls, lband), scored(Ds, dband))
    for worst, dl, dd, hl, hd in best[:6]:
        print("   %s / %s  worst %5.1f  (light %4.1f, dark %4.1f)  hue %3.0f"
              % (hl, hd, worst, dl, dd, hue(hl)))

    print("\n--- 3. best in-band pair inside each of his signature families")
    for name, lo, hi in FAMILIES:
        p = pairs(scored(Ls, lband, (lo, hi)), scored(Ds, dband, (lo, hi)))
        print("  %-8s (h %3d-%3d):" % (name, lo, hi))
        for worst, dl, dd, hl, hd in p[:4]:
            print("     %s / %s  worst %5.1f  (light %4.1f, dark %4.1f)  hue %3.0f"
                  % (hl, hd, worst, dl, dd, hue(hl)))
        if not p:
            print("     nothing in band")

    print("\n--- nearest shipped accents to a chosen pair "
          "(edit CHOSEN below and re-run)")
    for hx, pool, lbl in ((CHOSEN[0], light, "light"), (CHOSEN[1], dark, "dark")):
        lab = srgb_to_lab(hx)
        near = sorted((de(lab, srgb_to_lab(c)), c, slug_of[c]) for c in pool)[:6]
        print("  %s (%s, h=%.0f):" % (hx, lbl, hue(hx)))
        for d, c, s in near:
            print("     %5.1f  %s  %s" % (d, c, s))


# What shipped: the pink family's optimum. Worst-case CIE76 to all 248 shipped
# accents is 17.3, against 18.0 for the freest pair anywhere on the wheel — a
# kelly green with nothing to do with him. The saturated pinks and the mustard
# are all spoken for (see pass 1), so this is the sun-bleached register of his
# palette rather than the candy one.
CHOSEN = ("#9F6066", "#C69FA3")

if __name__ == "__main__":
    main()
