# Worksheet — 16×16, three grids

Print this page. It is the jig. **Never align steel to steel.**

Ceremony ID (4 chars, same on both plates): ` _ _ _ _ `

Notch sits bottom-left on every plate. A 180° rotation is silent
and catastrophic.

> Mapping is chosen **before the first throw** (PROTOCOL.md
> Phase 2). Do not switch mid-number.
>
> **Standard:** first throw = row, second = column. Copy five bits
> at a time from the card onto GRID 3 (key), then GRID 1 (mask).
> **Paranoid:** ignore columns. One throw, one cell: 1–3 → 0,
> 4–6 → 1. 256 throws per grid. Same worksheet.
>
> Same-or-different fills GRID 2.

Keypad (the worksheet feeds the device, not the die):
**bit 0 → press 1. bit 1 → press 4.**

Burn this sheet after steel re-derives the stamped address.

---

## GRID 1 — PLATE A / the mask

```
        0  1  2  3   4  5  6  7   8  9  A  B   C  D  E  F
      ┌────────────┬────────────┬────────────┬────────────┐
   0  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
   1  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
   2  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
   3  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
      ├────────────┼────────────┼────────────┼────────────┤
   4  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
   5  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
   6  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
   7  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
      ├────────────┼────────────┼────────────┼────────────┤
   8  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
   9  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
   A  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
   B  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
      ├────────────┼────────────┼────────────┼────────────┤
   C  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
   D  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
   E  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
   F  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
      └────────────┴────────────┴────────────┴────────────┘
        ⌐ notch bottom-left
```

## GRID 2 — PLATE B / key ⊕ mask

Stamp the receive address and **ADDRESS FINGERPRINT** (four words)
on plate B. Those words are a public checksum of the address.
They are not the key.

```
        0  1  2  3   4  5  6  7   8  9  A  B   C  D  E  F
      ┌────────────┬────────────┬────────────┬────────────┐
   0  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
   1  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
   2  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
   3  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
      ├────────────┼────────────┼────────────┼────────────┤
   4  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
   5  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
   6  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
   7  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
      ├────────────┼────────────┼────────────┼────────────┤
   8  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
   9  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
   A  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
   B  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
      ├────────────┼────────────┼────────────┼────────────┤
   C  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
   D  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
   E  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
   F  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
      └────────────┴────────────┴────────────┴────────────┘
        ⌐ notch bottom-left
```

ADDRESS FINGERPRINT (four words, public): `_ _ _ _`

## GRID 3 — KEY (author from the card; recover as same-or-different)

Same → 0. Different → 1. Read one row at a time through an index
card with a slot cut in it.

```
        0  1  2  3   4  5  6  7   8  9  A  B   C  D  E  F
      ┌────────────┬────────────┬────────────┬────────────┐
   0  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
   1  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
   2  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
   3  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
      ├────────────┼────────────┼────────────┼────────────┤
   4  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
   5  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
   6  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
   7  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
      ├────────────┼────────────┼────────────┼────────────┤
   8  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
   9  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
   A  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
   B  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
      ├────────────┼────────────┼────────────┼────────────┤
   C  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
   D  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
   E  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
   F  │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │ _  _  _  _ │
      └────────────┴────────────┴────────────┴────────────┘
```

Do not write KEY READING words here. That optional appendix is a
different word-group: it *is* the key in plaintext. This sheet's
four words, if any, are only the ADDRESS FINGERPRINT.
