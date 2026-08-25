#!/usr/bin/env python3
"""Nearest existing catalogue accent to a candidate, in CIELAB.

    python scratch/aot/accent_check.py "#3F5B34" "#8FBF6A"

Compares each candidate against every `accent` and every `accentDark` already
in properties/index.json (both, because a light candidate sitting on top of
someone else's dark value still reads as a collision on a dark-theme card).
sRGB -> linear -> XYZ (D65) -> Lab, plain CIE76 distance: the catalogue only
needs "is this visibly its own colour", not a perceptual-uniformity argument.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent


def lab(hex_):
    r, g, b = (int(hex_[i:i + 2], 16) / 255.0 for i in (1, 3, 5))

    def lin(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = lin(r), lin(g), lin(b)
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 1.00000
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883

    def f(t):
        return t ** (1 / 3.0) if t > 0.008856 else (7.787 * t + 16 / 116.0)

    fx, fy, fz = f(x), f(y), f(z)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def dist(a, b):
    return sum((x - y) ** 2 for x, y in zip(lab(a), lab(b))) ** 0.5


def main():
    idx = json.loads((ROOT / "properties" / "index.json")
                     .read_text(encoding="utf-8"))
    pool = [(e["slug"], k, e[k]) for e in idx
            for k in ("accent", "accentDark") if e.get(k)]
    print("%d accent values across %d lists" % (len(pool), len(idx)))
    for cand in sys.argv[1:]:
        near = sorted(((dist(cand, v), s, k, v) for s, k, v in pool))[:5]
        print("\n%s" % cand)
        for d, s, k, v in near:
            print("   dE %6.2f  %-28s %-11s %s" % (d, s, k, v))


if __name__ == "__main__":
    main()
