# Handoff

Everything you need to pick this up in VS Code and keep working on it.

---

## The one thing to understand first

**`index.html` is generated. Don't edit it.**

It's built from two files in `src/`, and any hand-edits get wiped the next time you build. The generated file is committed to the repo anyway, because GitHub Pages serves static files and has no build step of its own.

```
src/reading_order.py  →  the reading order (Python)
src/template.html     →  markup, CSS, JavaScript
        ↓  python3 src/build.py
index.html            →  generated, committed, served
```

If you'd rather drop the build step entirely, you can: delete `src/`, edit `index.html` directly, and accept that the 250-item `DATA` array is now hand-maintained. I wouldn't, but it's a legitimate choice for a project this size.

---

## Setup

```bash
git clone https://github.com/YOURNAME/REPO.git
cd REPO
code .
```

No dependencies. No `npm install`, no virtualenv, no package manager. Python 3.8+ is the only requirement and it's for the build script alone — nothing Python ships to the browser.

Verify it works:

```bash
python3 src/build.py
```

Expected:

```
wrote index.html
  14 sections, 250 issues
  tier 1: 130   tier 2: 61   tier 3: 59
  14/14 sections have series links, 38 direct issue links
```

If `git status` shows no changes to `index.html` after that, your tree is in sync.

---

## Running it locally

**Use a local server. Don't open the file directly.**

```bash
python3 -m http.server 8000
# → http://localhost:8000
```

Opening `index.html` from Finder gives you a `file://` URL, and Supabase auth will not work there — the magic-link redirect needs a real origin, and `file://` doesn't have one. The tracker will load and fall back to local storage, which looks like it's working right up until you try to sign in.

To sign in locally, add `http://localhost:8000` to **Authentication → URL Configuration → Redirect URLs** in Supabase. Leave the Site URL pointing at your Pages deployment.

### VS Code tasks

`.vscode/tasks.json` has three, reachable via `Cmd/Ctrl+Shift+P` → *Run Task*:

| Task | What it does |
|---|---|
| **Build index.html** | the default build task — `Cmd/Ctrl+Shift+B` |
| **Serve on localhost:8000** | starts the static server |
| **Build and serve** | both, in order |

The Live Server extension also works, but it watches `index.html` and won't rebuild from source, so you'd still run the build manually. The task is less confusing.

---

## Making changes

### Adding, removing or reordering issues

`src/reading_order.py`. Sections are dicts in the `SECTIONS` list:

```python
{"id": "tro", "tier": 1, "title": "Time Runs Out",
 "sub": "an eight-month jump · the strongest sustained stretch",
 "series": L(("Avengers", S_AV), ("New Avengers", S_NA)),
 "intro": "...",                     # optional prose block
 "items": [av(35, "eight months later", 1), na(24), ...]},
```

Helpers: `av(n)` and `na(n)` for Avengers / New Avengers, `sw(n)` for Secret Wars, `it(title, number, note, star, opt)` for anything else. `L()` builds the series-link list.

Build, refresh, done. Counts, tier totals and the tick strip all recompute.

### ⚠️ Renaming a title breaks saved progress

Item IDs are slugs derived from the title and issue number:

```python
it("Secret Wars: Siege", "#1")   →   secret-wars-siege-1
```

Progress is stored as a list of those IDs. **Reordering and moving items between sections is safe** — the ID travels with the item. **Renaming is not.** Change `"Secret Wars: Siege"` to `"Siege"` and every one of those IDs changes, and anyone who'd ticked them loses those ticks silently.

If you must rename, add an explicit `"id"` to the item to pin the old key:

```python
{"t": "Siege", "n": "#1", "id": "secret-wars-siege-1", ...}
```

The build raises on duplicate IDs, so collisions fail loudly rather than quietly.

### Changing the design

`src/template.html`. CSS variables are in `:root` at the top with a `prefers-color-scheme: dark` override below. The palette is deliberate — mono data columns and hairline rules, after the Rian Hughes infographic pages Hickman's books are known for. Change the four colour variables and the whole thing shifts coherently.

### Changing behaviour

Also `src/template.html`, in the `<script>` block:

| Function | Role |
|---|---|
| `readLocal` / `writeLocal` | localStorage |
| `pushCloud` / `persist` | Supabase writes, debounced 700ms |
| `adopt` / `onSession` | auth and the first-sign-in merge |
| `build` | renders sections and the tick strip, once |
| `paint` | syncs visual state after every change |
| `migrate` | one-shot upgrade from the old positional ID format |

`build()` runs once; `paint()` runs on every tick. Storage is touched only in the first two rows, so swapping backends means changing those and nothing else.

---

## Deploying

```bash
python3 src/build.py
git add -A
git commit -m "..."
git push
```

Pages redeploys in under a minute. **If you forget the build step, nothing changes on the live site** — you pushed source that Pages doesn't read.

Worth adding as a pre-commit hook if you'll be at this a while:

```bash
cat > .git/hooks/pre-commit <<'EOF'
#!/bin/sh
python3 src/build.py && git add index.html
EOF
chmod +x .git/hooks/pre-commit
```

---

## Gotchas

**The `progress.read_ids` column must be `text[]`, not `int[]`.** It was `int[]` in the first version, when IDs were array positions. If you rebuild the database from an old snippet you'll get `400` on every write. The current schema is in `README.md`.

**The anon key in the source is fine.** It's a publishable key; row-level security in Postgres is what protects the data. Removing those RLS policies while leaving RLS disabled would turn that key into a public read-write handle on the table.

**`git diff` on `index.html` is readable** because the build pretty-prints the JSON. If you ever change that to compact output, every rebuild becomes one enormous changed line and code review becomes impossible.

**Sync failures are non-fatal by design.** localStorage is always written first, so a Supabase outage costs you the sync, never the ticks. Errors surface in the status indicator and log to the console with a `[tracker]` prefix.

**Marvel links.** 38 of 250 items link to a specific issue; the rest link to a series. That's not laziness — Marvel renders only the 20 most recent issues of a series server-side, and `?offset`, `?limit` and `?byYear` are all ignored. The remainder can't be enumerated from outside.

---

## Where the reading order came from

Comic Book Herald, Crushing Krisis, How To Love Comics, and comicbookreadingorders.com. The *Fantastic Four*/*FF* weave follows the order Hickman gave for the omnibus. The *Secret Wars* interleave — Thors and Siege slotted between the main issues rather than read afterwards — follows the alternate order documented at comicbookreadingorders.com.

Tier assignments and the annotations are editorial judgement, not sourced fact. Disagree freely; they're one dict away from changing.
