# HARDCORE.md — extreme variants & open attack surfaces

This file is the agenda for the `experiments` branch. Everything here is
either a purity upgrade someone will demand, or a weakness someone will
find. Pick one, open an issue or PR, and argue.

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
