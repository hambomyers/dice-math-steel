# The Ceremony — Dice Math Steel

*The complete protocol, start to finish. Read the whole thing before
buying anything.*

> ⚠️ Rough draft. Unreviewed. Practice the entire ceremony with a
> throwaway key and signet coins first. Do not put real funds on
> this until the code has survived public review — and then start
> small anyway.

## Phase 0 — Sourcing [READY: you buy everything; we sell nothing]

Buy generic retail parts. This repo never links to a seller.

**Birth day (one device):**

- **Dice:** **one** casino-grade die (sharp edges, flush pips,
  translucent), any store, chosen that day. *The author of this
  protocol must never be your dice vendor.* One die, thrown
  twice in sequence — not two dice together (collision can
  correlate).
- **Birth device:** Raspberry Pi Pico (RP2040). **Not Pico W** — no
  radios on the ceremony board. Matrix keypad, SSD1306 OLED,
  battery pack (USB is power-only after flash).
- **Steel:** stainless plates and a letter/number stamp set,
  hardware store. Two plates (and a copy of each): A (pad) and
  B (`k ⊕ p` + address + **ADDRESS FINGERPRINT**). Each plate
  is a 16×16 grid. See **The plate** below.
- **Online machine with Bitcoin Core** (already reviewed by the
  world): used only on **public** data — the x-only public key /
  address check. It never sees rolls, `k`, or the pad.
- **A hammer.** Optional catharsis (Phase 7); not load-bearing.

**Spend day (witness machine — buy when you need to spend, not at
birth):**

- **Witness device:** Milk-V Duo **base model**, same keypad/OLED
  wiring as the Pico, plus an SD card slot and a buildroot Linux
  image you build from source.

  > **WARNING — Do not buy the Milk-V Duo S.** The Duo S has WiFi
  > and Bluetooth. The witness machine must be the base Duo without
  > radios.

No wire ever connects the birth device and the witness device.

## The plate

```
        0  1  2  3   4  5  6  7   8  9  A  B   C  D  E  F
      ┌────────────┬────────────┬────────────┬────────────┐
   0  │            │            │            │            │
   1  │            │            │            │            │
   .  │            │            │            │            │
   F  │            │            │            │            │
      └────────────┴────────────┴────────────┴────────────┘
        ⌐ notch bottom-left            ceremony ID: 4 chars
```

Rules, each with its stated reason:

- **16×16, with row/column labels and a gutter every 4 columns.**
  Ergonomics, not error correction. Any bit has a speakable
  address: "row 7, column C." Two people can confirm positions
  aloud.
- **No parity marks. No checksums. No third symbol.** The stamped
  address is already a 256-bit correcting code over the key
  (`tools/recover.py`). Two symbols is what makes two-pass
  stamping work.
- **Two-pass stamping.** Punch every zero in one pass, every one
  in a second pass. This degrades any strike-order side-channel
  to a popcount with no positional information. Assume everything
  in the room is listening, and stamp in an order that makes
  listening worthless.
- **Both symbols always marked. Never leave zeros blank.** A
  blank is ambiguous between "zero" and "worn away." Marking
  both turns fire and corrosion into an unreadable glyph — an
  *erasure*, cheaper to recover from than a substitution.
- **Corner notch on every plate.** A 180° rotation of a 16×16
  grid is silent and catastrophic. Four punches make it
  impossible.
- **4-character ceremony ID on both plates (and both copies).**
  Pick it *before* stamping; it is not derived from the key.
  Mixing plate A from one ceremony with plate B from another is
  a live failure mode.
- **Two copies of each plate.** Losing either half forever loses
  the coins. The copy of plate A must never live where plate B
  lives.
- **Plate B labels.** Stamp the four spoken words under the
  heading **ADDRESS FINGERPRINT**. They are a public checksum of
  the receive address, drawn from `english.txt`. They are *not*
  the key. Any later optional word-group that *is* the key
  (see `docs/words-appendix.md`) is labeled **KEY READING** and
  must never share a plate with the fingerprint.

## Phase 1 — Inspect the die [READY: eyes and hands]

No tally test. At ~120 throws there is essentially no statistical
power to detect bias small enough to matter; a ritual that
manufactures false confidence is worse than no test.

Physical inspection only: sharp edges, flush pips, no visible
wear, translucent casino-grade stock. Optional salt-water float
test. Bias remaining after that is discussed in HARDCORE.md §2 —
including that the 36-cell card is *more* sensitive to per-face
bias than the old half-split mapping.

## Phase 2 — Author [READY: paper only]

Alone. Curtains drawn. No phones in the room — not silenced,
absent. Print `docs/dice-card.md` and `docs/worksheet.md`.

**Choose your mapping before the first throw.**

- **Standard:** two throws per lookup, 5 bits per lookup, ~117
  throws per number. Fewer throws; every per-face deviation of
  the die propagates into the output.
- **Paranoid:** first throw only, low (1–3) → 0, high (4–6) → 1,
  256 throws per number. More throws; per-face bias largely
  washes out because six outcomes collapse into two.

Both produce the same object: 256 bits on the worksheet, which is
what the device consumes. Do not switch mid-number. The card is a
reference, not the home of this choice.

### Standard procedure

Throw **one die twice in sequence.** First throw = **row**.
Second throw = **column**. Read that cell. Never reverse, never
sort, never swap the two throws. Order comes from time, not
judgement.

32 of 36 cells carry a unique 5-bit pattern. 4 cells say
**REROLL** — throw both throws again, fresh. 52 lookups yield 260
bits; keep the first 256. Expected throws ≈ 117 per number (11%
rejection). Floor is log₂(6) ≈ 2.585 bits/throw → 99 throws if
nothing is rejected and you packed perfectly; we do not.

Copy five bits at a time onto the worksheet. Repeat the whole
process for the pad.

### Paranoid procedure

Ignore the columns. Throw once. Write **0** if the face is 1–3,
**1** if the face is 4–6. One bit per throw, one worksheet cell
per throw. 256 throws for the key, 256 for the pad. Same card,
same worksheet, no extra equipment.

### After the bits exist

The private key **is** that 256-bit integer `k`. No words, no
derivation. You will type those 256 bits (from the worksheet, not
from the die) into **one** device. `src/` still consumes a
256-bit integer; the mapping only changes how a hand produces it.

If the machine later reports `k == 0` or `k ≥ n` (secp256k1
order), **reroll the key from scratch**. Probability < 2^-127.
Do not "adjust" it. The pad is not a scalar; still fill 256 bits.

## Phase 3 — Ceremony [UNREVIEWED — passes pinned BIP340/341/350 vectors; no third-party audit]

1. **Reflash the birth device from this repo** before the ceremony.
   Hardware is amnesiac, not sacrificial.
2. Enter the 256-bit key and 256-bit pad from the **worksheet**
   into the **one** birth device (Pico). No second keyboard at
   birth. The die does not meet the device. The keypad still
   speaks faces: for each worksheet bit, press **1** if the bit
   is 0, **4** if the bit is 1. (`rolls_to_int` maps 1–3 → 0 and
   4–6 → 1; this is how the worksheet feeds the existing device
   without a `src/` change.)
3. The device displays: plate A = `p`, plate B = `k XOR p`, the
   Taproot receive address, and a **4-word fingerprint** of that
   address. Speak the fingerprint aloud while you copy it — short
   human channels, not hex-vs-hex eyeballing alone.
4. **Bitcoin Core check (public data only).** On an online machine
   that never saw your rolls, take the device's x-only **output**
   public key `Q` (32-byte hex the device shows for this step) and
   run:

       bitcoin-cli deriveaddresses "rawtr(Q)"

   Replace `Q` with that 32-byte hex (no `0x`). Core must return
   the **same** bech32m address the device showed. Mismatch: stop.
   Reflash. Re-enter. Do not stamp. Core is the third lineage —
   hundreds of authors, 17 years of hostile review — grading the
   device's homework without ever touching the secret.
5. Stamp **plate A** as a 16×16 grid of pad `p`. Notch. Ceremony
   ID. Two-pass (all zeros, then all ones). Both symbols marked.
   Verify against the worksheet twice, out loud, before anything
   burns.
6. Stamp **plate B** as a 16×16 grid of `k ⊕ p`, plus the receive
   address (the permanent checksum) and the four words under the
   stamped heading **ADDRESS FINGERPRINT**. Same notch, same ID,
   same two-pass, same both-symbols rule. Speak the fingerprint
   aloud while you copy it.
7. **Prove from steel before destroying paper.** Recover `k` on
   the printed worksheet (see **Recovery** below) — never steel
   against steel. Then power off, reflash, enter the recovered
   256 bits, re-derive the address, match the stamp **and** the
   Core `rawtr()` result. Only then burn worksheets and roll
   notes. This catch is for entry typos — threat #1.
8. Power off. Secrets existed only in RAM. After key entry, the
   Pico's USB stays power-only.

## Recovery — paper is the jig [READY]

**Never align steel to steel.** Stacking punched plates computes
AND (light only where both have holes), not XOR. The printed
16×16 worksheet is the jig. `docs/worksheet.md`.

1. Transcribe plate A onto the worksheet, one row at a time,
   reading through an index card with a slot cut in it.
2. Transcribe plate B onto the row directly beneath. Confirm
   the ceremony IDs match and both notches sit the same way.
3. Same-or-different on paper, where the printed grid guarantees
   alignment. Write the result in the third grid. That row is
   `k`.
4. Verify against the address stamped on plate B before trusting
   the result — by speaking the **ADDRESS FINGERPRINT**, by
   `tools/recover.py`, and (before first funding) by re-deriving
   on a reflashed device.

If a glyph is unreadable, it is an *erasure*, not a guessed bit.
`recover.py` searches Hamming distance 1, then 2, then 3 against
the stamped address and prints the plate cells it flipped. Go look
at those punches. If a mark is clean and unambiguous, STOP. Do
not invent a substitute bit by eye.

The search is a convenience, not a guarantee. Beyond three bits
you are not recovering: the plate failed, and the other copy of
the plate is the recovery path. Distance 3 is 2,796,417
candidates. Measured on the author's machine at this commit:
~5.6 ms per derivation → ~4.4 hours. The tool times a sample on
*your* machine and prints the estimate before it starts. Ctrl-C
is safe; nothing is written until a match is confirmed.

## Why Bitcoin Core, and why a raw number

Core is categorically different from every other dependency here.
No company, no vendor, no business model, nobody to subpoena or
bankrupt. Fifteen years of adversarial review, reproducible builds
signed by independent maintainers, and it *defines* consensus
rather than interpreting it. It already satisfies this protocol's
own test: the counterparty is anyone, because anyone can run it,
read it, or fork it.

A raw 256-bit scalar is the most portable representation that
exists. A word-list phrase is only meaningful after stretching
and a derivation tree — extra standards that must all survive
and all be applied correctly. The scalar is the object those
standards reduce to. Any competent developer can derive and sign
from it in forty lines. On standards rot, this design is *more*
durable than a phrase, not less. (Named comparison with the
deleted word-list stack: HARDCORE.md § "Why a raw scalar".)

The honest residual risk is different. Core's consensus rules are
extraordinarily stable; its wallet RPC surface is not. Legacy
BDB wallets were deprecated and then removed. `importdescriptors`
replaced `importmulti`. Descriptor syntax has evolved. The
durable claim is about the mathematics, not about a command line
surviving thirty years.

So the gap is **not** that the key becomes unrecoverable. It is
that recovery is an expert operation and an heir may not be an
expert. That is an operator problem with an operator fix: a
written recovery document a non-expert can execute, and a
rehearsal proving they can (Phase 4, Phase 5). Core is not a
single point of failure. Core's RPC is also not a forever
guarantee.

## Phase 4 — Rehearsal [READY: mandatory before real funds]

Borrowed from the Glacier Protocol, with credit.

1. Send about **$5** (or a throwaway dust amount you can afford to
   lose) to the stamped address on mainnet — or walk signet first,
   then mainnet dust. Watch a confirmation. The address must
   receive; that is the ledger round-trip.
2. Before any amount you would hate to lose: **re-derive from
   stamped steel again** on a fresh reflash (Phase 3 step 7). Match
   address and fingerprint. Typo catch, still.
3. Then spend the rehearsal amount out through Phase 6 (this is
   when you first need the witness machine). If the rehearsal
   fails, the wallet has not earned real funds.

A worked signet transcript lives in
`docs/rehearsal-signet.md`.

## Phase 5 — Heirs [READY: instructions]

**Pattern public, arrangement private.**

Heirs must be able to find:

1. Both plates (A and B) — matching ceremony ID, notches the
   same way,
2. The one-page instruction: *Never steel to steel. Transcribe
   both plates onto the printed worksheet. Same-or-different.
   The result is the key. Confirm the ADDRESS FINGERPRINT.
   Import that 256-bit integer into Bitcoin Core as a Taproot
   key, send.*

Rehearse the trail once **without the owner present**. If a
non-owner cannot finish, fix the instructions — not the math.

## Phase 6 — Spend [UNREVIEWED — passes pinned BIP340/341/350 vectors; no third-party audit]

Template only: **N inputs** (all owned by the one key) → **1
destination** + optional **1 change** back to the same address.

The second stranger-machine is required **here**, not at birth. It
witnesses the nonce: both devices must emit byte-identical BIP340
signatures.

1. Build the unsigned transaction on any online machine as the
   documented JSON (outpoints, amounts, destination, optional
   change). Copy it to the Duo's SD card. Public data only.
2. On **both** devices (birth Pico and witness Duo), enter `k`
   recovered on the worksheet from the plates (Recovery above).
   Load the unsigned JSON (Duo: SD; Pico: keyed or SD adapter
   per your build).
3. **Screen confirmation before signing:** destination, amount,
   fee. A tired human must be able to abort here.
4. Both devices construct the BIP341 key-path sighash and BIP340
   signature with `aux_rand` = 32 zero bytes. Signatures must be
   **byte-identical**. Mismatch: stop.
5. Write the signed raw transaction hex to SD (public). Broadcast
   from any online machine. Power off.

No wire between devices. No vendor portal.

## Phase 7 — Optional catharsis [READY: ritual]

The hammer. Clearly labeled **ritual**. The security step was
reflash-and-power-off. Smashing boards proves nothing to the
chain; it may help the operator sleep. Recycle the wreckage if
you swing.
