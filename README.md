# Dice Math Steel

**Nothing believed. Everything agreed.**

*Satoshi's setup, with dice.*

**New here? Read the white paper:** [Dice·Math·Steel —
a white paper for the kitchen table](docs/whitepaper.html)
(or view it rendered at dicemathsteel.com once live).

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
   `p`. 512 rolls total, entered once on one device. No RNG in
   the room.
2. **CHECKED by strangers** — the birth device is graded by Bitcoin
   Core (`rawtr()` on public data) plus a $5 ledger round-trip;
   steel re-derivation catches typos before real funding. The
   second stranger-machine witnesses the nonce on spend day.
3. **KEPT in steel** — plate A holds `p`; plate B holds `k XOR p`
   plus the receive address (checksum) and a 4-word fingerprint.
4. **SPENT in public** — fixed-template Taproot key-path spend;
   dual identical Schnorr signatures (birth device + witness);
   broadcast anywhere.

## Four layers

```
 DICE  ·  MATH  ·  STEEL  ·  SPEND
 "Nothing believed. Everything agreed."
 "Satoshi's setup, with dice."

 ┌──────────────────────────────────────────────────────────┐
 │ BORN        512 rolls, one device. k and p from physics. │
 │             if k is 0 or ≥ n, reroll (< 2^-127).         │
 └────────────────────────────┬─────────────────────────────┘
                              ▼
 ┌──────────────────────────────────────────────────────────┐
 │ CHECKED     Core rawtr() on public key; $5 round-trip;   │
 │             steel re-derive before real funds.           │
 │             mismatch → stop.                             │
 └────────────────────────────┬─────────────────────────────┘
                              ▼
 ┌──────────────────────────────────────────────────────────┐
 │ KEPT        plate A = p. plate B = k⊕p + address +       │
 │             fingerprint. one plate alone is worthless.   │
 └────────────────────────────┬─────────────────────────────┘
                              ▼
 ┌──────────────────────────────────────────────────────────┐
 │ SPENT       witness machine joins here. N inputs → 1     │
 │             destination (+ optional change). dual        │
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
| Ceremony hardware (birth device) | ~$15 | predicted — falsify this |
| Full build (birth + witness) | ~$40 | predicted — falsify this |
| Birth ceremony wall-clock | ~45 min | predicted — falsify this |
| Dual sign agreement (same JSON) | byte-identical | required by tests |

Target budgets in the prompt were ≤150 (birth) and ≤230 (sign).
Birth landed above 150; the table states the honest count. Sign
landed under 230.

## Residual trust

Both birth silicon and the spend-day witness are modern boards.
Bitcoin Core grades the address on public data. The claim is not
"trust nothing." The claim is that a successful lie at birth must
fool the device **and** Core, and a successful lie at spend must
get two codebases to emit the same false signature the same day —
and that **operator error remains threat #1**. Spoken fingerprints
and steel re-derivation exist because tired humans fail hex
comparison and double-entry.

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
