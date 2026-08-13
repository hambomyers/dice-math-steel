# DECISIONS.md — reversals from v0.3.4

Every change below deletes a past position on purpose. Date is the
v0.5-minimal pivot day. Old position is what v0.3.4 shipped. New
position is what this branch requires. Reason is why the old one
lost.

---

## 2026-08-03 — BIP39 deleted

- **Old:** Dice map into BIP39 mnemonics; the machine names word 12;
  interop with every wallet that speaks BIP39.
- **New:** The private key is a dice-rolled 256-bit integer `k`
  (0 < k < n). No BIP39. No words. No PBKDF2. No BIP32. No
  passphrase. No xpub.
- **Reason:** The interop stack served vendors we do not ask
  permission from. Dice entropy needs no stretching. Words and
  checksum theater were load for someone else's product line.

## 2026-08-03 — passphrase → one-time pad

- **Old:** Optional BIP39 passphrase, diced, stamped separately;
  practical split; no checksum on the passphrase (the silent-fail
  hole Phase 6 tried to catch by steel re-derivation).
- **New:** Plate A holds pad `p` (dice-rolled). Plate B holds
  `k XOR p`, plus the receive address (permanent checksum) and a
  4-word fingerprint. Each plate alone is information-theoretically
  worthless.
- **Reason:** Upgrades a practical split to an information-theoretic
  one. Kills the no-checksum mis-stamp hole: the address on plate B
  is the checksum any future re-derivation must reproduce.

## 2026-08-03 — junk PCs → two cheap boards, different ISA/nation/stack

- **Old:** Two thrift-store junk PCs, preferably identical-absent
  capabilities, booted from write-once CD-R. Honest label: identical
  machines are a fault detector, not a lie detector.
- **New:** Device A is a Raspberry Pi Pico (RP2040 — not Pico W).
  Device B is a Milk-V Duo base model (not root Duo S). Different
  ISA, different nation of origin, different software stack. No wire
  ever connects A and B.
- **Reason:** Identical machines were fault detectors. Independence
  is the requirement. Two strangers who must agree.

## 2026-08-03 — "loud vs silent" doctrine → "the address is the checksum"

- **Old:** Loud outputs (invalid mnemonic) need one machine; silent
  outputs (addresses, signatures) need two, byte-identical or stop.
- **New:** There is one key and one Taproot address. That address,
  stamped on plate B, is the permanent checksum. Both devices must
  speak the same address and the same 4-word fingerprint aloud
  before steel is stamped. Signatures must be byte-identical across
  both devices.
- **Reason:** Without BIP39 there is no loud checksum word. The
  address replaces it. Spoken fingerprints replace hex-vs-hex
  eyeballing (operator error is threat #1).

## 2026-08-03 — "hardware short-lived" → "hardware amnesiac"

- **Old:** Ceremony machines hold the secret in RAM for minutes,
  then are destroyed (sledge optional but traditional).
- **New:** Reflash both devices from this repo before every
  ceremony. After key entry, neither device connects to another
  computer. The Pico's USB is power-only post-flash. The Duo's SD
  card carries only public data. Destruction is optional catharsis,
  not a security step.
- **Reason:** Reflash-per-ceremony replaces destruction. Amnesia is
  cheaper and repeatable. The hammer remains available as ritual.

## 2026-08-03 — PSBT → fixed template

- **Old:** Roadmap milestone: PSBT signing with RFC 6979
  deterministic nonces across two independent implementations.
- **New:** Transactions have exactly one fixed template: N inputs
  (all owned by the one key) → 1 destination output + optional 1
  change output back to the same address. No PSBT. Unsigned tx
  arrives on SD as documented JSON. Both devices build the BIP341
  sighash, sign with BIP340 (`aux_rand` = 32 zero bytes), and must
  emit byte-identical signatures.
- **Reason:** Generality was bloat. A tired human in a garage needs
  one shape of transaction, screen-confirmed, not a PSBT dialect.

## 2026-08-03 — 20 addresses → 1 reused address

- **Old:** Hand-copied sheet of 20 receive addresses (BIP84), used
  in order, never reused; gap-limit aligned.
- **New:** One key, one Taproot key-path address, reused. Address
  reuse is a stated, accepted privacy cost. Multi-key mitigation
  (roll several independent keys) lives in HARDCORE.md.
- **Reason:** Derivation without BIP32 would be invented crypto. We
  do not invent crypto. One address is honest about that limit.

---

## Implementation independence (mandatory honesty)

Both `src/birth_pico.py` and `src/birth_duo.py` in this branch were
written by the same model in one session. That is not independence.
True independence requires a second human author. Implementation #2
(`birth_duo.py`, `sign_duo.py`) is marked **seat-warmer pending
independent rewrite**. Help-wanted item #1 in the README.

## 2026-08-05 — Bitcoin Core enrolled as senior referee

- **Old:** Birth-day verification is two stranger-machines agreeing
  on address and fingerprint; a third verifier (different ISA /
  vendor from both lineages) lived in HARDCORE.md Appendix E.
- **New:** Birth-day verification includes Bitcoin Core re-deriving
  the address from the public key via a `rawtr()` descriptor
  (public data only). Core is the third lineage: hundreds of
  authors, 17 years of hostile review. The third-verifier hardware
  appendix is retired as redundant.
- **Reason:** Core already is the senior referee the third-board
  appendix was trying to approximate. Using it on public data only
  adds a reviewed lineage without another ceremony keyboard.

## 2026-08-05 — Witness machine deferred to spend day

- **Old:** Birth requires two devices (Pico and Duo) entering the
  same 512 rolls and agreeing before steel is stamped.
- **New:** Birth requires **one** device. Its homework is graded by
  Core plus a $5 ledger round-trip; re-derivation from stamped
  steel before real funding catches entry typos. The second
  stranger-machine is purchased and used only for spending, where
  it witnesses the nonce (byte-identical BIP340 signatures).
- **Reason:** Halves ceremony hardware and halves the 512-roll
  double-entry — a direct strike at threat #1, operator error.

## 2026-08-12 — Whitepaper §7: plates encode XOR; they do not compute it

- **Old:** Stacking two random-dot sheets "is not a metaphor for
  the math; it is the math."
- **New:** One plate is information-theoretically worthless, like
  one sheet of visual-crypto dots. The plates *encode* a one-time
  pad. Recovery is pencil-on-paper. Punched steel stacked in
  light computes AND, not XOR.
- **Reason:** The old sentence was false as written. Honesty about
  the analogy is cheaper than a pretty lie.

## 2026-08-12 — BIP39 leftovers: archive table and vectors; keep english.txt

- **Old:** `table.txt` and `vectors.json` sat at repo root after
  the BIP39 stack was retired.
- **New:** Both files live in `archive/`. `english.txt` stays at
  root: plate B's 4-word address fingerprint is drawn from that
  2048-word list. `src/` does not open the file (it takes a
  wordlist argument); the ceremony still needs the committed list.
- **Reason:** `grep` of `src/` found no `open()` of these three
  files. Archiving a load-bearing wordlist would break the
  fingerprint. Archiving unused BIP39 test/lookup files would not.

## 2026-08-12 — Shared interpreter is not independence

- **Old:** Two codebases on Pico and Duo were described as
  independent implementations.
- **New:** Both lineages are Python. A shared interpreter
  correlates bug surfaces. Vector-pass is not "verified." The
  open issue is a bare-metal C second implementation.
- **Reason:** Claiming independence we do not have is worse than
  an honest caveat.

## 2026-08-12 — One die, two throws, 6×6 card

- **Old:** 256 rolls mapped `{1,2,3}→0 / {4,5,6}→1` for the key,
  same again for the pad (512 rolls). Two or more dice allowed.
- **New:** One die, thrown twice in sequence (row, then column)
  on a 36-cell card. 32 unique 5-bit cells, 4 REROLL. Expected
  ≈117 throws per 256-bit number. Worksheet bits enter the
  existing keypad as 1 (bit 0) or 4 (bit 1). `src/` unchanged.
- **Reason:** Sequential throws of one die remove an unmeasured
  collision-correlation. The card is a glance, not base-six in
  the head. The device still consumes a 256-bit integer.

## 2026-08-12 — Tally test deleted

- **Old:** Phase 1 tallied ~120 rolls on the {1,2,3} vs {4,5,6}
  split and talked about "128 bits of min-entropy."
- **New:** Physical inspection only (sharp edges, flush pips, no
  visible wear, translucent stock; optional salt-water float).
  No min-entropy number in the ceremony.
- **Reason:** At ~120 throws there is essentially no power to
  detect bias small enough to matter. A ritual that manufactures
  false confidence is worse than no test.

## 2026-08-12 — Plate rules: 16×16, two-pass, both symbols

- **Old:** Stamp "the pad" and "k XOR p + address + fingerprint"
  with no grid, no orientation mark, no ceremony ID, and no
  stated strike order.
- **New:** 16×16 with gutters every 4; corner notch; 4-character
  ceremony ID on both plates; two-pass stamping (all zeros, then
  all ones); both symbols always marked; no parity, no third
  symbol; plate B's four words stamped under ADDRESS FINGERPRINT.
- **Reason:** A 180° rotation is silent and catastrophic. Mixing
  plates across ceremonies is a live failure. Blanks are not
  zeros. Strike-order is a microphone. The address already
  corrects the key, so parity punches would be redundant and
  would break two-pass. Confusing the fingerprint with a key
  reading is catastrophic in one direction.

## 2026-08-12 — Recovery: paper jig, never steel to steel

- **Old:** "Line up the plates" / "XOR the plates" as if stacking
  steel computed the pad.
- **New:** Transcribe onto a printed 16×16 worksheet, one row at
  a time through a slotted index card. Same-or-different on
  paper. Verify against the stamped address before trusting `k`.
- **Reason:** Punched steel stacked in light computes AND, not
  XOR. The worksheet is the jig. Operator error is threat #1.

## 2026-08-12 — 36-cell card, not a giant lookup table

- **Old:** One bit per throw, `{1,2,3}→0 / {4,5,6}→1`.
- **New:** Printed 6×6 card, generated by `tools/make_card.py`.
  32 unique 5-bit cells, 4 REROLL. Paranoid mode printed on the
  card. The table is 36 cells because a lookup sits inside the
  cryptographic chain and must be hand-checkable.
- **Reason:** Auditability over 18 fewer throws. Same artifact
  degrades to the old mapping if you ignore the columns.

## 2026-08-12 — Printed 16×16 worksheet is the jig

- **Old:** Record rolls on undifferentiated paper; XOR "the
  plates."
- **New:** Three labeled 16×16 grids (pad, xor, key), gutters
  every 4, ceremony ID, notch reminder, keypad encoding on the
  sheet.
- **Reason:** Speakable bit addresses. Alignment is printed, not
  guessed. A tired heir can finish.

## 2026-08-12 — Error correction lives in recover.py, not in punches

- **Old:** (none — v0.5 had no Hamming search.)
- **New:** `tools/recover.py` XORs the plates, imports `p2tr_address`
  from both `src/` lineages, and searches distance 0/1/2 (3
  optional) against the stamped address.
- **Reason:** The address is already a 256-bit correcting code
  over the key. Parity punches would be redundant and would
  break two-pass stamping. The search has zero degrees of
  freedom: only the true key hits the stamp.

## 2026-08-12 — Four-sentence README

- **Old:** README led with four verbs and a STATUS that called
  vector-pass "cross-verified by three independent
  implementations."
- **New:** README opens with the four-sentence statement. Birth
  and spend code is labeled UNREVIEWED. Vector-pass is not an
  audit.
- **Reason:** If it is not in those four sentences, it is
  appendix, not protocol. "Verified" was a word we had not
  earned.

## 2026-08-12 — One-page machine figure

- **Old:** README "four layers" box (BORN / CHECKED / KEPT /
  SPENT).
- **New:** One ASCII page: entropy card, pad split, 16×16 plates,
  exactly two silicon contacts, both UNREVIEWED.
- **Reason:** A tired reader should see the whole machine before
  any appendix.

## 2026-08-12 — Words are a reading, optional, 25 long

- **Old:** (v0.5 deleted BIP39; no spoken-key channel remained.)
- **New:** Optional KEY READING appendix. 25 words, marker `steel`
  at position one, leftover 3 bits padded. Distinct from plate B's
  ADDRESS FINGERPRINT. Steel stays binary.
- **Reason:** 25 is rejected by every BIP39 wallet. Documentation
  alone would not stop an heir feeding 24 words into an empty
  wallet. The fingerprint is public; KEY READING is the key.

## 2026-08-12 — recover.py names the punches it flipped

- **Old:** A match printed distance and `k`. No grid cells.
- **New:** A match prints `row R col C` for every corrected bit
  (16×16 labels 0–F). Over-corruption at distance >3 fails clean
  and names the other plate copy. Search is a convenience, not a
  guarantee.
- **Reason:** Without indices a successful recovery is
  unfalsifiable to the person holding the steel. If a named mark
  is clean, stop — something else is wrong.

## 2026-08-12 — Paranoid mode is a fork, not a footnote

- **Old:** Five-bit procedure first; paranoid mapping as a
  postscript "(printed on the card)."
- **New:** Choose standard (~117 throws, 5-bit) or paranoid (256
  throws, half-split) before the first throw. Same 256-bit
  worksheet object. Do not switch mid-number.
- **Reason:** Bias-robustness is a posture, not a fallback you
  discover after the 5-bit path is already complete. Efficiency
  and bias-robustness trade against each other; the operator
  picks which side they are on.

## 2026-08-12 — "No trusted devices" overclaimed

- **Old:** README: "Cold storage with no trusted devices."
- **New:** "no believed devices — every device graded."
- **Reason:** Devices are used. They are disbelieved and graded.
  Residual trust already said so; the slogan must survive that
  reading.

## 2026-08-12 — Whitepaper brought to PROTOCOL parity

- **Old:** github.io still described one-bit mapping and conceptual
  plates after `main` had moved to the 6×6 card and 16×16 rules.
  The README linked that build with no warning. Birth board was
  "$4" in the paper and "~$15 predicted" in README.
- **New:** Whitepaper Fig. 1a–c match PROTOCOL: mapping chosen
  before the first throw, 16×16 plates, UNREVIEWED on birth and
  spend in the figure, worksheet jig, search limit. Board cost
  is ~$15 predicted in both places.
- **Reason:** The front door lagged. A reader tracking the project
  should know it lagged, and should not be sent to a stale
  ceremony. Two published prices for one checkable number is
  exactly the class of error this repo forbids.

## 2026-08-12 — Core check uses `tr()`, not `rawtr()`

- **Old:** Birth-day Core check was `deriveaddresses "rawtr(Q)"`
  with the device's x-only **output** public key.
- **New:** Birth-day Core check is `tr(P)` with the device's
  x-only **internal** public key (checksum via
  `getdescriptorinfo`). Recovery imports `tr(<WIF>)`.
- **Address unchanged.** On signet, Bitcoin Core 29.4 returned
  the same bech32m string for `tr(<WIF>)`, `tr(P)`, and
  `rawtr(Q)`, matching the device's `p2tr_address`. Feeding `Q`
  to `tr()` double-tweaks and disagrees — so the swap is the
  descriptor string and which hex the operator copies, not the
  stamped address. Device code is untouched.
- **Reason:** Core's own `descriptors.md` documents `rawtr(KEY)`
  downsides, including being unable to prove no hidden script
  path exists, and to use it at your own risk. Optech notes
  `rawtr` is for keys used without a tweak, which BIP341 does
  not recommend. This protocol applies the tweak
  (`Q = P + H_TapTweak(P)·G`). `tr()` is the BIP341-standard
  form, can sign rather than only watch, and drops that
  Core-documented caveat.
