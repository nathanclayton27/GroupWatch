#!/usr/bin/env python3
"""How far a candidate accent sits from every accent already in the catalogue.

    python scratch/naruto/accent.py            # rank the candidates
    python scratch/naruto/accent.py '#123456'  # score one colour

sRGB -> linear -> XYZ (D65) -> CIELAB, then plain CIE76 distance in Lab. The
number that matters is the distance to the NEAREST existing accent: a colour
can be lovely and still be a duplicate of one list three rows down.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent

CANDIDATES = [
    ("#2E7D6B", "deep teal"),
    ("#1F6F8B", "petrol blue"),
    ("#3F5FA8", "indigo"),
    ("#6B4C9A", "violet"),
    ("#8A2E5D", "plum"),
    ("#4A7A2B", "moss"),
    ("#B03A48", "brick"),
    ("#2F6D4F", "pine"),
    ("#5B6270", "slate"),
    ("#0F7B7B", "peacock"),
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


def score(hexstr, existing):
    ranked = sorted(((dist(hexstr, a), s, a) for s, a in existing))
    return ranked


def main():
    existing = catalogue()
    print("%d accents in the catalogue" % len(existing))
    args = [(a, "") for a in sys.argv[1:]] or CANDIDATES
    rows = []
    for hexstr, name in args:
        ranked = score(hexstr, existing)
        rows.append((ranked[0][0], hexstr, name, ranked[:3]))
    for d, hexstr, name, near in sorted(rows, reverse=True):
        print("\n%s %-14s nearest %.1f" % (hexstr, name, d))
        for dd, slug, acc in near:
            print("    %6.1f  %-26s %s" % (dd, slug, acc))


if __name__ == "__main__":
    main()
