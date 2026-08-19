#!/usr/bin/env python3
"""
linecount.py — non-blank, non-comment lines per src file.

Comment rules: a line whose first non-whitespace is # (Python) or // (C)
is a comment. Blank lines are ignored. I/O modules are listed separately;
they do not count against the crypto line budget.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "src")

CRYPTO = ["birth_pico.py", "sign_pico.py"]
IO = ["io_pico.py"]


def count_lines(path):
    n = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            if s.startswith("#") or s.startswith("//"):
                continue
            n += 1
    return n


def main():
    rows = []
    for name in CRYPTO + IO:
        path = os.path.join(SRC, name)
        if not os.path.exists(path):
            print("missing", name, file=sys.stderr)
            return 1
        rows.append((name, count_lines(path), name in IO))
    print("file                 lines  budget_note")
    print("-" * 48)
    for name, n, is_io in rows:
        note = "I/O (excluded from crypto budget)" if is_io else "crypto"
        print("%-20s %5d  %s" % (name, n, note))
    print("-" * 48)
    crypto_total = sum(n for name, n, is_io in rows if not is_io)
    print("crypto total: %d" % crypto_total)
    # machine-readable for check_docs
    if "--json" in sys.argv:
        import json
        print(json.dumps({name: n for name, n, _ in rows}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
