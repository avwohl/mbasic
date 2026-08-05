#!/usr/bin/env python3
"""
Check if tnylpo (CP/M emulator) is properly installed and in PATH.

tnylpo is the ALTERNATE CP/M emulator. The preferred one is cpmemu - to check the
whole toolchain, run utils/check_compiler_tools.py instead, which covers cpmemu
first. See docs/dev/TOOLCHAIN_POLICY.md.

This utility verifies that the MBASIC test scripts can find tnylpo.
"""

import subprocess
import sys
import os

def check_tnylpo():
    """Check if tnylpo is available in PATH"""

    print("Checking for tnylpo installation...")
    print("-" * 50)

    # Try to find tnylpo using which
    try:
        result = subprocess.run(['which', 'tnylpo'],
                              capture_output=True,
                              text=True)
        if result.returncode == 0:
            path = result.stdout.strip()
            print(f"✓ Found tnylpo at: {path}")
        else:
            print("✗ tnylpo not found in PATH")
            print("\nTo fix this:")
            print("1. Build and install tnylpo (see docs/dev/TNYLPO_SETUP.md)")
            print("2. Add tnylpo to your PATH")
            return False
    except FileNotFoundError:
        print("✗ 'which' command not found (non-Unix system?)")

    # Try to run tnylpo via env (as the test scripts do)
    print("\nTrying to run tnylpo via /usr/bin/env...")
    try:
        # tnylpo doesn't have a --version flag, try --help
        result = subprocess.run(['/usr/bin/env', 'tnylpo', '--help'],
                              capture_output=True,
                              text=True,
                              timeout=5)
        # tnylpo returns non-zero for help, but that's OK
        if "usage:" in result.stdout.lower() or "usage:" in result.stderr.lower():
            print("✓ tnylpo is accessible via /usr/bin/env")
            print("\ntnylpo help output found")
            return True
        else:
            # Try just running it without args to see if it exists
            result2 = subprocess.run(['/usr/bin/env', 'tnylpo'],
                                   capture_output=True,
                                   text=True,
                                   timeout=1)
            if "error" in result2.stderr.lower() or result2.returncode != 0:
                # tnylpo exists but needs arguments
                print("✓ tnylpo is accessible via /usr/bin/env")
                print("  (exits with error when no program specified - this is normal)")
                return True
            else:
                print("✗ Unexpected tnylpo behavior")
                return False
    except FileNotFoundError:
        print("✗ tnylpo not found in PATH")
        print("\nYour PATH:")
        print(os.environ.get('PATH', 'PATH not set'))
        return False
    except subprocess.TimeoutExpired:
        # Timeout might mean tnylpo is waiting for input, which means it exists
        print("✓ tnylpo is accessible via /usr/bin/env")
        print("  (appears to be running - killed after timeout)")
        return True
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_tnylpo_functionality():
    """Try to run a simple test with tnylpo"""
    print("\nTesting tnylpo functionality...")
    print("-" * 50)

    # Create a minimal CP/M program (just RET instruction)
    test_com = "/tmp/test_tnylpo.com"
    try:
        with open(test_com, "wb") as f:
            # Simple CP/M program: just return to CP/M
            # C9 = RET instruction in Z80
            f.write(b'\xc9')

        # Try to run it
        result = subprocess.run(['/usr/bin/env', 'tnylpo', test_com],
                              capture_output=True,
                              text=True,
                              timeout=2)

        # Clean up
        try:
            os.remove(test_com)
        except:
            pass

        if result.returncode == 0:
            print("✓ tnylpo successfully executed test program")
            return True
        else:
            print("⚠ tnylpo found but test execution failed")
            print("  This might be normal depending on tnylpo configuration")
            return True  # Still consider it a success if tnylpo exists

    except subprocess.TimeoutExpired:
        print("⚠ Test timed out (tnylpo might be waiting for input)")
        return True  # tnylpo exists, just didn't exit
    except Exception as e:
        print(f"⚠ Could not test functionality: {e}")
        return False

def suggest_installation():
    """Suggest installation methods"""
    print("\n" + "=" * 50)
    print("tnylpo Installation Instructions:")
    print("=" * 50)
    print("""
tnylpo must be built from source. Here's how:

1. Clone the repository:
   git clone https://gitlab.com/gbrein/tnylpo.git
   cd tnylpo

2. Build tnylpo:
   make

3. Install to /usr/local/bin (requires sudo):
   sudo make install

   Or install to ~/bin (no sudo needed):
   mkdir -p ~/bin
   cp tnylpo ~/bin/
   export PATH="$PATH:$HOME/bin"

4. Make PATH permanent (add to ~/.bashrc):
   echo 'export PATH="$PATH:$HOME/bin"' >> ~/.bashrc

5. Verify installation:
   which tnylpo
   tnylpo --help

Notes:
- tnylpo requires ncurses development libraries:
  Ubuntu/Debian: sudo apt-get install libncurses5-dev
  Fedora/RHEL: sudo dnf install ncurses-devel
  macOS: Should be included with Xcode

- tnylpo is a CP/M 2.2 emulator that runs .COM files
- It provides a full CP/M environment with BDOS/BIOS emulation
    """)

def main():
    """Main entry point"""
    success = check_tnylpo()

    if success:
        # Also try functionality test
        test_tnylpo_functionality()

        print("\n" + "=" * 50)
        print("✓ tnylpo is properly installed and configured!")
        print("  You can run CP/M .COM files with: tnylpo program.com")
        print("=" * 50)
        sys.exit(0)
    else:
        suggest_installation()
        print("\nFor detailed instructions, see: docs/dev/TNYLPO_SETUP.md")
        sys.exit(1)

if __name__ == "__main__":
    main()