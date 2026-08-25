#!/usr/bin/env python3
"""Pick the Christopher Nolan accent pair against every accent already shipped.

    PYTHONIOENCODING=utf-8 python scratch/nolan/accent.py            # scan
    PYTHONIOENCODING=utf-8 python scratch/nolan/accent.py '#RRGGBB'  # compare

Reads properties/index.json — the manifest carries every list's `accent` and
`accentDark`, so the comparison is against the whole catalogue and not against
a handful of lists someone remembered. Converts to CIELAB and scores candidates
by worst-case CIE76 distance to the shipped set.

Two scans, because pure max-min is a trap: the furthest-away colour is always
the one nobody wanted, so max-min alone drifts to muted mid-chroma mud. The
second scan keeps only candidates that clear a distance floor AND carry real
chroma, then ranks by chroma, so the choice is made among colours that look
like accents. Candidates in both scans stay inside the (L*, chroma) box the
shipped accents measurably occupy.

Any hex given on the command line is reported with its five nearest shipped
accents in each mode, which is the number that actually has to be defended.
"""
import colorsys
import json
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]

LIGHT_FLOOR, LIGHT_CHROMA = 16.0, 28.0
DARK_FLOOR, DARK_CHROMA = 15.0, 40.0


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


def load():
    manifest = json.loads((ROOT / "properties" / "index.json")
                          .read_text(encoding="utf-8"))
    light = [m["accent"] for m in manifest if m.get("accent")]
    dark = [m["accentDark"] for m in manifest if m.get("accentDark")]
    slug_of = {}
    for m in manifest:
        slug_of.setdefault(m["accent"], m["slug"])
        slug_of.setdefault(m["accentDark"], m["slug"])
    return manifest, light, dark, slug_of


GRID = sorted({hexof(h, s, l) for h in range(0, 360, 1)
               for s in (0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85)
               for l in (0.14, 0.18, 0.22, 0.26, 0.30, 0.34, 0.38, 0.42,
                         0.50, 0.58, 0.62, 0.66, 0.70, 0.74, 0.78)})


def main():
    manifest, light, dark, slug_of = load()
    print("shipped lists: %d  (%d light accents, %d dark)"
          % (len(manifest), len(light), len(dark)))
    Ls = [srgb_to_lab(c) for c in light]
    Ds = [srgb_to_lab(c) for c in dark]
    lband, dband = band(light), band(dark)
    print("light accents occupy L* %.0f-%.0f, chroma %.0f-%.0f" % lband)
    print("dark  accents occupy L* %.0f-%.0f, chroma %.0f-%.0f" % dband)

    def scan(against, box, label, floor, minc):
        lo_l, hi_l, lo_c, hi_c = box
        far, colourful = [], []
        for hx in GRID:
            lab = srgb_to_lab(hx)
            if not (lo_l <= lab[0] <= hi_l and lo_c <= chroma(lab) <= hi_c):
                continue
            d = min(de(lab, o) for o in against)
            far.append((d, hx, lab))
            if d >= floor and chroma(lab) >= minc:
                colourful.append((chroma(lab), d, hx, lab))
        far.sort(reverse=True)
        colourful.sort(reverse=True)
        print("\ntop in-band %s by worst-case CIE76 to shipped:" % label)
        for d, hx, lab in far[:6]:
            print("   %s  minDE %5.1f   L*=%5.1f C=%5.1f h=%3.0f"
                  % (hx, d, lab[0], chroma(lab), hue(hx)))
        print("%s clearing minDE %.0f with chroma >= %.0f: %d candidates, "
              "one per 10 deg of hue:" % (label, floor, minc, len(colourful)))
        seen = set()
        for c, d, hx, lab in colourful:
            k = int(hue(hx)) // 10
            if k in seen:
                continue
            seen.add(k)
            print("   %s  C=%5.1f  minDE %5.1f  L*=%5.1f  h=%3.0f"
                  % (hx, c, d, lab[0], hue(hx)))
        return far

    sl = scan(Ls, lband, "LIGHT", LIGHT_FLOOR, LIGHT_CHROMA)
    sd = scan(Ds, dband, "DARK", DARK_FLOOR, DARK_CHROMA)

    # A house accent pair is one hue: the dark value is the same colour opened
    # up. Score pairs jointly and keep the hues within 12 degrees, then report
    # the best per hue bucket so the pick is made across the wheel rather than
    # from whatever the top of one list happened to be.
    pairs = []
    for dl, hl, _ in sl[:900]:
        for dd, hd, _ in sd[:900]:
            gap = abs(hue(hl) - hue(hd))
            gap = min(gap, 360 - gap)
            if gap <= 12:
                pairs.append((min(dl, dd), dl, dd, hl, hd))
    pairs.sort(reverse=True)
    print("\nbest single-hue pairs, one per 15 deg of hue:")
    seen = set()
    for worst, dl, dd, hl, hd in pairs:
        k = int(hue(hl)) // 15
        if k in seen:
            continue
        seen.add(k)
        print("   %s / %s   worst minDE %5.1f  (light %4.1f, dark %4.1f)  "
              "hue %3.0f/%3.0f" % (hl, hd, worst, dl, dd, hue(hl), hue(hd)))

    for hx in sys.argv[1:]:
        lab = srgb_to_lab(hx)
        for label, names in (("light", light), ("dark", dark)):
            near = sorted((de(lab, srgb_to_lab(c)), c, slug_of[c])
                          for c in names)[:5]
            print("\n%s vs the %d %s accents:  L*=%.1f C=%.1f h=%.0f"
                  % (hx, len(names), label, lab[0], chroma(lab), hue(hx)))
            for d, c, slug in near:
                print("   %5.1f  %s  %s" % (d, c, slug))


if __name__ == "__main__":
    main()
