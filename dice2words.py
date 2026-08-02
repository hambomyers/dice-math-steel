#!/usr/bin/env python3
"""
dice2words.py v0.2 -- the machine checks your homework. It never does it.

    WARNING -- EXPERIMENTAL, UNREVIEWED. Do NOT use with real funds.
    Signet or throwaway amounts only, until strangers have broken this.

WHAT CHANGED FROM v0.1 (and why):
  v0.1 hashed your dice rolls into entropy. That made the COMPUTER the
  author of your key -- you could not verify one word without a second
  machine. v0.2 inverts authorship: YOU derive all 128 entropy bits at
  a table, from dice and a printed wordlist (see TABLE.md). This program
  is demoted to two jobs, in both of which it has ZERO choices:

    finish : you type your 11 table-derived words + 7 final bits;
             it computes the SHA-256 checksum and names the ONE word
             that can legally complete your sentence. Right or provably
             wrong -- a wrong answer is an invalid mnemonic that every
             wallet on earth rejects. It authors nothing.
    check  : you type 12 words; it verifies the checksum. A proofreader
             for transcription and recovery drills.

  (* Hardcore variant: even the checksum can be done without this
     program. By hand: SHA-256 with pencil and printed constant tables,
     a few hours, done by hobbyists. Or blind brute force: 1 word in 16
     passes the 4-bit checksum, so try table-ordered candidates against
     an offline wallet until one is accepted. See HARDCORE.md. *)

DELETIONS in this version, deliberately:
  - 24-word mode. 128 bits is sufficient; two modes means twice the
    mistakes. (* Hardcore: 24 words is a trivial patch -- see the
    experiments branch. *)
  - Hash-whitening of dice. Direct table mapping passes dice bias
    straight into the key; we accept that trade because casino dice
    plus the tally test (README) make bias small, measurable, and
    non-adversarial, while machine-authored keys are exactly the
    adversarial category this protocol exists to escape. This is the
    protocol's most attackable decision. Attack it.

KNOWN TRUSTED PARTS, stated instead of hidden:
  - The Python runtime under these ~150 lines is millions of lines we
    did not audit. Defense: run this on TWO unrelated machines; outputs
    must match exactly. We cross-examine computers, we do not trust them.
  - english.txt (official BIP39 wordlist) is verified by SHA-256 below
    and kept as a separate file on purpose: the PRINTED wordlist is
    load-bearing in this protocol, so the file must exist to be printed
    and independently checked (sha256sum english.txt).

USAGE:
  python3 dice2words.py --test      run official BIP39 vectors + round-trip
  python3 dice2words.py finish      11 words + 7 bits -> the final word
  python3 dice2words.py check       12 words -> checksum valid or not
"""

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORDLIST_SHA256 = "2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda"

# Dice-to-bit convention, identical to TABLE.md: 1,2,3 -> 0   4,5,6 -> 1
# One fair roll = exactly one uniform bit. No rejection, no arithmetic,
# no bias from the 6-vs-2048 mismatch that plagues base-6 mappings.
BIT = {"1": "0", "2": "0", "3": "0", "4": "1", "5": "1", "6": "1"}


def load_wordlist():
    with open(os.path.join(HERE, "english.txt"), "rb") as f:
        raw = f.read()
    if hashlib.sha256(raw).hexdigest() != WORDLIST_SHA256:
        sys.exit("FATAL: english.txt hash mismatch -- wordlist may be tampered.")
    words = raw.decode().split()
    assert len(words) == 2048
    return words


def checksum_bits(entropy: bytes) -> str:
    """First 4 bits of SHA-256(entropy). This is BIP39's typo detector.
    It adds NO secrecy -- it exists so a misread word fails loudly at
    recovery instead of silently stranding your coins."""
    return format(hashlib.sha256(entropy).digest()[0], "08b")[:4]


def words_to_bits(words, wordlist) -> str:
    out = []
    for w in words:
        if w not in wordlist:
            sys.exit(f"'{w}' is not on the BIP39 wordlist. Check your table work.")
        out.append(format(wordlist.index(w), "011b"))
    return "".join(out)


def finish(wordlist):
    print("Your 11 words from the table, in order, separated by spaces:")
    words = input("> ").split()
    if len(words) != 11:
        sys.exit(f"Need exactly 11 words, got {len(words)}.")
    print("Your 7 final dice rolls (1-6):")
    rolls = "".join(input("> ").split())
    if len(rolls) != 7 or set(rolls) - set("123456"):
        sys.exit("Need exactly 7 rolls, digits 1-6 only.")

    bits = words_to_bits(words, wordlist) + "".join(BIT[r] for r in rolls)
    assert len(bits) == 128  # every one of these bits came from YOUR hands
    entropy = int(bits, 2).to_bytes(16, "big")

    # The forced move: 7 of your bits + 4 checksum bits = one legal word.
    final = wordlist[int(bits[121:] + checksum_bits(entropy), 2)]
    print(f"\nThe only valid 12th word for your sequence:\n\n    12. {final}\n")
    print("Run this SAME input on your second machine. It must name the")
    print("same word. Then confirm the full 12 words in an unrelated")
    print("wallet app -- an invalid checksum will be rejected instantly.")


def check(wordlist):
    print("All 12 words, in order:")
    words = input("> ").split()
    if len(words) != 12:
        sys.exit(f"Need exactly 12 words, got {len(words)}.")
    bits = words_to_bits(words, wordlist)
    entropy = int(bits[:128], 2).to_bytes(16, "big")
    if bits[128:] == checksum_bits(entropy):
        print("\nChecksum VALID. Transcription is internally consistent.")
    else:
        print("\nChecksum INVALID -- a word is wrong, missing, or out of")
        print("order. Do not stamp steel from this. Recheck your table work.")


def run_tests(wordlist):
    """Two proofs, run them on any machine before believing this file:
    1. Official BIP39 vectors (Trezor reference): entropy -> mnemonic
       and mnemonic -> seed must match the reference exactly.
    2. Round-trip: split each 128-bit vector into 11 words + 7 bits,
       run our 'finish' math, and the forced 12th word must equal the
       reference mnemonic's 12th word. Proves the kitchen-table protocol
       and standard BIP39 are the same mathematics."""
    with open(os.path.join(HERE, "vectors.json")) as f:
        vectors = [v for v in json.load(f)["english"] if len(v[0]) == 32]

    fails = 0
    for ent_hex, ref_mnemonic, ref_seed, _ in vectors:
        entropy = bytes.fromhex(ent_hex)
        bits = format(int.from_bytes(entropy, "big"), "0128b")
        words = [wordlist[int(bits[i:i + 11], 2)] for i in range(0, 121, 11)]
        forced = wordlist[int(bits[121:] + checksum_bits(entropy), 2)]
        mnemonic = " ".join(words + [forced])
        seed = hashlib.pbkdf2_hmac("sha512", mnemonic.encode(),
                                   b"mnemonicTREZOR", 2048, 64).hex()
        ok = mnemonic == ref_mnemonic and seed == ref_seed
        fails += 0 if ok else 1
        print("PASS" if ok else "FAIL", ent_hex[:16] + "...")
    print()
    if fails:
        sys.exit(f"{fails} FAILED -- do not use.")
    print(f"All {len(vectors)} vectors passed, including 11-words+7-bits round-trip.")


if __name__ == "__main__":
    wl = load_wordlist()
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "--test":
        run_tests(wl)
    elif cmd == "finish":
        finish(wl)
    elif cmd == "check":
        check(wl)
    else:
        print(__doc__)
