#!/usr/bin/env python3
"""Enforce the project's Z80/CP/M toolchain preference in docs and code.

WHY THIS EXISTS
---------------
The preferred C compiler for the Z80/8080 backend is the sister project **uc80**
(with the um80 assembler and ul80 linker), and the preferred CP/M emulator is the
sister project **cpmemu**.  z88dk and tnylpo remain SUPPORTED ALTERNATES - z88dk is
still required for Microsoft Binary Format floats and for true Intel 8080 output -
but they are not the default and must never be documented as "required".

This has been corrected by hand many times and kept drifting back to z88dk/tnylpo.
This script turns the preference into something a machine checks, so a regression
fails a commit instead of surviving in the docs.  See docs/dev/TOOLCHAIN_POLICY.md.

If this script fails, fix the document.  Do not relax the rule.

WHAT IT CHECKS
--------------
1. Banned phrasing: no governed file may claim z88dk or tnylpo is required, or
   present them as *the* toolchain.
2. Precedence: in a governed file that mentions z88dk, uc80 must also be mentioned
   and must appear first.  Same for cpmemu vs tnylpo.

Usage:
    python3 utils/check_toolchain_policy.py            # check, exit 1 on violation
    python3 utils/check_toolchain_policy.py --list     # list governed files
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
POLICY_DOC = "docs/dev/TOOLCHAIN_POLICY.md"

# Trees that are a historical record or generated output.  Their job is to say what
# was true at the time, so the preference rule does not apply to them.
EXEMPT_PREFIXES = (
    "docs/history/",
    "docs/future/",
    "docs/external/",
    "site/",
    "build/",
    ".git/",
)

# Files whose whole subject IS the alternate toolchain - a setup guide for z88dk, or
# the script that checks for tnylpo.  They are allowed to lead with the tool they are
# named after; requiring them to mention uc80 first would be nonsense.
#
# This is a carve-out for topic, not a way to opt out of the policy: rule 1 (nothing
# may be called "required") still applies to every file here.  Do not add a file just
# because it fails - add it only if the alternate tool is genuinely its subject.
ALTERNATE_TOOLCHAIN_DOCS = {
    "docs/dev/Z88DK_SETUP.md",
    "docs/dev/TNYLPO_SETUP.md",
    "docs/dev/COMPILER_Z88DK_PATH_CHANGE.md",
    "utils/check_z88dk.py",
    "utils/check_tnylpo.py",
}

# The policy doc itself quotes the banned phrasing in order to forbid it.
SELF_EXEMPT = {POLICY_DOC, "utils/check_toolchain_policy.py"}

PREFERRED_COMPILER = re.compile(r"\buc80\b", re.IGNORECASE)
ALTERNATE_COMPILER = re.compile(r"\bz88dk\b", re.IGNORECASE)
PREFERRED_EMULATOR = re.compile(r"\bcpmemu\b", re.IGNORECASE)
ALTERNATE_EMULATOR = re.compile(r"\btnylpo\b", re.IGNORECASE)

# Phrasings that demote the preferred toolchain.  Kept deliberately narrow so the
# check stays honest: each pattern is something that is simply false under the policy.
BANNED_PHRASES = [
    (
        re.compile(r"\*\*z88dk\*\*\s*\(required\)", re.IGNORECASE),
        "z88dk is an alternate, not required - uc80 is the preferred compiler",
    ),
    (
        re.compile(r"\bz88dk\b[^.\n]{0,40}\bis required\b", re.IGNORECASE),
        "z88dk is an alternate, not required - uc80 is the preferred compiler",
    ),
    (
        re.compile(r"\brequires?\s+z88dk\b", re.IGNORECASE),
        "z88dk is an alternate, not required - uc80 is the preferred compiler",
    ),
    (
        re.compile(r"\byou\s+need\s+z88dk\b", re.IGNORECASE),
        "z88dk is an alternate, not required - uc80 is the preferred compiler",
    ),
    (
        re.compile(r"\*\*tnylpo\*\*\s*\(required\)", re.IGNORECASE),
        "tnylpo is an alternate, not required - cpmemu is the preferred emulator",
    ),
    (
        re.compile(r"\brequires?\s+tnylpo\b", re.IGNORECASE),
        "tnylpo is an alternate, not required - cpmemu is the preferred emulator",
    ),
]

# Extensions worth scanning.  Binary and data files are skipped.
SCANNED_SUFFIXES = {".md", ".py", ".sh", ".yml", ".yaml", ".toml", ".txt", ".cfg"}
SCANNED_NAMES = {"Makefile", "Dockerfile"}


def is_exempt(rel_path: str) -> bool:
    if rel_path in SELF_EXEMPT:
        return True
    return any(rel_path.startswith(prefix) for prefix in EXEMPT_PREFIXES)


def governed_files() -> list[Path]:
    """Every non-exempt file that mentions any of the four tools."""
    found = []
    for path in sorted(REPO_ROOT.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix not in SCANNED_SUFFIXES and path.name not in SCANNED_NAMES:
            continue
        rel = path.relative_to(REPO_ROOT).as_posix()
        if is_exempt(rel):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if ALTERNATE_COMPILER.search(text) or ALTERNATE_EMULATOR.search(text):
            found.append(path)
    return found


def first_match(pattern: re.Pattern, text: str) -> int | None:
    match = pattern.search(text)
    return match.start() if match else None


def line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def check_file(path: Path) -> list[str]:
    """Return a list of human-readable violations for one file."""
    rel = path.relative_to(REPO_ROOT).as_posix()
    text = path.read_text(encoding="utf-8", errors="ignore")
    violations = []

    # Rule 1: banned phrasing.  Applies to every governed file, including the
    # alternate-toolchain docs - those describe an alternate, not a requirement.
    for pattern, reason in BANNED_PHRASES:
        for match in pattern.finditer(text):
            line = line_of(text, match.start())
            violations.append(
                f"{rel}:{line}: {reason}\n"
                f"    found: {match.group(0).strip()!r}"
            )

    if rel in ALTERNATE_TOOLCHAIN_DOCS:
        return violations

    # Rule 2: precedence.  A file that talks about the alternate must also name the
    # preferred tool, and must name it first.
    for alt_re, pref_re, alt_name, pref_name, role in (
        (ALTERNATE_COMPILER, PREFERRED_COMPILER, "z88dk", "uc80", "C compiler"),
        (ALTERNATE_EMULATOR, PREFERRED_EMULATOR, "tnylpo", "cpmemu", "CP/M emulator"),
    ):
        alt_at = first_match(alt_re, text)
        if alt_at is None:
            continue
        pref_at = first_match(pref_re, text)
        if pref_at is None:
            violations.append(
                f"{rel}:{line_of(text, alt_at)}: mentions {alt_name} but never "
                f"{pref_name} - {pref_name} is the preferred {role}"
            )
        elif pref_at > alt_at:
            violations.append(
                f"{rel}:{line_of(text, alt_at)}: {alt_name} appears before "
                f"{pref_name} (line {line_of(text, pref_at)}) - the preferred "
                f"{role} {pref_name} must be presented first"
            )

    return violations


def main() -> int:
    if "--list" in sys.argv:
        for path in governed_files():
            print(path.relative_to(REPO_ROOT).as_posix())
        return 0

    all_violations = []
    for path in governed_files():
        all_violations.extend(check_file(path))

    if not all_violations:
        print("OK: toolchain policy satisfied (uc80 + cpmemu preferred)")
        return 0

    print("TOOLCHAIN POLICY VIOLATIONS")
    print()
    print("The preferred C compiler is uc80 (with um80/ul80); the preferred CP/M")
    print("emulator is cpmemu.  z88dk and tnylpo are supported alternates and must")
    print("not be presented as required or as the default.")
    print()
    for violation in all_violations:
        print(f"  {violation}")
    print()
    print(f"Total: {len(all_violations)} violation(s)")
    print(f"See {POLICY_DOC} - fix the document, do not weaken this check.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
