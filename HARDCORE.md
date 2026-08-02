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
- **Blind brute force**: 1 word in 16 satisfies the checksum. Try
  table-ordered candidate 12th words against an offline wallet until one
  is accepted. No hash step at all. Note: which candidate succeeds leaks
  nothing — the checksum contains no secret.

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
- "Byte-identical RFC 6979 signatures across two machines close nonce
  covert channels."
- "Pre-2006 hardware has no management engine and no radios."
- "1,2,3→0 / 4,5,6→1 is the least error-prone hand mapping."
Break any of these and you improve the protocol more than a thousand
retweets would.
