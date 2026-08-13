#!/usr/bin/env python3
"""
make_card.py — deterministic 6×6 dice card.

No RNG. Stdlib only. Mapping: cell n = (row-1)*6 + (col-1) in 0..35.
n < 32 → that integer as 5 bits. n ≥ 32 → REROLL.

    python3 tools/make_card.py           # print markdown
    python3 tools/make_card.py --write   # write docs/dice-card.md
    python3 tools/make_card.py --check   # regenerate and diff
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "docs", "dice-card.md")


def cell(row, col):
    n = (row - 1) * 6 + (col - 1)
    if n >= 32:
        return "REROLL"
    return format(n, "05b")


def mapping():
    grid = {}
    patterns = []
    rerolls = 0
    for r in range(1, 7):
        for c in range(1, 7):
            v = cell(r, c)
            grid[(r, c)] = v
            if v == "REROLL":
                rerolls += 1
            else:
                patterns.append(v)
    if rerolls != 4:
        raise SystemExit("need 4 REROLL cells, got %d" % rerolls)
    if len(set(patterns)) != 32:
        raise SystemExit("patterns not unique")
    expected = [format(i, "05b") for i in range(32)]
    if sorted(patterns) != expected:
        raise SystemExit("not exactly 00000..11111")
    return grid


def render(grid):
    lines = []
    lines.append("# Dice card — 6×6, one die, two throws")
    lines.append("")
    lines.append("*Print this page. Verify it before the ceremony.*")
    lines.append("")
    lines.append("> **First throw = row. Second throw = column.**")
    lines.append("> Never reverse, never sort.")
    lines.append(">")
    lines.append("> **Verify this card before use — each of the 32")
    lines.append("> patterns must appear exactly once.**")
    lines.append("")
    lines.append("> *Paranoid mode: ignore the columns. Use only")
    lines.append("> whether the first throw is low (1–3 → 0) or high")
    lines.append("> (4–6 → 1). One bit per throw, 256 throws, same")
    lines.append("> card, no extra equipment.*")
    lines.append("")
    lines.append("## Why 36 cells")
    lines.append("")
    lines.append("A lookup table sits inside the cryptographic chain.")
    lines.append("Four altered rows would bias every key generated")
    lines.append("from it, invisibly and unpatchably. A 36-cell card")
    lines.append("is auditable by its own reader in two minutes.")
    lines.append("A 2,187-row or 7,776-row table is not. We chose")
    lines.append("auditability over 18 fewer throws.")
    lines.append("")
    lines.append("Construction (no hidden permutation): number the")
    lines.append("cells 0..35 in row-major order. Cells 0..31 are")
    lines.append("that index as five bits. Cells 32..35 are REROLL.")
    lines.append("Regenerate with `python3 tools/make_card.py --check`.")
    lines.append("")
    lines.append("The 36-cell card is **more** sensitive to per-face")
    lines.append("die bias than `{1,2,3}→0 / {4,5,6}→1`. That is the")
    lines.append("trade: fewer throws, more structure used. Paranoid")
    lines.append("mode is printed above. See HARDCORE.md §2.")
    lines.append("")
    lines.append("## The card")
    lines.append("")
    header = "|     |  1    |  2    |  3    |  4    |  5    |  6    |"
    sep = "|-----|-------|-------|-------|-------|-------|-------|"
    lines.append(header)
    lines.append(sep)
    for r in range(1, 7):
        cells = ["**%d**" % r]
        for c in range(1, 7):
            v = grid[(r, c)]
            cells.append("**REROLL**" if v == "REROLL" else "`%s`" % v)
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")
    lines.append("Rows 1–6 = first throw. Columns 1–6 = second throw.")
    lines.append("")
    lines.append("## Use")
    lines.append("")
    lines.append("Throw once. That is the row. Throw again. That is")
    lines.append("the column. Copy the five bits onto the worksheet")
    lines.append("(`docs/worksheet.md`). REROLL means throw *both*")
    lines.append("throws again, fresh. 52 lookups yield 260 bits;")
    lines.append("keep the first 256. Expected throws ≈ 117 per")
    lines.append("number (11% rejection).")
    lines.append("")
    lines.append("The worksheet, not the die, is what you type into")
    lines.append("the device: worksheet bit 0 → press **1**, bit 1 →")
    lines.append("press **4**.")
    lines.append("")
    return "\n".join(lines) + "\n"


def main(argv):
    grid = mapping()
    text = render(grid)
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
            print("docs/dice-card.md is stale; run make_card.py --write",
                  file=sys.stderr)
            return 1
        print("dice-card.md matches tools/make_card.py")
        return 0
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
