#!/usr/bin/env python3
"""Pick the Hunter x Hunter accent pair by measuring it against the catalogue.

    PYTHONIOENCODING=utf-8 python scratch/hxh/pick_accent.py

Reads every accent and accentDark already shipping in properties/index.json,
converts sRGB -> linear -> XYZ (D65) -> CIELAB, and scores candidates by their
nearest neighbour (CIE76 delta-E) across BOTH palettes at once: a new card has
to be distinguishable from every other card on the wall, not only from the
ones in its own theme. Prints the ranking so the pick is arguable in a diff.
"""
import colorsys
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
SLUG = "hunter-x-hunter"


def srgb_to_lab(hexstr):
    r, g, b = (int(hexstr[i:i + 2], 16) / 255.0 for i in (1, 3, 5))

    def lin(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = lin(r), lin(g), lin(b)
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 1.00000
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883

    def f(t):
        return t ** (1 / 3.0) if t > 0.008856 else 7.787 * t + 16 / 116.0

    fx, fy, fz = f(x), f(y), f(z)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def de(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


def hexof(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h / 360.0, s, v)
    return "#%02X%02X%02X" % (round(r * 255), round(g * 255), round(b * 255))


def lum(h):
    def lin(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (int(h[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def ratio(a, b):
    la, lb = sorted((lum(a) + 0.05, lum(b) + 0.05))
    return lb / la


# Thematic candidates. Hunter x Hunter's own colours are Gon's green jacket and
# the Nen aura; the greens in the catalogue are either muted (Ghibli, Godzilla,
# Zelda, Lanterns) or the saturated corner fps-canon already took, so the
# shortlist walks the green -> teal -> aqua edge looking for the gap.
SHORTLIST = [
    ("gon grass green ", ("#2E8B12", "#7BE04A")),
    ("jump green      ", ("#1E8C3A", "#5FE07E")),
    ("nen jade        ", ("#0E7F63", "#3FDCB0")),
    ("nen teal        ", ("#00807F", "#2FDCDC")),
    ("nen aqua        ", ("#00798C", "#35D6EE")),
    ("aura spring     ", ("#0F8552", "#3FE39A")),
    ("kurapika scarlet", ("#A31226", "#FF5468")),
    ("license gold    ", ("#8A6A10", "#F0C038")),
]


def main():
    index = json.loads((ROOT / "properties" / "index.json")
                       .read_text(encoding="utf-8"))
    index = [e for e in index if e["slug"] != SLUG]
    taken = []
    for e in index:
        for key in ("accent", "accentDark"):
            if e.get(key):
                taken.append((e["slug"] + "." + key, srgb_to_lab(e[key]),
                              e[key]))
    print("compared against %d colours from %d shipped lists"
          % (len(taken), len(index)))

    def nearest(hexstr, n=1):
        lab = srgb_to_lab(hexstr)
        return sorted((de(lab, l), who, h) for who, l, h in taken)[:n]

    args = sys.argv[1:]
    if args:
        for c in args:
            print("\n%s" % c)
            for d, who, h in nearest(c, 4):
                print("   %6.1f  %-28s %s" % (d, who, h))
        return

    # Light-mode accents sit on white and live dark+saturated; dark-mode ones
    # sit on near-black and live light+saturated. Sweep inside those bands.
    for label, sats, vals in (
            ("accent    ", (0.55, 0.7, 0.85, 1.0), (0.40, 0.5, 0.6)),
            ("accentDark", (0.35, 0.5, 0.65, 0.8), (0.85, 0.93, 1.0))):
        rows = []
        for hue in range(0, 360, 5):
            for s in sats:
                for v in vals:
                    c = hexof(hue, s, v)
                    d, who, hx = nearest(c)[0]
                    rows.append((d, hue, c, who, hx))
        rows.sort(reverse=True)
        print("\n%s — best-separated candidates" % label)
        seen = set()
        for d, hue, c, who, hx in rows:
            if hue // 20 in seen:
                continue
            seen.add(hue // 20)
            print("   h=%3d  %s  nearest %.1f  %s %s" % (hue, c, d, who, hx))
            if len(seen) >= 12:
                break

    print("\nshortlist (thematic candidates, scored against both palettes):")
    for name, pair in SHORTLIST:
        out = []
        for c in pair:
            d, who, hx = nearest(c)[0]
            out.append("%s nearest %5.1f (%s %s)" % (c, d, who, hx))
        print("   %s  %s" % (name, "  |  ".join(out)))

    print("\ncontrast of the shortlist:")
    for name, (lt, dk) in SHORTLIST:
        print("   %s  %s on #FFFFFF %5.2f:1   %s on #111418 %5.2f:1"
              % (name, lt, ratio(lt, "#FFFFFF"), dk, ratio(dk, "#111418")))


if __name__ == "__main__":
    main()
