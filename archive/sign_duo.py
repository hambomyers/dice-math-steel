# sign_duo.py — implementation #2 fixed-template signer (Milk-V Duo)
# SEAT-WARMER pending independent rewrite by a second human author.
# See DECISIONS.md. Algorithms arranged differently from sign_pico.py.
#
# Physics authors all randomness. aux_rand = 32 zero bytes. No RNG.

import json
import sys

import birth_duo as crypto


def le32(n):
    return (n & 0xFFFFFFFF).to_bytes(4, "little")


def le64(n):
    return (n & 0xFFFFFFFFFFFFFFFF).to_bytes(8, "little")


def varint(n):
    if n < 0xFD:
        return bytes([n])
    if n <= 0xFFFF:
        return b"\xfd" + n.to_bytes(2, "little")
    if n <= 0xFFFFFFFF:
        return b"\xfe" + n.to_bytes(4, "little")
    return b"\xff" + n.to_bytes(8, "little")


def p2tr_script(program):
    return b"\x51\x20" + program


def addr_program(address):
    hrp, ver, prog = crypto.bech32m_decode(address)
    if ver != 1 or len(prog) != 32:
        raise ValueError("P2TR required")
    return prog


def tweak_secret(secret, merkle=None):
    sec, xonly = crypto.xonly_pubkey(secret)
    material = xonly if merkle is None else (xonly + merkle)
    t = int.from_bytes(crypto.tagged_hash("TapTweak", material), "big")
    if t >= crypto._N:
        raise ValueError("tweak range")
    return (sec + t) % crypto._N


def load_unsigned(doc):
    return (
        int(doc.get("version", 2)),
        int(doc.get("locktime", 0)),
        list(doc["inputs"]),
        dict(doc["destination"]),
        doc.get("change"),
    )


def make_outs(destination, change, change_script):
    prog = addr_program(destination["address"])
    result = [(int(destination["amount"]), p2tr_script(prog))]
    if change and int(change["amount"]) > 0:
        result.append((int(change["amount"]), change_script))
    return result


def compute_fee(vin, vout):
    return sum(int(x["amount"]) for x in vin) - sum(a for a, _ in vout)


def sighash_keypath(version, locktime, vin, vout, vin_index, hash_type=0):
    # BIP341 key-path; structure built as a list of pieces then joined.
    pieces = [b"\x00", bytes([hash_type]), le32(version), le32(locktime)]
    acp = (hash_type & 0x80) != 0
    base = hash_type & 3
    if hash_type == 0:
        base = 1

    if not acp:
        po = [bytes.fromhex(i["txid"])[::-1] + le32(i["vout"]) for i in vin]
        am = [le64(i["amount"]) for i in vin]
        sp = []
        sq = []
        for i in vin:
            s = bytes.fromhex(i["scriptPubKey"])
            sp.append(varint(len(s)) + s)
            sq.append(le32(i.get("sequence", 0xFFFFFFFF)))
        pieces += [crypto.sha256(b"".join(po)), crypto.sha256(b"".join(am)),
                   crypto.sha256(b"".join(sp)), crypto.sha256(b"".join(sq))]
    if base == 1:
        blob = b"".join(le64(a) + varint(len(s)) + s for a, s in vout)
        pieces.append(crypto.sha256(blob))

    pieces.append(b"\x00")  # spend_type key-path, no annex
    if acp:
        i = vin[vin_index]
        s = bytes.fromhex(i["scriptPubKey"])
        pieces.append(bytes.fromhex(i["txid"])[::-1] + le32(i["vout"]))
        pieces.append(le64(i["amount"]) + varint(len(s)) + s + le32(i.get("sequence", 0xFFFFFFFF)))
    else:
        pieces.append(le32(vin_index))
    if base == 3:
        if vin_index >= len(vout):
            raise ValueError("SINGLE")
        a, s = vout[vin_index]
        pieces.append(crypto.sha256(le64(a) + varint(len(s)) + s))
    return crypto.tagged_hash("TapSighash", b"".join(pieces))


def sign_one(secret, version, locktime, vin, vout, vin_index, hash_type=0):
    tweaked = tweak_secret(secret, None)
    digest = sighash_keypath(version, locktime, vin, vout, vin_index, hash_type)
    sig = crypto.schnorr_sign(tweaked, digest, bytes(32))
    if hash_type:
        sig += bytes([hash_type])
    return sig


def encode_tx(version, locktime, vin, vout, witnesses):
    out = bytearray()
    out += le32(version)
    out += b"\x00\x01"
    out += varint(len(vin))
    for i in vin:
        out += bytes.fromhex(i["txid"])[::-1]
        out += le32(i["vout"])
        out += b"\x00"
        out += le32(i.get("sequence", 0xFFFFFFFF))
    out += varint(len(vout))
    for amt, spk in vout:
        out += le64(amt)
        out += varint(len(spk)) + spk
    for stack in witnesses:
        out += varint(len(stack))
        for item in stack:
            out += varint(len(item)) + item
    out += le32(locktime)
    return bytes(out)


def human_confirm(ui, destination, fee, change_amount):
    text = "PAY %s\namount %s\nfee %s" % (
        destination["address"][:12] + "...", destination["amount"], fee)
    if change_amount:
        text += "\nchange %s" % change_amount
    if ui is not None:
        ui.show(text)
    else:
        print(text)
    return True


def sign_tx(secret, doc, ui=None, own_address=None):
    version, locktime, vin, destination, change = load_unsigned(doc)
    if own_address is None:
        own_address = crypto.p2tr_address(secret)[0]
    own_script = p2tr_script(addr_program(own_address))
    for i in vin:
        if bytes.fromhex(i["scriptPubKey"]) != own_script:
            raise ValueError("foreign input")
    vout = make_outs(destination, change, own_script)
    fee = compute_fee(vin, vout)
    if fee < 0:
        raise ValueError("fee")
    if not human_confirm(ui, destination, fee, change["amount"] if change else 0):
        raise SystemExit("stop")
    stacks = []
    hex_sigs = []
    for idx in range(len(vin)):
        sig = sign_one(secret, version, locktime, vin, vout, idx, 0)
        stacks.append([sig])
        hex_sigs.append(sig.hex())
    raw = encode_tx(version, locktime, vin, vout, stacks)
    return {"raw_tx_hex": raw.hex(), "signatures": hex_sigs, "fee": fee, "address": own_address}


def main(argv):
    if len(argv) != 3:
        print("usage: sign_duo.py <key_hex> <unsigned.json>", file=sys.stderr)
        return 2
    secret = int(argv[1], 16)
    with open(argv[2], "r") as fh:
        doc = json.load(fh)
    print(sign_tx(secret, doc)["raw_tx_hex"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
