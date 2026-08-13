#!/usr/bin/env python3
"""
check_docs.py -- fails the commit when a claim drifts.

It checks:

  1. RETRACTED CLAIMS. Wording we have publicly withdrawn must not
     reappear in any live file. CHANGELOG.md, DECISIONS.md, and
     HARDCORE.md are exempt where noted — history and appendices
     may name the dead ideas.

  2. THE NUMBERS AGREE. Receive-address count and line counts stated
     in README must match PROTOCOL / tools/linecount.py.

  3. THE IMAGES HAVE TEXT TWINS. Claims rendered into a PNG are
     invisible to grep. Every image must have a committed .txt
     source, and that text is checked like any other file.

  4. NO VERSION SELF-DESCRIPTIONS. CHANGELOG.md carries versions;
     nothing else should name "Dice Math Steel, vX.Y".

USAGE:
    python3 check_docs.py          # exit 0 = clean, 1 = drift found
"""

import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

EXEMPT = {"CHANGELOG.md"}

# Live files: current claims. Historical notes and private plans are out.
LIVE = [
    "README.md", "PROTOCOL.md", "HARDCORE.md", "CONTRIBUTING.md",
    "SECURITY.md", "DECISIONS.md", "docs/rehearsal-signet.md",
    "docs/whitepaper.html",
    "img/reply-card.txt", "img/poster.txt",
]

# v0.3-era retracted phrasing (still banned).
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
     "v0.3.3 sheet size; v0.5 uses 1 address"),
    ("5-10 receiv",
     "v0.3.3 sheet size; v0.5 uses 1 address"),
    ("5\u201310 receiv",
     "v0.3.3 sheet size; v0.5 uses 1 address"),
    ("100+ rolls",
     "v0.6 expected throws are ≈117 per number on the 6×6 card"),
    ("mandatory by tradition",
     "v0.3: the sledgehammer is optional"),
]

# v0.5: these words are dead outside DECISIONS.md and HARDCORE.md.
V05_RETRACTED = [
    "BIP39",
    "mnemonic",
    "passphrase",
    "seed words",
    "12 words",
    "PBKDF2",
    "CD-R",
    "pre-2006",
    "older than Bitcoin",
    "PSBT",
    "xpub",
]
V05_EXEMPT = {"DECISIONS.md", "HARDCORE.md", "CHANGELOG.md"}

IMAGE_TWINS = {
    "img/dice-math-steel-reply.png": "img/reply-card.txt",
    "img/dice-math-steel-poster.png": "img/poster.txt",
}

COUNT_SOURCES = ["PROTOCOL.md", "README.md", "img/reply-card.txt"]
# v0.5: exactly one receive address per key
COUNT_PATTERN = re.compile(
    r"\b([0-9]+)\s+receiv|\b([0-9]+)\s+addresses per key|"
    r"Receive addresses per key\s*\|\s*([0-9]+)",
    re.I,
)

SELF_NAMES = ["dice math steel"]
VERSION_SELF = re.compile(r"\bv\d+\.\d+")

LINECOUNT_FILES = [
    "birth_pico.py", "birth_duo.py", "sign_pico.py", "sign_duo.py", "io_pico.py",
]


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


def check_v05_retracted(problems):
    for path in LIVE:
        if path in V05_EXEMPT or path in EXEMPT:
            continue
        text = read(path)
        if text is None:
            continue
        for phrase in V05_RETRACTED:
            # case-sensitive for acronyms; case-insensitive for phrases
            if phrase.isupper() or any(c.isupper() for c in phrase if c.isalpha()):
                idx = text.find(phrase)
                if idx < 0:
                    idx = text.lower().find(phrase.lower())
                    if idx < 0:
                        continue
                    # found case-insensitive
                else:
                    pass
            else:
                idx = text.lower().find(phrase.lower())
                if idx < 0:
                    continue
            # re-find for line number
            low = text.lower()
            pos = low.find(phrase.lower())
            line = low[:pos].count("\n") + 1
            problems.append(
                f"{path}:{line}: v0.5 retracted wording {phrase!r}\n"
                f"    (allowed only in DECISIONS.md and HARDCORE.md)")


def check_counts(problems):
    # All live mentions of receive-address cardinality must be {1}
    found = {}
    for path in COUNT_SOURCES:
        text = read(path)
        if text is None:
            continue
        hits = set()
        for m in COUNT_PATTERN.finditer(text):
            val = m.group(1) or m.group(2) or m.group(3)
            if val:
                hits.add(val)
        # also catch "one key, one ... address"
        if re.search(r"\b1\b.*\baddress|\bone\b.*\baddress", text, re.I):
            hits.add("1")
        if hits:
            found[path] = hits
    values = set()
    for hits in found.values():
        values |= hits
    if "1" not in values and found:
        problems.append(
            "receive-address count: expected 1 in v0.5 docs, found "
            + str(found))
    extras = values - {"1"}
    if extras:
        problems.append(
            "receive-address count must be 1 in v0.5; also saw "
            + str(sorted(extras)) + " in " + str(found))


def check_linecounts(problems):
    tool = os.path.join(HERE, "tools", "linecount.py")
    if not os.path.exists(tool):
        problems.append("tools/linecount.py missing")
        return
    env = os.environ.copy()
    proc = subprocess.run(
        [sys.executable, tool],
        cwd=HERE, capture_output=True, text=True,
    )
    if proc.returncode != 0:
        problems.append("tools/linecount.py failed: " + proc.stderr.strip())
        return
    counts = {}
    for line in proc.stdout.splitlines():
        parts = line.split()
        if parts and parts[0].endswith(".py") and parts[0] in LINECOUNT_FILES:
            counts[parts[0]] = int(parts[1])
    readme = read("README.md") or ""
    for name, n in counts.items():
        # README table: `name` ... | N |
        pat = re.compile(
            r"`" + re.escape(name) + r"`[^|\n]*\|\s*(\d+)\s*\|")
        m = pat.search(readme)
        if not m:
            # io line may be worded differently
            if name == "io_pico.py":
                m = re.search(r"`io_pico\.py`[^|\n]*\|\s*(\d+)\s*\|", readme)
        if not m:
            problems.append(
                f"README.md missing linecount claim for {name}")
            continue
        claimed = int(m.group(1))
        if claimed != n:
            problems.append(
                f"README.md claims {name} has {claimed} lines but "
                f"linecount.py reports {n}")


def check_image_twins(problems):
    for image, twin in IMAGE_TWINS.items():
        if read(twin) is None:
            problems.append(
                f"{image} has no text twin at {twin}\n"
                f"    (claims inside an image are invisible to grep)")


def check_version_self(problems):
    for path in LIVE:
        if path in EXEMPT:
            continue
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
    check_v05_retracted(problems)
    check_counts(problems)
    check_linecounts(problems)
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
          "have text twins, line counts match.")
