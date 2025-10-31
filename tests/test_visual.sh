#!/bin/bash
# Test and capture visual state

# Use script to capture terminal output
script -q -c "expect << 'EOF'
set timeout 10
spawn python3 mbasic --backend curses test_program.bas
sleep 3
send \"\x12\"
sleep 2
send \"\x03\"
expect eof
EOF
" /tmp/terminal_capture.txt

# Parse the captured output to show just the visible screen
python3 << 'PYEOF'
import re

with open('/tmp/terminal_capture.txt', 'rb') as f:
    data = f.read().decode('utf-8', errors='ignore')

# Look for the screen content after initial setup
# Extract lines that look like content
lines = data.split('\n')
print("=== Screen capture (looking for divider and OK) ===")
for i, line in enumerate(lines[-30:]):
    # Remove ANSI codes for easier reading
    clean = re.sub(r'\x1b\[[0-9;]*[mGHJK]', '', line)
    clean = re.sub(r'\x1b\[[?][0-9;]*[hl]', '', clean)
    if '─' in clean or 'OK' in clean or 'Editor' in clean or 'Output' in clean:
        print(f"Line {i}: {repr(clean[:80])}")
PYEOF
