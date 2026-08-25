#!/usr/bin/env python3
"""Pick the FPS-canon accent pair by measuring it against the whole catalogue.

    python scratch/fps/pick_accent.py

Reads every accent and accentDark already shipping in properties/index.json,
converts to CIE Lab, and scores candidate hues by their nearest neighbour
(CIE76 delta-E) across BOTH palettes at once — a new list has to be
distinguishable from every card on the wall, not just from the ones in its own
theme. Prints the ranking so the pick is arguable in a diff instead of
eyeballed.
"""
import colorsys
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent


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


def main():
    index = json.loads((ROOT / "properties" / "index.json")
                       .read_text(encoding="utf-8"))
    # Once fps-canon is in the manifest it would score zero against itself
    # and hide the real nearest neighbour, so it is dropped from the field.
    index = [e for e in index if e["slug"] != "fps-canon"]
    taken = []
    for e in index:
        for key in ("accent", "accentDark"):
            if e.get(key):
                taken.append((e["slug"] + "." + key, srgb_to_lab(e[key]),
                              e[key]))
    print("compared against %d colours from %d shipped lists"
          % (len(taken), len(index)))

    def nearest(hexstr):
        lab = srgb_to_lab(hexstr)
        return min(((de(lab, l), n, h) for n, l, h in taken))

    # light-mode accents live dark and saturated (they sit on white); the
    # dark-mode ones live light and saturated (they sit on near-black).
    # Sweep hue, saturation and value inside those bands rather than at one
    # fixed point — the catalogue is 124 lists deep and the headroom is in
    # the corners.
    for label, sats, vals in (
            ("accent    ", (0.55, 0.7, 0.85, 1.0), (0.40, 0.5, 0.6)),
            ("accentDark", (0.35, 0.5, 0.65, 0.8), (0.85, 0.93, 1.0))):
        rows = []
        for hue in range(0, 360, 5):
            for s in sats:
                for v in vals:
                    c = hexof(hue, s, v)
                    d, who, hx = nearest(c)
                    rows.append((d, hue, c, who, hx))
        rows.sort(reverse=True)
        print("\n%s — best-separated candidates" % label)
        seen = set()
        for d, hue, c, who, hx in rows:
            if hue // 20 in seen:
                continue
            seen.add(hue // 20)
            print("   h=%3d  %s  nearest %.1f  %s %s" % (hue, c, d, who, hx))
            if len(seen) >= 10:
                break

    print("\nshortlist (thematic candidates, scored):")
    for name, pair in (
            ("muzzle orange/red", ("#B5401C", "#FF8A4C")),
            ("plasma violet    ", ("#5B2E9E", "#B98BFF")),
            ("HUD cyan         ", ("#0F6E7A", "#4FE0E8")),
            ("hazard amber     ", ("#8A6A00", "#FFCC33")),
            ("blood crimson    ", ("#8E1B2E", "#FF6B7E")),
            ("toxic green a    ", ("#0E7A1C", "#4CE05C")),
            ("toxic green b    ", ("#128A20", "#56E869")),
            ("toxic green c    ", ("#17832B", "#3FE05A")),
            ("CHOSEN           ", ("#10851E", "#4FE863"))):
        out = []
        for c in pair:
            d, who, hx = nearest(c)
            out.append("%s nearest %.1f (%s %s)" % (c, d, who, hx))
        print("   %s  %s" % (name, "  |  ".join(out)))

    # contrast against the two grounds the accents actually sit on
    def lum(h):
        def lin(c):
            c /= 255.0
            return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
        r, g, b = (int(h[i:i + 2], 16) for i in (1, 3, 5))
        return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)

    def ratio(a, b):
        la, lb = sorted((lum(a) + 0.05, lum(b) + 0.05))
        return lb / la

    # The pick: a toxic green nothing in the catalogue occupies. Every other
    # thematic candidate lands inside delta-E 11 of something already
    # shipping (muzzle orange sits 9.0 from Metroid, hazard amber 4.8 from
    # MST3K), while the greens already here are all muted or olive — Muppets,
    # Halo, Urusei Yatsura, Metal Gear — so the saturated corner is empty.
    print("\ncontrast of the pick:")
    for c, ground in (("#10851E", "#FFFFFF"), ("#4FE863", "#111418")):
        print("   %s on %s  %.2f:1" % (c, ground, ratio(c, ground)))


if __name__ == "__main__":
    main()
