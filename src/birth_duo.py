# birth_duo.py — implementation #2 (Milk-V Duo / desktop)
# SEAT-WARMER pending independent rewrite by a second human author.
# Written in the same session as birth_pico.py; structure and algorithms
# differ on purpose, but that is not independence. See DECISIONS.md.
#
# Physics authors all randomness. No RNG calls in this file.
# Secrets stay in RAM; this module never opens a file for write.

# Field prime and curve order stated as decimal strings then parsed —
# different presentation from birth_pico's hex literals.
_P = int("115792089237316195423570985008687907853269984665640564039457584007908834671663")
_N = int("115792089237316195423570985008687907852837564279074904382605163141518161494337")
_GX = int("55066263022277343669578718895168534326250603453777594175500187360389116729240")
_GY = int("32670510020758816978083085130507043184471273380659243275938904335757337482424")

# SHA-256 IV and round constants packed as big-endian words from a flat hex blob
# (different phrasing than birth_pico's list literal).
_IVHEX = (
    "6a09e667bb67ae853c6ef372a54ff53a510e527f9b05688c1f83d9ab5be0cd19"
)
_RKHEX = (
    "428a2f9871374491b5c0fbcfe9b5dba53956c25b59f111f1923f82a4ab1c5ed5"
    "d807aa9812835b01243185be550c7dc372be5d7480deb1fe9bdc06a7c19bf174"
    "e49b69c1efbe47860fc19dc6240ca1cc2de92c6f4a7484aa5cb0a9dc76f988da"
    "983e5152a831c66db00327c8bf597fc7c6e00bf3d5a7914706ca635114292967"
    "27b70a852e1b21384d2c6dfc53380d13650a7354766a0abb81c2c92e92722c85"
    "a2bfe8a1a81a664bc24b8b70c76c51a3d192e819d6990624f40e3585106aa070"
    "19a4c1161e376c082748774c34b0bcb5391c0cb34ed8aa4a5b9cca4f682e6ff3"
    "748f82ee78a5636f84c878148cc7020890befffaa4506cebbef9a3f7c67178f2"
)


def _words(hexstr):
    b = bytes.fromhex(hexstr)
    return [int.from_bytes(b[i:i + 4], "big") for i in range(0, len(b), 4)]


_IV = _words(_IVHEX)
_RK = _words(_RKHEX)


def _rr(v, n):
    return ((v >> n) | ((v << (32 - n)) & 0xFFFFFFFF)) & 0xFFFFFFFF


def sha256(blob):
    """SHA-256; accepts bytes or str. Independent code path from birth_pico."""
    data = blob.encode() if isinstance(blob, str) else bytes(blob)
    bitlen = len(data) * 8
    data += b"\x80"
    while (len(data) % 64) != 56:
        data += b"\x00"
    data += bitlen.to_bytes(8, "big")
    state = list(_IV)
    for base in range(0, len(data), 64):
        block = data[base:base + 64]
        w = [int.from_bytes(block[i:i + 4], "big") for i in range(0, 64, 4)]
        for t in range(16, 64):
            x = w[t - 15]
            y = w[t - 2]
            s0 = _rr(x, 7) ^ _rr(x, 18) ^ (x >> 3)
            s1 = _rr(y, 17) ^ _rr(y, 19) ^ (y >> 10)
            w.append((w[t - 16] + s0 + w[t - 7] + s1) & 0xFFFFFFFF)
        a, b, c, d, e, f, g, h = state
        for t in range(64):
            t1 = (h + (_rr(e, 6) ^ _rr(e, 11) ^ _rr(e, 25)) + ((e & f) ^ ((~e) & g)) + _RK[t] + w[t]) & 0xFFFFFFFF
            t2 = ((_rr(a, 2) ^ _rr(a, 13) ^ _rr(a, 22)) + ((a & b) ^ (a & c) ^ (b & c))) & 0xFFFFFFFF
            h, g, f, e, d, c, b, a = g, f, e, (d + t1) & 0xFFFFFFFF, c, b, a, (t1 + t2) & 0xFFFFFFFF
        state = [(state[i] + [a, b, c, d, e, f, g, h][i]) & 0xFFFFFFFF for i in range(8)]
    out = bytearray()
    for w in state:
        out += w.to_bytes(4, "big")
    return bytes(out)


def tagged_hash(tag, payload):
    th = sha256(tag if isinstance(tag, bytes) else tag.encode())
    return sha256(th + th + payload)


def _inv(x):
    return pow(x, _P - 2, _P)


def _ladder(k, ax, ay):
    # Montgomery-ladder-style constant schedule over affine points:
    # always double R1 and conditionally swap — different from pico double-and-add.
    r0x, r0y, r0inf = 0, 0, True
    r1x, r1y, r1inf = ax, ay, False
    for bit in range(k.bit_length() - 1, -1, -1):
        if ((k >> bit) & 1) == 0:
            # R1 = R0+R1; R0 = 2*R0
            r1x, r1y, r1inf = _add(r0x, r0y, r0inf, r1x, r1y, r1inf)
            r0x, r0y, r0inf = _dbl(r0x, r0y, r0inf)
        else:
            r0x, r0y, r0inf = _add(r0x, r0y, r0inf, r1x, r1y, r1inf)
            r1x, r1y, r1inf = _dbl(r1x, r1y, r1inf)
    if r0inf:
        return None
    return r0x, r0y


def _dbl(x, y, inf):
    if inf or y == 0:
        return 0, 0, True
    l = (3 * x * x * _inv((2 * y) % _P)) % _P
    x2 = (l * l - 2 * x) % _P
    y2 = (l * (x - x2) - y) % _P
    return x2, y2, False


def _add(x1, y1, i1, x2, y2, i2):
    if i1:
        return x2, y2, i2
    if i2:
        return x1, y1, i1
    if x1 == x2:
        if (y1 + y2) % _P == 0:
            return 0, 0, True
        return _dbl(x1, y1, False)
    l = ((y2 - y1) * _inv((x2 - x1) % _P)) % _P
    x3 = (l * l - x1 - x2) % _P
    y3 = (l * (x1 - x3) - y1) % _P
    return x3, y3, False


def xonly_pubkey(secret):
    if secret <= 0 or secret >= _N:
        raise ValueError("bad key")
    pt = _ladder(secret, _GX, _GY)
    x, y = pt
    if y & 1:
        secret = _N - secret
        y = _P - y
    return secret, x.to_bytes(32, "big")


def taproot_output_key(internal_xonly):
    tweak = int.from_bytes(tagged_hash("TapTweak", internal_xonly), "big")
    if tweak >= _N:
        raise ValueError("tweak")
    x = int.from_bytes(internal_xonly, "big")
    ysq = (pow(x, 3, _P) + 7) % _P
    y = pow(ysq, (_P + 1) // 4, _P)
    if (y * y) % _P != ysq:
        raise ValueError("lift")
    if y & 1:
        y = _P - y
    tx, ty = _ladder(tweak, _GX, _GY)
    qx, qy, _ = _add(x, y, False, tx, ty, False)
    return qx.to_bytes(32, "big"), tweak


_B32 = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
_GEN = (0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3)
_BECH32M = 0x2bc830a3


def _pm(values):
    c = 1
    for v in values:
        top = c >> 25
        c = ((c & 0x1ffffff) << 5) ^ v
        for i in range(5):
            if (top >> i) & 1:
                c ^= _GEN[i]
    return c


def _hrp_ex(hrp):
    return [ord(ch) >> 5 for ch in hrp] + [0] + [ord(ch) & 31 for ch in hrp]


def bech32m_encode(hrp, ver, prog):
    payload = [ver]
    buf = nbits = 0
    for byte in prog:
        buf = (buf << 8) | byte
        nbits += 8
        while nbits >= 5:
            nbits -= 5
            payload.append((buf >> nbits) & 31)
    if nbits:
        payload.append((buf << (5 - nbits)) & 31)
    pm = _pm(_hrp_ex(hrp) + payload + [0] * 6) ^ _BECH32M
    chk = [(pm >> 5 * (5 - i)) & 31 for i in range(6)]
    return hrp + "1" + "".join(_B32[i] for i in payload + chk)


def bech32m_decode(addr):
    low = addr.lower()
    if low != addr and addr.upper() != addr:
        raise ValueError("case")
    i = low.rfind("1")
    hrp = low[:i]
    vals = [_B32.index(ch) for ch in low[i + 1:]]
    if _pm(_hrp_ex(hrp) + vals) != _BECH32M:
        raise ValueError("chk")
    body = vals[:-6]
    ver = body[0]
    buf = nbits = 0
    out = bytearray()
    for v in body[1:]:
        buf = (buf << 5) | v
        nbits += 5
        if nbits >= 8:
            nbits -= 8
            out.append((buf >> nbits) & 0xFF)
    return hrp, ver, bytes(out)


def rolls_to_int(faces):
    if len(faces) != 256:
        raise ValueError("256 rolls required")
    acc = 0
    for face in faces:
        if face < 1 or face > 6:
            raise ValueError("face")
        acc = (acc << 1) | (1 if face >= 4 else 0)
    return acc


def fingerprint_words(address, words):
    digest = sha256(address.encode())
    return [words[((digest[2 * i] << 8) | digest[2 * i + 1]) % len(words)] for i in range(4)]


def p2tr_address(secret, hrp="bc"):
    sec, px = xonly_pubkey(secret)
    qx, tw = taproot_output_key(px)
    return bech32m_encode(hrp, 1, qx), sec, px, qx


def birth(key_rolls, pad_rolls, wordlist, hrp="bc"):
    key = rolls_to_int(key_rolls)
    pad = rolls_to_int(pad_rolls)
    if key == 0 or key >= _N:
        raise ValueError("reroll key from scratch")
    xor_plate = key ^ pad
    addr, sec, px, qx = p2tr_address(key, hrp)
    return {
        "k": key,
        "p": pad,
        "plate_a": pad,
        "plate_b": xor_plate,
        "address": addr,
        "fingerprint": fingerprint_words(addr, wordlist),
        "internal_pubkey": px,
        "output_pubkey": qx,
        "d_even": sec,
    }


def schnorr_sign(secret, message, aux_rand=None):
    # BIP340 with fixed aux_rand of 32 zero bytes unless overridden by vectors.
    # Physics authors all randomness — no RNG.
    aux = bytes(32) if aux_rand is None else aux_rand
    if len(aux) != 32:
        raise ValueError("aux")
    secret, pub = xonly_pubkey(secret)
    mask = tagged_hash("BIP0340/aux", aux)
    t = bytes(secret.to_bytes(32, "big")[i] ^ mask[i] for i in range(32))
    nonce = int.from_bytes(tagged_hash("BIP0340/nonce", t + pub + message), "big") % _N
    if nonce == 0:
        raise ValueError("nonce")
    rx, ry = _ladder(nonce, _GX, _GY)
    if ry & 1:
        nonce = _N - nonce
    e = int.from_bytes(tagged_hash("BIP0340/challenge", rx.to_bytes(32, "big") + pub + message), "big") % _N
    s = (nonce + e * secret) % _N
    return rx.to_bytes(32, "big") + s.to_bytes(32, "big")


def schnorr_verify(pubkey, message, signature):
    if len(pubkey) != 32 or len(signature) != 64:
        return False
    x = int.from_bytes(pubkey, "big")
    r = int.from_bytes(signature[:32], "big")
    s = int.from_bytes(signature[32:], "big")
    if x >= _P or r >= _P or s >= _N:
        return False
    ysq = (pow(x, 3, _P) + 7) % _P
    y = pow(ysq, (_P + 1) // 4, _P)
    if (y * y) % _P != ysq:
        return False
    if y & 1:
        y = _P - y
    e = int.from_bytes(tagged_hash("BIP0340/challenge", signature[:32] + pubkey + message), "big") % _N
    sx, sy = _ladder(s, _GX, _GY)
    ex, ey = _ladder(e, x, y)
    rx, ry, inf = _add(sx, sy, False, ex, (_P - ey) % _P, False)
    if inf or (ry & 1) or rx != r:
        return False
    return True
