# Rehearsal transcript — signet (dry run)

This document proves the math path was walked once end-to-end on
signet semantics. It uses **throwaway rolls** published here so
reviewers can reproduce. Do not send value to these addresses on
mainnet.

Current ceremony (see PROTOCOL.md): **one device at birth**, graded
by Bitcoin Core (`tr()` on public data) and a $5 ledger
round-trip; **witness machine at spend** for byte-identical
signatures. This transcript's dual-implementation checks are the
code seat-warmer; a human Core + hardware walk is still pending
(README STATUS).

## 0. Tooling check

```
$ python3 tests/vectors_test.py
OK pins
… per-suite OK lines …

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

Entered once (birth path). Both code lineages in
`tests/vectors_test.py` consume the same sequences
(`hrp=bcrt` for regtest-shaped addresses; signet would use `tb`).

## 2. Birth (one entry; dual code check)

Both implementations returned the same:

- Taproot address (bech32m, witness v1)
- 4-word fingerprint
- plate A = pad integer
- plate B = k XOR p

Mismatch rule exercised in code: any field inequality fails the
test harness (stop condition). On a live ceremony, Core
`deriveaddresses "tr(P)#<checksum>"` must also match before steel is
stamped.

## 3. Stamp check (logical)

Plate B carries the address. Re-deriving from `k = plate_B XOR
plate_A` reproduced the same address on both implementations. That
is the permanent checksum — and the typo catch before real funds.

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

Screen confirmation (destination, amount, fee) runs before signing.
On a live spend, both the birth device and the witness machine
must agree.

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

**Verdict (code harness):** birth agreement across code lineages,
address-as-checksum, screen confirm, and dual byte-identical
fixed-template signatures are exercised by the committed test
harness. A pocket-sat round-trip on public signet remains an
operator step — mandatory before mainnet funds (PROTOCOL.md
Phases 3–4 and 6).

## 8. Which tools recover a raw scalar today (2026-08-12)

Throwaway signet key, not casino dice. Scalar
`k = SHA-256("dice-math-steel-signet-throwaway-2026-08") mod n`.
Device (`p2tr_address`, `hrp=tb`):

```
tb1p3j4f60g60w2k37ltfdugdax0qqewq2let7r8el8t5wa230096lps9mea9g
P = c6dd43d180a763eb13535dc8df405356ade94c99c2fe75dedbeb5321641d9236
Q = 8caa9d3d1a7b9568fbeb4b7886f4cf0032e02bf95f867cfceba3baa8bde5d7c3
WIF (signet, compressed, even-Y d) =
  cMhUaBZQytonLNgMwn5B5ykHQugqZKbg6LY2dD4qTXtZwWYKzGSi
```

Do not send mainnet value here. This key is published.

### Table

Rows mean different things if we do not say how they were
produced. **Run** means a command was executed. **Source**
means the code was read. Mixed rows are labeled as such.

| Tool | Result |
|---|---|
| Bitcoin Core 29.4 | **works with caveats** — run |
| Sparrow 2.5.3 (source `b99b880`) | **untested — source inspection only** |
| Electrum (`c4cc40f`) | **does not work** — type gate reproduced; wallet not launched |
| embit 0.8.0 (one-off script) | **works** — run locally; not broadcast |

A negative cell is a fact, not a slight.

### Bitcoin Core — reference path

`tr(<WIF>)`, `tr(P)`, and `rawtr(Q)` all derived the device
address. `tr(Q)` did not (double tweak). Checksums from
`getdescriptorinfo`:

```
bitcoin-cli -signet getdescriptorinfo "tr(<WIF>)"
# checksum xlfchfp9; normalized tr(P)#hq3yqldu
bitcoin-cli -signet deriveaddresses "tr(<WIF>)#xlfchfp9"
bitcoin-cli -signet deriveaddresses "rawtr(<Q>)#vje5tnck"
# both → tb1p3j4f60g60w2k37ltfdugdax0qqewq2let7r8el8t5wa230096lps9mea9g
```

Import: a single-key `tr()` descriptor is not ranged, so
`active:true` is rejected (`Active descriptors must be ranged`).
`active:false` imports and the address is `ismine` / `solvable`:

```
bitcoin-cli -signet createwallet "sweep2" false true "" false true
bitcoin-cli -signet -rpcwallet=sweep2 importdescriptors \
  '[{"desc":"tr(<WIF>)#xlfchfp9","timestamp":"now","active":false}]'
bitcoin-cli -signet -rpcwallet=sweep2 getaddressinfo "<addr>"
# ismine: true, solvable: true, desc: tr([…]P)#…
```

Sign: `signrawtransactionwithwallet` on a one-input unsigned
transaction, with the previous output handed in
(`scriptPubKey` = `5120`∥`Q`, amount 0.001), returned
`complete: true` and a 64-byte Schnorr witness.

Broadcast: `sendrawtransaction` returned
`bad-txns-inputs-missingorspent`. The node was still in
initial block download and the input was synthetic — there
was no signet UTXO. Signing from `tr(<WIF>)` worked; a
funded round-trip was not completed in this sitting.

### Sparrow — Tools → Sweep Private Key

**Untested.** The GUI was not clicked. Nothing was swept.
What follows is source inspection of Sparrow `b99b880` and
drongo `ScriptType.java`, not a result.

- The sweep dialog's script-type list is
  `ScriptType.getAddressableScriptTypes(SINGLE_HD)`, which
  includes Taproot (`P2TR`). Default selection is **P2PKH**.
  That is a live operator trap: leave the default and the
  tool looks at a different script than this protocol's
  output.
- For `P2TR` + `SINGLE_HD`, `getOutputKey` calls
  `derivedKey.getTweakedOutputKey()` — the BIP341 tweak,
  same object as `tr()`.
- Create-transaction signs a Schnorr key-path spend when
  the selected type is `P2TR`.

What would settle it: fund a signet P2TR key-path output,
open Tools → Sweep Private Key, set script type to
**Taproot**, sweep, and confirm the coins move. Until that
happens, this row is not a second independent recovery
path. It is a pointer and a warning about the P2PKH
default.

### Electrum — raw scalar

Electrum the application was **not launched** (`electrum-ecc`
failed to build in this environment). The negative is from
source at `c4cc40f` plus a reproduced type gate, not from
clicking Import.

`WIF_SCRIPT_TYPES` in `electrum/bitcoin.py` is `p2pkh`,
`p2wpkh`, `p2wpkh-p2sh`, `p2sh`, `p2wsh`, `p2wsh-p2sh`.
There is no `p2tr`. `Imported_KeyStore.import_private_keys`
only accepts `p2pkh`, `p2wpkh`, `p2wpkh-p2sh`.

Reproduced the deserialize gate (same dict, same split):

```
p2tr:<WIF>  →  unknown script type: p2tr
```

Electrum's Taproot work (BIP86 HD trees; library-level
key-path spends) is not a raw-scalar import path. A
negative result. Launching the GUI would hit the same
gate; it would not make this row a run.

### One minimal script — embit 0.8.0

Library: [embit](https://github.com/diybitcoinhardware/embit)
0.8.0. Not a repo dependency; a one-off. No curve math
written here.

```
from embit import ec, networks
from embit.descriptor import Descriptor
from embit.transaction import Transaction, TransactionInput, TransactionOutput, SIGHASH
from embit.script import Script

net = networks.NETWORKS["signet"]
desc = Descriptor.from_string("tr(<WIF>)")
assert desc.address(network=net) == "<device tb1p…>"

prv = ec.PrivateKey.from_wif("<WIF>").taproot_tweak(b"")
spk = Script(bytes.fromhex("5120") + bytes.fromhex("<Q>"))
tx = Transaction(version=2,
                 vin=[TransactionInput(bytes.fromhex("11"*32), 0)],
                 vout=[TransactionOutput(90000, spk)],
                 locktime=0)
sh = tx.sighash_taproot(0, [spk], [100000], sighash=SIGHASH.DEFAULT)
sig = prv.schnorr_sign(sh)
assert prv.schnorr_verify(sig, sh)
```

Address matched the device. Signature verified under the
tweaked key. (It did not match Core's witness; Core does
not use this protocol's fixed-zero aux. Recovery only
needs a valid spend.)

### What this does not say

embit derived and signed from the same WIF today — locally.
That is one independent library path, not a ledger ruling.
Sparrow was not tested; its sweep default is P2PKH, which
is worth knowing even from source. Electrum's type gate
rejects a raw P2TR scalar. Core's wallet RPC (`active` must
be false for a single key; import commands have changed
before) is the operator surface, not the math. No funded
signet broadcast was completed in this sitting.
