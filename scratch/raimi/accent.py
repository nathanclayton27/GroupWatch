#!/usr/bin/env python3
"""Pick an accent pair perceptually distant from every accent already shipped.

    PYTHONIOENCODING=utf-8 python scratch/raimi/accent.py

Reads properties/index.json (the manifest carries every list's accent and
accentDark), converts to CIELAB, and scans hue/sat/lightness for the pair whose
worst-case CIE76 distance to the shipped set is largest. Eyeballing "is this
red taken?" against 120 lists is how two near-identical accents ship.

Candidates are held inside the house bands so the winner is a usable accent
rather than a neon that happens to sit in an empty corner: the light-mode
accent stays at the L* and chroma the shipped light accents occupy, and the
dark-mode one likewise. Both bands are measured off the shipped set, not
guessed.
"""
import colorsys
import json
import math
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]


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


def band(hexes, lo_pct=0.05, hi_pct=0.95):
    """The (L*, chroma) box the shipped accents actually live in."""
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
    print("shipped lists: %d  (%d light accents, %d dark)"
          % (len(manifest), len(light), len(dark)))
    Ls = [srgb_to_lab(c) for c in light]
    Ds = [srgb_to_lab(c) for c in dark]

    lband, dband = band(light), band(dark)
    print("light accents occupy L* %.0f-%.0f, chroma %.0f-%.0f" % lband)
    print("dark  accents occupy L* %.0f-%.0f, chroma %.0f-%.0f" % dband)

    grid = [hexof(h, s, l) for h in range(0, 360, 1)
            for s in (0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75)
            for l in (0.14, 0.18, 0.22, 0.26, 0.30, 0.34, 0.38, 0.42,
                      0.50, 0.58, 0.62, 0.66, 0.70, 0.74, 0.78)]

    def best(against, box, label):
        lo_l, hi_l, lo_c, hi_c = box
        scored = []
        for hx in set(grid):
            lab = srgb_to_lab(hx)
            if not (lo_l <= lab[0] <= hi_l and lo_c <= chroma(lab) <= hi_c):
                continue
            scored.append((min(de(lab, o) for o in against), hx, lab))
        scored.sort(reverse=True)
        print("\ntop in-band %s candidates (worst-case CIE76 to shipped):" % label)
        for d, hx, lab in scored[:8]:
            print("   %s  minDE %5.1f   L*=%5.1f C=%5.1f h=%3.0f"
                  % (hx, d, lab[0], chroma(lab), hue(hx)))
        return scored

    sl = best(Ls, lband, "light")
    sd = best(Ds, dband, "dark")

    # A house accent pair is one hue: the dark value is the same colour opened
    # up. Score pairs jointly, requiring the hues to stay within 14 degrees.
    pairs = []
    for dl, hl, _ in sl[:600]:
        for dd, hd, _ in sd[:600]:
            gap = abs(hue(hl) - hue(hd))
            gap = min(gap, 360 - gap)
            if gap <= 14:
                pairs.append((min(dl, dd), dl, dd, hl, hd))
    pairs.sort(reverse=True)
    print("\nbest single-hue pairs:")
    for worst, dl, dd, hl, hd in pairs[:10]:
        print("   %s / %s   worst minDE %5.1f  (light %4.1f, dark %4.1f)  hue %.0f"
              % (hl, hd, worst, dl, dd, hue(hl)))

    worst, dl, dd, hl, hd = pairs[0]
    for hx, names in ((hl, light), (hd, dark)):
        lab = srgb_to_lab(hx)
        near = sorted((de(lab, srgb_to_lab(c)), c, slug_of[c]) for c in names)[:6]
        print("\n%s nearest shipped accents:" % hx)
        for d, c, slug in near:
            print("   %5.1f  %s  %s" % (d, c, slug))


if __name__ == "__main__":
    main()
