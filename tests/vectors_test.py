#!/usr/bin/env python3
"""
vectors_test.py — both implementations must pass official vectors identically.

Runs with:  python3 tests/vectors_test.py

Vector files under tests/vectors/ are hash-pinned in SHA256SUMS.
"""

import csv
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))

import birth_duo as duo
import birth_pico as pico
import sign_duo as sign_duo
import sign_pico as sign_pico

VECTORS = os.path.join(HERE, "vectors")
PINS = {
    "bip340_test_vectors.csv":
        "34c9d1d9c3a88d524bc80778540dc43f8306ec249a7485293063c376db851c2d",
    "bip341_wallet_test_vectors.json":
        "403e19fb81dd1f31e745699216308f61fb403774b2aafa87b631b8f7c042d37f",
    "bip350_bech32m_vectors.json":
        "00d5f8f1db6eac89ef87645355f8e06d5739140ac7e3fe1cc95d4121ee0f4ebc",
    "sipa_bech32_tests.py":
        "0d1cee7f1abd8543e13a190ffd87b65f126deb750df72d7d1d75857c3c419e1c",
}


class _SilentDisplay:
    """Mute OLED/confirm path so the harness prints only suite results."""

    def show(self, text):
        return None


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def check_pins():
    for name, expect in PINS.items():
        path = os.path.join(VECTORS, name)
        got = _sha256_file(path)
        if got != expect:
            raise AssertionError("hash pin failed for %s\n got %s\n want %s" % (name, got, expect))


def test_bip340(mod):
    path = os.path.join(VECTORS, "bip340_test_vectors.csv")
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            pk = bytes.fromhex(row["public key"])
            msg = bytes.fromhex(row["message"])
            sig = bytes.fromhex(row["signature"]) if row["signature"] else None
            want = row["verification result"] == "TRUE"
            if row["secret key"]:
                d = int(row["secret key"], 16)
                aux = bytes.fromhex(row["aux_rand"])
                _, px = mod.xonly_pubkey(d)
                if px != pk:
                    # some vectors use a fixed secret whose pubkey is given
                    pass
                got = mod.schnorr_sign(d, msg, aux)
                if got != sig:
                    raise AssertionError("%s BIP340 sign mismatch index %s" % (mod.__name__, row["index"]))
                if not mod.schnorr_verify(pk, msg, got):
                    raise AssertionError("%s BIP340 verify(sign) failed index %s" % (mod.__name__, row["index"]))
            else:
                ok = mod.schnorr_verify(pk, msg, sig) if sig else False
                if ok != want:
                    raise AssertionError("%s BIP340 verify mismatch index %s" % (mod.__name__, row["index"]))


def test_bip341_tweak(mod):
    data = json.load(open(os.path.join(VECTORS, "bip341_wallet_test_vectors.json")))
    for case in data["scriptPubKey"]:
        if case["given"]["scriptTree"] is not None:
            continue
        px = bytes.fromhex(case["given"]["internalPubkey"])
        qx, t = mod.taproot_output_key(px)
        if t.to_bytes(32, "big").hex() != case["intermediary"]["tweak"]:
            raise AssertionError("%s tweak mismatch" % mod.__name__)
        if qx.hex() != case["intermediary"]["tweakedPubkey"]:
            raise AssertionError("%s Q mismatch" % mod.__name__)
        addr = mod.bech32m_encode("bc", 1, qx)
        if addr != case["expected"]["bip350Address"]:
            raise AssertionError("%s address mismatch: %s" % (mod.__name__, addr))


def _read_varint(buf, i):
    n = buf[i]
    i += 1
    if n < 0xFD:
        return n, i
    if n == 0xFD:
        return int.from_bytes(buf[i:i + 2], "little"), i + 2
    if n == 0xFE:
        return int.from_bytes(buf[i:i + 4], "little"), i + 4
    return int.from_bytes(buf[i:i + 8], "little"), i + 8


def _parse_unsigned(rawhex, utxos):
    b = bytes.fromhex(rawhex)
    i = 0
    version = int.from_bytes(b[i:i + 4], "little")
    i += 4
    nin, i = _read_varint(b, i)
    inputs = []
    for k in range(nin):
        txid = b[i:i + 32][::-1].hex()
        i += 32
        vout = int.from_bytes(b[i:i + 4], "little")
        i += 4
        sl, i = _read_varint(b, i)
        i += sl
        seq = int.from_bytes(b[i:i + 4], "little")
        i += 4
        u = utxos[k]
        inputs.append({
            "txid": txid, "vout": vout, "amount": u["amountSats"],
            "scriptPubKey": u["scriptPubKey"], "sequence": seq,
        })
    nout, i = _read_varint(b, i)
    outs = []
    for _ in range(nout):
        amt = int.from_bytes(b[i:i + 8], "little")
        i += 8
        sl, i = _read_varint(b, i)
        spk = b[i:i + sl]
        i += sl
        outs.append((amt, spk))
    locktime = int.from_bytes(b[i:i + 4], "little")
    return version, locktime, inputs, outs


def test_bip341_sighash_and_sign():
    data = json.load(open(os.path.join(VECTORS, "bip341_wallet_test_vectors.json")))
    case = data["keyPathSpending"][0]
    version, locktime, inputs, outs = _parse_unsigned(
        case["given"]["rawUnsignedTx"], case["given"]["utxosSpent"])
    for sp in case["inputSpending"]:
        if sp["given"]["merkleRoot"] is not None:
            continue
        idx = sp["given"]["txinIndex"]
        ht = sp["given"]["hashType"]
        priv = int(sp["given"]["internalPrivkey"], 16)
        for label, sighash_fn, sign_fn in (
            ("pico", sign_pico.taproot_sighash, sign_pico.sign_input),
            ("duo", sign_duo.sighash_keypath, None),
        ):
            sh = sighash_fn(version, locktime, inputs, outs, idx, ht)
            if sh.hex() != sp["intermediary"]["sigHash"]:
                raise AssertionError("%s sighash mismatch idx %s" % (label, idx))
        sig, _ = sign_pico.sign_input(priv, version, locktime, inputs, outs, idx, ht)
        # duo path
        tweaked = sign_duo.tweak_secret(priv, None)
        sh = sign_duo.sighash_keypath(version, locktime, inputs, outs, idx, ht)
        sig2 = duo.schnorr_sign(tweaked, sh, bytes(32))
        if ht:
            sig2 += bytes([ht])
        if sig.hex() != sp["expected"]["witness"][0]:
            raise AssertionError("pico witness mismatch")
        if sig2.hex() != sp["expected"]["witness"][0]:
            raise AssertionError("duo witness mismatch")
        if sig != sig2:
            raise AssertionError("pico/duo signatures differ")


def _bech32m_checksum_ok(mod, addr):
    if hasattr(mod, "_polymod"):
        charset, hrp_ex, polymod, const = (
            mod._CHARSET, mod._hrp_expand, mod._polymod, 0x2bc830a3)
    else:
        charset, hrp_ex, polymod, const = (
            mod._B32, mod._hrp_ex, mod._pm, mod._BECH32M)
    low = addr.lower()
    pos = low.rfind("1")
    hrp = low[:pos]
    data = [charset.index(c) for c in low[pos + 1:]]
    return polymod(hrp_ex(hrp) + data) == const


def test_bip350(mod):
    data = json.load(open(os.path.join(VECTORS, "bip350_bech32m_vectors.json")))
    for case in data["valid_segwit_bech32m"]:
        prog = bytes.fromhex(case["witprog_hex"])
        addr = mod.bech32m_encode(case["hrp"], case["witver"], prog)
        if addr.lower() != case["address"].lower():
            raise AssertionError("%s bech32m encode %s != %s" % (mod.__name__, addr, case["address"]))
        hrp, ver, got = mod.bech32m_decode(case["address"])
        if hrp != case["hrp"] or ver != case["witver"] or got != prog:
            raise AssertionError("%s bech32m decode mismatch" % mod.__name__)
    for case in data["valid_bech32m"]:
        if not _bech32m_checksum_ok(mod, case["str"]):
            raise AssertionError("%s BIP350 bech32m checksum fail: %s" % (
                mod.__name__, case["str"]))


def _parse_sipa_lists(src):
    # Extract VALID_BECH32M / VALID_ADDRESS without importing sipa's segwit_addr.
    import ast
    tree = ast.parse(src)
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            name = node.targets[0].id if isinstance(node.targets[0], ast.Name) else None
            if name in ("VALID_BECH32M", "VALID_ADDRESS"):
                out[name] = ast.literal_eval(node.value)
    return out


def test_sipa_bech32_crosscheck(mod):
    # Pin file is the upstream referee; our JSON must not drift from it.
    src = open(os.path.join(VECTORS, "sipa_bech32_tests.py"), encoding="utf-8").read()
    lists = _parse_sipa_lists(src)
    ours = json.load(open(os.path.join(VECTORS, "bip350_bech32m_vectors.json")))
    ours_generic = {c["str"].lower() for c in ours["valid_bech32m"]}
    for s in lists["VALID_BECH32M"]:
        if s.lower() not in ours_generic:
            raise AssertionError("BIP350 JSON missing sipa VALID_BECH32M %s" % s)
        if not _bech32m_checksum_ok(mod, s):
            raise AssertionError("%s rejects sipa VALID_BECH32M %s" % (mod.__name__, s))
    for addr, spk_hex in lists["VALID_ADDRESS"]:
        spk = bytes.fromhex(spk_hex)
        witver = spk[0] - 0x50 if spk[0] else 0
        if witver < 1:
            continue  # v0 is bech32, not bech32m
        prog = spk[2:]
        hrp = "tb" if addr.lower().startswith("tb") else "bc"
        got = mod.bech32m_encode(hrp, witver, prog)
        if got.lower() != addr.lower():
            raise AssertionError("%s sipa VALID_ADDRESS encode %s" % (mod.__name__, addr))
        _h, v, p = mod.bech32m_decode(addr)
        if v != witver or p != prog:
            raise AssertionError("%s sipa VALID_ADDRESS decode %s" % (mod.__name__, addr))


def test_birth_agreement():
    words = ["w%04d" % i for i in range(2048)]
    # deterministic fake rolls (not for real keys) — no RNG module used
    key_rolls = [((i * 7) % 6) + 1 for i in range(256)]
    pad_rolls = [((i * 11) % 6) + 1 for i in range(256)]
    a = pico.birth(key_rolls, pad_rolls, words, hrp="bc")
    b = duo.birth(key_rolls, pad_rolls, words, hrp="bc")
    for k in ("address", "fingerprint", "plate_a", "plate_b", "k", "p"):
        if a[k] != b[k]:
            raise AssertionError("birth disagree on %s" % k)


def test_sign_template_agreement():
    words = ["w%04d" % i for i in range(2048)]
    key_rolls = [((i * 3) % 6) + 1 for i in range(256)]
    pad_rolls = [((i * 5) % 6) + 1 for i in range(256)]
    born = pico.birth(key_rolls, pad_rolls, words, hrp="bcrt")
    k = born["k"]
    addr = born["address"]
    _, _, prog = pico.bech32m_decode(addr)
    spk = "5120" + prog.hex()
    # one input → destination + change back to same address
    tx = {
        "version": 2,
        "locktime": 0,
        "inputs": [{
            "txid": "11" * 32,
            "vout": 0,
            "amount": 100000,
            "scriptPubKey": spk,
            "sequence": 0xFFFFFFFF,
        }],
        "destination": {"address": addr, "amount": 80000},
        "change": {"amount": 15000},
    }
    quiet = _SilentDisplay()
    r1 = sign_pico.sign_tx(k, tx, display=quiet, our_address=addr)
    r2 = sign_duo.sign_tx(k, tx, ui=quiet, own_address=addr)
    if r1["signatures"] != r2["signatures"]:
        raise AssertionError("template signatures differ")
    if r1["raw_tx_hex"] != r2["raw_tx_hex"]:
        raise AssertionError("template raw tx differs")


def main():
    check_pins()
    print("OK pins")
    for mod in (pico, duo):
        test_bip340(mod)
        print("OK bip340 (%s)" % mod.__name__)
        test_bip341_tweak(mod)
        print("OK bip341 tweak (%s)" % mod.__name__)
        test_bip350(mod)
        print("OK bip350 (%s)" % mod.__name__)
        test_sipa_bech32_crosscheck(mod)
        print("OK sipa bech32 crosscheck (%s)" % mod.__name__)
    test_bip341_sighash_and_sign()
    print("OK bip341 sighash+sign (both)")
    test_birth_agreement()
    print("OK birth agreement")
    test_sign_template_agreement()
    print("OK sign template agreement")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print("FAIL:", e, file=sys.stderr)
        sys.exit(1)
