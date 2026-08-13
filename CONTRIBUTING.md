# Contributing

This project's review process is public attack. **Breaking this
is the contribution.** Here's how to aim it.

**Design-level critique** (trust model, bias math, protocol logic):
open an issue. Bring your reasoning; expect engagement. Good-faith
critics get credited in the README whether or not they're right.

**Code changes:** pull requests against `main`. Ground rules that
will not bend:

- Standard library only. A dependency is a trusted party.
- Short enough to read completely. If your PR doubles the line
  count, it needs to halve something else.
- Every change to birth or signing logic must keep
  `python3 tests/vectors_test.py` passing on **both**
  implementations, byte-identical where the protocol requires
  agreement.
- Explicit over clever. This code's audience includes people
  reading Python for the first time because their money depends
  on it.
- Implementation #2 needs a second human author. Same-model
  dual files are seat-warmers (DECISIONS.md).

**When a claim changes:** grep the whole repo for the old wording
before you commit. `check_docs.py` automates the known
retractions; it does not replace reading your own diff against
the rest of the tree. Claims rendered into an image are invisible
to grep, which is why both cards are generated from committed
text (`img/reply-card.txt`, `img/poster.txt`). Change the text,
regenerate the image, never hand-edit an image's words.

**Exploitable vulnerabilities:** SECURITY.md, privately, first.

**Style of argument:** attack the idea as hard as you like; the
maintainer will do the same. "This is wrong because X" with X
attached is the house currency.
