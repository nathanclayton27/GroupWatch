"""Pick an accent pair perceptually distant from every accent already shipped.

Distance is CIEDE2000 in CIELAB (D65), not eyeballed: sRGB -> linear -> XYZ ->
Lab -> dE00. Reports the nearest existing accent for each candidate so the
choice is defensible rather than asserted.
"""
import json, math, pathlib, colorsys

ROOT = pathlib.Path(__file__).resolve().parents[2]


def srgb_to_lab(hexs):
    h = hexs.lstrip("#")
    rgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    r, g, b = lin
    x = (0.4124564 * r + 0.3575761 * g + 0.1804375 * b) / 0.95047
    y = (0.2126729 * r + 0.7151522 * g + 0.0721750 * b) / 1.00000
    z = (0.0193339 * r + 0.1191920 * g + 0.9503041 * b) / 1.08883

    def f(t):
        return t ** (1 / 3) if t > 216 / 24389 else (841 / 108) * t + 4 / 29
    fx, fy, fz = f(x), f(y), f(z)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def de00(lab1, lab2):
    L1, a1, b1 = lab1
    L2, a2, b2 = lab2
    C1, C2 = math.hypot(a1, b1), math.hypot(a2, b2)
    Cb = (C1 + C2) / 2
    G = 0.5 * (1 - math.sqrt(Cb ** 7 / (Cb ** 7 + 25 ** 7))) if Cb else 0.5
    a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1p = math.degrees(math.atan2(b1, a1p)) % 360 if (a1p or b1) else 0
    h2p = math.degrees(math.atan2(b2, a2p)) % 360 if (a2p or b2) else 0
    dLp, dCp = L2 - L1, C2p - C1p
    if C1p * C2p == 0:
        dhp = 0
    elif abs(h2p - h1p) <= 180:
        dhp = h2p - h1p
    else:
        dhp = h2p - h1p - 360 if h2p > h1p else h2p - h1p + 360
    dHp = 2 * math.sqrt(C1p * C2p) * math.sin(math.radians(dhp) / 2)
    Lbp, Cbp = (L1 + L2) / 2, (C1p + C2p) / 2
    if C1p * C2p == 0:
        hbp = h1p + h2p
    elif abs(h1p - h2p) <= 180:
        hbp = (h1p + h2p) / 2
    elif h1p + h2p < 360:
        hbp = (h1p + h2p + 360) / 2
    else:
        hbp = (h1p + h2p - 360) / 2
    T = (1 - 0.17 * math.cos(math.radians(hbp - 30))
         + 0.24 * math.cos(math.radians(2 * hbp))
         + 0.32 * math.cos(math.radians(3 * hbp + 6))
         - 0.20 * math.cos(math.radians(4 * hbp - 63)))
    dTh = 30 * math.exp(-(((hbp - 275) / 25) ** 2))
    Rc = 2 * math.sqrt(Cbp ** 7 / (Cbp ** 7 + 25 ** 7)) if Cbp else 0
    Sl = 1 + (0.015 * (Lbp - 50) ** 2) / math.sqrt(20 + (Lbp - 50) ** 2)
    Sc, Sh = 1 + 0.045 * Cbp, 1 + 0.015 * Cbp * T
    Rt = -math.sin(math.radians(2 * dTh)) * Rc
    return math.sqrt((dLp / Sl) ** 2 + (dCp / Sc) ** 2 + (dHp / Sh) ** 2
                     + Rt * (dCp / Sc) * (dHp / Sh))


idx = json.loads((ROOT / "properties" / "index.json").read_text(encoding="utf-8"))
taken = [(p["slug"], p["accent"], p.get("accentDark")) for p in idx if p.get("accent")]
print("accents in use:", len(taken))
labs = [(s, srgb_to_lab(a)) for s, a, _ in taken]

# The light-mode accent has to read as text on white, so it lives in a narrow
# lightness band. Measure the band the shipped accents actually occupy and only
# consider candidates inside it — a "most distant" colour that is too pale to
# use is not a real answer.
Ls = sorted(l[0] for _, l in labs)
lo, hi = Ls[len(Ls) // 10], Ls[-len(Ls) // 10]
print("shipped accent L*: min %.1f  10th %.1f  median %.1f  90th %.1f  max %.1f"
      % (Ls[0], lo, Ls[len(Ls) // 2], hi, Ls[-1]))

cands = {}
for hue in range(0, 360, 3):
    for sat in (0.55, 0.65, 0.75, 0.85, 0.95):
        for val in (0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70):
            r, g, b = colorsys.hsv_to_rgb(hue / 360, sat, val)
            hexs = "#%02X%02X%02X" % (round(r * 255), round(g * 255), round(b * 255))
            cands[hexs] = None

scored = []
for hexs in cands:
    lab = srgb_to_lab(hexs)
    if not (lo <= lab[0] <= hi):
        continue
    d = sorted((de00(lab, l), s) for s, l in labs)
    scored.append((d[0][0], hexs, d[0][1], d[1][1], d[2][1]))
scored.sort(reverse=True)
print("\ncandidates inside the band, top 20 by nearest-neighbour dE00:")
for dist, hexs, n1, n2, n3 in scored[:20]:
    print("  %s  dE00 to nearest = %5.2f   (%s, %s, %s)" % (hexs, dist, n1, n2, n3))

import sys
for probe in sys.argv[1:]:
    lab = srgb_to_lab(probe)
    d = sorted((de00(lab, l), s) for s, l in labs)
    print("\n%s nearest existing accents:" % probe)
    for dist, s in d[:6]:
        print("   %5.2f  %-24s %s" % (dist, s, dict((x[0], x[1]) for x in taken)[s]))
