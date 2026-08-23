"""Static sweep: every property, every convention, every stray artifact.

Checks the classes of bug this project has actually shipped: wikitext plumbing
leaking into display strings, "0 films and" phrasing, ids that break build.py,
filter values with no tagged rows, paceTiers pointing at tiers nobody uses,
duplicate orders and accents, weights that are negative or absurd, and empty
or placeholder text where a reader would see it.
"""
import json
import pathlib
import re
import collections

PROPS = pathlib.Path("properties")
ID_OK = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")
WIKI_JUNK = re.compile(r"\[\[|\]\]|\{\{|\}\}|<ref|</ref|''|&nbsp;|<br|\|\||File:|thumb\|"
                       r"|rowspan=|colspan=|scope=|align=|style=")
HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")
ZERO_PHRASE = re.compile(r"\b0 (films?|seasons?|games?|episodes?|entries|shows?|winners?)\b")

findings = collections.defaultdict(list)
orders, accents = {}, {}

for f in sorted(PROPS.glob("*.json")):
    if f.name in ("index.json", "search.json"):
        continue
    slug = f.stem
    try:
        p = json.loads(f.read_text(encoding="utf-8"))
    except Exception as e:
        findings[slug].append("INVALID JSON: %s" % e)
        continue

    if p.get("slug") != slug:
        findings[slug].append("slug mismatch: %r" % p.get("slug"))
    for field in ("title", "unit"):
        if not p.get(field):
            findings[slug].append("missing %s" % field)
    u = p.get("unit") or {}
    if not (u.get("one") and u.get("many")):
        findings[slug].append("unit incomplete")

    o = p.get("order")
    if o in orders:
        findings[slug].append("order %s shared with %s" % (o, orders[o]))
    orders[o] = slug
    for k in ("accent", "accentDark"):
        v = p.get(k)
        if v and not HEX.match(v):
            findings[slug].append("%s not hex: %r" % (k, v))
    a = (p.get("accent"), p.get("accentDark"))
    if a in accents:
        findings[slug].append("accent pair shared with %s" % accents[a])
    accents[a] = slug

    ids, tiers_used, tags_used = [], set(), set()
    for s in p.get("sections", []):
        if not s.get("items"):
            findings[slug].append("empty section %r" % s.get("id"))
        if not ID_OK.match(s.get("id", "")):
            findings[slug].append("bad section id %r" % s.get("id"))
        for text_field in ("title", "sub", "intro"):
            v = s.get(text_field) or ""
            if WIKI_JUNK.search(v):
                findings[slug].append("wikitext junk in section %s %s: %r"
                                      % (s.get("id"), text_field, v[:60]))
            if ZERO_PHRASE.search(v):
                findings[slug].append("zero-phrase in section %s: %r"
                                      % (s.get("id"), v[:60]))
        for x in s.get("items", []):
            ids.append(x.get("id"))
            # build.py only enforces the strict charset on slugs and section
            # ids; item ids with accents and dots are live and load-bearing.
            # What actually breaks: whitespace, quotes, angle brackets.
            xid = x.get("id") or ""
            if not xid or re.search(r"[\s\"'<>&\\]", xid):
                findings[slug].append("dangerous item id %r" % xid)
            if not x.get("t"):
                findings[slug].append("item with no title: %r" % x.get("id"))
            w = x.get("w")
            if w is not None and (not isinstance(w, (int, float)) or w < 0 or w > 300):
                findings[slug].append("odd weight %r on %s" % (w, x.get("id")))
            tiers_used.add(x.get("tier") or s.get("tier") or 1)
            for t in x.get("tags") or []:
                tags_used.add(t)
            for text_field in ("t", "n", "note"):
                v = x.get(text_field)
                if isinstance(v, str) and WIKI_JUNK.search(v):
                    findings[slug].append("wikitext junk in %s.%s: %r"
                                          % (x.get("id"), text_field, v[:70]))
    dupes = [k for k, c in collections.Counter(ids).items() if c > 1]
    if dupes:
        findings[slug].append("duplicate ids: %s" % dupes[:4])

    flt = p.get("filter")
    if flt:
        vals = set(flt.get("values") or [])
        dead = vals - tags_used
        if dead:
            findings[slug].append("filter values with no tagged rows: %s" % sorted(dead))
        stray = tags_used - vals
        if stray:
            findings[slug].append("tags not in filter values: %s" % sorted(stray))
    elif tags_used:
        findings[slug].append("rows carry tags but no filter is declared: %s"
                              % sorted(tags_used)[:4])

    pt = p.get("paceTiers")
    if pt:
        missing = set(pt) - tiers_used
        if missing:
            findings[slug].append("paceTiers %s includes unused tier(s) %s"
                                  % (pt, sorted(missing)))

    alt = p.get("altSections")
    if alt:
        alt_ids = [x["id"] for s in alt.get("sections", []) for x in s.get("items", [])]
        if not set(alt_ids) <= set(ids):
            findings[slug].append("altSections invents ids")

    for note in p.get("notes", []):
        text = note[1] if isinstance(note, list) else note
        if WIKI_JUNK.search(text or ""):
            findings[slug].append("wikitext junk in notes: %r" % text[:70])

# ---- the committed tree must be self-consistent: every manifest entry has
# its property file and vice versa. A masked git add once shipped a manifest
# offering seven pages whose JSON 404'd on the live site.
manifest_file = PROPS / "index.json"
if manifest_file.exists():
    manifest = {m["slug"] for m in json.loads(
        manifest_file.read_text(encoding="utf-8"))}
    on_disk = {f.stem for f in PROPS.glob("*.json")
               if f.name not in ("index.json", "search.json")}
    for miss in sorted(manifest - on_disk):
        findings[miss].append("IN MANIFEST BUT NO FILE — would 404 live")
    for stray in sorted(on_disk - manifest):
        findings[stray].append("file not in manifest — rebuild before commit")

total = sum(len(v) for v in findings.values())
print("properties checked:", len(list(PROPS.glob('*.json'))) - 1)
print("findings:", total)
KNOWN = {("lanterns", "order 8"), ("metal-gear", "order 12"), ("one-pace", "order 6")}
serious = 0
for slug in sorted(findings):
    for msg in findings[slug]:
        known = any(slug == s and msg.startswith(m) for s, m in KNOWN)
        if not known:
            serious += 1
        print("  %-18s %s%s" % (slug, msg, "  (known tie)" if known else ""))
if serious:
    print("\n%d finding(s) beyond the known order ties" % serious)
    raise SystemExit(1)
