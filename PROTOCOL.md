# The Ceremony — Dice Math Steel

*The complete protocol, start to finish. Read the whole thing before
buying anything.*

> ⚠️ Rough draft. Unreviewed. Practice the entire ceremony with a
> throwaway key and signet coins first. Do not put real funds on
> this until the code has survived public review — and then start
> small anyway.

## Phase 0 — Sourcing (you buy everything; we sell nothing)

Buy generic retail parts. This repo never links to a seller.

- **Dice:** casino-grade (sharp-edge) dice, any store, chosen that
  day. Two or more dice from different sources is a free upgrade.
- **Device A:** Raspberry Pi Pico (RP2040). **Not Pico W** — no
  radios on the ceremony board.
- **Device B:** Milk-V Duo **base model**.

  > **WARNING — Do not buy the Milk-V Duo S.** The Duo S has WiFi
  > and Bluetooth. The ceremony requires the base Duo without
  > radios. Same keypad/OLED wiring as the Pico, plus an SD card
  > slot and a buildroot Linux image you build from source.

- **Keypads:** matrix keypads for GPIO on both boards (same wiring
  plan on A and B).
- **OLEDs:** SSD1306 displays for both boards.
- **Battery pack** for the Pico (USB is power-only after flash).
- **SD card** for the Duo (unsigned tx in, signed tx out; public
  data only).
- **Steel:** stainless plates and a letter/number stamp set,
  hardware store. Two plates: A (pad) and B (XOR + address +
  fingerprint).
- **A hammer.** Optional catharsis (Phase 7); not load-bearing.

No wire ever connects A and B.

## Phase 1 — Test the dice [READY: needs only the dice]

Roll each die ~120 times, but tally what the protocol actually
uses: the {1,2,3} vs {4,5,6} split, not per-face counts. Per-face
bands can look healthy while hiding a 55/45 lean on the bit
boundary — and a 55/45 die costs roughly 18 of your 128 bits of
min-entropy. At ~120 rolls, a split more lopsided than about 70/50
is suspect — demote that die to non-security duty. This threshold
catches gross defects, not subtle ones: a genuinely 55/45 die
passes it most of the time. Bounding bias that small takes roughly
800 rolls, not 120 — which is why we don't ask you to; more rolls
only tighten the bound on the aggregate. This is an assurance
check, not an entropy guarantee; casino-grade dice are doing the
real work. (The bias trade-off is discussed in HARDCORE.md §2.)

## Phase 2 — Author (roll key + pad)

Alone. Curtains drawn. No phones in the room — not silenced,
absent.

Mapping: **1, 2, or 3 → bit 0. 4, 5, or 6 → bit 1.** One bit per
roll.

```
 KEY   =  256 rolls  →  256-bit integer k
 PAD   =  256 rolls  →  256-bit integer p
                         ─────────
                          512 rolls total for the ceremony
```

Record rolls on paper as you go. After 256 key rolls, interpret
the bit string as integer `k` (big-endian). If `k == 0` or
`k >= n` (secp256k1 order), **reroll the key from scratch**. This
occurs with probability < 2^-127. Same check is not required for
the pad (the pad is not a scalar); still roll a full 256 bits.

There is no word list in this phase. The private key **is** `k`.

## Phase 3 — Ceremony (two strangers must agree)

1. **Reflash both devices from this repo** before every ceremony.
   Hardware is amnesiac, not sacrificial.
2. Enter the same key rolls and pad rolls into **both** devices
   (Pico and Duo). No wire between them.
3. Each device computes: plate A = `p`, plate B = `k XOR p`, the
   Taproot receive address, and a 4-word fingerprint of that
   address.
4. **Speak the fingerprint aloud.** Both devices must match. Then
   speak or compare the address the same way (short, human
   channels — not hex-vs-hex eyeballing of long strings alone).
   Mismatch: stop. Reflash. Re-enter. Do not stamp.
5. Stamp **plate A** with pad `p` (recorded in the form your stamp
   set can cut — the devices display the value for stamping).
6. Stamp **plate B** with `k XOR p`, the receive address (the
   permanent checksum), and the 4-word fingerprint.
7. Prove from steel before destroying paper: re-enter plate values
   on a fresh reflash, recover `k = plate_B_xor XOR plate_A`,
   re-derive the address, match the stamp. Only then burn roll
   sheets.
8. Power off. Secrets existed only in RAM. After key entry, the
   Pico's USB stays power-only; the Duo never carries secrets on
   SD.

## Phase 4 — Rehearsal (mandatory before real funds)

Borrowed from the Glacier Protocol, with credit: run a **full
cycle with pocket sats on the real chain** (or signet first, then
mainnet dust) before any amount you would hate to lose.

Deposit a trivial amount to the stamped address. Watch a
confirmation. Then spend it out through Phase 6. If the rehearsal
fails, the wallet has not earned real funds.

A worked signet transcript lives in
`docs/rehearsal-signet.md`.

## Phase 5 — Heirs

**Pattern public, arrangement private.**

Heirs must be able to find:

1. Both plates (A and B),
2. The one-page instruction: *XOR the plates, import the resulting
   256-bit key into Bitcoin Core or Electrum as a Taproot key,
   send.*

Rehearse the trail once **without the owner present**. If a
non-owner cannot finish, fix the instructions — not the math.

## Phase 6 — Spend

Template only: **N inputs** (all owned by the one key) → **1
destination** + optional **1 change** back to the same address.

1. Build the unsigned transaction on any online machine as the
   documented JSON (outpoints, amounts, destination, optional
   change). Copy it to the Duo's SD card. Public data only.
2. On each device, enter `k` recovered from the plates (or still in
   RAM only during a birth-and-spend rehearsal). Load the unsigned
   JSON (Duo: SD; Pico: keyed or SD adapter per your build).
3. **Screen confirmation before signing:** destination, amount,
   fee. A tired human must be able to abort here.
4. Both devices construct the BIP341 key-path sighash and BIP340
   signature with `aux_rand` = 32 zero bytes. Signatures must be
   **byte-identical**. Mismatch: stop.
5. Write the signed raw transaction hex to SD (public). Broadcast
   from any online machine. Power off.

No second wire. No vendor portal.

## Phase 7 — Optional catharsis

The hammer. Clearly labeled **ritual**. The security step was
reflash-and-power-off. Smashing boards proves nothing to the
chain; it may help the operator sleep. Recycle the wreckage if
you swing.
