#!/usr/bin/env python3
"""
check_docs.py -- fails the commit when a claim drifts.

Four commits in this repo exist only because a claim was fixed in one
place and left standing in another. dice2words.py --test makes bad math
impossible to ship; this makes stale claims impossible to ship. Same
idea, applied to prose.

It checks four things:

  1. RETRACTED CLAIMS. Wording we have publicly withdrawn must not
     reappear in any live file. CHANGELOG.md is exempt -- it is a
     record of what we said, not a claim we are making.

  2. THE NUMBERS AGREE. The receive-address count is stated in
     PROTOCOL.md, in README.md's diagram, and inside an image. All
     three must say the same thing.

  3. THE IMAGES HAVE TEXT TWINS. Claims rendered into a PNG are
     invisible to grep -- that is how "50 addresses" survived on the
     front page for a day. Every image must have a committed .txt
     source, and that text is checked like any other file.

  4. NO VERSION SELF-DESCRIPTIONS. A file that names its own version
     goes stale on the next commit. CHANGELOG.md carries versions;
     nothing else should. Deleting the claim beats maintaining it.

USAGE:
    python3 check_docs.py          # exit 0 = clean, 1 = drift found

Run it beside the vector test before every commit:
    python3 dice2words.py --test && python3 check_docs.py

WHAT THIS DOES NOT DO: it cannot read pixels. It checks the .txt twin
that the PNG is generated from. If someone edits a PNG by hand instead
of regenerating it from the text, this will not catch that -- which is
exactly why images are generated, never hand-edited.
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# A record of what we said is not a claim we are making.
EXEMPT = {"CHANGELOG.md"}

# Live files: everything whose words are a current claim.
LIVE = ["README.md", "PROTOCOL.md", "HARDCORE.md", "CONTRIBUTING.md",
        "SECURITY.md", "dice2words.py", "img/reply-card.txt",
        "img/poster.txt"]

# Wording we have withdrawn. Left side: the dead phrase. Right side:
# why it died, printed when it reappears.
RETRACTED = [
    ("only trust mechanism",
     "v0.3 demoted dual machines to a fault detector"),
    ("only be right, or be caught",
     "v0.3: identical twins catch faults, not lies"),
    ("only cross-examined",
     "v0.3: same reframe, this phrasing lived in the images"),
    ("small, measurable",
     "v0.3.2: bias is tolerated, not measured"),
    ("50 addresses",
     "v0.3.3: the sheet is 20"),
    ("5-10 receiv",
     "v0.3.3: the sheet is 20"),
    ("5\u201310 receiv",
     "v0.3.3: the sheet is 20"),
    ("100+ rolls",
     "v0.3.3: the key is 128 rolls; 120 is the dice test"),
    ("mandatory by tradition",
     "v0.3: the sledgehammer is optional"),
]

# Every image must have a text twin, or its claims are unsearchable.
IMAGE_TWINS = {
    "img/dice-math-steel-reply.png": "img/reply-card.txt",
    "img/dice-math-steel-poster.png": "img/poster.txt",
}

# Files that must agree on the receive-address count.
COUNT_SOURCES = ["PROTOCOL.md", "README.md", "img/reply-card.txt"]
COUNT_PATTERN = re.compile(r"(\d+)\s+receiv|(\d+)\s+addresses")

# A file naming its own version is a claim with an expiry date.
# The tell is grammatical: a self-description puts the name first
# ("Dice Math Steel, v0.2"), while history puts the version first
# ("v0.2 maps rolls directly", "(v0.2, done)"). Only the former
# goes stale, so only the former is flagged.
SELF_NAMES = ["dice math steel", "dice2words.py"]
VERSION_SELF = re.compile(r"\bv\d+\.\d+")


def read(path):
    full = os.path.join(HERE, path)
    if not os.path.exists(full):
        return None
    with open(full, encoding="utf-8") as f:
        return f.read()


def check_retracted(problems):
    for path in LIVE:
        if path in EXEMPT:
            continue
        text = read(path)
        if text is None:
            continue
        low = text.lower()
        for phrase, why in RETRACTED:
            if phrase.lower() in low:
                line = low[:low.index(phrase.lower())].count("\n") + 1
                problems.append(
                    f"{path}:{line}: retracted wording {phrase!r}\n"
                    f"    ({why})")


def check_counts(problems):
    found = {}
    for path in COUNT_SOURCES:
        text = read(path)
        if text is None:
            continue
        hits = set()
        for m in COUNT_PATTERN.finditer(text):
            hits.add(m.group(1) or m.group(2))
        if hits:
            found[path] = hits
    values = set()
    for hits in found.values():
        values |= hits
    if len(values) > 1:
        detail = "; ".join(f"{p}: {sorted(v)}" for p, v in found.items())
        problems.append(
            f"receive-address count disagrees across files -> {detail}")


def check_image_twins(problems):
    for image, twin in IMAGE_TWINS.items():
        if read(twin) is None:
            problems.append(
                f"{image} has no text twin at {twin}\n"
                f"    (claims inside an image are invisible to grep)")


def check_version_self(problems):
    for path in LIVE:
        text = read(path)
        if text is None:
            continue
        for i, line_text in enumerate(text.split("\n"), 1):
            m = VERSION_SELF.search(line_text)
            if not m:
                continue
            before = line_text[:m.start()].lower()
            if any(name in before for name in SELF_NAMES):
                problems.append(
                    f"{path}:{i}: names its own version ({m.group(0)})\n"
                    f"    (CHANGELOG.md carries versions; this one goes "
                    f"stale on the next commit)")


if __name__ == "__main__":
    problems = []
    check_retracted(problems)
    check_counts(problems)
    check_image_twins(problems)
    check_version_self(problems)

    if problems:
        print(f"\nDRIFT: {len(problems)} problem(s)\n")
        for p in problems:
            print(f"  {p}")
        print("\nFix these before committing, or add the wording to "
              "CHANGELOG's\nexempt list if it is a historical record "
              "rather than a live claim.\n")
        sys.exit(1)

    print("Docs clean: no retracted wording, numbers agree, images "
          "have text twins.")
