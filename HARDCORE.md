# HARDCORE.md — extreme variants & open attack surfaces

This file holds purity upgrades, attack surfaces, and **legacy
appendices** preserved from reviewed eras. Mainline ceremony is
PROTOCOL.md on `v0.5-minimal`. Pick an item, open an issue or PR,
and argue.

## 1. Zero-transistor checksum
The only computation left in key *generation* is the 4-bit checksum.
Two ways to delete the computer from even that:
- **Hand SHA-256**: pencil, paper, printed constant tables. A few hours;
  hobbyists have done it. Fine as a one-time ritual, bad as standing
  practice (hand-hash errors are likelier than machine conspiracies).
- **Blind brute force**: exactly one of the 16 words whose first 7 bits
  match your 7 rolled bits satisfies the checksum. Try only those 16, in
  table order, against an offline wallet until one is accepted. No hash
  step at all. Do NOT search all 2048 words: about 1 in 16 of them
  completes some valid mnemonic, so an unrestricted search silently
  replaces your rolled bits with a predictable word near the top of the
  table. Within the correct 16, which candidate succeeds leaks nothing —
  the checksum contains no secret.

## 2. Dice bias (the protocol's most attackable decision)
v0.2 maps rolls directly to bits, so die bias flows into the key.
Defenses in the main protocol: casino-grade dice, the 120-roll tally
test, and the 1-bit-per-roll mapping (bias in a d6 face affects one bit,
not a base-6 digit). Hardcore upgrades to argue about:
- **Von Neumann debiasing**: roll pairs, keep 01→0 / 10→1, discard
  00/11. Provably removes any fixed bias; roughly doubles the rolls.
- **XOR two independent dice** from different stores per bit.
- Bring math: how biased must a die be before 128 mapped bits fall
  below, say, 100 bits of min-entropy? Show your work in the issue.

## 3. 24-word mode
Deleted from main to halve the mistake surface. Trivial patch if you
want it: 23 words from the table + 3 final bits, 8-bit checksum.
Belongs in `experiments` unless someone makes the case 128 bits is
insufficient (that case must survive contact with physics).

## 4. The Python runtime
Our ~150 lines sit on millions of unaudited lines of CPython. Main
protocol answers with dual-machine cross-examination. Hardcore answers
wanted: a port in something radically smaller (C with no libc? Forth?
6502 assembly, for the full vintage thesis?) that still passes the
official vectors byte-for-byte.

## 5. RAM remanence
The main protocol says the secret dies with the power. Cold-boot
attacks say "eventually." Threat window is minutes and requires
physical presence during the ceremony. Proposals for paranoid
mitigation (RAM overwrite pass before shutdown?) welcome — with
evidence they help on 2004-era DRAM, not vibes.

## 6. Things we assert and want attacked
- "Nobody can pre-position an implant in a random dead thrift-store PC."
- "Byte-identical RFC 6979 signatures from two INDEPENDENT
  implementations close nonce covert channels." (Independence is the
  load-bearing word: two copies of the same malicious signer agree on
  the same malicious nonce and pass the check.)
- "Pre-2006 hardware has no management engine and no radios."
- "1,2,3→0 / 4,5,6→1 is the least error-prone hand mapping."
Break any of these and you improve the protocol more than a thousand
retweets would.

## 7. Duress / decoy passphrase
The coercion answer (the wrench attack). Same seed, second
passphrase: a low-value, surrenderable wallet lives behind the decoy
passphrase; the real funds live behind yours. Cryptographically
deniable — a BIP39 passphrase leaves no trace on the seed, so nobody
can prove a second one exists. Honest costs, stated up front: it is
a second checksumless secret with its own silent-failure surface (a
wrong decoy also derives some valid-looking wallet), it adds steel
and rehearsal burden, and it assumes the coercer leaves satisfied —
a wrench wielded by someone who knows about decoys defeats it. This
is a deliberate opt-in, not a default; the mainline ceremony stays
minimal (PROTOCOL.md, Phase 4).

## 8. Geographic 2-of-2 split (moved from mainline)
Seed plates in one location, passphrase plates in another: a thief
must compromise two sites to spend. What it costs: loss probability
rises (any unreachable site strands the funds — which is why every
factor must still be stamped ×2, the redundancy rule bends for
nothing), and inheritance now requires someone who is not you to
find, reach, and understand both sites. Mainline v0.3 keeps both
factors reachable by you; the split is for people whose threat model
earns it.

---

## Appendix A — v0.3.4 junk-PC build (legacy-reviewed)

Preserved for historians and for anyone who still wants the thrift-store
ceremony. **Not mainline.** Status: legacy-reviewed as of the v0.3.4
tag on `main`.

- Two unrelated junk PCs, capability-stripped (no radios, disk
  unplugged), booted from write-once media.
- Dice → word table → twelve-word seed ceremony with optional second
  factor; dual-machine byte-identical derivation; steel plates;
  annual rehearsal.
- Honest bound stated at the time: identical machines are a fault
  detector; independent implementations are required to catch lies.
- Do not mix this appendix with v0.5 plates or v0.5 device images.

## Appendix B — School-calculator build (benchmarks)

A purity ask: run birth math on something smaller than a Pi Pico.

**Measured (desktop reference harness, not the calculator itself) —
predicted on-device — falsify this:**

| Operation | Desktop CPython (this repo) | 32-bit small-int note |
|-----------|----------------------------:|------------------------|
| SHA-256 of 32 bytes | sub-millisecond | native word ops |
| secp256k1 scalar mul (Jacobian, Pico lineage) | ~tens of ms | 256-bit ints are multi-limb on 32-bit |
| Full birth (key+pad→address) | < 1 s typical | dominated by two scalar muls |

**32-bit small-int analysis:** MicroPython on RP2040 uses arbitrary
precision; school-calculator BASIC often does not. Any port to a
machine with 32-bit signed ints must implement 256-bit limbs
explicitly. The threat is not speed — it is silent overflow. A port
that cannot pass `tests/vectors_test.py` is not a port.

## Appendix C — BIP39-compatible variant (interop diehards)

Mainline deleted BIP39. If you require wallet interop:

- Map 128 or 256 dice bits through the standard wordlist and
  checksum (the old `dice2words.py` approach).
- Keep dual-device agreement on the derived Taproot address.
- Accept that you reintroduce PBKDF2, wordlists, and vendor-shaped
  recovery UX — the costs DECISIONS.md rejected.
- This variant is not maintained on `v0.5-minimal`. Ship it as a
  fork or a clearly labeled extra.

## Appendix D — Multi-key privacy mitigation

v0.5 reuses one address. That links payments permanently.

Mitigation: roll **several independent keys** (full 512-roll ceremony
each). Stamp separate plate pairs. Use a new key when you want an
unlinkable receive path. No invented derivation. No account trees.

## Appendix E — Third verifier (retired 2026-08-05)

**Retired.** Bitcoin Core is now the senior referee at birth
(`rawtr()` on public data only); see DECISIONS.md. A third
ceremony board is redundant for that role.

Historical note (kept for context): a third device that must agree
with both lineages was once proposed. Constraint then: it must
differ from **both** existing lineages. The Duo is already RISC-V /
China-origin. A third verifier would have been, for example, a
different-vendor ARM or MIPS part — **not** another RISC-V board
that collapses the ISA diversity claim.
