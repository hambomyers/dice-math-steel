#!/usr/bin/env python3
"""
make_words_table.py — 11-bit pattern ↔ word table from english.txt.

No RNG. Stdlib only. The list is a reading aid, not entropy.

    python3 tools/make_words_table.py --write
    python3 tools/make_words_table.py --check
    python3 tools/make_words_table.py --self-test
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WORDLIST = os.path.join(ROOT, "english.txt")
OUT = os.path.join(ROOT, "docs", "words-table.md")

MARKER = "steel"


def load_words():
    words = [w.strip() for w in open(WORDLIST, encoding="utf-8") if w.strip()]
    if len(words) != 2048:
        raise SystemExit("english.txt must have 2048 words, got %d" % len(words))
    if len(set(words)) != 2048:
        raise SystemExit("english.txt has duplicates")
    if words != sorted(words):
        raise SystemExit("english.txt is not alphabetical")
    pref = [w[:4] for w in words]
    if len(set(pref)) != 2048:
        raise SystemExit("first four letters are not unique")
    if MARKER not in words:
        raise SystemExit("marker %r missing from english.txt" % MARKER)
    return words


def render(words):
    lines = []
    lines.append("# KEY READING table — 11-bit pattern ↔ word")
    lines.append("")
    lines.append("Generated from `english.txt`. Do not edit by hand.")
    lines.append("`python3 tools/make_words_table.py --check`")
    lines.append("")
    lines.append("Match the row. Do not compute an index.")
    lines.append("")
    lines.append("```")
    for i, w in enumerate(words):
        lines.append("%s  %s" % (format(i, "011b"), w))
    lines.append("```")
    lines.append("")
    return "\n".join(lines) + "\n"


def bits_of(k):
    return format(k, "0256b")


def encode(k, words):
    if k < 0 or k >= (1 << 256):
        raise ValueError("need a 256-bit integer")
    b = bits_of(k)
    out = [MARKER]
    for i in range(23):
        chunk = b[i * 11:(i + 1) * 11]
        out.append(words[int(chunk, 2)])
    leftover = b[253:256]
    out.append(words[int("00000000" + leftover, 2)])
    if len(out) != 25:
        raise ValueError("need 25 words")
    return out


def decode(word_row, words):
    if len(word_row) != 25:
        raise ValueError("KEY READING is 25 words, got %d" % len(word_row))
    if word_row[0] != MARKER:
        raise ValueError("word 1 must be %r (KEY READING marker)" % MARKER)
    index = {w: i for i, w in enumerate(words)}
    bits = []
    for w in word_row[1:24]:
        if w not in index:
            raise ValueError("unknown word %r" % w)
        bits.append(format(index[w], "011b"))
    last = word_row[24]
    if last not in index:
        raise ValueError("unknown word %r" % last)
    pad = format(index[last], "011b")
    if pad[:8] != "00000000":
        raise ValueError("leftover word is not a 3-bit leftover")
    bits.append(pad[8:])
    b = "".join(bits)
    if len(b) != 256:
        raise ValueError("decoded %d bits" % len(b))
    return int(b, 2)


def self_test(words):
    for k in (1, (1 << 255) + 7, (1 << 256) - 1):
        row = encode(k, words)
        if len(row) != 25:
            raise SystemExit("self-test: not 25")
        if row[0] != MARKER:
            raise SystemExit("self-test: marker")
        got = decode(row, words)
        if got != k:
            raise SystemExit("self-test: round-trip failed for k=%d" % k)
    print("self-test ok: 25 words, marker %r, 256-bit round-trip" % MARKER)
    return 0


def main(argv):
    words = load_words()
    if "--self-test" in argv:
        return self_test(words)
    text = render(words)
    if "--write" in argv:
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        with open(OUT, "w", encoding="utf-8") as f:
            f.write(text)
        print("wrote", os.path.relpath(OUT, ROOT))
        return 0
    if "--check" in argv:
        with open(OUT, encoding="utf-8") as f:
            on_disk = f.read()
        if on_disk != text:
            print("docs/words-table.md is stale; run --write", file=sys.stderr)
            return 1
        print("words-table.md matches english.txt")
        return 0
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
