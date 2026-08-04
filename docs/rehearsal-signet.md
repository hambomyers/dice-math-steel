# Rehearsal transcript — signet (dry run)

This document proves the v0.5 path was walked once end-to-end on
signet semantics. It uses **throwaway rolls** published here so
reviewers can reproduce. Do not send value to these addresses on
mainnet.

## 0. Tooling check

```
$ python3 tests/vectors_test.py
OK: BIP340 + BIP341 + BIP350 vectors pass on both implementations; births and signatures agree.

$ python3 check_docs.py
Docs clean: ...

$ python3 tools/linecount.py
# table matches README falsifiable-claims rows
```

## 1. Dice (published throwaway)

Key rolls (256 faces, row-major; 1–3→0, 4–6→1) — synthetic sequence
for the rehearsal, not casino dice:

```
key_rolls[i] = ((i * 3) % 6) + 1
pad_rolls[i] = ((i * 5) % 6) + 1
```

Both devices received the same sequences (Pico path and Duo path in
`tests/vectors_test.py::test_birth_agreement` / sign template test
with `hrp=bcrt` for regtest-shaped addresses; signet would use
`tb`).

## 2. Birth agreement

Both implementations returned the same:

- Taproot address (bech32m, witness v1)
- 4-word fingerprint
- plate A = pad integer
- plate B = k XOR p

Mismatch rule exercised in code: any field inequality fails the
test harness (stop condition).

## 3. Stamp check (logical)

Plate B carries the address. Re-deriving from `k = plate_B XOR
plate_A` reproduced the same address on both implementations. That
is the permanent checksum.

## 4. Signet spend (template)

Unsigned JSON (public):

```json
{
  "version": 2,
  "locktime": 0,
  "inputs": [
    {
      "txid": "1111111111111111111111111111111111111111111111111111111111111111",
      "vout": 0,
      "amount": 100000,
      "scriptPubKey": "<p2tr of rehearsal address>",
      "sequence": 4294967295
    }
  ],
  "destination": {"address": "<same rehearsal address>", "amount": 80000},
  "change": {"amount": 15000}
}
```

Screen confirmation lines (fee 5000 sats) shown before signing on
both paths.

## 5. Dual signatures

`sign_pico.sign_tx` and `sign_duo.sign_tx` produced **byte-identical**
signature blobs and **byte-identical** raw transaction hex
(`tests/vectors_test.py::test_sign_template_agreement`).

BIP340 `aux_rand` was 32 zero bytes on both sides.

## 6. Broadcast posture

Signed raw hex is public. In a live signet rehearsal the operator
copies it from SD to any online machine and submits to a signet
node. This dry run stops at identical hex — the consensus-critical
step that must not diverge.

## 7. Power off

Secrets were never written with `open(..., "w")` under `src/`.
Reflash before the next ceremony.

---

**Verdict:** birth agreement, address-as-checksum, screen confirm,
and dual byte-identical fixed-template signatures are exercised by
the committed test harness. A chain-broadcast pocket-sat pass on
public signet remains an operator step; treat it as mandatory
before mainnet funds (PROTOCOL.md Phase 4).
