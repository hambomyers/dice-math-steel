# Changelog

## v0.6 — August 2026

Docs and tools only. `src/` and `tests/` unchanged.

### Fixed

- Signet recovery table labeled Sparrow as tested. It was
  source inspection. Row is now untested; Electrum row says
  the wallet was not launched.
- README STATUS and the signet transcript now state that no
  signature from this protocol has been accepted by any
  Bitcoin network. Local signing is not a ledger ruling.

- Whitepaper §7 claimed stacking plates *is* the XOR. Stacking
  punched steel in light computes AND, not XOR. The plates encode
  a one-time pad; recovery is pencil on a worksheet.
  ([c9c185e](https://github.com/hambomyers/dice-math-steel/commit/c9c185e2ff3d455bc8d07001fdd17764c238d117))
- Dual Python files were described as independent implementations.
  They share a MicroPython/CPython interpreter; bug surfaces are
  correlated. Vector-pass is not an audit.
  ([6e00b99](https://github.com/hambomyers/dice-math-steel/commit/6e00b9930d18aaf6f656e575785465d03cfda2e1))
- README slogan "no trusted devices" overclaimed. Devices are
  used; they are disbelieved and graded.
  ([e857b24](https://github.com/hambomyers/dice-math-steel/commit/e857b2458ee42bea615e2c4d407ac31f1bc9f7d7))

### Changed

- Entropy: one die, two sequential throws, 6×6 card (~117 throws
  per 256-bit number). Worksheet bits enter the existing keypad
  as 1 or 4. `rolls_to_int` unchanged.
  ([45ff44a](https://github.com/hambomyers/dice-math-steel/commit/45ff44a9ce1de99a98d4a023efbb01d772fea684))
- Paranoid mapping is a pre-throw fork (256 throws, half-split),
  not a footnote on the card.
  ([e857b24](https://github.com/hambomyers/dice-math-steel/commit/e857b2458ee42bea615e2c4d407ac31f1bc9f7d7))
- Plates: 16×16, gutters, notch, ceremony ID, two-pass, both
  symbols marked. No parity. Plate B words labeled ADDRESS
  FINGERPRINT.
  ([a445c33](https://github.com/hambomyers/dice-math-steel/commit/a445c33138ac83c4f35fd84c7af4553f0c1c497e))
- Recovery: paper worksheet as jig; never steel to steel.
  ([a7be799](https://github.com/hambomyers/dice-math-steel/commit/a7be7996fb423cbee98502c5997d00aa998b5845))
- README opens with four sentences. Birth and spend labeled
  UNREVIEWED. One-page ASCII figure.
  ([ed31e1e](https://github.com/hambomyers/dice-math-steel/commit/ed31e1e0414d7f12502ef8da6e49c9e07e2d78a9),
  [753c04a](https://github.com/hambomyers/dice-math-steel/commit/753c04ae8275f7c9d1840059045b3c521431fde8))
- Phase 3 and Phase 6 tagged UNREVIEWED. Every phase has a status.
- Core birth check is `tr(P)` (internal key), not `rawtr(Q)`.
  Same address; drops Core's documented `rawtr()` caveat.
- `docs/rehearsal-signet.md` records a 2026-08-12 check of
  which tools recover a raw scalar (Core, Sparrow, Electrum,
  embit).
  ([e857b24](https://github.com/hambomyers/dice-math-steel/commit/e857b2458ee42bea615e2c4d407ac31f1bc9f7d7))

### Added

- `docs/dice-card.md` + `tools/make_card.py` (36 cells, 4 REROLL,
  regenerable).
  ([46380ff](https://github.com/hambomyers/dice-math-steel/commit/46380ffc11d84ff37c78a7eac76689739356412c))
- `docs/worksheet.md` (three 16×16 grids).
  ([30d0a38](https://github.com/hambomyers/dice-math-steel/commit/30d0a38a15dfc4fda3a08ddb73946efe459a295c))
- `tools/recover.py` imports both `src/` lineages; prints plate
  cells it corrected; `--self-test` covers distance 1/2/3 and
  fail-clean at max-flips 3.
  ([c04a56e](https://github.com/hambomyers/dice-math-steel/commit/c04a56e71767941145980673de76d8ecaccd53a8),
  [afdfe13](https://github.com/hambomyers/dice-math-steel/commit/afdfe13ab43cb217f1022534811d30f1d68d65cd))
- Optional KEY READING appendix: 25 words, marker `steel`,
  distinct from ADDRESS FINGERPRINT.
  ([505dfc5](https://github.com/hambomyers/dice-math-steel/commit/505dfc5e758242460ac5dd5eeaff367eaa7f28d6))
- `CREDITS.md` — BIPs, pinned vectors, Core `rawtr()`, Vernam/
  Shannon, BIP39 wordlist origin, Diceware prior art.
  ([4ddad0f](https://github.com/hambomyers/dice-math-steel/commit/4ddad0f0fba7012c31f5b481fd25f670cadb1170))

### Removed

- Phase 1 aggregate-split tally (~120 throws had no power; it
  manufactured false confidence).
  ([45ff44a](https://github.com/hambomyers/dice-math-steel/commit/45ff44a9ce1de99a98d4a023efbb01d772fea684))
- Unused BIP39 `table.txt` and `vectors.json` (archived).
  `english.txt` kept — it feeds the address fingerprint.
  ([407c1f1](https://github.com/hambomyers/dice-math-steel/commit/407c1f1799e407329a9cabd3000e33143509a2db))
- `business-plan-PRIVATE.md` was never in git; deleted from the
  working tree and gitignored so it cannot be added.

## v0.3.4 — August 2026
- Version self-descriptions deleted from PROTOCOL.md and
  dice2words.py headers — CHANGELOG carries versions; a number in
  a file header goes stale every commit.
- `check_docs.py` added: fails the commit on retracted wording,
  disagreeing numbers, missing image text-twins, or a file naming
  its own version. Run beside `dice2words.py --test`.
- CONTRIBUTING.md: when a claim changes, grep the repo for the old
  wording; image words come from committed text, never hand-edits.

## v0.3.3 — August 2026
- Receive sheet 5–10 -> 20, with the reason stated: reuse links
  payments permanently, and 20 matches the wallet gap limit.
- Both launch images regenerated. The reply card claimed 50
  addresses and "100+ rolls" where the key is 128, and carried the
  pre-v0.3 "never trusted, only cross-examined" overclaim; the
  poster repeated those and still footed itself v0.2. The poster is
  now claim-free — motto and pointer only — so it cannot go stale
  again.
- img/reply-card.txt and img/poster.txt added so claims inside
  images are greppable.

## v0.3-draft — August 2026
Changes from post-launch adversarial review (red-team → adjudication
→ steelman). Critics credited in the README as findings land.
- Honesty reframe: dual identical machines relabeled a fault
  detector, not a lie detector — two copies of the same CD-R image
  agree on the same wrong answer. Catching lies requires independent
  implementations, now a hard requirement for the signing milestone.
- Loud/silent distinction adopted: loud outputs (invalid checksum,
  rejected everywhere) get one machine — the forced move now uses a
  single PC plus the mandatory unrelated-wallet confirmation; silent
  outputs (derivation, signing) keep two.
- Passphrase now optional, diced if used. Stated plainly that a
  BIP39 passphrase has no checksum: a wrong one silently derives a
  valid, empty wallet.
- Ceremony reorder: paper burns only after a recovery check sourced
  from the stamped steel re-derives address #1 in a second wallet
  app and matches the printed sheet.
- Redundancy rule: every factor stamped ×2. Geographic 2-of-2 split
  and duress/decoy passphrase moved to HARDCORE.md as deliberate
  opt-ins.
- Dice test now measures the aggregate {1,2,3} vs {4,5,6} split;
  relabeled an assurance check, not an entropy guarantee.
- Address sheet: 5–10 hand-copied addresses, with derivation path
  and tool version recorded on the sheet; sledgehammer optional.

## v0.2 — August 2026
- Authorship inverted: the human derives all 128 entropy bits at a
  table with dice and the printed lookup table (`table.txt`); the
  program is demoted to `finish` (compute the forced checksum word)
  and `check` (proofread) — zero choices in either.
- Deleted 24-word mode (half the modes, half the mistakes) and
  hash-whitening of dice (machine-authored keys judged a worse
  enemy than measurable dice bias — see HARDCORE.md §2).
- Added round-trip test proving the kitchen-table protocol and
  standard BIP39 are identical mathematics.
- Added PROTOCOL.md (full ceremony), HARDCORE.md, CONTRIBUTING.md,
  SECURITY.md, table.txt.
- v0.1 preserved in `archive/`.

## v0.1 — August 2026
- Initial rough draft: dice rolls hashed to entropy, full mnemonic
  generated by machine, verified against official BIP39 vectors.
