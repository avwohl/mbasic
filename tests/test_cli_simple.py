#!/usr/bin/env python3
"""Simple CLI test to understand prompting behavior"""

import pexpect
import sys

def test_cli():
    """Test CLI mode behavior"""
    print("Starting CLI test...")

    # Start CLI mode
    proc = pexpect.spawn('python3 mbasic.py --backend cli',
                        encoding='utf-8', timeout=5)

    # Enable logging to see what's happening
    proc.logfile = sys.stdout

    try:
        # Wait for initial prompt
        proc.expect('Ready')
        print("\n✓ Got initial prompt")

        # Enter a simple line
        proc.sendline('10 PRINT "HELLO"')
        # CLI doesn't echo "Ready" after each line entry
        # It just accepts the line

        # Try LIST command
        proc.sendline('LIST')
        proc.expect('10 PRINT "HELLO"')
        print("\n✓ LIST works")

        # Try RUN
        proc.sendline('RUN')
        proc.expect('HELLO')
        print("\n✓ RUN works")

        # Try immediate mode
        proc.sendline('PRINT 2+2')
        proc.expect('4')
        print("\n✓ Immediate mode works")

        # Exit
        proc.sendline('SYSTEM')
        proc.wait()
        print("\n✓ Clean exit")

        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        if proc.isalive():
            proc.terminate()
        return False

if __name__ == '__main__':
    success = test_cli()
    sys.exit(0 if success else 1)