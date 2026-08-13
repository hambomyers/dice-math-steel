#!/usr/bin/env python3
"""
recover.py — XOR two plates, derive the address, search near-misses.

Imports address derivation from src/. Does not reimplement the curve.

    python3 tools/recover.py --self-test
    python3 tools/recover.py --plate-a BITS --plate-b BITS --address bc1p...

BITS is 256 characters of 0/1 (whitespace ignored) or 64 hex chars.
Default search: Hamming distance 0, then 1, then 2. Distance 3 is
~2.7 million scalar muls — pass --max-flips 3 and wait.

An unreadable glyph is an erasure. Do not guess it by eye.
"""

import argparse
import itertools
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))

import birth_duo as duo  # noqa: E402
import birth_pico as pico  # noqa: E402

N = pico.N


def parse_bits(text):
    raw = "".join(text.split())
    if len(raw) == 64 and all(c in "0123456789abcdefABCDEF" for c in raw):
        v = int(raw, 16)
        if v.bit_length() > 256:
            raise ValueError("hex wider than 256 bits")
        return v
    bits = "".join(c for c in raw if c in "01")
    if len(bits) != 256:
        raise ValueError("need 256 bits or 64 hex chars, got %d chars" % len(bits))
    return int(bits, 2)


def derive_pico(k, hrp):
    if not (0 < k < N):
        return None
    return pico.p2tr_address(k, hrp)[0]


def confirm_both(k, hrp):
    """Accept a candidate only if both lineages agree."""
    addr_p = derive_pico(k, hrp)
    if addr_p is None:
        return None
    addr_d = duo.p2tr_address(k, hrp)[0]
    if addr_p != addr_d:
        raise SystemExit("impl mismatch: pico and duo disagree on address")
    return addr_p


def flipped(k, positions):
    out = k
    for i in positions:
        out ^= 1 << i
    return out


def search(k0, stamped, hrp, max_flips):
    """Yield (distance, k) for candidates; return the match or None."""
    for d in range(0, max_flips + 1):
        if d == 0:
            combos = [()]
        else:
            combos = itertools.combinations(range(256), d)
        for pos in combos:
            k = flipped(k0, pos)
            addr = derive_pico(k, hrp)
            if addr is None:
                continue
            if addr == stamped:
                if confirm_both(k, hrp) != stamped:
                    raise SystemExit("impl mismatch on matching candidate")
                return d, k
    return None


def self_test():
    hrp = "bc"
    k = 1
    p = 2
    plate_a = p
    plate_b = k ^ p
    stamped = confirm_both(k, hrp)
    if stamped is None:
        raise SystemExit("self-test: k=1 must derive")

    got = search(plate_a ^ plate_b, stamped, hrp, max_flips=0)
    if got != (0, k):
        raise SystemExit("self-test: clean XOR failed")

    one = flipped(k, (7,))
    got = search(one, stamped, hrp, max_flips=1)
    if got != (1, k):
        raise SystemExit("self-test: 1-bit search failed")

    two = flipped(k, (0, 1))
    miss = search(two, stamped, hrp, max_flips=1)
    if miss is not None:
        raise SystemExit("self-test: 2-bit error must miss at max-flips=1")
    got = search(two, stamped, hrp, max_flips=2)
    if got != (2, k):
        raise SystemExit("self-test: early 2-bit search failed")

    four = flipped(k, (3, 5, 8, 13))
    miss = search(four, stamped, hrp, max_flips=1)
    if miss is not None:
        raise SystemExit("self-test: 4-bit error must fail clean")

    print("self-test ok: distance 0, 1, early 2; over-corruption fails clean")
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--plate-a")
    ap.add_argument("--plate-b")
    ap.add_argument("--address")
    ap.add_argument("--hrp", default="bc")
    ap.add_argument("--max-flips", type=int, default=2, choices=(0, 1, 2, 3))
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()

    if not (args.plate_a and args.plate_b and args.address):
        ap.error("need --plate-a, --plate-b, and --address (or --self-test)")

    a = parse_bits(args.plate_a)
    b = parse_bits(args.plate_b)
    stamped = args.address.strip()
    k0 = a ^ b
    print("searching Hamming distance 0..%d against stamped address" % args.max_flips)
    hit = search(k0, stamped, args.hrp, args.max_flips)
    if hit is None:
        print("no match within distance %d." % args.max_flips)
        print("do not guess bits. re-transcribe. treat unreadable glyphs as erasures.")
        return 1
    d, k = hit
    print("match at distance %d" % d)
    print("k = %064x" % k)
    print("address = %s" % stamped)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
