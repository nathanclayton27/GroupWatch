"""Friend privacy toggles (CLU-118) — the switches, and where they are enforced.

  * master off      a friend sees your name and no shelves at all
  * per list        one list leaves a friend's view, the rest stay
  * clubs           a hidden list's club stack still shows every layer
  * reload          both kinds of switch come back from the server, not a cache
  * pre-migration   with the columns and RPCs absent, nothing is drawn, nothing
                    throws, and the friends page renders exactly as before
  * failed write    a switch that could not save reverts and says so

The Supabase stub is filterable the way fw_group_check.py's is, plus two
things this test needs and no earlier one did:

  1. progress SELECT goes through a transcription of the real RLS rules —
     "read own" OR "read group progress" OR "mutual friends read progress",
     the last one carrying the new owner's-profile check. Permissive policies
     OR together in PostgreSQL, which is precisely why the club branch cannot
     be narrowed by a change to the friends branch.
  2. a POLICY switch that lifts only the third branch. That is the negative
     control, and it is the whole proof of WHERE the hiding happens: with the
     policy lifted and src/template.html untouched, the hidden list comes
     straight back. Nothing in the page filters it — so nothing in the page
     could be talked out of filtering it.

The privacy columns live in PRIVDB rather than on the stub's profiles rows,
mirroring the column grant in the migration: a table read cannot see them, and
the three RPCs are the only way in.
"""
import json
import subprocess
import sys
import time

from playwright.sync_api import sync_playwright

# --- serving the site under test -------------------------------------------
# `srv.poll()` CANNOT detect a busy port here: http.server sets
# allow_reuse_address and Windows SO_REUSEADDR lets a second process bind a
# port another is already serving, so the child comes up healthy and the check
# silently tests whatever the OTHER server is pointed at. That happened — a
# mutation harness on the same port fed a different build to a check for forty
# assertions. Ask TCP instead, then make the server prove it is ours.
def _answering(port):
    import socket
    try:
        with socket.create_connection(("127.0.0.1", port), 0.35):
            return True
    except OSError:
        return False


def _serve(root, start, tries=12):
    import pathlib as _pl, subprocess as _sp, sys as _sys, time as _t
    import urllib.request as _u
    want = (_pl.Path(root) / "index.html").read_bytes()
    for port in range(start, start + tries):
        if _answering(port):
            continue
        proc = _sp.Popen([_sys.executable, "-m", "http.server", str(port)],
                         cwd=root, stdout=_sp.DEVNULL, stderr=_sp.DEVNULL)
        _t.sleep(1.2)
        try:
            got = _u.urlopen("http://localhost:%d/index.html" % port,
                             timeout=5).read()
        except Exception:
            got = None
        if got == want:
            if port != start:
                print("note: port %d was busy, serving on %d" % (start, port))
            return proc, port
        proc.terminate()          # someone else is serving a DIFFERENT build
    raise SystemExit(
        "PORT BUSY: %d..%d are taken or serving another build. This check "
        "would have tested a page nobody meant to test."
        % (start, start + tries - 1))


PORT = 8151
srv, PORT = _serve(".", PORT)   # this check served from cwd

BASE = "http://localhost:%d/" % PORT

MAN = json.load(open("properties/index.json", encoding="utf-8"))
OPEN_SLUGS = [m["slug"] for m in MAN if not m.get("secret")]
LIST = "columbo"                       # the club list, and the one bo hides
assert LIST in OPEN_SLUGS, "columbo is gone from the manifest"
OTHER = [s for s in OPEN_SLUGS if s != LIST][:2]

IX = json.load(open("properties/search.json", encoding="utf-8"))
IDS = [r[1] for r in IX["rows"] if r[0] == LIST]
MINE, THEIRS = IDS[:10], IDS[:5]


def title(slug):
    return [m["title"] for m in MAN if m["slug"] == slug][0]


NAMES = {"f1": "ada", "f2": "bo", "f3": "cy", "f4": "dot"}
FRIENDS = list(NAMES)

DB = {
    "friendships": [e for f in FRIENDS
                    for e in ({"a": "u1", "b": f}, {"a": f, "b": "u1"})],
    "profiles": [{"user_id": "u1", "username": "exx", "fcode": "CLB·AAAA"}]
                + [{"user_id": k, "username": v, "fcode": "CLB·" + k.upper()}
                   for k, v in NAMES.items()],
    "groups": [{"id": "g1", "name": "testers", "property_id": LIST,
                "code": "AAAAAA"}],
    # dot and I share a club for the very list we have both hidden from
    # friends — which is the case worth watching
    "group_members": [
        {"group_id": "g1", "user_id": "u1", "display_name": "exx",
         "color_index": 0},
        {"group_id": "g1", "user_id": "f4", "display_name": "dot",
         "color_index": 1},
    ],
    "progress": [
        {"user_id": "u1", "property_id": LIST, "read_ids": MINE,
         "updated_at": "2026-08-20T10:00:00Z"},
        # ada: three lists, and the master switch off
        {"user_id": "f1", "property_id": LIST, "read_ids": THEIRS},
        {"user_id": "f1", "property_id": OTHER[0], "read_ids": ["a1", "a2"]},
        {"user_id": "f1", "property_id": OTHER[1], "read_ids": ["a3"]},
        # bo: three lists, one hidden, no club anywhere near her
        {"user_id": "f2", "property_id": LIST, "read_ids": THEIRS},
        {"user_id": "f2", "property_id": OTHER[0], "read_ids": ["b1", "b2"]},
        {"user_id": "f2", "property_id": OTHER[1], "read_ids": ["b3"]},
        # cy: nothing set, so nothing changes for her — the control
        {"user_id": "f3", "property_id": LIST, "read_ids": THEIRS},
        {"user_id": "f3", "property_id": OTHER[0], "read_ids": ["c1"]},
        # dot: hides the club list, and is in the club for it
        {"user_id": "f4", "property_id": LIST, "read_ids": IDS[:7],
         "updated_at": "2026-08-20T10:00:00Z"},
        {"user_id": "f4", "property_id": OTHER[1], "read_ids": ["d1"]},
    ],
}

# what each person's profile holds, seen only through the RPCs
PRIVDB = {
    "f1": {"share_progress": False},
    "f2": {"hidden_slugs": [LIST]},
    "f4": {"hidden_slugs": [LIST]},
}

STUB = """
window.supabase = { createClient: () => {
  const DB = %(db)s, PRIVDB = %(priv)s;
  const RPCOK = %(rpcok)s, POLICY = %(policy)s, WRITEFAIL = %(writefail)s;
  const ME = 'u1', PK = '__priv', MK = '__meta';
  const DEF = { share_progress: true, share_activity: true, hidden_slugs: [] };
  const readMine = () => {
    let stored = null;
    try{ stored = JSON.parse(localStorage.getItem(PK) || 'null'); }catch(e){}
    return Object.assign({}, DEF, PRIVDB[ME] || {}, stored || {});
  };
  const writeMine = (o) => {
    try{ localStorage.setItem(PK, JSON.stringify(o)); }catch(e){}
  };
  const settingsOf = (id) => id === ME ? readMine()
    : Object.assign({}, DEF, PRIVDB[id] || {});
  const mutual = (id) =>
    (DB.friendships || []).some(e => e.a === ME && e.b === id) &&
    (DB.friendships || []).some(e => e.a === id && e.b === ME);
  const clubmate = (id, prop) => {
    const mine = (DB.group_members || [])
      .filter(m => m.user_id === ME).map(m => m.group_id);
    return (DB.group_members || []).some(m => m.user_id === id &&
      mine.indexOf(m.group_id) >= 0 &&
      (DB.groups || []).some(g => g.id === m.group_id && g.property_id === prop));
  };
  // The three permissive SELECT policies on progress, OR'd exactly as
  // PostgreSQL ORs them. Only the third one knows about privacy.
  const mayRead = (r) => {
    if(r.user_id === ME) return true;                    // "read own"
    if(clubmate(r.user_id, r.property_id)) return true;  // "read group progress"
    if(!mutual(r.user_id)) return false;
    if(!POLICY) return true;              // the pre-CLU-118 friends policy
    const s = settingsOf(r.user_id);
    if(s.share_progress === false) return false;
    return (s.hidden_slugs || [])
      .indexOf(String(r.property_id).split('#')[0]) < 0;
  };
  const readMeta = () => {
    try{ return JSON.parse(localStorage.getItem(MK) || '{}'); }catch(e){ return {}; }
  };
  const mkUser = () => ({
    id: ME, email: 'exx@example.com',
    created_at: '2026-03-04T10:00:00Z',
    identities: [{ provider: 'email', identity_data: { email: 'exx@example.com' } }],
    user_metadata: Object.assign(
      { username: 'exx', fcode: 'CLB\\u00b7AAAA' }, readMeta())
  });
  // Per-club sessions (CLU-389) read `club_progress`, and today's database
  // does not have it. A stub that answers every table name it is handed would
  // put the page into a club session the live site cannot enter, and this file
  // would be asserting against a database that does not exist. Say what
  // Postgres says. Declaring a club_progress key in DB models the other side.
  const NOCLUBTABLE = () => {
    const gone = {
      select(){ return gone; }, eq(){ return gone; }, in(){ return gone; },
      order(){ return gone; }, limit(){ return gone; },
      maybeSingle(){ return gone; }, single(){ return gone; },
      then(res, rej){ return Promise.resolve({ data: null, error: {
        code: '42P01',
        message: 'relation "public.club_progress" does not exist' } })
        .then(res, rej); }
    };
    return gone;
  };
  const ABSENT = (t) => {
    const gone = {
      select(){ return gone; }, eq(){ return gone; }, in(){ return gone; },
      order(){ return gone; }, limit(){ return gone; }, gte(){ return gone; },
      lte(){ return gone; }, gt(){ return gone; }, not(){ return gone; },
      or(){ return gone; }, neq(){ return gone; }, filter(){ return gone; },
      upsert(){ return gone; }, insert(){ return gone; },
      update(){ return gone; }, delete(){ return gone; },
      maybeSingle(){ return gone; }, single(){ return gone; },
      then(res, rej){ return Promise.resolve({ data: null, error: {
        code: '42P01',
        message: 'relation "public.' + t + '" does not exist' } })
        .then(res, rej); }
    };
    return gone;
  };
  const from = (t) => {
    if(t === 'club_progress' && !DB[t]) return NOCLUBTABLE();
    // A stub answers ONLY the tables its fixture defines. Anything else is
    // 42P01 — what a real database says about a table that is not there.
    // Returning [] instead made "absent" look like "present and empty", and
    // an entire absence path was once verified against a database nobody
    // has. A typo'd table name now fails loudly too.
    if(!(t in DB)) return ABSENT(t);
    let rows = (DB[t] || []).map(r => Object.assign({}, r));
    let single = false;
    const api = {
      select(){ return api; }, order(){ return api; }, limit(){ return api; },
      gte(){ return api; }, lte(){ return api; }, gt(){ return api; },
      not(){ return api; }, or(){ return api; }, neq(){ return api; },
      upsert(){ rows = []; return api; },
      insert(){ rows = []; return api; },
      update(){ rows = []; return api; },
      delete(){ rows = []; return api; },
      eq(k, v){ rows = rows.filter(r => r[k] === v); return api; },
      in(k, vs){ rows = rows.filter(r => vs.indexOf(r[k]) >= 0); return api; },
      maybeSingle(){ single = true; return api; },
      single(){ single = true; return api; },
      then(res, rej){
        const out = t === 'progress' ? rows.filter(mayRead) : rows;
        return Promise.resolve(
          { data: single ? (out[0] || null) : out, error: null }).then(res, rej);
      }
    };
    return api;
  };
  const rpc = async (name, args) => {
    if(!RPCOK) return { data: null, error: { code: 'PGRST202',
      message: 'Could not find the function public.' + name } };
    if(name === 'privacy_settings') return { data: readMine(), error: null };
    if(name !== 'set_privacy' && name !== 'set_list_hidden')
      return { data: null, error: null };
    if(WRITEFAIL) return { data: null,
      error: { code: '42501', message: 'permission denied for table profiles' } };
    const cur = readMine(), a = args || {};
    if(name === 'set_privacy'){
      if(a.p_share === true || a.p_share === false) cur.share_progress = a.p_share;
      if(a.p_activity === true || a.p_activity === false)
        cur.share_activity = a.p_activity;
    }else{
      const h = cur.hidden_slugs.slice(), i = h.indexOf(a.p_slug);
      if(a.p_hidden){ if(i < 0) h.push(a.p_slug); }
      else if(i >= 0) h.splice(i, 1);
      cur.hidden_slugs = h;
    }
    writeMine(cur);
    return { data: cur, error: null };
  };
  return {
    auth: {
      onAuthStateChange: (cb) => { setTimeout(() =>
        cb('SIGNED_IN', { user: mkUser() }), 30); return {}; },
      getSession: async () => ({ data: { session: { user: mkUser() } } }),
      getUser:    async () => ({ data: { user: mkUser() } }),
      updateUser: async (p) => {
        const m = Object.assign(readMeta(), (p && p.data) || {});
        try{ localStorage.setItem(MK, JSON.stringify(m)); }catch(e){}
        return { data: { user: mkUser() }, error: null };
      },
      signOut: async () => ({}),
      signInWithOtp: async () => ({}), signInWithOAuth: async () => ({})
    },
    from, rpc
  };
}};
"""

SEED = {
    "gw:last": LIST,
    "gw:v1:" + LIST: json.dumps(MINE),
    "gw:merged:u1:" + LIST: "1",
    "gw:syncback:off": "1",
    "gw:acctname": "exx",
    "gw:group:" + LIST: "g1",
}

ok = True
errors = []


def chk(name, cond):
    global ok
    print(("PASS " if cond else "FAIL ") + name)
    ok = ok and bool(cond)


def stub(rpcok=True, policy=True, writefail=False):
    return STUB % {"db": json.dumps(DB), "priv": json.dumps(PRIVDB),
                   "rpcok": "true" if rpcok else "false",
                   "policy": "true" if policy else "false",
                   "writefail": "true" if writefail else "false"}


def newpage(b, js, seed=None, priv=None):
    ctx = b.new_context(viewport={"width": 1280, "height": 900})
    ctx.route("**/cdn.jsdelivr.net/**", lambda route: route.abort())
    ctx.add_init_script(js)
    s = dict(SEED)
    s.update(seed or {})
    if priv is not None:
        s["__priv"] = json.dumps(priv)
    # the flag lives in localStorage, not on window: "survives a reload" is the
    # claim under test, and a per-document guard would re-seed the settings on
    # every reload and fake every pass
    ctx.add_init_script(
        "(()=>{try{if(localStorage.getItem('__seeded'))return;const s="
        + json.dumps(s) + ";for(const k in s)localStorage.setItem(k,s[k]);"
        "localStorage.setItem('__seeded','1');}catch(e){}})()")
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errors.append(str(e)))
    return pg


# Every friend card with the titles its shelf is showing
CARDS = """()=>[...document.querySelectorAll('#fp-list .acard')].map(c=>({
  name: ((c.querySelector('.afrow > b')||{}).textContent||'').trim(),
  lists: [...c.querySelectorAll('.mline')].map(m=> m.children[1].textContent)
}))"""


def cards(pg):
    return {c["name"]: c["lists"] for c in pg.evaluate(CARDS)}


def priv(pg):
    return pg.evaluate("()=>JSON.parse(localStorage.getItem('__priv')||'{}')")


try:
    with sync_playwright() as p:
        b = p.chromium.launch()

        # =============================================== the enforced world
        pg = newpage(b, stub(), priv={"hidden_slugs": [LIST]})
        pg.goto(BASE + "?p=" + LIST)
        pg.wait_for_timeout(2400)

        # ---- the list page's own switch
        chk("the list page carries the switch",
            pg.locator("#privpanel").is_visible())
        chk("it is a real checkbox, keyboard reachable", pg.evaluate(
            "()=>{const b=document.getElementById('p-hide');"
            "b.focus(); return b.tagName==='INPUT' && b.type==='checkbox' &&"
            " document.activeElement===b;}"))
        chk("its label is wired to it", pg.evaluate(
            "()=>{const l=document.querySelector(\"label[for='p-hide']\");"
            "return !!l && l.textContent.indexOf('Hide this list')>=0;}"))
        chk("it opens already on for a list I had hidden",
            pg.locator("#p-hide").is_checked())

        # ---- the club stack: untouched by anybody's hiding
        legend = pg.locator(".gitem").all_inner_texts()
        mine = [t for t in legend if "exx" in t]
        theirs = [t for t in legend if "dot" in t]
        chk("the club renders both layers (%d)" % len(legend), len(legend) == 2)
        chk("my layer still counts 10 on a list I hid (%s)"
            % (mine[0].replace("\n", " ") if mine else "missing"),
            bool(mine) and "(10)" in mine[0])
        chk("dot's layer still counts 7 on a list SHE hid (%s)"
            % (theirs[0].replace("\n", " ") if theirs else "missing"),
            bool(theirs) and "(7)" in theirs[0])

        # ---- unhide from the list page, and make it stick
        pg.click("#p-hide")
        pg.wait_for_timeout(500)
        chk("unhiding writes through to the server",
            priv(pg).get("hidden_slugs") == [])
        chk("and says so", "shows to friends again"
            in pg.locator("#privmsg").inner_text())
        pg.reload()
        pg.wait_for_timeout(2400)
        chk("unhidden survives a reload", not pg.locator("#p-hide").is_checked())
        pg.click("#p-hide")
        pg.wait_for_timeout(500)
        chk("re-hiding writes through", priv(pg).get("hidden_slugs") == [LIST])
        pg.reload()
        pg.wait_for_timeout(2400)
        chk("hidden survives a reload", pg.locator("#p-hide").is_checked())
        chk("the club stack is still whole after all that",
            len(pg.locator(".gitem").all_inner_texts()) == 2)

        # ---- the friends page: what the policy actually hands over
        pg.goto(BASE + "?friends")
        pg.wait_for_selector("#fp-list .acard", timeout=8000)
        pg.wait_for_timeout(900)
        c = cards(pg)
        chk("every friend is still a friend (%s)" % ",".join(sorted(c)),
            set(c) == {"ada", "bo", "cy", "dot"})
        chk("ada's master switch is off: name, no shelves (%d rows)"
            % len(c.get("ada", [])), c.get("ada") == [])
        chk("bo keeps her other lists (%s)" % ",".join(c.get("bo", [])),
            sorted(c.get("bo", [])) == sorted(title(s) for s in OTHER))
        chk("bo's hidden list is gone from her shelf",
            title(LIST) not in c.get("bo", []))
        chk("cy, who set nothing, is unchanged (%s)" % ",".join(c.get("cy", [])),
            sorted(c.get("cy", [])) == sorted([title(LIST), title(OTHER[0])]))
        # Deliberate, and the one place a reader might cry leak: dot hid this
        # list from friends, but she and I are in a club for it. The club is a
        # separate grant she made herself, so the row is still hers to me. If
        # this ever starts failing, something has leaked into the club path.
        chk("a club-mate's hidden list stays readable through the club (%s)"
            % ",".join(c.get("dot", [])),
            sorted(c.get("dot", [])) == sorted([title(LIST), title(OTHER[1])]))

        # ---- the account page: the switches and the list of what is hidden
        pg.goto(BASE + "?account")
        pg.wait_for_selector("#a-privcard", timeout=8000)
        pg.wait_for_timeout(700)
        chk("the account page carries the card",
            pg.locator("#a-privcard").is_visible())
        chk("the master switch reads on", pg.locator("#a-share").is_checked())
        chk("the hidden list is named where it can be found (%s)"
            % pg.locator("#a-hidden").inner_text().replace("\n", " "),
            title(LIST) in pg.locator("#a-hidden").inner_text())
        chk("the card reuses the account's switch, not a second one", pg.evaluate(
            "()=>{const a=getComputedStyle(document.getElementById('a-spoil'));"
            "const b=getComputedStyle(document.getElementById('a-share'));"
            "return a.width===b.width && a.height===b.height &&"
            " a.borderRadius===b.borderRadius;}"))
        pg.click("#a-hidden button[data-unhide]")
        pg.wait_for_timeout(500)
        chk("show again empties the set", priv(pg).get("hidden_slugs") == [])
        chk("and the card says nothing is hidden", "nothing hidden"
            in pg.locator("#a-hidden").inner_text())
        pg.click("#a-share")
        pg.wait_for_timeout(500)
        chk("the master switch writes through",
            priv(pg).get("share_progress") is False)
        chk("the ticks switch goes dead under it, rather than lying",
            pg.locator("#a-showticks").is_disabled())
        pg.reload()
        pg.wait_for_selector("#a-privcard", timeout=8000)
        pg.wait_for_timeout(700)
        chk("the master switch survives a reload",
            not pg.locator("#a-share").is_checked())
        chk("and the ticks switch is still held down",
            pg.locator("#a-showticks").is_disabled())
        pg.click("#a-share")
        pg.wait_for_timeout(500)
        chk("turning it back on frees the ticks switch",
            pg.locator("#a-share").is_checked()
            and not pg.locator("#a-showticks").is_disabled())
        pg.click("#a-showticks")
        pg.wait_for_timeout(500)
        chk("the ticks switch writes its own answer",
            priv(pg).get("share_activity") is False)
        pg.reload()
        pg.wait_for_selector("#a-privcard", timeout=8000)
        pg.wait_for_timeout(700)
        chk("and it survives a reload too",
            not pg.locator("#a-showticks").is_checked())
        chk("no console errors anywhere in the enforced world (%s)"
            % (errors[:1] or "none"), not errors)
        pg.close()

        # ====================== the negative control: WHERE the hiding happens
        # Same page, same build, same friends — only the policy's third branch
        # is lifted. If the browser were doing the hiding, this would look the
        # same. It does not, so the browser is not.
        del errors[:]
        pg = newpage(b, stub(policy=False))
        pg.goto(BASE + "?friends")
        pg.wait_for_selector("#fp-list .acard", timeout=8000)
        pg.wait_for_timeout(900)
        c = cards(pg)
        chk("policy lifted: ada's shelves come straight back (%d)"
            % len(c.get("ada", [])), len(c.get("ada", [])) == 3)
        chk("policy lifted: bo's hidden list comes back too",
            title(LIST) in c.get("bo", []))
        chk("policy lifted: so the page never did the hiding",
            len(c.get("bo", [])) == 3)
        pg.close()

        # ======================================= before the migration is run
        del errors[:]
        pg = newpage(b, stub(rpcok=False, policy=False))
        pg.goto(BASE + "?p=" + LIST)
        pg.wait_for_timeout(2400)
        chk("no columns: the list page draws no switch",
            not pg.locator("#privpanel").is_visible())
        chk("no columns: the club still renders",
            len(pg.locator(".gitem").all_inner_texts()) == 2)
        pg.goto(BASE + "?account")
        pg.wait_for_selector("#a-fcode", timeout=8000)
        pg.wait_for_timeout(900)
        chk("no columns: the account page draws no card",
            not pg.locator("#a-privcard").is_visible())
        chk("no columns: the rest of the account page is fine",
            "exx" in pg.locator("#a-who").inner_text()
            and pg.locator("#a-user").input_value() == "exx")
        pg.goto(BASE + "?friends")
        pg.wait_for_selector("#fp-list .acard", timeout=8000)
        pg.wait_for_timeout(900)
        c = cards(pg)
        chk("no columns: friends and shelves render as they did (%s)"
            % ",".join(sorted(c)), set(c) == {"ada", "bo", "cy", "dot"}
            and len(c["ada"]) == 3 and len(c["bo"]) == 3)
        chk("no columns: nothing threw (%s)" % (errors[:1] or "none"), not errors)
        pg.close()

        # ========================================= a write that cannot land
        del errors[:]
        pg = newpage(b, stub(writefail=True))
        pg.goto(BASE + "?p=" + LIST)
        pg.wait_for_timeout(2400)
        chk("failed write: the switch is there to try",
            pg.locator("#privpanel").is_visible()
            and not pg.locator("#p-hide").is_checked())
        pg.click("#p-hide")
        pg.wait_for_timeout(600)
        chk("failed write: the switch does not paint as if it landed",
            not pg.locator("#p-hide").is_checked())
        chk("failed write: the page says so (%s)"
            % pg.locator("#privmsg").inner_text(),
            "did not save" in pg.locator("#privmsg").inner_text())
        chk("failed write: nothing was stored either", priv(pg) == {})
        pg.close()
        b.close()
finally:
    srv.terminate()

print("VERDICT:", "clean" if ok else "FAILURES")
