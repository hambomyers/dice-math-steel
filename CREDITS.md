# Credits

Specifications this repo conforms to, and prior art it did not invent.
Conformance on pinned test vectors is not a third-party audit.
See README STATUS.

## BIP340 / BIP341 / BIP350

Schnorr signatures, Taproot key-path spends, and bech32m addresses.

- **BIP340** — Pieter Wuille, Jonas Nick, Tim Ruffing.
  [bip-0340.mediawiki](https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki)
- **BIP341** — Pieter Wuille, Greg Maxwell, Andrew Poelstra, Jonas
  Nick, Anthony Towns.
  [bip-0341.mediawiki](https://github.com/bitcoin/bips/blob/master/bip-0341.mediawiki)
- **BIP350** — Pieter Wuille, Greg Maxwell.
  [bip-0350.mediawiki](https://github.com/bitcoin/bips/blob/master/bip-0350.mediawiki)

BIPs are published under the BSD-2-Clause license of
[bitcoin/bips](https://github.com/bitcoin/bips). Compatible with
this repo's MIT license. We implement; we do not copy BIP prose.

## Pinned test vectors

Files under `tests/vectors/`. Hashes in `tests/vectors/SHA256SUMS`.
They were not authored here.

| File | Pin (SHA-256) | Upstream |
|------|----------------|----------|
| `bip340_test_vectors.csv` | `34c9d1d9…db851c2d` | [bitcoin/bips bip-0340/test-vectors.csv](https://github.com/bitcoin/bips/blob/master/bip-0340/test-vectors.csv) |
| `bip341_wallet_test_vectors.json` | `403e19fb…31d37f` | [bitcoin/bips bip-0341/wallet-test-vectors.json](https://github.com/bitcoin/bips/blob/master/bip-0341/wallet-test-vectors.json) |
| `bip350_bech32m_vectors.json` | `00d5f8f1…0f4ebc` | assembled from BIP350 mediawiki sections; see the file's `comment` field |
| `sipa_bech32_tests.py` | `0d1cee7f…419e1c` | [sipa/bech32 ref/python/tests.py](https://github.com/sipa/bech32/blob/master/ref/python/tests.py) |

`python3 tests/vectors_test.py` refuses to run if a pin drifts.

## Bitcoin Core

Senior referee at birth. On public data only:

    bitcoin-cli getdescriptorinfo "tr(P)"
    bitcoin-cli deriveaddresses "tr(P)#<checksum>"

`tr()` is Core's BIP341-standard descriptor for a Taproot
key-path output
([output script descriptors](https://github.com/bitcoin/bitcoin/blob/master/doc/descriptors.md)).
`P` is the device's x-only internal public key. The chain
grades the spend.

## One-time pad

Plate A holds `p`. Plate B holds `k ⊕ p`. One plate is
information-theoretically worthless.

- Gilbert Vernam, 1917 — the pad.
- Claude Shannon, "Communication Theory of Secrecy Systems"
  (1949) — perfect secrecy when the pad is uniform, as long as
  the message, and never reused.

The plates *encode* that mathematics. They are not a physical
computer for it.

## BIP39 English wordlist (`english.txt`)

2,048 words, alphabetical, unique first-four letters. Live
protocol: plate B's **ADDRESS FINGERPRINT** (four words) and the
optional KEY READING appendix. Not a leftover.

- **BIP39** — Marek Palatinus, Pavol Rusnak, Aaron Voisine, Sean
  Bowe. [bip-0039.mediawiki](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki)
- Wordlist: [bip-0039/english.txt](https://github.com/bitcoin/bips/blob/master/bip-0039/english.txt)
  under the bitcoin/bips BSD-2-Clause license.

We do not use BIP39 mnemonics, PBKDF2, or BIP32. The list is a
spoken encoding of bits already chosen by dice. 25-word KEY
READING is structurally rejected by BIP39 wallets (12/15/18/21/24
only).

## Diceware

Arnold G. Reinhold, 1995. Prior art for mapping dice throws onto
a printed word table. The 36-cell card cites the *idea* and
rejects the *size*: a 7,776-row table cannot be audited by a
tired human in two minutes, and a lookup sits inside the
cryptographic chain. See `docs/dice-card.md` and DECISIONS.md.

## Other ceremony prior art

Named in README: the Glacier Protocol (mandatory rehearsal),
SeedSigner and Krux (stateless DIY signing), SeedPicker and the
printed dice-table tradition, and dice-authored keys generally.
