#!/usr/bin/env python3
"""
Check which Z80/CP/M compiler tools are installed.

The preferred toolchain is uc80 (with the um80 assembler and ul80 linker) plus the
cpmemu emulator.  z88dk and tnylpo are supported alternates - still needed for
Microsoft Binary Format floats, true Intel 8080 output, and INP/OUT/WAIT port I/O.
See docs/dev/TOOLCHAIN_POLICY.md.

Either toolchain on its own is enough to build CP/M executables, so this script
reports what you have rather than insisting on a particular set.

Usage:
    python3 utils/check_compiler_tools.py
"""

import os
import shutil
import subprocess
import sys

# Make `import uc80` work the same way the compiler driver does.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def which(name):
    return shutil.which(name)


def version_of(cmd):
    """Best-effort one-line version string for a tool, or '' if it won't say."""
    for flag in ('--version', '-v'):
        try:
            result = subprocess.run([cmd, flag], capture_output=True, text=True,
                                    timeout=15)
        except (OSError, subprocess.SubprocessError):
            return ''
        text = (result.stdout or result.stderr).strip()
        if text:
            return text.splitlines()[0]
    return ''


def report(label, cmd, role, install):
    """Print one tool's status. Returns True if found."""
    path = which(cmd)
    if path:
        version = version_of(cmd)
        print(f"  OK    {label:<8} {path}" + (f"  [{version}]" if version else ""))
        return True
    print(f"  MISS  {label:<8} not on PATH ({role})")
    print(f"          install: {install}")
    return False


def find_uc80_libs():
    """Locate uc80's libc.lib - the .lib files are build artifacts and do not
    always sit beside the Python package."""
    try:
        from src.mbasic_main import uc80_lib_dir
    except Exception:
        return None
    try:
        return uc80_lib_dir()
    except Exception:
        return None


def main():
    print("MBASIC Z80/CP/M Toolchain Check")
    print("=" * 64)
    print("Preferred: uc80 + um80 + ul80 (compile)  /  cpmemu (run)")
    print("Alternate: z88dk (compile)               /  tnylpo (run)")
    print("Policy:    docs/dev/TOOLCHAIN_POLICY.md")

    print("\nPreferred toolchain")
    uc80_ok = report("uc80", "uc80", "preferred C compiler",
                     "pip install uc80")
    um80_ok = report("um80", "um80", "assembler for uc80", "pip install um80")
    ul80_ok = report("ul80", "ul80", "linker for uc80", "pip install um80")

    libs = find_uc80_libs()
    if uc80_ok:
        if libs:
            print(f"  OK    libs     {libs}")
        else:
            print("  MISS  libs     libc.lib/runtime.lib not found")
            print("          build them: python3 -m uc80.lib.build_libs")
            print("          or point MBASIC_UC80_LIB at the directory holding them")

    print("\nPreferred emulator")
    cpmemu_ok = report("cpmemu", "cpmemu", "preferred CP/M emulator",
                       "https://github.com/avwohl/cpmemu (.deb/.rpm on releases)")

    print("\nAlternate toolchain")
    # z88dk's CP/M driver is normally installed as z88dk.zcc (snap) or zcc.
    z88dk_cmd = 'z88dk.zcc' if which('z88dk.zcc') else 'zcc'
    z88dk_ok = report("z88dk", z88dk_cmd, "alternate C compiler; needed for "
                      "MBF32 floats and 8080", "snap install z88dk")
    tnylpo_ok = report("tnylpo", "tnylpo", "alternate CP/M emulator",
                       "build from source - see docs/dev/TNYLPO_SETUP.md")

    uc80_chain = uc80_ok and um80_ok and ul80_ok and bool(libs)

    print("\n" + "=" * 64)
    print("SUMMARY")
    print("=" * 64)

    if uc80_chain:
        print("Compile: uc80 toolchain ready (preferred)")
    elif z88dk_ok:
        print("Compile: uc80 incomplete; z88dk available - use --toolchain z88dk")
    else:
        print("Compile: NO C toolchain found - install uc80 (pip install uc80 um80)")

    if cpmemu_ok:
        print("Run:     cpmemu ready (preferred)")
    elif tnylpo_ok:
        print("Run:     cpmemu missing; tnylpo available - use --emulator tnylpo")
    else:
        print("Run:     no CP/M emulator found - compiled programs cannot be tested")

    if not z88dk_ok:
        print("\nNote: without z88dk you cannot build --cpu 8080, Microsoft Binary")
        print("      Format floats, or programs using INP/OUT/WAIT.")

    print()
    if uc80_chain and cpmemu_ok:
        print("Preferred toolchain is complete. Build and run with:")
        print("  python3 mbasic --compile-c program program.bas --run")
        sys.exit(0)

    if (uc80_chain or z88dk_ok) and (cpmemu_ok or tnylpo_ok):
        print("A usable toolchain is installed, but not the preferred one.")
        print("See docs/dev/TOOLCHAIN_POLICY.md and docs/dev/COMPILER_SETUP.md")
        sys.exit(0)

    print("Toolchain incomplete - see docs/dev/COMPILER_SETUP.md")
    sys.exit(1)


if __name__ == "__main__":
    main()
