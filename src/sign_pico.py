# sign_pico.py — fixed-template BIP341 key-path spend + BIP340 sign
# Physics authors all randomness. aux_rand = 32 zero bytes. No RNG.
# Displays destination + amount + fee BEFORE signing.

import binascii
import json
import sys

try:
    import birth_pico as C
except ImportError:
    from birth_pico import birth_pico as C  # noqa — desktop path variant unused


def _u32(n):
    return int(n).to_bytes(4, "little")


def _u64(n):
    return int(n).to_bytes(8, "little")


def _ser_compact(n):
    if n < 0xfd:
        return bytes([n])
    if n <= 0xffff:
        return b"\xfd" + int(n).to_bytes(2, "little")
    if n <= 0xffffffff:
        return b"\xfe" + int(n).to_bytes(4, "little")
    return b"\xff" + int(n).to_bytes(8, "little")


def _sha_concat(chunks):
    return C.sha256(b"".join(chunks))


def decode_address(addr):
    hrp, ver, prog = C.bech32m_decode(addr)
    if ver != 1 or len(prog) != 32:
        raise ValueError("need P2TR")
    return hrp, prog


def script_pubkey_p2tr(prog32):
    return bytes([0x51, 0x20]) + prog32


def tweaked_privkey(internal_priv, merkle_root=None):
    d, px = C.xonly_pubkey(internal_priv)
    if merkle_root is None:
        t = int.from_bytes(C.tagged_hash("TapTweak", px), "big")
    else:
        t = int.from_bytes(C.tagged_hash("TapTweak", px + merkle_root), "big")
    if t >= C.N:
        raise ValueError("tweak")
    return (d + t) % C.N, px


def parse_tx_json(obj):
    # Documented unsigned-tx JSON (public data on SD).
    # {
    #   "version": 2, "locktime": 0,
    #   "inputs": [{"txid": hex, "vout": int, "amount": sats, "scriptPubKey": hex}],
    #   "destination": {"address": str, "amount": sats},
    #   "change": {"amount": sats} | null
    # }
    version = int(obj.get("version", 2))
    locktime = int(obj.get("locktime", 0))
    inputs = obj["inputs"]
    dest = obj["destination"]
    change = obj.get("change")
    return version, locktime, inputs, dest, change


def build_outputs(dest, change, our_script):
    _hrp, dprog = decode_address(dest["address"])
    outs = [(int(dest["amount"]), script_pubkey_p2tr(dprog))]
    if change is not None and int(change["amount"]) > 0:
        outs.append((int(change["amount"]), our_script))
    return outs


def fee_sats(inputs, outs):
    return sum(int(i["amount"]) for i in inputs) - sum(a for a, _ in outs)


def taproot_sighash(version, locktime, inputs, outs, index, hash_type=0):
    # BIP341 key-path sighash (epoch 0). hash_type 0 = SIGHASH_DEFAULT (~ALL).
    # Field order: control/tx data → spend_type + input → SINGLE output (if any).
    ext_flag = 0
    annex = False
    spend_type = (ext_flag << 1) + (1 if annex else 0)
    ht = hash_type
    anyone = (ht & 0x80) != 0
    out_type = ht & 3
    if ht == 0:
        out_type = 1  # DEFAULT behaves like ALL for outputs

    prevouts = []
    amounts = []
    spks = []
    sequences = []
    for inp in inputs:
        txid = bytes.fromhex(inp["txid"])[::-1]
        prevouts.append(txid + _u32(inp["vout"]))
        amounts.append(_u64(inp["amount"]))
        spk = bytes.fromhex(inp["scriptPubKey"])
        spks.append(_ser_compact(len(spk)) + spk)
        sequences.append(_u32(inp.get("sequence", 0xFFFFFFFF)))

    msg = bytearray()
    msg.append(0)  # epoch
    msg.append(ht)
    msg += _u32(version)
    msg += _u32(locktime)
    if not anyone:
        msg += _sha_concat(prevouts)
        msg += _sha_concat(amounts)
        msg += _sha_concat(spks)
        msg += _sha_concat(sequences)
    if out_type == 1:  # ALL / DEFAULT
        ser_outs = []
        for amt, spk in outs:
            ser_outs.append(_u64(amt) + _ser_compact(len(spk)) + spk)
        msg += _sha_concat(ser_outs)
    msg.append(spend_type)
    if anyone:
        inp = inputs[index]
        txid = bytes.fromhex(inp["txid"])[::-1]
        spk = bytes.fromhex(inp["scriptPubKey"])
        msg += txid + _u32(inp["vout"])
        msg += _u64(inp["amount"])
        msg += _ser_compact(len(spk)) + spk
        msg += _u32(inp.get("sequence", 0xFFFFFFFF))
    else:
        msg += _u32(index)
    if out_type == 3:  # SINGLE — after input data
        if index >= len(outs):
            raise ValueError("SIGHASH_SINGLE missing output")
        amt, spk = outs[index]
        msg += C.sha256(_u64(amt) + _ser_compact(len(spk)) + spk)
    return C.tagged_hash("TapSighash", bytes(msg))


def sign_input(internal_priv, version, locktime, inputs, outs, index, hash_type=0):
    d_tw, _px = tweaked_privkey(internal_priv, None)
    sh = taproot_sighash(version, locktime, inputs, outs, index, hash_type)
    # BIP340 with aux_rand = 32 zero bytes
    sig = C.schnorr_sign(d_tw, sh, bytes(32))
    if hash_type != 0:
        sig += bytes([hash_type])
    return sig, sh


def serialize_signed(version, locktime, inputs, outs, witnesses):
    # segwit v2 tx: marker 0, flag 1
    tx = bytearray()
    tx += _u32(version)
    tx += b"\x00\x01"
    tx += _ser_compact(len(inputs))
    for inp in inputs:
        tx += bytes.fromhex(inp["txid"])[::-1]
        tx += _u32(inp["vout"])
        tx += b"\x00"  # empty scriptSig
        tx += _u32(inp.get("sequence", 0xFFFFFFFF))
    tx += _ser_compact(len(outs))
    for amt, spk in outs:
        tx += _u64(amt)
        tx += _ser_compact(len(spk)) + spk
    for wit in witnesses:
        tx += _ser_compact(len(wit))
        for item in wit:
            tx += _ser_compact(len(item)) + item
    tx += _u32(locktime)
    return bytes(tx)


def confirm_screen(display, dest, amount, fee, change_amt):
    # Human confirmation BEFORE signing — short lines, not hex.
    lines = "TO %s\n%s sats\nfee %s" % (dest["address"][:12] + "...", amount, fee)
    if change_amt:
        lines += "\nchg %s" % change_amt
    if display:
        display.show(lines)
    else:
        print(lines)
    return True


def sign_tx(internal_priv, tx_obj, display=None, our_address=None):
    version, locktime, inputs, dest, change = parse_tx_json(tx_obj)
    if our_address is None:
        our_address, _, _, _ = C.p2tr_address(internal_priv)
    _, our_prog = decode_address(our_address)
    our_script = script_pubkey_p2tr(our_prog)
    # All inputs must be our one key
    for inp in inputs:
        if bytes.fromhex(inp["scriptPubKey"]) != our_script:
            raise ValueError("input not our address")
    outs = build_outputs(dest, change, our_script)
    fee = fee_sats(inputs, outs)
    if fee < 0:
        raise ValueError("negative fee")
    if not confirm_screen(display, dest, dest["amount"], fee,
                          change["amount"] if change else 0):
        raise SystemExit("aborted")
    wits = []
    sigs = []
    for i in range(len(inputs)):
        sig, _sh = sign_input(internal_priv, version, locktime, inputs, outs, i, 0)
        wits.append([sig])
        sigs.append(sig)
    raw = serialize_signed(version, locktime, inputs, outs, wits)
    return {
        "raw_tx_hex": raw.hex(),
        "signatures": [s.hex() for s in sigs],
        "fee": fee,
        "address": our_address,
    }


def main(argv):
    # Usage: sign_pico.py <key_hex> <unsigned.json>
    # key from plates (XOR) entered on device; never written to flash.
    if len(argv) != 3:
        print("usage: sign_pico.py <key_hex> <unsigned.json>", file=sys.stderr)
        return 2
    key = int(argv[1], 16)
    with open(argv[2], "r") as f:
        tx_obj = json.load(f)
    result = sign_tx(key, tx_obj)
    # Public data only — signed raw tx hex to stdout for SD copy.
    print(result["raw_tx_hex"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
