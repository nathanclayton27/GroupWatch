#!/usr/bin/env python3
"""Pick an accent pair perceptually distant from every accent already in use.

    python3 scratch/bondgames/pick_accent.py

Reads the live accents out of properties/index.json, converts everything to
CIELAB, and scores candidates by their minimum CIEDE2000 distance to the whole
existing set — light accents against light accents, dark against dark, since
the two are shown in different themes and never compared to each other.
Eyeballing hex codes is how three near-identical blues shipped.
"""
import json
import math
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent


def srgb_to_lab(hexs):
    r, g, b = (int(hexs[i:i + 2], 16) / 255.0 for i in (1, 3, 5))

    def lin(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = lin(r), lin(g), lin(b)
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 1.00000
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883

    def f(t):
        return t ** (1 / 3.0) if t > 216 / 24389 else (841 / 108) * t + 4 / 29

    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def lab_to_srgb(lab):
    """Lab -> "#RRGGBB", or None when the colour is outside the sRGB gamut."""
    l, a, b = lab
    fy = (l + 16) / 116
    fx, fz = fy + a / 500, fy - b / 200

    def finv(t):
        return t ** 3 if t ** 3 > 216 / 24389 else (t - 4 / 29) * 108 / 841

    x, y, z = finv(fx) * 0.95047, finv(fy), finv(fz) * 1.08883
    r = 3.2406 * x - 1.5372 * y - 0.4986 * z
    g = -0.9689 * x + 1.8758 * y + 0.0415 * z
    bb = 0.0557 * x - 0.2040 * y + 1.0570 * z

    def gam(c):
        return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055

    out = []
    for c in (r, g, bb):
        v = gam(c)
        if v < -0.002 or v > 1.002:
            return None
        out.append(max(0, min(255, round(v * 255))))
    return "#%02X%02X%02X" % tuple(out)


def ciede2000(lab1, lab2):
    """The CIE's 2000 colour-difference formula, as published."""
    l1, a1, b1 = lab1
    l2, a2, b2 = lab2
    c1, c2 = math.hypot(a1, b1), math.hypot(a2, b2)
    cbar = (c1 + c2) / 2
    g = 0.5 * (1 - math.sqrt(cbar ** 7 / (cbar ** 7 + 25 ** 7))) if cbar else 0
    a1p, a2p = (1 + g) * a1, (1 + g) * a2
    c1p, c2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1p = math.degrees(math.atan2(b1, a1p)) % 360 if (a1p or b1) else 0
    h2p = math.degrees(math.atan2(b2, a2p)) % 360 if (a2p or b2) else 0
    dlp = l2 - l1
    dcp = c2p - c1p
    if c1p * c2p == 0:
        dhp = 0
    elif abs(h2p - h1p) <= 180:
        dhp = h2p - h1p
    else:
        dhp = h2p - h1p - 360 if h2p > h1p else h2p - h1p + 360
    dHp = 2 * math.sqrt(c1p * c2p) * math.sin(math.radians(dhp) / 2)
    lbar, cbarp = (l1 + l2) / 2, (c1p + c2p) / 2
    if c1p * c2p == 0:
        hbarp = h1p + h2p
    elif abs(h1p - h2p) <= 180:
        hbarp = (h1p + h2p) / 2
    elif h1p + h2p < 360:
        hbarp = (h1p + h2p + 360) / 2
    else:
        hbarp = (h1p + h2p - 360) / 2
    t = (1 - 0.17 * math.cos(math.radians(hbarp - 30))
         + 0.24 * math.cos(math.radians(2 * hbarp))
         + 0.32 * math.cos(math.radians(3 * hbarp + 6))
         - 0.20 * math.cos(math.radians(4 * hbarp - 63)))
    dtheta = 30 * math.exp(-(((hbarp - 275) / 25) ** 2))
    rc = 2 * math.sqrt(cbarp ** 7 / (cbarp ** 7 + 25 ** 7))
    sl = 1 + (0.015 * (lbar - 50) ** 2) / math.sqrt(20 + (lbar - 50) ** 2)
    sc = 1 + 0.045 * cbarp
    sh = 1 + 0.015 * cbarp * t
    rt = -math.sin(math.radians(2 * dtheta)) * rc
    return math.sqrt((dlp / sl) ** 2 + (dcp / sc) ** 2 + (dHp / sh) ** 2
                     + rt * (dcp / sc) * (dHp / sh))


def main():
    idx = json.loads((ROOT / "properties" / "index.json")
                     .read_text(encoding="utf-8"))
    light = {p["accent"]: p["slug"] for p in idx if p.get("accent")}
    dark = {p["accentDark"]: p["slug"] for p in idx if p.get("accentDark")}
    print("%d light accents, %d dark accents in use" % (len(light), len(dark)))

    light_lab = [(srgb_to_lab(h), s) for h, s in light.items()]
    dark_lab = [(srgb_to_lab(h), s) for h, s in dark.items()]

    # 120 properties have already spent most of the wheel, so search rather
    # than guess. The two accents are the same colour in two themes, so they
    # must share a hue: sweep LCh hue, and within each hue take the best
    # lightness/chroma in the band each theme actually uses (a light accent
    # has to read on white, a dark one on near-black). Score a hue by the
    # worse of its two distances — the pair is only as distinct as its
    # weakest half.
    # The bands are what the two themes actually use: a light accent lives
    # around L* 34-44 so it reads as text on white, a dark one around 72-82
    # so it reads on near-black, and chroma stays between 30 and 62 so the
    # winner is a colour rather than a grey. Unconstrained, the maximiser just
    # walks to the pale desaturated corner nothing else occupies.
    LIGHT_BAND, DARK_BAND, CHROMA = (34, 44), (72, 82), (30, 62)

    def best_in_band(pool, hue, band):
        won, wonlab, score, near = None, None, -1, None
        rad = math.radians(hue)
        for li in range(band[0], band[1] + 1):
            for c in range(CHROMA[0], CHROMA[1], 2):
                lab = (li, c * math.cos(rad), c * math.sin(rad))
                hexs = lab_to_srgb(lab)
                if not hexs:
                    continue
                d, who = min((ciede2000(lab, o), s) for o, s in pool)
                if d > score:
                    won, wonlab, score, near = hexs, lab, d, who
        return won, wonlab, score, near

    ranked = []
    for hue in range(0, 360, 2):
        lw = best_in_band(light_lab, hue, LIGHT_BAND)
        dw = best_in_band(dark_lab, hue, DARK_BAND)
        if not lw[0] or not dw[0]:
            continue
        ranked.append((min(lw[2], dw[2]), hue, lw, dw))
    ranked.sort(reverse=True)
    print("\ntop hues by worst-half distance:")
    for score, hue, lw, dw in ranked[:6]:
        print("   h=%3d  %s / %s  min dE %5.2f  (light->%s %.2f, dark->%s %.2f)"
              % (hue, lw[0], dw[0], score, lw[3], lw[2], dw[3], dw[2]))

    _, hue, (a, alab, ascore, anear), (ad, adlab, adscore, adnear) = ranked[0]
    print("\nchosen hue %d" % hue)
    print("light accent %s  L*=%.1f  nearest in use: %s at dE %.2f"
          % (a, alab[0], anear, ascore))
    print("dark  accent %s  L*=%.1f  nearest in use: %s at dE %.2f"
          % (ad, adlab[0], adnear, adscore))
    near_light = sorted((ciede2000(alab, o), s) for o, s in light_lab)[:5]
    near_dark = sorted((ciede2000(adlab, o), s) for o, s in dark_lab)[:5]
    print("\nnearest five, light:")
    for d, s in near_light:
        print("   %-24s dE %5.2f" % (s, d))
    print("nearest five, dark:")
    for d, s in near_dark:
        print("   %-24s dE %5.2f" % (s, d))

    versus = {}
    for slug in ("bond", "star-wars-games"):
        p = next(x for x in idx if x["slug"] == slug)
        versus[slug] = {
            "accent": p["accent"], "accentDark": p["accentDark"],
            "dE_light": round(ciede2000(alab, srgb_to_lab(p["accent"])), 2),
            "dE_dark": round(ciede2000(adlab, srgb_to_lab(p["accentDark"])), 2),
        }
        print("against %s (%s / %s): light dE %.2f, dark dE %.2f"
              % (slug, p["accent"], p["accentDark"],
                 versus[slug]["dE_light"], versus[slug]["dE_dark"]))

    (pathlib.Path(__file__).resolve().parent / "accent.json").write_text(
        json.dumps({
            "accent": a, "accentDark": ad, "hue": hue,
            "compared_against": {"light": len(light), "dark": len(dark)},
            "nearest_light": [{"slug": s, "dE": round(d, 2)}
                              for d, s in near_light],
            "nearest_dark": [{"slug": s, "dE": round(d, 2)}
                             for d, s in near_dark],
            "versus": versus,
        }, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
