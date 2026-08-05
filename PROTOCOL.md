# The Ceremony — Dice Math Steel

*The complete protocol, start to finish. Read the whole thing before
buying anything.*

> ⚠️ Rough draft. Unreviewed. Practice the entire ceremony with a
> throwaway key and signet coins first. Do not put real funds on
> this until the code has survived public review — and then start
> small anyway.

## Phase 0 — Sourcing (you buy everything; we sell nothing)

Buy generic retail parts. This repo never links to a seller.

**Birth day (one device):**

- **Dice:** casino-grade (sharp-edge) dice, any store, chosen that
  day. Two or more dice from different sources is a free upgrade.
- **Birth device:** Raspberry Pi Pico (RP2040). **Not Pico W** — no
  radios on the ceremony board. Matrix keypad, SSD1306 OLED,
  battery pack (USB is power-only after flash).
- **Steel:** stainless plates and a letter/number stamp set,
  hardware store. Two plates: A (pad) and B (XOR + address +
  fingerprint).
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
You enter the rolls **once**, into **one** device.

## Phase 3 — Ceremony (one device + Core as senior referee)

1. **Reflash the birth device from this repo** before the ceremony.
   Hardware is amnesiac, not sacrificial.
2. Enter the key rolls and pad rolls into the **one** birth device
   (Pico). No second keyboard at birth.
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
5. Stamp **plate A** with pad `p` (in the form your stamp set can
   cut — the device displays the value for stamping).
6. Stamp **plate B** with `k XOR p`, the receive address (the
   permanent checksum), and the 4-word fingerprint.
7. **Prove from steel before destroying paper:** power off, reflash,
   re-enter plate values only, recover `k = plate_B_xor XOR
   plate_A`, re-derive the address, match the stamp **and** the
   Core `rawtr()` result. Only then burn roll sheets. This catch
   is for entry typos — threat #1.
8. Power off. Secrets existed only in RAM. After key entry, the
   Pico's USB stays power-only.

## Phase 4 — Rehearsal (mandatory before real funds)

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

## Phase 5 — Heirs

**Pattern public, arrangement private.**

Heirs must be able to find:

1. Both plates (A and B),
2. The one-page instruction: *XOR the plates, import the resulting
   256-bit key into Bitcoin Core or Electrum as a Taproot key,
   send.*

Rehearse the trail once **without the owner present**. If a
non-owner cannot finish, fix the instructions — not the math.

## Phase 6 — Spend (witness machine required)

Template only: **N inputs** (all owned by the one key) → **1
destination** + optional **1 change** back to the same address.

The second stranger-machine is required **here**, not at birth. It
witnesses the nonce: both devices must emit byte-identical BIP340
signatures.

1. Build the unsigned transaction on any online machine as the
   documented JSON (outpoints, amounts, destination, optional
   change). Copy it to the Duo's SD card. Public data only.
2. On **both** devices (birth Pico and witness Duo), enter `k`
   recovered from the plates. Load the unsigned JSON (Duo: SD;
   Pico: keyed or SD adapter per your build).
3. **Screen confirmation before signing:** destination, amount,
   fee. A tired human must be able to abort here.
4. Both devices construct the BIP341 key-path sighash and BIP340
   signature with `aux_rand` = 32 zero bytes. Signatures must be
   **byte-identical**. Mismatch: stop.
5. Write the signed raw transaction hex to SD (public). Broadcast
   from any online machine. Power off.

No wire between devices. No vendor portal.

## Phase 7 — Optional catharsis

The hammer. Clearly labeled **ritual**. The security step was
reflash-and-power-off. Smashing boards proves nothing to the
chain; it may help the operator sleep. Recycle the wreckage if
you swing.
