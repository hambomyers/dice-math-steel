# archive/

Historical files, not live protocol.

- `dice2words_v0.1.py` — v0.2 BIP39 entrypoint, retired.
- `table.txt` — dice-to-word lookup for that entrypoint. Unused by
  `src/`. Retired 2026-08-12.
- `vectors.json` — BIP39 test vectors for that entrypoint. Live
  tests use `tests/vectors/` (BIP340/341/350). Retired 2026-08-12.

`english.txt` stays at repo root: the 4-word address fingerprint
on plate B is drawn from this 2048-word list. `src/` takes the
list as an argument and does not open the file; the ceremony
still needs a committed list.
