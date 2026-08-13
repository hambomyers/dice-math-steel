# KEY READING — optional appendix, not the protocol

**These KEY READING words are the key in plaintext.** They are not
the four-word **ADDRESS FINGERPRINT** stamped on plate B. The
fingerprint is a public checksum of the receive address. KEY READING
words *are* the 256-bit number, spoken. Confusing the two is
catastrophic in one direction: an heir who treats the fingerprint as
the key gets nothing; an heir who treats KEY READING as a public
checksum has written the key on the table.

This appendix is optional. Steel stays binary. Words are a channel
for saying the number aloud — not storage, not entropy, not part of
the ceremony that stamps plates.

> *These words are a reading of a number, not a wallet.*

## 25 words, always

256 bits = 23 words + 3 leftover bits. We write **25 words**:

1. Word 1 is the fixed marker **`steel`**.
2. Words 2–24 are the first 253 bits, eleven at a time, looked up
   on `docs/words-table.md` (match the 11-bit row; do not compute
   an index).
3. Word 25 is the last 3 bits, padded as `00000000` plus those
   three, looked up the same way.

BIP39 wallets accept only 12, 15, 18, 21, or 24 words. Twenty-five
is rejected by every such wallet, every time, with no arithmetic.
That is the interlock. An heir who types 24 of our words into a
standard wallet would get a *different, empty wallet* — no error,
no warning. Twenty-five makes that structurally impossible.

Head every KEY READING sheet with the sentence in the blockquote
above, and with the label **KEY READING**. Never stamp these words
on plate B. Plate B already carries **ADDRESS FINGERPRINT**.

## Why a wordlist may be printed, and a dice table may not

A biased dice table is invisible and silently costs entropy. A
tampered wordlist is loud: it decodes to different bits, lands on
a different address, and the mismatch surfaces immediately against
the stamp. Wordlists are gradeable. Dice tables are not. The dice
card is 36 cells for that reason (`docs/dice-card.md`).

Spot-check, committed: `english.txt` has 2,048 distinct words,
alphabetically ordered, first four letters unique.
`python3 tools/make_words_table.py --check`

## Words carry zero error detection

2,048 words against 11 bits is a perfect bijection. A flipped bit
yields a different real word, silently. The stamped address catches
errors; words only verify transcription between two people who can
already see the number.

## Minutes, then burned

Any KEY READING sheet is the plaintext key. Write it, speak it,
confirm the address, burn it. Never stored, never photographed,
never spoken to anyone not holding the coins.
