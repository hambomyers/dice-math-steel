# Contributing

This project's review process is public attack. Here's how to aim it.

**Design-level critique** (trust model, bias math, protocol logic):
open an issue. Bring your reasoning; expect engagement. Good-faith
critics get credited in the README whether or not they're right.

**Code changes:** pull requests against `main` for fixes, against
`experiments` for variants (see HARDCORE.md for the agenda). Ground
rules that will not bend:

- Standard library only. A dependency is a trusted party.
- Short enough to read completely. If your PR doubles the line
  count, it needs to halve something else.
- Every change to derivation logic must keep `--test` passing
  byte-for-byte against the official vectors, and say in the PR
  what new test proves the new behavior.
- Explicit over clever. This code's audience includes people
  reading Python for the first time because their money depends
  on it.

**When a claim changes:** grep the whole repo for the old wording
before you commit. Four commits here exist only because a claim was
fixed in one place and left standing in another. `check_docs.py`
automates the known retractions; it does not replace reading your
own diff against the rest of the tree. Claims rendered into an
image are invisible to grep, which is why both cards are generated
from committed text (`img/reply-card.txt`, `img/poster.txt`).
Change the text, regenerate the image, never hand-edit an image's
words.

**Exploitable vulnerabilities:** SECURITY.md, privately, first.

**Style of argument:** attack the idea as hard as you like; the
maintainer will do the same. "This is wrong because X" with X
attached is the house currency.
