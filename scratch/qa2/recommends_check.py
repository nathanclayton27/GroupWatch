"""Clubbothy Recommends (CLU-42): the shelf, the readiness gate, the hold.

  * the shelf sits in the slot the build reserved, with Tonight BELOW it
  * exactly three rows, never four, never a carousel
  * an ORDERED list contributes only its next unticked item — the reader is
    on #12 of Kurosawa and #30 must never surface, anywhere, ever
  * an UNORDERED list contributes anything unticked — Time Loops offers its
    189th entry to a reader who has ticked two
  * a fully ticked list contributes nothing, however loudly it is liked
  * every row carries one mono line of why: no line, no row
  * holding the eye lands a pick and pops the eye — fast up, slow down
  * a re-roll never repeats the pick before it
  * the shelf still works with the friends' thumbs read failing (which is
    the world the site ships in until migrate-add-thumbs.sql is run)
  * a signed-out reader sees none of it
  * no horizontal overflow at 1280 or 390

Stubbed Supabase the way thumbs_check.py does — a filterable table stub,
jsdelivr aborted so the real client cannot overwrite it — plus a MISSING set
so one run can prove the degraded world behaves.
"""
import json
import subprocess
import sys
import time

from playwright.sync_api import sync_playwright

PORT = 8153
srv = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.2)
if srv.poll() is not None:
    raise SystemExit(
        "PORT BUSY: another process already owns this port, so this script "
        "would have tested WHATEVER IT SERVES — possibly a stale build from "
        "another directory. Kill it and re-run.")

BASE = "http://localhost:%d/" % PORT

IX = json.load(open("properties/search.json", encoding="utf-8"))
MAN = {m["slug"]: m for m in
       json.load(open("properties/index.json", encoding="utf-8"))}


def rows(slug):
    return [r for r in IX["rows"] if r[0] == slug]


KUR = rows("kurosawa")          # ordered, 30 films — the reader stops at #12
LOOP = rows("time-loops")       # unordered (random) 189 entries
CARP = rows("carpenter")        # ordered, untracked, surfaced by friends
LANT = rows("lanterns")         # ordered, 8 episodes, finished outright
LYNCH = rows("david-lynch")     # ordered, 10, finished — the kin signal

KUR_NEXT = KUR[12][2]           # Ikiru — the only Kurosawa row that is ready
KUR_LAST = KUR[29][2]           # Madadayo — 17 films stand in front of it
LOOP_DEEP = LOOP[188]           # the 189th entry, offered on a two-tick list
CARP_FIRST = CARP[0]
# a row's meta line is the list's own title, which is not its slug
T = {s: MAN[s]["title"] for s in
     ("kurosawa", "time-loops", "carpenter", "lanterns", "david-lynch")}

NAMES = {"f1": "ada", "f2": "bo", "f3": "cy"}
FRIENDS = [{"a": "u1", "b": "f1"}, {"a": "f1", "b": "u1"},
           {"a": "u1", "b": "f2"}, {"a": "f2", "b": "u1"},
           {"a": "u1", "b": "f3"}, {"a": "f3", "b": "u1"}]
# Three friends on one Carpenter film, one on the deepest Time Loops entry.
# The second is the whole unordered case in one row: nothing on this device
# says the reader is anywhere near entry 189, and it is still startable.
FTHUMBS = [
    {"user_id": "f1", "property_id": "carpenter",
     "item_id": CARP_FIRST[1], "direction": "up"},
    {"user_id": "f2", "property_id": "carpenter",
     "item_id": CARP_FIRST[1], "direction": "up"},
    {"user_id": "f3", "property_id": "carpenter",
     "item_id": CARP_FIRST[1], "direction": "up"},
    {"user_id": "f1", "property_id": "time-loops",
     "item_id": LOOP_DEEP[1], "direction": "up"},
]

NOW = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
OLD = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - 5 * 86400))


def ev(ids, at):
    return json.dumps([{"i": i, "a": "tick", "k": "live", "at": at} for i in ids])


def thumbs(list_dir, items=None):
    return json.dumps({"list": list_dir, "items": items or {}})


KUR_DONE = [r[1] for r in KUR[:12]]
LOOP_DONE = [LOOP[0][1], LOOP[5][1]]
LANT_DONE = [r[1] for r in LANT]
LYNCH_DONE = [r[1] for r in LYNCH]

SEED = {
    "gw:acctname": "exx",
    "gw:syncback:off": "1",
    "gw:wallfold": "1",           # the wall folded keeps the page short
    # the reader is twelve films into an ordered run, likes the run as a
    # whole, and has thumbed two of the films inside it
    "gw:v1:kurosawa": json.dumps(KUR_DONE),
    "gw:evlog:kurosawa": ev(KUR_DONE, OLD),
    "gw:thumbs:v1:kurosawa": thumbs("up", {KUR[3][1]: "up", KUR[7][1]: "up"}),
    # two ticks on a 189-entry grab bag, also liked
    "gw:v1:time-loops": json.dumps(LOOP_DONE),
    "gw:evlog:time-loops": ev(LOOP_DONE, OLD),
    "gw:thumbs:v1:time-loops": thumbs("up"),
    # finished outright, and thumbed up as hard as the reader can — the
    # readiness gate has to beat the loudest possible taste signal
    "gw:v1:lanterns": json.dumps(LANT_DONE),
    "gw:evlog:lanterns": ev(LANT_DONE, NOW),
    "gw:thumbs:v1:lanterns": thumbs("up"),
    # finished this week: the freshest evidence of taste there is
    "gw:v1:david-lynch": json.dumps(LYNCH_DONE),
    "gw:evlog:david-lynch": ev(LYNCH_DONE, NOW),
}

STUB = """
window.supabase = { createClient: () => {
  const DB = %s;
  const MISSING = %s;
  const SIGNED = %s;
  const from = (t) => {
    const gone = MISSING.indexOf(t) >= 0;
    let rows = (DB[t] || []).map(r => Object.assign({}, r));
    let single = false;
    const err = { code: '42P01',
      message: 'relation "public.' + t + '" does not exist' };
    const api = {
      select(){ return api; }, order(){ return api; }, limit(){ return api; },
      gte(){ return api; }, lte(){ return api; }, gt(){ return api; },
      lt(){ return api; }, not(){ return api; },
      or(){ return api; }, neq(){ return api; },
      upsert(){ rows = []; return api; },
      insert(){ rows = []; return api; },
      update(){ rows = []; return api; },
      delete(){ rows = []; return api; },
      eq(k, v){ rows = rows.filter(r => r[k] === v); return api; },
      is(k, v){ rows = rows.filter(r => (r[k] === undefined ? null : r[k]) === v);
                return api; },
      in(k, vs){ rows = rows.filter(r => vs.indexOf(r[k]) >= 0); return api; },
      maybeSingle(){ single = true; return api; },
      single(){ single = true; return api; },
      then(res, rej){
        return Promise.resolve(gone
          ? { data: null, error: err }
          : { data: single ? (rows[0] || null) : rows, error: null }).then(res, rej);
      }
    };
    return api;
  };
  const mkUser = () => ({
    id: 'u1', email: 'exx@example.com',
    created_at: '2026-03-04T10:00:00Z',
    identities: [{ provider: 'email', identity_data: { email: 'exx@example.com' } }],
    user_metadata: { username: 'exx', fcode: 'CLB\\u00b7AAAA' }
  });
  const sess = () => SIGNED ? { user: mkUser() } : null;
  return {
    auth: {
      onAuthStateChange: (cb) => { setTimeout(() =>
        cb(SIGNED ? 'SIGNED_IN' : 'SIGNED_OUT', sess()), 30); return {}; },
      getSession: async () => ({ data: { session: sess() } }),
      getUser:    async () => ({ data: { user: SIGNED ? mkUser() : null } }),
      updateUser: async () => ({ data: { user: mkUser() }, error: null }),
      signOut: async () => ({}),
      signInWithOtp: async () => ({}), signInWithOAuth: async () => ({})
    },
    from, rpc: async () => ({ data: null, error: null })
  };
}};
"""


def db(with_thumbs):
    d = {
        "friendships": FRIENDS,
        "profiles": [{"user_id": k, "username": v, "fcode": "CLB·" + k.upper()}
                     for k, v in NAMES.items()],
        "groups": [], "group_members": [], "progress": [], "tick_events": [],
    }
    if with_thumbs:
        d["thumbs"] = FTHUMBS
    return d


ok = True
noise = []


def chk(name, cond):
    global ok
    print(("PASS " if cond else "FAIL ") + name)
    ok = ok and bool(cond)


def wire(pg):
    """Collect anything the page shouts. The aborted CDN script is this
    harness's own doing, so it is the one thing that does not count."""
    def seen(m):
        if m.type != "error":
            return
        if "jsdelivr" in ((m.location or {}).get("url") or ""):
            return
        noise.append("console.%s: %s" % (m.type, m.text))
    pg.on("pageerror", lambda e: noise.append("pageerror: %s" % e))
    pg.on("console", seen)
    return pg


def newpage(b, with_thumbs=True, signed=True, width=1280, seed=None):
    ctx = b.new_context(viewport={"width": width, "height": 900})
    ctx.route("**/cdn.jsdelivr.net/**", lambda route: route.abort())
    ctx.add_init_script(STUB % (json.dumps(db(with_thumbs)),
                                json.dumps([] if with_thumbs else ["thumbs"]),
                                "true" if signed else "false"))
    ctx.add_init_script(
        "(()=>{if(window.__seeded)return;window.__seeded=1;const s="
        + json.dumps(seed if seed is not None else SEED)
        + ";for(const k in s)localStorage.setItem(k,s[k]);})()")
    return wire(ctx.new_page())


def ready(pg):
    pg.goto(BASE)
    pg.wait_for_timeout(2000)


# One row, read the way a person reads it: the title, the list it lives on,
# and the single mono line of why.
READ = """s=>[...document.querySelectorAll(s)].map(e=>{
  const b = e.querySelector('.h b');
  let t = '';
  if(b){
    // the mono row number rides inside the title, exactly as Tonight does;
    // strip it so a title can be compared against the index
    const c = b.cloneNode(true), rn = c.querySelector('.rn');
    if(rn) rn.remove();
    t = c.textContent.trim();
  }
  return {
    t: t,
    rn: ((e.querySelector('.h .rn')||{}).textContent || '').trim(),
    n: ((e.querySelector('.n')||{}).textContent || '').trim(),
    w: ((e.querySelector('.why')||{}).textContent || '').trim(),
    kick: ((e.querySelector('.kick')||{}).textContent || '').trim()
  };
})"""


def shelf(pg):
    return pg.evaluate(READ, "#hrec .rec")


def picked(pg):
    got = pg.evaluate(READ, "#hrecpick .rec")
    return got[0] if got else None


def scale(pg):
    return pg.evaluate("""()=>{
      const m = getComputedStyle(document.getElementById('recwrap')).transform;
      if(!m || m === 'none') return 1;
      const p = m.match(/matrix\\(([^,]+),/);
      return p ? parseFloat(p[1]) : 1;
    }""")


def eyebox(pg):
    """The eye's box, with the page scrolled so it is really under the
    pointer — at 390 the shelf header can sit below the fold."""
    el = pg.locator("#rechold")
    el.scroll_into_view_if_needed()
    pg.wait_for_timeout(120)
    return el.bounding_box()


def hold(pg, ms=760, release=True):
    """Press and hold the eye. 620ms is the threshold; 760 lands past it."""
    box = eyebox(pg)
    pg.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    pg.mouse.down()
    pg.wait_for_timeout(ms)
    if release:
        pg.mouse.up()
        pg.wait_for_timeout(120)


def overflow(pg):
    return pg.evaluate(
        "()=>document.documentElement.scrollWidth - window.innerWidth")


try:
    with sync_playwright() as p:
        b = p.chromium.launch()

        # ============================================ the shelf, fully fed
        pg = newpage(b)
        ready(pg)

        order = pg.evaluate(
            "()=>[...document.querySelectorAll('#homev .hsec')]"
            ".filter(e=> !e.classList.contains('hide'))"
            ".map(e=> e.id || e.textContent.trim().split('\\n')[0].trim())")
        # the friend sections are legitimately between Lately and the shelf
        # when there are friends, so this is the relative order, not equality
        anchors = [x for x in order
                   if x in ("hrec-h", "Tonight", "The catalogue")]
        chk("the shelf claims the reserved slot: %s" % order,
            anchors == ["hrec-h", "Tonight", "The catalogue"])
        chk("Tonight really is below the shelf in the DOM", pg.evaluate(
            "()=>!!(document.getElementById('hrec').compareDocumentPosition("
            "document.getElementById('htonight')) & Node.DOCUMENT_POSITION_FOLLOWING)"))
        chk("the chips still sit between Tonight and the wall", pg.evaluate(
            "()=>{const c=document.getElementById('hchips'),"
            "w=document.getElementById('homewall'),"
            "t=document.getElementById('htonight');"
            "return !!(t.compareDocumentPosition(c) & Node.DOCUMENT_POSITION_FOLLOWING)"
            " && !!(c.compareDocumentPosition(w) & Node.DOCUMENT_POSITION_FOLLOWING);}"))

        s = shelf(pg)
        chk("exactly three rows (%d)" % len(s), len(s) == 3)
        chk("every row carries one mono line of why",
            len(s) == 3 and all(r["w"].strip() for r in s))
        chk("no row is a carousel: three lists, not three cuts of one (%s)"
            % [r["n"] for r in s],
            len({r["n"] for r in s}) == len(s))
        chk("the rows are real buttons, reachable by keyboard", pg.evaluate(
            "()=>[...document.querySelectorAll('#hrec .rec')]"
            ".every(e=> e.tagName === 'BUTTON')"))
        chk("the frame counts what is startable, and sits above the rows",
            pg.evaluate(
                "()=>{const q=document.querySelector('#hrechead .quiet');"
                "return !!q && q.textContent.trim() === '3 you could start"
                " tonight';}"))
        chk("...and writes no 'since you finished' it cannot show working for",
            pg.evaluate(
                "()=>{const b=document.querySelector('#hrechead b');"
                "const w=[...document.querySelectorAll('#hrec .rec .why')]"
                ".map(e=>e.textContent);"
                "return !b || w[0].indexOf('because you finished ') === 0;}"))

        # ------------------------------------------ the readiness gate
        kur = [r for r in s if r["n"] == T["kurosawa"]]
        chk("the ordered run offers its next unticked film (%s)"
            % (kur[0]["t"] if kur else "absent"),
            len(kur) == 1 and kur[0]["t"] == KUR_NEXT)
        loop = [r for r in s if r["n"] == T["time-loops"]]
        chk("the unordered list offers entry 189 on a two-tick shelf (%s)"
            % (loop[0]["t"] if loop else "absent"),
            len(loop) == 1 and loop[0]["t"] == LOOP_DEEP[2])
        chk("a friend's thumb is a reason, spelled out (%s)"
            % [r["w"] for r in s],
            any("friend" in r["w"] for r in s))

        # ------------------------------------------ the hold
        chk("the hold is a real button with a name", pg.evaluate(
            "()=>{const e=document.getElementById('rechold');"
            "return e.tagName==='BUTTON' && !e.disabled && "
            "/hold/i.test(e.getAttribute('aria-label'));}"))
        chk("nothing is picked before a hold", picked(pg) is None)

        box = eyebox(pg)
        pg.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        pg.mouse.down()
        pg.wait_for_timeout(300)
        chk("the ring arms while held", pg.evaluate(
            "()=>document.getElementById('rechold').classList.contains('arm')"))
        chk("...and Clubbothy shuts his eye first", pg.evaluate(
            "()=>document.getElementById('receye').__eye.closed"))
        pg.wait_for_timeout(500)          # ~800ms in: past 620ms, near the peak
        peak = scale(pg)
        got = picked(pg)
        chk("the hold lands a pick (%s)" % (got and got["t"]), bool(got))
        chk("...marked as picked just now (%s)" % (got and got["kick"]),
            bool(got) and "picked just now" in got["kick"])
        chk("...carrying its own line of why (%s)" % (got and got["w"]),
            bool(got) and bool(got["w"].strip()))
        chk("...and never one of the three already on screen",
            bool(got) and not any(r["t"] == got["t"] and r["n"] == got["n"]
                                  for r in s))
        chk("the eye pops open to about 1.8x (%.2f)" % peak, peak >= 1.6)
        chk("...and both eyes are open again at the pop", pg.evaluate(
            "()=>!document.getElementById('receye').__eye.closed && "
            "!document.getElementById('clubbothy').__eye.closed"))
        pg.mouse.up()
        pg.wait_for_timeout(650)          # ~1.45s in: still on the way down
        mid = scale(pg)
        chk("...then shrinks slowly rather than snapping back (%.2f)" % mid,
            1.02 < mid < peak)
        pg.wait_for_timeout(700)          # ~2.1s in: the move is over
        rest = scale(pg)
        chk("...and comes to rest at normal size (%.2f)" % rest, rest < 1.05)
        chk("the label beside it never moved", pg.evaluate(
            "()=>{const w=document.getElementById('recwrap');"
            "return Math.abs(w.getBoundingClientRect().width - 28) < 2;}"))

        # ------------------------------------------ re-rolls
        seen_picks = []
        repeat = None
        for _ in range(10):
            hold(pg)
            got = picked(pg)
            if not got:
                break
            key = got["n"] + "|" + got["t"]
            if seen_picks and seen_picks[-1] == key:
                repeat = key
            seen_picks.append(key)
        chk("ten re-rolls, none repeating the pick before it (%d distinct)"
            % len({k for k in seen_picks}), len(seen_picks) == 10 and not repeat)

        # ------------------------------------------ the gate, across the pool
        pool_lists = {k.split("|")[0] for k in seen_picks}
        pool_titles = {k for k in seen_picks}
        chk("no pick ever came from the finished list (%s)" % sorted(pool_lists),
            T["lanterns"] not in pool_lists and T["david-lynch"] not in pool_lists)
        chk("no pick ever came from Kurosawa — its one ready film is on the "
            "shelf already", not any(k.startswith(T["kurosawa"] + "|") for k in pool_titles))
        page = pg.evaluate("()=>document.getElementById('homev').textContent")
        chk("#30 of the ordered run never appears anywhere (%s)" % KUR_LAST,
            KUR_LAST not in page)
        chk("nor does any Kurosawa film past the one that is ready",
            not any(r[2] in page for r in KUR[13:] if len(r[2]) > 6))
        chk("nor a single episode of the list that is finished",
            not any(r[2] in page for r in LANT if r[2] != "Pilot"))

        # a hold that is let go early lands nothing
        before = picked(pg)
        hold(pg, ms=250)
        chk("letting go early lands nothing new",
            (picked(pg) or {}).get("t") == (before or {}).get("t"))

        # the keyboard has to be able to hold it too, or the control is a
        # dead end for anyone not using a pointer
        was = picked(pg)
        pg.focus("#rechold")
        pg.keyboard.down(" ")
        pg.wait_for_timeout(900)
        kb = picked(pg)
        pg.keyboard.up(" ")
        chk("Space held lands a fresh pick (%s -> %s)"
            % (was and was["t"], kb and kb["t"]),
            bool(kb) and bool(was)
            and (kb["n"] + "|" + kb["t"]) != (was["n"] + "|" + was["t"]))
        chk("the hold shows a visible focus ring", pg.evaluate(
            "()=>{const r=document.querySelector('#rechold .ring');"
            "return getComputedStyle(r).borderStyle === 'solid';}"))

        # A static Clubbothy is a bug. The tracking used to be bound to the
        # masthead by id, which would have shipped this second eye frozen —
        # so the shelf's eye has to be caught looking.
        pg.mouse.move(1240, 60)
        pg.wait_for_timeout(220)
        gaze = pg.evaluate(
            "()=>['clubbothy','receye'].map(i=>{const e=document.getElementById(i)"
            ".__eye; return [e.lx, e.ly];})")
        chk("both eyes track the cursor, not just the masthead one (%s)" % gaze,
            all(g[0] or g[1] for g in gaze))
        chk("...and each aims from its own position, not a shared one (%s)"
            % gaze, gaze[0] != gaze[1])
        chk("one shared pointermove drives them, not one per eye", pg.evaluate(
            "()=>EYES.length === document.querySelectorAll('.eye').length"))

        chk("no horizontal overflow at 1280 (%dpx)" % overflow(pg),
            overflow(pg) <= 0)
        chk("nothing broke loudly (%s)" % (noise[:3] if noise else "silent"),
            not noise)
        pg.close()

        # ====================================== friends' thumbs unreadable
        noise.clear()
        pg = newpage(b, with_thumbs=False)
        ready(pg)
        s2 = shelf(pg)
        chk("no friends' thumbs: the shelf still renders three rows (%d)"
            % len(s2), len(s2) == 3)
        chk("no friends' thumbs: every row still explains itself",
            len(s2) == 3 and all(r["w"].strip() for r in s2))
        chk("no friends' thumbs: nothing pretends a friend said anything (%s)"
            % [r["w"] for r in s2],
            not any("friend" in r["w"] for r in s2))
        kur2 = [r for r in s2 if r["n"] == T["kurosawa"]]
        chk("no friends' thumbs: the ordered gate still holds (%s)"
            % (kur2[0]["t"] if kur2 else "absent"),
            len(kur2) == 1 and kur2[0]["t"] == KUR_NEXT)
        chk("no friends' thumbs: a finish is still a reason (%s)"
            % [r["w"] for r in s2],
            any("because you finished" in r["w"] for r in s2))
        chk("no friends' thumbs: the frame still counts three", pg.evaluate(
            "()=>{const q=document.querySelector('#hrechead .quiet');"
            "return !!q && /^3 you could start tonight$/.test("
            "q.textContent.trim());}"))
        hold(pg)
        chk("no friends' thumbs: the hold still lands", bool(picked(pg)))
        chk("no friends' thumbs: nothing broke loudly (%s)"
            % (noise[:3] if noise else "silent"), not noise)
        pg.close()

        # ============================================== signed out: nothing
        noise.clear()
        out = dict(SEED)
        out.pop("gw:acctname")
        pg = newpage(b, signed=False, seed=out)
        ready(pg)
        chk("signed out: home renders from the device's own ticks",
            pg.evaluate("()=>!document.getElementById('homev')"
                        ".classList.contains('hide')"))
        chk("signed out: the shelf header is not on the page", pg.evaluate(
            "()=>document.getElementById('hrec-h').classList.contains('hide')"))
        chk("signed out: not one recommendation is rendered", pg.evaluate(
            "()=>document.querySelectorAll('#hrec .rec, #hrecpick .rec')"
            ".length === 0"))
        chk("signed out: no orphan frame left standing over nothing",
            pg.evaluate("()=>document.getElementById('hrechead')"
                        ".textContent.trim() === ''"))
        chk("signed out: the shelf occupies no space at all", pg.evaluate(
            "()=>{const h=document.getElementById('hrec-h');"
            "return h.getBoundingClientRect().height === 0;}"))
        chk("signed out: Tonight is still there — only the shelf went",
            pg.evaluate("()=>!!document.querySelector('#htonight .tc')"))
        chk("signed out: nothing broke loudly (%s)"
            % (noise[:3] if noise else "silent"), not noise)
        pg.close()

        # ==================================================== the phone
        noise.clear()
        pg = newpage(b, width=390)
        ready(pg)
        s3 = shelf(pg)
        chk("phone: three rows (%d)" % len(s3), len(s3) == 3)
        chk("phone: no horizontal overflow at 390 (%dpx)" % overflow(pg),
            overflow(pg) <= 0)
        hold(pg)
        chk("phone: the hold still lands a pick", bool(picked(pg)))
        chk("phone: still no overflow with a pick on screen (%dpx)"
            % overflow(pg), overflow(pg) <= 0)
        chk("phone: nothing broke loudly (%s)"
            % (noise[:3] if noise else "silent"), not noise)
        pg.close()

        # ======================================== reduced motion, one step
        noise.clear()
        ctx = b.new_context(viewport={"width": 1280, "height": 900},
                            reduced_motion="reduce")
        ctx.route("**/cdn.jsdelivr.net/**", lambda route: route.abort())
        ctx.add_init_script(STUB % (json.dumps(db(True)), json.dumps([]), "true"))
        ctx.add_init_script(
            "(()=>{if(window.__seeded)return;window.__seeded=1;const s="
            + json.dumps(SEED) + ";for(const k in s)localStorage.setItem(k,s[k]);})()")
        pg = wire(ctx.new_page())
        ready(pg)
        chk("reduced motion: the shelf still renders three rows (%d)"
            % len(shelf(pg)), len(shelf(pg)) == 3)
        box = eyebox(pg)
        pg.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        pg.mouse.down()
        pg.wait_for_timeout(800)
        rm = scale(pg)
        chk("reduced motion: the eye still changes size (%.2f)" % rm, rm >= 1.6)
        chk("reduced motion: a pick still lands", bool(picked(pg)))
        pg.mouse.up()
        # the class comes off 1300ms after the pick lands, and under reduced
        # motion that removal IS the whole return trip — one step, no tween
        pg.wait_for_timeout(1500)
        chk("reduced motion: and steps back in one move, not a shrink (%.2f)"
            % scale(pg), scale(pg) < 1.05)
        chk("reduced motion: nothing broke loudly (%s)"
            % (noise[:3] if noise else "silent"), not noise)
        pg.close()
        b.close()
finally:
    srv.terminate()

print("VERDICT:", "clean" if ok else "FAILURES")
