#!/usr/bin/env python3
"""
recover.py — XOR two plates, derive the address, search near-misses.

Imports address derivation from src/. Does not reimplement the curve.

    python3 tools/recover.py --self-test
    python3 tools/recover.py --plate-a BITS --plate-b BITS --address bc1p...

BITS is 256 characters of 0/1 (whitespace ignored) or 64 hex chars.

Search is a convenience, not a guarantee. Default is Hamming
distance 0 then 1 then 2. Distance 3 is ~2.7 million scalar muls
(--max-flips 3) and prints progress so a silent terminal is not
mistaken for a hang. Beyond three bits you are not recovering:
the plate failed, and the other copy is the recovery path.

A match prints plate-grid cells (row 0–F, col 0–F) for every
corrected bit. Go look at those punches. If a mark is clean and
unambiguous, STOP — something else is wrong.
"""

import argparse
import io
import itertools
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))

import birth_duo as duo  # noqa: E402
import birth_pico as pico  # noqa: E402

N = pico.N
HEX = "0123456789ABCDEF"
COMBOS_AT = {
    0: 1,
    1: 256,
    2: 32640,
    3: 2763520,
}

# Overridable in --self-test so fail-clean at max-flips 3 can
# enumerate 2.7M candidates without hours of scalar muls.
_derive = None


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


def bit_cell(bit):
    """LSB bit index → 16×16 plate cell, MSB-first row-major (0–F)."""
    cell = 255 - bit
    row, col = divmod(cell, 16)
    return "row %s col %s" % (HEX[row], HEX[col])


def format_cells(positions):
    return ", ".join(bit_cell(b) for b in positions)


def _progress(d, seen, total):
    if d < 3:
        return
    if seen == 1 or seen % 50000 == 0 or seen == total:
        sys.stderr.write("distance %d: %d/%d\n" % (d, seen, total))
        sys.stderr.flush()


def search(k0, stamped, hrp, max_flips):
    """Return (distance, k, positions) or None.

    positions are LSB bit indices of the corrections applied to k0.
    """
    derive = _derive or derive_pico
    for d in range(0, max_flips + 1):
        if d == 0:
            combos = [()]
            total = 1
        else:
            combos = itertools.combinations(range(256), d)
            total = COMBOS_AT[d]
        seen = 0
        for pos in combos:
            seen += 1
            _progress(d, seen, total)
            k = flipped(k0, pos)
            addr = derive(k, hrp)
            if addr is None:
                continue
            if addr == stamped:
                if confirm_both(k, hrp) != stamped:
                    raise SystemExit("impl mismatch on matching candidate")
                return d, k, pos
    return None


def print_match(d, k, positions, stamped):
    print("match at distance %d" % d)
    if d == 0:
        print("k = %064x" % k)
        print("address = %s" % stamped)
        return
    print("corrected: %s" % format_cells(positions))
    print("CHECK THESE PUNCHES ON THE PLATE before trusting this key.")
    print("If either mark is clean and unambiguous, STOP — something else is wrong.")
    print("k = %064x" % k)
    print("address = %s" % stamped)


def print_no_match(max_flips):
    print("no match within distance %d." % max_flips)
    print("do not guess bits. re-transcribe. treat unreadable glyphs as erasures.")
    print("beyond three bits this tool is not recovery; the other copy of the plate is.")


def _hex256(n):
    return "%064x" % n


def self_test():
    global _derive
    hrp = "bc"
    k = 1
    p = 2
    plate_a = p
    plate_b = k ^ p
    stamped = confirm_both(k, hrp)
    if stamped is None:
        raise SystemExit("self-test: k=1 must derive")

    got = search(plate_a ^ plate_b, stamped, hrp, max_flips=0)
    if got != (0, k, ()):
        raise SystemExit("self-test: clean XOR failed")

    one_pos = (7,)
    one = flipped(k, one_pos)
    got = search(one, stamped, hrp, max_flips=1)
    if got != (1, k, one_pos):
        raise SystemExit("self-test: 1-bit search failed")
    if format_cells(one_pos) != "row F col 8":
        raise SystemExit("self-test: cell map for bit 7 was %r" % format_cells(one_pos))

    # Not (0, 1) — that is the first combinations() pair.
    two_pos = (19, 183)
    two = flipped(k, two_pos)
    miss = search(two, stamped, hrp, max_flips=1)
    if miss is not None:
        raise SystemExit("self-test: 2-bit error must miss at max-flips=1")
    got = search(two, stamped, hrp, max_flips=2)
    if got[0] != 2 or got[1] != k or tuple(sorted(got[2])) != tuple(sorted(two_pos)):
        raise SystemExit("self-test: 2-bit search failed")

    # Not (0, 1, 2) — that is the first combinations() triple.
    three_pos = (0, 1, 40)
    three = flipped(k, three_pos)
    got = search(three, stamped, hrp, max_flips=3)
    if got[0] != 3 or got[1] != k or tuple(sorted(got[2])) != tuple(sorted(three_pos)):
        raise SystemExit("self-test: 3-bit search failed")

    four = flipped(k, (3, 5, 8, 13))
    calls = [0]

    def never_match(cand, hrp_):
        calls[0] += 1
        return "bc1pnottheaddress000000000000000000000000000000000000000"

    _derive = never_match
    try:
        buf = io.StringIO()
        old_out = sys.stdout
        sys.stdout = buf
        try:
            rc = main([
                "--plate-a", _hex256(plate_a),
                "--plate-b", _hex256(plate_b ^ (k ^ four)),
                "--address", stamped,
                "--max-flips", "3",
            ])
        finally:
            sys.stdout = old_out
    finally:
        _derive = None

    out = buf.getvalue()
    expect = 1 + 256 + 32640 + 2763520
    if calls[0] != expect:
        raise SystemExit("self-test: fail-clean enumerated %d, want %d" % (calls[0], expect))
    if rc != 1:
        raise SystemExit("self-test: fail-clean must exit 1")
    if "do not guess bits" not in out:
        raise SystemExit("self-test: fail-clean did not print the do-not-guess message")
    if "other copy of the plate" not in out:
        raise SystemExit("self-test: fail-clean did not name the other copy")

    print("self-test ok: distance 0, 1, 2 (not first pair), 3 (not first triple);")
    print("fail-clean at max-flips 3 enumerated %d and printed do-not-guess" % expect)
    return 0


def main(argv):
    ap = argparse.ArgumentParser(
        description=(
            "XOR two plates and search near-misses against the stamped "
            "address. Convenience, not a guarantee: beyond three bits "
            "the plate failed and the other copy is the recovery path."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
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
        print_no_match(args.max_flips)
        return 1
    d, k, positions = hit
    print_match(d, k, positions, stamped)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
