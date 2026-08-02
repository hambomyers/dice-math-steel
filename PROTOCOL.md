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
- **A sledgehammer.** Optional and ceremonial (see Phase 6);
  traditional nonetheless.

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

## Phase 2 — Author the key [READY: paper only, zero chips]

Alone. Curtains drawn. No phones in the room — not silenced, absent.

```
 ONE WORD  =  11 ROLLS.  DO THIS 11 TIMES.

 roll ─────────────────────────────────────────────┐
   ▼                                               │
 ┌──────────────────────────────────────────────┐  │
 │  see 1, 2, or 3  →  write 0                  │  │
 │  see 4, 5, or 6  →  write 1                  │  │
 └──────────────────────────────────────────────┘  │
   │                                               │
   │  11 bits yet?  ── no ─────────────────────────┘
   │
   yes
   ▼
 ┌──────────────────────────────────────────────┐
 │  read your 11 bits left to right             │
 │  find that exact pattern in table.txt        │
 │  write the word next to it                   │
 └──────────────────────────────────────────────┘
   │
   ▼
 ┌──────────────────────────────────────────────┐
 │  CHECK IT: cover the word. read the bits     │
 │  off your sheet again. look it up again.     │
 │  same word? then move on.                    │
 └──────────────────────────────────────────────┘

 WORKED EXAMPLE — word 1

   rolls:   3  5  1  6  2  2  4  1  3  6  5
   bits:    0  1  0  1  0  0  1  0  0  1  1
   pattern: 01010010011
   table.txt says:  → (the word on that line)

 EXAMPLE ONLY. Your dice, not these. Never reuse
 any pattern printed in any document, ever.
```

```
 THE FULL AUTHORING RUN

  words 1–11      11 rolls each  = 121 rolls  →  11 words
  final 7 bits     7 rolls        =   7 rolls  →  half of word 12
                                    ─────────
                                     128 rolls = 128 bits, all yours

  then, and only then, a machine gets involved:
  it computes the checksum and names word 12.
  it has zero choices. you authored everything.
```

## Phase 3 — The forced move [READY: dice2words.py]

Boot one junk machine from the CD-R (hard drive unplugged). Run:

    python3 dice2words.py --test     # must pass before anything else
    python3 dice2words.py finish     # enter your 11 words + 7 bits

The machine names the single word that can legally complete your
sequence — it computes the checksum and chooses nothing. One
machine suffices here, because this output is loud: a wrong word is
an invalid mnemonic every wallet on earth rejects. The second check
is not a second machine but the **mandatory confirmation of all 12
words in an unrelated wallet app**, which rejects an invalid
checksum instantly. Run `check` with all 12 words; it must say
VALID. Any failure: stop, diagnose, restart Phase 2 with fresh
rolls if in doubt. (Two machines are reserved for silent outputs —
derivation, signing — where a wrong answer looks right. See
Phase 5.)

Optional purity variants (hand-computed SHA-256, blind brute force
of the final word) are in HARDCORE.md §1.

## Phase 4 — Passphrase (optional) [READY: paper only]

Optional as of v0.3 — the mainline stays minimal. A passphrase buys
a second factor at the price of a second checksumless secret;
decide deliberately. If you use one, dice it from fresh rolls
(e.g., five words via the same table, or Diceware). Never a
human-invented phrase. Five words (~55–64 bits) is the floor, not
the target; six buys comfortable margin: the passphrase must stand
alone against an attacker who already holds the seed plates. And
know this plainly: **a BIP39 passphrase has NO checksum.** A wrong
passphrase does not fail — it silently derives a valid, empty
wallet. That is why the steel-sourced check in Phase 6 exists; do
not skip it. Record on paper for now. (A duress/decoy passphrase —
the coercion answer — is a deliberate variant: HARDCORE.md §7.)

## Phase 5 — Addresses and verification [GAP: uses outside tools]

This repo does not yet include key derivation (see the Roadmap in
README.md). Until it does, use a well-known open-source wallet, run
offline on both ceremony machines from your verified boot media —
e.g., Electrum in offline mode, or SeedSigner/Krux code — to:

1. Enter the 12 words (+ passphrase, if you chose one) on machine
   #1; derive the account xpub and the first 5–10 receiving
   addresses.
2. Repeat independently on machine #2. **Every address must match.**
   This output is silent — a wrong address looks exactly like a
   right one — which is why this step, unlike Phase 3, gets two
   machines.
3. Hand-copy the addresses to paper (both machines' screens agree,
   so copy from one and verify against the other). On the same
   sheet, record the derivation path (BIP84) and the wallet/tool
   and version used — none of that is secret, and it prevents a
   future path mismatch. This sheet becomes your permanent receive
   list — the root of truth: verified once, then trusted, so no
   screen sits in your receive path again.
4. Optional third check: reconstruct watch-only from the xpub on an
   ordinary online machine later; addresses must match again.

The address sheet cannot spend a coin, but guard it anyway: lose it
and you're back to trusting screens; show it and you've shown your
balances.

## Phase 6 — Steel, prove from steel, then death [GAP: the steel check uses Phase 5's outside tools]

1. Stamp every factor twice: two plates for the 12 words, and two
   more for the passphrase if you chose one. No single fire, flood,
   or forgotten hiding hole may be fatal. Verify each stamping
   against paper twice, out loud.
2. Prove from steel — before burning anything. Turn the paper face
   down. Reading only from the plates, re-enter the words (and
   passphrase) in a SECOND, different wallet app and re-derive
   address #1. It must match the printed sheet. From the plates,
   not the paper: a paper-sourced check is circular and proves
   nothing about the steel. The different app matters too: it
   catches wallet-specific divergence such as NFC/NFKD passphrase
   normalization. Honest label: this is a point-in-time check, not
   a standing checksum — steel has no self-test.
3. Only now burn all paper that carries secrets (rolls, words,
   passphrase). The address sheet is not a secret and survives.
4. Power off both machines. The secret existed only in RAM and is
   now fading charge. The sledgehammer is optional — ritual, not
   load-bearing: there is nothing left to kill. If you swing it,
   recycle the wreckage yourself.
5. Store the duplicate plates apart from each other, but keep both
   reachable by you. The geographic 2-of-2 split (seed and
   passphrase in locations that can never meet) is an advanced,
   deliberate opt-in with real loss and inheritance costs:
   HARDCORE.md §8.

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
