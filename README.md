# Dice Math Steel

> ⚠️ **EXPERIMENTAL — UNREVIEWED — DO NOT USE WITH REAL FUNDS.**
> Signet or throwaway amounts only until strangers smarter than us
> have broken and repaired this. That's not a disclaimer, it's the
> development model.

> Roll dice to make a 256-bit number.
> Punch it into steel, split across two places so neither alone means
> anything.
> One disbelieved computer turns it into an address —
> and Bitcoin itself grades the computer's work.
>
> **Nothing believed. Everything agreed.**

*Satoshi's setup, with dice.*

*Cold storage with no believed devices — every device graded. A
rough draft posted to be attacked, corrected, and improved — in
reply to July 30, 2026, the day the most trusted hardware wallet
in Bitcoin cost its users ~$38M because its firmware silently
generated weak randomness for five years.*

> **STATUS (pre-hardware):** Birth and spend code is **UNREVIEWED**.
> It passes pinned BIP340/341/350 vectors. That is not a third-party
> audit, and the two Python lineages share an interpreter. The code
> has not run on physical Pico/Duo hardware. The ceremony has not
> been walked by a human. **No signature from this protocol has
> been accepted by any Bitcoin network** — verified against pinned
> vectors and its own arithmetic, nothing else. Predictions in the
> claims table await falsification.

## The four verbs

1. **BORN of dice** — one die, thrown twice per lookup (row then
   column) on a 36-cell card. ≈117 throws make key `k`, ≈117 make
   pad `p`. Worksheet feeds the device a 256-bit integer. No RNG
   in the room.
2. **CHECKED by strangers** — the birth device is graded by Bitcoin
   Core (`tr()` on public data) plus a $5 ledger round-trip;
   steel re-derivation catches typos before real funding. The
   second stranger-machine witnesses the nonce on spend day.
3. **KEPT in steel** — 16×16 plates, notched, ceremony-ID'd,
   two-pass stamped, both symbols marked. Plate A holds `p`.
   Plate B holds `k ⊕ p`, the address, and four words under
   **ADDRESS FINGERPRINT** (public checksum — not the key).
4. **SPENT in public** — fixed-template Taproot key-path spend;
   dual identical Schnorr signatures (birth device + witness);
   broadcast anywhere.

## The machine, on one page

```
 ┌─ ENTROPY ────────────────────────────────────────────┐
 │   ONE die, thrown TWICE in sequence                  │
 │       first throw = ROW, second throw = COLUMN       │
 │       (order comes from time, never from sorting)    │
 │                                                      │
 │        36 outcomes ──▶ 32 patterns of 5 bits         │
 │                   └──▶  4 cells say REROLL           │
 │                                                      │
 │        52 lookups = 260 bits, keep 256               │
 │        ≈ 117 throws (11% rejection)                  │
 │        floor is log₂(6)=2.585 b/throw → 99 throws    │
 │                                                      │
 │   ONE CARD. 36 CELLS. HAND-CHECKABLE IN 2 MINUTES:   │
 │   each of the 32 patterns appears exactly once.      │
 └──────────────────────────────────────────────────────┘
                          │
                          ▼
       KEY  k = a raw 256-bit secp256k1 scalar
            written in pencil. no words, no
            derivation, no checksum.
                          │
        ┌─────────────────┴─────────────────┐
        ▼                                   ▼
   throw a PAD                         k XOR pad
   (same card)                              │
        │                                   ▼
        ▼                          ┌─────────────┐
 ┌─────────────┐                   │  PLATE B    │
 │  PLATE A    │                   │  16 × 16    │
 │  16 × 16    │                   │  key ⊕ pad  │
 │  the pad    │                   │  ⌐ notch    │
 │  ⌐ notch    │                   │  ID: XXXX   │
 │  ID: XXXX   │                   └──────┬──────┘
 └─────────────┘                          │ + ADDRESS
   LOCATION 1                             │ + ADDRESS FINGERPRINT
                                   LOCATION 2
                                          ▼
                                  the forever answer-key

 ┌─ SILICON CONTACT: EXACTLY TWICE, BOTH IRREDUCIBLE ───┐
 │  BIRTH   k ─▶ k·G ─▶ taproot tweak ─▶ bc1p…          │
 │          graded by Bitcoin Core tr()                 │
 │          + a small round-trip on the ledger          │
 │          UNREVIEWED                                  │
 │                                                      │
 │  SPEND   sign ─▶ witnessed by a second, unrelated    │
 │          machine; deterministic nonces must agree    │
 │          byte-for-byte, or you STOP                  │
 │          graded by the verification equation,        │
 │          checkable on any public computer            │
 │          UNREVIEWED                                  │
 │                                                      │
 │  Between them: years. Dice, pencil, steel, paper.    │
 │  This is the floor. Bitcoin requires an address to   │
 │  exist and a signature to be computed. Nothing in    │
 │  our design adds a third contact.                    │
 └──────────────────────────────────────────────────────┘
```

Address reuse is accepted. One key, one Taproot address.
Multi-key privacy mitigation: HARDCORE.md.

White paper: [Dice·Math·Steel — a white paper for the kitchen table](https://hambomyers.github.io/dice-math-steel/whitepaper.html).

Ceremony: **[PROTOCOL.md](PROTOCOL.md)**. Reversals: **[DECISIONS.md](DECISIONS.md)**.
Credits: **[CREDITS.md](CREDITS.md)**.

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
| Expected throws per number (6×6 card, 11% reroll) | ≈117 | by design |
| Expected throws, key + pad | ≈234 | by design |
| Receive addresses per key | 1 | by design (reuse accepted) |
| Ceremony hardware (birth device) | ~$15 | predicted — falsify this |
| Full build (birth + witness) | ~$40 | predicted — falsify this |
| Birth ceremony wall-clock | ~45 min | predicted — falsify this |
| Dual sign agreement (same JSON) | byte-identical | required by tests |

Target budgets in the prompt were ≤150 (birth) and ≤230 (sign).
Birth landed above 150; the table states the honest count. Sign
landed under 230.

## Residual trust

Birth runs on one board; Bitcoin Core grades the address on public
data; a witness board joins only on spend day. The claim is not
"trust nothing." The claim is that a successful lie at birth must
fool the device **and** Core, and a successful lie at spend must
get two codebases to emit the same false signature the same day —
and that **operator error remains threat #1**. Spoken fingerprints
and steel re-derivation exist because tired humans fail hex
comparison.

**Shared-interpreter caveat.** Both `src/` lineages are Python
(MicroPython on the boards, CPython in tests). They share a large
common trusted base; their bug surfaces are correlated. That
weakens "independent implementations" more than earlier docs
admitted. Passing pinned BIP340/341/350 vectors means the code
matches the spec on the cases the spec enumerates — not that it
has had a third-party audit, and not that it is free of side
channels. The largest undone deletion is a bare-metal C second
implementation that drops the shared interpreter.

## Help wanted

1. **Bare-metal C second implementation** — delete the shared
   MicroPython interpreter on one device. Same-session dual
   Python files remain seat-warmers (DECISIONS.md). This is the
   top ask.
2. Buildroot image recipe for the Milk-V Duo base model (spend-day
   witness), reproducible from source.
3. Physical wiring notes and photos for keypad + SSD1306 on the
   birth Pico (and the witness Duo when you build it) — no seller
   links.
4. Adversarial review of the fixed transaction template and the
   OTP plate encoding format.
5. Break the dice-bias story (HARDCORE.md §2) with measured math.
6. Walk the ceremony on physical hardware and falsify the predicted
   claims (BOM, wall-clock).

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
