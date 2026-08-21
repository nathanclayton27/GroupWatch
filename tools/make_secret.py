#!/usr/bin/env python3
"""Encrypt a property so the repository does not hold its contents.

    python3 tools/make_secret.py <plaintext.json> <slug> [--hint "..."]

A password gate that only hides a list from the switcher is worth very little
when the list itself sits in properties/<slug>.json for anyone to read. This
takes the real property — title, blurb, notes, everything — and writes a file
that carries none of it: a cover title, a neutral accent, and one AES-GCM
ciphertext. Without the password the file is bytes.

The password is read from the GW_SECRET environment variable rather than a
command-line argument, so it does not end up in a shell history file.

Key derivation is PBKDF2-HMAC-SHA256 at 210,000 iterations, which is what
WebCrypto can do in the browser without a visible pause, and AES-GCM
authenticates as well as encrypts — a wrong password fails to decrypt rather
than producing plausible rubbish, so the gate needs no separate password check.

The plaintext belongs outside the repository. scratch/ is gitignored and is the
right home for it.
"""
import base64
import getpass
import json
import os
import pathlib
import sys

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
except ImportError:
    raise SystemExit("needs `pip install cryptography`")

ITER = 210000
ROOT = pathlib.Path(__file__).resolve().parent.parent


def b64(b):
    return base64.b64encode(b).decode("ascii")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 2:
        raise SystemExit(__doc__.strip().splitlines()[2].strip())
    plain_path, slug = pathlib.Path(args[0]), args[1]
    hint = ""
    if "--hint" in sys.argv:
        hint = sys.argv[sys.argv.index("--hint") + 1]

    password = os.environ.get("GW_SECRET") or getpass.getpass("password: ")
    if not password:
        raise SystemExit("no password given")

    plain = json.loads(plain_path.read_text(encoding="utf-8"))
    for field in ("title", "unit"):
        if not plain.get(field):
            raise SystemExit("the plaintext needs a %s" % field)

    salt, iv = os.urandom(16), os.urandom(12)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER)
    key = kdf.derive(password.encode("utf-8"))
    body = json.dumps(plain, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    blob = AESGCM(key).encrypt(iv, body, None)

    # What ships. Everything here is deliberately dull: this file is public.
    out = {
        "slug": slug,
        "title": "Secret",
        "kind": "",
        "order": plain.get("order", 99),
        "unit": {"one": "entry", "many": "entries"},
        "accent": "#6C7178",
        "accentDark": "#8E9298",
        "tiers": False,
        "secret": {
            "v": 1,
            "kdf": "PBKDF2-HMAC-SHA256",
            "iter": ITER,
            "salt": b64(salt),
            "iv": b64(iv),
            "blob": b64(blob),
            "title": "Secret",
            "hint": hint or "If you know, you know.",
        },
    }

    dest = ROOT / "properties" / ("%s.json" % slug)
    with dest.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(out, indent=2, ensure_ascii=False) + "\n")

    leaks = [w for w in (plain.get("title", ""), plain.get("subtitle", ""))
             if w and w.lower() in json.dumps(out).lower()]
    if leaks:
        raise SystemExit("refusing to write: %r survived into the public file" % leaks)

    print("wrote properties/%s.json — %d bytes of ciphertext, nothing else"
          % (slug, len(blob)))
    print("  plaintext stays at %s (gitignored)" % plain_path)


if __name__ == "__main__":
    main()
