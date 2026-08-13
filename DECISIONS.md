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
