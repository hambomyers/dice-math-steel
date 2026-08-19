# archive/DUO_DELETED.md — Duo deletion note (historical)

This repo previously used a second device lineage (“Duo”) to provide
an unrelated implementation for the *spend* ceremony: it would
re-derive the deterministic nonce and disagree if the signer lied.

Decision in v0.7: the witness becomes “any unrelated BIP340
implementation” because two same-author MicroPython files no longer
represent independence. The spend ceremony is then graded by
comparability, demonstrated on signet by **Bitcoin Core** and a
desktop library path (see `docs/rehearsal-signet.md`).

The Duo source files are preserved only for history and reference.
They are no longer required by:

- `tests/vectors_test.py` (it now runs the Pico lineage for the
  pinned vectors)
- `tools/recover.py` (it repoints address derivation to the Pico
  lineage)
- `tools/linecount.py` / `check_docs.py` (crypto line budget now
  excludes Duo files)

Never edit these archived files. If a later pass needs a desktop
reference implementation for recovery logic, repoint imports in
the tool/test harness rather than rewriting crypto code here.

