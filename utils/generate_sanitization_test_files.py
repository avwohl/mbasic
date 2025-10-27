#!/usr/bin/env python3
"""
Generate test files with control characters and parity bits
for testing input sanitization.
"""

from pathlib import Path

# Create test files directory
test_dir = Path(__file__).parent.parent / 'tests' / 'sanitization_test_files'
test_dir.mkdir(exist_ok=True, parents=True)

# Test 1: File with various control characters
print("Creating control_chars_test.bas...")
control_file = test_dir / 'control_chars_test.bas'
with open(control_file, 'wb') as f:
    # Line with Ctrl+A (0x01)
    f.write(b'10 PRINT\x01 "HELLO"\n')
    # Line with BELL (0x07)
    f.write(b'20 REM BELL:\x07\n')
    # Line with ESC (0x1B)
    f.write(b'30 PRINT\x1B "ESCAPE"\n')
    # Line with DEL (0x7F)
    f.write(b'40 REM DEL:\x7F\n')
    # Normal line
    f.write(b'50 END\n')
print(f"Created {control_file}")

# Test 2: File with parity bits set (bit 7)
print("\nCreating parity_bits_test.bas...")
parity_file = test_dir / 'parity_bits_test.bas'
with open(parity_file, 'wb') as f:
    # "10 PRINT" with parity bits set on each character
    # '1' = 49, with parity = 177 (49 | 128)
    # '0' = 48, with parity = 176
    # ' ' = 32, with parity = 160
    # 'P' = 80, with parity = 208
    # 'R' = 82, with parity = 210
    # 'I' = 73, with parity = 201
    # 'N' = 78, with parity = 206
    # 'T' = 84, with parity = 212
    f.write(bytes([177, 176, 160, 208, 210, 201, 206, 212]))
    f.write(b' "TEST"\n')
    # Normal line
    f.write(b'20 END\n')
print(f"Created {parity_file}")

# Test 3: Mixed control chars and parity bits
print("\nCreating mixed_issues_test.bas...")
mixed_file = test_dir / 'mixed_issues_test.bas'
with open(mixed_file, 'wb') as f:
    # Line with both control char and parity
    f.write(bytes([177, 176]))  # "10" with parity
    f.write(b'\x01')  # Ctrl+A
    f.write(b' PRINT "TEST"\n')
    # Line with only parity
    f.write(bytes([178, 176]))  # "20" with parity
    f.write(b' END\n')
print(f"Created {mixed_file}")

# Test 4: Empty lines and whitespace with control chars
print("\nCreating whitespace_test.bas...")
whitespace_file = test_dir / 'whitespace_test.bas'
with open(whitespace_file, 'wb') as f:
    f.write(b'10 PRINT "START"\n')
    f.write(b'\x00\x01\x02\n')  # Line with only control chars (should be empty)
    f.write(b'20 PRINT "MIDDLE"\n')
    f.write(b'   \x07   \n')  # Line with spaces and BELL
    f.write(b'30 PRINT "END"\n')
print(f"Created {whitespace_file}")

# Test 5: DOS file (CRLF) with control chars
print("\nCreating dos_crlf_test.bas...")
dos_file = test_dir / 'dos_crlf_test.bas'
with open(dos_file, 'wb') as f:
    f.write(b'10 PRINT "DOS FILE"\r\n')
    f.write(b'20 REM\x01\x07 CONTROL CHARS\r\n')
    f.write(b'30 END\r\n')
print(f"Created {dos_file}")

print("\n" + "="*60)
print("Test files created successfully!")
print("="*60)
print("\nTest files location:", test_dir)
print("\nFiles created:")
for f in test_dir.glob('*.bas'):
    print(f"  - {f.name}")

print("\n" + "="*60)
print("TESTING FILE CONTENT")
print("="*60)

# Now test that sanitization works by loading each file
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from input_sanitizer import sanitize_and_clear_parity

for test_file in test_dir.glob('*.bas'):
    print(f"\nTesting {test_file.name}:")
    with open(test_file, 'rb') as f:
        raw_content = f.read()

    # Decode and sanitize
    try:
        text_content = raw_content.decode('utf-8', errors='ignore')
        sanitized, was_modified = sanitize_and_clear_parity(text_content)

        print(f"  Original size: {len(raw_content)} bytes")
        print(f"  Sanitized size: {len(sanitized.encode('utf-8'))} bytes")
        print(f"  Was modified: {was_modified}")

        if was_modified:
            print(f"  ✓ Sanitization detected issues (as expected)")
        else:
            print(f"  ⚠ No issues found (unexpected for test file)")

    except Exception as e:
        print(f"  ✗ Error: {e}")

print("\n" + "="*60)
print("DONE")
print("="*60)
