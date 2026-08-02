#!/usr/bin/env python3
"""
dice2words.py -- physical dice rolls in, BIP39 seed words out.

Part of an open, rough-draft cold storage protocol. Read every line.
This file uses ONLY the Python standard library: no pip installs,
no dependencies, nothing to trust except this text and Python itself.

    WARNING -- EXPERIMENTAL, UNREVIEWED CODE.
    Do NOT use with real funds until this has survived public review.
    Test on signet, or with amounts you are happy to lose.

Design rules for this file:
  1. Short enough to read completely over one cup of coffee.
  2. Deterministic: same dice in, same words out, on any machine.
     Run it on TWO different computers and compare word-for-word.
  3. Self-verifying: `python3 dice2words.py --test` checks this code
     against the official BIP39 test vectors (vectors.json, from the
     Trezor reference implementation). Do not trust us -- run the test.

Usage:
  python3 dice2words.py --test          run official test vectors
  python3 dice2words.py                 interactive: enter dice rolls
  echo "3141...52" | python3 dice2words.py --stdin
"""

import hashlib
import hmac
import json
import os
import sys

# ---------------------------------------------------------------------------
# The BIP39 English wordlist. 2048 words, one per line, from the official
# bitcoin/bips repository. We verify its SHA-256 so a tampered wordlist
# fails loudly instead of silently producing wrong (or attacker-chosen) words.
# You can independently confirm this hash: sha256sum english.txt should match
# the file at github.com/bitcoin/bips/blob/master/bip-0039/english.txt
# ---------------------------------------------------------------------------
WORDLIST_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "english.txt")
WORDLIST_SHA256 = "2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda"

# Each fair die roll carries log2(6) ~= 2.585 bits of entropy.
# 12 words need 128 bits -> 50 rolls minimum. We demand 100 (double margin,
# so even a visibly biased die still clears the bar). 24 words: 200 rolls.
MIN_ROLLS = {12: 100, 24: 200}
ENTROPY_BYTES = {12: 16, 24: 32}  # 128 or 256 bits


def load_wordlist():
    with open(WORDLIST_FILE, "rb") as f:
        raw = f.read()
    if hashlib.sha256(raw).hexdigest() != WORDLIST_SHA256:
        sys.exit("FATAL: english.txt hash mismatch -- wordlist may be tampered.")
    words = raw.decode("utf-8").split()
    if len(words) != 2048:
        sys.exit("FATAL: wordlist must contain exactly 2048 words.")
    return words


def entropy_from_dice(dice: str, n_words: int) -> bytes:
    """Hash the dice roll string into seed entropy.

    Why hash instead of converting rolls to binary directly?
    A d6 doesn't map cleanly onto bits (6 is not a power of 2); naive
    conversion introduces bias. SHA-256 distills all the entropy in the
    rolls into a uniform bitstring. The hash is deterministic, so two
    machines given the same rolls MUST produce identical words --
    that cross-check is your defense against a lying computer.
    """
    dice = "".join(dice.split())  # tolerate spaces/newlines between rolls
    if not dice:
        sys.exit("No dice rolls provided.")
    bad = set(dice) - set("123456")
    if bad:
        sys.exit(f"Invalid characters in rolls (only 1-6 allowed): {sorted(bad)}")
    if len(dice) < MIN_ROLLS[n_words]:
        sys.exit(
            f"Only {len(dice)} rolls given; this protocol requires at least "
            f"{MIN_ROLLS[n_words]} for {n_words} words. Keep rolling."
        )
    return hashlib.sha256(dice.encode("ascii")).digest()[: ENTROPY_BYTES[n_words]]


def entropy_to_mnemonic(entropy: bytes, wordlist) -> str:
    """BIP39: entropy -> checksum -> 11-bit indices -> words.

    For 128-bit entropy: checksum is the first 4 bits of SHA-256(entropy),
    giving 132 bits total = twelve 11-bit indices into the 2048-word list.
    Everything here is exactly the BIP39 spec -- verified by --test below.
    """
    ent_bits = len(entropy) * 8
    checksum_bits = ent_bits // 32
    checksum_byte = hashlib.sha256(entropy).digest()[0]

    # Build one long bitstring: entropy || checksum
    bits = bin(int.from_bytes(entropy, "big"))[2:].zfill(ent_bits)
    bits += bin(checksum_byte)[2:].zfill(8)[:checksum_bits]

    words = []
    for i in range(0, len(bits), 11):
        index = int(bits[i : i + 11], 2)
        words.append(wordlist[index])
    return " ".join(words)


def mnemonic_to_seed(mnemonic: str, passphrase: str = "") -> bytes:
    """BIP39: words (+ optional passphrase) -> 64-byte seed, via PBKDF2.

    This seed is what BIP32 derives keys from. The passphrase creates a
    completely different wallet -- store it separately from the words.
    """
    return hashlib.pbkdf2_hmac(
        "sha512",
        mnemonic.encode("utf-8"),
        ("mnemonic" + passphrase).encode("utf-8"),
        2048,
        64,
    )


def run_official_test_vectors() -> None:
    """Check this code against the BIP39 reference test vectors.

    vectors.json comes from the Trezor python-mnemonic repository (the
    reference implementation). Each vector gives: entropy, the expected
    mnemonic, and the expected seed using passphrase 'TREZOR'.
    If any of them fail, DO NOT USE THIS TOOL.
    """
    wordlist = load_wordlist()
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vectors.json")
    with open(path) as f:
        vectors = json.load(f)["english"]

    failures = 0
    for entropy_hex, expected_mnemonic, expected_seed, _xprv in vectors:
        entropy = bytes.fromhex(entropy_hex)
        if len(entropy) not in (16, 20, 24, 28, 32):
            continue
        mnemonic = entropy_to_mnemonic(entropy, wordlist)
        seed = mnemonic_to_seed(mnemonic, "TREZOR").hex()
        ok = mnemonic == expected_mnemonic and seed == expected_seed
        failures += 0 if ok else 1
        print(("PASS" if ok else "FAIL"), entropy_hex[:16] + "...")
    print()
    if failures:
        sys.exit(f"{failures} VECTOR(S) FAILED -- do not use this tool.")
    print(f"All {len(vectors)} official BIP39 test vectors passed.")


def main() -> None:
    if "--test" in sys.argv:
        run_official_test_vectors()
        return

    wordlist = load_wordlist()

    if "--stdin" in sys.argv:
        dice = sys.stdin.read()
    else:
        print("Enter your dice rolls (digits 1-6, spaces ok), blank line to finish:")
        lines = []
        while True:
            line = input("> ").strip()
            if not line:
                break
            lines.append(line)
        dice = "".join(lines)

    n_words = 24 if len("".join(dice.split())) >= MIN_ROLLS[24] else 12
    entropy = entropy_from_dice(dice, n_words)
    mnemonic = entropy_to_mnemonic(entropy, wordlist)

    print(f"\nYour {n_words} seed words (write on paper, then stamp in steel):\n")
    for i, w in enumerate(mnemonic.split(), 1):
        print(f"  {i:2d}. {w}")
    print(
        "\nNow run this SAME input on a SECOND, different computer.\n"
        "The words must match EXACTLY. If they differ, one machine is\n"
        "broken or lying: stop, and start over with fresh rolls.\n"
    )


if __name__ == "__main__":
    main()
