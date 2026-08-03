#!/usr/bin/env python3
"""
Check if z88dk is properly installed and in PATH.

z88dk is the ALTERNATE C toolchain. The preferred one is uc80 - to check the whole
toolchain, run utils/check_compiler_tools.py instead, which covers uc80/um80/ul80
and cpmemu first. See docs/dev/TOOLCHAIN_POLICY.md.

z88dk is still needed for Microsoft Binary Format floats, true Intel 8080 output,
and the INP/OUT/WAIT port statements, so this check is not obsolete.

This utility verifies that the MBASIC compiler can find z88dk.zcc.
"""

import subprocess
import sys
import os

def check_z88dk():
    """Check if z88dk.zcc is available in PATH"""

    print("Checking for z88dk installation...")
    print("-" * 50)

    # Try to find z88dk.zcc using which
    try:
        result = subprocess.run(['which', 'z88dk.zcc'],
                              capture_output=True,
                              text=True)
        if result.returncode == 0:
            path = result.stdout.strip()
            print(f"✓ Found z88dk.zcc at: {path}")
        else:
            print("✗ z88dk.zcc not found in PATH")
            print("\nTo fix this:")
            print("1. Install z88dk (see docs/dev/COMPILER_SETUP.md)")
            print("2. Add z88dk to your PATH")
            return False
    except FileNotFoundError:
        print("✗ 'which' command not found (non-Unix system?)")

    # Try to run z88dk.zcc via env (as the compiler does)
    print("\nTrying to run z88dk.zcc via /usr/bin/env...")
    try:
        result = subprocess.run(['/usr/bin/env', 'z88dk.zcc', '--version'],
                              capture_output=True,
                              text=True,
                              timeout=5)
        if result.returncode == 0:
            print("✓ z88dk.zcc is accessible via /usr/bin/env")
            print("\nVersion info:")
            print(result.stdout[:200])  # First 200 chars of version info
            return True
        else:
            print("✗ z88dk.zcc failed to run")
            print("Error:", result.stderr)
            return False
    except FileNotFoundError:
        print("✗ z88dk.zcc not found in PATH")
        print("\nYour PATH:")
        print(os.environ.get('PATH', 'PATH not set'))
        return False
    except subprocess.TimeoutExpired:
        print("✗ z88dk.zcc timed out")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def suggest_installation():
    """Suggest installation methods"""
    print("\n" + "=" * 50)
    print("z88dk Installation Options:")
    print("=" * 50)
    print("""
1. Snap (Ubuntu/Debian):
   sudo snap install z88dk
   export PATH="$PATH:/snap/bin"

2. Build from source:
   git clone https://github.com/z88dk/z88dk.git
   cd z88dk
   ./build.sh
   export PATH="$PATH:$HOME/z88dk/bin"

3. Docker with wrapper:
   docker pull z88dk/z88dk
   # Create wrapper script in ~/bin/z88dk.zcc

Add the export PATH line to ~/.bashrc to make it permanent.
    """)

def main():
    """Main entry point"""
    if check_z88dk():
        print("\n" + "=" * 50)
        print("✓ z88dk is properly installed and configured!")
        print("  The MBASIC compiler will be able to use it.")
        print("=" * 50)
        sys.exit(0)
    else:
        suggest_installation()
        print("\nFor detailed instructions, see: docs/dev/COMPILER_SETUP.md")
        sys.exit(1)

if __name__ == "__main__":
    main()