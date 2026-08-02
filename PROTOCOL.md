# The Ceremony — Dice Math Steel, v0.2

*The complete protocol, start to finish. Read the whole thing before
buying anything. Status flags are honest: [READY] means this repo's
code supports the step today; [GAP] means you currently need an
outside open-source tool, named inline, until this repo's roadmap
catches up.*

> ⚠️ Rough draft. Unreviewed. Practice the entire ceremony with a
> throwaway key and signet/testnet coins first. Do not put real funds
> on this until the code has survived public review — and then start
> small anyway.

## Phase 0 — Sourcing (you buy everything; we sell nothing)

- **Dice:** any casino-grade (sharp-edge) dice, any store, your
  choice made that day. Two or more dice from different sources is
  a free upgrade. The vendor of this protocol must never be your
  dice vendor — that's the point.
- **Two junk computers:** bought from different second-hand sources
  (thrift store, surplus, yard sale), chosen on the spot. Spec is
  about *absent capabilities*, not brand: no WiFi/Bluetooth hardware
  (desktops usually win; remove cards if present), pre-2006-era
  preferred (no management engine), working optical drive a plus,
  hard drive will be unplugged anyway. Old machines fail — buy an
  extra if they're $10.
- **Boot media:** one write-once CD-R per machine with a minimal
  offline Linux, burned and hash-verified beforehand, or a USB stick
  prepared the same way if no optical drive (CD-R preferred:
  write-once media cannot be reinfected).
- **Paper kit:** printed `table.txt` (the dice-to-word table),
  printed BIP39 wordlist (`english.txt`), roll-recording sheets,
  pens. Print these from a machine and printer you consider clean;
  the table's integrity can be re-checked on the ceremony machines.
- **Steel:** stainless plates or washers and a letter/number stamp
  set, hardware store. Two sets: one for the words, one for the
  passphrase.
- **A sledgehammer.** Ceremonial by design (see Phase 6), mandatory
  by tradition.

## Phase 1 — Test the dice [READY: needs only the dice]

Roll each die ~120 times, tallying faces. You are looking for gross
defects only: any face under ~12 or over ~28 counts is suspect —
demote that die to non-security duty. The protocol's 1-bit-per-roll
mapping plus excess entropy tolerates small bias; this test catches
big bias. (The bias trade-off is discussed in HARDCORE.md §2.)

## Phase 2 — Author the key [READY: paper only, zero chips]

Alone. Curtains drawn. No phones in the room — not silenced, absent.

1. For each of 11 words: roll 11 bits (1,2,3 → 0; 4,5,6 → 1),
   write the bit pattern, find it in the printed table, write the
   word. Double-check each lookup before moving on.
2. Roll 7 more bits and record them — the human half of word 12.
3. You now hold 128 bits of entropy authored entirely by your hands.
   Nothing electronic has been in the room yet.

## Phase 3 — The forced move [READY: dice2words.py]

Boot junk machine #1 from the CD-R (hard drive unplugged). Run:

    python3 dice2words.py --test     # must pass before anything else
    python3 dice2words.py finish     # enter your 11 words + 7 bits

The machine names the single word that can legally complete your
sequence — it computes the checksum and chooses nothing. Repeat the
identical input on machine #2. **The word must match.** Then run
`check` with all 12 words on both machines: both must say VALID.
Any mismatch anywhere: stop, diagnose, restart Phase 2 with fresh
rolls if in doubt.

Optional purity variants (hand-computed SHA-256, blind brute force
of the final word) are in HARDCORE.md §1.

## Phase 4 — Passphrase [READY: paper only]

Generate a passphrase from fresh dice rolls (e.g., five words via
the same table, or Diceware). Never a human-invented phrase. Use at
least five words (~55–64 bits) and treat that as the floor, not the
target: the passphrase must stand alone against an attacker who
already holds steel A. Six words buys comfortable margin. This
splits your secret into two factors stored apart; either alone is
useless. Record on paper for now.

## Phase 5 — Addresses and verification [GAP: uses outside tools]

This repo does not yet include key derivation (see the Roadmap in
README.md). Until it does, use a well-known open-source wallet, run
offline on both ceremony machines from your verified boot media —
e.g., Electrum in offline mode, or SeedSigner/Krux code — to:

1. Enter the 12 words + passphrase on machine #1; derive the
   account xpub and the first 50 receiving addresses.
2. Repeat independently on machine #2. **Every address must match.**
3. Copy the address list to paper (both machines' screens agree, so
   hand-copy from one and verify against the other), or print it if
   a printer you accept is available. This sheet becomes your
   permanent receive list — the root of truth.
4. Optional third check: reconstruct watch-only from the xpub on an
   ordinary online machine later; addresses must match again.

The address sheet cannot spend a coin, but guard it anyway: lose it
and you're back to trusting screens; show it and you've shown your
balances.

## Phase 6 — Steel, then death [READY: hands only]

1. Stamp the 12 words on steel set A; stamp the passphrase on steel
   set B. Verify each stamping against paper twice, out loud.
2. Burn all paper that carries secrets (rolls, words, passphrase).
   The address sheet is not a secret and survives.
3. Power off both machines. The secret existed only in RAM and is
   now fading charge. Then the sledge, through the chips — ceremony,
   not load-bearing: there was nothing left to kill. Recycle the
   wreckage yourself.
4. Steel A and steel B travel to separate locations. Neither alone
   can spend. No location's holder should be able to reach the other.

## Phase 7 — Prove it end to end [GAP: signing uses outside tools]

Before real funds: send a trivial amount to address #1. Watch it
confirm via any explorer. Then perform a full recovery drill — fresh
junk machine, boot media, steel plates only — re-derive, and sign a
spend of that trivial amount back out (offline signing via the same
outside open-source wallet for now; PSBT flow with dual-machine
byte-identical signature comparison is the roadmap's milestone 3).
Only after the round trip succeeds does the wallet earn real funds
— and only after this repo survives review should "real" mean
anything you'd hate to lose.

## Phase 8 — The rehearsal habit [READY: discipline only]

Annually: verify both steels exist and read cleanly; run a recovery
drill with the trivial amount; confirm your heir instructions still
decode for someone who is not you. Self-error, not theft, is how
most bitcoin dies. This phase is the protocol's real security
budget.
