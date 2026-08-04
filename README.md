A ground-up minimal rewrite is underway on the v0.5-minimal branch;
v0.3.4 remains the reviewed reference until v0.5 code ships.

# Dice Math Steel

**Nothing believed. Everything agreed.**

*Dice, steel, and two strangers who must agree.*

*Cold storage with no trusted devices. A rough draft posted to be
attacked, corrected, and improved — in reply to July 30, 2026, the
day the most trusted hardware wallet in Bitcoin cost its users ~$38M
because its firmware silently generated weak randomness for five
years.*

> ⚠️ **EXPERIMENTAL — UNREVIEWED — DO NOT USE WITH REAL FUNDS.**
> Signet or throwaway amounts only until strangers smarter than us
> have broken and repaired this. That's not a disclaimer, it's the
> development model.

> **STATUS (pre-hardware):** All math passes the official BIP340/
> BIP341/BIP350 vectors and was cross-verified by three
> independent implementations. The code has NOT yet run on
> physical Pico/Duo hardware, and the ceremony has not yet been
> walked by a human. Those are the next milestones; predictions
> in the claims table await falsification.

## The four verbs

1. **BORN of dice** — 256 rolls make key `k`, 256 rolls make pad
   `p`. 512 rolls total. No RNG in the room.
2. **CHECKED by strangers** — Raspberry Pi Pico and Milk-V Duo
   (base model, not Duo S) must agree byte-for-byte and
   fingerprint-for-fingerprint.
3. **KEPT in steel** — plate A holds `p`; plate B holds `k XOR p`
   plus the receive address (checksum) and a 4-word fingerprint.
4. **SPENT in public** — fixed-template Taproot key-path spend;
   dual identical Schnorr signatures; broadcast anywhere.

## Four layers

```
 DICE  ·  MATH  ·  STEEL  ·  SPEND
 "Nothing believed. Everything agreed."

 ┌──────────────────────────────────────────────────────────┐
 │ BORN        512 rolls. k and p from physics.             │
 │             if k is 0 or ≥ n, reroll (< 2^-127).         │
 └────────────────────────────┬─────────────────────────────┘
                              ▼
 ┌──────────────────────────────────────────────────────────┐
 │ CHECKED     two boards, two ISAs, two nations,           │
 │             two codebases. address + 4-word fingerprint  │
 │             spoken aloud. mismatch → stop.               │
 └────────────────────────────┬─────────────────────────────┘
                              ▼
 ┌──────────────────────────────────────────────────────────┐
 │ KEPT        plate A = p. plate B = k⊕p + address +       │
 │             fingerprint. one plate alone is worthless.   │
 └────────────────────────────┬─────────────────────────────┘
                              ▼
 ┌──────────────────────────────────────────────────────────┐
 │ SPENT       N inputs → 1 destination (+ optional change  │
 │             to same address). screen confirm. dual       │
 │             byte-identical BIP340 sigs. SD out.          │
 └──────────────────────────────────────────────────────────┘

 Address reuse is accepted. One key, one Taproot address.
 Multi-key privacy mitigation: HARDCORE.md.
```

Ceremony detail: **[PROTOCOL.md](PROTOCOL.md)**. Reversals from the
prior design: **[DECISIONS.md](DECISIONS.md)**.

## Quick start

    python3 tests/vectors_test.py
    python3 check_docs.py
    python3 tools/linecount.py

If the vector test does not pass, do not use the code.

## Falsifiable claims

Numbers below come from `tools/linecount.py` at commit time, or
are marked predicted.

| Claim | Value | Status |
|-------|------:|--------|
| `birth_pico.py` non-comment lines | 238 | measured (`tools/linecount.py`) |
| `birth_duo.py` non-comment lines | 232 | measured |
| `sign_pico.py` non-comment lines | 180 | measured |
| `sign_duo.py` non-comment lines | 149 | measured |
| `io_pico.py` (I/O; excluded from crypto budget) | 33 | measured |
| Ceremony die rolls (key + pad) | 512 | by design |
| Receive addresses per key | 1 | by design (reuse accepted) |
| Bill of materials | ~$60 | predicted — falsify this |
| Birth ceremony wall-clock | ~45 min | predicted — falsify this |
| Dual sign agreement (same JSON) | byte-identical | required by tests |

Target budgets in the prompt were ≤150 (birth) and ≤230 (sign).
Birth landed above 150; the table states the honest count. Sign
landed under 230.

## Residual trust

Both sides are modern silicon. The claim is not "trust nothing."
The claim is that a successful lie requires two companies, two
nations, two ISAs, and two codebases to emit the same false
address or the same false signature on the same day — and that
**operator error remains threat #1**. Spoken fingerprints exist
because tired humans fail hex comparison.

## Help wanted

1. **Independent rewrite of implementation #2** (`birth_duo.py`,
   `sign_duo.py`). Same-session dual authorship is a seat-warmer;
   see DECISIONS.md. This is the top ask.
2. Buildroot image recipe for the Milk-V Duo base model, reproducible
   from source.
3. Physical wiring notes and photos for keypad + SSD1306 on both
   boards (no seller links).
4. Adversarial review of the fixed transaction template and the
   OTP plate encoding format.
5. Break the dice-bias story (HARDCORE.md §2) with measured math.

## Prior art, credited gladly

The Glacier Protocol (especially the mandatory rehearsal before
real funds), SeedSigner and Krux (stateless DIY signing), SeedPicker
and the printed dice-table tradition, and the community's
dice-authored key practice — which is exactly what protected people
on July 30.

## Credits

v0.5 is a ground-up minimal rewrite. Critics of v0.3.4 are credited
in DECISIONS.md by the substance of what they forced us to delete.

## License

MIT — see LICENSE. Take it, fork it, break it.
Attribution appreciated; correction appreciated more.
