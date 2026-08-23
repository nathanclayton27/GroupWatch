"""HowLongToBeat story hours, behind the verify-by-name gate.

The gate is the house rule that once kept a text adventure called Lost Pig
out of Metal Gear: a result only counts when its name normalizes to what
was asked for, and (when a year is given) its release year sits inside the
window. Games that fail ship unweighted with a note — never a guessed
number.
"""
import re
import unicodedata


def _norm(t):
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    t = re.sub(r"[^a-z0-9]+", " ", t).strip()
    return re.sub(r"^(the|a|an) ", "", t)


def story_hours(name, year=None, year_slack=2, results=None):
    """Main-story hours for `name`, or None with a reason.

    `results` is the list from howlongtobeatpy's search (injected so callers
    control fetching/caching/retries). Returns (hours, entry, reason) where
    hours is None if nothing verified. comp_main is seconds.
    """
    if results is None:
        from howlongtobeatpy import HowLongToBeat
        results = HowLongToBeat().search(name) or []
    want = _norm(name)
    for r in results:
        got = _norm(getattr(r, "game_name", "") or "")
        if got != want:
            # HLTB suffixes some DLC entries with a literal " DLC"
            if got != want + " dlc":
                continue
        ry = getattr(r, "release_world", None)
        if year and ry and abs(int(ry) - year) > year_slack:
            return None, r, ("year mismatch: HLTB says %s, wanted %d" % (ry, year))
        secs = getattr(r, "comp_main", 0) or 0
        if secs <= 0:
            return None, r, "verified by name but no main-story figure"
        return round(secs / 3600.0, 2), r, "ok"
    return None, None, ("no result named %r (had: %s)"
                        % (name, [getattr(r, "game_name", "?")
                                  for r in results[:4]]))
