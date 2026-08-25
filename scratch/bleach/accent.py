#!/usr/bin/env python3
"""How far a candidate Bleach accent sits from every accent in the catalogue.

    python scratch/bleach/accent.py            # rank the candidates
    python scratch/bleach/accent.py '#123456'  # score one colour

sRGB -> linear -> XYZ (D65) -> CIELAB, then plain CIE76 distance in Lab. The
number that matters is the distance to the NEAREST existing accent: a colour
can be right for the show and still be a duplicate of a list three rows down.

Bleach's obvious colour is Ichigo orange, and orange is the most crowded band
on this catalogue, so the candidates below also cover the show's other two
signatures: the steel/slate greys of the Soul Society palette and the deep
Quincy red the Thousand-Year Blood War branding uses.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent

CANDIDATES = [
    ("#E8781E", "Ichigo orange"),
    ("#D2571E", "burnt orange"),
    ("#AC1E1B", "TYBW red"),
    ("#8E1B24", "Quincy blood"),
    ("#485858", "season 1 slate"),
    ("#3D5A6C", "Soul Society steel"),
    ("#5B7B8C", "pale steel"),
    ("#2B4C6F", "deep steel blue"),
    ("#6E4B8E", "Hollow violet"),
    ("#1F5E5A", "Zanpakuto teal"),
]


def to_lab(hexstr):
    h = hexstr.lstrip("#")
    rgb = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    lin = [(c / 12.92) if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
           for c in rgb]
    r, g, b = lin
    x = (0.4124564 * r + 0.3575761 * g + 0.1804375 * b) / 0.95047
    y = (0.2126729 * r + 0.7151522 * g + 0.0721750 * b) / 1.00000
    z = (0.0193339 * r + 0.1191920 * g + 0.9503041 * b) / 1.08883

    def f(t):
        return t ** (1.0 / 3) if t > 216 / 24389 else (841 / 108) * t + 4 / 29

    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def dist(a, b):
    la, lb = to_lab(a), to_lab(b)
    return sum((p - q) ** 2 for p, q in zip(la, lb)) ** 0.5


def catalogue():
    rows = json.loads((ROOT / "properties" / "index.json")
                      .read_text(encoding="utf-8"))
    return [(m["slug"], m["accent"]) for m in rows if m.get("accent")]


def main():
    existing = catalogue()
    print("%d accents in the catalogue" % len(existing))
    args = [(a, "") for a in sys.argv[1:]] or CANDIDATES
    rows = []
    for hexstr, name in args:
        ranked = sorted((dist(hexstr, a), s, a) for s, a in existing)
        rows.append((ranked[0][0], hexstr, name, ranked[:3]))
    for d, hexstr, name, near in sorted(rows, reverse=True):
        print("\n%s %-20s nearest %.1f" % (hexstr, name, d))
        for dd, slug, acc in near:
            print("    %6.1f  %-26s %s" % (dd, slug, acc))


if __name__ == "__main__":
    main()
