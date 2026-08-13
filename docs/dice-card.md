# Dice card — 6×6, one die, two throws

*Print this page. Verify it before the ceremony.*

> **First throw = row. Second throw = column.**
> Never reverse, never sort.
>
> **Verify this card before use — each of the 32
> patterns must appear exactly once.**

> *Paranoid mode: ignore the columns. Use only
> whether the first throw is low (1–3 → 0) or high
> (4–6 → 1). One bit per throw, 256 throws, same
> card, no extra equipment.*

## Why 36 cells

A lookup table sits inside the cryptographic chain.
Four altered rows would bias every key generated
from it, invisibly and unpatchably. A 36-cell card
is auditable by its own reader in two minutes.
A 2,187-row or 7,776-row table is not. We chose
auditability over 18 fewer throws. (Diceware — Arnold
Reinhold, 1995 — is prior art for dice-to-word lookup.
Those tables are thousands of rows. We cite the idea
and reject the size.)

Construction (no hidden permutation): number the
cells 0..35 in row-major order. Cells 0..31 are
that index as five bits. Cells 32..35 are REROLL.
Regenerate with `python3 tools/make_card.py --check`.

The 36-cell card is **more** sensitive to per-face
die bias than `{1,2,3}→0 / {4,5,6}→1`. That is the
trade: fewer throws, more structure used. Paranoid
mode is printed above. See HARDCORE.md §2.

## The card

|     |  1    |  2    |  3    |  4    |  5    |  6    |
|-----|-------|-------|-------|-------|-------|-------|
| **1** | `00000` | `00001` | `00010` | `00011` | `00100` | `00101` |
| **2** | `00110` | `00111` | `01000` | `01001` | `01010` | `01011` |
| **3** | `01100` | `01101` | `01110` | `01111` | `10000` | `10001` |
| **4** | `10010` | `10011` | `10100` | `10101` | `10110` | `10111` |
| **5** | `11000` | `11001` | `11010` | `11011` | `11100` | `11101` |
| **6** | `11110` | `11111` | **REROLL** | **REROLL** | **REROLL** | **REROLL** |

Rows 1–6 = first throw. Columns 1–6 = second throw.

## Use

Throw once. That is the row. Throw again. That is
the column. Copy the five bits onto the worksheet
(`docs/worksheet.md`). REROLL means throw *both*
throws again, fresh. 52 lookups yield 260 bits;
keep the first 256. Expected throws ≈ 117 per
number (11% rejection).

The worksheet, not the die, is what you type into
the device: worksheet bit 0 → press **1**, bit 1 →
press **4**.

