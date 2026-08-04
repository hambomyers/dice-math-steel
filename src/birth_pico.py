# birth_pico.py — implementation #1 (MicroPython / desktop)
# Physics authors all randomness. No RNG calls in this file.
# Secrets stay in RAM; this module never opens a file for write.

P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
_K = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
]


def _rotr(x, n):
    return ((x >> n) | (x << (32 - n))) & 0xFFFFFFFF


def sha256(msg):
    if isinstance(msg, str):
        msg = msg.encode()
    h = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]
    ml = len(msg)
    msg = msg + b"\x80" + b"\x00" * ((55 - ml) % 64) + (ml * 8).to_bytes(8, "big")
    for off in range(0, len(msg), 64):
        w = [int.from_bytes(msg[off + i * 4:off + i * 4 + 4], "big") for i in range(16)]
        for i in range(16, 64):
            s0 = _rotr(w[i - 15], 7) ^ _rotr(w[i - 15], 18) ^ (w[i - 15] >> 3)
            s1 = _rotr(w[i - 2], 17) ^ _rotr(w[i - 2], 19) ^ (w[i - 2] >> 10)
            w.append((w[i - 16] + s0 + w[i - 7] + s1) & 0xFFFFFFFF)
        a, b, c, d, e, f, g, hh = h
        for i in range(64):
            S1 = _rotr(e, 6) ^ _rotr(e, 11) ^ _rotr(e, 25)
            ch = (e & f) ^ ((~e) & g)
            t1 = (hh + S1 + ch + _K[i] + w[i]) & 0xFFFFFFFF
            S0 = _rotr(a, 2) ^ _rotr(a, 13) ^ _rotr(a, 22)
            maj = (a & b) ^ (a & c) ^ (b & c)
            t2 = (S0 + maj) & 0xFFFFFFFF
            hh, g, f, e, d, c, b, a = g, f, e, (d + t1) & 0xFFFFFFFF, c, b, a, (t1 + t2) & 0xFFFFFFFF
        h = [(x + y) & 0xFFFFFFFF for x, y in zip(h, [a, b, c, d, e, f, g, hh])]
    return b"".join(x.to_bytes(4, "big") for x in h)


def tagged_hash(tag, data):
    t = sha256(tag.encode() if isinstance(tag, str) else tag)
    return sha256(t + t + data)


def _modinv(a, m):
    return pow(a % m, m - 2, m)


def _jdoub(X, Y, Z):
    if Y == 0:
        return 0, 1, 0
    YSQ = (Y * Y) % P
    S = (4 * X * YSQ) % P
    M = (3 * X * X) % P
    X2 = (M * M - 2 * S) % P
    Y2 = (M * (S - X2) - 8 * YSQ * YSQ) % P
    Z2 = (2 * Y * Z) % P
    return X2, Y2, Z2


def _jadd(X1, Y1, Z1, X2, Y2, Z2):
    if Z1 == 0:
        return X2, Y2, Z2
    if Z2 == 0:
        return X1, Y1, Z1
    U1 = (X1 * Z2 * Z2) % P
    U2 = (X2 * Z1 * Z1) % P
    S1 = (Y1 * Z2 * Z2 * Z2) % P
    S2 = (Y2 * Z1 * Z1 * Z1) % P
    if U1 == U2:
        return _jdoub(X1, Y1, Z1) if S1 == S2 else (0, 1, 0)
    H = (U2 - U1) % P
    R = (S2 - S1) % P
    H2 = (H * H) % P
    H3 = (H * H2) % P
    U1H2 = (U1 * H2) % P
    X3 = (R * R - H3 - 2 * U1H2) % P
    Y3 = (R * (U1H2 - X3) - S1 * H3) % P
    Z3 = (H * Z1 * Z2) % P
    return X3, Y3, Z3


def _from_j(X, Y, Z):
    if Z == 0:
        return None
    zi = _modinv(Z, P)
    zi2 = (zi * zi) % P
    return (X * zi2) % P, (Y * zi2 * zi) % P


def _mul(k, x=Gx, y=Gy):
    # double-and-add in Jacobian
    X, Y, Z = 0, 1, 0
    Qx, Qy, Qz = x, y, 1
    while k:
        if k & 1:
            X, Y, Z = _jadd(X, Y, Z, Qx, Qy, Qz)
        Qx, Qy, Qz = _jdoub(Qx, Qy, Qz)
        k >>= 1
    return _from_j(X, Y, Z)


def xonly_pubkey(d):
    # BIP340: lift secret, even-Y internal key
    if not (0 < d < N):
        raise ValueError("bad key")
    pt = _mul(d)
    x, y = pt
    if y & 1:
        d = N - d
        x, y = x, P - y
    return d, x.to_bytes(32, "big")


def taproot_output_key(internal_xonly):
    # BIP341 key-path, no script tree: t = hash_TapTweak(P); Q = P + t*G
    t = int.from_bytes(tagged_hash("TapTweak", internal_xonly), "big") % N
    if t == 0:
        raise ValueError("tweak out of range")
    Px = int.from_bytes(internal_xonly, "big")
    # lift_x
    y2 = (pow(Px, 3, P) + 7) % P
    y = pow(y2, (P + 1) // 4, P)
    if (y * y) % P != y2:
        raise ValueError("lift_x")
    if y & 1:
        y = P - y
    qx, qy = _mul(t)
    # add P + tG
    X, Y, Z = _jadd(Px, y, 1, qx, qy, 1)
    Q = _from_j(X, Y, Z)
    # Output-key parity is irrelevant for the address — only x is encoded.
    return Q[0].to_bytes(32, "big"), t


_CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"


def _polymod(vals):
    GEN = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]
    chk = 1
    for v in vals:
        b = chk >> 25
        chk = ((chk & 0x1ffffff) << 5) ^ v
        for i in range(5):
            chk ^= GEN[i] if ((b >> i) & 1) else 0
    return chk


def _hrp_expand(hrp):
    return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]


def bech32m_encode(hrp, witver, witprog):
    # BIP350 bech32m
    data = [witver]
    acc = num = 0
    for b in witprog:
        acc = (acc << 8) | b
        num += 8
        while num >= 5:
            num -= 5
            data.append((acc >> num) & 31)
    if num:
        data.append((acc << (5 - num)) & 31)
    const = 0x2bc830a3
    values = _hrp_expand(hrp) + data
    polymod = _polymod(values + [0, 0, 0, 0, 0, 0]) ^ const
    checksum = [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]
    return hrp + "1" + "".join(_CHARSET[d] for d in data + checksum)


def bech32m_decode(addr):
    addr_l = addr.lower()
    if addr_l != addr and addr.upper() != addr:
        raise ValueError("mixed case")
    pos = addr_l.rfind("1")
    hrp, data = addr_l[:pos], [_CHARSET.index(c) for c in addr_l[pos + 1:]]
    if _polymod(_hrp_expand(hrp) + data) != 0x2bc830a3:
        raise ValueError("checksum")
    data = data[:-6]
    witver = data[0]
    acc = num = 0
    out = []
    for v in data[1:]:
        acc = (acc << 5) | v
        num += 5
        if num >= 8:
            num -= 8
            out.append((acc >> num) & 255)
    return hrp, witver, bytes(out)


def rolls_to_int(rolls):
    # 1-3 -> 0, 4-6 -> 1; 256 rolls -> 256-bit int
    if len(rolls) != 256:
        raise ValueError("need 256 rolls")
    v = 0
    for r in rolls:
        if r < 1 or r > 6:
            raise ValueError("die face")
        v = (v << 1) | (0 if r <= 3 else 1)
    return v


def fingerprint_words(address, wordlist):
    h = sha256(address.encode())
    out = []
    for i in range(4):
        idx = (h[i * 2] << 8 | h[i * 2 + 1]) % len(wordlist)
        out.append(wordlist[idx])
    return out


def p2tr_address(d, hrp="bc"):
    d2, px = xonly_pubkey(d)
    qx, _t = taproot_output_key(px)
    return bech32m_encode(hrp, 1, qx), d2, px, qx


def birth(key_rolls, pad_rolls, wordlist, hrp="bc"):
    # returns plate values + address; reroll if k==0 or k>=n (p < 2^-127)
    k = rolls_to_int(key_rolls)
    p = rolls_to_int(pad_rolls)
    if k == 0 or k >= N:
        raise ValueError("reroll key from scratch")
    if p == 0 or p >= (1 << 256):
        raise ValueError("bad pad")
    plate_b = k ^ p
    addr, d2, px, qx = p2tr_address(k, hrp)
    words = fingerprint_words(addr, wordlist)
    return {
        "k": k,
        "p": p,
        "plate_a": p,
        "plate_b": plate_b,
        "address": addr,
        "fingerprint": words,
        "internal_pubkey": px,
        "output_pubkey": qx,
        "d_even": d2,
    }


def schnorr_sign(d, msg, aux_rand=None):
    # BIP340; default aux_rand = 32 zero bytes (deterministic, byte-identical)
    # Physics authors all randomness — no RNG; aux_rand fixed zeros.
    if aux_rand is None:
        aux_rand = bytes(32)
    if len(aux_rand) != 32:
        raise ValueError("aux_rand")
    d, px = xonly_pubkey(d)
    t = bytes(a ^ b for a, b in zip(d.to_bytes(32, "big"), tagged_hash("BIP0340/aux", aux_rand)))
    k0 = int.from_bytes(tagged_hash("BIP0340/nonce", t + px + msg), "big") % N
    if k0 == 0:
        raise ValueError("nonce")
    Rx, Ry = _mul(k0)
    k = k0 if (Ry % 2 == 0) else (N - k0)
    e = int.from_bytes(tagged_hash("BIP0340/challenge", Rx.to_bytes(32, "big") + px + msg), "big") % N
    S = (k + e * d) % N
    return Rx.to_bytes(32, "big") + S.to_bytes(32, "big")


def schnorr_verify(pubkey, msg, sig):
    if len(pubkey) != 32 or len(sig) != 64:
        return False
    px = int.from_bytes(pubkey, "big")
    r = int.from_bytes(sig[:32], "big")
    s = int.from_bytes(sig[32:], "big")
    if px >= P or r >= P or s >= N:
        return False
    y2 = (pow(px, 3, P) + 7) % P
    y = pow(y2, (P + 1) // 4, P)
    if (y * y) % P != y2:
        return False
    if y & 1:
        y = P - y
    e = int.from_bytes(tagged_hash("BIP0340/challenge", sig[:32] + pubkey + msg), "big") % N
    sG = _mul(s)
    eP = _mul(e, px, y)
    X, Y, Z = _jadd(sG[0], sG[1], 1, eP[0], (P - eP[1]) % P, 1)
    R = _from_j(X, Y, Z)
    if R is None or (R[1] % 2 != 0) or R[0] != r:
        return False
    return True
